# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 2452-4727

## Scope And Purpose

This chunk is a generated AMD DCN 3.0.2 shift/mask header segment. It contains no executable C logic, functions, structs, enums, or mutable variables. Its exported interface is a dense set of preprocessor constants that describe bit positions and already-shifted masks for DCN display MMIO register fields:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

The range spans 2,276 source lines and contains 2,194 `#define` entries: 1,093 shift constants and 1,101 mask constants. It starts at the tail of `DMCU_INTERRUPT_STATUS`, covers DMCU interrupt routing/status/counters/mailboxes, DMCU perfmon and DPRX interrupt groups, then switches to the `dce_dc_dmu_ihc_dispdec` address block for GPU timer and display interrupt-harvester status registers. It ends at the first `DC_GPU_TIMER_START_POSITION_FLIP_AWAY` field, so whole-register coverage continues in the next chunk.

The source path is under a local `ceph-client` mirror, but the file itself is AMDGPU display hardware metadata. It is not Ceph filesystem code and has no filesystem persistence behavior.

## Register Groups Covered

Visible DMCU groups:

- `DMCU_INTERRUPT_STATUS_1`: occurred/clear bits for OTG0-5 range timing updates, generic DMCU interrupt, and ABM2-4 histogram/luma/backlight-update events.
- `DMCU_INTERRUPT_TO_HOST_EN_MASK`: host-delivery enable fields for ABM0-4, SCP, UC internal, and UC register read-timeout interrupts.
- `DMCU_INTERRUPT_TO_UC_EN_MASK` and `_1`: microcontroller-delivery enables for ABM, MCP, static-screen, external software, DCPG domain 0-5 power up/down, vblank, range timing update, and generic DMCU sources.
- `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL` and `_1`: XIRQ/IRQ routing selectors for the same families of DMCU, DCPG, vblank, static-screen, MCP, external software, and range timing sources.
- `DC_DMCU_SCRATCH`, `DMCU_FW_CHECKSUM_SMPL_BYTE_POS`, and `DMCU_UC_CLK_GATING_CNTL`: scratch, firmware-checksum sample byte-position, and microcontroller memory/read clock-gating fields.
- `DMCU_INT_CNT` plus `DMCU_INT_CNT_CONTINUE`, `DMCU_INT_CNT_CONT2`, `DMCU_INT_CNT_CONT3`, and `DMCU_INT_CNT_CONT4`: packed 8-bit interrupt counters for ABM, static-screen, DCPG, DMCUB timer, GPINT, mailbox, fault, timeout, internal, SCP, DCCG, and extended DCPG sources.
- `MASTER_COMM_DATA_REG1-3`, `MASTER_COMM_CMD_REG`, `MASTER_COMM_CNTL_REG`, `SLAVE_COMM_DATA_REG1-3`, `SLAVE_COMM_CMD_REG`, and `SLAVE_COMM_CNTL_REG`: byte-lane data and command/status registers for DMCU master/slave communication.
- `DMCU_PERFMON_INTERRUPT_STATUS1-5`, `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK1-5`, and `DMCU_PERFMON_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1-5`: occurred/clear, enable, and interrupt-line selection fields for DMCU perfmon interrupts from DCPG domains, DIO, DCCG, PHY, DCHUBBUB, DSCC, DSC_TOP, OPTC, DSC, and related display subblocks.
- `DMCU_DPRX_INTERRUPT_STATUS1`, `DMCU_DPRX_INTERRUPT_TO_UC_EN_MASK1`, and `DMCU_DPRX_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1`: DisplayPort receiver event status, delivery enable, and XIRQ/IRQ selection fields for stream MSA/VBID/vertical/SDP events, FEC-ready, cable/link/configuration changes, HPD, MST, AUX, LTTPR, panel replay, HDCP, and link-loss style events.
- `DMCU_INTERRUPT_STATUS_CONTINUE`, `DMCU_INTERRUPT_TO_UC_EN_MASK_CONTINUE`, and `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL_CONTINUE`: continuation status/enable/routing for DCPG domains 6-21, DSC underflow/core errors, DIO/DCCG/PHY/VGA hotplug, perfmon, and memory power events.
- `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL_CONT2`, `DMCU_INTERRUPT_STATUS_2`, and `DMCU_INTERRUPT_TO_UC_EN_MASK_2`: DMCUB timer, GPINT, inbox/outbox, general-data, undefined-address fault, DMU perfmon, RBBMIF timeout, DMCU internal/SCP, DCCG VSYNC latch/perfmon, and DCPG domain 22-25 event fields.

Visible DMU/IHC groups:

- `DC_GPU_TIMER_START_POSITION_V_UPDATE`, `DC_GPU_TIMER_START_POSITION_VSTARTUP`, `DC_GPU_TIMER_START_POSITION_VREADY`, `DC_GPU_TIMER_START_POSITION_FLIP`, `DC_GPU_TIMER_START_POSITION_V_UPDATE_NO_LOCK`, and the opening of `DC_GPU_TIMER_START_POSITION_FLIP_AWAY`: per-display timer start-position selectors. Most fields are three-bit lanes packed every four bits for display pipes D1-D6, while flip covers D1-D8.
- `DC_GPU_TIMER_READ` and `DC_GPU_TIMER_READ_CNTL`: timer read data, read-select, read-enable, and read-status fields.
- `DISP_INTERRUPT_STATUS` and `DISP_INTERRUPT_STATUS_CONTINUE` through `DISP_INTERRUPT_STATUS_CONTINUE22`: display interrupt-harvester status chain entries. The covered status sources include vblank/vline, OTG, HUBP flip/flip-away, DPP, MPC, OPP, DIO, DCCG, PHY, DCHUBBUB, DMCU/DMCUB, DCPG, DSC, DSCC, perfmon, hotplug, timer, inbox/outbox, general-data, fault, I2C/DDC, DP stream-disable/fast-training, VREADY, VSTARTUP, VUPDATE, VUPDATE-no-lock, and DRR v-total-reach events.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The important contract is the generated macro namespace consumed by AMD display register helpers.

Important macro families:

- `*_STATUS*__*_OCCURRED__SHIFT` and `*_STATUS*__*_OCCURRED_MASK`: identify latched or level interrupt/status bits.
- `*_STATUS*__*_CLEAR__SHIFT` and `*_STATUS*__*_CLEAR_MASK`: paired clear bits. In many groups, occurred and clear share the same bit position, but access semantics are hardware-defined outside this header.
- `*_TO_HOST_EN_MASK*__*_MASK`: host interrupt-delivery enable fields.
- `*_TO_UC_EN_MASK*__*_TO_UC_EN*`: DMCU-side interrupt-delivery enable fields.
- `*_XIRQ_IRQ_SEL*__*_XIRQ_IRQ_SEL*`: fields selecting the microcontroller interrupt path for a source.
- `*_INT_CNT*`: packed counter fields, typically byte-wide fields in a 32-bit register.
- `MASTER_COMM_*` and `SLAVE_COMM_*`: mailbox-style data, command, and status bitfields.
- `DISP_INTERRUPT_STATUS_CONTINUE<N>__DISP_INTERRUPT_STATUS_CONTINUE<N+1>`: bit-31 continuation fields that stitch the display interrupt status chain across registers.
- `DC_GPU_TIMER_START_POSITION_*`: packed per-pipe timer-position selectors for vupdate, vstartup, vready, flip, vupdate-without-lock, and flip-away timing capture.

Concrete companion addresses are supplied by `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h`. Examples in the covered range include `mmDMCU_INTERRUPT_STATUS_1`, `mmDMCU_DPRX_INTERRUPT_STATUS1`, `mmDISP_INTERRUPT_STATUS_CONTINUE22`, `mmDC_GPU_TIMER_START_POSITION_VREADY`, `mmDCCG_INTERRUPT_DEST`, `mmDMU_INTERRUPT_DEST`, and `mmDMU_INTERRUPT_DEST2`.

The DCN 3.0.2 resource code includes this header directly in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c`, together with `dimgrey_cavefish_ip_offset.h`, `dcn_3_0_2_offset.h`, DPCS register headers, and the shared DC register helper infrastructure. The local helper pattern uses token concatenation macros such as `SF(reg_name, field_name, post_fix)` to bind generated `__SHIFT` and `_MASK` constants into per-block register tables.

Shared DMUB register helpers in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_reg.h` show the broader generated-header contract: `FD_SHIFT(reg, field)` expands to `reg__field__SHIFT`, `FD_MASK(reg, field)` expands to `reg__field_MASK`, and `REG_SET`, `REG_UPDATE`, and `REG_GET` combine those shifts/masks with offsets for MMIO field access.

## Control Flow And Runtime Behavior

This header has no local control flow. Runtime behavior is indirect:

1. DCN 3.0.2 display code selects a symbolic register and field.
2. The offset header resolves the MMIO address through `mm<REGISTER>` and `mm<REGISTER>_BASE_IDX`.
3. This header resolves the field shift and mask.
4. Register helpers perform read-modify-write, full writes, or field extraction through the AMDGPU display MMIO path.

The hardware flows represented by this chunk are interrupt-heavy:

- DMCU interrupt reporting uses status/clear bits, enable masks, routing selectors, and counters to expose ABM, static-screen, DCPG, vblank, OTG range-update, perfmon, DPRX, DMCUB mailbox, fault, timeout, and SCP events.
- DMCU communication uses master/slave data, command, and status fields as a register mailbox surface between host/firmware-facing components.
- DMCU perfmon and DPRX flows expose low-level validation and event-delivery state for display subblocks and DisplayPort receiver/link changes.
- DMU/IHC display interrupt reporting uses the `DISP_INTERRUPT_STATUS*` continuation chain to surface display events to the interrupt-harvester path. `irq_service_dcn302.c` maps many of the corresponding source IDs to Display Core IRQ sources, including vblank/vstartup, vline0, page flip, vupdate-no-lock, HPD/HPDRX, and DMCUB outbox events.
- GPU timer start-position registers configure or identify the event point used for timer capture around vupdate, vstartup, vready, page flip, vupdate without lock, and flip-away events.

Because this is declarative hardware metadata, sequencing rules such as when to enable a source, when to clear a sticky bit, and whether a status bit is level, pulse, write-one-to-clear, self-clearing, or read-only are not encoded here. Those rules live in hardware specifications and in the display/IRQ/DMUB code using the macros.

## State And Persistence Behavior

The macros are compile-time constants and hold no state. They describe persistent or transient state in memory-mapped DCN 3.0.2 display registers.

State categories represented here:

- Interrupt policy state: host-enable, microcontroller-enable, and XIRQ/IRQ selection bits determine whether and where events are delivered.
- Interrupt observation state: occurred/status bits and continuation bits represent latched or level event state for DMCU, DMCUB, DCPG, OTG, HUBP, DPP, MPC, OPP, DIO, DCCG, PHY, DCHUBBUB, DSC, DSCC, I2C/DDC, HPD, and timer sources.
- Interrupt clear/ack state: `*_CLEAR` fields are used to acknowledge or clear selected hardware events, subject to per-register semantics.
- Counter state: `DMCU_INT_CNT*` fields pack event counters that can be read by diagnostics or firmware-facing code.
- Mailbox state: `MASTER_COMM_*` and `SLAVE_COMM_*` fields hold byte data, commands, and status for DMCU communication.
- Firmware/control state: scratch, checksum byte-position, and clock-gating fields persist until reset, power transition, or driver reprogramming.
- GPU timer state: timer read controls and start-position selectors affect timing capture and observation across display pipes.

Configuration fields generally persist until explicitly changed, display hardware is reset, power-gated state is lost, or the GPU is reinitialized. Status, clear, timer-read, and counter fields can be sticky, transient, read-triggered, or self-clearing; this generated header does not distinguish those behaviors.

## Dependencies And Integration Points

