# Group Research: group_1064_linux_stable_sources_os_linux_linux_stable_fs_pipe_c_sources_os_lin_f55b77fcd8c2

Scope: `Docs/research_subset_a.md` subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/pipe.c -->
# File Research: sources/os/linux/linux-stable/fs/pipe.c

## Purpose

Implements Linux anonymous pipes, FIFOs, pipe buffer lifecycle, pipe sizing/accounting, pipe poll/ioctl/fcntl behavior, and the internal `pipefs` pseudo filesystem.

## Main Responsibilities

- Provides pipe locking helpers: `pipe_lock()`, `pipe_unlock()`, and `pipe_double_lock()`.
- Implements anonymous pipe buffer operations:
  - `anon_pipe_get_page()` and `anon_pipe_put_page()` recycle temporary pages.
  - `anon_pipe_buf_release()` releases anonymous pipe pages.
  - `anon_pipe_buf_try_steal()` supports page stealing when refcount is one.
  - Generic exported helpers `generic_pipe_buf_try_steal()`, `generic_pipe_buf_get()`, and `generic_pipe_buf_release()` are used by splice/tee-style paths.
- Implements read/write paths:
  - `anon_pipe_read()` handles ordinary pipe reads, packetized buffers, whole-buffer semantics, watch queue loss notifications, blocking/nonblocking waits, and wakeups.
  - `fifo_pipe_read()` wraps reads with FIFO access-time accounting.
  - `anon_pipe_write()` handles SIGPIPE/EPIPE, page allocation, buffer merging through `PIPE_BUF_FLAG_CAN_MERGE`, packet mode via `O_DIRECT`, nonblocking behavior, and writer/reader wakeups.
  - `fifo_pipe_write()` wraps writes with timestamp update under superblock write protection.
- Implements file operations:
  - `pipe_ioctl()` supports `FIONREAD` and watch queue ioctls under `CONFIG_WATCH_QUEUE`.
  - `pipe_poll()` reports read/write readiness, EOF/HUP, and writer-side error states.
  - `pipe_release()` decrements reader/writer counts and wakes opposite endpoints.
  - `pipe_fasync()` manages async notification lists.
- Implements resource accounting:
  - Global pipe limits: `pipe_max_size`, `pipe_user_pages_hard`, `pipe_user_pages_soft`.
  - `alloc_pipe_info()` charges user pipe pages and shrinks default pipe size to `PIPE_MIN_DEF_BUFFERS` when soft-limited.
  - `free_pipe_info()` uncharges pages, releases buffers, watch queues, and cached pages.
- Implements pipe creation:
  - `get_pipe_inode()` creates pseudo inodes backed by `pipefs`.
  - `create_pipe_files()`, `__do_pipe_flags()`, `do_pipe_flags()`, and syscall wrappers `pipe()`/`pipe2()` create file pairs and install descriptors.
- Implements FIFO open semantics:
  - `fifo_open()` handles blocking/nonblocking read-only, write-only, and read-write FIFO opens, including partner wait counters.
- Implements pipe resizing:
  - `round_pipe_size()`, `pipe_resize_ring()`, `pipe_set_size()`, and `pipe_fcntl()` support `F_SETPIPE_SZ` and `F_GETPIPE_SZ`.
- Registers internal pipefs and sysctls:
  - `pipefs_init_fs_context()`, `pipe_fs_type`, and `init_pipe_fs()`.
  - Sysctls under `fs`: `pipe-max-size`, `pipe-user-pages-hard`, and `pipe-user-pages-soft`.

## Key Data/Control Flow

- Pipe ring indices use unmasked head/tail values and mask only on dereference, requiring power-of-two ring sizes.
- Read path locks `pipe->mutex`, drains buffers from tail, advances tail through `pipe_update_tail()`, and wakes writers if space was freed.
- Write path may merge a trailing partial write into the previous buffer before allocating new pages.
- Watch queue pipes cannot be written through `anon_pipe_write()` and cannot be resized through `pipe_set_size()`.
- `pipe_resize_ring()` copies existing ring contents into a new buffer array while holding `rd_wait.lock`, preserving occupancy and rejecting shrink below current occupancy.
- FIFO open uses `r_counter`/`w_counter` and `wait_for_partner()` to implement POSIX blocking partner semantics.

## Concurrency and Lifetime Notes

