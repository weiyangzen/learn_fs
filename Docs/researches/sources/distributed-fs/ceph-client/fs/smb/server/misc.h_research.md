# sources/distributed-fs/ceph-client/fs/smb/server/misc.h

## Purpose
Declares the shared utility API implemented by `misc.c` and the procfs helper API used by ksmbd diagnostics. It also exposes constants for directory information alignment and NTFS timestamp conversion.

## Important APIs, Types, and Functions
- Path/name helpers: `match_pattern()`, `ksmbd_validate_filename()`, `parse_stream_name()`, `convert_to_nt_pathname()`, `ksmbd_conv_path_to_unix()`, `ksmbd_strip_last_slash()`, `ksmbd_conv_path_to_windows()`, `ksmbd_casefold_sharename()`, `ksmbd_extract_sharename()`, and `convert_to_unix_name()`.
- Directory info conversion: `KSMBD_DIR_INFO_ALIGNMENT`, forward-declared `struct ksmbd_dir_info`, and `ksmbd_convert_dir_info_name()`.
- Time conversion: `NTFS_TIME_OFFSET`, `ksmbd_NTtimeToUnix()`, `ksmbd_UnixTimeToNT()`, and `ksmbd_systime()`.
- Procfs support under `CONFIG_PROC_FS`: `struct ksmbd_const_name`, initialization/cleanup/reset helpers, `ksmbd_proc_create()`, and formatting helpers `ksmbd_proc_show_flag_names()` and `ksmbd_proc_show_const_name()`.
- No-op inline procfs stubs are provided when procfs is disabled.

## Control Flow
Callers include this header to access path, name, time, and procfs helpers without coupling to implementation files. Conditional compilation keeps procfs users source-compatible even when procfs support is absent.

## State and Persistence
The header declares no state directly. The procfs declarations refer to runtime proc entries and counters maintained elsewhere. Path/time helpers return caller-owned buffers or values and do not persist data.

## Dependencies and Integration Points
The header depends on procfs declarations only when configured and forward declares most ksmbd/VFS structures to avoid heavy includes. It integrates with share management, VFS operations, directory enumeration, server/proc initialization, and session reporting.

## Risks and Edge Cases
- Callers must honor ownership of returned allocated strings and must not pass immutable strings to in-place path mutators.
- Procfs formatting helpers are declared here but implemented outside `misc.c` in this tree, so build linkage depends on the procfs/session implementation being present when `CONFIG_PROC_FS` is enabled.
- `NTFS_TIME_OFFSET` is a raw arithmetic macro; changes to timestamp units must be kept synchronized with both conversion functions.

## Test Signals
Build both with and without `CONFIG_PROC_FS`; compile users of all forward-declared types; run path/name/time tests described for `misc.c`; and verify procfs helpers link and emit expected names in session/cache/server diagnostic files.
