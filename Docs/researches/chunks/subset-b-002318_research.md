# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 71474-73858

## Scope

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice. It contains preprocessor constants only: no callable functions, structs, enums, storage objects, allocation, or executable control flow. The exported contract is the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` namespace, where each macro describes one field position or already-shifted mask for a 16-bit DPCS/PHY control register.

The requested range covers 2,385 source lines and 2,113 `#define` entries: 1,055 shift macros, 1,078 mask macros, and many reserved-bit definitions. It begins inside the tail of the `DPCSSYS_CR3_LANE3_DIG_ANA_TX_EQ_OVRD_OUT_2`/TX equalization override family, completes the lane 3 analog TX status, DCC, override, test, termination, and miscellaneous groups, then covers `DPCSSYS_CR3_RAWCMN` common PHY controls. It then covers essentially all visible `DPCSSYS_CR3_RAWLANE0` PCS/FSM/IRQ/PMA/TX/RX/control fields and starts the matching `DPCSSYS_CR3_RAWLANE1` PCS/FSM/IRQ fields through `RX_ADAPT_DIS_IRQ`, ending at the comment for `RX_RESET_IRQ_CLR`.

Although the repository path is under `sources/distributed-fs/ceph-client`, this header is AMD display/link PHY register metadata. It has no Ceph, distributed filesystem, network-storage, or persistent-disk behavior.

## Purpose

The purpose of this header range is to provide ASIC-specific bit geometry for DCN 3.1 DPCS 4.2.0 CR3 lane, common, raw-lane, FSM, IRQ, and PMA registers. Runtime display code includes this header with the matching `dpcs_4_2_0_offset.h` file so generated register tables can map logical link-encoder fields onto exact DPCS hardware layout.

The covered hardware areas are:

- Lane 3 analog TX tail: TX equalization override outputs for pre/post cursor values and leg-pull direction, analog status readback, TX DCC DAC override output, extra fast-start/loopback/ACJTAG override bits, analog TX measurement, power override, alternate bus, ATB measurement selection, DCC DAC/control, TX termination code and clock controls, override clock, miscellaneous clock/loopback/power-save bits, and reserved analog TX registers.
- CR3 raw-common controls: common PHY functional reset; `MPLLA`/`MPLLB` word-divide, TX-clock-divider, div8/div10, bandwidth, spread-spectrum, and fractional-N overrides; lane-FSM extension; common control for PLL init-cal disable, rtune, HDMI mode, and TX PWM clock; MPLL state timing and bank selection; TX calibration code; SRAM init status; OCLA/debug; supervisor analog overrides; PCS/FW ID-code readbacks; AON retune values for RX/TXDN/TXUP entries 0-7; SRAM block configuration; power-gate, supervisor, resistance, VREF, reference-range, and power-down timing controls.
- CR3 raw-lane0 PCS transfer and test controls: TX/RX PCS override inputs, PCS input mirrors, override outputs, ACK/readback outputs, RX adaptation ACK/FOM and TX pre/main/post direction hints, lane number, reserved scratch registers, ATE RX/TX override inputs, RX EQ delta-IQ controls, TX/RX termination controls, RX EQ override inputs, RX phase-2 calibration, and master MPLL loop controls.
- CR3 raw-lane0 FSM and IRQ controls: FSM override, memory-address/status monitors, fast-path timing flags for RX startup/adaptation/calibration/power/VCO/SUP and TX common-mode/RX-detect paths, continuous calibration/adaptation flags, CR register/memory locks, TX DCC flags/status, OCLA controls, TX EQ update flag, common calibration status, RX IQ phase offset, and IRQ status/clear/mask bits for RX reset/request/rate/pstate/adaptation, lane mode, PH2 calibration, RX-to-TX loopback, DCC on-demand, and TX reset/request.
- CR3 raw-lane0 PMA, TX, and RX control surfaces: PMA lane/supervisor/TX/RX transfer overrides and readbacks, lane rtune request/ack, MPHY override inputs/outputs, RX adaptation output, TX FSM and clock controls, TX DCC continuous status, TX/RX OCLA controls, RX LOS mask, RX data-enable override, off-canonical/adaptation continuous status, and repeated ATE PCS controls.
- CR3 raw-lane1 opening: a second raw-lane PCS/FSM/IRQ pattern mirroring raw-lane0 for TX/RX PCS transfer, RX adaptation, TX equalization direction hints, lane number, ATE and RX EQ controls, RX PH2 calibration, FSM fast flags/status, DCC status, OCLA, TX EQ update, RCAL/MPLL status, RX IQ phase offset, and the first RX IRQ status bits.

## Important APIs, Types, And Macros

There are no C APIs or concrete types in this chunk. The important interface is the generated macro naming pattern:

- `*_SHIFT` gives a field's least-significant bit position.
- `*_MASK` gives the field mask in final register position.
- Register names encode DPCS CR instance, lane/raw-lane, block, and register, such as `DPCSSYS_CR3_LANE3_ANA_TX_DCC_CTRL1`, `DPCSSYS_CR3_RAWCMN_DIG_MPLLA_OVRD_IN`, `DPCSSYS_CR3_RAWLANE0_DIG_PCS_XF_RX_OVRD_IN`, and `DPCSSYS_CR3_RAWLANE1_DIG_FSM_FAST_FLAGS`.

The lane 3 analog TX fields define low-level transmitter override and readback controls. Important families include `TX_ANA_CTRL_PRE`, `TX_ANA_CTRL_POST`, `TX_ANA_CTRL_EQ_MUX_SEL`, `TX_ANA_CTRL_LEG_PULL_DIR_*`, `TX_ANA_DCC_CAL_*`, `TX_ANA_FAST_START`, `TX_CLK_LB_EN`, measurement/ATB selectors, power override enables, TX DCC DAC controls, termination code fields, loopback, self-clear clock controls, and TX power-save/miscellaneous bits.

The raw-common `MPLLA`/`MPLLB` fields expose parallel PLL control paths. Each PLL has word-divide, TX clock divisor, div8/div10 enable, bandwidth override, SSC range/clock/enables, and fractional-N control. Common support fields include functional reset, PLL init-cal-disable overrides, rtune request, HDMI-mode and TX PWM controls, MPLL state/off/force-on timing, bank selection, supervisor analog overrides, SRAM init/readback, OCLA probe controls, ID-code readbacks, retune values, power-gate/isolation controls, supervisor force/ref-clock controls, VREF status, resistance request/ack controls, and reference-range override.

The raw-lane PCS transfer fields form the digital boundary between PCS, PMA, lane supervisor, and link logic. TX-side fields include `PSTATE`, `LPD`, `WIDTH`, `RATE`, `MPLLB_SEL`, `MPLL_EN`, master MPLL state, reset/request/detect-RX, VBOOST/IBOOST, beacon, data enable, async enable/data, serial loopback, ACK, detect-RX result, and TX dword-clock sync override. RX-side fields include `RATE`, `WIDTH`, `PSTATE`, low-power detect, reset/request, CDR VCO/ref load values, adaptation AFE/DFE enable, adaptation request/continuous/off-canonical controls, RX data enable, RX valid, RX LOS thresholds, EQ attenuation/VGA/CTLE/DFE readbacks, adaptation ACK/FOM, and TX pre/main/post direction outputs.

The raw-lane FSM fields provide firmware or microcontroller state-machine observability and fast-path controls. They include FSM override enables, program counter, RAM readiness, memory address/status monitors, one-bit fast timing or skip flags for startup and continuous RX calibration/adaptation steps, TX DCC flags/status, common MPLL/RCAL init/done status, CR register/memory locks, OCLA bank enable bits, TX EQ update flag, and RX IQ phase offset.

The IRQ control fields define lane event plumbing. This chunk includes status, clear, and mask families for reset, request, rate, pstate, adaptation request/disable, lane transceiver mode, RX PH2 calibration request/disable, RX-to-TX serial loopback enable, DCC on-demand, TX reset, and TX request. For raw-lane1 the chunk reaches only the first RX IRQ status bits; the clear and mask families continue after the requested range.

The PMA and control fields at the end of raw-lane0 expose PMA transfer boundaries and lane-local control. They include lane MPLL enables, supervisor state, TX/RX request/reset override paths, data enable, loopback, ACK/readback inputs, rtune control, MPHY PWM/term/async/clock-selection controls, RX adaptation output, TX FSM/clock/DCC continuous status, RX LOS masking, RX data enable override, off-canonical/adaptation continuous status, and OCLA debug enables.

## Control Flow

This header range has no local control flow. Runtime behavior is created by consumers that include `dpcs_4_2_0_offset.h` and `dpcs_4_2_0_sh_mask.h`, construct register/field tables, and then use AMD display register helpers to perform MMIO or CR-indirect reads and writes.

A typical DCN 3.1 path is:

1. `display/dc/resource/dcn31/dcn31_resource.c` includes `dpcs/dpcs_4_2_0_offset.h` and `dpcs/dpcs_4_2_0_sh_mask.h`.
2. Resource construction initializes `le_shift` and `le_mask` with `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)`.
3. Link encoder and HPO DP link encoder code use those tables through register helper operations such as `REG_GET`, `REG_SET`, and `REG_UPDATE` variants.
4. Higher-level display code sequences PHY reset, PLL setup, TX/RX lane enable, DisplayPort/HDMI mode transitions, lane training, equalization, power-state transitions, IRQ handling, debug capture, hotplug recovery, suspend/resume, and GPU reset recovery.