- `pipe->mutex` serializes most data path operations.
- Watch queue paths additionally use `pipe->rd_wait.lock` because notifications may be posted without the pipe mutex.
- `put_pipe_info()` uses `inode->i_lock` to guard `pipe->files` and clears `inode->i_pipe` on final reference.
- The file carefully wakes both wait queues when the last reader or writer disappears.

## Security/Policy Notes

- Unprivileged users are limited by pipe maximum size and per-user soft/hard page limits.
- Writes to notification/watch queue pipes return `-EXDEV`.
- `pipefs` is an internal pseudo filesystem intended not to be mounted by userspace.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/pipe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/pnode.c -->
# File Research: sources/os/linux/linux-stable/fs/pnode.c

## Purpose

Implements VFS mount propagation logic for shared, slave, private, and unbindable mounts, including mount propagation on attach and unmount propagation.

## Main Responsibilities

- Traverses peer and slave mount propagation relationships:
  - `next_peer()`, `first_slave()`, `next_slave()`.
  - `propagation_next()`, `next_group()`, and `skip_propagation_subtree()`.
- Computes propagation metadata:
  - `get_peer_under_root()` and `get_dominating_id()` find dominating shared peer groups visible under a root.
- Changes propagation state:
  - `change_mnt_propagation()` converts mounts to shared, slave, private, or unbindable.
  - `transfer_propagation()` reparents slave lists when a mount leaves a peer group or changes master.
  - `bulk_make_private()` efficiently privatizes a set of mounts while preserving slave transfer destinations.
- Propagates new mounts:
  - `propagate_mnt()` creates secondary copies of a source mount tree for peers/slaves that should receive the mount.
  - It links new copies into the propagation graph, attaches them at `dest_mp`, and accounts them against target namespaces.
- Checks overmount and busy states:
  - `propagation_would_overmount()` determines whether a propagated mount would cover a target mount root.
  - `propagate_mount_busy()` checks whether a propagated unmount would hit busy mounts.
  - `propagate_mount_unlock()` clears `MNT_LOCKED` on propagated children when safe.
- Propagates unmount:
  - `propagate_umount()` gathers propagation recipients, trims unsafe candidates, handles locked stacks, reparents surviving overmounts, and folds acceptable candidates into the unmount set.

## Key Data/Control Flow

- Peer groups are circular `mnt_share` lists.
- Slave relationships are hlist chains under `mnt_slave_list` with `mnt_master` pointers.
- `propagate_mnt()` walks peer groups depth-first, uses `copy_tree()`, and marks masters to find the correct propagation source copies.
- Unmount propagation works in stages:
  - `gather_candidates()` finds children under propagated parents.
  - `trim_one()` removes candidates blocked by surviving submounts.
  - `handle_locked()` deals with locked chains.
  - `reparent()` moves surviving overmounts above unmounted stacks.

## Concurrency and Locking Notes

- Several functions require `namespace_sem` exclusive or shared, as documented inline.
- Unmount propagation requires `mount_lock` write seqlock and `namespace_sem` exclusive.
- Busy/unlock propagation assumes the vfsmount lock is held for write.

## Important Invariants

- Shared peer groups form contiguous segments in slave lists; traversal helpers rely on that property.
- `T_MARKED` and `T_UMOUNT_CANDIDATE` are temporary traversal markers and are cleared before returning.
- `MNT_UMOUNT` marks mounts committed to unmount.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/pnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/pnode.h -->
# File Research: sources/os/linux/linux-stable/fs/pnode.h

## Purpose

Declares mount propagation helpers, propagation state macros, clone flags, and cross-file VFS mount helper prototypes used by `pnode.c` and mount code.

## Main Contents

- Propagation state macros:
  - `IS_MNT_SHARED()`, `IS_MNT_SLAVE()`, `IS_MNT_NEW()`, `IS_MNT_UNBINDABLE()`.
  - `CLEAR_MNT_SHARED()`, `IS_MNT_MARKED()`, `SET_MNT_MARK()`, `CLEAR_MNT_MARK()`.
  - `IS_MNT_LOCKED()`.
- Clone/propagation flags:
  - `CL_EXPIRE`, `CL_SLAVE`, `CL_COPY_UNBINDABLE`, `CL_MAKE_SHARED`, `CL_PRIVATE`, `CL_COPY_MNT_NS_FILE`.
- Inline helpers:
  - `set_mnt_shared()` clears shared mask bits and sets `T_SHARED`.
  - `peers()` compares nonzero mount group ids.
- Declares propagation API:
  - `change_mnt_propagation()`, `bulk_make_private()`, `propagate_mnt()`, `propagate_umount()`.
  - `propagate_mount_busy()`, `propagate_mount_unlock()`, `propagation_would_overmount()`.
