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
