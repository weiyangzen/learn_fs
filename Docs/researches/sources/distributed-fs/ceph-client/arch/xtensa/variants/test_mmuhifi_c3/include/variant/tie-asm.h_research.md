# sources/distributed-fs/ceph-client/arch/xtensa/variants/test_mmuhifi_c3/include/variant/tie-asm.h

## Purpose
This generated assembler header supplies save and restore macros for non-coprocessor optional state and the AudioEngineLX coprocessor on the `test_mmuhifi_c3` Xtensa variant.

## Important APIs, types, and macros
`XTHAL_SAS_*` selector constants classify saved state. `xchal_ncp_store` and `xchal_ncp_load` handle optional non-coprocessor registers `BR`, `SCOMPARE1`, and `THREADPTR`. `xchal_cp1_store` and `xchal_cp1_load`, aliased through `xchal_cp_AudioEngineLX_store/load`, save and restore the HiFi2 AudioEngineLX state: user registers `AE_OVF_SAR`, `AE_BITHEAD`, `AE_TS_FTS_BU_BP`, `AE_SD_NO`, eight `aep` 48-bit registers, and four `aeq` 56-bit registers. Empty macros are provided for unconfigured coprocessor IDs 0 and 2 through 7.

## Control flow
The NCP macros start a save-area sequence, align to 4-byte boundaries, then conditionally store or load each selected optional register. The CP1 macros align the pointer to 8 bytes, store fixed user registers at offsets 0 through 12, store `aep0` through `aep7` in two groups, then store `aeq0` through `aeq3`; load reverses by loading `aeq` after an 80-byte pointer bump and then loading `aep` with negative offsets. Selection is controlled by assembler `.ifeq` expressions over `select`.

## State and persistence behavior
The file defines how task or exception code serializes volatile core and coprocessor registers into a caller-owned save area. The NCP layout is 12 bytes and the CP1 layout is 112 bytes, matching `tie.h`; total alignment padding brings combined save area to 128 bytes.

## Dependencies and integration points
The macros depend on Xtensa assembler opcodes such as `rur240`, `wur240`, `AE_SP24X2S.I`, `AE_SQ56S.I`, `AE_LP24X2.I`, and `AE_LQ56.I`, plus HAL helpers `xchal_sa_start` and `xchal_sa_align`. They integrate with Xtensa low-level context management and any lazy coprocessor switching logic for CP1.

## Risks
Pointer arithmetic in CP1 load/store is asymmetric but layout-compatible; changing offsets without checking `tie.h` can break restore. The save-area pointer contract says 8-byte alignment for CP1, and violations can fault or corrupt state on this core. `select` lacks the newer `alloc` parameter present in other generated variants, so callers must match this HAL generation.

## Test signals
Build the Xtensa assembly that expands these macros, run context-switch tests while executing HiFi2 instructions, compare CP1 save size against `XCHAL_CP1_SA_SIZE`, and validate that disabled CP macros assemble as no-ops.
