# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 40593-42955

## Scope

This chunk is a generated AMD DPCS 4.2.0 register shift/mask header segment. It covers line 40593 through line 42955 and defines 2,132 preprocessor constants: 1,065 `__SHIFT` macros and 1,067 `_MASK` macros.

The count mismatch is a chunk-boundary artifact. The range starts in the middle of `DPCSSYS_CR1_SUPX_ANA_MPLLA_CTR3`, where four mask definitions are included but the matching shifts are immediately before line 40593. The range ends after the first two shift definitions for `DPCSSYS_CR1_LANEX_DIG_ANA_SIGDET_OVRD_OUT_1`; the remaining shifts and masks for that register follow after line 42955.

The content is declarative only. It exports bitfield positions and masks for DPCS CR1 SUPX and LANEX hardware registers; it contains no C functions, structs, runtime storage, or branching logic.

## Purpose

The header gives AMDGPU display code symbolic field definitions for programming DPCS 4.2.0 display PHY, PLL, lane, adaptation, power, calibration, statistics, and analog override registers. Consumer code includes these macros together with companion register-address headers to form read-modify-write operations against memory-mapped display hardware without open-coded bit positions.

In this range, the exported constants cover:

- SUPX analog MPLLA and MPLLB controls, overrides, ATB measurement fields, PLL tuning fields, and reserved windows.
- SUPX digital MPLL power-control, PLL lock/calibration/timer, spread-spectrum, bandgap/reference power-up, resistor tuning, and analog status/override fields.
- LANEX ASIC-facing lane, TX, RX, equalization, CDR/VCO, and override input/output fields.
- LANEX TX and RX power-state, power-up timing, DCC calibration, clock alignment, loopback/BERT, CDR, VCO calibration, DPLL, adaptation, and statistics fields.
- LANEX MPHY and analog TX/RX override fields for terminations, equalization, receiver front-end tuning, calibration DAC selection, slicer/scope control, status readback, and signal-detect controls.

## Exported API Surface

There are no callable APIs or local types. The public surface is the macro namespace used by AMD display code after including this generated ASIC register header.

Important macro families:

- `DPCSSYS_CR1_SUPX_ANA_MPLLA_*` and `DPCSSYS_CR1_SUPX_ANA_MPLLB_*`: analog PLL control and measurement fields. The chunk begins with `MPLLA_CTR3` masks, then covers `MPLLA_CTR4`, `MPLLA_CTR5`, `MPLLA_RESERVED1/2`, and the analogous MPLLB `MISC`, `OVRD`, `ATB`, `CTR`, and reserved registers.
- `DPCSSYS_CR1_SUPX_DIG_MPLLA_MPLL_PWR_CTL_*` and `DPCSSYS_CR1_SUPX_DIG_MPLLB_MPLL_PWR_CTL_*`: digital PLL override, status, DAC max range, lock/power timers, calibration, and analog DAC output fields for the two MPLL blocks.
- `DPCSSYS_CR1_SUPX_DIG_CLK_RST_*` and `DPCSSYS_CR1_SUPX_DIG_RTUNE_*`: bandgap/reference power-up timing, reference voltage/power-up behavior, and RTUNE calibration configuration/status/set-value fields.
- `DPCSSYS_CR1_SUPX_DIG_ANA_*`: digital-to-analog override and status outputs for MPLLA, MPLLB, RTUNE, bandgap, and PMIX controls.
- `DPCSSYS_CR1_LANEX_DIG_ASIC_*`: ASIC-side per-lane TX/RX controls, overrides, equalization controls, VCO/CDR inputs, loopback/status outputs, and OCLA control.
- `DPCSSYS_CR1_LANEX_DIG_TX_PWRCTL_*` and `DPCSSYS_CR1_LANEX_DIG_RX_PWRCTL_*`: transmit and receive power-state programming plus power-up timing registers.
- `DPCSSYS_CR1_LANEX_DIG_RX_VCOCAL_*`, `RX_CDR_*`, and `RX_DPLL_*`: receiver VCO calibration, CDR loop, and DPLL frequency/boundary fields.
- `DPCSSYS_CR1_LANEX_DIG_RX_ADPTCTL_*`: receiver adaptation configuration, reset, status, DAC selection, CR-bank access, slicer, DFE, CTLE, VGA, and attenuator fields.
- `DPCSSYS_CR1_LANEX_DIG_RX_STAT_*`: match/statistic control, masks, counters, sample counters, stop control, and calibration compare clock control fields.
- `DPCSSYS_CR1_LANEX_DIG_ANA_*`: analog TX/RX override outputs, termination-code override and clock strobes, TX equalization override fields, RX control/power/VCO/calibration/AFE/scope/slicer/IQ/status/MPHY/signal-detect fields.

