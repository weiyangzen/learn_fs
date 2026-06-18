# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h lines 7257-9642

## Scope

This chunk is part of the generated AMD DPCS 4.2.3 ASIC register offset header. It contains only C preprocessor address constants: every exported symbol in the requested range has the form `ixDPCSSYS_*` and maps a DPCS indirect-register name to a numeric offset. There are no C functions, structs, typedefs, enums, branches, locks, allocations, direct MMIO operations, or persistent software objects in this slice.

The range contains 2,382 `#define` entries. It starts in the CR2 `SUPX` alias block at `ixDPCSSYS_CR2_SUPX_DIG_ASIC_IN` and covers 414 CR2 offsets, then crosses the `dpcssys_cr3_rdpcstxcrind` address-block marker at lines 7673-7674 and covers 1,968 CR3 offsets. The final visible line is `ixDPCSSYS_CR3_LANEX_DIG_ANA_RX_DAC_CTRL_SEL`; the rest of the CR3 `LANEX` analog RX tail continues after this chunk.

## Purpose

The purpose of this header chunk is to publish exact DPCS 4.2.3 register offsets for AMDGPU display/PHY code. Runtime consumers pair these `ixDPCSSYS_*` offsets with companion field definitions from `dpcs_4_2_3_sh_mask.h` and with AMD display register access helpers. The offset header lets driver tables refer to generated symbolic addresses rather than embedding raw indirect-register numbers in link training, PHY power, calibration, diagnostics, and hardware bring-up code.

The covered register-map areas are:

- CR2 `SUPX` support/common aliases for ASIC inputs, analog prescaler, RTUNE, bandgap, MPLLA/MPLLB controls, MPLL power-control/status/timers/calibration, clock/reset timing, and digital-to-analog override/status outputs.
- CR2 `LANEX` lane alias offsets for ASIC-facing TX/RX override and live-status registers, TX/RX power sequencing, RX VCO calibration, CDR/DPLL, RX adaptation, RX statistics, MPHY low-speed controls, digital analog override/status, and analog TX/RX controls through reserved RX registers.
- CR2 `RAWLANEX` raw lane alias offsets for PCS transfer, FSM status/control, IRQ status/clear/mask, PMA transfer, TX/RX controller, OCLA/UPCS observation, ATE overrides, master MPLL loop, and secondary override banks.
- CR3 `SUP` and `SUPX` support/common offsets for ID code, reference clock, MPLLA/MPLLB overrides, SSC parameters, charge-pump controls, prescaler, ASIC input mirrors, bandgap, RTUNE, MPLL power controls, clock/reset timing, and analog override/status.
- CR3 concrete lane windows: `LANE0` and `LANE3` appear as smaller lane subsets, while `LANE1` and `LANE2` are broader lane maps with ASIC, TX/RX power, RX VCO/CDR/DPLL/adaptation/statistics, MPHY, digital analog, and analog TX/RX offsets.
- CR3 raw common, raw lane, raw always-on lane, and alias windows: `RAWCMN`, `RAWLANE0` through `RAWLANE3`, `RAWAONLANE0` through `RAWAONLANE3`, `RAWAONLANEX`, `RAWLANEX`, plus the start of `LANEX`.

Although this repository path is under `sources/distributed-fs/ceph-client`, this file is AMD GPU display hardware metadata. It has no Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace:

- `ixDPCSSYS_<CR instance>_<block>_<register>` gives the indirect DPCS CR offset for one hardware register.
- `CR2` and `CR3` identify DPCS CR instances. In this range, CR2 is the tail of an existing address block and CR3 begins explicitly at `dpcssys_cr3_rdpcstxcrind`.
- `SUP`, `SUPX`, `LANE0` through `LANE3`, `LANEX`, `RAWCMN`, `RAWLANE*`, `RAWLANEX`, `RAWAONLANE*`, and `RAWAONLANEX` encode address-space and lane/alias scope.

Important address families in this slice include:

- `ixDPCSSYS_CR2_SUPX_*`: support/common alias offsets around the `0x8000` range, including MPLL A/B analog controls, MPLL power-control status and timers, SSC spread-type registers, bandgap/reference timing, RTUNE set/status values, and analog override output registers.
- `ixDPCSSYS_CR2_LANEX_*`: lane alias offsets around `0x9000` through `0x90ff`, covering ASIC override/status, TX/RX P-state registers, DCC DAC programming, TX clock alignment, LBERT, RX VCO calibration, CDR/DPLL, RX adaptation, RX statistics, MPHY, digital analog override/status, and analog TX/RX controls.
- `ixDPCSSYS_CR2_RAWLANEX_*`: raw lane alias offsets around `0xe000`, covering PCS transfer inputs/outputs, fast FSM control/status, IRQ status/clear/mask, PMA handshakes, TX/RX controller state, ATE hooks, master MPLL loop, and late override registers.
- `ixDPCSSYS_CR3_SUP_*` and `ixDPCSSYS_CR3_SUPX_*`: supervisor/common offsets at the base CR3 range and the `0x8000` alias range. These define PLL/reference/RTUNE/bandgap/clock-reset surfaces used before or during lane programming.
- `ixDPCSSYS_CR3_LANE0_*` through `ixDPCSSYS_CR3_LANE3_*`: concrete lane windows. Lane 1 and lane 2 have 203 offsets each in this chunk; lane 0 and lane 3 have 85 offsets each, reflecting the generated hardware map rather than a software normalization.
- `ixDPCSSYS_CR3_RAWCMN_*`: raw common offsets for common control, MPLL status, SRAM initialization, OCLA, firmware identifiers, and always-on common RTUNE values.
- `ixDPCSSYS_CR3_RAWLANE*_*` and `ixDPCSSYS_CR3_RAWLANEX_*`: raw lane PCS/FSM/IRQ/PMA/TX/RX/ATE offsets repeated at per-lane ranges and alias ranges.
- `ixDPCSSYS_CR3_RAWAONLANE*_*` and `ixDPCSSYS_CR3_RAWAONLANEX_*`: always-on lane calibration, adaptation, signal-detect, DCC, firmware configuration, and lane transceiver-mode offsets.
- `ixDPCSSYS_CR3_LANEX_*`: CR3 lane alias offsets starting at `0x9000`; this chunk reaches only through `DIG_ANA_RX_DAC_CTRL_SEL`, so later analog RX status/control and raw alias offsets must be read from the next chunk.

## Control Flow

This header has no runtime control flow. The runtime sequence is supplied by AMDGPU display and PHY code:

1. DCN 3.1.6 resource code includes `dpcs/dpcs_4_2_3_offset.h` and `dpcs/dpcs_4_2_3_sh_mask.h`.
2. Generated register tables or helper macros combine `ixDPCSSYS_*` offsets with matching shift/mask definitions.
3. Link encoder, PHY, and display code issue indexed register reads, writes, masked updates, and polls through the AMD register-access infrastructure.
4. Hardware and firmware implement the actual sequencing for PLL setup, reference and bandgap power, TX/RX P-state transitions, VCO/CDR/DPLL calibration, receiver adaptation, DCC, IRQ signaling, statistics collection, MPHY control, and debug or manufacturing override paths.

The implicit hardware flow represented by these offsets is: configure supervisor/common resources, select the correct CR instance and lane/alias window, program TX/RX power and timing, run calibration/adaptation, coordinate PCS/PMA and firmware-owned state machines, and observe status through raw, statistics, IRQ, OCLA, ATE, and analog readback registers.

## State And Persistence Behavior

The macros are stateless compile-time constants. The mutable state they name lives in volatile DPCS hardware registers.

State represented by this slice includes:

- Common/supervisor state: ID codes, reference-clock overrides, MPLL A/B override values, SSC parameters, charge-pump controls, prescaler, bandgap, RTUNE, clock/reset timers, MPLL power-control status, and analog override output state.
- Lane power and timing state: TX/RX P-state controls, power-up timers, DCC DAC bank/address/data controls, TX clock alignment, MPHY PWM/termination/stable-clock controls, and analog TX/RX power/clock/termination controls.
- Receiver calibration and link-quality state: RX VCO calibration controls/status, CDR controls/status, DPLL frequency and bounds, adaptation configuration, ATT/VGA/CTLE/DFE status, slicer and DAC offset controls, statistic counters, signal-detect calibration, and firmware calibration configuration.
- Raw and diagnostic state: PCS/PMA request/acknowledge mirrors, raw FSM status and fast flags, IRQ status/clear/mask registers, OCLA/UPCS observability, ATE override registers, LBERT controls/errors, analog test-bus registers, and DCC calibration status.
- Alias state: `SUPX`, `LANEX`, `RAWLANEX`, and `RAWAONLANEX` expose alias or indexed views over common/lane resources. The access path determines whether an alias targets a selected lane, a broadcast-style window, or a hardware-defined shared view.

Persistence is governed by hardware. Values may survive until a DPCS reset, GPU reset, display engine reset, lane reset, power gating transition, suspend/resume, firmware reload, modeset, hotplug-triggered retraining, or link-rate/lane-count change. The header itself stores no durable policy and provides no reset values, access permissions, side-effect markers, or timeout rules.

## Dependencies

This chunk depends on AMD's generated DPCS 4.2.3 register database staying synchronized with silicon and firmware expectations. Offset constants alone identify register locations; correct programming also requires matching field metadata and access semantics.

