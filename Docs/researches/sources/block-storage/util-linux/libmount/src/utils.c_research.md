# File Research: sources/block-storage/util-linux/libmount/src/utils.c

## Scope

Implements miscellaneous libmount utility routines for safe path probing, filesystem/tag parsing, mount ID lookup, filesystem classification, account parsing, utab path probing, temporary file creation, mountpoint discovery, kernel command-line parsing, and root-device guessing.

## Public And Internal APIs Covered

- File/path helpers: `is_file_empty()`, `mnt_safe_stat()`, `mnt_safe_lstat()`, `mnt_is_path()`, `mnt_chdir_to_parent()`, `mnt_is_readonly()`.
- Tag parsing: `mnt_valid_tagname()`, `mnt_tag_is_valid()`, `mnt_parse_offset()`.
- Mount IDs: `mnt_id_from_fd()`, `mnt_id_from_path()`.
- String encoding: `mnt_mangle()`, `mnt_unmangle()`.
- Filesystem classification: `mnt_fstype_is_pseudofs()`, `mnt_fstype_is_netfs()`, `mnt_statfs_get_fstype()`, `mnt_match_fstype()`.
- Filesystem list handling: `mnt_get_filesystems()`, `mnt_free_filesystems()`.
- User/group/mode parsing: `mnt_get_username()`, `mnt_get_uid()`, `mnt_get_gid()`, `mnt_parse_uid()`, `mnt_parse_gid()`, `mnt_parse_mode()`, `mnt_in_group()`.
- Table path helpers: `mnt_has_regular_mtab()`, `mnt_has_regular_utab()`, `mnt_get_swaps_path()`, `mnt_get_fstab_path()`, `mnt_get_mtab_path()`, `mnt_get_utab_path()`.
- File replacement helper: `mnt_open_uniq_filename()`.
- Mount/root helpers: `mnt_get_mountpoint()`, `mnt_get_kernel_cmdline_option()`, `mnt_guess_system_root()`.

## Control Flow And Behavior

- `safe_stat()` prefers `statx()` with `AT_STATX_DONT_SYNC` and `AT_NO_AUTOMOUNT`, falling back to `fstatat()` or `stat/lstat`; this avoids triggering automounts where possible.
- `mnt_chdir_to_parent()` moves into an absolute path's parent and optionally returns the final component.
- `mnt_is_readonly()` distinguishes permission denial from read-only filesystems using `access()` and, when available, `utimensat()`.
- Mount ID helpers wrap `statx()` `STATX_MNT_ID` and optional `STATX_MNT_ID_UNIQUE`, returning `-ENOSYS` when unsupported.
- Pseudofs detection uses a sorted static array and `bsearch`; network filesystem detection uses explicit string comparisons.
- `mnt_statfs_get_fstype()` maps many Linux statfs magic values to filesystem names.
- `mnt_get_filesystems()` reads `/etc/filesystems` first, respects `*` continuation semantics, and falls back to `/proc/filesystems`, skipping comments and `nodev` entries.
- UID/GID parsers try names first and numeric values when the string begins with a digit.
- `mnt_has_regular_utab()` verifies utab is regular and optionally creates the containing directory/file to test writability.
- `mnt_open_uniq_filename()` builds `<filename>.XXXXXX`, masks group/world permissions while calling `mkstemp_cloexec()`, and returns the fd plus allocated temporary path.
- `mnt_get_mountpoint()` walks upward comparing `st_dev` to find the mountpoint, with a warning in comments that overlay-style filesystems can defeat this traditional method.
- `mnt_get_kernel_cmdline_option()` scans `/proc/cmdline`, stops at ` -- `, and returns the last matching bare option or `name=` value.
- `mnt_guess_system_root()` tries sysfs devno resolution first, then `root=` kernel command-line forms: `major:minor`, hex encoded dev_t, device names, and tags.

## State And Data Structures

- Static pseudofs list must remain sorted.
- Filesystem lists are NULL-terminated dynamically grown arrays.
- Root guessing uses sysfs paths, optional libmount cache, and allocated result strings.

## Dependencies

- libblkid tag parser.
- libmount canonicalization, mangle, match, cache, sysfs, env, and path helpers.
- Linux/POSIX APIs: `statx`, `statfs`, `getpwuid_r`, `getpwnam_r`, `getgrnam_r`, `getgroups`, `mkstemp`, `posix` file operations.

## Risks And Invariants

- `mnt_fstype_is_pseudofs()` relies on the array being sorted for `bsearch`.
- `mnt_get_mountpoint()` uses device-number transitions and is not authoritative for all modern filesystems.
- UID/GID numeric conversion checks both `ULONG_MAX` and cast round-trip to avoid truncation.
- Utab writability checks may create `/run/mount` and the utab file when requested.
- Kernel command-line parsing is intentionally approximate and does not fully emulate kernel parsing.
