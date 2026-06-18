# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 46341-48787

## Scope

This chunk is a generated AMD DPCS 3.1.4 shift/mask header segment. It covers lines 46341-48787 of `dpcs_3_1_4_sh_mask.h`, defining bit positions and masks for DPCS CR2 raw always-on lane registers, generic lane mirrors, supervisor PLL/control registers, and the beginning of the generic lane ASIC/TX power-control register block.

The chunk is declarative only. It contains no C functions, types, storage, or executable control flow. The exported surface is preprocessor constants named as:

- `DPCSSYS_CR2_*__FIELD__SHIFT`
- `DPCSSYS_CR2_*__FIELD_MASK`

Within the exact line range, the slice contains 1,077 `__SHIFT` definitions and 1,076 `_MASK` definitions. The imbalance is from chunk boundaries: line 46341 is the trailing mask for `DPCSSYS_CR2_RAWAONLANE3_DIG_DFE_BYPASS_EVEN_VDAC_OFST`, whose shift is above this range, and line 48787 is only the next register comment for `DPCSSYS_CR2_LANEX_DIG_TX_PWRCTL_DCC_DAC_ACK`, whose shift/mask definitions continue after this chunk.

## Purpose

The header gives DCN 3.1.4 display driver code symbolic bitfield metadata for DPCS hardware registers. These constants are intended to be paired with register offset constants from `dpcs_3_1_4_offset.h` and consumed by AMD display register helper macros that perform read/modify/write, field extraction, and field composition without embedding raw bit positions in handwritten code.

This chunk focuses on DPCSSYS CR2:

- The tail of concrete `RAWAONLANE3` receive/adaptation/calibration fields.
- A complete generic `RAWAONLANEX` mirror of the same raw always-on lane register surface.
- The `SUPX` supervisor register surface for reference clocks, MPLLA/MPLLB override/ASIC-in status, spread-spectrum control, RTUNE, bandgap, and MPLL power control.
- The start of the `LANEX` generic lane register surface for ASIC override/status paths and TX power-control timing/DCC programming.

The repeated `LANE3` and `LANEX` naming is important: `LANE3` maps to a concrete lane address range, while `LANEX` maps to a generic lane/indirect access range. Their field semantics are largely parallel but their offsets differ in the companion offset header.

## Exported API Surface

There are no callable APIs or structs. The exported API is a set of macros usable anywhere this generated header is included. The header is included by DCN 3.1.4 resource code alongside `dpcs_3_1_4_offset.h`, for example in `drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`.

Important macro families in this chunk:

- `DPCSSYS_CR2_RAWAONLANE3_DIG_*`: concrete lane 3 fields for RX adaptation, DFE/DCC calibration, signal detect, fast calibration bypass flags, firmware configuration bits, lane mode selection, and TX DCC config.
- `DPCSSYS_CR2_RAWAONLANEX_DIG_*`: generic lane mirror fields for the same RX/DFE/adaptation/calibration/signal-detect surfaces, including additional early fields such as AFE offsets, RX IQ adaptation, RX adaptation figure-of-merit, DFE data/ref-level offsets, phase-adjust linear/map fields, and then the same later controls as lane 3.
- `DPCSSYS_CR2_SUPX_DIG_*` and `DPCSSYS_CR2_SUPX_ANA_*`: supervisor clock, PLL, bandgap, RTUNE, analog status, override output, ASIC input, and MPLL power-control fields.
- `DPCSSYS_CR2_LANEX_DIG_ASIC_*`: generic lane ASIC interface fields for TX/RX override inputs, ASIC input/status mirrors, CDR/VCO values, EQ controls, request/ack handshakes, and override output/status.
- `DPCSSYS_CR2_LANEX_DIG_TX_PWRCTL_*`: TX power-state bitfields, TX power-up timing fields, and the first TX DCC control-bank/DAC-selection fields.

All field values in this range are low-level numeric constants. Most masks are 16-bit-style values with an `L` suffix, matching the CR register width exposed by this block. Some fields are full 16-bit data payloads such as `ADDR`, `DATA`, or `VAL`.

## Register Areas Covered

### RAWAONLANE3 Lane Tail

The `RAWAONLANE3` portion begins mid-register at line 46341, with the reserved mask for `DPCSSYS_CR2_RAWAONLANE3_DIG_DFE_BYPASS_EVEN_VDAC_OFST`. It then covers the rest of the concrete lane 3 raw always-on digital block.

