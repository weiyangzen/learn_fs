# Group Research: group_822_linux_sources_os_linux_linux_fs_pipe_c_sources_os_linux_linux_fs_pno_50c501c9a5e3

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/pipe.c -->
# File Research: sources/os/linux/linux/fs/pipe.c

## Purpose
Implements Linux anonymous pipes, FIFOs, pipefs pseudo-filesystem support, pipe buffer accounting, pipe resizing, and pipe-specific syscall/fcntl/ioctl behavior. This file is the core VFS implementation behind `pipe()`, `pipe2()`, named FIFO open/read/write semantics, and kernel pipe buffers used by splice-style paths.

## Main Responsibilities
- Maintains `struct pipe_inode_info` lifetime, wait queues, reader/writer counters, ring buffers, temporary page caches, and user page accounting.
- Implements anonymous pipe reads/writes via `anon_pipe_read()` and `anon_pipe_write()`, with FIFO wrappers that update access/write metadata.
- Provides pipe buffer operations: anonymous release, steal, get, and generic exported buffer helpers.
- Creates pipe file pairs with `create_pipe_files()`, `__do_pipe_flags()`, `do_pipe_flags()`, and syscall wrappers for `pipe`/`pipe2`.
- Implements FIFO open behavior in `fifo_open()`, including blocking/nonblocking POSIX semantics for read-only, write-only, and read-write opens.
- Provides `FIONREAD`, watch queue ioctls, poll, fasync, and fcntl pipe-size controls.
- Registers the internal `pipefs` pseudo filesystem and sysctls under `fs`.

## Key Interfaces
- Exported helpers: `pipe_lock`, `pipe_unlock`, `generic_pipe_buf_try_steal`, `generic_pipe_buf_get`, `generic_pipe_buf_release`, `alloc_pipe_info`, `free_pipe_info`, `round_pipe_size`, `pipe_resize_ring`, `get_pipe_info`, `pipe_fcntl`, `do_pipe_flags`.
- File operation tables: `pipefifo_fops` for FIFOs and `pipeanon_fops` for anonymous pipes.
- Sysctls: `pipe-max-size`, `pipe-user-pages-hard`, `pipe-user-pages-soft`.

## Control Flow and Data Handling
Pipe reads acquire `pipe->mutex`, handle watch-queue loss notifications, consume `pipe_buffer` entries from tail to head, release pages when buffers empty, and wake writers/readers after unlock as needed. Writes preallocate pages outside the mutex for large writes, merge into the previous mergeable buffer when possible, allocate page-backed buffers, publish them by advancing `head`, and wake readers or writers according to empty/full transitions.

The ring uses unmasked monotonically wrapping `head`/`tail` indices, masking only at dereference. Pipe resizing allocates a new power-of-two buffer array, copies live buffers in ring order, resets `tail` to zero and `head` to occupancy, then adjusts accounting and wakeups.

## Dependencies and Integration
Depends heavily on VFS file/inode APIs, wait queues, page allocation/accounting, memcg charging, `iov_iter`, fasync, poll/epoll flags, pseudo fs registration, sysctl, and optional `CONFIG_WATCH_QUEUE`. It is also coupled to splice through pipe buffer operations and `iter_file_splice_write`.

## Concurrency and Lifetime Notes
The primary synchronization object is `pipe->mutex`; watch queues additionally use `rd_wait.lock` because notifications may arrive without holding the mutex. Reader/writer counters govern EOF, `SIGPIPE`, `EPIPE`, wakeups, and FIFO open blocking. `put_pipe_info()` frees the pipe when the last file reference disappears. Temporary page caching in `tmp_page[]` reduces allocator churn but must preserve page refcount and memcg semantics.

## Risks and Review Hotspots
- Wakeup logic is delicate: missed or excessive wakeups can deadlock jobserver-like users or break epoll behavior.
- `pipe_resize_ring()` must preserve buffer order and not shrink below current occupancy.
- Watch queue pipes are intentionally restricted for writes/splice and resizing; violating that can break notification invariants.
- Page stealing and release paths must maintain refcounts, locking, and memcg charging.
- FIFO open paths rely on reader/writer counters and partner wakeups; small changes can alter POSIX visible blocking behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/pipe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/pnode.c -->
# File Research: sources/os/linux/linux/fs/pnode.c

