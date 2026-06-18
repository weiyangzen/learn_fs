# Group Research: group_1160_minix_sources_teaching_minix_minix_fs_ptyfs_ptyfs_c_sources_teachin_3c3969fb108b

Scope checked against `Docs/research_subset_a.md`: all requested files are under `sources/teaching/minix`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/ptyfs/ptyfs.c -->
# File Research: sources/teaching/minix/minix/fs/ptyfs/ptyfs.c

PTYFS is the `/dev/pts` filesystem server for Unix98 pseudoterminal slave nodes. It is an `fsdriver`-based in-memory filesystem with fixed root inode `1` and slave inodes computed as `BASE_INO_NR + index`.

Key responsibilities:
- Mounts as a non-root filesystem and returns a synthetic root node.
- Resolves `"."` and numeric slave names through `ptyfs_lookup`.
- Enumerates `"."`, `".."`, and allocated slave nodes through `ptyfs_getdents`.
- Supports metadata-only `chown`, `chmod`, `stat`, and `statvfs`.
- Accepts non-filesystem control messages from the service label `"pty"`:
  - `PTYFS_SET` creates or updates a slave node.
  - `PTYFS_CLEAR` removes a slave node.
  - `PTYFS_NAME` returns the generated slave node name.
- Initializes node storage through `init_nodes()` and exits cleanly on `SIGTERM`.

Important interactions:
- Depends on `node.h` functions `init_nodes`, `get_node`, `set_node`, `clear_node`, and `get_max_node`.
- Uses DS label lookup to restrict control messages to PTY.
- Runs through `fsdriver_task` with a small callback table.

Notable detail:
- `parse_name` rejects non-digits, leading zeroes, and arithmetic overflow.
- `make_name` calls `snprintf(name, sizeof(name), ...)` even though `name` is a pointer parameter; that uses pointer size rather than the supplied buffer size and can truncate generated names unexpectedly.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/ptyfs/ptyfs.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/vbfs/Makefile -->
# File Research: sources/teaching/minix/minix/fs/vbfs/Makefile

Build file for the VirtualBox Shared Folders filesystem server.

Key contents:
- Builds program `vbfs` from `vbfs.c`.
- Installs manual page `vbfs.8`.
- Installs `vbfs.conf` as `/etc/system.conf.d/vbfs`.
- Links against `libsffs`, `libvboxfs`, `libfsdriver`, and `libsys`.
- Uses `<minix.service.mk>`, so the target is built and installed as a MINIX service.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/vbfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/vbfs/vbfs.c -->
# File Research: sources/teaching/minix/minix/fs/vbfs/vbfs.c

VBFS is a thin MINIX VirtualBox shared-folder filesystem server. It configures the SFFS layer and connects it to the VirtualBox shared-folder backend.

Key responsibilities:
- Documents the stack: `VBFS -> libsffs -> libvboxfs -> libsys/vbox -> VBOX driver -> VirtualBox host`.
- Parses `-o` options using `optset`: `share`, `prefix`, `uid`, `gid`, `fmask`, `dmask`.
- Sets defaults for ownership, masks, prefix, and case sensitivity.
- Requires a non-empty share name.
- Initializes `libvboxfs` and receives the SFFS operation table, case-sensitivity flag, and read-only flag.
- Initializes SFFS with server name `"VBFS"`.
- Registers SEF fresh-start initialization and delegates signal handling to `sffs_signal`.
- Runs `sffs_loop()` and calls `vboxfs_cleanup()` after the loop exits.

Failure behavior:
- Missing share returns `EINVAL`.
- Unknown host share reports `ENOENT`.
- If SFFS init fails after VBOXFS init, it cleans up `libvboxfs`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/vbfs/vbfs.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/fs/vbfs/vbfs.conf -->
# File Research: sources/teaching/minix/minix/fs/vbfs/vbfs.conf

Service configuration for the `vbfs` filesystem server.

