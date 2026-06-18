# Group Research: group_554_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_m_8e1488690c29

Scope confirmed against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. Read all seven listed source files completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/modsubr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/modsubr.c

## Purpose

`modsubr.c` provides support routines for the illumos module and driver binding subsystem. It maps driver names to major numbers, manages driver `dev_ops` holds, installs module call stubs, initializes `devnames`, tracks syscall names, parses driver `.conf` attachment data into parent/class lists, and indexes `.conf` child specs for nexus lookup.

Read completely: 1,154 lines.

## Main Responsibilities

- Validates and queries driver major-number state with `major_valid()`, `driver_installed()`, and `driver_active()`.
- Holds and releases loaded driver `dev_ops` by major number or `dev_info_t`, autoloading drivers when needed.
- Provides default `nomod_*` stub functions for absent modules.
- Installs, uninstalls, and resets module stubs through `install_stubs_by_name()`, `init_stubs()`, `install_stubs()`, `uninstall_stubs()`, and `reset_stubs()`.
- Maintains name-to-major and name-to-syscall binding hash tables.
- Initializes `devnamesp` from boot-time bindings and creates individual driver name slots.
- Parses and attaches `driver.conf` parent lists and global properties to `devnames`.
- Maintains hashed `.conf` child specs by parent name/path and exported class name.

## Key Data Structures And Globals

- `mb_hashtab`: driver/module name and alias to major-number hash.
- `sb_hashtab`: syscall name to syscall-number hash.
- `struct bind`: hash entry with key name, numeric binding, optional binding name, and deletion-by-negative-number state.
- `devnamesp`: global per-major driver metadata array populated by `init_devnamesp()` and `make_devname()`.
- `hwc_par_hash`: `.conf` child specs keyed by parent path, device name, binding name, or driver name.
- `hwc_class_hash`: `.conf` child specs keyed by exported hardware class.
- `hwc_hash_lock`: serializes insertion, removal, and lookup of `.conf` child spec hash state.

## Driver Holds And Stubs

`mod_hold_dev_by_major()` checks that a major number is active, locks the corresponding `devnames` entry, autoloads the driver if the installed `dev_ops` is still a placeholder, and increments the `dev_ops` reference count. `mod_rele_dev_by_major()` decrements that reference and panics on an unheld driver outside debug builds.

Stub installation resolves each module stub symbol name from the kernel symbol table, looks up the real function address in the loaded module, records it in `mod_stub_info`, and then marks stubs installed with producer memory barriers. Resetting stubs returns weak/nounload stubs to their error functions and ordinary stubs to `mod_hold_stub`.

## Binding Tables

`make_mbind()` inserts a `(name, number, bind_name)` entry after rejecting active duplicates. `delete_mbind()` and `purge_mbind()` keep entries in place but negate `b_num`, allowing debug detection of stale references to removed drivers. `mod_name_to_major()` returns only active matches, while `mod_major_to_name()` reads from `devnamesp`.

`init_devnamesp()` allocates the `devnames` array, transfers all active name-to-major bindings into it, warns on duplicate or invalid major numbers, and initializes `.conf` spec hash tables. `init_syscallnames()` similarly converts syscall bindings into the `syscallnames` array.

## Driver.conf Handling

`impl_make_parlist()` parses `drv/<driver>.conf` through `hwc_parse()`, installs global property lists, hashes every parsed `hwc_spec`, and sets per-driver flags such as force attach, interruptible open, SCSI size clean, pHCI driver, and devid registrant. `impl_free_parlist()` unreferences global properties, unhashes child specs, deletes the parent list, and clears parsed state.

`hwc_get_child_spec()` is the main nexus-facing lookup. For a parent `dip`, it searches from most specific to least specific:

- full device pathname,
- `nodename@address`,
- parent/binding form from `i_ddi_parname()`,
- binding name,
- driver name,
- exported classes.

It duplicates matching specs into a caller-owned list and can filter matches by child driver major.

## Locking And Ordering

- `devnamesp[major].dn_lock` protects driver `dev_ops`, per-major flags, parsed `.conf` lists, and global property pointers.
- `mod_lock` protects module-list search in `mod_getctl()`.
- `hwc_hash_lock` protects both parent and class `.conf` hash tables.
- Stub install/uninstall uses producer memory barriers around `MODS_INSTALLED` flag changes.
- Binding hash helpers are explicitly unsynchronized and intended for boot-time or externally locked use.

## Notable Edge Cases

