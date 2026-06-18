# Group Research: group_681_libguestfs_sources_virtualization_libguestfs_daemon_file_c_sources_v_69140fb267d6

Scope: `Docs/research_subset_a.md` includes `sources/virtualization/libguestfs`. This report covers the listed daemon C files only.

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/file.c -->
# File Research: sources/virtualization/libguestfs/daemon/file.c

Implements core file mutation and byte-range I/O daemon actions: `touch`, `rm`, `rm_f`, `chmod`, `chown`, `lchown`, deprecated `write_file`, internal write helpers, `pread`/`pwrite` for files and devices, `zfile`, `filesize`, and `copy_attributes`.

Important behavior:
- Uses `CHROOT_IN/CHROOT_OUT` for guest filesystem paths, while device reads/writes operate directly on device paths.
- `do_touch` first `lstat`s and only permits regular files or non-existent paths, with an acknowledged TOCTOU caveat.
- `pread_fd` rejects negative count/offset and caps reads below `GUESTFS_MESSAGE_MAX`.
- `pwrite_fd` closes before optionally calling `udev_settle` for block-device writes.
- `do_zfile` builds a quoted shell pipeline `zcat|bzcat ... | file -bsL -`.
- `do_copy_attributes` optionally copies mode, ownership, and xattrs, with `all` expanding unspecified optional flags.

Filesystem relevance: this is the daemon’s generic local file/syscall bridge and its direct raw block-device byte I/O path.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/file.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/fill.c -->
# File Research: sources/virtualization/libguestfs/daemon/fill.c

Provides file creation/filling helpers: `do_fill`, `do_fill_pattern`, and `do_fill_dir`.

Important behavior:
- `do_fill` validates byte value `0..255` and non-negative length, then writes BUFSIZ chunks to a chrooted file.
- `do_fill_pattern` requires a non-empty pattern and writes repeated pattern fragments until length is reached.
- `do_fill_dir` creates numbered files `%08d` in a target directory.
- Progress is reported during fill loops.

Filesystem relevance: stress/test utility for allocating data or many dentries inside the guest filesystem.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/fill.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/find.c -->
# File Research: sources/virtualization/libguestfs/daemon/find.c

Implements `do_find0`, a FileOut API returning NUL-separated `find` results.

Important behavior:
- Validates the sysroot-expanded target exists and is a directory.
- Builds a quoted `find <sysrootdir> -print0` shell command.
- Sends the normal reply before streaming results via `send_file_write`.
- Strips the sysroot directory prefix from returned paths.
- Uses `input_to_nul` with `GUESTFS_MAX_CHUNK_SIZE`; overlong path chunks are rejected.

Filesystem relevance: streams recursive directory enumeration from the appliance without materializing the whole result in the protocol reply.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/find.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/fs-min-size.c -->
# File Research: sources/virtualization/libguestfs/daemon/fs-min-size.c

Implements filesystem minimum-size dispatch for shrink planning.

Important behavior:
- `do_vfs_minimum_size` calls `do_vfs_type` and dispatches by filesystem type.
- ext filesystems use `ext_minimum_size(device)`.
- NTFS uses `ntfs_minimum_size(device)`.
- btrfs and xfs require a current mountpoint, found through `do_mountpoints`, then call mountpoint-based helpers.
- Unsupported types return `NOT_SUPPORTED`.

Filesystem relevance: abstracts minimum shrink size across filesystem implementations and highlights which filesystems require mounted state for size probing.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/fs-min-size.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/fsck.c -->
# File Research: sources/virtualization/libguestfs/daemon/fsck.c

Thin wrapper for `fsck`.

Important behavior:
- `do_fsck(fstype, device)` runs `fsck -a -t <fstype> <device>` via `commandr`.
- Returns the fsck process status rather than only success/failure.
- Command execution failure reports captured stderr.

Filesystem relevance: exposes filesystem repair/check exit status through the daemon API.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/fsck.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/fstrim.c -->
# File Research: sources/virtualization/libguestfs/daemon/fstrim.c

Implements discard/TRIM support.

Important behavior:
- `optgroup_fstrim_available` checks for `fstrim`.
- `do_fstrim` validates optional `offset >= 0`, `length > 0`, and `minimumfreeextent > 0`.
- Converts the guest path to `sysroot_path`.
- Calls `sync_disks()` before and after trimming.
- Runs `fstrim` twice as a documented workaround for RHEL-88450.
- Maps “discard operation is not supported” errors to `ENOTSUP`.