## Purpose
Implements mount propagation mechanics for shared, slave, private, and unbindable mounts. This file maintains propagation relationships between mount peer groups and handles propagation during mount attachment and unmount operations.

## Main Responsibilities
- Finds peer and slave mounts in propagation trees.
- Changes mount propagation type via `change_mnt_propagation()`.
- Converts groups of mounts to private with `bulk_make_private()`.
- Creates propagated secondary mount copies with `propagate_mnt()`.
- Checks whether propagation would overmount a mount with `propagation_would_overmount()`.
- Determines propagated unmount busy state and unlock behavior.
- Expands an unmount set according to propagation rules with `propagate_umount()`.

## Key Interfaces
- `get_dominating_id()`
- `change_mnt_propagation()`
- `bulk_make_private()`
- `propagate_mnt()`
- `propagation_would_overmount()`
- `propagate_mount_busy()`
- `propagate_mount_unlock()`
- `propagate_umount()`

## Control Flow and Algorithms
The file models peer groups as circular `mnt_share` lists and slave relationships as hlist chains. Propagation walks use helpers such as `propagation_next()`, `skip_propagation_subtree()`, and `next_group()` to traverse peer/slave hierarchies while respecting mounts newly created by propagation.

`propagate_mnt()` walks peer groups depth-first, determines whether secondary copies are needed, copies source trees with the right clone flags, attaches copies at the destination mountpoint, and records them in `tree_list`.

`propagate_umount()` first gathers propagated unmount candidates, trims candidates that would reveal covered mounts or violate locked mount constraints, handles locked chains, reparents surviving overmounts, and finally folds valid propagated unmounts into the caller’s set.

## Dependencies and Integration
Uses `struct mount`, `struct mountpoint`, namespace state, mount locks, `copy_tree()`, `count_mounts()`, mountpoint manipulation helpers, and propagation flags from `pnode.h`/mount internals. It is tightly integrated with namespace locking and VFS mount/unmount code.

## Concurrency and Lifetime Notes
Comments document required locks: many paths require `namespace_sem`, and unmount checks require `mount_lock` write protection. The implementation mutates shared/slave lists and temporary mount flags (`T_MARKED`, `T_UMOUNT_CANDIDATE`), so correct cleanup of marks is critical.

## Risks and Review Hotspots
- Propagation tree traversal is subtle; incorrect peer/slave ordering can duplicate, miss, or wrongly attach mounts.
- Temporary flags must be cleared on all paths to avoid corrupting later propagation operations.
- Unmount candidate trimming has security and namespace visibility implications, especially around locked mounts and overmount chains.
- `propagate_mnt()` error handling must leave copied mount trees and marks in a state expected by callers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/pnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/pnode.h -->
# File Research: sources/os/linux/linux/fs/pnode.h

## Purpose
Internal header for mount propagation support. It defines propagation state predicates, clone flags, and prototypes used by mount namespace code and `pnode.c`.

## Main Contents
- Mount state macros:
  - `IS_MNT_SHARED`
  - `IS_MNT_SLAVE`
  - `IS_MNT_NEW`
  - `IS_MNT_UNBINDABLE`
  - `IS_MNT_MARKED`
  - `IS_MNT_LOCKED`
- Mutation helpers:
  - `CLEAR_MNT_SHARED`
  - `SET_MNT_MARK`
  - `CLEAR_MNT_MARK`
  - `set_mnt_shared()`
- Clone flags:
  - `CL_EXPIRE`
  - `CL_SLAVE`
  - `CL_COPY_UNBINDABLE`
  - `CL_MAKE_SHARED`
  - `CL_PRIVATE`
  - `CL_COPY_MNT_NS_FILE`
- Peer predicate: `peers()` checks nonzero matching mount group IDs.

## Exposed Interfaces
Declares the propagation functions implemented in `pnode.c` plus cross-file mount helpers such as `mnt_release_group_id()`, `mnt_get_count()`, `mnt_set_mountpoint()`, `mnt_change_mountpoint()`, `copy_tree()`, `is_path_reachable()`, and `count_mounts()`.

## Dependencies and Integration
Includes `linux/list.h` and internal `mount.h`. It is an internal VFS mount header, not a user-facing API.

