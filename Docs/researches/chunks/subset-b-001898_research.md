# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 2509-4798

## Scope

This chunk is a generated DCN 3.1.6 register-field shift/mask slice. It contains only preprocessor constants and register/address-block comments: `_SHIFT` macros encode field bit positions and `_MASK` macros encode raw register bitmasks. There are no C functions, structs, enums, loops, branches, allocations, or direct MMIO accesses in this range.

The range starts in the middle of `DMCU_INTERRUPT_STATUS`, after earlier ABM/MCP/static-screen fields, and continues through legacy DMCU interrupt routing, DMCU command mailboxes, DMCU perfmon and DPRX interrupt routing, RBBMIF timeout/security fields, DC perfmon instance 2 fields, GPU timer readback fields, and the display interrupt status chain through the first field of `DISP_INTERRUPT_STATUS_CONTINUE18`. Neighboring chunks are needed for the complete file-level view of both the leading `DMCU_INTERRUPT_STATUS` register and the trailing continuation-18 register.

## Purpose And Hardware Surface

This header supplies the bit-layout ABI used by AMDGPU Display Core and DMUB support code for DCN 3.1.6 display hardware. Companion generated headers provide register offsets; this file provides masks and shifts consumed by register-helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_WRITE`, and generated table builders.

Major hardware areas represented here:

- DMCU interrupt status and routing: ABM ready/update events, static-screen events, OTG range/timing update events, DCPG power-up/power-down events, vblank events, DMCU generic/internal/SCP/MCP events, DCIO DPCS TX events, host enable masks, uC enable masks, and XIRQ/IRQ selection masks.
- DMCU command and scratch registers: `DC_DMCU_SCRATCH`, ABM interrupt counters, firmware checksum byte-position sampling, uC clock-gating controls, master/slave command/data byte lanes, and mailbox interrupt/in-progress controls.
- DMCU perfmon interrupts: occurred/clear, route-to-uC, and XIRQ/IRQ-select fields for DMU, DIO, DCCG, HPO, HUBP0-7, HUBBUB, DPP0-7, writeback, DCCG perfmon2, MMHUBBUB, MPC, OPP, OPTC, HDA, and DSC0-5 counter events.
- DPRX interrupt routing: stream decode events for SD0P0/SD1P0, DPRX DPHY threshold/error/lock/alignment/deskw failure events, AUX/I2C/CPU/message-timeout events, plus enable and XIRQ/IRQ-select routing for those same receiver-side events.
- DMU RBBMIF security and timeout diagnostics: DMCUB RBBMIF security level/trust/source fields, timeout delay/hold configuration, timeout client decode status, timeout address/op/read-write/ack/mask fields, per-client timeout-disable bits for clients 0-38, and invalid-access status.
- DC perfmon instance 2: performance counter event/value selection, increment/run/restart/interrupt controls, counted-value and hardware-stop selectors, per-counter state readback, perfmon run state, counter-off interrupt control/status/ack/type, clock enable, high/low value readback, and current-value interrupt status/ack fields.
- IHC display interrupt status chain: top-level display interrupt aggregation for OPTC underflow, OTG snapshot/force/trigger/vsync/vtotal/vertical/DRR events, DIG fast-training and stream-disable events, HPD and HPDRX, AUX SW/LS/GTC events, I2C completion, RBBMIF timeout, DMCU and ABM signals, MCIF/DWB/WBSCL events, perfmon events, DCCG latches, MPCC stalls, VGA CRT, HUBBUB VM/timeout/compbuf events, DCPG domain events, HUBP vblank/vline/timeout/flip/flip-away events, and the continuation-bit linkage across status registers.

## Important Definitions

The exported API is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field least-significant bit.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted bitmask in the register value.
- `// addressBlock: ...` comments group registers by hardware address block.
- `//<REGISTER>` comments group fields belonging to each register.

Important macro families in this chunk:

- `DMCU_INTERRUPT_STATUS`, `DMCU_INTERRUPT_STATUS_1`, `DMCU_INTERRUPT_STATUS_CONTINUE`, and `DMCU_INTERRUPT_STATUS_2` expose latched DMCU-side events and matching clear bits. Many occurred and clear fields intentionally share the same bit position and mask, making write-one-clear handling dependent on the caller's register helper sequence.
- `DMCU_INTERRUPT_TO_HOST_EN_MASK`, `DMCU_INTERRUPT_TO_UC_EN_MASK*`, and `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL*` define which DMCU-side events are exposed to the host, routed to the microcontroller, or selected as XIRQ/IRQ inputs. The continued variants extend routing for DCPG domains, DCIO DPCS TX errors, and DCIO DPCS TXA-TXG events.
- `DMCU_INT_CNT`, `DMCU_INT_CNT_CONTINUE`, `DMCU_INT_CNT_CONT2`, and `DMCU_INT_CNT_CONT3` provide packed 8-bit interrupt counters for ABM0-3 high-gain ready, local-store ready, and backlight-update events.
- `MASTER_COMM_*` and `SLAVE_COMM_*` define four byte lanes per command/data register plus interrupt and message-in-progress bits. Shared DCE ABM/DMCU helpers use similarly named fields to send legacy microcontroller commands such as ABM, backlight, PSR, PHY sync, and EDID-related commands.
- `DMCU_PERFMON_INTERRUPT_STATUS1..5`, `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK1..5`, and `DMCU_PERFMON_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1..5` repeat the same occurred/clear, enable, and IRQ-select pattern across display performance monitor blocks.
- `DMCU_DPRX_INTERRUPT_STATUS1`, `DMCU_DPRX_INTERRUPT_TO_UC_EN_MASK1`, and `DMCU_DPRX_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1` cover DisplayPort receiver-side stream decode, physical layer, AUX, I2C, CPU, and message timeout interrupts for port 0.
- `DMCUB_RBBMIF_SEC_CNTL` is in the foreground-security address block and defines security level, trust level, and source ID fields for DMCUB RBBMIF traffic.
- `RBBMIF_*` registers cover timeout programming and diagnostics. `RBBMIF_TIMEOUT_DIS` and `_DIS_2` provide one bit per timeout client, while `RBBMIF_STATUS_FLAG` exposes state, read-timeout, FIFO empty/full, invalid-access flag, invalid-access type, and invalid-access address.
- `DC_PERFMON2_*` fields implement the second DC perfmon register set, including counter selection, run/stop policy, interrupt policy, state readback, current-value interrupt status/ack, and high/low result readout.
- `DC_GPU_TIMER_*` fields select and read GPU timer values aligned with D1-D6 vupdate, vstartup, and nominal-vsync timing positions.
- `DISP_INTERRUPT_STATUS` through `DISP_INTERRUPT_STATUS_CONTINUE17` define a linked interrupt summary chain. Bit 31 in each register indicates the next continuation register has pending status. Line 4798 begins `DISP_INTERRUPT_STATUS_CONTINUE18` with `AZ_PERFMON_COUNTER0_INTERRUPT__SHIFT`; the remaining fields are outside this chunk.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears when DCN 3.1.6-specific tables combine these constants with matching offsets from `dcn_3_1_6_offset.h`, then shared display code performs MMIO reads/writes through register helpers.

Typical runtime flow:

1. DCN316 resource, DMUB, interrupt, ABM, DMCU, perfmon, or hardware-sequencing code selects a register offset from a generated register table.
2. Register helpers use this header's masks and shifts to pack fields, decode status bits, perform read/modify/write updates, or write clear/ack bits.
3. The hardware side latches interrupt state, routes events to host/uC/IRQ paths, advances mailbox handshakes, updates counters, reports timeout diagnostics, or returns timer/perfmon values.

The state represented here is hardware register state, not persistent driver-owned memory:

- Persistent configuration includes interrupt routing masks, XIRQ/IRQ selection bits, timeout delay/hold controls, per-client RBBMIF timeout-disable policy, DMCUB RBBMIF security/trust/source attributes, DMCU clock-gating controls, mailbox command/data bytes, perfmon event/run/interrupt selection, and GPU timer read selectors.
- Volatile readback includes interrupt occurred bits, ABM interrupt counters, mailbox in-progress state, RBBMIF timeout clients, timeout address/op/read-write status, RBBMIF FIFO/invalid-access state, perfmon counter state and values, current-value interrupt status, GPU timer reads, and display interrupt summary-chain bits.
- Side-effecting fields include clear, ack, and interrupt-mask bits in DMCU status, DPRX status, perfmon status, RBBMIF timeout status, and DC perfmon current-value interrupt registers. Because many clear/ack fields share bit positions with status fields, broad writes or stale read/modify/write values can clear diagnostics unintentionally.

## Dependencies And Integration Points

This chunk depends on generated-name consistency across the DCN 3.1.6 register-header family. It is paired with `dcn_3_1_6_offset.h` and consumed by DCN316 display code through macro-expanded register and mask tables.

Primary integration points include:

- `display/dmub/src/dmub_dcn316.c` includes this header and `dcn_3_1_6_offset.h` to build `dmub_srv_dcn316_regs`. The table stores DCN31-family DMUB register offsets plus field masks/shifts for the shared DMUB service layer.
- `display/dmub/src/dmub_dcn31.c` uses the resulting field tables for DMUB reset, boot, secure-region programming, inbox/outbox pointer management, GPINT acking, firmware status scratch reads, debug collection, and interrupt enable/ack handling.
- `display/dc/resource/dcn316/dcn316_resource.c` includes this header to populate DCN316 resource tables. The hardware sequencer register list includes `RBBMIF_TIMEOUT_DIS` and `RBBMIF_TIMEOUT_DIS_2`, and the mask/shift lists feed shared DCN31 hardware sequencing and power-management logic.
- Shared DCE/DMCU/ABM helpers (`display/dc/dce/dce_dmcu.*`, `dce_abm.*`) use `MASTER_COMM_CMD_REG`, `MASTER_COMM_DATA_REG*`, and `DMCU_INTERRUPT_TO_UC_EN_MASK` style fields to send DMCU commands and route DMCU events. On DCN316, DMUB is the primary firmware path, but generated DMCU definitions remain part of the register ABI and shared code surface.
- Interrupt services and display-core IRQ mapping depend on the IHC summary-chain fields for HPD/HPDRX, vblank/vline/vupdate-related OTG events, page-flip/HUBP events, AUX completion/GTC events, DMCU/ABM events, RBBMIF timeout, and perfmon interrupts. The continuation bit at bit 31 is part of the hardware's interrupt traversal contract.
- Perfmon, diagnostics, and debug tooling can use DMCU perfmon interrupt fields, DC perfmon2 fields, RBBMIF timeout status, and GPU timer registers to observe display pipeline health, counter thresholds, timeout causes, and timestamp alignment.

Because this file is only macro definitions, a missing macro usually fails at compile time where referenced. Incorrect numeric masks or shifts generally compile successfully but can misroute interrupts, lose clear/ack operations, corrupt security/timeout policy, or decode volatile diagnostics incorrectly at runtime.

## Risks And Maintenance Notes