Key contents:
- Declares `service vbfs`.
- Allows IPC with `SYSTEM`, `pm`, `vfs`, `rs`, `ds`, `vm`, and `vbox`.
- Grants VM calls `SETCACHEPAGE` and `CLEARCACHE`.

Role:
- Provides the runtime service permissions needed for VBFS to talk to VFS, VM, service management, DS, and the VirtualBox driver.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/fs/vbfs/vbfs.conf -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/lib/libminixfs/Makefile -->
# File Research: sources/teaching/minix/minix/lib/libminixfs/Makefile

Build file for `libminixfs`.

Key contents:
- Includes `<bsd.own.mk>`.
- Adds `_MINIX_SYSTEM` to `CPPFLAGS`.
- Builds library `minixfs`.
- Compiles `cache.c` and `bio.c`.
- Includes `<bsd.lib.mk>` for library build rules.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/lib/libminixfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/lib/libminixfs/bio.c -->
# File Research: sources/teaching/minix/minix/lib/libminixfs/bio.c

`bio.c` adapts `libminixfs` buffer-cache operations into block I/O hooks usable by filesystem servers, especially root-capable filesystems.

Key responsibilities:
- `lmfs_driver` records the driver label for a device major through `bdev_driver`.
- `lmfs_bio` implements block-device read, write, and peek over cached filesystem blocks.
- `block_prefetch` uses `lmfs_readahead` to prefetch contiguous blocks for reads and peeks.
- `lmfs_bflush` flushes and invalidates cached blocks for a block device.

Important behavior:
- Validates `NO_DEV`, zero-length I/O, negative offsets, oversized byte counts, and offset overflow.
- Uses `DIOCGETP` on every call to determine current partition size, because repartitioning may change geometry.
- Handles EOF and partial final device blocks explicitly.
- For full-block writes, uses `NO_READ` to avoid reading data that will be overwritten.
- Marks buffers dirty after write copy-in even if copy-in fails, because the copy may have partially succeeded.
- Returns transferred byte count when partial progress was made, or the error if no bytes were transferred.

Dependencies:
- Uses `lmfs_get_block`, `lmfs_get_partial_block`, `lmfs_put_block`, `lmfs_markdirty`, `lmfs_flushdev`, and `lmfs_invalidate`.
- Uses `bdev_ioctl` for geometry and `fsdriver_copyin/copyout` for user-buffer movement.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/lib/libminixfs/bio.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/lib/libminixfs/cache.c -->
# File Research: sources/teaching/minix/minix/lib/libminixfs/cache.c

`cache.c` implements the shared MINIX filesystem block cache. It maintains a local buffer pool with hash lookup, LRU eviction, dirty tracking, read-ahead, writeback, optional VM secondary-cache integration, dynamic sizing, and file-hole cache support.

Core data structures and state:
- `buf` is the buffer array.
- `buf_hash` maps block numbers to cache chains.
- `front` and `rear` form an LRU list of unused buffers.
- `bufs_in_use` counts referenced buffers.
- `fs_block_size` tracks the filesystem block size.
- `fs_btotal` and `fs_bused` feed cache-size heuristics.
- `vmcache` and `may_use_vmcache` control VM cache integration.

Key responsibilities:
- `lmfs_get_block`, `lmfs_get_block_ino`, and `lmfs_get_partial_block` acquire cached blocks by device/block, optionally associating them with inode offsets for VM mappings.
- `lmfs_put_block` returns buffers to the LRU and may hand them to VM with `vm_set_cacheblock`.
- `lmfs_markdirty`, `lmfs_markclean`, and `lmfs_isclean` manage dirty state.
- `lmfs_free_block` forgets VM cache state and invalidates local state for freed blocks.
- `lmfs_zero_block_ino` creates one-shot zero blocks for file holes in VM mappings.
- `lmfs_readahead` and `lmfs_prefetch` batch best-effort reads.
- `lmfs_flushdev` writes dirty unused buffers for one device.
- `lmfs_flushall` flushes all devices and triggers deferred cache resizing checks.
- `lmfs_invalidate` purges all blocks for a device locally and in VM.
- `lmfs_buf_pool`, `lmfs_set_blocksize`, and cache heuristics allocate and resize the buffer pool.