Filesystem relevance: bridges mounted filesystem discard support to the backing virtual block device.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/fstrim.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/gdisk.c -->
# File Research: sources/virtualization/libguestfs/daemon/gdisk.c

Small GPT helper using `sgdisk`.

Important behavior:
- `optgroup_gdisk_available` checks for `sgdisk`.
- `do_part_expand_gpt(device)` runs `sgdisk -e <device>`.
- Folds stdout onto stderr for better error reporting.

Filesystem relevance: repairs/expands GPT metadata to the full disk size after virtual disk growth.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/gdisk.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/glob.c -->
# File Research: sources/virtualization/libguestfs/daemon/glob.c

Implements glob expansion inside the guest root.

Important behavior:
- Uses glibc `glob()` under `CHROOT_IN`.
- Defaults to `GLOB_BRACE | GLOB_MARK`.
- Optional `directoryslash=false` removes `GLOB_MARK`.
- `GLOB_NOMATCH` returns an empty list, not an error.
- Returns `glob_t.gl_pathv` directly and relies on caller-side freeing.

Filesystem relevance: expands guest path patterns while keeping lookup scoped through the daemon chroot mechanism.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/glob.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/grep.c -->
# File Research: sources/virtualization/libguestfs/daemon/grep.c

Wraps `grep` and `zgrep` variants.

Important behavior:
- Shared `grep()` helper validates incompatible `extended && fixed`.
- Opens the guest file under `CHROOT_IN`, then copies that fd to command stdin with `COMMAND_FLAG_CHROOT_COPY_FILE_TO_STDIN`.
- Treats grep exit status `1` as “no matches” and returns an empty list.
- Supports API-era aliases: `grep`, `egrep`, `fgrep`, case-insensitive variants, and compressed variants.

Filesystem relevance: content search is performed through host/appliance command execution while file access stays chroot-scoped.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/grep.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/grub.c -->
# File Research: sources/virtualization/libguestfs/daemon/grub.c

Wraps legacy `grub-install`.

Important behavior:
- `optgroup_grub_available` checks for `grub-install`.
- `do_grub_install(root, device)` constructs `--root-directory=<sysroot><root>`.
- Captures stderr and, in verbose mode, stdout.

Filesystem relevance: installs a bootloader into a guest-mounted root and target block device.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/grub.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/guestfsd.c -->
# File Research: sources/virtualization/libguestfs/daemon/guestfsd.c

Daemon entry point and transport setup.

Important behavior:
- Parses daemon flags for channel path, listen mode, network enablement, standalone root mode, test mode, and verbosity.
- Initializes OCaml stubs with `caml_startup`.
- Sets controlled environment: `PATH`, `SHELL`, `LC_ALL=C`, `TERM=dumb`, and default umask.
- Opens virtio-serial channel by default, supports `fd:<n>`, or listens on a Unix socket.
- Sends `GUESTFS_LAUNCH_FLAG` to signal readiness, then enters `main_loop`.
- Provides `shell_quote` and `sysroot_shell_quote` utilities used by shell-pipeline wrappers.

Filesystem relevance: establishes the appliance daemon process, sysroot mode, and protocol channel that all filesystem operations use.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/guestfsd.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/headtail.c -->
# File Research: sources/virtualization/libguestfs/daemon/headtail.c

Wraps `head` and `tail`.

Important behavior:
- Opens the guest path under chroot and pipes fd contents to command stdin.
- Shared helper returns `split_lines(out)`.
- `do_tail_n` maps negative `n` to GNU tail’s `+N` form.

Filesystem relevance: bounded text extraction from guest files without direct full-file reads in daemon code.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/headtail.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/hexdump.c -->
# File Research: sources/virtualization/libguestfs/daemon/hexdump.c

Wraps `hexdump -C`.

Important behavior:
- Opens the guest file under chroot.
- Copies fd to command stdin with `COMMAND_FLAG_CHROOT_COPY_FILE_TO_STDIN`.
- Returns the complete hexdump string.

Filesystem relevance: diagnostic byte-level rendering of guest file contents.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/hexdump.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/hivex.c -->
# File Research: sources/virtualization/libguestfs/daemon/hivex.c