## Risks and Review Hotspots
- Macros directly inspect and mutate mount flags; callers must hold the correct locks.
- `peers()` treats group ID zero as non-peer even if IDs match, which is essential for private/non-shared mounts.
- Clone flag values are consumed by tree-copying and propagation logic; changing them affects mount namespace semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/pnode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/posix_acl.c -->
# File Research: sources/os/linux/linux/fs/posix_acl.c

## Purpose
Provides generic VFS support for POSIX ACLs: inode ACL caching, ACL allocation/refcounting, validation, permission checks, chmod/create mode transformations, xattr encoding/decoding, idmapped mount handling, and VFS-level ACL get/set/remove operations.

## Main Responsibilities
- Manages cached access/default ACL pointers in inodes.
- Fetches ACLs through filesystem inode operations with sentinel-based race handling.
- Allocates, initializes, clones, validates, and releases ACL objects.
- Converts ACLs to and from traditional Unix mode bits.
- Applies POSIX ACL permission checks with user/group/idmap handling.
- Computes inherited ACLs during file creation and updates ACLs during chmod.
- Converts ACLs between in-memory and xattr/uapi representations.
- Provides VFS ACL set/get/remove helpers with LSM hooks, delegation breaking, ownership checks, and fsnotify.
- Provides simple filesystem helpers for cached in-memory ACLs.

## Key Interfaces
Exports or defines:
- Cache: `get_cached_acl`, `get_cached_acl_rcu`, `set_cached_acl`, `forget_cached_acl`, `forget_all_cached_acls`, `get_inode_acl`.
- Object handling: `posix_acl_init`, `posix_acl_alloc`, `posix_acl_clone`.
- Validation/conversion: `posix_acl_valid`, `posix_acl_equiv_mode`, `posix_acl_from_mode`, `posix_acl_from_xattr`, `posix_acl_to_xattr`.
- Permission/mode: `posix_acl_permission`, `__posix_acl_create`, `__posix_acl_chmod`, `posix_acl_chmod`, `posix_acl_create`, `posix_acl_update_mode`.
- VFS operations: `set_posix_acl`, `vfs_set_acl`, `vfs_get_acl`, `vfs_remove_acl`, `do_set_acl`, `do_get_acl`.
- Simple helpers: `simple_set_acl`, `simple_acl_create`.

## Control Flow and Data Handling
ACL cache access uses inode `i_acl` and `i_default_acl` with RCU/refcount coordination. `__get_acl()` installs an uncached sentinel before invoking filesystem callbacks, so concurrent fetches or invalidations can be detected without corrupting cache state.

ACL validation enforces POSIX ordering and required mask entries. Permission checking walks entries in order, first checking owner, then named users, owning group, named groups, mask, and other. Idmapped mounts are handled through VFS uid/gid conversion helpers during permission checks and user-visible xattr conversion.

Setting ACLs parses the ACL name, translates IDs for idmapped mounts, locks the inode, checks write-xattr permission, invokes LSM hooks, breaks delegations, calls the filesystem `set_acl`, and posts fsnotify/security notifications. Getting ACLs performs LSM checks, rejects unsupported inode types, fetches via cache/filesystem, and converts missing ACLs to `-ENODATA`.

## Dependencies and Integration
Integrates with inode operations (`get_acl`, `get_inode_acl`, `set_acl`), xattr names, user namespaces, idmapped mounts, LSM hooks, fsnotify, delegation handling, and VFS inode locking. Filesystems use these helpers to avoid duplicating ACL semantics.

## Concurrency and Lifetime Notes
ACL objects are refcounted. Cache replacement uses atomic exchange and releases old ACLs unless they are uncached sentinels. VFS set/remove paths hold inode locks and may retry after breaking delegations. RCU paths must not take references unless safe.

## Risks and Review Hotspots
- ACL cache sentinel logic is race-sensitive.
- ID mapping must be correct at the filesystem boundary versus user boundary; mixing mount idmaps with filesystem cache representation would be a security bug.
- `posix_acl_update_mode()` can clear setgid and null out equivalent ACLs; callers must honor modified pointers.
- xattr parsing validates sizes, versions, uid/gid mappings, and ACL structure; relaxing checks can admit invalid on-disk ACLs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/posix_acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/Kconfig -->
# File Research: sources/os/linux/linux/fs/proc/Kconfig

## Purpose
Defines Kconfig options controlling procfs availability and optional procfs features.

