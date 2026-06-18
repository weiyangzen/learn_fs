# subset-b-005980 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ethtool_netlink.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ethtool_netlink.h

This UAPI header provides hand-maintained ethtool netlink constants that complement the generated ethtool netlink command and attribute header. It is a user/kernel ABI contract for cable-test notifications, Time Domain Reflectometry result nesting, and standardized Ethernet/PHY statistics group IDs.

Important exports are `ETHTOOL_FLAG_ALL`, cable result codes such as `ETHTOOL_A_CABLE_RESULT_CODE_OK`, `OPEN`, `SAME_SHORT`, `CROSS_SHORT`, `IMPEDANCE_MISMATCH`, `NOISE`, and `RESOLUTION_NOT_POSSIBLE`, pair IDs `ETHTOOL_A_CABLE_PAIR_A` through `D`, source IDs `ETHTOOL_A_CABLE_INF_SRC_TDR` and `ALCD`, and notification statuses `STARTED` and `COMPLETED`. TDR payload attributes are split into nested amplitude, pulse, step, and TDR nest enums. Statistics exports include `ETHTOOL_STATS_ETH_PHY`, `ETH_MAC`, `ETH_CTRL`, `RMON`, and `PHY`, plus individual IEEE 802.3 and RMON counter attribute IDs.

Control flow is encoded as generic-netlink message layout rather than functions: ethtool emits notifications and replies whose nested attributes use these numeric IDs, while userspace decoders walk the nested netlink attributes according to the max/count constants. The header itself stores no state; operational state is in net devices, PHY drivers, ethtool netlink handlers, cable-test work, and counter providers. Persistence is ABI persistence: assigned numeric values and append-only enum ordering must remain stable for existing `ethtool` and monitoring binaries.

Dependencies include `linux/ethtool.h` for base flags and `linux/ethtool_netlink_generated.h` for the generated family command/attribute surface. Integration points are the kernel ethtool netlink family, PHY cable diagnostics, ALCD/TDR hardware support, and userspace tools parsing cable-test notifications and grouped statistics.

Risks are ABI drift between the hand-written and generated headers, incorrect nested attribute type assumptions, counter name/value mismatches with IEEE clauses, and breaking older tools by reusing or renumbering enum slots. Test signals include UAPI header selftests, `tools/net/ynl` schema checks where applicable, ethtool netlink cable-test decode tests, statistics dump tests on drivers with PHY/MAC/RMON counters, and build checks for userspace inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ethtool_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ethtool_netlink_generated.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ethtool_netlink_generated.h

This generated UAPI header is the main ethtool generic-netlink ABI description emitted from the kernel netlink YAML specification. It defines ethtool command IDs, multicast group names, top-level and nested attribute IDs, compact bitset layout pieces, string-set/statistic request formats, link settings, pause/coalesce/ring/channel/FEC/MM/PSE/PLCA/module/PHY controls, and notification event attributes.

Important APIs are enum namespaces rather than functions. The file exports ethtool command IDs such as `ETHTOOL_MSG_*_GET`, `*_SET`, `*_NTF`, and `*_ACT`, header attribute IDs under `ETHTOOL_A_HEADER_*`, bitset/string set formats, and per-operation attributes for link modes, link info, WOL, debug, features, priv flags, rings, channels, coalesce, pause, EEE, timestamping, cable tests, tunnel info, FEC, module EEPROM, PSE, MM, PLCA, RSS, PHY stats, and module firmware flashing. It also defines multicast group strings such as `ETHTOOL_MCGRP_MONITOR_NAME`.

Control flow follows generic netlink: userspace sends a command with an `ETHTOOL_A_HEADER_*` selector and operation-specific nested attributes; kernel validates policy, queries or mutates the selected `net_device`/PHY/driver state, and returns attributes or monitor notifications. State is not stored in the header. Persistent behavior is ABI numbering and generated schema compatibility; runtime state lives in device drivers, ethtool ops, link mode bitmaps, PHY state machines, module EEPROM/firmware, and netlink subscription queues.

Dependencies are the YNL generation pipeline, `Documentation/netlink/specs/ethtool.yaml` or equivalent source spec, generic-netlink attribute encoding, and the hand-maintained `ethtool_netlink.h` companion for cable-test/statistic groups. Integration points include `tools/net/ynl`, `iproute2`/`ethtool` userspace, kernel ethtool netlink handlers, and driver `ethtool_ops`.

Risks are typical generated-UAPI risks: editing the file by hand, desynchronizing generated constants from the YAML spec, renumbering attributes, failing to append new enum values before `__*_CNT`, or accepting userspace payloads whose nested layout does not match policy. Test signals include regenerating with `ynl-regen`, comparing generated output, building exported headers, netlink policy validation tests, ethtool userspace command coverage, and monitor notification decode tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ethtool_netlink_generated.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/eventfd.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/eventfd.h

This small UAPI header defines flags for the `eventfd` and `eventfd2` syscalls. It is the public contract for creating a counter-backed file descriptor used for userspace/kernel notifications and lightweight wakeups.

Exports are `EFD_SEMAPHORE`, `EFD_CLOEXEC`, and `EFD_NONBLOCK`. `EFD_CLOEXEC` and `EFD_NONBLOCK` deliberately alias the generic `O_CLOEXEC` and `O_NONBLOCK` definitions from `linux/fcntl.h`, keeping file descriptor creation semantics aligned with other fd-producing syscalls.

Control flow is syscall driven: userspace calls `eventfd2(initval, flags)`, the kernel creates an anonymous fd with a 64-bit counter, writes add to the counter and wake waiters, reads either drain the counter or decrement by one in semaphore mode, and poll/epoll observe readability/writability. State is the in-kernel counter and wait queue tied to the fd; no state exists in the header and no persistent on-disk state is involved.

Dependencies are `linux/fcntl.h` and the eventfd implementation in the kernel core. Integration points include epoll, io_uring, AIO, KVM irqfds, VFIO, FPGA DFL interrupt eventfds, and many driver notification APIs.

Risks are flag-value ABI mismatches with `O_*` values, userspace assuming semaphore and counter modes behave identically, counter overflow blocking writes, and close-on-exec omissions leaking synchronization fds across exec. Test signals include eventfd syscall tests for blocking/nonblocking reads and writes, `EFD_SEMAPHORE` decrement behavior, `EFD_CLOEXEC` inheritance tests, and poll/epoll readiness checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/eventfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/eventpoll.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/eventpoll.h

This UAPI header defines the epoll userspace ABI: creation flags, control operation codes, event mask bits, the packed `struct epoll_event`, and busy-poll parameter ioctls. It is consumed directly by libc, applications, and kernel compatibility layers.

Important exports include `EPOLL_CLOEXEC`, `EPOLL_CTL_ADD`, `EPOLL_CTL_DEL`, `EPOLL_CTL_MOD`, readiness bits `EPOLLIN`, `EPOLLPRI`, `EPOLLOUT`, `EPOLLERR`, `EPOLLHUP`, `EPOLLRDHUP`, edge/one-shot flags `EPOLLET` and `EPOLLONESHOT`, power-management flag `EPOLLWAKEUP`, exclusive wakeup flag `EPOLLEXCLUSIVE`, and internal recursion marker `EPOLL_URING_WAKE`. `struct epoll_event` carries `__poll_t events` and opaque `__u64 data`; `struct epoll_params` is used with `EPIOCSPARAMS` and `EPIOCGPARAMS`.

