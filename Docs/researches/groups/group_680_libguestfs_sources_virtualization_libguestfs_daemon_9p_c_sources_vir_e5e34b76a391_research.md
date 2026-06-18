# Group Research: group_680_libguestfs_sources_virtualization_libguestfs_daemon_9p_c_sources_vir_e5e34b76a391

Scope checked against `Docs/research_subset_a.md`: `sources/virtualization/libguestfs` is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/9p.c -->
# File Research: sources/virtualization/libguestfs/daemon/9p.c

This file preserves daemon RPC entry points for removed 9p support. `do_list_9p` and `do_mount_9p` both immediately return protocol errors stating that 9p support was removed in libguestfs 1.48.

Key points:
- Keeps ABI/API stubs available while preventing use.
- `do_mount_9p` still accepts the historical optional-argument shape but ignores parameters.
- No sysroot, mount, or external command behavior remains.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/9p.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/Makefile.am -->
# File Research: sources/virtualization/libguestfs/daemon/Makefile.am

This is the Automake build manifest for `guestfsd`. It enumerates generated RPC files, daemon C sources, OCaml sources/interfaces, linker inputs, test binaries, and manpage generation.

Key points:
- `BUILT_SOURCES` and `generator_built` capture generated daemon dispatch/stub/action files and generated OCaml interfaces.
- `guestfsd_SOURCES` is the central C daemon source list, including every C file in this group.
- Links C with OCaml output object `camldaemon.o`, gnulib, protocol/utils libraries, and optional feature libraries such as ACL, cap, Augeas, hivex, SELinux, TSK, YARA, JSON-C, PCRE2, rpm.
- Builds OCaml daemon components via `OCAMLFIND ... -output-obj`.
- Defines `daemon_utils_tests`, linking selected C helpers with OCaml test objects and stubs.
- Generates `guestfsd.8` and website HTML from `guestfsd.pod`.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/acl.c -->
# File Research: sources/virtualization/libguestfs/daemon/acl.c

Implements ACL optional-group support when libacl is available.

Key points:
- `optgroup_acl_available` reports support under `HAVE_ACL`.
- `do_acl_get_file` accepts `access` or `default`, calls `acl_get_file` inside the sysroot chroot, converts ACLs to text, duplicates libacl-owned strings, and returns caller-owned memory.
- `do_acl_set_file` parses ACL text with `acl_from_text` and applies it inside the sysroot.
- `do_acl_delete_def_file` removes a directory’s default ACL inside the sysroot.
- Without libacl, `OPTGROUP_ACL_NOT_AVAILABLE` supplies unavailable stubs.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/augeas.c -->
# File Research: sources/virtualization/libguestfs/daemon/augeas.c

Provides the daemon’s Augeas API implementation with one process-global Augeas handle.

Key points:
- Maintains static `augeas *aug`; callers must initialize via `do_aug_init`.
- `aug_read_version` lazily opens a no-load Augeas handle and encodes version as `(major << 16) | (minor << 8) | patch`.
- Destructor `aug_finalize` closes any live handle.
- Implements wrappers for `aug_defvar`, `aug_defnode`, `aug_get`, `aug_set`, `aug_clear`, `aug_insert`, `aug_rm`, `aug_mv`, `aug_match`, `aug_save`, `aug_load`, `aug_ls`, `aug_setm`, `aug_label`, and `aug_transform`.
- Converts Augeas internal strings into caller-owned copies.
- Errors include detailed Augeas message/minor/details through `AUGEAS_ERROR` or local error formatting.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/augeas.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/available.c -->
# File Research: sources/virtualization/libguestfs/daemon/available.c

Implements feature and filesystem availability queries.

Key points:
- `do_internal_feature_available` searches generated `optgroups[]` and returns `0` available, `1` unavailable, `2` unknown group.
- `do_available_all_groups` returns all optional group names.
- `filesystem_available` checks `/proc/filesystems` through `grep`, then optionally tries `modprobe` if Linux module support is available.
- `do_filesystem_available` validates filesystem names as alnum or underscore before probing.
- Designed so the internal probe path avoids `reply_with_error`, allowing callers to control error reporting.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/available.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/base64.c -->
# File Research: sources/virtualization/libguestfs/daemon/base64.c

Implements base64 FileIn/FileOut transfer helpers using the external `base64` utility.

