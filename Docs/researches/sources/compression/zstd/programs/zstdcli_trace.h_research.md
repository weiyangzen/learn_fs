# sources/compression/zstd/programs/zstdcli_trace.h

## Purpose

This header exposes the minimal trace-control API for the zstd CLI.

## Important APIs, Types, and Functions

`TRACE_enable(char const* filename)` starts logging trace output to a path. `TRACE_finish(void)` shuts tracing down and releases resources. There are no public structs or constants.

## Control Flow, State, and Persistence

The header intentionally hides all trace state. Implementations either enable CSV logging and zstd hook overrides or compile to no-ops when tracing support is disabled.

## Dependencies and Integration Points

It is included by `zstdcli.c` and implemented by `zstdcli_trace.c`.

## Risks and Test Signals

Callers should pair enable with finish through normal cleanup. Tests should verify builds with and without `ZSTD_NOTRACE`, that `--trace` accepts a filename, and that cleanup runs on normal and early-return CLI paths.
