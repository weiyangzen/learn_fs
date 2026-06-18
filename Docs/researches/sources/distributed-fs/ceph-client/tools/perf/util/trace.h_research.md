# sources/distributed-fs/ceph-client/tools/perf/util/trace.h

## Purpose

`trace.h` declares optional BPF-backed syscall/trace summary support for perf trace.

## Important APIs, Types, and Functions

`enum trace_summary_mode` selects no summary, total summary, per-thread summary, or per-cgroup summary. With `HAVE_BPF_SKEL`, the header declares prepare/start/end/print/cleanup functions. Without BPF skeleton support, inline stubs return failure or no-op.

## Control Flow and State

The header provides build-time feature gating. Runtime code can call the same API and receive `-1`/no-op behavior on unsupported builds.

## Dependencies and Integration Points

It depends only on `FILE` and is consumed by `perf trace` code that wants optional BPF aggregation.

## Risks and Test Signals

Risks include callers assuming BPF support unconditionally or ignoring `trace_prepare_bpf_summary()` failure. Tests should build with and without BPF skeleton support and verify graceful fallback.
