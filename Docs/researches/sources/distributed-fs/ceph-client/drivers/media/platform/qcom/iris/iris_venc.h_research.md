# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_venc.h

## Purpose
Declares encoder-specific Iris operations used by generic V4L2 and vb2 code.

## Important APIs
Includes instance init, enum/try/set/validate format, event subscription, crop selection, stream parameters, stream-on input/output, qbuf, and encoder START/STOP command handlers.

## Control Flow And Integration Points
`iris_vidc.c` dispatches encoder ioctls here, and `iris_vb2.c` dispatches stream/qbuf operations here for encoder sessions.

## State And Persistence Behavior
No header state; implementation mutates encoder session formats, crop, rates, scaling fields, buffers, and drain state.

## Dependencies
Requires V4L2 types and `struct iris_inst`.

## Risks
Header guard uses `_IRIS_VENC_H_` while most Iris headers use double-underscore names; functionally fine but style differs.

## Test Signals
Compile coverage plus encoder V4L2 lifecycle tests.
