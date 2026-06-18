# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/rc_calc.c

## Purpose

`rc_calc.c` is a thin non-FPU wrapper around the AMD DSC rate-control calculator. It maps DRM DSC PPS fields to the internal FPU calculator enums and invokes `_do_calc_rc_params` inside the DC floating-point guard.

## Important APIs, Types, And Functions

The only exported function is `calc_rc_params(struct rc_params *rc, const struct drm_dsc_config *pps)`. It chooses `enum colour_mode`, `enum bits_per_comp`, BPP, slice width/height, native422/native420 flag, and DSC version minor.

## Control Flow

When `CONFIG_DRM_AMD_DC_FP` is defined, the function derives mode from `convert_rgb`, `simple_422`, `native_422`, and `native_420`; maps 8/10/other BPC to 8/10/12; enters `DC_FP_START`; calls `_do_calc_rc_params`; and exits with `DC_FP_END`. Without FP support the function is effectively empty.

## State, Dependencies, Risks, And Test Signals

It only mutates caller-provided `rc_params`. It depends on `rc_calc.h`, which includes `dml/dsc/rc_calc_fpu.h`. `dsc_prepare_config` uses it before optional RC override and DSCC parameter computation. Risks include non-8/10 BPC collapsing to 12 and empty behavior when FP support is disabled. Tests should compare calculated RC parameters for RGB, simple422, native422, native420, 8/10/12bpc, and DSC 1.1/1.2.
