# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002381`: lines 1-2484, `Docs/researches/chunks/subset-b-002381_research.md`
- `subset-b-002382`: lines 2485-4870, `Docs/researches/chunks/subset-b-002382_research.md`
- `subset-b-002383`: lines 4871-7256, `Docs/researches/chunks/subset-b-002383_research.md`
- `subset-b-002384`: lines 7257-9642, `Docs/researches/chunks/subset-b-002384_research.md`
- `subset-b-002385`: lines 9643-11969, `Docs/researches/chunks/subset-b-002385_research.md`

## Chunk Research

### subset-b-002381: lines 1-2484

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h lines 1-2484

## Purpose

This chunk is generated AMD DPCS 4.2.3 register-offset metadata. It contains no executable C logic; it publishes preprocessor constants that map symbolic DisplayPort/Display PHY Control Subsystem register names to numeric offsets and, for direct MMIO registers, matching `_BASE_IDX` selectors. The values are consumed by AMDGPU display code to build register tables for DCN 3.1.6-class hardware.

The requested range is the first 2,484 lines of a larger 11,969-line header. It covers the license/header guard, direct MMIO offsets for DPCSSYS CR apertures, panel power sequencers, RDPCS transmitters/pipes, DCIO, GPIO, and UNIPHY reserved macro-control blocks, then begins the `dpcssys_cr0_rdpcstxcrind` indirect register address map. In this range there are 2,373 `#define` lines. The direct-register portion consistently pairs `reg...` offsets with `reg..._BASE_IDX`, and every direct `_BASE_IDX` in this chunk is `2`. The indirect CR-register portion uses `ixDPCSSYS_CR0_...` index constants without `_BASE_IDX` companions because those values are written through CR address/data windows rather than used as standalone MMIO offsets.

Although the path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, allocation paths, or locking primitives in this range. The interface is the generated macro namespace:

- `reg<block>_<register>`: a direct MMIO register offset in the DPCS/DCIO register space.
- `reg<block>_<register>_BASE_IDX`: the base-address segment selector used by register helper macros when computing an absolute MMIO address.
- `ixDPCSSYS_CR0_<register>`: an indirect CR register index for the CR0 RDPCS transmitter/PHY register window.

Major direct-register families in this slice:

- `regDPCSSYS_CR0` through `regDPCSSYS_CR4`: CR address/data access windows at repeated link offsets, each exposing `DPCSSYS_CR_ADDR` and `DPCSSYS_CR_DATA`.
- `regPWRSEQ0` and `regPWRSEQ1`: panel power-sequencer GPIO enable/control/mask/Y registers, panel power state/control/delay/reference-divider registers, backlight PWM control/period/lock registers, and spare registers.
- `regRDPCSTX0` through `regRDPCSTX4`: repeated RDPCS transmitter blocks for control, clock control, interrupt control, PLL update data, CR address/data access, SRAM control, scratch/spare/debug, PHY control registers 0-17, PHY fuse registers, DPALT/DMCU controls, `DPALT_CONTROL_REG`, `RDPCS_CNTL3`, and PLL update override address/data.
- `regRDPCSPIPE0` and `regRDPCSPIPE1`: pipe-level `RDPCSPIPE_PHY_CNTL6`. The chunk also contains explicit bring-up aliases for `regRDPCSPIPE2`, `regRDPCSPIPE3`, and `regRDPCSPIPE4`, with an in-file comment that the driver should not need RDPCS registers after bring-up cleanup.
- `regDC_*`, `regDCIO_*`, `regUNIPHYA` through `regUNIPHYE`, `regINTERCEPT_STATE`, `regPHY_AUX_CNTL`, and `regAUXI2C_PAD_ALL_PWR_OK`: DCIO clock/reference/pinstrap/reset/debug/link-routing registers, UNIPHY link and channel crossbar controls, GPIO mask/data/enable/Y registers for generic/DDC/HPD/genlock/power-sequencer pads, pad strength, AUX controls, pull-ups, RX enable, and AUX/I2C power-good state.
- `regDCIO_UNIPHY1` through `regDCIO_UNIPHY4`: each exposes `UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED57` as contiguous direct offsets for macro-level control/reserved slots.

The indirect CR0 table begins at line 1229 and includes:

- `ixDPCSSYS_CR0_SUP_DIG_*` and `ixDPCSSYS_CR0_SUP_ANA_*`: supervisor digital/analog ID, refclk override, MPLLA/MPLLB override, spread-spectrum, prescaler, ASIC input/status, bandgap, charge pump, power timing, RTUNE, and analog status indices.
- `ixDPCSSYS_CR0_LANE0` through partial `LANE3`: per-lane ASIC override/input/output, TX power-state and DCC controls, RX power/VCO/CDR/adaptation/status controls, LBERT, DPLL, MPHY, analog TX/RX override/status/calibration/measurement controls. The chunk covers full lane 0, lane 1, lane 2, and the TX/status-oriented beginning of lane 3.
- `ixDPCSSYS_CR0_RAWCMN_*`: common raw PCS/PHY control, MPLL override, SSC, lane FSM, SRAM init, OCLA, firmware/PCS ID, always-on RTUNE values, power-gating, VREF, resistor, and reference-range controls.
- `ixDPCSSYS_CR0_RAWLANE0` through partial `RAWLANE3`: PCS/PMA cross-interface overrides, RX adaptation and lane-numbering controls, FSM status/fast calibration controls, IRQ/status/clear/mask controls, PMA override/monitor registers, TX/RX control/status, and ATE/debug indices.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by the AMDGPU display driver:

1. DCN 3.1.6 resource code includes this file together with `dpcs_4_2_3_sh_mask.h`.
2. Resource/register table macros paste block names and instance IDs into constants such as `regRDPCSTX0_RDPCSTX_PHY_CNTL6`, `regPWRSEQ0_PANEL_PWRSEQ_CNTL`, or `ixDPCSSYS_CR0_LANE1_DIG_RX_CDR_CDR_CTL_0`.
3. Direct `reg...` values are combined with their `_BASE_IDX` segment to access MMIO registers through the driver register helpers.
4. Indirect `ix...` values are used as CR indices behind the CR address/data windows exposed by `regDPCSSYS_CR*_DPCSSYS_CR_ADDR`, `regDPCSSYS_CR*_DPCSSYS_CR_DATA`, and the equivalent RDPCS TX CR address/data aliases.
5. Higher-level display code performs the actual ordering for power sequencing, link enablement, PHY setup, PLL updates, DisplayPort/alternate-mode training, interrupt handling, and diagnostic reads.

The macros do not encode access permissions, timing, polling, read-modify-write masks, or side effects. Consumers must pair them with the matching shift/mask header and the hardware programming sequence for the active ASIC.

