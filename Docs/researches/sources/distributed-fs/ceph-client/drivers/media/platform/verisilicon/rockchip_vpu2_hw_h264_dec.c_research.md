# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/rockchip_vpu2_hw_h264_dec.c

## Purpose
Programs the Rockchip VDPU2 H.264 stateless decoder run for the Hantro mem2mem driver. It translates the current V4L2 H.264 SPS/PPS/decode controls, decoded-picture-buffer metadata, and vb2 DMA buffers into VDPU software registers, then starts one decode job.

## Important APIs, Types, And Functions
- Exports `rockchip_vpu2_h264_dec_run(struct hantro_ctx *ctx)`.
- Internal helpers `set_params()`, `set_ref()`, and `set_buffers()` write control registers, reference lists/reference numbers, DPB addresses, stream/output addresses, direct-motion-vector storage, and the auxiliary qtable buffer.
- Depends on `struct hantro_h264_dec_ctrls`, `struct v4l2_ctrl_h264_*`, `struct v4l2_h264_reference`, `hantro_h264_dec_prepare_run()`, `hantro_h264_get_ref_nbr()`, and `hantro_h264_get_ref_buf()`.

## Control Flow
`rockchip_vpu2_h264_dec_run()` prepares the H.264 context, fetches the source buffer, writes stream length/endian/AXI/mode/field/profile/PPS/SPS parameters, writes P and B reference-list packing registers, writes all DPB reference addresses, writes source/destination/DMV/qtable addresses, ends the prepare phase, and sets `VDPU_REG_DEC_E` in software register 57. Bottom-field decodes offset the output start by one aligned line, and high-profile reference pictures write a DMV buffer after the decoded frame storage.

## State And Persistence
No durable state is stored. The function consumes per-job control state cached in `ctx->h264_dec`, per-context auxiliary DMA from H.264 init, and vb2 buffer timestamps/addresses. Register writes are transient hardware state for a single decode job.

## Dependencies And Integration Points
Integrated through Rockchip codec ops in `rockchip_vpu_hw.c`, primarily RK3399/RK3328/RK3568 VDPU2 variants. It uses Hantro core run fencing via `hantro_start/end_prepare_run()` and completion through the shared VDPU2 IRQ path.

## Risks And Edge Cases
Correctness is sensitive to V4L2 control validation, DPB index ordering, interlaced field flags, monochrome high-profile DMV sizing, and destination layout assumptions in `hantro_get_dec_buf_addr()`. Missing or stale references can program wrong DPB addresses. Bottom-field offset and DMV offset arithmetic must match the backing buffer allocation.

## Test Signals
Useful signals are successful stateless H.264 decode for baseline/high profile, frame and field pictures, B slices, long-term references, monochrome streams, and no VDPU2 timeout/bus-error IRQs. Compare decoded CRCs against software decode and watch for corruption across reference-heavy streams.
