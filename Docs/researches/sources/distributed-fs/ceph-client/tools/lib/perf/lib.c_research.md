<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/lib.c -->
# sources/distributed-fs/ceph-client/tools/lib/perf/lib.c

## Purpose
This libperf implementation file provides exact-size read/write helpers used by internal code and defines the global `page_size` variable.

## Important APIs, Types, and Functions
- `unsigned int page_size` is shared state used by mmap sizing.
- Static `ion(bool is_read, int fd, void *buf, size_t n)` loops until exactly `n` bytes are read/written or an error/EOF occurs, retrying `EINTR`.
- `readn(int fd, void *buf, size_t n)` reads exactly `n` bytes.
- `preadn(int fd, void *buf, size_t n, off_t offs)` does positioned exact reads while advancing the offset.
- `writen(int fd, const void *buf, size_t n)` writes exactly `n` bytes.

## Control Flow and State
The helpers repeatedly call `read`, `write`, or `pread`, adjust the remaining byte count and buffer pointer, and return `n` only on full completion. `ion` asserts the final pointer delta with `BUG_ON`.

## Dependencies and Integration Points
It includes libc unistd/errno, Linux `kernel.h`, and `internal/lib.h`. Mmap code depends on `page_size` for mapping length and ring-buffer data offset.

## Risks and Test Signals
Returning `0` or negative values on short/EOF paths means callers must distinguish partial failure from full success. Pointer arithmetic on `void *` relies on compiler extensions used in kernel tooling. There are no direct tests in this subset; coverage is indirect through libperf file and mmap operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/perf/lib.c -->
