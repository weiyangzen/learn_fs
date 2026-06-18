# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-fw-isys.h

## Purpose

This header declares the host-side ISYS firmware interface used by ISYS video/queue code.

## Important APIs, Types, and Functions

It declares init/release/open/close, dump helpers, simple/complex command submission, and response get/put APIs. It includes `ipu7_fw_isys_abi.h` and forward-declares ISYS structures.

## Control Flow

No implementation flow. Callers initialize firmware support, open booted firmware, send stream/buffer commands, consume responses, and close/release firmware support.

## State and Persistence Behavior

The APIs operate on `struct ipu7_isys` state, including subsystem config DMA memory and syscom queues.

## Dependencies and Integration Points

It is the bridge between V4L2 stream management and firmware syscom/boot layers.

## Risks and Edge Cases

Command callers must provide CPU and DMA pointers for complex payloads and respect stream handle/queue limits.

## Test Signals

Compile ISYS users and run stream open/capture/close command sequences with response draining.
