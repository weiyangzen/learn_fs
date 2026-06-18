# sources/distributed-fs/glusterfs/xlators/meta/src/measure-file.c

## Purpose
Implements a writable meta control file that starts and stops latency measurement.

## Important APIs, Types, and Functions
- `measure_file_fill()` prints nothing and returns current size.
- `measure_file_write()` interprets `start` and `stop`, calling `gf_latency_toggle(1)` or `gf_latency_toggle(0)`, and rejects other data with `EINVAL`.
- `measure_file_ops` exposes fill and write.
- `meta_measure_file_hook()` attaches ops.

## Control Flow
Write-only control semantics: users write a command string to toggle latency collection.

## State and Persistence
Mutates process-wide latency measurement state. No file content persists.

## Dependencies and Integration Points
Depends on GlusterFS latency instrumentation and meta writable-file plumbing.

## Risks
Simple string comparison requires exact `start` or `stop`; trailing newline behavior depends on write buffer passed by meta core.

## Test Signals
Write `start`/`stop` and verify latency toggles; invalid writes should fail with `EINVAL`.