Key dependencies are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h`, which supplies the field shifts and masks for these register names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes both the DPCS 4.2.3 offset and shift/mask headers for DCN 3.1.6 resource construction.
- AMDGPU display register helper infrastructure that knows how to address DPCS indirect CR registers and apply shift/mask metadata.
- Firmware and hardware state machines that may own raw FSM, PCS/PMA, DCC, calibration, signal-detect, and adaptation registers during portions of link bring-up.
- Correct CR-instance and lane-window selection. CR2, CR3, concrete lanes, and alias windows expose highly repetitive names but are not interchangeable.

## Integration Points

The main integration point is AMDGPU display PHY/link code that builds version-specific register tables for DPCS 4.2.3 hardware.

Important integration surfaces are:

- PLL and common-resource bring-up through `SUP`/`SUPX` MPLL, SSC, refclk, bandgap, RTUNE, and clock/reset offsets.
- Lane power sequencing through `DIG_TX_PWRCTL_*`, `DIG_RX_PWRCTL_*`, `DIG_MPHY_*`, and analog TX/RX offsets.
- Receiver calibration and adaptation through `DIG_RX_VCOCAL_*`, `DIG_RX_CDR_*`, `DIG_RX_DPLL_*`, `DIG_RX_ADPTCTL_*`, raw always-on adaptation and signal-detect offsets, and RX statistic counters.
- PCS/PMA and firmware coordination through `RAWLANE*`, `RAWLANEX`, `RAWCMN`, and `RAWAONLANE*` offsets for request/acknowledge, reset, rate, pstate, DCC, RTUNE, IRQ, and firmware configuration paths.
- Diagnostics and validation through LBERT, OCLA, UPCS observation, ATE override, IRQ clear/mask, raw FSM status, analog test-bus, RX statistic, and analog status/readback offsets.
- Multi-lane mapping through repeated concrete lane ranges and alias ranges. Consumers must choose the namespace expected by the hardware sequence rather than deriving it by string similarity.

## Risks And Failure Modes

- A wrong offset can compile cleanly while writing or polling the wrong hardware register, causing blank displays, failed hotplug, link-training timeouts, unstable high-rate links, bad RX adaptation, or misleading debug output.
- CR2/CR3 prefix mistakes are easy because the same functional families repeat across instances. Programming CR2 when CR3 is intended, or vice versa, can leave the target PHY unconfigured while perturbing another path.
- Alias misuse is dangerous. `LANEX`, `RAWLANEX`, `RAWAONLANEX`, and `SUPX` are not mechanically equivalent to concrete lane or support windows.
- The generated map is asymmetric in this chunk: CR3 lane 0 and lane 3 expose fewer visible lane offsets than lane 1 and lane 2. Refactors that assume all lanes have identical surfaces can introduce invalid references.
- Raw FSM, IRQ clear, ATE, PCS/PMA, firmware, and calibration registers may have side effects. The offset header does not mark read-clear, write-one-to-clear, self-clearing, firmware-owned, or power-domain-limited registers.
- Power, clock, PLL, DCC, CDR, DPLL, VCO, adaptation, signal-detect, and analog override registers are sequencing-sensitive. Incorrect access order or stale override enables can force the PHY away from normal hardware/firmware control.
- This range is a chunk, not a complete file analysis. It starts after earlier CR2 `SUPX` definitions and ends before the rest of the CR3 `LANEX` analog/raw tail, so whole-map claims must be reconciled with adjacent chunk reports.

## Test Signals

Useful validation signals for changes touching this generated header or its consumers include:

- Kernel build coverage for AMDGPU display code that includes `dpcs_4_2_3_offset.h` through DCN 3.1.6 resource initialization.
- Generated-header consistency checks that every consumed `ixDPCSSYS_*` offset has a matching register name in `dpcs_4_2_3_sh_mask.h`.
- Repetition checks across CR3 `LANE1`/`LANE2`, raw lane windows, and always-on lane windows, while allowing the intentional reduced lane 0/lane 3 surfaces seen in this map.
- Version-diff checks against nearby generated DPCS versions to catch unintended address movement, missing aliases, or generator drift.
- Display smoke tests on hardware using this DPCS generation: boot display, hotplug, modeset, link retraining, lane-count changes, link-rate changes, suspend/resume, GPU reset, and power-gating recovery.
- PHY bring-up traces showing correct MPLL lock/calibration, bandgap/reference timing, TX/RX P-state transitions, RX VCO calibration completion, CDR/DPLL lock or frequency readback, DCC acknowledgements, adaptation completion, and signal-detect status.
- Diagnostics exercising RX statistic counters, LBERT, IRQ status/clear/mask, OCLA/UPCS selection, raw FSM monitors, PCS/PMA mirrors, ATE override paths, analog test-bus readback, and firmware calibration/configuration offsets.

## Chunk Notes

This is only the source-tree-aligned chunk report for `subset-b-002384`. It intentionally does not create a final per-file research document for `dpcs_4_2_3_offset.h`; the merge/reconciliation lane should combine this report with adjacent chunks before making complete-file statements.