I/O behavior:
- Local cache lookup ignores entries marked `VMMC_EVICTED`.
- VM cache is queried before disk reads when enabled and request mode is not `NO_READ`.
- `PEEK` returns `ENOENT` when neither local nor VM cache has the block.
- `read_block` handles both page-sized and multi-page blocks using `bdev_read` or `bdev_gather`.
- `rw_scattered` batches contiguous reads/writes using gather/scatter vectors and sorts dirty writes by block number.

Notable risks and caveats:
- Several static buffers/lists are used, consistent with single-service threading assumptions but worth noting for reentrancy.
- Dirty buffers in use are deliberately not flushed to avoid writing partially updated contents.
- VM cache failures disable VM calls on `ENOSYS`, log on `ENOMEM`, and panic for unexpected failures.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/lib/libminixfs/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/lib/libminixfs/inc.h -->
# File Research: sources/teaching/minix/minix/lib/libminixfs/inc.h

Small internal header for `libminixfs`.

Declarations:
- `lmfs_get_partial_block`
- `lmfs_readahead`
- `lmfs_readahead_limit`

Role:
- Shares internal cache helpers between `cache.c` and `bio.c`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/lib/libminixfs/inc.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/Makefile -->
# File Research: sources/teaching/minix/minix/servers/vfs/Makefile

Build file for the MINIX Virtual File System server.

Key contents:
- Builds program `vfs`.
- Compiles the core VFS modules: startup/main loop, open/read/write, pipes, mount/path/device handling, link/exec, descriptors, stat/protection/time, locks, requests, vnode/vmnt, threads, block/character/socket devices.
- Adds `gcov.c` and `-DUSE_COVERAGE` when coverage is enabled.
- Adds a GCC warning suppression for MINIX optimized builds.
- Uses strict warning flags: `-Wall -Wextra -Wno-sign-compare -Werror`.
- Links against `libsys`, `libtimers`, `libexec`, and `libmthread`.
- Uses `<minix.service.mk>`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/bdev.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/bdev.c

`bdev.c` handles VFS operations on block device nodes opened by user processes.

Key responsibilities:
- `bdev_open` sends `BDEV_OPEN` to the mapped block driver.
- `bdev_close` sends `BDEV_CLOSE`.
- `bdev_ioctl` creates an IOCTL grant and sends `BDEV_IOCTL`.
- `bdev_reply` wakes the worker thread waiting for a block-driver reply.
- `bdev_up` handles block-driver restart/recovery by reopening block-special filps and notifying mounted filesystems of the new driver label.

Important behavior:
- Block drivers are treated synchronously: operations block the worker thread until reply.
- `bdev_sendrec` retries `ERESTART` up to five times.
- Dead driver endpoints trigger `dmap_unmap_by_endpt` and return `EIO`.
- Open access bits are translated from `R_BIT/W_BIT` to block-driver flags.
- On driver recovery, open block-special files are reopened once per filp, and affected mounted filesystems receive `req_newdriver`.

Dependencies:
- Uses `dmap` major-device mappings.
- Uses `drv_sendrec` from `comm.c`.
- Uses `make_ioctl_grant` from `device.c`.
- Coordinates with filp/vnode/vmnt tables.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/bdev.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/cdev.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/cdev.c

`cdev.c` handles character device operations. Unlike block drivers, character drivers may suspend read/write/ioctl/select operations and reply later.

Key responsibilities:
- `cdev_map` maps `/dev/tty` to the process controlling terminal.
- `cdev_open` and `cdev_close` send open/close requests to character drivers.
- `cdev_io` initiates read, write, or ioctl and suspends the process.
- `cdev_select` initiates select monitoring.
- `cdev_cancel` cancels suspended I/O and revokes grants.
- `cdev_reply` dispatches character-driver replies.
- `cdev_clone` handles cloned device opens by replacing the opened vnode with a new PFS-created device node.

