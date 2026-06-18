# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h - subset-b-002393

## Scope

This chunk covers lines 16955-19453 of the generated AMD DPCS 4.2.3 shift/mask header. It is declarative hardware metadata: 2,099 `#define` lines and 400 register comment headings, with no C functions, structs, enums, runtime branches, allocation, locking, or software-owned persistent state.

The range begins at the final mask for `DPCSSYS_CR0_RAWLANE3_DIG_PMA_XF_RX_OVRD_OUT`, then completes the tail of the CR0 `RAWLANE3` PMA/TX/RX/ATE register-field definitions. It then defines complete repeated `DPCSSYS_CR0_RAWAONLANE0_DIG_*` through `RAWAONLANE3_DIG_*` always-on lane field layouts and ends inside `DPCSSYS_CR0_RAWAONLANEX_DIG_FAST_FLAGS_2`, where only the first eleven shift definitions are present in this chunk.

## Purpose

The header exposes generated `__SHIFT` and `_MASK` constants for DPCS CR0 register fields. AMDGPU display/link code can combine these constants with matching register offsets and register-access helpers to pack write values, decode read values, and avoid hard-coded bit numbers when programming the DPCS PHY.

Within this chunk, the purpose is lane 3 low-level control plus always-on lane calibration/status:

- `RAWLANE3_DIG_PMA_XF_*` maps PMA bridge handshakes and overrides for lane/supervisor/TX/RX paths, MPHY PWM/termination/asynchronous control, RX adaptation override output, and lane RTUNE request/ack state.
- `RAWLANE3_DIG_TX_CTL_*` and `RAWLANE3_DIG_RX_CTL_*` map lane-local TX/RX control policy: FSM enables, TX clock source/enables, RX data-enable timing, LOS mask counts, continuous DCC/off-cancellation/adaptation status, and OCLA/UPCS debug visibility.
- `RAWLANE3_DIG_PCS_XF_ATE_*` and related PCS-XF registers map automated-test and override paths for RX/TX rate, width, power state, low-power disable, loopback, detect-RX, vboost/iboost, MPLL selection/state, async controls, RX validity, and RX data enable.
- `RAWAONLANE0` through `RAWAONLANE3` provide repeated always-on lane telemetry and control fields for analog calibration, RX adaptation, DFE, phase adjustment, common calibration, signal detect, DCC, firmware configuration, and lane transceiver mode.
- `RAWAONLANEX` begins the generic lane-X always-on template/broadcast-style layout and mirrors the early always-on lane schema through part of `FAST_FLAGS_2`.

## Important Constants And Register Families

The public API in this range is the macro namespace. Each register comment is followed by field constants shaped as `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`. Most fields are 16-bit DPCS indirect-register fields represented as C integer constants with an `L` suffix. Consumers need the matching offset definitions from `dpcs_4_2_3_offset.h`, not this file alone, to address the hardware registers.

Key `RAWLANE3` families:

- PMA bridge tail: `DPCSSYS_CR0_RAWLANE3_DIG_PMA_XF_RX_PMA_IN` exposes RX PMA `ACK`; `LANE_RTUNE_CTL` requests lane RTUNE; `SUP_PMA_IN_1` exposes RTUNE acknowledge; `MPHY_OVRD_IN` and `MPHY_OVRD_OUT` force PWM word clock/data/clock, termination, PWM enable, PWM clock select, and async enable behavior; `RX_ADAPT_OVRD_OUT` forces the RX PMA IQ phase-adjust map.
- TX control: `TX_FSM_CTL` packs MPLL-off wait time and whether RX-detect is allowed in P0/P0S/P1/P2; `TX_CLK_CTL` controls TX clock enable, clock select, and async beacon wait time; `TX_DCC_CONT_STATUS`, `OCLA`, and `UPCS_OCLA` expose DCC continuous enable and debug capture controls.
- RX control: `RX_FSM_CTL` enables the RX control FSM and rate change in P1; `RX_LOS_MASK_CTL` sets the LOS mask count; `RX_DATA_EN_OVRD_CTL` packs data-enable override and internal reference tracking counts; `OFFCAN_CONT_STATUS`, `ADAPT_CONT_STATUS`, and `UPCS_OCLA` report continuous off-cancellation/adaptation and debug data/clock enables.
- ATE/test override path: `ATE_RX_OVRD_IN`, `ATE_TX_OVRD_IN`, `ATE_TX_OVRD_IN_1`, `MASTER_MPLL_LOOP`, `ATE_RX_OVRD_IN_1`, `ATE_RX_OVRD_IN_2`, `ATE_RX_OVRD_IN_3`, `RX_OVRD_OUT_2`, and `TX_OVRD_IN_2` cover forced RX/TX rate/width/pstate/LPD, RX-to-TX and TX-to-RX loopback, MPLL enable/selection/master-state override, detect-RX request, voltage/current boost, beacon and async data overrides, RX valid/data enable overrides, RX adaptation and EQ controls, PLL reference/VCO load values, LOS threshold, and continuous adaptation/off-cancellation controls.

