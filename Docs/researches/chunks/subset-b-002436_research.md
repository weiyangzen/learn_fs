# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 123299-125849

## Scope

This chunk is a generated AMD DPCS 4.2.3 shift/mask header slice. The requested range contains 2,118 `#define` entries across 434 observed register groups, and every define in this exact slice is a `__SHIFT` macro. The corresponding `_MASK` macros for these fields are outside this line range.

The range belongs to the `c20_phy_cr1_rdpcspipecrind` section of `dpcs_4_2_3_sh_mask.h`. It starts at the final field of `C20_PHY_CR1_LANE2_DIG_RX_STAT_LD_VAL_EXT_1`, continues through lane 2 RX IQ/statistic and analog-RX bridge fields, covers a broad lane 3 TX/RX PHY control surface, then enters raw lane 0 TX/RX PCS/FW/IRQ transfer fields. It ends inside `C20_PHY_CR1_RAWLANE0_DIG_RX_IRQ_CTL_RX_MARGIN_VDAC_START_IRQ`, immediately before that register's reserved shift and the following margin IRQ clear/status registers.

This content is declarative hardware metadata only. There are no functions, structs, enums, variables, includes, branches, loops, allocations, locks, MMIO calls, or persistence logic in this chunk.

## Purpose

`dpcs_4_2_3_sh_mask.h` gives AMDGPU display code symbolic bit positions and masks for the DPCS 4.2.3 register layout. Consumers use these generated constants with register-access helpers and generated register tables so PHY, link-encoder, diagnostics, and firmware-interaction paths do not embed raw bit numbers.

This slice covers lower-level C20 PHY CR1 fields rather than the small high-level DPCS register lists commonly initialized by DCN316 resource code. The fields describe per-lane TX/RX sequencing, analog override bridges, RX adaptation/statistic capture, CDR/VCO calibration, DCC controls, LBERT/test facilities, PCS/PMA handshakes, firmware-facing transfer registers, and raw lane IRQ status/mask/clear bits.