- Removed bindings remain in hash chains with negative numbers for stale-reference diagnostics.
- `mod_rele_dev_by_major()` panics if a driver reference is released when not held.
- `make_devname()` rejects major numbers beyond `L_MAXMAJ32` and slots reserved by `getudev()`.
- `.conf` parent specs for unresolved absolute paths can remain discoverable for dynamic reconfiguration.
- `hwc_hash_remove()` may replace a hash head with the next spec while preserving the key.

## Research Relevance

This file is central to illumos device and storage discovery because it connects driver names, major numbers, `driver.conf` properties, and nexus-created child specs. Filesystem and block-device availability depend on this machinery to bind storage drivers and expose configured child devices.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/modsubr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/modsysfile.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/modsysfile.c

## Purpose

`modsysfile.c` implements kernel parsers for early boot configuration files and driver metadata files. It reads `/etc/system` and `/etc/system.d/.self-assembly`, parses `driver.conf` files, alias/binding files, driver classes, DACF rules, optional PSM machine lists, and optional RTC configuration.

Read completely: 3,292 lines.

## Main Responsibilities

- Tokenizes kernel configuration files through `kobj_lex()`.
- Reads `/etc/system` commands into `sysparam` records.
- Applies `set`, `set32`, and `set64` assignments to kernel or module symbols.
- Applies early boot settings for `moddir`, root filesystem, swap device, and swap filesystem.
- Processes `forceload` and `exclude` directives.
- Parses `driver.conf` files into `.conf` child specs and global property lists.
- Parses `/etc/driver_aliases` and `/etc/ppt_aliases` into binding hashes.
- Parses generic binding files such as `/etc/name_to_major`, `/etc/name_to_sysnum`, and `/etc/path_to_inst`.
- Parses `/etc/dacf.conf` into DACF rules.
- Maintains driver class exports from `/etc/driver_classes`.

## Key Globals

- `systemfile`, `self_assembly`: early system configuration files.
- `versionfile`, `buildversion`: build-version string source and storage.
- `sysparam_hd`, `sysparam_tl`: parsed `/etc/system` command list.
- `mod_sysfile_arena`: vmem arena for parser-owned system parameter memory.
- `hcl_head`, `hcl_lock`: driver class list and lock.
- `obp_bootpath`: boot path storage.
- Optional `_PSM_MODULES` state for `/etc/mach`.
- Optional `_RTC_CONFIG` state for `/etc/rtc_config`.

## Lexer And /etc/system Parser

`kobj_lex()` recognizes punctuation, comments, strings, decimal and hexadecimal values, escaped names, unary numeric forms, whitespace, newlines, and EOF. `read_system_file()` consumes comments and one command per line, delegating command bodies to `do_sysfile_cmd()`.

Supported `/etc/system` command families include:

- `exclude`, `include`, `forceload`
- `rootdev`, `rootfs`, `swapdev`, `swapfs`
- `moddir`
- `set`, `set32`, `set64`

`include` is parsed but ignored. `set32` and `set64` are parsed for syntax but discarded on the opposite kernel data model. Duplicate logical entries are detected by `check_system_file()`, which also computes the final value for repeated `set` operations using assignment, bitwise AND, and bitwise OR semantics.

## Applying Settings

`mod_read_system_file()` creates the parser arena, optionally prompts for parameters, reads self-assembly first, then `/etc/system`, checks duplicates, runs parameter preset/check hooks, applies kernel variable assignments, optionally sets early boot parameters, and reads the build version file.

`mod_sysctl()` processes parsed commands for:

- `SYS_FORCELOAD`: loads modules and prevents autounload; driver paths also trigger `ddi_install_driver()`.
- `SYS_SET_KVAR` / `SYS_SET_MVAR`: writes parsed values into kernel or module symbols.
- `SYS_CHECK_EXCLUDE`: tests whether a module is excluded.

`sys_set_var()` uses ELF symbol lookup and writes 1-, 2-, 4-, or 8-byte integer values. Size-zero symbols are treated as `int` with a warning. `kobj_get_string()` stores string tokens in the parser arena, and `kobj_getvalue()` parses decimal, octal, hexadecimal, negated, and one's-complement numeric values.

## Driver.conf Parser

`hwc_parse()` is the public entry. Non-`t0` callers are handed to a double-stack helper thread to avoid deep-stack boot failures. `hwc_parse_now()` opens the `.conf` file through `kobj_open_path()`, tokenizes it, and parses entries with `get_hwc_spec()`.

`get_hwc_spec()` recognizes `parent`, `name`, `class`, and arbitrary properties. It builds a temporary `dev_info` to reuse DDI property creation helpers, then transfers the device name and system property list into an `hwc_spec`.