## State And Persistence Behavior

The chunk stores no software state and persists nothing to disk. It describes hardware state reachable through MMIO and CR-indirect access windows. The represented state includes:

- Panel/backlight sequencing state: GPIO ownership, panel power targets/current state, delay counters, PWM control/period/locking, and power-sequencer reference dividers.
- RDPCS transmitter and PHY state: clocks, interrupts, PLL update data/overrides, SRAM control, debug/scratch registers, PHY control and fuse-visible values, DPALT controls, and CR address/data windows.
- DCIO and GPIO state: DCIO clock/reference control, pinstraps, soft reset, link/channel crossbar mapping, genlock/swaplock pads, DDC/HPD/generic/power-sequence GPIO masks/data/enables/Y values, pad strengths, AUX controls, RX/pull-up enables, and pad power-good status.
- UNIPHY macro-control reserved state for several repeated PHY instances.
- CR0 supervisor/lane/common/raw-lane state: MPLL and spread-spectrum controls, power timing, RTUNE calibration, analog status, lane TX/RX power/CDR/VCO/adaptation/calibration, FSM and interrupt status, PMA/PCS override paths, and test/debug controls.

Persistence is hardware-defined. Configuration registers may retain values until modeset, power gating, suspend/resume, link reset, or ASIC reset. Status, interrupt, clear, calibration, debug, and override registers can be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive. This offset header does not identify those semantics; field definitions and consuming code determine correct access patterns.

## Dependencies And Integration Points

This chunk depends on AMD's generated DPCS 4.2.3 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h` for field shifts and masks.
- SOC/DCN base-address definitions used by AMDGPU register helpers to interpret `_BASE_IDX == 2`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which directly includes this offset header and the matching shift/mask header.

The broader integration pattern is generated-register token pasting. DCN resource code initializes register structures from symbolic names; HPO DP link encoder and panel-control paths consume RDPCS, DPCSSYS, DCIO, GPIO, and PWRSEQ register definitions through those structures. The companion mask header supplies fields such as RDPCS PHY DP alternate-mode disable bits and panel power-sequencer/backlight bits, while this file supplies only numeric addresses or CR indices.

The CR-indirect names are especially tied to the direct CR access windows in the same chunk: a driver must program an `ixDPCSSYS_CR0_*` index through the appropriate `DPCSSYS_CR_ADDR`/`DPCSSYS_CR_DATA` or RDPCS TX CR address/data pair for the target PHY instance. Using an `ix...` constant as a direct MMIO offset would be wrong.

## Risks And Edge Cases

- Offset or base-index drift is the central risk. These macros are untyped constants, so an incorrect address or `_BASE_IDX` can compile cleanly while targeting the wrong hardware register.
- Direct and indirect namespaces are easy to confuse. `reg...` constants are MMIO offsets with base-index companions; `ix...` constants are CR indices. Mixing the two access mechanisms can corrupt unrelated registers or fail silently.
- Repeated instance blocks are copy-sensitive. `CR0`-`CR4`, `RDPCSTX0`-`RDPCSTX4`, `PWRSEQ0`-`PWRSEQ1`, `UNIPHY1`-`UNIPHY4`, lanes, and raw lanes have regular spacing but are not interchangeable in a live modeset. Instance mistakes may only appear on a particular connector, lane count, panel path, or DP alternate-mode path.
- The `RDPCSPIPE2`-`RDPCSPIPE4` aliases are explicitly marked as bring-up hacks. Code that grows new dependencies on those aliases would preserve temporary hardware access assumptions and could break when the generated map or cleanup changes.
- Power-sequencing and GPIO registers are side-effect-sensitive. Wrong masks, enables, delays, or PWM/register-lock offsets can cause blank eDP panels, backlight failures, bad HPD/DDC/AUX behavior, or suspend/resume regressions.
- PHY and CR-indirect controls affect high-speed link training and calibration. Bad MPLL, RTUNE, DCC, CDR, VCO, RX adaptation, or lane override addresses can produce intermittent link failures, rate/lane-specific instability, DisplayPort alternate-mode failures, or diagnostics that only fail on certain boards.
- The chunk boundary is artificial. It stops inside the `RAWLANE3` CR0 raw-lane register table; adjacent chunks are required for the full `dpcs_4_2_3_offset.h` map and for any file-level conclusions about all DPCS instances.

## Test Signals

- Compile coverage for `dcn316_resource.c` and any generated register tables that include `dpcs_4_2_3_offset.h` is the baseline signal; missing or renamed macros should fail at build time.
- Static consistency checks are valuable: each direct `reg...` macro in this chunk should have a matching `_BASE_IDX`, all direct base indices in this slice should remain `2`, repeated instance blocks should preserve expected spacing, and `ix...` CR indices should not be paired with `_BASE_IDX`.
- Boot and modeset tests on DCN 3.1.6 hardware should exercise connector detection, HPD, DDC/EDID, AUX/DPCD access, eDP panel power sequencing, backlight PWM, suspend/resume, and multi-display routing through the DCIO/UNIPHY/RDPCS tables.
- DisplayPort link-training tests should cover multiple link rates and lane counts, DP alternate-mode paths, hotplug cycles, and error recovery so RDPCS TX, PLL, PHY, CR-indirect, raw-lane, and interrupt offsets are exercised.
- Hardware diagnostics should watch for register read/write timeouts, AUX failures, link-training failures, HPD storms, blank panels, missing backlight, PHY calibration errors, and lane-specific instability. These are the practical failure signatures for incorrect offsets in this header.

### subset-b-002382: lines 2485-4870

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h lines 2485-4870

## Scope

This chunk is a generated AMD DPCS 4.2.3 offset-header segment. It covers 2,386 source lines and 2,382 `#define` constants. Every definition in this selected range is an indexed DPCSSYS register offset named with the `ixDPCSSYS_...` convention; there are no C functions, structs, enums, storage objects, branches, loops, or executable statements.

The range starts inside the `DPCSSYS_CR0_RAWLANE3` raw-lane table, at the RX control/PCS ATE tail. It then covers complete CR0 raw always-on lane blocks for lanes 0 through 3 and `RAWAONLANEX`, the CR0 support-X (`SUPX`) block, the CR0 lane-X (`LANEX`) broadcast/template block, and the CR0 raw-lane-X (`RAWLANEX`) block. The chunk then crosses into the CR1 indexed map and covers the CR1 support block, lane 0 tail, full lane 1 and lane 2 blocks, lane 3 tail, raw common (`RAWCMN`), raw lane 0 through 3 blocks, raw always-on lane 0 and lane 1 blocks, and the beginning of raw always-on lane 2. The next chunk continues CR1 raw always-on lane 2 at `DIG_RX_DCC_CAL_ICM_CODE_0`.

