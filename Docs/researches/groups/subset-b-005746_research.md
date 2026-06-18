# subset-b-005746 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pipe.c -->
# sources/distributed-fs/ceph-client/fs/pipe.c

Purpose: Implements Linux anonymous pipes, FIFOs, the private `pipefs` pseudo filesystem, pipe creation syscalls, pipe buffer lifetime helpers used by splice/tee/watch queues, pipe capacity accounting, and `/proc/sys/fs/pipe-*` sysctls.

Important APIs and types: The central runtime object is `struct pipe_inode_info`, referenced through `inode->i_pipe` and `file->private_data`, with a power-of-two `struct pipe_buffer` ring, `head`/`tail`, wait queues, reader/writer/file counts, async notification lists, cached temporary pages, and per-user buffer accounting. Exported helpers include `pipe_lock()`, `pipe_unlock()`, `generic_pipe_buf_try_steal()`, `generic_pipe_buf_get()`, `generic_pipe_buf_release()`, `alloc_pipe_info()`, `free_pipe_info()`, `create_pipe_files()`, `do_pipe_flags()`, `pipe_wait_readable()`, `pipe_wait_writable()`, `round_pipe_size()`, `pipe_resize_ring()`, `get_pipe_info()`, and `pipe_fcntl()`. User-facing entry points include `SYSCALL_DEFINE2(pipe2)`, `SYSCALL_DEFINE1(pipe)`, `pipefifo_fops`, and the anonymous pipe file operations.

Control flow: `init_pipe_fs()` registers and kernel-mounts `pipefs`, then installs pipe sysctls when `CONFIG_SYSCTL` is enabled. `pipe2()` validates flags, creates a pseudo inode with `get_pipe_inode()`, allocates paired read/write files with `create_pipe_files()`, reserves file descriptors, copies them to userspace, and installs the files. Reads lock the pipe, drain ring buffers in FIFO order, honor packet/whole-buffer flags, inject watch-queue loss notifications, advance `tail`, and wake writers when space becomes available. Writes reject notification pipes, merge small data into the last mergeable buffer when possible, allocate/copy pages into new ring slots, signal readers on transition from empty, and block or return `-EAGAIN`/`-EPIPE` as required. FIFO open adds the missing endpoint accounting and may wait for a partner unless nonblocking rules allow immediate return.

State and persistence: Pipe state is in memory only and persists while any pipe or FIFO file references the inode. `pipe->files`, reader/writer counters, and `put_pipe_info()` determine teardown; `free_pipe_info()` releases unread buffers, cached pages, watch queues, and user page charges. `pipe_max_size`, `pipe_user_pages_hard`, and `pipe_user_pages_soft` are global tunables exposed through sysctl and used by allocation and resize paths. Anonymous pipe inodes live on the internal pipefs mount and expose dynamic names such as `pipe:[ino]` through dentry operations.

Dependencies and integration points: This file integrates with VFS file operations, pseudo filesystems, fd allocation/audit, wait queues, poll/epoll, fasync/SIGIO, splice, memcg accounting, user_struct quota accounting, sysctl, watch queues, uaccess/iov_iter, and capability checks for privileged resizing. It also supplies `get_pipe_info()` for splice-like paths that need to detect real pipes and avoid notification pipes.

Risks: Correctness depends on subtle locking between `pipe->mutex`, `rd_wait.lock` for watch-queue posting, and lock ordering in `pipe_double_lock()`. Wait/wakeup behavior must avoid lost wakeups and excessive wake storms, especially with epoll historical semantics and GNU make jobserver-style token pipes. Page ownership and steal/merge flags are security-sensitive because splice can transfer pages between subsystems. Quota enforcement must roll back user page charges on every allocation or resize failure. In this repository snapshot, visible duplicated lines and a malformed-looking extra brace around `pipe_ioctl()`/`pipe_resize_ring()` are source-integrity risks to validate before building.

Test signals: Exercise `pipe()`/`pipe2()` flag validation, blocking and nonblocking reads/writes, `O_DIRECT` packetized pipes, `FIONREAD`, `F_SETPIPE_SZ`/`F_GETPIPE_SZ`, per-user soft/hard limits, zero-length IO, SIGPIPE and SIGIO behavior, poll/epoll readiness after endpoint close, FIFO open partner waits, splice/tee page stealing, notification-pipe ioctl paths, sysctl rounding, and teardown with unread buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pnode.c -->
# sources/distributed-fs/ceph-client/fs/pnode.c

Purpose: Implements mount propagation graph operations for shared, slave, private, and unbindable mounts. It decides how new mounts, propagation-mode changes, and unmounts replicate across peer groups and slave chains in a mount namespace.

