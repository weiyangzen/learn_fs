# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 91232-93607

## Purpose

This chunk is part of AMDGPU's generated NBIO 6.1 shift/mask header. It contains C preprocessor constants for bitfield positions and masks in the Synopsys DesignWare `DWC_E12MP_PHY_X4_NS_X4_2` PCIe PHY register namespace. The selected range starts in the middle of the lane 2 receiver adaptation-control block at `LANE2_DIG_RX_ADPTCTL_ADPT_CFG_5`, covers the rest of lane 2 adaptation, RX statistics, digital analog override/status, and analog TX/RX control registers, then covers most of the corresponding lane 3 block through `LANE3_ANA_TX_OVRD_MEAS`.

The definitions describe the hardware field geometry used to compose or decode 16-bit PHY register values. They are generated hardware metadata, not executable logic. Runtime code pairs these constants with register addresses from the matching NBIO 6.1 offset/SMN headers and AMDGPU register-access helpers.

## Important APIs, Types, and Macros

There are no C functions, structs, enums, typedefs, variables, allocations, or exported callable APIs in this chunk. The exported interface is a macro namespace with the standard AMD register-header pattern:

- `<REGISTER>__<FIELD>__SHIFT`: field bit offset.
- `<REGISTER>__<FIELD>_MASK`: field mask at its encoded register position.

The range contains 2,139 `#define` rows: 1,071 shift constants and 1,068 mask constants. The small mismatch is because the assigned range begins at a chunk boundary inside one register's field list.

Important register families in the chunk include:

- Lane 2 RX adaptation control and status: `LANE2_DIG_RX_ADPTCTL_ADPT_CFG_5` through `ADPT_CFG_9`, reset controls, ATT/VGA/CTLE/DFE tap status registers, DFE VDAC offsets, slicer controls, error slicer level, and bypass offsets.
- Lane 2 RX statistics: `LANE2_DIG_RX_STAT_*` load values, data masks, pattern/match controls, status controls, sample count, statistic counters, and calibration-comparison clock control.
- Lane 2 digital analog override/status: TX analog clock/data/refgen/reset/serial/data-rate override fields, TX termination and EQ override fields, RX control/power/VCO/calibration/AFE/scope/slicer override fields, IQ phase/sense controls, self-clearing analog update strobes, and analog status fields.
- Lane 2 analog TX/RX control: analog test-bus (`ATB`) selection, TX power/loopback/alternate bus controls, VBOOST, termination/boost codes, override clock, miscellaneous TX settings, RX DCC/power/control, CDR/AFE, calibration muxes, RX termination, slicer control, and vreg measurement fields.
- Lane 3 ASIC and PHY handoff: `LANE3_DIG_ASIC_*` override and live ASIC input/output mirrors for lane loopback, TX/RX reset, data enable, request/ack, P-state, rate, width, PLL selection, detect-RX, equalization, CDR/VCO, and adaptation enable/status.
- Lane 3 power, calibration, and receive path: TX/RX power-state timing and control, LBERT controls/errors, RX VCO calibration controls/timing/status, RX alignment, CDR/DPLL control/status/frequency bounds, full RX adaptation-control/status blocks, RX statistics, and digital analog TX/RX override/status blocks.
- The tail starts lane 3 analog TX measurement override with `LANE3_ANA_TX_OVRD_MEAS`, including clock shift, VCM hold, measurement sample, and pull-up/pull-down fields.

Field names show the major hardware domains: CTLE, VGA, ATT, DFE taps, slicers, CDR, DPLL, VCO calibration, LBERT, power states, TX equalization, termination, loopback, analog test bus, and RX/TX override handshakes.

## Control Flow and Runtime Behavior

This chunk has no direct control flow. Including the header only makes compile-time constants available. Operational flow exists in consumers:

1. Select a PHY register address from `nbio_6_1_offset.h` or `nbio_6_1_smn.h`.
2. Read or write the register through AMDGPU MMIO/SMN/SOC15 helpers.
3. Use the `__SHIFT` and `_MASK` constants directly, or indirectly through helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, and `WREG32_FIELD15`.
4. Hardware applies the programmed PHY state or returns status bits for the selected lane.

The generated ordering is still meaningful. Lane 2 is completed before lane 3 begins; lane 3 then repeats the same broad PHY programming model from ASIC handoff through RX adaptation and analog controls. Consumers should treat lane number as part of the register identity, not as a field inside a shared register.

## State and Persistence Behavior