Property parsing supports:

- boolean properties with no value,
- integer arrays,
- string arrays,
- validation against reserved IEEE 1275 property-name characters,
- rejection of mixed value types.

`add_spec()` groups node specs into `par_list` records by parent major or class. `add_props()` preserves global property order. `impl_delete_par_list()` and `hwc_free_spec_list()` free parsed structures.

## Alias, Binding, Class, And DACF Files

`parse_aliases()` and `make_aliases()` read `/etc/ppt_aliases` and `/etc/driver_aliases`, resolve each driver name to a major number, and add alias bindings.

`read_binding_file()` is a generic parser for files with `name number [binding-name]` entries. It clears an existing hash, opens the file, invokes the supplied line parser for each complete entry, and returns the largest parsed number.

`read_class_file()` rebuilds `hcl_head` from `/etc/driver_classes`. `add_class()` validates that the exporter has a major number before linking a class export. `get_class()` returns class names for an exporter while the caller holds `hcl_lock`. `impl_parlist_to_major()` resolves parent lists into parent major-number sets, including class-to-exporter expansion.

`read_dacf_binding_file()` parses `/etc/dacf.conf`, clears the DACF rule database under `dacf_lock`, and registers rules of the form device-spec, optional module/opset, operation, options, and named config arguments.

## Optional Platform Parsers

Under `_PSM_MODULES`, `open_mach_list()`, `get_next_mach()`, and `close_mach_list()` maintain a simple list of platform-specific machine module names from `/etc/mach`.

Under `_RTC_CONFIG`, `process_rtc_config_file()` extracts only `zone_lag=<decimal>` from `/etc/rtc_config`, warning on malformed partial entries and ignoring unrelated configuration.

## Locking And Memory

- `/etc/system` parser allocations live in `mod_sysfile_arena`.
- Driver class list access is serialized by `hcl_lock`.
- DACF rule replacement is serialized by `dacf_lock`.
- `hwc_parse()` helper thread uses a semaphore to return parse completion to the caller.
- `driver.conf` property creation uses DDI property APIs on temporary devinfo state.

## Notable Edge Cases

- `hwc_parse_now()` returns success after opening a file even when individual lines are malformed; bad lines are skipped.
- Comments in DACF files are accepted only at the start of a line.
- `read_binding_file()` panics if a required binding file is missing.
- `mod_sysvar()` can fetch an early global or module-specific `set` value before module load.
- Duplicate `/etc/system` warnings report the final effective value, not merely the last token.
- Unresolved absolute `parent=` paths can be retained with major `(major_t)-2` for later dynamic reconfiguration.

## Research Relevance

This file defines how boot-time kernel configuration, driver aliases, `driver.conf` child nodes, and class metadata enter the kernel. It is directly relevant to filesystem and storage behavior because module loading, root/swap setup, block driver binding, and nexus child creation all depend on these parsed files.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/modsysfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/move.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/move.c

## Purpose

`move.c` implements core `uio_t` data movement helpers used throughout the kernel for copying bytes between kernel buffers, user address spaces, and kernel I/O vectors. It also contains optional asynchronous copy support using the platform dcopy/I/OAT DMA framework.

Read completely: 795 lines.

## Main Responsibilities

- Moves byte ranges through `uiomove()`, updating `uio` progress.
- Prefaults user or kernel pages referenced by a `uio` without modifying it.
- Copies through `uiocopy()` without changing the source `uio`.
- Reads or writes single bytes through `ureadc()` and `uwritec()`.
- Skips data in a `uio` with `uioskip()`.
- Duplicates a `uio` and caller-supplied iovec storage with `uiodup()`.
- Supports asynchronous copy setup, submission, and cleanup with `uioainit()`, `uioamove()`, and `uioafini()`.

## Core UIO Copy Paths

`uiomove()` iterates over iovecs, skips zero-length entries, copies up to the smaller of requested bytes and current iovec length, and advances `iov_base`, `iov_len`, `uio_resid`, `uio_loffset`, and the source pointer. It chooses copy helpers by segment flag:

- `UIO_USERSPACE` / `UIO_USERISPACE`: `xcopyout_nta()` for reads and `xcopyin_nta()` for writes.
- `UIO_SYSSPACE`: `kcopy_nta()` in the appropriate direction.

`uiocopy()` mirrors the same copy rules but leaves the original `uio` untouched and reports copied bytes through `cbytes`.

`uio_prefaultpages()` touches one byte per page and the final byte in each segment with `fuword8()` or `kcopy()` to encourage page residency before later I/O.

## Character And Cursor Helpers