Key points:
- `do_base64_in` receives uploaded base64 data and pipes it into `base64 -d -i > /sysroot/path`.
- Uses `sysroot_shell_quote` for destination quoting and `receive_file` for streaming input.
- Cancels input transfer correctly on command setup or write failure.
- `do_base64_out` verifies the target exists and is not a directory, then streams `base64 file` output to the client.
- Once FileOut reply is sent, later errors can only cancel the transfer via `send_file_end(1)`.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/base64.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/blkdiscard.c -->
# File Research: sources/virtualization/libguestfs/daemon/blkdiscard.c

Wraps Linux block discard ioctls when available.

Key points:
- `do_blkdiscard` gets the full device size via `do_blockdev_getsize64`, opens the device writable, and issues `BLKDISCARD` over the full byte range.
- `do_blkdiscardzeroes` opens the device read-only and returns the boolean result of `BLKDISCARDZEROES`.
- Optional groups are only available when the relevant ioctl macros are defined.
- Comments intentionally defer sysfs discard-limit probing because virtio-scsi usually supports arbitrary discards.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/blkdiscard.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/blkid.c -->
# File Research: sources/virtualization/libguestfs/daemon/blkid.c

Provides blkid-backed filesystem metadata queries.

Key points:
- `get_blkid_tag` runs `blkid -c /dev/null -o value -s TAG device`, treats exit status `2` as “tag not found,” and trims trailing newline.
- `do_vfs_label` delegates to Btrfs or NTFS label helpers when appropriate, otherwise uses blkid `LABEL`.
- `do_vfs_uuid` uses blkid `UUID`.
- `do_blkid` probes once whether blkid supports `-p` and `-i`.
- Modern path parses `blkid -p -i -o export` into alternating key/value strings; fallback returns only `TYPE`, `LABEL`, and `UUID`.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/blkid.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/blockdev.c -->
# File Research: sources/virtualization/libguestfs/daemon/blockdev.c

Centralizes wrappers around the external `blockdev` command.

Key points:
- `call_blockdev` runs `udev_settle()` before every blockdev invocation to avoid udev/blkid races after prior writes.
- Handles commands with optional integer arguments and optional numeric stdout parsing.
- Exposes set/get read-only, sector size, block size, total sectors, byte size, flush buffers, and reread partition table.
- `do_blockdev_setbsz` is intentionally a no-op due to historical bug compatibility.
- `do_blockdev_setra` rejects negative readahead sectors.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/blockdev.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/btrfs.c -->
# File Research: sources/virtualization/libguestfs/daemon/btrfs.c

Large Btrfs daemon adapter. It wraps `btrfs`, `mkfs.btrfs`, `btrfsck`, `btrfstune`, and `btrfs-image`, validates optional arguments, and parses selected text outputs into libguestfs structs or key/value lists.

Key points:
- Optional group is available in test mode, or when the `btrfs` program exists and kernel btrfs filesystem support is available.
- Implements label get/set, filesystem resize, mkfs, subvolume snapshot/create/delete/show/set-default, sync, balance start/status/pause/cancel/resume, device add/delete, fsck, quota/qgroup operations, scrub start/cancel/resume/full/status, defragment, rescue chunk/super recover, btrfstune options, image, replace, filesystem show, and minimum-size query.
- Uses `sysroot_path` for guest filesystem paths and raw device paths for device operations.
- Mountable-based quota helpers temporarily mount Btrfs devices/subvolumes under `/tmp/btrfs.XXXXXX`, run commands, then unmount and remove the temporary mountpoint.
- Contains compatibility probes for `btrfs device add --force`, `btrfstune -u/-U`, `btrfs qgroup show --raw`, and `btrfs inspect-internal min-dev-size`.
- Parses Btrfs text output carefully for subvolume show, qgroup show, balance status, scrub status, and filesystem show, with explicit truncated/unrecognized-output errors.
- Uses PCRE2 for balance status state parsing.
- `btrfs_minimum_size` requires btrfs-progs support for `inspect-internal min-dev-size`; otherwise returns `ENOTSUP`.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/btrfs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/cap.c -->
# File Research: sources/virtualization/libguestfs/daemon/cap.c

Implements Linux file capability get/set support when libcap is available.

