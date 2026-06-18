# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 21535-23895

## Scope

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for `DPCSSYS_CR0` supervisor and lane-X display PHY register fields. It contains no executable C logic; its exported surface is a set of preprocessor constants describing bit positions (`__SHIFT`) and bit masks (`_MASK`) for 16-bit DPCS indirect hardware registers.

The requested range contains 2,361 lines, 2,139 `#define` entries, 1,080 shift definitions, 1,070 mask definitions, and 222 register comment headings. The line range starts inside `DPCSSYS_CR0_SUPX_DIG_CLK_RST_REF_PWRUP_TIME_0`, where only the final two masks are in this chunk, and ends inside `DPCSSYS_CR0_LANEX_ANA_RX_ATB_MEAS1`, where only the `master_atb_en` shift appears before the next chunk.

Although this repository path is under a local `ceph-client` mirror, the file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The header lets AMD display driver code refer to DPCS 4.2.2 register fields symbolically instead of hard-coding bit positions. Consumer code pairs these macros with addresses from `dpcs_4_2_2_offset.h` and the AMD DC register helper layer to compose, isolate, or update hardware register fields during link bring-up, link training, PHY power management, debug, and diagnostics.

This chunk covers the end of CR0 supervisor reference-clock power timing, supervisor RTUNE and analog/MPLL override fields, lane-X ASIC override/input/output transfer fields, lane TX and RX power/control/calibration/statistic fields, digital-to-analog override outputs, and the beginning of raw analog TX/RX register fields.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The important interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask used to isolate or update that field.

Major macro families in this chunk include:

- `DPCSSYS_CR0_SUPX_DIG_CLK_RST_REF_*`: supervisor reference-clock and reference-regulator timing/control fields, including `FAST_REF_WAIT` and `SUP_ANA_VPHUD_*`.
- `DPCSSYS_CR0_SUPX_DIG_RTUNE_*`: common RTUNE debug, enable, status, RX/TXDN/TXUP set values and readbacks, timing counters, and TX calibration code fields.
- `DPCSSYS_CR0_SUPX_DIG_ANA_MPLLA_*`, `DPCSSYS_CR0_SUPX_DIG_ANA_MPLLB_*`, `DPCSSYS_CR0_SUPX_DIG_ANA_RTUNE_OVRD_OUT`, `DPCSSYS_CR0_SUPX_DIG_ANA_BG_OVRD_OUT`, and `DPCSSYS_CR0_SUPX_DIG_ANA_*PMIX_OVRD_OUT`: supervisor analog override/status fields for MPLLA/MPLLB clocks, outputs, charge-pump values, RTUNE, bandgap/reference regulation, async reset, and PMIX controls.
- `DPCSSYS_CR0_LANEX_DIG_ASIC_*`: lane-X ASIC-side override inputs/outputs and normal ASIC input/output mirrors for lane, TX, RX, RX EQ, and RX CDR/VCO signals. These fields describe request, pstate, rate, width, MPLL select, data enable, loopback, polarity, EQ coefficients, adaptation controls, signal-detect, calibration, and acknowledgement/status paths.
- `DPCSSYS_CR0_LANEX_DIG_TX_PWRCTL_*` and `DPCSSYS_CR0_LANEX_DIG_RX_PWRCTL_*`: lane TX/RX power-state encodings and power-up timing fields for P0, P0S, P1, P2, DCC, and RX power-up flows.
- `DPCSSYS_CR0_LANEX_DIG_TX_PWRCTL_DCC_*` and `DPCSSYS_CR0_LANEX_DIG_TX_CLK_ALIGN_*`: TX DCC CR-bank, DAC control/range/selection/ack/address, and TX clock alignment controls.
- `DPCSSYS_CR0_LANEX_DIG_TX_LBERT_*` and `DPCSSYS_CR0_LANEX_DIG_RX_LBERT_*`: TX/RX low-level BERT test controls and RX BERT error reporting.
- `DPCSSYS_CR0_LANEX_DIG_RX_VCOCAL_*`, `DPCSSYS_CR0_LANEX_DIG_RX_CDR_*`, and `DPCSSYS_CR0_LANEX_DIG_RX_DPLL_*`: RX VCO calibration controls/timers/status, CDR controls/status, DPLL frequency, and DPLL frequency bounds.
- `DPCSSYS_CR0_LANEX_DIG_RX_ADPTCTL_*`: RX adaptation configuration, reset/status, DFE tap statuses, even/odd VDAC offsets, slicer controls, error levels, DAC control selection, and CR-bank address/data access.
- `DPCSSYS_CR0_LANEX_DIG_RX_STAT_*`: RX statistic loading, masks, match controls, statistic source controls, sample counts, statistic counters, calibration-comparison clock control, extended match controls, and statistic stop controls.
- `DPCSSYS_CR0_LANEX_DIG_MPHY_RX_*`: MPHY RX PWM, low-speed termination, and analog PWM clock-stable counter fields.
- `DPCSSYS_CR0_LANEX_DIG_ANA_*`: digital override outputs and status fields bridging lane digital control into analog TX/RX, including TX power/clock/reset/data, TX termination and EQ, RX control/power/VCO/calibration/DAC/slicer/scope, signal-detect, term-code clocks, MPHY, and DCC DAC override fields.
- `DPCSSYS_CR0_LANEX_ANA_TX_*` and `DPCSSYS_CR0_LANEX_ANA_RX_*`: raw analog TX/RX fields for measurement override, TX power, alternate/test bus, ATB controls, DCC DAC/control, termination, override clocks, TX miscellaneous controls, RX clocks, CDR/deserializer, slicer, RX power, squelch, calibration, and ATB/reference measurement controls.