Implements Windows Registry hive access through libhivex.

Important behavior:
- Optional build block under `HAVE_HIVEX`; otherwise emits optgroup unavailable stubs.
- Maintains one global `hive_h *h` per daemon/guestfs handle and closes it with a destructor.
- `do_hivex_open` converts filename via `sysroot_path` and honors optional flags: verbose, debug, write, unsafe.
- Read APIs expose root, node names, children, parents, values, keys, types, raw values, and strings.
- Write APIs commit, add/delete child nodes, and set values.
- `do_hivex_commit` manually validates optional output paths because generator lacks `OptPathname`.

Filesystem relevance: gives structured access to registry hive files inside mounted Windows guests.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/hivex.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/htonl.c -->
# File Research: sources/virtualization/libguestfs/daemon/htonl.c

Compatibility implementations for byte-order conversion functions.

Important behavior:
- Provides `htonl`/`ntohl` when `HAVE_NTOHL` is absent.
- Provides `htons`/`ntohs` when `HAVE_NTOHS` is absent.
- Uses compile-time endian macros and `bswap_32`/`bswap_16`.
- Avoids Windows headers due to conflicting declarations.

Filesystem relevance: protocol portability support, especially for XDR/network-order daemon communication.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/htonl.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/initrd.c -->
# File Research: sources/virtualization/libguestfs/daemon/initrd.c

Lists and extracts files from compressed initrd/cpio archives.

Important behavior:
- `do_initrd_list` runs a quoted `zcat <sysroot path> | cpio --quiet -it` pipeline and returns line-split filenames.
- `do_initrd_cat` extracts one named file into a temporary directory with `cpio --quiet -id`.
- Enforces `GUESTFS_MESSAGE_MAX` before returning extracted file contents.
- Cleans up extracted file and containing temporary directories.
- Uses shell quoting for archive path, temp directory, and requested filename.

Filesystem relevance: inspects boot initramfs contents stored in guest filesystems.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/initrd.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/inotify.c -->
# File Research: sources/virtualization/libguestfs/daemon/inotify.c

Implements optional inotify watch/read APIs.

Important behavior:
- Optional under `HAVE_SYS_INOTIFY_H`.
- Maintains a global nonblocking close-on-exec inotify fd and a 64 MiB static event buffer.
- `do_inotify_init` requires a mounted root and may write `/proc/sys/fs/inotify/max_queued_events`.
- `do_inotify_add_watch` watches `sysroot_path(path)`.
- `do_inotify_read` drains available events, preserves incomplete events in `inotify_buf`, and estimates protocol message space.
- `do_inotify_files` reads all pending events, sorts unique non-empty names through `sort -u`, and returns them.

Filesystem relevance: exposes Linux filesystem event monitoring for guest-root paths during daemon sessions.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/inotify.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/internal.c -->
# File Research: sources/virtualization/libguestfs/daemon/internal.c

Internal daemon-only lifecycle actions.

Important behavior:
- `do_internal_autosync` conditionally calls `do_umount_all` if `autosync_umount` is set, then calls `sync_disks`.
- `do_internal_exit` replies first, then exits successfully; intended for valgrind daemon runs.

Filesystem relevance: final synchronization and unmount behavior before handle shutdown.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/internal.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/is.c -->
# File Research: sources/virtualization/libguestfs/daemon/is.c

Implements simple existence and file-type predicates.

Important behavior:
- Shared `get_mode(path, mode, followsymlinks)` uses `lstat` or `stat` under chroot.
- `ENOENT` and `ENOTDIR` return false, not error.
- Exposes `exists`, `is_chardev`, `is_blockdev`, `is_fifo`, and `is_socket`.
- Optional `followsymlinks` defaults to false unless corresponding optarg bit is set.

Filesystem relevance: guest path metadata classification.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/is.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/journal.c -->
# File Research: sources/virtualization/libguestfs/daemon/journal.c

Implements optional systemd journal access.

Important behavior:
- Optional under `HAVE_SD_JOURNAL`.
- Maintains one global `sd_journal *j` and closes it with a destructor.
- `do_journal_open` opens a journal directory under `sysroot_path`.
- Supports close, next, skip forward/backward, threshold get/set, and realtime timestamp retrieval.
- `do_internal_journal_get` streams current entry fields as length-prefixed big-endian blobs using FileOut.

