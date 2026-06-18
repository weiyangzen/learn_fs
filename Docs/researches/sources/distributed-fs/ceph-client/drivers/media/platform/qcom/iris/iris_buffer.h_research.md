# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_buffer.h

## Purpose
`iris_buffer.h` defines the driver-facing buffer model shared by vb2, Iris instance state, HFI command builders, and HFI response handlers. It is the contract that lets generation-specific firmware code and generic V4L2 code agree on buffer type, address, payload, timestamp, and lifecycle state.

## Important APIs, Types, And Functions
The key type is `enum iris_buffer_type`, with user-visible `BUF_INPUT`/`BUF_OUTPUT` plus internal buffers such as `BUF_BIN`, `BUF_ARP`, `BUF_COMV`, `BUF_NON_COMV`, `BUF_LINE`, `BUF_DPB`, `BUF_PERSIST`, `BUF_SCRATCH_1`, `BUF_SCRATCH_2`, `BUF_VPSS`, and `BUF_PARTIAL`. `enum iris_buffer_attributes` declares lifecycle bits used across queue, response, release, and vb2 completion paths. `struct iris_buffer` embeds `struct vb2_v4l2_buffer`, carries DMA address information, data offsets, V4L2 flags, timestamps, and attr bits. `struct iris_buffers` is the per-type instance list, minimum count, and buffer size.

## Control Flow
The header exports creation, queueing, release, destroy, deferred queue, and vb2 completion helpers implemented by `iris_buffer.c`. HFI Gen1 and Gen2 command files consume `enum iris_buffer_type` to translate driver buffers to firmware buffer identifiers. HFI response files mutate `attr` and call `iris_vb2_buffer_done()` after firmware returns input or output buffers.

## State And Persistence Behavior
Persistent state is per-instance: `inst->buffers[BUF_TYPE_MAX]` stores list heads, min counts, and sizes, while each `struct iris_buffer` records its current firmware/vb2 lifecycle through attr bits. Internal buffers are heap objects with DMA backing; user buffers are vb2-backed and are not allocated here.

## Dependencies And Integration Points
The file depends on `videobuf2-v4l2.h` and forward-declares `struct iris_inst`. It is included broadly by instance, HFI common, HFI command/response, VPU buffer, and common streaming code. `to_iris_buffer()` is the standard conversion from embedded vb2 buffer to Iris metadata.

## Risks And Test Signals
Because buffer attrs are bit flags rather than a strict enum, illegal combinations can occur if command and response paths diverge. Tests should assert that input and output buffers are completed once, queued buffers are never freed before firmware release, and each internal buffer type is translated by both Gen1 and Gen2 command/response code where applicable.
