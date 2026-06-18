# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-points.c

## Purpose
`visl-trace-points.c` is the tracepoint instantiation unit for VISL codec-control tracing.

## Important APIs, types, and functions
The file includes `visl.h`, defines `CREATE_TRACE_POINTS`, and includes the FWHT, MPEG-2, VP8, VP9, H.264, HEVC, and AV1 trace headers. This causes the Linux tracepoint framework to generate the concrete tracepoint definitions once.

## Control flow
There is no runtime control flow in this file. Its build-time role is to ensure that `trace_v4l2_ctrl_*()` functions referenced by `visl-dec.c` have storage and metadata.

## State and persistence
No VISL state is owned here. Tracepoint state is managed by the kernel tracing subsystem.

## Dependencies and integration points
It depends on all VISL trace headers and must remain in the module build whenever those trace functions are called. It is the central integration point between declarative trace headers and decoder runtime calls.

## Risks and test signals
The key risk is duplicate or missing tracepoint instantiation if headers are included incorrectly elsewhere. Test signals include successful module link and visible trace events under `/sys/kernel/tracing/events/visl_*_controls`.