## Register Areas Covered

The SUPX analog area exposes two similar MPLL paths. `MPLLA` and `MPLLB` fields describe charge-pump, regulator, SPO, VINT capacitor, standby, calibration-lock, bypass, DLL/divider, ATB measurement, and override behavior. These names indicate low-level PLL tuning and diagnostic access rather than ordinary display policy.

The SUPX digital area manages MPLL power and calibration sequencing. It includes override enable/data bits, reference-clock enable, reset, calibration requests, lock/power timers, DAC range and output fields, spread-spectrum type, clock/reset power-up timing, RTUNE comparator/code fields, and analog-facing override outputs. This area is the bridge between driver-controlled digital sequencing and the analog MPLL/RTUNE/BG hardware.

The LANEX ASIC interface area maps the logical lane controls exchanged with the rest of the display engine. It defines lane reset, TX/RX reset and enable, width/rate, DETRX, PMA/PCS power state, loopback, equalization, clock-shift, data-enable, CDR/VCO inputs, and status outputs. The repeated `*_OVRD_IN`, `*_OVRD_OUT`, `*_ASIC_IN`, and `*_ASIC_OUT` naming shows that this block supports both normal ASIC-driven operation and explicit override paths.

The LANEX TX/RX datapath area covers state-machine programming for link bring-up and diagnostics. TX fields include P-state settings, power-up timers, duty-cycle-correction DAC bank/address/data/ack fields, clock alignment, and LBERT control. RX fields include P-state settings, power-up timers, VCO calibration control/status/time, LBERT control/error, CDR loop controls/status, DPLL frequency/bounds, and receiver adaptation controls/status.

The LANEX analog output area exposes direct analog override signals. TX fields control terminations, EQ main/post/pre cursors, EQ clock strobes, idle detect, lane power, clock shifting, and DCC. RX fields control AFE attenuation/VGA/CTLE, CDR/VCO frequency tuning, calibration muxes and DACs, slicer even/odd controls, IQ phase adjustment, scope capture, MPHY low-speed controls, status readback, RX termination override, and the beginning of signal-detect high-frequency threshold override fields.

## Control Flow And State Behavior

This file has no local control flow. Runtime behavior appears when AMDGPU display code uses these constants with register read/write helpers.

The field names imply several hardware state machines and handshakes:

- PLL bring-up and tuning use `MPLL_PWR_CTL_*` overrides, power/lock timers, reset/calibration controls, DAC outputs, spread-spectrum selection, and analog `CTR*` fields.
- Analog power and reference sequencing use bandgap and reference power-up timers plus status/override fields for BG, PMIX, VREG, and RTUNE.
- Link-lane activation uses per-lane TX/RX reset, enable, width, rate, PMA/PCS power-state, clock-ready, data-enable, DETRX, and loopback fields.
- Receiver clock recovery and adaptation use VCO calibration controls/status, CDR loop controls/status, DPLL frequency/bounds, adaptation configuration, DFE/CTLE/VGA/ATT status, DAC selection, and calibration compare clock controls.
- Diagnostics use LBERT controls/errors, RX statistic match/mask/control/counter registers, analog scope controls, ATB measurement selectors, and status readback fields.
- Self-clearing strobes are visible in fields such as RX DAC control enable, AFE update enable, IQ phase-adjust clock, RX termination clock, TX EQ clock, and VCO frequency tune clock; consumers must account for hardware-cleared bits and optional self-clear-disable fields.

No software persistence is implemented in this header. Hardware register contents persist only according to the ASIC reset and power domains. Fields named `RESERVED`, `STAT`, `STATUS`, `ACK`, `RESULT`, `COUNTER`, `SPARE`, `DAC`, and `*_CODE` may expose latches, counters, hardware readback, or programmable calibration values, but this chunk does not define policy for retaining or restoring them.

## Dependencies And Integration Points