The header itself does not encode ordering, delays, polling loops, field writability, lane ownership, or policy. Those rules live in display resource, link encoder, HPO DP, GPIO, IRQ, clock manager, hardware sequencer, and firmware-facing code that consumes the generated tables.

## State And Persistence Behavior

The file itself stores no runtime state and persists nothing. It describes hardware register state whose lifetime is controlled by DPCS/PHY programming, link training, modesets, hotplug handling, DP/HDMI mode changes, runtime power management, suspend/resume, and GPU reset.

State represented by this chunk includes:

- Lane 3 analog TX state for equalization, leg-pull direction, termination, DCC DAC/control, clock/loopback/fast-start, ATB/measurement selection, power override, and analog TX status.
- Common PHY state for reset, PLL dividers, bandwidth/SSC/fractional-N controls, init calibration disable, rtune, HDMI/PWM mode, MPLL state timing, SRAM init, supervisor analog overrides, retune values, power-gate/isolation, VREF, resistance handshakes, and reference range.
- Raw-lane PCS state for TX/RX reset/request/ack handshakes, rate/width/pstate/LPD, MPLL selection, data/async enable, VBOOST/IBOOST, detect-RX, loopback, RX valid, RX adaptation request/ack/FOM, equalization readbacks, and direction hints used during training.
- Raw-lane FSM and IRQ state for fast/skip flags, continuous calibration/adaptation state, DCC and common calibration status, CR locks, debug bank enables, IRQ status/clear/mask values, TX EQ update state, and RX IQ phase offset.
- Raw-lane PMA/control state for PMA supervisor/TX/RX transfer overrides, rtune, MPHY PWM/term/async controls, TX/RX clock and FSM state, LOS masking, data-enable override, and OCLA/debug capture.

Many fields are status-like readbacks, including ACK bits, calibration done/status bits, FOM values, EQ readbacks, SRAM init done, ID codes, retune values, VREF stats, IRQ status bits, FSM status monitors, CR lock bits, and PMA/PCS mirrors. Other fields are writable controls that can immediately change live PHY behavior or arm clear/pulse-style paths. Fields named `*_REQ`, `*_ACK`, `*_CLR`, `*_OVRD_EN`, `*_UPDATE_FLAG`, `*_SELF_CLEAR_DISABLE`, `*_CLK`, or `*_START` are especially sequencing-sensitive.

Bad values can persist until the lane, common PHY, DPCS block, display link, or whole GPU is reset or reprogrammed. Some state is reconstructed during modeset, hotplug recovery, link training, suspend/resume, and runtime PM, but this generated header has no restore logic; it only defines the bit layout those paths rely on.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h`, which provides matching generated register offsets. These masks are only correct when paired with the DPCS 4.2.0 offset header and DCN 3.1 resource layout.

Visible integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, which directly includes both DPCS 4.2.0 generated headers and builds `le_shift`/`le_mask` tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h`, which defines `DPCS_DCN31_MASK_SH_LIST` and the logical DPCS field set token-pasted against `__SHIFT` and `_MASK`.
- DCN link encoder and HPO DP link encoder code that consumes generated shift/mask tables through AMD display register helpers for DPCS PHY and link-encoder control.
- GPIO, IRQ, clock-manager, and resource code for nearby AMD display generations, which follow the same generated offset/shift-mask pairing pattern.

The generated namespace is cross-generation in shape but not interchangeable. Nearby DPCS headers such as `dpcs_4_2_2_sh_mask.h`, `dpcs_4_2_3_sh_mask.h`, and older `dpcs_3_*_sh_mask.h` contain similar register families, but field availability, field widths, and exact masks may differ. Consumers must bind the correct offset and mask pair for the target ASIC.

## Risks And Edge Cases

The main risk is silent PHY misprogramming. Shift and mask constants compile cleanly even when wrong, but a bad value can update a neighboring field, truncate a multi-bit control, miss a clear/pulse bit, decode a status bit incorrectly, or force the wrong lane/PLL state.

Chunk-boundary risk is present. The first in-scope lines are already inside the lane 3 TX equalization override family; the preceding chunk owns earlier `TX_EQ_OVRD_OUT_2` context and the first lane 3 TX-EQ fields. The final line is only the comment for `DPCSSYS_CR3_RAWLANE1_DIG_IRQ_CTL_RX_RESET_IRQ_CLR`; its shift/mask definitions and the rest of raw-lane1 IRQ/PMA/control fields continue in the next chunk. The final per-file report should merge adjacent chunks before making complete claims about those boundary registers.

