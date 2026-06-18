
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-params.c

## Purpose

`c3-isp-params.c` implements the ISP metadata-output video node used by userspace 3A/image-processing algorithms to submit per-frame parameter blocks. It validates V4L2 ISP parameter buffers, copies them into driver-owned scratch memory, queues them, and programs AWB gains/configuration, AE, AF, post gamma, CCM, CSC, and BLC hardware blocks at stream start and frame end.

## Important APIs, Types, And Functions

`union c3_isp_params_block` overlays the generic block header with each supported block-specific structure from `linux/media/amlogic/c3-isp-config.h`. `c3_isp_params_handlers[]` maps block type IDs to handlers, and `c3_isp_params_block_types_info[]` maps the same IDs to validation sizes. `static_assert()` enforces table length parity.

Hardware handlers include `c3_isp_params_cfg_awb_gains()`, `c3_isp_params_cfg_awb_config()`, `c3_isp_params_cfg_ae_config()`, `c3_isp_params_cfg_af_config()`, `c3_isp_params_cfg_pst_gamma()`, `c3_isp_params_cfg_ccm()`, `c3_isp_params_cfg_csc()`, and `c3_isp_params_cfg_blc()`. Helpers write zone weights/coordinates and LUT data.

The video-node entry points are `c3_isp_params_register()`, `c3_isp_params_unregister()`, `c3_isp_params_pre_cfg()`, and `c3_isp_params_isr()`. VB2 operations allocate scratch buffers with `kvmalloc()`, validate/copy user payloads in `buf_prepare`, enqueue under `buff_lock`, and return pending buffers on stop.

## Control Flow

Userspace opens the metadata-output node, allocates VMALLOC/DMABUF buffers of `sizeof(struct c3_isp_params_cfg)`, fills a validated `v4l2_isp_params_buffer`-style block stream, and queues buffers. `buf_prepare` checks the payload size, copies user data to `buf->cfg`, and calls `v4l2_isp_params_validate_buffer()` against the block type table.

At resizer stream start, `c3_isp_params_pre_cfg()` disables many unused ISP modules, disables AE/AF/AWB stats until explicitly enabled by parameter blocks, sets WB limits to max, and applies only the first pending buffer if one exists. On each frame-end IRQ, `c3_isp_params_isr()` removes the first pending buffer, walks its block list in `c3_isp_params_cfg_blocks()`, programs hardware, stamps sequence/timestamp/field, and marks the VB2 buffer done.

## State And Persistence

`struct c3_isp_params` stores video format, VB2 queue, mutex, spinlock, pending list, and current `buff`. Each queued `struct c3_isp_params_buffer` owns scratch `cfg` memory until cleanup. State is in memory only; hardware register state changes when parameter buffers are processed and is not persisted across power/runtime reset.

## Dependencies And Integration Points

The file depends on the V4L2 ISP parameter validation helpers, C3 ISP public parameter ABI in `c3-isp-config.h`, VB2 VMALLOC memory ops, metadata-output V4L2 ioctls, media-controller pads, and register definitions from `c3-isp-regs.h`. It integrates with `c3-isp-dev.c` through `c3_isp_params_isr()`, with `c3-isp-resizer.c` through `c3_isp_params_pre_cfg()`, and with the core params sink media link.

## Risks

`c3_isp_params_cfg_blocks()` indexes `c3_isp_params_handlers[block->header.type]` without local bounds or NULL checks, relying entirely on prior validation. The while loop advances by `block->header.size`; corrupted internal scratch data would risk an infinite loop or out-of-bounds access. Several coordinate and zone-weight writers trust `horiz_zones_num * vert_zones_num` and point counts to fit the ABI arrays. Pre-configuration keeps the first pending buffer on the list while applying it, so the same buffer can be applied again at the next frame-end unless the queue order is intended as an initial programming pass.

## Test Signals

Run V4L2 metadata-output format enumeration and verify only `V4L2_META_FMT_C3ISP_PARAMS` is accepted. Queue valid and invalid block streams to exercise buffer-size, block-size, type, and payload validation. Hardware tests should verify enable/disable flags gate module bits, AWB/AE weights are written in groups of eight plus remainder, gamma LUT writes all entries for three channels, and frame-end completion returns exactly one params buffer with the current sequence.
