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
