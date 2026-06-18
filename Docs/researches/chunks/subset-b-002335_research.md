# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h lines 7243-9628

## Scope

This chunk is a generated AMD DPCS 4.2.2 offset-header segment. It covers 2,386 source lines and 2,382 `#define` constants. Every constant in the selected range is an indexed DPCS register offset named with the `ixDPCSSYS_...` convention; there are no `_BASE_IDX` constants, functions, structs, enums, runtime variables, loops, branches, or executable statements in this slice.

The line range starts inside the `DPCSSYS_CR2` indexed-register map, at the tail of the `CR2_SUPX` analog MPLLA group. It continues through the `CR2_SUPX`, `CR2_LANEX`, `CR2_RAWMEM`, and `CR2_RAWLANEX` regions, then crosses the explicit `dpcssys_cr3_rdpcstxcrind` address-block marker and covers most of the corresponding `DPCSSYS_CR3` indexed-register map through `CR3_LANEX_DIG_ANA_SIGDET_OVRD_OUT_2`. The next lines after this chunk continue the `CR3_LANEX` analog tail and the `CR3_RAWMEM`/`CR3_RAWLANEX` aliases, so the CR3 map is not complete in this chunk alone.

## Purpose

`dpcs_4_2_2_offset.h` gives AMDGPU display code symbolic names for DPCS 4.2.2 register offsets. The `regDPCSSYS_CR*_DPCSSYS_CR_ADDR` and `regDPCSSYS_CR*_DPCSSYS_CR_DATA` registers near the top of the file provide the MMIO address/data windows for CR instances; these `ix...` constants are the indirect offsets written through those windows. Consumer code pairs this offset header with `dpcs_4_2_2_sh_mask.h` to read or update named bitfields without hard-coding internal PHY register numbers.

This chunk specifically maps low-level PHY control, status, calibration, debug, and test registers for CR2 and CR3. It includes common support/MPLL blocks, lane-local digital and analog blocks, raw per-lane PCS/PMA crossbar blocks, raw common always-on control blocks, and lane broadcast forms such as `LANEX`, `RAWAONLANEX`, and `RAWLANEX`.

## Exported API Surface

There are no callable APIs or local C types. The exported surface is the preprocessor macro namespace:

- `ixDPCSSYS_CR2_SUPX_*`: partial CR2 support broadcast region, starting at MPLLA analog ATB/control registers and covering MPLLB analog controls, MPLLA/MPLLB digital power-control registers, clock/reset timing, RTUNE configuration/status, and analog override/status outputs.
- `ixDPCSSYS_CR2_LANEX_*`: CR2 lane-broadcast digital/analog register offsets, including ASIC override/input/output windows, TX/RX power-control and calibration controls, RX CDR/DPLL/adaptation/statistics controls, MPHY controls, digital-to-analog override outputs, and direct analog TX/RX measurement/control registers.
- `ixDPCSSYS_CR2_RAWMEM_*` and `ixDPCSSYS_CR2_RAWLANEX_*`: CR2 raw ROM/RAM and raw lane-broadcast PCS/FSM/IRQ/PMA/TX/RX/ATE offsets in the high indirect range around `0xa000`, `0xc000`, and `0xe000`.
- `ixDPCSSYS_CR3_SUP_*` and `ixDPCSSYS_CR3_SUPX_*`: CR3 support register offsets for IDCODE, refclk, MPLLA/MPLLB override, SSC, charge pump, prescaler, ASIC input/output, bandgap, RTUNE, MPLL power control, clock/reset, and analog override/status.
- `ixDPCSSYS_CR3_LANE{0,1,2,3}_*`: CR3 lane-specific register offsets. Lane 0 and lane 3 are partial in this chunk; lane 1 and lane 2 are more complete and include digital ASIC, TX/RX power, RX CDR/DPLL/adaptation/statistics/MPHY, digital analog-output, and analog TX/RX blocks.
- `ixDPCSSYS_CR3_RAWAONLANE{0,1,2,3,X}_*`: CR3 raw always-on per-lane RX/TX state, power-gating, PCS/PMA request/ack, reset, status, DCC, RTUNE, and analog override/status offsets.
- `ixDPCSSYS_CR3_RAWCMN_*`: CR3 raw common always-on offsets for RTUNE, SRAM boot/load, power-gating override, common reset/supply/reference/MPLL request and acknowledge plumbing, VREF status, reference-range override, and MPLL powerdown timing.
- `ixDPCSSYS_CR3_RAWLANE{0,1,2,3,X}_*`: CR3 raw per-lane PCS/FSM/IRQ/PMA/TX/RX/ATE offsets. These are repeated per physical lane and also exposed through `RAWLANEX` for lane-broadcast or lane-indexed access.

All values in this selected range are 16-bit internal register offsets, not host virtual addresses. The high-order ranges carry block meaning: support/common registers occupy low offsets and `0x8000`-class broadcast support offsets, lane broadcast uses `0x9000`-class offsets, raw ROM/RAM use `0xa000`/`0xc000`, and raw-lane PCS/PMA/control windows use `0xe000`-class offsets.

