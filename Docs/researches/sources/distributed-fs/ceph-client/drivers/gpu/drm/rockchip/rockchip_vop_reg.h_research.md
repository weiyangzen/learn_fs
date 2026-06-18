## sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_vop_reg.h

### Purpose

`rockchip_vop_reg.h` defines raw MMIO register offsets for the older Rockchip VOP controller generations. It is the address map used by `rockchip_vop_reg.c` to build typed field descriptors for system control, display timing, windows, alpha, interrupts, AFBC, MMU, color conversion, LUTs, BCSH/CABC, HDR/SDR conversion, and MCU bypass regions.

### Important APIs, Types, and Functions

The file has no functions or C types. Its API is a set of preprocessor macros grouped by SoC/register layout: RK3288, RK3368, RK3366, RK3399, RK3328, RK3036, RK3126, PX30, RK3188, RK3066, and RK3506. Macro families include common controller registers (`*_SYS_CTRL`, `*_DSP_CTRL*`, `*_REG_CFG_DONE`), window registers (`WIN0..WIN3_*`), hardware cursor registers (`HWC_*`), timing registers (`DSP_HTOTAL_HS_END`, `DSP_HACT_ST_END`, etc.), interrupt registers, AFBCD blocks, YUV2YUV/CSC coefficient ranges, MMU registers, LUT address windows, and post-processing/HDR blocks.

### Control Flow

There is no executable control flow. Include guards prevent duplicate definitions. Consumers include the header and use symbolic offsets to build `struct vop_reg` descriptors or direct table entries.

### State and Persistence Behavior

The header owns no state. It names persistent hardware locations, so writes through these offsets alter display controller state until later reprogramming, reset, runtime PM, or power loss. LUT address ranges and MMU/AFBC offsets identify memory-backed programming windows with side effects outside simple scalar registers.

### Dependencies and Integration Points

It has no external includes and is tightly integrated with `rockchip_vop_reg.c`. The macro names form an internal contract with the common VOP driver and any future table additions for the same controller generations.

### Risks and Edge Cases

Offset mistakes are difficult to catch at compile time. Several SoCs share near-identical maps with small shifts in interrupt, MMU, LUT, or HDR regions, so copy/paste changes are risky. Some maps include reserved/debug/post-processing registers that may not be safe to program generically. New code should avoid assuming that similarly named registers have the same width or bit layout across SoCs; `rockchip_vop_reg.c` must still provide masks and shifts per field.

### Test Signals

Compile-time signal is use by all VOP table definitions. Runtime validation comes from successful modeset, vblank interrupt, LUT, AFBC, MMU, and plane programming on each SoC family. Register dumps from vendor documentation or hardware bring-up are useful to compare every offset group before enabling new features.