- Declares supporting mount helpers from other VFS files:
  - `mnt_release_group_id()`, `mnt_get_count()`, `mnt_set_mountpoint()`, `mnt_change_mountpoint()`, `copy_tree()`, `is_path_reachable()`, `count_mounts()`.

## Notes

This header is tightly coupled to internal `struct mount` fields and is not a public API. It encodes the state bits and traversal predicates that `pnode.c` depends on.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/pnode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/posix_acl.c -->
# File Research: sources/os/linux/linux-stable/fs/posix_acl.c

## Purpose

Provides generic VFS support for POSIX ACL allocation, caching, validation, permission checks, chmod/create transformations, xattr conversion, and VFS get/set/remove ACL operations.

## Main Responsibilities

- ACL cache handling:
  - `acl_by_type()` selects `inode->i_acl` or `inode->i_default_acl`.
  - `get_cached_acl()` and `get_cached_acl_rcu()` read cached ACLs safely.
  - `set_cached_acl()`, `forget_cached_acl()`, and `forget_all_cached_acls()` update or invalidate caches.
  - `__get_acl()` handles sentinel-based cache fill races and calls filesystem `get_acl` or `get_inode_acl`.
- ACL object lifecycle:
  - `posix_acl_init()`, `posix_acl_alloc()`, and `posix_acl_clone()`.
- ACL validation and mode equivalence:
  - `posix_acl_valid()` validates tag order, permission bits, mask requirements, and uid/gid mappings.
  - `posix_acl_equiv_mode()` determines whether an ACL can be represented by traditional mode bits.
  - `posix_acl_from_mode()` constructs a three-entry ACL from mode bits.
- Permission checking:
  - `posix_acl_permission()` evaluates owner, named user, group object, named group, mask, and other entries with idmapped mount translation.
- ACL create/chmod transformations:
  - `posix_acl_create_masq()` applies create mode/umask semantics.
  - `__posix_acl_chmod_masq()` applies chmod semantics.
  - `__posix_acl_create()`, `__posix_acl_chmod()`, `posix_acl_chmod()`, and `posix_acl_create()` expose these workflows.
- Mode update for set ACL:
  - `posix_acl_update_mode()` updates inode mode bits from ACL and clears setgid when needed.
- Xattr conversion:
  - `posix_acl_from_xattr()` converts on-disk/uapi ACL xattrs into VFS ACLs.
  - `posix_acl_to_xattr()` converts VFS ACLs to filesystem idmapping xattr form.
  - `vfs_posix_acl_to_xattr()` converts to userspace-visible xattr form, accounting for mount idmaps and caller namespace.
- VFS ACL operations:
  - `set_posix_acl()` validates type, directory default ACL rules, ownership, and filesystem support.
  - `vfs_set_acl()` applies idmapped mount translation, VFS write checks, LSM hooks, delegation breaking, filesystem set, fsnotify, and post hooks.
  - `vfs_get_acl()` applies LSM get hook, type checks, symlink rejection, and cache-backed retrieval.
  - `vfs_remove_acl()` applies write checks, LSM remove hook, delegation breaking, filesystem removal, fsnotify, and post hooks.
  - `do_set_acl()` and `do_get_acl()` are xattr syscall-facing helpers.
- Simple filesystem helpers:
  - `simple_set_acl()` updates cached ACLs and ctime/i_version.
  - `simple_acl_create()` initializes inherited ACLs on simple filesystems.
- Xattr listing and legacy handlers:
  - `posix_acl_listxattr()` lists present access/default ACL xattr names.
  - `nop_posix_acl_access` and `nop_posix_acl_default` list POSIX ACL names for older filesystem code.

## Key Data/Control Flow

- The cache sentinel in `__get_acl()` prevents stale cache publication when another thread races with ACL retrieval.
- ACL validity requires canonical entry ordering: user object, optional named users, group object, optional named groups, optional mask, other.
- Named user/group entries require a mask entry.
- Idmapped mounts are applied during permission checks and VFS userspace boundaries, not when caching filesystem ACLs.
- `vfs_set_acl()` mutates the supplied ACL for idmapped mounts before calling filesystem `set_acl()`.

## Security and Correctness Notes

- ACL set/remove paths call `may_write_xattr()` and LSM hooks.
- ACL get path calls `security_inode_get_acl()` but intentionally does not run generic xattr permission checks.
- Default ACLs are only valid on directories; setting a non-null default ACL on non-directories returns `-EACCES`.
- Delegation breaking is retried in set/remove paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/posix_acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/proc/Kconfig

