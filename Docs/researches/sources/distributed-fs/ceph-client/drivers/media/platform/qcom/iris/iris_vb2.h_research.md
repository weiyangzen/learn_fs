# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vb2.h

## Purpose
Declares Iris vb2 operation callbacks.

## Important APIs
- Buffer lifecycle: `iris_vb2_buf_init()`, `iris_vb2_buf_prepare()`, `iris_vb2_buf_out_validate()`, `iris_vb2_buf_queue()`.
- Queue lifecycle: `iris_vb2_queue_setup()`, `iris_vb2_start_streaming()`, `iris_vb2_stop_streaming()`.

## Control Flow And Integration Points
`iris_vidc.c` references these functions in its static `vb2_ops` table for both decoder and encoder queues.

## State And Persistence Behavior
No header state; implementation mutates instances, queues, and buffers.

## Dependencies
Requires vb2 types and Iris instance definitions in including files.

## Risks
Signature changes must stay synchronized with the V4L2/vb2 callback table.

## Test Signals
Compile coverage and V4L2 queue lifecycle tests.
