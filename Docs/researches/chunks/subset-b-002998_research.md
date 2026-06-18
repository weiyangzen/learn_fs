# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h lines 8639-11461

## Scope

This chunk is a generated AMDGPU NBIO 6.1 default-value header segment. It contains only C preprocessor constants of the form `*_DEFAULT`; there are no functions, structures, enums, includes, allocation paths, locking, or direct register reads/writes in this range.

The range covers 2,805 `#define` rows. It starts in the middle of the `nbio_pipe_pcs_dwc_e12mp_phy_x4_ns0...mem_map` area, at `smnDWC_E12MP_PHY_X4_NS_X4_0_RAWCMNX_DIG_MEM_CMN4_B5_R14_DEFAULT`, proceeds through raw common memory, MPLL, lane digital, DXIO/KP, PCS, and PCIe x16 gasket defaults, then enters the `nbio_pipe_pcs_dwc_e12mp_phy_x4_ns1...mem_map` area. It ends in the middle of the `smnDWC_E12MP_PHY_X4_NS_X4_1_RAWCMN_DIG_MEM_CMN6` table at `B6_R3`.

Visible address-block markers in this slice are:

- `nbio_pipe_pcs_lcu_pcie_pcs_prime_phyx4_pcs_prime_dir`
- `nbio_lcu_kpfifo_kpfifo0_kpfifo_dir`
- `nbio_lcu_kpnp_kpnp0_kpnp_dir`
- `nbio_pipe_pcs_pcs_core0_dir`
- `nbio_pipe_pcs_pcs_pciex16_gaskt_pcs_pciex16_gaskt_dir`
- `nbio_pipe_pcs_dwc_e12mp_phy_x4_ns1_dwc_e12mp_phy_x4_ns_UP16_dwc_e12mp_phy_x4_ns_UP16_mem_map`

Because the chunk begins and ends inside generated register families, the merge lane should treat this as a partial source-file slice, not as a complete logical register block.

## Purpose

`nbio_6_1_default.h` is the reset/default-value half of AMD's generated NBIO 6.1 register interface. The companion NBIO headers provide offsets, SMN addresses, and field masks; this file gives the reset or expected default values for those registers. Driver code can include it when it needs ASIC-specific constants for comparing observed hardware state, programming known initial values, or carrying generated register metadata through build-time consumers.

This chunk focuses on the physical/link side of NBIO rather than PCI configuration-space defaults. The largest families describe Synopsys `DWC_E12MP_PHY_X4` PCIe PHY instances, including common memory table rows, MPLL spread-spectrum and bandwidth defaults, lane adaptation/calibration controls, RX/TX PCS/PMA handoff signals, analog lane defaults, and common/supervisor controls. Smaller sections cover DXIO linkage, KP FIFO/KPNP reset/link request defaults, PCS core global controls, per-lane x16 control/coefficients, and PCIe x16 gasket defaults.

## Macro Families and Coverage

The first 687 definitions are a continuation from the prior address block, covering the tail of the `NS_X4_0` PHY map. This includes:

- `RAWCMNX_DIG_MEM_CMN4` rows from `B5_R14` through `B7_R31`, then full `RAWCMNX_DIG_MEM_CMN5` and most of `RAWCMNX_DIG_MEM_CMN6`.
- `RAWCMNX_DIG_MPLLA_*` and `RAWCMNX_DIG_MPLLB_*` defaults such as bandwidth override and spread-spectrum override values.
- `RAWLANEX_DIG_*` lane defaults for PCS/PMA transfer, fast state-machine calibration/power-up controls, always-on adaptation values, DFE/AFE offsets, IRQ controls, TX/RX control, RTUNE, and RX data enable/loss-of-signal behavior.

The explicit intermediate address blocks then define:

- `smnDXIO_*`, `smnMAC_CAPABILITIES*`, and PCS aperture/capability/reset defaults in the prime PHY/PCS direction block.
- `smnKPFIFO0_*` defaults for HSCID, per-lane primary TX FIFO controls, and PCS/PMA soft reset.
- `smnKPNP_SNPS0_*` defaults for KPNP hardware version, lane ID/request control/status, PHY information/control, PMA control, and reset control.
- `smnPCS_PCIEX16_*` defaults in the PCS core, including global controls, soft reset, LCU control, per-lane controls for lanes 0 through 15, and `smnPCS_EXTENDED_CAP_DEFAULT`.
- `smnPCS_GLOBAL_CONTROL17` through `30`, eight lane-group mappings, and repeated `smnPCS_LANE{0..15}_CNTRL1/COEFF1/COEFF2/COEFF3` defaults in the PCIe x16 gasket block.

The final 1,953 definitions are the start and middle of the `NS_X4_1` PHY map. This portion includes:

- `SUP_DIG_*` and `SUP_ANA_*` defaults for ID codes, reference clock overrides, MPLLA/MPLLB overrides, PLL power-control timing thresholds, spread-spectrum frequency/phase, RTUNE status/set values, and analog switch/bandgap measurement defaults.
- Four lane families, `LANE0` through `LANE3`, covering ASIC RX/TX inputs/outputs, analog TX/RX defaults, RX adaptation configuration/status, CDR, DPLL bounds/frequency, LBERT, RX/TX power-state timing, status match/counter controls, VCO calibration, TX equalization override outputs, slicer/DAC controls, and PMA/PCS interface defaults.
- `RAWCMN_DIG_MEM_CMN2`, `CMN3`, `CMN4`, `CMN5`, and a partial `CMN6` table. The chunk ends while `CMN6` is still being enumerated.

Across the whole slice, 837 of the 2,805 default values are `0x00000000`. Nonzero patterns include repeated ID/default timing constants such as `0x000074cd`, `0x00000733`, `0x00000043`, `0x00005000`, `0x00000080`, `0x00000800`, `0xa6121400`, `0xa6141700`, and `0xd02c1d00`.

## Important APIs, Types, and Functions

There are no callable APIs, C types, or functions in this chunk. The exported interface is the generated macro namespace:

- `smnDWC_E12MP_PHY_X4_NS_X4_0_*_DEFAULT` for the first visible x4 PHY instance and its raw common/lane defaults.
- `smnDWC_E12MP_PHY_X4_NS_X4_1_*_DEFAULT` for the next x4 PHY instance, including supervisor, lane 0-3, and raw common memory defaults.
- `smnDXIO_*_DEFAULT`, `smnKPFIFO0_*_DEFAULT`, `smnKPNP_SNPS0_*_DEFAULT`, `smnPCS_*_DEFAULT`, and `smnMAC_*_DEFAULT` for DXIO, KP FIFO, KPNP, PCS, and MAC/PCS capability or reset defaults.

Consumers use these names as compile-time constants. Address selection comes from `nbio_6_1_offset.h` or `nbio_6_1_smn.h`; field extraction/composition comes from `nbio_6_1_sh_mask.h`.

## Control Flow

This chunk has no runtime control flow. Inclusion is controlled by the header guard at the top of `nbio_6_1_default.h`, outside this slice.

The inferred consumer flow is:

1. Include the NBIO 6.1 generated header set.
2. Select an NBIO/SMN register address from the offset or SMN header.
3. Optionally compare a hardware readback against the matching `*_DEFAULT` macro, or use the default as a base value before field updates.
4. Use `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_*`, or `RREG32_*` style helpers in AMDGPU code for actual register access.

The source reader should not infer any ordering or polling semantics from the macro order alone. The sequence mirrors the generated register database layout, not executable initialization code.

## State and Persistence Behavior

The header stores no software state and has no persistence behavior. It documents hardware reset/default values for NBIO, DXIO, PCS, KPNP, KP FIFO, and Synopsys PHY registers.

The represented hardware state persists in registers after reset according to the ASIC and firmware initialization sequence. Runtime code, firmware, PCIe link training, power management, soft reset, clock gating, PHY calibration, lane adaptation, and GPU reset can change those registers after their default state. Many status-like defaults are zero because the corresponding hardware state is produced later by calibration or link bring-up.

