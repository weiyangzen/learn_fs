# subset-b-006009 research

Grouped research for the subset B work item covering Linux IPC, kernel build, process accounting, async work scheduling, and audit subsystem files mirrored under `sources/distributed-fs/ceph-client`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/util.c -->
# sources/distributed-fs/ceph-client/ipc/util.c

## Purpose
`ipc/util.c` is the common SysV IPC support layer used by semaphores, message queues, and shared memory. It initializes IPC namespaces and `/proc/sysvipc`, manages IPC object identifiers, translates permission structures, enforces generic IPC permissions, and provides shared lookup/creation helpers for `semget`, `msgget`, and `shmget` style operations.

## Important APIs, types, and functions
The file centers on `struct ipc_ids`, `struct kern_ipc_perm`, and helper descriptors from `util.h` such as `struct ipc_ops` and `struct ipc_params`. `ipc_init()` creates the proc directory and calls `sem_init()`, `msg_init()`, and `shm_init()`. `ipc_init_ids()` initializes per-namespace identifier state: `rwsem`, rhashtable key lookup, IDR, sequence counters, and checkpoint-restore fields.

ID allocation is split between `ipc_idr_alloc()` and `ipc_addid()`. `ipc_idr_alloc()` assigns an IDR index, computes the sequence component, handles `CONFIG_CHECKPOINT_RESTORE` requested IDs, and publishes the object with ordering comments around RCU visibility. `ipc_addid()` initializes the object refcount, spinlock, creator credentials, deletion flag, inserts into IDR and the key rhashtable when the key is public, and returns the object locked on success.

Lookup and control helpers include `ipc_findkey()`, `ipc_obtain_object_idr()`, `ipc_obtain_object_check()`, `ipcget()`, `ipcctl_obtain_check()`, `ipc_rmid()`, `ipc_set_key_private()`, `ipc_rcu_getref()`, and `ipc_rcu_putref()`. Permission conversion and enforcement are provided by `ipcperms()`, `kernel_to_ipc64_perm()`, `ipc64_perm_to_ipc_perm()`, and `ipc_update_perm()`. The procfs path is implemented by `ipc_init_proc_interface()` and the `sysvipc_proc_*` seq-file operations.

## Control flow
Creation through `ipcget()` branches on `IPC_PRIVATE`. Private objects call `ipcget_new()`, which takes `ids->rwsem` for writing and delegates to the resource-specific `getnew`. Public keys call `ipcget_public()`, which takes the same writer semaphore because it may create a new object. It searches by key in the rhashtable, creates if missing and `IPC_CREAT` is present, rejects `IPC_CREAT|IPC_EXCL` conflicts, runs resource-specific `more_checks`, then calls `ipc_check_perms()`.

Deletion via `ipc_rmid()` removes the IDR entry, removes the key hash entry if needed, decrements `in_use`, marks the object deleted, and recalculates `max_idx` if the removed index was the maximum. Procfs iteration takes `ids->rwsem` for reading, maps seq-file positions to IDR indexes, locks each object while formatting, and releases namespace references on file close.

## State and persistence behavior
IPC state is in-memory and namespace-scoped. Persistence is limited to object lifetime, ID sequence numbers, and procfs visibility. `ids->seq`, `last_idx`, and `max_idx` prevent stale ID reuse from being accepted without a matching sequence. Object memory is RCU protected: readers may obtain objects without immediate object locks, while final freeing is scheduled with `call_rcu()`.

## Dependencies and integration points
This file integrates with IDR, rhashtable, RCU, namespace lifetime, procfs seq-file support, LSM hooks (`security_ipc_permission` and resource-specific `associate` callbacks), audit hooks (`audit_ipc_obj`, `audit_ipc_set_perm`), capabilities, user namespaces, and the IPC resource implementations in `sem.c`, `msg.c`, and `shm.c`.

## Risks and invariants
The main risk is violating the documented locking model. `ids->rwsem` protects creation, removal, and proc iteration; `kern_ipc_perm.lock` protects per-object mutation; RCU protects lockless lookup windows. Incorrect publication ordering could expose partially initialized objects, and incorrect sequence handling could make stale user-visible IDs valid. Permission paths must preserve the order of normal DAC checks, capability checks in the IPC namespace userns, LSM checks, and audit logging.

## Test signals
Useful signals include SysV IPC creation/removal stress across namespaces, concurrent `IPC_CREAT` with shared keys, `IPC_RMID` races with lookup and procfs iteration, permission tests for owner/group/other/capability paths, checkpoint-restore requested IDs, and `/proc/sysvipc/*` formatting under churn. Kernel concurrency tools such as KCSAN/lockdep are relevant because most failures would be locking or lifetime regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/util.h -->
# sources/distributed-fs/ceph-client/ipc/util.h

## Purpose
`ipc/util.h` is the shared internal header for SysV IPC implementation files. It defines the IPC ID layout, declares namespace initialization/exit helpers, describes common get/create operation callbacks, exposes generic permission/lookup/update helpers, and provides small locking, reference, and PID utility inlines used by semaphore, message queue, and shared memory code.