Important APIs and types: The file works on `struct mount`, peer lists (`mnt_share`), slave lists (`mnt_slave_list`/`mnt_slave`), `mnt_master`, mount flags such as `T_SHARED`, `T_UNBINDABLE`, `T_MARKED`, `T_UMOUNT_CANDIDATE`, and namespace roots. Public functions include `get_dominating_id()`, `change_mnt_propagation()`, `bulk_make_private()`, `propagate_mnt()`, `propagation_would_overmount()`, `propagate_mount_busy()`, `propagate_mount_unlock()`, and `propagate_umount()`.

Control flow: Propagation-mode changes remove mounts from peer groups, release group IDs, move slave lists to new masters, and set unbindable/private/shared flags. `bulk_make_private()` first traces propagation transfers for a set being detached, marks intermediate nodes, then rewires slaves and clears marks. `propagate_mnt()` walks destination peer groups and their slave subtrees, uses `copy_tree()` to create secondary copies, links them under matching mountpoints, preserves shared/slave relationships, adds the new mounts to the caller's tree list, and checks namespace mount counts. `propagate_umount()` gathers propagated candidates, trims mounts blocked by visible children or locks, reparents surviving overmounts, and appends accepted propagated unmounts to the caller's set.

State and persistence: All state is stored in the global mount graph: peer group IDs, master/slave links, namespace membership, child mount lists, transient mark bits, and `MNT_UMOUNT`. There is no persistent storage. The functions assume namespace and mount locks documented in comments, and their side effects directly reshape the in-memory namespace graph.

Dependencies and integration points: Integrates with `namespace.c`/mount internals through `copy_tree()`, `count_mounts()`, `mnt_set_mountpoint()`, `mnt_change_mountpoint()`, `move_from_ns()`, `mnt_notify_add()`, `__lookup_mnt()`, `is_path_reachable()`, and mount namespace locking. It relies on path reachability and anonymous namespace detection to skip mounts that should not receive propagated copies.

Risks: Propagation logic is graph-sensitive; stale `T_MARKED` or candidate bits can corrupt later traversals. Unmount propagation must not detach mounts that are visible through locked or non-overmounted children, and reparenting temporarily violates parent/mountpoint uniqueness until the caller detaches the stack. `propagate_mnt()` must clean marks on all error paths and avoid overmounting propagation loops. The source contains duplicated comment text and compact control flow that makes audit of candidate trimming important.

Test signals: Cover shared-peer mount creation, slave chains, unbindable/private transitions, recursive bind/mount propagation, mount count limit failures, overmount detection, unmount propagation with locked mounts, surviving overmount reparenting, namespace-root-limited dominating IDs, and stress tests with deep peer/slave hierarchies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pnode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pnode.h -->
# sources/distributed-fs/ceph-client/fs/pnode.h

Purpose: Declares mount propagation helpers and flag macros shared by mount namespace code and `pnode.c`.

Important APIs and types: Defines predicates and mutators for propagation flags, including `IS_MNT_SHARED()`, `IS_MNT_SLAVE()`, `IS_MNT_NEW()`, `CLEAR_MNT_SHARED()`, `IS_MNT_UNBINDABLE()`, `IS_MNT_MARKED()`, `SET_MNT_MARK()`, `CLEAR_MNT_MARK()`, and `IS_MNT_LOCKED()`. It defines copy/clone flags such as `CL_EXPIRE`, `CL_SLAVE`, `CL_COPY_UNBINDABLE`, `CL_MAKE_SHARED`, `CL_PRIVATE`, and `CL_COPY_MNT_NS_FILE`. Inline helpers `set_mnt_shared()` and `peers()` encapsulate shared group setup and peer-group equality.

Control flow: The header itself has no runtime flow beyond inline flag updates. It exposes the public propagation surface used by namespace operations: propagation-mode changes, mount-copy propagation, unmount propagation, busy/unlock checks, group ID release, mountpoint updates, copy-tree helpers, reachability, mount counting, and overmount prediction.

State and persistence: The macros directly mutate or inspect `struct mount` fields such as `mnt_t_flags`, `mnt_group_id`, `mnt_master`, and `mnt.mnt_flags`. These fields are transient kernel mount namespace state, protected by namespace/mount locks in callers.

Dependencies and integration points: Includes `linux/list.h` and local `mount.h`, so it is tightly coupled to the VFS mount implementation. Callers include mount namespace setup, bind/clone paths, mount propagation code, and unmount logic.

Risks: Because these are low-level macros, callers must hold the documented locks and avoid double-evaluating expressions with side effects. `peers()` requires a nonzero group ID, which prevents unrelated private mounts with ID zero from comparing as peers. Incorrect use of `CL_*` flags can silently change propagation behavior across namespaces.

