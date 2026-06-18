# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 82681-85088

## Purpose

This chunk is a generated AMD DPCS 4.2.3 shift/mask header slice for display PHY/control registers. It contains no executable C code; it publishes preprocessor constants describing bit positions and masks inside DPCS control-register fields. The matching register-address constants live in `dpcs_4_2_3_offset.h`, and both generated headers are included by `display/dc/resource/dcn316/dcn316_resource.c` for DCN 3.1.6 display resource construction.

The requested range contains 2,171 `#define` lines: 1,158 `__SHIFT` definitions and 1,013 `_MASK` definitions. The imbalance is caused by line-based chunk boundaries. The range starts inside the lane 1 RX power-control section, immediately after the comment for `DPCSSYS_CR4_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0S`, and ends after the first two shift definitions for `DPCSSYS_CR4_LANE2_DIG_RX_ADPTCTL_ADPT_CFG_8`. It covers the remainder of lane 1 RX power, calibration, CDR/DPLL, adaptation, statistics, MPHY, digital/analog override, and analog TX/RX field definitions, then continues through the beginning of lane 2 ASIC/TX/RX field definitions.

Although the source path sits under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, memory allocations, callbacks, or runtime APIs in this chunk. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position of a register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate, preserve, or update that field in a DPCS register value.

Major register families in this range are:

- `DPCSSYS_CR4_LANE1_DIG_RX_PWRCTL_*`: lane 1 RX power-state templates for `P0S`, `P1`, and `P2`, plus RX power-up timing fields. These control analog AFE, clock regulator, analog clock, deserializer, CDR, VCO reset/calibration, continuous calibration, and digital clock enable bits for each power state.
- `DPCSSYS_CR4_LANE1_DIG_RX_VCOCAL_*`: lane 1 RX VCO calibration controls, timing, and status fields. The fields include calibration counters, hold/disable controls, override selection, frequency/calibration resets, continuous calibration enable, DPLL calibration update gain, frequency tune start/step controls, skip controls, startup/update/counter timing, FSM state, calibration-done/status, final counter value, and fast/correct/up status flags.
- `DPCSSYS_CR4_LANE1_DIG_RX_CDR_*` and `DPCSSYS_CR4_LANE1_DIG_RX_DPLL_*`: lane 1 RX CDR and DPLL fields for phase detector enables/edge/polarity, PR-mode enable, realign behavior, DPLL gain override, spread-spectrum counters/gains, live CDR gain status, DPLL frequency value, and upper/lower frequency bounds.
- `DPCSSYS_CR4_LANE1_DIG_RX_ADPTCTL_*`: lane 1 RX adaptation configuration and readback fields. These include ATT/VGA/CTLE/DFE enable masks, thresholds, adaptation step sizes, training pattern fields, reset bits, ATT/VGA/CTLE status, DFE tap status, even/odd data and error VDAC offsets, slicer controls, adaptation reset, DAC control selectors, and CR-bank address/data fields.
- `DPCSSYS_CR4_LANE1_DIG_RX_STAT_*`: lane 1 receive statistic and pattern-matching fields for load value, data masks, match controls, statistic controls, sample counts, statistic counters, comparator clock control, and statistic stop control.
- `DPCSSYS_CR4_LANE1_DIG_MPHY_*`: lane 1 MPHY low-speed/PWM support fields, including RX PWM control, low-speed termination control, and analog PWM clock stable-count fields.
- `DPCSSYS_CR4_LANE1_DIG_ANA_*`: lane 1 digital outputs into analog TX/RX controls and status. The fields cover TX override output, termination-code override, EQ override, RX control/power/VCO override, RX calibration/DAC/AFE/CTLE/scope/slicer/IQ controls, analog signal-change enable, status, RX termination-code override, MPHY override, signal-detect override, and TX DCC DAC override output fields.
- `DPCSSYS_CR4_LANE1_ANA_TX_*` and `DPCSSYS_CR4_LANE1_ANA_RX_*`: lane 1 direct analog TX/RX controls and diagnostics for TX measurement, power, alternate bus, ATB selection, DCC DAC/control, termination, clock override, miscellaneous TX settings, RX clocks, CDR/deserializer, slicer, power, squelch, calibration, ATB measurements, ATB force, and reserved analog fields.
- `DPCSSYS_CR4_LANE2_DIG_ASIC_*`: lane 2 ASIC-facing live and override fields for lane reset/power state, TX override inputs/outputs, RX override inputs, RX equalization override inputs, ASIC input/output status, RX CDR/VCO ASIC inputs, OCLA controls, and late TX/RX override groups.
- `DPCSSYS_CR4_LANE2_DIG_TX_PWRCTL_*`: lane 2 TX power-state templates, TX power-up timing, DCC CR-bank and DAC controls, TX clock alignment, and TX LBERT control fields.
- `DPCSSYS_CR4_LANE2_DIG_RX_PWRCTL_*`, `DPCSSYS_CR4_LANE2_DIG_RX_VCOCAL_*`, `DPCSSYS_CR4_LANE2_DIG_RX_CDR_*`, `DPCSSYS_CR4_LANE2_DIG_RX_DPLL_*`, and the start of `DPCSSYS_CR4_LANE2_DIG_RX_ADPTCTL_*`: lane 2 RX power, VCO calibration, CDR, DPLL, and initial adaptation configuration fields. The chunk ends before `ADPT_CFG_8` is complete.

