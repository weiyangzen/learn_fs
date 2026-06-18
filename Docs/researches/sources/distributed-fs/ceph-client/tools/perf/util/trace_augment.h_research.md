# sources/distributed-fs/ceph-client/tools/perf/util/trace_augment.h

## Purpose

`trace_augment.h` declares optional BPF augmentation helpers for syscall tracing.

## Important APIs, Types, and Functions

With `HAVE_BPF_SKEL`, it declares preparation, BPF output creation/setup, PID filtering, map fd retrieval, BPF program lookup by title, unaugmented program lookup, and cleanup. Without BPF skeleton support, inline stubs return `-1`, `0`, or `NULL` as appropriate.

## Control Flow and State

The header is a feature gate; implementation state exists only in BPF-enabled builds.

## Dependencies and Integration Points

It references `struct bpf_program` and `struct evlist`. `perf trace` uses it to attach augmentation programs that enrich syscall enter/exit data.

## Risks and Test Signals

Risks include callers failing to handle disabled support, PID filter no-op semantics in stub builds, and map fd lifetime in real builds. Build tests should cover both feature configurations.
