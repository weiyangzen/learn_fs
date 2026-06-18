# sources/compression/zstd/programs/zstdcli_trace.c

## Purpose

This file implements optional zstd CLI trace logging. When `ZSTD_TRACE` is enabled, it overrides weak zstd trace hooks and records compression/decompression metrics as CSV rows.

## Important APIs, Types, and Functions

Public APIs are `TRACE_enable(filename)` and `TRACE_finish()`. Internal state includes `g_traceFile`, `g_mutexInit`, `g_mutex`, and `g_enableTime`. `TRACE_log()` extracts compression level and worker count from trace params and writes algorithm, version, method, mode, level, workers, dictionary size, input/output sizes, duration, ratio, and speed. Hook overrides are `ZSTD_trace_compress_begin/end` and `ZSTD_trace_decompress_begin/end`.

## Control Flow, State, and Persistence

`TRACE_enable()` appends to the target file and writes a CSV header when the path was not already a regular file. It initializes a mutex and starts a relative clock. Begin hooks return nanoseconds since enable; end hooks compute durations and log rows under the mutex. `TRACE_finish()` closes the file and destroys the mutex. In non-trace builds the APIs are no-ops.

## Dependencies and Integration Points

It depends on `timefn`, `util`, zstd static APIs, `zstd_trace.h`, and threading macros. `zstdcli.c` enables it via `--trace`.

## Risks and Test Signals

Risks include trace file open failure silently disabling output, division by compressed size when malformed trace data reports zero, mutex initialization failure, and version mismatch assertions. Tests should cover appending/header behavior, concurrent compression with multiple workers, disabled-trace builds, and CSV content for compress and decompress paths.
