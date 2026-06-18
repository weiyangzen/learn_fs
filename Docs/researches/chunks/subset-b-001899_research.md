# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 4799-7213

## Scope

This chunk is part of the generated AMD DCN 3.1.6 shift/mask header. It exports C preprocessor constants that describe bit positions and masks for DCN display-controller registers. The source range is macro-only: it has no functions, structs, typedefs, branches, loops, or software-owned storage.

The range starts in the middle of `DISP_INTERRUPT_STATUS_CONTINUE18`, so the first field's shift definition is outside this chunk while the later shift and mask constants are present. It ends in the middle of `DWB_OGAM_RAMA_END_CNTL2_R`, where the final `DWB_OGAM_RAMA_EXP_REGION_END_SLOPE_R_MASK` constant is outside the requested lines. The merge lane should combine adjacent chunks before making complete-register claims for those two boundary registers.

## Purpose

The purpose of this range is to expose DCN 3.1.6 hardware bitfield layout to AMDGPU display code. The companion `dcn_3_1_6_offset.h` header names MMIO registers; this header names fields inside those registers. Runtime code combines both through register helper macros such as `REG_GET`, `REG_UPDATE`, `FD_MASK`, `FD_SHIFT`, and DC/DMUB register-list constructors.

The covered definitions fall into four broad groups:

- Display interrupt status continuation registers and interrupt destination routing registers for DC, DMU/DMCUB, DCPG, MMHUBBUB, DCHUB, DPP perfmon, MPC, OPP, OPTC, OTG, DIG/DIO/DCIO, HPD, audio, AUX, DSC, and HPO sources.
- DMU miscellaneous and display power-gating registers, including clock gating, memory-power control, SMU interrupt controls, Z-state/SOC-access controls, per-domain power-gating config/status, DCPG interrupt status/control, and IP request enable.
- DMCUB registers for region mapping, code-window mapping, interrupt enable/ack/status/type, external interrupt reporting, security/fault handling, inbox/outbox queues, timers, scratch registers, GPINT data, memory power, processor ID, and soft reset.
- Display Writeback (`DWB`) top and color-pipeline registers for enable/clocking, memory power, frame capture, window/source sizing, CRC, output formatting, overflow/backpressure/debug state, HDR multiplier, gamut remap matrices, OGAM mode/LUT controls, and the first OGAM RAM A endpoint controls.

## Important Definitions

The public surface is the generated shift/mask naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask.

The interrupt-status continuation group covers `DISP_INTERRUPT_STATUS_CONTINUE18` through `DISP_INTERRUPT_STATUS_CONTINUE25`. Important fields include AZ audio endpoint format/enabled/disabled interrupts, DIG fast-training and video-stream-disable interrupts, OTG CPU static-screen/vupdate/GSL-vsync-gap/vstartup/vready events for six OTGs, I2C DDC hardware-done and read-request events, DCPG domain power up/down events, DSC underflow/core-error/perfmon events, DMCUB timer/inbox/outbox/GPINT/fault events, ABM ready/update events, DPIA, whitelist-invalid-access, HPO perfmon, and MMHUBBUB warmup. Continuation bits at bit 31 link each status register to the next continuation register.

The interrupt-destination group maps the same classes of hardware events to destinations. It includes `DCCG_INTERRUPT_DEST`, `DMU_INTERRUPT_DEST`, `DMU_INTERRUPT_DEST2`, `DCPG_INTERRUPT_DEST`, `DCPG_INTERRUPT_DEST2`, `MMHUBBUB_INTERRUPT_DEST`, `WB_INTERRUPT_DEST`, `DCHUB_INTERRUPT_DEST`, `DCHUB_PERFCOUNTER_INTERRUPT_DEST`, `DCHUB_INTERRUPT_DEST2`, `DPP_PERFCOUNTER_INTERRUPT_DEST`, `MPC_INTERRUPT_DEST`, `OPP_INTERRUPT_DEST`, `OPTC_INTERRUPT_DEST`, `OTG0_INTERRUPT_DEST` through `OTG5_INTERRUPT_DEST`, `DIG_INTERRUPT_DEST`, `I2C_DDC_HPD_INTERRUPT_DEST`, `DIO_INTERRUPT_DEST`, `DCIO_INTERRUPT_DEST`, `HPD_INTERRUPT_DEST`, `AZ_INTERRUPT_DEST`, `AUX_INTERRUPT_DEST`, `DSC_INTERRUPT_DEST`, and `HPO_INTERRUPT_DEST`.

