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
