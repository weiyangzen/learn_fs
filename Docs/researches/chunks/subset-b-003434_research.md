# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_7_0_sh_mask.h

## Chunk Scope

- Work item: `subset-b-003434`
- Source range: lines 1-2467 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_7_0_sh_mask.h`
- This is the first chunk of a larger generated AMD UMC 6.7.0 register shift/mask header. The chunk starts at the license and include guard, covers the MCA status/address register bitfields, covers full UMC channel blocks for channels 0-5, and ends inside the channel 6 performance monitor field definitions at `UMCCH6_0_PerfMonCtl7__VCSel__SHIFT`.

## Purpose

This header provides C preprocessor constants for decoding and composing bitfields in AMD GPU Unified Memory Controller (UMC) 6.7.0 hardware registers. Each register field has a `__SHIFT` macro and a matching `__MASK` macro. Driver code combines these definitions with AMDGPU helper macros such as `REG_GET_FIELD()` and `REG_SET_FIELD()` to read machine-check status, ECC counters, ECC control state, address decoding configuration, and UMC performance-monitor registers without hard-coding bit positions at each call site.

The chunk is data-only: it has no functions, structs, executable statements, or runtime allocation. Its behavioral importance comes from making the register ABI visible to C code that performs RAS/MCA/ECC handling for UMC 6.7.0 ASICs.

## Important Exports

- Include guard: `_umc_6_7_0_SH_MASK_HEADER`.
- MCA status register fields for `MCA_UMC_UMC0_MCUMC_STATUST0`:
  `ErrorCode`, `ErrorCodeExt`, `AddrLsb`, `ErrCoreId`, `Scrub`, `Poison`, `Deferred`, `UECC`, `CECC`, `Transparent`, `SyndV`, `TCC`, `ErrCoreIdVal`, `PCC`, `AddrV`, `MiscV`, `En`, `UC`, `Overflow`, and `Val`, plus reserved fields.
- MCA address register fields for `MCA_UMC_UMC0_MCUMC_ADDRT0`:
  `ErrorAddr` in bits 0-55 and `Reserved` in bits 56-63.
- Repeated channel decode fields for `UMCCH<n>_0` channel blocks:
  `BaseAddrCS0`, `AddrMaskCS01`, `AddrSelCS01`, and `AddrHashBank0` through `AddrHashBank5`.
- ECC state fields:
  `UMC_CONFIG`, `EccCtrl`, and `UmcLocalCap` appear for channels 0-3 in this chunk; channel 4 and later in this chunk do not expose those three groups before their ECC counters, matching the generated source as read.
- ECC counter fields:
  `EccErrCntSel` exports chip-select, interrupt, and enable fields; `EccErrCnt` exports the 16-bit count field.
- Performance monitor fields:
  `PerfMonCtlClk`, `PerfMonCtrClk_Lo`, `PerfMonCtrClk_Hi`, and per-counter `PerfMonCtl1..8` plus `PerfMonCtrN_Lo`/`PerfMonCtrN_Hi` groups for complete channel blocks. The range ends mid-definition for `UMCCH6_0_PerfMonCtl7`, so later chunks must cover the rest of channel 6 and subsequent channel blocks.

## Register Group Map

- Lines 27-85: MCA UMC status and address masks for `umc_w_phy_umc0_mca_ip_umc0_mca_map`.
- Lines 88-445: `umc_w_phy_umc0_umcch0_umcchdec`, channel 0 full block.
- Lines 448-805: channel 1 full block.
- Lines 808-1165: channel 2 full block.
- Lines 1168-1525: channel 3 full block.
- Lines 1528-1856: channel 4 block, including address decode, ECC counters, and performance monitor fields.
- Lines 1859-2187: channel 5 block with the same reduced set as channel 4.
- Lines 2190-2467: beginning of channel 6 block through `PerfMonCtl7` shifts.

Across lines 1-2467 there are 2,145 `#define` lines: 56 for the MCA register family, 316 each for channels 0-3, 290 each for channels 4-5, 244 for the partial channel 6 range, and the include-guard define.

## Integration Points

