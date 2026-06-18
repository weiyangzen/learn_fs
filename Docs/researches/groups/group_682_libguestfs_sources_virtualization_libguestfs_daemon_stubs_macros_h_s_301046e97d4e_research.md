# Group Research: group_682_libguestfs_sources_virtualization_libguestfs_daemon_stubs_macros_h_s_301046e97d4e

Scope checked: `Docs/research_subset_a.md` includes `sources/virtualization/libguestfs`. All files listed for this group were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/stubs-macros.h -->
# File Research: sources/virtualization/libguestfs/daemon/stubs-macros.h

## Role
Defines daemon stub helper macros used by generated action stubs to normalize device, mountable, and path-or-device arguments before dispatching to implementation functions.

## Main Responsibilities
- `RESOLVE_DEVICE` runs `device_name_translation`, validates the result with `is_device_parameter`, and cancels pending FileIn transfers on argument failure.
- `RESOLVE_MOUNTABLE` parses `btrfsvol:` descriptors into `mountable_t`, otherwise resolves ordinary device strings.
- `REQUIRE_ROOT_OR_RESOLVE_DEVICE` accepts either a valid device parameter or an absolute path inside the mounted guest root.
- `REQUIRE_ROOT_OR_RESOLVE_MOUNTABLE` accepts either a device/mountable descriptor or an absolute path represented as `MOUNTABLE_PATH`.

## Error Handling
The macros reply through daemon protocol helpers and return directly from the caller. File upload paths call `cancel_receive()` before reporting validation failures.

## Filesystem/Storage Relevance
This header is part of the trust boundary for daemon filesystem APIs. It decides whether strings are treated as guest filesystem paths, appliance device names, or btrfs subvolume mountables.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/stubs-macros.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/swap.c -->
# File Research: sources/virtualization/libguestfs/daemon/swap.c

## Role
Implements daemon actions for creating, enabling, disabling, and relabeling Linux swap devices and swap files.

## Main Operations
- `do_mkswap()` wraps `mkswap -f`, with optional `-L` label and `-U` UUID.
- `do_mkswap_L()` and `do_mkswap_U()` are compatibility wrappers that set `optargs_bitmask`.
- `do_mkswap_file()` maps a guest path through `sysroot_path()` and runs `mkswap` on the file.
- `do_swapon_*()` and `do_swapoff_*()` wrap `swapon` and `swapoff` for devices, files, labels, and UUIDs.
- `swap_set_uuid()` and `swap_set_label()` wrap `swaplabel`.

## Validation and Side Effects
- Swap labels are limited to 16 bytes.
- Device creation calls `wipe_device_before_mkfs()` before `mkswap`.
- Swap on/off operations call `udev_settle()` after command completion.

## Filesystem/Storage Relevance
This file manages swap signatures and active swap state on guest block devices/files, including UUID/label metadata used by `/etc/fstab` and boot-time activation.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/swap.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/sync.c -->
# File Research: sources/virtualization/libguestfs/daemon/sync.c

## Role
Implements daemon disk synchronization for guestfs `sync`, with Linux and Windows-specific flushing behavior.

## Main Flow
- `do_sync()` calls `sync_disks()` and reports failure.
- On Unix systems with `sync(2)`, `sync_disks()` calls `sync()` first.
- On Linux with `fsync`, `fsync_devices()` scans `/sys/block`, opens common disk-like devices, skips the appliance root device, and `fsync()`s each.
- On Windows, `sync_win32()` enumerates fixed logical drives and calls `FlushFileBuffers()` on volume handles.

## Semantics
The Linux path explicitly compensates for qemu writeback caching by fsyncing block devices after scheduling writes with `sync()`.

## Filesystem/Storage Relevance
This file is important for ensuring filesystem mutations performed inside the appliance reach the underlying virtual disks before the caller assumes persistence.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/sync.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/syslinux.c -->
# File Research: sources/virtualization/libguestfs/daemon/syslinux.c

## Role
Implements daemon actions for installing Syslinux and Extlinux bootloaders.

## Main Operations
- `optgroup_syslinux_available()` and `optgroup_extlinux_available()` probe for `syslinux` and `extlinux`.
- `do_syslinux()` runs `syslinux --install --force`, optionally with `--directory`.
- `do_extlinux()` maps the guest directory through `sysroot_path()` and runs `extlinux --install`.

## Error Handling
External command stderr is captured and returned through `reply_with_error`.