Key points:
- `optgroup_linuxcaps_available` reports availability under `HAVE_CAP`.
- `do_cap_get_file` calls `cap_get_file` inside the sysroot; `ENODATA` is normalized to an empty string.
- Capability text returned by libcap is duplicated before `cap_free`.
- `do_cap_set_file` parses text via `cap_from_text` and applies it inside the sysroot.
- Without libcap, `OPTGROUP_LINUXCAPS_NOT_AVAILABLE` is used.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/cap.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/checksum.c -->
# File Research: sources/virtualization/libguestfs/daemon/checksum.c

Implements checksum APIs for files, devices, and directory trees.

Key points:
- Maps checksum names to external programs: `cksum`, `md5sum`, `sha*sum`, `gostsum`, `gost12sum`.
- `checksum` streams an already-open fd to the program using `COMMAND_FLAG_CHROOT_COPY_FILE_TO_STDIN`.
- `do_checksum` opens a sysroot file inside chroot; `do_checksum_device` opens a raw device.
- `do_checksums_out` validates the path is a directory, then streams `find -type f -print0 | xargs -0 <sum-program>` from that sysroot directory.
- Uses pulse-mode progress for potentially long single-file/device checksum work.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/checksum.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/cleanups.c -->
# File Research: sources/virtualization/libguestfs/daemon/cleanups.c

Small cleanup helper file for GCC cleanup attributes used in the daemon.

Key points:
- `cleanup_aug_close` closes non-null Augeas handles.
- `cleanup_free_stringsbuf` frees daemon `stringsbuf` instances.
- Supports macros declared in `daemon.h`: `CLEANUP_AUG_CLOSE` and `CLEANUP_FREE_STRINGSBUF`.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/cleanups.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/clevis-luks.c -->
# File Research: sources/virtualization/libguestfs/daemon/clevis-luks.c

Wraps Clevis LUKS unlock support.

Key points:
- Optional group availability checks for `clevis-luks-unlock`.
- `do_clevis_luks_unlock` executes `clevis luks unlock -d <device> -n <mapname>`.
- Errors include both device and mapper name.
- Calls `udev_settle()` after successful unlock so new mapper nodes are ready.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/clevis-luks.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/cmp.c -->
# File Research: sources/virtualization/libguestfs/daemon/cmp.c

Implements file equality testing.

Key points:
- `do_equal` maps both guest paths through `sysroot_path`.
- Runs `cmp -s file1 file2`.
- Returns boolean true for exit `0`, false for exit `1`, and daemon error for execution failure or unexpected status.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/cmp.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/command.c -->
# File Research: sources/virtualization/libguestfs/daemon/command.c

Core daemon helper for executing external commands and capturing output.

Key points:
- Provides variadic and argv-based wrappers: `commandf`, `commandrf`, `commandvf`, `commandrvf`.
- Uses `fork`, `execvp`, pipes, and `select` rather than shell expansion for normal command execution.
- Can capture stdout and/or stderr into null-terminated buffers; trims trailing newlines from stderr.
- `COMMAND_FLAG_FOLD_STDOUT_ON_STDERR` supports tools that report errors on stdout.
- `COMMAND_FLAG_CHROOT_COPY_FILE_TO_STDIN` lets a chrooted fd be fed to command stdin, used for guest file checksums/hexdumps.
- `COMMAND_FLAG_DO_CHROOT` chroots the child into `sysroot` before execution.
- Resets SIGALRM/SIGPIPE in the child, sets stdin to `/dev/null` unless forwarding a file descriptor, and always waits for child status.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/command.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/command.h -->
# File Research: sources/virtualization/libguestfs/daemon/command.h

Header for daemon external-command helpers.

Key points:
- Defines convenience macros `command`, `commandr`, `commandv`, and `commandrv`.
- Declares command flags and fd mask.
- Declares the four implementation functions.
- Variadic declarations use `__attribute__((sentinel))` to enforce null termination.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/command.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/compress.c -->
# File Research: sources/virtualization/libguestfs/daemon/compress.c

Implements compressed FileOut streaming for files and devices.

Key points:
- Supports `compress`, `gzip`, `bzip2`, `xz`, and `lzop`, checking each external program exists before use.
- Validates compression levels according to tool-specific ranges.
- `do_compress_out` compresses a sysroot file; `do_compress_device_out` compresses raw device input using shell redirection.
- Streams command stdout to the client in `GUESTFS_MAX_CHUNK_SIZE` chunks.
- After sending the FileOut reply, subsequent read/pclose errors are reported by transfer cancellation.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/copy.c -->
# File Research: sources/virtualization/libguestfs/daemon/copy.c