Test signals: Compile coverage from namespace/mount code, mount propagation xfstests, shared/slave/private flag transitions, recursive bind tests with unbindable mounts, and lockdep coverage around `set_mnt_shared()` callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/pnode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/posix_acl.c -->
# sources/distributed-fs/ceph-client/fs/posix_acl.c

Purpose: Provides generic VFS support for POSIX ACL caching, validation, permission checking, mode/ACL conversion, xattr encoding/decoding, simple filesystem ACL helpers, and VFS get/set/remove ACL wrappers with idmapped mount and LSM handling.

Important APIs and types: The file centers on `struct posix_acl`, `struct posix_acl_entry`, inode ACL cache slots `i_acl` and `i_default_acl`, ACL tags such as `ACL_USER_OBJ`, `ACL_USER`, `ACL_GROUP_OBJ`, `ACL_GROUP`, `ACL_MASK`, and `ACL_OTHER`, and xattr names for access/default ACLs. Key exports include `get_cached_acl()`, `get_cached_acl_rcu()`, `set_cached_acl()`, `forget_cached_acl()`, `forget_all_cached_acls()`, `get_inode_acl()`, `posix_acl_alloc()`, `posix_acl_clone()`, `posix_acl_valid()`, `posix_acl_equiv_mode()`, `posix_acl_from_mode()`, `__posix_acl_create()`, `__posix_acl_chmod()`, `posix_acl_chmod()`, `posix_acl_create()`, `posix_acl_update_mode()`, `posix_acl_from_xattr()`, `posix_acl_to_xattr()`, `set_posix_acl()`, `vfs_set_acl()`, `vfs_get_acl()`, `vfs_remove_acl()`, `do_set_acl()`, and `do_get_acl()`.

Control flow: Cache lookup uses RCU and sentinel values to serialize racing `get_acl`/`set_acl` operations without a global lock. Validation enforces canonical ACL entry ordering and id mappings. Permission checks scan entries in order, select owner/user/group/other permissions, and apply the mask entry when needed. Creation and chmod clone ACLs, mask entries against requested modes, and either retain or discard ACLs based on mode equivalence. VFS set/remove paths parse ACL names, translate ids for idmapped mounts, lock the inode, check write-xattr permissions, call LSM hooks, break delegations, invoke filesystem `set_acl`, and notify fsnotify/security post hooks. VFS get paths invoke LSM, reject unsupported/symlink cases, fetch/cache ACLs, and convert to userspace xattr format on demand.

State and persistence: The VFS cache stores positive, negative, and sentinel ACL values in inode fields and releases refcounted ACL objects through `posix_acl_release()`. Persistent ACL storage is delegated to filesystem `get_acl`, `get_inode_acl`, and `set_acl` operations, commonly backed by extended attributes. Simple in-memory filesystems can use `simple_set_acl()` and `simple_acl_create()` to keep ACL state in inode cache only.

Dependencies and integration points: Integrates with inode operations, xattr APIs, idmapped mount helpers (`mnt_idmap`, `vfsuid`, `vfsgid`), user namespaces, LSM hooks, delegation breaking, fsnotify, inode versioning, mode update rules, and permission checks. It is a shared service used by filesystems rather than a standalone filesystem.

Risks: ACL cache races are subtle; sentinel cleanup must happen on errors so future lookups are not blocked. Idmapped mount translation must occur only at VFS/userspace boundaries or set paths, not when caching filesystem-wide ACLs. Mode updates must clear setgid when required. Default ACLs must be accepted only on directories. In this repository snapshot, duplicate `return PTR_ERR(acl);` in `posix_acl_chmod()` is harmless but indicates copied-source integrity should be checked.

Test signals: Validate canonical and malformed ACLs, missing uid/gid mappings, cache hit/miss/race behavior, chmod/create ACL masking, default ACL inheritance for files and directories, xattr get/set/remove through idmapped mounts, LSM denial paths, delegation retry paths, symlink rejection, and simple filesystem helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/posix_acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/Kconfig -->
# sources/distributed-fs/ceph-client/fs/proc/Kconfig

Purpose: Defines Kconfig switches controlling procfs and optional `/proc` features.

Important APIs and types: User-visible symbols include `PROC_FS`, `PROC_KCORE`, `PROC_VMCORE`, `PROC_VMCORE_DEVICE_DUMP`, `NEED_PROC_VMCORE_DEVICE_RAM`, `PROC_VMCORE_DEVICE_RAM`, `PROC_SYSCTL`, `PROC_PAGE_MONITOR`, `PROC_CHILDREN`, `PROC_PID_ARCH_STATUS`, and `PROC_CPU_RESCTRL`. These symbols gate compilation in the proc Makefile and many `#ifdef` paths in proc sources.