## Filesystem/Storage Relevance
This file supports bootloader installation into guest filesystems or devices, a common operation after manipulating boot partitions or disk images.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/syslinux.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/sysroot-c.c -->
# File Research: sources/virtualization/libguestfs/daemon/sysroot-c.c

## Role
Provides an OCaml binding for retrieving the daemon `sysroot` string.

## Main Operation
- `guestfs_int_daemon_get_sysroot()` returns `sysroot` as an OCaml string via `caml_copy_string`.

## Notes
This file is small glue between C daemon state and OCaml inspection code.

## Filesystem/Storage Relevance
The sysroot path is the base directory used for mounted guest filesystems inside the appliance.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/sysroot-c.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/tar.c -->
# File Research: sources/virtualization/libguestfs/daemon/tar.c

## Role
Implements tar-based archive upload and download actions, including compressed variants and optional preservation of xattrs, SELinux labels, ACLs, numeric owners, and directory symlinks.

## Tar In
- `do_tar_in()` receives a FileIn stream and pipes it into `tar -C <sysroot-dir> -xf -`.
- Supports compression filters: compress, gzip, bzip2, xz, lzop, lzma, and zstd.
- Checks whether `chown` is supported on the target filesystem and adds `--no-same-owner` when needed.
- Captures tar stderr in a temporary error file so upload failures can report meaningful errors.
- `do_tgz_in()` and `do_txz_in()` are gzip/xz compatibility wrappers.

## Tar Out
- `do_tar_out()` verifies the target is a directory, builds a tar command, replies before streaming, then sends FileOut chunks.
- Supports excludes through a temporary `-X` exclude file.
- On read or subprocess failure after the protocol reply, it cancels the file transfer with `send_file_end(1)`.
- `do_tgz_out()` and `do_txz_out()` are gzip/xz wrappers.

## Filesystem/Storage Relevance
This is the daemon’s bulk tree import/export path for guest filesystems, preserving filesystem metadata when requested.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/tar.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/truncate.c -->
# File Research: sources/virtualization/libguestfs/daemon/truncate.c

## Role
Implements file truncation actions inside the guest filesystem.

## Main Operations
- `do_truncate_size()` opens a guest path under `CHROOT_IN`, calls `ftruncate()` to the requested size, and closes the file.
- `do_truncate()` truncates to zero by delegating to `do_truncate_size()`.

## Error Handling
Open, truncate, and close failures are reported with the guest path.

## Filesystem/Storage Relevance
This provides direct guest file size manipulation, affecting file allocation and sparse-file behavior depending on the underlying filesystem.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/truncate.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/tsk.c -->
# File Research: sources/virtualization/libguestfs/daemon/tsk.c

## Role
Implements internal filesystem walking and inode search using The Sleuth Kit when libtsk support is available.

## Main Flow
- `do_internal_filesystem_walk()` opens the mountable’s device with TSK and recursively walks allocated and unallocated directory entries.
- `do_internal_find_inode()` performs the same walk but emits only entries whose metadata address matches the requested inode.
- `open_filesystem()` uses `tsk_img_open()` and `tsk_fs_open_img()` with type autodetection.
- Callbacks serialize `guestfs_int_tsk_dirent` records with XDR and stream them via FileOut.

## Metadata Extraction
- Maps TSK file name/meta types to compact type characters.
- Computes allocation, reallocation, and compression flags.
- Copies size, link count, atime, mtime, ctime, crtime, and symlink target when metadata exists.
- Skips `.` and `..` entries except the filesystem root entry.

## Feature Gate
When libtsk is unavailable, the file expands `OPTGROUP_LIBTSK_NOT_AVAILABLE`.

## Filesystem/Storage Relevance
This file enables forensic-style traversal of filesystems, including deleted/unallocated entries, without mounting them through the kernel.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/tsk.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/umask.c -->
# File Research: sources/virtualization/libguestfs/daemon/umask.c

## Role
Implements daemon actions for setting and reading the process umask.

## Main Operations
- `do_umask()` validates the mask is between `0000` and `0777`, calls `umask()`, and returns the previous value.
- `do_get_umask()` reads the current mask by temporarily setting it to `022`, then restores the previous value.

## Filesystem/Storage Relevance
The daemon umask influences default permissions for files and directories created during guest filesystem operations.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/umask.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/upload.c -->
# File Research: sources/virtualization/libguestfs/daemon/upload.c

## Role
Implements raw file/device upload and download actions over the libguestfs FileIn/FileOut protocol.

