# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 59639-62003

## Scope And Purpose

This chunk is generated AMD DPCS 4.2.2 register field metadata. It contains no executable C logic; it publishes preprocessor constants for bit shifts and masks used to pack, update, and read fields in the DPCS `CR2` PHY/control-register space. Runtime code combines these field macros with the matching register-offset macros from `dpcs_4_2_2_offset.h` and DC register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `FD`, `SR`, and `SRI`.

The requested range is a mid-file slice of `dpcs_4_2_2_sh_mask.h` under the AMDGPU display driver source mirror. It starts inside the `DPCSSYS_CR2_RAWAONLANEX_DIG_TX_DCC_CONT` field definitions, then covers RAWAON lane signal-detect and firmware/calibration controls, a large `SUPX` shared-PHY block for reference clocks, MPLL A/B programming, analog bandgap/RTUNE/PLL controls, and the beginning-to-middle of per-lane `LANEX` TX/RX override, power-state, calibration, CDR, and LBERT controls. Although this repository path is under `ceph-client`, this file is GPU display hardware metadata, not distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, allocation paths, or persistence APIs in this range. The public interface is the generated macro namespace:

- `DPCSSYS_CR2_<register>__<field>__SHIFT`: the low bit position for a field.
- `DPCSSYS_CR2_<register>__<field>_MASK`: the raw bitmask for the same field.
- `RESERVED_*` field macros: generated masks for reserved bit ranges that consumers should generally preserve unless the hardware programming guide says otherwise.

Major register families covered by this chunk:

- `RAWAONLANEX_DIG_*`: always-on lane controls for MPLL bandgap state delay, HF/LF signal-detect override and readback, firmware micro/manual/adaptation/calibration configuration, lane transceiver mode override/readback, RX signal-detect filter counters, and TX duty-cycle-correction configuration.
- `SUPX_DIG_REFCLK_OVRD_IN`: shared reference-clock override fields for clock enable, pad selection, clock range, bandgap enable, HDMI mode, and pre-high-power override.
- `SUPX_DIG_MPLLA_*` and `SUPX_DIG_MPLLB_*`: symmetric MPLL A/B fields for divider clocks, HDMI divider clocks, enable/standby/frequency/VCO/calibration control, multipliers, fractional-N and spread-spectrum controls, SSC peak/stepsize words, charge-pump and gain controls, ASIC input mirrors, power-control status/timers/calibration, DAC output, and SSC spread type.
- `SUPX_DIG_SUP_*`, `PRESCALER_*`, `LVL_*`, `BANDGAP_*`, and `ASIC_IN`: shared supervisor, prescaler, level, bandgap, and ASIC input/override fields that bridge firmware/driver-visible digital control to analog PHY state.
- `SUPX_ANA_*`: analog-facing field maps for prescaler, RTUNE, bandgap, MPLL A/B miscellaneous, override, ATB, control, and reserved registers. These expose low-level PLL/bias/test controls and analog state mirrors.
- `SUPX_DIG_RTUNE_*` and `SUPX_DIG_ANA_*_OVRD_OUT`: RTUNE debug/config/status/set/stat/code fields plus digital-to-analog override outputs for MPLL, RTUNE, bandgap, and PMIX paths.
- `LANEX_DIG_ASIC_*`: per-lane TX/RX ASIC override input and output fields for lane mode, TX serializer/data/clock/swing/de-emphasis style controls, RX AFE/CDR/equalization controls, and status mirrors.
- `LANEX_DIG_TX_PWRCTL_*`: TX power-state bitfields for P0, P0S, P1, and P2 plus TX power-up timers, DCC bank address/data, DCC DAC control/range/select/ack/address, TX clock alignment, and TX LBERT control.
- `LANEX_DIG_RX_PWRCTL_*`: RX power-state bitfields for P0, P0S, P1, and P2 plus RX AFE/VREG/clock/fast-start/rate/CDR/deserializer power-up timing.
- `LANEX_DIG_RX_VCOCAL_*`: RX VCO calibration controls, timing, and status fields for startup/update/counter timing, override selection, reset, continuous calibration, DPLL update gain, tune start/steps, skip bits, FSM state, calibration done, counter values, and VCO correctness/up indicators.
- `LANEX_DIG_RX_CDR_*`, `RX_LBERT_*`, and `RX_RX_ALIGN_XAUI_COMM_MASK`: RX CDR phase/frequency detector/gain/SSC fields, CDR/DPLL status and bounds, loopback/error-rate-test controls and counters, and XAUI comma alignment mask.

Most masks in this chunk are 16-bit register-field masks represented as `0x....L`, with some generated as 32-bit-form constants whose active bits remain in the low 16 bits. That width matters because DPCS CR access is often addressed through 16-bit PHY register windows even when C code stores values in `uint32_t`.

## Control Flow

This header has no runtime control flow. The runtime sequence is supplied by display-driver code:

1. DCN 3.1.5 resource code includes `dpcs/dpcs_4_2_2_offset.h` and this matching `dpcs/dpcs_4_2_2_sh_mask.h`.
2. Register tables and helper macros token-paste register and field names into offset, shift, and mask constants.
3. Link encoder, PHY, clock, power, and diagnostic paths use register helpers to write field values, preserve unrelated bits, and poll status fields.
4. Hardware then performs the actual state transitions: reference-clock and bandgap bring-up, MPLL programming/calibration, TX/RX lane power-state entry and exit, signal detection, CDR/VCO calibration, DCC adjustment, RTUNE calibration, and LBERT/debug capture.

