# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001751`: lines 1-2451, `Docs/researches/chunks/subset-b-001751_research.md`
- `subset-b-001752`: lines 2452-4727, `Docs/researches/chunks/subset-b-001752_research.md`
- `subset-b-001753`: lines 4728-7202, `Docs/researches/chunks/subset-b-001753_research.md`
- `subset-b-001754`: lines 7203-9815, `Docs/researches/chunks/subset-b-001754_research.md`
- `subset-b-001755`: lines 9816-12326, `Docs/researches/chunks/subset-b-001755_research.md`
- `subset-b-001756`: lines 12327-14847, `Docs/researches/chunks/subset-b-001756_research.md`
- `subset-b-001757`: lines 14848-17356, `Docs/researches/chunks/subset-b-001757_research.md`
- `subset-b-001758`: lines 17357-19868, `Docs/researches/chunks/subset-b-001758_research.md`
- `subset-b-001759`: lines 19869-22375, `Docs/researches/chunks/subset-b-001759_research.md`
- `subset-b-001760`: lines 22376-24894, `Docs/researches/chunks/subset-b-001760_research.md`
- `subset-b-001761`: lines 24895-27447, `Docs/researches/chunks/subset-b-001761_research.md`
- `subset-b-001762`: lines 27448-29915, `Docs/researches/chunks/subset-b-001762_research.md`
- `subset-b-001763`: lines 29916-32314, `Docs/researches/chunks/subset-b-001763_research.md`
- `subset-b-001764`: lines 32315-34689, `Docs/researches/chunks/subset-b-001764_research.md`
- `subset-b-001765`: lines 34690-37088, `Docs/researches/chunks/subset-b-001765_research.md`
- `subset-b-001766`: lines 37089-39485, `Docs/researches/chunks/subset-b-001766_research.md`
- `subset-b-001767`: lines 39486-41907, `Docs/researches/chunks/subset-b-001767_research.md`
- `subset-b-001768`: lines 41908-44291, `Docs/researches/chunks/subset-b-001768_research.md`
- `subset-b-001769`: lines 44292-46764, `Docs/researches/chunks/subset-b-001769_research.md`
- `subset-b-001770`: lines 46765-49290, `Docs/researches/chunks/subset-b-001770_research.md`
- `subset-b-001771`: lines 49291-51798, `Docs/researches/chunks/subset-b-001771_research.md`
- `subset-b-001772`: lines 51799-54370, `Docs/researches/chunks/subset-b-001772_research.md`
- `subset-b-001773`: lines 54371-56929, `Docs/researches/chunks/subset-b-001773_research.md`
- `subset-b-001774`: lines 56930-59302, `Docs/researches/chunks/subset-b-001774_research.md`
- `subset-b-001775`: lines 59303-61604, `Docs/researches/chunks/subset-b-001775_research.md`
- `subset-b-001776`: lines 61605-62433, `Docs/researches/chunks/subset-b-001776_research.md`

## Chunk Research

### subset-b-001751: lines 1-2451

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 1-2451

## Scope And Purpose

This chunk is the opening portion of the generated DCN 3.0.2 register shift/mask header used by the AMDGPU display driver. It does not implement executable logic; it declares preprocessor constants that describe bit positions and bit masks for memory-mapped display registers. Those constants are the ABI between DCN 3.0.2 C code and the hardware register layout.

The file begins with AMD's permissive license and the `_dcn_3_0_2_SH_MASK_HEADER` include guard, then defines register-field macros in the local naming pattern:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit.
- `<REGISTER>__<FIELD>_MASK` gives the field mask, usually as a `L`-suffixed integer literal.

The requested range covers several display blocks: legacy VGA/MMHUBBUB display decode, DCCG clock generation and clock gating, DCCG performance counters, RBBM interface timeout reporting, DMU display power gating, DMU/DC performance counters, DMU miscellaneous clock/memory controls, and the beginning of DMCU microcontroller control and interrupt status. Later chunks continue the same generated register catalog.

## Important Macro Groups

The first address block, `dce_dc_mmhubbub_vga_dispdec`, describes legacy VGA decode and memory aperture behavior. It includes VGA page address registers, render and mode control, sequencer reset behavior, pitch/height selection, memory base/high address fields, HDP/cache controls, per-display `D1VGA_CONTROL` through `D6VGA_CONTROL`, VGA status/interrupt/clear registers, VGA test/QoS controls, and indexed legacy VGA register data ports such as CRTC, sequencer, graphics, DAC, attribute, and generic feature/miscellaneous registers.

The VGA macros are used to preserve or alter narrow bitfields without disturbing adjacent hardware state. Examples include `VGA_RENDER_CONTROL__VGA_VSTATUS_CNTL_MASK`, VGA memory access status and interrupt bits, and per-pipe mode enable/timing/sync/rotation fields. The later source search shows older AMDGPU DCE paths also use the shared `VGA_RENDER_CONTROL` field names when manipulating VGA status behavior, which illustrates why these generated masks must match the real register layout exactly.

The `dce_dc_dccg_dccg_dispdec` block describes display clock generation. It includes PHY PLL pixel clock resync/enable/deep-color fields for PHYPLLA through PHYPLLE, DP DTO enable bits, DSC and DPP DTO phase/modulo fields, REFCLK/DPREFCLK selection and CGTT delays, DISPCLK frequency ramp/error-detection controls, display memory global power request disable, GTC and DS DTO counters, microsecond/millisecond time-base dividers, clock gate-disable registers, symbolic clock enable/force controls, soft-reset bits, audio DTO selection and phase/module registers, OTG pixel-rate controls for OTG0 through OTG4, and VSYNC latch/counter/interrupt controls for OTG0 through OTG5.

The DCCG macros expose repeated lane or instance patterns. For example, `OTGx_PIXEL_RATE_CNTL` fields select the pixel-rate source, enable a matching `DP_DTOx`, request add/drop pixel adjustment, enable half-rate output, and report DIO FIFO error/count bits. `DPPCLKx_DTO_PARAM` and `DSCCLKx_DTO_PARAM` provide phase/modulo fields, while `DPPCLK_DTO_CTRL` and `DSCCLK_DTO_CTRL` enable individual DTOs and their double-buffering. These constants feed clock programming code that needs exact field composition to avoid unstable link, stream, or compressor clocks.

The `dce_dc_dccg_dccg_dfs_dispdec` block contributes `DENTIST_DISPCLK_CNTL`, including DISPCLK and DPPCLK divider fields plus change-toggle/done bits. This is a synchronization point for clock divider changes: software writes divider and toggle fields and observes done fields.

The `dce_dc_dccg_dccg_dcperfmon0_dc_perfmon_dispdec` and `dcperfmon1` blocks define two DCCG performance monitor instances. Each instance has the same structure: `PERFCOUNTER_CNTL`, `PERFCOUNTER_CNTL2`, `PERFCOUNTER_STATE`, `PERFMON_CNTL`, `PERFMON_CNTL2`, `PERFMON_CVALUE_INT_MISC`, current-value low/high, and readback high/low registers. The fields select events, counted value type, increment mode, hardware start/stop sources, counter-off behavior, interrupt enable/status/ack, state reporting for counters 0-7, and read-select behavior.

The RBBMIF section describes timeout observability and masking for display register bus clients. It includes timeout delay and request-hold fields, decoded client status words, timeout address/op/read-write/ack/mask fields, per-client timeout-disable bits for clients 0-37, and status flags for interface state, read timeout, FIFO empty/full, and invalid access type/address.

The `dce_dc_dmu_dc_pg_dispdec` block defines display power-gating domains. It provides paired `DOMAINn_PG_CONFIG` and `DOMAINn_PG_STATUS` fields for domains 0-9 and 16-20 in this chunk, plus interrupt status/control registers for domains 0-21 and `DC_IP_REQUEST_CNTL__IP_REQUEST_EN`. Nearby DCN 3.0.2 hardware sequencer code uses these exact domain field names to power-gate HUBP, DPP, and DSC instances with `REG_UPDATE()` and `REG_WAIT()`.

The `dce_dc_dmu_dmu_dcperfmon_dc_perfmon_dispdec` block defines `DC_PERFMON2`, matching the DCCG perfmon register pattern but under DMU. The `dce_dc_dmu_dmu_misc_dispdec` block covers pipe disable/DMCUB enable, DMU clock gating and clock-on status, DMCU ERAM/IRAM memory power control, DMCU-SMU/static-screen interrupt reporting, DC-SMU interrupt control, and a forced deep-sleep allow field.

The final visible block, `dce_dc_dmu_dmcu_dispdec`, begins the DMCU microcontroller register definitions. It includes DMCU reset/enable/IRQ masking/dynamic clock gating/read-timeout fields, DMCU status bits, firmware/program counter start and checksum registers, host access controls for ERAM/IRAM with auto-increment and byte-enable fields, event trigger fields for software/internal interrupts, internal microcontroller interrupt-status bits, static-screen interrupt status/clear bits, and the beginning of the large `DMCU_INTERRUPT_STATUS` field map for ABM, MCP/SCP, UC internal/read-timeout, DCPG IHC power, and VBLANK events.

## Integration Points

This header is included by `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c` alongside `dcn_3_0_2_offset.h`. That resource file constructs the DCN 3.0.2 display resource pool and passes register address, shift, and mask tables into lower-level display objects. The shift/mask header is therefore tied to the matching offset header and to the generated register list macros in DCN 3.0.2 components.

The macros are not usually consumed directly as raw constants in hand-written code. AMD display code normally wraps them through `reg_helper.h` conventions such as `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT`, using helper `FN(reg_name, field_name)` macros to route a logical field name to the generated `shifts` and `masks` tables. The nearby DCN 3.0.2 hardware sequencer is a concrete example: it updates `DOMAINn_POWER_GATE`, waits on `DOMAINn_PGFSM_PWR_STATUS`, and temporarily enables `IP_REQUEST_EN` around DSC power-gating operations.

The DCCG fields integrate with display clock source, DTO, OTG, link encoder, audio, and timing generator setup. The power-gating fields integrate with HUBP/DPP/DSC lifecycle code. The RBBMIF and perfmon fields integrate with diagnostics, timeout handling, and performance telemetry. The DMCU/DMU fields integrate with display microcontroller, SMU notification, static-screen, memory-power, and vblank/ABM interrupt paths.

## Control Flow And State Behavior

There is no C control flow in this header. Runtime control flow emerges when the driver combines these constants with register access helpers:

- Read-modify-write updates preserve non-target bits using `_MASK` and `_SHIFT`.
- Poll loops such as power-gating waits read status fields until they match expected values.
- Clear-on-write interrupt/status fields are represented by duplicate `*_OCCURRED` and `*_CLEAR` names sharing the same bit positions and masks.
- DTO and clock-divider programming writes phase/modulo/divider/change-toggle fields, then observes enable/done/status fields.
- Perfmon programming selects events and run/start/stop behavior, then reads low/high value registers and acknowledges interrupts.

Hardware state persists in device registers, not in this header. The fields in this chunk control persistent or semi-persistent display hardware state including VGA legacy aperture setup, display and PHY clocks, clock gating disable/force decisions, DTO ratios, power-gated domain states, timeout masks, microcontroller firmware access windows, interrupt masks/clears, and static-screen or vblank interrupt status. Incorrect values can survive until reset or until later driver code rewrites the affected register.

## Dependencies

The chunk depends on the matching DCN 3.0.2 register offset definitions in `dcn_3_0_2_offset.h` and on the broader AMD display register access infrastructure. The constants also depend on AMD's hardware register specification for this ASIC revision. The source is generated-style C preprocessor data; its effective type and width depend on kernel C compilation rules for hexadecimal integer literals, so callers should treat masks as register-width values rather than portable semantic constants.

The names are part of a cross-file generated contract. A field rename, missing macro, or mismatched instance number can break compilation in files that populate register structures. A numerically wrong mask/shift can compile cleanly but silently manipulate the wrong hardware bits.

## Risks And Edge Cases

- Wrong masks or shifts are high-risk because failures are hardware-behavioral, not type-checked. A one-bit error in power gating can hang a display domain, while an error in DTO or DISPCLK fields can cause unstable clocks or link/display corruption.
- Many fields are repeated across instances (`OTG0`-`OTG5`, `DPPCLK0`-`DPPCLK5`, `DOMAIN0`-`DOMAIN21`, `DC_PERFMON0`-`2`). Copy/paste or generation drift can affect only one instance and escape broad testing.
- Status and clear fields often intentionally share bit positions and masks. Generic tooling must not treat duplicate shifts as accidental duplicates.
- Some fields cover full 32-bit masks (`0xFFFFFFFFL`), and some high-bit masks use signed-looking `L` literals such as `0x80000000L`. Register helpers should operate on unsigned 32-bit values to avoid sign-extension or comparison surprises.
- Legacy VGA fields are shared conceptually with older DCE code and may be touched by boot/VGA handoff paths. Misprogramming can affect early display, VGA decode, or console restore behavior.
- Power-gating domain numbering is semantic. DCN 3.0.2 hardware sequencer maps HUBP, DPP, and DSC instances to specific domains; a swapped domain field can wait on the wrong status bit or gate the wrong block.
- Interrupt status/clear fields for DMCU, DMU power gating, and perfmon can lose events if software writes broad masks instead of precise clear bits.
- This chunk ends in the middle of the `DMCU_INTERRUPT_STATUS` macro family, so later chunk research is needed before making whole-file conclusions about complete DMCU interrupt coverage.

## Test Signals

Useful validation signals for this chunk include:

- Kernel build coverage for DCN 3.0.2 display code, proving all referenced generated field names exist and the header composes with the matching offset header.
- Register table initialization compile checks in `dcn302_resource.c` and adjacent DCN 3.0.2 modules that use `FN()` mappings for shifts and masks.
- Hardware smoke tests on DCN 3.0.2 ASICs covering display bring-up, hotplug/link training, mode set, vblank, audio clocking, DSC enablement, and suspend/resume.
- Power-gating tests that exercise HUBP, DPP, and DSC domain transitions and confirm `DOMAINn_PGFSM_PWR_STATUS` reaches expected values without timeouts.
- Clock tests around DISPCLK/DPPCLK/DSCCLK/DP DTO programming, including frequency changes, half-rate output, and FIFO error counters.
- Interrupt tests for DCPG, DMCU static-screen, vblank, ABM, UC internal interrupt, and perfmon clear/ack paths.
- Diagnostics or debugfs-style register dumps comparing encoded field values against the hardware specification for masks with full-width, high-bit, and duplicated status/clear semantics.

### subset-b-001752: lines 2452-4727

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

### subset-b-001753: lines 4728-7202

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 4728-7202

## Scope

This chunk is a generated DCN 3.0.2 register field definition slice from `dcn_3_0_2_sh_mask.h`. It contains only preprocessor constants: every meaningful entry is a register-field `_SHIFT` and matching `_MASK` value, plus comment markers naming register blocks. There are no C functions, structs, enums, or executable control-flow constructs in the range. Its purpose is to provide the bit layout contract consumed by AMDGPU Display Core register access helpers when they read, write, update, acknowledge, or decode display hardware registers.

The range begins in the middle of the `DC_GPU_TIMER_START_POSITION_FLIP_AWAY` definitions, covers the tail of display interrupt status continuation registers, then covers interrupt destination registers for many display subblocks. It then transitions through the `dce_dc_dmu_dmcub_dispdec` DMCUB register block, MCIF writeback and MMHUBBUB/VGAIF blocks, two display perfmon blocks, and Azalia HDA stream/endpoint/audio control blocks. Because this file is generated from ASIC register specifications, correctness depends on exact numeric parity with hardware documentation and the companion address header for the same IP version.

## Purpose And Hardware Surface

The constants define bit positions and bitmasks for DCN 3.0.2 display registers. Driver code can combine these with register addresses from companion `*_offset.h` headers and with helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, or generated register table initializers. The `_SHIFT` constants express the low bit of each field, while `_MASK` constants express the full raw register mask before shifting.

Major hardware areas represented in this chunk:

- Display interrupt status continuation: `DISP_INTERRUPT_STATUS_CONTINUE23`, `CONTINUE24`, and `CONTINUE25` expose pending status bits for DCPG domain power transitions, DSC underflow/core/perfmon events, DMCUB inbox/outbox/timer/general/fault events, MMHUBBUB warmup, and ABM2-ABM5 events.
- Interrupt routing/destination: `DCCG_INTERRUPT_DEST`, `DMU_INTERRUPT_DEST`, `DMU_INTERRUPT_DEST2`, `DCPG_INTERRUPT_DEST`, `DCPG_INTERRUPT_DEST2`, `MMHUBBUB_INTERRUPT_DEST`, `WB_INTERRUPT_DEST`, `DCHUB_INTERRUPT_DEST`, `DCHUB_PERFCOUNTER_INTERRUPT_DEST`, `DCHUB_INTERRUPT_DEST2`, `DPP_PERFCOUNTER_INTERRUPT_DEST`, `MPC_INTERRUPT_DEST`, `OPP_INTERRUPT_DEST`, `OPTC_INTERRUPT_DEST`, `OTG0_INTERRUPT_DEST` through `OTG5_INTERRUPT_DEST`, `DIG_INTERRUPT_DEST`, `I2C_DDC_HPD_INTERRUPT_DEST`, `DIO_INTERRUPT_DEST`, `DCIO_INTERRUPT_DEST`, `HPD_INTERRUPT_DEST`, `AZ_INTERRUPT_DEST`, `AUX_INTERRUPT_DEST`, and `DSC_INTERRUPT_DEST` define which display events are routed to interrupt destinations.
- DMCUB register block: `DMCUB_REGION*`, `DMCUB_REGION3_CW*`, interrupt enable/ack/status/type registers, external interrupt status/context/ack, fault address registers, secure and memory controls, inbox/outbox ring base/size/read/write pointers, timers, scratch registers, control, GPINT data registers, low-power wake, memory power, timer current, and processor ID.
- MCIF writeback block for `mcif_wb0`: buffer manager control/status, four writeback buffer status/status2 registers, pitch, Y/C base addresses and high address parts, arbitration, SCLK/P-state/watermark controls, clock/self-refresh controls, luma/chroma sizes, per-buffer resolution, VMID, and timing timeout fields.
- MMHUBBUB and VGAIF block: writeback P-state/watermark and warmup controls, warmup base/region/VMID, outstanding counters, VGA source split, memory power status/control, clock control, soft reset, DMU interface error status, and client unit IDs.
- Display performance monitor blocks: `DC_PERFMON3_*` for MMHUBBUB perfmon and `DC_PERFMON4_*` for Azalia perfmon, including counter control, counter control 2, counter state, perfmon control, counter-value interrupt misc, and low/high value readout fields.
- Azalia HDA display audio: stream index/data windows for streams 0-7, endpoint index/data windows for endpoints 0-7, `AZ_CLOCK_CNTL`, and `AZALIA_CONTROLLER_CLOCK_GATING`.

## Important Definitions

The primary API surface is the macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field shift count.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the unshifted register word.
- Comment-only `// addressBlock: ...` lines group subsequent register definitions by hardware aperture.
- Comment-only `//<REGISTER>` lines group the field macros for each register.

Notable field families:

- Interrupt status bits are single-bit flags, commonly at direct bit positions. Examples include DCPG power up/down bits in `DISP_INTERRUPT_STATUS_CONTINUE23`, DMCUB inbox/outbox/timer/fault bits in `DISP_INTERRUPT_STATUS_CONTINUE24`, and ABM ready/backlight update bits in `DISP_INTERRUPT_STATUS_CONTINUE25`.
- Interrupt destination bits are also single-bit selectors. They mirror the status-event taxonomy and let driver code select routing for OTG timing events, HUBP vblank/vline/timeout/flip events, HPD/RX events, AUX/DDC events, DSC error/perfmon events, DMCUB mailbox events, and display block perf counters.
- DMCUB region address fields use large address masks, for example low offsets starting at bit 8 with `0xFFFFFF00L`, high offsets with `0x0000FFFFL`, top-address masks like `0x1FFFFFFFL`, and enable bits at bit 31. Region 3 is subdivided into code windows `CW0` through `CW7`, each with base, top, offset, and offset-high definitions.
- DMCUB mailbox registers use full-width or size/pointer masks for firmware/driver ring-buffer communication. The register names distinguish inboxes from host to DMCUB and outboxes from DMCUB to host, each with base address, size, write pointer, and read pointer.
- DMCUB interrupt registers separate enable, acknowledge, current status, and type. This makes it possible to configure interrupt generation, inspect fault or mailbox completion state, and clear individual bits without conflating status and control semantics.
- MCIF writeback buffer fields track buffer ownership and progress through active, software-locked, VCE-locked, overflow, disabled, mode, buffer tag, next buffer, current line, new content, color depth, TMZ, Y/C overrun, and eye-flag fields. The duplicated buffer 1-4 layout means writeback clients must use the instance-matched register and field names.
- Perfmon controls provide event selection, counter value selection, increment mode, hardware control source, run enable mode, restart, interrupt enable, off-mask, active state, counter selection, counted value type, hardware stops, count-off selection, perfmon run start/stop controls, interrupt status/ack bits, and low/high counter readout fields.
- Azalia stream and endpoint windows are indirect index/data pairs. Stream index fields include register index and write-enable bits; endpoint index fields expose the endpoint register index, while data registers are full 32-bit payload fields.

## Control Flow And State Behavior

There is no local control flow in this header. Runtime behavior emerges only when other driver code uses these constants to manipulate MMIO registers. The likely flow is:

1. Display code selects a register address from the matching DCN 3.0.2 offset header.
2. It uses a field macro from this file to encode a value, decode a readback, or set/clear a bit.
3. Hardware persists the resulting state in display registers until overwritten, reset, power-gated, or acknowledged according to the register semantics.

The state represented by these fields is entirely hardware-backed:

- Interrupt status and fault fields are volatile state generated by display hardware or DMCUB firmware. ACK fields are write paths used to clear latched events.
- Interrupt destination fields persist interrupt routing policy inside display hardware.
- DMCUB region, mailbox, scratch, control, and memory power fields persist firmware boot/configuration state and host-firmware communication state.
- MCIF writeback buffer fields persist live buffer ownership, addresses, dimensions, and error/status state for display writeback.
- MMHUBBUB/VGAIF fields persist memory-client controls, warmup setup, outstanding counter state, reset controls, and clock/memory-power settings.
- Perfmon fields persist counter configuration and expose volatile counter values and interrupt states.
- Azalia stream/endpoint indirect windows persist selected index/write-enable state and pass data to or from the underlying HDA display-audio registers.

The generated masks do not enforce ordering. Driver code must still respect hardware sequencing, for example disabling interrupts before changing routing, acknowledging latched interrupt bits after service, programming DMCUB region windows before firmware access, updating mailbox pointers in the expected order, and avoiding writeback buffer address changes while a buffer is active or locked.

## Dependencies And Integration Points

This header is not useful by itself; it integrates with:

- Companion DCN 3.0.2 register address headers, especially `dcn_3_0_2_offset.h`, which provide the MMIO register offsets for the names defined here.
- AMDGPU Display Core register helper layers that combine register offsets, masks, and shifts into safe read/modify/write operations.
- DMCUB host interface code that initializes DMCUB memory regions, ring buffers, scratch registers, GPINT paths, fault handling, and interrupt enable/ack/status registers.
- IRQ handling code that maps display block events into Linux DRM/AMDGPU interrupt handling paths.
- Display timing/pipe code for OTG, HUBP, DPP, OPP, MPC, DCCG, DSC, DIO/DCIO, AUX, HPD, DDC/I2C, and writeback paths.
- Display audio code using Azalia stream and endpoint indirect register windows.
- Debug/performance tooling that configures or samples DC perfmon counters.

The chunk also depends on exact naming consistency across generated headers and driver register tables. A typo or stale field name can break compile-time macro expansion even if the numeric value is correct.

## Risks And Maintenance Notes

- Generated-header drift is the main risk. Any mismatch between `_SHIFT`/`_MASK` values and the ASIC specification can silently corrupt unrelated bits during register updates or cause interrupt/fault handling to read the wrong bit.
- Interrupt status and destination definitions are dense and repetitive. Copying an `OTG`, `HUBP`, `DPP`, `DSC`, `ABM`, `DCPG`, `AUX`, `HPD`, or `DMCUB` field across instances without changing the instance number can route or clear the wrong event.
- Several fields are ACK bits. Treating ACK masks like ordinary persistent control bits can clear pending events or hide fault evidence.
- DMCUB address-window fields are security- and stability-sensitive. Incorrect base/top/offset masks can expose the firmware to the wrong memory region, generate undefined-address faults, or break firmware boot/mailbox traffic.
- MCIF writeback buffer fields include active/locked/overflow/TMZ/Y-C overrun state. Misprogramming them can corrupt captured frames, trigger underflow/overflow reports, or violate trusted-memory handling.
- Full-width data fields such as mailbox base/data, scratch registers, Azalia data registers, and perfmon low counters carry no range checking in this header. Callers must validate address alignment, size, and ownership constraints separately.
- Because these constants are preprocessor macros, there is no type safety. Incorrectly pairing a mask from one register with a shift from another can compile successfully if done through generic helper code.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, register-table, and hardware smoke tests:

- The AMDGPU driver should compile with DCN 3.0.2 support enabled, proving all referenced macro names still exist.
- Register helper tests or static checks should verify that every generated field has a mask/shift pair and that shifted masks fit within 32 bits.
- IRQ smoke tests should exercise hotplug, AUX/DDC completion, vblank/vline, flip, DSC error/underflow, DMCUB mailbox, and DMCUB fault paths and confirm the expected status/ack/destination bits are used.
- DMCUB firmware boot tests should confirm region windows, inbox/outbox pointers, scratch registers, GPINT data, and undefined-address/fetch/write fault reporting work.
- Display writeback tests should capture through MCIF writeback and check buffer active/lock/tag/current-line/new-content/overflow status transitions.
- Display audio tests should validate Azalia stream and endpoint indirect index/data access and audio enable/format-change interrupt reporting.
- Perfmon diagnostics should configure `DC_PERFMON3` and `DC_PERFMON4`, trigger counter interrupts, read low/high values, and acknowledge counter interrupt status bits.

## Chunk-Specific Summary

Lines 4728-7202 define a broad DCN 3.0.2 register-field surface rather than executable behavior. The most important responsibilities in this slice are interrupt status/routing for display subsystems, DMCUB memory/mailbox/interrupt/fault control, MCIF writeback and MMHUBBUB memory-client control, perfmon counter programming, and Azalia display-audio indirect register access. The constants are low-level ABI between the driver and display hardware; correctness is measured by exact field values, consistent generated naming, and successful hardware register behavior under interrupt, firmware, writeback, performance-monitor, and audio workloads.

### subset-b-001754: lines 7203-9815

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 7203-9815

## Scope And Purpose

This chunk is part of AMDGPU's generated DCN 3.0.2 shift/mask header. It contains C preprocessor constants only: no functions, structs, enums, storage, branches, loops, or local policy. The exported surface is a set of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros that describe bit offsets and already-positioned masks for memory-mapped display-controller registers.

The range spans 2,613 source lines and 2,065 `#define` entries. It starts at the final mask for `AZALIA_CONTROLLER_CLOCK_GATING`, covers Azalia/HDA audio, DCHUBBUB memory/VM/arbitration/performance, VM request/fault context registers, the first HUBP0/HUBPREQ0/HUBPRET0/cursor0 instance, DC performance monitor 5 and 6 blocks, and ends after the first fields of `HUBP1_DCSURF_ADDR_CONFIG`. Because the start and end are both chunk boundaries inside larger register groups, file-level reconciliation must merge adjacent chunks before making whole-file completeness claims.

The purpose is to let DCN302 display code program hardware fields through symbolic masks rather than open-coded bit constants. The companion `dcn_3_0_2_offset.h` supplies matching register addresses and base indices, while DCN302 resource code includes both generated headers and builds register tables for hubbub, VMID, HUBP, audio, stream encoder, and hardware sequencer components.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMD display hardware metadata. It has no Ceph, filesystem, distributed-storage, or network protocol behavior.

## Register Blocks Covered

The opening audio section completes an Azalia clock-gating field and then defines Azalia audio DTO, SOC clock, underflow filler, DMA cache/snoop/isochronous controls, cyclic-buffer sync, payload capability, stream arbiter, input/output CRC controls and results, and audio memory-power force/status fields.

`dce_dc_hda_azf0root_dispdec` covers HDA function-zero codec root parameters and controls: vendor/device and revision IDs, channel-count controls, resync FIFO startup keepout, function parameter capabilities, power-state set/actual state, codec reset, subsystem ID response bytes, converter synchronization, audio port connectivity overrides, GTC group offsets, and register-backed connectivity overrides.

The `AZF0STREAM8` through `AZF0STREAM15` blocks expose indexed stream register access through `AZALIA_STREAM_INDEX` and `AZALIA_STREAM_DATA`. The `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7` blocks similarly expose indexed endpoint access through input endpoint index/data registers.

`dce_dc_dchubbub_hubbub_sdpif_dispdec` defines SDPIF request/response, credit, force-IO, physical VM request, framebuffer/AGP/local-HBM apertures, per-pipe security levels for DCC metadata, cursor, GPUVM, surface, and DM data requests, SDPIF memory power, snoop control, host-VM security level, and unit-ID masks.

`dce_dc_dchubbub_hubbub_ret_path_dispdec` covers return-path DCC configuration constants, return-path memory power, and DCHUBBUB CRC controls/results.

`dce_dc_dchubbub_hubbub_dispdec` covers DCHUBBUB arbitration and global controls: outstanding request limits, saturation/QoS force, DRAM-state controls, four watermark sets A-D for urgency, self-refresh, and DRAM clock changes, watermark-change sequencing, timeout enable, global timer, surface check addresses/in-use bits, VTG0-VTG4 controls, soft reset, clock gating, DCFCLK gating delays, latency/performance measurement, timeout detection/interrupt status, fractional urgency bandwidth for nominal/flip cases, and `FMON_CTRL`/`FMON_CTRL_1`.

`dce_dc_dchubbub_dchubbub_dcperfmon_dc_perfmon_dispdec` defines DC performance monitor 5. `dce_dc_dcbubp0_dispdec_hubp_dcperfmon_dc_perfmon_dispdec` defines DC performance monitor 6. Both expose counter event selection, counted-value type, run/stop/count-off controls, per-counter state selectors, perfmon state/report count, comparison values, interrupt status/ack fields, and high/low readback.

`dce_dc_dchubbub_hubbub_vmrq_if_dispdec` defines display VM request interface state for contexts 0-15. Each VM context has page-table depth, block size, base address high/low, logical start high/low, and logical end high/low masks. The block also defines default address, default SPA/snoop, VM fault control, status, VMID/table-level/pipe decode, interrupt status, and fault address high/low fields.

`dce_dc_dcbubp0_dispdec_hubp_dispdec` defines the first HUBP instance's surface format, address/tiling configuration, primary/secondary luma and chroma viewport start/dimensions, request-size configuration for luma/chroma, HUBP enable/blank/timeout/underflow control, clock gating/status, VM page size, and DCFCLK/DPPCLK measurement windows.

`dce_dc_dcbubp0_dispdec_hubpreq_dispdec` covers HUBPREQ0 fetch-side state: surface pitch, VMID, primary/secondary and metadata surface addresses, surface control, flip control and interrupt status/clear bits, in-use and earliest-in-use addresses, expansion mode, TTU/QoS controls for surfaces and cursors, DM data VM controls, system aperture and L1 TLB controls, blanking/destination/prefetch/vblank/flip/nominal timing parameters, per-line delivery, cursor request settings, reference-to-pixel frequency conversion, DRQ limit, and request memory-power state.

`dce_dc_dcbubp0_dispdec_hubpret_dispdec` covers HUBPRET0 return-side state: DET buffer base, element packing, crossbar component selection, DET/DMROB/PIXCDC memory power, read-line windows, vblank/read-line interrupt mask/type/clear/status fields, current/snapshot read-line values, and read-line status.

`dce_dc_dcbubp0_dispdec_cursor0_dispdec` covers cursor0 and DM data delivery for HUBP0: cursor enable, mode, security/snoop/system flags, pitch, rotation/mirroring bypass, lines per chunk, latency measurement, address high/low, size, position, hot spot, stereo offsets, destination offset, cursor memory power, DM data address/security flags, hardware and software DM data control, QoS, status, underflow clear, and software payload data.

The final lines begin `dce_dc_dcbubp1_dispdec_hubp_dispdec` by defining `HUBP1_DCSURF_SURFACE_CONFIG` and the first two `HUBP1_DCSURF_ADDR_CONFIG` shifts. The rest of HUBP1 continues in the next chunk.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The important contract is the generated macro naming scheme:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in register position.
- Register-heading comments, such as `//HUBPREQ0_DCSURF_FLIP_CONTROL`, group field macros by hardware register.
- Address-block comments, such as `// addressBlock: dce_dc_dcbubp0_dispdec_hubpreq_dispdec`, identify generated hardware blocks and replicated instances.

The most operationally important macro families are the Azalia audio DMA/codec/power fields, DCHUBBUB arbitration and watermark fields, VM context and fault fields, HUBP0 surface/request/clock/underflow fields, HUBPREQ0 address/flip/TTU/QoS/prefetch/timing fields, HUBPRET0 read-line and interrupt fields, cursor0 address/mode/DM-data fields, and DC_PERFMON5/6 diagnostics fields.

Several names legitimately contain a logical field named `MASK`, producing identifiers such as `DCHUBBUB_TIMEOUT_INTERRUPT_STATUS__DCHUBBUB_TIMEOUT_INT_MASK_MASK`, `HUBPRET0_HUBPRET_INTERRUPT__PIPE_VBLANK_INT_MASK_MASK`, and `DC_PERFMON*_PERFCOUNTER_CNTL__PERFCOUNTER_OFF_MASK_MASK`. Tooling must not treat the first `_MASK` substring as the generated suffix.

## Control Flow

This header has no local control flow. Runtime behavior is created by consumers that include `dcn_3_0_2_offset.h` and this shift/mask header, assemble register/shift/mask structures, and call AMD display register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_FIELD`, `SF`, `SRI`, and related generated-list macros.

Typical runtime flows represented by these fields include:

- Audio setup: audio and stream encoder code programs Azalia DMA snoop/isochronous policy, DTO values, payload capability, stream/indexed endpoint access, HDA codec power/reset controls, and audio memory-power state.
- Display memory setup: hubbub code programs framebuffer/AGP/local address ranges, VM contexts, default/fault handling, VM request policy, security levels, and page-table aperture fields.
- Bandwidth and watermarks: DCHUBBUB and HUBPREQ fields encode urgency, self-refresh, DRAM-clock-change, TTU, QoS, prefetch, vblank, flip, nominal, and per-line delivery timing values derived from display-mode and DML calculations.
- Plane programming and flips: HUBP0/HUBPREQ0 fields carry surface format, tiling, pitch, viewport, primary/secondary/meta addresses, flip mode, flip pending/in-use status, and surface update interrupt/clear state.
- Cursor and metadata delivery: cursor0 fields program cursor image location, mode, size, position, hot spot, stereo offsets, memory security/snoop/system attributes, DM data payload location, QoS, and underflow status.
- Diagnostics and interrupt handling: CRC, timeout, force-IO, VM fault, hubp underflow, hubpret vblank/read-line, DM data, and perfmon status/ack fields expose transient hardware state to debug or IRQ paths.

The chunk does not encode whether a field is read-only, write-one-to-clear, self-clearing, sticky, safe only in vblank, or dependent on clocks/power. Those semantics live in the hardware specification and higher-level AMD display code.

## State And Persistence Behavior

The macros themselves hold no mutable state and persist nothing. They describe state in MMIO registers whose lifetime is controlled by the display hardware, the AMD display driver, DMUB/DMCU firmware, modesets, page flips, cursor updates, power transitions, suspend/resume, and GPU reset.

Configuration state includes Azalia audio DMA/cache policy, codec power/reset settings, SDPIF security and snoop policy, DCHUBBUB watermarks, VM page-table base/start/end registers, fault policy, HUBP surface format/tiling/viewports/request sizing, HUBPREQ surface addresses and timing parameters, HUBPRET read-line windows, cursor mode/address/size/position, memory-power force/disable fields, and perfmon event selections.

Live or latched state includes audio CRC completion/results, memory-power status, SDPIF response/credit errors, force-IO sticky status, DCHUBBUB CRC values, surface-check in-use bits, timeout status, VM fault status/address, HUBP timeout/underflow status, flip/in-use/earliest-in-use addresses, DM data fault/underflow/late/done state, HUBPRET read-line/vblank status, cursor/DM data underflow, and perfmon counter/interrupt/readback state.

Several fields are clear or ack bits (`*_CLEAR`, `*_ACK`, `*_STATUS_CLEAR`, `*_UNDERFLOW_CLEAR`, `*_INT_CLEAR`). The header only supplies bit positions; callers must preserve hardware-specific clear semantics when using read/modify/write helpers.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h`, which defines matching register addresses and base indices. The main visible include site is `display/dc/resource/dcn302/dcn302_resource.c`, which includes both generated DCN 3.0.2 headers and builds DCN302 register, shift, and mask tables.

Concrete integration points visible in the DCN302 resource path include:

- `dcn302_hubbub_create()`, which constructs the hubbub and VMID objects using generated hubbub and VMID register/mask tables. This ties in the DCHUBBUB, VM context, VM fault, memory aperture, watermark, and arbitration families in this chunk.
- `dcn302_hubp_create()`, which constructs HUBP instances with generated `hubp_regs`, `hubp_shift`, and `hubp_mask`; the HUBP0/HUBPREQ0/HUBPRET0/cursor0 families here form the instance-0 plane fetch and cursor surface.
- `dcn302_create_audio()` and `dcn302_stream_encoder_create()`, which construct audio, VPG, AFMT, and stream encoder resources. The Azalia/HDA macros in this chunk provide the audio-side register fields used by those paths.
- DCN302 hardware sequencer setup, which uses `HWSEQ_DCN302_REG_LIST()` and `HWSEQ_DCN302_MASK_SH_LIST()` tables from generated offsets/masks for power gating, hubp control, and display sequencing.
- IRQ and diagnostics paths that consume timeout, VM fault, underflow, surface flip, vblank/read-line, audio CRC, and perfmon status/ack fields through common DC register helpers.

The broader dependencies are the AMD display core register helper framework, DCN resource creation, DML bandwidth calculations, hubbub/hubp/hubpret/cursor implementations, audio/HDA components, DMUB firmware coordination, and ASIC-version dispatch that selects DCN302 layouts for compatible GPUs.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A wrong mask or shift can still compile but cause read/modify/write helpers to update the wrong bits, leave stale state, truncate values, or decode status incorrectly.

Chunk boundaries matter. The first line is only the `AZALIA_CONTROLLER_CLOCK_GATING__CLOCK_ON_STATE_MASK`; its matching shift and register context are in the previous chunk. The final register, `HUBP1_DCSURF_ADDR_CONFIG`, is incomplete in this chunk and continues later. Whole-file research must reconcile adjacent chunks before declaring complete Azalia clock-gating or HUBP1 coverage.

Audio fields affect both display audio and memory/cache policy. Incorrect DMA snoop, isochronous, underflow, DTO, codec power, or stream endpoint masks can produce HDMI/DP audio dropouts, bad HDA responses, broken CRC diagnostics, or low-power audio failures.

DCHUBBUB and HUBPREQ timing fields have high display risk. Bad watermarks, TTU, QoS, prefetch, vblank, flip, nominal, per-line-delivery, or DRQ-limit masks can cause underflow, visible corruption, failed page flips, missed prefetch windows, or unstable memory-clock/self-refresh transitions.

VM context and fault fields are security- and stability-sensitive. Wrong page-table base/start/end, aperture, default address, snoop/SPA, TLB, or fault clear/status masks can route display fetches through the wrong address space, hide faults, report the wrong VMID/pipe, or fault during flip/cursor/DM-data fetches.

HUBP0/HUBPREQ0/HUBPRET0/cursor0 are instance-specific. A generated error in instance 0 can affect only one plane or cursor and may pass tests that happen to light a different pipe. The repeated structure also makes copy/paste or diff review easy to misread.

Interrupt, status, and clear fields are easy to misuse. Fields named `*_STATUS`, `*_INT_STATUS`, `*_CLEAR`, `*_ACK`, `*_UNDERFLOW_CLEAR`, and `*_MASK_MASK` require hardware-specific write semantics; generic tooling or naive suffix parsing can corrupt event handling.

Memory-power fields are compact but broad in effect. Incorrect force/disable/state masks for Azalia, SDPIF, return path, HUBPREQ, HUBPRET, cursor, DET, DMROB, PIXCDC, or CROB memories can create failures that appear only during blanking, runtime power management, suspend/resume, or low-power display states.

## Test Signals

Build-time signals are direct: stale or missing macros should fail compilation in DCN302 resource, hubbub, hubp, audio, stream encoder, hardware sequencer, IRQ, and register-list paths around generated `SF`, `SRI`, `REG_FIELD`, `REG_GET`, `REG_SET`, `REG_UPDATE`, shift, and mask identifiers.

Generated-header validation should check that every visible `__SHIFT` has the expected matching `_MASK`, masks fit in 32-bit registers, repeated instance families retain expected parity, and all register names exist in `dcn_3_0_2_offset.h`. Validation must account for legitimate `_MASK_MASK` names and for this chunk's partial first and last register groups.

Runtime display tests should exercise DCN302 modesets, plane enable/disable, page flips, format/tiling changes, primary/secondary and chroma surfaces, DCC metadata paths, cursor enable/move/resize/stereo/security flags, DM data payload delivery, and multi-pipe operation that includes HUBP0 and HUBP1.

Bandwidth and power tests should cover DML-driven watermark programming, memory clock changes, self-refresh entry/exit, urgent traffic, prefetch windows, vblank/flip timing, VM fetches, low-power memory modes, suspend/resume, and runtime power transitions. Watch for HUBP underflow, DCHUBBUB timeout, force-IO sticky status, VM faults, and DM data underflow/late flags.

Audio tests should cover HDMI/DP audio playback, compressed/HBR channel counts, stream index/data paths, codec power-state transitions, audio CRC readback, underflow filler behavior, and suspend/resume with audio active.

Diagnostics should include perfmon 5/6 counter programming/readback, DCHUBBUB CRC capture, VM fault injection or fault-status validation where available, read-line/vblank interrupt behavior through HUBPRET, surface flip interrupt clear/status behavior, and register dumps on DCN302 hardware compared against expected bitfield layouts.

## Cross-Chunk Notes

This chunk is a middle slice of `dcn_3_0_2_sh_mask.h`. The previous chunk owns the earlier `AZALIA_CONTROLLER_CLOCK_GATING` fields and likely the preceding HDA register context. The next chunk continues `HUBP1_DCSURF_ADDR_CONFIG` and the rest of the replicated HUBP1/HUBPREQ1/HUBPRET1/cursor1 surface. The merge lane should combine these slices before describing full Azalia or all-HUBP instance coverage.

### subset-b-001755: lines 9816-12326

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 9816-12326

## Scope And Purpose

This chunk covers 2,511 lines from the generated AMD DCN 3.0.2 shift/mask header. It contains C preprocessor constants only: 2,106 `#define` entries, including 1,054 `__SHIFT` definitions and 1,069 `_MASK` definitions, plus generated register and address-block comments. There are no functions, structs, enums, global storage objects, or runtime branches in this range.

The range is a hardware-register field map for display pipe memory input blocks. It starts at the tail of the `HUBP1_DCSURF_ADDR_CONFIG` field group, completes most of HUBP/HUBPREQ/HUBPRET/cursor/perfmon instance 1, covers complete instance 2 and most of instance 3, and ends inside `HUBPRET3_HUBPRET_MEM_PWR_CTRL`. In display-driver terms, this is the bit-layout contract used by DCN 3.0.2 HUBP and HUBPREQ programming code to pack and extract surface, viewport, flip, prefetch, cursor, DMDATA, VM, QoS, timing, memory-power, interrupt, and perfmon fields.

Although this repository path is under `sources/distributed-fs/ceph-client`, this file is imported Linux AMD GPU display-driver register metadata, not Ceph filesystem logic.

## Register Blocks Covered

The first section finishes and then continues the `dce_dc_dcbubp1_dispdec_hubp_dispdec` block. It includes `HUBP1_DCSURF_TILING_CONFIG`, primary and secondary viewport start/dimension registers for luma and chroma planes, request sizing for luma/chroma, `DCHUBP_CNTL`, HUBP clock control, VMPG page-size config, and DCFCLK/DPPCLK measurement-window controls. These fields describe surface swizzle/tiling, viewport geometry, memory request granularity, blank/disable/underflow/timeout state, VTG selection, TTU enablement, clock gating/status, and perfmon measurement windows.

`dce_dc_dcbubp1_dispdec_hubpreq_dispdec` covers HUBPREQ instance 1. It defines surface pitch, VMID, primary/secondary luma/chroma surface addresses, primary/secondary metadata addresses, TMZ and DCC controls, flip control and flip interrupt status, in-use and earliest-in-use address readbacks, request expansion modes, TTU QoS watermarks, global/surface/cursor TTU controls, DMDATA VM control, VM system aperture and L1 TLB controls, blank/destination/prefetch timing, vblank/flip/nominal request timing parameters, per-line delivery timing, cursor request settings, reference-to-pixel frequency ratio, DRQ limit, HUBPREQ memory power control/status, and the DCN 2.1-era VM group timing additions.

`dce_dc_dcbubp1_dispdec_hubpret_dispdec` covers HUBPRET instance 1. It maps DET buffer base, 3-to-2 packing disable, crossbar source selection, DET/DMROB/PIXCDC memory power control and status, pipe read-line ranges, vblank/read-line interrupt mask/type/clear/status bits, read-line value snapshots, and read-line status bits.

`dce_dc_dcbubp1_dispdec_cursor0_dispdec` covers cursor instance `CURSOR0_1`. It defines cursor enable/mode/magnify/TMZ/snoop/system/pitch/lines-per-chunk/perfmon bits, cursor base address, size, position, hot spot, stereo offsets, destination X offset, CROB memory power control/status, DMDATA hardware address flags, DMDATA control/QoS/status, software DMDATA control, and software DMDATA data payload.

`dce_dc_dcbubp1_dispdec_hubp_dcperfmon_dc_perfmon_dispdec` covers `DC_PERFMON7`, the HUBP instance 1 perfmon block. It includes counter event selection, counted-value selection, increment mode, run/stop control, interrupt enable/status/ack, counter state selection for counters 0-7, perfmon state/report count/counter-off interrupt control, run-enable start/stop selection, captured value high/low fields, and read selection.

The instance 2 blocks repeat the same structure under `HUBP2`, `HUBPREQ2`, `HUBPRET2`, `CURSOR0_2`, and `DC_PERFMON8`. This range includes the full HUBP2/HUBPREQ2/HUBPRET2/cursor/perfmon field families, including surface address and metadata registers, DCC/TMZ control, flip sequencing, DMDATA VM status, TTU timing, request memory-power state, read-line interrupts, cursor DMDATA, and perfmon control/readback.

The instance 3 blocks begin at `dce_dc_dcbubp3_dispdec_hubp_dispdec`. The chunk covers `HUBP3` and `HUBPREQ3` in the same detail as the earlier instances, including surface geometry, request sizing, flip, VM, TTU, DMDATA, prefetch, vblank/flip/nominal timing, memory-power, and VM-group timing fields. It then starts `HUBPRET3`, covering `HUBPRET3_HUBPRET_CONTROL` and the beginning of `HUBPRET3_HUBPRET_MEM_PWR_CTRL`; the remaining HUBPRET3 fields continue in the next chunk.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated macro naming convention:

- `<BLOCK><instance>_<REGISTER>__<FIELD>__SHIFT` gives the field's low bit position in a 32-bit MMIO register.
- `<BLOCK><instance>_<REGISTER>__<FIELD>_MASK` gives the already-shifted field mask.
- Address-block comments such as `// addressBlock: dce_dc_dcbubp2_dispdec_hubpreq_dispdec` group fields by replicated hardware block.
- Register comments such as `//HUBPREQ2_DCSURF_FLIP_CONTROL` delimit logical MMIO registers.

The main field families are:

- `HUBP*_DCSURF_*`: surface pixel format, address configuration, tiling, luma/chroma primary and secondary viewport geometry.
- `HUBP*_DCHUBP_*`: request-size configuration, blank/disable/status control, clock control, VMPG page-size config, and measure-window controls.
- `HUBPREQ*_DCSURF_*`: pitch, VMID, base addresses, metadata addresses, DCC/TMZ control, flip control, flip interrupts, and in-use/earliest-in-use readback.
- `HUBPREQ*_DCN_*`: request expansion, TTU QoS, per-surface/per-cursor delivery timing, DMDATA VM, system aperture, and L1 TLB controls.
- `HUBPREQ*_{BLANK,DST,PREFETCH,VBLANK,FLIP,NOM,PER_LINE,CURSOR,REF_FREQ,DST_Y}_*`: display timing and delivery-parameter fields that feed DLG/TTU programming.
- `HUBPRET*_HUBPRET_*`: return-side DET/crossbar setup, memory power, read-line windows, read-line/vblank interrupt state, and live read-line snapshots.
- `CURSOR0_*_*`: cursor image address/geometry/control, cursor memory power, and cursor-attached DMDATA hardware/software payload controls.
- `DC_PERFMON7` and `DC_PERFMON8`: HUBP perfmon counter control, state, interrupts, and readback fields.

This chunk is consumed indirectly by AMD display register helpers. In DCN 3.0.2 resource setup, `display/dc/resource/dcn302/dcn302_resource.c` includes `dcn/dcn_3_0_2_sh_mask.h` and builds `hubp_shift` and `hubp_mask` from `HUBP_MASK_SH_LIST_DCN30(__SHIFT)` and `HUBP_MASK_SH_LIST_DCN30(_MASK)`. The matching register addresses come from `dcn/dcn_3_0_2_offset.h`, using macros such as `SRI(DCN_DMDATA_VM_CNTL, HUBPREQ, id)` and `HUBP_REG_LIST_DCN30(id)`.

## Control Flow And Runtime Use

This header has no runtime control flow. Its effective flow is preprocessor and MMIO-helper expansion:

1. DCN 3.0.2 resource code includes the matching offset and shift/mask headers.
2. Register-list macros instantiate per-pipe register-address tables for HUBP/HUBPREQ/HUBPRET/cursor blocks.
3. Shift/mask-list macros populate field tables by resolving tokens like `HUBP0_DCHUBP_CNTL__HUBP_BLANK_EN__SHIFT` or `HUBPREQ0_DCSURF_FLIP_CONTROL__SURFACE_UPDATE_LOCK_MASK`.
4. Runtime HUBP code calls helpers such as `REG_UPDATE`, `REG_GET`, `REG_SET`, `REG_WRITE`, and `REG_WAIT`; those helpers use the populated tables to read, mask, shift, update, and write 32-bit MMIO registers.

Representative runtime consumers are the DC hubp implementations under `display/dc/hubp/`. DCN 1.x/2.x/3.x HUBP code updates `DCHUBP_CNTL` for blanking, disable/reset, VTG selection, underflow clear, and no-outstanding-request polling; updates `DCSURF_FLIP_CONTROL` and `DCSURF_FLIP_CONTROL2` for surface update locks, stereo-sync flips, GSL, and triple buffering; writes cursor and DMDATA registers; and reads status fields for flip pending, DMDATA done, and HUBP state snapshotting. The exact DCN 3.0.2 shift/mask constants in this chunk make those generic paths hit the correct instance-specific bit positions.

## State And Persistence Behavior

The header itself stores no state and persists nothing. It describes state held in GPU display-engine MMIO registers:

- Surface and viewport fields represent the programmed scanout buffer shape, luma/chroma geometry, swizzle, DCC/TMZ settings, metadata surfaces, and primary/secondary surface address state. These usually persist until the next plane programming update, flip, HUBP disable, or display reset.
- Flip-control fields represent synchronization state around surface updates: update locks, flip type, vupdate skip count, pending flags, stereo-sync controls, pending delay/minimum time, GSL enable, and triple-buffer enable. Some fields are control bits; others are live status bits.
- HUBP control fields represent pipeline enable/blanking, VTG routing, TTU behavior, timeout/underflow status, and clear bits. Underflow and timeout clear fields have event-style semantics, so writes are not durable configuration in the same way as VTG or blanking fields.
- Request timing fields encode DLG/TTU and memory-request timing for vblank, flip, and nominal scanout: PTE/meta/VM group cycles, destination-Y intervals, prefetch ratios, per-line delivery, and DRQ limits. These persist as the timing program for a mode until recalculated or reset.
- VM and address fields represent VMID, L1 TLB enable/mode, system aperture bounds, DMDATA VM timing, VM fault/underflow/late status, and status-clear bits.
- Cursor fields represent cursor image address, size, position, hot spot, stereo offsets, DMDATA payload source, DMDATA QoS, update toggles, memory-power state, and completion/underflow status.
- HUBPRET fields represent return-side DET/crossbar setup, memory-power state, vblank/read-line interrupt configuration and status, and current/snapshot read-line position.
- Perfmon fields represent selected counted events, counter state, run/stop gating, interrupt state/acknowledge, and counter readback values.

Persistence is hardware-defined. Control fields remain programmed until later MMIO writes or reset events. Status fields reflect live hardware and may be sticky until a corresponding clear/ack bit is written. This header does not encode access direction; writable controls, read-only status, and write-to-clear fields all use the same macro style.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.0.2 register database staying synchronized across files:

- `dcn_3_0_2_offset.h` supplies the register addresses and base indices for the register names whose fields are defined here.
- `display/dc/resource/dcn302/dcn302_resource.c` includes this header and builds the DCN 3.0.2 HUBP register, shift, and mask tables.
- `display/dc/hubp/dcn30/dcn30_hubp.h`, `dcn20_hubp.h`, `dcn21_hubp.h`, and related hubp headers define `HUBP_REG_LIST_*` and `HUBP_MASK_SH_LIST_*` macros that expect the generated names to exist with the `HUBP0`/`HUBPREQ0`/`CURSOR0_0` token forms.
- The generic register helpers in `reg_helper.h` consume the populated shift/mask fields for MMIO reads and updates.
- Higher-level display workflows integrate through plane programming, page flips, cursor updates, DMDATA metadata programming, VM fault handling, watermarks/DLG/TTU calculation, suspend/resume restore, and underflow diagnostics.
- IRQ metadata under `include/ivsrcid/dcn/irqsrcs_dcn_1_0.h` names related HUBP flip, flip-away, VM-context-error, vblank/vline, and perfcounter interrupt sources for instances 1-3; this header provides the bitfield side for some per-block interrupt/status registers.

The key integration contract is preprocessor naming plus numeric correctness. Missing or renamed macros usually break compilation when resource tables are built. Wrong masks or shifts can compile and only fail as incorrect hardware behavior on a specific pipe.

## Risks And Edge Cases

- The chunk boundaries are partial. It starts after the beginning of `HUBP1_DCSURF_ADDR_CONFIG` and ends inside `HUBPRET3_HUBPRET_MEM_PWR_CTRL`; final per-file reconciliation must combine adjacent chunks before claiming complete coverage of those two register groups.
- Instance replication hides drift. HUBP/HUBPREQ/HUBPRET/cursor/perfmon blocks for instances 1, 2, and 3 are mechanically similar, so a one-bit error in one instance may appear as a pipe-specific display failure rather than a compile-time problem.
- Shift/mask errors in address, VMID, TMZ, DCC, and metadata fields can cause scanout from the wrong memory, incorrect protected-memory handling, bad DCC interpretation, VM faults, or stale metadata fetches.
- Flip-control fields mix controls and status. Mispacking `SURFACE_UPDATE_LOCK`, `SURFACE_FLIP_PENDING`, stereo-sync fields, GSL, or triple-buffer fields can deadlock updates, miss vblank synchronization, or produce stale scanout.
- Several registers pack luma and chroma values together. Mistakes in `_C` fields, viewport fields, pitch fields, and chroma timing fields can affect multi-plane formats such as NV12/P010 differently from RGB formats.
- Timing fields are tightly width-limited, often using 7-bit, 13-bit, 17-bit, 21-bit, or 23-bit masks. Callers must clamp/calibrate values before packing; this header only supplies masks and cannot validate display-mode math.
- Clear/ack/status fields such as underflow clear, timeout clear, flip interrupt clear, DMDATA VM fault clear, DMDATA underflow clear, read-line interrupt clear, and perfcounter interrupt ack have side effects. Treating them like ordinary persistent configuration can clear evidence or leave interrupts stuck.
- Cross-generation reuse is risky. Nearby DCN 3.2+ headers add or rename some HUBP fields such as soft reset, unbounded request mode, segment allocation error, or cursor request mode. DCN 3.0.2 code must use the header matching its offset table and ASIC resource path.
- Full-register masks such as surface address low words and perfmon low-value words require unsigned 32-bit handling. Sign extension or host-width assumptions around `0xFFFFFFFFL` can distort debug or register-composition code on unusual build targets.

## Test Signals

Build-time signals:

- Compile DCN 3.0.2 AMD display resource and HUBP code that includes `dcn_3_0_2_sh_mask.h`; missing generated names should surface through `HUBP_REG_LIST_DCN30` and `HUBP_MASK_SH_LIST_DCN30` expansion.
- Preprocess `dcn302_resource.c` to confirm `hubp_shift` and `hubp_mask` resolve the expected `HUBP*`, `HUBPREQ*`, and `CURSOR0_*` macros against `dcn_3_0_2_offset.h`.
- Statically compare this generated header with the authoritative register database and adjacent instance blocks to catch one-instance mask/shift drift.

Runtime and hardware signals:

- Exercise multi-pipe scanout on DCN 3.0.2 hardware, especially pipes 1-3, with RGB and multi-plane YUV formats to validate viewport, pitch, chroma, DCC, and address fields.
- Run page-flip tests with immediate, vblank-synchronized, stereo-sync, GSL, and triple-buffer paths; monitor `SURFACE_FLIP_PENDING`, flip interrupts, and in-use/earliest-in-use address readbacks.
- Move and resize hardware cursors, enable/disable cursor surfaces, and exercise DMDATA hardware/software modes while checking `DMDATA_DONE`, underflow, QoS, address, and update toggles.
- Validate underflow handling by checking `HUBP_UNDERFLOW_STATUS` and `HUBP_UNDERFLOW_CLEAR`, plus timeout status/clear behavior if the platform exposes it.
- Test modes with different timing and memory-pressure profiles to verify DLG/TTU fields: prefetch ratio, vblank/flip/nominal PTE/meta/VM group cycles, per-line delivery, and DRQ limit.
- Exercise suspend/resume, display reset, and power-gating paths while watching HUBP/HUBPREQ/HUBPRET/cursor memory-power status fields and restored plane/cursor state.
- Use perfmon/debug tooling, where available, to program `DC_PERFMON7` and `DC_PERFMON8` counters, verify interrupt ack/status behavior, and confirm readback high/low values increment for selected events.

## Open Cross-Chunk Questions

- The previous chunk should be merged with this one to present the complete `HUBP1_DCSURF_ADDR_CONFIG` field group.
- The next chunk should be merged with this one to present complete `HUBPRET3_HUBPRET_MEM_PWR_CTRL` and the remaining HUBPRET3 read-line/interrupt/status groups.
- Whole-file reconciliation should verify whether all expected DCN 3.0.2 HUBP instances are present and whether the repeated instance layouts are intentionally identical or contain ASIC-specific deltas.

### subset-b-001756: lines 12327-14847

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 12327-14847

## Scope

This chunk is a generated AMD DCN 3.0.2 ASIC register bitfield header segment. It contains preprocessor constants only: for each hardware register field, a `__SHIFT` macro gives the bit offset and a `_MASK` macro gives the bit mask. The chunk spans 2,521 source lines and contains 2,112 `#define` entries, including 1,054 shift definitions and 1,072 mask definitions. It starts in the tail of the `HUBPRET3` block and ends at the start of `CM0_CM_BLNDGAM_RAMA_REGION_6_7`, so both the opening and closing register families require adjacent chunks for full register coverage.

The covered surface is DCN display-pipe local MMIO state for HUBP/HUBPREQ/HUBPRET/cursor/perfmon instances 3 and 4, plus the beginning of DPP0 conversion, scaler, and color-management masks. There are no C functions, structs, or executable branches in this header chunk; its effective API is the generated macro namespace consumed by AMDGPU display resource construction and register helper tables.

## Purpose

The purpose of this header segment is to expose symbolic bit positions for DCN 3.0.2 display pipeline programming. Driver code includes this file with `dcn_3_0_2_offset.h` and uses the macros through register helper table builders such as `HUBP_MASK_SH_LIST_DCN30(__SHIFT)`, `HUBP_MASK_SH_LIST_DCN30(_MASK)`, `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)`, and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)`. Those tables let runtime code perform field-safe `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and direct read/write operations without embedding literal bit positions.

For this chunk, the main hardware purposes are:

- tracking HUBP read-line interrupts and memory power for pipe 3;
- programming cursor and display metadata fetches for pipe 3 and pipe 4;
- programming HUBP4 surface layout, tiling, viewport, surface address, flip, DCC/TMZ, VMID, request-size, timing, QoS, prefetch, TTU, VM, and low-power controls;
- exposing DC performance counter controls for the HUBP side of pipe 3 and pipe 4;
- programming the first DPP instance's top control, pixel-format conversion, cursor conversion overlay, scaler, line buffer, post/pre color-space conversion, gamut remap, gamma correction LUTs, and the beginning of blend-gamma LUTs.

## Address Blocks And Register Surface

The chunk begins inside the `dce_dc_dcbubp3_dispdec_hubpret_dispdec` block, continuing `HUBPRET3` definitions for memory power, read-line windows, read-line interrupt mask/type/clear/status fields, current read-line value, snapshot, and read-line status.

Visible address blocks then include:

- `dce_dc_dcbubp3_dispdec_cursor0_dispdec`: `CURSOR0_3_*` cursor surface, size, position, hotspot, stereo, memory power, and `DMDATA` metadata registers.
- `dce_dc_dcbubp3_dispdec_hubp_dcperfmon_dc_perfmon_dispdec`: `DC_PERFMON9_*` counter control, state, control/status, and counter-value masks.
- `dce_dc_dcbubp4_dispdec_hubp_dispdec`: `HUBP4_*` surface config, tiling, viewports, request-size, enable/blank/underflow control, clock, VM page config, and measurement windows.
- `dce_dc_dcbubp4_dispdec_hubpreq_dispdec`: `HUBPREQ4_*` surface pitch, VMID, primary/secondary and chroma surface/meta addresses, flip control, flip interrupt, current and earliest in-use addresses, expansion, QoS/TTU, VM controls, timing model parameters, prefetch, cursor timing, and memory power.
- `dce_dc_dcbubp4_dispdec_hubpret_dispdec`: `HUBPRET4_*` crossbar/packing/det-buffer control, memory power, read-line windows, interrupt/status, and read-line value.
- `dce_dc_dcbubp4_dispdec_cursor0_dispdec`: `CURSOR0_4_*` cursor and `DMDATA` metadata registers mirroring the pipe-3 cursor block.
- `dce_dc_dcbubp4_dispdec_hubp_dcperfmon_dc_perfmon_dispdec`: `DC_PERFMON10_*` counter register masks.
- `dce_dc_dpp0_dispdec_dpp_top_dispdec`: `DPP_TOP0_*` DPP clock/control, soft reset, CRC values, CRC control, and host read control.
- `dce_dc_dpp0_dispdec_cnvc_cfg_dispdec`: `CNVC_CFG0_*` pixel format, format control, FP bias/scale, color keyer, alpha LUT, pre-dealpha, pre-CSC matrices, coefficient format, pre-degamma, and pre-realpha.
- `dce_dc_dpp0_dispdec_cnvc_cur_dispdec`: `CNVC_CUR0_*` DPP-side cursor control, colors, and FP scale/bias.
- `dce_dc_dpp0_dispdec_dscl_dispdec`: `DSCL0_*` scaler coefficient RAM, mode, taps, control, two-tap control, manual replicate, ratios, init values, black color, update, autocal, overscan, OTG blanking, recout, MPC size, line-buffer, memory power, output buffer, and line-buffer counters.
- `dce_dc_dpp0_dispdec_cm_dispdec`: `CM0_*` color-management control, post-CSC, gamut remap, bias, gamma-correction LUT, gamma RAM A/B region programming, and the beginning of blend-gamma RAM A programming.

## Important Macro Families

`HUBPRET3_*` and `HUBPRET4_*` describe the post-request HUBP return path. The important fields are memory power force/disable/low-power-state controls for DET, DMROB, and PIXCDC memory; read-line programming for two line windows; interrupt mask/type/clear/status bits for vblank/read-line events; read-line current/snapshot values; and crossbar/pack controls in `HUBPRET4_HUBPRET_CONTROL`.

`CURSOR0_3_*` and `CURSOR0_4_*` expose cursor fetch and placement state. They include enable, 2x magnify, mode, TMZ, snoop/system, pitch, rotation/mirror bypass, lines per chunk, perfmon latency controls, 48-bit surface address fields, width/height, x/y position, hotspot, stereo offsets, destination x offset, cursor memory power, and DMDATA address/control/QoS/status/software-data fields.

`HUBP4_*` defines front-end HUBP surface interpretation for pipe 4: pixel format, rotation, horizontal mirror, alpha plane enable, address config (`NUM_PIPES`, `PIPE_INTERLEAVE`, compressed fragments, packers), tiling (`SW_MODE`, `META_LINEAR`, `PIPE_ALIGNED`), primary/secondary and chroma viewports, request-size grouping, blank/underflow/disable/VTG selection, clock enable/force-on, VM page config, and DCFCLK/DPPCLK measurement windows.

`HUBPREQ4_*` defines the request-generation and flip side of pipe 4. It covers pitch/meta pitch, VMID, primary/secondary surface and meta-surface base addresses for luma and chroma, TMZ/DCC surface-control bits, flip type/mode/pending/lock/triple-buffer/GSL controls, flip interrupt status/clear/mask, in-use and earliest-in-use address snapshots, request expansion modes, TTU QoS watermarks, per-surface and cursor delivery timing, metadata VM control/status/clear bits, system aperture and L1 TLB controls, blank offsets, destination timing, prefetch ratios, vblank/flip/nominal timing parameters, per-line delivery, cursor timing, and HUBPREQ memory power.

`DC_PERFMON9_*` and `DC_PERFMON10_*` expose the local display performance counters attached to HUBP instances. They include per-counter enable, clear, mode, state, counter selection, enable window, counter-off trigger, stopped/started flags, count-enable/status, high/low value, overflow, and event generation controls.

`DPP_TOP0_*`, `CNVC_CFG0_*`, and `CNVC_CUR0_*` are DPP instance 0 front-end controls. They cover DPP clock enable and disable gating, soft reset, CRC readback, host-read path, surface pixel format, conversion bypass/expansion/output FP and alpha enable, floating-point conversion bias/scale, color keying, alpha LUT, pre-dealpha/realpha, pre-CSC matrices for normal and B components, pre-degamma mode/select, and DPP-side cursor color/format.

`DSCL0_*` defines the scaler and line buffer. Important fields include coefficient RAM pair/phase/filter type and even/odd coefficient writes, scaler mode/current mode, chroma coefficient mode, taps, boundary mode, two-tap hardcode/sharpen controls, manual replicate controls, fixed-point horizontal/vertical luma/chroma ratios and initial phases, black color, update/autocal controls, overscan, OTG blank windows, recout and MPC dimensions, line-buffer format/memory configuration, LUT and OBUF memory power, and line-buffer v-counter readback.

`CM0_*` in this chunk covers DPP0 color management. It exposes CM enable and post-CSC enable/mode/current fields, post-CSC and gamut-remap matrices, per-component bias, gamma correction control and LUT index/data/control fields, gamma RAM A/B start/end/base/slope/offset/region definitions, and blend-gamma control plus the beginning of blend-gamma RAM A definitions.

## Control Flow And Runtime Behavior

There is no direct control flow in this file segment. Runtime behavior is indirect through AMDGPU display code that maps these constants into typed register tables.

The relevant integration path for this ASIC is `display/dc/resource/dcn302/dcn302_resource.c`, which includes `dcn/dcn_3_0_2_offset.h` and `dcn/dcn_3_0_2_sh_mask.h`. In `dcn302_hubp_create()`, the resource code builds `hubp_regs[]`, `hubp_shift`, and `hubp_mask`, then calls `hubp3_construct()`. In `dcn302_dpp_create()`, it builds `dpp_regs[]`, `tf_shift`, and `tf_mask`, then calls `dpp3_construct()`. The current chunk supplies the instance-4 register field values for the HUBP tables and the instance-0 DPP field values for the DPP tables.

Hardware flows represented by the bitfields include:

- Surface programming: HUBP/HUBPREQ macros define surface format, tiling, pitch, viewport, surface addresses, meta addresses, DCC enablement, TMZ bits, VMID, and aperture/TLB state before a plane can fetch pixels.
- Flip sequencing: `HUBPREQ4_DCSURF_FLIP_CONTROL*`, surface in-use snapshots, flip interrupt fields, and flip/vblank timing parameters support immediate, vblank, stereosync, triple-buffer, and GSL-related flip behavior.
- Cursor and metadata fetch: `CURSOR0_3_*`, `CURSOR0_4_*`, `HUBPREQ4_CURSOR_SETTINGS`, and `DMDATA` fields define cursor memory fetches, cursor placement, display metadata address/control, DMDATA repeat/update/mode, QoS, VM timing, and status/underflow signals.
- Bandwidth and timing model programming: `HUBPREQ4_DCN_*`, `VBLANK_PARAMETERS_*`, `FLIP_PARAMETERS_*`, `NOM_PARAMETERS_*`, `PER_LINE_DELIVERY*`, `PREFETCH_SETTINGS*`, and TTU controls carry the computed display-mode timing values from the display mode library and watermarks into hardware.
- Scaler programming: DPP scaler code chooses a DSCL mode, programs line-buffer format and partitioning, writes coefficient RAM through `SCL_COEF_RAM_TAP_SELECT`/`SCL_COEF_RAM_TAP_DATA`, swaps coefficient RAM using `SCL_COEF_RAM_SELECT`, sets ratios/init phases, and programs taps/two-tap sharpening through `DSCL0_*` fields.
- Color pipeline programming: DPP code reads and writes `DPP_CONTROL`, `CNVC_SURFACE_PIXEL_FORMAT`, `FORMAT_CONTROL`, pre/post CSC, gamut-remap, pre-degamma, gamma-correction RAM, and blend-gamma registers while applying per-plane color transforms and gamma LUTs.
- Power and low-power control: HUBPREQ/HUBPRET/CURSOR/DSCL memory power fields, clock control fields, and DPP clock/reset fields participate in display pipe power gating, memory low-power entry, and resume/reprogram paths.

## State And Persistence

The macros do not store mutable software state. They describe persistent hardware state in memory-mapped registers. Values written through fields in this chunk persist until rewritten, reset by the display block, or reinitialized during suspend/resume, modeset, power-gating, or GPU reset.

Several field classes represent latched or handshake state:

- Flip and address state: `SURFACE_FLIP_PENDING`, `SURFACE_FLIP_IN_STEREOSYNC`, in-use address readbacks, earliest-in-use address readbacks, and `HUBPREQ_MASTER_UPDATE_LOCK_STATUS` expose asynchronous surface update state.
- Interrupt and clear state: `PIPE_VBLANK_INT_*`, `PIPE_READ_LINE*_INT_*`, `SURFACE_FLIP_INT_*`, and DMDATA underflow clear fields require hardware-specific acknowledgement semantics. The mask constants alone do not encode whether a field is write-one-to-clear, level, edge, or read-only.
- VM and DMDATA status: `DMDATA_VM_FAULT_STATUS`, `DMDATA_VM_UNDERFLOW_STATUS`, `DMDATA_VM_LATE_STATUS`, status-clear fields, `DMDATA_VM_DONE`, `DMDATA_DONE`, and `DMDATA_UNDERFLOW` reflect metadata fetch status and error state.
- Memory power state: `*_MEM_PWR_FORCE`, `*_MEM_PWR_DIS`, `*_MEM_PWR_LS_MODE`, and `*_MEM_PWR_STATE` fields expose low-power controls/status for HUBPREQ, HUBPRET, cursor, DSCL LUT/line buffer/output-buffer, and color-management RAMs.
- Double-buffered LUT state: gamma and blend-gamma control fields include active/current selector fields and LUT index/data/control state; software typically alternates RAMs or updates host-selected LUTs before selecting the active bank.
- Performance counter state: `DC_PERFMON*_PERFCOUNTER_STATE`, `PERFMON_*_STARTED`, `STOPPED`, `OVERFLOW`, and high/low counter registers are readback state controlled by counter enable/clear fields.

## Dependencies And Integration Points

This header depends on the matching generated DCN 3.0.2 offset header for register addresses and on display-core register helper macros that combine register addresses, masks, and shifts. The same generated naming convention is used across `dcn302_resource.c`, HUBP headers, DPP headers, IRQ sources, and lower-level `reg_helper.h` accessors.

Concrete integration points visible in the source tree:

- `display/dc/resource/dcn302/dcn302_resource.c` includes this file and constructs DCN 3.0.2 resource objects for HUBP and DPP instances. Its `hubp_shift`/`hubp_mask` and `tf_shift`/`tf_mask` structures are populated from the macros in this header.
- `display/dc/hubp/dcn30/dcn30_hubp.h` defines `HUBP_MASK_SH_LIST_DCN30`, which references many fields present here, including `HUBPREQ0_*`, `HUBP0_*`, `HUBPRET0_*`, and `CURSOR0_0_*`. The generated per-instance names (`HUBPREQ4_*`, `HUBP4_*`, `HUBPRET4_*`, `CURSOR0_4_*`) are selected through the corresponding register-list address table.
- `display/dc/hubp/dcn10/dcn10_hubp.c` contains runtime behavior for HUBP request/read-line and debug DB handling, using the same field names abstracted by the table.
- `display/dc/dpp/dcn30/dcn30_dpp.h` defines DPP register and shift/mask lists for DCN 3.0. The DPP0 macros in this chunk satisfy the fields used by DCN 3.0.2 `dpp3_construct()`.
- `display/dc/dpp/dcn10/dcn10_dpp.c` consumes conversion and color-management fields such as `DPP_CONTROL`, `CM_GAMUT_REMAP_CONTROL`, `FORMAT_CONTROL`, `CNVC_SURFACE_PIXEL_FORMAT`, `CURSOR_CONTROL`, and `CURSOR0_CONTROL`.
- `display/dc/dpp/dcn10/dcn10_dpp_dscl.c` consumes scaler fields such as `DSCL_MEM_PWR_CTRL`, `DSCL_MEM_PWR_STATUS`, `LB_DATA_FORMAT`, `LB_MEMORY_CTRL`, `SCL_COEF_RAM_TAP_SELECT`, `SCL_COEF_RAM_TAP_DATA`, `DSCL_2TAP_CONTROL`, `SCL_MODE`, `SCL_TAP_CONTROL`, ratios, init values, recout, and MPC size.
- `display/dc/irq/dcn302/irq_service_dcn302.c` uses HUBPREQ interrupt register mappings for flip interrupt sources. This chunk's `HUBPREQ4_DCSURF_SURFACE_FLIP_INTERRUPT` masks provide the pipe-4 field definitions for that interrupt class.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong mask or shift can silently alter unrelated bits in a 32-bit MMIO register, causing incorrect surface fetches, cursor corruption, color errors, scaler artifacts, VM faults, hangs, or display underflow.
- The chunk starts in the middle of `HUBPRET3` and ends immediately after the `CM0_CM_BLNDGAM_RAMA_REGION_6_7` comment. Merge/reconciliation must combine adjacent chunks before making whole-block completeness claims.
- Instance families are highly repetitive. `HUBP4`, `HUBPREQ4`, `HUBPRET4`, and `CURSOR0_4` should parallel lower instances, but assuming exact parity can hide valid per-ASIC or per-instance differences. Consistency checks should compare against the generated offset header and hardware spec, not only against nearby instances.
- Field names that themselves end in `MASK`, `STATUS`, or `CLEAR` can produce ambiguous macro names such as interrupt mask masks or status-clear masks. Tooling that naively splits on `_MASK` or assumes `CLEAR` fields are always write-one-to-clear can misparse semantics.
- Several fields expose security and memory-routing controls (`TMZ`, `SNOOP`, `SYSTEM`, surface metadata TMZ, VMID, aperture, TLB, DMDATA VM status). Incorrect values can route fetches through the wrong memory path or break protected-content behavior.
- Gamma and scaler LUT programming depends on correct bank/index/data sequencing. A correct bit mask does not ensure safe ordering; runtime code must respect current-bank selectors, host selection, and update timing to avoid visible artifacts.
- Power-state controls are easy to misuse. Forcing memories off, selecting low-power states, or disabling clocking while a pipe is active can manifest as intermittent blanking, underflow, or stale status reads rather than immediate compile failures.
- DC performance counter controls are diagnostic but still stateful; incorrect clear/enable/mode masks can corrupt performance telemetry and make display underflow or bandwidth regressions harder to diagnose.

## Test Signals

Useful validation for this chunk is a mix of generated-header checks, compile coverage, and hardware/display regression signals:

- Build AMDGPU display with DCN 3.0.2 enabled so `dcn302_resource.c`, HUBP, DPP, IRQ, and register-helper consumers compile against these macro names.
- Run generated consistency checks that each visible `__SHIFT` field has a matching mask where expected, masks fit within 32 bits, and repeated instance blocks preserve intended parity with `HUBP0`-`HUBP4`, `HUBPREQ0`-`HUBPREQ4`, `HUBPRET0`-`HUBPRET4`, and `CURSOR0_0`-`CURSOR0_4`.
- Exercise modesets on DCN 3.0.2 hardware with plane enable/disable, format changes, tiling/DCC, rotation/mirror, alpha planes, protected surfaces, immediate and vblank flips, triple buffering, cursor movement, cursor format changes, and DMDATA/HDR metadata updates.
- Stress bandwidth-sensitive scenarios that validate TTU/QoS/prefetch/vblank/flip/nominal timing fields: high-resolution scanout, multi-plane overlays, chroma planes, scaling, fast page flips, and memory clock transitions.
- Validate scaler output for bypass, 444 RGB/YCbCr scaling, 420 luma/chroma modes, two-tap sharpening, coefficient RAM updates, line-buffer partition choices, and DSCL low-power entry/exit.
- Validate color behavior through pre-CSC, post-CSC, gamut remap, pre-degamma, gamma correction RAM A/B selection, blend-gamma RAM programming, cursor color, color keying, and FP16/fixed format conversion.
- Monitor runtime error/status signals: HUBP underflow, flip pending not clearing, surface flip interrupt delivery, DMDATA done/underflow/VM fault/late status, read-line/vblank interrupt status, line-buffer state, DSCL/CM memory power state, and DC_PERFMON overflow/counter state.
- Include suspend/resume, display hotplug, runtime power management, and pipe power-gating tests to ensure persistent register state is reprogrammed or safely reset.

## Open Questions For Merge Lane

- Confirm the previous chunk contains the start of `HUBPRET3_HUBPRET_MEM_PWR_CTRL`; this chunk begins at `DMROB_MEM_PWR_DIS__SHIFT`, not at the register comment.
- Confirm the next chunk completes `CM0_CM_BLNDGAM_RAMA_REGION_6_7` and the rest of blend-gamma RAM A/B fields before the final file report summarizes the full DPP0 color-management surface.
- Compare DCN 3.0.2 masks against `dcn_3_0_2_offset.h` and equivalent DCN 3.0/3.0.1/3.0.3 generated headers to identify intentional ASIC differences versus generation drift.

### subset-b-001757: lines 14848-17356

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 14848-17356

## Scope

This chunk is a generated AMD DCN 3.0.2 ASIC register shift/mask header segment. It contains preprocessor constants only: every hardware register field is represented by a `__SHIFT` macro and a matching `_MASK` macro. The slice spans 2,509 source lines and contains 2,113 `#define` entries across 379 register symbols. It starts inside the `CM0_CM_BLNDGAM_RAMA_REGION_6_7` field list and ends inside `CM1_CM_BLNDGAM_RAMB_REGION_24_25`, so both boundaries are partial register groups that must be reconciled with neighboring chunks for complete file-level coverage.

## Purpose

The purpose of this header segment is to expose symbolic bit locations for DCN 3.0.2 display pipe programming. Driver code does not hand-code these bit offsets directly; it includes generated `*_sh_mask.h` headers and feeds the `__SHIFT`/`_MASK` constants into AMDGPU display register helper tables. The covered hardware is mostly display pipe processor (DPP) color-management, converter, scaler, cursor, and diagnostics state for DPP instance 0 and DPP instance 1.

This chunk is data-like source rather than executable logic. Its correctness depends on exact agreement with the matching DCN 3.0.2 register specification and the companion `dcn_3_0_2_offset.h` address header. A wrong value here changes how runtime code masks or shifts MMIO fields.

## Address Blocks And Register Surface

The visible address blocks are:

- `dce_dc_dpp0_dispdec_cm_dispdec` tail: end of `CM0` blend-gamma RAM A, full blend-gamma RAM B region descriptors, CM0 shaper, CM0 3D LUT, memory-power, debug, and HDR multiplier controls.
- `dce_dc_dpp0_dispdec_dpp_dcperfmon_dc_perfmon_dispdec`: `DC_PERFMON11` counter control, state, counter values, and performance-monitor compare/value registers.
- `dce_dc_dpp1_dispdec_dpp_top_dispdec`: `DPP_TOP1` pipe-level enable/reset and DPP CRC controls/status.
- `dce_dc_dpp1_dispdec_cnvc_cfg_dispdec`: `CNVC_CFG1` input format, expansion, pre-CSC, pre-degamma, pre-dealpha/pre-realpha, color key, alpha LUT, and FP scale/bias fields.
- `dce_dc_dpp1_dispdec_cnvc_cur_dispdec`: `CNVC_CUR1` cursor enable/mode/color/floating-point scale-bias fields.
- `dce_dc_dpp1_dispdec_dscl_dispdec`: `DSCL1` scaler coefficient RAM, mode, taps, filter ratios/initial phases, recout/MPC dimensions, line-buffer, memory-power, OBUF, and OTG blanking fields.
- `dce_dc_dpp1_dispdec_cm_dispdec`: start of the `CM1` color-management block, including control, post-CSC, gamut-remap, bias, gamma-correction RAM A/B, and blend-gamma RAM A/B definitions through the partial `Ramb region 24/25` block.

By counted prefix, the chunk includes 718 `CM0_CM*` definitions, 126 `DC_PERFMON11*` definitions, 56 `DPP_TOP1*` definitions, 154 `CNVC_CFG1/CNVC_CUR1*` definitions, 200 `DSCL1*` definitions, and 859 `CM1_CM*` definitions.

## Important Macro Families

The `CM0_CM_BLNDGAM_*` and `CM1_CM_BLNDGAM_*` groups describe blend/output gamma LUT control and piecewise-linear RAM metadata. The visible fields cover mode/current-select bits, LUT index/data/control, RAM A and RAM B start/end/offset registers, per-channel B/G/R start values, start segments, start slopes, start bases, end bases, end slopes, and dense region descriptors. Region registers pack two regions per register, each with a 9-bit LUT offset and 3-bit segment count.

The `CM0_CM_SHAPER_*` group describes the shaper LUT path for DPP0. It includes shaper control and status/current mode, per-channel offsets and scales, LUT index/data/write mask, RAM A/B start/end registers, and shaper region descriptors. These fields are used with 3D LUT programming because the shaper prepares color values before 3D LUT lookup.

The `CM0_CM_3DLUT_*` group describes 3D LUT mode, host index/data access, 30-bit data path fields, read/write controls, output normalization factor, and RGB output offsets. The read/write control fields include configuration status, mode, read selection, width, and 30-bit enable state.

The `CM1_CM_GAMCOR_*` group describes the DPP1 gamma-correction RAM. It mirrors the blend-gamma PWL layout with RAM A/B start, base, slope, end, offset, and region registers, plus LUT index/data/control and mode/current-select fields.

The `CM1_CM_POST_CSC_*` and `CM1_CM_GAMUT_REMAP_*` groups describe color matrix programming. Each matrix register packs coefficient pairs such as `C11/C12` through `C33/C34`, and there are A/B or current/alternate coefficient banks so the driver can stage updates before switching modes.

The `CNVC_CFG1_*` groups describe DPP1 input conversion. They cover source pixel format, expansion, bypass, alpha enable, 16-bit conversion format, component crossbar, positive clamp, pre-CSC matrix banks, pre-degamma select, pre-dealpha and pre-realpha control, fixed-point conversion scale/bias, color-key ranges, and a packed 2-bit alpha LUT.

The `CNVC_CUR1_*` groups describe cursor format and color controls for DPP1. Fields include cursor enable, mode, expansion, ROM enable, pixel inversion, pixel alpha modulation, two cursor colors, and FP scale/bias.

The `DSCL1_*` groups describe scaler and line-buffer programming. They include coefficient RAM tap select/data, scaler mode and coefficient-bank select, horizontal/vertical/chroma tap counts, 2-tap hardcoded/sharp controls, manual replicate controls, scale ratios, initial phases, recout rectangle, MPC size, line-buffer data format and memory configuration, DSCL update/autocal controls, OTG blanking, memory-power, and OBUF state.

The `DPP_TOP1_*` and `DC_PERFMON11_*` groups describe diagnostics and status rather than color math. `DPP_TOP1` includes pipe clock enable, soft reset, host-read and CRC control/result fields. `DC_PERFMON11` includes counter enable/clear/selection, perfmon state, mode, windowing, high/low counter values, and compare/mask values.

## Integration Points

The main runtime integration path is through generated register tables in AMDGPU display code. For DCN 3.0-style DPPs, `display/dc/dpp/dcn30/dcn30_dpp.h` defines `DPP_REG_LIST_DCN30*` and `DPP_REG_LIST_SH_MASK_DCN30*` macros. Those macros name fields such as `CM0_CM_BLNDGAM_CONTROL__CM_BLNDGAM_MODE`, `CM0_CM_3DLUT_MODE__CM_3DLUT_MODE_CURRENT`, `CNVC_CFG0_FORMAT_CONTROL__FORMAT_EXPANSION_MODE`, and `DSCL0_SCL_MODE__DSCL_MODE`; instance-specific address macros then map the same field layout onto each DPP instance. The generated `__SHIFT` and `_MASK` constants in this chunk are the low-level values assigned into the `dcn3_dpp_shift` and `dcn3_dpp_mask` structures.

`display/dc/resource/dcn30/dcn30_resource.c` is the resource-construction side of that integration. It includes DCN offset and sh/mask headers, builds DPP register-address arrays with `DPP_REG_LIST_DCN30(id)`, and builds shift/mask tables with `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)`. DCN 3.0.2-specific resource code follows the same pattern with the DCN 3.0.2 generated headers.

`display/dc/dpp/dcn30/dcn30_dpp.c` is the direct consumer pattern. It reads and writes these fields through `REG_GET`, `REG_GET_2`, `REG_SET`, `REG_SET_2`, `REG_UPDATE`, and `REG_READ`. Examples include `dpp30_read_state()` reading DPP enable, pre-degamma, gamma-correction current mode, shaper mode, 3D LUT mode/bit depth/size, and blend-gamma current mode; `dpp3_program_post_csc()` selecting between CSC banks and programming coefficient registers; and DPP scaler/converter functions programming format, pre-degamma, cursor, recout, filter ratios, taps, and line-buffer state.

The helper layer comes from `reg_helper.h` and associated display core code. Those helpers combine an MMIO register address, a field mask, and a field shift to perform read-modify-write or extraction. The macros in this chunk therefore become part of the ABI between generated hardware descriptions and typed DC driver structures.

## Control Flow And Runtime Behavior

There is no C control flow in this header chunk. The represented runtime flows are indirect:

- DPP construction selects the DCN 3.0.2 register address and shift/mask tables for a specific pipe instance.
- DPP state readback extracts status/current fields from registers, such as DPP clock enable, shaper/3D LUT/gamma modes, memory-power state, scaler mode, recout size, and OBUF state.
- Color-management programming writes staged coefficient or LUT data into CM registers, then switches mode/select fields so hardware uses the intended RAM or matrix bank.
- Converter setup writes pixel format, alpha, expansion, crossbar, pre-CSC, pre-degamma, pre-dealpha/pre-realpha, color-key, cursor, and fixed-point conversion fields.
- Scaler setup writes tap counts, coefficient RAM entries, filter ratios, initial phases, recout/MPC dimensions, line-buffer partitioning, autocal, update, and memory-power controls.
- Diagnostics paths may enable DPP CRC or DC performance counters, read low/high counter values, and clear or reset state.

The double-buffering pattern is important even though it is not implemented here. Several mode/current, select/current, and A/B matrix/RAM field pairs imply that driver code writes an inactive bank, then flips a control selector so the new color transform takes effect on a safe hardware boundary.

## State And Persistence

The macros themselves hold no mutable software state. They describe persistent hardware state in memory-mapped registers. Once the driver writes fields described here, the device state persists until another write, a block reset, a full display reinitialization, suspend/resume restore, or GPU reset.

Important state categories exposed by this slice:

- LUT and PWL state: blend-gamma, gamma-correction, shaper, and 3D LUT fields define visible color output. Bad persistence or failed restore can cause wrong gamma, HDR tone mapping, or color-space conversion after mode changes and resume.
- Bank/current state: `*_MODE_CURRENT`, `*_SELECT_CURRENT`, and current coefficient-bank fields expose which staged bank hardware is actually using.
- Memory-power state: `CM_MEM_PWR_CTRL`, `CM_MEM_PWR_STATUS`, `CM_MEM_PWR_CTRL2`, `CM_MEM_PWR_STATUS2`, `DSCL_MEM_PWR_CTRL`, `DSCL_MEM_PWR_STATUS`, `LB_MEMORY_CTRL`, and `OBUF_MEM_PWR_CTRL` affect whether LUT, shaper, 3D LUT, line-buffer, scaler, and output-buffer memories are powered or forced.
- Status and clear state: DPP CRC status, soft reset, performance counter state, autocal status, update pending/taken, and host-read controls represent transient hardware handshakes.
- Cursor/converter/scaler state: CNVC and DSCL fields define the active surface interpretation, cursor appearance, scaling geometry, and filtering.

## Dependencies

This chunk depends on companion generated DCN 3.0.2 headers for register addresses and base indices, especially the matching `dcn_3_0_2_offset.h`. It also depends on the AMD display register-helper convention where `REG_FIELD` tables contain masks and shifts in separate structures. Macro naming must match the typed field names in DPP headers; a mismatch is a compile-time failure when referenced, while a numerically wrong mask/shift can compile cleanly and break runtime hardware programming.

The hardware semantics are outside this file. The header gives bit positions only; it does not describe write-one-to-clear behavior, double-buffer timing, reset sequencing, memory-power timing, or legal enum values for mode fields. Runtime code must get those semantics from the DPP implementation and hardware spec.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A single wrong mask or shift can corrupt adjacent fields in a 32-bit MMIO register, causing color corruption, scaler misprogramming, cursor artifacts, CRC/test failures, memory-power issues, or display blanking.
- The chunk boundaries are partial. The first visible definitions are the tail of `CM0_CM_BLNDGAM_RAMA_REGION_6_7`; the final visible definition starts `CM1_CM_BLNDGAM_RAMB_REGION_24_25`. Merge/reconciliation must include adjacent chunks before making completeness claims.
- Instance parity is easy to assume incorrectly. `CM0` and `CM1`, `CNVC_CFG0/1`, and `DSCL0/1` are structurally similar, but the actual generated macros are instance-qualified and may differ across ASIC revisions or block revisions.
- Dense repeated PWL region definitions are off-by-one sensitive. Region registers encode pairs such as regions 0/1, 2/3, ..., 32/33. Consumers that calculate offsets or generate arrays must preserve the exact register/field pairing.
- Fields whose logical names contain `MASK` generate macro names ending in `_MASK_MASK`, such as LUT write-enable masks. Parsers or validators that strip `_MASK` naively can misidentify these names.
- Hardware-current fields are readback/status-oriented. Writing only the desired mode field and then immediately trusting the corresponding current field without respecting update boundaries can create races in diagnostics or tests.
- Memory-power controls are shared with LUT and scaler programming. Powering a memory block down while a LUT/scaler path still expects it can produce nondeterministic display output or stale readback.

## Test Signals

Useful validation signals for this chunk are mostly build-time, generated-header consistency, and hardware-display regression signals:

- Compile DCN 3.0.2 AMDGPU display paths so all referenced DPP, CM, CNVC, DSCL, DPP_TOP, and PERFMON field names resolve.
- Run a generated-header consistency check that every field has both `__SHIFT` and `_MASK`, masks fit within 32 bits, and paired region registers use the expected offset/segment bit positions.
- Compare DCN 3.0.2 masks against the matching offset header and against adjacent DCN 3.0.x revisions to catch accidental drift in repeated CM/CNVC/DSCL blocks.
- Exercise display mode changes with scaling enabled, bypass scaling, 4:4:4 and 4:2:0 formats, cursor enable/disable, color-keying, alpha formats, and FP formats.
- Exercise color-management paths: pre-degamma, post-CSC, gamut remap, gamma-correction RAM A/B, blend-gamma RAM A/B, shaper LUT, 3D LUT, HDR multiplier, and bank switching.
- Exercise suspend/resume, display off/on, and memory-power transitions while verifying LUT/scaler state restores and no underflow, blanking, or color shifts occur.
- Use diagnostics that read DPP CRC, DPP soft reset/clock enable, DC performance counters, DSCL update/autocal state, OBUF/LB memory state, and readback current-mode fields.

## Open Questions For Merge Lane

- Confirm adjacent chunks include the missing opening definitions for `CM0_CM_BLNDGAM_RAMA_REGION_6_7` and the remaining definitions for `CM1_CM_BLNDGAM_RAMB_REGION_24_25`.
- Check whether DCN 3.0.2 resource code includes this exact header directly or through ASIC-specific include indirection, and note the final per-file integration path accordingly.
- Compare CM0 and CM1 field coverage in the final merged file to determine whether any apparent asymmetry is a chunk-boundary artifact or an intentional hardware/layout difference.

### subset-b-001758: lines 17357-19868

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 17357-19868

Chunk: `subset-b-001758`
Covered source range: lines 17357-19868 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h`

## Purpose

This chunk is a generated AMD DCN 3.0.2 register shift/mask header section. It does not implement runtime logic; it publishes C preprocessor constants that describe bit positions and masks for display hardware registers. Driver code combines these constants with matching register-address macros from `dcn_3_0_2_offset.h` and register helper macros such as `REG_SET`, `REG_UPDATE`, and field-table builders to program AMDGPU display blocks.

The range is concentrated on Display Pipe Processor color-management and related DPP instance-2 metadata:

- the tail of `CM1` blend-gamma RAM-B region programming and the rest of `CM1` HDR multiplier, memory power, dealpha, coefficient format, shaper LUT, shaper RAM-A/RAM-B, 3D LUT, and test/debug fields;
- `DC_PERFMON12` performance-counter control, state, monitor control, compare-value interrupt, and counter readout fields;
- `DPP_TOP2`, `CNVC_CFG2`, `CNVC_CUR2`, and `DSCL2` fields for DPP instance 2 control, conversion, cursor, scaler, line-buffer, and output-buffer state;
- the beginning and bulk of the `CM2` color-management block, including post-CSC, gamut-remap, gamma-correction RAM-A/RAM-B, blend-gamma RAM-A/RAM-B, shaper, memory-power, 3D-LUT, and shaper RAM-A fields;
- the first fields of `CM2_CM_SHAPER_RAMB_END_CNTL_B`, with the matching continuation in the next chunk.

Although the repository path includes `ceph-client`, this file is AMDGPU display hardware metadata. It has no Ceph filesystem behavior, distributed storage state, networking path, or persistence semantics beyond compiled kernel constants used by the GPU display driver.

## Important APIs, Types, And Macros

There are no functions, structs, typedefs, enums, global variables, or callable APIs in this chunk. Its public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low-bit shift for encoding or decoding a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.

Important macro families in this range include:

- `CM1_CM_BLNDGAM_RAMB_REGION_24_25` through `CM1_CM_BLNDGAM_RAMB_REGION_32_33`: tail of DPP1 blend gamma RAM-B region descriptors. Each region-pair register encodes two piecewise-linear region LUT offsets and segment counts with offsets at bits 0 and 16, segment counts at bits 12 and 28, 9-bit LUT-offset masks, and 3-bit segment-count masks.
- `CM1_CM_HDR_MULT_COEF`, `CM1_CM_MEM_PWR_CTRL`, `CM1_CM_MEM_PWR_STATUS`, `CM1_CM_MEM_PWR_CTRL2`, and `CM1_CM_MEM_PWR_STATUS2`: CM1 HDR multiplier and memory power force/disable/status fields for gamma-correction, blend-gamma, shaper, and 3D-LUT memories.
- `CM1_CM_DEALPHA`, `CM1_CM_COEF_FORMAT`, `CM1_CM_SHAPER_*`, and `CM1_CM_3DLUT_*`: CM1 dealpha enable/ablend, coefficient-format selectors, shaper LUT mode/current mode, shaper offsets/scales, shaper LUT index/data/write selection, RAM-A/RAM-B shaper region programming, 3D-LUT mode/current mode/index/data/read-write control, output normalization, and output RGB offsets.
- `CM1_CM_TEST_DEBUG_INDEX` and `CM1_CM_TEST_DEBUG_DATA`: indexed CM test/debug readback and write data selectors.
- `DC_PERFMON12_PERFCOUNTER_*` and `DC_PERFMON12_PERFMON_*`: performance event select, value select, counter increment/run/restart/interrupt controls, counter state machine, compare-value interrupt status/clear/mode/mask/select, and high/low counter readouts.
- `DPP_TOP2_DPP_CONTROL`, `DPP_TOP2_DPP_SOFT_RESET`, `DPP_TOP2_DPP_CRC_*`, and `DPP_TOP2_HOST_READ_CONTROL`: DPP2 enable, clock-gate disable, output muxing, soft reset, CRC values/control, and host readback mode.
- `CNVC_CFG2_*`: DPP2 converter and pre-color-stage fields for surface pixel format and alpha-plane enable, format bypass/alpha/expansion/crossbar/clamping, floating-point conversion bias/scale, color/luma keying, 2-bit alpha LUT, pre-dealpha/pre-realpha, pre-CSC mode/current mode, A/B pre-CSC coefficient matrices, coefficient format, and pre-degamma mode/select.
- `CNVC_CUR2_CURSOR0_*`: cursor enable, mode, 2x magnify, expansion, alpha, position readback mode, color entries, and floating-point cursor scale/bias.
- `DSCL2_*`: DPP2 scaler coefficient RAM access, scaler mode/taps/control, manual replication, luma/chroma horizontal and vertical scale ratios and initial phases, black color, update-autocal state, overscan, OTG blanking, recout/MPC sizing, line-buffer format, memory control/status, FIFO status, v-counter, and output-buffer controls.
- `CM2_CM_CONTROL`, `CM2_CM_POST_CSC_*`, `CM2_CM_GAMUT_REMAP_*`, and `CM2_CM_BIAS_*`: DPP2 color-management bypass/update-pending state, post-CSC mode/current mode, A/B post-CSC matrices, gamut-remap mode/current mode, A/B gamut-remap matrices, and bias channels.
- `CM2_CM_GAMCOR_*` and `CM2_CM_BLNDGAM_*`: DPP2 gamma-correction and blend-gamma mode/select/current/PWL controls, LUT index/data/control, RAM-A/RAM-B start/end/slope/base/offset descriptors, and 34-region paired region descriptors.
- `CM2_CM_HDR_MULT_COEF`, `CM2_CM_MEM_PWR_*`, `CM2_CM_DEALPHA`, `CM2_CM_COEF_FORMAT`, `CM2_CM_SHAPER_*`, and `CM2_CM_3DLUT_*`: DPP2 equivalents of CM1 HDR, memory power, dealpha, coefficient format, shaper, and 3D-LUT fields.

The chunk is boundary-split. It begins in the middle of the `CM1_CM_BLNDGAM_RAMB_REGION_24_25` macro group: the first line in this chunk is the mask for region 24's LUT offset, while the comment and shift macros are in the previous chunk. It ends at the first two shift macros for `CM2_CM_SHAPER_RAMB_END_CNTL_B`; its masks and the G/R RAM-B end-control fields continue in the next chunk.

## Control Flow

This header has no runtime control flow. Each line is a compile-time constant consumed by generated register tables and read/modify/write helper paths.

Typical consumer control flow is:

1. Display code builds a software state for a DPP pipe: pixel conversion, pre-CSC, scaler ratios, cursor state, line-buffer format, color transforms, gamma curves, shaper curves, 3D LUTs, memory power state, diagnostics, or perf counters.
2. The relevant DCN generation header maps logical fields to instance-prefixed register names using shift/mask constants from this file and addresses from `dcn_3_0_2_offset.h`.
3. Register helper macros clear the target `_MASK`, shift the input by the matching `__SHIFT`, and write or update the hardware register.
4. Hardware latches the state according to the target block: immediate write, update lock, mode/current handoff, vertical update, LUT write sequence, memory-power transition, or readback/status polling.

Several field groups indicate sequenced state rather than simple configuration. `*_MODE_CURRENT`, `*_SELECT_CURRENT`, `*_UPDATE_PENDING`, `*_MEM_PWR_STATE`, `*_MEM_PWR_STATUS`, `*_SOFT_RESET`, `*_CRC_*`, `*_PERFCOUNTER_STATE`, `*_PERFMON_CVALUE_INT_*`, `*_LUT_INDEX`, `*_LUT_DATA`, and `*_LUT_WRITE_*` fields are normally used in ordered programming flows with polling, readback, or explicit handoff points.

## State And Persistence Behavior

The header itself is stateless and persists nothing. The state described by these constants lives in DCN 3.0.2 display hardware registers and in compiled driver register-field tables.

Hardware state represented by this chunk includes:

- color pipeline state: CM bypass/update-pending, dealpha, coefficient formats, post-CSC matrices, gamut-remap matrices, bias, HDR multiplier, gamma-correction and blend-gamma modes, and current-mode readbacks;
- LUT state: gamma-correction RAM-A/RAM-B, blend-gamma RAM-A/RAM-B, shaper RAM-A/RAM-B, 3D LUT index/data, 30-bit 3D LUT data, 3D LUT output normalization and offsets, and LUT write/read color selection controls;
- converter and cursor state: source pixel format, alpha-plane enable, format expansion, channel crossbar, clamp behavior, pre-dealpha/realpha, pre-degamma, pre-CSC matrices, color keying, alpha LUT, cursor enable/mode/magnification/alpha, cursor colors, and cursor scale/bias;
- scaler and line-buffer state: coefficient RAM contents, tap counts, luma/chroma ratios and phases, overscan, recout/MPC size, line-buffer format, memory partitions, request/data FIFO status, memory power state, and output-buffer controls;
- diagnostics and monitoring state: DPP CRC capture, host-read control, CM test/debug indexed registers, and `DC_PERFMON12` event selection, counter state, interrupt compare values, and high/low counter values;
- power/reset state: DPP soft reset, CM and DSCL memory power force/disable/status bits, and clock-gate disable controls.

Most configuration fields persist until a modeset, atomic commit, LUT/color update, suspend/resume, GPU reset, display block reset, or runtime power transition reprograms them. Status fields and interrupt/comparison bits are transient and may be level-sensitive, latched, write-one-to-clear, or readback-only depending on the hardware register specification. The mask header does not encode access type or required ordering.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.0.2 register database. The constants are meaningful only with the matching register address header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h`

Practical integration points are AMDGPU Display Core and DRM/KMS color, plane, and diagnostics paths:

- DPP resource construction and generation-specific register tables include DCN `*_sh_mask.h` and `*_offset.h` headers to populate field masks/shifts for DPP, scaler, input pixel processor, and color-management helpers.
- Color-management code maps DRM color properties, degamma/regamma, CTM/CSC, shaper LUT, 3D LUT, and HDR multiplier state into CM and CNVC fields. The user-facing 3D LUT properties in `amdgpu_dm_color.c`, `amdgpu_dm_plane.c`, and `amdgpu_mode.h` ultimately rely on generated field metadata like these when the hardware path supports the block.
- DPP/scaler programming uses `DSCL2_*`, `CNVC_CFG2_*`, and `DPP_TOP2_*` fields to translate plane state into converter, scaling, line-buffer, viewport, CRC, and output sizing registers.
- Power-management and reset paths use `*_MEM_PWR_CTRL`, `*_MEM_PWR_STATUS`, `*_MEM_PWR_CTRL2`, `*_MEM_PWR_STATUS2`, `DPP_TOP2_DPP_SOFT_RESET`, `DSCL2_DSCL_MEM_PWR_*`, and `DSCL2_OBUF_MEM_PWR_CTRL` to sequence block memories and resets.
- Diagnostics and performance paths use `DPP_TOP2_DPP_CRC_*`, `CM*_CM_TEST_DEBUG_*`, and `DC_PERFMON12_*` to validate output, inspect internal state, count events, and compare counter thresholds.

The field layout also aligns with later-generation MPC/DPP shaper and 3D-LUT programming patterns. For example, DCN3.2 MPC code programs shaper RAM-A/RAM-B start/end/region registers with the same conceptual fields: per-channel start points, end bases, region LUT offsets, segment counts, LUT index/data, and RAM select/write masks. That makes the repeated DCN 3.0.2 CM1/CM2 shaper fields integration-sensitive even though this file contains only raw macros.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These are untyped integer macros; an incorrect mask, shift, register prefix, or field pairing can compile successfully while corrupting a neighboring field or programming the wrong display pipe.

High-risk areas include:

- Repeated instance prefixes. `CM1` and `CM2` fields are structurally similar but target different DPP instances. Mixing prefixes can update the wrong pipe's color or LUT state while leaving the intended pipe unchanged.
- Boundary-split macro groups. This chunk is incomplete for `CM1_CM_BLNDGAM_RAMB_REGION_24_25` at the start and `CM2_CM_SHAPER_RAMB_END_CNTL_B` at the end. Chunk-local mask/shift-pair checks must account for adjacent chunks; the final file merge should verify complete pairs.
- LUT programming order. Gamma, blend-gamma, shaper, and 3D LUT fields require correct index/data/write-enable sequencing and correct RAM-A/RAM-B selection. Wrong `*_LUT_WRITE_SEL`, color mask, index width, data mask, or region segment count can cause banding, bad colors, stale LUTs, or partial updates.
- Color-matrix and coefficient formats. CSC, gamut-remap, bias, coefficient-format, pre-CSC, and format-conversion fields are dense and repetitive. Bad shifts or signedness assumptions can alter color range, HDR/SDR mapping, channel order, or fixed-point interpretation.
- Mode/current handoff. Fields with both requested and current values, such as `*_MODE` and `*_MODE_CURRENT`, can be misread as writable state or sampled too early. Consumers must respect hardware update timing rather than assuming immediate current-mode changes.
- Memory power and reset sequencing. Forcing or disabling CM, shaper, 3D-LUT, DSCL, or OBUF memory while the block is active can blank output or lose LUT state. Status fields should be polled using the proper block sequence.
- Scaler and line-buffer programming. Ratio, phase, tap, overscan, recout, MPC size, and line-buffer memory fields must match plane and timing state. Incorrect masks can produce cropping, unstable scaling, underflow, or corrupted scanout.
- Interrupt/perfmon semantics. `DC_PERFMON12` compare interrupt fields and counter run/restart controls must be updated in the expected order. Confusing status, clear, mask, and mode fields can miss performance events or leave interrupts asserted.
- High-bit masks. Constants such as `0xFFFF0000L` and `0x70000000L` should be handled through existing fixed-width register helpers, not ad hoc signed arithmetic.

## Test Signals

Useful validation signals are mostly build, generated-header, and hardware-behavior oriented:

- Kernel build coverage for DCN 3.0.2 display code that includes `dcn_3_0_2_sh_mask.h`; missing or renamed field macros should fail compilation.
- Generated-register-map comparison against AMD's authoritative DCN 3.0.2 database, verifying every shift/mask in lines 17357-19868 and reconciling boundary-split fields with adjacent chunks.
- Static checks that every non-boundary `_MASK` has a matching `__SHIFT`, repeated `CM1`/`CM2` register layouts stay intentionally identical where expected, and every register has a matching address macro in `dcn_3_0_2_offset.h`.
- DRM/KMS modeset and atomic plane tests covering DPP2 converter formats, alpha-plane handling, cursor modes, pre-CSC, scaler ratios/phases/taps, recout/MPC sizing, and line-buffer behavior.
- Color-management tests for post-CSC, gamut remap, bias, coefficient formats, HDR multiplier, gamma-correction LUTs, blend-gamma LUTs, shaper LUTs, 3D LUT programming, RAM-A/RAM-B switching, and current-mode readback.
- Visual and CRC tests using `DPP_TOP2_DPP_CRC_*` and CM test/debug registers to detect wrong color transforms, channel swaps, LUT corruption, scaling errors, or stale register programming.
- Power-management and reset tests across suspend/resume, runtime display power transitions, GPU reset, pipe disable/enable, and LUT reprogramming after CM/DSCL memory power changes.
- Performance-counter tests that configure `DC_PERFMON12`, start/stop counters, read high/low values, trigger compare interrupts, and verify clear/mask behavior without disturbing adjacent control fields.

Regression symptoms from incorrect constants include blank or corrupted scanout, wrong colors, banding, failed HDR or 3D-LUT validation, bad cursor blending, scaler artifacts, underflows, stuck update-pending/current-mode state, failed CRC checks, missed perfmon interrupts, or display failures after power transitions.

## Cross-Chunk Notes

This is chunk 8 of 26 for the large generated `dcn_3_0_2_sh_mask.h` file. Earlier chunks define the beginning of the DCN 3.0.2 register map and the preceding CM1 blend-gamma groups. Later chunks complete `CM2_CM_SHAPER_RAMB_END_CNTL_B`, continue the remaining CM2 shaper RAM-B region fields, and proceed through subsequent DCN display blocks. The final per-file document should treat this source as generated hardware ABI metadata and merge these notes with adjacent chunks before drawing conclusions about complete per-register definitions.

### subset-b-001759: lines 19869-22375

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 19869-22375

## Scope

This chunk is a generated AMD DCN 3.0.2 ASIC register bitfield header segment. It contains preprocessor constants only: each hardware register field is represented by a `__SHIFT` macro for the bit offset and a `_MASK` macro for the bit mask. The assigned range spans 2,507 source lines, with 2,117 `#define` entries, 1,061 shift definitions, and 1,066 mask definitions.

The chunk starts inside the `CM2_CM_SHAPER_RAMB_*` definitions and ends inside `DC_PERFMON14_PERFCOUNTER_STATE`. The merge lane must stitch adjacent chunks before treating the opening CM2 shaper group or closing perfmon14 group as complete.

## Purpose

The purpose of this header segment is to expose symbolic bit positions for DCN 3.0.2 display pipe programming in the AMDGPU display driver. Driver code includes this file, along with companion address and base-index headers, so register read-modify-write helpers can program MMIO fields without duplicating raw numeric constants.

The covered register surfaces are concentrated around DPP pipe 3 and the tail of DPP pipe 2:

- tail of `CM2` color-management shaper and 3D LUT state for DPP2.
- `DC_PERFMON13` performance counter controls for DPP2.
- `DPP_TOP3`, `CNVC_CFG3`, `CNVC_CUR3`, `DSCL3`, and `CM3` display pipe 3 blocks.
- beginning of `DC_PERFMON14` performance counter controls for DPP3.

This is data-like source rather than executable logic. Its behavior is indirect: correctness depends on exact alignment with AMD's hardware register specification and with the corresponding `dcn_3_0_2` register-address header.

## Address Blocks And Register Surface

Visible address blocks:

- `dce_dc_dpp2_dispdec_dpp_dcperfmon_dc_perfmon_dispdec`: `DC_PERFMON13` performance counter control, counter state, perfmon control, interrupt/status, and low/high value fields for the DPP2 monitor.
- `dce_dc_dpp3_dispdec_dpp_top_dispdec`: `DPP_TOP3` clock, gate, soft-reset, CRC value/control, and host-read rate fields.
- `dce_dc_dpp3_dispdec_cnvc_cfg_dispdec`: `CNVC_CFG3` pixel-format conversion, format expansion, alpha, color keyer, pre-dealpha, pre-CSC matrix, pre-degamma, and pre-realpha fields.
- `dce_dc_dpp3_dispdec_cnvc_cur_dispdec`: `CNVC_CUR3` cursor enable, mode, color, floating-point scale, and bias fields.
- `dce_dc_dpp3_dispdec_dscl_dispdec`: `DSCL3` scaler coefficient RAM, scaling mode/taps/ratios/inits, overscan, recout/MPC size, line-buffer format/memory, scaler and output-buffer memory power, and update/status fields.
- `dce_dc_dpp3_dispdec_cm_dispdec`: `CM3` color-management controls, post-CSC, gamut remap, gamma correction, blend gamma, HDR multiplier, dealpha, shaper LUT, 3D LUT, memory power, and debug fields.
- `dce_dc_dpp3_dispdec_dpp_dcperfmon_dc_perfmon_dispdec`: starts `DC_PERFMON14` counter control and state fields for DPP3; the range ends before the `PERFCOUNTER_STATE` register is fully listed.

## Important Macros And Register Families

`CM2_CM_SHAPER_RAMB_*` continues the DPP2 color-management shaper RAM-B region table. The visible fields define per-channel end controls for B/G/R and paired region descriptors from `REGION_0_1` through `REGION_32_33`. Each region descriptor packs two piecewise-linear region LUT offsets and segment counts into one register, using 9-bit offset masks and 3-bit segment-count masks. `CM2_CM_MEM_PWR_CTRL2`, `CM2_CM_MEM_PWR_STATUS2`, `CM2_CM_3DLUT_*`, and `CM2_CM_TEST_DEBUG_*` expose shaper/HDR 3D LUT memory power, 3D LUT mode/size/current state, index/data access, 30-bit data access, RAM selection/write/read controls, output normalization and RGB offset/scale, and test-debug index/data fields.

`DC_PERFMON13_*` defines the DPP2 performance-monitor programming interface. `PERFCOUNTER_CNTL` selects events, counted value, increment mode, hardware control, run-enable mode, restart, interrupt enable, off-mask behavior, active state, and counter selector. `PERFCOUNTER_CNTL2` selects counted value type, hardware stop inputs, counter-off source, and counter-control selector. `PERFCOUNTER_STATE`, `PERFMON_CNTL`, `PERFMON_CNTL2`, `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW` define state selection, report count, counter-off interrupt status/acknowledge, clock enable, run-enable start/stop sources, per-counter interrupt bits, and counter value readback.

`DPP_TOP3_*` defines top-level DPP3 control bits. These include DPP clock enable, static/dynamic clock-gate disables, DSCL gate disable, DISPCLK/DPPCLK gate controls, test clock selection, CNVC/DSCL/CM/OBUF soft resets, CRC result registers, CRC enable/one-shot/status/source/pixel-format/cursor-format/mask fields, and host-read rate control.

`CNVC_CFG3_*` defines the converter configuration path before scaling/color management. It covers surface pixel format and alpha-plane enable, format expansion and 16-bit conversion, CNVC bypass/MSB alignment, positive clamps, update-pending status, RGB crossbar selection, floating-point bias/scale for R/G/B, color-keyer enable/alpha and low/high thresholds for RGB, four-entry 2-bit alpha LUT, pre-dealpha and pre-realpha enable/ABLND enable, pre-CSC mode/current mode, primary and alternate 3x4 pre-CSC matrices, coefficient format, and pre-degamma mode/select.

`CNVC_CUR3_*` defines a narrow cursor surface for pipe 3: cursor0 enable, expansion mode, pixel inversion, ROM enable, mode, pixel-alpha modulation, update-pending status, two 24-bit cursor colors, and floating-point scale/bias.

`DSCL3_*` defines DPP3 scaler and line-buffer fields. The coefficient RAM fields select tap pair, phase, filter type, and even/odd tap coefficients with enable bits. Scale mode fields select scaler mode, coefficient RAM bank and current/readback bank, chroma/alpha coefficient modes, luma/chroma tap counts, boundary mode, two-tap hard-coded/sharp mode and sharp factors, manual replicate factors, horizontal and vertical scale ratios and init phases for luma/chroma/top/bottom paths, black color, update-pending, autocal mode/pipe selection, external overscan, OTG blanking, recout start/size, MPC size, line-buffer interleave/alpha, memory partitioning, vertical counters, DSCL/LB memory power control/status, OBUF bypass/full-buffer/hold behavior, and OBUF memory power state.

`CM3_*` is the largest family in this range. It defines the DPP3 color-management pipeline: global bypass/update pending, post-CSC mode and A/B 3x4 matrices, gamut-remap mode and A/B 3x4 matrices, bias registers, gamma-correction controls and LUT access, gamma RAM A/B PWL region programming, blend-gamma controls and RAM A/B PWL region programming, HDR multiplier, CM memory power control/status, dealpha enable, coefficient formats, shaper control/offset/scale/LUT access, shaper RAM A/B region programming, shaper and HDR3DLUT memory power control/status, 3D LUT mode/index/data/read-write controls, output normalization and RGB offset/scale, and CM test-debug index/data.

`DC_PERFMON14_*` begins the DPP3 performance-monitor interface and mirrors the `DC_PERFMON13` structure for pipe 3. This chunk includes full `PERFCOUNTER_CNTL` and `PERFCOUNTER_CNTL2` definitions plus the start of `PERFCOUNTER_STATE`; masks for counter states 5 through 7 and following perfmon registers are outside the assigned range.

## Control Flow And Runtime Behavior

There is no C control flow in this chunk. Runtime control flow is represented by hardware programming sequences that consume these masks through AMDGPU register helpers.

The likely hardware flows represented here are:

- DPP3 pipe bring-up and reset sequencing: `DPP_TOP3_DPP_CONTROL` enables the pipe clock and controls clock gating, while `DPP_TOP3_DPP_SOFT_RESET` resets CNVC, DSCL, CM, and OBUF subblocks.
- Pixel conversion before scaling: `CNVC_CFG3_*` fields configure the source pixel format, alpha handling, color keying, crossbar, pre-CSC matrices, pre-degamma, and update-pending handshakes.
- Cursor composition preparation: `CNVC_CUR3_*` fields select cursor mode, color registers, ROM/pixel-inversion behavior, alpha modulation, and update-pending status.
- Scaling and viewport sizing: `DSCL3_*` fields program coefficient RAM, scaler mode, taps, ratios, init phases, overscan, recout/MPC size, line-buffer partitions, and OBUF behavior.
- Color-management programming: `CM3_*` fields program post-CSC, gamut remap, gamma correction, blend gamma, shaper curves, 3D LUT RAM selection/data, output normalization, and bypass/update state.
- Performance monitoring: `DC_PERFMON13_*` and `DC_PERFMON14_*` select events, value types, counter sources, run/stop conditions, interrupt behavior, and value readback for display performance counters.
- Memory-power management: `CM2_CM_MEM_PWR_*`, `DSCL3_DSCL_MEM_PWR_*`, `DSCL3_OBUF_MEM_PWR_*`, and `CM3_CM_MEM_PWR_*` expose force/disable/state bits for LUTs, line-buffer banks, OBUF, gamma/blend/shaper memories, and HDR 3D LUT memory.

## State And Persistence

The macros themselves hold no mutable state and allocate no storage. They describe fields in persistent MMIO registers. Writes through these fields can change display hardware state until another write, block reset, GPU reset, suspend/resume restore, or mode-set reprogramming occurs.

Important state classes represented by this chunk:

- Double-buffer and update state: `*_UPDATE_PENDING`, `*_MODE_CURRENT`, `*_SELECT_CURRENT`, `SCL_COEF_RAM_SELECT_CURRENT`, and `SCL_COEF_RAM_SELECT_RD` fields expose hardware-applied vs requested state. Consumers must sequence writes around vupdate or other hardware latch points.
- Indexed RAM state: `CM*_3DLUT_INDEX`, `CM*_3DLUT_DATA`, `CM*_SHAPER_LUT_INDEX`, `CM*_SHAPER_LUT_DATA`, `CM*_GAMCOR_LUT_*`, `CM*_BLNDGAM_LUT_*`, and `DSCL3_SCL_COEF_RAM_*` represent address/data style access to internal RAMs. The selected index, RAM bank, color mask, read selector, and write-enable fields are stateful programming context.
- Piecewise-linear curve state: gamma, blend-gamma, and shaper RAM A/B region definitions persist as hardware curve descriptors. Region offset/segment fields must match the LUT data layout programmed through the corresponding indexed data registers.
- Power state: memory force, disable, mode, and state fields expose low-power state machines. Incorrect writes can leave LUT or line-buffer memories forced on, disabled during active scanout, or inconsistent with status bits.
- Interrupt and acknowledgement state: perfmon counter-off and per-counter interrupt status/ack fields are latched hardware events; header masks do not encode write-one-to-clear or acknowledgement ordering semantics.
- Debug/readback state: CRC, performance counters, vertical counters, and CM test-debug registers expose diagnostic state rather than pure configuration.

## Dependencies And Integration Points

This chunk depends on companion generated DCN 3.0.2 headers for register addresses, base indices, and field aggregation. The naming convention is the AMDGPU DC convention where a register symbol, a field symbol, a `__SHIFT`, and a `_MASK` are combined by generated or hand-written register access macros.

Likely integration points include:

- DPP3 resource construction and pipe programming code in AMDGPU DC, especially CNVC, DSCL, CM, cursor, and DPP top helper code.
- Color-management code that loads transfer functions, shaper curves, blend/gamma curves, post-CSC/gamut matrices, and 3D LUT data.
- Scaler code that programs DSCL ratios, taps, coefficient RAM, recout/MPC dimensions, line-buffer partitioning, and overscan.
- Display diagnostics that use DPP CRC registers, DSCL counters, perfmon counters, and CM debug registers.
- Power-management and suspend/resume paths that restore DPP subblock memory power and indexed LUT state.
- Generated register tables that map generic block instances to instance-specific names such as `CM2`, `CM3`, `DSCL3`, `CNVC_CFG3`, `DPP_TOP3`, `DC_PERFMON13`, and `DC_PERFMON14`.

Because this is a public include within the AMDGPU source tree, compile-time consumers are sensitive to exact macro spelling. A rename, missing field, or bit-position drift can break builds or silently program the wrong hardware field.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong mask or shift can corrupt neighboring fields in the same 32-bit MMIO register, causing display blanking, color errors, bad scaling, cursor artifacts, incorrect performance data, or power-management regressions.
- The assigned range starts and ends mid-block. `CM2_CM_SHAPER_RAMB_END_CNTL_B` starts before line 19869, and `DC_PERFMON14_PERFCOUNTER_STATE` continues after line 22375. File-level conclusions must merge adjacent chunks.
- Repeated RAM region tables are easy to misgenerate. Gamma, blend-gamma, and shaper RAM A/B each use many near-identical `REGION_N_N+1` macros, with offsets at bits 0 and 16 and segment counts at bits 12 and 28. Off-by-two or RAM A/B swaps would route PWL descriptors to the wrong curve bank.
- Several logical field names include the word `MASK`, producing generated names such as `CM3_CM_SHAPER_LUT_WRITE_EN_MASK__CM_SHAPER_LUT_WRITE_EN_MASK_MASK` and perfmon off-mask fields. Parsers that naively split on `_MASK` can misclassify these.
- Status, ack, and current-state bits have hardware-specific semantics that are not represented in the header. Consumers must not infer safe write values solely from the mask constants.
- Indexed RAM programming is order-sensitive. Losing the selected index, RAM bank, 30-bit mode, color write mask, or host/config mode can corrupt LUT contents even when the individual masks are correct.
- Memory-power fields can interact with active scanout. Forcing or disabling DSCL, OBUF, gamma/blend, shaper, or HDR3DLUT memories at the wrong time can produce visible underflow, stale color data, or hangs.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, generated-header consistency, and hardware/display regression signals:

- AMDGPU DCN 3.0.2 compile coverage catches missing or renamed macros used by register tables and helper code.
- Generated-header checks should verify every `__SHIFT` has a corresponding `_MASK`, masks fit within 32 bits, repeated DPP2/DPP3 and RAM A/B families retain expected parity, and partial chunk boundaries are reconciled by adjacent chunks.
- Display mode-set tests should exercise DPP3 enable/reset, CNVC pixel formats, alpha, color-keying, cursor modes, DSCL scaling ratios/taps/coefficients, recout/MPC sizing, and line-buffer partitioning.
- Color-management tests should cover post-CSC, gamut remap, gamma correction, blend gamma, shaper LUTs, HDR 3D LUT mode/data paths, output normalization, and bypass/current-mode readbacks.
- Power tests should cover suspend/resume and runtime power transitions for DSCL LUT/LB banks, OBUF, CM gamma/blend/shaper memories, and HDR3DLUT memory.
- Diagnostic tests should compare DPP CRC results, perfmon13/perfmon14 counter programming/readback, interrupt ack behavior, DSCL vertical counters, and CM debug-index/data readback against expected hardware behavior.

## Open Questions For Merge Lane

- Confirm the previous chunk contains the start of `CM2_CM_SHAPER_RAMB_END_CNTL_B` and any preceding CM2 shaper setup needed to describe the complete RAM-B programming surface.
- Confirm the next chunk completes `DC_PERFMON14_PERFCOUNTER_STATE` and includes the remaining perfmon14 control/value registers.
- Identify the concrete AMDGPU DCN 3.0.2 register tables and helper functions that consume the DPP3 `CNVC`, `DSCL`, `CM`, `DPP_TOP`, and `DC_PERFMON` macros before the final per-file report names call sites.

### subset-b-001760: lines 22376-24894

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 22376-24894

## Scope

This chunk is a generated AMD DCN 3.0.2 ASIC register bitfield header segment. It contains preprocessor constants only: each hardware field is represented by a `__SHIFT` macro and a `_MASK` macro used by AMDGPU display code to compose and extract MMIO register fields. The chunk spans 2,519 source lines and includes 2,115 `#define` entries.

The range starts in the tail of `DC_PERFMON14_PERFCOUNTER_STATE`, covers the full DPP4 display pipe register surface for converter, scaler, color-management, cursor, and performance-monitor blocks, then covers the beginning of OPP0 output formatting and pipe CRC state. It ends on the `OPP_PIPE_CRC0_OPP_PIPE_CRC_RESULT2` register comment; the result2 field definitions are outside this exact chunk and must be reconciled by the adjacent chunk.

## Purpose

The purpose of this header segment is to expose symbolic bit positions for DCN 3.0.2 display hardware registers. Driver code includes `dcn_3_0_2_sh_mask.h` together with the matching offset header and uses these constants to build typed register tables for register helper read-modify-write operations.

The covered hardware area is display data processing and output processing:

- `DPP4` pipeline control, clock gating, soft reset, host read throttling, CRC, surface conversion, cursor, scaler, line-buffer, output buffer, and color-management fields.
- `CM4` color pipeline programming for pre/post CSC, gamut remap, gamma correction, blend gamma, shaper LUT, HDR multiplier, 3D LUT, memory power, and debug access.
- `DC_PERFMON14` and `DC_PERFMON15` performance monitor controls around DPP4.
- `FMT0`, `DPG0`, `OPPBUF0`, `OPP_PIPE0`, and most of `OPP_PIPE_CRC0`, which belong to output pixel processing for pipe 0.

The chunk is data-like source rather than executable logic. Its correctness depends on exact agreement with the AMD DCN 3.0.2 register specification and with `dcn_3_0_2_offset.h`.

## Address Blocks And Register Surface

Visible address blocks:

- Tail of `dce_dc_dpp4_dispdec_dpp_dcperfmon_dc_perfmon_dispdec`: final `DC_PERFMON14_PERFCOUNTER_STATE` masks plus `DC_PERFMON14_PERFMON_*` control, count value, interrupt, high, and low value fields.
- `dce_dc_dpp4_dispdec_dpp_top_dispdec`: `DPP_TOP4_DPP_CONTROL`, soft reset, DPP CRC value/control, and host read control.
- `dce_dc_dpp4_dispdec_cnvc_cfg_dispdec`: converter configuration, surface pixel format, format control, FP bias/scale, color keyer, 2-bit alpha LUT, pre-dealpha, pre-CSC matrix registers, pre-degamma, and pre-realpha fields.
- `dce_dc_dpp4_dispdec_cnvc_cur_dispdec`: cursor0 control, palette colors, and cursor floating-point scale/bias.
- `dce_dc_dpp4_dispdec_dscl_dispdec`: scaler coefficient RAM, scaling mode/taps, 2-tap sharpening, manual replication, horizontal/vertical ratios and init values, black color, update/autocal, overscan, timing blank references, recout, MPC size, line-buffer format/memory, DSCL memory power, and OBUF power/control.
- `dce_dc_dpp4_dispdec_cm_dispdec`: color-management control, post-CSC, gamut remap, gamma/blend-gamma LUT and piecewise-linear regions, HDR multiplier, memory power/status, dealpha, coefficient format, shaper LUT, 3D LUT, and test-debug fields.
- `dce_dc_dpp4_dispdec_dpp_dcperfmon_dc_perfmon_dispdec`: complete `DC_PERFMON15_*` counter and monitor controls for another perfmon selector in the DPP4 block.
- `dce_dc_opp_fmt0_dispdec`: FMT0 clamp, dynamic expansion, pixel encoding/subsampling, truncation, spatial/temporal dithering, random seeds, 4:2:0 memory power, and 4:2:2 edge control.
- `dce_dc_opp_dpg0_dispdec`: display pattern generator mode, dimensions, ramp, colors, segment offset, and double-buffer status.
- `dce_dc_opp_oppbuf0_dispdec`: active width, segmentation, overlap, repetition, 3D parameters, dummy data, and padded-pixel control.
- `dce_dc_opp_opp_pipe0_dispdec`: OPP pipe clock enable/status and digital bypass.
- `dce_dc_opp_opp_pipe_crc0_dispdec`: CRC control, CRC mask, result0, result1, and the opening comment for result2.

## Important Macros And Register Families

`DPP_TOP4_*` fields control the DPP4 block boundary: clock enable, multiple gate-disable knobs, test clock selection, soft reset for CNVC/DSCL/CM/OBUF subblocks, and DPP CRC one-shot/continuous mode, source, stereo/interlace/pixel-format selection, and component results.

`CNVC_CFG4_*` and `CNVC_CUR4_*` fields describe input conversion. They cover surface pixel format, alpha-plane enable, bypass/MSB alignment, 16-bit conversion, positive clamp modes, channel crossbar selection, color key ranges, alpha LUT entries, FP bias/scale, pre-dealpha/re-alpha, pre-degamma mode/select, pre-CSC coefficient format, and cursor mode/enable/ROM/pixel-inversion/alpha modulation.

`DSCL4_*` fields describe scaling and line-buffer behavior. The register families include coefficient RAM tap selection/data, scale modes, tap counts, 2-tap sharpening, chroma/luma ratios and initial phases, black fill color, recout and MPC dimensions, autocalibration, overscan, OTG blank windows, line-buffer interleave/alpha/memory partitioning, live line-buffer counters, and memory-power controls/status for LUT, data, and coefficient memories.

`CM4_*` is the largest family in this chunk. It provides post-CSC and gamut-remap matrix fields, bias, gamma-correction and blend-gamma LUT controls, RAM A/B region descriptors from regions 0-33, start/end/slope/base/offset values per RGB component, shaper LUT controls and regions, HDR multiplier, dealpha, coefficient format, 3D LUT mode/index/data/read-write/out normalization/out offsets, memory power controls/status for gamma/blend/shaper/3D LUT memories, and indexed debug access.

`DC_PERFMON14_*` and `DC_PERFMON15_*` define display performance counter control surfaces. They include event select, counted value type, increment/run-enable mode, hardware stop controls, count-off selection, interrupt enable/status/ack, active state, report count, read selector, and split high/low count values.

`FMT0_*` fields describe the output formatter: component clamp bounds, dynamic expansion, pixel encoding, subsampling mode/order, CbCr bit-reduction bypass, double-buffer update pending, truncation, spatial/temporal dithering, random seed and per-channel offsets, clamp enable/color format, side-by-side stereo width, 4:2:0 memory power state, and 4:2:2 left-edge extra pixel count.

`DPG0_*`, `OPPBUF0_*`, `OPP_PIPE0_*`, and `OPP_PIPE_CRC0_*` describe output-pipe support. DPG fields configure internal test pattern generation and expose double-buffer pending state. OPPBUF fields control active width, segmentation, overlap, pixel repetition, 3D vertical-active spacing, dummy RGB data, and padded segment pixels. OPP pipe fields gate the pipe clock and enable digital bypass. CRC fields enable one-shot or continuous CRC collection and expose stereo/interlace/source/pixel-select controls plus component result registers.

## Control Flow And Runtime Behavior

There is no C control flow in this chunk. Runtime behavior is indirect: `dcn302_resource.c` includes `dcn/dcn_3_0_2_sh_mask.h`, creates DPP and OPP register shift/mask tables, and passes those tables into hardware block constructors.

For DPP, `dcn302_resource.c` defines `tf_shift` and `tf_mask` from `DPP_REG_LIST_SH_MASK_DCN30(__SHIFT)` and `DPP_REG_LIST_SH_MASK_DCN30(_MASK)`, then passes them to `dpp3_construct()` for instances 0-4. The `DPP_REG_LIST_SH_MASK_DCN30` macro in `dcn30_dpp.h` expands through `TF_SF(...)`/`TF2_SF(...)` entries for the same logical fields represented here, using instance-0 names such as `CM0_*`, `CNVC_CFG0_*`, and `DSCL0_*`. The generated DCN header supplies equivalent instance-specific macros; this chunk is the instance-4 register-data source used when the generated field names are expanded for DPP4.

For OPP, `dcn302_resource.c` defines `opp_shift` and `opp_mask` from `OPP_MASK_SH_LIST_DCN20(__SHIFT)` and `OPP_MASK_SH_LIST_DCN20(_MASK)`, then passes them to `dcn20_opp_construct()` for instances 0-4. The OPP mask lists in `dcn10_opp.h` and `dcn20_opp.h` consume fields such as `FMT0_FMT_BIT_DEPTH_CONTROL`, `FMT0_FMT_CONTROL`, `FMT0_FMT_MAP420_MEMORY_CONTROL`, `DPG0_*`, `OPPBUF0_*`, and `OPP_PIPE0_*`, all present in this chunk.

Hardware-oriented flows represented by the fields include:

- DPP block enable/reset and CRC capture through `DPP_TOP4_*`.
- Surface format conversion, alpha handling, cursor composition, and pre-CSC/pre-degamma setup through `CNVC_CFG4_*` and `CNVC_CUR4_*`.
- Scaling setup through coefficient RAM programming, tap selection, scale ratios, recout/MPC dimensions, autocalibration, and DSCL update bits.
- Color processing through pre/post CSC, gamut remap, gamma/blend/shaper LUT programming, HDR multiplier, and 3D LUT read/write controls.
- Formatter and output-pipe setup through FMT0 bit-depth/dither/subsampling/clamp controls, DPG pattern generation, OPP buffer segmentation, and OPP pipe clocking.
- Performance and validation flows through perfmon counters, DPP CRC, OPP pipe CRC, memory power status, double-buffer pending fields, and indexed debug data.

## State And Persistence

The macros themselves hold no mutable state and introduce no storage. They describe persistent hardware state in memory-mapped display registers. Writes through these fields can affect device state until overwritten, reset, power-gated, or restored during display reinitialization.

Several field groups represent latched or handshake state:

- Double-buffer and update state: `CNVC_UPDATE_PENDING`, `DSCL_UPDATE`, `FMT_DOUBLE_BUFFER_REG_UPDATE_PENDING`, `DPG_DOUBLE_BUFFER_PENDING`, `OPPBUF_DOUBLE_BUFFER_PENDING`, and CRC one-shot pending fields expose hardware update synchronization and must be polled or cleared according to register-specific semantics.
- Memory power state: `DSCL4_DSCL_MEM_PWR_CTRL/STATUS`, `DSCL4_OBUF_MEM_PWR_CTRL`, `CM4_CM_MEM_PWR_CTRL/STATUS`, `CM4_CM_MEM_PWR_CTRL2/STATUS2`, and `FMT0_FMT_MAP420_MEMORY_CONTROL` contain force/disable/default-low-power/state fields. Incorrect programming can leave memories powered unnecessarily or unavailable while LUT/scaler data is being used.
- Indexed/table state: gamma, blend-gamma, shaper, and 3D LUT index/data/control registers represent internal RAM programming windows. Host code must coordinate index selection, read/write control, host select, and color write masks.
- Status and ack state: perfmon count-off and per-counter interrupt status/ack fields, CRC status/result registers, and DPG/OPPBUF pending bits are hardware-observed state. Masks do not document whether a bit is write-one-to-clear, read-only, sticky, or self-clearing.

## Dependencies And Integration Points

This chunk depends on companion generated headers for the same IP version:

- `dcn_3_0_2_offset.h` supplies register addresses and base indices.
- `dcn_3_0_2_sh_mask.h` supplies the shift/mask values in this chunk.
- Resource construction code in `display/dc/resource/dcn302/dcn302_resource.c` selects these generated headers for the DCN 3.0.2 ASIC path.
- DPP integration comes through `display/dc/dpp/dcn30/dcn30_dpp.h` register and mask-list macros and through `dpp3_construct()`.
- OPP integration comes through `display/dc/opp/dcn10/dcn10_opp.h`, `display/dc/opp/dcn20/dcn20_opp.h`, and `dcn20_opp_construct()`.
- Runtime register access uses AMD display helper macros that combine a register address table with the generated mask/shift tables to write packed bitfields without open-coded bit positions.

The chunk also intersects display validation and debug paths: CRC collection, DPG test patterns, perfmon counters, memory power reporting, and test-debug index/data registers are all observable signals used when bring-up or diagnosing display failures.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong shift or mask can overwrite adjacent bits in a 32-bit MMIO register, causing blank displays, incorrect color conversion, scaler failures, cursor corruption, bad dithering, CRC mismatches, or power-management regressions.
- The range begins after the start of `DC_PERFMON14_PERFCOUNTER_STATE` and ends before the `OPP_PIPE_CRC0_OPP_PIPE_CRC_RESULT2` field definitions. The final file report must merge adjacent chunks before treating either register family as complete.
- Field names ending in `_MASK_MASK` are legitimate generated names when the logical field is named `..._MASK`. Parsers or scripts that strip `_MASK` naively can mis-handle fields such as DPP/OPP CRC mask registers and other bitmask-valued fields.
- DPP4 is an instance of a repeated pipe family. Code often defines tables from instance-0 macro names and generates per-instance register addresses separately; reviewers should avoid assuming that all visible `*4` macros are directly referenced by name in hand-written C even though they are part of the generated register namespace.
- Table programming registers are sequencing-sensitive. Gamma, blend, shaper, and 3D LUT data paths require correct index/control/host-select ordering; the masks alone do not encode required delays, locks, or double-buffer handshakes.
- Power-control fields combine force, disable, default-low-power, and state fields in adjacent bit ranges. A mask typo or wrong write value can silently change power behavior for LUT, scaler, OBUF, or formatter memories.
- Perfmon and CRC status/ack bits can be sticky or self-clearing depending on hardware semantics. Consumers must not infer safe acknowledge behavior from the masks alone.

## Test Signals

Useful validation signals for this chunk include:

- Compile coverage for the DCN 3.0.2 resource path, especially `dcn302_resource.c`, `dcn30_dpp.h`, `dcn10_opp.h`, and `dcn20_opp.h`, to catch missing or renamed generated macros.
- Generated-header consistency checks that verify every full field has a matching `__SHIFT` and `_MASK`, masks fit within 32 bits, masks align with shifts, and repeated pipe instances are consistent where the hardware spec requires parity.
- Display mode-set tests that exercise DPP4 enable/reset, scaling, cursor, pre/post CSC, gamut remap, gamma/blend/shaper LUTs, 3D LUT programming, HDR multiplier, and output formatter dithering/clamping/subsampling.
- Hardware validation using DPP CRC, OPP pipe CRC, DPG test patterns, DSCL line-buffer counters, perfmon counts, and debug index/data registers.
- Suspend/resume and power-gating tests that verify DSCL, OBUF, CM, shaper, 3D LUT, and FMT 4:2:0 memory power controls are restored correctly and do not leave pending double-buffer updates.
- Negative/regression checks for common symptoms: black screen after mode set, wrong cursor colors or alpha, scaler artifacts, incorrect HDR/gamut output, unexpected dither/truncation, stale LUT contents, CRC mismatch, perfmon interrupt storms, or memory power state stuck in forced-on/forced-off.

## Open Questions For Merge Lane

- Confirm the adjacent previous chunk supplies the full opening context for `DC_PERFMON14_PERFCOUNTER_STATE`.
- Confirm the adjacent next chunk supplies the `OPP_PIPE_CRC0_OPP_PIPE_CRC_RESULT2` shift/mask definitions and then continues into `FMT1`.
- Compare the DPP4 instance fields in this chunk against DPP0-DPP3 chunks for intentional instance differences versus generation defects.
- Map which of the many visible `CM4_*` LUT and 3D LUT fields are actually reachable through current DCN 3.0.2 color-management code and which are reserved for debug or future feature paths.

### subset-b-001761: lines 24895-27447

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 24895-27447

## Scope And Purpose

This chunk is part of the generated DCN 3.0.2 shift/mask register header for the AMD display driver. It contains C preprocessor constants only: each hardware register field has a `__SHIFT` value and a matching `_MASK` value. Driver code uses these constants to build register field tables for typed register access helpers such as `REG_UPDATE`, `REG_GET`, `REG_READ`, and wait/update macros in the DC display stack.

The slice covers 2,127 macro definitions in the middle of the file: 1,065 shift constants and 1,062 masks. It begins with the tail field for `OPP_PIPE_CRC0_OPP_PIPE_CRC_RESULT2`, then defines repeated instance blocks for OPP/FMT/DPG/OPPBUF/OPP pipe CRC instances 1 through 4, OPP top and DSCRM blocks, a DC perfmon block, ODM input blocks 0 through 4, all of OTG0 timing-generator field masks, and the beginning of OTG1 timing-generator field masks through `OTG1_OTG_VERT_SYNC_CONTROL`.

## Register Blocks Covered

The chunk is organized by generated `addressBlock` comments and register comments:

- `dce_dc_opp_fmt1_dispdec` through `dce_dc_opp_fmt4_dispdec`: formatter controls for OPP instances 1-4. These define clamping lower/upper bounds per RGB component, dynamic expansion, pixel encoding, subsampling, dither/truncation/FRC fields, dither seeds, clamp color format, side-by-side stereo width, 4:2:0 memory power controls, and 4:2:2 left-edge extra-pixel control.
- `dce_dc_opp_dpg1_dispdec` through `dce_dc_opp_dpg4_dispdec`: display pattern generator controls. Fields include `DPG_EN`, mode, dynamic range, bit depth, horizontal/vertical resolution, ramp increments, active dimensions, test colors, segment offsets, and double-buffer pending status.
- `dce_dc_opp_oppbuf1_dispdec` through `dce_dc_opp_oppbuf4_dispdec`: OPP buffer controls. Fields describe active width, display segmentation, overlap pixels, pixel repetition, 3D dummy data and v-active spacing, padded pixels, and double-buffer pending status.
- `dce_dc_opp_opp_pipe1_dispdec` through `dce_dc_opp_opp_pipe4_dispdec`: OPP pipe clock and digital bypass fields.
- `dce_dc_opp_opp_pipe_crc1_dispdec` through `dce_dc_opp_opp_pipe_crc4_dispdec`: OPP pipe CRC control, masks, and result registers for alpha/red, green/blue, and C-channel results.
- `dce_dc_opp_opp_top_dispdec`: top-level OPP clock gating and ABM selector fields, including ABM0-4 clock-on status bits.
- `dce_dc_opp_dscrm0_dispdec` through `dce_dc_opp_dscrm4_dispdec`: DSC remapper forward configuration, including enable, OPP pipe source select, double-buffer pending, and enable-status bits.
- `dce_dc_opp_opp_dcperfmon_dc_perfmon_dispdec`: DC perfmon counter control, counter state, perfmon control, count-value interrupt/ack/status bits, and low/high counter value fields for `DC_PERFMON16`.
- `dce_dc_optc_odm0_dispdec` through `dce_dc_optc_odm4_dispdec`: ODM/OPTC input controls for soft reset, underflow status/clear/interrupts, segment source selection, DSC data format, bytes-per-pixel, segment/slice width, input clock gating, memory select, and spare register storage.
- `dce_dc_optc_otg0_dispdec`: a full OTG0 timing-generator block, including horizontal/vertical totals, blank/sync ranges, trigger A/B controls, flow control, stereo/interlace state, status counters, update locks, double-buffer status, blank color, vertical interrupts, CRC windows/data/control, static-screen detection, 3D structure, global-sync-lock controls, master update, dynamic refresh rate fields, DSC start position, pipe update status, and spare registers.
- `dce_dc_optc_otg1_dispdec`: the start of the equivalent OTG1 block through vertical sync control.

## Important APIs, Types, And Functions

This header does not declare C functions or structs, but its macros become fields in several DC hardware abstraction structs:

- `struct dcn20_opp_shift` and `struct dcn20_opp_mask` in `display/dc/opp/dcn20/dcn20_opp.h` are populated in DCN302 by `OPP_MASK_SH_LIST_DCN20(__SHIFT)` and `OPP_MASK_SH_LIST_DCN20(_MASK)`.
- `struct dcn20_opp_registers` receives the matching register addresses from `OPP_REG_LIST_DCN30(id)` in `display/dc/resource/dcn302/dcn302_resource.c`.
- `struct dcn_optc_shift` and `struct dcn_optc_mask` are populated by `OPTC_COMMON_MASK_SH_LIST_DCN30(__SHIFT)` and `OPTC_COMMON_MASK_SH_LIST_DCN30(_MASK)`.
- `struct dcn_optc_registers` receives the matching OTG/ODM addresses from `OPTC_COMMON_REG_LIST_DCN3_0(id)`.

The concrete construction path for DCN 3.0.2 is in `dcn302_resource.c`:

- `dcn302_opp_create()` allocates `struct dcn20_opp`, then calls `dcn20_opp_construct(opp, ctx, inst, &opp_regs[inst], &opp_shift, &opp_mask)`.
- `dcn302_timing_generator_create()` allocates `struct optc`, attaches `&optc_regs[instance]`, `&optc_shift`, and `&optc_mask`, then calls `dcn30_timing_generator_init()`.
- The resource constructor creates up to five OPP objects and five timing generator objects, matching the 0-4 instance coverage represented by this chunk and neighboring chunks.

The OPP macros from this chunk support operations in `dcn10_opp.c`, `dcn20_opp.c`, and related helpers: bit-depth truncation, spatial/temporal dithering, pixel encoding, chroma subsampling, 4:2:2 edge handling, display test pattern generation, and OPP CRC state capture. The OPTC/OTG/ODM macros support timing-generator programming in `dcn10_optc.c`, `dcn30_optc.c`, and later inherited code paths: mode timing, vertical interrupts, underflow clear/readout, update-lock and double-buffer synchronization, CRC capture, dynamic refresh rate, global sync lock, and ODM segment routing.

## Control Flow And Data Flow

There is no runtime control flow in this header. The generated data flow is:

1. The DCN302 resource file includes `dcn_3_0_2_offset.h` and this `dcn_3_0_2_sh_mask.h`.
2. Register-list macros from subsystem headers expand symbolic register names into ASIC-specific addresses.
3. Mask/shift-list macros expand symbolic field names into the `__SHIFT` and `_MASK` constants defined here.
4. Constructors store those addresses, shifts, and masks into per-block register tables.
5. Runtime DC code calls register helper macros. Those helpers use the field shift and mask tables to insert or extract field values without hard-coded bit arithmetic at each call site.

For example, an OPP formatter update such as a pixel encoding or dither-mode write depends on `FMTn_FMT_CONTROL__...` and `FMTn_FMT_BIT_DEPTH_CONTROL__...` definitions. An OPTC underflow query or clear depends on `ODMn_OPTC_INPUT_GLOBAL_CONTROL__OPTC_UNDERFLOW_OCCURRED_STATUS` and `__OPTC_UNDERFLOW_CLEAR`. Timing programming depends on OTG total/blank/sync masks, while CRC capture depends on OTG and OPP CRC control/result masks.

## State And Persistence Behavior

The macros themselves are compile-time constants and hold no software state. The state they describe is hardware state persisted in display engine registers until overwritten by driver programming, display engine reset, power gating, or ASIC reset.

Important state classes represented in this chunk include:

- Double-buffer and update synchronization state: `FMT_DOUBLE_BUFFER_REG_UPDATE_PENDING`, `DPG_DOUBLE_BUFFER_PENDING`, `OPPBUF_DOUBLE_BUFFER_PENDING`, `DSCRM_DSC_DOUBLE_BUFFER_REG_UPDATE_PENDING`, `OPTC_DOUBLE_BUFFER_PENDING`, `OTG_UPDATE_PENDING`, and several OTG pending subfields.
- Interrupt/status/ack state: ODM underflow status/clear fields, OTG vertical interrupt status/clear fields, OTG vtotal event status/ack fields, perfmon counter interrupt status/ack fields, and trigger/force-count/force-vsync occurrence fields.
- Timing state: OTG horizontal and vertical counters, frame/VF/HV counters, nominal vertical position, dynamic refresh rate bounds, update windows, keepout windows, and global-sync status.
- CRC and readback state: OPP pipe CRC results, OTG CRC result data and windows, CRC masks, pixel data readback registers, and CRC one-shot pending indicators.
- Power/clock state: OPP pipe clock enable/on bits, FMT 4:2:0 memory power fields, OPP top ABM clock-on fields, ODM input clock enable/on/gate-disable bits, and OTG clock busy/enable/on/gate-disable fields.

## Dependencies And Integration Points

This chunk depends on the generated offset header having matching register address names. It also depends on the display subsystem field-list macros selecting the correct instance-0 field names when building reusable shift/mask tables. For OPP and OPTC, the resource code builds one shared shift/mask table from instance-0-style field names and separate per-instance address tables. Therefore the bit layouts must be identical across instances 0-4; this chunk provides the instance 1-4 evidence for that layout.

Primary integration points:

- `display/dc/resource/dcn302/dcn302_resource.c` includes the header and binds its constants into DCN302 resource objects.
- `display/dc/opp/dcn20/dcn20_opp.h` and inherited `dcn10_opp` code define and consume OPP formatter, DPG, OPPBUF, and CRC field tables.
- `display/dc/optc/dcn30/dcn30_optc.h` defines the OPTC/OTG/ODM register and field lists used by DCN302 timing generators.
- `display/dc/optc/dcn10/dcn10_optc.c`, `display/dc/optc/dcn30/dcn30_optc.c`, and inherited OPTC functions consume the tables for underflow handling, timing setup, trigger handling, CRC, and status reads.
- Diagnostic/debug structures in `display/dc/dc.h` name many of the same fields for register-state capture, especially formatter, OPP CRC, and OPTC underflow fields.

## Risks And Edge Cases

- Generated macro drift is high impact. If a shift/mask value is wrong but still compiles, the driver may silently program the wrong hardware bit, causing display corruption, black screen, underflow storms, CRC mismatch, broken stereo/interlace behavior, or incorrect power/clock handling.
- Instance consistency matters. Shared shift/mask structs are based on common field layouts while addresses vary per instance. Any real ASIC layout difference between OPP/ODM/OTG instances would not be represented safely by this pattern.
- Double-buffer pending and update-lock masks are synchronization critical. Incorrect masks around `OTG_DOUBLE_BUFFER_CONTROL`, `OPTC_DOUBLE_BUFFER_PENDING`, formatter pending fields, or DSCRM pending fields can make the driver believe an update has latched when hardware is still pending, or wait forever on the wrong bit.
- Status-clear fields are often write-one-to-clear. Incorrect masks for ODM underflow clear, OTG interrupt clear, perfmon ack, trigger clear, or vtotal ack fields can lose events or leave stale interrupt state asserted.
- CRC fields are used for validation and diagnostics. Wrong CRC control/result masks may make automated display CRC tests fail even when output is correct, or hide real output corruption.
- The chunk boundary splits logical content: it starts with the last field of OPP pipe CRC0 result2 from the previous block and ends in the middle of OTG1 vertical sync control. The final per-file merge must combine adjacent chunks before drawing whole-file conclusions.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware/display integration signals:

- Build coverage for `amd/display` with DCN302 enabled should catch missing or renamed macro fields in `OPP_MASK_SH_LIST_DCN20`, `OPTC_COMMON_MASK_SH_LIST_DCN30`, and `dcn302_resource.c` table initialization.
- Display mode-set tests on DCN302-class hardware should exercise OTG totals, blanking, sync polarity, `OTG_MASTER_EN`, update-lock behavior, and ODM source/width configuration.
- Underflow tests and logs should verify `OPTC_UNDERFLOW_OCCURRED_STATUS` and `OPTC_UNDERFLOW_CLEAR` read/clear the expected ODM input state.
- Dithering, truncation, YCbCr 4:2:2/4:2:0, and pixel-encoding tests should validate the FMT fields in `FMT_CONTROL`, `FMT_BIT_DEPTH_CONTROL`, `FMT_CLAMP_CNTL`, and `FMT_422_CONTROL`.
- DisplayPort compliance or KMS CRC tests can exercise OPP pipe CRC and OTG CRC windows/data fields.
- Test pattern paths through `opp2_set_disp_pattern_generator()`, `opp2_program_dpg_dimensions()`, `opp2_dpg_set_blank_color()`, and `opp2_dpg_is_pending()` can validate DPG and OPPBUF masks.
- Dynamic refresh rate, PSR/static-screen, stereo/interlace, and global-sync-lock tests should cover the OTG0 fields for vtotal min/max/mid, static-screen control, stereo control/status, interlace control/status, and GSL status/control.

### subset-b-001762: lines 27448-29915

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 27448-29915

## Scope And Purpose

This chunk covers 2,468 lines from AMD's generated DCN 3.0.2 shift/mask header. It contains C preprocessor constants for Output Timing Generator (`OTG`) register fields: `__SHIFT` macros define field bit positions and `_MASK` macros define already-shifted 32-bit MMIO masks. There are no functions, structs, enums, local variables, storage objects, or runtime branches in this slice.

The range starts at the mask half of `OTG1_OTG_VERT_SYNC_CONTROL`, covers the rest of the `OTG1` register-field block, then covers complete `OTG2` and `OTG3` OTG blocks. It begins the `OTG4` block and ends at `OTG4_OTG_COUNT_CONTROL`, immediately before `OTG4_OTG_COUNT_RESET`. Macro counts in this exact line range are 507 `OTG1` defines, 716 `OTG2` defines, 716 `OTG3` defines, and 202 `OTG4` defines.

In driver terms, this is the field-layout half of the DCN 3.0.2 timing-generator register contract. The matching `dcn_3_0_2_offset.h` file supplies register addresses, while this file supplies bit placement. `dcn302_resource.c` includes both files and declares five timing generators for this ASIC family, so these replicated OTG masks are used to instantiate per-pipe display timing resources.

## Register Blocks Covered

The partial `OTG1` tail begins with force-vsync-next-line status/control masks and then covers stereo, snapshot, interrupt, update-lock, double-buffer, master-enable, blank-color, vertical interrupt, CRC, static-screen, 3D-structure, global-sync-lock, update-window, global-control, manual-trigger, dynamic-refresh-rate, DTO, request, DSC start-position, pipe update status, and spare-register fields.

`OTG2` and `OTG3` are complete repeated timing-generator blocks. Each includes:

- Core horizontal and vertical timing fields: `OTG_H_TOTAL`, `OTG_H_BLANK_START_END`, `OTG_H_SYNC_A`, `OTG_H_SYNC_A_CNTL`, `OTG_H_TIMING_CNTL`, `OTG_V_TOTAL`, `OTG_V_TOTAL_MIN`, `OTG_V_TOTAL_MAX`, `OTG_V_TOTAL_MID`, `OTG_V_TOTAL_CONTROL`, `OTG_V_TOTAL_INT_STATUS`, `OTG_VSYNC_NOM_INT_STATUS`, `OTG_V_BLANK_START_END`, `OTG_V_SYNC_A`, and `OTG_V_SYNC_A_CNTL`.
- Trigger and forced-sync fields: `OTG_TRIGA_CNTL`, `OTG_TRIGA_MANUAL_TRIG`, `OTG_TRIGB_CNTL`, `OTG_TRIGB_MANUAL_TRIG`, `OTG_FORCE_COUNT_NOW_CNTL`, `OTG_FLOW_CONTROL`, `OTG_MANUAL_FORCE_VSYNC_NEXT_LINE`, and `OTG_VERT_SYNC_CONTROL`.
- Master, interlace, status, and counter fields: `OTG_CONTROL`, `OTG_MASTER_EN`, `OTG_INTERLACE_CONTROL`, `OTG_INTERLACE_STATUS`, `OTG_STATUS`, `OTG_STATUS_POSITION`, `OTG_NOM_VERT_POSITION`, `OTG_STATUS_FRAME_COUNT`, `OTG_STATUS_VF_COUNT`, `OTG_STATUS_HV_COUNT`, `OTG_COUNT_CONTROL`, and `OTG_COUNT_RESET`.
- Frame-phase and update fields: `OTG_UPDATE_LOCK`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_MASTER_UPDATE_MODE`, `OTG_MASTER_UPDATE_LOCK`, `OTG_VSTARTUP_PARAM`, `OTG_VUPDATE_PARAM`, `OTG_VREADY_PARAM`, `OTG_VUPDATE_KEEPOUT`, `OTG_PIPE_UPDATE_STATUS`, and `OTG_REQUEST_CONTROL`.
- Stereo/3D and pixel output fields: `OTG_STEREO_FORCE_NEXT_EYE`, `OTG_STEREO_STATUS`, `OTG_STEREO_CONTROL`, `OTG_3D_STRUCTURE_CONTROL`, `OTG_BLANK_DATA_COLOR`, `OTG_BLANK_DATA_COLOR_EXT`, `OTG_PIXEL_DATA_READBACK0`, and `OTG_PIXEL_DATA_READBACK1`.
- Interrupt and diagnostic fields: `OTG_INTERRUPT_CONTROL`, `OTG_VERTICAL_INTERRUPT0/1/2_*`, `OTG_SNAPSHOT_*`, `OTG_CRC_CNTL`, `OTG_CRC_CNTL2`, `OTG_CRC0/1_WINDOW*`, `OTG_CRC0/1/2/3_DATA_*`, `OTG_CRC_SIG_*`, and `OTG_STATIC_SCREEN_CONTROL`.
- Global sync and DRR fields: `OTG_GLOBAL_SYNC_STATUS`, `OTG_GSL_CONTROL`, `OTG_GSL_VSYNC_GAP`, `OTG_GSL_WINDOW_X/Y`, `OTG_GLOBAL_CONTROL0` through `OTG_GLOBAL_CONTROL4`, `OTG_DRR_TIMING_INT_STATUS`, `OTG_DRR_V_TOTAL_REACH_RANGE`, `OTG_DRR_V_TOTAL_CHANGE`, `OTG_DRR_TRIGGER_WINDOW`, and `OTG_DRR_CONTROL`.
- Miscellaneous per-pipe fields: `OTG_CLOCK_CONTROL`, `OTG_M_CONST_DTO0/1`, `OTG_DSC_START_POSITION`, and `OTG_SPARE_REGISTER`.

The `OTG4` portion covers the same block shape only through the early timing/counter status registers. It includes horizontal/vertical timing, DRR total controls, trigger A/B controls, force-count-now, flow control, stereo force-next-eye, master control, interlace, pixel readback, live status, position counters, frame/VF/HV counts, and count-control fields. The remaining `OTG4` fields continue after this chunk.

## Important APIs, Types, And Macros

This chunk exposes no callable API. Its interface is the generated macro naming convention consumed by AMD display register helpers:

- `OTG<n>_<REGISTER>__<FIELD>__SHIFT` gives the low bit of a field inside a 32-bit OTG MMIO register.
- `OTG<n>_<REGISTER>__<FIELD>_MASK` gives the field mask at its final bit position.
- Register comments such as `//OTG2_OTG_V_TOTAL_CONTROL` delimit logical hardware registers.
- Address-block comments such as `// addressBlock: dce_dc_optc_otg2_dispdec`, `otg3`, and `otg4` mark repeated OPTC/OTG hardware instances.

The constants are normally reached indirectly through AMDGPU display helper patterns such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_FIELD`, `FD_MASK`, `FD_SHIFT`, and instance register-list macros. Higher-level code deals with timing generators, OPTC resources, DRR, DSC, CRC, and interrupt controls; preprocessor expansion binds those logical field names to concrete `OTG1_`, `OTG2_`, `OTG3_`, or `OTG4_` masks and shifts.

No C type information is encoded here. The implicit data model is 32-bit register words with packed bit fields. Range validation, access direction, sequencing, and hardware reset behavior are the responsibility of the caller and the DCN hardware specification.

## Control Flow And Runtime Behavior

This header has no local control flow. Runtime behavior emerges when DCN 3.0.2 resource and timing-generator code includes this mask header with the companion offset header, constructs per-instance register tables, and performs MMIO read/modify/write operations.

A typical timing-programming path computes a `dc_crtc_timing`, selects a timing-generator instance, then uses register helpers to program horizontal total, blanking, sync, vertical total, vertical blanking, sync polarity, update timing, and master enable fields. Dynamic refresh paths program `OTG_V_TOTAL_MIN/MAX/MID`, `OTG_V_TOTAL_CONTROL`, `OTG_DRR_*`, and related double-buffer update fields. Display Stream Compression paths depend on `OTG_DSC_START_POSITION` and OPTC-side timing/segment state outside this exact chunk. Diagnostics and validation paths read status counters, CRC result registers, vertical interrupt status, static-screen status, and live blank/active/sync flags.

The repeated `OTG2` and `OTG3` blocks show that the same logical timing-generator implementation can be bound to different hardware pipes by changing the macro prefix. The chunk boundaries are meaningful: `OTG1` is partial because its earlier base timing fields appear in the previous chunk, and `OTG4` is partial because later update, CRC, global-sync, and DRR fields appear in the next chunk.

## State And Persistence Behavior

The header itself persists no state. It describes hardware state stored in the display engine's OTG registers:

- Timing state: horizontal total, blank start/end, sync start/end/polarity, vertical total/min/max/mid, vertical blank, vertical sync, interlace, counter reset, repetition/count-by-two, and live horizontal/vertical position.
- Enable and routing state: `OTG_MASTER_EN`, `OTG_CONTROL`, current master-enable state, output mux, flow-control source and polarity, trigger source/pipe/polarity/delay, and forced-count or forced-vsync controls.
- Update and synchronization state: update locks, master update lock, double-buffer pending bits, startup/update/ready parameters, keepout windows, global sync lock control/status, manual trigger, and global control registers.
- DRR state: v-total replacement controls, min/max/mid selection, last-used v-total, change limits, trigger windows, reach-range events, timing interrupt state, and DRR double-buffer mode.
- Interrupt and event state: vertical interrupt enable/status/clear/type fields, snapshot occurred/clear/manual trigger fields, vsync nominal interrupt status, force-count and force-vsync occurred/clear fields, trigger occurred/clear fields, and global-sync event clear/mask/enable fields.
- Diagnostic state: CRC enable/mode/window/result fields, static-screen frame count/events, pixel readback channels, status frame/VF/HV counters, pipe update status, and spare fields.
- Stereo/3D/output-color state: stereo enable/sync/eye/status, forced next eye, 3D structure enable/sync patterns, blank data color and extended color fields.

Writable configuration generally persists until the driver rewrites it or the display block is reset. Status, counter, pending, and interrupt fields are live hardware observations or write-to-clear/acknowledge fields; this header does not distinguish those access semantics beyond names such as `*_STATUS`, `*_INT`, `*_CLEAR`, `*_ACK`, `*_PENDING`, and `*_MSK`.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.0.2 register database remaining synchronized with the matching offset header. If an offset exists without the right field macros, helper expansions fail to compile; if a mask or shift has the wrong numeric value, the driver can compile but program the wrong hardware bits.

Important integration points include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c`, which includes `dcn_3_0_2_offset.h` and `dcn_3_0_2_sh_mask.h` and declares DCN302 timing-generator resources.
- `dcn30` timing-generator/OPTC code, which reuses common register-list structures for DCN 3.0-family hardware.
- Core DC hardware sequencing, which locks/unlocks OPTC programming, waits for double-buffer pending state, sets manual triggers, configures ODM/DSC relationships, and programs timing updates.
- DC/DMUB DRR and FAMS update paths, which pass OTG instance and v-total range values for firmware-assisted refresh changes.
- IRQ service code that maps OTG vertical update, vstartup, vsync, and global-sync status bits to display interrupt sources.
- Debug and test paths that capture OPTC register state, CRCs, underflow/update status, and live timing counters.

Although this file lives under `sources/distributed-fs/ceph-client`, it is imported Linux AMD GPU display-driver code. It is not Ceph filesystem logic.

## Risks And Edge Cases

The largest risk is generated-register drift. One wrong shift or mask can make a correct `REG_UPDATE` alter a neighboring field, miss a write-to-clear bit, or read an unrelated status bit. High-risk packed registers in this chunk include `OTG_V_TOTAL_CONTROL`, `OTG_TRIGA_CNTL`, `OTG_TRIGB_CNTL`, `OTG_INTERRUPT_CONTROL`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_GLOBAL_SYNC_STATUS`, `OTG_GSL_CONTROL`, `OTG_DRR_TIMING_INT_STATUS`, and `OTG_CRC_CNTL`.

Chunk boundaries are partial. This slice starts after the `OTG1_OTG_VERT_SYNC_CONTROL` shift definitions and ends before the rest of `OTG4`; final file-level reconciliation must combine adjacent chunks before claiming complete coverage for either instance.

Instance replication can hide pipe-specific errors. `OTG2` and `OTG3` are structurally mirrored, and the `OTG4` prefix starts the same pattern. A single generated prefix, address-block transition, or field-name mismatch may show up only on one display pipe or only in a multi-display/ODM/DRR scenario.

Several fields encode frame-phase-sensitive behavior. Bad update-lock, double-buffer, vstartup/vupdate/vready, manual-trigger, force-vsync, or GSL window masks can produce timing changes on the wrong frame, stuck pending updates, global-sync lock failures, or visible display glitches.

DRR and v-total fields are tightly coupled. Incorrect `V_TOTAL_MIN/MAX/MID`, replacement-enable, reach-range, trigger-window, or change-limit masks can break variable refresh, cause missed events, or allow timing values outside the safe range for the active stream.

Interrupt/status fields use similar names to control fields. Confusing `*_INT_STATUS`, `*_STATUS`, `*_CLEAR`, `*_ACK`, `*_MSK`, and `*_INT_TYPE` can leave interrupts asserted, clear evidence before it is sampled, or mask real timing faults.

CRC and diagnostic fields are useful for validation but can perturb test state if enabled at the wrong time. Window coordinates, one-shot pending bits, stereo/interlace modes, and blank-only/new-pixel selection must match the active timing mode when comparing expected CRCs.

## Test Signals

Build-time validation should compile DCN302 display code that includes this header and exercises timing-generator register tables. Missing or renamed `OTG<n>_*` macros should be caught by preprocessor expansion in register helper structures.

Static validation should compare this generated mask header against `dcn_3_0_2_offset.h` and the authoritative AMD register database. High-signal checks include ensuring every `OTG2` and `OTG3` register in this chunk has both shift and mask definitions for each field, verifying repeated field layouts match across instances, and confirming the `OTG1`/`OTG4` partial boundaries are completed by adjacent chunks.

Runtime validation should exercise DCN302 hardware with multiple active pipes, especially pipes mapped to OTG2 and OTG3. Useful scenarios include mode set, blank/unblank, interlace if supported, stereo/3D paths if exposed, ODM/DSC modes, display reset, suspend/resume, and hot transitions between single and multi-display states.

Timing-specific signals include correct horizontal/vertical totals and sync positions on the link, stable live position counters, frame count increments, correct vblank/vactive/hblank/hactive status transitions, and no stuck double-buffer pending bits after programming.

DRR and refresh tests should vary `v_total_min`, `v_total_max`, and `v_total_mid`, observe v-total reach/change interrupts, verify trigger windows, and confirm firmware-assisted DRR updates target the intended OTG instance.

Interrupt and synchronization tests should enable vertical interrupts, vsync nominal interrupts, force-count-now events, force-vsync-next-line events, and GSL events, then verify status, clear, ack, mask, and interrupt-type behavior.

Diagnostic tests should collect OTG CRCs over known frames, validate static-screen events, check pixel readback channels, and ensure pipe update status reflects completed timing changes without underflow or stale pending state.

## Open Cross-Chunk Questions

- The merge lane should combine this with the previous chunk to describe the full `OTG1` block, including base timing and count-control fields that precede line 27448.
- The merge lane should combine this with the next chunk to describe the complete `OTG4` block and any later OTG instances in the DCN 3.0.2 file.
- Whole-file reconciliation should verify all five timing generators declared for DCN302 have complete offset and shift/mask coverage and that the repeated OTG layouts match the ASIC register source.

### subset-b-001763: lines 29916-32314

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 29916-32314

## Scope And Purpose

This chunk is a generated AMD DCN 3.0.2 register shift/mask table. It exports C preprocessor constants that describe hardware register field bit positions (`__SHIFT`) and field masks (`_MASK`) for memory-mapped display-controller registers. The matching address definitions live in `dcn_3_0_2_offset.h`; this file supplies the bit layout metadata consumed by the AMDGPU Display Core register helper layer.

The requested range contains 2,169 `#define` entries: 1,085 shift constants and 1,084 mask constants. The one-entry imbalance is caused by the chunk ending inside `DP_AUX1_AUX_DPHY_TX_REF_CONTROL`: it includes the `AUX_TX_REF_SEL`, `AUX_TX_RATE`, and `AUX_TX_REF_DIV` shifts and the first two masks, while the remaining mask for that register continues after line 32314.

There are no C functions, structs, enums, or runtime branches in this slice. Its API surface is the generated macro namespace used by symbol-pasting register list macros such as `SF`, `HWS_SF`, `SRI`, `REG_READ`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.

## Register Blocks Covered

The chunk starts in the middle of the `dce_dc_optc_otg4_dispdec` address block and completes the later `OTG4` timing-generator fields. Covered OTG4 registers include count reset, manual and automatic force-vsync controls, stereo status/control, snapshot capture, interrupt control, update locks, double-buffer pending status, master enable, blank colors, vertical interrupts 0 through 2, CRC control/data/windowing, static-screen detection, 3D structure control, global-sync-lock (GSL) timing, master update windows, global update controls, dynamic refresh rate (DRR) status/control, M/N DTO constants, request mode, DSC start position, pipe update status, and a spare register.

The `dce_dc_optc_optc_misc_dispdec` block then defines mux, clock, and ODM memory-power fields: `DWB_SOURCE_SELECT`, `GSL_SOURCE_SELECT`, `OPTC_CLOCK_CONTROL`, `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL2`, `ODM_MEM_PWR_CTRL3`, `ODM_MEM_PWR_STATUS`, and `OPTC_MISC_SPARE_REGISTER`.

The `dce_dc_optc_optc_dcperfmon_dc_perfmon_dispdec` block covers `DC_PERFMON17`, including performance-counter event selection, counter state, monitor enable/state, counter off interrupt state, and low/high counter-value readback fields.

The `dce_dc_dio_dout_i2c_dispdec` block covers the display I2C/DDC engine. It includes `DC_I2C_CONTROL`, arbitration, interrupt control, software status, DDC1 through DDC5 hardware status/speed/setup, transaction descriptors 0 through 3, indexed data access, EDID detect control, and DDC read-request interrupt fields. DDC6/VGA-related fields are present in adjacent generated ranges, not this exact slice.

The DIO common block covers scratch registers, DIO memory power status/control, display and symbol clock gating, display interface power management, DIG front-end/back-end soft reset bits for DIGA through DIGG, HDMI RX status timer, generic interrupt message/clear registers, and `DC_PERFMON18`.

The HPD blocks cover `HPD0` through `HPD4`. Each instance includes hot-plug interrupt status, interrupt control, HPD enable/timers, fast-training delays/enables, and connect/disconnect toggle filter timing.

The final portion covers the complete `DP_AUX0` AUX controller field set and the beginning of `DP_AUX1`. `DP_AUX0` includes AUX enable/reset, HPD selection, software transaction control, arbitration, interrupts, software and link-service status/data windows, DPHY TX/RX timing/status, GTC sync controls/status/error fields, and PHY wake control. `DP_AUX1` is covered through control, software control, arbitration, interrupts, software/link-service status/data, and the beginning of DPHY TX reference control.

## Important APIs, Types, And Macros

The primary API contract is the generated name shape:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for that field.
- Comment markers such as `//OTG4_OTG_INTERRUPT_CONTROL` and `// addressBlock: dce_dc_dio_dp_aux0_dispdec` are generator structure only; they are not compiled C symbols.

Important macro families in this chunk are:

- `OTG4_OTG_*` for the fifth output timing generator instance's status, events, CRC, update-lock, GSL, DRR, and DSC-position fields.
- `DWB_SOURCE_SELECT`, `GSL_SOURCE_SELECT`, `OPTC_CLOCK_CONTROL`, and `ODM_MEM_PWR_*` for OPTC misc and ODM memory-power integration.
- `DC_PERFMON17_*` and `DC_PERFMON18_*` for OPTC/DIO performance monitor programming and readback.
- `DC_I2C_*` for DDC/I2C command, arbitration, per-DDC timing, transaction, data, EDID-detect, and interrupt fields.
- `DIO_*` and `DIG_SOFT_RESET` for DIO clock, memory-power, scratch, reset, and generic interrupt controls.
- `HPD0_*` through `HPD4_*` for connector hot-plug-detect sense, debounce, interrupt, and fast-train behavior.
- `DP_AUX0_AUX_*` and `DP_AUX1_AUX_*` for DisplayPort AUX/I2C-over-AUX transaction engines.

The concrete DCN 3.0.2 integration point is `display/dc/resource/dcn302/dcn302_resource.c`, which includes `dcn_3_0_2_offset.h` and this header. That resource file builds DIO, I2C, AUX, HPD, and link-encoder register tables and initializes shift/mask structs from these generated constants. For example, it uses `DIO_REG_LIST_DCN10()`, `I2C_HW_ENGINE_COMMON_REG_LIST(id)`, `I2C_COMMON_MASK_SH_LIST_DCN2(__SHIFT/_MASK)`, `DCN2_AUX_REG_LIST(id)`, and `HPD_REG_LIST(id)` to bind generic display-core code to the DCN 3.0.2 register map.

## Functional Field Groups

OTG4 timing and event fields describe a live scanout timing generator. Snapshot fields capture vertical/horizontal/frame counters. Vertical interrupt fields define line positions, polarity, enable/status/clear bits, and interrupt type. Global sync status fields expose VSTARTUP, VUPDATE, VUPDATE no-lock, VREADY, stereo select, and field-number events. Pipe update status fields report flip, DC register update, cursor update, and vupdate keepout state.

OTG4 update-lock and double-buffer fields coordinate when timing-sensitive changes latch. `OTG_UPDATE_LOCK`, `OTG_MASTER_UPDATE_LOCK`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_GLOBAL_CONTROL*`, and `OTG_VUPDATE_KEEPOUT` provide the hardware side of frame-aligned update sequencing. Incorrect masks here can cause updates to latch too early, never latch, or race vblank/vupdate.

OTG4 CRC fields support validation and diagnostics. `OTG_CRC_CNTL`, `OTG_CRC_CNTL2`, CRC window controls, `OTG_CRC*_DATA_*`, and CRC signal masks configure capture source, capture windows, component masks, and readback values. These are important for display CRC selftests and diagnosing scanout corruption.

Static screen, stereo, 3D, and DRR fields describe specialized display modes. Static-screen controls enable CPU static-screen interrupts and override state. Stereo and 3D fields expose eye/field selection and 3D structure frame count. DRR fields expose vtotal reach/update interrupts, trigger windows, and last vtotal used by dynamic refresh.

I2C/DDC fields define the software and hardware transaction engine used for EDID and display sideband operations. The runtime sequence is to obtain I2C register ownership through `DC_I2C_ARBITRATION`, program DDC speed/setup and transaction registers, use `DC_I2C_DATA` as an indexed buffer, assert `DC_I2C_GO`, then poll or acknowledge `DC_I2C_SW_STATUS` and interrupt bits. Error status includes timeout, abort, buffer overflow, stopped-on-NACK, and per-transaction NACK bits.

HPD fields provide the connector-presence and HPD RX interrupt interface. The status registers report immediate and delayed HPD sense, RX interrupt state, and filter timer values. Control registers acknowledge interrupts, select polarity, enable HPD/RX interrupts, and program connection/RX timers. Toggle filter fields debounce connect/disconnect events.

DP AUX fields define the DisplayPort AUX controller and its PHY timing. Control fields enable/reset AUX, bind the AUX engine to an HPD source, ignore HPD disconnect for special cases, enable mode detection, request impedance calibration, and deglitch AUX input. Arbitration fields coordinate software and DMCU ownership. SW/LS status fields report done/request, timeout, overflow, HPD disconnect, malformed start/stop/sync/reply states, reply byte count, CP IRQ, and low-speed update status. Data registers are indexed byte windows. DPHY fields configure TX reference/rate/divider, precharge, RX windows, timeout, detection threshold, and expose TX/RX state. GTC sync fields configure and report global time-code sync over AUX.

Perfmon fields are diagnostic/profiling surfaces. `DC_PERFMON17` corresponds to the OPTC side and `DC_PERFMON18` to the DIO side in this generated range. Each exposes event selection, counter control, counter state, monitor state, counter-off interrupt control/status/ack, and low/high value readback.

## Control Flow And State Behavior

This header has no direct control flow. Runtime behavior is produced when display resource initialization binds offset macros and these shift/mask macros into register tables. Later, hardware modules call helper macros that use those tables to pack or extract fields in MMIO register values.

The state described by this chunk is hardware-resident and persists until changed by the driver, firmware/DMCU, hardware event logic, reset, or power management. Some fields are configuration state, such as HPD filter delays, DDC timing, AUX PHY timing, OTG blank color, CRC windows, DRR trigger windows, and clock-gating controls. Other fields are live status or event state, such as interrupt occurred/status bits, reset-done bits, clock-on/busy bits, pending-update bits, AUX/I2C reply/error bits, perf counter values, HPD sense, and memory-power status.

Several registers are stateful command/status interfaces. `DC_I2C_DATA` and `DP_AUX*_AUX_*_DATA` are indexed byte windows, so access order and index/autoincrement behavior matter. I2C and AUX ownership bits must be requested and released in order or transactions can be denied, race firmware, or leave a sideband engine busy. Interrupt ack/clear fields generally require writing the correct bit, not merely reading status.

Frame-synchronized OTG fields are especially ordering-sensitive. Update locks, double-buffer pending bits, VUPDATE/VREADY/VSTARTUP events, keepout windows, and GSL fields are used around atomic modeset and page-flip sequencing. A wrong shift or mask can manifest as missed vblank/vline events, stuck page flips, tearing, incorrect VRR timing, or only one pipe failing because this chunk is specific to `OTG4`.

## Dependencies And Integration Points

This header depends on the matching `dcn_3_0_2_offset.h` register address header. A field macro without a matching address macro, or an address mapped to the wrong field layout, can compile while silently programming the wrong bits.

`display/dc/resource/dcn302/dcn302_resource.c` is the main DCN 3.0.2 resource integration site. It includes this generated header, constructs DIO registers from `DIO_REG_LIST_DCN10()`, creates I2C engine tables for DDC instances 1 through 5, creates AUX tables for AUX instances 0 through 4, and creates HPD tables for HPD instances 0 through 4. The line-range content therefore feeds DIO construction, DDC/I2C hardware engines, DisplayPort AUX engines, HPD handling, and link encoder setup.

I2C/DDC fields integrate with `display/dc/dce/dce_i2c_hw.h` and `display/dc/dce/dce_i2c_hw.c`. Those paths define `struct dce_i2c_shift`, `struct dce_i2c_mask`, transaction action enums, arbitration/status enums, and the common I2C field lists. They use fields such as `DC_I2C_GO`, `DC_I2C_DDC_SELECT`, `DC_I2C_TRANSACTION_COUNT`, `DC_I2C_SW_USE_I2C_REG_REQ`, `DC_I2C_SW_DONE_USING_I2C_REG`, `DC_I2C_SW_STATUS`, `DC_I2C_DDC1_*`, transaction slot fields, and `DC_I2C_DATA`.

AUX fields integrate with `display/dc/dce/dce_aux.h`, `display/dc/dce/dce_aux.c`, and DCN link-encoder register definitions under `display/dc/dio/dcn10/` and `display/dc/dio/dcn20/`. `DCN2_AUX_REG_LIST(id)` maps per-instance `DP_AUX<n>` register addresses, while AUX mask lists consume the `DP_AUX0_AUX_*` field layout as the canonical per-instance field shape.

HPD fields integrate with GPIO and IRQ code, including `display/dc/gpio/hpd_regs.h`, hardware factory files under `display/dc/gpio/dcn*`, and generic IRQ handling in `display/dc/irq/irq_service.c`. The generated HPD fields back hotplug sense reads, polarity management, debouncing, RX interrupt enable/ack, and connector plug/unplug IRQ service.

OTG4 interrupt fields align with DCN IRQ source definitions under `include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`, where OTG4 vupdate, snapshot, force-count, force-vsync-next-line, trigger, GSL, vertical interrupt, DRR/range timing, static-screen, VSTARTUP, VREADY, and VSYNC-nominal events have source/context IDs. The higher-level timing-generator and hardware-sequencer code access these fields through generic OTG register tables assembled elsewhere in the same generated header family.

## Risks And Edge Cases

The chunk begins and ends mid-generated block. Earlier OTG4 timing fields appear before line 29916, and the `DP_AUX1_AUX_DPHY_TX_REF_CONTROL` mask list continues after line 32314. The final per-file report must reconcile those boundaries rather than treating this chunk as a complete standalone hardware description.

Repeated-instance families are copy-sensitive. HPD0 through HPD4 are structurally similar, and DP_AUX0/DP_AUX1 share nearly identical layouts. A one-instance generator error can affect only a specific connector or board routing, making regressions look monitor- or port-specific.

Ownership and arbitration fields are concurrency-sensitive. I2C and AUX engines can be requested by software and DMCU/firmware paths; wrong masks around `DC_I2C_ARBITRATION` or `DP_AUX*_AUX_ARB_CONTROL` can cause denied transactions, indefinite busy state, or races between driver and firmware.

Interrupt ack/mask/type fields use dense adjacent bits. A shifted mask in I2C, AUX, HPD, OTG, or perfmon interrupt control can either fail to clear an interrupt or mask the wrong source, leading to lost hotplug events, interrupt storms, missed DDC completion, or stuck AUX transactions.

Clock, reset, and memory-power fields affect block availability. Bad constants in `DIO_CLK_CNTL*`, `DIG_SOFT_RESET`, `DIO_MEM_PWR_*`, `OPTC_CLOCK_CONTROL`, or `ODM_MEM_PWR_*` can leave display blocks gated, reset, or unable to wake reliably.

Indexed data registers are prone to ordering bugs. `DC_I2C_DATA`, `DP_AUX0_AUX_SW_DATA`, `DP_AUX0_AUX_LS_DATA`, and the corresponding AUX1 data registers depend on index and autoincrement semantics; wrong field definitions can corrupt byte order or read/write the wrong FIFO slot.

## Test Signals

Useful validation signals include:

- Generated-header consistency checks that every visible field has the expected shift/mask pair, that masks are contiguous where the hardware spec expects contiguous fields, and that fields in repeated HPD/AUX instances match their intended siblings.
- Compile coverage of `dcn302_resource.c` with this header and `dcn_3_0_2_offset.h`, proving that resource tables, shift structs, and mask structs still resolve.
- Modeset and atomic page-flip tests that exercise OTG4, including vblank/vline delivery, VUPDATE/VREADY/VSTARTUP events, update-lock release, double-buffer pending completion, and cursor/flip pending status.
- Display CRC tests that use OTG CRC windows and readback fields to detect scanout mismatches.
- VRR/DRR tests on an OTG4-backed pipe, checking vtotal reach/update interrupts and trigger-window behavior.
- Hotplug tests across HPD0 through HPD4, including connect/disconnect debounce, delayed sense, RX interrupt ack/enable, and polarity handling.
- EDID/DDC reads across DDC1 through DDC5, including timeout/NACK/abort paths and DDC read-request interrupt acknowledgement.
- DisplayPort AUX transaction tests on AUX0 and AUX1, including successful native AUX/I2C-over-AUX reads and writes, HPD disconnect handling, timeout/error status decoding, reply byte count, and CP IRQ/low-speed update status where applicable.
- Power-management tests that suspend/resume or light-sleep DIO/I2C/AUX/DIG blocks while verifying that memory-power status, clock-on/busy, reset-done, and sideband transaction paths recover correctly.

### subset-b-001764: lines 32315-34689

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 32315-34689

## Purpose

This chunk is generated AMDGPU DCN 3.0.2 display-controller register field metadata. It contains no executable C logic; it publishes preprocessor constants that describe bit positions and bit masks inside DCN 3.0.2 MMIO registers. Consumers pair these constants with register offsets from `dcn_3_0_2_offset.h` and then use AMD display register helpers to read, update, poll, and write display hardware state.

The range is a mid-file slice. It starts at the final mask entry for `DP_AUX1_AUX_DPHY_TX_REF_CONTROL`, covers the remaining `DP_AUX1` DPHY/GTC/wake fields, then covers complete `DP_AUX2`, `DP_AUX3`, and `DP_AUX4` AUX blocks. It then covers the instance-0 stream-output families: `VPG0`, `AFMT0`, `DME0`, `DIG0`, and the beginning of `DP0`, ending with the complete `DP0_DP_DPHY_FAST_TRAINING_STATUS` register fields just before `DP0_DP_SEC_CNTL`.

Although this repository path is under a local `ceph-client` source tree, this file is AMD display-driver hardware metadata. It has no distributed filesystem protocol behavior and no Ceph persistence semantics.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or callbacks in this chunk. The API surface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT`: the least-significant-bit position for a field.
- `REGISTER__FIELD_MASK`: the already-positioned bit mask for that field.

The macros are consumed through higher-level register-description macros such as `SF`, `SE_SF`, `AUX_SF`, `LE_SF`, and driver helpers including `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and `REG_WAIT`. The generated constants are therefore an ABI-like contract between the ASIC register database and the DCN 3.0.2 display code.

Major field families in this range:

- `DP_AUX1` tail: DPHY TX/RX timing and status, GTC sync control/error/status, and AUX PHY wake handshaking.
- `DP_AUX2`, `DP_AUX3`, `DP_AUX4`: AUX enable/reset, low-speed read control, HPD selection, mode detection, impedance calibration request, arbitration, interrupt masking/ack/status, software AUX status and data, low-speed AUX status and data, DPHY TX/RX controls, GTC sync controls and errors, and PHY wake fields.
- `VPG0`: generic packet access/data bytes, conflict status/clear, generic-stream-packet frame-update and immediate-update bits for packet slots 0-14, generic packet memory power, ISRC access/data, and MPEG info packet fields.
- `AFMT0`: VBI and audio packet controls, audio channel enable/layout/oversampling overrides, HDMI/DP audio info bytes, IEC 60958 channel-status words, audio CRC controls/results, ramp controls, audio source selection, infoframe update, status, and AFMT memory power.
- `DME0`: DME enable/reset/ready, indirect index/data controls, register read/write controls, and DME memory power state.
- `DIG0`: stream encoder front-end and back-end fields, HDMI metadata/audio/ACR/VBI/infoframe/generic packet controls, generic packet line/send/continuous flags, gamut/control packet fields, TMDS control characters/sync/DC-balancer generation, FIFO status, CRC/test/random pattern controls, lane enablement, and forced DIG disable.
- `DP0`: DisplayPort link training completion, pixel format, MSA colorimetry/misc/timing/VBID, stream enable/status/deferred disable, steer FIFO overflow/ack bits, video `M/N`, link framing, HBR2 eye pattern, video interrupt clear/mask, DPHY FEC/bypass/training-pattern/symbol/8b10b/PRBS/scrambler/CRC/MST CRC/fast-training fields.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by the display driver:

1. `dcn302_resource.c` includes `dcn_3_0_2_offset.h` and this `dcn_3_0_2_sh_mask.h` file.
2. Resource construction macros paste register and field names into constants, for example `SRI(AUX_CONTROL, DP_AUX, id)` for addresses and `DCN_AUX_MASK_SH_LIST(__SHIFT)` or `DCN_AUX_MASK_SH_LIST(_MASK)` for AUX field tables.
3. VPG, AFMT, stream encoder, link encoder, and AUX objects receive per-block register addresses plus shift/mask tables.
4. Operational code uses those tables to perform read-modify-write updates, waits, status decoding, and error checks while programming connectors, AUX transactions, info packets, audio, HDMI/TMDS output, DisplayPort streams, and link training.

The macros do not encode safe ordering. Consumers must still handle reset sequencing, HPD/AUX arbitration, AUX transaction timeout handling, stream enable/disable waits, HDMI/DP packet update timing, AFMT memory power, link training, FEC state, CRC capture, and interrupt acknowledge behavior.

## State And Persistence Behavior

The chunk stores no software state and persists nothing on its own. It describes packed fields in GPU MMIO registers. The represented hardware state includes:

- AUX channel configuration, reset status, HPD routing, transaction status, reply/error bits, software and low-speed data bytes, DPHY timing/status, GTC sync lock/error state, and wake handshakes.
- VPG packet RAM access state, generic packet payload bytes, packet update triggers, conflict status, memory power state, ISRC data, and MPEG infoframe data.
- AFMT audio and infoframe state, including audio source, channel mapping, packet send/mute controls, IEC 60958 channel status, CRC test state, and memory power controls.
- DIG/HDMI/TMDS stream-encoder state for front-end source selection, start/stop, back-end enable, audio/video packet generation, ACR values and status, generic packet scheduling, test patterns, FIFO status, lane enable, TMDS symbol generation, and forced disable.
- DP0 link and stream state for link-training completion, stream enable/status, timing/colorimetry payloads, DPHY training/test generation, FEC status, PRBS/scrambler controls, CRC results, MST CRC phase status, and fast-training completion/ack bits.

Persistence is hardware-defined. Configuration fields typically retain values until a modeset, link reconfiguration, power-gating event, suspend/resume path, firmware action, or ASIC reset changes them. Status, interrupt, clear, ack, timeout, CRC, conflict, wake, and reset-done fields can be sticky, self-clearing, read-only, write-one-to-clear, or sequencing-sensitive. This generated header only defines bit layout; access semantics come from hardware documentation and the consuming AMD display code.

## Dependencies And Integration Points

The direct dependency is the matching offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h`

The direct include point found in this tree is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c`

Important consumer-side integration points include:

- `dcn302_resource.c`: builds DCN 3.0.2 resource tables, including AUX engines, link encoders, stream encoders, VPG, AFMT, and related display blocks.
- `dce/dce_aux.h` and `dce/dce_aux.c`: define AUX register and field lists, then use AUX status/error fields such as `AUX_SW_DONE`, `AUX_SW_REPLY_BYTE_COUNT`, timeout, invalid-stop, no-detect, HPD-disconnect, and NACK fields to drive DPCD/EDID AUX transactions.
- `dce/dce_link_encoder.h`, `dce/dce_link_encoder.c`, and `dio/dcn10/dcn10_link_encoder.h`: consume AUX, DP link, DP fast-training, and link-encoder fields for HPD routing, low-speed AUX reads, link training completion, stream disable, and fast training.
- `dce/dce_stream_encoder.h` and `dce/dce_stream_encoder.c`: consume `DIG0` and `DP0` stream fields for HDMI generic packets, DP stream enable/status waits, TMDS pixel/color format, DIG source selection, stereosync, and info packet scheduling.
- `dcn30/dcn30_vpg.h` and `dcn30/dcn30_vpg.c`: consume `VPG0` fields for generic packet data writes, conflict polling/clearing, and per-packet frame or immediate updates.
- `dcn30/dcn30_afmt.h` and `dcn30/dcn30_afmt.c`: consume `AFMT0` fields for audio source selection, channel enablement, IEC 60958 channel status, audio sample send/mute, audio-info update, and AFMT power behavior.

The generated file also depends on naming stability across AMD's register-generation pipeline. The consumer macros assume instance-0 field names such as `DP_AUX0_AUX_CONTROL__AUX_RESET_MASK`, `VPG0_VPG_GENERIC_PACKET_DATA__VPG_GENERIC_DATA_BYTE0_MASK`, `AFMT0_AFMT_AUDIO_PACKET_CONTROL__AFMT_AUDIO_SAMPLE_SEND_MASK`, `DIG0_DIG_FE_CNTL__DIG_START_MASK`, and `DP0_DP_VID_STREAM_CNTL__DP_VID_STREAM_ENABLE_MASK` exist and have compatible field positions for all repeated hardware instances described by the register tables.

## Risks And Edge Cases

- Wrong shifts or masks compile cleanly but cause silent hardware misprogramming. A bad mask can corrupt neighboring fields in packed MMIO registers, while a bad shift can decode status incorrectly or write an intended value into the wrong bit lane.
- Chunk boundaries are artificial. The first line is only the last mask of `DP_AUX1_AUX_DPHY_TX_REF_CONTROL`; its matching shifts and earlier masks are in the previous chunk. The next chunk starts with `DP0_DP_SEC_CNTL`. File-level conclusions must merge adjacent chunks.
- AUX fields are side-effect-sensitive. Incorrect reset, HPD selection, timeout, reply-byte-count, NACK, invalid-start/stop, overflow, arbitration, interrupt ack, or wake fields can break EDID reads, DPCD access, hotplug, link training, panel wake, or low-power resume.
- Repeated AUX instances are copy-sensitive. This chunk covers full `DP_AUX2` through `DP_AUX4`, and DCN 3.0.2 resources expose five AUX engines. A field drift in one repeated block may only appear on particular connectors or board routings.
- VPG packet update fields are timing-sensitive. Incorrect immediate/frame update masks, conflict clear/status bits, data index fields, or payload byte masks can corrupt HDMI/DP infoframes and metadata without necessarily causing a modeset failure.
- AFMT audio fields can fail as audio-only regressions. Bad IEC 60958 channel-number fields, audio source selection, sample-send, channel-enable, layout override, or memory power masks can cause silence, wrong channel mapping, or intermittent audio while video remains functional.
- DIG/HDMI/TMDS fields are broad and packed. Generic packet controls, ACR values, TMDS symbol generation, FIFO status, lane enable, source selection, and forced-disable fields affect HDMI display bring-up, color format, stereo sync, packet scheduling, and test modes.
- DP0 stream and DPHY fields interact with link state outside this header. Bad masks for `DP_LINK_TRAINING_COMPLETE`, stream enable/status, FEC, scrambler, PRBS, CRC, or fast-training status can produce blank displays, link retraining loops, CRC false positives, or failures limited to specific link rates, lane counts, MST paths, or panels.
- Some generated fields contain `MASK` as part of the field name, for example `DPHY_FAST_TRAINING_COMPLETE_MASK`. Consumers and validation scripts must distinguish the field name from the `_MASK` suffix when checking shift/mask pairs.

## Test Signals

Useful validation combines generated-header consistency with display hardware behavior:

- Build the AMDGPU display driver with DCN 3.0.2 support enabled. Missing or renamed macros should fail where `dcn302_resource.c`, AUX, link-encoder, stream-encoder, VPG, and AFMT tables are initialized.
- Mechanically verify that every field in lines 32315-34689 has the expected shift/mask pair after accounting for the artificial chunk start at the tail of `DP_AUX1_AUX_DPHY_TX_REF_CONTROL`.
- Diff the chunk against AMD's authoritative DCN 3.0.2 register database and nearby compatible generated headers, especially `dcn_3_0_0_sh_mask.h` and later DCN 3.x headers where unchanged hardware blocks are expected.
- Exercise all exposed AUX engines on DCN 3.0.2 hardware: HPD detection, EDID reads, DPCD reads/writes, AUX retry paths, timeout and disconnect handling, suspend/resume, and low-power wake.
- Test connector diversity and instance coverage: use systems or boards that route displays through high-numbered AUX/link/stream instances, not only instance 0.
- Validate HDMI output with audio and metadata: modeset, color format changes, generic packets, infoframes, ACR behavior, audio channel layout, mute/unmute, IEC 60958 status, and suspend/resume.
- Validate DP output: link training, fast training, link-rate and lane-count changes, stream enable/disable, MST where supported, FEC where supported, CRC capture, scrambler/PRBS test paths, and hotplug under load.
- Watch kernel logs and display diagnostics for AUX timeout/NACK/HPD-disconnect errors, link training failures, stuck `DP_VID_STREAM_STATUS`, packet conflicts, audio dropouts, FIFO/CRC errors, and resume regressions.

## Cross-Chunk Notes

Previous chunks own the beginning of the `DP_AUX1` block and the earlier DCN 3.0.2 field namespace. This chunk begins in the middle of `DP_AUX1_AUX_DPHY_TX_REF_CONTROL` and then covers `DP_AUX2` through `DP_AUX4` plus the first instance-0 stream/link blocks. The following chunk continues the `DP0` secondary-data packet and later DisplayPort fields. The final per-file research document should merge adjacent chunks before making complete claims about all AUX channels, all stream encoder instances, or the full DCN 3.0.2 link register surface.

### subset-b-001765: lines 34690-37088

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 34690-37088

## Scope

This chunk is a generated AMD DCN 3.0.2 ASIC register shift/mask header slice. It contributes preprocessor constants only: 2,171 `#define`s over 212 register names, with 1,093 `__SHIFT` constants and 1,078 `_MASK` constants. There are no C functions, structs, storage objects, or executable control flow in the chunk. The chunk starts at the tail of `DP0_DP_DPHY_FAST_TRAINING_STATUS`, covers the rest of the DIO/DIG0 and DIO/DIG1 display encoder register field map, and ends in the `VPG2_VPG_GSP_FRAME_UPDATE_CTRL` definitions.

## Purpose

The file provides the bit layout contract for Dimgrey Cavefish/DCN 3.0.2 display hardware registers. This chunk specifically maps field positions and bit masks for DisplayPort, HDMI/DIG, VPG generic secondary packets, AFMT audio formatter, DME metadata, and related display encoder control/status registers. Runtime driver code does not hard-code these numeric bit positions directly; it builds shift and mask tables from these generated names and passes those tables into reusable DCN 3.0 display block implementations.

## Register Areas Covered

- `DP0_*`: completes the DisplayPort instance 0 group, including secondary-data-packet control (`DP_SEC_CNTL*`), audio M/N and timestamp fields, MST/MSE allocation and status, MSA timing parameters, MSO controls, DSC packet controls, data-bypass controls, VBID miscellaneous fields, adaptive link power management (`DP_ALPM_CNTL`), and generic secondary packet controls `DP_GSP8_CNTL` through `DP_GSP11_CNTL`.
- `VPG1_*`: video packet generator instance 1 generic-packet access/data, frame-update and immediate-update controls for generic packets 0-14, generic packet conflict/status bits, memory power bits, ISRC access/data, and MPEG info registers.
- `AFMT1_*`: audio formatter instance 1 VBI/audio packet controls, audio info bytes, IEC 60958 channel-status registers, CRC/ramp/status fields, audio source selection, infoframe update, and memory power fields.
- `DME1_*`: metadata engine instance 1 enable, HUBP requestor id, stream type, memory light-sleep control, and memory power state fields.
- `DIG1_*`: digital front-end/output encoder instance 1 HDMI and TMDS control/status, generic HDMI packet controls 0-14, audio clock regeneration packets, infoframe controls, output CRC, test/random patterns, FIFO status, backend enable, lane enable, and force-disable fields.
- `DP1_*`: DisplayPort instance 1 link, pixel format, MSA, stream, DPHY training, PHY symbol/CRC/scramble controls, secondary packet/audio/MST/DSC/MSO/data-bypass/metadata/ALPM/GSP fields.
- `VPG2_*`: starts video packet generator instance 2, covering generic packet access/data and most of `VPG2_VPG_GSP_FRAME_UPDATE_CTRL`; the next chunk continues this VPG2 block.

## Important API and Type Contracts

This chunk's "API" is the macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the right-shift count for extracting or inserting a hardware bitfield.
- `<REGISTER>__<FIELD>_MASK` gives the register-width bit mask for that field.
- Register comments such as `//DP1_DP_SEC_CNTL` and address-block comments group fields by hardware block. The actual register addresses live in `dcn_3_0_2_offset.h`; this header supplies only field layout.

The values are consumed through macro indirection in `display/dc/resource/dcn302/dcn302_resource.c`:

- `SF(reg_name, field_name, post_fix)` expands to `.field_name = reg_name ## __ ## field_name ## post_fix`, so generated constants initialize typed shift/mask structs.
- `SRI(reg_name, block, id)` binds per-instance register addresses from the offset header, while this chunk supplies matching field layouts.
- `DCN3_VPG_MASK_SH_LIST(__SHIFT/_MASK)` and `DCN3_AFMT_MASK_SH_LIST(__SHIFT/_MASK)` initialize `struct dcn30_vpg_shift`, `struct dcn30_vpg_mask`, `struct dcn30_afmt_shift`, and `struct dcn30_afmt_mask`.
- `SE_COMMON_MASK_SH_LIST_DCN30(__SHIFT/_MASK)` initializes `struct dcn10_stream_encoder_shift` and `struct dcn10_stream_encoder_mask` for DP/HDMI/DIG stream encoder operations.

The practical dependent types are defined outside this generated header, especially in `display/dc/dcn30/dcn30_vpg.h`, `display/dc/dcn30/dcn30_afmt.h`, and `display/dc/dio/dcn30/dcn30_dio_stream_encoder.h`.

## Control Flow and Runtime Use

The chunk has no local branches or calls. Runtime control flow enters through DCN 3.0.2 resource creation:

1. `dcn302_resource.c` includes `dcn_3_0_2_offset.h` and this `dcn_3_0_2_sh_mask.h`.
2. Static register arrays and shift/mask structs are initialized at compile time using the generated constants.
3. `dcn302_resource_construct()` creates the DIO resource pool and stream encoders.
4. `dcn302_stream_encoder_create()` maps a DIG engine id to VPG and AFMT instances, calls `dcn302_vpg_create()` and `dcn302_afmt_create()`, and passes the resulting register/shift/mask tables to `dcn30_dio_stream_encoder_construct()`.
5. Later display operations use the reusable encoder, VPG, and AFMT methods to program DP secondary packets, HDMI infoframes, audio packets, DSC PPS packets, metadata packets, MST slot allocation, FIFO/status handling, and related hardware controls via these field definitions.

## State and Persistence

All state represented by this chunk is hardware register state. The header itself persists no software state and allocates no memory. Fields ending in `_PENDING`, `_STATUS`, `_ACK`, `_OCCURED`, `_CLR`, `_UPDATE`, or `_SEND_ACTIVE` are status/handshake bits in display hardware. Examples include VPG frame/immediate update pending bits, DP GSP send pending/deadline-missed bits, DP fast-training complete/ack bits, FIFO error/ack bits, and generic packet conflict clear/status bits. Misprogramming these fields can leave the driver waiting for an update, failing to clear a status, or writing a control bit into the wrong hardware field.

## Dependencies and Integration Points

- Depends on the matching DCN 3.0.2 register offset header for `mm...` register addresses and base indices.
- Depends on `dcn302_resource.c` macro glue (`SF`, `SRI`, `BASE`) to convert generated constants into block-specific tables.
- Integrates with DCN 3.0 reusable implementations for stream encoder, VPG, AFMT, DCE audio, link encoder, and resource-pool construction.
- The DP/HDMI/VPG/AFMT/DME definitions are part of the display path used by AMDGPU DC for modeset, audio enablement, info packet programming, DSC metadata, MST/MSO behavior, link training support, and power-management controls.
- Instance-specific groups (`DP0`, `DP1`, `DIG1`, `VPG1`, `AFMT1`, `DME1`, partial `VPG2`) must stay aligned with the instance numbering used by `VPG_DCN3_REG_LIST(id)`, `AFMT_DCN3_REG_LIST(id)`, and `SE_DCN3_REG_LIST(id)`.

## Risks

- Generated-header drift is the main risk: if masks/shifts do not match the hardware spec or the paired offset header, the compiler still succeeds but runtime register writes target wrong bits.
- Field-name drift breaks macro expansion at build time. For example, a missing `DP0_DP_SEC_CNTL__DP_SEC_GSP0_ENABLE_MASK` would break `SE_COMMON_MASK_SH_LIST_DCN30(_MASK)`.
- Instance asymmetry is risky. The generic mask/shift tables are often built from instance 0 names and reused across instances, so the bit layouts for `DP0`/`DP1`, `VPG0`/`VPG1`/`VPG2`, and `AFMT0`/`AFMT1` must remain equivalent where the common structs assume equivalence.
- Status/control bit confusion is possible because adjacent fields often pair command and pending bits, such as frame update versus frame update pending or send versus send pending.
- This chunk cuts off in the middle of the `VPG2` block, so whole-file analysis must reconcile the continued VPG2 definitions in the next chunk.

## Test and Validation Signals

- Compile coverage is strong for referenced names: missing or renamed macros fail initialization of DCN 3.0.2 shift/mask structs in `dcn302_resource.c`.
- Runtime smoke signals include successful modesets on DCN 3.0.2 hardware, DP link training, HDMI and DP audio, HDMI infoframes, DP secondary data packets, DSC PPS packet delivery, MST/MSO operation, and absence of FIFO/link-training/status timeout errors.
- Debugging signals include register dumps for DP/DIG/VPG/AFMT blocks, packet update pending bits clearing, GSP send status progressing, and expected audio/video info packets observed by sink-side compliance tools.
- Regression tests should compare generated mask/shift values with the authoritative ASIC register database, because many errors in this header are semantically invisible to normal build tests.

### subset-b-001766: lines 37089-39485

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 37089-39485

## Scope

This chunk is part of the generated DCN 3.0.2 shift/mask register header used by the AMD display driver. The range begins in the tail of the `VPG2_VPG_GSP_FRAME_UPDATE_CTRL` definitions, covers the remaining DIG2 display-output register blocks, covers all of the DP2 block in this file, and then starts the DIG3 block through the beginning of `DIG3_HDMI_GENERIC_PACKET_CONTROL5`.

The chunk contains macro constants only. There are no C functions, structs, or executable control-flow bodies in this range. Its 2,170 `#define` entries map hardware register bit fields to paired `__SHIFT` and `_MASK` constants that higher-level register-helper macros use to build read/modify/write operations.

Major register families covered here are:

- `VPG2_*`: video packet generator generic-packet update, immediate-update, status, memory-power, ISRC, and MPEG info fields for DIG2.
- `AFMT2_*`: audio formatter packet, audio infoframe, IEC 60958 channel-status, CRC, ramp, status, source, infoframe update, and memory-power fields for DIG2.
- `DME2_*`: metadata-engine enable, HUBP requestor, stream type, and light-sleep/power-state fields for DIG2.
- `DIG2_*` and `DIG3_*`: front-end/back-end controls, HDMI control, audio clock regeneration, metadata, VBI/infoframe/generic-packet controls, TMDS patterns, FIFO status, CRC, double-buffering, and link-disable controls.
- `DP2_*`: DisplayPort stream enable/status, timing M/N generation, main-stream attributes, PHY training/test/CRC/scrambler controls, secondary-data-packet controls, MST/MSE slot allocation, DSC, ALPM, metadata transmission, and GSP controls for secondary-data packets 8-11.
- The beginning of the DIG3 VPG/AFMT/DME/DIG/HDMI families, mirroring the DIG2 layout for engine instance 3.

## Purpose

The purpose of this header chunk is to provide the authoritative bit layout for DCN 3.0.2 display-output register fields. The runtime display code does not hard-code bit positions. Instead, resource construction code includes this header and populates per-block shift/mask tables. Register helpers such as `REG_UPDATE`, `REG_UPDATE_2`, `REG_SET_*`, and `REG_GET` then use those tables to pack field values into MMIO register writes or extract fields from MMIO reads.

This chunk is therefore a hardware-description layer, not a behavior implementation layer. Correctness depends on exact alignment with the ASIC register specification: if a shift or mask is wrong, otherwise-correct driver logic can write the wrong bits for HDMI info packets, DP stream state, metadata packets, audio format, DSC, or link-training support.

## Important APIs, Types, And Macros

The direct "APIs" exported by this chunk are preprocessor symbols in the form:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

For example, HDMI generic-packet fields are emitted for both DIG2 and DIG3 register instances, including send/continuous/line-reference/update-lock fields for generic packets 0-14 and immediate-send/pending fields. The fields are split across control registers: packets 0-7 primarily use `HDMI_GENERIC_PACKET_CONTROL0`, packets 8-14 use `HDMI_GENERIC_PACKET_CONTROL6`, line numbers live in packet-control registers 1-4 and 7-10 in surrounding chunks, and immediate sends use `HDMI_GENERIC_PACKET_CONTROL5`.

The important consumers are not in this header but in the AMD display register framework:

- `drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c` includes `dcn_3_0_2_offset.h` and this file, then builds static shift/mask tables such as `vpg_shift`, `vpg_mask`, `afmt_shift`, `afmt_mask`, `se_shift`, and `se_mask`.
- `DCN3_VPG_MASK_SH_LIST`, `DCN3_AFMT_MASK_SH_LIST`, and `SE_COMMON_MASK_SH_LIST_DCN30` expand through `SF`/`SE_SF` style macros to reference these generated `__SHIFT` and `_MASK` symbols.
- `dcn302_stream_encoder_create()` maps stream engines through DIGE to matching VPG and AFMT instances, then calls `dcn30_dio_stream_encoder_construct()` with the register table and this chunk's shift/mask data.
- `drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_stream_encoder.[ch]` uses the resulting tables when programming HDMI info packets, DP secondary data packets, metadata transmission, DSC controls, MSA timing fields, audio controls, and DME metadata fields.

The relevant runtime objects include `struct dcn10_stream_encoder`, `struct dcn10_stream_encoder_shift`, `struct dcn10_stream_encoder_mask`, `struct dcn30_vpg`, `struct dcn30_vpg_shift`, `struct dcn30_vpg_mask`, `struct dcn30_afmt`, `struct dcn30_afmt_shift`, and `struct dcn30_afmt_mask`.

## Control Flow

There is no local control flow in the chunk. All behavior appears when another compilation unit expands the macros into register metadata and passes that metadata into helper calls.

The effective runtime flow is:

1. DCN302 resource initialization includes this generated header.
2. Static register, shift, and mask tables are built from macro-list expansions.
3. Stream encoder, VPG, and AFMT objects are constructed with pointers to those tables.
4. Output paths call stream-encoder methods for HDMI, DP, audio, metadata, DSC, and infoframe programming.
5. Register helpers combine field values with the `__SHIFT` and `_MASK` constants from this header to perform MMIO read/modify/write operations.

For HDMI generic packets, `enc3_update_hdmi_info_packet()` chooses a packet index and writes `HDMI_GENERIC*_CONT`, `HDMI_GENERIC*_SEND`, and `HDMI_GENERIC*_LINE` fields. The DIG2/DIG3 definitions in this chunk provide the bit positions and masks used by those writes. For DP secondary packets, the stream encoder and related paths update fields such as `DP_SEC_STREAM_ENABLE`, `DP_SEC_GSP*_ENABLE`, `DP_SEC_GSP*_SEND`, line numbers, active/pending status, and PPS/DSC controls through the same shift/mask mechanism.

## State And Persistence Behavior

The header has no persistent state and allocates no memory. Its constants influence hardware state indirectly through MMIO writes performed by display code.

Hardware state affected by consumers includes:

- VPG generic-packet RAM access, packet-data bytes, frame-update and immediate-update request bits, pending bits, lock/conflict status, and VPG memory power mode.
- AFMT audio and infoframe state, including audio layout/channel enable, channel-status bytes, CRC test configuration/results, ramp generation, audio clock selection, audio source select, and memory power.
- DME metadata generation state, including enable, stream type, HUBP requestor selection, and memory power.
- DIG HDMI/TMDS state, including HDMI enable/status, deep color, scrambling, general control packets, null/ACP/ISRC packets, audio ACR values, metadata packets, generic packet scheduling, TMDS control characters, sync patterns, DC balancing, and FIFO diagnostics.
- DP link/stream state, including stream enable/status, pixel format, MSA fields, link framing, DPHY training/scrambling/CRC/test pattern state, secondary-packet transmission, MST/MSE allocation fields, DSC bytes-per-pixel and mode, ALPM PHY sleep/standby request bits, and GSP enable double-buffer status.

These register values persist in the display hardware until the driver rewrites them, the block is reset, or the GPU enters a power/reset transition that loses the register state.

## Dependencies

This chunk depends on the companion DCN 3.0.2 offset header for register addresses. A shift/mask pair is only useful when combined with the corresponding `mm<REGISTER>` address and base-index macros from `dcn_3_0_2_offset.h`.

It also depends on the AMD display register-helper abstraction:

- `reg_helper.h` supplies the macro machinery that turns a logical register field into a masked/shifted MMIO operation.
- DCN/DCE stream-encoder headers define the field-list macros that select which generated fields are present in a given hardware generation's register tables.
- DCN302 resource construction determines which engine IDs map to these instance-specific definitions. In this driver, DCN302 advertises five stream encoders and creates VPG/AFMT instances for engines through `ENGINE_ID_DIGE`; this chunk's DIG2 and DIG3 definitions are two entries in that per-instance set.

The hardware protocol dependencies are HDMI, DisplayPort, audio infoframe/channel-status, DisplayPort secondary-data-packet handling, Display Stream Compression, MST/MSE slot allocation, metadata transmission, and panel/link low-power signaling.

## Integration Points

The main integration point is `dcn302_resource.c`, which includes this header and builds the DCN302 hardware tables. The `stream_enc_regs`, `se_shift`, and `se_mask` tables are passed into `dcn30_dio_stream_encoder_construct()`, while `vpg_shift`/`vpg_mask` and `afmt_shift`/`afmt_mask` are passed to `vpg3_construct()` and `afmt3_construct()`.

The most visible downstream integration is `dcn30_dio_stream_encoder.c`. Its HDMI info-packet code calls the VPG packet-data updater, then sets the HDMI generic-packet control fields defined here. Its DP paths program `DP_SEC_*`, `DP_MSA_*`, `DP_DSC_*`, `DP_MSE_*`, and metadata fields through the same tables. Audio paths use AFMT and HDMI ACR fields. Link and stream setup paths use `DIG_FE_CNTL`, `DIG_BE_CNTL`, `DP_VID_STREAM_CNTL`, `DP_PIXEL_FORMAT`, and FIFO/status fields.

Because this is an instance-specific generated header, integrations rely on naming regularity. `DIG2_*` and `DIG3_*` fields must match the generic `DIG0_*` field-list names after macro substitution, and field names must remain identical across instances where the shared stream-encoder code expects them.

## Risks

The highest risk is silent hardware misprogramming from a wrong mask or shift. A compile succeeds as long as the symbol exists, but an incorrect bit layout can break output without an obvious software error. Examples include:

- HDMI or DP info packets not being sent, sent continuously when they should not be, or sent on the wrong line.
- Audio failures from wrong AFMT channel, layout, ACR, or IEC 60958 channel-status fields.
- DP stream bring-up failures from wrong `DP_VID_STREAM_ENABLE`, `DP_VID_STREAM_STATUS`, M/N, MSA, DPHY, or link-framing fields.
- MST/MSE allocation errors from wrong slot-count, SAT update, or per-slot fields.
- DSC or PPS transport failures from wrong `DP_DSC_*` or GSP11/PPS-related fields.
- Metadata and HDR packet loss from wrong DME, HDMI metadata, or DP secondary metadata fields.
- Power-management issues if light-sleep or memory-power fields are mis-specified for VPG/AFMT/DME.

Boundary risk is present in this research chunk because it starts mid-register at the remaining `VPG2_VPG_GSP_FRAME_UPDATE_CTRL` mask definitions and ends mid-register in `DIG3_HDMI_GENERIC_PACKET_CONTROL5`. The final per-file reconciliation should merge adjacent chunks so that those split register definitions are described as complete blocks.

## Test Signals

Useful test signals are mostly integration and hardware-observation signals rather than unit tests for this generated header:

- A successful AMDGPU/DC build for DCN302 confirms all expected shift/mask symbols still exist and macro-list expansions compile.
- Booting on DCN 3.0.2 hardware with HDMI and DP displays confirms basic stream encoder, link, and packet register programming.
- HDMI validation should check AVI/vendor/SPD/HDR/VTEM infoframes, deep color, scrambling, audio packets, ACR/N/CTS values, and generic-packet scheduling.
- DP validation should check stream enable/status, MSA timing, audio SDP, VSC/SPD/HDR secondary packets, MST/MSE allocation where applicable, DSC/PPS transmission, and metadata packets.
- Register readback through debugfs or driver tracing should show field values landing in the expected bits for `DIG2_*`, `DP2_*`, and `DIG3_*` registers after `REG_UPDATE` and `REG_SET_*` calls.
- Negative signals include black screens after link training, FIFO level errors, missing HDR metadata, HDMI audio loss, DP audio loss, DSC negotiation failures, MST stream allocation failures, or repeated pending bits in generic-packet/frame-update registers.

### subset-b-001767: lines 39486-41907

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 39486-41907

Chunk: `subset-b-001767`
Covered source range: lines 39486-41907 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h`

## Purpose

This chunk is part of AMD's generated DCN 3.0.2 register field mask header. It does not implement executable driver behavior. Its purpose is to publish C preprocessor constants for bit shifts and bit masks used when AMDGPU display code reads, writes, or read-modify-writes DCN digital output, HDMI, DisplayPort, video packet generator, audio format, metadata engine, and DisplayPort secondary-data registers.

The file pairs with DCN register address headers and is directly included by `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c`. Resource construction and hardware block descriptors use these generated names to bind register lists, masks, and shifts for DCN 3.0.2 ASICs. Consumers typically do not use the numeric literals directly; they use register helper macros and hardware sequencer code that combine an address macro with the matching `__SHIFT` and `_MASK` constants.

This range covers the tail of the DIG3 HDMI generic packet block, the remaining DIG3 HDMI/TMDS/backend fields, a full DP3 display-port output block, the beginning-to-end DIG4-side VPG/AFMT/DME/DIG HDMI/TMDS block, and the beginning of DP4 through `DP4_DP_MSE_SAT0`. The high-level register families are:

- DIG3 HDMI generic packet immediate-send, line-selection, double-buffer, guard-band/control, ACR, audio clock, backend enable/source, TMDS control, lane enable, and force-disable fields.
- DP3 DisplayPort link, stream, main stream attribute, video timing, PHY training, 8b/10b, PRBS, scrambler, CRC, fast training, secondary packet, MST/MSE, MSO, DSC, metadata, GSP, ALPM, and double-buffer fields.
- DIG4 VPG generic packet access/data, GSP update/status, memory power, ISRC, and MPEG info fields.
- AFMT4 audio packet, HDMI/DP audio info, IEC 60958 channel-status, audio CRC, ramp/test audio, audio status, audio source, and memory power fields.
- DME4 metadata engine enable, stream selection, HUBP requestor, double-buffer, and memory power fields.
- DIG4 frontend, output CRC, test pattern, FIFO status, HDMI metadata/control/status, ACR/VBI/infoframe/generic packet, HDMI double-buffer, ACR status, audio clock, backend, TMDS, lane enable, and force-disable fields.
- DP4 DisplayPort link, stream, MSA, timing, PHY, CRC, fast training, secondary packet, audio M/N, MSE rate, and the start of SAT0 slot-allocation fields.

## Important APIs, Types, And Macros

There are no functions, structs, enums, typedefs, or runtime APIs in this chunk. The public surface is a generated macro API. Each field normally appears as two macros:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used to shift a raw field value into or out of a register dword.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate or update that field.

The prefix identifies the display block instance and register domain. `DIG3_*` and `DIG4_*` describe digital encoder/frontend/backend and HDMI/TMDS fields for links 3 and 4. `DP3_*` and `DP4_*` describe DisplayPort link-output registers for DP instances 3 and 4. `VPG4_*`, `AFMT4_*`, and `DME4_*` describe the video packet generator, audio format, and metadata engine blocks associated with DIG4.

Important DIG3 fields in this range include:

- `DIG3_HDMI_GENERIC_PACKET_CONTROL5` immediate-send and pending flags for generic packets 0-14.
- `DIG3_HDMI_GC` AVMUTE, continuous AVMUTE, default phase, packing phase, and packing override fields.
- `DIG3_HDMI_GENERIC_PACKET_CONTROL1` through `CONTROL10` line-number fields for generic packets and `HDMI_GENERIC*_EN_DB_PENDING` double-buffer-pending bits.
- `DIG3_HDMI_DB_CONTROL` pending/taken/clear/lock/disable bits for HDMI and vupdate double-buffer state.
- `DIG3_HDMI_ACR_*` and `DIG3_HDMI_ACR_STATUS_*` CTS/N fields for 32, 44.1, and 48 kHz audio clock regeneration.
- `DIG3_AFMT_CNTL`, `DIG3_DIG_BE_CNTL`, and `DIG3_DIG_BE_EN_CNTL` audio clock, backend source/mode/HPD, DIG enable, and backend symbol clock status fields.
- `DIG3_TMDS_*` sync phase, control characters, sync patterns, control-bit generation, DC balancer, lane enable, DIG version, and force-disable fields.

Important DP3 fields cover nearly the full DisplayPort output programming surface:

- Link and stream control: `DP3_DP_LINK_CNTL`, `DP3_DP_PIXEL_FORMAT`, `DP3_DP_CONFIG`, `DP3_DP_VID_STREAM_CNTL`, `DP3_DP_LINK_FRAMING_CNTL`, and `DP3_DP_VID_INTERRUPT_CNTL`.
- Timing and MSA fields: `DP3_DP_MSA_COLORIMETRY`, `DP3_DP_MSA_MISC`, `DP3_DP_VID_TIMING`, `DP3_DP_VID_N`, `DP3_DP_VID_M`, `DP3_DP_VID_MSA_VBID`, and `DP3_DP_MSA_TIMING_PARAM1` through `PARAM4`.
- PHY and training fields: `DP3_DP_DPHY_CNTL`, `DP3_DP_DPHY_TRAINING_PATTERN_SEL`, `DP3_DP_DPHY_SYM0` through `SYM2`, `DP3_DP_DPHY_8B10B_CNTL`, `DP3_DP_DPHY_PRBS_CNTL`, `DP3_DP_DPHY_SCRAM_CNTL`, `DP3_DP_DPHY_FAST_TRAINING`, and `DP3_DP_DPHY_FAST_TRAINING_STATUS`.
- CRC and diagnostics: `DP3_DP_DPHY_CRC_EN`, `CRC_CNTL`, `CRC_RESULT`, `CRC_MST_CNTL`, and `CRC_MST_STATUS`.
- Secondary data and audio: `DP3_DP_SEC_CNTL`, `SEC_CNTL1` through `SEC_CNTL7`, `SEC_FRAMING1` through `SEC_FRAMING4`, `SEC_AUD_N`, `SEC_AUD_M`, readbacks, timestamp, packet control, metadata transmission, and GSP8-GSP11 controls.
- MST/MSO/DSC: `DP3_DP_MSE_RATE_CNTL`, `MSE_RATE_UPDATE`, `MSE_SAT0` through `SAT2`, `MSE_SAT*_STATUS`, `MSE_LINK_TIMING`, `MSE_MISC_CNTL`, `MSO_CNTL`, `MSO_CNTL1`, `DSC_CNTL`, and `DSC_BYTES_PER_PIXEL`.
- Double-buffer and low-power state: `DP3_DP_DB_CNTL`, `DP3_DP_MSA_VBID_MISC`, `DP3_DP_ALPM_CNTL`, and `DP3_DP_GSP_EN_DB_STATUS`.

DIG4-associated blocks mirror many DIG3 and DP3 concepts for a later instance while adding VPG, AFMT, and DME coverage:

- `VPG4_VPG_GENERIC_PACKET_ACCESS_CTRL`, `DATA`, `GSP_FRAME_UPDATE_CTRL`, `GSP_IMMEDIATE_UPDATE_CTRL`, `GENERIC_STATUS`, `MEM_PWR`, `ISRC1_2_*`, and `MPEG_INFO*` define packet RAM access, update modes, pending status, memory power, and infoframe payload fields.
- `AFMT4_AFMT_*` defines VBI/audio packet control, audio infoframe fields, 60958 channel status, audio CRC controls/results, ramp/test-audio counters, status/overflow bits, source selection, and AFMT memory power state.
- `DME4_DME_CONTROL` and `DME4_DME_MEMORY_CONTROL` define metadata-engine requestor ID, enable, stream type, double-buffer handshake, and memory power controls.
- `DIG4_DIG_FE_CNTL`, output CRC, clock/test/random pattern, FIFO status, HDMI metadata, HDMI control/status, ACR/VBI/infoframe/generic-packet controls, HDMI double-buffer controls, ACR CTS/N, AFMT clock, backend, TMDS, lane enable, and force-disable fields define the DIG4 HDMI/TMDS path.
- `DP4_*` begins another DisplayPort instance. This chunk covers link status, pixel format, stream enable/status, FIFO overflow, MSA/misc/timing, M/N, framing, HBR2 eye pattern, VBID, video interrupt, DPHY FEC/bypass/training/symbol/8b10b/PRBS/scrambler, CRC, fast training, secondary packet/audio fields, MSE rate update, and the first three fields of `DP4_DP_MSE_SAT0`.

## Control Flow

This header chunk has no runtime control flow. It is a compile-time register contract.

Runtime control flow appears in the display driver code that includes the generated header and passes these constants through DC register helper layers. A typical consumer path is:

1. The DCN 3.0.2 resource code selects register, shift, and mask tables for an ASIC generation.
2. Link encoder, stream encoder, audio, VPG, AFMT, DME, or DisplayPort helper code chooses a symbolic register field based on requested display state.
3. Register helpers read the current MMIO dword, clear bits using the `_MASK`, insert a field value shifted by `__SHIFT`, and write the dword back.
4. For handshake fields, the caller may poll status bits such as pending, taken, active, complete, overflow, CRC-valid, FIFO error, link status, or audio/status flags.

The implicit hardware programming sequence for the covered registers is ordered by display bring-up and update flows rather than by this header. For example, HDMI generic packets are prepared in VPG or HDMI packet memory, line/control/send bits are armed, double-buffer pending/taken state is observed, and packets are emitted during the selected video line or immediately. DisplayPort streams similarly require link/training state, pixel format, timing/M/N, MSA/VBID, secondary-data/audio packet setup, and stream enablement to be coherent. The header only defines the bit locations needed by those sequences.

## State And Persistence Behavior

The header itself is stateless and persists no data. It contributes numeric constants to compiled driver objects.

The hardware fields described by the macros are stateful MMIO bits. They include durable-until-reset programming state, transient handshake state, status/interrupt state, and diagnostic counters/results:

- Configuration state: pixel encoding, component depth, lane enables, link framing, MSA timing, video M/N, DP/HDMI packet enables, packet line numbers, audio CTS/N, 60958 audio channel-status, metadata stream selection, memory-power controls, test patterns, DSC mode, MSO/MSE settings, and ALPM/low-power controls.
- Handshake and double-buffer state: HDMI/DP/VPG/DME DB pending/taken/clear/disable/lock fields, generic packet update-pending fields, MSE rate/SAT update-pending fields, GSP send/pending/deadline-missed/active/in-idle fields, and vupdate-taken fields.
- Runtime status: link-training complete/status, stream status, FIFO overflow/error/calibration state, HDMI packet errors, AVMUTE state, AFMT audio enable/FIFO overflow, DPHY CRC valid/results, MST CRC phase status, fast-training state/completion, collision status, audio mute status, metadata-packet missed bits, and GSP enable DB status.
- Test and diagnostic state: output CRC enable/result, PRBS enable/seed, 8b/10b disparity controls, scrambler advance/count/K-code, HBR2 eye pattern, static/random/clock patterns, audio CRC results, and ramp generator counters.

Persistence is indirect and hardware-dependent. Some settings are reprogrammed during modeset, stream enable, audio enable, suspend/resume, link retraining, or GPU reset. Some status bits must be acknowledged using paired ACK or CLR fields. Because the generated masks do not encode access semantics, caller code must know which fields are read-only, write-one-to-clear, pulse-triggered, double-buffered, or safe for read-modify-write.

## Dependencies And Integration Points

Direct dependencies are minimal: a C preprocessor and code including this header. The important dependency is semantic alignment with the rest of the generated DCN 3.0.2 register set:

- matching address headers under `include/asic_reg/dcn/`, which provide register offsets for these field masks;
- DCN 3.0.2 resource definitions in `display/dc/resource/dcn302/dcn302_resource.c`, which include this header and bind register tables for hardware blocks;
- display core register helper macros that expect `__SHIFT` and `_MASK` naming conventions;
- link encoder, stream encoder, audio, VPG, AFMT, DME, DisplayPort, HDMI, MST, DSC, and panel/link power-management code that consumes the generated tables.

The covered registers integrate with external display protocols and AMD display hardware blocks:

- HDMI/TMDS integration includes generic packets, audio/video infoframes, ACR, AVMUTE, deep color, scrambling, metadata packets, VBI packets, control characters, and TMDS DC balancing.
- DisplayPort integration includes link training, MSA/VBID, SST/MST secondary data packets, MSE slot allocation, MSO, FEC, DSC, CRC, PRBS, scrambler, audio M/N, ALPM, and fast training.
- VPG and DME integration covers dynamic metadata, Dolby Vision metadata-missed status, HDR/metadata packet scheduling, and packet-memory access.
- AFMT integration covers audio sample packet generation, audio test/ramp generation, HDMI/DP audio infoframes, IEC 60958 channel-status, FIFO overflow handling, and audio CRC diagnostics.

The same conceptual blocks repeat across DCN instances. DIG3/DP3 and DIG4/DP4 fields are intentionally near-identical in many places, but their prefixes bind them to different hardware instances. Instance confusion can compile cleanly and still program the wrong link.

## Risks And Edge Cases

Generated register headers are silicon contracts. A numeric shift or mask change can silently alter display hardware programming while leaving all C code type-correct.

Important risk areas in this chunk include:

- Double-buffer and pending/taken bits. HDMI, DP, VPG, DME, MSE, and GSP registers contain many pending, taken, clear, disable, and lock bits. Using the wrong mask can leave updates stuck pending, clear a status bit prematurely, or apply packet data at the wrong vupdate boundary.
- Packet scheduling. HDMI generic packets, DP secondary data packets, GSP packets, metadata packets, ISRC, MPEG, audio info, and VBI packets have line-reference and line-number fields. Bad line fields can miss vblank deadlines or produce visible/receiver-side protocol errors.
- Audio correctness. ACR CTS/N, DP audio M/N, AFMT 60958 channel-status, sample-send, FIFO overflow ACK, and audio infoframe fields must match audio format and link timing. Wrong masks can cause muted, distorted, or intermittent HDMI/DP audio.
- Link training and PHY diagnostics. DPHY training pattern, FEC, PRBS, scrambler, 8b/10b, fast-training, HBR2 eye pattern, CRC, and symbol fields affect link bring-up and compliance diagnostics. Accidental writes can destabilize a live link.
- MST/MSO/DSC programming. MSE rate, SAT slot allocation, SAT status, MSO stream enables, and DSC bytes-per-pixel/slice fields are tightly coupled to bandwidth allocation. Incorrect masks can break MST payload allocation or DSC stream decode.
- Status/ACK semantics. Many fields are status, interrupt, or write-one-to-clear style bits. The mask header alone does not distinguish those semantics, so callers must avoid blind read-modify-write patterns on registers containing ACK/CLR/pulse fields.
- Instance boundaries. The chunk begins in the middle of `DIG3_HDMI_GENERIC_PACKET_CONTROL5` and ends in the middle of `DP4_DP_MSE_SAT0`. Final file-level analysis must merge this with adjacent chunks before making conclusions about those complete register groups.

Because this header is generated, manual edits should be treated as high risk unless they are regenerated from the authoritative register database and checked against matching address headers and resource tables.

## Test Signals

The most useful validation is compile-time consistency plus hardware/display behavior:

- Build the AMDGPU DCN 3.0.2 display path, especially translation units that include `dcn_3_0_2_sh_mask.h` through `dcn302_resource.c`.
- Static-check macro consistency: every field used by DCN 3.0.2 register tables has both a `__SHIFT` and `_MASK`, duplicated instance groups retain expected per-instance prefixes, and masks align with shifts and field widths.
- Compare generated output against the authoritative AMD register source for DCN 3.0.2; manual diffs in this file should be suspicious.
- Exercise HDMI modes with generic packets, audio infoframes, metadata packets, ACR, AVMUTE, deep color, scrambling, and TMDS control-character behavior.
- Exercise DisplayPort SST and MST modes that cover stream enable/disable, MSA timing, VBID, secondary data packets, MSE slot allocation, MSO, DSC, FEC, link retraining, fast training, ALPM, and audio M/N.
- Validate packet double-buffer behavior by changing infoframes, metadata, HDR/Dolby Vision packets, and generic packets across vblank without missed-packet or stale-packet artifacts.
- Run audio tests over HDMI and DP for 32 kHz, 44.1 kHz, 48 kHz, HBR/non-HBR, channel-status updates, FIFO overflow handling, and audio CRC diagnostics.
- Run display CRC and DP DPHY CRC tests where supported, checking valid/result bits and ACK behavior.
- Test suspend/resume, hotplug, modeset, link-loss recovery, and GPU reset paths to verify DIG3/DIG4, DP3/DP4, VPG4, AFMT4, and DME4 state is restored or intentionally reinitialized.
- On MST/DSC-capable monitors, verify payload allocation, DSC slice/bytes-per-pixel setup, secondary packet transmission, and metadata packet delivery remain correct across topology changes.

### subset-b-001768: lines 41908-44291

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 41908-44291

## Scope And Purpose

This chunk is a generated register shift/mask section for AMD Display Core Next 3.0.2 (`dcn_3_0_2`). It does not implement executable control flow; instead it defines C preprocessor constants that describe bit positions and bit masks for memory-mapped display hardware registers. The constants are consumed by AMDGPU display code through register descriptor tables and helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, and per-block field-list macros that bind `__SHIFT` and `_MASK` values into typed register access structures.

The requested slice starts in the middle of the DP4 register block, with the last visible mask for `DP4_DP_MSE_SAT0`, and continues through complete blocks for DP4 secondary data packets, DCIO, GPIO/pad controls, DSC0 encoder and perfmon registers, then reaches the beginning of the DSC1 encoder block and ends mid-register in `DSCC1_DSCC_INTERRUPT_CONTROL_STATUS`. The surrounding header-level purpose is to provide the hardware contract for DCN 3.0.2 register programming: callers use these definitions to pack field values into 32-bit register writes and unpack status fields from 32-bit register reads without hard-coding shifts or masks at each call site.

## Register Families Covered

The DP4 section covers DisplayPort stream/link encoder fields for a fourth DP instance. It includes MST stream allocation table registers (`DP4_DP_MSE_SAT1`, `SAT2`, update/status registers, link timing, and misc control), Main Stream Attribute timing parameters (`DP_MSA_TIMING_PARAM1` through `PARAM4`), Multi-Stream Operation controls (`DP_MSO_CNTL`, `CNTL1`), DSC-over-DP controls (`DP_DSC_CNTL`, `DP_DSC_BYTES_PER_PIXEL`), secondary packet controls (`DP_SEC_CNTL2` through `CNTL7`), double-buffer control (`DP_DB_CNTL`), VBID override fields (`DP_MSA_VBID_MISC`), metadata transmission, ALPM link power management, and GSP8 through GSP11 packet controls. These fields support DisplayPort MST/MSO scheduling, secondary data packet timing, audio/video metadata delivery, DSC payload signalling, double-buffered update handshakes, and low-power link transitions.

The DCIO display-decoder block starts at `dce_dc_dcio_dcio_dispdec`. It defines generic clock/test output selectors (`DC_GENERICA`, `DC_GENERICB`), clock gating (`DCIO_CLOCK_CNTL`), reference clock output selection (`DC_REF_CLK_CNTL`), UNIPHY link controls for PHY A through E, per-lane channel crossbar selection, write-command delays, pin strap readouts, LVTMA panel power sequencing, backlight PWM control, GSL/genlock and swaplock pad controls, and soft-reset bits for UNIPHY/DSYNC/DCRXPHY/ZCAL paths. These masks are used when the display resource layer creates and programs link encoders, panel controls, clock sources, and output PHY state.

The DCIO chip-level GPIO block starts at `dce_dc_dcio_dcio_chip_dispdec`. It describes generic GPIO pads, DDC/AUX pads, VGA DDC, genlock, hot-plug detect, panel power-sequence pads, pad-strength registers, AUX PHY tuning/control, TX/RX enables, pullups, and power-good status. Register naming follows a repeated pattern: `_MASK` registers select pad ownership and pull-down or receive behavior, `_A` registers expose input/sample values, `_EN` registers control output enable, and `_Y` registers drive output values. DDC1 through DDC5 and DDCVGA are represented as clock/data pairs; HPD exposes six hot-plug detect pins; AUX controls expose termination, polarity, hysteresis, voltage/output drive tuning, I2C mode, and per-pad power state.

The DSC0 section spans three address blocks: `dce_dc_dsc0_dispdec_dsc_top_dispdec`, `dce_dc_dsc0_dispdec_dsccif_dispdec`, and `dce_dc_dsc0_dispdec_dscc_dispdec`. It defines top-level DSC clock/debug controls, DSCC input interface configuration, core DSC encoder configuration, interrupt/status bits for rate-buffer and rate-control-buffer events, PPS configuration registers `DSCC0_DSCC_PPS_CONFIG0` through `CONFIG22`, memory power controls, error counters, buffer fullness monitors, and debug bus rotation. These fields map closely to Display Stream Compression PPS and rate-control concepts: version, bits per component/pixel, picture and slice dimensions, initial delays, scale intervals, BPG offsets, model size, quantization limits, buffer thresholds, and range parameters.

The `DC_PERFMON19` block is associated with the DSC0 display-decoder perfmon address block. It exposes eight performance counter controls, counter-state controls, top-level perfmon enable/state/report-count fields, count-off interrupt configuration, counter interrupt status/ack bits, and low/high readback fields. These masks support driver or debug tooling that selects internal DSC/display events, starts/stops counters by hardware signals, reads accumulated values, and acknowledges threshold interrupts.

The DSC1 section starts near the end of this chunk. It mirrors the top, DSCCIF, and early DSCC fields from DSC0 for a second DSC instance: top clock/debug controls, input interface config, picture dimensions, core slice/ICH config, rate-control model size, double-buffer pending status, and the beginning of rate-buffer/rate-control-buffer interrupt status and interrupt-enable masks. The chunk ends before the complete DSC1 PPS register set appears, so this document only covers the visible early DSC1 fields.

## Important APIs, Types, And Macro Contract

This file exports only preprocessor symbols. The important API contract is the naming convention:

- `REGISTER__FIELD__SHIFT` gives the bit position used when encoding or decoding a field.
- `REGISTER__FIELD_MASK` gives the field mask in the final 32-bit register value.
- Address-block comments group related registers by hardware block but do not affect compilation.

Higher-level AMD display code generally does not reference every constant directly. It uses macro lists in block-specific headers and resource constructors to initialize register structures. For DSC, headers such as `display/dc/dsc/dcn20/dcn20_dsc.h` declare field lists with `DSC_SF(..., mask_sh)`, then implementation files use `REG_SET_*`/`REG_UPDATE` helpers to program PPS and control fields. For DCN 3.0.2 specifically, `display/dc/resource/dcn302/dcn302_resource.c` includes this `dcn_3_0_2_sh_mask.h` together with the matching offset header, then creates DCN302 resource objects for stream encoders, DSC engines, AUX/I2C engines, link encoders, panel controls, and other display blocks.

The DP4 fields integrate with DIO/link encoder and stream encoder code that pairs these field masks with matching register offsets from `dcn_3_0_2_offset.h`. The GPIO fields integrate with GPIO factory and hardware abstractions for DDC, AUX, HPD, generic GPIO, genlock/swaplock, and panel power sequencing. The perfmon fields integrate with diagnostic counter paths rather than normal modesetting logic.

## Control Flow And Data Flow

There is no runtime control flow inside this chunk. Runtime behavior emerges when other driver code includes the header and calls register helper macros:

1. Resource construction selects the DCN302 offset and mask headers for the ASIC.
2. Block constructors build per-instance register address tables and shift/mask tables.
3. Modeset, link training, hotplug, panel, DSC, or diagnostics code calls typed helper functions.
4. Helper macros read or write memory-mapped registers, using the shift and mask constants to preserve unrelated bits and encode only the requested field.
5. Hardware latches or reports state through the corresponding register fields, including double-buffer pending bits, send-pending bits, interrupt status bits, power-sequence done bits, HPD samples, and counter readbacks.

Several groups represent hardware handshakes rather than simple configuration. DP secondary packet and GSP registers expose send, pending, active, deadline-missed, and send-in-idle bits. DP and DSC double-buffer fields expose pending/taken/update status. LVTMA power sequencing exposes target state, DIGON/SYNCEN/BLON, and done/state readbacks. Interrupt/status registers combine occurrence bits and interrupt-enable bits, and some companion control registers contain ack/clear fields in nearby chunks or related blocks.

## State And Persistence Behavior

The macros themselves carry no mutable state, but the hardware registers they describe are persistent device state until overwritten, reset, power-gated, or reinitialized by modeset sequences. Important state categories in this chunk include:

- Link and stream state: DP4 MST slot allocation, MSA timing, MSO packet enable masks, secondary packet scheduling, DSC payload fields, VBID overrides, metadata packet timing, and ALPM requests persist in the DP encoder until reprogrammed.
- Pad and PHY state: UNIPHY lane inversion/crossbar/link-enable fields, DCIO soft resets, AUX/DDC pad tuning, RX/pullup/TX enables, and GPIO output values persist as hardware pad configuration and directly affect connector behavior.
- Panel state: LVTMA power-sequence and backlight PWM fields persist across display enable/disable transitions until the panel control code changes them or a reset occurs.
- DSC state: PPS, picture/slice dimensions, rate-control parameters, input format, memory power settings, and interrupt enables persist inside each DSC instance. Double-buffer pending fields indicate when hardware has accepted or is still waiting to apply a programmed state.
- Diagnostic state: `DC_PERFMON19` counter selections, counter states, interrupt status/ack, and accumulated high/low values persist until the perfmon is stopped, cleared, acknowledged, or the block is reset.

Because these are low-level MMIO definitions, persistence semantics are hardware-defined. The driver must sequence writes around vblank, double-buffer update windows, power state, and link training state; the header only supplies bit positions.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.0.2 register offset header for actual addresses. A shift/mask constant is not useful unless paired with the corresponding `mm...` register offset and base index. It also depends on AMD display register-access infrastructure, including generated register structs, `REG_*` helper macros, DC context MMIO accessors, and per-block field descriptor arrays.

Major integration points are:

- `display/dc/resource/dcn302/dcn302_resource.c`, which includes this header and wires DCN302 resources to the proper register/mask tables.
- DSC block code under `display/dc/dsc/`, which programs DSC top, DSCCIF, DSCC, PPS, memory power, and status fields using field-list macros and register helpers.
- DIO/link encoder and stream encoder code, which uses DP stream/link fields for MSA programming, secondary data packet scheduling, MST/MSO behavior, DSC-over-DP signalling, and link power management.
- GPIO and AUX/I2C hardware factories, which use GPIO, DDC, AUX, HPD, and generic pad fields for connector detection, EDID/DDC access, AUX transactions, and board-specific pin programming.
- Panel control and power-sequence code, which uses LVTMA and backlight PWM fields to control embedded-panel power rails, sync enable, digital enable, and brightness output.
- Debug/performance tooling paths, which use `DC_PERFMON19` field selections and readback registers to observe display-block activity.

The source path is under `drivers/gpu/drm/amd/include/asic_reg/dcn`, so it is part of the Linux AMDGPU display hardware definition layer. Changes here have broad compile-time reach because many resource constructors and hardware blocks include the ASIC-specific generated headers.

## Risks And Edge Cases

The primary risk is incorrect bit layout. A wrong shift or mask can silently write the wrong hardware field, preserve stale bits, clear adjacent fields, or decode status incorrectly. In this chunk, that risk affects high-impact display behavior: connector detection, AUX/DDC access, DP MST allocation, DSC bitstream validity, link power management, panel/backlight sequencing, and interrupt handling.

Generated-header consistency is critical. The same field name must match between offset headers, mask headers, register-list macros, and implementation code. Renaming or dropping a field can break compilation where `*_SF(..., mask_sh)` expands to missing symbols. Keeping a stale mask while hardware changed the register layout can compile cleanly but fail only on affected ASICs or connector configurations.

The chunk contains repeated per-instance patterns. DP4 fields mirror other DP instances, UNIPHY A-E fields share the same layout, DDC1-DDC5 fields repeat, HPD1-HPD6 fields repeat, and DSC0/DSC1 fields mirror each other. Copy-generation errors are plausible: an instance number may be wrong, a mask may use another instance's field width, or a later instance may have a truncated field set. The visible `DSC_TOP1_DSC_DEBUG_CONTROL` block has `DSC_DBG_EN_MASK` in this chunk while its `DSC_TEST_CLOCK_MUX_SEL_MASK` appears outside the visible range or is absent here, so consumers must rely on the full file rather than this chunk alone for final completeness.

Several fields represent status, pending, ack, or interrupt-enable semantics. Treating a status bit like a writable config bit, writing ack bits without preserving enables, or enabling interrupts before clearing old occurrence bits can cause lost events or interrupt storms. Similarly, double-buffer and vblank-timed fields must be updated in the correct display timing window; the masks do not enforce ordering.

Power and pad controls are especially sensitive. Incorrect LVTMA power sequencing can blank or flicker panels. Incorrect GPIO/AUX/DDC pad tuning can break EDID reads, HPD detection, or AUX link training. Incorrect UNIPHY reset/crossbar/channel inversion fields can prevent link bring-up or produce lane mapping issues that appear as link-training failures rather than obvious register programming bugs.

DSC PPS fields must match the negotiated DSC stream parameters. Incorrect bit packing for picture size, slice size, bits per pixel/component, rate-control model, or range parameters can produce sink decode failures, visual corruption, underflow/overflow status, or fallback to uncompressed modes. The error counters and buffer fullness fields in this chunk are useful for diagnosing those failures, but only if their masks remain correct.

## Test Signals

There are no direct unit tests for this generated header in the chunk. Useful validation signals come from build coverage, hardware bring-up, display conformance behavior, and register readback:

- Compile tests should catch missing or renamed macros when DCN302 resources, DSC, DIO, GPIO, panel, or perfmon code expands register field lists.
- Display smoke tests should verify monitor detection, EDID reads, HPD interrupts, DP link training, MST/MSO topologies, secondary packet delivery, audio/metadata delivery, panel power-up/down, and backlight control on DCN 3.0.2 hardware.
- DSC-specific tests should exercise DSC enable/disable, compressed stream negotiation, multiple slice sizes, 8/10/12 bpc formats where supported, MST with DSC, and readback of underflow/overflow/error counters.
- GPIO/AUX/DDC tests should check all connector instances, including DDC1-DDC5, AUX1-AUX6, HPD1-HPD6, DDCVGA, and boards that use LVTMA/panel power sequencing.
- Perfmon/debug tests should configure `DC_PERFMON19` counters, start/stop them through hardware selectors, read low/high values, trigger count-off interrupts, and verify status/ack behavior.
- Register readback tracing is a strong regression signal: programmed field values should round-trip through the same shift/mask definitions, and unrelated bits in the same register should remain unchanged after `REG_UPDATE` operations.

For generated register headers, a high-value maintenance check is comparing this file against the vendor register database or adjacent ASIC versions. Repeated field families should be mechanically diffed for expected instance-number substitutions and deliberate generation differences, especially around DP4, DSC0/DSC1, GPIO instance groups, and perfmon field widths.

### subset-b-001769: lines 44292-46764

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 44292-46764

## Scope And Purpose

This chunk is part of the generated AMD DCN 3.0.2 register shift/mask header. It contains preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for memory-mapped display hardware registers. The companion `dcn_3_0_2_offset.h` header supplies register addresses; this file supplies the field layout used by the AMD display register helper macros.

The requested range begins inside the DSC encoder 1 DSCC interrupt-control/status register, then completes DSC encoder 1's PPS, memory-power, error, and buffer-fullness fields. It then covers complete generated field layouts for DSC encoder instances 2, 3, and 4, including their DSC top, DSCCIF, DSCC, and associated DSC perfmon blocks. The range also covers the WB0 DWB top block, WB0 perfmon block, and the beginning of the WB0 DWB color-processing block through the start of `DWB_OGAM_RAMA_REGION_6_7`.

There are no functions, structs, branches, loops, or direct runtime side effects in this chunk. The exported surface is macro metadata for generated register tables. Runtime behavior occurs when DCN 3.0.2 resource construction binds these masks and shifts into hardware block objects and later display code uses `REG_SET`, `REG_UPDATE`, `REG_GET`, and related helpers to program registers.

The chunk has partial-block boundaries. It starts after the first half of `DSCC1_DSCC_INTERRUPT_CONTROL_STATUS`; the instance 1 top, DSCCIF, config, status, and early interrupt definitions live in the previous chunk. It ends in the middle of the DWB output-gamma RAM A region table; `DWB_OGAM_RAMA_REGION_6_7` is completed and the remaining RAM A regions plus RAM B fields continue in the next chunk.

## Register Blocks Covered

The DSC encoder 1 tail covers `DSCC1_DSCC_INTERRUPT_CONTROL_STATUS` masks for rate-buffer underflow, rate-control model overflow, and interrupt-enable bits, followed by `DSCC1_DSCC_PPS_CONFIG0` through `DSCC1_DSCC_PPS_CONFIG22`. These PPS fields encode Display Stream Compression parameters such as DSC version, bits per component, bits per pixel, picture and slice dimensions, chunk size, initial transmit/decode delays, scale increments/decrements, BPG offsets, initial/final offsets, flatness QP bounds, RC model size, RC quantization limits, RC buffer thresholds, and range QP/BPG offsets 0 through 14. The instance 1 tail also includes DSCC memory-power controls, squared-error and maximum-absolute-error counters, and rate-buffer/rate-control-buffer maximum-fullness readback fields.

DSC encoder instances 2, 3, and 4 are covered as repeated full blocks. Each instance has:

- `DSC_TOPx_DSC_TOP_CONTROL` and `DSC_TOPx_DSC_DEBUG_CONTROL` fields for DSC clock enable/gating and debug clock selection.
- `DSCCIFx_DSCCIF_CONFIG0` and `DSCCIFx_DSCCIF_CONFIG1` fields for input-interface underflow recovery/status/interrupt, input pixel format, bits per component, slice width, and picture dimensions.
- `DSCCx_DSCC_CONFIG0`, `DSCCx_DSCC_CONFIG1`, `DSCCx_DSCC_STATUS`, and `DSCCx_DSCC_INTERRUPT_CONTROL_STATUS` fields for slice topology, ICH behavior, rate-control buffer model sizing, double-buffer update pending, rate-buffer overflow/underflow events, rate-control model overflow events, and interrupt enables.
- `DSCCx_DSCC_PPS_CONFIG0` through `DSCCx_DSCC_PPS_CONFIG22` fields for the packed DSC PPS programming described above.
- `DSCCx_DSCC_MEM_POWER_CONTROL`, channel squared-error counters, maximum absolute-error counters, and rate-buffer/rate-control-buffer maximum-fullness counters.

The DSC performance monitor blocks `DC_PERFMON20` through `DC_PERFMON23` follow DSC instances 1 through 4. Each perfmon block includes `PERFCOUNTER_CNTL`, `PERFCOUNTER_CNTL2`, `PERFCOUNTER_STATE`, `PERFMON_CNTL`, `PERFMON_CNTL2`, `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW`. These fields cover performance counter enable/clear/mode, counter event selection, counter status readback, perfmon enable/clear modes, threshold and interrupt controls, trigger/window selection, and high/low counter-value readback.

The WB0 top block begins at `dce_dc_wb0_dispdec_dwb_top_dispdec`. It includes `DWB_ENABLE_CLK_CTRL`, `DWB_MEM_PWR_CTRL`, frame-capture controls (`FC_MODE_CTRL`, `FC_FLOW_CTRL`, `FC_WINDOW_START`, `FC_WINDOW_SIZE`, `FC_SOURCE_SIZE`), update locking/pending (`DWB_UPDATE_CTRL`), DWB CRC controls/masks/results, output format/range controls (`DWB_OUT_CTRL`), MMHUBBUB backpressure counters, host-read rate control, overflow status/counter, and soft reset.

`DC_PERFMON24` is the WB0 performance monitor with the same perfmon shape as the DSC perfmon instances. It is associated with the writeback path rather than a DSC encoder.

The WB0 DWB color-processing block begins at `dce_dc_wb0_dispdec_dwbcp_dispdec`. This chunk covers `DWB_HDR_MULT_COEF`, gamut-remap mode and coefficient format, both A and B gamut-remap coefficient matrices, output gamma (`DWB_OGAM`) mode/index/data/control registers, RAM A start/base/slope/end/offset fields for B/G/R channels, and RAM A region descriptors through regions 6 and 7.

## Important APIs, Types, And Macros

The important interface is the generated macro naming contract:

- `<register>__<field>__SHIFT` gives the bit offset for a field inside a 32-bit register.
- `<register>__<field>_MASK` gives the mask for that field.
- Comments such as `//DSCC2_DSCC_PPS_CONFIG0` and `// addressBlock: ...` delimit generated register groups but are not compiled APIs.
- Instance prefixes in this chunk include `DSC_TOP2` through `DSC_TOP4`, `DSCCIF2` through `DSCCIF4`, `DSCC1` through `DSCC4`, `DC_PERFMON20` through `DC_PERFMON24`, and unindexed WB0 names such as `DWB_ENABLE_CLK_CTRL`, `FC_MODE_CTRL`, `DWB_GAMUT_REMAP_MODE`, and `DWB_OGAM_CONTROL`.

The macros are consumed indirectly through AMD display register-list helpers. `display/dc/resource/dcn302/dcn302_resource.c` includes `dcn/dcn_3_0_2_offset.h` and this `dcn/dcn_3_0_2_sh_mask.h` header, builds DSC register arrays with `DSC_REG_LIST_DCN20(id)`, and initializes `dsc_shift`/`dsc_mask` with `DSC_REG_LIST_SH_MASK_DCN20(__SHIFT/_MASK)`. It creates DSC objects with `dsc2_construct(dsc, ctx, inst, &dsc_regs[inst], &dsc_shift, &dsc_mask)`.

The DSC field list is defined in `display/dc/dsc/dcn20/dcn20_dsc.h`. That header maps canonical field names such as `DSCC_PPS_CONFIG1.BITS_PER_PIXEL`, `DSCC_PPS_CONFIG3.SLICE_WIDTH`, `DSCC_CONFIG0.NUMBER_OF_SLICES_PER_LINE`, and `DSCC_MEM_POWER_CONTROL.DSCC_MEM_PWR_STATE` to the instance-0 generated macro names. The DCN register helper layer then pairs those generic shifts/masks with per-instance register addresses, allowing a single DSC implementation to program instances 0 through 4.

The DWB writeback macros are consumed through `display/dc/dwb/dcn30/dcn30_dwb.h`, where `DWBC_COMMON_REG_LIST_DCN30` names the top and color-processing registers and `DWBC_COMMON_MASK_SH_LIST_DCN30(__SHIFT/_MASK)` maps fields such as `FC_FRAME_CAPTURE_EN`, `DWB_CRC_EN`, `DWB_GAMUT_REMAPA_C11`, `DWB_OGAM_MODE`, and `DWB_OGAM_RAMA_EXP_REGION0_LUT_OFFSET`. In `dcn302_resource.c`, `dcn302_dwbc_create()` constructs one DCN30 DWBC instance from these register, shift, and mask tables.

The DWB color-management fields are used by `display/dc/dwb/dcn30/dcn30_dwb_cm.c`. That code programs `DWB_HDR_MULT_COEF`, alternates between gamut-remap A/B coefficient banks, reads `DWB_GAMUT_REMAP_MODE_CURRENT`, configures output-gamma RAM A/B selection through `DWB_OGAM_CONTROL`, writes `DWB_OGAM_LUT_INDEX` and `DWB_OGAM_LUT_DATA`, and programs PWL region descriptors with the `DWB_OGAM_RAMA_*` and `DWB_OGAM_RAMB_*` masks.

## Functional Field Groups

The DSCC PPS fields encode the Display Stream Compression picture parameter set into hardware registers. The chunk covers the dense packing of DSC wire-format parameters into 32-bit registers: version and component precision, bits per pixel, VBR, RGB conversion, native 4:2:0/4:2:2 flags, picture and slice geometry, chunk size, delay values, BPG offsets, RC model sizing, flatness and quantization constraints, RC target offsets, fourteen RC buffer thresholds, and fifteen range parameter triples. This is the core hardware programming surface for compressed display streams.

DSCC configuration and status fields describe how each encoder instance consumes slices and handles initial-code-history behavior. `NUMBER_OF_SLICES_PER_LINE`, `NUMBER_OF_SLICES_IN_VERTICAL_DIRECTION`, `ICH_RESET_AT_END_OF_LINE`, `ALTERNATE_ICH_ENCODING_EN`, and `DSCC_DISABLE_ICH` must match the DSC mode selected by link and timing code. `DSCC_DOUBLE_BUFFER_REG_UPDATE_PENDING` is the status bit that tells callers whether deferred updates are still waiting to take effect.

DSCC interrupt and telemetry fields expose underflow, overflow, and rate-control error conditions. The rate-buffer overflow/underflow bits and rate-control-buffer-model overflow bits are paired with interrupt-enable fields. Squared-error and max-absolute-error fields give diagnostic quality/error measurements for R/Y, G/Cb, and B/Cr channels. Maximum-fullness registers expose peak fullness for rate buffers and rate-control buffer models 0 through 3.

DSCC memory-power fields expose low-power controls and status for DSC memories, including default low-power state, force mode, disable bits, current memory state, and native 4:2:2 memory power controls. These fields tie DSC functionality to DCN power-management sequencing.

The `DC_PERFMON20` through `DC_PERFMON24` fields describe hardware performance counter configuration and readback. Counter-control fields select enable, clear, counter mode, clock enable, event selection, and threshold behavior. State fields expose status, error, current selected counters, and latched values. Perfmon control fields select trace/window behavior and trigger source, while low/high readback registers expose counter values.

The DWB top fields describe the writeback capture pipeline. Clock and memory-power fields control DWBC enable/gating and OGAM LUT memory power. Frame-capture fields select enable, capture rate, crop enable, stereo eye, stereo polarity, new-content flag, current capture state, window start/size, source size, and first-pixel delay. Update-control fields provide lock and pending status for double-buffered programming.

DWB CRC, overflow, backpressure, host-read, and output fields are validation and flow-control surfaces. CRC fields select one-shot/continuous mode and CRC source, then pack masks and signatures for red/green/blue/alpha. Output fields select output format, denormalization, and min/max clamp/range behavior. Overflow status fields report and acknowledge data overflow conditions, and the overflow counter/backpressure counter fields expose pressure in the writeback path.

DWB color-processing fields provide writeback-specific color correction. `DWB_HDR_MULT_COEF` applies HDR multiplier state. `DWB_GAMUT_REMAP_MODE`, `DWB_GAMUT_REMAP_COEF_FORMAT`, and A/B coefficient matrices provide banked color-space conversion. `DWB_OGAM_CONTROL`, LUT index/data/control, and RAM A region descriptors expose an output-gamma PWL LUT. The RAM A region table is only partially present in this chunk; it continues after `DWB_OGAM_RAMA_REGION_6_7`.

## Control Flow And State Behavior

This header has no direct control flow. Runtime behavior is created by macro expansion in resource initialization and register helper calls. DCN 3.0.2 resource setup binds addresses from `dcn_3_0_2_offset.h` and masks/shifts from this header into `dcn20_dsc` and `dcn30_dwbc` objects. Later DSC and DWB code uses those structures to read, write, or update memory-mapped hardware registers.

The hardware state described here persists in display-controller registers until changed by driver programming, firmware, reset logic, power-management transitions, or hardware status events. PPS registers, slice topology, memory-power control, frame-capture parameters, DWB output format, gamut coefficients, HDR multiplier, and OGAM LUT descriptors are configuration state. Overflow/underflow flags, max-fullness counters, perfmon counters, CRC result registers, current-mode bits, update-pending bits, and current memory-power state are live status or telemetry.

Several groups are timing-sensitive. DSCC and DWB update-pending fields indicate double-buffered updates that may not be active immediately after a register write. DSC PPS and slice fields must be programmed coherently before enabling compressed output. DWB frame capture and output-gamma programming similarly use stateful index/data windows and bank selection, so write ordering matters.

The DWB color path uses banked state. `dcn30_dwb_cm.c` reads current gamut-remap and OGAM mode state, programs the inactive A/B bank, then switches selection. For OGAM, LUT programming depends on `DWB_OGAM_LUT_HOST_SEL`, `DWB_OGAM_LUT_WRITE_COLOR_MASK`, `DWB_OGAM_LUT_INDEX`, and sequential writes to `DWB_OGAM_LUT_DATA`. A valid mask with the wrong bank or stale index still writes hardware, but to the wrong state.

Perfmon and CRC fields are stateful diagnostic windows. Clear/enable ordering, threshold/trigger selection, continuous versus one-shot mode, and read selection determine whether values represent the intended interval. Stale counters or pending one-shot state can make diagnostics misleading even when the field masks are correct.

## Dependencies And Integration Points

This file must stay synchronized with `dcn_3_0_2_offset.h`. The offset header provides `reg...` symbols for the same register names, while this header provides the field layout. A renamed or mismatched macro on either side can break compilation in generated register-list initializers or, worse, compile while programming the wrong hardware bits if the generated specification is inconsistent.

The main DCN 3.0.2 include site is `display/dc/resource/dcn302/dcn302_resource.c`. That file includes this header, creates five DSC objects, creates one DWBC object, and initializes their shared mask/shift tables with `DSC_REG_LIST_SH_MASK_DCN20` and `DWBC_COMMON_MASK_SH_LIST_DCN30`.

The DSC fields integrate with the DCN20 DSC implementation through `display/dc/dsc/dcn20/dcn20_dsc.h` and the `dsc2_construct()` path. Higher-level display code computes DSC mode feasibility and required DSCCLK in DML/resource code, then hardware sequencing programs DSC instances through these generated register fields. The chunk's PPS, slice, interrupt, memory-power, and telemetry fields are the low-level endpoint for that programming.

The DWB top and color-processing fields integrate with `display/dc/dwb/dcn30/dcn30_dwb.c`, `display/dc/dwb/dcn30/dcn30_dwb_cm.c`, and `display/dc/inc/hw/dwb.h`. Runtime paths update capture windows, enable/disable frame capture, set stereo parameters, program output format, enable DWB CRC, configure gamut remap, program output gamma, and apply HDR multiplier through these masks.

The writeback instance is also integrated through hardware sequencing in DCN30-family code. `dcn30_hwseq.c` connects writeback to the MPC DWB mux, updates DWBC parameters, enables DWBC, warms up MMHUBBUB/MCIF writeback state, and disables the DWB path when capture stops. The register fields in this chunk are the DWBC-side control/status surface for those operations.

The perfmon fields are generated metadata for diagnostic or profiling access. The visible resource constructors bind the masks, but this tree has fewer high-level named consumers for `DC_PERFMON20` through `DC_PERFMON24` than for the DSC and DWBC functional blocks. Likely users include register dumps, debug tooling, firmware-assisted diagnostics, or future instrumentation using the standard register helper layer.

## Risks And Edge Cases

The primary risk is generated-header drift from the hardware register specification or from the matching offset header. An incorrect shift or mask can corrupt DSC PPS programming, slice layout, memory power state, writeback capture parameters, CRC masks/results, gamut-remap coefficients, or output-gamma LUT region descriptors. These failures often appear as display corruption, failed compressed link training, bad writeback output, unreliable CRCs, or silent diagnostic errors rather than simple crashes.

The chunk starts and ends in partial logical regions. Instance 1 DSCC interrupt definitions are split with the previous chunk, and DWB OGAM RAM A definitions are split with the next chunk. Per-file reconciliation must merge adjacent chunk reports before claiming complete coverage of DSCC1 or DWB OGAM.

DSC PPS programming is packed and truncation-sensitive. Many fields are narrow bit ranges in shared 32-bit registers, and range parameters pack QP and BPG offsets tightly. Callers must clamp values to the protocol/hardware limits and use mask/shift helpers, especially for bits-per-pixel fixed-point values, picture/slice dimensions, delay intervals, BPG offsets, RC buffer thresholds, and range offsets.

DSC topology fields must match the stream, link, and clock plan. Wrong slice counts, picture dimensions, chunk size, or DSCCLK assumptions can create underflow/overflow events, stuck update-pending state, or an apparently valid mode that fails only under bandwidth pressure.

Interrupt/status fields combine event bits and enable bits in a single register for the older DSCC layout. Code that treats status bits as pure configuration, or that writes a full register value without preserving unrelated fields, can lose latched errors or accidentally enable/disable interrupt sources.

DWB color programming is banked and ordered. Gamut remap alternates A/B coefficient banks based on current mode, and OGAM alternates RAM A/B LUTs. Selecting a bank before all coefficient or LUT data is programmed can produce transient color errors in writeback. Programming the LUT data window with a stale index or wrong color mask writes valid values to the wrong component or entry.

DWB frame capture and CRC diagnostics are stateful. `FC_FRAME_CAPTURE_EN_CURRENT`, `DWB_UPDATE_PENDING`, overflow flags, CRC continuous/one-shot mode, CRC source selection, and CRC masks all affect how tests should interpret readback. Missing reset/clear sequencing can make captures or CRC comparisons look wrong even with correct register definitions.

Memory-power controls for DSCC and DWB OGAM LUT memory are sensitive to mode changes and suspend/resume. Forcing low-power or disabling memory while DSC or writeback color processing is active can cause failures that only reproduce around blanking, stream reconfiguration, hotplug, or power-management transitions.

## Test Signals

Build-time coverage should catch missing or renamed generated macros in `dcn302_resource.c`, `dcn20_dsc.h`, and `dcn30_dwb.h`. High-signal compile failures include missing `DSCC0_*`, `DSCCIF0_*`, `DWB_*`, `FC_*`, or `DWB_OGAM_*` field names referenced through `DSC_REG_LIST_SH_MASK_DCN20` or `DWBC_COMMON_MASK_SH_LIST_DCN30`.

DSC runtime validation should exercise compressed display modes on DCN 3.0.2 across DSC instances 1 through 4 where hardware routing permits. Useful signals include successful modesets with DSC enabled, correct PPS values in register dumps, no stuck `DSCC_DOUBLE_BUFFER_REG_UPDATE_PENDING`, no unexpected rate-buffer overflow/underflow interrupts, stable DSCCLK programming, and sane max-fullness/error counters under bandwidth-heavy modes.

Writeback validation should exercise frame-capture enable/disable, crop windows, source/window size programming, stereo fields where supported, output format/range controls, update locking, overflow status handling, and MMHUBBUB backpressure counters. Expected signals are correct captured dimensions and format, no unexpected overflow, and update-pending bits clearing after the intended update point.

Color/writeback validation should cover HDR multiplier programming, gamut-remap bypass and A/B bank switching, coefficient-format selection, output-gamma bypass and RAM LUT modes, LUT index/data writes, and current-mode readback. CRC-based comparisons of writeback output are useful because many color-path errors do not crash the driver.

Perfmon and CRC diagnostic tests should validate clear/enable/readback sequencing for `DC_PERFMON20` through `DC_PERFMON24`, low/high counter reads, trigger/window selection, DWB CRC masks, one-shot versus continuous CRC mode, and CRC source selection. Hardware register-spec cross-checks remain the strongest regression signal because this file is generated metadata.

### subset-b-001770: lines 46765-49290

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 46765-49290

## Scope

This chunk covers a generated AMD DCN 3.0.2 register shift/mask header region. It contains C preprocessor constants only: register grouping comments plus `__SHIFT` and `_MASK` `#define` entries. There are no C functions, structs, enums, storage objects, or direct MMIO operations in this slice.

The range starts in the middle of the display writeback output-gamma RAM A region table, continues through display writeback output-gamma RAM B fields, covers MPCC0 through MPCC4 compositor/blender field definitions, then covers MPCC output-gamma and gamut-remap blocks for MPCC OGAM0, OGAM1, OGAM2, and the beginning of OGAM3. It ends inside `MPCC_OGAM3_MPCC_OGAM_RAMA_REGION_12_13`, so the later merge lane must combine adjacent chunks before making whole-file completeness claims.

## Purpose

The purpose of this header region is to define bit positions and masks for DCN 3.0.2 display writeback, multi-plane composition, output-gamma, and gamut-remap registers. AMD display code uses these generated constants through register-helper macros so implementation files can update fields symbolically instead of hard-coding bit shifts and masks.

The covered hardware areas are:

- DWB OGAM RAMA/RAMB region descriptors and start/end/offset controls, used by the display writeback path's output transfer function programming.
- MPCC0-4 compositor controls, including top/bottom source selection, OPP assignment, alpha/blending controls, overlap behavior, global alpha/gain, per-layer gain, background color, memory power state, and disabled status.
- MPCC OGAM0-3 output-gamma LUT controls, including RAM A/B selection, mode/current-mode fields, LUT index/data access, per-color write masks, read selection, host RAM selection, and configuration mode.
- MPCC OGAM0-3 piecewise-linear region controls for RAM A and RAM B, including per-channel start/end/base/slope/offset fields and 34 region descriptors packed two regions per register.
- MPCC OGAM0-2 gamut-remap controls and matrix coefficient registers, with the beginning of MPCC OGAM3 following in the next chunk.

This is a hardware contract file. Its behavioral importance is that the numeric mask/shift values must match the DCN 3.0.2 register database and the matching offset header.

## Important APIs, Types, And Constants

There are no callable APIs or concrete types in this chunk. The exported interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field mask.
- Address-block comments such as `// addressBlock: dce_dc_mpc_mpcc0_dispdec` and register comments such as `//MPCC0_MPCC_CONTROL` preserve the hardware grouping used by register-table macros.

Important register families in this chunk include:

- `DWB_OGAM_RAMA_REGION_6_7` through `DWB_OGAM_RAMA_REGION_32_33`, plus `DWB_OGAM_RAMB_*`, define DWB output gamma PWL RAM region layout. Region-pair registers pack one region's LUT offset at bits 0-8, segment count at bits 12-14, the next region's LUT offset at bits 16-24, and segment count at bits 28-30. Start controls carry an 18-bit start value and a start segment field; start/end base and slope fields are 18-bit or 16-bit depending on register; offsets are 19-bit.
- `MPCC<n>_MPCC_TOP_SEL`, `MPCC_BOT_SEL`, and `MPCC_OPP_ID` map compositor input and output routing fields for MPCC instances 0-4.
- `MPCC<n>_MPCC_CONTROL` maps composition mode and alpha/blend state: `MPCC_MODE`, `MPCC_ALPHA_BLND_MODE`, `MPCC_ALPHA_MULTIPLIED_MODE`, `MPCC_BLND_ACTIVE_OVERLAP_ONLY`, `MPCC_GLOBAL_ALPHA`, `MPCC_GLOBAL_GAIN`, `MPCC_BG_BPC`, and `MPCC_BOT_GAIN_MODE`.
- `MPCC<n>_MPCC_SM_CONTROL` maps state-machine controls and status such as `MPCC_SM_FORCE_NEXT_FRAME_POL`, `MPCC_SM_FIELD_ALT`, `MPCC_SM_FRAME_ALT`, `MPCC_SM_FORCE_NEXT_TOP_POL`, and current polarity fields.
- `MPCC<n>_MPCC_UPDATE_LOCK_SEL` maps the update lock source for each MPCC.
- `MPCC<n>_MPCC_TOP_GAIN`, `BOT_GAIN_INSIDE`, `BOT_GAIN_OUTSIDE`, and `BG_R_CR/G_Y/B_CB` map gain and background color data.
- `MPCC<n>_MPCC_MEM_PWR_CTRL` maps OGAM memory power controls and status: force, disable, and power-state fields.
- `MPCC<n>_MPCC_STATUS` maps the `MPCC_DISABLED` status bit.
- `MPCC_OGAM<n>_MPCC_OGAM_CONTROL`, `LUT_INDEX`, `LUT_DATA`, and `LUT_CONTROL` define output-gamma mode selection, active/current RAM selection, 9-bit LUT index, 18-bit LUT data, color write mask, read color selection, debug read, host RAM selection, and config mode.
- `MPCC_OGAM<n>_MPCC_OGAM_RAMA_*` and `RAMB_*` define the double-buffered output-gamma PWL RAM control surface for each MPCC OGAM block.
- `MPCC_OGAM<n>_MPCC_GAMUT_REMAP_COEF_FORMAT` and `MPCC_GAMUT_REMAP_MODE` define coefficient format and active/current gamut-remap mode fields.
- `MPCC_OGAM<n>_MPC_GAMUT_REMAP_C11_C12_A` through `C33_C34_B` pack signed matrix coefficients two 16-bit fields per register for two coefficient banks, A and B.

Related semantic values live outside this chunk. For example, generated enum headers define values such as `MPCC_GAMUT_REMAP_COEF_FORMAT_S2_13`, `MPCC_GAMUT_REMAP_COEF_FORMAT_S3_12`, gamut-remap mode selectors, DWB OGAM mode/select values, LUT host selection, and LUT read color selection.

## Control Flow

This chunk has no runtime control flow. Its effective control flow is compile-time macro expansion into register-helper operations:

1. DCN 3.0.2 display code includes this shift/mask header with the matching DCN 3.0.2 offset header.
2. Register table macros such as `SR`, `SRII`, `SF`, and DWB-specific `SF_DWB2` bind generated register names and field names into per-block register, shift, and mask structures.
3. Runtime code calls helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, and multi-field variants.
4. The helper layer uses the generated shift and mask values from this header to produce the MMIO read/modify/write value for the selected register field.

The runtime consumers provide the actual flow. DWB code configures frame capture, programs gamut remap and output gamma, then enables or updates capture under DWB update-lock handling. MPC code configures composition trees by programming MPCC source routing, blend mode, OPP ID, gains, status, memory power controls, MPCC OGAM LUTs, and gamut-remap matrices. The header only supplies the field layout needed for those sequences.

## State And Persistence Behavior

The header itself stores no state and persists no data. It describes stateful hardware registers:

- DWB OGAM RAMA/RAMB fields persist the display writeback output transfer function's PWL segmentation, start/end values, slopes, base values, offsets, and selected LUT RAM until reprogrammed or reset.
- MPCC routing state persists which DPP/top source and bottom MPCC feed each compositor, and which OPP receives the composed output.
- MPCC control state persists blend mode, alpha semantics, global alpha/gain, background bit depth, and bottom gain handling.
- MPCC update-lock selection and state-machine fields coordinate when compositor changes take effect relative to display timing.
- MPCC OGAM mode/select/current fields expose double-buffered output-gamma state. Software programs one RAM bank while hardware can continue using another, then switches selected/current RAM under the block's update semantics.
- MPCC OGAM LUT index/data/control fields represent host access to LUT RAM; the index and host selection determine which RAM entry and color component subsequent data writes or reads touch.
- Gamut-remap mode/current-mode and coefficient bank fields persist matrix color conversion state in the MPC/MPCC OGAM path.
- Memory power control bits can force, disable, or report OGAM memory power state. Incorrect values can make later LUT or gamma programming ineffective even if the register writes appear to complete.

Persistence is hardware-defined. Writable control fields remain until a later driver update, block reset, display power-state transition, or full ASIC reset. Status/current fields are read by software but are represented with the same mask/shift style as writable fields, so legal read/write direction is not encoded in this header.

## Dependencies And Integration Points

This chunk depends on several generated and handwritten AMD display components staying synchronized:

- The matching `dcn_3_0_2_offset.h` register-offset header supplies MMIO addresses for the register names whose fields are described here.
- The register helper layer in AMD display code consumes the suffix convention through macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, and `FD_SHIFT`.
- DWB integration appears in `drivers/gpu/drm/amd/display/dc/dwb/dcn30/`, where `dcn30_dwb.h` lists the DWB OGAM registers and field masks and `dcn30_dwb.c` programs DWB enable/update, gamut remap, and output transfer function state.
- MPC integration appears in `drivers/gpu/drm/amd/display/dc/mpc/dcn10/` and `dcn30/`. `dcn10_mpc.c` uses MPCC top/bottom/OPP/control fields to build and tear down composition trees. `dcn30_mpc.h` adds the DCN 3.x MPCC OGAM and gamut-remap register/field table entries.
- Higher-level display color management and plane composition code supplies transfer functions, blend parameters, gamut-remap matrices, and stream/plane topology that eventually become writes through these fields.
- Generated enum headers such as `soc21_enum.h` and `soc24_enum.h` document semantic values for DWB OGAM and MPCC gamut-remap fields, but this file only defines bit placement.

The main integration contract is preprocessor naming. If a field macro is missing or renamed, register-table construction usually fails at compile time. If a mask or shift is numerically wrong, the code can compile and then program the wrong hardware bits.

## Risks And Edge Cases

- The line range starts mid-DWB `RAMA` region table and ends mid-MPCC OGAM3 `RAMA` region table. Adjacent chunk reconciliation is required for complete DWB/OGAM3 coverage.
- The repeated region-pair pattern is easy to generate incorrectly. A wrong offset or segment-count mask in one pair can corrupt only one part of the gamma curve while most neighboring registers continue to look correct.
- Region descriptors have unused bit gaps between LUT offset and segment count fields. Code must rely on masks rather than assuming adjacent packed fields.
- RAM A and RAM B fields are nearly identical. Accidentally using a `RAMA` field with a `RAMB` register, or selecting the wrong host RAM, can write a valid-looking LUT into the inactive or unintended bank.
- Current-mode/current-select fields are status/readback fields adjacent to desired mode/select fields. Confusing desired and current fields can make polling or update sequencing unreliable.
- Gamut-remap matrices pack two 16-bit coefficients per 32-bit register. Bad masks can swap or overwrite adjacent coefficients and cause subtle color-space errors rather than obvious hardware faults.
- MPCC top/bottom/OPP routing fields use small instance identifiers. A bad field width or invalid sentinel value can miswire a composition tree, especially when planes are inserted or removed dynamically.
- MPCC memory power fields affect OGAM RAM availability. Power gating or forced memory state mismatches can make LUT programming fail or produce stale output after resume.
- The macros do not encode access direction. Status bits such as `MPCC_DISABLED`, `MPCC_OGAM_MODE_CURRENT`, or memory power state look like ordinary fields to the preprocessor.
- Cross-generation reuse is risky. DCN 3.0.0, 3.0.1, and 3.0.2 names are similar, but the offset and shift/mask headers must match the target ASIC.

## Test Signals

Useful validation is mostly build-time and hardware-integration oriented:

- Compile the DCN 3.0.2 AMD display driver paths that include this header to catch missing or renamed `__SHIFT`/`_MASK` macros in `SF`, `SR`, `SRII`, and DWB field-list expansion.
- Preprocess representative DWB and MPC objects to confirm that register-helper field names resolve to the expected generated constants.
- Compare this chunk against the matching DCN 3.0.2 register database and offset header to verify register/field coverage, especially the DWB OGAM RAMA/RAMB and MPCC OGAM0-3 repeated blocks.
- Exercise DWB capture with output transfer functions enabled and disabled; expected signals are correct capture color output, stable DWB update-lock behavior, and no stale LUT bank after switching RAM A/B.
- Exercise display color-management paths that program MPCC OGAM LUTs and gamut-remap matrices, then validate visible output or CRCs across identity, sRGB-like, HDR/PQ-like, and custom matrix cases.
- Exercise plane composition with multiple planes, alpha blending, global alpha/gain, background color, and plane insert/remove operations; watch for MPCC routing errors or incorrect disabled status.
- Test suspend/resume and display power transitions, because OGAM memory power control and LUT RAM persistence are common failure points for generated mask mistakes.
- Run register readback/debug traces around `MPCC_OGAM_MODE_CURRENT`, `MPCC_OGAM_SELECT_CURRENT`, gamut-remap current mode, and `MPCC_DISABLED` to ensure software observes state changes through the expected fields.

## Open Cross-Chunk Questions

- The later merge lane should combine this with the previous chunk to present the full DWB OGAM RAMA table and the start of the DWB OGAM block.
- The later merge lane should combine this with the next chunk to present complete MPCC OGAM3 RAMA/RAMB and gamut-remap coverage.
- Whole-file analysis should verify that all MPCC and MPCC OGAM instances expected for DCN 3.0.2 are represented consistently across the offset header, shift/mask header, and the DCN 3.x MPC register-list macros.

### subset-b-001771: lines 49291-51798

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 49291-51798

## Scope

This chunk is a generated register shift/mask slice for AMD DCN 3.0.2 display hardware. It covers 2,508 lines, with 2,106 `#define` constants split almost evenly between `__SHIFT` and `_MASK` definitions. The source file is included by `drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c` together with `dcn_3_0_2_offset.h`, and the field names are consumed by AMD Display Core register-table macros such as `SF(...)` in `drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.h`.

The chunk is declarative rather than executable: it exports preprocessor constants that tell the DC register helper layer how to pack, update, and read bitfields in 32-bit display engine registers.

## Purpose

The constants in this range describe several MPC and MPCC color-pipeline register blocks:

- Tail of `MPCC_OGAM3` output gamma RAM A/B region metadata, offsets, endpoints, and gamut-remap coefficient fields.
- Full `MPCC_OGAM4` output gamma block, including LUT selection/control/data fields, RAM A/B piecewise-linear region descriptors, per-channel start/end/offset values, and gamut-remap matrix fields.
- `dce_dc_mpc_mpc_cfg_dispdec` MPC configuration fields for clock gating, soft reset, CRC control/results, background bypass color, host read throttling, DPP/OPP update-pending status, vupdate lock sets, and DWB muxing.
- `dce_dc_mpc_mpc_ocsc_dispdec` output mux, denormalization, and output CSC register fields for outputs 0 through 4.
- Start of `dce_dc_mpc_mpc_rmu_dispdec`, including RMU muxing, memory power control, RMU0 shaper LUT/RAM and 3DLUT fields, and RMU1 shaper LUT/RAM fields through `MPC_RMU1_SHAPER_RAMB_REGION_26_27`.

These definitions let shared DCN30-era MPC code use symbolic field names while the ASIC-specific header supplies the actual bit positions for DCN 3.0.2.

## Important APIs, Types, and Macro Families

There are no C functions or types in this chunk. The API surface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the raw register value.
- Register comments such as `//MPC_CRC_CTRL` and address block comments group constants by hardware block.

Important families visible in this slice:

- `MPCC_OGAM3_*` and `MPCC_OGAM4_*`: per-MPCC output gamma and gamut remap. The RAM region pairs define `EXP_REGIONn_LUT_OFFSET` and `EXP_REGIONn_NUM_SEGMENTS` fields using the common pattern offsets at bits 0/12/16/28 and masks `0x000001FF`, `0x00007000`, `0x01FF0000`, and `0x70000000`.
- `MPCC_OGAM4_MPCC_OGAM_CONTROL`, `LUT_INDEX`, `LUT_DATA`, and `LUT_CONTROL`: mode/select/current/status fields for OGAM LUT programming.
- `MPCC_OGAM*_MPC_GAMUT_REMAP_Cxx_Cyy_[AB]`: 16-bit coefficient pairs for gamut-remap matrices, with one coefficient in bits 0-15 and another in bits 16-31.
- `MPC_CLOCK_CONTROL`, `MPC_SOFT_RESET`, `MPC_CRC_*`, `MPC_DPP_PENDING_STATUS`, and `MPC_PENDING_STATUS_MISC`: global MPC control, diagnostics, and update-state observation fields.
- `ADR_CFG_CUR_VUPDATE_LOCK_SETn`, `ADR_CFG_VUPDATE_LOCK_SETn`, `ADR_VUPDATE_LOCK_SETn`, `CFG_VUPDATE_LOCK_SETn`, and `CUR_VUPDATE_LOCK_SETn`: five sets of vupdate lock flags.
- `MPC_OUT[0-4]_MUX`, `MPC_OUT[0-4]_DENORM_*`, `MPC_OUT[0-4]_CSC_*`, and `MPC_OUT_CSC_COEF_FORMAT`: output path routing, clamping/denormalization, and color-space conversion.
- `MPC_RMU_CONTROL` and `MPC_RMU_MEM_PWR_CTRL`: RMU mux select/status and memory power/low-power state fields for RMU0-RMU2.
- `MPC_RMU0_*` and `MPC_RMU1_*`: shaper LUT offsets/scales, LUT index/data/write enables, RAM A/B region descriptors, and RMU0 3DLUT mode/data/read-write controls.

The companion consumer macros in `dcn30_mpc.h` declare register field lists and `MASK_SH` mappings, for example mapping `MPC_RMU0_SHAPER_RAMA_REGION_0_1` plus `MPC_RMU_SHAPER_RAMA_EXP_REGION0_LUT_OFFSET` through `SF(...)` into the runtime `mpc_shift` and `mpc_mask` tables. Runtime code then uses helpers such as `REG_UPDATE`, `REG_UPDATE_2`, `REG_SET`, `REG_GET`, and `REG_WAIT` against those tables.

## Control Flow and State Behavior

This header chunk has no direct control flow. Its behavior is compile-time substitution into the AMD display register access layer:

1. DCN302 resource setup includes the DCN 3.0.2 offset and shift/mask headers.
2. MPC/MPCC register structs are initialized with ASIC-specific register addresses, masks, and shifts.
3. Higher-level display code calls generic MPC operations, such as output mux setup, OGAM programming, CSC programming, CRC control, RMU shaper/3DLUT programming, or pending-status reads.
4. Register helper macros combine the runtime value with the field shift and mask from this header, preserving unrelated bits in the same register where appropriate.

Hardware state persists in MMIO registers, not in this file. Several fields expose latched or current hardware state:

- `*_CURRENT` fields report active OGAM/gamut/CSC/shaper modes after double-buffered programming takes effect.
- `*_STATUS` fields report mux or configuration status, including DWB mux, RMU mux, OGAM LUT status, shaper config status, and 3DLUT config status.
- `MPC_DPP_PENDING_STATUS` and `MPC_PENDING_STATUS_MISC` expose pending DPP, cursor, OPP, and DWB update bits.
- `MPC_CRC_RESULT_*` holds CRC output values when CRC capture is enabled.
- Memory power state fields in `MPC_RMU_MEM_PWR_CTRL` represent RMU shaper and 3DLUT memory state for RMU instances.

The many LUT and RAM fields are used by software sequencing that writes indices, data, region starts, region ends, offsets, and mode fields in a hardware-required order. The constants themselves do not enforce that order.

## Dependencies and Integration Points

Primary dependencies:

- `dcn_3_0_2_offset.h` supplies the matching register addresses. This file supplies only bit shifts and masks.
- `drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c` includes this header for DCN302 hardware resource construction.
- `drivers/gpu/drm/amd/display/dc/mpc/dcn30/dcn30_mpc.h` and `dcn30_mpc.c` provide the shared MPC implementation that consumes these field names through generated register tables.
- The `reg_helper.h` macros consume field metadata to perform read-modify-write, field extraction, and wait loops.

Notable integration with display features:

- MPCC OGAM fields integrate with per-plane/per-MPCC output gamma LUT programming and gamut remap.
- MPC output CSC and denorm fields integrate with OPP/output color conversion and clamp control for each of five outputs.
- MPC CRC fields integrate with display CRC validation paths used for diagnostics and automated display tests.
- DPP/OPP/DWB pending-status fields integrate with update synchronization and flip/update sequencing.
- RMU shaper and 3DLUT fields integrate with advanced color management and RAM-backed LUT programming.
- RMU and OGAM memory-power fields integrate with display power-management sequencing; callers must usually power memories before LUT programming and wait for state changes.

## Risks and Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask silently writes the wrong hardware bits, which can break color output, mux routing, CRC reads, power sequencing, or update synchronization.
- Register field names must stay aligned with the field-list macros in `dcn30_mpc.h`. If a consumer references a field not present in this ASIC header, compilation fails; if the name exists but the value is wrong, failure is runtime-only.
- Many registers pack two 16-bit values or two region descriptors into one register. Incorrect masks can corrupt the paired field during read-modify-write operations.
- Region descriptors use repeated bit layouts for RAM A/B and multiple instances. Copy-generation mistakes are hard to spot manually because the macro families are highly repetitive.
- Status/current fields should generally be treated as read-only or hardware-owned. Writing them accidentally through generic helpers can cause undefined display behavior if the register map does not ignore writes.
- The chunk boundary ends after `MPC_RMU1_SHAPER_RAMB_REGION_26_27`; subsequent RMU1 RAMB regions continue outside this chunk. Whole-file research must merge adjacent chunks before drawing complete conclusions about RMU1 coverage.

## Test Signals

Useful validation signals for code using this header include:

- Compile coverage for DCN302 resource construction and MPC register tables; missing or renamed macros are caught at build time.
- Display color-management tests that program OGAM, gamut remap, output CSC, shaper LUTs, and 3DLUTs, then verify visible output or hardware CRC values.
- CRC capture tests using `MPC_CRC_CTRL`, `MPC_CRC_SEL_CONTROL`, and `MPC_CRC_RESULT_*`.
- Flip/update sequencing tests that watch `MPC_DPP_PENDING_STATUS`, `MPC_PENDING_STATUS_MISC`, and vupdate lock bits for expected transitions.
- Power-management tests that exercise RMU memory power force/disable/state fields and confirm LUT access only occurs when memory is powered.
- Register trace or MMIO readback comparison against AMD register specifications for DCN 3.0.2, especially for packed coefficient and region descriptor fields.

### subset-b-001772: lines 51799-54370

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 51799-54370

## Purpose

This chunk is part of the generated AMD DCN 3.0.2 register shift/mask header. It contains C preprocessor constants only; there are no functions, structs, storage objects, branches, or executable algorithms in this source slice. Each exported constant maps a hardware register field to either a low bit position ending in `__SHIFT` or an already-positioned bit mask ending in `_MASK`.

The covered hardware area is the tail of MPC RMU color-management metadata, display performance-monitor instances, high-performance-output clock control, ambient/backlight-management instances, HD Audio/Azalia controller metadata, and legacy VGA indexed-register metadata:

- The chunk starts in the middle of the `MPC_RMU1` shaper RAM-B region table, then completes `MPC_RMU1` 3D LUT fields.
- It defines a full `MPC_RMU2` shaper and 3D LUT macro set, including shaper LUT control, per-channel offsets/scales, RAM-A and RAM-B region descriptors, 3D LUT mode/index/data/read-write controls, and output normalization/offset/scale fields.
- It defines `DC_PERFMON25` under the MPC performance-monitor block and `DC_PERFMON26` under the HPO performance-monitor block.
- It defines `HPO_TOP_CLOCK_CONTROL` for HDMI stream-clock gate disable.
- It defines repeated `ABM0`, `ABM1`, `ABM2`, `ABM3`, and `ABM4` backlight/ABM register fields for PWM levels, automatic backlight control, adaptive contrast enhancement, histogram/luma statistics, sample rates, update locks, and readback state.
- It defines HDA/Azalia controller command/response ring and immediate-command fields, plus endpoint immediate-command data/index fields.
- It ends in legacy VGA sequencer and CRT-controller indexed registers, through `CRT07` vertical high-bit fields.

The header is hardware ABI metadata for AMDGPU Display Core. Driver code combines these field constants with register-address macros from `dcn_3_0_2_offset.h`, stores them in generated register tables, and accesses hardware through helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_READ`, and lower-level MMIO wrappers.

Although the path is under a `ceph-client` source mirror, this chunk is AMD GPU display/audio register metadata. It does not implement Ceph filesystem behavior, distributed storage logic, network protocol handling, or filesystem persistence.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The public interface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: positioned bit mask for the same field.

Important macro families are:

- `MPC_RMU1_SHAPER_RAMB_REGION_28_29` through `MPC_RMU1_SHAPER_RAMB_REGION_32_33`: tail region descriptors for the second RAM bank of RMU instance 1 shaper LUTs. Each paired region register carries per-region LUT offsets and segment counts.
- `MPC_RMU1_3DLUT_*`: 3D LUT mode/current-mode, size, index, two-16-bit data writes, 30-bit data writes, RAM-bank selection, 30-bit enable, read selection, output normalization, and per-channel output offset/scale fields.
- `MPC_RMU2_SHAPER_*`: full shaper state for RMU instance 2. This includes shaper LUT mode/current mode, RGB offsets, RGB scale, LUT index/data/write-enable, RAM-A and RAM-B start/end controls, and paired exponent-region descriptors for regions 0 through 33.
- `MPC_RMU2_3DLUT_*`: 3D LUT control/data/normalization fields for RMU instance 2, matching the instance-1 shape.
- `DC_PERFMON25_*` and `DC_PERFMON26_*`: performance-counter control, secondary control, per-counter state, monitor state/repeat count, count-off interrupt control/status/ack, counter value interrupt status/ack, high/low current values, and selected high/low readback windows.
- `HPO_TOP_CLOCK_CONTROL__HPO_HDMISTREAMCLK_GATE_DIS`: HPO HDMI stream clock gating control bit.
- `ABM[0-4]_BL1_PWM_*`: backlight/PWM-facing fields for ambient light level, user-requested level, target/current ABM level, final/minimum duty cycle, ABM enable/use-ambient/auto-update controls, sample-rate counters, and group-2 double-buffer lock/update state.
- `ABM[0-4]_DC_ABM1_*`: ABM processing fields for enable/bypass, input color-space coefficient selection, ACE offset/slope and threshold parameters, missed-frame state, HGLS read progress, histogram controls, luma-statistic readbacks, histogram and luma sample rates, histogram bin shift flags/indexes, 24 histogram result registers, and the backlight master lock.
- `CORB_*`, `RIRB_*`, `IMMEDIATE_*`, `DMA_POSITION_*`, and `WALL_CLOCK_COUNTER_ALIAS`: HDA/Azalia controller fields for command output ring buffer pointers/control/status/size, response input ring buffer base addresses/pointers/control/status/size, immediate command/response paths, DMA position buffer base/enable, and wall-clock readback.
- `AZENDPOINT_*` and `AZENDPOINT_IMMEDIATE_COMMAND_INPUT_*`: endpoint immediate command data/index fields for output and input endpoints.
- `SEQ00` through `SEQ04`: legacy VGA sequencer reset, clocking, map mask, character-map select, and memory mode fields.
- `CRT00` through `CRT07`: legacy VGA CRT controller horizontal timing fields and vertical high-bit packing fields.

Several names contain repeated terms such as `MPC_RMU_3DLUT_WRITE_EN_MASK_MASK` or `PERFCOUNTER_OFF_MASK_MASK`. That is expected in generated register headers: the first `MASK` is part of the hardware field name and the final `_MASK` suffix denotes the generated mask constant.

## Control Flow

This header chunk has no runtime control flow. Runtime behavior is created by caller code that uses these constants to encode and decode MMIO register values.

A typical path is:

1. A DCN 3.0.2-specific resource or hardware block file includes `dcn_3_0_2_offset.h` and `dcn_3_0_2_sh_mask.h`.
2. Register-list and shift/mask table macros select register addresses from the offset header and field definitions from this shift/mask header.
3. Constructors for display objects, such as MPC, ABM, HPO/hwseq, or audio-adjacent blocks, bind those tables into per-IP-block structs.
4. Higher-level Display Core code computes color-management, backlight, link/audio, timing, or diagnostics state.
5. Hardware code writes or reads fields through `REG_*` helpers, which use the stored shift and mask values generated from this file.

Concrete integration patterns in the tree include:

- MPC color-management code and resource definitions use the same shaper RAM region and 3D LUT macro shape in newer DCN generations. The `MPC_RMU` and `MPCC_MCM` register lists are used to program shaper LUT region descriptors, select LUT banks, write 3D LUT entries, choose 30-bit mode, and read current LUT mode/status.
- `amdgpu_dm_color.c`, Display Core color state, and hardware sequencer code treat 3D LUTs as part of the color pipeline. This chunk supplies the bit-level register ABI used below those policy layers for the DCN 3.0.2 RMU instances.
- `dce_abm.c`, `dmub_abm_lcd.c`, `dce_abm.h`, and DCN resource headers use ABM register families such as `BL1_PWM_CURRENT_ABM_LEVEL`, `BL1_PWM_TARGET_ABM_LEVEL`, `BL1_PWM_USER_LEVEL`, and `DC_ABM1_HGLS_REG_READ_PROGRESS` to set backlight levels and clear missed-frame/readback status.
- Hardware-sequencer definitions reference `HPO_TOP_CLOCK_CONTROL` and its HPO HDMI stream clock-gate field to configure display output clock gating.
- The HDA/Azalia fields match standard GPU audio command paths: software programs CORB/RIRB ring buffers or immediate-command registers, then polls/handles busy, result-valid, response interrupt, overrun, and memory-error state.
- VGA `SEQ*` and `CRT*` fields exist for legacy VGA-compatible modes or low-level bring-up paths that still need indexed VGA register definitions, even though normal atomic KMS display programming mostly uses DCN-native blocks.

The hardware sequencing implied by these fields is important:

- Shaper and 3D LUT programming is generally banked or indexed. Callers must select the intended bank/read-write mode, write LUT data in the expected order, and switch the active LUT mode only after contents and normalization/scale fields are ready.
- ABM fields include update locks, pending bits, frame-start update controls, readback-in-progress bits, missed-frame flags, and clear bits. Callers need frame-boundary-aware sequencing to avoid stale or partially latched brightness/statistics state.
- Performance monitors require event selection, counter state programming, run/stop control, optional interrupt enable, and ordered status/ack handling before values are meaningful.
- HDA command rings require DMA base addresses, size programming, pointer resets, DMA enable, interrupt setup, and overrun/error clearing in the correct order.
- Legacy VGA CRT timing fields pack high bits across multiple registers, so callers must update related registers coherently if they are ever used for mode programming.

## State And Persistence Behavior

The header itself stores no state and persists nothing. It defines compile-time constants.

The state represented by this chunk lives in GPU registers and in caller-maintained Display Core objects:

- RMU shaper LUT and 3D LUT RAM contents, current mode, active bank, output normalization, and output per-channel offset/scale are display hardware state. They affect color transformation until overwritten, reset, or power-gated.
- ABM/PWM registers hold current, target, user, ambient, final, and minimum backlight levels, plus automatic transition controls. Histogram, luma-statistic, ACE, and HGLS fields expose both programmed parameters and hardware-produced readbacks.
- Double-buffer lock and update-pending bits represent staged hardware state that may latch at frame start rather than immediately on CPU write.
- Performance-monitor counters and current values are volatile diagnostic state. Interrupt status and ack bits have write-sensitive side effects.
- HDA CORB/RIRB base addresses and DMA-position buffers point at system memory managed by the audio driver. Pointer reset, DMA enable, and status bits are device state, not persistent storage.
- VGA sequencer/CRT fields are legacy display register state.

None of this is filesystem-persistent. Across GPU reset, suspend/resume, display reinitialization, or power-gating transitions, caller code must reprogram the required registers from software state.

## Dependencies

This chunk depends conceptually on:

- `dcn_3_0_2_offset.h` for the matching register addresses and base-index values. The shift/mask constants are useful only when paired with the correct address definitions for the same ASIC generation.
- Display Core register-helper infrastructure that stores address, shift, and mask tables and implements field updates over MMIO.
- DCN resource definitions that know which physical instances exist and how instance-prefixed generated names map to abstract blocks such as MPC RMU, ABM, HPO, and audio controller paths.
- DRM/KMS color-management, backlight, audio, and mode-setting code that decides when these fields should be programmed.
- Hardware-generated enum headers for symbolic field values in some domains, for example 3D LUT size/depth/bank choices and HDA ring-size/status meanings.

The definitions are tightly coupled to DCN 3.0.2. Reusing them with a different offset header or another ASIC revision can silently program the wrong bits.

## Integration Points

The main integration points are:

- **MPC/RMU color pipeline:** shaper LUTs and 3D LUTs are used for post-blend or multi-plane color-management paths. DRM color state and DC color transforms eventually become RAM region descriptors, LUT entries, output normalization, offsets, scales, and active LUT-bank selections.
- **ABM/backlight:** Display Core and DMUB-assisted backlight paths program PWM levels, current/target/user brightness, sample rates, and HGLS/ACE/statistics controls. The repeated `ABM0` through `ABM4` blocks support multiple display/backlight instances.
- **Diagnostics/performance:** `DC_PERFMON25` and `DC_PERFMON26` expose counter selection, run control, current-value selection, interrupt, and readback fields for low-level display diagnostics or debug tooling.
- **HPO clocking:** `HPO_TOP_CLOCK_CONTROL` participates in high-performance-output clock gating, specifically the HDMI stream clock gate-disable bit in this generation slice.
- **Audio:** HDA/Azalia controller and endpoint fields integrate GPU display audio with command ring, response ring, immediate command, DMA position, and wall-clock mechanisms.
- **Legacy display compatibility:** VGA sequencer and CRT-controller fields provide low-level definitions for VGA-compatible indexed register access where needed.

## Risks And Edge Cases

- **Generated ABI drift:** The most important risk is mismatch between this shift/mask header and the corresponding offset header or hardware generation. Such mismatches compile cleanly but corrupt MMIO field programming.
- **Chunk boundary context:** The slice begins mid-register at `MPC_RMU1_SHAPER_RAMB_REGION_26_27` mask definitions and ends mid-VGA CRT block after `CRT07` partial fields. The final merged per-file research should combine adjacent chunks for complete block coverage.
- **Indexed RAM/LUT sequencing:** Shaper and 3D LUT writes rely on index, data, bank, and write-enable fields. Off-by-one indexes, wrong bank selection, or switching active mode before loading completes can produce visible color corruption.
- **Double-buffer and frame-boundary latching:** ABM and backlight fields include lock, pending, readback, and frame-start controls. Incorrect ordering can miss a frame, expose stale readbacks, or leave pending bits set.
- **Write-one/clear-style status:** Missed-frame clear, performance counter ack, HDA pointer reset, interrupt ack, and overrun/status fields are likely side-effect-sensitive. Read-modify-write helpers must preserve unrelated bits and use the hardware-required clear semantics.
- **Memory-address alignment:** HDA RIRB and DMA-position lower base registers mask low unimplemented bits. Callers must provide correctly aligned DMA memory and program upper/lower addresses consistently.
- **Clock gating:** Forcing or disabling HPO stream-clock gating at the wrong time can affect HDMI/HPO bring-up, power behavior, or link stability.
- **Legacy VGA packed bits:** `CRT07` carries high bits for multiple vertical timing fields. Any consumer must update it as a packed register, not as independent uncoordinated fields.

## Test Signals

Useful validation signals for changes touching consumers of these macros include:

- Successful AMDGPU/DC build coverage for DCN 3.0.2 paths, ensuring generated shift/mask names match resource table references.
- Display color-management tests that exercise shaper LUT and 3D LUT enable/disable, bank switching, LUT upload, 30-bit mode, and output normalization/scale programming.
- Visual or CRC-based display validation after programming LUTs, especially across atomic commits, modesets, suspend/resume, and power-gating transitions.
- Backlight tests that set user/current/target brightness, enable/disable ABM, verify smooth transitions, read HGLS status, and confirm missed-frame clear behavior.
- Hardware diagnostics or debugfs tests that program `DC_PERFMON25`/`DC_PERFMON26`, observe counters incrementing for selected events, and verify interrupt/status ack paths.
- HDMI/HPO bring-up and hotplug testing around `HPO_TOP_CLOCK_CONTROL`, watching for link training, audio, and clock-gating regressions.
- HDMI/DP audio playback and codec-command tests that exercise CORB/RIRB DMA, immediate command busy/result-valid polling, response interrupts, DMA position buffer updates, and overrun/error status.
- Legacy VGA or firmware-console handoff smoke tests if code paths still use the `SEQ*`/`CRT*` fields.

For this exact header chunk, the basic repository-level signal is that `Docs/researches/chunks/subset-b-001772_research.md` exists and is non-empty; no generated source or checklist state should be changed by this research item.

### subset-b-001773: lines 54371-56929

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 54371-56929

## Purpose

This chunk is generated AMD DCN 3.0.2 register field metadata. It contains no executable C code; it publishes `#define` constants for field shifts and masks used by AMDGPU display code when packing and unpacking DCN 3.0.2 register values.

The selected range spans 2,054 macro definitions. It starts in the middle of the legacy VGA CRTC indexed register field block, covers the VGA graphics and attribute indexed fields, then covers a large part of the Azalia/HD-audio display-audio register model. The Azalia coverage includes F2 codec converter/pin/root fields, audio descriptor and sink-info indexed fields, CRC result fields, input endpoint fields, stream latency/FIFO fields for streams 0 through 15, all endpoint 0 converter and pin-control fields, and endpoint 1 fields through the first `AZF0ENDPOINT1_AZALIA_F0_CODEC_PIN_CONTROL_SINK_INFO8__DESCRIPTION16__SHIFT` line. The following endpoint 1 hot-plug, configuration-default, multichannel-enable2, channel-status override, and later fields are outside this chunk.

Although this file is under a local `ceph-client` source mirror, the content is AMDGPU display-controller hardware metadata, not Ceph or distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation sites, locks, or callbacks in this range. Its public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a field within the register value.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field, normally written with an `L` suffix.

Major macro families in this slice:

- VGA CRTC tail: `CRT07` through `CRT22` fields for legacy timing extension bits, row scan and byte pan, cursor position and shape, display start, vertical sync/blank/display-end values, pitch, underline, address-count mode, line compare, and basic decode status fields.
- VGA graphics indexed registers: `GRA00` through `GRA08` fields for set/reset bits, set/reset enables, color compare, rotate/function select, read map select, write/read mode, odd/even addressing, graphics/address-select mode, color don't-care bits, and bit mask.
- VGA attribute indexed registers: `ATTR00` through `ATTR14` fields for palette entries, graphics/monochrome/line-graphics/blink/panning/pixel-clock/color-select modes, overscan color, plane enable, horizontal pixel pan, and color select.
- `AZALIA_F2_CODEC_CONVERTER_*`: converter stream format, stream/channel ID, digital converter control, stripe control, ramp rate, GTC embedding, audio widget capabilities, supported rates, and stream-format capabilities.
- `AZALIA_F2_CODEC_PIN_CONTROL_*`: connection list, widget control, unsolicited response, pin sense, configuration defaults, speaker/channel allocation, downmix, audio descriptor selection/data, multichannel controls, lipsync, HBR, sink-info index/data, LPIB snapshot/readback, coding type, format-change status, wireless display identification, and remote keepalive.
- `AZALIA_F2_PIN_CONTROL_CODEC_CS_OVERRIDE_*`: IEC 60958 channel-status override fields for mode, source, clock accuracy, word length, sample frequency, original sample frequency, CGMS-A, category, channel numbers, and source number.
- Descriptor and sink-info indexed blocks: `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`, `AZALIA_F2_CODEC_PIN_CONTROL_MANUFACTURER_ID`, `PRODUCT_ID`, `SINK_DESCRIPTION_LEN`, `PORTID0/1`, and `SINK_DESCRIPTION0` through `SINK_DESCRIPTION17`.
- CRC result blocks: `AZALIA_INPUT_CRC0/1_CHANNEL0..7` and `AZALIA_CRC0/1_CHANNEL0..7`, each exposing full-register CRC result fields.
- `AZALIA_F2_CODEC_INPUT_*`: input converter and input pin-control fields for format, stream/channel, digital converter control, capabilities, configuration default, channel allocation, multichannel channels 0 through 7, HBR, LPIB, input status, infoframe header/body/checksum, and audio channel status low/high words.
- `AZALIA_F2_CODEC_ROOT_*` and function-control fields: vendor/device ID, revision ID, node count, power state, subsystem ID response bytes, converter synchronization, reset, group type, supported rates/formats, and power-state capabilities.
- `AZF0STREAM0` through `AZF0STREAM15`: repeated stream FIFO-size control, latency counter control, worst-case latency, cumulative latency, and cumulative request count fields.
- `AZF0ENDPOINT0_AZALIA_F0_*`: endpoint 0 converter and pin fields for capabilities, format programming, GTC counter deltas, pin capabilities, unsolicited response, pin sense, widget control, speaker/channel allocation, descriptors 0 through 13, multichannel enables, lipsync, HBR, sink info, hot-plug control, forced unsolicited response, default configuration, multichannel enable2/mode, channel-status overrides, LPIB/coding/format-change, wireless/keepalive, and audio enable/interrupt status.
- `AZF0ENDPOINT1_AZALIA_F0_*`: endpoint 1 converter and pin fields through sink-info description field `DESCRIPTION16` in `SINK_INFO8`; it mirrors the early endpoint 0 shape but this chunk stops before endpoint 1 hot-plug and later controls.

The masks and shifts are usually consumed through token-pasting macros such as `SF(reg_name, field_name, __SHIFT)` and `SF(reg_name, field_name, _MASK)`, not by handwritten references to every generated macro.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by the display driver:

1. DCN 3.0.2 resource code includes `dcn_3_0_2_offset.h` and this matching `dcn_3_0_2_sh_mask.h`.
2. Resource macros such as `SF(reg_name, field_name, post_fix)` paste register and field tokens into names like `AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_INDEX__AZALIA_ENDPOINT_REG_INDEX_MASK`.
3. Static shift/mask tables are initialized, for example `audio_shift` and `audio_mask` in `dcn302_resource.c`.
4. Component constructors such as `dce_audio_create()` receive the register, shift, and mask tables.
5. Later display-audio, stream-encoder, hotplug, and modeset paths use register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, and indexed-register accessors to read, modify, and write the hardware fields.

The selected macros do not encode ordering. Consumers still must sequence power/clock enablement, endpoint index/data access, audio stream setup, sink capability discovery, infoframe and channel-status programming, interrupt clear/ack, hotplug response, and suspend/resume restore correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes bit layouts for MMIO or indexed-register state maintained by the GPU display hardware.

Important hardware state represented by the fields includes:

- Legacy VGA state: CRTC timing extension bits, cursor position, display start, graphics plane behavior, attribute palette/mode/panning/color selection, and decode behavior.
- Display-audio converter state: stream format, channel and stream IDs, digital converter enable/status, non-audio/professional/copyright/emphasis bits, ramp/GTC controls, supported-rate and widget-capability reporting.
- Pin and sink state: pin widget control, unsolicited response tag/enables, pin sense, ELD-like manufacturer/product/port/description data, speaker/channel allocation, descriptor capabilities, HBR and lipsync flags, and default pin configuration fields.
- Audio transport and diagnostics: multichannel enable/mute/channel IDs, LPIB snapshots and timers, input CRC/output CRC result registers, FIFO allocation, worst-case and cumulative latency counters, request counters, and audio enable/format-change interrupts.
- Input-audio state: input converter and pin fields, infoframe payload bytes, input status, and channel status words.

Persistence is hardware-defined. Configuration fields generally remain until overwritten, power-gated, reset, or restored after suspend/resume. Status, interrupt, CRC, counter, snapshot, pin-sense, and unsolicited-response fields may be read-only, sticky, write-one-to-clear, self-clearing, or latch-on-read depending on the register. This generated header gives only masks and shifts; it does not identify access type or side effects.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.0.2 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h`, which supplies matching register offsets and base-index constants.
- DCN base segment definitions used by `BASE(mm..._BASE_IDX)` in resource code.
- Display component register table definitions for audio, AFMT, stream encoders, and DIO blocks that expect these field names to exist.

The direct include site for this ASIC generation in the inspected tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c`. That file defines `SR`, `SRI`, and `SF` token-pasting helpers, includes the offset and shift/mask headers, and initializes structures such as `audio_shift` and `audio_mask`. In the audio path, `DCE120_AUD_COMMON_MASK_SH_LIST(__SHIFT)` and `DCE120_AUD_COMMON_MASK_SH_LIST(_MASK)` populate common Azalia endpoint index/data fields plus the base audio field list before `dce_audio_create()` constructs the audio object.

The broader integration point is the AMD Display Core register-helper framework. The generated constants are compile-time data for register packing, not a hardware abstraction on their own.

## Risks And Edge Cases

- Mask/shift drift is the central risk. A wrong value still compiles but can silently write the wrong bits in hardware.
- The selected range is artificially chunked. It begins after the start of the VGA CRTC block and ends inside endpoint 1 sink-info fields, so adjacent chunks are required for complete file-level reasoning.
- Repeated Azalia families are copy-sensitive. F2 codec, input codec, streams 0 through 15, endpoint 0, and endpoint 1 have similar field layouts; an incorrect prefix or channel index can affect only one audio endpoint, stream, or multichannel lane.
- Indexed endpoint access is order-sensitive. Fields behind endpoint index/data registers rely on the caller selecting the correct index before reading or writing data.
- Status and interrupt fields may be sticky or write-one-to-clear. Treating these masks as ordinary read/write configuration bits can lose hotplug, format-change, audio-enabled, audio-disabled, or unsolicited-response events.
- Sink-info and descriptor fields encode externally visible audio capabilities. Bad masks can corrupt ELD-like information, causing wrong channel counts, sample-rate exposure, HBR capability reporting, speaker allocation, or sink description strings.
- Legacy VGA fields are rarely exercised in modern modesets but can matter for firmware handoff, VGA-compatible paths, early boot display, virtualization, and console fallback.

## Test Signals

Useful validation signals for changes touching this chunk or generated data around it include:

- Build coverage of the AMDGPU display driver for the DCN 3.0.2 target; token-pasting users catch missing or renamed field macros at compile time.
- Display bring-up on DCN 3.0.2 hardware with HDMI/DP audio enabled, including stereo and multichannel playback.
- Hotplug and modeset tests that verify audio devices appear and disappear correctly, unsolicited responses are delivered, and audio enable/disable or format-change interrupts are acknowledged.
- EDID/ELD and sink capability checks: channel count, speaker allocation, supported rates, HBR support, manufacturer/product IDs, port ID, and sink description should match the connected display.
- Suspend/resume and runtime power-management tests that verify audio state, endpoint configuration, and legacy display handoff recover after power gating.
- Diagnostic register reads for LPIB, stream latency counters, FIFO allocation, CRC channels, and format-change status when debugging audio underruns, silence, or wrong stream mapping.

### subset-b-001774: lines 56930-59302

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 56930-59302

## Scope

This chunk is a generated register field header slice from the AMD DCN 3.0.2 ASIC register tables. It contains C preprocessor `#define` constants for bit shifts and masks, not executable functions. The specific range spans the tail of Azalia endpoint 1 pin/audio fields, the complete repeated field maps for Azalia endpoints 2 through 5, and the start of endpoint 6 converter widget capability fields.

The slice defines 2046 shift/mask macros across 313 endpoint-specific register blocks. The naming pattern is:

`AZF0ENDPOINT<N>_<REGISTER>__<FIELD>__SHIFT` and `AZF0ENDPOINT<N>_<REGISTER>__<FIELD>_MASK`

where `N` is an Azalia audio endpoint instance and `<REGISTER>` names an indirectly addressed HDMI/DP audio codec endpoint register.

## Purpose

The purpose of this header range is to give the display/audio driver exact bit positions for DCN 3.0.2 Azalia codec endpoint registers. The masks are consumed by register helper macros such as `SF()`, `FN()`, `REG_SET()`, `REG_GET()`, and `set_reg_field_value()` through resource-specific shift/mask tables. They prevent hard-coded bit arithmetic in the audio implementation and keep the driver aligned with the generated ASIC register specification.

In the wider DCN 3.0.2 integration, `dcn302_resource.c` includes both `dcn_3_0_2_offset.h` and this `dcn_3_0_2_sh_mask.h`. It creates `audio_regs[]` for audio instances 0 through 6 and initializes `struct dce_audio_shift` / `struct dce_audio_mask` from the generated symbols. Runtime Azalia access is performed by `dce_audio.c`, which writes an endpoint index register and then reads or writes endpoint data.

## Important Register Families

This chunk is dominated by repeated endpoint-local register families:

- `AZF0ENDPOINT1_*`: tail of endpoint 1 pin control fields. The chunk begins after `SINK_INFO8` has already started in the previous chunk, then covers hot-plug control, forced unsolicited responses, default pin configuration, multichannel controls, IEC 60958 channel status overrides, LPIB snapshot state, format-change state, remote keepalive, and audio enable/disable/format-change interrupt status.
- `AZF0ENDPOINT2_*`, `AZF0ENDPOINT3_*`, `AZF0ENDPOINT4_*`, `AZF0ENDPOINT5_*`: complete repeated maps for four Azalia codec endpoints. These include converter capability/control fields, pin capability/control fields, descriptor fields, sink information fields, channel status overrides, LPIB state, and interrupt/status fields.
- `AZF0ENDPOINT6_*`: start of endpoint 6, covering `CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` through the beginning of `CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT`; the rest of endpoint 6 continues in the next chunk.

The main field groups are:

- Converter capabilities and format: `AUDIO_CHANNEL_CAPABILITIES`, amplifier presence/override flags, `FORMAT_OVERRIDE`, `STRIPE`, `PROCESSING_WIDGET`, `UNSOLICITED_RESPONSE_CAPABILITY`, `CONNECTION_LIST`, `DIGITAL`, `POWER_CONTROL`, `LR_SWAP`, widget delay, type, `NUMBER_OF_CHANNELS`, `BITS_PER_SAMPLE`, sample base divisor/multiple/rate, and stream type.
- Converter stream routing: `STREAM_ID`, `CHANNEL_ID`, digital converter enable/validity, category code, pre-emphasis, copy/level flags, professional/consumer status, and V-bit or validity behavior.
- Timing and GTC: `GTC_EMBEDDING_ENABLE`, `GTC_EMBEDDING_GROUP`, `GTC_EMBEDDING_HBR_AUDIO_PACKET_ALIGN`, and counter delta/min/max fields.
- Pin capabilities and controls: impedance/presence detect, trigger requirement, HDMI/DP/HBR support bits, unsolicited response tag/enable, pin sense, widget enable, channel/speaker allocation, and multiple CEA-like audio descriptor fields.
- Multichannel and speaker mapping: base `MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2` fields encode enable/mute/channel-id triplets for odd channel lanes 1/3/5/7 and related channel layout state.
- Sink and descriptor metadata: audio descriptors 0-13, `SINK_INFO0` through `SINK_INFO8`, manufacturer/product/port IDs, sink description bytes, and default configuration fields such as sequence, default association, color, connection type, default device, location, and port connectivity.
- IEC 60958 channel status overrides: `PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8` cover source number, clock accuracy, word length, sampling frequency, original frequency, sampling-frequency coefficient, MPEG surround, CGMS-A, and channel numbers.
- Runtime/status fields: hot-plug clock gating and `AUDIO_ENABLED`, `OUTPUT_ACTIVE`, `LPIB`, `LPIB_TIMER_SNAPSHOT`, cyclic buffer wrap count, coding type, format-change reason/response, wireless display identification, remote keepalive capability, and enabled/disabled/format-changed interrupt flag/mask/type fields.

## APIs, Types, and Macros

This slice does not declare functions, structs, enums, or storage. Its API surface is the macro namespace exported by the header.

Important consumers in the AMD display tree include:

- `dcn302_resource.c`, which includes this header and builds DCN 3.0.2 audio register descriptors. `audio_regs[]` binds per-instance MMIO endpoint index/data registers, while `audio_shift` and `audio_mask` are initialized with generated `_SHIFT` and `_MASK` constants.
- `struct dce_audio_registers`, `struct dce_audio_shift`, and `struct dce_audio_mask` in `dce_audio.h`, which carry register addresses and common field layout information into the DCE audio implementation.
- `dce_audio.c`, where `write_indirect_azalia_reg()` and `read_indirect_azalia_reg()` program `AZALIA_ENDPOINT_REG_INDEX` and `AZALIA_ENDPOINT_REG_DATA`. Higher-level audio paths then use `AZ_REG_READ()` and `AZ_REG_WRITE()` with indirect register indices such as `AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL`.

The endpoint-specific macros in this chunk are generated for all endpoints, but the common DCE audio code mostly abstracts access through the selected audio instance and generic Azalia register names. The resource layer chooses the correct instance registers, and the shift/mask table supplies the bit layout.

## Control Flow and Data Flow

There is no direct control flow in this header chunk. Runtime flow through the surrounding driver is:

1. DCN 3.0.2 resource construction includes the generated offset and sh/mask headers.
2. Resource initialization creates audio objects for available instances, using `audio_regs[inst]`, `audio_shift`, and `audio_mask`.
3. Higher layers assign audio resources to display streams based on sink EDID audio information, stream signal type, and available audio endpoints.
4. Audio configuration code uses indirect Azalia reads/writes. It first writes an endpoint register index to the endpoint index MMIO register, then reads/writes endpoint data.
5. Field helpers apply the generated shifts and masks to set fields such as `CLOCK_GATING_DISABLE`, `AUDIO_ENABLED`, descriptor fields, channel allocation, HBR capability, and lipsync/format values.

For this chunk, the most visible runtime state mutation is hot-plug/audio enable behavior. `dce_aud_az_enable()` reads `AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL`, sets `CLOCK_GATING_DISABLE` and `AUDIO_ENABLED`, writes the register, then clears clock-gating disable. `dce_aud_az_disable()` performs the inverse for `AUDIO_ENABLED`. The endpoint 1-5 hot-plug control masks in this chunk specify the exact bits used for the endpoint-local versions of that register.

## State and Persistence

The macros themselves are compile-time constants and hold no mutable state. The state they describe is hardware state in Azalia codec endpoint registers:

- Persistent while programmed: endpoint data fields such as audio descriptors, sink metadata, default configuration, channel allocation, IEC 60958 overrides, and multichannel setup stay in hardware until reprogrammed, reset, power-gated, or overwritten by another driver path.
- Volatile/status-like: pin sense, output active, LPIB snapshots, timer snapshots, audio enable status, and interrupt flag fields reflect hardware activity and can change asynchronously.
- Control/ack fields: forced unsolicited response, format-change acknowledgement/response, interrupt masks, and clock gating/audio enable fields can affect event delivery and hardware behavior.

Because this is an ASIC register definition file, persistence semantics are determined by the hardware block and the driver sequences in `dce_audio.c`, not by this header.

## Dependencies and Integration Points

This chunk depends on the generated DCN 3.0.2 register naming contract:

- Address macros from `dcn_3_0_2_offset.h` define MMIO and indirect register indices, including endpoint index/data registers and `ixAZF0ENDPOINT*` indirect indices.
- Shift/mask macros from this file define how to extract or update fields within those registers.
- Register helper infrastructure (`reg_helper.h`) uses the shift and mask structs to implement field update macros.
- DC resource files for a specific ASIC generation, especially `dcn302_resource.c`, bind generated register metadata to audio objects.
- DCE audio code (`dce_audio.c`) performs the actual HDMI/DP audio programming and status reads.

The repeated endpoint layout is an integration contract between hardware generation files and the generic audio code. If a field name changes here, the `SF()`/`FN()` expansions that expect that field name fail at compile time. If a mask value changes incorrectly, the driver can compile but program the wrong hardware bits.

## Risks and Edge Cases

- Chunk boundary risk: this range starts mid endpoint 1 sink-info sequence and ends mid endpoint 6 converter format. A final merged per-file report must reconcile this chunk with adjacent chunks to avoid treating endpoint 1 or endpoint 6 as incomplete hardware support.
- Generated-header drift: hand-editing any mask or shift can silently break audio enablement, EDID-derived audio descriptors, HBR reporting, channel mapping, or interrupt behavior.
- Endpoint repetition risk: endpoint 2 through 5 definitions are structurally identical by design. Copy/generation errors for a single endpoint can affect only that audio instance and may appear as connector-specific audio failure.
- Indirect register access risk: the endpoint register data path relies on writing the correct index before data access. Wrong `ix` indices from the paired offset header or wrong masks here can make reads/writes target valid but unintended fields.
- Status/control overlap: fields such as `FORMAT_CHANGED`, interrupt flags/masks, and `AUDIO_ENABLED` can be touched by hotplug, stream reconfiguration, and interrupt handling paths. Incorrect masks can leave interrupts stuck, suppress notifications, or report stale audio state.
- Hardware-variant risk: this file is specific to DCN 3.0.2. Sharing assumptions with nearby generations such as DCN 3.0.1, 3.0.3, or 3.2.x should be validated against their own generated headers.

## Test Signals

Useful validation signals for changes involving this header or its consumers:

- Build the AMDGPU display driver with DCN 3.0.2 resource support enabled; field name mismatches in `SF()`/`FN()` initializers should fail compilation.
- Exercise HDMI/DP audio on hardware using audio instances corresponding to endpoints 1 through 6, including plug/unplug and stream reconfiguration.
- Confirm `AUDIO_ENABLED` transitions by checking driver logs around `dce_aud_az_enable()` and `dce_aud_az_disable()` or by reading the Azalia hot-plug control endpoint register.
- Validate EDID audio descriptor propagation for LPCM and compressed formats, channel counts, sample rates, HBR capability, speaker allocation, sink name/manufacturer/product metadata, and lipsync fields.
- Test multichannel and HBR audio paths because this chunk contains both base and secondary multichannel enable fields plus HBR response/capability masks.
- Check interrupt behavior for audio enabled, audio disabled, and audio format changed status fields; stuck or missing events can indicate incorrect flag/mask/type bit definitions.
- Compare generated masks against the ASIC register source or a known-good generated header when updating DCN 3.0.2 register files.

## Summary

Lines 56930-59302 of `dcn_3_0_2_sh_mask.h` are a generated DCN 3.0.2 Azalia endpoint field map. They provide the bit-level contract for HDMI/DP audio endpoint registers, especially endpoints 2 through 5 and boundary portions of endpoints 1 and 6. The driver integrates these constants through DCN 3.0.2 resource initialization and the generic DCE audio indirect-register path; correctness is primarily validated by compile-time field expansion plus runtime HDMI/DP audio, hotplug, descriptor, multichannel, HBR, and interrupt behavior.

### subset-b-001775: lines 59303-61604

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 59303-61604

## Scope

This chunk covers 2,302 lines from the generated DCN 3.0.2 shift/mask header. It contains only C preprocessor constants and generated grouping comments; there are no functions, structs, enums, storage objects, or executable statements in this slice.

The line range is part of the AMD display Azalia function 0 register field map. It starts in the middle of the `AZF0ENDPOINT6_AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` field list, continues through the rest of output endpoint 6, covers a complete output endpoint 7 block, then covers complete input endpoint 0 through input endpoint 3 blocks and the beginning of input endpoint 4. It ends inside `AZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_HOT_PLUG_CONTROL`, after the `CLOCK_GATING_DISABLE_MASK` definition and before the remaining masks and later input endpoint 4 pin-control groups.

The chunk contains 2,035 `#define` entries: 1,014 `__SHIFT` definitions and 1,021 `_MASK` definitions. The named register groups include 70 output endpoint 6 groups, 71 output endpoint 7 groups, 23 groups each for input endpoints 0-3, and 16 groups for the partial input endpoint 4 block.

## Purpose

The purpose of this header region is to provide symbolic bit positions and bit masks for DCN 3.0.2 display-audio hardware registers. The AMDGPU display code can use these generated constants through register helper macros instead of embedding raw shifts and masks when it programs or reads Azalia/HD-audio-style converter and pin registers.

For output endpoints 6 and 7, this chunk describes converter format, stream/channel routing, digital converter state, supported stream formats and size/rate capabilities, stripe/ramp/GTC controls, pin widget and pin capabilities, speaker/channel mapping, audio descriptors, multichannel routing, lipsync and HBR state, sink information, hot-plug state, forced unsolicited responses, default configuration, IEC channel-status overrides, LPIB snapshots, coding type, format-change state, wireless-display identification, remote keepalive, audio enable status, and audio enable/disable/format-change interrupt status.

For input endpoints 0 through 4, it describes input converter capabilities, input stream format selection, channel/stream IDs, digital converter flags, supported input stream formats and size/rates, input pin capabilities, unsolicited-response controls, input pin-sense state, widget input enable, multichannel routing, HBR, channel allocation, hot-plug audio state, default configuration, LPIB snapshots, input activity/status controls, and audio infoframe fields. Input endpoint 4 is incomplete in this chunk and continues in the next source range.

This is a hardware contract file. Its value is the exact macro name and numeric field layout consumed by ASIC-specific DCN register code, not local algorithmic behavior.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the preprocessor naming contract:

- `AZF0ENDPOINT<n>_<REGISTER>__<FIELD>__SHIFT` gives the bit offset for an output endpoint register field.
- `AZF0ENDPOINT<n>_<REGISTER>__<FIELD>_MASK` gives the mask for the same output endpoint field.
- `AZF0INPUTENDPOINT<n>_<REGISTER>__<FIELD>__SHIFT` and `_MASK` provide the equivalent contract for input endpoint registers.
- Comments such as `// addressBlock: azf0endpoint7_endpointind` and `//AZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL` group generated constants by indexed register block and logical register.

The output endpoint register families covered here include:

- `AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, with widget capability fields such as channel capability, amplifier presence, format override, stripe, processing widget, unsolicited response, connection list, digital, power control, LR swap, widget delay, and type. Endpoint 6's first capability group is partial in this range; endpoint 7's is complete.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT`, which maps number of channels, bits per sample, sample base divisor, sample base multiple, sample base rate, and stream type.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_CHANNEL_STREAM_ID`, with channel ID and stream ID fields.
- `AZALIA_F0_CODEC_CONVERTER_CONTROL_DIGITAL_CONVERTER`, which maps `DIGEN`, validity/config/preemphasis/copy/non-audio/professional flags, category code, and `KEEPALIVE`.
- `AZALIA_F0_CODEC_CONVERTER_PARAMETER_STREAM_FORMATS` and `AZALIA_F0_CODEC_CONVERTER_PARAMETER_SUPPORTED_SIZE_RATES`, which expose supported format, rate, and bit-depth bitmaps.
- `AZALIA_F0_CODEC_CONVERTER_STRIPE_CONTROL`, `CONTROL_RAMP_RATE`, `CONTROL_GTC_EMBEDDING`, and `GTC_COUNTER_DELTA*`, which cover striping, ramp rate, GTC embedding, and GTC delta counters.
- `AZALIA_F0_CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `AZALIA_F0_CODEC_PIN_PARAMETER_CAPABILITIES`, which describe pin-side widget and pin capabilities including HDMI/DP, EAPD, VREF, input/output capability, balanced I/O, presence-detect, trigger, and headphone drive fields.
- `AZALIA_F0_CODEC_PIN_CONTROL_CHANNEL_SPEAKER`, `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`, `MULTICHANNEL_ENABLE`, `MULTICHANNEL_ENABLE2`, and `MULTICHANNEL_MODE`, which describe speaker allocation, channel allocation, SAD-like descriptor bytes, per-channel enable/mute/channel-ID fields, and multichannel mode.
- `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_LIPSYNC`, `RESPONSE_HBR`, and `SINK_INFO0` through `SINK_INFO8`, which expose video/audio latency, HBR capability/enablement, manufacturer/product identity, port ID, sink description bytes, connection info, and converter ID.
- `AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8`, which define IEC 60958 channel-status override value and enable fields such as mode, category code, source number, channel numbers, clock accuracy, word length, sampling frequency, original sampling frequency, CGMS-A, and MPEG surround information.
- `AZALIA_F0_CODEC_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL`, `LPIB`, and `LPIB_TIMER_SNAPSHOT`, which describe position/timer snapshot fields.
- `AZALIA_F0_AUDIO_ENABLE_STATUS`, `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, and `AUDIO_FORMAT_CHANGED_INT_STATUS`, which define audio enabled state plus interrupt flag/mask/type fields.

The input endpoint register families covered here include:

- `AZALIA_F0_CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, `INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT`, `INPUT_CONVERTER_CONTROL_CHANNEL_STREAM_ID`, `INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`, `INPUT_CONVERTER_PARAMETER_STREAM_FORMATS`, and `INPUT_CONVERTER_PARAMETER_SUPPORTED_SIZE_RATES`, mirroring the converter-side output endpoint fields with input endpoint names.
- `AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `INPUT_PIN_PARAMETER_CAPABILITIES`, which define input pin widget and pin capability fields.
- `INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE`, `RESPONSE_INPUT_PIN_SENSE`, and `WIDGET_CONTROL`, which cover unsolicited response tags/enables, impedance/presence bits, and input widget enable.
- `INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2`, which pack enable, mute, and channel-ID fields for input multichannel slots 0-7.
- `INPUT_PIN_CONTROL_RESPONSE_HBR`, `CHANNEL_ALLOCATION`, `HOT_PLUG_CONTROL`, `UNSOLICITED_RESPONSE_FORCE`, `RESPONSE_CONFIGURATION_DEFAULT`, `LPIB*`, `INPUT_STATUS_CONTROL`, and `INFOFRAME`, which cover input-side HBR, channel allocation, hot-plug audio enable state, forced unsolicited responses, pin default configuration, position snapshots, input activity/channel layout, and infoframe contents.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time macro resolution:

1. DCN 3.0.2 display code includes this `*_sh_mask.h` header together with the matching DCN 3.0.2 register offset header.
2. Register helper macros in the AMD display stack concatenate register and field tokens to resolve `__SHIFT` and `_MASK` constants.
3. Runtime code uses those resolved constants in MMIO read/modify/write paths, register-table initialization, or status extraction.

The declaration order still carries generated hardware structure. The chunk begins inside output endpoint 6, enters a complete `// addressBlock: azf0endpoint7_endpointind` block, then enters `azf0inputendpoint0_inputendpointind` through `azf0inputendpoint4_inputendpointind` blocks in ascending order. Within each register group, shift definitions generally appear before mask definitions for the same fields.

## State And Persistence Behavior

The header itself stores no state and persists no data. It describes bit layout for hardware state in the DCN 3.0.2 display audio block:

- Converter controls represent programmed audio stream shape, stream/channel association, IEC/digital converter flags, keepalive behavior, stripe/ramp configuration, and GTC timing/counter relationships.
- Capability registers represent hardware-advertised widget, pin, stream-format, sample-rate, and sample-size support. The macro file does not encode read/write permissions, so consumers must follow the hardware programming model.
- Output pin controls represent HDMI/DisplayPort audio presentation state, including speaker/channel allocation, audio descriptor data, lipsync, HBR, sink identity, sink connection data, hot-plug audio enablement, format-change state, wireless-display identification, and remote keepalive.
- IEC channel-status override fields can alter transmitted channel-status metadata when the paired override-enable bits are programmed.
- LPIB and timer snapshot fields represent hardware position/timing state, including snapshot lock and cyclic-buffer wrap count fields.
- Interrupt status fields represent audio enabled, disabled, and format-changed flag/mask/type state.
- Input pin controls represent input activity, channel layout, infoframe validity/data, input pin sense, unsolicited-response setup, and multichannel channel-slot routing.

Persistence is hardware-defined. Writable control fields may retain values until driver reprogramming, display/audio block reset, suspend/resume restore, or ASIC reset. Status and capability fields may change asynchronously as hardware state, connected sinks/sources, or display audio paths change.

## Dependencies And Integration Points

This chunk depends on generated DCN 3.0.2 register files staying synchronized:

- `dcn_3_0_2_offset.h` supplies matching `mm...` indirect index/data register addresses and `ix...` indexed register offsets for the register names whose fields are defined here. For example, the matching offset header defines the endpoint 7 indexed register access pair and input endpoint 4 indexed register offsets through `ixAZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME`.
- AMD display register helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, and `FD_SHIFT` rely on the exact `__SHIFT` and `_MASK` suffix convention.
- DCN resource, audio, HDMI, and DisplayPort paths integrate with these constants when programming display audio endpoints, reading sink capabilities/status, handling audio hotplug, and restoring register state around power transitions.
- Hardware register databases and generated offset/value headers provide the source-of-truth semantics for field values. This header only maps field positions and masks.

The main integration point is the preprocessor name contract. Missing or renamed macros usually fail at compile time. Wrong numeric shifts or masks can compile successfully while causing incorrect MMIO field extraction or writes.

## Risks And Edge Cases

- The chunk starts mid-register group and ends mid-register group. Endpoint 6's first converter capability group and input endpoint 4's hot-plug and later pin controls must be reconciled with adjacent chunks before whole-endpoint completeness claims are made.
- The endpoint blocks are mechanically repetitive. Generator drift affecting only one endpoint number can be hard to notice during review because most lines differ only by the endpoint prefix.
- Shift/mask mismatches are high risk. Bad definitions for high-bit fields such as `AUDIO_ENABLED`, `PRESENCE_DETECT`, `INFOFRAME_VALID`, `DOWN_MIX_INHIBIT`, or interrupt type/mask bits may not be caught by compilation.
- Several full-width masks use `0xFFFFFFFFL`, including stream formats, GTC deltas, LPIB, timer snapshots, and association/info payload fields. Consumers should avoid signed-width assumptions when combining these values.
- Capability, status, and control fields share the same macro style. This header does not prevent writes to read-only or write-one-to-clear style fields.
- `UNSOLICITED_RESPONSE_FORCE` fields can synthesize events. Incorrect writes to force bits could create misleading audio, hotplug, or pin notifications.
- Multichannel enable registers pack enable, mute, and 4-bit channel-ID fields for four slots per register. An incorrect mask can corrupt adjacent slot fields.
- IEC channel-status override registers use both values and override-enable bits. Programming only a value field, or using the wrong endpoint's override field, can silently leave transmitted metadata unchanged.
- Cross-generation reuse is risky. DCN 3.0.2 Azalia field names are similar to earlier DCN headers, but code must include the offset and shift/mask files that match the target ASIC.

## Test Signals

Useful validation signals are mostly build-time and hardware-integration oriented:

- Compile the DCN 3.0.2 AMD display code that includes this header to catch missing macro names in register-helper expansions.
- Preprocess representative users of `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, and `REG_UPDATE` for Azalia endpoint fields to verify that expected `AZF0ENDPOINT*` and `AZF0INPUTENDPOINT*` macros resolve.
- Compare this header against `dcn_3_0_2_offset.h` and the generator's register database to ensure every indexed endpoint register has matching field definitions and that field masks align with documented bit ranges.
- Exercise HDMI and DisplayPort audio enumeration on DCN 3.0.2 hardware, checking advertised widget/pin capabilities, stream format/rate support, SAD/audio descriptor fields, sink info, and channel allocation.
- Test audio enable/disable, format-change, and hotplug paths while observing `AUDIO_ENABLE_STATUS`, `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, `AUDIO_FORMAT_CHANGED_INT_STATUS`, and hot-plug `AUDIO_ENABLED` fields.
- Exercise stereo, multichannel, and HBR audio modes to validate multichannel enable/mute/channel-ID fields, HBR capability/enable bits, speaker/channel allocation, and IEC channel-status overrides.
- Test suspend/resume and display reset paths to confirm converter, pin, sink info, hotplug, LPIB snapshot, infoframe, interrupt, and keepalive state is restored or re-read correctly.
- For input endpoints, validate input activity, channel layout, infoframe-valid, input pin sense, channel allocation, and unsolicited-response behavior if the platform exposes those input audio paths.

## Open Cross-Chunk Questions

- The merge lane should combine this with the previous chunk to present the beginning of `AZF0ENDPOINT6_AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` accurately.
- The merge lane should combine this with the next chunk to complete `AZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_HOT_PLUG_CONTROL` and the remaining input endpoint 4 register groups.
- Whole-file analysis should verify the expected number of DCN 3.0.2 output and input Azalia endpoint blocks and compare generated masks/shifts against the authoritative AMD register source.

### subset-b-001776: lines 61605-62433

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 61605-62433

## Scope

This chunk is the final slice of the generated DCN 3.0.2 shift/mask header. It contains preprocessor constants only: 742 `#define` entries in this range, split into 370 field shifts and 372 field masks. There are no C functions, structs, enums, or executable statements.

The range starts in the middle of the `AZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_HOT_PLUG_CONTROL` mask group, then covers the tail of input endpoint 4, all generated input endpoint 5 and 6 field definitions, all generated input endpoint 7 field definitions, and finally the header guard `#endif`.

Address blocks and register families covered here:

- Tail of `azf0inputendpoint4_inputendpointind`: hot-plug-control masks plus input pin controls for unsolicited response forcing, default configuration response, LPIB snapshot/readback, input status, and input audio infoframe.
- `azf0inputendpoint5_inputendpointind`, `azf0inputendpoint6_inputendpointind`, and `azf0inputendpoint7_inputendpointind`: full repeated input endpoint register sets.
- The closing file guard for `_dcn_3_0_2_SH_MASK_HEADER`.

## Purpose

This file is part of AMDGPU Display Core's generated hardware register ABI for DCN 3.0.2. The constants describe bit positions and masks inside Azalia F0 codec input endpoint registers. They allow driver register helpers and generated tables to refer to hardware fields symbolically rather than duplicating numeric bit layouts.

At a hardware level, the chunk describes HDMI/DisplayPort audio input endpoint widgets and pins for endpoint instances 5 through 7, plus the end of instance 4. The fields model HD Audio/Azalia converter capabilities, stream format controls, channel and stream IDs, digital converter controls, pin capabilities, unsolicited response handling, sink/presence sensing, multichannel enable/mute/channel routing, HBR audio capability, channel allocation, hot-plug audio enablement, LPIB snapshots, input activity, channel layout, and input infoframe status.

The generated names are instance-qualified, for example `AZF0INPUTENDPOINT5_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT__NUMBER_OF_CHANNELS_MASK`. This preserves the hardware instance relationship and prevents a caller or generated table from accidentally applying endpoint 5 field definitions to a different indexed endpoint block.

## Important APIs, Types, And Constants

There are no callable APIs or local types. The interface is entirely the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same hardware field.
- `// addressBlock: ...` comments: generated grouping markers for endpoint-indexed address blocks.
- `//<REGISTER>` comments: generated grouping markers for individual registers.

Important repeated macro families for endpoints 5, 6, and 7 are:

- `*_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: HD Audio converter widget capability fields such as channel capability, amplifier presence, format override, processing widget, unsolicited response capability, connection list, digital/power-control/LR-swap support, delay, and widget type.
- `*_INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT`: converter format fields for number of channels, bits per sample, sample base divisor/multiple/rate, and stream type.
- `*_INPUT_CONVERTER_CONTROL_CHANNEL_STREAM_ID`: channel ID and stream ID selection fields.
- `*_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`: digital converter control/status fields including `DIGEN`, validity/config/pro/pre/copy/non-audio bits, channel-status category code (`CC`), and `KEEPALIVE`.
- `*_INPUT_CONVERTER_PARAMETER_STREAM_FORMATS` and `*_SUPPORTED_SIZE_RATES`: full stream-format capability mask plus supported audio rates and sample sizes.
- `*_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `*_INPUT_PIN_PARAMETER_CAPABILITIES`: pin widget and pin capability fields including impedance sense, trigger requirement, jack detection, input/output capability, HDMI/DP indication, VREF control, and EAPD capability.
- `*_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE` and `*_UNSOLICITED_RESPONSE_FORCE`: unsolicited response tag/enable bits and forced response payload/force bit.
- `*_INPUT_PIN_CONTROL_RESPONSE_INPUT_PIN_SENSE`: impedance sense and presence detect readback.
- `*_INPUT_PIN_CONTROL_WIDGET_CONTROL`: input-enable bit.
- `*_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE` and `*_MULTICHANNEL_ENABLE2`: enable, mute, and channel-ID fields for multichannel slots 0-7.
- `*_INPUT_PIN_CONTROL_RESPONSE_HBR`: high-bit-rate audio capability and enable fields.
- `*_INPUT_PIN_CONTROL_CHANNEL_ALLOCATION`: CEA/HDMI-style channel allocation byte.
- `*_INPUT_PIN_CONTROL_HOT_PLUG_CONTROL`: clock-gating disable, clock-on state, and audio-enabled fields.
- `*_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT`: HD Audio default configuration fields including sequence, association, misc, color, connection type, default device, location, and port connectivity.
- `*_INPUT_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL`, `*_LPIB`, and `*_LPIB_TIMER_SNAPSHOT`: LPIB snapshot locking, cyclic-buffer wrap count, LPIB value, and timer snapshot readback.
- `*_INPUT_PIN_CONTROL_INPUT_STATUS_CONTROL` and `*_INFOFRAME`: input activity, channel layout, unsolicited-response enables, channel count/allocation, infoframe byte 5, and infoframe validity.

The endpoint 4 portion is partial. It includes two hot-plug-control masks at the start of the chunk, then the same tail pin-control families from unsolicited response force through infoframe.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time and hardware-indexed:

1. DCN 3.0.2 resource code includes `dcn_3_0_2_offset.h` and this `dcn_3_0_2_sh_mask.h` header.
2. Register-list and field-list macros such as `SR`, `SRI`, `SF`, and block-specific table initializers concatenate register and field names to populate per-ASIC register offsets, shifts, and masks.
3. Runtime helpers use those tables with `REG_SET`, `REG_UPDATE`, `REG_READ`, `REG_WRITE`, `get_reg_field_value`, and `set_reg_field_value` style helpers to compose MMIO values or decode readbacks.
4. Azalia audio code accesses endpoint registers through an indirect index/data model: it writes an endpoint register index and then reads or writes endpoint data. This chunk describes part of the endpoint register data layout for indexed input endpoint blocks; the sequencing policy remains in audio and stream-encoder code.

The order in the header is generated and register-database oriented: each register comment is followed by all `__SHIFT` entries and then all `_MASK` entries. Endpoint blocks are repeated numerically.

## State And Persistence Behavior

The header stores no software state and persists no data. It describes hardware state in DCN 3.0.2 Azalia input endpoint registers.

Programmed control state includes converter format, channel/stream IDs, digital converter enable and channel-status bits, input widget enablement, multichannel enable/mute/channel routing, HBR enablement, channel allocation, hot-plug clock-gating and audio-enable policy, unsolicited-response tags/enables, and forced unsolicited response payloads.

Capability and default-configuration state includes audio widget capabilities, supported formats/rates/sample sizes, pin capabilities, HDMI/DP indication, default device/connection/location/port-connectivity descriptors, and HBR capability.

Readback/status state includes presence detect and impedance sense, clock-on state, LPIB and LPIB timer snapshots, cyclic-buffer wrap count, input activity, channel layout, infoframe channel count/allocation, infoframe byte 5, and infoframe-valid status. These fields can change asynchronously with display/audio link state, hot-plug behavior, stream activity, and hardware buffer progression.

Persistence is hardware-defined. Values generally remain until rewritten, reset by the display/audio block, or cleared by a broader ASIC reset. The shift/mask header does not encode read-only, write-only, volatile, latch, or write-one-to-clear semantics, so users must follow the Azalia endpoint programming model supplied by the surrounding display audio code and hardware documentation.

## Dependencies And Integration Points

This generated header depends on its companion DCN 3.0.2 register offset header. Shift/mask macros only identify bit positions; callers also need matching register offsets or indexed register numbers to reach the correct hardware register.

Observed source-tree integration points include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c` includes `dcn/dcn_3_0_2_offset.h` and `dcn/dcn_3_0_2_sh_mask.h`, defines the `SF`/`SRI` macro style used to build register tables, and wires Azalia endpoint index/data fields for the DCE audio object.
- `drivers/gpu/drm/amd/display/dc/dce/dce_audio.c` implements indirect Azalia endpoint access by programming `AZALIA_F0_CODEC_ENDPOINT_INDEX` and reading/writing `AZALIA_F0_CODEC_ENDPOINT_DATA`. It also reads default configuration port connectivity for endpoint validity, toggles hot-plug clock-gating disable while initializing audio rate and power-state fields, and exposes audio functions such as endpoint validation, hardware init, DTO setup, and HBR enable/disable.
- `drivers/gpu/drm/amd/display/dc/dce/dce_audio.h` defines the common audio register, shift, and mask table shapes that resource files populate.
- `drivers/gpu/drm/amd/display/dc/dce/dce_stream_encoder.c` programs audio packet, AFMT, HDMI ACR, and DP audio behavior that must agree with the Azalia endpoint capability and status model described by these generated fields.

The direct contract is the preprocessor name and numeric bit layout. Missing or renamed macros usually fail at compile time when a generated table references them. Incorrect masks or shifts are more dangerous because the driver can still build while reading or writing the wrong hardware bits.

## Risks And Edge Cases

- The chunk starts mid-register. `AZF0INPUTENDPOINT4_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_HOT_PLUG_CONTROL` is incomplete here, with only trailing masks present in this slice. The final per-file merge must combine this with the previous chunk before making endpoint 4 completeness claims.
- Endpoint families are highly repetitive. A generator error in a single endpoint instance can be visually hard to spot while affecting only one audio engine or stream.
- Many fields are narrow bitfields packed into the same 32-bit register. Bad read/modify/write composition can alter adjacent channel, mute, validity, or enable bits.
- Full-width masks such as `STREAM_FORMATS`, `LPIB`, and `LPIB_TIMER_SNAPSHOT` require callers to preserve unsigned 32-bit behavior.
- High-bit fields such as `AUDIO_ENABLED`, `PRESENCE_DETECT`, and `INFOFRAME_VALID` use bit 31. Signed temporary types or incorrect mask constants can produce bad tests or writes.
- `MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2` encode four channels per register, each with enable, mute, and channel-ID fields. Off-by-one endpoint or channel mapping errors could silently route or mute the wrong audio channel.
- HBR capability and enable fields are adjacent but semantically different. Treating a capability readback as a control bit, or enabling HBR without matching stream-format setup, can produce audio negotiation failures.
- Hot-plug clock-gating and audio-enable fields affect hardware accessibility and link-visible behavior. The runtime audio init path explicitly disables clock gating before programming some endpoint registers; incorrect masks here can make endpoint writes unreliable.
- `UNSOLICITED_RESPONSE_FORCE` contains a 26-bit payload plus a force bit. Incorrect payload masking can generate malformed unsolicited responses to the HD Audio controller.
- LPIB snapshot locking and cyclic-buffer wrap-count fields can be timing-sensitive. Polling or snapshot code must avoid assuming static values while audio DMA progresses.
- Similar endpoint macro names exist in sibling DCN headers. Reusing DCN 3.0.2 constants for another ASIC generation is unsafe unless the generated register database confirms identical layouts.

## Test Signals

Useful validation is mostly compile-time, register-generation, and hardware smoke testing:

- Build AMDGPU Display Core with DCN 3.0.2 enabled to catch missing macro names in `dcn302_resource.c`, DCE audio table initialization, and register helper expansions.
- Preprocess the DCN 3.0.2 resource file and verify that `SF`/`SRI` expansions resolve to the intended `dcn_3_0_2_offset.h` and `dcn_3_0_2_sh_mask.h` definitions.
- Compare this slice against the upstream/generated register database and the companion offset header for endpoints 4-7, especially because endpoint 4 is split across chunks.
- Exercise HDMI and DP audio enumeration on DCN 3.0.2 hardware, checking endpoint validity, default configuration port connectivity, supported sample rates, stream formats, and pin capabilities.
- Test audio playback across common formats: 2-channel PCM, multichannel LPCM, high sample rates, and HBR-capable formats where supported.
- Validate hot-plug and suspend/resume behavior while audio is active, watching for stale `AUDIO_ENABLED`, `CLOCK_ON_STATE`, presence-detect, or input-activity state.
- Check channel allocation and infoframe readback for stereo and multichannel modes, including `INFOFRAME_VALID`.
- Exercise LPIB snapshot/readback paths if available through diagnostics, ensuring snapshot lock and timer values progress consistently.
- Run display audio tests across all exposed DCN302 audio instances, because this chunk specifically contains the higher-numbered endpoint blocks.

## Open Cross-Chunk Questions

- The final per-file report should merge the previous chunk's endpoint 4 definitions with this chunk's endpoint 4 tail.
- Whole-file reconciliation should verify how many input endpoint instances DCN 3.0.2 exposes versus how many `audio_regs[]` entries are instantiated by `dcn302_resource.c`.
- If generation provenance is available, the final report should identify the register database/import source. These numeric masks are generated hardware ABI data and should not be hand-edited without regenerating and comparing the full header.
