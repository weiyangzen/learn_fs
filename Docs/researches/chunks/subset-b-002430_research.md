# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 107501-110169

## Scope

This chunk is a late segment of the generated AMD DPCS 4.2.3 shift/mask header. It covers line 107501 through line 110169 and contains 2,008 `__SHIFT` macro definitions across 661 visible C20 PHY CR0 raw-lane register groups. The range starts in the middle of `C20_PHY_CR0_RAWLANE1_DIG_TX_PCS_XF_IN_1`, continues through lane 1 TX/RX/FSM digital interface fields, covers the corresponding lane 2 TX/RX/FSM field set, and ends in the lane 3 FSM skip-control area at `C20_PHY_CR0_RAWLANE3_DIG_FSM_SKIP_RX_VGA_CONT_ADAPT__SKIP_RX_VGA_CONT_ADAPT__SHIFT`.

The content is declarative only. There are no C functions, structs, enums, branches, loops, runtime allocations, or local side effects. The exported surface is a generated set of preprocessor constants that encode bit positions for hardware register fields. This assigned range contains shift definitions only; companion `_MASK` definitions are elsewhere in the same generated header and must be reconciled at file level.

## Purpose

`dpcs_4_2_3_sh_mask.h` gives AMDGPU display code symbolic bitfield positions for the DPCS 4.2.3 register layout. These macros are paired with register offsets from `dpcs_4_2_3_offset.h` and with AMD display register helper macros so driver code can compose, update, or decode register values without hard-coding raw bit numbers.

This chunk focuses on C20 PHY CR0 raw-lane digital interfaces:

- Lane 1 tail coverage for TX PCS transfer, TX firmware transfer, TX IRQ, TX control, TX PMA transfer, RX PCS transfer, RX firmware transfer, RX IRQ, RX control, RX PMA transfer, and lane firmware/FSM control fields.
- Full lane 2 coverage for the same digital TX, RX, PMA, IRQ, control, firmware, and FSM families.
- Lane 3 coverage from TX PCS/firmware/IRQ/control/PMA and RX PCS/firmware/IRQ/control/PMA through the beginning of FSM fast/skip calibration controls.

The repeated raw-lane structure describes how each lane exchanges request/acknowledge signals, reset state, power state, rate/width context, PLL selection, deskew controls, RX adaptation, margining, interrupts, and firmware/FSM debug state with the rest of the display PHY.

## Exported API Surface

There are no callable APIs or local types. The public interface is the generated macro namespace rooted under `C20_PHY_CR0_RAWLANE{1,2,3}_DIG_*`.

Major macro families in this chunk are:

- `DIG_TX_PCS_XF_*` and `DIG_RX_PCS_XF_*`: PCS-facing transfer registers for reset/request/ack handshakes, rate, width, power state, data/clock enables, inversion, beacon or signal detect, PLL/VCO state, deskew controls, context selection, RX equalization mode, termination and DCC controls, DFE bypass, VREF controls, and context configuration words.
- `DIG_TX_FW_XF_*` and `DIG_RX_FW_XF_*`: firmware-facing transfer and override registers for lane reset/request/ack, rate and PLL/VCO selection, master PLL state, deskew, adaptation acknowledgements, figures of merit, TX pre/main/post cursor direction hints, clock control, and per-lane numbering.
- `DIG_TX_IRQ_CTL_*` and `DIG_RX_IRQ_CTL_*`: interrupt mask, enable, status, and clear bit positions for rate, request, reset, loopback, RTUNE, termination, lane mode, VCO, misc, DCC, DFE bypass, RX equalization, RX adaptation, and RX margining events.
- `DIG_TX_CTL_*` and `DIG_RX_CTL_*`: lane control and status surfaces for FSM interrupt enables, clock selection, off-canonical continuous state, rate IRQ acknowledgement, termination code, firmware power-up completion, MPLL restart calibration, RX adaptation mode/select/FOM, CDR detection, PPM drift, phase adjust, margin deltas/status/error, and IQ code read/write fields.
- `DIG_TX_PMA_XF_*` and `DIG_RX_PMA_XF_*`: PMA-facing transfer and override fields for lane MPLL enables, RX-to-TX parallel loopback, TX/RX request/reset/ack signals, RTUNE controls, supervisor PMA state, and PMA misc handshakes.
- `DIG_FSM_*`: firmware state-machine override, jump bank, breakpoint, status monitor, configuration-stage, scratch, debug, lock, fast-path, and calibration-skip controls.