Observed macro-family counts in this chunk include:

- `CR0_RAWLANE3`: 13 tail entries from `DIG_RX_CTL_RX_DATA_EN_OVRD_CTL` through `DIG_PCS_XF_TX_OVRD_IN_2`.
- `CR0_RAWAONLANE0/1/2/3/RAWAONLANEX`: 82 entries each, `0x4000-0x4051`, `0x4100-0x4151`, `0x4200-0x4251`, `0x4300-0x4351`, and `0x7000-0x7051`.
- `CR0_SUPX`: 139 support broadcast entries around `0x8000-0x8096`.
- `CR0_LANEX`: 203 lane broadcast/template entries around `0x9000-0x90ff`.
- `CR0_RAWLANEX`: 125 raw lane-X entries around `0xe000-0xe0c8`.
- `CR1_SUP`: 139 entries around `0x0000-0x0096`.
- `CR1_LANE0/3`: 85 tail sections each; `CR1_LANE1/2`: 203 full lane blocks each.
- `CR1_RAWCMN`: 52 entries around `0x2000-0x2040`.
- `CR1_RAWLANE0/1/2/3`: 125 entries each around `0x3000-0x33c8`.
- `CR1_RAWAONLANE0/1`: 82 entries each, plus the first 61 entries of `CR1_RAWAONLANE2`.

## Purpose

`dpcs_4_2_3_offset.h` gives AMDGPU display code symbolic names for DPCS 4.2.3 indirect register offsets. The top of the file defines `regDPCSSYS_CR*_DPCSSYS_CR_ADDR` and `regDPCSSYS_CR*_DPCSSYS_CR_DATA` MMIO address/data windows; the `ixDPCSSYS_*` constants in this chunk are the internal offsets selected through those windows, not final CPU virtual addresses.

This chunk maps low-level display PHY register spaces for the DCN316-era DPCS 4.2.3 block. The constants cover link-lane power and reset controls, PLL/support registers, raw PCS/PMA state-machine controls, IRQ status/clear/mask registers, RX adaptation and signal-detect calibration, TX DCC controls, analog TX/RX override/status registers, and broadcast/template aliases used by register-list generation.

## Important APIs, Types, And Macros

There are no callable APIs or local C types. The exported interface is the preprocessor macro namespace:

- `ixDPCSSYS_CR0_*` and `ixDPCSSYS_CR1_*`: indirect register offsets for DPCS CR instance 0 and CR instance 1.
- `*_SUP` and `*_SUPX`: common support/supervisor register spaces for IDCODE, reference clock, MPLLA/MPLLB override, SSC, charge pump, ASIC feedback, prescaler, bandgap, RTUNE, MPLL power/timing/calibration, and analog override/status registers.
- `*_LANE0` through `*_LANE3`: per-lane digital and analog register offsets.
- `*_LANEX`: lane-X broadcast or template aliases for the same lane register layout.
- `*_RAWCMN`: raw always-on common control for RTUNE, SRAM boot/load, power gate, resets, supply/reference/MPLL request and acknowledge plumbing, monitor inputs, VREF state, and MPLL powerdown timing.
- `*_RAWLANE0` through `*_RAWLANE3` and `*_RAWLANEX`: raw per-lane PCS/FSM/IRQ/PMA/TX/RX/ATE offsets.
- `*_RAWAONLANE0` through `*_RAWAONLANE3` and `*_RAWAONLANEX`: raw always-on per-lane offsets for RX adaptation results, DFE/slicer/phase state, signal-detect calibration, DCC, firmware calibration/configuration, and lane transceiver mode control.

The names encode functional areas rather than software abstractions. Common groups in this chunk include `DIG_PCS_XF`, `DIG_FSM`, `DIG_IRQ_CTL`, `DIG_PMA_XF`, `DIG_TX_CTL`, `DIG_RX_CTL`, `DIG_AON_CMN`, `DIG_ASIC_*`, `DIG_TX_PWRCTL`, `DIG_RX_PWRCTL`, `DIG_RX_VCOCAL`, `DIG_RX_CDR`, `DIG_RX_DPLL`, `DIG_RX_ADPTCTL`, `DIG_RX_STAT`, `DIG_MPHY`, `DIG_ANA_*`, `ANA_TX_*`, `ANA_RX_*`, `MPLLA`, `MPLLB`, `RTUNE`, `BG`, `ATB`, `DCC`, `SIGDET`, and firmware calibration/configuration groups.

## Register Areas Covered

The opening `CR0_RAWLANE3` tail completes the raw lane 3 RX controller and PCS ATE window. It includes RX data-enable override, off-cancel/adaptation continuous status, UPCS observability, ATE RX/TX override inputs, master MPLL loop control, and late PCS override outputs.

The CR0 raw always-on lane blocks expose a compact repeated 82-register layout for each lane and for the lane-X alias. They include RX AFE/CTLE/DFE offset and reference-level readbacks, phase and IQ adjustment state, MPLLA/MPLLB coarse tune, initial power-up done, adaptation status for ATT/VGA/CTLE/DFE taps, slicer controls, common-calibration status, adaptation control registers, MPLL disable, fast flags, TX/RX override input, LOS and signal-detect filtering/calibration, DCC calibration codes, TX DCC bank address/data/control, MPLL bandgap control, firmware mode/adaptation/calibration config, lane transceiver mode override/input, RX signal-detect config, and TX DCC config.

The CR0 `SUPX` support block maps broadcast-style support offsets from identification and refclk override through MPLLA/MPLLB control. It covers SSC peak/step registers, ASIC input/output feedback for both PLLs, prescaler and bandgap analog controls, MPLLA/MPLLB analog controls and ATB readouts, digital MPLL power-control/timing/status/calibration registers, reference and clock/reset timing controls, RTUNE configuration/status, and analog override/status outputs for MPLLs, RTUNE, bandgap, and PMIX.

The CR0 `LANEX` block is a lane broadcast/template view of the full lane register schema. It starts with ASIC override/input/output windows, then covers TX power-state and power-up timing registers, TX DCC DAC programming and acknowledgement, TX clock alignment and LBERT controls, RX power-state and timing registers, RX VCO calibration, RX alignment and LBERT, CDR and DPLL controls, RX adaptation configuration/status/DAC-selector/banked access, RX statistics controls and counters, MPHY low-speed controls, digital analog override/status outputs, and direct analog TX/RX control and measurement registers through reserved analog slots.

The CR0 `RAWLANEX` block provides a lower-level lane-X view of PCS/PMA/FSM state. It includes PCS TX/RX override/input/output and adaptation-direction registers, FSM fast-start/calibration/adaptation status, CR lock and DCC status, lane IRQ status/clear/mask registers, PMA crossbar override/input/output and RTUNE controls, TX/RX controller status/OCLA windows, and PCS ATE override registers.

