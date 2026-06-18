# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 12099-14529

## Purpose

This chunk is generated AMDGPU Display Core register metadata for the DPCS 4.2.3 block. It defines preprocessor constants for bit shifts and masks in the `DPCSSYS_CR0` control-register namespace. The file contains no executable code; its job is to let AMD display register helpers compose field-safe reads and writes when paired with the matching `dpcs_4_2_3_offset.h` address definitions.

The requested range starts in the middle of `DPCSSYS_CR0_LANE3_DIG_RX_STAT_STAT_CTL1` and ends in the middle of `DPCSSYS_CR0_RAWLANE1_DIG_FSM_RX_IQ_PHASE_OFFSET`. Within those boundaries it covers 2,146 macro definitions across 286 register names. Functionally, this slice describes late lane3 RX statistic fields, lane3 digital and analog TX override/status fields, raw-common MPLL/AON controls, the complete raw-lane0 PCS/FSM/IRQ/PMA/TX/RX control region, and the beginning of raw-lane1 PCS/FSM definitions.

Although the repository path is under `sources/distributed-fs/ceph-client`, this header is GPU display PHY metadata from the Linux AMDGPU driver tree, not Ceph filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, classes, variables, locks, or allocation APIs in this range. The public interface is the generated macro naming contract:

- `DPCSSYS_CR0_<register>__<field>__SHIFT` gives the least-significant bit index of a field.
- `DPCSSYS_CR0_<register>__<field>_MASK` gives the already-shifted field mask.
- `RESERVED_*` macros describe generated reserved bit ranges and should normally be preserved by read-modify-write operations.

Most masks in this chunk are 16-bit CR-register masks such as `0x0001L`, `0x7FFFL`, or `0xFFFEL`. Driver code commonly stores register values in wider integer types, but these field layouts target the DPCS CR register window. The shift/mask macros are meaningful only with the matching `ixDPCSSYS_CR0_*` offsets from `dpcs_4_2_3_offset.h`; for example the companion offset header maps this chunk's fields around lane3 RX statistics at `0x1385`-`0x1394`, lane3 TX analog controls at `0x13a0`-`0x13ef`, raw-common registers at `0x2000`-`0x2040`, raw-lane0 at `0x3000`-`0x30c8`, and raw-lane1 starting at `0x3100`.

Major register groups covered:

- Lane3 RX statistics: `DIG_RX_STAT_*` sample counters, seven statistic counters, pattern/mask compare controls, statistic control/stop bits, valid-loss control, statistic clock enable, and calibration compare clock setup.
- Lane3 digital-to-analog TX overrides: `DIG_ANA_TX_OVRD_OUT`, termination-code overrides, TX EQ override words, DCC DAC override words, fast-start/clock-loopback/JTAG override bits, and `DIG_ANA_STATUS_0` readback bits.
- Lane3 direct analog TX registers: measurement and test-bus controls, TX power override, alternative bus/JTAG selection, ATB muxing, DCC DAC/control, termination-code update/reset, MPLLA/MPLLB and word-clock override bits, and TX miscellaneous VREG/slew/pre/post controls.
- Raw-common controls: PHY function reset, MPLLA/MPLLB divider/bandwidth/SSC/fractional-N overrides, common lane-FSM extension bit, MPLL state control, SRAM init, OCLA, supervisor analog overrides, raw PCS/firmware ID codes, AON RTUNE values for RX/TXDN/TXUP indexes 0-7, power-gate override in/out, supervisor force/ack overrides, VREF stats, reset request/ack overrides, reference-range override, and MPLL power-down timing.
- Raw-lane0 PCS crossface: TX and RX override input/output fields, PCS input/output status, RX adaptation figure of merit and ack, directed TX pre/main/post values, lane number, ATE overrides, RX equalizer override fields, TX/RX termination controls, phase-2 calibration handshakes, and master MPLL loop controls.
- Raw-lane0 FSM and IRQ controls: FSM override/jump/command/break fields, memory address and state monitors, fast calibration/adaptation flags, common calibration status, register/memory lock bits, TX DCC flags/status, OCLA enables, TX EQ update flag, RX IQ phase offset, RX/TX request/reset/rate/pstate/adaptation IRQ status and clear registers, and IRQ mask fields.
- Raw-lane0 PMA/TX/RX control: PMA lane and supervisor overrides, TX/RX PMA override outputs, RTUNE request/ack, MPHY PWM/async/termination override fields, RX adaptation PMA phase adjustment, TX FSM/clock/DCC continuous status, TX/UPCS OCLA bits, RX FSM/LOS mask/data-enable counters, and RX adaptation/offcan continuous status.
- Raw-lane1 beginning: mirrors raw-lane0 PCS crossface and much of the FSM region through `DPCSSYS_CR0_RAWLANE1_DIG_FSM_RX_IQ_PHASE_OFFSET`; the following IRQ fields begin after this chunk.

