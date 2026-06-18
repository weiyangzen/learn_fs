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
