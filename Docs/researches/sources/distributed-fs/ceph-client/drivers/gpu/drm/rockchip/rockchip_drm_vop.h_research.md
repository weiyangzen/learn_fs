# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_vop.h

## Purpose

`rockchip_drm_vop.h` is the register-description and helper contract for legacy Rockchip VOP hardware. It defines version macros, AFBC modifier support, register-field descriptors, SoC data tables, interrupt bits, alpha/scaler/dither enums, scaler math helpers, and component ops.

## Important APIs, Types, and Functions

- `ROCKCHIP_AFBC_MOD` defines the supported AFBC modifier: 16x16 sparse blocks with YTR transform.
- `struct vop_reg` describes offset, mask, shift, write-mask behavior, and relaxed-write behavior.
- `struct vop_data` aggregates the SoC descriptor, including version, windows, LUT size, max output, and feature flags.
- Scaler helpers compute fixed-point coefficients, vertical skip, scaling mode, and line-buffer mode.

## Control Flow

The header contributes inline scaler decision flow. `scl_get_scl_mode` picks none/up/down, `scl_get_vskiplines` chooses vertical skip for large downscale ratios, and `scl_vop_cal_lb_mode` selects line-buffer mode based on width and YUV/RGB.

## State and Persistence Behavior

The structures are mostly static SoC descriptions referenced by live `struct vop` instances. The `write_mask` and `relaxed` fields affect persistent register-shadow behavior in `vop_reg_set`.

## Dependencies and Integration Points

The header depends on DRM format modifier definitions, Linux bits, and the component framework through includers. It is paired with SoC register tables in `rockchip_vop_reg.c` and implementation in `rockchip_drm_vop.c`.

## Risks and Edge Cases

Wrong masks, shifts, or write-mask flags cause silent hardware misprogramming. `enum sacle_up_mode` contains a spelling error that is stable internally. `scl_cal_scale` assumes destination greater than one. AFBC modifier bits must match userspace producers.

## Test Signals

Compile all VOP SoC tables. Runtime signals include correct scaling, AFBC modifier negotiation, interrupt mask/clear behavior, dither modes, alpha blending, and line-buffer mode validation.
