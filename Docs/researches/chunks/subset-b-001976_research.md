# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 115026-117470

## Purpose

This chunk is a generated AMD DCN 3.2.0 register-field shift/mask slice for C20 PHY CR1 lane control. It contains only C preprocessor constants: `*_SHIFT` macros for field bit positions, `*_MASK` macros for already-positioned bit masks, and `//<REGISTER>` comments that group the fields by hardware register. There are no functions, structs, enums, local variables, branches, loops, locks, allocation paths, or file-backed persistence in this range.

The line range covers 2,445 source lines and 2,119 `#define` lines. It starts in the tail of `C20_PHY_CR1_RAWLANEAON2_DIG_RX_CDR_DETECTOR_CTL`, where only the `DIS_IN_ADAPT` and reserved masks are visible from the previous register group. It then covers the end of raw-lane-AON2 RX signal-detect and override fields; a large raw-lane-AON3 TX/RX calibration, adaptation, DCC, IQ, and signal-detect section; and lane-generic `LANEX` ASIC/TX power/stat/analog-transfer fields. The chunk ends inside `C20_PHY_CR1_LANEX_DIG_ANA_XF_TX_ANA_CREG03`; the remaining masks and later CREG registers continue in the next chunk.

Although the repository path is under a Ceph client mirror, this file is AMDGPU Display Core hardware metadata for DCN 3.2 display PHY/DCIO programming. Its purpose is to let generated register tables and AMD display register helpers pack and decode MMIO fields without hard-coding bit positions in driver logic.

## Register Families Covered

The opening `RAWLANEAON2` tail covers receive-side signal-detect and PMA-facing controls:

- `C20_PHY_CR1_RAWLANEAON2_DIG_RX_CDR_RECOVERY_TIME` exposes CDR recovery timing.
- `DIG_RX_OVRD_IN_0`, `DIG_RX_IN_0`, `DIG_RX_OVRD_OUT_0`, and `DIG_RX_OUT_0` expose RX disable, termination enable/type, low/high-frequency signal-detect enable, high-frequency filter disable, VREF generator master, and signal-detect readback/override fields.
- `DIG_RX_SIGDET_EN_MASK_CTL` and `DIG_RX_SIGDET_FILT_CTL` define signal-detect enable masking, low/high-frequency filter counts, and LF hold fields.
- `DIG_RX_PMA_OVRD_OUT_0` exposes RX termination ground/DC enable and VREF generator output overrides.

The `RAWLANEAON3_DIG_TX` section covers TX firmware state, debug, recovery, power-up, DCC calibration, and calibration results:

- Firmware/debug state fields include `DIG_TX_FW_STATES_0`, `DIG_TX_FW_STATES_1`, `DIG_TX_MEM_BREAKPOINT_2`, and SRAM recovery registers for recovery control, max iteration count, base/current address, current iteration, and recovery enable.
- Control counters and flow-shortcut fields include CCA start/wait counts, startup/continuous algorithm controls, fast supervisor flags, high-power protection enable, lane transceiver mode, initial power-up done, and TX disable override.
- DCC calibration fields are split across MPLLA and MPLLB, with four banks each for control-range, full-rate common/differential code, half-rate common/differential code, and full/half calibration done flags.
- Aggregate readback/control fields include MPLLA/MPLLB calibration done, global TX calibration done, TX DCC control-range code, common/differential DCC code readback, half/full-rate code registers, TX recalibration bank select, and TX disable input.

The `RAWLANEAON3_DIG_RX` section is the largest part of the chunk and describes receive calibration and adaptive equalization:

- Startup and continuous algorithm skip controls cover RX AFE, reference, external reference, attenuator, VGA, external VGA, CTLE, IQ, IQ delta, phase, external phase, DFE, external DFE, error, bypass, VGEN, signal-detect, VGA slicer, buffer, DCC, full-rate/half-rate, DCC data/phase/bypass, rate-time DCC/range/IQC, banked AFE/DFE/IQ adaptation, reload, TX inc/dec, FOM, and margining.
- Fast flags expose shortened startup calibration, adaptation, continuous calibration/adaptation, power-up, VCO calibration, and VCO wait behavior.
- Analog calibration offsets include VGEN VDAC offset/done, signal-detect LF/HF calibration, AFE resistor trim, reference VDAC offsets, DFE even/odd VDAC offsets, CTLE/VGA setup IDAC offsets, VDAC range selection, AFE attenuator/CTLE/VGA/buffer IDAC offsets, DFE phase/data/bypass/error VDAC offsets, and IQ calibration divider/ranges.
- Four RX DCC/IQ banks provide control range, full/half data/bypass/phase common and differential codes, IQ half/full values, and calibration done bits.
- Aggregate RX DCC and IQ fields provide bank selection, data/bypass/phase common/differential code registers, half/full-rate split code registers, IQ calibration value, calibration done, IQ adaptation controls, DPLL thresholds, IQ limits, and error slicer mode.
- Banked adaptation results are present for banks 0 and 1: attenuator, VGA, CTLE boost/pole, DFE taps 1-5, multiple DFE tap-1 offsets by even/odd high/low data/error paths, tap-valid flags, IQ result/valid, reference error, and adaptation done.
- TX-coefficient guidance for RX adaptation includes direction polarity, pre-divider, main attenuator/VGA thresholds, post boost threshold, and post tap1 threshold.
- Generic adaptation controls `DIG_RX_ADPT_CTL_0` through `DIG_RX_ADPT_CTL_28` are 16-bit value registers.
- RX CDR/margin/signal-detect/override fields mirror the earlier raw-lane-AON2 tail: IQ margin min/max, CDR detector enable/PPM monitor/disable-in-adapt, CDR recovery time, RX disable/termination/signal-detect/VREF overrides, signal-detect filter/mask controls, PMA output overrides, RX input status, and signal-detect outputs.

The lane-generic `C20_PHY_CR1_LANEX` section bridges ASIC-side lane signals, digital TX power/stat controls, and analog TX controls:

- `DIG_ASIC_*` registers expose lane serial/parallel loopback, transceiver mode, TX clock-ready/reset/invert/data-enable/request/low-power-detect/pstate/rate/width/alignment/MPLLB/detect-rx/flyover controls, TX NYQUIST/disable/beacon/iboost/vboost/enable controls, pre/main/post cursor controls, DCC bypass/range/update, async FIFO, lane/clock deskew, KR driver enable, VREG bypass, TX ack, detect-rx result, calibration status, and miscellaneous override fields.
- `DIG_TX_PWRCTL_*` registers define TX P-state templates for P0, P0S, P1, and P2. Each template controls analog refgen, VCM hold, clock enable, reset, serial enable, digital clock, data enable, RX detect allowance, VBOOST allowance, analog DCC, VREG bleeders, and word clock enable. Power-up timing registers define delays for refgen, clock, VCM hold, VBOOST disable, reset, RX detect, fast start, serial enable, and bleeder enable.
- TX power/control/status fields include clock enable, clock alignment skip controls, DTB select, DCC DAC force/write enable, TX request disable, clock loopback late enable, calibration DAC override gating, rate IRQ, and power-state-machine state.
- TX DCC/stat/debug fields include differential/common IDAC offsets with override enables, DCC FSM states, stat counter controls, sample counters, comparator clock controls, explicit stat stop, clock-alignment controls/status, LBERT mode/pattern/error trigger, level calibration bin, and FIFO read-pointer/bypass controls.
- `DIG_ANA_XF_TX_*` registers expose the digital-to-analog TX boundary: analog clock/MPLL/divider/reset/serial/data/refgen/VCM/VREG/bleeder/rate/loopback/RXDET/VBOOST/word-clock/asynchronous-reset overrides, analog termination and termination-clock overrides, analog DCC enable/config/calibration controls, DCC DAC range/data, EQ override/readback for pre/post and leg pull fields, analog status outputs, analog status inputs, and analog CREG00-CREG03 control/test fields.

## Important APIs, Types, And Functions

This range exposes a macro-only API:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index of a hardware register field.
- `<REGISTER>__<FIELD>_MASK` gives the register-positioned mask for that field, usually with an `L` suffix.
- Single-bit controls and status fields commonly use `0x0001L`, while packed fields cover 2-bit to 16-bit values such as pstate, rate, width, DCC codes, IQ/DPLL thresholds, analog trim values, counters, and firmware addresses.
- `RESERVED_*` masks are present throughout and are important for read-modify-write helpers that preserve reserved bits.