Important behavior:
- `/dev/tty` is special: it maps to `fp_tty`, and open/close for the CTTY major is not actually sent to the driver.
- Open logic manages controlling-terminal assignment and `O_NOCTTY`.
- Read/write grants are made with `cpf_grant_magic`; IOCTL grants use `make_ioctl_grant`.
- Suspended character I/O records device endpoint and grant in `fp_cdev`.
- Replies either wake a waiting worker thread or revive the blocked process.
- Some legacy status translations convert `EINTR`/`EAGAIN` around cancellation/nonblocking behavior.

Dependencies:
- Uses `dmap` for major-to-driver mapping.
- Uses `req_newnode` to create cloned device nodes in PFS.
- Calls select reply handlers for `CDEV_SEL1_REPLY` and `CDEV_SEL2_REPLY`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/cdev.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/comm.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/comm.c

`comm.c` provides VFS message transport to filesystem servers, device drivers, and VM, with worker-thread suspension and per-mount request throttling.

Key responsibilities:
- `sendmsg` sends asynchronous requests with VFS transaction IDs.
- `send_work` pushes queued filesystem work when mounts have capacity.
- `fs_cancel` cancels pending requests for a mount.
- `fs_sendmore` drains a mount queue subject to `c_max_reqs` and callback restrictions.
- `drv_sendrec` implements blocking send/receive to block drivers using dmap locks.
- `fs_sendrec` sends filesystem requests, queuing when a filesystem has no request capacity.
- `vm_sendrec` sends request/reply messages to VM.
- `vm_vfs_procctl_handlemem` wraps a VM `VM_PROCCTL` request.
- `queuemsg` appends a worker to a mount request queue.

Important behavior:
- Filesystem request messages are tagged with worker transaction IDs so replies can be routed back.
- Mounts maintain current request count and max concurrency.
- `fs_sendrec` maps filesystem `ERESTART` replies to `EIO`.
- `drv_sendrec` serializes driver requests with `dmap_lock` and records the servicing thread.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/comm.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/const.h -->
# File Research: sources/teaching/minix/minix/servers/vfs/const.h

VFS constants header.

Key definitions:
- Table sizes: `NR_FILPS`, `NR_LOCKS`, `NR_MNTS`, `NR_VNODES`, `NR_WTHREADS`, `NR_SOCKDEVS`.
- System UID/GID constants.
- Process blocked-state constants:
  - none
  - pipe
  - file lock
  - pipe open
  - select
  - character device
  - socket device
- `fp_is_blocked` helper macro.
- `INVALID_THREAD`.
- `SYMLOOP`.
- Label/type-size limits.
- Select operation aliases shared between character and socket devices.
- Compile-time assertion that CDEV and SDEV select constants match.
- `CTTY_ENDPT` for the special `/dev/tty` mapping.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/const.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/coredump.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/coredump.c

`coredump.c` writes ELF core files for dying processes.

Key responsibilities:
- `write_elf_core_file` assembles and writes the ELF core file.
- Builds ELF header and program headers.
- Adds a PT_NOTE segment containing MINIX core metadata and general registers.
- Queries VM for process memory regions and emits each as a PT_LOAD segment.
- Writes segment data by copying from the target process; unreadable pages are represented as zeroes.

Important behavior:
- The first program header is always the NOTE segment.
- Region information comes from `vm_info_region`.
- Register state comes from `sys_getregs`.
- Writes are routed through `read_write` on the destination filp.
- Segment lengths over `LONG_MAX` are truncated.
- Padding follows ELF note alignment requirements.

Dependencies:
- Uses MINIX ELF core structures from `sys/elf_core.h`.
- Relies on global `fp` as the process being dumped.
- Used by `pm_dumpcore` in `misc.c`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/coredump.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/device.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/device.c