The direct consumers found in this source tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v6_7.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mca.c`

Both include this header along with `umc_6_7_0_offset.h`. The offset header supplies register addresses such as `regMCA_UMC_UMC0_MCUMC_STATUST0`, `regMCA_UMC_UMC0_MCUMC_ADDRT0`, `regUMCCH0_0_EccErrCntSel`, `regUMCCH0_0_EccErrCnt`, and `regUMCCH0_0_EccCtrl`; this header supplies the field layout once those registers have been read.

Representative usage:

- `umc_v6_7.c` checks `MCA_UMC_UMC0_MCUMC_STATUST0.Val`, `CECC`, `UECC`, `Deferred`, `PCC`, `UC`, and `TCC` to classify correctable and uncorrectable UMC errors.
- `umc_v6_7.c` extracts `MCA_UMC_UMC0_MCUMC_ADDRT0.ErrorAddr` to translate UMC error addresses to SoC physical addresses.
- `umc_v6_7.c` writes `UMCCH0_0_EccErrCntSel.EccErrCntCsSel` with `REG_SET_FIELD()` to select lower and upper chips before reading or resetting `UMCCH0_0_EccErrCnt.EccErrCnt`.
- `umc_v6_7.c` reads `UMCCH0_0_EccCtrl.UCFatalEn` to infer poison/fatal mode.
- `amdgpu_mca.c` uses the MCA status fields to provide common MCA correctable/uncorrectable counting helpers.

The repeated `UMCCH0_0` field names are also used for other channel instances because the driver computes per-channel register offsets separately. In that pattern, one logical field layout applies to several physical channel addresses.

## Control Flow

There is no executable control flow in this chunk. The effective control flow exists in the consumers:

1. A consumer reads a register with `RREG32_PCIE()` or `RREG64_PCIE()` using an address from `umc_6_7_0_offset.h` plus a calculated UMC/channel offset.
2. It passes the register value, register token, and field name to `REG_GET_FIELD()`.
3. The helper uses this header's `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` macros to extract the field.
4. For writes, `REG_SET_FIELD()` composes a new register value using the same mask/shift pair before `WREG32_PCIE()` or `WREG64_PCIE()` persists it to hardware.

Correctness therefore depends on each mask matching its shift and the ASIC hardware spec. A one-bit error in this header can invert runtime decisions even though this file itself compiles as simple constants.

## State And Persistence

The header has no local mutable state and no persistence. It describes persistent hardware state:

- MCA status bits are latched by hardware and cleared by writes in consumers such as `amdgpu_mca_reset_error_count()` and `umc_v6_7_query_error_address()`.
- ECC counter registers persist counts until selected and reset by UMC RAS code.
- ECC control bits such as `UCFatalEn` represent current hardware configuration that affects poison/fatal behavior.
- Address decode and hash masks describe programmed memory mapping state used by hardware and diagnostic code.
- Performance monitor control/counter fields describe hardware counters; this chunk does not show consumers for those fields, but the definitions expose the ABI for monitoring code.

## Dependencies

- AMDGPU register helper macros: `REG_GET_FIELD()` and `REG_SET_FIELD()` require the exact `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` naming convention used here.
- Register address macros from `umc_6_7_0_offset.h`.
- PCIe/MMIO register accessors such as `RREG32_PCIE()`, `RREG64_PCIE()`, `WREG32_PCIE()`, and `WREG64_PCIE()` in consumer files.
- RAS/UMC data structures in `amdgpu_umc`, `amdgpu_ras`, and `amdgpu_mca` code that decide how many UMC and channel instances are walked and how channel offsets are calculated.
- The generated register layout must match the target UMC 6.7.0 ASIC family. Nearby headers for UMC 6.1.1, 8.7.0, 8.10.0, and 12.0.0 show similar but not identical layouts.

## Risks

- Silent hardware misdecode: if a mask or shift is wrong, `REG_GET_FIELD()` returns plausible but incorrect status. RAS logic could undercount errors, overcount errors, misclassify correctable versus uncorrectable errors, or clear the wrong condition.
- Address translation errors: wrong `ErrorAddr` or `AddrLsb` definitions can lead diagnostics to report bad physical addresses for memory faults.
- Width and type sensitivity: MCA status/address masks use 64-bit values with an `L` suffix. On kernel-supported builds this is expected to be wide enough, but any nonstandard environment where `long` is 32-bit would truncate these constants. AMDGPU kernel builds normally target 64-bit architectures for this path.
- Generated repetition risk: many channel blocks are near-identical. Copy-generation defects can affect a subset of channels while still passing basic compilation.
- Partial chunk risk: this research range ends before the header's include guard closes and before channel 6 is complete. File-level conclusions must be merged with later chunks before deciding whole-header coverage.
- ABI drift risk: consumer code often uses `UMCCH0_0_*` field tokens against offset-adjusted channel addresses. That is valid only if all channel instances share the same field layout.

## Test Signals

- Compile/build signal: `umc_v6_7.c` and `amdgpu_mca.c` must compile with this header and `umc_6_7_0_offset.h`; missing or renamed field macros should fail at compile time in `REG_GET_FIELD()`/`REG_SET_FIELD()` call sites.
- Static consistency signal: for each exported field, `MASK >> SHIFT` should produce the expected contiguous field width; paired fields should not overlap within a register. This is especially valuable for generated channel blocks.
- RAS runtime signal: correctable error injection or firmware-provided ECC records should increment CE counts when `Val && CECC` is set and should log/translate `ErrorAddr` consistently.
- Uncorrectable/deferred runtime signal: status values with `Val` plus `Deferred`, `UECC`, `PCC`, `UC`, or `TCC` should increment UE paths in `umc_v6_7.c` and `amdgpu_mca.c`.
- Reset signal: after UMC RAS reset paths write zero or the initial CE counter value, follow-up reads should no longer report stale MCA status or ECC counter deltas.
- Cross-version review signal: compare generated UMC 6.7.0 fields against the corresponding hardware XML/spec or adjacent generated headers only where the ASIC version is expected to share layout; do not assume all UMC versions are interchangeable.

## Open Questions For Merge Lane

- Later chunks need to confirm the rest of channel 6, remaining channel blocks, and the closing include guard.
- Later chunks should determine whether channel 4+ intentionally omit `UMC_CONFIG`, `EccCtrl`, and `UmcLocalCap` in this generated layout or whether those groups appear elsewhere in the file.
- Whole-file reconciliation should verify whether any performance monitor fields in this large header are consumed outside the direct `umc_v6_7.c` and `amdgpu_mca.c` usage found for this chunk.
