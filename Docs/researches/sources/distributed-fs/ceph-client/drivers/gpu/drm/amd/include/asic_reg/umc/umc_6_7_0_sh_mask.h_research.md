# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_7_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003434`: lines 1-2467, `Docs/researches/chunks/subset-b-003434_research.md`
- `subset-b-003435`: lines 2468-4929, `Docs/researches/chunks/subset-b-003435_research.md`
- `subset-b-003436`: lines 4930-7386, `Docs/researches/chunks/subset-b-003436_research.md`
- `subset-b-003437`: lines 7387-9846, `Docs/researches/chunks/subset-b-003437_research.md`
- `subset-b-003438`: lines 9847-10796, `Docs/researches/chunks/subset-b-003438_research.md`

## Chunk Research

### subset-b-003434: lines 1-2467

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

### subset-b-003435: lines 2468-4929

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_7_0_sh_mask.h lines 2468-4929

## Scope

This chunk covers lines 2,468 through 4,929 of the generated AMD UMC 6.7.0 shift/mask header. The range contains 2,154 preprocessor `#define` macros across 285 register-name families. It starts in the middle of the `UMCCH6_0` performance-monitor register group, covers full repeated UMC channel decoder/performance-monitor blocks for `UMCCH7_0` and `UMCCH0_1` through `UMCCH5_1`, and ends in the first part of `UMCCH6_1`.

The covered address blocks are:

- Tail of `umc_w_phy_umc0_umcch6_umcchdec`: `UMCCH6_0_PerfMonCtl7`, counter 7, `PerfMonCtl8`, and counter 8.
- Full `umc_w_phy_umc0_umcch7_umcchdec`: channel 7 of UMC instance 0.
- Full `umc_w_phy_umc1_umcch0_umcchdec` through `umc_w_phy_umc1_umcch5_umcchdec`: channels 0 through 5 of UMC instance 1.
- Start of `umc_w_phy_umc1_umcch6_umcchdec`: base address, address mask/selection, bank hash, ECC counter selection/count, performance clock control, and `PerfMonCtrClk_Lo`.

This is a generated C preprocessor bitfield map. It defines no functions, structs, variables, storage, branches, loops, or executable control flow.

## Purpose

The purpose of this header section is to expose the bit-level ABI for AMDGPU access to UMC 6.7.0 memory-controller channel registers. Each field is represented by generated constants using the standard AMD register-header convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask.

Driver code combines these macros with matching register offsets from `umc_6_7_0_offset.h` and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32`, `WREG32`, `RREG32_PCIE`, `WREG32_PCIE`, or SOC15 offset helpers. The offset header identifies where the per-channel register lives; this shift/mask header identifies how to pack and unpack fields inside each register value.

## Important Macro Families

### Channel Address Decode

Each full channel block begins with the memory address decode registers:

- `BaseAddrCS0` has `CSEnable` and `BaseAddr` fields. It controls whether chip select 0 participates in decoding and where that chip-select base begins.
- `AddrMaskCS01` exposes the chip-select address mask for CS0/CS1.
- `AddrSelCS01` maps address bits into DRAM bank and row fields with `BankBit0` through `BankBit4`, `RowLo`, and `RowHi`.
- `AddrHashBank0` through `AddrHashBank5` define bank-hash controls, each with `XorEnable`, `ColXor`, and `RowXor`.

The same layout repeats for `UMCCH7_0`, `UMCCH0_1`, `UMCCH1_1`, `UMCCH2_1`, `UMCCH3_1`, `UMCCH4_1`, `UMCCH5_1`, and the beginning of `UMCCH6_1`. These fields describe physical DRAM decode and swizzle/hash policy, so consumers must use the instance/channel-specific offset and the matching channel mapping table rather than treating one channel's name as globally unique hardware.

### ECC Error Counting

Each full channel block includes:

- `EccErrCntSel`, with `EccErrCntCsSel`, `EccErrInt`, and `EccErrCntEn`.
- `EccErrCnt`, with a 16-bit `EccErrCnt` field.

These fields are the per-channel ECC count selection and count surfaces. Nearby AMDGPU UMC code for UMC 6.x uses the analogous `UMCCH0_0_EccErrCntSel` and `UMCCH0_0_EccErrCnt` masks with `REG_SET_FIELD` and `REG_GET_FIELD` while adding per-channel offsets, so this generated layout is part of the RAS path that clears, enables, and queries correctable and uncorrectable UMC error counters.

### Performance Monitor Clock Control

Each full channel block defines:

- `PerfMonCtlClk`, with `GlblResetMsk`, `ClkGate`, `GlblReset`, `GlblMonEn`, `NumCounters`, and `CtrClkEn`.
- `PerfMonCtrClk_Lo`, with a full-width 32-bit `Data` field.
- `PerfMonCtrClk_Hi`, with low `Data` bits plus an `Overflow` bit.

`PerfMonCtlClk` gates and globally controls per-channel UMC performance monitoring. The clock counter is split into low/high registers; callers must read the pair consistently and account for the overflow bit if constructing a wider count.

The chunk ends before the `UMCCH6_1_PerfMonCtrClk_Hi` and later `UMCCH6_1` performance-counter fields, so the final merged research for the full source file must reconcile that continuation from the next chunk.

### Performance Monitor Event Counters

For each complete channel block, the generated layout contains `PerfMonCtl1` through `PerfMonCtl8`, with associated `PerfMonCtrN_Lo` and `PerfMonCtrN_Hi` registers. The control fields are regular across all eight counters:

- `EventSelect` chooses the hardware event.
- `RdWrMask`, `PriorityMask`, `ReqSizeMask`, `BankSel`, `VCSel`, and `SubChanMask` filter the counted traffic.
- `Enable` arms the counter.

The low counter register exposes full-width `Data`. The high counter register exposes `Data`, `Overflow`, `ThreshCntEn`, and `ThreshCnt`. The same pattern is visible at the opening tail for `UMCCH6_0` counters 7 and 8, throughout the complete `UMCCH7_0` and `UMCCH0_1` through `UMCCH5_1` blocks, and partially for `UMCCH6_1`.

These macros are the field definitions needed by any UMC performance telemetry/debug path that configures counters by event, request type, bank, virtual channel, and subchannel, then reads split low/high values.

## APIs, Types, and Functions

This chunk defines no callable APIs, C types, inline functions, or data structures. Its effective API is the macro naming contract consumed by AMDGPU register-access helpers. The important contract is that generated register field names must match the `REG_GET_FIELD(reg, REGISTER, FIELD)` and `REG_SET_FIELD(reg, REGISTER, FIELD, value)` expectations, where those helpers derive `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`.

The companion `umc_6_7_0_offset.h` supplies the `regUMCCH...` addresses and base indices for these same register names. Runtime code usually computes an instance/channel offset or uses SOC15 register macros, then applies the shift/mask definitions from this header to the value read from that address.

## Control Flow and State Behavior

There is no source-level runtime control flow in this chunk. The macros affect compiled code by determining how callers compose writes and decode reads.

The state represented by these macros lives in UMC hardware registers, not in this header. Important state includes:

- DRAM chip-select enable/base/mask state.
- DRAM address-to-bank/row selection and bank-hash XOR state.
- Per-channel ECC counter selection, interrupt selection, enable state, and count value.
- Per-channel performance-monitor global enable/reset/clock-gate state.
- Per-counter event selection, filters, enable bits, counter data, overflow state, threshold-count enable, and threshold count.

The macros do not encode register access semantics such as read-only, write-only, write-one-to-clear, sticky, reset-on-read, latch sequencing, or counter rollover behavior. Callers must get those rules from the hardware specification and the surrounding AMDGPU UMC/RAS/performance-monitor code.

## Dependencies and Integration Points

This header is coupled to:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_7_0_offset.h`, which defines the matching `regUMCCH...` register offsets and base indices.
- AMDGPU bitfield helpers such as `REG_GET_FIELD` and `REG_SET_FIELD`, which depend on the exact `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` names.
- AMDGPU MMIO/PCIe/SOC15 register access paths used by UMC code.
- UMC/RAS code that iterates UMC instances and channels, computes per-channel offsets, clears ECC counts, and queries ECC state.
- Any debug or performance path that programs UMC performance monitor event counters.

