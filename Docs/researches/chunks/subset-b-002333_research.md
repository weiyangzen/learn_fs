# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h lines 2471-4856

## Scope

This chunk is a generated AMD DPCS 4.2.2 register-offset header segment. It covers 2,386 source lines and 2,382 `#define` entries. The content is declarative only: it exports C preprocessor constants for register offsets and contains no functions, structs, enums, runtime branches, allocation, locks, or software persistence.

The slice starts inside the `DPCSSYS_CR0_RAWAONLANE0` always-on lane register group and ends inside `DPCSSYS_CR1_RAWAONLANE2`. Later chunks must provide the trailing `CR1_RAWAONLANE2` entry and subsequent lane/common groups.

## Purpose

`dpcs_4_2_2_offset.h` maps symbolic DPCS 4.2.2 register names to internal register offsets. Driver code pairs these `ix...` address constants with field definitions from `dpcs_4_2_2_sh_mask.h` and AMD display register helpers to program display PHY/DPCS hardware without hard-coded addresses.

This chunk covers low-level DisplayPort/PHY control windows for:

- `CR0_RAWAONLANE0` tail, full `CR0_RAWAONLANE1` through `CR0_RAWAONLANE3`, and `CR0_RAWAONLANEX`.
- `CR0_SUPX`, including supervisor digital registers and analog MPLLA/MPLLB controls.
- `CR0_LANEX`, including generic lane digital/analog TX and RX registers.
- `CR0_RAWMEM` and `CR0_RAWLANEX`.
- `CR1_SUP`, `CR1_LANE0` through `CR1_LANE3`, `CR1_RAWCMN`, and full `CR1_RAWLANE0` through `CR1_RAWLANE3`.
- `CR1_RAWAONLANE0`, `CR1_RAWAONLANE1`, and most of `CR1_RAWAONLANE2`.

## Important API Surface

There are no callable APIs. The exported interface is the generated macro namespace:

- `ixDPCSSYS_CR0_RAWAONLANE{0,1,2,3,X}_DIG_*`: always-on lane offsets for AFE/CTLE offsets, RX adaptation IQ/FOM, DFE ref levels and VDAC/IDAC offsets, RX phase adjust, MPLLA/MPLLB coarse tune, power-up done, adapted ATT/VGA/CTLE/DFE taps, slicer controls, common calibration status, adaptation controls, MPLL disable, signal detect, DCC calibration codes, firmware config, lane transceiver mode, and TX DCC config.
- `ixDPCSSYS_CR0_SUPX_DIG_*` and `ixDPCSSYS_CR1_SUP_DIG_*`: supervisor/common offsets for ID code, reference clock override, MPLL divider and mode override, refgen control, RTUNE control/status, SRAM boot/load, clock selection, supply isolation and power-gate overrides, debug/OCLA controls, reset/power outputs, and analog PMIX override outputs.
- `ixDPCSSYS_CR0_SUPX_ANA_*` and `ixDPCSSYS_CR1_SUP_ANA_*`: analog supervisor offsets for prescaler, RTUNE, bandgap, switch power measurement, MPLLA/MPLLB miscellaneous controls, overrides, ATB entries, control words, and reserved slots.
- `ixDPCSSYS_CR0_LANEX_*` and `ixDPCSSYS_CR1_LANE{0,1,2,3}_*`: lane-scoped ASIC override, TX/RX power control, VCO calibration, CDR/DPLL, RX adaptation controls/status, RX statistics counters, MPHY controls, analog TX/RX override outputs, DCC DAC/term controls, ATB measurement, and reserved analog lane slots.
- `ixDPCSSYS_CR0_RAWLANEX_DIG_*` and `ixDPCSSYS_CR1_RAWLANE{0,1,2,3}_DIG_*`: raw PCS/PMA lane offsets for TX/RX override/input, ATE overrides, master MPLL loop, FSM control and monitor registers, fast RX calibration/adaptation states, IRQ status/clear/mask registers, PMA crossbar override/status, TX/RX controller status, and OCLA/UPCS debug hooks.
- `ixDPCSSYS_CR1_RAWCMN_DIG_*`: raw common-domain offsets for common controls, PMA/PCS power-stable overrides, power-gate override/status, monitor and analog isolation controls, SRAM boot/load, reference clock, MPLL force/ack, VREF status, RTUNE values, reference range override, and miscellaneous always-on common config.

The offsets in repeated lane groups follow regular windows. Examples in this chunk include `CR0_RAWAONLANE1` at `0x4100`-`0x4151`, `CR0_RAWAONLANE2` at `0x4200`-`0x4251`, `CR0_RAWAONLANE3` at `0x4300`-`0x4351`, `CR1_RAWLANE0` at `0x3000`-`0x30c8`, `CR1_RAWLANE1` at `0x3100`-`0x31c8`, `CR1_RAWLANE2` at `0x3200`-`0x32c8`, and `CR1_RAWLANE3` at `0x3300`-`0x33c8`.

## Control Flow

This header has no software control flow. The implied hardware programming flow is:

1. DCN 3.1.5 display resource code includes this offset header and the matching shift/mask header.
2. Resource/link encoder code selects a DPCS block, lane, and symbolic offset.
3. Register helper code performs MMIO or indexed register access using the address constant.
4. Field values from `dpcs_4_2_2_sh_mask.h` are applied during read-modify-write operations.
5. DPCS hardware state machines consume request, reset, power, calibration, adaptation, interrupt, and override writes, while status offsets expose acknowledgements and calibration/debug readback.

The repeated `LANEX` and `RAWLANEX` blocks are generic per-lane templates, while numbered `LANE0`-`LANE3` and `RAWLANE0`-`RAWLANE3` blocks provide concrete lane windows. `RAWAONLANE*` blocks are separate always-on calibration/status windows, not the same layout as raw PCS lane blocks.

## State And Persistence

The file itself stores no runtime state. Its constants address hardware state that persists according to DPCS power domains, resets, and firmware/hardware sequencing.

Important hardware-backed state named in this chunk includes TX/RX pstate and power-up timing, reset/request/ack handshakes, MPLL selection and force/ack controls, RX CDR and VCO calibration state, RX adaptation and DFE status, RTUNE and DCC calibration controls, signal detect filters and readback, IRQ status/clear/mask bits, OCLA/debug monitor registers, ATE/test overrides, and analog TX/RX control or measurement registers.

Because many registers are override or clear/status surfaces, software consumers must preserve reserved bits and respect access semantics from the hardware spec. This offset header only tells callers where registers live; it does not encode write-one-to-clear behavior, read-only status behavior, timing requirements, or reset defaults.

## Dependencies And Integration Points

The syntactic dependency is the C preprocessor and the include guard in the full header. The semantic dependency is AMD's generated DPCS 4.2.2 register database and the companion `dpcs_4_2_2_sh_mask.h` bitfield map.

In this tree, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes both `dpcs/dpcs_4_2_2_offset.h` and `dpcs/dpcs_4_2_2_sh_mask.h`, alongside DCN 3.1.5 register headers. The same file defines DPCS base segments after the includes, tying these offsets to DCN 3.1.5 display resource initialization.

Likely consumers are AMD display register tables and link/resource code involved in DisplayPort/PHY bring-up, lane programming, link training, rate/width/pstate changes, hotplug recovery, suspend/resume, power gating, calibration, DCC/RTUNE handling, IRQ handling, and validation/debug flows that read FSM/OCLA/ATE state.

## Risks

- Generated-header drift is the primary risk. A wrong offset can direct a valid field mask to the wrong hardware register, producing silent PHY misconfiguration.
- The chunk is highly repetitive across lanes and controllers. A generation error in one lane window can cause lane-specific link-training or signal-integrity failures that are hard to distinguish from board or cable issues.
- This slice starts and ends mid-group. Merge/reconciliation must not treat `CR0_RAWAONLANE0` or `CR1_RAWAONLANE2` as complete based only on this document.
- `CR0` and `CR1` blocks reuse many offset values under different controller prefixes. Consumers must combine the correct block base, address macro, and field mask rather than assuming a globally unique numeric offset.
- Override registers can bypass normal state-machine control. Leaving ATE, PMA/PCS, reset, MPLL, signal-detect, or data-enable overrides asserted can break normal display operation or power management.
- IRQ status, clear, and mask registers have very similar names. Incorrect access semantics can lose interrupts, create interrupt storms, or clear the wrong event.
- Analog and calibration offsets control MPLL, RTUNE, DCC, CDR, VCO, RX adaptation, and termination behavior. Bad values can produce intermittent failures, not just immediate compile or probe failures.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-facing:

- Compile AMDGPU display code that includes `dcn315_resource.c`, verifying `dpcs_4_2_2_offset.h` and `dpcs_4_2_2_sh_mask.h` remain synchronized.
- Static generated-header checks should confirm expected repeated lane-window structure and matching offset/mask prefixes for complete groups in this range.
- Compare DPCS 4.2.2 offsets against adjacent generated versions, especially `dpcs_4_2_0` and `dpcs_4_2_3`, to catch unintended lane-window or block-offset drift.
- Hardware tests should cover DisplayPort link bring-up, lane-count/rate changes, retraining, hotplug, suspend/resume, low-power entry/exit, RX adaptation, DCC/RTUNE calibration, signal detect, and IRQ clear/mask behavior on DCN 3.1.5-class hardware.
- Debug readback should show sane transitions for reset/request acknowledgements, power-up done, MPLL/RCAL/VREF calibration status, RX adaptation done/FOM, CDR/VCO status, TX DCC status, signal detect outputs, FSM fast-state flags, and OCLA monitor values.

## Chunk Notes For Merge

This document intentionally covers only lines 2471-4856 of `dpcs_4_2_2_offset.h`. The final per-file report should describe the entire file as a generated ASIC register-address map for AMD DPCS 4.2.2, paired with `dpcs_4_2_2_sh_mask.h` and integrated through `dcn315_resource.c`.
