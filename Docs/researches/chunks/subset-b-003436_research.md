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