## Purpose

Defines kernel configuration options for procfs and optional procfs-backed features.

## Main Options

- `PROC_FS`
  - Enables `/proc`.
  - Defaults to yes.
  - Described as a virtual filesystem that generates information dynamically.
- `PROC_KCORE`
  - Enables `/proc/kcore` live kernel ELF core view.
  - Depends on `PROC_FS && MMU`.
  - Selects `VMCORE_INFO`.
- `PROC_VMCORE`
  - Enables `/proc/vmcore` crash dump image export.
  - Depends on `PROC_FS && CRASH_DUMP`.
  - Defaults to yes.
- `PROC_VMCORE_DEVICE_DUMP`
  - Allows device hardware/firmware logs to be added as ELF notes to `/proc/vmcore`.
  - Depends on `PROC_VMCORE`.
- `NEED_PROC_VMCORE_DEVICE_RAM`
  - Internal bool selected by architectures.
- `PROC_VMCORE_DEVICE_RAM`
  - Includes device-provided RAM ranges, such as virtio-mem, in crash dump metadata.
  - Depends on `PROC_VMCORE`, `NEED_PROC_VMCORE_DEVICE_RAM`, and `VIRTIO_MEM`.
- `PROC_SYSCTL`
  - Enables `/proc/sys`.
  - Depends on `PROC_FS`, selects `SYSCTL`, defaults to yes.
- `PROC_PAGE_MONITOR`
  - Enables memory monitoring proc files such as `smaps`, `clear_refs`, `pagemap`, `kpagecount`, and `kpageflags`.
  - Depends on `PROC_FS && MMU`, defaults to yes.
- `PROC_CHILDREN`
  - Enables `/proc/<pid>/task/<tid>/children`.
  - Depends on `PROC_FS`, defaults to no.
- `PROC_PID_ARCH_STATUS`
  - Architecture-specific proc pid status support, default no.
- `PROC_CPU_RESCTRL`
  - CPU resource control proc status support, default no.

## Notes

This file controls build-time availability of many entries referenced by `fs/proc/base.c`, `array.c`, and the proc Makefile.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/proc/Makefile

## Purpose

Builds the procfs composite object and conditionally includes procfs feature objects.

## Main Contents

- Always builds `proc.o`.
- Selects memory-management implementation:
  - `nommu.o task_nommu.o` by default.
  - `task_mmu.o` when `CONFIG_MMU=y`.
- Always included proc components:
  - `inode.o`, `root.o`, `base.o`, `generic.o`, `array.o`, `fd.o`.
  - Global proc files: `cmdline.o`, `consoles.o`, `cpuinfo.o`, `devices.o`, `interrupts.o`, `loadavg.o`, `meminfo.o`, `stat.o`, `uptime.o`, `util.o`, `version.o`, `softirqs.o`, `namespaces.o`, `self.o`, `thread_self.o`.
- Conditional components:
  - `proc_tty.o` under `CONFIG_TTY`.
  - `proc_sysctl.o` under `CONFIG_PROC_SYSCTL`.
  - `proc_net.o` under `CONFIG_NET`.
  - `kcore.o` under `CONFIG_PROC_KCORE`.
  - `vmcore.o` under `CONFIG_PROC_VMCORE`.
  - `kmsg.o` under `CONFIG_PRINTK`.
  - `page.o` under `CONFIG_PROC_PAGE_MONITOR`.
  - `bootconfig.o` under `CONFIG_BOOT_CONFIG`.

## Notes

This file ties the source files in this research group into the procfs build, especially `base.o`, `generic.o`, `array.o`, and `fd.o`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/array.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/array.c

## Purpose

Formats core per-task proc outputs such as `/proc/<pid>/status`, `/proc/<pid>/stat`, `/proc/<pid>/statm`, and optionally `/proc/<pid>/task/<tid>/children`.

## Main Responsibilities

- Task name formatting:
  - `proc_task_name()` chooses worker, kernel thread, or normal task names and optionally escapes output.
- Task status:
  - `task_state()` prints state, pid namespace ids, credentials, groups, FD table size, thread/kernel-thread status.
  - `task_sig()` prints pending, blocked, ignored, caught signals, thread count, and signal queue limits.
  - `task_cap()` prints inheritable, permitted, effective, bounding, and ambient capabilities.
  - `task_seccomp()` prints `NoNewPrivs`, seccomp mode/filter count, and speculation control state.
  - `task_cpus_allowed()`, `task_core_dumping()`, `task_thp_status()`, and `task_untag_mask()` add CPU, coredump, THP, and memory tag data.
  - `proc_pid_status()` composes the full `/proc/<pid>/status`.