`ureadc()` writes one byte into the address space represented by a `uio`, skipping empty iovecs and advancing all relevant fields. `uwritec()` reads one byte from a `uio` and returns `-1` on failure. Both reject invalid or exhausted `uio` structures.

`uioskip()` advances over `n` bytes without copying, updating the iovec cursor and offset. It refuses to skip past `uio_resid`. `uiodup()` shallow-copies the `uio` and duplicates each iovec into caller-supplied storage, failing if the destination iovec array is too small.

## Async Copy Support

The async path is built around `uioa_t` and dcopy handles:

- `uioa_dcopy_enable()` / `uioa_dcopy_disable()` toggle global async availability.
- `uioainit()` allocates a dcopy channel, copies the `uio`, validates iovec count, marks async state, locks user pages with `as_pagelock()`, and stores either page lists or synthesized PFN arrays.
- `uioamove()` supports only kernel-to-user `UIO_READ` into `UIO_USERSPACE`. It splits DMA commands on source and destination page boundaries, allocates linked dcopy commands, fills source/destination physical addresses, posts copy commands, and advances the `uioa` cursor.
- `uioafini()` optionally polls or blocks for the last dcopy command, frees commands and channel state, unlocks all locked pages, copies final `uioa` progress back into the caller's `uio`, and resets the async state.

## Dependencies

The file depends on copy primitives, `uio_t`/`iovec_t`, VM address spaces, page locking, HAT PFN translation, segkpm-style page state, dcopy channel/command APIs, and current process address-space state.

## Notable Edge Cases

- `uiomove()` and `uiocopy()` return immediately on the first copy fault, leaving progress already applied for prior iovecs.
- `uio_prefaultpages()` is best effort and silently stops on fault.
- `uioainit()` disables async copy globally if dcopy resources disappear.
- Async copy has comments noting Intel I/OAT-specific implementation assumptions.
- `uioafini()` contains an explicit comment questioning why `cmd == NULL` can occur.
- PFN-array cleanup uses the stored `uioa_pfncnt` path when `as_pagelock()` did not return page pointers.

## Research Relevance

This is a core data-transfer file for filesystem and device I/O paths. Read/write implementations commonly rely on `uiomove()` semantics for residual counts, offsets, fault handling, and kernel/user memory separation; async copy support affects high-throughput copyout behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/move.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/msacct.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/msacct.c

## Purpose

`msacct.c` implements illumos microstate accounting for LWPs/threads and CPUs. It tracks high-resolution time spent in execution, sleep, stopped, fault, wait-CPU, user, system, and idle states, and derives recent CPU percentage from those transitions.

Read completely: 849 lines.

## Main Responsibilities

- Initializes and terminates per-LWP microstate accounting.
- Initializes, transitions, and disables per-CPU microstate accounting.
- Updates thread and CPU state on syscall, trap, dispatcher, sleep, stop, and termination paths.
- Aggregates process and thread microstate times.
- Maintains zone user/system/wait CPU accounting arrays.
- Computes decayed/grown recent CPU percentage values.

## Thread And CPU State Initialization

`init_mstate()` initializes an LWP-backed thread's `lwp_mstate`, starting timestamp, previous state, current thread state, wait-runqueue timestamp, and accounting arrays. Kernel threads without LWPs are skipped by later accounting paths.

`init_cpu_mstate()` initializes CPU state, start timestamp, runqueue wait total, and CPU accounting arrays. `term_cpu_mstate()` switches a CPU to `CMS_DISABLED`, a placeholder state not accumulated as active time.

## CPU Microstate Transitions

`new_cpu_mstate()` changes the current CPU among `CMS_USER`, `CMS_SYSTEM`, and `CMS_IDLE`. It is intentionally lockless because only the local CPU updates its own state. Readers rely on `cpu_mstate_gen`, which is set to zero during updates and restored to a non-zero generation afterward.

The file documents that this depends on TSO or equivalent store ordering. The update path avoids producer barriers because syscall transitions are performance-critical.

## Thread Accounting Paths

`syscall_mstate()` handles common user/system syscall transitions, charges elapsed time to the old LWP state, updates zone user/system counters, and updates the current CPU microstate while preemption is disabled.

`new_mstate()` is the general LWP state transition function. It accounts elapsed time in the old state, maps several fault and user-lock states into system accounting, updates recent CPU percentage, remembers the previous runnable state, updates zone counters, and switches CPU state when appropriate.

`restore_mstate()` is called by the dispatcher when selecting a thread. It accounts sleep or stopped time, restores the previous runnable state, clears `t_waitrq`, charges wait-CPU time, and updates per-zone and per-CPU wait totals.