## Important APIs, types, and macros
The header defines the standard and extended IPCMNI layouts: `IPCMNI_SHIFT`, `IPCMNI_EXTEND_SHIFT`, `IPCMNI`, `IPCMNI_EXTEND`, `ipcmni_seq_shift()`, `IPCMNI_IDX_MASK`, `ipcid_to_idx()`, `ipcid_to_seqx()`, and `ipcid_seq_max()`. These macros define how the user-visible IPC ID is split into an index and a sequence number.

`struct ipc_params` carries common `key`, `flg`, and type-specific creation parameters (`size` for shared memory or `nsems` for semaphores). `struct ipc_ops` supplies resource-specific callbacks for new object creation, LSM association, and optional extra validation. Public APIs include `ipc_init_ids()`, `ipc_addid()`, `ipc_rmid()`, `ipc_set_key_private()`, `ipcperms()`, `ipc_obtain_object_idr()`, `ipcctl_obtain_check()`, `ipc_update_perm()`, `kernel_to_ipc64_perm()`, `ipc64_perm_to_ipc_perm()`, and message helpers such as `load_msg()` and `store_msg()`.

The header also declares procfs support (`ipc_init_proc_interface()`, `ipc_seq_pid_ns()`), namespace hooks for SysV IPC and POSIX mqueue, and compatibility stubs when features are disabled. Locking helpers `ipc_lock_object()`, `ipc_unlock_object()`, and `ipc_assert_locked_object()` wrap the object spinlock.

## Control flow and integration
The header's declarations establish the common path implemented in `util.c`: resource-specific code prepares an `ipc_params` and `ipc_ops`, then calls `ipcget()` or lower-level helpers. Control operations call `ipcctl_obtain_check()` while holding the namespace ID semaphore and RCU read lock. Proc emitters use the `IPC_SEM_IDS`, `IPC_MSG_IDS`, and `IPC_SHM_IDS` indexes to select namespace ID arrays.

## State and persistence behavior
No state is stored in this header, but its macros define persistent ABI behavior for IPC IDs. Changing the ID bit split or masks would alter lookup semantics and stale-ID detection. Conditional externs for `ipc_mni`, `ipc_mni_shift`, and `ipc_min_cycle` make runtime sysctl-selected IPCMNI extension mode visible to all IPC users.

## Dependencies and integration points
It depends on kernel IPC namespace types, PID references, user/kernel IPC permission structures, RCU/refcounted `kern_ipc_perm` objects, and optional configs such as `CONFIG_SYSVIPC`, `CONFIG_PROC_FS`, `CONFIG_POSIX_MQUEUE`, `CONFIG_SYSVIPC_SYSCTL`, `CONFIG_CHECKPOINT_RESTORE`, and `CONFIG_ARCH_WANT_IPC_PARSE_VERSION`.

## Risks and invariants
The critical invariant is that every user of the ID macros agrees on the index/sequence split. `ipc_checkid()` must remain consistent with `ipc_idr_alloc()` in `util.c`. Callers must honor comments about required locks: `ipc_addid()` under write `ids->rwsem`, `ipc_rmid()` with both namespace and object locks, `ipcperms()` with the object locked, and object lookup inside RCU sections.

## Test signals
Compile coverage across relevant config combinations is important because this header has many conditional stubs. Runtime tests should exercise normal and extended IPCMNI modes, namespace init/exit, procfs enabled/disabled builds, old IPC command parsing when configured, and stale-ID rejection after removal and sequence increment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/Makefile -->
# sources/distributed-fs/ceph-client/kernel/Makefile

## Purpose
This Makefile controls which core kernel objects and subdirectories are built for the kernel tree snapshot under `sources/distributed-fs/ceph-client/kernel`. It is the integration point that wires core process, scheduling, audit, accounting, tracing, crash, module, namespace, BPF, sanitizer, and generated-header components into Kbuild based on configuration symbols.

## Important build entries
The base `obj-y` list includes core always-built objects such as `fork.o`, `exit.o`, `softirq.o`, `workqueue.o`, `pid.o`, `cred.o`, `async.o`, and others. Subdirectories such as `sched/`, `locking/`, `power/`, `printk/`, `irq/`, `rcu/`, `livepatch/`, `liveupdate/`, `dma/`, `entry/`, and `unwind/` are always included, while `module/`, `futex/`, `cgroup/`, `time/`, `trace/`, `events/`, and debug/test directories are gated by config.

The files in this work item are selected here: `async.o` is in the core `obj-y`, `acct.o` is built under `CONFIG_BSD_PROCESS_ACCT`, `audit.o` and `auditfilter.o` under `CONFIG_AUDIT`, and `auditsc.o audit_watch.o audit_fsnotify.o audit_tree.o` under `CONFIG_AUDITSYSCALL`.

