# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001656`: lines 1-2452, `Docs/researches/chunks/subset-b-001656_research.md`
- `subset-b-001657`: lines 2453-4726, `Docs/researches/chunks/subset-b-001657_research.md`
- `subset-b-001658`: lines 4727-7156, `Docs/researches/chunks/subset-b-001658_research.md`
- `subset-b-001659`: lines 7157-9803, `Docs/researches/chunks/subset-b-001659_research.md`
- `subset-b-001660`: lines 9804-12312, `Docs/researches/chunks/subset-b-001660_research.md`
- `subset-b-001661`: lines 12313-14826, `Docs/researches/chunks/subset-b-001661_research.md`
- `subset-b-001662`: lines 14827-17356, `Docs/researches/chunks/subset-b-001662_research.md`
- `subset-b-001663`: lines 17357-19859, `Docs/researches/chunks/subset-b-001663_research.md`
- `subset-b-001664`: lines 19860-22381, `Docs/researches/chunks/subset-b-001664_research.md`
- `subset-b-001665`: lines 22382-24866, `Docs/researches/chunks/subset-b-001665_research.md`
- `subset-b-001666`: lines 24867-27467, `Docs/researches/chunks/subset-b-001666_research.md`
- `subset-b-001667`: lines 27468-29926, `Docs/researches/chunks/subset-b-001667_research.md`
- `subset-b-001668`: lines 29927-32383, `Docs/researches/chunks/subset-b-001668_research.md`
- `subset-b-001669`: lines 32384-34755, `Docs/researches/chunks/subset-b-001669_research.md`
- `subset-b-001670`: lines 34756-37152, `Docs/researches/chunks/subset-b-001670_research.md`
- `subset-b-001671`: lines 37153-39580, `Docs/researches/chunks/subset-b-001671_research.md`
- `subset-b-001672`: lines 39581-42008, `Docs/researches/chunks/subset-b-001672_research.md`
- `subset-b-001673`: lines 42009-44390, `Docs/researches/chunks/subset-b-001673_research.md`
- `subset-b-001674`: lines 44391-46846, `Docs/researches/chunks/subset-b-001674_research.md`
- `subset-b-001675`: lines 46847-49414, `Docs/researches/chunks/subset-b-001675_research.md`
- `subset-b-001676`: lines 49415-51898, `Docs/researches/chunks/subset-b-001676_research.md`
- `subset-b-001677`: lines 51899-54266, `Docs/researches/chunks/subset-b-001677_research.md`
- `subset-b-001678`: lines 54267-56533, `Docs/researches/chunks/subset-b-001678_research.md`
- `subset-b-001679`: lines 56534-56648, `Docs/researches/chunks/subset-b-001679_research.md`

## Chunk Research

### subset-b-001656: lines 1-2452

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 1-2452

## Purpose

This chunk is the opening portion of the generated DCN 2.1.0 shift/mask header used by the AMD display driver. It does not implement executable logic; it publishes C preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for memory-mapped display hardware registers.

The covered range starts at the include guard and covers the first hardware address blocks in the header:

- MMHUBBUB VGA/display-decode fields for legacy VGA page addresses, render/mode control, VGA status, VGA interrupts, and per-display VGA routing.
- DCCG display clock generator fields for PHY pixel clock resynchronization, DP DTOs, reference clocks, clock-gating controls, DISPCLK/DPPCLK/DSCCLK DTO programming, audio DTOs, VSYNC counters, and test clock selection.
- DFS/Dentist display-clock divider fields for DISPCLK and DPPCLK frequency changes.
- DC performance monitor register fields for perfmon instances 0, 1, and 2.
- PLL macro reserved register masks.
- DMU/RBBMIF timeout/status fields, display power-gating domain fields, DMU clock/memory-power controls, and the beginning of DMCU control, firmware memory access, event, and interrupt masks.

The chunk ends at line 2452 inside the `DMCU_INTERRUPT_TO_UC_EN_MASK` register description, after the `DCPG_IHC_DOMAIN4_POWER_UP_INT_TO_UC_EN` shift field. The remaining fields for that register and the rest of the header are outside this chunk.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or runtime APIs defined in this chunk. The important interface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT`: bit offset for a field within a 32-bit MMIO register.
- `REGISTER__FIELD_MASK`: mask for the same field, already positioned in the register word.
- Include guard `_dcn_2_1_0_SH_MASK_HEADER`.

Typical consumers combine these macros with register-access helper layers such as `REG_GET`, `REG_UPDATE`, `REG_UPDATE_N`, `FD_MASK`, and `FD_SHIFT`. The paired offset header `dcn_2_1_0_offset.h` provides register addresses, while this file provides the bit layout needed to encode/decode fields at those addresses.

High-value register groups in this chunk include:

- VGA compatibility: `VGA_RENDER_CONTROL`, `VGA_SEQUENCER_RESET_CONTROL`, `VGA_MODE_CONTROL`, `VGA_HDP_CONTROL`, `VGA_CACHE_CONTROL`, `D1VGA_CONTROL` through `D6VGA_CONTROL`, `VGA_STATUS`, `VGA_INTERRUPT_CONTROL`, and `VGA_SOURCE_SELECT`.
- DCCG clocking: `PHYPLL[A-E]_PIXCLK_RESYNC_CNTL`, `DP_DTO_DBUF_EN`, `REFCLK_CNTL`, `DPREFCLK_CNTL`, `DCCG_DS_*`, `DCCG_GTC_*`, `DISPCLK_FREQ_CHANGE_CNTL`, `DCCG_GATE_DISABLE_CNTL`, `DCCG_GATE_DISABLE_CNTL2`, `DPPCLK_DTO_CTRL`, `DSCCLK_DTO_CTRL`, and `DCCG_AUDIO_DTO_*`.
- Pixel-rate DTOs: `OTG0_PIXEL_RATE_CNTL` through `OTG3_PIXEL_RATE_CNTL`, `DP_DTO0_PHASE/MODULO` through `DP_DTO3_PHASE/MODULO`, and `OTG[0-3]_PHYPLL_PIXEL_RATE_CNTL`.
- Clock divider control: `DENTIST_DISPCLK_CNTL`.
- Performance counters: `DC_PERFMON0_*`, `DC_PERFMON1_*`, and `DC_PERFMON2_*`.
- Power and management: `DOMAIN[0-7,16-18]_PG_CONFIG/STATUS`, `DCPG_INTERRUPT_STATUS`, `DCPG_INTERRUPT_STATUS_2`, `DCPG_INTERRUPT_CONTROL_[1-3]`, `DC_IP_REQUEST_CNTL`, `DMU_CLK_CNTL`, `DMU_MEM_PWR_CNTL`, `SMU_INTERRUPT_CONTROL`, and `DMU_MISC_ALLOW_DS_FORCE`.
- DMCU firmware/microcontroller access: `DMCU_CTRL`, `DMCU_STATUS`, firmware start/end/checksum registers, ERAM/IRAM access control/data registers, `DMCU_EVENT_TRIGGER`, `DMCU_UC_INTERNAL_INT_STATUS`, static-screen interrupt fields, and DMCU interrupt status/enable masks.

## Control Flow

This header has no control flow. At compile time, it expands into constants used by DCN 2.1 display code. Runtime control flow appears in the consuming modules when they:

1. Select a register address from `dcn_2_1_0_offset.h`.
2. Select a field mask and shift from this header.
3. Read, write, or poll the MMIO register through AMD display register helpers.

The implied hardware flows represented by the fields are state-machine oriented:

- VGA fields drive legacy display-memory mapping, sequencer reset behavior, per-pipe VGA enablement, status reporting, and interrupt clearing.
- DCCG fields configure display clock sources, pixel clock resync, fractional DTO phase/modulo values, audio DTO selection, VSYNC counter latching, clock gating, soft resets, and test clock routing.
- Dentist fields coordinate divider writes and change/done toggles for DISPCLK/DPPCLK changes.
- Perfmon fields select events, configure counter modes, start/stop conditions, interrupt reporting, and readback paths.
- Power-gating and DMCU interrupt fields expose request/status/clear/mask bits for display power domains and microcontroller-visible display events.

## State And Persistence Behavior

The header itself has no software state and performs no persistence. The state described by the constants lives in hardware registers. Writes made by consumers persist in the GPU display block until reset, power-gate transition, firmware action, or another driver write changes the same register.

Several field families are explicitly stateful at hardware level:

- `*_ENABLE`, `*_GATE_DISABLE`, `*_SOFT_RESET`, `*_POWER_FORCEON`, and `*_POWER_GATE` fields control persistent enable, gating, reset, and power-domain request state.
- `*_STATUS`, `*_CHG_DONE`, `*_DONETOG`, `*_INT_OCCURRED`, and `*_INT_STATUS` fields expose hardware state or latched events.
- Interrupt clear fields often share the same bit positions and masks as the corresponding occurred/status fields, for example in `DCCG_VSYNC_CNT_INT_CTRL`, `DMCU_SS_INTERRUPT_CNTL_STATUS`, and `DMCU_INTERRUPT_STATUS`.
- DTO phase/modulo and divider fields represent programmed clock ratios used continuously by display timing paths.
- DMCU ERAM/IRAM access fields describe host-visible windows into DMCU memory. Auto-increment and host-access-enable bits affect subsequent firmware memory transfers.

Because all masks are raw constants, the type and width semantics come from the consuming register helpers. Most masks are 32-bit values with an `L` suffix, and full-width fields use `0xFFFFFFFFL`.

## Dependencies

This chunk depends on the generated AMD display register naming scheme and the matching offset header for DCN 2.1. Consumers include:

- `display/dc/resource/dcn21/dcn21_resource.c`, which includes this header with `dcn_2_1_0_offset.h` and builds register tables through macros such as `SR`, `SRI`, and `SRIR`.
- `display/dmub/src/dmub_dcn21.c`, which includes this header to populate DMUB common register field masks and shifts through `FD_MASK` and `FD_SHIFT`.
- DCN 2.1 GPIO, IRQ service, and hardware translation code, which include this header for SoC-specific field layouts.
- Shared display modules such as clock manager, DCCG, audio, DMCU, and perfmon code paths that consume the generated field names through per-generation register structures.

The file must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h` for register addresses and base indices.
- DCN 2.1 resource and register-list macros that expect these exact field names.
- Hardware documentation for Renoir/DCN 2.1 display registers.

## Integration Points

The integration boundary is compile-time rather than call-time. DCN 2.1 driver components include this header to specialize generic display code for the DCN 2.1 register layout.

Practical integration examples visible in the tree include:

- `dmub_dcn21.c` maps DMCUB/DMUB common fields to masks and shifts. DMCU/DMCUB interrupt and memory-control fields in this chunk are part of that bridge between host driver and display microcontroller firmware.
- `dcn21_resource.c` uses this header while constructing hardware object register tables for the DCN 2.1 resource pool.
- Clock management code references `DENTIST_DISPCLK_CNTL` fields to read, update, and wait for DISPCLK/DPPCLK divider changes.
- DCE/DCN audio code uses `DCCG_AUDIO_DTO_SOURCE`, `DCCG_AUDIO_DTO0_PHASE/MODULE`, and `DCCG_AUDIO_DTO1_PHASE/MODULE` fields when programming audio clock DTOs.
- DMCU code uses `DMCU_INTERRUPT_TO_UC_EN_MASK`, `DMCU_INTERRUPT_STATUS`, and related fields to enable static-screen, ABM/backlight, vblank, and internal microcontroller interrupt paths.

The final per-file research should stitch this chunk with later chunks because many logical register blocks continue beyond line 2452, especially the DMCU interrupt-to-UC mask register and subsequent DCN display blocks.

## Risks And Edge Cases

- This is generated hardware-description code. A one-bit mask or shift error can misprogram display hardware while still compiling cleanly.
- Field names are part of a macro ABI used by generation-specific register tables. Renaming or removing macros can break consumers that build field tables with token-pasting macros.
- Several interrupt clear fields intentionally share bit positions and masks with occurred/status fields. Mechanical deduplication could remove meaningful aliases and break source readability or register-helper use.
- Full-width masks such as `0xFFFFFFFFL` and high-bit masks such as `0x80000000L` rely on consumers treating values as 32-bit register fields. Refactors should avoid sign-extension surprises when moving these constants through wider signed types.
- The chunk ends in the middle of `DMCU_INTERRUPT_TO_UC_EN_MASK`; any analysis of that register must include the next chunk before drawing completeness conclusions.
- Repeated per-instance blocks, such as `OTG0`-`OTG3`, `DPPCLK0`-`DPPCLK3`, `SYMCLK[A-E]`, and perfmon instances 0-2, are prone to generator or copy drift. Consumers often assume instance layouts are symmetric.
- Power-gating and clock-gating fields are order-sensitive at runtime. Incorrect masks can leave clocks forced on, gate clocks needed by active display paths, or misreport power-domain transitions.
- DMCU ERAM/IRAM host-access fields can affect firmware load/readback flows. Wrong masks may corrupt firmware upload, stall DMCU register reads, or prevent timeout interrupts from being enabled or cleared.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, register-table, and hardware bring-up checks:

- The AMD display driver should compile with DCN 2.1 enabled, with no missing field macros in resource, GPIO, IRQ, DMUB, DMCU, audio, DCCG, and clock-manager code.
- Generated register tables should contain the expected masks and shifts for `DENTIST_DISPCLK_CNTL`, `DCCG_AUDIO_DTO_SOURCE`, `DPPCLK_DTO_CTRL`, `DMCU_INTERRUPT_STATUS`, and `DMCU_INTERRUPT_TO_UC_EN_MASK`.
- Display bring-up on DCN 2.1 hardware should successfully program DISPCLK/DPPCLK and observe `DENTIST_*_CHG_DONE` fields during clock changes.
- DP/HDMI audio tests should validate DTO source, module, and phase programming through the `DCCG_AUDIO_DTO*` fields.
- Hotplug, vblank, static-screen, ABM/backlight, and DMCU internal interrupt tests should exercise the corresponding status, mask, and clear fields.
- Runtime power-management tests should enter and leave display power-gated states while checking domain desired-state and PGFSM status fields.
- Register dump tooling can compare repeated instance masks for OTG, DPPCLK, DSCCLK, SYMCLK, and perfmon blocks to detect unexpected asymmetry.
- Static checks can verify that every `__SHIFT`/`_MASK` pair is internally consistent, for example mask width starts at the declared shift and repeated aliases intentionally share the same bit positions.

### subset-b-001657: lines 2453-4726

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

### subset-b-001658: lines 4727-7156

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 4727-7156

## Purpose

This chunk is part of AMDGPU's generated DCN 2.1 register field shift/mask header. It contains no executable C logic; it publishes compile-time bit layout constants for DCN display hardware registers. Each field is exposed as paired preprocessor macros: `REGISTER__FIELD__SHIFT` gives the low bit position and `REGISTER__FIELD_MASK` gives the already-positioned bit mask used by AMD display register helpers.

The assigned range starts in the middle of `DMU_INTERRUPT_DEST` and then covers a large set of DCN 2.1 display interrupt-routing, writeback, memory-interface, performance-monitor, MMHUBBUB/VGAIF, and HDA Azalia stream fields:

- Interrupt destination registers for DMU/DMCUB, DCPG power domains, MMHUBBUB, writeback, DCHUB, DPP perf counters, MPC, OPP, OPTC, OTG0 through OTG5, DIG, I2C/DDC/HPD, DIO/DCIO, HPD, audio/Azalia, AUX, and DSC blocks.
- DWB/CNV writeback capture fields for writeback enable, clock/power configuration, crop/window/source dimensions, capture rate, stereo/new-content bits, update locking/status, test CRCs, debug access, soft reset, and warmup programming.
- WBSCL writeback scaler fields for coefficient RAM addressing/data, scaler mode, taps, destination size, horizontal/vertical ratios and initial phases, rounding/clamping, overflow and host-conflict interrupt status/ack/mask bits, CRC/debug, backpressure counters, and outside-pixel strategy.
- `DC_PERFMON3` and `DC_PERFMON4` fields for writeback/MMHUBBUB performance counter control, counter state, monitor control, captured values, interrupt status/ack, and readback selection.
- `MCIF_WB0` and `MCIF_WB1` fields for writeback buffer-manager control/status, buffer addresses and offsets, pitches, dimensions, buffer status, arbitration, SCLK/p-state/self-refresh behavior, VCE coordination, watermarks, QoS, security, and high address bits.
- MMHUBBUB/VGAIF fields for WBIF control, SMU watermark control, outstanding counters, VGA split source, memory power status/control, clock gating, soft reset, DMU interface error status, and client-unit ID.
- HDA Azalia stream indexed register access for stream instances 0 through the first line of stream 7 in this chunk.

Although the repository path is under a `ceph-client` source tree, this chunk is AMD GPU display hardware metadata. It has no Ceph protocol behavior, distributed filesystem state, block I/O path, or storage persistence semantics.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or global objects defined in this chunk. The public surface is the generated macro namespace consumed by display driver register tables.

Important macro families include:

- `DMU_INTERRUPT_DEST__*`: routes DMCUB timers, GPINTs, inbox/outbox events, perfmon interrupts, ABM events, undefined-address faults, RBBMIF timeouts, DMCU internal interrupts, and SCP interrupts toward interrupt handling destinations.
- `DCPG_INTERRUPT_DEST*__*`: describes power-up and power-down interrupt destination bits for DCPG domains 0 through 21, split between `DCPG_INTERRUPT_DEST` and `DCPG_INTERRUPT_DEST2`.
- `*_INTERRUPT_DEST__*`: field layouts for display interrupt routing across MMHUBBUB, WB/WBSCL, DCHUB, DCHUB perf counters, DPP perf counters, MPC, OPP, OPTC, OTG, DIG, DDC/HPD, DIO/DCIO, Azalia, AUX, and DSC. These route many classes of hardware events before normal IRQ source decoding sees them.
- `WB_ENABLE`, `WB_EC_CONFIG`, `WB_SOFT_RESET`, `WB_WARM_UP_MODE_CTL1`, and `WB_WARM_UP_MODE_CTL2`: enable, power/clock, reset, and warmup fields for the display writeback block.
- `CNV_MODE`, `CNV_WINDOW_START`, `CNV_WINDOW_SIZE`, `CNV_UPDATE`, `CNV_SOURCE_SIZE`, `CNV_TEST_*`, `WB_DEBUG_CTRL`, `WB_DBG_MODE`, `WB_HW_DEBUG`, and `CNV_TEST_DEBUG_*`: writeback converter and capture-control metadata for source sizing, cropping, output depth, frame capture, stereo/interlaced mode, update locking, CRC signatures, and debug indexing.
- `WBSCL_*`: writeback scaler metadata for coefficient RAM programming, output format/depth, tap counts, destination size, scale ratios, initial phases, rounding, overflow/host-conflict handling, CRC/debug, clamping, backpressure, and outside-pixel behavior.
- `DC_PERFMON3_*` and `DC_PERFMON4_*`: generic performance-monitor fields for event selection, compare/count modes, run/stop/restart control, interrupt enable/status/ack, counter state, captured-value high/low readback, and monitor state.
- `MCIF_WB0_*` and `MCIF_WB1_*`: memory-client interface writeback fields for buffer manager enable/lock/interrupts, VMID/fencing/security, current line/status, per-buffer tiling/rotation/burst/packing/address/pitch/resolution, arbitration, watermarks, p-state/self-refresh, QoS, VCE handshake, and 64-bit address high halves.
- `WBIF0_*`, `MMHUBBUB_*`, `MCIF_*`, `DMU_IF_ERR_STATUS`, and `MMHUBBUB_CLIENT_UNIT_ID`: MMHUBBUB and VGAIF fields for memory power/clock/reset control, write-combine controls, outstanding counters, client identifiers, and DMU interface error state.
- `AZF0STREAM[0-6]_AZALIA_STREAM_INDEX`, `AZF0STREAM[0-6]_AZALIA_STREAM_DATA`, and the first `AZF0STREAM7_AZALIA_STREAM_INDEX` field in this range: indexed HDA stream register access fields, with an 8-bit index, write-enable bit, and 32-bit data payload for completed stream instances.

These constants are normally paired with address macros from `dcn_2_1_0_offset.h`. Runtime register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, `FN`, and `FD` combine an address with the shift/mask pair to pack or extract a field value.

## Control Flow

This header chunk has no runtime control flow. It influences runtime behavior when included by DCN 2.1 code that builds register tables and manipulates hardware registers.

A typical control path is:

1. DCN 2.1 resource setup includes `dcn_2_1_0_offset.h` and this shift/mask header.
2. Per-block register tables select addresses for a hardware instance, often through macros such as `SR`, `SRI`, `SRI2_DWB`, or `SRI_DMUB`.
3. Matching shift and mask tables are initialized from the generated `*_SHIFT` and `*_MASK` macros.
4. Operational code calls register helpers such as `REG_UPDATE(CNV_MODE, CNV_FRAME_CAPTURE_EN, ...)` or `REG_GET(CNV_UPDATE, CNV_UPDATE_LOCK, ...)`.
5. The helper uses the field shift and mask from this header to update or read the correct bits in a memory-mapped hardware register.

The main behavioral control sequences represented by this chunk are interrupt routing, writeback capture setup, writeback scaler programming, MCIF writeback buffer operation, performance-monitor setup/readback, MMHUBBUB power/clock/reset control, and Azalia stream indexed access. The macros do not encode sequencing rules; those are enforced by consumers such as DWB code, IRQ service code, resource construction, DMUB support, and audio code.

For writeback specifically, `dcn20_dwb.c` uses these field names through `struct dcn20_dwbc_shift` and `struct dcn20_dwbc_mask`. It enables `WB_ENABLE`, programs `CNV_SOURCE_SIZE`, crop window fields, capture rate/depth, `WBSCL_MODE`, destination size, taps, ratios, init phases, rounding, clamping, and outside-pixel strategy, then enables capture through `CNV_FRAME_CAPTURE_EN`. Updates may lock `CNV_UPDATE_LOCK` while changing CNV/WBSCL fields. Disable clears frame capture and writeback enable, then toggles `WB_SOFT_RESET`.

For interrupts, `irq_service_dcn21.c` includes this file and uses generated masks in `IRQ_REG_ENTRY` style tables. The chunk's interrupt destination fields are lower-level routing metadata, while the IRQ service maps source IDs and context IDs to DAL interrupt sources such as vblank, vline, page flip, HPD, HPD RX, vupdate, and DMCUB outbox.

## State And Persistence Behavior

The file stores no software state and persists nothing itself. It describes state held in DCN 2.1 hardware registers.

The represented hardware state includes:

- Interrupt routing and interrupt status/control bits for many display blocks.
- Writeback enablement, capture mode, crop/source/window geometry, update lock/pending/taken bits, stereo/interlace/new-content flags, test CRC results, debug selectors, soft reset, and warmup programming.
- Writeback scaler coefficient RAM contents/selectors, scaler mode, tap counts, destination size, ratios, initial phases, rounding, clamps, outside-pixel strategy, backpressure counters, overflow flags, host-conflict flags, and acknowledgements.
- MCIF writeback buffer manager state, current line, buffer availability/active/overrun/frame-captured status, buffer addresses and dimensions, pitch, tiling/swap/rotation metadata, VMID/fence/security level, watermarks, arbitration, p-state controls, self-refresh, and QoS.
- Performance monitor configuration, active/run/restart state, counted values, compare/counter-off behavior, interrupt status/ack bits, and high/low readback registers.
- MMHUBBUB power, clock, soft-reset, memory-power, outstanding-counter, write-combine, client ID, and DMU interface error state.
- Azalia stream indexed-register address/data state.

Persistence is entirely hardware-defined. Some fields are latched programming values that remain until reprogrammed, reset, power-gated, or overwritten during a modeset. Some fields are live status bits. Some are sticky interrupt/status bits that require explicit acknowledgement. Some are request, lock, update, or reset bits whose effects depend on hardware timing. This generated header does not indicate which fields are read-only, write-one-to-clear, self-clearing, double-buffered, or safe to change while active.

## Dependencies And Integration Points

The companion address header is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`. The shift/mask constants in this chunk are only meaningful when paired with those register addresses and the DCN base offset macros from `renoir_ip_offset.h`.

Direct DCN 2.1 include points found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`

The most direct integration point for the writeback section is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_dwb.h`, which defines `DWBC_COMMON_REG_LIST_DCN2_0` and `DWBC_COMMON_MASK_SH_LIST_DCN2_0`. Those lists map the generated `WB_*`, `CNV_*`, and `WBSCL_*` macros into `struct dcn20_dwbc_registers`, `struct dcn20_dwbc_shift`, and `struct dcn20_dwbc_mask`. `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_dwb.c` then uses those tables to implement `dwb2_enable`, `dwb2_disable`, `dwb2_update`, `dwb2_is_enabled`, `dwb2_set_stereo`, `dwb2_set_new_content`, `dwb2_set_warmup`, and scaler setup.

Resource construction in `dcn21_resource.c` includes this generated header and constructs DCN 2.1 block register, shift, and mask tables for clock sources, DMCU/ABM/audio/DCCG/OPP/timing generators, DPP/HUBP/HUBBUB, DWB, GPIO, AUX/I2C, link encoders, and related display objects. This chunk contributes fields for several of those tables, especially DWB and audio/interrupt-related surfaces.

The DMCUB/DMUB integration includes this header in `dmub_dcn21.c`; DMUB register helpers use `FD_MASK` and `FD_SHIFT` to populate common DMUB field layouts. The chunk's `DMU_INTERRUPT_DEST` fields are adjacent to DMUB/DMCUB event routing, while common DMUB enable/ack registers are handled elsewhere in the generated file.

The audio integration uses Azalia register index/data fields through display audio code and resource tables. This chunk covers per-stream indexed access fields for streams 0 through 6 and begins stream 7; the rest of stream 7 is outside this chunk and should be covered by the following chunk.

## Risks And Edge Cases

- Generated-header drift is high risk: a wrong shift or mask compiles cleanly but writes the wrong hardware bits, causing silent display, capture, interrupt, power, audio, or diagnostic failures.
- This chunk starts and ends mid-register-family. `DMU_INTERRUPT_DEST` begins before line 4727, and `AZF0STREAM7_AZALIA_STREAM_INDEX` continues after line 7156. Any per-file summary must reconcile adjacent chunks before treating those families as complete.
- Interrupt destination fields are easy to confuse with interrupt enable, ack, and status fields. Destination routing mistakes can make otherwise-correct IRQ enable/ack code ineffective.
- MCIF writeback fields touch addresses, VMID, security, fencing, buffer status, arbitration, and p-state/self-refresh behavior. Bad masks here can lead to memory writeback corruption, hangs, overrun status storms, or security-domain mistakes.
- WBSCL coefficient and update fields are timing sensitive. Programming coefficient RAM or scaler geometry while the wrong buffer is active can cause host-conflict flags, visual corruption in captured frames, or stale scaler state.
- Some status and ack fields share registers with control bits. Consumers must preserve unrelated bits and use the correct write semantics; this header only supplies bit geometry.
- The writeback code has capability checks that reject luma scaling in DCN2-era DWB paths, but the register fields still expose scaler programming. Tests should distinguish unsupported policy from missing field definitions.
- Performance-monitor fields have repeated layouts across `DC_PERFMON3` and `DC_PERFMON4`; instance mix-ups can read or arm the wrong counter block.
- HDA Azalia stream registers use indexed access. Wrong index/write-enable masks can target the wrong indirect register even if the data register field is correct.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware/driver runtime checks:

- Build coverage for DCN 2.1 display code that includes `dcn_2_1_0_sh_mask.h`, especially `dcn21_resource.c`, `irq_service_dcn21.c`, GPIO translation/factory code, and `dmub_dcn21.c`.
- Compile-time initialization of DWB register, shift, and mask structs from `DWBC_COMMON_MASK_SH_LIST_DCN2_0`; missing or renamed macros should fail the build.
- Runtime DWB smoke tests: enable capture, program source/crop/window geometry, toggle `CNV_UPDATE_LOCK`, program WBSCL mode/taps/ratios, enable frame capture, verify `dwb2_is_enabled`, then disable and check `WB_SOFT_RESET` behavior.
- Captured-frame validation for DWB crop, output depth, stereo/new-content paths, WBSCL clamping, outside-pixel strategy, and scaler coefficients when supported.
- WBSCL diagnostic checks for overflow and host-conflict flags/ack/mask behavior under stress or deliberately invalid coefficient programming.
- MCIF writeback tests that verify buffer address high/low programming, pitch/resolution, frame-captured/buffer-active status, overrun handling, watermarks, and backpressure counters.
- IRQ tests for vblank, vline, page flip, HPD/HPD RX, vupdate, DMCUB outbox, AUX, DSC, and DWB-related interrupt delivery, with attention to destination routing versus enable/ack masks.
- Perfmon tests that arm counters, select events, read high/low captured values, and verify counter interrupt status/ack for `DC_PERFMON3` and `DC_PERFMON4`.
- Suspend/resume, modeset, power-gating, and ASIC-reset tests that reinitialize MMHUBBUB, DWB, MCIF, interrupt, and Azalia stream fields without relying on stale hardware state.

### subset-b-001659: lines 7157-9803

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 7157-9803

## Scope And Purpose

This chunk is generated AMD DCN 2.1 register bitfield metadata. It contains no executable C logic. Its purpose is to publish compile-time `__SHIFT` and `_MASK` constants used by AMDGPU display-core register helpers to pack, update, and read fields in MMIO registers.

The file is under a local `ceph-client` source mirror, but this path is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

The requested range contains 2,056 `#define` lines across 38 generated address blocks and 477 register comments. It is source-tree-aligned to a large generated header chunk, not to semantic subsystem boundaries. The slice starts with `AZF0STREAM7_AZALIA_STREAM_INDEX`, covers the remainder of the Azalia/HDA audio register family in this area, covers DCHUBBUB and VM request register fields, then enters the first HUBP/HUBPREQ/HUBPRET/CURSOR instance. It ends inside `DC_PERFMON7_PERFCOUNTER_CNTL`; the matching `DC_PERFMON7_PERFCOUNTER_CNTL2` and later perfmon fields are in the next chunk.

Major register families covered here:

- HDA/Azalia stream, endpoint, controller, root-node, stream 8-15, and input endpoint index/data fields.
- DC perfmon instance 5 for HDA and instance 6 for DCHUBBUB, plus the first register of instance 7 for HUBP0.
- DCHUBBUB SDPIF, VM framebuffer/aperture/HBM window, security-level, return-path DCC, CRC, arbitration, watermark, host-VM, timeout, reset, clock, and performance-measurement fields.
- DCN VM request interface contexts 0-15, default address, fault control/status, and fault address fields.
- HUBP0 surface configuration, tiling, viewport, request size, hubp control, clock, VMPG, and measurement fields.
- HUBPREQ0 surface address, metadata address, flip, surface-in-use, TTU/QoS, VM aperture/TLB, prefetch, vblank/flip/nominal timing, cursor, memory power, and delivery fields.
- HUBPRET0 request return, read-line, vblank/read-line interrupt, and memory power fields.
- CURSOR0_0 cursor image, position, size, hot spot, stereo, display metadata, QoS, software metadata, memory power, and underflow fields.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or storage objects in this range. The public interface is the macro set consumed by generated register lists and display register-access helpers.

Every complete field follows the generated naming contract:

- `<REGISTER>__<FIELD>__SHIFT` for bit offsets.
- `<REGISTER>__<FIELD>_MASK` for bit masks.

The corresponding register offsets live in the paired `dcn_2_1_0_offset.h` header. Consumer code normally reaches these constants through AMD display macros such as `SRI(...)`, `SR(...)`, `SE_SF(...)`, `LE_SF(...)`, `REG_SET`, `REG_SET_2`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT`, rather than by writing raw bit arithmetic.

Important macro families in this chunk:

- `AZF0STREAM7_AZALIA_STREAM_INDEX/DATA` and `AZF0STREAM8` through `AZF0STREAM15` expose indirect stream register index, write-enable, and data fields for HDA stream windows.
- `AZ_CLOCK_CNTL` defines Azalia clock-gating and test clock selection bits.
- `DC_PERFMON5_*`, `DC_PERFMON6_*`, and partial `DC_PERFMON7_PERFCOUNTER_CNTL` provide event selection, counted-value selection, increment/run modes, counter state, interrupt status/acknowledge, high/low counter values, and read selectors for display performance counters.
- `AZF0ENDPOINT[0-7]_*` and `AZF0INPUTENDPOINT[0-7]_*` define indirect endpoint register index/data fields for output and input codec endpoints.
- `AZALIA_*` controller fields cover DTO programming, SOCCLK control, underflow filler sample data, DMA control for data/BDL/CORB/RIRB paths, cyclic buffer sync, payload capabilities, stream arbitration, CRC controls/results, and Azalia memory power control/status.
- `AZALIA_F0_CODEC_*`, `CC_RCU_DC_AUDIO_*`, `REG_DC_AUDIO_*`, and `AZALIA_F0_GTC_GROUP_OFFSET*` expose codec root parameters, channel counts, resync FIFO, function parameters, power/reset controls, converter synchronization, audio port connectivity, and global-time-counter offsets.
- `DCHUBBUB_SDPIF_*`, `VM_REQUEST_PHYSICAL`, `DCN_VM_FB_*`, `DCN_VM_AGP_*`, and `DCN_VM_LOCAL_HBM_*` describe hubbub request routing, forced IO status, framebuffer/agp/HBM apertures, lock control, pipe security levels, and SDPIF memory power state.
- `DCHUBBUB_RET_PATH_DCC_CFG*`, `DCHUBBUB_RET_PATH_MEM_PWR_*`, and `DCHUBBUB_CRC*` define display compression return-path controls, memory power controls, CRC enable/selection/continual mode, and CRC result components.
- `DCHUBBUB_ARB_*`, `DCHUBBUB_GLOBAL_TIMER_CNTL`, `SURFACE_CHECK*`, `VTG[0-3]_CONTROL`, `DCHUBBUB_SOFT_RESET`, `DCHUBBUB_CLOCK_CNTL`, `DCFCLK_CNTL`, `DCHUBBUB_TIMEOUT_*`, and `FMON_CTRL` define arbitration thresholds, QoS forces, self-refresh/DRAM-clock-change watermarks A-D, watermark change request/done state, timeout detection/interrupt state, surface-check addresses, VTG enables, soft resets, clocks, host-VM behavior, and firmware-monitor control.
- `DCN_VM_CONTEXT[0-15]_*`, `DCN_VM_DEFAULT_ADDR_*`, `DCN_VM_FAULT_*` define VM context enable/page table ranges, default-address behavior, and fault reporting.
- `HUBP0_DCSURF_*`, `HUBP0_DCHUBP_*`, and `HUBP0_HUBP_*` cover surface pixel format/rotation/mirror, address/tiling, primary and secondary viewport geometry for luma/chroma planes, request sizing, blank enable, underflow/TTU disable, clock gating, and measurement windows.
- `HUBPREQ0_DCSURF_*`, `HUBPREQ0_DCN_*`, `HUBPREQ0_*PARAMETERS*`, and `HUBPREQ0_*DELIVERY*` describe surface pitch, primary/secondary and metadata addresses, flip control/status/interrupts, surface-in-use and earliest-in-use latches, TTU watermarks, VM/TLB aperture, blank offsets, destination dimensions, prefetch, vblank/flip/nom timing, cursor prefetch, and memory power state.
- `HUBPRET0_*` covers HUBP return path control, detile-buffer memory power, read-line control/ranges, vblank/read-line interrupt mask/type/clear/status bits, current/snapshot read-line value, and read-line inside/outside status.
- `CURSOR0_0_*` covers cursor enable, magnification, mode, TMZ/snoop/system flags, pitch, rotation/mirroring bypass, cursor address high/low, size, position, hot spot, stereo offsets, destination offset, cursor memory power, DMDATA address/control/QoS/status/software-data fields, and DMDATA underflow clear.

## Control Flow

This header chunk has no internal runtime control flow. Its data flow is compile-time substitution: DCN 2.1 code includes `dcn_2_1_0_sh_mask.h`, expands these generated macro names into per-register mask/shift tables, and then display register helpers use those constants during MMIO reads, writes, updates, waits, and interrupt acknowledgements.

Representative runtime flows in local consumers:

- `display/dc/resource/dcn21/dcn21_resource.c` includes this header when constructing DCN 2.1 resources and wiring generated register offset/mask tables into hubbub, hubp, irq, gpio, clock, and display-pipeline objects.
- `display/dmub/src/dmub_dcn21.c` includes this header with `dcn_2_1_0_offset.h` and `renoir_ip_offset.h` for DMUB-facing DCN 2.1 register access.
- `display/dc/irq/dcn21/irq_service_dcn21.c` includes these constants for interrupt source definitions and acknowledge/mask handling.
- `display/dc/gpio/dcn21/hw_factory_dcn21.c` and `display/dc/gpio/dcn21/hw_translate_dcn21.c` include the generated DCN 2.1 register headers as part of GPIO/DDC/HPD translation support.
- HUBBUB/HUBP runtime code programs watermarks, surface apertures, VM contexts, flip state, and cursor or DMDATA state using register-table abstractions backed by these field constants.

Because the file is declarative, it does not enforce required sequencing. Consumers must decide when to program apertures before enabling VM, when to update watermarks relative to modesets and clock changes, when to arm flips and wait for pending/in-use status, when to clear sticky interrupt/status fields, when to lock or latch double-buffered values, and when power-gated memories are safe to access.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. The macros describe fields in hardware MMIO registers.

Hardware state represented by this chunk includes:

- Azalia audio state: stream indirect register selectors, endpoint index/data windows, controller clocking, DTO and SOCCLK selection, DMA enables/positions, cyclic buffer sync, stream payload capacity, CRC controls/results, underflow filler samples, codec root parameters, power/reset controls, converter synchronization, audio connectivity, GTC offsets, and Azalia memory power status.
- Performance-counter state: event selectors, run/stop mode, counter active state, counted values, compare/off events, interrupt status, interrupt acknowledge, and high/low readback registers for DC perfmon instances.
- DCHUBBUB global state: SDPIF routing/security, framebuffer and AGP apertures, local HBM range locks, return-path DCC configuration, return-path memory power, CRC control/results, arbitration outstanding/saturation/QoS settings, watermark sets A-D, timeout detection, reset/clock controls, host-VM configuration, performance measurement, and FMON control.
- VM state: per-context page-table base/start/end addresses for contexts 0-15, default address programming, fault enable/retry/protection controls, fault status, and fault address readback.
- HUBP0/HUBPREQ0 state: surface format/tiling/viewports, request-size calculation, blank/underflow controls, clock gating, VM page settings, surface and metadata addresses, flip scheduling and completion/interrupt bits, surface-in-use latches, TTU/QoS watermarks, destination/prefetch/vblank/flip/nominal timing parameters, memory power status, and line delivery controls.
- HUBPRET0 state: return-path enabled/forced behavior, read-line interrupt ranges and masks, vblank/read-line clear/status bits, read-line snapshot/current values, and detile-buffer memory power.
- CURSOR0_0 state: cursor image address, dimensions, screen position, hot spot, stereo offsets, display metadata addresses and transfer status, metadata QoS, cursor memory power, underflow flag, and software metadata payload.

Persistence is hardware-specific and not encoded in this file. Some fields are programming knobs that remain until modeset, reset, suspend/resume, power-gating transition, or explicit rewrite. Others are read-only status, sticky interrupt/status, write-one-to-clear acknowledgement, self-clearing update/send requests, pending/in-use latches, CRC result fields, fault registers, or double-buffered values latched at vblank or flip boundaries. Names such as `*_STATUS`, `*_ACK`, `*_CLEAR`, `*_DONE`, `*_PENDING`, `*_INUSE`, `*_FAULT`, `*_UPDATED`, `*_FORCE`, and `*_LOCK` signal possible side effects but do not define access type by themselves.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header contract:

- `dcn_2_1_0_offset.h` supplies the matching MMIO register offsets for these field masks and shifts.
- `dcn_2_1_0_sh_mask.h` is included by DCN 2.1 resource, DMUB, IRQ, and GPIO code in the AMD display tree.
- DCN/DCE display code supplies register access helpers and mask/shift structs that combine offsets from the offset header with field constants from this header.
- Hardware programming logic in hubbub, hubp, cursor, IRQ, audio, and VM paths supplies the legal values and access ordering; this header only supplies bit positions.

Practical integration points include:

- Azalia/HDA display audio paths that program stream windows, codec endpoint/root registers, DMA controls, CRC validation, payload capacity, and audio power-gating behavior.
- HUBBUB memory/arbitration paths that program framebuffer apertures, AGP/HBM windows, self-refresh and DRAM-clock-change watermarks, host-VM behavior, timeouts, soft resets, clocks, and performance measurements.
- VM request handling and diagnostics that program per-context page tables and inspect fault status/address fields.
- HUBP0 plane paths that program surface format, tiling, addresses, viewports, pitch, request sizing, VM settings, flips, prefetch timing, TTU watermarks, and memory power state.
- Interrupt paths for surface flip, vblank/read-line, timeout, perf counter, fault, and status/ack fields.
- Cursor and display metadata paths that update cursor address/position/size/hot spot and DMDATA transfer/QoS/underflow state.

## Risks And Edge Cases

- These constants are hardware ABI. A wrong mask or shift can compile cleanly but write the wrong bits in a live display register.
- The chunk boundary is not semantic. It starts at `AZF0STREAM7_AZALIA_STREAM_INDEX` after stream 6 in the previous chunk and ends after the masks for `DC_PERFMON7_PERFCOUNTER_CNTL`, before `DC_PERFMON7_PERFCOUNTER_CNTL2` in the next chunk. Merge/reconciliation needs to preserve those boundary facts.
- Instance repetition is easy to damage manually. Endpoint 0-7, input endpoint 0-7, stream 8-15, VM context 0-15, watermark sets A-D, DCC config 0-7, and repeated surface address pairs have nearly identical layouts with only prefix/index changes.
- Status, clear, acknowledge, and programming bits are interleaved in the same register families. Treating every mask as ordinary read/write state can accidentally clear a sticky condition, miss an interrupt, or poll the wrong bit.
- Azalia DMA, cyclic-buffer, codec power, and stream index/data masks affect display audio. Drift can cause silent audio, channel-count errors, underflows, corrupted CRC validation, wrong endpoint access, or stuck DMA.
- VM aperture and page-table fields are address-critical. Incorrect high/low masks or context fields can route display fetches to wrong memory, trigger page faults, produce blank planes, or expose security/isolation bugs.
- Watermark, QoS, TTU, and prefetch timing masks are latency-critical. Bad fields can produce underflow, flicker, missed flips, power-state entry/exit stalls, or memory-clock-change instability.
- Flip and surface-in-use fields are synchronization-critical. Incorrect pending/clear/interrupt/in-use masks can lead to missed page-flip completion, tearing, stale addresses, or incorrect earliest-in-use accounting.
- Cursor and DMDATA masks directly affect visible overlay and metadata transfer. Bad address, TMZ/snoop/system, underflow-clear, QoS, size, hot-spot, or position masks can cause cursor corruption, metadata underflow, or memory-attribute mismatches.
- Power-gating memory control/status fields must be interpreted with hardware access rules. Writing force/disable bits at the wrong time can make dependent blocks inaccessible or leave status polling stuck.

## Test Signals

Useful validation is build coverage plus hardware/display behavior:

- Build AMDGPU/DC with DCN 2.1 support enabled. Missing or renamed macros should fail in DCN 2.1 resource, DMUB, IRQ, GPIO, hubbub, hubp, cursor, or audio paths.
- Compare this generated range against `dcn_2_1_0_offset.h` and adjacent DCN generation headers to catch instance-prefix, mask-width, or field-layout drift.
- Exercise display audio on DCN 2.1 hardware: stream setup, endpoint/root codec access, DMA enable/disable, channel count, suspend/resume, hotplug, CRC/error status, and audio playback without underflow.
- Exercise modesets and page flips on HUBP0-backed planes: surface address changes, metadata/DCC addresses, primary/chroma surfaces, VMID changes, flip interrupt delivery, surface-in-use latches, vblank timing, and suspend/resume.
- Validate VM fault behavior by checking that normal display fetches do not produce `DCN_VM_FAULT_STATUS`, and that deliberate invalid mappings report plausible fault addresses/status.
- Validate watermark and power behavior across memory-clock changes, self-refresh, DRAM-state transitions, high-bandwidth modes, multi-plane composition, and low-power entry/exit; watch for underflow, timeout interrupts, or flicker.
- Exercise cursor paths: enable/disable, size/mode changes, position/hot-spot updates, stereo offsets if relevant, TMZ/snoop/system memory attributes, DMDATA updates, and underflow-clear behavior.
- Read diagnostic counters/status: DC perfmon 5/6/partial 7, DCHUBBUB CRC results, timeout status, HUBPRET read-line/vblank interrupt state, HUBP measurement windows, memory power statuses, and DMDATA status. Stuck pending bits, wrong clears, repeated underflows, or implausible counter values are strong mask/shift regression signals.

### subset-b-001660: lines 9804-12312

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 9804-12312

## Purpose

This chunk is generated AMDGPU DCN 2.1 register field metadata. It contains no executable C logic; its API is a set of preprocessor constants that describe bit positions and masks for display-controller registers. Each decoded field is represented by paired macros:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit position.
- `REGISTER__FIELD_MASK` gives the already-positioned bit mask.

The path is under a local `ceph-client` source mirror, but the content is AMD display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

The range starts in the middle of `DC_PERFMON7_PERFCOUNTER_CNTL` mask definitions, then covers DCN hub pipe and request/return blocks for pipe instances 1 and 2, cursor blocks for instances 1 and 2, performance-monitor blocks 8 and 9, and the beginning of pipe instance 3 HUBP/HUBPREQ coverage. The chunk ends inside `HUBPREQ3_PER_LINE_DELIVERY`; later instance-3 fields continue in the next chunk.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or runtime storage objects in this range. The important surface is the generated macro namespace consumed by AMD display register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `REG_UPDATE`, `REG_READ`, `REG_WRITE`, `SRI(...)`, and `HUBP_SF(...)`.

Major macro families in this chunk:

- `DC_PERFMON7_*`, `DC_PERFMON8_*`, and `DC_PERFMON9_*`: performance counter control, counted-value type, hardware start/stop/count-off selection, per-counter state selection, perfmon global control, clock/run-enable control, interrupt status/ack fields, counter value low/high fields, and read selector fields. `DC_PERFMON7` is partial at the start of the chunk; `DC_PERFMON8` and `DC_PERFMON9` are complete in this range.
- `HUBP1_*`, `HUBP2_*`, and visible `HUBP3_*`: hub pipe display surface descriptors for pixel format, rotation, horizontal mirror, address/tiling configuration, primary and secondary viewport start/dimensions for luma and chroma planes, request-size configuration, request/control fields, clock control, virtual memory page config, debug DB, and DCFCLK/DPPCLK measurement-window controls.
- `HUBPREQ1_*`, `HUBPREQ2_*`, and visible `HUBPREQ3_*`: hub request surface programming, including luma/chroma pitch, VMID, primary/secondary surface and metadata addresses, surface control for TMZ/DCC/independent-64B-block fields, flip control and flip interrupts, in-use and earliest-in-use address reporting, request expansion modes, TTU/QoS watermarks, VM aperture and L1 TLB control, blanking/scaler/prefetch timing, vblank/flip/nominal PTE and meta-row timing parameters, per-line delivery timing, cursor request settings, reference-frequency conversion, DRQ limits, and memory power controls/status.
- `HUBPRET1_*` and `HUBPRET2_*`: hub return control, DET buffer plane base and crossbar selection, memory power control/status, read-line controls and read-line values, read-line status, and interrupt mask/type/status/ack fields for DET buffer underflow and read-line events.
- `CURSOR0_1_*` and `CURSOR0_2_*`: cursor control, cursor surface addresses, size, position, hot spot, stereo control, destination offset, cursor memory power control/status, and display metadata (`DMDATA`) address/control/QoS/status/software-data fields.

The repeated suffixes `1`, `2`, and `3` are hardware pipe or instance selectors. The field layouts are mostly cloned across instances, so a consumer normally writes generic HUBP code against `HUBPREQ0_*` masks in register-table macros and instantiates addresses per pipe with `SRI(..., id)`.

## Control Flow

This header chunk has no control flow. It is declarative hardware layout data used by code that builds register descriptor tables and then performs MMIO read-modify-write operations.

Runtime use follows this pattern:

1. DCN 2.1 display code includes `dcn_2_1_0_offset.h` for register addresses and `dcn_2_1_0_sh_mask.h` for field masks/shifts.
2. Resource, hubp, cursor, IRQ, GPIO, and DMUB code expands generated names through macros such as `SRI(...)`, `HUBP_SF(...)`, and related register-list helpers.
3. HUBP code programs surface format, tiling, addresses, viewport, VMID, flip control, DCC/TMZ, TTU/QoS, VM aperture, TLB, blanking, prefetch, and delivery timing fields during plane updates, flips, modesets, and power transitions.
4. Cursor and DMDATA code programs cursor address/geometry/hotspot/stereo state and metadata packets used by display streams.
5. IRQ and diagnostic paths read or acknowledge flip, HUBPRET, and perfmon status fields and may configure perf counters for display-block profiling.

The macros do not encode sequencing. Consumers must know when clocks are enabled, when double-buffered plane updates latch, how flip-pending and interrupt bits are cleared, and which fields are read-only status versus writable control.

## State And Persistence Behavior

The header stores no software state and persists nothing. It describes MMIO-backed GPU display hardware state.

The represented hardware state includes:

- Plane and surface state: pixel format, rotation, mirror, tiling/swizzle, address-bank configuration, luma/chroma viewport geometry, pitches, primary/secondary surface addresses, metadata addresses, DCC enablement, TMZ protection bits, and current in-use/earliest-in-use addresses.
- Flip and update state: flip type/mode, stereo sync, flip pending, surface update lock, master update lock status, triple buffering, VM update mode, flip clear/status bits, and flip-away interrupt fields.
- Memory-system and QoS state: request-size tuning, DRQ/CRQ/MRQ/PRQ expansion modes, TTU/QoS watermarks, request-delivery reference-cycle values for surfaces and cursors, prefetch ratios, vblank/flip/nominal PTE/meta timing, VM system aperture, and L1 TLB/system-access controls.
- Power and clock state: HUBP clock enable/disable and gating controls, DCFCLK/DPPCLK measurement controls, HUBPREQ/HUBPRET/CURSOR memory power force/disable/status fields, and virtual-memory page config.
- Cursor and metadata state: cursor mode, 2x magnify, pitch, alpha and color controls, surface address, size/position/hotspot/stereo settings, destination offsets, and DMDATA buffer address/control/status/QoS/software data.
- Diagnostics and events: HUBPRET read-line status and interrupt fields, HUBPREQ debug DB, perfmon counter active/state/interrupt/value fields, and measurement-window counters.

Persistence depends on hardware behavior outside this generated header. Some fields are normal configuration that remains until a modeset, plane update, power-gating transition, suspend/resume, or ASIC reset. Others are status, sticky interrupt, snapshot, self-clearing request, or read-only diagnostic fields. Names such as `*_INT_STATUS`, `*_ACK`, `*_CLEAR`, `*_PENDING`, `*_INUSE`, `*_MEM_PWR_STATUS`, and `*_CLOCK_ENABLE` should be treated as side-effect-sensitive unless the consuming driver path or hardware specification proves otherwise.

## Dependencies And Integration Points

This chunk depends on the matching generated address header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`

Direct include points for `dcn_2_1_0_sh_mask.h` in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`

The closest generic consumers are the DCN hub pipe implementations and register-list definitions under `display/dc/hubp`, especially `dcn10_hubp.h` and DCN 2.x variants. They define HUBP register lists for `DCSURF_*`, `HUBPREQ_*`, and `HUBPRET_*` registers, then bind fields with `HUBP_SF(HUBPREQ0_..., FIELD, mask_sh)` style macros. Runtime code in `dcn10_hubp.c` and DCN 2.x hubp files uses those tables to program plane addresses, viewport, tiling, DCC, flip behavior, VM/TLB state, QoS timing, DET/read-line state, and power controls.

IRQ integration uses `HUBPREQ` entries for surface-flip interrupts. DMUB integration includes the DCN 2.1 offset/mask headers so firmware mailbox and register access code can use the same generated register contract. Legacy memory-management code in adjacent ASIC generations also reads `HUBPREQ*_DCSURF_SURFACE_PITCH` via `REG_GET_FIELD`, illustrating why the generated pitch masks must remain compatible with MMIO consumers.

## Risks And Edge Cases

- These macros are a hardware ABI. Wrong masks or shifts usually compile successfully but write the wrong bits, causing blank planes, corrupted scanout, broken flips, bad cursor placement, incorrect DCC/TMZ state, or QoS underflow failures.
- Repeated instance blocks create drift risk. `HUBP1`, `HUBP2`, and `HUBP3`, plus `HUBPREQ1/2/3`, `HUBPRET1/2`, `CURSOR0_1/2`, and `DC_PERFMON8/9`, are highly similar. A single copied mask from the wrong instance can produce failures only on one pipe or high display count.
- The chunk boundaries are artificial. The first lines are only the tail masks of `DC_PERFMON7_PERFCOUNTER_CNTL`, and the final line stops before the complete `HUBPREQ3_PER_LINE_DELIVERY` mask list. Whole-file conclusions require adjacent chunks.
- Packed fields require read-modify-write discipline. Surface control, flip control, QoS, memory power, cursor control, DMDATA control, and interrupt registers pack unrelated fields together; full-register writes can corrupt neighboring state.
- Flip and interrupt fields may be sticky or write-one-to-clear. Misusing `SURFACE_FLIP_CLEAR`, `SURFACE_FLIP_AWAY_CLEAR`, `*_INT_ACK`, or status fields can miss flips, leave stale interrupts, or produce interrupt storms.
- Address fields are split into low/high words and luma/chroma/metadata variants. Mixing primary, secondary, chroma, or metadata address masks can scan out stale memory, break stereo/dual-plane formats, or violate protection settings.
- VM/TLB and TMZ/DCC fields interact with memory management and compression. Bad masks can cause page faults, decompression artifacts, security-policy mistakes for trusted memory, or failures limited to compressed/protected surfaces.
- QoS and prefetch timing fields are workload-sensitive. Incorrect `REFCYC_*`, `DST_Y_*`, `VRATIO_*`, or TTU watermark masks may only show up at high resolution, high refresh, multi-plane, scaling, cursor-heavy, or low-memory-clock conditions.
- Power and clock fields have sequencing dependencies not represented here. Accessing HUBP/HUBPREQ/HUBPRET/CURSOR state while clocks or memories are disabled may return stale data or drop writes.

## Test Signals

Useful validation is compile-time plus hardware behavior:

- Build AMDGPU/DC with DCN 2.1 support; missing or renamed macros should fail at include sites and in generated HUBP/IRQ/DMUB/GPIO register tables.
- Diff this generated chunk against AMD's register database and adjacent DCN family headers to catch instance drift across `HUBP1/2/3`, `HUBPREQ1/2/3`, `HUBPRET1/2`, `CURSOR0_1/2`, and `DC_PERFMON8/9`.
- Exercise multi-display DCN 2.1 hardware with enough active pipes to use instances 1, 2, and 3. Validate modesets, page flips, plane enable/disable, cursor movement, cursor format changes, scaling, rotation/mirroring, suspend/resume, hotplug, and DPMS.
- Test luma/chroma and metadata address paths with RGB and YUV formats, DCC-enabled surfaces, primary and secondary surfaces, and protected/TMZ surfaces where supported.
- Stress flip paths: immediate and vblank-synchronized flips, triple buffering, stereo sync modes, update locks, flip-away interrupt handling, and flip-pending status.
- Validate bandwidth and QoS behavior at high resolution/refresh and low memory-clock states. Watch for underflow, flicker, corruption, missed vblank, stalled flips, and failures that appear only with multiple planes or cursors.
- Exercise cursor and DMDATA programming: large cursor sizes, hot-spot offsets, stereo cursor settings, cursor memory power transitions, metadata address/control/QoS/status updates, and software DMDATA writes.
- Use perfmon tests or debug tools to configure `DC_PERFMON8` and `DC_PERFMON9`, start/stop counters, read low/high values, and verify interrupt/status/ack behavior.
- Monitor kernel logs and display diagnostics for hubp underflow, page faults, DCC errors, flip timeout, IRQ storms, power-gating resume failures, and pipe-specific regressions.

## Cross-Chunk Notes

Previous chunks of `dcn_2_1_0_sh_mask.h` define the earlier `DC_PERFMON7_PERFCOUNTER_CNTL` shift fields and masks before line 9804. Later chunks continue `HUBPREQ3_PER_LINE_DELIVERY` and the remaining DCN 2.1 generated register namespace. The final per-file research document should merge those chunks before making complete claims about perfmon7 or pipe instance 3 coverage.

### subset-b-001661: lines 12313-14826

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 12313-14826

## Scope And Purpose

This chunk is part of the generated AMD DCN 2.1.0 register shift/mask header. It contains compile-time preprocessor constants only: 2,121 `#define` entries in this range, including 1,060 `__SHIFT` constants and 1,082 `_MASK` constants. There are no C functions, structs, enums, variables, or executable branches in the chunk.

The path is under a local `ceph-client` source mirror, but this file is AMDGPU display hardware metadata, not Ceph filesystem code. Its purpose is to publish exact bit positions for DCN 2.1 display hub, cursor, DPP, converter, scaler, color-management, and performance-monitor registers so AMD display code can use symbolic field names through register helper macros rather than open-coded constants.

The range starts at the final `HUBPREQ3_PER_LINE_DELIVERY` chroma mask, then covers:

- `HUBPREQ3` cursor delivery, ref-frequency conversion, destination-Y request limit, request-memory power control/status, and vblank/flip timing fields.
- `HUBPRET3` return-path detile-buffer control, return-memory power control/status, read-line windows, vblank/read-line interrupt control/status/clear bits, current read-line value, and read-line status bits.
- `CURSOR0_3` cursor fetch state, including control, surface address high/low, size, position, hotspot, stereo, destination offset, cursor memory power, DMDATA address/control/QoS/status/software-data registers.
- `DC_PERFMON10` and `DC_PERFMON11` performance counter and performance-monitor control/value fields for HUBP/DPP-adjacent instrumentation blocks.
- `DPP_TOP0`, `CNVC_CFG0`, `CNVC_CUR0`, `DSCL0`, and `CM0` fields for DPP top-level clock/reset/CRC/host-read, pixel format conversion, cursor color conversion, scaler programming, line-buffer/output-buffer state, color matrices, degamma/blending/shaper LUTs, 3D LUTs, memory power, and test/debug access.
- The beginning of repeated instance-1 DPP fields: `DPP_TOP1`, `CNVC_CFG1`, `CNVC_CUR1`, and the start of `DSCL1`.

The chunk boundaries are not semantic. Line 12313 is only the chroma mask for a register whose shifts and luma mask are in the previous chunk. Line 14826 is only the comment for `DSCL1_SCL_HORZ_FILTER_SCALE_RATIO`; that register's actual shift/mask definitions begin in the next chunk. The final per-file report must reconcile those boundaries.

## Important API Surface

The exported interface is the generated AMD register-field naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field's packed 32-bit mask.
- Consumers combine this header with the matching `dcn_2_1_0_offset.h` register-address header and AMD display helper macros such as `SF`, `SRI`, `TF_SF`, `IPP_SF`, `REG_SET`, `REG_UPDATE`, `REG_GET`, `set_reg_field_value`, and `get_reg_field_value`.

Important macro families in this chunk include:

- `HUBPREQ3_CURSOR_SETTINGS`, `HUBPREQ3_REF_FREQ_TO_PIX_FREQ`, `HUBPREQ3_DST_Y_DELTA_DRQ_LIMIT`, `HUBPREQ3_HUBPREQ_MEM_PWR_CTRL`, `HUBPREQ3_HUBPREQ_MEM_PWR_STATUS`, `HUBPREQ3_VBLANK_PARAMETERS_[5-6]`, and `HUBPREQ3_FLIP_PARAMETERS_[3-6]`. These describe cursor request offsets, chunk-handle adjustment, request scheduler timing, VM/PTE/meta fetch timing, and request-side memory power state for pipe instance 3.
- `HUBPRET3_HUBPRET_CONTROL`, `HUBPRET3_HUBPRET_MEM_PWR_CTRL`, `HUBPRET3_HUBPRET_MEM_PWR_STATUS`, `HUBPRET3_HUBPRET_READ_LINE_CTRL[0-1]`, `HUBPRET3_HUBPRET_READ_LINE[0-1]`, `HUBPRET3_HUBPRET_INTERRUPT`, `HUBPRET3_HUBPRET_READ_LINE_VALUE`, and `HUBPRET3_HUBPRET_READ_LINE_STATUS`. These fields define return-path detile-buffer layout, crossbar source selection, memory power, read-line comparators, vblank/read-line interrupt behavior, and live/snapshot line status.
- `CURSOR0_3_CURSOR_*` and `CURSOR0_3_DMDATA_*`. These cover cursor enable/mode/TMZ/snoop/system/pitch/chunk settings, surface addresses, dimensions, position, hotspot, stereo mode, destination offset, cursor memory power state, and display metadata address/QoS/status/software-write fields.
- `DC_PERFMON10_*` and `DC_PERFMON11_*`. These expose counter select fields, clear bits, counter state, performance-monitor mode, update/clear selection, window-control and static-screen/selectable-trigger fields, plus high/low/current-value registers.
- `DPP_TOP0_*` and `DPP_TOP1_*`. These include DPP clock enable/gating controls, soft reset, CRC value/control fields, and host-read rate control.
- `CNVC_CFG0_*` and `CNVC_CFG1_*`. These describe surface pixel format, format expansion, 16-bit conversion, alpha enable, converter bypass, MSB alignment, positive clamping, update-pending status, FP bias/scale for RGB channels, color-key ranges, and 2-bit alpha LUT entries.
- `CNVC_CUR0_*` and `CNVC_CUR1_*`. These describe DPP-side cursor color conversion: cursor enable, expansion, pixel inversion, ROM enable, mode, pixel-alpha modulation, update-pending state, two cursor colors, and FP scale/bias.
- `DSCL0_*` plus the first `DSCL1_*` fields. These cover scaler coefficient RAM selection/data, scaler mode and coefficient-bank selection, luma/chroma/alpha tap counts, 2-tap hardcoded/sharpness control, manual replicate factors, horizontal/vertical luma/chroma scale ratios and initial phases, external overscan, OTG blanking, RECOUT/MPC sizing, line-buffer format/counter/memory control, DSCL memory power/status, and output-buffer memory power/control.
- `CM0_*`. This is the largest family in the chunk: color-management control, input color-space conversion matrices for regular and B paths, gamut remap matrices, bias, degamma LUT index/data/write masks, degamma RAM A/B region descriptors, blending gamma LUT and RAM A/B region descriptors, HDR multiplier, memory power/status, dealpha, coefficient format, shaper control/offset/scale/LUT/region descriptors, 3D LUT mode/index/data/read-write control/output normalization/offsets, and test debug index/data.

## Control Flow

This chunk has no local runtime control flow. It is declarative hardware metadata. Runtime sequencing lives in AMD display code that binds register offsets, shifts, and masks into per-block tables, then performs MMIO reads and writes through helper macros.

Representative integration patterns in this source tree are:

- `display/dc/resource/dcn21/dcn21_resource.c` includes both `dcn_2_1_0_offset.h` and `dcn_2_1_0_sh_mask.h`, then constructs the DCN 2.1 resource pool. This is where generated constants become part of the DCN 2.1 block tables for HUBP, DPP, timing, GPIO, IRQ, audio/DMUB-related resources, and other display components.
- `display/dmub/src/dmub_dcn21.c`, `display/dc/irq/dcn21/irq_service_dcn21.c`, `display/dc/gpio/dcn21/hw_factory_dcn21.c`, and `display/dc/gpio/dcn21/hw_translate_dcn21.c` also include this header for DCN 2.1 register metadata.
- Shared DPP and IPP headers such as `display/dc/dpp/dcn10/dcn10_dpp.h`, `display/dc/dpp/dcn20/dcn20_dpp.h`, and `display/dc/dcn10/dcn10_ipp.h` show the symbol-pasting pattern for fields visible in this chunk: `TF_SF(DSCL0_SCL_MODE, DSCL_MODE, mask_sh)`, `TF_SF(CM0_CM_3DLUT_MODE, CM_3DLUT_MODE, mask_sh)`, `TF_SF(CNVC_CFG0_FORMAT_CONTROL, CNVC_BYPASS, mask_sh)`, and `IPP_SF(CURSOR0_0_CURSOR_CONTROL, CURSOR_ENABLE, mask_sh)`. Instance-specific resource code maps those base patterns to the actual register instances.
- Hardware sequencing code programs these fields during plane enable, scaling setup, format conversion, color pipeline setup, cursor updates, interrupt setup/acknowledgement, power gating, and diagnostic readback. This header does not encode the order; callers must apply DCN-specific ordering such as update locks, coefficient/LUT bank selection, memory-power polling, interrupt clear rules, and modeset/flip timing constraints.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. The represented fields describe persistent or live hardware state inside DCN display blocks while those blocks are powered.

State represented by this chunk includes:

- Request-side HUBPREQ3 timing and memory power state for VM/PTE/meta fetches, cursor request scheduling, flip/vblank parameters, and ref-clock-to-pixel-clock conversion.
- Return-side HUBPRET3 detile-buffer assignment, read-line comparator windows, vblank/read-line interrupt state, live read-line snapshots, and return-path memory power state.
- Cursor0 pipe-3 fetch configuration, addresses, dimensions, position, stereo presentation, memory power, and DMDATA payload/address/QoS/status state.
- DPP top-level clock/reset/CRC/host-read state and performance-monitor counter state.
- CNVC pixel format, color key, alpha, clamp, FP bias/scale, and cursor conversion state for DPP instances 0 and 1.
- DSCL scaler coefficient RAM contents/selectors, scale ratios, init phases, tap counts, overscan, output sizing, line-buffer state, output-buffer state, and DSCL memory power state.
- CM0 color pipeline state: input CSC, gamut remap, degamma and blending gamma LUT programming, shaper LUT and region descriptors, HDR multiplier, 3D LUT data/control, coefficient format, dealpha, memory power, and debug selector/data state.

Persistence is hardware-defined. Many programming fields remain active until the driver reprograms the plane, performs a modeset, disables the block, power-gates memory, resumes from suspend, or the GPU resets. Status, update-pending, interrupt, perfmon, read-line snapshot, LUT index/data, and debug fields may be transient, latched, sticky, self-clearing, write-one-to-clear, or banked; the access type is not captured by this generated header.

## Dependencies And Integration Points

This chunk depends on the generated DCN 2.1 register ecosystem:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h` supplies the matching MMIO register offsets and instance-indexed address macros.
- `dcn_2_1_0_sh_mask.h` supplies the shift/mask constants in this chunk plus adjacent chunks for complete register families.
- AMD display register access helpers in the DC codebase paste register and field names into the generated `__SHIFT` and `_MASK` symbols.
- DCN 2.1 resource construction, IRQ service, GPIO translation/factory, and DMUB code include this header directly.
- Common DPP/IPP/scaler/color-management code from DCN10/DCN20 generations consumes the same families of field names through generated per-generation tables.

Functional integration points include multi-pipe display plane programming, cursor updates, page flip/vblank/read-line interrupt behavior, DPP clock/reset management, CRC collection, scaler coefficient loading, line-buffer/output-buffer memory management, color-keying, degamma/blending/shaper/3D LUT programming, gamut remap, HDR multiplier setup, display metadata cursor/DMDATA handling, performance monitoring, and suspend/resume or power-gating restoration.

## Risks And Edge Cases

- These constants are a hardware ABI. A wrong bit shift or mask can compile cleanly while programming the wrong field in MMIO.
- The chunk starts and ends in the middle of logical register groups. The previous chunk is required for the complete `HUBPREQ3_PER_LINE_DELIVERY` definition, and the next chunk is required for the actual `DSCL1_SCL_HORZ_FILTER_SCALE_RATIO` fields.
- Repeated instance families create drift risk. `DPP_TOP0` and `DPP_TOP1`, `CNVC_CFG0` and `CNVC_CFG1`, `CNVC_CUR0` and `CNVC_CUR1`, plus the partial `DSCL0` and `DSCL1` families should remain consistent where hardware requires it, but each macro names a specific instance.
- Interrupt registers mix mask, type, clear, raw status, and interrupt-status bits. Incorrect masks in `HUBPRET3_HUBPRET_INTERRUPT` can lose vblank/read-line events or clear sticky state unexpectedly.
- Memory power fields for HUBPREQ, HUBPRET, cursor, DSCL, OBUF, and CM memories have side effects and status dependencies. Bad shifts can leave memory forced on, forced off, or incorrectly reported.
- Address-related cursor and DMDATA fields are split into high/low pieces. Treating all address fields as identical widths can truncate addresses or fetch from the wrong memory.
- Scaler ratio/init/tap/coefficient fields are narrow packed fields. Overflow, truncation, or bank-selection mistakes can produce visible image scaling artifacts, underflow, or mode validation failures only for specific formats and viewport sizes.
- Color-management LUT and region descriptors are dense and repetitive. A swapped channel, RAM bank, region offset, or write-enable mask can create hard-to-diagnose gamma, shaper, gamut, HDR, or 3D LUT errors that may not affect basic modes.
- Fields such as `*_UPDATE_PENDING`, CRC one-shot state, perfmon clear/update controls, read-line snapshots, and debug selectors may be volatile or side-effectful even though this header exposes only numeric masks.
- Cross-generation headers contain similar names with different field presence. For example later DCN generations add or remove fields around cursor control and format crossbars; copying values between `dcn_2_1_0_sh_mask.h` and `dcn_3_*`/`dcn_4_*` headers is unsafe without vendor-register validation.

## Test Signals

Useful validation for this chunk combines build checks, generated-header comparisons, and hardware behavior:

- Build AMDGPU display code with DCN 2.1 enabled. Missing or renamed fields should fail in `dcn21_resource.c`, `irq_service_dcn21.c`, DMUB, GPIO, or shared DPP/IPP field tables.
- Compare this generated range against the matching vendor register database and the companion `dcn_2_1_0_offset.h` offsets; every field should have the expected register address, shift, and mask.
- Static-diff repeated instance families (`DPP_TOP0` versus `DPP_TOP1`, `CNVC_CFG0` versus `CNVC_CFG1`, `CNVC_CUR0` versus `CNVC_CUR1`, `DSCL0` versus `DSCL1`) to catch unintended per-instance drift.
- Exercise multi-display and multi-plane modes that use pipe 3, including cursor movement, cursor format changes, vblank/read-line interrupt delivery, page flips, and DMDATA handling.
- Exercise scaling paths across luma/chroma formats, integer and fractional ratios, overscan, line-buffer programming, and coefficient-bank updates; watch for underflow, blanking, or visual artifacts.
- Validate color-management paths with degamma, blending gamma, shaper LUTs, gamut remap, HDR multiplier, and 3D LUT programming, using CRC/readback or visual test patterns where available.
- Test memory power and suspend/resume sequences; verify memory power status fields converge and that cursor, DPP, DSCL, OBUF, CM, and HUBPREQ/HUBPRET state is restored after power transitions.
- Use DPP CRC and perfmon readback as diagnostic signals for field-table correctness, but remember these paths themselves depend on the same generated masks.

### subset-b-001662: lines 14827-17356

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 14827-17356

## Scope

This chunk is a generated AMD DCN 2.1.0 register shift/mask slice. It contains preprocessor constants only: no functions, structs, enums, data storage, or executable branches. The exported contract is the pair of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros that AMD display register helpers use to pack, update, and extract fields in DPP/DSCL/CM/perfmon/CNVC registers.

The line range starts in the middle of the DPP1 DSCL register group, covers all of the DPP1 color-management group, includes DPP1 display performance monitor fields, and then starts DPP2 with top-level DPP, CNVC config/cursor, DSCL, and the beginning of CM2 blend-gamma fields.

## Purpose

The purpose of this chunk is to describe the bit layout for per-pipe Display Pipe Processor hardware on DCN 2.1.0. The names are instance-qualified (`DSCL1_`, `CM1_`, `DC_PERFMON12_`, `DPP_TOP2_`, `CNVC_CFG2_`, `CNVC_CUR2_`, `DSCL2_`, `CM2_`) while the runtime DPP code consumes them through generation-specific register tables and field tables.

Major hardware areas represented here are:

- DPP1 DSCL tail: scaler horizontal/vertical ratios, phase initial values, bottom-field initial values, chroma ratios/inits, black offsets, scaler update/autocal controls, overscan, OTG blanking, recout/MPC dimensions, line-buffer data/memory controls, line-buffer counters, DSCL memory power controls/status, output-buffer control, and output-buffer memory power state.
- DPP1 CM: CM bypass/update status, input CSC A/B matrices, gamut-remap A/B matrices, bias fields, degamma LUT index/data/write controls, degamma RAM A/B PWL region descriptors, blend-gamma LUT and RAM A/B PWL descriptors, HDR multiplier coefficient, CM memory power, dealpha, coefficient format, shaper LUT/RAM A/B descriptors, CM memory power status2, 3D LUT mode/index/data/read-write controls, 3D LUT normalization/output offsets, and CM test debug index/data.
- DPP1 perfmon: `DC_PERFMON12_*` counter selection, counter state, perfmon window controls, current-value interrupt/mask/type/clear/status fields, and high/low counter values.
- DPP2 top/CNVC/DSCL/CM start: DPP2 top control/reset/CRC/host-read fields, CNVC2 pixel-format, format, FP bias/scale, color-keyer, alpha LUT, cursor0 control/color/FP-scale-bias, DSCL2 scaler controls mirroring DSCL1, and the start of CM2 input CSC/gamut/degamma/blend-gamma fields.

This header does not define policy. It gives exact bit positions and masks so the DPP implementation can program scaler, color, cursor, CRC, perfmon, and memory-power registers without hard-coding ASIC-specific bit numbers in runtime code.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The important interface is the generated macro namespace:

- `*_SHIFT` constants give the low bit position of a field.
- `*_MASK` constants give the already-shifted field mask.
- Register comments such as `//CM1_CM_DGAM_LUT_WRITE_EN_MASK` and address-block comments such as `// addressBlock: dce_dc_dpp2_dispdec_dscl_dispdec` group field macros by hardware block.

The direct consumers are the AMD display DPP register table macros:

- `TF_REG_LIST_DCN`, `TF_REG_LIST_DCN20`, and `TF_REG_LIST_DCN201` in `display/dc/dpp/dcn10/dcn10_dpp.h`, `display/dc/dpp/dcn20/dcn20_dpp.h`, and `display/dc/dpp/dcn201/dcn201_dpp.h` paste the register names into instance-specific register arrays.
- `TF_REG_LIST_SH_MASK_DCN*` macros paste field names into shift/mask initializers for `struct dcn10_dpp_shift`, `struct dcn10_dpp_mask`, `struct dcn20_dpp_shift`, `struct dcn20_dpp_mask`, and the DCN201 aliases.
- Runtime code uses `REG_SET`, `REG_SET_N`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, `IX_REG_GET`, and related helpers from the display register-helper layer. Those helpers receive the shifts and masks through `FN(reg, field)` expansion.

Important field families in this chunk include:

- Scaler and line buffer: `SCL_H_SCALE_RATIO`, `SCL_V_SCALE_RATIO`, chroma variants, `SCL_*_INIT_*`, `SCL_BLACK_OFFSET_*`, `AUTOCAL_*`, `RECOUT_*`, `MPC_*`, `INTERLEAVE_EN`, `ALPHA_EN`, `MEMORY_CONFIG`, `LB_MAX_PARTITIONS`, `LB_NUM_PARTITIONS`, and `LB_MEM_PWR_*`.
- Color matrices: `CM_ICSC_*`, `CM_ICSC_B_*`, `CM_GAMUT_REMAP_*`, and `CM_GAMUT_REMAP_B_*`.
- Transfer functions and LUTs: `CM_DGAM_*`, `CM_BLNDGAM_*`, `CM_SHAPER_*`, `CM_3DLUT_*`, their LUT index/data/write-select/config-status fields, and their RAM A/RAM B region descriptors.
- Memory power: DSCL line-buffer/LUT/OBUF power force/disable/status fields, and CM DGAM/3DLUT/SHAPER/GAMCOR/BLNDGAM memory power controls/status.
- CNVC/cursor: pixel format, format control, FP bias/scale, color-keyer channels, alpha 2-bit LUT, cursor enable/mode/2x-magnify/pitch/line-per-chunk, cursor color entries, and cursor FP scale/bias.
- Perfmon: counter enable/reset/mode/window/selection fields, counter high/low state, current-value interrupt controls, and counter readback registers.

## Control Flow

This chunk has no local control flow. Control flow is in the DPP implementation that includes the generated offset and mask headers and then uses the resulting tables.

Important runtime flows represented by these fields are:

1. DSCL programming in `dcn10_dpp_dscl.c`: `dpp1_dscl_set_scaler_manual_scale()` caches `struct scaler_data`, powers DSCL memory on if needed, disables autocal, programs recout and MPC size, chooses line-buffer partitions, writes black offsets, writes manual scale ratios and initial phases, sets tap counts, programs coefficient RAM, and swaps scaler coefficient RAM selection. The ratio/init/line-buffer/OBUF fields in this chunk are the exact bit layouts used by that flow for DPP1 and DPP2 instances.
2. DSCL memory power: `dpp1_power_on_dscl()` updates `DSCL_MEM_PWR_CTRL` and waits on `DSCL_MEM_PWR_STATUS`. Incorrect force/status masks can leave the scaler LUT or line-buffer memories powered down, or prevent low-power transitions from completing.
3. CM input CSC and gamut remap: `dpp1_program_input_csc()`, `dpp2_program_input_csc()`, `dpp1_cm_set_gamut_remap()`, and `dpp2_cm_set_gamut_remap()` program 3x4 matrices through `cm_helper_program_color_matrices()`. DCN2 uses A/B matrix banks and debug-status reads to select the inactive bank, so the A/B field pairs in this chunk are part of frame-boundary-safe updates.
4. Degamma, blend-gamma, shaper, and 3D LUT programming: DCN2 CM code configures write masks/selectors, writes LUT index/data registers, programs RAM A/B PWL regions, then flips the active mode. Fields such as `CM_DGAM_CONFIG_STATUS`, `CM_BLNDGAM_CONFIG_STATUS`, `CM_*_LUT_WRITE_SEL`, `CM_*_LUT_MODE`, and `CM_*_EXP_REGION*` provide the hardware bank state and region metadata for those flows.
5. CNVC/cursor programming: resource and DPP code use CNVC format, pixel conversion, color-keyer, alpha LUT, and cursor fields to set plane input conversion and hardware cursor appearance for DPP2.
6. DPP top/CRC/perfmon: CRC control/value and performance monitor registers expose diagnostics and counters. The macros describe event selection, counter accumulation windows, interrupt threshold/status bits, and readback fields; test/debug code supplies the sequencing.

The macros do not encode read/write ordering, register volatility, write-one-to-clear behavior, or whether a field is status-only. Callers must still follow the hardware sequencing requirements for modeset, plane update, LUT bank switch, cursor update, memory power, and perfmon interrupt acknowledgement.

## State And Persistence Behavior

The header itself stores no software state and persists nothing. It describes hardware state that persists in MMIO registers until changed by the driver, hardware, firmware, power gating, reset, or a full modeset/reinitialization path.

State represented by this chunk includes:

- Per-DPP scaler state: scale ratios, phase initial values, black offsets, autocal mode, overscan, recout/MPC size, line-buffer memory configuration, and coefficient-bank selection.
- Per-DPP memory power state: DSCL LUT/LB/OBUF memory force/disable/status bits and CM LUT memory force/disable/status bits. These interact with low-power debug flags and deferred register writes in the display core.
- Cached software state in consumers: `struct dcn201_dpp` and related DPP structs cache current `scaler_data`, filter coefficient pointers, and PWL parameters. The generated masks determine how those cached values are serialized into hardware.
- CM matrix and LUT state: ICSC/gamut matrices, degamma/blend-gamma/shaper LUT contents, RAM A/B region descriptors, active/bypass modes, config-status bits, 3D LUT indexing/data, and normalization/offset registers.
- Plane-format and cursor state: CNVC surface pixel format, format-conversion controls, FP bias/scale, color keyer, alpha LUT, cursor mode/color, cursor pitch/chunk layout, and cursor FP scale/bias.
- Observability state: DPP CRC values/control, host read control, perfmon counter values/state, current-value interrupts, and counter windows.

Many of these fields are double-buffered or banked. The matrix and LUT flows often write an inactive A/B RAM, then flip mode or select bits so the new state becomes active on a frame boundary. Bad masks can therefore produce delayed or intermittent failures rather than an immediate register-write error.

## Dependencies And Integration Points

The companion address header is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`, which supplies register offsets. This chunk supplies field layout inside those registers. Both are needed for meaningful MMIO access.

Primary integration points in the source tree are:

- `display/dc/dpp/dcn10/dcn10_dpp.h`, `display/dc/dpp/dcn20/dcn20_dpp.h`, and `display/dc/dpp/dcn201/dcn201_dpp.h`, which define the register/shift/mask structs and macro lists that consume these names.
- `display/dc/dpp/dcn10/dcn10_dpp_dscl.c`, which uses DSCL fields for manual scaling, line-buffer setup, coefficient RAM programming, memory power, recout, MPC size, and scaler mode.
- `display/dc/dpp/dcn10/dcn10_dpp_cm.c` and `display/dc/dpp/dcn20/dcn20_dpp_cm.c`, which use CM fields for input CSC, gamut remap, degamma, blend-gamma, shaper, and LUT bank programming.
- DCN201 resource construction code, which wires DCN2.1 register tables into DPP instances and selects the right per-instance address/mask arrays.
- Display diagnostics and debug paths that read DPP CRC and `DC_PERFMON12_*` counters.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata. It has no Ceph filesystem, network protocol, storage replication, distributed locking, or persistent filesystem behavior.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A generated shift/mask error usually compiles cleanly but causes `REG_SET` or `REG_UPDATE` to write the wrong bits, leave stale bits in place, truncate values, or read a misleading status field.

DSCL risks include black screens, shifted/scaled images, corrupted chroma on YCbCr or 4:2:0 planes, incorrect interlaced bottom-field phase, bad line-buffer partitioning, coefficient RAM writes to the wrong tap/filter type, and failures that only appear with specific taps, ratios, formats, or recout dimensions. The chunk starts after the first `DSCL1_SCL_HORZ_FILTER_SCALE_RATIO` comment, so adjacent chunk context is needed for the complete DSCL1 register group.

CM risks include wrong color conversion, broken degamma/blend-gamma/shaper output, incorrect HDR multiplier behavior, bad 3D LUT indexing/data, bank-switch races, and frame-boundary glitches if A/B config-status or write-select masks are wrong. Because many LUT regions use repeated `REGION_0_1` through `REGION_32_33` patterns, copy-generation mistakes can affect only part of a transfer curve and produce subtle banding or clipping.

Memory power fields are sensitive. Incorrect force/disable/status masks can power down active DSCL/CM memories, prevent optimized low-power entry, or make waits poll the wrong status bits. These bugs tend to surface during suspend/resume, runtime power management, display off/on, or modeset transitions rather than during simple boot tests.

CNVC and cursor risks include wrong pixel-format interpretation, broken FP bias/scale for FP formats, color-keyer mismatches, cursor invisibility/corruption, wrong cursor colors, and chunk/pitch bugs that appear only with certain cursor sizes or magnification settings.

Perfmon and CRC fields are diagnostic but still control-sensitive. Wrong masks can make validation counters meaningless, fail to clear or mask current-value interrupts, or report the wrong counter state. This can hide performance regressions or make debug tooling chase false signals.

Instance repetition matters. The same logical fields appear for DPP1 and DPP2 with instance-qualified prefixes. The merge lane should check structural consistency across `DSCL1`/`DSCL2`, `CM1`/`CM2`, and corresponding offset definitions while still allowing intentional per-instance address differences.

## Test Signals

Useful validation signals are a mix of generated-header checks and real display behavior:

- Compile coverage for DCN2.1/DCN201 display code that includes `dcn_2_1_0_offset.h` and `dcn_2_1_0_sh_mask.h`, especially DPP, DSCL, CM, resource, and diagnostics paths.
- Generated consistency checks that every `REGISTER__FIELD__SHIFT` has the expected `REGISTER__FIELD_MASK`, masks align with shifts, field widths are plausible, and every register has a matching offset definition.
- Cross-instance checks that repeated DPP1/DPP2 register families have matching field names, widths, and shifts unless the hardware database documents a difference.
- Plane scaling tests covering bypass, RGB scaling, YCbCr scaling, 4:2:0 luma/chroma bypass cases, 1/2/3/4/6/8 tap filters, large downscales, interlaced/bottom-field init paths, recout offsets, and line-buffer pressure.
- Color pipeline tests for input CSC, gamut remap, degamma PWL, blend-gamma PWL, shaper LUT, HDR multiplier, 3D LUT enable/read-write/index/data paths, and transitions between bypass/RAM A/RAM B.
- Power-management tests across display blank/unblank, modeset, runtime PM, suspend/resume, and low-power debug options to catch DSCL/CM memory power mask errors.
- CNVC/cursor tests for multiple pixel formats, FP16/FP conversion, color keying, alpha LUT behavior, cursor color/pitch/chunk layout, 2x cursor magnification, and cursor movement during modesets.
- CRC/perfmon tests that confirm DPP CRC values change with known frame content, perf counters count selected events, current-value interrupts can be masked/cleared, and counter high/low reads are coherent.

Regression symptoms from this chunk include black or incorrectly scaled planes, chroma misalignment, color shifts, LUT banding, cursor artifacts, stuck memory-power waits, failures only after resume or display off/on, useless perf counters, and diagnostics that disagree with visible frame output.

## Cross-Chunk Notes

This is an artificial line-range slice of a generated constants header. It begins inside the DSCL1 family and ends mid-way through CM2 blend-gamma RAM A region definitions. The final per-file report should merge this chunk with adjacent chunks to describe complete DPP1/DPP2 coverage and avoid treating partial register families as standalone modules.

### subset-b-001663: lines 17357-19859

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 17357-19859

## Scope

This chunk is a generated AMD DCN 2.1.0 register shift/mask header slice. It contains preprocessor constants only: no functions, structs, enums, storage objects, or executable control flow. Its exported contract is the paired `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros that AMD display register helpers use to pack and unpack fields in memory-mapped DCN registers.

The range has 2,503 source lines, including 2,119 `#define` entries, 1,060 shift constants, 1,059 mask constants, 372 register/address comments, and 6 address-block markers. The chunk begins inside the DPP2 color-management block at the tail of `CM2_CM_BLNDGAM_RAMA_REGION_6_7`, then covers the rest of DPP2 blend gamma, shaper, 3D LUT, CM memory-power, and CM debug masks. It then enters DPP3 register blocks for DPP top, CNVC converter/cursor, DSCL scaler, DC perfmon instance 13, and a large part of DPP3 color management ending inside `CM3_CM_SHAPER_RAMB_REGION_10_11`.

## Purpose

The chunk provides exact bit positions and already-shifted masks for DCN 2.1 display pipe/plane processing hardware. Higher-level display code names logical fields through register helper macros; this generated header supplies the ASIC-specific bit layout for Renoir/DCN 2.1.

Major hardware areas covered here are:

- `CM2_CM_BLNDGAM_*`: DPP2 blend/output gamma RAM A/B controls, per-channel start/end/slope values, LUT region descriptors for regions 0-33, LUT index/data/write-enable fields, and current/config status bits.
- `CM2_CM_SHAPER_*`: DPP2 shaper LUT controls, offsets, scales, LUT access, write masks, RAM A/B start/end controls, and 34-region piecewise-linear segment descriptors.
- `CM2_CM_3DLUT_*`: DPP2 3D LUT mode, index, 12-bit/30-bit data path, read/write control, output normalization, and RGB output offsets.
- `CM2_CM_MEM_PWR_*`, `CM2_CM_HDR_MULT_COEF`, `CM2_CM_DEALPHA`, `CM2_CM_COEF_FORMAT`, and `CM2_CM_TEST_DEBUG_*`: color-management memory power, HDR multiplier, de-alpha, coefficient format, and indexed debug/status access.
- `DC_PERFMON13_*`: perf counter and perfmon control/state/value masks for the DPP2 perfmon address block.
- `DPP_TOP3_*`: DPP3 top-level enable/reset/CRC/host-read controls.
- `CNVC_CFG3_*` and `CNVC_CUR3_*`: DPP3 converter pixel format, format expansion/bypass/alpha controls, floating-point bias/scale, color keyer ranges, 2-bit alpha LUT, cursor mode/colors, and cursor FP scale/bias.
- `DSCL3_*`: DPP3 scaler coefficient RAM, tap counts, scaler mode, scale ratios, filter init, recout/MPC sizes, line-buffer format/memory, autocal, overscan/blanking geometry, memory power, and output-buffer controls.
- `CM3_CM_*`: DPP3 color-management control, ICSC and gamut-remap A/B coefficient banks, bias, degamma, blend gamma, HDR multiplier, shaper, dealpha, coefficient format, and CM memory-power masks. This chunk includes complete DPP3 degamma and blend gamma region blocks and a partial DPP3 shaper block.

## Important APIs, Types, And Macros

There are no callable APIs in this range. The important interface is the generated macro naming scheme:

- `*_SHIFT` constants hold a field's low bit position.
- `*_MASK` constants hold the field mask already shifted into register position.
- Register comments such as `//CM2_CM_SHAPER_RAMA_REGION_0_1` group the following field macros by hardware register.
- Address-block comments such as `// addressBlock: dce_dc_dpp3_dispdec_dscl_dispdec` mark generated hardware register windows.

The constants are consumed through AMD display register helper conventions rather than direct hand-written bit operations. DCN21 resource setup includes `dcn_2_1_0_offset.h` and this file, then expands macros such as `SRI`, `SR`, `TF_SF`, `FD_MASK`, and `FD_SHIFT` into register, shift, and mask tables. Runtime code then uses helpers such as `REG_SET`, `REG_SET_2`, `REG_SET_4`, `REG_UPDATE`, `REG_GET`, and `IX_REG_GET`.

Representative DPP2 color-management fields in this chunk include `CM2_CM_BLNDGAM_RAMB_REGION_0_1__CM_BLNDGAM_RAMB_EXP_REGION0_LUT_OFFSET_MASK`, `CM2_CM_BLNDGAM_LUT_WRITE_EN_MASK__CM_BLNDGAM_LUT_WRITE_SEL_MASK`, `CM2_CM_SHAPER_CONTROL__CM_SHAPER_LUT_MODE_MASK`, `CM2_CM_SHAPER_RAMA_END_CNTL_B__CM_SHAPER_RAMA_EXP_REGION_END_BASE_B_MASK`, `CM2_CM_3DLUT_READ_WRITE_CONTROL__CM_3DLUT_CONFIG_STATUS_MASK`, and `CM2_CM_TEST_DEBUG_DATA__CM_TEST_DEBUG_DATA_MASK`.

Representative DPP3 converter/scaler/top fields include `DPP_TOP3_DPP_CONTROL__DPP_CLOCK_ENABLE_MASK`, `CNVC_CFG3_FORMAT_CONTROL__CNVC_BYPASS_MASK`, `CNVC_CFG3_CNVC_SURFACE_PIXEL_FORMAT__CNVC_SURFACE_PIXEL_FORMAT_MASK`, `CNVC_CUR3_CURSOR0_CONTROL__CUR0_ENABLE_MASK`, `DSCL3_SCL_MODE__DSCL_MODE_MASK`, `DSCL3_SCL_TAP_CONTROL__SCL_H_NUM_TAPS_MASK`, `DSCL3_SCL_COEF_RAM_TAP_DATA__SCL_COEF_RAM_EVEN_TAP_COEF_MASK`, `DSCL3_LB_MEMORY_CTRL__LB_MEMORY_CONFIG_MASK`, and `DSCL3_DSCL_MEM_PWR_CTRL__LUT_MEM_PWR_FORCE_MASK`.

Representative DPP3 color fields include `CM3_CM_CONTROL__CM_BYPASS_MASK`, `CM3_CM_ICSC_CONTROL__CM_ICSC_MODE_MASK`, `CM3_CM_GAMUT_REMAP_CONTROL__CM_GAMUT_REMAP_MODE_MASK`, `CM3_CM_DGAM_CONTROL__CM_DGAM_LUT_MODE_MASK`, `CM3_CM_BLNDGAM_LUT_WRITE_EN_MASK__CM_BLNDGAM_CONFIG_STATUS_MASK`, `CM3_CM_SHAPER_CONTROL__CM_SHAPER_LUT_MODE_MASK`, and the many `CM3_CM_*_REGION_*__*_LUT_OFFSET/NUM_SEGMENTS` masks that describe piecewise-linear LUT programming.

## Control Flow

This header has no local control flow. Runtime behavior is created by the consumers that combine these shift/mask macros with the matching addresses from `dcn_2_1_0_offset.h`.

A typical DPP path is:

1. `display/dc/resource/dcn21/dcn21_resource.c` includes `dcn_2_1_0_offset.h` and `dcn_2_1_0_sh_mask.h`.
2. Register-list macros instantiate per-DPP address, shift, and mask tables. `dcn21_dpp_create()` constructs `struct dcn20_dpp` objects with `dpp2_construct()`, passing `tf_regs`, `tf_shift`, and `tf_mask`.
3. Generic DCN2 DPP code in `display/dc/dpp/dcn20/` uses those tables for converter setup, cursor setup, scaler setup, color-management programming, LUT access, gamut remap, degamma, blend gamma, shaper, 3D LUT, memory power, and state reads.
4. `REG_*` and `IX_REG_*` helpers combine a register address with the field's shift and mask from this generated header to perform MMIO reads/writes or indexed debug-register reads.

Control-sensitive flows represented by this chunk include pixel-format selection, alpha enable, input color-space conversion, color keying, cursor attribute programming, scaler coefficient/tap/ratio programming, line-buffer setup, DPP clock/soft-reset/CRC handling, color-management bypass, double-buffered ICSC/gamut-remap coefficient selection, degamma/shaper/blend LUT RAM A/B selection, 3D LUT data access, and DPP/DSCL/CM memory power transitions.

The macros do not encode sequencing, access type, volatility, field value limits beyond bit width, frame-boundary latch timing, or write-one-to-clear behavior. Callers must still know when a field is read-only status, live hardware state, sticky debug/status, double-buffered RAM selection, or safe to modify only during a blanking/update sequence.

## State And Persistence Behavior

The file itself stores no software state and performs no persistence. It describes hardware register state that persists according to DCN register semantics until changed by software, hardware sequencing, power management, reset, or firmware activity.

State represented in this range includes:

- DPP2/DPP3 color-management pipeline state: CM bypass, ICSC and gamut-remap coefficient bank selection, coefficient format, RGB bias, de-alpha, HDR multiplier, degamma/blend/shaper LUT modes, LUT RAM selection, LUT data/index state, LUT region metadata, 3D LUT mode/size/bit depth/data, output normalization, and RGB offsets.
- DPP3 converter/cursor state: pixel format, format expansion, alpha enable, clamp/crossbar controls, FP bias/scale values, color-key ranges, alpha 2-bit LUT values, cursor mode/enable/expansion/ROM/pixel-alpha controls, cursor colors, and cursor FP bias/scale.
- DPP3 scaler state: coefficient RAM selector and coefficient data, tap counts, scaler and chroma coefficient modes, horizontal/vertical scale ratios and initial phases for luma/chroma, output geometry, MPC size, line-buffer format/memory configuration, autocal controls, overscan/OTG blanking, black offsets, DSCL update controls, and DSCL/OBUF memory power state.
- Top/debug/perf state: DPP clock enable, soft reset, CRC values/control, host-read control, perf counter control/state/value registers, and CM indexed debug status/data.

Many fields are configuration latches, some are live readbacks, and some are selected through indexed debug paths. Incorrect values can persist until the affected pipe is reprogrammed by a modeset, plane update, color update, scaler update, suspend/resume, DPP power transition, or full GPU reset.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`, which supplies matching MMIO offsets and base-index macros. This chunk supplies bit layout inside those registers.

Visible include sites for the full generated header in this tree are:

- `display/dc/resource/dcn21/dcn21_resource.c`, which builds Renoir/DCN21 resources and instantiates DPP, IPP, AUX/I2C, IRQ, link, audio, clock, hub, MPC, OPP, DSC, and other display blocks.
- `display/dc/irq/dcn21/irq_service_dcn21.c`, which uses the generated namespace for interrupt-source tables.
- `display/dc/gpio/dcn21/hw_factory_dcn21.c` and `display/dc/gpio/dcn21/hw_translate_dcn21.c`, which use DCN21 generated masks for GPIO/HPD translation.
- `display/dmub/src/dmub_dcn21.c`, which expands `FD_MASK` and `FD_SHIFT` values for DMUB service register tables.

For this chunk specifically, the strongest functional integration is with `display/dc/dpp/dcn20/dcn20_dpp.h`, `dcn20_dpp.c`, and `dcn20_dpp_cm.c`. Those files define the DCN2 DPP register lists and the runtime operations that use the CM, CNVC, DSCL, DPP_TOP, and memory-power fields represented here. `display/dc/inc/hw/dpp.h` documents the DPP pipeline as CNVC, DSCL, CM, OBUF, and DPB, matching the hardware blocks in this chunk.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata. It has no Ceph filesystem, distributed storage, network protocol, or persistence-layer behavior.

## Risks And Edge Cases

The dominant risk is silent hardware misprogramming. A wrong shift or mask compiles cleanly but can write the wrong bits, truncate a field, read stale status, choose the wrong RAM bank, or corrupt unrelated control fields.

Color-management fields are especially sensitive because they are often double-buffered or RAM-backed. Bad masks in blend gamma, shaper, degamma, ICSC, gamut-remap, or 3D LUT registers can produce wrong colors, banding, HDR errors, broken color-space conversion, incorrect gamma/transfer curves, or updates that tear because software wrote the active bank instead of the inactive bank.

Scaler and converter fields affect plane correctness. Incorrect `CNVC_*` masks can select the wrong pixel format, alpha behavior, cursor mode, color key range, or channel mapping. Incorrect `DSCL3_*` masks can produce bad scaling ratios, wrong tap counts, coefficient RAM corruption, line-buffer underuse/overflow, chroma misalignment, clipped recout geometry, or failures that appear only for video formats, 4:2:0 planes, high bit depth, cursors, or scaling cases.

Power-management fields must match hardware semantics. Bad `CM_MEM_PWR_*`, `DSCL_MEM_PWR_*`, or `OBUF_MEM_PWR_*` masks can leave memories powered down while being accessed, prevent low-power entry, or cause intermittent failures around plane enable/disable, idle, suspend/resume, or clock gating.

Repeated generated layouts create copy hazards. DPP2 and DPP3 register families are structurally similar but not always identical; apparent one-off differences must be checked against the ASIC register database and matching offset header before being treated as bugs. The chunk boundary also matters: it begins with mask definitions from a register whose earlier shift definitions are in the previous chunk, and it ends inside the DPP3 shaper RAMB region sequence. Whole-file conclusions need adjacent chunks.

## Test Signals

Useful validation signals are a mix of generated-header consistency checks and display behavior:

- Build coverage for DCN21 resource, DPP, IRQ, GPIO, DMUB, and common register-helper users that include `dcn_2_1_0_sh_mask.h`.
- Generated-register validation that every field used by DCN21 register-list macros has a matching shift and mask, a matching address in `dcn_2_1_0_offset.h`, and a mask consistent with its shift and expected width.
- Structural comparison across repeated DPP instances and RAM A/B blocks: `CM2` vs `CM3`, `RAMA` vs `RAMB`, and region pairs `0_1` through `32_33`.
- Plane-format tests for ARGB/ABGR/RGB565/RGB111110/FP formats, alpha enable/disable, 2-bit alpha LUT paths, color keying, cursor modes, and cursor disable cases for selected video formats.
- Scaling tests covering bypass, up/downscale, luma/chroma scaling, 4:2:0 content, tap count variations, coefficient RAM updates, recout/MPC geometry, overscan, and line-buffer partition changes.
- Color tests for degamma, gamut remap, ICSC, blend gamma, shaper, HDR multiplier, 3D LUT programming, and double-buffered RAM bank switching across frame updates.
- Power-management tests around plane enable/disable, display idle, memory power-gating, suspend/resume, and modeset transitions while using CM/DSCL/OBUF memories.
- CRC/perf/debug sanity checks that DPP CRC registers, DC perfmon instance 13, and CM test-debug indexed reads return plausible values and do not break normal pipe programming.

Regression symptoms from bad constants include black or corrupted planes, wrong colors or gamma, broken HDR/color-management paths, bad scaling or chroma placement, cursor corruption, alpha/color-key errors, flicker during LUT updates, memory-power transition hangs, invalid CRC reads, and failures limited to DPP instance 2 or 3 because this chunk mostly covers `CM2` and `*3` blocks.

## Cross-Chunk Notes

This is a generated constants-only chunk, not a standalone module. The previous chunk owns the beginning of the DPP2 blend-gamma RAMA register sequence, including some shifts for fields whose masks appear at this chunk's start. Later chunks own the remainder of the DPP3 shaper RAMB sequence and subsequent DCN 2.1 register blocks. The final per-file document should merge adjacent chunks to describe the complete `dcn_2_1_0_sh_mask.h` register-layout contract.

### subset-b-001664: lines 19860-22381

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 19860-22381

## Scope

This chunk is a generated AMDGPU DCN 2.1 register shift/mask header slice. It contains preprocessor constants only: no functions, structs, enums, storage objects, or executable control flow. The exported surface is the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macro contract used by AMD display register helpers to pack, update, and decode DCN 2.1 hardware register fields.

The range has 2,522 source lines, including 2,114 `#define` entries: 1,055 shift constants and 1,059 mask constants, plus 382 register/address-block comments. It starts in the middle of the `CM3_CM_SHAPER_RAMB_REGION_10_11` field group, covers the tail of DPP3 color-management shaper and 3DLUT fields, then moves through DPP3 perfmon, MPCC0-MPCC7, MPC global control/status/output fields, and MPCC OGAM0-2 output-gamma PWL/LUT fields. The chunk ends inside `MPCC_OGAM2_MPCC_OGAM_RAMB_END_CNTL2_B`, so some OGAM2 RAMB end fields continue in the following chunk.

## Purpose

The purpose of this slice is to describe exact bit positions and masks for several DCN 2.1 display pipeline blocks:

- `CM3_CM_SHAPER_RAMB_REGION_*`, `CM3_CM_MEM_PWR_*`, and `CM3_CM_3DLUT_*`: DPP3 color-management shaper RAM-B region metadata, shaper/HDR 3DLUT memory power state, 3DLUT mode/index/data/read-write control, output normalization, RGB output offset/scale, and CM test/debug access.
- `DC_PERFMON14_*`: DPP3 display performance counter and perfmon control/status/value registers.
- `MPCC0_MPCC_*` through `MPCC7_MPCC_*`: repeated multi-plane compositor combiner instances, including input selection, output pipe binding, blend mode, alpha/gain settings, stereo/multiview controls, update-lock status, background color, OGAM memory power control, stall interrupt status, and idle/busy/error status.
- `MPC_*`: global MPC clock/reset, CRC configuration/results, perfmon event enable, bypass background color, stall grace window, host-read throttling, update pending/taken/ack status, vertical-update lock set bits, and four MPC output mux/denormalization blocks.
- `MPCC_OGAM0_*`, `MPCC_OGAM1_*`, and the first part of `MPCC_OGAM2_*`: per-MPCC output gamma LUT mode/index/data/RAM control plus RAM-A and RAM-B piecewise-linear region layout for RGB channels.

The header lets generic display code name logical fields while this ASIC-specific file supplies the Renoir/DCN 2.1 bit layout. It is metadata for MMIO programming; it does not itself implement color, blending, CRC, perfmon, or update-lock behavior.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The important interface is the generated macro schema:

- `*_SHIFT` constants hold the low bit position of a named field.
- `*_MASK` constants hold the already-positioned bit mask for the same field.
- Register comments such as `//MPCC3_MPCC_CONTROL` group field macros by hardware register.
- Address-block comments such as `// addressBlock: dce_dc_mpc_mpcc3_dispdec` mark repeated hardware register windows.

Important field families include:

- Shaper/3DLUT fields: `CM3_CM_SHAPER_RAMB_REGION_12_13__CM_SHAPER_RAMB_EXP_REGION12_LUT_OFFSET`, `...NUM_SEGMENTS`, `CM3_CM_MEM_PWR_CTRL2__SHAPER_MEM_PWR_FORCE`, `CM3_CM_MEM_PWR_STATUS2__HDR3DLUT_MEM_PWR_STATE`, `CM3_CM_3DLUT_MODE__CM_3DLUT_MODE`, `CM3_CM_3DLUT_READ_WRITE_CONTROL__CM_3DLUT_WRITE_EN_MASK`, `CM3_CM_3DLUT_READ_WRITE_CONTROL__CM_3DLUT_CONFIG_STATUS`, and RGB output offset/scale fields.
- Perfmon fields: `DC_PERFMON14_PERFCOUNTER_CNTL__PERFCOUNTER_EVENT_SEL`, `...INC_MODE`, `...INT_EN`, `...ACTIVE`, `DC_PERFMON14_PERFCOUNTER_STATE`, `DC_PERFMON14_PERFMON_CNTL`, value high/low counters, and C-value interrupt/status fields.
- MPCC compositor fields: `MPCCn_MPCC_TOP_SEL`, `MPCCn_MPCC_BOT_SEL`, `MPCCn_MPCC_OPP_ID`, `MPCCn_MPCC_CONTROL__MPCC_MODE`, `...ALPHA_BLND_MODE`, `...GLOBAL_ALPHA`, `...GLOBAL_GAIN`, `MPCCn_MPCC_SM_CONTROL`, `MPCCn_MPCC_UPDATE_LOCK_SEL`, `MPCCn_MPCC_MEM_PWR_CTRL`, `MPCCn_MPCC_STALL_STATUS`, and `MPCCn_MPCC_STATUS`.
- MPC global fields: `MPC_SOFT_RESET__MPCC0_SOFT_RESET` through `MPCC3_SOFT_RESET`, `MPC_CRC_CTRL__MPC_CRC_EN`, `...SRC_SEL`, `...ONE_SHOT_PENDING`, `...UPDATE_LOCK`, `MPC_CRC_RESULT_AR/GB/C`, `MPC_PENDING_TAKEN_STATUS_REG1`, `MPC_PENDING_TAKEN_STATUS_REG3`, `MPC_UPDATE_ACK_REG5`, per-pipe `*_VUPDATE_LOCK_SET*`, and `MPC_OUT0_*` through `MPC_OUT3_*`.
- MPCC OGAM fields: `MPCC_OGAMn_MPCC_OGAM_MODE`, `...LUT_INDEX`, `...LUT_DATA`, `...LUT_RAM_CONTROL`, per-channel RAMA/RAMB start/slope/end controls, and repeated `RAMA_REGION_0_1` through `RAMA_REGION_32_33` plus `RAMB_REGION_*` region offset/segment masks.

Consumers generally do not reference these long macro names directly in algorithmic code. They are fed through helper macros such as `SF`, `SR`, `SRI`, `SRII`, `FD_MASK`, and `FD_SHIFT` to build register, shift, and mask tables for DCN objects.

## Control Flow

This header has no local control flow. Runtime behavior occurs in AMD display code that includes `dcn_2_1_0_offset.h` with this shift/mask header and then issues MMIO register reads/writes through register helper macros.

A typical control path is:

1. DCN 2.1 resource or block code includes the generated offset and mask headers.
2. Register-list macros in DPP, MPC, MPCC, OPP, IRQ, GPIO, audio, and DMUB-adjacent code paste register and field names into generated macro names.
3. Code constructs register/shift/mask tables for a hardware object instance, such as DPP3, MPCC3, MPC output 1, or MPCC OGAM1.
4. Runtime helpers such as `REG_SET`, `REG_SET_N`, `REG_UPDATE`, `REG_GET`, and indexed table loaders use the offsets from `dcn_2_1_0_offset.h` and the shifts/masks from this file to program or inspect hardware fields.

Control-sensitive flows represented by this slice include DPP shaper/3DLUT programming, DPP perf counter selection and sampling, MPCC tree composition and blend parameter updates, MPCC update-lock coordination, MPC CRC capture, update-pending/ack polling, vupdate lock set operations, MPC output mux/denormalization setup, and MPCC OGAM LUT/PWL programming.

The macros do not encode operation ordering, access permissions, volatility, write-one-to-clear semantics, double-buffering rules, or synchronization requirements. Callers must still know which fields are live status, sticky interrupt state, self-clearing command bits, read-only capability/status, or safe to update only while a pipe, MPCC, or LUT bank is idle/locked.

## State And Persistence Behavior

The file itself stores no state and performs no persistence. It describes hardware register state that persists in the display engine until changed by driver writes, hardware state machines, power management, modeset reprogramming, or reset.

State represented in this range includes:

- DPP color state: shaper RAM-B region offsets and segment counts, shaper/HDR 3DLUT SRAM power controls/status, 3DLUT mode and size, 3DLUT RAM selection/write enables, 30-bit access mode, output normalization, and RGB output offset/scale.
- DPP perfmon state: event selection, counter run/stop/interrupt control, counter current value selection, high/low counter values, C-value interrupt metadata, and perfmon state bits.
- Per-MPCC composition state: top/bottom inputs, OPP destination, blend mode, alpha blending mode, premultiplied-alpha flag, active-overlap behavior, background bit depth/color, bottom gain mode, global alpha/gain, stereo/multiview controls, update-lock selection/status, OGAM SRAM power state, stall interrupt state, and idle/busy/disabled/error flags.
- Global MPC state: clock-gating test controls, soft reset bits, CRC enable/source/stereo/interlace/update lock controls, CRC results, perfmon event enable, bypass background color, stall grace timing, host-read rate limiting, update pending/taken/ack state, vertical-update lock latches, output mux routing, and denormalization clamp/mode values.
- MPCC OGAM state: output-gamma mode, LUT index/data, RAM bank selection/write mask/config status, per-channel PWL start/end/slope/base controls, and RAMA/RAMB region offset/segment tables.

Some values are configuration latches, some are live hardware status, and some represent SRAM/LUT programming windows. Incorrect values can persist until the next full pipe programming sequence, LUT reload, modeset, suspend/resume recovery, power reset, or GPU reset.

## Dependencies And Integration Points

The direct companion for this chunk is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`, which provides matching register addresses and base indices. This file provides the bit layout inside those addresses.

Visible include sites for the DCN 2.1 generated header pair include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`, which builds Renoir/DCN 2.1 display resources and register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`, which uses generated register fields for interrupt source setup and acknowledge paths.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c` and `hw_translate_dcn21.c`, which include the generated header for GPIO translation.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`, which includes the DCN 2.1 register definitions for DMUB-facing display support.

Important generic consumers and integration layers include:

- DPP color code and definitions under `display/dc/dpp/dcn10` and later DPP implementations, where `CM_3DLUT_*` and `CM_SHAPER_RAMB_*` fields are part of color pipeline register structures and LUT-loading sequences.
- MPC/MPCC code under `display/dc/mpc/dcn10`, `dcn20`, `dcn30`, and later versions, where MPCC control/status, output mux, CRC, denormalization, and OGAM fields are abstracted into `struct dcn*_mpc_registers`, `struct dcn*_mpc_shift`, and `struct dcn*_mpc_mask` tables.
- Hardware-sequencer and CRC diagnostics, which expose MPC CRC result registers through debug or validation paths.
- DC state/debug capture in `display/dc/dc.h`, where MPCC control and OGAM state are recorded as part of hardware state snapshots.

Although this repository path sits under `sources/distributed-fs/ceph-client`, the chunk is AMD display hardware metadata. It has no Ceph filesystem, distributed storage, networking, or on-disk persistence behavior.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A wrong mask or shift can compile cleanly but write the wrong bit, truncate a value, preserve stale bits during read/modify/write, fail to observe a status bit, or acknowledge the wrong event.

Color pipeline fields are visually sensitive. Incorrect `CM3_CM_SHAPER_RAMB_*`, `CM3_CM_3DLUT_*`, or MPCC OGAM masks can corrupt color management, HDR 3DLUT programming, shaper/OGAM PWL segmentation, LUT bank selection, or SRAM write enables. Symptoms may be subtle, such as banding or wrong gamma, or severe, such as bad HDR output after a modeset.

MPCC and MPC fields are topology-sensitive. Bad `MPCC_TOP_SEL`, `MPCC_BOT_SEL`, `MPCC_OPP_ID`, blend mode, alpha/gain, or output mux masks can route planes to the wrong compositor/output, break overlay blending, leave MPCCs busy/disabled, or produce black screens only for multi-plane, stereo, or multi-display configurations.

Update-lock, pending/taken, and ack fields are synchronization-sensitive. Misprogramming `MPCC_UPDATE_LOCK_SEL`, `MPC_PENDING_TAKEN_STATUS_REG*`, `MPC_UPDATE_ACK_REG5`, or `*_VUPDATE_LOCK_SET*` can make software believe an update was accepted before hardware has latched it, or leave updates blocked until a later vupdate/modeset.

Status and interrupt-like fields are easy to misuse. `MPCC_STALL_STATUS`, `MPCC_STATUS`, CRC one-shot pending/update lock, and perfmon interrupt/status fields include live or sticky state. A generic read/modify/write with a wrong mask can miss a stall, clear or fail to clear a condition, or poll forever on a status bit.

The repeated generated layouts are copy-regeneration hazards. MPCC0-MPCC7 should remain structurally aligned, and MPCC_OGAM0/1/2 RAMA/RAMB regions repeat the same field pattern. Any one-off width, shift, or mask difference should be treated as suspicious unless the ASIC register database explicitly documents it.

Chunk boundaries are artificial. This range starts after the beginning of `CM3_CM_SHAPER_RAMB_REGION_10_11` and ends at the beginning of `MPCC_OGAM2_MPCC_OGAM_RAMB_END_CNTL2_B`; the final file-level document should merge adjacent chunks before drawing conclusions about complete CM3 or MPCC_OGAM2 coverage.

## Test Signals

Useful validation signals are a mix of generated-header checks and DCN 2.1 display behavior:

- Build coverage for DCN 2.1 resource, IRQ, GPIO, DMUB, DPP, MPC, and hardware-sequencer code that includes `dcn_2_1_0_sh_mask.h`.
- Generated-register validation that every field in this chunk has a matching register address in `dcn_2_1_0_offset.h`, every mask is consistent with its shift and field width, and repeated MPCC/OGAM instances remain structurally consistent.
- DPP color tests covering shaper LUT/PWL programming, 3DLUT enable/disable, 30-bit LUT writes, HDR and SDR modes, color-management bypass, and suspend/resume or modeset LUT reload.
- MPCC composition tests with single-plane, overlay, cursor, alpha blending, global alpha/gain, background color, multi-display routing, and stereo/multiview modes.
- MPC output tests covering mux selection, denormalization clamps/modes, bypass background color, and output pipe changes across hotplug and full modesets.
- CRC and perfmon validation that one-shot and continuous CRC modes produce plausible changing results, perf counters count selected events, interrupts/status bits clear as expected, and update-lock status does not hang.
- Update synchronization tests that inspect pending/taken/ack state around surface, config, cursor, MPCC, and OPP updates, especially during vblank/vupdate, fast flips, and pipe enable/disable transitions.
- Power-management tests for shaper/HDR 3DLUT and MPCC OGAM memory power state across idle, display off/on, runtime power management, and resume.

Regression symptoms from bad constants include wrong colors, broken HDR/3DLUT/OGAM output, failed overlays or plane blending, black screens on specific pipe topologies, stale or stuck update locks, bad CRC/debug output, stuck perfmon counters, MPCC stall/error reports, or failures that affect only one repeated MPCC or OGAM instance.

## Cross-Chunk Notes

This is a generated constants-only chunk in the middle of `dcn_2_1_0_sh_mask.h`. Adjacent chunks own the beginning of the CM3 shaper RAM-B block and the continuation of MPCC_OGAM2 RAMB/end-region fields. The merge lane should treat this document as a source-tree-aligned slice of the full DCN 2.1 register-layout contract rather than as a standalone module.

### subset-b-001665: lines 22382-24866

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h

Chunk: `subset-b-001665`
Lines researched: 22382-24866

## Purpose

This chunk is part of the generated DCN 2.1 register shift/mask header for the AMD display driver. It defines bit positions (`__SHIFT`) and bit masks (`_MASK`) for selected MPC/MPCC display color blocks. The line range covers:

- The tail of `dce_dc_mpc_mpcc_ogam2_dispdec`, specifically `MPCC_OGAM2` RAM B end and region fields.
- Full output-gamma register field tables for `MPCC_OGAM3` through `MPCC_OGAM7`.
- The beginning of `dce_dc_mpc_mpc_ocsc_dispdec`, covering `MPC_OUT_CSC_COEF_FORMAT` and the first output CSC coefficient registers for `MPC_OUT0`, `MPC_OUT1`, `MPC_OUT2`, and the opening of `MPC_OUT3`.

The header itself contains no executable logic. Its purpose is to give the display core exact ASIC bit layouts so common register helper macros can write output gamma LUT configuration and output color-space conversion coefficients without hard-coded shifts in the C implementation.

## Important Definitions

The `MPCC_OGAMn` definitions are repeated per MPCC instance. For `n = 3..7`, each instance has:

- `MPCC_OGAMn_MPCC_OGAM_MODE`: 2-bit output gamma mode selector.
- `MPCC_OGAMn_MPCC_OGAM_LUT_INDEX`: 9-bit LUT write/read index.
- `MPCC_OGAMn_MPCC_OGAM_LUT_DATA`: 19-bit LUT data payload.
- `MPCC_OGAMn_MPCC_OGAM_LUT_RAM_CONTROL`: write-enable mask, RAM A/B select, and config status fields.
- `MPCC_OGAMn_MPCC_OGAM_RAMA_*` and `MPCC_OGAMn_MPCC_OGAM_RAMB_*`: double-buffered gamma RAM A/B fields for blue, green, and red channel start, slope, end, and 34 region descriptors.

The RAM A/B region definitions use a consistent packed layout:

- Region LUT offset: bits `[8:0]`, mask `0x000001FF`.
- Region segment count: bits `[14:12]`, mask `0x00007000`.
- Paired odd region offset: bits `[24:16]`, mask `0x01FF0000`.
- Paired odd region segment count: bits `[30:28]`, mask `0x70000000`.

Per-channel start/end definitions also repeat:

- `EXP_REGION_START_*`: 18-bit value at shift `0x0`, mask `0x0003FFFF`.
- `EXP_REGION_START_SEGMENT_*`: 7-bit segment field at shift `0x14`, mask `0x07F00000`.
- `EXP_REGION_LINEAR_SLOPE_*`: 18-bit field at shift `0x0`, mask `0x0003FFFF`.
- `EXP_REGION_END_*`: 16-bit field at shift `0x0`, mask `0x0000FFFF`.
- `EXP_REGION_END_SLOPE_*` and `EXP_REGION_END_BASE_*`: two 16-bit fields packed into low/high halves of the end-control register.

The `MPC_OUT_CSC_*` portion begins the output CSC block:

- `MPC_OUT_CSC_COEF_FORMAT`: one coefficient-format bit per OCSC pipe (`MPC_OCSC0_COEF_FORMAT` through `MPC_OCSC3_COEF_FORMAT`).
- `MPC_OUT{0,1,2}_CSC_MODE`: 2-bit `MPC_OCSC_MODE` selectors.
- `MPC_OUT{0,1,2}_CSC_Cxx_Cyy_{A,B}`: paired 16-bit color matrix coefficients packed into one register, with the first coefficient in bits `[15:0]` and the second in bits `[31:16]`.
- `MPC_OUT3_CSC_MODE` and the start of `MPC_OUT3_CSC_C11_C12_A` appear at the chunk boundary; the remaining `MPC_OUT3` CSC masks are outside this chunk.

## Integration Points

These macros are included by generated DCN 2.1 resource/register tables and then consumed through the display core's MPC abstraction. The immediate integration pattern is:

- Resource and MPC headers use `SF(register, field, mask_sh)`-style macros to populate `struct dcn20_mpc_shift` and `struct dcn20_mpc_mask` fields.
- Register-address macros from the companion offset header identify which MMIO register to access.
- `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_UPDATE_2`, and related helpers combine the register address with these shift/mask values.

Observed downstream consumers in the same source tree include:

- `display/dc/mpc/dcn20/dcn20_mpc.h`, which declares the DCN2 MPC register, shift, and mask field lists for MPCC OGAM and MPC output CSC.
- `display/dc/mpc/dcn20/dcn20_mpc.c`, where `mpc2_set_output_csc()`, `mpc2_set_ocsc_default()`, `mpc2_set_output_gamma()`, `mpc2_program_luta()`, and `mpc2_program_lutb()` use these fields indirectly through `mpc20->mpc_shift` and `mpc20->mpc_mask`.
- `display/dc/hwss/dcn20/dcn20_hwseq.c`, where `dcn20_program_output_csc()` chooses custom or default CSC programming and calls the MPC callbacks.

## Control Flow

This chunk does not implement control flow. Runtime flow is in the MPC and hardware-sequencer code:

1. The DC hardware sequencer decides whether a stream needs custom output CSC or a default CSC matrix.
2. It calls `mpc->funcs->set_output_csc()` or `mpc->funcs->set_ocsc_default()`.
3. The MPC code selects the inactive A/B coefficient set by reading the current OCSC mode, programs the chosen coefficient registers through `cm_helper_program_color_matrices()`, then updates `MPC_OCSC_MODE`.
4. For output gamma, the MPC code checks the current OGAM RAM state, selects the opposite RAM bank, programs region/start/end/slope registers through `cm_helper_program_xfer_func()`, writes LUT data through `MPCC_OGAM_LUT_DATA`, and switches `MPCC_OGAM_MODE` to the newly programmed RAM bank.

The mask definitions in this chunk are the contract that makes those register writes land on the intended fields.

## State And Persistence

There is no software-owned persistent state in this header. The state represented by the macros lives in display hardware registers:

- OGAM mode, LUT index/data, RAM select, and config status are MMIO-visible hardware state per MPCC instance.
- RAM A and RAM B hold double-buffered output gamma transfer-function programming.
- OCSC coefficient banks A and B hold double-buffered output color matrices per output pipe.

State survives only as long as the display hardware register context remains valid. Driver reinitialization, display mode set, GPU reset, power-gating, or register reprogramming can replace it. The driver can also read selected status fields, such as `MPCC_OGAM_CONFIG_STATUS` and OCSC debug status, to choose a non-active bank for updates.

## Dependencies

This chunk depends on the generated register-address companion headers for the actual MMIO offsets; the macros here only describe field positions and masks. It also depends on the driver-side register helper layer interpreting shift/mask pairs consistently.

Important code-level dependencies visible from consumers:

- `reg_helper.h` macros perform read/modify/write operations using the shifts and masks.
- `dcn20_mpc.h` maps these generated definitions into typed `dcn20_mpc_shift` and `dcn20_mpc_mask` structs.
- `dcn10_cm_common.h` and color-management helpers provide `cm_helper_program_xfer_func()` and `cm_helper_program_color_matrices()`, which pack gamma and matrix data into these registers.
- DC stream and pipe state choose when output CSC and OGAM programming happens.

## Risks

- A wrong shift or mask can silently corrupt adjacent fields in an MMIO register. This is especially risky in paired registers such as region pairs and CSC coefficient pairs, where low and high halves share a 32-bit word.
- The repeated `MPCC_OGAM3` through `MPCC_OGAM7` pattern means copy/generation mistakes may affect only a subset of pipes. Such errors can appear as display-dependent color failures rather than global bring-up failures.
- Incomplete coverage at chunk boundaries matters. This chunk begins in the middle of `MPCC_OGAM2` RAM B definitions and ends in the middle of the `MPC_OUT3` CSC table, so whole-file reconciliation must merge adjacent chunks before asserting full register coverage.
- The DCN2 MPC consumer field list samples `MPCC_OGAM0` masks into common per-instance fields, relying on repeated instance layouts. If any generated per-instance mask diverges unexpectedly, code using common shift/mask fields may not detect that divergence at compile time.
- A/B double buffering depends on accurate mode/status fields. Bad `MPCC_OGAM_CONFIG_STATUS`, `MPCC_OGAM_LUT_RAM_SEL`, or `MPC_OCSC_MODE` masks can cause programming into the active bank or switching to an unprogrammed bank.

## Test Signals

Useful signals for validating this chunk's correctness include:

- Build coverage for DCN2.1 resource and MPC code: missing or renamed macros should fail compilation where `SF()` field lists instantiate shift/mask structs.
- Register write tracing or MMIO dumps while enabling output gamma should show `MPCC_OGAM_LUT_RAM_CONTROL`, `MPCC_OGAM_LUT_INDEX`, `MPCC_OGAM_LUT_DATA`, RAM A/B region registers, and `MPCC_OGAM_MODE` changing for the expected MPCC instance.
- Output CSC updates should alternate between coefficient bank A and B, update only the intended `MPC_OUTn_CSC_Cxx_Cyy_{A,B}` registers, and then switch `MPC_OCSC_MODE`.
- Visual color tests should cover multiple pipes/MPCC instances, not only `MPCC_OGAM0`, because this chunk mainly covers higher instances 3 through 7.
- HDR, gamma ramp, color-management, and output colorspace changes are high-value functional paths because they exercise both OGAM and OCSC programming.
- Debug reads of `MPCC_OGAM_CONFIG_STATUS` and OCSC current mode should match the bank chosen by the driver after a programmed update.

## Chunk Notes For Merge Lane

This is a declarative register-mask chunk, not a standalone functional module. The final per-file research should merge it with neighboring chunks to describe the complete `dcn_2_1_0_sh_mask.h` generated-header contract. This chunk specifically contributes the MPC output gamma and output CSC bitfield portion for DCN 2.1.

### subset-b-001666: lines 24867-27467

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 24867-27467

## Scope

This chunk is part of the generated AMD DCN 2.1.0 ASIC register shift/mask header. It covers lines 24867-27467 and exports preprocessor constants for display register fields. The slice contains 2,118 `#define` entries: 1,059 `__SHIFT` constants and 1,059 `_MASK` constants. It has no C functions, structs, enums, or executable control flow; the API is the generated macro namespace consumed by AMDGPU display register access helpers.

The chunk starts in the tail of `MPC_OUT3` output CSC coefficient fields and ends inside the beginning of the `OTG0` timing generator interrupt/status fields. Whole-file reconciliation should merge this with adjacent chunks for complete MPC and OTG coverage.

## Purpose

The purpose of this chunk is to map DCN 2.1 output/display-pipe hardware fields to exact bit positions and bit masks. Runtime display code can then use symbolic field names through register helper macros instead of literal bit constants.

Major hardware domains represented here are:

- `MPC_OUT3` output color-space-conversion coefficient registers for MPC output instance 3, including A/B coefficient banks.
- `DC_PERFMON15` and OPP-side `DC_PERFMON4` performance monitor counter control, state, count, compare-value, interrupt, run-enable, and clock fields.
- `BL1_PWM_*` and `DC_ABM1_*` backlight and ambient/backlight modulation fields, including PWM levels, ABM control, histogram/luma statistics, ACE coefficients, sample rates, histogram result bins, and master lock.
- Repeated OPP instance groups `FMT0` through `FMT5`, `DPG0` through `DPG5`, `OPPBUF0` through `OPPBUF5`, `OPP_PIPE0` through `OPP_PIPE5`, and `OPP_PIPE_CRC0` through `OPP_PIPE_CRC5`.
- OPP top-level memory power status/control fields and `DSCRM0` through `DSCRM5` DSC rate-control/average-rate fields.
- `ODM0` through `ODM5` OPTC input blocks for ODM segmentation, DSC mode, bytes-per-pixel, segment/slice width, input clock gating, memory selection, soft reset, underflow, and double-buffer state.
- The first `OTG0` timing generator fields for horizontal/vertical total, blanking, sync, dynamic refresh-rate vertical-total control, and vertical-total/vsync interrupt status.

## Important API Surface

The exported naming convention is:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

Important families in this chunk include:

- `MPC_OUT3_CSC_C*_A/B__MPC_OCSC_*` for 16-bit packed output CSC matrix coefficients.
- `DC_PERFMON15_PERFCOUNTER_CNTL`, `DC_PERFMON15_PERFCOUNTER_CNTL2`, `DC_PERFMON15_PERFCOUNTER_STATE`, `DC_PERFMON15_PERFMON_CNTL`, and `DC_PERFMON15_PERFMON_CVALUE_INT_MISC` for selecting performance events, count modes, hardware stop/count-off conditions, active state, interrupt status/ack, and 48-bit count-value halves.
- `BL1_PWM_*` fields for ambient light level, user/target/current/final/minimum duty-cycle levels, ABM enable and gradient/scale control, sample-rate updates, and group register locking.
- `DC_ABM1_CNTL`, `DC_ABM1_IPCSC_COEFF_SEL`, `DC_ABM1_ACE_*`, `DC_ABM1_HG_*`, and `DC_ABM1_LS_*` for adaptive backlight modulation setup and histogram/luma-stat readback.
- `FMTn_FMT_CONTROL`, `FMTn_FMT_BIT_DEPTH_CONTROL`, `FMTn_FMT_CLAMP_*`, `FMTn_FMT_DITHER_RAND_*`, `FMTn_FMT_MAP420_MEMORY_CONTROL`, and `FMTn_FMT_422_CONTROL` for OPP pixel encoding, subsampling, truncation, temporal/spatial dithering, clamp limits, random seeds, 4:2:0 memory power, and 4:2:2 edge handling.
- `DPGn_DPG_CONTROL`, `DPGn_DPG_RAMP_CONTROL`, `DPGn_DPG_DIMENSIONS`, `DPGn_DPG_COLOUR_*`, and `DPGn_DPG_STATUS` for display pattern generator mode, dimensions, colors, ramp parameters, segment offset, and double-buffer status.
- `OPPBUFn_OPPBUF_CONTROL` and `OPPBUFn_OPPBUF_3D_PARAMETERS_*` for active width, display segmentation, overlap/repetition, padded pixels, stereo/3D active-space sizes, dummy data, and double-buffer pending state.
- `OPP_PIPE_CRCn_OPP_PIPE_CRC_CONTROL`, `*_MASK`, and `*_RESULT*` for OPP CRC enable/mode/source selection, one-shot pending, masks, and component results.
- `ODM*_OPTC_INPUT_GLOBAL_CONTROL`, `ODM*_OPTC_DATA_SOURCE_SELECT`, `ODM*_OPTC_DATA_FORMAT_CONTROL`, `ODM*_OPTC_BYTES_PER_PIXEL`, `ODM*_OPTC_WIDTH_CONTROL`, and `ODM*_OPTC_INPUT_CLOCK_CONTROL` for ODM input routing, DSC, segmentation, clocks, soft reset, underflow, and update-pending status.
- `OTG0_OTG_H_*`, `OTG0_OTG_V_TOTAL*`, `OTG0_OTG_V_TOTAL_CONTROL`, `OTG0_OTG_V_TOTAL_INT_STATUS`, and the start of `OTG0_OTG_VSYNC_NOM_INT_STATUS` for timing programming and dynamic refresh-rate/event interrupt handling.

These constants are normally referenced indirectly through AMD display register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `SF`, `OPP_SF`, and generated field-list tables. The header must be paired with the matching DCN 2.1.0 register offset header.

## Control Flow

There is no local control flow in this generated header. Runtime behavior is imposed by callers:

- OPP constructors bind `FMT`, `DPG`, `OPPBUF`, `OPP_PIPE`, and `OPP_PIPE_CRC` offsets, masks, and shifts into per-instance register tables.
- Display pipe programming writes `FMTn` fields when setting pixel encoding, subsampling, clamp, truncation, dithering, and memory power behavior.
- Pattern generator code writes `DPGn` fields and waits on double-buffer status when producing test patterns.
- CRC capture paths program `OPP_PIPE_CRCn` control/mask fields, then read component result registers for validation or diagnostics.
- ABM/backlight code programs `BL1_PWM_*` and `DC_ABM1_*` fields and reads histogram/luma result fields to drive panel brightness decisions.
- ODM/OPTC code writes `ODM*_OPTC_*` fields for output-merger segmentation and DSC routing, while monitoring soft reset, underflow, clock, and double-buffer state.
- Timing-generator code writes `OTG0` horizontal/vertical timing and dynamic refresh-rate fields, then handles vertical-total or vsync interrupt status/ack/mask fields.
- Perfmon code programs event selection, counting modes, count-off conditions, run-enable/stop sources, and interrupt acknowledgement using the `DC_PERFMON*` fields.

Ordering, locking, and polling are external contracts. For example, callers must not update packed FMT/ODM/OTG fields mid-frame without the relevant double-buffer/update semantics, and interrupt status/ack bits must be handled with hardware-prescribed write patterns.

## State and Persistence

The file stores no software state. Its macros describe memory-mapped display hardware state that persists in GPU registers while the blocks are powered:

- MPC CSC coefficients persist as active output color conversion state.
- FMT fields persist as active output formatting, dither, clamp, subsampling, and memory-power state for each OPP instance.
- DPG and OPPBUF fields persist as test-pattern, segmentation, stereo, and output-buffer state.
- OPP CRC state persists as capture configuration and latched result values.
- BL/ABM fields persist as backlight control, image-statistics, histogram, and adaptive contrast/backlight state.
- ODM fields persist as OPTC input routing, segment width, DSC slice/bytes-per-pixel, clock, memory selection, underflow, and pending-update state.
- OTG fields persist as timing-generator configuration and sticky/event interrupt state.
- Perfmon fields persist as counter configuration, live counter values, active state, and sticky interrupt bits.

Incorrect constants can leave display hardware programmed incorrectly until a modeset, block reinitialization, power transition, or GPU reset restores known values.

## Dependencies and Integration Points

This chunk depends on the generated DCN 2.1.0 offset header and on the AMD display register-access macro framework that token-pastes register and field names into `__SHIFT` and `_MASK` symbols.

Key integration points include:

- DCN 2.1 display bring-up paths selected through the DC resource, clock manager, GPIO, and DMUB code. `dmub_dcn21.c`, DCN21 GPIO factory/translate code, and related DCN21 modules include `dcn/dcn_2_1_0_sh_mask.h`.
- OPP code in `drivers/gpu/drm/amd/display/dc/opp/`, especially DCN10/DCN20-style field lists and helpers that use `FMT0_*`, `DPG0_*`, `OPPBUF0_*`, and `OPP_PIPE_CRC0_*` symbols as the base instance and instantiate per-OPP register tables.
- ABM/backlight code such as `drivers/gpu/drm/amd/display/dc/dce/dmub_abm_lcd.c`, which writes `DC_ABM1_*` setup fields and reads/statistically consumes histogram/luma fields.
- OPTC timing and ODM code in `drivers/gpu/drm/amd/display/dc/optc/`, which uses `OTG0_*` and `ODM0_OPTC_*` masks for timing, dynamic refresh-rate, DSC, segmentation, underflow, and clock/pending status.
- Performance-monitor and diagnostic paths that consume `DC_PERFMON*` fields for event selection, counters, and interrupt management.
- Cross-generation generated headers (`dcn_2_0_*`, `dcn_3_*`, and later) with similar names but potentially different field availability, mask widths, or reserved-bit layout.

## Risks

- A wrong shift or mask silently writes the wrong hardware bit. Highest-risk fields here include interrupt ack/status bits, double-buffer pending bits, clock enable/status, soft reset, underflow clear/status, OTG timing, ODM DSC/segment routing, and FMT dither/clamp/subsampling controls.
- Instance drift is likely because `FMT`, `DPG`, `OPPBUF`, `OPP_PIPE`, `OPP_PIPE_CRC`, `DSCRM`, and `ODM` families repeat from 0 through 5. A copy/paste or generation mismatch may only break a specific pipe.
- Packed 16-bit coefficient/result fields are common in MPC, FMT clamp/seed, DPG colors, CRC results, and OTG timing. Swapping high/low fields or using the wrong half of a packed register can create visual corruption without compile-time errors.
- Status and clear/ack bits share registers with enable, mask, type, and control bits in perfmon, ODM underflow, OTG interrupts, and CRC paths. Careless read-modify-write sequences can lose events or acknowledge sticky status unexpectedly.
- Timing and segment-width masks are narrow. Overflow in OTG totals, ODM segment/slice widths, DPG dimensions, OPPBUF active width, or side-by-side stereo width can manifest only on particular modes or DSC/ODM topologies.
- ABM histogram and luma-stat result fields are readback-heavy. Wrong masks may bias adaptive backlight decisions rather than causing an obvious failure.
- Generated headers are rarely unit-tested directly; many regressions surface only through full driver builds, static register-database comparisons, or hardware display behavior.

## Test Signals

Useful validation signals for changes to this chunk are:

- AMDGPU display build coverage for DCN 2.1 and neighboring DCN20 code paths, catching missing/renamed macros in OPP, ABM, OPTC/ODM, GPIO, DMUB, and timing code.
- Static comparison against the vendor register database and the matching DCN 2.1.0 offset header, verifying every `__SHIFT` has the intended `_MASK` and that repeated instance families are consistent where hardware requires them.
- Multi-display and multi-pipe runtime tests that exercise OPP instances 0-5, including format changes, RGB/YUV subsampling, clamp/dither configuration, 4:2:0 memory power, OPPBUF segmentation, and OPP CRC readback.
- ABM/backlight tests that cover PWM level programming, ABM enable/disable, histogram/luma result reads, sample-rate updates, and lock behavior.
- ODM/DSC tests with split output, DSC enabled, varying slice/segment widths, underflow detection/clear, input clock gating, and memory selection.
- OTG timing tests covering modesets, dynamic refresh-rate vertical-total min/max/mid behavior, vsync/vtotal interrupts, and interrupt mask/ack behavior.
- Perfmon diagnostics that select events, run counters under different enable/stop modes, read low/high count values, and verify interrupt status/ack handling.

## Chunk Notes

This chunk is generated register metadata, not functional logic. Its research value is identifying which hardware surfaces are covered and where mask/shift errors would propagate: OPP formatting and diagnostics, ABM/backlight statistics, ODM/DSC routing, output timing, performance counters, and repeated per-pipe register families. The final merged file report should combine this with adjacent chunks for full `dcn_2_1_0_sh_mask.h` coverage.

### subset-b-001667: lines 27468-29926

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 27468-29926

## Purpose

This chunk is part of AMD's generated DCN 2.1 register field mask header. It defines preprocessor constants for display timing generator / output timing generator (OTG) register bit positions and masks. The covered range starts in the `dce_dc_optc_otg0_dispdec` block, contains the complete repeated field definitions for `dce_dc_optc_otg1_dispdec` and `dce_dc_optc_otg2_dispdec`, and ends at the first timing fields of `dce_dc_optc_otg3_dispdec`.

The file does not implement executable logic. Its purpose is to provide stable compile-time metadata used by AMDGPU display code to construct register access tables and field-update helpers for Renoir/DCN21 hardware.

## Chunk Shape

- Line range: 27468-29926.
- Macro volume in this range: 2144 `#define` entries, consisting of 1071 `*_SHIFT` definitions and 1073 `*_MASK` definitions.
- Prefix coverage: late `OTG0` definitions, full `OTG1` and `OTG2` definitions, and the start of `OTG3`.
- Each register field generally appears as a pair:
  - `<REGISTER>__<FIELD>__SHIFT`
  - `<REGISTER>__<FIELD>_MASK`

## Important Register Areas

- Timing geometry: `OTG_H_TOTAL`, `OTG_H_BLANK_START_END`, `OTG_H_SYNC_A`, `OTG_V_TOTAL`, `OTG_V_TOTAL_MIN`, `OTG_V_TOTAL_MAX`, `OTG_V_TOTAL_MID`, `OTG_V_BLANK_START_END`, `OTG_V_SYNC_A`, and related polarity/control fields. These fields describe the horizontal and vertical timing programmed for an active display pipe.
- Dynamic refresh / variable timing: `OTG_V_TOTAL_CONTROL`, `OTG_DRR_CONTROL`, and `OTG_V_TOTAL_LAST_USED_BY_DRR` expose fields used when the driver adjusts vertical totals for DRR/VRR behavior.
- Triggering and synchronization: `OTG_TRIGA_CNTL`, `OTG_TRIGB_CNTL`, manual trigger registers, `OTG_FORCE_COUNT_NOW_CNTL`, `OTG_GSL_CONTROL`, `OTG_GSL_WINDOW_X/Y`, and `OTG_GSL_VSYNC_GAP` describe trigger source selection, pipe selection, edge detection, GSL master/slave behavior, and sync windows.
- Master/update locking: `OTG_UPDATE_LOCK`, `OTG_MASTER_UPDATE_LOCK`, `OTG_GLOBAL_CONTROL0/1/2/3`, and `OTG_VUPDATE_KEEPOUT` define fields that gate when timing and pipe state updates are applied.
- Interrupt and event status: `OTG_GLOBAL_SYNC_STATUS`, `OTG_VERTICAL_INTERRUPT0/1/2_CONTROL`, `OTG_V_TOTAL_INT_STATUS`, `OTG_VSYNC_NOM_INT_STATUS`, and `OTG_RANGE_TIMING_INT_STATUS` define enable, status, event, clear, mask, and interrupt-type bits.
- Display state/status readback: `OTG_STATUS`, `OTG_STATUS_POSITION`, `OTG_NOM_VERT_POSITION`, `OTG_STATUS_FRAME_COUNT`, `OTG_STATUS_VF_COUNT`, `OTG_STATUS_HV_COUNT`, interlace/stereo status, pixel readback registers, and snapshot status/control/position/frame fields.
- Blank/black/color handling: `OTG_BLANK_CONTROL`, `OTG_BLANK_DATA_COLOR`, `OTG_BLANK_DATA_COLOR_EXT`, `OTG_BLACK_COLOR`, and `OTG_BLACK_COLOR_EXT` describe color channel packing and blanking behavior.
- CRC and validation: `OTG_CRC_CNTL`, `OTG_CRC_CNTL2`, CRC window controls, CRC data registers, and CRC signature mask controls define the hardware CRC capture and readback surfaces used for display validation.
- Pipe update tracking: `OTG_PIPE_UPDATE_STATUS` exposes pending/taken/clear bits for flip, DC register update, cursor update, and vupdate keepout status.
- Miscellaneous control: `OTG_CLOCK_CONTROL`, `OTG_REQUEST_CONTROL`, `OTG_DSC_START_POSITION`, `OTG_STATIC_SCREEN_CONTROL`, `OTG_3D_STRUCTURE_CONTROL`, `OTG_PIPE_ABORT_CONTROL`, and `OTG_SPARE_REGISTER`.

## APIs, Types, and Macro Contracts

This chunk exports C preprocessor symbols only. There are no functions, structs, enums, storage objects, or inline helpers in the chunk itself. The important API contract is naming consistency:

- Register names are prefixed by hardware instance, for example `OTG1_OTG_GLOBAL_SYNC_STATUS`.
- Field names are embedded after a double underscore, for example `VSTARTUP_INT_EN`.
- Consumers concatenate tokens to form `OTG<n>_<register>__<field>_MASK` or `OTG<n>_<register>__<field>__SHIFT`.

The DCN21 display stack includes this header from:

- `display/dmub/src/dmub_dcn21.c`, where `FD_MASK` and `FD_SHIFT` use generated masks/shifts for DMUB register tables.
- `display/dc/irq/dcn21/irq_service_dcn21.c`, where IRQ table macros form OTG mask names for vblank, vupdate-no-lock, and vertical-line interrupt programming.
- `display/dc/resource/dcn21/dcn21_resource.c`, where DCN21 resource construction pulls generated addresses and masks into hardware object register tables.
- DCN21 GPIO factory/translator files, for shared generated DCN21 register metadata outside this specific OTG chunk.

The chunk also aligns with the common OPTC abstraction under `display/dc/optc/dcn10/dcn10_optc.h`, whose field lists include many of these names (`OTG_MASTER_UPDATE_LOCK`, `OTG_V_TOTAL`, `OTG_TRIGA_CNTL`, CRC fields, DRR fields, update-lock DB fields). Those field lists are used to populate typed mask/shift tables for timing generator code.

## Control Flow and Runtime Behavior

There is no runtime control flow in this header. Runtime behavior appears when other compilation units use these constants in register helpers:

- IRQ setup in `irq_service_dcn21.c` maps DC IRQ sources to OTG registers. For example, `vupdate_no_lock_int_entry(reg_num)` expands to an `OTG<reg_num>_OTG_GLOBAL_SYNC_STATUS` enable bit `VUPDATE_NO_LOCK_INT_EN` and ack bit `VUPDATE_NO_LOCK_EVENT_CLEAR`. `vblank_int_entry(reg_num)` similarly uses `VSTARTUP_INT_EN` and `VSTARTUP_EVENT_CLEAR`.
- Resource and OPTC initialization code uses generated addresses from the matching `dcn_2_1_0_offset.h` plus these masks/shifts to build per-pipe register tables. Later display operations use those tables to program timing, triggers, blanking, CRC capture, update locks, and dynamic vertical totals.
- Register helper macros normally read/modify/write only the masked field, so the correctness of every write depends on the mask and shift matching the hardware register layout exactly.

## State and Persistence

The macros are immutable compile-time constants. They do not persist state directly.

The state they address is hardware state in DCN OTG blocks:

- Programmed timing state persists in MMIO registers until overwritten, reset, or power-gated.
- Event/status bits such as vstartup, vupdate, range timing update, and flip/update-taken bits can be sticky until cleared through corresponding `*_CLEAR` fields.
- Master/update lock fields can delay or gate when pending pipe state becomes visible to scanout.
- CRC data, frame counters, current position counters, and interlace/stereo status are readback-oriented state derived from live scanout.

The chunk therefore affects persistence indirectly by determining which bits the driver writes or clears in hardware registers.

## Dependencies and Integration Points

- Depends on the matching generated offset header `dcn_2_1_0_offset.h`; masks/shifts alone do not identify MMIO addresses.
- Depends on generated base segment symbols from `renoir_ip_offset.h` in DCN21 users.
- Integrated through AMD display register helper macros such as `FD_MASK`, `FD_SHIFT`, field-list `SF(...)` expansion, and IRQ table token concatenation.
- Closely coupled to DCN21/Renoir hardware generation. Copying these definitions to a different DCN generation without matching offsets and hardware field layout would be unsafe.
- Related semantic enums for some fields live in ASIC enum headers such as `navi10_enum.h` and `soc24_enum.h`, but this header itself only provides bit layout.

## Risks

- A wrong mask or shift silently targets the wrong hardware bits, causing display timing corruption, missed interrupts, stuck update locks, CRC mismatches, bad DRR behavior, or blank/black-frame errors.
- Because consumers build symbol names through token concatenation, renaming a macro or dropping one field becomes a compile-time failure in dependent DCN21 code.
- Instance repetition is easy to corrupt mechanically. `OTG1` and `OTG2` must preserve the same field layout while binding to their own instance addresses from the offset header.
- Status and clear bits share registers in several areas. Incorrect masks for `*_EVENT_CLEAR`, `*_TAKEN_CLEAR`, or interrupt clear fields can accidentally clear unrelated events or leave sticky interrupts asserted.
- Update lock and GSL fields are timing-sensitive. Bad values can make pipe updates occur outside intended vblank/vupdate windows, causing visible artifacts or synchronization loss across pipes.

## Test Signals

- Build signal: DCN21 AMDGPU display objects compile. Missing or renamed symbols should surface in `dmub_dcn21.c`, `irq_service_dcn21.c`, `dcn21_resource.c`, and OPTC register table construction.
- IRQ signal: vblank, vupdate-no-lock, and vertical-line interrupts can be enabled, acknowledged, and do not storm. Relevant masks are in `OTG_GLOBAL_SYNC_STATUS` and `OTG_VERTICAL_INTERRUPT0_CONTROL`.
- Mode-set signal: displays light correctly across OTG0/1/2/3-capable pipes with correct sync polarity, blanking intervals, and frame counters.
- DRR/VRR signal: vertical total min/max/mid programming behaves correctly and `OTG_DRR_CONTROL` readback reflects expected totals.
- Update-lock signal: atomic flips, cursor updates, and DC register updates transition through pending/taken bits in `OTG_PIPE_UPDATE_STATUS` without getting stuck.
- CRC signal: display CRC capture over configured windows produces stable values for static frames and changes predictably when content changes.
- Multi-pipe sync signal: GSL/master update lock paths synchronize pipes without vupdate-no-lock events under synchronized display scenarios.

### subset-b-001668: lines 29927-32383

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 29927-32383

## Scope

This chunk is a generated AMDGPU DCN 2.1 shift/mask header slice. It contains preprocessor constants only: no functions, structs, enums, storage objects, or executable control flow. The exported surface is the usual AMD register-helper contract of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros.

The range has 2,457 source lines. Inside the requested line window there are 2,144 `#define` entries: 1,074 shift macros and 1,070 mask macros. The count is intentionally uneven because the chunk ends in the middle of `OTG5_OTG_RANGE_TIMING_INT_STATUS`: line 32383 contains only the first mask for that register, while the remaining masks and subsequent `OTG5_OTG_DRR_CONTROL` fields start in the next chunk.

The covered hardware domain is the DCN output timing generator and display encoder controller register layout for later OTG instances:

- Tail of `OTG3`, beginning at `OTG3_OTG_H_SYNC_A_CNTL` and continuing through `OTG3_OTG_SPARE_REGISTER`.
- Complete generated `addressBlock: dce_dc_optc_otg4_dispdec`, from `OTG4_OTG_H_TOTAL` through `OTG4_OTG_SPARE_REGISTER`.
- Most of generated `addressBlock: dce_dc_optc_otg5_dispdec`, from `OTG5_OTG_H_TOTAL` through the first mask of `OTG5_OTG_RANGE_TIMING_INT_STATUS`.

## Purpose

The chunk provides exact bit positions and already-positioned bit masks for DCN 2.1 OTG timing-generator registers. The OTG block is responsible for display timing production and synchronization: horizontal and vertical totals, blanking, sync pulses, vblank/vupdate/vready events, update locks, dynamic refresh-rate programming, global-swap-lock coordination, CRC capture, stereo/3D timing state, and display pipeline update status.

Higher-level display code does not hand-code these bit positions. Instead, DCN21 resource setup includes this generated header and expands generic field-list macros into per-generation `shift` and `mask` tables. Runtime register helpers then use those tables to encode or decode fields during modesets, page flips, vblank/vline interrupt setup, CRC capture, DSC positioning, dynamic refresh-rate changes, and synchronized multi-display updates.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The important interface is the generated macro namespace:

- `OTG3_*`, `OTG4_*`, and `OTG5_*` prefixes identify the hardware instance.
- `*_SHIFT` constants hold the low bit of a field.
- `*_MASK` constants hold the field mask already shifted into register position.
- Register-heading comments such as `//OTG4_OTG_GLOBAL_SYNC_STATUS` group related field macros.
- Address-block comments identify generated register windows, notably `dce_dc_optc_otg4_dispdec` and `dce_dc_optc_otg5_dispdec`.

Important register families in this range include:

- Timing geometry: `OTG_H_TOTAL`, `OTG_H_BLANK_START_END`, `OTG_H_SYNC_A`, `OTG_H_SYNC_A_CNTL`, `OTG_H_TIMING_CNTL`, `OTG_V_TOTAL`, `OTG_V_TOTAL_MIN`, `OTG_V_TOTAL_MAX`, `OTG_V_TOTAL_MID`, `OTG_V_BLANK_START_END`, `OTG_V_SYNC_A`, and `OTG_V_SYNC_A_CNTL`.
- Dynamic refresh rate and vtotal control: `OTG_V_TOTAL_CONTROL`, `OTG_V_TOTAL_INT_STATUS`, and `OTG_DRR_CONTROL` for OTG3 and OTG4. The OTG5 DRR fields are outside this chunk.
- Trigger and manual control: `OTG_TRIGA_CNTL`, `OTG_TRIGA_MANUAL_TRIG`, `OTG_TRIGB_CNTL`, `OTG_TRIGB_MANUAL_TRIG`, `OTG_FORCE_COUNT_NOW_CNTL`, `OTG_MANUAL_FORCE_VSYNC_NEXT_LINE`, `OTG_TRIG_MANUAL_CONTROL`, and `OTG_MANUAL_FLOW_CONTROL`.
- Output state and counters: `OTG_CONTROL`, `OTG_BLANK_CONTROL`, `OTG_PIPE_ABORT_CONTROL`, `OTG_INTERLACE_CONTROL`, `OTG_INTERLACE_STATUS`, `OTG_STATUS`, `OTG_STATUS_POSITION`, `OTG_NOM_VERT_POSITION`, `OTG_STATUS_FRAME_COUNT`, `OTG_STATUS_VF_COUNT`, `OTG_STATUS_HV_COUNT`, `OTG_COUNT_CONTROL`, and `OTG_COUNT_RESET`.
- Interrupts and event status: `OTG_GLOBAL_SYNC_STATUS`, `OTG_INTERRUPT_CONTROL`, `OTG_VERTICAL_INTERRUPT0_CONTROL`, `OTG_VERTICAL_INTERRUPT1_CONTROL`, `OTG_VERTICAL_INTERRUPT2_CONTROL`, `OTG_VSYNC_NOM_INT_STATUS`, and `OTG_RANGE_TIMING_INT_STATUS`.
- Double-buffer and update control: `OTG_UPDATE_LOCK`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_MASTER_UPDATE_LOCK`, `OTG_GLOBAL_CONTROL0`, `OTG_GLOBAL_CONTROL1`, `OTG_GLOBAL_CONTROL2`, `OTG_GLOBAL_CONTROL3`, and `OTG_VUPDATE_KEEPOUT`.
- Color, CRC, and readback: `OTG_BLANK_DATA_COLOR`, `OTG_BLANK_DATA_COLOR_EXT`, `OTG_BLACK_COLOR`, `OTG_BLACK_COLOR_EXT`, `OTG_PIXEL_DATA_READBACK0`, `OTG_PIXEL_DATA_READBACK1`, `OTG_CRC_CNTL`, `OTG_CRC_CNTL2`, CRC window controls, CRC data registers, and CRC signal masks.
- Stereo, 3D, GSL, and DSC: `OTG_STEREO_FORCE_NEXT_EYE`, `OTG_STEREO_STATUS`, `OTG_STEREO_CONTROL`, `OTG_3D_STRUCTURE_CONTROL`, `OTG_GSL_VSYNC_GAP`, `OTG_GSL_CONTROL`, `OTG_GSL_WINDOW_X`, `OTG_GSL_WINDOW_Y`, and `OTG_DSC_START_POSITION`.
- Pipeline status: `OTG_PIPE_UPDATE_STATUS` for flip, DC register, cursor update, and vupdate keepout state. The complete OTG5 pipe-update block is outside this line range.

## Control Flow

This header has no local control flow. Runtime behavior is in consumers that include `dcn_2_1_0_offset.h` and this shift/mask header, then bind addresses and fields into register tables.

A typical control path is:

1. DCN21 resource code includes `dcn/dcn_2_1_0_offset.h` and `dcn/dcn_2_1_0_sh_mask.h`.
2. Resource setup expands `TG_COMMON_REG_LIST_DCN2_0(id)` to assign OTG register addresses and expands `TG_COMMON_MASK_SH_LIST_DCN2_0(__SHIFT)` and `TG_COMMON_MASK_SH_LIST_DCN2_0(_MASK)` into timing-generator shift/mask tables.
3. Common OPTC code calls helpers such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, `REG_READ`, `REG_WRITE`, and `REG_WAIT`.
4. Those helpers use this generated field data to program timing, enable or disable CRTC output, lock or unlock double-buffered updates, configure vblank/vline/vupdate events, collect CRCs, and read status fields.

Representative flows represented by the fields in this chunk include:

- CRTC timing programming writes horizontal total, blanking, sync, vertical total, vblank, vsync, and divide-by-two timing fields.
- Dynamic refresh rate programming writes `OTG_V_TOTAL_MIN`, `OTG_V_TOTAL_MAX`, `OTG_V_TOTAL_MID`, and selection bits in `OTG_V_TOTAL_CONTROL`; later status can read `OTG_V_TOTAL_LAST_USED_BY_DRR` where present.
- Vblank and vupdate interrupt setup uses `OTG_GLOBAL_SYNC_STATUS` fields such as `VSTARTUP_INT_EN`, `VSTARTUP_EVENT_CLEAR`, `VUPDATE_NO_LOCK_INT_EN`, and `VUPDATE_NO_LOCK_EVENT_CLEAR`.
- Vline interrupt setup uses `OTG_VERTICAL_INTERRUPT0_POSITION` and `OTG_VERTICAL_INTERRUPT0_CONTROL` fields for line start/end, enable, status, clear, and interrupt type.
- Page flip, register update, cursor update, and keepout status are exposed through `OTG_PIPE_UPDATE_STATUS`.
- CRC capture setup uses `OTG_CRC_CNTL`, `OTG_CRC_CNTL2`, CRC window coordinates, CRC data readbacks, and signal masks.
- Multi-display synchronization and master-update-lock behavior use `OTG_GSL_CONTROL`, `OTG_GSL_VSYNC_GAP`, GSL windows, vupdate keepout, and global control/update-lock fields.
- DSC timing alignment uses `OTG_DSC_START_POSITION` X and line-number fields.

The macros do not express ordering rules, access permissions, volatile behavior, or write-one-to-clear semantics. Callers must know which fields are configuration latches, read-only status, sticky event bits, clear bits, interrupt masks, update-pending indicators, or self-clearing controls.

## State And Persistence Behavior

The file itself stores no state and has no persistence. It describes fields in MMIO registers whose values persist according to DCN hardware semantics until changed by software, hardware state machines, display reset, power management, or GPU reset.

Important hardware state represented here includes:

- Programmed scanout timing: horizontal/vertical totals, blanking windows, sync windows, sync polarity, timing divide mode, and nominal vertical counters.
- Dynamic refresh-rate state: min/max/mid vertical totals, selection bits, mid-frame replacement controls, event masks, last-used-vtotal status, and vtotal event interrupt state.
- Output enable and blanking state: master enable, blank-data enable, display read-request disable, current blank state, pipe abort, clock enable/gating/reset, and busy status.
- Counter and live-position state: current horizontal/vertical counters, frame counters, vertical-field counters, interlace current/next field, snapshot position/frame, and status readbacks for hblank, vblank, hsync, vsync, vupdate, and active display.
- Buffered update state: update locks, double-buffer pending bits, immediate-update control, blank-data double-buffer enable, timing update pending flags, DSC-position update pending, and master update-lock windows.
- Interrupt state: vstartup, vupdate, vupdate-no-lock, vready, vtotal-min, vsync-nominal, vertical interrupt 0/1/2, snapshot, force-count, force-vsync, trigger, GSL gap, and range-timing status/mask/type/clear fields.
- CRC and readback state: programmed CRC selection, one-shot pending flags, DSC/data-stream/data-format modes, CRC windows, CRC result registers, and pixel readback registers.
- Stereo, 3D, and synchronization state: stereo eye/field controls, stereo sync output, 3D structure enable/update/reset/status, GSL master and group enable, GSL delay/check windows, and GSL gap observation.

Incorrect state can survive until a full modeset, CRTC disable/enable, link reconfiguration, suspend/resume, or GPU reset rewrites the affected register block.

## Dependencies And Integration Points

The direct companion file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`, which provides matching register addresses. This chunk provides bit layout within those registers.

Observed integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`, which includes the DCN 2.1 offset and shift/mask headers and expands timing-generator register, shift, and mask lists for DCN21 resources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn20/dcn20_optc.h`, which defines `TG_COMMON_REG_LIST_DCN2_0` and `TG_COMMON_MASK_SH_LIST_DCN2_0`; those lists consume OTG fields from this generated namespace for DCN2-class timing generators.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`, which includes this header and uses generated masks for OTG vblank, vupdate-no-lock, and vertical-line interrupt register entries.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`, which includes the same generated header for DMUB common register-field definitions. This chunk is not primarily DMUB-specific, but it shares the generation header contract.
- Common OPTC implementation files such as `dcn10_optc.c` and `dcn20_optc.c`, which call register helpers against fields represented here for timing setup, DRR, CRC, DSC, GSL, double-buffer locks, and status collection.
- Display debug and state-reporting structures in `dc.h`, where comments explicitly map fields such as `OTG_H_TOTAL`, `OTG_V_TOTAL`, `OTG_V_TOTAL_CONTROL`, `OTG_GSL_CONTROL`, `OTG_DRR_CONTROL`, `OTG_DOUBLE_BUFFER_CONTROL`, and `OTG_PIPE_UPDATE_STATUS` to captured hardware state.

Although the repository path includes `sources/distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata. It has no Ceph filesystem, distributed storage, network protocol, or persistent filesystem behavior.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These constants can be syntactically valid while pointing a register helper at the wrong bit. A bad shift or mask can corrupt adjacent fields, truncate values, miss read-only status, acknowledge the wrong event, or leave sticky bits uncleared.

Timing fields are display-critical. Errors in `OTG_H_TOTAL`, blanking, sync, `OTG_V_TOTAL`, or vtotal min/max/mid fields can produce unstable modes, blank displays, refresh-rate mismatch, VRR/DRR failures, broken interlace behavior, or timing that violates sink limits.

Interrupt fields mix enable, status, type, clear, and mask bits in the same registers. Mistakes in `OTG_GLOBAL_SYNC_STATUS`, `OTG_VERTICAL_INTERRUPT*_CONTROL`, `OTG_V_TOTAL_INT_STATUS`, `OTG_INTERRUPT_CONTROL`, or `OTG_RANGE_TIMING_INT_STATUS` can cause missing vblank/vline/vupdate notifications, interrupt storms, stale event state, or page-flip completion problems.

Double-buffer and update-lock fields are ordering-sensitive. Wrong masks in `OTG_UPDATE_LOCK`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_MASTER_UPDATE_LOCK`, global controls, GSL controls, or vupdate keepout can cause register updates to latch in the wrong frame, never latch, latch during active scanout, or desynchronize multiple pipes.

CRC and readback fields are validation-sensitive. Incorrect `OTG_CRC_CNTL`, `OTG_CRC_CNTL2`, CRC window, data, or signal mask constants can invalidate automated display CRC tests, especially with DSC, split/combine modes, stereo, or interlace.

The repeated OTG3/OTG4/OTG5 layout creates copy-generation risk. The register families are mostly structurally identical across instances, so a one-off field-width or shift difference should be treated as suspicious unless confirmed by the ASIC register source. This chunk also has artificial boundaries: it starts after the beginning of the OTG3 block and ends before the full `OTG5_OTG_RANGE_TIMING_INT_STATUS` mask set, so per-file conclusions must be reconciled with neighboring chunks.

## Test Signals

Useful validation signals are mostly build coverage plus display hardware behavior:

- Compile coverage for DCN21 resource, IRQ, OPTC, DCCG, DMUB, and display-core code that includes `dcn_2_1_0_sh_mask.h`.
- Generated-header consistency checks that each `*_SHIFT`/`*_MASK` pair matches the field width, that every register has a matching address in `dcn_2_1_0_offset.h`, and that repeated OTG3/OTG4/OTG5 layouts stay aligned where the hardware spec expects them to.
- Modeset tests over multiple timing modes, including high-resolution, high-refresh, low-refresh, interlaced, DSC, ODM/combine, and blanking-sensitive modes.
- Vblank, vline, page-flip, and vupdate interrupt tests that verify events are enabled, delivered, acknowledged, and cleared on all applicable pipes, especially OTG4 and OTG5.
- Dynamic refresh-rate and VRR tests that exercise min/max/mid vtotal programming, vtotal event paths, and last-used-vtotal readback where the full register block is present.
- CRC validation through IGT-style display CRC tests, including one-shot and continuous CRC, windowed CRC, DSC mode, split/combine data streams, and blank-only or active-frame captures.
- Suspend/resume, display off/on, hotplug, and runtime power-management tests that confirm OTG timing, update locks, global sync, interrupt masks, and clock/reset state are restored correctly.
- Multi-display synchronization tests for GSL, master update locks, vupdate keepout windows, and synchronized flips across adjacent timing generators.

Regression symptoms from bad constants include black screen, unstable refresh, missed vblank or vline events, stuck page flips, cursor or plane updates that never latch, visible tearing during atomic updates, failed display CRC tests, broken DSC timing, incorrect VRR behavior, interrupt storms, or failures limited to later pipes corresponding to OTG3, OTG4, or OTG5.

## Cross-Chunk Notes

This is a generated constants-only chunk. It starts in the middle of the OTG3 register family; earlier OTG3 timing fields such as `OTG3_OTG_H_TOTAL`, `OTG3_OTG_H_BLANK_START_END`, and `OTG3_OTG_H_SYNC_A` are owned by the previous chunk. It ends at line 32383 in the middle of `OTG5_OTG_RANGE_TIMING_INT_STATUS`; the remaining masks for that register and the following OTG5 DRR/request/DSC/pipe-update/spare registers belong to the next chunk.

The final per-file document should merge this slice with adjacent chunks before making whole-file claims about DCN 2.1 OTG coverage.

### subset-b-001669: lines 32384-34755

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 32384-34755

## Scope

This chunk is part of the generated AMD DCN 2.1.0 ASIC register mask/shift header. It covers lines 32384-34755 and exports bit-position and bit-mask constants for the tail of OTG5 timing, OPTC misc and performance monitor registers, DIO I2C, DIG soft reset and clock/power/interrupt registers, HPD0-HPD4, DIO performance monitor 18, and DP AUX0-AUX3. The slice contains 2,178 `#define` entries: 1,091 `__SHIFT` constants and 1,087 `_MASK` constants. It has no C functions, structs, enums, or executable code; its API is the generated macro namespace consumed by AMDGPU display register helper tables.

The chunk starts mid-register with the remaining `OTG5_OTG_RANGE_TIMING_INT_STATUS` masks and ends mid-register at `DP_AUX3_AUX_SW_STATUS`, so whole-file reconciliation must merge it with adjacent chunks for complete register-family coverage.

## Purpose

The purpose of this chunk is to bind symbolic DCN 2.1.0 display register fields to exact hardware bit layouts. Driver code uses these constants through register-field tables and generic access helpers instead of open-coded masks and shifts.

Major hardware domains represented here are:

- OTG5 timing state: dynamic refresh-rate tracking, DSC start position, request mode, range-timing interrupt status, pipe update pending/taken/clear bits, and vupdate keepout status.
- OPTC misc state: display-writeback source selection, global swap-lock ready/timing source selection, OPTC clock gating/test clock controls, ODM memory power controls for memories 0-11, vblank/unassigned memory power modes, and memory power status.
- DC performance monitors 17 and 18: event selection, counter modes, run-enable selectors, counter state, counter interrupt status/ack, high/low value readback, and counter-off interrupt controls.
- DIO I2C engine: software transaction control, arbitration between software and DMCU, interrupt status/ack/mask bits, DDC1-DDC5 hardware status, per-DDC speed/setup, four transaction descriptors, data FIFO/index access, EDID detect, and read-request interrupts for DDC1-DDC6/DDCVGA.
- DIO global controls: DIG front-end/back-end soft resets for DIGA-DIGG, AFMT/DME memory power status, clock gate controls for AFMT and TMDS symbol clocks, HDMI RX status timer interrupt configuration, PSP interrupt message/status, and generic interrupt message/status.
- HPD0-HPD4: hotplug sense and delayed-sense status, RX interrupt status, HPD interrupt ack/polarity/enable, connection/RX timers, fast-train delays/enables, and connect/disconnect toggle filter delays.
- DP AUX0-AUX3: AUX enable/reset, HPD selection, arbitration with software/DMCU, software transaction trigger and status, interrupt ack/masks, native and link-service data/status, DPHY TX/RX timing/status, GTC sync control/error/status for AUX0-AUX2, and AUX PHY wake controls.

## Important API Surface

The exported surface follows the generated convention:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

Important macro families in this chunk include:

- `OTG5_OTG_PIPE_UPDATE_STATUS__OTG_FLIP_PENDING`, `OTG5_OTG_PIPE_UPDATE_STATUS__OTG_DC_REG_UPDATE_TAKEN`, and `OTG5_OTG_PIPE_UPDATE_STATUS__OTG_CURSOR_UPDATE_TAKEN_CLEAR` for pipe update sequencing.
- `DWB_SOURCE_SELECT__OPTC_DWB*_SOURCE_SELECT`, `GSL_SOURCE_SELECT__GSL*_READY_SOURCE_SEL`, and `OPTC_CLOCK_CONTROL__OPTC_DISPCLK_R_*` for routing and clock state in the OPTC misc block.
- `ODM_MEM_PWR_CTRL*` and `ODM_MEM_PWR_STATUS__ODM_MEM*_PWR_STATE` for controlling and observing ODM memory power state.
- `DC_PERFMON17_*` and `DC_PERFMON18_*` for display performance counter selection, run gating, interrupt acknowledgement, and value readback.
- `DC_I2C_CONTROL`, `DC_I2C_ARBITRATION`, `DC_I2C_INTERRUPT_CONTROL`, `DC_I2C_SW_STATUS`, `DC_I2C_DDC*_SPEED`, `DC_I2C_DDC*_SETUP`, `DC_I2C_TRANSACTION*`, and `DC_I2C_DATA` for DDC/EDID software I2C transactions.
- `DC_I2C_READ_REQUEST_INTERRUPT__DC_I2C_DDC*_READ_REQUEST_*` for hardware read-request interrupt reporting, acknowledgement, masking, and interrupt type.
- `DIG_SOFT_RESET`, `DIO_CLK_CNTL2`, `DIO_CLK_CNTL3`, `DIO_HDMI_RXSTATUS_TIMER_CONTROL`, `DIO_PSP_INTERRUPT_*`, and `DIO_GENERIC_INTERRUPT_*` for global DIO reset, clock/power, and interrupt-message handling.
- `HPD[0-4]_DC_HPD_*` for hotplug detect sense, interrupt control, connection timer programming, fast-train timing, and toggle filtering.
- `DP_AUX[0-3]_AUX_CONTROL`, `AUX_SW_CONTROL`, `AUX_ARB_CONTROL`, `AUX_INTERRUPT_CONTROL`, and `AUX_SW_STATUS` for AUX channel ownership, software transaction launch, status polling, and interrupt acknowledgement.
- `DP_AUX[0-2]_AUX_LS_STATUS`, `AUX_SW_DATA`, `AUX_LS_DATA`, `AUX_DPHY_*`, `AUX_GTC_SYNC_*`, and `AUX_PHY_WAKE_CNTL` for link-service events, AUX data windows, DPHY timing, GTC sync lock/error reporting, and PHY wake handshakes.

These constants are normally consumed through AMD display register access helpers such as `REG_GET`, `REG_UPDATE`, `REG_SET`, symbol-pasting field-list macros, and block-specific table initializers. For DCN 2.1, `drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`, `drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c`, `drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.c`, `drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`, and `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c` include the matching `dcn_2_1_0_offset.h` and `dcn_2_1_0_sh_mask.h` headers.

## Control Flow

There is no local control flow in this header chunk. Runtime behavior is in display driver code that binds these generated constants to register tables and then performs ordered MMIO reads/writes:

- DCN 2.1 resource construction builds link encoder AUX and HPD register arrays with macros such as `DCN2_AUX_REG_LIST(id)` and `HPD_REG_LIST(id)`. Those arrays pair offset-header addresses with the shifts and masks defined here.
- AUX transaction paths in DCE/DCN link encoder and AUX code request ownership through `AUX_ARB_CONTROL`, program software data and transaction byte counts, trigger `AUX_SW_GO`, then poll `AUX_SW_STATUS` or acknowledge `AUX_INTERRUPT_CONTROL`.
- I2C/DDC paths request I2C register ownership through `DC_I2C_ARBITRATION`, configure per-DDC speed/setup and transaction descriptors, write/read `DC_I2C_DATA`, trigger `DC_I2C_GO`, and interpret `DC_I2C_SW_STATUS` error bits such as timeout, aborted, buffer overflow, and NACK.
- HPD handling code reads `DC_HPD_INT_STATUS`/`DC_HPD_SENSE`, programs HPD timers and filters, and acknowledges/enables hotplug and RX interrupts through `DC_HPD_INT_CONTROL`.
- IRQ service code for DCN 2.1 includes this header so generated masks/shifts can back interrupt source setup and status/ack handling.
- Link encoder bring-up and low-level DIO code use DPHY timing, AUX reset, HPD select, and wake bits to prepare AUX channels for DisplayPort link training and sideband transactions.
- Clock, reset, and power-management paths use `DIG_SOFT_RESET`, `DIO_CLK_CNTL*`, `DIO_MEM_PWR_STATUS1`, `ODM_MEM_PWR_CTRL*`, and `ODM_MEM_PWR_STATUS` fields around modeset, encoder reset, and power-gating sequences.
- Performance-monitor control code can select events, start/stop counters, acknowledge counter interrupts, and read low/high counter values through the `DC_PERFMON17_*` and `DC_PERFMON18_*` fields.

Ordering is an implicit hardware contract. For example, ownership request/status fields must be sequenced before writes to shared I2C/AUX registers, sticky interrupt/status bits must be acknowledged without clobbering adjacent enable/mask fields, and reset/wake bits must be paired with polling of done/ack status where hardware requires it.

## State and Persistence

The file stores no software state. Its macros describe memory-mapped hardware state that persists in GPU display blocks while those blocks are powered:

- OTG5 pipe update bits expose live and sticky flip/register/cursor update state, including clear bits that alter hardware status.
- OPTC routing, GSL source selection, clock controls, and ODM memory power fields persist as active display pipe configuration.
- Performance monitor registers hold selected events, run/stop mode, counter state, interrupt state, and counter values until disabled, reset, overwritten, or power-cycled.
- I2C/DDC registers hold transaction descriptors, selected DDC line, speed/setup timing, data index/window state, EDID detect settings, and software/hardware status bits.
- HPD registers hold debounce/timer/filter configuration and live hotplug/RX interrupt state for each HPD instance.
- AUX registers hold reset/enable/HPD selection, transaction byte count and data window state, arbitration ownership, link-service update state, DPHY timing calibration, GTC sync thresholds/state, and PHY wake handshakes.
- DIO reset, clock gate, memory power, PSP, and generic interrupt registers affect shared display I/O state across encoders.

Wrong constants can leave hardware in a bad programmed state until a modeset, block reset, suspend/resume, GPU reset, or full driver reinitialization restores known-good register contents.

## Dependencies and Integration Points

This chunk depends on the matching `dcn_2_1_0_offset.h` register addresses and on AMD display helper macros that paste register and field names into `__SHIFT` and `_MASK` identifiers. The masks are only correct for DCN 2.1.0 hardware; same-named fields in DCN 2.0, DCN 3.x, DCN 4.x, and DCE headers can differ.

Key integration points include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`, where DCN 2.1 resource tables include this header and construct AUX/HPD register arrays for five link instances.
- `drivers/gpu/drm/amd/display/dc/dce/dce_aux.h` and `dce_aux.c`, where AUX field-list structures and ownership/polling helpers consume `DP_AUX0_*` style masks/shifts through symbol-pasting macros.
- `drivers/gpu/drm/amd/display/dc/dce/dce_i2c_hw.h` and `dce_i2c_hw.c`, where I2C field-list structures and software transaction helpers consume `DC_I2C_*` masks/shifts for arbitration, setup, transaction, data, and status handling.
- `drivers/gpu/drm/amd/display/dc/dio/dcn20/dcn20_link_encoder.c` and related DCN link encoder code, where AUX DPHY timing and AUX control fields are programmed during encoder initialization and DisplayPort AUX setup.
- `drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c` and `hw_translate_dcn21.c`, where HPD/DDC GPIO abstractions bind DCN 2.1 register metadata to generic GPIO services.
- `drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`, which includes the generated DCN 2.1 offset and mask headers for interrupt source integration.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`, which includes this header for DMUB-facing DCN 2.1 register access.

## Risks

- A wrong shift or mask silently targets the wrong hardware bit. Highest-risk fields here are ownership/arbitration bits, transaction launch bits, reset bits, interrupt acknowledgements, and packed timing fields.
- The I2C and AUX engines have shared ownership with DMCU/firmware paths. Incorrect `*_USE_*_REQ`, `*_DONE_USING_*`, or `*_REG_RW_CNTL_STATUS` fields can deadlock register access or race firmware ownership.
- Status, mask, ack, and enable bits are often packed into the same register. A bad read-modify-write mask can drop hotplug, AUX, I2C, PSP, generic, or performance counter interrupts, or repeatedly retrigger stale sticky status.
- HPD0-HPD4 and DP_AUX0-DP_AUX3 are near-duplicate register families. Instance drift can affect only one connector, making regressions appear as board-, port-, or monitor-specific failures.
- DDC speed/setup and AUX DPHY timing fields are narrow and hardware-sensitive. Bit mistakes can cause EDID read failures, AUX timeouts, link training failures, or intermittent DisplayPort sideband errors rather than immediate compile failures.
- `DP_AUX3` is truncated in this chunk after the first `AUX_SW_STATUS` shifts, while AUX0-AUX2 have complete LS/DPHY/GTC/wake coverage in this slice. Final reporting must avoid treating this chunk alone as the complete AUX3 definition.
- Performance monitor fields expose diagnostic counters, so most mask errors are unlikely to break normal display bring-up but can invalidate profiling, interrupt-on-threshold behavior, or debug telemetry.
- Generated headers are not usually unit-tested directly. Many errors surface only when a specific DCN generation, connector instance, interrupt path, low-power path, or hardware transaction is exercised.

## Test Signals

Useful validation signals for changes to this chunk are:

- AMDGPU display build coverage for DCN 2.1 paths, including `dcn21_resource.c`, `irq_service_dcn21.c`, GPIO translation/factory code, DCE I2C, DCE AUX, link encoder code, and DMUB DCN21 code.
- Static comparison against the vendor register database and the adjacent `dcn_2_1_0_offset.h`, verifying that each field's shift and mask match the correct register address and that repeated HPD/AUX/DDC instance families stay intentionally consistent.
- Display hotplug testing across HPD0-HPD4, including connect/disconnect debounce, delayed sense, RX interrupt generation, interrupt acknowledgement, and fast-train timing where supported.
- EDID/DDC tests across all wired DDC instances, covering normal reads, NACK handling, timeout handling, abort paths, read-request interrupts, and DDC speed/setup programming.
- DisplayPort AUX tests across AUX0-AUX3, including software AUX reads/writes, link-service update status, HPD disconnect during AUX, timeout/overflow/error reporting, AUX reset, and AUX PHY wake.
- Modeset and DisplayPort link-training tests that exercise AUX DPHY timing and HPD/AUX routing, especially on multi-connector systems.
- Suspend/resume, runtime power-management, and low-power display tests that observe DIG/AFMT/DME/ODM memory power status and verify DIO clocks/resets recover correctly.
- Performance monitor smoke tests or debugfs/tooling checks that can configure counters, observe active/run state, read low/high counter values, and clear counter interrupts.

## Chunk Notes

This chunk is generated register metadata, not functional logic. The main research value is identifying the hardware contracts covered by the constants: OTG5 update/timing status, OPTC routing and memory power, DIO I2C/HPD/AUX transaction machinery, DIO reset/clock/interrupt controls, and DC performance monitoring. The final merged report should connect this slice with adjacent chunks to provide complete coverage of `dcn_2_1_0_sh_mask.h`, especially for the partial `OTG5_OTG_RANGE_TIMING_INT_STATUS` start and partial `DP_AUX3_AUX_SW_STATUS` end.

### subset-b-001670: lines 34756-37152

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 34756-37152

## Scope

This chunk is a generated AMDGPU DCN 2.1.0 register shift/mask header segment. It contains preprocessor constants only: no functions, structs, enums, storage objects, or executable control flow. The exported surface is the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` namespace used by AMD display register helper macros to insert, extract, acknowledge, or decode fields in DCN 2.1.0 MMIO registers.

The range covers 2,397 source lines with 2,170 `#define` entries, 1,083 shift macros, 1,087 mask macros, and 219 register/address-block comments. It starts in the middle of `DP_AUX3_AUX_SW_STATUS`, completes the `DP_AUX3` AUX register group, defines the full `DP_AUX4` AUX block, then covers `DIG0`, `DP0`, and the beginning of `DIG1` display-output blocks.

## Purpose

The chunk provides exact bit positions and already-shifted masks for DCN 2.1.0 display I/O hardware fields. Higher-level AMD display code can use stable symbolic field names while this generated header supplies ASIC-specific bit layout.

Major hardware areas covered here are:

- `DP_AUX3_*` and `DP_AUX4_*`: DisplayPort AUX engine status, low-speed status, data FIFOs, DPHY TX/RX timing controls, DPHY status, GTC synchronization, interrupt/ack/mask fields, arbitration, and PHY wake handshakes.
- `DIG0_*`: digital front-end/back-end controls, output CRC/test/random pattern generation, FIFO status, HDMI packet generation, HDMI infoframes, HDMI ACR/audio control, AFMT audio packet and channel-status metadata, TMDS control character generation, lane enable, VBI packet scheduling, data-bypass controls, and forced DIG disable.
- `DP0_*`: DisplayPort link controls, pixel/MSA configuration, video stream timing and M/N values, DPHY training/scrambling/CRC/PRBS, secondary-data packet scheduling, audio M/N and timestamp programming, MST/MSE slot allocation, MSO and DSC control, metadata transmission, VBID/misc fields, ALPM control, and DisplayPort debug-bypass controls.
- `DIG1_*`: the beginning of the second digital display instance, structurally mirroring the `DIG0` front-end, FIFO, HDMI, generic-packet, GC, AFMT audio-packet, and ISRC metadata fields until the chunk ends inside `DIG1_AFMT_ISRC1_3`.

Although the repository path is under `sources/distributed-fs/ceph-client`, this source is AMDGPU display hardware metadata. It has no Ceph filesystem, distributed storage, network protocol, or userspace persistence behavior.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The contract is the generated macro naming scheme and the pairing of field shifts with masks:

- `*_SHIFT` constants hold the field low-bit position.
- `*_MASK` constants hold the field mask already shifted into register position.
- Register-heading comments such as `//DP0_DP_SEC_CNTL2` group the macros by hardware register.
- Address-block comments such as `// addressBlock: dce_dc_dio_dp_aux4_dispdec`, `// addressBlock: dce_dc_dio_dig0_dispdec`, `// addressBlock: dce_dc_dio_dp0_dispdec`, and `// addressBlock: dce_dc_dio_dig1_dispdec` mark generated register windows.

Representative AUX macros include `DP_AUX4_AUX_CONTROL__AUX_EN_MASK`, `DP_AUX4_AUX_SW_CONTROL__AUX_SW_START_DELAY_MASK`, `DP_AUX4_AUX_INTERRUPT_CONTROL__AUX_SW_DONE_ACK_MASK`, `DP_AUX4_AUX_SW_STATUS__AUX_SW_REPLY_BYTE_COUNT_MASK`, `DP_AUX4_AUX_DPHY_TX_REF_CONTROL__AUX_TX_REF_DIV_MASK`, `DP_AUX4_AUX_DPHY_RX_CONTROL0__AUX_RX_DETECTION_THRESHOLD_MASK`, `DP_AUX4_AUX_GTC_SYNC_CONTROLLER_STATUS__AUX_GTC_SYNC_CRITICAL_ERR_OCCURRED_ACK_MASK`, and `DP_AUX4_AUX_PHY_WAKE_CNTL__DP_AUX_PHY_WAKE_ACK_MASK`. The `DP_AUX3` group uses the same layout for AUX instance 3 but this chunk begins after that register group's first heading and first several shift definitions.

Representative DIG/HDMI/AFMT macros include `DIG0_DIG_FE_CNTL__DIG_SOURCE_SELECT_MASK`, `DIG0_DIG_OUTPUT_CRC_CNTL__DIG_OUTPUT_CRC_CONT_EN_MASK`, `DIG0_DIG_FIFO_STATUS__DIG_FIFO_OVERFLOW_MASK`, `DIG0_HDMI_CONTROL__HDMI_DATA_SCRAMBLE_EN_MASK`, `DIG0_HDMI_ACR_PACKET_CONTROL__HDMI_ACR_AUTO_SEND_MASK`, `DIG0_HDMI_GENERIC_PACKET_CONTROL0__HDMI_GENERIC7_CONT_MASK`, `DIG0_AFMT_AUDIO_PACKET_CONTROL2__AFMT_AUDIO_CHANNEL_ENABLE_MASK`, `DIG0_AFMT_60958_0__AFMT_60958_CS_CHANNEL_NUMBER_L_MASK`, `DIG0_AFMT_AUDIO_PACKET_CONTROL__AFMT_60958_CS_UPDATE_MASK`, `DIG0_TMDS_DCBALANCER_CONTROL__TMDS_DCBALANCER_EN_MASK`, and `DIG0_FORCE_DIG_DISABLE__FORCE_DIG_DISABLE_MASK`. `DIG1` repeats the same generated families for the second DIG instance, but this range only covers the initial part of the instance.

Representative DP0 macros include `DP0_DP_LINK_CNTL__DP_LINK_TRAINING_COMPLETE_MASK`, `DP0_DP_PIXEL_FORMAT__DP_PIXEL_ENCODING_MASK`, `DP0_DP_VID_STREAM_CNTL__DP_VID_STREAM_ENABLE_MASK`, `DP0_DP_STEER_FIFO__DP_STEER_FIFO_RESET_MASK`, `DP0_DP_DPHY_CNTL__DPHY_BS_SR_SWAP_MASK`, `DP0_DP_DPHY_FAST_TRAINING__DPHY_RX_FAST_TRAINING_CAPABLE_MASK`, `DP0_DP_SEC_CNTL__DP_SEC_STREAM_ENABLE_MASK`, `DP0_DP_SEC_CNTL2__DP_SEC_GSP4_SEND_MASK`, `DP0_DP_MSE_SAT0__DP_MSE_SAT_SRC0_MASK`, `DP0_DP_MSO_CNTL__DP_MSO_ENABLE_MASK`, `DP0_DP_DSC_CNTL__DP_DSC_ENABLE_MASK`, and `DP0_DP_ALPM_CNTL__DP_ALPM_ENABLE_MASK`.

## Control Flow

This header has no local runtime control flow. Runtime behavior is created by consumers that include `dcn_2_1_0_offset.h` with this shift/mask header, assemble register tables, and then access MMIO through AMD display helper macros.

A typical flow is:

1. DCN21 resource, IRQ, GPIO, DMUB, AUX/DDC, link-encoder, stream-encoder, or audio code includes the generated offset and shift/mask headers.
2. Generation-specific register lists use macro-pasting helpers such as `REG_OFFSET`, `SF`, `SRI`, `FD_MASK`, `FD_SHIFT`, and resource/IRQ register-table macros.
3. Driver code issues `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, or equivalent helper calls.
4. The helpers combine the offset header's register addresses with this file's masks and shifts to read status, program configuration, clear sticky/ack fields, or build packed register values.

Control-sensitive flows represented by this chunk include AUX transaction completion and error decoding, AUX low-speed updates, HPD disconnect detection during AUX operations, AUX GTC synchronization lock/error handling, HDMI packet scheduling, HDMI/AFMT audio infoframe and channel-status programming, TMDS symbol/control-character generation, DisplayPort link training and video-stream enablement, secondary-data packet insertion, MST slot allocation, DSC enablement, ALPM entry/exit, and interrupt/status acknowledgement.

The macros do not encode ordering, access type, volatility, reset value, read-only/write-only semantics, or write-one-to-clear behavior. Those constraints remain in the calling code and hardware programming sequences.

## State And Persistence Behavior

The file itself stores no software state and performs no persistence. It describes hardware register fields whose state persists according to DCN/DIO register semantics until changed by software, hardware state machines, power management, modeset reset, or GPU reset.

State represented in this range includes:

- AUX engine state: request/done bits, reply byte counts, timeout state, overflow/partial-byte/error flags, non-AUX mode detection, low-speed update state, AUX data byte/index windows, PHY TX/RX timing, GTC lock acquisition and maintenance state, GTC error counters/status, and PHY wake pending/ack state.
- DIG and HDMI state: source selection, front-end enable, CRC/test-pattern controls, FIFO underflow/overflow indicators, metadata and generic-packet send/continuous/line-reference controls, HDMI scramble/deep-color/AVMUTE state, ACR selection, null/GC/ISRC/infoframe scheduling, and HDMI/AFMT audio packet controls.
- AFMT audio metadata state: audio layout/channel enable, DP audio stream ID, ISRC bytes, MPEG/generic packet payload bytes, audio infoframe bytes, IEC 60958 channel-status override bytes, audio CRC control/result, ramp controls, AFMT status, VBI packet insertion, and audio source control.
- TMDS/DIG back-end state: DIG back-end enable, TMDS output enable, control-character patterns, stereo sync selection, sync-character patterns, CTL bit generation, DC balancer controls, lane enable, and forced-disable state.
- DP0 link state: link training complete, pixel format, MSA colorimetry/misc/timing fields, stream enable, video timing, link framing, DPHY lane/symbol/training/scrambling/CRC controls, secondary stream/audio packet controls, MST/MSE allocation state, MSO controls, DSC enablement, metadata transmission, DSC bytes-per-pixel, and ALPM state.

Some fields are configuration latches, some are live status readbacks, and some are interrupt/status/ack/mask fields. Incorrect writes can persist through normal display operation until a modeset, hotplug cycle, suspend/resume path, power-gate cycle, or full GPU reset reinitializes the affected block.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`, which supplies matching register offsets. This file supplies bit layouts within those registers. The constants also depend on AMD display helper conventions that paste register and field names into `*_MASK` and `__SHIFT` identifiers.

Direct include sites visible in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`, which includes the DCN 2.1.0 headers while building Renoir/DCN21 display resources such as DIO, AUX/DDC, GPIO, stream encoders, clocks, IRQs, and related register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`, which includes the headers for DCN21 interrupt source mapping and register mask definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.c`, which include the generated DCN21 headers for GPIO/AUX/HPD register object construction and translation.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`, which includes the same offset/mask headers while assembling DMUB service register metadata.

Functional integration points are broader than the include list. AUX fields feed DCE/DCN AUX and DDC operations, HPD sideband handling, DisplayPort link training, EDID/DPCD transactions, and GTC synchronization. DIG/HDMI/AFMT fields feed stream encoder setup, HDMI/DP audio programming, infoframe construction, metadata insertion, CRC/test-pattern diagnostics, and TMDS output programming. DP0 fields feed link encoder and stream encoder code for DP video, MST, secondary-data packets, DSC, MSO, and ALPM.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A wrong shift or mask can compile cleanly but target the wrong bit, truncate a field, leave stale bits set after a read/modify/write, miss a status condition, or acknowledge the wrong event.

AUX fields are connector-critical. Bad `DP_AUX3` or `DP_AUX4` status, data, interrupt, DPHY, GTC, or PHY wake constants can break EDID/DPCD reads, DisplayPort link training, HPD-disconnect handling during transactions, timeout/error classification, link-service updates, AUX-GTC synchronization, or power-management wake handshakes. Some failures will be board-, connector-, cable-, or resume-specific.

DIG/HDMI/AFMT fields are protocol-visible. Incorrect packet-control, ACR, generic-packet, infoframe, ISRC, MPEG, audio-channel, IEC 60958, TMDS, deep-color, or scramble masks can produce missing HDMI/DP audio, wrong channel count/sample-rate metadata, malformed infoframes, no AVMUTE, invalid TMDS control symbols, broken compliance-test patterns, or audio behavior that regresses only after hotplug or modeset.

DP0 fields affect link bring-up and display correctness. Bad DPHY/training/scramble/CRC, MSA, video timing, M/N, secondary-data, MST/MSE, DSC, MSO, metadata, or ALPM masks can cause link-training failures, black screens, incorrect colorimetry, unstable MST allocation, missing audio secondary packets, DSC corruption, or low-power link-management failures.

The repeated generated instances create copy/generation hazards. `DP_AUX3` and `DP_AUX4` are structurally similar, and `DIG0`/`DIG1` should align for the covered registers. One-off differences should be treated as suspicious unless the ASIC register database requires them.

Chunk boundaries matter. The range starts after the `DP_AUX3_AUX_SW_STATUS` heading and first several shift definitions, so the full register group is split with the previous chunk. The range ends inside `DIG1_AFMT_ISRC1_3`, so the rest of the `DIG1` instance belongs to a later chunk. The final merge lane should avoid drawing whole-file conclusions from this artificial slice alone.

## Test Signals

Useful validation signals are generated-header consistency checks plus DCN21 display, connector, AUX, DP, HDMI, and audio behavior:

- Build coverage for DCN21 resource, IRQ, GPIO, DMUB, AUX/DDC, link, stream-encoder, and audio paths that include `dcn_2_1_0_sh_mask.h`.
- Generated-register validation that every field in this chunk has a matching register definition in `dcn_2_1_0_offset.h`, masks match their shifts and field widths, and repeated `DP_AUX3`/`DP_AUX4` and `DIG0`/`DIG1` layouts remain intentionally aligned.
- AUX/DDC tests for EDID reads, DPCD reads/writes, link-service updates, HPD-disconnect during transactions, timeout/error reporting, PHY wake behavior, and suspend/resume reinitialization.
- DisplayPort tests for link training, MSA timing/colorimetry, stream enable/disable, scrambling, PRBS/CRC diagnostics, audio secondary packets, MST/MSE slot allocation, DSC operation, MSO operation, metadata transmission, and ALPM transitions.
- HDMI/DVI tests for scrambling, deep color, TMDS control characters, AVMUTE, ACR packet generation, generic-packet scheduling, infoframes, audio channel layouts, ISRC/MPEG/generic payload handling, and hotplug/modeset recovery.
- Interrupt/status tests that verify AUX done/error acks, GTC sync errors, FIFO underflow/overflow indicators, HDMI error status, DP video interrupts, and audio-format/status updates report and clear as expected.

Regression symptoms from bad constants include failed EDID/AUX transactions, missing HPD-related AUX aborts, black screen after link training, incorrect colorimetry or timing, no HDMI/DP audio, wrong audio channel metadata, malformed infoframes, stuck AUX/GTC/DP/HDMI status bits, MST allocation failures, DSC corruption, or failures limited to AUX4, DP0, DIG0, or DIG1 instance-specific paths.

## Cross-Chunk Notes

This is a generated constants-only chunk of `dcn_2_1_0_sh_mask.h`. Adjacent chunks own the beginning of `DP_AUX3_AUX_SW_STATUS` and the continuation of `DIG1` after `DIG1_AFMT_ISRC1_3`. The later per-file report should merge this with neighboring chunks to describe the complete DCN 2.1.0 register layout contract rather than treating this line range as an independently designed module.

### subset-b-001671: lines 37153-39580

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 37153-39580

## Scope

This chunk is a generated constants-only slice of AMDGPU's DCN 2.1.0 register shift/mask header. It covers lines 37153-39580 of `dcn_2_1_0_sh_mask.h` and contains 2,164 `#define` entries: 1,081 `__SHIFT` constants and 1,083 `_MASK` constants, grouped by 258 register/address-block comments. There are no functions, structs, enums, variables, branches, loops, or local storage.

The range starts in the middle of the `DIG1` display encoder audio/HDMI block at `DIG1_AFMT_ISRC1_4`, completes many `DIG1` HDMI/audio/TMDS/DIG backend field definitions, covers the full visible `DP1` DisplayPort encoder register group, covers the full visible `DIG2` HDMI/audio/TMDS/DIG backend group, and begins the `DP2` DisplayPort encoder group through `DP2_DP_SEC_FRAMING1`. The logical hardware blocks are split by artificial chunk boundaries, so adjacent chunks are needed for the preceding `DIG1` fields and the remaining `DP2` fields.

Although this repository path is under `ceph-client`, this file is AMD display hardware metadata. It has no Ceph filesystem protocol behavior and no distributed filesystem persistence model.

## Purpose

The purpose of this range is to publish exact bit positions and already-positioned masks for DCN 2.1.0 digital display encoder registers. Runtime display code includes this header together with the matching register-address header, `dcn_2_1_0_offset.h`, then uses AMD display register helpers to encode and decode packed MMIO fields without hard-coding bit values in functional code.

The represented hardware areas are:

- Tail `DIG1` AFMT/HDMI audio packet state: ISRC bytes, generic HDMI packet line control, HDMI double-buffer control, metadata engine control, MPEG infoframe bytes, generic packet header/payload bytes, ACR N/CTS values for 32/44.1/48 kHz families, ACR status, audio infoframe bytes, IEC 60958 channel-status fields, audio CRC controls/results, audio ramp generator controls, AFMT status, audio/VBI packet control, infoframe control, and audio source selection.
- Tail `DIG1` digital encoder/TMDS state: backend routing and enablement, TMDS sync/control characters, feedback, stereo-sync selection, DC balancer controls, generated TMDS control bits, DIG version/lane enablement, AFMT control, VBI packet control, generic packet control, and force-disable.
- `DP1` DisplayPort state under `dce_dc_dio_dp1_dispdec`: link status/training, pixel format, MSA colorimetry/misc/timing, lane configuration, video stream enable and timing, link framing, HBR2 eye pattern/test symbols, DPHY training/8b10b/PRBS/scrambler/CRC/FEC/fast-training controls, secondary-data-packet controls, audio M/N values, MST/MSE slot allocation and status, MSO controls, DSC mode and bytes-per-pixel, metadata transmission, double buffering, VBID misc, and ALPM link sleep/standby controls.
- `DIG2` digital encoder state under `dce_dc_dio_dig2_dispdec`: the same family of front-end, output CRC, HDMI, AFMT/audio/infoframe, backend, TMDS, lane, VBI, generic packet, and force-disable fields for digital encoder instance 2.
- Beginning `DP2` DisplayPort state under `dce_dc_dio_dp2_dispdec`: link status/training, pixel format/MSA/video-stream setup, DPHY training/test/CRC/FEC/fast-training fields, and initial secondary packet framing fields through `DP2_DP_SEC_FRAMING1`.

## Important API Surface

There are no callable APIs in this chunk. The exported surface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask already shifted into register position.
- Register comments such as `//DP1_DP_SEC_CNTL` or `//DIG2_HDMI_CONTROL` group fields by hardware register.
- Address-block comments identify instance windows: `dce_dc_dio_dp1_dispdec`, `dce_dc_dio_dig2_dispdec`, and `dce_dc_dio_dp2_dispdec`.

Representative `DIG1`/`DIG2` audio and HDMI macros include `DIG1_HDMI_DB_CONTROL__HDMI_DB_PENDING_MASK`, `DIG1_DME_CONTROL__METADATA_ENGINE_EN_MASK`, `DIG1_AFMT_GENERIC_HDR__AFMT_GENERIC_HB0_MASK`, `DIG1_HDMI_ACR_32_0__HDMI_ACR_CTS_32_MASK`, `DIG1_AFMT_60958_0__AFMT_60958_CS_CHANNEL_NUMBER_L_MASK`, `DIG1_AFMT_AUDIO_PACKET_CONTROL__AFMT_AUDIO_SAMPLE_SEND_MASK`, `DIG2_HDMI_CONTROL__HDMI_DATA_SCRAMBLE_EN_MASK`, `DIG2_AFMT_AUDIO_PACKET_CONTROL2__AFMT_AUDIO_CHANNEL_ENABLE_MASK`, `DIG2_AFMT_STATUS__AFMT_AUDIO_FIFO_OVERFLOW_MASK`, and `DIG2_DIG_BE_CNTL__DIG_MODE_MASK`.

Representative TMDS/DIG backend macros include `DIG1_DIG_BE_CNTL__DIG_FE_SOURCE_SELECT_MASK`, `DIG1_DIG_BE_EN_CNTL__DIG_BE_EN_MASK`, `DIG1_TMDS_SYNC_CHAR_PATTERN_0_1__TMDS_SYNC_CHAR_PATTERN0_MASK`, `DIG1_TMDS_DCBALANCER_CONTROL__TMDS_DCBALANCER_EN_MASK`, `DIG1_TMDS_CTL0_1_GEN_CNTL__TMDS_CTL0_DATA_SEL_MASK`, `DIG2_DIG_FE_CNTL__DIG_SOURCE_SELECT_MASK`, `DIG2_TMDS_CTL_BITS__TMDS_CTL0_MASK`, and `DIG2_FORCE_DIG_DISABLE__FORCE_DIG_DISABLE_MASK`.

Representative DisplayPort macros include `DP1_DP_LINK_CNTL__DP_LINK_TRAINING_COMPLETE_MASK`, `DP1_DP_PIXEL_FORMAT__DP_PIXEL_ENCODING_MASK`, `DP1_DP_CONFIG__DP_UDI_LANES_MASK`, `DP1_DP_VID_STREAM_CNTL__DP_VID_STREAM_ENABLE_MASK`, `DP1_DP_DPHY_CNTL__DPHY_FEC_EN_MASK`, `DP1_DP_DPHY_FAST_TRAINING_STATUS__DPHY_FAST_TRAINING_COMPLETE_OCCURRED_MASK`, `DP1_DP_SEC_CNTL__DP_SEC_GSP0_ENABLE_MASK`, `DP1_DP_MSE_SAT0__DP_MSE_SAT_SLOT_COUNT0_MASK`, `DP1_DP_DSC_CNTL__DP_DSC_MODE_MASK`, `DP1_DP_ALPM_CNTL__DP_ML_PHY_SLEEP_SEND_MASK`, `DP2_DP_LINK_CNTL__DP_EMBEDDED_PANEL_MODE_MASK`, `DP2_DP_DPHY_CNTL__DPHY_FEC_ACTIVE_STATUS_MASK`, and `DP2_DP_SEC_FRAMING1__DP_SEC_FRAME_START_LOCATION_MASK`.

Consumers generally do not treat these long identifiers as business logic. DCN code expands them through register-list and field-list macros, then passes the resulting addresses, shifts, and masks to helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_WAIT`, and related AMD display MMIO wrappers.

## Control Flow

This header has no local runtime control flow. The practical control flow is in the display driver that consumes the constants:

1. DCN 2.1 code includes `dcn_2_1_0_offset.h` for register addresses and this file for field layout.
2. Resource, GPIO, IRQ, DMUB, link encoder, audio, and stream-encoder setup code builds tables or inline helper arguments from the generated macro names.
3. Higher-level display code performs modeset, link training, stream enablement, audio setup, metadata packet programming, hotplug handling, or power-management operations.
4. Register helpers combine the target register address with the corresponding `__SHIFT` and `_MASK` values from this header to update or read packed hardware fields.

The control-sensitive flows represented by this chunk include HDMI scrambling/deep-color setup, HDMI/DP audio packet enablement, infoframe and generic packet scheduling, audio clock-regeneration programming, metadata double-buffer handoff, TMDS control-symbol generation, DisplayPort link training and video-stream enablement, secondary data packet transmission, MST slot allocation, DSC activation, DP CRC diagnostics, FEC and fast-training state, and ALPM sleep/standby requests.

Ordering, access type, volatility, reset values, and write-one-to-clear behavior are not encoded here. Callers must know when fields are status-only, sticky interrupt state, self-clearing, double-buffered, safe only while a stream is disabled, or synchronized to vblank/link-training hardware.

## State And Persistence Behavior

The file itself stores no software state and performs no persistence. It describes hardware register state that persists according to DCN 2.1.0 display-engine rules until software reprograms the block, hardware updates status bits, display power management resets the block, or the GPU resets.

State represented in this range includes:

- HDMI/audio payload state: ISRC/UPC bytes, MPEG infoframe bytes, generic packet headers and payload bytes, generic packet target lines, VBI/audio packet controls, ACR CTS/N values, audio infoframe bytes, IEC 60958 channel status, ramp generator values, CRC controls/results, audio FIFO/status flags, HBR state, and audio source selection.
- Metadata and double-buffer state: HDMI DB pending/taken/lock/disable fields, vupdate DB state, metadata engine enablement, requestor ID, stream type, and metadata DB pending/taken/disable fields.
- DIG/TMDS routing and electrical-symbol state: FE source selection, stereo-sync selection, start/bypass/input-pixel selection, backend mode, dual-link/swap/RB switch, HPD selection, symbol clock enablement, lane enablement, TMDS control characters, sync patterns, generated control bits, feedback paths, DC balancer controls, and force-disable state.
- DisplayPort link/video state: link training complete/status, embedded panel mode, pixel encoding/depth/combine, lane count, MSA colorimetry and timing parameters, video N/M, VBID, stream interrupt controls, link framing, DPHY test symbols, training patterns, 8b10b reset/dispersion, PRBS/scrambler controls, CRC configuration/readback, MST CRC phase status, FEC, fast training, and stream disable acknowledgements.
- DisplayPort secondary packet and MST/DSC state: ASP/ATP/AIP/ACM/GSP/MPG enable bits, ISRC and GSP send/line/deadline state, audio M/N values and readbacks, secondary packet timestamp/coding fields, MSE rate and slot allocation tables/status, MSO controls, DSC mode/slice width/bytes-per-pixel, metadata transmission, and ALPM sleep/standby pending bits.

Some fields are programmed configuration latches, some are live readbacks, some are interrupt/status acknowledgements, and some are update-pending indicators. A wrong mask or shift can therefore create state that survives until the next modeset, audio reconfiguration, hotplug sequence, suspend/resume cycle, or GPU reset.

## Dependencies And Integration Points

The direct companion for this file is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`

Direct include sites visible in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.c`

For this specific chunk, the strongest functional integration is the DCN stream/link encoder and audio machinery. Shared display code uses the generated instance fields to program HDMI and DisplayPort encoders during stream creation, audio endpoint setup, DP link training, infoframe/metadata packet updates, MST scheduling, DSC enablement, and low-power link transitions. IRQ and DMUB code may also consume related status/ack/mask fields when reporting display events or coordinating firmware-controlled display paths.

The instance suffixes are part of the contract. `DIG1` and `DIG2` are separate digital encoder instances, and `DP1` and `DP2` are separate DisplayPort encoder instances with mostly mirrored but not safely interchangeable field names. The matching `*_offset.h` entries, such as `mmDIG1_AFMT_ISRC1_4`, `mmDP1_DP_LINK_CNTL`, `mmDIG2_HDMI_CONTROL`, and `mmDP2_DP_SEC_FRAMING1`, provide the address side of the same generated contract.

Cross-generation headers such as `dcn_2_0_1_sh_mask.h`, `dcn_3_*_sh_mask.h`, and `dcn_4_*_sh_mask.h` contain similarly named fields but may add, remove, or move fields. Generated constants should be compared against the correct DCN 2.1.0 register database rather than copied across generations.

## Risks And Edge Cases

- Silent hardware misprogramming is the main risk. A wrong shift or mask compiles cleanly but can write adjacent bits, fail to acknowledge status, or leave the intended field unchanged.
- Repeated instance blocks are easy to confuse. `DIG1` versus `DIG2` and `DP1` versus `DP2` names often mirror each other, but instance-specific generated values and offsets must stay paired.
- Chunk boundaries are not semantic boundaries. This slice starts after earlier `DIG1_AFMT_ISRC1_*` definitions and ends before completing the `DP2` secondary packet/audio block, so absence of a field in this chunk does not imply absence from the file or hardware.
- HDMI audio and infoframe fields are packed byte-by-byte. Incorrect masks in `AFMT_GENERIC_*`, `AFMT_MPEG_INFO*`, `AFMT_AUDIO_INFO*`, or `AFMT_60958_*` can corrupt only selected payload bytes, making failures dependent on sink EDID, audio layout, or metadata type.
- Double-buffer and metadata fields have sequencing semantics outside this file. Misusing pending/taken/clear/lock/disable masks can drop packet updates, latch old metadata, or race vupdate handoff.
- DisplayPort link and DPHY fields are timing sensitive. Bad training, scrambler, PRBS, 8b10b, FEC, fast-training, or CRC masks can cause intermittent link-training failures, blank screens, or diagnostics that look valid but measure the wrong field.
- Secondary packet and MST/MSE fields combine source IDs, slot counts, line numbers, pending/deadline states, and status readbacks. Incorrect masks can affect only MST, DSC PPS/GSP packets, high-bandwidth audio, or specific stream counts.
- DSC fields are compact and mode-dependent. Incorrect `DP_DSC_MODE`, slice width, or bytes-per-pixel masks can produce stream corruption only when DSC is enabled.
- ALPM fields combine request and pending state. Confusing send and pending masks can wedge link low-power transitions or make power-management tests flaky.
- Status and acknowledge fields often sit next to mask fields with similar names, such as `*_MASK_MASK` generated identifiers. Consumers must distinguish hardware interrupt masks from C preprocessor masks.

## Test Signals

Useful validation for changes to this generated range is mostly build-time, generated-header comparison, and hardware display coverage:

- Build AMDGPU display code that includes `dcn_2_1_0_sh_mask.h`, especially DCN21 resource, IRQ, GPIO translation/factory, and DMUB translation units.
- Compare every shift/mask in this line range against the authoritative DCN 2.1.0 register database and the matching addresses in `dcn_2_1_0_offset.h`.
- Run HDMI modeset coverage across 8/10/12 bpc, deep color, scrambling, audio enable/disable, HBR audio, infoframes, generic packets, VBI packets, and metadata update paths.
- Run DisplayPort SST and MST coverage across link rates, lane counts, training retries, stream enable/disable, MSA timing/colorimetry changes, FEC where supported, fast training where supported, and CRC diagnostics.
- Exercise DSC over DP, including slice-width and bytes-per-pixel programming, and verify sink stability and visual correctness.
- Exercise secondary packet paths: audio M/N readback, ASP/ATP/AIP/ACM/GSP/MPG packet enablement, ISRC/generic packet scheduling, PPS/GSP sends, deadline-missed status, and metadata transmission.
- Stress hotplug, suspend/resume, runtime power transitions, ALPM sleep/standby, and repeated modesets while watching for stuck pending bits, missed acknowledgements, audio FIFO overflow, link retraining loops, and unexpected blanking.
- Use cross-generation diffs only as a sanity signal. Similar fields in other DCN headers help detect obvious generator drift, but DCN 2.1.0-specific generated values remain authoritative for this file.

## Cross-Chunk Notes

This is one large-file chunk from a generated shift/mask header. The final per-file reconciliation should merge it with adjacent `dcn_2_1_0_sh_mask.h` chunks to describe complete `DIG1`, `DP1`, `DIG2`, and `DP2` register families. This chunk should not be treated as a complete logical file report.

### subset-b-001672: lines 39581-42008

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 39581-42008

## Scope

This chunk is a generated AMDGPU DCN 2.1.0 register shift/mask header range. It contains C preprocessor constants only: no functions, structs, enums, objects, executable statements, or local storage. The exported contract is the generated naming convention `REGISTER__FIELD__SHIFT` plus `REGISTER__FIELD_MASK`, where the shift is the field low bit and the mask is already positioned in the MMIO register word.

The assigned range has 2,428 source lines with 2,165 `#define` entries: 1,085 shift constants and 1,080 mask constants. It includes 257 register or address-block comments. The chunk starts in the middle of the `DP2` DisplayPort secondary-data/audio/MST section, contains complete `DIG3` HDMI/audio-formatter and `DP3` DisplayPort blocks, and ends in the early `DIG4` audio formatter block at `DIG4_AFMT_60958_0`.

Major generated groups in this range are:

- `DP2_*`: tail of DisplayPort instance 2, covering secondary-data packet framing, audio M/N, MST/MSE slot allocation, MSA timing, MSO, DSC, double-buffering, metadata, and ALPM controls.
- `DIG3_*`: display encoder/audio formatter instance 3, covering DIG front-end/backend controls, HDMI packet/infoframe paths, audio formatter payload registers, TMDS controls, generic packet update machinery, and forced-DIG-disable control.
- `DP3_*`: DisplayPort instance 3, covering link control, pixel format, MSA, video stream timing and interrupts, DPHY training/scrambler/CRC/PRBS/fast-training, secondary-data/audio packet controls, MST/MSE/MSO, DSC, double-buffering, metadata, and ALPM.
- `DIG4_*`: beginning of display encoder/audio formatter instance 4, mirroring the early DIG/HDMI/AFMT register layout visible for `DIG3` through the first IEC 60958 channel-status register.

## Purpose

The chunk gives DCN 2.1 display code exact bit layouts for Renoir-generation display output hardware. The companion offset header identifies where a register lives; this file identifies which bits in that register carry a named control or status field. Consumers can then build register tables and use helper macros to read, update, or poll hardware fields by logical name instead of hard-coded bit arithmetic.

The `DP2` and `DP3` material models DisplayPort stream generation and link-side packetization. It covers video stream enablement, pixel format, colorimetry, MSA timing, VBID overrides, training pattern selection, DPHY symbols, 8b/10b behavior, scrambler and PRBS control, CRC capture, fast-training, secondary-data packet enable/send/status lines, audio clock M/N programming, MST slot allocation tables and status readbacks, MSO secondary-packet routing, DSC mode/bytes-per-pixel/slice width, metadata packet scheduling, double-buffer handoff state, and low-power ALPM sleep/standby requests.

The `DIG3` and `DIG4` material models encoder and audio formatter behavior used by HDMI/TMDS and display audio. It includes DIG front-end selection and reset, CRC output, test/clock/random patterns, FIFO status, HDMI control/status, audio clock regeneration packet controls, VBI/infoframe/generic packet scheduling, metadata double-buffering, Dynamic Metadata Engine controls, MPEG/audio/generic infoframe payload bytes, Audio Clock Regeneration values and readbacks, IEC 60958 channel-status fields, audio CRC and ramp controls, audio packet/VBI controls, audio source selection, backend enablement, TMDS control characters and DC-balancer settings, and AFMT clock enable/on state.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The important interface is the macro namespace itself:

- `*_SHIFT` macros are integer bit positions, often expressed in hex, used by `FD_SHIFT`, `REG_SET`, `REG_UPDATE`, and related generated register helpers.
- `*_MASK` macros are bit masks with the field already shifted into register position, used by `FD_MASK`, `REG_GET`, `REG_SET`, `REG_UPDATE_N`, and bitfield extraction helpers.
- Register-heading comments such as `//DP3_DP_DPHY_CNTL` or `//DIG3_HDMI_INFOFRAME_CONTROL0` group the fields belonging to one hardware register.
- Address-block comments such as `// addressBlock: dce_dc_dio_dig3_dispdec`, `// addressBlock: dce_dc_dio_dp3_dispdec`, and `// addressBlock: dce_dc_dio_dig4_dispdec` mark repeated display encoder/link instances.

Representative DisplayPort field groups include:

- Link and stream setup: `DP3_DP_LINK_CNTL__DP_LINK_TRAINING_COMPLETE_MASK`, `DP3_DP_PIXEL_FORMAT__DP_PIXEL_ENCODING_MASK`, `DP3_DP_CONFIG__DP_UDI_LANES_MASK`, `DP3_DP_VID_STREAM_CNTL__DP_VID_STREAM_ENABLE_MASK`, and `DP3_DP_VID_TIMING__DP_VID_M_N_GEN_EN_MASK`.
- Main Stream Attribute and VBID fields: `DP3_DP_MSA_MISC__DP_MSA_MISC0_MASK`, `DP3_DP_MSA_TIMING_PARAM1__DP_MSA_VTOTAL_MASK`, `DP3_DP_MSA_TIMING_PARAM3__DP_MSA_HSYNCPOLARITY_MASK`, and `DP3_DP_MSA_VBID_MISC__DP_VBID1_OVERRIDE_EN_MASK`.
- DPHY training and diagnostics: `DP3_DP_DPHY_CNTL__DP_DPHY_ATEST_SEL_MASK`, `DP3_DP_DPHY_TRAINING_PATTERN_SEL__DPHY_TRAINING_PATTERN_SEL_MASK`, `DP3_DP_DPHY_SCRAM_CNTL__DPHY_SCRAMBLER_BS_COUNT_MASK`, `DP3_DP_DPHY_CRC_CNTL__DPHY_CRC_CONT_EN_MASK`, and `DP3_DP_DPHY_FAST_TRAINING_STATUS__DPHY_RX_FAST_TRAINING_COMPLETE_MASK`.
- Secondary data and audio: `DP3_DP_SEC_CNTL__DP_SEC_STREAM_ENABLE_MASK`, `DP3_DP_SEC_CNTL1__DP_SEC_GSP0_SEND_PENDING_MASK`, `DP3_DP_SEC_FRAMING4__DP_SEC_AUDIO_MUTE_MASK`, `DP3_DP_SEC_AUD_N__DP_SEC_AUD_N_MASK`, `DP3_DP_SEC_AUD_M__DP_SEC_AUD_M_MASK`, and `DP3_DP_SEC_PACKET_CNTL__DP_SEC_ASP_CODING_TYPE_MASK`.
- MST/MSO/DSC/metadata: `DP3_DP_MSE_RATE_CNTL__DP_MSE_RATE_Y_MASK`, `DP3_DP_MSE_SAT0__DP_MSE_SAT_SLOT_COUNT0_MASK`, `DP3_DP_MSO_CNTL__DP_MSO_NUM_OF_SSTLINK_MASK`, `DP3_DP_DSC_CNTL__DP_DSC_MODE_MASK`, `DP3_DP_DSC_BYTES_PER_PIXEL__DP_DSC_BYTES_PER_PIXEL_MASK`, and `DP3_DP_SEC_METADATA_TRANSMISSION__DP_SEC_METADATA_PACKET_LINE_MASK`.

Representative DIG/HDMI/AFMT field groups include:

- Encoder front/back end and diagnostics: `DIG3_DIG_FE_CNTL__DIG_SOURCE_SELECT_MASK`, `DIG3_DIG_OUTPUT_CRC_CNTL__DIG_OUTPUT_CRC_EN_MASK`, `DIG3_DIG_TEST_PATTERN__DIG_TEST_PATTERN_MASK`, `DIG3_DIG_FIFO_STATUS__DIG_FIFO_READ_PTR_MASK`, `DIG3_DIG_BE_CNTL__DIG_HPD_SELECT_MASK`, and `DIG3_DIG_BE_EN_CNTL__DIG_BE_ENABLE_MASK`.
- HDMI packetization: `DIG3_HDMI_CONTROL__HDMI_ENABLE_MASK`, `DIG3_HDMI_STATUS__HDMI_STREAM_STATUS_MASK`, `DIG3_HDMI_AUDIO_PACKET_CONTROL__HDMI_AUDIO_PACKETS_PER_LINE_MASK`, `DIG3_HDMI_ACR_PACKET_CONTROL__HDMI_ACR_SEND_MASK`, `DIG3_HDMI_INFOFRAME_CONTROL0__HDMI_AUDIO_INFO_SEND_MASK`, and `DIG3_HDMI_GENERIC_PACKET_CONTROL0__HDMI_GENERIC0_SEND_MASK`.
- Generic and metadata payloads: `DIG3_AFMT_GENERIC_HDR__AFMT_GENERIC_HB0_MASK`, `DIG3_AFMT_GENERIC_0__AFMT_GENERIC_BYTE0_MASK`, `DIG3_HDMI_GENERIC_PACKET_CONTROL1__HDMI_GENERIC0_LINE_MASK`, `DIG3_HDMI_DB_CONTROL__HDMI_DB_PENDING_MASK`, and `DIG3_DME_CONTROL__METADATA_ENGINE_EN_MASK`.
- Audio formatting: `DIG3_AFMT_AUDIO_INFO0__AFMT_AUDIO_INFO_CC_MASK`, `DIG3_AFMT_AUDIO_INFO1__AFMT_AUDIO_INFO_CA_MASK`, `DIG3_AFMT_60958_0__AFMT_60958_CS_SAMPLING_FREQUENCY_MASK`, `DIG3_AFMT_AUDIO_CRC_CONTROL__AFMT_AUDIO_CRC_EN_MASK`, `DIG3_AFMT_AUDIO_PACKET_CONTROL__AFMT_AUDIO_SAMPLE_SEND_MASK`, and `DIG3_AFMT_CNTL__AFMT_AUDIO_CLOCK_EN_MASK`.
- TMDS and HDMI physical formatting: `DIG3_TMDS_CNTL__TMDS_PIXEL_ENCODING_MASK`, `DIG3_TMDS_CONTROL_CHAR__TMDS_CONTROL_CHAR0_MASK`, `DIG3_TMDS_DCBALANCER_CONTROL__TMDS_DCBALANCER_EN_MASK`, and `DIG3_TMDS_CTL0_1_GEN_CNTL__TMDS_CTL0_USE_FEEDBACK_MASK`.

The `DP2`, `DP3`, `DIG3`, and `DIG4` definitions are instance-specific copies. They are expected to be structurally similar to other generated instances, with only the register prefix changing unless the ASIC database intentionally describes per-instance differences.

## Control Flow

This header has no local control flow. Runtime control flow is created by AMD display code that includes this header and expands generated register macros into register tables. Typical use is:

1. A DCN 2.1 module includes `dcn_2_1_0_offset.h` and `dcn_2_1_0_sh_mask.h`.
2. Local register-list macros paste register and field names into `mm...` offsets, `FD_MASK(reg, field)`, and `FD_SHIFT(reg, field)`.
3. Driver objects such as resource, IRQ, GPIO, DIO, AUX/I2C, link encoder, stream encoder, DMUB service, and audio formatter code call register helpers.
4. The helpers use the generated masks and shifts to perform MMIO read/modify/write, extract status bits, set update triggers, clear pending bits, or wait for hardware state changes.

Control-sensitive hardware flows represented by this range include DisplayPort link training completion, training pattern and symbol programming, scrambler enable/reset, CRC capture, video stream enablement, MSA/VBID generation, secondary data packet scheduling, audio mute and audio M/N programming, MST slot table updates, DSC enablement, metadata packet transmission, ALPM sleep/standby requests, HDMI packet send/update sequencing, generic infoframe frame/immediate updates, audio sample packet emission, AFMT clock gating, TMDS control-character generation, and DIG back-end enablement.

The macros do not encode access type, ordering, volatility, self-clearing behavior, write-one-to-clear semantics, or safe update windows. Those rules remain in the display driver logic and hardware programming sequences.

## State And Persistence Behavior

The file itself stores no state and persists nothing. It describes stateful hardware fields whose values live in DCN 2.1 display MMIO registers until changed by software, reset by hardware, altered by hardware state machines, or lost across power/reset events.

State represented by this chunk includes:

- DisplayPort link and stream state: lane/link training completion, pixel encoding, lane count, stream enablement, FIFO steering, MSA fields, VBID overrides, training pattern selection, DPHY symbol values, scrambler mode, PRBS mode, CRC capture state, fast-training status, and ALPM pending/sending states.
- Secondary-data and display-audio state: SDP packet enable bits, generic stream packet send requests and pending/deadline status, line scheduling, frame start positions, idle widths, audio mute status, audio N/M values and readbacks, ASP coding/version/channel override fields, and metadata packet line control.
- MST/MSO/DSC state: MSE rate numerator/denominator, SAT source/slot assignments, SAT update status, MSE link timing, MSO SST-link count and secondary-packet enables, DSC mode, slice width, and bytes-per-pixel.
- DIG/HDMI state: source select, DIG clock/reset controls, CRC enable/results, test pattern selection, FIFO status, HDMI enable/status, ACR packet controls, VBI/infoframe/generic packet sends, packet line numbers, packet double-buffer pending/taken/lock/disable bits, and metadata-engine double-buffer state.
- Audio formatter state: MPEG/audio infoframe payload bytes, AFMT generic payload bytes, ACR CTS/N values and status readbacks, IEC 60958 channel-status values, audio CRC controls/results, ramp controls, audio packet sample layout, VBI packet enablement, audio source selection, and AFMT clock enable/on status.
- TMDS/backend state: backend enable, HPD select, TMDS enable, pixel encoding, control characters, sync pattern fields, CTL bits, DC balancer enable/test state, feedback control, and force-disable state.

Some fields are programmed configuration latches, some are live readbacks, some are hardware pending/status bits, and some are update or clear triggers. A bad read/modify/write can therefore persist until the next modeset, stream reprogramming, connector hotplug sequence, audio reconfiguration, display power transition, suspend/resume, or full GPU reset.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`, which supplies the register offsets matching these field names. This chunk also depends on AMD display register helper conventions in `reg_helper.h` and related DCN macros that paste register and field identifiers into `FD_MASK` and `FD_SHIFT` lookups.

Visible include sites for `dcn_2_1_0_sh_mask.h` in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`, which builds DCN 2.1 resource tables for Renoir display hardware and maps generated registers into display objects.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`, which includes the mask and offset headers while defining DCN 2.1 interrupt service behavior.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.c`, which use generated DCN 2.1 register metadata for GPIO/HPD/DDC/AUX construction and translation.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`, which expands common DMUB register fields using the DCN 2.1 generated masks and shifts.

The `DP2` and `DP3` definitions integrate with DisplayPort link encoder and stream encoder programming, MST bandwidth/slot allocation, DSC setup, metadata packet transport, and low-power link states. The `DIG3` and `DIG4` definitions integrate with DIO/DIG stream encoders, HDMI/TMDS output, audio formatter setup, generic infoframe programming, HDR or vendor metadata transport, and display audio paths.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata. It has no Ceph filesystem, distributed storage, network protocol, or application persistence behavior.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These are compile-time constants, so an incorrect shift or mask can pass C compilation while directing register helpers to the wrong bit, truncating a value, failing to observe a status bit, or clearing/updating the wrong field.

DisplayPort fields are especially sensitive during link training and modeset sequencing. Bad `DP3_DP_DPHY_*`, `DP3_DP_LINK_*`, `DP3_DP_VID_*`, `DP3_DP_MSA_*`, or `DP3_DP_DSC_*` definitions can produce link-training failures, black screens, wrong color/pixel encoding, incorrect timing advertised in MSA, broken DSC transport, missing CRC diagnostics, or errors that only appear on certain lane counts, link rates, monitors, docks, MST topologies, or low-power transitions.

Secondary-data, metadata, and audio fields are protocol-visible. Incorrect SDP, GSP, infoframe, metadata, audio N/M, ASP coding, ACR, IEC 60958, or audio packet masks can result in missing HDMI/DP audio, wrong sample-rate recovery, stale HDR/vendor metadata, malformed AVI/audio/generic infoframes, muted audio, GSP deadline misses, or update-pending bits that never settle.

MST/MSO state has repeated source/slot fields and update controls. Off-by-one field widths or copied masks in `DP*_DP_MSE_SAT*`, `DP*_DP_MSO_CNTL*`, or `DP*_DP_SEC_CNTL*` can allocate the wrong virtual channel payload slots, misroute secondary packets, or break multi-stream and multi-SST-link displays while single-stream panels still work.

DIG/TMDS/HDMI fields mix normal configuration, live status, update triggers, double-buffer handoff bits, and clear bits. Register helpers that use a wrong mask around `DIG*_HDMI_DB_CONTROL`, `DIG*_DME_CONTROL`, `DIG*_HDMI_GENERIC_PACKET_CONTROL*`, or `DIG*_AFMT_VBI_PACKET_CONTROL1` could lose metadata updates, lock a packet buffer, report stale pending state, or send packets on the wrong line.

Repeated generated instances create copy hazards. `DP2` and `DP3` should remain structurally aligned for shared DP register families, and `DIG3` and `DIG4` should mirror each other for the common DIG/HDMI/AFMT families visible in this range. A one-off shift or mask difference should be treated as suspicious unless corroborated by the ASIC register database or matching offset/header generation.

Chunk boundaries are artificial. The range starts after the `DP2_DP_SEC_FRAMING1` heading and first two field shifts, so the `DP2_DP_SEC_FRAMING1` register is split with the previous chunk. It ends inside `DIG4_AFMT_60958_0`, before the remaining masks for that register and later `DIG4` registers. The final merged file research should not infer whole-register completeness at either boundary.

## Test Signals

Useful validation signals are mostly generated-header consistency checks plus hardware/display behavior:

- Build coverage for DCN 2.1 display modules that include `dcn_2_1_0_sh_mask.h`, especially `dcn21_resource.c`, `irq_service_dcn21.c`, DCN21 GPIO translation/factory code, DMUB DCN21 support, DIO/link encoder code, and display audio paths.
- Generated-register validation that every `REGISTER__FIELD__SHIFT` has the expected `REGISTER__FIELD_MASK`, that masks match field widths and shifts, and that matching registers exist in `dcn_2_1_0_offset.h`.
- Structural diff checks across repeated instances: `DP2` versus `DP3`, `DIG3` versus `DIG4`, and adjacent DCN 2.x generated headers where hardware revisions are supposed to be layout-compatible.
- DisplayPort link-training tests across link rates and lane counts, including DPHY training patterns, scrambler reset, CRC diagnostics, PRBS paths, fast-training status, and link-training-complete observation.
- Modeset and stream tests that exercise MSA timing, VBID override, pixel encoding/colorimetry, video stream enable/disable, DSC enablement and bytes-per-pixel programming, and double-buffer update/taken/clear state.
- MST/MSO tests with multiple streams or tiled panels to confirm MSE rate programming, SAT source/slot assignment, SAT updates, MSO secondary packet enables, and metadata packet scheduling.
- HDMI/TMDS tests for HDMI enable/status, ACR CTS/N values, audio sample packets, IEC 60958 channel-status bits, generic infoframes, AVI/audio/vendor/HDR metadata, packet line scheduling, and packet frame/immediate update pending bits.
- Hotplug, suspend/resume, runtime power, display off/on, and ALPM tests that verify link, packet, AFMT, metadata, and double-buffer state is reprogrammed or restored correctly.

Regression symptoms from bad constants in this chunk include black screen after modeset, failed DP link training, MST stream loss, broken DSC panels, stale or missing HDR metadata, no HDMI/DP audio, wrong audio sample rate or channel status, stuck packet update-pending bits, bad CRC diagnostics, HDMI/TMDS output instability, and failures isolated to connector/link instances backed by `DP2`, `DP3`, `DIG3`, or `DIG4`.

## Cross-Chunk Notes

This is one chunk of the generated `dcn_2_1_0_sh_mask.h` file. The previous chunk owns the beginning of the `DP2` secondary-data region, and the next chunk owns the rest of `DIG4_AFMT_60958_0` and later generated `DIG4` definitions. The merge/reconciliation lane should combine this document with adjacent chunks before making final whole-file statements about register-family completeness, instance counts, or generated-header endings.

### subset-b-001673: lines 42009-44390

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 42009-44390

## Scope

This chunk is a generated AMDGPU DCN 2.1.0 register shift/mask header slice. It contains C preprocessor constants only: no functions, structs, enums, storage, or local executable logic. The exported contract is the naming and value pairing of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros used by AMD display register helpers to pack, update, and decode fields in MMIO registers.

The range covers 2,382 source lines with 2,179 `#define` entries, including 1,087 `__SHIFT` constants and 1,253 mask constants or mask-named fields. It starts in the DIG4 audio formatter S/PDIF channel-status area, then covers DIG4 audio packet/TMDS controls, DP4 DisplayPort link and secondary-data controls, DCIO/UNIPHY routing and panel power/backlight controls, DC GPIO/DDC/HPD/AUX pad controls, AUX/I2C pad power-good state, and the first DSC0 top/DSCCIF fields.

## Purpose

The chunk provides the bit layout for a DCN 2.1.0 display-output lane: encoder instance 4 (`DIG4`), DisplayPort instance 4 (`DP4`), shared DCIO and GPIO pad controls, and the start of DSC encoder instance 0. Higher-level AMDGPU display code can use logical register and field names while this generated header supplies ASIC-specific field offsets and masks.

Major hardware areas covered here are:

- `DIG4_AFMT_*`: HDMI/DP audio formatter state for IEC 60958 channel status, audio CRC, audio test ramps, audio FIFO/status/ack bits, audio packet send, audio source selection, infoframe update, generic packet update/pending bits, and immediate-send status.
- `DIG4_DIG_*` and `DIG4_TMDS_*`: digital backend enable/source/mode/HPD selection, symbol clock state, lane enable, TMDS sync/control characters, control-bit generation, DC balancer configuration, feedback selection, and test pattern generation.
- `DP4_DP_*`: DisplayPort link state, pixel format, stream enable/status, M/N timing, MSA/VBID fields, DPHY training/test/CRC/scrambler/FEC controls, secondary-data packet generation, MST/MSE scheduling, MSO controls, DSC-over-DP mode and bytes-per-pixel, double-buffer control, metadata transmission, and ALPM sleep/standby controls.
- `DC_*`, `UNIPHY*`, `LVTMA_*`, and `BL_PWM_*`: display clock/generic clock selection, UNIPHY channel inversion and crossbar routing, write-command delays, pinstrap readback, LVTM panel power sequencing, backlight PWM, genlock/swaplock pad selection, DCIO clock gating, and soft resets.
- `DC_GPIO_*`, `PHY_AUX_CNTL`, and `AUXI2C_PAD_ALL_PWR_OK`: generic GPIOs, DDC pads 1-5 plus VGA DDC, genlock/swaplock, HPD pins, power-sequence pins, pad strength, AUX electrical controls, TX/RX enable, pullups, DDC I2C mode, AUX termination/hysteresis/VOD tuning, DP/DN swap, and per-PHY power-good status.
- `DSC_TOP0_*` and `DSCCIF0_*`: DSC clock/debug control and the first DSCCIF input-interface fields for underflow recovery/status, pixel format, component depth, double-buffer pending state, picture width, and picture height.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The important interface is the generated macro namespace:

- `*_SHIFT` constants give the low bit position for a field.
- `*_MASK` constants give the field mask already shifted into register position.
- Register-heading comments such as `//DP4_DP_SEC_CNTL2` group fields by hardware register.
- Address-block comments such as `// addressBlock: dce_dc_dio_dp4_dispdec` identify the generated register block that owns the following registers.

Representative DIG4 audio and HDMI/TMDS macros include `DIG4_AFMT_60958_0__AFMT_60958_CS_*`, `DIG4_AFMT_AUDIO_CRC_CONTROL__AFMT_AUDIO_CRC_*`, `DIG4_AFMT_STATUS__AFMT_AUDIO_FIFO_OVERFLOW_MASK`, `DIG4_AFMT_AUDIO_PACKET_CONTROL__AFMT_AUDIO_FIFO_OVERFLOW_ACK_MASK`, `DIG4_AFMT_VBI_PACKET_CONTROL1__AFMT_GENERICn_*`, `DIG4_HDMI_GENERIC_PACKET_CONTROL5__HDMI_GENERICn_IMMEDIATE_SEND*`, `DIG4_DIG_BE_CNTL__DIG_FE_SOURCE_SELECT_MASK`, `DIG4_DIG_LANE_ENABLE__DIG_LANEnEN_MASK`, and the `DIG4_TMDS_CTL*_GEN_CNTL` field groups for per-control-symbol source, delay, invert, modulation, feedback, and pattern output.

The DP4 block is the densest protocol surface in this chunk. Important groups include:

- `DP4_DP_LINK_CNTL`, `DP4_DP_CONFIG`, `DP4_DP_PIXEL_FORMAT`, `DP4_DP_VID_STREAM_CNTL`, `DP4_DP_VID_TIMING`, `DP4_DP_VID_N`, and `DP4_DP_VID_M` for stream/link enablement, lane count, pixel encoding/depth, and video timing generation.
- `DP4_DP_DPHY_CNTL`, `DP4_DP_DPHY_TRAINING_PATTERN_SEL`, `DP4_DP_DPHY_SYM*`, `DP4_DP_DPHY_8B10B_CNTL`, `DP4_DP_DPHY_PRBS_CNTL`, `DP4_DP_DPHY_SCRAM_CNTL`, `DP4_DP_DPHY_CRC_*`, and `DP4_DP_DPHY_FAST_TRAINING*` for physical-layer training, FEC, test symbols, scrambler, PRBS, CRC, MST CRC slot selection, and fast-training status.
- `DP4_DP_SEC_CNTL`, `DP4_DP_SEC_CNTL1`, `DP4_DP_SEC_CNTL2` through `_7`, `DP4_DP_SEC_FRAMING*`, `DP4_DP_SEC_AUD_*`, `DP4_DP_SEC_PACKET_CNTL`, and `DP4_DP_SEC_METADATA_TRANSMISSION` for secondary-stream/audio/generic packet scheduling, timestamps, GSP line targeting, active/idle send status, metadata packets, and PPS-related send state.
- `DP4_DP_MSE_*`, `DP4_DP_MSO_*`, `DP4_DP_DSC_CNTL`, and `DP4_DP_DSC_BYTES_PER_PIXEL` for MST allocation timing, multi-stream/multi-segment operation, and Display Stream Compression transport programming.
- `DP4_DP_DB_CNTL`, `DP4_DP_MSA_VBID_MISC`, and `DP4_DP_ALPM_CNTL` for double-buffer commit status, VBID/MSA overrides, and main-link PHY sleep/standby transitions.

DCIO and connector-pad macros include repeated `UNIPHYA` through `UNIPHYE` `*_LINK_CNTL` and `*_CHANNEL_XBAR_CNTL` groups, `DCIO_SOFT_RESET__UNIPHY*_SOFT_RESET_MASK`, `LVTMA_PWRSEQ_*`, `BL_PWM_*`, `DC_GPIO_DDCn_*`, `DC_GPIO_HPD_*`, `DC_GPIO_PWRSEQ_*`, `PHY_AUX_CNTL__AUX_PAD_*`, `DC_GPIO_AUX_CTRL_0` through `_5`, and `AUXI2C_PAD_ALL_PWR_OK__AUXI2C_PHYn_ALL_PWR_OK_MASK`.

The DSC fields are a partial start of a later whole-file section: `DSC_TOP0_DSC_TOP_CONTROL__DSC_CLOCK_EN_MASK`, clock-gating debug fields, and `DSCCIF0_DSCCIF_CONFIG0`/`CONFIG1` input format, underflow, update-pending, width, and height masks.

## Control Flow

This header has no local control flow. Runtime control flow appears in consumers that include `dcn_2_1_0_offset.h` and this shift/mask header, then feed the macros into AMD display register helper tables and read/modify/write operations.

A typical runtime path is:

1. DCN 2.1 code includes the generated offset header and this shift/mask header.
2. Register-table macros such as `REG`, `SF`, `SF_DDC`, `SF_HPD`, and family-specific mask-list macros paste register and field names into these `__SHIFT` and `_MASK` symbols.
3. Driver code calls register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, or generated table initializers.
4. The helper layer uses the shift and mask values to isolate fields, update only the intended bits, poll status, or acknowledge hardware events.

Control-sensitive hardware flows represented by this chunk include audio formatter programming, HDMI/DP infoframe and generic packet updates, TMDS control-character generation, digital backend enable/disable, DP stream enable/disable, link training, FEC and scrambler setup, DPHY test/CRC capture, MST/MSE allocation, secondary-data packet scheduling, DSC transport setup, ALPM sleep/standby requests, UNIPHY lane routing, panel power sequencing, backlight PWM commits, hotplug/DDC/AUX pad operation, and DSC input-interface programming.

The macros do not encode access type or ordering. Callers must still know whether a field is read-only status, sticky status, write-one-to-clear ack, self-clearing command, double-buffered configuration, safe only while disabled, or owned jointly by firmware and hardware state machines.

## State And Persistence Behavior

The file itself stores no software state and performs no persistence. It describes hardware state that persists in DCN registers until software writes it, hardware changes it, a block reset occurs, or power management loses/restores the register contents.

State represented in this range includes:

- Audio formatter state: IEC 60958 channel-status bytes, audio sample send enable, audio source selection, audio test/ramp controls, CRC enable/result, FIFO overflow status/ack, audio enable/HBR status, and generic/infoframe packet update-pending flags.
- Digital encoder state: backend source selection, mode, HPD association, lane enables, symbol-clock on state, TMDS control symbol patterns, modulation/delay/invert settings, and forced digital disable.
- DisplayPort link state: training completion/status, lane count, stream enable/status, pixel format/depth, timing M/N values, DPHY FEC/training/scrambler/CRC/test state, secondary/audio packet control, MSE/MSO allocation, DSC packetization, metadata transmission, double-buffer pending/taken status, and ALPM pending state.
- DCIO state: generic clock routing, UNIPHY channel inversion/crossbar/link-enable state, pinstrap readbacks, soft reset bits, genlock/swaplock pad control, panel power-sequence target and status, and PWM period/duty/update lock.
- GPIO/AUX/DDC/HPD state: pin masks, output values, enables, readbacks, pad pullup/pulldown and strength, DDC clock/data modes, AUX pad electrical tuning, HPD receive/mask selection, TX/RX enable, and AUX/I2C PHY power-good bits.
- DSC state: DSC top-level clock/debug enable and DSCCIF input-interface underflow, pixel format, bits-per-component, update-pending, picture width, and picture height fields.

Many fields are configuration latches, but several are live status or pending bits. Incorrect values can persist until a modeset, connector hotplug, audio reconfiguration, suspend/resume sequence, DCN block reset, or full GPU reset reprograms the affected hardware.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`, which supplies matching register addresses and base indices. This chunk supplies the bit positions inside those registers. The generated identifiers also depend on AMD display macro conventions that paste register and field names into `_MASK` and `__SHIFT` symbols.

Direct include sites visible in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`, which includes the DCN 2.1 offset and mask headers for DMUB-facing DCN21 register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`, which includes these headers while mapping DCN21 IRQ sources and programming interrupt/status register fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`, which includes the generated headers while constructing DCN21 resources for links, encoders, GPIO/DDC/AUX, audio/display output, DSC, and related blocks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c`, which expands DDC and HPD register/mask lists from this header into GPIO hardware objects.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.c`, which translates generated GPIO register offsets and masks such as `DC_GPIO_GENERIC_A__...`, `DC_GPIO_HPD_A__...`, and genlock/swaplock masks into software `gpio_id` and enum values.

Cross-generation helpers also reveal how these macros are consumed. `display/dc/gpio/ddc_regs.h` references `DC_GPIO_AUX_CTRL_5` and DDC I2C-mode field macros, while `display/dc/dsc/dcn20/dcn20_dsc.h` uses `DSCCIF0_DSCCIF_CONFIG0` field macros for DSC input-interface programming. The same generated field names appear across closely related ASIC generations, so field layout drift can affect shared helper macros even when the include path is generation-specific.

Although the repository prefix is `sources/distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata. It has no Ceph filesystem, distributed storage, networking, or durable persistence behavior.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A wrong shift or mask compiles cleanly but can make register helpers alter the wrong bits, truncate a value, miss status, clear the wrong event, or leave a pending command stuck.

DIG4 and DP4 fields are output-path critical. Bad masks in audio formatter, TMDS, DP stream, DPHY, secondary packet, MSE/MSO, DSC, or ALPM fields can cause no display, failed link training, unstable MST, missing HDR/metadata/PPS packets, broken DSC transport, incorrect audio sample/channel status, stuck audio FIFO overflow, or incomplete stream disable/enable sequencing.

Status, ack, and pending bits are especially sensitive. Fields such as `AFMT_AUDIO_FIFO_OVERFLOW_ACK`, `AFMT_60958_CS_UPDATE`, generic packet pending bits, DP secondary-packet deadline/pending bits, DPHY CRC valid/status bits, double-buffer taken/clear bits, and ALPM pending bits often require precise write sequences. A generic read/modify/write using an inaccurate mask can acknowledge an unrelated event or fail to clear the intended one.

GPIO, DDC, HPD, and AUX pad fields are board- and connector-sensitive. Errors in DDC pad mode, pullups, power disable, HPD receive masks, AUX termination, DP/DN swap, hysteresis, VOD tuning, or AUX/I2C power-good handling may show up only on certain connectors, boards, cables, sink devices, or suspend/resume paths.

Repeated blocks increase copy-generation risk. `UNIPHYA` through `UNIPHYE`, `DC_GPIO_DDC1` through `DDC5`, HPD1 through HPD6, AUX1 through AUX6, and generic packet slots should be structurally consistent unless the ASIC register database intentionally differs. A one-off shift or width should be treated as suspicious during generated-header validation.

Chunk boundaries matter. This range starts after the beginning of the DIG4 audio-info section and ends in the middle of `DSCCIF0_DSCCIF_CONFIG1`; the final per-file document should merge adjacent chunks before making whole-file conclusions about DIG4 and DSC coverage.

## Test Signals

Useful validation signals are mostly generated-header checks plus DCN21 display, connector, audio, and DSC behavior:

- Build coverage for DCN21 DMUB, IRQ service, resource construction, GPIO factory/translation, DDC/AUX, display audio, DisplayPort, and DSC code that includes `dcn_2_1_0_sh_mask.h`.
- Generated-register validation that every field in this chunk has a matching register/address definition in `dcn_2_1_0_offset.h`, that masks align with shifts and field widths, and that repeated instances remain structurally consistent.
- HDMI/DP audio tests for sample-rate and channel-status programming, infoframe updates, HBR/non-HBR audio, audio FIFO overflow handling, generic packet updates, hotplug audio recovery, and mode changes.
- DisplayPort tests for link training, stream enable/disable, lane-count changes, MST/MSE allocation, MSO paths, FEC/scrambler behavior, DPHY CRC/test modes, metadata/PPS packet transmission, DSC link operation, and ALPM sleep/standby transitions.
- Connector tests for HPD1-HPD6 detection and interrupts, HPDRX sideband events, EDID reads over DDC/AUX, AUX pad power transitions, suspend/resume, runtime power management, and plug/unplug stress.
- Panel tests for LVTMA power sequencing, backlight PWM period/duty/update locking, power-down minimum delays, and backlight recovery after modeset or power events.
- DSC tests that exercise `DSC_TOP0` clock enable/debug state and `DSCCIF0` input configuration, including underflow status/recovery and double-buffer update-pending behavior.

Regression symptoms from bad constants include failed EDID/AUX transactions, missing hotplug events, black screen on DP4/DIG4 connectors, unstable MST/MSO, incorrect or absent HDMI/DP audio, missing metadata or DSC PPS packets, stuck pending bits, panel power/backlight sequencing failures, DSC underflow interrupts, or failures that appear only on one generated link/pad instance.

## Cross-Chunk Notes

This is a constants-only chunk from a generated DCN 2.1.0 hardware header. Adjacent chunks own earlier DIG4 HDMI/audio-info fields and later DSCC/DSC fields. The merge lane should combine this artificial line range with neighboring chunks so the final per-file document presents the generated register contract as a whole rather than as independent source modules.

### subset-b-001674: lines 44391-46846

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 44391-46846

## Scope

This chunk is a generated AMD DCN 2.1.0 register shift/mask header slice. It exports preprocessor constants only: `REGISTER__FIELD__SHIFT` values and `REGISTER__FIELD_MASK` values used by AMDGPU display register helpers to pack and extract MMIO fields. There are no C functions, structs, enums, or local algorithms in this range.

The slice contains 2,139 `#define` entries: 1,069 shift constants and 1,070 mask constants across 267 register names. It starts at the tail of `DSCCIF0_DSCCIF_CONFIG1` with `PIC_WIDTH` and `PIC_HEIGHT` masks, covers complete generated field sets for DSC/DSCC instances 0 through 3, includes most of instance 4, and ends inside `DSCC4_DSCC_B_CR_SQUARED_ERROR_UPPER`. It also includes DC perfmon instances 19 through 22.

Major hardware domains represented here are:

- `DSC_TOP1` through `DSC_TOP4` top-level Display Stream Compression clock/debug controls.
- `DSCCIF0` through `DSCCIF4` DSC input interface fields for underflow recovery/status/interrupt enable, pixel format, bits per component, picture width, and picture height.
- `DSCC0` through `DSCC4` DSC compressor core fields for slice geometry, initial chunk handling, rate-control buffer model, PPS programming, interrupt/status, memory power, error counters, fullness readbacks, and debug-bus rotation.
- `DC_PERFMON19` through `DC_PERFMON22` performance counter fields for event selection, run/stop control, counter state, interrupt control/status/ack, counter values, high/low reads, and selection control.

## Purpose

The purpose of this chunk is to map DCN 2.1 display-compression and performance-monitor register fields to exact bit positions. Runtime display code uses these generated constants through register-table macros instead of hard-coding numeric shifts and masks.

The DSC portions support programming VESA Display Stream Compression encoder state. The field families map the input interface and compressor core configuration needed for compressed DisplayPort/eDP output: input pixel format, color depth, picture and slice dimensions, slice counts, bits per pixel, chunk size, initial transmit/decode delays, scale intervals, BPG offsets, initial/final offsets, flatness QP bounds, rate-control thresholds, all 15 rate-control range parameter sets, and compressor memory-power controls.

The perfmon portions expose hardware diagnostics around the same DC display fabric. They are repeated generated instances, each with counter event selectors, clear/load/run bits, active/counter state, interrupt threshold/status/ack fields, and high/low counter data.

## Important API Surface

The public surface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

Important DSC top and input-interface constants include:

- `DSC_TOP<n>_DSC_TOP_CONTROL__DSC_CLOCK_EN`, `DSC_DISPCLK_R_GATE_DIS`, and `DSC_DSCCLK_R_GATE_DIS` for clock enable and clock-gating behavior.
- `DSC_TOP<n>_DSC_DEBUG_CONTROL__DSC_DBG_EN` and `DSC_TEST_CLOCK_MUX_SEL` for debug routing.
- `DSCCIF<n>_DSCCIF_CONFIG0__INPUT_INTERFACE_UNDERFLOW_RECOVERY_EN`, `INPUT_INTERFACE_UNDERFLOW_OCCURRED_INT_EN`, `INPUT_INTERFACE_UNDERFLOW_OCCURRED_STATUS`, `INPUT_PIXEL_FORMAT`, and `BITS_PER_COMPONENT`.
- `DSCCIF<n>_DSCCIF_CONFIG1__PIC_WIDTH` and `PIC_HEIGHT`.

Important DSCC compressor core constants include:

- `DSCC<n>_DSCC_CONFIG0__ICH_RESET_AT_END_OF_LINE`, `NUMBER_OF_SLICES_PER_LINE`, `ALTERNATE_ICH_ENCODING_EN`, and `NUMBER_OF_SLICES_IN_VERTICAL_DIRECTION`.
- `DSCC<n>_DSCC_CONFIG1__DSCC_RATE_CONTROL_BUFFER_MODEL_SIZE` and `DSCC_DISABLE_ICH`.
- `DSCC<n>_DSCC_STATUS__DSCC_DOUBLE_BUFFER_REG_UPDATE_PENDING`.
- `DSCC<n>_DSCC_INTERRUPT_CONTROL_STATUS__DSCC_RATE_BUFFER[0-3]_{OVERFLOW,UNDERFLOW}_OCCURRED` and matching interrupt-enable fields, plus `DSCC_RATE_CONTROL_BUFFER_MODEL[0-3]_OVERFLOW_OCCURRED` and interrupt-enable fields.
- `DSCC<n>_DSCC_PPS_CONFIG0` through `DSCC_PPS_CONFIG22`, which carry the generated register form of the DSC picture parameter set and rate-control parameters.
- `DSCC<n>_DSCC_MEM_POWER_CONTROL__DSCC_DEFAULT_MEM_LOW_POWER_STATE`, `DSCC_MEM_PWR_FORCE`, `DSCC_MEM_PWR_DIS`, `DSCC_MEM_PWR_STATE`, and native-422 memory-power fields.
- Error and diagnostic readback fields such as `DSCC_R_Y_SQUARED_ERROR_*`, `DSCC_G_CB_SQUARED_ERROR_*`, `DSCC_B_CR_SQUARED_ERROR_*`, `DSCC_MAX_ABS_ERROR*`, rate-buffer maximum-fullness fields, rate-control-buffer maximum-fullness fields, and `DSCC_TEST_DEBUG_BUS_ROTATE`.

Important perfmon constants include:

- `DC_PERFMON19` through `DC_PERFMON22` `PERFCOUNTER_CNTL`, `PERFCOUNTER_CNTL2`, `PERFCOUNTER_STATE`, `PERFMON_CNTL`, `PERFMON_CNTL2`, `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW` fields.

The main consumer pattern is in `display/dc/dsc/dcn20/dcn20_dsc.h`, where `DSC_REG_LIST_DCN20(id)` builds per-instance DSC register tables and `DSC_REG_LIST_SH_MASK_DCN20(__SHIFT)` / `_MASK` build `dcn20_dsc_shift` and `dcn20_dsc_mask` tables. `display/dc/resource/dcn21/dcn21_resource.c` instantiates those tables for DCN 2.1 DSC instances and passes them to `dsc2_construct`.

## Control Flow

There is no local control flow in this header. Runtime behavior is supplied by AMD display code that pairs these field constants with offsets from `dcn_2_1_0_offset.h`.

A typical DSC flow is:

1. DCN21 resource construction includes `dcn_2_1_0_offset.h` and this shift/mask header.
2. `dcn21_resource.c` expands `DSC_REG_LIST_DCN20(id)` into `dcn20_dsc_registers` for DSC instances 0 through 5 and expands `DSC_REG_LIST_SH_MASK_DCN20` into common shift and mask tables.
3. `dsc2_construct` stores those register, shift, and mask tables in each `dcn20_dsc` object.
4. `dsc2_validate_stream` and `dsc_prepare_config` compute valid DSC register values from `dsc_config`, DRM DSC PPS data, rate-control parameters, slice counts, pixel format, and ODM requirements.
5. `dsc_write_to_registers` uses `REG_SET`, `REG_SET_2`, `REG_SET_3`, `REG_SET_4`, `REG_SET_5`, and similar helpers to program `DSCCIF_CONFIG*`, `DSCC_CONFIG*`, `DSCC_INTERRUPT_CONTROL_STATUS`, and the full `DSCC_PPS_CONFIG0-22` set.
6. `dsc2_enable`, `dsc2_disable`, and `dsc2_disconnect` toggle `DSC_TOP_CONTROL.DSC_CLOCK_EN` and DSCRM forwarding state, while `dsc2_read_state` and `dsc2_read_reg_state` read back selected DSC fields for logging and diagnostics.

Perfmon control flow is similarly external: diagnostic or debug code selects events, clears or loads counters, enables counting, reads high/low counter values, and acknowledges counter interrupts using the generated perfmon fields.

## State And Persistence Behavior

The file stores no software state. It describes hardware state in memory-mapped DCN display registers, which persists until rewritten, reset, power-gated, or changed by hardware.

State represented by this chunk includes:

- DSC top-level clock/debug state per compressor instance.
- DSCCIF input format and image-size state, including underflow recovery, sticky underflow status, and underflow interrupt enable.
- DSCC compressor slice topology, ICH reset behavior, alternate ICH encoding, and rate-control buffer-model sizing.
- The active DSC PPS register image: DSC version, PPS ID, line buffer depth, bits per component, bits per pixel, RGB/YCbCr/native mode flags, block prediction, chunk size, picture/slice dimensions, transmit/decode delays, scale intervals, line and slice BPG offsets, initial/final offsets, flatness limits, rate-control model size, target offsets, 14 buffer thresholds, and 15 QP/BPG range parameter triplets.
- Compressor status and error state: double-buffer update pending, rate-buffer overflow/underflow, RC model overflow, squared-error accumulators, maximum absolute error, maximum fullness levels, and debug-bus rotation selection.
- Compressor memory-power force/disable/default/status fields, including separate native-422 memory power fields.
- Perfmon counter configuration, run state, interrupt state, and counter value state for four generated perfmon instances.

Several fields are sticky status or interrupt bits, several are live readbacks, and several are latched programming values. The header does not encode access permissions, write-one-to-clear semantics, valid value ranges, update-lock requirements, or timing restrictions; callers must enforce those rules.

## Dependencies And Integration Points

This chunk is tightly coupled to the matching DCN 2.1 register offset header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`. Offsets identify the MMIO registers, while this file identifies the bit fields inside those registers.

Direct integration points visible in this source tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`, which includes this header, builds `dsc_regs`, `dsc_shift`, and `dsc_mask`, constructs DCN21 DSC objects, and creates six DSC register-table entries.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.h`, whose `DSC_REG_LIST_DCN20` and `DSC_REG_LIST_SH_MASK_DCN20` macros name the fields defined here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.c`, which validates DSC streams, computes DSC PPS and rate-control parameters, writes DSCCIF/DSCC/PPS fields, toggles DSC enable state, waits for disconnect/update-pending behavior, and reads back selected DSC state.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`, which includes the same DCN 2.1 shift/mask header for DMUB common register field tables, although this specific chunk's DSC fields are not the main DMUB surface.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`, which also includes this header for DCN21 interrupt register field metadata.
- DRM DSC helpers and types, especially `<drm/display/drm_dsc.h>` and `<drm/display/drm_dsc_helper.h>`, plus local DSC helpers under `display/dc/dsc/` such as `dscc_types.h` and `rc_calc.h`.

The repeated generated instance layout is part of the contract. The chunk shows complete field sets for instances 0-3 and most of instance 4, while `dcn21_resource.c` expects six DSC instances. Adjacent chunks must be merged to cover the tail of `DSCC4` and all of `DSCC5`.

## Risks And Edge Cases

- A wrong shift or mask silently programs the wrong hardware bits while C still compiles. The highest-risk fields here are PPS dimensions, bits per pixel/component, slice width/height, slice count, chunk size, rate-control thresholds/ranges, native 420/422 flags, and interrupt enable/status fields.
- DSC programming is protocol-visible. Bad constants can produce corrupted compressed output, link training or stream validation failures, DP/eDP sink decode errors, black screens, underflow, or visual artifacts that only reproduce for DSC-enabled modes.
- `DSCCIF_CONFIG0` and `DSCC_PPS_CONFIG0` both carry bits-per-component style fields and use generated duplicate-field workarounds in `dcn20_dsc.h`. Misnaming or mismatching those macros can put color depth into the wrong register table field.
- The 14 buffer thresholds and 15 rate-control range entries are dense repeated fields spread across `PPS_CONFIG12-22`. Off-by-one, mask-width, or range-order mistakes can pass compile tests but break rate-control behavior under specific bpp, slice, or pixel-format combinations.
- Interrupt status and interrupt-enable fields share `DSCC_INTERRUPT_CONTROL_STATUS`. Incorrect read/modify/write handling or stale masks can miss rate-buffer overflow/underflow events, fail to enable RC model overflow interrupts, or accidentally preserve/clear sticky status.
- Instance-copy errors are easy because `DSCC0` through `DSCC4`, `DSCCIF0` through `DSCCIF4`, and `DSC_TOP1` through `DSC_TOP4` are near-duplicates. A bad instance suffix may affect only a particular display pipe, ODM configuration, or multi-monitor topology.
- Memory-power fields affect compressor SRAM availability. Incorrect `DSCC_MEM_POWER_CONTROL` masks can leave DSC memory powered down while active, block power savings, or report the wrong power state.
- Chunk boundaries are artificial. This range begins after the `DSCCIF0_DSCCIF_CONFIG1` shift definitions and ends before the complete DSCC4 diagnostic set; whole-file reconciliation must combine neighboring chunks before judging completeness.

## Test Signals

Useful validation signals for this chunk include:

- A full AMDGPU display build with DCN21 enabled, covering `dcn21_resource.c`, `dcn20_dsc.c`, DMUB DCN21 code, and DCN21 IRQ code that include `dcn_2_1_0_sh_mask.h`.
- Static generated-header checks against AMD's DCN 2.1 register database and the companion `dcn_2_1_0_offset.h`, verifying that each `__SHIFT` has the expected `_MASK`, field masks do not overlap unintentionally, and repeated DSC instances remain consistent where hardware requires consistency.
- DSC modeset tests for DisplayPort/eDP streams with DSC enabled across different bits per component, RGB/YCbCr 4:4:4, simple 4:2:2, native 4:2:2, native 4:2:0, multiple bpp values, and multiple horizontal/vertical slice counts.
- High-resolution and ODM/multi-DSC tests that exercise multiple compressor instances, especially instances 0-5 as constructed by DCN21 resource code.
- PPS pack/readback comparisons: compare the packed DRM DSC PPS and computed `dsc_reg_values` with hardware readback from `dsc2_read_state` and selected `DSCC_PPS_CONFIG*` registers.
- Underflow and overflow diagnostics that deliberately stress bandwidth or invalid timing and verify DSCCIF underflow status, DSCC rate-buffer overflow/underflow status, RC model overflow status, and corresponding interrupt-enable behavior.
- Suspend/resume, runtime power management, and DSC enable/disable/disconnect tests that verify `DSC_CLOCK_EN`, DSCRM forwarding state, `DSCC_DOUBLE_BUFFER_REG_UPDATE_PENDING`, and DSCC memory-power status converge correctly.
- Perfmon smoke tests that select DC perf events on instances 19-22, run counters, read high/low values, and validate interrupt threshold/status/ack fields.

Regression symptoms from bad constants include DSC stream enable failures, black or corrupted display only on compressed modes, sink-side DSC decode errors, underflow/overflow interrupts, bad bpp or color-depth programming, incorrect slice/chunk sizing, stuck disconnect/update-pending waits, missing power savings, or impossible perf counter values.

## Cross-Chunk Notes

This is a chunk of a generated hardware register layout contract, not a standalone module. The final per-file report should merge it with adjacent `dcn_2_1_0_sh_mask.h` chunks to cover the complete DCN 2.1 field map, including the preceding `DSCCIF0_DSCCIF_CONFIG1` shifts, the remainder of `DSCC4`, and the complete `DSCC5` instance that DCN21 resource construction expects.

### subset-b-001675: lines 46847-49414

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 46847-49414

## Scope

This chunk is a generated constants-only slice of the AMDGPU DCN 2.1.0 register shift/mask header. It contains no functions, structs, enums, storage, or executable code. Its exported contract is preprocessor macros named as `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`; register helper code uses those constants to place or extract bitfields in MMIO and indexed display/audio registers.

The requested range covers 2,568 source lines, with 2,121 `#define` entries: 1,060 shift constants and 1,061 mask constants. It contains 15 generated `addressBlock` sections and 402 register comments. The chunk begins at the final mask for `DSCC4_DSCC_B_CR_SQUARED_ERROR_UPPER`, continues through the tail of DSC instance 4 telemetry, all DSC instance 5 mask/shift definitions, DMCUB, MCIF writeback, DCHVM, legacy VGA indexed register windows, and Azalia F2 endpoint/audio descriptor metadata. It ends at the `//SINK_DESCRIPTION15` register comment, so the sink-description array continues in the next chunk.

## Purpose

The purpose of this header section is to encode the DCN 2.1 ASIC bit layout for several hardware blocks that are otherwise accessed through generic AMD display helpers. The matching offset header supplies register addresses; this header supplies the field positions and masks within each register.

Major hardware areas covered by the chunk are:

- DSC telemetry and DSC instance 5 control: DSCC4 tail error/fullness/debug fields, `DSC_TOP5_*`, `DSCCIF5_*`, `DSCC5_*`, and `DC_PERFMON23/24_*`.
- DMCUB firmware interface: `DMCUB_REGION*`, `DMCUB_INTERRUPT_*`, inbox/outbox ring registers, scratch registers, timer, fault address registers, security/memory controls, and GPINT data paths.
- MCIF writeback instance 2: `MCIF_WB2_*` buffer manager, buffer addresses, pitch, arbitration, watermark, power/self-refresh, QoS, luma/chroma size, high address, and resolution fields.
- Display core host VM: `DCHVM_CTRL0`, `DCHVM_CTRL1`, `DCHVM_CLK_CTRL`, `DCHVM_MEM_CTRL`, `DCHVM_RIOMMU_CTRL0`, and `DCHVM_RIOMMU_STAT0`.
- Legacy VGA indexed windows: sequencer (`SEQ*`), CRT controller (`CRT*`), graphics controller (`GRA*`), and attribute controller (`ATTR*`) bitfields.
- Azalia/HDA display-audio endpoint F2 metadata: converter controls, pin controls, audio descriptors, multichannel controls, HBR, lipsync, sink info access, channel-status overrides, LPIB snapshots, coding/format tracking, wireless display ID, remote keepalive, pin/widget capabilities, standalone audio descriptor records, and sink information strings.

Although this repository path is under `sources/distributed-fs/ceph-client`, the file is AMDGPU display hardware metadata. It has no Ceph filesystem, distributed-storage, network, or on-disk persistence behavior.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The relevant API surface is the generated macro namespace:

- `*_SHIFT` constants hold the low-bit position for a named field.
- `*_MASK` constants hold the already-positioned mask for the same field.
- `//REGISTER_NAME` comments group field macros by hardware register.
- `// addressBlock: ...` comments group registers by generated hardware address block.

The DSC portions include:

- Tail DSCC4 metric masks for squared-error upper bits, max absolute error, rate-buffer fullness, rate-control-buffer fullness, and debug-bus rotation.
- `DC_PERFMON23_*` and `DC_PERFMON24_*` performance monitor fields for event selection, counted-value type, hardware start/stop selection, counter states, perfmon state, report count, count-off interrupt enable/status/ack, counter interrupt status/ack, and high/low value reads.
- `DSC_TOP5_DSC_TOP_CONTROL` and `DSC_TOP5_DSC_DEBUG_CONTROL` fields for DSC clock enables, clock-gating controls, debug selection, and debug status.
- `DSCCIF5_DSCCIF_CONFIG0/1` fields for stream/source selection, clock enable, endianness, 4:2:0 native support, DSCCIF clock gating, OTG vertical start edge, and test seed.
- `DSCC5_DSCC_CONFIG*`, status, interrupt, 23 PPS configuration registers, memory power controls, error accumulators, buffer fullness counters, and test debug bus rotation.

The DMCUB block is the densest section in this chunk. It defines fields for:

- Region base/top/offset programming, including high address halves and region enable bits.
- Region 3 code-window base/top/offset entries `CW0` through `CW7`.
- Interrupt enables, status, ack, type, external interrupt status/context/ack, and low-power wake interrupt enable.
- Fault reporting for instruction fetch, data write, and undefined address faults.
- Security and memory control bits such as reset, memory unit ID, outbox/inbox selection, auto-increment, memory power state/force/disables, and dynamic power controls.
- Inbox and outbox base/size/read-pointer/write-pointer pairs for channels 0 and 1.
- Timer trigger/window/current registers, scratch registers 0 through 15, DMCUB enable/trace/wait/soft-status fields, GPINT data in/out, and processor ID.

The MCIF writeback block covers `MCIF_WB2_*` fields used by the memory-client side of display writeback. Important groups include buffer manager software control/status, current line readback, buffer pitch, four-buffer status and address programming, luma/chroma address offsets and high address halves, arbitration and SCLK-change handling, test debug index/data, VCE control, latency watermark and NB pstate control, self-refresh, clock gating, warm-up, multi-level QoS, buffer luma/chroma sizes, and per-buffer resolution.

The DCHVM block defines the masks used by host-VM/rIOMMU display memory setup. Representative fields are `HOSTVM_INIT_REQ`, `HVM_*_PWR_*`, `HVM_*CLK_*_GATE_DIS`, request/response clock request modes, `HOSTVM_PREFETCH_REQ`, `HOSTVM_POWERSTATUS`, `RIOMMU_ACTIVE`, and `HOSTVM_PREFETCH_DONE`.

The VGA indexed blocks expose legacy VGA register fields such as sequencer reset, clocking mode, map mask, character-map select, memory mode, CRT timing registers, cursor start/end/location, start address, offset, underline, mode control, line compare, graphics set/reset, color compare, rotate, read map select, graphics mode, miscellaneous graphics, color don't-care, bit mask, and attribute palette/control/overscan/plane-enable/pixel-panning/color-select fields.

The Azalia F2 endpoint block defines HDA-style HDMI/DP audio codec fields. Important groups include converter format fields, channel/stream IDs, digital converter state, stripe/ramp/GTC embedding controls, capability reports, pin widget control, unsolicited response, pin sense, configuration default words, speaker/channel allocation, downmix, audio descriptor selection/data, multichannel enables, lipsync, HBR, sink-info index/data windows, multichannel mode, channel-status override words 0-8, association/digital-output status, LPIB snapshot/control, coding type, format changed, wireless display identity, remote keepalive, pin/widget capabilities, and connection-list length. The separate `azendpoint_descriptorind` section defines `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`, each with max channels, supported frequencies, descriptor byte 2, and stereo frequency fields. The `azendpoint_sinkinfoind` section begins manufacturer/product ID, sink description length, port ID, and sink-description byte records through the `SINK_DESCRIPTION15` comment at the requested boundary.

## Control Flow

This chunk has no local control flow. Runtime control flow appears in consumers that expand the generated macros into register tables, then use generic register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_WAIT`, `FD_MASK`, and `FD_SHIFT`.

The common flow is:

1. A DCN 2.1 component includes `dcn_2_1_0_offset.h` and `dcn_2_1_0_sh_mask.h`.
2. The component declares generation-specific register tables by pasting register and field names through macros such as `SR`, `SRI`, `SRII`, `REG_OFFSET`, `FD_MASK`, and `FD_SHIFT`.
3. Runtime code calls the register helpers against those tables.
4. The helpers use these shifts and masks to construct read/modify/write values, decode status, acknowledge interrupts, poll hardware state, or program indexed audio/VGA windows.

Control-sensitive flows represented by this chunk include DSC compressor configuration and telemetry reads, DMCUB boot and mailbox setup, DMCUB outbox interrupt enable/ack handling, display writeback buffer programming, DCHVM/rIOMMU initialization and prefetch polling, legacy VGA indexed access, and HDMI/DisplayPort audio endpoint programming.

Concrete integration examples in this tree include:

- `display/dmub/src/dmub_dcn21.c` includes this header and builds `dmub_srv_dcn21_regs` from `DMUB_COMMON_REGS()` and `DMCUB_INTERNAL_REGS()`, with field masks and shifts from `DMUB_COMMON_FIELDS()`.
- `display/dc/irq/dcn21/irq_service_dcn21.c` includes this header and maps the DMCUB outbox interrupt through `DMCUB_INTERRUPT_ENABLE.DMCUB_OUTBOX1_READY_INT_EN` and `DMCUB_INTERRUPT_ACK.DMCUB_OUTBOX1_READY_INT_ACK`.
- `display/dc/resource/dcn21/dcn21_resource.c` includes this header, instantiates DSC register/mask/shift tables, creates DSC instances from `dsc_regs[]`, `dsc_shift`, and `dsc_mask`, and wires in DWB/MMHUB/DCHVM resources.
- `display/dc/hubbub/dcn21/dcn21_hubbub.[ch]` uses the DCHVM fields to request host-VM initialization, poll `RIOMMU_ACTIVE`, set host-VM power status, request prefetch, enable clock gating, and wait for `HOSTVM_PREFETCH_DONE`.

## State And Persistence Behavior

The header itself stores no software state and performs no persistence. It describes hardware-visible state whose lifetime is controlled by the ASIC, driver programming, firmware, reset domains, and display power-management transitions.

State represented by the DSC and DC perfmon fields includes DSC enable/configuration, picture parameter set values, native 4:2:0/4:2:2 and bits-per-component settings, slice geometry, rate-control and quantization parameters, memory power-control bits, interrupt status/ack/mask/type, error accumulators, rate-buffer fullness levels, debug-bus selectors, and perfmon counter configuration/state/value/interrupt state.

DMCUB state includes address windows for firmware regions, code windows, inbox/outbox rings, ring pointers, interrupt masks/status/acks, external interrupt context, security reset/memory controls, scratch registers used for firmware-driver handshake and diagnostics, GPINT payloads, timer state, fault addresses, low-power wake controls, memory power state, and processor identity. Some of these values are programmed during DMUB boot; others are live readbacks, firmware-owned handshake fields, or sticky fault/interrupt status.

MCIF writeback state includes capture buffer selection and address programming, pitch, luma/chroma offsets and sizes, buffer status, arbitration and pstate/watermark behavior, QoS, clock-gating/self-refresh/warm-up controls, current-line readback, VCE-facing controls, and debug selectors. These fields persist until the writeback pipeline is reprogrammed, reset, or power-gated.

DCHVM state includes host-VM initialization request, rIOMMU active/prefetch status, display host-VM power reflection, GPUVM return controls, and clock-gating policy. The driver code expects a specific sequence: request init, poll activity, reflect power, request prefetch, and wait for completion.

VGA indexed state is legacy display state. These fields can affect VGA-compatible mode timing, memory maps, palette attributes, cursor, text/graphics behavior, and controller resets. Modern DC paths may rarely touch them, but stale or wrong masks can still affect compatibility paths.

Azalia F2 state includes audio stream format, channel and stream binding, digital converter metadata, pin capabilities/control/status, ELD/sink-derived descriptors, multichannel mapping, HBR/lipsync settings, channel-status overrides, LPIB snapshots, format-change state, wireless display identity, remote keepalive, sink manufacturer/product/port IDs, and sink description bytes. Some fields are capability mirrors exposed through the HDA codec model, some are programmed from display sink data, and some are live or sticky status.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`, which defines the matching register addresses and base indices. This header is only useful together with those offsets and AMD's register-helper macro conventions.

Visible DCN 2.1 include sites are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.c`

DSC integration is through `dcn20_dsc` structures and `DSC_REG_LIST_DCN20` / `DSC_REG_LIST_SH_MASK_DCN20` expansions in the DCN 2.1 resource pool. Only a subset of the six generated DSC instances may be exposed by the resource capability; the full generated register layout still exists in the header.

DMCUB integration crosses both the DMUB service and DC IRQ service. The DMUB service programs region windows, scratch/inbox/outbox state, and common fields. IRQ service uses DMCUB interrupt enable/ack masks for outbox notification. Incorrect constants here can break the display microcontroller boot path, driver/firmware command rings, interrupt delivery, or fault diagnostics.

MCIF writeback integration is through DCN 2.0 writeback and MMHUB helper code reused by DCN 2.1 (`dcn20_dwb`, `dcn20_mmhubbub`). The `MCIF_WB2_*` fields line up with writeback buffer, watermark, arbitration, and memory-client programming.

DCHVM integration is through `dcn21_hubbub`. Its masks are consumed in host-VM/rIOMMU bring-up and power/clock policy programming.

Azalia integration is shared with HDMI/DP audio code and HDA endpoint indexed-register handling. The F2 endpoint and descriptor/sink-info windows are protocol-facing because they contribute to stream format, sink descriptor, channel allocation, and HDA codec responses.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A wrong generated shift or mask will compile cleanly but can update the wrong bitfield, truncate a value, fail to clear a sticky status bit, or poll a bit that never changes.

DSC fields are display-quality and link-bandwidth sensitive. Bad PPS, rate-control, slice, BPC, native mode, memory-power, or interrupt fields can produce DSC validation failures, blank display, corrupt compressed output, wrong buffer-fullness/error telemetry, or interrupts that cannot be acknowledged. The range begins at line 46847 in the middle of the DSCC4 register family, so whole-instance conclusions require the previous chunk.

DMCUB fields are boot and firmware-communication critical. Errors in region offsets/top addresses, inbox/outbox sizes or pointers, scratch fields, interrupt ack/enable bits, security reset, memory power controls, or GPINT payloads can prevent DMUB firmware from starting, cause stuck command rings, lose outbox notifications, hide fault addresses, or break suspend/resume and low-power wake behavior.

MCIF writeback fields are memory-safety and capture-correctness sensitive. Wrong luma/chroma address high/low fields, offsets, buffer sizes, pitch, or resolution masks can write captured frames to the wrong memory location or with the wrong layout. Incorrect arbitration, pstate, watermark, QoS, or self-refresh fields can cause underrun/overrun, stalls, excessive latency, or power-management regressions.

DCHVM fields have ordering and polling requirements that are not encoded by the macros. Callers must still request initialization, observe rIOMMU activity, reflect power status, request prefetch, configure clock gating, and wait for prefetch completion in a safe order. Bad masks can create hangs in `REG_WAIT` paths or falsely mark the host-VM path active.

VGA fields are legacy but broad in effect. A bad field in an indexed VGA register can affect mode reset, palette, timing, memory map, or cursor behavior in compatibility paths. These indexed registers are also easy to misuse because address/data-window sequencing is outside this header.

Azalia fields are externally observable through HDA/HDMI/DP audio behavior. Incorrect converter format, stream ID, digital converter, audio descriptor, multichannel, HBR, channel allocation, LPIB, sink info, or channel-status masks can cause missing audio, wrong sample rate/channel count, bad non-PCM/HBR behavior, bad ELD/sink advertisement, stuck format-change events, or incorrect codec responses after hotplug.

Chunk boundaries are important. The first line is a lone DSCC4 mask whose shift and register heading are in the previous chunk. The final requested line is only the `//SINK_DESCRIPTION15` comment; its shift and mask definitions are immediately after the requested range and belong to the next chunk. The merge lane should reconcile those partial register groups before producing the final per-file document.

## Test Signals

Useful validation is mostly build coverage plus hardware/driver behavior:

- Compile coverage for DCN 2.1 display, DMUB, IRQ, GPIO, resource, DSC, DWB, MMHUB, hubbub, and audio paths that include `dcn_2_1_0_sh_mask.h`.
- Generated-header consistency checks that each `*_SHIFT` has a corresponding `*_MASK`, masks match shift and field width expectations, and all registers have matching addresses in `dcn_2_1_0_offset.h`.
- DSC validation on DCN 2.1 display modes that require DSC, including modeset, hotplug, suspend/resume, PPS programming, rate-control behavior, DSC interrupt status/ack, and error/fullness telemetry.
- DMUB boot and mailbox tests that verify region programming, firmware start, inbox/outbox pointer movement, scratch/status values, GPINT data exchange, outbox IRQ delivery, low-power wake, and fault capture.
- DCHVM/rIOMMU tests that exercise host-VM initialization, `RIOMMU_ACTIVE` polling, prefetch request/completion, clock gating, power transitions, and resume paths.
- Display writeback tests covering buffer address programming, pitch, luma/chroma sizes, four-buffer rotation, current-line/status reads, watermark/pstate behavior, QoS, and captured frame correctness.
- VGA compatibility smoke tests where applicable, especially modes that touch indexed sequencer/CRT/graphics/attribute registers.
- HDMI/DisplayPort audio tests for PCM and non-PCM formats, sample-rate changes, multichannel layouts, HBR, lipsync, channel-status overrides, LPIB snapshots, sink info/descriptors, hotplug, and format-change handling.

Regression symptoms from bad constants include DMUB firmware not booting, hung outbox interrupts, display init timeouts, DSC validation or visual failures, broken writeback captures, host-VM prefetch waits timing out, no HDMI/DP audio, wrong audio channel/rate advertisement, stuck audio status bits, and endpoint- or instance-specific failures that follow a generated register instance.

## Cross-Chunk Notes

This is an artificial line-range slice of a generated header, not a standalone module. It partially overlaps DSCC4 at the start and cuts the `azendpoint_sinkinfoind` sink-description sequence before the `SINK_DESCRIPTION15` field macros. The final merge should combine this document with adjacent chunks for whole-file conclusions about DCN 2.1.0 register coverage and repeated instance consistency.

### subset-b-001676: lines 49415-51898

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 49415-51898

## Scope

This chunk is a generated constants-only slice of AMDGPU's DCN 2.1.0 register shift/mask header. It contains no functions, structs, enums, storage objects, or executable code. The exported interface is 2,030 preprocessor definitions: 1,015 `__SHIFT` constants and 1,015 already-positioned `_MASK` constants for fields in DCN 2.1 Azalia/display-audio registers.

The range starts at the tail of sink description byte fields (`SINK_DESCRIPTION15` through `SINK_DESCRIPTION17`), then covers Azalia input/output CRC result windows, the function-2 input codec node, function-2 root/function codec parameters, sixteen `AZF0STREAM*` stream latency/FIFO windows, full function-0 output endpoint blocks 0 through 2, and the opening converter fields of output endpoint 3. The source line boundary is artificial: endpoint 3 continues after this chunk and the earlier sink description fields begin in the previous chunk.

## Purpose

The header provides exact bit positions and masks for DCN 2.1.0 display-audio hardware registers. Consumers use these generated constants with matching address macros from `dcn_2_1_0_offset.h` so generic register helpers can read, compose, update, and decode hardware fields without hard-coding bit arithmetic at each call site.

Major hardware areas represented in this chunk are:

- `SINK_DESCRIPTION15` through `SINK_DESCRIPTION17`: final single-byte sink description fields, used by audio sink/ELD-style metadata paths.
- `AZALIA_INPUT_CRC{0,1}_CHANNEL0..7` and `AZALIA_CRC{0,1}_CHANNEL0..7`: 32-bit per-channel input and output audio CRC result fields for diagnostic validation.
- `AZALIA_F2_CODEC_INPUT_*`: function-2 input converter and input pin controls, including stream format, channel/stream binding, digital converter status, pin enable, unsolicited response, pin sense, default configuration, channel allocation, multichannel enable/mute/channel IDs, HBR, LPIB snapshots, input activity, infoframe fields, channel status, widget capabilities, and pin capabilities.
- `AZALIA_F2_CODEC_ROOT_*` and `AZALIA_F2_CODEC_FUNCTION_*`: root/function-level vendor/device, revision, subordinate-node, power-state, subsystem-ID, converter synchronization, reset, supported rate/format, group type, and power-state capability fields.
- `AZF0STREAM0` through `AZF0STREAM15`: repeated FIFO sizing and latency counter controls for each audio stream, including manual/ack/update flags, RAM byte count, worst-case latency count, cumulative latency count, and cumulative request count.
- `AZF0ENDPOINT0`, `AZF0ENDPOINT1`, and `AZF0ENDPOINT2`: repeated function-0 HDMI/DisplayPort output audio endpoint register fields for converter controls, pin controls, sink information, audio descriptors, multichannel routing, channel-status overrides, LPIB snapshots, format-change tracking, remote keepalive, and audio enable/disable/format-change interrupt status.
- `AZF0ENDPOINT3`: the first converter capability and converter-format fields for a fourth output endpoint, with the remainder outside this line range.

Although the repository path is under `sources/distributed-fs/ceph-client`, this source is AMD display hardware metadata. It has no Ceph filesystem, distributed storage, network protocol, or persistent storage behavior.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The API contract is the generated macro naming scheme:

- `REGISTER__FIELD__SHIFT` gives the low bit position for a field.
- `REGISTER__FIELD_MASK` gives the field mask already shifted into register position.
- Register comments such as `//AZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL` group fields by hardware register.
- Address-block comments such as `// addressBlock: azf0stream0_streamind` and `// addressBlock: azf0endpoint0_endpointind` identify indexed hardware register windows.

The input codec group exposes HDA-style format and capability fields. Representative macros include `AZALIA_F2_CODEC_INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT__NUMBER_OF_CHANNELS_MASK`, `...BITS_PER_SAMPLE_MASK`, `...SAMPLE_BASE_DIVISOR_MASK`, `...SAMPLE_BASE_MULTIPLE_MASK`, `...SAMPLE_BASE_RATE_MASK`, and `...STREAM_TYPE_MASK`; `AZALIA_F2_CODEC_INPUT_CONVERTER_CONTROL_CHANNEL_STREAM_ID__CHANNEL_ID_MASK` and `...STREAM_ID_MASK`; `AZALIA_F2_CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER__DIGEN_MASK`, `...V_MASK`, `...NON_AUDIO_MASK`, `...PRO_MASK`, `...CC_MASK`, and `...KEEPALIVE_MASK`; and input pin status/infoframe fields such as `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_INPUT_STATUS_CONTROL__INPUT_ACTIVITY_MASK` and `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_INFOFRAME__INFOFRAME_VALID_MASK`.

The stream blocks repeat a small latency/FIFO model per `AZF0STREAMn`. Each stream has `AZALIA_FIFO_SIZE_CONTROL` fields for `AZALIA_FIFO_SIZE_MANUAL`, `AZALIA_FIFO_SIZE_UPDATE`, `AZALIA_FIFO_SIZE_ACK`, and `AZALIA_FIFO_SIZE_RAM`; plus `AZALIA_LATENCY_COUNTER_CONTROL`, `AZALIA_WORSTCASE_LATENCY_COUNT`, `AZALIA_CUMULATIVE_LATENCY_COUNT`, and `AZALIA_CUMULATIVE_REQUEST_COUNT`.

The endpoint blocks repeat a dense output codec model. Important groups include:

- `AZF0ENDPOINTn_AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` for audio widget capability flags, delay, and type.
- `...CONVERTER_CONTROL_CONVERTER_FORMAT` for channel count, sample size, sample-rate encoding, and PCM/non-PCM stream type.
- `...CONVERTER_CONTROL_CHANNEL_STREAM_ID` for stream-to-channel binding.
- `...CONVERTER_CONTROL_DIGITAL_CONVERTER` for digital enable, validity, pre-emphasis, copyright, non-audio/professional metadata, category code, generation level, and keepalive.
- `...CONVERTER_PARAMETER_STREAM_FORMATS`, `...SUPPORTED_SIZE_RATES`, `...STRIPE_CONTROL`, `...CONTROL_RAMP_RATE`, `...CONTROL_GTC_EMBEDDING`, and `...GTC_COUNTER_DELTA*` for capabilities and presentation-time/GTC synchronization.
- `...CODEC_PIN_PARAMETER_*` and `...CODEC_PIN_CONTROL_*` for pin capabilities, unsolicited response, pin sense, output enable, speaker/channel allocation, audio descriptors 0 through 13, multichannel enable/mute/channel IDs, lipsync, HBR, sink info, hot-plug audio enable, forced unsolicited response payloads, configuration default, LPIB, coding type, format-change state, wireless display identification, and remote keepalive.
- `...PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8` for IEC 60958 channel-status override fields.
- `...AUDIO_ENABLE_STATUS`, `...AUDIO_ENABLED_INT_STATUS`, `...AUDIO_DISABLED_INT_STATUS`, and `...AUDIO_FORMAT_CHANGED_INT_STATUS` for endpoint audio state and interrupt metadata.

## Control Flow

This header has no local control flow. Runtime behavior occurs in the DCN 2.1 display driver code that includes the offset and mask headers and expands register tables through helper macros.

A typical path is:

1. DCN 2.1 resource, IRQ, GPIO, DMUB, or audio code includes `dcn_2_1_0_offset.h` and this `dcn_2_1_0_sh_mask.h`.
2. Register-table macros such as `REG_OFFSET`, `SRI`, `SR`, `SF`, `FD_MASK`, and `FD_SHIFT` paste register and field names into generated macro names.
3. Driver code stores the resulting offsets, masks, and shifts in generation-specific register structures.
4. Common helpers issue MMIO or indexed Azalia endpoint accesses, using the masks and shifts to update or decode individual fields.

The control-sensitive flows represented by this chunk include display-audio stream format programming, stream ID assignment, digital converter enable/metadata handling, endpoint/pin capability reporting, channel and speaker allocation, high-bit-rate audio enablement, sink descriptor propagation, hot-plug audio enablement, latency counter sampling, LPIB snapshot locking, format-change acknowledgment, and audio enable/disable/format-change interrupt reporting.

## State And Persistence Behavior

The file itself stores no state and performs no persistence. It describes hardware register state whose lifetime is controlled by DCN/Azalia hardware, driver writes, power management, reset, and hotplug/modeset activity.

State represented in this range includes:

- CRC readback state for input and output audio channels, useful for validation rather than normal configuration.
- Input converter state: stream format, channel/stream routing, digital converter control, keepalive, supported size/rate masks, and supported stream formats.
- Input pin state: pin enable, unsolicited response tag/enable, pin sense, default configuration bytes, channel allocation, multichannel enable/mute/channel IDs, HBR capability/enable, LPIB snapshots, input activity, channel layout, infoframe contents, and channel-status words.
- Root/function codec state: vendor/device/revision identity, subordinate node counts, power-state request/actual state, clock-stop capability, reset, group type, supported size/rates, supported stream formats, and subsystem ID bytes.
- Stream telemetry state: FIFO size update/ack bits plus worst-case and cumulative latency/request counters.
- Output endpoint state: converter format, stream binding, digital converter metadata, presentation-time/GTC embedding, endpoint/pin capabilities, output active/enable status, audio descriptor and sink information, hot-plug audio enable state, channel-status overrides, LPIB snapshots, coding type, format-change response fields, wireless display identity, remote keepalive, and interrupt flags/masks/types.

Some of these fields are writable configuration latches, some are read-only or hardware-updated status/counter values, and some combine status, mask, type, enable, force, and acknowledgment semantics. The generated header does not encode access permissions or ordering rules; consumers must apply the hardware programming sequence correctly.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`, which supplies matching register addresses and indexed offsets. This chunk supplies the field layout within those registers. Both headers depend on AMD display helper conventions that paste register and field identifiers into `_MASK` and `__SHIFT` names.

Visible DCN 2.1 include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`, which includes the generated headers and builds DCN 2.1 resource tables, including `audio_regs`, `audio_shift`, and `audio_mask`. Its audio mask list uses `AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_INDEX` and `AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_DATA` fields as the indexed access pair for output audio endpoints.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h`, which defines the common `AUD_COMMON_REG_LIST` and audio field-list macros consumed by DCN resource files.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`, which includes this header for DCN 2.1 interrupt register and field definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c` and `hw_translate_dcn21.c`, which include the same generated header for GPIO/HPD translation and register-mask tables elsewhere in the file.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`, which uses `FD_MASK` and `FD_SHIFT` expansions from the generated header for DMUB common field tables.

The Azalia field names also align with generated enum headers such as `soc24_enum.h` and `vega10_enum.h`, which document symbolic values for fields like input converter bits per sample, number of channels, sample-base divisor/multiple/rate, stream type, digital enable, multichannel mute, unsolicited response enable, and input pin enable.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A wrong shift or mask will usually compile cleanly but can set or read the wrong bit, truncate a field, leave stale bits behind during read/modify/write, or acknowledge/mask the wrong interrupt.

Display audio fields are externally visible. Bad converter format, sample-rate, channel-count, stream-type, stream-ID, digital-converter, channel-allocation, audio-descriptor, sink-info, HBR, or IEC 60958 channel-status masks can lead to no HDMI/DisplayPort audio, incorrect PCM/non-PCM handling, wrong channel layout, bad sample rate/word length metadata, broken HBR audio, or endpoint-specific audio failures after hotplug.

Interrupt and event fields are sensitive because they mix flag, mask, type, response, enable, and force fields. Incorrect constants in `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, `AUDIO_FORMAT_CHANGED_INT_STATUS`, `UNSOLICITED_RESPONSE`, `UNSOLICITED_RESPONSE_FORCE`, or `FORMAT_CHANGED` can drop events, generate spurious events, fail to clear sticky status, or route events to the wrong endpoint.

The generated repetition creates copy/generation hazards. `AZF0STREAM0` through `AZF0STREAM15` should remain structurally aligned; `AZF0ENDPOINT0` through `AZF0ENDPOINT2` are near-identical endpoint instances; and endpoint 3 begins with the same converter pattern. Any one-off difference in a repeated shift or mask should be verified against the ASIC register database rather than assumed intentional.

Chunk boundaries matter. This range begins after the first sink-description fields and ends after only the opening `AZF0ENDPOINT3` converter format definitions. The final per-file research merge should avoid treating this slice as a complete Azalia or endpoint inventory.

## Test Signals

Useful validation signals include:

- Build coverage for DCN 2.1 resource, IRQ, GPIO, DMUB, and audio code that includes `dcn_2_1_0_sh_mask.h`.
- Generated-header consistency checks that every `__SHIFT` has a matching `_MASK`, masks align with their shifts and expected widths, and every register appears in the matching `dcn_2_1_0_offset.h`.
- Repetition checks across `AZF0STREAM0..15` and `AZF0ENDPOINT0..3` to detect accidental drift in repeated generated instances.
- HDMI/DisplayPort audio playback tests across PCM and non-PCM formats, sample-rate changes, word-length changes, two-channel and multichannel layouts, HBR, hotplug, modeset, suspend/resume, and monitor replacement.
- Audio event tests confirming enabled, disabled, and format-changed interrupt flags/masks/types assert and clear as expected for each endpoint.
- Sink metadata tests that validate audio descriptor, sink info, channel allocation, speaker allocation, channel-status override, and ELD-derived behavior reported to the audio stack.
- CRC and latency telemetry checks that audio CRC, FIFO-size update/ack, worst-case latency, cumulative latency, request counts, LPIB, and timer snapshots move plausibly while audio streams are active.

Regression symptoms from bad constants include missing or distorted HDMI/DP audio, incorrect channel count or sample rate, stuck audio interrupts, repeated unsolicited responses, failure to detect format changes, broken HBR streams, bad sink capability reporting, or a failure that affects only one generated stream or endpoint instance.

## Cross-Chunk Notes

This is one artificial line-range chunk from a generated whole-file register map. The previous chunk owns earlier sink description fields and likely more Azalia/global audio definitions. The next chunk continues `AZF0ENDPOINT3` and later endpoint/input-endpoint material. The final merge lane should present this as part of the DCN 2.1 generated register contract rather than as an independently maintained module.

### subset-b-001677: lines 51899-54266

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 51899-54266

## Scope

This chunk is part of AMDGPU's generated DCN 2.1.0 register shift/mask header. It contains preprocessor constants only: no functions, structs, enums, storage objects, or executable control flow. The exported surface is the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macro pairs used by AMD display register helpers to encode and decode fields in DCN 2.1 Azalia/HDA display-audio endpoint registers.

The range covers 2,368 source lines with 2,048 `#define` entries: 1,025 shift constants and 1,023 mask constants. It starts in the middle of the `AZF0ENDPOINT3` output endpoint block, fully covers output endpoints 4, 5, and 6, and ends in the early audio-descriptor portion of output endpoint 7. The repeated endpoint model is visible through the `addressBlock: azf0endpoint4_endpointind`, `azf0endpoint5_endpointind`, `azf0endpoint6_endpointind`, and `azf0endpoint7_endpointind` comments.

## Purpose

This header chunk describes bit layouts for DCN 2.1 display audio output endpoint registers. The endpoint names use AMD's `AZF0ENDPOINTn_AZALIA_F0_*` convention, where each endpoint is an indexed HDA/Azalia codec endpoint used for HDMI/DisplayPort audio exposure and control.

The covered register families provide field positions and masks for:

- Converter stream binding, including channel ID, stream ID, converter sample format, stream type, and advertised stream formats/rates.
- Digital converter state, including digital enable, valid/config/pre-emphasis/copyright/non-audio/professional/channel-status category fields, generation level, and keepalive.
- Audio stream synchronization support, including stripe control, ramp rate, Global Time Counter embedding controls, and GTC delta/min/max readback fields.
- Pin capability and control state, including HDA widget capabilities, pin capabilities, unsolicited response tags, pin sense, output enable, channel/speaker allocation, and HDMI/DP connection indicators.
- Short audio descriptor storage, with descriptor registers 0 through 13 for full endpoint blocks and descriptor 0 through 7 for the partial endpoint 7 tail in this chunk.
- Multichannel routing and mute/channel-ID assignment through `MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2`.
- Sink/ELD-style metadata, including manufacturer/product IDs, sink description length, port IDs, and 18 bytes of sink description spread across `SINK_INFO4` through `SINK_INFO8`.
- Hot-plug audio enablement, forced unsolicited responses, default pin configuration, channel-status override words, LPIB snapshots, coding type, format-change response, wireless display identification, remote keepalive, and audio enable/disable/format-change interrupt status.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The interface is the macro namespace and the guarantee that consumers can paste a register name and field name into AMD register helper macros.

Key conventions:

- `*_SHIFT` gives the low bit position for a field.
- `*_MASK` gives the already-shifted bit mask for that field.
- Register-heading comments such as `//AZF0ENDPOINT4_AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL` group the field macros belonging to one generated register.
- Address-block comments identify indexed endpoint register windows, not C scopes.

Representative converter groups include `AZF0ENDPOINTn_AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, `...CONVERTER_CONTROL_CONVERTER_FORMAT`, `...CONVERTER_CONTROL_CHANNEL_STREAM_ID`, `...CONVERTER_CONTROL_DIGITAL_CONVERTER`, `...PARAMETER_STREAM_FORMATS`, `...PARAMETER_SUPPORTED_SIZE_RATES`, `...STRIPE_CONTROL`, `...CONTROL_RAMP_RATE`, `...CONTROL_GTC_EMBEDDING`, and `...GTC_COUNTER_DELTA*`.

Representative pin groups include `AZF0ENDPOINTn_AZALIA_F0_CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, `...PIN_PARAMETER_CAPABILITIES`, `...PIN_CONTROL_UNSOLICITED_RESPONSE`, `...RESPONSE_PIN_SENSE`, `...WIDGET_CONTROL`, `...CHANNEL_SPEAKER`, `...AUDIO_DESCRIPTOR0` through `...AUDIO_DESCRIPTOR13`, `...MULTICHANNEL_ENABLE`, `...RESPONSE_LIPSYNC`, `...RESPONSE_HBR`, `...SINK_INFO0` through `...SINK_INFO8`, `...HOT_PLUG_CONTROL`, `...UNSOLICITED_RESPONSE_FORCE`, `...RESPONSE_CONFIGURATION_DEFAULT`, and `...MULTICHANNEL_ENABLE2`.

Endpoint bookkeeping and interrupt/status groups include `...PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8`, `...CODEC_PIN_ASSOCIATION_INFO`, `...DIGITAL_OUTPUT_STATUS`, `...LPIB_SNAPSHOT_CONTROL`, `...LPIB`, `...LPIB_TIMER_SNAPSHOT`, `...CODING_TYPE`, `...FORMAT_CHANGED`, `...WIRELESS_DISPLAY_IDENTIFICATION`, `...REMOTE_KEEPALIVE`, `...AUDIO_ENABLE_STATUS`, `...AUDIO_ENABLED_INT_STATUS`, `...AUDIO_DISABLED_INT_STATUS`, and `...AUDIO_FORMAT_CHANGED_INT_STATUS`.

## Control Flow

This chunk has no local control flow. Runtime control flow appears in consumers that include the matching DCN 2.1 offset and shift/mask headers, build register-field tables, and access MMIO or indexed Azalia registers through AMD display helper macros.

A typical path is:

1. DCN21 resource, IRQ, GPIO, DMUB, or audio-related display code includes `dcn_2_1_0_offset.h` and `dcn_2_1_0_sh_mask.h`.
2. Generation-specific tables are assembled with macro expansion helpers such as register/field initializers and mask/shift lists.
3. Runtime code programs endpoint registers during display audio setup, hotplug processing, modeset, audio stream changes, interrupt handling, suspend/resume, or DMUB-assisted flows.
4. Register helpers use the `_MASK` and `__SHIFT` constants to preserve unrelated bits while setting or extracting individual fields.

The control-sensitive hardware flows represented here are endpoint-to-stream assignment, converter format programming, digital converter enable/metadata programming, HDMI/DP sink audio descriptor propagation, multichannel channel mapping, hot-plug audio enablement, forced unsolicited response generation, channel-status override programming, LPIB snapshot capture, audio coding/format-change tracking, and audio enable/disable/format-change interrupt reporting.

The macros do not encode sequencing, access permissions, volatile status behavior, write-one-to-clear semantics, self-clearing behavior, or required clock/power state. Callers must supply those semantics from the register programming model and the surrounding DC/audio code.

## State And Persistence Behavior

The file itself stores no software state and performs no persistence. It describes hardware register state whose lifetime is controlled by the DCN 2.1 display-audio block, driver programming, hotplug/modeset activity, power management, and GPU reset.

State represented in this chunk includes:

- Converter configuration: channel and stream IDs, sample size/rate encoding, stream type, supported stream formats/rates, stripe/ramp settings, and GTC presentation-time embedding state.
- Digital audio metadata: enable/valid/configuration bits, pre-emphasis, copyright and non-audio flags, professional mode, category code, level, and remote/stream keepalive state.
- Pin and sink state: pin capabilities, pin sense, output-enable state, channel/speaker allocation, HDMI/DP connection markers, descriptor payloads, lipsync/HBR response fields, ELD-like sink information, and default pin configuration.
- Routing state: multichannel enable, mute, and channel-ID fields for paired even channels in `MULTICHANNEL_ENABLE` and odd channels in `MULTICHANNEL_ENABLE2`.
- Position and status state: LPIB snapshot controls, snapshot values, timer snapshots, coding type, format-change response, wireless display identification, digital output status, endpoint association, and audio enablement status.
- Interrupt state: audio enabled, audio disabled, and audio format changed flag/mask/type fields for each complete endpoint block in the range.

Some of these fields are capability constants, some are writable configuration latches, some are live status readbacks, and some are interrupt status or masking controls. Misprogrammed values can persist until the next audio reconfiguration, hotplug event, modeset, suspend/resume reinitialization, or full GPU reset.

## Dependencies And Integration Points

The direct companion file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`, which supplies the matching register addresses and indexed endpoint offsets. This chunk supplies the bit layout within those registers.

Visible include sites for the DCN 2.1.0 offset and shift/mask headers in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`, where DCN21 resource construction wires generation-specific display, link, audio, GPIO, and IRQ register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`, where generated masks feed interrupt source definitions and status/ack handling.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.c` and `.../hw_translate_dcn21.c`, which include the same generated namespace for DCN21 GPIO object creation and translation.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`, where DCN21 DMUB support uses generation-specific register definitions.

The display-audio endpoint constants integrate with the common AMD display audio path that programs HDMI/DP audio capabilities, stream formats, sink descriptors, channel allocation, HBR state, and endpoint interrupts. Although the repository prefix is `distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata and has no Ceph filesystem or distributed-storage behavior.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A bad mask or shift compiles cleanly, but register helpers may update the wrong bits, truncate a value, fail to preserve neighboring fields, or misread status.

Endpoint repetition creates copy/generation hazards. Endpoint 4, 5, and 6 are full repeated blocks and should be structurally aligned. Endpoint 3 starts mid-block because earlier endpoint 3 definitions live in the previous chunk. Endpoint 7 is incomplete in this chunk and continues in the next chunk after `AUDIO_DESCRIPTOR7`. Merge/reconciliation should avoid treating those chunk boundaries as hardware boundaries.

Audio protocol behavior is sensitive to these constants. Errors in converter format, stream ID, supported rates, digital converter metadata, pin capabilities, audio descriptors, HBR, channel allocation, sink info, or channel-status override fields can lead to missing HDMI/DP audio, wrong sample rate/channel exposure, incorrect non-PCM handling, bad IEC 60958 metadata, or endpoint-specific failures after hotplug.

Interrupt/status fields are also sensitive. `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, and `AUDIO_FORMAT_CHANGED_INT_STATUS` combine flag, mask, and type fields. Incorrect field definitions can leave interrupts stuck, masked, unacknowledged, or attributed to the wrong endpoint. Forced unsolicited-response fields can also create misleading HDA codec events if payload and force bits are mishandled.

LPIB and GTC fields cross timing and presentation domains. Wrong snapshot, timer, or GTC embedding masks can break audio position reporting or presentation-time correlation in ways that appear as drift, stale position reads, or format-change glitches rather than obvious register failures.

## Test Signals

Useful validation signals are a mix of generated-header consistency checks and DCN21 display-audio behavior:

- Build coverage for DCN21 resource, IRQ, GPIO, DMUB, and display audio paths that include `dcn_2_1_0_sh_mask.h`.
- Generated-register validation that every field in this chunk has a matching register definition in `dcn_2_1_0_offset.h`, and that each mask is consistent with its shift and field width.
- Structural comparison across `AZF0ENDPOINT4`, `AZF0ENDPOINT5`, and `AZF0ENDPOINT6`, with special handling for the partial `AZF0ENDPOINT3` and `AZF0ENDPOINT7` chunk boundaries.
- HDMI and DisplayPort audio tests for endpoint stream binding, PCM and non-PCM formats, sample-rate changes, multichannel layouts, channel allocation, HBR, descriptor updates, and channel-status override behavior.
- Hotplug and modeset tests that verify audio enablement, ELD/sink-info propagation, unsolicited response behavior, and audio recovery after disconnect/reconnect and suspend/resume.
- Interrupt tests that confirm audio enabled, audio disabled, and audio format changed events report, mask, clear, and route correctly per endpoint.
- LPIB/GTC sanity checks during playback that confirm snapshot locks, LPIB values, timer snapshots, and presentation-time delta fields move plausibly and do not regress across format changes.

Regression symptoms from bad constants include no HDMI/DP audio, wrong channel count or sample rate, missing or stale sink descriptions, broken HBR/non-PCM playback, incorrect channel-status metadata, audio disappearing after hotplug, stuck audio interrupts, or endpoint-specific failures that only affect one generated `AZF0ENDPOINTn` instance.

## Cross-Chunk Notes

This is chunk 22 of 24 for `dcn_2_1_0_sh_mask.h`. The previous chunk contains the beginning of `AZF0ENDPOINT3`, and the next chunk continues `AZF0ENDPOINT7` after `AUDIO_DESCRIPTOR7`. The final per-file research document should merge these slices into the full generated DCN 2.1 register-layout contract and should not infer architectural boundaries from this artificial line range.

### subset-b-001678: lines 54267-56533

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 54267-56533

## Purpose

This chunk is part of AMD's generated DCN 2.1 ASIC register field mask header. It does not define functions or runtime logic; it defines `#define` constants for bit shifts and masks used when reading or programming Azalia/HD-audio codec registers through the display controller register access layer.

The covered lines span the tail of the `azf0endpoint7` output pin-control block and most of the repeated `azf0inputendpointN_inputendpointind` input endpoint blocks for endpoints 0 through 7. The constants describe HDMI/DisplayPort audio capabilities, audio stream format fields, channel mapping, hot-plug/audio-enable status, unsolicited response signaling, LPIB snapshots, IEC 60958 channel-status overrides, and input audio infoframe/status fields.

## Important Definitions

- `AZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR7..13__*`: remaining audio descriptor fields for output endpoint 7. The repeated layout exposes `MAX_CHANNELS`, `SUPPORTED_FREQUENCIES`, and `DESCRIPTOR_BYTE_2` masks/shifts used to advertise supported sink audio formats.
- `AZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE*__*`: output endpoint 7 channel-pair enable, mute, and channel-id fields. The first register groups channel pairs `01`, `23`, `45`, and `67`; `MULTICHANNEL_ENABLE2` exposes odd channel controls; `MULTICHANNEL_MODE` selects the multi-channel mode.
- `AZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_*`: output pin response fields for lipsync, high bit rate audio (`HBR_CAPABLE`, `HBR_ENABLE`), default configuration, sink information, and unsolicited response forcing.
- `AZF0ENDPOINT7_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_0..8__*`: IEC 60958 channel-status override fields for mode, source number, clock accuracy, word length, sampling frequency, original sampling frequency, channel numbers, CGMS-A, MPEG surround, and validity/override-enable bits.
- `AZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_CONTROL_LPIB*__*`: link position in buffer snapshot, raw LPIB value, timer snapshot, and cyclic buffer wrap count fields.
- `AZF0ENDPOINT7_AZALIA_F0_AUDIO_*_INT_STATUS__*`: output endpoint 7 interrupt status/mask/type fields for audio enabled, disabled, and format changed events.
- `AZF0INPUTENDPOINT0..7_AZALIA_F0_CODEC_INPUT_CONVERTER_*__*`: repeated input converter fields for audio widget capabilities, converter format, channel/stream id, digital converter control, stream format capabilities, and supported size/rate capabilities.
- `AZF0INPUTENDPOINT0..7_AZALIA_F0_CODEC_INPUT_PIN_*__*`: repeated input pin fields for widget capabilities, pin capabilities, unsolicited response enable/tag, input pin sense, widget input enable, channel allocation, hot-plug/audio enable, default configuration, LPIB snapshots, input status, and HDMI/DP audio infoframe data.

Each named field has a paired `__SHIFT` and `_MASK` definition. The conventional consumer pattern is to combine these constants with register read/modify/write helpers so callers can isolate a field using the mask and position a new value using the shift.

## Control Flow

There is no executable control flow in this chunk. The practical control flow appears in including C files that select DCN 2.1 register lists and then use generated offset/mask headers with AMD display register macros. In this repository, `dcn_2_1_0_sh_mask.h` is included by DCN 2.1 display modules such as `display/dmub/src/dmub_dcn21.c`, `display/dc/irq/dcn21/irq_service_dcn21.c`, `display/dc/gpio/dcn21/hw_factory_dcn21.c`, `display/dc/gpio/dcn21/hw_translate_dcn21.c`, and `display/dc/resource/dcn21/dcn21_resource.c`.

For this specific chunk, the runtime flow is indirect:

1. A DCN 2.1 module includes `dcn_2_1_0_offset.h` and `dcn_2_1_0_sh_mask.h`.
2. Register access tables bind symbolic register offsets to masks/shifts.
3. Display/audio setup, interrupt, GPIO, or DMUB code reads or writes hardware registers through AMD's register helper macros.
4. These constants define which bits correspond to a requested Azalia endpoint field.

The repeated input endpoint sections imply table-driven or macro-generated use. Endpoints 0 through 6 are complete in this chunk; endpoint 7 begins and continues beyond line 56533.

## State And Persistence Behavior

The header itself has no memory, persistence, initialization, or teardown behavior. The state represented by the constants lives in hardware registers:

- Capability registers report persistent hardware/firmware-advertised properties such as widget capabilities, supported stream formats, supported sample rates, HDMI/DP pin support, HBR capability, and sink identity fields.
- Control registers hold mutable device state such as converter format, digital converter enable, channel/stream id, channel enable/mute/channel id, unsolicited response configuration, hot-plug audio enable, input widget enable, and remote keepalive.
- Snapshot/status registers expose transient hardware state such as LPIB position, timer snapshots, wrap counts, input activity, infoframe validity, audio enable status, and interrupt flags.

Persistence is therefore owned by the display/audio hardware and any driver paths that program it. Misprogramming a mask or shift affects live MMIO/register state, not a software-owned data structure in this file.

## Dependencies And Integration Points

- Paired offset headers such as `dcn_2_1_0_offset.h` provide the register addresses; this file provides field layout. A mask without the matching offset does not identify a hardware location.
- AMD display register helper macros in the DC driver consume `*_MASK` and `*__SHIFT` constants to generate field reads/writes.
- The constants align with HD Audio/Azalia codec concepts: converter format, stream id, digital converter control, pin widget capabilities, unsolicited responses, pin sense, infoframe fields, channel allocation, and IEC 60958 channel status.
- The repeated `AZF0INPUTENDPOINTN_` naming binds each logical input endpoint to the same register shape. Any table or macro that assumes uniform endpoint layout depends on all endpoint blocks staying consistent.
- The output endpoint 7 definitions integrate with HDMI/DP audio output handling, audio format-change reporting, HBR support, sink information, and channel-status override programming.

## Risks

- Because this file is generated hardware contract data, a one-bit error in a mask or shift can silently corrupt unrelated register fields during read/modify/write operations.
- Repeated endpoint blocks are easy to miscompare by eye. A copy-generation mismatch for one `AZF0INPUTENDPOINTN_` block would affect only that endpoint and may surface as port-specific audio failures.
- The chunk starts mid-register (`AUDIO_DESCRIPTOR7`) and ends mid-endpoint (`AZF0INPUTENDPOINT7`), so whole-file review must reconcile this chunk with adjacent chunks before making conclusions about the complete endpoint 7 input block.
- Several fields affect interrupt behavior (`*_UR_ENABLE`, `AUDIO_*_INT_STATUS__*_MASK`) and live audio routing (`DIGEN`, channel IDs, stream IDs, mute bits). Incorrect definitions can produce missing notifications, stuck interrupts, wrong channel layout, or silent audio.
- The constants use long integer hexadecimal literals. Consumers should avoid assumptions about signedness or field width beyond the masks provided here.

## Test Signals

- Build coverage: any syntax or name collision issue should appear when compiling DCN 2.1 display code that includes `dcn_2_1_0_sh_mask.h`.
- Register table coverage: tests or static checks that instantiate DCN 2.1 register/mask tables should catch missing macro names referenced by C sources.
- Hardware/display validation: HDMI/DP audio enumeration, hot-plug audio enable, HBR playback, multi-channel output, input endpoint reporting, and audio format-change interrupts are the meaningful runtime signals for this region.
- Regression checks should compare this generated header against AMD's authoritative register database or adjacent ASIC-generation headers for endpoint layout consistency.
- For chunk reconciliation, confirm that the final merged research accounts for the preceding output endpoint 7 definitions before line 54267 and the continuation of input endpoint 7 after line 56533.

### subset-b-001679: lines 56534-56648

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 56534-56648

## Scope

This chunk is the final slice of AMDGPU's generated DCN 2.1.0 shift/mask header. It contains C preprocessor constants only: no functions, structs, enums, storage objects, or executable code. The exported contract is a set of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros that describe bit positions and already-positioned masks for DCN 2.1.0 hardware registers.

The range starts in the middle of the `AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE` masks, then completes the remaining input endpoint 7 audio pin-control register fields through `INFOFRAME`. It ends with `MPC_OCSC_TEST_DEBUG_INDEX`, `MPC_OCSC_TEST_DEBUG_DATA`, and the header-closing `#endif`.

## Purpose

The macros provide ASIC-specific bitfield metadata for two hardware areas:

- `AZF0INPUTENDPOINT7_*`: indexed Azalia/HDA display-audio input endpoint 7 pin-control fields, covering multichannel channel routing, HBR capability and enablement, channel allocation, hot-plug audio enablement, forced unsolicited responses, default codec pin configuration, LPIB snapshots, input activity/status, and audio infoframe metadata.
- `MPC_OCSC_TEST_DEBUG_*`: memory pixel combiner output color-space conversion test/debug index and data fields, used as a small index/data debug access pair for MPC OCSC internal state.

Higher-level driver code can use logical field names while the generated header supplies the exact DCN 2.1.0 bit layout. This is especially important because the same register names recur across DCN generations and endpoint instances, while masks or register availability can still diverge by ASIC.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The important interface is the macro naming pattern:

- `*_SHIFT` is the low bit position for a field.
- `*_MASK` is the field mask already shifted into register position.
- Register-heading comments group fields by hardware register name.

The first lines finish `AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE` for channels 0-3. Each channel uses the same byte lane pattern: enable at bit 0/8/16/24, mute at bit 1/9/17/25, and a 4-bit channel ID at bits 4-7, 12-15, 20-23, or 28-31.

`AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE2` repeats the same layout for channels 4-7:

- `MULTICHANNEL4_ENABLE`, `MULTICHANNEL4_MUTE`, `MULTICHANNEL4_CHANNEL_ID`
- `MULTICHANNEL5_ENABLE`, `MULTICHANNEL5_MUTE`, `MULTICHANNEL5_CHANNEL_ID`
- `MULTICHANNEL6_ENABLE`, `MULTICHANNEL6_MUTE`, `MULTICHANNEL6_CHANNEL_ID`
- `MULTICHANNEL7_ENABLE`, `MULTICHANNEL7_MUTE`, `MULTICHANNEL7_CHANNEL_ID`

`AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_HBR` exposes `HBR_CAPABLE` at bit 0 and `HBR_ENABLE` at bit 4. These fields advertise and control high-bit-rate audio behavior for the endpoint.

`AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_CHANNEL_ALLOCATION` contains an 8-bit `CHANNEL_ALLOCATION` field at bits 0-7. This matches HDMI/DisplayPort audio channel layout metadata carried through the HDA codec model.

`AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_HOT_PLUG_CONTROL` has `CLOCK_GATING_DISABLE`, `CLOCK_ON_STATE`, and `AUDIO_ENABLED`. The high bit `AUDIO_ENABLED_MASK` (`0x80000000L`) is the most visible state/control flag in this group.

`AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE_FORCE` defines a 26-bit `UNSOLICITED_RESPONSE_PAYLOAD` field and a force bit at bit 28. This lets software force an HDA-style unsolicited response payload for endpoint event notification paths.

`AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT` packs the HDA pin default configuration fields:

- `SEQUENCE` bits 0-3
- `DEFAULT_ASSOCIATION` bits 4-7
- `MISC` bits 8-11
- `COLOR` bits 12-15
- `CONNECTION_TYPE` bits 16-19
- `DEFAULT_DEVICE` bits 20-23
- `LOCATION` bits 24-29
- `PORT_CONNECTIVITY` bits 30-31

`AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL`, `..._LPIB`, and `..._LPIB_TIMER_SNAPSHOT` describe link-position-in-buffer snapshot locking, an 8-bit cyclic-buffer wrap count, a 32-bit LPIB value, and a 32-bit timer snapshot value.

`AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INPUT_STATUS_CONTROL` exposes `INPUT_ACTIVITY`, 2-bit `CHANNEL_LAYOUT`, and two unsolicited-response enable bits for activity and channel-layout/channel-status infoframe changes.

`AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME` exposes `CHANNEL_COUNT`, `CHANNEL_ALLOCATION`, `INFOFRAME_BYTE_5`, and `INFOFRAME_VALID`. This group is the endpoint's decoded input audio infoframe summary.

The final MPC debug macros are:

- `MPC_OCSC_TEST_DEBUG_INDEX__MPC_OCSC_TEST_DEBUG_INDEX__SHIFT/MASK` for the 8-bit debug index.
- `MPC_OCSC_TEST_DEBUG_INDEX__MPC_OCSC_TEST_DEBUG_WRITE_EN__SHIFT/MASK` for the write-enable bit at bit 8.
- `MPC_OCSC_TEST_DEBUG_DATA__MPC_OCSC_TEST_DEBUG_DATA__SHIFT/MASK` for the full 32-bit data value.

## Control Flow

This header has no local control flow. Runtime behavior is created by consumers that include the DCN 2.1.0 offset and mask headers and then use AMD display register helpers to read, update, or decode fields.

A typical use pattern is:

1. DCN 2.1 code includes `dcn_2_1_0_offset.h` and this shift/mask header.
2. Register tables or helper macros paste register and field names into `_MASK` and `__SHIFT` identifiers.
3. Driver paths issue MMIO or indexed-register operations through helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, or register table initializers.
4. The helpers use these constants to isolate the intended bitfields.

For the Azalia input endpoint fields, the runtime sequencing lives in display-audio setup, hotplug, infoframe, and stream routing code. This chunk only states the bitfield layout; it does not encode whether a field is read-only, write-one-to-clear, sticky, self-clearing, clock-gated, or safe only while audio is disabled.

For the MPC OCSC debug pair, runtime code would normally select an internal debug index, set write enable when needed, and read or write the data register. The chunk does not define legal debug indices, side effects, or synchronization requirements.

## State And Persistence Behavior

The file itself stores no state and persists nothing. It describes hardware register state whose lifetime is controlled by the DCN display block, Azalia/HDA codec endpoint logic, power management, reset, and driver reprogramming.

Endpoint state represented here includes:

- Per-channel enable, mute, and channel-ID routing for multichannel input audio lanes 0-7.
- HBR capability and enable state.
- Channel allocation and infoframe-derived channel count/allocation/byte-5/valid state.
- Hot-plug and audio-enabled state for input endpoint 7.
- Forced unsolicited-response payload and force trigger state.
- HDA default pin configuration fields that describe endpoint association, device type, physical location, connection type, color, and port connectivity.
- LPIB snapshot lock, cyclic-buffer wrap count, current link position, and timer snapshot readback.
- Input activity, channel layout, and unsolicited-response enable state.

Some of these are configuration latches, some are live status readbacks, and some represent event-generation controls. Bad writes may persist until a display audio reconfiguration, hotplug cycle, suspend/resume, DCN power transition, or full GPU reset rewrites the endpoint.

The MPC OCSC debug index/data registers are debug state. Their contents may affect only diagnostic readback paths, but if write-enable is used incorrectly they can also alter an indexed internal debug register until changed or reset.

## Dependencies And Integration Points

The direct companion for this chunk is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`, which defines the matching register addresses and indexed offsets. Relevant companions include:

- `ixAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE2` at indexed offset `0x0037`.
- `ixAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_HBR` at `0x0038`.
- `ixAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_CHANNEL_ALLOCATION` at `0x0053`.
- `ixAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_HOT_PLUG_CONTROL` at `0x0054`.
- `ixAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE_FORCE` at `0x0055`.
- `ixAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT` at `0x0056`.
- `ixAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL` at `0x0064`.
- `ixAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_LPIB` at `0x0065`.
- `ixAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_LPIB_TIMER_SNAPSHOT` at `0x0066`.
- `ixAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INPUT_STATUS_CONTROL` at `0x0067`.
- `ixAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME` at `0x0068`.
- `mmMPC_OCSC_TEST_DEBUG_INDEX` and `mmMPC_OCSC_TEST_DEBUG_DATA` at MMIO offsets `0x163b` and `0x163c`, base index 2.

Visible include sites for `dcn_2_1_0_sh_mask.h` in this tree are:

- `display/dc/resource/dcn21/dcn21_resource.c`, which builds DCN 2.1 resource objects and register tables.
- `display/dc/irq/dcn21/irq_service_dcn21.c`, which uses generated masks for interrupt handling tables.
- `display/dc/gpio/dcn21/hw_factory_dcn21.c` and `display/dc/gpio/dcn21/hw_translate_dcn21.c`, which use the same generated register namespace for GPIO-related objects.
- `display/dmub/src/dmub_dcn21.c`, which includes DCN 2.1 register metadata for DMUB-facing display microcontroller support.

Direct textual references to these exact endpoint 7 macros are uncommon because AMD's display code often consumes generated headers through macro-paste register lists rather than spelling every field name directly. Cross-generation headers such as `dcn_3_0_1_sh_mask.h`, `dcn_3_5_0_sh_mask.h`, and `dcn_3_5_1_sh_mask.h` carry similar endpoint fields, which makes this range part of a broader generated-register compatibility surface.

Although the repository path sits under `sources/distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata. It has no Ceph, filesystem, distributed-storage, or network protocol behavior.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A wrong mask or shift still compiles but can write the wrong bit, truncate a field, decode status incorrectly, or leave stale bits behind during read/modify/write operations.

The multichannel fields are dense and repeated. Each channel occupies a byte lane, with a 4-bit channel ID in the high nibble. Off-by-one shifts or masks can swap enable/mute bits, route an audio channel to the wrong slot, or corrupt the neighboring channel's ID.

The HBR, channel allocation, and infoframe fields are protocol-visible. Incorrect masks can cause HDMI/DisplayPort audio to advertise the wrong channel count, channel allocation, or high-bit-rate support, leading to missing audio, wrong speaker mapping, or failures that appear only with multichannel/HBR sinks.

The hot-plug and unsolicited-response fields interact with event delivery. A bad `AUDIO_ENABLED`, unsolicited payload, or unsolicited-response enable mask can make endpoint state changes invisible to the codec model, generate unexpected events, or fail to report activity/channel-layout changes.

The LPIB snapshot fields mix locking, wrap count, position, and timer snapshot readback. Incorrect usage can produce inconsistent audio position reporting or races around snapshot capture. The header does not say whether callers must lock before reading both snapshot registers; that ordering must come from the hardware programming guide or existing audio helper code.

The MPC OCSC debug index/data pair is sensitive because indexed debug register interfaces can have side effects. The `MPC_OCSC_TEST_DEBUG_WRITE_EN` bit must not be confused with the index field; accidental writes may alter debug state rather than only reading it. The matching enums in `soc21_enum.h` and later `soc24_enum.h` define false/true values for this write-enable field, reinforcing that it is a real control bit rather than padding.

Chunk boundaries are also relevant. The first lines are only the masks for the tail of `MULTICHANNEL_ENABLE`; the matching shift macros for channels 0-3 are in the previous chunk. Whole-file reconciliation should merge this slice with the preceding endpoint 7 material before drawing conclusions about complete input endpoint coverage.

## Test Signals

Useful validation is mostly generated-header and hardware-behavior oriented:

- Build coverage for DCN 2.1 display resource, IRQ, GPIO, DMUB, and audio-related code that includes `dcn_2_1_0_sh_mask.h`.
- Generated-register consistency checks that every mask in this chunk has the expected shift and width, and that every register has a matching offset in `dcn_2_1_0_offset.h`.
- Cross-generation diffs against adjacent DCN headers for endpoint 7 and MPC OCSC debug fields, with expected differences reviewed against the ASIC register database.
- HDMI/DisplayPort audio tests for stereo, multichannel 5.1/7.1, channel allocation changes, HBR/non-PCM formats, hotplug, modeset, suspend/resume, and sink changes.
- Infoframe and input-status tests that confirm channel count, allocation, byte 5, valid bit, input activity, channel layout, and unsolicited-response behavior update as expected.
- LPIB position tests that verify snapshot lock, wrap count, LPIB, and timer snapshot values are stable and plausible during playback or capture-style endpoint activity.
- Debugfs or internal validation, where available, for MPC OCSC test-debug index/data access without unintended writes when write-enable is clear.

Regression symptoms from bad constants include no HDMI/DP audio, wrong speaker mapping, broken HBR playback, stale or missing audio hotplug events, incorrect HDA pin default reporting, inconsistent audio position reporting, stuck unsolicited responses, or MPC debug reads/writes returning impossible values.

## Cross-Chunk Notes

This is the final chunk of `dcn_2_1_0_sh_mask.h`. The previous chunk owns the beginning of input endpoint 7, including the first `MULTICHANNEL_ENABLE` shift definitions and earlier input pin-control capability/status fields. The final per-file document should treat this chunk as the tail of a generated DCN 2.1.0 register-layout contract rather than a standalone module.