There are no callable C APIs or C data types in this chunk. Consumers normally include this file with the matching DCN 3.2.0 offset header and use generated AMD display register helpers such as field-setting, field-reading, polling, and read-modify-write macros. Missing or renamed symbols tend to fail at compile time; incorrect numeric values usually compile and fail only as hardware behavior.

## Control Flow

There is no executable control flow in the header itself. Runtime control flow is supplied by AMDGPU Display Core, DCN/DCIO PHY sequencing code, firmware handshakes, and hardware state machines that read or write the registers described here.

The hardware flows represented by these fields include:

1. TX bring-up and power-state sequencing. P-state templates, power-up timers, clock/reset/request/data controls, VREG/bleeder/refgen controls, and power-state-machine status fields determine how the lane transitions between active and lower-power states.
2. TX DCC calibration. Startup/continuous skip bits, MPLLA/MPLLB banked DCC codes, DAC control-range fields, DCC FSM status, calibration done bits, and analog DCC override/config fields participate in transmit duty-cycle-correction calibration.
3. RX startup calibration and adaptation. Algorithm skip fields and fast flags control which AFE, reference, VGEN, signal-detect, VGA, CTLE, DFE, IQ, phase, bypass, error, DCC, and margining steps run during lane initialization or continuous adaptation.
4. RX signal-detect/CDR and PMA interaction. RX CDR detector, recovery timing, signal-detect filters, termination controls, and PMA override outputs provide the bit layout for physical link presence and receive-path readiness.
5. ASIC-to-analog lane control. `LANEX` ASIC and analog transfer fields map high-level digital lane state into analog TX enables, clocks, loopback, EQ coefficients, termination, VBOOST, RX detect, DCC, and status handshakes.
6. Test and debug flows. Breakpoint, SRAM recovery, LBERT pattern, stat counters, comparator clocks, CREG test controls, and analog test-bus fields support hardware bring-up or lab diagnostics rather than ordinary display modeset policy.

The header does not encode sequencing order, reset values, access permissions, volatile/read-only behavior, write-one-to-clear semantics, or self-clearing behavior beyond field names such as `SELF_CLEAR_DISABLE`. Those rules live in the hardware specification and in the driver/firmware code that consumes the generated metadata.

## State And Persistence Behavior

This file stores no software state. It describes MMIO-backed hardware state. Written values persist in hardware registers until reset, power gating, firmware ownership changes, link reinitialization, or another software write changes them.

Configuration-style fields in this chunk include TX/RX algorithm skip controls, fast flags, override enable/value pairs, TX P-state templates, TX power-up timers, DCC offset/override controls, DCC DAC/range controls, analog override registers, EQ override fields, RX CDR/signal-detect filtering, RX adaptation controls, IQ margin range, and analog CREG control/test fields.

Status/readback-style fields include firmware state bits, recovery iteration/address values, initialization power-up done, MPLLA/MPLLB/TX/RX calibration done flags, banked adaptation results, reference error, adaptation done, signal-detect outputs, TX ack, detect-rx result, calibration status, TX power-state-machine state, DCC FSM states, stat/sample counter done fields, clock-alignment status, analog status outputs, and analog status inputs.

Side-effect-sensitive fields include override enables, disable bits, reset bits, DCC DAC write enable/force controls, calibration control enables, self-clear-disable fields, stat counter starts/stops, LBERT error triggers, and TX request disable. Treating these as passive booleans can force a lane into an unintended power/reset/calibration/test state.

## Dependencies And Integration Points

