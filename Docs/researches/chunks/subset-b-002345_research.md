# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 19118-21534

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice. It contains no executable C logic; it publishes preprocessor constants for bit positions (`__SHIFT`) and masks (`_MASK`) used to access fields in DPCS indirect hardware registers.

The requested range contains 2,101 `#define` entries across 316 register comment groups. It starts at `DPCSSYS_CR0_RAWAONLANE2_DIG_LANE_CMNCAL_RCAL_STATUS`, continues through the tail of raw always-on lane 2 controls, complete raw always-on lane 3 controls, the raw always-on lane-X template controls, and a large CR0 supervisor (`SUPX`) digital/analog/MPLL section. It ends inside `DPCSSYS_CR0_SUPX_DIG_CLK_RST_REF_PWRUP_TIME_0`: only the first mask for that register is in this chunk, with the remaining masks in the next chunk.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, memory allocations, callbacks, or direct MMIO operations in this range. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for the hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate, compose, or update the field.

The main macro families in this chunk are:

- `DPCSSYS_CR0_RAWAONLANE2_DIG_*`: tail of raw always-on lane 2, covering common RCAL status, TX/RX disable overrides, RX loss-of-signal mask timing, RX signal-detect filtering, RX status, RX PMA/squelch/VREF/termination/signal-detect overrides, signal-detect calibration codes, VREF enable, current/VREF calibration codes, RX DCC calibration code banks, TX DCC bank address/data/continuous enable, MPLL bandgap control, signal-detect output override/input, firmware memory/adaptation/calibration configuration, lane transceiver-mode override/input, RX signal-detect configuration, and TX DCC configuration.
- `DPCSSYS_CR0_RAWAONLANE3_DIG_*`: complete repeated raw always-on lane 3 register map for RX adaptation offsets, DFE reference/data/error/bypass values, RX IQ and FOM readback, MPLLA/MPLLB coarse tune, power-up done state, adaptation status, fast calibration flags, DFE taps, slicer controls, common MPLL/RCAL status, adaptation control words, MPLL disable, TX/RX disable overrides, LOS/signal-detect controls, RX PMA override outputs, calibration code registers, DCC banks, firmware config, lane mode, signal-detect, and TX DCC config.
- `DPCSSYS_CR0_RAWAONLANEX_DIG_*`: lane-X template version of the same raw always-on lane controls. This is used as a generic lane pattern rather than a fixed physical lane number and mirrors the lane 3 fields for adaptation, DFE, calibration, overrides, signal-detect, firmware config, and DCC setup.
- `DPCSSYS_CR0_SUPX_DIG_*`: supervisor digital fields for ID code, reference-clock override, MPLLA/MPLLB divider and HDMI clock overrides, PLL override inputs, SSC peak/stepsize words, fractional PLL words, charge-pump overrides, supervisor/prescaler/level overrides, debug, ASIC-provided PLL and supervisor inputs, bandgap inputs, charge-pump ASIC inputs, MPLL power-control state, PLL timers, calibration override, analog DAC readback, SSC spread type, and the start of clock/reset power-up timing.
- `DPCSSYS_CR0_SUPX_ANA_*`: supervisor analog fields for prescaler control, RTUNE control, bandgap controls, switch power measurement, MPLLA/MPLLB analog miscellaneous controls, overrides, analog test bus selectors, PLL control words, and reserved analog words.

Most masks are 16-bit-style values with an `L` suffix, matching the DPCS indirect register-field convention. The companion offset header maps representative groups in this chunk to offsets such as `0x422e` for `RAWAONLANE2_DIG_LANE_CMNCAL_RCAL_STATUS`, `0x4300` for lane 3 raw always-on fields, `0x7000` for the lane-X template, `0x8000` for supervisor ID code, and `0x807b` for `CLK_RST_REF_PWRUP_TIME_0`.

## Control Flow

This header has no runtime control flow. It participates in compile-time register-table construction:

1. DCN 3.1.5 resource code includes `dpcs_4_2_2_offset.h` and this shift/mask header.
2. Generated register-list, shift-list, and mask-list initializers token-paste register and field names into AMD Display Core resource tables.
3. Runtime display code uses register helpers to read, write, get, set, or update individual fields through the matching offsets and these shift/mask constants.
4. Actual sequencing for lane power, RX adaptation, signal-detect calibration, DCC/RTUNE calibration, MPLL programming, reference-clock setup, PLL power control, bandgap bring-up, and supervisor analog controls lives in AMDGPU display code, firmware, and hardware state machines outside this header.

The macros only describe bit layout. They do not encode reset values, access width beyond the mask shape, read-only/write-only status, write-one-to-clear behavior, self-clearing behavior, polling order, clock-domain restrictions, or power-domain validity.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR0 raw always-on lane and supervisor DPCS registers:

- Lane 2 tail state includes common RCAL init/done status, TX/RX disable override state, RX LOS mask count, signal-detect filter settings, RX PMA status, PMA override values/enables, signal-detect calibration thresholds and codes, VREF/current calibration code latches, RX DCC calibration code banks, TX DCC bank address/data/continuous enable, MPLL bandgap control, firmware config bits, lane transceiver mode, and signal-detect/DCC configuration.
- Lane 3 and lane-X state includes RX adaptation values for ATT/VGA/CTLE/DFE, DFE even/odd reference and data/error/bypass offsets, slicer controls, adaptation done flags, fast calibration/adaptation flags, continuous calibration flags, common MPLL/RCAL status, coarse-tune values, RX IQ phase and FOM readback, PMA RX override outputs, signal-detect status/override, and DCC/calibration code registers.
- Supervisor digital state includes ID-code readback, reference-clock and divider/HDMI clock overrides, MPLLA/MPLLB enable/divider/VCO/fractional/SSC/standby/calibration/clock-sync controls, charge-pump and gain-scheduled charge-pump controls, supervisor override inputs/outputs, prescaler and level overrides, ASIC-driven PLL/supervisor inputs, bandgap inputs, MPLL power-control FSM status, PLL lock status, PCLK/output/feedback clock enables, timer values, calibration override, analog DAC output readback, SSC spread type, and clock/reset power-up timing.
- Supervisor analog state includes prescaler enable/divider/output controls, RTUNE comparator and manual tuning controls, bandgap calibration and power measurement controls, MPLLA/MPLLB analog overrides, ATB/test-bus selectors, loop-filter/capacitor/current/DAC/VCO-related PLL controls, and reserved analog latches.