Filesystem relevance: structured log extraction from guest journal directories.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/journal.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/labels.c -->
# File Research: sources/virtualization/libguestfs/daemon/labels.c

Dispatches filesystem label setting by filesystem type.

Important behavior:
- `do_set_label` obtains filesystem type via `do_vfs_type`.
- ext filesystems use `do_set_e2label`.
- btrfs, FAT variants, NTFS, XFS, and swap map to their helper functions.
- XFS rejects special label `"---"` because that clears labels in `xfs_admin`.
- Unsupported filesystems return `NOT_SUPPORTED`.

Filesystem relevance: central label-setting dispatcher across local filesystem families.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/labels.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/ldm.c -->
# File Research: sources/virtualization/libguestfs/daemon/ldm.c

Wraps `ldmtool` for Windows Logical Disk Manager metadata.

Important behavior:
- `optgroup_ldm_available` checks for `ldmtool`.
- Exposes create/remove all, scan, scan selected devices, diskgroup name/volumes/disks, and volume type/hint/partitions.
- Parses `ldmtool` JSON output with json-c strict and UTF-8 validation.
- Converts JSON arrays of strings and object string fields into daemon protocol return values.
- Handles JSON null-to-empty for volume hints.

Filesystem relevance: discovers and activates Windows dynamic disk volume topology.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/ldm.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/link.c -->
# File Research: sources/virtualization/libguestfs/daemon/link.c

Implements readlink-list and link creation APIs.

Important behavior:
- `do_internal_readlinklist` opens a directory fd under chroot and uses `fstatat`/`readlinkat` for each name.
- Missing/non-symlink/error entries intentionally return empty strings.
- `do_ln` and `do_ln_f` use hard-link syscalls under chroot.
- Symlink creation uses external `ln -s`/`ln -sf` with `--` so targets beginning with `-` are not parsed as options; linkname is sysroot-prefixed.

Filesystem relevance: link metadata and hard/symbolic link creation within guest filesystems.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/link.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/ls.c -->
# File Research: sources/virtualization/libguestfs/daemon/ls.c

Implements directory listing APIs.

Important behavior:
- `do_ls0` streams NUL-terminated entry names through FileOut, excluding `.` and `..`.
- Once streaming begins, errors cancel the FileOut transfer.
- `do_ll` and `do_llz` resolve a chrooted realpath, convert it to sysroot path, then run `ls -la` or `ls -laZ`.

Filesystem relevance: directory enumeration and long-listing views of guest paths.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/ls.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/luks.c -->
# File Research: sources/virtualization/libguestfs/daemon/luks.c

Small cryptsetup/LUKS helper.

Important behavior:
- Optgroup availability is based on cryptsetup support.
- `do_luks_uuid(device)` runs the LUKS UUID query through cryptsetup and trims command output.
- Errors are reported with command stderr.

Filesystem relevance: exposes encrypted block-device metadata used before mounting contained filesystems.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/luks.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/lvm-filter.c -->
# File Research: sources/virtualization/libguestfs/daemon/lvm-filter.c

Manages the daemon’s LVM device filter configuration.

Important behavior:
- Reads `LVM_SYSTEM_DIR` at constructor time, defaulting to `/etc/lvm`.
- Rewrites `lvm.conf` with `filter` and `global_filter`.
- Disables LVM devices-file use when supported by `lvmdevices`/`vgimportdevices`.
- `do_lvm_set_filter` builds allow regexes for exact devices and whole-disk partitions, then rejects everything else.
- Filter changes deactivate VGs, write config, clear cache/rescan, then reactivate.
- `do_lvm_clear_filter` restores allow-all filtering.

Filesystem relevance: constrains LVM discovery to intended block devices, reducing cross-disk contamination in appliance operations.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/lvm-filter.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/lvm.c -->
# File Research: sources/virtualization/libguestfs/daemon/lvm.c

Main LVM2 command wrapper.