## Upload Path
- `upload_to_fd()` receives FileIn chunks and writes them to a supplied file descriptor, tracking progress.
- `upload()` opens either a device path directly or a guest filesystem path under chroot, optionally seeks to an offset, and delegates to `upload_to_fd()`.
- `do_upload()` truncates or creates the target.
- `do_upload_offset()` writes at an offset without truncation and rejects negative offsets.

## Download Path
- `do_download()` opens a file or device, rejects directories, computes total size, replies, and streams chunks.
- Device sizes are obtained through `do_blockdev_getsize64()`.
- `do_download_offset()` streams a bounded range from a file/device and permits short reads at EOF.

## Protocol Semantics
After the initial FileOut reply, later read/close errors cannot be reported as normal RPC errors; the transfer is canceled instead.

## Filesystem/Storage Relevance
This is the low-level data transfer path for moving whole files or block-device contents between host and guest.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/upload.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/utils-c.c -->
# File Research: sources/virtualization/libguestfs/daemon/utils-c.c

## Role
Provides OCaml bindings for selected daemon utility functions.

## Exposed Bindings
- `guestfs_int_daemon_get_verbose_flag()`
- `guestfs_int_daemon_is_device_parameter()`
- `guestfs_int_daemon_is_root_device()`
- `guestfs_int_daemon_prog_exists()`
- `guestfs_int_daemon_udev_settle()`
- `guestfs_int_get_random_uuid()`

## Constraints
The file notes that OCaml-called utility bindings must not call daemon `reply*` functions. Most bindings are `[@@noalloc]`-style simple boolean wrappers.

## Filesystem/Storage Relevance
These bindings let OCaml daemon/inspection code reuse C-side device classification, tool probing, udev settling, and UUID generation.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/utils-c.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/utils.c -->
# File Research: sources/virtualization/libguestfs/daemon/utils.c

## Role
Provides shared daemon utility state and helpers for device classification, sysroot path construction, robust I/O, string-list management, mountable parsing, udev settling, UUID generation, and temporary exclude files.

## Global State
- Tracks `root_device`, `verbose`, `enable_network`, `sysroot`, `sysroot_len`, `autosync_umount`, and `test_mode`.
- `sysroot` defaults to `/sysroot`.

## Device and Path Helpers
- `is_root_device()` compares device `st_rdev` against the appliance root device.
- `is_device_parameter()` accepts `/dev/...` disk-like block devices, rejects the appliance root device, handles `/dev/sd*` translation compatibility, and verifies `BLKGETSIZE64`.
- `sysroot_path()` prepends `/sysroot`.
- `sysroot_realpath()` resolves a path inside chroot and maps it back to sysroot.

## Utility Infrastructure
- `xwrite()` and `xread()` perform complete writes/reads.
- `stringsbuf` helpers build NULL-terminated string vectors.
- `split_lines()` implements command-output line splitting with documented corner-case behavior.
- `filter_list()`, `trim()`, `sort_strings()`, and `empty_list()` provide common list/string operations.

## Mountable and External State
- `parse_btrfsvol()` parses `btrfsvol:/dev/.../subvol` descriptors and resolves the backing device.
- `mountable_to_string()` converts mountable structs back to text.
- `prog_exists()` searches `$PATH`.
- `random_name()` substitutes random base36 characters into path templates.
- `udev_settle_file()` wraps `udevadm settle`.
- `get_random_uuid()` wraps `uuidgen`.
- `make_exclude_from_file()` writes tar/rsync-style exclude patterns to a temp file.

## Filesystem/Storage Relevance
This file is central daemon plumbing for safe guest path handling, block-device recognition, btrfs subvolume mountables, udev consistency after device changes, and file-list construction.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/utils.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/utimens.c -->
# File Research: sources/virtualization/libguestfs/daemon/utimens.c

## Role
Implements timestamp updates for guest filesystem paths.

## Main Operation
- `do_utimens()` maps sentinel nanosecond values `-1` to `UTIME_NOW` and `-2` to `UTIME_OMIT`.
- Calls `utimensat()` inside the guest chroot with `AT_SYMLINK_NOFOLLOW`.

## Semantics
The operation updates the path itself without following symlinks.

## Filesystem/Storage Relevance
This file mutates file atime and mtime metadata in guest filesystems.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/utimens.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/utsname.c -->
# File Research: sources/virtualization/libguestfs/daemon/utsname.c

## Role
Returns appliance kernel/system identity data.

## Main Operation
- `do_utsname()` calls `uname()`, allocates `guestfs_int_utsname`, and copies sysname, release, version, and machine fields.

