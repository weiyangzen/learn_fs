# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_7_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003432`: lines 1-2523, `Docs/researches/chunks/subset-b-003432_research.md`
- `subset-b-003433`: lines 2524-2626, `Docs/researches/chunks/subset-b-003433_research.md`

## Chunk Research

### subset-b-003432: lines 1-2523

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_7_0_offset.h lines 1-2523

## Scope

This chunk covers the start of the generated AMD UMC 6.7.0 register-offset header through line 2523. It includes the copyright and include guard, one MCA UMC status/address block, and generated offset definitions for UMC channel decode blocks from `umc0/ch0` through the beginning of `umc3/ch6`. The physical-source file continues past this chunk with the rest of `umc3/ch6`, `umc3/ch7`, and the closing guard; those trailing lines are outside this work item and are expected to be reconciled by the merge lane.

The chunk is a C preprocessor hardware register map. It does not define C functions, structs, enums, executable control flow, locks, allocation, or software-owned storage. Its contract is the exact register-offset and base-index names consumed by AMDGPU UMC/RAS code.

## Purpose

`umc_6_7_0_offset.h` names memory-controller registers for the UMC 6.7.0 IP block. Each hardware register is represented as a pair:

- `reg...` gives the register offset used with AMDGPU SOC15 register helpers.
- `reg..._BASE_IDX` gives the register base-index selector for the SOC15 register table.

The companion `umc_6_7_0_sh_mask.h` supplies bit fields for these registers. Runtime code combines both headers with helpers such as `SOC15_REG_OFFSET`, `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_PCIE`, `RREG64_PCIE`, `WREG32_PCIE`, and `WREG64_PCIE`.

## Important Macro Families

The first address block is `umc_w_phy_umc0_mca_ip_umc0_mca_map` at base address `0x50f00`. It defines MCA UMC registers:

- `regMCA_UMC_UMC0_MCUMC_STATUST0`
- `regMCA_UMC_UMC0_MCUMC_ADDRT0`
- `regMCA_UMC_UMC0_MCUMC_MISC0T0`
- `regMCA_UMC_UMC0_MCUMC_IPIDT0`
- `regMCA_UMC_UMC0_MCUMC_SYNDT0`

These names are used to read status, syndrome, IP ID, miscellaneous status, and error address information for UMC machine-check reporting.

The repeated `regUMCCH<channel>_<umc>_*` blocks describe per-channel UMC decode and monitoring registers. In this chunk there are 31 logical channel blocks: all channels 0-7 for UMC instances 0, 1, and 2, plus UMC instance 3 channels 0-6 up to line 2523. Each complete channel block follows the same generated naming scheme:

- Address decode registers: `BaseAddrCS0`, `AddrMaskCS01`, `AddrSelCS01`.
- Address hash selectors: `AddrHashBank0` through `AddrHashBank5`.
- Configuration and capability registers where present: `UMC_CONFIG`, `EccCtrl`, `UmcLocalCap`.
- ECC counter registers: `EccErrCntSel` and `EccErrCnt`.
- Performance monitor registers: `PerfMonCtlClk`, `PerfMonCtrClk_Lo`, `PerfMonCtrClk_Hi`, `PerfMonCtl1` through `PerfMonCtl8`, and paired `PerfMonCtr*_Lo`/`PerfMonCtr*_Hi` counters.

The first four UMC0 channel blocks have `BASE_IDX 0` and include more local configuration/capability symbols. Later blocks mostly use `BASE_IDX 1` and repeat channel offsets across wider address ranges, matching the non-linear register layout handled by `umc_v6_7.c`.

## Control Flow

There is no local control flow in the header. The runtime flow is in consumers, especially `drivers/gpu/drm/amd/amdgpu/umc_v6_7.c`.

The main consumer pattern is:

1. Select a logical UMC/channel in the AMDGPU RAS loop.
2. Compute a per-channel register displacement with `get_umc_v6_7_reg_offset()`. That helper flattens `umc_inst * channel_inst_num + ch_inst`, remaps it into non-linear four-channel register groups, and returns `adev->umc.channel_offs * ch_inst + UMC_V6_7_INST_DIST * umc_inst`.
3. Use a base macro such as `regUMCCH0_0_EccErrCntSel`, `regUMCCH0_0_EccErrCnt`, `regUMCCH0_0_EccCtrl`, `regMCA_UMC_UMC0_MCUMC_STATUST0`, or `regMCA_UMC_UMC0_MCUMC_ADDRT0`.
4. Add the computed displacement, multiply by four for byte addressing, and perform PCIe MMIO reads or writes.

This means many per-channel macros in this header are both direct generated documentation and a cross-check against the arithmetic accessor used by the C code. The driver often starts from the channel-0 macro plus an offset rather than spelling every generated `regUMCCHx_y_*` name at call sites.