## Main Options
- `PROC_FS`: core `/proc` filesystem support, default enabled.
- `PROC_KCORE`: live kernel ELF core file at `/proc/kcore`.
- `PROC_VMCORE`: crash dump image export at `/proc/vmcore`.
- `PROC_VMCORE_DEVICE_DUMP`: optional device firmware/hardware dump notes in vmcore.
- `NEED_PROC_VMCORE_DEVICE_RAM` and `PROC_VMCORE_DEVICE_RAM`: support adding RAM discovered by devices such as virtio-mem to vmcore.
- `PROC_SYSCTL`: `/proc/sys` sysctl interface.
- `PROC_PAGE_MONITOR`: process/page monitoring files such as smaps, clear_refs, pagemap, kpagecount, and kpageflags.
- `PROC_CHILDREN`: optional `/proc/<pid>/task/<tid>/children`.
- `PROC_PID_ARCH_STATUS`: arch-specific pid status hook.
- `PROC_CPU_RESCTRL`: CPU resource control proc status hook.

## Dependencies and Integration
Options depend on broader kernel facilities including `MMU`, `CRASH_DUMP`, `VIRTIO_MEM`, `SYSCTL`, and `PROC_FS`. The Makefile consumes these symbols to include optional procfs object files.

## Risks and Review Hotspots
- Several procfs interfaces expose sensitive memory, process, or crash data; Kconfig dependencies and defaults materially affect attack surface.
- Disabling procfs or sysctl can break userspace expectations.
- `PROC_PAGE_MONITOR` gates interfaces used by monitoring/debugging tools but also exposes memory layout and page state information.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/Makefile -->
# File Research: sources/os/linux/linux/fs/proc/Makefile

## Purpose
Build rules for procfs objects.

## Main Behavior
- Builds the procfs composite object via `obj-y += proc.o`.
- Selects `task_mmu.o` when `CONFIG_MMU` is enabled, otherwise `nommu.o` and `task_nommu.o`.
- Always includes core files such as `inode.o`, `root.o`, `base.o`, `generic.o`, `array.o`, `fd.o`, and common `/proc` files (`cmdline`, `consoles`, `cpuinfo`, `devices`, etc.).
- Conditionally includes objects for TTY, sysctl, networking, kcore, vmcore, printk kmsg, page monitor, and bootconfig.

## Dependencies and Integration
Directly reflects Kconfig choices from `fs/proc/Kconfig` and other subsystem configs. This Makefile defines the compiled surface area of procfs.

## Risks and Review Hotspots
- Object inclusion determines whether sensitive proc entries exist.
- `task_mmu.o` receives `-Wno-override-init`, indicating known initializer patterns in that file.
- Conditional object coverage must match declarations used by `base.c` and other procfs files.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/array.c -->
# File Research: sources/os/linux/linux/fs/proc/array.c

## Purpose
Renders process and thread status/statistics text for procfs, especially `/proc/<pid>/status`, `/proc/<pid>/stat`, `/proc/<pid>/statm`, and optional `/proc/<pid>/task/<tid>/children`.

## Main Responsibilities
- Formats task names, states, IDs, credentials, groups, namespace PID views, and kernel-thread status.
- Renders signal pending/blocked/ignored/caught sets.
- Renders capabilities, seccomp state, speculation mitigation state, CPU masks, cpuset status, context switch counts, THP state, untag mask, and arch thread features.
- Emits the legacy fixed-field `/proc/<pid>/stat` and `/proc/<tid>/stat` formats.
- Emits `/proc/<pid>/statm` memory summary.
- Optionally emits first-level child PIDs when `CONFIG_PROC_CHILDREN` is enabled.

## Key Interfaces
- `proc_task_name()`
- `render_sigset_t()`
- `proc_pid_status()`
- `proc_tid_stat()`
- `proc_tgid_stat()`
- `proc_pid_statm()`
- `proc_tid_children_operations` under `CONFIG_PROC_CHILDREN`

## Control Flow and Data Handling
`proc_pid_status()` composes a multi-line human-readable status file. It obtains task memory via `get_task_mm()`, credentials via `get_task_cred()`, signal state under `lock_task_sighand()`, and namespace-aware IDs from pid namespace helpers.