The header itself owns no state and persists nothing. The state described here lives in NBIO PCIe PHY hardware registers.

Several fields represent writable controls that can persist until reset or reprogramming, including power-state encodings, override-enable bits, adaptation thresholds, DFE/CTLE/VGA/ATT tuning values, CDR/DPLL/VCO calibration settings, TX equalization values, TX/RX termination controls, and analog calibration mux selections. Other fields are live status or diagnostic state, such as adaptation done/status bits, VCO calibration status, DPLL frequency, CDR gain/status values, LBERT error counts, RX loss-of-signal, analog calibration result, and statistic counters.

Some fields are action-like or timing-sensitive rather than passive configuration. Examples include reset fields, `START_ASM1`, RX/TX request and acknowledgment handshakes, calibration enable/update strobes, self-clear-disable controls, link BERT synchronization, and clock/phase update bits. Incorrect programming can change link training, lane power sequencing, calibration behavior, or signal integrity.

## Dependencies and Integration Points

This generated mask header depends on matching generated register metadata:

- `nbio_6_1_offset.h` and `nbio_6_1_smn.h` provide the register addresses for these `DWC_E12MP_PHY_X4_NS_X4_2_*` names.
- `nbio_6_1_default.h` provides reset/default values for the same PHY registers.
- AMDGPU register helpers in the driver combine address, shift, and mask constants for read/modify/write operations.

Direct in-tree include users of `nbio_6_1_sh_mask.h` include `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, and Vega power-management include aggregators such as `pm/powerplay/hwmgr/vega10_inc.h` and `vega12_inc.h`. The exact macros in this chunk are part of the NBIO 6.1 PCIe PHY register vocabulary used by low-level bring-up, debug, link training, power management, virtualization diagnostics, and hardware validation paths, even if many are not referenced directly by hand-written C code.

Integration is source-tree aligned with the AMD GPU driver hierarchy: this is an ASIC register header under `drivers/gpu/drm/amd/include/asic_reg/nbio`, not Ceph filesystem logic despite the repository path prefix.

## Risks

- Generated-header drift is the primary risk. A wrong mask or shift silently makes every compiled consumer program or decode the wrong PHY bits.
- Lane repetition creates copy/paste risk. Lane 2 and lane 3 blocks should match where the hardware layout is repeated, except for the lane number and chunk-boundary truncation.
- Reserved-bit masks are common. Read/modify/write code must preserve reserved bits according to hardware requirements rather than blindly writing constants derived from named fields.
- PHY control fields are signal-integrity sensitive. Wrong CTLE/VGA/ATT/DFE, CDR/DPLL, VCO, slicer, or TX EQ settings can cause link training failures, degraded error rates, or unstable PCIe links.
- Override-enable fields can bypass normal firmware or hardware sequencing. Setting `*_OVRD_EN`, calibration overrides, power overrides, or analog update bits in the wrong context can conflict with BIOS/SMU/hardware-managed state.
- Status and control fields with similar names must not be interchanged. For example, adaptation status, VCO calibration status, analog status, and RX statistic counters are observational, while matching control/config registers can alter hardware behavior.
- This chunk starts and ends in the middle of larger generated lane sections. Final file-level research must reconcile adjacent chunks before making whole-file completeness claims.

## Test and Validation Signals

Useful validation is mostly compile-time, generated-header consistency, and hardware integration:

- Kernel build coverage for AMDGPU users that include `nbio_6_1_sh_mask.h` catches missing or renamed macros referenced by code.
- Static generated-header checks should verify every field has the expected paired shift/mask, masks are contiguous where required, and register names align across `nbio_6_1_offset.h`, `nbio_6_1_smn.h`, `nbio_6_1_default.h`, and `nbio_6_1_sh_mask.h`.
- Lane consistency checks should compare lane 2 and lane 3 repeated PHY blocks for identical field geometry except for lane prefixes and partial chunk boundaries.
- Hardware smoke tests on NBIO 6.1 ASICs should cover PCIe link training, link speed/width negotiation, suspend/resume or power-state transitions, and error-free operation under load.
- PHY diagnostics should inspect CDR/DPLL/VCO calibration status, adaptation done/status values, RX statistics, LBERT counters, and analog status fields after bring-up and under stress.
- Validation for debug or override paths should confirm that TX EQ, termination, RX AFE/CTLE/VGA/DFE, slicer, and analog test-bus settings are only applied in intended lab/debug contexts and do not leak into normal runtime configuration.