The chunk does not encode sequencing rules. Consumers must still order operations correctly: enable reference and bandgap resources before PLL use, program PLL dividers before dependent lane clocks, observe MPLL/RX VCO lock and calibration status before enabling high-speed data, and avoid overriding analog/ASIC fields while firmware or hardware finite-state machines own them.

## State And Persistence Behavior

The file stores no software state and persists nothing by itself. It describes MMIO or indirect CR-backed hardware state.

State represented by these fields includes:

- Shared PHY clocking state: reference-clock source/range/enables, HDMI mode, prescaler, bandgap, MPLL A/B enable/standby/divider/multiplier/fractional-N/SSC/charge-pump settings, lock and calibration timing, and PLL status.
- Per-lane TX state: power-state contents for P0/P0S/P1/P2, analog reference/clock/serializer/data enables, DCC compensation and DAC settings, power-up timing, TX clock alignment, and LBERT mode.
- Per-lane RX state: power-state contents, AFE/VREG/clock/CDR/deserializer timing, signal detection, equalizer-related ASIC overrides, RX VCO calibration configuration/status, CDR gain/SSC/phase detector settings, DPLL frequency and frequency bounds, XAUI comma masking, and LBERT error counters.
- Calibration and diagnostics: RTUNE set/stat/code values, firmware calibration/adaptation words, analog test-bus controls, OCLA selection, debug mux fields, FSM state readbacks, sticky status indicators, and error counters.

Persistence is hardware-defined. Configuration registers typically retain values until the link is reprogrammed, the PHY lane is power-gated, suspend/resume or display core reset runs, firmware reinitializes PHY state, or the ASIC resets. Status, calibration-done, counter, debug, and acknowledgment fields may be read-only, self-clearing, sticky, or write-sensitive depending on the underlying register. The mask header does not distinguish those access semantics, so driver code must rely on the hardware specification and existing register-access conventions.

## Dependencies And Integration Points

This chunk depends on the generated DPCS register database staying internally consistent:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies the `ixDPCSSYS_CR2_*` register addresses that pair with these masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` directly includes both the DPCS 4.2.2 offset and shift/mask headers and defines the DPCS base segments used by the display resource stack.
- AMD display register helpers consume the `__SHIFT` and `_MASK` macros through token-pasting field descriptors such as `FD(reg__field)` and through `REG_SET`/`REG_UPDATE`/`REG_GET` style helpers.

Functional integration points include DC link encoder and PHY programming, DisplayPort and HDMI link bring-up, link training, clock-source and PLL selection, PHY firmware handoff, lane power management, suspend/resume restore, hotplug and signal-detect handling, manufacturing or debug calibration flows, and diagnostic paths that read CDR/VCO/LBERT/OCLA/RTUNE status.

The chunk is also tightly coupled to adjacent generated slices. Its first lines are the tail of `TX_DCC_CONT` and its final line stops inside `DPCSSYS_CR2_LANEX_DIG_RX_CDR_CDR_CTL_4`; neighboring chunks are needed for complete register-family coverage and for any file-level conclusions.

## Risks And Edge Cases

- Mask or shift drift is the main risk. These are untyped preprocessor constants, so a wrong bit position or mask can compile cleanly while silently programming the wrong PHY field.
- DPCS CR2 field names are highly repetitive across `MPLLA`/`MPLLB`, TX/RX, and P0/P0S/P1/P2. Copy-generation mistakes can affect only one PLL, lane direction, or power state, making failures connector-specific or link-rate-specific.
- Reserved fields are exposed as macros but are not permission to write reserved bits. Read-modify-write helpers must preserve unrelated bits, especially in analog and PLL control registers.
- Override fields can fight autonomous hardware or firmware control. Incorrect use of `*_OVRD_EN`, `*_OVRD_VAL`, `ASIC_*_OVRD_*`, or analog override outputs can leave clocks, bandgap, PLLs, CDR, or lane power in a forced state after modeset, suspend/resume, or error recovery.
- PLL and clock fields are sequencing-sensitive. Bad `REFCLK`, `MPLL*`, SSC, charge-pump, timer, or lock/calibration masks can produce blank displays, unstable high link rates, HDMI clocking issues, spread-spectrum failures, or long waits on lock polling.
- TX/RX power-state and timer fields directly affect lane bring-up and power saving. Incorrect bitfields can cause excessive power, failure to exit low power, missed RX detection, broken deserializer/CDR startup, or intermittent link training failures.
- Calibration/status fields are often side-effect-sensitive. Misreading VCO/RTUNE/LBERT/DCC status or writing to ack/control fields with the wrong mask can hide real hardware faults or corrupt diagnostic data.

## Test Signals

Useful validation signals are mostly integration and hardware-facing rather than unit-testable:

- Build coverage for `dcn315_resource.c` and any resource/link encoder code that includes `dpcs_4_2_2_sh_mask.h`, catching missing or renamed generated macros.
- Static consistency checks that each field has both a `__SHIFT` and `_MASK`, that active masks remain within the expected 16-bit CR field width, and that paired A/B or P-state families remain structurally symmetric where the hardware expects symmetry.
- Display smoke tests on DCN 3.1.5-era hardware across HDMI and DisplayPort, including hotplug, EDID/DPCD reads, link training at multiple rates/lane counts, suspend/resume, and multi-monitor modesets.
- PHY-specific debug evidence: successful MPLL lock/calibration polling, RX VCO calibration done/correct/up status, stable signal-detect state, expected RTUNE status/code values, no LBERT error counter growth under test modes, and no unexpected CDR/DPLL frequency-bound violations.
- Regression signals include blank or flickering displays, HDMI audio/video clock issues, DP training failures, wake/resume failures, elevated power from stuck PHY states, unexpected timeouts in register polling, and failures limited to one connector or one link rate.