## Control flow
Kbuild evaluates `obj-y` and `obj-$(CONFIG_*)` lines to build a composite object list. Conditional instrumentation variables tune compiler flags per object. Later rules generate embedded config and kernel header archive artifacts: `config_data.gz` from `$(KCONFIG_CONFIG)` and `kheaders_data.tar.xz` from generated source/object header lists and checksum files.

## State and generated artifacts
The Makefile does not maintain runtime state, but it defines build outputs and clean targets. Generated files include `config_data`, `config_data.gz`, `kheaders_data.tar.xz`, `kheaders-srclist`, `kheaders-objlist`, and `kheaders.md5`; `clean-files` removes the kheaders helper lists/checksum.

## Dependencies and integration points
It depends on Kbuild variables and macros such as `obj-y`, `obj-$()`, `targets`, `FORCE`, `if_changed`, `filechk`, compiler option probes, and sanitizer/instrumentation variables. It integrates with config symbols, architecture include paths via `SRCARCH`, generated include directories, and `gen_kheaders.sh`.

## Risks and invariants
Build selection mistakes can silently omit required core services or compile objects under the wrong config. Audit has a split dependency: base audit logging/filtering requires `CONFIG_AUDIT`, while syscall auditing and path watches require `CONFIG_AUDITSYSCALL`; moving these incorrectly would create unresolved symbols or missing behavior. Instrumentation exclusions are also important: softirq, extable, kcov, and kstack erase are deliberately excluded from specific sanitizers/tracers to avoid recursion, unsafe instrumentation, or noisy coverage.

## Test signals
The best tests are config matrix builds: audit on/off, auditsyscall on/off, BSD accounting on/off, tracing/KCOV/KASAN/KCSAN combinations, modules on/off, and IKHEADERS on/off. Build logs should show expected objects included and generated header/config targets rebuilt when inputs change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/acct.c -->
# sources/distributed-fs/ceph-client/kernel/acct.c

## Purpose
`acct.c` implements BSD process accounting. When enabled through the `acct()` syscall, the kernel writes a compact `acct_t` record for exiting processes to a configured regular file. It handles enabling/disabling accounting per PID namespace, accounting file lifetime across mounts, free-space based pause/resume, record encoding, and collection of per-process CPU, memory, fault, UID/GID, TTY, and exit information.

## Important APIs, types, and functions
The central state is `struct bsd_acct_struct`, which contains an `fs_pin`, refcount, RCU head, mutex, active/check-space flags, next check time, accounting file, PID namespace, close work item, completion, and reusable `acct_t` record buffer. `acct_on()` opens and validates the target file, clones an internal mount, allocates state, inserts the fs pin, and atomically swaps `ns->bacct`. `SYSCALL_DEFINE1(acct)` enforces `CAP_SYS_PACCT` and enables or disables accounting.

Lifetime helpers include `acct_get()`, `acct_put()`, `acct_pin_kill()`, `close_work()`, and `acct_exit_ns()`. Record helpers include `fill_ac()`, `acct_write_process()`, `do_acct_process()`, `acct_collect()`, `slow_acct_process()`, and `acct_process()`. Encoding helpers implement legacy compressed fields: `encode_comp_t()`, `encode_comp2_t()`, and `encode_float()` depending on `ACCT_VERSION`.

## Control flow
Enabling accounting opens the user path with `O_WRONLY|O_APPEND|O_LARGEFILE`, rejects non-regular, internal, procfs/sysfs-visible, or non-writable files, builds an internal mount-backed file, and installs a new pin in the active PID namespace. Replacing a file kills the previous pin. Disabling accounting calls `pin_kill()` on the namespace's active pin.

On process exit, `acct_collect()` accumulates signal-shared accounting fields while holding `siglock`; for the last thread it walks VMAs under `mmap_read_lock()` to compute memory use. `acct_process()` walks the current PID namespace and its parents, obtains each active accounting state with RCU/refcount protection, fills the record, temporarily removes `RLIMIT_FSIZE`, writes under the file owner's credentials, and restores the limit. Free space is checked periodically by `check_free_space()`, which toggles active state according to sysctl-controlled resume/suspend thresholds.

## State and persistence behavior
Persistent output is the append-only accounting file. Runtime state is per PID namespace via `ns->bacct`, protected by RCU, mutexes, fs pins, and atomic references. The fs pin prevents unsafe unmount/remount interactions; if the mount is killed, `acct_pin_kill()` writes a final record for the current task, schedules synchronous close work, clears `ns->bacct`, removes the pin, and releases the state.

## Dependencies and integration points
The file integrates with sysctl (`kernel.acct`), syscall dispatch, capabilities, PID namespaces, VFS open/write/statfs/freeze protection, mount pinning, workqueues, RCU, task signal accounting, credentials, TTY handling, time conversion, and user namespace UID/GID mapping.

## Risks and invariants
Key risks are lifetime races around `ns->bacct`, mount teardown, and concurrent file replacement. The lock order around `acct_on_mutex`, per-accounting mutex, RCU, and fs pins must be preserved. Writes intentionally bypass `RLIMIT_FSIZE` and use the opener's credentials; regressions here can break ABI expectations. Free-space logic must avoid writing to frozen filesystems and must not deadlock during unmount or remount.