The direct generated companion is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`

The offset header supplies register addresses and base indices; this shift/mask header supplies field layouts. They must be generated from the same DCN 3.2.0 register database.

Likely source-tree integration points are:

- DCN 3.2 resource and register-table construction that binds register offsets to shift/mask structures for the display driver.
- DCIO/PHY link training code that programs lane rate, pstate, reset/request, TX coefficients, loopback, signal-detect, CDR, and calibration controls.
- DisplayPort link training and diagnostics that inspect RX adaptation, DFE/CTLE/VGA/AFE/IQ results, reference errors, margining ranges, and TX coefficient adjustment hints.
- Power-management and suspend/resume paths that restore TX P-state templates, power-up timing, clock/reset/data enable controls, and analog VREG/refgen/bleeder state.
- Firmware-assisted PHY management and bring-up tools that use SRAM recovery, firmware states, breakpoints, calibration done bits, and skip/fast control registers.
- Hardware validation tooling that uses LBERT patterns, stat counters, analog CREG test-bus fields, DCC status, and comparator/clock-alignment registers.

Because these macros are generated, hand edits are risky. A mismatch between the offset header and this shift/mask header can cause driver code to write a valid field layout into the wrong register, or a valid register address with the wrong field layout.

## Risks And Edge Cases

- The first visible line is partial: `C20_PHY_CR1_RAWLANEAON2_DIG_RX_CDR_DETECTOR_CTL` began in the previous chunk, and only tail masks are visible here.
- The last visible register is partial: `C20_PHY_CR1_LANEX_DIG_ANA_XF_TX_ANA_CREG03` continues beyond line 117470 with remaining fields and masks.
- Many fields are repeated by bank number, PLL instance, rate class, common/differential half, or analog/digital boundary. Copy-generation drift can silently swap bank 0-3, MPLLA/MPLLB, full/half, data/bypass/phase, common/differential, or override/status meanings.
- Override registers often pair value bits with enable bits. Setting a value without its enable may do nothing; setting an enable with a stale value can force unintended lane behavior.
- TX power and analog controls are sequencing-sensitive. Wrong masks can leave a lane in reset, disable data, block RX detect, select the wrong MPLL, break clock alignment, or hold analog circuitry in an unsafe power state.
- RX calibration and adaptation skip bits are powerful lab controls. Incorrect defaults can bypass DCC, IQ, AFE, DFE, CTLE, VGA, phase, signal-detect, or margining operations and produce links that are unstable only at certain rates, channels, or power states.
- DCC and analog calibration fields influence signal integrity. Incorrect common/differential or full/half-rate codes may compile cleanly while causing bit errors, failed link training, or intermittent display loss.
- Status, control, and test/debug fields live next to each other. A broad read-modify-write mask that touches reserved or self-clearing fields can corrupt diagnostics or trigger hardware actions.
- Generic `LANEX` naming indicates lane-template style fields rather than a concrete raw lane number. Consumers must bind the correct instance address from the offset/header register table.

## Test Signals

Useful validation signals for consumers of this metadata include:

- Build AMDGPU Display Core with DCN 3.2 enabled; missing or malformed generated macros should fail in register-table or helper macro expansion.
- Mechanically compare this range against the authoritative DCN 3.2.0 register database or a regenerated `dcn_3_2_0_sh_mask.h`, preserving the partial opening and closing register groups.
- Run generated-header consistency checks: each complete non-reserved field should have matching shift and mask definitions, masks should match shifts/widths, repeated banked fields should be consistent, and reserved masks should cover only the intended bits.
- On DCN 3.2 hardware, exercise DisplayPort link training across rates and lane counts, checking TX request/reset/data enable, pstate, MPLL selection, TX coefficients, RX CDR, signal detect, calibration done, and adaptation done behavior.
- Test suspend/resume, hotplug, modeset, and power-state transitions to verify TX P-state templates, power-up timers, analog refgen/clock/reset/serial/data/VREG controls, and calibration state restoration.
- Run PHY diagnostics or margining tests that inspect RX IQ margin range, IQ adaptation, reference error, DFE/CTLE/VGA/AFE adaptation results, DCC data/bypass/phase codes, and TX coefficient direction thresholds.
- Use controlled lab validation for LBERT, stat counters, DCC override, analog CREG/test-bus, and SRAM recovery/breakpoint paths, since these fields can intentionally perturb normal lane operation.

## Chunk Boundary Notes

This report covers only lines 115026-117470. It should be reconciled with the adjacent chunks before the final per-file document makes complete claims about `RAWLANEAON2_DIG_RX_CDR_DETECTOR_CTL` or `LANEX_DIG_ANA_XF_TX_ANA_CREG03`. The final merge should also keep the distinction between raw-lane-AON2 tail fields, raw-lane-AON3 TX/RX calibration/adaptation fields, and lane-generic `LANEX` ASIC/TX/analog transfer fields.