`do_task_stat()` renders the legacy numeric stat line. It holds `exec_update_lock` while gathering sensitive execution fields, gates some fields behind `ptrace_may_access()`, and aggregates either thread-group-wide or per-thread counters. It intentionally masks or zeroes fields that are racy or sensitive.

The optional children seq file walks the task’s children under `tasklist_lock`, with comments documenting that the output is not perfectly race-free unless tasks are frozen.

## Dependencies and Integration
Depends on scheduler, signal, credential, pid namespace, time namespace, memory-management, cpuset, seccomp, ptrace, architecture, and procfs internals. `base.c` references these renderers in PID/TID entry tables.

## Concurrency and Lifetime Notes
The code uses RCU, task locks, sighand locks, `exec_update_lock`, seqlock reads for signal stats, and mm references. Many values are snapshots and can race with process exit or exec; the implementation prefers stable references and permission-gated fallbacks.

## Risks and Review Hotspots
- `/proc/<pid>/stat` field ordering is ABI-sensitive.
- Permission-gated address and wchan fields are security-sensitive.
- Namespace conversions must remain correct for nested PID/user namespaces.
- Children iteration explicitly trades precision for speed and should not be treated as an exact process-tree API.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/array.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/base.c -->
# File Research: sources/os/linux/linux/fs/proc/base.c

## Purpose
Central implementation of per-process and per-thread procfs directories. It defines dynamic `/proc/<pid>` and `/proc/<pid>/task/<tid>` entry tables, lookup/readdir behavior, permissions, inode ownership, symlinks, high-sensitivity files such as `mem` and `map_files`, process control knobs, namespace mapping files, and task dcache invalidation.

## Main Responsibilities
- Defines `struct pid_entry` and macros for PID directory entries.
- Implements `/proc/<pid>/cmdline`, `environ`, `auxv`, `mem`, `cwd`, `root`, `exe`, `wchan`, `stack`, `limits`, `sched`, `oom_*`, `comm`, `timerslack_ns`, and many config-gated entries.
- Enforces hidepid, ptrace, capability, LSM, and same-thread-group permission rules.
- Creates proc inodes tied to task/pid lifetime and updates ownership based on dumpability and credentials.
- Provides dynamic lookup and readdir for PID directories, TID directories, `/task`, `/fd`, `/fdinfo`, `/map_files`, `/attr`, and related subdirectories.
- Exposes user namespace id maps and `setgroups` files.
- Flushes proc dentries for exiting pids.

## Key Interfaces
- Entry helpers: `proc_pid_make_inode()`, `proc_pid_make_base_inode()`, `proc_fill_cache()`.
- Permission/lifetime: `proc_pid_permission()`, `pid_getattr()`, `pid_update_inode()`, `pid_delete_dentry()`, `proc_flush_pid()`.
- Root PID operations: `proc_pid_lookup()`, `proc_pid_readdir()`.
- Task operations: `proc_task_lookup()`, `proc_task_readdir()`, `proc_task_getattr()`.
- Memory access: `proc_mem_open()`, `mem_read()`, `mem_write()`, `mem_lseek()`.
- Link helpers: `proc_pid_link_inode_operations`, `proc_pid_readlink()`, `proc_pid_get_link()`.
- Initialization helper: `set_proc_pid_nlink()`.

## Control Flow and Data Handling
PID directory lookup parses numeric names, finds tasks in the proc superblock’s PID namespace, applies hidepid policy, and instantiates a task-backed directory inode. Readdir emits `self`, `thread-self`, then iterates TGIDs with `find_ge_pid()` while skipping hidden tasks.

PID/TID subentry lookup scans static `pid_entry` arrays and instantiates entries with the right file/inode operations. Directory iteration uses `proc_fill_cache()` to keep dcache inode numbers consistent with stat output.

`/proc/<pid>/mem` opens by acquiring an mm through ptrace-aware `mm_access()`, stores a stable mm reference in `file->private_data`, and reads/writes remote memory page by page via `access_remote_vm()`. The `proc_mem.force_override` early parameter controls when `FOLL_FORCE` is used.

`map_files` parses VMA address ranges from dentry names, verifies exact VMAs under `mmap_lock`, lists file-backed VMAs in two passes, and restricts symlink following to checkpoint/restore capable callers.