## Test signals
Test enabling/disabling accounting with valid and invalid files, replacing the active file, PID namespace parent accounting, mount unmount/remount while accounting is active, low-space pause/resume thresholds, exiting multithreaded processes, UID/GID mapping, and all supported `ACCT_VERSION` encodings. Lockdep, KASAN, and fault injection around allocation/open/write paths are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/acct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/async.c -->
# sources/distributed-fs/ceph-client/kernel/async.c

## Purpose
`async.c` implements the kernel's asynchronous function call facility used primarily to improve boot performance. It lets initialization code schedule independent work on a dedicated workqueue while preserving externally visible ordering through monotonically increasing cookies and synchronization APIs.

## Important APIs, types, and functions
The core state includes global `next_cookie`, `async_global_pending`, default domain `async_dfl_domain`, `async_lock`, dedicated `async_wq`, waitqueue `async_done`, and `entry_count`. Each `struct async_entry` links into a domain pending list and the global pending list, stores the work item, cookie, callback, data, and domain.

Exported APIs include `async_schedule_node_domain()`, `async_schedule_node()`, `async_schedule_dev_nocall()`, `async_synchronize_full()`, `async_synchronize_full_domain()`, `async_synchronize_cookie_domain()`, `async_synchronize_cookie()`, and `current_is_async()`. `async_init()` allocates the dedicated unbound workqueue and raises its minimum active worker count.

## Control flow
Scheduling allocates an `async_entry`, initializes list and work fields, takes `async_lock`, assigns a cookie, appends to the domain list and possibly the global list, increments the pending count, releases the lock, and queues work on the requested NUMA node. If allocation fails or pending work exceeds `MAX_WORK`, `async_schedule_node_domain()` executes the callback synchronously after still assigning a cookie.

Execution in `async_run_entry_fn()` invokes the callback with data and cookie, logs debug timing, removes the entry from pending lists under lock, frees it, decrements the pending count, and wakes waiters. Synchronization waits until `lowest_in_progress(domain)` is at or beyond the requested cookie; a `NULL` domain means all registered domains through the global pending list.

## State and persistence behavior
All state is in-memory. Cookies are monotonic `async_cookie_t` values and represent ordering checkpoints, not durable IDs. Pending list membership is the source of truth for synchronization. The workqueue exists for the life of the kernel after `async_init()`.

## Dependencies and integration points
This file depends on workqueues, waitqueues, spinlocks, atomics, NUMA-aware `queue_work_node()`, device NUMA helpers, task PID debug output, and `workqueue_internal.h` to identify current worker functions. Boot and driver initialization code integrate by scheduling callbacks and synchronizing before publishing ordered side effects.

## Risks and invariants
The main invariant is that pending-list insertion happens before work can complete, and removal+wakeup happens after callback completion. Cookie ordering must remain consistent even for synchronous fallback. `async_schedule_dev_nocall()` intentionally differs from `async_schedule_dev()`-style behavior by returning false instead of running synchronously, so callers must handle dropped async attempts. Deadlocks are possible if callbacks wait on cookies that include themselves or if domains are misused.

## Test signals
Boot-time initcall ordering tests, driver probe tests using cookies, stress with many scheduled async jobs, allocation-failure injection, NUMA node scheduling smoke tests, and synchronization tests for domain-specific and global waits are relevant. Debug logs showing call and completion cookie order are useful for diagnosing regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/async.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/audit.c -->
# sources/distributed-fs/ceph-client/kernel/audit.c

## Purpose
`audit.c` is the core kernel audit gateway between kernel audit producers, LSMs, and userspace audit daemons. It initializes audit netlink sockets, tracks the audit daemon connection, receives audit control messages, queues audit records, performs rate/backlog/failure handling, formats audit buffers, logs task/path/network/security-context information, and exposes exported `audit_log*` APIs.

## Important APIs, types, and functions
Global control state includes `audit_initialized`, `audit_enabled`, `audit_default`, `audit_failure`, rate/backlog tunables, lost counters, audit feature bits, LSM context provider arrays, and audit queues (`audit_queue`, `audit_retry_queue`, `audit_hold_queue`). `struct auditd_connection` tracks auditd PID, portid, and net namespace under RCU. `struct audit_buffer` wraps one or more skb records sharing an audit timestamp/serial. `struct audit_net` holds the per-netns netlink socket.

Key public/exported functions include `audit_log_start()`, `audit_log_end()`, `audit_log_format()`, `audit_log()`, `audit_log_n_hex()`, `audit_log_n_string()`, `audit_log_n_untrustedstring()`, `audit_log_d_path()`, `audit_log_task_info()`, `audit_log_task_context()`, `audit_log_subj_ctx()`, `audit_log_obj_ctx()`, `audit_log_nf_skb()`, `audit_set_loginuid()`, `audit_signal_info()`, `audit_serial()`, `audit_panic()`, `audit_ctl_lock()`, and `audit_ctl_unlock()`.