## Register Areas Covered

The CR2 support-broadcast portion begins midstream at `ixDPCSSYS_CR2_SUPX_ANA_MPLLA_ATB3`. It completes the visible MPLLA analog monitor/control tail, covers MPLLB analog monitor/control and reserved slots, then defines digital MPLL power-control/status/timer/calibration offsets for both MPLLA and MPLLB. The same section exposes clock/reset power-up timers, reference VPHUD, RTUNE configuration and readback registers, and digital analog-override outputs for MPLLA/MPLLB, RTUNE, bandgap, and PMIX.

The CR2 `LANEX` block describes a lane-broadcast view of a single lane register layout. Digital offsets cover ASIC override and ASIC input/output windows, TX power states and power-up timing, TX DCC DAC programming and acknowledgement, TX clock alignment, TX loopback/BERT control, RX power states and timing, RX VCO calibration, RX alignment/LBERT, CDR and DPLL controls, RX adaptation configuration/status/DAC selector/banked access, RX statistics counters and match controls, MPHY low-speed/PWM controls, and digital outputs into analog TX/RX blocks. The following analog offsets expose TX measurement, power override, alternate bus, ATB, DCC DAC, termination, clocks, miscellaneous registers, and RX CDR/slicer/power/squelch/calibration/ATB/reserved registers.

The CR2 raw region includes two memory offsets, `ROM_CMN0_B0_R0` and `RAM_CMN0_B0_R0`, followed by `RAWLANEX` PCS crossbar, FSM, IRQ, PMA crossbar, TX control, RX control, and ATE override windows. This gives software a lower-level lane-broadcast interface to PCS/PMA state-machine inputs and outputs, interrupt status/clear/mask registers, TX/RX request and acknowledgement paths, calibration state, DCC state, OCLA/UPCS observability, and manufacturing/test override controls.

The CR3 block starts cleanly at `// addressBlock: dpcssys_cr3_rdpcstxcrind`. It first maps the normal `SUP` support region from IDCODE and reference-clock overrides through MPLLA/MPLLB overrides, SSC programming, charge pump controls, ASIC inputs, prescaler/bandgap analog controls, MPLL analog controls, MPLL power/timing/calibration, RTUNE, and analog override/status outputs. It then maps lane-specific regions: lane 0 begins at analog RX ATB/reserved registers and continues through raw always-on lane 0; lanes 1 and 2 are complete enough to show the full repeated digital/analog lane layout; lane 3 begins at digital analog outputs and analog TX/RX controls before entering raw always-on lane 3. The CR3 `SUPX` and `LANEX` broadcast regions repeat the same support and lane schemas for broadcast or indexed access across CR3 lanes.

The CR3 raw common and raw lane sections mirror the earlier CR2 raw schema. `RAWCMN` covers common AON RTUNE, SRAM boot/load, power gate and reset override, supply/reference/MPLL request and acknowledge routing, monitor inputs, VREF and reference range state, and MPLL powerdown timing. `RAWLANE0` through `RAWLANE3` plus `RAWLANEX` cover PCS TX/RX override/input/output, FSM status, IRQ status/clear/masks, PMA crossbar input/output, TX/RX controller status, and ATE/loopback/master-MPLL override registers.

## Control Flow And State Behavior

This header chunk has no software control flow. All behavior is supplied by driver code that selects these offsets and by the DPCS hardware reached through the CR address/data windows.

The register names imply several hardware state domains:

- Link and PHY bring-up: support registers drive or observe reference-clock, prescaler, bandgap, MPLL, SSC, RTUNE, clock/reset, SRAM boot/load, and VREF-related state.
- Per-lane power management: TX/RX pstate and power-up timing registers, low-power detect, reset/request/ack fields in the raw PCS/PMA blocks, and supply power-stable controls participate in lane enable, disable, and low-power transitions.
- Clocking and calibration: MPLLA/MPLLB power-control and timing registers, RX VCO calibration, CDR/DPLL controls, DCC DAC programming, RTUNE values, AFE/CTLE/DFE adaptation status, slicer controls, and phase/IQ adjustment offsets represent hardware calibration workflows.
- Status and diagnostics: RX statistics counters, FSM status monitors, OCLA/UPCS windows, LBERT controls/errors, analog ATB/measurement registers, and ATE override windows provide bring-up and validation observability.
- Interrupt lifecycle: raw lane IRQ status, clear, and mask offsets encode a conventional status-clear-mask register pattern for lane reset/request/rate/pstate/adaptation/loopback/DCC/TX events.

No software state is stored in this file. Hardware register contents persist only according to ASIC power domains, resets, and firmware/hardware sequencing. The header itself is stateless and is regenerated from the ASIC register database.

## Dependencies And Integration Points