Control flow: Kconfig has no runtime flow. During configuration, `PROC_FS` defaults to enabled; dependent options select or depend on crash dump, MMU, sysctl, page-monitoring, boot/crash, and architecture support. Help text documents user-visible files such as `/proc/kcore`, `/proc/vmcore`, `/proc/sys`, page monitoring files, and `/proc/<pid>/task/<tid>/children`.

State and persistence: Configuration choices are persisted in the kernel `.config` and compiled into the kernel image. They determine which proc entries can exist at runtime, but this file does not manage runtime state itself.

Dependencies and integration points: Drives `fs/proc/Makefile` object selection and conditional code in proc files such as `base.c`, `array.c`, `page.c`, `proc_sysctl.c`, `kcore.c`, and `vmcore.c`. It also selects `SYSCTL` and `VMCORE_INFO` where necessary.

Risks: Disabling `PROC_FS` or `PROC_SYSCTL` can break userspace assumptions. Enabling crash/core interfaces exposes sensitive kernel memory/dump data and must rely on their runtime permission checks. `PROC_CHILDREN` is off by default because it provides a specialized interface with consistency caveats.

Test signals: Build matrix with procfs enabled/disabled, MMU and crash-dump combinations, sysctl enabled/disabled, page-monitoring enabled/disabled, and boot tests verifying expected proc entries appear or are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/Makefile -->
# sources/distributed-fs/ceph-client/fs/proc/Makefile

Purpose: Lists procfs objects and conditionally includes feature-specific files according to kernel configuration.

Important APIs and types: Builds `proc.o` from `proc-y` members. Core objects include `inode.o`, `root.o`, `base.o`, `generic.o`, `array.o`, `fd.o`, and common global proc files such as `cmdline.o`, `consoles.o`, `cpuinfo.o`, `devices.o`, `interrupts.o`, `loadavg.o`, `meminfo.o`, `stat.o`, `uptime.o`, `util.o`, `version.o`, `softirqs.o`, `namespaces.o`, `self.o`, and `thread_self.o`. Conditional objects include `task_mmu.o` or `task_nommu.o`, `proc_tty.o`, `proc_sysctl.o`, `proc_net.o`, `kcore.o`, `vmcore.o`, `kmsg.o`, `page.o`, and `bootconfig.o`.

Control flow: Kbuild aggregates `proc-y` into the procfs built-in object. `CONFIG_MMU` selects the task memory implementation, while other config symbols append optional proc subsystems.

State and persistence: The Makefile does not hold runtime state. Its choices persist only as compiled object composition in a kernel build.

Dependencies and integration points: Integrates with the Kconfig symbols in `fs/proc/Kconfig` and top-level kernel build. The warning suppression for `task_mmu.o` is a targeted compiler flag adjustment.

Risks: Missing a core object can remove proc entry registration or inode operations. Wrong conditional selection between MMU/NOMMU task memory code changes `/proc/<pid>/maps` and related behavior. Optional object gates must match their source-level `#ifdef`s.

Test signals: Build procfs across MMU/NOMMU, NET, TTY, SYSCTL, PRINTK, KCORE, VMCORE, PAGE_MONITOR, and BOOT_CONFIG configurations; boot smoke tests should confirm core and optional entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/array.c -->
# sources/distributed-fs/ceph-client/fs/proc/array.c

Purpose: Formats per-task proc status/stat/statm data and the optional `/proc/<pid>/task/<tid>/children` file.

Important APIs and types: Public entry points include `proc_task_name()`, `render_sigset_t()`, `proc_pid_status()`, `proc_tid_stat()`, `proc_tgid_stat()`, `proc_pid_statm()`, and, under `CONFIG_PROC_CHILDREN`, `proc_tid_children_operations`. It works with `task_struct`, `signal_struct`, `mm_struct`, `pid_namespace`, `cred`, signal sets, capabilities, cpumasks, time namespaces, delay accounting, and architecture hooks such as `arch_proc_pid_thread_features()`.

Control flow: Status output starts with task name, then emits state, IDs, credentials, namespace PID views, memory data, signal sets, capabilities, seccomp/speculation state, CPU affinity, cpuset data, context-switch counts, and optional architecture fields. `do_task_stat()` collects task/session/tty/fault/cputime/mm data under the appropriate locks, applies ptrace restrictions to sensitive addresses, converts boot time through time namespaces, and emits the legacy space-delimited `/proc/<pid>/stat` layout. `proc_pid_statm()` emits virtual memory counters from `task_statm()`. The children seq file walks the parent task's children under `tasklist_lock`, with a fast continuation path when the previous pid is still valid.