## Control flow
`audit_init()` allocates the buffer cache, initializes skb queues and inode hash buckets, registers per-netns audit netlink sockets, starts `kauditd`, and emits an initialization record. Boot parameters `audit=` and `audit_backlog_limit=` set initial state. Incoming netlink messages arrive through `audit_receive()`, are serialized by `audit_cmd_mutex`, authorized by `audit_netlink_ok()`, and handled by `audit_receive_msg()`. Control cases cover status get/set, auditd registration, feature get/set, user messages, rule add/delete/list, tree trim/equivalence, signal info, and TTY audit settings.

Audit record generation starts with `audit_log_start()`: it checks initialization, exclude filters, backlog limits, and allocates an audit buffer with a timestamp/serial prefix. Formatting appends to the skb, expanding if needed. `audit_log_end()` enqueues all skbs and wakes `kauditd`. `kauditd_thread()` drains hold, retry, and main queues; it attempts unicast to auditd, multicasts to listeners, moves failed records between retry/hold queues, prints last-resort records, and wakes backlog waiters.

## State and persistence behavior
Audit records persist only after userspace auditd receives and stores them; the kernel maintains transient queues and counters. Lost records are counted in `audit_lost`, and backlog wait time is accumulated. Audit loginuid/session state is stored in each task. Feature locks and `AUDIT_LOCKED` can make configuration immutable until reboot. The auditd connection holds references to its PID and network namespace and is replaced under RCU.

## Dependencies and integration points
The file integrates with netlink, per-network namespace operations, kthreads/freezer, skbuffs, LSM security context APIs, audit filters from `auditfilter.c`, syscall audit context from `auditsc.c`, path and tty helpers, credentials, capabilities, PID/user namespaces, netfilter packet structures, and kernel panic/printk paths.

## Risks and invariants
The highest-risk areas are loss/backpressure behavior, auditd connection lifetime, and sleeping while holding the audit control mutex. The code deliberately avoids blocking auditd itself or the control-lock owner in backlog handling. `auditd_reset()` must not dereference possibly stale connection pointers. Netlink authorization is intentionally restricted to the initial user and PID namespaces for control operations. Formatting untrusted strings must preserve audit log parseability by hex-encoding unsafe content.

## Test signals
Use auditctl/auditd integration tests for status changes, daemon replacement, locked mode, feature locks, rule operations, multicast read-log listeners, backlog overflow, rate limiting, auditd disconnect/reconnect, and user messages. Add LSM multi-context tests, network skb logging tests for IPv4/IPv6/TCP/UDP/SCTP, loginuid permission tests, and fault injection for skb/kmem allocation and netlink send failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/audit.h -->
# sources/distributed-fs/ceph-client/kernel/audit.h

## Purpose
`audit.h` is the private kernel audit subsystem header. It defines internal audit state structures, especially the per-task `struct audit_context`, and declares cross-file interfaces between core audit logging, syscall auditing, rule filtering, fsnotify watches, tree watches, and audit netlink listing.

## Important APIs, types, and declarations
`enum audit_state` defines whether a task has no audit context, builds one lazily, or records always. `struct audit_entry` wraps `struct audit_krule` for filter lists and RCU freeing. `struct audit_names` stores path lookup/name data collected during audited syscalls, including inode/device, mode, ownership, object LSM properties, and file capabilities. `struct audit_context` is the large per-task syscall/io_uring record with state, timestamp, syscall arguments, return code, priority, names list, current working directory, auxiliary data, socket address, task credentials, target task info, tree references, and unions for IPC, mq, capset, mmap, openat2, execve, module, and time/NTP audit payloads.

The header declares helpers from `audit.c` (`audit_log_session_info`, `auditd_test_task`, `audit_make_reply`, `audit_panic`, `audit_ctl_lock`), from `auditfilter.c` (`audit_match_class`, comparators, path comparison, `audit_filter`, rule list/mutex symbols), and from watch/tree files (`audit_to_watch`, `audit_add_watch`, `audit_remove_watch_rule`, `audit_alloc_mark`, `audit_remove_mark`, `audit_make_tree`, `audit_add_tree_rule`, `audit_tag_tree`, `audit_kill_trees`). It provides disabled stubs when `CONFIG_AUDITSYSCALL` is off.

## Control flow and integration
The declarations encode the audit subsystem layering: core logging calls filters, filters own `audit_entry` lists and may attach watch/tree/exe objects, syscall auditing fills `audit_context`, and fsnotify callbacks update or remove rules asynchronously. Netlink list replies use `struct audit_netlink_list` and `audit_send_list_thread()`.

## State and persistence behavior
The header defines in-memory state only. Its structures determine what data can be persisted into emitted audit records. The `AUDIT_NAMES` preallocation is a performance contract: first path names are stored inline in the task context and overflow names are dynamically allocated and flagged with `should_free`.

## Dependencies and integration points
It depends on VFS path/inode types, `linux/audit.h` UAPI definitions, LSM properties, skbuffs, tty, POSIX mqueue UAPI, and `openat2` structures. It bridges files built under different configs, so its stubs must match real function signatures closely.