Implements in-process byte-copy APIs for file/device combinations.

Key points:
- Shared `copy` helper handles source/destination opening, optional source offset, destination offset, size limit, sparse-hole creation, and progress.
- Negative offsets and sizes are rejected when specified.
- Sparse mode seeks over all-zero buffers instead of writing them.
- Unlimited-size copies use pulse-mode progress; fixed-size copies report position/total.
- Supports device-to-device, device-to-file, file-to-device, and file-to-file.
- File destinations can append or truncate; append is rejected for device destinations.
- File-to-file deletes the destination on failure to avoid leaving partial created files.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/copy.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/cpio.c -->
# File Research: sources/virtualization/libguestfs/daemon/cpio.c

Implements cpio archive streaming from a guest directory.

Key points:
- `do_cpio_out` validates the sysroot path exists and is a directory.
- Optional format is limited to `newc` or `crc`; default is `newc`.
- Runs `cd <dir> && find -print0 | cpio -0 -o -H <format> --quiet`.
- Streams archive bytes as FileOut chunks.
- Uses transfer cancellation for errors after the FileOut reply.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/cpio.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/cpmv.c -->
# File Research: sources/virtualization/libguestfs/daemon/cpmv.c

Implements simple `cp`, `cp -a`, `cp -rP`, and `mv` wrappers.

Key points:
- Guest paths are converted to sysroot paths before invoking external commands.
- `cpmv_cmd` centralizes command construction and error handling.
- Uses pulse-mode progress around external copy/move commands.
- `do_cp`, `do_cp_a`, `do_cp_r`, and `do_mv` differ only by command/flags.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/cpmv.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/daemon-c.c -->
# File Research: sources/virtualization/libguestfs/daemon/daemon-c.c

C/OCaml bridge helpers for the daemon.

Key points:
- `guestfs_int_daemon_exn_to_reply_with_error` maps OCaml exceptions to daemon protocol errors, including Unix errors, `Failure`, `Sys_error`, `Invalid_argument`, Augeas errors, and PCRE errors.
- Converts C `mountable_t` into OCaml `Mountable.t` representation.
- Converts C string arrays to OCaml lists.
- Converts OCaml string lists, mountables, mountable lists, and hashtable-style association lists back to C return arrays.
- Isolated from `daemon.h` so most C files do not include OCaml runtime headers.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/daemon-c.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/daemon-c.h -->
# File Research: sources/virtualization/libguestfs/daemon/daemon-c.h

Header for C/OCaml bridge functions.

Key points:
- Includes `daemon.h` plus OCaml `mlvalues.h`.
- Declares exception translation, mountable conversion, string-list conversion, and hashtable return conversion helpers.
- Kept separate from `daemon.h` to avoid exposing OCaml headers across the daemon.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/daemon-c.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/daemon-utils-tests-stubs.c -->
# File Research: sources/virtualization/libguestfs/daemon/daemon-utils-tests-stubs.c

Test-only stubs for linking daemon utility tests without full daemon dependencies.

Key points:
- Stubs `device_name_translation`, `reply_with_error_errno`, and `reply_with_perror_errno`.
- Each stub is `noreturn` and aborts if unexpectedly called.
- Lets `daemon_utils_tests` link selected helper files without pulling protocol/device translation machinery.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/daemon-utils-tests-stubs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/daemon.h -->
# File Research: sources/virtualization/libguestfs/daemon/daemon.h

Main shared header for C daemon modules.

Key points:
- Declares global daemon state, sysroot helpers, xread/xwrite, stringsbuf utilities, mountable handling, protocol reply functions, FileIn/FileOut transfer functions, progress APIs, and many cross-file helper APIs.
- Defines `mountable_t` and `stringsbuf`.
- Declares optional group table structure and generated dispatch interfaces.
- Provides `NEED_ROOT`, `ABS_PATH`, `CHROOT_IN`, and `CHROOT_OUT` macros.
- Error macros normalize protocol replies and unavailable feature reporting.
- Exposes filesystem-specific helpers used across modules, including ext, Btrfs, XFS, NTFS, swap, blkid, LVM, xattrs, debug-bmap, Augeas, hivex, and journal finalizers.
- Documents important chroot constraints: match enter/exit paths, keep cwd `/`, use absolute paths, and preserve `errno`.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/daemon.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/daemon_config.ml.in -->
# File Research: sources/virtualization/libguestfs/daemon/daemon_config.ml.in