## State and Persistence Behavior

The header stores no software state. It describes hardware register state in the UMC block:

- MCA status state for valid, correctable, uncorrectable, deferred, poisoned, and other memory-controller error conditions.
- MCA error address and syndrome state used to translate UMC channel addresses into system physical addresses.
- ECC counter selection and counter state for lower and higher chip-select paths.
- ECC fatal/poison-mode configuration through `EccCtrl`.
- Address decode, chip-select, and address-hash configuration state.
- Performance monitor selector and counter state.

Persistence is hardware-defined. Some registers may be sticky across parts of reset handling, some may be cleared by writes, and some may be initialized by firmware or the driver. The header does not encode write-one-to-clear, read-clear, reset-domain, or retention semantics; consumers must follow the UMC 6.7.0 programming model and existing AMDGPU RAS code.

## Dependencies and Integration Points

This header is included by:

- `drivers/gpu/drm/amd/amdgpu/umc_v6_7.c`, the main UMC 6.7 RAS implementation.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_mca.c`, generic MCA helpers that decode the MCA UMC status bit fields.

It also shares macro names with later UMC implementations such as `umc_v8_10.c` and `umc_v12_0.c`, which use their own offset headers but the same MCA register naming pattern.

The main integration point is AMDGPU RAS. `gmc_v9_0.c` wires IP version `6.7.0` to `umc_v6_7_ras`, sets `channel_inst_num`, `umc_inst_num`, `channel_offs`, and `retire_unit`, and chooses one of two channel index tables based on die ID. `umc_v6_7.c` then uses this header to query error counts, query error addresses, reset ECC counters, print MCA IPID/SYND/MISC registers, and query fatal/poison behavior.

The offset macros are also tied to:

- `umc_6_7_0_sh_mask.h` for field extraction and composition.
- `amdgpu_ras`, `amdgpu_umc`, and MCA helper code for error aggregation and reporting.
- AMDGPU PCIe MMIO register access helpers.
- Platform firmware and SMU/MCA flows that may have initialized or recorded ECC/MCA state before the driver queries it.

## Risks

- Hardware ABI drift is the primary risk. These generated constants must match UMC 6.7.0 exactly; a wrong offset or base index can read the wrong MMIO register or clear the wrong counter.
- The register layout is not linear. `umc_v6_7.c` explicitly compensates for non-linear UMC/channel placement. Any consumer that assumes `regUMCCHn_m_*` offsets can be linearly derived without the same mapping can report wrong channels or addresses.
- The chunk boundary cuts through the `umc3/ch6` block at `regUMCCH6_3_PerfMonCtr5_Lo_BASE_IDX`. Research or generation tools must not treat line 2523 as the complete source file.
- ECC counter selection is stateful: code writes `EccErrCntSel` to choose lower or higher chip-select before reading or clearing `EccErrCnt`. Races or missed restore semantics could skew counts.
- MCA status and address registers are 64-bit and accessed over PCIe. Using 32-bit accessors or forgetting the `* 4` byte-address conversion would corrupt reads.
- Address translation depends on channel-index tables and hash handling in `umc_v6_7.c`. Correct offsets alone are insufficient to produce correct physical addresses.
- Generated repetition makes review error-prone. A suffix mismatch between channel/UMC name, offset, and `_BASE_IDX` may compile cleanly while breaking only a specific memory channel.

## Test Signals

Useful validation signals for code consuming this chunk include:

- AMDGPU build coverage for `umc_v6_7.c` and `amdgpu_mca.c` with this header and `umc_6_7_0_sh_mask.h`.
- Hardware RAS tests on UMC IP `6.7.0` that inject or observe correctable and uncorrectable memory errors, then verify CE/UE counts, MCA status decoding, and physical-address translation.
- Tests that iterate all configured UMC/channel combinations and confirm `get_umc_v6_7_reg_offset()` points at live channel registers rather than aliases.
- Counter reset tests that select both chip-select paths through `EccErrCntSel`, write `UMC_V6_7_CE_CNT_INIT`, and verify subsequent reads do not carry stale counts.
- Poison/fatal-mode checks that read `regUMCCH0_0_EccCtrl` plus the computed offset and confirm `UCFatalEn` matches platform RAS policy.
- Suspend/resume and GPU-reset tests that confirm UMC error counters, MCA status, and RAS configuration are either preserved or reinitialized according to driver policy.
- Log/telemetry checks for `MCA STATUS`, `MCA IPID`, `MCA SYND`, `MCA MISC0`, and `Error Address(PA)` messages when valid MCA UMC errors are present.

### subset-b-003433: lines 2524-2626

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_7_0_offset.h lines 2524-2626

## Chunk Scope

- Work item: `subset-b-003433`
- Source chunk: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_7_0_offset.h`, lines 2524-2626
- Parent file role: generated AMDGPU UMC 6.7.0 register offset map.
- Chunk shape: the tail of `UMCCH6_3` performance-monitor counter definitions, the complete `umc_w_phy_umc3_umcch7_umcchdec` address block, and the closing include guard. Every visible register macro has a paired `*_BASE_IDX` macro set to `1`.