`device.c` contains device-type-independent IOCTL helpers.

Key responsibilities:
- `do_ioctl` dispatches an IOCTL on an fd to:
  - `bdev_ioctl` for block devices.
  - `cdev_io(CDEV_IOCTL)` for character devices.
  - `sdev_ioctl` for sockets.
  - `ENOTTY` for other file types.
- `make_ioctl_grant` creates a grant for IOCTL buffer access based on encoded request direction and size.

Important behavior:
- For block-device IOCTLs, the filp records `filp_ioctl_fp` to prevent dangerous descriptor copying deadlocks.
- Grant access flags are derived from `_MINIX_IOCTL_IOR`, `_MINIX_IOCTL_IOW`, `_MINIX_IOCTL_SIZE`, and `_MINIX_IOCTL_SIZE_BIG`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/device.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/dmap.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/dmap.c

`dmap.c` owns the device-major-to-driver mapping table and driver recovery hooks.

Key responsibilities:
- Defines global `dmap[NR_DEVICES]`.
- Initializes mappings and locks with `init_dmap`.
- Handles RS `do_mapdriver` requests.
- Maps boot services through `map_service`.
- Unmaps drivers by endpoint.
- Looks up mappings by major or endpoint.
- Handles driver-up DS events through `dmap_endpt_up`.

Important behavior:
- Only RS may call `do_mapdriver`.
- Driver labels are copied from user space, null-termination checked, and resolved through DS.
- Mapping a service marks its `fproc` as `FP_SRV_PROC`.
- Unmapping a character driver invalidates open character filps for that major.
- Block driver recovery calls `bdev_up`; character driver recovery stops waiting workers and invalidates char filps.
- `CTTY_MAJOR` is mapped specially to `"vfs"` and `CTTY_ENDPT`.

Dependencies:
- Uses DS for label-to-endpoint lookup.
- Uses worker functions for stopping threads waiting on failed drivers.
- Coordinates with socket-driver mapping through `smap_map` and `smap_unmap_by_endpt`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/dmap.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/dmap.h -->
# File Research: sources/teaching/minix/minix/servers/vfs/dmap.h

Header declaring the VFS device mapping table.

Structure fields:
- `dmap_driver`: driver endpoint.
- `dmap_label`: service label.
- `dmap_sel_busy` and `dmap_sel_filp`: select-related state.
- `dmap_servicing`: worker thread currently waiting on the driver.
- `dmap_lock`: per-driver mutex.
- `dmap_recovering`: block-driver recovery state.
- `dmap_seen_tty`: whether the driver has produced controlling TTYs.

Role:
- Shared definition for device lookup, driver locking, recovery, and select coordination.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/dmap.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/exec.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/exec.c

`exec.c` implements the VFS side of `execve`, coordinating path lookup, script handling, ELF loading, dynamic linker setup, stack patching, VM mappings, and close-on-exec.

Key responsibilities:
- `pm_exec` is the main entry point called from PM-postponed work.
- Fetches the user-supplied stack frame before destroying the old image.
- Resolves and opens the executable vnode with execute-permission checks.
- Handles setuid/setgid mode bits.
- Detects scripts with `#!` and patches the stack to invoke the interpreter.
- Detects ELF interpreters and opens the dynamic loader.
- Opens the main program as an fd for dynamic loaders when needed.
- Optionally gives VM an fd and mmap callback for page-backed executable mapping.
- Uses `libexec_load_elf` to load executable images.
- Fills ELF auxiliary vectors for dynamic executables.
- Copies the final stack into the new process and closes `FD_CLOEXEC` descriptors.

