# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001687`: lines 1-2452, `Docs/researches/chunks/subset-b-001687_research.md`
- `subset-b-001688`: lines 2453-4724, `Docs/researches/chunks/subset-b-001688_research.md`
- `subset-b-001689`: lines 4725-7166, `Docs/researches/chunks/subset-b-001689_research.md`
- `subset-b-001690`: lines 7167-9804, `Docs/researches/chunks/subset-b-001690_research.md`
- `subset-b-001691`: lines 9805-12287, `Docs/researches/chunks/subset-b-001691_research.md`
- `subset-b-001692`: lines 12288-14786, `Docs/researches/chunks/subset-b-001692_research.md`
- `subset-b-001693`: lines 14787-17309, `Docs/researches/chunks/subset-b-001693_research.md`
- `subset-b-001694`: lines 17310-19827, `Docs/researches/chunks/subset-b-001694_research.md`
- `subset-b-001695`: lines 19828-22333, `Docs/researches/chunks/subset-b-001695_research.md`
- `subset-b-001696`: lines 22334-24838, `Docs/researches/chunks/subset-b-001696_research.md`
- `subset-b-001697`: lines 24839-27351, `Docs/researches/chunks/subset-b-001697_research.md`
- `subset-b-001698`: lines 27352-29904, `Docs/researches/chunks/subset-b-001698_research.md`
- `subset-b-001699`: lines 29905-32369, `Docs/researches/chunks/subset-b-001699_research.md`
- `subset-b-001700`: lines 32370-34834, `Docs/researches/chunks/subset-b-001700_research.md`
- `subset-b-001701`: lines 34835-37214, `Docs/researches/chunks/subset-b-001701_research.md`
- `subset-b-001702`: lines 37215-39587, `Docs/researches/chunks/subset-b-001702_research.md`
- `subset-b-001703`: lines 39588-41983, `Docs/researches/chunks/subset-b-001703_research.md`
- `subset-b-001704`: lines 41984-44385, `Docs/researches/chunks/subset-b-001704_research.md`
- `subset-b-001705`: lines 44386-46812, `Docs/researches/chunks/subset-b-001705_research.md`
- `subset-b-001706`: lines 46813-49204, `Docs/researches/chunks/subset-b-001706_research.md`
- `subset-b-001707`: lines 49205-51607, `Docs/researches/chunks/subset-b-001707_research.md`
- `subset-b-001708`: lines 51608-54079, `Docs/researches/chunks/subset-b-001708_research.md`
- `subset-b-001709`: lines 54080-56610, `Docs/researches/chunks/subset-b-001709_research.md`
- `subset-b-001710`: lines 56611-59133, `Docs/researches/chunks/subset-b-001710_research.md`
- `subset-b-001711`: lines 59134-61618, `Docs/researches/chunks/subset-b-001711_research.md`
- `subset-b-001712`: lines 61619-64242, `Docs/researches/chunks/subset-b-001712_research.md`
- `subset-b-001713`: lines 64243-66684, `Docs/researches/chunks/subset-b-001713_research.md`
- `subset-b-001714`: lines 66685-69052, `Docs/researches/chunks/subset-b-001714_research.md`
- `subset-b-001715`: lines 69053-71029, `Docs/researches/chunks/subset-b-001715_research.md`

## Chunk Research

### subset-b-001687: lines 1-2452

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 1-2452

## Scope

This chunk covers the opening 2,452 lines of the generated DCN 3.0.0 register shift/mask header. It defines preprocessor constants for register fields only; there are no C functions, structs, enums, or executable control paths in this slice. The paired offset header, `dcn_3_0_0_offset.h`, provides register addresses, while this file provides `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` constants used by AMD display register helper macros.

The slice contains roughly 2,170 `#define` entries plus the MIT SPDX line and header guard. The file continues after this chunk, so this report is intentionally partial and should be merged with later chunks for whole-file conclusions.

## Purpose

The purpose of this header slice is to encode the bit layout of DCN 3.0 display hardware registers in a form that driver code can consume safely through generated field access helpers. Instead of scattering literal shifts and masks across display, DMUB, IRQ, clock, and power-management code, the AMD driver includes this header and uses macros such as `FD_MASK(reg, field)`, `FD_SHIFT(reg, field)`, `REG_GET`, `REG_SET`, and `REG_UPDATE` to read, compose, and update memory-mapped register fields.

This chunk covers these major hardware areas:

- Legacy VGA/MMHUB display decode fields.
- DCCG clock generation, resync, DTO, pixel-rate, gating, reset, VSYNC-count, audio DTO, and perfmon fields.
- DCCG DFS `DENTIST_DISPCLK_CNTL` display-clock divider control.
- DC perfmon blocks 0 and 1 under DCCG.
- RBBMIF timeout/status/interrupt fields.
- DMU display power-gating domains and power transition interrupts.
- DMU perfmon block 2.
- DMU miscellaneous clock, memory power, SMU interrupt, and pipe disable fields.
- The start of DMCU microcontroller control, RAM access, firmware address/checksum, event, and interrupt status fields.

## Important APIs, Types, And Constants

There are no callable APIs or exported data objects. The exported interface is a generated macro namespace:

- `REGISTER__FIELD__SHIFT`: bit position for a hardware field.
- `REGISTER__FIELD_MASK`: bit mask for the same field.
- Register section comments such as `//VGA_RENDER_CONTROL` and `//DCCG_GATE_DISABLE_CNTL` group related field constants.
- Address-block comments such as `// addressBlock: dce_dc_dccg_dccg_dispdec` identify the IP block that owns the following registers.

Important field groups in this chunk include:

- VGA control and status: `VGA_MEM_WRITE_PAGE_ADDR`, `VGA_MEM_READ_PAGE_ADDR`, `VGA_RENDER_CONTROL`, `VGA_SEQUENCER_RESET_CONTROL`, `VGA_MODE_CONTROL`, `VGA_HDP_CONTROL`, `VGA_CACHE_CONTROL`, `D1VGA_CONTROL` through `D6VGA_CONTROL`, VGA interrupt status/clear/control, VGA indexed CRTC/SEQ/GRPH/DAC registers, and `VGA_SOURCE_SELECT`.
- Pixel clock and DTO controls: `PHYPLL[A-F]_PIXCLK_RESYNC_CNTL`, `DP_DTO_DBUF_EN`, `DSCCLK[0-5]_DTO_PARAM`, `DPPCLK[0-5]_DTO_PARAM`, `DP_DTO[0-5]_PHASE`, `DP_DTO[0-5]_MODULO`, `OTG[0-5]_PIXEL_RATE_CNTL`, and `OTG[0-5]_PHYPLL_PIXEL_RATE_CNTL`.
- DCCG timing and gating: `REFCLK_CNTL`, `DPREFCLK_CNTL`, `DISPCLK_FREQ_CHANGE_CNTL`, `DCCG_GATE_DISABLE_CNTL`, `DCCG_GATE_DISABLE_CNTL2`, `DCCG_SOFT_RESET`, `DCCG_DISP_CNTL_REG`, `DCCG_DS_*`, `DCCG_GTC_*`, `MILLISECOND_TIME_BASE_DIV`, and `MICROSECOND_TIME_BASE_DIV`.
- Perfmon layout: `DCCG_PERFMON_CNTL`, `DCCG_PERFMON_CNTL2`, `DC_PERFMON0_*`, `DC_PERFMON1_*`, and `DC_PERFMON2_*` define event selection, counter state, run/stop control, interrupt status/ack, and counter readback fields.
- Power management and interrupts: `DOMAIN0_PG_CONFIG` through `DOMAIN21_PG_STATUS` for selected domains, `DCPG_INTERRUPT_STATUS`, `DCPG_INTERRUPT_STATUS_2`, and `DCPG_INTERRUPT_CONTROL_[1-3]`.
- DMU/DMCU fields: `CC_DC_PIPE_DIS`, `DMU_CLK_CNTL`, `DMU_MEM_PWR_CNTL`, `DMCU_CTRL`, `DMCU_STATUS`, firmware address/checksum registers, ERAM/IRAM read-write controls, `DMCU_EVENT_TRIGGER`, `DMCU_UC_INTERNAL_INT_STATUS`, `DMCU_SS_INTERRUPT_CNTL_STATUS`, and the start of `DMCU_INTERRUPT_STATUS`.

## Control Flow

This chunk has no runtime control flow. Its effects are compile-time only:

1. The compiler preprocesses this header into C translation units that include it.
2. Driver register helper macros concatenate register and field names to resolve these `SHIFT` and `MASK` constants.
3. Runtime code performs the actual register reads/writes through helper macros and MMIO accessors in consumer files.

The visible ordering still matters for human and generator maintenance: the file is grouped by hardware address block and register, and each register generally lists all shifts first followed by all masks. Reordering does not usually affect C compilation, but it can make generated diffs harder to review and can hide mismatches between shift/mask pairs.

## State And Persistence Behavior

The header stores no software state and persists no data. It describes persistent hardware register state owned by the GPU display IP:

- VGA fields control compatibility display modes, VGA memory apertures, cache behavior, sequencer reset behavior, and legacy VGA interrupts.
- DCCG fields control clock selection, enablement, fractional divider/DTO settings, pixel-rate paths, clock gating, soft reset, and status counters. Incorrect values can persist in hardware until reset or until overwritten by the driver.
- Perfmon fields configure hardware counters and interrupt/ack behavior. Counter low/high fields expose sampled hardware state.
- DCPG/DMU fields describe display power-domain force-on/gate requests, desired power states, power FSM status, and power transition interrupt mask/clear bits.
- DMCU fields expose microcontroller reset/enable/status, firmware address metadata, RAM access, and interrupt sources.

Many interrupt status and clear fields intentionally share bit positions and masks, for example DMCU and DCCG VSYNC interrupt status/clear definitions. Consumers must understand whether a field is read-only status, write-one-to-clear, mask, or control based on the register programming model, not from the macro name alone.

## Dependencies And Integration Points

This header depends on generated naming compatibility with AMD's display register infrastructure. It is normally included together with:

- `sienna_cichlid_ip_offset.h` for base segment information.
- `dcn/dcn_3_0_0_offset.h` for register offsets.
- `dmub_reg.h`, `dm_services.h`, and DC register helper macros that build field metadata from `FD_MASK` and `FD_SHIFT`.

Observed direct consumers include:

- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`, which includes this header to populate `dmub_srv_dcn30_regs` common field arrays using `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)`.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c`, which reuses DCN 3.0 masks for closely related DMUB support.
- `drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c` and `irq/dcn302/irq_service_dcn302.c`, which include the DCN 3.0 offset and mask headers for IRQ-source register programming.
- Older amdgpu display/VGA paths such as `amdgpu/cik.c`, `amdgpu/vi.c`, `amdgpu/si.c`, `amdgpu/gmc_v6_0.c`, and `amdgpu/dce_v6_0.c` use shared VGA mask names including `VGA_RENDER_CONTROL__VGA_VSTATUS_CNTL_MASK`.

The file also integrates indirectly with DCN 3.0 clock, power, DMU, DMCU, perfmon, and debug code wherever generated register field tables are compiled from the macros in this header.

## Risks And Edge Cases

- A wrong bit mask or shift silently corrupts MMIO field access. The compiler will not detect a semantically wrong numeric value if the macro name exists.
- Missing or renamed fields can break generated register tables at compile time through unresolved macro concatenations.
- Cross-ASIC reuse is risky. Nearby DCN versions define similar names with different field sets, for example newer `OTG*_PIXEL_RATE_CNTL` layouts add status/source fields not present in this DCN 3.0.0 chunk.
- Some fields use the same bit for status and clear semantics. Accidentally using a clear macro in a read/modify/write path can acknowledge an interrupt unexpectedly.
- Large full-register masks such as `0xFFFFFFFFL` for DTO phase/modulo and counter readback require width-safe handling in callers.
- The legacy VGA block shares names with non-DCN amdgpu paths. A generated change here can affect code outside the immediate DC display tree.
- Power-gating and clock-gating fields can cause display hangs, blanking, or firmware communication failures if field definitions diverge from the hardware specification.
- This chunk ends in the middle of DMCU interrupt definitions. Whole-file analysis must reconcile the continuation before drawing final conclusions about DMCU interrupt coverage.

## Test Signals

Useful validation signals for this header are mostly build-time and hardware-integration oriented:

- Compile coverage for DCN 3.0/3.0.2 display and DMUB code, especially files that include `dcn_3_0_0_sh_mask.h`.
- Macro expansion checks for representative consumers using `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.
- Display bring-up on DCN 3.0 ASICs with modeset, hotplug, vblank, page flip, and DMUB firmware loading paths active.
- Clock programming tests covering DP DTOs, OTG pixel-rate controls, DPP/DSC DTOs, DISPCLK/DPPCLK changes, and PHYPLL pixel clock resync.
- Interrupt tests for vblank/vupdate, DMCUB outbox, power-domain transitions, DCCG VSYNC counter latches, and DMCU events.
- Power-management tests for display power gating, clock gating, static-screen interrupts, suspend/resume, and runtime display idle/deep-sleep behavior.
- Perf/debug tests that configure `DC_PERFMON0`, `DC_PERFMON1`, and `DC_PERFMON2`, verify counter activity, and acknowledge counter interrupts.

## Open Cross-Chunk Questions

- Later chunks must finish the DMCU interrupt and any remaining DCN register groups to determine whether this file is a complete generated mask set for every DCN 3.0.0 register block.
- Whole-file reconciliation should compare this header against `dcn_3_0_0_offset.h` to detect registers with offsets but missing field definitions, or fields without matching register offsets.
- If the repository has generated-header provenance scripts, the final report should identify the generator/source specification, because hand-editing this file would be high risk.

### subset-b-001688: lines 2453-4724

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 2453-4724

## Purpose

This chunk is generated AMDGPU DCN 3.0 register field metadata. It contains no executable C logic; its public surface is a large set of preprocessor constants that describe bit positions and masks for display-controller MMIO registers. Each field is represented by paired macros:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit position.
- `REGISTER__FIELD_MASK` gives the already-positioned bit mask.

The path is under a local `ceph-client` source mirror, but the content is AMD display-driver hardware metadata, not Ceph or distributed-filesystem code.

The range starts in the middle of the `DMCU_INTERRUPT_STATUS` field list and ends in the middle of `DISP_INTERRUPT_STATUS_CONTINUE21`. Within that span it covers DMCU/DMU interrupt status, host/uc enable masks, XIRQ/IRQ routing selectors, scratch and communication mailbox registers, DMCU perfmon and DPRX interrupt routing, continued DMCU interrupt banks for power-domain and DCIO DPCS events, DC GPU timer read/start-position registers, and the display interrupt status chain through continue bank 21.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or runtime storage objects in this range. The important API is the generated macro namespace consumed by AMD display register helpers such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_READ`, and `REG_WRITE`, together with the matching address macros from `dcn_3_0_0_offset.h`.

Major macro families in this chunk:

- `DMCU_INTERRUPT_STATUS`, `DMCU_INTERRUPT_STATUS_1`, `DMCU_INTERRUPT_STATUS_2`, and `DMCU_INTERRUPT_STATUS_CONTINUE`: sticky/ack-style DMCU interrupt status bits. These include ABM ready/backlight update events, microcontroller internal and register-read-timeout events, external software and SCP/MCP events, static-screen and vblank events, OTG range-timing updates, DCPG IHC domain power-up/power-down events for domains 0-21, and DCIO DPCS TXA-TXG interrupt bits.
- `DMCU_INTERRUPT_TO_HOST_EN_MASK`: host-visible enable bits for ABM0-ABM5 ready/backlight events plus selected SCP, UC internal, and UC register-read-timeout events.
- `DMCU_INTERRUPT_TO_UC_EN_MASK`, `_1`, `_2`, and `_CONTINUE`: routing enables for sending selected display events to the DMCU/DMU microcontroller, including ABM, static-screen, vblank, OTG range timing, domain power, DPRX, and DCIO DPCS events.
- `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL`, `_1`, `_CONTINUE`, and `_CONT2`: selectors that choose the interrupt line/type used when enabled events are routed to the microcontroller. Their bit layout mirrors the corresponding `*_TO_UC_EN_MASK*` banks.
- `DC_DMCU_SCRATCH`, `DMCU_INT_CNT`, and `DMCU_INT_CNT_CONT2` through `CONT5`: scratch data and per-ABM event counters, with 8-bit count fields for high-gain ready, local-slope ready, and backlight-update interrupts across ABM1-ABM5.
- `DMCU_FW_CHECKSUM_SMPL_BYTE_POS` and `DMCU_UC_CLK_GATING_CNTL`: firmware checksum sample-byte selectors and microcontroller IRAM/ERAM/RBBM read clock-gating controls.
- `MASTER_COMM_DATA_REG1-3`, `MASTER_COMM_CMD_REG`, `MASTER_COMM_CNTL_REG`, `SLAVE_COMM_DATA_REG1-3`, `SLAVE_COMM_CMD_REG`, and `SLAVE_COMM_CNTL_REG`: byte-granular communication/mailbox registers between host-side code and the display microcontroller, plus interrupt and in-progress bits.
- `DMCU_PERFMON_INTERRUPT_STATUS1-5`, `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK1-5`, and `DMCU_PERFMON_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1-5`: status, clear, enable, and routing macros for perfmon counter interrupts from DMU, DIO, DCCG, HUBP0-7, HUBBUB, DPP0-7, writeback, MMHUBBUB, MPC, OPP, OPTC, HDA, and DSC0-5.
- `DMCU_DPRX_INTERRUPT_STATUS1`, `DMCU_DPRX_INTERRUPT_TO_UC_EN_MASK1`, and `DMCU_DPRX_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1`: DisplayPort receiver stream, PHY, AUX, I2C, CPU, timeout, training, symbol, disparity, alignment, deskew, and sideband packet interrupt fields for the DPRX path.
- `DC_GPU_TIMER_START_POSITION_V_UPDATE`, `DC_GPU_TIMER_START_POSITION_VSTARTUP`, `DC_GPU_TIMER_READ`, and `DC_GPU_TIMER_READ_CNTL`: per-display GPU timer start-position selectors for vupdate/vstartup/vsync-nominal timing and a 32-bit timer readout selector.
- `DISP_INTERRUPT_STATUS` through `DISP_INTERRUPT_STATUS_CONTINUE21`: the main display interrupt status chain. It covers OPTC underflows, OTG snapshot/trigger/vsync/set-vtotal/vertical/vupdate/vstartup/vready/static-screen events, DIGA-DIGH DisplayPort fast-training and stream-disable events, HPD/HPD RX, AUX software and link-service done events, DMCU/ABM events, DMCU perfmon/DPRX/DCPG/DCIO continued banks, CRTC force-count/snapshot2, audio endpoint format/enabled/disabled events, AZ perfmon interrupts, DPCS IHC errors, I2C DDC hardware-done/read-request events, and continuation-link bits that chain one status register to the next.

The repeated suffixes and numbers are hardware-bank selectors, not software arrays. Consumers normally bind these names into register descriptor tables and let common register helper macros perform bit extraction and insertion.

## Control Flow

This header chunk has no control flow. It is declarative hardware layout data.

Runtime use follows this pattern:

1. DCN 3.0/3.0.2 code includes `dcn_3_0_0_offset.h` for addresses and this `dcn_3_0_0_sh_mask.h` file for shifts/masks.
2. Register-table initializers expand field names with macros such as `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)`.
3. Runtime code uses the resulting descriptors through `REG_GET`, `REG_UPDATE`, `REG_SET`, `REG_WRITE`, and related helpers to read, update, route, enable, clear, or acknowledge MMIO-backed display and DMCU state.
4. Interrupt code or firmware-facing paths read status banks, follow `*_CONTINUE*` chain bits, map asserted fields to IV source IDs, and clear or route events according to the relevant enable and XIRQ/IRQ selector masks.
5. DMUB/DMCU communication and diagnostics paths use the communication, scratch, counter, timer, and perfmon fields to exchange messages, profile display blocks, timestamp display events, or observe interrupt behavior.

The macros do not encode sequencing. Correct behavior depends on the caller knowing which registers are read-only status, writable control, write-one-to-clear status, sticky interrupt status, or self-clearing request bits.

## State And Persistence Behavior

The file stores no software state and persists nothing. It describes MMIO-backed GPU display hardware state.

The represented hardware state includes:

- DMCU/DMU interrupt state: occurred/clear bits for ABM, vblank, static-screen, OTG range-timing, power-domain, DPRX, DPCS, UC internal, SCP/MCP, and software events.
- Interrupt routing and masking state: host enable masks, microcontroller enable masks, and XIRQ/IRQ selector bits for the same interrupt families.
- Firmware and communication state: scratch register contents, byte-packed master/slave command and data registers, host/microcontroller interrupt bits, and message-in-progress indication.
- Diagnostics and counters: ABM event counters, perfmon counter interrupt status/clear bits, perfmon routing enables/selectors, DPRX status, and GPU timer read/start-position controls.
- Display interrupt aggregation state: chained display interrupt status banks for OPTC, OTG, DIG, HPD, AUX, I2C, audio, DPCS, DCPG, DMCU, ABM, and perfmon signals.
- Clock/power-adjacent control state: DMCU UC clock-gating read delays/enables and DCPG IHC power up/down events for many domains.

Persistence is defined by the hardware, not this header. Configuration fields such as enable masks, routing selectors, communication bytes, scratch data, and clock-gating controls normally remain until reprogrammed, reset, or lost through power gating. Event/status fields with names such as `*_OCCURRED`, `*_CLEAR`, `*_INT`, `*_STATUS`, `*_DONE`, `*_TIMEOUT`, and `*_CONTINUE` may be sticky, write-one-to-clear, read-only, edge-sensitive, or continuation indicators. Treating them as ordinary writable storage is risky without the corresponding register specification or caller-side helper contract.

## Dependencies And Integration Points

This chunk depends on the matching generated address header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`

Direct include points found in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c`

Those files include the DCN 3.0 offset and mask headers and build `dmub_srv_common_regs` tables by expanding `DMUB_COMMON_REGS()`, `DMCUB_INTERNAL_REGS()`, and `DMUB_COMMON_FIELDS()` through `REG_OFFSET`, `FD_MASK`, and `FD_SHIFT`. The chunk's DMCU/DMUB-adjacent communication and interrupt metadata is therefore part of the generated register contract available to DMUB service code, even when a given source file only references it through macro expansion rather than spelling every field name directly.

Related source-ID integration appears in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`, which documents several `DISP_INTERRUPT_STATUS_CONTINUE20` OTG static-screen, vupdate, GSL vsync-gap, vstartup, and vready fields as display interrupt source IDs. That header is not the register mask consumer itself, but it shows the semantic mapping between status-bank bits and the interrupt vectors surfaced to AMDGPU display IRQ handling.

The main consumers are hardware register helpers and firmware/display infrastructure rather than hand-written code in this header. The generated names must stay synchronized with DCN 3.0 register addresses, ASIC IP offsets such as `sienna_cichlid_ip_offset.h` and `dimgrey_cavefish_ip_offset.h`, DMUB register tables, display IRQ source tables, and firmware protocols that depend on DMCU/DMUB mailbox and interrupt behavior.

## Risks And Edge Cases

- These macros are a hardware ABI. Wrong shifts or masks usually compile successfully but read or write the wrong bit, causing missed interrupts, stale clears, interrupt storms, broken firmware communication, incorrect timer reads, bad perfmon routing, display underflow reporting failures, or pipe-specific display event loss.
- The range begins in the middle of `DMCU_INTERRUPT_STATUS` and ends before the complete `DISP_INTERRUPT_STATUS_CONTINUE21`/later continuation chain. Whole-file conclusions require adjacent chunks.
- Many status and clear fields deliberately share the same bit position and mask. Code that treats `*_CLEAR` as an independent field from `*_OCCURRED` can clear pending events unintentionally or fail to acknowledge them.
- Enable-mask and XIRQ/IRQ selector banks mirror status banks but are not interchangeable. Copying a field from `*_TO_UC_EN_MASK*` to `*_XIRQ_IRQ_SEL*`, or from the wrong continued bank, can silently route the wrong event.
- Chained display status banks rely on continuation bits such as `DISP_INTERRUPT_STATUS_CONTINUE*`. A wrong continuation mask can hide all later status registers or make software scan nonexistent banks.
- Repeated instance patterns create drift risk. ABM1-ABM5 counters, OTG1-OTG6 timing events, DCPG domain 0-21 power events, DPCS TXA-TXG bits, audio endpoint 0-7 bits, and DDC1-DDC6 fields are easy to misalign by one bit or one bank.
- Mailbox registers are byte-packed. Full-register writes or wrong byte masks can corrupt adjacent command/data bytes and desynchronize host-to-firmware or firmware-to-host messages.
- Interrupt status registers may be side-effect-sensitive. Read/modify/write sequences on write-one-to-clear fields can clear unrelated pending interrupts if the caller writes back a stale full-register value.
- Timer selector fields are shared packed controls. Wrong masks for `DC_GPU_TIMER_READ_CNTL` or start-position fields can return misleading timestamps and break diagnostics that depend on vupdate, vstartup, or vsync-nominal timing.
- Some field names include historical or generated spelling quirks such as `OCCURED` and `REUEST`. Renaming them for spelling cleanup would break macro consumers.

## Test Signals

Useful validation is compile-time plus hardware or simulator behavior:

- Build AMDGPU display and DMUB sources that include `dcn_3_0_0_sh_mask.h`; missing or renamed macros should fail in register table expansion through `FD_MASK`/`FD_SHIFT`.
- Diff this generated chunk against AMD's DCN 3.0 register database and adjacent DCN family headers to catch bit drift in DMCU, DPRX, perfmon, timer, and display interrupt status banks.
- Exercise DCN 3.0 or DCN 3.0.2 hardware with multiple active displays so OTG1-OTG6, HPD/AUX, vblank/vupdate/vstartup/vready, static-screen, and display underflow status paths are covered.
- Validate interrupt acknowledge behavior for `*_OCCURRED`/`*_CLEAR` pairs by checking that events clear once, do not clear unrelated bits, and do not retrigger as storms after handling.
- Test DMUB/DMCU communication paths that use master/slave command and data registers, including message-in-progress handling, interrupt signaling, firmware load/boot interactions, and timeout recovery.
- Exercise ABM/backlight events across ABM instances and verify high-gain ready, local-slope ready, and backlight-update counters/status bits.
- Run perfmon diagnostics for HUBP, HUBBUB, DPP, WB, DCCG, MMHUBBUB, MPC, OPP, OPTC, HDA, and DSC counters; confirm counter interrupt status, clear, enable, and routing selector behavior.
- Exercise DisplayPort/AUX/DPRX-related events where supported: MSA receive, VBID stream status toggles, vertical interrupts, SDP receive, PHY error thresholds, training errors, AUX/I2C/CPU interrupts, and message timeouts.
- Check GPU timer reads against expected display timing at vupdate, vstartup, and vsync-nominal positions for all active pipes.
- Monitor kernel logs and display diagnostics for missed hotplug/AUX completion, page-flip or vblank timeouts, underflow reports, audio endpoint event loss, firmware mailbox stalls, DPCS errors, power-domain interrupt anomalies, and pipe-specific regressions.

## Cross-Chunk Notes

Previous chunks of `dcn_3_0_0_sh_mask.h` define the earlier DCN 3.0 register field namespace and the beginning of `DMCU_INTERRUPT_STATUS` before line 2453. Later chunks continue after `DISP_INTERRUPT_STATUS_CONTINUE21`, including the rest of the display interrupt continuation chain and additional generated DCN 3.0 register masks. The final per-file research document should merge those chunks before making complete claims about the entire header.

### subset-b-001689: lines 4725-7166

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 4725-7166

## Purpose

This chunk is generated AMDGPU DCN 3.0 register field metadata. It contains no executable C logic; its API is a set of preprocessor constants that describe bit positions and already-shifted masks for DCN 3.0 display, DMU/DMCUB, MMHUBBUB/writeback, HDA audio, and display performance-monitor registers.

Each field is represented by paired macros:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit position.
- `REGISTER__FIELD_MASK` gives the positioned bit mask.

The path sits under a local `ceph-client` source mirror, but this content is AMD display-driver hardware metadata, not distributed filesystem logic.

The range starts with the tail of `DISP_INTERRUPT_STATUS_CONTINUE21`, then covers `DISP_INTERRUPT_STATUS_CONTINUE22` through `CONTINUE25`, GPU timer start-position fields, many interrupt-destination registers, the DMCUB/DMU register block, MMHUBBUB and display writeback register fields, the MMHUBBUB perfmon block, HDA/Azalia stream register fields, and the start of HDA perfmon4. It ends at the `DC_PERFMON4_PERFMON_CNTL` comment; that register's actual field definitions are in the next chunk.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or runtime storage objects in this range. The important surface is the generated macro namespace consumed by AMD display register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `REG_UPDATE`, `REG_READ`, `REG_WRITE`, `SF(...)`, `SRI(...)`, `DMUB_SF(...)`, and IRQ register-table helpers.

Major macro families in this chunk:

- `DISP_INTERRUPT_STATUS_CONTINUE22`, `CONTINUE23`, `CONTINUE24`, and `CONTINUE25`: packed display interrupt status continuation fields for DCPG power-domain up/down events, ABM ready/backlight-update events, OTG v-update-no-lock and DRR v-total events, DSC underflow/core-error/perfmon events, DMCUB timer/mailbox/general/fault events, MMHUBBUB warmup, and ABM2-5 events. Bit 31 continues the chained status register series until `CONTINUE25`.
- `DC_GPU_TIMER_START_POSITION_*`: per-pipe start-position selectors for vready, flip, v-update-no-lock, and flip-away GPU timer capture. Vready/v-update-no-lock cover D1-D6; flip/flip-away cover D1-D8.
- Interrupt destination registers: `DCCG_INTERRUPT_DEST`, `DMU_INTERRUPT_DEST`, `DMU_INTERRUPT_DEST2`, `DCPG_INTERRUPT_DEST`, `DCPG_INTERRUPT_DEST2`, `DCIO_INTERRUPT_DEST`, `DIO_INTERRUPT_DEST`, `HPD_INTERRUPT_DEST`, `DIG_INTERRUPT_DEST`, `DCHUB_INTERRUPT_DEST`, `DCHUB_PERFCOUNTER_INTERRUPT_DEST`, `DCHUB_INTERRUPT_DEST2`, `DPP_PERFCOUNTER_INTERRUPT_DEST`, `MPC_INTERRUPT_DEST`, `OPP_INTERRUPT_DEST`, `OPTC_INTERRUPT_DEST`, `OTG0_INTERRUPT_DEST` through `OTG5_INTERRUPT_DEST`, `I2C_DDC_HPD_INTERRUPT_DEST`, `AUX_INTERRUPT_DEST`, `AZ_INTERRUPT_DEST`, and `DSC_INTERRUPT_DEST`. These fields route block-specific interrupt sources to the intended interrupt destination path.
- `dce_dc_dmu_dmcub_dispdec` address block: DMCUB region offsets/top-address enables, region3 code-window base/top/offset registers for windows 0-7, DMCUB interrupt enable/ack/status/type registers, external interrupt count/id/context/ack, instruction/data fault addresses, security and memory controls, inbox/outbox base/size/read/write pointers for two mailboxes, GPINT data in/out registers, scratch0-15, timer current/trigger/window registers, processor ID, control, low-speed wake enable, and memory power control.
- `dce_dc_mmhubbub_mcif_wb0_dispdec` address block: MCIF writeback buffer manager status/SW/VCE controls, pitch, four writeback buffer status/status2 groups, luma/chroma low/high addresses, buffer resolution, arbitration, SCLK/DRAM/P-state/self-refresh controls, QoS, luma/chroma size, VMID, and minimum time-to-urgent fields.
- `dce_dc_mmhubbub_mmhubbub_dispdec` and `dce_dc_mmhubbub_vgaif_dispdec`: MMHUBBUB watermarks and warmup programming, WBIF watermark-control/misc/outstanding counters, VGA source split, memory power status/control, clock gating, soft reset, DMU interface error status, client unit IDs, warmup VMID, VGAIF MCIF latency/write-combine controls, and outstanding counters.
- `DC_PERFMON3_*`: MMHUBBUB display perfmon control, counter configuration, counted-value type, hardware stop/count-off selection, per-counter state selection, perfmon run/control/interrupt/ack fields, counter value low/high fields, and read selectors.
- `AZF0STREAM0_*` through `AZF0STREAM7_*` and `AZ_CLOCK_CNTL`: HDA/Azalia stream indirect index/data fields and Azalia clock-gating/test-clock fields.
- `DC_PERFMON4_PERFCOUNTER_CNTL`, `DC_PERFMON4_PERFCOUNTER_CNTL2`, and `DC_PERFMON4_PERFCOUNTER_STATE`: start of the HDA perfmon block, covering counter event selection, value selection, increment/run/interrupt controls, count-off fields, active status, counted-value type, hardware stop selectors, and eight counter state selectors. The following `DC_PERFMON4_PERFMON_CNTL` register is only introduced by comment at the chunk boundary.

## Control Flow

This header chunk has no control flow. It is declarative hardware layout data used by code that builds register descriptor tables and performs MMIO read-modify-write operations.

Runtime use follows this pattern:

1. DCN 3.0 display code includes `dcn_3_0_0_offset.h` for register addresses and `dcn_3_0_0_sh_mask.h` for field masks/shifts.
2. Resource, IRQ, GPIO, DMUB, clock-manager, MMHUBBUB, DWB, and audio/perfmon code expands these generated names through register-list macros.
3. IRQ code uses the interrupt status and destination fields to enable, route, report, and acknowledge display, DMU/DMCUB, OTG, DSC, DCHUB, HPD, AUX, I2C, Azalia, and perfmon events.
4. DMUB code programs DMCUB memory windows, mailbox pointers, GPINT registers, scratch registers, timers, interrupts, fault handling, and power controls.
5. MMHUBBUB/DWB code programs display writeback buffer addresses, pitch, size, resolution, buffer status/control, watermark/QoS behavior, VMID, and power/clock controls.
6. Perfmon/debug paths configure perf counters, start/stop counter collection, read low/high counter values, and clear or inspect perf counter interrupt status.

The macros do not encode sequencing. Consumers must know whether a field is read-only status, write-one-to-clear ack, sticky fault state, self-clearing request, or persistent configuration.

## State And Persistence Behavior

The header stores no software state and persists nothing. It describes MMIO-backed GPU display hardware state.

The represented hardware state includes:

- Interrupt state and routing: chained interrupt status bits, DMCUB interrupt enables/types/acks/status, destination routing for display sub-blocks, and perfmon interrupt status/ack fields.
- DMCUB firmware interface state: memory region windows and enables, mailbox base/size/read/write pointers, GPINT input/output registers, scratch registers, timers, processor/control status, fault addresses, security reset/fault-clear bits, and memory power controls.
- Display writeback and MMHUBBUB state: buffer manager status, buffer locks, active/overflow/disable/mode/tag/current-line status, luma/chroma addresses and high bits, buffer resolution, pitch, buffer sizes, VCE/SW controls, p-state/watermark/self-refresh/QoS settings, VMID, outstanding counters, warmup address/config/control, clock gates, soft reset, and memory power state.
- Timing and diagnostic state: GPU timer start-position selectors for vready/flip/v-update-no-lock/flip-away, MCIF latency/write-combine counters, perfmon counter control/state/value/interrupt fields, and MMHUBBUB/DCHUB/DPP/DSC perf counter destination fields.
- HDA/Azalia state: per-stream indirect index/data windows and clock gate/test-clock controls for the display audio block.

Persistence is hardware-defined. Configuration fields usually remain until overwritten, power-gated, reset, or reinitialized during modeset, suspend/resume, or ASIC reset. Status, ack, fault-clear, interrupt, and pointer fields are side-effect-sensitive. Names containing `*_STATUS`, `*_STAT`, `*_ACK`, `*_CLEAR`, `*_FAULT`, `*_WPTR`, `*_RPTR`, `*_ACTIVE`, `*_LOCKED`, `*_OVERRUN`, `*_PWR_STATUS`, or `*_SOFT_RESET` should be treated as requiring hardware-specific access discipline.

## Dependencies And Integration Points

The direct generated companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`, which supplies matching register addresses and base indices. This file supplies only the bit layouts inside those addresses.

Direct include points for `dcn_3_0_0_sh_mask.h` in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c`

Close consumers visible in the tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c`, which binds DMCUB interrupt registers and fields through IRQ register-entry macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c` and `dmub_dcn302.c`, which use the DMCUB register contract for firmware mailbox, GPINT, interrupt, scratch, and control paths.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_mmhubbub.c` and `dcn30_mmhubbub.h`, which program MCIF writeback buffer addresses, high address bits, and other MMHUBBUB/DWB fields using these masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`, which documents interrupt source IDs that correspond to several status names in this chunk, including DMCUB mailbox events under `DISP_INTERRUPT_STATUS_CONTINUE24`.

## Risks And Edge Cases

- These macros are a hardware ABI. Wrong masks or shifts compile successfully but can route interrupts incorrectly, miss acknowledgements, corrupt mailbox pointers, program wrong DMCUB memory windows, break display writeback, or produce misleading perf counter reads.
- The chunk boundaries are artificial. The first lines are only the tail of `DISP_INTERRUPT_STATUS_CONTINUE21`, and the last line is only the `DC_PERFMON4_PERFMON_CNTL` comment before that register's field definitions.
- Repeated fields create copy-drift risk. OTG0-5, AZF0STREAM0-7, MCIF writeback buffers 1-4, DMCUB region3 code windows 0-7, ABM2-5, DSC0-5, DPP0-7, HUBP0-7, and perf counter 0-7 fields are highly similar but not always semantically interchangeable.
- Packed interrupt registers require read-modify-write and ack discipline. Full-register writes to destination, enable, status, type, or ack registers can affect unrelated interrupt sources in the same word.
- DMCUB region and mailbox fields are firmware-interface critical. Bad base, top, offset, size, `WPTR`, or `RPTR` masks can hang DMUB communication, fault instruction/data fetches, or cause firmware-visible memory corruption.
- Fault and security fields are side-effect-sensitive. Misusing `DMCUB_SEC_RESET`, fault clear bits, fault address reads, or data fault interrupt disables can hide real firmware/memory bugs or leave the block wedged after a fault.
- Writeback address fields are split into low/high luma/chroma addresses. Mixing buffers, planes, or high-bit fields can write captured frames to the wrong memory, corrupt output, or violate VMID/protection expectations.
- Watermark, QoS, P-state, self-refresh, and clock-gating fields are workload-sensitive. Bad masks can appear only under high resolution, high refresh, display writeback, low memory-clock, suspend/resume, or multi-display stress.
- Destination fields do not by themselves define interrupt source IDs or Linux IRQ handlers. The driver must keep routing bits, source ID tables, enable/ack registers, and handler expectations aligned.

## Test Signals

Useful validation is compile-time plus hardware behavior:

- Build AMDGPU/DC with DCN 3.0 and DCN 3.0.2 support; missing or renamed macros should fail at include sites and in generated IRQ, DMUB, GPIO, clock, resource, MMHUBBUB, and DWB register tables.
- Diff this generated chunk against AMD's DCN 3.0 register database and the adjacent `dcn_3_0_0_offset.h` addresses to catch shifted fields, stale masks, or instance drift.
- Exercise DCN 3.0 hardware with hotplug, modeset, vblank, page flip, DRR, vstartup/vready, v-update-no-lock, DSC, ABM, AUX, I2C/DDC, HPD, and Azalia audio interrupt activity. Watch for missed IRQs, IRQ storms, and wrong destination routing.
- Stress DMUB communication: firmware boot, inbox/outbox messages, GPINTs, scratch access, timers, suspend/resume, fault injection where available, and recovery after undefined-address or instruction/data fault events.
- Test display writeback through `dcn30_mmhubbub`: program all four buffers, luma/chroma addresses, high address bits, resolution, pitch, buffer locking, VCE/SW ownership, overflow/overrun reporting, and VMID behavior.
- Run bandwidth and power-state stress with writeback enabled: memory-clock changes, NB p-state changes, watermark updates, self-refresh, clock gating, MMHUBBUB warmup, and low-power transitions. Watch for underflow, stale frames, corruption, and resume failures.
- Use perfmon/debug tooling to configure `DC_PERFMON3` and the visible portion of `DC_PERFMON4`, start/stop counters, read low/high values, and verify interrupt status/ack behavior.

## Cross-Chunk Notes

Adjacent earlier chunks define the beginning of `DISP_INTERRUPT_STATUS_CONTINUE21`; this chunk starts at its final mask lines. Adjacent later chunks define the actual `DC_PERFMON4_PERFMON_CNTL` fields and the rest of the HDA perfmon4 block. The final per-file research document should merge these boundaries before making complete claims about either register family.

### subset-b-001690: lines 7167-9804

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 7167-9804

## Scope

This chunk is part of the generated AMD DCN 3.0.0 ASIC register shift/mask header. It covers lines 7167-9804 and contains 2,055 `#define` entries: 1,030 `__SHIFT` constants and 1,025 `_MASK` constants across 483 distinct register names. There are no C functions, structs, enums, storage objects, or executable branches; the API surface is the generated macro namespace used by AMDGPU Display Core register helper code.

The slice starts in the tail of `DC_PERFMON4_PERFMON_CNTL` after the matching `DC_PERFMON4_PERFCOUNTER_*` fields from the prior chunk, and it ends at the beginning of `DC_PERFMON6_PERFCOUNTER_CNTL`. The final per-file report should merge adjacent chunks before treating performance-monitor instances 4 and 6 as complete.

## Purpose

The purpose of this chunk is to map DCN 3.0.0 display/audio register fields to exact bit positions and positioned masks. Runtime code combines these constants with register offsets from `dcn_3_0_0_offset.h` and register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, and field-list symbol-pasting helpers.

Major hardware surfaces represented here are:

- Display performance monitor tails and instances: the end of `DC_PERFMON4`, the full `DC_PERFMON5` block for DCHUBBUB, and the start of `DC_PERFMON6` for HUBP0.
- Display HDA/Azalia audio: codec endpoint index/data windows for endpoints 0-7, input endpoints 0-7, stream index/data windows for streams 8-15, controller DMA/cache/clock/DTO controls, CRC/debug registers, codec root/function parameters, power/reset controls, port connectivity, and GTC group offsets.
- DCHUBBUB SDPIF/return/hubbub blocks: request credit/status, VM physical request controls, forced-I/O status capture, framebuffer/AGP/HBM aperture registers, per-pipe security levels for DCC metadata/cursor/GPUVM/surface/DMDATA, DCC return constants, CRC controls/results, arbitration watermarks, DRAM-state timing, global timer, timeout detection, soft reset, clock controls, surface-check registers, VTG controls, and FMON controls.
- VM request interface: `DCN_VM_CONTEXT0` through `DCN_VM_CONTEXT15` page-table control/base/start/end fields, default address fields, and VM fault control/status/address fields.
- HUBP0/HUBPREQ0/HUBPRET0: surface format, tiling, viewport, request sizing, enable/blank/underflow/timeout, clock and measurement windows, pitch, VMID, luma/chroma primary/secondary surface and metadata addresses, DCC/TMZ control, flip control/interrupt/in-use tracking, TTU/QoS/vblank/flip/nominal timing, prefetch, cursor request timing, memory power control/status, return-path read-line windows, vblank/read-line interrupts, and read-line status.
- Cursor and DMDATA for pipe 0: cursor enable/mode/pitch/address/size/position/hotspot/stereo/destination offset, cursor memory power, DMDATA address attributes, QoS, underflow/done status, and software DMDATA injection.

Although the repository path is under a `ceph-client` source mirror, this source slice is AMD GPU display/audio register metadata. It does not implement Ceph filesystem logic, distributed storage behavior, or filesystem persistence.

## Important API Surface

The exported interface is the generated two-macro pattern:

- `<REGISTER>__<FIELD>__SHIFT`: low bit number for the field.
- `<REGISTER>__<FIELD>_MASK`: already-positioned bit mask for the same field.

Important macro families in this chunk include:

- `DC_PERFMON4_*`, `DC_PERFMON5_*`, and the first `DC_PERFMON6_PERFCOUNTER_CNTL` fields for event selection, counted-value selection, increment/run-enable modes, counter state, monitor clocking, current-value interrupt status/ack, and high/low counter readback.
- `AZF0ENDPOINT*`, `AZF0INPUTENDPOINT*`, and `AZF0STREAM8` through `AZF0STREAM15` index/data macros for indirect Azalia endpoint, input endpoint, and stream register access.
- `AZALIA_*` controller fields for clock gating, audio DTO, SOCCLK deep-sleep exit, DMA snoop/isochronous attributes, RIRB/DP/CORB DMA behavior, cyclic buffer position/sync, payload capabilities, stream arbiter latency, input/output CRC controls/results, memory power, codec parameters, codec power/reset, converter synchronization, port connectivity, and GTC offsets.
- `DCHUBBUB_SDPIF_*`, `VM_REQUEST_PHYSICAL`, `DCHUBBUB_FORCE_IO_STATUS_*`, `DCN_VM_FB_*`, `DCN_VM_AGP_*`, `DCN_VM_LOCAL_HBM_*`, and per-pipe `DCHUBBUB_SDPIF_PIPE_*_SEC_LVL` fields for display hub memory access, security level tagging, and aperture setup.
- `DCHUBBUB_RET_PATH_DCC_CFG*`, `DCHUBBUB_CRC_*`, `DCHUBBUB_ARB_*`, `DCHUBBUB_TIMEOUT_*`, `DCHUBBUB_CLOCK_CNTL`, `DCFCLK_CNTL`, `VTG*_CONTROL`, and `FMON_CTRL*` for compression return constants, CRC validation, arbitration/watermark programming, clock/reset behavior, timeout interrupts, vertical timing generator control, and fabric-monitor diagnostics.
- `DCN_VM_CONTEXT[0-15]_*`, `DCN_VM_DEFAULT_ADDR_*`, and `DCN_VM_FAULT_*` for display VM page-table layout, logical page range limits, default-address behavior, and fault status/address capture.
- `HUBP0_DCSURF_*`, `HUBP0_DCHUBP_*`, and `HUBP0_HUBP_*` for surface format/rotation/alpha, tiling, viewport, request chunk sizing, blank/disable/underflow/timeout state, clock gating/readback, VMPG configuration, and DCFCLK/DPPCLK performance windows.
- `HUBPREQ0_DCSURF_*`, `HUBPREQ0_DCN_*`, `HUBPREQ0_PREFETCH_*`, `HUBPREQ0_VBLANK_*`, `HUBPREQ0_FLIP_*`, `HUBPREQ0_NOM_*`, and `HUBPREQ0_PER_LINE_DELIVERY*` for scanout address programming, DCC/TMZ surface controls, frame-boundary flip sequencing, request timing, and QoS.
- `HUBPRET0_HUBPRET_*` for return-path detile/ROB/CDC memory power, read-line interval/window programming, vblank/read-line interrupt mask/type/clear/status fields, and current read-line readback.
- `CURSOR0_0_*` for cursor fetch/display state and DMDATA transport.

Generated names that end in repeated words, such as `*_MASK_MASK`, are expected when the hardware field itself is named `MASK` and the generated suffix also denotes a mask constant.

## Control Flow

This header chunk has no local control flow. The runtime sequence is supplied by Display Core and DMUB code that includes the DCN 3.0.0 offset and mask headers, builds per-block register tables, and then writes or reads fields through MMIO helpers.

Typical external flow is:

1. DCN30 resource, IRQ, clock, GPIO, and DMUB sources include `dcn_3_0_0_offset.h` and `dcn_3_0_0_sh_mask.h`.
2. Block-specific field-list macros paste names from this header into shift/mask tables for HUBBUB, HUBP, DPP/cursor, IRQ, clock-manager, and DMUB register access.
3. Modeset and plane programming paths write HUBP/HUBPREQ/HUBPRET surface, viewport, tiling, DCC/TMZ, VMID, timing, flip, cursor, and memory-power fields.
4. Clock and power paths program DCHUBBUB/HUBP/Azalia clock gates, memory power controls, and status polling.
5. IRQ/debug paths enable, query, and clear flip, vblank, read-line, timeout, CRC, fault, underflow, and performance-monitor state.

Ordering constraints are implicit. Callers must coordinate update locks, flip timing, VM page-table/aperture setup, address high/low pairs, DCC metadata, security/TMZ bits, interrupt clear bits, and memory power transitions in the sequence required by the hardware.

## State And Persistence Behavior

The file itself stores no state. The macros describe memory-mapped hardware state that persists in DCN 3.0.0 display/audio blocks while those blocks remain powered and programmed.

Persistent or semi-persistent hardware state represented here includes:

- Azalia audio controller, endpoint, stream, DMA, payload, DTO, CRC, codec power/reset, and connectivity configuration.
- DCHUBBUB aperture, security-level, DCC return, arbitration watermark, DRAM-state, timeout, FMON, CRC, clock, and reset state.
- VM context page-table base/start/end configuration, default addresses, and fault status/address capture.
- HUBP0 surface format, tiling, viewport, request sizing, clocking, blank/disable state, timeout and underflow state.
- HUBPREQ0 surface pitch, luma/chroma and metadata addresses, DCC/TMZ controls, VMID, flip locks/pending/interrupts, in-use/earliest-in-use readbacks, TTU/QoS, vblank/flip/nominal timing, prefetch, and request memory power state.
- HUBPRET0 return path control, memory power, read-line windows, read-line/vblank interrupts, and read-line status.
- Cursor and DMDATA address, format, position, QoS, software data, underflow, and memory power state.
- Performance-monitor counter state, thresholds, interrupt status/ack, and readback values.

Many fields are not ordinary configuration values. Fields named `STATUS`, `CLEAR`, `ACK`, `PENDING`, `INUSE`, `FAULT`, `UNDERFLOW`, or `*_INT_*` can be live readback, sticky state, write-one-to-clear, or edge-sensitive control depending on the hardware register. This header encodes bit layout only; it does not encode access type, reset value, latch timing, or legal programming sequences.

## Dependencies And Integration Points

This chunk depends on the DCN 3.0.0 register contract and is meaningful only with the matching register offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`
- AMD Display Core register helper infrastructure that turns register and field names into shift/mask table entries.

Observed local include points for this header include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c`

Other integration points are the generic HUBBUB/HUBP/DPP/cursor and DMUB command definitions. For example, cursor fields from `CURSOR0_0_CURSOR_CONTROL` are represented in `display/dc/dpp/dcn30/dcn30_dpp.h` and `display/dmub/inc/dmub_cmd.h`, while DCHUBBUB arbitration watermarks are used through HUBBUB field tables in display hub code.

Cross-generation headers such as `dcn_3_2_0_sh_mask.h`, `dcn_3_5_1_sh_mask.h`, and `dcn_4_1_0_sh_mask.h` contain similar names but not always identical fields. Copying masks or assumptions between generations is risky; for example, later cursor control blocks add fields not present in this DCN 3.0.0 slice.

## Risks And Edge Cases

- Wrong shifts or masks compile cleanly but can silently program the wrong display/audio bits. Highest-risk fields include VM page-table bases/ranges, default/fault addresses, surface and metadata addresses, DCC/TMZ enables, DMA snoop/isochronous attributes, flip controls, interrupt clears, memory power controls, and clock/reset fields.
- Chunk boundaries split related performance-monitor blocks. `DC_PERFMON4` is incomplete at the start of this slice and `DC_PERFMON6` is incomplete at the end, so isolated reasoning can miss counter-control fields.
- Address fields are split across low 32-bit and high narrow masks, often 16-bit or 4-bit high fragments. Treating high and low halves uniformly can truncate physical, metadata, VM, cursor, DMDATA, or fault addresses.
- Repeated instance/index windows are easy to mix up. Azalia endpoints/input endpoints, stream 8-15 windows, VM contexts 0-15, VTG0-5 controls, DCC constant pairs, and pipe security-level fields rely on exact prefix matching.
- Status, clear, ack, and interrupt-mask fields frequently share registers. Generic read-modify-write sequences can accidentally acknowledge events, clear sticky status, or fail to clear an event if the mask is stale.
- HUBP/HUBPREQ/HUBPRET timing fields are tightly packed and mode-sensitive. Bad request sizing, TTU, prefetch, vblank, flip, nominal, per-line delivery, read-line, or watermark values can produce underflow, timeout, tearing, missed flips, or display blanking only under specific modes.
- VM and security fields interact with GPUVM, HostVM, TMZ, DCC metadata, cursor, and DMDATA fetches. Incorrect fields may surface as page faults, protected-content failures, corrupted scanout, or forced-I/O status captures rather than simple validation errors.
- Azalia DMA and clock/power fields affect audio stream delivery and power transitions. Incorrect values can cause underflow filler behavior, lost interrupts, bad payload reporting, or audio dropouts.
- Full-width masks such as `0xFFFFFFFFL` should stay inside existing 32-bit register helper paths to avoid signedness or width surprises in ad hoc code.

## Test Signals

Useful validation signals for code that consumes this chunk include:

- Build coverage for DCN30/DCN302 Display Core and DMUB sources that include `dcn_3_0_0_sh_mask.h`.
- Static generated-header validation that every intended field has matching `__SHIFT` and `_MASK` definitions, masks align with shifts and field widths, and repeated families remain consistent where the hardware spec requires it.
- Diff checks against the authoritative DCN 3.0.0 register database and the matching `dcn_3_0_0_offset.h`, especially around the `DC_PERFMON4` and `DC_PERFMON6` chunk boundaries.
- Modeset and multi-plane tests on DCN 3.0 hardware with luma/chroma formats, DCC-enabled surfaces, TMZ-protected surfaces, metadata address changes, rotations/mirroring, alpha-plane state, and viewport changes on HUBP0.
- Flip tests covering update locks, immediate and vupdate-synchronized flips, pending/min-time behavior, triple-buffer/GSL bits, in-use/earliest-in-use readbacks, and flip/flip-away interrupt status/clear handling.
- VM tests that exercise multiple VMIDs and contexts, page-table ranges, default-address behavior, display VM faults, forced-I/O status capture, HostVM/security levels, and protected cursor/DMDATA/surface fetches.
- HUBBUB watermark, DRAM-state, timeout, soft-reset, clock-gating, memory-power, suspend/resume, and runtime power-management tests that verify status bits converge and no underflow/timeout bits remain stuck.
- Cursor and DMDATA tests for movement, hotspot, size, stereo offsets, TMZ/system/snoop attributes, software DMDATA injection, QoS, underflow clear, and memory power transitions.
- Azalia/HD-audio tests for stream setup, DMA snoop/isochronous configuration, cyclic buffer position/sync, payload capability reporting, codec power/reset, DTO programming, CRC/debug readback, and audio through suspend/resume.
- Diagnostic tests for DCHUBBUB and Azalia CRC, FMON, DC performance monitors, timeout interrupts, vblank/read-line interrupts, and surface-check registers.

## Chunk Notes

This is generated register metadata rather than functional logic. The main research value is the hardware coverage map and risk profile: display audio control, DCHUBBUB memory/VM/arbitration/security, HUBP0 scanout and flip sequencing, return-path/read-line interrupts, cursor/DMDATA fetches, and performance diagnostics. The merge lane should combine this with neighboring chunks before presenting complete per-file coverage for `dcn_3_0_0_sh_mask.h`.

### subset-b-001691: lines 9805-12287

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 9805-12287

## Scope

This chunk is generated AMD DCN 3.0.0 register field metadata. It contains 2,112 `#define` entries in the visible range: 1,054 `__SHIFT` constants and 1,058 `_MASK` constants. There are no C functions, structs, enums, variables, or executable branches in this file slice; its API is the generated preprocessor namespace that maps display-controller register fields to bit positions and already-shifted bit masks.

The path is under a local `ceph-client` source mirror, but this source is AMDGPU display hardware metadata, not Ceph or distributed filesystem logic.

The chunk starts inside the `DC_PERFMON6_PERFCOUNTER_CNTL` register definition, after earlier fields from that register have already appeared in the previous chunk. It then covers:

- The remainder of `DC_PERFMON6_*` perfmon control/state/value fields.
- HUBP/HUBPREQ/HUBPRET/CURSOR instance 1 field masks and shifts.
- Complete `DC_PERFMON7_*` definitions.
- HUBP/HUBPREQ/HUBPRET/CURSOR instance 2 field masks and shifts.
- Complete `DC_PERFMON8_*` definitions.
- HUBP instance 3 and the first part of HUBPREQ instance 3, ending at `HUBPREQ3_BLANK_OFFSET_0__REFCYC_H_BLANK_END_MASK`.

Because the first and last register families are partial, whole-file conclusions for `DC_PERFMON6_PERFCOUNTER_CNTL` and `HUBPREQ3` must be reconciled with adjacent chunks.

## Purpose

The purpose of this header range is to let AMD display code program DCN 3.0.0 hardware registers symbolically. Each field is represented by a pair:

- `REGISTER__FIELD__SHIFT`: the field's least-significant bit position.
- `REGISTER__FIELD_MASK`: the field's already-positioned register mask.

Runtime code combines these constants with the matching generated address header, `dcn_3_0_0_offset.h`, and AMD display register helpers such as `REG_SET`, `REG_SET_2`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, `SRI(...)`, and `HUBP_SF(...)`. The constants in this chunk are therefore part of the DCN 3.0.0 register ABI used by plane programming, page flips, cursor programming, VM/TLB setup, memory power control, interrupt handling, and display performance monitoring.

## Important API Surface

The major macro groups are:

- `DC_PERFMON6_*`, `DC_PERFMON7_*`, and `DC_PERFMON8_*`: display performance counter control and status fields. These include event selection, counted-value selection, increment mode, hardware control selection, run enable mode, count-off and restart controls, interrupt enable/status/ack fields, counter active/state fields for counters 0-7, global perfmon state/report count, clock/run-enable controls, counter value low/high fields, and read selector fields.
- `HUBP1_*`, `HUBP2_*`, and `HUBP3_*`: hub pipe surface metadata. These define surface pixel format, rotation, horizontal mirror, alpha plane enable, address configuration, tiling/swizzle mode, primary and secondary viewport start/dimensions for luma and chroma planes, request size programming, HUBP blank/disable/underflow state, clock control, virtual memory page config, and DCFCLK/DPPCLK measurement-window fields.
- `HUBPREQ1_*`, `HUBPREQ2_*`, and visible `HUBPREQ3_*`: hub request path fields for scanout memory fetches. These include luma/chroma pitch, VMID, primary and secondary surface addresses, metadata addresses, DCC and TMZ controls, flip control, flip interrupts, in-use and earliest-in-use address reporting, expansion mode, TTU/QoS programming, VM aperture and L1 TLB controls, blanking/scaler/prefetch timing, vblank and flip timing, nominal PTE/meta-row timing, per-line delivery, cursor request settings, reference-frequency conversion, destination-Y request limits, and request-side memory power control/status.
- `HUBPRET1_*` and `HUBPRET2_*`: hub return path fields for DET buffer plane base addresses, component crossbar selection, pack control, return memory power control/status, read-line control/value/status, and HUBPRET interrupt mask/type/status/ack fields.
- `CURSOR0_1_*` and `CURSOR0_2_*`: cursor and display metadata fields for cursor enable/mode/pitch, magnification, line chunking, alpha and color controls, cursor surface address, size, position, hot spot, stereo control, destination offset, cursor memory power state, DMDATA address, DMDATA mode/update/repeat/size, QoS control, completion/error status, and software DMDATA writes.

Important examples include:

- `HUBP1_DCSURF_SURFACE_CONFIG__SURFACE_PIXEL_FORMAT__SHIFT` / `_MASK`, `HUBP2_DCSURF_TILING_CONFIG__SW_MODE__SHIFT` / `_MASK`, and `HUBP3_DCSURF_ADDR_CONFIG__NUM_PKRS__SHIFT` / `_MASK` for plane format, tiling, and address layout.
- `HUBPREQ1_DCSURF_PRIMARY_SURFACE_ADDRESS*`, `HUBPREQ2_DCSURF_PRIMARY_META_SURFACE_ADDRESS*`, and matching `_C` chroma macros for split low/high luma, chroma, and metadata addresses.
- `HUBPREQ*_DCSURF_SURFACE_CONTROL__PRIMARY_SURFACE_DCC_EN`, `*_SECONDARY_SURFACE_DCC_EN`, `*_TMZ`, and metadata TMZ fields for compressed and trusted-memory scanout behavior.
- `HUBPREQ*_DCSURF_FLIP_CONTROL`, `HUBPREQ*_DCSURF_FLIP_CONTROL2`, and `HUBPREQ*_DCSURF_SURFACE_FLIP_INTERRUPT` for update locking, flip type, stereo sync, pending status, GSL, triple buffering, interrupt mask/type/status, and clear fields.
- `HUBPREQ*_DCN_DMDATA_VM_CNTL`, `HUBPREQ*_DCN_VM_SYSTEM_APERTURE_*`, and `HUBPREQ*_DCN_VM_MX_L1_TLB_CNTL` for DMDATA VM timing/status and display VM/TLB setup.
- `CURSOR0_*_DMDATA_*` for metadata packet programming attached to a cursor/plane pipe.

## Control Flow

There is no local control flow. The chunk is declarative register-layout data used by external driver code.

The runtime flow that consumes these constants is:

1. DCN 3.0 resource and block constructors include `dcn_3_0_0_offset.h` and `dcn_3_0_0_sh_mask.h`.
2. Register-list macros such as `HUBP_REG_LIST_DCN30(id)` bind per-instance MMIO addresses with generated symbols like `HUBP1_*`, `HUBPREQ1_*`, `HUBPRET1_*`, and `CURSOR0_1_*`.
3. Mask/shift table macros such as `HUBP_MASK_SH_LIST_DCN30(__SHIFT)` and `HUBP_MASK_SH_LIST_DCN30(_MASK)` paste register and field names through `HUBP_SF(...)` into `struct dcn_hubp2_shift` and `struct dcn_hubp2_mask`.
4. HUBP runtime code programs VM apertures, TLB controls, surface addresses, metadata addresses, DCC/TMZ bits, flip type, stereo flip state, cursor state, and timing/QoS controls with `REG_SET*` and `REG_UPDATE*` helpers.
5. IRQ service code builds page-flip interrupt entries with `SRI(HUBPREQ, id, DCSURF_SURFACE_FLIP_INTERRUPT)` and generated `SURFACE_FLIP_INT_MASK` / `SURFACE_FLIP_CLEAR` fields.
6. DMUB, resource, GPIO, clock manager, and IRQ paths include the same generated mask/offset pair so firmware-facing and display-manager paths use one register contract.

The generated masks do not encode sequencing. Consumers must still enforce hardware ordering, for example writing address high words before low words for latching, using surface update locks correctly, enabling clocks before MMIO access, and acknowledging sticky interrupt/status bits in the required manner.

## State And Persistence Behavior

The header itself stores no software state and persists nothing. It describes MMIO-backed GPU display state.

Hardware state represented by this chunk includes:

- Plane interpretation state: pixel format, alpha plane enable, rotation, mirror, tiling mode, address configuration, viewport coordinates, viewport dimensions, request size, and swath/PTE/meta chunk sizing.
- Scanout memory state: luma and chroma primary/secondary surface addresses, metadata surface addresses, address high words, VMID, VM system aperture, L1 TLB enable and access mode, and in-use/earliest-in-use address snapshots.
- Compression and protection state: DCC enable, independent block sizing, TMZ bits for primary/secondary and metadata surfaces, including chroma variants.
- Flip and update state: surface update lock, flip type, pending status, stereo sync mode, GSL enable, triple buffering, pending delay/min-time, and flip/flip-away interrupt mask/type/status/clear bits.
- Request timing and QoS state: TTU watermarks, fixed QoS levels, QoS ramp disable, vblank timing, flip timing, nominal PTE/meta timing, prefetch settings, per-line delivery values, reference-frequency-to-pixel-frequency conversion, blank offsets, scaler output timing, and destination-Y DRQ limits.
- Power and clock state: HUBP clock enable/disable fields, HUBPREQ/HUBPRET/CURSOR memory power force/disable/status fields, virtual memory page config, and measurement-window clock counters.
- Cursor and DMDATA state: cursor control, surface address, size, position, hot spot, stereo control, destination offset, DMDATA address/control/QoS/status/software-update fields.
- Diagnostics and profiling state: underflow/status bits, read-line values, HUBPRET interrupts, perfmon counter values and counter state, perfmon interrupt status and ack bits, and clock measurement-window counters.

Persistence is hardware-defined. Configuration fields usually remain programmed until a plane update, modeset, suspend/resume, power-gating transition, or GPU reset. Status and interrupt fields may be read-only, sticky, write-one-to-clear, self-clearing, or side-effect-sensitive. Names such as `*_STATUS`, `*_ACK`, `*_CLEAR`, `*_PENDING`, `*_INUSE`, `*_UNDERFLOW_CLEAR`, `*_MEM_PWR_STATUS`, and `*_CLOCK_ENABLE` should be treated as side-effect-sensitive unless the consuming code or hardware specification proves otherwise.

## Dependencies And Integration Points

This chunk depends on the matching generated address header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`

Observed include points for the DCN 3.0.0 offset/mask pair include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c`

The closest structural integration is `display/dc/hubp/dcn30/dcn30_hubp.h`, where `HUBP_MASK_SH_LIST_DCN30(mask_sh)` references fields in this chunk through `HUBP_SF(...)`: surface config, tiling, pitch, flip control, viewport, surface and metadata addresses, DCC/TMZ, flip interrupt, HUBPRET control, expansion mode, request sizing, blanking, prefetch, vblank/flip/nominal timing, TTU/QoS, cursor, DMDATA, VM aperture, and L1 TLB fields.

`display/dc/resource/dcn30/dcn30_resource.c` instantiates `hubp_shift` and `hubp_mask` from `HUBP_MASK_SH_LIST_DCN30(__SHIFT)` and `HUBP_MASK_SH_LIST_DCN30(_MASK)`, then passes them to `hubp3_construct(...)`. `display/dc/hubp/dcn30/dcn30_hubp.c` uses the resulting register tables in functions such as `hubp3_set_vm_system_aperture_settings(...)` and `hubp3_program_surface_flip_and_addr(...)`. `display/dc/irq/dcn30/irq_service_dcn30.c` maps page-flip IRQ sources to `HUBPREQ` `DCSURF_SURFACE_FLIP_INTERRUPT` fields.

## Risks And Edge Cases

- These constants are hardware ABI, not ordinary compile-time conveniences. A wrong mask or shift can compile cleanly while programming the wrong bits, causing blank planes, corrupted scanout, bad cursor placement, missed flips, VM faults, underflow, or pipe-specific failures.
- Repeated instance blocks are high drift risk. `HUBP1`, `HUBP2`, and `HUBP3`, `HUBPREQ1`, `HUBPREQ2`, and partial `HUBPREQ3`, `HUBPRET1/2`, `CURSOR0_1/2`, and `DC_PERFMON7/8` are highly similar. Copying one field width or mask from the wrong instance can affect only one active pipe.
- The chunk starts and ends mid-family. The leading `DC_PERFMON6_PERFCOUNTER_CNTL` fields are incomplete here, and `HUBPREQ3` stops after the first `BLANK_OFFSET_0` mask. Adjacent chunks must be consulted before claiming full coverage for those families.
- Packed control/status registers require read-modify-write discipline. Surface control, flip control, interrupt, memory power, VM/TLB, cursor control, and DMDATA control registers contain unrelated fields in one word; full-register writes can corrupt neighboring state.
- Address programming is order-sensitive. DCN HUBP code documents that high address registers must be programmed before low address registers because the low write can latch the address set. Bad masks for low/high, chroma, metadata, or primary/secondary fields can scan out stale or unintended memory.
- Interrupt and sticky status bits can have write-one-to-clear or self-clearing behavior. Misusing `SURFACE_FLIP_CLEAR`, `SURFACE_FLIP_AWAY_CLEAR`, perfmon ack bits, HUBPRET interrupt ack bits, or underflow clear bits can miss events or create interrupt storms.
- DCC and TMZ fields interact with compression and memory protection. A stale or misplaced `*_DCC_EN`, `*_DCC_IND_BLK`, or `*_TMZ` mask can cause decompression artifacts, memory-security policy violations, or failures limited to protected/compressed surfaces.
- TTU, prefetch, vblank, flip, nominal, and per-line delivery fields are workload-sensitive. Bad masks may only fail at high resolution, high refresh, low memory clock, multi-plane, scaling, cursor-heavy, or DCC-enabled workloads.
- Power and clock fields have sequencing dependencies outside this header. Accessing HUBP/HUBPREQ/HUBPRET/CURSOR registers while clock or memory domains are disabled can produce stale reads or dropped writes.
- Perfmon fields are diagnostic but still side-effect-sensitive. Wrong counter select, interrupt, restart, active, or read selector masks can make profiling misleading or leave perfmon interrupts uncleared.

## Test Signals

Useful validation signals for this range include:

- Build AMDGPU/DC with DCN 3.0.0 support enabled. Missing or renamed macros should fail at `dcn30_resource.c`, `dcn30_hubp.h`, IRQ, GPIO, clock manager, and DMUB include sites.
- Statically compare this generated header chunk against AMD's DCN 3.0.0 register database and the matching `dcn_3_0_0_offset.h` to verify every visible `__SHIFT` and `_MASK` pair matches the intended register field.
- Diff repeated instance families across `HUBP1/2/3`, `HUBPREQ1/2/3`, `HUBPRET1/2`, `CURSOR0_1/2`, and `DC_PERFMON7/8` to catch accidental instance drift where the hardware layout should be identical.
- Exercise display hardware with enough active pipes to use instances 1, 2, and 3. Cover modeset, page flip, plane enable/disable, cursor movement, cursor format changes, scaling, rotation, mirroring, multi-monitor, hotplug, DPMS, suspend/resume, and GPU reset recovery.
- Test RGB and YUV/chroma paths with primary and secondary surfaces, metadata addresses, DCC-enabled surfaces, and TMZ/protected surfaces where supported.
- Stress page-flip behavior: immediate flips, vblank-synchronized flips, update locks, stereo sync modes, GSL, triple buffering, flip pending status, flip-away status, and IRQ clear/mask behavior.
- Validate VM/TLB and DMDATA paths by exercising VM aperture setup, DMDATA VM fault/underflow/late/done status, cursor/metadata address programming, and software DMDATA update paths.
- Run bandwidth-sensitive display workloads at high resolution/refresh and low memory clock. Watch for underflow, flicker, corruption, missed vblank, page faults, flip timeouts, or failures isolated to one pipe.
- Use display perfmon/debug tooling, where available, to configure `DC_PERFMON7` and `DC_PERFMON8`, start/stop counters, read low/high values, and verify interrupt/status/ack behavior.

## Cross-Chunk Notes

The previous chunk is needed for the beginning of `DC_PERFMON6_PERFCOUNTER_CNTL`. The next chunk is needed for the rest of `HUBPREQ3`, including later blanking, destination, prefetch, vblank, flip, nominal, delivery, cursor, reference-frequency, DRQ-limit, and memory-power fields. The final per-file research document should merge those adjacent reports before making complete statements about the DCN 3.0.0 generated register map.

### subset-b-001692: lines 12288-14786

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 12288-14786

## Chunk Scope

This chunk covers a generated AMD DCN 3.0.0 ASIC register shift/mask header slice. The file is guarded by `_dcn_3_0_0_SH_MASK_HEADER` and contains no executable functions, types, storage, or inline logic; it exports preprocessor constants that describe bit positions and bit masks for memory-mapped display hardware registers. Within lines 12288-14786, the slice contains 2,113 `#define` entries, split into 1,056 `__SHIFT` constants and 1,076 `*_MASK` constants, organized under 15 `addressBlock` comments and about 350 register comments.

The chunk starts mid-register at `HUBPREQ3_BLANK_OFFSET_0__DLG_V_BLANK_END_MASK`, continues through HUBP/HUBPREQ/HUBPRET/CURSOR/PERFMON blocks for display pipe instances 3, 4, and 5, and ends at the beginning of the DPP0 CNVC format-conversion block with `CNVC_CFG0_FCNV_FP_BIAS_G`.

## Purpose

The purpose of this chunk is to provide compile-time bitfield metadata for DCN 3.0 display programming. Driver code combines these constants with matching offset definitions from `dcn_3_0_0_offset.h` to program display pipe registers through generated field tables and register access helpers.

The register families represented here map the display pipeline data path:

- `HUBP*` and `HUBPREQ*` define hub pipe surface, VM, request sizing, flip, TTU/QoS, prefetch, blanking, delivery, and memory power fields.
- `HUBPRET*` defines hub pipe return/read-line, interrupt, crossbar, DET/DMROB/PIXCDC memory power, and status fields.
- `CURSOR0_*` defines cursor surface address, size, position, hot spot, stereo, cursor memory power, and display metadata fields.
- `DC_PERFMON9`, `DC_PERFMON10`, and `DC_PERFMON11` define per-pipe display performance monitor counter selection, state, interrupt, and counter value fields.
- `DPP_TOP0` begins display pipe processor top-level clock/reset/CRC/host-read fields.
- `CNVC_CFG0` begins DPP conversion and pixel-format fields.

## Important APIs, Types, And Constants

There are no C APIs or types in this chunk. The exported interface is naming-convention based:

- `REGISTER__FIELD__SHIFT` gives the bit offset to use when packing or unpacking a field.
- `REGISTER__FIELD_MASK` gives the already-positioned field mask for read/modify/write operations.
- Register comments such as `//HUBPREQ4_DCSURF_SURFACE_CONTROL` group adjacent shift/mask pairs.
- `// addressBlock: ...` comments identify the hardware block instance that owns the following register definitions.

Important block groups in this range:

- `HUBPREQ3_*` completes instance 3 timing/request definitions: blank offsets, destination dimensions, scaler positions, prefetch ratios, vblank/flip/nominal PTE and meta chunk timing, per-line delivery, cursor settings, frequency conversion, DRQ limits, and request-side memory power state.
- `HUBPRET3_*`, `HUBPRET4_*`, and `HUBPRET5_*` define return-side control, DET buffer base, 3-to-2 packing disable, crossbar source selection, memory power controls/status, read-line windows, vblank/read-line interrupts, read-line snapshots, and read-line status.
- `CURSOR0_3_*`, `CURSOR0_4_*`, and `CURSOR0_5_*` define cursor enable/mode/TMZ/snoop/system/pitch/lines-per-chunk fields, 48-bit-ish address split into low/high registers, geometry, stereo offsets, memory power state, and `DMDATA` address/control/QoS/status/software data fields.
- `HUBP4_*` and `HUBP5_*` define surface config, address/tiling config, primary/secondary luma and chroma viewports, request-size config, HUBP control, clock gating/status, VM page size, and measurement windows.
- `HUBPREQ4_*` and `HUBPREQ5_*` are large repeated blocks for surface pitch, VMID, primary/secondary luma/chroma surface and meta-surface addresses, TMZ/DCC surface controls, flip controls, flip interrupts, in-use/earliest-in-use latched addresses, TTU/QoS controls for surface and cursor requests, display metadata VM control, VM aperture and L1 TLB controls, blanking, vblank/flip/nominal timing, delivery timing, cursor request settings, and request memory power.
- `DC_PERFMON9_*`, `DC_PERFMON10_*`, and `DC_PERFMON11_*` define event selection, counted-value selection, increment mode, hardware stop/control, run enable, counter active/interrupt fields, 8 counter state selectors, report control, counter-off interrupt handling, clock enable, start/stop selectors, high/low counter value fields, and interrupt status/ack bits.
- `DPP_TOP0_*` covers DPP clock enable and clock gate disable fields, soft reset fields for CNVC/DSCL/CM/OBUF, CRC values and CRC control, and host-read rate control.
- `CNVC_CFG0_*` starts conversion configuration: surface pixel format and alpha-plane enable, format expansion/conversion/alpha/bypass/clamp/crossbar/update-pending fields, and the first floating-point bias register.

## Control Flow And Data Flow

This header does not implement runtime control flow. Its data flow is compile-time:

1. Source files include `dcn/dcn_3_0_0_offset.h` and `dcn/dcn_3_0_0_sh_mask.h`.
2. Component-specific register-list macros select register offsets by instance id, for example `HUBP_REG_LIST_DCN30(id)` in DCN 3.0 resource setup.
3. Component-specific mask/shift list macros expand field names with `__SHIFT` or `_MASK`, for example `HUBP_MASK_SH_LIST_DCN30(__SHIFT)` and `HUBP_MASK_SH_LIST_DCN30(_MASK)`.
4. The expanded values populate static register, shift, and mask tables such as the DCN 3.0 HUBP tables in resource code.
5. Runtime register helpers use the tables to pack field values into hardware register writes, extract status bits from reads, and perform read/modify/write updates.

For DPP/CNVC, `dcn30_dpp.h` uses macros such as `TF_SF(CNVC_CFG0_FORMAT_CONTROL, CNVC_BYPASS, mask_sh)` and `TF_SF(DPP_TOP0_DPP_CONTROL, DPP_CLOCK_ENABLE, mask_sh)` to map these constants into transform/DPP field tables. For HUBP/HUBPREQ/HUBPRET, `dcn30_resource.c` builds per-instance tables with `HUBP_REG_LIST_DCN30(id)`, `HUBP_MASK_SH_LIST_DCN30(__SHIFT)`, and `HUBP_MASK_SH_LIST_DCN30(_MASK)`.

## State And Persistence Behavior

The chunk itself has no persistent software state. It describes persistent hardware state in memory-mapped registers:

- Surface address and meta-address fields persist in HUBPREQ until a flip or update sequence replaces them.
- `SURFACE_INUSE` and `SURFACE_EARLIEST_INUSE` expose latched hardware addresses and VMIDs for active or earliest queued surfaces.
- Flip state fields such as `SURFACE_FLIP_PENDING`, flip occurred/status bits, and clear bits expose transient hardware state around page flips.
- VM/TLB and aperture fields control address translation behavior for display metadata and surface fetches.
- Memory power control/status fields reflect or force power states for request, return, cursor, DET, DMROB, PIXCDC, DPTE, MPTE, META, and PDE memories.
- PERFMON counter and interrupt fields hold hardware performance-monitor state until read, reset, acknowledged, or reprogrammed.

Because these are raw bit descriptions, persistence semantics depend on the underlying hardware register behavior and on the driver code that writes or clears the bits.

## Dependencies

Direct dependencies are implicit rather than included in this chunk:

- Matching register offset headers, especially `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`, must define the corresponding register addresses.
- DC register helper macros and structures in the display core consume the field tables produced from these constants.
- DCN HUBP, DPP, IRQ, DMUB, clock, GPIO, and resource code include this header for DCN 3.0/3.0.2 support.
- The constants assume the hardware register layout for DCN 3.0.0; they are not self-validating and must remain synchronized with ASIC-generated register specs.

Observed include/integration points include `display/dc/resource/dcn30/dcn30_resource.c`, `display/dc/irq/dcn30/irq_service_dcn30.c`, `display/dc/irq/dcn302/irq_service_dcn302.c`, `display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`, `display/dc/gpio/dcn30/*`, and `display/dmub/src/dmub_dcn30.c` / `dmub_dcn302.c`.

## Integration Points

This chunk is primarily integrated through macro expansion rather than direct symbol references:

- HUBP register programming: `display/dc/hubp/dcn30/dcn30_hubp.h` extends earlier HUBP mask/shift lists with DCN 3.0 fields, while `display/dc/resource/dcn30/dcn30_resource.c` instantiates the lists for hardware pipe ids.
- Resource creation: DCN 3.0 resource code creates HUBP objects and assigns per-instance register/mask/shift tables, so instance-specific constants such as `HUBP4_*`, `HUBPREQ4_*`, and `CURSOR0_4_*` become runtime access metadata.
- DPP format programming: `display/dc/dpp/dcn30/dcn30_dpp.h` consumes `DPP_TOP0_*` and `CNVC_CFG0_*` fields in transform/DPP field lists for clock, pixel-format, alpha, clamp, crossbar, and floating-point bias/scale programming.
- IRQ handling: HUBP flip interrupt sources for pipes 4 and 5 are handled in DC IRQ services; the mask/shift constants here describe the underlying per-HUBPREQ flip interrupt status/clear fields.
- DMUB and clock/GPIO code include the same header for register-level firmware/mailbox or display infrastructure operations where DCN 3.0 register fields are needed.

The per-instance naming is significant. The same logical field appears with numeric prefixes, for example `HUBPREQ4_DCSURF_SURFACE_CONTROL__PRIMARY_SURFACE_DCC_EN_MASK` and `HUBPREQ5_DCSURF_SURFACE_CONTROL__PRIMARY_SURFACE_DCC_EN_MASK`. Driver macros choose the instance by composing register names from a block prefix and id.

## Risks And Edge Cases

- Generated-header drift is the main risk. If a mask or shift no longer matches the ASIC register spec or the paired offset header, the compiler will still succeed while runtime register programming corrupts unrelated bits.
- Some macros encode status-clear bits adjacent to status bits, such as flip, underflow, PERFMON interrupt, and DMDATA VM fault/underflow clears. Incorrect read/modify/write policy can acknowledge or clear events unexpectedly.
- Surface address fields are split into low and high registers and have separate luma/chroma and meta variants. Mixing `_C`, meta, primary, secondary, in-use, or earliest-in-use registers can program the wrong plane or inspect the wrong latched state.
- TMZ, snoop, system, DCC, and VM/TLB fields affect memory security and address translation. Wrong masks could produce display faults, underflow, secure-memory exposure, or silent corruption.
- Clock-gating, memory-power, and soft-reset fields can make blocks inaccessible or unstable if programmed with stale assumptions.
- PERFMON fields are repeated per pipe with large selector fields; event selection and interrupt acknowledgement can be miswired if instance numbers are confused.
- The chunk begins and ends mid-logical-file. `HUBPREQ3_BLANK_OFFSET_0` starts before this chunk, and `CNVC_CFG0_FCNV_FP_BIAS_G` continues after it. The merge lane must combine adjacent chunk reports before drawing whole-file conclusions.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware/display regression signals:

- Build coverage that compiles DCN 3.0 and DCN 3.0.2 display paths including `dcn30_resource.c`, `dcn302_resource.c`, `dcn30_dpp.h` consumers, IRQ services, DMUB sources, clock manager, and GPIO files.
- Static checks that every mask/shift field referenced by `HUBP_MASK_SH_LIST_DCN30`, `TF_SF`, `TF2_SF`, and related macros resolves against this header.
- Display bring-up on DCN 3.0 hardware with multiple active pipes, especially pipes 3, 4, and 5, validates the repeated instance tables.
- Page-flip and vblank/read-line interrupt tests exercise `HUBPREQ*_DCSURF_FLIP_CONTROL`, `HUBPREQ*_DCSURF_SURFACE_FLIP_INTERRUPT`, and `HUBPRET*_HUBPRET_INTERRUPT` fields.
- Cursor movement, cursor format, stereo cursor, and display metadata tests exercise `CURSOR0_[3-5]_*` and `DMDATA_*` definitions.
- DCC/TMZ/VM surface tests exercise surface-control, aperture, TLB, address, and meta-address fields.
- CRC capture and DPP format-conversion tests exercise `DPP_TOP0_DPP_CRC_*`, `CNVC_CFG0_CNVC_SURFACE_PIXEL_FORMAT`, and `CNVC_CFG0_FORMAT_CONTROL`.
- Power-management and clock-gating tests exercise HUBP/HUBPREQ/HUBPRET/CURSOR memory power fields plus `DPP_TOP0_DPP_CONTROL` and `DPP_TOP0_DPP_SOFT_RESET`.

### subset-b-001693: lines 14787-17309

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 14787-17309

## Purpose

This chunk is part of AMD DCN 3.0.0's generated ASIC register shift/mask header. It does not implement executable logic; it defines bit positions (`__SHIFT`) and bit masks (`_MASK`) for display pipe processor (DPP) registers used by the AMDGPU display driver. The line range covers the tail of DPP0 converter configuration, DPP0 cursor/scaler/color/performance-monitor blocks, and the beginning of DPP1 top/converter/cursor/scaler blocks.

The macros provide the hardware layout contract consumed by DCN display code. Runtime code builds `dcn3_dpp_shift` and `dcn3_dpp_mask` tables from these definitions, then uses `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and related helper macros to encode/decode hardware register fields safely.

## Address Blocks Covered

- `dce_dc_dpp0_dispdec_cnvc_cfg_dispdec` tail: floating-point converter bias/scale, color keyer, 2-bit alpha LUT, pre-dealpha, pre-CSC matrices, coefficient format, pre-degamma, and pre-realpha fields.
- `dce_dc_dpp0_dispdec_cnvc_cur_dispdec`: cursor enable/mode/color/FP scale-bias fields for DPP0.
- `dce_dc_dpp0_dispdec_dscl_dispdec`: DPP0 display scaler fields for coefficient RAM, tap control, scale ratios, initial phases, overscan, blanking, recout/MPC sizes, line buffer format/memory, memory power control/status, and output buffer power control.
- `dce_dc_dpp0_dispdec_cm_dispdec`: DPP0 color-management fields for CM control, post-CSC, gamut remap, gamma correction RAM A/B, blend gamma RAM A/B, HDR multiplier, dealpha, coefficient format, shaper LUT RAM A/B, memory power state, 3D LUT, and test debug access.
- `dce_dc_dpp0_dispdec_dpp_dcperfmon_dc_perfmon_dispdec`: performance counter and performance monitor fields for `DC_PERFMON12`.
- `dce_dc_dpp1_dispdec_dpp_top_dispdec`: DPP1 top control, soft reset, CRC readout/control, and host-read throttle fields.
- `dce_dc_dpp1_dispdec_cnvc_cfg_dispdec` and `dce_dc_dpp1_dispdec_cnvc_cur_dispdec`: DPP1 equivalents of the converter and cursor fields.
- `dce_dc_dpp1_dispdec_dscl_dispdec` beginning: DPP1 scaler fields through `DSCL1_LB_MEMORY_CTRL`.

## Important APIs, Types, and Macros

- Field macros follow `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming. For example, `DSCL0_SCL_MODE__DSCL_MODE__SHIFT` and `DSCL0_SCL_MODE__DSCL_MODE_MASK` define where the scaler mode field lives in `DSCL0_SCL_MODE`.
- DPP register lists in `display/dc/dpp/dcn30/dcn30_dpp.h` use `SRI(...)` entries such as `SRI(SCL_MODE, DSCL, id)` and `SRI(FORMAT_CONTROL, CNVC_CFG, id)` to bind per-instance register addresses.
- The same header's `DPP_REG_LIST_SH_MASK_DCN30*` macros use field selectors such as `TF_SF(DSCL0_SCL_MODE, DSCL_MODE, mask_sh)` to populate `struct dcn3_dpp_shift` and `struct dcn3_dpp_mask`.
- `display/dc/resource/dcn30/dcn30_resource.c` instantiates `dpp_regs[]`, `tf_shift`, and `tf_mask` from these macro lists, making the generated masks available to live DPP objects.
- DPP implementation code in `display/dc/dpp/dcn30/dcn30_dpp.c` and `dcn30_dpp_cm.c` consumes these tables through register helper macros, not by spelling numeric masks directly.

## Functional Areas

- CNVC pixel conversion: `CNVC_CFG{0,1}_CNVC_SURFACE_PIXEL_FORMAT`, `FORMAT_CONTROL`, FP bias/scale, color keying, alpha LUT, pre-dealpha/realpha, pre-CSC matrix banks A/B, pre-degamma ROM select, and coefficient format. These fields control input format expansion, alpha handling, channel crossbar mapping, clamping, and pre-scaler color transforms.
- Cursor conversion: `CNVC_CUR{0,1}_CURSOR0_*` fields control cursor enable, expansion/inversion/ROM mode, cursor pixel format mode, update-pending status, packed RGB colors, and FP scale/bias.
- DSCL scaler: `DSCL{0,1}_SCL_*`, `DSCL_CONTROL`, `DSCL_AUTOCAL`, `RECOUT_*`, `MPC_SIZE`, `LB_*`, and memory-power fields define filter coefficient RAM access, horizontal/vertical/chroma ratios, phase initialization, tap counts, overscan/blanking geometry, line-buffer allocation, and scaler memory power state.
- CM color management: `CM0_CM_*` fields define CM bypass, post-CSC and gamut-remap double-buffered matrix banks, gamma correction LUTs, blend gamma LUTs, shaper LUTs, HDR multiplier, dealpha, memory power, 3D LUT indexing/data, output normalization/offset, and debug register access.
- DPP top/CRC/perfmon: `DPP_TOP1_*` fields provide DPP enable/reset, CRC value/control selection, and host-read rate control. `DC_PERFMON12_*` fields expose counter selection, counter state, monitor state, interrupt status/ack bits, and low/high counter-value readout.

## Control Flow

There is no direct control flow in this header. Runtime control flow is created by consumers:

- Resource construction includes this header and expands the mask/shift macros into static tables during compilation.
- Plane programming paths call DPP functions such as converter setup, pre-degamma programming, post-CSC programming, scaler setup, gamma/LUT programming, and state-readback helpers.
- Register helpers combine a field value with its shift and mask before writing a 32-bit register, or apply mask/shift extraction after reading one.
- Double-buffered color blocks use current-state fields such as `*_MODE_CURRENT` and `*_SELECT_CURRENT` to choose the inactive bank, program RAM A or RAM B, then switch mode/select fields so hardware applies changes on the intended boundary.
- Memory-power flows use control/status fields such as `CM_MEM_PWR_CTRL`, `CM_MEM_PWR_STATUS`, `DSCL_MEM_PWR_CTRL`, and `DSCL_MEM_PWR_STATUS`; consumers may wait for status fields before accessing LUT or line-buffer RAM.

## State and Persistence

The macros themselves are compile-time constants and have no persistence. The persistent state is in display hardware registers and SRAM/LUT memories:

- CNVC and DSCL configuration persists in DPP instance registers until reprogrammed, reset, or power-gated.
- CM LUT state persists in gamma/blend/shaper/3D LUT RAMs; the A/B RAM convention allows preparing one bank while the other is live.
- Update-pending/current fields expose whether hardware has latched or is still waiting to latch programmed state.
- Perfmon counter value/status fields represent live hardware counter state and interrupt status. Acknowledge fields are write-sensitive and must be treated as side-effecting hardware bits.
- Memory power control fields can invalidate assumptions about LUT/LB availability if clients write data while the corresponding memory is off or forced into low power.

## Dependencies and Integration Points

- Paired offset definitions in `dcn_3_0_0_offset.h` provide register addresses; this file provides per-field positions and masks.
- `display/dc/dpp/dcn30/dcn30_dpp.h` maps these register fields into the DPP abstraction used by the display core.
- `display/dc/resource/dcn30/dcn30_resource.c` constructs per-pipe DPP register objects for instances 0 through 5 and initializes the shared shift/mask tables from this header.
- `display/dc/dpp/dcn30/dcn30_dpp.c` uses CNVC, DSCL, and DPP top fields for state readback, converter setup, pre-degamma, scaler geometry, and power-state handling.
- `display/dc/dpp/dcn30/dcn30_dpp_cm.c` uses CM fields for gamma correction, post-CSC, gamut remap, blend gamma, shaper LUT, 3D LUT, CM bypass, and CM memory-power sequencing.
- The broader AMDGPU display stack includes this header from DCN30 resource, IRQ, clock, GPIO, and DMUB-related code, but the fields in this chunk primarily integrate through DPP construction and programming.

## Risks and Edge Cases

- Register layout drift is the main risk. A wrong mask or shift silently writes the wrong bit field and can corrupt unrelated hardware control bits.
- Instance duplication increases maintenance risk: DPP0 fields are referenced by generic DPP mask lists and then reused for all instances, while the file also contains explicit DPP1 definitions. Any mismatch between corresponding `0` and `1` fields is suspicious unless documented by hardware.
- Packed two-field and four-field registers require exact masks. CSC matrix registers, region registers, blanking registers, recout size/start, and line-buffer partition registers pack independent values into one 32-bit word.
- Current/pending fields such as `*_MODE_CURRENT`, `*_SELECT_CURRENT`, `CNVC_UPDATE_PENDING`, `CUR0_UPDATE_PENDING`, and `SCL_UPDATE_PENDING` are readback/status-sensitive; treating them as ordinary writable configuration can break frame-boundary synchronization.
- LUT programming depends on RAM select, host select, write color mask, index auto-increment, and memory power state. Incorrect masks here can produce color corruption that only appears under HDR, color-management, or multi-plane blending workloads.
- Perfmon interrupt status and ack masks are side-effecting. Mixing status and ack bits, or writing a full register without masking, can drop events or leave interrupts asserted.
- Many masks are hardware-width limited, such as 13/14-bit geometry fields and 27-bit scale ratios. Callers must still validate values before encoding; masks truncate but do not make invalid modes safe.

## Test Signals

- Build coverage: compile AMDGPU DCN30 code with this header included; struct initializers for `dcn3_dpp_shift` and `dcn3_dpp_mask` catch missing or renamed fields.
- Display bring-up: enabling a DCN30 GPU display exercises DPP top enable/reset, CNVC format setup, DSCL geometry, and CM bypass/default programming.
- Plane format tests: RGB/YUV, alpha plane, cursor, color key, and FP16/HDR-like paths exercise CNVC format, alpha, crossbar, FP bias/scale, and cursor fields.
- Scaling tests: non-native modes, underscan/overscan, chroma scaling, and multi-plane composition exercise DSCL ratios, taps, coefficient RAM, line-buffer allocation, recout/MPC sizing, and update-pending behavior.
- Color-management tests: gamma, degamma, CSC, gamut remap, shaper LUT, blend gamma, and 3D LUT validation exercise the large CM0 register region and double-buffered RAM bank selection.
- Power-management tests: display idle/active transitions, low-power memory settings, and IPS-related flows should verify `CM_MEM_PWR_*` and `DSCL_MEM_PWR_*` status waits before LUT or scaler memory access.
- Diagnostics: CRC readback, perfmon counter programming, and debugfs or driver state dumps can reveal incorrect DPP top, CRC, perfmon, recout, scaler, and CM state decoding.

### subset-b-001694: lines 17310-19827

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 17310-19827

## Scope

This chunk is a large middle slice of AMDGPU's generated DCN 3.0.0 shift/mask header. It contains preprocessor constants only: no functions, structs, enums, storage objects, or local executable control flow. The exported contract is a dense set of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros that describe the bit positions and already-shifted masks for DCN 3.0.0 display hardware registers.

The range starts in the tail of the DPP1 DSCL line-buffer memory-control group, covers the rest of DPP1 DSCL memory/power and output-buffer fields, then covers almost the full DPP1 color-management block, DPP1 display-performance monitor block, and the beginning of DPP2. The DPP2 material includes top-level DPP control, CNVC format/cursor conversion, DSCL scaler fields, and the beginning of the DPP2 color-management block through `CM2_CM_GAMCOR_RAMA_OFFSET_R`. The chunk ends before the remaining `CM2_CM_GAMCOR_RAMA_REGION_*` fields, so whole-file reconciliation must merge this slice with adjacent chunks.

## Purpose

The purpose of this header region is to provide ASIC-specific field metadata for DCN 3.0 display pipe programming. Runtime DC code can refer to logical field names while the generated header supplies the exact bit layout for the DCN 3.0.0 register database.

The covered hardware areas are:

- DPP1 DSCL tail fields: line-buffer partitioning, luma/chroma vertical counters, DSCL LUT/line-buffer memory power control and status, output-buffer bypass/full-buffer/hold control, and output-buffer memory power state.
- DPP1 CM fields: post color-space conversion matrices, gamut remap matrices, bias registers, gamma-correction LUT programming, blending gamma LUT programming, HDR multiplier coefficient, CM memory-power controls/status, dealpha/coefficient-format controls, shaper LUT programming, 3D LUT programming, and CM test/debug index/data registers.
- DPP1 DC perfmon 13 fields: performance-counter event selection, counter control, counter state, perfmon control, current-value comparison, and high/low counter readback.
- DPP2 DPP top fields: DPP clock enable/gating, soft reset, CRC values/control, and host-read control.
- DPP2 CNVC fields: surface pixel format, format expansion/conversion/alpha/crossbar controls, floating-point bias/scale, color keying, alpha LUT, pre-dealpha, pre-CSC matrices, coefficient format, pre-degamma, pre-realpha, and cursor color/scale/bias fields.
- DPP2 DSCL fields: scaler coefficient RAM access, scaler mode/tap controls, two-tap sharpening, manual replication, scale ratios, initial phases, black color, update/autocal controls, overscan, OTG blanking windows, recout/MPC sizes, line-buffer format/memory fields, and DSCL/OBUF memory power.
- DPP2 CM start fields: post CSC, gamut remap, bias, and the beginning of gamma-correction RAM A setup.

Although this repository path sits under `sources/distributed-fs/ceph-client`, this file is AMD display hardware metadata. It has no Ceph, filesystem, distributed-storage, or network protocol behavior.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The important interface is the generated macro naming scheme:

- `*_SHIFT` gives the field's low bit position.
- `*_MASK` gives the field mask already shifted into the register position.
- Register-heading comments group macros by hardware register.
- `addressBlock` comments identify generated register blocks such as `dce_dc_dpp1_dispdec_cm_dispdec`, `dce_dc_dpp1_dispdec_dpp_dcperfmon_dc_perfmon_dispdec`, `dce_dc_dpp2_dispdec_dpp_top_dispdec`, `dce_dc_dpp2_dispdec_cnvc_cfg_dispdec`, `dce_dc_dpp2_dispdec_cnvc_cur_dispdec`, `dce_dc_dpp2_dispdec_dscl_dispdec`, and `dce_dc_dpp2_dispdec_cm_dispdec`.

The DSCL memory and output-buffer groups use compact masks for power and buffering state. `DSCL1_DSCL_MEM_PWR_CTRL` and `DSCL2_DSCL_MEM_PWR_CTRL` define force/disable fields for LUT memory and line-buffer groups `LB_G1` through `LB_G6`, plus `LB_MEM_PWR_MODE`. Their matching `*_STATUS` registers expose each memory group's state. `DSCL*_OBUF_CONTROL` covers bypass, full-buffer use, half recout width, and output hold count; `DSCL*_OBUF_MEM_PWR_CTRL` combines force, disable, mode, and state bits for the output buffer memory.

The CM1 and CM2 matrix groups follow a consistent 16-bit-pair layout. Post-CSC and gamut-remap coefficient registers pack pairs such as `C11/C12`, `C13/C14`, `C21/C22`, `C23/C24`, `C31/C32`, and `C33/C34` into low and high 16-bit halves. The `_B_` variants provide the alternate bank of coefficients. Control registers such as `CM*_CM_POST_CSC_CONTROL` and `CM*_CM_GAMUT_REMAP_CONTROL` expose mode and current-mode fields, while `CM*_CM_CONTROL` provides bypass and update-pending status.

The CM1 gamma-correction, blending-gamma, and shaper blocks expose indexed LUT programming surfaces. `CM1_CM_GAMCOR_LUT_INDEX`, `CM1_CM_GAMCOR_LUT_DATA`, and `CM1_CM_GAMCOR_LUT_CONTROL` define index, data, write-color mask, read-color select, debug read, host select, and config mode. `CM1_CM_BLNDGAM_*` mirrors the gamma-correction pattern for blend gamma. `CM1_CM_SHAPER_*` defines shaper control, RGB offsets, scale fields, LUT index/data, write-enable masks, and RAM A/B region descriptors.

The LUT region descriptors are repeated and mechanically generated. For gamma-correction and blend-gamma RAM A/B, each color channel has start, start slope, start base, end base, end/slope, and offset registers. Region-pair registers such as `CM1_CM_GAMCOR_RAMA_REGION_0_1` through `REGION_32_33` pack one 9-bit LUT offset and one segment-count field per region into the low and high halves. Shaper RAM A/B uses the same region-pair idea for its piecewise approximation tables, while CM2 starts the same `GAMCOR_RAMA` sequence before the chunk ends.

The 3D LUT group is specific to CM1 in this range. `CM1_CM_3DLUT_MODE` carries enable/interpolation/size/readback configuration fields. `CM1_CM_3DLUT_INDEX`, `CM1_CM_3DLUT_DATA`, and `CM1_CM_3DLUT_DATA_30BIT` provide indexed data access. `CM1_CM_3DLUT_READ_WRITE_CONTROL` exposes write-enable, readback, config status, bit-depth, and mode-change/update fields. Output normalization and RGB output offsets are described by `CM1_CM_3DLUT_OUT_NORM_FACTOR` and `CM1_CM_3DLUT_OUT_OFFSET_*`.

The DPP1 perfmon block defines the `DC_PERFMON13_*` field contract. `DC_PERFMON13_PERFCOUNTER_CNTL` selects events, counted current-value source, increment mode, run-enable mode, restart/int enable, active/off-mask bits, and counter select. `DC_PERFMON13_PERFCOUNTER_CNTL2` adds counted-value type and hardware stop controls. `DC_PERFMON13_PERFCOUNTER_STATE` exposes current state, restart pending, stop pending, clear state bits, current value, and carry/overflow style status. The `PERFMON_CNTL*`, `PERFMON_CVALUE_*`, `PERFMON_HI`, and `PERFMON_LOW` groups define counter-window, comparison, and readback fields.

The DPP2 top and CNVC groups describe the start of a second display pipe. `DPP_TOP2_DPP_CONTROL` includes DPP clock enable and several DPP/DISPCLK gate-disable controls plus a test clock selector. `DPP_TOP2_DPP_SOFT_RESET` exposes reset and reset-status bits for top, DSCL, CM, CNVC, and cursor subblocks. `DPP_TOP2_DPP_CRC_CTRL` selects CRC components, region source, mode, window inclusion/exclusion, and enablement. `CNVC_CFG2_FORMAT_CONTROL` defines format expansion, 16-bit conversion, alpha enable, bypass/MSB alignment, positive clamps, update pending, and RGB crossbar selection.

The DPP2 DSCL groups are the scaler programming surface. The key fields include coefficient RAM tap pair/phase/filter type and even/odd coefficient values, scaler mode and RAM selection, luma/chroma/alpha coefficient modes, vertical/horizontal tap counts for luma and chroma, two-tap hardcoded coefficient and sharpening controls, horizontal/vertical scale ratios, initial phases for top/bottom and chroma, black color values, update pending, autocal pipe fields, overscan rectangles, OTG blanking start/end, recout and MPC dimensions, line-buffer format/memory partitioning, vertical counters, and DSCL/OBUF memory power.

## Control Flow

This header region has no local control flow. Runtime behavior is created by consumers that include `dcn_3_0_0_offset.h` and this shift/mask header, then use AMD display register helpers and generated register tables.

A typical path is:

1. DCN 3.0/3.0.2 code includes the DCN 3.0.0 offset and shift/mask headers.
2. Register-table macros paste instance-neutral names such as `DPP_CONTROL`, `FORMAT_CONTROL`, `SCL_MODE`, `CM_GAMCOR_CONTROL`, or `CM_3DLUT_MODE` onto instance-specific generated names such as `DPP_TOP2_DPP_CONTROL__DPP_CLOCK_ENABLE_MASK`.
3. Helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_SET_N`, `REG_UPDATE_N`, `REG_WAIT`, and the `SRI`/`TF_SF` table-building macros use the `*_SHIFT` and `*_MASK` constants to isolate fields during MMIO read/modify/write operations.
4. Display code sequences the hardware operations around power, blanking, update-lock, plane programming, or LUT programming requirements.

Examples visible in the display tree include DPP clock control through `DPP_CONTROL`, format programming through `FORMAT_CONTROL`, DSCL programming through `SCL_MODE`, `SCL_TAP_CONTROL`, scale-ratio, init, recout, and memory-power fields, and color-state readback/programming through CM shaper, blend gamma, gamma correction, and 3D LUT registers. The header does not encode the ordering rules for those operations; it only defines the bit layout needed by the sequenced code.

## State And Persistence Behavior

The file itself stores no state and persists nothing. It describes hardware register state in DPP/DSCL/CNVC/CM/perfmon blocks whose lifetime is controlled by display pipe power, modeset programming, plane updates, resets, suspend/resume, and GPU reset.

State represented by this chunk includes:

- DSCL scaler configuration: filter taps, coefficient RAM selection and values, scale ratios, initial phases, overscan, output dimensions, line-buffer partitioning, and update-pending state.
- DSCL and OBUF memory power state: force/disable/mode controls and readback status for LUT, line-buffer, and output-buffer memories.
- CM color pipeline state: CSC/gamut matrices, biases, coefficient formats, HDR multiplier, dealpha, shaper, gamma-correction, blend-gamma, and 3D LUT configuration and data.
- CNVC state: surface format, conversion behavior, alpha and color-key controls, pre-CSC/pre-degamma/pre-realpha, floating-point bias/scale, and cursor color controls.
- DPP top state: clock gating, soft-reset state, CRC capture state, and host-read routing.
- Perfmon state: event selection, counter enable/restart/interrupt controls, counter state, current-value comparison, and high/low counter values.
- Test/debug state: CM test debug index/data controls.

Some fields are configuration latches, some are live status readbacks, some are indexed data ports, and some are power/reset controls. A bad write can persist until the affected display pipe is reprogrammed, power-cycled, reset, or the GPU is reset. Indexed LUT/data registers are especially stateful: writes through an index/data pair alter table entries, not just a scalar register, and the selected index may affect subsequent reads or writes.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`, which provides the matching register addresses and base indices. Representative anchors in that file include:

- `mmDSCL1_LB_V_COUNTER` at `0x0e81` and `mmDSCL1_DSCL_MEM_PWR_CTRL` at `0x0e82`.
- `mmCM1_CM_CONTROL` at `0x0e8b`, `mmCM1_CM_GAMCOR_CONTROL` at `0x0ea8`, `mmCM1_CM_BLNDGAM_CONTROL` at `0x0ef2`, `mmCM1_CM_SHAPER_CONTROL` at `0x0f42`, and `mmCM1_CM_3DLUT_MODE` at `0x0f7b`.
- `mmDC_PERFMON13_PERFCOUNTER_CNTL` at `0x0f8f`.
- `mmDPP_TOP2_DPP_CONTROL` at `0x0f9b`.
- `mmCNVC_CFG2_FORMAT_CONTROL` at `0x0fa6` and `mmCNVC_CUR2_CURSOR0_CONTROL` at `0x0fc7`.
- `mmDSCL2_SCL_COEF_RAM_TAP_SELECT` at `0x0fcf`, `mmDSCL2_SCL_MODE` at `0x0fd1`, and `mmDSCL2_DSCL_MEM_PWR_CTRL` at `0x0fed`.
- `mmCM2_CM_CONTROL` at `0x0ff6`, `mmCM2_CM_GAMCOR_CONTROL` at `0x1013`, and `mmCM2_CM_GAMCOR_RAMA_OFFSET_R` at `0x1028`.

Visible include sites for `dcn_3_0_0_sh_mask.h` in this tree are:

- `display/dc/resource/dcn30/dcn30_resource.c`, which builds DCN 3.0 display resources and register tables.
- `display/dc/irq/dcn30/irq_service_dcn30.c` and `display/dc/irq/dcn302/irq_service_dcn302.c`, which use generated register metadata for interrupt tables.
- `display/dc/gpio/dcn30/hw_factory_dcn30.c` and `display/dc/gpio/dcn30/hw_translate_dcn30.c`, which consume the same generated namespace for GPIO support.
- `display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`, which includes the DCN 3.0 register headers for clock-management programming.
- `display/dmub/src/dmub_dcn30.c` and `display/dmub/src/dmub_dcn302.c`, which include these headers for DMUB-facing display microcontroller support.

The most important functional consumers are the DPP/DSCL/CM helpers under `display/dc/dpp/`. Common register lists in `dcn10_dpp.h` map logical registers such as `SCL_MODE`, `FORMAT_CONTROL`, `DPP_CONTROL`, `DSCL_MEM_PWR_CTRL`, and `CM_*` tables to instance-specific generated names. Runtime code in `dcn10_dpp.c`, `dcn10_dpp_dscl.c`, `dcn10_dpp_cm.c`, and later DCN DPP implementations then uses those register tables through generic helper macros.

Cross-generation integration is also relevant. Headers such as `dcn_3_0_1_sh_mask.h`, `dcn_3_5_1_sh_mask.h`, and `dcn_3_6_0_offset.h` contain similar DPP/CM/DSCL/CNVC/perfmon names, but offsets and field availability can differ. Consumers must bind the correct offset and mask header pair for the target ASIC.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. Shift and mask constants compile cleanly even when wrong, but a bad value can update the wrong field, leave stale bits behind, truncate a coefficient, corrupt a neighboring field, or decode live status incorrectly.

Chunk-boundary risk is high in this work item. The first lines are only the tail of `DSCL1_LB_MEMORY_CTRL` masks without the full preceding register context, and the final lines stop at `CM2_CM_GAMCOR_RAMA_OFFSET_R` before the remaining CM2 RAM A region descriptors. The final per-file report should not infer complete DPP1 DSCL or CM2 gamma coverage from this chunk alone.

Color-management fields are precision-sensitive. The CSC/gamut matrices use packed 16-bit coefficients, gamma/blend/shaper data fields use 18-bit-style data masks, and 3D LUT data has both standard and 30-bit paths. Incorrect masks or shifts can cause visible color errors, banding, wrong gamut remap, bad HDR/shaper behavior, or LUT programming that appears successful but produces wrong output.

Indexed LUT programming is ordering-sensitive. LUT index, data, write color mask, host select, config mode, and read/debug selectors must be sequenced by the caller. This header does not say which updates require blanking, update locks, pipe disable, or current-mode polling. Those rules must come from the DC code and hardware programming guide.

DSCL fields affect geometry and sampling. Wrong scale ratios, phase init fields, tap counts, coefficient RAM selectors, recout/MPC sizes, overscan, or line-buffer partitioning can produce distorted images, chroma misalignment, underflow, clipped output, or hangs that occur only for certain formats, rotations, scaling ratios, or multi-pipe layouts.

Power and reset fields can be hazardous. `DSCL*_DSCL_MEM_PWR_CTRL`, `DSCL*_OBUF_MEM_PWR_CTRL`, `CM1_CM_MEM_PWR_CTRL*`, `DPP_TOP2_DPP_SOFT_RESET`, and clock-gate-disable fields interact with block availability. Incorrect use can force memories off while active, fail to restore state after power transitions, or leave update/status bits stuck.

Perfmon fields can be misleading if masks are wrong. Event selection, counter select, compare value, restart, interrupt, and state fields may still return plausible values while counting the wrong event or clearing the wrong status. This is a diagnostic risk rather than a direct display-output risk, but it can hide real performance regressions.

The generated namespace is highly repetitive across DPP instances. A field that is correct for DPP1 may look identical for DPP2 while binding to a different register address through the offset header. Mixing DCN generations or pairing `dcn_3_0_0_sh_mask.h` with the wrong offset header would be a systemic failure mode.

## Test Signals

Useful validation is mostly generated-header, build, and hardware-behavior oriented:

- Compile coverage for all DCN 3.0/3.0.2 include sites: resource construction, IRQ service, GPIO factory/translate, clock manager, and DMUB support.
- Generated-register consistency checks that every `*_MASK` has a matching `*_SHIFT`, expected width, and matching register offset in `dcn_3_0_0_offset.h`.
- Cross-generation diffs against `dcn_3_0_1_sh_mask.h` and later DCN headers, with expected differences reviewed against the ASIC register database.
- DPP/DSCL display tests for bypass, upscaling/downscaling, chroma 4:2:0 paths, non-integer ratios, overscan, multi-plane composition, and recout/MPC size changes.
- Color-management tests for post-CSC, gamut remap, gamma correction, blend gamma, shaper LUT, 3D LUT, HDR multiplier, coefficient format, and suspend/resume restoration.
- CNVC tests for surface pixel formats, alpha enable, format conversion, crossbar mapping, color keying, pre-CSC/pre-degamma/pre-realpha, and cursor color/FP scale-bias behavior.
- Power-management tests that exercise DSCL/OBUF/CM memory power, DPP clock gating, soft reset, display idle, modeset, hotplug, runtime PM, and system suspend/resume.
- CRC tests using `DPP_TOP2_DPP_CRC_*` to verify region/component selection and output stability for known frames.
- Perfmon tests that select known events, start/restart counters, validate high/low readback, compare-value behavior, and interrupt/state handling.

Regression symptoms from bad constants include blank or distorted display output, incorrect scaling or chroma alignment, color shifts, LUT banding, HDR errors, alpha/cursor artifacts, stale update-pending bits, failed memory-power transitions, broken CRC capture, misleading perf counters, or failures that appear only on DCN 3.0/3.0.2 ASICs.

## Cross-Chunk Notes

This is not a standalone source module. It is a generated register-layout slice inside `dcn_3_0_0_sh_mask.h`. The preceding chunk owns the start of the DPP1 DSCL scaler and line-buffer groups, and the following chunk owns the rest of CM2 gamma-correction RAM region descriptors and subsequent DPP2 material. The merge/reconciliation lane should treat this document as the DPP1 CM/perfmon and early DPP2 middle portion of the full DCN 3.0.0 shift/mask contract.

### subset-b-001695: lines 19828-22333

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 19828-22333

## Scope

This chunk is part of the generated AMD DCN 3.0.0 ASIC register shift/mask header. It covers lines 19828-22333 and exports 2,113 preprocessor constants: 1,056 `__SHIFT` constants and 1,057 `_MASK` constants. There are no C functions, structs, enums, or executable statements; the API is the generated macro namespace used by AMDGPU display register helper code.

The slice starts in the tail of DPP2 color-management gamma-correction RAM A region metadata and ends mid-way through DPP3 gamma-correction RAM B region metadata at `CM3_CM_GAMCOR_RAMB_REGION_18_19`. Whole-file reconciliation should merge this with neighboring chunks to describe the complete DCN 3.0.0 register map.

## Purpose

The purpose of this chunk is to bind symbolic DCN 3.0.0 display register fields to exact bit positions and masks. Runtime driver code uses these macros through `REG_SET`, `REG_UPDATE`, `REG_GET`, `TF_SF`, `SF`, and instance register-list macros rather than hard-coding packed bitfield values.

Major hardware domains represented here are:

- `CM2` color-management registers for DPP instance 2, including the tail of `CM_GAMCOR_RAMA`, full `CM_GAMCOR_RAMB`, blending gamma RAM A/B, HDR multiplier, memory power control/status, dealpha, coefficient format, shaper LUT RAM A/B, and HDR 3D LUT control/data/output normalization.
- `DC_PERFMON14` performance-counter registers in the DPP2 performance-monitor address block, including counter control, counter state, monitor control, current-value interrupt status/clear/mask fields, and high/low counter value readback.
- `DPP_TOP3` top-level DPP instance 3 control, soft reset, CRC value/control, and host-read control fields.
- `CNVC_CFG3` and `CNVC_CUR3` converter and cursor-color fields for DPP instance 3, including surface pixel format, alpha/dealpha/re-alpha handling, expansion/rounding/clamp controls, pre-CSC matrices, pre-degamma, color keying, cursor mode/color, and cursor FP scale/bias.
- `DSCL3` scaler and line-buffer fields for DPP instance 3, including coefficient RAM, scaler mode/taps/ratios/init values, manual replication, black color, update/autocal, overscan, OTG blank timing, RECOUT/MPC sizing, line-buffer format/counters, DSCL memory power, and output-buffer power/control.
- `CM3` color-management registers for DPP instance 3, including post-CSC matrices, gamut remap matrices, channel bias, gamma-correction LUT control/data, and gamma-correction RAM A plus the beginning of RAM B region descriptors.

## Important API Surface

The exported API shape is the generated pair:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

Important groups in this chunk include:

- `CM2_CM_GAMCOR_RAMB_*` and `CM3_CM_GAMCOR_RAMA/RAMB_*` fields for gamma-correction piecewise LUT start, slope, base, end, offset, and per-region segment descriptors. These are consumed by DCN30 DPP color-management code when programming `dpp3_program_gamcor_lut`.
- `CM2_CM_BLNDGAM_CONTROL`, `CM2_CM_BLNDGAM_LUT_INDEX`, `CM2_CM_BLNDGAM_LUT_DATA`, and RAM A/B descriptor fields for blend gamma LUT programming.
- `CM2_CM_SHAPER_*` fields for shaper LUT mode, channel offset/scale, LUT write selection, RAM A/B region setup, and LUT data writes.
- `CM2_CM_3DLUT_MODE`, `CM2_CM_3DLUT_INDEX`, `CM2_CM_3DLUT_DATA`, `CM2_CM_3DLUT_DATA_30BIT`, `CM2_CM_3DLUT_READ_WRITE_CONTROL`, and output normalization/offset fields for HDR 3D LUT programming.
- `CM2_CM_MEM_PWR_CTRL`, `CM2_CM_MEM_PWR_STATUS`, `CM2_CM_MEM_PWR_CTRL2`, and `CM2_CM_MEM_PWR_STATUS2` fields for LUT, shaper, 3D LUT, and gamma memory power force/disable/low-power/status controls.
- `DC_PERFMON14_PERFCOUNTER_*` and `DC_PERFMON14_PERFMON_*` fields for selecting performance sources, arming counters, defining window/start/stop events, and reporting or clearing current-value interrupt conditions.
- `DPP_TOP3_DPP_CONTROL`, `DPP_TOP3_DPP_SOFT_RESET`, and `DPP_TOP3_DPP_CRC_CTRL` fields for DPP3 enable, reset, alpha selection, CRC selection, CRC enable, continuous mode, region mode, and CRC mask/valid state.
- `CNVC_CFG3_FORMAT_CONTROL`, `CNVC_CFG3_PRE_CSC_*`, `CNVC_CFG3_PRE_DEGAM`, and `CNVC_CFG3_PRE_REALPHA` fields used by DPP setup and format conversion paths.
- `DSCL3_SCL_*`, `DSCL3_RECOUT_*`, `DSCL3_MPC_SIZE`, `DSCL3_LB_*`, `DSCL3_DSCL_MEM_PWR_*`, and `DSCL3_OBUF_*` fields used by scaler, line-buffer, and output-buffer programming.
- `CM3_CM_POST_CSC_*`, `CM3_CM_GAMUT_REMAP_*`, `CM3_CM_BIAS_*`, and `CM3_CM_GAMCOR_*` fields used by DPP3 color transforms and gamma correction.

## Control Flow

This header chunk has no local control flow. Runtime behavior is supplied by AMD display code that includes the DCN 3.0.0 mask header, binds the macros into per-block register tables, and then performs ordered register programming through display helper macros.

The typical external flow is:

- DCN30 resource construction builds DPP, scaler, color-management, IRQ, GPIO, clock, and DMUB register tables from matching offset and shift/mask headers.
- Plane setup programs `CNVC_CFG3` format, conversion, pre-CSC, pre-degamma, alpha, and cursor-color fields according to the selected framebuffer format and color pipeline.
- Scaling setup programs `DSCL3` coefficient RAM, taps, ratios, initial phases, RECOUT/MPC dimensions, line-buffer format, autocal/update state, and memory-power fields.
- Color-management setup powers LUT memories, selects RAM A or RAM B, writes region descriptors and LUT entries, then flips the active mode for gamma correction, blend gamma, shaper, and 3D LUT blocks.
- Status/readback paths query current shaper and 3D LUT mode fields, DPP CRC values, memory power status bits, line-buffer counters, and perf monitor counters.

Ordering is an implicit hardware contract enforced by callers such as `drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.c` and `drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp_cm.c`. For example, LUT programming must select the intended RAM bank and write-enable mask before streaming LUT data, and memory power bits must be set before depending on LUT or scaler RAM contents.

## State and Persistence

The file stores no software state. The macros describe memory-mapped hardware state that persists inside DCN display blocks while those blocks remain powered:

- Color LUT data, RAM-bank selection, mode-current fields, region start/end/base/slope descriptors, and offsets persist as the active plane color pipeline until reprogrammed, bypassed, power-gated, or reset.
- `CM2` memory power controls affect whether LUT/shaper/3D-LUT/gamma memories retain valid contents and whether status bits report powered, low-power, or disabled states.
- Converter state persists the active surface interpretation: pixel format, alpha handling, color keying, clamping, component expansion, pre-CSC matrices, and pre-degamma mode.
- Scaler state persists coefficient RAM contents, taps, ratios, phase initialization, output rectangle, MPC size, line-buffer format, blanking reference fields, and output-buffer power state.
- CRC and performance-monitor registers hold live measurement state, sticky status, clear bits, selected counter sources, and captured counter values.

Incorrect constants can therefore corrupt persistent hardware programming until a modeset, DPP reprogramming, display block reset, GPU reset, or power transition restores valid register contents.

## Dependencies and Integration Points

This chunk depends on the matching DCN 3.0.0 register offset header and on AMD display register helper macros that paste register and field identifiers into generated `__SHIFT` and `_MASK` symbols. The constants are only meaningful when paired with the correct DCN 3.0.0 register addresses.

Direct include points for `dcn_3_0_0_sh_mask.h` include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`, which wires DCN30 display resources and register tables.
- `drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c` and `drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c`, which need the same generated field metadata for interrupt setup.
- `drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c` and `hw_translate_dcn30.c`, plus `drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c` and `dmub_dcn302.c`, which share DCN30 register metadata with DMUB-side helpers.

Important functional consumers include `drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.h`, `dcn30_dpp.c`, and `dcn30_dpp_cm.c`. Those files define DPP3 field lists and use fields visible in this chunk for post-CSC/gamut remap, converter setup, cursor attributes, scaler setup, blend gamma programming, shaper LUT programming, HDR 3D LUT programming, gamma-correction LUT programming, state readback, and deferred update handling.

## Risks

- A wrong mask or shift silently writes unrelated hardware bits. The highest-risk fields here are LUT RAM bank selection, LUT write masks, memory power controls, scaler ratios/taps, surface format controls, color matrices, and CRC/perfmon clear or status fields.
- DPP instance drift is likely because `CM2` and `CM3` use near-identical register families. A bad generated instance prefix or copied field can affect only one pipe, making failures dependent on display topology or plane assignment.
- Region descriptor macros repeat 34 gamma/shaper regions with paired `LUT_OFFSET` and `NUM_SEGMENTS` fields. An off-by-one region, swapped RAM A/B selector, or channel mismatch can create color artifacts without compile-time failures.
- Some fields are write-one-to-clear or status/mask/control mixes, especially in CRC and performance-monitor interrupt registers. Incorrect read-modify-write usage can drop measurement events or leave sticky flags uncleared.
- Memory power bits gate LUT and scaler memories. Programming data while RAM is disabled or trusting stale status masks can produce intermittent color/scaler failures after suspend, clock gating, or power transitions.
- `DC_PERFMON14` values are diagnostic but still sensitive: incorrect counter source, state, or interrupt masks can invalidate performance data and mislead debug or validation work.
- The chunk boundary is mid-family: it begins after the first `CM2_CM_GAMCOR_RAMA` fields and ends before all `CM3_CM_GAMCOR_RAMB` fields. Isolated edits or review of this chunk can miss cross-boundary consistency problems.

## Test Signals

Useful validation signals for changes to this chunk are:

- Build AMDGPU display code for DCN30 and DCN302 configurations to catch renamed, missing, or mismatched shift/mask macros in DPP, IRQ, GPIO, clock, resource, and DMUB paths.
- Static comparison against the vendor register database and the adjacent generated DCN 3.0.0 offset/mask files, especially verifying every `__SHIFT` has the intended `_MASK` and matching register offset.
- Multi-plane display tests that force use of DPP2 and DPP3, including format conversion, cursor composition, scaling, RECOUT/MPC sizing, and line-buffer behavior.
- Color pipeline tests for post-CSC, pre-CSC, gamut remap, gamma correction, blend gamma, shaper LUT, HDR 3D LUT, HDR multiplier, dealpha, and bias programming; visual CRC, readback, or color ramp tests are good signals.
- Suspend/resume and display idle/power-gating tests that verify `CM2` and `DSCL3` memory power state fields converge and LUT/scaler contents are restored when required.
- CRC/performance-monitor smoke tests that arm counters, check high/low readback, clear current-value interrupt status, and verify DPP3 CRC valid/status fields under active scanout.

## Chunk Notes

This is generated register metadata, not logic. The main research value is mapping the hardware surfaces covered by the constants: DPP2 advanced color LUTs and perf monitoring, plus DPP3 top/converter/cursor/scaler/color-management fields. The final merged file report should connect this slice with neighboring chunks to cover complete DPP2 and DPP3 register families.

### subset-b-001696: lines 22334-24838

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 22334-24838

## Scope

This chunk is chunk 10 of the oversized generated DCN 3.0.0 register mask header. It covers lines 22334-24838 of `dcn_3_0_0_sh_mask.h`, beginning inside the `CM3_CM_GAMCOR_RAMB_REGION_*` table, finishing most of the DPP3 color-management register masks, then switching into DPP4 top, format conversion, cursor, scaler, and color-management masks. The final visible line starts `CM4_CM_BLNDGAM_RAMA_REGION_30_31`, so the DPP4 blend-gamma RAMA table continues into the next chunk.

The file is a generated C preprocessor header. It contains no functions, storage definitions, structs, or runtime control flow. Its API is the set of `#define` constants named `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`, consumed by AMD DC register helper macros to pack, unpack, update, and poll MMIO bitfields.

## Purpose

This chunk supplies bit positions and bit masks for display pipe processor register fields in DCN 3.0.0 hardware. The definitions let the AMD display driver use symbolic field names instead of literal bit operations when programming:

- DPP3 color-management gamma correction, blend gamma, shaper LUT, 3D LUT, memory power, and test/debug registers.
- DC performance monitor instance 15 counter, control, interrupt, and value registers.
- DPP4 top-level DPP control, soft reset, CRC, and host read controls.
- DPP4 CNVC format-conversion and cursor controls, including surface format, alpha/color keying, pre-CSC matrices, pre-degamma, pre-dealpha, and pre-realpha fields.
- DPP4 DSCL scaler coefficient RAM, scaler mode, taps, ratios, initial phases, overscan, recout/MPC size, line-buffer settings, memory power controls, OBUF control, and blanking/viewport fields.
- DPP4 CM post-CSC, gamut remap, bias, gamma-correction RAM/LUT, and the beginning of blend-gamma RAMA definitions.

The constants are part of the hardware ABI for the DCN 3.0 register layout. A wrong mask or shift would compile successfully but steer later register writes into the wrong hardware bits.

## Important Macro Surfaces

### DPP3 Color Management Tail

The first part of the chunk is still in the DPP3 color-management block and starts mid-table:

- `CM3_CM_GAMCOR_RAMB_REGION_20_21` through `CM3_CM_GAMCOR_RAMB_REGION_32_33` define gamma-correction RAMB region LUT offsets and segment counts. Each pair uses a stable packing pattern: even region offset at shift `0x0`, even region segment count at `0xc`, odd region offset at `0x10`, and odd region segment count at `0x1c`; masks are `0x000001FFL`, `0x00007000L`, `0x01FF0000L`, and `0x70000000L`.
- `CM3_CM_BLNDGAM_CONTROL`, `CM3_CM_BLNDGAM_LUT_INDEX`, `CM3_CM_BLNDGAM_LUT_DATA`, and `CM3_CM_BLNDGAM_LUT_CONTROL` expose blend-gamma mode/select/current-state fields plus host LUT index/data/read/write controls.
- `CM3_CM_BLNDGAM_RAMA_*` and `CM3_CM_BLNDGAM_RAMB_*` define piecewise linear blend-gamma RAM programming for both RAM banks. Per color channel, start controls include start value and start segment, start slope/base use 18-bit masks, end controls split end base and end/slope words, offsets use 19-bit masks, and region tables cover regions 0 through 33 in pairs.
- `CM3_CM_HDR_MULT_COEF`, `CM3_CM_DEALPHA`, and `CM3_CM_COEF_FORMAT` provide color pipeline coefficient/de-alpha formatting controls.
- `CM3_CM_MEM_PWR_CTRL`, `CM3_CM_MEM_PWR_STATUS`, `CM3_CM_MEM_PWR_CTRL2`, and `CM3_CM_MEM_PWR_STATUS2` expose memory power force/disable/mode/state fields for CM LUT memories, 3D LUTs, and related RAMs.
- `CM3_CM_SHAPER_*` covers shaper offset/scale, LUT index/data/write masks, and RAMA/RAMB piecewise region programming.
- `CM3_CM_3DLUT_*` covers 3D LUT mode/size/current mode, LUT index/data words, 30-bit data mode, read/write enable, RAM select, read select, output normalization, and per-channel output scale/offset.
- `CM3_CM_TEST_DEBUG_INDEX` and `CM3_CM_TEST_DEBUG_DATA` expose CM test/debug selector and data fields.

These DPP3 names align with color-management programming paths in the DPP helpers. For example, the DPP code reads 3D LUT and blend-gamma status through `CM_3DLUT_*` and `CM_BLNDGAM_*` field names after the DPP register-list macros map the instance-specific register names.

### DC Performance Monitor 15

The `dce_dc_dpp3_dispdec_dpp_dcperfmon_dc_perfmon_dispdec` block defines `DC_PERFMON15_*` fields:

- `DC_PERFMON15_PERFCOUNTER_CNTL` selects event, counted value, increment mode, hardware control, run-enable mode, counter offset behavior, restart, interrupt enable, active status, and counter-control selector. It has dense high-bit control fields up to `PERFCOUNTER_CNTL_SEL` at mask `0xE0000000L`.
- `DC_PERFMON15_PERFCOUNTER_CNTL2` selects counted value type, hardware stop sources, counter-offset source, and secondary control selector.
- `DC_PERFMON15_PERFCOUNTER_STATE` packs state and state-select fields for eight counters, alternating 2-bit state and 2-bit selector nibbles.
- `DC_PERFMON15_PERFMON_CNTL` and `DC_PERFMON15_PERFMON_CNTL2` define performance monitor run, report count, counter-offset boolean behavior, interrupt type/status/ack, clock enable, and run-start/stop selectors.
- `DC_PERFMON15_PERFMON_CVALUE_INT_MISC`, `DC_PERFMON15_PERFMON_CVALUE_LOW`, `DC_PERFMON15_PERFMON_HI`, and `DC_PERFMON15_PERFMON_LOW` expose counter interrupt status/ack bits and sampled counter value words.

These macros are diagnostic and instrumentation infrastructure rather than display-mode policy. The high risk is stale field layout against the matching `dcn_3_0_0_offset.h` `mmDC_PERFMON15_*` addresses or later DCN family variants.

### DPP4 Top-Level Controls

The `dce_dc_dpp4_dispdec_dpp_top_dispdec` block starts DPP instance 4:

- `DPP_TOP4_DPP_CONTROL` contains clock gating/enable fields such as `DPP_CLOCK_ENABLE`, DPPCLK/DISPCLK gate-disable fields, and `DPP_TEST_CLK_SEL`.
- `DPP_TOP4_DPP_SOFT_RESET` supplies soft reset bits for CNVC, DSCL, CM, and OBUF sub-blocks.
- `DPP_TOP4_DPP_CRC_VAL_R_G`, `DPP_TOP4_DPP_CRC_VAL_B_A`, and `DPP_TOP4_DPP_CRC_CTRL` define DPP CRC value and control fields, including CRC enable, continuous mode, one-shot pending, 4:2:0 component select, source select, stereo/interlace/pixel/cursor format selects, and CRC mask.
- `DPP_TOP4_HOST_READ_CONTROL` exposes host-read rate control.

These fields integrate with resource and debug code that builds DPP register tables via `DPP_REG_LIST_DCN30(id)` and field tables via `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` / `_MASK` in `dcn30_resource.c`.

### DPP4 CNVC Format Conversion And Cursor

The `dce_dc_dpp4_dispdec_cnvc_cfg_dispdec` block defines format-converter fields:

- `CNVC_CFG4_CNVC_SURFACE_PIXEL_FORMAT` selects surface pixel format and alpha-plane enable.
- `CNVC_CFG4_FORMAT_CONTROL` includes format expansion, 16-bit conversion, alpha enable, CNVC bypass, MSB alignment, positive clamps, update-pending status, and R/G/B crossbar selectors.
- `CNVC_CFG4_FCNV_FP_BIAS_*` and `CNVC_CFG4_FCNV_FP_SCALE_*` define floating-point conversion bias and scale values for RGB channels.
- `CNVC_CFG4_COLOR_KEYER_*` provides enable/mode plus low/high threshold fields for alpha, red, green, and blue.
- `CNVC_CFG4_ALPHA_2BIT_LUT` packs four 2-bit alpha LUT entries.
- `CNVC_CFG4_PRE_DEALPHA`, `CNVC_CFG4_PRE_DEGAM`, and `CNVC_CFG4_PRE_REALPHA` expose pre-processing enables and degamma mode/select fields.
- `CNVC_CFG4_PRE_CSC_MODE`, `CNVC_CFG4_PRE_CSC_C*`, and `CNVC_CFG4_PRE_CSC_B_C*` define current-mode status and A/B coefficient matrix fields for pre-CSC.
- `CNVC_CFG4_CNVC_COEF_FORMAT` selects pre-CSC coefficient format.

The `dce_dc_dpp4_dispdec_cnvc_cur_dispdec` block defines cursor controls:

- `CNVC_CUR4_CURSOR0_CONTROL` includes cursor enable, expansion mode, pixel inversion mode, ROM enable, cursor mode, pixel alpha modulation, and update pending status.
- `CNVC_CUR4_CURSOR0_COLOR0` and `CNVC_CUR4_CURSOR0_COLOR1` define palette colors.
- `CNVC_CUR4_CURSOR0_FP_SCALE_BIAS` packs cursor floating-point scale and bias.

These fields feed plane format, cursor, color key, and input color conversion paths. Because many fields are state bits such as `*_UPDATE_PENDING` or `*_MODE_CURRENT`, callers may read them to confirm hardware state after programming double-buffered controls.

### DPP4 DSCL Scaler

The `dce_dc_dpp4_dispdec_dscl_dispdec` block is broad and latency-sensitive:

- Coefficient RAM access: `DSCL4_SCL_COEF_RAM_TAP_SELECT` and `DSCL4_SCL_COEF_RAM_TAP_DATA` select tap pair, phase, filter type, even/odd coefficients, and coefficient enables.
- Mode and taps: `DSCL4_SCL_MODE`, `DSCL4_SCL_TAP_CONTROL`, `DSCL4_DSCL_CONTROL`, and `DSCL4_DSCL_2TAP_CONTROL` select DSCL mode, coefficient RAM source/current/readback, chroma/alpha coefficient modes, vertical/horizontal luma and chroma tap counts, boundary mode, and 2-tap hardcode/sharpness fields.
- Ratios and phases: `DSCL4_SCL_HORZ_FILTER_SCALE_RATIO`, `DSCL4_SCL_HORZ_FILTER_INIT`, chroma `*_C` equivalents, `DSCL4_SCL_VERT_FILTER_SCALE_RATIO`, `DSCL4_SCL_VERT_FILTER_INIT`, bottom-field variants, and chroma/bottom-field variants provide horizontal/vertical scale ratios and fixed-point integer/fractional initialization.
- Viewport and output geometry: `DSCL4_DSCL_EXT_OVERSCAN_LEFT_RIGHT`, `DSCL4_DSCL_EXT_OVERSCAN_TOP_BOTTOM`, `DSCL4_OTG_H_BLANK`, `DSCL4_OTG_V_BLANK`, `DSCL4_RECOUT_START`, `DSCL4_RECOUT_SIZE`, and `DSCL4_MPC_SIZE` pack overscan, blanking, recout start/size, and MPC dimensions.
- Line buffer and memory: `DSCL4_LB_DATA_FORMAT`, `DSCL4_LB_MEMORY_CTRL`, `DSCL4_LB_V_COUNTER`, `DSCL4_DSCL_MEM_PWR_CTRL`, `DSCL4_DSCL_MEM_PWR_STATUS`, `DSCL4_OBUF_CONTROL`, and `DSCL4_OBUF_MEM_PWR_CTRL` define alpha/interleave, memory partitioning, counters, LUT/LB memory power force/disable/mode/state, OBUF bypass/full-buffer/half-width/hold count, and OBUF memory power.
- Update/autocal: `DSCL4_DSCL_UPDATE` exposes scaler update pending, and `DSCL4_DSCL_AUTOCAL` selects autocal mode, pipe count, and pipe ID.

Runtime DPP scaler code uses corresponding generic names such as `DSCL_MEM_PWR_CTRL`, `DSCL_MEM_PWR_STATUS`, `SCL_MODE`, `SCL_TAP_CONTROL`, and `DSCL_AUTOCAL` through per-instance register arrays. Incorrect DSCL shifts can lead to visible scaler artifacts, invalid viewport programming, hangs while polling memory power state, or silent corruption of line-buffer partitioning.

### DPP4 Color Management Start

The `dce_dc_dpp4_dispdec_cm_dispdec` block defines the start of DPP4 CM:

- `CM4_CM_CONTROL` and `CM4_CM_POST_CSC_CONTROL` define CM enable/mode and post-CSC mode/current status.
- `CM4_CM_POST_CSC_C*` and `CM4_CM_POST_CSC_B_C*` define A/B matrix coefficient pairs for post-CSC. Most coefficient-pair registers pack two signed/fixed-width coefficients with low/high halfword masks.
- `CM4_CM_GAMUT_REMAP_CONTROL`, `CM4_CM_GAMUT_REMAP_C*`, and `CM4_CM_GAMUT_REMAP_B_C*` mirror that pattern for gamut remap.
- `CM4_CM_BIAS_CR_R` and `CM4_CM_BIAS_Y_G_CB_B` define bias fields for chroma/red and Y/green/CB/blue paths.
- `CM4_CM_GAMCOR_CONTROL`, `CM4_CM_GAMCOR_LUT_INDEX`, `CM4_CM_GAMCOR_LUT_DATA`, and `CM4_CM_GAMCOR_LUT_CONTROL` define gamma-correction mode/select/current state plus LUT host access.
- `CM4_CM_GAMCOR_RAMA_*` and `CM4_CM_GAMCOR_RAMB_*` provide gamma-correction PWL RAM programming for both banks, including start/end/base/slope/offset and paired region tables 0 through 33.
- `CM4_CM_BLNDGAM_CONTROL`, `CM4_CM_BLNDGAM_LUT_INDEX`, `CM4_CM_BLNDGAM_LUT_DATA`, and `CM4_CM_BLNDGAM_LUT_CONTROL` begin DPP4 blend-gamma control and LUT access.
- `CM4_CM_BLNDGAM_RAMA_*` starts the DPP4 blend-gamma RAMA table and reaches `CM4_CM_BLNDGAM_RAMA_REGION_30_31` at the chunk boundary. The matching `REGION_32_33` and RAMB definitions continue in chunk `subset-b-001697`.

The DPP4 CM region mirrors the DPP3 CM pattern earlier in this chunk. That symmetry is an important validation signal: mismatches between `CM3_` and `CM4_` field layouts in otherwise repeated blocks should be intentional hardware differences, not manual edits.

## Control Flow And State Behavior

There is no executable control flow in this header. The relevant flow is compile-time expansion:

1. DCN resource files include `dcn/dcn_3_0_0_offset.h` and `dcn/dcn_3_0_0_sh_mask.h`.
2. Register-list macros, for example the DPP register list in DCN30 resource code, expand address constants from the offset header into per-block register structures.
3. Field-list macros expand this header's `__SHIFT` and `_MASK` constants into mask/shift structures.
4. Runtime helper macros such as `REG_UPDATE`, `REG_SET`, `REG_GET`, and `REG_WAIT` use those structures to read-modify-write or poll MMIO fields.

The state represented here is hardware register state, not software persistence:

- `*_MODE`, `*_SELECT`, `*_WRITE_*`, `*_FORCE`, and `*_DIS` fields are writable controls.
- `*_CURRENT`, `*_UPDATE_PENDING`, `*_STATE`, `*_STATUS`, `*_ACTIVE`, and counter value fields are readback/status signals.
- RAM/LUT index/data/control fields expose host-programmed tables whose persistence is in display hardware until reprogrammed, reset, power-gated, or reinitialized by the display stack.
- Memory power fields (`CM3_CM_MEM_PWR_*`, `DSCL4_DSCL_MEM_PWR_*`, `DSCL4_OBUF_MEM_PWR_*`) are especially stateful because write-side force/disable fields and read-side state fields are paired and often polled.

## Dependencies And Integration Points

This chunk depends on the matching register-address header for DCN 3.0.0. Field macros alone do not identify MMIO addresses; they are paired with `dcn_3_0_0_offset.h` entries such as `mmDPP_TOP4_*`, `mmCNVC_CFG4_*`, `mmDSCL4_*`, `mmCM4_*`, and `mmDC_PERFMON15_*`.

Local include sites for `dcn_3_0_0_sh_mask.h` include:

- `display/dc/resource/dcn30/dcn30_resource.c`, where the DPP register and mask/shift tables are built.
- `display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`, `display/dmub/src/dmub_dcn30.c`, and `display/dmub/src/dmub_dcn302.c`.
- DCN30/302 IRQ service files and DCN30 GPIO factory/translation files.

The most direct consumer family for this chunk is the DPP code under `display/dc/dpp/`, particularly common DCN10/DCN20/DCN30 DPP and DSCL helpers. Those helpers use generic field names after the register-list macros resolve instance-specific prefixes. Examples visible in the local tree include reads of `CM_3DLUT_*` and `CM_BLNDGAM_*` status in DPP code and writes/polls of `DSCL_MEM_PWR_CTRL` and `DSCL_MEM_PWR_STATUS` in DSCL memory-power handling.

## Risks

- Generated-header drift: if this file is regenerated from a different hardware description than `dcn_3_0_0_offset.h`, the compiler will not catch semantic mismatches between register addresses and bitfields.
- Instance skew: this chunk switches from DPP3 to DPP4. Copy/paste or generation errors can silently put a DPP3 field layout under a DPP4 name, or miss a DPP4-specific field. The repeated CM RAMA/RAMB tables make this hard to review manually.
- Boundary incompleteness: the chunk starts in the middle of `CM3_CM_GAMCOR_RAMB_REGION_*` and ends in the middle of `CM4_CM_BLNDGAM_RAMA_REGION_*`. Whole-file synthesis must merge adjacent chunks before drawing conclusions about complete table coverage.
- Status/control confusion: fields ending in `CURRENT`, `UPDATE_PENDING`, `STATE`, `STATUS`, or `ACTIVE` are readback/status fields in many call paths. Treating them as ordinary writable configuration bits can produce ineffective writes or incorrect waits.
- Memory power polling risk: wrong `*_MEM_PWR_STATE` masks or shifts can make `REG_WAIT` loops wait on the wrong bits, leading to timeouts or using RAM blocks before they are powered.
- DSCL visual correctness risk: wrong scaler tap, ratio, phase, overscan, or line-buffer fields can produce visible corruption, underflow, or mode-set failures without a clean compile-time error.
- Perfmon diagnostic risk: `DC_PERFMON15_*` mistakes may only show under debug/performance tooling, making regressions easy to miss in normal display validation.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware/display behavior:

- Build coverage for DCN30 and DCN302 display code that includes `dcn_3_0_0_sh_mask.h`, especially `dcn30_resource.c`, DPP, DSCL, DMUB, IRQ, and clock manager objects.
- Register table initialization should compile without missing field symbols from `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` and `_MASK`.
- Display mode-set tests covering DPP4 planes should exercise CNVC format conversion, cursor enable/color modes, DSCL scaling ratios/taps, recout sizing, and CM post-CSC/gamut/gamma programming.
- Plane scaling tests should cover luma/chroma paths, bottom-field vertical init fields, bypass/scaling mode changes, and line-buffer partition programming.
- Color pipeline tests should cover post-CSC, gamut remap, gamma correction, blend gamma, shaper, and 3D LUT programming with readback of current/pending/status fields where available.
- Power-management tests should exercise DSCL/OBUF/CM memory power force/disable/state fields and verify waits do not time out.
- CRC and perfmon debug tests should verify DPP4 CRC controls/value registers and `DC_PERFMON15_*` counter setup/readback.
- Header consistency checks should diff repeated CM3/CM4 and RAMA/RAMB region layouts, and compare this header against adjacent DCN family generated headers where hardware compatibility is expected.

## Cross-Chunk Notes

- Previous chunk `subset-b-001695` is needed for the beginning of `CM3_CM_GAMCOR_RAMB_REGION_*` and earlier DPP3 CM state.
- Next chunk `subset-b-001697` is needed to complete `CM4_CM_BLNDGAM_RAMA_REGION_30_31`, `REGION_32_33`, and the remaining DPP4 blend-gamma RAMB or later register definitions.
- The final per-file report should synthesize all 29 chunks and avoid treating this chunk as an independently complete DPP3 or DPP4 register map.

### subset-b-001697: lines 24839-27351

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 24839-27351

## Scope

This chunk is a generated AMD DCN 3.0.0 register field header slice. It exports preprocessor constants only: `__SHIFT` bit positions and `_MASK` bit masks for fields in DPP4 and DPP5 display-pipe registers. There are no C functions, structs, enums, or local algorithms in this range.

The covered hardware domains are:

- Tail of DPP4 color-management (`CM4`) blend gamma RAM A/B, HDR multiplier, color-management memory power, dealpha, coefficient format, shaper LUT, shaper RAM A/B, and 3D LUT fields.
- DPP4 perfmon instance 16 (`DC_PERFMON16`) counter control, counter state, perfmon control, and value registers.
- DPP5 top (`DPP_TOP5`) control, soft reset, CRC, and host-read fields.
- DPP5 CNVC config/cursor (`CNVC_CFG5`, `CNVC_CUR5`) format conversion, FP bias/scale, color keyer, alpha LUT, pre-dealpha, pre-CSC, pre-degamma, pre-realpha, and cursor fields.
- DPP5 DSCL (`DSCL5`) scaler coefficient RAM, scaling mode/taps/ratios/init, overscan, output geometry, line-buffer format/memory, memory power, and output-buffer power fields.
- Start and middle of DPP5 color-management (`CM5`) control, post-CSC, gamut remap, bias, gamma correction RAM A/B, blend gamma RAM A/B, HDR multiplier, memory power, dealpha, coefficient format, and shaper fields.

The line range starts mid-register at `CM4_CM_BLNDGAM_RAMA_REGION_30_31` and ends mid-register group at `CM5_CM_SHAPER_RAMA_START_CNTL_R`; whole-file reconciliation must join this with adjacent chunks for the complete `CM4` and `CM5` register maps.

## Purpose

The purpose of this chunk is to bind DCN 3.0 display driver code to exact field encodings for DPP color, scaler, converter, perfmon, CRC, and memory-power hardware. The companion offset header gives register addresses; this header gives the bit layout inside those registers. Functional code avoids hard-coded bit arithmetic by expanding these macros into typed shift/mask tables, then using register helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, and `REG_WAIT`.

For DCN30 DPP programming, these constants are consumed primarily through `display/dc/dpp/dcn30/dcn30_dpp.h`. `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)` initialize `struct dcn3_dpp_shift` and `struct dcn3_dpp_mask` in DCN30-family resource files. Runtime DPP methods then read and write fields by symbolic names such as `CM_BLNDGAM_MODE`, `CM_BLNDGAM_SELECT_CURRENT`, `HDR3DLUT_MEM_PWR_STATE`, `SHAPER_MEM_PWR_FORCE`, `LUT_MEM_PWR_STATE`, `FORMAT_CONTROL__ALPHA_EN`, and `CM_GAMCOR_MODE_CURRENT`.

## Important API Surface

The exported API surface is the macro namespace. Important groups include:

- Blend gamma fields for `CM4` and `CM5`: `CM_BLNDGAM_CONTROL`, `CM_BLNDGAM_LUT_INDEX`, `CM_BLNDGAM_LUT_DATA`, `CM_BLNDGAM_LUT_CONTROL`, RAM A/B start/end/base/slope/offset fields, and region descriptors `REGION_0_1` through `REGION_32_33`. Region registers pack two PWL regions per register with LUT offset fields at bits 0/16 and segment-count fields at bits 12/28.
- Gamma correction fields for `CM5`: `CM_GAMCOR_CONTROL`, LUT index/data/control, RAM A/B start/end/base/slope/offset fields, and 34 region descriptors.
- Shaper and 3D LUT fields: `CM_SHAPER_CONTROL`, offsets/scales, LUT index/data/write-enable, RAM A/B region descriptors, and `CM_3DLUT_*` mode, index, data, read/write, normalization, and output-offset fields in the `CM4` part of this slice.
- Color matrix and format fields: `CM_POST_CSC_*`, `CM_GAMUT_REMAP_*`, `CM_BIAS_*`, `CM_COEF_FORMAT`, `CNVC_CFG5_PRE_CSC_*`, `PRE_DEGAM`, `PRE_DEALPHA`, `PRE_REALPHA`, `FORMAT_CONTROL`, `CNVC_SURFACE_PIXEL_FORMAT`, and FP conversion bias/scale fields.
- Scaler fields: coefficient RAM tap select/data, mode, tap control, manual replicate, horizontal/vertical scale ratios and init values for luma/chroma, black color, update/autocal, overscan, OTG blanking, recout size/start, MPC size, line-buffer data format/memory control, DSCL memory power, and OBUF memory power.
- Diagnostics and monitoring fields: DPP5 CRC control/value fields, host-read rate control, and DPP4 `DC_PERFMON16` counter/perfmon control and value fields.
- Memory-power controls and status: `CM_MEM_PWR_CTRL`, `CM_MEM_PWR_STATUS`, `CM_MEM_PWR_CTRL2`, `CM_MEM_PWR_STATUS2`, `DSCL_MEM_PWR_CTRL`, `DSCL_MEM_PWR_STATUS`, `OBUF_MEM_PWR_CTRL`, and their force/disable/state fields.

The repeated `CM4_` and `CM5_` prefixes are instance-specific generated names. Consumer macros usually refer to instance 0 field names, for example `CM0_CM_BLNDGAM_CONTROL__CM_BLNDGAM_MODE_MASK`, then token-paste the desired instance through register-address tables. The bit layouts are expected to be identical across DPP instances.

## Control Flow

There is no local control flow in this header. Runtime control flow is external:

1. DCN30 resource construction includes `dcn_3_0_0_offset.h` and this mask header.
2. Macros such as `DPP_REG_LIST_DCN30(id)` populate per-DPP register-address tables for six DPP instances.
3. `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)` populate the corresponding field shift/mask tables.
4. DPP methods in `dcn30_dpp.c`, DPP scaler code, and shared color-management helpers use the tables through `REG_*` helpers.
5. Hardware latches selected fields on modeset, vupdate, or block-specific update boundaries; the header only defines the bit positions used by those writes.

Representative runtime paths tied to this chunk include:

- `dpp30_read_state()` reads current gamma correction, shaper, 3D LUT, and blend gamma modes through `CM_GAMCOR_CONTROL`, `CM_SHAPER_CONTROL`, `CM_3DLUT_MODE`, and `CM_BLNDGAM_CONTROL`.
- `dpp3_cnv_setup()` programs CNVC format, alpha, pre-dealpha/realpha, pre-CSC/post-CSC selection, pixel format, and cursor disable behavior for input surfaces.
- Blend gamma programming chooses the inactive RAM A/B bank, writes LUT entries through `CM_BLNDGAM_LUT_INDEX` and `CM_BLNDGAM_LUT_DATA`, programs PWL region start/end/segment metadata through `CM_BLNDGAM_RAMA_*` or `CM_BLNDGAM_RAMB_*`, and flips `CM_BLNDGAM_CONTROL` select/mode fields.
- Memory low-power paths clear force fields and wait for state fields when powering on, while deferred disable paths set force fields after bypass is latched. This applies to DSCL LUT memory, gamma correction, blend gamma, 3D LUT, and shaper memory.
- Scaler control paths program DSCL coefficient RAM, ratios, taps, init phases, output geometry, line-buffer partitioning, and memory-power state using the DSCL5-equivalent field layouts.

## State and Persistence

The header itself has no mutable software state or persistence. It defines compile-time constants that address hardware state in MMIO registers.

The hardware state represented by this chunk persists until reprogrammed, power-gated, reset, or overwritten by a later display update. Important state includes:

- Double-buffered transfer-function state in gamma correction, blend gamma, and shaper RAM A/B banks.
- LUT index/data cursors and write-color masks used while host-loading LUT payloads.
- Current versus requested mode/select fields for gamma, blend gamma, shaper, 3D LUT, post-CSC, pre-CSC, and gamut remap.
- PWL region metadata: start value, start segment, start slope/base, end value/base/slope, offset, LUT offsets, and segment counts.
- CNVC pixel format, alpha handling, color keying, pre-degamma, pre/post CSC, and cursor configuration.
- DSCL filter coefficients, scaling ratios, taps, init phase, output rectangles, line-buffer memory configuration, and autocal state.
- Sticky or latched diagnostic state in CRC and perfmon registers.
- Memory power force/disable/state fields for color-management and scaler memories.

Because many fields are double-buffered or update-boundary latched, a wrong field definition can create delayed symptoms: the write may appear to succeed but the active `*_CURRENT` field, selected LUT bank, or memory-power state changes on a later vupdate.

## Dependencies and Integration Points

This chunk is tightly coupled to:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`, which supplies the matching register offsets.
- DCN30-family resource files such as `display/dc/resource/dcn30/dcn30_resource.c`, `dcn301_resource.c`, `dcn302_resource.c`, `dcn303_resource.c`, `dcn31_resource.c`, `dcn314_resource.c`, and `dcn315_resource.c`, which initialize DPP register, shift, and mask tables.
- `display/dc/dpp/dcn30/dcn30_dpp.h`, where `DPP_REG_LIST_SH_MASK_DCN30_COMMON` and `DPP_REG_LIST_SH_MASK_DCN30_UPDATED` name the fields consumed from this generated header.
- `display/dc/dpp/dcn30/dcn30_dpp.c`, which reads state, sets CNVC format, programs post-CSC, handles blend gamma/shaper/3D LUT power, and drives blend LUT bank switching.
- Shared color-management helpers under `display/dc/dcn30/dcn30_cm_common.c` and older DPP color code, which program transfer functions and color matrices using register/mask bundles assembled from these macros.
- DSCL code in `display/dc/dpp/dcn10/dcn10_dpp_dscl.c`, `dcn20_dpp.c`, and DCN30 DPP paths, which uses DSCL memory-power and scaler field layouts.
- Debug and validation paths in hardware sequencer/resource code that expose DPP CRC state and perfmon state.

The generated field layout also integrates with DC debug options. For example, `enable_mem_low_power.bits.cm` controls whether `CM_MEM_PWR_CTRL*` fields are manipulated, and deferred register writes rely on `*_MODE_CURRENT` fields to verify bypass before forcing memories off.

## Risks

- Field drift is high impact. A wrong mask or shift still compiles but writes the wrong bits, causing corrupted color output, invalid scaling, broken cursor/alpha handling, stuck memory-power state, or broken diagnostics.
- The chunk contains many nearly identical RAM A/RAM B and R/G/B field groups. Copy/paste errors can affect only one color channel, one LUT bank, or one DPP instance, making failures mode- and pipe-specific.
- Double-buffered LUT selection is sensitive. Incorrect `CM_BLNDGAM_SELECT`, `CM_BLNDGAM_SELECT_CURRENT`, or region metadata fields can cause updates to program the active bank or fail to switch banks cleanly.
- Memory-power force/status fields are timing-sensitive. Bad masks for `GAMCOR_MEM_PWR_FORCE`, `BLNDGAM_MEM_PWR_FORCE`, `HDR3DLUT_MEM_PWR_FORCE`, `SHAPER_MEM_PWR_FORCE`, `LUT_MEM_PWR_FORCE`, or matching state fields can lead to waits timing out or blocks being powered down while active.
- Region descriptor widths are contract-critical. LUT offsets use 9-bit masks and segment counts use 3-bit masks in packed two-region registers; wrong limits can make generated PWL curves index outside expected hardware regions.
- CNVC format fields affect surface interpretation. Wrong pixel-format, alpha-plane, crossbar, clamp, color-key, pre-dealpha, or pre-CSC masks can produce channel swaps, alpha artifacts, or incorrect YCbCr/RGB conversion.
- DSCL coefficient and tap fields directly affect image quality and bounds. Bad masks can corrupt filter coefficients, scale ratios, recout/MPC geometry, or line-buffer partitioning.
- Perfmon and CRC fields are debug-facing but still important. Incorrect fields can make validation counters, CRC captures, or host-read diagnostics misleading.

## Test Signals

Good validation signals for this chunk combine build coverage, generated-header comparison, and display behavior:

- Build all DCN30-family AMDGPU display configurations so `DPP_REG_LIST_SH_MASK_DCN30`, resource initializers, and `REG_*` call sites catch missing or renamed macros.
- Diff this generated header against AMD register database output and adjacent DCN 3.x mask headers to catch unexpected field-width, shift, or instance-layout changes.
- Exercise modesets across all DPP instances with RGB and YCbCr formats, alpha formats, 10-bit/FP formats, cursor formats, color keying, and pre/post CSC enabled.
- Validate color-management paths: pre-degamma, gamma correction, blend gamma, shaper LUT, 3D LUT, gamut remap, HDR multiplier, and RAM A/B bank switching.
- Run suspend/resume and display idle/active transitions with color-management memory low power enabled, watching for `REG_WAIT` failures on CM and DSCL memory-power state fields.
- Test scaling paths with identity, upscaling, downscaling, chroma scaling, non-default taps, coefficient RAM programming, overscan, and line-buffer partition changes.
- Use CRC/perfmon debug reads to confirm DPP CRC values and perfmon counters remain plausible after modesets and pipe reconfiguration.
- Check visual output for channel swaps, banding, incorrect gamma, alpha/dealpha artifacts, scaler ringing, and pipe-specific failures on DPP4/DPP5.

## Chunk Notes

This is a constants-only generated slice, so its research value is the hardware contract rather than local logic. It is especially important because it bridges color-management LUT programming, scaler setup, format conversion, memory power, and diagnostics for late DPP4 and DPP5 blocks in DCN 3.0. Changes here should be treated as hardware-spec changes and validated against both generated register sources and real display/color/scaler behavior.

### subset-b-001698: lines 27352-29904

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 27352-29904

## Scope

This chunk is a generated AMDGPU DCN 3.0.0 register shift/mask header slice. It contains preprocessor constants only: no functions, structs, enums, global storage, or executable code. The exported surface is the usual generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macro pairs consumed by AMD display register helpers.

The range covers 2,553 source lines and 2,137 `#define` entries: 1,061 shift constants and 1,076 mask constants. The imbalance is caused by artificial chunk boundaries. The first line starts inside `CM5_CM_SHAPER_RAMA_START_CNTL_R`, after its first shift macro appeared in the previous chunk, and the last line starts `ODM5_OPTC_BYTES_PER_PIXEL`, whose mask and following ODM5 fields continue in the next chunk.

The covered hardware areas are late DPP5 color-management registers, DPP5 and OPP display performance monitors, six repeated OPP/FMT/DPG/OPPBUF/CRC instances, OPP top-level clock and ABM controls, six DSC-remapper forwarding blocks, and the beginning of six ODM/OPTC input blocks.

## Purpose

The file maps DCN 3.0.0 hardware bitfields to C macros so higher-level display code can program MMIO registers by field name instead of hard-coding bit numbers. This chunk supplies field layouts for:

- `CM5` color-management shaper RAM A/B region programming, shaper and 3D LUT memory power controls/status, 3D LUT indexed data access, output normalization/offset/scale, and test-debug index/data access.
- `DC_PERFMON17` under `dce_dc_dpp5_dispdec_dpp_dcperfmon_dc_perfmon_dispdec`, exposing DPP5 display performance counter setup, state, run control, interrupt status/ack, and counter value readback.
- `FMT0` through `FMT5`, covering output formatter clamp ranges, dynamic expansion, pixel encoding, subsampling, truncation, spatial/temporal dithering, random seeds, 4:2:0 memory power, and 4:2:2 edge handling.
- `DPG0` through `DPG5`, the display pattern generator blocks for test pattern enablement, mode, dynamic range, bit depth, resolution fields, ramp controls, colors, offsets, segment width, and double-buffer pending status.
- `OPPBUF0` through `OPPBUF5`, output pixel-processor buffer width/segmentation/repetition/3D-parameter/padding fields.
- `OPP_PIPE0` through `OPP_PIPE5`, pipe clock and digital bypass controls.
- `OPP_PIPE_CRC0` through `OPP_PIPE_CRC5`, CRC enable/mode/source/mask/result fields for output validation.
- `OPP_TOP_CLK_CONTROL` and `OPP_ABM_CONTROL`, top-level OPP clock gating/test-clock/ABM clock-on fields and ABM backlight PWM selection.
- `DSCRM0` through `DSCRM5`, DSC forwarding enable/source/status and double-buffer pending fields.
- `DC_PERFMON18` under `dce_dc_opp_opp_dcperfmon_dc_perfmon_dispdec`, exposing the OPP-level performance counter block.
- `ODM0` through the start of `ODM5`, describing OPTC input global reset/underflow/double-buffer fields, data source segment selection, DSC data format, bytes-per-pixel, width, input-clock, memory-select, and spare-register fields. `ODM5` is partial in this chunk.

Although the repository path is under `sources/distributed-fs/ceph-client`, this source is AMDGPU display hardware metadata. It has no Ceph filesystem, distributed-storage, or network behavior.

## Important APIs, Types, And Macros

There are no callable APIs or C types here. The API-like contract is the macro namespace:

- `*_SHIFT` gives the low bit position for a register field.
- `*_MASK` gives the already-shifted register mask for that field.
- Register-heading comments group the generated fields for one MMIO register.
- `addressBlock` comments identify generated hardware register blocks, not C scopes.

Important macro families in this chunk include:

- `CM5_CM_SHAPER_RAMA_*` and `CM5_CM_SHAPER_RAMB_*`: start/end controls per RGB channel and 34 exponential-region descriptors packed as region pairs. Region descriptors use LUT offset fields and segment-count fields, while start/end controls expose 18-bit or 16-bit range fields plus base/segment selectors.
- `CM5_CM_MEM_PWR_CTRL2` and `CM5_CM_MEM_PWR_STATUS2`: power force/disable and state fields for shaper and HDR 3D LUT memories.
- `CM5_CM_3DLUT_*`: mode/size/current-mode fields, 11-bit index, packed 16-bit data lanes, 30-bit data access, write-enable mask, RAM/read selectors, output normalization, and per-channel output offset/scale.
- `CM5_CM_TEST_DEBUG_INDEX` and `CM5_CM_TEST_DEBUG_DATA`: an indexed debug access pair with an 8-bit index, write-enable bit, and 32-bit data value.
- `DC_PERFMON17_*` and `DC_PERFMON18_*`: performance counter control fields such as event select, counted value select/type, increment mode, run-enable mode, hardware stop/start selectors, active state, counter state selectors, report count, counter-off interrupt status/ack, eight per-counter interrupt status/ack bits, and low/high value readback.
- `FMTn_FMT_*`: six repeated formatter instances. `FMT_BIT_DEPTH_CONTROL` is the densest formatter register, packing truncation, spatial dithering, temporal dithering, randomization, FRC selection, and reset fields. `FMT_CONTROL` carries stereo override, dither frame counter fields, pixel encoding, subsampling mode/order, CbCr bit-reduction bypass, and double-buffer pending status.
- `DPGn_DPG_*`: repeated pattern generator fields for enable, mode, dynamic range, bit depth, horizontal/vertical resolution encoding, field polarity, ramp offset/increment, active dimensions, two colors per component, X offset, segment width, and double-buffer pending.
- `OPPBUFn_OPPBUF_*` and `OPP_PIPEn_OPP_PIPE_CONTROL`: active width, display segmentation, overlap pixels, pixel repetition, pending status, 3D vactive space sizes, dummy RGB data, segment padding, pipe clock enable/on state, and digital bypass.
- `OPP_PIPE_CRCn_*`: per-pipe CRC enable, continuous mode, stereo/interlace modes, pixel/source select, one-shot pending, mask, and A/R/G/B/C result fields.
- `DSCRMn_DSCRM_DSC_FORWARD_CONFIG`: `DSCRM_DSC_FORWARD_EN`, `DSCRM_DSC_OPP_PIPE_SOURCE`, `DSCRM_DSC_DOUBLE_BUFFER_REG_UPDATE_PENDING`, and `DSCRM_DSC_FORWARD_EN_STATUS`.
- `ODMn_OPTC_*`: input soft reset, underflow interrupt enable/type/status/clear/current, double-buffer pending, input/output segment counts, segment source selectors, data format, DSC mode, DSC bytes per pixel, segment/slice widths, input clock gate/enable/on state, memory select, and spare register data.

## Control Flow

This chunk has no local control flow. Runtime behavior is supplied by consumers that include `dcn_3_0_0_offset.h` and this shift/mask header, build generation-specific register tables, and then access MMIO through AMD display helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_WAIT`, and `REG_READ`.

A typical path is:

1. DCN30/DCN302 display code includes the offset and shift/mask headers.
2. Register-list macros paste instance names such as `FMT0_FMT_CONTROL`, `DPG0_DPG_CONTROL`, `DSCRM0_DSCRM_DSC_FORWARD_CONFIG`, or `ODM0_OPTC_INPUT_GLOBAL_CONTROL` into address, shift, and mask initializers.
3. OPP, DPP, DSC, ODM/OPTC, IRQ, clock, GPIO, or DMUB runtime code issues field-level register reads and writes during resource construction, modeset, pipe programming, color pipeline setup, DSC routing, diagnostics, interrupt handling, or power transitions.
4. The generated masks and shifts isolate the requested bitfields while preserving unrelated bits in the same register.

The control-sensitive flows represented by this chunk include shaper/3D LUT programming, DPP/OPP performance counter start/stop/interrupt handling, output formatting and dithering, display pattern generation, output CRC collection, OPP pipe clocking, DSC forwarding to an OPP pipe, and ODM input segment routing. The header does not encode sequencing rules, write-one-to-clear behavior, self-clearing bits, read-only status fields, clock-domain requirements, or double-buffer commit timing.

## State And Persistence Behavior

The header itself stores no state and persists nothing. It describes hardware register state in the DCN 3.0 display pipeline. That state lives in display-controller registers and persists according to hardware reset, display pipe reprogramming, power gating, suspend/resume, modeset, and driver reinitialization behavior.

State represented here includes:

- Color pipeline state for DPP5 shaper RAM region topology, shaper/HDR LUT memory power mode, 3D LUT mode/size/index/data, output normalization, and RGB output offset/scale.
- Diagnostic state for CM5 indexed test-debug access and DPP/OPP performance monitors, including active counter selection, run state, counter states, interrupt enable/status/ack, and value readback.
- OPP formatter state for clamp ranges, dynamic expansion, truncation and dithering configuration, random seeds, pixel encoding, subsampling, stereo override, 4:2:0 memory power, 4:2:2 extra pixel handling, and double-buffer pending flags.
- Pattern generator state for generated output test patterns, dimensions, colors, ramp parameters, segment placement, field polarity, and pending updates.
- Output buffer and pipe state for active width, segmentation, overlap, pixel repetition, 3D padding/dummy data, pipe clock enables, clock-on readback, and digital bypass.
- CRC capture state for per-pipe output CRC source/mode/mask/result and one-shot pending status.
- DSC forwarding state for each `DSCRM` instance, including enable, selected OPP pipe source, enable status, and double-buffer pending.
- ODM/OPTC input state for soft reset, underflow interrupt tracking, segment source mapping, data/DSC format, width fields, input clock gating/enablement, memory selection, and spare register contents.

Many fields are configuration latches, while others are live status or interrupt/status-ack fields. Misprogrammed configuration can persist until the next modeset, stream revalidation, color-management update, CRC/debug teardown, DSC reprogramming, power transition, or GPU reset.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`, which supplies the matching MMIO addresses and base indices. Examples from that companion include `mmCM5_CM_SHAPER_RAMA_START_CNTL_R`, `mmCM5_CM_3DLUT_MODE`, `mmDC_PERFMON17_PERFCOUNTER_CNTL`, `mmFMT0_FMT_CONTROL`, `mmDPG0_DPG_CONTROL`, `mmOPPBUF0_OPPBUF_CONTROL`, `mmOPP_PIPE_CRC0_OPP_PIPE_CRC_CONTROL`, `mmDSCRM0_DSCRM_DSC_FORWARD_CONFIG`, `mmDC_PERFMON18_PERFCOUNTER_CNTL`, and `mmODM0_OPTC_INPUT_GLOBAL_CONTROL`.

Visible include sites for the DCN 3.0.0 offset and shift/mask headers in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c`

Important consuming abstractions are the common DPP, OPP, DSC, ODM/OPTC, IRQ, clock-manager, GPIO, and DMUB register-table patterns. For example, OPP code uses `OPP_SF(...)`, `REG_UPDATE(FMT_CONTROL, ...)`, `REG_UPDATE(DPG_CONTROL, ...)`, and `REG_READ(OPP_PIPE_CRC_CONTROL)` style helpers; DSC code uses `DSCRM_DSC_FORWARD_CONFIG` fields to route DSC forwarding to OPP pipes; color-management paths use DPP shaper and 3D LUT fields through DPP register tables.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. These macros compile as constants; an incorrect shift or mask can write a neighboring field, truncate a value, fail to clear stale bits, misread status, or make a wait loop observe the wrong condition.

Chunk boundaries are not hardware boundaries. The first three lines finish `CM5_CM_SHAPER_RAMA_START_CNTL_R` after the previous chunk supplied `CM_SHAPER_RAMA_EXP_REGION_START_R__SHIFT`. The final line supplies only `ODM5_OPTC_BYTES_PER_PIXEL__OPTC_DSC_BYTES_PER_PIXEL__SHIFT`; its mask and the remaining `ODM5` width, clock, memory, and spare-register fields continue in the next chunk. Reconciliation must merge adjacent chunks before declaring complete coverage for those registers.

The repeated instance blocks create copy-generation hazards. `FMT0` through `FMT5`, `DPG0` through `DPG5`, `OPPBUF0` through `OPPBUF5`, `OPP_PIPE_CRC0` through `OPP_PIPE_CRC5`, `DSCRM0` through `DSCRM5`, and `ODM0` through `ODM5` should be structurally aligned except where the range is partial. A single wrong instance prefix or drifted field width could make only one pipe fail.

Color and formatter fields are user-visible. Bad shaper, 3D LUT, clamp, dynamic expansion, bit-depth, dither, pixel encoding, or subsampling constants can produce wrong colors, banding, crushed ranges, invalid YCbCr output, stereo formatting problems, or failures that appear only with HDR, LUT updates, or non-RGB formats.

Double-buffer and pending bits need correct masks. `FMT_DOUBLE_BUFFER_REG_UPDATE_PENDING`, `DPG_DOUBLE_BUFFER_PENDING`, `OPPBUF_DOUBLE_BUFFER_PENDING`, `DSCRM_DSC_DOUBLE_BUFFER_REG_UPDATE_PENDING`, and `OPTC_DOUBLE_BUFFER_PENDING` are synchronization/status fields. Incorrect definitions can cause premature programming, missed waits, or hangs in register wait paths.

Performance monitor and CRC fields mix control, status, interrupt, and readback semantics. Wrong interrupt status/ack masks can leave perf counter interrupts stuck or lost. Wrong CRC source/mode/result masks can make debugfs or validation CRCs look mismatched even when the pixel stream is correct.

Clock and power fields can affect availability of downstream state. Misusing `OPP_PIPE_CLOCK_EN`, `OPP_PIPE_CLOCK_ON`, `OPP_DISPCLK_*_GATE_DIS`, `FMT_MAP420MEM_PWR_*`, `SHAPER_MEM_PWR_*`, or `HDR3DLUT_MEM_PWR_*` can lead to reads from gated blocks, failed LUT access, or intermittent programming failures across power transitions.

ODM and DSC fields are display-topology sensitive. Bad `OPTC_SEGn_SRC_SEL`, segment-count fields, DSC mode, bytes-per-pixel, slice width, or DSC forwarding source can route pixels from the wrong segment or pipe, break DSC pass-through, or cause underflow conditions on multi-pipe or compressed-display configurations.

## Test Signals

Useful validation signals include:

- Build coverage for DCN30/DCN302 resource, IRQ, GPIO, clock-manager, DMUB, OPP, DPP, DSC, and ODM/OPTC paths that include `dcn_3_0_0_sh_mask.h`.
- Generated-header checks that every field has a shift/mask pair where the complete register is in the chunk, masks align with shifts, and every register has a matching address in `dcn_3_0_0_offset.h`.
- Cross-generation diffs against adjacent DCN headers such as `dcn_2_1_0_sh_mask.h`, `dcn_3_0_1_sh_mask.h`, and later DCN 3.x headers, with expected ASIC differences reviewed against the register database.
- Pipe-by-pipe structural checks across `FMTn`, `DPGn`, `OPPBUFn`, `OPP_PIPE_CRCn`, `DSCRMn`, and `ODMn` instances to catch accidental instance-specific drift.
- Color-management tests for shaper LUT and 3D LUT programming, HDR modes, LUT bypass/enable transitions, suspend/resume, and memory power state transitions.
- Display format tests covering RGB and YCbCr, 4:2:0, 4:2:2, dithering/truncation paths, bit-depth changes, stereo override, and clamp/dynamic-expansion behavior.
- Pattern generator tests for solid color, ramp, dimensions, segment offsets, dynamic range, and bit-depth settings on all six pipes.
- CRC validation through output CRC/debugfs or internal test hooks, checking continuous and one-shot captures, stereo/interlace modes, source select, masks, and result registers.
- DSC/ODM topology tests for single-pipe, multi-pipe, DSC-enabled, ODM-combine/split, and underflow recovery paths.
- Performance monitor tests that start/stop counters, select events, read low/high values, trigger and acknowledge counter interrupts, and verify no stuck interrupt status remains.

Regression symptoms from bad constants include wrong color output, banding, failed HDR LUT programming, display underflow, incorrect DSC routing, blank or partially routed displays in ODM modes, stuck double-buffer waits, missing or false CRC mismatches, invalid performance counter values, stuck perfmon interrupts, and pipe-specific failures that reproduce only on one generated instance.

## Cross-Chunk Notes

This chunk is one slice of the large generated `dcn_3_0_0_sh_mask.h` file. The previous chunk owns the beginning of `CM5_CM_SHAPER_RAMA_START_CNTL_R`; this chunk owns the rest of CM5 shaper/3D LUT material and the majority of OPP/ODM material described above; the next chunk continues `ODM5_OPTC_BYTES_PER_PIXEL` and the remaining ODM5 fields. The final per-file research document should treat this as part of the DCN 3.0.0 generated register-layout contract rather than a standalone module.

### subset-b-001699: lines 29905-32369

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 29905-32369

## Purpose

This chunk is part of AMD's generated DCN 3.0 ASIC register field mask header. It does not implement executable driver logic; it defines `#define` constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for fields inside DCN output data merger/output timing generator registers.

The range starts at the tail of the `ODM5` OPTC field definitions and then covers the `dce_dc_optc_otg0_dispdec`, `dce_dc_optc_otg1_dispdec`, and beginning of `dce_dc_optc_otg2_dispdec` address blocks. In practical driver terms, these constants are the hardware contract used by AMD display code to program display timing, trigger events, frame counting, CRC capture, vertical interrupts, global swap-lock/update-lock behavior, DSC/ODM width controls, and dynamic refresh rate state for DCN 3.0 display pipes.

## Important Definitions

- `ODM5_OPTC_BYTES_PER_PIXEL__OPTC_DSC_BYTES_PER_PIXEL_MASK`, `ODM5_OPTC_WIDTH_CONTROL__*`, `ODM5_OPTC_INPUT_CLOCK_CONTROL__*`, `ODM5_OPTC_MEMORY_CONFIG__*`, and `ODM5_OPTC_INPUT_SPARE_REGISTER__*`: the tail of the sixth ODM/OPTC instance. These fields describe DSC bytes-per-pixel, segment and DSC slice width, OPTC input clock gate/enable/on status, memory selection, and a spare register.
- `OTG0_*` and `OTG1_*`: complete repeated field-layout blocks for timing generator instances 0 and 1. The two blocks expose the same register shapes with instance-specific macro prefixes.
- `OTG2_*`: the beginning of the timing generator instance 2 block. This chunk covers the OTG2 fields from basic horizontal/vertical timing through `OTG2_OTG_DRR_CONTROL__OTG_DRR_AVERAGE_FRAME__SHIFT`; the remainder of OTG2 continues in the next chunk.
- Horizontal timing registers: `OTG*_OTG_H_TOTAL`, `OTG*_OTG_H_BLANK_START_END`, `OTG*_OTG_H_SYNC_A`, `OTG*_OTG_H_SYNC_A_CNTL`, and `OTG*_OTG_H_TIMING_CNTL` define total pixels, blanking start/end, sync start/end, sync polarity, composite sync enable, cutoff, and horizontal timing divisor/update mode fields.
- Vertical timing and DRR registers: `OTG*_OTG_V_TOTAL`, `OTG*_OTG_V_TOTAL_MIN`, `OTG*_OTG_V_TOTAL_MAX`, `OTG*_OTG_V_TOTAL_MID`, `OTG*_OTG_V_TOTAL_CONTROL`, `OTG*_OTG_DRR_TIMING_INT_STATUS`, `OTG*_OTG_DRR_V_TOTAL_REACH_RANGE`, `OTG*_OTG_DRR_V_TOTAL_CHANGE`, `OTG*_OTG_DRR_TRIGGER_WINDOW`, and `OTG*_OTG_DRR_CONTROL` describe nominal/adaptive vertical totals, DRR event windows, update/reach interrupt state, and average-frame selection.
- Trigger and flow-control registers: `OTG*_OTG_TRIGA_CNTL`, `OTG*_OTG_TRIGB_CNTL`, their manual trigger registers, `OTG*_OTG_FORCE_COUNT_NOW_CNTL`, `OTG*_OTG_FLOW_CONTROL`, `OTG*_OTG_TRIG_MANUAL_CONTROL`, and `OTG*_OTG_MANUAL_FLOW_CONTROL` define source selection, pipe selection, polarity, edge detection, delay, clear bits, manual trigger, and flow-control status fields.
- Generator enable/status registers: `OTG*_OTG_CONTROL`, `OTG*_OTG_MASTER_EN`, `OTG*_OTG_STATUS`, `OTG*_OTG_STATUS_POSITION`, `OTG*_OTG_NOM_VERT_POSITION`, `OTG*_OTG_STATUS_FRAME_COUNT`, `OTG*_OTG_STATUS_VF_COUNT`, `OTG*_OTG_STATUS_HV_COUNT`, `OTG*_OTG_COUNT_CONTROL`, `OTG*_OTG_COUNT_RESET`, `OTG*_OTG_UPDATE_LOCK`, and `OTG*_OTG_DOUBLE_BUFFER_CONTROL` expose enable state, current raster position, frame counters, vertical-frequency counters, horizontal/vertical count snapshots, count reset control, update lock, and double-buffer update controls.
- Interlace, stereo, and vertical-sync controls: `OTG*_OTG_INTERLACE_CONTROL`, `OTG*_OTG_INTERLACE_STATUS`, `OTG*_OTG_MANUAL_FORCE_VSYNC_NEXT_LINE`, `OTG*_OTG_VERT_SYNC_CONTROL`, `OTG*_OTG_STEREO_FORCE_NEXT_EYE`, `OTG*_OTG_STEREO_STATUS`, and `OTG*_OTG_STEREO_CONTROL` define field polarity/counting, stereo eye state, stereo force commands, and vertical-sync force/lock behavior.
- Snapshot and interrupt registers: `OTG*_OTG_SNAPSHOT_STATUS`, `OTG*_OTG_SNAPSHOT_CONTROL`, `OTG*_OTG_SNAPSHOT_POSITION`, `OTG*_OTG_SNAPSHOT_FRAME`, `OTG*_OTG_INTERRUPT_CONTROL`, `OTG*_OTG_V_TOTAL_INT_STATUS`, `OTG*_OTG_VSYNC_NOM_INT_STATUS`, and `OTG*_OTG_GLOBAL_SYNC_STATUS` define capture control/status and interrupt enable/type/status/clear fields for vstartup, vupdate, vupdate-no-lock, vready, vtotal-min, nominal vsync, and stereo/field status.
- Blank data and CRC registers: `OTG*_OTG_BLANK_DATA_COLOR`, `OTG*_OTG_BLANK_DATA_COLOR_EXT`, `OTG*_OTG_CRC_CNTL`, `OTG*_OTG_CRC_CNTL2`, `OTG*_OTG_CRC0_WINDOW*`, `OTG*_OTG_CRC1_WINDOW*`, `OTG*_OTG_CRC*_DATA_*`, `OTG*_OTG_CRC_SIG_RED_GREEN_MASK`, and `OTG*_OTG_CRC_SIG_BLUE_CONTROL_MASK` define blanking color fields, CRC window positions, CRC data readout, CRC component masks, and CRC control.
- Global sync and update-lock registers: `OTG*_OTG_GSL_VSYNC_GAP`, `OTG*_OTG_MASTER_UPDATE_MODE`, `OTG*_OTG_CLOCK_CONTROL`, `OTG*_OTG_VSTARTUP_PARAM`, `OTG*_OTG_VUPDATE_PARAM`, `OTG*_OTG_VREADY_PARAM`, `OTG*_OTG_MASTER_UPDATE_LOCK`, `OTG*_OTG_GSL_CONTROL`, `OTG*_OTG_GSL_WINDOW_X`, `OTG*_OTG_GSL_WINDOW_Y`, `OTG*_OTG_VUPDATE_KEEPOUT`, and `OTG*_OTG_GLOBAL_CONTROL0..4` describe global swap-lock, vstartup/vupdate/vready placement, master update locks, update keepout windows, manual flow-control source selection, and digital update position/field/eye selection.
- Stream/request/DSC support registers in complete OTG0/OTG1 blocks: `OTG*_OTG_M_CONST_DTO0`, `OTG*_OTG_M_CONST_DTO1`, `OTG*_OTG_REQUEST_CONTROL`, `OTG*_OTG_DSC_START_POSITION`, `OTG*_OTG_PIPE_UPDATE_STATUS`, and `OTG*_OTG_SPARE_REGISTER` define DTO phase/modulo, requestor selection/incrementing, DSC start coordinates, pipe update flags, and spare state. OTG2 reaches only `OTG_DRR_CONTROL` in this chunk.

Each field appears as a paired shift and mask macro. Consumers generally combine a field value with the shift and mask through AMD register helper macros rather than writing these constants directly.

## Control Flow

There is no local control flow, branching, or function call behavior in this header chunk. The runtime flow is indirect and table-driven:

1. DCN 3.0 modules include `dcn_3_0_0_offset.h` and `dcn_3_0_0_sh_mask.h`.
2. OPTC/OTG register structs and macro lists bind symbolic register names to hardware offsets and bind field names to the generated masks and shifts.
3. Display code calls helper macros such as `REG_UPDATE`, `REG_GET`, `REG_READ`, `SRI`, `SRI_ARR`, and `SF`.
4. Those helpers use the macros from this header to isolate, update, or test specific MMIO fields for a selected ODM/OTG instance.

Concrete integration references in this tree include `display/dc/optc/dcn30/dcn30_optc.h`, which maps `OTG_DRR_CONTROL`, `OPTC_WIDTH_CONTROL`, `OTG_H_TOTAL`, and `OTG_V_TOTAL_LAST_USED_BY_DRR` fields into the OPTC register/mask tables; `display/dc/optc/dcn30/dcn30_optc.c`, which writes `OPTC_WIDTH_CONTROL`; `display/dc/irq/dcn30/irq_service_dcn30.c`, which wires `OTG_GLOBAL_SYNC_STATUS` fields into interrupt sources; and DCN 3.0 resource, clock, GPIO, DMUB, and IRQ files that include this generated header.

## State And Persistence Behavior

The header itself stores no state and has no persistence behavior. It names fields in hardware registers whose state is owned by the display engine:

- Timing state includes horizontal and vertical totals, blanking intervals, sync positions, vtotal min/max/mid values, DRR transition limits, and raster position counters.
- Control state includes OTG master enable, update lock, double-buffer updates, force-count-now controls, trigger controls, manual flow controls, clock control, global sync lock, and DSC/ODM width settings.
- Status state includes current master-enable status, interlace/stereo field status, trigger occurrence bits, count snapshots, CRC results, pipe update status, vstartup/vupdate/vready/vsync events, and DRR timing/reach events.
- Persistence across modesets or power transitions is not defined by this file. Driver code must program or reprogram the corresponding registers when constructing a display pipe, changing a mode, enabling DRR/VRR, entering/exiting stereo/interlace paths, or restoring hardware after reset/power-gating.

Because the macros describe MMIO bit layouts, an incorrect definition changes how driver code mutates live hardware state. There is no software guard in this file that validates field values or prevents writes to reserved/neighbor bits.

## Dependencies And Integration Points

- The matching offset header, `dcn_3_0_0_offset.h`, supplies register addresses. This `*_sh_mask.h` chunk supplies field positions and masks; both are required for meaningful register access.
- AMD display register helpers in `display/dc` consume these field definitions through generated register structs and macros. The common pattern is that a logical field name such as `OTG_H_TOTAL` maps to an instance-specific macro such as `OTG0_OTG_H_TOTAL__OTG_H_TOTAL_MASK`.
- OPTC implementation files consume the ODM/OPTC fields for DSC slice width, segment width, and input clock/memory control. Public state comments in `display/dc/dc.h` also reference `OPTC_WIDTH_CONTROL->OPTC_SEGMENT_WIDTH`, `OPTC_WIDTH_CONTROL->OPTC_DSC_SLICE_WIDTH`, and `OTG_DRR_CONTROL->OTG_V_TOTAL_LAST_USED_BY_DRR` as relevant hardware-derived values.
- IRQ service code uses `OTG_GLOBAL_SYNC_STATUS` fields such as `VSTARTUP_INT_EN`, `VSTARTUP_EVENT_CLEAR`, `VUPDATE_NO_LOCK_INT_EN`, and `VUPDATE_NO_LOCK_EVENT_CLEAR` to route DCN timing interrupts.
- CRC capture and timing validation paths depend on the `OTG_CRC*`, status-position, frame-count, and HV-count fields matching the hardware so debugfs, diagnostics, or automated display validation can read meaningful values.
- Global swap-lock/update-lock behavior depends on `OTG_GSL_*`, `OTG_MASTER_UPDATE_LOCK`, `OTG_GLOBAL_CONTROL*`, `OTG_VUPDATE_KEEPOUT`, and vstartup/vupdate/vready fields. These are integration points for synchronized multi-pipe updates and stereo/field-aware programming.
- The chunk is source-tree-aligned with AMD GPU display code under `drivers/gpu/drm/amd/display`; it is not Ceph-specific despite living under the repository's `sources/distributed-fs/ceph-client` import path.

## Risks

- This is generated hardware contract data. A one-bit error in a mask or shift can make otherwise correct register helper calls corrupt adjacent fields or fail to update the intended hardware field.
- The OTG0 and OTG1 blocks are large repeated layouts, and OTG2 begins the same pattern. Instance-copy errors are hard to spot by eye and could produce pipe-specific display failures.
- The range starts mid-ODM5 block and ends mid-OTG2 `OTG_DRR_CONTROL`, so whole-file reconciliation must use adjacent chunks to avoid claiming complete coverage for ODM5 or OTG2.
- Timing fields are mode-critical. Bad masks for totals, blanking, sync, or divisor fields can cause blank displays, unstable scanout, incorrect interlace/stereo behavior, or timing underflow symptoms.
- Interrupt status and clear masks are sensitive. Incorrect `*_EVENT_CLEAR`, `*_INT_EN`, or `*_INT_STATUS` fields can cause missed vupdate/vstartup/vready events or stuck interrupts.
- Update-lock and global-sync fields coordinate multi-register programming. Incorrect definitions can expose partially updated timing state, break multi-pipe synchronization, or disrupt variable refresh operation.
- CRC and readback fields are often used for validation and diagnostics. Incorrect masks may hide real display corruption or create false failures in test automation.

## Test Signals

- Build coverage: DCN 3.0 display, DMUB, IRQ, GPIO, clock-manager, resource, and OPTC objects should compile when including `dcn_3_0_0_sh_mask.h`. Missing or malformed macros surface as compile-time errors in register table construction or helper macro expansion.
- Static/register-generation validation: compare this generated header against AMD's authoritative register database and adjacent DCN generations for identical repeated OTG field layouts where the hardware contract is expected to match.
- Modeset/runtime validation: exercise display modes on OTG0, OTG1, and OTG2-backed pipes, including changes to horizontal/vertical timing, blanking, sync polarity, interlace, stereo fields, and enable/disable sequencing.
- DRR/VRR validation: verify vtotal min/max/mid programming, DRR timing-update/reach interrupts, trigger windows, and `OTG_V_TOTAL_LAST_USED_BY_DRR` readback.
- Interrupt validation: verify vstartup, vupdate, vupdate-no-lock, vready, nominal-vsync, and vtotal-min event enable/status/clear behavior through the DCN IRQ service.
- CRC/readback validation: check CRC window programming, CRC data readouts, blank data color fields, pixel data readback, and raster/frame counters against expected scanout behavior.
- Synchronization validation: test global swap-lock, master update lock, update keepout, manual flow control, and digital update position behavior across synchronized multi-pipe updates.

### subset-b-001700: lines 32370-34834

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 32370-34834

## Scope And Purpose

This chunk is a generated AMD DCN 3.0.0 register shift/mask table for display timing-generator hardware. It contains C preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for Output Timing Generator (`OTG`) registers. The covered range starts in the tail of `OTG2`, contains the full `dce_dc_optc_otg3_dispdec` and `dce_dc_optc_otg4_dispdec` address blocks, and ends inside the `dce_dc_optc_otg5_dispdec` block after `OTG5_OTG_DRR_V_TOTAL_REACH_RANGE`.

There are no executable functions, structs, or runtime branches in this chunk. Its purpose is to provide compile-time field metadata consumed by AMD display driver register-access macros. The companion offset header supplies register addresses such as `mmOTG3_OTG_H_TOTAL`; this header supplies the matching field layout such as `OTG3_OTG_H_TOTAL__OTG_H_TOTAL__SHIFT` and `OTG3_OTG_H_TOTAL__OTG_H_TOTAL_MASK`.

The register groups in this slice program and observe display scanout timing, vertical/horizontal blank and sync intervals, dynamic refresh-rate timing, global sync lock windows, vertical interrupts, stereo/interlace state, CRC capture windows and result fields, blanking colors, update locks, clock gating/reset state, DSC start position, and pending pipe-update status.

## Register Blocks Covered

The first lines finish `OTG2` with fields for DRR control, M/N constant DTO programming, request control for horizontal duplicate handling, DSC start position, pipe update pending status, and a spare register. This is only a partial tail of the `OTG2` block; the preceding chunk owns the earlier `OTG2` timing fields.

`OTG3` is fully represented under `// addressBlock: dce_dc_optc_otg3_dispdec`. It has 716 `#define` entries in the requested line slice and covers the full per-OTG timing generator layout from `OTG3_OTG_H_TOTAL` through `OTG3_OTG_SPARE_REGISTER`.

`OTG4` mirrors the `OTG3` layout under `// addressBlock: dce_dc_optc_otg4_dispdec`. It also contributes 716 `#define` entries. The field names, bit widths, and masks are structurally the same with the instance prefix changed from `OTG3_` to `OTG4_`.

`OTG5` starts under `// addressBlock: dce_dc_optc_otg5_dispdec` and is covered through `OTG5_OTG_DRR_V_TOTAL_REACH_RANGE`. The chunk includes the same major groups as `OTG3` and `OTG4` through DRR timing interrupt status and the DRR v-total reach range fields, but the later `OTG5` DRR change/window/control, DTO, request-control, DSC, pipe-status, and spare-register fields continue after line 34834.

## Important APIs, Types, And Macros

The important exported surface is the macro naming contract:

- `<instance>_<register>__<field>__SHIFT` gives the bit offset used when packing or extracting a field.
- `<instance>_<register>__<field>_MASK` gives the masked field bits in the 32-bit hardware register value.
- Instance prefixes in this chunk are `OTG2`, `OTG3`, `OTG4`, and `OTG5`.
- Register comments such as `//OTG3_OTG_GLOBAL_SYNC_STATUS` delimit groups but are not consumed by C code.
- Address-block comments such as `// addressBlock: dce_dc_optc_otg4_dispdec` identify the replicated display-controller hardware block.

The header is consumed by generated-style AMD display macros including `SF(...)`, `SRI(...)`, `REG_FIELD`, `REG_GET`, `REG_SET`, and `REG_UPDATE` through higher-level register lists. For example, `display/dc/optc/dcn30/dcn30_optc.h` declares `OPTC_COMMON_REG_LIST_DCN3_0(inst)` with `SRI(OTG_H_TOTAL, OTG, inst)`, `SRI(OTG_GLOBAL_SYNC_STATUS, OTG, inst)`, `SRI(OTG_DRR_TRIGGER_WINDOW, OTG, inst)`, and `SRI(OTG_PIPE_UPDATE_STATUS, OTG, inst)`. Its mask list uses `SF(OTG0_OTG_H_TOTAL, OTG_H_TOTAL, mask_sh)` style entries, relying on the same field-layout definitions replicated across OTG instances.

The IRQ service for DCN 3.0 and DCN 3.0.2 includes this header and maps vupdate/vblank interrupts through fields in `OTG_GLOBAL_SYNC_STATUS`, including `VUPDATE_NO_LOCK_INT_EN`, `VUPDATE_NO_LOCK_EVENT_CLEAR`, `VSTARTUP_INT_EN`, and `VSTARTUP_EVENT_CLEAR`. Later OPTC diagnostic code reads registers represented here into state snapshots, including `OTG_DRR_TIMING_INT_STATUS`, `OTG_GLOBAL_SYNC_STATUS`, `OTG_GSL_CONTROL`, `OTG_H_TOTAL`, CRC fields, and related timing registers.

## Functional Field Groups

Horizontal and vertical timing fields define scanout geometry. `OTG_H_TOTAL`, `OTG_H_BLANK_START_END`, `OTG_H_SYNC_A`, `OTG_H_SYNC_A_CNTL`, and `OTG_H_TIMING_CNTL` describe horizontal total pixels, blanking window, sync start/end, sync polarity, composite sync enable/cutoff, and timing divider behavior. `OTG_V_TOTAL`, `OTG_V_TOTAL_MIN`, `OTG_V_TOTAL_MAX`, `OTG_V_TOTAL_MID`, `OTG_V_BLANK_START_END`, `OTG_V_SYNC_A`, and `OTG_V_SYNC_A_CNTL` define vertical totals, variable-refresh bounds, blanking, sync timing, polarity, and sync mode.

Dynamic refresh-rate fields are centered on `OTG_V_TOTAL_CONTROL`, `OTG_DRR_TIMING_INT_STATUS`, `OTG_DRR_V_TOTAL_REACH_RANGE`, `OTG_DRR_V_TOTAL_CHANGE`, `OTG_DRR_TRIGGER_WINDOW`, and `OTG_DRR_CONTROL`. They expose min/max/mid v-total selection, masked min-vtotal updates, frame counts, DRR timing-update interrupts, v-total-reach interrupts, clear/mask/type bits, v-total reach ranges, v-total change limits, trigger windows, and the last v-total used by DRR. These fields are timing-sensitive because the driver uses them to vary refresh while preserving scanout stability.

Trigger and forced-count fields include `OTG_TRIGA_CNTL`, `OTG_TRIGB_CNTL`, manual trigger registers, `OTG_FORCE_COUNT_NOW_CNTL`, `OTG_TRIG_MANUAL_CONTROL`, and `OTG_MANUAL_FLOW_CONTROL`. They select trigger sources and source pipes, polarity, rising/falling edge detection, frequency, delay, status, clear bits, and manual trigger paths. `OTG_FLOW_CONTROL` adds source selection, polarity, granularity, and input status for flow-control signaling.

Mastering, update, and global-sync fields include `OTG_CONTROL`, `OTG_MASTER_EN`, `OTG_UPDATE_LOCK`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_MASTER_UPDATE_MODE`, `OTG_MASTER_UPDATE_LOCK`, `OTG_GLOBAL_SYNC_STATUS`, `OTG_GSL_CONTROL`, `OTG_GSL_WINDOW_X/Y`, `OTG_VUPDATE_KEEPOUT`, and `OTG_GLOBAL_CONTROL0` through `OTG_GLOBAL_CONTROL4`. They control OTG enable state, disable/start points, update locks and pending state, global swap lock participation, vstartup/vupdate/vready events, vupdate keepout regions, double-buffer regions, digital update positions, and master-update-lock selection.

Status, snapshot, stereo, and interlace fields include `OTG_STATUS`, `OTG_STATUS_POSITION`, `OTG_NOM_VERT_POSITION`, `OTG_STATUS_FRAME_COUNT`, `OTG_STATUS_VF_COUNT`, `OTG_STATUS_HV_COUNT`, `OTG_COUNT_CONTROL`, `OTG_COUNT_RESET`, `OTG_VERT_SYNC_CONTROL`, `OTG_STEREO_STATUS`, `OTG_STEREO_CONTROL`, `OTG_STEREO_FORCE_NEXT_EYE`, `OTG_3D_STRUCTURE_CONTROL`, `OTG_INTERLACE_CONTROL`, `OTG_INTERLACE_STATUS`, and the snapshot registers. These fields expose current vblank/active/sync state, horizontal and vertical counters, frame counters, stereo eye state, forced next field/eye controls, and snapshot triggers or captured positions.

Interrupt and CRC fields include vertical interrupt position/control registers for interrupt slots 0 through 2, `OTG_INTERRUPT_CONTROL`, `OTG_CRC_CNTL`, `OTG_CRC_CNTL2`, CRC window controls, CRC data readbacks, and CRC signature masks. These support vline/vblank-style interrupt routing and validation/debug capture of displayed pixel streams.

Output data, clock, and miscellaneous fields include blank data color and extended-color fields, pixel data readback registers, `OTG_CLOCK_CONTROL`, `OTG_VSTARTUP_PARAM`, `OTG_VUPDATE_PARAM`, `OTG_VREADY_PARAM`, DTO phase/modulo constants, request-control flags, DSC start position, pipe update status, and spare registers.

## Control Flow And State Behavior

This header has no direct control flow. The effective control flow is created at compile time by macro expansion in DCN display modules. Register-list macros select an OTG instance, bind the corresponding offset from `dcn_3_0_0_offset.h`, then bind the field masks and shifts from this file. Runtime code then performs memory-mapped register reads and writes through AMD display register helpers.

The hardware state described here is persistent in display controller registers until the driver, firmware, reset logic, power management, or hardware event logic changes it. Some fields are configuration state, such as timing totals, blanking windows, update-lock settings, CRC windows, DTO constants, and blank colors. Some fields are live status, such as current blank/sync state, counters, frame counts, busy/clock-on bits, input status bits, pending-update bits, and current stereo/interlace state. Some interrupt/event fields use write-to-clear or acknowledge-style semantics, reflected by field names such as `*_CLEAR`, `*_ACK`, and `*_EVENT_CLEAR`.

Several registers are double-buffered or synchronized to scanout phases. Fields involving update locks, global update lock, vupdate keepout, digital update position, GSL windows, and DRR trigger windows must be programmed with attention to vstartup/vupdate/vready timing. Incorrect sequencing can cause updates to miss the intended frame, block indefinitely behind update locks, or land during active scanout.

## Dependencies And Integration Points

This file depends on hardware register contracts for AMD DCN 3.0.0. It must stay aligned with `dcn_3_0_0_offset.h`, which provides the register addresses and base indices for the same `OTG3`, `OTG4`, and `OTG5` names. It also must stay compatible with generated register-list and mask-list macros in the display core, especially the DCN 3.0 OPTC path.

Direct include sites for this header include DCN 3.0 and DCN 3.0.2 display components such as `display/dc/resource/dcn30/dcn30_resource.c`, `display/dc/irq/dcn30/irq_service_dcn30.c`, `display/dc/irq/dcn302/irq_service_dcn302.c`, `display/dmub/src/dmub_dcn30.c`, `display/dmub/src/dmub_dcn302.c`, `display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`, and DCN 3.0 GPIO factory/translation code.

The most important integration point for this chunk is the OPTC/timing-generator stack. `display/dc/optc/dcn30/dcn30_optc.h` lists many of the registers covered here in `OPTC_COMMON_REG_LIST_DCN3_BASE` and `OPTC_COMMON_REG_LIST_DCN3_0`, including timing, vtotal, trigger, static-screen, status, blank color, clock, vertical interrupt, GSL, CRC, DRR, DSC, and pipe-update-status registers. IRQ setup uses `OTG_GLOBAL_SYNC_STATUS` fields for vblank and vupdate sources. Diagnostic register-state capture uses these same register names to snapshot OTG timing and CRC/debug state.

## Risks And Edge Cases

The primary risk is field drift between this mask header, the companion offset header, and the real hardware specification. A wrong shift or mask can silently write the wrong bitfield in a memory-mapped register, which may produce display timing failures, missed interrupts, stuck update locks, incorrect CRC/readback data, or unstable variable-refresh behavior.

Instance replication is another risk. `OTG3`, `OTG4`, and `OTG5` are largely identical, so generation errors that affect only one prefix are easy to miss in review. Conversely, assuming all instances are complete in this chunk would be wrong: `OTG5` continues after the requested range, while `OTG2` only appears as a tail from the previous block.

Interrupt/status fields require particular care. Fields named `*_EVENT_OCCURRED`, `*_INT_STATUS`, `*_CLEAR`, `*_ACK`, `*_MSK`, and `*_INT_TYPE` are adjacent in shared registers. If a clear mask is confused with a status mask, the driver can either fail to acknowledge interrupts or clear state unexpectedly.

Timing-window and update-lock fields have frame-phase dependencies. Values for vstartup/vupdate/vready, vupdate keepout, GSL windows, vertical interrupt positions, DRR trigger windows, and double-buffer regions must be valid relative to programmed totals and blanking ranges. Bad values can create race-like failures that only reproduce on particular modes, refresh ranges, or multi-display topologies.

Many fields are limited-width counters or positions, commonly 15-bit horizontal/vertical values and packed 16-bit low/high halves. Callers must clamp or validate mode-derived values before packing them through these masks. Overwide values would be truncated by the mask and can shift timing positions to unintended scanout coordinates.

## Test Signals

Build-time signals are straightforward: any stale or missing macro used by DCN 3.0 register lists should fail compilation in AMD display modules that include this header. Warnings or errors around `SF`, `SRI`, `REG_FIELD`, or missing `OTGx_*__*` identifiers are high-signal indicators of a register metadata mismatch.

Runtime validation comes from display mode-set and scanout tests on DCN 3.0-class hardware. Useful signals include successful modesets across displays attached to OTG instances 3, 4, and 5; stable vblank/vupdate IRQ delivery; no stuck update-lock or GSL state; correct dynamic-refresh behavior; and absence of underflow, blanking, or sync glitches during resolution and refresh-rate changes.

Debug and conformance signals include CRC capture tests over `OTG_CRC*` windows, register-state dumps that show expected `OTG_STATUS_POSITION` and frame counters advancing, vertical interrupt tests at programmed line positions, stereo/interlace mode tests where supported, DSC start-position validation, and pipe update status returning to idle after flips, cursor updates, and DC register updates.

Because this is generated register metadata rather than algorithmic code, the strongest regression tests are cross-checks against the hardware register database and smoke tests that exercise every OTG instance using the same driver paths.

### subset-b-001701: lines 34835-37214

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 34835-37214

## Scope

This chunk is a late slice of AMDGPU's generated DCN 3.0.0 register shift/mask header. It is not executable C; it exports preprocessor constants of the form `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` for display-controller MMIO fields. These definitions are paired with register addresses from `dcn_3_0_0_offset.h` and consumed by AMD display register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_WAIT`, `SF`, `SRI`, `FD_MASK`, and `FD_SHIFT`.

The range starts at the tail of the `OTG5` timing-generator register family, then covers OPTC miscellaneous source/power controls, DC perfmon instance 19, DIO I2C/DDC infrastructure, DIO clock/reset/power controls, HPD0 through HPD5 hotplug-detect blocks, DC perfmon instance 20, and most of the DP AUX0 through DP AUX2 register families. It ends at the chunk boundary inside `DP_AUX2_AUX_GTC_SYNC_CONTROLLER_STATUS`, so later lines own the remaining status fields for that register and subsequent register families.

## Purpose

The header range describes bit positions and masks for DCN 3.0 display timing, display-output, I2C/DDC, HPD, DP AUX, memory-power, and diagnostic hardware. Its purpose is to let generation-specific DCN30 code use stable logical field names while the generated register database supplies ASIC-specific field layout.

Major hardware areas covered here are:

- `OTG5_*` fields for dynamic refresh-rate timing changes, DRR trigger windows, constant DTO phase/modulo programming, DSC start position, request control, pipe update status, and spare debug storage on timing generator 5.
- `DWB_SOURCE_SELECT`, `GSL_SOURCE_SELECT`, `OPTC_CLOCK_CONTROL`, and `ODM_MEM_PWR_*` fields for writeback source selection, genlock/swaplock ready-source routing, OPTC clock gating/status, and ODM memory power force/disable/status policy.
- `DC_PERFMON19_*` and `DC_PERFMON20_*` fields for event selection, counted-value selection, run/stop control, counter state, active status, interrupt enable/ack/status, and high/low counter reads.
- `DC_I2C_*` and `DC_I2C_DDC1` through `DC_I2C_DDC6` fields for the display I2C engine, DDC line selection, arbitration between SW/HW/DMCU users, transaction programming, FIFO/data indexing, EDID detection, read-request interrupts, speed/prescale thresholds, setup timing, and per-DDC hardware status.
- `DIO_*` fields for scratch registers, DIO memory power status/control, display-output clocks, power-management overrides, DIG soft reset lines, HDMI RX status timer settings, and generic DIO interrupt message/clear registers.
- `HPD0_*` through `HPD5_*` fields for hotplug sense/status, interrupt enable/ack/polarity, HPD RX interrupt control, HPD enable, filter/connect/disconnect delays, and fast-training timing.
- `DP_AUX0_*`, `DP_AUX1_*`, and `DP_AUX2_*` fields for DisplayPort AUX channel enable/reset/HPD selection, SW and LS AUX transactions, arbitration, interrupt controls, status/error reporting, data windows, DPHY TX/RX timing, GTC sync control/error/status, and PHY wake behavior where present in the range.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or persistent software objects in this chunk. The generated macro namespace is the API surface:

- `*_SHIFT` values provide the low bit number for a register field.
- `*_MASK` values provide the already-positioned mask used for extraction and read/modify/write.
- Address-block comments group fields under hardware blocks such as `dce_dc_optc_optc_misc_dispdec`, `dce_dc_optc_optc_dcperfmon_dc_perfmon_dispdec`, `dce_dc_dio_dout_i2c_dispdec`, `dce_dc_dio_hpd*_dispdec`, `dce_dc_dio_dio_dcperfmon_dc_perfmon_dispdec`, and `dce_dc_dio_dp_aux*_dispdec`.

The `OTG5_*` macros expose the same field shape used by the DCN30 timing-generator code for OTG instances. Important fields include `OTG_DRR_V_TOTAL_CHANGE_LIMIT`, `OTG_DRR_TRIGGER_WINDOW_START_X`, `OTG_DRR_TRIGGER_WINDOW_END_X`, `OTG_DRR_AVERAGE_FRAME`, `OTG_V_TOTAL_LAST_USED_BY_DRR`, `OTG_M_CONST_DTO_PHASE`, `OTG_M_CONST_DTO_MODULO`, `OTG_DSC_START_POSITION_X`, `OTG_DSC_START_POSITION_LINE_NUM`, and pipe-update status bits for pending flips, DC register updates, cursor updates, and vupdate keepout.

The OPTC/ODM miscellaneous macros cover shared routing and power fields. `DWB_SOURCE_SELECT` routes OPTC outputs into display writeback blocks. `GSL_SOURCE_SELECT` chooses ready sources and timing-sync source for genlock/swaplock flows. `OPTC_CLOCK_CONTROL` controls/report OPTC display-clock gating. `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL2`, `ODM_MEM_PWR_CTRL3`, and `ODM_MEM_PWR_STATUS` describe force/disable and status bits for ODM memory banks 0-11 plus unassigned/vblank power modes.

The `DC_PERFMON19_*` and `DC_PERFMON20_*` macros form repeated diagnostic counter instances. Each instance has `PERFCOUNTER_CNTL`, `PERFCOUNTER_CNTL2`, `PERFCOUNTER_STATE`, `PERFMON_CNTL`, `PERFMON_CNTL2`, `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW` fields. These select events, counted value types, increment modes, hardware start/stop sources, count-off behavior, active state, interrupt handling, and counter readback.

The I2C/DDC macros describe the DC I2C controller used for DDC/EDID transactions. `DC_I2C_CONTROL` carries `DC_I2C_GO`, soft reset, send reset, DDC select, transaction count, and status reset fields. `DC_I2C_ARBITRATION` covers software request/done signals, hardware request, DMCU request, queued-go policy, arbitration status, and abort flags. `DC_I2C_INTERRUPT_CONTROL`, `DC_I2C_SW_STATUS`, `DC_I2C_DDCx_HW_STATUS`, `DC_I2C_DDCx_SPEED`, `DC_I2C_DDCx_SETUP`, `DC_I2C_TRANSACTION0` through `TRANSACTION3`, `DC_I2C_DATA`, `DC_I2C_EDID_DETECT_CTRL`, and `DC_I2C_READ_REQUEST_INTERRUPT` define the transaction engine and its interrupt/status surface.

The DIO macros cover display-output infrastructure rather than a single link. `DIO_MEM_PWR_STATUS`, `DIO_MEM_PWR_CTRL`, and `DIO_MEM_PWR_CTRL2` expose I2C and HPD memory power states and force/disable controls. `DIO_CLK_CNTL`, `DIO_CLK_CNTL2`, and `DIO_CLK_CNTL3` define display, reference, SOCCLK, symbol-clock, HDCP, fast-clock, and related gating/reporting fields. `DIG_SOFT_RESET` contains reset controls for DIG frontend/backend blocks, PHY wrappers, and HDCP paths. Scratch, HDMI RX timer, generic interrupt message, and interrupt clear fields provide low-level diagnostics and glue.

The HPD macros are repeated for HPD0 through HPD5. Each block contains delayed and live sense bits, interrupt pending/ack/enable/polarity fields, HPD RX interrupt controls, HPD enable, connection state/status, fast-training enable/status/delay/count fields, and toggle-filter connect/disconnect delays.

The DP AUX macros are repeated for AUX0, AUX1, and AUX2. `AUX_CONTROL` enables/resets AUX, selects HPD, configures low-speed read/update handling, HPD-disconnect behavior, mode detection, impedance calibration, test/deglitch, and spare bits. `AUX_SW_CONTROL`, `AUX_ARB_CONTROL`, `AUX_INTERRUPT_CONTROL`, `AUX_SW_STATUS`, `AUX_LS_STATUS`, `AUX_SW_DATA`, and `AUX_LS_DATA` describe transaction start/done, command type, reply handling, byte count, arbitration, interrupt/ack/mask, and data windows. `AUX_DPHY_*` fields tune and report TX/RX physical-layer timings. `AUX_GTC_SYNC_*` fields configure and report global-time-code synchronization attempts, lock acquisition, lock loss, phase/offset error states, and timeout handling.

## Control Flow

This header has no runtime control flow. Runtime behavior appears in consumers that combine these generated fields with register addresses and MMIO helper functions.

A typical control sequence is:

1. A DCN30 display component includes `dcn_3_0_0_offset.h` and this shift/mask header.
2. Generation-specific register tables are built with `SRI(...)`, `SR(...)`, `SF(...)`, `HWS_SF(...)`, `LE_SF(...)`, or related macros.
3. Driver code calls helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, or indexed AUX/I2C helper wrappers.
4. The helper uses the generated shift and mask constants to clear, insert, poll, or extract the desired field in a read/modify/write MMIO operation.
5. Hardware performs the actual state transition: timing update, DRR adjustment, ODM memory power change, HPD interrupt acknowledgement, I2C/DDC transaction, AUX request, AUX reset, DIO clock-gate change, DIG reset, or perf counter update.

Control-sensitive flows represented by this chunk include timing-generator DRR and DSC positioning through the `OTG5_*` fields, genlock/swaplock source selection through `GSL_SOURCE_SELECT`, display writeback routing through `DWB_SOURCE_SELECT`, ODM memory low-power programming through `ODM_MEM_PWR_CTRL*`, software I2C command setup and completion through `DC_I2C_*`, EDID and link-side DDC access through DDC setup/speed/status fields, HPD connect/disconnect interrupt handling through the `HPD*_DC_HPD_*` fields, DP AUX reset/request/reply flows through `DP_AUX*_AUX_*`, and diagnostic counter operation through `DC_PERFMON19_*` and `DC_PERFMON20_*`.

The macros do not encode ordering constraints. Callers must still know when a field is read-only, write-one-to-clear, sticky, self-clearing, double-buffered, safe only while the engine is idle, safe only during blank, or owned by firmware.

## State And Persistence Behavior

The file stores no software state and performs no persistence. It describes hardware register state that persists according to DCN/MMIO semantics until rewritten, reset, power-gated, clock-gated, or changed by hardware/firmware.

State represented in this chunk includes:

- OTG/OPTC state: DRR limits/windows, last DRR vtotal, DTO phase/modulo, DSC start position, request-control policy, pending pipe update bits, writeback source routing, GSL ready/timing sync routing, and OPTC clock status.
- ODM/DIO power state: ODM memory bank force/disable/status, unassigned/vblank memory power policy, I2C/HPD memory power force/disable/status, DIO clock gating, DIG soft-reset state, and DIO power-management overrides.
- Perfmon state: selected events, counted value type, increment mode, run-enable and hardware start/stop selection, count-off policy, counter active/state fields, interrupt enable/status/ack bits, and high/low counter values.
- I2C/DDC state: arbitration ownership, queued command state, transaction descriptors, data FIFO/index window, selected DDC line, DDC speed/prescale/setup timing, EDID detect controls, read-request interrupts, software status/errors, and per-DDC hardware status.
- HPD state: live and delayed sense values, connect/disconnect filters, interrupt enable/status/ack/polarity, HPD RX interrupt controls, HPD enable, connection status, and fast-training counters/status.
- DP AUX state: AUX enable/reset/reset-done, HPD selection, low-speed read mode, SW/LS request status, arbitration state, interrupt enables/acks/masks, reply byte counts, protocol error bits, data index/data windows, DPHY timing/status, GTC sync lock/error/offset status, and PHY wake controls.

Some fields are programming latches, some are live status readbacks, some are counters, and some are sticky interrupt or error bits that require explicit acknowledgement. Suspend/resume, hotplug, modeset, DisplayPort link training, EDID reads, DSC/DRR programming, runtime power management, HPD storms, AUX timeouts, and debug/perf tooling can all alter the underlying hardware state. The generated header does not document reset defaults, access permissions, lock ordering, ownership, or volatility.

## Dependencies And Integration Points

The direct generated companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`, which provides register addresses and base indexes. This file provides the bit positions inside those addresses.

Direct include and usage points visible in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c` and `dmub_dcn302.c`, which include the DCN 3.0.0 offset and mask headers for firmware-side display register access tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn30/dcn30_optc.h`, which maps `OTG*_OTG_DRR_*`, `OTG*_OTG_M_CONST_DTO*`, `OTG*_OTG_DSC_START_POSITION`, `OTG*_OTG_PIPE_UPDATE_STATUS`, `DWB_SOURCE_SELECT`, and `GSL_SOURCE_SELECT` fields into timing-generator register and shift/mask tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn20/dcn20_optc.c`, which uses `GSL_SOURCE_SELECT` fields to program genlock/swaplock ready sources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn30/dcn30_hwseq.c` and `display/dc/hwss/dce/dce_hwseq.h`, which use `ODM_MEM_PWR_CTRL3` fields for ODM memory power policy during hardware sequencing.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c`, which builds HPD and DDC register/shift/mask tables from the HPD and DDC macros in this header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c`, which includes this header while translating DCN30 GPIO offsets and masks into logical GPIO IDs for DDC, HPD, generic, and GSL pins.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c` and `irq_service_dcn302.c`, which map HPD/HPDRX interrupt enable, status, and ack fields into DC IRQ source entries.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_i2c_hw.c` and `.h`, which consume `DC_I2C_*`, `DC_I2C_DDCx_*`, `DIO_MEM_PWR_CTRL`, and `DIO_MEM_PWR_STATUS` style fields through generation-specific tables for hardware I2C/DDC transactions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_link_encoder.c` and `.h`, plus DCN30 resource construction, which rely on `DP_AUX*_AUX_*` and `HPD*_DC_HPD_*` fields for AUX channel reset, HPD selection, link encoder setup, DPCD access, and link training support.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`, which carries generation resource caps and AUX reset-mask constants derived from this register family.

Although the repository path sits under `sources/distributed-fs/ceph-client`, this chunk is AMDGPU display hardware metadata. It has no Ceph protocol logic, filesystem cache state, network messaging, or distributed-storage persistence behavior.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A generated shift or mask can be wrong while all C code still compiles, causing a read/modify/write helper to alter the wrong bit, fail to clear a sticky bit, corrupt an adjacent field, or poll a status bit that never changes.

Timing and display-output risks are visible. Incorrect `OTG5_OTG_DRR_*`, `OTG5_OTG_DSC_START_POSITION`, `OTG5_OTG_M_CONST_DTO*`, `OTG5_OTG_PIPE_UPDATE_STATUS`, `GSL_SOURCE_SELECT`, or `DWB_SOURCE_SELECT` masks can cause bad variable-refresh behavior, DSC slice/start-position errors, wrong output timing, missed pending-update detection, broken genlock/swaplock coordination, or display writeback sourced from the wrong OPTC.

Power and clock fields are sensitive. Bad `OPTC_CLOCK_CONTROL`, `ODM_MEM_PWR_CTRL*`, `ODM_MEM_PWR_STATUS`, `DIO_MEM_PWR_CTRL*`, `DIO_MEM_PWR_STATUS`, `DIO_CLK_CNTL*`, `DIO_POWER_MANAGEMENT_CNTL`, or `DIG_SOFT_RESET` constants can leave memory banks forced on, power-gate an active I2C/HPD/ODM path, prevent light sleep, reset the wrong DIG/HDCP/PHY path, or keep display-output clocks gated while link hardware is active.

I2C/DDC fields have user-visible failure modes. Incorrect `DC_I2C_CONTROL`, `DC_I2C_ARBITRATION`, `DC_I2C_SW_STATUS`, `DC_I2C_DDCx_SPEED`, `DC_I2C_DDCx_SETUP`, `DC_I2C_TRANSACTION*`, `DC_I2C_DATA`, `DC_I2C_EDID_DETECT_CTRL`, or read-request interrupt masks can break EDID reads, fail arbitration with firmware/hardware users, hang the software I2C engine, misprogram speed/timing, corrupt data FIFO indexing, or leave the engine owned by software after a failed transaction.

HPD risks include missed or repeated hotplug events. Bad `HPD*_DC_HPD_INT_STATUS`, `HPD*_DC_HPD_INT_CONTROL`, `HPD*_DC_HPD_CONTROL`, `HPD*_DC_HPD_FAST_TRAIN_CNTL`, or `HPD*_DC_HPD_TOGGLE_FILT_CNTL` fields can invert polarity, acknowledge the wrong event, mask HPD RX IRQs, misread live sense state, shorten filter delays, or destabilize fast-training behavior.

DP AUX risks affect DisplayPort link bring-up and runtime DPCD operations. Incorrect `DP_AUX*_AUX_CONTROL`, `AUX_SW_CONTROL`, `AUX_ARB_CONTROL`, `AUX_INTERRUPT_CONTROL`, `AUX_SW_STATUS`, `AUX_LS_STATUS`, `AUX_SW_DATA`, `AUX_LS_DATA`, `AUX_DPHY_*`, or `AUX_GTC_SYNC_*` fields can prevent AUX reset completion, target the wrong HPD, lose arbitration, misreport reply length, hide timeout/overflow/protocol errors, corrupt DPCD payload bytes, mis-tune AUX PHY timing, or break GTC sync lock maintenance.

Perfmon risks are diagnostic but still important. Wrong `DC_PERFMON19_*` or `DC_PERFMON20_*` fields can select the wrong event, leave counters active, miss interrupts, acknowledge the wrong source, or return misleading counter values during display performance and power investigations.

The range contains many repeated generated patterns: DDC1-DDC6 setup/status/speed registers, HPD0-HPD5 blocks, DP_AUX0-DP_AUX2 blocks, and perfmon instances 19-20. Instance suffix mistakes are hard to catch at compile time because macro names are structurally valid and often differ only by a digit.

Chunk-boundary risk is present at both ends. The chunk begins at `OTG5_OTG_DRR_V_TOTAL_CHANGE`, after earlier OTG5 fields were defined in the previous chunk, and ends inside the `DP_AUX2_AUX_GTC_SYNC_CONTROLLER_STATUS` field list. The final merge lane should treat those as artificial chunk boundaries, not hardware block boundaries.

## Test Signals

Useful validation signals are mostly generated-header checks plus DCN30 display behavior:

- Build coverage for DCN30/DCN302 display, DMUB, timing-generator, GPIO/DDC/HPD, IRQ, DIO/link encoder, I2C, and resource files that include `dcn_3_0_0_sh_mask.h`.
- Generated-register validation that every `*_MASK` in this chunk matches its corresponding `*__SHIFT`, does not overlap unintended fields, and matches AMD's authoritative DCN 3.0.0 register database and the companion `dcn_3_0_0_offset.h`.
- Modeset, variable-refresh-rate, DSC, and multi-display tests that exercise OTG5 DRR timing, DSC start position, DTO fields, pipe update pending/status fields, GSL source selection, and DWB source routing.
- ODM/OPTC/DIO power-management tests during boot, modeset, idle, vblank, suspend/resume, and hotplug, watching for incorrect memory-power status, clock-gate state, reset state, underflow, or resume failures.
- EDID/DDC tests across DDC1-DDC6 and VGA-style paths, including repeated reads, failed reads, DDC arbitration contention, slow devices, reset recovery, and speed/prescale variations.
- HPD and HPDRX interrupt tests that connect/disconnect monitors rapidly, verify debounce/filter behavior, check delayed and live sense values, acknowledge interrupts, and ensure polarity and mask bits behave correctly.
- DisplayPort link training and DPCD/AUX transaction tests over AUX0-AUX2, including AUX reset, SW and low-speed reads, timeout/overflow/error paths, reply byte count handling, HPD disconnect during AUX, and PHY timing sensitivity.
- GTC sync diagnostics that validate AUX GTC sync enablement, lock acquisition, lock lost, timeout, phase-adjust violation, offset error, retry, and status/readback fields.
- DC perfmon diagnostics for instances 19 and 20 that program event selection and run/stop modes, read high/low counter values, and verify counter interrupts and acknowledge behavior.

Regression symptoms from bad constants include blank or unstable display, wrong DRR behavior, DSC artifacts, broken display writeback, failed EDID detection, I2C engine hangs, missed or repeated hotplug events, failed DisplayPort link training, AUX timeouts on valid sinks, stuck AUX reset, incorrect HPD sense, failure to enter display low-power states, resume failures, and impossible perf/GTC/debug readbacks.

## Cross-Chunk Notes

This is not a standalone source module; it is one chunk of a large generated DCN 3.0.0 register layout contract. Neighboring chunks own the preceding OTG5 register definitions and the continuation of `DP_AUX2_AUX_GTC_SYNC_CONTROLLER_STATUS` plus subsequent DIO/register families. The later merge/reconciliation lane should combine this with other chunks into a single per-file view and avoid treating this artificial line range as a semantic source boundary.

### subset-b-001702: lines 37215-39587

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 37215-39587

## Scope

This chunk is a generated AMDGPU DCN 3.0.0 register shift/mask header segment. It contains preprocessor constants only: no functions, structs, enums, storage, or executable control flow. Its exported contract is a dense set of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros that describe bit positions and already-shifted masks for display I/O hardware registers.

The range begins in the tail of `DP_AUX2_AUX_GTC_SYNC_CONTROLLER_STATUS`, completes the remaining AUX2 GTC-sync status and PHY-wake fields, then covers full repeated DP AUX3, AUX4, and AUX5 register blocks. It then moves into DIG0-adjacent stream output blocks: `VPG0`, `AFMT0`, `DME0`, `DIG0`, HDMI/TMDS controls, and the beginning of `DP0` link, DPHY, and secondary-data-packet registers through the first fields of `DP0_DP_SEC_FRAMING4`.

## Purpose

The purpose of this file chunk is to bind DCN 3.0.0 symbolic register-field names to the ASIC-specific bit layout used by AMD display code. Consumers include the matching `dcn_3_0_0_offset.h` address header and this shift/mask header, then use register-helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `SRI`, and `SE_SF` to paste register and field names into address, shift, and mask tables.

The covered hardware areas are:

- AUX channel engines for DP AUX instances 3, 4, and 5, plus the end of AUX2. These implement software AUX transactions, link-service status, AUX data windows, DPHY timing/status, GTC sync, interrupts, arbitration between software and DMCU/DMUB-style clients, HPD-sensitive behavior, and PHY wake handshakes.
- VPG0, the video packet generator for generic secondary-data packets, ISRC data, MPEG info, per-packet frame/immediate update triggers, pending bits, conflict status, and memory-power state.
- AFMT0, the audio formatter, including HDMI audio packet limits, audio layout/channel/HBR controls, audio infoframe fields, IEC 60958 channel-status bits, audio CRC/test-ramp controls, audio enable/HBR/FIFO status, source selection, and memory power.
- DME0, the dynamic metadata engine, with metadata stream enable/source selection, double-buffer state, and memory-power fields.
- DIG0 front-end/backend-facing controls for source selection, stream start, Dolby Vision enable/status, CRC, test patterns, FIFO calibration/status, HDMI metadata/audio/infoframe/generic packet transmission, general-control packet state, ACR timing packet controls, TMDS lane/control-symbol generation, lane enable, and force-disable.
- DP0 link and stream encoding controls for link training complete/status, pixel format, DP MSA fields, video stream enable/defer/status, steer/TU FIFO overflow reporting, video timing M/N generation, DPHY training/test/scrambler/CRC/fast-training controls, and DP secondary packet stream/audio/GSP framing controls.

Although the repository path is under `sources/distributed-fs/ceph-client`, this chunk is AMDGPU display hardware metadata. It has no Ceph, filesystem, distributed storage, or network protocol behavior.

## Important APIs, Types, And Macros

There are no callable APIs or C types defined here. The important interface is the generated macro namespace:

- `*_SHIFT` gives the field's low bit.
- `*_MASK` gives the field mask in its register position.
- Comment lines such as `//DP_AUX3_AUX_CONTROL` and `// addressBlock: ...` group the macros by hardware register and register block.

The AUX3/AUX4/AUX5 groups are structurally repeated. Each instance defines:

- `AUX_CONTROL`: `AUX_EN`, `AUX_RESET`, `AUX_RESET_DONE`, link-service read/update gates, `AUX_IGNORE_HPD_DISCON`, mode detect, HPD select, impedance-calibration request enable, test mode, deglitch enable, and spare high bits.
- `AUX_SW_CONTROL`: software transaction launch via `AUX_SW_GO`, link-service read trigger, start delay, and write-byte count.
- `AUX_ARB_CONTROL`: AUX register arbitration priority, owner/status bits, queued-go suppression, software request/done bits, and DMCU request/done aliases.
- `AUX_INTERRUPT_CONTROL`: SW done, LS done, GTC sync lock-done, and GTC sync error interrupt/ack/mask triplets.
- `AUX_SW_STATUS` and `AUX_LS_STATUS`: done/request state, timeout state, timeout/overflow/HPD disconnect/non-AUX-mode/invalid framing errors, reply byte count, arbitration state for SW, CP IRQ and updated/ack bits for LS.
- `AUX_SW_DATA` and `AUX_LS_DATA`: 8-bit data windows, 5-bit indexes, read/write direction for SW, and SW autoincrement disable.
- `AUX_DPHY_TX_REF_CONTROL`, `AUX_DPHY_TX_CONTROL`, `AUX_DPHY_RX_CONTROL0`, `AUX_DPHY_RX_CONTROL1`, `AUX_DPHY_TX_STATUS`, and `AUX_DPHY_RX_STATUS`: reference selection/dividers, TX precharge/OE timing, RX windows and thresholds, timeout length/multiplier, TX/RX state, and measured half-symbol periods.
- `AUX_GTC_SYNC_CONTROL`, `AUX_GTC_SYNC_ERROR_CONTROL`, `AUX_GTC_SYNC_CONTROLLER_STATUS`, and `AUX_GTC_SYNC_STATUS`: GTC sync enable, impedance calibration, acquisition/maintenance periods, block requests, retry/threshold controls, lock/error state, ACK bits, AUX transaction-style receive errors, reply byte count, NACK, and master request reporting.
- `AUX_PHY_WAKE_CNTL`: wake go, pending, priority, and ack fields.

The VPG0 group defines byte-indexed packet payload access (`VPG_GENERIC_PACKET_ACCESS_CTRL`, `VPG_GENERIC_PACKET_DATA`), frame and immediate update controls for generic packets 0-14, pending mirrors, generic lock/conflict status, memory power state, ISRC1/2 indexed data access, and MPEG infoframe payload/update fields.

The AFMT0 group defines audio and protocol-visible fields: HDMI audio packets per line and max-packet behavior, audio layout override/select, channel-enable bitmap, DP audio stream ID, HBR and 60958 overrides, audio infoframe checksum/channel-count/coding-type/extended-coding/channel-allocation/level-shift/downmix/LFE fields, IEC 60958 channel-status and validity fields, audio CRC controls/results, ramp test controls, audio FIFO overflow and enable-change ACKs, infoframe update/source, source select, and memory-power state.

The DIG0 and HDMI/TMDS groups define front-end start/source routing, output CRC, clock/static/random test patterns, FIFO calibration state, HDMI metadata packet control, HDMI 2.0-style scramble/deep-color/clock-channel controls, HDMI error and AVMUTE/audio/VBI/infoframe/ACR controls, generic packet send/continuous/line-reference/update-lock bits for packets 0-14, immediate send and pending bits, generic packet line registers, double-buffer pending bits, general control packet phase/AVMUTE fields, TMDS control characters/sync patterns/control bits/DC balancing, per-control-symbol data-select/delay/invert/modulation/feedback/pattern fields, DIG version, lane enable, and force-disable.

The DP0 portion defines the first stream/link fields for link training and embedded-panel mode, pixel encoding/depth/combine, MSA colorimetry/misc bytes, DP lane count, video stream enable/deferred disable/status, steer/TU FIFO overflow/reset/ack/mask fields, video M/N timing and values, link framing/idle/VBID/enhanced-frame controls, HBR2 eye pattern enable, MSA/VBID location and field polarity, video-disable interrupt/ack/mask fields, DPHY test lanes/FEC/bypass/skew, DPHY training pattern and custom 10-bit symbols, 8b/10b reset/disparity fields, PRBS and scrambler controls, DPHY CRC and MST CRC controls/status, fast-training controls/status, and the start of DP secondary packet controls (`DP_SEC_CNTL`, `DP_SEC_CNTL1`, `DP_SEC_FRAMING1-4`).

## Control Flow

This header has no local control flow. Runtime behavior is created by display code that includes this generated namespace and passes the masks/shifts into register-helper tables.

The main consumption pattern is:

1. DCN 3.0/3.0.2 source includes `dcn/dcn_3_0_0_offset.h` and `dcn/dcn_3_0_0_sh_mask.h`.
2. Register-list macros such as `SRI(AFMT_CNTL, DIG, id)` or `SRI(DP_SEC_CNTL, DP, id)` resolve the correct instance-specific register addresses from the offset header.
3. Field-list macros such as `SE_SF(DP0_DP_SEC_CNTL, DP_SEC_STREAM_ENABLE, mask_sh)` or `AUX_SF(DP_AUX0_AUX_CONTROL, AUX_EN, mask_sh)` paste generated `__SHIFT`/`_MASK` names into shift/mask structures.
4. Driver methods call `REG_UPDATE`, `REG_UPDATE_N`, `REG_SET`, `REG_GET`, `REG_WAIT`, or `REG_READ/WRITE`; those helpers use this chunk's constants to isolate and encode bitfields.

For AUX, the operational sequencing lives in `display/dc/dce/dce_aux.c`: code checks arbitration state, enables/reset AUX, requests software ownership, writes AUX transaction bytes through `AUX_SW_DATA`, launches `AUX_SW_GO`, polls/acks `AUX_SW_DONE`, decodes reply byte counts, and releases ownership through `AUX_ARB_CONTROL`. This chunk provides the per-instance bit layout for those operations on later AUX instances, but it does not implement the transaction state machine.

For stream encoding, `display/dc/dio/dcn30/dcn30_dio_stream_encoder.h` and `.c` are representative consumers. The header maps many fields from this chunk into `SE_COMMON_MASK_SH_LIST_DCN30`, including HDMI generic packet controls, `DP_SEC_CNTL`, `DP_SEC_CNTL1`, `DP_SEC_FRAMING4`, `DIG_FE_CNTL`, `DIG_FIFO_STATUS`, `DP_PIXEL_FORMAT`, `DP_VID_STREAM_CNTL`, `DP_VID_TIMING`, `DP_SEC_AUD_N`, `DP_SEC_TIMESTAMP`, and DME metadata controls. The `.c` file then updates HDMI generic packet send/continuous/line registers, DP GSP enable bits, DP secondary stream master enable, HDMI scrambling/deep-color/ACR/VBI/audio-infoframe controls, FIFO reset via `DIG_START`, and DP audio timestamp/N configuration.

For DP link encoding, `display/dc/dio/dcn10/dcn10_link_encoder.h` and `.c` show the shared lower-level DP consumption pattern. Link encoder methods use the DP0 DPHY symbols, PRBS, scrambler, training pattern, link framing, link-training complete, and secondary-packet fields to program test patterns, link training state, MST allocation, PSR fast training, and DP PHY behavior.

## State And Persistence Behavior

The header stores no state and persists nothing. It describes MMIO register state in the DCN display hardware. That state is owned by the display engine, AUX PHY/controller logic, stream encoders, audio formatter, packet generators, metadata engine, power-management logic, firmware-facing display microcontroller paths, and reset/suspend/resume flows.

State represented by this chunk includes:

- AUX controller configuration, ownership, software/link-service transaction progress, indexed data windows, interrupt latches and ACK bits, DPHY timing configuration/status, GTC sync lock/error status, and PHY wake handshakes for AUX2 tail and AUX3-AUX5.
- VPG packet payload storage and update state, including pending frame/immediate updates for generic packets 0-14 and memory power state for packet storage.
- AFMT audio packet configuration, audio infoframe and IEC 60958 metadata, channel enable/layout/HBR state, audio CRC and test-ramp state, FIFO overflow latches, audio enable-change status, and AFMT memory power.
- DME metadata requestor/stream-type/enable and double-buffer pending/taken/clear/disable state, plus DME memory power state.
- DIG/HDMI/TMDS state for source routing, stream start/reset, Dolby Vision enable/missed status, FIFO calibration/error state, HDMI metadata and generic packet scheduling, HDMI error/AVMUTE/deep-color/scrambling/ACR/audio/VBI/infoframe state, TMDS symbol/control generation, lane enables, and forced DIG disable.
- DP link/stream state for link training completion, stream enable/deferred disable, MSA bytes, M/N timing values, FIFO overflow flags, DPHY training/test/FEC/scrambler/CRC/fast-training status, DP secondary stream master enable, GSP enables, GSP0 line/send/pending/deadline fields, secondary-packet framing windows, collision status/ACK, and audio mute status.

Some fields are configuration latches, some are live readback, some are write-one-to-clear or ACK-style bits, and some are double-buffer pending indicators. The generated names and masks do not encode access type or ordering requirements. Incorrect writes can persist until a modeset, link retrain, hotplug, display stream reprogramming, power transition, suspend/resume restore, or GPU/display reset rewrites the block.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`, which supplies the matching register addresses and base indices. In that header, the DP0 block in this chunk maps to addresses such as `mmDP0_DP_LINK_CNTL` at `0x2108`, `mmDP0_DP_DPHY_CNTL` at `0x2117`, `mmDP0_DP_SEC_CNTL` at `0x212b`, and `mmDP0_DP_SEC_FRAMING4` at `0x2130`, all with base index 2. The offset file continues beyond this chunk with later DP0 secondary, MST, DSC, metadata, ALPM, and GSP registers whose masks appear in later chunks.

Visible include sites for `dcn_3_0_0_sh_mask.h` in this tree include:

- `display/dc/resource/dcn30/dcn30_resource.c`, which builds DCN 3.0 resource objects and register tables.
- `display/dc/irq/dcn30/irq_service_dcn30.c` and `display/dc/irq/dcn302/irq_service_dcn302.c`, which use generated masks for IRQ source/status/ack programming.
- `display/dc/gpio/dcn30/hw_factory_dcn30.c` and `display/dc/gpio/dcn30/hw_translate_dcn30.c`, which use the same generated register namespace for GPIO/HPD/DDC translation.
- `display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`, which includes DCN 3.0 register metadata for display clock manager programming.
- `display/dmub/src/dmub_dcn30.c` and `display/dmub/src/dmub_dcn302.c`, which expose DCN 3.0/3.0.2 register metadata to DMUB-facing support.

Functional integration points include `display/dc/dce/dce_aux.*` for AUX transaction state, `display/dc/dio/dcn30/dcn30_dio_stream_encoder.*` for HDMI/DP stream packet/audio/metadata programming, `display/dc/dio/dcn10/dcn10_link_encoder.*` for DP PHY/link training and MST-related programming, `display/dc/dio/dcn30/dcn30_vpg.*` for VPG packet payload/update paths, and `display/dc/dio/dcn30/dcn30_afmt.*` for AFMT audio formatter control.

Direct textual references to every exact `DP_AUX3_`, `DP_AUX4_`, or `DP_AUX5_` macro are uncommon because register tables usually instantiate a generic AUX object with an instance ID. Macro pasting converts a generic field like `AUX_SW_GO` into the correct generated `DP_AUXn_AUX_SW_CONTROL__AUX_SW_GO_*` constants.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A wrong shift or mask usually still compiles; it can update the wrong bit, truncate a value, fail to clear an ACK bit, decode stale status, or corrupt adjacent fields during read/modify/write.

AUX fields are timing- and ownership-sensitive. Bad arbitration masks can let software and firmware contend for the same AUX registers. Bad `AUX_SW_DATA` index/data masks can corrupt DP AUX payload bytes or addresses. Bad status/error masks can cause false timeouts, missed HPD disconnects, undetected invalid replies, or loops waiting on the wrong done bit. GTC sync status includes sticky error and ACK fields; confusing status bits with ACK bits can hide lock-loss or critical error conditions.

Repeated AUX3/AUX4/AUX5 layouts are easy to copy incorrectly. If one instance's mask diverges accidentally, only connectors wired to that AUX instance may fail, making the bug appear board- or port-specific.

Packet scheduling fields are dense. VPG and HDMI generic packet controls pack many send/continuous/update/pending bits into one register. Off-by-one shifts can make the driver enable the wrong packet index, use the wrong line number, leave update locks disabled, or wait on another packet's pending bit. That can break HDR metadata, VSC/SPD/adaptive-sync packets, ISRC/MPEG packets, or HDMI vendor-specific packets without breaking basic modeset.

AFMT and HDMI audio fields are protocol-visible. Incorrect channel-count, channel-allocation, IEC 60958, HBR, ACR, or audio-packet fields can produce missing HDMI/DP audio, wrong speaker mapping, broken HBR/non-PCM playback, audio FIFO overflow, invalid CRC/test results, or audio that only fails at specific sample rates/deep-color modes.

DIG/HDMI/TMDS fields can affect visible video. Bad `DIG_START`, source-select, lane-enable, TMDS control-symbol, scrambling, deep-color, FIFO, or force-disable fields can cause blank screens, unstable links, color/deep-color mismatches, HDMI 2.0 scrambling failures above 340 MHz, or hard-to-reproduce FIFO underflow/overflow symptoms.

DP DPHY and link fields are link-training sensitive. Wrong masks for training patterns, PRBS, scrambler, 8b/10b, FEC, fast training, link-training complete, M/N timing, or steer FIFO status can cause link training failure, PSR/fast-training regressions, MST timing problems, CRC validation failures, or invalid custom PHY test patterns.

Chunk boundaries matter. This chunk starts after the beginning of the AUX2 GTC sync controller status register, so the full AUX2 GTC sync field set is split across chunks. It also ends inside `DP0_DP_SEC_FRAMING4`; the final masks for `DP_SEC_AUDIO_MUTE` and `DP_SEC_AUDIO_MUTE_STATUS`, plus later DP0 secondary/MST/DSC/metadata fields, are in following chunks. Per-file reconciliation should merge adjacent chunks before drawing complete-register conclusions.

## Test Signals

Useful validation is mostly generated-header and hardware-behavior oriented:

- Compile coverage for all DCN 3.0 and DCN 3.0.2 files that include `dcn_3_0_0_sh_mask.h`, especially resource, IRQ, GPIO, clock manager, DMUB, AUX, stream encoder, link encoder, VPG, and AFMT paths.
- Generated-header consistency checks that each `REGISTER__FIELD__SHIFT` has a matching `REGISTER__FIELD_MASK`, that the mask width/position agrees with the shift, and that each register in this chunk has a matching offset/base index in `dcn_3_0_0_offset.h`.
- Cross-generation diffs against neighboring DCN headers, reviewed against the ASIC register database, for repeated AUX blocks, HDMI generic packet controls, AFMT audio fields, DP DPHY fields, and DP secondary packet controls.
- AUX functional tests for DPCD reads/writes, I2C-over-AUX EDID reads, reply-byte counts, timeout/defer/NACK handling, HPD disconnect during AUX, CP IRQ/update handling, suspend/resume, and ports wired to AUX3/AUX4/AUX5.
- HDMI and DP modeset tests covering RGB/YCbCr formats, deep color, HDMI scrambling above and below 340 MHz, audio enable/disable, AVMUTE, ACR packets, audio infoframes, HDR/static metadata, vendor-specific packets, and generic packet immediate/frame updates.
- DP link tests for link training, custom/test patterns, PRBS, scrambler, FEC status, enhanced framing, MSA/M/N values, MST allocation, PSR fast training, stream disable/defer, and DPHY/MST CRC reporting.
- Audio tests for stereo and multichannel layouts, HBR/non-PCM formats, sample-rate changes, channel allocation, IEC 60958 channel status, FIFO overflow handling, audio mute/status, and suspend/resume restore.
- Power-management tests that exercise VPG/AFMT/DME memory-power fields and verify packet/audio/metadata state is restored after light sleep, display power gating, and DCN reset paths.

Regression symptoms from bad constants include AUX timeouts or invalid replies on only some ports, missing EDID/DPCD reads, blank HDMI/DP output, bad color depth or HDMI scrambling, missing HDR/adaptive-sync/info packets, no or incorrectly mapped audio, audio FIFO overflows, failed DP link training, PSR fast-training failures, MST allocation errors, stale packet pending bits, or unexpected interrupt storms/missed ACKs.

## Cross-Chunk Notes

This chunk is one slice of the generated DCN 3.0.0 register-layout contract. The previous chunk owns the beginning of `DP_AUX2_AUX_GTC_SYNC_CONTROLLER_STATUS`; this chunk completes AUX2 tail state and adds complete AUX3-AUX5 blocks. The next chunk should complete `DP0_DP_SEC_FRAMING4` and continue through additional DP0 secondary/MST/DSC/metadata registers. The final per-file document should treat this chunk as part of the DCN 3.0 display I/O register namespace, not as an independently maintained module.

### subset-b-001703: lines 39588-41983

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 39588-41983

## Purpose

This chunk is generated AMD DCN 3.0 register field metadata. It contains no executable C code; it publishes `#define` constants for bit shifts and bit masks used to access fields inside DCN 3.0 display MMIO registers. Runtime display code pairs these field constants with register offsets from `dcn_3_0_0_offset.h` and with register helper macros such as `REG_UPDATE`, `REG_SET`, `REG_GET`, and `REG_WAIT`.

The range covers 2,172 shift/mask macros. It starts in the middle of the `DP0` DisplayPort secondary-data block, covers `VPG1`, `AFMT1`, `DME1`, `DIG1`, and a large `DP1` link/stream block, then enters the beginning of `VPG2`. Although this tree path is under a `ceph-client` source mirror, the file is AMDGPU display-driver hardware metadata and has no distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this chunk. The public interface is the macro naming contract:

- `<register>__<field>__SHIFT`: bit index for a field.
- `<register>__<field>_MASK`: bit mask for that field.
- Register comments, such as `//DP1_DP_DPHY_CNTL`, group the following field macros by hardware register.

Major register families in this chunk:

- `DP0_*`: secondary-data packet, audio `M/N`, MST multi-stream encoder allocation, MSA timing, MSO, DSC, metadata, ALPM, generic-stream-packet slots 8-11, and double-buffer status fields for DisplayPort instance 0.
- `VPG1_*`: generic packet RAM index/data, frame-update and immediate-update controls for generic packets 0-14, conflict status, memory power, ISRC data, and MPEG info fields.
- `AFMT1_*`: HDMI/DP audio formatter packet control, audio infoframe fields, IEC 60958 channel-status fields, ramp and CRC controls, status, source selection, infoframe update, and memory-power fields.
- `DME1_*`: metadata engine enable, requestor ID, stream type, source select, pixel format, line reference, line number, and memory-control fields.
- `DIG1_*`: digital stream encoder fields for front-end control, output CRC, clock/test/random patterns, FIFO status, HDMI metadata, HDMI control/status, audio/ACR/VBI/infoframe/generic-packet controls, AVMUTE/general-control, TMDS controls, lane enable, and forced disable.
- `DP1_*`: full DisplayPort instance 1 field coverage for link control, pixel format, MSA colorimetry/misc/timing/VBID, video stream, steer FIFO, video `M/N`, DPHY training/test/CRC/fast-training/FEC fields, secondary-data/audio/metadata fields, MST slot allocation, MSO, DSC, ALPM, generic-stream-packet controls, and double-buffer status.
- `VPG2_*`: beginning of generic packet access/data and update/status fields for video packet generator instance 2.

The chunk is consumed indirectly by DCN object declarations. Examples from nearby AMD display code include `VPG_DCN3_REG_LIST`, `DCN3_VPG_MASK_SH_LIST`, `AFMT_DCN3_REG_LIST`, `DCN3_AFMT_MASK_SH_LIST`, `SE_DCN3_REG_LIST`, `SE_COMMON_MASK_SH_LIST_DCN30`, and `LINK_ENCODER_MASK_SH_LIST_DCN30`. These macros copy the generated shifts into `struct dcn30_vpg_shift`, `struct dcn30_afmt_shift`, `struct dcn10_stream_encoder_shift`, and `struct dcn10_link_enc_shift`, and copy masks into matching `*_mask` structs.

## Control Flow

This header has no runtime control flow. The runtime sequence is provided by the display driver:

1. DCN30/302 resource, IRQ, GPIO, clock, and DMUB code includes `dcn_3_0_0_offset.h` and this matching `dcn_3_0_0_sh_mask.h`.
2. Resource construction in `dcn30_resource.c` creates register tables for VPG, AFMT, stream encoders, and link encoders. `SRI(...)` builds per-instance register addresses from the offset header, while `SE_SF(...)` and `LE_SF(...)` pull shift/mask fields from this header.
3. `dcn30_stream_encoder_create()` maps a `DIG` engine to matching VPG/AFMT/DME instances, allocates `struct dcn10_stream_encoder`, `struct vpg`, and `struct afmt`, and passes the generated register, shift, and mask tables into `dcn30_dio_stream_encoder_construct()`.
4. Link encoder construction uses the `DP0`-style field names from this header to initialize per-link `dcn10_link_enc_shift`/`mask` state for DP training, MST allocation, DPHY test patterns, AUX/HPD integration, and stream enablement.
5. Later modeset, hotplug, audio, DP, HDMI, DSC, metadata, and MST paths call helper macros that apply these shifts and masks to MMIO reads/writes.

The macro values do not encode sequencing. Correct order is still enforced by higher-level stream/link/audio code: link training, video timing programming, info-packet updates, audio setup, DSC PPS packet programming, metadata engine enablement, double-buffer commits, and status/ack polling all happen outside this generated file.

## State And Persistence Behavior

The file stores no software state and persists nothing on disk. It describes fields in persistent or semi-persistent GPU MMIO registers.

Hardware state represented here includes DP stream enablement, link/framing/timing settings, MST slot allocation, DPHY training/test/CRC state, secondary-data packet enables and send/pending/deadline state, audio `M/N` values, HDMI/TMDS packet generation, VPG generic packet RAM contents and update requests, AFMT audio channel/status fields, DSC enable and bytes-per-pixel fields, ALPM sleep/standby requests, and metadata packet scheduling.

Register persistence is hardware-defined. Configuration bits generally remain until another modeset, link reconfiguration, power-gating event, suspend/resume, or ASIC reset. Many status and control fields in this chunk are side-effect-sensitive: `*_PENDING`, `*_ACTIVE`, `*_STATUS`, `*_DEADLINE_MISSED`, `*_ACK`, `*_CLR`, `*_DB_TAKEN_CLR`, CRC-valid, FIFO-error, collision, conflict, fast-training-complete, and memory-power status fields may be read-only, sticky, write-one-to-clear, self-clearing, or timing-sensitive. This generated header only gives bit positions; consumers must know each field's access semantics.

## Dependencies And Integration Points

This chunk must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`, which provides the matching MMIO register addresses and base indices.
- DCN base-address definitions such as `DCN_BASE__INST0_SEG*`, used by resource macros to turn offsets into absolute MMIO addresses.
- AMD display helper macros in `reg_helper.h` and DCN resource code, which depend on the generated token names compiling exactly.

Key integration points in this source tree:

- `display/dc/resource/dcn30/dcn30_resource.c`: builds `vpg_regs`, `afmt_regs`, `stream_enc_regs`, `link_enc_regs`, `vpg_shift`, `afmt_shift`, `se_shift`, and `le_shift` from the generated constants.
- `display/dc/dcn30/dcn30_vpg.h` and `.c`: use `VPG_GENERIC_PACKET_ACCESS_CTRL`, `VPG_GENERIC_PACKET_DATA`, frame-update, immediate-update, and conflict fields for generic info-packet programming.
- `display/dc/dcn30/dcn30_afmt.h` and `.c`: use AFMT audio and IEC 60958 fields for HDMI/DP audio setup, mute, update, and memory-power control.
- `display/dc/dio/dcn30/dcn30_dio_stream_encoder.h` and `.c`: use DIG/HDMI/DP/DSC/metadata fields for stream attribute programming, info packets, DP audio, HDMI audio, DSC PPS packets, and state readback.
- `display/dc/dio/dcn10/dcn10_link_encoder.h` and link encoder implementations: use DP DPHY, link framing, MST slot allocation, and stream-enable fields for physical link setup and diagnostics.
- `display/dmub/src/dmub_dcn30.c` and `dmub_dcn302.c`: include the same DCN 3.0 generated headers for DMUB-facing register access.

## Risks And Edge Cases

- Register drift is the primary risk. These are untyped numeric constants; a wrong bit shift or mask can compile cleanly while programming or reading the wrong hardware field.
- The chunk is instance-heavy. `DP0`, `DP1`, `DIG1`, `VPG1`, `VPG2`, `AFMT1`, and `DME1` names are structurally similar, so copy-generation mistakes can affect only one connector, stream engine, packet generator, or audio formatter.
- Some runtime field lists use instance-0 field names as canonical mask/shift sources, for example `DP0_*`, `DIG0_*`, `VPG0_*`, and `AFMT0_*`. This works only if repeated instances have identical field layouts; any instance-specific layout difference requires explicit handling.
- Status/control fields are easy to misuse. Pending, ack, clear, collision, conflict, deadline-missed, CRC-valid, FIFO-error, and double-buffer bits often have hardware side effects or required polling windows.
- Packet update timing matters. VPG and HDMI generic packet frame/immediate updates, DP secondary packet sends, GSP line numbers, metadata packet line references, and double-buffer pending bits interact with vertical blank, line timing, and packet RAM locking.
- DisplayPort MST/MSO and DSC fields are coupled to link bandwidth and stream allocation decisions. Incorrect `DP_MSE_*`, `DP_MSO_*`, `DP_DSC_*`, or GSP PPS fields can produce failures only with MST, DSC, high refresh, high bpp, or multi-display modes.
- Audio failures can be subtle. Bad AFMT or DP secondary audio masks may only show as silent audio, incorrect channel status, bad IEC 60958 metadata, wrong audio clock regeneration, or packet underflow with specific sample rates.
- HDMI/TMDS packet fields cover many generic packet slots. Mask errors can corrupt AVI/audio/vendor/infoframe scheduling or cause missed metadata/AVMUTE behavior without a direct kernel error.

## Test Signals

Useful validation signals are mostly integration and hardware-facing:

- Build coverage for AMDGPU display with DCN30/302 paths enabled catches missing or renamed generated macros in `dcn30_resource.c`, `dcn30_vpg.h`, `dcn30_afmt.h`, stream encoder, link encoder, IRQ, GPIO, clock, and DMUB include paths.
- Boot and modeset on DCN 3.0 hardware with DP and HDMI outputs should show stable link training, no blank displays, correct hotplug, and no stream-disable or FIFO-level errors.
- DP audio and HDMI audio tests should verify audio presence, channel layout, mute/unmute, IEC 60958 channel-status fields, and sample-rate changes.
- Info-packet tests should exercise HDMI generic packets, DP secondary-data packets, metadata packets, ISRC/MPEG data, and immediate/frame update paths.
- MST validation should cover slot allocation, payload updates, multiple streams, and `DP_MSE_*` status/pending behavior.
- DSC validation should cover enabling/disabling DSC, PPS packet delivery through GSP11, slice width/bytes-per-pixel fields, and high-bandwidth modes.
- Low-power and eDP tests should watch ALPM sleep/standby fields and resume behavior.
- Diagnostic readback should monitor `*_PENDING`, `*_DEADLINE_MISSED`, `*_COLLISION_STATUS`, `VPG_GENERIC_CONFLICT_OCCURED`, HDMI packet missed/error, DIG FIFO error, DPHY CRC validity, fast-training complete, and double-buffer taken/pending bits.

### subset-b-001704: lines 41984-44385

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 41984-44385

## Scope

This chunk is part of the generated AMD DCN 3.0.0 ASIC register shift/mask header. It exports preprocessor constants for bit positions and bit masks used by AMDGPU display code when programming DCN 3.0 stream-output hardware. There is no executable C logic in this range: no functions, structs, enums, variables, allocation, locking, or persistence code.

The requested line range contains 2,168 `#define` entries: 1,087 `__SHIFT` constants and 1,081 `_MASK` constants. The mismatch is because the chunk boundary is artificial: it starts at the tail of `VPG2_VPG_GENERIC_STATUS` mask definitions and ends inside the `DIG3_HDMI_GENERIC_PACKET_CONTROL10` definition set.

Although the source path is under a local `ceph-client` tree, this file is AMDGPU display-driver hardware metadata, not distributed filesystem code.

## Purpose

The purpose of this chunk is to provide exact bitfield metadata for DCN 3.0 Display IO stream generation blocks. Runtime code combines these constants with the matching register offsets from `dcn_3_0_0_offset.h` so helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `SE_SF`, `HWS_SF`, and DMUB field helpers can write or read named hardware fields without open-coded bit arithmetic.

Major hardware domains covered in this slice are:

- Tail fields for `VPG2`, then complete `VPG3` generic packet generator metadata: generic packet access/data, generic stream packet frame/immediate update controls, status, memory power, ISRC packet data, and MPEG infoframe fields.
- `AFMT2` and `AFMT3` audio formatter fields: HDMI audio/VBI packet controls, audio infoframe bytes, IEC 60958 channel-status words, CRC, audio test ramp controls, status/ack bits, audio source selection, and formatter memory power.
- `DME2` and `DME3` display micro-engine control and memory-power fields.
- `DIG2` and beginning of `DIG3` stream encoder front-end and HDMI/TMDS fields: front-end control, output CRC, test/clock/random patterns, FIFO status, HDMI metadata/control/status/audio/ACR/VBI/infoframe/generic-packet controls, HDMI double-buffering, TMDS control-symbol generation, lane enable, version, and force-disable controls.
- The full `DP2` stream/link field set: link control, pixel format, MSA, video timing and `M/N`, link framing, DPHY training/test/CRC/scrambler controls, secondary-data packet control, audio packet timing, MST/MSE allocation fields, MSO controls, DSC enable/bytes-per-pixel, ALPM, generic-stream-packet controls, and DP double-buffer status.

## Important API Surface

The exported API is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

Important visible register families include:

- `VPG2_VPG_*` and `VPG3_VPG_*` fields for packet table access, generic packet byte programming, per-packet frame/immediate update bits, pending bits, conflict status/clear, GSP memory light sleep, ISRC data indexing, and MPEG info update.
- `AFMT2_AFMT_*` and `AFMT3_AFMT_*` fields for audio layout selection, channel enable masks, DP audio stream ID, 60958 override and channel status, audio CRC source/channel/count/result, test ramp min/max/inc/dec controls, FIFO overflow ack, AZ audio enable-change ack, and audio infoframe line/update behavior.
- `DME2_DME_*` and `DME3_DME_*` fields for DME enable/reset/read-write arbitration, reference clock control, urgent state, memory power modes, and memory power status.
- `DIG2_DIG_*` and `DIG3_DIG_*` fields for stream-encoder front-end start, stereosync, HDMI/DP pixel encoding, TMDS color format, output CRC enable/source, pattern generators, FIFO level/error/calibration state, backend power/status, lane enablement, and forced disable.
- `DIG2_HDMI_*` and `DIG3_HDMI_*` fields for HDMI packet generation version, keepout/deep-color/scramble settings, audio clock regeneration, VBI/infoframe/audio packet send controls, metadata packet controls, generic packet line controls, generic packet send/continuous/immediate/double-buffer pending bits, global control AVMUTE, and HDMI double-buffer lock/taken/clear state.
- `DIG2_TMDS_*` fields for TMDS control characters, sync characters, stereo sync, DC balancer, and generated control-symbol counts. The chunk does not reach the matching `DIG3_TMDS_*` family.
- `DP2_DP_*` fields for stream enable/status/defer, pixel encoding/depth, MSA timing/color/VBID, DPHY training and test patterns, scrambler/8b10b/PRBS/CRC, secondary-data packet enables and pending bits, audio `M/N`/timestamp, MST slot allocation tables, MSO split controls, DSC transport controls, metadata transmission, ALPM, and DP generic stream packets 8 through 11.

These constants are consumed indirectly through field-list macros. For example, `dcn30_resource.c` builds `dcn30_vpg_shift`/`dcn30_vpg_mask` from `DCN3_VPG_MASK_SH_LIST`, `dcn30_afmt_shift`/`dcn30_afmt_mask` from `DCN3_AFMT_MASK_SH_LIST`, and stream encoder field tables from `SE_COMMON_MASK_SH_LIST_DCN30`. `dcn30_dio_stream_encoder.h` lists many `DIG`, `HDMI`, `DP`, and `DME` registers that line up with this chunk.

## Control Flow

This header chunk has no local runtime control flow. The runtime sequence is provided by AMDGPU display code:

1. DCN 3.0/3.0.2 resource, IRQ, GPIO, clock, and DMUB files include `dcn_3_0_0_offset.h` and this mask/shift header.
2. Resource construction token-pastes register and field names into generated constants. Address macros such as `SRI(reg_name, block, id)` bind offsets, while field macros such as `SE_SF(reg, field, __SHIFT)` and `SE_SF(reg, field, _MASK)` bind the bit metadata.
3. Stream encoder, VPG, AFMT, DME, DP, HDMI, TMDS, IRQ, GPIO, and DMUB code uses those tables through register helpers to program modesets, link training, packet generation, audio, metadata, MST allocation, DSC transport, double buffering, status polling, and interrupt/status acknowledgment.

The constants do not encode ordering requirements. Callers must still sequence clock and memory power, register double-buffer locks, infoframe packet writes, GSP frame/immediate update requests, HDMI/DP stream enablement, DP link training, MST payload updates, DSC transport setup, FIFO/status clears, and suspend/resume restoration correctly.

## State And Persistence Behavior

This chunk stores no software state and persists no files. It describes memory-mapped GPU display state:

- VPG state persists packet RAM/index contents, frame/immediate update request bits, pending bits, conflict flags, ISRC/MPEG payload bytes, and packet-generator memory-power settings.
- AFMT state persists HDMI/DP audio packet formatting, channel-status words, audio infoframes, source/channel layout selection, CRC/test-ramp configuration, status/ack bits, and AFMT memory-power state.
- DIG/HDMI/TMDS state persists stream encoder control, pixel encoding/deep color/scrambling, packet generation, audio clock regeneration, generic packet scheduling, double-buffer status, FIFO calibration/error state, CRC capture, test patterns, lane enablement, and TMDS symbol generation.
- DP2 state persists DisplayPort link and stream configuration, MSA timing, secondary-data packet enables, audio timing values, DPHY training/test/scrambler/CRC controls, MST payload allocation state, MSO split state, DSC transport controls, ALPM controls, metadata transmission, and DP generic stream-packet scheduling.

Hardware persistence is power-domain dependent. Values can remain active until a modeset, link reconfiguration, display block reset, power gate, suspend/resume transition, or GPU reset. Status, pending, clear, acknowledge, lock, and power-state fields may be sticky, self-clearing, read-only, write-one-to-clear, or sequencing-sensitive; the generated header only supplies bit positions and masks, not semantic access rules.

## Dependencies And Integration Points

This chunk is tightly coupled to:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`, which provides the matching MMIO register offsets and base indices.
- AMD display register helpers in `reg_helper.h`, DMUB field helpers in `dmub_reg.h`, and generated field-list macros in DCN stream encoder, VPG, AFMT, DIO, and resource headers.
- DCN 3.0 register database generation. The macro names and numeric constants must match the ASIC specification and the corresponding offset header exactly.

Direct include sites in this repository include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c`

The most direct functional integration is stream output. `dcn30_resource.c` maps VPG, AFMT, and DME blocks to DIO stream encoder instances. `dcn30_dio_stream_encoder.h` constructs the stream encoder register set for `DIG`, `DP`, `DME`, HDMI, and AFMT programming and lists field names that depend on matching `__SHIFT` and `_MASK` macros from this header family.

## Risks And Edge Cases

- A wrong shift or mask compiles cleanly but targets the wrong hardware bits. High-risk fields here include stream enables, DP link/DPHY training, HDMI deep-color/scrambler controls, audio/ACR timing, generic packet send/pending bits, double-buffer locks, interrupt/status clears, MST allocation, DSC transport, and memory-power controls.
- Repeated instance families are copy-sensitive. `VPG2`/`VPG3`, `AFMT2`/`AFMT3`, `DME2`/`DME3`, and `DIG2`/`DIG3` are structurally similar but not fully interchangeable; a drift can affect only one connector, pipe, or multi-display configuration.
- `DP2` is a dense field set spanning link training, stream timing, secondary packets, MST, MSO, DSC, and ALPM. Small bitfield errors may only appear under specific combinations such as high link rates, DSC-enabled modes, MST topologies, audio, or low-power transitions.
- Status and control bits share many registers. Incorrect read-modify-write masks can fail to clear sticky status, clear a status bit unexpectedly, leave a pending update stuck, or race with hardware double-buffer ownership.
- The range starts and ends mid-family. Whole-file conclusions about `VPG2_GENERIC_STATUS` or `DIG3_HDMI_GENERIC_PACKET_CONTROL10` require adjacent chunks.
- Generated constants are untyped preprocessor macros. They provide no compile-time validation of access width, read/write semantics, reset value, volatile behavior, or required register sequencing.

## Test Signals

Useful validation signals for this chunk are:

- Compile AMDGPU display support for DCN 3.0 and DCN 3.0.2. Missing or renamed macros should fail in resource construction, stream encoder, VPG/AFMT, IRQ, GPIO, clock, and DMUB paths.
- Mechanically verify the generated structure: every complete field in this range should have a matching `__SHIFT` and `_MASK`, while known chunk-boundary exceptions should reconcile with adjacent chunks.
- Diff this slice against AMD's authoritative DCN 3.0 register database and the matching `dcn_3_0_0_offset.h`; also compare repeated instance families where the ASIC expects identical layouts.
- Exercise display outputs using DIO instances 2 and 3: HDMI and DP modesets, hotplug, link-rate/lane-count changes, suspend/resume, blank/unblank, and multi-display configurations.
- Validate HDMI packet behavior: audio playback, ACR generation, infoframes, generic packets, metadata packets, AVMUTE, deep color, scrambling, VBI packets, and double-buffer update/pending behavior.
- Validate DP behavior on instance 2: link training patterns, scrambler/8b10b/PRBS/CRC paths, MSA timing, audio secondary packets, metadata transmission, MST payload allocation, MSO split modes, DSC transport, ALPM, and stream enable/disable sequencing.
- Watch for kernel log or diagnostic symptoms: link-training failures, AUX/DP timeouts, blank displays, FIFO level errors, CRC mismatches, audio dropouts, corrupt infoframes, stuck pending bits, MST bandwidth/allocation errors, DSC artifacts, and resume failures.

## Cross-Chunk Notes

This chunk is a partial view of `dcn_3_0_0_sh_mask.h`. Previous chunks own the beginning of the `VPG2` family, including the missing `VPG2_VPG_GENERIC_STATUS` shift definitions. Later chunks continue `DIG3_HDMI_GENERIC_PACKET_CONTROL10` and cover the rest of the `DIG3`/`DP3` and later DCN 3.0 field namespace. The final per-file research document should merge adjacent chunk reports before making complete claims about all stream encoder instances or all DCN 3.0 register fields.

### subset-b-001705: lines 44386-46812

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 44386-46812

## Scope

This chunk is a generated AMD DCN 3.0.0 register shift/mask slice. It contains no C functions, structs, enums, variables, includes, locks, or executable logic. Its exported interface is entirely preprocessor constants of the form `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`, consumed with matching register-offset constants from `dcn_3_0_0_offset.h`.

The requested range contains 2,164 `#define` entries: 1,078 shift constants and 1,086 mask constants. It starts in the tail of `DIG3_HDMI_GENERIC_PACKET_CONTROL10`, finishes the remaining DIG3 HDMI/audio/TMDS/backend field masks, covers a complete `DP3` DisplayPort stream/link block, covers the `VPG4`, `AFMT4`, `DME4`, and `DIG4` stream-encoder companion blocks, and then enters `DP4` through `DP4_DP_MSA_TIMING_PARAM3`. The final requested line is only the `//DP4_DP_MSA_TIMING_PARAM4` section marker; its fields start after this chunk and should be handled by the following chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata, not distributed filesystem logic.

## Purpose

The purpose of this slice is to describe bit layouts for DCN 3.0 display I/O registers so driver code can program HDMI, TMDS, DisplayPort, audio, generic secondary-data packets, metadata packets, link training, MST allocation, DSC-over-DP control, and stream timing through symbolic field names instead of hard-coded bit positions.

The major hardware areas covered here are:

- DIG3 tail: HDMI generic packet double-buffer status, HDMI double-buffer control, HDMI ACR N/CTS values for 32/44.1/48 kHz families, AFMT audio clock status, DIG backend routing/enables, TMDS control characters, sync patterns, DC balancer fields, DIG version/lane enables, and forced disable.
- DP3: DisplayPort link, pixel format, MSA colorimetry/timing, video stream enable/status, steer FIFO, video M/N, DPHY training/test/scrambler/CRC/fast-training fields, secondary-data packet controls, audio M/N readback, MST/MSE payload timing and slot allocation, DSC mode/slice width, metadata transmission, ALPM, GSP8-GSP11, and generic-packet double-buffer status.
- VPG4: generic packet RAM access/data, frame and immediate update requests/pending flags for generic packets 0-14, generic packet conflict/lock status, VPG memory power, ISRC indexed data, and MPEG infoframe fields.
- AFMT4: HDMI/DP audio packet controls, audio infoframe bytes, IEC 60958 channel-status words, audio CRC/test ramp controls, audio status/ack fields, source select, infoframe update, and AFMT memory power.
- DME4: dynamic metadata engine enable, HUBP requestor select, stream type, double-buffer pending/taken/clear/disable, and DME memory power fields.
- DIG4: front-end source selection/start/bypass/input-pixel/Dolby Vision fields, output CRC, test/clock/random patterns, FIFO status, HDMI metadata/control/status/audio/ACR/VBI/infoframe/generic packet controls, HDMI double-buffering, AFMT bridge control, backend routing/enables, TMDS fields, lane enables, DIG version, and forced disable.
- DP4 partial: DisplayPort link, pixel format, MSA colorimetry, lane config, video stream control, timing, video M/N, link framing, HBR2 pattern, interrupt control, DPHY training/symbol/scrambler/CRC/fast-training, secondary packet/audio/MST/MSE controls, and MSA timing parameters 1-3.

## Important APIs, Types, And Macros

There are no callable APIs. The important API surface is the generated macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the bit offset for a field within a 32-bit MMIO register.
- `REGISTER__FIELD_MASK` gives the pre-shifted bit mask for that field.
- Register comments such as `//DP3_DP_SEC_CNTL` and address-block comments such as `// addressBlock: dce_dc_dio_dp3_dispdec` group constants by hardware register block.

Driver helper macros such as `FD_SHIFT`, `FD_MASK`, `REG_SET`, `REG_UPDATE`, and `REG_GET` depend on these names being stable. Stream-encoder register lists typically use token-pasting against instance 0 names in structure definitions while instance register tables map `DP`, `DIG`, `VPG`, `AFMT`, and `DME` IDs to concrete `DP3`, `DIG4`, and similar register names.

High-value field groups in this chunk include:

- Double-buffer state and synchronization: `HDMI_DB_PENDING`, `HDMI_DB_TAKEN`, `HDMI_DB_TAKEN_CLR`, `VUPDATE_DB_PENDING`, `DP_SEC_DB_*`, `METADATA_DB_*`, and generic packet update pending fields.
- DisplayPort link and stream control: `DP_LINK_TRAINING_COMPLETE`, `DP_LINK_STATUS`, `DP_VID_STREAM_ENABLE`, `DP_VID_STREAM_STATUS`, `DP_UDI_LANES`, `DP_PIXEL_ENCODING`, `DP_COMPONENT_DEPTH`, `DP_MSA_MISC0`, and MSA timing fields.
- Link training and diagnostics: `DPHY_TRAINING_PATTERN_SEL`, `DPHY_SCRAMBLER_BS_COUNT`, PRBS/scrambler controls, CRC enable/result/MST status fields, fast-training state/ack/mask fields, and HBR2 pattern controls.
- Secondary packet and audio transport: `DP_SEC_STREAM_ENABLE`, `DP_SEC_ASP_ENABLE`, `DP_SEC_GSP[0-7]_ENABLE`, `DP_SEC_GSP*_SEND`, deadline/pending/any-line fields, line-number fields, `DP_SEC_AUD_N/M` and readback fields, timestamp mode, packet coding/version/channel-count override, and collision/audio mute fields.
- MST and DSC: `DP_MSE_RATE_X/Y`, payload slot allocation tables/status, SAT update, link timing, blank-code/timestamp/zero-encoder controls, `DP_DSC_MODE`, `DP_DSC_SLICE_WIDTH`, and PPS/metadata-related GSP fields.
- HDMI/TMDS: HDMI control/status/audio/ACR/VBI/infoframe/generic packet fields, TMDS sync patterns, control character generation, DC balance, lane enables, backend/front-end source routing, and AVMUTE/general-control fields.
- Audio formatter fields: `AFMT_AUDIO_CHANNEL_ENABLE`, layout override/select, HBR and 60958 overrides, audio infoframe channel/count/type/allocation fields, CRC controls/results, FIFO overflow status/ack, and audio source selection.
- Memory and power fields: `VPG_MEM_PWR`, `AFMT_MEM_PWR`, and `DME_MEMORY_CONTROL` fields that describe low-power state controls for packet/audio/metadata helper blocks.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by display-driver consumers:

1. DCN 3.0 resource, IRQ, GPIO, clock, DIO, and DMUB code includes this mask header with the matching offset header.
2. Register-list macros build tables for stream encoders and supporting blocks using symbolic registers such as `DP_SEC_CNTL`, `AFMT_AUDIO_PACKET_CONTROL`, `DME_CONTROL`, and `HDMI_GENERIC_PACKET_CONTROL*`.
3. Field helper macros paste register and field tokens into this header's `SHIFT` and `MASK` constants.
4. Functional code then sequences MMIO reads/writes for modeset, link training, packet setup, audio enablement, metadata transmission, MST payload allocation, DSC setup, CRC/debug capture, suspend/resume, and interrupt handling.

The ordering in the header is still meaningful for generated-header maintenance. Each register normally lists all shift fields followed by masks; repeated instance blocks (`DP3` then `DP4`, `DIG3` then `DIG4`) are expected to remain structurally aligned where the hardware block is replicated.

## State And Persistence Behavior

The file persists no software state. It describes fields in hardware registers whose values persist according to DCN hardware rules until overwritten, reset, power-gated, or cleared by register-specific side effects.

State represented by this chunk includes:

- Stream encoder routing and enable state for DIG3 and DIG4, including FE/BE source selection, backend enable, symbol clock on/status, lane enables, and forced-disable controls.
- HDMI packet and audio state: generic packet line scheduling, immediate/frame update requests, double-buffer pending/taken state, AVMUTE, ACR N/CTS values, metadata packet configuration, and VBI/infoframe/audio controls.
- TMDS physical/link symbol state: control characters, sync patterns, DC balance, test/feedback paths, and static/random pattern generation.
- DP3 and DP4 stream state: active stream enable/status, pixel encoding/depth, MSA fields, video timing, M/N values, link framing, training pattern, scrambler/PRBS/CRC controls, DPHY status, and fast-training completion/ack state.
- DP secondary-packet state: stream/audio packet enablement, GSP scheduling, line references, collision status/ack, audio mute/status, audio M/N values, timestamp mode, and packet coding/version fields.
- MST state: MSE rate, payload slot allocation and status, SAT update pending, link frame/line timing, and related encoding controls.
- VPG4, AFMT4, and DME4 local RAM/power/status state for generic packets, ISRC/MPEG data, HDMI/DP audio formatting, audio CRC/test paths, and dynamic metadata packet generation.

Several fields are status, pending, ack, clear, or write-one-to-clear style controls. The macro names expose the bit location but do not encode access semantics. Consumers must know the register model before using a field in read/modify/write paths.

## Dependencies And Integration Points

This chunk depends on generated consistency with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`, which supplies the corresponding `mm...` register offsets and `_BASE_IDX` selectors.
- DCN base-address headers such as `sienna_cichlid_ip_offset.h`, which make offset/base-index pairs addressable.
- AMD display register helpers that expand `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)` into the constants in this file.

Direct include sites in this tree include `display/dc/resource/dcn30/dcn30_resource.c`, `display/dc/irq/dcn30/irq_service_dcn30.c`, `display/dc/irq/dcn302/irq_service_dcn302.c`, `display/dc/gpio/dcn30/hw_factory_dcn30.c`, `display/dc/gpio/dcn30/hw_translate_dcn30.c`, `display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`, `display/dmub/src/dmub_dcn30.c`, and `display/dmub/src/dmub_dcn302.c`.

The most relevant functional integration is the DIO stream-encoder stack. `display/dc/dio/dcn10/dcn10_stream_encoder.h` defines register and field lists for AFMT audio controls, DP secondary-packet controls, DP audio N/M, metadata controls, and HDMI packet controls. Newer stream encoder implementations program the same conceptual registers with `REG_UPDATE`, `REG_SET`, and `REG_GET` for MSA timing, DP packet enablement, metadata packets, HDMI metadata, and audio enablement. This chunk supplies the instance-specific DCN 3.0 bit positions for those shared register-list abstractions.

## Risks And Edge Cases

- A wrong shift or mask can compile cleanly while corrupting a hardware field at runtime. This is especially risky for enable, ack, clear, and power fields.
- Chunk boundaries are artificial. The range starts after the beginning of `DIG3_HDMI_GENERIC_PACKET_CONTROL10` and ends before the fields for `DP4_DP_MSA_TIMING_PARAM4`; adjacent chunk research is required before making complete file-level claims.
- Repeated instance copy errors can be localized. `DP3` and `DP4`, and `DIG3` and `DIG4`, are similar but not safe to assume interchangeable; a single mismatched field can affect only one connector/encoder instance.
- Double-buffer and pending/taken fields are sequencing-sensitive. Misusing `*_TAKEN_CLR`, `*_DB_DISABLE`, or pending masks can cause stale HDMI/DP infoframes, metadata updates at the wrong vblank, or lost packet updates.
- DP secondary packet and GSP fields are dense and side-effect-prone. Incorrect `SEND`, `PENDING`, `DEADLINE_MISSED`, line-number, PPS, or any-line fields can break audio packets, HDR metadata, DSC PPS delivery, or MST secondary-data scheduling.
- DisplayPort link training and DPHY fields affect physical link stability. Errors in training pattern, scrambler, CRC, HBR2, or fast-training bits may present only at particular link rates, lane counts, panels, or resume paths.
- MSA timing, pixel format, and video M/N fields directly describe the stream sent to the sink. Wrong fields can cause blank displays, bad color/depth negotiation, timing mismatch, flicker, or audio/video synchronization failures.
- Audio formatter fields can fail silently as audio dropouts, incorrect channel mapping, wrong IEC 60958 status, HBR mode issues, FIFO overflow handling problems, or invalid HDMI/DP audio infoframes.
- Memory-power fields for VPG/AFMT/DME can interact with clock gating and block reset. Programming packet or metadata RAM while the block is in low-power state can lose updates or produce transient status conflicts.

## Test Signals

Useful validation signals are mostly build-time macro coverage plus hardware display behavior:

- Build AMDGPU/DC with DCN 3.0 and DCN 3.0.2 support enabled. Missing or renamed macros should fail where stream-encoder, IRQ, GPIO, clock, resource, or DMUB tables are generated.
- Mechanically compare this slice against the matching generated register database and `dcn_3_0_0_offset.h` to ensure every field mask/shift belongs to a register with a valid offset and that shift/mask pairs remain aligned.
- Exercise display outputs that map to DIG/DP instances 3 and 4: hotplug, modeset, DP link training, HDMI/TMDS modes, lane enable/disable, suspend/resume, and forced link-rate/lane-count combinations.
- Validate DP stream setup with RGB/YCbCr formats, different component depths, MSA timing programming, video M/N values, stream enable/disable deferral, and keepout behavior.
- Test DP secondary packet paths: audio playback, audio M/N readback, ASP/ATP/AIP/ACM packet enablement, GSP scheduling, generic packet send/pending/deadline flags, HDR/metadata packets, and DSC PPS delivery where supported.
- Exercise MST payload programming and status readback for MSE rate, SAT slot allocation, SAT update pending, and link timing fields.
- Run HDMI audio/infoframe paths on DIG3/DIG4: ACR N/CTS values, generic packet frame/immediate updates, double-buffer pending/taken/clear behavior, AVMUTE, VBI packet controls, and metadata packet delivery.
- Use CRC/debug features where available: DIG output CRC, DP DPHY CRC, audio CRC, TMDS test patterns, random/static test patterns, and FIFO/status readbacks.
- Watch kernel logs, display diagnostics, and sink behavior for link-training failures, AUX/DP timeouts, blanking, bad color format, audio FIFO overflow, missing HDR/DSC metadata, packet update conflicts, stuck pending bits, and resume-only regressions.

## Cross-Chunk Notes

This is a constants-only chunk. The final per-file report should merge it with neighboring chunks before drawing complete conclusions about the whole `dcn_3_0_0_sh_mask.h` file. In particular, the previous chunk owns the beginning of DIG3 HDMI generic packet control definitions, and the next chunk owns `DP4_DP_MSA_TIMING_PARAM4`, DP4 MSO, and the remaining DP4/next-block field definitions.

### subset-b-001706: lines 46813-49204

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 46813-49204

## Scope

This chunk covers lines 46813-49204 of the generated DCN 3.0.0 register shift/mask header. It contains 2,174 `#define` entries and register/address-block comments only; there are no C functions, structs, enums, variables, or executable branches in this slice. The exported interface is the generated macro namespace of `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` constants consumed by AMD display register helpers.

The range starts in the tail of the `DP4` DisplayPort encoder block, then covers the complete `DIG5` instance sideband/video-packet/audio-format/metadata/digital-encoder blocks, most of the `DP5` DisplayPort block, shared DCIO/UNIPHY/pinstrap controls, and the start of LVTMA panel power sequencing. The last line is only the `//LVTMA_PWRSEQ_REF_DIV` heading; that register's field definitions continue in the following chunk.

## Purpose

The purpose of this chunk is to describe the bit layout for one late digital output instance and shared display I/O registers on DCN 3.0 hardware. Driver code includes this header with the matching offset header and turns the generated constants into per-block register tables and field metadata. That keeps the functional display code from hard-coding raw bit positions for DisplayPort stream setup, HDMI/TMDS packet programming, audio metadata, generic packet scheduling, physical link routing, pinstrap reads, and panel power sequencing.

Major hardware areas covered here are:

- `DP4` MSO, DSC, secondary-data, generic-stream-packet, double-buffer, MSA/VBID, metadata-transmission, DSC bytes-per-pixel, and ALPM field definitions.
- `VPG5` generic-packet, frame-update, immediate-update, ISRC, MPEG infoframe, status, and memory-power fields.
- `AFMT5` HDMI/DP audio packet, audio infoframe, IEC 60958 channel-status, audio CRC, ramp-test, status, source-select, and memory-power fields.
- `DME5` metadata engine enable, HUBP requestor selection, stream type, double-buffer state, and memory-power fields.
- `DIG5` front-end/backend digital encoder fields for source routing, CRC/test patterns, FIFO status, HDMI metadata and generic packets, audio clock recovery, TMDS control characters, lane enablement, and force-disable controls.
- `DP5` link, pixel-format, MSA, stream, main-link DPHY, MST, secondary-data, MSO, DSC, packet, ALPM, and generic-packet fields.
- Shared `DCIO` fields for generic clock outputs, DCIO clock gating, reference clock output selection, UNIPHY A-F link/channel crossbar control, write-command delay, hardware pinstraps, and LVTMA power sequencing.

## Important APIs, Types, And Constants

There are no callable APIs in this header chunk. The important API surface is the generated macro shape:

- `REGISTER__FIELD__SHIFT` gives the field bit position.
- `REGISTER__FIELD_MASK` gives the already-shifted field mask.
- Address block comments such as `// addressBlock: dce_dc_dio_dig5_dispdec` partition the macros by hardware instance.
- Register comments such as `//DP5_DP_DPHY_CNTL` and `//LVTMA_PWRSEQ_CNTL` identify the register whose following field constants are being defined.

Important macro groups include:

- `DP4_DP_MSO_CNTL`, `DP4_DP_MSO_CNTL1`, `DP4_DP_DSC_CNTL`, `DP4_DP_SEC_CNTL2` through `DP4_DP_SEC_CNTL7`, `DP4_DP_GSP8_CNTL` through `DP4_DP_GSP11_CNTL`, and `DP4_DP_GSP_EN_DB_STATUS`, which describe multi-stream operation, DSC slice width/mode, secondary-data send/pending/deadline status, per-packet line numbers, and double-buffer pending state for DisplayPort instance 4.
- `VPG5_VPG_GENERIC_PACKET_ACCESS_CTRL`, `VPG5_VPG_GENERIC_PACKET_DATA`, `VPG5_VPG_GSP_FRAME_UPDATE_CTRL`, and `VPG5_VPG_GSP_IMMEDIATE_UPDATE_CTRL`, which expose indexed packet payload bytes plus update/pending bits for generic packet slots 0-14.
- `AFMT5_AFMT_AUDIO_PACKET_CONTROL2`, `AFMT5_AFMT_AUDIO_INFO0`, `AFMT5_AFMT_AUDIO_INFO1`, `AFMT5_AFMT_60958_0` through `AFMT5_AFMT_60958_2`, and `AFMT5_AFMT_AUDIO_PACKET_CONTROL`, which define audio layout/channel/HBR controls, audio infoframe contents, IEC 60958 channel status, ACK bits, channel swap, and audio test fields.
- `DME5_DME_CONTROL` and `DME5_DME_MEMORY_CONTROL`, which define the metadata engine enable path, requestor ID, stream type, double-buffer pending/taken/clear bits, memory power force/disable/state, and default low-power state.
- `DIG5_DIG_FE_CNTL`, `DIG5_DIG_BE_CNTL`, `DIG5_DIG_BE_EN_CNTL`, `DIG5_DIG_LANE_ENABLE`, and `DIG5_FORCE_DIG_DISABLE`, which describe digital front-end source selection, stereo sync, start/bypass/pixel selection, Dolby Vision flags, backend source/mode/HPD selection, lane enables, and the force-disable bit.
- `DIG5_HDMI_*` and `DIG5_TMDS_*` registers, which cover HDMI metadata packets, scrambling/deep color/error ACK, ACR send/source/N/CTS programming, generic packet controls 0-10, AVMUTE/general-control state, HDMI double buffering, TMDS sync/control-character generation, DC balancing, and ACR status readback.
- `DP5_DP_LINK_CNTL`, `DP5_DP_PIXEL_FORMAT`, `DP5_DP_VID_STREAM_CNTL`, `DP5_DP_STEER_FIFO`, `DP5_DP_VID_TIMING`, `DP5_DP_DPHY_*`, `DP5_DP_SEC_*`, `DP5_DP_MSE_*`, `DP5_DP_MSA_TIMING_PARAM*`, `DP5_DP_MSO_*`, `DP5_DP_DSC_*`, and `DP5_DP_ALPM_CNTL`, which mirror the DisplayPort link, main-link PHY, secondary-data, MST, MSA, MSO, DSC, and low-power controls for instance 5.
- `DC_GENERICA`, `DC_GENERICB`, `DCIO_CLOCK_CNTL`, and `DC_REF_CLK_CNTL`, which select and gate generic display clock outputs and reference-clock outputs.
- `UNIPHY[A-F]_LINK_CNTL` and `UNIPHY[A-F]_CHANNEL_XBAR_CNTL`, which repeat the same physical-link field layout across six UNIPHY blocks: pixel-valid reset, minimum low duration, per-channel inversion, lane stagger, HPD link-enable mask, channel crossbar source, and link enable.
- `DC_PINSTRAPS`, whose `DC_PINSTRAPS_AUDIO` field is read by DCN resource code to populate resource strap data.
- `LVTMA_PWRSEQ_CNTL` and `LVTMA_PWRSEQ_STATE`, which define panel power sequence enable/target state, DIGON/SYNCEN/BLON override/polarity bits, and readback/done/state fields. `LVTMA_PWRSEQ_REF_DIV` starts at the chunk end and must be reconciled with the next chunk.

## Control Flow

This chunk has no runtime control flow. Its behavior is compile-time macro expansion:

1. DCN 3.0 display code includes generated offset and mask headers.
2. Register-list macros concatenate register and field names to resolve these `SHIFT` and `MASK` definitions.
3. Runtime helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_WAIT`, `FN(...)`, and generated `*_MASK_SH_LIST` tables use the resulting constants when reading or writing MMIO registers.

The order of definitions still matters operationally for maintenance. Each register generally lists all shifts first and masks second, and the repeated instance layout (`DP4` followed by `DIG5`/`DP5`) lets generated diffs catch field drift across otherwise similar encoder blocks. Reordering would usually compile, but it would make generator output review and cross-instance comparison harder.

## State And Persistence Behavior

The header itself stores no software state and persists nothing. It describes hardware state that persists in GPU display registers until overwritten, reset, or power-gated:

- DisplayPort secondary-data and generic-stream-packet registers hold send requests, pending/active status, deadline-missed bits, line numbers, and double-buffer state for HDR metadata, infoframes, PPS packets, and related sideband data.
- VPG and HDMI generic-packet registers store indexed packet payload bytes and update scheduling bits. Incorrect masks can cause stale, partial, or mistimed packets to be sent on a live stream.
- AFMT fields represent audio packet generation state, channel layout, HBR/60958 state, CRC/test behavior, FIFO overflow status, and ACK bits.
- DIG5 fields control encoder source routing, timing/test-pattern output, FIFO status, HDMI/TMDS output behavior, and lane enables. These settings directly affect link bring-up and visible output.
- DP5 DPHY fields configure training patterns, FEC state, 8b/10b behavior, PRBS, scrambling, CRC, fast-training controls, and MST CRC windows.
- UNIPHY fields route logical encoder channels to physical lanes and control link enable/inversion/stagger behavior; bad values can persist as lane mapping or link-training failures.
- LVTMA fields control panel power, backlight enable, DIGON/SYNCEN sequencing, override bits, polarity, and readback state. These interact with panel-control code and with the backlight registers that continue after this chunk.

Several registers mix control, status, ACK, clear, pending, and mask fields in one word. For example `*_DB_TAKEN_CLR`, `*_ERROR_ACK`, `*_FIFO_OVERFLOW_ACK`, and `*_SEND_PENDING` style fields require callers to know whether a bit is read-only status, write-one-to-clear, or a control latch; the generated macro names only encode bit positions.

## Dependencies And Integration Points

This header chunk depends on exact naming compatibility with AMD's generated display register infrastructure and the matching `dcn_3_0_0_offset.h` offsets. The constants are normally integrated through:

- DCN register accessor macros that build field metadata from `FN(register, field)`, `FD_MASK(register, field)`, and `FD_SHIFT(register, field)`.
- Resource construction code that passes per-block register, shift, and mask tables into link encoders, audio objects, VPG objects, AFMT objects, and panel control objects.
- `drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`, which reads `DC_PINSTRAPS__DC_PINSTRAPS_AUDIO` through `generic_reg_get()` and constructs panel control, audio, and VPG objects using generated tables.
- `drivers/gpu/drm/amd/display/dc/dce/dce_panel_cntl.h` and `dce_panel_cntl.c`, which map `LVTMA_PWRSEQ_CNTL`, `LVTMA_PWRSEQ_STATE`, and `LVTMA_PWRSEQ_REF_DIV` fields into panel-control shift/mask structs and use them for panel power/backlight sequencing.
- Link encoder and DIO paths that bind DIG/DP/UNIPHY field masks with offsets for routing a display stream to a physical encoder and link.
- HDMI/DP audio and packet paths that depend on `AFMT5`, `VPG5`, `DIG5_HDMI_*`, and `DP5_DP_SEC_*` definitions for audio infoframes, generic packets, ACR values, metadata packets, and secondary-data scheduling.

The visible `DP5` and `DIG5` names are instance-specific. They are not generic aliases: consumers must select the correct instance table before using these fields, or they risk programming the wrong display encoder.

## Risks And Edge Cases

- A wrong shift or mask silently corrupts MMIO field access. C compilation only proves that the macro exists, not that its numeric value matches the ASIC register database.
- This range covers repeated per-instance blocks. Copy/paste or generator drift between `DP4`, `DP5`, and adjacent DIG instances can leave one encoder instance broken while others work.
- `*_MASK_MASK` names such as `HDMI_ERROR_MASK_MASK`, `DP_STEER_OVERFLOW_MASK_MASK`, and `DP_VID_STREAM_DISABLE_MASK_MASK` are generated from fields named `*_MASK`; they are easy to misread during manual review.
- ACK/clear fields share registers with status fields. Read-modify-write sequences that preserve stale status bits can accidentally acknowledge errors or double-buffer state.
- Packet update bits and pending bits are timing-sensitive. Bad masks in VPG, HDMI generic packet, DP secondary-data, or DME double-buffer fields can cause metadata changes to miss a frame boundary or occur immediately when a vertical-update path expected deferral.
- `LVTMA_PWRSEQ_REF_DIV` begins at the final line without its field definitions. Any final file report must merge this chunk with the next one before making complete claims about panel PWM/reference-divider fields.
- UNIPHY crossbar and lane inversion fields affect physical routing. Incorrect values can manifest as DP/HDMI link training failures, lane swaps, blank displays, or intermittent errors rather than obvious software faults.
- Several masks use high bits or broad fields, including `0x80000000L`, `0xFFFF0000L`, and `0xFF000000L`. Callers must preserve unsigned 32-bit semantics when composing values.
- Cross-ASIC reuse is risky because adjacent DCN families share many names while adding, dropping, or moving fields.

## Test Signals

Useful validation signals for this chunk are mostly build-time, generated-header diff, and hardware-integration oriented:

- Build DCN 3.0 display code with consumers that include `dcn_3_0_0_sh_mask.h`, especially resource, link encoder, audio, VPG, AFMT, and panel-control paths.
- Preprocessor or compile-time checks that `FN`, `FD_MASK`, `FD_SHIFT`, and generated `*_MASK_SH_LIST` expansions resolve all `DP5`, `DIG5`, `VPG5`, `AFMT5`, `DME5`, `DC_PINSTRAPS`, and `LVTMA` fields used by DCN 3.0 tables.
- Generated-header comparison against the authoritative AMD register database and against adjacent DCN families where the same register instance is expected to remain layout-compatible.
- Display bring-up tests on outputs mapped to DIG/DP instance 5, including hotplug, modeset, stream enable/disable, link training, MST, DSC, FEC, and ALPM transitions.
- HDMI validation for scrambling, deep color, ACR N/CTS programming, audio packet send, infoframe updates, generic packet scheduling, AVMUTE/general-control behavior, and TMDS test/control-character paths.
- DP metadata validation for secondary-data packets, PPS packets, HDR or other metadata line scheduling, GSP pending/active/deadline status, and double-buffer update timing.
- Panel-control tests for LVTMA power sequencing, DIGON/SYNCEN/BLON overrides, backlight enable/restore, suspend/resume, and eDP panel power state readback.
- PHY/routing tests for UNIPHY A-F channel crossbar selection, lane inversion, link enable, HPD-mask behavior, and clock/ref output selection.

## Open Cross-Chunk Questions

- The next chunk must provide the `LVTMA_PWRSEQ_REF_DIV` fields and subsequent backlight PWM fields before the final per-file report can fully describe panel-control coverage.
- Whole-file reconciliation should compare this mask header with `dcn_3_0_0_offset.h` to ensure every register represented here has the expected offset and base-index entry.
- If generator provenance exists elsewhere in the repository, the final report should identify it, because manual edits to this generated header are high risk.

### subset-b-001707: lines 49205-51607

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 49205-51607

## Scope

This chunk covers lines 49,205 through 51,607 of the generated DCN 3.0.0 register shift/mask header. It contains 2,165 `#define` entries and address-block comments for display-core hardware registers. There are no C functions, structs, enums, or executable statements in this slice; the exported interface is a macro namespace consumed by AMD display register helper code.

The range starts inside the LVTMA power-sequencer/backlight area with `LVTMA_PWRSEQ_REF_DIV` field macros, continues through DCIO GPIO/DDC/AUX pad controls, and then covers DSC compressor instances 0, 1, and the beginning of instance 2. The range is chunk-local and stops in the middle of `DSCC2_DSCC_PPS_CONFIG15`; line 51608, just outside this work item, contains the missing `DSCC2_DSCC_PPS_CONFIG15__RANGE_BPG_OFFSET0_MASK` pair for the included `RANGE_BPG_OFFSET0__SHIFT`.

## Purpose

The purpose of this header slice is to encode bit positions and masks for DCN 3.0 display hardware registers so driver code can compose and extract MMIO fields without hard-coded numeric literals. The matching offset header supplies register addresses, while this file supplies `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` constants used by helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_SHIFT`, `FD_MASK`, `DCE_PANEL_CNTL_SF`, `SF_DDC`, and `DSC_SF`.

This chunk covers these main hardware areas:

- LVTMA panel power sequencing and backlight PWM timing: reference dividers, power-up/power-down delays, PWM duty, PWM period, frame-start update delay, and the PWM group lock/update-pending register.
- Genlock and swaplock GPIO pad routing plus DCIO soft reset for UNIPHY/DSYNC lanes, DCRXPHY, and ZCAL.
- DCIO GPIO block for generic GPIOs, DDC pins 1-6, DDC VGA, genlock/swaplock pins, HPD pins, panel power sequence pins, pad drive strength, AUX controls, RX enable, pull-up enable, and AUX/I2C pad power-good status.
- DSC top, DSCCIF, DSCC, and DSC-local perfmon register fields for DSC instances 0 and 1, plus the start of DSC instance 2.
- DSC picture parameter set programming fields covering DSC version, picture size, slice geometry, bits per pixel/component, native 4:2:2/4:2:0 flags, rate-control model parameters, thresholds, and the first QP range entry.

## Important APIs, Types, And Functions

This chunk defines macros only. The important exported patterns are:

- `REGISTER__FIELD__SHIFT`: the low bit index for a field.
- `REGISTER__FIELD_MASK`: the bit mask for the field in the 32-bit register word.
- Register comments such as `//BL_PWM_CNTL`, `//DC_GPIO_DDC1_MASK`, and `//DSCC0_DSCC_PPS_CONFIG0`, which group shift/mask pairs by hardware register.
- Address-block comments such as `dce_dc_dcio_dcio_chip_dispdec`, `dce_dc_dsc0_dispdec_dscc_dispdec`, and `dce_dc_dsc1_dispdec_dsc_dcperfmon_dc_perfmon_dispdec`, which identify the IP block whose generated fields follow.

Important macro groups in the chunk:

- LVTMA/backlight: `LVTMA_PWRSEQ_REF_DIV`, `LVTMA_PWRSEQ_DELAY1`, `LVTMA_PWRSEQ_DELAY2`, `BL_PWM_CNTL`, `BL_PWM_CNTL2`, `BL_PWM_PERIOD_CNTL`, and `BL_PWM_GRP1_REG_LOCK`.
- DCIO synchronization/reset: `DCIO_GSL_GENLK_PAD_CNTL`, `DCIO_GSL_SWAPLOCK_PAD_CNTL`, and `DCIO_SOFT_RESET`.
- Generic GPIO: `DC_GPIO_GENERIC_MASK`, `DC_GPIO_GENERIC_A`, `DC_GPIO_GENERIC_EN`, and `DC_GPIO_GENERIC_Y` for generic pins A-G.
- DDC/AUX pin groups: `DC_GPIO_DDC[1-6]_MASK`, `DC_GPIO_DDC[1-6]_A`, `DC_GPIO_DDC[1-6]_EN`, `DC_GPIO_DDC[1-6]_Y`, equivalent `DDCVGA` registers, `PHY_AUX_CNTL`, `DC_GPIO_TX12_EN`, `DC_GPIO_AUX_CTRL_0` through `DC_GPIO_AUX_CTRL_5`, and `AUXI2C_PAD_ALL_PWR_OK`.
- Hotplug/power-sequence GPIO: `DC_GPIO_HPD_MASK`, `DC_GPIO_HPD_A`, `DC_GPIO_HPD_EN`, `DC_GPIO_HPD_Y`, `DC_GPIO_PWRSEQ_MASK`, `DC_GPIO_PWRSEQ_A`, `DC_GPIO_PWRSEQ_EN`, and `DC_GPIO_PWRSEQ_Y`.
- DSC top/control path: `DSC_TOP[0-2]_DSC_TOP_CONTROL`, `DSC_TOP[0-2]_DSC_DEBUG_CONTROL`, `DSCCIF[0-2]_DSCCIF_CONFIG0`, `DSCCIF[0-2]_DSCCIF_CONFIG1`, `DSCC[0-2]_DSCC_CONFIG0`, `DSCC[0-2]_DSCC_CONFIG1`, and `DSCC[0-2]_DSCC_STATUS`.
- DSC interrupts and PPS fields: `DSCC[0-2]_DSCC_INTERRUPT_CONTROL_STATUS` and `DSCC[0-2]_DSCC_PPS_CONFIG0` through at least `PPS_CONFIG15` for the instances present in this range.
- DSC diagnostics/perfmon: `DSCC0` and `DSCC1` memory power, squared-error counters, max-absolute-error counters, rate-buffer fullness counters, debug bus rotation, and `DC_PERFMON21_*` / `DC_PERFMON22_*` perf counter fields.

## Control Flow

There is no runtime control flow in this chunk. Its behavior is compile-time macro expansion:

1. A DCN 3.0 display translation unit includes this header, usually with the matching offset header.
2. Hardware-specific register tables expand field names through helper macros, for example `DSC_SF(DSCC0_DSCC_PPS_CONFIG1, BITS_PER_PIXEL, mask_sh)` or `SF_DDC(DC_GPIO_DDC1_MASK, AUX_PAD1_MODE, mask_sh)`.
3. Runtime driver code reads or writes MMIO registers through generated tables and helpers. The helpers combine register offsets with the shift/mask constants from this file.

The ordering is meaningful for generated-header review and reconciliation. Registers are grouped by address block and each register normally lists all shift macros first, followed by corresponding masks. The final included register is split by the chunk boundary, so whole-file analysis must not treat `DSCC2_DSCC_PPS_CONFIG15` as complete from this chunk alone.

## State And Persistence Behavior

The header itself stores no software state and persists no data. It describes hardware state in DCN display registers:

- LVTMA and backlight PWM fields affect panel sequencing state, backlight duty/period, update timing, and lock behavior. Values written there persist in hardware until the driver changes them or the display block resets.
- DCIO soft-reset bits can reset specific UNIPHY, DSYNC, DCRXPHY, and ZCAL blocks. Misprogramming these fields can disrupt live display links.
- GPIO `MASK`, `A`, `EN`, and `Y` groups describe the common pin model: mask/control, output data, output enable, and readback for DDC, HPD, genlock/swaplock, and panel power pins.
- DDC/AUX control fields choose AUX-vs-DDC pad modes, polarity, pull-down/pull-up behavior, drive strength, termination, hysteresis, voltage swing, I2C mode, and pad power controls.
- DSC top and DSCC fields persist compression-engine setup across a programmed stream: clock enable/gating behavior, input format, picture size, slice layout, PPS values, rate control model, and interrupt enable/status fields.
- DSC status, error, fullness, and perfmon fields expose hardware-observed state. Some are readback counters or latched statuses rather than ordinary writable configuration fields.

The macro names do not encode all access semantics. A mask may target a read-only status field, a write-one-to-clear status bit, a writeable configuration field, or a counter readback field. Callers must rely on the register programming model and local helper usage, not just the macro suffix.

## Dependencies And Integration Points

This generated header depends on name and numeric consistency with adjacent AMD register headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h` supplies the corresponding register offsets.
- Other DCN 3.x `*_sh_mask.h` headers define similar namespaces for related ASIC versions; reusing fields across versions requires care because field layouts drift.
- Enumeration headers such as `navi10_enum.h` document some field value meanings for DCIO/LVTMA/backlight controls, while this file supplies only raw bit geometry.

Important in-tree integration points found from nearby consumers include:

- `drivers/gpu/drm/amd/display/dc/dce/dce_panel_cntl.[ch]` and `dc/dcn301/dcn301_panel_cntl.[ch]` use `BL_PWM_GRP1_REG_LOCK` fields to lock/unlock PWM register updates and wait for update completion.
- `drivers/gpu/drm/amd/display/dc/gpio/ddc_regs.h` uses `DC_GPIO_DDC1_MASK` fields such as `DC_GPIO_DDC1DATA_PD_EN`, `DC_GPIO_DDC1CLK_PD_EN`, and `AUX_PAD1_MODE` through the DDC register table macros.
- `drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.h` and newer DSC headers use `DSC_SF` field-table macros for DSCC PPS, DSCCIF, status, memory-power, diagnostic, and perfmon fields. DCN 3.0 carries the same style of generated DSC field namespace.
- IRQ, modeset, AUX/DDC, hotplug, panel power, DSC programming, and perfmon/debug paths consume these constants indirectly through generated register field structures and MMIO helper macros.

The chunk is also part of a generated register contract for hardware bring-up. Direct hand edits are risky unless matched to the source register database and the paired offset definitions.

## Risks And Edge Cases

- A wrong shift or mask silently writes the wrong bits in an MMIO register. This can blank displays, break AUX/DDC transactions, mis-detect hotplug, corrupt DSC PPS programming, or wedge a display link.
- The assigned range begins and ends mid-register context. `LVTMA_PWRSEQ_REF_DIV` starts with its comment outside the range, and `DSCC2_DSCC_PPS_CONFIG15` lacks one mask line inside this chunk. Merge/reconciliation must account for neighboring chunks before judging field completeness.
- Backlight PWM group lock fields are synchronization-sensitive. Incorrect `BL_PWM_GRP1_REG_LOCK`, update-pending, or frame-start selection masks can cause brightness updates to race scanout or fail to latch.
- DDC/AUX pad mode, polarity, termination, and I2C-mode fields are board- and connector-sensitive. Bad definitions can cause EDID read failures, AUX training failures, or inconsistent hotplug behavior.
- GPIO mask fields mix enable, pull-down, receiver, drive-strength, and mode bits in compact layouts. Treating a multi-bit field as a boolean or using the wrong numbered DDC/HPD instance can affect an unrelated connector.
- `DCIO_SOFT_RESET` controls multiple PHY and DSYNC blocks. Using a stale mask from a related ASIC could reset the wrong lane or leave the intended block running.
- DSC PPS fields must match the DSC standard and the sink's negotiated capabilities. Wrong masks for `BITS_PER_PIXEL`, `CHUNK_SIZE`, slice dimensions, rate-control thresholds, or QP ranges can produce visible corruption or link underflow.
- `DSCC*_DSCC_INTERRUPT_CONTROL_STATUS` combines occurred-status and interrupt-enable fields in one generated register group. Confusing status bits with enable bits can leave overflow/underflow events unreported or stuck.
- Perfmon fields include event-selection, counter-state, interrupt, and readback fields. Incorrect masks can make diagnostic counters misleading even if display output appears functional.

## Test Signals

Useful validation signals for this chunk are build-time, macro-expansion, and hardware-integration oriented:

- Compile DCN 3.0/3.x AMD display code that includes `dcn_3_0_0_sh_mask.h`, especially panel control, GPIO/DDC, AUX, DSC, IRQ, and perfmon paths.
- Preprocessor or unit-style checks that representative `FD_MASK`, `FD_SHIFT`, `DCE_PANEL_CNTL_SF`, `SF_DDC`, and `DSC_SF` expansions resolve for fields in this range.
- Panel/backlight tests covering PWM enable, fractional duty programming, period programming, frame-start update latching, brightness changes, and suspend/resume backlight restore.
- GPIO/DDC/AUX tests covering EDID reads over all DDC instances, DisplayPort AUX transactions, HPD plug/unplug events, DDC VGA behavior where applicable, and pad power-good reporting.
- Link bring-up tests that exercise genlock/swaplock pads if the platform uses them, plus PHY reset paths around modeset and hotplug.
- DSC validation on DCN 3.0 hardware with compressed streams: mode validation, PPS programming, slice geometry, 4:2:0/4:2:2/native modes, high bits-per-pixel modes, and visual corruption checks.
- DSC error-path testing that observes DSCC rate-buffer overflow/underflow, rate-control buffer model overflow, and DSCCIF input-interface underflow status/interrupt behavior.
- Perfmon/debug tests that select events in `DC_PERFMON21_*` and `DC_PERFMON22_*`, start/stop counters, read low/high values, and acknowledge counter interrupts.

## Open Cross-Chunk Questions

- The previous chunk should be consulted for the beginning of the LVTMA power-sequencer register group and the `LVTMA_PWRSEQ_REF_DIV` comment context.
- The next chunk must complete `DSCC2_DSCC_PPS_CONFIG15` and continue the rest of DSC instance 2. Whole-file reconciliation should avoid flagging the missing `RANGE_BPG_OFFSET0_MASK` as a source defect when it is only outside this chunk boundary.
- The final per-file report should compare this mask header with `dcn_3_0_0_offset.h` and the active DCN 3.0 display register tables to identify any offset/mask coverage gaps.

### subset-b-001708: lines 51608-54079

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 51608-54079

## Scope

This chunk is a partial slice of the generated DCN 3.0.0 register shift/mask header. It contains only preprocessor constants and address-block/register comments; there are no C functions, structs, enums, or executable statements. The exported contract is the generated `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` namespace consumed by AMD display register helper macros.

The range starts mid-register at the final `DSCC2_DSCC_PPS_CONFIG15__RANGE_BPG_OFFSET0_MASK` definition, continues through the tail of DSC compressor instance 2, covers DSC compressor instances 3 and 4, starts DSC compressor instance 5, covers the first display writeback top/perfmon/control-processing blocks, and ends mid-register at `DWB_OGAM_RAMB_START_BASE_CNTL_G__SHIFT`. The next chunk must supply the matching `DWB_OGAM_RAMB_START_BASE_CNTL_G_MASK` and the rest of the DWB RAMB output-gamma fields.

## Purpose

The purpose of this header chunk is to describe bit layouts for DCN 3.0 display stream compression and display writeback hardware registers. Driver code combines these masks and shifts with register offsets from `dcn_3_0_0_offset.h` so higher-level DSC/DWB code can program MMIO fields through macros such as `REG_SET`, `REG_SET_N`, `REG_UPDATE`, `REG_GET`, `DSC_SF`, `FD_MASK`, and `FD_SHIFT` without hard-coding numeric bit positions.

The main hardware areas visible in this chunk are:

- DSC instance 2 tail fields: remaining PPS range QP/BPG-offset fields, DSCC memory power control, encoder error/statistic readbacks, and rate-buffer fullness readbacks.
- DSC instance 2 perfmon block: `DC_PERFMON23_*` counter configuration, state, interrupt/status/ack, and readback fields.
- Full DSC instances 3 and 4: `DSC_TOP3/4`, `DSCCIF3/4`, `DSCC3/4`, and `DC_PERFMON24/25` field definitions.
- Start of DSC instance 5: `DSC_TOP5`, `DSCCIF5`, `DSCC5`, and `DC_PERFMON26` definitions through the common DSC control, PPS, status, and perfmon patterns.
- Display writeback instance 0: `DWB_ENABLE_CLK_CTRL`, memory power control, frame-composer controls, CRC fields, output control, MMHUBBUB backpressure counters, host-read control, overflow status/counter, soft reset, `DC_PERFMON27`, gamut-remap matrices, HDR multiplier, output-gamma LUT control, RAMA region tables, and the start of RAMB start-control fields.

## Important APIs, Types, And Constants

There are no callable APIs or data types. The important interface is the macro set:

- `DSC_TOPn_DSC_TOP_CONTROL` and `DSC_TOPn_DSC_DEBUG_CONTROL` fields control per-instance DSC clock enable, clock-gating disable bits, and debug enable.
- `DSCCIFn_DSCCIF_CONFIG0/1` fields describe input-interface recovery/underflow status, input pixel format, bits per component, double-buffer update pending state, and picture dimensions.
- `DSCCn_DSCC_CONFIG0/1` fields describe ICH reset behavior, slice counts, alternate ICH encoding, vertical slice count, rate-control buffer model size, and ICH disable.
- `DSCCn_DSCC_INTERRUPT_CONTROL_STATUS` packs rate-buffer overflow/underflow status bits, rate-control model overflow status bits, and the matching interrupt-enable bits.
- `DSCCn_DSCC_PPS_CONFIG0` through `DSCCn_DSCC_PPS_CONFIG22` encode the DSC picture parameter set: DSC version, PPS identifier, line-buffer depth, bits per component, bits per pixel, native/simple 4:2:2 or 4:2:0 flags, chunk size, picture/slice dimensions, initial delays, scale intervals, first/second-line offsets, BPG offsets, RC model size, flatness QP bounds, quantization increment limits, target offsets, rate-control buffer thresholds, and range min/max QP plus range BPG offsets.
- `DSCCn_DSCC_MEM_POWER_CONTROL` controls default low-power state, forced memory power state, memory power disable, current memory power state, and native 4:2:2 memory power fields.
- `DSCCn_DSCC_*_SQUARED_ERROR_*`, `DSCCn_DSCC_MAX_ABS_ERROR*`, `DSCCn_DSCC_RATE_BUFFER*_MAX_FULLNESS_LEVEL`, and `DSCCn_DSCC_RATE_CONTROL_BUFFER*_MAX_FULLNESS_LEVEL` expose diagnostic/statistical readback fields.
- `DC_PERFMON23` through `DC_PERFMON27` repeat the standard perfmon layout: event selection, counted value selection, increment mode, hardware stop selectors, counter state selectors, perfmon state, report count, counter-off interrupt control/status/ack, per-counter interrupt status/ack bits, and low/high counter readback.
- `DWB_*` fields describe writeback clock/memory power, frame-composer mode and window/source geometry, update/CRC/output controls, MMHUBBUB backpressure and overflow reporting, soft reset, HDR multiplier, gamut-remap mode and 3x4 matrix coefficient registers for two matrices, output-gamma mode/LUT access, and RAMA/RAMB piecewise-linear region geometry.

The DSC register families are instance-suffixed in the generated header (`DSCC3_...`, `DSCC4_...`, etc.) but are normally consumed through per-instance register tables. For example, `drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.h` uses `SRI(DSCC_PPS_CONFIG16, DSCC, id)` for offsets and `DSC_SF(DSCC0_DSCC_PPS_CONFIG16, RANGE_MIN_QP1, mask_sh)` style macros for shifts/masks, allowing runtime DSC code to use unsuffixed logical register names such as `DSCC_PPS_CONFIG16`.

## Control Flow

This chunk has no runtime control flow. Its compile-time flow is:

1. DCN 3.0 consumers include `sienna_cichlid_ip_offset.h`, `dcn_3_0_0_offset.h`, and this shift/mask header.
2. Register-list macros concatenate generated register and field names to populate register-address and field-mask tables.
3. Runtime DSC and DWB functions call generic register helpers against those tables.
4. The helpers use the generated shift/mask constants here to preserve unrelated bits while programming individual hardware fields.

The ordering is still important for maintenance because the file is organized by address block and register. Each register generally lists all field shifts first, then masks. Because this is generated hardware metadata, reordering or partial hand edits can make diffs harder to audit and can hide mismatches against the paired offset header.

## State And Persistence Behavior

The header itself stores no software state and persists no data. It defines how driver writes reach persistent hardware register state until the driver overwrites it, the display block resets, or the GPU resets.

Important state described by this chunk includes:

- DSC enablement and clock/debug state in `DSC_TOPn`.
- DSC input-interface underflow recovery, underflow status, pixel format, component depth, picture dimensions, and double-buffer update pending state in `DSCCIFn`.
- DSC encoder configuration and PPS state in `DSCCn`, including slice topology, rate-control model size, PPS programming, RC thresholds, QP ranges, and native 4:2:2/4:2:0 flags.
- Error and fullness counters for DSC quality/debug visibility. Many of these are readback-style 16-, 18-, or 32-bit fields.
- Perfmon event selection, run/stop control, interrupt enable/status/ack, and counter readback state for the DSC and DWB-related performance monitor blocks.
- DWB clock/memory-power, frame-composer geometry, output mode, CRC mask/value, backpressure/overflow counters, color-processing matrices, output-gamma LUT mode/index/data, and output-gamma RAM region geometry.

Some registers contain status and acknowledgement fields in the same word, especially perfmon interrupt/status/ack fields. Consumers must rely on the hardware programming model to distinguish read-only status, write-one-to-clear acknowledgement, and normal control fields; the generated mask names alone do not encode access semantics.

## Dependencies And Integration Points

This chunk depends on strict generated-name compatibility with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`, which supplies the matching register offsets.
- ASIC base-offset headers such as `sienna_cichlid_ip_offset.h`.
- AMD display register helper macros in the DC codebase, including `SRI`, `SR`, `REG_SET`, `REG_SET_N`, `REG_UPDATE`, `REG_GET`, `DSC_SF`, `FD_MASK`, and `FD_SHIFT`.

Observed direct include sites for the whole `dcn_3_0_0_sh_mask.h` header include DCN 3.0 and DCN 3.0.2 DMUB, IRQ, GPIO, resource, and clock-manager code:

- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c`
- `drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c`
- `drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c`
- `drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c`
- `drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c`
- `drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`
- `drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`

The DSC-specific field families integrate with `drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.h` and related DSC implementations. Those files define register lists and field-list macros for programming DSC PPS registers and reading DSC status. The DWB fields integrate with writeback/resource paths that configure display capture/output formatting, color processing, CRC, and output-gamma state.

## Risks And Edge Cases

- This is generated numeric hardware metadata. A wrong mask or shift can compile cleanly while silently programming the wrong MMIO bits.
- The range starts and ends in the middle of registers. Whole-file merge must reconcile `DSCC2_DSCC_PPS_CONFIG15` with the previous chunk and `DWB_OGAM_RAMB_START_BASE_CNTL_G` with the next chunk before drawing final completeness conclusions.
- DSC instances 3, 4, and 5 repeat nearly identical layouts. Copy/generator drift in only one instance can create instance-specific failures that normal compile tests will not catch.
- Offset/header mismatch is high risk: the logical DSC register tables combine offsets from `dcn_3_0_0_offset.h` with masks from this file. If either side gains, loses, or renames an instance register independently, field accesses can target the wrong address or fail to compile.
- Several fields use full-register masks such as `0xFFFFFFFFL` for counter/error readbacks. Callers must preserve unsigned width expectations and avoid sign-extension assumptions.
- Perfmon status/ack fields are adjacent to control bits. Read/modify/write code that writes back stale status or ack bits can inadvertently clear interrupts or change counter behavior.
- DSC PPS fields directly affect compressed stream syntax and rate-control behavior. Bad values can produce link failures, corrupted compressed output, underflow/overflow interrupts, or display blanking.
- DWB output-gamma and gamut-remap fields are stateful color-processing controls. Incorrect masks can cause visible color errors in writeback/capture paths without necessarily breaking modeset.
- Memory-power and clock-enable fields can cause hangs or lost state if consumers disable memory or clocks while a block is active.

## Test Signals

Useful validation for this chunk is mostly compile-time plus DCN hardware integration:

- Build DCN 3.0/3.0.2 display paths that include `dcn_3_0_0_sh_mask.h`, with attention to DSC, DWB, DMUB, IRQ, GPIO, resource, and clock-manager translation units.
- Compile-check representative `DSC_SF`, `FD_MASK`, `FD_SHIFT`, `REG_SET_N`, `REG_UPDATE`, and `REG_GET` expansions for `DSCC_PPS_CONFIG0-22`, `DSCCIF_CONFIG0/1`, `DSC_TOP_CONTROL`, and DWB color/output registers.
- Exercise DSC enable/disable, PPS programming, multiple slice layouts, native 4:2:2/4:2:0 flags, bits-per-pixel/component settings, and DSC underrun/overflow interrupt paths on DCN 3.0 hardware.
- Read DSC diagnostic counters and max/squared error registers after DSC traffic to confirm masks select the expected low/high fields.
- Program and read back `DC_PERFMON23` through `DC_PERFMON27` counters, including interrupt status and ack behavior.
- Exercise DWB capture/writeback with frame-composer windows, CRC enable/masks, MMHUBBUB backpressure counters, overflow handling, gamut remap, HDR multiplier, and OGAM LUT/RAMA/RAMB programming.
- Compare generated masks in this range against the paired DCN 3.0.0 offset header and adjacent DCN family headers where the DSC/DWB layouts are expected to remain stable.

## Open Cross-Chunk Questions

- The previous chunk should confirm the first four fields and masks of `DSCC2_DSCC_PPS_CONFIG15`; this chunk only contains its final mask.
- The next chunk should confirm the missing mask for `DWB_OGAM_RAMB_START_BASE_CNTL_G` and the remaining RAMB/OGAM region table definitions.
- Whole-file reconciliation should verify that every `DSC_TOPn`, `DSCCIFn`, `DSCCn`, `DC_PERFMON2x`, and DWB register offset has matching field definitions and that instance numbering stays aligned across offset and mask headers.

### subset-b-001709: lines 54080-56610

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 54080-56610

## Scope

This chunk covers lines 54080-56610 of the generated DCN 3.0.0 shift/mask header. It is a register-field definition slice only: there are no C functions, structs, enums, or runtime branches here. The exported surface is a large set of preprocessor constants named as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`, consumed by AMD display register helper macros and paired with register offsets from `dcn_3_0_0_offset.h`.

The slice begins in the middle of the Display Writeback output-gamma RAM B block, covers the MPCC0 through MPCC5 composition/blending register field layouts, then covers MPCC output-gamma and gamut-remap blocks for MPCC_OGAM0, MPCC_OGAM1, MPCC_OGAM2, and the beginning of MPCC_OGAM3. It ends inside `MPCC_OGAM3_MPCC_OGAM_RAMA_REGION_28_29`, so MPCC_OGAM3 RAMA continuation and RAMB/gamut-remap fields belong to a later chunk.

## Purpose

The purpose of this chunk is to describe bit positions and masks for DCN 3.0 display composition, output-gamma, and color-remap hardware:

- `DWB_OGAM_RAMB_*` defines the tail of the Display Writeback output-gamma RAM B transfer-function region descriptors: per-channel start/end values, slopes, offsets, and 34 piecewise-linear region descriptors.
- `MPCC0_MPCC_*` through `MPCC5_MPCC_*` define six Multi-Plane Composition Controller instances. These fields select the top DPP input, bottom MPCC link, OPP target, alpha/blend mode, stereo/alternate-frame behavior, per-plane gains, background color, OGAM memory power, and MPCC status.
- `MPCC_OGAM0_*`, `MPCC_OGAM1_*`, and `MPCC_OGAM2_*` provide full per-MPCC output-gamma control, LUT host access, RAM A/RAM B transfer-function descriptors, and gamut-remap matrix storage.
- `MPCC_OGAM3_*` starts the same per-MPCC OGAM pattern, but this chunk only includes control/LUT access and RAM A through region pair 28/29.

The chunk lets driver code avoid hard-coded bit arithmetic while programming blending chains, double-buffered output gamma, writeback gamma, memory power, and 3x4 gamut-remap matrices.

## Important APIs, Types, And Constants

There are no callable APIs in this slice. The important interface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT`: the field's least-significant bit position.
- `REGISTER__FIELD_MASK`: the field mask already shifted into register position.
- Section comments such as `//MPCC0_MPCC_CONTROL` and `//MPCC_OGAM0_MPCC_OGAM_RAMA_REGION_0_1` group related fields.
- Address-block comments such as `// addressBlock: dce_dc_mpc_mpcc0_dispdec` identify the hardware instance block.

Important field groups include:

- DWB OGAM RAM B: `DWB_OGAM_RAMB_START_*`, `DWB_OGAM_RAMB_END_*`, `DWB_OGAM_RAMB_OFFSET_*`, and `DWB_OGAM_RAMB_REGION_0_1` through `DWB_OGAM_RAMB_REGION_32_33`. These mirror the RAM A region model from the preceding chunk and describe blue/green/red channel PWL start, end, slope, base, offset, LUT-offset, and segment-count values.
- MPCC topology: `MPCC*_MPCC_TOP_SEL`, `MPCC*_MPCC_BOT_SEL`, and `MPCC*_MPCC_OPP_ID` use 4-bit selectors for input DPP, lower MPCC in the composition chain, and output pixel processor target.
- MPCC blending: `MPCC*_MPCC_CONTROL` includes `MPCC_MODE`, `MPCC_ALPHA_BLND_MODE`, `MPCC_ALPHA_MULTIPLIED_MODE`, `MPCC_BLND_ACTIVE_OVERLAP_ONLY`, `MPCC_BG_BPC`, `MPCC_BOT_GAIN_MODE`, `MPCC_GLOBAL_ALPHA`, and `MPCC_GLOBAL_GAIN`.
- MPCC stereo/multiview: `MPCC*_MPCC_SM_CONTROL` exposes enable, mode, frame/field alternation, forced next-frame polarity, forced top polarity, and current-frame polarity fields.
- MPCC programming synchronization: `MPCC*_MPCC_UPDATE_LOCK_SEL` selects update-lock routing and reports locked status.
- MPCC gain/background/status: `MPCC*_MPCC_TOP_GAIN`, `MPCC*_MPCC_BOT_GAIN_INSIDE`, `MPCC*_MPCC_BOT_GAIN_OUTSIDE`, `MPCC*_MPCC_BG_R_CR`, `MPCC*_MPCC_BG_G_Y`, `MPCC*_MPCC_BG_B_CB`, `MPCC*_MPCC_MEM_PWR_CTRL`, and `MPCC*_MPCC_STATUS`.
- MPCC OGAM control and LUT access: `MPCC_OGAM*_MPCC_OGAM_CONTROL`, `MPCC_OGAM*_MPCC_OGAM_LUT_INDEX`, `MPCC_OGAM*_MPCC_OGAM_LUT_DATA`, and `MPCC_OGAM*_MPCC_OGAM_LUT_CONTROL` define mode/select state, current mode/select readback, PWL disable, 9-bit LUT index, 18-bit LUT data, color write mask, read color select, host RAM select, debug read, and config mode.
- MPCC OGAM RAM A/RAM B PWL descriptors: `MPCC_OGAM*_MPCC_OGAM_RAMA_*` and `MPCC_OGAM*_MPCC_OGAM_RAMB_*` use repeated field layouts. Start values and start bases are 18-bit masks (`0x0003FFFFL`), start segments are 7-bit fields at bit 20 (`0x07F00000L`), offsets are 19-bit masks (`0x0007FFFFL`), end values are low 16 bits, end slopes are high 16 bits, LUT offsets are 9-bit fields, and region segment counts are 3-bit fields.
- MPCC gamut remap: `MPCC_OGAM*_MPCC_GAMUT_REMAP_COEF_FORMAT`, `MPCC_OGAM*_MPCC_GAMUT_REMAP_MODE`, and `MPCC_OGAM*_MPC_GAMUT_REMAP_Cxx_Cyy_[AB]` define coefficient format, active/current coefficient set, and packed 16-bit matrix coefficient pairs for A/B banks.

## Control Flow

This header chunk has no runtime control flow. Its practical compile-time flow is:

1. DCN 3.0 display source includes register offset and shift/mask headers.
2. Register-list macros in MPCC/DWB code expand generated register names into address tables.
3. Field-list macros expand these `SHIFT` and `MASK` constants into per-block `shift` and `mask` structs.
4. Runtime code uses `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and `REG_READ` against those tables to program MMIO registers.

The register order is still meaningful for maintainers and generated-header validation. MPCC0-5 are laid out as identical repeated address blocks, followed by MPCC_OGAM0-3 repeated color blocks. The chunk boundary cuts through generated sequences: it starts after the first two DWB RAMB start-control fields and ends before the MPCC_OGAM3 RAMA/RAMB/gamut-remap block is complete.

## State And Persistence Behavior

The header stores no software state and persists no data by itself. It describes hardware state that persists in DCN registers until overwritten by the driver, reset, or power-gated:

- MPCC topology fields persist composition routing: which DPP feeds the top layer, which MPCC is chained below, and which OPP receives the composited output.
- MPCC blend fields persist plane-composition behavior, including alpha mode, premultiplied alpha interpretation, overlap-only blending, background bit depth, global alpha, and gain factors.
- `MPCC*_MPCC_STATUS` exposes hardware idle/busy/disabled state used by driver wait and state-capture paths.
- `MPCC*_MPCC_MEM_PWR_CTRL` controls OGAM LUT memory force/power-disable/low-power behavior and reports power state. Incorrect settings can block LUT writes or prevent low-power entry.
- MPCC OGAM control fields persist the active output gamma mode and selected RAM bank. Current-mode/current-select fields are readback/status fields used to choose the next bank for double-buffered updates.
- MPCC and DWB OGAM RAM descriptors persist the piecewise transfer-function layout for RAM A/RAM B. These include region starts, bases, slopes, offsets, LUT offsets, and segment counts for each color channel.
- Gamut-remap coefficient registers persist A and B matrix coefficient banks. The mode register selects which bank is active and exposes the current active bank.

Because many field names are repeated across MPCC instances and across RAM A/RAM B, the instance index and register bank are part of the state contract. A correct mask on the wrong instance or wrong bank still programs valid hardware bits, but with incorrect display behavior.

## Dependencies And Integration Points

This generated mask header depends on matching generated offsets from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h` and on AMD display register helper macros that concatenate register/field names.

Observed integration points in this repository include:

- `drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.h` builds DCN 3.0 MPC register and field tables from these macros. `MPC_REG_LIST_DCN3_0()` includes MPCC gain, memory-power, OGAM LUT, OGAM RAMA/RAMB, gamut-remap, and OGAM control registers. The associated mask/shift lists use fields such as `MPCC_OGAM_RAMA_EXP_REGION_START_BASE_B`, `MPCC_OGAM_RAMB_EXP_REGION_END_SLOPE_B`, `MPCC_GAMUT_REMAP_C11_A`, and `MPCC_OGAM_MEM_PWR_STATE`.
- `drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.c` consumes these fields in `mpc3_power_on_ogam_lut()`, `mpc3_configure_ogam_lut()`, `mpc3_program_luta()`, `mpc3_program_lutb()`, `mpc3_program_ogam_pwl()`, `mpc3_set_output_gamma()`, `program_gamut_remap()`, `mpc3_set_gamut_remap()`, `mpc3_get_gamut_remap()`, `mpc3_read_mpcc_state()`, and `mpc3_read_reg_state()`.
- Legacy/common MPC code in `dcn10_mpc.c` and `dcn20_mpc.c` consumes the shared MPCC field names for background color, blending, stereo mode, status waits, gains, and memory power. DCN 3.0 extends those tables with OGAM/gamut-remap fields.
- `drivers/gpu/drm/amd/display/dc/dwb/dcn30/dcn30_dwb.h` consumes the DWB OGAM RAMB field macros in `DWBC_COMMON_REG_LIST_DCN30()` and `DWBC_COMMON_MASK_SH_LIST_DCN30()`.
- `drivers/gpu/drm/amd/display/dc/dwb/dcn30/dcn30_dwb_cm.c` uses DWB gamut-remap and gamma programming helpers, so the DWB fields in this chunk are part of writeback color-processing correctness.
- Color helper code such as `dcn30_cm_common` and `dcn10_cm_common` receives these masks through `dcn3_xfer_func_reg` and `color_matrices_reg` structures and performs the actual packing and MMIO writes.

## Risks And Edge Cases

- A wrong shift or mask silently programs the wrong MMIO bits. The compiler will usually only catch missing macro names, not semantically incorrect values.
- MPCC0-5 field layouts are intentionally repeated. Copy/generator skew in one instance can break only a subset of display pipes and be hard to notice without multi-plane or multi-output coverage.
- MPCC topology selector fields are only 4 bits. `0xf` is used by driver code as a disconnected/idle selector in related MPC paths; misdocumenting or misprogramming these selectors can create invalid composition chains.
- The chunk starts mid-DWB RAMB and ends mid-MPCC_OGAM3 RAMA. Whole-file analysis must merge adjacent chunks before making completeness claims about DWB or MPCC_OGAM3.
- OGAM programming is double-buffered between RAM A and RAM B. Incorrect `MPCC_OGAM_SELECT`, current-select readback, or LUT host-select masks can cause writes to the active bank, visible color corruption, or no visible update.
- `MPCC_OGAM_MEM_PWR_STATE` is polled before LUT writes. If its mask or shift is wrong, `REG_WAIT()` may time out or proceed while the LUT memory is inaccessible.
- Region descriptor masks have narrow, mixed widths: 18-bit bases/starts, 19-bit offsets, 16-bit end/slope fields, 9-bit LUT offsets, and 3-bit segment counts. Width drift in any one field changes gamma curve interpretation.
- Gamut-remap registers pack two signed/fixed-point coefficients into one 32-bit register. A mask or shift error swaps or truncates coefficients and can produce strong color casts.
- Later DCN generations reorganize some MPCC fields, for example newer code introduces `MPCC_CONTROL2` for selected blend fields. Reusing this DCN 3.0.0 mask set against another ASIC revision is risky.

## Test Signals

Useful validation signals are mostly build-time macro coverage plus hardware/display behavior:

- Build DCN 3.0 display code with `dcn30_mpc.h`, `dcn30_mpc.c`, `dcn30_dwb.h`, and `dcn30_dwb_cm.c` included; missing or renamed field macros should fail through register-table expansion.
- Exercise MPCC composition with one plane, multiple planes, alpha blending, premultiplied alpha, global alpha/gain, background color, and bottom MPCC chaining.
- Validate MPCC idle/busy/disabled waits and state dumps through `mpc3_read_mpcc_state()` and `mpc3_read_reg_state()`.
- Program output gamma on several MPCC instances and verify RAM A/RAM B switching, LUT host writes, current-mode/current-select readback, and visible transfer-function changes.
- Test OGAM memory power transitions: power on before LUT writes, wait for `MPCC_OGAM_MEM_PWR_STATE`, then allow low-power mode when debug policy enables it.
- Program gamut remap A/B coefficient banks and confirm the driver can read back the current selected bank and matrix values without coefficient swaps.
- Exercise Display Writeback with output gamma RAM B active and validate captured-frame color output, not just scanout color.
- Run suspend/resume, modeset, hotplug, multi-display, and plane-update tests to catch stale MPCC routing or color block state after reprogramming.

## Open Cross-Chunk Questions

- The previous chunk must be consulted for the beginning of `DWB_OGAM_RAMB_START_CNTL_B/G/R`; this chunk starts after some RAMB start fields have already been defined.
- The next chunk must complete `MPCC_OGAM3` and likely cover additional MPCC OGAM instances or downstream MPC/DWB blocks before whole-file coverage can be reconciled.
- Final reconciliation should compare every register listed in `dcn30_mpc.h` and `dcn30_dwb.h` against both the offset and shift/mask headers to catch missing registers, missing fields, or generated-name mismatches.

### subset-b-001710: lines 56611-59133

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 56611-59133

## Scope

This chunk is a generated DCN 3.0.0 register field-layout slice. It contains only preprocessor constants for hardware register fields: `<REGISTER>__<FIELD>__SHIFT` bit positions and `<REGISTER>__<FIELD>_MASK` bit masks. There are no functions, structs, enums, variables, includes, locks, allocation paths, or runtime branches in this range.

The requested range contains 2,097 `#define` entries: 1,047 `__SHIFT` constants and 1,050 `_MASK` constants. The imbalance is caused by the artificial chunk boundary: the range starts in the middle of the `MPCC_OGAM3_MPCC_OGAM_RAMA_REGION_28_29` field group and ends at `MPC_RMU0_SHAPER_RAMB_END_CNTL_B`, before the matching masks and remaining RMU RAMB region definitions continue in the next chunk.

Although the source path is under a local `ceph-client` mirror, this header is AMDGPU display-controller metadata, not distributed filesystem code.

## Purpose

This header slice gives AMD DC display code the bit-level definitions needed to program the DCN 3.0 Multi-Plane Compositor (MPC), MPCC output gamma blocks, output color-space conversion, CRC/debug/status paths, and the beginning of RMU shaper programming. Driver code combines these constants with matching register offsets from `dcn_3_0_0_offset.h` through field helper macros such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

Major hardware areas covered by this chunk:

- Tail of `MPCC_OGAM3` output gamma RAM A/RAM B region definitions and gamut remap coefficients.
- Complete `MPCC_OGAM4` and `MPCC_OGAM5` output gamma blocks, including LUT access, RAM A/RAM B piecewise-linear region setup, offsets, starts, ends, slopes, mode/current-state fields, and gamut remap matrices.
- MPC global configuration: clock gating, MPCC/SFR/SFT/MPC soft resets, CRC selection/result fields, bypass background color, host read rate, DPP/OPP/MPCC/DWB pending status, vupdate lock registers, and DWB muxing.
- MPC output-combiner color path for outputs 0 through 5: output mux, rate-control/error fields, denormalization clamps, output CSC coefficient format, CSC modes, and CSC matrix coefficient registers.
- Beginning of MPC RMU support: RMU mux/status, memory power controls for RMU0 through RMU2, RMU0 shaper mode, offset/scale/LUT access, LUT write mask, and the start of RMU0 shaper RAM A/RAM B PWL region programming.

## Important APIs, Types, And Constants

There are no callable APIs. The exported interface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT`: the bit position for a field inside a DCN 3.0 register.
- `REGISTER__FIELD_MASK`: the field mask used to isolate or compose that field.
- Section comments such as `//MPCC_OGAM4_MPCC_OGAM_CONTROL` and address-block comments such as `// addressBlock: dce_dc_mpc_mpc_cfg_dispdec` group related constants by hardware register block.

Important macro families in this slice:

- `MPCC_OGAM[3-5]_MPCC_OGAM_RAMA_REGION_*` and `MPCC_OGAM[3-5]_MPCC_OGAM_RAMB_REGION_*`: LUT offset and segment-count fields for paired PWL regions 0 through 33. Each paired region normally has fields for even/odd region LUT offsets and segment counts.
- `MPCC_OGAM[3-5]_MPCC_OGAM_RAMA/RAMB_START_*`, `END_*`, and `OFFSET_*`: per-channel B/G/R start, start segment, start slope, start base, end base, end value, end slope, and offset fields for output gamma RAM interpolation.
- `MPCC_OGAM[4-5]_MPCC_OGAM_CONTROL`, `LUT_INDEX`, `LUT_DATA`, and `LUT_CONTROL`: output gamma mode/select/current-state, LUT host/read/write selection, color write masks, index, and 30-bit LUT payload access fields.
- `MPCC_OGAM[3-5]_MPCC_GAMUT_REMAP_*` and `MPC_GAMUT_REMAP_C*_C*_[AB]`: coefficient format/mode/current-state fields and packed signed coefficient fields for MPCC-local gamut remap matrices.
- `MPC_CLOCK_CONTROL`, `MPC_SOFT_RESET`, `MPC_CRC_*`, `MPC_BYPASS_BG_*`, `MPC_DPP_PENDING_STATUS`, and `MPC_PENDING_STATUS_MISC`: global MPC clock, reset, CRC capture, background, and pending-update status fields.
- `ADR_CFG_CUR_VUPDATE_LOCK_SET[0-5]`, `ADR_CFG_VUPDATE_LOCK_SET[0-5]`, `ADR_VUPDATE_LOCK_SET[0-5]`, `CFG_VUPDATE_LOCK_SET[0-5]`, and `CUR_VUPDATE_LOCK_SET[0-5]`: per-set vupdate lock controls used to coordinate atomic address/config/current updates.
- `MPC_OUT[0-5]_MUX`, `MPC_OUT[0-5]_DENORM_*`, `MPC_OUT_CSC_COEF_FORMAT`, and `MPC_OUT[0-5]_CSC_*`: output pipe selection, rate/flow control, denormalization clamp limits, output CSC mode, and packed CSC coefficient fields.
- `MPC_RMU_CONTROL`, `MPC_RMU_MEM_PWR_CTRL`, and `MPC_RMU0_SHAPER_*`: RMU mux/status, memory power controls, shaper mode/current state, offsets, scales, LUT index/data/write-mask, and first PWL region descriptors.

## Control Flow

This chunk has no runtime control flow. Its behavior is compile-time token expansion:

1. DCN 3.0 resource, MPC, DMUB, IRQ, GPIO, and clock code includes `dcn_3_0_0_sh_mask.h` with the matching offset header.
2. Register-table macros paste register and field tokens into names such as `MPCC_OGAM4_MPCC_OGAM_CONTROL__MPCC_OGAM_MODE_MASK` or `MPC_OUT2_CSC_C11_C12_A__MPC_OCSC_C11_A__SHIFT`.
3. Runtime code uses the generated field metadata through MMIO helpers to read, write, update, and poll the actual hardware registers.

The programming order is not encoded here. Consumers must still sequence MPCC disconnect/connect, LUT bank selection, gamma RAM programming, gamut remap enablement, output CSC update, CRC capture, vupdate locking, reset, memory power transitions, and RMU shaper writes according to the display hardware programming model.

## State And Persistence Behavior

The header stores no software state and persists nothing. It describes stateful MMIO fields owned by DCN hardware:

- MPCC OGAM fields hold output gamma mode, bank selection, LUT contents, interpolation region boundaries, slopes, bases, offsets, and gamut remap matrices. These affect color output until overwritten, power gated, reset, or replaced during a modeset/color-management update.
- MPC output fields hold the selected MPCC feeding each OPP, rate/flow-control configuration, denormalization clamp ranges, CSC mode, and CSC coefficients for each of six outputs.
- CRC fields control capture source, update locking, one-shot or continuous capture, stereo/interlace behavior, and expose CRC result channels.
- Pending-status and vupdate-lock fields expose or coordinate double-buffered update state across DPP, OPP, MPCC, DWB, address, configuration, and current parameters.
- Soft-reset and clock-gating fields can reset or gate compositor subblocks. Their effects are hardware-visible and may persist until explicitly changed or reset by the device.
- RMU memory power and shaper fields configure muxing, memory low-power behavior, LUT access, scaling, offsets, and PWL region layout for the RMU0 shaper path.

The macros do not distinguish read-only status, write-one-to-clear, sticky status, self-clearing command bits, or ordinary read/write controls. That semantic burden remains with the consuming driver code and hardware specification.

## Dependencies And Integration Points

This chunk depends on generated-name compatibility with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h` for register offsets.
- DC register helper infrastructure that builds field metadata from `FD_MASK`, `FD_SHIFT`, `SF`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and indexed register-table macros.
- SOC/DCN base-address headers that map generated offsets to the correct MMIO segment.

Observed integration points in this tree include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`, which includes this generated header to build DCN 3.0 resource register tables.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c` and `dmub_dcn302.c`, which include the same offset and mask headers for DMUB-facing register metadata.
- `drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c` and `irq/dcn302/irq_service_dcn302.c`, which consume DCN 3.0 field definitions for interrupt sources.
- MPC code and resource macros across DCN generations use the same naming pattern for `MPC_OUT*_MUX`, `MPC_CRC_*`, `MPCC_OGAM*`, and `MPC_RMU*` fields. For example, `dc/mpc/dcn32/dcn32_mpc.h` defines field lists for MPCC OGAM LUT/gamut/PWL fields, and `dc/mpc/dcn10/dcn10_mpc.c` updates `MPC_OUT_MUX` fields through generated register helpers.

## Risks And Edge Cases

- Wrong shifts or masks compile cleanly but corrupt MMIO field access at runtime. A bad mask can route the wrong MPCC to an output, apply bad color transforms, leave stale pending status, or reset/gate an unintended compositor block.
- The chunk starts and ends mid-family. Whole-file conclusions must merge adjacent chunks for the full `MPCC_OGAM3` RAM A tail and the rest of `MPC_RMU0_SHAPER_RAMB_*`.
- Repeated instance families are copy-sensitive. `MPCC_OGAM4` and `MPCC_OGAM5`, and `MPC_OUT0` through `MPC_OUT5`, share layouts but are not interchangeable; one bad instance macro may only fail on a specific pipe/output.
- Gamma and CSC fields are visual-quality critical. Incorrect LUT indices/data masks, PWL segment masks, coefficient masks, or coefficient formats can cause banding, clipping, wrong color space, HDR/SDR conversion errors, or black/washed-out output.
- Pending and vupdate lock fields affect atomic update sequencing. Misidentified bits can make updates appear complete too early or keep them stuck pending, which can surface as flicker, missed flips, cursor artifacts, or modeset timeouts.
- Reset, clock, and memory power fields are high risk because writes can disable active display paths or interact badly with power-gated hardware.
- CRC and debug/status fields may have mixed control/status semantics. Using a status field in an update path or holding update locks incorrectly can make validation signals misleading.
- The generated constants are untyped `long` literals with `L` suffixes. Consumers must keep 32-bit register semantics intact when composing masks, especially for high-bit masks such as `0x80000000L` and packed 16-bit coefficient/result fields.

## Test Signals

Useful validation signals for this chunk are mostly build-time consistency plus DCN 3.0 display behavior:

- Build AMDGPU display code with DCN 3.0/3.0.2 enabled; unresolved or renamed field macros should fail in resource, DMUB, IRQ, GPIO, clock, and MPC register-table compilation.
- Mechanically verify that each complete register group in this range has paired shift/mask definitions, allowing for the intentional boundary exceptions at the first `MPCC_OGAM3` group and final `MPC_RMU0_SHAPER_RAMB_END_CNTL_B` line.
- Compare the generated shifts/masks against AMD's authoritative DCN 3.0 register database and the matching `dcn_3_0_0_offset.h` register names.
- Exercise color-management paths: output gamma LUT programming, RAM A/RAM B bank selection, gamut remap matrices, output CSC coefficients/modes, denormalization clamps, HDR/SDR transitions, and suspend/resume restoration.
- Test multi-display and high-instance configurations that use MPCC/OPP outputs beyond 0-3, especially output paths 4 and 5 and `MPCC_OGAM4`/`MPCC_OGAM5`.
- Validate atomic update timing with page flips, cursor updates, surface/config/current updates, vupdate locking, and pending-status polling.
- Validate MPC CRC capture using one-shot and continuous modes, selected sources, stereo/interlace modes, and result readback.
- Test reset, clock gating, memory power, and RMU shaper flows during modeset, blanking, idle, suspend/resume, and color-pipeline reconfiguration.
- Watch kernel logs and display diagnostics for underflow, modeset timeout, stale pending bits, CRC mismatch, color corruption, black screens, flicker, or resume failures.

## Cross-Chunk Notes

The previous chunk owns the beginning of the `MPCC_OGAM3` output gamma block. This chunk begins at the tail of `MPCC_OGAM3_MPCC_OGAM_RAMA_REGION_28_29`, then covers the rest of `MPCC_OGAM3` RAM B/gamut fields and complete `MPCC_OGAM4`/`MPCC_OGAM5` blocks. The next chunk continues after `MPC_RMU0_SHAPER_RAMB_END_CNTL_B` and is required to complete RMU0 RAMB end/region definitions and the later RMU register layout.

### subset-b-001711: lines 59134-61618

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 59134-61618

## Scope

This chunk is a late slice of AMD's generated DCN 3.0.0 register shift/mask header. It contains 2,123 `#define` entries and 348 register/address-block comments, but no C functions, structs, enums, global variables, includes, allocation paths, or executable control flow. The exported interface is the generated `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` namespace consumed by register helper macros.

The range begins in the middle of `MPC_RMU0_SHAPER_RAMB_END_CNTL_B`, covers the rest of the `MPC_RMU0` shaper/3DLUT fields, complete analogous `MPC_RMU1` and `MPC_RMU2` shaper/3DLUT field groups, DC perfmon blocks 28 and 29, stream packet/audio fields for instance 6 (`AFMT6`, `VPG6`, `DME6`), `HPO_TOP_CLOCK_CONTROL`, complete ABM field groups for `ABM0` and `ABM1`, and the first part of `ABM2` through `ABM2_DC_ABM1_ACE_THRES_12`.

Although this source tree is under a local `ceph-client` mirror, the file is AMDGPU display-controller hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this chunk is to describe bit layouts for DCN 3.0 display hardware registers so runtime driver code can read, compose, and update MMIO fields without hard-coding shifts and masks at each call site. It pairs with `dcn_3_0_0_offset.h`, which supplies register addresses. Consumers typically include both files and feed these constants into macros such as `SF`, `FD_SHIFT`, `FD_MASK`, `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_READ`, and `REG_WRITE`.

The covered hardware areas are:

- MPC RMU shaper and 3D LUT color-management fields for RMU instances 0, 1, and 2.
- DC performance monitor field layouts for counters 28 and 29.
- `AFMT6`, `VPG6`, and `DME6` stream-output support fields for audio, infoframes, generic packets, ISRC/MPEG metadata, CRC/status, memory power, and DME control.
- HPO top-level clock-gating control.
- ABM/backlight fields for ambient light input, user/target/current levels, final/minimum duty cycle, ABM enablement, frame-rate update control, grouped register locking, ACE curve programming, histogram/luma statistics, sample-rate control, histogram result readback, and master lock.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. Its only API surface is generated preprocessor constants:

- `REGISTER__FIELD__SHIFT`: bit position for a field.
- `REGISTER__FIELD_MASK`: bit mask for the same field.
- Register comments such as `//MPC_RMU1_3DLUT_MODE` and address-block comments such as `// addressBlock: dce_dc_opp_abm0_dispdec` group the constants by hardware block.

Important field groups:

- `MPC_RMU[0-2]_SHAPER_*`: shaper enable/mode, per-channel offsets and scales, LUT index/data, write-enable mask, RAM A/B start/end controls, and 34 exponential-region descriptors per RAM bank. Region pairs use LUT-offset fields and segment-count fields; start/end controls split per-channel end/base values.
- `MPC_RMU[0-2]_3DLUT_*`: 3D LUT mode, size, current mode readback, index, packed data writes, 30-bit data path, read/write control fields such as write-enable mask, RAM select, 30-bit enable, config status, and read select, plus output normalization and RGB offsets.
- `DC_PERFMON28_*` and `DC_PERFMON29_*`: event-selection, counter-control, counter-state, perfmon-run control, interrupt status/ack, low/high counter readback, and current-value misc fields.
- `AFMT6_*`: VBI/audio packet control, audio layout override, audio info fields, IEC 60958 channel-status fields, CRC control/result/status, ramp controls, packet enables, infoframe control, audio source selection, and memory power.
- `VPG6_*`: generic packet access/data, generic-stream-packet frame and immediate update controls, update locks and pending flags, generic status, memory power, ISRC access/data, and MPEG info fields.
- `DME6_*`: DME enable/reset, ready/status, clock gating, memory low-power, and shut-down control fields.
- `HPO_TOP_CLOCK_CONTROL`: HPO top clock-gating disable field.
- `ABM[0-2]_*`: PWM level fields, ABM enable and auto-update controls, grouped register lock/update behavior, ABM processing enable/bypass, IPCSC coefficient selection, ACE slopes/offsets/thresholds, histogram/luma-sensor read-progress flags, histogram bin controls, luma sums/min/max/counts, sample-rate frame counters, histogram result registers, and backlight master lock.

## Control Flow

This header has no runtime control flow. Its effect is compile-time symbol resolution:

1. DCN 3.0 display code includes `dcn_3_0_0_sh_mask.h` with the matching offset header.
2. Register-list macros paste register and field names into `SF(...)`/`FD_*` macro invocations.
3. The resulting shift/mask tables are stored in per-block structures such as ABM, VPG, AFMT, stream encoder, DMUB, IRQ, GPIO, and clock-manager register metadata.
4. Runtime code uses those tables through MMIO helpers to program color LUTs, packet generators, audio formatting, performance counters, HPO clock state, ABM backlight processing, and histogram/luma measurement.

Runtime ordering is external to this header. Consumers must still sequence power/clock enablement, LUT RAM selection, shaper/3DLUT programming, frame-synchronized packet updates, ABM grouped-register locking, histogram sampling, perfmon run/ack handling, and suspend/resume restoration.

## State And Persistence Behavior

The chunk stores no software state and writes no persistent files. It describes MMIO-backed hardware state:

- MPC RMU state includes shaper/3DLUT mode, active RAM bank selection, LUT payload, region layout, output normalization, and offset/scale state. These values affect color processing until reprogrammed, disabled, power-gated, or reset.
- VPG/AFMT/DME state controls secondary-data packets, audio payload metadata, CRC/status reporting, memory power, and DME block readiness for stream instance 6.
- Perfmon state includes selected events, counter enable/run state, sampled counter values, and sticky interrupt/ack state.
- ABM state includes backlight PWM levels, ambient/user/target/current/final values, auto-update configuration, ACE curve coefficients, histogram/luma sample results, read-progress flags, register lock state, and master lock state.

The macros do not encode access permissions or side effects. Some represented fields are ordinary read/write controls, some are read-only status/counter fields, and some are sticky clear/ack or lock fields. Callers must use the register programming model, not just the macro name, to decide whether read-modify-write is safe.

## Dependencies And Integration Points

This chunk depends on generated consistency with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h` for register addresses and base-index selection.
- SOC/DCN base-address headers such as `sienna_cichlid_ip_offset.h`.
- AMD display helper macros in `dm_services.h`, `dmub_reg.h`, and DC block headers that build field metadata from `SF`, `FD_MASK`, and `FD_SHIFT`.

Observed direct include sites for the DCN 3.0 mask/offset pair include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c`

Specific integration patterns visible in nearby code:

- `dcn30_resource.c` instantiates `abm_regs`, `abm_shift`, and `abm_mask` with `ABM_DCN30_REG_LIST` and `ABM_MASK_SH_LIST_DCN30`, then creates per-pipe DMUB ABM objects. It also instantiates `vpg_regs`/`vpg_shift`/`vpg_mask` and `afmt_regs`/`afmt_shift`/`afmt_mask` for stream encoders.
- `dce/dmub_abm_lcd.c` programs fields from this ABM namespace through calls such as `REG_WRITE(DC_ABM1_HG_SAMPLE_RATE, ...)`, `REG_SET_3(DC_ABM1_HG_MISC_CTRL, ...)`, `REG_UPDATE(BL1_PWM_CURRENT_ABM_LEVEL, ...)`, and `REG_SET_3(DC_ABM1_HGLS_REG_READ_PROGRESS, ...)`.
- `dc/dpp/dcn10/dcn10_dpp.h` shows the broader color-management table shape for shaper and 3DLUT fields, including RAM A/B region descriptors, 3DLUT mode/index/data/read-write controls, and shaper LUT data/index registers. The RMU names in this chunk are the DCN 3.x MPC/RMU-side equivalents of that style of field metadata.

## Risks And Edge Cases

- A wrong shift or mask compiles cleanly but can corrupt hardware programming. This is especially risky for full-width masks, lock bits, clear/ack bits, and packed fields with adjacent channel data.
- The chunk starts and ends inside logical register groups. `MPC_RMU0_SHAPER_RAMB_END_CNTL_B` begins before this range, and `ABM2_DC_ABM1_ACE_THRES_12` continues after it. Whole-file analysis must merge adjacent chunks before claiming complete RMU0 or ABM2 coverage.
- Repeated instance families are copy-sensitive. `MPC_RMU0`, `MPC_RMU1`, `MPC_RMU2`, `ABM0`, `ABM1`, and `ABM2` use nearly identical field layouts; an instance-specific typo may only break one plane, pipe, panel, or multi-display configuration.
- LUT and shaper programming is stateful. Incorrect RAM selection, index increments, write-enable masks, 30-bit mode, or region descriptors can produce color corruption that may only appear with plane 3D LUT, HDR/color-management, or specific LUT dimensions.
- ABM fields combine backlight controls, histogram/luma measurement, grouped register locks, and DMUB-managed firmware behavior. Bad masks can cause incorrect brightness, flicker, missed frame updates, stuck locks, histogram readback failures, or ABM state divergence after suspend/resume.
- VPG/AFMT instance 6 may be exercised only on systems or configurations with enough stream encoders. Errors in these fields can escape single-display testing and appear as audio loss, bad infoframes, bad generic packets, ISRC/MPEG metadata failures, or CRC/status anomalies.
- Perfmon fields can have sticky or write-one-to-clear behavior. Using an interrupt-ack mask in a generic update path can drop evidence or leave counters in a stuck state.
- Clock/power fields such as HPO clock gating and DME/VPG/AFMT memory power must be programmed only when their blocks are in a valid clock/reset state; this header cannot enforce that sequencing.

## Test Signals

Useful validation signals are mostly compile-time consistency plus hardware exercise:

- Build AMDGPU/DC with DCN 3.0 and DCN 3.0.2 enabled. Missing or renamed fields should fail at macro expansion in resource, DMUB, IRQ, GPIO, clock, ABM, VPG, AFMT, and stream-encoder code.
- Mechanically verify that every `__SHIFT` macro in lines 59134-61618 has a matching `_MASK` macro with the same `REGISTER__FIELD` prefix, accounting for the artificial range boundaries at the first and last registers.
- Compare this chunk against AMD's generated register database and nearby DCN versions where field layouts are expected to remain compatible.
- Exercise color-management paths that use shaper LUTs and 3DLUTs: plane color properties, 17-cube and 9-cube LUT modes, host/DMA LUT loading where applicable, HDR/degamma/gamma transitions, modesets, and suspend/resume.
- Exercise stream encoder instance 6 where hardware supports it: DP/HDMI modesets, generic packets, audio playback, audio channel-status fields, infoframes, MPEG/ISRC metadata, CRC capture, and memory-power transitions.
- Run ABM/backlight tests on eDP panels: initial backlight programming, ABM level changes, ambient-level updates, PWM fraction changes, pause/save/restore, panel mask selection, histogram/ACE readback, and suspend/resume.
- Configure DC perfmon counters 28 and 29, validate event selection, low/high readback, run/stop state, interrupt status, and interrupt acknowledge behavior.
- Watch kernel logs and display diagnostics for blank displays, color corruption, audio dropouts, bad infoframes, stuck ABM updates, flicker, unexpected brightness changes, perfmon interrupt storms, and resume regressions.

## Cross-Chunk Notes

Adjacent chunks are required for complete file-level conclusions. The previous chunk owns the start of the `MPC_RMU0_SHAPER_RAMB_END_CNTL_B` register fields, and the next chunk continues `ABM2` ACE threshold fields and the remaining generated mask namespace. The merge lane should reconcile this report with neighboring chunks before making final claims about full `MPC_RMU0` or `ABM2` coverage.

### subset-b-001712: lines 61619-64242

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 61619-64242

## Scope

This chunk covers lines 61,619-64,242 of the generated DCN 3.0.0 register shift/mask header. It contains only preprocessor definitions for hardware register bit fields; there are no C functions, structs, enums, variables, or executable paths in this slice. The active interface is the macro namespace of `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` constants consumed by AMDGPU display register helper code together with the matching `dcn_3_0_0_offset.h` register-address header.

The chunk starts in the tail of the `ABM2` adaptive backlight block, contains complete `ABM3`, `ABM4`, and `ABM5` field layouts, then switches to HDA/Azalia controller, endpoint, legacy VGA indexed-register, HDMI/DP audio codec, audio descriptor, sink-info, CRC, input codec, and root-codec parameter blocks. It ends at `AZALIA_F2_CODEC_FUNCTION_PARAMETER_GROUP_TYPE`; the remaining root codec fields continue in the next chunk.

## Purpose

The purpose of this chunk is to describe the bit layout for several DCN 3.0 display sideband blocks that sit around the primary pipe programming path:

- ABM/PWM hardware instances that drive adaptive backlight management, brightness PWM levels, histogram/luma collection, ACE thresholds, and frame-synchronized register locking.
- HDA Azalia command/response controller registers for CORB/RIRB DMA rings, immediate verbs, DMA position buffers, and wall-clock snapshots.
- Legacy VGA indexed sequencer, CRTC, graphics-controller, and attribute-controller registers used by compatibility display paths.
- Azalia function group 2 output and input codec nodes used by HDMI/DisplayPort audio programming, ELD/sink data, channel allocation, stream format, channel status, LPIB, HBR, GTC timestamp embedding, multichannel mapping, and codec parameter reporting.
- Audio descriptor and sink-info index spaces plus audio CRC result registers used for debug/validation paths.

The header keeps these field definitions centralized so display, audio, ABM, and debug code can use generated `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, `FD_MASK`, and `FD_SHIFT` style helpers instead of hard-coded bit numbers.

## Important APIs, Types, And Constants

There are no callable APIs in this header. Important exported constants in this chunk are grouped by address block and register family:

- `ABM2_*`, `ABM3_*`, `ABM4_*`, and `ABM5_*` define adaptive backlight fields. Repeated fields include `BL1_PWM_AMBIENT_LIGHT_LEVEL`, `BL1_PWM_USER_LEVEL`, `BL1_PWM_TARGET_ABM_LEVEL`, `BL1_PWM_CURRENT_ABM_LEVEL`, `BL1_PWM_FINAL_DUTY_CYCLE`, `BL1_PWM_MINIMUM_DUTY_CYCLE`, `BL1_PWM_ABM_CNTL`, `BL1_PWM_BL_UPDATE_SAMPLE_RATE`, `BL1_PWM_GRP2_REG_LOCK`, `DC_ABM1_CNTL`, `DC_ABM1_IPCSC_COEFF_SEL`, `DC_ABM1_ACE_OFFSET_SLOPE_[0-4]`, `DC_ABM1_ACE_THRES_12`, `DC_ABM1_ACE_THRES_34`, `DC_ABM1_HGLS_REG_READ_PROGRESS`, `DC_ABM1_HG_MISC_CTRL`, luma-statistic registers, sample-rate registers, histogram bin shift/index registers, `DC_ABM1_HG_RESULT_[1-24]`, and `DC_ABM1_BL_MASTER_LOCK`.
- ABM lock/update fields include `ABM1_HGLS_REG_LOCK`, `ABM1_ACE_LOCK`, `ABM1_DBUF_HGLS_REG_UPDATE_PENDING`, `ABM1_ACE_DBUF_REG_UPDATE_PENDING`, `BL1_PWM_GRP2_REG_UPDATE_PENDING`, frame-start display-select fields, readback-double-buffer enables, and master-lock bypass bits. These are critical for frame-synchronized ABM programming.
- HDA controller fields include `CORB_WRITE_POINTER`, `CORB_READ_POINTER`, `CORB_CONTROL`, `CORB_STATUS`, `CORB_SIZE`, `RIRB_*`, `RESPONSE_INTERRUPT_COUNT`, `IMMEDIATE_COMMAND_*`, `IMMEDIATE_RESPONSE_INPUT_INTERFACE`, `IMMEDIATE_COMMAND_STATUS`, `DMA_POSITION_*`, and `WALL_CLOCK_COUNTER_ALIAS`.
- VGA indexed fields include `SEQ00`-`SEQ04`, `CRT00`-`CRT18`, `CRT1E`, `CRT1F`, `CRT22`, `GRA00`-`GRA08`, and `ATTR00`-`ATTR14`. These expose conventional VGA timing, cursor, memory-map, latch, graphics mode, palette, panning, and color-select fields.
- Output codec fields under `azendpoint_f2codecind` include converter format, channel/stream IDs, digital converter control, stripe control, GTC embedding, widget capabilities, supported rates, stream formats, pin widget control, unsolicited response, pin sense, default configuration bytes, speaker/channel allocation, downmix info, audio descriptors, multichannel enables, lip-sync, HBR, sink-info indexing/data, IEC 60958 channel-status override bytes, association info, digital output status, LPIB snapshots, coding type, format-change notification, wireless-display identification, remote keepalive, pin parameter capabilities, and connection-list length.
- Descriptor and sink-info blocks define `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`, manufacturer/product IDs, sink description length, port IDs, and `SINK_DESCRIPTION0` through `SINK_DESCRIPTION17`.
- CRC blocks define `AZALIA_INPUT_CRC0_CHANNEL[0-7]`, `AZALIA_INPUT_CRC1_CHANNEL[0-7]`, `AZALIA_CRC0_CHANNEL[0-7]`, and `AZALIA_CRC1_CHANNEL[0-7]`, each as full-register readback masks.
- Input codec fields under `azinputendpoint_f2codecind` mirror output converter/pin concepts for input status, input channel layout, input infoframe fields, channel status, multichannel input enables, LPIB snapshots, HBR, and input pin/codec capabilities.
- Root codec fields begin with vendor/device ID, revision ID, subordinate node count, function power state, subsystem ID bytes, converter synchronization, reset, subordinate node count, and group type.

## Control Flow

This chunk has no runtime control flow. Its behavior is compile-time macro expansion:

1. DCN 3.0 display/audio code includes the DCN 3.0.0 offset header and this shift/mask header.
2. Register-list macros concatenate generated register and field names into constants from this file.
3. Runtime helper calls perform MMIO reads/writes against the address constants while using the shift/mask constants here to isolate fields.

The ordering is still meaningful for maintenance. Each register generally lists all shifts before all masks, and address-block comments separate hardware register spaces. ABM3, ABM4, and ABM5 are near-identical generated instances; a one-off field drift between instances would be suspicious unless backed by hardware specification changes.

## State And Persistence Behavior

The file itself stores no software state and persists nothing. It describes hardware state that can persist in display/audio blocks until overwritten, reset, or power-gated:

- ABM/PWM registers hold brightness levels, ambient-light input, target/current/final duty cycles, ABM enable/bypass state, luma statistics, histogram bins, sample-rate frame counters, ACE slopes/offsets/thresholds, and lock/update-pending state.
- HDA controller registers hold DMA ring pointers, ring sizes, DMA enables, response interrupt counts, immediate-command busy/result-valid status, DMA position buffer base addresses, and wall-clock readback.
- VGA indexed registers hold legacy timing, cursor, memory addressing, graphics mode, palette, panning, and interrupt enable/clear state.
- Azalia codec fields represent stream format, channel mapping, digital converter state, channel-status bytes, HBR enablement, infoframe/sink data, LPIB/timer snapshots, unsolicited-response enables, pin sense, format-change state, and power/reset controls.
- CRC result registers expose sampled audio CRC state for validation and debug.

Many registers are double-buffered or latched. ABM fields include explicit lock, update-at-frame-start, update-pending, readback, and missed-frame/clear bits. HDA/Azalia command and response fields include busy, result-valid, reset, interrupt, overrun, and DMA-enable bits. Callers must preserve register-specific read/modify/write semantics because the macro names do not encode whether a bit is read-only, write-one-to-clear, edge-triggered, or latch-control.

## Dependencies And Integration Points

This generated header depends on exact name and numeric consistency with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`, which provides the corresponding register offsets.
- ASIC base-offset headers such as `sienna_cichlid_ip_offset.h`.
- AMD display register helper infrastructure that expands `SR`, `SRI`, `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, `FD_MASK`, and `FD_SHIFT`.

Important consumers and integration points include:

- `drivers/gpu/drm/amd/display/dc/dce/dce_abm.h`, `dce_abm.c`, and `dmub_abm_lcd.c`, which build ABM register tables and program sample rates, histogram/luma controls, PWM levels, thresholds, and read-progress clear bits.
- DCN resource code that maps per-instance ABM registers using `SRI(..., ABM, id)` style macros. The ABM instance prefixes in this chunk must line up with the offset header and the instance count exposed by the ASIC resource tables.
- Display audio code such as `drivers/gpu/drm/amd/display/dc/dce/dce_audio.c`, which uses Azalia codec and audio descriptor concepts to program HDMI/DP audio capabilities, descriptors, channel allocation, and stream-related registers.
- HDA/Azalia controller paths that depend on CORB/RIRB, immediate-command, DMA-position, wall-clock, stream-format, LPIB, and codec-node parameter fields matching the hardware's HD-audio programming model.
- Legacy VGA paths that can include generated VGA field names for indexed VGA register handling and compatibility mode setup.
- Debug and validation tooling that reads audio CRC channels, sink-info bytes, audio descriptors, pin sense, channel status, and format-change fields.

## Risks And Edge Cases

- A wrong shift or mask compiles cleanly but can corrupt MMIO field programming. This is particularly risky for ABM lock/update bits, audio DMA ring pointers, codec reset/power fields, and interrupt/clear bits.
- ABM instances are repetitive. Copy/generation drift between `ABM2`, `ABM3`, `ABM4`, and `ABM5` could affect only one display/backlight instance and be hard to catch in single-panel testing.
- Several ABM fields update at frame boundaries and expose `*_MISSED_FRAME` plus clear bits. Misusing a clear mask in a read/modify/write sequence can drop diagnostic state or hide missed programming windows.
- ABM brightness and PWM fields use 17-bit masks while many histogram and CRC fields use full 32-bit masks. Callers must not assume a uniform field width across the block.
- HDA CORB/RIRB and DMA-position base fields include unimplemented low bits and upper/lower base-address splits. Bad masks here can create misaligned DMA addresses or ring pointer corruption.
- Azalia codec nodes contain many protocol-defined byte fields, including IEC 60958 channel status, ELD/sink data, speaker allocation, HBR, and stream format. A one-bit error can present wrong audio capabilities to userspace or sinks even if display modeset succeeds.
- Input and output codec field names are similar but not interchangeable. Accidentally using output pin masks on input endpoint registers can compile if names are manually wired through generic helpers but will program the wrong bit layout.
- Legacy VGA fields are shared with compatibility paths. Changes in this generated section can affect boot consoles, handoff, or VGA disable/restore flows outside normal DCN modeset testing.
- This chunk ends mid-root-codec block. Whole-file reconciliation must include the next chunk before concluding that root codec function parameters are complete.

## Test Signals

Useful validation signals are mostly build-time, hardware-integration, and display/audio functional tests:

- Compile DCN 3.0/3.0.2 display code that includes `dcn_3_0_0_sh_mask.h`, especially ABM, audio, VGA, IRQ, and DMUB-adjacent register table builders.
- Macro-expansion or generated-header checks that compare every `ABM[2-5]`, HDA, VGA, Azalia, descriptor, sink-info, CRC, input-codec, and root-codec register field against the matching `dcn_3_0_0_offset.h` register names.
- Panel/backlight tests on hardware with ABM enabled and disabled, including brightness changes, ambient-light paths, histogram/luma statistics, sample-rate programming, frame-start update behavior, and suspend/resume.
- HDMI/DisplayPort audio playback tests covering channel count, sample rates, bit depths, HBR formats, channel allocation, lip-sync, ELD/sink description reporting, channel status, keepalive, and stream start/stop.
- HDA controller tests that exercise CORB/RIRB command rings, immediate codec commands, response interrupts, overrun handling, DMA position buffer snapshots, and wall-clock reads.
- Audio CRC and descriptor readback tests that verify all channel result registers and `AUDIO_DESCRIPTOR[0-13]` remain readable and stable.
- Legacy VGA smoke tests for boot handoff, console modes, VGA disable paths, and suspend/resume when compatibility registers may be saved or restored.
- Negative/error-path checks for format-change notifications, unsolicited-response enablement, pin sense, LPIB snapshot locking, and codec reset/power-state transitions.

## Open Cross-Chunk Questions

- The previous chunk must be consulted for the start of `ABM2`; this chunk only includes its tail from `ACE_THRES_34` onward.
- The next chunk must finish the `azroot_f2codecind` root codec function-parameter block before a complete Azalia root-node assessment is possible.
- Whole-file merge should compare ABM instance coverage in this mask header with DCN 3.0 resource tables to confirm whether all exposed ABM instances are actually used on every supported ASIC.

### subset-b-001713: lines 64243-66684

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 64243-66684

## Purpose

This chunk is a generated DCN 3.0.0 register shift/mask header slice for AMDGPU display audio hardware. It contains no executable C logic; its public interface is preprocessor constants of the form `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. These constants pair with the generated offset header so AMD display register helpers can compose field values for Azalia/HDA codec function, stream, and endpoint-indirect registers.

The range begins at the tail of the Azalia codec function parameter fields, then covers all 16 `azf0stream*_streamind` stream latency/FIFO blocks and endpoint-indirect field definitions for `AZF0ENDPOINT0`, `AZF0ENDPOINT1`, `AZF0ENDPOINT2`, and the first part of `AZF0ENDPOINT3`. There are 2,035 `#define` entries in this slice. The path sits under a `ceph-client` source mirror, but this code is AMD GPU display/audio metadata, not Ceph filesystem logic.

## Important APIs, Types, And Constants

There are no functions, structs, enums, variables, or runtime data structures. The important API surface is the generated macro namespace consumed by register-table and field-access macros:

- `AZALIA_F2_CODEC_FUNCTION_PARAMETER_*`: codec function group type, supported sample sizes/rates, stream-format capability, and power-state capability fields, including `CLKSTOP` and `EPSS`.
- `AZF0STREAM0` through `AZF0STREAM15`: repeated stream-indirect field groups for `AZALIA_FIFO_SIZE_CONTROL`, `AZALIA_LATENCY_COUNTER_CONTROL`, `AZALIA_WORSTCASE_LATENCY_COUNT`, `AZALIA_CUMULATIVE_LATENCY_COUNT`, and `AZALIA_CUMULATIVE_REQUEST_COUNT`.
- `AZF0ENDPOINT0` through `AZF0ENDPOINT3`: endpoint-indirect converter and pin-widget fields. Endpoint 0, 1, and 2 are complete in this chunk; endpoint 3 is partial and ends in `AZF0ENDPOINT3_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_1`.
- Converter widget fields: audio-widget capabilities, converter stream format, channel/stream ID, digital converter status/control bits, supported stream formats, supported size/rate capabilities, stripe control, ramp rate, GTC embedding, and GTC counter delta/min/max readbacks.
- Pin widget fields: pin audio-widget capabilities, HDMI/DP pin capability bits, unsolicited response controls, pin sense, output widget enable, channel/speaker allocation, 14 audio descriptors, multichannel enable/mute/channel maps, lipsync response, HBR capability, sink info and description bytes, hotplug/audio-enable control, forced unsolicited response payload, configuration default, IEC 60958 channel-status overrides, LPIB snapshots, coding type, format-change state, wireless display identification, remote keepalive, and audio enable/disable/format-change interrupt status fields.

The generated convention is regular: most registers list all shift constants first and all mask constants second. Full-width status/counter fields use `0xFFFFFFFFL`; narrow HDA fields use masks such as 4-bit channel IDs, 7-bit speaker allocations, 8-bit frequency/descriptor bytes, 16-bit product IDs, and high-bit control/status flags.

## Control Flow

This chunk has no local runtime control flow. Its practical use is compile-time expansion:

1. DCN 3.0 display/audio code includes this mask header with `dcn_3_0_0_offset.h`.
2. Register tables or helpers concatenate register and field names through macros such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, `REG_UPDATE`, `AZ_REG_READ`, and `AZ_REG_WRITE`.
3. Consumer code performs the actual MMIO or Azalia endpoint-indirect index/data accesses.

The stream blocks and endpoint blocks are declarative replicas. Any sequencing rules for HDA stream reset/run transitions, latency counter reset, endpoint index selection, converter programming, pin unsolicited responses, LPIB snapshot locking, interrupt acknowledgement, or hotplug audio enablement live in the AMD display audio driver and the hardware specification, not in this header.

## State And Persistence Behavior

The header stores no software state and persists no data. It describes hardware state held by the DCN 3.0 Azalia/HDA audio path:

- Codec function parameters advertise static or firmware-programmed capabilities: supported rates, bit depths, stream formats, group type, and power states.
- Stream-indirect registers expose FIFO sizing and latency telemetry for 16 Azalia streams. `AZALIA_LATENCY_COUNTER_RESET` is a control bit; worst-case, cumulative latency, and request counts are hardware counters/readbacks.
- Converter fields configure or report audio stream format, stream/channel routing, digital converter enable/status, IEC 60958-style channel status, HDMI/DP keepalive, striping, ramping, and GTC presentation-time embedding.
- Pin fields describe sink-facing state: HDMI/DP capability, speaker/channel allocation, ELD-like sink manufacturer/product/description bytes, hotplug audio enablement, HBR and multichannel capability, lipsync response values, unsolicited response payloads, default configuration, and remote keepalive.
- LPIB snapshot fields and timer snapshots expose stream position state. The snapshot lock and cyclic-buffer wrap count are synchronization-sensitive and should be handled by consumer code as hardware state with side effects.
- Audio enabled/disabled/format-changed interrupt status fields expose flag, mask, and type bits for endpoint state transitions.

Persistence is hardware-dependent. Some fields remain programmed until modeset, audio route change, suspend/resume, codec reset, or ASIC reset. Others are counters, snapshots, sticky flags, interrupt state, or write-sensitive controls.

## Dependencies And Integration Points

This chunk depends on generated-name compatibility with the DCN 3.0 offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`

The offset header supplies matching `ixAZF0STREAM*_*` and `ixAZF0ENDPOINT*_*` indirect register indexes, while this chunk supplies the field positions and masks for those registers. The two headers are normally consumed together by AMD display code that builds ASIC-specific register descriptors.

Important integration points in the surrounding driver are the display audio and resource paths that program HDMI/DP audio over the GPU's HDA/Azalia controller. Typical consumers include DCN resource setup, audio endpoint programming, IRQ handling, DMUB/DCN register table construction, and HDA/DP/HDMI hotplug or ELD update flows. The endpoint-indirect nature matters: callers must select the correct endpoint/index register before using the paired data register; these macros do not distinguish safe direct MMIO fields from indirect codec fields by type.

## Risks And Edge Cases

- A wrong shift or mask can compile cleanly while corrupting HDA/Azalia register programming, causing no audio, wrong channel layout, incorrect sample-rate reporting, bad ELD/sink data, broken HBR, or hotplug/audio-enable regressions.
- The repeated `AZF0STREAM0` through `AZF0STREAM15` and `AZF0ENDPOINT0` through `AZF0ENDPOINT3` patterns create copy/paste drift risk. A single instance-specific mismatch can affect only one stream or display audio endpoint.
- `mm`/`ix` access classes must not be confused. These stream and endpoint names correspond to indirect Azalia register spaces, so direct MMIO access without the proper index/data sequence is unsafe.
- Status, mask, and control fields are mixed in adjacent registers. Names such as `*_INT_STATUS`, `*_FORMAT_CHANGED`, `*_UNSOLICITED_RESPONSE_FORCE`, `*_HOT_PLUG_CONTROL`, and `*_LPIB_SNAPSHOT_CONTROL` should be treated as side-effect-sensitive until the consumer path proves its access semantics.
- Full-width counter and payload fields use `0xFFFFFFFFL` or large payload masks; callers need width-safe reads and writes, especially on code paths that combine values with shifts.
- Audio descriptor and sink-info bytes encode externally visible capabilities. Incorrect masks can make userspace or audio middleware see unsupported formats, wrong maximum channels, or stale monitor identity.
- The chunk ends mid-endpoint for `AZF0ENDPOINT3`; later chunks must complete the endpoint 3 channel-status override and remaining pin/audio status fields before whole-file conclusions are drawn.

## Test Signals

Useful validation signals are mostly build-time and hardware-integration oriented:

- Build AMDGPU/DC with DCN 3.0 and DCN 3.02 support so missing or renamed `AZALIA`, `AZF0STREAM`, and `AZF0ENDPOINT` field macros are caught by register table initializers and audio code.
- Diff this generated range against the authoritative AMD register database or adjacent DCN-generation headers, with special attention to repeated stream/endpoint instance drift.
- Exercise HDMI and DisplayPort audio on DCN 3.0 hardware: hotplug, modeset, DPMS, suspend/resume, audio enable/disable transitions, ELD/sink-info updates, and stream format changes.
- Test multichannel and HBR audio formats, including channel allocation, speaker allocation, IEC 60958 channel-status override fields, and endpoint `MULTICHANNEL_ENABLE`/`MULTICHANNEL_ENABLE2` mappings.
- Validate latency and position telemetry by reading stream FIFO sizing, worst-case/cumulative latency counters, request counters, LPIB snapshots, and timer snapshots while audio is active.
- Check interrupt behavior for audio enabled, audio disabled, format changed, and unsolicited response paths; monitor for missed events, repeated events, or interrupt storms.
- Inspect kernel logs and audio userspace state for HDA command timeouts, wrong monitor audio capability reporting, silent endpoints, channel swaps, bad sample-rate negotiation, and resume-only failures.

## Cross-Chunk Notes

The range starts after earlier Azalia function parameter definitions, so the `AZALIA_F2_CODEC_FUNCTION_PARAMETER_GROUP_TYPE` comment and any preceding fields are outside this chunk. It ends at line 66684 in the middle of `AZF0ENDPOINT3_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_1`; the remainder of endpoint 3 and additional endpoints, if present later in the file, must be merged from subsequent chunks.

### subset-b-001714: lines 66685-69052

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 66685-69052

## Scope

This chunk is a generated AMDGPU DCN 3.0.0 register shift/mask header slice. It contains only C preprocessor field constants: `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. There are no functions, structs, enums, storage objects, or executable branches in this range.

The covered range starts in the tail of the `AZF0ENDPOINT3` Azalia output endpoint field list, then defines complete repeated field groups for output endpoints `AZF0ENDPOINT4` through `AZF0ENDPOINT7`, and ends at the beginning of `AZF0INPUTENDPOINT0` input endpoint fields. The paired offset/index constants live in `dcn_3_0_0_offset.h`; this file supplies the bit layout used after the driver has selected an indirect Azalia endpoint register.

Within lines 66685-69052 there are 2,042 `#define` entries grouped under 312 register comments/address-block sections.

## Purpose

The purpose of this slice is to describe the bit layout of DCN 3.0 Azalia/HDA codec endpoint registers for HDMI/DisplayPort audio. AMD display code uses these macros through generated register helpers instead of open-coded shifts and masks when programming audio converters, pin widgets, sink/ELD information, channel allocation, IEC 60958 channel status, multichannel controls, hotplug/audio enable state, LPIB snapshots, and endpoint interrupt/status fields.

The output endpoint blocks model HDA codec converter widgets and pin widgets for display audio endpoints. The beginning input endpoint block mirrors the converter/pin field pattern for `AZF0INPUTENDPOINT0`, which represents an Azalia input endpoint space rather than an output pin.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The public interface is the generated macro namespace consumed by AMD display register-table macros:

- `AZF0ENDPOINT3_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_2` through endpoint 3 audio interrupt status groups: tail definitions for IEC 60958 channel-status override, pin association, digital output status, LPIB snapshot/readback, format change, remote keepalive, audio enable/disable, and audio format-change interrupt state.
- `AZF0ENDPOINT4_*`, `AZF0ENDPOINT5_*`, `AZF0ENDPOINT6_*`, and `AZF0ENDPOINT7_*`: four complete repeated output endpoint definitions. Each endpoint has the same converter/pin/audio-status schema with instance-specific prefixes.
- `AZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_CONVERTER_*`: input converter audio widget capability, format, channel/stream ID, digital converter, stream format, and supported size/rate fields.
- `AZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: beginning of input pin widget capability fields at the chunk boundary.

Important field families include:

- Converter capabilities and format fields: `AUDIO_CHANNEL_CAPABILITIES`, amplifier capability flags, `FORMAT_OVERRIDE`, `STRIPE`, `UNSOLICITED_RESPONSE_CAPABILITY`, `DIGITAL`, `POWER_CONTROL`, `LR_SWAP`, `TYPE`, `NUMBER_OF_CHANNELS`, `BITS_PER_SAMPLE`, `SAMPLE_BASE_DIVISOR`, `SAMPLE_BASE_MULTIPLE`, `SAMPLE_BASE_RATE`, and `STREAM_TYPE`.
- Stream routing and digital converter fields: `CHANNEL_ID`, `STREAM_ID`, `DIGEN`, validity/configuration/pre-emphasis/copy/non-audio/professional/level bits, `CC`, and `KEEPALIVE`.
- Pin capability and widget-control fields: jack/presence/trigger/HDMI/DP capability, output enable, unsolicited response tag/enable, response pin sense, channel allocation/speaker mapping, hotplug control, forced unsolicited response, configuration default, and digital output status.
- Audio descriptor and sink info fields: supported audio format descriptors `0` through `13`, ELD/sink information registers `0` through `8`, latency/HBR response fields, and sink product/manufacturer/port ID style fields.
- Multichannel and channel-status fields: `MULTICHANNEL*_ENABLE`, `MULTICHANNEL*_MUTE`, `MULTICHANNEL*_CHANNEL_ID`, multichannel mode, IEC 60958 mode/source/clock accuracy/word length/sampling frequency/original sampling frequency/channel number fields, and override-enable bits.
- Runtime status and interrupt fields: `AUDIO_ENABLE_STATUS`, audio enabled/disabled/format-changed interrupt flags, interrupt masks, interrupt types, `FORMAT_CHANGED`, change reason/response, `REMOTE_KEEP_ALIVE_*`, LPIB snapshot lock/wrap count, LPIB readback, and LPIB timer snapshot.

The pattern for each register is generated as all shifts followed by all masks. Consumers normally refer to these through `FD_SHIFT`, `FD_MASK`, `SF`, `REG_GET_FIELD`, `REG_SET`, `REG_UPDATE`, or audio-specific helpers rather than by naming the constants directly.

## Control Flow

This header chunk has no runtime control flow. Its effect is compile-time macro expansion:

1. DCN 3.0 display code includes `dcn_3_0_0_offset.h` and `dcn_3_0_0_sh_mask.h`.
2. Resource files instantiate audio register and field tables with generated helper macros. For example, DCN resource code uses `SF(AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_INDEX, AZALIA_ENDPOINT_REG_INDEX, mask_sh)` and matching data fields to describe the endpoint indirect index/data registers.
3. `dce_audio` code selects an endpoint through the endpoint index/data pair and accesses codec pin/converter indirect registers with `AZ_REG_READ` and `AZ_REG_WRITE`.
4. Field helpers compose or extract values using this chunk's shift and mask constants when updating audio endpoint state.

The chunk does not encode ordering rules. The required ordering for indirect endpoint access, hotplug enablement, audio descriptor programming, ELD/sink info writes, interrupt acknowledgement, and snapshot locking is implemented in the audio/display driver and the hardware programming model.

## State And Persistence Behavior

No software state is stored by this file. It describes fields in hardware-visible Azalia endpoint state.

State represented by this slice includes:

- Converter programming: channel count, sample width, rate divisor/multiple/base-rate, stream type, stream ID, channel ID, digital converter enable, validity/copyright/non-audio/professional bits, channel status category code, and keepalive state.
- Pin widget capability and control: HDMI/DP capability, jack/presence sense, output enable, unsolicited response configuration, default configuration encoding, channel allocation and speaker mapping, hotplug control, and forced response generation.
- ELD and sink metadata: sink information registers, audio descriptors, product/manufacturer/port fields, audio latency, video latency, HBR capability, and display-speaker allocation data used by HDMI/DP audio enumeration.
- IEC 60958 channel-status overrides: mode, source number, clock accuracy, word length, sample frequency, original sample frequency, sampling frequency coefficient, MPEG surround, CGMS-A, and per-channel number fields.
- Multichannel routing: enable/mute/channel ID state for even and odd multichannel slots plus a multichannel-mode bit.
- Runtime and interrupt state: audio enable status, audio enabled/disabled/format-changed flags, masks, type fields, format-change reason/response, remote keepalive capability/enable, LPIB byte position, LPIB timer snapshot, and cyclic buffer wrap count.

Persistence is hardware-dependent. Many converter, pin, ELD, descriptor, channel-status, and multichannel fields remain programmed until a modeset, audio reconfiguration, hotplug event, suspend/resume transition, power-gating event, or ASIC reset overwrites them. Status, interrupt, LPIB, snapshot, format-change, and output-active fields are dynamic and can change asynchronously with display/audio stream activity.

## Dependencies And Integration Points

This chunk is meaningful only with the generated DCN 3.0 register offset/index header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`

Observed direct include points for the DCN 3.0 offset/mask pair include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c`

Important runtime integration points:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h` defines the audio register list entries for `AZALIA_F0_CODEC_ENDPOINT_INDEX` and `AZALIA_F0_CODEC_ENDPOINT_DATA`, parameterized by endpoint instance.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.c` implements `AZ_REG_READ` and `AZ_REG_WRITE` and programs HBR/lipsync responses, hotplug control, channel speaker allocation, audio descriptors, and sink info registers that correspond to field groups in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c` wires DCN 3.0 audio endpoint index/data field metadata into the display resource tables.
- Similar field names are present in adjacent DCN and DCE generation headers, indicating this Azalia endpoint schema is reused across multiple ASIC generations with generated per-generation constants.

## Risks And Edge Cases

- These macros are part of the hardware programming ABI. A wrong shift or mask can compile cleanly while causing the driver to write the wrong bits in an HDA codec endpoint register.
- Output endpoints 4-7 are highly repetitive. Instance-prefix drift can affect only one display audio endpoint, making failures topology-dependent: one connector may lose audio while others still work.
- The range starts and ends mid-logical block. Endpoint 3 is only the tail of an earlier block, and input endpoint 0 continues after line 69052. Whole-file conclusions must merge adjacent chunks.
- Indirect endpoint access requires the correct index/data sequence. These field masks do not distinguish indirect codec registers from ordinary MMIO registers; consumers must not treat `AZF0ENDPOINT*` codec fields as direct addresses.
- Some names describe dynamic or side-effect-sensitive state. `INT_STATUS`, `FORMAT_CHANGED`, `LPIB`, `SNAPSHOT`, `HOT_PLUG_CONTROL`, `UNSOLICITED_RESPONSE_FORCE`, `OUTPUT_ACTIVE`, and response/status fields should be handled with the ordering and acknowledge rules expected by the audio hardware.
- Audio descriptor and sink-info fields are externally visible through HDMI/DP audio enumeration. Incorrect masks can advertise invalid channel counts, coding types, sample rates, bit depths, latency, HBR capability, or speaker allocation to the operating system/audio stack.
- IEC 60958 channel-status override fields can create subtle interoperability failures. Bad word length, sample-frequency, clock-accuracy, non-audio, or professional/consumer status bits may only show up with particular receivers or encoded-audio formats.
- LPIB snapshot and cyclic wrap count fields affect stream-position reporting. Incorrect field definitions can cause audio drift diagnostics, underrun handling, or playback-position reporting to fail without an obvious modeset/display symptom.
- Input endpoint fields at the boundary resemble output endpoint fields but are not interchangeable with output pin controls. Reusing output-only assumptions for input endpoints can corrupt the wrong Azalia widget state.

## Test Signals

Useful validation signals are mostly build-time macro expansion plus hardware audio behavior:

- Build AMDGPU/DC with DCN 3.0 and DCN 3.02 support enabled. Missing or renamed macros should fail in resource, audio, IRQ, clock, GPIO, or DMUB consumers that include this generated header.
- Diff this range against the generated source register database and neighboring DCN/DCE generation headers to detect per-endpoint copy/paste drift in endpoints 4-7 and the input endpoint 0 boundary.
- Exercise HDMI and DisplayPort audio on hardware using multiple output endpoints, including hotplug, unplug, DPMS off/on, modeset, suspend/resume, and audio route changes.
- Validate ELD and sink-info programming by checking that the OS audio stack sees correct sink name/manufacturer/product/port data, speaker allocation, latency, HBR support, and audio descriptors.
- Test common PCM formats across channel counts, sample widths, and rates, plus HBR/encoded formats where supported, to cover converter format and IEC 60958 channel-status fields.
- Verify multichannel layouts and channel allocation against receiver-reported capabilities, including mute/enable behavior and per-channel ID mapping.
- Confirm audio enable/disable and audio format-change interrupts are delivered and acknowledged without storms or missed transitions.
- Check LPIB and timer snapshot readback during active playback for monotonic position behavior, wrap-count handling, and absence of underrun/position timeout logs.
- Run receiver interoperability tests with HDMI TVs, AVRs, DisplayPort monitors, and MST/dock paths because channel-status and ELD mistakes often appear only with specific sinks.

## Cross-Chunk Notes

Adjacent chunks are required for a complete view of the Azalia field map. Earlier lines contain the start of `AZF0ENDPOINT3` and prior endpoint blocks; later lines continue `AZF0INPUTENDPOINT0` pin and input-control fields. The final per-file report should reconcile this mask header with `dcn_3_0_0_offset.h` so every indirect Azalia register used by the audio code has both an index/offset definition and matching field masks.

### subset-b-001715: lines 69053-71029

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 69053-71029

## Scope

This chunk covers the final 1,977 lines of the generated DCN 3.0.0 shift/mask header. It contains only preprocessor register-field constants and register grouping comments; there are no C functions, structs, enums, or executable statements in this slice.

The chunk is the tail of the `AZF0INPUTENDPOINT` register mask section for AMD display audio. It begins inside the endpoint 0 input-pin audio-widget-capability register, then defines the rest of endpoint 0 input-pin fields. It then provides complete, repeated register field definitions for `AZF0INPUTENDPOINT1` through `AZF0INPUTENDPOINT7`, and ends with the file's closing `#endif`.

## Purpose

The purpose of this header region is to describe the bit layout of DCN 3.0.0 Azalia function 0 input endpoint registers. These are HD-audio codec-style registers exposed through the GPU display audio path. Driver code combines these `__SHIFT` and `_MASK` constants with register-offset definitions from the companion offset header and with AMD display register helper macros to read, write, or compose specific fields without hard-coding numeric bit positions in implementation files.

At a higher level, the section models eight hardware input endpoints. For each endpoint, the generated macros describe:

- Input converter widget capabilities, format controls, stream/channel routing, digital-converter flags, stream format support, and supported sample size/rate capabilities.
- Input pin widget capabilities and pin capabilities, including HDMI/DP capability bits, jack/presence related fields, and output/input capability flags.
- Pin controls for unsolicited responses, input-pin sense, widget input enable, multichannel routing, high-bit-rate audio capability/enable, channel allocation, hot-plug audio enable state, forced unsolicited responses, default configuration, link-position snapshots, input activity state, and audio infoframe contents.

This file is part of the generated hardware contract. Its correctness matters because display audio programming code generally consumes the symbolic field names through macro concatenation rather than checking masks manually.

## Important APIs, Types, And Constants

There are no callable APIs or local types in this chunk. The exported interface is the macro namespace:

- `AZF0INPUTENDPOINT<n>_<REGISTER>__<FIELD>__SHIFT`: bit offset for a field in a specific input endpoint register.
- `AZF0INPUTENDPOINT<n>_<REGISTER>__<FIELD>_MASK`: 32-bit mask for the same field.
- Register comments such as `//AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME` group each field set.
- Address-block comments such as `// addressBlock: azf0inputendpoint7_inputendpointind` identify the generated register block for each endpoint.

The complete endpoint blocks in this chunk are endpoints 1 through 7. Endpoint 0 is partial because previous lines already defined its input-converter register fields and the first input-pin audio-widget capability shifts. Within each complete endpoint, the key register families are:

- `AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: exposes widget capability flags such as channel capability, input/output amplifier presence, format override, stripe, processing widget, unsolicited response capability, connection list, digital, power control, LR swap, delay, and widget type.
- `AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT`: encodes stream format fields including number of channels, bits per sample, sample base divisor, sample base multiple, sample base rate, and stream type.
- `AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_CHANNEL_STREAM_ID`: maps a converter to `CHANNEL_ID` and `STREAM_ID`.
- `AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`: describes digital converter control and IEC-style status bits such as `DIGEN`, validity/config/preemphasis/copy/non-audio/professional flags, category code, and keepalive.
- `AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_STREAM_FORMATS` and `SUPPORTED_SIZE_RATES`: full stream-format capability mask plus separate audio rate and bit-depth capability masks.
- `AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: pin widget capabilities, similar to converter widget capabilities but without `FORMAT_OVERRIDE`.
- `AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_CAPABILITIES`: pin capability fields for impedance sense, trigger requirement, jack detection, headphone drive, input/output capability, balanced I/O, HDMI, VREF control, EAPD, and DP.
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE`: unsolicited response `TAG` and `ENABLE` fields.
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_INPUT_PIN_SENSE`: 31-bit impedance sense plus the high `PRESENCE_DETECT` bit.
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_WIDGET_CONTROL`: input widget enable bit.
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2`: per-channel enable, mute, and channel-ID fields for multichannel indices 0-7.
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_HBR`: high-bit-rate capability and enable fields.
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_CHANNEL_ALLOCATION`: 8-bit channel allocation field.
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_HOT_PLUG_CONTROL`: clock-gating disable, clock-on state, and high-bit `AUDIO_ENABLED`.
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE_FORCE`: forced unsolicited response payload and force trigger bit.
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT`: HD-audio default pin configuration fields, including sequence, association, misc, color, connection type, default device, location, and port connectivity.
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL`, `LPIB`, and `LPIB_TIMER_SNAPSHOT`: lock/wrap-count and 32-bit link-position snapshot fields.
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INPUT_STATUS_CONTROL`: input activity, channel layout, and unsolicited-response enables for activity and channel-status/infoframe changes.
- `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME`: channel count, channel allocation, byte 5, and infoframe-valid fields.

The repeated endpoint shape is mechanically consistent: complete endpoints 1 through 7 each contribute 232 `#define` entries, while endpoint 0 contributes only the remaining 153 entries present in this chunk because its earlier converter fields precede line 69053.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time macro expansion:

1. C files include this generated shift/mask header, usually with the matching offset header for DCN 3.0.0 register addresses.
2. Register helper macros concatenate a register name and field name to resolve `__SHIFT` and `_MASK` constants.
3. Runtime driver code uses the resolved values in MMIO read/modify/write helpers or generated register-field tables.

The ordering is still semantically useful for maintainers and generators. Each register section generally lists all `__SHIFT` values first and then all `_MASK` values. Endpoint blocks are ordered numerically, and fields within a complete endpoint follow the HD-audio input converter and input pin register sequence.

## State And Persistence Behavior

The header itself stores no software state and persists no data. It describes hardware register state owned by the GPU display audio block:

- Converter state includes selected audio stream format, channel count, sample rate/base parameters, channel and stream IDs, digital converter flags, keepalive, and advertised format/rate capabilities.
- Pin state includes capabilities and policy fields that report or control audio presentation through HDMI/DisplayPort style endpoints.
- Unsolicited response fields control whether hardware can report asynchronous activity or configuration changes and which tag is used for those events.
- Input pin sense and presence fields report physical or logical endpoint status, including the high-bit `PRESENCE_DETECT` indicator.
- Multichannel enable and mute fields determine how up to eight channel slots are enabled and mapped.
- Hot-plug control contains clock-gating and audio-enable state; wrong bit definitions here can leave audio disabled or clocks held on/off incorrectly.
- LPIB and timer snapshot fields expose hardware playback/capture position style state, including a snapshot lock and cyclic-buffer wrap count.
- Infoframe and input-status fields expose current channel layout/activity and HDMI/DP audio infoframe data validity.

Persistence is hardware-defined. Writes to these registers can remain effective until another driver write, a display/audio reset, or an ASIC reset. Read-only capability and status fields must not be treated as writable simply because this generated header provides masks for them.

## Dependencies And Integration Points

This chunk depends on the generated DCN register model staying synchronized across several files:

- `dcn_3_0_0_offset.h` supplies the register offsets that pair with these field masks.
- `dcn_3_0_0_sh_mask.h` supplies the field layout consumed by AMD display register macros such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.
- Adjacent generated enum headers, for example `soc24_enum.h`, define symbolic values for many similarly named Azalia codec fields. Those enums provide meaning for field values, while this header provides bit placement.
- AMD display audio, DMUB, and DC register-table code can include this header indirectly when building DCN 3.0 register access tables.

The direct integration point is not a function call; it is the preprocessor name contract. Consumer code must spell the same generated register and field names used here. Any rename or missing define breaks macro expansion at build time, while a wrong numeric mask can compile successfully but corrupt MMIO behavior.

The section also integrates conceptually with the Linux DRM/ALSA display-audio path: hotplug, HDMI/DP audio capability exposure, channel allocation, infoframe validity, and stream-format programming all depend on these hardware fields matching the DCN 3.0.0 register specification.

## Risks And Edge Cases

- This chunk begins mid-register for endpoint 0. Whole-file reconciliation must combine it with the prior chunk to avoid falsely reporting endpoint 0 as missing converter fields or initial pin-widget shifts.
- The endpoint blocks are highly repetitive. Copy/generator drift in a single endpoint could be hard to see in review but would affect only one hardware endpoint at runtime.
- Numeric mask errors compile cleanly if the macro names still exist. A shifted `AUDIO_ENABLED`, `PRESENCE_DETECT`, `INFOFRAME_VALID`, or multichannel `CHANNEL_ID` field can produce silent display-audio failures.
- Some masks cover full 32-bit values, such as stream formats, LPIB, and timer snapshots. Callers need width-safe arithmetic and should avoid signed interpretation of full-register masks.
- Several fields are capability/status fields rather than normal writable controls. Register helpers do not encode access permissions, so caller correctness depends on the hardware programming model.
- `UNSOLICITED_RESPONSE_FORCE` can synthesize events. Using the force bit accidentally in a read/modify/write path could generate spurious audio or hotplug-related notifications.
- Multichannel enable and mute fields pack four channel slots per register. Incorrect channel-ID masks can cross-contaminate adjacent channel slot settings.
- Cross-ASIC reuse is risky. Similar Azalia endpoint field names appear in other generated AMD ASIC headers, but field coverage or semantics can vary by generation.
- The file ends at the include guard immediately after endpoint 7 infoframe masks. Any generator truncation here would likely surface as missing endpoint 7 or missing `#endif`, so keeping this tail stable is a basic structural integrity signal.

## Test Signals

Useful validation signals for this header are build-time and hardware-integration oriented:

- Compile AMD DCN 3.0 display code with `W=1` or equivalent warning coverage to catch missing generated field names in macro expansions.
- Preprocess or compile representative register-table users that expand `FD_MASK` and `FD_SHIFT` for Azalia/input-endpoint fields.
- Compare this header against `dcn_3_0_0_offset.h` and the register generator source to confirm every endpoint register with fields has matching shift and mask definitions.
- Exercise HDMI and DisplayPort audio enumeration on DCN 3.0 hardware, checking that endpoint capability reporting, stream format/rate reporting, and pin default configuration are sane.
- Run hotplug and audio enable/disable tests across connectors, watching `AUDIO_ENABLED`, unsolicited response behavior, and infoframe-valid status.
- Test multichannel audio modes, including channel allocation and 8-channel enable/mute/channel-ID programming.
- Validate high-bit-rate audio paths where `HBR_CAPABLE` and `HBR_ENABLE` are expected to be used.
- Exercise suspend/resume and display reset paths to catch stale converter, pin, hotplug, LPIB snapshot, or infoframe state after hardware reinitialization.

## Open Cross-Chunk Questions

- The final per-file report should merge this with the previous chunk to present endpoint 0 as a complete block.
- Whole-file reconciliation should verify that the generated endpoint count and field layout match the hardware specification for DCN 3.0.0, not just nearby ASIC headers.
- If the repository keeps generation provenance, the final report should identify whether these masks are imported from AMD register database output or hand-maintained snapshots, because manual edits would be unusually high risk.