- Numeric drift from the DCN 3.1.6 hardware register specification is the main risk. Wrong shifts/masks in this range affect interrupt delivery, interrupt clearing, mailbox byte packing, perfmon programming, timeout diagnosis, GPU timer selection, and DMUB/RBBMIF security policy.
- The chunk begins and ends inside logical register families. Merge/reconciliation should combine it with adjacent chunks before making final statements about full `DMCU_INTERRUPT_STATUS` and `DISP_INTERRUPT_STATUS_CONTINUE18` coverage.
- The DMCU interrupt routing blocks are highly repetitive across status, enable, and XIRQ/IRQ-select registers. Copy-generation mistakes can leave a field name valid but mapped to the wrong event, causing only specific power-domain, vblank, static-screen, ABM, or DCIO paths to fail.
- Occurred/clear and status/ack fields commonly share the same bit. Callers must treat them as side-effecting write-one-clear/write-one-ack fields, not ordinary persistent configuration bits.
- The display interrupt status chain relies on bit 31 continuation fields. If any continuation mask or shift is wrong, interrupt service code can stop scanning too early or chase the wrong summary state, leading to lost HPD, AUX, vblank, flip, underflow, timeout, or perfmon events.
- RBBMIF timeout-disable masks span 39 clients across two registers. Off-by-one client mapping can hide real timeouts or leave noisy clients enabled, which affects display hang diagnosis and recovery.
- Mailbox byte-lane fields are packed. Incorrect byte shifts in `MASTER_COMM_*` or `SLAVE_COMM_*` can transform a valid command into a different firmware command or corrupt command parameters.
- DC perfmon2 fields mix configuration, run state, current-value interrupt status, acks, high/low values, and read selectors. Broad updates risk changing counter source or clearing threshold events while reading values.
- Some macro families describe legacy DMCU-facing paths even on DMUB-era hardware. Consumers must confirm which firmware path owns a register before adding new runtime uses.

## Test Signals

Useful validation combines generated-header checks, build coverage, and hardware/runtime interrupt tests:

- Build AMDGPU Display Core with DCN316 enabled and ensure all `dcn_3_1_6_sh_mask.h` names referenced by `dmub_dcn316.c`, `dcn316_resource.c`, shared DMUB, DMCU/ABM, hardware sequencing, and IRQ code resolve.
- Run generated-header consistency checks that every in-scope field has matching `_SHIFT` and `_MASK` definitions where expected, masks fit in 32 bits, fields do not overlap unexpectedly inside each register, and repeated register families keep event ordering aligned.
- Compare this range against the authoritative DCN 3.1.6 register specification, especially DMCU interrupt route/clear fields, DPRX events, RBBMIF timeout client numbering, DC perfmon2 fields, and `DISP_INTERRUPT_STATUS_CONTINUE*` continuation bits.
- Exercise HPD/HPDRX, AUX software done, AUX link-service done, AUX GTC lock/error, DC I2C software done, vblank/vline/vupdate/DRR, page-flip/flip-away, underflow, WBSCL overflow, MPCC stall, HUBBUB VM fault/timeout, and DCPG power-domain interrupt paths on DCN316 hardware.
- Validate DMCU/ABM-related events where applicable: ABM ready/update interrupts, ABM counters, static-screen events, and mailbox command/data byte packing.
- Inject or observe RBBMIF timeout and invalid-access scenarios, confirming timeout address/op/read-write/ack/mask fields and per-client timeout-disable bits decode correctly.
- Test DMUB reset/boot/GPINT/debug paths on DCN316, since this generated header supplies the field masks and shifts used by the DMUB register table.
- Validate perfmon programming by selecting events, enabling counter/current-value interrupts, reading high/low values, acknowledging threshold events, and confirming the display interrupt status chain reports corresponding perfmon interrupts.
- Test suspend/resume and runtime power transitions with active displays, checking that DCPG power-up/power-down, RBBMIF timeout policy, DMUB/DMCU routing, and display interrupt traversal recover consistently.

## Chunk-Specific Summary

Lines 2509-4798 define a DCN 3.1.6 generated mask/shift slice for DMCU interrupt status/routing, DMCU mailbox and ABM counter fields, DMCU perfmon and DPRX interrupt routing, DMCUB/RBBMIF security and timeout diagnostics, DC perfmon2 controls/readback, GPU timer readback, and the IHC display interrupt status chain through the start of continuation 18. Correctness depends on exact bit positions, careful handling of clear/ack side effects, instance/event ordering across repeated macro families, and runtime validation of interrupt delivery, timeout diagnostics, DMUB table usage, perfmon behavior, and power-transition recovery.