Control flow is the standard epoll lifecycle: create an epoll fd, add/modify/delete target fds with `epoll_ctl`, then block or poll with `epoll_wait` variants. Kernel state consists of interest lists, ready lists, target file callbacks, busy-poll settings, and wakeup bookkeeping. Persistence is fd lifetime only; closing the epoll fd drops all registrations.

Dependencies include `linux/fcntl.h` for `O_CLOEXEC`, `linux/types.h` for `__poll_t`, and architecture-specific packing behavior. Integration points are virtually all pollable file types, io_uring poll paths, network busy-poll support, suspend blockers, and userspace event loops.

Risks include structure packing mismatches on x86-64/compat, incorrect use of edge-triggered or one-shot modes causing missed wakeups, `EPOLLEXCLUSIVE` semantics surprises, CAP requirements for `EPOLLWAKEUP`, and recursion issues involving io_uring wakeups. Test signals include libc header compatibility, epoll ctl/wait selftests, 32-bit compat ABI tests, busy-poll ioctl validation, and race tests for close, dup, fork, and nested epoll.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/eventpoll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/exfat.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/exfat.h

This UAPI header defines the exFAT-specific filesystem shutdown ioctl. It is a narrow ABI for forcing an exFAT filesystem into a shutdown/down state for testing, administration, and error-handling workflows.

The main export is `EXFAT_IOC_SHUTDOWN`, encoded as `_IOR('X', 125, __u32)`, plus shutdown mode flags `EXFAT_GOING_DOWN_DEFAULT`, `EXFAT_GOING_DOWN_FULLSYNC`, and `EXFAT_GOING_DOWN_NOSYNC`.

Control flow is ioctl-based: privileged or otherwise authorized userspace passes a shutdown flag to an open exFAT file or mount-related fd; the filesystem implementation interprets the mode, optionally syncs metadata/data, and transitions the superblock/mount into a state where further operations fail or are restricted. State and persistence live in the exFAT superblock and mounted filesystem structures, not this header. Disk persistence depends on the selected sync mode.

Dependencies include `linux/types.h`, `linux/ioctl.h`, and the exFAT filesystem driver. Integration points include generic shutdown semantics shared with `FS_IOC_SHUTDOWN`/ext4-style flag values, mount lifecycle handling, and filesystem error injection tests.

Risks are destructive administrative misuse, incomplete sync semantics causing data loss, and ABI collision with other `'X',125` shutdown ioctls. Test signals include exFAT ioctl tests for each flag, post-shutdown operation failure checks, remount/fsck behavior, and sync/no-sync persistence validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/exfat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ext4.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ext4.h

This UAPI header defines ext4-specific ioctl commands, structures, and flags for version fields, online resize, extent movement, delayed allocation flushing, extent-status cache inspection, checkpointing, filesystem UUID operations, shutdown, and tunable superblock parameters.

Important exports include `EXT4_IOC_GETVERSION`, `SETVERSION`, `GETRSVSZ`, `SETRSVSZ`, `GROUP_EXTEND`, `GROUP_ADD`, `MIGRATE`, `ALLOC_DA_BLKS`, `MOVE_EXT`, `RESIZE_FS`, `SWAP_BOOT`, `PRECACHE_EXTENTS`, `CLEAR_ES_CACHE`, `GETSTATE`, `GET_ES_CACHE`, `CHECKPOINT`, `GETFSUUID`, `SETFSUUID`, `GET_TUNE_SB_PARAM`, `SET_TUNE_SB_PARAM`, and `EXT4_IOC_SHUTDOWN`, with 32-bit compat forms for older integer-sized commands. Key types are `struct fsuuid`, `struct move_extent`, `struct ext4_new_group_input`, and `struct ext4_tune_sb_params`; key flags include exposed inode state bits, checkpoint flags, shutdown flags, tune field masks, and `EXT4_FIEMAP_EXTENT_HOLE`.

Control flow is ioctl dispatch from an fd on an ext4 filesystem into ext4-specific handlers. Some commands query state, some update persistent superblock or inode metadata, and others initiate heavyweight operations such as online resize, extent migration, journal checkpointing, or shutdown. Runtime state includes inode flags, extent status cache, journal state, superblock tunables, and online-resize metadata. Persistent behavior applies to UUIDs, superblock tunables, version fields, and resized filesystem layout.

Dependencies include `linux/fiemap.h`, `linux/fs.h`, `linux/ioctl.h`, and `linux/types.h`. Integration points are e2fsprogs/chattr/lsattr/debug tooling, fscrypt ioctl number reservations, fiemap extent reporting, VFS ioctl routing, journal checkpoint logic, and block-layer discard/zeroout behavior during checkpoints.

Risks include destructive or privileged operations, compat-ABI struct-size differences, reserved ioctl-number collisions with fscrypt, inconsistent behavior if commands run during mount shutdown, and persistent corruption if online resize or tune operations are mishandled. Test signals include ext4 ioctl xfstests, 32-bit compat tests, online resize tests, journal checkpoint/discard tests, move-extent correctness tests, UUID/tune persistence checks, and fiemap hole flag validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ext4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/f2fs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/f2fs.h

This UAPI header exposes F2FS-specific ioctl constants and small ABI structures. It covers atomic/volatile writes, garbage collection, range movement, defragmentation, flush and shutdown, feature queries, compression controls, pinned files, and filesystem labels.

Important exports include `F2FS_IOCTL_MAGIC`, atomic write commands `F2FS_IOC_START_ATOMIC_WRITE`, `COMMIT_ATOMIC_WRITE`, `ABORT_ATOMIC_WRITE`, volatile write commands, `F2FS_IOC_GARBAGE_COLLECT`, `WRITE_CHECKPOINT`, `DEFRAGMENT`, `MOVE_RANGE`, `FLUSH_DEVICE`, `GET_FEATURES`, `GET_PIN_FILE`, `SET_PIN_FILE`, `PRECACHE_EXTENTS`, compression commands, and `F2FS_IOC_SHUTDOWN`. Key structures include `struct f2fs_gc_range`, `struct f2fs_defragment`, `struct f2fs_move_range`, and `struct f2fs_flush_device`.

Control flow is ioctl driven on files or directories in an F2FS mount. Commands mutate per-inode atomic/volatile write state, trigger segment cleaning, flush checkpoint/device state, manipulate extents, or query features. State lives in the mounted F2FS superblock, segment cleaner, checkpoint pack, inode flags, compression metadata, and pinned-file accounting. Persistence varies: feature and label state is persistent, compression and pinning are inode metadata, and GC/flush actions affect on-disk placement.

Dependencies are `linux/types.h`, `linux/ioctl.h`, and the F2FS filesystem implementation. Integration points include Android/storage tooling, fsck.f2fs, generic VFS ioctl routing, block discard/flush paths, compression infrastructure, and xfstests.

Risks include data-loss semantics around atomic/volatile write abort/commit, GC latency and wear behavior, alignment and range validation bugs, shutdown mode misuse, and ABI compatibility when adding ioctl structures. Test signals include F2FS xfstests for atomic writes, GC, defrag, compression, shutdown, feature queries, 32-bit compat ioctls, and fsck/mount persistence checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/f2fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fadvise.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/fadvise.h

This header defines the Linux `posix_fadvise` advice constants shared by userspace and the kernel. It gives applications a way to describe expected file access patterns to the page cache and filesystem readahead logic.

Exports are `POSIX_FADV_NORMAL`, `POSIX_FADV_RANDOM`, `POSIX_FADV_SEQUENTIAL`, `POSIX_FADV_WILLNEED`, `POSIX_FADV_DONTNEED`, and `POSIX_FADV_NOREUSE`, with architecture-specific value handling where required by the UAPI.

