# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rga/rga-hw.c

Purpose: converts an `rga_ctx` plus queued source/destination buffers into an RGA hardware command buffer and starts execution.

Important APIs/functions: `rga_hw_start()` is the exported hardware entry point. Internal helpers compute scaling (`rga_get_scaling()`), crop/rotation/mirror address offsets (`rga_get_addr_offset()`, `rga_lookup_draw_pos()`), set source/source1/destination MMU descriptor bases, program transform information, source/destination base offsets, render mode, and command buffer address. `rga_cmd_set()` assembles the command buffer and syncs it for device access.

Control flow/state: command setup clears the shared command buffer, writes descriptor table addresses shifted by four bits, enables MMU control bits, disables alpha blending, computes CSC only when input/output colorspace families differ, applies H/V flip and 0/90/180/270 rotation, swaps scaling destination dimensions for 90/270 rotation, programs virtual strides and active sizes, writes base offsets for cropped source and rotated/mirrored destination, then kicks registers `RGA_SYS_CTRL`, `RGA_INT`, and `RGA_CMD_CTRL`.

Dependencies/integration: called from `device_run()` in `rga.c` under `ctrl_lock` with `rga->curr` set. It uses `rga.h` context/frame/buffer structures and bitfield unions/register macros from `rga-hw.h`.

Risks and test signals: address-offset math is highly sensitive for YUV subsampling, rotation, and mirroring. A version workaround adjusts source dimensions for old hardware around 90/270 rotation. CSC mode uses input or output colorspace depending on conversion direction. Test RGB->RGB, YUV->RGB, RGB->YUV, scaling up/down, all rotations/flips, nonzero crop/compose, old RGA version values, and DMA sync correctness.