The raw memory-table defaults (`*_DIG_MEM_CMN*_B*_R*`) are dense generated constants rather than named bitfields. They should be treated as opaque vendor PHY programming data unless cross-referenced with the authoritative register database. Hand-editing individual values without the generator context is risky.

## Dependencies and Integration Points

This chunk integrates with:

- `nbio_6_1_offset.h`, `nbio_6_1_sh_mask.h`, and `nbio_6_1_smn.h`, which provide the companion address and field metadata for the same NBIO 6.1 register database.
- `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, which includes all NBIO 6.1 generated headers and uses SOC15/PCIE register helpers for NBIO setup, doorbells, interrupt control, clock gating, link power management, and related register programming.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h`, which includes NBIO 6.1 generated defaults, offsets, and masks alongside THM, MP, and GC generated headers for Vega10 power-management code.
- AMDGPU register helper conventions such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, and `REG_GET_FIELD`.
- Hardware/firmware expectations for Synopsys E12MP PHY calibration, PLL setup, spread-spectrum clocking, lane adaptation, PCIe PCS behavior, and DXIO/KP reset state.

## Risks and Edge Cases

- The file is generated. A one-value generation error can compile cleanly while causing subtle PHY, PCS, or link-training failures.
- This chunk has partial boundaries at both ends. It begins mid `NS_X4_0_RAWCMNX_DIG_MEM_CMN4` and ends mid `NS_X4_1_RAWCMN_DIG_MEM_CMN6`, so local counts are not complete family counts.
- Raw common memory tables encode opaque PHY programming. Treating `B*_R*` rows as independently meaningful registers without the generator spec can lead to incorrect patches.
- Several sections are highly repetitive across lanes and PHY instances. Copy/paste or generator skew between lane 0-3, lane group 0-7, and lane 0-15 PCS definitions may only show up as signal-integrity or link-width/speed problems.
- Default constants for reset, override, IRQ clear/status, calibration status, and power-state timing have different runtime semantics. Using a default value as a blind writeback can clear events, force overrides, or reset link-related blocks unexpectedly.
- Zero defaults are common but do not always mean "disabled forever"; many zero-valued status and calibration fields are expected to become nonzero after firmware, hardware FSMs, or link training run.
- PLL, spread-spectrum, RTUNE, RX/TX power-up timing, and DFE/AFE defaults are board/ASIC-sensitive. Incorrect values can affect PCIe stability, clock tolerance, or low-power transitions.
- PCS lane coefficient defaults are repeated for lanes 0-15. An incorrect per-lane value may only appear under specific negotiated widths, lane reversal, or degraded-link cases.

## Test Signals

Useful validation signals for this chunk:

- Build AMDGPU configurations that include `nbio_6_1_default.h`; missing, malformed, or duplicate macros should fail at compile time.
- Run generated-header consistency checks against the authoritative NBIO 6.1 register database, especially for `*_DEFAULT` alignment with `nbio_6_1_offset.h`, `nbio_6_1_smn.h`, and `nbio_6_1_sh_mask.h`.
- Compare repeated lane families for expected parity across `LANE0` through `LANE3` in the `NS_X4_1` PHY map and lanes 0 through 15 in PCS coefficient/control defaults.
- Compare the partial `NS_X4_0` and `NS_X4_1` raw common memory table patterns with neighboring chunks to catch boundary or generator ordering errors.
- Boot and suspend/resume tests on NBIO 6.1 hardware with PCIe link training at expected widths and speeds.
- PCIe diagnostics such as link speed/width readback, AER absence under idle and load, and stable retraining behavior after GPU reset or runtime power transitions.
- PHY/link stress tests under ASPM, clock gating, low-power transitions, and high-throughput DMA to expose bad PLL, RTUNE, PCS, or lane adaptation defaults.
- Register readback spot checks after reset or early init for high-signal constants such as `smnDXIO_HWDID_DEFAULT`, `smnPCS_PCIEX16_GLOBAL_CONTROL0_DEFAULT`, `smnPCS_LANE*_COEFF*`, supervisor ID-code defaults, and PLL timing defaults.