Control flow is syscall driven: userspace calls `posix_fadvise`/`fadvise64` with an fd, offset, length, and advice; kernel/VFS applies cache, readahead, or eviction hints without changing file contents. State is transient page-cache/readahead state and file access heuristics. There is no persistent storage behavior, though `DONTNEED` may cause dirty pages to be written before cache eviction.

Dependencies are minimal and architecture UAPI glue supplies syscall ABI details. Integration points include libc wrappers, VFS page cache, readahead code, filesystem address-space operations, and performance-sensitive applications such as databases and backup tools.

Risks include applications treating hints as guarantees, performance regressions from inappropriate advice, arch value mismatches, and semantic changes to `NOREUSE`. Test signals include syscall ABI tests, cache/readahead behavior benchmarks, cross-arch header checks, and workloads validating that advice does not corrupt data or bypass required writeback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fadvise.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/falloc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/falloc.h

This UAPI header defines `fallocate(2)` mode flags. It is the public contract for space preallocation, hole punching, range collapse/insert, zeroing, unsharing, fixed-range allocation, and write-zeroes behavior.

Important exports include `FALLOC_FL_KEEP_SIZE`, `PUNCH_HOLE`, `NO_HIDE_STALE`, `COLLAPSE_RANGE`, `ZERO_RANGE`, `INSERT_RANGE`, `UNSHARE_RANGE`, and newer flags such as `FALLOC_FL_ALLOCATE_RANGE` and `FALLOC_FL_WRITE_ZEROES`. The header also documents valid flag combinations and mutually exclusive operations.

Control flow is syscall driven: userspace invokes `fallocate(fd, mode, offset, len)`, VFS validates generic constraints, and the filesystem implements the chosen operation through its fallocate method. State changes live in file size, extent maps, unwritten/allocated extent metadata, copy-on-write sharing state, and block allocation. Persistence is filesystem metadata and possibly zeroed data ranges after journal/transaction completion.

Dependencies are VFS and individual filesystem implementations such as ext4, XFS, Btrfs, F2FS, and network filesystems. Integration points include database preallocation, sparse-file tools, VM image management, reflink/COW unsharing, and block discard/zeroing support.

Risks include stale-data exposure when zero/no-hide semantics are wrong, incompatible flag combinations, alignment restrictions for collapse/insert, quota/enospc accounting bugs, and network filesystem semantic gaps. Test signals include xfstests fallocate groups, sparse-file hole maps via fiemap, fsck after crash tests, reflink unshare tests, and data-zeroing validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/falloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fanotify.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/fanotify.h

This UAPI header defines fanotify events, initialization flags, mark flags, event metadata records, permission response structures, and helper macros. It is the ABI for filesystem notification and permission mediation through `fanotify_init`, `fanotify_mark`, reads from fanotify fds, and writes of permission responses.

Important exports include event masks `FAN_ACCESS`, `MODIFY`, `ATTRIB`, close/open/move/create/delete events, permission events `FAN_OPEN_PERM`, `FAN_ACCESS_PERM`, `FAN_OPEN_EXEC_PERM`, filesystem/mount events, `FAN_FS_ERROR`, `FAN_RENAME`, and `FAN_PRE_ACCESS`. Init flags cover classes, queue/mark limits, audit, pidfd/TID/FID/name/target/mount reporting, and fd-error reporting. Mark flags cover add/remove/flush, inode/mount/filesystem/mount-namespace scopes, ignore masks, evictable marks, and child events. Key types are `struct fanotify_event_metadata`, info headers and records for FID, pidfd, error, range, mount, plus `struct fanotify_response` and response info.

Control flow is event-queue based: userspace creates a fanotify group, installs marks, reads variable-length metadata plus optional info records, optionally opens reported fds or decodes file handles, and writes allow/deny responses for permission events. Kernel state includes notification groups, marks, ignored masks, event queues, permission waiters, and audit data. Persistence is fd lifetime and marks; no on-disk state is created.

Dependencies include `linux/types.h`, VFS path/file-handle logic, fsnotify core, audit, pidfd support, mount IDs, and filesystem file-handle support for FID modes. Integration points include antivirus/scanners, container monitors, backup/indexing tools, security policy daemons, and filesystem error reporting.

Risks include permission-event deadlocks, queue overflow, variable-length record parsing bugs, fd lifetime leaks, incompatible report flag combinations, races with rename/delete/mount changes, and security bypasses from incorrect mark scope. Test signals include fanotify selftests, permission response tests, overflow tests, FID/name/rename record parsing, pidfd/error/range/mount info checks, audit response tests, and cross-filesystem file-handle coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fanotify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fb.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/fb.h

This header defines the legacy Linux framebuffer userspace ABI. It exposes framebuffer ioctls, fixed and variable screen information, color maps, console-to-framebuffer mapping, vblank status, drawing helper structures, hardware cursor structures, visual/type/acceleration constants, blanking modes, and backlight constants.

Important exports include ioctls `FBIOGET_VSCREENINFO`, `FBIOPUT_VSCREENINFO`, `FBIOGET_FSCREENINFO`, `FBIOGETCMAP`, `FBIOPUTCMAP`, `FBIOPAN_DISPLAY`, `FBIO_CURSOR`, `FBIOGET_CON2FBMAP`, `FBIOPUT_CON2FBMAP`, `FBIOBLANK`, `FBIOGET_VBLANK`, and `FBIO_WAITFORVSYNC`. Key structures are `struct fb_fix_screeninfo`, `fb_var_screeninfo`, `fb_bitfield`, `fb_cmap`, `fb_con2fbmap`, `fb_vblank`, `fb_copyarea`, `fb_fillrect`, `fb_image`, and `fb_cursor`.

Control flow is character-device ioctl and mmap based: applications open `/dev/fbN`, query fixed and variable mode state, set modes/panning/blanking/colormaps/cursors, optionally wait for vblank, and mmap framebuffer memory for drawing. Runtime state lives in fbdev driver mode objects, hardware registers, console binding, mmapped VRAM, colormaps, and cursor state. Persistence is hardware/display state and fbdev driver lifetime; some settings may persist until mode reset or close but are not durable storage.

Dependencies include `linux/types.h`, `linux/i2c.h`, `linux/vesa.h`, fbdev core, console subsystem, and device-specific framebuffer drivers. Integration points include boot splash, simple graphics, embedded systems, DRM fbdev emulation, and old userspace graphics stacks.

Risks include pointer-bearing UAPI structs (`fb_cmap`, `fb_image`, `fb_cursor`) on compat ABIs, physical-address exposure through fixed info, stale or driver-specific acceleration constants, mode-setting races with console/DRM, and memory corruption if mmap dimensions are mishandled. Test signals include fbdev ioctl tests, 32-bit compat tests, mode set/pan/vblank validation, colormap and cursor rendering checks, mmap bounds tests, and DRM-fbdev emulation coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fcntl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/fcntl.h

This UAPI header layers Linux-specific `fcntl` commands and `*at` syscall flags on top of architecture `asm/fcntl.h`. It defines leases, dnotify, fd duplication queries, pipe sizing, memfd seals, write lifetime hints, delegations, special dirfd constants, pidfs/nsfs root constants, and path-operation flags.

