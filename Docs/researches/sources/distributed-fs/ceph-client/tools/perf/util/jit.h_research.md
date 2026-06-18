<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/jit.h -->
# sources/distributed-fs/ceph-client/tools/perf/util/jit.h

## Purpose

`jit.h` declares perf inject helpers for JIT dump processing.

## Important APIs, Types, and Functions

`jit_process()` processes one mmap filename that may be a jitdump marker, injects generated JIT ELF mmap records into an output perf data stream, and returns bytes written. `jit_inject_record()` is declared for record-side injection by filename.

## Control Flow

Perf inject/report paths call `jit_process()` when mmap records are seen. The implementation in `jitdump.c` detects `jit-<pid>.dump`, reads records, writes ELF files, emits mmap2 events, and may suppress anonymous JIT code mmaps after a pid is processed.

## State and Persistence Behavior

The interface writes derived ELF files and perf data records through implementation code. It has no state in the header.

## Dependencies and Integration Points

It includes `data.h` and uses perf session, perf data, machine, pid/tid, and byte-count types.

## Risks and Edge Cases

Callers must pass the correct namespace-aware filename and pid/tid from mmap records. Return codes distinguish no-op, processed, and error behavior and must be handled carefully by perf inject.

## Test Signals

Tests should feed jitdump mmap records and verify generated ELF files, mmap2 injection, byte counts, and anonymous-map suppression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/jit.h -->