- `/proc/<pid>/stat` and `/proc/<pid>/task/<tid>/stat`:
  - `do_task_stat()` gathers pid/session/tty data, faults, CPU times, scheduling fields, RSS/vsize, memory address fields, signal data, wchan flag, delay accounting, guest time, and exit code.
  - `proc_tid_stat()` reports a single thread.
  - `proc_tgid_stat()` reports the whole thread group.
- `/proc/<pid>/statm`:
  - `proc_pid_statm()` prints total, resident, shared, text, lib placeholder, data, and dt placeholder fields.
- Optional `/children`:
  - Under `CONFIG_PROC_CHILDREN`, implements iteration over first-level child pids using `get_children_pid()` and seq operations.

## Key Data/Control Flow

- Uses `get_task_mm()`/`mmput()` when memory data is available.
- Uses `lock_task_sighand()` for signal-related state.
- Uses namespace-aware pid helpers such as `task_pid_nr_ns()`, `task_tgid_nr_ns()`, `task_pgrp_nr_ns()`, and `task_session_nr_ns()`.
- Uses ptrace permission checks to gate sensitive instruction pointer, stack pointer, wchan, and memory address fields.
- Applies time namespace offset to process start boottime in `/stat`.

## Security and Compatibility Notes

- Kernel addresses are not exposed in `/stat`; wchan is reduced to a 0/1 availability flag.
- Some obsolete signal fields remain in `/stat` for Linux 2.0 compatibility.
- `/children` is explicitly documented as not perfectly accurate under concurrent child exit.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/array.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/base.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/base.c

## Purpose

Implements the per-process and per-thread procfs hierarchy: `/proc/<pid>`, `/proc/<pid>/task/<tid>`, task symlinks, memory-related files, credentials/security attributes, scheduler/OOM controls, namespace/id maps, and directory lookup/readdir behavior.

## Main Responsibilities

- Defines per-entry descriptors:
  - `struct pid_entry` and macros `DIR`, `LNK`, `REG`, `ONE`, `ATTR`.
  - Static entry tables `tgid_base_stuff[]` and `tid_base_stuff[]`.
- Implements cmdline reading:
  - `get_mm_cmdline()` reads argv memory, including special `setproctitle()` handling.
  - `proc_pid_cmdline_read()` exposes `/proc/<pid>/cmdline`.
- Implements debugging/introspection files:
  - `proc_pid_wchan()` under `CONFIG_KALLSYMS`.
  - `proc_pid_stack()` under `CONFIG_STACKTRACE`, restricted to `CAP_SYS_ADMIN`.
  - `proc_pid_schedstat()` under `CONFIG_SCHED_INFO`.
  - `proc_pid_syscall()` under `CONFIG_HAVE_ARCH_TRACEHOOK`.
  - `proc_pid_personality()`, livepatch patch state, KSM stats, stack depth metrics.
- Implements `/proc/<pid>/mem`, `environ`, and `auxv`:
  - `proc_mem_open()` uses `mm_access()` and pins `mm_struct` lifetime.
  - `mem_rw()` performs remote memory access page by page.
  - `proc_mem.force_override=` early parameter controls `FOLL_FORCE` behavior.
  - `environ_read()` reads environment memory.
  - `auxv_read()` reads saved auxiliary vector.
- Implements OOM knobs:
  - `proc_oom_score()`, `oom_adj_read/write()`, and `oom_score_adj_read/write()`.
  - `__set_oom_adj()` enforces privilege rules and propagates score changes to processes sharing an mm when appropriate.
- Implements audit/fault/scheduler/time controls:
  - `loginuid` and `sessionid` under `CONFIG_AUDIT`.
  - Fault injection knobs under `CONFIG_FAULT_INJECTION`.
  - `sched`, `autogroup`, and `timens_offsets`.
  - `comm` read/write with same-thread-group restriction for renaming.
- Implements symlink behavior:
  - `proc_cwd_link()`, `proc_root_link()`, `proc_exe_link()`.
  - `proc_pid_get_link()` and `proc_pid_readlink()` check fd-style access permissions before resolving paths.
