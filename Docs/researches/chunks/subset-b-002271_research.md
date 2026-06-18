# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 29266-31717

## Purpose

This chunk is a generated AMD DPCS 3.1.4 shift/mask header slice for `DPCSSYS_CR1` PHY control-register fields. It contains preprocessor constants that describe bit positions and masks for a large run of 16-bit CR registers covering:

- the tail of RAW always-on lane 2 receiver/transceiver controls;
- the complete RAW always-on lane 3 receiver adaptation, DFE, slicer, MPLL, signal-detect, DCC, firmware, and transceiver-mode field set;
- the generic `RAWAONLANEX` version of the same lane field layout at the lane-X address window;
- the CR1 supervisor (`SUPX`) PLL, reference-clock, bandgap, rtune, analog override/status, and power-timer controls;
- the beginning of the `LANEX` ASIC-lane and transmit power-control register layout, ending at `TX_PWRCTL_TX_PWRUP_TIME_0`.

The header has no executable logic. Its purpose is to let DCN 3.1.4 display/link encoder code build register field tables and perform CR/MMIO read-modify-write operations with stable generated names instead of open-coded bit constants. Although this repository path is under `ceph-client`, the file is AMDGPU display hardware metadata, not distributed filesystem code.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, globals, locks, allocations, callbacks, or inline helpers in this range. The exported API is entirely macro based:

- `DPCSSYS_CR1_*__*__SHIFT` gives the bit offset for a hardware field.
- `DPCSSYS_CR1_*__*_MASK` gives the mask for preserving, extracting, clearing, or updating that field.

The main register families in this chunk are:

- `DPCSSYS_CR1_RAWAONLANE2_DIG_*`: finishes the lane 2 `LANE_XCVR_MODE_OVRD_IN`, `LANE_XCVR_MODE_IN`, and `RX_SIGDET_CONFIG` definitions. The first line is a continuation from the previous chunk, so the complete `LANE_XCVR_MODE_OVRD_IN` field set must be reconciled across chunk boundaries.
- `DPCSSYS_CR1_RAWAONLANE3_DIG_*`: per-lane receiver/PHY metadata for lane 3. Fields include RX adaptation values (`IQ`, `ATT`, `VGA`, `CTLE`, `DFE_TAP1` through `DFE_TAP5`), DFE offset/reference-level registers, phase adjust registers, slicer controls, common calibration status, adaptation control words `ADPT_CTL_0` through `ADPT_CTL_7`, MPLL disable/control fields, fast-mode flags, TX/RX override inputs, loss-of-signal and signal-detect controls, statistics/status bits, RX override outputs, RX signal-detect calibration/code registers, VREF/calibration-code registers, RX DCC calibration code banks, TX DCC bank address/data/control fields, MPLL bandgap controls, firmware adaptation/calibration words, lane transceiver mode override/input fields, and RX signal-detect filter counters.
- `DPCSSYS_CR1_RAWAONLANEX_DIG_*`: the same RAW always-on lane pattern generalized to a lane-X window. The field names mirror the lane 3 fields and are paired with a separate address window in `dpcs_3_1_4_offset.h`, allowing code or diagnostics to address the generic lane instance instead of a fixed lane number.
- `DPCSSYS_CR1_SUPX_DIG_*` and `DPCSSYS_CR1_SUPX_ANA_*`: supervisor-level PLL/reference/analog controls. These define ID-code fields, reference-clock override, MPLLA/MPLLB divided and HDMI clock override/input fields, MPLLA/MPLLB override words, SSC peak/step-size fields, charge-pump override/status fields, prescaler, support-level override/status, ASIC input mirrors, bandgap input/status/override, analog prescaler/rtune/bandgap controls, MPLL power-control override/status/timer/calibration/DAC fields, SSC spread type, clock/reset power-up timers, reference VPHUD timing, rtune configuration/status/set-value/stat fields, TX calibration code, and analog override/status outputs.
- `DPCSSYS_CR1_LANEX_DIG_*`: lane-X ASIC-facing lane/TX/RX override and status fields plus the start of TX power-control p-state timing. This chunk includes lane override input, TX override inputs 0-5, TX override outputs, RX override inputs/outputs and EQ/CDR/ASIC input mirrors, OCLA enable bits, and TX p-state controls for `P0`, `P0S`, `P1`, and `P2`.