## Error Handling
Allocation and `uname()` failures are returned through daemon reply helpers.

## Filesystem/Storage Relevance
Indirect relevance: callers can identify the appliance kernel environment that is performing filesystem operations.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/utsname.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/uuids.c -->
# File Research: sources/virtualization/libguestfs/daemon/uuids.c

## Role
Dispatches UUID-setting requests to filesystem-specific implementations.

## Main Operations
- `do_set_uuid()` reads the device filesystem type via `get_blkid_tag(device, "TYPE")`.
- Ext filesystems are handled through `do_set_e2uuid()` after rejecting ext magic UUID strings.
- XFS, swap, and btrfs are dispatched through a small handler table.
- `do_set_uuid_random()` generates a UUID and dispatches ext, XFS, btrfs, or swap-specific randomization.

## Validation
- Ext rejects `clear`, `random`, and `time` for the generic fixed-UUID API.
- XFS rejects `nil` and `generate` for fixed UUIDs.
- Unsupported filesystem types produce `NOT_SUPPORTED`.

## Filesystem/Storage Relevance
This file coordinates persistent filesystem identity metadata across ext, XFS, swap, and btrfs.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/uuids.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/wc.c -->
# File Research: sources/virtualization/libguestfs/daemon/wc.c

## Role
Implements line, word, and byte count actions for guest files.

## Main Operation
- `wc()` opens a guest path inside chroot and runs `wc` with the requested flag, feeding the file descriptor to stdin through `COMMAND_FLAG_CHROOT_COPY_FILE_TO_STDIN`.
- Parses the leading integer from command output.
- `do_wc_l()`, `do_wc_w()`, and `do_wc_c()` provide line, word, and byte counts.

## Filesystem/Storage Relevance
Provides simple file content metrics without exposing guest paths directly to host commands.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/wc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/xattr.c -->
# File Research: sources/virtualization/libguestfs/daemon/xattr.c

## Role
Implements Linux extended attribute operations for guest files, including symlink-aware variants and bulk xattr listing.

## Feature Gate
The implementation is compiled when Linux xattr headers and list/get/set/remove xattr APIs are available. Otherwise it expands `OPTGROUP_LINUXXATTRS_NOT_AVAILABLE`.

## Main Operations
- `do_getxattrs()` and `do_lgetxattrs()` list and read all attributes for a path.
- `do_setxattr()` and `do_lsetxattr()` set attributes.
- `do_removexattr()` and `do_lremovexattr()` remove attributes.
- `do_getxattr()` and `do_lgetxattr()` read one attribute value.
- `do_internal_lxattrlist()` returns grouped xattr data for many path names under a base path.
- `copy_xattrs()` copies non-hidden attributes from one path to another.

## Data Handling
- `split_attr_names()` converts Linux’s NUL-separated xattr name buffer into a string vector without duplicating individual names.
- `not_hidden_xattr()` filters out `user.WofCompressedData`, used by NTFS CompactOS/system compression.
- Results are sorted by attribute name.
- Attribute value lengths are checked against `XATTR_SIZE_MAX`.

## Error Handling
Most syscalls run inside `CHROOT_IN`/`CHROOT_OUT`. `do_internal_lxattrlist()` treats some per-file list failures as nonfatal and records a special empty-name entry containing the number of attributes.

## Filesystem/Storage Relevance
This file exposes filesystem metadata beyond POSIX mode/ownership, including SELinux labels, ACL backing attributes, user metadata, and filesystem-specific xattrs.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/xfs.c -->
# File Research: sources/virtualization/libguestfs/daemon/xfs.c

## Role
Implements XFS-specific daemon helpers for growfs, admin metadata changes, UUID/label setters, and minimum-size reporting.

## Main Operations
- `optgroup_xfs_available()` checks for `mkfs.xfs`.
- `do_xfs_growfs()` maps a mount path through `sysroot_path()` and builds an `xfs_growfs` command with optional data/log/realtime sizing controls.
- `do_xfs_admin()` wraps `xfs_admin` for feature flags, lazycounter, label, and UUID options.
- `xfs_set_uuid()`, `xfs_set_uuid_random()`, and `xfs_set_label()` configure `optargs_bitmask` and delegate to `do_xfs_admin()`.
- `xfs_minimum_size()` returns the current XFS data section size because XFS does not support shrinking.

## Validation
Numeric size and percentage arguments must be nonnegative. XFS labels are limited by `XFS_LABEL_MAX`. Minimum-size computation checks for integer overflow.