Key `RAWAONLANE<n>` families, repeated for lanes 0, 1, 2, and 3:

- Analog and adaptation readback: `AFE_ATT_IDAC_OFST`, `AFE_CTLE_IDAC_OFST`, `RX_ADPT_IQ`, `RX_ADAPT_FOM`, `RX_ADPT_ATT`, `RX_ADPT_VGA`, `RX_ADPT_CTLE`, and `RX_ADPT_DFE_TAP1` through `TAP5` expose calibration/adaptation results.
- DFE and phase data: `DFE_SUMMER_ODD_IDAC_OFST`, `DFE_PHASE_*_VDAC_OFST`, `DFE_*_REF_LVL`, `DFE_DATA_*_VDAC_OFST`, `DFE_BYPASS_*_VDAC_OFST`, `DFE_ERROR_*_VDAC_OFST`, `RX_PHSADJ_LIN`, `RX_PHSADJ_MAP`, and `RX_IQ_PHASE_ADJUST` describe equalization, slicer, and phase-related values.
- Power and calibration status: `INIT_PWRUP_DONE`, `LANE_CMNCAL_MPLL_STATUS`, `LANE_CMNCAL_RCAL_STATUS`, `MPLLA_COARSE_TUNE`, `MPLLB_COARSE_TUNE`, and `MPLL_DISABLE` cover power-up done, phase-2 power-up done, common calibration init/done, coarse MPLL tune, and lane MPLL disable bits.
- Fast/adaptation control words: `FAST_FLAGS` packs RX startup/adapt/AFE/DFE/bypass/ref-level/IQ/power/VCO fast controls plus supervisor and TX RX-detect flags; `FAST_FLAGS_2` packs continuous calibration/adaptation, TX/RX DCC, VPHUD/VREF, TX RTUNE skip, and signal-detect calibration fast controls; `ADPT_CTL_0` through `ADPT_CTL_7` are full-word adaptation control values.
- Signal-detect and PMA override status: `TXRX_OVRD_IN`, `RX_LOS_MASK_CTL`, `RX_SIGDET_FILT_CTRL`, `STATS`, `RX_OVRD_OUT_1`, `RX_OVRD_OUT_2`, `RX_OVRD_OUT_3`, `RX_SIGDET_CAL`, `RX_SIGDET_HF_CODE`, `RX_SIGDET_LF_CODE`, and `RX_VREFGEN_EN` cover TX/RX disable override, LOS timing, signal-detect filtering, RX PMA squelch/VREF/termination/signal-detect overrides, and signal-detect calibration/code values.
- DCC, firmware, and mode fields: `CAL_IOFF_CODE`, `CAL_ICONST_CODE`, `CAL_VREFGEN_CODE`, `RX_DCC_CAL_*_CODE_*`, `TX_DCC_BANK_ADDR`, `TX_DCC_BANK_DATA`, `TX_DCC_CONT`, `MPLL_BG_CTL`, `SIGDET_OUT_OVRD`, `SIGDET_OUT_IN`, `FW_MM_CONFIG`, `FW_ADPT_CONFIG`, `FW_CALIB_CONFIG`, `LANE_XCVR_MODE_OVRD_IN`, `LANE_XCVR_MODE_IN`, `RX_SIGDET_CONFIG`, and `TX_DCC_CONFIG` define calibration code latches, DCC bank access, firmware configuration, lane mode override/readback, RX signal-detect filter counters, and TX DCC behavior.

The matching offset header places the visible `RAWLANE3` tail at offsets such as `0x3367` through `0x33c8`; `RAWAONLANE0` through `RAWAONLANE3` occupy regular windows `0x4000..0x4051`, `0x4100..0x4151`, `0x4200..0x4251`, and `0x4300..0x4351`; the `RAWAONLANEX` template begins at `0x7000` and reaches `FAST_FLAGS_2` at `0x702d` in this chunk.

## Control Flow

There is no executable software control flow in this chunk. The operational flow is implied by how consumers use the constants:

1. Select the DPCS 4.2.3 offset and shift/mask headers for the ASIC.
2. Address a register with the matching `ixDPCSSYS_CR0_*` offset macro.
3. Pack or extract a field using the `__SHIFT` and `_MASK` macros from this header.
4. For override registers, write both the override value and the paired override enable bit when forcing hardware behavior.
5. Poll status/ack/done fields to observe PMA/PCS handshakes, power-up completion, common calibration completion, RX adaptation state, signal detect, DCC calibration, or lane-mode readback.

The paired `*_OVRD_VAL` and `*_OVRD_EN` fields are important: a value bit without its enable bit usually only stages a forced value, while an enable bit with an unintended value can force reset, disable, loopback, clocking, adaptation, termination, or signal-detect behavior.

## State And Persistence

The macros do not store software state. They describe volatile hardware register fields in the GPU DPCS block.