Most masks in this slice are 16-bit values using the generated `0x....L` convention. Several logical values span split fields across adjacent registers, such as MPLL SSC peak/step-size words, MPLL fractional-N values, VCM hold timers, VBOOST disable timers, and pstate/timer fields. Some register comments intentionally have no following field macros in this chunk, for example reserved or empty generated placeholders such as `DIG_TX_DCC_CONFIG` and `FW_MM_CONFIG`.

## Control Flow

This chunk has no runtime control flow. It participates in driver control paths indirectly:

1. DCN 3.1.4 resource code includes `dpcs_3_1_4_offset.h` and this shift/mask header.
2. Register-list macros and field-list macros token-paste generated register names with `_BASE_IDX`, address, `__SHIFT`, and `_MASK` suffixes.
3. Link encoder and HPO DP link encoder objects receive register offsets and field masks through static tables in `dcn314_resource.c`.
4. Runtime display/link code uses those tables through register helper paths to program DP/HDMI PHY state, PLL state, lane p-states, lane overrides, training-related controls, and status reads.

The generated constants do not encode sequencing. Consumers still need to follow PHY bring-up, link training, clock/PLL programming, and suspend/resume ordering: select PLL/reference clocks, wait for lock/stable indications, program per-lane rates and widths, manage p-states, apply overrides only when safe, and clear or restore diagnostic/firmware control bits after use.

## State And Persistence Behavior

The header itself stores no state and persists nothing. The underlying registers represent live PHY and analog state:

- RAWAON lane fields hold receiver adaptation results, calibration codes, signal-detect thresholds, transceiver mode bits, DFE and slicer settings, and lane-local override/status state.
- `FAST_FLAGS` and `FAST_FLAGS_2` fields can alter or skip calibration/adaptation waits. If enabled in live hardware, they persist until reset or driver/firmware reprogramming and can shorten training at the cost of relying on previous calibration state.
- Supervisor fields persist PLL, reference-clock, bandgap, prescaler, rtune, SSC, charge-pump, timer, DAC, and analog override state while the DPCS block remains powered.
- LANEX override and p-state fields persist transmit/receive lane override state and p-state enable/reset/data/clock/serial settings. These are hardware control bits, not software cache variables.
- Status-like fields such as common-calibration done, rtune status, ASIC input mirrors, analog status, and override output mirrors are observations of hardware state. This header does not identify read-only, write-one-to-clear, sticky, self-clearing, or firmware-owned semantics.

The driver must treat these masks as an ABI to the ASIC register database. Reset values, access permissions, side effects, and power-domain persistence are defined by the hardware spec and driver sequencing, not by this header.

## Dependencies And Integration Points

