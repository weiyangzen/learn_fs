# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_utils.h

## Purpose
Declares shared Iris utility types and helper functions.

## Important APIs And Types
- Metadata structs: `iris_hfi_rect_desc`, `iris_hfi_frame_info`, and `iris_ts_metadata`.
- `NUM_MBS_PER_FRAME(height, width)` macro computes 16x16 macroblock count.
- `iris_v4l2_type_to_driver()` maps V4L2 OUTPUT to `BUF_INPUT` and all other types to `BUF_OUTPUT`.
- Function declarations cover resolution comparison, MBPF, split mode, instance lookup, buffer draining, response waiting, core capacity checks, and rotation.

## Control Flow And Integration Points
Included broadly by codec, vb2, VPU buffer, HFI response, and control code. The inline V4L2-to-driver mapping is used in queue paths to select Iris buffer type.

## State And Persistence Behavior
No state in the header; declared helpers operate on `iris_inst` and `iris_core`.

## Dependencies
Includes `iris_buffer.h` and relies on V4L2 types being visible to users.

## Risks
`iris_v4l2_type_to_driver()` treats any non-output type as output/capture driver buffer, so callers should validate V4L2 type before using it.

## Test Signals
Compile coverage and queue-type tests through vb2 stream-on/qbuf.
