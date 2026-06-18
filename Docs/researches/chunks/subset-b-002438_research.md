# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 128518-131242

## Scope

This chunk is a late segment of the generated AMD DPCS 4.2.3 shift/mask header. It covers line 128518 through line 131242 and defines 1,945 preprocessor constants, all of them `__SHIFT` macros, across 781 visible register groups. No `_MASK` definitions appear inside this slice; the corresponding masks are later in the same generated header or across adjacent chunk boundaries.

The range starts in the middle of the CR1 raw lane 3 RX PCS context configuration block, beginning with `C20_PHY_CR1_RAWLANE3_DIG_RX_PCS_XF_CNTX_CFG_5__REF_LD_VAL__SHIFT`. It then covers lane 3 RX firmware handshakes, RX IRQ/margining/control fields, raw lane 3 FSM and firmware/debug controls, and the always-on per-lane TX/RX calibration blocks for `RAWLANEAON0`, `RAWLANEAON1`, and the beginning of `RAWLANEAON2`. The chunk ends in `C20_PHY_CR1_RAWLANEAON2_DIG_RX_CAL_BANK_SEL`; later lines continue the raw lane AON2 RX code/readback fields.

The content is declarative register metadata. There are no C functions, structs, enums, branches, loops, allocations, locks, or direct MMIO operations in this chunk.

## Purpose

`dpcs_4_2_3_sh_mask.h` provides generated symbolic bit positions and masks for AMDGPU display code that targets the DPCS 4.2.3 register layout. Consumers pair these `__SHIFT` names with companion `_MASK` names and register offsets from `dpcs_4_2_3_offset.h` so driver code can compose, update, and decode DPCS PHY registers without embedding raw bit numbers.

This slice focuses on low-level CR1 raw-lane receive, firmware state-machine, and always-on lane calibration surfaces:

- `C20_PHY_CR1_RAWLANE3_DIG_RX_*` describes lane 3 RX PCS/FW/PMA crossbar handshakes, IRQ status and clear bits, adaptation controls, margining controls, PPM/CDR status, IQ/phase adjustment, and PMA override inputs/outputs.
- `C20_PHY_CR1_RAWLANE3_DIG_FSM_*` describes lane 3 embedded PHY firmware/FSM controls: override/jump controls, breakpoints, monitored addresses/status, firmware stage and scratch registers, debug registers, fast-path controls, skip-calibration bits, and RX calibration status.
- `C20_PHY_CR1_RAWLANEAON0_DIG_TX_*`, `RAWLANEAON1_DIG_TX_*`, and `RAWLANEAON2_DIG_TX_*` describe repeated always-on TX firmware state, SRAM record, startup/continuous algorithm, high-power protection, transceiver-mode, DCC calibration bank, MPLLA/MPLLB calibration-done, DCC code, calibration-bank select, and TX input fields.
- `C20_PHY_CR1_RAWLANEAON0_DIG_RX_*`, `RAWLANEAON1_DIG_RX_*`, and the first part of `RAWLANEAON2_DIG_RX_*` describe repeated always-on RX startup/continuous calibration algorithms, fast flags, VGEN/sigdet/AFE trims, reference and DFE offsets, DCC banks, IQ calibration, adaptation taps, error/reference measurements, adaptation control tables, CDR detector/recovery, and RX override/input/output fields.

## Exported API Surface

There are no callable APIs or local types. The exported surface is the macro namespace consumed by generated AMD display register tables and by any code that performs DPCS CR indexed register access.

The main macro families in this chunk are:

- `C20_PHY_CR1_RAWLANE3_DIG_RX_PCS_XF_*`: RX PCS crossbar context configuration, firmware override input/output, request/ack, pstate/rate/width, DFE bypass, adaptation request, delta IQ, TX pre/main/post direction hints, and RX clock-enable fields.
- `C20_PHY_CR1_RAWLANE3_DIG_RX_IRQ_CTL_*`: mask, enable, status, and clear fields for RX request/rate/pstate/adaptation/reset/termination and margining events.
- `C20_PHY_CR1_RAWLANE3_DIG_RX_CTL_*`: RX termination code, continuous offset/adaptation status, adaptation mode/select/FOM/error values, PPM drift, CDR detector status, phase adjustment read/write/update, margin IQ/VDAC deltas and errors, rate IRQ acknowledgement, and IQ linear/step code fields.
- `C20_PHY_CR1_RAWLANE3_DIG_RX_PMA_XF_*`: PMA-side RX override and input/output bridge fields.
- `C20_PHY_CR1_RAWLANE3_DIG_FSM_*`: firmware state-machine control, breakpoints, scratch/debug registers, CR lock, fast/skip flags for TX and RX calibration paths, and final RX calibration status.
- `C20_PHY_CR1_RAWLANEAON{0,1,2}_DIG_TX_*`: per-lane always-on TX firmware state and calibration registers.
- `C20_PHY_CR1_RAWLANEAON{0,1,2}_DIG_RX_*`: per-lane always-on RX calibration, adaptation, DCC/IQ code, and status registers.