Important behavior:
- Checks availability with `prog_exists("lvm")`.
- Lists PVs/VGs through `lvm pvs/vgs`, trims and sorts output, and suppresses `"unknown device"`.
- Creates/removes/resizes/renames PVs, VGs, and LVs using command-vector construction.
- Many mutating operations call `udev_settle`.
- `do_lvm_remove_all` is explicitly destructive and removes LVs, VGs, then PVs.
- UUID and membership APIs use `--unbuffered --noheadings -o <field>`.
- `lv_canonical` maps `/dev/mapper` or `/dev/dm-*` paths to canonical LV names by matching `st_rdev`.
- `do_vgmeta` writes `vgcfgbackup` to a temp file and returns it subject to protocol size limits.
- Includes PV/VG UUID regeneration helpers.

Filesystem relevance: central block-storage volume management layer for LVM-backed guest filesystems.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/lvm.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/md.c -->
# File Research: sources/virtualization/libguestfs/daemon/md.c

Wraps mdadm RAID operations and mdstat parsing.

Important behavior:
- Optgroup availability checks `mdadm`.
- OCaml noalloc helper tests whether a device is a real RAID array via `GET_ARRAY_INFO` when available.
- `do_md_create` validates optional level, chunk alignment, spare count, nrdevices, and missingbitmap invariants.
- Builds `mdadm --create --run` with real devices and `"missing"` placeholders.
- `do_md_stop` runs `mdadm --stop`.
- `do_md_stat` parses `/proc/mdstat` for a named array and returns device/index/flag entries.

Filesystem relevance: manages Linux software RAID devices that can contain filesystems or higher storage layers.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/md.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/mkfs.c -->
# File Research: sources/virtualization/libguestfs/daemon/mkfs.c

Generic filesystem creation wrapper.

Important behavior:
- Uses `mke2fs` directly for ext filesystems and `mkfs -t` for others.
- Adds filesystem-specific flags for ext, NTFS, reiserfs/jfs/xfs, GFS/GFS2, FAT, btrfs, f2fs, and label handling.
- Validates block size as positive power-of-two.
- Maps FAT block size to sectors-per-cluster using `do_blockdev_getss`.
- Rejects unsupported option/type combinations, such as inode size outside ext or sector size outside ufs.
- Detects whether `mkfs.fat` supports `--mbr=n` and caches the result.
- Calls `wipe_device_before_mkfs(device)` before running mkfs.
- `do_mkfs_b` is a compatibility wrapper setting only the blocksize optarg.

Filesystem relevance: core filesystem formatting entry point across many local filesystem tools.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/mkfs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/mknod.c -->
# File Research: sources/virtualization/libguestfs/daemon/mknod.c

Implements special file creation when `mknod` is available.

Important behavior:
- Optional under `HAVE_MKNOD`.
- `do_mknod` rejects negative modes and calls `mknod` under chroot.
- `do_mkfifo`, `do_mknod_b`, and `do_mknod_c` require mode to contain only permission bits, then OR in the file type.
- Uses `makedev(devmajor, devminor)` for block/char nodes.

Filesystem relevance: creates FIFOs and device nodes inside guest filesystems.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/mknod.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/mktemp.c -->
# File Research: sources/virtualization/libguestfs/daemon/mktemp.c

Temporary file and directory creation wrappers.

Important behavior:
- `do_mkdtemp` duplicates the template and calls `mkdtemp` under chroot.
- `do_mktemp` optionally appends a suffix, requiring the original template to end in `X`.
- Uses `mkstemps` under chroot and closes the created fd.
- Returns the generated guest path string.

Filesystem relevance: safe unique-name creation in guest filesystems.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/mktemp.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/modprobe.c -->
# File Research: sources/virtualization/libguestfs/daemon/modprobe.c

Kernel module loading wrapper.

Important behavior:
- Optgroup availability returns false when `/proc/modules` is absent with `ENOENT`.
- Otherwise requires `modprobe` to exist.
- `do_modprobe(module)` runs `modprobe <module>` and returns the process status.

Filesystem relevance: enables loading kernel modules needed for filesystem, block, or device support in the appliance.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/modprobe.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/mount.c -->
# File Research: sources/virtualization/libguestfs/daemon/mount.c

Mount-state inspection and unmount/remount helpers.

