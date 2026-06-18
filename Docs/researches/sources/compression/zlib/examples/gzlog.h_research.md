# sources/compression/zlib/examples/gzlog.h

## Purpose
Public header for the gzlog example library. It defines an opaque `gzlog` object and documents an append-oriented gzip log abstraction that remains decompressible after successful writes and can recover from interrupted operations on the next open.

## APIs, Types, And Functions
The only type is `typedef void gzlog`, intentionally opaque to callers. Declared functions are `gzlog_open(char *path)`, `gzlog_write(gzlog *log, void *data, size_t len)`, `gzlog_compress(gzlog *log)`, and `gzlog_close(gzlog *log)`. Return conventions are documented: open returns `NULL` on error; write/compress return `0`, `-1` for file I/O, `-2` for allocation, or `-3` for invalid log; close returns `0` or `-3`.

## Control Flow Role
This header has no executable flow, but it defines the lifecycle contract: open creates/locks/recovers the log, write appends data and may trigger compression, optional compress forces stored data recompression, and close releases the lock and frees the object. It also documents that `gzlog_open()` followed by `gzlog_close()` is enough to recover a previously interrupted operation.

## State And Persistence
The header documents all persistent side files: `path.gz`, `path.dict`, `path.temp`, `path.add`, `path.lock`, and `path.repairs`. It promises that successful writes leave the gzip file valid and that stored uncompressed data is compressed after about 1 MiB. The opaque handle is freed by `gzlog_close()` and must not be reused.

## Dependencies And Integration
Consumers include this header and link with `gzlog.c` and zlib. The declaration uses `size_t` but does not include `<stddef.h>` itself, so callers must include a header that defines `size_t` before or through their compilation context. The API is C-style and mutable; `path` is a prefix for generated files, not necessarily the final `.gz` path.

## Risks And Test Signals
Risks are mostly contract-level: callers may misunderstand the prefix path, reuse a closed object, pass invalid pointers, or force compression too frequently and harm ratio/performance. Header-level tests are compile tests from a minimal C consumer, invalid-handle return-code checks, and lifecycle tests that validate every documented auxiliary file behavior through `gzlog.c`.
