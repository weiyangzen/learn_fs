# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 47686-50047

## Purpose

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice for low-level display PHY lane registers. It contains preprocessor constants only; there is no executable C logic, no types, no storage, and no direct MMIO access in this range.

The line window covers 2,138 `#define` entries: 1,071 `__SHIFT` constants and 1,067 `_MASK` constants. It starts inside the lane 1 RX VCO calibration status area, covers the rest of the visible lane 1 digital RX, analog override, analog TX, and analog RX register-field metadata, then begins the lane 2 register-field metadata through the first masks of `DPCSSYS_CR2_LANE2_DIG_RX_ADPTCTL_ADPT_CFG_6`. The boundaries are artificial chunk boundaries: the previous chunk owns the beginning of lane 1 RX VCO calibration definitions, and the next chunk owns the remaining lane 2 adaptation masks and later lane 2 fields.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display-controller metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, locks, allocations, or includes in this range. The public contract is the generated register-field macro naming pattern:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position of a hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field inside the register.

Major register families covered in this chunk:

- `DPCSSYS_CR2_LANE1_DIG_RX_VCOCAL_*`: lane 1 RX VCO calibration status and control fields visible at the chunk start, including RX VCO FSM state, frequency/calibration resets, continuous calibration enable, calibration done, DPLL frequency reset, final VCO counter, too-fast/correct/up status, and related reserved ranges.
- `DPCSSYS_CR2_LANE1_DIG_RX_RX_ALIGN_XAUI_COMM_MASK` and `...LBERT_*`: receive alignment comma masking plus link BERT mode, sync, error count, and overflow status.
- `DPCSSYS_CR2_LANE1_DIG_RX_CDR_*`: lane 1 clock-data-recovery controls for phase detector enable/edge/polarity, PR mode, realign behavior, diagnostic bus selection, spread-spectrum on/off counters, DPLL gain override, phase/frequency update gains, CDR status, DPLL frequency, and upper/lower frequency bounds.
- `DPCSSYS_CR2_LANE1_DIG_RX_ADPTCTL_*`: lane 1 receiver adaptation configuration and status. This includes adaptation timing, start, clock division, CTLE pole override, TGG patterns, CTLE/VGA/ATT/DFE/eye/TGG enables, thresholds, adaptation step sizes, saturation thresholds, initial error levels, reset bits, ATT/VGA/CTLE/DFE status fields, DFE VDAC offsets, slicer controls, error slicer levels, DAC control mux selection, and CR-bank address/data access.
- `DPCSSYS_CR2_LANE1_DIG_RX_STAT_*`: lane 1 receive statistics and match/counter controls, including load values, data masks, match values, counter enable/invert/clear/edge/continuous mode fields, sample count, six statistic counters, calibration compare clock control, additional match controls, stat control extensions, and stop control.
- `DPCSSYS_CR2_LANE1_DIG_MPHY_RX_*`: MPHY receive PWM control, low-speed termination control, and analog PWM clock stable-count fields.
- `DPCSSYS_CR2_LANE1_DIG_ANA_*`: digital-side analog override outputs for TX, RX, VCO, calibration, DAC, AFE, slicer, IQ phase/sense, signal-change enables, analog status, MPHY overrides, signal-detect overrides, DCC DAC overrides, TX override measurement, TX power, alternate/test bus controls, TX DCC/termination/misc/reserved registers, RX clock/CDR/slicer/power/squelch/calibration/test-bus/reserved registers.
- `DPCSSYS_CR2_LANE2_DIG_ASIC_*`: start of lane 2 digital ASIC-facing lane/TX/RX override input/output and normal ASIC input/output fields, including RX equalization and CDR/VCO ASIC inputs, OCLA, and extra TX/RX override outputs.
- `DPCSSYS_CR2_LANE2_DIG_TX_PWRCTL_*`: lane 2 TX power-state programming, P0/P0S/P1/P2 state fields, TX power-up timers, DCC CR-bank address/data, DCC DAC control/range/selection/ack/address fields.
- `DPCSSYS_CR2_LANE2_DIG_TX_CLK_ALIGN_TX_CTL_0` and `...TX_LBERT_CTL`: lane 2 TX clock alignment and TX-side BERT mode/sync controls.
- `DPCSSYS_CR2_LANE2_DIG_RX_PWRCTL_*`: lane 2 RX power-state fields and RX power-up timing controls.
- `DPCSSYS_CR2_LANE2_DIG_RX_VCOCAL_*`: lane 2 RX VCO calibration control, timing, and status fields, mirroring the lane 1 VCO calibration layout.
- `DPCSSYS_CR2_LANE2_DIG_RX_*` through `ADPTCTL_ADPT_CFG_6`: beginning of lane 2 receive alignment, LBERT, CDR, DPLL, and receiver adaptation config fields. The chunk stops after the `CTLE_MU` and `VGA_MU` masks for `ADPT_CFG_6`, so the complete register belongs partly to the next chunk.