Important exports include `F_SETLEASE`, `F_GETLEASE`, `F_NOTIFY`, `F_DUPFD_QUERY`, `F_CREATED_QUERY`, `F_DUPFD_CLOEXEC`, `F_SETPIPE_SZ`, `F_GETPIPE_SZ`, `F_ADD_SEALS`, `F_GET_SEALS`, seal flags `F_SEAL_*`, write lifetime hint commands and `RWH_WRITE_LIFE_*`, delegation commands and `struct delegation`, dnotify `DN_*` masks, `AT_FDCWD`, `PIDFD_SELF_THREAD`, `PIDFD_SELF_THREAD_GROUP`, `FD_PIDFS_ROOT`, `FD_NSFS_ROOT`, `FD_INVALID`, generic `AT_*` flags, rename/access/unlink/handle flags, and `AT_EXECVE_CHECK`.

Control flow is syscall argument interpretation: `fcntl` dispatches commands against an fd, while openat/statx/unlinkat/renameat2/name_to_handle_at/execveat-style syscalls interpret `AT_*` flags against dirfd and path arguments. State includes file locks/leases, dnotify registrations, pipe buffer sizes, inode or file write-hint metadata, memfd seal masks, and filesystem namespace resolution. Persistence varies: seals persist for memfd lifetime, write hints may live on inode or open file, and path flags affect only one syscall.

Dependencies include `asm/fcntl.h`, `linux/openat2.h`, `linux/types.h`, VFS lock/lease/seal code, pipe implementation, pidfs/nsfs, and path resolution. Integration points include libc, coreutils, memfd users, container runtimes, pidfd-aware tools, NFS/delegation users, and statx/openat2 security patterns.

Risks include overlapping per-syscall flag values, fd leaks when CLOEXEC is omitted, seal semantics mistakes that allow writes/exec changes after sealing, ambiguous PID/thread special fd constants, and ABI collisions with architecture-specific `fcntl` bases. Test signals include fcntl syscall selftests, memfd seal tests, pipe sizing tests, path resolution flag tests, pidfd special constant tests, delegation/lease tests, and cross-architecture header checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fcntl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fd.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/fd.h

This header defines the legacy floppy disk userspace ABI for geometry, formatting, error thresholds, drive parameters, drive/FDC status, write-error logging, raw controller commands, and eject/reset operations.

Important exports include `struct floppy_struct`, `struct format_descr`, `struct floppy_max_errors`, `floppy_drive_name`, `struct floppy_drive_params`, `struct floppy_drive_struct`, `enum reset_mode`, `struct floppy_fdc_state`, `struct floppy_write_errors`, and `struct floppy_raw_cmd`. Ioctls include `FDCLRPRM`, `FDSETPRM`, `FDDEFPRM`, `FDGETPRM`, `FDMSGON`, `FDMSGOFF`, format commands `FDFMTBEG/TRK/END`, `FDFLUSH`, `FDSETMAXERRS`, `FDGETMAXERRS`, `FDGETDRVTYP`, `FDSETDRVPRM`, `FDGETDRVPRM`, `FDGETDRVSTAT`, `FDPOLLDRVSTAT`, `FDRESET`, `FDGETFDCSTAT`, `FDWERRORCLR`, `FDWERRORGET`, `FDRAWCMD`, `FDTWADDLE`, and `FDEJECT`.

Control flow is device ioctl based on `/dev/fd*`: userspace configures media geometry, optionally formats tracks, queries drive/controller state, sends raw FDC commands, or resets/ejects media. State lives in the floppy driver, drive motor and head position, cached geometry, media-change generation, controller registers, DMA buffers, and write-error accounting. Persistent behavior is physical media formatting and written data; most parameters are driver runtime state.

Dependencies include `linux/ioctl.h`, `linux/compiler.h`, the floppy block driver, FDC hardware, DMA/IRQ plumbing, and architecture I/O port access. Integration points are fdutils, old installers/recovery tools, and block-device stack compatibility.

Risks include pointer fields and chained raw commands in UAPI structs, privilege requirements for destructive commands, stale media-change detection, timing-sensitive hardware behavior, 32-bit compat layout problems, and the potential for raw commands to wedge controllers. Test signals include floppy driver ioctl tests where hardware/emulation exists, QEMU floppy tests, raw-command validation, format/readback tests, media-change polling tests, and compile/compat layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fdreg.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/fdreg.h

This UAPI header provides low-level floppy disk controller register offsets, command bits, status bits, and controller result codes. It is used by floppy driver code and low-level diagnostic utilities that need symbolic names for FDC programming.

Important exports include register offsets such as `FD_SRA`, `FD_SRB`, `FD_DOR`, `FD_TDR`, `FD_DSR`, `FD_STATUS`, `FD_DATA`, `FD_DIR`, `FD_DCR`, digital output bits like motor and DMA/IRQ enable masks, main status bits, command opcodes for read/write/format/seek/recalibrate/sense/configure, and status register result bits for abnormal termination, write protect, no data, CRC, missing address marks, and seek/equipment errors.

Control flow is hardware-protocol oriented: the floppy driver writes commands and parameters to the data register, watches main/status registers, waits for IRQ/DMA completion, then reads result bytes and updates drive state. The header has no state itself; state is in the physical FDC, drive motors, media, IRQ/DMA engine, and driver bookkeeping.

Dependencies are the IBM PC-compatible floppy controller programming model and the Linux floppy driver. Integration points include `fd.h` raw commands, architecture I/O port helpers, and legacy hardware emulators.

Risks are incorrect bit definitions causing controller hangs, emulator/hardware variation, command/result byte ordering mistakes, and accidental exposure of hardware-level controls to untrusted users. Test signals include floppy hardware or QEMU regression tests, command/status decode tests, raw command ioctl coverage, and compile checks for driver constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fdreg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fib_rules.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/fib_rules.h

This header defines the rtnetlink ABI for policy routing/FIB rules. It describes rule messages, rule actions, flags, and nested attributes used to create, inspect, and delete routing rules.

Important exports include `struct fib_rule_hdr`, actions such as `FR_ACT_TO_TBL`, `FR_ACT_GOTO`, `FR_ACT_NOP`, `FR_ACT_BLACKHOLE`, `FR_ACT_UNREACHABLE`, and `FR_ACT_PROHIBIT`, flags such as `FIB_RULE_PERMANENT`, `FIB_RULE_INVERT`, `FIB_RULE_UNRESOLVED`, and attribute IDs `FRA_DST`, `FRA_SRC`, `FRA_IIFNAME`, `FRA_GOTO`, `FRA_PRIORITY`, `FRA_FWMARK`, `FRA_FLOW`, `FRA_TUN_ID`, `FRA_SUPPRESS_IFGROUP`, `FRA_SUPPRESS_PREFIXLEN`, `FRA_TABLE`, `FRA_FWMASK`, `FRA_OIFNAME`, `FRA_PAD`, `FRA_L3MDEV`, `FRA_UID_RANGE`, `FRA_PROTOCOL`, `FRA_IP_PROTO`, `FRA_SPORT_RANGE`, `FRA_DPORT_RANGE`, and `FRA_DSCP`.

Control flow is rtnetlink based: userspace sends `RTM_NEWRULE`, `RTM_DELRULE`, or `RTM_GETRULE`; kernel validates `fib_rule_hdr` plus attributes, inserts/deletes rules in priority order, and lookup code evaluates rules during route resolution. State is persistent in the running network namespace until deleted or namespace teardown; it is not on disk unless userspace network configuration persists it externally.

Dependencies include rtnetlink, route tables, network namespaces, l3mdev/VRF, mark/UID/protocol/port selectors, and address-family-specific FIB implementations. Integration points are `ip rule`, systemd-networkd, NetworkManager, container networking, VRFs, policy routing, and firewall marking.

