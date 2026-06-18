# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-trace-vp9.h

## Purpose
`visl-trace-vp9.h` defines tracepoints for VP9 stateless frame controls, compressed header probabilities, coefficient probabilities, and motion-vector probabilities.

## Important APIs, types, and functions
The trace system is `visl_vp9_controls`. Event classes cover `struct v4l2_ctrl_vp9_frame`, `struct v4l2_ctrl_vp9_compressed_hdr`, coefficient arrays within the compressed header, and `struct v4l2_vp9_mv_probs`. Defined events are `v4l2_ctrl_vp9_frame`, `v4l2_ctrl_vp9_compressed_hdr`, `v4l2_ctrl_vp9_compressed_coeff`, and `v4l2_vp9_mv_probs`.

The frame event prints loop filter, quantization, segmentation, flags, headers, dimensions, reference timestamps, sign bias, reset context, profile, bit depth, interpolation filter, tile geometry, and reference mode. Header and coefficient events dump probability arrays.

## Control flow
For `VISL_CODEC_VP9`, `visl_trace_ctrls()` emits frame, compressed-header, coefficient, and motion-vector probability events.

## State and persistence
The header creates trace snapshots only. It does not track VP9 frame contexts or probability updates beyond the submitted control values.

## Dependencies and integration points
It depends on V4L2 VP9 stateless controls and the Linux tracepoint framework. It is tied to `visl_vp9_ctrls` and `struct visl_vp9_run`.

## Risks and test signals
Risks include very large trace output and stale probability-array formatting if the uAPI changes. Test signals are successful tracepoint compilation and expected VP9 events during stateless VP9 request playback.