The immediate source-tree evidence is that UMC 6.x runtime code uses the same register-helper convention around `EccErrCntSel`, `EccErrCnt`, MCA UMC status fields, and per-channel offset calculation. UMC 6.7.0 uses `reg`-prefixed offset names in the companion offset header, so consumers must use the right header pair for this ASIC generation rather than mixing it with the older `mm`-prefixed UMC 6.1.x set.

## Risks

- Bitfield drift is high impact. A wrong mask or shift can alter unrelated address-decode, ECC, or performance-monitor bits.
- Address-decode fields (`BaseAddrCS0`, `AddrMaskCS01`, `AddrSelCS01`, and bank hash registers) describe memory routing. Incorrect writes can break channel decode, cause aliasing, or make error attribution unreliable.
- ECC counter selection is stateful. Changing `EccErrCntCsSel`, `EccErrInt`, or `EccErrCntEn` in the wrong order can produce misleading RAS counts or clear/sample the wrong chip select.
- Counter reads are split across low/high registers. Consumers need rollover/overflow handling when combining `PerfMonCtr*_Lo` and `PerfMonCtr*_Hi`.
- Performance-monitor control fields are highly repetitive. Mechanical generation or hand edits can easily corrupt one channel or counter while leaving adjacent copies correct.
- The chunk has partial families at both ends: it starts after part of `UMCCH6_0_PerfMonCtl7` and ends after `UMCCH6_1_PerfMonCtrClk_Lo`. Any final per-file report needs neighboring chunks to avoid presenting these as complete channel descriptions.
- Similar UMC generations use similar names with different offset conventions and sometimes different register coverage. Mixing `umc_6_7_0_sh_mask.h` with another generation's offset header would silently target the wrong fields or addresses.

## Test and Validation Signals

Useful validation is mostly compile-time and hardware/RAS integration coverage:

- Build AMDGPU code that includes `umc/umc_6_7_0_sh_mask.h` and its matching offset header; this catches missing, renamed, or malformed generated macros.
- Exercise UMC RAS paths that clear ECC counters, select chip-select/error sources, and query correctable/uncorrectable counts.
- Verify per-channel iteration against `adev->umc` instance/channel counts and offsets so `UMCCH*_1` registers are addressed on the intended UMC instance and channel.
- Use ECC injection or hardware error telemetry, where available, to confirm `EccErrCntSel` and `EccErrCnt` decode expected counts.
- Run performance-monitor tests that program `PerfMonCtlClk`, configure `PerfMonCtl1` through `PerfMonCtl8`, read low/high counter pairs, and validate overflow/threshold behavior.
- Validate memory-channel address mapping diagnostics against `BaseAddrCS0`, `AddrMaskCS01`, `AddrSelCS01`, and bank-hash fields when firmware or platform code exposes expected decode state.
- Include suspend/resume, GPU reset, and RAS recovery tests, because UMC address-decode, ECC counter, and performance-monitor registers may need to persist, reset, or be reinitialized according to ASIC policy.

### subset-b-003436: lines 4930-7386

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_7_0_sh_mask.h lines 4930-7386

