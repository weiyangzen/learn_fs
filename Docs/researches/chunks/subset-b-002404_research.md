# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 43783-46183

## Purpose

This chunk is a generated AMD DPCS 4.2.3 shift/mask header slice for the `DPCSSYS_CR2` display PHY/register block. It contains no executable C logic. Its exported surface is preprocessor metadata that tells AMDGPU display register helpers where each hardware register field starts (`__SHIFT`) and which bits it occupies (`_MASK`).

The requested range covers 2,401 source lines with 2,173 `#define` statements, 1,117 shift macros, 1,056 mask macros, and 228 register comment markers. It starts in the middle of `DPCSSYS_CR2_SUP_DIG_ANA_MPLLB_OVRD_OUT_0`, continues through CR2 supervisor analog/RTUNE/bandgap/PMIX definitions, covers CR2 lane 0 digital ASIC override/mirror, TX power/DCC, RX statistic, digital-to-analog TX override/status, and analog TX definitions, then covers a large part of CR2 lane 1 digital ASIC, TX/RX power, RX VCO/CDR/DPLL/adaptation/statistic/MPHY, and digital analog TX override fields. The final line begins `DPCSSYS_CR2_LANE1_DIG_ANA_TX_TERM_CODE_OVRD_OUT`; its remaining definitions continue after this chunk.

