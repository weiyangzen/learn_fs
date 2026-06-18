# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/rc_calc.h

## Purpose

`rc_calc.h` exposes the DSC rate-control calculation wrapper to DSC hardware backends while hiding the FPU implementation behind `dml/dsc/rc_calc_fpu.h`.

## Important APIs, Types, And Functions

It declares `calc_rc_params(struct rc_params *rc, const struct drm_dsc_config *pps)` and brings in `struct rc_params` plus calculator enums through the FPU header.

## Control Flow

The header has no control flow. It defines the compile-time dependency that allows `dcn20_dsc.c` and other DSC code to call the wrapper without directly invoking FPU internals.

## State, Dependencies, Risks, And Test Signals

No state is defined here. All mutation occurs in the implementation through the caller-supplied `rc_params`. It depends directly on the DML DSC FPU calculator. Risks include exposing FPU-only declarations to non-FPU build contexts and mismatched `rc_params` definitions. Kernel build matrix coverage with and without `CONFIG_DRM_AMD_DC_FP` is the primary signal.
