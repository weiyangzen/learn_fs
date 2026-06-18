# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 88865-91231

## Scope

This chunk covers a generated register shift/mask slice from the AMD NBIO 6.1 register header. The source is not executable C logic; it is a hardware register field map used by amdgpu code through register helpers such as `REG_SET_FIELD()`, `REG_GET_FIELD()`, `WREG32_SOC15()`, `RREG32_SOC15()`, and PCIe/SMN register accessors.

The line range begins inside the `DWC_E12MP_PHY_X4_NS_X4_2_LANE1_DIG_ASIC_TX_ASIC_OUT` register block, containing only its mask definitions after the shift definitions appeared in the previous chunk. It then covers the rest of a large lane 1 PCIe PHY group and the beginning of the corresponding lane 2 group. It ends on the marker for `DWC_E12MP_PHY_X4_NS_X4_2_LANE2_DIG_RX_ADPTCTL_ADPT_CFG_5`; the actual fields for that register continue in the next chunk.

The covered register families are:

- Lane 1 digital ASIC RX interface, RX equalization, RX CDR/VCO input and status, TX/RX power-state control, LBERT controls, VCO calibration, CDR/DPLL controls, RX adaptation controls, RX statistics/match counters, and digital-to-analog override/status surfaces.
- Lane 1 analog TX/RX controls for override measurement, power, alternate/test buses, term codes, boost, CDR/AFE, calibration muxes, slicers, and ATB/VREG measurement.
- Lane 2 digital ASIC lane/TX/RX override and ASIC interfaces, TX/RX power-state controls, LBERT controls, VCO calibration, CDR/DPLL controls, and the first RX adaptation configuration registers.

The paired address and default-value metadata for these same names lives in `nbio_6_1_offset.h` and `nbio_6_1_default.h`. This chunk supplies only the `__SHIFT` and `_MASK` constants needed to isolate fields inside the 16-bit or 32-bit register values.

## Purpose

`nbio_6_1_sh_mask.h` gives the driver symbolic bit positions and masks for NBIO 6.1 registers. In this chunk the symbols describe the Synopsys/DWC E12MP PCIe PHY lane register space under `DWC_E12MP_PHY_X4_NS_X4_2`, specifically the X4 lane 1 and lane 2 control/status blocks.

The practical purpose is to keep PHY programming code from hard-coding bit positions. A driver path can read a register, update fields such as `PSTATE`, `RATE`, `WIDTH`, `TX_P*_DATA_EN`, `RX_P*_CDR_TRACK_EN`, `RX_VCO_CAL_DONE`, `FREQ_BOUND_EN`, or `DFE_TAP*_ADPT_CODE`, then write the result back using the normal amdgpu register macros. The same mask names also make diagnostic paths more readable when extracting status fields like `LOS`, `VALID`, `ACK`, `RX_VCO_FSM_STATE`, `VCOCLK_TOO_FAST`, `PHUG_VALUE`, or adaptation completion bits.

This line range is especially hardware-facing. It covers per-lane PHY tuning and bring-up state, not high-level PCIe configuration such as BARs, doorbells, interrupts, or mailbox protocol. Mistakes here can affect link training, low-power transitions, signal equalization, loopback/test modes, and analog measurement hooks.

## Important APIs, Types, And Constants

There are no functions, structs, enums, or callable APIs in this chunk. The important exported items are preprocessor constants with the naming pattern:

- `REGISTER__FIELD__SHIFT`: the least-significant bit position of a field.
- `REGISTER__FIELD_MASK`: the bit mask to isolate or insert that field.

The dominant register groups and fields are:

- `DWC_E12MP_PHY_X4_NS_X4_2_LANE1_DIG_ASIC_RX_ASIC_IN_*` and lane 2 equivalents: digital RX control fields such as `RESET`, `INVERT`, `DATA_EN`, `REQ`, `LPD`, `PSTATE`, `RATE`, `WIDTH`, `DIV16P5_CLK_EN`, `ADAPT_AFE_EN`, `ADAPT_DFE_EN`, `CDR_TRACK_EN`, `CDR_SSC_EN`, `ALIGN_EN`, `DISABLE`, `LOS_THRSHLD`, `LOS_LPFS_EN`, `RX_TERM_EN`, and `RX_TERM_ACDC`.
- `DWC_E12MP_PHY_X4_NS_X4_2_LANE*_DIG_ASIC_RX_EQ_ASIC_IN_*`: RX equalizer field inputs, including attenuation level, VGA gains, CTLE boost/pole, and DFE tap 1.
- `DWC_E12MP_PHY_X4_NS_X4_2_LANE*_DIG_ASIC_RX_CDR_VCO_ASIC_IN_*`: RX CDR/VCO input load values, including low-frequency mode, ref load, and VCO load values.
- `DWC_E12MP_PHY_X4_NS_X4_2_LANE*_DIG_ASIC_RX_ASIC_OUT_0`: hardware status fields `ACK`, `LOS`, `VALID`, and `ADAPT_STS`.
- `DWC_E12MP_PHY_X4_NS_X4_2_LANE*_DIG_TX_PWRCTL_TX_PSTATE_P0/P0S/P1/P2`: per-TX-power-state enables for analog refgen, VCM hold, analog clock, word clock, analog reset, serial enable, digital clock, data enable, and RX detect allowance.
- `DWC_E12MP_PHY_X4_NS_X4_2_LANE*_DIG_RX_PWRCTL_RX_PSTATE_P0/P0S/P1/P2`: per-RX-power-state enables for analog refgen, VCM hold, analog clock, word clock, analog reset, DFE/VGA/CTLE/attenuator enables, digital clock, data enable, CDR tracking, continuous calibration, LOS, LPD, and clock-ready generation.
- `DWC_E12MP_PHY_X4_NS_X4_2_LANE*_DIG_TX_PWRCTL_TX_PWRUP_TIME_*` and `DIG_RX_PWRCTL_RX_PWRUP_TIME_*`: timing fields for analog power-up, digital power-up, data-enable/ready delays, CDR/VCO startup timing, adaptation timing, and lock timing.
- `DWC_E12MP_PHY_X4_NS_X4_2_LANE*_DIG_RX_VCOCAL_*`: VCO calibration control, threshold, period, count time, FSM/status, calibration done, VCO counter, and direction/correctness flags.
- `DWC_E12MP_PHY_X4_NS_X4_2_LANE*_DIG_RX_CDR_CDR_CTL_*`, `DIG_RX_CDR_STAT`, and `DIG_RX_DPLL_*`: CDR phase detector controls, SSC on/off counters, DPLL gain override fields, CDR status, DPLL frequency value, and upper/lower frequency bounds.
- `DWC_E12MP_PHY_X4_NS_X4_2_LANE*_DIG_RX_ADPTCTL_*`: RX adaptation setup and status for CTLE, VGA, attenuator, DFE taps, slicer offsets, thresholds, mu parameters, adaptation reset, and completion indicators. Lane 1 has a fuller adaptation/status/statistics set in this chunk; lane 2 reaches only through the marker for `ADPT_CFG_5`.
- `DWC_E12MP_PHY_X4_NS_X4_2_LANE1_DIG_RX_STAT_*`: lane 1 statistical measurement and match controls, including match masks/offsets, field selectors, window selection, sample count, and status counters.
- `DWC_E12MP_PHY_X4_NS_X4_2_LANE1_DIG_ANA_*` and `DWC_E12MP_PHY_X4_NS_X4_2_LANE1_ANA_*`: lane 1 digital-to-analog and analog override/status fields for TX override output, TX equalization, RX control/power/VCO override, RX calibration, DAC controls, AFE/CTLE/scope/slicer controls, IQ phase/sense, analog status, TX/RX ATB measurement, boost, termination, CDR/AFE, calibration muxes, and VREG hooks.

Most masks in this chunk are 16-bit values with an `L` suffix, matching PHY register widths such as `0x0001L`, `0x00FEL`, `0x1FFFL`, or `0xF800L`. Some generated names represent logical 32-bit constants elsewhere in the NBIO header, but this line range is dominated by 16-bit PHY subregister fields.

## Control Flow

This chunk has no runtime control flow. Its behavior is entirely compile-time symbol substitution:

1. A translation unit includes NBIO 6.1 register headers, usually both `nbio_6_1_offset.h` and `nbio_6_1_sh_mask.h`.
2. Driver code selects a register address, either through SOC15 MMIO macros or SMN/PCIe indirect accessors.
3. Code reads the current value when a read-modify-write is needed.
4. `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` uses `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` to clear and insert the requested field.
5. `REG_GET_FIELD(value, REGISTER, FIELD)` or manual mask/shift logic extracts status fields using the same generated constants.
6. The driver writes the resulting value back through the appropriate MMIO, PCIe, SMN, or indirect register path.

For the fields in this chunk, that runtime flow would typically be used in PHY bring-up, link training, power management, diagnostics, or board-specific tuning flows. The code directly visible in this repository uses `nbio_6_1_sh_mask.h` in `amdgpu/nbio_v6_1.c`, `amdgpu/mxgpu_ai.c`, PSP code, powerplay include bundles, and display resource code. The visible NBIO driver code mostly uses other NBIO fields from the same header family, while these lane-level DWC PHY fields are available for low-level programming paths and for any generated or platform-specific code that needs exact lane register fields.

## State And Persistence Behavior

The chunk defines no persistent software state. The macros disappear after preprocessing and do not allocate storage. The real state is in hardware registers on the GPU/NBIO PCIe PHY.

Writes to the fields described here can persist in device register state until the hardware block is reset, reinitialized, power-gated, placed into a different PCIe power state, or overwritten by firmware/driver code. Some status fields are read-only observations of hardware state, such as lane ACK/LOS/valid indicators, VCO calibration status, CDR status, counters, and adaptation completion bits. Some control fields drive state machines, such as power-state enables, CDR/VCO calibration controls, DPLL bounds, adaptation resets, test modes, and analog override enables.

Several fields interact with transient hardware handshakes:

- `REQ` and `ACK` fields model lane-level request/acknowledge transitions.
- `VALID`, `LOS`, and `ADAPT_STS` report RX status and adaptation state.
- VCO calibration fields expose calibration FSM state, done bits, counter values, and up/down/correct decisions.
- LBERT and RX statistics registers expose test/error counts that can change as traffic or built-in test patterns run.
- Override-enable fields can force values that bypass normal automatic PHY adaptation until cleared or reset.

Because this is register metadata, persistence behavior depends on hardware and firmware sequencing, not on any data structure in the header.

## Dependencies And Integration Points

The constants are part of a generated NBIO 6.1 register description set:

- `nbio_6_1_offset.h` provides the corresponding `mm*`, `ix*`, or `smn*` register addresses.
- `nbio_6_1_default.h` provides default reset values for many of the same `DWC_E12MP_PHY_X4_NS_X4_2_LANE*` registers.
- `nbio_6_1_smn.h` provides selected SMN addresses.
- `soc15.h`, amdgpu register helpers, and GPU MMIO/SMN/PCIe access macros supply the runtime read/write mechanisms.