`term_mstate()` finalizes an exiting LWP by switching it to stopped, scaling all microstate accumulators into process totals, transferring resource usage counters, adding elapsed real time, and incrementing the defunct LWP count.

## Aggregation And CPU Percent

`mstate_thread_onproc_time()` returns scaled user+system+trap on-processor time for a thread, including current in-flight state time where applicable.

`mstate_systhread_times()` returns system-thread on-processor and runnable time, noting that unlocked fields make this interface inherently race-prone and not strictly monotonic.

`mstate_aggr_state()` aggregates a process state from process-level exited-LWP accounting plus live thread accounting.

`exp_x()`, `cpu_decay()`, `cpu_grow()`, and `cpu_update_pct()` implement recent CPU percentage as a scaled exponential decay/growth function. `cpu_update_pct()` uses atomic CAS because it can be called at elevated PIL and cannot safely take locks.

## Locking And Ordering

- Process aggregation requires `p_lock`.
- Some thread-time readers assert `THREAD_LOCK_HELD(t)` but document that self-updated fields can still race.
- CPU microstate updates require preemption disabled when tied to current thread CPU.
- CPU state readers must use generation checks and consumer barriers outside this file.
- CPU microstate writes rely on volatile fields and TSO-like ordering.

## Notable Edge Cases

- Negative elapsed time can occur from inconsistent unscaled high-resolution timestamps across CPUs; loops retry with a fresh timestamp.
- The initial startup thread may have `ms_state_start == 0`, so zone accounting skips that initial span.
- Interrupt threads that pin another thread are excluded from LWP microstate updates.
- `mstate_systhread_times()` explicitly warns its results can temporarily decrease or be too large.
- Fault and user-lock microstates may contribute to `LMS_SYSTEM` aggregation depending on context.

## Research Relevance

This file is not filesystem-specific, but it is relevant to performance research. Filesystem and storage workloads consume these accounting paths for system time, runqueue wait time, process resource accounting, zone usage, and CPU percentage metrics visible through proc/stat tooling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/msacct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/msg.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/msg.c

## Purpose

`msg.c` implements the illumos System V message queue facility. It provides the loadable syscall module for `msgget`, `msgctl`, `msgsnd`, `msgrcv`, `msgids`, and `msgsnap`, with per-zone/project resource control integration and scalable waiter wakeup logic.

Read completely: 1,584 lines.

## Main Responsibilities

- Registers the System V message syscall module and 32-bit syscall entry points.
- Creates and destroys IPC service state for message queue IDs.
- Allocates, initializes, removes, and destroys message queues.
- Implements permission checks, resource controls, auditing hooks, and zone cleanup.
- Sends messages with bounded byte and message-count limits.
- Receives messages by type semantics, including exact, any, and negative type selection.
- Provides message queue snapshots without consuming messages.
- Avoids receiver thundering-herd wakeups through targeted waiter queues.

## Key Data Structures And Globals

- `msq_svc`: IPC service for message queues.
- `msg_zone_key`: zone cleanup key.
- `kmsqid_t`: per-message-queue kernel state, including message list, byte counts, qbytes/qmax limits, wait lists, receiver/sender counts, and selection rotors.
- `struct msg`: queued message with type, size, payload pointer, flags, reference/copy count, and list linkage.
- `msgq_wakeup_t`: stack-allocated waiter record with thread, condition variable, message type/size, and wake metadata.
- `msg_fnd_sndr`: rotating selector array for type-0, exact positive, and negative receive waiters.
- `msg_fnd_rdr`: selector for copyout waiters.

## Module Lifecycle

`_init()` creates the IPC service with `ipcs_create()`, registers a zone cleanup callback, and installs the syscall module. `_fini()` always returns `EBUSY`, so the module is not unloadable. `_info()` delegates to `mod_info()`.

`msg_dtor()` asserts and destroys all queue lists. `msg_rmid()` removes all messages, wakes every receiver/sender/copyout waiter, and leaves the object ready for IPC destruction. `msg_remove_zone()` removes all queues associated with a halted zone.

## Queue Creation And Control

`msgget()` uses common IPC allocation/lookup code. For new queues, it initializes message and waiter lists, receiver/sender counters, negative-message metadata, selection rotors, and resource-control-derived limits for queue bytes and message count.

`msgctl()` handles `IPC_SET`, `IPC_STAT`, `IPC_SET64`, `IPC_STAT64`, and `IPC_RMID`. It performs copyin before lookup where needed, enforces privilege/resource-control checks for increasing `msg_qbytes`, updates IPC permissions and timestamps, and copies status out after releasing the queue lock.