Reserved bit ranges are emitted with `RESERVED_*__SHIFT` names. They are part of the generated ABI for this header even though normal driver code should not assign semantic meaning to them without the hardware database.

## Register Areas Covered

The lane 1 portion begins at the tail of `DIG_TX_PCS_XF_IN_1`, so earlier fields for that register belong to the previous chunk. From there, lane 1 covers TX PCS context configuration, TX firmware override and status handshakes, TX interrupt controls, TX control state, TX PMA handshakes, then the RX PCS/FW/IRQ/control/PMA areas and a complete lane 1 FSM block. Lane 1 contributes 224 visible register groups in this slice.

Lane 2 is the most complete part of this chunk. It repeats the full TX, RX, and FSM digital lane pattern with 232 visible register groups. The TX side includes PCS/FW request and reset handshakes, interrupt mask/status/clear fields, lane power and clock control, PMA overrides, and RTUNE controls. The RX side includes PCS/FW overrides, adaptation controls, margining IRQs, CDR/VCO-related status, phase adjustment and IQ controls, and RX PMA request/ack overrides. The lane 2 FSM block includes override controls, breakpoints, status monitor bits, configuration-stage flags, twelve firmware scratch registers, debug registers, lock bits, fast TX/RX controls, and many skip bits for startup/rate/continuous calibrations.

Lane 3 starts with a full TX digital area and a full RX digital area, then continues into the FSM area. Its visible 205 register groups end before the full lane 3 FSM skip list is complete. The final line is the shift for `SKIP_RX_REFLVL_CONT_ADAPT`; the following reserved bit for that register and subsequent lane 3 FSM skip controls continue after this assigned range.

## Control Flow And State Behavior

This header has no local software control flow. Runtime behavior arises when AMD display code includes the generated constants and uses them through register access helpers for MMIO or indexed CR register operations.

The field names describe several hardware control flows:

- PCS and firmware handshakes use request, reset, acknowledge, and override-enable fields. Driver or firmware sequences can force values through `*_OVRD_*` fields, while non-override `*_IN_*` and `*_OUT_*` registers expose the active handshake paths.
- Link-rate and power-state transitions flow through `RATE`, `WIDTH`, `PSTATE`, `LPD`, `MPLLB_SEL`, `MPLL_EN`, `VCO_FREQ`, `CLK_RDY`, `DATA_EN`, and related context configuration fields.
- TX and RX interrupt flows use per-event mask, enable, status, and clear registers. Clear fields such as `*_IRQ_CLR` and acknowledgement fields such as `RATE_IRQ_ACK` are important because stale sticky interrupt state can affect later link training or recovery sequences.
- RX adaptation and margining expose request/acknowledge signals, FOM readbacks, phase adjustment maps, IQ code read/write values, VDAC/IQ margin deltas, error/status fields, and a global margin interrupt. These are likely used by firmware-assisted calibration and diagnostics rather than broad resource-table code.
- FSM control fields allow firmware state-machine override, explicit jump commands, breakpoint setup, status monitoring, scratch/debug storage, lock control, fast-mode execution, and selective skip of TX/RX startup, rate, and continuous calibration steps.

The file itself persists no software state. Hardware register state persists according to ASIC reset and power domains. Fields named `STATUS`, `STAT`, `OUT`, `ACK`, `DONE`, `MON`, `RD`, `FOM`, and `DEBUG` are readback-oriented by name, while `OVRD`, `OVRD_EN`, `MASK`, `EN_FLAGS`, `CLR`, `CTL`, `CFG`, `WR`, `SKIP`, and `FAST` fields are control-oriented by name. Actual read/write, sticky, and clear-on-write semantics must be taken from the hardware register database and the driver access policy.

## Dependencies And Integration Points