## Filesystem/Storage Relevance
This file handles XFS grow and metadata operations used during guest filesystem resize, relabeling, and UUID management workflows.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/xfs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/yara.c -->
# File Research: sources/virtualization/libguestfs/daemon/yara.c

## Role
Implements daemon YARA rule loading, destruction, and internal scanning actions when libyara is available.

## Main Flow
- `do_yara_load()` receives a FileIn rules file into a temporary file.
- Initializes YARA once with `yr_initialize()`.
- Destroys any previously loaded rules.
- Attempts `yr_rules_load()` first, then compiles source rules with `yr_compiler_add_file()` if the file is not already compiled rules.
- `do_yara_destroy()` frees loaded rules.
- `do_internal_yara_scan()` opens a guest path under chroot and scans its file descriptor.

## Output
Matching rules are serialized as `guestfs_int_yara_detection` records containing path and rule identifier, then streamed through FileOut.

## Lifecycle
A destructor `yara_finalize()` destroys remaining rules and calls `yr_finalize()` on daemon exit.

## Filesystem/Storage Relevance
This file enables malware/signature scanning of guest filesystem files from inside the appliance.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/yara.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/zero.c -->
# File Research: sources/virtualization/libguestfs/daemon/zero.c

## Role
Implements zeroing, wipefs, zero-detection, free-space zeroing, and pre-mkfs signature wiping.

## Main Operations
- `do_zero()` zeroes the first 32 blocks of a device, skipping writes for already-zero blocks.
- `do_wipefs()` runs `wipefs -a`, adding `--force` when supported.
- `do_zero_device()` writes zeroes across the entire block device, checking existing data first.
- `do_is_zero()` and `do_is_zero_device()` scan a file or device for nonzero bytes.
- `do_zero_free_space()` creates a randomly named file filled with zeroes until `ENOSPC`, syncs, reports progress from `statvfs`, and unlinks the file.
- `wipe_device_before_mkfs()` internally invokes `wipefs -a` before mkfs-style operations.

## Behavior Notes
`wipefs_has_force_option()` caches whether the installed `wipefs` supports `--force`. `do_zero_free_space()` is intentionally described as open to future sparse/discard implementations but currently fills free space with a temporary file.

## Filesystem/Storage Relevance
This file is used for disk signature removal, whole-device zeroing, sparse-image preparation, and free-space scrubbing before image conversion or compression.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/zero.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/zerofree.c -->
# File Research: sources/virtualization/libguestfs/daemon/zerofree.c

## Role
Wraps the external `zerofree` utility.

## Main Operations
- `optgroup_zerofree_available()` checks for `zerofree`.
- `do_zerofree()` runs `zerofree <device>` and reports command errors.

## Filesystem/Storage Relevance
`zerofree` zeroes unused blocks in supported filesystems, improving sparsification and compressed image efficiency.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/zerofree.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/Makefile.am -->
# File Research: sources/virtualization/libguestfs/lib/Makefile.am

## Role
Autotools build definition for the host-side `libguestfs.la` library and its internal unit test binary.

## Main Contents
- Declares generator-built outputs such as `actions-*.c`, generated headers, POD fragments, symbol file, and struct helpers.
- Builds `libguestfs.la` from common protocol/utils/qemuopts/structs code plus core library modules such as launch, appliance, drives, command, proto, fuse, inspection, copy, create, TSK, YARA, and generated actions.
- Sets include paths for common libraries, gnulib, and public headers.
- Adds external CFLAGS/LIBS for RPC, PCRE2, libvirt, libxml2, SELinux, JSON-C, sockets, clock, gettext, threads, and gnulib.
- Uses version-info tied to `MAX_PROC_NR` and a version script.
- Optionally builds `libvirt-is-version` when libvirt support is enabled.
- Defines `unit-tests` linked against library objects for internal helper testing.
- Generates manpages and HTML from `guestfs.pod` plus generated POD fragments.

## Filesystem/Storage Relevance
This file defines which host-side storage, appliance, protocol, and filesystem helper modules are compiled into libguestfs.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/actions-support.c -->
# File Research: sources/virtualization/libguestfs/lib/actions-support.c

## Role
Provides support helpers for generated host-side action wrappers.

## Main Operations
- `guestfs_int_check_reply_header()` validates protocol program, version, direction, procedure number, and serial number for daemon replies.
- `guestfs_int_check_appliance_up()` rejects daemon calls before launch or while launching.
- `guestfs_int_trace_open()` opens a trace buffer, falling back to stderr if `open_memstream()` fails.
- `guestfs_int_trace_send_line()` emits trace text through `GUESTFS_EVENT_TRACE`.