`msgids()` delegates ID enumeration to common IPC code.

## Send Path

`msgsnd()` copies the message type, validates that it is positive, and preallocates small messages up to `MSG_PREALLOC_LIMIT` before taking the queue lock. Larger messages are allocated and copied outside the queue lock after space is available, then the function revalidates the queue and retries.

If the queue lacks byte space or has reached `msg_qmax`, senders either fail with `EAGAIN` under `IPC_NOWAIT` or enqueue on `msg_wait_rcv`. `msg_wakeup_senders()` scans waiting senders in order, waking those whose sizes can fit into the available projected space.

On successful send, the message is appended, queue byte/message counters and send metadata are updated, the lowest message type hint is adjusted, and `msg_wakeup_rdr()` wakes a matching receiver.

## Receive Path

`msgrcv()` looks up the queue, checks read permission, and repeatedly searches for a matching message through `msgrcv_lookup()`:

- `msgtyp == 0`: first message.
- `msgtyp > 0`: first message with exact type, with a low-type hint fast rejection.
- `msgtyp < 0`: lowest type less than or equal to `-msgtyp`, with negative-copy serialization.

`msg_copyout()` marks a message `MSG_RCVCOPY`, holds a reference, releases the queue lock, copies type and text to userland, reacquires the lock, clears copy state, handles queue deletion, unlinks the message on success, and wakes senders through `msgunlink()`.

If no message matches, receivers fail with `ENOMSG` under `IPC_NOWAIT` or sleep on either positive/zero `msg_wait_snd` buckets or negative `msg_wait_snd_ngt` buckets. If a matching message is already being copied out, receivers sleep on `msg_cpy_block` and restart lookup after wakeup.

## Waiter Selection And Hashing

`msg_type_hash()` maps type zero to bucket 0, positive types to hashed buckets 1..`MSG_MAX_QNUM`, and negative type ranges to interval buckets capped at `MSG_MAX_QNUM`.

`msg_wakeup_rdr()` rotates through selector functions to avoid starving any class of receiver. The selectors find:

- any-message receivers,
- exact positive type receivers,
- eligible negative type receivers,
- copyout waiters.

Negative receiver selection randomizes its starting bucket using the queue's last send time within the eligible range. `msg_rcvq_sleep()` inserts a stack waiter, waits interruptibly, relocks the IPC object, decrements receiver count, and removes itself on unexpected wakeup.

## Snapshot Path

`msgsnap()` computes required buffer size and matching message count, optionally holds references to matching messages, releases the lock, copies out a snapshot header and per-message headers/payloads with native or 32-bit alignment, then drops holds while checking for queue deletion.

If the provided buffer is too small, it reports the required size and zero messages rather than copying payloads.

## Resource Controls And Compatibility

The preferred limits are resource controls:

- `zone.max-msg-ids`
- `project.max-msg-ids`
- `process.max-msg-qbytes`
- `process.max-msg-messages`

Obsolete `msginfo_*` tunables remain declared for compatibility. The module also provides 32-bit syscall wrappers on LP64 kernels, including 32-bit message type conversion.

## Notable Edge Cases

- Message payload copyout occurs without the queue lock to prevent denial of service from slow user memory.
- `MSG_RCVCOPY` and the copyout waiter chain prevent multiple receivers from consuming or indefinitely blocking on the same message.
- Negative receive lookup uses `msg_neg_copy` and a static sentinel to serialize negative-type copyout cases.
- `msgsnd()` must redo space checks after large-message copyin because the lock was dropped.
- `msg_wakeup_senders()` projects byte space and message slots as if awakened senders will succeed.
- Queue deletion during waits or copy operations returns `EIDRM`.

## Research Relevance

This file is core IPC rather than filesystem code, but it is important OS infrastructure. Filesystem daemons, test harnesses, and storage management tools may rely on System V IPC behavior; the implementation also demonstrates illumos IPC locking, resource controls, zone cleanup, and copyin/copyout patterns.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/msg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/mutex.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/mutex.c

## Purpose

`mutex.c` implements illumos kernel mutual exclusion primitives for adaptive and spin mutexes. It provides the C slow paths behind assembly fast paths, lock initialization/destruction, ownership queries, adaptive blocking through turnstiles, spin-lock backoff, panic diagnostics, and lockstat instrumentation.

Read completely: 724 lines.

## Main Responsibilities