## Purpose

This chunk supplies symbolic register offsets for the final channels of UMC instance 3. It is not executable driver logic. Its purpose is to let AMDGPU code name UMC channel registers with generated symbols and resolve those symbols through SOC15 register-address helpers, rather than embedding raw offsets such as `0x180f29` in C code.

The visible register set covers three operational areas:

- Memory address decode configuration for `UMCCH7_3`, including base address, address mask, address selection, and address hash-bank registers.
- ECC error counter selection and counter registers for `UMCCH7_3`.
- UMC performance-monitor clock control and counters for `UMCCH7_3`, plus the ending performance counter 5-8 definitions for `UMCCH6_3`.

The block also terminates `_umc_6_7_0_OFFSET_HEADER`, so this is the last chunk of the generated offset header.

## Important APIs, Types, And Symbols

There are no C functions, structs, enums, or storage objects in this range. The public interface is entirely preprocessor constants:

- `regUMCCH6_3_PerfMonCtr5_Hi` through `regUMCCH6_3_PerfMonCtr8_Hi` finish the performance-monitor counter group for channel 6 of UMC instance 3.
- `regUMCCH7_3_BaseAddrCS0`, `regUMCCH7_3_AddrMaskCS01`, and `regUMCCH7_3_AddrSelCS01` name the channel-7 chip-select address decode registers.
- `regUMCCH7_3_AddrHashBank0` through `regUMCCH7_3_AddrHashBank5` name the per-bank address hashing registers used to describe or program how column and row bits participate in bank selection.
- `regUMCCH7_3_EccErrCntSel` and `regUMCCH7_3_EccErrCnt` identify the ECC counter select and counter data registers for channel 7.
- `regUMCCH7_3_PerfMonCtlClk`, `regUMCCH7_3_PerfMonCtrClk_Lo`, and `regUMCCH7_3_PerfMonCtrClk_Hi` identify the global performance-monitor clock/control counter path.
- `regUMCCH7_3_PerfMonCtl1` through `regUMCCH7_3_PerfMonCtl8` and their `PerfMonCtr*_Lo`/`PerfMonCtr*_Hi` companions identify eight programmable performance counters for channel 7.
- Each `reg*` macro has a `reg*_BASE_IDX` companion. In this chunk all base indices are `1`, which tells SOC15 register-offset machinery which generated UMC base table entry to combine with the raw offset.

The matching bit layouts live in `umc_6_7_0_sh_mask.h`. For example, the companion mask header defines ECC counter select fields such as `EccErrCntCsSel`, performance counter control fields such as `EventSelect`, `RdWrMask`, `BankSel`, `VCSel`, `SubChanMask`, and `Enable`, and high-counter fields such as `Overflow`, `ThreshCntEn`, and `ThreshCnt`.

## Control Flow

This header chunk has no executable control flow. Runtime behavior is in consumers that combine these offsets with channel arithmetic and register helpers.

The visible UMC 6.7 integration point is `amdgpu/umc_v6_7.c`. That file includes this offset header and the matching mask header, then uses `SOC15_REG_OFFSET(UMC, 0, regUMCCH0_0_EccErrCntSel)` and `SOC15_REG_OFFSET(UMC, 0, regUMCCH0_0_EccErrCnt)` as base channel-zero addresses. Runtime code computes a per-channel offset with `get_umc_v6_7_reg_offset()`, adds it to the channel-zero register address, multiplies by four, and accesses the resulting PCIE register address with `RREG32_PCIE`, `WREG32_PCIE`, or `RREG64_PCIE`.

That means the explicit `UMCCH7_3` symbols in this chunk document the generated hardware map for the final channel, while current generic UMC 6.7 code can also reach the same physical channel by adding the correct per-channel offset to channel-zero register symbols. Register dumps, diagnostics, generated validation, and any code that directly names channel-specific registers depend on these final channel macros remaining accurate.

## State And Persistence Behavior

The file stores no software state. All state represented by these macros is hardware register state in the UMC block:

- Address decode and hashing registers describe memory address mapping for channel 7. Their persistence is controlled by hardware reset domains, firmware setup, and any driver save/restore logic.
- ECC counter registers expose mutable error-accounting state. `EccErrCntSel` selects which chip-select or counter source is being observed, and `EccErrCnt` returns or accepts the counter value depending on access semantics.
- Performance-monitor control registers program event selection, masks, bank/subchannel filters, and enable bits.
- Performance-monitor counter registers hold low/high counter data, overflow state, and threshold counter fields.

