# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 7278-9690

## Scope

This chunk is a generated AMD DPCS 4.2.3 shift/mask header slice. It contains C preprocessor constants only: `__SHIFT` bit-position macros and `_MASK` bit masks for DPCS CR0 lane registers. There are no functions, structs, enums, executable branches, memory allocations, locks, or software-owned persistence paths in this range.

The range begins mid-register at the final mask for `DPCSSYS_CR0_LANE0_DIG_ANA_TX_OVRD_OUT`, then completes lane 0 TX analog override and TX analog direct-control masks. Most of the chunk is the lane 1 register surface, covering digital ASIC TX/RX override and status registers, lane ASIC inputs, TX/RX power-control and calibration controls, RX adaptation/status/statistic controls, MPHY low-speed controls, digital-to-analog TX/RX override/status masks, and direct analog TX/RX controls. The range ends in the first lane 2 RX ASIC override register after starting the lane 2 digital ASIC override sequence.

I counted 2,174 macro definitions in this assigned range: 1,200 shift macros and 974 mask macros. The imbalance is expected for this generated style because many one-bit analog fields publish only shifts plus reserved/NC masks, and because this chunk starts and ends inside larger per-lane sequences.

## Purpose

The header supplies symbolic bit layouts for DPCS 4.2.3 CR0 indexed registers used by AMD display PHY and link-encoder code. The matching offset header identifies register addresses such as `ixDPCSSYS_CR0_LANE1_DIG_ASIC_TX_OVRD_IN_0`, while this file defines how driver code packs and extracts individual fields after selecting an indexed DPCS CR register.

The hardware areas represented here are low-level display lane controls:

- TX and RX ASIC-facing lane override inputs for reset, request, data enable, power state, link rate, lane width, MPLL selection, clock-ready, detect-RX request/result, polarity invert, low-power detect, DC coupling, MPHY mode, HDMI mode, main/pre/post cursor values, beacon/async drive, loopback, CDR tracking, SSC, alignment, clock shift, RX valid, and RX adaptation controls.
- ASIC-observed lane inputs and outputs that mirror normal controller-driven values, including TX/RX requests, pstate/rate/width, clock ready, detect-RX result, RX adaptation enable/DFE tap state, VCO/reference load values, RX valid, lane numbers, VCO calibration codes, and EQ status.
- Lane 1 TX power-control pstate registers and power-up timers for `P0`, `P0S`, `P1`, and `P2`, plus DCC DAC bank/address/data/control/range/select/ack fields.
- Lane 1 RX power-control pstate and timer registers, VCO calibration control/time/status, CDR/DPLL controls, RX adaptation state-machine configuration and status, RX stat match/control/counter registers, LBERT controls, and MPHY RX PWM/termination controls.
- Digital analog override/status registers for lane 1 TX and RX, including TX analog power/equalization/termination/DCC overrides, RX data-rate/clock/DFE/adaptation/power/VCO/calibration/DAC/AFE/CTLE/scope/slicer/IQ/sigdet/MPHY overrides, and hardware status readback.
- Direct analog TX/RX lane 1 controls for ATB measurement, loopback, power enables, voltage/reference/DCC/termination controls, CDR/deserializer/slicer/power/squelch/calibration knobs, and reserved or not-connected fields.

## Important API Surface

The exported API is the macro namespace itself. These definitions are intended to be consumed with `dpcs_4_2_3_offset.h` and AMD display register helper patterns such as generated `REG_GET`, `REG_SET`, `REG_UPDATE`, or equivalent indexed-register accessors.

Important register families in this chunk include:

- `DPCSSYS_CR0_LANE0_DIG_ANA_TX_*` and `DPCSSYS_CR0_LANE0_ANA_TX_*`: the tail of lane 0 TX analog control, including TX termination-code override, TX equalization override, TX DCC DAC override, TX fast-start/clock-loopback override, analog TX power, ATB measurement, DCC, termination, clock, peaking/slew/inversion, and reserved controls.
- `DPCSSYS_CR0_LANE1_DIG_ASIC_*`: the lane 1 digital ASIC interface. TX override registers expose `REQ`, `PSTATE`, `RATE`, `WIDTH`, `MPLLB_SEL`, `DATA_EN`, TX cursor, HDMI mode, reset, detect-RX, polarity, FIFO, DC-coupling, and MPHY controls. RX override registers expose request/data/pstate/rate/width, reference and VCO load values, CDR/SSC/alignment/disable, RX valid, adaptation, PCS selector, lossless LPD, term-control, and RX EQ delta/IQ controls. ASIC input/output registers provide the non-overridden hardware values and acknowledgement/status bits.
- `DPCSSYS_CR0_LANE1_DIG_TX_PWRCTL_*`: TX pstate and timing control. Each TX pstate register describes enable, clock-divider, serialization, data enable, width, rate, MPLL select, pstate, and request behavior for a specific power state. The DCC subfamily provides indirect bank address/data and DAC control/range/select/ack/address fields.
- `DPCSSYS_CR0_LANE1_DIG_RX_PWRCTL_*` and `DPCSSYS_CR0_LANE1_DIG_RX_VCOCAL_*`: RX pstate sequencing, RX power-up timing, VCO calibration thresholds, calibration enable, VCO load direction, startup-mode controls, timeouts, oscillator/divider status, and calibration result/status fields.
- `DPCSSYS_CR0_LANE1_DIG_RX_CDR_*`, `DPCSSYS_CR0_LANE1_DIG_RX_DPLL_*`, and `DPCSSYS_CR0_LANE1_DIG_RX_ADPTCTL_*`: CDR/DPLL and adaptation controls for filter coefficients, frequency bounds, state-machine counts, reset/disables, ATT/VGA/CTLE/DFE status, DAC selector controls, CR bank address/data, and slicer/reference-level offsets.
- `DPCSSYS_CR0_LANE1_DIG_RX_STAT_*`: match/statistic capture controls for sampled data masks, match words, rolling counters, clear/hold/enable controls, compare clock selection, and statistic stop.
- `DPCSSYS_CR0_LANE1_DIG_ANA_*`: digital override outputs into analog TX/RX blocks and analog status readback. Notable fields include TX analog request, data rate, pstate, divider/serial/data enables, TX eq pre/main/post controls, RX analog data rate, word clock/div4, DFE taps, adaptation, CDR VCO controls, calibration control, DAC selector, AFE ATT/VGA, CTLE, scope, slicer control, IQ phase adjustment, signal-detect, RX/TX term-code clocks, MPHY and sigdet overrides, DCC DAC override, and status bits such as RX/TX calibration and signal-detect results.
- `DPCSSYS_CR0_LANE1_ANA_TX_*` and `DPCSSYS_CR0_LANE1_ANA_RX_*`: direct analog lane 1 register fields for power, clock, loopback, ATB, DCC, term-code, peaking/slew/VREG, RX CDR startup/bias, IQ phase, word clock, slicer control, AFE/DFE/deserializer enables, squelch, calibration muxes, reference overrides, ATB measurement, and reserved/NC fields.
- `DPCSSYS_CR0_LANE2_DIG_ASIC_*`: the start of lane 2 digital ASIC override layout. It mirrors the lane 1 TX override/control pattern through `LANE2_DIG_ASIC_RX_OVRD_IN_0`, so the next chunk must complete lane 2 RX and downstream lane 2 families.

Most fields are 16-bit DPCS CR fields, with masks such as `0x0001L`, `0x00E0L`, `0x1FFFL`, `0x8000L`, and reserved masks like `0xFFF0L` or `0xFF00L`. Multi-bit fields that need width-sensitive handling include `PSTATE`, `RATE`, `WIDTH`, TX cursor fields, RX reference/VCO load values, adaptation counters, DPLL frequency bounds, CDR coefficients, calibration data, and RX stat counters.

## Control Flow

This header has no executable control flow. The implied runtime flow lives in display driver register-access code:

1. Driver code selects a DPCS CR0 indexed register address from `dpcs_4_2_3_offset.h`.
2. It reads or writes the 16-bit register through the DPCS CR address/data access path for the target display PHY instance.
3. It uses this header's shift and mask macros to pack field values or decode status bits.
4. Hardware lane controllers, PCS/PMA bridges, TX/RX PHY state machines, CDR/DPLL logic, adaptation engines, calibration circuits, and analog blocks perform the actual transitions.

The chunk's layout is strongly ordered by lane and block. It finishes the previous lane 0 TX analog sequence, provides a broad lane 1 digital-to-analog path, then starts lane 2 with the same digital ASIC override naming pattern. Merge/reconciliation should preserve that boundary context rather than treating this chunk as a complete per-file view.

## State And Persistence

The file stores no runtime state. Its constants describe hardware-backed state and control fields:

- Override-enable fields can force lane state away from normal controller ownership for reset, request, pstate, rate, width, data enable, clocking, CDR/adaptation, analog power, loopback, TX equalization, term-code, DCC, VCO/reference load, signal detect, and MPHY behavior.
- Status/readback fields expose transient hardware state such as TX/RX acknowledgements, detect-RX result, RX valid, calibration done/result values, RX signal-detect status, adaptation status, DFE/CTLE/VGA/ATT state, DPLL/CDR frequency, statistic counters, DCC ACK/status, and analog measurement values.
- Pstate, timing, mask, clear, and control registers are hardware state that persists until rewritten, cleared, power-gated, or reset by the display/PHY sequencing path. This header only names the bits; it does not cache or serialize them.
- Reserved and `NC` fields are part of the register word and should normally be preserved on read-modify-write unless the hardware database or register helper guarantees safe writes.