Persistence is hardware-defined. Programmed control and override fields generally remain until modeset/link reprogramming, PHY power gating, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization rewrites them. Status, calibration, statistic, ACK, and lock fields may be latched, sampled, self-clearing, read-only, or only valid while the relevant lane/common clock and power domains are active. This generated header does not define those semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.2 register database and its companion address map:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies matching `ixDPCSSYS_*` offsets for the register groups whose fields are defined here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` directly includes both `dpcs_4_2_2_offset.h` and `dpcs_4_2_2_sh_mask.h`, tying this generated contract to DCN 3.1.5 resource construction.
- The AMD Display Core register-helper layer consumes the generated offset, shift, and mask tables to access hardware without open-coding bit positions.
- Firmware and hardware state machines share these fields with the driver for RX adaptation, signal detection, DCC and RTUNE calibration, PLL power sequencing, reference-clock control, bandgap bring-up, and debug or manufacturing override paths.

Behaviorally, this range sits below the user-facing display stack. DisplayPort/HDMI link bring-up, PHY clock programming, lane calibration, hotplug/modeset, suspend/resume, diagnostics, and manufacturing/ATE flows can depend on these bitfield definitions being exactly correct.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong hardware bit, corrupting a reserved field, or decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the companion offset header, firmware assumptions, and silicon documentation.
- The range is repetitive across lane 2, lane 3, and lane-X. A generator or merge error can affect only one lane/template while nearby fields look correct.
- Many registers pair override value bits with override enable bits. Leaving enable bits asserted after debug or validation use can bypass normal PHY, supervisor, or PLL state-machine control.
- PLL, SSC, fractional divider, charge-pump, bandgap, prescaler, and clock/reset timing fields are timing-sensitive and electrically significant. Bad masks can produce clock instability, lock failures, black screens, rate-specific retraining loops, or compliance regressions.
- RX adaptation, DFE, slicer, signal-detect, DCC, VREF, and RTUNE fields are calibration-sensitive. Incorrect bit definitions can cause subtle link-training failures, degraded margins, misleading debug readbacks, or stuck polling loops.
- Status and control fields with similar names repeat across override, ASIC input, supervisor output, and power-control blocks. Consumers must pair each mask with the correct offset block and access semantics.
- Chunk boundaries are artificial. This chunk starts cleanly at `RAWAONLANE2_DIG_LANE_CMNCAL_RCAL_STATUS`, but it ends mid-register at `DPCSSYS_CR0_SUPX_DIG_CLK_RST_REF_PWRUP_TIME_0`; the `FAST_REF_WAIT` and reserved masks are outside this slice.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build AMDGPU display support for DCN 3.1.5. Missing, renamed, or malformed macros should fail where `dcn315_resource.c` and generated register tables consume DPCS 4.2.2 symbols.
- Mechanically verify that complete register groups in this range have matching `__SHIFT` and `_MASK` definitions, allowing the known end-boundary exception for `DPCSSYS_CR0_SUPX_DIG_CLK_RST_REF_PWRUP_TIME_0`.
- Cross-check every complete register group in this chunk against `dpcs_4_2_2_offset.h`, especially the transitions from raw always-on lane 2 to lane 3, lane-X, and supervisor offsets.
- Diff against AMD's generated source register database and adjacent DPCS versions such as 4.2.0 or 4.2.3 where compatible hardware layout is expected.
- Exercise DP and HDMI link bring-up across lane counts, link rates, power states, and hotplug/modeset paths. Expected signals are stable link training, successful RX adaptation, correct signal-detect behavior, PLL lock, and no unexpected lane or supervisor timeout.
- Exercise suspend/resume, GPU reset, low-power entry/exit, and display disable/enable paths to catch stale override, bandgap, reference-clock, PLL, DCC, RTUNE, or calibration state.
- Use register dumps or PHY debug traces during failures to confirm DFE/adaptation values, RX IQ/FOM readbacks, RCAL status, DCC code banks, signal-detect output, MPLL power-control FSM status, PLL lock, SSC/fractional PLL values, charge-pump fields, bandgap controls, and clock/reset timing decode correctly.
- Where supported, run debug/manufacturing paths for ATB, analog test bus, signal-detect override, DCC bank access, manual RTUNE, prescaler override, and PLL override controls, then confirm normal link training resumes after overrides are released.

## Cross-Chunk Notes

The previous chunk covers earlier raw always-on lane 2 fields and ends immediately before the `RAWAONLANE2_DIG_LANE_CMNCAL_RCAL_STATUS` group. This chunk completes the lane 2 tail, covers lane 3, lane-X, and a broad CR0 supervisor digital/analog/MPLL section. The next chunk should finish `DPCSSYS_CR0_SUPX_DIG_CLK_RST_REF_PWRUP_TIME_0` masks and continue supervisor clock/reset and RTUNE configuration fields. The final per-file report should reconcile these boundaries before making whole-file claims about all DPCS 4.2.2 register groups.