State and persistence: It does not store proc state; it snapshots live task, signal, mm, credential, and namespace state when files are read. Values can race with task exit or mutation by design, and references such as `get_task_mm()` and `get_task_cred()` bound object lifetime during formatting.

Dependencies and integration points: Called by the pid entry tables in `base.c`. Integrates with scheduler accounting, ptrace permission checks, memory management, cpusets, capabilities, seccomp, time namespaces, NUMA balancing, coredump state, and procfs seq/file operations.

Risks: `/proc/<pid>/stat` is ABI-sensitive and field order must remain stable. Address and wchan exposure must obey ptrace gating to avoid information leaks. Children enumeration is explicitly approximate under concurrent exit and can skip tasks. The code must avoid holding locks while doing slow seq output except for short protected snapshots.

Test signals: Compare `/proc/self/status`, `stat`, and `statm` field formats with procps expectations; test non-dumpable and ptrace-denied processes; PID namespaces; time namespaces; kthreads/workqueue names; seccomp/capability output; coredump state; and `CONFIG_PROC_CHILDREN` with concurrent child exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/array.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/base.c -->
# sources/distributed-fs/ceph-client/fs/proc/base.c

Purpose: Implements the per-process and per-thread procfs directory hierarchy: `/proc/<pid>`, `/proc/<pid>/task/<tid>`, their dynamic entry tables, lookup/readdir/inode instantiation, permission behavior, symlink resolution, memory access files, and many task control/status files.

Important APIs and types: Core types are `struct pid_entry`, `union proc_op`, `struct proc_inode`, `struct task_struct`, `struct pid`, `struct proc_fs_info`, and generated inode/dentry operations. Major exported or shared functions include `proc_nochmod_setattr()`, `proc_pid_make_inode()`, `proc_pid_evict_inode()`, `task_dump_owner()`, `pid_getattr()`, `pid_update_inode()`, `pid_delete_dentry()`, `proc_fill_cache()`, `proc_flush_pid()`, `proc_pid_lookup()`, `proc_pid_readdir()`, `tgid_pidfd_to_pid()`, and `set_proc_pid_nlink()`. The `tgid_base_stuff` and `tid_base_stuff` arrays define most visible entries.

Control flow: Numeric lookup under `/proc` parses the pid name, finds a task in the proc pid namespace, applies `hidepid` rules, creates a base inode tied to the pid, and installs pid dentry operations. Directory reads first emit `self` and `thread-self`, then iterate TGIDs with `find_ge_pid()` and instantiate entries through `proc_fill_cache()` to keep inode numbers consistent. Per-pid entry lookup searches `pid_entry` tables and instantiates regular files, directories, symlinks, or one-shot seq files with the table-provided operations. `/proc/<pid>/task` iterates thread group members and stores a readdir continuation cookie in `file->private_data`.

State and persistence: Proc pid inodes are ephemeral cache objects referencing a `struct pid`; directory inodes are linked into `pid->inodes` so `proc_flush_pid()` can invalidate dentries when a task exits. File contents are snapshots or live operations over task, mm, files, signal, namespace, audit, scheduler, cgroup, security, and timer state. The early `proc_mem.force_override=` parameter persists as a boot-time policy for whether `/proc/<pid>/mem` uses `FOLL_FORCE`.

Dependencies and integration points: Integrates with ptrace permission checks, `hidepid` mount options, user namespaces, pid namespaces, scheduler/autogroup, audit, LSM process attributes, cgroups, cpusets, namespaces, memory management (`maps`, `mem`, `environ`, `auxv`, `map_files`), timers, fault injection, OOM adjustment, checkpoint/restore, KSM, livepatch, and fd handling from `fd.c`. It also calls operations implemented in `array.c`, `task_mmu.o`/`task_nommu.o`, namespaces, mount reporting, and security modules.

Risks: This file is security-sensitive. Permission must be checked at operation time because task credentials and dumpability can change after open. `/proc/<pid>/mem`, `map_files`, symlink following, stack, syscall, and wchan paths can leak or modify sensitive state if ptrace/capability checks regress. Dentry revalidation must handle task exit without use-after-free. The pid-entry arrays are ABI surfaces, so renames/mode changes are high risk. In this snapshot, duplicate initializer/comment lines and repeated text indicate source-integrity issues to verify before compilation.