## Scope

This chunk is a generated AMD UMC 6.7.0 register shift/mask header slice. It covers line 4930 through line 7386 of `umc_6_7_0_sh_mask.h`, starting inside the `UMCCH6_1` performance-monitor register family and ending at the start of `UMCCH5_2_PerfMonCtr5_Lo`. The source file pairs with `umc_6_7_0_offset.h`: this file supplies bit positions and masks, while the offset header supplies register addresses and base indices.

The covered blocks are:

- Tail of `umc_w_phy_umc1_umcch6_umcchdec`: `UMCCH6_1_PerfMonCtrClk_Hi`, `PerfMonCtl1` through `PerfMonCtl8`, and their low/high counters.
- Complete `umc_w_phy_umc1_umcch7_umcchdec`: `BaseAddrCS0`, `AddrMaskCS01`, `AddrSelCS01`, `AddrHashBank0` through `AddrHashBank5`, `EccErrCntSel`, `EccErrCnt`, `PerfMonCtlClk`, clock counter, and performance monitor counters 1-8.
- Complete `umc_w_phy_umc2_umcch0_umcchdec` through `umc_w_phy_umc2_umcch4_umcchdec`, each with the same base-address, address-hash, ECC-count, and perf-monitor register layout.
- Beginning of `umc_w_phy_umc2_umcch5_umcchdec`, through `UMCCH5_2_PerfMonCtr5_Lo`.

## Purpose

The header provides compile-time field constants for per-channel UMC hardware registers on AMD GPU memory-controller instances. Each `*_SHIFT` macro names a bit offset and each `*_MASK` macro names the field mask for extracting or setting fields through the AMDGPU register helpers, primarily `REG_GET_FIELD()` and `REG_SET_FIELD()`.

The important hardware concerns in this chunk are:

- DRAM address decode state: `BaseAddrCS0`, `AddrMaskCS01`, and `AddrSelCS01`.
- Channel address hashing: `AddrHashBank0` through `AddrHashBank5`.
- ECC counter selection and count readback: `EccErrCntSel` and `EccErrCnt`.
- UMC performance monitoring: `PerfMonCtlClk`, `PerfMonCtrClk_Lo/Hi`, and `PerfMonCtlN` plus `PerfMonCtrN_Lo/Hi` for counters 1-8.

There are no C functions or storage objects in this slice. The API surface is the macro namespace consumed by AMDGPU UMC/RAS code and any diagnostics that program these registers.

## Important Macro Families

`BaseAddrCS0` exposes `Val`, `LgcyMmioHoleEn`, `IntLvNumChan`, `IntLvAddrSel`, `DramBaseAddr`, and `DramBaseAddrSec`. These describe whether a chip-select base address is valid, whether legacy MMIO hole handling applies, how many channels participate in interleaving, how interleave address bits are selected, and the primary/secondary DRAM base address fields.

`AddrMaskCS01` exposes `AddrMask`, `LgcyMmioHole`, and `AddrMaskSec`. This is the matching address-mask register for the chip-select pair. A consumer must use this with the offset header address for the same channel instance; using the wrong channel's mask would decode a different physical DRAM aperture.

`AddrSelCS01` exposes `SocketId`, `DctSel`, `ChannelSel`, `RankSel`, `BankGroupSel`, `BankSel`, `RowSel`, and a `SubChanSec` field. These fields define which address bits feed socket, controller, channel, rank, bank-group, bank, row, and secondary subchannel selection.

`AddrHashBank0` through `AddrHashBank5` expose `XorEnable`, `ColXor`, and `RowXor`. These fields describe bank hash XOR selection. The active driver code for UMC 6.7 address conversion uses software channel hash helpers (`SET_CHANNEL_HASH()` in `umc_v6_7.c`) rather than reading these macros directly in the inspected call path, but these constants are the register-level description needed by lower-level debug or future decode logic.

`EccErrCntSel` exposes `EccErrCntCsSel`, `EccErrInt`, and `EccErrCntEn`. `EccErrCnt` exposes the 16-bit `EccErrCnt` field. In `umc_v6_7.c`, the driver programs the selector through the corresponding `UMCCH0_0_EccErrCntSel` field names and adds a computed per-channel offset; this chunk provides identical field layouts for the explicitly named channels covered here.

`PerfMonCtlClk` exposes `GlblResetMsk`, `ClkGate`, `GlblReset`, `GlblMonEn`, `NumCounters`, and `CtrClkEn`. This is the global per-channel performance-monitor control register. `PerfMonCtrClk_Lo` is a 32-bit low data register, and `PerfMonCtrClk_Hi` contains a 16-bit high `Data` field plus `Overflow`.

Each `PerfMonCtlN` exposes the same programming fields: `EventSelect`, `RdWrMask`, `PriorityMask`, `ReqSizeMask`, `BankSel`, `VCSel`, `SubChanMask`, and `Enable`. Each matching `PerfMonCtrN_Lo` contains 32 data bits. Each `PerfMonCtrN_Hi` contains the high 16 data bits plus `Overflow`, `ThreshCntEn`, and `ThreshCnt`. Together the low/high registers form a wide counter with optional threshold-count behavior.

## Control Flow and Integration

This header is included by `drivers/gpu/drm/amd/amdgpu/umc_v6_7.c` and `drivers/gpu/drm/amd/amdgpu/amdgpu_mca.c`. The active RAS control flow is centered in `umc_v6_7.c`:

- `amdgpu_umc_loop_channels()` iterates UMC and channel instances.
- `get_umc_v6_7_reg_offset()` maps logical `(umc_inst, ch_inst)` to a non-linear hardware register offset using `adev->umc.channel_inst_num`, `adev->umc.channel_offs`, and `UMC_V6_7_INST_DIST`.
- ECC count paths read and write `EccErrCntSel` and `EccErrCnt` through `RREG32_PCIE()` and `WREG32_PCIE()`.
- MCA status and address paths read `MCA_UMC_UMC0_MCUMC_*` registers through `RREG64_PCIE()` and parse status fields using macros from earlier in the same header.
- Error address conversion combines the MCA error address with `adev->umc.channel_idx_tbl` and software hash helpers, then emits `ras_err_data` records.

The driver normally uses the `UMCCH0_0` field names as a template and reaches other channels by adding the computed register offset to `regUMCCH0_0_*` addresses from `umc_6_7_0_offset.h`. The repeated `UMCCH6_1`, `UMCCH7_1`, and `UMCCH*_2` macros in this chunk still matter because they document that the concrete channel registers have the same bit layout and provide direct symbolic access for code that names a specific channel register.

`amdgpu_mca.c` also includes this header for MCA status field extraction. It counts correctable errors when `Val` and `CECC` are set, counts uncorrectable/deferred conditions when `Val` combines with `Deferred`, `UECC`, `PCC`, `UC`, or `TCC`, and resets status by writing zero to the MCA status address. Those MCA status fields are outside this line range, but this chunk's ECC counter fields feed the same UMC RAS reporting surface.

## State and Persistence Behavior

The macros are stateless compile-time constants. Runtime state is entirely in hardware registers and driver-owned RAS data structures:

- `EccErrCntSel` selects which chip-select counter is visible through `EccErrCnt`; changing the selector changes subsequent count reads for that channel.
- `EccErrCnt` is a hardware-maintained counter. `umc_v6_7.c` subtracts `UMC_V6_7_CE_CNT_INIT` from the field value and resets both lower and higher chip counters back to that init value after querying.
- MCA status registers persist error-valid state until cleared. `umc_v6_7_query_error_address()` writes zero to clear the status after address handling.
- Performance-monitor control registers program persistent hardware counting behavior until reset, disabled, clock gated, or reprogrammed. Counter high-register `Overflow` and threshold fields represent state accumulated by the hardware monitor.
- Address decode and hash registers represent memory-controller configuration. Driver code should treat them as hardware configuration, not ordinary mutable software state.

## Dependencies

This chunk depends on standard AMDGPU register helper conventions:

- `REG_GET_FIELD(value, REG, FIELD)` requires `REG__FIELD_MASK` and `REG__FIELD__SHIFT`.
- `REG_SET_FIELD(value, REG, FIELD, field_value)` uses the same mask/shift pair to update a field.
- `SOC15_REG_OFFSET(ip, inst, reg)` consumes address macros from `umc_6_7_0_offset.h`.
- `RREG32_PCIE()`, `WREG32_PCIE()`, `RREG64_PCIE()`, and `WREG64_PCIE()` perform actual MMIO/PCIe register access.

The source also depends on generated naming consistency. A typo or drift between `umc_6_7_0_offset.h` and `umc_6_7_0_sh_mask.h` would compile for unused direct-channel names but break consumers that use the affected macro with `REG_GET_FIELD()` or `REG_SET_FIELD()`.

## Risks and Edge Cases

- The requested line range starts after `UMCCH6_1_EccErrCntSel`, `UMCCH6_1_EccErrCnt`, and most of `UMCCH6_1_PerfMonCtlClk`; those immediately preceding definitions are needed for the complete `UMCCH6_1` story but are outside this chunk.
- The range ends before the rest of `UMCCH5_2_PerfMonCtr5_Lo`, `UMCCH5_2_PerfMonCtr5_Hi`, and counters 6-8. Any merged per-file research should reconcile the next chunk for the full `UMCCH5_2` performance-monitor family.
- These definitions are highly repetitive. Copy-generation errors are easy to miss by inspection, especially channel suffix mistakes such as `_1` versus `_2`, or mask/shift mismatches across channels.
- Several fields are wide and have high bits set, such as `Enable_MASK` at `0x80000000L` and `ThreshCnt_MASK` at `0xFFF00000L`. Consumers should use unsigned-width register values consistently to avoid sign-extension surprises in local arithmetic.
- ECC count reads are selector-dependent. Reading `EccErrCnt` without first programming the desired `EccErrCntCsSel` can report the wrong chip-select count.
- Performance counters combine low and high registers. Consumers must account for overflow and read ordering if they need stable snapshots under active counting.
- Address decode/hash fields are hardware-configuration sensitive. Programming them incorrectly would affect memory address mapping, not just software reporting.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware-integration checks:

- AMDGPU builds must compile any use of `REG_GET_FIELD()` or `REG_SET_FIELD()` with these macro names; missing `*_MASK` or `*_SHIFT` symbols fail at compile time.
- RAS ECC tests on UMC 6.7 hardware should show correct CE/UE counts while iterating all UMC/channel instances, including channels covered here by computed offsets.
- Injected or reported CE counts should reset to `UMC_V6_7_CE_CNT_INIT` after `umc_v6_7_query_ras_error_count()` runs.
- UE address reporting should produce stable physical-address records through `umc_v6_7_convert_error_address()` for channel indices in `umc_v6_7_channel_idx_tbl_first` or `umc_v6_7_channel_idx_tbl_second`.
- Register dumps should show that repeated channel families have identical field masks for the same logical register, while offsets differ by channel and UMC instance in `umc_6_7_0_offset.h`.
- Perf-monitor diagnostics should confirm that `PerfMonCtlN.Enable`, event selection, and high-register `Overflow` fields behave consistently for all channels in this chunk.