## Risks and invariants
`audit_context` layout and lifecycle are sensitive because many syscall audit paths fill it incrementally. `dummy` is required as the first field. Names must be managed through `names_list` rather than direct preallocated array access after setup. Stubs under `!CONFIG_AUDITSYSCALL` must fail safely without leaving callers believing watches or trees are active.

## Test signals
Compile-test audit on/off and auditsyscall on/off configurations. Runtime signals include syscall audit records with many path names, IPC/mqueue/capset/mmap/openat2/execve/time audit records, LSM context output, tree/watch rule addition, and rule-list netlink dumping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/audit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/audit_fsnotify.c -->
# sources/distributed-fs/ceph-client/kernel/audit_fsnotify.c

## Purpose
`audit_fsnotify.c` implements fsnotify-backed executable/path mark tracking for audit rules, especially `AUDIT_EXE` style filters. It associates an audit rule with a filesystem mark, tracks the target inode/device as filesystem events occur, and removes rules automatically when the marked object disappears or is unmounted.

## Important APIs, types, and functions
`struct audit_fsnotify_mark` stores the tracked device, inode, insertion path string, embedded `fsnotify_mark`, and owning `audit_krule`. The global `audit_fsnotify_group` is initialized by `audit_fsnotify_init()`. Public helpers are `audit_alloc_mark()`, `audit_remove_mark()`, `audit_remove_mark_rule()`, `audit_mark_path()`, and `audit_mark_compare()`.

`audit_update_mark()` refreshes inode/device values or sets them to unset. `audit_mark_handle_event()` is the fsnotify event callback. `audit_autoremove_mark_rule()` logs and deletes the owning rule when the mark target is invalidated. `audit_fsnotify_free_mark()` releases mark memory through `audit_fsnotify_mark_free()`.

## Control flow
Rule parsing calls `audit_alloc_mark()` with a pathname. The function rejects non-absolute paths and trailing slashes, resolves the parent and child dentry, rejects negative child dentries, allocates the mark, stores the path, records the child inode/dev, and attaches an inode mark to the parent directory with create/move/delete/self event masks. On create/move/delete events, the callback compares the event dentry name with the final path component and updates the stored inode/dev. On delete-self, unmount, or move-self events, it autoremove-deletes the rule through `audit_del_rule()`.

## State and persistence behavior
State is in-memory and tied to fsnotify marks. The persistent user-visible effect is that audit rules with executable/path conditions continue matching the current inode for a path as it is recreated or moved into place, and are removed when the watched container itself disappears.

## Dependencies and integration points
This file depends on fsnotify backend APIs, path lookup (`kern_path_parent`), audit rule deletion/logging, audit filters, LSM/security includes, and path comparison from `auditfilter.c`. `audit_watch.c` calls `audit_dupe_exe()` and `audit_exe_compare()` using these mark helpers.

## Risks and invariants
Path validation and dentry comparison are important: the mark lives on the parent directory but stores child inode/dev. If name comparison is wrong, unrelated events can retarget rules. Autoremove calls into the rule engine from fsnotify context, so locking and GFP choices (`GFP_NOFS` for logging) must avoid filesystem recursion. Mark memory ownership must leave `path` attached exactly once or cleared on attach failure.

## Test signals
Tests should cover `AUDIT_EXE` rules for an executable path, replacement by rename, deletion and recreation, parent directory move/delete/unmount, duplicate exe rule copying, and rule deletion cleanup. Fault injection for allocation and fsnotify mark attach failures is useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/audit_fsnotify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/audit_tree.c -->
# sources/distributed-fs/ceph-client/kernel/audit_tree.c

## Purpose
`audit_tree.c` implements recursive directory audit watches. It tracks audit rules bound to directory trees by tagging all relevant mount path inodes with fsnotify marks and maintaining an RCU-visible mapping from inodes to `audit_chunk` ownership records. It supports trimming stale tags, mount equivalence updates, asynchronous pruning, and delayed tree killing during syscall audit processing.

## Important APIs, types, and functions
`struct audit_tree` represents a watched path, rule list, tagged chunks, root chunk, same-root links, goner state, refcount, and pathname. `struct audit_chunk` represents one inode mark and a variable set of owning trees through embedded `audit_node` entries. `struct audit_tree_mark` embeds `fsnotify_mark` and points to the active chunk. Global state includes `tree_list`, `prune_list`, `prune_thread`, `audit_tree_group`, a mark slab cache, a 128-bucket chunk hash table, and `hash_lock`.

External APIs include `audit_make_tree()`, `audit_add_tree_rule()`, `audit_remove_tree_rule()`, `audit_trim_trees()`, `audit_tag_tree()`, `audit_tree_lookup()`, `audit_tree_match()`, `audit_put_chunk()`, `audit_tree_path()`, `audit_put_tree()`, and `audit_kill_trees()`.