The direct syntactic dependency is the C preprocessor. The semantic dependency is AMD's generated DPCS 4.2.2 register database and the companion `dpcs_4_2_2_sh_mask.h` bitfield map.

In this tree, `drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes both `dpcs/dpcs_4_2_2_offset.h` and `dpcs/dpcs_4_2_2_sh_mask.h`. That ties this generated offset contract to the DCN 3.1.5 resource implementation. The same file defines DPCS base segments and instantiates RDPCSTX register lists for display link encoders, while DIO/HPO link encoder code elsewhere uses RDPCS/RDPCSTX register and field abstractions for DP/HDMI PHY control.

Important integration surfaces include:

- AMD DC resource construction for DCN315, where generated offset and mask headers populate register-address and bitfield tables.
- DisplayPort and HDMI link encoder programming, especially reference-clock enable, DP alt-mode state, lane rate/width/pstate, TX FIFO/clocking, and MPLL programming paths.
- PHY power and suspend/resume flows that need TX/RX pstate, power-up timers, SRAM boot/load, MPLL powerdown timing, and acknowledgement/status readback.
- Hardware bring-up, lab, or manufacturing flows that use ATE, ATB, OCLA, LBERT, raw PCS/PMA, RTUNE, RX adaptation, CDR/DPLL, DCC, and analog override registers.
- Generated-register validation across adjacent DPCS versions. The same offsets appear in nearby `dpcs_4_2_0_offset.h`, `dpcs_4_2_3_offset.h`, and older `dpcs_3_1_4_offset.h` families, so version-to-version diffs are a useful way to detect accidental generated-header drift.

## Risks

- The chunk is all generated numeric register offsets. A single wrong value can route a read or write to the wrong internal PHY register, which may cause display link failures without any C compiler warning.
- The line range starts and ends inside larger logical groups. Merge/reconciliation must not treat the CR2 `SUPX` beginning or the CR3 `LANEX`/`RAWLANEX` ending as complete based only on this chunk.
- CR2 and CR3 blocks are highly repetitive, and lane 0/1/2/3 plus `LANEX`/`RAWLANEX` forms differ mostly by prefix and offset range. Copy-generation drift can create lane-specific or instance-specific failures that are difficult to diagnose.
- Broadcast forms such as `LANEX`, `SUPX`, `RAWAONLANEX`, and `RAWLANEX` can affect more than one lane or can depend on external lane selection. Consumer code must not substitute them blindly for lane-specific offsets.
- Raw and ATE override registers can force hardware away from normal PCS/PMA state-machine control. Leaving override-enable state asserted after debug or manufacturing operations can break link training, calibration, power management, or hotplug recovery.
- IRQ status, clear, and mask registers have similar generated names but different access semantics. The offset header does not encode write-one-to-clear behavior, mask polarity, or ordering requirements.
- Reserved analog and digital slots are named as offsets. They should not be used as scratch registers, and read-modify-write users must preserve reserved bitfields from the companion mask header.

## Test Signals

Useful validation is mainly build-time, generated-data, and hardware integration oriented:

- Compile/preprocess AMDGPU display code for DCN315 with `dpcs_4_2_2_offset.h` and `dpcs_4_2_2_sh_mask.h` included through `dcn315_resource.c`.
- Static generation checks that this slice contains 2,382 non-`BASE_IDX` `ix...` defines and that no callable code or declarations were introduced into the generated header.
- Cross-check each register prefix in this range against the companion `dpcs_4_2_2_sh_mask.h` so offsets and bitfield masks exist for the same generated register names where field definitions are expected.
- Diff DPCS 4.2.2 offsets against adjacent generated versions (`dpcs_4_2_0_offset.h`, `dpcs_4_2_3_offset.h`, and where applicable `dpcs_3_1_4_offset.h`) to catch unintended address movement or missing repeated lane entries.
- Hardware display tests on DCN315-class systems: DP/HDMI link training, lane-count and link-rate changes, hotplug, DP alt-mode transitions, suspend/resume, low-power entry/exit, MST/HPO paths where available, and error recovery after failed training.
- PHY bring-up readback should show expected transitions for reference-clock enable, MPLL lock/power state, SRAM boot/load, RTUNE status, TX/RX pstate acknowledgements, RX VCO/CDR/DPLL calibration, adaptation status, DCC acknowledgement, IRQ status/clear/mask behavior, and analog/ATE override cleanup.

## Chunk Notes For Merge

This document intentionally covers only lines 7243-9628 of `dpcs_4_2_2_offset.h`. Earlier chunks should cover the start of the CR2 indexed-register map, including the missing beginning of `CR2_SUPX`. Later chunks should continue the CR3 `LANEX` analog tail and CR3 raw memory/raw lane-broadcast regions. The final per-file report should describe the whole header as a generated indirect DPCS 4.2.2 offset map for AMDGPU display PHY programming, with `dcn315_resource.c` and the matching shift/mask header as primary in-tree integration anchors.