The generated offset header does not encode whether a register is sticky, write-one-to-clear, reset-on-read, read-only, or writeable. Consumers must use the matching shift/mask definitions and the UMC programming model when clearing ECC counts, resetting counters, or enabling performance monitors.

## Dependencies And Integration Points

- Included by `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/umc_v6_7.c`, which implements UMC 6.7 RAS paths for querying correctable and uncorrectable ECC errors, resetting error counts, reading MCA status/address registers, and translating UMC error addresses.
- Included by `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_mca.c`, making the generated UMC 6.7 offsets part of AMDGPU MCA/RAS handling.
- Depends on `umc_6_7_0_sh_mask.h` for field-level shifts and masks. This offset header identifies register addresses; the mask header identifies the bit layout inside each register.
- Depends on the AMDGPU SOC15 register framework. The raw offsets and `BASE_IDX == 1` values are only meaningful when combined with generated UMC base addresses through helpers such as `SOC15_REG_OFFSET`.
- Integrates with AMDGPU register access macros such as `RREG32_PCIE`, `WREG32_PCIE`, and `RREG64_PCIE` in the UMC RAS path.
- Relates to `amdgpu_umc_loop_channels()`, `get_umc_v6_7_reg_offset()`, and the UMC channel index tables in `umc_v6_7.c`, which determine how logical UMC/channel instances map to non-linear register offsets and physical error-address channel bits.

## Risks And Edge Cases

- The chunk begins mid-family at `UMCCH6_3_PerfMonCtr5_Hi`. Merge/reconciliation must preserve continuity with the previous chunk for the full channel-6 performance-monitor story.
- This is the final block of the header. Missing or malformed closing guard text would affect every translation unit that includes the generated offset header.
- The visible `*_BASE_IDX` values are all `1`. A wrong base index can compile cleanly while resolving to the wrong UMC base window at runtime.
- The channel register layout is repetitive. Generator drift, a copied suffix error, or a single wrong offset in `UMCCH7_3` could affect only one channel and be difficult to catch through ordinary build testing.
- ECC counter access is selection-dependent. Writing or reading `EccErrCnt` without first programming `EccErrCntSel` for the intended chip-select can report the wrong count or reset the wrong counter.
- Address decode and hash-bank registers are mapping-critical. Misaddressed reads can produce bad error-address translation; misaddressed writes can corrupt memory-channel decode policy.
- Performance-monitor counters are split across low and high registers. Consumers that read low/high halves without hardware-prescribed ordering can observe torn counter values or miss overflow state.
- Performance-monitor control fields include enable and filter bits. Accidentally programming the wrong channel or bank filter can produce misleading performance data.

## Test And Validation Signals

- Build coverage with UMC 6.7 support should compile `umc_v6_7.c` and `amdgpu_mca.c` with this offset header and the companion mask header without unresolved or redefined symbols.
- Generated-header consistency checks should confirm every visible `reg*` macro in this chunk has the expected `reg*_BASE_IDX`, and that all visible base indices remain `1`.
- Cross-channel comparison should verify that `UMCCH7_3` follows the same register stride and family pattern as earlier `UMCCH*_3` blocks, while preserving the documented base address `0x753000`.
- ECC RAS testing on matching hardware should inject or observe correctable errors, select lower and higher chip counters with `EccErrCntSel`, read `EccErrCnt`, and verify that counts match MCA status and rasdaemon-visible reporting.
- Error count reset testing should confirm both chip-select counter paths return to `UMC_V6_7_CE_CNT_INIT` through the generic per-channel offset flow.
- Error-address validation should confirm channel-7 MCA/UMC errors are translated with the expected channel index and that address hash behavior matches firmware/hardware policy.
- Performance-monitor validation should program one or more `PerfMonCtl*` registers, read `PerfMonCtr*_Lo`/`Hi`, verify monotonic counter behavior under load, and check overflow/threshold fields.
- Suspend/resume and GPU reset tests should verify that ECC counters, performance-monitor controls, and address decode state are restored or intentionally reinitialized according to UMC 6.7 policy.

## Notes For Merge/Reconciliation

- This is a chunk-level report only for `subset-b-003433`; no final per-file report was produced.
- The chunk starts in the previous `UMCCH6_3` address block and then covers the complete `UMCCH7_3` block plus the header footer.
- Keep this report under `Docs/researches/chunks/`; the merge/reconciliation lane should create the final source-tree-aligned document after all chunks for `umc_6_7_0_offset.h` are available.
