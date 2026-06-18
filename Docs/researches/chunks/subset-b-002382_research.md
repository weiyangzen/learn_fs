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