Configure-time OCaml template for daemon configuration.

Key points:
- Defines `hivex_flag_unsafe` from `@HIVEX_OPEN_UNSAFE_FLAG@`.
- Used by the OCaml daemon/inspection code after configure substitution.
- No runtime logic beyond exposing the configured constant.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/daemon_config.ml.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/dd.c -->
# File Research: sources/virtualization/libguestfs/daemon/dd.c

Implements dd-style whole-copy and fixed-size copy APIs.

Key points:
- `do_dd` builds `if=` and `of=` arguments for raw devices or sysroot files and invokes `dd bs=1024K`.
- `do_copy_size` copies exactly `ssize` bytes in-process, supporting file/device source and destination.
- File destinations are created/truncated; device destinations are opened writable.
- Reports progress during fixed-size copy.
- Detects short input and read/write/close errors.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/dd.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/debug-bmap.c -->
# File Research: sources/virtualization/libguestfs/daemon/debug-bmap.c

Interim debug APIs for virt-bmap-style cache/read mapping experiments.

Key points:
- Maintains static open file descriptor or directory handle prepared by `debug_bmap_file` or `debug_bmap_device`.
- Destructor closes any leftover fd/dir.
- `bmap_prepare` stats and opens either a directory or file/device, using sequential/no-reuse fadvise for regular reads.
- `debug_bmap` drops caches, reads the prepared file/device fully or iterates the prepared directory, then closes resources.
- Returns `"ok"` on successful prepare/read.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/debug-bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/debug.c -->
# File Research: sources/virtualization/libguestfs/daemon/debug.c

Implements the unstable internal `debug` command surface.

Key points:
- Dispatches subcommands such as `help`, `binaries`, `bmap`, `core_pattern`, `device_speed`, `env`, `error`, `fds`, `ldd`, `ls`, `ll`, `print`, `progress`, `qtrace`, `segv`, `setenv`, `sh`, and `spew`.
- Exposes appliance internals including open fds, environment, executable inventory, ldd output, shell execution outside guest chroot, and file listings.
- Provides test hooks for long errors, progress messages, debug output volume, core dumps, intentional trap crashes, qtrace read patterns, and device speed benchmarking.
- `do_debug_upload` and `do_internal_upload` accept FileIn uploads to arbitrary appliance paths, not guest sysroot paths.
- `do_internal_rhbz914931` is a regression crash path during FileIn receive.
- Not stable ABI; comments explicitly direct users to source for behavior.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/device-name-translation.c -->
# File Research: sources/virtualization/libguestfs/daemon/device-name-translation.c

Implements stable public device-name translation for daemon block device paths.

Key points:
- At startup, `device_name_translation_init` caches non-partition `/dev/disk/by-path` symlinks, sorted by `ls -1v`, excluding the root appliance device.
- Translates public `/dev/sdX`, `/dev/hdX`, and `/dev/vdX`-style names to actual kernel device names using drive index mapping.
- Leaves MD, LVM, mapper, and dm paths untranslated.
- Verifies translated devices are openable; falls back from `/dev/sd*` to `/dev/vd*`, `/dev/hd*`, and `/dev/ubd*` variants when needed.
- `reverse_device_name_translation` maps cached real devices back to canonical `/dev/sdX` names.
- Also reverses `btrfsvol:/dev/.../subvol` descriptors.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/device-name-translation.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/devsparts.c -->
# File Research: sources/virtualization/libguestfs/daemon/devsparts.c

Implements listing of libguestfs disk labels.

Key points:
- Reads `/dev/disk/guestfs`.
- Missing directory is treated as an empty list, usually meaning no labels.
- For each non-dot entry, resolves the symlink with `realpath`.
- Returns alternating label and raw device path strings.
- Carefully handles directory close and `readdir` errors.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/devsparts.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/df.c -->
# File Research: sources/virtualization/libguestfs/daemon/df.c

Wraps `df` and `df -h`.

Key points:
- Both `do_df` and `do_df_h` require a root filesystem mounted via `NEED_ROOT`.
- Runs external `df` in the appliance context.
- Returns command stdout directly to caller.
- Errors are propagated from captured stderr.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/df.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/dir.c -->
# File Research: sources/virtualization/libguestfs/daemon/dir.c

