# sources/distributed-fs/openafs/src/tools/dumpscan/xf_files.c

## Purpose
Implements concrete `XFILE` backends for local Unix files, existing `FILE *` streams, file descriptors, and standard input/output. It lets dumpscan code access ordinary files through the same `XFILE` interface used for profile wrappers, Rx calls, and volume dump streams.

## Important APIs, Types, And Functions
Public entry points are `xfopen_path`, `xfopen_FILE`, `xfopen_fd`, `xfon_path`, `xfon_fd`, and `xfon_stdio`. Static backend methods include `xf_FILE_do_read`, `xf_FILE_do_write`, `xf_FILE_do_tell`, `xf_FILE_do_seek`, `xf_FILE_do_skip`, `xf_FILE_do_close`, and `prepare`. The `O_MODE_MASK` macro limits mode handling to `O_RDONLY`, `O_WRONLY`, and `O_RDWR`.

## Control Flow
`xfopen_path` rejects write-only mode, opens a path with `open`, wraps the descriptor with `fdopen`, and calls `prepare`. `xfopen_FILE` and `xfopen_fd` do the same preparation for existing handles. `prepare` zeros the `XFILE`, installs stdio callbacks, marks writability for read/write mode, and enables seek/skip only for regular and block files detected by `fstat`. The concrete callbacks map `fread`, `fwrite`, `ftell`, `fseek`, and `fclose` to xfile return conventions.

## State And Persistence
The file stores no global state. Per-open state is the `FILE *` in `XFILE.refcon`; `xfclose` via the backend closes that stream. Disk state is whatever path or descriptor the caller opened, and `xfon_stdio` maps read mode to `stdin` and write/read mode to `stdout`.

## Dependencies And Integration Points
It depends on POSIX `open`, `close`, `fstat`, stdio, and xfile error constants. `xfiles.c` registers `xfon_path` under `FILE`, `xfon_fd` under `FD`, and uses `xfon_stdio` when the open name is `-`.

## Risks And Test Signals
The comments note missing handling for short/interrupted stdio reads and writes; `fread(buf, count, 1)` treats partial reads as EOF/error. Large offsets are squeezed through `off_t` via `get64`, so platform offset width matters. Tests should cover regular files, pipes/nonseekable input, block/regular seek detection, descriptor ownership after close, rejected `O_WRONLY`, stdin/stdout mode mapping, EOF behavior, and passthrough interactions through the higher-level `xfread`.