## Control flow
Rule parsing creates a temporary tree with `audit_make_tree()`. Rule insertion under `audit_filter_mutex` calls `audit_add_tree_rule()`, which reuses an existing tree with the same path or adds a new tree, launches the prune thread if needed, resolves the path, collects related mount paths, and tags each inode through `tag_chunk()`. Tagging either creates a new mark/chunk or replaces an existing chunk with a larger owner set. Once tagging succeeds, temporary high-bit markers in `audit_node.index` are cleared and the rule is attached to the tree.

Removal via `audit_remove_tree_rule()` detaches the rule. If it was the last rule on a tree, the tree is marked goner, moved to `prune_list`, and the prune thread later calls `prune_one()` to untag chunks and drop references. `audit_trim_trees()` recomputes which collected paths still belong to each tree and prunes uncommitted/stale chunks. `audit_tag_tree(old,new)` handles mount equivalence by tagging trees under an old path with inodes collected from a new path. Fsnotify mark freeing calls `audit_tree_freeing_mark()`, which detaches the mark's chunk, evicts root-owning trees, and schedules or postpones pruning.

## State and persistence behavior
The watched tree rules are in audit filter lists; tree/chunk/mark state is in-memory. RCU readers in syscall audit can call `audit_tree_lookup()` on inodes and later match chunks to trees without taking the heavy filter mutex. Refcounts on trees and chunks maintain lifetime across RCU and fsnotify callbacks. No on-disk persistence is provided; userspace must reload audit rules after boot.

## Dependencies and integration points
This file depends on fsnotify internals, VFS path resolution, mount path collection, kthreads, audit rule/filter locking, RCU, spinlocks, refcounts, syscall audit tree reference collection, and audit config logging. It cooperates with `auditfilter.c` for rule insertion/removal and `auditsc.c` for `audit_killed_trees()` and inode filtering.

## Risks and invariants
The data structure is concurrency-heavy. Chunk replacement must fully initialize new chunks before RCU publication; comments explicitly pair `smp_wmb()` with data dependency reads. `hash_lock` and `audit_tree_group` mark mutex together stabilize mark-to-chunk associations. The high bit of `audit_node.index` is used as a temporary prune marker and must be preserved/cleared correctly. Error cleanup during partial tagging is complex and must not leave rules referencing goner trees or leaked chunk references.

## Test signals
Exercise recursive directory audit rules across mount points, bind mounts, path equivalence updates, deletion/unmount of watched roots, concurrent rule removal during tagging, trim operations, and syscall audit matching under rename/unmount churn. Lockdep, KCSAN, RCU stall detection, and allocation-failure injection are high-value for this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/audit_tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/audit_watch.c -->
# sources/distributed-fs/ceph-client/kernel/audit_watch.c

## Purpose
`audit_watch.c` implements non-recursive path watches for audit rules. It tracks a watched child path through an fsnotify mark on the parent directory, updates inode/device rule matching data when the child is created, moved, or deleted, and removes associated rules when the watched parent disappears.

## Important APIs, types, and functions
`struct audit_watch` stores refcount, device, path, inode, parent pointer, parent watch-list node, and rule-list anchor. `struct audit_parent` stores all watches attached to a parent inode and the embedded fsnotify mark. Public helpers include `audit_to_watch()`, `audit_add_watch()`, `audit_remove_watch_rule()`, `audit_watch_path()`, `audit_watch_compare()`, `audit_get_watch()`, `audit_put_watch()`, plus executable helpers `audit_dupe_exe()` and `audit_exe_compare()`.

Important internals include `audit_init_parent()`, `audit_init_watch()`, `audit_find_parent()`, `audit_add_to_parent()`, `audit_get_nd()`, `audit_update_watch()`, `audit_remove_parent_watches()`, and `audit_watch_handle_event()`.

## Control flow
Rule parsing calls `audit_to_watch()`, which validates absolute non-directory paths, allowed filter lists, equality operation, and mutual exclusivity with inode/tree/watch fields. Rule insertion calls `audit_add_watch()` while holding `audit_filter_mutex`; it takes a temporary watch reference, drops the mutex to resolve the parent path, reacquires the mutex, finds or creates a parent fsnotify mark, attaches the rule to an existing same-path watch or adds a new watch, and chooses the inode hash bucket for the rule list.

Fsnotify events on the parent call `audit_watch_handle_event()`. Create/move-to events update matching watches with the new inode/dev. Delete/move-from invalidates inode/dev and first runs inode filtering for the current context so pending events are not missed. Delete-self/unmount/move-self removes all watches and rules for that parent. Updating a watch duplicates affected rules, swaps RCU list entries, moves the rule to the new inode hash bucket, removes stale exe marks, and RCU-frees old entries.

## State and persistence behavior
Watch state is in-memory and rule-backed. The watched path string remains the stable user rule identity, while inode/dev fields are dynamic matching accelerators. Parent marks live until fsnotify reports `FS_IGNORED` or all watches are removed. Rules are persisted only in kernel memory until userspace deletes or reloads them.

