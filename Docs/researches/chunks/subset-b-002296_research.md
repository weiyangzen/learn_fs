# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 19123-21539

## Scope

This chunk is a middle segment of the generated AMD DPCS 4.2.0 shift/mask header. It covers line 19123 through line 21539 and defines 2,101 preprocessor constants: 1,058 `__SHIFT` macros and 1,043 `_MASK` macros across 317 visible register groups. The uneven count is expected for this slice because the range ends inside `DPCSSYS_CR0_SUPX_DIG_ANA_MPLLB_OVRD_OUT_0`; the remaining masks for that register continue after line 21539. The range starts cleanly at `DPCSSYS_CR0_RAWAONLANE2_DIG_RX_DCC_CAL_ICM_CODE_0`.

The content is declarative only. It exports symbolic bitfield positions for memory-mapped DPCS CR0 lane/common/supervisor registers and contains no C functions, structs, enums, runtime storage, loops, or branches.

## Purpose

The header provides machine-generated bit shift and mask constants for AMDGPU display code that programs the DPCS 4.2.0 display PHY/register surface. Consumer code combines these macros with companion register-offset macros from `dpcs_4_2_0_offset.h` and AMD display register helpers to read, compose, update, and decode hardware register fields without embedding raw numeric bit positions in driver logic.

This specific chunk covers:

- The tail of CR0 always-on lane 2 calibration and control fields.
- A complete CR0 always-on lane 3 field surface for RX adaptation, DFE/AFE calibration, fast bring-up flags, overrides, signal-detect, DCC calibration, firmware configuration, and lane transceiver mode.
- A matching `RAWAONLANEX` generic lane template block with the same field families as lane 3.
- CR0 `SUPX` common/supervisor digital and analog fields for reference clock override, MPLLA/MPLLB override and ASIC inputs, SSC programming, charge-pump controls, bandgap, prescaler, RTUNE, PLL power-control state/timers/calibration, and analog PLL override outputs.

## Exported API Surface

There are no callable APIs or local types. The public surface is the generated macro namespace:

- `DPCSSYS_CR0_RAWAONLANE2_DIG_*`: remaining lane-2 RX DCC calibration codes, TX DCC bank address/data/control, MPLL bandgap control, signal-detect override/readback, firmware config, transceiver mode override/readback, RX signal-detect filter config, and TX DCC config.
- `DPCSSYS_CR0_RAWAONLANE3_DIG_*`: lane-3 AFE/DFE offsets, RX IQ/ATT/VGA/CTLE/DFE adaptation status, phase adjustment, MPLLA/MPLLB coarse tune, initial power-up done bits, fast calibration/adaptation flags, adaptive control windows, MPLL disable, common calibration status, TX/RX overrides, signal-detect calibration/status, DCC codes, firmware config, and lane mode fields.
- `DPCSSYS_CR0_RAWAONLANEX_DIG_*`: generic lane-X equivalents of the lane-3 definitions, useful where generated code wants a lane-agnostic register template.
- `DPCSSYS_CR0_SUPX_DIG_*`: supervisor digital identification, refclock override, MPLLA/MPLLB div/HDMI clock overrides, PLL override input sets, SSC peak/step-size fields, charge-pump overrides, supervisor/prescaler/lane-level overrides, ASIC input mirrors, PLL power-control status/timers/calibration, bandgap/ref clock power-up timing, RTUNE configuration/status/set values, and analog MPLL override output fields.
- `DPCSSYS_CR0_SUPX_ANA_*`: supervisor analog prescaler, RTUNE, bandgap, MPLLA/MPLLB miscellaneous/override/ATB/control/reserved fields.