The CR1 portion repeats the same generated DPCS schema for CR instance 1. `CR1_SUP` covers the ordinary support space; `CR1_LANE1` and `CR1_LANE2` are full per-lane digital/analog maps; lane 0 and lane 3 appear as partial tail sections in this chunk. The CR1 raw common and raw lane blocks cover common always-on control, raw PCS/FSM/IRQ/PMA/TX/RX/ATE windows for all four lanes, and the start of raw always-on lane status/configuration for lanes 0, 1, and 2.

## Control Flow

This header contributes no runtime control flow. Runtime sequencing is in AMD display/DC and link encoder code that selects these offsets, combines them with matching shift/mask metadata from `dpcs_4_2_3_sh_mask.h`, and performs MMIO or indirect DPCS CR address/data accesses.

The hardware workflows implied by the register names are sequencing-sensitive:

- PHY/link bring-up and shutdown through support, MPLL, RTUNE, clock/reset, SRAM boot/load, and TX/RX P-state registers.
- Per-lane request/acknowledge handshakes through raw PCS/PMA and ASIC input/output windows.
- RX receiver calibration through VCO, CDR, DPLL, AFE/CTLE/DFE, slicer, phase/IQ, signal-detect, and adaptation-control offsets.
- TX calibration through DCC DAC/bank/control registers, clock alignment, and power-state timing.
- Interrupt lifecycle through raw lane IRQ status, clear, and mask offsets.
- Lab/manufacturing/debug paths through ATE, ATB, OCLA, LBERT, raw analog override/status, and firmware calibration/configuration registers.

## State And Persistence Behavior

The file is stateless compile-time data. It has no memory ownership, persistence, locks, allocation, initialization, or teardown.

The mutable state described by these offsets lives in volatile DPCS hardware registers. That state can be changed by display initialization, DisplayPort/HDMI link training, modesets, hotplug handling, suspend/resume, GPU reset recovery, PHY power gating, firmware-mediated sequences, and debug or manufacturing tools. Some status registers latch calibration, adaptation, IRQ, DCC acknowledgement, PLL, and signal-detect results until read, cleared, reset, or power-cycled according to hardware rules that are not encoded in this offset header.

Because many entries are override controls, a write through the wrong offset can persistently redirect hardware away from normal state-machine control until the register is restored or the relevant reset/power-domain transition occurs. Reserved analog/digital offsets are part of the hardware contract and should not be treated as scratch space.

## Dependencies

The direct syntactic dependency is the C preprocessor. The semantic dependency is AMD's generated DPCS 4.2.3 register database remaining synchronized with the ASIC hardware specification.

Important companion inputs are:

- `dpcs_4_2_3_sh_mask.h`, which supplies matching bitfield shift and mask definitions for the register names defined here.
- The top-level `regDPCSSYS_CR*_DPCSSYS_CR_ADDR` and `regDPCSSYS_CR*_DPCSSYS_CR_DATA` definitions in the same header, which provide the address/data windows for indirect CR access.
- AMD display register-helper macros that token-paste generated register names into resource tables and issue the actual read/write operations.
- Neighboring generated DPCS versions such as `dpcs_4_2_0_offset.h`, `dpcs_4_2_2_offset.h`, and `dpcs_3_1_4_offset.h`, which share many schemas and are useful for validating intended generation-to-generation deltas.

This imported Linux GPU driver subtree is under a repository named for Ceph learning, but this file has no direct dependency on Ceph filesystem logic.

## Integration Points

In this tree, `drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` directly includes both `dpcs/dpcs_4_2_3_offset.h` and `dpcs/dpcs_4_2_3_sh_mask.h`. That resource file also defines DPCS base segments, expands `DPCS_DCN31_REG_LIST(id)` and `DPCS_DCN31_MASK_SH_LIST(...)`, and instantiates `DCN3_1_RDPCSTX_REG_LIST(0)` through `DCN3_1_RDPCSTX_REG_LIST(4)`. This ties the generated DPCS 4.2.3 offset contract to DCN316 display resource construction and link encoder register tables.

Consumers must pair the correct CR instance, lane, and broadcast form. A `CR1_LANE2` offset is not interchangeable with a `CR0_LANEX` or `CR1_RAWLANE2` offset even when suffixes look similar. `SUPX`, `LANEX`, `RAWLANEX`, and `RAWAONLANEX` forms are broadcast/template-style aliases and can have wider effect or lane-selection requirements that are not visible from the numeric macro alone.

## Risks

- A single wrong numeric offset can compile cleanly but send a PHY read or write to the wrong internal register, causing display link failures, PLL instability, failed calibration, or misleading diagnostics.
- The chunk starts and ends inside larger logical tables. The previous chunk is needed for the earlier `CR0_RAWLANE3` entries, and the next chunk is needed to complete `CR1_RAWAONLANE2` and later CR1/CR2/CR3/CR4 material.
- The register map is dense and repetitive. Lane blocks differ mostly by lane number and offset page, so generated drift or manual copy errors can create lane-specific failures that are hard to isolate.
- Raw lane, ATE, analog override, and firmware calibration/configuration registers can bypass or perturb normal hardware state machines. Leaving override enables asserted after diagnostics can break later link training, hotplug recovery, suspend/resume, or GPU reset recovery.
- IRQ status, IRQ clear, and IRQ mask offsets are adjacent and similarly named, but their access semantics differ. The offset header does not encode write-one-to-clear behavior, mask polarity, ordering requirements, or polling timeouts.
- Field-level safety depends on the matching shift/mask header. Offset/mask name mismatches or version mixing can apply valid-looking bit operations to the wrong DPCS generation or register.
- Reserved analog and digital offsets are exposed as names. They should not be programmed unless hardware documentation explicitly requires it.

## Test Signals

Useful validation signals for changes touching this generated header or code that consumes it include:

- Build coverage for DCN316 AMDGPU display code, especially `dcn316_resource.c` and link encoder/resource-table initialization that includes `dpcs_4_2_3_offset.h` with `dpcs_4_2_3_sh_mask.h`.
- Static consistency checks that each register-name offset used by generated register-list macros has corresponding shift/mask metadata where field access is expected.
- Version-diff checks against adjacent DPCS generated headers to catch accidental movement of repeated lane/support/raw-lane offsets.
- Hardware display bring-up on DCN316-class systems, including boot display, hotplug, DisplayPort link training, HDMI/TMDS paths, multi-monitor modesets, suspend/resume, and GPU reset recovery.
- PHY diagnostics or lab tests that exercise MPLLA/MPLLB setup, RTUNE, TX/RX P-state transitions, DCC calibration, RX VCO/CDR/DPLL/adaptation, signal-detect calibration, raw lane IRQ handling, LBERT/OCLA/ATE paths, and analog override/status readback.