Implements directory creation/removal APIs.

Key points:
- `do_rmdir`, `do_mkdir`, and `do_mkdir_mode` call libc operations inside sysroot chroot.
- `do_rm_rf` blocks removing `/`, then runs `rm -rf` on the sysroot path.
- `do_mkdir_mode` rejects negative modes.
- `recursive_mkdir` implements mkdir-p semantics and distinguishes existing non-directory path components.
- `do_mkdir_p` runs recursive creation inside chroot and maps `-2` to a clear “path element was not a directory” error.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/dmesg.c -->
# File Research: sources/virtualization/libguestfs/daemon/dmesg.c

Simple wrapper for appliance kernel log output.

Key points:
- `do_dmesg` runs external `dmesg`.
- Returns stdout as caller-owned string.
- Captured stderr is used for daemon error reply on failure.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/dmesg.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/dropcaches.c -->
# File Research: sources/virtualization/libguestfs/daemon/dropcaches.c

Implements Linux page/cache dropping.

Key points:
- Calls `sync_disks()` first.
- Writes the requested integer to `/proc/sys/vm/drop_caches`.
- Used by debug/bmap/qtrace paths to force cache effects before reads.
- Reports sync/open/write-close failures through daemon errors.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/dropcaches.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/du.c -->
# File Research: sources/virtualization/libguestfs/daemon/du.c

Wraps `du -s` for guest paths.

Key points:
- Converts guest path through `sysroot_path`.
- Runs `du -s <path>` with pulse-mode progress.
- Parses the leading integer from stdout as an `int64_t`.
- Reports parsing failure if command output does not start with a number.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/du.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/echo-daemon.c -->
# File Research: sources/virtualization/libguestfs/daemon/echo-daemon.c

Implements daemon-side echo.

Key points:
- `do_echo_daemon` joins argv strings with spaces using `guestfs_int_join_strings`.
- Returns the joined string.
- Only failure path is allocation failure.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/echo-daemon.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/ext2.c -->
# File Research: sources/virtualization/libguestfs/daemon/ext2.c

Large ext2/ext3/ext4 daemon adapter for e2fsprogs-backed operations.

Key points:
- Recognizes `ext2`, `ext3`, and `ext4` via `fstype_is_extfs`.
- Parses `tune2fs -l` output into alternating key/value strings, normalizing `<none>`, `<not available>`, and `(none)` to empty.
- Implements e2 label/UUID get/set, resize variants, minimum-size query, fsck, external journal creation/use, general `tune2fs`, ext attributes, generation get/set, full `mke2fs`, and `mklost+found`.
- Runs `e2fsck -f` before resize when the target filesystem is not mounted.
- `ext_minimum_size` parses `resize2fs -P -f` block count, retrieves block size from `tune2fs`, checks overflow, and returns bytes.
- `do_e2fsck` enforces mutual exclusion among `correct`, `forceall`, and `forceno`; accepts e2fsck exit 0 or 1 only.
- Label length is limited to `EXT2_LABEL_MAX` bytes.
- `do_mke2fs` maps a large optional-argument surface into `mke2fs` flags and validates non-negative numeric options.
- Journal device optional argument manually performs device-name translation when needed.
- File attributes are validated for allowed ASCII letters, duplicates, and chattr-reserved letters before invoking `chattr`.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/ext2.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/f2fs.c -->
# File Research: sources/virtualization/libguestfs/daemon/f2fs.c

Implements minimal f2fs expansion support.

Key points:
- Optional group availability checks for `resize.f2fs`.
- `do_f2fs_expand` runs `resize.f2fs <device>`.
- Uses `COMMAND_FLAG_FOLD_STDOUT_ON_STDERR` because tool output/error behavior is command-oriented.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/f2fs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/daemon/fallocate.c -->
# File Research: sources/virtualization/libguestfs/daemon/fallocate.c

Implements file allocation APIs.

Key points:
- `do_fallocate` rejects negative 32-bit length and delegates to `do_fallocate64`.
- `do_fallocate64` opens/truncates a sysroot file for writing.
- Uses `posix_fallocate` when available.
- Fallback writes zero-filled buffers until requested length is reached.
- Reports open, allocation/write, and close errors.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/daemon/fallocate.c -->