Although this path is under a local `ceph-client` source mirror, the file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocations, locks, includes, callbacks, or direct MMIO accesses in this range. The interface is a generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK`: mask value for extracting, composing, or updating that field in a register word.

The important register-field families in this chunk are:

- CR2 supervisor analog and PLL output controls: `DPCSSYS_CR2_SUP_DIG_ANA_MPLLB_OVRD_OUT_0/1/2` provides MPLLB clock enable, HDMI/divided/fb clock, output enable, reset, calibration, standby, override-select, analog integral, and charge-pump proportional/integral field locations. The chunk starts at the masks for `_OUT_0`; its shifts are immediately before the requested range.
- CR2 supervisor calibration and analog status: `DPCSSYS_CR2_SUP_DIG_ANA_RTUNE_OVRD_OUT`, `DPCSSYS_CR2_SUP_DIG_ANA_STAT`, and `DPCSSYS_CR2_SUP_DIG_ANA_BG_OVRD_OUT` describe RTUNE reset/mode/enable/value/override, analog comparator and reference clock-detect status, bandgap enable/start/reset, reference regulator fast-start, reference selection, and override-enable bits.
- CR2 MPLL phase-mixer controls: `DPCSSYS_CR2_SUP_DIG_ANA_MPLLA_PMIX_OVRD_OUT` and `DPCSSYS_CR2_SUP_DIG_ANA_MPLLB_PMIX_OVRD_OUT` define phase-mixer select, enable, and override-enable fields for both MPLLs.
- CR2 lane 0 ASIC digital override/mirror fields: `DPCSSYS_CR2_LANE0_DIG_ASIC_*` defines lane loopback, TX request/pstate/rate/width/MPLLB/data-enable/main/pre/post cursor/HDMI/clock-ready/detect-RX/invert/LPD/DC-coupling/FIFO/MPHY, TX output ACK/status, RX output data-enable/detect/pstate/rate/width/ack/status, and non-override ASIC input/output mirrors.
- CR2 lane 0 TX power, DCC, clock alignment, and LBERT controls: `DPCSSYS_CR2_LANE0_DIG_TX_PWRCTL_*`, `DPCSSYS_CR2_LANE0_DIG_TX_CLK_ALIGN_TX_CTL_0`, and `DPCSSYS_CR2_LANE0_DIG_TX_LBERT_CTL` define TX pstate behavior for P0/P0s/P1/P2, request/data-enable/reset/rx-detect behavior, power-up timing windows, DCC CR-bank and DAC address/data/control/range/select/ACK fields, clock-alignment controls, and loopback/BERT test controls.
- CR2 lane 0 RX statistic and pattern-match controls: `DPCSSYS_CR2_LANE0_DIG_RX_STAT_*` defines sample load/start, data masks, CR1A/CR1B pattern match and masks, correlation/statistic source and shift selection, statistic counter enables, pause/clock/data-delay/valid-loss controls, sample and statistic counters, calibration-comparator clock settings, extended pattern match words, statistic stop, and disable-sample-count behavior.
- CR2 lane 0 digital analog TX and raw analog TX fields: `DPCSSYS_CR2_LANE0_DIG_ANA_TX_*`, `DPCSSYS_CR2_LANE0_DIG_ANA_STATUS_0`, `DPCSSYS_CR2_LANE0_ANA_TX_*` describe digital-to-analog TX clocks, data enable, reference generator, reset, serial enable, data rate, divider and RX-detect controls, TX termination-code override, TX EQ leg/pre/post/main fields, DCC DAC override, analog status bits such as PLL lock and receive-detect, raw analog TX measurement, power override, alternate bus, ATB, DCC DAC/control, termination code/control, override clock, miscellaneous driver/vreg/slew/peaking controls, and reserved fields.
- CR2 lane 1 ASIC digital override/mirror fields: `DPCSSYS_CR2_LANE1_DIG_ASIC_*` repeats the lane/TX surface and adds broader RX-side override/input coverage in this range, including RX request/data-enable/reset/pstate/rate/width, loopback, adaptation controls, squelch thresholds/response, CDR/VCO, DFE/CTLE/VGA/ATT, PH2 calibration, ATE, RX EQ controls, RX CDR/VCO ASIC input mirrors, OCLA selection, and TX/RX output/status mirrors.
- CR2 lane 1 TX power, DCC, clock alignment, and LBERT controls: `DPCSSYS_CR2_LANE1_DIG_TX_PWRCTL_*`, `TX_CLK_ALIGN_TX_CTL_0`, and `TX_LBERT_CTL` mirror the lane 0 TX pstate, timing, DCC, alignment, and BERT controls for lane 1.
- CR2 lane 1 RX power, calibration, CDR/DPLL, adaptation, statistics, and MPHY controls: `DPCSSYS_CR2_LANE1_DIG_RX_PWRCTL_*`, `RX_VCOCAL_*`, `RX_CDR_*`, `RX_DPLL_*`, `RX_ADPTCTL_*`, `RX_STAT_*`, and `DIG_MPHY_RX_*` define RX pstate behavior, power-up timing, VCO calibration control/status/timing, XAUI alignment mask, RX LBERT control/error, CDR control/status, DPLL frequency/bounds, RX adaptation configuration/status for ATT/VGA/CTLE/DFE/slicer/VDAC offsets, adaptation reset, DAC control muxes, CR-bank access, statistic counters/matchers, MPHY PWM polarity, low-speed termination, and analog PWM clock-stability count.
- CR2 lane 1 digital analog TX lead-in: `DPCSSYS_CR2_LANE1_DIG_ANA_TX_OVRD_OUT` defines TX analog clock/data/reference/reset/serial/rate/divider/RX-detect/override fields, and the chunk begins `DPCSSYS_CR2_LANE1_DIG_ANA_TX_TERM_CODE_OVRD_OUT` with its first shift definitions.

Most masks are 16-bit `L`-suffixed constants. The names encode hardware semantics such as `REQ`, `ACK`, `PSTATE`, `RATE`, `WIDTH`, `OVRD_EN`, `STATUS`, `DONE`, `CAL`, `DCC`, `DFE`, `CTLE`, `VGA`, `ATT`, `SLICER`, `LBERT`, `ATB`, and `RESERVED`, but this header only defines field location.

## Control Flow

This header has no runtime control flow. It contributes compile-time constants to the AMDGPU display stack:

1. The companion `dpcs_4_2_3_offset.h` header supplies register indexes such as `ixDPCSSYS_CR2_SUP_DIG_ANA_MPLLB_OVRD_OUT_0`, `ixDPCSSYS_CR2_LANE0_DIG_ASIC_LANE_OVRD_IN`, and `ixDPCSSYS_CR2_LANE1_DIG_ANA_TX_TERM_CODE_OVRD_OUT`.
2. This shift/mask header supplies field layout constants for those register names.
3. DCN 3.1.6 display resource code includes both generated DPCS 4.2.3 headers from `dcn316_resource.c`.
4. Display Core register tables and token-pasting helper macros combine offsets, shifts, and masks.
5. Runtime link, PHY, encoder, and diagnostics code performs the real read/modify/write, polling, decode, clear, and sequencing operations through AMD register helper paths.

Actual control decisions are outside this file: asserting or releasing TX/RX resets, changing pstate/rate/width, selecting MPLL paths, enabling clocks and data, starting VCO or DCC calibration, programming TX EQ/termination, running RX adaptation, clearing or masking status, collecting RX statistics, and using LBERT/OCLA/ATE/debug overrides.

## State And Persistence Behavior

This chunk stores no software state and persists nothing itself. It names hardware-visible state in CR2 supervisor and lane registers:

- Supervisor MPLLB/RTUNE/bandgap/PMIX state includes clock/output enables, reset/calibration/standby controls, charge-pump tuning fields, RTUNE mode/value/override, reference-clock detection, analog comparator status, bandgap start/reset/reference selection, and MPLLA/MPLLB phase-mixer selection.
- Lane 0 and lane 1 ASIC override state includes forced loopback, request, pstate, rate, width, reset, clock-ready, detect-RX, data-enable, TX cursor/EQ, HDMI mode, async driver, MPHY, RX adaptation, squelch, CDR/VCO, DFE/CTLE/VGA/ATT, PH2 calibration, ATE, OCLA, and the corresponding override-enable bits.
- Lane 0 and lane 1 TX state includes pstate programming, request/data-enable/reset behavior, power-up timers, DCC CR-bank/DAC controls, TX clock alignment, LBERT controls, digital analog TX override outputs, TX termination and equalization settings, analog TX measurement/power/ATB/DCC/termination/clock/miscellaneous fields, and analog TX status.
- Lane 1 RX state includes RX pstate programming, power-up timers, VCO calibration controls and status, CDR controls/status, DPLL frequency and bounds, RX adaptation configuration/status, slicer/VDAC offsets, statistic pattern matching/counters, MPHY PWM and low-speed termination controls, and LBERT error state.

Persistence is hardware-defined rather than described by these macros. Configuration fields usually remain until link reprogramming, modeset, suspend/resume, GPU reset, ASIC reset, power-gating, firmware ownership changes, or explicit driver reinitialization modifies them. Status, ACK, calibration, statistic, LBERT, and handshake fields may be read-only, transient, latched, write-one-to-clear, self-clearing, sampled under a specific clock domain, or invalid while PHY power is gated. This generated header does not encode access type, reset values, legal values, volatility, or sequencing rules.

## Dependencies And Integration Points

This file must stay synchronized with AMD's DPCS 4.2.3 register database and the matching offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h` defines matching `ix...` register offsets. Examples visible for this chunk include `ixDPCSSYS_CR2_SUP_DIG_ANA_MPLLB_OVRD_OUT_0` at `0x008f`, `ixDPCSSYS_CR2_LANE0_DIG_ASIC_LANE_OVRD_IN` at `0x1000`, and `ixDPCSSYS_CR2_LANE1_DIG_ANA_TX_TERM_CODE_OVRD_OUT` at `0x11a1`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` includes `dpcs/dpcs_4_2_3_offset.h` and `dpcs/dpcs_4_2_3_sh_mask.h` when building DCN 3.1.6 display resources.
- AMDGPU Display Core register-list, link encoder, PHY, power-management, lane-training, calibration, diagnostics, and debug paths consume these macros indirectly through generated register tables and register helper macros.
- The generated names are an ABI-like source contract for token-pasted users. Case, spelling, lane number, PLL letter, and suffixes such as `__SHIFT`, `_MASK`, `OVRD_IN`, `OVRD_OUT`, `ASIC_IN`, `ASIC_OUT`, `PSTATE`, `STAT`, and `CTL` must remain exactly aligned with generated consumers.

Behaviorally, this range sits below user-facing display modeset and link code. It provides bit locations for DisplayPort/HDMI PHY operations such as MPLL output control, RTUNE and bandgap calibration, TX/RX pstate transitions, lane request/ack handshakes, DCC calibration, TX equalization and termination, RX VCO/CDR/DPLL/adaptation, statistic collection, MPHY controls, and diagnostic LBERT/OCLA/ATE override paths.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong mask or shift can compile cleanly while updating the wrong hardware field, corrupting reserved bits, or decoding status incorrectly.
- The file is generated metadata. Manual edits can diverge from AMD's register source, companion offset headers, firmware assumptions, and silicon documentation.
- The requested range starts inside `DPCSSYS_CR2_SUP_DIG_ANA_MPLLB_OVRD_OUT_0`; its shift definitions and register marker are before line 43783, while this chunk contains only its mask tail. Whole-register analysis must reconcile the previous chunk.
- The requested range ends inside `DPCSSYS_CR2_LANE1_DIG_ANA_TX_TERM_CODE_OVRD_OUT`; later shift/mask definitions for that register continue after line 46183.
- CR2 lane 0 and lane 1 definitions are repetitive but not identical. Lane 1 includes substantial RX power/calibration/adaptation coverage in this chunk while lane 0 coverage here focuses on TX and RX-statistic/digital-analog TX surfaces. Copying assumptions between lanes can hide real layout differences.
- Override-value and override-enable fields are easy to confuse. Enabling a stale override, or setting an override value without its enable bit, can force clocks, resets, requests, data-enable, pstate/rate/width, loopback, analog controls, or calibration state away from hardware/firmware ownership.
- Request/ACK, done, status, statistic, and error fields are sequencing-sensitive. A wrong field definition can produce false readiness, stuck polling, missed events, stale statistics, link-training timeouts, or diagnostic false positives.
- PLL, RTUNE, bandgap, DCC, TX EQ/termination, RX VCO/CDR/DPLL/adaptation, squelch, slicer, DFE/CTLE/VGA/ATT, MPHY, and analog power fields are silicon- and board-sensitive. Errors may appear only at specific link rates, connectors, cables, sinks, voltage/temperature corners, suspend/resume paths, or hotplug sequences.
- Reserved masks are emitted throughout the range. Generic register writes must preserve reserved bits unless an authoritative programming guide requires a specific value.
- LBERT, OCLA, ATE, ATB, analog measurement, and forced override paths are diagnostic/test surfaces. Misuse can bypass normal PHY state machines or make debug data misleading.
- Because generated macros are consumed through token pasting, renames or spelling normalization can break builds even when the underlying value is unchanged.

## Test Signals

Useful validation should combine generated-header consistency checks with display hardware testing:

- Build AMDGPU display support for DCN 3.1.6 with `dcn316_resource.c`, `dpcs_4_2_3_offset.h`, and `dpcs_4_2_3_sh_mask.h`. Missing, renamed, or malformed macros should surface in generated register-table compilation.
- Mechanically verify that complete field groups in this range have paired `__SHIFT` and `_MASK` definitions, allowing the known split-register exceptions at `DPCSSYS_CR2_SUP_DIG_ANA_MPLLB_OVRD_OUT_0` and `DPCSSYS_CR2_LANE1_DIG_ANA_TX_TERM_CODE_OVRD_OUT`.
- Cross-check each complete register marker in this chunk against `dpcs_4_2_3_offset.h` and AMD's authoritative register database.
- Diff repeated CR2 lane 0/lane 1 TX, DCC, statistic, digital analog, and ASIC override groups against each other and against adjacent DPCS versions where the hardware specification expects matching layouts.
- Exercise DisplayPort and HDMI link bring-up, link-rate changes, hotplug, modeset, blank/unblank, suspend/resume, GPU reset, and power-gating paths on hardware using DPCS 4.2.3/DCN 3.1.6.
- Watch register dumps and driver traces for stuck TX/RX request or ACK bits, failed pstate transitions, unexpected data-enable/reset/clock overrides, MPLL lock or output-clock issues, RTUNE/bandgap anomalies, DCC calibration problems, RX VCO/CDR/DPLL/adaptation failures, and unstable RX statistics.
- Run available diagnostic paths for LBERT, RX statistic pattern matching/counters, OCLA/UPCS observation, ATE overrides, ATB/analog measurement, DCC on-demand, and VCO/adaptation calibration. Expected signals are counters and done/status bits that decode consistently with hardware documentation and reference tools.
- Use known-good register dumps to verify decode of MPLLB clock/output fields, TX pstate timers, DCC DAC fields, TX EQ/termination fields, RX adaptation status fields, VCO/CDR/DPLL fields, MPHY controls, and analog TX override/status fields.

## Cross-Chunk Notes

The previous chunk owns the start of `DPCSSYS_CR2_SUP_DIG_ANA_MPLLB_OVRD_OUT_0`, including the register marker and all shift definitions for that register. This chunk starts at its mask definitions, then owns the subsequent CR2 supervisor analog/PMIX definitions and the CR2 lane 0/lane 1 register families described above.

The next chunk should complete `DPCSSYS_CR2_LANE1_DIG_ANA_TX_TERM_CODE_OVRD_OUT` and continue the remaining lane 1 digital analog, analog TX/RX, and later CR2 lane definitions. The final per-file report should reconcile these artificial line boundaries before making whole-file claims about DPCS 4.2.3 CR2 coverage.
