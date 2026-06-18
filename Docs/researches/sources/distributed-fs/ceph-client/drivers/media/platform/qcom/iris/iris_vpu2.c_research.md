# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu2.c

## Purpose
Provides VPU2 generation operations, chiefly frequency calculation for gen1 platforms.

## Important APIs And Functions
- `iris_vpu2_calc_freq()` computes required frequency from source/crop macroblocks per frame, default FPS, platform VPP/VSP cycle coefficients, and compressed input data size.
- `iris_vpu2_ops` supplies generic VPU power on/off/controller/hwmode operations plus the VPU2-specific `calc_freq`.

## Control Flow And Integration Points
Gen1 platform data assigns `.vpu_ops = &iris_vpu2_ops`. Power scaling calls `vpu_ops->calc_freq()` after scanning queued source buffers. Core/firmware init and runtime PM call the power/controller functions through VPU common code.

## State And Persistence Behavior
No persistent state. Frequency calculation reads instance format, crop, and platform caps.

## Dependencies
Depends on VPU common power helpers, register defines, `iris_instance`, and platform instance caps.

## Risks
- Uses `DEFAULT_FPS` instead of actual frame/operating rate.
- Data-size contribution is included only in VSP frequency and can dominate for high-bitrate inputs.
- Cycle coefficients in platform caps must be valid for VPU2.

## Test Signals
- Power-scaling traces on SM8250/SC7280 with varied resolution and input sizes.
- Runtime PM firmware boot and shutdown on VPU2 platforms.