The GPU timer start-position registers, `DC_GPU_TIMER_START_POSITION_VREADY`, `DC_GPU_TIMER_START_POSITION_FLIP`, `DC_GPU_TIMER_START_POSITION_V_UPDATE_NO_LOCK`, and `DC_GPU_TIMER_START_POSITION_FLIP_AWAY`, define per-display-pipe timing selectors. Most pipe fields are 3-bit values spaced every four bits; the flip and flip-away variants cover D1-D8 while vready and vupdate-no-lock cover D1-D6 in this chunk.

The DMU/DCPG group covers `CC_DC_PIPE_DIS`, `DMU_CLK_CNTL`, `DMU_MEM_PWR_CNTL`, `DMCU_SMU_INTERRUPT_CNTL`, `SMU_INTERRUPT_CONTROL`, `ZSC_CNTL`, `ZSC_CNTL2`, `DMU_MISC_ALLOW_DS_FORCE`, `ZSC_STATUS`, domain power-gate config/status registers for domains 0-3 and 16-18, `DCPG_INTERRUPT_STATUS`, `DCPG_INTERRUPT_STATUS_2`, `DCPG_INTERRUPT_CONTROL_1`, `DCPG_INTERRUPT_CONTROL_3`, and `DC_IP_REQUEST_CNTL`.

The DMCUB group is dense and operationally important. Region registers define 64-bit-style offsets via low and high pieces, top addresses, and enable bits for regions 0, 1, 2, 4, 5, 6, and 7 plus code windows `REGION3_CW0` through `REGION3_CW7`. Interrupt registers expose enable, ack, status, and type fields for timers, inbox/outbox ready/done, GPINT0-GPINT6, GPINT_IH, and undefined-address faults. Queue registers expose base, size, write pointer, and read pointer for inboxes and outboxes 0 and 1. Control/fault registers include security level, unit ID, secure reset, fault interrupt disable, auto-reset and secure-reset status, instruction-fetch/data-write fault clear bits, full-width fault addresses, timer trigger/current, scratch0-scratch15, GPINT data in/out, light-sleep wake interrupt enable, memory-power control, processor ID, and soft reset.

The DWB top group covers `DWB_ENABLE_CLK_CTRL`, `DWB_MEM_PWR_CTRL`, `FC_MODE_CTRL`, `FC_FLOW_CTRL`, `FC_WINDOW_START`, `FC_WINDOW_SIZE`, `FC_SOURCE_SIZE`, `DWB_UPDATE_CTRL`, `DWB_CRC_*`, `DWB_OUT_CTRL`, `DWB_MMHUBBUB_BACKPRESSURE_*`, `DWB_HOST_READ_CONTROL`, `DWB_OVERFLOW_*`, `DWB_SOFT_RESET`, and `DWB_DEBUG_CTRL`. These fields control capture enable/rate/cropping/stereo/new-content state, capture dimensions, update locking, CRC selection and readback, output denorm/min/max/format, host read throttling, overflow interrupt status/ack/mask/type, and debug selection.

The DWB color-pipeline group starts `dce_dc_wb0_dispdec_dwbcp_dispdec`. It includes `DWB_HDR_MULT_COEF`, gamut-remap mode/current mode, coefficient format, two complete remap coefficient banks `A` and `B` with 3x4-style C11-C34 packed pairs, `DWB_OGAM_CONTROL`, `DWB_OGAM_LUT_INDEX`, `DWB_OGAM_LUT_DATA`, `DWB_OGAM_LUT_CONTROL`, and OGAM RAM A start/base/slope/end controls for B, G, and R channels through the partial `DWB_OGAM_RAMA_END_CNTL2_R` register.

