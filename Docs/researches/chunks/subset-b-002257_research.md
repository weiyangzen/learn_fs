# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h lines 2406-4791

## Purpose

This chunk is a generated AMD DisplayPort PHY/PCS register-offset section for the DPCS 3.1.4 block used by DCN 3.1.4 display hardware. It contains C preprocessor constants only: every entry maps an `ixDPCSSYS_*` symbolic register name to an indirect register index. The values are not MMIO byte offsets by themselves; they are the indexed addresses consumed by the AMD display register-access helpers for DPCS/DPCSSYS control, status, calibration, and debug registers.

The range starts mid-way through the `CR1` lane 1 register map at `ixDPCSSYS_CR1_LANE1_DIG_RX_STAT_SMPL_CNT1` (`0x1186`), covers the rest of `CR1` lane 1, complete or near-complete `CR1` lane 2/3 and raw lane/common definitions, then starts the `CR2` address block (`dpcssys_cr2_rdpcstxcrind`) and covers `CR2` common, lanes 0-2, and the first part of lane 3 through `ixDPCSSYS_CR2_LANE3_DIG_RX_STAT_STAT_CNT_0` (`0x1387`). The next chunk continues lane 3 RX statistics and later registers.

## Contents and Important Definitions

The chunk contains 2,382 `#define` entries. Major groups are:

- `CR1_LANE1` tail: RX statistic counters and match/stat controls (`0x1186-0x1197`), digital analog override outputs (`0x11a0-0x11c4`), TX analog override and measurement controls (`0x11e0-0x11ef`), and RX analog clock/CDR/power/calibration/ATB measurement controls (`0x11f0-0x11fc`).
- `CR1_LANE2`: a full lane map from ASIC override/input/output registers (`0x1200-0x121f`) through TX power/DCC/clock/LBERT registers, RX power/VCO/CDR/DPLL/adaptation/statistic registers, MPHY and analog override registers, and analog TX/RX calibration and ATB registers through `0x12fc`.
- `CR1_LANE3`: a reduced lane map. It includes ASIC override registers, TX power/DCC/LBERT controls, RX statistic registers, digital TX analog override/status registers, and analog TX controls through `0x13ef`, but does not include the full RX power/adaptation/analog RX set present on lanes 1 and 2.
- `CR1_RAWCMN`: common raw PCS/PHY control registers at `0x2000-0x2040`, including common control, MPLLA/MPLLB overrides and SSC controls, lane FSM extension, SRAM init status, OCLA, firmware ID codes, AON common RTUNE values for multiple lanes, power-gate overrides, VREF stats, resource overrides, and reference range/misc config.
- `CR1_RAWLANE0` through `CR1_RAWLANE3`: per-lane raw PCS transfer and FSM/IRQ/PMA/TX/RX control registers. Each raw lane starts at `0x3000`, `0x3100`, `0x3200`, or `0x3300` and reaches `*_DIG_PCS_XF_TX_OVRD_IN_2` at `0x30c8`, `0x31c8`, `0x32c8`, or `0x33c8`.
- `CR1_RAWAONLANE0` through `CR1_RAWAONLANE3` and `CR1_RAWAONLANEX`: always-on raw lane calibration/status register families. These include AFE ATT/CTLE offsets, RX IQ and FOM status, DFE reference/phase/data/error offsets, adaptation results, fast flags, MPLL coarse tune/status, slicer controls, SIGDET controls, RX DCC calibration codes, TX DCC bank/config controls, firmware config, and lane XCVR mode input. The `LANEX` aliases use the `0x7000` range for lane-generic access.
- `CR1_SUPX` and `CR1_RAWLANEX`: generic or broadcast-style aliases for supervisor and raw lane registers. `SUPX` starts at `0x8000` and mirrors supervisor PLL/reference/RTUNE definitions, while `RAWLANEX` starts at `0xe000` and mirrors raw PCS lane controls for lane-generic programming.
- `CR2` address block: a second DPCSSYS instance begins at line 4162 with base `0x0`. The chunk includes `CR2_SUP` definitions from ID/refclk/MPLL overrides through RTUNE and analog status outputs, then lane maps for `CR2_LANE0`, `CR2_LANE1`, `CR2_LANE2`, and the beginning of `CR2_LANE3`.

Important repeated register families are:

- `DIG_ASIC_*`: override inputs/outputs and ASIC-facing lane/TX/RX/equalization/CDR/VCO signals.
- `DIG_TX_PWRCTL_*` and `DIG_RX_PWRCTL_*`: TX/RX p-state and power-up timing controls.
- `DIG_RX_VCOCAL_*`, `DIG_RX_CDR_*`, and `DIG_RX_DPLL_*`: RX clock recovery, VCO calibration, frequency, and status controls.
- `DIG_RX_ADPTCTL_*`: RX adaptation configuration, reset, status, DFE tap, slicer, DAC selector, and CR bank address/data registers.
- `DIG_RX_STAT_*`: statistic match controls, sample count, counter outputs, statistic control, and stop controls.
- `DIG_ANA_*` and `ANA_*`: digital-to-analog override outputs plus analog TX/RX power, termination, equalization, CDR, slicer, calibration, ATB, and measurement registers.
- `RAWLANE*_DIG_FSM_*`, `IRQ_CTL_*`, `PMA_XF_*`, `TX_CTL_*`, and `RX_CTL_*`: raw PCS/PHY lane state-machine, interrupt, PMA transfer, TX, and RX controls.
- `RAWAONLANE*_DIG_*`: always-on lane calibration and adaptation state.

## APIs, Types, and Functions

This header chunk defines no functions, structs, enums, or run-time data. Its API is the macro naming contract:

- `ixDPCSSYS_CR<n>_SUP_*` for supervisor/common indirect registers.
- `ixDPCSSYS_CR<n>_LANE<m>_*` for concrete lane indirect registers.
- `ixDPCSSYS_CR<n>_RAWCMN_*` for raw common PCS/PHY indirect registers.
- `ixDPCSSYS_CR<n>_RAWLANE<m>_*` and `ixDPCSSYS_CR<n>_RAWLANEX_*` for lane-specific or generic raw PCS/PHY indirect registers.
- `ixDPCSSYS_CR<n>_RAWAONLANE<m>_*` and `ixDPCSSYS_CR<n>_RAWAONLANEX_*` for always-on calibration/adaptation indirect registers.

Functional code combines these offset macros with companion field shift/mask macros from `dpcs_3_1_4_sh_mask.h`. In this tree, `display/dc/resource/dcn314/dcn314_resource.c` includes both `dpcs/dpcs_3_1_4_offset.h` and `dpcs/dpcs_3_1_4_sh_mask.h`, making this generated offset namespace available while constructing DCN 3.1.4 display resources. The broader DPCS access pattern is visible in link-encoder headers such as `dcn201_link_encoder.h`, where `SRI_IX(RAWLANE0_DIG_PCS_XF_RX_OVRD_IN_2, DPCSSYS_CR, id)` style macros assemble indexed register table entries from `ixDPCSSYS_CR<id>_*` constants, and `LE_SF(...)` entries pair the same registers with field masks and shifts.

## Control Flow

There is no executable control flow in the chunk. Runtime flow is indirect:

1. DCN 3.1.4 resource code includes this generated header and its shift/mask companion.
2. Register-list macros select constants such as `ixDPCSSYS_CR1_RAWLANE2_DIG_PCS_XF_RX_OVRD_IN_2` or `ixDPCSSYS_CR2_SUP_DIG_RTUNE_CONFIG` for a concrete DPCS instance.
3. Link encoder, PHY, or low-level display code passes the selected indices into AMD display register helpers for indirect DPCS reads/writes.
4. Hardware state changes occur in the DPCS block: PLL/reference clock programming, TX/RX power sequencing, lane adaptation, CDR/VCO calibration, DCC calibration, signal-detect behavior, raw PCS override paths, debug/statistic capture, or analog measurement setup.

Because all constants are compile-time values, errors here do not create local C control-flow failures. They manifest as deterministic access to the wrong hardware index.

## State and Persistence Behavior

The file itself has no mutable software state and stores no persistent data. It describes hardware state that persists in DPCS registers until reset, power-gating, firmware/hardware sequencing, or another driver write changes it.

Stateful hardware surfaces represented by this chunk include:

- Supervisor/common PLL and reference state: MPLLA/MPLLB overrides, SSC settings, RTUNE configuration/status, bandgap/reference power-up timing, and common AON calibration values.
- Lane power and p-state state: TX/RX p-state controls and power-up timing values for active lanes.
- RX training/adaptation state: ATT/VGA/CTLE/DFE status, slicer/DAC selections, adaptation resets, VCO/CDR/DPLL state, and statistic counters.
- Calibration state: DCC bank address/data/control registers, RX DCC calibration codes, VREF and signal-detect calibration, MPLL coarse tune/status, and TX/RX analog calibration registers.
- Debug and validation state: LBERT control/error registers, OCLA taps, RX statistic match/count registers, ATB measurement controls, and raw FSM/status/IRQ registers.

The repeated concrete-lane and generic-lane aliases mean the same functional hardware areas can be reached through multiple symbolic address families depending on the access path chosen by the driver or generated register table.

## Dependencies and Integration Points

Key dependencies are:

- `dpcs_3_1_4_sh_mask.h`: companion generated bitfield definitions. Offset constants here only identify registers; field shifts and masks are needed for safe field updates and reads.
- AMD Display Core register-helper macros, including `SRI_IX`, `LE_SF`, `REG_READ`, `REG_UPDATE`, `REG_GET`, `REG_SET`, and related indexed-register helpers.
- DCN 3.1.4 resource construction in `display/dc/resource/dcn314/dcn314_resource.c`, which includes this header alongside DCN and DPCS generated register headers.
- DPCS/link-encoder table definitions inherited from earlier DCN generations, especially raw lane override entries used for VCO/ref load override programming.
- Hardware generation inputs for DPCS 3.1.4. The source is generated under `include/asic_reg`, so correctness depends on generated register metadata matching the actual ASIC register map.

The chunk is source-tree-aligned with AMD GPU display code, despite living in a Ceph-client source mirror. It does not interact with Ceph file-system logic; it is part of the vendored Linux AMDGPU display driver tree.

## Risks and Maintenance Hazards

- Register-index drift is high impact. A wrong numeric value can program the wrong DPCS indirect register while still compiling cleanly.
- Chunk boundaries split logical register families. This slice starts after the beginning of `CR1_LANE1_DIG_RX_STAT_*` and ends before the rest of `CR2_LANE3_DIG_RX_STAT_*`, so file-level analysis must merge adjacent chunk research before drawing completeness conclusions.
- Lane symmetry is partial. Lanes 1 and 2 have full RX power/adaptation/analog RX coverage in this range, while lane 3 has a reduced subset in both `CR1` and the visible part of `CR2`. Consumers must use the generated per-lane tables, not assume every lane has the same register family.
- Generic aliases (`SUPX`, `RAWLANEX`, `RAWAONLANEX`) can obscure whether a path targets a concrete lane or a broadcast/generic lane aperture. Misusing an alias can affect the wrong scope.
- Many registers are calibration and sequencing sensitive. Incorrect DCC, VCO, CDR, RTUNE, SIGDET, or power timing indices can cause subtle link-training failures, unstable DisplayPort/HDMI PHY behavior, or intermittent modeset failures rather than immediate driver errors.
- Debug/status registers such as LBERT, RX statistics, OCLA, and ATB measurement controls are also operationally useful. Bad offsets can mislead diagnostics and validation even when ordinary display paths appear to work.

## Test and Validation Signals

Useful validation signals for changes touching this generated section include:

- Compile coverage for `dcn314_resource.c` and related display/link-encoder objects. Renamed or removed macros should fail at build time where register tables reference them.
- DCN 3.1.4 hardware display bring-up with multiple physical links, covering both DPCS `CR1` and `CR2` instances.
- DisplayPort link training across lane counts and link rates, because the chunk covers TX power, RX CDR/VCO/DPLL, raw lane override, and lane adaptation surfaces.
- Hotplug, modeset, suspend/resume, and power-gating tests that exercise DPCS supervisor PLL/reference and lane power timing state.
- PHY calibration stress, including RTUNE, DCC, signal-detect, RX adaptation, and VREF/DFE/slicer behavior.
- Debug validation that reads RX statistic counters, LBERT error paths, OCLA/debug taps, and ATB measurement registers to confirm offsets report plausible lane-specific state.
- Regression comparison against generated AMD register headers for the same ASIC version; because this file is generated, manual edits should generally be treated as suspect unless they match the upstream generation source.