## Control Flow

This header has no runtime control flow. Its role is compile-time register metadata:

1. `dcn31_resource.c` includes `dpcs_4_2_0_offset.h` and this matching `dpcs_4_2_0_sh_mask.h` for DCN 3.1 display resource construction.
2. Resource and link-encoder tables use macro expansion, for example `DPCS_DCN31_REG_LIST`, `DPCS_DCN31_MASK_SH_LIST(__SHIFT)`, and `DPCS_DCN31_MASK_SH_LIST(_MASK)`, to pair generated offsets with generated field positions and masks.
3. Runtime display code uses the resulting register tables through helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, and related AMD display register helpers.
4. Hardware sequencing for VCO calibration, TX/RX power-state changes, CDR tuning, receiver adaptation, DFE/CTLE/VGA programming, statistics capture, and analog override access is implemented by driver or firmware code outside this generated header.

The constants in this chunk therefore enable control flow elsewhere but do not encode ordering, timing, read/write permissions, write-one-to-clear behavior, polling loops, or power/clock dependencies themselves.

## State And Persistence Behavior

The file stores no software state and persists nothing. It names bitfields for hardware-visible state in CR2 lane registers:

- Lane 1 and lane 2 RX VCO calibration state, including FSM state, reset controls, calibration completion, VCO counter results, and too-fast/correct/up indications.
- CDR and DPLL configuration/status, including phase-detector behavior, spread-spectrum counters, update gains, DPLL frequency values, and frequency bounds.
- Receiver adaptation state for CTLE, VGA, attenuator, DFE taps, eye-height/eye-horizontal controls, TGG patterns, thresholds, step sizes, saturation behavior, reset controls, and live adaptation status/readback.
- RX statistics state for match masks/values, counter control, sample counts, statistic counters, and stop/clock controls.
- Analog lane override state for TX and RX power, equalization, termination, DAC, VCO, slicer, IQ, squelch, calibration, test bus, DCC, and signal-detect controls.
- Lane 2 TX/RX power-state programming and power-up timing state.

Actual persistence and side effects are hardware-defined. Some fields are configuration bits that remain until reset, power gating, suspend/resume, modeset reprogramming, or firmware intervention. Status and counter fields may be read-only, latched, self-clearing, write-one-to-clear, or meaningful only when the corresponding DPCS lane, PHY clocks, and power domains are active. This generated slice does not describe those access semantics.

## Dependencies And Integration Points