Important helpers:
- `get_read_vp` switches the current executable vnode and reads the header.
- `vfs_memmap` asks VM to map file-backed regions through VFS.
- `stack_prepare_elf` fills aux vector entries such as `AT_BASE`, `AT_ENTRY`, `AT_EXECFD`, effective IDs, and page size.
- `patch_stack` rewrites script arguments.
- `insert_arg` inserts or replaces argv entries in the stack image.
- `read_seg` loads file segments through `req_readwrite`.
- `map_header` reads the first executable bytes into an aligned static header buffer.

Important behavior:
- Serializes exec work with VM using `lock_exec`.
- Dynamic loader is placed below the stack with a load offset to help catch null dereferences.
- If a VM fd was created but unused, it is closed on failure/cleanup.
- If image loading succeeds and setuid/setgid is still allowed, effective credentials are changed after loading.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/exec.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/file.h -->
# File Research: sources/teaching/minix/minix/servers/vfs/file.h

Defines the global filp table, VFS’s intermediate layer between per-process file descriptors and vnodes.

`struct filp` fields include:
- Open mode, flags, reference count, vnode pointer, and file position.
- Filp mutex.
- Soft-lock tracking for cases where the current thread already locked the vnode.
- IOCTL owner tracking to avoid descriptor-copy deadlocks.
- Generic select state.
- Pipe/device/socket select-specific state.

Key constants:
- `FILP_CLOSED` marks a filp whose associated device/file is closed or gone.
- `FSF_*` flags track select state and blocked read/write/error operations.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/file.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/filedes.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/filedes.c

`filedes.c` manages file descriptors and filps.

Key responsibilities:
- Initializes filp mutexes.
- Finds free descriptor and filp slots with `get_fd`.
- Looks up descriptors with `get_filp` and `get_filp2`.
- Finds filps by vnode or socket device.
- Invalidates filps by character major, socket driver, or filesystem endpoint.
- Locks and unlocks filps while coordinating vnode locks.
- Closes filps and underlying special devices.
- Implements `do_copyfd` for copying or closing file descriptors across endpoints.

Important behavior:
- `get_fd` reserves neither descriptor nor filp permanently; callers claim them after open succeeds.
- `get_filp2` allows close on `FILP_CLOSED` but rejects other operations with `EIO`.
- Pipe vnodes are always locked for write even for read operations, because pipe reads mutate pipe state.
- `close_filp` handles last-reference cleanup:
  - flushes block-special cache when needed,
  - closes block/character/socket devices,
  - releases pipe waiters,
  - truncates FIFO state on last close,
  - drops vnode references.
- Socket close may suspend only for user `close(2)` and only when nonblocking flags allow it.
- `do_copyfd` requires superuser and contains explicit checks to avoid UDS in-flight fd deadlocks.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/filedes.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/fproc.h -->
# File Research: sources/teaching/minix/minix/servers/vfs/fproc.h

Defines VFS per-process state in `fproc[NR_PROCS]`.

Important fields:
- Process ID and endpoint.
- Root and working directory vnodes.
- File descriptor table and close-on-exec fd set.
- Controlling terminal.
- Blocked-state field plus per-block-type saved state for pipes, pipe open, file locks, character devices, and socket devices.
- Real/effective UID/GID and supplemental groups.
- Process mutex, active worker, pending work function, pending messages, and process name.

Flags:
- `FP_SRV_PROC`
- `FP_REVIVED`
- `FP_SESLDR`
- `FP_PENDING`
- `FP_EXITING`
- `FP_PM_WORK`

Also defines `fproc_light`, a smaller process snapshot for MIB/sysinfo use.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/fproc.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/fs.h -->
# File Research: sources/teaching/minix/minix/servers/vfs/fs.h

Master VFS header included by VFS C files.

Key contents:
- Defines `_SYSTEM`.
- Includes MINIX config, system types, constants, endpoint/DS/RS/call-number headers, libc/system utility headers, and timers.
- Includes VFS internal headers:
  - `const.h`
  - `dmap.h`
  - `proto.h`
  - `threads.h`
  - `glo.h`
  - `type.h`
  - `vmnt.h`
  - `fproc.h`

