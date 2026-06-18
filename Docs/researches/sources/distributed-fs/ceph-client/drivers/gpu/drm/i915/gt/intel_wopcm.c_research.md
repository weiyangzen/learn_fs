# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_wopcm.c

## Purpose
`intel_wopcm.c` computes and validates the WOPCM layout used by GuC and HuC firmware plus reserved hardware context space.

## Important APIs, Types, And Functions
Public functions are `intel_wopcm_init_early()` and `intel_wopcm_init()`. Internal helpers compute context reservations, validate Gen9 dword-gap and HuC-fit restrictions, verify whole layout bounds, detect locked GuC WOPCM registers, check register writability under GuC deprivilege, and map `intel_wopcm` back to `intel_gt`.

## Control Flow
Early init sets the platform default WOPCM size for GTs with microcontrollers: 2 MiB on Gen11+ and 1 MiB on earlier Gen9-era platforms. Full init reads GuC/HuC upload sizes and reserved context size. If firmware sizes are absent it returns. If registers are already locked, it trusts programmed base/size, relaxing total-size validation when i915 cannot write deprivileged registers. Otherwise it rejects unlocked media-GT cases, computes a HuC-reserving aligned GuC base, assigns remaining aligned space to GuC, validates all restrictions, and stores `wopcm->guc.base/size`.

## State, Persistence, And Dependencies
State persists in `struct intel_wopcm` embedded in GT. Hardware state is reflected in `DMA_GUC_WOPCM_OFFSET`, `GUC_WOPCM_SIZE`, and deprivilege shim registers. Dependencies include GuC/HuC firmware metadata, `intel_uc_supports_huc()`, i915 platform macros, uncore reads, and size/alignment constants.

## Integration Points
GuC/HuC firmware upload and register programming consume the computed GuC WOPCM region. Platform init must run early enough that firmware loading can abort if layout is invalid.

## Risks
Layout math is constrained by several hardware reservations and Gen9 quirks. Media-GT platforms are expected to have prelocked deprivileged registers; unlocked media GT returns without configuring WOPCM. Prelocked BIOS/IFWI values are trusted more than calculated values on deprivileged systems, deferring impossible layouts to firmware DMA failure.

## Test Signals
Boot logs for WOPCM calculations, GuC/HuC firmware load success/failure, Gen9 small firmware-layout tests, deprivileged prelocked register tests, media-GT probe paths, and boundary tests for firmware sizes and alignment validate this code.