Direct dependencies:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h` for matching register offsets and base-index macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dimgrey_cavefish_ip_offset.h` for the DCN base-address segments used by DCN 3.0.2 resource code.
- AMD display register helper macros in files such as `display/dc/resource/dcn302/dcn302_resource.c` and shared helper headers that concatenate register/field names with `__SHIFT` and `_MASK`.
- Interrupt source definitions in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`, which names sources that correspond to many `DISP_INTERRUPT_STATUS*` fields. For example, the status-chain entries in this chunk include source names for ABM0, DCPG domain 8-15 power events, OTG vupdate-no-lock, and DRR v-total-reach interrupts.

Key integration points:

- DCN 3.0.2 resource initialization in `display/dc/resource/dcn302/dcn302_resource.c`, which includes this generated header and builds register/shift/mask tables for DCN 3.0.2 display blocks.
- DCN 3.0.2 IRQ service in `display/dc/irq/dcn302/irq_service_dcn302.c`, which maps interrupt source IDs to `enum dc_irq_source` values for vblank/vstartup, vline0, page flip, vupdate-no-lock, DMCUB outbox, and HPD paths. That file includes the DCN 3.0.0 generated headers for its IRQ table, so the merge lane should distinguish the dcn302 resource consumer from the dcn302 IRQ service's inherited register-table include choice.
- DMUB/DMCU service paths that use generated masks and shifts through `FD_SHIFT`, `FD_MASK`, `REG_SET`, `REG_UPDATE`, and `REG_GET` style helpers for firmware boot, mailbox, outbox/inbox, scratch, timer, and interrupt acknowledgement code.
- Display power, clock, and diagnostics paths that rely on DCPG power events, DCCG/DMU perfmon, DMCU clock gating, DSC underflow/core errors, DIO/PHY/DCHUBBUB/DMCU memory power events, and DMCUB fault/timeout events.
- DisplayPort/HPD/AUX-related handling through DPRX status/enable/routing fields and the broader display interrupt status chain.

## Risks And Edge Cases

- These constants are a hardware ABI. A wrong mask or shift can compile cleanly while reading or writing the wrong register bit, causing missed interrupts, unacknowledged interrupt storms, DMCU/DMCUB notification failure, incorrect power-event reporting, or corrupted timer configuration.
- The chunk begins mid-register and ends mid-register. The first lines are the tail of `DMCU_INTERRUPT_STATUS`, and `DC_GPU_TIMER_START_POSITION_FLIP_AWAY` continues after line 4727. Whole-register analysis requires adjacent chunks.
- Occurred and clear fields often share the same bit. Consumers must use correct write-one-to-clear or ack semantics rather than treating all fields as ordinary writable configuration.
- Names ending in `_MASK_MASK` are valid generated names where the logical field name contains `MASK`, such as interrupt enable mask fields. Tooling that strips `_MASK` naively can misparse them.
- Continuation bits at bit 31 are structurally important in `DISP_INTERRUPT_STATUS_CONTINUE*` registers. An incorrect continuation field can hide later status registers from software or diagnostics.
- Repeated source families are patterned but not safe to infer manually. ABM0-4, DCPG domains 0-25, OTG0-6, D1-D8 timer lanes, DSC0-5, perfmon counters, and DPRX stream/link fields have similar naming with generation-specific gaps and limits.
- DMCU and DMCUB fields are adjacent in this range but refer to different firmware/control surfaces. Confusing legacy DMCU interrupt routing with DMCUB mailbox/timer/fault status can route or acknowledge the wrong event.
- Packed timer-position fields require read-modify-write discipline. Full-register writes can corrupt neighboring per-pipe settings because fields are only three bits wide and spaced every four bits.
- DPRX fields cover scenarios that may only be exercised by specific hardware setups, such as MST, AUX traffic, LTTPR, panel replay, HDCP, downspread changes, training-pattern changes, and link-loss events.
- DCN 3.0.2 has five primary display resources in `dcn302_resource.c`, while some generated status/timer fields expose six or eight pipe slots inherited from the register block. Consumers must respect runtime resource caps rather than assuming every generated lane is usable on this ASIC.

## Test Signals

Useful validation signals for changes touching this chunk:

- Build AMDGPU/DC with DCN 3.0.2 support. Missing or renamed macros should fail where `dcn302_resource.c` expands generated shift/mask tables or where shared helper macros reference this namespace.
- Compare the generated DCN 3.0.2 shifts and masks against the matching AMD register database and `dcn_3_0_2_offset.h`, especially for repeated DMCU, DMCUB, DCPG, OTG, DSC, DPRX, timer, and display interrupt continuation groups.
- Boot a DCN 3.0.2/Dimgrey Cavefish class GPU and verify display bring-up, DMUB/DMCU firmware communication, scratch/mailbox access, and DMCUB outbox interrupt delivery.
- Exercise vblank/vstartup, vline0, page flip, vupdate-no-lock, VREADY, flip-away, and DRR v-total-reach paths across all active pipes. Watch for missing events, spurious events, or incorrect per-pipe source mapping.
- Stress HPD/HPDRX, AUX, DisplayPort link training, MST, HDCP, LTTPR, panel replay, downspread, lane-count, and bandwidth-change scenarios where available to cover DPRX event fields.
- Stress suspend/resume and display power gating to validate DCPG power up/down reporting, DIO/PHY/DCHUBBUB/DMCU memory power status, DCCG/DMU perfmon events, and restoration of interrupt routing.
- Monitor kernel logs and register dumps for uncleared `DISP_INTERRUPT_STATUS*` bits, DMCUB undefined-address faults, RBBMIF timeout, DMCU internal/SCP events, DSC input underflow/core errors, DPHY/DPRX link errors, and interrupt storms.
- Add or run generated-header consistency checks that verify every `__SHIFT` has a corresponding `_MASK`, masks fit in 32 bits, and repeated instance families retain expected parity with DCN 3.0.0/3.0.1/3.0.2 where the hardware spec requires it.

## Open Questions For Merge Lane

- Reconcile the opening tail of `DMCU_INTERRUPT_STATUS` with the previous chunk and the trailing `DC_GPU_TIMER_START_POSITION_FLIP_AWAY` definitions with the next chunk.
- Confirm whether the dcn302 IRQ service's inclusion of DCN 3.0.0 generated headers is intentional shared-layout reuse, while `dcn302_resource.c` uses the DCN 3.0.2 headers directly.
- Identify exact runtime consumers of the DMCU perfmon, DPRX, and display interrupt status continuation fields before the final per-file report describes concrete call sites beyond the generated-table and IRQ source mapping layers.