## Control Flow

The header has no runtime control flow. Runtime sequencing is indirect:

1. DCN 3.1.6 resource code includes `dpcs/dpcs_4_2_3_offset.h` and this `dpcs/dpcs_4_2_3_sh_mask.h`.
2. AMD display register tables and helper macros token-paste register and field names into offset, shift, and mask constants.
3. Link encoder, PHY, clock, power, training, hotplug, and diagnostic code use those constants through `REG_SET`, `REG_UPDATE`, `REG_GET`, `FD`, `SR`, `SRI`, or related AMD display register helpers.
4. The hardware and PHY firmware perform the real state transitions: PLL selection and calibration, lane TX/RX power sequencing, signal-detect and adaptation handshakes, DCC/RTUNE/VREF calibration, IRQ latching/clearing, and debug/OCLA capture.

This chunk does not encode required ordering. Consumers still need hardware-specific sequences such as enabling reference resources before MPLL use, preserving firmware-owned fields unless explicitly taking override ownership, polling calibration/status bits before enabling high-speed data paths, and clearing IRQs with the intended write semantics.

## State And Persistence Behavior

The macros are compile-time constants and store no software state. They describe hardware state in DPCS CR-backed registers.

State represented by these fields includes:

- RX statistic state: sample counters, counter-done flags, match patterns/masks, valid-loss control, statistic pause/stop, and sample clock gating.
- TX analog and lane state: serializer/data/refgen/clock enable bits, reset/serial/rate/div4/rx-detect controls, TX EQ leg-pull/pre/post controls, termination code and driver-source override fields, DCC compensation controls, fast-start, loopback clocking, AC JTAG, ATB/test measurement muxes, VREG/slew/pre/post settings, and direct analog status readbacks.
- Shared common PHY state: function reset, MPLLA/MPLLB divider and SSC override values/enables, MPLL state and bank selection, SRAM initialization, OCLA probe selection, supervisor analog overrides, firmware ID/raw PCS ID, AON RTUNE arrays, power-gate and reset request/ack signals, and VREF calibration status.
- Raw-lane PCS/FSM/PMA state: TX/RX requests, resets, pstate/LPD/width/rate, MPLL selection/enables, adaptation request/continuous/offcan controls, VCO/ref lock values, EQ ATT/VGA/CTLE/DFE settings, ATE overrides, FSM state/cmd/status, IRQ latches and clear bits, PMA handshakes, TX/RX data-enable overrides, clocking, RTUNE, LOS mask counters, and continuous adaptation status.

Persistence is hardware-defined. Configuration and override registers can retain programmed values until the display driver reprograms the link, the PHY is power-gated, suspend/resume reinitializes hardware, firmware retakes ownership, or a display-core/ASIC reset occurs. Status, counter, done, ack, interrupt, and clear fields may be read-only, sticky, self-clearing, write-one-to-clear, or side-effect-sensitive. The shift/mask header intentionally does not record those access semantics.

