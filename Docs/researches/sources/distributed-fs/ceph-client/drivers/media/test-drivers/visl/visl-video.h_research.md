# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl-video.h

## Purpose
`visl-video.h` declares the public video-interface hooks exported by `visl-video.c` to the VISL core.

## Important APIs, types, and functions
The header exports `visl_ioctl_ops`, all codec control-set descriptors (`visl_fwht_ctrls` through `visl_av1_ctrls`), `visl_queue_init()`, `visl_set_default_format()`, and `visl_request_validate()`.

## Control flow
`visl-core.c` consumes `visl_ioctl_ops` when defining the `video_device`, passes `visl_queue_init()` to `v4l2_m2m_ctx_init()` during open, calls `visl_set_default_format()` for new contexts, and registers `visl_request_validate()` as the media-device request validator.

## State and persistence
The header owns no state. It exposes operations that initialize and validate per-context state.

## Dependencies and integration points
It includes V4L2 mem2mem and `visl.h`. It is the narrow interface between device lifecycle code and V4L2/vb2 implementation code.

## Risks and test signals
The main risk is declaration drift from `visl-video.c` or missing exports when codec control sets change. Build coverage is the primary test signal.