Most registers expose a predictable pair pattern: `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. Reserved fields are also generated, so consumers can preserve or explicitly mask reserved bits during read-modify-write sequences.

## Register Areas Covered

The lane-local part of the chunk describes RX adaptation and calibration state. Lane 3 and the lane-X template include AFE ATT/CTLE IDAC offsets, RX figure-of-merit and adaptation-done status, DFE summer/phase/data/bypass/error offset readbacks, DFE tap status, slicer controls, IQ phase adjustment, RX signal-detect thresholds and filters, LF/HF signal-detect tune codes, VREF generator enable/calibration, RX DCC calibration code families, and TX DCC bank access/configuration. Fast flags name the accelerated calibration steps that hardware or firmware can bypass or shorten, such as startup calibration, AFE/DFE calibration, reference-level calibration, IQ calibration, continuous adaptation, TX common-mode, RX detect, power-up, VCO wait, and VCO calibration.

The lane override groups expose control/readback bits for TX/RX mode selection, power-up and request handshakes, reset and rate changes, RX adaptation request/disable, serial loopback, PMA signal-detect enable and output, data-enable override, and lane transceiver mode. These are the fields most likely to be touched by low-level PHY bring-up, debug, validation, or firmware-assisted recovery paths.

The `SUPX` digital block defines common resources shared by lanes: refclock and bandgap overrides, HDMI mode, MPLLA/MPLLB div/HDMI clocks, PLL power and reset/calibration controls, SSC peak and step-size programming, charge-pump proportional/integral/gearshift controls, supervisor/prescaler/lane-level overrides, ASIC-facing mirrors, and readback/status fields. The MPLL power-control sub-blocks for MPLLA and MPLLB include override controls, finite-state-machine status, lane ownership/status bits, lock/readback bits, DAC range/input, lock and stable timing, gearshift/preset timing, PCLK enable/disable/powerdown timing, calibration override, analog DAC output, and SSC spread type.

The `SUPX` analog block mirrors the same common domain from the analog side: prescaler controls, RTUNE controls, bandgap controls and measurement switches, MPLLA/MPLLB misc/control/override/ATB fields, and reserved analog registers. These definitions are still plain masks, but their names indicate direct coupling to PLL, bias, termination, and measurement circuitry.

## Control Flow And State Behavior

This file has no local control flow. Runtime behavior emerges when AMD display code includes the generated header and uses the constants through register helper macros for direct MMIO or indexed CR register access.

The field names imply several hardware state machines and handshakes:

- Lane bring-up and recovery: `INIT_PWRUP_DONE`, `PH2_PWRUP_DONE`, `LANE_XCVR_MODE`, `MPLL_DISABLE`, RX/TX reset/request/rate/pstate/adapt bits, and RX/TX override enables participate in lane power and mode sequencing.
- RX adaptation: ATT/VGA/CTLE/DFE tap fields, adaptation figure-of-merit, adaptation-done status, DFE offset readbacks, slicer controls, and fast-adaptation flags expose the state of receive equalization and calibration.
- Signal detection and VREF/DCC calibration: LF/HF signal-detect thresholds and tune codes, signal-detect override/readback, RX VREF generator fields, RX DCC calibration codes, and TX DCC bank address/data/control fields support calibration workflows.
- Common PLL and clocking: refclock override, MPLLA/MPLLB clock enable, HDMI/div clocks, SSC peak/step-size, charge pump, PLL power-control status, lock/stable timers, PCLK timing, calibration override, and analog override outputs define the common clock domain that lanes depend on.
- RTUNE and bandgap: RTUNE config/status/set/stat fields plus bandgap/ref power-up timers describe shared analog calibration and power sequencing.

No software persistence is implemented here. Hardware register contents persist according to ASIC reset and power domains. Fields named `*_STAT`, `*_STATUS`, `*_OUT`, `*_ASIC_IN`, and `*_DONE` are readback/status-oriented by name, while `*_OVRD_IN`, `*_OVRD_EN`, `*_SET_VAL`, timer, calibration, and config fields are writable controls by name; this header does not encode those access permissions.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, this chunk is paired with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h`, which supplies the `ix...` register addresses for the fields defined here.

