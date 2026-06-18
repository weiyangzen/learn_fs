# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 16697-19122

## Scope

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice. It contains preprocessor constants only: no C functions, structs, enums, branches, allocation paths, locks, MMIO calls, or software-owned persistent state. Its public surface is the generated register-field macro namespace consumed by AMDGPU display and PHY register-table code.

The requested range is 2,426 lines. It contains 2,082 `#define` entries and 344 register-comment blocks; because some comment/register blocks are tiny and the chunk starts and ends mid-register, those counts do not imply 344 complete logical registers. The slice begins inside `DPCSSYS_CR0_RAWLANE3_DIG_PCS_XF_RX_OVRD_IN_1`, after several shift definitions from the previous chunk, and ends inside `DPCSSYS_CR0_RAWAONLANE2_DIG_RX_DCC_CAL_QCM_CODE_0`, before that register's final mask lines and subsequent lane2 calibration registers.

This is AMD display/link PHY metadata despite the repository path containing `ceph-client`. It has no Ceph, filesystem, distributed-storage, network, or disk persistence behavior.

## Purpose

The purpose of this chunk is to publish bit positions and masks for DPCS CR0 RAW lane 3 and RAW always-on lane 0/1/2 registers in the DPCS 4.2.0 hardware block. Runtime code combines these generated constants with the companion `dpcs_4_2_0_offset.h` register-address definitions and AMDGPU register helpers to program or decode individual hardware fields without open-coded bit arithmetic.

Major covered hardware areas are:

- Tail of RAWLANE3 PCS RX override input 1, then RAWLANE3 PCS RX override/input/output/status fields for RX request/reset, link rate, width, pstate, low-power detect, CDR VCO low-frequency state, adaptation request/continuous/off-candidate controls, VCO/ref load values, equalizer settings, TX pre/main/post direction hints, lane number, ATE overrides, RX equalization delta, and RX/TX termination controls.
- RAWLANE3 FSM control/status and fast-sequence timing registers for RX startup calibration, adaptation, AFE/DFE calibration, bypass/ref-level/IQ calibration, supervisor and TX common-mode/RX-detect sequences, RX power-up, VCO wait/calibration, continuous adaptation/calibration, common calibration status, fast flags, CR locking, TX DCC flags/status, OCLA selection, TX EQ update flag, RCAL status, and RX IQ phase offset.
- RAWLANE3 IRQ control registers for RX reset/request/rate/pstate/adapt request/adapt disable events, corresponding clear registers, IRQ mask registers, lane transceiver-mode events, phase-2 calibration request/disable events, RX-to-TX serial loopback events, DCC on-demand interrupt, and TX reset/request events.
- RAWLANE3 PMA transfer fields for lane/supervisor/TX/RX override and real PMA inputs/outputs, lane RTUNE control, MPHY override/status, and RX adaptation output handoff.
- RAWLANE3 TX/RX control registers for TX FSM/clock control, DCC continuous status, OCLA/upstream OCLA selection, RX FSM control, RX loss-of-signal masking, RX data-enable override, off-candidate and adaptation continuous status.
- RAWLANE3 PCS ATE and master MPLL loop registers, plus late RX/TX override fields.
- RAWAONLANE0 and RAWAONLANE1 digital always-on lane fields for analog-front-end offsets, RX adaptation outputs, DFE offsets/reference levels, phase adjustment, MPLLA/MPLLB coarse tuning, power-up done, adaptation status, fast flags, slicer controls, common calibration status, adaptation control registers, MPLL disable, signal-detect filtering/calibration, RX override outputs, VREF/calibration code registers, RX DCC calibration code banks, TX DCC bank/data/continuous controls, MPLL bandgap control, signal-detect overrides/input, firmware configuration, transceiver mode, and TX/RX signal-detect/DCC configuration.
- Start of RAWAONLANE2, covering the same always-on adaptation, DFE, phase, MPLL, initialization, slicer, common calibration, adaptation-control, MPLL-disable, signal-detect, RX override, VREF/calibration, and the first RX DCC calibration code registers through `RX_DCC_CAL_QCM_CODE_0`.

## Important Macros And Field Families

There are no callable APIs or C data types in this range. The important API is the generated macro naming contract:

- `DPCSSYS_CR0_<REGISTER>__<FIELD>__SHIFT`: least-significant bit offset for a field.
- `DPCSSYS_CR0_<REGISTER>__<FIELD>_MASK`: already shifted mask for the same field.
- Instance prefixes such as `RAWLANE3` and `RAWAONLANE0/1/2` are part of the ABI between generated headers, offset headers, and register table macros.

Important macro families in this chunk include:

- `DPCSSYS_CR0_RAWLANE3_DIG_PCS_XF_*`: PCS-facing lane 3 control and status for RX/TX request/reset handshakes, rate/width/pstate, AFE/DFE adaptation controls, equalizer/load values, acknowledge/status outputs, ATE override values, termination controls, and master MPLL loop selection.
- `DPCSSYS_CR0_RAWLANE3_DIG_FSM_*`: finite-state-machine timing, status, and debug fields. These include fast RX startup/adaptation/calibration phases, continuous calibration/adaptation flags, common calibration status, CR lock, TX DCC status, OCLA, and TX equalization update signaling.
- `DPCSSYS_CR0_RAWLANE3_DIG_IRQ_CTL_*`: interrupt latch, clear, and mask fields for lane 3 RX/TX state changes and calibration-related events.
- `DPCSSYS_CR0_RAWLANE3_DIG_PMA_XF_*`: digital-to-PMA and PMA-to-digital handoff fields for supervisor, lane, TX, RX, RTUNE, MPHY, and RX adaptation signals.
- `DPCSSYS_CR0_RAWLANE3_DIG_TX_CTL_*` and `DPCSSYS_CR0_RAWLANE3_DIG_RX_CTL_*`: compact control/status fields for TX/RX FSM behavior, clock/DCC status, OCLA selection, loss-of-signal masking, data-enable override, and continuous adaptation/off-candidate status.
- `DPCSSYS_CR0_RAWAONLANE[0-2]_DIG_AFE_*`, `RX_ADPT_*`, `DFE_*`, and `RX_SLICER_*`: always-on lane readback/control fields for receiver adaptation results, analog offsets, DFE references/taps, phase adjust, slicer controls, and figure-of-merit reporting.
- `DPCSSYS_CR0_RAWAONLANE[0-2]_DIG_MPLLA_*`, `MPLLB_*`, `MPLL_DISABLE`, `MPLL_BG_CTL`, and `LANE_CMNCAL_*`: MPLL coarse tuning, disable control, bandgap, and common calibration status fields.
- `DPCSSYS_CR0_RAWAONLANE[0-2]_DIG_FAST_FLAGS*`, `ADPT_CTL_*`, `FW_MM_CONFIG`, `FW_ADPT_CONFIG`, and `FW_CALIB_CONFIG`: fast calibration/adaptation flags and firmware-visible configuration knobs.
- `DPCSSYS_CR0_RAWAONLANE[0-2]_DIG_RX_SIGDET_*`, `SIGDET_OUT_*`, `RX_VREFGEN_EN`, `CAL_*`, and `RX_DCC_CAL_*`: signal-detect filtering/calibration, VREF generation, calibration code, and RX DCC calibration code fields.
- `DPCSSYS_CR0_RAWAONLANE[0-1]_DIG_TX_DCC_*`, `LANE_XCVR_MODE_*`, `RX_SIGDET_CONFIG`, and `TX_DCC_CONFIG`: TX DCC bank/data/continuous access, transceiver mode override/input, and lane signal-detect/DCC configuration fields. Lane2 begins the same family but continues in the next chunk.

Most masks are 16-bit CR-style masks (`0x0000FFFFL` or narrower bit ranges). Reserved fields are emitted explicitly; they are part of the generated description of the register layout but should not be treated as safe software write targets without an authoritative PHY sequence.

## Control Flow And Runtime Integration

This header has no runtime control flow. Runtime behavior is created by code that includes `dpcs_4_2_0_offset.h` and `dpcs_4_2_0_sh_mask.h`, constructs register/field tables, and uses AMDGPU display register helpers to access the hardware.

Visible integration in this tree includes:

1. `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` includes `dpcs/dpcs_4_2_0_offset.h` and this shift/mask header.
2. That DCN 3.1 resource file expands DPCS register and mask/shift tables with macros such as `DPCS_DCN31_REG_LIST(id)`, `DPCS_DCN31_MASK_SH_LIST(__SHIFT)`, and `DPCS_DCN31_MASK_SH_LIST(_MASK)`.
3. The companion offset header maps the same internal CR0 names to addresses in `dpcssys_cr0_rdpcstxcrind`; for example the RAWLANE3 PCS/FSM/IRQ families in this chunk correspond to `ixDPCSSYS_CR0_RAWLANE3_*` address definitions.
4. Higher-level AMD display code uses generic register helpers and link/PHY programming sequences to perform masked read/modify/write or polling operations using the generated address, mask, and shift metadata.

The represented hardware flow is typically: select ASIC-owned or software-override controls, sequence PCS/PMA RX/TX request and reset handshakes, start or monitor FSM calibration/adaptation phases, handle IRQ latches/clears, configure PMA/MPHY handoff values, and read always-on lane adaptation/calibration/status fields.

## State And Persistence Behavior

The file itself has no mutable state and persists nothing. All state described by these macros lives in DPCS hardware registers.

State represented by this chunk includes:

- RAWLANE3 PCS/PMA lane state: RX/TX request/reset, pstate/rate/width, adaptation request/ack/FOM, RX equalization/load values, CDR low-frequency state, TX pre/main/post direction, lane numbering, termination, and ATE override state.
- RAWLANE3 FSM state: fast startup/adaptation/calibration timing, continuous calibration/adaptation flags, common calibration and RCAL status, CR lock, TX DCC status, OCLA selection, and TX EQ update flags.
- RAWLANE3 IRQ state: interrupt request latches, clear bits, mask bits, lane transceiver mode events, phase-2 calibration events, loopback events, DCC on-demand events, and TX reset/request events.
- RAWAONLANE0/1/2 always-on lane state: analog offsets, RX adaptation values and done flags, DFE tap/reference values, phase adjustment, slicer controls, MPLL coarse tuning and disable state, initialization complete state, signal detect filtering/calibration, VREF/calibration codes, RX DCC calibration code readbacks, firmware configuration, transceiver mode, and TX DCC configuration where present in this slice.

Persistence is hardware-defined. Values generally survive only until the relevant lane, DPCS block, display engine, power domain, or GPU is reset or power-gated, and they may need to be restored or recalculated during modeset, hotplug retraining, suspend/resume, runtime power management, or ASIC reset. Status, clear, and handshake fields may be read-only, sticky, self-clearing, write-one-to-clear, or valid only while related clocks and power are present; this generated header does not encode those access semantics.

## Dependencies

This chunk depends on the matching generated DPCS 4.2.0 offset header. Shift/mask constants alone do not identify MMIO or internal CR addresses.