The only syntactic dependency is the C preprocessor. These macros are intended to be included with generated DPCS 4.2.0 address headers and consumed by AMDGPU/DC register helper macros that combine a register offset, field shift, and field mask.

Integration points visible from the naming:

- AMDGPU DRM display code under `drivers/gpu/drm/amd`, especially DC/DPCS link encoder, PHY, clock, lane, and diagnostics code.
- DPCS 4.2.0 generated address headers that define the register offsets matching this shift/mask header.
- DisplayPort and HDMI PHY programming paths that set TX/RX lane width, rate, power state, terminations, equalization, PLL, and clock-recovery behavior.
- Link training and recovery paths that inspect RX CDR/VCO/adaptation status, lane acknowledgements, LBERT errors, and RX statistic counters.
- Suspend/resume and hotplug paths that reinitialize clocks, PLLs, analog power, lane P-states, and calibration values after power-domain transitions.
- Hardware validation and debug tools that use ATB, OCLA, LBERT, scope, statistic, CR-bank, and analog override fields.

## Risks

- Generated-header drift is the dominant risk. A wrong shift or mask can silently write adjacent analog or PHY control bits during read-modify-write operations.
- Many registers mix writable controls with readback/status bits. Examples include request/ack, enable/status, counter/result, calibration control/status, and interrupt-like statistic fields. Consumers need the hardware access semantics from the register database, not just these masks.
- The analog override families can bypass normal training or firmware-controlled behavior. Misusing `*_OVRD_*` fields can leave PLLs, RX front-end tuning, lane power states, or signal-detect thresholds in invalid states.
- Boundary slicing matters for reconciliation. `MPLLA_CTR3` is incomplete at the start of this chunk and `SIGDET_OVRD_OUT_1` is incomplete at the end, so per-file merge logic should combine adjacent chunks before checking per-register completeness.
- Repeated MPLLA/MPLLB and per-lane TX/RX field patterns are copy-generation sensitive. A single prefix, mask width, or shift error can affect only one PLL instance or one lane path and may not be caught by compile-only testing.
- Reserved masks are exposed beside active fields. Driver code should preserve reserved bits unless the hardware specification explicitly defines a value.
- Self-clearing strobe fields and self-clear-disable fields can produce timing-sensitive bugs if software assumes ordinary persistent bit storage.

## Test Signals

Useful validation signals are mostly build-time and hardware-integration oriented:

- Compile/preprocess AMDGPU display code that includes `dpcs_4_2_0_sh_mask.h`.
- Static generated-register checks that compare this header against the DPCS 4.2.0 register database.
- Macro-pair checks for matching `__SHIFT` and `_MASK` definitions, allowing the expected boundary imbalance for this sliced range: four masks-only entries from `MPLLA_CTR3` at the start and two shifts-only entries from `SIGDET_OVRD_OUT_1` at the end.
- Grep/compile checks for consumers of `DPCSSYS_CR1_SUPX_ANA_MPLLA`, `DPCSSYS_CR1_SUPX_ANA_MPLLB`, `DPCSSYS_CR1_SUPX_DIG_MPLL`, `DPCSSYS_CR1_LANEX_DIG_ASIC`, `DPCSSYS_CR1_LANEX_DIG_RX_ADPTCTL`, and `DPCSSYS_CR1_LANEX_DIG_ANA` macros.
- Runtime display tests on ASICs using DPCS 4.2.0: DP/HDMI link training, hotplug, suspend/resume, lane power-state transitions, PLL calibration/lock, RX VCO/CDR convergence, receiver adaptation convergence, and error-recovery paths.
- Diagnostic readback during bring-up for MPLL lock/status, RTUNE status, bandgap/reference power-up behavior, lane ACK/status fields, RX VCO calibration result, CDR status, DPLL bounds, adaptation status, LBERT errors, statistic counters, analog status, and self-clearing strobe behavior.

## Chunk Notes For Merge

This chunk is source-tree aligned and intentionally documents only lines 40593-42955 of `dpcs_4_2_0_sh_mask.h`. Adjacent chunks should supply the missing `MPLLA_CTR3` shifts before this range and the remaining `SIGDET_OVRD_OUT_1` definitions after this range. The later per-file merge should treat the whole file as a generated ASIC register bitfield map for AMD DPCS 4.2.0, not handwritten driver logic.