## Dependencies And Integration Points

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h` supplies the matching `ixDPCSSYS_CR0_*` register offsets. The mask header must stay in sync with that offset header and the same generated hardware register database.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` directly includes both `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`, selecting this DPCS generation for the DCN 3.1.6 display resource stack.
- AMD Display Core register helper infrastructure consumes these macros through field descriptors rather than through normal typed APIs. A missing or renamed generated macro can fail compilation; a wrong mask or shift can compile but program the wrong hardware bit.
- Functional integration points include DisplayPort and HDMI link bring-up, link training, DPCS/PHY power management, lane rate/width/pstate transitions, RX adaptation, signal detection, IRQ service paths, suspend/resume restore, manufacturing test modes, and debug features such as OCLA, ATE, ATB, LBERT-style controls, RTUNE, and DCC calibration.
- The chunk is adjacent to generated siblings for nearby DPCS revisions (`dpcs_4_2_0`, `dpcs_4_2_2`, `dpcs_3_1_4`) and DCN aggregate headers. Similar field names are useful for drift checks, but generation-specific headers must not be mixed unless the ASIC register source explicitly says the layout is shared.

## Risks And Edge Cases

- Bitfield drift is the main risk. These are untyped preprocessor constants, so an incorrect `__SHIFT` or `_MASK` can silently write the wrong lane, IRQ, PLL, adaptation, or analog-control bit.
- The range starts and ends mid-family. `STAT_CTL1` begins before the requested first line, and `RAWLANE1_DIG_FSM_RX_IQ_PHASE_OFFSET` continues at the first line after the requested end. Neighboring chunks are required for complete file-level conclusions.
- Reserved masks are exposed but should not be treated as writable feature bits. Unsafe full-register writes can disturb reserved fields in analog, PLL, or power-gating controls.
- Override value/enable pairs are common throughout this chunk. Setting an override value without the corresponding enable has no intended effect; leaving enable bits asserted after diagnostics can fight firmware or autonomous PHY state machines.
- Lane and instance naming is repetitive. This slice mixes lane3 direct registers, raw-common registers, all raw-lane0 groups, and the start of raw-lane1. Copying field names between `LANE3`, `RAWLANE0`, and `RAWLANE1` can target a different physical or logical path while still compiling.
- PLL, power, and calibration fields are sequencing-sensitive. Bad masks in `MPLLA/MPLLB`, RTUNE, VREF, DCC, VCO/ref lock, pstate, or reset/ack fields can show up as blank displays, intermittent training failures, unstable high link rates, suspend/resume failures, or power states that never settle.
- Interrupt status, clear, and mask registers are easy to misuse because their access semantics are not represented here. Wrong clear masks can lose interrupts; wrong mask bits can suppress real RX/TX request, reset, pstate, adaptation, loopback, or DCC events.

## Test Signals

Useful validation is mostly integration and hardware-facing:

- Build AMDGPU Display Core for the DCN 3.1.6 configuration that includes `dcn316_resource.c`; macro spelling, include selection, and token-pasted field descriptors should compile cleanly.
- Run generated-header consistency checks: every non-reserved field should have paired shift and mask macros, active masks should remain in the expected 16-bit CR field width, and repeated raw-lane0/raw-lane1 field families should stay structurally symmetric where the hardware database expects symmetry.
- Diff this DPCS 4.2.3 slice against the authoritative AMD register source and compatible sibling generated headers. Identical names across versions are a sanity signal, but changed field positions need hardware-source confirmation.
- Exercise display hardware across DP and HDMI modes: hotplug, EDID/DPCD access, link training at multiple link rates and lane counts, modeset, MST if applicable, suspend/resume, and multi-monitor operation.
- Check PHY debug/status evidence: MPLL calibration and state bits reach expected values, SRAM/init status is sane, VREF/RTUNE status is stable, RX adaptation ack/FOM and EQ values are plausible, signal-detect and LOS behavior matches cable state, TX/RX request/reset IRQs latch and clear as expected, and no unexpected DCC or calibration status persists after link bring-up.
- Regression symptoms include blank or flickering displays, DP training retries/timeouts, HDMI clock/audio instability, failures isolated to one lane or connector, stuck IRQs, stuck power/clock enables, elevated display power, and diagnostics showing impossible counter or status values.