Incorrect use can leave a lane in reset, low-power, loopback, disabled data, forced HDMI/MPHY mode, invalid rate/width/pstate, wrong PLL selection, bad analog calibration, hidden interrupts/status, or a stale override until the PHY block is reinitialized.

## Dependencies And Integration Points

This generated header depends only on the C preprocessor, but it must stay synchronized with these layers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h`, which provides the matching `ixDPCSSYS_CR0_LANE*_*` register addresses. For this chunk, examples include `ixDPCSSYS_CR0_LANE1_DIG_ASIC_TX_OVRD_IN_0`, `ixDPCSSYS_CR0_LANE1_DIG_RX_ADPTCTL_ADPT_CFG_0`, and `ixDPCSSYS_CR0_LANE1_DIG_ANA_RX_CTL_OVRD_OUT`.
- AMD display register access helpers and generated register tables that combine offset, shift, and mask definitions.
- DisplayPort/HPO/DPCS link encoder and PHY bring-up code that programs lane rate, width, pstate, MPLL selection, TX/RX data enable, reset/request handshakes, equalization, calibration, and power transitions.
- PHY diagnostics, link training, low-power entry/exit, retraining, and debug/test flows that read status or temporarily set overrides, OCLA/LBERT/stat controls, ATB measurement, loopback, MPHY, signal-detect, and DCC controls.
- Sibling generated register packages. The same logical field families appear in nearby headers such as `dpcs_3_1_4_sh_mask.h`, `dpcs_4_2_0_sh_mask.h`, and `dcn_4_1_0_sh_mask.h`. They are useful for drift checks, but consumers must bind the DPCS 4.2.3 mask file to the DPCS 4.2.3 offset file for the target ASIC.

## Risks

- A wrong shift or mask in request/reset, pstate, rate, width, MPLL select, data enable, CDR/adaptation, VCO load, or analog power fields can cause lane-specific display link bring-up failures.
- Lane 1 is a large repeated block. Generated copy or naming drift can be hard to notice because neighboring lanes may still operate correctly.
- The range starts and ends mid-sequence. File-level research must reconcile adjacent chunks before claiming complete coverage for lane 0 or lane 2.
- Override value fields and override-enable fields are often adjacent. Setting a value without the intended enable, or leaving an enable set after diagnostics, can make hardware ignore normal PHY state-machine control.
- Status, clear, mask, control, and reserved/NC fields use similar names and small 16-bit masks. Mixing them can hide real PHY events, corrupt reserved bits, or clear diagnostic evidence.
- Analog fields often publish shifts without masks for every single-bit control. Callers must rely on register helper conventions or explicit bit construction and avoid assuming every shift has a matching `_MASK`.
- Cross-generation names overlap. Pulling a same-named field from `dpcs_4_2_0_sh_mask.h`, `dpcs_3_1_4_sh_mask.h`, or a DCN header can compile but still be the wrong generated contract if field widths or masks differ.

## Test Signals

Useful validation is primarily compile-time generation checks plus hardware/display smoke coverage:

- Build AMD display configurations that include DPCS 4.2.3 headers; missing, duplicated, or renamed macros should fail at compile time.
- Check every `_MASK` against its matching `__SHIFT` where both exist, especially multi-bit fields such as `PSTATE`, `RATE`, `WIDTH`, TX cursor fields, `RX_VCO_LD_VAL`, `RX_REF_LD_VAL`, adaptation counters, CDR coefficients, DPLL frequency bounds, RX stat counters, and reserved upper-byte masks.
- Compare lane 1 and lane 2 generated families for expected parity once the next chunk completes lane 2, excluding only the lane-number prefix and documented lane-specific exceptions.
- Cross-check this slice against `dpcs_4_2_3_offset.h` so every register family here has a matching indexed register address and no stale field family exists without an offset.
- Run hardware/link smoke tests for DisplayPort link bring-up, lane count/rate changes, link training and retraining, low-power transitions, reset/request handshakes, TX equalization updates, CDR/DPLL lock, RX adaptation, VCO calibration, DCC programming, and signal-detect behavior.
- Diagnostic reads after link training should show plausible `ACK`, `RX_VALID`, calibration status, DPLL/CDR status, adaptation status, DCC status, and analog status values for lane 1.
- Failure signatures include lane 1 only link failures, stuck TX/RX request or reset, bad detect-RX result, wrong data-enable state, broken rate/width changes, adaptation not starting or not converging, invalid VCO/reference load status, unexpected signal-detect state, or failures limited to DPCS 4.2.3 while adjacent DPCS generations pass.
