# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002256`: lines 1-2405, `Docs/researches/chunks/subset-b-002256_research.md`
- `subset-b-002257`: lines 2406-4791, `Docs/researches/chunks/subset-b-002257_research.md`
- `subset-b-002258`: lines 4792-7215, `Docs/researches/chunks/subset-b-002258_research.md`

## Chunk Research

### subset-b-002256: lines 1-2405

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h lines 1-2405

## Scope

This chunk covers lines 1-2405 of `drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h` under the Ceph client source mirror. It includes the MIT license/header guard and the first two `dpcssys_*_rdpcstxcrind` address blocks:

- Full `dpcssys_cr0_rdpcstxcrind` offset map, starting at line 30 and running through the CR0 raw lane/X aliases.
- Start of `dpcssys_cr1_rdpcstxcrind`, from line 2096 through `ixDPCSSYS_CR1_LANE1_DIG_RX_STAT_STAT_CTL1` at line 2405.

Within the 1-2405 range there are 2,370 `ixDPCSSYS_*` register-offset macros: 2,062 for `CR0` and 308 for the beginning of `CR1`. The full source file is 7,215 lines; later chunks cover the rest of CR1/CR2 and the display decoder/PWRSEQ address maps.

## Purpose

This file is a generated ASIC register offset header for AMD DPCS version `3_1_4`. It provides symbolic C preprocessor constants for indexed DPCS register offsets used by AMDGPU display code. The names encode the hardware hierarchy:

- `DPCSSYS`: DisplayPort/PHY/clocking subsystem register namespace.
- `CR0` and `CR1`: clock/recovery or PHY register-bank instances. This chunk fully maps `CR0` and starts `CR1`.
- `SUP`, `SUPX`: supervisor/common PLL and analog support register regions.
- `LANE0` through `LANE3`, plus `LANEX`: per-lane PHY/DIG/ANA register regions and a generic lane alias.
- `RAWCMN`, `RAWLANE*`, `RAWAONLANE*`, `RAWLANEX`, `RAWAONLANEX`: raw common, raw per-lane, and always-on raw lane register views.

The header has no executable behavior. Its functional role is to keep hard-coded MMIO/indexed-register offsets out of C logic and to make call sites use named constants when programming or reading DPCS PHY state.

## Important API Surface

The only exported API is macro definitions guarded by `_dpcs_3_1_4_OFFSET_HEADER`. There are no structs, functions, enums, inline helpers, or storage definitions in this chunk.

Key macro families in the chunk:

- `ixDPCSSYS_CR0_SUP_DIG_*` and `ixDPCSSYS_CR1_SUP_DIG_*`: supervisor digital registers for ID code, refclk overrides, MPLLA/MPLLB overrides, SSC programming, MPLL power-control status/timers/calibration, clock/reset timing, RTUNE configuration/status, and analog override outputs.
- `ixDPCSSYS_CR0_SUP_ANA_*` / `ixDPCSSYS_CR0_SUPX_ANA_*`: analog supervisor controls for prescaler, RTUNE, bandgap, and power measurement.
- `ixDPCSSYS_CR0_LANE*_DIG_ASIC_*`: ASIC-facing per-lane override/input/output registers. Lane 0 and lane 3 in this chunk are mostly TX/status focused; lanes 1 and 2 include fuller RX calibration/adaptation sets.
- `ixDPCSSYS_CR0_LANE*_DIG_TX_PWRCTL_*`: TX p-state and power-up timing registers, with DCC DAC controls and `TX_LBERT_CTL`.
- `ixDPCSSYS_CR0_LANE*_DIG_RX_PWRCTL_*`, `RX_VCOCAL_*`, `RX_CDR_*`, `RX_ADPTCTL_*`, and `RX_STAT_*`: RX p-state, VCO calibration, CDR, adaptation, and receiver statistic/counter controls for RX-capable lane views.
- `ixDPCSSYS_CR0_LANE*_DIG_ANA_*` and `ixDPCSSYS_CR0_LANE*_ANA_*`: digital-to-analog override/status and raw analog TX/RX register offsets, including TX equalization, term-code, DCC, RX AFE, CTLE, slicer, phase, signal detect, and ATB measurement registers.
- `ixDPCSSYS_CR0_RAWCMN_DIG_*`: raw common controls for common lane FSM extension, MPLL state, SRAM init status, OCLA, PCS/FW ID codes, AON common RTUNE values, and common power/resource overrides.
- `ixDPCSSYS_CR0_RAWLANE*_DIG_*`: raw PCS/PMA/FSM/IRQ/TX/RX control views for each lane. These expose PCS crossbar override/input/output, RX adaptation acknowledgements/FOM, fast FSM calibration/adaptation steps, interrupt status/clear/mask registers, PMA crossbar, and TX/RX control status.
- `ixDPCSSYS_CR0_RAWAONLANE*_DIG_*`: always-on lane state such as AFE/DFE calibration offsets, adaptation results, signal-detect calibration, RX DCC calibration, TX DCC bank access, firmware config, and lane transceiver mode inputs.
- Generic aliases `CR0_RAWAONLANEX`, `CR0_SUPX`, `CR0_LANEX`, and `CR0_RAWLANEX`: X-suffixed offset templates for programming a selected lane/supervisor view through a common indexed aperture.

The macro values are offsets, not absolute CPU physical addresses. The file comments state `base address: 0x0` for both CR0 and CR1 indexed blocks in this chunk.

## Control Flow

There is no runtime control flow in this header. At compile time, including C files can reference these constants in register read/write expressions. Runtime ordering is determined by the caller, typically AMDGPU display, link training, PHY initialization, diagnostics, or power-management routines.

The implicit control pattern supported by these offsets is:

1. Select or address the DPCS indexed register aperture for the target CR/lane/register block.
2. Write override/control registers such as `*_OVRD_IN`, `*_PSTATE_*`, `*_MPLL_PWR_CTL_*`, `*_ADPT_CFG_*`, or IRQ clear/mask offsets.
3. Poll or read status registers such as `*_STAT`, `*_STATUS`, `*_ADAPT_DONE`, `*_INIT_PWRUP_DONE`, `*_VCO_STAT_*`, `*_LBERT_ERR`, or receiver statistic counters.
4. Use per-lane or X-alias offsets according to whether the code is targeting a fixed hardware lane or a generic lane-selected path.

Because this chunk is only offsets, it does not define access width, bit fields, masking, locking, polling loops, timeouts, or reset sequencing. Those are expected to come from paired mask/shift headers and from AMDGPU display code.

## State And Persistence

This header persists symbolic definitions in the compiled driver. It does not allocate memory or persist runtime state by itself.

The hardware registers named here represent volatile device state. Important state classes exposed by this chunk include:

- PLL and clock state: MPLLA/MPLLB overrides, SSC peak/stepsize/spread-type fields, MPLL power-control status/timers/calibration, refclk and prescaler controls.
- Power and reset state: TX/RX p-states, power-up timing, bandgap/ref power-up timing, reset-related IRQs, and low-speed/MPHY controls.
- Calibration/adaptation state: RTUNE values, RX VCO calibration, CDR/DPLL state, AFE/CTLE/VGA/DFE adaptation controls and status, DCC DAC and calibration banks.
- Diagnostic/test state: LBERT controls/errors, OCLA hooks, IRQ masks/clear/status, PCS/PMA raw override paths, statistic sample/match/counter registers, ATB measurement registers, and firmware ID/config registers.

Any persistence across suspend/resume, GPU reset, display hotplug, or mode set depends on higher-level AMDGPU display code reprogramming these hardware registers from driver state. This header only supplies the offsets required for that reprogramming.

## Dependencies

