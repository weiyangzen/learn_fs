# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 141854-144246

## Scope

This chunk is part of the generated AMD DCN 4.1.0 ASIC register shift/mask header. It contains preprocessor constants only: hardware fields are exposed as `...__SHIFT` bit offsets and `..._MASK` bit masks. There are no C functions, structs, branches, allocations, locks, or direct MMIO operations in this range.

The range covers 2,173 macro definitions across 220 register-comment blocks. It starts at the tail of `DPCSSYS_CR3_SUPX_ANA_MPLLAB_CTR_OUTCLK` mask definitions, continues through CR3 supervisor/PLL and lane-X digital PHY control/status fields, and ends at the first field of `DPCSSYS_CR3_LANEX_DIG_ANA_SIGDET_OVRD_OUT_1`. Neighboring chunks are needed for the complete boundary registers.

## Purpose

The purpose of this chunk is to publish exact bitfield metadata for DCN 4.1.0 DPCS/DPCSSYS CR3 supervisor and lane PHY registers. Runtime display code combines these shift/mask constants with matching register-address definitions from offset headers and with AMD display register-helper macros to read, write, update, or poll individual hardware fields without hand-coded bit arithmetic.

Important covered areas:

- CR3 supervisor MPLL analog control: `DPCSSYS_CR3_SUPX_ANA_MPLLAB_CTR_LOCK`, `CTR1` through `CTR7`, and `CTR_PMIX` define paired MPLLA/MPLLB analog PLL override, charge-pump, VREG, PLL ring, DAC, PFD, lock-phase, DLL, and PMIX fields.
- CR3 MPLLA/MPLLB digital power control: `DPCSSYS_CR3_SUPX_DIG_MPLLA_MPLL_PWR_CTL_*` and `...MPLLB...` define override selection, power/clock enable controls, FSM/status bits, DAC max-range fields, lock/stable/gearshift/pixel-clock-stable timers, calibration, analog DAC output, and SSC spread type.
- Supervisor clock/reset and resistor tuning: `DPCSSYS_CR3_SUPX_DIG_CLK_RST_*` and `DPCSSYS_CR3_SUPX_DIG_RTUNE_*` define bandgap/reference power-up timings, RTUNE configuration/status, RX/TX set values, calibration counters, and TX calibration code status.
- Supervisor-to-analog override/status paths: `DPCSSYS_CR3_SUPX_DIG_ANA_MPLLA_OVRD_OUT_*`, `...MPLLB_OVRD_OUT_*`, `RTUNE_OVRD_OUT`, `ANA_STAT`, `ANA_BG_OVRD_OUT`, and PMIX override registers expose digital override values, self-clearing clock controls, analog status readbacks, bandgap controls, and PLL/PMIX override-enable fields.
- Lane-X ASIC interface and override surfaces: `DPCSSYS_CR3_LANEX_DIG_ASIC_*` blocks define lane, TX, RX, and RX EQ override inputs, live ASIC input mirrors, output/acknowledge fields, OCLA selection, power-state requests, data rate/width, HDMI mode, inversion, reset, detect-RX, equalization, CDR tracking, and VCO controls.
- Lane-X TX/RX power and calibration controls: `DIG_TX_PWRCTL_*`, `DIG_RX_PWRCTL_*`, `DIG_RX_VCOCAL_*`, `DIG_RX_CDR_*`, `DIG_RX_DPLL_*`, and `DIG_RX_ADPTCTL_*` define pstate programming, power-up timers, DCC DAC control/acknowledge/address, VCO calibration, CDR/DPLL tuning, adaptation configuration, adaptation status, DFE offsets, slicer controls, reset, and CR bank access.
- Lane-X diagnostics/statistics and analog digital overrides: `DIG_RX_STAT_*`, `DIG_MPHY_RX_*`, and `DIG_ANA_*` blocks define pattern/statistic controls, counters, stop controls, MPHY PWM/termination timing, TX/RX analog override outputs, equalization, termination, CDR/VCO override, RX calibration mux/DAC/scope/slicer/IQ controls, analog status, and MPHY override controls.

## Important Macros and Field Families

The exported API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit position of a field inside the hardware register.
- `<REGISTER>__<FIELD>_MASK` gives the field mask, usually within a 16-bit DPCS sideband register.
- Register prefixes are semantically significant. `DPCSSYS_CR3_SUPX_*` names are supervisor/common PHY fields for CR3, while `DPCSSYS_CR3_LANEX_*` names are lane-replicated PHY fields.

Notable field families include:

- MPLL control and status: `MPLLA_*` and `MPLLB_*` fields for PLL override locks, power FSM state, PCLK/output/feedback clock enable, calibration/reset/analog-enable/lock status, DAC range, lock and stable timers, PCLK stable timing, calibration triggers, and SSC spread type.
- Override-enable pairs: many blocks pair a forced value with an enable bit, for example `OVRD_SEL`, `*_OVRD_EN`, `FAST_MPLL_*`, `TX_OVRD_EN`, `RX_CTL_OVRD_EN`, `RX_PWR_OVRD_EN`, `RX_VCO_CDR_OVRD_EN`, `TX_EQ_OVRD_EN`, and RTUNE/bandgap override fields.
- ASIC lane programming: TX and RX override/input fields cover `REQUEST`, `PSTATE`, `PSTATE_ACK`, `RATE`, `WIDTH`, `DATA_EN`, `SERIAL_EN`, `CLK_EN`, `RESET`, `INVERT`, `HDMI_MODE`, `CTRL_PRE`, `CTRL_POST`, `CTRL_MAIN`, `AUXRD`, `MPLL_SEL`, `CDR_TRACK_EN`, `DFE_TAPS_EN`, and adaptation enables.
- Power-state tables: TX/RX `PSTATE_P0`, `P0S`, `P1`, and `P2` registers encode per-state analog clock/data/serial/deserial/DCC/VCO/AFE/CDR enable and reset behavior.
- Calibration and tuning: VCO calibration registers define range, mode, enables, counters, done/correct/up indicators, and result values; CDR/DPLL/adaptation registers define coefficient, comparator, VCO divider, SSC mode, frequency bound, CTLE/VGA/ATT/DFE status, slicer levels, DAC selectors, and adaptation reset fields.
- Diagnostics and counters: LBERT controls, RX statistic match/control/sample/counter registers, OCLA selection, scope controls, VCO counters, calibration DAC controls, IQ phase adjustment, and analog status fields support lab/debug validation and link diagnostics.

## Control Flow and Runtime Integration

This header has no executable control flow. Runtime behavior is indirect:

1. ASIC-specific display and link code includes this generated shift/mask header with the matching DCN/DPCS offset headers.
2. Register descriptor tables or helper macros pair a register address such as a DPCS `ix...` offset with the corresponding `__SHIFT` and `_MASK` definitions from this file.
3. Driver code uses AMD display register helpers such as register get/set/update/wait helpers to isolate and modify fields.
4. Hardware state changes occur in DPCS/DPCSSYS registers; this file only supplies compile-time metadata for those changes.

The represented flow is typically: program supervisor MPLL and clock/reset timing, configure lane pstate/rate/width and power sequencing, optionally assert override paths for bring-up or debug, start calibration/adaptation, and poll status/counter/result fields such as MPLL lock, VCO calibration done/correct/up, DCC DAC acknowledge, adaptation done, statistic counters, or analog status bits.

## State and Persistence Behavior

The file itself has no mutable or persistent state. All represented state lives in hardware registers.

The hardware state described by these fields includes:

- PLL/supervisor state: MPLLA/MPLLB control trims, power FSM status, lock state, clocks, calibration, stable timers, SSC mode, bandgap/reference power-up timing, and RTUNE calibration state.
- Override state: software-forced values and enable bits can pin PLL, RTUNE, bandgap, TX, RX, CDR/VCO, equalization, termination, calibration, and analog power/control paths.
- Lane power state: pstate tables and timing registers encode how TX/RX analog and digital blocks enter or leave P0/P0S/P1/P2 and how long power-up or stable waits last.
- Calibration/adaptation state: VCO/CDR/DPLL tuning, DCC DAC settings, CTLE/VGA/ATT/DFE results, slicer/DAC offsets, calibration muxes, scope controls, counters, and completion/status flags are latched in the PHY hardware.
- Diagnostic state: RX statistic match/counter setup, LBERT controls/errors, OCLA selection, MPHY low-speed/PWM controls, and analog status/counter readbacks are maintained by hardware until reset or reprogramming.

Persistence is limited to the lifetime of the hardware register programming. Values may be reset or need reprogramming after GPU reset, display engine reset, DPCS reset, lane reset, power gating, suspend/resume, hotplug retraining, or mode set. Higher-level driver state and link-training policy remain the source of truth.

## Dependencies

This chunk depends on matching generated address definitions, especially DPCS/DCN 4.1.0 or closely related offset headers that define the `ixDPCSSYS_CR3_*` register addresses. Shift/mask macros alone do not identify an MMIO or indirect-register address.

It also depends on:

- AMD display register-helper infrastructure that expands register and field names into masked reads, writes, updates, and waits.
- DCN 4.1.0 DPCS/DPCSSYS silicon register specifications used to generate this header.
- Link encoder, PHY, and display core code that programs DP/HDMI/USB-C PHY lanes, MPLLs, power states, link training, calibration, and diagnostics.
- Generated or hand-maintained register tables that keep CR3 supervisor and lane-X prefixes aligned with the matching address namespace.

Because this is generated silicon metadata, manual changes are risky unless synchronized with the register database, the paired offset headers, and any generated register tables.

## Integration Points

The main integration point is the macro-name ABI between generated headers and display code. A consumer naming a field such as `DPCSSYS_CR3_LANEX_DIG_RX_CDR_CDR_CTL_0__CDR_REF_DIV` relies on this header to provide the exact bit offset and mask for the selected register.

Integration surfaces include:

- DP/HDMI PHY bring-up: MPLL selection, rate/width programming, TX/RX enable/reset, data/serial clocks, HDMI mode, detect-RX, pre/main/post cursor controls, and DCC calibration.
- Link training and recovery: VCO calibration, CDR tracking, DPLL frequency bounds, CTLE/VGA/ATT/DFE adaptation, slicer/VDAC offsets, RX calibration, and status polling.
- Power management: supervisor clock/reset timing, MPLL power FSM controls, lane pstate tables, TX/RX power-up timers, fast-start paths, and low-power MPHY/PWM/termination controls.
- Diagnostics and validation: LBERT, OCLA, RX statistics, scope/IQ phase controls, analog status bits, VCO counters, termination code overrides, and calibration DAC controls.
- Multi-instance hardware mapping: CR3-specific and lane-X-replicated names must line up with the correct DPCS address offsets so a field update targets the intended controller/lane.

## Risks and Failure Modes

- Incorrect shifts or masks can corrupt adjacent fields in the same 16-bit DPCS register, causing link-training failures, unstable PLL/CDR lock, bad equalization, broken power transitions, or blank display.
- CR3 and lane-X naming alignment is critical. A copied field from another CR or lane block can compile cleanly but program the wrong hardware instance.
- Stale override-enable bits can pin PHY state and defeat normal hardware sequencing, especially for MPLL power, RTUNE, bandgap, TX/RX power, CDR/VCO, equalization, termination, and calibration paths.
- Status, acknowledge, load-clock, self-clear-disable, and reset fields require correct write semantics. A bad mask can miss a completion condition or accidentally hold a calibration/debug operation active.
- Analog trim and calibration fields are silicon-sensitive. Errors in PLL charge pump/VREG/DAC, RTUNE, DCC, CDR/VCO, AFE/CTLE/VGA/DFE, termination, or slicer fields can produce intermittent failures dependent on cable, sink, board, temperature, lane count, and link rate.
- Many fields use high-bit masks such as `0x8000L`; consumers should preserve unsigned-safe register math and avoid narrowing assumptions.
- This chunk begins and ends inside larger register families, so a final per-file report must reconcile adjacent chunks for complete `OUTCLK` and `SIGDET_OVRD_OUT_1` context.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Compile-time coverage: DCN 4.1.0 display/link/PHY code builds with no missing `DPCSSYS_CR3_SUPX_*` or `DPCSSYS_CR3_LANEX_*` `__SHIFT`/`_MASK` symbols.
- Register-table sanity: generated CR3 supervisor and lane-X register tables pair these shift/mask definitions with matching DPCS offsets and preserve expected prefix ordering.
- Display smoke tests: DP and HDMI mode set, hotplug, suspend/resume, GPU reset, link retraining, and different lane-count/link-rate combinations.
- PLL and power validation: MPLLA/MPLLB lock/status, power FSM state, PCLK/output/FB clock enables, stable/lock timer behavior, pstate transitions, and fast-start paths.
- Link-training diagnostics: VCO calibration done/correct/up fields, CDR tracking and DPLL frequency bounds, CTLE/VGA/ATT/DFE adaptation status, slicer/VDAC offsets, RX calibration results, and analog status readbacks.
- Debug path checks: LBERT error counters, OCLA selection, RX statistic match/counter operation, scope/IQ phase controls, VCO counter reads, DCC DAC request/ack/address behavior, and termination override clocks.

## Chunk Notes

This chunk is a source-tree-aligned chunk report only. It intentionally does not attempt a final per-file synthesis for `dcn_4_1_0_sh_mask.h`; that merge is left for the reconciliation lane after all chunks for this generated header are available.
