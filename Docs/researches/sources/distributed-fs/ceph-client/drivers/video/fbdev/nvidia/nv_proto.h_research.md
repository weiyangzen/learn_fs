# sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_proto.h

## Purpose

`nv_proto.h` is the cross-file prototype contract for the NVIDIA fbdev driver. It declares setup/VGA register helpers, hardware state helpers, optional I2C and backlight entry points, Open Firmware EDID probing, and acceleration operations. The source was read as a complete 68-line file.

## Important APIs, Types, and Functions

Declared APIs include `NVCommonSetup`, `NVWriteCrtc`, `NVReadCrtc`, `NVWriteGr`, `NVReadGr`, `NVWriteSeq`, `NVReadSeq`, `NVWriteAttr`, `NVReadAttr`, DAC accessors, `NVCalcStateExt`, `NVLoadStateExt`, `NVUnloadStateExt`, `NVSetStartAddress`, `NVShowHideCursor`, `NVLockUnlock`, `nvidia_probe_of_connector`, `NVResetGraphics`, `nvidiafb_copyarea`, `nvidiafb_fillrect`, `nvidiafb_imageblit`, and `nvidiafb_sync`. Conditional stubs are provided for I2C and backlight when their config symbols are disabled.

## Control Flow

There is no runtime control flow. This header controls compile/link-time coupling among `nvidia.c`, `nv_setup.c`, `nv_hw.c`, `nv_accel.c`, `nv_i2c.c`, `nv_of.c`, and `nv_backlight.c`.

## State and Persistence Behavior

No state is stored. The prototypes describe functions that mutate `struct nvidia_par`, `struct fb_info`, hardware registers, and optional subsystem state elsewhere.

## Dependencies and Integration Points

It depends on `struct nvidia_par`, `struct fb_info`, and `struct _riva_hw_state` declarations from included or prior headers. It is the main integration point ensuring optional object files can be omitted while callers still compile through stub macros/functions.

## Risks and Edge Cases

Prototype drift can produce build failures or, worse, mismatched call assumptions if declarations and definitions diverge. Optional stubs must preserve return-value semantics expected by `NVCommonSetup()`; for example, disabled I2C probing returns failure so OF probing can still run.

## Test Signals

Build all NVIDIA fbdev config combinations: base only, I2C enabled, backlight enabled, both enabled, built-in and module. Warnings about missing prototypes or incompatible declarations are direct regression signals.
