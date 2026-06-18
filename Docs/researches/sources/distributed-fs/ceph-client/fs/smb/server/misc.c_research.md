# sources/distributed-fs/ceph-client/fs/smb/server/misc.c

## Purpose
Implements general ksmbd helper routines for wildcard matching, filename and stream validation, share/path conversion, share name casefolding, directory entry name conversion, and NTFS/Unix time conversion. These helpers are used throughout request handling and VFS integration.

## Important APIs, Types, and Functions
- `match_pattern()` performs case-insensitive matching with `*` and `?` wildcards. It is a compact backtracking matcher and explicitly does not implement DOS wildcard semantics for `DOS_DOT`, `DOS_QM`, or `DOS_STAR`.
- `ksmbd_validate_filename()` rejects ASCII control characters and reserved wildcard/device-like characters through `is_char_allowed()`, returning `-ENOENT` on failure.
- `parse_stream_name()` splits an NTFS alternate data stream suffix from `filename`, validates the stream name, and classifies `$DATA` as `DATA_STREAM` or `$INDEX_ALLOCATION` as `DIR_STREAM`.
- `convert_to_nt_pathname()` converts a kernel `struct path` into a share-relative Windows pathname. It uses `d_path()`, verifies the absolute path has the configured share path prefix, allocates a returned buffer, and converts `/` to `\`.
- `get_nlink()` reports `st->nlink`, subtracting one for directories.
- `ksmbd_conv_path_to_unix()`, `ksmbd_conv_path_to_windows()`, and `ksmbd_strip_last_slash()` mutate path strings in place.
- `ksmbd_casefold_sharename()` lower/casefolds a share name using `utf8_casefold()` when Unicode support and a map are available, falling back to ASCII lowercasing.
- `ksmbd_extract_sharename()` returns the final backslash component of a UNC tree name, casefolded through `ksmbd_casefold_sharename()`.
- `convert_to_unix_name()` joins a share root path with a share-relative SMB path.
- `ksmbd_convert_dir_info_name()` converts directory entry names to UTF-16 using `smbConvertToUTF16()` and returns byte length via `conv_len`.
- `ksmbd_NTtimeToUnix()`, `ksmbd_UnixTimeToNT()`, and `ksmbd_systime()` convert between NT 100ns timestamps since 1601 and Unix `timespec64`.

## Control Flow
Path handling generally normalizes inbound SMB/Windows names to Unix separators, validates illegal characters, joins with a share root, and later converts kernel paths back to NT pathnames for responses. Stream parsing mutates the caller's filename by `strsep()` at the first colon and optionally parses a second colon-delimited stream type. Share lookup extracts and casefolds the UNC share component before configuration lookup. Time conversion uses the constant `NTFS_TIME_OFFSET` and handles negative NT-to-Unix deltas by avoiding signed division on 32-bit architectures.

## State and Persistence
This file keeps no global state. It allocates transient buffers with `KSMBD_DEFAULT_GFP`; callers own returned buffers from conversion and casefold helpers. Path strings passed to separator/strip/stream functions may be modified in place. `ksmbd_systime()` reads wall-clock time but does not persist it.

## Dependencies and Integration Points
The file depends on Linux VFS path APIs, xattrs, Unicode support, NLS conversion, and generic string helpers. It uses `ksmbd_share_config` for share roots and `ksmbd_dir_info`/NLS data for directory enumeration output. It integrates with VFS open/query paths, tree connect share lookup, directory listing, stream handling, and file information responses.

## Risks and Edge Cases
- `parse_stream_name()` calls `strchr(s_name, ':')` after `strsep()` without guarding `s_name` against `NULL`; callers must only invoke it when a colon-delimited stream component exists.
- `convert_to_nt_pathname()` uses simple prefix matching against `share->path`; a share path that is a prefix of another directory name requires upstream path containment guarantees.
- `ksmbd_casefold_sharename()` advances `cf_name` during ASCII lowercasing and returns `cf_name - cf_len`; this relies on `strscpy()` returning copied length and is easy to break if refactored.
- `ksmbd_convert_dir_info_name()` allocates `min(4 * name_len, PATH_MAX)` bytes and then writes two trailing NUL bytes at `conv_len` and `conv_len + 1`; conversion length must remain within allocation.
- Wildcard matching is not full SMB/DOS-compatible, so directory query semantics can diverge from Windows clients.

## Test Signals
Tests should cover wildcard cases with mixed case, trailing `*`, failed backtracking, and unsupported DOS wildcard forms; filenames containing control/reserved characters; alternate stream parsing for valid `$DATA`, `$INDEX_ALLOCATION`, invalid stream types, and missing stream names; share names with Unicode and ASCII casefolding; path conversions at share root and nested files; UTF-16 directory name conversion with long and non-ASCII names; and timestamp round trips before/after 1970 on 32-bit and 64-bit builds.
