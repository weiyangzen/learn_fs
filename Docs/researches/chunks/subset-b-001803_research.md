# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 2467-4750

## Purpose

This chunk is generated AMD DCN 3.1.2 register field metadata. It contains no executable C logic; it exposes `__SHIFT` and `_MASK` preprocessor constants that describe bit positions and bit masks for display microcontroller, interrupt, timeout, timer, and display interrupt-controller registers.

The range starts at the tail of `DMCU_PERFMON_INTERRUPT_STATUS3`, covers complete DMCU perfmon interrupt status/routing groups, DMCU DPRX and continued interrupt groups, RBBMIF security/timeout/status fields, DC perfmon2 fields, GPU timer start/read fields, the display interrupt-status continuation chain through `DISP_INTERRUPT_STATUS_CONTINUE25`, and ends at the first field of `DCPG_INTERRUPT_DEST`. The requested range has 2,284 source lines, including 2,193 `#define` lines, 1,095 shift macros, and 1,213 mask macros.

Although the path is under a local `ceph-client` source mirror, this header is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, allocation paths, or locks in this range. The interface is the generated field macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: the field mask before callers shift values into or out of the register.

Consumers normally pair these definitions with `dcn_3_1_2_offset.h` register-offset macros through helper APIs such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_READ`, `REG_WRITE`, and the generated `FD_SHIFT`/`FD_MASK` tables.

Major field families in this slice:

- `DMCU_PERFMON_INTERRUPT_STATUS4/5`: occurred/clear bits for writeback, DCCG perfmon2, MMHUBBUB, MPC, OPP, OPTC, HDA, and DSC0-DSC5 perfmon counter interrupts.
- `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK1` through `5`: enable bits that route perfmon counter interrupts to the display microcontroller for DMU, DIO, DCCG, HPO, HUBP0-HUBP7, HUBBUB, DPP0-DPP7, WB0-WB2, MMHUBBUB, MPC, OPP, OPTC, HDA, and DSC blocks.
- `DMCU_PERFMON_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1` through `5`: XIRQ/IRQ selection bits for the same perfmon interrupt sources.
- `DMCU_DPRX_INTERRUPT_STATUS1`, `DMCU_DPRX_INTERRUPT_TO_UC_EN_MASK1`, and `DMCU_DPRX_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1`: occurred/clear, microcontroller-enable, and route-selection fields for DCIO HDP/DPCS, DMUB, I2C, and DPHY fast-training interrupts.
- `DMCU_INTERRUPT_STATUS_CONTINUE`, `DMCU_INTERRUPT_TO_UC_EN_MASK_CONTINUE`, and `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL_CONTINUE`: ABM0/ABM1 ready/update, DCPG domain power up/down, DIO FIFO underflow, DCIO CM/PHY, and DCIO DPCS TX interrupt status and routing fields.
- `DMCU_INT_CNT_CONTINUE`, `DMCU_INT_CNT_CONT2`, and `DMCU_INT_CNT_CONT3`: 8-bit ABM interrupt counters for high-gain ready, local-scene ready, and backlight update events.
- `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL_CONT2`, `DMCU_INTERRUPT_STATUS_2`, and `DMCU_INTERRUPT_TO_UC_EN_MASK_2`: additional DCPG domain16-domain21 power and DCIO DPCS TXA-TXG interrupt route/status/enable fields.
- `DMCUB_RBBMIF_SEC_CNTL`: trust-level and source-ID fields for DMCUB RBBMIF security configuration.
- `RBBMIF_TIMEOUT`, `RBBMIF_STATUS`, `RBBMIF_STATUS_2`, `RBBMIF_INT_STATUS`, `RBBMIF_TIMEOUT_DIS`, `RBBMIF_TIMEOUT_DIS_2`, and `RBBMIF_STATUS_FLAG`: timeout delay/hold, timeout-client decode, operation/read-write status, ACK/mask, per-client timeout disables for clients 0-38, state, FIFO status, read-timeout, and invalid-access diagnostic fields.
- `DC_PERFMON2_*`: perf counter event selection, counted-value type, state selectors for eight counters, perfmon mode/run/clear/start/count-status controls, current-value interrupt status/clear/ack/enable, and 64-bit high/low counter value fields.
- `DC_GPU_TIMER_*`: start-position fields for vupdate, vstartup, vready, flip, no-lock vupdate, and flip-away timing, plus timer read and read-select fields.
- `DISP_INTERRUPT_STATUS` through `DISP_INTERRUPT_STATUS_CONTINUE25`: the IHC display interrupt pending chain for OTG timing events, HUBP flips, DSC/DWB/ABM/DMUB/perfmon interrupts, underflow, HPD and DDC/I2C-related events, AUX/DP sink paths, DMCUB mailbox/timer/general-data interrupts, and continuation-bit links between status registers.
- `DCCG_INTERRUPT_DEST`, `DMU_INTERRUPT_DEST`, and `DMU_INTERRUPT_DEST2`: destination fields for DCCG VSYNC/perfmon events, DMCUB timers/GPINT/mailboxes/outboxes, DMU perfmon, ABM0-ABM5, undefined-address fault, RBBMIF timeout, DMCU internal, and SCP interrupts.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code:

1. DCN 3.1 code includes `dcn_3_1_2_offset.h` and this mask header.
2. Register table initializers use token-pasting helpers such as `SR`, `SRI`, `SRI_DMUB`, `FD_SHIFT`, and `FD_MASK` to turn the generated names into addresses, masks, and shifts.
3. IRQ, resource, HW sequencer, perfmon, and DMUB code use those tables with register helper macros to read, write, update, acknowledge, or route hardware fields.
4. Hardware then interprets the programmed bits as interrupt status, interrupt enable, interrupt destination, timeout, security, timer, or perf counter state.

The macros do not express ordering rules. Callers must still manage DMCUB boot/reset, interrupt mask/ack ordering, write-one-to-clear semantics, timer latch sequencing, perf counter start/stop/reset, and power-domain readiness before touching these registers.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed GPU state:

- DMCU/DMCUB interrupt state: occurred bits, clear bits, routing bits, microcontroller enable bits, IRQ/XIRQ selection, mailbox readiness, GPINT, undefined-address fault, timer, and general-data events.
- Display interrupt-controller state: pending flags across the `DISP_INTERRUPT_STATUS*` continuation chain and destination fields that steer events to the selected interrupt path.
- RBBMIF security and timeout state: trust level/source ID, timeout delay and request hold, timeout client decode, ACK/mask, per-client timeout disable, FIFO state, read-timeout, and invalid-access diagnostics.
- DC perfmon state: event/counter selection, counter run/active state, counter values, interrupt status/clear/ack/mask, and counter-low/high value fields.
- GPU timer state: programmed start positions for vertical update/startup/ready/flip-related timestamps and selected timer-read channels.
- ABM and power-domain interrupt counters/status for ready/update and DCPG domain power transitions.

Persistence is hardware-defined. Configuration fields generally remain until reset, modeset, power gating, suspend/resume, or explicit reprogramming. Status, ACK, clear, interrupt, timeout, and counter fields may be sticky, write-one-to-clear, read-only, self-clearing, latched, or dependent on clock/power state. This header only provides bit layouts; consuming driver code and hardware documentation define the side effects.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.1.2 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h` for the corresponding register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/yellow_carp_offset.h` and DCN base-address definitions used by `BASE(reg..._BASE_IDX)`.
- Common AMD display register helpers in `reg_helper.h` and DMUB register helpers in `dmub_reg.h`.
- IRQ source IDs in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`, which name events such as RBBMIF timeout and DMCUB outbox interrupts.

