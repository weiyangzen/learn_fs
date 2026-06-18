# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wopcm.c

## Purpose

`xe_wopcm.c` partitions and programs Intel Xe Write Once Protected Content Memory for GuC and HuC firmware. It calculates platform WOPCM size, reserves mandatory regions, validates firmware fit, honors BIOS/IFWI prelocked registers, and writes the GuC WOPCM size/base registers when unlocked.

## Important APIs, Types, And Functions

Public APIs are `xe_wopcm_size()` and `xe_wopcm_init()`. Internal helpers include `context_reserved_size()`, `__check_layout()`, `__wopcm_regs_locked()`, and `__wopcm_init_regs()`. Constants define default WOPCM sizes, GuC/HuC reserved areas, GuC stack reservation, alignment, and hardware-context reservation.

## Control Flow

Initialization derives GuC and HuC upload sizes, rejects missing GuC firmware, chooses the platform WOPCM size, asserts force-wake ownership, and checks whether WOPCM registers are already locked. If locked, it reads and validates the programmed base/size against a maximum WOPCM size. If unlocked, it aligns the GuC base after the HuC firmware plus reserved area, clamps it below the hardware-context reservation, assigns the remaining aligned space to GuC, validates the layout, stores `wopcm->guc.base` and `wopcm->guc.size`, and writes/verifies `GUC_WOPCM_SIZE` and `DMA_GUC_WOPCM_OFFSET`.

## State And Persistence Behavior

Persistent driver state is stored in `struct xe_wopcm`: total WOPCM size and GuC region base/size. Hardware persistence is stronger: the GuC WOPCM size and offset registers are locked/valid write-once configuration until reset. If HuC firmware is available, the HuC-loading-agent bit is included in the offset programming.

## Dependencies And Integration Points

It depends on GT/device conversion, force-wake assertions, Xe MMIO read/write-and-verify helpers, GuC register definitions, firmware upload sizes from `xe_uc_fw`, platform info such as DGFX, Meteor Lake, and Nova Lake P, and DRM diagnostics. `ALLOW_ERROR_INJECTION()` allows failure testing in probe paths.

## Risks And Test Signals

Risks include firmware sizes exceeding static WOPCM assumptions, mismatch between prelocked BIOS layout and driver validation, per-GT vs global maximum-size FIXME behavior, alignment/mask mistakes, and write-once register failures that block GuC upload. Test by injecting `xe_wopcm_init()` errors, booting with GuC-only and GuC+HuC firmware, exercising locked and unlocked register paths, checking MMIO values, and validating error logs for too-large firmware.