- `RAWLANE3` fields represent active lane control, PMA/PCS handshakes, test overrides, and debug/status state for CR0 lane 3.
- `RAWAONLANE*` fields live in the raw always-on lane namespace. They expose calibration and adaptation state that may remain observable across some lane power transitions, but the header does not define retention or reset semantics.
- `*_STATUS`, `*_IN`, `*_DONE`, `*_ACK`, `*_CODE`, and adaptation readback fields should be treated as hardware snapshots that can change after retraining, link-rate changes, hotplug, reset, or power sequencing.
- `*_IRQ_CLR` is not present in this specific line range, but earlier adjacent RAWLANE3 sections have clear/mask/status semantics. This chunk's control/status fields must still be coordinated with those neighboring interrupt fields in the full-file report.
- Full-word `ADPT_CTL_*`, firmware config, DCC config, LOS mask counts, and override controls persist only as programmed hardware register state until changed or reset by the device.

## Dependencies And Integration Points

This header depends on AMDGPU's generated ASIC register ecosystem:

- `dpcs_4_2_3_offset.h` supplies the `ix...` register addresses for the same register names.
- AMD display/link code uses register helper macros and MMIO/indirect-register accessors to combine offsets, masks, shifts, and values.
- Related generated headers for other DPCS revisions, such as 4.2.2 or 4.2.0, have similarly named fields but must not be mixed with this 4.2.3 file unless the ASIC register database explicitly says they are compatible.

Integration points include:

- Display PHY bring-up and retraining flows that program lane rate, width, power state, MPLL selection, TX/RX request/reset, RX data enable, LOS masking, signal detect, and adaptation behavior.
- Low-level diagnostics, factory ATE, or debug tooling that force PCS/PMA signals through the `ATE_*`, `MPHY_OVRD_*`, `TXRX_OVRD_IN`, and `RX_OVRD_OUT_*` fields.
- Calibration telemetry paths that read AFE/CTLE/VGA/DFE/DCC/signal-detect codes and adaptation figures of merit from `RAWAONLANE*`.
- Firmware-assisted or microcontroller-assisted DPCS calibration, where `FW_MM_CONFIG`, `FW_ADPT_CONFIG`, `FW_CALIB_CONFIG`, and `ADPT_CTL_*` fields define configuration words shared with the hardware firmware path.
- Lane template handling through `RAWAONLANEX`; consumers must know from the offset/header conventions whether the `X` namespace is a broadcast alias, lane-selected indirect view, or generated template and must not blindly substitute it for a numbered physical lane.

## Risks

- The chunk starts and ends mid-register. Line 16955 contains only the reserved mask for `RAWLANE3_DIG_PMA_XF_RX_OVRD_OUT`; its shift and non-reserved masks are in the previous chunk. Line 19453 stops inside `RAWAONLANEX_DIG_FAST_FLAGS_2`; remaining shift and all mask definitions for that register continue in the next chunk.
- Repeated lane groups invite copy/paste or generator drift. `RAWAONLANE0` through `RAWAONLANE3` should match field-for-field except for lane prefixes and offset windows.
- Reserved masks must be preserved during read-modify-write sequences. Writing outside defined masks can alter reserved hardware bits.
- Override enable bits are risky in production paths. Enabling stale force values can unintentionally disable a TX/RX lane, change termination, force signal-detect state, enter loopback, select a wrong MPLL, or bypass calibration.
- The `RAWAONLANEX` namespace may have broader or indirect effects than numbered lane registers. Code must pair it with the correct addressing model.
- Masks are hardware ABI. Any mismatch between this 4.2.3 shift/mask header and its offset header, ASIC revision table, or register database can cause silent PHY programming failures.

## Test Signals

Useful validation signals for this chunk:

- Compile coverage that includes `dpcs_4_2_3_sh_mask.h` with `dpcs_4_2_3_offset.h` and exercises representative `RAWLANE3`, `RAWAONLANE<n>`, and `RAWAONLANEX` symbols.
- Generated-header consistency checks confirming every complete visible field has both `__SHIFT` and `_MASK` macros, while explicitly allowing the chunk-boundary exceptions at the first and last registers.
- Cross-lane parity checks comparing `RAWAONLANE0`, `RAWAONLANE1`, `RAWAONLANE2`, and `RAWAONLANE3` for identical register/field layouts and expected `0x100` offset strides.
- Hardware bring-up or simulation logs showing expected transitions in `ACK`, `DONE`, `INIT`, signal-detect, DCC, RX adaptation, and lane-mode readback fields after programming the corresponding controls.
- Register readback tests that verify packed writes preserve reserved bits and that `*_OVRD_EN` fields only affect hardware when intentionally set with the matching value field.
- Version checks ensuring DPCS 4.2.3 ASIC paths use this header instead of adjacent generated variants such as 4.2.2.

## Boundary Notes For Merge

The previous chunk should provide the full `DPCSSYS_CR0_RAWLANE3_DIG_PMA_XF_RX_OVRD_OUT` register definition before the reserved mask at line 16955. The next chunk should complete `DPCSSYS_CR0_RAWAONLANEX_DIG_FAST_FLAGS_2` and continue the `RAWAONLANEX` always-on lane tail. The final per-file report should reconcile these boundaries before making completeness claims for either register.