Direct dependencies are minimal:

- C preprocessor include guard `_dpcs_3_1_4_OFFSET_HEADER`.
- AMDGPU include conventions for ASIC register headers, especially `ix*` naming for indexed-register offsets.
- Pairing with adjacent generated register definition headers, commonly mask/shift headers for the same DPCS IP version, so callers can combine an offset macro with bit-field masks.

There are no Linux kernel includes, type dependencies, function declarations, or module-level dependencies in this chunk.

## Integration Points

Likely consumers are AMDGPU DRM display/DM/DCN code paths that configure DPCS PHY, DisplayPort/HDMI transmit lanes, link training, signal integrity, and PHY diagnostics. The integration contract is purely symbolic: a call site includes this header, selects a named `ixDPCSSYS_*` offset, and passes that offset to AMD register access helpers.

Important integration details:

- The offset namespace is IP-version-specific (`dpcs_3_1_4`), so it must match the ASIC/IP block selected by the driver. Using these offsets on a different DPCS revision can target the wrong hardware register.
- CR0 and CR1 macro values intentionally repeat many numeric offsets because they are separate indexed blocks. The instance prefix is part of the semantic address even when the offset literal is the same.
- X-suffixed macros (`LANEX`, `RAWLANEX`, `RAWAONLANEX`, `SUPX`) are not simple duplicates of lane-specific macros; they expose generic/indirect address windows starting at distinct ranges such as `0x7000`, `0x8000`, `0x9000`, and `0xe000`.
- This chunk stops mid-CR1, at lane1 RX stat control. Any research or generated final document must not infer that the CR1 map ends here.

## Risks And Edge Cases

- Register drift risk: generated headers must match the ASIC register database. A single stale offset can silently misprogram PHY power, PLL, training, or diagnostic controls.
- Instance confusion: CR0 and CR1 reuse many offset values. Callers must use the correct access path/address block, not just the numeric offset.
- Lane asymmetry: lane 0 and lane 3 sections in this chunk are smaller TX/stat-focused subsets, while lane 1/lane 2 and generic `LANEX` include fuller RX/adaptation/analog sets. Code that assumes every lane has every macro can fail at compile time or, worse, use the wrong alias.
- Raw and public views: `RAW*` register views expose lower-level PCS/PMA/FSM/IRQ/AON controls. These are more sensitive to sequencing and are likely intended for firmware bring-up, diagnostics, or tightly ordered PHY routines.
- Partial chunk boundary: line 2405 ends in the middle of the CR1 lane1 RX stat group. Consumers of this research should reconcile with later chunks before making file-level conclusions.
- Reserved or test-oriented registers: names containing `RESERVED`, `ATE`, `OCLA`, `ATB`, and `LBERT` should be treated cautiously. They may be hardware debug/test hooks, not stable product-facing programming interfaces.

## Test Signals

Useful validation for this header is mostly build-time and hardware-integration focused:

- Compile coverage: AMDGPU display objects that include `dpcs_3_1_4_offset.h` must compile with all referenced `ixDPCSSYS_*` names present.
- Header hygiene: include guard prevents duplicate definitions; no generated macro should collide with another macro name in the same IP-version namespace.
- Register database checks: regenerated offsets should diff cleanly against this header for DPCS 3.1.4. Review any numeric change in PLL, p-state, DCC, CDR, IRQ, or adaptation-related offsets.
- Runtime bring-up tests: display link training, hotplug, suspend/resume, GPU reset recovery, and modeset tests can reveal wrong offsets through link failures, PHY calibration timeouts, blank displays, or unstable high-rate links.
- Diagnostic paths: LBERT/OCLA/stat-counter reads should return plausible values when supported by hardware; IRQ clear/mask flows should not leave stale lane events asserted.
- Static sanity checks: the chunk contains 2,370 `ixDPCSSYS_*` defines; within this slice the CR0/CR1 split is 2,062/308. A changed count is not necessarily wrong, but it is a strong signal for register database or chunk-boundary review.