Although the repository path is under `distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no callable APIs or local types. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a field inside a hardware register.
- `_MASK` companions are expected elsewhere in the generated file, but none appear in this exact range.

Major macro families in this chunk are:

- `C20_PHY_CR1_LANE2_DIG_RX_STAT_*`: tail RX statistic fields for extended sample-count load values, sample counters, match patterns, statistic counters, stop controls, and done flags.
- `C20_PHY_CR1_LANE2_DIG_RX_IQC_CTL_*`: IQ calibration/reset/config/status fields such as bypass/data adjust, step sizes, jump dividers, data enable, DFE bypass selection, and IQC FSM status.
- `C20_PHY_CR1_LANE2_DIG_ANA_XF_RX_*`: digital-to-analog RX bridge fields for analog clock/data-rate/power/VCO/signal-detect/calibration/AFE/scope/slicer/IQ/loopback/DCC/term-code controls and status/readback CREG words.
- `C20_PHY_CR1_LANE3_DIG_ASIC_*`: lane 3 ASIC override/input/output mirrors for lane mode, TX reset/request/data-enable/rate/width/MPLL selection/EQ/DCC/deskew, RX reset/request/pstate/rate/width/signal-detect/VCO/equalization, ACK/status, and OCLA controls.
- `C20_PHY_CR1_LANE3_DIG_TX_*`: lane 3 TX power-state bitmaps, power-up timers, TX control/status, DCC offsets/status, statistic registers, TX clock alignment, LBERT pattern controls, TX level calculation, FIFO controls, and analog TX override/status bridges.
- `C20_PHY_CR1_LANE3_DIG_RX_*`: lane 3 RX power-state and timing fields, VCO calibration controls/status, LBERT error reporting, CDR controls/status, DPLL frequency/bounds, adaptation configuration/status, DFE tap and slicer controls, DCC calibration offsets, SSM fields, RX statistics, and IQC controls.
- `C20_PHY_CR1_LANE3_DIG_ANA_XF_RX_*`: lane 3 analog RX bridge fields parallel to the lane 2 bridge: analog control/power/VCO/sigdet/calibration/AFE/slicer/IQ/DCC/loopback/term-code/status/CREG fields.
- `C20_PHY_CR1_RAWLANE0_DIG_TX_*`: raw lane 0 TX PCS, firmware transfer, IRQ, FSM/control, and PMA transfer fields for reset/request/data-enable/rate/pstate/loopback/MPLL/termination/RTUNE and TX FW handshakes.
- `C20_PHY_CR1_RAWLANE0_DIG_RX_*`: raw lane 0 RX PCS and firmware transfer fields, RX context configuration, directed TX coefficient feedback, RX clock controls, RX ACK/FOM/readback fields, and the beginning of RX IRQ mask/status/clear definitions.

## Control Flow

This header has no local runtime control flow. The runtime flow is external:

1. AMD display code includes generated DPCS offset and shift/mask headers for the target ASIC generation.
2. Resource and hardware blocks build register, shift, and mask tables using token-pasted macro names.
3. Link encoder, PHY, firmware, and diagnostics code use register helper APIs to compose or decode register values from those tables.
4. Hardware and firmware state machines perform the actual TX/RX power sequencing, adaptation, calibration, IRQ latching, and status updates.

Within this chunk, all behavior is implied by field names. `*_OVRD_VAL` plus `*_OVRD_EN` pairs describe override workflows; `*_ASIC_IN`, `*_IN`, and `*_CNTX_CFG_*` describe control/configuration inputs; `*_OUT`, `*_STAT`, `*_STATUS`, `*_ACK`, `*_DONE`, `*_ERR`, and `*_FOM` describe readback/status surfaces by name. The header itself does not define access permissions, update ordering, reset values, clear semantics, or power-domain validity.

## State And Persistence Behavior

No software state is stored here. The named state is hardware-resident and persists according to ASIC reset, PHY reset, lane power, clock gating, firmware, and modeset/link-training behavior.

Important state surfaces include:

- Lane 2 RX measurement state: statistic counters, sample counts, extended load values, match/mask controls, IQC FSM state, calibration adjust strobes, and analog RX status/CREG readbacks.
- Lane 3 TX state: TX request/reset/data-enable/rate/width/pstate, TX EQ cursors, TX DCC bypass/range/update fields, power-state tables for P0/P0S/P1/P2, power-up timer fragments, TX ACK/status, LBERT patterns, FIFO controls, and analog TX status.
- Lane 3 RX state: RX request/reset/pstate/rate/width/DFE bypass, signal-detect, CDR/VCO/DPLL calibration, adaptation config/status, DFE tap status, slicer/VDAC offsets, RX statistic counters, IQC state, analog RX power/control/VCO/AFE/slicer/term-code/status fields, and loopback controls.
- Raw lane 0 PCS/FW state: PCS TX/RX handshakes, firmware transfer reset/request/pstate/rate/width/adaptation request, directed TX pre/main/post feedback, RX valid override, RX clock enable, ACK/FOM reporting, context configuration, and TX/RX firmware output mirrors.
- Raw lane 0 IRQ state: TX and RX reset/request/rate/pstate/adaptation/term-control/margin/loopback/RTUNE/lane-mode IRQ mask, enable, status, and clear fields. This chunk ends during the RX margin IRQ status group, so the remaining RX margin clear/status definitions belong to the next chunk.

Because these are untyped macros, read-only status fields and writable control fields look the same to the compiler. Consumers must rely on the hardware register database and driver sequencing code to know which bits are writable, sticky, self-clearing, write-one-to-clear, or reserved.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, this file must stay synchronized with AMD's DPCS 4.2.3 register database and the companion DPCS offset/header set under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/`.

The direct include point found in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes `dpcs/dpcs_4_2_3_offset.h` and `dpcs/dpcs_4_2_3_sh_mask.h`. That resource file initializes DCN316 link encoder register/shift/mask tables through `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST`.

These exact `C20_PHY_CR1_*` field names are lower-level PHY fields and are not directly referenced outside generated register headers in this tree. They are still part of the generated ASIC register surface available to display PHY bring-up, firmware-assisted flows, diagnostics, validation tooling, and any table-driven or indirect CR/message-bus access path that targets C20 PHY CR1 registers.

Likely behavioral integration points include:

- DisplayPort and HDMI PHY lane bring-up, link-rate and lane-width changes, lane power-state transitions, hotplug recovery, suspend/resume reinitialization, and GPU reset recovery.
- TX equalization, DCC calibration, termination control, deskew, FIFO, and LBERT/debug paths.
- RX CDR/VCO/DPLL calibration, adaptation, DFE/slicer/AFE controls, signal-detect, IQ calibration, and statistic/margin measurement flows.
- Firmware/PCS/PMA handshakes for raw lane 0, including request/ack, rate/pstate, RX valid, adaptation acknowledgement, FOM reporting, directed TX coefficient feedback, and lane IRQ handling.
- Lab or manufacturing diagnostics using OCLA, ATB/CREG readbacks, analog override outputs, loopback controls, LBERT, and margin/statistic counters.