## Control Flow

This header has no software control flow. It participates in compile-time construction of register/shift/mask tables:

1. AMD DCN 3.1.5 resource code includes `dpcs_4_2_2_offset.h` and `dpcs_4_2_2_sh_mask.h`.
2. Driver table macros token-paste register and field names from the offset and shift/mask headers into version-specific hardware access tables.
3. Runtime display code uses AMD DC register helpers to read, write, update, or decode the underlying DPCS registers.
4. Actual sequencing for RTUNE, MPLL overrides, TX/RX power transitions, DCC calibration, VCO/CDR setup, RX adaptation, RX statistics, LBERT, analog overrides, and test-bus control lives outside this generated header and inside the display driver, firmware, or hardware state machines.

The macros only encode bit layout. They do not encode access type, reset values, polling order, write-one-to-clear behavior, self-clearing behavior, clock-domain validity, power-domain constraints, or reserved-bit policy.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR0 DPCS supervisor and lane-X registers:

- Supervisor/common state includes RTUNE debug/manual values, RTUNE enable/status, RX/TX termination calibration set values and readbacks, RTUNE timing counters, TX calibration code, MPLLA/MPLLB output enable/reset/calibration/standby/clock-select override values, RTUNE analog override, bandgap/reference-regulator controls, analog status, async reset, and PMIX controls.
- Lane ASIC transfer state includes override values and enables for lane TX/RX requests, pstate, rate, width, MPLL selection, data enable, loopback, async drive, polarity, TX pre/main/post cursor values, RX adaptation requests, RX EQ controls, signal-detect thresholds, RX VCO/reference loads, phase calibration, termination, and lane outputs/acknowledgements.
- TX state includes lane P-state bitfields, TX power-up timings, DCC CR-bank address/data, DCC DAC programming, DAC ACK/address fields, TX clock alignment, and TX LBERT test controls.
- RX state includes RX P-state and power-up timing, VCO calibration control/timer/status, XAUI alignment mask, RX LBERT control/error status, CDR control/status, DPLL frequency/bounds, adaptation configuration/status, DFE tap readbacks, slicer and error offsets, adaptation reset, RX statistic capture controls and counters, and MPHY low-speed controls.
- Digital analog override state includes TX/RX analog enable, clock, reset, power, termination, EQ, VCO, DAC, calibration, slicer, signal-detect, MPHY, DCC, and status/readback fields.
- Raw analog state includes TX/RX power and clock override latches, measurement/test-bus selections, ATB selectors, DCC/termination controls, TX slew/peaking/vreg/inversion controls, RX CDR/deserializer/slicer/AFE/DFE/deserializer/loopback/fast-start/squelch/calibration/reference controls, and the first RX ATB measurement bit at the chunk boundary.

Persistence is hardware-defined. Configuration fields usually remain until link reprogramming, modeset, PHY power gating, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization rewrites them. Status, ACK, calibration, statistic, BERT, and handshake fields may be sampled, latched, self-clearing, clear-on-write, or valid only while relevant DPCS clocks and power domains are active. This generated header does not define those runtime semantics.

## Dependencies And Integration Points

The syntactic dependency is the C preprocessor. The semantic dependency is AMD's DPCS 4.2.2 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies matching `ixDPCSSYS_*` offsets. Example anchors for this chunk include `ixDPCSSYS_CR0_SUPX_DIG_RTUNE_CONFIG` at `0x8081`, `ixDPCSSYS_CR0_LANEX_DIG_TX_PWRCTL_TX_PSTATE_P0` at `0x9020`, `ixDPCSSYS_CR0_LANEX_DIG_RX_ADPTCTL_ADPT_CFG_0` at `0x9060`, and `ixDPCSSYS_CR0_LANEX_ANA_RX_ATB_MEAS1` at `0x90fa`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes both `dpcs/dpcs_4_2_2_offset.h` and `dpcs/dpcs_4_2_2_sh_mask.h`, tying this register contract to DCN 3.1.5 display resource setup.
- Higher-level display integration points include link encoder and PHY programming, DisplayPort/HDMI link training, lane power-state transitions, PLL/MPLL control, RX adaptation and CDR/VCO calibration, DCC and RTUNE calibration, hotplug/modeset/suspend/resume flows, manufacturing ATE/LBERT paths, OCLA/statistic/debug readback, and low-level interrupt or status polling paths that decode these fields through generated tables.