### subset-b-002257: lines 2406-4791

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

### subset-b-002258: lines 4792-7215

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h lines 4792-7215

## Purpose

This chunk is the final slice of AMD's generated DPCS 3.1.4 register-offset header. It contains no executable driver logic; it publishes C preprocessor constants that map symbolic Display Core PHY/PCS/DCIO register names to numeric offsets and, for MMIO-style `reg...` entries, companion `_BASE_IDX` selectors. Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU display hardware metadata, not distributed filesystem code.

The range starts in the tail of the `DPCSSYS_CR2_LANE3` internal-index register list, then covers the `DPCSSYS_CR2_RAWCMN` common block and raw lanes 0 through 7. It then switches to direct display decoder register aliases for DCIO, GPIO/DDC/HPD/AUX pads, UNIPHY macro reserved spaces, RDPCSTX transmit PHY instances, CR address/data windows, RDPCSPIPE controls, and two panel/backlight power sequencer blocks. The chunk ends with the file's closing `#endif`.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, local includes, allocation paths, or locking primitives in this chunk. The public interface is the generated macro namespace:

- `ixDPCSSYS_CR2_*`: indirect DPCS CR2 register indices. These are used through CR address/data access paths rather than as plain MMIO offsets.
- `reg<block>_<register>`: direct register offset aliases for DCIO, RDPCSTX, RDPCSPIPE, DPCSSYS CR windows, and PWRSEQ blocks.
- `reg<block>_<register>_BASE_IDX`: base-address segment selector paired with each direct `reg...` offset. All visible `_BASE_IDX` values in this chunk are `2`.

The requested range contains 2,354 `#define` statements: 1,434 `ix...` internal-index constants and 920 `reg...` direct-offset/base-index constants. Major register families in this slice are:

- `ixDPCSSYS_CR2_LANE3_*`: the end of lane 3 receive statistic counters, match/stat controls, digital-to-analog TX override outputs, analog TX power/termination/equalization/DCC registers, and reserved analog TX slots.
- `ixDPCSSYS_CR2_RAWCMN_*`: common DPCS raw controls for MPLL A/B overrides, spread-spectrum controls, lane FSM extension, MPLL state, TX calibration code, SRAM init status, OCLA/debug visibility, PCS/FW ID codes, AON RTUNE values for lanes 0 through 7, power-gate overrides, VREF stats, resistance overrides, and reference-range/misc configuration.
- `ixDPCSSYS_CR2_RAWLANE0` through `ixDPCSSYS_CR2_RAWLANE7`: repeated per-lane PCS/PMA/FSM/IRQ/TX/RX control blocks. Each lane has PCS transfer override/input/output registers, RX adaptation and figure-of-merit registers, per-lane FSM fast-path and status registers, RX/TX interrupt and clear registers, PMA transfer controls, TX/RX control/status registers, ATE override hooks, and master MPLL loop controls.
- `regDC_*`, `regDCIO_*`, `regUNIPHY*_*`, `regDC_GPIO_*`, `regPHY_AUX_CNTL`, and `regAUXI2C_PAD_ALL_PWR_OK`: DCIO clock/reference/mux state, UNIPHY link and channel crossbar controls, pinstraps/intercept/soft-reset controls, backlight frame-start selection, genlock/swaplock pads, DDC/HPD/generic GPIO masks/data/enables/readbacks, pad strength, AUX controls, RX/pull-up enables, and AUX/I2C pad power-good status.
- `regDCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED0` through `...RESERVED57`, and equivalent ranges for UNIPHY2, UNIPHY3, and UNIPHY4: contiguous reserved macro-control address spaces for PHY instances at base addresses `0x360`, `0x6c0`, `0xa20`, and `0xd80`; the UNIPHY0 address block is present but empty in this chunk.
- `regRDPCSTX0`, `regRDPCSTX1`, and `regRDPCSTX2`: repeated RDPCS transmitter control, clock, interrupt, PLL update, CR address/data, SRAM, scratch/spare, PHY control 0-17, PHY fuse 0-3, RX load value, DPALT control, and PLL override registers.
- `regDPCSSYS_CR0`, `regDPCSSYS_CR1`, and `regDPCSSYS_CR2`: direct aliases for each instance's CR address/data window; these overlap the corresponding RDPCSTX CR address/data offsets.
- `regRDPCSPIPE0_RDPCSPIPE_PHY_CNTL6` and `regRDPCSPIPE1_RDPCSPIPE_PHY_CNTL6`: pipe-level PHY control aliases.
- `regPWRSEQ0_*` and `regPWRSEQ1_*`: panel power GPIO enable/control/mask/readback, panel sequence control/state/delay/reference-divider registers, backlight PWM control/period/register-lock registers, and spare power-sequencer state.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMD display driver code that includes this generated offset header with matching shift/mask headers and register-access helper macros. The typical flow is:

1. Resource, GPIO, DIO/PHY, link-training, backlight, or firmware-facing display code selects an ASIC-specific register set.
2. Token-pasting helper macros resolve names such as `regRDPCSTX2_RDPCSTX_PHY_CNTL0`, `regPWRSEQ0_BL_PWM_CNTL`, or `ixDPCSSYS_CR2_RAWLANE3_DIG_FSM_STATUS_MON`.
3. For direct `reg...` entries, access helpers combine `BASE(reg..._BASE_IDX)` with the offset before issuing MMIO reads/writes.
4. For `ixDPCSSYS_CR2_*` entries, code programs a CR address register and transfers data through the paired CR data register for the relevant DPCS/RDPCS instance.
5. Higher-level display code sequences resets, clocks, PLL programming, link enablement, lane training, GPIO/AUX/DDC access, panel power, backlight PWM, interrupt handling, and suspend/resume restore using these constants.

The macro data does not encode ordering, access width, polling requirements, write-one-to-clear behavior, or read-only/write-only status. Those semantics come from the companion mask/enum headers and the code that consumes this file.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It describes hardware-backed state:

- CR2 raw common and lane registers hold PHY/PCS configuration and live status for PLLs, RTUNE calibration, SRAM initialization, lane FSMs, RX adaptation, TX/RX power and reset paths, PMA/PCS override paths, ATE/debug paths, and interrupt latches/clears.
- DCIO and GPIO registers hold display IO routing, clock/reference selection, UNIPHY link/crossbar configuration, GPIO output/input/mask/enable state, DDC/HPD/generic pin state, pad strengths, AUX pad controls, pull-up/RX enablement, and soft-reset state.
- RDPCSTX registers hold transmitter reset/clock/FIFO state, PHY DP/HDMI rate and width controls, PLL update state, CR bridge state, SRAM controls, DPALT controls, PHY fuses, and scratch/spare registers.
- PWRSEQ registers hold panel target/state sequencing, delay and reference divider values, backlight PWM configuration, PWM register lock state, and power-sequencer GPIO state.

Persistence is hardware-defined. Configuration registers may survive until the next modeset, link reconfiguration, power gate, suspend/resume, or ASIC reset. Status, interrupt, clear, counter, debug, and calibration registers may be volatile, sticky, self-clearing, write-one-to-clear, or sequencing-sensitive. The offset header intentionally does not model those behaviors.

## Dependencies And Integration Points

The direct dependency is the C preprocessor plus AMD's generated ASIC register-header convention. This file must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h`, which provides shifts and masks for the register names defined here.
- SOC/DCN base-address tables and helper macros that interpret `_BASE_IDX == 2`.
- Related generated enum headers such as `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc21_enum.h` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h`, which define field values for PWRSEQ and RDPCSTX concepts.
- ATOM firmware structures in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/atomfirmware.h`, whose transmitter parameter comments map values such as TX equalization and voltage boost to RDPCSTX PHY fuse/control fields.