Important source integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`: NBIO 6.1 implementation for memory-controller access enablement, doorbell aperture setup, interrupt control, HDP flush offsets/masks, clock gating, light sleep, LTR handling, and PCIe settings. It includes this header and uses the same mask/shift scheme heavily.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`: virtualized GPU mailbox code for AI-era devices. It includes this header and uses NBIO mailbox field masks from nearby portions of the same generated file.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v3_1.c`: PSP code includes the NBIO 6.1 offset header and works in the same device generation context.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h` and `vega12_inc.h`: include bundles pull in NBIO 6.1 defaults/offsets/masks for power-management code.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.c`: display resource code includes NBIO offsets for platform/resource setup.

At the hardware boundary, these definitions integrate with the PCIe PHY and NBIO block on Vega/AI-class AMD GPUs. Lane 1 and lane 2 symbols map to per-lane physical link controls. Multi-lane link behavior depends on programming the related lane groups consistently with the active link width and the hardware strap/default configuration.

## Risks And Edge Cases

The highest risk is silent hardware misprogramming from an incorrect mask or shift. A one-bit error can write reserved bits, leave a requested control bit unchanged, corrupt an adjacent field, or misread a status bit. For PHY fields this can surface as link training failures, unstable PCIe operation, poor signal margin, power-state transition failures, or diagnostics that report the wrong lane condition.

This chunk has boundary hazards for merge/reconciliation. The first lines are only the mask tail of `LANE1_DIG_ASIC_TX_ASIC_OUT`; a chunk-local parser will not see the matching `TX_ACK`, `DETRX_RESULT`, and reserved shift lines unless it reads the previous chunk. The final line is only the comment marker for `LANE2_DIG_RX_ADPTCTL_ADPT_CFG_5`; its field definitions are in the next chunk. Any generated documentation merger should avoid treating the ending marker as a complete register block.

Many lane 1 and lane 2 register names are intentionally near-identical. Copying a mask from `LANE1` into a `LANE2` access path, or vice versa, may compile cleanly because the field names and bit positions often match, but it can hide an address/register selection bug. The offset header and mask header must be kept in sync by register name.

Reserved masks are present throughout the chunk. Driver code should generally avoid writing arbitrary values into `RESERVED_*` fields unless the hardware programming guide explicitly requires a documented reset/default value. Read-modify-write helpers reduce this risk only when callers start from a current or known-good register value.

Several fields are analog or calibration related. Values for CTLE, VGA, DFE taps, VCO calibration, DAC offsets, termination, boost, and slicer levels are hardware-specific and can be board-, stepping-, firmware-, and link-speed-sensitive. A value that works for one ASIC revision or lane may degrade another.

Status and counter fields can be volatile. Polling logic that uses `ACK`, `VALID`, `LOS`, `RX_VCO_CAL_DONE`, `ASM1_DONE`, LBERT error counts, or RX statistic counters needs timeouts and should account for hardware state changes between reads.

The mask width is another edge case. Most fields here are 16-bit PHY subregister fields even though amdgpu helpers often manipulate `u32` register values. Callers need to use the correct address/access path and not assume that all NBIO registers in the header are full 32-bit MMIO registers with the same access semantics.

Because these headers are generated hardware descriptions, manual edits are fragile. If a definition is wrong, the durable fix should come from the register database/generation source or a synchronized update across offset/default/mask headers.

## Test Signals

Useful validation for this chunk includes:

- Build coverage for all translation units that include `nbio_6_1_sh_mask.h`, especially `amdgpu/nbio_v6_1.c`, `amdgpu/mxgpu_ai.c`, and powerplay/display include users. This catches missing or malformed macros introduced by generation or merge errors.
- Static consistency checks that every `REGISTER__FIELD__SHIFT` in this line range has a corresponding `REGISTER__FIELD_MASK` and that the mask aligns with the shift and field width. Boundary exceptions should account for the opening `LANE1_DIG_ASIC_TX_ASIC_OUT` tail and closing `LANE2_DIG_RX_ADPTCTL_ADPT_CFG_5` marker.
- Cross-header checks that every complete `DWC_E12MP_PHY_X4_NS_X4_2_LANE1` and `LANE2` register block in this chunk has a matching address in `nbio_6_1_offset.h` and, where applicable, a reset default in `nbio_6_1_default.h`.
- Hardware smoke tests on NBIO 6.1 devices covering PCIe link bring-up, negotiated link width/speed, suspend/resume, runtime power-management transitions, and reset flows. PHY power-state fields and CDR/VCO/adaptation fields should not destabilize link training or recovery.
- Diagnostics that read lane status fields after link training: RX `ACK`, `VALID`, `LOS`, VCO calibration done/correct/up bits, DPLL frequency bounds, and adaptation done/status fields should match expected hardware states.
- PCIe error monitoring under load, including AER counters, link retrain events, and unexpected downtraining. PHY mask errors may appear as intermittent link errors rather than compile-time failures.
- If any code path writes analog override, equalization, or adaptation fields, run signal-margin or stress tests at supported PCIe speeds and widths, with repeated cold boot, warm reset, suspend/resume, and power-gating cycles.
- For generated-header maintenance, diff regenerated `nbio_6_1_sh_mask.h`, `nbio_6_1_offset.h`, and `nbio_6_1_default.h` together. The lane 1/lane 2 DWC PHY register names should remain synchronized across mask, address, and default-value files.