## Dependencies and Integration
Integrates with procfs root/inode internals, pid namespaces, user namespaces, ptrace, LSM hooks, cgroups, cpuset, memory management, VMA iteration, scheduler, audit, OOM, file descriptors, mount namespace files, proc page-monitor files, timers, KSM, livepatch, seccomp, networking, and architecture hooks.

## Concurrency and Lifetime Notes
Task references are acquired with `get_proc_task()`, `get_pid_task()`, or RCU lookups. Sensitive task state is protected by task locks, `exec_update_lock`, signal locks, mmap locks, inode locks, and namespace/capability checks. Proc directory inodes are linked into pid inode lists so `proc_flush_pid()` can invalidate dentries on exit.

## Risks and Review Hotspots
- `/proc/<pid>/mem`, `map_files`, symlink resolution, and stack/wchan output are security-critical.
- hidepid and ptrace checks must stay consistent across lookup, getattr, readdir, and open/read paths.
- PID/TID readdir uses position cookies and cached TID fallback; seek/short-read behavior is ABI-sensitive.
- `pid_entry` tables define proc ABI surface; adding entries affects permissions, nlink counts, and userspace.
- Inode ownership depends on dumpability and credentials and can change at runtime.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/base.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/bootconfig.c -->
# File Research: sources/os/linux/linux/fs/proc/bootconfig.c

## Purpose
Creates `/proc/bootconfig`, exposing extra boot configuration in a normalized text format.

## Main Responsibilities
- Walks bootconfig key/value nodes.
- Composes key names and quoted values into a saved buffer.
- Appends bootloader command-line parameters when extra options are present.
- Registers a single proc file that emits the saved bootconfig buffer.

## Key Interfaces
- `boot_config_proc_show()`
- `copy_xbc_key_value_list()`
- `proc_boot_config_init()`

## Control Flow and Data Handling
At init, the file first calls `copy_xbc_key_value_list(NULL, 0)` to compute required output length, allocates `saved_boot_config`, then calls the same formatter again to fill it. Values are quoted with either double or single quotes depending on embedded quote characters. Empty values are rendered as `""`.

## Dependencies and Integration
Depends on bootconfig parser APIs (`xbc_for_each_key_value`, `xbc_node_compose_key`, array value helpers), `boot_command_line`, seq_file, and procfs creation.

## Risks and Review Hotspots
- Length calculation and formatting share one function; `snprintf` return handling must remain correct.
- Saved output is allocated once at init and intentionally reused for reads.
- Quoting is minimal and tailored to display, not a general parser/serializer contract.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/bootconfig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/cmdline.c -->
# File Research: sources/os/linux/linux/fs/proc/cmdline.c

## Purpose
Creates `/proc/cmdline`, exposing the saved kernel command line.

## Main Responsibilities
- Implements a seq_file show callback that writes `saved_command_line` followed by newline.
- Registers a permanent single proc entry named `cmdline`.
- Sets proc entry size to `saved_command_line_len + 1`.

## Key Interfaces
- `cmdline_proc_show()`
- `proc_cmdline_init()`

## Dependencies and Integration
Uses procfs single-file helpers and global command-line state from proc internals/kernel init.

## Risks and Review Hotspots
- This is a stable userspace ABI file; output format changes would affect tooling.
- The proc entry is made permanent, so removal is not expected.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/cmdline.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/consoles.c -->
# File Research: sources/os/linux/linux/fs/proc/consoles.c

## Purpose
Implements `/proc/consoles`, listing registered kernel consoles and their capabilities, flags, and device numbers.

## Main Responsibilities
- Iterates the console list through seq_file operations.
- Formats console name/index, read/write/unblank capabilities, console flags, and optional major/minor device.
- Serializes console device lookup with `console_lock()`.
- Protects list traversal with `console_list_lock()`.

## Key Interfaces
- `show_console_dev()`
- `consoles_op`
- `proc_consoles_init()`

## Control Flow and Data Handling
The seq start operation locks the console list and advances to the requested position. `show_console_dev()` builds a compact flag string from known `CON_*` bits and optionally asks the console for its backing tty driver/device index. Stop releases the console list lock.

## Dependencies and Integration
Depends on console core APIs, tty drivers, seq_file, and procfs creation.