## Risks And Edge Cases

- These are untyped preprocessor constants. An incorrect mask or shift can compile cleanly while updating the wrong hardware field, corrupting reserved bits, or decoding a status bit incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, firmware expectations, silicon documentation, and the companion offset header.
- The range starts and ends inside logical registers. `DPCSSYS_CR0_SUPX_DIG_CLK_RST_REF_PWRUP_TIME_0` has its heading, shifts, and first mask before this chunk; `DPCSSYS_CR0_LANEX_ANA_RX_ATB_MEAS1` continues in the next chunk. Merge/reconciliation must not treat either register as fully documented by this chunk alone.
- Many fields pair an override value with an override-enable bit. Writing the value without enabling it may do nothing; leaving an enable asserted after test/debug use can force hardware away from normal state-machine control.
- Supervisor RTUNE, MPLLA/MPLLB, bandgap/reference, and PMIX fields can affect clocks, termination, and analog supplies. Bad masks here can cause PLL instability, black screens, link training failures, or power-management regressions.
- TX/RX power, request, reset, pstate, rate, width, MPLL-select, data-enable, and ACK fields are sequencing-sensitive. Misprogramming them can leave a lane stuck in reset, powered down, unclocked, or out of sync with the display controller.
- RX adaptation, DFE, slicer, CDR, VCO, DPLL, statistic, and calibration fields are easy to misread because status, configuration, reset, and CR-bank access fields are densely packed and similarly named.
- DCC, termination-code, TX EQ, peaking, slew, vreg, and analog test-bus fields affect electrical behavior. Wrong values may produce mode-specific failures or compliance problems rather than immediate software faults.
- BERT, ATE, OCLA, ATB, and raw analog override fields are intended for validation/debug/manufacturing-style flows. Using them in normal paths can perturb link training and power management.
- Reserved and `NC` masks cover large bit ranges. Consumers should preserve these bits through read-modify-write operations unless the hardware specification says otherwise.

## Test Signals

Useful validation is mainly generated-header, build, and hardware-integration oriented:

- Build AMDGPU display support for DCN 3.1.5 so `dcn315_resource.c` preprocesses the DPCS 4.2.2 offset and mask headers. Missing or renamed macros should fail during table initialization.
- Mechanically verify each complete register group in this range has matching `__SHIFT` and `_MASK` pairs, allowing the known boundary exceptions at `DPCSSYS_CR0_SUPX_DIG_CLK_RST_REF_PWRUP_TIME_0` and `DPCSSYS_CR0_LANEX_ANA_RX_ATB_MEAS1`.
- Cross-check register-family names in this chunk against `dpcs_4_2_2_offset.h` so every complete group has a matching `ixDPCSSYS_CR0_*` address.
- Diff against AMD's generated source data and nearby DPCS versions such as `dpcs_4_2_0_sh_mask.h` where compatible layouts are expected, watching for accidental field-width, shift, or mask drift.
- Runtime display tests on DPCS 4.2.2 hardware should cover DP/HDMI link bring-up, lane-count/rate changes, pstate transitions, hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset.
- Link-training and PHY debug traces should show expected transitions for RTUNE calibration, MPLLA/MPLLB enable/lock-related control, TX/RX request and ACK fields, DCC calibration, RX VCO/CDR/DPLL state, RX adaptation done/status fields, signal-detect, and statistic counters.
- Diagnostic validation should exercise LBERT, OCLA/statistic capture, ATB/test-bus selection, analog override readbacks, DCC DAC controls, termination-code controls, and RX/TX loopback or ATE paths where available.

## Chunk Notes For Merge

This document intentionally covers only lines 21535-23895 of `dpcs_4_2_2_sh_mask.h`. The previous chunk owns most of `DPCSSYS_CR0_SUPX_DIG_CLK_RST_REF_PWRUP_TIME_0`; this chunk begins with its final two masks. The next chunk owns the rest of `DPCSSYS_CR0_LANEX_ANA_RX_ATB_MEAS1` and subsequent raw analog/raw lane register groups. The final per-file report should describe the whole file as generated ASIC bitfield metadata for DPCS 4.2.2, with `dcn315_resource.c` and `dpcs_4_2_2_offset.h` as primary in-tree integration anchors.
