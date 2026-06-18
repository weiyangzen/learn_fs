<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_reg.h

## Purpose
Defines a compact set of i915 MMIO registers and bit fields used by core GT, GTT, interrupt, stolen-memory, clock-gating, power, L3 parity, GSC/HECI, and legacy display/GMBUS-adjacent paths. The file also documents the register macro style used across i915.

## Important APIs, types, and functions
- Register-address macros use `_MMIO()` from `i915_reg_defs.h` and display helpers from `intel_display_reg_defs.h`.
- Important groups include `GU_CNTL`, stolen memory reservation masks, reset registers, IOSF sideband registers, fence registers, ring base offsets, HECI/GSC registers, GT/PCU interrupt triplets, L3 parity registers, GGC/GSM/DSM stolen-memory registers, and MTL stolen-access registers.
- `I915_IRQ_REGS()` and `I915_ERROR_REGS()` group register triplets/pairs for interrupt and error handling callers.

## Control flow
This header is declarative. Runtime code expands these macros to platform-specific MMIO offsets and bit masks, then accesses them through uncore/display register helpers. Function-like macros choose register instances for fence slots, rings, HECI firmware status registers, L3 slices, and GT interrupt banks.

## State and persistence
No C state is stored here. The definitions address persistent hardware state: interrupt masks/status, stolen memory layout, fence registers, power/performance registers, clock-gating bits, and firmware status windows. Incorrect definitions affect hardware state programmed elsewhere.

## Dependencies and integration points
Included by core i915 files such as utility code, uncore/GT code, interrupt handling, stolen-memory probing, GSC/HECI firmware logic, sysfs L3 parity paths, and platform workarounds. It depends on typed register wrappers and generic Intel register bit helpers.

## Risks
The macros are platform-sensitive. Wrong bit shifts or generation-specific reuse can cause invalid MMIO writes, missed interrupts, broken stolen-memory discovery, bad fence tiling setup, or firmware communication failures. Large legacy sections mix raw shifts with newer `REG_BIT`/`REG_GENMASK` style, so edits need careful local consistency.

## Test signals
Build coverage catches type mismatches. Runtime signals include clean MMIO unclaimed-access logs, correct interrupt delivery, stolen-memory size detection, working GSC/HECI status polling, L3 parity sysfs behavior, GT reset handling, and platform workarounds passing on gen2 through Xe-era hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_reg.h -->
