# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-av1.h

## Purpose
`visl-trace-av1.h` defines Linux tracepoints for AV1 stateless V4L2 controls submitted to VISL.

## Important APIs, types, and functions
The header sets `TRACE_SYSTEM` to `visl_av1_controls` and declares event classes for `v4l2_ctrl_av1_sequence`, `v4l2_ctrl_av1_tile_group_entry`, `v4l2_ctrl_av1_frame`, and `v4l2_ctrl_av1_film_grain`. Each event copies the entire control struct into the trace entry and prints important scalar fields, flags, and arrays with `__print_flags()` and `__print_array()`.

The frame trace covers tile layout, quantization, super-resolution, segmentation, loop filter, CDEF, skip mode, restoration, frame flags, dimensions, frame IDs, buffer removal time, order hints, reference timestamps, reference indices, and refresh flags. The film-grain trace covers grain flags, points, AR coefficients, scaling, and chroma multipliers/offsets.

## Control flow
The header contributes tracepoint definitions that are instantiated by `visl-trace-points.c`. `visl_trace_ctrls()` in `visl-dec.c` calls the generated `trace_v4l2_ctrl_av1_*()` functions for the current AV1 request.

## State and persistence
Trace events copy control data at the time of tracing. They do not modify decoder state and are retained only by the kernel tracing infrastructure according to tracing configuration.

## Dependencies and integration points
It depends on `linux/tracepoint.h`, AV1 V4L2 stateless control structs and constants, and `TRACE_INCLUDE_PATH` pointing back to the VISL source directory for trace generation.

## Risks and test signals
Risks include large trace payloads, stale field lists if AV1 control structs evolve, and reference-index values being printed without semantic validation. Test signals include successful tracepoint compilation and readable events under `trace-cmd`/ftrace while decoding AV1 requests.