Important behavior:
- `is_root_mounted` scans `/proc/mounts` for mounts at or below `sysroot`.
- `is_device_mounted` compares `st_rdev` of the device and mounted fs names under sysroot.
- `do_umount` accepts a path or device, supports optional force/lazy flags, and uses external `umount`.
- `do_mounts` and `do_mountpoints` return mounted devices and optional mountpoints; `/dev/mapper` and `/dev/dm-*` paths are canonicalized through LVM.
- `do_umount_all` finalizes Augeas, hivex, and journal handles, sorts mount paths longest-first, then unmounts.
- `do_mount_loop` mounts a sysroot file with `-o loop`.
- `do_remount` requires explicit `rw` optional arg and remounts ro/rw.
- `do_mkmountpoint` and `do_rmmountpoint` intentionally bypass `NEED_ROOT`.

Filesystem relevance: manages the daemon’s mounted guest filesystem tree and cleanup order.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/mount.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/mountable.c -->
# File Research: sources/virtualization/libguestfs/daemon/mountable.c

Converts internal `mountable_t` values into protocol structs.

Important behavior:
- Allocates `guestfs_int_internal_mountable`.
- Copies type, device string, and volume string.
- Converts null device/volume fields to empty strings.
- Cleans up partial allocations on failure.

Filesystem relevance: diagnostic/introspection bridge for mountable parsing results.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/mountable.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/ntfs.c -->
# File Research: sources/virtualization/libguestfs/daemon/ntfs.c

NTFS-related command wrappers and minimum-size parser.

Important behavior:
- Availability checks for `ntfs-3g.probe` and `ntfsresize`.
- Label get/set use `ntfslabel`.
- `do_ntfs_3g_probe` runs read/write probe and returns its status.
- `do_ntfsresize` validates optional size and force flag, then runs `ntfsresize -P`.
- `ntfs_minimum_size` parses `ntfsresize --info -ff` output, including special handling for full volumes.
- `do_ntfsfix` optionally clears bad sectors with `-b`.
- `do_ntfscat_i` streams an inode via `ntfscat -i`.
- `do_ntfs_chmod` wraps `ntfssecaudit`, optionally recursive.

Filesystem relevance: NTFS metadata, repair, resizing, raw inode extraction, and ACL-mode manipulation.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/ntfs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/ntfsclone.c -->
# File Research: sources/virtualization/libguestfs/daemon/ntfsclone.c

Streams NTFS clone images in and out.

Important behavior:
- `do_ntfsclone_in` receives FileIn data and pipes it to `ntfsclone -O <device> --restore-image -`.
- Uses a temp stderr file so command errors can be reported after pipe failure.
- Handles receive cancellation separately from write errors.
- `do_ntfsclone_out` constructs `ntfsclone -o - --save-image` with optional metadata/rescue/ignore-fs-check/preserve-timestamps/force flags.
- FileOut streaming sends reply first, then chunks stdout, with cancellation on read or process failure.

Filesystem relevance: efficient NTFS image backup/restore over the daemon file-transfer protocol.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/ntfsclone.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/parted.c -->
# File Research: sources/virtualization/libguestfs/daemon/parted.c

Partition table manipulation using `parted` and one `sfdisk` helper.

Important behavior:
- Normalizes supported partition table aliases through `check_parttype`.
- Calls `udev_settle` before and after partition table mutations.
- Implements label creation, partition add/delete/resize, whole-disk single partition creation, boot flag set/get, GPT name set/get, and MBR ID setting.
- Uses `parted -s --` for mutations and `parted -m -s ... unit b print` for parsing.
- `do_part_disk` uses 128-sector alignment and leaves 128 sectors at disk end.
- `print_partition_table` maps unrecognized disk labels to `EINVAL`.
- `get_table_field` parses colon/semicolon-delimited machine output.

Filesystem relevance: block-device partition topology setup for filesystems and virtual disks.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/parted.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/pingdaemon.c -->
# File Research: sources/virtualization/libguestfs/daemon/pingdaemon.c

Minimal liveness endpoint.

Important behavior:
- `do_ping_daemon` returns success without side effects.

Filesystem relevance: no filesystem behavior; used to confirm daemon responsiveness.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/pingdaemon.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/proto.c -->
# File Research: sources/virtualization/libguestfs/daemon/proto.c

Core daemon protocol implementation.