## Control Flow

This header has no runtime control flow. Runtime behavior comes from AMDGPU display code that includes the header and passes these constants into register-helper tables:

1. `dcn316_resource.c` includes `dpcs/dpcs_4_2_3_offset.h` and this matching `dpcs/dpcs_4_2_3_sh_mask.h`.
2. DCN/DPCS register-list macros token-paste generated register and field names into offset, shift, and mask table initializers.
3. Display Core resource construction wires those tables into link-encoder, PHY, and related display objects.
4. Runtime paths use AMD display register helpers to read, write, update, poll, or decode DPCS fields through the generated offsets, shifts, and masks.

The macros do not encode programming order. Consumers must still sequence lane reset release, TX/RX power-state changes, analog clock and regulator enables, deserializer/CDR/VCO/DPLL programming, DCC and VCO calibration, RX adaptation, statistic sampling, loopback/LBERT diagnostics, and suspend/resume restoration according to hardware rules.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes hardware-backed state in CR4 lane 1 and lane 2 DPCS registers:

- RX power and timing state: AFE, analog clock regulator, analog clock, deserializer, CDR, VCO reset/calibration, continuous calibration, digital clock, and power-up timing controls.
- Clock recovery and calibration state: VCO calibration control/status, DPLL frequency and bounds, CDR phase detector settings, spread-spectrum compensation counters, gain overrides, and calibration-done/readback flags.
- RX adaptation state: ATT/VGA/CTLE/DFE enable masks, thresholds, adaptation gains, reset controls, tap status, DAC selector fields, slicer controls, VDAC offsets, CR-bank access, and adaptation status done flags.
- Statistics and diagnostics: RX pattern/match/statistic counters, calibration comparator clocking, statistic stop control, LBERT mode/sync/error count, OCLA, ATB measurement selectors, analog status, and signal-detect override fields.
- TX and analog state: lane 1 analog TX/RX controls and lane 2 TX power/DCC/clock/LBERT fields, including override values that can bypass normal ASIC-driven PHY control.

Persistence is hardware-defined. Programmed control fields generally remain until link reprogramming, PHY reset, lane power-down, power gating, suspend/resume, GPU reset, or ASIC reset rewrites them. Status, acknowledgement, calibration, statistic, and error fields may be read-only, sticky, self-clearing, write-one-to-clear, or valid only while the relevant DPCS clock and power domains are active. This generated header does not encode those access semantics.

## Dependencies And Integration Points

This chunk must stay synchronized with AMD's generated DPCS 4.2.3 register database and especially with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h`, which provides matching `ixDPCSSYS_*` register addresses. The companion offsets place lane 1 groups in the `0x1141` through later `0x11xx` range for the start of this chunk, and lane 2 groups around `0x1200` through `0x1268` for the portion that ends at `ADPT_CFG_8`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which directly includes both DPCS 4.2.3 generated headers.
- The AMD Display Core register-helper layer, which expects consistent register, shift, and mask names when building register tables and performing read-modify-write operations.
- Neighboring generated DPCS revisions such as `dpcs_4_2_0_*`, `dpcs_4_2_2_*`, and older `dpcs_3_1_4_*`, which are useful comparison points when validating field drift across ASIC generations.