Test signals: Exercise hidepid modes, PID namespaces, setuid/non-dumpable transitions after opening proc files, `/proc/self` and `/proc/thread-self`, pid/task directory readdir under concurrent exit, symlink readlink/get_link for `cwd`/`root`/`exe`, `/proc/<pid>/mem` read/write policy combinations, `oom_adj`/`oom_score_adj`, uid/gid/projid maps and setgroups, LSM attr directories, map_files permission checks, timers, coredump_filter, task comm same-thread-group exception, and pidfd conversion through TGID directory files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/bootconfig.c -->
# sources/distributed-fs/ceph-client/fs/proc/bootconfig.c

Purpose: Exposes parsed boot configuration through `/proc/bootconfig` when boot config support is built.

Important APIs and types: Uses `saved_boot_config`, bootconfig iterators such as `xbc_for_each_key_value()`, `xbc_node_compose_key()`, `xbc_node_get_child()`, `xbc_array_for_each_value()`, `xbc_node_is_array()`, `cmdline_has_extra_options()`, and `boot_command_line`. Registers a proc single file with `proc_create_single()`.

Control flow: At `fs_initcall`, `proc_boot_config_init()` computes the required output length by calling `copy_xbc_key_value_list(NULL, 0)`, allocates a buffer, fills it with formatted `key = "value"` lines and optional bootloader parameter comments, then creates `/proc/bootconfig`. Reads simply dump the saved buffer through `boot_config_proc_show()`.

State and persistence: The formatted boot config is copied once into `saved_boot_config` during init and persists for the lifetime of the kernel. It is a read-only snapshot of early boot configuration rather than live state.

Dependencies and integration points: Depends on `CONFIG_BOOT_CONFIG` object selection, the bootconfig parser, procfs single-file helpers, slab allocation, and global boot command-line data.

Risks: The two-pass length computation depends on `snprintf()` accounting and stable bootconfig data between passes. Quote selection must preserve values containing double quotes. Allocation failure prevents the file from containing data but returns an init error only for allocation/format failures; proc creation is not checked for failure.