Important behavior:
- `main_loop` reads length-prefixed XDR messages, validates program/version/direction/status, sets global `proc_nr`, `serial`, `progress_hint`, and `optargs_bitmask`, then dispatches.
- Errors are encoded by `send_error` with bounded error message length and errno string mapping.
- `reply` serializes normal replies and converts oversized reply-body encoding failures into daemon errors.
- `receive_file` consumes FileIn chunks, supports library cancellation, and invokes a write callback.
- `cancel_receive` sends cancellation back and drains incoming chunks.
- `send_file_write` sends FileOut chunks and checks for library-side cancellation.
- Progress notifications are rate-limited; pulse mode uses `SIGALRM` and an async-safe prebuilt XDR byte layout when timers/signals exist.

Filesystem relevance: every streamed file, directory, image, and command-output transfer depends on this chunk/cancel/progress machinery.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/proto.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/readdir.c -->
# File Research: sources/virtualization/libguestfs/daemon/readdir.c

Streams rich directory entries.

Important behavior:
- `do_internal_readdir` opens a directory under chroot.
- Encodes `guestfs_int_dirent` records into an XDR buffer up to `GUESTFS_MAX_CHUNK_SIZE`.
- Precomputes maximum encoded record size using a filled `struct dirent`.
- Sends OK reply before streaming and can only cancel after that.
- Uses `d_type` when available, mapping to file type characters; otherwise returns unknown.

Filesystem relevance: efficient structured directory entry enumeration for guest directories.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/readdir.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/rename.c -->
# File Research: sources/virtualization/libguestfs/daemon/rename.c

Simple rename syscall wrapper.

Important behavior:
- `do_rename(oldpath, newpath)` calls `rename` under chroot.
- Reports both source and destination on error.

Filesystem relevance: atomic guest path rename where supported by the underlying filesystem.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/rename.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/rpm-c.c -->
# File Research: sources/virtualization/libguestfs/daemon/rpm-c.c

Lightweight OCaml C bindings for librpm-backed package enumeration.

Important behavior:
- Without `HAVE_LIBRPM`, all entry points raise OCaml failure.
- With librpm, initializes rpm config, creates a transaction set, starts a package iterator, and returns package records to OCaml.
- Disables signature checking when `RPMVSF_MASK_NOSIGNATURES` is available.
- Extracts name, version, release, arch, URL, summary, description, and epoch.
- Converts null string fields to empty strings in the OCaml result.
- Maintains static rpm transaction and iterator until end.

Filesystem relevance: package inventory for RPM-based guests, reading the guest RPM database via librpm context.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/rpm-c.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/rsync.c -->
# File Research: sources/virtualization/libguestfs/daemon/rsync.c

Rsync wrapper for guest-local and remote sync.

Important behavior:
- Optgroup availability checks `rsync`.
- Shared helper builds `rsync` argv with optional `--archive` and `--delete`.
- `do_rsync` sysroot-prefixes both source and destination.
- `do_rsync_in` uses remote source to sysroot destination.
- `do_rsync_out` uses sysroot source to remote destination.

Filesystem relevance: bulk tree synchronization into, out of, or within mounted guest filesystems.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/rsync.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/scrub.c -->
# File Research: sources/virtualization/libguestfs/daemon/scrub.c

Wraps secure overwrite/free-space scrubbing.

Important behavior:
- Optgroup availability checks `scrub`.
- `do_scrub_device` runs `scrub <device>`.
- `do_scrub_file` resolves `sysroot_realpath(file)` and runs `scrub -r`.
- `do_scrub_freespace` sysroot-prefixes a directory and runs `scrub -X`.
- Errors include original guest path/device and command stderr.

Filesystem relevance: destructive data sanitization for devices, files, and free space.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/scrub.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/selinux.c -->
# File Research: sources/virtualization/libguestfs/daemon/selinux.c

Optional SELinux context helpers.

Important behavior:
- Optional under `HAVE_LIBSELINUX`.
- `optgroup_selinux_available` returns true when built with libselinux.
- `optgroup_selinuxrelabel_available` historically checks `setfiles`.
- `do_setcon` calls `setcon` when available.
- `do_getcon` calls `getcon`, duplicates the returned context, then `freecon`s it.

Filesystem relevance: supports SELinux context-sensitive guest operations and relabel workflows.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/selinux.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/sfdisk.c -->
# File Research: sources/virtualization/libguestfs/daemon/sfdisk.c

Legacy `sfdisk` partitioning wrappers.