The direct include site in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, which includes both `dpcs_4_2_0_offset.h` and `dpcs_4_2_0_sh_mask.h`. That resource file builds DCN31 link encoder register, shift, and mask tables using `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST`. The specific macros in this slice are not all surfaced through those high-level DCN31 lists, but they are part of the same generated DPCS 4.2.0 namespace available to display, PHY, diagnostics, and bring-up code.

Related integration points include:

- AMD DC link encoder and HPO DP link encoder code that programs DPCS/RDPCS PHY and clock resources.
- Register helper macros such as `LE_SF`, `SRI`, `SRI_IX`, and generated register-list macros that map shifts and masks into driver tables.
- DisplayPort/HDMI link training, low-level PHY programming, suspend/resume, hotplug recovery, DP Alt Mode coordination, and hardware validation flows that need lane or common PLL state.
- Firmware or debug paths that use CR access windows and override fields to inspect or force PHY state.

## Risks

- Generated-header drift is the main risk. A wrong shift or mask can silently target adjacent analog or PLL bits during read-modify-write operations.
- This slice contains repeated lane-specific and lane-template definitions. Copy-generation mistakes can affect only lane 2, lane 3, or the generic lane-X template, making failures lane-dependent and difficult to reproduce.
- The chunk mixes writable controls with status/readback fields by name. Consumers must rely on the hardware register specification and surrounding driver policy to avoid writing status-only, clear-on-read, or reserved bits.
- Override-enable patterns are common. Setting an override value without its matching enable bit, or leaving an enable bit asserted after recovery/debug work, can hold the PHY in a forced state across link training or resume.
- PLL, SSC, charge-pump, RTUNE, bandgap, and power-up timer masks affect shared analog resources. Incorrect writes can destabilize all lanes served by the common block, not just one link.
- Full-width or broad `data`, reserved, ASIC input, and analog-reserved masks provide little semantic validation in C. Values need to come from hardware tables or firmware-approved sequences, not arbitrary driver state.
- The range ends in the middle of `DPCSSYS_CR0_SUPX_DIG_ANA_MPLLB_OVRD_OUT_0`; chunk-level validation must account for the remaining masks in the next chunk rather than reporting missing fields as source corruption.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-integration oriented:

- Compile or preprocess AMDGPU display code for DCN31 targets that include `dpcs_4_2_0_offset.h` and `dpcs_4_2_0_sh_mask.h`.
- Static generation checks that every complete register in the full file has matching `__SHIFT` and `_MASK` definitions, with this chunk boundary allowing the partial `MPLLB_OVRD_OUT_0` mask list.
- Consistency checks between this header and the DPCS 4.2.0 register database, especially for repeated `RAWAONLANE3` and `RAWAONLANEX` groups.
- Grep/compile checks for renamed or missing DPCS fields consumed by DCN31 resource and link encoder register-table macros.
- Hardware tests on DPCS 4.2.0/DCN31-class ASICs: DP and HDMI link training, link-rate changes, lane power-state transitions, hotplug, suspend/resume, RX detect/signal-detect behavior, PLL lock, SSC programming, and recovery from failed link training.
- Register readback during bring-up to confirm `INIT_PWRUP_DONE`, adaptation done/FOM/tap values, signal-detect outputs, MPLL lock/status, RTUNE stat values, bandgap/ref power-up timing behavior, and override enable cleanup.

## Chunk Notes For Merge

This document is intentionally source-tree aligned and covers only lines 19123-21539 of `dpcs_4_2_0_sh_mask.h`. Earlier chunks should cover the lower CR0, PWRSEQ, RDPCS, RAWLANE, RAWCMN, and beginning of lane-2 definitions. Later chunks should continue `DPCSSYS_CR0_SUPX_DIG_ANA_MPLLB_OVRD_OUT_0` and the remaining DPCS 4.2.0 register groups. The final per-file merge should describe the whole file as a generated ASIC register bitfield map used by AMD display code, not as handwritten runtime logic.
