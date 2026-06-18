# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-dec.h

## Purpose
`visl-dec.h` defines the per-job control payload container used by the virtual decode path.

## Important APIs, types, and functions
The header declares one small run structure per supported codec: `visl_fwht_run`, `visl_mpeg2_run`, `visl_vp8_run`, `visl_vp9_run`, `visl_h264_run`, `visl_hevc_run`, and `visl_av1_run`. Each stores typed pointers to the stateless V4L2 control structs needed by that codec. `struct visl_run` combines source and destination `vb2_v4l2_buffer` pointers with a union of those codec-specific structures.

It also declares `visl_dec_start()`, `visl_dec_stop()`, `visl_job_ready()`, and `visl_device_run()`. In this source set only `visl_device_run()` is implemented and wired into the mem2mem ops.

## Control flow
`visl_device_run()` fills the relevant union member based on `ctx->current_codec`, then passes the run object to TPG, tracepoint, and debugfs routines. The header is the typed contract that keeps those consumers from manually re-fetching controls.

## State and persistence
The run object is stack-local for one mem2mem job and does not persist beyond a single output/capture buffer pair. It contains borrowed pointers into the active V4L2 control handler.

## Dependencies and integration points
It includes V4L2 stateless control definitions and `visl.h`. It is included by decoder and debugfs code because bitstream tracing needs access to the source buffer in `struct visl_run`.

## Risks and test signals
The header must be kept synchronized with the controls registered in `visl-core.c` and the trace dispatch in `visl-dec.c`. New codec controls need new fields or updated trace paths. Build warnings and per-codec request tests are the best signals for mismatch.