The syntactic dependency is only the C preprocessor. Semantically, this chunk pairs with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h`, which provides matching register offsets for the same DPCS 4.2.3 namespace. The full generated header also supplies `_MASK` definitions that are required with these `__SHIFT` macros for normal read-modify-write helpers.

The direct include site in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes both `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`. That resource code builds DCN316 DPCS register, shift, and mask tables through `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST`. The raw-lane C20 PHY fields in this chunk are lower-level than the compact link encoder table fields, but they share the same generated namespace made available to display bring-up, firmware coordination, diagnostics, and hardware validation code.

Related integration points include:

- DCN316 display resource initialization and DPCS register table construction.
- DCN31-style DIO and HPO DP link encoder paths that use DPCS register/shift/mask tables.
- DisplayPort and HDMI link training, rate switching, lane power-state transitions, hotplug recovery, suspend/resume, PLL/VCO selection, RX detect, deskew, and loopback flows.
- Firmware-assisted lane calibration, RX adaptation, margining, and debug workflows using scratch, debug, breakpoint, and FSM override registers.
- Generated ASIC register database tooling that must keep offset, shift, and mask headers synchronized.

## Risks

- The primary risk is generated-header drift. A wrong shift value can silently read or write an adjacent control bit, which is especially dangerous for reset, request, IRQ clear, override-enable, PLL/VCO, and calibration-skip fields.
- This chunk contains only `__SHIFT` definitions. Consumers normally need both shift and mask constants; file-level merge validation must ensure matching `_MASK` definitions exist in the full header and that chunk boundaries are not mistaken for missing data.
- Override registers frequently pair a value bit with an enable bit. Setting a value without its enable bit may do nothing, while leaving an enable bit asserted after debug or recovery can hold a PHY lane in a forced state.
- Interrupt status and clear fields are represented as ordinary macros. Code must know which bits are sticky, write-one-to-clear, masked, or gated by enable flags before using them in generic helpers.
- TX/RX lane definitions are highly repetitive across lanes 1, 2, and 3. Copy-generation errors can produce lane-specific failures that only appear on particular link widths or lane remaps.
- RX adaptation, margining, DCC, IQ, phase adjustment, and FSM skip fields affect analog calibration quality. Ad hoc writes can create unstable links even when register access compiles cleanly.
- Reserved fields are defined alongside live fields. Generic code should preserve reserved bits during read-modify-write sequences unless the hardware spec explicitly requires writing them.
- This slice starts and ends inside register groups. The previous chunk owns the beginning of `C20_PHY_CR0_RAWLANE1_DIG_TX_PCS_XF_IN_1`, and the next chunk owns the remainder of `C20_PHY_CR0_RAWLANE3_DIG_FSM_SKIP_RX_VGA_CONT_ADAPT` plus later lane 3 FSM fields.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-integration oriented:

- Compile or preprocess AMDGPU display support for DCN316 paths that include `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`.
- Static generation checks that every complete register in the full `dpcs_4_2_3_sh_mask.h` file has expected `__SHIFT` and `_MASK` definitions, with explicit chunk-boundary exceptions for the partial first and last registers in this work item.
- Cross-check these lane 1, lane 2, and lane 3 C20 PHY field names and bit positions against AMD's authoritative DPCS 4.2.3 register database and the matching `dpcs_4_2_3_offset.h` names.
- Diff lane 1, lane 2, and lane 3 repeated register families to detect accidental asymmetry, while allowing real boundary differences caused by the chunk start/end.
- Build checks for DCN316 resource code and DCN31 DIO/HPO link encoder tables using `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST`.
- Hardware tests on DPCS 4.2.3/DCN316-class ASICs: DP and HDMI link training across lane counts, link-rate changes, lane power transitions, hotplug, suspend/resume, RX detect, loopback, deskew, PLL/VCO selection, IRQ clear/mask behavior, RX adaptation/margining, and recovery after failed training.
- Register readback during bring-up to confirm request/ack transitions, `RATE_IRQ_ACK`, calibration done/status bits, FSM status monitor values, scratch/debug visibility, and cleanup of override-enable and calibration-skip bits.

## Chunk Notes For Merge

This document is source-tree aligned and covers only lines 107501-110169 of `dpcs_4_2_3_sh_mask.h`. The final per-file research should merge this with the previous chunk for the start of `C20_PHY_CR0_RAWLANE1_DIG_TX_PCS_XF_IN_1` and with the next chunk for the remainder of `C20_PHY_CR0_RAWLANE3_DIG_FSM_SKIP_RX_VGA_CONT_ADAPT` and later raw-lane 3 FSM definitions. The full file should be treated as a generated ASIC register bitfield contract for AMD display PHY programming, not as handwritten executable driver logic.