## Cross-Chunk Notes

Chunk `subset-b-002381` covers the beginning of `dpcs_4_2_3_offset.h` through line 2484 and is needed to understand the full CR0 address windows and earlier CR0 raw-lane material. This chunk (`subset-b-002382`) runs from line 2485 through line 4870 and ends after `ixDPCSSYS_CR1_RAWAONLANE2_DIG_CAL_VREFGEN_CODE`. Chunk `subset-b-002383` should continue at `ixDPCSSYS_CR1_RAWAONLANE2_DIG_RX_DCC_CAL_ICM_CODE_0` and complete the rest of the CR1 raw always-on and later register-map sections.

### subset-b-002383: lines 4871-7256

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h lines 4871-7256

## Scope

This chunk is a generated AMD DPCS 4.2.3 offset-header segment. It contains C preprocessor constants only: no functions, structs, enums, storage, or executable logic. The visible range starts in the middle of the `ixDPCSSYS_CR1_RAWAONLANE2_*` always-on raw-lane block at `DIG_RX_DCC_CAL_ICM_CODE_0` and ends in the middle of the `ixDPCSSYS_CR2_SUPX_*` supervisor-X block at `DIG_MPLLB_HDMI_CLK_ASIC_IN`.

The constants are DPCS indexed-control-register addresses. Earlier in the same header, each DPCS CR instance has display MMIO address/data ports such as `regDPCSSYS_CR1_DPCSSYS_CR_ADDR`, `regDPCSSYS_CR1_DPCSSYS_CR_DATA`, `regDPCSSYS_CR2_DPCSSYS_CR_ADDR`, and `regDPCSSYS_CR2_DPCSSYS_CR_DATA`. The `ixDPCSSYS_*` values in this chunk are the 16-bit-style indirect addresses written to those address ports before reading or writing the corresponding data port.

## Purpose

The header provides compile-time register-index metadata for AMDGPU display PHY code on the DCN 3.1.6 / DPCS 4.2.3 path. Driver code pairs these offset macros with companion shift/mask macros from `dpcs_4_2_3_sh_mask.h` and with DC register access helpers to configure DisplayPort/HDMI PHY lanes, power states, PLLs, receiver adaptation, signal detection, calibration, and debug/test paths.

Within this chunk, the main hardware areas are:

- CR1 always-on raw lane 2 tail and lane 3 full blocks, covering RX DCC calibration readback, TX DCC bank access/control, MPLL bandgap control, signal-detect override/readback, firmware mode/adaptation/calibration configuration, lane transceiver-mode inputs, and RX signal-detect/TX DCC configuration.
- CR1 `RAWAONLANEX`, the lane-generic always-on raw-lane template at the `0x7000` index range.
- CR1 `SUPX`, the extended supervisor block at `0x8000` through `0x8096`, covering ID, reference-clock overrides, MPLLA/MPLLB override and spread-spectrum registers, charge-pump controls, ASIC inputs, prescaler/bandgap/level controls, analog PLL controls, RTUNE controls/status, and digital analog override/status outputs.
- CR1 `LANEX`, the lane-generic main lane template at `0x9000` through `0x90ff`, covering ASIC override/input/output interfaces, TX/RX power controls, RX VCO/CDR/DPLL, RX adaptation, RX statistics, MPHY, digital analog override/status, and raw analog TX/RX controls.
- CR1 `RAWLANEX`, the lane-generic raw PCS/PMA/FSM/IRQ/control template at `0xe000` through `0xe0c8`.
- CR2 supervisor, lane, raw common, raw lane, always-on raw lane, lane-generic always-on, and early supervisor-X blocks. CR2 coverage begins at the full `SUP` block and continues through lane 0, lane 1, lane 2, lane 3, raw common, raw lanes 0-3, always-on raw lanes 0-3, `RAWAONLANEX`, and the start of `SUPX`.

## Macro Groups

The chunk's generated macro families and line spans are:

- `ixDPCSSYS_CR1_RAWAONLANE2_*` lines 4871-4891: tail of CR1 raw AON lane 2, from RX DCC calibration codes through TX DCC configuration.
- `ixDPCSSYS_CR1_RAWAONLANE3_*` lines 4892-4973: full CR1 raw AON lane 3, `0x4300` through `0x4351`.
- `ixDPCSSYS_CR1_RAWAONLANEX_*` lines 4974-5055: lane-generic CR1 raw AON template, `0x7000` through `0x7051`.
- `ixDPCSSYS_CR1_SUPX_*` lines 5056-5194: CR1 extended supervisor, `0x8000` through `0x8096`.
- `ixDPCSSYS_CR1_LANEX_*` lines 5195-5397: CR1 lane-generic main lane template, `0x9000` through `0x90ff`.
- `ixDPCSSYS_CR1_RAWLANEX_*` lines 5398-5522: CR1 lane-generic raw lane template, `0xe000` through `0xe0c8`.
- `ixDPCSSYS_CR2_SUP_*` lines 5527-5665: CR2 supervisor, `0x0000` through `0x0096`.
- `ixDPCSSYS_CR2_LANE0_*` lines 5666-5750: partial CR2 lane 0 set, `0x1000` through `0x10ef`; this lane has ASIC/TX-power/statistic/analog-TX coverage in this chunk but not the full RX/control breadth visible for lanes 1 and 2.
- `ixDPCSSYS_CR2_LANE1_*` lines 5751-5953: full CR2 lane 1, `0x1100` through `0x11ff`.
- `ixDPCSSYS_CR2_LANE2_*` lines 5954-6156: full CR2 lane 2, `0x1200` through `0x12ff`.
- `ixDPCSSYS_CR2_LANE3_*` lines 6157-6241: partial CR2 lane 3 set, `0x1300` through `0x13ef`.
- `ixDPCSSYS_CR2_RAWCMN_*` lines 6242-6293: CR2 raw common controls, `0x2000` through `0x2040`.
- `ixDPCSSYS_CR2_RAWLANE0_*` through `ixDPCSSYS_CR2_RAWLANE3_*` lines 6294-6793: four CR2 raw lane PCS/PMA/FSM/IRQ/control blocks at `0x3000`, `0x3100`, `0x3200`, and `0x3300` bases.
- `ixDPCSSYS_CR2_RAWAONLANE0_*` through `ixDPCSSYS_CR2_RAWAONLANE3_*` lines 6794-7121: four CR2 always-on raw-lane blocks at `0x4000`, `0x4100`, `0x4200`, and `0x4300` bases.
- `ixDPCSSYS_CR2_RAWAONLANEX_*` lines 7122-7203: CR2 lane-generic always-on raw-lane template, `0x7000` through `0x7051`.
- `ixDPCSSYS_CR2_SUPX_*` lines 7204-7256: beginning of CR2 extended supervisor, `0x8000` through `0x8035`; the following source lines continue this block.