Risks include rule priority conflicts, unsupported selector combinations, goto loops/unresolved references, namespace-specific behavior, and ABI extension mistakes in `FRA_*` numbering. Test signals include rtnetlink policy-rule selftests, `ip rule` roundtrip tests, route lookup tests with marks/ports/UID ranges/VRF, namespace isolation tests, and netlink attribute fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fib_rules.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fiemap.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/fiemap.h

This UAPI header defines the `FS_IOC_FIEMAP` data structures and flags used to report logical-to-physical file extent mappings. It is a filesystem-independent ABI for sparse-file inspection, backup tools, defragmenters, and diagnostics.

Important exports are `struct fiemap_extent`, `struct fiemap`, `FIEMAP_MAX_OFFSET`, request flags `FIEMAP_FLAG_SYNC`, `FIEMAP_FLAG_XATTR`, `FIEMAP_FLAG_CACHE`, and extent flags such as `FIEMAP_EXTENT_LAST`, `UNKNOWN`, `DELALLOC`, `ENCODED`, `DATA_ENCRYPTED`, `NOT_ALIGNED`, `DATA_INLINE`, `DATA_TAIL`, `UNWRITTEN`, `MERGED`, and `SHARED`.

Control flow is ioctl based: userspace fills `struct fiemap` with a start, length, flags, and extent array capacity; VFS/filesystem maps extents, writes `fm_mapped_extents`, possibly updates `fm_flags`, and fills extent records until capacity or end. State is a snapshot of filesystem extent metadata and delayed allocation/writeback state. Persistence is the underlying file layout, not the ioctl response itself.

Dependencies include `linux/types.h`, generic `FS_IOC_FIEMAP` in `fs.h`, and filesystem extent mapping implementations. Integration points include `filefrag`, backup/deduplication tools, ext4/XFS/Btrfs/F2FS, reflink detection through `SHARED`, and xattr tree mapping.

Risks include races with concurrent writes/truncates, misreporting delayed/unwritten/shared/encoded extents, alignment assumptions, and exposing physical block layout where permissions are insufficient. Test signals include xfstests fiemap coverage, sparse/reflink/unwritten extent tests, concurrent modification tests, encrypted/compressed file behavior, and userspace `filefrag` comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fiemap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/filter.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/filter.h

This UAPI header defines classic Linux socket filter structures and macros. It is the userspace ABI for attaching classic BPF programs via `SO_ATTACH_FILTER` and related socket/filter interfaces.

Important exports include `BPF_MAJOR_VERSION`, `BPF_MINOR_VERSION`, `struct sock_filter`, `struct sock_fprog`, `BPF_RVAL`, `BPF_A`, misc op macros `BPF_MISCOP`, `BPF_TAX`, `BPF_TXA`, initializer macros `BPF_STMT` and `BPF_JUMP`, `BPF_MEMWORDS`, ancillary data offsets `SKF_AD_*`, and negative offset spaces `SKF_NET_OFF`/`SKF_LL_OFF`.

Control flow is attach-and-evaluate: userspace provides an array of `sock_filter` instructions; kernel validates/translates them, attaches the filter to a socket or packet path, and runs it on packets to return accept length or reject. State is attached to the socket or filter object; scratch memory is per evaluation. There is no persistence beyond fd/filter lifetime.

Dependencies include `linux/compiler.h`, `linux/types.h`, `linux/bpf_common.h`, socket options, packet capture paths, and cBPF/eBPF translation/JIT infrastructure. Integration points are tcpdump/libpcap, seccomp’s related BPF heritage, socket filters, packet sockets, and network receive paths.

Risks include verifier gaps, incorrect ancillary offset handling, signed/negative offset mistakes, JIT/interpreter divergence, and ABI mismatch with BSD-compatible filter definitions. Test signals include classic BPF selftests, libpcap/tcpdump attach tests, JIT vs interpreter equivalence, malformed program rejection, and ancillary data filter tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/firewire-cdev.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/firewire-cdev.h

This large UAPI header defines the FireWire character-device ABI. It covers asynchronous transaction events, local address allocation, bus reset reporting, isochronous transmit/receive contexts, PHY packet send/receive, config ROM descriptors, cycle timers, and isochronous resource allocation.

Important exports include event types `FW_CDEV_EVENT_BUS_RESET`, `RESPONSE`, `REQUEST`, `ISO_INTERRUPT`, ISO resource events, request/response v2/v3 timestamped variants, and PHY packet events. Key event types include `fw_cdev_event_common`, `bus_reset`, `response`, `response2`, `request`, `request2`, `request3`, `iso_interrupt`, `iso_interrupt_mc`, `iso_resource`, `phy_packet`, and `phy_packet2`. Operation structs include `fw_cdev_get_info`, `send_request`, `send_response`, `allocate`, `deallocate`, `initiate_bus_reset`, descriptor add/remove, ISO context setup/queue/start/stop/flush, cycle timer reads, ISO resource allocation, stream packets, PHY packets, and PHY receive activation. The ioctl set is exposed as `FW_CDEV_IOC_*`.

Control flow is fd/event based: userspace opens a FireWire device, negotiates ABI info, handles bus reset events, issues asynchronous requests, reads response/request events, registers local address ranges and sends responses, creates and queues isochronous contexts using mmaped buffers, and manages bus/ISO resources across generation changes. State lives in firewire-core device files, bus generation IDs, node IDs, pending transactions, address handlers, descriptors, ISO contexts, DMA buffers, and resource allocations. Persistence is fd lifetime except physical bus/config ROM side effects and automatic resource reallocation across bus resets.

Dependencies include `linux/ioctl.h`, `linux/types.h`, `linux/firewire-constants.h`, IEEE 1394 transaction codes, OHCI controller behavior, POSIX clocks for cycle-timer variants, and firewire-core. Integration points include libraw1394-like tools, AV/C/IEC 61883 stacks, device firmware/debug tools, local-node management, and isochronous audio/video applications.

Risks include ABI-version compatibility between old/new request and response event layouts, variable-length event parsing, bus reset races invalidating node IDs/generations, endian rules for packet headers, mmap/DMA buffer lifetime bugs, resource leaks, and privileged PHY/local-node operations. Test signals include firewire-core cdev selftests or hardware tests, ABI version negotiation tests, bus reset event tests, async transaction loopback, ISO queue/start/flush tests, cycle timer monotonicity checks, and 32-bit compat layout validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/firewire-cdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/firewire-constants.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/firewire-constants.h

This header defines IEEE 1394/FireWire transaction, response, speed, acknowledgment, and retry constants shared by FireWire kernel and userspace code.

Important exports include transaction codes `TCODE_WRITE_QUADLET_REQUEST`, `WRITE_BLOCK_REQUEST`, `READ_*`, `LOCK_REQUEST`, `STREAM_DATA`, extended lock opcodes `EXTCODE_*`, Linux-specific combined lock tcodes, response codes `RCODE_COMPLETE`, `CONFLICT_ERROR`, `DATA_ERROR`, `TYPE_ERROR`, `ADDRESS_ERROR`, Linux-specific send/cancel/busy/generation/no-ack rcodes, speed codes `SCODE_100` through `SCODE_3200`, ack codes `ACK_*`, and retry codes `RETRY_*`.

Control flow is protocol interpretation: FireWire request/response packets and cdev events carry these values, and userspace or kernel code selects packet handling and error recovery based on them. The header has no runtime state; state is in bus transactions, controller queues, and cdev pending-event state.

Dependencies are IEEE 1394 protocol definitions and `firewire-cdev.h`. Integration points include asynchronous transactions, lock operations, stream packets, error reporting, and FireWire diagnostic tools.