## Risks And Edge Cases

- Generated-header drift is the central risk. A wrong shift compiles cleanly but can make driver or firmware code write an adjacent analog, calibration, IRQ, or override bit.
- This line range contains only `__SHIFT` macros. Pair validation must look outside the chunk for `_MASK` definitions; flagging all fields as missing masks from this chunk alone would be a false positive.
- The start and end boundaries split register groups. `C20_PHY_CR1_LANE2_DIG_RX_STAT_LD_VAL_EXT_1__SC1_LD_VAL_EXT_14_0__SHIFT` is immediately before the chunk, and the rest of `C20_PHY_CR1_RAWLANE0_DIG_RX_IRQ_CTL_RX_MARGIN_VDAC_START_IRQ` plus following margin IRQ groups are immediately after it.
- Override fields are common. Setting an override value without its enable bit has no intended effect; leaving an enable bit asserted after diagnostics can hold a lane in a forced state during later training or resume.
- TX/RX power-state and timer fields are split across multiple registers. Partial updates can create unstable sequencing or mode-specific failures.
- IRQ status, clear, enable, and mask groups reuse very similar names. Confusing status and clear bits can drop events, leave stale events latched, or cause repeated interrupt handling.
- Analog and calibration fields affect electrical behavior. Bad shifts around DCC, termination, EQ, CDR/VCO, AFE, slicer, signal-detect, or IQC controls can produce black screens, unstable links, compliance failures, or misleading debug readbacks.
- Raw lane PCS/FW/PMA fields can bypass normal state machines. Misprogramming reset/request/rate/pstate/loopback/MPLL/RTUNE/adaptation fields can leave software and hardware with inconsistent views of lane state.
- Reserved fields are emitted like normal fields. Consumers need hardware guidance before writing reserved ranges or constructing full-register values.

## Test Signals

Useful validation is mainly build-time, generation-time, and hardware-integration oriented:

- Build or preprocess AMDGPU display support for the DCN316/DPCS 4.2.3 target that includes `dpcs_4_2_3_sh_mask.h`.
- Mechanically verify that every complete field in the full generated header has matching `__SHIFT` and `_MASK` definitions, allowing this chunk's known boundary exceptions and the fact that this slice contains only shift macros.
- Cross-check the C20 PHY CR1 field names and bit positions against AMD's authoritative DPCS/C20 PHY register database and nearby generated variants such as DPCS 4.2.0/4.2.2 or DCN 3.2.0 where layouts are expected to align.
- Run DP/HDMI link training across rates, widths, and lane mappings that exercise lane 2, lane 3, and raw lane 0 pathways. Watch for stable PLL/CDR lock, successful adaptation, expected ACK/status bits, and absence of unexpected lane IRQs.
- Exercise hotplug, modeset, stream disable/enable, suspend/resume, GPU reset, and failed-link recovery paths to catch stale override enables, uncleared IRQs, or missing PHY reinitialization.
- Use register dumps during failures to verify TX/RX pstate/rate/reset/request/data-enable, DCC range/status, TX EQ, CDR/VCO/DPLL, DFE tap status, slicer/VDAC offsets, RX statistic counters, IQC FSM state, RX valid/ACK/FOM, and margin IRQ status decode correctly.
- Exercise diagnostics where available: LBERT patterns/errors, OCLA, analog CREG/status readbacks, loopback paths, directed TX pre/main/post feedback, RX margin/statistic capture, and firmware PCS/PMA handshakes.

## Chunk Notes For Merge

This document covers only lines 123299-125849 of `dpcs_4_2_3_sh_mask.h`. Earlier chunks own the beginning of lane 2 RX statistic definitions, including the first field of `C20_PHY_CR1_LANE2_DIG_RX_STAT_LD_VAL_EXT_1`. Later chunks own the rest of raw lane 0 RX IRQ margin definitions and the corresponding mask definitions that are outside this all-shift slice. The final per-file report should treat the whole file as generated AMD display PHY register metadata and reconcile the DPCSSYS and C20 PHY address-block sections together.
