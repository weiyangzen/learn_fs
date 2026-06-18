# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crt_regs.h

## Purpose
Defines ADPA register addresses and bit fields for analog CRT/VGA output programming.

## Important definitions
The file defines `ADPA`, `PCH_ADPA`, and `VLV_ADPA`, plus fields for DAC enable, pipe select, hotplug monitor result, hotplug enable/period/warmup/sample/voltage/reference/force-trigger, VGA polarity source, sync disable bits, and sync active-high bits.

## Control flow and state
There is no executable code. These definitions encode persistent hardware state used by `intel_crt.c` for DPMS, detection, reset, and pipe selection.

## Dependencies, risks, and tests
It depends on display register helper macros. Risks are field-mask mistakes causing wrong pipe routing, hotplug mis-detection, or sync polarity errors. Tests include CRT mode set, DPMS, hotplug force trigger, and register readback on native, PCH, and VLV paths.