### subset-b-003437: lines 7387-9846

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_7_0_sh_mask.h lines 7387-9846

## Scope

This chunk covers generated shift and mask macros for AMD UMC 6.7.0 memory-controller channel registers. The range starts in the middle of `UMCCH5_2` performance-monitor counter 5 definitions, includes complete register field sets for `UMCCH6_2`, `UMCCH7_2`, and `UMCCH0_3` through `UMCCH4_3`, and ends in the early address-decode fields for `UMCCH5_3`.

The complete address blocks in this chunk are:

- `umc_w_phy_umc2_umcch6_umcchdec`
- `umc_w_phy_umc2_umcch7_umcchdec`
- `umc_w_phy_umc3_umcch0_umcchdec`
- `umc_w_phy_umc3_umcch1_umcchdec`
- `umc_w_phy_umc3_umcch2_umcchdec`
- `umc_w_phy_umc3_umcch3_umcchdec`
- `umc_w_phy_umc3_umcch4_umcchdec`

The chunk also contains the tail of `umc_w_phy_umc2_umcch5_umcchdec`, from `PerfMonCtr5_Lo__Data_MASK` through counter 8, and the beginning of `umc_w_phy_umc3_umcch5_umcchdec`, from `BaseAddrCS0` through `EccErrCntSel`.

This is a generated hardware bitfield header. It defines C preprocessor constants only. There are no functions, structs, global objects, allocation paths, locks, or executable branches in the chunk.

## Purpose

The purpose of this section is to provide the bit-level ABI used by AMDGPU UMC 6.7.0 code when reading, composing, and updating 32-bit UMC channel registers. Each register field is emitted in the standard generated form:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field's 32-bit mask.