Risks include confusing Linux-specific combined tcodes with wire tcodes, speed-code aliasing such as beta speed representation, and incomplete error handling for busy/generation/no-ack cases. Test signals include transaction encode/decode tests, cdev event response-code handling, hardware loopback tests, and protocol analyzer comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/firewire-constants.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fou.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/fou.h

This generated UAPI header defines the generic-netlink ABI for Foo-over-UDP and related UDP tunnel port management. It is generated from `Documentation/netlink/specs/fou.yaml`.

Important exports include family metadata `FOU_GENL_NAME` and `FOU_GENL_VERSION`, encapsulation types for direct FOU and GUE, attribute IDs such as port, address family, IP protocol, local peer, peer port, interface index, encapsulation type, and UDP checksum controls, plus command IDs for add, delete, and get/dump operations.

Control flow is generic-netlink based: userspace sends add/delete/get commands with the required attributes; the kernel updates or reports UDP tunnel socket state for FOU/GUE encapsulation. State lives in network namespace tunnel-port tables and sockets. Persistence is runtime only and normally recreated by network configuration tools.

Dependencies are generic netlink, UDP tunnel infrastructure, IP protocol numbers, network namespaces, and the YNL generation pipeline. Integration points include `ip fou`, tunnel drivers, GUE/FOU encapsulation, and `tools/net/ynl`.

Risks include hand-editing generated constants, invalid attribute combinations, namespace leaks, tunnel port conflicts, checksum setting mismatches, and schema/header drift. Test signals include YNL regeneration diff checks, `ip fou` roundtrip tests, netlink policy tests, namespace isolation tests, and tunnel packet encapsulation/decapsulation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fou.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fpga-dfl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/fpga-dfl.h

This UAPI header defines the ioctl ABI for Intel/DFL-based FPGA devices. It covers common API version/extension checks, AFU port reset and region discovery, DMA map/unmap, eventfd-backed interrupts, and FME partial reconfiguration plus port assignment/release and error IRQs.

Important exports include `DFL_FPGA_API_VERSION`, `DFL_FPGA_MAGIC`, base ranges `DFL_FPGA_BASE`, `DFL_PORT_BASE`, `DFL_FME_BASE`, common ioctls `DFL_FPGA_GET_API_VERSION` and `DFL_FPGA_CHECK_EXTENSION`, AFU ioctls `DFL_FPGA_PORT_RESET`, `PORT_GET_INFO`, `PORT_GET_REGION_INFO`, `PORT_DMA_MAP`, `PORT_DMA_UNMAP`, port error/UINT IRQ get/set commands, and FME commands `DFL_FPGA_FME_PORT_PR`, `PORT_RELEASE`, `PORT_ASSIGN`, and FME error IRQ get/set. Key structs include `dfl_fpga_port_info`, `dfl_fpga_port_region_info`, `dfl_fpga_port_dma_map`, `dfl_fpga_port_dma_unmap`, `dfl_fpga_irq_set`, and `dfl_fpga_fme_port_pr`.

Control flow is ioctl and mmap/eventfd based: userspace opens an AFU or FME fd, checks API support, discovers regions, mmaps device regions, maps user pages for DMA to obtain IOVAs, binds eventfds to interrupts, resets ports, or asks FME to partially reconfigure a port. State lives in DFL device drivers, IOMMU mappings, FPGA manager state, port ownership, interrupt routing, and eventfd references. Persistence can include FPGA programmed image/port assignment until reset or reconfiguration.

Dependencies include `linux/types.h`, `linux/ioctl.h`, eventfd, IOMMU/DMA mapping, FPGA manager, and DFL bus drivers. Integration points include OPAE-like userspace, VFIO-inspired ABI design, hardware accelerators, and platform management tools.

Risks include DMA mapping of unpinned or misaligned memory, stale IOVA unmap bugs, eventfd lifetime mistakes, destructive resets during DMA/partial reconfiguration, ABI extension handling through `argsz`/flags, and privilege boundaries around FME controls. Test signals include DFL driver selftests, ioctl struct size/flags validation, DMA map/unmap stress, eventfd interrupt tests, partial reconfiguration failure tests, and IOMMU fault handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fpga-dfl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/fs.h

This central UAPI header defines generic filesystem and block-device constants, ioctl numbers, shared structures, inode attribute flags, range clone/dedupe/trim structures, read/write flags, pagemap scan/query ABIs, proc maps query ABI, and generic filesystem shutdown flags.

Important exports include seek constants including `SEEK_DATA`/`SEEK_HOLE`, rename flags, `PROCFS_ROOT_INO`, `struct file_clone_range`, `fstrim_range`, `fsuuid2`, `fs_sysfs_path`, `logical_block_metadata_cap`, dedupe structures, `files_stat_struct`, `inodes_stat_t`, `fsxattr`, `file_attr`, `FS_XFLAG_*`, block ioctls `BLK*`, filesystem ioctls `FIBMAP`, `FIGETBSZ`, `FIFREEZE`, `FITHAW`, `FITRIM`, `FICLONE`, `FICLONERANGE`, `FIDEDUPERANGE`, `FS_IOC_*`, inode flags `FS_*_FL`, `RWF_*` per-I/O flags, pagemap scan structures, `procmap_query`, and `FS_IOC_SHUTDOWN`.

Control flow spans many syscalls/ioctls: VFS dispatches generic fs ioctls for clone, dedupe, freeze, trim, labels, UUIDs, xattrs, fiemap, shutdown, and block-device controls; read/write syscalls interpret `RWF_*`; procfs ioctls scan pagemap or query VMAs. State lives in mounted filesystems, inodes, block devices, page tables, VMA metadata, and procfs. Persistence applies to inode flags, labels, UUIDs, dedupe/clone extent sharing, trims/discards, and block-device settings where supported.

Dependencies include `linux/limits.h`, `linux/ioctl.h`, `linux/types.h`, `linux/fscrypt.h` for userspace, `linux/mount.h`, block layer, VFS, MM/procfs, and numerous filesystem implementations. Integration points include coreutils, util-linux, xfs/ext tooling, backup/dedupe applications, databases using `RWF_*`, memory introspection tools, and container/security tooling using procfs queries.

Risks are very high ABI blast radius: changing constants breaks libc and tools, inode flag exhaustion, compat issues for `long`/pointer-sized ioctl payloads, incorrect permission checks exposing physical layout or process memory metadata, destructive block ioctls, and semantic divergence across filesystems. Test signals include exported header builds, xfstests generic ioctl suites, block ioctl tests, clone/dedupe/trim/freeze tests, read/write flag tests, pagemap/procmap selftests, and 32-bit compat coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fscrypt.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/fscrypt.h

This UAPI header defines the filesystem encryption userspace ABI. It covers encryption policy versions, modes, flags, key specifiers, key management ioctls, key status reporting, nonce retrieval, and file encryption policy get/set operations.

Important exports include policy structs such as `fscrypt_policy_v1`, `fscrypt_policy_v2`, and union wrappers, mode constants for AES/Adiantum variants, policy flags for padding, direct-key, IV_INO_LBLK_64, IV_INO_LBLK_32, and inlinecrypt optimization, key specifier types, `fscrypt_add_key_arg`, `fscrypt_remove_key_arg`, `fscrypt_get_key_status_arg`, and ioctls such as `FS_IOC_SET_ENCRYPTION_POLICY`, `GET_ENCRYPTION_POLICY`, `GET_ENCRYPTION_PWSALT`, `GET_ENCRYPTION_POLICY_EX`, `ADD_ENCRYPTION_KEY`, `REMOVE_ENCRYPTION_KEY`, `REMOVE_ENCRYPTION_KEY_ALL_USERS`, `GET_ENCRYPTION_KEY_STATUS`, and `GET_ENCRYPTION_NONCE`.