## Important APIs, Types, And Functions

There are no callable APIs in this chunk. The public interface is the generated macro naming contract:

- `ixDPCSSYS_CRn_SUP_*` and `ixDPCSSYS_CRn_SUPX_*` name supervisor indexed-register addresses.
- `ixDPCSSYS_CRn_LANE0_*` through `ixDPCSSYS_CRn_LANE3_*` name concrete per-lane indexed-register addresses.
- `ixDPCSSYS_CRn_LANEX_*`, `ixDPCSSYS_CRn_RAWLANEX_*`, and `ixDPCSSYS_CRn_RAWAONLANEX_*` name lane-generic template addresses.
- `ixDPCSSYS_CRn_RAWLANE*_*` names raw PCS/PMA/FSM/IRQ/control indexed-register addresses for specific lanes.
- `ixDPCSSYS_CRn_RAWAONLANE*_*` names always-on raw-lane indexed-register addresses for calibration/adaptation/signal-detect/DCC state.

The companion shift/mask header supplies bitfield names for these register groups. This offset header supplies only the register-index side of the address plus field pair.

## Control Flow

This header contributes no runtime control flow. Runtime code includes the header, expands selected macros into register tables, and uses those tables during link encoder and PHY operations.

The implied hardware flows are sequencing-sensitive even though they are not implemented here:

- Supervisor PLL and clock programming through `SUP`/`SUPX` reference-clock, MPLLA/MPLLB, SSC, charge-pump, prescaler, bandgap, and RTUNE indices.
- Lane TX power and DCC setup through `LANE*`/`LANEX` TX power-control, DCC CR-bank, DAC, clock-alignment, and LBERT indices.
- Lane RX power, VCO/CDR/DPLL, adaptation, statistics, and analog status through the `LANE*`/`LANEX` RX control families.
- PCS/PMA handshakes, IRQ masks/status/clear paths, FSM shortcuts, OCLA debug controls, and ATE/test overrides through `RAWLANE*`/`RAWLANEX`.
- Always-on calibration and status readback through `RAWAONLANE*`/`RAWAONLANEX`, including DFE/AFE offsets, IQ phase adjustment, common calibration status, DCC calibration codes, signal detection, firmware configuration, and lane transceiver mode.

## State And Persistence

The macros themselves are stateless compile-time constants. The state they address lives in volatile DPCS PHY hardware behind indirect CR address/data ports. That state is affected by modesets, link training, hotplug handling, PHY power transitions, suspend/resume, reset recovery, diagnostics, and any debug path that writes raw DPCS CR registers.

Several addressed registers are status or latched readback locations: ID registers, calibration-done/status registers, adaptation results, FOM/statistic counters, DCC acknowledgements, signal-detect state, PLL/RTUNE status, ASIC input/output handshakes, and analog status registers. Others are override controls, timing controls, calibration configuration, or raw analog controls. Override state can outlive a single debug operation until explicitly cleared or until hardware reset, so consumers must restore normal ASIC ownership after special sequences.

Because this is an offset header, persistence correctness mostly means preserving the address map. A wrong numeric macro value can send an otherwise valid field write to the wrong DPCS CR register and silently corrupt unrelated PHY state.

## Dependencies

This chunk depends on the AMD ASIC register-generation pipeline and the DPCS 4.2.3 hardware specification staying synchronized. It is normally consumed with:

- `dpcs_4_2_3_sh_mask.h`, which provides the field masks and shifts for these indexed registers.
- The top-level DPCS address/data port definitions in the same file, such as `regDPCSSYS_CR1_DPCSSYS_CR_ADDR`/`DATA` and `regDPCSSYS_CR2_DPCSSYS_CR_ADDR`/`DATA`.
- AMD display register-list macros such as `DPCS_DCN31_REG_LIST` and `DCN3_1_RDPCSTX_REG_LIST`, which build link encoder register tables from generated offsets.
- DCN 3.1.6 resource construction in `drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes both `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`.
- Link encoder, HPO DP link encoder, PHY power, link training, and diagnostics code that ultimately uses these DPCS indexed registers through AMDGPU display register helpers.

The file is part of an imported AMDGPU display driver subtree in this repository. It has no direct dependency on Ceph filesystem logic despite the repository path containing `ceph-client`.

## Integration Points

In `dcn316_resource.c`, DPCS 4.2.3 offsets are included with DCN 3.1.6 offsets and masks to populate link encoder and HPO DP link encoder register tables. `DPCS_DCN31_REG_LIST(id)` includes the indexed DPCS CR address/data access registers (`RDPCS_TX_CR_ADDR` and `RDPCS_TX_CR_DATA`) along with RDPCSTX PHY controls; HPO DP resource construction also includes `DCN3_1_RDPCSTX_REG_LIST` entries. These tables are the bridge between the generated address constants and runtime link encoder objects.

The chunk's concrete CR1 and CR2 prefixes matter. The same suffix, for example `RAWAONLANE2_DIG_TX_DCC_CONFIG`, can appear under different CR instances with the same index value but a different CR address/data port. Consumers must pair `ixDPCSSYS_CR1_*` indices with CR1 access paths and `ixDPCSSYS_CR2_*` indices with CR2 access paths.

The `LANEX`, `RAWLANEX`, and `RAWAONLANEX` blocks are lane-generic templates. They are useful for generated table patterns and structural validation, but direct programming paths still need to resolve the intended physical lane and CR instance. Concrete lane blocks (`LANE0`-`LANE3`, `RAWLANE0`-`RAWLANE3`, `RAWAONLANE0`-`RAWAONLANE3`) encode the per-lane base increments.

## Risks

- The chunk starts in the middle of `ixDPCSSYS_CR1_RAWAONLANE2_*`; the previous chunk owns the beginning of that always-on lane 2 block.
- The chunk ends in the middle of `ixDPCSSYS_CR2_SUPX_*`; the next chunk owns the remaining CR2 supervisor-X analog and RTUNE/override/status indices.
- Generated address drift compiles cleanly. A wrong `ixDPCSSYS_*` value will not be caught by C type checking and can route a valid field write to the wrong indirect register.
- CR instance mixups are easy because CR1 and CR2 blocks reuse many suffixes and many numeric index ranges. The CR access port and index macro must be kept together.
- Lane mixups are easy because lane blocks are repetitive and often differ only by the `0x100` base increment or by a lane-template `X` prefix.
- Partial lane coverage is asymmetric in this chunk: CR2 lane 0 and lane 3 blocks are shorter than lane 1 and lane 2 in the visible range. Per-file reconciliation should not infer missing lane support solely from this chunk.
- Supervisor PLL, RTUNE, bandgap, power-state, VCO/CDR/DPLL, adaptation, DCC, and raw analog registers are hardware-sequencing sensitive. Incorrect writes can cause failed link training, display blanking, unstable high-rate links, bad signal-detect behavior, or misleading diagnostics.
- Reserved analog registers and undocumented template locations should be treated as hardware-owned unless a validated sequence explicitly writes them.

## Test Signals

Useful validation signals for changes touching this header or its consumers include:

- Kernel build coverage for AMDGPU display code that includes `dpcs_4_2_3_offset.h`, especially DCN 3.1.6 resource and link encoder paths.
- Generated-header consistency checks that compare repeated CR1/CR2 and lane 0-3 blocks for expected base increments and suffix preservation.
- Diff checks against neighboring generated DPCS versions such as `dpcs_4_2_2_offset.h` and `dpcs_4_2_0_offset.h` to distinguish intentional ASIC-version changes from generator drift.
- Static checks that each offset macro used by a field mask has a matching register group in `dpcs_4_2_3_sh_mask.h`.
- Hardware bring-up on DCN 3.1.6/DPCS 4.2.3 devices: boot display, hotplug, modesets, suspend/resume, GPU reset recovery, and multi-monitor operation.
- DisplayPort and HDMI link-training stress across lane counts, link rates, UHBR/HBR modes where applicable, and power-state transitions.
- PHY diagnostics that exercise CR1/CR2 supervisor PLL/RTUNE status, TX DCC programming, RX adaptation/statistic readback, signal-detect calibration, raw PCS/PMA IRQ handling, OCLA/debug controls, and analog status readback.

## Boundary Notes For Merge

The final per-file report should reconcile this chunk with adjacent chunks before making whole-file claims. The first visible CR1 raw AON lane 2 register is `ixDPCSSYS_CR1_RAWAONLANE2_DIG_RX_DCC_CAL_ICM_CODE_0` at `0x423d`, not the start of lane 2. The final visible CR2 `SUPX` register is `ixDPCSSYS_CR2_SUPX_DIG_MPLLB_HDMI_CLK_ASIC_IN` at `0x8035`; immediately following source lines continue `SUPX` with additional ASIC input, analog, RTUNE, and override/status offsets.

### subset-b-002384: lines 7257-9642

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

### subset-b-002385: lines 9643-11969

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h lines 9643-11969

## Scope

This chunk is the final segment of the generated AMD DPCS 4.2.3 register-offset header. It covers lines 9643-11969, contains 2,320 `#define` entries, and ends at the file's closing `#endif`. The selected range exports numeric indirect-register offsets only; it has no C functions, structs, enums, typedefs, runtime variables, branches, locking, allocation, direct MMIO access, or persistence logic.