The immediate companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h`, which defines the matching CR register addresses. In the corresponding offset range, lane 3 registers occupy `0x4300` through `0x4351`, generic `RAWAONLANEX` registers occupy `0x7000` through `0x7051`, supervisor registers start at `0x8000`, and LANEX ASIC/TX power-control registers start at `0x9000`.

The exact DPCS 3.1.4 headers are included directly by `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`. That file uses:

- `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)` to populate `struct dcn10_link_enc_shift` and `struct dcn10_link_enc_mask` tables.
- `DCN3_1_RDPCSTX_REG_LIST(...)` to populate HPO DP link encoder register tables.
- register helper infrastructure from `reg_helper.h` to map generated register metadata into runtime register access.

The specific macros in this chunk are lower-level DPCS CR field definitions than the public link encoder tables usually expose. They can still be consumed by indirect CR address/data paths, diagnostics, bring-up scripts, firmware flows, or future link encoder changes that need detailed PHY calibration, analog, or override fields. The repeated lane 3 and lane-X layouts are an important consistency contract with the offset header and with adjacent generated DPCS versions such as 4.2.x.

## Risks And Edge Cases

- A wrong shift or mask compiles cleanly but can program the wrong PHY bits, leading to link-training failures, unstable high-bit-rate links, lost signal detect, bad PLL lock behavior, or intermittent display/audio link faults.
- This chunk starts mid-register for `DPCSSYS_CR1_RAWAONLANE2_DIG_LANE_XCVR_MODE_OVRD_IN`; completeness checks for that register require the previous chunk.
- This chunk ends at `DPCSSYS_CR1_LANEX_DIG_TX_PWRCTL_TX_PWRUP_TIME_0`; the rest of the TX power-up timing and later LANEX power-control fields are in the next chunk.
- Many fields are hardware or firmware override enables paired with override values. Setting an override-enable bit without a valid value, or leaving overrides asserted after diagnostic use, can block normal firmware/hardware control.
- Reserved masks are present throughout. Whole-register writes that do not preserve reserved bits risk toggling undocumented behavior or diverging from firmware-owned state.
- Split fields require coordinated programming across multiple registers. Examples include SSC peak/step-size, MPLL timers, VCM hold timing, VBOOST disable timing, and multi-bank DCC/calibration values.
- Calibration skip/fast flags can reduce required waits only under valid preconditions. Misuse may make problems appear data-rate, temperature, or resume dependent.
- Status fields and output mirror fields are not necessarily writable. Treating them as ordinary RMW targets can be harmless on one ASIC revision and harmful on another.
- Generated DPCS 3.1.4 naming overlaps with generated DCN 4.1.0 and DPCS 4.2.x headers. Consumers must include the ASIC-matched offset and mask headers together; mixing versions can silently produce valid C with wrong hardware layout.

## Test Signals

Useful validation signals for this chunk include:

- Build AMDGPU Display Core with DCN 3.1.4 enabled. Missing or renamed macros should surface where `dcn314_resource.c` initializes link encoder and HPO DP link encoder register/field tables.
- Mechanically compare each complete register in this chunk against `dpcs_3_1_4_offset.h` and the generated AMD register database. Every non-placeholder field should have a matching `__SHIFT` and `_MASK` pair.
- Cross-check lane 3 and `RAWAONLANEX` field layouts for parity where the hardware intends the generic lane window to mirror fixed lane registers.
- Exercise DP and HDMI link bring-up on DCN 3.1.4 hardware across lane counts, link rates, voltage swing/pre-emphasis levels, hotplug cycles, and suspend/resume.
- Stress PHY power transitions and p-state changes, especially `P0`, `P0S`, `P1`, `P2`, clock/data/serial enable bits, reset bits, RX-detect allowance, and VBOOST/DCC calibration behavior.
- Use debug or hardware-trace paths to read PLL lock/stable status, signal-detect status, rtune status, calibration-done status, and lane statistics after link training and resume.
- Compare register dumps before and after link training or suspend/resume to ensure override bits, reserved bits, and fast-calibration flags are restored or preserved as expected.

## Cross-Chunk Notes

This slice contains 2,452 lines, 316 register-comment markers, and 2,136 `#define` lines. It is the middle of a much larger generated DPCS 3.1.4 mask header, so final per-file research should reconcile:

- the preceding chunk for the start of lane 2 `LANE_XCVR_MODE_OVRD_IN`;
- this chunk for full lane 3, lane-X, supervisor, and early LANEX TX power-control coverage;
- the following chunk for the remainder of LANEX TX power-up timing, DCC, clock-align, LBERT, RX power-control, and later fields.