Key dependencies are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h`, which provides `reg*`, base-index, and `ixDPCSSYS_CR0_*` address definitions for the fields described here.
- AMDGPU display register-helper infrastructure, including token-paste macros and masked read/write/update helpers that consume generated `__SHIFT` and `_MASK` constants.
- DCN 3.1 display resource initialization, which includes this DPCS 4.2.0 generation and builds DPCS register and mask/shift lists for the hardware generation.
- Link encoder, PHY bring-up, link training, hotplug, power-management, suspend/resume, diagnostics, and firmware-facing code that programs or observes DPCS CR0 lane and always-on lane registers.
- The authoritative AMD silicon register database that generated this header and its companion offset header. Manual edits are risky unless synchronized with that source and every generated consumer table.

## Integration Points

Primary integration points are generated macro names used by register tables and masked field helpers. A consumer referencing a field such as `DPCSSYS_CR0_RAWLANE3_DIG_IRQ_CTL_IRQ_MASK__RX_REQ_IRQ_MASK_MASK` or `DPCSSYS_CR0_RAWAONLANE1_DIG_RX_ADPT_CTLE__RX_ADPT_CTLE_MASK` relies on this file for the exact bit geometry.

Integration surfaces include:

- Link training and lane bring-up: PCS RX/TX request/reset, pstate/rate/width, adaptation controls, termination controls, and PMA handoff fields.
- PHY calibration and adaptation: FSM fast-calibration flags/timers, continuous RX calibration/adaptation, RX AFE/DFE/CTLE/VGA values, phase adjustment, VREF/calibration codes, DCC code readbacks, and common calibration status.
- Interrupt handling and event tracking: RX/TX request/reset/rate/pstate/adaptation event latches, clears, and masks, plus lane transceiver-mode, phase-2 calibration, serial loopback, and DCC on-demand events.
- Diagnostics and observability: OCLA/upstream OCLA selection, FSM memory/status monitors, fast flags, TX DCC status, RX adaptation FOM, signal-detect status/configuration, and firmware configuration registers.
- Multi-lane mapping: RAWLANE3 and RAWAONLANE0/1/2 use repeated field layouts with lane-specific names. Address tables must keep these names aligned with the physical lane and always-on lane instances.

## Risks And Edge Cases

- Wrong shift/mask values can compile cleanly while writing the wrong bit in a PHY register, corrupting adjacent fields or decoding status incorrectly.
- The chunk starts inside `DPCSSYS_CR0_RAWLANE3_DIG_PCS_XF_RX_OVRD_IN_1`; the first several `__SHIFT` definitions for that register are in the previous chunk, while this chunk contains later shifts and masks. Pairing checks must account for this boundary.
- The chunk ends inside `DPCSSYS_CR0_RAWAONLANE2_DIG_RX_DCC_CAL_QCM_CODE_0`; the next chunk owns the remaining mask lines and the following lane2 DCC calibration code registers.
- Override fields are sensitive because they can transfer ownership from normal ASIC/FSM control to software-forced values. Bad masks can hold reset/request/adaptation/termination signals in the wrong state.
- FSM and calibration fields are timing and sequencing dependent. Incorrect constants can cause link-training timeouts, unstable clocks, calibration loops, bad RCAL/DCC results, or resume-only failures.
- IRQ clear and mask fields may have side effects. Misidentifying a latch, clear, or mask bit can hide real events, create interrupt storms, or leave stale status latched.
- Always-on lane status fields are often used for debug, firmware calibration, or marginal-signal diagnosis. A field drift can look like a sink/cable/link-training problem rather than an obvious software regression.
- Repeated RAWAONLANE0/1/2 families are copy-error prone. Mixing lane instance prefixes can work on one lane topology and fail on another.
- Reserved masks are present throughout the generated file. Generic read-modify-write code should preserve reserved bits unless a silicon-authored sequence explicitly programs them.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Build AMDGPU display support with DCN 3.1/DPCS 4.2.0 enabled. Missing or renamed generated macros should fail in resource table construction or in code that token-pastes DPCS field names.
- Run mechanical consistency checks against AMD's authoritative DPCS 4.2.0 register database: complete fields should have matching `__SHIFT` and `_MASK` definitions with expected widths, while allowing the known start/end chunk-boundary exceptions.
- Compare this range with nearby generated DPCS versions, such as DPCS 4.2.2/4.2.3 or older 3.x layouts, only where the hardware team expects compatible register layouts. Do not assume cross-generation interchangeability.
- Exercise DisplayPort and HDMI hotplug, modeset, lane-count changes, link-rate changes, link retraining, suspend/resume, runtime power management, and GPU reset on hardware using DPCS 4.2.0.
- Watch link-training logs and display diagnostics for RX/TX request/reset timeouts, clock-not-ready, adaptation failures, IRQ storms, calibration timeout, DCC/RCAL failures, unstable link clocks, blank displays, or resume-only display loss.
- Validate high-bandwidth and marginal-signal scenarios that stress TX/RX termination, RX adaptation, CTLE/VGA/DFE values, signal-detect configuration, VREF/calibration codes, and DCC calibration readbacks.
- Use register dumps, debugfs, firmware traces, or vendor register-validation tooling where available to confirm that CR0 address/data accesses hit the intended RAWLANE3 and RAWAONLANE instances.

## Chunk Notes

This is a source-tree-aligned chunk report only. It intentionally does not create a final per-file synthesis for `dpcs_4_2_0_sh_mask.h`; that merge belongs to the reconciliation lane after every chunk for this generated header is available.