The chunk starts in the tail of the `DPCSSYS_CR3` lane-broadcast region at `ixDPCSSYS_CR3_LANEX_DIG_ANA_RX_AFE_ATT_VGA` and completes the CR3 `LANEX` analog tail plus the CR3 `RAWLANEX` raw lane-broadcast block. It then starts the explicit `// addressBlock: dpcssys_cr4_rdpcstxcrind` section at lines 9821-9822 and covers the CR4 indexed register map through `ixDPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_TX_OVRD_IN_2`.

Observed macro counts in this range are 176 `CR3` symbols and 2,144 `CR4` symbols. The CR4 block includes `SUP` and `SUPX` support regions, lane regions, raw common, raw lane, raw always-on lane, and lane-broadcast aliases.

## Purpose

`dpcs_4_2_3_offset.h` publishes symbolic offsets for AMD DPCS 4.2.3 display/link PHY registers. These `ixDPCSSYS_*` constants are the indirect register numbers used with DPCSSYS CR address/data windows defined earlier in the same header, not host virtual addresses or ordinary direct MMIO offsets.

This chunk's purpose is to finish the CR3 lane-broadcast map and provide the complete final CR4 indexed-register block for DCN316-era DPCS hardware. Runtime display code can combine these offsets with the companion `dpcs_4_2_3_sh_mask.h` field definitions to program DisplayPort/PHY link state, PLLs, TX/RX lane power, receiver adaptation, signal detection, calibration, raw PCS/PMA handoff, IRQ status/clear/mask registers, diagnostics, and manufacturing/test override paths without hard-coded numeric register addresses.

## Important Macros and Address Families

The exported API surface is the generated preprocessor namespace:

- `ixDPCSSYS_CR3_LANEX_*`: the final visible CR3 lane-broadcast analog RX/TX tail around `0x90b2-0x90ff`, including RX AFE/CTLE/slicer/IQ/signal-detect override outputs, analog TX measurement/power/ATB/DCC/termination/misc registers, and analog RX clock/CDR/slicer/power/squelch/calibration/ATB registers.
- `ixDPCSSYS_CR3_RAWLANEX_*`: CR3 raw lane-broadcast offsets around `0xe000-0xe0c8`, covering PCS TX/RX override/input/output mirrors, RX adaptation acknowledgement and figure-of-merit values, FSM status and fast-calibration controls, lane IRQ status/clear/masks, PMA crossbar inputs/outputs, TX/RX controller status, OCLA/UPCS observability, ATE overrides, and master MPLL loop controls.
- `ixDPCSSYS_CR4_SUP_*`: CR4 supervisor/common offsets for IDCODE, refclk and MPLL override inputs, MPLLA/MPLLB SSC parameters, charge-pump controls, ASIC feedback inputs, prescaler, RTUNE, bandgap/reference controls, analog MPLL controls, power-control timers/status, clock/reset timing, and digital-to-analog override/status outputs.
- `ixDPCSSYS_CR4_LANE0` through `ixDPCSSYS_CR4_LANE3`: concrete lane register offsets. Lanes 1 and 2 expose the larger repeated lane surface with TX/RX power, VCO, CDR, DPLL, adaptation, statistics, MPHY, analog override, and analog TX/RX controls. Lanes 0 and 3 expose smaller generated subsets in this range and are paired with their separate raw always-on and raw-lane blocks.
- `ixDPCSSYS_CR4_RAWAONLANE0` through `ixDPCSSYS_CR4_RAWAONLANE3` and `ixDPCSSYS_CR4_RAWAONLANEX`: always-on lane offsets for AFE/CTLE/DFE adaptation values, slicer and phase controls, MPHY/RTUNE/DCC state, signal-detect calibration, firmware calibration/adaptation configuration, lane transceiver mode, and TX DCC configuration.
- `ixDPCSSYS_CR4_RAWCMN_*`: raw common always-on offsets for SRAM boot/load state, power gating and reset overrides, supply/reference/MPLL request and acknowledgement routing, firmware ID, VREF state, reference-range override, and MPLL powerdown timing.
- `ixDPCSSYS_CR4_SUPX_*`, `ixDPCSSYS_CR4_LANEX_*`, and `ixDPCSSYS_CR4_RAWLANEX_*`: broadcast or lane-indexed alias views of the CR4 support, lane, and raw-lane register layouts.