## Risks and Review Hotspots
- Console list traversal requires correct lock pairing across seq start/stop.
- `con->device()` is serialized with `console_lock()` because console state such as foreground console can change.
- Output is consumed by diagnostics and should remain stable.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/consoles.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/cpuinfo.c -->
# File Research: sources/os/linux/linux/fs/proc/cpuinfo.c

## Purpose
Registers `/proc/cpuinfo`, delegating architecture-specific CPU information rendering to the external `cpuinfo_op` seq operations.

## Main Responsibilities
- Opens `cpuinfo_op` with `seq_open()`.
- Defines proc operations using `seq_read_iter`, `seq_lseek`, and `seq_release`.
- Registers a permanent proc entry named `cpuinfo`.

## Key Interfaces
- `cpuinfo_open()`
- `cpuinfo_proc_ops`
- `proc_cpuinfo_init()`

## Dependencies and Integration
The actual content is provided by architecture-defined `cpuinfo_op`. This file supplies generic procfs registration and seq plumbing.

## Risks and Review Hotspots
- ABI content is architecture-specific, but registration and read behavior must remain stable.
- Entry is permanent, matching core procfs expectations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/cpuinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/devices.c -->
# File Research: sources/os/linux/linux/fs/proc/devices.c

## Purpose
Implements `/proc/devices`, listing registered character and block device majors.

## Main Responsibilities
- Iterates through character major range and, when block support is enabled, block major range.
- Emits section headers for character and block devices.
- Calls `chrdev_show()` and `blkdev_show()` for per-major content.
- Registers a permanent seq proc entry named `devices`.

## Key Interfaces
- `devinfo_show()`
- `devinfo_ops`
- `proc_devices_init()`

## Dependencies and Integration
Depends on character device registry, optional block device registry, seq_file, and procfs.

## Risks and Review Hotspots
- Iteration bounds combine `CHRDEV_MAJOR_MAX` and `BLKDEV_MAJOR_MAX`; block-disabled builds still compile with the shared logic.
- Output format is longstanding userspace ABI for device discovery/debugging.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/devices.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/fd.c -->
# File Research: sources/os/linux/linux/fs/proc/fd.c

## Purpose
Implements `/proc/<pid>/fd` symlink directories and `/proc/<pid>/fdinfo` metadata directories for task file descriptors.

## Main Responsibilities
- Lists open file descriptors for a task.
- Instantiates fd symlinks that resolve to the file path of a specific descriptor.
- Instantiates fdinfo regular files that show position, flags, mount ID, inode number, locks, and file-specific fdinfo.
- Enforces ptrace-read permissions for fdinfo.
- Provides same-thread-group permission bypass for `/proc/self/fd` use after setuid-like transitions.
- Updates fd symlink inode mode based on target file read/write mode.

## Key Interfaces
- `proc_fd_operations`
- `proc_fd_inode_operations`
- `proc_fdinfo_operations`
- `proc_fdinfo_inode_operations`
- `proc_fd_permission()`
- Internal helpers: `proc_fd_link()`, `proc_fd_instantiate()`, `proc_fdinfo_instantiate()`, `proc_readfd_common()`, `proc_lookupfd_common()`.

## Control Flow and Data Handling
Fd lookup parses the dentry name as an integer fd, gets the task, verifies the fd exists via `fget_task()`, records the file mode, and instantiates either a symlink or fdinfo file.

Directory iteration emits dots, then repeatedly calls `fget_task_next()` to find the next open fd from the task’s file table. Each fd is passed to `proc_fill_cache()` to create dcache-consistent entries.

Fdinfo reads acquire the task and file under task/file locks, snapshot flags including close-on-exec, take a file reference, release task locks, then print metadata and optional file-specific information.

## Dependencies and Integration
Uses procfs inode helpers from `base.c`, file descriptor tables, path/mount internals, file locks, ptrace checks, LSM inode labeling, and VFS link operations.

## Concurrency and Lifetime Notes
The code takes task references and file references before using task file data outside locks. Dentry revalidation checks that the fd still exists and refreshes inode ownership/mode. `pid_delete_dentry()` removes stale entries when the task exits.

## Risks and Review Hotspots
- fd table iteration races with close/open; file references must be taken before use.
- fdinfo exposes sensitive state and therefore requires ptrace read permission.
- `/proc/<pid>/fd` permission behavior is intentionally special for same-thread-group access.
- Symlink mode is derived from file mode and can change as the fd target changes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/fd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/fd.h -->
# File Research: sources/os/linux/linux/fs/proc/fd.h