## Control Flow And State

This header has no direct control flow. At runtime, DCN 3.1.6 code includes this file and expands field constants into register metadata tables. For example, `display/dmub/src/dmub_dcn316.c` includes `dcn_3_1_6_offset.h` and this header, then fills `dmub_srv_dcn316_regs` with register offsets plus `FD_MASK`/`FD_SHIFT` field values. `display/dc/resource/dcn316/dcn316_resource.c` includes the same generated pair while constructing DC resource objects and DWB/MMHUBBUB support. IRQ service code in nearby DCN generations uses `DMCUB_INTERRUPT_ENABLE` and `DMCUB_INTERRUPT_ACK` fields to build outbox interrupt descriptors, matching fields defined here.

Runtime flow is table-driven:

1. Resource or service code selects a register address from the offset header.
2. It selects a field from this shift/mask header.
3. Register helpers combine address, mask, and shift to read, write, or update the MMIO field.
4. Hardware keeps the programmed value or reports live status until reset, power gating, firmware activity, or a later write changes it.

Most state represented here is persistent hardware register state. DMCUB region mappings, inbox/outbox base and pointer registers, interrupt enables/types, clock/memory power controls, DWB capture configuration, color matrices, LUT controls, output format, and GPU timer selectors persist as MMIO-programmed state. Status fields are live hardware or firmware state, such as interrupt status bits, power-gate FSM state, ZSC access/fence status, DMCUB fault addresses, external interrupt count/ID/context, DWB update pending, CRC values, overflow flags/counters, and current color-mode readbacks.

Several protocols are ordering-sensitive. Interrupt status and ack fields must be masked, acknowledged, and routed consistently. DCPG power state must coordinate force-on/gate requests with PGFSM status and power up/down interrupt clear bits. DMCUB region and mailbox registers must be valid before firmware use; pointer updates need producer/consumer discipline. DWB capture should coordinate enable, window/source size, update lock/pending, memory power, and overflow handling. DWB color programming must use the intended matrix bank, OGAM host selection, LUT index/data ordering, and current-mode status.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register contract. It is meaningful only with:

- `dcn_3_1_6_offset.h`, which supplies the matching register offsets and base indices.
- DC and DMUB register helper layers that expand `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_UPDATE`, `IRQ_REG_ENTRY`, and related macros.
- DCN 3.1.6 resource construction in `display/dc/resource/dcn316/dcn316_resource.c`.
- DMUB service construction in `display/dmub/src/dmub_dcn316.c`.
- DWB support from the DC DWB register-list family, including `display/dc/dwb/dcn30/dcn30_dwb.c` and `dcn30_dwb.h`, which use fields such as `DWB_ENABLE`, update controls, CRC, output format, and overflow status through per-generation register tables.
- IRQ service tables and interrupt source ID mappings that rely on the status, destination, enable, ack, and type field layout for DMCUB outbox events, OTG timing events, HPD/AUX/I2C, DCPG, DSC, audio, and perfmon sources.

Integration is compile-time but behavior is hardware-facing. A bad constant can compile cleanly if the symbol name exists, then program the wrong bit in an MMIO register. The risk surface is larger than ordinary local C code because these definitions are shared by display modeset, firmware mailbox, interrupt, power-management, writeback, color, and diagnostics paths.

## Risks And Edge Cases

Generated-header drift is the main risk. If any shift or mask differs from the silicon register specification or from the companion offset header, the driver can silently manipulate the wrong field. Likely failures include missing or storming interrupts, stuck DMUB mailbox communication, firmware fault handling failures, display power-gating hangs, broken DWB capture, incorrect writeback color, stale CRC or perfmon data, and subtle suspend/resume or idle-state failures.

