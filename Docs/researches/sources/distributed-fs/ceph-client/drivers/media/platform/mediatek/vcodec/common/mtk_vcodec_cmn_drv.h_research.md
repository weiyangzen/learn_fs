# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_cmn_drv.h

## Purpose
This common header defines shared MediaTek vcodec queue, register, clock, power-management, format, and instance state types used by both decoder and encoder code.

## Important APIs, Types, And Functions
`enum mtk_q_type` indexes source and destination queue data. `enum mtk_hw_reg_idx` defines shared decoder and encoder register-base indexes. `struct mtk_vcodec_clk_info`, `struct mtk_vcodec_clk`, and `struct mtk_vcodec_pm` describe clock/PM resources. `enum mtk_vdec_hw_id` distinguishes core/LAT hardware. `enum mtk_instance_state` models codec instance lifecycle from free through init, header, flush, and abort. `struct mtk_video_fmt` and `struct mtk_q_data` store V4L2 format metadata and queue geometry. `enum mtk_instance_type` distinguishes decoder and encoder contexts.

## Control Flow
No direct control flow. These types are consumed by probe, ioctl, queue setup, worker, PM, and firmware paths.

## State, Persistence, And Dependencies
State is in-memory per-device or per-context. Dependencies include platform devices, V4L2 controls/devices/ioctls/mem2mem, and videobuf2 core.

## Integration Points
Included by decoder/encoder driver headers, common util, firmware, interrupt, and debugfs code.

## Risks
Several common helpers infer instance type by reading the first field of decoder/encoder contexts, so `enum mtk_instance_type type` must stay first in those structs. Register indexes are shared across modules and must match mapped arrays.

## Test Signals
Compile coverage for decoder and encoder, runtime memory alloc/free from both instance types, and register-index bounds testing.
