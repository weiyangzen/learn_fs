# sources/distributed-fs/ceph-client/tools/perf/util/compress.h

Purpose: declares compression and decompression helpers for perf data streams with optional gzip/zlib, lzma, and zstd support.

Important APIs/types: gzip decompression/probing under `HAVE_ZLIB_SUPPORT`; lzma stream/file decompression and probing with stubs when disabled; `struct zstd_data`, `zstd_init`, `zstd_fini`, `zstd_compress_stream_to_records`, and `zstd_decompress_stream`.

Control flow: callers compile against common APIs and interpret return values for unsupported builds. Zstd state stores stream pointers and compression level only when zstd is present.

State and persistence: `struct zstd_data` holds per-stream state; file decompression APIs write to caller-provided fds.

Dependencies and integration: optional zstd/zlib/lzma libraries, stdio, sys/types, and Linux compiler annotations. Used by perf data read/write paths.

Risks: stub semantics differ by API: lzma fails with `-1`/false, zstd stubs return zero. The zstd record header callback contract must be followed exactly.

Test signals: build matrix with libraries enabled/disabled; gzip/lzma decompress; zstd record round trips; unsupported fallback paths.