## Dependencies and integration points
The file depends on fsnotify backend APIs, path lookup, audit filter mutex/list structures, inode hash buckets from `audit.c`, RCU rule freeing from `auditfilter.c`, path comparison helpers, and fsnotify mark helpers from `audit_fsnotify.c` for executable filters.

## Risks and invariants
The rule update path must copy-and-replace entries instead of mutating RCU-visible structures in place. Watch and parent refcounts must balance across shared same-path watches. The function deliberately drops `audit_filter_mutex` around path lookup to avoid blocking under the global filter lock; callers expect it locked again on return. Name comparison errors can update the wrong watch. Removing parent watches must also remove exe marks associated with those rules.

## Test signals
Add/delete audit watch rules, create/delete/rename the watched file, replace it with a new inode, delete/unmount/move the parent, add multiple rules for the same path, and delete rules while events occur. Verify inode hash matching after replacement and RCU safety with lockdep/KASAN/KCSAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/audit_watch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/auditfilter.c -->
# sources/distributed-fs/ceph-client/kernel/auditfilter.c

## Purpose
`auditfilter.c` implements audit rule parsing, validation, storage, listing, matching, and LSM-rule refresh. It converts userspace `struct audit_rule_data` messages into internal `struct audit_entry`/`audit_krule` objects, maintains RCU-protected filter lists and inode hash lists, and evaluates non-syscall audit filters such as user, exclude, filesystem, subject, and executable filters.

## Important APIs, types, and functions
Global state includes `audit_filter_list[]` for fast RCU filtering, `audit_rules_list[]` for ordered rule listing, and `audit_filter_mutex` for writers/blocking readers. Rule lifetime helpers include `audit_init_entry()`, `audit_free_lsm_field()`, `audit_free_rule()`, `audit_free_rule_rcu()`, and `audit_dupe_rule()`.

Parsing and serialization are handled by `audit_unpack_string()`, `audit_to_entry_common()`, `audit_field_valid()`, `audit_data_to_entry()`, `audit_pack_string()`, and `audit_krule_to_data()`. Rule operations are `audit_add_rule()`, `audit_del_rule()`, `audit_rule_change()`, `audit_list_rules_send()`, and `audit_list_rules()`. Matching helpers include `audit_register_class()`, `audit_match_class()`, `audit_comparator()`, UID/GID comparators, `parent_len()`, `audit_compare_dname_path()`, and `audit_filter()`. LSM policy reload support is in `audit_update_lsm_rules()` and `update_lsm_rule()`.

## Control flow
Netlink rule add/delete from `audit.c` calls `audit_rule_change()`. The payload is parsed by `audit_data_to_entry()`, which validates list/action/field count, expands syscall classes into masks, validates field/operator combinations, translates UID/GID values into kernel IDs, initializes LSM rules, creates watch/tree/exe helper objects, and records string buffer lengths. Add operations take `audit_filter_mutex`, reject duplicates using `audit_find_rule()`, attach watch/tree state if present, assign priority for exit/uring lists, and insert into both listing and filtering lists with RCU-safe list operations. Delete operations find the matching rule, remove watch/tree/exe attachments, update audit rule counters, remove list entries, and RCU-free the old object.

Rule listing takes the mutex, serializes each internal rule back to `audit_rule_data`, queues multipart netlink replies, and sends them from a helper kthread to avoid deadlocking auditctl. `audit_filter()` runs under RCU, evaluates fields against current task state, message type, LSM subject data, and executable mark data, and returns whether the event should be audited.

## State and persistence behavior
Rules live in memory in ordered per-list `audit_rules_list` and RCU-visible filtering lists. Inode/watch rules may live in `audit_inode_hash` buckets rather than the generic list. String fields, LSM opaque rules, watch/tree/exe marks, filter keys, syscall masks, and priorities are part of the rule state. Rule state is not durable across reboot unless userspace reloads it.

## Dependencies and integration points
This file integrates with audit netlink control, `audit.c` logging/replies, syscall audit counters under `CONFIG_AUDITSYSCALL`, LSM audit rule initialization/matching, fsnotify watch/tree/exe helpers, UID/GID namespace conversion, RCU, mutexes, and audit UAPI constants.

## Risks and invariants
Validation is security-sensitive: unsupported field/list/operator combinations must be rejected before insertion. RCU-visible rule structures must never be mutated in place; updates duplicate and replace. Watch/tree/exe setup has cross-file cleanup requirements on parse/add/delete failure. `audit_filter_mutex` synchronizes writers, while RCU readers can run concurrently, so list deletion must use `list_del_rcu()` and delayed freeing. LSM rules may be temporarily invalid across policy changes and are refreshed by duplication.

## Test signals
Use auditctl rule add/delete/list tests across all filter lists, duplicate detection, invalid field/operator/list combinations, UID/GID namespace values, syscall class expansion, filter key serialization, LSM subject/object rules before and after policy reload, watch/tree/exe rules, and concurrent filtering while replacing rules. Fault injection for allocations and LSM rule init should verify cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/auditfilter.c -->