## Filesystem/Storage Relevance
This file safeguards the RPC protocol used by all host-to-appliance filesystem and block-device actions.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/actions-support.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/alloc.c -->
# File Research: sources/virtualization/libguestfs/lib/alloc.c

## Role
Implements libguestfs internal allocation wrappers that abort through the handle’s abort callback on allocation failure.

## Main Helpers
- `guestfs_int_safe_malloc()`
- `guestfs_int_safe_calloc()` with overflow protection for non-GNU calloc implementations.
- `guestfs_int_safe_realloc()`
- `guestfs_int_safe_strdup()`
- `guestfs_int_safe_strndup()`
- `guestfs_int_safe_memdup()`
- `guestfs_int_safe_asprintf()`

## Design
The wrappers centralize out-of-memory behavior and avoid repeated error-path handling in internal library code.

## Filesystem/Storage Relevance
Indirect but broad: all host-side filesystem, launch, drive, and protocol code relies on these allocation helpers.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/appliance-cpu.c -->
# File Research: sources/virtualization/libguestfs/lib/appliance-cpu.c

## Role
Selects the CPU model string used to boot the libguestfs appliance under qemu/libvirt.

## Main Logic
- On aarch64, returns `host` for KVM and `cortex-a57` for TCG because qemu’s default `virt` machine CPU is unsuitable.
- On powerpc64 and loongarch64, returns `NULL` to avoid problematic CPU options.
- On most other architectures, returns `max`.

## Filesystem/Storage Relevance
The selected CPU model affects whether the appliance boots reliably and efficiently, which gates all filesystem operations.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/appliance-cpu.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/appliance-kcmdline.c -->
# File Research: sources/virtualization/libguestfs/lib/appliance-kcmdline.c

## Role
Builds the Linux kernel command line for the libguestfs appliance.

## Root UUID Handling
- `get_root_uuid_with_file()` reads ext filesystem magic and UUID directly from a raw appliance image.
- It skips direct ext-superblock probing for qcow2 magic.
- `run_qemu_img_dd()` uses `qemu-img dd` to extract the first 256 KiB of qcow2-like images into a raw temp file.
- `get_root_uuid()` combines both paths and returns the appliance root UUID.

## Command Line Construction
`guestfs_int_appliance_command_line()` builds a space-joined argument list containing panic behavior, architecture console settings, boot workarounds, udev timeouts, TCG `lpj`, logging controls, cgroup/USB/crypto optimizations, root UUID, SELinux mode, verbosity, network enablement, sanitized `TERM`, handle identifier, and user append string.

## Architecture Handling
Defines serial console and early printk settings per architecture, including aarch64-specific EFI RTC suppression and log verbosity.

## Filesystem/Storage Relevance
This file determines how the appliance locates and mounts its root filesystem and how it boots into a state capable of serving guest filesystem requests.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/appliance-kcmdline.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/appliance-uefi.c -->
# File Research: sources/virtualization/libguestfs/lib/appliance-uefi.c

## Role
Finds UEFI firmware needed to boot the appliance, currently relevant mainly for aarch64.

## Main Flow
- If libvirt firmware autoselection is supported and allows `efi`, returns that firmware string.
- Otherwise scans generated `guestfs_int_uefi_aarch64_firmware` entries for readable code and vars files.
- Copies the vars/NVRAM file to a libguestfs temp path because firmware variables must be writable.
- Uses debug firmware code when verbose mode is enabled and a debug code file is available.
- Returns firmware flags plus code/vars paths.

## Error Semantics
No firmware found is not an error. Copy or command execution failure is an error.

## Filesystem/Storage Relevance
Correct UEFI setup is required to boot appliances on platforms where the filesystem service VM cannot use legacy BIOS.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/appliance-uefi.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/appliance.c -->
# File Research: sources/virtualization/libguestfs/lib/appliance.c

## Role
Locates or builds the libguestfs appliance used to run the daemon VM.

## Appliance Search Order
- Search each element of `g->path`.
- Prefer supermin appliance skeletons under `supermin.d`.
- If found, build/cache a full appliance with `supermin --build`.
- Otherwise accept a fixed appliance containing `README.fixed`, `kernel`, `initrd`, and `root`.
- Otherwise accept old-style appliance files `vmlinuz.<host_cpu>` and `initramfs.<host_cpu>.img`.

