# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 2453-4726

## Scope And Purpose

This chunk is a generated AMD DCN 2.1 register shift/mask header segment. It contains no executable C logic; its interface is a dense set of preprocessor constants that describe hardware register bit positions and already-shifted masks. The names follow the generated AMD display convention:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

The matching offset header, `dcn_2_1_0_offset.h`, supplies the MMIO register addresses. Driver code combines the offset and shift/mask headers through AMD display helpers such as `FD_MASK`, `FD_SHIFT`, `FN`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and IRQ table macros.

The covered range begins in the middle of `DMCU_INTERRUPT_TO_UC_EN_MASK`, covers the DMCU-to-microcontroller interrupt routing, DMCU mailbox/scratch/perfmon/DPRX interrupt groups, and then moves into the `dce_dc_dmu_ihc_dispdec` address block. In that DMU interrupt-harvester block it defines GPU timer start-position fields, the display interrupt status continuation chain through `DISP_INTERRUPT_STATUS_CONTINUE24`, and the first interrupt destination selectors for DCCG and DMU. The chunk ends inside `DMU_INTERRUPT_DEST`, so the destination coverage continues in the next source chunk.

The path is under a local `ceph-client` source mirror, but this source is AMDGPU display hardware metadata. It is unrelated to Ceph filesystem protocol or persistence logic.

## Register Groups Covered

This line range contains 78 visible register/comment groups and roughly 2,194 generated field constants, split across DMCU and DMU/IHC hardware surfaces.

Major DMCU-related groups:

- `DMCU_INTERRUPT_TO_UC_EN_MASK_1`: enables delivery of OTG0-5 range timing update interrupts and a generic DMCU interrupt to the display microcontroller.
- `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL` and `_1`: selects XIRQ/IRQ routing for ABM1 ready/update interrupts, MCP, static-screen, DCPG power up/down, vblank, range timing update, and generic DMCU interrupt sources.
- `DC_DMCU_SCRATCH`: a full-width DMCU scratch register.
- `DMCU_INT_CNT` and `DMCU_INT_CNT_CONTINUE`: 8-bit interrupt counters for ABM, static-screen, and DCPG power-transition interrupts.
- `DMCU_FW_CHECKSUM_SMPL_BYTE_POS`: low/high checksum sample byte-position selectors.
- `DMCU_UC_CLK_GATING_CNTL`: microcontroller IRAM/ERAM read-delay fields and RBBM read clock-gating enable.
- `MASTER_COMM_DATA_REG1-3`, `MASTER_COMM_CMD_REG`, `MASTER_COMM_CNTL_REG`, `SLAVE_COMM_DATA_REG1-3`, `SLAVE_COMM_CMD_REG`, and `SLAVE_COMM_CNTL_REG`: byte-lane data registers and command/status controls for a DMCU master/slave communication mailbox.
- `DMCU_PERFMON_INTERRUPT_STATUS1-5`: occurred/clear status bits for DMCU perfmon counters across DCPG domains, DIO, DCCG, PHY, DCHUBBUB, DSCC, DSC_TOP, OPTC, and other display subblocks.
- `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK1-5`: delivery-enable masks for those perfmon interrupts.
- `DMCU_PERFMON_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1-5`: interrupt-line selection bits for those perfmon sources.
- `DMCU_DPRX_INTERRUPT_STATUS1`, `DMCU_DPRX_INTERRUPT_TO_UC_EN_MASK1`, and `DMCU_DPRX_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1`: DisplayPort receiver event status, microcontroller enable, and line-selection fields. The fields cover cable detect/lost, link bandwidth, training pattern changes, downspread, enhanced framing, lane count, HPD/IRQ, AUX interactions, MST, LTTPR, panel replay, HDCP, and link-loss style events for DPRX0.
- `DMCU_INTERRUPT_STATUS_CONTINUE`, `DMCU_INTERRUPT_TO_UC_EN_MASK_CONTINUE`, and `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL_CONTINUE`: additional DMCU status, enable, and IRQ-select fields for DCPG domains 6-21, DSC input underflow/core errors, DIO/DCCG/PHY/VGA hotplug and perfmon interrupts.
- `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL_CONT2`, `DMCU_INTERRUPT_STATUS_2`, and `DMCU_INTERRUPT_TO_UC_EN_MASK_2`: continuation fields for DMCUB timer, GPINT, inbox/outbox, general data, undefined-address fault, DMU perfmon, RBBMIF timeout, DMCU internal/SCP, DCCG VSYNC latch/perfmon, and DCPG domain 22-25 power events.

Major DMU/IHC display interrupt groups:

- `DC_GPU_TIMER_START_POSITION_V_UPDATE`, `DC_GPU_TIMER_START_POSITION_VSTARTUP`, `DC_GPU_TIMER_START_POSITION_VREADY`, `DC_GPU_TIMER_START_POSITION_FLIP`, `DC_GPU_TIMER_START_POSITION_V_UPDATE_NO_LOCK`, and `DC_GPU_TIMER_START_POSITION_FLIP_AWAY`: per-display timer start-position fields, generally three-bit lanes spaced every four bits for display pipes D1-D6 or D1-D8 depending on event family.
- `DC_GPU_TIMER_READ` and `DC_GPU_TIMER_READ_CNTL`: full-width GPU timer read data, read select, and read-enable fields.
- `DISP_INTERRUPT_STATUS` and `DISP_INTERRUPT_STATUS_CONTINUE` through `DISP_INTERRUPT_STATUS_CONTINUE24`: the display interrupt status chain. It includes vblank/vline, OTG, HUBP flip and flip-away, DPP, MPC, OPP, DIO, DCCG, PHY, DCHUBBUB, DMCU/DMCUB, DCPG, DSC, DSCC, perfmon, hotplug, timer, inbox/outbox, general data, fault, and continuation-link bits.
- `DCCG_INTERRUPT_DEST`: destination controls for DCCG VSYNC latch interrupts on OTG0-5 and DCCG perfmon counter interrupts.
- `DMU_INTERRUPT_DEST`: destination controls for DMCUB timers, GPINT0/1/2, inbox0/1 ready/done, outbox0/1 ready/done, DMU perfmon, DMCU ABM ready/update, undefined-address fault, RBBMIF timeout, DMCU internal, and SCP interrupts. This group continues after the chunk boundary.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or callable APIs in this chunk. The important exported contract is the generated macro namespace itself.

Important macro families:

- `*_STATUS*__*_OCCURRED__SHIFT` and `*_STATUS*__*_OCCURRED_MASK`: used to read whether a hardware interrupt/event is latched.
- `*_STATUS*__*_CLEAR__SHIFT` and `*_STATUS*__*_CLEAR_MASK`: paired clear bits for status registers. Callers must know whether a register is write-one-to-clear, read-clear, or uses other hardware-specific semantics; the generated header only gives bit layout.
- `*_TO_UC_EN_MASK*__*_TO_UC_EN_*`: microcontroller interrupt enable masks.
- `*_XIRQ_IRQ_SEL*__*_XIRQ_IRQ_SEL_*`: selection masks for the DMCU interrupt line/path.
- `*_INT_CNT*`: counter fields, usually byte lanes that pack multiple counters in one 32-bit register.
- `MASTER_COMM_*` and `SLAVE_COMM_*`: byte-lane data and command/status fields for DMCU communication registers.
- `DISP_INTERRUPT_STATUS_CONTINUE*__DISP_INTERRUPT_STATUS_CONTINUE<N>_*`: continuation bits that stitch the interrupt status scan chain across multiple registers.
- `*_INTERRUPT_DEST`: destination-routing bits used by the interrupt harvester fabric to choose where a source is delivered.

Representative consumers in the local AMDGPU display tree include:

- `display/dmub/src/dmub_dcn21.c`, which includes `dcn_2_1_0_offset.h` and this header, then builds `dmub_srv_dcn21_regs` by expanding `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)` into DMUB register tables.
- `display/dmub/src/dmub_reg.h`, where `FD_SHIFT`, `FD_MASK`, `FN`, `REG_SET`, `REG_UPDATE`, and `REG_GET` concatenate the register/field tokens defined by generated headers.
- `display/dc/irq/dcn21/irq_service_dcn21.c`, which includes the same DCN 2.1 headers and uses generated register masks in IRQ source table entries such as DMCUB outbox enable/ack handling.
- `include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`, which maps interrupt source IDs and context IDs to hardware status-chain names such as `DMCUB_OUTBOX_LOW_PRIORITY_READY_INTERRUPT` in `DISP_INTERRUPT_STATUS_CONTINUE24`.
- `display/amdgpu_dm/amdgpu_dm.c`, which registers the DMCUB outbox source ID with AMDGPU IRQ handling and connects it to Display Core interrupt registration.

## Control Flow

This header has no local runtime control flow. It is declarative metadata used by code that performs MMIO reads, writes, field updates, and interrupt table construction.

The typical runtime path is:

1. A DCN 2.1 driver component selects a symbolic register and field.
2. The offset helper resolves `mm<REGISTER>` and `mm<REGISTER>_BASE_IDX` from `dcn_2_1_0_offset.h`.
3. The field helper resolves `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` from this header.
4. The register helper packs, updates, or extracts the field value and performs an MMIO transaction.