Role:
- Centralizes global types, constants, prototypes, and global declarations for the VFS server.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/fs.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/gcov.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/gcov.c

`gcov.c` implements VFS support for requesting coverage data from system services.

Key responsibilities:
- `do_gcov_flush` accepts a label and caller buffer.
- Requires superuser.
- Resolves the target service label through DS.
- Rejects `init` as a target.
- Grants the target service write access to the caller buffer.
- For VFS itself, calls `gcov_flush` directly.
- For other services, sends `COMMON_REQ_GCOV_DATA`.
- Revokes the grant before returning.

Important caveat:
- The comment warns this can deadlock the system because it performs a direct call to the target service.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/gcov.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/glo.h -->
# File Research: sources/teaching/minix/minix/servers/vfs/glo.h

Declares VFS global variables and convenience macros.

Important globals:
- Current process pointer `fp`.
- Suspension, lock, revival, sending, and verbosity counters.
- Root device and root filesystem endpoint.
- System clock frequency.
- Incoming message `m_in`.
- Current worker `self`.
- Block-special-file lock.
- Worker thread array.
- Mount label buffer.
- Temporary `err_code`.
- Syscall dispatch vector `call_vec`.

Important macros:
- `who_p`, `who_e`, and `call_nr`.
- `job_m_in`, `job_m_out`, and `job_call_nr`.
- `super_user`.
- `fproc_addr`.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/glo.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/link.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/link.c

`link.c` implements link, unlink, rename, truncate, symlink, and readlink operations.

Key responsibilities:
- `do_link` creates hard links after source lookup, target parent lookup, same-filesystem check, and permissions.
- `do_unlink` handles unlink and rmdir with directory, permission, sticky-bit, and mount-lock checks.
- `do_rename` handles rename with old/new parent lookups, sticky-bit checks, same-filesystem enforcement, and mount-lock upgrade.
- `do_truncate` and `do_ftruncate` validate target, permissions, and size before truncating.
- `truncate_vnode` sends `req_ftrunc` and updates cached vnode size.
- `do_slink` creates symlinks through `req_slink`.
- `rdlink_direct` performs internal readlink-like resolution.
- `do_rdlink` implements user `readlink`.

Important behavior:
- Sticky directory checks compare the target owner against caller effective UID or superuser.
- Hard links and renames across filesystem endpoints return `EXDEV`.
- Truncate avoids issuing a request when regular-file size is unchanged for POSIX timestamp behavior.
- `PATH_RET_SYMLINK` is used where operations must act on symlinks themselves.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/link.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/lock.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/lock.c

`lock.c` implements POSIX advisory byte-range file locks for `fcntl`.

Key responsibilities:
- `lock_op` handles `F_GETLK`, `F_SETLK`, and `F_SETLKW`.
- Copies `struct flock` from user space and validates lock type, file type, and access mode.
- Computes byte ranges from `SEEK_SET`, `SEEK_CUR`, or `SEEK_END`.
- Detects conflicts with existing locks.
- Suspends `F_SETLKW` callers on conflicts.
- Adds, removes, shrinks, or splits lock ranges.
- `lock_revive` revives all processes blocked on file locks when any lock is released.

Important behavior:
- Read locks can coexist with other read locks.
- Locks owned by the same PID do not conflict for set operations.
- Unlocking a middle range may split one lock into two, requiring a free lock slot.
- The wakeup strategy is broad: all blocked lock waiters are revived and will recheck.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/lock.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/lock.h -->
# File Research: sources/teaching/minix/minix/servers/vfs/lock.h

Declares the global advisory file-lock table.

`struct file_lock` fields:
- `lock_type`: `F_RDLCK`, `F_WRLCK`, or unused.
- `lock_pid`: owner PID.
- `lock_vnode`: locked vnode.
- `lock_first` and `lock_last`: byte range.

Role:
- Shared table used by `lock.c` and VFS global state.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/lock.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/main.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/main.c