Test signals: Boot with no bootconfig, scalar values, arrays, values containing quotes, extra bootloader options, and long key/value lists; verify `/proc/bootconfig` formatting and absence/presence with `CONFIG_BOOT_CONFIG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/bootconfig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/cmdline.c -->
# sources/distributed-fs/ceph-client/fs/proc/cmdline.c

Purpose: Registers `/proc/cmdline`, exposing the saved kernel command line.

Important APIs and types: Uses `saved_command_line`, `saved_command_line_len`, `proc_create_single()`, `pde_make_permanent()`, and `struct proc_dir_entry`.

Control flow: `proc_cmdline_init()` creates a single-read proc file named `cmdline`, marks it permanent, and sets its size to the command-line length plus newline. `cmdline_proc_show()` writes the saved command line and a trailing newline.

State and persistence: The file reflects the boot-time `saved_command_line`; it does not change after initialization.

Dependencies and integration points: Built as a core proc object and registered at `fs_initcall`. Uses proc generic helpers and seq_file output.

Risks: Assumes proc entry creation succeeds before dereferencing the returned `pde`. Size metadata must match the emitted newline. The command line may include sensitive boot parameters, so access mode and system policy matter.

Test signals: Boot with empty and long command lines, verify size/read output and permanent-entry behavior, and ensure `/proc/cmdline` exists when procfs is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/cmdline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/consoles.c -->
# sources/distributed-fs/ceph-client/fs/proc/consoles.c

Purpose: Implements `/proc/consoles`, listing registered kernel consoles, capabilities, flags, and device numbers.

Important APIs and types: Uses `struct console`, console flag bits (`CON_ENABLED`, `CON_CONSDEV`, `CON_BOOT`, `CON_NBCON`, `CON_PRINTBUFFER`, `CON_BRL`, `CON_ANYTIME`), `struct tty_driver`, `console_list_lock()`, `console_lock()`, and seq operations registered with `proc_create_seq()`.

Control flow: The seq iterator locks the console list in `c_start()`, walks consoles with `for_each_console()` and hlist next pointers, and unlocks in `c_stop()`. `show_console_dev()` optionally calls a console's `device()` callback under `console_lock()`, computes the device number, formats read/write/unblank capability letters, flag letters, and major:minor output.

State and persistence: It stores no private persistent state; each read traverses the current console list. Locking snapshots enough state to avoid unsafe list traversal and serialize device callback state.

Dependencies and integration points: Integrates with printk console registration, TTY drivers, procfs seq files, and device number formatting.

Risks: Console list traversal must hold the list lock for seq iteration lifetime. Device callback serialization is needed because console state such as foreground VT can change under `console_lock()`. Formatting is userspace-visible and should remain stable.

Test signals: Systems with early boot consoles, real tty consoles, net/nbcon consoles, braille consoles, console unregister/register races, and reads while switching virtual terminals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/consoles.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/cpuinfo.c -->
# sources/distributed-fs/ceph-client/fs/proc/cpuinfo.c

Purpose: Registers `/proc/cpuinfo` and delegates architecture-specific CPU information iteration to `cpuinfo_op`.

Important APIs and types: Uses external `const struct seq_operations cpuinfo_op`, `cpuinfo_open()`, `cpuinfo_proc_ops`, `proc_create()`, and seq read/seek/release helpers.

Control flow: `proc_cpuinfo_init()` creates the proc entry. Opening the file calls `seq_open(file, &cpuinfo_op)`, and read/lseek/release are handled by generic seq_file operations.

State and persistence: This file stores no CPU state; architecture code behind `cpuinfo_op` supplies live or boot-time CPU data.

Dependencies and integration points: Integrates with arch CPU info providers, cpufreq headers, procfs, and seq_file. The proc ops are marked `PROC_ENTRY_PERMANENT`.

Risks: Correctness mostly depends on the architecture `cpuinfo_op`. Proc registration failure is not checked. Output format is userspace ABI for many tools.

Test signals: Boot on each architecture, hotplug CPUs if supported, verify seq iteration across all CPUs, and compare expected `/proc/cpuinfo` fields after cpufreq/topology changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/cpuinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/devices.c -->
# sources/distributed-fs/ceph-client/fs/proc/devices.c

Purpose: Implements `/proc/devices`, listing registered character and, when block support is enabled, block device majors.

Important APIs and types: Uses `chrdev_show()`, `blkdev_show()`, `CHRDEV_MAJOR_MAX`, `BLKDEV_MAJOR_MAX`, seq operations, `proc_create_seq()`, and `pde_make_permanent()`.

Control flow: The seq iterator uses the file position as a major-number index. `devinfo_show()` prints a character-device header at index zero, calls `chrdev_show()` for character majors, then prints a block-device header and calls `blkdev_show()` for block majors after offsetting past character majors. Iteration stops after the combined major range.

State and persistence: No state is stored here; reads reflect current registered device majors maintained by char/block device subsystems.

Dependencies and integration points: Integrates with procfs seq files, char device registration, optional block device registration, and permanent proc entry handling.

Risks: Off-by-one errors in position handling could omit major zero headers or overrun the valid range. Output format is traditional and consumed by scripts. With `CONFIG_BLOCK` disabled, the combined range still includes `BLKDEV_MAJOR_MAX` in the iterator condition even though only character output is produced for the first range.

Test signals: Register/unregister char and block majors, read while registrations change, build with and without `CONFIG_BLOCK`, and verify header placement and termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/devices.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/fd.c -->
# sources/distributed-fs/ceph-client/fs/proc/fd.c

Purpose: Implements `/proc/<pid>/fd` symlinks and `/proc/<pid>/fdinfo` files for per-task file descriptors.

Important APIs and types: Exports `proc_fd_operations`, `proc_fd_inode_operations`, `proc_fdinfo_operations`, `proc_fdinfo_inode_operations`, and `proc_fd_permission()`. It uses `struct fd_data`, `proc_fd(inode)`, `fget_task()`, `fget_task_next()`, `files_lookup_fd_locked()`, `show_fd_locks()`, `file->f_op->show_fdinfo`, `proc_pid_link_inode_operations`, and dentry revalidation through `tid_fd_dentry_operations`.

Control flow: Lookup parses a numeric fd name, verifies that the target task still has the fd, captures mode, and instantiates either a symlink inode for `/fd/N` or a regular file for `/fdinfo/N`. Readdir emits numeric fd names by iterating open descriptors with `fget_task_next()` and filling proc cache entries. `/fd/N` symlink resolution gets the target file path and jumps to it. `/fdinfo/N` opens a single seq file that snapshots position, flags including close-on-exec, mount ID, inode number, locks, and optional file-specific fdinfo.

State and persistence: It stores the descriptor number in `PROC_I(inode)->fd`; actual file state remains in the target task's `files_struct`. Dentries are revalidated by checking whether the fd still exists and updating inode ownership/mode from the current file mode. Directory getattr reports the current count of open fds.

Dependencies and integration points: Integrates with `base.c` pid inode helpers, task files locking, fd tables, ptrace permissions, path/mount reporting, file locks, security task-to-inode labeling, and the common proc symlink operations.

Risks: Permission rules are security-sensitive: `/fdinfo` requires ptrace read access, while `/fd` has a same-thread-group exception for `/proc/self/fd` after setuid. Revalidation must avoid RCU lookup when it cannot safely ref target files. Iteration races with close/open and should remain robust. In this snapshot, duplicated loop text in `proc_readfd_common()` should be checked before compiling.

Test signals: Open/close descriptors while reading directories, readlink regular files/sockets/pipes/deleted files, close-on-exec flag reporting, fdinfo for epoll/eventfd/timerfd where `show_fdinfo` exists, permission checks across users and same thread group after setuid, directory size count, and task exit during lookup/read.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/fd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/fd.h -->
# sources/distributed-fs/ceph-client/fs/proc/fd.h

Purpose: Declares the proc fd/fdinfo operations used by the per-pid entry tables.

Important APIs and types: Exposes `proc_fd_operations`, `proc_fd_inode_operations`, `proc_fdinfo_operations`, `proc_fdinfo_inode_operations`, `proc_fd_permission()`, and inline `proc_fd()` which returns `PROC_I(inode)->fd`.

Control flow: The header has no complex runtime flow. Its inline helper maps a proc inode to the descriptor number stored by fd/fdinfo instantiation.

State and persistence: State is the `fd` field embedded in `struct proc_inode`; the header only provides access to it.

Dependencies and integration points: Includes `linux/fs.h` and relies on proc internal definitions available to includers. It is included by `base.c` for entry tables and by `fd.c` for implementation.

Risks: `proc_fd()` assumes the inode is a proc inode instantiated by fd handling. Using it on the wrong inode would read unrelated proc inode state. Operation declarations must stay synchronized with `fd.c`.

Test signals: Compile coverage through `base.c` and `fd.c`, lookup/read of fd and fdinfo entries, and permission tests that call `proc_fd_permission()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/fd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/generic.c -->
# sources/distributed-fs/ceph-client/fs/proc/generic.c