## Purpose
Internal procfs header declaring fd/fdinfo operations and helper accessors used by per-process procfs code.

## Main Contents
- Extern declarations for:
  - `proc_fd_operations`
  - `proc_fd_inode_operations`
  - `proc_fdinfo_operations`
  - `proc_fdinfo_inode_operations`
  - `proc_fd_permission()`
- Inline helper `proc_fd()` returning `PROC_I(inode)->fd`.

## Dependencies and Integration
Includes `linux/fs.h` and relies on proc inode internals through `PROC_I`. Used by `base.c` to wire `/proc/<pid>/fd`, `/fdinfo`, and `map_files` permissions, and by `fd.c` for implementation.

## Risks and Review Hotspots
- `proc_fd()` assumes the inode is a proc inode with a valid fd field.
- The shared `proc_fd_permission()` is used outside `fd.c`, so behavior changes affect multiple procfs directories.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/fd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/generic.c -->
# File Research: sources/os/linux/linux/fs/proc/generic.c

## Purpose
Provides generic procfs directory-entry infrastructure: `struct proc_dir_entry` allocation/freeing, name lookup, rb-tree child management, dynamic inode allocation, proc entry registration/removal, and helper APIs for creating proc files, directories, symlinks, seq files, and single files.

## Main Responsibilities
- Maintains each proc directory’s children in an rb-tree under `proc_subdir_lock`.
- Allocates dynamic proc inode numbers from an IDA range.
- Implements generic proc lookup and readdir over `proc_dir_entry` trees.
- Defines generic proc directory/file inode operations.
- Creates and registers proc symlinks, directories, mount points, regular entries, seq entries, and single entries.
- Removes individual proc entries or entire subtrees with rundown and refcount release.
- Provides helpers to set proc entry size, ownership, and permanent status.

## Key Interfaces
- Lookup/readdir: `proc_lookup_de()`, `proc_lookup()`, `proc_readdir_de()`, `proc_readdir()`.
- Registration/creation: `proc_register()`, `proc_symlink()`, `_proc_mkdir()`, `proc_mkdir_data()`, `proc_mkdir_mode()`, `proc_mkdir()`, `proc_create_mount_point()`, `proc_create_reg()`, `proc_create_data()`, `proc_create()`, `proc_create_seq_private()`, `proc_create_single_data()`.
- Removal/lifetime: `pde_put()`, `remove_proc_entry()`, `remove_proc_subtree()`, `proc_remove()`.
- Metadata: `proc_set_size()`, `proc_set_user()`, `proc_get_parent_data()`, `proc_simple_write()`, `impl_proc_make_permanent()`.

## Control Flow and Data Handling
Creation resolves slash-separated names with `xlate_proc_name()`, validates final component names, allocates a `proc_dir_entry`, stores names inline when small, inherits parent ownership, and registers the entry into the parent rb-tree. Registration allocates a dynamic proc inode number and increments parent link count.

Lookup searches the rb-tree, takes a PDE reference, creates an inode with `proc_get_inode()`, and splices it into dcache with appropriate dentry operations. Readdir walks the rb-tree in sorted order and emits entries by stored inode number and mode.

Removal erases entries from parent rb-trees under write lock, rejects permanent entries, runs `proc_entry_rundown()`, warns on non-empty single-entry removal, and releases PDE references. Subtree removal walks descendants depth-first.

## Dependencies and Integration
Used across procfs and by many kernel subsystems that call proc creation APIs. Integrates with proc inode creation, dcache operations, seq_file, IDA allocation, rbtrees, module lifetime/rundown, and proc root state.

## Concurrency and Lifetime Notes
`proc_subdir_lock` protects tree lookup/insertion/removal. PDE refcounts protect entries while lookups/readdir temporarily drop the tree lock. Removal calls rundown so openers complete safely before final release. Permanent entries cannot be removed.

## Risks and Review Hotspots
- Tree/refcount/rundown ordering is critical for module unload safety.
- Name validation prevents collisions with dynamic PID directories at `/proc` root.
- `pidonly` mounts hide generic proc entries and must be respected in lookup/readdir.
- Subtree removal can abort on permanent descendants after partial unlinking, so callers must avoid mixed permanent/removable trees.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/generic.c -->