The address ranges convey hardware grouping: low offsets cover supervisor/common and concrete lane spaces, `0x4000`-class offsets cover raw always-on lane blocks, `0x8000` and `0x9000` are support/lane alias windows, and `0xe000`-class offsets cover raw lane PCS/PMA/FSM/IRQ/control windows.

## Control Flow

There is no executable control flow in this header chunk. The runtime flow is supplied by AMDGPU display code and the DPCS hardware:

1. DC resource code includes this generated offset header with `dpcs_4_2_3_sh_mask.h`.
2. Register-list macros expand selected `ixDPCSSYS_*` offsets and matching shift/mask constants into static register tables.
3. Link encoder and PHY code use AMD display register helpers to read, write, update, and poll the addressed DPCS indirect registers.
4. The hardware performs the actual sequencing for reference-clock enablement, PLL and MPLL setup, lane TX/RX power states, VCO/CDR/DPLL calibration, receiver adaptation, DCC, signal detect, IRQ generation/clearing, PCS/PMA handoff, and diagnostic capture.

For this source tree, `drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` includes `dpcs/dpcs_4_2_3_offset.h` and `dpcs/dpcs_4_2_3_sh_mask.h`, then uses `DPCS_DCN31_REG_LIST(id)` and `DPCS_DCN31_MASK_SH_LIST(...)` to populate DCN316 link encoder/resource register metadata.

## State and Persistence Behavior

The file itself is stateless. All values are immutable compile-time constants generated from an ASIC register database. It owns no memory, stores no driver state, opens no files, and has no initialization or teardown behavior.

The represented hardware registers do carry state when other code accesses them. State domains include PLL and clock state, SRAM boot/load state, TX/RX lane power states, CDR/DPLL/VCO calibration results, RX adaptation and DFE/CTLE/AFE tuning, DCC calibration, signal-detect calibration, IRQ status and masks, PCS/PMA request/acknowledgement paths, raw FSM status, OCLA/UPCS diagnostic selection, ATE overrides, and analog test-bus readback. Hardware contents persist only according to the relevant reset and power domains, so higher-level code must reprogram or revalidate them after GPU reset, DPCS reset, power gating, suspend/resume, hotplug retraining, link-rate changes, or firmware-driven reinitialization.

## Dependencies and Integration Points

The direct dependency is the C preprocessor. The semantic dependencies are stronger:

- The companion `dpcs_4_2_3_sh_mask.h` must stay aligned with these register names so field helpers apply shifts and masks to the correct offsets.
- `dcn316_resource.c` is the main in-tree consumer for DPCS 4.2.3, binding the offset and shift/mask headers into DCN316 display resource tables.
- DIO/link encoder and DC register-helper code rely on stable generated naming conventions such as `ixDPCSSYS_CR4_LANE2_DIG_RX_CDR_CDR_CTL_0` and token-pasted register-list macros.
- The DPCSSYS CR address/data windows and base-index constants defined earlier in this header provide the indirect access path for these `ix...` offsets.
- Firmware and hardware controllers may own raw FSM, raw common, AON lane, calibration, and PCS/PMA control surfaces during parts of link bring-up; software must coordinate rather than treating every offset as a free direct-control register.
- Adjacent generated DPCS versions such as `dpcs_4_2_0_offset.h` and `dpcs_4_2_2_offset.h` provide useful diff references for detecting unintended generated-header drift versus expected ASIC-version changes.

## Risks

- A wrong numeric offset can compile cleanly while directing a read or write to the wrong PHY register, causing link-training failure, PLL instability, broken signal detect, bad receiver adaptation, failed DCC calibration, or power-state hangs.
- This chunk begins mid-CR3 and then switches to CR4. Merge or review logic must preserve the earlier chunks for the full CR3 context and must not treat the CR3 tail here as an independent complete address block.
- CR4 contains many repeated lane and alias layouts. Prefix mistakes between `LANE*`, `LANEX`, `RAWLANE*`, `RAWLANEX`, `RAWAONLANE*`, and `RAWAONLANEX` can target an unintended concrete lane or broadcast/indexed view.
- IRQ status, clear, and mask registers have similar names but different side effects. The offset header does not encode write-one-to-clear behavior, clear ordering, or mask polarity.
- Raw PCS/PMA, ATE, OCLA, firmware config, and override registers can force hardware away from normal state-machine ownership. Incorrect writes can disrupt calibration, link recovery, or manufacturing/debug paths.
- Reserved analog/digital offsets are still named in the generated map. Consumers must not assume reserved registers are safe scratch space or safe to modify without matching field guidance.
- Manual edits to this generated header can desynchronize the offset map from `dpcs_4_2_3_sh_mask.h`, DCN316 resource tables, and the underlying silicon register database.

## Test and Validation Signals

Useful validation signals are build-time, generated-data, and hardware-integration oriented:

- Build or preprocess AMDGPU display code for DCN316 with `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`; missing or renamed macros should fail where resource tables expand DPCS register lists.
- Static checks should confirm this chunk remains offset-only, contains the expected 2,320 `#define` entries in the selected range, and ends with the header guard footer.
- Cross-check consumed `ixDPCSSYS_CR3_*` and `ixDPCSSYS_CR4_*` register names against `dpcs_4_2_3_sh_mask.h` for matching bitfield definitions where field access is expected.
- Diff repeated CR4 lane, raw-lane, raw always-on, `SUPX`, `LANEX`, and `RAWLANEX` families against neighboring generated versions to catch accidental missing entries or address shifts.
- Exercise DCN316 display paths on hardware: DisplayPort and HDMI modeset, hotplug, link retraining, lane-count and link-rate changes, suspend/resume, GPU reset, power-gating recovery, and error recovery after failed training.
- Hardware bring-up should show expected readback for reference-clock enable, MPLL lock and calibration, bandgap/reference timing, TX/RX pstate acknowledgements, RX VCO/CDR/DPLL calibration, receiver adaptation completion, DCC acknowledgement, signal detect, IRQ status/clear/mask behavior, raw FSM status, and analog/ATE override cleanup.

## Chunk Notes

This is a source-tree-aligned chunk report only for `subset-b-002385`. It intentionally does not create a final per-file synthesis for `dpcs_4_2_3_offset.h`; that belongs to the later merge/reconciliation lane after all chunks for this generated header are available.