Purpose: Provides generic procfs directory-entry management: `struct proc_dir_entry` allocation/freeing, name lookup, directory iteration, dynamic inode numbers, proc entry creation helpers, and removal/rundown.

Important APIs and types: Uses global `proc_subdir_lock`, `proc_dir_entry_cache`, red-black trees under each directory `subdir`, `proc_inum_ida`, and `struct proc_dir_entry` fields such as name, mode, nlink, proc ops, seq ops, data, parent, flags, refcount, and in-use state. Exported APIs include `proc_symlink()`, `_proc_mkdir()`, `proc_mkdir_data()`, `proc_mkdir_mode()`, `proc_mkdir()`, `proc_create_mount_point()`, `proc_create_data()`, `proc_create()`, `proc_create_seq_private()`, `proc_create_single_data()`, `proc_set_size()`, `proc_set_user()`, `remove_proc_entry()`, `remove_proc_subtree()`, `proc_get_parent_data()`, and `proc_remove()`.

Control flow: Creation parses slash-separated proc names, finds the parent, validates the final component, allocates a PDE, initializes ownership/mode/name/refcount, sets operation flags, allocates a dynamic inode number, and inserts the entry into the parent RB tree under a write lock. Lookup finds a child PDE under a read lock, pins it, creates a VFS inode with `proc_get_inode()`, and splices a dentry with the appropriate dentry ops. Readdir walks the RB tree by position, pins entries while emitting, and releases them after advancing. Removal erases entries from the tree, refuses permanent entries, runs `proc_entry_rundown()`, warns on non-empty single removal, and drops references; subtree removal recursively erases children before rundown.

State and persistence: The proc entry tree is in-memory global procfs metadata. Dynamic inode numbers are allocated from an IDA range starting at `PROC_DYNAMIC_FIRST`. Entry lifetime is controlled by PDE refcounts and in-use/rundown synchronization; no on-disk state exists.

Dependencies and integration points: Integrates with proc root setup, VFS inode/dentry operations, seq_file and single_open helpers, module-exported proc creation APIs used by drivers/subsystems, proc net force-lookup behavior, and `proc_get_inode()`/`proc_entry_rundown()` from proc internals.

Risks: Global tree locking and PDE refcounts must prevent use-after-free while allowing concurrent lookup/readdir/remove. Name translation must not allow manual creation of numeric `/proc/<pid>` entries. Permanent entries must not be removed. Recursive removal must not leak children if a permanent child is encountered. In this snapshot, duplicated `return`/assignment lines in a few paths should be source-integrity checked.

Test signals: Create/remove regular, seq, single, symlink, mount-point, and directory entries; nested names; duplicate registration warnings; removal during open/read; subtree removal; permanent-entry removal refusal; pidonly procfs mode hiding non-pid entries; proc net force lookup; and dynamic inode allocation/free reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/generic.c -->