- Builds proc inodes and dentries:
  - `task_dump_owner()` computes ownership based on dumpability, credentials, user namespace, and kernel-thread state.
  - `proc_pid_make_inode()` and `proc_pid_make_base_inode()` allocate proc inodes and attach pid references.
  - `pid_revalidate()` updates dynamic ownership on lookup revalidation.
  - `pid_delete_dentry()` drops dead task dentries.
  - `proc_fill_cache()` instantiates dentries during readdir to keep readdir inode numbers consistent with stat.
- Implements `/proc/<pid>/map_files`:
  - Parses VMA address names with `dname_to_vma_addr()`.
  - Validates exact VMAs in `map_files_d_revalidate()`.
  - Resolves mapped file paths with `map_files_get_link()`.
  - Restricts symlink following to checkpoint/restore capable users.
  - Uses two-pass readdir to avoid holding `mmap_lock` during dentry instantiation.
- Implements POSIX timers and timerslack:
  - `/proc/<pid>/timers` under checkpoint/restore and POSIX timers.
  - `timerslack_ns` read/write with `CAP_SYS_NICE` and scheduler LSM checks for other tasks.
- Implements LSM attributes under `/proc/<pid>/attr`:
  - Reads/writes through `security_getprocattr()` and `security_setprocattr()`.
  - Writes are restricted to the current task and opener mm, and protected by `cred_guard_mutex`.
  - Optional Smack/AppArmor subdirectories are generated with macro helpers.
- Implements coredump filter, IO accounting, and user namespace maps:
  - `coredump_filter` under `CONFIG_ELF_CORE`.
  - `io` under `CONFIG_TASK_IO_ACCOUNTING`, gated by ptrace checks.
  - `uid_map`, `gid_map`, `projid_map`, `setgroups` under `CONFIG_USER_NS`.
- Implements directory lookup and iteration:
  - `proc_pid_lookup()` looks up numeric `/proc/<pid>` entries.
  - `proc_pid_readdir()` emits `self`, `thread-self`, and visible tgids.
  - `proc_task_lookup()` and `proc_task_readdir()` handle `/proc/<pid>/task/<tid>`.
  - `proc_dir_llseek()` preserves a cached tid cookie across partial readdir.

## Permission Model

- The file’s header warns that proc permission checks must happen at operation time, because task state changes dynamically.
- `hidepid` policy is centralized in `has_pid_permissions()` and `proc_pid_permission()`.
- Many sensitive reads use `ptrace_may_access()` with `PTRACE_MODE_READ_FSCREDS` or attach modes.
- `map_files` symlink following is additionally restricted to checkpoint/restore capability.
- `/proc/<pid>/task/<tid>/comm` has special same-thread-group permissions for pthread naming compatibility.
- Write operations for OOM, loginuid, fault injection, scheduler, time namespace, and LSM attrs include targeted capability or ownership checks.

## Lifetime and Concurrency Notes

- Task references are acquired through `get_proc_task()`, `get_pid_task()`, or pid namespace lookup, and released promptly.
- `mm_struct` lifetime is pinned with `mmgrab()` for `/mem`-style open files but memory itself is not pinned.
- Signal data uses `lock_task_sighand()` or `exec_update_lock` depending on operation.
- `/map_files` uses `mmap_read_lock_killable()` and releases it before `proc_fill_cache()`.
- Base directory inodes are linked into `pid->inodes` so `proc_flush_pid()` can invalidate dentries on task exit.

## Entry Tables

- `tgid_base_stuff[]` defines process-level entries including `task`, `fd`, `map_files`, `fdinfo`, `ns`, `net`, `environ`, `auxv`, `status`, `limits`, `sched`, `cmdline`, `stat`, `maps`, `mem`, symlinks, mounts, page monitor files, attrs, OOM knobs, namespace maps, timers, KSM and optional debug files.
- `tid_base_stuff[]` defines analogous thread-level entries, with differences such as `children` under `CONFIG_PROC_CHILDREN` and special `comm` inode operations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/base.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/bootconfig.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/bootconfig.c

## Purpose

Creates `/proc/bootconfig`, exposing extra boot configuration parsed from the kernel bootconfig tree.

## Main Responsibilities

- Stores formatted boot configuration in `saved_boot_config`.
- `boot_config_proc_show()` prints the saved string through seq_file.
- `copy_xbc_key_value_list()` walks bootconfig key/value nodes:
  - Composes full keys.
  - Prints `key = value` lines.
  - Handles arrays by printing comma-separated quoted values.
  - Chooses quote style based on whether values contain double quotes.
  - Emits empty-string values for keys without child values.
  - Appends bootloader command line comments when extra options exist.