- Implements adaptive mutex acquisition slow path in `mutex_vector_enter()`.
- Implements spin mutex acquisition and tryenter slow paths.
- Implements contended/waiter-aware mutex release in `mutex_vector_exit()`.
- Provides `mutex_init()`, `mutex_destroy()`, `mutex_owned()`, and `mutex_owner()`.
- Implements default exponential randomized backoff and delay hooks.
- Implements simple spin-lock slow paths `lock_set_spin()` and `lock_set_spl_spin()`.
- Records lockstat events for spin, block, acquire, release, and destroy cases.

## Design Model

The file documents the mutex model in detail:

- Spin mutexes raise/block interrupts and spin until available; they are intended mainly for interrupt synchronization.
- Adaptive mutexes spin if the owner is running on another CPU and block otherwise.
- Fast-path `mutex_enter()` assumes adaptive layout; non-adaptive or held cases punt here.
- Blocking uses turnstiles and priority inheritance support.
- Adaptive mutex release wakes all waiters after clearing the lock and waiter state, avoiding direct handoff.

A key correctness issue is avoiding missed wakeups between `mutex_vector_enter()` setting the waiter bit and `mutex_exit()` clearing the owner without an atomic instruction. The implementation relies on platform trap/preemption fixups and carefully documented memory ordering.

## Key Data And Hooks

- `mutex_sobj_ops`: synchronization-object operations used by turnstile sleep.
- `panic_mutex` / `panic_mutex_addr`: first offending mutex snapshot for panic diagnostics.
- `mutex_backoff_base`, `mutex_backoff_cap`, `mutex_cap_factor`, `mutex_backoff_shift`: backoff tunables.
- `mutex_lock_backoff`, `mutex_lock_delay`, `mutex_delay`: function pointers for platform/default delay behavior.

## Acquisition And Release

`mutex_vector_enter()` handles spin locks by calling `lock_set_spl()`. For adaptive locks, it checks high-PIL misuse, records stats, repeatedly delays with backoff, tries to acquire unowned locks, detects recursion, spins while the owner is running, and blocks on a turnstile only after setting the waiter bit and rechecking state.

`mutex_vector_tryenter()` handles failed assembly tryenter cases. Adaptive locks have already been tried and return failure. Spin locks raise PIL, attempt `lock_try()`, store old PIL on success, and restore PIL on failure.

`mutex_vector_exit()` handles spin unlock via `lock_clear_splx()`. For adaptive locks, it verifies ownership, looks up the turnstile, atomically clears lock and waiter state through the macro path, wakes all writer waiters if any, and records release.

## Initialization And Destruction

`mutex_init()` chooses spin versus adaptive solely from the interrupt block cookie/PIL. PIL above `LOCK_LEVEL` creates a spin mutex with minimum SPL state; otherwise it creates an adaptive mutex. Optional alignment checking warns on unsupported unaligned mutex addresses.

`mutex_destroy()` permits destroying an unlocked mutex, destroying spin mutexes, or destroying an adaptive mutex held by the current thread with no waiters. It panics on bad type, non-owner destroy, or waiters.

## Spin Slow Paths

`lock_set_spin()` and `lock_set_spl_spin()` provide C fallback loops for contended spin locks. They panic on single-CPU deadlock scenarios, apply randomized exponential backoff, return early during panic, and record lockstat spin/acquire events. The SPL version temporarily drops to the old PIL while waiting, then raises again before retrying acquisition.

## Locking And Ordering Requirements

The top comment records external requirements:

- interrupt/trap code must restart preempted `mutex_exit()` critical regions,
- `resume()` must issue a store-load barrier after setting `CPU_THREAD`,
- `mutex_owner_running()` requires similar preemption fixup,
- idle threads cannot acquire adaptive locks.

These requirements are part of correctness, not just optimization.

## Notable Edge Cases

- Adaptive mutex acquisition at high PIL panics unless the system is already panicking.
- Recursive `mutex_enter()` panics.
- During panic, several paths return rather than spinning forever.
- `mutex_owned()` returns true during panic or quiesce.
- On single CPU, contended spin-lock slow paths panic because no other CPU can release the lock.
- Misaligned mutex warnings are capped to avoid log floods.

## Research Relevance

This file underpins synchronization throughout illumos, including VFS, device, and filesystem paths. Understanding its adaptive spin/block behavior and destruction rules is important when reasoning about storage-stack locking, deadlock risks, interrupt-level constraints, and performance under contention.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/mutex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ndifm.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ndifm.c

## Purpose

`ndifm.c` implements nexus-driver support for illumos DDI fault management. It manages per-child access/DMA handle caches, dispatches child error handlers, sets handle error state, and calls parent bus fault-management operations.