The slice contains only shift constants. Complete use requires the matching masks from later portions of the header and the matching register offsets from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h`.

## Control Flow And State Behavior

This file has no local control flow. Runtime behavior appears only after AMD display code includes the generated header and uses the constants through register access helpers for MMIO or indexed DPCS CR transactions.

The field names reveal several hardware state machines and handshakes that driver or firmware code can observe or override:

- RX PCS/FW handshakes use `RESET`, `REQ`, `ACK`, `PSTATE`, `LPD`, `RATE`, `WIDTH`, `DFE_BYPASS`, `ADAPT_REQ`, `DELTA_IQ`, and paired `*_OVRD_EN` fields to let firmware, diagnostics, or recovery code force or inspect lane 3 receive state.
- RX IRQ and margining registers expose sticky event state and explicit clear bits for reset, request, rate, pstate, adaptation, termination-control, global margining, IQ/VDAC margin start, error clear, margin init, and margin finish events.
- RX adaptation and calibration state is represented by continuous adaptation/offset status, adaptation mode/select, FOM values, reference errors, IQ left/right bounds, phase adjustment maps, margin status/error, CDR detector status, and DCC/IQ calibration results.
- The lane 3 FSM block models an embedded PHY firmware controller. Its breakpoints, monitored address/status, stage, scratch/debug words, CR lock, fast flags, skip flags, and calibration-status fields are control and diagnostic surfaces around the PHY calibration sequence rather than software logic in this header.
- The AON TX/RX blocks are repeated for lanes 0, 1, and 2. They preserve per-lane calibration banks and computed codes for DCC, IQ, AFE, CTLE, VGA, DFE taps, VDAC offsets, error/reference measurements, and adaptation completion.

No software persistence is implemented here. Hardware register contents persist according to ASIC reset, power, and clock domains. Names ending in `*_STATUS`, `*_OUT`, `*_ACK`, `*_DONE`, `*_CODE`, `*_RD`, or `*_MON` are readback-oriented by name, while `*_OVRD_IN`, `*_OVRD_EN`, `*_CTL`, `*_WR`, `*_CLR`, algorithm, fast, and skip fields are control-oriented by name. The header itself does not encode read-only, write-one-to-clear, sticky, or reserved-bit semantics.

## Dependencies And Integration Points

The direct syntactic dependency is only the C preprocessor. Semantically this chunk depends on the generated DPCS 4.2.3 register database that produced both this header and `dpcs_4_2_3_offset.h`.

The direct include site in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes both `dpcs/dpcs_4_2_3_offset.h` and `dpcs/dpcs_4_2_3_sh_mask.h`. That resource file builds DCN316 DPCS register, shift, and mask tables using `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST` from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h`.

Important integration surfaces include:

- DCN316 link encoder resource initialization and DPCS register table construction.
- DCN31-style DIO link encoder helpers that consume DPCS register offsets, shifts, and masks.
- DisplayPort/HDMI PHY bring-up paths that depend on RX signal detect, CDR, pstate/rate/width, adaptation, margining, PLL/DCC/IQ calibration, and lane power state.
- Firmware-assisted or lab-validation flows that use override, fast-path, skip-calibration, breakpoint, scratch, SRAM record, and debug fields.
- Hardware diagnostics and failure recovery that read calibration status, adaptation done, reference error, IQ/DCC code, PMA/RX outputs, and margining IRQ/status fields.

## Risks

- This is generated hardware metadata. A wrong shift value can silently target the wrong bit when combined with an otherwise correct mask and register offset.
- The slice contains only `__SHIFT` macros. Consumers or validation scripts must match these with `_MASK` macros elsewhere in the full header; checking this chunk alone will falsely report missing masks.
- Many control surfaces are override-style value plus enable pairs. Writing a value without the matching enable bit may do nothing, while leaving an override enable asserted after diagnostics can hold the PHY in a forced state across later link training, hotplug recovery, or suspend/resume.
- IRQ clear, status, and mask fields are represented as ordinary constants. Driver code must know which fields are sticky, write-one-to-clear, read-only, or reserved from the hardware spec.
- The AON calibration registers are banked and repeated across lanes. Mixing lane numbers or bank selectors can make failures appear lane-dependent and can corrupt cached calibration state for the wrong physical lane.
- Fast and skip flags for TX/RX calibration can hide real analog bring-up problems if used outside controlled validation or recovery flows.
- Field names include many reserved ranges. Macros make it easy to build bit patterns that touch reserved bits unless values are constrained by generated tables or documented hardware sequences.
- The chunk starts and ends inside register groups, so reconciliation must account for adjacent chunks before treating boundary groups as incomplete.

## Test Signals

Useful validation is primarily build-time, generation-time, and hardware-integration oriented:

- Compile or preprocess AMDGPU display code for DCN316 targets that include `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`.
- Generation checks against the DPCS 4.2.3 register database to confirm every shift in this range has the expected field position and a matching mask in the full header.
- Cross-check `C20_PHY_CR1_RAWLANE3_*` and `C20_PHY_CR1_RAWLANEAON{0,1,2}_*` register names against `dpcs_4_2_3_offset.h`.
- Static checks around `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)` expansion in DCN316 resource code.
- Hardware tests on DPCS 4.2.3-class ASICs for DP/HDMI link training, link-rate and width changes, hotplug, suspend/resume, RX detect, signal detect, CDR recovery, pstate transitions, RX margining, lane adaptation, and recovery after failed training.
- Register readback during PHY bring-up to confirm request/ack transitions, IRQ clear behavior, margin status/error reporting, adaptation done/FOM values, DCC/IQ calibration banks, and cleanup of override/fast/skip bits.

## Chunk Notes For Merge

This document is source-tree aligned and covers only lines 128518-131242 of `dpcs_4_2_3_sh_mask.h`. Earlier chunks should cover the start of `C20_PHY_CR1_RAWLANE3_DIG_RX_PCS_XF_CNTX_CFG_5` and preceding lane 3 RX PCS fields. Later chunks should continue `C20_PHY_CR1_RAWLANEAON2_DIG_RX_CAL_BANK_SEL`, the rest of AON2 RX calibration/adaptation fields, and the associated `_MASK` definitions for this late header section. The final per-file report should treat the whole file as a generated ASIC register bitfield map, not as handwritten runtime driver logic.