Lane and instance pairing are critical. This range mixes `CR3_LANE3`, `CR3_RAWCMN`, `CR3_RAWLANE0`, and `CR3_RAWLANE1` names. A valid macro copied to the wrong lane instance or paired with a mismatched offset can produce failures that look like link-training, clocking, or signal-integrity bugs.

PLL and common-clock fields are high risk. `MPLLA`/`MPLLB` dividers, bandwidth controls, spread-spectrum fields, fractional-N values, PLL state timing, HDMI mode, TX PWM clock controls, and reference-range overrides affect symbol clocks and link stability. Wrong masks can cause no-link, intermittent training failure, jitter, or mode-specific display loss.

Analog and equalization fields are calibration-sensitive. TX pre/post, leg-pull direction, termination, DCC DAC/control, VBOOST/IBOOST, RX LOS thresholds, RX EQ readbacks, CDR VCO/ref load values, adaptation controls, and signal-detect behavior can produce subtle failures at high link rates, with specific cables, docks, boards, alt-mode paths, or lane mappings.

Handshake and power-state fields are sequencing-sensitive. TX/RX request/reset/ack, pstate/rate/width, data-enable, async enable/data, detect-RX, adaptation request/ack, PMA ACK, rtune, loopback, and supervisor state must be changed in hardware-defined order. The masks do not express waits, ownership, read-only/write-one-to-clear behavior, self-clearing semantics, or required restore order.

IRQ and debug fields can mislead diagnostics. Incorrect status, clear, or mask constants may hide lane events, clear the wrong interrupt, leave an interrupt stuck, or make OCLA/FSM/DCC/debug readbacks appear plausible but wrong.

Reserved fields appear frequently. Generic full-register writes must preserve reserved bits unless the hardware database explicitly requires otherwise. Many registers are 16-bit views with dense reserved regions, so read-modify-write discipline matters.

## Test Signals

Useful validation is mostly generated-header, build, and hardware-behavior oriented:

- Compile DCN 3.1 AMDGPU Display Core resource, link encoder, HPO DP, GPIO, IRQ, and clock/resource code with DPCS 4.2.0 headers enabled, ensuring all generated symbols used by `DPCS_DCN31_MASK_SH_LIST` resolve.
- Run generated-register consistency checks: every logical field has a matching offset/header pair, each `*_MASK` matches the intended `*_SHIFT` and width, and no field list references a missing or wrong-generation macro.
- Diff against AMD's authoritative DPCS 4.2.0 register database and nearby DPCS 4.2.2/4.2.3 headers, with expected generation differences reviewed instead of normalized away.
- Exercise DP/HDMI link bring-up across lane counts, link rates, MST/HPO paths, USB-C/DP alt-mode, dock paths, hotplug/unplug, suspend/resume, runtime PM, and GPU reset.
- Validate PLL and common-clock paths for MPLLA/MPLLB selection, dividers, SSC/fractional-N, bandwidth override, HDMI/PWM modes, reference-range, SRAM init, power-gating, and supervisor force/ack behavior.
- Test TX/RX lane handshakes for reset/request/ack, pstate/rate/width transitions, data/async enable, detect-RX, VBOOST/IBOOST, loopback, RX valid, adaptation request/ack/FOM, PMA ACK, and rtune.
- Run signal-integrity and link-training tests that stress TX EQ pre/post, termination, DCC DAC, RX LOS thresholds, RX EQ/CTLE/DFE values, VCO/ref load controls, continuous adaptation, and IQ phase offset at high rates.
- Trigger IRQ/debug events for reset/request/rate/pstate/adaptation, PH2 calibration, loopback, DCC on-demand, and TX reset/request; verify status, mask, and clear behavior plus FSM/OCLA readbacks.
- Validate recovery from interrupted or failed link-training sequences through hotplug recovery, modeset, suspend/resume, runtime power cycling, and GPU reset.

Regression symptoms from bad constants include blank display output, intermittent DP training failures, reduced maximum link rate, HDMI mode failures, USB-C/DP alt-mode instability, dock-specific failures, flicker at high rates, stuck reset/request/ack bits, missing or storming interrupts, failed suspend/resume recovery, incorrect PHY debug counters, and failures isolated to DCN 3.1 ASICs using DPCS 4.2.0.

## Cross-Chunk Notes

This is not a standalone source module. It is a generated register-layout slice inside `dpcs_4_2_0_sh_mask.h`. The previous chunk is required for the beginning of lane 3 analog TX equalization override context before line 71474. The next chunk is required for the raw-lane1 IRQ clear/mask continuation and later raw-lane1 PMA/TX/RX/control definitions after line 73858. The merge/reconciliation lane should treat this document as the CR3 lane 3 analog TX tail, raw-common, raw-lane0 PCS/FSM/IRQ/PMA/control, and raw-lane1 opening portion of the full DPCS 4.2.0 shift/mask contract.