## Supermin Build
- Uses `$TMPDIR/.guestfs-$UID/appliance.d` and a lock file.
- Runs `supermin --build --if-newer --lock --copy-kernel -f ext2 --host-cpu <host_cpu>`.
- Touches built kernel/initrd/root files so temp cleanup policies do not remove active cache entries.

## Error Handling
If no path element matches, reports that no suitable supermin, fixed, or old-style appliance was found on `LIBGUESTFS_PATH`.

## Filesystem/Storage Relevance
This file creates or locates the miniature Linux environment that performs all guest filesystem and block operations.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/appliance.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/available.c -->
# File Research: sources/virtualization/libguestfs/lib/available.c

## Role
Implements host-side availability checks for optional daemon feature groups.

## Main Flow
- `find_or_cache_feature()` checks `g->features` for a cached group result.
- On cache miss, calls `guestfs_internal_feature_available()` and stores the result.
- `guestfs_impl_available()` reports errors for unknown or unavailable groups.
- `guestfs_impl_feature_available()` returns boolean availability while still erroring for unknown groups.

## Result Semantics
The daemon feature result values are interpreted as available, unavailable, or unknown group.

## Filesystem/Storage Relevance
Many filesystem features depend on appliance packages or compile-time options; this file caches and exposes those capability checks.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/available.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/canonical-name.c -->
# File Research: sources/virtualization/libguestfs/lib/canonical-name.c

## Role
Implements canonicalization of device names for public API callers.

## Main Logic
- Converts simple `/dev/hd*`, `/dev/vd*`, and similar disk names to `/dev/sd*` style while avoiding LVs and `/dev/md`.
- For `/dev/mapper/*` and `/dev/dm-*`, tries `guestfs_lvm_canonical_lv_name()`.
- Suppresses errors from LVM canonicalization and returns the original string on failure, preserving historical API behavior.

## Filesystem/Storage Relevance
Canonical device naming affects how callers correlate guest block devices, LVs, and filesystem mount targets.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/canonical-name.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/command.c -->
# File Research: sources/virtualization/libguestfs/lib/command.c

## Role
Implements the host-side internal subprocess runner used throughout libguestfs for qemu-img, supermin, tar, cp, and other external tools.

## Command Construction
- Supports execv-style argument vectors and system-style shell command strings.
- Provides quoted and unquoted shell-string append helpers.
- Supports formatted argument addition.
- Enforces one command style per command object.

## Execution Model
- `guestfs_int_cmd_run()` finalizes, logs, forks, captures output, loops over file descriptors, and waits.
- Child process resets signal handlers, closes extra file descriptors, sets umask `022`, runs optional child setup, applies optional rlimits, sets `LC_ALL=C`, and then `execvp()`s or runs `system()`.
- Stdout callbacks can be line-buffered, unbuffered, or whole-buffer.
- Stderr can be captured into appliance event callbacks or redirected to stdout.

## Pipe Mode
- `guestfs_int_cmd_pipe_run()` is a popen-like interface for streaming stdin/stdout to a child.
- It stores child stderr in a temporary file retrievable with `guestfs_int_cmd_get_pipe_errors()`.
- `guestfs_int_cmd_pipe_wait()` waits for the child.

## Cleanup
`guestfs_int_cmd_close()` frees arguments, temp error files, buffers, child rlimit records, open fds, and waits for any still-running child without reporting errors.

## Filesystem/Storage Relevance
This is the core command execution layer for host-side image creation, appliance building, archive transfer helpers, firmware copying, and external storage tooling.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/command.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/conn-socket.c -->
# File Research: sources/virtualization/libguestfs/lib/conn-socket.c

## Role
Implements the POSIX socket transport between the host library and the guestfs daemon/appliance console.

## Connection Modes
- `guestfs_int_new_conn_socket_listening()` owns a listening daemon socket and optional console socket, then waits for the daemon to connect.
- `guestfs_int_new_conn_socket_connected()` wraps an already connected daemon socket.
- Sockets are set nonblocking.

## Operations
- `accept_connection()` polls daemon and console sockets until the daemon connects or appliance timeout expires.
- `read_data()` and `write_data()` poll daemon data readiness while also draining console logs.
- `can_read_data()` performs nonblocking readiness polling.
- `get_console_sock()` exposes the console socket when present.
- `free_conn_socket()` closes all owned sockets.

## Console Handling
`handle_log_message()` reads appliance console output, emits log callbacks, and responds to SGABIOS serial-console Device Status Report queries with a fake 24x80 response to avoid boot delays.