Key lane 3 register categories:

- DFE and phase/calibration remnants: bypass/error VDAC offsets, RX IQ phase adjust, MPLLA/MPLLB coarse tune, and initial power-up done.
- RX adaptation readouts: attenuation, VGA, CTLE boost/pole, DFE taps 1-5, slicer controls, and `ADPT_CTL_0` through `ADPT_CTL_7` full-width control words.
- Calibration/status bits: lane common MPLL/RCAL init and done bits, MPLL disable, RX adaptation done, stats, DCC code fields for ICM/IDF/QCM/QDF, IOFF/ICONST/VREFGEN calibration codes, and RX VREFGEN enable.
- Fast-mode flags: `FAST_FLAGS` exposes bypass/fast paths for startup, adaptation, AFE/DFE/bypass/reference/IQ calibration, TX common mode, TX RX detection, RX power-up, VCO wait, and VCO calibration. `FAST_FLAGS_2` extends this to continuous calibration/adaptation paths, DCC/VPHUD/VREF/sigdet shortcuts, and `SKIP_TX_RTUNE_CAL`.
- RX/TX override and signal-detect controls: TX/RX override input, RX loss-of-signal mask, signal-detect filter control, RX override outputs, signal-detect calibration and HF/LF codes, signal-detect output override/input, and RX signal-detect configuration.
- Firmware hooks: firmware MM, adaptation, and calibration config registers.
- Lane mode and DCC setup: lane transceiver mode override/input and TX DCC bank/address/data/config controls.

These fields model values that are typically set or observed during link bring-up, receiver adaptation, signal detection, calibration, and PHY debugging.

### RAWAONLANEX Generic Lane Mirror

The `RAWAONLANEX` block repeats the lane register map in generic form. It starts earlier than the visible `RAWAONLANE3` tail, so this chunk includes the full generic sequence from AFE offset/adaptation fields through TX DCC configuration.

Additional generic-lane fields visible here include:

- AFE/CTLE IDAC offsets.
- RX IQ adaptation values and RX adaptation figure-of-merit.
- DFE summer, phase, data, bypass, error, even/odd reference-level, and phase-adjust mapping fields.

After those early generic fields, `RAWAONLANEX` mirrors the same adaptation, calibration, fast flag, signal-detect, firmware, lane mode, and TX DCC families present for `RAWAONLANE3`. This symmetry is a useful generated-header consistency signal: if a driver can address a lane through a generic lane path, it can use the same field semantics without hard-coding lane 3-specific names.

### SUPX Supervisor And PLL Control

The `SUPX` portion exposes shared CR2 supervisor state rather than per-lane raw adaptation state.

Covered supervisor areas include:

- ID code placeholders: `DPCSSYS_CR2_SUPX_DIG_IDCODE_LO` and `_HI` appear as comments only in this slice, indicating register names with no field macros in the chunk.
- Reference clock override: enable, override-enable, pad selection, clock range, bandgap enable, HDMI mode enable, and pre-high-power override controls.
- MPLLA/MPLLB divider and HDMI clock overrides: divider clock enable, divider multipliers, pixel-clock divider, HDMI divider, and override enables.
- MPLLA/MPLLB analog override inputs: enable, div5, TX clock divider, V2I, standby, VCO frequency, calibration force, FRACN, clock sync, multiplier, calibration comparator settings, multiplier thresholds, integer/fractional fields, SSC peak/step settings, accumulator control, gear-shift fields, charge-pump controls, and VREG/VCM/PMIX related settings.
- Supervisor override/input/status: general supervisor override bits, prescaler override, supervisor override outputs, level override, MPLLA/MPLLB ASIC input mirrors, divider/HDMI ASIC input mirrors, bandgap ASIC input, charge-pump ASIC input, and analog status/override output.
- Analog controls: prescaler control, RTUNE control, bandgap registers, and switch power measurement.
- MPLL power-control sub-blocks for MPLLA and MPLLB: MPLL power override, status, DAC max range, lock/pixel-clock stable timers, calibration controls, analog DAC output, and SSC spread type.
- Clock/reset timing and RTUNE: bandgap/reference power-up timers, reference VPHUD timing, RTUNE config/status, RX/TXDN/TXUP set and status values, RTUNE counters, and TX calibration code.

This block is the shared PLL/reference/termination layer that per-lane link programming depends on. It contains many request/status pairs and override/override-enable pairs, so consumers need to treat field direction carefully.