Integration points are display-hardware focused: DC link encoder/PHY setup, DisplayPort and HDMI PHY programming, AUX/DDC/HPD GPIO translation, panel power sequencing, backlight PWM control, DMU/firmware-assisted PHY programming, debug/OCLA inspection, and low-power or reset flows. The `regDPCSSYS_CR*_DPCSSYS_CR_ADDR` and `reg..._CR_DATA` aliases are especially important because they are the bridge between direct MMIO access and the many `ixDPCSSYS_CR2_*` internal register indices in this chunk.

## Risks And Edge Cases

- Offset or base-index drift is the central risk. These constants are untyped macros, so a wrong offset or `_BASE_IDX` can compile cleanly while targeting the wrong MMIO address.
- `ix...` and `reg...` constants are not interchangeable. Treating an internal CR index such as `ixDPCSSYS_CR2_RAWLANE0_DIG_FSM_STATUS_MON` as a direct MMIO offset, or bypassing the CR address/data window, would access the wrong hardware path.
- The range begins mid-block at the tail of `DPCSSYS_CR2_LANE3`; adjacent chunks are needed for the complete lane 3 CR2 map and complete file-level interpretation.
- Repeated lane and instance families are copy-sensitive. RAWLANE0-7, UNIPHY1-4, RDPCSTX0-2, CR0-2, and PWRSEQ0-1 have similar names but different offsets and base addresses; off-by-one instance selection can create connector-specific, lane-count-specific, or panel-specific failures.
- Some apparent overlaps are intentional aliases. For example, RDPCSTX CR address/data offsets are also exposed through `regDPCSSYS_CR*`; validation must distinguish generated aliases from collisions.
- The UNIPHY reserved ranges are named `RESERVED`, but they still occupy concrete addresses. New code should not infer field semantics from those names without the matching hardware database or mask definitions.
- RDPCSTX, PLL, CR, SRAM, and lane FSM registers are sequencing-sensitive. Misordered reset, clock, SRAM init, PLL update, or lane training accesses can produce blank displays, link-training failures, FIFO errors, or intermittent failures after resume.
- GPIO/DDC/HPD/AUX and PWRSEQ registers affect external pins and panel power. Incorrect mask/enable/polarity/delay/PWM programming can break EDID reads, hotplug detection, backlight control, panel sequencing, or low-power wake.

## Test Signals

Useful validation signals are mostly integration or hardware tests rather than unit tests:

- Build coverage that includes ASIC paths using `dpcs_3_1_4_offset.h` and `dpcs_3_1_4_sh_mask.h`; macro spelling or missing companion definitions should fail at compile time.
- Register-header consistency checks that every direct `reg...` offset has a matching `_BASE_IDX`, and that alias pairs such as `regRDPCSTX*_RDPCS_TX_CR_ADDR` and `regDPCSSYS_CR*_DPCSSYS_CR_ADDR` intentionally match.
- Display bring-up tests across connectors mapped to different RDPCSTX/UNIPHY instances, including link training at multiple DP rates and lane counts, HDMI/DP mode changes, hotplug, AUX DPCD reads, and DDC EDID reads.
- Suspend/resume and power-gating tests that exercise RDPCSTX SRAM/PLL/clock restore, CR register access, GPIO state restoration, panel power sequencing, and backlight PWM restoration.
- Panel-specific tests for PWRSEQ0 and PWRSEQ1: power on/off timing, backlight enable/disable, PWM period and brightness changes, register lock behavior, and GPIO polarity.
- Debug/fault tests using interrupt/status paths for RDPCSTX FIFO errors, DPALT toggles, RAWLANE IRQ status/clear registers, and OCLA/debug visibility where hardware support is available.