`main.c` is the VFS server main loop, SEF startup path, worker dispatch hub, PM-message handler, and blocked-process revival coordinator.

Key responsibilities:
- Starts SEF, initializes VFS, and enters the permanent message loop.
- Routes filesystem replies by transaction ID to waiting worker threads.
- Handles PM control messages.
- Handles DS, kernel, and clock notifications.
- Dispatches block, character, and socket driver replies.
- Starts worker threads for normal syscalls.
- Initializes fproc state from PM, subscribes to driver DS events, maps boot services, initializes tables, and mounts PFS plus the root filesystem.

Important components:
- `handle_work` starts workers and handles callbacks from filesystem servers without deadlocking.
- `do_reply` stores filesystem replies into the waiting worker’s sendrec message and wakes it.
- `do_work` dispatches VFS syscalls through `call_vec`.
- Live update callbacks stop/restart worker threads around request-free/protocol-free update states.
- `service_pm_postponed` handles blocking PM requests such as exec, exit, dumpcore, and unpause in worker context.
- `service_pm` handles immediate PM requests and schedules postponed ones.
- `unblock` reconstructs blocked pipe or file-lock requests for retry.
- `reply` and `replycode` send replies to user processes.

Startup behavior:
- Receives process table initialization messages from PM.
- Subscribes to DS driver events matching block/character driver patterns.
- Initializes workers, global locks, dmap, smap, fproc locks, vnodes, vmnts, select, and filps.
- Starts a worker to mount PFS and the boot ramdisk root filesystem.

Concurrency model:
- The main thread does not block on work that can suspend.
- Worker threads carry process context through `fp`.
- Filesystem callbacks from service processes use spare-thread handling and `VMNT_CALLBACK` flags.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/misc.c -->
# File Research: sources/teaching/minix/minix/servers/vfs/misc.c

`misc.c` contains assorted VFS syscalls and PM-side process lifecycle helpers.

Key responsibilities:
- `do_getsysinfo` exposes selected VFS tables to superuser callers.
- `do_fcntl` handles descriptor duplication, close-on-exec flags, status flags, advisory locks, file-space freeing, no-sigpipe flags, and cache flushing.
- `do_sync` syncs mounted filesystems.
- `do_fsync` syncs filesystems associated with a file descriptor’s device.
- `dupvm` duplicates a process fd into VM for mmap/peek support.
- `do_vm_call` handles VM-to-VFS fd lookup, fd close, and fd I/O requests.
- `pm_reboot` syncs, frees process resources, unmounts filesystems, and replies to PM.
- `pm_fork` clones fproc state and increments filp/vnode references.
- `pm_exit` and `free_proc` release descriptors, directories, driver mappings, mounted filesystem state, and controlling terminals.
- `pm_setgid`, `pm_setgroups`, `pm_setuid`, and `pm_setsid` update VFS-side credentials/session state.
- `do_svrctl` supports VFS parameter get/set and diagnostics.
- `pm_dumpcore` creates `core.<pid>` and writes an ELF core file.
- `ds_event` processes DS driver-up events for block, character, and socket drivers.
- `panic_hook` prints VFS thread stack traces.
- `do_getrusage` is an obsolete stub returning `OK`.

Important behavior:
- `do_fcntl(F_FLUSH_FS_CACHE)` requires superuser and flushes either block-device or hosting-filesystem cache.
- `do_vm_call` replies asynchronously with `VM_VFS_REPLY` and then returns `SUSPEND` so no normal reply is sent.
- Reboot performs multiple sync/unmount/free passes, first avoiding active filesystem services and later forcing unmounts.
- `free_proc` unpauses blocked processes, closes fds, releases root/working directories, unmaps dead drivers, invalidates filesystem state, and revokes controlling TTYs when a session leader exits.
- `pm_dumpcore` unblocks the process first, writes the core, then frees the process as exiting.
<!-- END FILE RESEARCH: sources/teaching/minix/minix/servers/vfs/misc.c -->