This chunk must stay synchronized with the AMD DPCS 4.2.0 register database and companion generated offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h` provides the matching register addresses/base indices for the field names in this header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` includes the 4.2.0 DPCS offset and shift/mask headers and builds DCN 3.1 link-encoder and DPCS register tables from them.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.h` and related link-encoder code show the integration style for RDPCSTX/DPCS register arrays and shift/mask table population, even though this specific slice is CR2 lane-level metadata rather than the common RDPCSTX control fields.
- AMD display register helpers in `reg_helper.h` consume the shift/mask values indirectly through generated tables; a wrong mask can compile successfully but route MMIO updates to the wrong bit range.
- Neighboring chunks for the same file are required for whole-register and whole-lane interpretation. This chunk starts after part of lane 1 VCO calibration was already defined and ends before all lane 2 `ADPT_CFG_6` masks are present.

Behaviorally, these fields sit below connector/link policy code. They describe per-lane PHY calibration, receiver adaptation, analog test/override, power-state, and diagnostic controls that influence display link bring-up, training, signal integrity, power transitions, and debug capture.

## Risks And Edge Cases

- These constants are untyped preprocessor macros. A wrong shift or mask can build cleanly and only fail as a runtime hardware programming bug.
- The header is generated. Manual edits risk divergence from silicon register definitions, the matching offset header, firmware assumptions, and debug tooling.
- Chunk boundaries split semantic registers. `DPCSSYS_CR2_LANE1_DIG_RX_VCOCAL_RX_VCO_STAT_1` begins before this chunk, and `DPCSSYS_CR2_LANE2_DIG_RX_ADPTCTL_ADPT_CFG_6` continues after it; per-file synthesis must reconcile adjacent chunks before asserting complete register coverage.
- Lane repetition is copy-sensitive. Lane 1 and lane 2 definitions should be structurally aligned where the hardware lanes are symmetric; a generator drift can create port-, lane-, or link-width-specific failures.
- VCO, CDR, DPLL, and adaptation fields are sequencing-sensitive. Incorrect masks can cause calibration-done polling failures, unstable clock recovery, bad equalization, link-training failures, or marginal behavior that depends on rate, cable, sink, voltage, and temperature.
- Analog override and test-bus fields are dangerous if treated as ordinary controls. They can bypass normal firmware/hardware behavior, alter termination/equalization/power, or expose debug buses whose semantics may differ by stepping.
- Counter and status fields can have non-obvious clear/latch behavior. Using the correct bit location is necessary but not sufficient; runtime code must still follow hardware access rules outside this header.
- Reserved fields are present throughout the range. Software should not infer that reserved masks are safe to program just because they are generated.
- The file uses `L`-suffixed 16-bit-style masks inside 32-bit C constants. Consumers must preserve unsigned-width expectations used by AMD's register helpers.

## Test Signals

Useful validation is mostly generated-header consistency plus runtime display PHY behavior:

- Build AMDGPU display support for the DCN 3.1 configuration that includes `dcn31_resource.c`. Missing or renamed macros should surface as compile failures in the generated register table setup.
- Mechanically compare this line range against the authoritative DPCS 4.2.0 register-field database and confirm each complete field has the expected `__SHIFT`/`_MASK` pair, allowing for the known split at the chunk start and end.
- Cross-check all registers represented here against `dpcs_4_2_0_offset.h`, especially CR2 lane 1 and lane 2 offsets for VCOCAL, CDR, ADPTCTL, STAT, MPHY, ANA, ASIC, TX_PWRCTL, and RX_PWRCTL blocks.
- Run repetition checks between lane 1 and lane 2 for mirrored register families. Expected intentional differences should be limited to lane numbering and chunk-boundary incompleteness.
- Exercise DisplayPort and HDMI/PHY link bring-up across lane counts and link rates. Watch for calibration timeouts, CDR instability, link-training retries, lane-specific failures, and intermittent high-rate signal-integrity problems.
- Test power transitions, suspend/resume, hotplug link retraining, and modesets while monitoring TX/RX power-state and calibration status behavior.
- Use hardware register dumps or debug tooling to verify DPCS CR2 lane fields after link training and after power-state changes, comparing against firmware/hardware reference values.
- Exercise diagnostics that read RX statistics or use analog/test-bus controls only on supported platforms, checking for counter aliasing, stuck counters, and incorrect match masks.

## Cross-Chunk Notes

The previous chunk owns the beginning of lane 1 RX VCO calibration definitions, including fields immediately before `DPCSSYS_CR2_LANE1_DIG_RX_VCOCAL_RX_VCO_STAT_1`. This chunk then covers the rest of lane 1 receive, adaptation, statistics, and analog override metadata and starts lane 2 from ASIC override and TX/RX power/calibration metadata. The next chunk must finish `DPCSSYS_CR2_LANE2_DIG_RX_ADPTCTL_ADPT_CFG_6` and continue lane 2 adaptation/status definitions before a final per-file report can make whole-lane or whole-file claims.