### LANEX ASIC And TX Power-Control Start

The `LANEX` portion begins the generic lane digital block. It covers interface wiring between the ASIC/display controller and the PHY lane, plus the start of TX power management.

Covered `LANEX_DIG_ASIC_*` areas include:

- Lane override input fields for lane power state, RX/TX state, lane mode, and MPLL selection.
- TX override inputs for analog power, clocking, reset, serial/data enable, boost, common-mode, voltage mode, main/pre/post cursor levels, TX muxing, DCC compensation, clock loopback, AC JTAG, and additional TX fast-start style controls.
- RX override inputs for signal-detect calibration, squelch controls, PWM controls, reference generator, clock/data enable, reset, equalization/VCO controls, DCC, VPHUD, VREF, adaptation, and DFE/slicer settings.
- ASIC input mirrors for lane, TX, RX, RX EQ, RX CDR/VCO, and ASIC output/status fields.
- Override outputs for TX/RX controls, repeater enable, digital clock state, shift/ack handshakes, and OCLA clock/data enables.

The TX power-control sub-block covers:

- P-state definitions for `P0`, `P0S`, `P1`, and `P2`, including TX analog reference generator, VCM hold, analog clock/word clock, reset, serial enable, digital clock, data enable, RX detection allowance, VBOOST allowance for P2, and DCC compensation calibration enable.
- Power-up timing registers for reference generator enable time, clock enable time, VCM hold time, VBOOST disable time, ground-sense VCM hold pulse timing, RX-detect time, reset time, serial-enable time, and fast/skip controls.
- DCC control-bank and DAC programming registers: CR bank address/data, DAC control, DAC range, and DAC selection request/update bits. The next `DCC_DAC_ACK` register is only introduced by comment at the final line of this chunk; its actual fields are in the following chunk.

## Control Flow And State Behavior

This file has no software control flow. Runtime sequencing is imposed by the hardware state machines that consume these fields and by driver code that writes or polls them through register helpers.

The fields imply several important state-machine surfaces:

- RX adaptation and calibration: adapted ATT/VGA/CTLE/DFE values, adaptation done, DCC code readouts, calibration config fields, continuous calibration fast flags, slicer controls, and VREFGEN fields expose the state of receiver tuning.
- Power-up and power-state transitions: initial power-up done, TX P-state bitfields, TX power-up timers, reference generator timing, VCM hold timing, VBOOST timing, reset/serial/data enables, and clock-enable fields must be programmed in hardware-defined order.
- PLL and clock control: MPLLA/MPLLB override inputs, divider/HDMI clock overrides, SSC configuration, MPLL power-control timers, calibration controls, lock/status fields, and supervisor reference-clock controls define shared clock state used by lanes.
- Request/ack and override handshakes: many fields pair a requested value with an override-enable bit or a status/ack bit. Examples include supervisor override paths, ASIC TX/RX overrides, signal-detect output override/input, RTUNE status, shift output/ack, DAC selection request, and lane common calibration init/done status.
- Signal detection and link presence: loss-of-signal masks, signal-detect filter, signal-detect calibration/HF/LF codes, squelch/PWM controls, and RX signal-detect configuration feed hotplug/link-detect behavior and low-power entry/exit decisions.
- TX DCC programming: bank address/data and DAC selection/update fields form an indirect programming path into DCC calibration state. The sliced boundary before `DCC_DAC_ACK` means the request side is visible here but the acknowledgement macro definitions are outside this work item.

No state is persisted by this header. Persistence belongs to hardware registers and their power/reset domains. Full-width `VAL`, `ADDR`, `DATA`, timer, scratch-like, and calibration code masks merely expose writable/readable register storage; this chunk does not define software ownership or retention policy for those values.

## Dependencies And Integration Points

The header depends only on the C preprocessor, but it is meaningful only in combination with generated register address definitions and AMD display register access helpers.

Key dependencies and integration points:

- `dpcs_3_1_4_offset.h`: provides `ixDPCSSYS_CR2_*` offsets for the register names whose fields are defined here. For example, `RAWAONLANE3` registers in this area map around offsets `0x430f` through `0x4351`, generic `RAWAONLANEX` starts at `0x7000`, and `LANEX_DIG_TX_PWRCTL_DCC_DAC_SEL` maps to `0x902e`.
- DCN 3.1.4 resource code includes both `dpcs_3_1_4_offset.h` and this shift/mask header, making these constants available to display resource construction and lower-level register programming.
- AMD display register helper code such as `reg_helper.h` expects separate register, field, mask, and shift definitions. These macros fit that convention.
- Hardware/firmware coordination paths: names such as `FW_MM_CONFIG`, `FW_ADPT_CONFIG`, `FW_CALIB_CONFIG`, supervisor override outputs, ASIC input mirrors, and generic lane override paths show integration with firmware-managed or hardware-managed PHY state.
- Display PHY link-management paths: receiver adaptation, signal detect, DFE/DCC calibration, MPLL programming, RTUNE, TX P-state sequencing, and DCC DAC programming all affect DisplayPort/HDMI/PHY bring-up and recovery.

There are no local includes or compile-time conditionals in this slice; include guards and licensing are outside the chunk.

## Risks

- Generated-header drift is the primary risk. Any wrong shift or mask can corrupt adjacent hardware fields in read-modify-write operations. This is especially risky in dense 16-bit CR registers where many one-bit enable/status fields are packed together.
- The `RAWAONLANE3` and `RAWAONLANEX` blocks are highly parallel. A copy/generation mismatch between concrete lane and generic lane fields would be hard to detect at compile time but could cause lane-specific and generic access paths to behave differently.
- Many fields expose override values next to override-enable bits. Driver code that writes a value without coordinating the corresponding `_OVRD_EN` field may appear to update a value while hardware continues using the non-overridden path, or may unexpectedly seize control from firmware/hardware state machines.
- Request/status ordering matters. Fields such as calibration init/done, RTUNE status, DAC selection request/update, shift/ack, clock enable/status, and MPLL power-control status should not be treated as plain configuration bits.
- Fast/skip flags can bypass calibrations or timing waits. Incorrect values in `FAST_FLAGS`, `FAST_FLAGS_2`, `SKIP_TX_RTUNE_CAL`, `FAST_TX_RXDET`, or timer skip bits can produce marginal links, unstable training, or failures that only appear on specific boards, cables, link rates, or power states.
- Reserved fields are explicitly named and masked in many registers. Code should preserve reserved bits unless the hardware programming guide says otherwise; writing raw full-register values with these masks risks toggling undocumented controls.
- The line-range boundaries split complete register definitions. The opening line is only a trailing mask for a previous field, and the final `DCC_DAC_ACK` register is only a comment in this chunk. Any automated per-chunk validation must account for boundary carry-over rather than assuming every comment in the chunk has a complete field set.
- Cross-generation comparison shows similarly named DPCS versions may differ in width or added fields. Consumers must not mix masks from `dpcs_3_1_4_sh_mask.h` with offsets or field expectations from later `dpcs_4_*` or `dcn_4_*` generated headers.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, generation-time, and hardware-integration oriented:

- AMDGPU/DCN 3.1.4 build coverage that preprocesses `dcn314_resource.c` and any downstream files including `dpcs_3_1_4_sh_mask.h`.
- Generated-register consistency checks comparing this header against the authoritative DPCS 3.1.4 register database, especially for paired `RAWAONLANE3` and `RAWAONLANEX` fields.
- Static checks that field masks align with shifts and expected widths, while allowing this chunk's two boundary exceptions.
- Cross-header checks that every register field in this shift/mask chunk has a corresponding register offset in `dpcs_3_1_4_offset.h`.
- Runtime link bring-up tests on DCN 3.1.4 ASICs: DisplayPort and HDMI hotplug, link training across rates, suspend/resume, display mode changes, low-power transitions, and error recovery.
- PHY diagnostics/readback during bring-up: RX adaptation done/readouts, DFE tap values, signal-detect status, MPLL lock/power-control status, RTUNE status, TX P-state transitions, TX DCC DAC request/ack, and calibration code readbacks.
- Stress tests for paths implied by fast/skip controls: repeated hotplug, short/long cable combinations, cold boot, warm resume, high link rates, and continuous calibration/adaptation behavior.

## Chunk Notes For Merge

This chunk should merge into the per-file report as one middle section of a much larger generated register-map header. It is not handwritten driver logic. The merged document should describe this file as an ASIC-specific bitfield map and should preserve the distinction between concrete CR2 lane 3 fields, generic `LANEX`/`RAWAONLANEX` fields, and shared `SUPX` supervisor fields. The following chunk is needed to complete `DPCSSYS_CR2_LANEX_DIG_TX_PWRCTL_DCC_DAC_ACK` and subsequent `LANEX` TX clock/lane controls.