Control flow is ioctl based: userspace configures an empty directory with an encryption policy, adds or removes keys to the filesystem keyring, queries key status, and obtains policy/nonce metadata. Kernel state includes fscrypt master keys, per-filesystem keyrings, policy metadata in inodes, prepared per-file encryption keys, and eviction state when keys are removed. Persistence includes encryption policy and nonce metadata on disk; raw key material should not persist in this ABI.

Dependencies include `linux/types.h`, `linux/ioctl.h`, VFS, filesystem fscrypt hooks, kernel crypto API, keyrings, inline encryption hardware, and generic `fs.h` ioctl reservations. Integration points include ext4, F2FS, userspace key management, Android file-based encryption, backup/restore tools, and fsverity when combined with encrypted files.

Risks include irreversible access loss if keys/policies are mishandled, policy version confusion, mode/flag incompatibility, key identifier collisions or leakage, incorrect zeroing of reserved fields, and cross-filesystem behavior differences. Test signals include fscrypt xfstests, key add/remove/status tests, v1/v2 policy compatibility, inlinecrypt tests, locked-directory access tests, nonce retrieval tests, and compat ioctl layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fscrypt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fsi.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/fsi.h

This header defines userspace ioctls for the FSI subsystem, especially raw SCOM access and SBEFIFO control. It is used by low-level service/debug tools for POWER/OpenBMC-style hardware management paths.

Important exports include `struct scom_access`, SCOM interface error flags `SCOM_INTF_ERR_*`, PIB status values `SCOM_PIB_*`, check/reset flags `SCOM_CHECK_*` and `SCOM_RESET_*`, and ioctls `FSI_SCOM_CHECK`, `FSI_SCOM_READ`, `FSI_SCOM_WRITE`, and `FSI_SCOM_RESET`. The file also defines `/dev/sbefifo*` ioctl structures and command constants for controlling SBE FIFO behavior.

Control flow is ioctl based: userspace opens SCOM or SBEFIFO character devices, checks support/protection, issues raw reads/writes with address/data/mask, interprets interface and PIB status, or resets the interface/PIB. State lives in FSI master/slave drivers, SCOM engines, secure boot/protection state, and hardware FIFOs. Persistence is hardware-side register effects, not file data.

Dependencies include `linux/types.h`, `linux/ioctl.h`, FSI core drivers, SCOM/SBE hardware, OpenBMC platform support, and secure-boot policy. Integration points include service processors, chip diagnostics, firmware update/debug tools, and platform bring-up workflows.

Risks include hardware register corruption, secure-boot bypass attempts, future error bits requiring conservative handling, partial writes through masks, timeout/reset side effects, and ABI size changes in low-level structs. Test signals include FSI driver selftests, hardware or simulator SCOM read/write tests, protected-interface tests, reset-path validation, and error/status decode tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fsl_hypervisor.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/fsl_hypervisor.h

This UAPI header defines Freescale/NXP hypervisor ioctl interfaces used by guests to interact with hypervisor-managed resources, including doorbells, partitions, byte channels, DMA windows, and device tree/resource information.

Important exports include ioctl command numbers under the Freescale hypervisor magic, structures for doorbell management, partition status/control, memory or DMA window operations, byte-channel send/receive, and interrupt/event routing. The ABI uses fixed-width integer types and ioctl payload structs to pass guest physical addresses, handles, status codes, and resource IDs.

Control flow is guest userspace ioctl into a hypervisor-facing kernel driver: userspace requests resource information or operations, the driver validates permissions and forwards hypercalls or platform calls, and hypervisor state changes are reflected back through output fields or events. State lives in hypervisor partition/resource tables, guest-visible device nodes, interrupt channels, and any shared buffers. Persistence depends on hypervisor configuration, not the header.

Dependencies include `linux/types.h`, `linux/ioctl.h`, PowerPC/Freescale hypervisor support, device tree resource descriptions, and platform-specific hypercalls. Integration points are embedded PowerPC virtualization, management tools, guest drivers, and board support packages.

Risks include privileged resource misuse, guest/host ABI drift, endianness and physical-address width issues, stale handles after partition changes, and insufficient validation of user-provided guest physical addresses. Test signals include platform hypervisor ioctl tests, device-tree resource discovery tests, 32/64-bit guest ABI checks, negative permission tests, and hypercall error-path validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fsl_hypervisor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fsl_mc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/fsl_mc.h

This UAPI header defines the ioctl ABI for Freescale/NXP Management Complex user access. It lets userspace send management commands through an MC portal and receive command status/results.

Important exports include the MC ioctl magic, `struct fsl_mc_command` with a command header and parameter array, and `FSL_MC_SEND_MC_COMMAND`. The structure is intentionally close to the hardware/firmware command format, carrying command IDs, flags/status in the header, and raw command parameters.

Control flow is ioctl based: userspace opens an MC portal device, fills an `fsl_mc_command`, calls the ioctl, the kernel forwards it to MC firmware, and the command buffer is updated with status and output parameters. State lives in MC firmware objects, portal arbitration, and kernel device ownership. Persistence depends on the specific MC command, because some commands create/configure hardware objects.

Dependencies include `linux/ioctl.h`, `linux/types.h`, NXP DPAA2/FSL MC bus drivers, and MC firmware command semantics. Integration points are DPAA2 management tools, DPL/DPCON/DPNI object configuration, networking/storage accelerator setup, and platform provisioning.

Risks include allowing raw firmware commands from insufficiently trusted userspace, command header layout drift, endianness mistakes, firmware-version incompatibility, and persistent hardware misconfiguration. Test signals include MC command roundtrip tests, firmware compatibility tests, permission checks on portal device nodes, negative command status handling, and DPAA2 object lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fsl_mc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fsmap.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/fsmap.h

This header defines the generic reverse-mapping ioctl ABI for filesystem space maps. It lets userspace query which owners occupy physical block ranges, primarily for filesystem diagnostics and scrub/repair tooling.

Important exports include `struct fsmap`, `struct fsmap_head`, device selector constants, owner constants for metadata/free/unknown/static filesystem regions, flag bits such as `FMR_OF_*`, and request flags such as `FMH_OF_DEV_T` where present. The ABI is consumed through `FS_IOC_GETFSMAP` in filesystem-specific ioctl dispatch.

Control flow is ioctl based: userspace provides low and high keys plus a record count; the filesystem walks its reverse mapping metadata and returns sorted `fsmap` records, updating the head with actual count and flags. State is a snapshot of allocator/reverse-map metadata and can race with concurrent allocation. Persistence is the filesystem allocation state being reported.

Dependencies include `linux/types.h`, generic VFS ioctl plumbing, and filesystems that implement reverse mapping such as XFS and Btrfs-like designs. Integration points include `xfs_io`, scrub tools, defragmentation/space accounting tools, and filesystem repair diagnostics.

Risks include exposing physical layout, inconsistent snapshots under concurrent writes, owner-code compatibility across filesystems, device ID ambiguity, and off-by-one range handling. Test signals include fsmap xfstests, low/high key iteration tests, multi-device filesystem tests, metadata owner validation, and permission checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fsmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fsverity.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/fsverity.h

This UAPI header defines the fs-verity userspace ABI for enabling transparent file authenticity verification, measuring file digests, and reading verity metadata. It is used by filesystems that support Merkle-tree-backed read-only verification.