Direct include sites in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`

Important integration patterns:

- `dmub_dcn31.c` builds `dmub_srv_dcn31_regs` using `DMUB_DCN31_REGS()`, `DMCUB_INTERNAL_REGS()`, `FD_MASK`, and `FD_SHIFT`, then uses `REG_GET`, `REG_UPDATE`, `REG_WRITE`, and related helpers for DMCUB reset, mailbox pointers, scratch registers, GPINT, firmware windows, and fault/debug state.
- `irq_service_dcn31.c` maps hardware source IDs to DAL IRQ sources and builds interrupt register entries with `IRQ_REG_ENTRY` and `IRQ_REG_ENTRY_DMUB`. The DMCUB outbox path uses DMUB interrupt enable/ack field definitions from the same generated header family.
- `dcn31_resource.c` includes this mask header for broad DCN register tables. In this chunk specifically, `HWSEQ_DCN31_REG_LIST()` references `RBBMIF_TIMEOUT_DIS` and `RBBMIF_TIMEOUT_DIS_2`, so the timeout-disable masks are part of display hardware-sequencer configuration.

## Risks And Edge Cases

- Generated field drift is the central risk. A wrong shift or mask compiles cleanly but makes `REG_UPDATE`/`REG_GET` touch the wrong bits in MMIO registers.
- Interrupt fields are side-effect-sensitive. Confusing occurred, clear, ack, mask, enable, route-select, and destination fields can cause stuck interrupts, missed interrupts, interrupt storms, or routing to the wrong handler.
- Many status and clear fields intentionally share the same bit position and mask. Generic read/modify/write code must respect write-one-to-clear and ACK semantics rather than treating every field as normal storage.
- The `DISP_INTERRUPT_STATUS*` chain uses continuation bits. Incorrect masks for continuation fields can hide pending interrupts in later status registers or make software believe no further status register needs inspection.
- DMCUB mailbox/timer/GPINT/undefined-address-fault bits sit on firmware communication paths. Incorrect masks can break command completion, outbox notification, diagnostics, or firmware recovery.
- RBBMIF timeout controls are diagnostic and fault-containment sensitive. Bad timeout-disable masks can either hide real bus timeouts or falsely report hangs and invalid accesses.
- Perfmon masks affect debug and telemetry paths. Incorrect event, active, interrupt, or counter-value fields can corrupt performance counters or leave perfmon interrupts uncleared.
- ABM and DCPG power-domain interrupt fields span multiple continuation registers and destination registers. Instance-number mistakes can affect only higher ABM instances or specific display power domains, making issues hardware-configuration dependent.
- This is an artificial chunk. It starts at the tail of `DMCU_PERFMON_INTERRUPT_STATUS3` and stops after the first `DCPG_INTERRUPT_DEST` field; adjacent chunks are required for complete file-level claims.

## Test Signals

Useful validation combines generated-header consistency checks with hardware behavior:

- Build AMDGPU/DC with DCN 3.1 support enabled; missing or renamed field macros should fail in `dmub_dcn31.c`, `irq_service_dcn31.c`, `dcn31_resource.c`, and their register-table initializers.
- Mechanically compare every `__SHIFT`/`_MASK` pair in lines 2467-4750 against AMD's authoritative DCN 3.1.2 register database and the matching `dcn_3_1_2_offset.h` register names.
- Validate that every field used by `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_SHIFT`, and `FD_MASK` in DCN 3.1 paths has the expected mask width and shift position.
- Exercise DMCUB boot/reset, GPINT commands, inbox/outbox notification, firmware diagnostics, undefined-address fault reporting, suspend/resume, and recovery from forced DMCUB hangs.
- Exercise interrupt delivery for vblank/vstartup, vupdate no-lock, page flip, HPD/HPDRX, DMCUB outbox, ABM ready/update, DCPG power transitions, DSC/perfmon, and RBBMIF timeout events.
- Trigger and verify RBBMIF timeout diagnostics where possible: timeout client decode, timeout ACK, mask behavior, invalid-access flags, and per-client timeout-disable programming.
- Run display modesets across one to six pipes, DSC-capable modes, backlight/ABM paths, multi-display configurations, and suspend/resume while watching for stuck interrupts, lost vblank/pageflip events, hotplug storms, DMCUB mailbox stalls, RBBMIF timeout messages, and perfmon interrupt leaks.

## Cross-Chunk Notes

Previous chunks own the beginning of the DMCU perfmon interrupt status area, including most of `DMCU_PERFMON_INTERRUPT_STATUS3`. Later chunks continue `DCPG_INTERRUPT_DEST` and the remaining DCN 3.1.2 shift/mask namespace. The final per-file research document should merge adjacent chunks before making complete claims about all DMCU, DCPG, DMUB, IRQ destination, or display interrupt-controller fields in `dcn_3_1_2_sh_mask.h`.