Important behavior:
- Shared `sfdisk` helper builds a fixed-size shell command string and writes partition lines to stdin.
- Explicitly bounds `extra_flag` and device length before appending to the command buffer.
- After successful `sfdisk`, calls `blockdev --rereadpt` and `udev_settle`.
- Provides full-table, single-partition `-N`, megabyte-unit `-uM`, list, kernel geometry, and disk geometry APIs.
- Query variants use argument-vector `command`.

Filesystem relevance: older partition table creation/query path complementary to `parted.c`.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/sfdisk.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/sh.c -->
# File Research: sources/virtualization/libguestfs/daemon/sh.c

Runs arbitrary commands inside the guest root.

Important behavior:
- Before command execution, bind-mounts `/dev`, `/dev/pts`, `/proc`, `/sys`, and SELinux paths into the sysroot where possible.
- If networking is enabled, bind-mounts appliance `/etc/resolv.conf` read-only over guest `/etc/resolv.conf`, creating/removing a placeholder if needed.
- `do_command` requires a mounted root and non-empty argv, then runs command with `COMMAND_FLAG_DO_CHROOT`.
- Cleanup attributes unmount bind mounts and resolver mount.
- `do_command_lines` splits stdout into lines.
- `do_command_out` streams stdout over FileOut.
- `do_sh`, `do_sh_lines`, and `do_sh_out` execute `/bin/sh -c`.

Filesystem relevance: general-purpose chroot command execution against mounted guest filesystems, with temporary system pseudo-filesystem setup.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/sh.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/sleep.c -->
# File Research: sources/virtualization/libguestfs/daemon/sleep.c

Simple sleep helper.

Important behavior:
- `do_sleep(secs)` calls `sleep(secs)` and always returns success.

Filesystem relevance: no direct filesystem behavior; useful for timing and daemon interaction tests.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/sleep.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/sleuthkit.c -->
# File Research: sources/virtualization/libguestfs/daemon/sleuthkit.c

Wraps Sleuth Kit extraction commands.

Important behavior:
- `do_download_inode` validates non-negative inode and streams `icat -r <device> <inode>`.
- `do_download_blocks` validates start/stop range and streams `blkls`.
- Shared `send_command_output` uses `popen`, sends FileOut reply first, streams chunks, and cancels on read/process errors.
- Optgroup availability checks `icat`.

Filesystem relevance: forensic extraction of inode and block ranges from filesystems without mounting them normally.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/sleuthkit.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/squashfs.c -->
# File Research: sources/virtualization/libguestfs/daemon/squashfs.c

Creates SquashFS images from guest paths and streams them out.

Important behavior:
- Optgroup availability checks `mksquashfs`.
- Converts input path to `sysroot_path`.
- Creates temporary output under `/var/tmp` rather than `/tmp` to avoid tmpfs size limits.
- Builds `mksquashfs <path> <tmpfile> -noappend -root-becomes <path> -wildcards -no-recovery`.
- Supports optional compressor and exclude list via an exclude-from file.
- Streams the resulting image over FileOut and unlinks temp files via cleanup attributes.

Filesystem relevance: packages a guest subtree into a SquashFS filesystem image.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/squashfs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/stat.c -->
# File Research: sources/virtualization/libguestfs/daemon/stat.c

Nanosecond stat/lstat wrappers and batched lstat.

Important behavior:
- `stat_to_statns` maps `struct stat` into `guestfs_int_statns`, including optional block size, block count, and nanosecond fields.
- `do_statns` follows symlinks; `do_lstatns` does not.
- `do_internal_lstatnslist` opens a directory fd and runs `fstatat(..., AT_SYMLINK_NOFOLLOW)` for each name.
- Per-entry failures in the batched API are represented by `st_ino = -1`, not total failure.
- Directory fd close failure is reported as a total error.

Filesystem relevance: high-resolution guest file metadata retrieval.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/stat.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/strings.c -->
# File Research: sources/virtualization/libguestfs/daemon/strings.c

Wraps GNU `strings`.

Important behavior:
- `do_strings_e` validates encoding is one of `sSblBL`.
- Opens the guest file under chroot and copies fd to command stdin.
- Runs `strings -a -e <encoding>`.
- Splits stdout into returned lines.
- `do_strings` defaults to encoding `"s"`.

Filesystem relevance: extracts printable strings from guest files for inspection.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/strings.c -->