- `proc_boot_config_init()` computes required length, allocates the saved buffer, populates it, and creates `/proc/bootconfig`.

## Notes

The proc file is initialized with `fs_initcall()` and is built only when `CONFIG_BOOT_CONFIG` includes `bootconfig.o`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/bootconfig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/cmdline.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/cmdline.c

## Purpose

Creates `/proc/cmdline`, exposing the saved kernel command line.

## Main Responsibilities

- `cmdline_proc_show()` writes `saved_command_line` followed by a newline.
- `proc_cmdline_init()` creates a permanent single proc entry named `cmdline`.
- Sets the proc entry size to `saved_command_line_len + 1`.

## Notes

This is a small global proc entry initialized with `fs_initcall()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/cmdline.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/consoles.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/consoles.c

## Purpose

Implements `/proc/consoles`, listing registered kernel consoles and their capabilities/flags/device numbers.

## Main Responsibilities

- `show_console_dev()` formats one console entry:
  - Console name and index.
  - Read/write/unblank capabilities.
  - Flags for enabled, preferred console, boot console, nbcon, printbuffer, braille, anytime.
  - Device major/minor when available from the console’s tty driver.
- Traverses consoles with seq operations:
  - `c_start()` locks the console list and advances to the requested offset.
  - `c_next()` advances through console hlist nodes.
  - `c_stop()` unlocks the console list.
- `proc_consoles_init()` creates the `consoles` seq proc entry.

## Concurrency Notes

- Holds `console_list_lock()` during seq traversal.
- Takes `console_lock()` around console `device()` callback to serialize with console operations such as vt switching.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/consoles.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/cpuinfo.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/cpuinfo.c

## Purpose

Creates `/proc/cpuinfo` using architecture-provided seq operations.

## Main Responsibilities

- Declares external `cpuinfo_op`.
- `cpuinfo_open()` opens the file with `seq_open(file, &cpuinfo_op)`.
- Defines permanent proc operations for open/read/lseek/release.
- `proc_cpuinfo_init()` creates the `cpuinfo` proc entry.

## Notes

Formatting is architecture-owned through `cpuinfo_op`; this file only wires it into procfs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/cpuinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/devices.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/devices.c

## Purpose

Implements `/proc/devices`, listing registered character and, when enabled, block device majors.

## Main Responsibilities

- `devinfo_show()` prints:
  - `Character devices:` header at index zero.
  - Character device major entries through `chrdev_show()`.
  - Under `CONFIG_BLOCK`, `Block devices:` header and block majors through `blkdev_show()`.
- Provides seq iteration over major-number space:
  - `devinfo_start()`, `devinfo_next()`, and `devinfo_stop()`.
- `proc_devices_init()` creates a permanent `devices` seq entry.

## Notes

Iteration spans `CHRDEV_MAJOR_MAX + BLKDEV_MAJOR_MAX`; block output is conditionally compiled.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/devices.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/fd.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/fd.c

## Purpose

Implements `/proc/<pid>/fd`, `/proc/<pid>/fdinfo`, and their per-file descriptor entries.

## Main Responsibilities

- `/fdinfo/<fd>` file output:
  - `seq_show()` resolves the target task and fd, prints file position, flags, mount id, inode number, file locks, and optional `show_fdinfo()`.
  - `seq_fdinfo_open()` uses `single_open()`.
- Permission model:
  - `proc_fdinfo_permission()` requires ptrace read access in addition to generic permission.
  - `proc_fd_permission()` allows normal permission or same-thread-group access, supporting `/proc/self/fd` after setuid exec.
- FD symlink behavior:
  - `tid_fd_mode()` reads target fd mode.
  - `tid_fd_update_inode()` updates dynamic owner/mode/security state.
  - `tid_fd_revalidate()` validates fd entries and refreshes inode metadata.
  - `proc_fd_link()` returns the path for a task fd.
  - `proc_fd_instantiate()` creates symlink inodes for `/fd/<fd>`.
- Directory lookup and iteration:
  - `proc_lookupfd_common()` parses numeric fd names and instantiates fd/fdinfo entries.
  - `proc_readfd_common()` iterates open fds via `fget_task_next()` and emits cache entries.
  - `proc_readfd_count()` counts open fds for directory size.
- Exports operations:
  - `proc_fd_operations`, `proc_fd_inode_operations`.
  - `proc_fdinfo_operations`, `proc_fdinfo_inode_operations`.

## Key Data/Control Flow

- `proc_fd()` from `fd.h` stores the fd number in `PROC_I(inode)->fd`.
- fd directory entries are dentry-revalidated because target fds can close or change.
- `/fd/<fd>` symlink permissions reflect read/write mode: read fds get read/execute bits; write fds get write/execute bits.

## Concurrency Notes

- Uses task locking and `files->file_lock` for direct lookup in `seq_show()`.
- Uses `fget_task()`/`fget_task_next()` helpers to safely hold file references while inspecting fd state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/fd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/fd.h -->
# File Research: sources/os/linux/linux-stable/fs/proc/fd.h

## Purpose

Declares proc fd/fdinfo operations and a helper to retrieve the fd number stored in a proc inode.

## Main Contents

- Extern declarations:
  - `proc_fd_operations`
  - `proc_fd_inode_operations`
  - `proc_fdinfo_operations`
  - `proc_fdinfo_inode_operations`
  - `proc_fd_permission()`
- Inline helper:
  - `proc_fd(struct inode *inode)` returns `PROC_I(inode)->fd`.

## Notes

This header is used by proc base code and `fd.c` to share fd directory operations.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/fd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/generic.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/generic.c

## Purpose

Provides generic procfs directory/file registration, lookup, readdir, inode metadata, creation helpers, removal helpers, and simple write support.

## Main Responsibilities

- Proc directory entry storage:
  - Maintains subdirectories in red-black trees protected by `proc_subdir_lock`.
  - `pde_subdir_find()`, `pde_subdir_insert()`, `pde_subdir_first()`, and `pde_subdir_next()` manage lookup/order.
- Entry allocation and lifetime:
  - `proc_alloc_inum()`/`proc_free_inum()` allocate dynamic proc inode numbers.
  - `pde_free()` frees names, symlink targets, and the slab object.
  - `pde_put()` drops references and frees entries.
- Generic lookup/readdir:
  - `proc_lookup_de()` finds PDEs and builds VFS inodes.
  - `proc_lookup()` respects `pidonly` proc mounts.
  - `proc_readdir_de()` emits entries from the PDE rb-tree.
  - `proc_readdir()` also respects `pidonly`.
- Directory/file inode operations:
  - `proc_setattr()` applies setattr and reflects uid/gid/mode into PDE metadata.
  - `proc_getattr()` refreshes nlink from PDE before generic stat fill.
  - `proc_dir_operations` and `proc_dir_inode_operations`.
- Proc registration:
  - `proc_register()` assigns inode number, sets permanent/read/lseek flags, inserts into parent tree, and updates nlink.
  - `__proc_create()` validates paths/names, resolves parent path components, rejects numeric names directly under `/proc`, allocates PDEs, initializes metadata, and inherits forced lookup flags.
- Creation helpers:
  - `proc_symlink()`
  - `_proc_mkdir()`, `proc_mkdir_data()`, `proc_mkdir_mode()`, `proc_mkdir()`
  - `proc_create_mount_point()`
  - `proc_create_reg()`, `proc_create_data()`, `proc_create()`
  - `proc_create_seq_private()`
  - `proc_create_single_data()`
  - `proc_set_size()` and `proc_set_user()`
- Removal helpers:
  - `remove_proc_entry()` removes one entry, runs down users, warns if non-empty.
  - `remove_proc_subtree()` removes a full subtree with permanent-entry checks.
  - `proc_remove()` wraps subtree removal for a PDE.
- Misc support:
  - `proc_get_parent_data()` retrieves parent private data.
  - `proc_simple_write()` copies a bounded user buffer and calls a PDE write callback.

## Key Data/Control Flow

- Names with path components are resolved by `__xlate_proc_name()`.
- Entries under parents marked `PROC_ENTRY_FORCE_LOOKUP` inherit force lookup behavior, important for `/proc/<pid>/net`.
- Dentry operations differ:
  - Generic proc entries use `proc_misc_dentry_ops`, which invalidates removed PDEs.
  - Forced lookup/net entries use `proc_net_dentry_ops`, which forces revalidation/deletion.
- Seq and single proc helpers wrap kernel `seq_file` APIs into `struct proc_ops`.

## Concurrency and Lifetime Notes

- `proc_subdir_lock` protects the PDE tree.
- `pde_get()`/`pde_put()` protect entries while lookup/readdir drop the tree lock.
- Removal calls `proc_entry_rundown()` before dropping final references to wait for active users.
- Permanent entries cannot be removed and trigger warnings.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/generic.c -->