Important exports include hash algorithm IDs `FS_VERITY_HASH_ALG_SHA256` and `SHA512`, `struct fsverity_enable_arg`, `struct fsverity_digest`, `struct fsverity_descriptor`, `struct fsverity_formatted_digest`, metadata type constants for Merkle tree, descriptor, and signature, `struct fsverity_read_metadata_arg`, and ioctls `FS_IOC_ENABLE_VERITY`, `FS_IOC_MEASURE_VERITY`, and `FS_IOC_READ_VERITY_METADATA`.

Control flow is ioctl based: userspace writes file contents, optionally supplies a salt and signature, calls enable verity, then the filesystem builds/stores metadata and marks the file verity-protected; later reads verify blocks against the Merkle tree, and userspace can measure digest or read metadata. State includes per-inode verity flag, descriptor, Merkle tree pages, optional signature, and page-cache verification state. Persistence is file metadata and Merkle tree storage.

Dependencies include `linux/ioctl.h`, `linux/types.h`, kernel crypto, filesystem fsverity hooks, key/signature verification if enabled, and generic `FS_XFLAG_VERITY`/`FS_VERITY_FL` flags. Integration points include Android verified files, package managers, immutable asset stores, ext4/F2FS, and userspace signing tools.

Risks include enabling verity on mutable or incomplete files, digest format/endian mistakes, signature context confusion, unsupported hash algorithms/block sizes, metadata disclosure, and incompatibility with encryption/compression features. Test signals include fsverity selftests, digest reproducibility tests, signature verification tests, corrupted block detection, metadata read tests, and filesystem-specific enable/read-only behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fsverity.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fuse.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/fuse.h

This large UAPI header defines the kernel/userspace protocol for FUSE and CUSE. It includes protocol versioning, request/reply headers, opcodes, capability flags, initialization negotiation, file/open/read/write/statx/ioctl/poll/notify structures, passthrough and backing-map features, and device ioctl helpers.

Important exports include protocol version constants, `FUSE_ROOT_ID`, opcodes such as `FUSE_LOOKUP`, `FORGET`, `GETATTR`, `SETATTR`, `READLINK`, `MKNOD`, `MKDIR`, `UNLINK`, `RMDIR`, `SYMLINK`, `RENAME`, `LINK`, `OPEN`, `READ`, `WRITE`, `STATFS`, `RELEASE`, `FSYNC`, xattr operations, `INIT`, `OPENDIR`, `READDIR`, `INTERRUPT`, `BMAP`, `IOCTL`, `POLL`, `NOTIFY_REPLY`, `BATCH_FORGET`, `FALLOCATE`, `READDIRPLUS`, `LSEEK`, `COPY_FILE_RANGE`, and newer protocol operations. Key structures include `fuse_in_header`, `fuse_out_header`, `fuse_entry_out`, `fuse_attr`, `fuse_open_in/out`, `fuse_read_in`, `fuse_write_in/out`, `fuse_init_in/out`, `fuse_ioctl_*`, `fuse_notify_*`, and many per-op payloads.

Control flow is request/reply over `/dev/fuse`: kernel VFS operations enqueue FUSE requests, a userspace daemon reads request headers and op payloads, performs policy or backing-store work, then writes replies. Initialization negotiates major/minor protocol, limits, flags, and capabilities. State lives in kernel FUSE connections, inode/entry caches, request queues, daemon process state, file handles, writeback cache, notification queues, and optional passthrough/backing mappings. Persistence is controlled by the userspace filesystem backing store, not the header.

Dependencies include `linux/types.h`, `linux/ioctl.h`, VFS, mount infrastructure, splice/read/write device semantics, poll/notify, and CUSE character-device support. Integration points include libfuse, sshfs, virtiofs, container overlay tools, user-mode filesystems, and kernel filesystem caching/writeback.

Risks include protocol-version negotiation bugs, untrusted daemon hangs causing VFS stalls, request size and alignment mistakes, cache coherency issues, security bugs in ioctl/passthrough/backing-map features, 32-bit compat layout problems, and deadlocks during writeback or interrupt handling. Test signals include libfuse protocol tests, kernel FUSE selftests, fstests on FUSE mounts, init negotiation tests across protocol versions, interrupt/abort tests, readdirplus/cache invalidation tests, ioctl/poll/notify tests, and virtiofs integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/fuse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/futex.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/futex.h

This UAPI header defines futex syscall operation codes, futex2 flags, vector wait structures, robust futex list structures, owner/waiter bits, wake-op encoding macros, and requeue/bitset constants. It is a core userspace synchronization ABI used by threading libraries.

Important exports include operations `FUTEX_WAIT`, `WAKE`, `FD`, `REQUEUE`, `CMP_REQUEUE`, `WAKE_OP`, `LOCK_PI`, `UNLOCK_PI`, `TRYLOCK_PI`, `WAIT_BITSET`, `WAKE_BITSET`, `WAIT_REQUEUE_PI`, `CMP_REQUEUE_PI`, and `LOCK_PI2`, plus private and realtime flags. Futex2 exports include size flags, NUMA/MPOL/private bits, `FUTEX_WAITV_MAX`, and `struct futex_waitv`. Robust futex exports include `struct robust_list`, `struct robust_list_head`, `FUTEX_WAITERS`, `FUTEX_OWNER_DIED`, `FUTEX_TID_MASK`, `ROBUST_LIST_LIMIT`, `FUTEX_BITSET_MATCH_ANY`, and wake-op composition macros.

Control flow is syscall based around userspace memory: user code performs atomic operations in userspace and calls futex only to block, wake, requeue, or participate in PI locking. The kernel validates user addresses, hashes futex keys, manages wait queues and PI rtmutex state, and scans robust lists at thread exit to mark owner death. State is split between user memory words and kernel wait queues/PI state; robust list head is per-thread user memory registered with the kernel. Persistence is only process/thread lifetime.

Dependencies include `linux/compiler.h`, `linux/types.h`, scheduler, rtmutex priority inheritance, memory management/user access, robust-list registration syscalls, and libc pthread implementations. Integration points include glibc/musl pthread mutexes/conds, JVMs, runtimes, databases, and sandboxed synchronization primitives.

Risks include ABI immutability of robust structs, user memory races, priority-inheritance deadlocks, time namespace/realtime clock behavior, wake-op encoding mistakes, NUMA futex2 compatibility, and security exposure from arbitrary user addresses. Test signals include futex selftests, pthread stress tests, PI mutex tests, robust owner-death tests, waitv tests, timeout/realtime tests, 32-bit compat tests, and race/fuzz testing under sanitizers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gameport.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/gameport.h

This UAPI header defines constants for the legacy gameport input subsystem. It names gameport operating modes and vendor IDs used by joystick/gameport drivers and userspace identification tools.

Important exports are modes `GAMEPORT_MODE_DISABLED`, `GAMEPORT_MODE_RAW`, and `GAMEPORT_MODE_COOKED`, plus vendor IDs for Analog, Mad Catz, Logitech, Creative, Genius, InterAct, Microsoft, Thrustmaster, Gravis, and Guillemot.

Control flow is indirect through gameport/input drivers: drivers identify or switch gameport mode and expose input devices; userspace mostly observes the resulting input events or metadata. The header stores no state. Runtime state is in the gameport driver, hardware port mode, attached device protocol, and input subsystem device registration.

Dependencies are the legacy gameport core and input subsystem. Integration points include old joystick drivers, input device enumeration, and compatibility with historical hardware.

Risks include stale vendor ID coverage, limited hardware availability, raw/cooked mode mismatch, and keeping obsolete constants stable for old userspace. Test signals include build coverage for gameport drivers, input enumeration tests on supported hardware or emulators, and header compatibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/gameport.h -->