## Filesystem/Storage Relevance
All daemon filesystem and block-device RPC traffic passes through this connection implementation for direct socket-based launches.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/conn-socket.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/copy-in-out.c -->
# File Research: sources/virtualization/libguestfs/lib/copy-in-out.c

## Role
Implements high-level host-to-guest and guest-to-host recursive copy APIs using tar streams.

## Copy In
- Verifies the local source exists.
- Verifies the remote target is a directory.
- Splits the local path into directory and basename.
- Runs local `tar -cf - <basename>` and passes `/dev/fd/<fd>` to `guestfs_tar_in()`.

## Copy Out
- Verifies the local target directory exists.
- If remote path is a file, downloads it directly to `localdir/basename`.
- If remote path is a directory, starts local `tar -xf -` with a child setup callback that enters `localdir/basename`, then streams `guestfs_tar_out()` into it.
- Handles remote `/` basename as `.`.

## Helper
`split_path()` normalizes trailing slashes and splits path strings into dirname/basename components.

## Filesystem/Storage Relevance
This file provides user-facing recursive file transfer between host filesystems and mounted guest filesystems.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/copy-in-out.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/create.c -->
# File Research: sources/virtualization/libguestfs/lib/create.c

## Role
Implements host-side APIs for creating empty raw and qcow2 disk images.

## Public Entry
`guestfs_impl_disk_create()` validates size/backing-file semantics, dispatches to raw or qcow2 creation, and rejects unsupported formats.

## Raw Creation
- Rejects backing files and raw-incompatible options.
- Supports sparse/off or full preallocation.
- Refuses to overwrite character devices.
- For block devices, attempts `BLKDISCARD` instead of recreating the target.
- For files, creates/truncates the file and uses `ftruncate()` for sparse or `posix_fallocate()`/zero-write emulation for full allocation.

## Qcow2 Creation
- Validates backing format, preallocation, compat (`0.10` or `1.1`), and power-of-two cluster size between 512 and 2 MiB.
- Infers backing format with `guestfs_disk_format()` when a backing file is used and no format is supplied.
- Builds `qemu-img create -f qcow2` with escaped `-o` options.
- Prefixes relative filenames with `./` to avoid qemu protocol interpretation.
- Captures qemu output for error reporting/debug logging.

## Filesystem/Storage Relevance
This file creates virtual disks that are later partitioned, formatted, mounted, or used as backing images.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/create.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/drives.c -->
# File Research: sources/virtualization/libguestfs/lib/drives.c

## Role
Manages the `guestfs_h` drive array and all metadata needed to add file, network, remote, scratch, read-only, and special drives before appliance launch.

## Drive Creation
- File drives store path, format, name, disk label, cache mode, readonly flag, discard mode, copy-on-read flag, and block size.
- Non-file drives store protocol, servers, export name, username, secret, and format.
- Read-only drives create backend-specific COW overlays so original storage is protected.
- `/dev/null` drives are replaced with a temporary 4 KiB raw file.
- A dummy drive slot is used internally for the appliance.

## Protocol Validation
Supports file, ftp, ftps, http, https, iscsi, nbd, rbd, and ssh. Protocol-specific validation covers server count, transport type, path/export syntax, username/secret support, and default NBD port.

## Option Validation
- Format must be alphanumeric plus `-_`.
- Disk label must be alphabetic and at most 20 characters.
- Cache mode is limited to `writeback` or `unsafe`.
- Discard is `disable`, `enable`, or `besteffort`.
- Block size must be 512 or 4096.
- Read-only drives cannot enable discard.

## Public APIs
- `guestfs_impl_add_drive_opts()` is the main add path and only works in `CONFIG` state; hotplugging returns an error.
- `guestfs_impl_add_drive_ro()`, `add_drive_with_if()`, `add_drive_ro_with_if()`, and `add_cdrom()` are compatibility wrappers.
- `guestfs_impl_add_drive_scratch()` creates a temporary raw disk and adds it with unsafe cache mode.
- `guestfs_impl_remove_drive()` reports removed hotplug support.
- Checkpoint/rollback helpers support atomic drive additions.
- `guestfs_impl_debug_drives()` returns textual drive descriptions.
- `guestfs_impl_device_index()` and `guestfs_impl_device_name()` convert between `/dev/sd*` names and drive indexes.

## Filesystem/Storage Relevance
This file is the main host-side model for storage sources presented to the appliance, including protection overlays, remote block protocols, scratch disks, labels, discard behavior, and block size selection.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/drives.c -->