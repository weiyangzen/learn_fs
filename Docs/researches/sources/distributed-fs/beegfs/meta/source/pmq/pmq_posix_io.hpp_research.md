## sources/distributed-fs/beegfs/meta/source/pmq/pmq_posix_io.hpp

Purpose: header-only POSIX I/O helpers for PMQ file opening and full-length read/write loops. It centralizes error logging and regular-file checks around low-level syscalls.

Important APIs: `pmq_open_dir` opens directories with `O_RDONLY | O_DIRECTORY`. `pmq_check_regular_file` validates `fstat` and `S_ISREG`. `pmq_openat_regular_existing` opens an existing regular file without creation flags. `pmq_openat_regular_create` creates with `O_CREAT | O_EXCL`. `assert_sane_size` guards syscall sizes against `ssize_t` overflow. `pmq_write_all`, `pmq_pwrite_all`, `pmq_read_all`, and `pmq_pread_all` loop until the full slice is transferred.

Control flow: PMQ init and persistence use these helpers for `state.dat`, `wal.dat`, and `chunks.dat`. On syscall failure they log with PMQ errno-aware logging and preserve `errno` for callers where needed.

State and persistence behavior: this file performs no high-level persistence decisions but directly writes and reads PMQ serialized state and chunk/slot data. Full-transfer loops are critical for avoiding partial durable records.

Dependencies and integration points: depends on POSIX open/fstat/read/write/pread/pwrite and `pmq_logging.hpp`. It consumes `Untyped_Slice` from `pmq_base.hpp` through included logging/base headers.

Risks: read helpers do not treat zero-byte reads as errors inside a non-empty request, so an unexpected EOF can spin because the slice does not advance. Write helpers similarly do not explicitly handle zero-byte writes. Creation helper relies on `O_EXCL` instead of validating regular-file type afterward.

Test signals: short read/write injection, EOF during fixed-size read, symlink/directory open attempts, errno preservation, and files larger than `SSIZE_MAX` should be covered with fakes or controlled temp files.
