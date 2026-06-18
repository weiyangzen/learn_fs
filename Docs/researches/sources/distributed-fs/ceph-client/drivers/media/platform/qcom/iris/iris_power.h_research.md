# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_power.h

## Purpose
Declares the Iris power-scaling entry point.

## Important APIs
- `int iris_scale_power(struct iris_inst *inst);` recalculates and applies clock and interconnect votes for a session.

## Control Flow And Integration Points
Included by vb2 and codec queue paths so stream-on/qbuf can request updated power votes. Implementation is in `iris_power.c`.

## State And Persistence Behavior
The header owns no state.

## Dependencies
Forward-declares `struct iris_inst`; implementation depends on PM runtime, V4L2 mem2mem, platform VPU ops, and resource helpers.

## Risks
Callers must check the return value if power scaling failure should abort the current operation.

## Test Signals
Compile coverage catches signature drift; runtime stream-on/qbuf paths exercise the implementation.
