# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vdec.h

## Purpose
Declares decoder-specific Iris operations used by generic V4L2 and vb2 code.

## Important APIs
Includes instance init, enum/try/set/validate format, event subscription, source-change event, stream-on input/output, qbuf, and decoder START/STOP command handlers.

## Control Flow And Integration Points
`iris_vidc.c` uses the ioctl-facing helpers. `iris_vb2.c` uses stream-on/qbuf helpers. HFI response code can call source-change notification.

## State And Persistence Behavior
No header state; implementation mutates decoder session format, crop, buffers, and sub-state.

## Dependencies
Requires V4L2 types and `struct iris_inst`.

## Risks
Prototype drift impacts generic dispatch in `iris_vidc.c` and queue dispatch in `iris_vb2.c`.

## Test Signals
Build coverage plus decoder V4L2 lifecycle tests.
