# sources/distributed-fs/openafs/src/vol/ntops.c

## Purpose
Implements Windows NT file-operation wrappers for the OpenAFS volume layer. It translates POSIX-like open, read, write, pread, pwrite, seek, truncate, sync, close, unlink, and drive/device operations into Win32 `HANDLE` and `CreateFile`/`ReadFile`/`WriteFile` semantics.

## Important APIs, Types, And Functions
Exported functions are `nt_unlink`, `nt_open`, `nt_close`, `nt_write`, `nt_pwrite`, `nt_read`, `nt_pread`, `nt_size`, `nt_getFileCreationTime`, `nt_setFileCreationTime`, `nt_sync`, `nt_ftruncate`, `nt_fsync`, `nt_seek`, `nt_DevToDrive`, and `nt_DriveToDev`. The file uses delete-on-close, POSIX name semantics, overlapped I/O offsets, `BY_HANDLE_FILE_INFORMATION`, `SetFilePointerEx`, `SetEndOfFile`, and OpenAFS `nterr_nt2unix` error mapping.

## Control Flow
`nt_open` maps POSIX flags to access, share, and create modes before calling `CreateFile`. Sequential reads/writes use `ReadFile`/`WriteFile`; positioned reads/writes populate an `OVERLAPPED` offset without modifying the shared file pointer. EOF during read is treated as a short read, not an error. `nt_sync` opens the raw drive path and flushes it, while `nt_ftruncate` seeks to the target length and calls `SetEndOfFile`.

## State And Persistence
The wrappers persist changes to NTFS files and volume metadata through Win32 handles. They do not own long-lived global state. `nt_unlink` emulates Unix delete-on-last-close, affecting later name reuse semantics until all handles close.

## Dependencies And Integration Points
The implementation is compiled only for `AFS_NT40_ENV` and integrates with `ihandle`, vnode/volume code, NAMEI-on-NT path handling, `partition.c`, and error translation from `afs/errmap_nt.h`. `namei_ops.c` uses NT creation times as hidden metadata through these wrappers.

## Risks And Test Signals
Risks include mismatch between POSIX and mandatory-locking/delete semantics, truncation of large counts to `DWORD`, partial I/O behavior, error mapping drift, and drive-letter assumptions. Tests should cover create/truncate/open flag combinations, positioned I/O beyond 4 GiB offsets, delete while open, drive flush, creation-time metadata round trips, and invalid drive conversion.
