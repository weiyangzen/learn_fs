# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-mpeg2.h

## Purpose
`visl-trace-mpeg2.h` defines tracepoints for MPEG-2 stateless controls submitted to VISL.

## Important APIs, types, and functions
The trace system is `visl_mpeg2_controls`. It declares event classes for sequence, picture, and quantisation controls and defines `v4l2_ctrl_mpeg2_sequence`, `v4l2_ctrl_mpeg2_picture`, and `v4l2_ctrl_mpeg2_quantisation`. The sequence event prints dimensions, VBV buffer size, profile/level, chroma format, and progressive flag. The picture event prints reference timestamps, picture flags, f-code bytes, coding type, structure, and intra DC precision. The quantisation event prints quantizer matrices.

## Control flow
`visl_trace_ctrls()` emits all three MPEG-2 events for `VISL_CODEC_MPEG2`. `visl-trace-points.c` instantiates the tracepoints.

## State and persistence
The header creates trace snapshots only. MPEG-2 reference behavior remains in request controls and TPG reference text.

## Dependencies and integration points
It depends on V4L2 MPEG-2 stateless control structs and tracepoint helpers. It is paired with the MPEG-2 control descriptors in `visl-core.c`.

## Risks and test signals
Risks are small but include stale field coverage and high output from matrix arrays. Test signals include trace output for sequence/picture/quantisation controls when MPEG-2 requests are queued.