Read completely: 753 lines.

## Main Responsibilities

- Creates the global FM cache-entry kmem cache.
- Allocates and destroys per-device FM resource caches.
- Inserts and removes protected access and DMA handles from child FM caches.
- Matches bus error state against cached access/DMA handles.
- Sets access/DMA handle error state and invokes child error handlers.
- Dispatches registered child FM handlers for nexus errors.
- Calls parent bus `fm_init`, `fm_fini`, `fm_access_enter`, and `fm_access_exit` operations.

## Key Data Structures

- `ndi_fm_entry_cache`: global `kmem_cache_t` for `ndi_fmcentry_t`.
- `ndi_fmc_t`: per-device FM cache with lock, head, and tail.
- `ndi_fmcentry_t`: cached handle record containing resource pointer, bus-specific data, and list links.
- `i_ddi_fmhdl`: per-device FM handle state with capability flags, DMA/access caches, child targets, and FM kstats.
- `i_ddi_fmtgt`: child FM target entry with child dip and registered error handler.

## Cache Lifecycle And Handle Tracking

`ndi_fm_init()` creates the entry cache. `i_ndi_fmc_create()` allocates a cache and initializes its lock with the nexus-provided interrupt block cookie. `i_ndi_fmc_destroy()` frees remaining entries, destroys the lock, and frees the cache.

`ndi_fmc_insert()` checks the child FM capabilities, allocates an entry without sleeping, records resource and bus-specific data, stores the backpointer in the access or DMA handle error structure, and appends the entry to the cache list under `fc_lock`.

`ndi_fmc_remove()` finds the entry from the handle's stored `err_fep`, clears that handle pointer, unlinks the cache entry under `fc_lock`, and frees it. Capability mismatches increment or post FM diagnostics depending on access versus DMA cases.

## Error Matching

`ndi_fmc_entry_error()` scans a single child's matching cache. For each cached resource with a compare callback, it calls the callback with the bus error state. Fatal and nonfatal matches set the resource's FM error state, retrieve the updated error record, and attach the matching access or DMA handle to the `ddi_fm_error_t`.

`ndi_fmc_error()` enters the parent FM handler critical section, walks all registered child targets or a single target, calls `ndi_fmc_entry_error()` for each child cache, and invokes the child's registered error handler when a cached resource matched. It returns fatal if any fatal result occurred, nonfatal if any nonfatal result occurred, otherwise unknown.

`ndi_fmc_entry_error_all()` is a broader helper that marks all cached FLAGERR resources as nonfatal unexpected errors and returns nonfatal if anything was marked.

## Handler Dispatch And Busops

`ndi_fm_handler_dispatch()` invokes registered child error handlers for a nexus, either all targets or one target. It aggregates return statuses with fatal dominating nonfatal, nonfatal dominating unknown, and OK only if all handlers return OK.

`ndi_fm_acc_err_set()` and `ndi_fm_dma_err_set()` are simple wrappers around internal access/DMA error setters.

`i_ndi_busop_fm_init()` calls the parent bus `bus_fm_init()` if available and busops revision is high enough, returning system FM capabilities for the root node. `i_ndi_busop_fm_fini()` calls parent cleanup if present. `i_ndi_busop_access_enter()` and `i_ndi_busop_access_exit()` call parent exclusive-access busops for cautious access handles.

## Locking And Context

- FM cache lists are protected by each cache's `fc_lock`.
- Cache entry allocation uses `KM_NOSLEEP`, matching fault/error-path constraints.
- Handler dispatch is bracketed by `i_ddi_fm_handler_enter()` and `i_ddi_fm_handler_exit()`.
- Comments state insert/remove may be called from user or kernel context at or below `LOCK_LEVEL`; error scans may run in contexts permitted by the initialized interrupt block cookie.
- Removing a resource relies on the handle-stored entry pointer rather than searching by resource.

## Notable Edge Cases

- If a DMA-capable or access-capable child lacks the required capability, insert/remove returns early; access mismatch posts a driver ereport.
- Allocation failure increments the FM cache full kstat and silently leaves the resource uncached.
- Removing a missing cache entry increments the FM cache miss kstat.
- `ndi_fmc_error()` can invoke both cache comparison logic and child handlers, so a child may influence final status twice.
- Root node FM init returns system FM plus ereport capability without parent busops.

## Research Relevance

This file is important for storage and filesystem reliability research because nexus fault management is how bus, DMA, and programmed-I/O errors are associated with child device handles. Block-device drivers and storage HBAs rely on these paths to surface fatal or nonfatal I/O fault information.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ndifm.c -->