The main behavioral integration is display-link PHY handling: DisplayPort/USB-C style lane bring-up, lane power management, link training, TX/RX calibration, clock recovery, RX equalization/adaptation, loopback or LBERT diagnostics, hardware debug, and low-level PHY characterization.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while writing the wrong DPCS bit, corrupting adjacent PHY state, or returning misleading status.
- The file is generated metadata. Manual edits can diverge from AMD's authoritative register database, the matching offset header, firmware assumptions, and silicon documentation.
- The chunk boundary is artificial. It starts after the `LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0S` comment and omits the prior `P0` group; it ends after only `DFE1_MU` and `DFE2_MU` shifts for `LANE2_DIG_RX_ADPTCTL_ADPT_CFG_8`, leaving the rest of that register's shifts and all masks to the next chunk.
- Lane 1 and lane 2 register families are highly repetitive but not safe to collapse blindly. Lane-specific offsets, status naming, reserved fields, and incomplete boundary groups can make mechanical copy assumptions wrong.
- PHY power, CDR, VCO, DPLL, DCC, and RX adaptation fields are sequencing-sensitive. Incorrect masks can cause link-training failures, calibration timeouts, unstable high-rate links, marginal RX equalization, or failures that only appear after low-power transitions.
- Override-enable and analog debug fields can bypass normal hardware/firmware control. Writing the wrong override, test-bus, signal-detect, OCLA, or MPHY field can leave a lane in a debug state or mask real PHY status.
- Reserved fields are exposed as masks. Consumer code should avoid writing non-reset values to reserved bits unless a validated hardware sequence requires it.
- Status, statistic, and error fields may have side effects or limited validity windows. Treating read-only, sticky, self-clearing, or write-one-to-clear fields as ordinary read/write fields can lose diagnostics or create stuck polling loops.

## Test Signals

Useful validation combines generated-header consistency checks with hardware/link behavior:

- Build AMDGPU display support for DCN 3.1.6. Include, token-paste, or symbol regressions should surface where `dcn316_resource.c` and register helper tables consume `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`.
- Mechanically verify that complete register groups in lines 82681-85088 have matching `__SHIFT` and `_MASK` definitions, while allowing the known boundary exceptions at `LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0S` and `LANE2_DIG_RX_ADPTCTL_ADPT_CFG_8`.
- Cross-check each register group in this slice against `dpcs_4_2_3_offset.h`, including lane 1 offsets beginning at `ixDPCSSYS_CR4_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0S` (`0x1141`) and lane 2 adaptation offset `ixDPCSSYS_CR4_LANE2_DIG_RX_ADPTCTL_ADPT_CFG_8` (`0x1268`).
- Diff this slice against AMD's generated DPCS 4.2.3 source and adjacent DPCS revisions where CR4 lane layouts are expected to be compatible.
- On hardware using this DPCS revision, exercise hotplug, modeset, DisplayPort link training, link-rate and lane-count changes, high-rate/marginal links, USB-C/DP alternate-mode paths, suspend/resume, low-power state entry/exit, and GPU reset.
- Inspect register dumps or debugfs-style diagnostics around RX power states, VCO/CDR/DPLL convergence, adaptation status, DFE tap readbacks, statistic counters, analog status, LBERT/OCLA controls, and TX DCC state before and after power transitions.
- Watch kernel logs and display diagnostics for link-training failures, blank displays after resume, calibration timeouts, stuck done/ack polling, unexpected retraining, unstable signal-detect behavior, or failures isolated to a CR4-backed lane or encoder.

## Cross-Chunk Notes

This document intentionally covers only lines 82681-85088 of `dpcs_4_2_3_sh_mask.h`. The previous chunk owns the lane 1 RX `P0` group and the comment immediately preceding the first `P0S` field in this chunk. This chunk then covers the rest of lane 1 RX/digital/analog field definitions and the beginning of lane 2 through a partial `DPCSSYS_CR4_LANE2_DIG_RX_ADPTCTL_ADPT_CFG_8` group. The next chunk must complete `ADPT_CFG_8`, continue lane 2 adaptation/status/analog groups, and should be merged before making whole-file claims about complete CR4 lane coverage.
