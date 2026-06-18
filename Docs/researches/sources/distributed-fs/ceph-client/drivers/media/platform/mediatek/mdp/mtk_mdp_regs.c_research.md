# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_regs.c

## Purpose
Despite its name, this file does not directly program MMIO registers. It translates V4L2 context/frame settings into the legacy VPU shared `mdp_process_vsi` structure for source/destination buffers, crop, formats, rotation/flip, and alpha.

## Important APIs, Types, and Functions
The exported helpers are `mtk_mdp_hw_set_input_addr()`, `mtk_mdp_hw_set_output_addr()`, `mtk_mdp_hw_set_in_size()`, `mtk_mdp_hw_set_in_image_format()`, `mtk_mdp_hw_set_out_size()`, `mtk_mdp_hw_set_out_image_format()`, `mtk_mdp_hw_set_rotation()`, and `mtk_mdp_hw_set_global_alpha()`. `mtk_mdp_map_color_format()` maps V4L2 fourccs to firmware `MDP_COLOR_*` encodings.

## Control Flow
The mem2mem worker prepares DMA addresses in frames, then calls these helpers in sequence before `mtk_mdp_vpu_process()`. Each helper writes the corresponding fields in `ctx->vpu.vsi`.

## State and Persistence
The state written here is shared-memory job state consumed by VPU firmware. It is overwritten for each queued job and does not persist after context deinit.

## Dependencies and Integration Points
The file depends on `mtk_mdp_core.h`, `mtk_mdp_regs.h`, and the IPI structs from `mtk_mdp_ipi.h`. It is the conversion point from Linux V4L2 formats/crops to firmware ABI.

## Risks and Edge Cases
Unsupported formats map to `MDP_COLOR_UNKNOWN` after logging, but callers do not get an explicit error at this layer. Stride fields are set to zero so firmware must infer them from color format and plane sizes. Plane size loops use `plane_num` from format metadata and must stay within `MTK_MDP_MAX_NUM_PLANE`.

## Test Signals
Verify VPU shared memory for each supported fourcc, crop geometry, plane size, rotation, hflip/vflip, and global alpha before processing.