For DMUB/DMCU service setup, `dmub_dcn21.c` uses this header to initialize a per-ASIC table of common DMUB register offsets, masks, and shifts. Later DMUB service code reads and writes DMCUB control, mailbox, interrupt, scratch, and timer fields through that table.

For interrupt handling, `irq_service_dcn21.c` maps hardware source IDs to `enum dc_irq_source` values. For the DMCUB low-priority outbox interrupt, the DCN 2.1 IRQ table enables `DMCUB_INTERRUPT_ENABLE.DMCUB_OUTBOX1_READY_INT_EN` and acknowledges `DMCUB_INTERRUPT_ACK.DMCUB_OUTBOX1_READY_INT_ACK` through generated masks. The source-ID table also documents that the low-priority outbox ready interrupt is represented in the display status chain as `DMCUB_OUTBOX_LOW_PRIORITY_READY_INTERRUPT` in `DISP_INTERRUPT_STATUS_CONTINUE24`.

For the large `DISP_INTERRUPT_STATUS*` chain, driver control flow is distributed across the interrupt harvester and Display Core IRQ service. The generated status bits are the hardware facts the service code relies on; this file does not encode the scan order, ack policy, or ISR dispatch logic.

## State And Persistence Behavior

The macros themselves are compile-time constants and hold no state. The state represented by this range is hardware register state in the DCN 2.1 display engine.

State categories represented here:

- DMCU interrupt policy: enable bits decide which ABM, static-screen, DCPG, vblank, OTG range timing, perfmon, DPRX, DMCUB, and fault events are sent to the microcontroller.
- DMCU interrupt routing: XIRQ/IRQ select fields choose which interrupt path is used for each source.
- DMCU event status and counters: occurred/clear bits and packed counters expose interrupt occurrence and event frequency for selected sources.
- DMCU communication state: master/slave communication data bytes, commands, and status bits represent a register mailbox between host/DMCU-side actors.
- DMCU scratch/checksum/clock-gating state: scratch registers, firmware checksum byte-position selectors, read-delay fields, and clock-gating enables are persistent register configuration until reset or reprogramming.
- DPRX state: status/enable/routing bits represent DisplayPort receiver events and AUX/link/HPD-related changes observed by the hardware.
- DMU/IHC display interrupt state: the `DISP_INTERRUPT_STATUS*` chain represents latched or level interrupt state for almost every display subblock in this DCN generation.
- GPU timer observation: timer read controls and timer start-position fields configure or observe timer alignment for vupdate, vstartup, vready, flip, vupdate-without-lock, and flip-away events.
- Interrupt destination state: `DCCG_INTERRUPT_DEST` and `DMU_INTERRUPT_DEST` configure where selected interrupt-harvester events are delivered.

Hardware persistence depends on the register. Configuration fields usually remain active until driver reprogramming, display reset, power gating, or GPU reset. Status, clear, ack, counter, and read-trigger fields may be sticky, edge-triggered, write-one-to-clear, self-clearing, or snapshot-driven. This generated header does not declare those semantics; consumers must preserve reserved bits and follow the hardware programming sequence from the register spec or existing driver code.

## Dependencies And Integration Points

Direct dependencies:

- `dcn_2_1_0_offset.h`: provides the paired register offsets and base-index macros.
- `renoir_ip_offset.h`: supplies the IP block base macros used by DCN 2.1/Renoir display register calculations.
- AMD display register helpers such as `REG_OFFSET`, `FD_SHIFT`, `FD_MASK`, `FN`, `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, and `REG_GET`.
- DC interrupt source identifiers in `include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`.

Key integration points:

- DMUB firmware service (`display/dmub/src/dmub_dcn21.c` and shared DMUB service code): builds per-ASIC register tables and later uses them for firmware boot, mailbox movement, interrupt ack, timer reads, scratch registers, and diagnostics.
- DCN 2.1 IRQ service (`display/dc/irq/dcn21/irq_service_dcn21.c`): maps hardware interrupt source IDs to Display Core IRQ sources and uses generated masks for enable/ack register table entries.
- AMDGPU DM IRQ registration (`display/amdgpu_dm/amdgpu_dm.c`): registers the DMCUB outbox interrupt source ID with the kernel IRQ layer and associates it with Display Core callbacks.
- Display power and clock management: DCPG domain power up/down bits, DMCU clock-gating fields, and DCCG/DIO/PHY/DCHUBBUB interrupt status bits connect this register metadata to power-gating, link, and display-clock transitions.
- DisplayPort receiver and hotplug handling: DPRX and HPD-like status bits feed firmware or interrupt paths that react to AUX, link training, MST, HPD IRQ, cable, and link state changes.
- Performance monitoring and diagnostics: perfmon interrupt status/enable/routing groups provide low-level observability for display subblocks and can be used in debug or validation paths.

## Risks And Edge Cases

- The macros are a hardware ABI. A wrong shift or mask can compile cleanly while reading or writing the wrong bit, leading to missed interrupts, unacknowledged interrupt storms, broken DMUB mailbox notification, wrong DMCU routing, or incorrect power-event handling.
- This chunk begins and ends mid-register. `DMCU_INTERRUPT_TO_UC_EN_MASK` starts in the previous chunk, and `DMU_INTERRUPT_DEST` continues in the next chunk. Whole-register conclusions require reconciliation with adjacent chunk reports.
- Interrupt status and clear bits often share the same bit position. Code must use the correct access semantics for the specific register; treating an occurred bit as an ordinary read/write bit can clear events accidentally or fail to clear sticky interrupts.
- Continuation bits are structurally important. The `DISP_INTERRUPT_STATUS_CONTINUE<N>` fields at bit 31 link the interrupt status chain; incorrect values can prevent higher-numbered status registers from being scanned or interpreted correctly by hardware/firmware tooling.
- Repeated source families are easy to drift. DCPG domains, OTG0-5 events, D1-D8 timer lanes, DSC0-5 events, DSCC/DSC perfmon counters, and DPRX link fields are patterned but not always identical. Manual edits risk one instance being wrong while neighboring instances look correct.
- DMCU and DMCUB names are similar but not interchangeable. This chunk includes legacy DMCU communication/routing fields and newer DMCUB interrupt/mailbox-visible status bits; confusing the two can route or acknowledge the wrong firmware-side event.
- Destination routing fields can change interrupt delivery target rather than merely enabling a source. Incorrect `DCCG_INTERRUPT_DEST` or `DMU_INTERRUPT_DEST` programming can make an event visible to the wrong client or invisible to the expected handler.
- Timer start-position masks pack several small fields into a 32-bit register. Full-register writes without read-modify-write discipline can corrupt adjacent display pipe timer settings.
- DPRX fields represent many link-state transitions. A mask mismatch may only appear on specific DisplayPort scenarios such as MST, HPD IRQ, AUX transactions, LTTPR, panel replay, downspread, training-pattern changes, or HDCP events.
- Power-domain events for DCPG domains 0-25 interact with display power gating. Incorrect enable, status, or counter bits can hide power-transition failures or trigger firmware work at the wrong time.

## Test Signals

Useful validation signals for changes touching this chunk are mostly compile-time plus hardware integration behavior:

- Build AMDGPU/DC with DCN 2.1 support. Missing or renamed shift/mask macros should fail in `dmub_dcn21.c`, `irq_service_dcn21.c`, or shared register-helper expansions.
- Compare the generated DCN 2.1 masks against the authoritative register database and adjacent DCN generations to catch accidental shifts in repeated DMCU, DMU, DCPG, DSC, and OTG families.
- Boot DCN 2.1/Renoir-class hardware and verify DMUB firmware starts, DMUB/DMCU scratch and mailbox access works, and DMCUB outbox interrupts are delivered without hangs or interrupt storms.
- Exercise DMCUB outbox notification paths, including low-priority outbox ready handling, and confirm `amdgpu_dm` interrupt registration maps source ID `0x68` to `DC_IRQ_SOURCE_DMCUB_OUTBOX` as expected.
- Run display modesets, page flips, vblank waits, vline events, vupdate-no-lock events, and flip-away scenarios across multiple pipes. Watch for missing events, spurious events, or broken per-pipe indexing.
- Test DisplayPort hotplug/link scenarios that can trigger DPRX fields: cable attach/detach, HPD IRQ, link training, MST, AUX traffic, bandwidth/lane-count changes, downspread toggles, and HDCP or panel-replay paths where available.
- Stress display power transitions and suspend/resume to validate DCPG power up/down event reporting and DMCU routing through power-gated states.
- Check kernel logs and debug counters for DMCUB undefined address faults, RBBMIF timeout, DMCU internal/SCP interrupts, DSC input underflow/core errors, DCCG/DMU perfmon interrupts, and persistent uncleared display interrupt status bits.
- Use register dumps or hardware diagnostics to confirm `DISP_INTERRUPT_STATUS_CONTINUE23/24` and `DCCG_INTERRUPT_DEST`/`DMU_INTERRUPT_DEST` fields align with expected source/destination routing.