The matching offset header, `umc_6_7_0_offset.h`, supplies register addresses such as `regUMCCH0_0_EccErrCntSel` and per-channel offsets. This mask header supplies the field extraction and insertion layout used by helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_PCIE`, and `WREG32_PCIE`.

## Important Macro Families

### Channel Address Decode

For each complete channel block, the chunk defines address-decode masks for:

- `BaseAddrCS0`: `CSEnable` at bit 0 and `BaseAddr` in bits 31:1.
- `AddrMaskCS01`: `AddrMask` in bits 31:1.
- `AddrSelCS01`: bank and row selection fields, including `BankBit0` through `BankBit4`, `RowLo`, and `RowHi`.
- `AddrHashBank0` through `AddrHashBank5`: `XorEnable`, `ColXor`, and `RowXor` fields.

These fields describe how UMC channel address bits are decoded, masked, and hashed into chip-select, bank, column, and row coordinates. They are important for memory error address translation and for any diagnostics that need to map a reported UMC address back to a physical address or memory topology. The ending `UMCCH5_3` section includes this same family only through `EccErrCntSel`; the rest of that channel continues in the next chunk.

### ECC Error Counter Selection

Each complete block includes:

- `EccErrCntSel`, with `EccErrCntCsSel`, `EccErrInt`, and `EccErrCntEn`.
- `EccErrCnt`, with the 16-bit `EccErrCnt` field.

These are the legacy per-channel correctable-error counter controls. `EccErrCntCsSel` selects the lower or higher chip-select path before `EccErrCnt` is read or reset. The field layout is directly consumed by `amdgpu/umc_v6_7.c`, which uses `REG_SET_FIELD(..., UMCCH0_0_EccErrCntSel, EccErrCntCsSel, ...)` to select each chip and `REG_GET_FIELD(..., UMCCH0_0_EccErrCnt, EccErrCnt)` to accumulate correctable error counts. The generated per-channel macro sets repeat the same field layout across physical channels, while the driver usually uses `UMCCH0_0` field names plus an address offset computed for the target channel.

### Performance Monitor Control and Counters

The bulk of each complete channel block defines one clock control/counter pair and eight event counters:

- `PerfMonCtlClk`: global reset mask, clock gate, global reset, global monitor enable, number of counters, and counter-clock enable.
- `PerfMonCtrClk_Lo` and `PerfMonCtrClk_Hi`: a 48-bit clock counter split into low 32 bits and high 16 bits, with high-register overflow and threshold-count fields.
- `PerfMonCtl1` through `PerfMonCtl8`: event selection and filter controls.
- `PerfMonCtr1_Lo` through `PerfMonCtr8_Lo`: low 32 bits of each event counter.
- `PerfMonCtr1_Hi` through `PerfMonCtr8_Hi`: high 16 bits plus overflow and threshold fields.

The performance-control registers share a repeated layout: `EventSelect` at bits 7:0, `RdWrMask` at bits 9:8, `PriorityMask` at bits 13:10, `ReqSizeMask` at bits 15:14, `BankSel` at bits 23:16, `VCSel` at bits 28:24, `SubChanMask` at bits 30:29, and `Enable` at bit 31. The counter-high registers share `Data`, `Overflow`, `ThreshCntEn`, and `ThreshCnt`. These fields provide hardware telemetry for UMC traffic, filtered by read/write direction, priority, request size, bank, virtual channel, and subchannel.

## Control Flow and State Behavior

This header chunk has no runtime control flow. Its behavior appears only after another C file includes it and uses the macros in register read-modify-write or field extraction operations.

The state described by the macros is persistent hardware state in UMC channel registers:

- Address-decode and hash registers are configuration state that controls or describes memory topology and address mapping.
- ECC counter registers hold hardware-maintained error counts and selector state. The selector must be programmed before reading or resetting the count for a specific chip-select path.
- Performance monitor control registers configure event selection, filters, enable bits, global reset, clock gating, and monitor enablement.
- Performance monitor counter registers are hardware-updated state. Low/high halves must be combined carefully, and overflow or threshold fields in the high halves are status-like state that can change while software samples it.

The chunk starts and ends mid-channel. A complete per-file view must reconcile adjacent chunks for the missing start of `UMCCH5_2` and the missing remainder of `UMCCH5_3`.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header convention used under `drivers/gpu/drm/amd/include/asic_reg/umc`:

- `umc_6_7_0_offset.h` provides the address and base-index macros for the register names defined here.
- `umc_6_7_0_sh_mask.h` provides the field masks and shifts. There is no `umc_6_7_0_default.h` companion in this tree.
- AMDGPU register helpers consume these definitions through `REG_GET_FIELD`, `REG_SET_FIELD`, `SOC15_REG_OFFSET`, and PCIe/MMIO accessors.

Direct source-tree integration points include:

- `amdgpu/umc_v6_7.c`, which includes both the offset and mask headers, computes non-linear UMC/channel offsets with `get_umc_v6_7_reg_offset()`, reads MCA status/address registers, programs `EccErrCntSel`, reads or clears `EccErrCnt`, and loops channels through `amdgpu_umc_loop_channels()`.
- `amdgpu/amdgpu_mca.c`, which includes this mask header for MCA/UMC status decoding through `REG_GET_FIELD`.
- AMDGPU RAS flows that query correctable and uncorrectable UMC errors, translate UMC error addresses into system physical addresses, fill retired-page records, reset error counters, and query poison/fatal mode.
- Potential diagnostics or performance tooling that programs the UMC performance monitor counter controls and samples the low/high counter halves.

The generated channel-specific names are repetitive but not interchangeable with other ASIC versions. Consumers must include the UMC 6.7.0 offset and mask set together and must preserve the channel-instance offset logic in `umc_v6_7.c`, because the register addresses are not linear across all UMC/channel instances.

## Risks

- Bitfield drift is high impact. An incorrect shift or mask can select the wrong chip-select counter, misread ECC counts, write reserved bits, or enable the wrong performance-monitor filter.
- ECC counter reads require sequencing. `EccErrCntCsSel` must be set before reading `EccErrCnt`; using a stale selector can attribute counts to the wrong chip-select path.
- Counter reset paths are stateful. `umc_v6_7.c` writes the initial counter value for lower and higher chip paths separately, so mask errors can leave one side uncleared or corrupt unrelated selector bits.
- Performance counters are split across low and high registers. Sampling without overflow handling can produce torn or misleading 48-bit counter values.
- Address-decode and hash fields affect error-address interpretation. Wrong `AddrSelCS01` or `AddrHashBank*` definitions can cause incorrect physical-address reconstruction or bad channel attribution in RAS reports.
- The register families are highly repetitive across channels. Copy-generation mistakes are easy to miss because most channels differ only by the `UMCCHx_y` prefix.
- This chunk begins and ends in partial channel blocks. Research or validation that treats it as an isolated complete channel map would miss part of `UMCCH5_2` and most of `UMCCH5_3`.

## Test and Validation Signals

Useful validation is primarily build and hardware/RAS coverage:

- Build AMDGPU with `umc_v6_7.c` and `amdgpu_mca.c` to catch missing, renamed, or syntactically invalid generated macros.
- Exercise UMC RAS correctable-error paths and confirm `EccErrCntCsSel` selects lower and higher chip paths and that `EccErrCnt` deltas match injected or observed correctable errors.
- Exercise uncorrectable and deferred MCA status paths and confirm status/address decoding is consistent with the UMC 6.7.0 hardware specification.
- Validate counter reset by checking both chip-select paths return to `UMC_V6_7_CE_CNT_INIT` after `umc_v6_7_reset_error_count()`.
- For address translation, compare reported retired pages and channel indices against known injected error addresses, especially where channel hash bits are involved.
- For performance monitoring, program representative `PerfMonCtl*` filters, sample `PerfMonCtr*_Lo/Hi`, and check overflow/threshold behavior under memory traffic.
- Run register-header consistency checks, if available, against the ASIC register database to verify that every `__SHIFT` and `_MASK` pair matches the generated UMC 6.7.0 layout for all covered channels.

### subset-b-003438: lines 9847-10796

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_7_0_sh_mask.h lines 9847-10796

## Scope

This chunk covers the final 950 lines of the generated AMD UMC 6.7.0 shift/mask header. It starts in the middle of the `UMCCH5_3` channel decoder block with the remaining `AddrHashBank2` mask and continues through the end of the file. The range defines 833 preprocessor macros for UMC channel instance 3, covering:

- The tail of `UMCCH5_3`: address hash-bank fields 3 through 5, ECC counter selection/count fields, the UMC performance monitor clock control, and performance monitor counters 1 through 8.
- The full `umc_w_phy_umc3_umcch6_umcchdec` address block: `UMCCH6_3` base/mask/select/hash address-decoder fields, ECC counter fields, and performance monitor fields.
- The full `umc_w_phy_umc3_umcch7_umcchdec` address block: the same `UMCCH7_3` address-decoder, ECC counter, and performance monitor field layouts.

The file section is declarative hardware ABI data only. It contains no C functions, structs, variables, runtime branches, loops, allocations, locks, or direct register accesses. Runtime behavior comes from AMDGPU code that includes this header together with `umc_6_7_0_offset.h` and uses register-access helpers.

## Purpose

The purpose of this generated header section is to name the bit positions for UMC 6.7.0 channel-decoder, ECC counter, and performance-monitor registers. Each field is represented by the usual generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the least-significant bit position of the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or compose that field in the raw register value.

The companion offset header supplies the register address macros, while this mask header supplies field layout. Consumers normally use these constants through AMDGPU helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_PCIE`, `WREG32_PCIE`, and `RREG64_PCIE`. For UMC 6.7.0 RAS flows, `umc_v6_7.c` computes per-channel register offsets and often uses the channel-0 field names against offset-adjusted addresses because the repeated channels share the same field layouts. The per-channel names in this chunk still matter as generated documentation and as a compile-time ABI for any consumer that chooses to address channel 5, 6, or 7 instance 3 directly.