Chunk boundaries are not semantic. The first register and final register are incomplete in this chunk. The merge lane should not infer that `DISP_INTERRUPT_STATUS_CONTINUE18` lacks the counter0 shift or that `DWB_OGAM_RAMA_END_CNTL2_R` lacks its slope mask.

Replicated fields are easy to mis-index. OTG0-OTG5, DMCUB GPINT0-GPINT6, DCPG domains 0-3 and 16-18, AUX/HPD/DDC instances, DSC0-DSC5, and DWB channel registers rely on predictable bit ordering. Off-by-one instance mapping can route an interrupt or configure a capture/color channel for the wrong hardware block.

Some field names intentionally produce doubled suffixes such as `*_MASK_MASK` for fields whose hardware name already contains `MASK`. Those should be treated as generated names, not cleanup candidates.

Interrupt and status fields do not encode access semantics. Names such as `*_ACK`, `*_CLEAR`, `*_MASK`, `*_STATUS`, `*_INT_TYPE`, and `*_CURRENT` imply write-one-to-clear, mask, level/pulse, or readback behavior, but this header only supplies bits. Callers must still follow the sequencing expected by hardware and by the IRQ helper tables.

DMCUB address and mailbox fields are full-width or wide physical/firmware-facing values. Region offsets use low/high pieces and top-address enable bits, so truncation, wrong alignment, or enabling before programming both halves can expose invalid firmware memory windows.

DWB capture/color fields are stateful and banked. Matrix coefficients, OGAM LUT data, start/end/base/slope controls, current-mode readbacks, update locks, and memory-power state can make errors appear as intermittent capture glitches or color inaccuracies rather than immediate build or modeset failures.

## Test Signals

There are no unit-testable functions in this chunk. Useful validation is structural and integration-focused:

- Build coverage: DCN 3.1.6 display and DMUB objects that include `dcn_3_1_6_sh_mask.h` should compile with no missing field macros in resource, DMUB, DWB, and IRQ table construction.
- Generated consistency checks: every field's mask should align with its shift and expected width; replicated register families should keep identical layouts where the hardware block is replicated.
- Interrupt validation: HPD/AUX/I2C, OTG vupdate/vstartup/vready, DMCUB outbox/GPINT, DCPG power events, DSC error/perfmon, and audio endpoint interrupts should route, mask, ack, and clear correctly without spurious repeats.
- DMUB validation: firmware boot, region setup, inbox/outbox command traffic, GPINT signaling, scratch register use, timer interrupts, fault reporting, secure reset, and soft reset should work across suspend/resume and power transitions.
- Power-management validation: DMCU/DMCUB/DMU memory-power fields, DCPG domain force/gate/status, ZSC allow/access/fence status, and DC IP request enable should behave across idle, display-off, and resume scenarios.
- DWB validation: frame capture enable/rate/crop/source-size paths should produce expected writeback output; update pending should drain; CRC values should change with content; overflow and backpressure counters should remain clear under valid bandwidth.
- Color validation: DWB HDR multiplier, gamut remap bank A/B, OGAM LUT programming, and OGAM RAM endpoint controls should produce expected pixel-capture or CRC signatures for known color test patterns.

## Chunk Notes For Merge Lane

- The chunk covers lines 4799-7213 of `dcn_3_1_6_sh_mask.h`.
- It contains generated `#define` constants only; no local includes, functions, data objects, enums, or structs are introduced in the range.
- Address blocks fully or partly covered are `dce_dc_dmu_dmu_misc_dispdec`, `dce_dc_dmu_dc_pg_dispdec`, `dce_dc_dmu_dmcub_dispdec`, `dce_dc_wb0_dispdec_dwb_top_dispdec`, and `dce_dc_wb0_dispdec_dwbcp_dispdec`, preceded by interrupt continuation and interrupt destination registers that belong to the surrounding generated interrupt namespace.
- Boundary registers are partial: `DISP_INTERRUPT_STATUS_CONTINUE18` begins before the chunk, and `DWB_OGAM_RAMA_END_CNTL2_R` continues after it.
