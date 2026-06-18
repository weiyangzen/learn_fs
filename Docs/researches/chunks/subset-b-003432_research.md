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