## Important Macro Families

### Address Decode and Hashing

`UMCCH6_3_BaseAddrCS0` and `UMCCH7_3_BaseAddrCS0` define a chip-select enable bit and a high-width base-address field:

- `CSEnable` at bit 0.
- `BaseAddr` at bits 31:1.

`UMCCH6_3_AddrMaskCS01` and `UMCCH7_3_AddrMaskCS01` expose `AddrMask` at bits 31:1. These fields describe the address range mask for chip-select pair 0/1.

`UMCCH6_3_AddrSelCS01` and `UMCCH7_3_AddrSelCS01` describe how physical address bits are selected for memory-controller bank and row decode:

- `BankBit0` through `BankBit3` are four-bit selectors at bits 3:0, 7:4, 11:8, and 15:12.
- `BankBit4` is a five-bit selector at bits 20:16.
- `RowLo` and `RowHi` are four-bit row selector fields at bits 27:24 and 31:28.

`AddrHashBank0` through `AddrHashBank5` repeat the same hash layout for both channel 6 and channel 7, and the chunk also finishes `UMCCH5_3_AddrHashBank3` through `AddrHashBank5` plus the preceding `AddrHashBank2__RowXor_MASK` line from the previous register block:

- `XorEnable` at bit 0.
- `ColXor` at bits 13:1.
- `RowXor` at bits 31:14.

These macros describe the hardware address interleave and hashing rules for specific UMC channels. They are relevant to RAS error-address translation, memory-channel hashing, and debug code that needs to correlate UMC channel addresses with SoC physical addresses. The chunk itself does not perform that translation; in `umc_v6_7.c`, translation code reads MCA error-address fields and combines 8 KiB block, 256-byte block, offset, and channel-hash information using driver-side tables.

### ECC Counter Selection and Counts

`UMCCH5_3_EccErrCntSel`, `UMCCH6_3_EccErrCntSel`, and `UMCCH7_3_EccErrCntSel` all expose the same three fields:

- `EccErrCntCsSel` at bits 3:0 selects the chip-select or chip side whose ECC counter is visible.
- `EccErrInt` at bits 13:12 reports or selects ECC error interrupt state depending on the hardware semantics used by the caller.
- `EccErrCntEn` at bit 15 enables ECC error counting.

The corresponding `EccErrCnt` registers provide a 16-bit `EccErrCnt` field at bits 15:0. `umc_v6_7.c` uses the `UMCCH0_0_EccErrCntSel` and `UMCCH0_0_EccErrCnt` layouts with offset-adjusted channel addresses to select lower and higher chip counters, read the count, subtract `UMC_V6_7_CE_CNT_INIT`, and accumulate correctable-error totals. It also writes the initial counter value back during reset.

Because the field layout is repeated across channels, field drift in any generated channel macro would be a strong signal that the underlying register block is not as uniform as the current driver assumes. The chunk therefore acts as a consistency reference for per-channel ECC counter access even when the current implementation uses channel-0 symbols.

### Performance Monitor Clock Control

`UMCCH5_3_PerfMonCtlClk`, `UMCCH6_3_PerfMonCtlClk`, and `UMCCH7_3_PerfMonCtlClk` provide common control over the UMC performance-monitor block:

- `GlblResetMsk` at bits 8:0 selects counters affected by global reset.
- `ClkGate` at bit 22 controls counter clock gating.
- `GlblReset` at bit 24 requests a global monitor reset.
- `GlblMonEn` at bit 25 enables global monitoring.
- `NumCounters` at bits 29:26 reports or configures the available counter count.
- `CtrClkEn` at bit 31 enables the counter clock.

These fields gate and reset the monitor infrastructure used by the per-counter `PerfMonCtlN` and `PerfMonCtrN` registers. Since the generated masks expose write-capable control bits next to hardware status-like fields, callers must follow the register specification and avoid blind writes that accidentally reset, gate, or enable counters.

### Performance Monitor Counters 1 Through 8

For each covered channel, `PerfMonCtl1` through `PerfMonCtl8` share the same event-filter layout:

- `EventSelect` at bits 7:0.
- `RdWrMask` at bits 9:8.
- `PriorityMask` at bits 13:10.
- `ReqSizeMask` at bits 15:14.
- `BankSel` at bits 23:16.
- `VCSel` at bits 28:24.
- `SubChanMask` at bits 30:29.
- `Enable` at bit 31.

The counter data registers use paired low/high words. `PerfMonCtrN_Lo` exposes a full 32-bit `Data` field. `PerfMonCtrN_Hi` exposes:

- `Data` at bits 15:0, forming the high data portion of the counter value with the low word.
- `Overflow` at bit 16.
- `ThreshCntEn` at bits 19:18.
- `ThreshCnt` at bits 31:20.

`PerfMonCtrClk_Lo` and `PerfMonCtrClk_Hi` provide the same low/full and high/overflow pattern for the clock counter, except the high clock counter in this chunk has only `Data` and `Overflow`. The presence of eight per-channel performance counters plus the clock counter suggests a monitor block intended for memory-controller throughput, request classification, bank selection, virtual-channel selection, and threshold/overflow diagnostics.

## Control Flow

There is no executable control flow in this chunk. The implied runtime sequence for consumers is:

1. Resolve a UMC channel register address with `SOC15_REG_OFFSET` and the matching offset macro from `umc_6_7_0_offset.h`, or compute a channel-relative offset as `umc_v6_7.c` does with `get_umc_v6_7_reg_offset()`.
2. Read a raw 32-bit or 64-bit register value through an MMIO/PCIe helper.
3. Extract a field with `REG_GET_FIELD` and the generated `__SHIFT`/`_MASK` pair, or update a field with `REG_SET_FIELD`.
4. Write the updated raw value back if the hardware register is writable and the register's side-effect rules allow it.

The important control-flow property is that the header does not encode ordering, locking, polling, clear-on-read, write-one-to-clear, or reset semantics. Those behaviors must be enforced by the caller and by the hardware programming guide.

## State and Persistence Behavior

The macros describe persistent hardware state, not driver-owned memory:

- Address base, mask, select, and hash fields describe channel address decode state that persists in UMC registers until hardware reset or explicit reprogramming.
- ECC counter selection and count fields expose hardware error-count state. Driver code can change the selected counter and reset counts by writing the counter register.
- Performance monitor control fields configure monitor state, and counter data/overflow fields expose hardware accumulation state. Counter state is persistent across reads until reset, overflow handling, or block reconfiguration.

The header contributes no storage of its own. Persistence risks are therefore all hardware-side: a bad mask can make software preserve, clear, or overwrite the wrong register bits when composing a read-modify-write value.

## Dependencies and Integration Points

Direct dependencies are limited to C preprocessing: consumers include this header and the matching `umc_6_7_0_offset.h`. Practical integration points in this tree include:

- `drivers/gpu/drm/amd/amdgpu/umc_v6_7.c`, which includes the 6.7.0 UMC offset and mask headers, loops over UMC channels, computes non-linear per-channel register offsets, selects ECC counters, reads counts, resets counters, and translates MCA error addresses.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_mca.c`, which includes the same UMC 6.7.0 headers for MCA status field decoding used by RAS error counting. This file is more focused on MCA register fields than on the channel decoder fields in this chunk, but it shares the same generated hardware ABI source.
- AMDGPU register helper macros (`REG_GET_FIELD`, `REG_SET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG64_PCIE`) that consume the generated `__SHIFT` and `_MASK` definitions.
- RAS and UMC state in `struct amdgpu_device`, especially `adev->umc.channel_inst_num`, `adev->umc.channel_offs`, `adev->umc.channel_idx_tbl`, and RAS ECC tables used to map per-channel MCA data into user-visible error counts and addresses.

The `UMCCH6_3` and `UMCCH7_3` names line up with address-block comments for `umc_w_phy_umc3_umcch6_umcchdec` and `umc_w_phy_umc3_umcch7_umcchdec`. Any generated update must keep these names synchronized with the companion offset file so that a register address and a field layout refer to the same hardware register.

## Risks and Edge Cases

- Generated layout drift: the driver currently relies on repeated channel layouts. If channel 5/6/7 instance 3 fields diverge from channel 0 while code continues using channel-0 masks with offset-adjusted addresses, `REG_GET_FIELD` and `REG_SET_FIELD` operations may silently decode or write the wrong bits.
- Register-name mixups: many `PerfMonCtlN` and `PerfMonCtrN` blocks are mechanically identical. A copy/generation error in the register prefix can target the wrong counter or channel while retaining plausible masks.
- Partial chunk boundary: line 9847 begins with only `UMCCH5_3_AddrHashBank2__RowXor_MASK`; the matching comment and shifts for `AddrHashBank2` are in the previous chunk. Merge/reconciliation should combine adjacent chunk research before treating `AddrHashBank2` as fully covered.
- Read-modify-write side effects: control registers such as `PerfMonCtlClk` mix reset, enable, and clock-gating fields. A caller using broad masks or stale raw values can reset counters, disable counting, or change gating unexpectedly.
- Counter sizing and overflow: performance counters use low/high words and separate overflow bits. Consumers need an ordered read strategy and overflow handling; this header only gives bit positions.
- ECC counter selection race: `EccErrCntSel` changes which counter `EccErrCnt` exposes. Concurrent or interrupt-driven readers could observe a counter selected by another path unless access is serialized at a higher layer.
- Address decode sensitivity: base/mask/select/hash fields directly affect memory-channel address interpretation. Incorrect decode constants can corrupt RAS address reporting or any diagnostic that maps UMC-local addresses back to physical addresses.

## Test Signals

Useful validation signals for this chunk are mostly build-time, static, and hardware/RAS oriented:

- Compile AMDGPU with UMC 6.7.0 support enabled so every referenced `UMCCH*_3_*` macro and companion offset symbol resolves cleanly.
- Run static checks or generated-header comparison against AMD's register source to confirm that each `__SHIFT`/`_MASK` pair matches the hardware specification and that repeated channel layouts are intentionally identical.
- Exercise UMC RAS paths on supported hardware: inject or observe correctable ECC events, confirm lower/higher chip counter selection through `EccErrCntCsSel`, verify counts after subtracting `UMC_V6_7_CE_CNT_INIT`, and confirm reset writes restore the initial value.
- Validate MCA/UMC error-address reporting on hardware with known channel mappings; the reported physical address should remain stable across the channel index tables and hash reconstruction used by `umc_v6_7.c`.
- If performance monitoring is exposed through debug or profiling paths, verify that enabling `GlblMonEn`/`CtrClkEn`, programming `PerfMonCtlN`, reading low/high counter words, and detecting `Overflow` produce monotonic counters under memory traffic.
- Review generated-header churn together with `umc_6_7_0_offset.h`; field-name, channel-name, or address-block changes should be treated as hardware ABI changes, not cosmetic edits.
