# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001581`: lines 1-2533, `Docs/researches/chunks/subset-b-001581_research.md`
- `subset-b-001582`: lines 2534-4917, `Docs/researches/chunks/subset-b-001582_research.md`
- `subset-b-001583`: lines 4918-7308, `Docs/researches/chunks/subset-b-001583_research.md`
- `subset-b-001584`: lines 7309-9956, `Docs/researches/chunks/subset-b-001584_research.md`
- `subset-b-001585`: lines 9957-12472, `Docs/researches/chunks/subset-b-001585_research.md`
- `subset-b-001586`: lines 12473-15001, `Docs/researches/chunks/subset-b-001586_research.md`
- `subset-b-001587`: lines 15002-17515, `Docs/researches/chunks/subset-b-001587_research.md`
- `subset-b-001588`: lines 17516-20046, `Docs/researches/chunks/subset-b-001588_research.md`
- `subset-b-001589`: lines 20047-22602, `Docs/researches/chunks/subset-b-001589_research.md`
- `subset-b-001590`: lines 22603-25075, `Docs/researches/chunks/subset-b-001590_research.md`
- `subset-b-001591`: lines 25076-27514, `Docs/researches/chunks/subset-b-001591_research.md`
- `subset-b-001592`: lines 27515-29881, `Docs/researches/chunks/subset-b-001592_research.md`
- `subset-b-001593`: lines 29882-32307, `Docs/researches/chunks/subset-b-001593_research.md`
- `subset-b-001594`: lines 32308-34753, `Docs/researches/chunks/subset-b-001594_research.md`
- `subset-b-001595`: lines 34754-37195, `Docs/researches/chunks/subset-b-001595_research.md`
- `subset-b-001596`: lines 37196-39642, `Docs/researches/chunks/subset-b-001596_research.md`
- `subset-b-001597`: lines 39643-42087, `Docs/researches/chunks/subset-b-001597_research.md`
- `subset-b-001598`: lines 42088-44705, `Docs/researches/chunks/subset-b-001598_research.md`
- `subset-b-001599`: lines 44706-47394, `Docs/researches/chunks/subset-b-001599_research.md`
- `subset-b-001600`: lines 47395-49843, `Docs/researches/chunks/subset-b-001600_research.md`
- `subset-b-001601`: lines 49844-52212, `Docs/researches/chunks/subset-b-001601_research.md`
- `subset-b-001602`: lines 52213-54345, `Docs/researches/chunks/subset-b-001602_research.md`

## Chunk Research

### subset-b-001581: lines 1-2533

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 1-2533

## Scope And Purpose

This chunk is the opening portion of AMDGPU's generated-style DCN 1.0 register shift/mask header. It starts with the license and include guard, then defines C preprocessor constants for hardware bitfields in three major display-related areas: HD Audio controller/endpoint/stream registers, VGA compatibility registers, and the beginning of DCCG display clock generator registers.

There are no functions, structs, enums, or executable control paths in this chunk. The public interface is a large set of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros. Driver code combines these constants with sibling register-address headers and MMIO helpers so it can read, update, and compose individual fields without embedding raw bit positions in C code.

## Important APIs, Types, And Macro Families

The macro namespace is the API surface. Important groups in this chunk are:

- HDA controller global state: `AZCONTROLLER0_GLOBAL_CAPABILITIES`, version, payload capability, `AZCONTROLLER0_GLOBAL_CONTROL`, wake/status, stream synchronization, interrupt control/status, wall-clock counter, and alias fields describe controller reset, flush, unsolicited responses, stream interrupt enables, and stream-level synchronization.
- HDA command and response rings: `AZCONTROLLER0_CORB_*` and `AZCONTROLLER0_RIRB_*` define lower/upper DMA base address fields, read/write pointers, reset bits, DMA enable bits, memory-error and response-overrun interrupt fields, ring size, and response interrupt counts.
- HDA immediate command paths: `AZCONTROLLER0_IMMEDIATE_COMMAND_*`, endpoint/root/input endpoint immediate command data/index fields, and matching unprefixed aliases define codec verb/payload writes, codec address selection, command busy/result valid status, and immediate response reads.
- HDA DMA position reporting: `AZCONTROLLER0_DMA_POSITION_*` and unprefixed `DMA_POSITION_*` fields define the DMA position buffer enable bit and 64-bit base address split, with low address alignment/unimplemented bits masked separately.
- HDA stream descriptors: `AZSTREAM0_0` through `AZSTREAM7_0`, then `AZSTREAM0_1` through `AZSTREAM7_1`, repeat the same output stream descriptor layout for multiple stream instances. The fields cover stream reset/run, completion/FIFO/descriptor-error interrupt enables and statuses, FIFO readiness, stream number, link position, cyclic buffer length, last valid index, FIFO size, audio format, BDL lower/upper base address, and link-position aliases.
- VGA indexed and legacy registers: `CRTC8_*`, `GENFC_*`, `GENS*`, `ATTR*`, `GENMO_*`, `SEQ8_*`, `DAC_*`, `GRPH8_*`, and `VGA_MEM_*_PAGE_ADDR` preserve masks for VGA CRTC, sequencer, graphics, attribute, DAC, memory-page, and miscellaneous control/status fields.
- VGA display integration: `VGA_RENDER_CONTROL`, `VGA_SEQUENCER_RESET_CONTROL`, `VGA_MODE_CONTROL`, surface address/pitch registers, `VGA_HDP_CONTROL`, `VGA_CACHE_CONTROL`, per-pipe `D1VGA_CONTROL` through `D6VGA_CONTROL`, status/interrupt/clear registers, `VGA_MAIN_CONTROL`, `VGA_TEST_CONTROL`, `VGA_QOS_CTRL`, and `VGA_SOURCE_SELECT` describe VGA scanout routing, memory aperture handling, cache behavior, sequencer reset effects, and interrupt/status reporting.
- DCCG clocks and resynchronization: `PHYPLL[A-G]_PIXCLK_RESYNC_CNTL`, `PIXCLK[0-2]_RESYNC_CNTL`, `REFCLK_CNTL`, `DPREFCLK_CNTL`, `MIPI_CLK_CNTL`, `DAC_CLK_ENABLE`, `DVO_CLK_ENABLE`, `SYMCLK[A-G]_CLOCK_ENABLE`, and `AOMCLK[0-2]_CNTL` expose clock enables, source selections, deep-color controls, front-end force controls, and pixel-clock resync enables.
- DCCG DTOs and counters: `DP_DTO_DBUF_EN`, `DP_DTO[0-5]_PHASE`, `DP_DTO[0-5]_MODULO`, `DCCG_DS_DTO_*`, `MIPI_DTO_*`, `DCCG_GTC_*`, `AVSYNC_COUNTER_*`, millisecond/microsecond time-base dividers, audio DTO phase/module/modulo registers, and vsync latch/counter fields describe fractional clock generation and time/counter capture.
- DCCG power, reset, and diagnostics: `DCCG_GATE_DISABLE_CNTL`, `DCCG_GATE_DISABLE_CNTL2`, clock-gating turn-on/off delay registers, `DCCG_SOFT_RESET`, `DISPCLK_FREQ_CHANGE_CNTL`, `DC_MEM_GLOBAL_PWR_REQ_CNTL`, `DCCG_PERFMON_CNTL`, `DCCG_PERFMON_CNTL2`, `DCCG_CAC_STATUS`, `DCCG_CBUS_WRCMD_DELAY`, `DCCG_DISP_CNTL_REG`, DVO skew controls, and `DCE_VERSION` expose display clock ramping, soft reset domains, performance monitor inputs, power request gating, and version/status fields.
- OTG pixel-rate control: `OTG0_PIXEL_RATE_CNTL` through `OTG5_PIXEL_RATE_CNTL`, paired `DP_DTOx_PHASE/MODULO`, and `OTGx_PHYPLL_PIXEL_RATE_CNTL` define the source, DTO enable, downspread disable, add/drop pixel, FIFO error, error count, and PLL source fields for each timing generator.

The naming convention is regular enough for AMDGPU field helper macros: a caller can extract a field with `(value & REGISTER__FIELD_MASK) >> REGISTER__FIELD__SHIFT`, or update one by clearing the mask and OR-ing `(field_value << SHIFT) & MASK`. Fields whose names end in `MASK` naturally create symbols such as `DCCG_VSYNC_CNT_INT_CTRL__DCCG_VSYNC_CNT_OTG0_LATCH_MASK_MASK`; these are generated names, not duplicate suffix mistakes.

## Control Flow And Data Flow

This header has no runtime control flow. Its data flow is compile-time macro substitution into DC, DCE, DCCG, audio, IRQ, and AMDGPU register access code.

Several hardware protocols are implied by the field layout:

- HDA controller bring-up uses reset/flush bits, capability reads, interrupt enables, CORB/RIRB base programming, pointer resets, ring-size selection, DMA enables, and polling or interrupt-driven status checks.
- HDA stream programming uses a repeated stream-descriptor sequence: stop/reset a stream, program cyclic buffer length and BDL addresses, choose format and stream number, enable interrupts, run the stream, then observe link-position, FIFO-ready, completion, FIFO-error, and descriptor-error fields.
- VGA ownership and compatibility flows read and write legacy indexed registers, switch VGA source selection, program surface addresses/pitches, adjust `VGA_VSTATUS_CNTL`, gate memory access, and clear or mask VGA access/display-switch interrupts.
- DCCG programming selects reference and symbol clock sources, enables or gates clocks, programs DTO phase/modulo values, resynchronizes pixel clocks, ramps display clock changes, handles soft resets, and observes FIFO/error/performance/counter status.
- Vsync counter and latch fields provide a capture protocol: enable the counter, choose reset/reference/trigger behavior, enable per-OTG latch capture, read latch-value registers, and clear or mask latch interrupts.

## State And Persistence Behavior

The header itself stores no state. The durable or mutable state is in hardware registers addressed elsewhere.

Important state classes represented by this chunk include:

- Controller state: HDA reset, flush, unsolicited-response enablement, wake/status bits, interrupt enables/status, stream synchronization, wall-clock counters, immediate-command busy/result state, and CORB/RIRB ring pointers.
- DMA-visible addresses: CORB, RIRB, HDA stream BDL, and DMA position-buffer base addresses are split into lower and upper registers, with low alignment bits marked as unimplemented or enable fields.
- Stream state: per-stream run/reset, format, buffer length, BDL pointer, stream number, FIFO readiness, link position, and error/completion status persist in stream descriptor registers until changed or reset.
- VGA state: legacy indexed register data, memory page selects, render/mode controls, source selection, per-display VGA enables, cache/HDP controls, interrupt mask/status/clear bits, and test/QoS settings.
- Clocking state: DCCG clock source selection, gate-disable bits, resync enablement, DTO phase/modulo values, time-base dividers, soft-reset bits, performance-monitor enables, audio DTO source selection, and OTG pixel-rate controls all affect active display timing and audio clock behavior.
- Latched status: VGA access/display-switch status, DCCG FIFO/error counts, GTC/current counters, avsync reads, vsync latch values, and vsync latch interrupts expose state that can be consumed by diagnostics, IRQ handlers, or timing code.

Because the state is hardware-backed, incorrect masks can survive until a later driver write or hardware reset and can affect scanout, audio, memory apertures, interrupts, and clock trees.

## Dependencies And Integration Points

This header is meant to be included with DCN 1.0 register address definitions from the same `include/asic_reg/dcn/` area and consumed by AMDGPU/DC register helpers. The generated constants integrate with helper conventions such as `REG_SET_FIELD`, `REG_UPDATE`, `SR(...)`, and `SF(..., mask_sh)` tables used throughout the AMD display stack.

Concrete integration points visible in the source tree include `display/dc/irq/dcn10/irq_service_dcn10.c`, which includes `dcn/dcn_1_0_sh_mask.h`, and common AMDGPU/DCE code paths that use shared field names such as `VGA_RENDER_CONTROL__VGA_VSTATUS_CNTL_MASK` and `DCCG_AUDIO_DTO_SOURCE__DCCG_AUDIO_DTO0_SOURCE_SEL`. DCE/DC audio code uses `DCCG_AUDIO_DTO_SOURCE` fields to choose audio DTO sources and 512-frame-base-rate behavior. VGA setup and handoff code uses `VGA_RENDER_CONTROL` to control VGA vstatus handling during memory/display initialization. DCCG modules for newer DCN generations follow the same mask/shift table pattern for clock-gating, audio DTO, and pixel-rate fields.

The HDA groups integrate with the GPU display audio path rather than with a normal CPU HD-audio controller driver in this tree: DC/AMDGPU code can use these definitions when programming display audio endpoints, stream DMA descriptors, codec immediate commands, and audio timing derived from DCCG DTOs.

## Risks And Edge Cases

The main risk is register-spec drift. This file is generated from ASIC register data, and consumers assume these constants exactly match DCN 1.0 hardware. A wrong shift or mask can silently write the wrong bit in a hardware register.

Specific high-risk areas in this chunk are:

- HDA DMA base address fields, where incorrect masking of unimplemented low bits or upper/lower halves can point CORB, RIRB, BDL, or position buffers at the wrong memory.
- CORB/RIRB and stream pointer/status bits, where bad reset, run, interrupt, or error masks can hang command submission, lose responses, or hide FIFO/descriptor faults.
- Repeated stream descriptor blocks, where copy/paste or generator errors between `AZSTREAMx_0` and `AZSTREAMx_1` can affect only one stream instance and be hard to detect without multi-stream audio coverage.
- VGA legacy and render controls, where an incorrect source, aperture, cache, or vstatus bit can corrupt VGA handoff, boot console behavior, suspend/resume display restoration, or legacy register access.
- DCCG clock-gating and soft-reset fields, where writing the wrong bit can gate a live clock, reset a PLL/interface, or block display/audio timing.
- DTO phase/modulo and pixel-rate fields, where programming mistakes can cause clock drift, audio/video sync faults, FIFO underflow/overflow, or timing generator errors.
- Interrupt status/clear/mask fields that share bit positions, especially in `DCCG_VSYNC_CNT_INT_CTRL`, where clear and status names intentionally map to the same bit positions.
- Chunk boundary risk: this research covers only lines 1-2533. `DCCG_VSYNC_CNT_INT_CTRL` continues past the mapped end, and the full header contains many later DCN 1.0 register groups that must be researched by later chunk documents before drawing full-file conclusions.

## Test Signals

There are no unit tests for this header alone. Useful validation is indirect:

- Build coverage for AMDGPU/DC code that includes `dcn_1_0_sh_mask.h`; this catches missing or renamed macros but not incorrect numeric values.
- Comparison against the matching AMD DCN 1.0 register database or upstream generated header to verify every `_SHIFT` and `_MASK` value.
- Display boot, modeset, suspend/resume, hotplug, and boot-console handoff tests that exercise VGA render/source/memory controls and DCCG pixel-clock programming.
- HDMI/DP audio tests that exercise HDA stream descriptor programming, CORB/RIRB command/response handling, immediate codec commands, DMA position reporting, and audio DTO source/phase/module fields.
- Interrupt tests for HDA stream completion/error, VGA access/display-switch/status clear, and DCCG vsync latch interrupt mask/clear behavior.
- Clocking diagnostics that read back DCCG gate-disable, resync, DTO, display-clock ramp, perfmon, GTC, avsync, and FIFO error/status fields under active displays.
- Multi-pipe and multi-stream coverage, because many fields are replicated per stream, per OTG, per PHYPLL, or per display pipe and a single-pipe test can miss index-specific register-definition errors.

### subset-b-001582: lines 2534-4917

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 2534-4917

## Scope

This chunk is a generated register field mask/shift slice for AMD DCN 1.0 display hardware. It does not define executable code, C types, structs, or functions. Its API surface is a large set of preprocessor constants named as:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

The constants describe bit positions and bit masks for fields in DCN 1.0 display clock, display microcontroller, power-gating, performance-monitor, interrupt, and GPU timer registers. Consumers combine these definitions with register address headers and AMD display register helper macros to build typed register tables and to perform read/modify/write operations against MMIO-backed display registers.

## Purpose

The chunk maps hardware bit layouts into compile-time constants for DCN 1.0. The nearby header prologue identifies the file as an AMD register mask header under `include/asic_reg/dcn`, guarded by `_dcn_1_0_SH_MASK_HEADER`. This range starts at the tail of DCCG vsync/test-clock definitions and continues through DCCG DFS/perfmon blocks, DMU/RBBM interface and power-gating controls, DMCU firmware/control/interrupt/mailbox fields, and the beginning of DMU IHC GPU timer start-position fields.

The main purpose is to keep display driver code out of raw numeric bit positions. Higher-level DC code can refer to symbolic names such as `DMCU_CTRL__DMCU_ENABLE_MASK`, `DCPG_INTERRUPT_CONTROL_1__DOMAIN0_POWER_UP_INT_CLEAR_MASK`, or `DC_PERFMON0_PERFCOUNTER_CNTL__PERFCOUNTER_EVENT_SEL_MASK` when programming the display engine.

## Major Register Blocks

### DCCG clock/test and DFS fields

The chunk begins with the end of `DCCG_VSYNC_CNT_INT_CTRL` and a complete `DCCG_TEST_CLK_SEL` definition. `DCCG_TEST_CLK_SEL` contains selector and invert fields for generic test clocks A and B:

- `DCCG_TEST_CLK_GENERICA_SEL`, `DCCG_TEST_CLK_GENERICA_INV`
- `DCCG_TEST_CLK_GENERICB_SEL`, `DCCG_TEST_CLK_GENERICB_INV`

The following `dce_dc_dccg_dccg_dfs_dispdec` block defines `DENTIST_DISPCLK_CNTL`, which controls display clock and DP reference clock divider changes. It exposes write/read dividers, change mode, change toggles, done toggles, and completion status fields:

- `DENTIST_DISPCLK_WDIVIDER`, `DENTIST_DISPCLK_RDIVIDER`
- `DENTIST_DISPCLK_CHG_MODE`, `DENTIST_DISPCLK_CHGTOG`, `DENTIST_DISPCLK_DONETOG`, `DENTIST_DISPCLK_CHG_DONE`
- `DENTIST_DPREFCLK_CHG_DONE`, `DENTIST_DPREFCLK_CHGTOG`, `DENTIST_DPREFCLK_DONETOG`, `DENTIST_DPREFCLK_WDIVIDER`

These fields are integration points for clock manager code that changes display clocks and waits for hardware completion bits.

### DCCG and DMU performance monitors

The DCCG blocks define `DC_PERFMON0_*` and `DC_PERFMON1_*`; the DMU block later defines `DC_PERFMON2_*`. Each perfmon instance has the same register pattern:

- `PERFCOUNTER_CNTL`: event selector, counted-value selector, increment mode, hardware-control selection, run-enable mode, count-off behavior, restart enable, interrupt enable, active bit, and counter-control selector.
- `PERFCOUNTER_CNTL2`: counted value type, hardware stop selectors, count-off selector, and control selector.
- `PERFCOUNTER_STATE`: compact state fields for counters 0 through 7.
- `PERFMON_CNTL` and `PERFMON_CNTL2`: global perfmon state, report count, count-off interrupt behavior/status/ack, clock enable, and run-enable start/stop selectors.
- `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW`: counter interrupt status/ack bits and latched counter values.

The field layout repeats across instances, which lets common perfmon helper code use register and mask tables per instance. Because `*_ACK` and `*_STATUS` bits often share related registers, users must preserve hardware write-one-to-clear semantics when acknowledging interrupts.

### PLL reserved controls

The `dce_dc_dccg_dccg_pll_dispdec` block defines `PLL_MACRO_CNTL_RESERVED0` through `PLL_MACRO_CNTL_RESERVED41`. Each register exposes a single full-width `PLL_MACRO_CNTL_RESERVED<n>` field with mask `0xFFFFFFFFL`.

These are reserved PLL macro control registers. They are not self-describing and should not be manipulated by generic code unless tied to a hardware programming sequence from the relevant ASIC specification or an existing AMD display driver path.

### DMU RBBM interface diagnostics

The `dce_dc_dmu_rbbmif_dispdec` block exposes timeout and status fields for the DMU RBBM interface:

- `RBBMIF_TIMEOUT` contains the timeout delay and request-hold fields.
- `RBBMIF_STATUS` reports timeout client decode bits.
- `RBBMIF_INT_STATUS` reports timeout operation, read/write status, ack, and mask fields.
- `RBBMIF_TIMEOUT_DIS` contains per-client timeout-disable bits for clients 0 through 29.
- `RBBMIF_STATUS_FLAG` reports RBBMIF state, read timeout, FIFO empty/full, invalid access flag/type/address.

These fields support hang diagnostics and defensive timeout masking for individual display-side RBBM clients. The `RBBMIF_TIMEOUT_ACK` field is a likely write-to-ack bit and must be handled carefully in interrupt/status code.

### DMU power gating

The `dce_dc_dmu_dc_pg_dispdec` block describes power-gating controls and status for domains 0 through 15:

- `DOMAIN<n>_PG_CONFIG` fields: `DOMAIN<n>_POWER_FORCEON` and `DOMAIN<n>_POWER_GATE`.
- `DOMAIN<n>_PG_STATUS` fields: `DOMAIN<n>_DESIRED_PWR_STATE` and `DOMAIN<n>_PGFSM_PWR_STATUS`.
- `DCPG_INTERRUPT_STATUS`: domain power-up and power-down occurred bits for all 16 domains.
- `DCPG_INTERRUPT_CONTROL_1`: mask/clear fields for domains 0 through 7.
- `DCPG_INTERRUPT_CONTROL_2`: mask/clear fields for domains 8 through 15.
- `DC_IP_REQUEST_CNTL`: `IP_REQUEST_EN`.
- `DC_PGCNTL_STATUS_REG`: present as a register marker in this chunk without field defines immediately following it.

This block is the declarative register surface for runtime display power-domain sequencing. The split between `DCPG_INTERRUPT_STATUS` and `DCPG_INTERRUPT_CONTROL_*` matters: status reports events while control registers separately mask and clear events.

### DMU miscellaneous controls

The `dce_dc_dmu_dmu_misc_dispdec` block includes:

- `CC_DC_PIPE_DIS`, a display pipe disable field.
- `DMU_CLK_CNTL`, including `DMU_DISPCLK_R_GATE_DIS`, `DMU_EDPCLK_R_GATE_DIS`, and `DMU_DISPCLK_G_GATE_DIS`.
- `DMU_MEM_PWR_CNTL`, including memory power-force and shutdown/select fields for ABM, DMCU, and DMCU IRAM.
- `DMCU_SMU_INTERRUPT_CNTL` and `SMU_INTERRUPT_CONTROL`, which expose DMCU/SMU interrupt clear, mask, and ack fields.

These fields sit at the boundary between display clock gating, display microcontroller memory power state, and SMU interrupt delivery.

### DMCU control, firmware memory, and mailbox

The `dce_dc_dmu_dmcu_dispdec` block is the largest part of this chunk. It exposes the display microcontroller control/status surface:

- `DMCU_CTRL`: reset, ignore power management, IRQ/XIRQ disable, DMCU enable, dynamic clock gating, and uC register-read timeout.
- `DMCU_STATUS`: uC reset, wait mode, and stop mode status.
- `DMCU_PC_START_ADDR`, `DMCU_FW_START_ADDR`, `DMCU_FW_END_ADDR`, `DMCU_FW_ISR_START_ADDR`: byte-split firmware address fields.
- `DMCU_FW_CS_HI` and `DMCU_FW_CS_LO`: firmware checksum halves.
- `DMCU_RAM_ACCESS_CTRL`: host access and address auto-increment controls for ERAM and IRAM.
- ERAM/IRAM read/write control and data registers: `DMCU_ERAM_WR_CTRL`, `DMCU_ERAM_WR_DATA`, `DMCU_ERAM_RD_CTRL`, `DMCU_ERAM_RD_DATA`, `DMCU_IRAM_WR_CTRL`, `DMCU_IRAM_WR_DATA`, `DMCU_IRAM_RD_CTRL`, `DMCU_IRAM_RD_DATA`.
- `DMCU_EVENT_TRIGGER`: software interrupt to uC, internal interrupt code, and generated internal interrupt to host.
- `DMCU_UC_INTERNAL_INT_STATUS`: internal microcontroller interrupt causes, including IRQ/XIRQ pins, software interrupt, illegal opcode trap, timer compare/overflow, real-time interrupt, input capture, and pulse accumulator events.
- Static-screen interrupt fields in `DMCU_SS_INTERRUPT_CNTL_STATUS`.
- `DC_DMCU_SCRATCH`, `DMCU_INT_CNT`, `DMCU_FW_CHECKSUM_SMPL_BYTE_POS`, and `DMCU_UC_CLK_GATING_CNTL`.
- Master/slave communication data, command, and control registers (`MASTER_COMM_*`, `SLAVE_COMM_*`), with byte-granular data and command fields plus interrupt/in-progress bits.

These fields are used when the host initializes or communicates with DMCU firmware, loads or inspects microcontroller memory, triggers microcontroller events, and exchanges mailbox messages. The chunk only provides layout; sequencing, polling, delays, and firmware validation live in consumers.

### DMCU interrupt routing

Several register families define interrupt status, enable, and IRQ/XIRQ selection for the DMCU:

- `DMCU_INTERRUPT_STATUS` and `DMCU_INTERRUPT_STATUS_1`: ABM1 readiness/update events, MCP/SCP/external/internal uC interrupts, uC register-read timeout, DCPG power domain events, vblank events, static-screen events, range timing updates, and generic DMCU interrupt events.
- `DMCU_INTERRUPT_TO_HOST_EN_MASK`: host-facing enable bits for ABM1, external software, uC internal, uC timeout, and static-screen interrupts.
- `DMCU_INTERRUPT_TO_UC_EN_MASK`, `DMCU_INTERRUPT_TO_UC_EN_MASK_1`: uC-facing enable bits for ABM1, MCP, static-screen, external software, DCPG domains 0-5, vblank 1-6, range timing updates, and generic interrupts.
- `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL`, `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL_1`: per-source selection between XIRQ and IRQ routing for the same interrupt classes.
- Continuation registers later in the chunk extend DCPG domain 6-15, DCCG vsync count OTG0-5, and ABM0 events through `DMCU_INTERRUPT_STATUS_CONTINUE`, `DMCU_INTERRUPT_TO_UC_EN_MASK_CONTINUE`, `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL_CONTINUE`, and `DMCU_INT_CNT_CONTINUE`.

An important pattern is that many `*_OCCURRED` and `*_CLEAR` fields share the same bit position and mask. This usually models a hardware status bit that is cleared by writing the same bit. Code using these macros must avoid blind full-register writes that could unintentionally clear unrelated pending events.

### DMCU perfmon and DPRX interrupt routing

The chunk also defines perfmon interrupt status and uC routing:

- `DMCU_PERFMON_INTERRUPT_STATUS1` through `STATUS5` report and clear perfmon counter interrupts for DMU, DIO, DCCG, HUBP0-7, HUBBUB, DPP0-7, WB0-1, DCCG perfmon2, MMHUBBUB, MPC, OPP, OPTC, and HDA.
- Matching `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK1` through `MASK5` enable those interrupt sources to the uC.
- Matching `DMCU_PERFMON_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1` through `SEL5` select XIRQ versus IRQ routing for those sources.

The DMCU DPRX section defines `DMCU_DPRX_INTERRUPT_STATUS1`, `DMCU_DPRX_INTERRUPT_TO_UC_EN_MASK1`, and `DMCU_DPRX_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1`. It covers AUX software/low-speed done events, DP fast-training-complete events, video stream disable events, HPD RX events, and HPD sense delayed events across links A through F. Like other status registers, occurrence and clear fields share masks.

### DMU IHC GPU timer start positions

The chunk ends in the `dce_dc_dmu_ihc_dispdec` block with:

- `DC_GPU_TIMER_START_POSITION_V_UPDATE`
- the beginning of `DC_GPU_TIMER_START_POSITION_VSTARTUP`

Both encode per-display-pipe D1 through D6 start-position fields in 3-bit slots at bit offsets 0, 4, 8, 12, 16, and 20. The `VSTARTUP` register continues beyond this chunk. These fields integrate with interrupt/timing code that aligns GPU timer sampling with vertical update/startup positions.

## Important API Surface

There are no callable APIs in this chunk. The important public surface is the naming and value contract of the macros. The most important macro families are:

- Clock programming: `DCCG_TEST_CLK_SEL__*`, `DENTIST_DISPCLK_CNTL__*`.
- Perfmon programming: `DC_PERFMON0_*`, `DC_PERFMON1_*`, `DC_PERFMON2_*`, `DMCU_PERFMON_INTERRUPT_*`.
- RBBMIF diagnostics: `RBBMIF_TIMEOUT__*`, `RBBMIF_INT_STATUS__*`, `RBBMIF_TIMEOUT_DIS__*`, `RBBMIF_STATUS_FLAG__*`.
- Power gating: `DOMAIN<n>_PG_CONFIG__*`, `DOMAIN<n>_PG_STATUS__*`, `DCPG_INTERRUPT_STATUS__*`, `DCPG_INTERRUPT_CONTROL_1__*`, `DCPG_INTERRUPT_CONTROL_2__*`.
- DMCU lifecycle and firmware memory: `DMCU_CTRL__*`, `DMCU_STATUS__*`, `DMCU_RAM_ACCESS_CTRL__*`, `DMCU_ERAM_*`, `DMCU_IRAM_*`, `DMCU_FW_*`.
- DMCU host/uC communication: `MASTER_COMM_*`, `SLAVE_COMM_*`, `DMCU_EVENT_TRIGGER__*`.
- Interrupt routing: `DMCU_INTERRUPT_STATUS*__*`, `DMCU_INTERRUPT_TO_HOST_EN_MASK__*`, `DMCU_INTERRUPT_TO_UC_EN_MASK*__*`, `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL*__*`, `DMCU_DPRX_INTERRUPT_*`.
- GPU timer alignment: `DC_GPU_TIMER_START_POSITION_V_UPDATE__*`, `DC_GPU_TIMER_START_POSITION_VSTARTUP__*`.

## Control Flow

The file itself has no runtime control flow. Runtime control flow is implied by how consumers should use the registers:

1. Compose bitfield values by shifting logical values by `__SHIFT` and masking with `_MASK`.
2. Program MMIO registers through AMD display register helpers.
3. Poll status or done bits for clock changes, power-gating state, DMCU reset/wait/stop state, perfmon active state, or firmware/mailbox progress.
4. Acknowledge interrupt/status bits by writing the documented clear/ack mask bits, often using the same bit positions as occurred/status bits.
5. Route interrupt sources to host, uC IRQ, or uC XIRQ by programming the matching enable and selection masks.

The chunk's repeated register families strongly suggest table-driven consumers: the same perfmon and power-domain layouts can be referenced by instance-specific register addresses and shared mask/shift lists.

## State and Persistence Behavior

All state represented here is hardware state, not software-owned persistent state:

- Clock divider, clock-gating, and DMCU enable/reset bits persist in hardware registers until modified, reset, or power-gated.
- Perfmon counters and latched values are hardware counter state. Interrupt status and ack fields may be edge/level sensitive and are subject to hardware clear semantics.
- Power-gating config and status reflect requested and finite-state-machine hardware power state for display domains.
- DMCU ERAM/IRAM and firmware address/checksum registers reflect microcontroller firmware loading and host access state.
- Master/slave communication registers behave as mailbox state shared between host and firmware.
- Interrupt enable and IRQ/XIRQ selection bits persist as routing configuration for the running display firmware/hardware session.

There is no filesystem, allocation, locking, or serialization behavior in this header. Persistence across suspend/resume or GPU reset depends on surrounding display driver save/restore and hardware reset flows.

## Dependencies and Integration Points

This header is part of the AMD GPU display register definition stack. It depends on companion register address headers for actual MMIO offsets and on AMD display helper macros that interpret `REG_FIELD`, mask/shift tables, or direct `REG_SET`/`REG_GET` style operations.

The source tree includes direct inclusion from `drivers/gpu/drm/amd/display/dc/irq/dcn10/irq_service_dcn10.c`, and many DCN1.0-style mask names are also composed into module-specific mask lists under display blocks such as MPC and DWB. Similar mask names recur in DCE and later DCN headers, so ASIC-specific code must include the correct generation header to avoid silently using a nearby but wrong bit layout.

Primary integration areas are:

- DCN 1.0 IRQ service: maps display interrupt sources to kernel interrupt handlers using these status, mask, and clear fields.
- Clock manager paths: use `DENTIST_DISPCLK_CNTL` fields to request and verify display clock divider changes.
- DMCU firmware/backlight/static-screen paths: use DMCU control, memory, event, and mailbox registers.
- Power management paths: use `DOMAIN<n>_PG_*`, `DCPG_INTERRUPT_*`, `DMU_MEM_PWR_CNTL`, and clock-gating controls.
- Perfmon/debug paths: use `DC_PERFMON*` and `DMCU_PERFMON_INTERRUPT_*` fields.
- DisplayPort/AUX/HPD interrupt paths: use `DMCU_DPRX_INTERRUPT_*` routing and status fields.

## Risks and Edge Cases

- Wrong ASIC header selection is high risk. A field name can exist across DCE/DCN generations with different meaning, width, or naming (`DPREFCLK` in this DCN 1.0 `DENTIST_DISPCLK_CNTL` block versus `DPPCLK` in some later DCN headers).
- Status and clear fields often share the same bit. Blind writes can clear events that a handler has not processed yet.
- Full-width reserved PLL fields are opaque. Treating them as normal control fields can destabilize clocks or violate undocumented hardware requirements.
- Perfmon fields include interrupt enable, active, count-off, restart, and selector bits in the same registers. Read/modify/write code must preserve unrelated selector/control bits.
- DMCU RAM host-access and auto-increment bits can affect firmware memory transfers. Enabling host access at the wrong time or using the wrong byte/word mode may corrupt firmware state.
- Interrupt routing has separate host enable, uC enable, and IRQ/XIRQ selection registers. Enabling only one side or using mismatched route selection can create lost interrupts.
- Power-gating interrupt controls split domains 0-7 and 8-15. Loops over domains must select the correct control register and bit stride.
- GPU timer start-position fields use packed 3-bit slots with one unused bit between each slot. Code must not assume dense 3-bit packing.

## Test Signals

Useful validation for changes involving this chunk:

- Build validation for DCN 1.0 display code, especially files that include `dcn/dcn_1_0_sh_mask.h`.
- Compile-time checks that mask/shift names used by DCN1.0 register lists still resolve.
- Runtime display smoke test on DCN 1.0 ASICs: modeset, vblank/VSYNC interrupts, HPD/AUX events, backlight or ABM behavior where supported, suspend/resume, and GPU reset recovery.
- Clock-change validation: display clock divider programming should complete with `DENTIST_DISPCLK_CHG_DONE`/toggle behavior and no underruns.
- Power-gating validation: domain force-on/gate transitions should report expected `DOMAIN<n>_PG_STATUS` and not leave stale `DCPG_INTERRUPT_STATUS` bits.
- DMCU validation: firmware load/checksum, reset release, host-access memory writes/reads, mailbox command completion, and internal interrupt/timeout handling.
- Perfmon validation: counters can be selected, started, read, interrupted, acknowledged, and restarted without losing unrelated counter state.
- Interrupt validation: each affected source can be masked, unmasked, routed to host or uC, and acknowledged without clearing unrelated pending sources.

### subset-b-001583: lines 4918-7308

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 4918-7308

## Scope

This chunk covers 2,391 lines from the generated DCN 1.0 register shift/mask header. It starts in the middle of `DC_GPU_TIMER_START_POSITION_VSTARTUP`, covers GPU timer read control, the display interrupt-status continuation chain, writeback converter/scaler/perfmon register fields for WB0 and WB1, and begins the MCIF writeback buffer-manager definitions for WB0/WB1. The slice ends on the `MCIF_WB1_MCIF_WB_BUF_1_ADDR_C_OFFSET` comment, so the matching shift/mask definitions for that final register are in the next chunk.

The source has no C functions, structs, or executable statements. Its exported interface is a dense set of preprocessor constants in the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` form. In this slice there are 2,160 `#define` entries, roughly split between shift constants and already-positioned masks.

## Purpose

The chunk describes bit layouts for several DCN 1.0 display hardware blocks:

- GPU timer readback and start-position selection fields for per-display timing events, including VSTARTUP, VSYNC_NOM, VREADY, FLIP, V_UPDATE_NO_LOCK, and FLIP_AWAY timing positions.
- The `DISP_INTERRUPT_STATUS` fan-out chain and `DISP_INTERRUPT_STATUS_CONTINUE*` registers, which map interrupt bits for OPTC/OTG timing events, DIG link events, HPD/AUX/DDC/I2C, DMCU/ABM, writeback scaler and MCIF writeback conditions, audio, power-gating, DCFE/DCFCLK, hub/read-client stalls, and DC perfmon conditions.
- Writeback converter (`CNV0`/`CNV1`) controls for capture enable, frame rate, cropping/window size, stereo/interlace selection, update lock/taken/pending state, source size, color-space conversion matrices, rounding offsets, clamps, CRC test readback, input pipe/source selection, soft reset, and warm-up configuration.
- Writeback scaler (`WBSCL0`/`WBSCL1`) fields for coefficient RAM access, tap programming, mode, destination size, horizontal/vertical scale ratios and filter initials, rounding/clamp, overflow and coefficient-conflict status, outside-pixel strategy, CRC testing, backpressure counters, and RAM shutdown.
- Writeback perfmon blocks (`DC_PERFMON3` and `DC_PERFMON4`) for performance counter selection, trigger/reference/clear behavior, state snapshots, counter valid/overflow/testbus mux fields, and high/low counter values.
- MCIF writeback buffer-manager fields for WB0 and the start of WB1, including buffer-manager enable/locks/interrupts, VMID and address fencing, current-line readback, current/next buffer status, luma/chroma pitch, four buffer status/status2 registers, arbitration, SCLK/watermark acknowledgment, buffer addresses and offsets, VCE control, p-state watermark/control, clock gating, warm-up, self-refresh, QoS, and luma/chroma buffer sizes.

## Important Macro Families

The GPU timer tail at lines 4918-4943 provides timer read and read-control fields. `DC_GPU_TIMER_READ` exposes a full 32-bit timer value, while `DC_GPU_TIMER_READ_CNTL` selects a read source and includes per-pipe VSYNC_NOM start-position fields. The first eight lines are a chunk-boundary continuation of `DC_GPU_TIMER_START_POSITION_VSTARTUP`; the shifts for D1-D4 appear before this slice.

The interrupt chain begins at line 4944 with `DISP_INTERRUPT_STATUS` and continues through `DISP_INTERRUPT_STATUS_CONTINUE22` at line 5748. It is structured as one root status register plus continuation registers linked by `DISP_INTERRUPT_STATUS_CONTINUE*` bits. The field groups cover:

- Pipe/timing-generator events such as `OPTCn_DATA_UNDERFLOW_INTERRUPT`, OTG immediate hardware cursor/event triggers, VSYNC_NOM, vertical interrupts, external timing sync and sync-loss.
- Link and connector events such as `DIGA`-`DIGF` fast training completion, video stream disable, HPD1-HPD6, HPD RX, AUX SW/LS done, and DDC/I2C completion.
- Display microcontroller/backlight events such as DMCU internal interrupt and ABM ready/update interrupts.
- Writeback and scaler events such as WBSCL host conflict/data overflow and MCIF writeback VCE/software/slice/overrun interrupts.
- System/display fabric events such as p-state response, power-gating response, DCFCLK watermark, DCFE and hub/read-client underflow/overflow/stall conditions, and perfmon events.

The writeback converter blocks begin at line 5861 for `CNV0` and line 6324 for `CNV1`. The two instances are parallel: each has `WB_ENABLE`, extensive `WB_EC_CONFIG` clock/memory power fields, `CNV_MODE`, window start/size, update state, source size, CSC control and matrix coefficients, clamp/rounding fields, CRC test controls/readback, input selection, soft reset, and warm-up controls.

The writeback scaler blocks begin at line 6046 for `WBSCL0` and line 6509 for `WBSCL1`. Important fields include coefficient RAM index/write enables, tap data, scaler mode and tap counts, destination dimensions, fixed-point horizontal/vertical ratios, initial phases for Y/RGB and CbCr, rounding/clamp, overflow status, coefficient RAM conflict status, outside-pixel strategy, CRC test fields, backpressure counter enable/value, and RAM shutdown control.

The perfmon blocks begin at line 6186 for `DC_PERFMON3` and line 6649 for `DC_PERFMON4`. Their counters expose enable/reset/clear/start controls, counter source selection, trigger/reference selection, counter ID, testbus mux, paired state readback, valid and overflow status, C-value interrupt fields, and high/low counter words. These are instance-specific performance monitor macros for writeback-related display paths.

The MCIF writeback section begins at line 6787 for `MCIF_WB0` and line 7092 for `MCIF_WB1`. `MCIF_WB0` is nearly complete in this slice, while `MCIF_WB1` is only partially included. Repeated buffer status registers for buffers 1-4 report active/locked/overflow/disabled/mode/buftag/next-buffer/field/current-line and long-line/short-line/frame-length errors; the companion `STATUS2` registers hold right-eye/current-line, new-content, color-depth, and Y/C overrun fields.

## APIs, Types, and Functions

There are no callable APIs, type definitions, enums, or functions in this region. The macros themselves are the hardware-facing API contract:

- `*_SHIFT` constants define the bit offset for a field within the MMIO register value.
- `*_MASK` constants define the already-shifted mask used by register helper macros to test, clear, or update a field.
- Address-block comments identify which generated register namespace the following definitions belong to, such as `dce_dc_wb0_dispdec_cnv_dispdec`, `dce_dc_wb1_dispdec_wbscl_dispdec`, and `dce_dc_mmhubbub_mcif_wb0_dispdec`.

These constants are normally paired with register offset macros from the companion DCN 1.0 offset header and with AMD display register helpers that perform read/modify/write operations.

## Control Flow

This header has no intrinsic runtime control flow. The operational flow is imposed by the display driver code that consumes the macros:

1. The caller chooses a DCN 1.0 register offset for timer, interrupt, writeback converter/scaler, perfmon, or MCIF writeback hardware.
2. The caller reads a register, prepares a value, or handles an interrupt/status readback.
3. The caller applies the appropriate `*_MASK` and `*_SHIFT` macros to isolate a field, pack a value, acknowledge an event, or preserve unrelated bits during a register update.
4. The hardware block consumes the updated state at its own synchronization point, such as a writeback update lock/taken transition, scaler coefficient load, MCIF buffer-manager lock, perfmon start/clear, or interrupt acknowledgment.

Several macro groups imply important runtime sequencing even though they do not implement it. `CNV*_CNV_UPDATE` has lock/pending/taken fields and should be coordinated with writeback programming. Coefficient RAM programming in `WBSCL*_WBSCL_COEF_RAM_SELECT` and `WBSCL*_WBSCL_COEF_RAM_TAP_DATA` requires ordered access to the selected tap pair. MCIF buffer-manager SW control has lock, interrupt enable/ack, VMID, and address fence fields that must be programmed coherently with buffer addresses and pitch/size.

## State and Persistence

The file stores no software state. It describes persistent hardware register state in DCN 1.0 display/writeback blocks. State represented by this chunk includes:

- Latched timer readback values and selected timer event positions.
- Interrupt status bits that persist until the corresponding hardware event is cleared or acknowledged by the proper status/control path.
- Writeback converter enable/mode/window/source/CSC/clamp/update state.
- Scaler coefficient RAM contents, scaling ratios, tap configuration, clamp/rounding behavior, overflow/conflict status, and CRC status.
- Perfmon counter configuration, active state, overflow/valid flags, and high/low counter values.
- MCIF writeback buffer-manager state: enabled buffers, locks held by software/VCE, current/next buffer selection, current line, buffer tags, line/frame errors, luma/chroma addresses and sizes, watermark/p-state/clock-gating controls, QoS, self-refresh, and warm-up settings.

These values persist in hardware until modified by MMIO writes, reset, mode-set teardown, power-management transitions, or firmware/hardware initialization. Status and interrupt fields may be clear-on-read, write-one-to-clear, or cleared through companion control registers depending on the underlying block; this generated header only gives bit positions and masks, not side-effect semantics.

## Dependencies and Integration Points

This chunk depends only on the C preprocessor and on inclusion in the generated DCN 1.0 ASIC register header set. It integrates with:

- Companion DCN 1.0 register offset definitions, typically `dcn_1_0_offset.h`, that provide the MMIO addresses for these masks.
- AMDGPU Display Core and DCN 1.0 resource, interrupt, timing, writeback, and hardware-sequencer code that programs the same registers through common register helper macros.
- IRQ handling code that uses `DISP_INTERRUPT_STATUS` and continuation bits to discover and service display events across multiple display pipes, link encoders, HPD/AUX/DDC paths, writeback blocks, and perfmon.
- Writeback pipeline code that configures `CNV*`, `WBSCL*`, and `MCIF_WB*` registers for display capture, scaling, color conversion, and memory writeout.
- Power-management and watermark code that consumes MCIF p-state, SCLK-change, self-refresh, and clock-gating fields.
- Diagnostic and validation paths that use CRC test registers, perfmon counters, underflow/overflow status, current-line fields, and buffer error flags.

The repeated `CNV0`/`CNV1`, `WBSCL0`/`WBSCL1`, `DC_PERFMON3`/`DC_PERFMON4`, and `MCIF_WB0`/`MCIF_WB1` naming establishes an instance mapping. Callers must not mix instance-specific offset macros with the wrong instance-specific shift/mask macros.

## Risks

The primary risk is silent hardware misprogramming. A wrong mask or shift compiles cleanly but can corrupt adjacent fields in display timing, interrupt routing, writeback memory programming, scaler coefficients, or perfmon control.

Interrupt fields are especially sensitive because this chunk contains a long chained status register map. Misinterpreting a continuation bit as a normal event, or failing to follow the chain to later `DISP_INTERRUPT_STATUS_CONTINUE*` registers, can lose interrupts. Conversely, acknowledging the wrong bit can clear unrelated display events such as HPD/AUX, OTG vertical interrupts, underflow, MCIF overrun, or perfmon status.

Writeback register programming has synchronization hazards. `CNV*_CNV_UPDATE` lock/taken/pending fields, scaler coefficient RAM selection/write-enable fields, and MCIF buffer-manager locks need ordered updates. Programming addresses, pitch, size, or CSC/scaler fields while capture is active can produce corrupted frames, memory writes to unexpected locations, line-length errors, or stale content.

MCIF fields carry memory-safety consequences. VMID, address fence, buffer address, luma/chroma offset, pitch, size, and current/next-buffer fields define where hardware writes captured frames. Incorrect values can cause writeback to target the wrong GPU virtual address range or overrun an allocated buffer.

Power-management fields can create display-visible or capture-visible failures. SCLK-change acknowledgment, p-state watermark, self-refresh, clock-gating, and RAM power state controls interact with writeback latency. Bad programming may show up as writeback underrun/overrun, corrupted captures, or stalls under clock changes.

This chunk has two merge-boundary risks: it starts mid-register at `DC_GPU_TIMER_START_POSITION_VSTARTUP`, and it ends immediately after the `MCIF_WB1_MCIF_WB_BUF_1_ADDR_C_OFFSET` comment. The reconciliation lane should merge adjacent chunks so those partial register definitions are not treated as complete standalone sections.

## Test Signals

Useful validation signals include:

- Build coverage for translation units that include `dcn_1_0_sh_mask.h`, catching duplicate names, malformed macros, or missing continuation from adjacent chunks.
- Generated-header consistency checks that every field has matching `__SHIFT` and `_MASK` constants, masks align with shifts, and repeated instance blocks (`CNV0`/`CNV1`, `WBSCL0`/`WBSCL1`, `MCIF_WB0`/`MCIF_WB1`) remain structurally consistent.
- Diff checks against AMD's authoritative DCN 1.0 register database and neighboring ASIC-generation headers for stable field layouts.
- IRQ smoke tests that trigger or emulate HPD/AUX/DDC, OTG vertical, underflow, writeback overflow, MCIF overrun, DMCU/ABM, and perfmon interrupts and verify the chained `DISP_INTERRUPT_STATUS_CONTINUE*` walk.
- Writeback functional tests that enable capture, program CNV window/source/CSC, program WBSCL ratios/coefficients, route input pipe/source selection, and verify output frames through CRC/readback or memory comparison.
- MCIF writeback tests that exercise buffer rotation across buffers 1-4, SW/VCE locks, address fencing, luma/chroma offsets, pitch/size, current-line status, overrun and line/frame error reporting.
- Power-management and watermark tests that run writeback while changing clocks/p-states and inspect `MCIF_WB*_SCLK_CHANGE`, watermark/p-state controls, and overflow/stall signals.
- Perfmon tests that start, clear, and read `DC_PERFMON3`/`DC_PERFMON4` counters, verifying valid/overflow flags and high/low counter values.

## Cross-Chunk Notes

This is a middle slice of a generated DCN 1.0 shift/mask header. The final per-file research document should merge it with the preceding GPU timer definitions and the following MCIF_WB1 address/control continuation. Treat the chunk as a register-map segment spanning display interrupts and writeback hardware, not as a standalone source module with local control flow.

### subset-b-001584: lines 7309-9956

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 7309-9956

## Purpose

This chunk is generated AMD DCN 1.0 register field metadata. It defines `_SHIFT` and `_MASK` macros for bitfields in display-core MMIO registers, pairing with `dcn_1_0_offset.h` register addresses so the DC driver can use typed register/field tables and `REG_*` helpers instead of hard-coded bit arithmetic.

The covered range starts in the middle of the `MCIF_WB1` writeback block and then spans these DCN 1.0 address blocks:

- `dce_dc_mmhubbub_mmhubbub_dispdec` and `dce_dc_mmhubbub_vgaif_dispdec`: writeback interface, VGA interface, MMHUBBUB memory power, clock gating, soft reset, write-combine, and outstanding-counter fields.
- `dce_dc_mmhubbub_mmhubbub_dcperfmon_dc_perfmon_dispdec`: DC perfmon instance 5.
- HDA/Azalia display-audio blocks: stream index/data windows for streams 0-15, endpoint and input-endpoint indirect windows, controller DMA/DTO/CRC/memory-power controls, root codec parameters, channel/power state, connectivity, and GTC offsets.
- `dce_dc_dchubbub_hubbub_sdpif_dispdec`, `ret_path`, and `hubbub`: framebuffer/aperture routing, MARC remap windows, pipe security levels, DCC return-path config, CRC values, arbitration/watermarks, VTG controls, soft reset, clocking, DCFCLK gating, and performance measurement fields.
- `dce_dc_dchubbub_dchubbub_dcperfmon_dc_perfmon_dispdec`: DC perfmon instance 7.
- `dce_dc_dcbubp0_dispdec_hubp`, `hubpreq`, `hubpret`, and `cursor`: HUBP0 surface format/tiling/viewport, request sizing, clocks, VM/page-table/protection fault registers, flip/in-use status, TTU/QoS/prefetch timing, read-line/vblank interrupts, cursor memory/address/size/position/hotspot/stereo fields, and cursor memory power.
- `dce_dc_dcbubp0_dispdec_hubp_dcperfmon_dc_perfmon_dispdec`: the beginning of DC perfmon instance 8.

There are no C functions or data objects in this range. Its purpose is to make hardware register layouts available to the rest of the DCN 1.0 display driver at compile time.

## Important APIs, Types, And Macros

The public surface is the macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted 32-bit field mask.
- Full-width address/data registers use mask `0xFFFFFFFFL`; high-address halves commonly use `0x0000FFFFL`.
- Repeated register instances preserve hardware instance names, for example `AZF0STREAM0` through `AZF0STREAM15`, `VTG0` through `VTG5`, `SURFACE_CHECK0` through `SURFACE_CHECK3`, and perfmon instances `DC_PERFMON5`, `DC_PERFMON6`, `DC_PERFMON7`, and partial `DC_PERFMON8`.

Important field families in this chunk include:

- Writeback and MMHUBBUB: `MCIF_WB1_MCIF_WB_BUF_[2-4]_ADDR_[Y/C]`, buffer offsets, VCE buffer-manager lock/interrupt fields, NB P-state watermark/control fields, client watermark, warmup pitch, self-refresh, QoS, luma/chroma buffer sizes, `WBIF[0-1]_SMU_WM_CONTROL`, `MMHUBBUB_MEM_PWR_*`, `MMHUBBUB_CLOCK_CNTL`, and `MMHUBBUB_SOFT_RESET`.
- Audio/Azalia: stream and endpoint indirect access fields, `AZ_CLOCK_CNTL`, `AZALIA_AUDIO_DTO`, DMA non-snoop/isochronous controls, CORB/RIRB/BDL controls, payload capability, CRC/input-CRC controls/results, memory power controls/status, root codec parameters, and port-connectivity overrides.
- DCHUBBUB: SDPIF framebuffer/AGP/aperture bounds, MMIO and MARC mappings, pipe security level, memory power, DCC return-path configuration per pipe, CRC values, arbitration outstanding/saturation/QoS/DRAM state, watermark sets A-D, watermark-change request/status/ack, timeout enable, global timer, surface checkers, VTG controls, soft reset, clock control, DCFCLK gate delays, and latency measurement fields.
- HUBP/HUBPREQ/HUBPRET: primary/secondary viewport and chroma viewport dimensions, surface pixel format/rotation/mirroring, address/tiling configuration, request size, VM system aperture and context0 page-table registers, primary/secondary surface and metadata addresses, flip control/interrupt/in-use state, TTU and prefetch timing, blank/nominal/vblank parameters, cursor settings, ref-to-pixel frequency ratio, read-line windows, and vblank/read-line interrupt state.
- Cursor: enable/mode/snoop/system/pitch/lines-per-chunk, cursor surface address high/low, size, screen position, hotspot, stereo offset, destination X offset, and cursor RAM power fields.
- Perfmon: control, control2, per-counter state, run-enable, count-off interrupt, counter interrupt status/ack, current value, high/low counter reads, and read select fields.

These macros are consumed through AMD DC register-list macros such as `SR`, `SRI`, `SRII`, and field-list macros such as `HWS_SF`, `HUBP_SF`, `HUBBUB_SF`, `IPP_SF`, `TF_SF`, and irq field tables. The include is visible in DCN 1.0 resource and IRQ setup, including `display/dc/resource/dcn10/dcn10_resource.c` and `display/dc/irq/dcn10/irq_service_dcn10.c`.

## Control Flow

This header has no runtime control flow. The effective flow happens at compile time and at driver initialization:

1. DCN 1.0 code includes `dcn_1_0_offset.h` for register addresses and this file for field positions.
2. Register-list macros build per-block register structures from address macros.
3. Field-list macros build per-block mask/shift structures from this file's `_SHIFT` and `_MASK` macros.
4. Runtime code uses generic register helpers to compose read-modify-write values, poll status bits, acknowledge interrupts, and unpack hardware state.

Because this chunk is a schema, every macro is an input to later generated or hand-written initialization paths. There are no local branches, loops, allocations, or calls here, but incorrect metadata directly changes register programming in the consumers.

## State And Persistence Behavior

The header itself has no mutable state and persists no software data. The state it describes is hardware state in the display engine:

- Writeback, HUBP, HUBPREQ, and DCHUBBUB address fields point display scanout/writeback traffic at VRAM/system apertures and metadata surfaces.
- Watermark, QoS, prefetch, TTU, and arbitration fields control when the memory hub asks for bandwidth, enters/exits self-refresh, or permits DRAM clock changes.
- Flip and in-use fields describe pending/current surfaces and are synchronized to display timing.
- Interrupt fields mask, clear, acknowledge, and report vblank, read-line, perfmon, and watermark-change events.
- Memory power, clock-gate, and soft-reset fields alter persistent hardware block state until another driver write or hardware reset.
- Perfmon and CRC fields accumulate hardware measurement or validation results until reset/acknowledged/reprogrammed.

These definitions do not enforce ordering. Ordering requirements live in the consumers: for example, addresses and tiling must be programmed coherently before a flip is armed, VM aperture/page-table state must match the memory manager's view, and interrupt status/ack bits must be handled according to the hardware protocol.

## Dependencies

This chunk depends on the generated DCN 1.0 register address header, `dcn_1_0_offset.h`, because masks and shifts are useful only when paired with the matching `mm...` addresses and base-index macros. It also depends on the AMD display core register helper conventions that expect exact macro names in the `<REGISTER>__<FIELD>_{SHIFT,MASK}` form.

Important code-level dependencies include:

- DCN 1.0 resource construction in `display/dc/resource/dcn10/dcn10_resource.c`, which includes this header and builds register tables for HUBP, HUBBUB, DPP/IPP, DWB, audio, timing, and IRQ services.
- DCN 1.0 IRQ service setup in `display/dc/irq/dcn10/irq_service_dcn10.c`, which includes this header to map interrupt control/status fields.
- Hardware block headers under `display/dc/dcn10/`, `display/dc/dpp/dcn10/`, `display/dc/hwss/dce/`, and related DCE/DCN components that declare the field-list macros consumed by resource setup.
- The ASIC-specific hardware contract for DCN 1.0; later DCN/DCE generations carry similar macro names but not always identical masks, shifts, or field presence.

## Integration Points

Display bring-up and mode programming use the HUBP/HUBPREQ/HUBPRET and DCHUBBUB definitions heavily. Surface programming relies on fields such as `SURFACE_PIXEL_FORMAT`, tiling mode, viewport start/dimensions, primary/secondary luma/chroma surface addresses, metadata addresses, flip control, and in-use status. Memory-system programming relies on VM aperture, page-table base/start/end, protection fault status/address, L1 TLB control, request-size, prefetch, TTU, and watermark fields.

Power and bandwidth management integrate through MMHUBBUB/DCHUBBUB and writeback fields: NB P-state controls, self-refresh, SMU watermark-change request/ack, DCHUBBUB watermark sets A-D, DRAM state controls, DCFCLK gating, MMHUBBUB/DCHUBBUB clock gating, memory-power force/disable/status, and soft reset.

Audio integration uses the Azalia register map. DTO fields configure the display audio clock ratio, stream/endpoint index-data windows expose codec/stream registers indirectly, DMA control fields select snoop/isochronous behavior, payload capability and channel-count fields advertise stream capacity, CRC fields support validation, and memory-power fields control audio SRAM blocks.

Diagnostics and validation integrate through perfmon and CRC blocks. Perfmon instances 5, 6, 7, and the start of 8 provide event selection, run control, counter state, interrupt status/ack, and 48-bit-ish high/low counter readout fields for MMHUBBUB, audio, DCHUBBUB, and HUBP-related measurement paths. DCHUBBUB and Azalia CRC controls expose frame/audio data validation signals.

Cursor and scan-position integration uses `CURSOR0_*` and `HUBPRET0_*`: cursor address, size, position, hotspot, stereo offsets, vblank/read-line windows, interrupt masks/types/clears, status, and read-line snapshots.

## Risks And Edge Cases

- This is generated hardware metadata, so small numeric errors have large blast radius. A bad mask or shift can cause register helpers to preserve the wrong bits, overwrite adjacent fields, fail to clear interrupts, or program invalid addresses.
- The chunk starts mid-`MCIF_WB1` block and ends mid-`DC_PERFMON8` block. Final file-level reconciliation must combine it with neighboring chunks before drawing conclusions about full block coverage.
- Several fields are single-bit control/status/ack fields packed near each other, especially interrupt and power-control registers. Confusing status bits with clear/ack bits can create lost interrupts or repeated interrupt storms in consumers.
- Address fields are split across low and high registers with 16-bit high masks. Consumers must keep low/high luma, chroma, and metadata addresses consistent, especially around atomic flips.
- VM and aperture fields in `HUBPREQ0_DCN_VM_*` are security- and stability-sensitive. Wrong masks can expose incorrect memory, report misleading faults, or break page-table walks.
- Repeated hardware instances invite copy/paste or generator drift. Stream, endpoint, VTG, surface-checker, watermark-set, and perfmon instances should remain structurally symmetric except where the hardware intentionally differs.
- Some names contain hardware spelling quirks, such as `PREFETCH_SETTINS`. Consumers must use the exact generated macro names; "fixing" spelling locally would break table expansion.
- Register definitions are generation-specific. Similar DCE/DCN headers nearby may define additional fields or different widths; cross-generation code must not assume these DCN 1.0 masks match later ASICs.
- Full-width masks use `L`-suffixed constants. Refactors should preserve unsigned 32-bit register semantics and avoid sign-extension surprises in helper code.

## Test Signals

Useful validation for this chunk is mostly integration and hardware-oriented:

- Build coverage for DCN 1.0 display code should compile all field-list users that include `dcn_1_0_sh_mask.h`; missing or renamed macros are caught at compile time.
- Static checks can pair every `_SHIFT` with a matching `_MASK`, verify masks fit within 32 bits, and ensure repeated instances such as `AZF0STREAM[0-15]`, endpoint/input-endpoint windows, `VTG[0-5]`, surface checkers, and perfmon blocks remain consistent.
- Register read/write helper tests or trace validation should confirm that field updates preserve unrelated bits in packed registers such as watermark-change control, clock gating, memory power, flip interrupt, HUBPRET interrupt, cursor control, and perfmon control.
- Display mode-set smoke tests should exercise scanout with primary/chroma surfaces, viewport changes, flips, cursor enable/move/disable, vblank/read-line interrupts, and power-gating transitions.
- VM fault and aperture tests should confirm HUBPREQ aperture bounds, context0 page-table programming, fault address/status reporting, and L1 TLB control behave as expected.
- Bandwidth/power tests should watch for stable watermark changes, self-refresh/DRAM-clock-change behavior, DCFCLK gating, and no underruns under stress.
- Audio tests should cover HDMI/DP audio stream setup, DTO programming, endpoint index/data access, DMA controls, payload capability, channel count, CRC result paths, and audio memory power transitions.
- Perfmon/CRC diagnostics should be able to start counters, observe active/state/status bits, acknowledge interrupts, read low/high values, and validate CRC complete/result fields without corrupting adjacent fields.

### subset-b-001585: lines 9957-12472

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 9957-12472

## Scope And Purpose

This chunk is a generated AMD DCN 1.0 register field shift/mask table. It contains no executable C logic; its purpose is to publish compile-time bitfield metadata for DCN display MMIO registers so AMDGPU display code can compose and decode register values safely.

The source path is under a local `ceph-client` mirror, but this file is AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

The chunk starts in the middle of `DC_PERFMON8_PERFMON_CNTL`: the initial lines finish interrupt-enable/status/ack shift and mask definitions whose register family began in the previous chunk. It then covers full or near-full field families for:

- `DC_PERFMON8_*` tail fields for performance monitor 8 control, counted-value interrupt/misc status, and high/low counter reads.
- HUBP/HUBPREQ/HUBPRET/CURSOR instance 1 blocks: `HUBP1_*`, `HUBPREQ1_*`, `HUBPRET1_*`, `CURSOR1_*`, plus associated `DC_PERFMON9_*`.
- HUBP/HUBPREQ/HUBPRET/CURSOR instance 2 blocks: `HUBP2_*`, `HUBPREQ2_*`, `HUBPRET2_*`, `CURSOR2_*`, plus associated `DC_PERFMON10_*`.
- HUBP/HUBPREQ/HUBPRET instance 3 blocks and the beginning of `CURSOR3_CURSOR_CONTROL`.

The chunk ends inside `CURSOR3_CURSOR_CONTROL`; only the shift fields and first two masks are in this range, while the remaining `CURSOR3` masks and registers continue in the following chunk.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or storage objects in this range. The public surface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Numeric suffixes identify repeated DCN display hub pipe instances and their local performance monitors.

Important register families in this chunk:

- `HUBP[1-3]_DCSURF_*` defines surface format, rotation, mirror, address/tiling configuration, primary/secondary luma and chroma viewport start/dimension, swath/request size, HUBP blank/disable/VTG selection, underflow status/clear, clock enables/gates/status bits, virtual-memory page size, debug data, and DCFCLK/DPPCLK measurement-window controls.
- `HUBPREQ[1-3]_DCSURF_*` defines surface pitch, primary/secondary surface addresses and high address halves, chroma variants, primary/secondary meta-surface addresses, DCC enable and 64-byte block indicators, surface update/flip locks and pending state, frame pacing, flip interrupts, current and earliest-in-use addresses, and DRQ/CRQ/MRQ/PRQ expansion modes.
- `HUBPREQ[1-3]_DCN_*` defines TTU/QoS watermarks, global TTU control, surface and cursor request-delivery timing, VM system aperture low/high/default addresses, VM context-0 protection fault defaults, page-table base/start/end addresses, protection-fault status and clear bits, page-table depth/fault interrupt/default behavior, and L1 TLB controls.
- `HUBPREQ[1-3]_*PARAMETERS*`, `*_PREFETCH*`, and `*_PER_LINE_DELIVERY*` define display-logistics timing inputs: blank offsets, destination dimensions after scaler, prefetch ratios, vblank PTE/meta group timing, nominal PTE/meta row timing, per-line delivery timing, cursor delivery adjustments, and reference-frequency-to-pixel-frequency conversion.
- `HUBPREQ[1-3]_HUBPREQ_MEM_PWR_*` defines DPTE, MPTE, and META request-memory power force/disable/fine-grain controls and status fields.
- `HUBPRET[1-3]_*` defines DET buffer base address, 3-to-2 packing disable, channel crossbar source selection, DET memory power controls/status, read-line interval/window registers, vblank/read-line interrupt mask/type/clear/status fields, current/snapshot read-line values, and inside/outside/vblank read-line status.
- `CURSOR1_*` and `CURSOR2_*` define cursor enable, mode, snoop/system, pitch, rotation/mirror bypass, lines per chunk, latency measurement, surface address/high address, size, position, hot spot, stereo offsets, destination X offset, and cursor memory power controls/status. `CURSOR3_CURSOR_CONTROL` begins the same instance-3 control layout.
- `DC_PERFMON9_*` and `DC_PERFMON10_*` mirror the performance counter/monitor layout for HUBP instances 1 and 2: event selection, counted-value selection, increment mode, hardware control/start/stop selections, count-off selection, per-counter state, monitor report count, interrupt enable/status/ack, counted-value high/low data, and read selectors.

## Control Flow

This chunk has no runtime control flow. Every meaningful line is a preprocessor definition consumed by C register-helper code.

Runtime flow exists in callers that combine these field macros with addresses from the companion offset header. Typical usage is:

1. Select a DCN display instance through register addresses and instance offsets.
2. Program HUBP surface format, viewport, request-size, VM, and TTU/QoS registers while the plane update path is locked or synchronized to vblank.
3. Program HUBPREQ surface addresses, meta addresses, DCC/tiling state, prefetch, vblank, nominal, and per-line delivery parameters computed by display-mode validation and bandwidth code.
4. Enable or disable HUBP/HUBPREQ/HUBPRET/CURSOR memory power and clocks around pipe allocation, blanking, reset, suspend/resume, or power-gating transitions.
5. Use HUBPRET read-line/vblank interrupt fields and HUBPREQ surface-flip interrupt fields to drive vblank, read-line, or page-flip event handling.
6. Read status, in-use address, fault, underflow, power-state, performance-counter, and debug fields for synchronization, diagnostics, and error recovery.

Because this header is declarative, it does not encode ordering. Consumers must provide the sequencing around update locks, pending/taken bits, interrupt clear semantics, MMU/TLB programming, memory-power transitions, and active display scanout.

## State And Persistence Behavior

The header itself stores no state and has no persistence behavior. The macros describe state held in DCN hardware registers.

The represented hardware state includes:

- Plane configuration: pixel format, rotation, mirror, tiling, viewport, luma/chroma dimensions, surface pitch, surface addresses, metadata addresses, DCC enablement, update/flip lock state, flip-pending state, frame pacing, and current/earliest in-use addresses.
- Request and timing state: swath height, chunk sizes, PTE/MPTE/meta group sizing, TTU/QoS controls, prefetch timing, vblank and nominal PTE/meta timing, per-line delivery timing, cursor delivery adjustment, reference-to-pixel-frequency ratio, and destination/blank offsets.
- VM and fault state: system aperture bounds/defaults, context-0 page-table base/start/end, protection-fault default address attributes, fault status, faulting address fragments, page-table depth, L1 TLB enablement, and fault interrupt/default controls.
- Power and clock state: HUBP clock enables/gates/status bits, request-memory power force/disable/fine-grain controls, DET memory power state, cursor memory power state, and related status fields.
- Interrupt and diagnostic state: surface flip interrupts, HUBPRET vblank/read-line interrupts, underflow status/clear bits, read-line snapshot/status bits, performance-counter state and interrupts, and debug/performance measurement windows.

Persistence is register-specific and not declared by this generated table. Some fields are control bits that remain programmed until a modeset, plane disable, power transition, reset, or later write. Others are transient or sticky status bits, read-only counters, write-one-to-clear bits, self-clearing clear/ack bits, or hardware-latched pending values. Field names such as `*_STATUS`, `*_CLEAR`, `*_ACK`, `*_PENDING`, `*_INUSE`, `*_FAULT`, `*_MEM_PWR_STATE`, and `*_INT_STATUS` hint at behavior but do not specify access type or side effects.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header convention and DCN 1.0 hardware layout. It is meaningful when paired with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h` for register addresses and base-index macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_enum.h` for symbolic field values where generated enum values exist.
- AMD display register helpers and macros that use address, shift, and mask triplets for read-modify-write operations.

Direct include users found in this source tree include DCN 1.0 resource, IRQ, and GPIO code:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn10/irq_service_dcn10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_factory_dcn10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_translate_dcn10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_translate_dcn20.c`

The practical integration points are DCN resource construction, hub pipe programming, plane address flips, cursor programming, VM aperture/page-table setup for display fetch, DCC/meta-surface setup, bandwidth and prefetch timing programming, display request QoS, memory power management, vblank/read-line/page-flip interrupt handling, underflow/fault diagnostics, and performance counter readout.

The instance numbering is important. The macro families in this chunk correspond to repeated hub pipe instances 1, 2, and 3 and their local performance-monitor instances 9 and 10. They must stay layout-compatible with the corresponding address definitions in the offset header and with repeated instance tables in DCN resource code.

## Risks And Edge Cases

- The masks and shifts are hardware ABI. A one-bit error can compile cleanly while writing the wrong MMIO field, corrupting neighboring fields, misprogramming a plane, failing to clear an interrupt, or hiding a real fault.
- This range is generated and repetitive. Copy/paste or generator drift across instances 1, 2, and 3 would be difficult to see in review because most register layouts are intentionally identical with only the instance number changed.
- Chunk boundaries split register families. `DC_PERFMON8_PERFMON_CNTL` is incomplete without the previous chunk, and `CURSOR3_CURSOR_CONTROL` is incomplete without the next chunk.
- Surface update and flip fields are sequencing-sensitive. Incorrect use of `SURFACE_UPDATE_LOCK`, `SURFACE_FLIP_PENDING`, `SURFACE_UPDATE_PENDING`, frame pacing, or in-use address status can lead to missed flips, torn updates, stuck commits, or page-flip timeout behavior.
- VM and TLB fields are high risk. Incorrect aperture, page-table, fault-default, or L1 TLB fields can turn display fetch faults into black frames, memory faults, fault storms, or security-sensitive access behavior.
- Request timing, TTU, QoS, prefetch, vblank, and nominal parameter fields must match mode validation and bandwidth calculations. Bad values can cause underflow, flicker, corruption, or power-management regressions that appear only under high memory pressure or multi-display modes.
- Interrupt fields mix mask, type, clear, occurred, and status semantics. Surface flip, vblank, and read-line paths need the correct clear polarity and ordering to avoid lost events or interrupt storms.
- Power controls operate on live display fetch memories. Forcing or disabling DPTE/MPTE/META/DET/CROB memory power at the wrong time can break scanout, cursor fetch, VM translation, or resume.
- The header does not describe access permissions. Callers must know which fields are read-only, write-one-to-clear, reserved, self-clearing, clock-gated, or only valid while a pipe is enabled.

## Test Signals

Useful validation is mostly compile-time plus hardware/display behavior:

- Build AMDGPU/DCN 1.0 display code; renamed or missing macros should be caught by resource, IRQ, GPIO, and register helper users.
- Compare generated masks/shifts against `dcn_1_0_offset.h`, adjacent chunks of `dcn_1_0_sh_mask.h`, and repeated instance families to catch instance drift or split-family omissions.
- Exercise modesets and plane commits on pipes using HUBP instances 1, 2, and 3: primary/secondary planes, luma/chroma formats, DCC-enabled surfaces, rotated or mirrored surfaces, viewport changes, and fast page flips.
- Test cursor enable/disable, movement, hot spot, stereo offset, surface-address update, and cursor memory power behavior for cursor instances 1 and 2, with instance 3 covered after merging the next chunk.
- Exercise vblank, read-line, and page-flip interrupt paths and verify that occurred/status bits set and clear without storms or lost events.
- Stress memory-pressure and bandwidth-sensitive modes: multi-display, high resolution, high refresh, scaling, DCC, chroma formats, suspend/resume, power gating, and repeated flips while monitoring for HUBP underflow or DCN VM fault status.
- Use debug and performance signals where available: HUBPREQ debug data, DCFCLK/DPPCLK measurement windows, `DC_PERFMON9/10` counters, in-use/earliest-in-use surface addresses, read-line snapshots, memory power status, and protection-fault address/status fields.

### subset-b-001586: lines 12473-15001

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 12473-15001

## Scope

This chunk covers lines 12473-15001 of the generated AMD DCN 1.0 register shift/mask header. It contains only preprocessor constants: no C functions, structs, enums, or executable logic. The slice starts inside the `CURSOR3_CURSOR_CONTROL` macro family, after its `*_SHIFT` definitions, and ends inside the `CM1_CM_DGAM_RAMB_START_CNTL_G` family; adjacent chunks are required for both complete boundary register groups.

The chunk has 2529 source lines, including 2123 `#define` lines and 382 comment/address-block lines. Its public surface is the generated register-field macro namespace consumed by DCN 1.0 display code together with `dcn_1_0_offset.h` and register helper macros.

## Purpose

The macros define bit positions and masks for DCN 1.0 display pipe hardware:

- Tail of `CURSOR3`: cursor enable/mode fields from the previous chunk plus surface address, high address, size, position, hotspot, stereo offsets, destination X offset, and cursor memory power control/status.
- `DC_PERFMON11`: HUBP/cursor-side display performance-monitor event selection, counter control, counter state, monitor state, interrupt status/ack fields, and low/high counter readback.
- DPP0 top-level control: DPP clock enables, clock gating disable bits, clock rate control, soft reset controls for CNVC/DSCL/CM blocks, CRC readback/control, and host-read setup.
- DPP0 CNVC configuration and cursor: surface pixel format, format expansion/alpha/bypass, floating-point conversion scale/bias, denormal handling, color-key controls, cursor mode/enable/expansion, cursor colors, and cursor FP scale/bias.
- DPP0 DSCL scaler: coefficient RAM selection/data, scaler mode, tap control, two-tap filtering, manual replication, horizontal/vertical luma/chroma ratios and initial phases, black offset, recout/MPC/OTG geometry, line-buffer format and memory control, autocalibration, memory power controls/status, and output-buffer control.
- DPP0 CM color management: bypass, color adjustment matrices, input CSC, gamut remap, output CSC, bias/scale, degamma and regamma LUT controls, piecewise-linear region definitions, HDR multiplier, range clamp, output rounding/truncation, denorm, memory power, and debug index/data.
- `DC_PERFMON12`: DPP0-local performance-monitor fields matching the perfmon control/readback pattern.
- DPP1 top-level, CNVC, cursor, and DSCL blocks: a second DPP instance with the same kinds of clock/reset/CRC, format, cursor, and scaler fields as DPP0.
- First part of DPP1 CM: color matrices, input CSC, gamut remap, output CSC, bias/scale, degamma LUT mode/index/data/write enable, RAMA region setup, and the beginning of RAMB start controls.

## Important Macro Families

Each generated field normally appears as:

- `REGISTER__FIELD__SHIFT` for the field bit offset.
- `REGISTER__FIELD_MASK` for the already-positioned mask.

When the hardware field itself is named `*_MASK`, the generated output uses names such as `CM0_CM_DGAM_LUT_WRITE_EN_MASK__CM_DGAM_LUT_WRITE_EN_MASK__SHIFT` and `..._MASK_MASK`. These double `MASK` names are intentional generated identifiers, not typographical errors.

The `CURSOR3_*` fields describe a hardware cursor attached to a fourth pipe/plane instance. They cover 48-bit-ish address programming through low and high address registers, dimensions, screen position, hotspot, stereo primary/secondary offsets, destination X offset, and cursor object memory power state.

The `DC_PERFMON11_*` and `DC_PERFMON12_*` blocks expose a common DC performance-monitor interface: event select, counted-value select/type, increment mode, hardware start/stop controls, count-off behavior, restart and interrupt enable, active state, packed per-counter state selectors for counters 0-7, monitor state/report count, clock enable, interrupt status/ack bits, and split low/high counter values. `DC_PERFMON11` belongs to the `dce_dc_dcbubp3_dispdec_hubp_dcperfmon_dc_perfmon_dispdec` address block, while `DC_PERFMON12` belongs to DPP0's perfmon block.

DPP top-level macros (`DPP_TOP0_*`, `DPP_TOP1_*`) are clocking, reset, CRC, and debug/control surfaces. The clock fields include enable and multiple gate-disable/rate-control bits. Soft reset bits independently reset CNVC, DSCL, and CM subblocks. CRC fields provide R/G and B/A values plus mode, window enable, continuous/region selection, and source selection controls.

`CNVC_CFG*` and `CNVC_CUR*` define the conversion path that adapts surface format and cursor pixels into the DPP pipeline. Pixel format, alpha, expansion, bypass, denormal, color key, and FP scale/bias fields are used during format setup. Cursor fields choose cursor mode, expansion, enable, two colors, and FP scale/bias.

`DSCL*` is the densest scaler family. It covers programming coefficient RAM taps and phases, selecting scaler/chroma coefficient modes, enabling two-tap hardcoded/sharp behavior, setting luma and chroma scale ratios and init phases, setting recout/MPC geometry, configuring line-buffer depth/format/dither/interleaving/memory partitioning, requesting autocalculation, and controlling scaler and output-buffer memory power.

`CM0_*` and `CM1_*` are the color-management blocks. They include matrix coefficients for COMA/COMB, input CSC, gamut remap, output CSC, bias/scale values, degamma (`DGAM`) and regamma (`RGAM`) LUT index/data/write-enable controls, RAMA/RAMB start/slope/end/region definitions for PWL LUT segments, HDR multiplier, range clamp, denorm, output format, and memory/debug controls. DPP0's CM block is complete in this chunk; DPP1's CM block is only partially covered and continues in the next chunk.

## APIs, Types, and Functions

There are no callable APIs, data types, or functions in this source range. The API-like contract is the macro namespace itself. AMDGPU display code builds register field tables from these names using macros such as `TF_SF(...)`, `TF2_SF(...)`, and `TF_REG_LIST_SH_MASK_DCN10(...)` in `display/dc/dpp/dcn10/dcn10_dpp.h`.

Observed inclusion points for `dcn_1_0_sh_mask.h` include DCN 1.0 resource construction, IRQ service setup, GPIO factory/translation code, and DPP field-table definitions. The header is paired with `dcn_1_0_offset.h`; offset macros choose the register address, while this file provides the field masks and shifts used by register read/modify/write helpers.

## Control Flow

This header has no runtime control flow. Hardware programming flow is implied by how callers consume the field macros:

1. Select a pipe instance and register family, such as `DPP_TOP0` versus `DPP_TOP1`, `DSCL0` versus `DSCL1`, `CM0` versus `CM1`, or `CURSOR3`.
2. Use the matching offset macro from `dcn_1_0_offset.h` to address the MMIO register.
3. Clear the field with `REGISTER__FIELD_MASK`, shift the value by `REGISTER__FIELD__SHIFT`, and combine it with any other fields that share the register.
4. For status and ack fields, read status bits and write documented acknowledge bits without treating all fields as ordinary read/write data.
5. For LUT and coefficient RAM programming, choose an index or tap/phase register first, then write data registers in the sequence expected by the display pipeline.

The most sequencing-sensitive implied flows are cursor address/size/position enable ordering, perfmon event selection before start/readback, DPP clock/reset transitions around subblock programming, scaler coefficient and geometry setup before enabling a plane, line-buffer memory-power handling, and CM LUT region/index/data writes.

## State and Persistence

The header stores no software state. Its constants describe persistent hardware register fields whose values remain in display-controller state until reset, power transition, firmware/hardware action, or driver writes change them.

Important state domains include cursor surface address and geometry, cursor memory power state, performance-monitor configuration and latched counter values, DPP clock/reset/CRC state, CNVC pixel-format and color-key state, DSCL scaler geometry/filter/line-buffer/memory state, and CM matrix/LUT/range-clamp/output-conversion state.

Full-width fields such as cursor surface addresses, perfmon low counters, coefficient RAM data, and debug data need normal 32-bit MMIO treatment. Narrow fields packed into shared registers require preserving unrelated and reserved bits, especially in clock control, soft reset, memory power, LUT write-enable, and interrupt/status registers.

## Dependencies and Integration Points

This chunk has no runtime dependencies beyond the C preprocessor, but it is meaningful only as generated ASIC data integrated with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h` for register addresses and base indices.
- `display/dc/dpp/dcn10/dcn10_dpp.h`, where many `DSCL0`, `CM0`, `CNVC_CFG0`, `CNVC_CUR0`, and `DPP_TOP0` fields from this chunk are assembled into DCN 1.0 DPP register masks.
- DCN 1.0 resource, IRQ, and GPIO translation code that includes the same generated offset and mask headers.
- The common AMD display register helper layer, which consumes mask/shift structures generated from these macro names.

The repeated `0` and `1` instance prefixes are important. DPP0 fields are directly represented in the DCN 1.0 DPP field lists; DPP1 fields describe the same hardware layout for the next pipe instance and must remain bit-compatible where the ASIC design is replicated.

## Risks

The main risk is silent hardware misprogramming. A wrong mask or shift still compiles, but can set the wrong bit, corrupt a neighboring field, fail to reset or enable a display subblock, select the wrong scaler mode, damage color conversion, or leave performance counters and memory-power controls in an unexpected state.

Chunk-boundary risk is real here. The slice starts after the first `CURSOR3_CURSOR_CONTROL` shift definitions and ends before the full `CM1_CM_DGAM_RAMB_*` region. The final per-file reconciliation should not describe either boundary group as complete based only on this chunk.

Generated repeated instances are copy/generation sensitive. Differences between `DPP_TOP0` and `DPP_TOP1`, `CNVC_CFG0` and `CNVC_CFG1`, `DSCL0` and `DSCL1`, or `CM0` and `CM1` may be either legitimate instance offsets in companion files or accidental field drift. Static comparison is useful because the error mode is usually hardware-visible display corruption rather than an obvious compiler failure.

Status and control bits share registers with reserved fields. Blind writes to soft reset, memory power, perfmon interrupt ack, LUT write-enable, or clock-gating registers can disrupt active pipes. Color-management LUT and PWL region fields also have ordering and bank-selection concerns: writing indices, data, region starts, slopes, and end points out of order can produce incorrect gamma/color output.

## Test Signals

Useful validation signals for this chunk are mostly build, generated-data, and hardware-display oriented:

- Build all DCN 1.0 display objects that include `dcn_1_0_sh_mask.h`, especially DPP, resource, IRQ, and GPIO translation units.
- Static generated-header checks that each `__SHIFT` has a matching mask, masks align with their shifts, masks fit in 32 bits, and duplicate macro names are absent.
- Instance-layout comparison for DPP0/DPP1, CNVC0/CNVC1, DSCL0/DSCL1, and CM0/CM1 fields that should be identical aside from register addresses.
- Regeneration or diff checks against the authoritative DCN 1.0 ASIC register database.
- Modeset smoke tests using multiple pipes to exercise DPP0 and DPP1 clocking, soft reset, format conversion, scaler programming, line-buffer setup, and cursor behavior.
- Plane scaling tests covering luma/chroma ratios, init phases, two-tap settings, coefficient RAM writes, recout/MPC geometry, and line-buffer memory configuration.
- Color pipeline tests for input CSC, gamut remap, output CSC, degamma/regamma LUT programming, PWL region setup, bias/scale, range clamp, HDR multiplier, and output rounding/truncation.
- Perfmon tests that program `DC_PERFMON11` and `DC_PERFMON12`, start/stop counting, read low/high values, and exercise interrupt status/ack paths.
- Runtime register readback around memory power/status fields for cursor, DSCL, output buffer, and CM memories after power-management transitions.

## Cross-Chunk Notes

This is an interior slice of a 54345-line generated header. Adjacent chunks should provide the beginning of `CURSOR3_CURSOR_CONTROL` before line 12473 and the continuation of `CM1_CM_DGAM_RAMB_*` plus the rest of DPP1 color-management state after line 15001.

### subset-b-001587: lines 15002-17515

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 15002-17515

## Scope

This chunk is chunk 7 of the generated AMD DCN 1.0 register shift/mask header. It covers lines 15002-17515 of `dcn_1_0_sh_mask.h`, starting in the middle of the DPP1 color-management gamma table definitions and ending at the first `DSCL3_SCL_VERT_FILTER_INIT_BOT_C` comment. The file is not executable code; it is a generated hardware register field contract made of `#define` constants named as `<register>__<field>__SHIFT` and `<register>__<field>_MASK`.

## Purpose

The chunk supplies bit positions and masks for display pipe processor register fields used by the AMD DC display driver. These constants let typed display code compose and decode memory-mapped hardware register values without hard-coding bit arithmetic at each call site.

The visible hardware areas are:

- Tail of `CM1` DPP1 color-management gamma fields, especially degamma RAM B and regamma RAM A/B piecewise-linear region programming.
- DPP1 output color controls including HDR multiplier, range clamp, denormalization, CM output mode, random seeds, and CM memory power state.
- DPP1 perf monitor block `DC_PERFMON13`.
- Full DPP2 top, CNVC format conversion, cursor, DSCL scaler, color-management, and perf monitor blocks.
- Beginning of DPP3 top, CNVC, cursor, and DSCL scaler blocks.

## Important API Surface

There are no C functions, structs, or enums in this chunk. The important API is the macro namespace consumed by register helper macros in the display driver.

Key macro families:

- `CM1_CM_DGAM_RAMB_*`: DPP1 degamma RAM B control. It defines per-channel start, start segment, linear slope, end, end slope/base, and region LUT offset/segment fields for regions 0-15.
- `CM1_CM_RGAM_*`: DPP1 regamma controls. It includes `CM_RGAM_CONTROL`, LUT index/data/write enable/status fields, and RAM A/B piecewise-linear programming. RAM A/B region tables cover regions 0-33 in packed pairs.
- `CM1_CM_HDR_MULT_COEF`, `CM1_CM_RANGE_CLAMP_CONTROL_{R,G,B}`, `CM1_CM_DENORM_CONTROL`, `CM1_CM_CMOUT_CONTROL`, `CM1_CM_MEM_PWR_{CTRL,STATUS}`: DPP1 color output and memory power fields.
- `DC_PERFMON13_*` and `DC_PERFMON14_*`: DPP performance counter selector, state, counter control, and high/low count fields for DPP1 and DPP2 perfmon instances.
- `DPP_TOP2_*` and `DPP_TOP3_*`: pipe top-level controls, soft reset, CRC values/control, and host read rate control.
- `CNVC_CFG2_*` and `CNVC_CFG3_*`: pixel format, format conversion, denormalization, color keyer thresholds, and update-pending fields.
- `CNVC_CUR2_*` and `CNVC_CUR3_*`: cursor enable/mode/min/max/color/FP scale-bias fields.
- `DSCL2_*` and `DSCL3_*`: scaler coefficient RAM, filter mode, tap counts, ratios, init phases, overscan, recout/MPC size, line-buffer format, memory power, output buffer, and autocal fields.
- `CM2_CM_*`: DPP2 color-management matrix, input gamma, input/output CSC, gamut remap, bias/scale, degamma/regamma, HDR multiplier, clamps, denorm, output, random seed, and memory power fields.

The macros integrate with display register access helpers such as `FD(reg__field)`, `REG_SET`, `REG_UPDATE`, and the DPP mask/shift list macros in `drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp.h`. The paired `dcn_1_0_offset.h` supplies register addresses; this file supplies field layout.

## Control Flow

The chunk has no runtime control flow. Its effective flow is compile-time token expansion:

1. Hardware block-specific C code includes `dcn/dcn_1_0_sh_mask.h`.
2. DPP, scaler, color-management, GPIO, IRQ, and resource code names register fields through helper macros.
3. The preprocessor resolves field names to the `__SHIFT` and `_MASK` constants from this header.
4. Register helpers use the constants to preserve unrelated bits, insert field values at the correct shift, and read masked fields back from MMIO registers.

The ordering inside the chunk mirrors hardware block ordering, not program order. Repeated groups for DPP1, DPP2, and DPP3 are intentionally similar because each display pipe has its own register instance.

## State and Persistence

This header does not hold software state and does not persist data. It describes persistent hardware register state in the display engine:

- Gamma LUT and PWL region macros describe values that remain programmed in DPP CM RAM/registers until reprogrammed, reset, or power-gated.
- `*_UPDATE_PENDING`, `*_CONFIG_STATUS`, `*_AUTOFILL_DONE`, `*_MEM_PWR_STATUS`, and perf counter state masks describe hardware status bits that driver code polls or reads.
- `*_MEM_PWR_CTRL` fields for CM, DSCL line-buffer/LUT, and OBUF memory influence power-gated hardware RAM state.
- CRC and performance monitor counters expose diagnostic hardware state used for validation and telemetry.

Because the values are register layout constants, stale or incorrect masks can corrupt hardware state even though this file itself is static.

## Dependencies and Integration Points

Direct dependencies are generated companion headers and AMD display support macros:

- `dcn_1_0_offset.h` provides `mm...` register addresses and base indices for the same register names.
- `drivers/gpu/drm/amd/display/dc/dm_services.h` defines helper patterns such as `FD(reg_field)` that concatenate field names with `__SHIFT` and masks.
- DPP headers and source under `display/dc/dpp/dcn10/` define mask/shift lists and register-field structs that consume these symbols for color, gamma, scaler, cursor, and DPP top programming.
- Resource and initialization paths such as `display/dc/resource/dcn10/dcn10_resource.c` include the DCN 1.0 register definitions when constructing hardware objects for DCN 1.0 ASICs.
- GPIO, IRQ, and other display components include the same header for their own register namespaces elsewhere in the file; this chunk is focused on DPP/CNVC/DSCL/CM/perfmon fields.

The DPP2 and DPP3 macros in this chunk follow the same naming and field-width patterns as DPP1, allowing common or instance-indexed display pipe code to use register-list macros for multiple pipe instances.

## Risks

- Bit layout drift is the main risk. Any mismatch with the ASIC register specification can cause writes to affect the wrong field, especially packed fields such as gamma region offset/segment pairs, CSC matrix coefficients, DSCL ratios, line-buffer partition controls, and memory power controls.
- Boundary risk exists because this chunk begins mid-register group at `CM1_CM_DGAM_RAMB_START_CNTL_G` and ends just before the remaining `DSCL3_SCL_VERT_FILTER_INIT_BOT_C` definitions. Merge logic must combine neighboring chunks before drawing whole-file conclusions.
- Repeated instance naming creates copy/paste risk. `CM1` versus `CM2`, `CNVC_CFG2` versus `CNVC_CFG3`, and `DSCL2` versus `DSCL3` fields are structurally similar but must map to the correct instance and offset header entries.
- Some fields are write-sensitive or status-sensitive. Misusing masks for `*_MEM_PWR_FORCE`, `*_MEM_PWR_DIS`, `*_SOFT_RESET`, `*_UPDATE_PENDING`, perfmon state, or CRC controls can hang display programming sequences or invalidate diagnostics.
- Generated header changes are hard to unit-test directly; regressions often appear as display bring-up failures, color/gamma errors, scaler artifacts, cursor problems, CRC mismatches, or power-management instability.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing:

- Build coverage for AMDGPU DCN 1.0 paths, proving every macro referenced by DPP, CM, CNVC, cursor, DSCL, perfmon, IRQ, GPIO, and resource code still resolves.
- Register programming tests or boot smoke tests on DCN 1.0 hardware that exercise plane enable, pipe reset, scaler setup, cursor enable, color conversion, gamma/degamma/regamma programming, and line-buffer allocation.
- CRC tests using `DPP_TOP{2,3}_DPP_CRC_*` and visual/color tests that detect wrong CSC, gamut remap, clamp, HDR multiplier, denorm, or gamma fields.
- Perf monitor tests that configure `DC_PERFMON13`/`DC_PERFMON14` counters and verify high/low counter reads change as expected.
- Power-management checks that toggle or inspect `CM*_CM_MEM_PWR_*`, `DSCL2_DSCL_MEM_PWR_*`, and `DSCL2_OBUF_MEM_PWR_*` without display underruns or hangs.
- Generated-header comparison against the authoritative ASIC register database, especially for packed masks, shift values above bit 16, and repeated DPP instance groups.

### subset-b-001588: lines 17516-20046

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 17516-20046

## Purpose

This chunk is part of the generated DCN 1.0 register shift/mask header for AMD display hardware. It does not implement executable logic; it defines field positions and bit masks used by the display driver register helper macros to read, write, and compose MMIO values safely for DCN 1.0 display blocks.

The assigned range starts at the tail of the `DSCL3` scaler definitions and then covers several display pipeline register blocks:

- `DSCL3` scaler/output-buffer tail fields for black offset, update state, autocalibration, overscan, OTG blanking, recout/MPC sizing, line-buffer format, line-buffer memory partitioning, memory power control/status, and OBUF control.
- `CM3` color-management fields for input/output color matrices, input degamma, degamma/regamma RAM programming, gamut remap, output CSC, bias/scale, HDR multiplier, clamps, denorm, output dither, random seeds, and CM memory power state.
- `DC_PERFMON15` and `DC_PERFMON16` display performance monitor fields.
- `MPCC0` through `MPCC3` composition fields and the common MPC configuration block for clock gating, soft reset, CRC, output muxing, stall grace, and vupdate locks.
- The beginning of `ABM0` and `ABM1` adaptive backlight management definitions, including PWM levels, ABM enable/control, ACE curve parameters, histogram/luma-stat control, sample rates, histogram bins/results, and update/read locks.

The practical purpose is to provide the bitfield metadata consumed by `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, `SF`, `SR`, and related AMD display register-list macros. For this header, correctness of every shift/mask pair is the interface contract.

## Important APIs, Types, And Functions

This header exports preprocessor constants, not functions or C types. The important "APIs" are the generated macro names:

- `*_SHIFT` constants, such as `CM3_CM_DGAM_CONTROL__CM_DGAM_LUT_MODE__SHIFT`, specify the low bit of a hardware field.
- `*_MASK` constants, such as `MPCC0_MPCC_CONTROL__MPCC_GLOBAL_ALPHA_MASK`, specify the full bitmask for that field in its 32-bit MMIO register.
- Address-block comments, such as `// addressBlock: dce_dc_dpp3_dispdec_cm_dispdec`, group the register fields by hardware block and instance.
- `DSCL3_*` fields describe the DPP3 scaler and output-buffer tail.
- `CM3_*` fields describe color-management hardware attached to DPP3.
- `DC_PERFMON15_*` and `DC_PERFMON16_*` fields describe performance counter programming and readout registers for DPP3 and MPC performance-monitor instances.
- `MPCC[0-3]_*` and `MPC_*` fields describe multi-plane composition and composition-wide configuration.
- `ABM0_*` and `ABM1_*` fields describe OPP adaptive backlight/PWM and histogram/luma-stat units.

The main consumers are the AMD display register helper layers under `drivers/gpu/drm/amd/display/dc/`. For example, `dcn10_dpp.c`, `dcn10_dpp_cm.c`, `dcn10_dpp_dscl.c`, `dcn10_cm_common.c`, and `dcn10_mpc.h` build register tables and use these masks through the `TF_SF`, `SF`, `SRI`, `SRII`, `REG_SET_*`, `REG_UPDATE_*`, and `REG_GET_*` macros.

## Control Flow

There is no runtime control flow in this header. The effective control flow appears in the generated macro expansion path:

1. DCN-specific code declares register address arrays and mask/shift tables using macros such as `SF(MPCC0_MPCC_CONTROL, MPCC_MODE, mask_sh)` or transfer-function variants for CM and DSCL fields.
2. Those macros resolve to the matching `__SHIFT` and `_MASK` constants from this file.
3. Runtime driver code calls register helpers such as `REG_SET`, `REG_SET_2`, `REG_UPDATE`, `REG_UPDATE_7`, `REG_GET`, or `REG_WAIT`.
4. The helpers use the stored mask/shift data to clear, insert, extract, or poll bitfields in 32-bit MMIO register values.

The driver-level flows represented by this chunk include:

- Scaler programming: DSCL code writes sizing, overscan, line-buffer, black-offset, and memory-power fields while setting up DPP scaling paths.
- Color pipeline programming: DPP color-management code selects gamut-remap, input/output CSC, degamma/regamma LUT mode, RAM A/B bank selection, region segmentation, and LUT data writes.
- MPC composition programming: MPC code binds DPP outputs into MPCC slots, selects top/bottom inputs, programs alpha blending/global alpha/gain, sets backgrounds, and monitors MPCC busy/stall/exception state.
- Diagnostics and validation: CRC and perfmon fields let driver/debug paths select sources, start one-shot or continuous CRCs, program event counters, read counter values, and acknowledge interrupt/status bits.
- Backlight/statistics: ABM fields program PWM levels, adaptive-brightness controls, histogram/luma-stat collection, sample-rate counters, and status/readback locks.

## State And Persistence Behavior

The header itself stores no software state and persists nothing. Its constants describe persistent hardware state in DCN MMIO registers. Writes performed using these masks persist in the display engine until another MMIO write, a display block reset, GPU reset, power-gating transition, or firmware/driver reinitialization changes the same registers.

Important state surfaces described by this range include:

- DSCL3 update state, line-buffer memory partitioning, memory-power control/status, OBUF mode, and scaler black-offset/overscan/blanking values.
- CM3 LUT mode, LUT index/data, RAM A/B region setup, gamut and CSC coefficient matrices, range clamps, dither enable/mode/depth, random seeds, and CM memory-power state.
- MPCC link state, alpha/composition modes, update-lock selection/status, background color, idle/busy indicators, stall interrupt/ack/mask, and MPCC input-check exception flags.
- MPC-wide soft reset bits, CRC source/control/result state, output mux selections, vupdate lock bits for address/config/cursor update groups, and stall grace-window duration.
- ABM0/ABM1 PWM duty/target/current values, ACE curves/thresholds, histogram/luma-stat result registers, sample-rate counters, missed-frame/read-progress bits, and lock/update-pending controls.

Several fields are explicitly lock- or latch-oriented. `*_REG_LOCK`, `*_UPDATE_PENDING`, `*_UPDATE_AT_FRAME_START`, `*_READBACK_DB_REG_VALUE_EN`, `*_IGNORE_MASTER_LOCK_EN`, `MPC_CRC_UPDATE_LOCK`, and vupdate lock fields indicate that writes may be double-buffered, frame-start-latched, or blocked by higher-level display update locking. Driver code must respect those semantics when programming live pipes.

## Dependencies

This file depends on the generated ASIC register naming convention used across the AMDGPU display stack. It is normally paired with the matching DCN 1.0 offset header, which provides register addresses, while this file provides field extraction and insertion metadata.

The key dependencies are:

- `drivers/gpu/drm/amd/display/dc/inc/reg_helper.h`, which defines the generic register access helpers that combine register addresses with these field masks and shifts.
- DCN 1.0 DPP/CM code under `drivers/gpu/drm/amd/display/dc/dpp/dcn10/`, which consumes `DSCL3_*` and `CM3_*` fields for scaler and color-management programming.
- DCN CM helper code under `drivers/gpu/drm/amd/display/dc/dcn10/`, which uses mask/shift tables for CSC and piecewise-linear gamma region programming.
- MPC code under `drivers/gpu/drm/amd/display/dc/mpc/dcn10/`, which consumes `MPCC0_*`-derived masks for all MPCC instances because repeated instances share the same field layout.
- Interrupt source definitions under `include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`, which map ABM and MPC perfmon status bits to display interrupt sources.
- DC color, plane, and stream state structures that select which gamut, CSC, gamma, scaler, composition, CRC, or ABM programming path the register helpers execute.

The generated field layout also depends on hardware-family stability: code often uses instance-zero field masks for multiple instances (`MPCC0` masks for MPCC arrays, CM0/CM3 family layouts, and repeated perfmon schemas). A mismatch between instance field layout and the chosen mask table would corrupt unrelated bits.

## Integration Points

This chunk integrates with several DCN 1.0 display subsystems:

- DPP scaler and line buffer: `dcn10_dpp_dscl.c` uses DSCL fields such as `SCL_BLACK_OFFSET`, `DSCL_MEM_PWR_CTRL`, and `DSCL_MEM_PWR_STATUS` while setting scaler state, memory power, and format-dependent offsets.
- DPP color management: `dcn10_dpp.c` and `dcn10_dpp_cm.c` read/write CM fields for input gamma, degamma, regamma, gamut remap, output CSC, and LUT RAM programming. The coefficient fields are integrated through common CSC helper structures.
- Common CM helpers: `dcn10_cm_common.c` receives register IDs plus shift/mask structures and writes packed CSC coefficients and PWL gamma-region registers. This chunk supplies many of the packed field definitions those helpers need.
- MPC/MPCC composition: `dcn10_mpc.h` and later MPC implementations use the MPCC field definitions to program top/bottom DPP selection, OPP routing, alpha blending, stereo/field mode, update locks, background color, and status checking.
- Diagnostics and debug paths: MPC CRC fields and perfmon fields are used to validate composition output, monitor hardware events, count display block events, and acknowledge counter interrupts.
- ABM/DMCU integration: ABM0/ABM1 fields correspond to adaptive backlight management and stats interrupts. The interrupt-source header maps histogram-ready, luma-stat-ready, and backlight-update events for both ABM instances.

The chunk starts in the middle of the `DSCL3_SCL_VERT_FILTER_INIT_BOT_C` register group and ends in the middle of the `ABM1` block. The per-file merge should join this research with adjacent chunks for the full DSCL3 scaler context before line 17516 and the remainder of ABM1 after line 20046.

## Risks And Edge Cases

- Off-by-one field definitions are high-impact. A wrong shift or mask can silently write the wrong hardware bits, causing bad color, bad scaling, composition corruption, missed interrupts, display underflow, stuck update locks, or unusable backlight control.
- Many registers pack two or more signed/fixed-point fields into one 32-bit value, especially CSC coefficients, LUT region endpoints, offsets, clamps, alpha/gain, and PWM/sample-rate fields. Callers must pass values preformatted for the hardware field width.
- The chunk contains repeated layouts for RAM A/B, MPCC0-3, DC_PERFMON15/16, and ABM0/1. Repetition makes generated-copy errors possible and makes reviews dependent on comparing corresponding instances for field consistency.
- Several fields are status/ack or write-one-style control surfaces, such as stall interrupts, perfcounter interrupts, missed-frame clears, and update-pending/read-progress bits. Treating them as ordinary persistent configuration fields can clear events or leave stale status.
- Update-lock fields require correct sequencing with vertical update/frame-start boundaries. Programming locked or double-buffered fields without checking pending/status bits can delay changes or apply partial state.
- Memory power fields for DSCL and CM interact with register access. Polling `*_MEM_PWR_STATUS` and sequencing force/disable fields incorrectly can produce timeouts or writes to unavailable memories.
- CRC and perfmon fields are diagnostic but can still affect interrupt behavior. Enabling counter/CRC interrupts without an ACK path can generate persistent display interrupts.
- ABM histogram and luma-stat result registers are hardware-produced data. Result reads must account for ready/read-progress/missed-frame bits and should not assume software owns the update cadence.

## Test Signals

Useful validation signals for code depending on this chunk include:

- Build-time coverage: compile DCN 1.0 display code that includes the generated offset and sh/mask headers, especially DPP, CM, DSCL, MPC, and ABM paths.
- Register helper sanity: check that `SF`/`TF_SF` entries resolve to the intended `__SHIFT` and `_MASK` fields and that no field name typo selects the wrong register family.
- Display functional tests: exercise scaling, underscan/overscan, YCbCr/RGB formats, line-buffer partitioning, and plane updates that use DSCL3 fields.
- Color tests: run degamma/regamma/gamut/CSC paths, verify LUT programming and RAM A/B selection, and compare CRC or visual output for known color transforms.
- Composition tests: enable multiple planes/cursors and alpha blending, then verify MPCC routing, background, global alpha/gain, and idle/busy/status behavior.
- CRC/perfmon diagnostics: program MPC CRC one-shot/continuous modes and perfmon counters, read high/low values, and confirm interrupt status/ack bits clear as expected.
- ABM tests: vary ambient/user/backlight levels, enable ABM, collect histogram/luma-stat results, and confirm ready/update interrupts map to the expected ABM0/ABM1 sources.
- Power-management tests: enter/exit display memory power states and confirm `DSCL_MEM_PWR_STATUS`, `CM_MEM_PWR_STATUS`, and OBUF memory state fields are polled and restored correctly.

### subset-b-001589: lines 20047-22602

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 20047-22602

## Purpose

This chunk is part of the generated AMD DCN 1.0 register shift/mask header. It contains C preprocessor constants only; there are no functions, structs, storage objects, branches, or executable algorithms in this source slice. Each register field is exposed as a bit-position macro ending in `__SHIFT` and a positioned bit mask ending in `_MASK`.

The covered hardware area is the late display pipeline and timing generator side of DCN 1.0:

- The chunk begins in the tail of the ABM1 ambient/backlight-management histogram block, with histogram bin shift-index registers, histogram result registers, and the ABM backlight master lock.
- It defines output pixel processor formatter (`FMT0` through `FMT5`) fields for clamp ranges, dynamic expansion, pixel encoding, 4:2:0/subsampling behavior, bit-depth reduction, dithering, random seeds, stereo active width, and 4:2:0 memory power control.
- It defines output pixel processor buffer (`OPPBUF0` through `OPPBUF5`) fields for active width, segmentation, overlap, pixel repetition, double-buffer pending status, and 3D timing/dummy-data parameters.
- It defines OPP pipe control and OPP pipe CRC registers for six OPP instances.
- It includes OPP top clock control and display performance monitor instance 17.
- It defines ODM/OPTC input blocks (`ODM0` through `ODM5`) for underflow status/clear, double-buffer pending, input source selection, input clock control, and spare registers.
- It defines a complete OTG0 timing-generator block and begins OTG1, ending at `OTG1_OTG_COUNT_RESET`.

The header is hardware ABI metadata for AMDGPU Display Core. Driver code combines these constants with register-address macros from `dcn_1_0_offset.h`, then uses register helpers such as `REG_UPDATE`, `REG_SET`, `REG_READ`, or lower-level MMIO helpers to program DCN display hardware.

Although the file path is under a `ceph-client` source mirror, this chunk is AMD GPU display register metadata. It does not implement Ceph filesystem behavior, distributed storage state, network protocol handling, or filesystem persistence.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The public interface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: low bit number for a field.
- `<REGISTER>__<FIELD>_MASK`: already-positioned mask for the same field.

Important macro families are:

- `ABM1_DC_ABM1_HG_BIN_*`, `ABM1_DC_ABM1_HG_RESULT_*`, and `ABM1_DC_ABM1_BL_MASTER_LOCK`: ABM1 histogram and luma-statistics readback/control fields. The chunk starts after the earlier ABM sample-rate and luma-stat blocks, so the final per-file merge needs adjacent chunk context for the full ABM1 story.
- `FMTn_FMT_CLAMP_COMPONENT_[RGB]`: per-channel lower/upper clamp values. Each register carries two 16-bit fields.
- `FMTn_FMT_DYNAMIC_EXP_CNTL`: dynamic expansion enable and mode, used when expanding lower color depths toward a wider output pipeline representation.
- `FMTn_FMT_CONTROL`: stereo override, spatial dither frame-counter behavior, pixel encoding, subsampling mode/order, Cb/Cr bit-reduction bypass, and double-buffer update-pending state.
- `FMTn_FMT_BIT_DEPTH_CONTROL`: truncation, truncation depth/mode, spatial dithering, randomization controls, temporal dithering, temporal offsets, temporal level, reset, and FRC selection fields.
- `FMTn_FMT_DITHER_RAND_[RGB]_SEED`: per-channel random seed and output offset fields for dither behavior.
- `FMTn_FMT_CLAMP_CNTL`: clamp enable and clamp color-format selection.
- `FMTn_FMT_SIDE_BY_SIDE_STEREO_CONTROL`: active width for side-by-side stereo.
- `FMTn_FMT_MAP420_MEMORY_CONTROL`: 4:2:0 mapping memory power force/disable/status fields.
- `OPPBUFn_OPPBUF_CONTROL`: active width, display segmentation, overlap pixels, pixel repetition, and double-buffer pending state.
- `OPPBUFn_OPPBUF_3D_PARAMETERS_0/1`: vertical active-space sizes plus dummy RGB data used by 3D/stereo output-buffer behavior.
- `OPP_PIPEn_OPP_PIPE_CONTROL`: OPP pipe clock enable.
- `OPP_PIPE_CRCn_OPP_PIPE_CRC_*`: CRC enable/continuous mode, stereo/interlace modes, pixel/source select, one-shot pending status, CRC mask, and result registers for A/R/G/B channels.
- `OPP_TOP_CLK_CONTROL`: OPP top-level clock force/allow/state fields.
- `DC_PERFMON17_*`: display performance monitor instance 17 fields for counter control, current-value selection, counter state, performance-monitor state, interrupt threshold/status/ack, and high/low value readback.
- `ODMn_OPTC_*`: output data merger/input-to-timing-generator fields for underflow state, source selection, input clock enable/on/gate-disable, and spare register content.
- `OTG0_OTG_*`: timing generator 0 fields for horizontal/vertical totals, blanking, sync, dynamic refresh/vertical-total controls, trigger A/B controls, force-count-now, flow control, stereo/AV sync, master enable, blanking, pipe abort, interlace, field indication, pixel readback, scanout status/counters, interrupts, double buffering, test patterns, colors, CRC windows/results, static-screen detection, 3D structure, global sync lock, global update control, dynamic refresh rate, request control, and spare register state.
- `OTG1_OTG_*`: the beginning of timing generator 1 with the same shape as OTG0 through count reset. The chunk ends before the remaining OTG1 stereo, interrupt, CRC, global sync, DRR, request, and spare fields.

Several generated macro names contain repeated words, such as `OPP_PIPE_CRC_MASK__OPP_PIPE_CRC_MASK_MASK`. That is expected: the first `MASK` is part of the hardware field name and the final `_MASK` suffix identifies the generated mask constant.

## Control Flow

This header chunk has no runtime control flow. Runtime behavior is created by caller code that uses these macros to encode and decode DCN 1.0 registers.

A typical use pattern is:

1. DCN10 resource setup includes `dcn/dcn_1_0_offset.h` and `dcn/dcn_1_0_sh_mask.h`.
2. Register-list macros in modules such as `dcn10_opp.h` and `dcn10_optc.h` select the `FMT0`, `OPPBUF0`, `OPP_PIPE0`, `OTG0`, and `ODM0` field names and instantiate per-block shift/mask tables.
3. Object constructors bind instance-specific register addresses and the shared shift/mask tables into objects such as `struct dcn10_opp` and timing generator/OPTC objects.
4. Higher-level Display Core code computes DRM modeset, stream, color, plane, vblank, CRC, stereo, and timing state.
5. Hardware-specific code writes or reads fields through helpers such as `REG_UPDATE`, `REG_UPDATE_2`, and `REG_READ`, which use the stored shift and mask values generated from this header.

Concrete local consumers illustrate this flow:

- `dcn10_opp.h` uses `OPP_SF(FMT0_FMT_BIT_DEPTH_CONTROL, ...)`, `OPP_SF(FMT0_FMT_CONTROL, ...)`, `OPP_SF(FMT0_FMT_DYNAMIC_EXP_CNTL, ...)`, `OPP_SF(FMT0_FMT_MAP420_MEMORY_CONTROL, ...)`, `OPP_SF(OPPBUF0_OPPBUF_CONTROL, ...)`, and `OPP_SF(OPP_PIPE0_OPP_PIPE_CONTROL, ...)` to build OPP shift/mask structures.
- `dcn10_opp.c` programs dynamic expansion through `FMT_DYNAMIC_EXP_CNTL`, 4:2:0 memory behavior through `FMT_MAP420_MEMORY_CONTROL`, bit-depth reduction and clamp/pixel-encoding state through FMT registers, stereo active widths through `OPPBUF_CONTROL` and `OPPBUF_3D_PARAMETERS_0`, and OPP clock enable through `OPP_PIPE_CONTROL`.
- `dcn10_optc.h` maps many `OTG0` and `ODM0` fields into timing-generator structures, including master update lock, blank control, timing totals, syncs, interlace, stereo, dynamic vertical total, triggers, scanout status, clocks, vertical interrupts, ODM underflow, global sync lock, CRC, and global update control fields.

The hardware sequencing implied by the register names is important even though it is not encoded in this file:

- Double-buffer and update-lock fields (`FMT_DOUBLE_BUFFER_REG_UPDATE_PENDING`, `OPPBUF_DOUBLE_BUFFER_PENDING`, `OTG_UPDATE_PENDING`, `OTG_MASTER_UPDATE_LOCK`, `UPDATE_LOCK_STATUS`, `OPTC_DOUBLE_BUFFER_PENDING`) imply staged state changes that latch on specific display timing boundaries.
- Clear and ack fields (`*_CLEAR`, `*_ACK`, `*_INT_CLEAR`, `OTG_PIPE_ABORT_DONE`, `OTG_TRIGA_CLEAR`, `OTG_TRIGB_CLEAR`) imply write-sensitive status handling.
- CRC fields require configuration, enable/one-shot or continuous operation, then result readback.
- Dynamic vertical total, global sync lock, force-count-now, and trigger fields require coordination with active scanout and vblank timing.

## State And Persistence Behavior

The header itself stores no state and persists nothing. The state represented by these macros lives in GPU display registers and in caller-maintained Display Core objects.

Hardware state represented in this chunk includes:

- ABM1 histogram/readback state: histogram bin shift flags/indexes, histogram results, and backlight master lock state.
- Formatter state for six OPPs: clamp lower/upper values, clamp enable/color format, pixel encoding, subsampling, Cb/Cr reduction bypass, dynamic expansion mode, truncation mode/depth, spatial/temporal dithering, random seeds, temporal FRC selection, stereo active width, and 4:2:0 memory power state.
- OPP buffer state: active width, display segmentation, overlap pixels, pixel repetition, double-buffer pending state, and 3D active-space/dummy-data parameters.
- OPP pipe state: pipe clock enable and CRC configuration/results.
- OPP top and performance monitor state: clock-force/allow/status and DC performance counter programming, thresholding, status, ack, and readback values.
- ODM/OPTC input state: selected input source, input clock state, underflow status/clear, double-buffer pending status, and spare register state.
- OTG timing state: horizontal/vertical totals, blank start/end, sync start/end, sync polarity, interlace control/status, field output, blank data color, black color, test-pattern state, scanout counters, frame counters, CRC windows/data, vertical interrupts, global sync lock, trigger configuration, dynamic vertical total limits, DRR/request behavior, and global update controls.

Persistence is hardware-specific:

- Programmed mode, color, dither, stereo, timing, CRC window, test-pattern, and global sync fields persist until rewritten, reset, or lost through display block power/reset.
- Pending and lock status fields are transient and reflect whether hardware has accepted or is waiting to latch a staged update.
- Counter, status-position, frame-count, vblank/hblank, and pixel-readback fields are live readback of current scanout state.
- Interrupt, underflow, trigger, force-count, snapshot, CRC, and performance-monitor status fields may be sticky until cleared or acknowledged.
- Memory power status for `FMT_MAP420_MEMORY_CONTROL` is a live hardware power-state readback rather than durable driver state.

Callers must distinguish ordinary configuration fields from status/clear fields. This header gives bit positions and masks, not access type, reset value, latch timing, or write-one-to-clear semantics.

## Dependencies And Integration Points

This chunk depends on the generated DCN 1.0 register contract. Its constants are meaningful only with sibling generated headers and Display Core helpers, especially:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h`, which provides matching `mm*` register addresses and base-index macros.
- Other DCN/DCE display headers that define register-list macros, field-list macros, object layouts, enum values, and helper wrappers.
- `reg_helper.h` and Display Core register access helpers that combine register addresses, masks, and shifts.
- Earlier and later sections of `dcn_1_0_sh_mask.h`, because this chunk starts in the middle of ABM1 and ends in the middle of OTG1.

Observed local include points for `dcn_1_0_sh_mask.h` include:

- `display/dc/resource/dcn10/dcn10_resource.c`, which creates DCN10 hardware object resources and includes the DCN 1.0 offset and shift/mask headers.
- `display/dc/irq/dcn10/irq_service_dcn10.c`, which needs register field metadata for DCN10 interrupt setup and handling.
- `display/dc/gpio/dcn10/hw_factory_dcn10.c` and `display/dc/gpio/dcn10/hw_translate_dcn10.c`, plus the DCN20 GPIO translator, which use shared DCN 1.0 register metadata for GPIO-related display hardware.

Primary runtime integration points are:

- OPP formatter programming: color depth reduction, dynamic expansion, 4:2:0 formatting, dithering, clamp and pixel-encoding setup, and stereo output-buffer setup.
- OPP clock and CRC programming: enabling/disabling OPP pipe clocks, selecting CRC sources, capturing CRC results, and logging/readback of OPP register state.
- Timing generator programming: DRM modeset timing totals, blanking, sync polarity, enable/disable sequencing, vblank/vertical interrupts, scanout position queries, blank data colors, test patterns, dynamic refresh, global sync lock, and master update lock.
- ODM/OPTC routing and underflow handling: selecting input sources to timing generators, controlling input clocks, observing/clearing underflow, and tracking double-buffer update state.
- Performance diagnostics: DC performance monitor 17 and OTG/OPP CRC fields for validation and debug.
- Power management and reset paths: 4:2:0 memory power controls, OPP/OTG clock controls, and state reprogramming after display reset or runtime power transitions.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These are raw preprocessor constants; a wrong shift, wrong mask, stale generated value, or mismatched offset can compile successfully while programming the wrong display bit.

Important risk areas in this chunk are:

- Repeated instance layouts. `FMT0` through `FMT5`, `OPPBUF0` through `OPPBUF5`, `OPP_PIPE_CRC0` through `OPP_PIPE_CRC5`, `ODM0` through `ODM5`, and `OTG0`/`OTG1` repeat nearly identical field names. A prefix or instance mismatch can steer writes to the wrong pipe without a type-system failure.
- Chunk boundaries. The chunk begins after the start of ABM1 histogram configuration and ends before the rest of OTG1. Whole-file conclusions must be merged with adjacent chunks to avoid missing setup or clear/readback fields.
- Update-lock and double-buffer ordering. FMT, OPPBUF, ODM/OPTC, and OTG pending/lock fields indicate timing-sensitive staged updates. Incorrect sequencing can expose partially updated timing, color, dither, stereo, segmentation, or CRC state during active scanout.
- Status/clear aliases. Fields named `CLEAR`, `ACK`, `INT_CLEAR`, or underflow/trigger clears can be write-one-to-clear or otherwise edge-sensitive. Generic read-modify-write code can accidentally clear interrupts, trigger status, underflow state, or performance monitor status if it writes back stale set bits.
- Timing-generator programming. OTG horizontal/vertical totals, sync windows, blanking windows, interlace, field polarity, disable/start points, and dynamic vertical-total min/max fields are mode-critical. Bad values can cause blank screens, unstable vblank accounting, modeset failures, or monitor link issues.
- Dynamic refresh and global sync. `OTG_V_TOTAL_CONTROL`, `OTG_DRR_CONTROL`, `OTG_GSL_*`, force-count-now, trigger, and global-control fields are synchronized with frame timing. Misconfiguration can break variable refresh, genlock/global sync, multi-display synchronization, or update lock behavior.
- Color and format precision. FMT clamp, truncation, dither, temporal FRC, dynamic expansion, pixel encoding, and 4:2:0/subsampling fields affect visible output. Off-by-one clamp ranges, wrong dither depth, wrong pixel encoding, or wrong 4:2:0 memory power/control can produce banding, color shifts, chroma artifacts, or underrun.
- Clock and power fields. OPP pipe clock, OPP top clock, OTG clock, input clock, and 4:2:0 memory power controls interact with active scanout and block availability. Disabling or forcing clocks at the wrong time can hang updates, produce underflow, or make status polling unreliable.
- CRC and debug side effects. OPP and OTG CRC, test patterns, pixel readback, DTM/test, performance monitor, and static-screen fields are useful for validation but can affect or confuse normal display output if left enabled or if windows/selectors are wrong.
- Full-width masks. Several readback/result/spare fields use `0xFFFFFFFFL`. Consumers should use existing 32-bit register helpers to avoid signedness or width surprises.

## Test Signals

Useful validation signals for code that consumes this chunk include:

- Build coverage for DCN10 display code that includes `dcn_1_0_sh_mask.h` and instantiates OPP, OPTC, IRQ, GPIO, and resource objects.
- Static generated-header checks that every `__SHIFT` has a matching `_MASK`, masks align to their shifts, and repeated instance families are consistent across `FMT0-5`, `OPPBUF0-5`, `OPP_PIPE_CRC0-5`, `ODM0-5`, and `OTG0/OTG1`.
- Diff checks against the authoritative DCN 1.0 register database and `dcn_1_0_offset.h`, especially around the ABM1 and OTG1 chunk boundaries.
- Modeset tests across common timings, blanking/sync polarities, interlaced and progressive modes, high-refresh modes, and multi-display configurations that exercise OTG totals, syncs, blanking, enable/disable, and update locks.
- Plane/stream update tests that verify pending bits drain and no partial frame is visible while changing formatter, OPP buffer, ODM, or OTG state.
- Format/color tests for RGB, YCbCr, 4:2:0, 8/10/12-bit depths, clamp ranges, dynamic expansion, truncation, spatial/temporal dithering, and FRC behavior.
- Stereo/3D tests that exercise FMT stereo override, side-by-side active width, OPPBUF 3D parameters, OTG stereo status/control, and 3D structure control.
- Vblank, vline, vertical-total, trigger, force-count-now, underflow, and performance-monitor interrupt tests that confirm status, mask, ack, and clear semantics.
- CRC validation using OPP pipe CRC and OTG CRC windows/results against known framebuffers and timing configurations.
- Power-management tests around OPP/OTG/input clocks, 4:2:0 memory power control, suspend/resume, runtime power transitions, and display block reset to ensure state is restored and polling does not hang.
- Debug/readback tests for scanout position, frame count, HV/VF counters, pixel readback, static-screen status, global sync status, and performance monitor high/low value reads.

## Cross-Chunk Notes

This source slice starts at `ABM1_DC_ABM1_HG_BIN_9_16_SHIFT_INDEX` follow-on definitions and then continues through ABM1 histogram result fields; earlier ABM1 control, sample-rate, luma-statistics, and threshold fields are outside this chunk. It ends immediately after `OTG1_OTG_COUNT_RESET`, before the rest of the OTG1 timing-generator fields. The final per-file report should reconcile this chunk with neighboring chunks before describing the complete ABM1 and OTG1 register families.

### subset-b-001590: lines 22603-25075

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 22603-25075

## Purpose

This chunk is part of AMDGPU's generated DCN 1.0 register field mask header. It contains no executable C code; it publishes preprocessor constants that describe bit positions and masks for display timing-generator registers.

The range covers the tail of `OTG1`, all visible `OTG2` and `OTG3`, and the beginning of `OTG4` inside the `dce_dc_optc_otg*_dispdec` address blocks:

- `OTG1` from count reset / force-vsync controls through stereo, snapshot, interrupt, update-lock, double-buffer, test-pattern, blank/black color, vertical interrupt, CRC, static-screen, 3D structure, global-sync, global-sync-lock, GSL, vupdate keepout, global-control, trigger/manual-flow, range timing, DRR, request, and spare-register fields.
- Complete `OTG2` and `OTG3` register-mask runs for horizontal and vertical timing, total/min/max/mid totals, trigger controls, flow control, stereo and AV sync, blanking, pipe abort, interlace, status/readback counters, snapshots, interrupts, update locking, test patterns, CRC windows/data, static-screen detection, global-swap-lock, GSL windows, DRR, request control, and spare registers.
- The start of `OTG4`, from horizontal timing through stereo control. The following chunk continues `OTG4` snapshot, interrupt, CRC, global-sync, and later timing-generator families.

Each hardware field is exposed as a pair of macros: `REGISTER__FIELD__SHIFT` gives the low bit index, and `REGISTER__FIELD_MASK` gives the already-positioned bit mask. Driver code combines these constants with matching register-address definitions from `dcn_1_0_offset.h` and the DC register helper macros that generate read/modify/write operations.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or persistent objects in this chunk. The API surface is the generated macro namespace.

The `OTG*_OTG_H_*` and `OTG*_OTG_V_*` families describe timing geometry. They include horizontal total, horizontal blank start/end, horizontal sync start/end/polarity, horizontal timing division, vertical total, vertical total min/max/mid, vertical total control, vertical blank start/end, vertical sync start/end/polarity, vstartup/vupdate/vready parameters, and nominal/status counter positions.

The trigger and flow families include `OTG_TRIGA_CNTL`, `OTG_TRIGB_CNTL`, `OTG_TRIGA_MANUAL_TRIG`, `OTG_TRIGB_MANUAL_TRIG`, `OTG_FORCE_COUNT_NOW_CNTL`, and `OTG_FLOW_CONTROL`. These masks cover trigger source selection, source pipe selection, polarity, resync bypass, input and occurrence status, edge detection mode, frequency select, delay, clear bits, manual trigger bits, force-count-now modes/checks/trigger selection/clear, and flow-control source/polarity/granularity/status.

The mode and status families include `OTG_CONTROL`, `OTG_MASTER_EN`, `OTG_BLANK_CONTROL`, `OTG_PIPE_ABORT_CONTROL`, `OTG_INTERLACE_CONTROL`, `OTG_INTERLACE_STATUS`, `OTG_FIELD_INDICATION_CONTROL`, `OTG_STATUS`, `OTG_STATUS_POSITION`, `OTG_NOM_VERT_POSITION`, `OTG_STATUS_FRAME_COUNT`, `OTG_STATUS_VF_COUNT`, `OTG_STATUS_HV_COUNT`, `OTG_COUNT_CONTROL`, `OTG_COUNT_RESET`, `OTG_MANUAL_FORCE_VSYNC_NEXT_LINE`, and `OTG_VERT_SYNC_CONTROL`. These fields expose master enable state, disable/start points, field-number behavior, blanking state/data enable, pipe abort/done, interlace current/next fields, field indication, live vblank/hblank/active/sync state, frame and counter readback, horizontal count options, frame-count reset, and forced-vsync-next-line status/clear/mode.

The stereo and snapshot families include `OTG_STEREO_FORCE_NEXT_EYE`, `OTG_AVSYNC_COUNTER`, `OTG_STEREO_STATUS`, `OTG_STEREO_CONTROL`, `OTG_SNAPSHOT_STATUS`, `OTG_SNAPSHOT_CONTROL`, `OTG_SNAPSHOT_POSITION`, and `OTG_SNAPSHOT_FRAME`. They describe stereo eye forcing, AV sync frame/line counters, active stereo eye/sync/3D state, stereo output line and polarity controls, snapshot trigger selection, snapshot position, and snapshot frame counters.

The interrupt/update families include `OTG_INTERRUPT_CONTROL`, `OTG_UPDATE_LOCK`, `OTG_DOUBLE_BUFFER_CONTROL`, `OTG_VERTICAL_INTERRUPT0_*`, `OTG_VERTICAL_INTERRUPT1_*`, `OTG_VERTICAL_INTERRUPT2_*`, `OTG_GLOBAL_SYNC_STATUS`, `OTG_MASTER_UPDATE_LOCK`, `OTG_MASTER_UPDATE_MODE`, `OTG_GSL_CONTROL`, `OTG_GSL_VSYNC_GAP`, `OTG_GSL_WINDOW_X`, `OTG_GSL_WINDOW_Y`, `OTG_VUPDATE_KEEPOUT`, and `OTG_RANGE_TIMING_INT_STATUS`. These masks cover interrupt enables/types/status/clear bits, vertical interrupt line ranges, update-lock and pending status, double-buffer update modes, vstartup/vupdate/vready and no-lock events, global swap lock enables and lock/unlock controls, GSL windowing, keepout windows, and range timing interrupt occurrence/clear/status.

The color/test/CRC families include `OTG_TEST_PATTERN_CONTROL`, `OTG_TEST_PATTERN_PARAMETERS`, `OTG_TEST_PATTERN_COLOR`, `OTG_BLANK_DATA_COLOR`, `OTG_BLANK_DATA_COLOR_EXT`, `OTG_BLACK_COLOR`, `OTG_BLACK_COLOR_EXT`, `OTG_PIXEL_DATA_READBACK0`, `OTG_PIXEL_DATA_READBACK1`, `OTG_CRC_CNTL`, `OTG_CRC0_WINDOWA_*`, `OTG_CRC0_WINDOWB_*`, `OTG_CRC0_DATA_*`, `OTG_CRC1_*`, `OTG_CRC2_DATA_*`, `OTG_CRC3_DATA_*`, `OTG_CRC_SIG_RED_GREEN_MASK`, and `OTG_CRC_SIG_BLUE_CONTROL_MASK`. These fields configure internal test patterns, blank/black color components and extension bits, pixel readback, CRC enable/selection/windowing/masking, and CRC result readback.

`OTG_STATIC_SCREEN_CONTROL`, `OTG_3D_STRUCTURE_CONTROL`, `OTG_GLOBAL_CONTROL0` through `OTG_GLOBAL_CONTROL3`, `OTG_TRIG_MANUAL_CONTROL`, `OTG_MANUAL_FLOW_CONTROL`, `OTG_DRR_CONTROL`, `OTG_REQUEST_CONTROL`, and `OTG_SPARE_REGISTER` expose display-state edge controls: static-screen detection thresholds and frame counters, 3D structure enable/state selection, global update/swap-lock and flow-control buses, manual trigger/flow outputs, dynamic refresh-rate averaging/last-used totals, immediate/request-controlled updates, and spare bits.

## Control Flow

This chunk has no runtime control flow. It is preprocessor data consumed by the DCN display driver.

A typical runtime path in the display driver is:

1. A DCN 1.0 component table selects an OPTC/OTG register address from `dcn_1_0_offset.h`, often through `SRI(OTG_..., OTG, inst)` style register-table macros.
2. The component code selects fields with `SF(OTG0_OTG_..., FIELD, mask_sh)` or equivalent generated field metadata.
3. Register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, or multi-field variants use the mask/shift values from this header to pack, clear, extract, or update fields.
4. Hardware performs the actual timing, interrupt, lock, snapshot, CRC, trigger, or double-buffer action according to DCN sequencing rules.

The control-sensitive actions represented by this chunk include programming scan timing, enabling and observing master timing state, locking updates across double-buffered registers, forcing counts or vsyncs, generating vertical interrupts, setting vstartup/vupdate/vready windows, controlling global swap lock, configuring GSL timing, enabling dynamic refresh behavior, selecting test patterns, capturing CRCs, and reading live counters. The macros do not encode ordering, read-only/write-one-to-clear semantics, valid value ranges, or synchronization requirements.

## State And Persistence Behavior

The header stores no software state. It describes state held in DCN timing-generator registers.

The represented hardware state includes:

- Latched timing-programming state, such as totals, blanking windows, sync windows, vstartup/vupdate/vready lines, test-pattern parameters, blank/black colors, stereo output settings, GSL windows, and global control buses.
- Live status and counters, such as blank/active/sync flags, current stereo eye, interlace field status, status positions, frame counts, VF/HV counts, snapshot position/frame, pixel readback, AV sync counter, trigger input/polarity/occurrence, pipe abort done, and current master enable or blank state.
- Sticky or explicitly cleared event state, such as vertical interrupt status, snapshot occurred, force-count-now occurred, force-vsync-next-line occurred, vstartup/vupdate/vready events, no-lock events, range timing events, and CRC done/overflow-like status fields.
- Double-buffer and lock state, including update-lock bits, update-pending bits, global update lock behavior, master update lock, and update request modes.
- Diagnostic state, including CRC window selections and masks, CRC result registers, static-screen counters/events, and spare/debug-style fields.

Persistence is hardware-defined. Values may survive within an enabled display engine until modeset, power-gating, suspend/resume, ASIC reset, or driver reprogramming. Some bits are live read-only status, some are writable programming fields, some are sticky clear-on-write fields, and some may self-clear after a trigger. This generated header does not distinguish those classes.

## Dependencies And Integration Points

This chunk depends on the generated DCN 1.0 register-header set. `dcn_1_0_sh_mask.h` supplies bit layouts; `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h` supplies the matching register addresses.

Direct local include points for the DCN 1.0 offset and mask headers include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn10/irq_service_dcn10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_factory_dcn10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_translate_dcn10.c`

The OTG field names also integrate with the OPTC implementation under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/`, especially the DCN timing-generator register and mask structures defined around `dcn10_optc.h`. Later DCN generations reuse many of the same logical field names, so the correctness of this generated DCN 1.0 mask header matters to common helper code that is parameterized by per-generation register tables.

Although the repository path is under a local `ceph-client` source tree, this file is AMDGPU display-controller hardware metadata. It has no Ceph protocol, filesystem, or distributed-storage behavior.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A wrong shift or mask can compile and still update the wrong bits, fail to update intended bits, or corrupt adjacent fields during read/modify/write operations.

High-risk fields in this chunk include timing totals and blank/sync windows, vertical total min/max/mid/control fields used for variable refresh and dynamic refresh behavior, update-lock and double-buffer pending fields, master enable and pipe abort fields, global sync and GSL lock fields, vertical interrupt enables/status/clear bits, vstartup/vupdate/vready events, trigger source and clear bits, and CRC/test-pattern fields. Errors here can produce blank displays, flicker, wrong refresh timing, missed interrupts, stuck update locks, failed multi-pipe synchronization, bad VRR/DRR behavior, incorrect CRC diagnostics, or modeset hangs.

Repeated instance layouts create copy-generation risk. `OTG2` and `OTG3` are complete, nearly identical register-mask sequences; `OTG1` and `OTG4` are partial because of chunk boundaries. An instance suffix mismatch or one-off mask difference could affect only a specific timing generator and might not appear on systems using fewer pipes.

Several masks describe status, event-clear, or trigger fields, but the header does not indicate access type. Consumers must know which fields are read-only, write-one-to-clear, self-clearing, or latch-on-update from hardware documentation and DCN sequencing code. Treating status bits like writable state, or clearing an event while enabling an interrupt, can lose display timing events.

This chunk starts immediately after earlier `OTG1` status/readback definitions and ends in the middle of the `OTG4_STEREO_CONTROL` block boundary transition to later `OTG4` snapshot/interrupt definitions. The final merged per-file research should treat those as chunk boundaries, not as missing register definitions.

## Test Signals

Useful validation signals are compile-time generated-header checks plus display hardware behavior:

- Kernel or AMDGPU display builds should compile all DCN 1.0 IRQ, resource, GPIO, and OPTC users of the generated `OTG*_...` field names.
- Register-generation validation should compare every `*_MASK` and `*__SHIFT` pair in this chunk against AMD's source register database and the corresponding `dcn_1_0_offset.h` addresses.
- Modeset tests should exercise multiple DCN timing generators, especially OTG2 and OTG3, to catch instance-specific copy errors.
- Display timing tests should verify horizontal/vertical totals, blanking, sync polarity, interlace, frame counters, and live status transitions across common modes.
- VRR/DRR and vtotal-min/max tests should observe stable `OTG_DRR_CONTROL` and vertical total behavior without flicker or invalid refresh jumps.
- IRQ tests should validate vstartup, vupdate, vready, vertical interrupt, snapshot, force-count-now, force-vsync, GSL-vsync-gap, and range-timing interrupt enable/status/clear behavior.
- Multi-pipe and synchronized update tests should exercise update locks, double-buffer pending state, master update lock, global swap lock, GSL windows, and global control fields.
- CRC and test-pattern tests should verify CRC window selection, masks, result registers, static-screen detection, blank/black color programming, and test-pattern output.
- Suspend/resume, hotplug, runtime power-management, and repeated modeset stress should not leave update locks stuck, timing generators disabled unexpectedly, or event status bits uncleared.

Regression symptoms from bad constants include blank or unstable displays, wrong refresh rate, tearing during atomic updates, missed vblank/vupdate interrupts, VRR failures, display CRC mismatches, test-pattern errors, stuck global sync, pipe abort timeouts, stereo/interlace field errors, and problems isolated to one OTG instance.

## Cross-Chunk Notes

Earlier chunks define the beginning of the DCN 1.0 header and the preceding OTG0/OTG1 timing-generator fields. This chunk begins at the tail of `OTG1` and contains complete `OTG2` and `OTG3` runs. The next chunk continues from `OTG4_OTG_STEREO_CONTROL` into the rest of `OTG4` and later register families. The final per-file merge should describe the whole header as a generated hardware register layout contract, not as algorithmic code.

### subset-b-001591: lines 25076-27514

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 25076-27514

## Scope

This chunk covers lines 25076-27514 of the generated-style AMD DCN 1.0 register shift/mask header. It contains only C preprocessor constants: no functions, structs, enums, inline helpers, or executable control flow. The chunk starts inside the `OTG4_OTG_STEREO_CONTROL` macro family and ends after `DIO_CLK_CNTL` masks, just before `DIO_POWER_MANAGEMENT_CNTL`.

The slice contains 2439 source lines and 2157 `#define` lines. Its exported surface is a set of globally visible `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros used with companion DCN 1.0 register offset headers and AMDGPU display MMIO/indexed-register helpers.

## Purpose

The macros describe bit positions and already-positioned masks for several DCN 1.0 display controller blocks:

- Tail of OPTC/OTG instance 4: stereo control, snapshot capture, timing interrupts, double-buffer/update control, test patterns, blank/black colors, CRC windows and signatures, static-screen detection, 3D structure control, global sync lock, vertical update windows, dynamic refresh-rate control, manual triggers, request control, and spare register fields.
- Full OPTC/OTG instance 5: horizontal and vertical timing totals, blanking/sync positions, trigger A/B controls, force-count and force-vsync controls, flow control, AV sync counter, blanking and pipe abort controls, interlace and field state, pixel readback, current position/frame counters, stereo state/control, snapshot controls, interrupt controls, update locks, test patterns, colors, CRC, static-screen, global sync, vertical update keepout, global control, DRR, request, and spare fields.
- OPTC misc and performance monitor blocks: DWB/GSL source selection, OPTC clock-control/spare fields, and `DC_PERFMON18` perf counter/perfmon selection, state, interrupt, and counter-value fields.
- DIO DAC block: DAC enable/source selection, DAC CRC configuration and readback, sync tristate/stereosync selection, autodetect control/status/interrupt fields, forced output/data fields, powerdown/control/comparator fields, DFT config, and FIFO status.
- DIO I2C and generic I2C blocks: display DDC engine control, arbitration, interrupt, software/hardware status, per-DDC speed/setup, transaction descriptors, data FIFO/index fields, EDID detect, read-request interrupt, generic I2C control/status/speed/setup/transaction/data/pin-selection.
- DIO misc block: scratch registers, VCE audio stream select, DIO memory power status/control for I2C/DP/HDMI/AFMT memories, and DIO clock gating controls for DIO, DVO, DACA, reference clock, and DIGA-DIGG.

## Important Macro Families

All field constants follow the generated naming convention:

- `REGISTER__FIELD__SHIFT` gives the bit offset.
- `REGISTER__FIELD_MASK` gives the field mask in final register position.
- Fields whose hardware names end in `MASK` generate names like `OTG5_OTG_CRC_SIG_RED_GREEN_MASK__OTG_CRC_SIG_RED_MASK__SHIFT` and `..._MASK_MASK`; this double `MASK` form is intentional generated output, not a typo.

The `OTG4_*` portion continues an instance already opened before this range. It focuses on late timing-generator controls: snapshots, interrupt masks/types, update locks, double-buffer update-pending bits, test-pattern generation, blank and black color programming, vertical interrupts, CRC control/windows/data/signature masks, static-screen detection, 3D stereo structure, global sync lock, vertical startup/update/ready timing, global control, manual trigger/flow control, range timing interrupt status, dynamic refresh rate, and request controls.

`OTG5_*` mirrors the OPTC/OTG timing-generator layout for the next instance. It includes the primary modeset timing fields (`H_TOTAL`, `H_BLANK_START/END`, `H_SYNC_A`, `V_TOTAL`, `V_TOTAL_MIN/MAX/MID`, `V_BLANK`, `V_SYNC_A`), runtime status fields (`OTG_STATUS`, position counters, frame counters, HV count, nominal vertical position), trigger and force-count controls, update/double-buffering controls, color/test-pattern/CRC diagnostics, stereo and interlace state, global sync controls, vertical update keepout, DRR control, and request generation.

The OPTC misc/perfmon section exposes source muxes for DWB and GSL, clock gating for the OPTC block, a spare register, and a full `DC_PERFMON18` counter set. The perfmon macros select events and counted-value inputs, control increment mode and restart/count-off behavior, report active state and interrupt latches, select stop conditions, and read low/high counter values.

The DAC macros describe the legacy analog-output path. They cover enable and source selection, RGB/control CRC masking and readback, sync tristate and stereosync, load/autodetect control with threshold and sense fields, autodetect interrupt enable/status/ack/type, forced blank/sync/data outputs, powerdown controls, comparator enable/output, DAC power controls, DFT bits, and FIFO overflow/underflow flags.

The I2C macros define both the DC DDC hardware engines and a generic I2C controller. They include soft reset, go/send-reset, transaction count, DDC selection, arbitration, interrupt enable/status/ack/type, software status, DDC1-DDC6 and VGA hardware status, per-channel reference-divider/threshold/prescale/setup limits, transaction direction/start/stop/stop-on-NACK/count fields, data read/write and index fields, EDID-detect configuration, read-request interrupts, and generic SCL/SDA pin selection.

The DIO misc macros expose software scratch space, VCE audio stream select, memory power state/control for I2C, DP links A-G, HDMI instances 0-6, AFMT instances 0-5, and clock gate disable bits for display, reference, DVO, DAC, and DIG links.

## APIs, Types, and Functions

There are no callable APIs, C types, or functions in this chunk. The macros form a low-level ABI-like contract between generated ASIC register data and hand-written AMDGPU display code.

The header is included by DCN 1.0 resource setup, DCN 1.0 IRQ service, DCN 1.0 GPIO factory/translation code, and DCN 2.0 GPIO translation code. Fields in this chunk are also consumed indirectly through shared DCE helper structures and macros, especially I2C and DAC helpers such as `dce_i2c_hw` and `dce_link_encoder`. Callers pair these mask/shift constants with address macros from `dcn_1_0_offset.h` and access them through register helpers such as `REG_UPDATE`, `REG_GET`, and related AMD display macros.

## Control Flow

The header has no runtime control flow. Hardware programming flow is implied by the register fields:

1. Select the target block and instance, such as `OTG4`, `OTG5`, `DC_PERFMON18`, DAC, DC I2C, generic I2C, or DIO misc.
2. Read the matching MMIO register using the companion offset macro and display register-access helper.
3. Clear or preserve fields with `*_MASK`, position new values with `*__SHIFT`, and write the composed register value back.
4. For timing generator programming, hold update locks or use double-buffer controls, program totals/blanking/sync/update windows, then allow the update to latch at the intended vertical boundary.
5. For interrupts and latched status, read status bits and write the corresponding `*_CLEAR`, `*_ACK`, or `*_AK` fields according to hardware semantics.
6. For I2C, program speed/setup and transaction descriptors/data, assert `GO`, then poll status and interrupt bits for completion, NACK, timeout, or arbitration events.
7. For perfmon/CRC/autodetect diagnostics, configure selection and masks, enable measurement, then read status or counter/signature fields.

The sequencing-sensitive areas are OTG update locks and pending bits, vertical total/DRR programming, global sync lock and manual trigger controls, write-one-to-clear interrupt/status fields, I2C transaction ordering, DAC autodetect setup/status clearing, memory power force/disable bits, and clock gate disable bits.

## State and Persistence

The header stores no software state and has no persistence of its own. Its constants describe hardware register state that persists until reset, power-management transitions, display mode changes, firmware/hardware action, or explicit driver writes.

Important state domains in this chunk include:

- OTG4/OTG5 timing state: totals, blanking, sync positions, counters, frame count, interlace/stereo state, vertical update windows, global sync status, update pending/lock bits, DRR state, snapshot captures, CRC signatures, static-screen detection, and test-pattern/blank/black color values.
- Interrupt state: OTG snapshot, force-count, force-vsync, trigger, vsync, GSL gap, vertical interrupt, range timing, DAC autodetect, DC I2C, generic I2C, and read-request interrupt status/ack/mask/type fields.
- Diagnostic state: CRC windows and accumulated RGB/blue signatures, pixel readback, perfmon active/report/counter values, DAC comparator/autodetect status, FIFO overflow/underflow flags, I2C status and data indexes.
- Power and clock state: DIO memory power states and force/disable controls for I2C, DP, HDMI, and AFMT subblocks, plus DIO/DVO/DAC/reference/DIG clock gate disables.
- Scratch and integration state: full-width DIO scratch registers and VCE audio stream selection.

Because these are hardware-facing constants, callers must preserve reserved bits and use the correct access path and width. Full-width fields such as scratch registers and CRC/perfmon counter pieces can be safely represented as 32-bit values, while packed state fields require masking before interpretation.

## Dependencies and Integration Points

This chunk depends only on the C preprocessor, but it is meaningful only with the rest of the DCN 1.0 generated register headers and AMD display register helper infrastructure.

Primary integration points are:

- `display/dc/resource/dcn10/dcn10_resource.c`, which includes the header for DCN 1.0 resource and register table setup.
- `display/dc/irq/dcn10/irq_service_dcn10.c`, which uses DCN 1.0 mask/shift data for interrupt source programming and acknowledgement.
- `display/dc/gpio/dcn10/hw_factory_dcn10.c`, `display/dc/gpio/dcn10/hw_translate_dcn10.c`, and `display/dc/gpio/dcn20/hw_translate_dcn20.c`, which include the header for GPIO/DDC mapping and translation.
- Shared DCE display helpers for timing generators, I2C/DDC, link encoders, DAC/autodetect, performance monitoring, CRC, and power/clock controls.
- Hardware programming paths for modeset timing, vblank/vsync IRQs, DisplayPort global sync, dynamic refresh rate, diagnostics, EDID/DDC transactions, analog output handling, and DIO memory/clock power management.

The repeated `OTG4` and `OTG5` layouts are especially important for instance-indexed timing-generator code. Repeated DDC speed/setup/status fields and DIG/DP/HDMI/AFMT power fields are similar integration signals: driver tables should select the intended instance instead of synthesizing names manually.

## Risks

The main risk is silent hardware misprogramming. Incorrect shifts or masks compile normally but can write the wrong bit, corrupt adjacent fields, fail to acknowledge interrupts, or leave reserved bits changed. Failures would likely appear as modeset instability, missing vblank/vsync events, incorrect DRR timing, broken global sync, invalid CRC/test-pattern diagnostics, I2C/DDC timeouts, bad EDID reads, DAC detect failures, audio-stream selection errors, or power-management glitches.

Boundary risk exists for this chunk. It starts after the beginning of `OTG4_OTG_STEREO_CONTROL` and ends before `DIO_POWER_MANAGEMENT_CNTL`, so the final per-file reconciliation should merge adjacent chunk notes before treating the OTG4 stereo-control and DIO power-management areas as complete.

The OTG update and timing fields are timing-sensitive. Programming totals, blanking, vertical total min/max/mid, update locks, or `OTG_UPDATE_INSTANTLY` at the wrong time can create visible glitches or transient invalid modes. DRR and global sync fields are similarly sensitive because they affect frame pacing and multi-pipe synchronization.

Status/ack/clear fields require the hardware access semantics, not just the bit layout. Blind read/modify/write can acknowledge or clear latched status unexpectedly, especially for vertical interrupts, range timing interrupts, DAC autodetect, and I2C completion/error bits.

The generated `*_MASK_MASK` names are easy to misread. They represent fields whose hardware names include `MASK`; renaming or normalizing them would break consistency with generated code and existing call sites.

DIO power and clock gating bits can affect multiple display links. Incorrect force/disable settings may make DDC, DP, HDMI, AFMT, DAC, or DIG blocks appear intermittently unavailable, particularly across suspend/resume and hotplug paths.

## Test Signals

Useful validation signals for this chunk are mostly static plus hardware integration tests:

- Build coverage for DCN 1.0 display resource, IRQ, GPIO, timing, I2C, and link-encoder code that includes or indirectly consumes `dcn_1_0_sh_mask.h`.
- Generated-header consistency checks that every `REGISTER__FIELD__SHIFT` has an aligned mask, repeated OTG instances preserve equivalent field layouts, and duplicate macro names do not collide.
- Diff or regeneration checks against the authoritative DCN 1.0 ASIC register database.
- Modeset tests across pipes using OTG4/OTG5, including timing totals, blank/sync positions, frame counters, interlace/stereo, update-lock behavior, vblank/vsync interrupts, global sync, and DRR.
- CRC/test-pattern/static-screen diagnostic tests that program windows and masks, then verify nonzero and stable signature readback.
- IRQ tests for snapshot, force-count, force-vsync, trigger, vertical interrupt, range timing, DAC autodetect, and I2C status/ack/mask/type fields.
- DDC/EDID tests on all DDC channels and generic I2C pins, covering speed/setup programming, transaction sequencing, NACK/timeout/arbitration handling, and data FIFO indexes.
- DAC/autodetect tests for load detection, forced output, comparator state, powerdown controls, and FIFO status where analog-output hardware is present.
- Suspend/resume and runtime power tests that verify DIO memory power state/control and DIO clock gate fields return to expected values and do not break hotplug, EDID, DP/HDMI, AFMT, or DAC behavior.

## Cross-Chunk Notes

This is one interior slice of a large generated header. The final per-file document should reconcile this with the previous chunk for the beginning of `OTG4_OTG_STEREO_CONTROL` and with the following chunk for `DIO_POWER_MANAGEMENT_CNTL` and the remaining DIO/PHY/audio/display-output register definitions.

### subset-b-001592: lines 27515-29881

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 27515-29881

## Scope

This chunk covers lines 27515-29881 of AMD's generated DCN 1.0 register shift/mask header. It contains 2367 source lines, 2176 `#define` lines, and 165 register/address-block comments. There are no C functions, structs, enums, or inline helpers; the exported surface is a large set of preprocessor constants that give bit shifts and already-positioned masks for DCN display I/O registers.

The range starts in the tail of the `DIO_CLK_CNTL` macro family and ends in the middle of `DP_AUX5_AUX_GTC_SYNC_CONTROLLER_STATUS`. It covers DIO clock/reset/power interrupt controls, HPD0-HPD5 hot-plug blocks, `DC_PERFMON19`, and DP AUX channel blocks AUX0 through most of AUX5.

## Purpose

The macros describe DCN 1.0 display I/O register fields so AMDGPU display code can build read/modify/write values without open-coded bit positions. Each generated field follows the convention:

- `REGISTER__FIELD__SHIFT` gives the field's bit offset.
- `REGISTER__FIELD_MASK` gives the field mask in final register position.
- If the hardware field is itself named `*_MASK`, the generated name becomes `REGISTER__FIELD_MASK__SHIFT` and `REGISTER__FIELD_MASK_MASK`; these double-`MASK` names are intentional generated output.

The first section covers DIO-level controls: display/ref clock gate-disable bits, power-management reset/busy status, stereo sync selection, DIO and DIG soft resets, AFMT memory-power status, AFMT/TMDS clock gate controls, HDMI RX-status timer configuration, PSP and generic DIO interrupt status/message/clear fields.

The HPD sections repeat the same layout for `HPD0` through `HPD5`. They expose hot-plug status, current and delayed sense, RX interrupt status, connect/disconnect toggle filter timer values, interrupt ack/polarity/enable fields, RX interrupt ack/enable fields, connection and RX interrupt timer programming, HPD enable, fast-train delay/enable controls, and connect/disconnect debounce/filter delay fields.

`DC_PERFMON19` exposes one display performance-monitor instance. Its fields cover event selection, counted-value selection, increment mode, hardware control selection, run-enable mode, count-off/start/restart controls, interrupt enable/status/ack, active state, counter selection, counted-value type, hardware stop selectors, count-off selector, packed per-counter states for counters 0-7, report count, clock enable, run-enable start/stop selectors, high/low counter values, and per-counter interrupt status/ack bits.

The DP AUX sections define repeated register layouts for `DP_AUX0` through `DP_AUX5`. Each instance includes AUX enable/reset/reset-done, link-status read controls, HPD selection, HPD-disconnect ignore, mode detection, impedance calibration request, test/deglitch/spare bits, software transaction control, arbitration between software and DMCU users, interrupt status/ack/mask fields for software/LS/GTC events, software and link-service status/error fields, data/index access windows, TX/RX DPHY timing/status, and GTC sync error/controller/status fields. The requested slice stops before the full AUX5 GTC sync controller/status layout is present.

## Important APIs, Types, and Functions

This chunk has no callable APIs, data types, or executable functions. Its important API is the macro namespace itself. Consumers combine these masks and shifts with companion register offsets from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h` and AMD display register helpers.

Relevant consumer patterns in this tree include:

- `display/dc/gpio/dcn10/hw_factory_dcn10.c` and `display/dc/gpio/dcn10/hw_translate_dcn10.c`, which include `dcn_1_0_sh_mask.h` for DCN10 GPIO/HPD register translation.
- `display/dc/irq/dcn10/irq_service_dcn10.c`, which includes the DCN 1.0 mask header for IRQ source metadata.
- `display/dc/irq/irq_service.c`, where HPD ack code reads `HPD0_DC_HPD_INT_STATUS.DC_HPD_SENSE_DELAYED` and flips `HPD0_DC_HPD_INT_CONTROL.DC_HPD_INT_POLARITY` after generic acknowledgement.
- `display/dc/dce/dce_aux.h`, where `DCN10_AUX_MASK_SH_LIST` maps fields such as `DP_AUX0_AUX_CONTROL.AUX_EN`, `AUX_RESET`, `AUX_RESET_DONE`, arbitration fields, `AUX_SW_GO`, `AUX_SW_DATA`, `AUX_SW_REPLY_BYTE_COUNT`, `AUX_SW_DONE`, and `AUX_SW_DONE_ACK` into the generic AUX engine field table.
- `display/dc/dio/dcn10/dcn10_link_encoder.h`, where link-encoder field lists use `DP_AUX0_AUX_CONTROL.AUX_HPD_SEL`, `AUX_LS_READ_EN`, `DP_AUX0_AUX_DPHY_RX_CONTROL0.AUX_RX_RECEIVE_WINDOW`, and `HPD0_DC_HPD_CONTROL.DC_HPD_EN`.

Although the chunk defines all six AUX and HPD instances, several generic field-list macros are written against instance 0 and rely on per-instance register-offset arrays or generated macros elsewhere to select the actual hardware instance.

## Control Flow

The header itself has no runtime control flow. Runtime flow is implied by the register fields:

1. Select the correct DCN 1.0 offset/register instance, such as HPD0 versus HPD5 or AUX0 versus AUX5.
2. Read a register with AMD display MMIO helpers such as `dm_read_reg()` or generation-specific register wrappers.
3. Extract fields with the generated mask and shift, or clear and set fields before writing a modified value back.
4. For HPD events, read sense/status, acknowledge latched interrupt bits, and adjust polarity so the next edge is detected.
5. For AUX transactions, arbitrate register access, program request bytes in `AUX_SW_DATA`, start the transaction with `AUX_SW_GO`, poll or interrupt on `AUX_SW_DONE`, read reply byte count/data, and inspect timeout/overflow/HPD-disconnect/protocol-error fields.
6. For perfmon, enable the monitor clock, choose event/counter controls, start or stop counting, handle threshold/interrupt status, and read low/high counter values.

Sequencing is external to this header. The macros do not say which bits are read-only, write-one-to-clear, self-clearing, sticky, reserved, or safe only while the block is disabled.

## State and Persistence

The file stores no software state and persists nothing at runtime. Its constants describe hardware-backed state in the DCN 1.0 display I/O block.

State represented by this chunk includes:

- DIO clock gating, test clock selection, reset assertion, soft-reset controls, AFMT memory-power state, HDMI RX-status timer status, and DIO-to-PSP/generic interrupt messages.
- HPD sense, delayed sense, RX interrupt status, hot-plug interrupt polarity/enables/acks, debounce/toggle filter timers, fast-train trigger timing, and per-pin enable state for six HPD pins.
- Perfmon19 event selection, counter modes, active/running state, report count, interrupt latches, selected counter state, and 48-bit-style value readback split across low/high fields.
- AUX channel enable/reset state, software/DMCU arbitration state, software and link-service request/done/error state, AUX data FIFOs/index windows, DPHY timing and active/RX/TX state, GTC sync error counters, and GTC sync lock/error controller state.

These hardware states can persist until driver writes, hardware self-clears, interrupt acknowledgement, link retraining, hotplug state transitions, DMCU/firmware activity, display power gating, suspend/resume, or ASIC reset changes them.

## Dependencies and Integration Points

The direct dependency is only the C preprocessor, but the constants are meaningful only with the matching DCN 1.0 offset header and DC display register-access framework. The practical integration points are:

- DCN10 GPIO factory/translation and IRQ-service construction.
- Common HPD interrupt acknowledgement and hotplug polarity handling.
- Generic DCE/DCN AUX engine code that uses per-generation field lists for DP AUX transactions and DPCD access.
- DCN10 link encoder construction and setup paths that select AUX/HPD routing and link-service behavior.
- Display performance-monitor debug, diagnostics, or telemetry paths that can program `DC_PERFMON19`.
- Low-level power-management and hardware-sequencing code that may gate DIO clocks, reset DIO/DIG blocks, or inspect memory-power status.

The same register-family names appear in nearby DCE/DCN generations. Callers must include the mask/shift header that matches the ASIC generation and its offset header; identical field names do not guarantee identical addresses or complete field availability across generations.

## Risks

Incorrect masks or shifts compile cleanly but can silently program the wrong hardware bits. In this chunk, likely symptoms include missed or repeated hotplug interrupts, wrong HPD polarity after acknowledgement, AUX transaction timeouts, corrupted AUX reply parsing, broken DPCD/EDID reads, DisplayPort link-training failures, disabled AUX/HPD routing, inaccurate perf counters, or stuck DIO/DIG reset/clock gating.

Status and acknowledgement fields are especially sensitive. `*_ACK`, `*_CLEAR`, status, and mask fields often live in the same register. A careless read/modify/write can acknowledge an event unintentionally or preserve a stale mask bit. The generated names do not encode write-one-to-clear versus read-only semantics.

Repeated HPD/AUX instances create copy or generation risks. HPD0-HPD5 and AUX0-AUX5 should have parallel layouts, but a one-bit drift affects only one connector path and may appear as board- or port-specific failure. Conversely, assuming all instances exist on every ASIC or board can touch unimplemented registers.

The AUX arbitration fields expose shared access between software and DMCU. Programming AUX without respecting `AUX_SW_USE_AUX_REG_REQ`, pending status, and done-using-register fields can conflict with firmware or queued link-service operations.

Boundary risk exists for this research chunk. It starts after the beginning of `DIO_CLK_CNTL` and ends before the complete `DP_AUX5_AUX_GTC_SYNC_CONTROLLER_STATUS` and following `DP_AUX5_AUX_GTC_SYNC_STATUS` definitions. The final per-file report should merge adjacent chunks before treating those register families as complete.

## Test Signals

Useful validation signals are mostly static and hardware-integration oriented:

- Kernel build coverage for DCN10 display code that includes `dcn_1_0_sh_mask.h`, especially GPIO, IRQ, AUX, and link-encoder paths.
- Generated-header consistency checks that every `REGISTER__FIELD__SHIFT` has a matching mask, masks align with their shifts, and repeated HPD/AUX instances have identical field layouts where expected.
- Regeneration or diff checks against the authoritative AMD DCN 1.0 register database.
- Hotplug tests on all physical connector paths, including connect/disconnect debounce, delayed sense, RX IRQ, polarity flipping after ack, suspend/resume, and fast-train timing.
- AUX/DPCD/EDID tests across all available AUX channels, covering normal replies, reply byte counts, timeout, overflow, HPD disconnect during transaction, malformed AUX response status bits, and DMCU/software arbitration.
- Link-training smoke tests for DisplayPort connectors, since AUX, HPD routing, DPHY timing, and fast-train fields are prerequisites for stable training.
- Perfmon tests that program `DC_PERFMON19`, start and stop counters, read low/high values, and exercise counter interrupt status/ack fields.
- Power-management tests that enter/exit display power states and verify DIO clock gate, soft reset, AFMT memory-power status, and AUX/HPD state recover correctly.

## Cross-Chunk Notes

This is one interior slice of a 54345-line generated header. Earlier chunks should describe the start of the DIO clock-control register family before line 27515. Later chunks should complete `DP_AUX5_AUX_GTC_SYNC_CONTROLLER_STATUS`, add `DP_AUX5_AUX_GTC_SYNC_STATUS`, and continue the remaining DCN 1.0 register mask definitions. The final per-file document should treat this header as generated hardware metadata, not algorithmic driver code.

### subset-b-001593: lines 29882-32307

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 29882-32307

## Chunk Scope

Work item `subset-b-001593` covers line range 29882-32307 of `dcn_1_0_sh_mask.h`. This chunk is one slice of a generated AMD DCN 1.0 register shift/mask header. It contains 2164 `#define` entries and 254 register/comment markers for Display Core Next display I/O blocks:

- the tail of `DP_AUX5_AUX_GTC_SYNC_STATUS`
- the full `dce_dc_dio_dp_aux6_dispdec` / `DP_AUX6_*` AUX block
- the full `dce_dc_dio_dig0_dispdec` / `DIG0_*` stream encoder block
- the full `dce_dc_dio_dp0_dispdec` / `DP0_*` DisplayPort stream block
- the start of `dce_dc_dio_dig1_dispdec` / `DIG1_*`, through `DIG1_AFMT_CNTL`

The file is not handwritten control logic. It is generated hardware metadata: every register field has a `__SHIFT` value and a `__MASK` value used by AMDGPU display code to construct typed register-field tables and read/modify/write DCN display registers.

## Purpose

This chunk defines bit positions and bit masks for DCN 1.0 display AUX, DIG, HDMI/AFMT, TMDS, and DP register fields. The definitions let higher-level display code describe hardware fields symbolically, for example `DP0_DP_VID_STREAM_CNTL__DP_VID_STREAM_ENABLE_MASK` instead of open-coded constants.

The practical purpose is to keep register access code independent from raw bit positions while still compiling to constant masks. Display code uses these constants through macro-generated structs such as stream encoder masks/shifts and AUX engine masks/shifts. The chunk therefore acts as an ABI-like contract between driver source and the DCN 1.0 register layout.

## Important Macro Families

### `DP_AUX5_AUX_GTC_SYNC_STATUS`

The chunk starts mid-address-block with the final `DP_AUX5` GTC sync status definitions. Fields include:

- transaction completion/request state: `AUX_GTC_SYNC_DONE`, `AUX_GTC_SYNC_REQ`
- receive error status: timeout state, timeout, overflow, HPD disconnect, partial byte, non-AUX mode, min-count violation, invalid stop/start, invalid sync, invalid receive levels
- response accounting: `AUX_GTC_SYNC_REPLY_BYTE_COUNT`
- protocol outcome: `AUX_GTC_SYNC_NACKED`, `AUX_GTC_MASTER_REQ_BY_RX`

This continuation depends on earlier `DP_AUX5` GTC sync control/status definitions from the previous chunk. It is a read/status-oriented group and likely participates in diagnostics or GTC sync handling rather than normal software AUX transactions.

### `DP_AUX6_*`

The `dce_dc_dio_dp_aux6_dispdec` address block is fully represented. It defines the sixth AUX engine register field layout:

- `DP_AUX6_AUX_CONTROL`: enable, reset, reset-done, link-service read enable, update disable, HPD-disconnect ignore, mode-detect enable, HPD select, impedance calibration request, test/deglitch/spare bits.
- `DP_AUX6_AUX_SW_CONTROL`: software AUX transaction launch and write-byte count fields.
- `DP_AUX6_AUX_ARB_CONTROL`: arbitration priority, register access status, queued transaction inhibition, SW/DMCU ownership request and done bits. Some request and pending aliases intentionally share the same shift/mask.
- `DP_AUX6_AUX_INTERRUPT_CONTROL`: SW done, LS done, GTC sync lock done, and GTC sync error interrupt/ack/mask fields.
- `DP_AUX6_AUX_SW_STATUS` and `DP_AUX6_AUX_LS_STATUS`: transaction done/request status, receive timeout/error classifications, HPD disconnect, reply byte count, CP IRQ/update bits, and arbitration status.
- `DP_AUX6_AUX_SW_DATA` and `DP_AUX6_AUX_LS_DATA`: indexed byte data windows, including data direction and auto-increment disable for software AUX.
- `DP_AUX6_AUX_DPHY_*`: TX reference selection/rate/divider, TX precharge/config, RX window/threshold timing, TX/RX state, and measured half-symbol period fields.
- `DP_AUX6_AUX_GTC_SYNC_*`: error thresholds, lock acquisition status, error ack fields, controller state, and GTC sync transaction status.

These fields mirror the earlier AUX instances (`DP_AUX0` through `DP_AUX5`) and support driver code that treats AUX engines as an indexed register array. The sixth instance matters for systems exposing enough display links or internal AUX-capable ports to require `DP_AUX6`.

### `DIG0_*`

The `dce_dc_dio_dig0_dispdec` block describes digital stream encoder 0. It includes:

- Front-end encoder control: `DIG0_DIG_FE_CNTL` fields for start, output enable, source select, stereosync, TMDS color/pixel encoding, sync gating, and HDMI/VSync muxing.
- Diagnostics/test: output CRC control/result, clock/test/random patterns, FIFO status, FIFO error ack and calibration/min/max status.
- HDMI packet/control status: `HDMI_CONTROL`, `HDMI_STATUS`, audio packet control, ACR packet control, VBI packet control, infoframe control, generic packet controls, deep color, null/ACP/GC send, AVI/audio info send, and packet generator behavior.
- AFMT audio/generic packet register windows: interrupt status, ISRC packet payload registers, MPEG infoframe words, generic packet header/body registers 0-7, audio info, IEC 60958 channel status, audio CRC, ramp/test control, AFMT status, audio packet control, VBI packet conflict/lock/index, infoframe update/source, and audio source select.
- Back-end encoder and TMDS fields: `DIG_BE_CNTL`, `DIG_BE_EN_CNTL`, lane/symbol clocks, TMDS sync/control character generation, DC balancer, CTL bit generation, pattern output, feedback-path selectors, and lane enable.
- `DIG0_AFMT_VBI_PACKET_CONTROL1`: frame/immediate update and pending bits for generic packets 0-7.

Many of these `DIG0` fields are consumed directly by DCN 1.0 stream encoder register field lists. They drive HDMI/DP packetization, audio metadata, display stream startup, and test/diagnostic features.

### `DP0_*`

The `dce_dc_dio_dp0_dispdec` block describes DisplayPort stream/link registers for DP stream encoder 0:

- Stream/link setup: link training complete/status, embedded panel mode, pixel encoding/component depth/combine, lane count, video stream enable/status/deferred-disable.
- Main Stream Attribute data: colorimetry `MISC0`, `MSA_MISC`, timing parameter registers, VBID misc, and MSA timing overrides.
- Stream timing and rate generation: `DP_VID_TIMING`, `DP_VID_N`, `DP_VID_M`, link framing, stream FIFO reset/overflow/interrupt/ack, TU overflow ack, M/N double buffering and generator fields.
- PHY/link training: DPHY control, training pattern selection, symbol patterns, 8b/10b control, PRBS, scramble control, HBR2 eye pattern, CRC enable/control/result, MST CRC status, fast training control/status, bit-stream/symbol swap, and HBR2 pattern control.
- Secondary data/audio: `DP_SEC_CNTL`, `DP_SEC_CNTL1` through `DP_SEC_CNTL7`, `DP_SEC_FRAMING1` through `DP_SEC_FRAMING4`, audio N/M and readbacks, timestamps, packet control, VSC SDP controls, GSP packet enables and send/line fields, and PPS/metadata packet controls.
- MST/MSE scheduling: rate control/update, slot allocation tables `DP_MSE_SAT0..2`, status readbacks, link timing, misc control, and MSO control.
- Compression/database: DSC control, secondary control extensions, and `DP_DB_CNTL`.

This block supplies the mask/shift constants that stream encoder code uses for DisplayPort main-link activation, video M/N generation, secondary packet scheduling, audio transport, MST time-slot programming, and test CRC paths.

### `DIG1_*` Start

The final part begins the `dce_dc_dio_dig1_dispdec` block and mirrors the `DIG0` layout for stream encoder instance 1. It includes the same front-end, CRC/test, HDMI/AFMT/audio/generic packet, back-end, TMDS, lane-enable, and AFMT clock definitions through `DIG1_AFMT_CNTL`. The block continues in the next chunk with `DIG1_AFMT_VBI_PACKET_CONTROL1` and then `DP1_*`.

Because the stream encoder code usually defines field masks from `DIG0_*` and applies per-instance register offsets separately, `DIG1_*` constants are still important for generated completeness and any code path that refers to instance-specific register names directly.

## APIs, Types, and Functions

This chunk exports only C preprocessor constants. There are no structs, enums, functions, or runtime-visible symbols here.

The important "API" shape is the naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register.
- Some fields intentionally alias the same bit, such as `AUX_SW_USE_AUX_REG_REQ` and `AUX_SW_PENDING_USE_AUX_REG_REQ`, because the hardware presents different semantic names for write/request and read/pending views.

Consumers build compound accessors around these names. Relevant integration examples found in this tree include:

- `drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_stream_encoder.h`, where `SE_SF(reg_name, field_name, mask_sh)` expands register/field names into `.field_name = reg_name__field_name_MASK` or `_SHIFT` initializers.
- `drivers/gpu/drm/amd/display/dc/dce/dce_aux.h`, where `AUX_SF(...)` does the same for AUX engine field tables.
- `drivers/gpu/drm/amd/display/dc/dce/dce_aux.c`, where the resulting fields are used by `REG_UPDATE`, `REG_WAIT`, `REG_READ`, `REG_GET`, and raw status-bit checks.
- `drivers/gpu/drm/amd/display/dc/dce/dce_link_encoder.c` and `drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_link_encoder.c`, where AUX HPD selection, link-service-read enable, and encoder behavior are programmed.

## Control Flow

The header has no executable control flow. The effective runtime flow is indirect:

1. ASIC-specific DCN headers provide address macros and this shift/mask header.
2. Resource, link encoder, stream encoder, AUX, and IRQ service code instantiate per-generation register tables.
3. Driver operations call register helper macros such as `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, and `REG_WAIT`.
4. Those helpers use the mask/shift constants from this file to isolate or update individual register fields.
5. Hardware state changes in MMIO registers drive display behavior, AUX transaction completion, HDMI/DP packet transmission, interrupts, and status polling.

For AUX specifically, the control flow around this chunk is visible in `dce_aux.c`: software requests register ownership using `AUX_ARB_CONTROL`, resets/enables `AUX_CONTROL`, waits on `AUX_SW_STATUS.AUX_SW_DONE`, reads reply count and status/error masks, and classifies timeout/HPD/protocol failures. The `DP_AUX6_*` constants are the indexed sixth-instance equivalent of that flow.

For stream encoders, `dcn10_stream_encoder.h` maps `DIG0_*` and `DP0_*` field constants into field tables. Runtime stream encoder functions then program pixel format, stream enable, secondary-data packet enables, audio packet controls, MSA timing, and HDMI infoframes through register helper macros.

## State and Persistence Behavior

All state represented by this chunk lives in DCN hardware registers, not in kernel memory managed by this header. The masks name several categories of hardware state:

- Latched/acknowledged interrupt state: AUX SW/LS/GTC interrupt bits, FIFO overflow flags, HDMI/AFMT audio enable changes, DP steer/TU overflow flags, and generic packet conflict bits.
- Pollable readiness state: AUX reset done, AUX transaction done, AUX arbitration status, DP stream status, link-training status, fast-training status, FIFO calibration, AFMT audio clock status, and GTC sync lock state.
- Runtime configuration state: stream enable bits, pixel encoding/component depth, HDMI deep color/scrambling/null/audio/ACR packet controls, AFMT packet payload selection, DP M/N/timing fields, secondary-data packet enables, MST slot allocation, and TMDS generation settings.
- Indexed payload/data windows: AUX software/link-service data bytes and AFMT generic/audio/ISRC/MPEG packet payload registers.

Persistence is hardware-scoped. Values survive as long as the display engine retains register state, but can be reset by GPU reset, display controller reset, DCN power-gating, suspend/resume, or mode-set reprogramming. The driver must reinitialize relevant fields during link training, hotplug recovery, stream creation, audio enablement, and resume paths.

## Dependencies

This chunk depends on the broader generated register-header set:

- address macros such as `mmDIG0_*`, `mmDP0_*`, and `mmDP_AUX6_*` from matching DCN/DCE `*_d.h` headers
- register helper infrastructure in AMD display code that understands masks and shifts
- naming compatibility with field-list macros in DCN/DCE code
- hardware register layout for DCN 1.0 display I/O blocks

The constants also depend on consistent instance layout. `DP_AUX6`, `DIG0`, `DP0`, and `DIG1` are instance-specific generated names; driver code often treats only instance 0 names as the canonical field layout and relies on per-instance register addresses for different encoders or AUX engines. If a later ASIC changes a field layout, it needs a separate generation-specific mask header instead of reusing these constants.

## Integration Points

Important integration points visible from this chunk:

- AUX engine access and reset: `dce_aux.h`, `dce_aux.c`, `dce_link_encoder.c`, `dcn10_link_encoder.c`, and resource files that initialize AUX reset masks.
- DCN stream encoder setup: `dcn10_stream_encoder.h` uses `DIG0_*`, `DP0_*`, HDMI, AFMT, MSA, and DP secondary-data masks to build `dcn10_stream_encoder_shift` and `dcn10_stream_encoder_mask` tables.
- IRQ/service wiring: DCN interrupt service headers include the same generated mask file and can use interrupt/ack/mask fields to describe source behavior.
- DisplayPort behavior: DP0 masks support link training status, stream enable/disable, video timing M/N, secondary data packets, MST slot scheduling, DSC/PPS packet signaling, CRC/test paths, and embedded-panel state.
- HDMI/audio behavior: DIG0/DIG1 HDMI and AFMT masks support packet generator setup, ACR/audio clocking, audio channel status, generic infoframes, ISRC/MPEG packets, and audio FIFO/CRC status.
- TMDS/back-end behavior: DIG masks support HDMI/DVI TMDS control characters, DC balancing, lane enable, back-end source/mode selection, and dual-link/TMDS lane state.

## Risks and Failure Modes

- Wrong mask/shift values can silently corrupt adjacent fields during read/modify/write operations. For display registers that pack many one-bit flags, a single bad mask can alter unrelated interrupt, ack, stream-enable, or packet-send bits.
- Status and ack fields share registers with enable/control fields. Driver writes must preserve unrelated bits and use the intended write-one-to-ack semantics where applicable.
- Alias fields in `AUX_ARB_CONTROL` make semantic errors easy: request/pending names share masks, but software must know whether it is writing a request bit or reading a pending/status bit.
- AUX status interpretation depends on raw mask checks in addition to field helpers. If the masks for timeout, HPD disconnect, invalid stop/start, or reply byte count are wrong, AUX transactions may be retried, failed, or classified incorrectly.
- `DIG0` and `DIG1` mirror each other. Any generated drift between instances can break code that assumes uniform field layouts across stream encoder instances.
- DP secondary-data and MST fields coordinate multiple packet slots and update-pending flags. Incorrect masks can lead to stale metadata, missing audio/infoframes, broken MST bandwidth allocation, or PPS/DSC signaling issues.
- Hardware generation coupling is strict. These constants are only valid for the DCN 1.0 register map; applying them to later DCN generations can work for unchanged fields but is unsafe for fields that moved, widened, or changed semantics.

## Test Signals

Useful signals for validating this chunk and its consumers include:

- compile coverage of AMDGPU display code that includes `dcn_1_0_sh_mask.h`, especially DCN 1.0 stream encoder, AUX, link encoder, and IRQ service objects
- static checks that every field referenced by `SE_SF(...)`, `AUX_SF(...)`, and link encoder field lists has both `_MASK` and `__SHIFT` definitions
- AUX transaction tests on each physical AUX instance, including hotplug/disconnect, timeout, invalid reply, and reply-byte-count paths; the `DP_AUX6` instance should be tested on hardware exposing that engine
- display mode-set tests over DP and HDMI that verify stream enable/disable, link training, M/N timing generation, packet transmission, and audio enablement
- HDMI/DP audio tests for ACR values, IEC 60958 channel-status programming, audio clock enable/status, and audio FIFO overflow ack
- MST and secondary-data tests that exercise MSE slot allocation, SDP/GSP packet enables, update-pending behavior, and DSC/PPS metadata
- suspend/resume and GPU reset tests that confirm hardware registers are reprogrammed rather than relying on retained state
- debugfs or register-dump comparisons against vendor register specifications for representative fields such as `DP0_DP_VID_STREAM_CNTL`, `DP0_DP_SEC_CNTL*`, `DIG0_HDMI_CONTROL`, `DIG0_AFMT_VBI_PACKET_CONTROL1`, and `DP_AUX6_AUX_SW_STATUS`

## Cross-Chunk Notes

- The `DP_AUX5` group is only the tail of a larger AUX5 section that starts in the prior chunk.
- The `DIG1` block is incomplete here and continues in `subset-b-001594`, which should cover `DIG1_AFMT_VBI_PACKET_CONTROL1` and the following `DP1_*` block.
- Whole-file reconciliation should merge this chunk with neighboring chunks before drawing conclusions about complete DCN 1.0 register coverage or instance counts.

### subset-b-001594: lines 32308-34753

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 32308-34753

## Scope

This chunk covers 2,446 lines from the generated DCN 1.0 register shift/mask header. It starts at the tail of the `DIG1_AFMT_CNTL` definitions, contains `DIG1_AFMT_VBI_PACKET_CONTROL1`, then covers the complete `dce_dc_dio_dp1_dispdec`, `dce_dc_dio_dig2_dispdec`, and `dce_dc_dio_dp2_dispdec` address blocks. It ends inside the `dce_dc_dio_dig3_dispdec` block at `DIG3_AFMT_AUDIO_INFO1`; the rest of the DIG3 audio-format fields continue in the following chunk.

The source is not executable C. It exports preprocessor constants of the form `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` for DCN 1.0 DisplayPort, HDMI/TMDS, DIG, and AFMT register fields. These macros pair with `dcn_1_0_offset.h` register addresses and with AMD display register helper macros such as `REG_UPDATE`, `REG_GET`, `REG_SET`, and the `SE_SF`/`LE_SF` mask-list builders used by DCN10 stream and link encoders.

## Purpose

The chunk describes the bit layouts for three display-output lanes/engines:

- `DP1_*` and `DP2_*` DisplayPort encoder state: link control, pixel format, MSA fields, video stream enable/status, DPHY training/test/CRC controls, secondary-data packets, audio M/N, MST/MSE slot-allocation tables, MSO, DSC control, double-buffering, and MSA/VBID misc controls.
- `DIG2_*` digital encoder state: front-end and back-end control, output CRC/test-pattern generation, FIFO status, HDMI mode/control/status, HDMI audio and ACR packet controls, HDMI infoframe and generic packet controls, AFMT packet/audio metadata, TMDS control and test generation, DIG version/lane enable, AFMT clock control, and AFMT VBI generic-packet update triggers.
- The beginning of the analogous `DIG3_*` digital encoder state, from DIG front-end/output-test fields through HDMI/AFMT generic packets, ACR registers, status readback, and the start of audio infoframe fields.

These definitions let higher-level DCN10 code address replicated hardware blocks by instance while writing generic field names. The generated macros preserve the concrete hardware layout for DP1/DP2/DIG2/DIG3, including fields that are writable controls, read-only status, sticky interrupt/overflow flags, and pending bits used for synchronized hardware updates.

## Important Macro Families

The `DIG1_AFMT_VBI_PACKET_CONTROL1` tail defines per-generic-packet update controls for AFMT generic slots 0 through 7. For each slot it exposes frame-update, frame-update-pending, immediate-update, and immediate-update-pending bits. This is used to schedule auxiliary/audio-format packet payload changes either at a frame boundary or immediately.

The `DP1_*` and `DP2_*` blocks are structurally repeated and include:

- Link and stream controls: `DP_LINK_CNTL`, `DP_PIXEL_FORMAT`, `DP_MSA_COLORIMETRY`, `DP_CONFIG`, `DP_VID_STREAM_CNTL`, `DP_LINK_FRAMING_CNTL`, `DP_VID_MSA_VBID`, `DP_VID_INTERRUPT_CNTL`, and `DP_MSA_VBID_MISC`.
- Stream timing and M/N generation: `DP_VID_TIMING`, `DP_VID_N`, `DP_VID_M`, and `DP_MSA_TIMING_PARAM1` through `PARAM4`.
- PHY training and diagnostics: `DP_DPHY_CNTL`, `DP_DPHY_TRAINING_PATTERN_SEL`, `DP_DPHY_SYM0` through `SYM2`, `DP_DPHY_8B10B_CNTL`, PRBS/scrambler/CRC controls and results, fast-training controls/status, byte/symbol swap controls, and HBR2 pattern selection.
- Secondary-data and audio transport: `DP_SEC_CNTL`, `DP_SEC_CNTL1` through `CNTL7`, `DP_SEC_FRAMING1` through `FRAMING4`, `DP_SEC_AUD_N`, `DP_SEC_AUD_M`, readback registers, `DP_SEC_TIMESTAMP`, and `DP_SEC_PACKET_CNTL`.
- MST/MSO/DSC support: `DP_MSE_RATE_CNTL`, `DP_MSE_RATE_UPDATE`, `DP_MSE_SAT0` through `SAT2`, `DP_MSE_SAT_UPDATE`, `DP_MSE_LINK_TIMING`, `DP_MSE_MISC_CNTL`, status mirrors, `DP_MSO_CNTL`, `DP_MSO_CNTL1`, and `DP_DSC_CNTL`.
- Double-buffer controls: `DP_DB_CNTL` exposes pending, taken, clear, lock, and disable bits for synchronized register updates.

The `DIG2_*` block and the visible `DIG3_*` portion provide HDMI/TMDS and AFMT controls:

- DIG front-end and test/readback fields: `DIG_FE_CNTL`, output CRC control/result, clock/test/random patterns, and FIFO underflow/overflow interrupt, ack, mask, and force bits.
- HDMI mode and packets: `HDMI_CONTROL`, `HDMI_STATUS`, audio packet, ACR packet, VBI packet, infoframe controls, generic packet controls, general-control packet, deep-color/scrambler/keepout fields, ACR CTS/N programming and readback, and double-buffer status.
- AFMT metadata/audio fields: interrupt status, audio packet control, ISRC packet data, MPEG info, generic packet header and 32-byte generic payload banks, audio infoframe fields, IEC 60958 channel-status words, audio CRC, ramp/test controls, AFMT status, audio source selection, and AFMT clock enable/status.
- TMDS controls: encoder enable, sync/control-character patterns, DCBalancer, stereo-sync selection, lane/control-bit generation, per-control-symbol data selection, delays, inversion, modulation, feedback, and pattern output.
- DIG back-end and lane state: `DIG_BE_CNTL`, `DIG_BE_EN_CNTL`, `DIG_VERSION`, and `DIG_LANE_ENABLE`.

## APIs, Types, and Functions

There are no C functions, structs, enums, or runtime APIs in this chunk. The macros themselves are the ABI-like interface between generated ASIC metadata and DCN display code:

- `*_SHIFT` values are the bit offsets for packing or extracting a field.
- `*_MASK` values are already-positioned bit masks for read/modify/write helpers.
- Address-block comments group replicated hardware instances: `dce_dc_dio_dp1_dispdec`, `dce_dc_dio_dig2_dispdec`, `dce_dc_dio_dp2_dispdec`, and the start of `dce_dc_dio_dig3_dispdec`.

Integration code maps the instance-specific macros into per-object register structures. For example, `dcn10_stream_encoder.h` lists DP and DIG stream encoder registers such as `DP_SEC_CNTL`, `DP_MSE_RATE_CNTL`, `DP_VID_STREAM_CNTL`, `HDMI_CONTROL`, and AFMT audio registers, then uses `SE_SF(DP0_..., FIELD, mask_sh)` aliases so generic encoder code can operate on a selected instance. `dcn10_link_encoder.h` similarly maps link-side DP MST slot-allocation and video-stream fields through `LE_SF(...)`.

## Control Flow

This header has no control flow by itself. The runtime sequences are in DCN10 link and stream encoder code that consumes these masks:

1. Resource construction includes `dcn_1_0_offset.h` and this header, then builds register address and shift/mask tables for each stream/link encoder instance.
2. Mode-set and link-training code programs DP link, pixel, lane, DPHY, M/N, framing, stream-enable, and secondary-data fields with register helper macros.
3. HDMI setup writes `HDMI_CONTROL`, packet-control, ACR, infoframe, AFMT, and TMDS fields according to the signal type, pixel clock, color depth, audio layout, and infoframe payloads.
4. MST setup writes `DP_MSE_SAT*`, `DP_MSE_RATE_*`, and update bits, then polls pending/keepout/status fields before considering slot allocation active.
5. Stream disable paths clear `DP_VID_STREAM_ENABLE`, may program `DP_VID_STREAM_DIS_DEFER`, and wait for `DP_VID_STREAM_STATUS` to drop before proceeding.
6. Generic packet, AFMT, double-buffer, CRC, FIFO, overflow, and interrupt-style fields expose status, pending, ack, mask, and clear bits that caller code must order correctly around hardware update points.

The replicated DP1/DP2 and DIG2/DIG3 names are not arbitrary aliases: their prefixes encode the physical register instance. A mismatch between offset and shift/mask instance can program the wrong display engine or corrupt a neighboring field in the right engine.

## State and Persistence

The header stores no software state, but every macro describes persistent hardware register state in DCN display output blocks. Relevant state includes:

- DP link/stream state: link training complete/status, embedded-panel mode, lane count, pixel encoding/depth, video stream enable/status, M/N generation, MSA/VBID placement, interrupt state, and enhanced framing.
- DP PHY/test state: training pattern selection, custom symbol patterns, 8b/10b disable, PRBS/scrambler toggles, CRC enable/reset/continuous mode/result, fast-training status, and byte/symbol swap controls.
- DP secondary-data and audio state: global and per-packet enables, packet line numbers, MSA/audio timestamping, audio M/N values and readbacks, packet priority, generic stream-packet send/pending bits, and VSC SDP metadata.
- MST/MSO/DSC state: payload slot allocation, rate update pending status, keepout status, link timing, MSO segment mapping and timing fields, and DSC mode enable.
- HDMI/TMDS/AFMT state: deep color, scrambler, keepout, packet enable/line controls, ACR N/CTS, infoframes, generic payload bytes, ISRC/MPEG/audio info fields, IEC 60958 channel status, audio source/channel layout, CRC/ramp test state, TMDS symbols, and DIG lane enables.

These hardware fields persist until overwritten, reset, disabled by power management, or reinitialized by firmware/driver mode-set flows. Pending, taken, ack, clear, interrupt, overflow, and status fields are especially stateful because some are read-only hardware observations while others require write-one-to-clear or explicit update sequences. The generated header does not encode those semantics beyond the field names.

## Dependencies and Integration Points

Direct dependencies are limited to the C preprocessor and the companion register offset file `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h`. Real users include:

- `display/dc/resource/dcn10/dcn10_resource.c`, which includes both DCN 1.0 offset and shift/mask headers while constructing DCN10 hardware resource tables.
- `display/dc/dio/dcn10/dcn10_stream_encoder.h` and `.c`, which consume DP secondary-data, DP video stream, HDMI, AFMT, ACR, and audio-field masks.
- `display/dc/dio/dcn10/dcn10_link_encoder.h` and `.c`, which consume `DP_VID_STREAM_CNTL`, `DP_SEC_CNTL1`, and MST `DP_MSE_SAT*` fields.
- `display/dc/irq/dcn10/irq_service_dcn10.c`, GPIO translation/factory code, and DCN20 GPIO translation code, which include this generated header as part of the shared DCN register description surface.
- Shared display register helpers from `reg_helper.h`, whose macros rely on consistent shift/mask naming to generate correct MMIO read/modify/write operations.

The DP and DIG block structures are repeated across instances and generations. Later DCN stream encoder headers show the same conceptual field groups, which is a useful consistency check when validating generated DCN 1.0 masks.

## Risks

The highest risk is silent hardware misprogramming. A wrong shift or mask in this generated header can compile cleanly while changing an unrelated field inside a live DP, HDMI, AFMT, or TMDS register.

Chunk-boundary risk is present at both ends. The chunk starts after the `DIG1_AFMT_CNTL__AFMT_AUDIO_CLOCK_EN__SHIFT` definition but includes its `AFMT_AUDIO_CLOCK_ON` shift and both masks. It also ends midway through `DIG3_AFMT_AUDIO_INFO1`; the later merge lane must combine this with adjacent chunks to avoid treating partial register families as complete.

Instance-alignment errors are possible because DP1/DP2 and DIG2/DIG3 are repeated with near-identical fields. Code that pairs `mmDP2_*` offsets with `DP1_*` masks, or DIG2 offsets with DIG3 masks, may hit a valid-looking register with wrong instance semantics.

Several fields have order-sensitive hardware behavior. `DP_VID_STREAM_ENABLE` and `DP_VID_STREAM_STATUS` are used in disable/enable waits; `DP_MSE_SAT_UPDATE` and keepout fields gate MST slot changes; `DP_MSE_RATE_UPDATE_PENDING`, `DP_SEC_GSP*_SEND_PENDING`, double-buffer pending/taken bits, and AFMT VBI update-pending bits require polling or frame-boundary synchronization. Incorrect masks here can cause hangs, lost packets, or visible mode-set glitches.

Audio/video packet fields have protocol-visible consequences. Bad ACR N/CTS, IEC 60958, AFMT audio info, HDMI infoframe, generic packet, or DP secondary-data masks can produce broken HDMI/DP audio, missing HDR/VRR/VSC metadata, invalid AVI/SPD/vendor packets, or sink compatibility failures without crashing the driver.

Diagnostic and interrupt fields can hide real faults. FIFO underflow/overflow masks, CRC controls/results, DPHY training status, fast-training status, and interrupt ack/mask fields are often used for hardware bring-up and failure handling; incorrect masks may suppress errors or report false positives.

## Test Signals

Useful validation signals include:

- Build coverage for DCN10/DCN20 display code that includes `dcn_1_0_sh_mask.h`, especially stream/link encoder, resource, IRQ, and GPIO translation objects.
- Generated-header checks that each `REGISTER__FIELD__SHIFT` has a matching `REGISTER__FIELD_MASK`, masks align with shifts, and repeated DP1/DP2 and DIG2/DIG3 blocks stay structurally equivalent where hardware intends them to be equivalent.
- Diff checks against AMD's authoritative DCN 1.0 register database or known-good upstream generated headers.
- DP link-training and mode-set smoke tests that exercise `DP_LINK_CNTL`, `DP_CONFIG`, `DP_DPHY_*`, `DP_VID_STREAM_CNTL`, MSA/M/N, and video-stream disable waits.
- MST tests that program payload slot allocations through `DP_MSE_SAT*`, assert update/keepout behavior, and verify payload bandwidth on multiple streams.
- HDMI tests across color depths and pixel clocks that validate `HDMI_CONTROL`, scrambler/deep-color, ACR N/CTS, audio packet transmission, infoframes, and TMDS lane behavior.
- Audio and metadata tests for AFMT audio source/channel layout, IEC 60958 channel status, audio infoframes, generic packet payloads, HDR/VSC/SPD/AVI metadata, and DP secondary packets.
- Hardware diagnostic tests for output CRC, DPHY CRC, PRBS/scrambler patterns, FIFO overflow/underflow reporting, and interrupt ack/mask fields.

## Cross-Chunk Notes

This chunk is a middle slice of a large generated header. It should be merged with neighboring chunks for a complete per-file report: the preceding chunk owns the earlier DIG1/DIG0 families, and the following chunk continues `DIG3_AFMT_AUDIO_INFO1` and the rest of the DIG3/DIG/DP replicated blocks. Treat this document as coverage for the DP1/DIG2/DP2 complete blocks plus partial DIG1 and DIG3 boundaries, not as a standalone module boundary.

### subset-b-001595: lines 34754-37195

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 34754-37195

## Research Scope

This chunk covers `subset-b-001595`, a line-bounded section of AMD DCN 1.0 register field definitions from `dcn_1_0_sh_mask.h`. The span is generated-style C preprocessor data: it contains no functions, structs, control statements, or storage declarations. Its exported surface is the set of `#define` constants used by display driver code to compose, extract, and acknowledge bitfields in DIG, HDMI, AFMT, TMDS, and DisplayPort register blocks.

The chunk begins inside `DIG3_AFMT_AUDIO_INFO1`, so only the final two mask constants for that register are included in this work item. It ends at `DIG5_AFMT_AUDIO_PACKET_CONTROL2`; the following `DIG5_AFMT_ISRC*` register definitions continue outside this chunk. Downstream merge should preserve those boundary facts when synthesizing the full-file report.

## Purpose

The purpose of this range is to define bit positions (`__SHIFT`) and bit masks (`_MASK`) for several display encoder instances:

- `DIG3` audio formatter and TMDS/backend fields.
- `DP3` DisplayPort link, main stream attribute, DPHY, secondary data packet, MST/MSE, DSC, and double-buffer fields.
- `DIG4` front-end, HDMI, audio formatter, generic packet, TMDS, backend, lane, and VBI update fields.
- `DP4` DisplayPort fields equivalent to the `DP3` block for a separate hardware instance.
- The start of `DIG5`, covering front-end, HDMI, CRC/test/FIFO, generic packet, global control, and audio packet control fields.

The driver can use these macros with register accessor helpers to write only selected fields without hardcoding numeric bit layouts at call sites.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The important interface is the macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low-bit position of a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned bit mask for the same field.
- Register prefixes such as `DIG3_`, `DP3_`, `DIG4_`, `DP4_`, and `DIG5_` identify repeated display encoder/link instances.

I counted 2,162 `#define` lines in the requested range: 1,080 `__SHIFT` defines, 1,082 `_MASK` defines, and 267 distinct register names. The two extra masks are due to the chunk starting after the corresponding `DIG3_AFMT_AUDIO_INFO1` shift definitions.

Key register families in this chunk include:

- Audio formatter fields: `AFMT_60958_*`, `AFMT_AUDIO_INFO*`, `AFMT_AUDIO_CRC_*`, `AFMT_AUDIO_PACKET_CONTROL*`, `AFMT_STATUS`, `AFMT_RAMP_CONTROL*`, `AFMT_VBI_PACKET_CONTROL*`, `AFMT_GENERIC_*`, `AFMT_MPEG_INFO*`, and ISRC-adjacent packet controls.
- HDMI fields: `HDMI_CONTROL`, `HDMI_STATUS`, `HDMI_AUDIO_PACKET_CONTROL`, `HDMI_ACR_*`, `HDMI_VBI_PACKET_CONTROL`, `HDMI_INFOFRAME_CONTROL*`, `HDMI_GENERIC_PACKET_CONTROL*`, `HDMI_DB_CONTROL`, and `HDMI_GC`.
- DIG/TMDS fields: `DIG_FE_CNTL`, `DIG_BE_CNTL`, `DIG_BE_EN_CNTL`, `DIG_LANE_ENABLE`, `DIG_FIFO_STATUS`, `DIG_TEST_PATTERN`, `DIG_RANDOM_PATTERN_SEED`, `DIG_OUTPUT_CRC_*`, `TMDS_*`, and `DIG_VERSION`.
- DisplayPort fields: `DP_LINK_CNTL`, `DP_PIXEL_FORMAT`, `DP_CONFIG`, `DP_VID_STREAM_CNTL`, `DP_MSA_*`, `DP_VID_*`, `DP_DPHY_*`, `DP_SEC_*`, `DP_MSE_*`, `DP_MSO_*`, `DP_DSC_CNTL`, `DP_DB_CNTL`, and `DP_MSA_VBID_MISC`.

## Register Coverage Notes

The `DIG3` portion finishes audio formatter, backend, TMDS, lane, and VBI packet control definitions, then transitions to the full `dce_dc_dio_dp3_dispdec` address block. `DP3` contains a complete-looking DisplayPort register-field group in this chunk, including link status/training, video format and timing, MSA metadata, physical-layer training and CRC, secondary packets, audio N/M timestamp data, MST allocation table fields, MSO controls, DSC enable, generic secondary packet send status/line controls, double-buffer control, and VBID/MSA override fields.

The `DIG4` portion starts with `dce_dc_dio_dig4_dispdec` and covers a broad digital encoder block: front-end source selection, output CRC, clock/test/random patterns, FIFO status, HDMI control and status, HDMI audio clock regeneration, VBI/infoframe/generic packet controls, HDMI guard-band/global control, AFMT audio layout/channel stream selection, ISRC and MPEG metadata payload bytes, generic packet header/body bytes, ACR parameter/status values, 60958 channel-status fields, audio CRC/ramp/status, backend enable and HPD selection, TMDS pattern generation, lane enable, AFMT clock state, and generic VBI frame/immediate update handshakes.

The `DP4` portion mirrors the `DP3` DisplayPort field set for another link instance. It repeats link/training, video timing, DPHY, secondary packet, MST/MSE, MSO, DSC, double-buffer, and VBID override definitions with `DP4_` prefixes. Because the fields and masks match the `DP3` shape, code using instance-specific register tables can select equivalent behavior for encoder/link 4.

The `DIG5` portion begins `dce_dc_dio_dig5_dispdec` and covers only the early part of that block in this chunk: front-end selection, CRC/test/fifo controls, HDMI control/status/audio/ACR/VBI/infoframe/generic packet fields, global control, and `AFMT_AUDIO_PACKET_CONTROL2`. The chunk ends before the `DIG5_AFMT_ISRC*` continuation.

## Control Flow

This header chunk has no runtime control flow. Its values participate in control flow indirectly when compiled driver code uses them in register programming sequences. Typical usage is expected to be:

1. Select a register for a DIG, DP, HDMI, TMDS, or AFMT hardware instance.
2. Shift a field value by the matching `__SHIFT` value.
3. Mask it with the matching `_MASK` value, often via generated AMD register macros or helper functions.
4. Write, read, poll, or acknowledge the underlying MMIO register.

Several field groups imply hardware handshakes even though no code executes here. Examples include `_UPDATE_PENDING`, `_SEND_PENDING`, `_SEND_ACTIVE`, `_ACK`, `_CLR`, `_DONE`, `_STATUS`, and `_MASK` interrupt/status bits. Correct caller control flow must respect those hardware semantics in implementation files outside this header.

## State And Persistence Behavior

The macros themselves are compile-time constants and persist only in object code after preprocessing. They do not allocate memory or maintain software state.

The hardware fields they describe do represent persistent device state until changed by MMIO writes or hardware events. Notable state categories in this chunk are:

- Enable state: audio clocks, DIG enable, DP secondary streams, HDMI packet sends, DSC enable, lane enables, test patterns, deep color, and data scrambling.
- Status/interrupt state: FIFO errors, HDMI packet errors, DPHY CRC status, link status, audio enable changes, secondary packet collisions, send pending/deadline missed, MSE allocation status, and double-buffer pending/taken state.
- Packet payload state: audio infoframes, MPEG info, ISRC data, generic packet headers/body bytes, HDMI ACR N/CTS values, 60958 channel-status words, and DisplayPort audio M/N values.
- Timing/allocation state: DP MSA timings, MSE slot allocation tables, MSO link count/secondary stream enables, and secondary packet framing positions.

Because these values map directly to hardware registers, incorrect masks can persist wrong state in display hardware across modesets until the driver reprograms the block or resets the encoder.

## Dependencies

This chunk depends on the rest of the AMD display register-definition system for register addresses, register access helpers, and generated table glue. The local file provides only field positions and masks; address definitions are expected in sibling register headers such as offset/address headers for DCN 1.0.

Integration normally depends on:

- C preprocessor inclusion by AMDGPU DC display code.
- Register accessor macros/functions that accept `*_MASK` and `*__SHIFT` constants.
- Instance-specific DIG/DP register tables that pair these field constants with register addresses.
- Hardware documentation or generated register databases that define the authoritative bit layouts.

There are no external library dependencies in this chunk.

## Integration Points

The definitions are intended for AMDGPU DCN display encoder paths, especially code that configures HDMI, DisplayPort, audio formatting, secondary packets, TMDS output, link training, MST/MSO, DSC, and mode timing. Likely consumers include encoder enable/disable paths, link training routines, audio setup, infoframe programming, CRC/test utilities, hotplug/backend selection, and modeset validation or commit code.

The repeated `DIG3`/`DIG4`/`DIG5` and `DP3`/`DP4` prefix pattern is important for instance mapping. Driver code can use the same logical sequence for different hardware pipes while selecting register constants for the active encoder instance.

## Risks And Edge Cases

- Bitfield drift is the primary risk. A wrong mask or shift can silently program the wrong hardware field, causing display link failures, missing audio, bad infoframes, MST allocation errors, or difficult-to-debug training/status behavior.
- The file is generated-style and highly repetitive. Manual edits are risky because one instance can diverge from equivalent `DIG`/`DP` siblings.
- Boundary chunks are partial. This work item starts after some `DIG3_AFMT_AUDIO_INFO1` shift definitions and ends before the `DIG5_AFMT_ISRC*` continuation, so a full-file report must merge neighboring chunks before making complete statements about those registers.
- Status and acknowledge fields require careful write behavior. Fields ending in `_ACK`, `_CLR`, or status-like names may be write-one-to-clear or hardware-owned; consumers must follow register reference semantics, not infer behavior from mask names alone.
- Some names include `_MASK_MASK` patterns, such as complete-mask fields for interrupt/status masking. These are not duplicate suffix mistakes in this generated naming scheme and should not be normalized away.
- The same field layout appears across `DP3` and `DP4` and across `DIG3`/`DIG4`/`DIG5` subsets. Tests or code generation checks should verify expected equivalence without assuming every instance is complete inside this chunk.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-integration oriented:

- The header should preprocess cleanly with AMDGPU DC code and produce no duplicate or malformed macro names for this line range.
- Register accessor code should build against every `*_MASK`/`*__SHIFT` name referenced by DCN 1.0 DIG, HDMI, DP, AFMT, and TMDS implementation files.
- Generated-header consistency checks should compare sibling instance layouts, especially `DP3` vs `DP4` and overlapping `DIG3`/`DIG4`/`DIG5` register families.
- Runtime display tests should exercise HDMI and DisplayPort modesets, audio enablement, infoframe programming, DP link training, MST slot allocation, DSC enable paths, CRC/test-pattern paths, and status/ack flows.
- Negative signals include missing audio packets, HDMI/DP link training failure, stuck `_PENDING` bits, FIFO or packet error interrupts, bad MSA timing, wrong MST payload allocation, or failed CRC/readback checks.

### subset-b-001596: lines 37196-39642

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 37196-39642

## Scope

This chunk is an interior slice of AMDGPU's generated DCN 1.0 register shift/mask header. It contains only preprocessor definitions: no functions, structs, enums, storage, or executable C logic. The exported surface is a set of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants that describe bit positions inside display-controller MMIO registers.

The range covers 2447 source lines and 2161 `#define` lines. It starts at `DIG5_AFMT_ISRC1_0`, after earlier DIG5 HDMI/AFMT packet-control definitions, and ends inside `DP6_DP_SEC_CNTL2`, after the first generic-secondary-packet masks. The final per-file reconciliation should treat those start/end points as chunk boundaries, not source omissions.

## Purpose

The macros describe the bit layout for late DCN 1.0 DIO instance 5 and early/mid DIO instance 6 display output blocks:

- Tail of `DIG5` audio formatter and HDMI/TMDS support, including ISRC/UPC/EAN bytes, generic HDMI packet controls, double-buffer control, MPEG infoframe bytes, generic packet payload bytes, audio clock regeneration values, audio info packets, IEC 60958 channel-status words, audio CRC, ramp generator controls, AFMT status, packet controls, audio source selection, backend enable controls, TMDS control-symbol generation, lane enable, and AFMT clock control.
- Complete `DP5` DisplayPort stream/link register fields, including link status, pixel format, MSA colorimetry/misc/timing metadata, video timing `M/N`, link framing, HBR2/test pattern controls, VBID and interrupts, DPHY training/PRBS/scrambler/CRC controls, secondary-data packet controls, audio `N/M` values, timestamping, MST/MSE allocation tables, Multi-Stream Operation controls, DSC enable, generic secondary-packet send state, debug controls, and MSA VBID miscellaneous status.
- Most of `DIG6`, beginning at `DIG6_DIG_FE_CNTL` and continuing through the same HDMI/audio/TMDS/AFMT register families seen for DIG5.
- Beginning of `DP6`, from DisplayPort link and stream programming through `DP6_DP_SEC_CNTL2` generic secondary-packet send fields.

These constants are an ABI-like contract between generated ASIC register data and AMDGPU display code. The companion offset header gives the register addresses, while this file gives each field's packed bit position and mask.

## Important Macro Families

Every normal field appears as a pair:

- `REGISTER__FIELD__SHIFT`: the low bit for a field.
- `REGISTER__FIELD_MASK`: the already-positioned field mask.

The `DIG5_*` and `DIG6_*` groups describe digital encoder instances used for HDMI/TMDS and audio-infoframe handling. Important fields include ISRC status/valid/continue bits, packed ISRC byte payloads, generic packet header/payload bytes, generic packet send/continuous/line controls, HDMI double-buffer pending/taken/lock/disable bits, MPEG infoframe bytes, HDMI audio clock regeneration values for 32/44.1/48 kHz families, AFMT audio info bytes, IEC 60958 channel-status bytes, audio CRC engine controls/results, audio test-ramp controls, AFMT status and packet send controls, VBI packet controls, infoframe update behavior, and audio source selection.

The `DIG5_DIG_BE_CNTL`, `DIG5_DIG_BE_EN_CNTL`, `DIG6_DIG_BE_CNTL`, and `DIG6_DIG_BE_EN_CNTL` groups expose backend stream enable and timing selection fields. `DIG6_DIG_FE_CNTL` additionally selects the front-end source, stereo sync, start state, digital bypass select, symbol-clock state, TMDS pixel encoding, and color format.

The TMDS groups for both instances cover character/control-symbol programming: `TMDS_CNTL`, `TMDS_CONTROL_CHAR`, `TMDS_CONTROL0_FEEDBACK`, `TMDS_STEREOSYNC_CTL_SEL`, sync-character patterns, `TMDS_CTL_BITS`, DC balancer settings, and `TMDS_CTL0_1_GEN_CNTL` / `TMDS_CTL2_3_GEN_CNTL`. These fields are used when the digital encoder is operating in HDMI/DVI-style TMDS modes rather than native DisplayPort stream mode.

`DP5_*` is the most complete DisplayPort block in this chunk. It includes:

- Link and stream basics: `DP_LINK_CNTL`, `DP_PIXEL_FORMAT`, `DP_CONFIG`, `DP_VID_STREAM_CNTL`, and `DP_STEER_FIFO`.
- Main Stream Attribute programming: `DP_MSA_COLORIMETRY`, `DP_MSA_MISC`, `DP_VID_TIMING`, `DP_VID_N`, `DP_VID_M`, `DP_LINK_FRAMING_CNTL`, `DP_VID_MSA_VBID`, `DP_MSA_TIMING_PARAM1` through `PARAM4`, and `DP_MSA_VBID_MISC`.
- DPHY training and diagnostics: `DP_DPHY_CNTL`, training pattern selection, symbol pattern registers, 8b/10b, PRBS, scrambler, CRC enable/control/result, MST CRC control/status, fast-training control/status, BS/SR swap, and HBR2 pattern controls.
- Secondary-data and audio packet state: `DP_SEC_CNTL`, `DP_SEC_CNTL1`, `DP_SEC_CNTL2` through `CNTL7`, framing bytes, audio `N/M` programming and readback, timestamp, packet control, debug control, and generic secondary-packet send/pending/deadline bits.
- MST/MSE/MSO and DSC: MSE rate control/update, SAT allocation and status registers, SAT update/link timing/misc fields, MSO secondary stream enable masks, and `DP_DSC_CNTL__DP_DSC_EN`.

`DP6_*` repeats the same DisplayPort layout as `DP5_*` through the middle of `DP_SEC_CNTL2`. Because the range ends at line 39642, this chunk does not contain the remaining `DP6_DP_SEC_CNTL2` masks or later DP6 registers.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The macro namespace is the interface.

Consumers combine these macros with address definitions from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h`, such as `mmDIG5_AFMT_ISRC1_0`, `mmDP5_DP_LINK_CNTL`, and `mmDIG6_DIG_FE_CNTL`. DCN display code includes both the offset and mask headers, then feeds the generated names into register helpers and resource tables.

Direct include points found in this tree include DCN 1.0 GPIO factory/translation code, DCN 1.0 IRQ service code, DCN 1.0 resource setup, and DCN 2.0 GPIO translation code that reuses the DCN 1.0 register definitions. The chunk is therefore part of the low-level display hardware contract, not a Ceph filesystem or distributed-storage implementation despite the repository path prefix.

## Control Flow

This header has no runtime control flow. It supplies constants used by runtime code that performs MMIO or indexed-register operations.

The implied programming flow is:

1. Choose the correct digital/DP instance, for example DIG5 versus DIG6 or DP5 versus DP6.
2. Select the matching register address from `dcn_1_0_offset.h`.
3. Read the register when preserving unrelated fields is required.
4. Clear the target field with `*_MASK`, shift the new value by `*__SHIFT`, and write the combined register value.
5. For status, ack, pending, deadline-missed, taken, clear, or update bits, follow the hardware access semantics rather than assuming ordinary read/modify/write behavior.

The hardware sequencing implied by this chunk is sensitive around stream enable/disable, audio packet enable, infoframe update timing, HDMI double-buffer locking, DP link training/test pattern selection, scrambler and CRC controls, MST/MSE allocation updates, MSO secondary stream enabling, DSC enable, TMDS symbol programming, and lane/backend enable transitions. The generated macros do not encode valid value ranges, access type, self-clearing behavior, or required ordering.

## State And Persistence Behavior

The file itself stores no state and has no persistence. It describes fields inside display-engine registers whose values persist according to hardware behavior.

State represented by the DIG/AFMT/HDMI/TMDS groups includes audio-infoframe payloads, ISRC and MPEG metadata bytes, generic packet payloads, HDMI packet send state, double-buffer pending/taken/lock state, audio clock regeneration values and readbacks, IEC 60958 channel-status overrides, AFMT CRC and ramp-test state, packet transmission enables, backend/front-end source selection, lane enables, TMDS control characters, and AFMT clock enable/status.

State represented by the DP groups includes link-training-complete/status bits, embedded-panel mode, pixel encoding/depth/range, MSA colorimetry/misc/timing fields, stream enable/status/deferred-disable state, FIFO reset/overflow/ack state, DPHY training and test-pattern state, PRBS/scrambler/CRC configuration and results, secondary-data packet send/pending/deadline state, audio timing values, timestamps, MST stream allocation tables, MSE rate and SAT update state, MSO stream packet enables, DSC enable, debug fields, and MSA VBID readback/miscellaneous state.

Some fields are latched programming values, some are live status, some are sticky error/status bits, some are write-one-to-clear or write-one-to-ack, and some may be hardware- or firmware-updated during link training, hotplug handling, modeset, power management, suspend/resume, or ASIC reset. This header does not distinguish those access classes.

## Dependencies And Integration Points

The immediate dependency is the generated DCN 1.0 register ecosystem:

- `dcn_1_0_offset.h` supplies register addresses and base indices.
- `dcn_1_0_sh_mask.h` supplies field shifts and masks.
- AMDGPU display register helpers consume these names through local macros and read/modify/write wrappers.

Integration points include:

- DCN 1.0 resource construction, where stream encoders, link encoders, IRQ sources, GPIO/AUX/I2C, and hardware sequencing are wired to generated register names.
- HDMI/DVI output paths that program DIG5/DIG6 TMDS, generic packets, infoframes, AV mute, audio layout, ACR values, IEC 60958 metadata, and audio CRC/test state.
- DisplayPort output paths that program DP5/DP6 stream attributes, link training, pixel format, MSA/VBID metadata, scrambler/CRC/test features, secondary-data packets, audio timing, MST allocation, MSO state, and DSC.
- IRQ and diagnostic code that reads status, overflow, CRC, pending, deadline, and update bits.
- Reuse by later DCN-family code where register layouts are compatible enough to include the DCN 1.0 mask header.

The repeated instance names are important. `DIG5` pairs with `DP5`, and `DIG6` pairs with `DP6`, but callers must still select the correct physical stream/link encoder from resource tables; these macros do not encode topology or connector routing.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A wrong mask or shift compiles normally but can update the wrong bit, corrupt adjacent fields, or leave a required bit unchanged.

High-risk DIG/HDMI/AFMT fields include audio layout, channel enable, DP audio stream ID, ACR values, IEC 60958 channel-status bytes, generic packet send/line controls, HDMI double-buffer lock/clear, AV mute, infoframe update behavior, backend/frontend source selection, lane enable, and TMDS control-symbol settings. Errors here can produce missing or malformed audio, wrong HDMI packets, black screens, bad colors, failed DVI/HDMI modes, or compliance failures.

High-risk DP fields include stream enable and deferred-disable bits, pixel encoding/depth/range, MSA timing and VBID fields, DPHY training pattern/test/PRBS/scrambler controls, CRC controls/results, FIFO reset/overflow ack bits, secondary-data packet send/deadline bits, MST/MSE SAT programming, MSO secondary-packet enables, and DSC enable. Errors can appear as failed link training, flicker, blank displays, wrong colorimetry, lost MST streams, missing audio, bad CRC diagnostics, or incorrect DisplayPort compliance patterns.

Repeated generated layouts create copy/paste or generator drift risk. DP5 and DP6 should remain layout-compatible across many register families; a suffix mismatch or one-bit drift may affect only one output instance and can be hard to catch with build-only testing.

Chunk-boundary risk is explicit in this work item. The range begins after earlier DIG5 HDMI controls and ends before `DP6_DP_SEC_CNTL2` is complete. Any per-file summary should merge adjacent chunks before claiming full coverage of DIG5 or DP6.

Reserved semantics are not visible here. Some fields named status, pending, clear, update, taken, or deadline-missed likely have special read/write behavior. Generic register updates that preserve or write back status bits without respecting hardware rules can clear events, trigger sends, miss packet deadlines, or leave FIFOs in a bad state.

## Test Signals

Useful validation signals are mostly static generation checks plus hardware/display behavior:

- Build coverage for DCN 1.0 display resource, GPIO, IRQ, and modeset code that includes `dcn_1_0_sh_mask.h`.
- Generated-register consistency checks that every complete `REGISTER__FIELD__SHIFT` has the expected matching mask, masks align with shifts, and repeated DP5/DP6 and DIG5/DIG6 fields match where the hardware layout is intended to match.
- Diff/regeneration checks against AMD's authoritative DCN 1.0 register database and the companion `dcn_1_0_offset.h` addresses.
- HDMI/DVI tests on DIG5/DIG6-capable hardware covering modeset, AV mute, generic/infoframe packet sends, ACR/audio layout/channel programming, IEC 60958 metadata, audio CRC/ramp diagnostics, and suspend/resume.
- DisplayPort tests on DP5/DP6 covering link training, fast training, HBR2/test patterns, scrambler/PRBS/CRC diagnostics, stream enable/disable, pixel format/colorimetry/range, MSA/VBID programming, and FIFO overflow/reset paths.
- MST/MSO/DSC tests that exercise MSE SAT programming and status, rate updates, secondary-packet enables, DSC enable, and generic secondary-packet deadline/pending bits.
- Hotplug, HPD IRQ, runtime power-management, and full modeset stress tests that detect stale packet state, stuck pending bits, bad lane/backend enables, and incorrect restoration of display register state after reset or resume.

Regression symptoms from bad constants include blank display, flicker, link stuck at a lower rate, wrong colors or quantization, missing HDMI/DP audio, malformed infoframes, repeated hotplug/link-training failures, MST stream loss, CRC/test-pattern mismatches, or failures isolated to the fifth or sixth digital output instance.

## Cross-Chunk Notes

Earlier chunks of `dcn_1_0_sh_mask.h` define the beginning of the DIG5 HDMI/AFMT block and earlier DCN 1.0 display registers. Later chunks complete `DP6_DP_SEC_CNTL2` and continue through the remaining DP6 register families and subsequent DCN 1.0 hardware blocks. The final per-file document should present this source as a generated hardware register layout contract rather than as algorithmic driver logic.

### subset-b-001597: lines 39643-42087

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 39643-42087

## Scope And Purpose

This chunk is part of the generated AMD DCN 1.0 ASIC register field mask/shift header. It contains no executable C logic. Its purpose is to publish compile-time bitfield constants used by AMDGPU display code to compose and decode MMIO register values for DCN 1.0 display hardware.

The path lives under a local `ceph-client` source mirror, but this file is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

The range covers 2,134 preprocessor definitions: 1,059 `__SHIFT` constants and 1,075 mask constants. It begins at the tail of `DP6_DP_SEC_CNTL2` secondary-data packet fields, then covers these address blocks:

- `dce_dc_dcio_dcio_dispdec`: DP6 packet control tail, generic clock/reference controls, UNIPHY A-G link and crossbar controls, DCIO delays, pinstraps, DVO mapping, LVTMA panel power sequencing, backlight PWM, genlock/swaplock pads, DCIO clocks, OTG external-vsync routing, DCIO soft reset, DPHY lane selection, impedance calibration, DPCS interrupts, semaphores, and USB-C flip selection.
- `dce_dc_dcio_dcio_chip_dispdec`: generic GPIO, DVO data pins, DDC1-DDC6/VGA, sync, genlock/swaplock, HPD1-HPD6, panel-power GPIOs, pad strengths, AUX/I2C/DVO analog controls, I2S/SPDIF pins, AUX/HPD electrical controls, GPIO receive enables, and pull-up enables.
- `dce_dc_dcio_dcio_dac_dispdec`: four full-width reserved DAC macro control registers.
- Start of `dce_dc_dcio_dcio_uniphy0_dispdec`: `DCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED0` through `...RESERVED151`, each exposing one 32-bit reserved macro-control field.

This is a generated hardware ABI surface: the macro names and bit positions are the contract consumed by DCN register tables and field-access helper macros.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or storage objects in this chunk. The interface is the generated preprocessor naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit position.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for the same field.
- Matching register address macros come from the DCN 1.0 address headers, especially `dcn_1_0_offset.h` / `dcn_1_0_d.h` style headers in the same ASIC register tree.
- Display-core helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_WRITE`, `REG_READ`, `FD`, `FN`, and `SF`-style register-table macros consume these generated names indirectly.

Important macro groups in this chunk:

- `DP6_DP_SEC_CNTL2` through `DP6_DP_SEC_CNTL7`, `DP6_DP_DB_CNTL`, and `DP6_DP_MSA_VBID_MISC`: DP6 secondary packet send, pending, missed-deadline, line-number, active, double-buffer, MSA, and VBID override fields.
- `DC_GENERICA`, `DC_GENERICB`, `DC_REF_CLK_CNTL`, and `DC_GPIO_DEBUG`: generic output and reference/debug mux fields, including UNIPHY clock-selector fields and GPIO/DPRX debug selection.
- `UNIPHYA_LINK_CNTL` through `UNIPHYG_CHANNEL_XBAR_CNTL`: seven repeated UNIPHY link-control and channel-crossbar register families for pixel-valid reset, channel inversion, lane-stagger delay, HPD-gated link enable, per-channel crossbar source, and link enable.
- `DCIO_WRCMD_DELAY`, `DC_PINSTRAPS`, `DC_DVODATA_CONFIG`, `DCIO_CLOCK_CNTL`, `DIO_OTG_EXT_VSYNC_CNTL`, `DCIO_SOFT_RESET`, `DCIO_DPHY_SEL`, and `DCIO_USBC_FLIP_EN_SEL`: global DCIO timing, static strap, DVO, clock-gating/test clock, external-vsync routing, soft-reset, DPHY lane-map, and USB-C DisplayPort flip routing fields.
- `LVTMA_PWRSEQ_*` and `BL_PWM_*`: panel power sequencing, DIGON/SYNCEN/BLON override and state fields, power-up/down delays, PWM reference divider, PWM duty/period/fractional enable, and frame-start/register-lock controls.
- `DCIO_GSL_GENLK_PAD_CNTL` and `DCIO_GSL_SWAPLOCK_PAD_CNTL`: genlock/swaplock pad mask and flip-ready selection fields.
- `UNIPHY_IMPCAL_*`, `AUXP_IMPCAL`, `AUXN_IMPCAL`, and `DCIO_IMPCAL_CNTL*`: impedance-calibration enable/status/error/override/period/power-switch fields for UNIPHY links A-F and AUX P/N pads.
- `DCIO_DPCS_TX_INTERRUPT` and `DCIO_DPCS_RX_INTERRUPT`: DPCS TX A-G and RX A interrupt type, mask, and occurrence bits.
- `DCIO_SEMAPHORE0` through `DCIO_SEMAPHORE7`: request/grant bit ranges for DCIO hardware semaphores.
- `DC_GPIO_GENERIC_*`, `DC_GPIO_DVODATA_*`, `DC_GPIO_DDC*`, `DC_GPIO_SYNCA_*`, `DC_GPIO_GENLK_*`, `DC_GPIO_HPD_*`, `DC_GPIO_PWRSEQ_*`, `DC_GPIO_I2CPAD_*`, and `DC_GPIO_I2S_SPDIF_*`: GPIO mask/value/enable/readback register families for generic pins, DVO data/control/clock, DDC/AUX pads, sync, genlock, swaplock, hotplug, panel power, general I2C, and audio pins.
- `DC_GPIO_PAD_STRENGTH_*`, `DC_GPIO_I2CPAD_STRENGTH`, `DVO_STRENGTH_CONTROL`, `DVO_VREF_CONTROL`, `DVO_SKEW_ADJUST`, `DC_GPIO_I2S_SPDIF_STRENGTH`, `DC_GPIO_AUX_CTRL_0`, `DC_GPIO_AUX_CTRL_1`, and `DC_GPIO_AUX_CTRL_2`: pad drive-strength, slew, spike rejection, comparator, bias, voltage-reference, and skew tuning fields.
- `DC_GPIO_TX12_EN`, `DC_GPIO_RXEN`, and `DC_GPIO_PULLUPEN`: grouped transmit, receive, and pull-up enables for GPIO, sync, HPD, genlock, swaplock, and panel-power pins.
- `DAC_MACRO_CNTL_RESERVED*` and `DCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED*`: full-register reserved fields that preserve generated register-map coverage even when field semantics are not public here.

## Control Flow

This chunk has no runtime control flow. Each line is a preprocessor definition, so all behavioral sequencing happens in consumer code that reads and writes MMIO registers.

DCN 1.0 display-core consumers in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn10/irq_service_dcn10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_factory_dcn10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_translate_dcn10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_translate_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.c`

Representative runtime flows enabled by this macro vocabulary:

- GPIO translation maps logical HPD, DDC, generic, sync, and panel-power pins to `DC_GPIO_*_A`, `DC_GPIO_*_EN`, `DC_GPIO_*_Y`, and related mask fields. For example, `hw_translate_dcn10.c` switches over DCN GPIO register offsets and returns the appropriate `DC_GPIO_HPD_A__DC_GPIO_HPDn_A_MASK` or `DC_GPIO_DDCn_A__...CLK/DATA..._MASK` bits.
- Panel-control code shared across DCE/DCN generations uses `LVTMA_PWRSEQ_CNTL`, `LVTMA_PWRSEQ_STATE`, `LVTMA_PWRSEQ_REF_DIV`, `BL_PWM_CNTL`, `BL_PWM_CNTL2`, `BL_PWM_PERIOD_CNTL`, and `BL_PWM_GRP1_REG_LOCK` fields to program backlight duty cycle, PWM period, PWM enable, update locks, and panel power state.
- Link-encoder and PHY bring-up code uses DCIO soft-reset and UNIPHY fields to reset individual UNIPHY/DSYNC blocks, configure lane inversion/crossbar routing, choose link-enable behavior, and manage signal-routing side effects.
- Interrupt service code consumes DPCS and display-related generated bit names through register tables so interrupt type, mask, occurrence, ACK, and routing code can refer to fields symbolically rather than using raw constants.
- Modeset/link paths can use DP6 packet and MSA/VBID fields when enabling secondary-data packet scheduling, PPS/GSP transmission, line-numbered packet sends, and double-buffered packet updates for the sixth DP stream.
- Connector sideband paths use DDC/AUX GPIO and pad-control fields when switching pads between AUX and DDC modes, configuring polarity, pull-ups, receive enables, pad strength, spike rejection, and comparator/bias behavior.

Because the header is declarative, it does not protect callers from bad sequencing. Consumers must order writes around reset, link enable, impedance calibration, panel-power delays, PWM update locks, HPD/DDC state transitions, interrupt clears, and semaphores.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. It describes hardware MMIO state.

The represented hardware state includes:

- DP6 packet-scheduler state: pending sends, active sends, line numbers, missed-deadline status, any-line sends, PPS, double-buffer pending/taken/lock/disable, and MSA/VBID overrides.
- DCIO and PHY state: generic clock outputs, reference clock output selection, debug muxes, UNIPHY link enable/reset/channel mapping/inversion, DPHY lane mapping, write-command delays, USB-C flip routing, soft-reset bits, and semaphore grants.
- Calibration state: UNIPHY and AUX impedance calibration enables, status bits, error/ack bits, measured values, step delays, override values, power-switch controls, and calibration intervals.
- Panel and backlight state: LVTMA power-sequence target/current state, DIGON/SYNCEN/BLON controls and polarities, delay counters, PWM duty/period/reference divider/fractional enable, and frame-start lock/update state.
- Connector GPIO state: mask, pull-up/pull-down, receive, output value, output enable, and readback bits for DDC, HPD, sync, generic, DVO, I2C, I2S/SPDIF, genlock, swaplock, and panel-power pins.
- Pad electrical state: drive strengths, slew settings, spike rejection, comparator selection, bias/reference enables, voltage reference, skew adjustment, AUX/DDC pad mode, and audio-pin strength.
- Reserved DAC and UNIPHY macro-control state: full-width register regions that are represented for address-map completeness but have no field semantics in this generated header chunk.

Field lifetime is hardware-specific and not encoded here. Some bits are persistent configuration until modeset, suspend/resume, power-gating, reset, or a later write. Others are read-only status, write-one-to-clear status, self-clearing request bits, sticky interrupt occurrence bits, hardware-latched strap/readback bits, or values sampled by firmware/PHY logic. Names such as `*_PENDING`, `*_TAKEN`, `*_LOCK`, `*_SOFT_RESET`, `*_CALOUT_ERROR_AK`, `*_INT_OCCUR`, `*_GNT`, `*_RECV`, `*_Y`, and `*_PWRSEQ_DONE` are semantic hints only; access type and side effects must come from the hardware specification and caller context.

## Dependencies And Integration Points

This chunk depends on the generated DCN 1.0 register-header set. It is useful only with the matching address and enum headers under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/`, plus display-core register accessor macros.

Direct include points for `dcn_1_0_sh_mask.h` found in this tree are:

- `display/dc/irq/dcn10/irq_service_dcn10.c`
- `display/dc/gpio/dcn10/hw_factory_dcn10.c`
- `display/dc/gpio/dcn10/hw_translate_dcn10.c`
- `display/dc/gpio/dcn20/hw_translate_dcn20.c`
- `display/dc/resource/dcn10/dcn10_resource.c`

Primary integration areas:

- DCN10/DCN20 GPIO factory and translation layers for logical-to-MMIO mapping of HPD, DDC, sync, generic GPIO, and panel-power pins.
- DCN10 resource construction, where generated `mm` register addresses and field masks populate hardware block register tables.
- IRQ service tables for display and DCIO interrupt mask/status/ack fields.
- Shared panel-control code (`display/dc/dce/dce_panel_cntl.*` and later DCN panel-control implementations) that uses this same generated field vocabulary for backlight and panel power control.
- Link encoder and PHY code in later DCN generations use analogous `DCIO_SOFT_RESET`, `UNIPHY*_LINK_CNTL`, and crossbar fields, so this chunk is also a reference point for generation-to-generation compatibility of DCIO field names.
- Matching address headers such as `dcn_1_0_offset.h` / `dcn_1_0_d.h` provide register offsets; matching enum headers provide symbolic field values where fields are not simple booleans.

The file is generated, so the real upstream dependency is the ASIC register database and generator that produced the DCN 1.0 header family. Hand-edited divergence from sibling address/mask/enum headers is a build-time and hardware-behavior risk.

## Risks And Edge Cases

- Masks and shifts are hardware ABI. A one-bit error can compile successfully while programming the wrong GPIO pin, link lane, reset bit, interrupt mask, backlight value, or calibration control.
- This range contains many repeated instance families: UNIPHY A-G, DDC1-DDC6 plus VGA, HPD1-HPD6, semaphores 0-7, and reserved UNIPHY0 macro registers 0-151. Instance drift is easy to miss in review because names and masks differ only by small suffixes and bit positions.
- `*_MASK_MASK` names are intentional generated artifacts for fields whose logical field name ends in `MASK`. They are awkward but must not be simplified without changing all consumers.
- Several fields are sequencing-sensitive: `DCIO_SOFT_RESET`, `UNIPHY*_LINK_ENABLE`, impedance-calibration `ENABLE`/`OVERRIDE`, `BL_PWM_GRP1_REG_LOCK`, `DP6_DP_DB_LOCK`, DPCS interrupt occurrence bits, and semaphore request/grant fields can cause hangs, missed interrupts, or stale state if handled as ordinary read/write bits.
- GPIO families mix output value (`*_A`), output enable (`*_EN`), readback (`*_Y`), receive-enable, pull-up/pull-down, and mask semantics. Confusing these can break HPD detection, EDID/DDC transactions, AUX/DDC pad mode, panel power, or genlock/swaplock signaling.
- Backlight and panel-power fields affect visible hardware state. Wrong PWM period/duty, reference divider, BLON/DIGON/SYNCEN polarity, or delay programming can produce black panels, flicker, unsafe power sequencing, or resume failures.
- DDC/AUX pad electrical fields affect signal integrity. Incorrect slew, spike rejection, comparator, bias, polarity, pull-up, or drive-strength settings may work on one board and fail on long cables, marginal connectors, or Type-C/DP-alt-mode paths.
- Reserved DAC and UNIPHY macro-control registers are exposed as full-width masks without semantic protection. Consumers should treat them as generated coverage, not as permission to write arbitrary values.
- The chunk boundary is not semantic. It starts after earlier `DP6_DP_SEC_CNTL2` shift definitions and ends in the middle of the `DCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED*` sequence. The final per-file report must reconcile neighboring chunks for whole-file completeness.

## Test Signals

Useful validation is mainly compile-time plus hardware display behavior:

- Build AMDGPU display code with DCN 1.0 support enabled; missing or renamed macros should fail in DCN10 IRQ, GPIO, resource, panel-control, and register-table code.
- Compare this generated range against the matching DCN 1.0 address headers and adjacent DCN generations (`dcn_2_1_0_sh_mask.h`, `dcn_3_2_0_sh_mask.h`) to catch generation or instance-index drift in repeated DCIO/GPIO families.
- Exercise DCN10 hardware modesets across all available connectors and PHYs: DP/HDMI link bring-up, link disable/enable, suspend/resume, GPU reset recovery, multi-display, and Type-C/DP-alt-mode flip behavior where available.
- Validate connector sideband behavior: HPD connect/disconnect, HPD storm handling, DDC EDID reads on DDC1-DDC6/VGA, AUX/DDC pad mode switching, and GPIO readback/enable transitions.
- Validate panel/backlight behavior on eDP/LVDS-style panels: PWM duty and period programming, brightness changes, power on/off, suspend/resume, DIGON/BLON sequencing, and absence of flicker or black-screen regressions.
- Validate interrupt behavior for DPCS TX/RX and related display paths: masks, occurrence bits, ACK/clear handling, and lack of stuck interrupts after hotplug, link training, or modeset.
- Check negative signals in kernel logs and user-visible behavior: EDID read failures, HPD flapping, link-training loops, black screen, backlight stuck on/off, missed vblank/page events, display underflow, AUX errors, resume failures, and interrupt storms.

### subset-b-001598: lines 42088-44705

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 42088-44705

## Purpose

This chunk is part of the generated AMDGPU DCN 1.0 register field shift/mask header. It contains no executable logic; it publishes preprocessor constants that describe packed bit fields in DCN 1.0 DCIO, ComboPHY common, ComboPHY transmitter, and ComboPHY PLL registers.

Each field is represented by the standard generated pair:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit position.
- `REGISTER__FIELD_MASK` gives the already-positioned bit mask.

The constants in this chunk are paired with register address definitions from `dcn_1_0_offset.h`. Consumers use both files through AMD display register helpers and structures, so the chunk is a hardware-layout contract for link encoder, PHY, PLL, clock-source, BIOS-table, and display resource code rather than a standalone software module.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, or runtime APIs in this line range. The macro namespace is the API surface.

Major macro groups in this chunk are:

- Tail of `DCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED152` through `RESERVED159`: full-width `UNIPHY_MACRO_CNTL_RESERVED` masks for the end of UNIPHY0's reserved macro-control window.
- `DC_COMBOPHYCMREGS0_*`, `DC_COMBOPHYCMREGS1_*`, and `DC_COMBOPHYCMREGS2_*`: common ComboPHY register fields for PHY instances 0, 1, and 2. These include fuse-valid and fuse payload fields (`COMMON_FUSE1` through `COMMON_FUSE3`), nominal margin/de-emphasis defaults (`COMMON_MAR_DEEMPH_NOM`), lane power management (`COMMON_LANE_PWRMGMT`), transmitter common control (`COMMON_TXCNTRL`), lane resets (`COMMON_LANE_RESETS`), impedance/calibration override fields (`COMMON_ZCALCODE_CTRL`), and reserved display RFU registers.
- `DC_COMBOPHYTXREGS0_*`, `DC_COMBOPHYTXREGS1_*`, and the start of `DC_COMBOPHYTXREGS2_*`: per-lane transmitter command bus fields. For each lane, `CMD_BUS_TX_CONTROL_LANEn` exposes `tx_pwr`, `tx_pg_en`, and `tx_rdy`; `MARGIN_DEEMPH_LANEn` exposes `txmarg_sel`, `deemph_sel`, and `tx_margin_en`; `CMD_BUS_GLOBAL_FOR_TX_LANEn` exposes link and PCS controls such as `twosym_en`, `link_speed`, `gang_mode`, `max_linkrate`, `pcs_freq`, `pcs_clken`, `pcs_clkdone`, `pll1_always_on`, `rdclk_div2_en`, `tx_boost_adj`, `tx_boost_en`, and `tx_binary_ron_code_offset`. Each lane also has `TX_DISP_RFU0` through `TX_DISP_RFU12` full-width reserved fields.
- `DC_COMBOPHYPLLREGS0_*` and `DC_COMBOPHYPLLREGS1_*`: ComboPHY PLL tuning, calibration, observation, and wrapper fields. These define frequency-control words (`fcw*_frac` and `fcw*_int`), coarse/fine bandwidth and bias controls, calibration enable/delay/range/test fields, loop-control fields, voltage regulator configuration, observation outputs, DFT output, and wrapper power/reset/lock/status controls.
- `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED159` and `DCIO_UNIPHY2_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED159`: full-width reserved macro-control windows for additional UNIPHY instances. These keep generated address/mask coverage complete even when most fields are not named at this level.

The range ends in the middle of `DC_COMBOPHYTXREGS2_CMD_BUS_GLOBAL_FOR_TX_LANE3`, after the `pll1_always_on` shift definition. Later chunks continue that register and the rest of the ComboPHY instance 2 transmitter/PLL definitions.

## Control Flow

This header chunk has no runtime control flow. It is a collection of `#define` statements.

Runtime control flow appears in consumers that:

1. Select a register address from `dcn_1_0_offset.h`, such as `mmDC_COMBOPHYCMREGS0_COMMON_FUSE1`, `mmDC_COMBOPHYTXREGS0_CMD_BUS_TX_CONTROL_LANE0`, `mmDC_COMBOPHYPLLREGS0_FREQ_CTRL0`, or `mmDCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED0`.
2. Use a matching `*_MASK` and `*__SHIFT` macro from this header to extract or insert a field.
3. Read, modify, and write the MMIO register through AMDGPU/display register helper macros or through structures initialized in DC resource construction.

Sequencing-sensitive runtime operations represented by these fields include PHY lane power transitions, lane resets, link-rate and PCS clock programming, transmitter margin/de-emphasis setup, PLL frequency programming, PLL calibration, PLL reset/power transitions, and lock/status polling. The header does not encode required ordering, delays, access permissions, or read-only versus write-only behavior; those rules live in display, BIOS, firmware, and hardware programming code.

## State And Persistence Behavior

The file stores no software state and has no persistence behavior. It describes state located in hardware registers.

The represented hardware state includes eFuse-derived PHY calibration values, PHY lane power-gating controls, lane reset bits, transmitter power/readiness state, per-lane electrical margin and de-emphasis settings, link-speed and PCS clock controls, PLL frequency-control words, PLL bandwidth/bias/calibration controls, PLL lock and observation status, and large reserved UNIPHY and RFU register windows.

Persistence is hardware-defined. Some fields are stable configuration values until a later driver/firmware write, some are sampled fuse or status values, some may change as hardware calibration or PLL lock progresses, and reset/power-gating fields may be lost or reinitialized across display reset, ASIC reset, suspend/resume, runtime power transitions, or BIOS/firmware transmitter-control calls. The generated masks themselves do not document volatility or clear-on-read/write-one-to-clear behavior.

## Dependencies And Integration Points

Primary paired address dependency:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h`

Direct DCN 1.0 include point:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.c` includes both `dcn/dcn_1_0_offset.h` and `dcn/dcn_1_0_sh_mask.h`.

Important integration paths:

- `dcn10_resource.c` builds DCN 1.0 resource tables and maps `TRANSMITTER_UNIPHY_A` through `TRANSMITTER_UNIPHY_D` to PHY instances. These transmitter/PHY identities align with the generated UNIPHY and ComboPHY instance namespaces in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_link_encoder.*` handles DCN 1.0 link encoder behavior, including UNIPHY transmitter assignment, lane mapping, resets, and link enablement. It consumes the same generated register infrastructure even when higher-level macros hide individual field names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_clock_source.h` defines DCN 1.0 clock-source register and mask lists. Those lists are initialized from the generated address and shift/mask headers in `dcn10_resource.c`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/bios/command_table.c` provides BIOS transmitter and PHY programming calls for UNIPHY-backed outputs. The generated register fields here describe the MMIO-level state that BIOS/driver sequences must leave coherent.
- Display link code maps encoder IDs and transmitters through `TRANSMITTER_UNIPHY_*` values in files such as `display/dc/link/link_factory.c`, `display/dc/core/dc_resource.c`, and related DIO/HWSS paths.

Equivalent or near-equivalent definitions also appear in generated DCE 12.0 and later DCN/DPCS headers, showing that these PHY bit layouts are part of AMD's generated register database and evolve across ASIC generations.

Although the source tree is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It has no Ceph filesystem protocol behavior, no distributed filesystem data flow, and no persistent storage semantics.

## Risks And Edge Cases

The main risk is silent display hardware misprogramming. A bad mask or shift can compile cleanly while writing the wrong PHY, PLL, or lane-control bits.

High-risk areas include:

- ComboPHY PLL fields: wrong frequency-control word, bandwidth, bias, calibration, reset, or wrapper-control masks can prevent PLL lock, produce unstable pixel/link clocks, break modesets, or cause intermittent link training failures.
- Transmitter lane controls: incorrect `tx_pwr`, `tx_pg_en`, `tx_rdy`, link speed, PCS clock, gang-mode, boost, margin, or de-emphasis masks can leave lanes powered down, fail readiness polling, train at the wrong rate, or violate DP/HDMI electrical requirements.
- Lane reset and power-management fields: incorrect reset or power gating masks can wedge a PHY lane, race link enablement, or cause resume failures after display power transitions.
- Fuse and calibration fields: mis-decoding `COMMON_FUSE*` or `ZCALCODE_CTRL` can apply wrong termination, impedance, CDR, or calibration defaults. These bugs can be board- or cable-sensitive.
- Reserved/RFU registers: many fields are full-width placeholders. Treating them as generally writable is risky because reserved registers may have undocumented side effects; generated masks only describe bit positions, not safe programming policy.
- Chunk boundary risk: the assigned range starts after earlier UNIPHY0 reserved definitions and stops mid-register in ComboPHYTXREGS2. The merge lane must not interpret this chunk as a complete module boundary.

## Test Signals

Useful validation signals are mostly compile-time, register-database, and hardware-integration oriented:

- Build coverage for DCN 1.0 display paths that include `dcn_1_0_offset.h` and `dcn_1_0_sh_mask.h`.
- Static comparison of every `*_MASK` and `*__SHIFT` pair in this chunk against AMD's register database and the matching addresses in `dcn_1_0_offset.h`.
- Modeset and link-training tests on DCN 1.0 hardware for all supported UNIPHY transmitters and lane counts, including DP, eDP, HDMI, and any board-specific PHY routing.
- PLL programming tests that verify lock status, stable pixel clocks, clock-source selection, deep-color pixel-clock behavior, and repeated modeset changes.
- Suspend/resume, runtime power management, and hotplug cycles that exercise PHY power gating, lane reset, transmitter readiness, and BIOS/driver reinitialization ordering.
- Electrical/link margin validation, especially across different cables, link rates, de-emphasis/margin settings, and multi-lane configurations.
- Register readback or debug tooling that confirms writes affect only intended fields and that reserved/RFU registers are not touched by normal programming paths.

Regression symptoms from incorrect constants include no display after modeset, intermittent DP link training failure, HDMI/eDP output instability, missing or unstable pixel clock, PLL lock timeouts, lanes stuck in reset or power-down, display corruption at specific link rates, resume failures, and hardware status polling loops that never observe the expected ready or lock bit.

## Cross-Chunk Notes

Earlier chunks of `dcn_1_0_sh_mask.h` define the preceding DCN display, clocking, DIO, and UNIPHY0 fields. This chunk continues the DCIO/ComboPHY register map for PHY instances 0 through 2. Later chunks complete `DC_COMBOPHYTXREGS2_CMD_BUS_GLOBAL_FOR_TX_LANE3` and continue subsequent ComboPHY/UNIPHY instances and remaining DCN 1.0 register field definitions. The final per-file research document should treat the full header as one generated DCN 1.0 register-layout contract.

### subset-b-001599: lines 44706-47394

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 44706-47394

Chunk: `subset-b-001599`
Covered source range: lines 44706-47394 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h`

## Purpose

This chunk is part of the generated AMD DCN 1.0 register shift/mask header. It contains no executable driver code; it exports C preprocessor constants that describe bit positions and positioned masks for display PHY, legacy VGA, and Azalia/HD-audio indexed registers.

The range begins at the tail of the `DC_COMBOPHYTXREGS2_MARGIN_DEEMPH_LANE3` block, then covers complete mask groups for COMBOPHY PLL instance 2, UNIPHY3 reserved registers, COMBOPHY common/TX/PLL instance 3, ZCAL, legacy VGA sequencer/CRT/graphics/attribute indexed registers, Azalia F2 output codec and pin blocks, audio descriptors, sink-info fields, Azalia CRC result blocks, and the beginning of the Azalia F2 input endpoint block. It ends after the `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_HBR__HBR_ENABLE__SHIFT` macro, before the matching HBR masks and later input-pin fields.

Every field follows the generated naming contract:

- `REGISTER__FIELD__SHIFT` is the field's least-significant bit position.
- `REGISTER__FIELD_MASK` is the already-positioned mask for that field.

The companion `dcn_1_0_offset.h` header provides the matching `mm*` and `ix*` register offsets. This file provides the per-register field layout used by AMDGPU Display Core register helpers.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or storage objects in this slice. The exported API is the macro namespace itself. This chunk contains 2,063 `#define` directives, 19 address-block comments, and 499 register comments in the requested range.

Major macro families:

- `DC_COMBOPHYTXREGS2_*`: the chunk starts in the final instance-2 lane-3 TX tuning/control area. `CMD_BUS_GLOBAL_FOR_TX_LANE3` defines link-speed, lane-gang, PCS clock, PLL always-on, boost, and RON offset fields. `TX_DISP_RFU0_LANE3` through `TX_DISP_RFU12_LANE3` expose full-width reserved-for-future-use payloads.
- `DC_COMBOPHYPLLREGS2_*`: PLL instance 2 frequency-control, bandwidth, calibration, loop, regulator, observation, DFT, and wrapper-control fields. These include fractional/integer frequency words, denominator/slew values, refclk/VCO/divider and spread-spectrum controls, loop bandwidth parameters, calibration disables/ratios, feedback and clock selection controls, regulator configuration, lock-detection observation state, digital observation selectors, and full-width DFT data.
- `DCIO_UNIPHY3_UNIPHY_MACRO_CNTL_RESERVED0..159`: a large reserved UNIPHY3 macro-control aperture. Each register exposes a single full-width `UNIPHY_MACRO_CNTL_RESERVED` field with shift `0x0` and mask `0xFFFFFFFFL`.
- `DC_COMBOPHYCMREGS3_COMMON_*`: common instance-3 display PHY fields. Fuse registers expose validity and impedance/current/override state; `COMMON_MAR_DEEMPH_NOM` carries nominal margin/de-emphasis values; `COMMON_LANE_PWRMGMT`, `COMMON_TXCNTRL`, `COMMON_TMDP`, `COMMON_LANE_RESETS`, and `COMMON_ZCALCODE_CTRL` cover lane power, common TX, TMDS/DP mode, resets, and impedance calibration code controls. `COMMON_DISP_RFU1..7` are full-width reserved display registers.
- `DC_COMBOPHYTXREGS3_*`: per-lane TX controls for lanes 0-3. Each lane has `CMD_BUS_TX_CONTROL_LANE<n>` for power/power-gate/ready bits, `MARGIN_DEEMPH_LANE<n>` for margin and de-emphasis selection, `CMD_BUS_GLOBAL_FOR_TX_LANE<n>` for link/PCS/boost/global lane settings, and `TX_DISP_RFU0..12_LANE<n>` reserved payloads.
- `DC_COMBOPHYPLLREGS3_*`: the instance-3 copy of the PLL frequency, bandwidth, calibration, loop, regulator, observation, DFT, and wrapper-control layout used for instance 2.
- `ZCAL_MACRO_CNTL_RESERVED0..4`, `COMP_EN_CTL`, `COMP_EN_DFX`, and `ZCAL_FUSES`: Z-calibration reserved registers plus comparator-enable and fuse-derived calibration fields. These drive or report impedance/reference calibration behavior shared by the display PHY.
- `SEQ00..SEQ04`, `CRT00..CRT22`, `GRA00..GRA08`, and `ATTR00..ATTR14`: legacy VGA indexed register fields for sequencer reset/clock/map/font/memory mode, CRT timing/cursor/display-start/sync/overflow/underline/mode-control fields, graphics controller set/reset/plane/rotate/mode/misc/compare/mask fields, and attribute controller palette/mode/overscan/plane/pel-pan/color-select fields.
- `AZALIA_F2_CODEC_CONVERTER_*`: output converter format, stream/channel ID, digital converter status/control, stripe, ramp rate, GTC embedding, audio widget capabilities, supported size/rates, and stream-format fields.
- `AZALIA_F2_CODEC_PIN_*`: output pin controls and parameters, including connection-list response, widget control, unsolicited response, pin sense, default configuration words, speaker/channel allocation, down-mix info, audio descriptor selection/data, multichannel enable groups and individual channels, lip-sync, HBR, sink-info selection, codec channel-status overrides, pin association, digital output status, LPIB snapshots, coding type, format-change reporting, wireless display identification, remote keepalive, pin widget capabilities, pin capabilities, and connection-list length.
- `AUDIO_DESCRIPTOR0..13`: audio descriptor slots with maximum-channel count, sample-rate mask, and PCM/compressed coding-type capability bits.
- `AZALIA_F2_CODEC_PIN_CONTROL_MANUFACTURER_ID`, `PRODUCT_ID`, `SINK_DESCRIPTION_LEN`, `PORTID0`, `PORTID1`, and `SINK_DESCRIPTION0..17`: sink identity and description words for the Azalia endpoint sink-info block.
- `AZALIA_INPUT_CRC0_CHANNEL0..7`, `AZALIA_INPUT_CRC1_CHANNEL0..7`, `AZALIA_CRC0_CHANNEL0..7`, and `AZALIA_CRC1_CHANNEL0..7`: full-width 32-bit CRC result fields for input and output/general Azalia diagnostic paths.
- `AZALIA_F2_CODEC_INPUT_CONVERTER_*` and `AZALIA_F2_CODEC_INPUT_PIN_*`: the beginning of the F2 input endpoint converter and input-pin field layout. This includes input converter format, stream/channel ID, digital converter state, input widget capabilities, supported sizes/rates, input pin widget control, unsolicited response, pin sense, default configuration, channel allocation, even-numbered multichannel enables 0/2/4/6, and the first two HBR shift fields. The HBR masks and subsequent odd-channel/input status fields are outside this chunk.

## Control Flow

This header slice has no runtime control flow. It is a linear sequence of `#define` directives inside the larger DCN 1.0 include guard.

Effective runtime flow appears in consumers that:

1. choose a register offset from `dcn_1_0_offset.h`, such as `mmDC_COMBOPHYPLLREGS3_FREQ_CTRL0`, `mmCOMP_EN_CTL`, `ixSEQ00`, `ixCRT00`, `ixAZALIA_F2_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR`, `ixAUDIO_DESCRIPTOR0`, or `ixAZALIA_F2_CODEC_INPUT_PIN_CONTROL_HBR`;
2. access the corresponding MMIO register directly or through the correct indexed-register window for VGA/Azalia endpoint blocks;
3. extract fields with `(value & REGISTER__FIELD_MASK) >> REGISTER__FIELD__SHIFT`, or clear and insert fields using the same pair;
4. write back only when the hardware register is writable and the caller is in the correct display, PHY, VGA, or HD-audio programming sequence.

The macros do not encode sequencing. External code must handle PLL programming order, calibration enable/polling, lane reset release, link training, display audio stream setup, unsolicited-response delivery, LPIB snapshot locking, CRC latch semantics, and legacy VGA indexed-register access rules.

## State And Persistence Behavior

The header has no mutable software state and persists only as compiled constants.

The fields describe hardware state in DCN 1.0 display PHY, ZCAL, VGA compatibility, and Azalia display-audio blocks. Important hardware state represented here includes:

- COMBOPHY PLL frequency, bandwidth, loop, calibration, regulator, lock-observation, and DFT/debug state for PHY instances 2 and 3;
- UNIPHY3 reserved macro-control state, retained in the generated map for register database completeness;
- COMBOPHY instance-3 fuse, impedance, lane power, common TX, TMDS/DP mode, reset, ZCAL code, lane TX power, margin, de-emphasis, PCS, boost, and reserved lane state;
- ZCAL comparator enable, DFX, and fuse-derived calibration values;
- legacy VGA sequencer, CRT controller, graphics controller, and attribute controller indexed state used by compatibility display paths;
- Azalia F2 output converter and pin state, including audio format, channel/stream IDs, digital converter status, pin sense, unsolicited-response state, sink capability data, channel allocation, multichannel/HBR controls, LPIB snapshots, coding type, format-change status, and remote keepalive;
- Azalia sink identity/description and audio descriptor payloads;
- full-width Azalia input/output CRC result snapshots;
- partial Azalia F2 input converter/input-pin state at the end of the slice.

Persistence depends on register class. Some fields are read-only capability/status values, some are writable controls, some are debug selector/readback values, and some are reserved or fuse-derived. Values may be reset or reinitialized by display modeset, link retraining, audio stream setup/teardown, hot-plug handling, runtime power management, suspend/resume, GPU reset, display core reset, firmware/BIOS initialization, or full device power loss.

## Dependencies And Integration Points

The direct generated companion is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h`

Examples of matching offsets in that companion header include:

- `mmDCIO_UNIPHY3_UNIPHY_MACRO_CNTL_RESERVED0`
- `mmDC_COMBOPHYCMREGS3_COMMON_FUSE1`
- `mmDC_COMBOPHYTXREGS3_CMD_BUS_TX_CONTROL_LANE0`
- `mmDC_COMBOPHYPLLREGS3_FREQ_CTRL0`
- `mmCOMP_EN_CTL`
- `mmZCAL_FUSES`
- `ixSEQ00`
- `ixCRT00`
- `ixAZALIA_F2_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR`
- `ixAUDIO_DESCRIPTOR0`
- `ixAZALIA_F2_CODEC_INPUT_PIN_CONTROL_HBR`

The local DCN 1.0 resource code includes both the offset and mask headers in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.c`. The broader integration point is AMDGPU Display Core for Vega/DCN 1.0 hardware, where generated register constants feed register-helper macros and hardware block constructors.

Functional integration areas include:

- display PHY and link encoder paths that program COMBOPHY PLLs, lane power, resets, TX margin/de-emphasis, boost, and PCS behavior for DisplayPort/HDMI/DVI signaling;
- ASIC initialization, power management, and resume paths that preserve or restore PHY, ZCAL, and reserved register state;
- debug and validation paths that use observation, DFT, lock, ZCAL, and CRC readback fields;
- legacy VGA compatibility paths that access indexed sequencer/CRT/graphics/attribute registers;
- display audio and HDA/Azalia paths that expose GPU HDMI/DP audio converter/pin capabilities, sink descriptions, audio descriptors, channel allocation, HBR support, hot-plug/pin-sense events, and stream-position snapshots.

Although the repository root is named `ceph-client`, this chunk is AMDGPU kernel display-driver register metadata. It has no distributed filesystem protocol behavior and no Ceph persistence semantics.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. Incorrect masks or shifts compile cleanly but can read the wrong bit, fail to update the intended field, or corrupt adjacent fields in packed hardware registers.

This range is highly repetitive. COMBOPHY instance 2 and 3 PLL layouts should remain structurally aligned where the hardware database says they match; TX lane 0-3 layouts must preserve lane numbers; Azalia multichannel fields repeat by channel; VGA indexed registers reuse short historical register names. A generated prefix, instance, channel, or lane mismatch can look plausible in review while targeting the wrong hardware path.

Reserved and RFU fields require caution. `DCIO_UNIPHY3_UNIPHY_MACRO_CNTL_RESERVED*`, COMBOPHY `*_RFU*`, `ZCAL_MACRO_CNTL_RESERVED*`, and similar full-width masks exist for register-map completeness, not as permission for arbitrary writes. Writing undocumented/reserved apertures can affect board-specific or ASIC-internal behavior.

PHY and PLL fields are timing and board dependent. Bad frequency-control, loop-bandwidth, regulator, calibration, impedance, margin, de-emphasis, reset, or lane-power values can cause link-training failures, black screens, intermittent DisplayPort/HDMI instability, high error rates, or suspend/resume regressions without obvious software exceptions.

Legacy VGA fields are narrow indexed registers represented in a 32-bit macro namespace. Callers must respect VGA indexed-register addressing and historical side effects; treating these as ordinary flat 32-bit display registers can corrupt timing, cursor, blanking, graphics mode, or palette/attribute state.

Azalia output and input fields are externally visible through the audio stack. Wrong format, stream ID, channel allocation, HBR, descriptor, sink-info, pin-sense, or unsolicited-response masks can produce missing HDMI/DP audio devices, wrong channel layouts, bad sample-rate/coding advertisements, spurious hot-plug events, failed HBR audio, or unstable playback-position reporting.

CRC fields are full-width diagnostic readbacks. They should be treated as result snapshots, not bitfield controls, despite following the same generated mask/shift naming pattern.

The chunk boundaries are partial. The first line is a single tail mask for `DC_COMBOPHYTXREGS2_MARGIN_DEEMPH_LANE3`; the rest of that register is in the previous chunk. The final two macros start `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_HBR`; its masks and following input-pin fields are in the next chunk.

## Test Signals

Useful validation signals include:

- kernel build coverage for DCN 1.0/Vega display paths that include `dcn_1_0_sh_mask.h`;
- generated-header consistency checks that each `REGISTER__FIELD_MASK` has the matching `REGISTER__FIELD__SHIFT`, with this chunk's first and last boundary splits reconciled at file-merge time;
- diffs against the authoritative DCN 1.0 register database for COMBOPHY, UNIPHY3, ZCAL, VGA, and Azalia blocks;
- cross-checks that every mask macro is paired with the expected offset name in `dcn_1_0_offset.h`;
- instance and lane consistency checks comparing `DC_COMBOPHYPLLREGS2` with `DC_COMBOPHYPLLREGS3`, lane 0-3 TX layouts in `DC_COMBOPHYTXREGS3`, and repeated Azalia multichannel field shapes;
- hardware modeset and link-training tests across ports that exercise PHY instances 2 and 3, including DisplayPort and HDMI/DVI where available;
- PLL and ZCAL validation that verifies requested clocks, lock/observation fields, calibration behavior, impedance calibration, and stable link output after suspend/resume and runtime power transitions;
- legacy VGA smoke tests for early console, mode switching, cursor, blanking, palette/attribute behavior, and resume on DCN 1.0 hardware or emulation;
- HDMI/DisplayPort audio tests across stereo, multichannel, compressed formats, HBR, sample-rate changes, stream enable/disable cycles, and sink re-enumeration;
- hot-plug and pin-sense tests that verify unsolicited response tags/enables, presence-detect state, audio device creation/removal, and sink capability refresh;
- ELD/sink-capability checks that confirm `AUDIO_DESCRIPTOR*`, manufacturer/product IDs, port IDs, sink descriptions, speaker allocation, and channel allocation decode as expected;
- LPIB snapshot and playback-position tests under wraparound and stream restarts;
- CRC diagnostic tests that read `AZALIA_INPUT_CRC*` and `AZALIA_CRC*` channels under known audio/display traffic.

Regression symptoms from bad constants include missing or unstable display links, link-training failures isolated to a PHY instance or lane, black screens after resume, wrong VGA compatibility output, missing HDMI/DP audio, incorrect advertised audio capabilities, wrong channel mapping, HBR failures, spurious or missing hot-plug events, incorrect LPIB/timer snapshots, and CRC diagnostics changing on the wrong channel.

## Cross-Chunk Notes

This is a middle slice of a much larger generated header. The final per-file research document should merge this with adjacent chunks before making whole-file claims. Specifically:

- `DC_COMBOPHYTXREGS2_MARGIN_DEEMPH_LANE3` starts before line 44706.
- `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_HBR` continues after line 47394.
- Later chunks are needed for the rest of the F2 input endpoint input-pin fields and the file guard tail.

### subset-b-001600: lines 47395-49843

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 47395-49843

## Purpose

This chunk is part of AMDGPU's generated DCN 1.0 register field mask/shift header. It contains no executable C logic; it publishes compile-time bit layout constants for Azalia/HD-audio registers in the display audio block.

Each register field is represented by paired macros:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit position.
- `REGISTER__FIELD_MASK` gives the already-positioned bit mask.

Driver code combines these definitions with matching register address macros from `dcn_1_0_offset.h` and with AMD display register helper macros such as `SF(...)`, `REG_SET`, `REG_UPDATE`, and lower-level MMIO read/write helpers. Correctness is therefore a hardware-layout contract: a wrong bit position can compile cleanly while programming the wrong audio endpoint, stream, or status bit.

The range is centered on the DCN 1.0 display audio/Azalia namespace:

- Tail fields for the function-2 input pin, including HBR capability/enable masks, multichannel controls, LPIB snapshot registers, input activity/status, infoframe/channel status, and pin capabilities.
- The `azroot_f2codecind` root/function codec block, including vendor/device and revision parameters, subordinate node counts, power state, subsystem ID response bytes, converter synchronization, codec reset, supported sample rates/formats, and power-state capabilities.
- Sixteen repeated `azf0stream<N>_streamind` stream blocks, each exposing FIFO size and latency counter fields for stream indices 0-15.
- Four repeated `azf0endpoint<N>_endpointind` endpoint blocks, for endpoint indices 0-3. Endpoints 0-2 are fully represented in this chunk; endpoint 3 is present through its audio descriptor fields and then the chunk ends at the next multichannel-control comment.

Although the repository path is under a local `ceph-client` source tree, this file is AMDGPU display-driver hardware metadata. It has no Ceph filesystem protocol behavior, no distributed filesystem state, and no filesystem persistence semantics.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or runtime APIs in this chunk. The macro namespace is the API surface.

The first section completes function-2 input-pin fields:

- `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_HBR__HBR_CAPABLE_MASK` and `...__HBR_ENABLE_MASK` expose HBR audio capability and enable bits.
- `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL1_ENABLE`, `MULTICHANNEL3_ENABLE`, `MULTICHANNEL5_ENABLE`, and `MULTICHANNEL7_ENABLE` each provide enable, mute, and channel-ID fields for odd-numbered multichannel pairs.
- `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL`, `LPIB`, and `LPIB_TIMER_SNAPSHOT` expose a snapshot lock, cyclic buffer wrap count, current link position in buffer, and timer snapshot.
- `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_INPUT_STATUS_CONTROL` exposes input activity, channel layout, unsolicited-response enablement for activity, and unsolicited-response enablement for channel-layout/channel-status/infoframe changes.
- `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_INFOFRAME`, `CHANNEL_STATUS_L`, and `CHANNEL_STATUS_H` expose audio infoframe channel count/allocation/validity and IEC channel-status payload words.
- `AZALIA_F2_CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `..._CAPABILITIES` describe pin widget capabilities such as digital/power-control/LR-swap support, widget type, jack detection, input/output capability, HDMI/DP capability, VREF control, and EAPD capability.

The `azroot_f2codecind` group describes codec root and function-level Azalia metadata:

- `AZALIA_F2_CODEC_ROOT_PARAMETER_VENDOR_AND_DEVICE_ID`, `REVISION_ID`, and `SUBORDINATE_NODE_COUNT` expose full-width root parameter values.
- `AZALIA_F2_CODEC_FUNCTION_CONTROL_POWER_STATE` exposes requested and actual power state plus `CLKSTOPOK` and settings reset.
- `AZALIA_F2_CODEC_FUNCTION_CONTROL_RESPONSE_SUBSYSTEM_ID` and byte-specific variants expose subsystem ID bytes.
- `AZALIA_F2_CODEC_FUNCTION_CONTROL_CONVERTER_SYNCHRONIZATION` and `..._RESET` expose converter synchronization and codec reset controls.
- `AZALIA_F2_CODEC_FUNCTION_PARAMETER_SUPPORTED_SIZE_RATES`, `STREAM_FORMATS`, and `POWER_STATES` expose audio rate/bit capabilities, stream format capabilities, and function power capabilities including `CLKSTOP` and `EPSS`.

The `AZF0STREAM0` through `AZF0STREAM15` groups are mechanically repeated. For each stream, the macros define:

- `AZALIA_FIFO_SIZE_CONTROL` fields for minimum FIFO size, maximum FIFO size, and maximum latency support.
- `AZALIA_LATENCY_COUNTER_CONTROL__AZALIA_LATENCY_COUNTER_RESET`.
- Full-width worst-case latency count, cumulative latency count, and cumulative request count fields.

The `AZF0ENDPOINT0`, `AZF0ENDPOINT1`, `AZF0ENDPOINT2`, and partial `AZF0ENDPOINT3` groups describe function-0 codec converter and pin controls:

- Converter widget capabilities: audio channel capability, amplifier presence, format override, striping, processing widget, unsolicited response capability, connection list, digital/power-control/LR-swap support, delay, and widget type.
- Converter format and stream routing: number of channels, bits per sample, sample base divisor/multiple/rate, stream type, channel ID, and stream ID.
- Digital converter status/control: `DIGEN`, validity, validity configuration, pre/copy/non-audio/professional/channel-status bits, channel count, and keepalive.
- Supported formats and rates: full-width stream-format capability plus rate and bit-depth capability fields.
- Striping, ramp rate, GTC embedding, and GTC counter delta/min/max fields.
- Pin widget capabilities and pin capabilities, including digital, HDMI, DP, power, jack-detect, VREF, EAPD, and input/output support bits.
- Pin controls for unsolicited responses, pin sense, widget output enable, channel/speaker allocation, HDMI/DP connection bits, extra connection information, LFE level, level shift, and down-mix inhibit.
- Audio descriptor 0-13 fields for EDID-like short audio descriptor contents: max channels, supported frequencies, descriptor byte 2, and for descriptor 0 an extra stereo-frequency field.
- Endpoint 0-2 additional controls after the descriptor list: multichannel enable groups, lipsync/HBR response fields, sink-info words, hot-plug and unsolicited-response force controls, configuration default, multichannel mode, IEC 60958 channel-status override registers, association and digital-output status, LPIB snapshots, coding type, format-change status/ack/reason/response, wireless display identification, remote keepalive, audio-enable status, and audio enabled/disabled/format-changed interrupt status fields.

The endpoint pattern is copy-generated. Endpoint 0 spans `AZF0ENDPOINT0_AZALIA_F0_*`, endpoint 1 spans `AZF0ENDPOINT1_AZALIA_F0_*`, endpoint 2 spans `AZF0ENDPOINT2_AZALIA_F0_*`, and endpoint 3 begins the same pattern through `AZF0ENDPOINT3_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR13`.

## Control Flow

This header chunk has no runtime control flow. It is preprocessor data.

Runtime control appears in consumers that follow a generated-register pattern:

1. DCN 1.0 resource code includes `dcn/dcn_1_0_offset.h` and `dcn/dcn_1_0_sh_mask.h`.
2. Resource tables bind address macros and field masks/shifts into hardware object register descriptors. In `dcn10_resource.c`, the audio table uses `AUD_COMMON_REG_LIST(id)` for four audio instances and builds `dce_audio_shift` and `dce_audio_mask` from `DCE120_AUD_COMMON_MASK_SH_LIST(...)`.
3. The generic DCE/DCN audio implementation selects an audio endpoint instance, writes endpoint index/data windows when needed, and programs converter/pin fields for the active stream.
4. Mode-set, audio setup, hotplug, DP/HDMI infoframe, and enable/disable flows read or write the resulting MMIO fields through the DC register helper layer.

Control-sensitive hardware actions represented by this chunk include codec reset and power-state changes, digital converter enable, stream/channel ID routing, audio format programming, pin output enable, HBR enablement, multichannel mute/enable/channel ID programming, channel-status override, sink audio descriptor publication, LPIB snapshot locking, format-change acknowledgement, remote keepalive, and audio interrupt mask/status handling. The macros themselves do not enforce legal sequencing, valid enum values, write-one-to-clear behavior, or endpoint ownership.

## State And Persistence Behavior

The file stores no software state and has no persistence mechanism. It describes state held in Azalia/HD-audio hardware registers.

The represented state includes:

- Codec identity and topology state: vendor/device ID, revision ID, subordinate node counts, group type, stream formats, supported rates, bit depths, and power states.
- Function-level control state: requested/actual power state, clock-stop capability, reset, subsystem ID response bytes, and converter synchronization.
- Stream performance state: FIFO size limits, latency counter reset control, worst-case latency, cumulative latency, and cumulative request counters for stream indices 0-15.
- Converter state: sample format, stream/channel routing, digital converter enable/status bits, validity and channel-status bits, keepalive, striping, ramp rate, and GTC presentation-time embedding/counter deltas.
- Pin/endpoint state: output enable, pin sense, speaker/channel allocation, HDMI/DP connection flags, audio descriptors, sink info, HBR and lipsync responses, configuration default, multichannel controls, codec channel-status overrides, LPIB snapshots, coding type, format-change status, wireless display identification, remote keepalive, audio enable state, and audio interrupt status/mask/type fields.

Persistence depends on hardware semantics outside this generated header. Some fields are read-only capability or status values, some are latched control bits that persist until another driver/firmware write, some are counters or snapshots, some are sticky interrupt/status bits requiring acknowledgement, and some may be reset by audio disable, hotplug handling, power gating, suspend/resume, codec reset, or ASIC reset. The header does not distinguish read-only, writable, volatile, self-clearing, or write-one-to-clear fields.

## Dependencies And Integration Points

This chunk depends on the generated DCN 1.0 address header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h`

Direct include points for `dcn_1_0_sh_mask.h` in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn10/irq_service_dcn10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_factory_dcn10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_translate_dcn10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_translate_dcn20.c`

The most direct integration point for this specific chunk is the DC audio resource setup in `dcn10_resource.c`. It constructs four `dce_audio_registers` entries, one per audio instance, then fills `dce_audio_shift` and `dce_audio_mask`. The field list includes endpoint index/data window fields and the common audio mask/shift list used by the DCE audio implementation. Other DC core code assigns and releases audio objects from the resource pool, copies EDID-derived `audio_info` into streams, and calls audio object functions during stream enable/disable paths.

Related generated enum metadata appears in broader AMD include headers, such as `soc24_enum.h`, where Azalia converter format and pin/audio descriptor values are named. Those enum names are not defined in this chunk, but they document legal values for fields whose bit positions are exposed here.

## Risks And Edge Cases

The primary risk is silent audio hardware misprogramming. A wrong mask or shift can compile successfully while updating the wrong endpoint, routing audio to the wrong stream/channel, losing a status bit, or corrupting adjacent fields during read-modify-write updates.

High-risk fields include converter format and stream routing. Bad `NUMBER_OF_CHANNELS`, `BITS_PER_SAMPLE`, sample base rate/divisor/multiple, `STREAM_ID`, or `CHANNEL_ID` constants can produce missing audio, distorted audio, wrong sample rate, incorrect channel mapping, or failures in DP/HDMI audio compliance tests.

HBR and multichannel fields are sensitive for high-bandwidth and surround audio. Incorrect `HBR_ENABLE`, `MULTICHANNEL*_ENABLE`, `MULTICHANNEL*_MUTE`, or `MULTICHANNEL*_CHANNEL_ID` masks can break compressed/HBR formats, mute only part of a multichannel stream, or route channels inconsistently.

Pin and descriptor fields affect sink-visible capability reporting. Bad audio descriptor masks, speaker/channel allocation fields, HDMI/DP connection bits, lipsync values, sink-info fields, or configuration-default fields can make the display audio codec report capabilities that disagree with EDID or link state. Symptoms include the OS selecting unsupported modes, missing formats, channel layout errors, or receiver compatibility failures.

Power, reset, keepalive, and status fields affect sequencing. Incorrect codec reset, function power-state, `CLKSTOPOK`, digital converter enable, remote keepalive, output enable, or audio enable/disable interrupt masks can cause audio not to start, not to stop cleanly, or to leave stale interrupt/status state across hotplug, DPMS, suspend/resume, or modeset.

The repeated stream and endpoint patterns create copy-generation risk. Stream blocks 0-15 are nearly identical, and endpoints 0-3 repeat long converter/pin sequences. A mismatched endpoint suffix, missing field, or copied mask from a neighboring instance might only fail for one connector/audio engine and could be missed by build tests.

The line range boundaries are artificial. This chunk starts with the `HBR` masks after the corresponding HBR shift definitions from the prior chunk, and it ends on the `AZF0ENDPOINT3_AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE` comment before that register's fields. The final per-file merge should treat these as chunk boundaries, not source omissions.

## Test Signals

Useful validation signals are mostly compile-time plus hardware behavior:

- Kernel or module build coverage for DCN 1.0 display paths that include `dcn_1_0_sh_mask.h`.
- Generated-header consistency checks comparing every `*_MASK` and `*__SHIFT` pair in this range against AMD's register database and the matching addresses in `dcn_1_0_offset.h`.
- Static checks that every `SF(...)` field used by DCN 1.0 audio resource tables has matching mask and shift macros.
- HDMI and DisplayPort audio playback tests across all exposed audio instances, including stereo PCM, multichannel LPCM, compressed formats, and HBR-capable formats where hardware/sink support exists.
- EDID/audio capability tests verifying that short audio descriptors, speaker allocation, channel allocation, sample rates, sample sizes, lipsync, and sink-info fields match the connected sink.
- Hotplug, DPMS, modeset, and suspend/resume stress tests checking that audio endpoints are acquired/released correctly, audio enable/disable status changes are observed, and stale format-change or interrupt bits do not persist.
- LPIB and latency-counter diagnostics, when available, should show monotonic/current position behavior, correct snapshot locking, and sane worst-case/cumulative latency counts.
- Compliance or lab tests for IEC 60958 channel-status override fields, HBR audio, keepalive/silent-stream behavior, and DP/HDMI audio infoframe behavior.

Regression symptoms from bad constants include no HDMI/DP audio, audio on the wrong display, wrong channel count, bad sample rate or bit depth, muted channels, intermittent audio after hotplug or resume, HBR-only failures, incorrect sink capabilities exposed to the OS, interrupt storms or missing audio interrupts, LPIB position mismatches, and audio format-change handshakes that never clear.

## Cross-Chunk Notes

Earlier chunks of `dcn_1_0_sh_mask.h` define the preceding Azalia controller, codec, converter, and function-2 input-pin fields, including the beginning of the HBR register whose masks appear at the top of this chunk. Later chunks continue endpoint 3 from `AZF0ENDPOINT3_AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE` and then proceed through the remaining DCN 1.0 register mask namespace. The final per-file research document should treat the full header as one generated DCN 1.0 hardware register-layout contract rather than as independent algorithmic code.

### subset-b-001601: lines 49844-52212

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 49844-52212

## Scope And Purpose

This chunk is a generated AMD DCN 1.0 register field shift/mask table for Azalia/HD-audio codec endpoint registers. It contains no executable C logic. Its purpose is to provide compile-time bitfield metadata that the AMDGPU display audio code uses when it selects an Azalia endpoint index register, reads or writes endpoint data, and composes or decodes HD-audio codec response/control values.

The path is under a local `ceph-client` source mirror, but this file is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

This range is the late output-endpoint area of `dcn_1_0_sh_mask.h`. It starts in the middle of `AZF0ENDPOINT3` and then covers complete or near-complete repeated endpoint blocks:

- Tail of `AZF0ENDPOINT3`: multichannel controls, lip-sync/HBR/sink info, hot-plug audio enable, configuration default, IEC 60958 channel-status override, LPIB snapshots, format-change and keepalive status, and audio enable/disable/format-change interrupt status.
- Complete `AZF0ENDPOINT4`, `AZF0ENDPOINT5`, and `AZF0ENDPOINT6` output endpoint indexed blocks: converter capabilities/control, pin capabilities/control, audio descriptors, multichannel routing, sink metadata, hot-plug/audio enable, IEC 60958 overrides, LPIB tracking, coding/format status, keepalive, and audio interrupt status.
- Most of `AZF0ENDPOINT7`: from converter capability/control through IEC 60958 channel-number override 7; the final endpoint 7 tail continues in the next chunk.

The chunk is highly repetitive by design. Each endpoint instance exposes the same HD-audio style register fields so display code can bind one logical audio object per hardware endpoint.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or storage objects in this range. The public interface is the generated preprocessor contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit endpoint-data value.
- The register names in this chunk are instance-qualified, such as `AZF0ENDPOINT4_AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL__AUDIO_ENABLED_MASK`.

Important macro families in this chunk:

- `AZF0ENDPOINTn_AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: endpoint converter capability bits, including channel capability, amplifier/format override support, stripe/processing/unsolicited response capability, connection-list and digital/power-control flags, LR swap, delay, and widget type.
- `AZF0ENDPOINTn_AZALIA_F0_CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT`: stream format fields for channel count, bits per sample, sample divisor/multiple/base rate, and PCM/non-PCM stream type.
- `AZF0ENDPOINTn_AZALIA_F0_CODEC_CONVERTER_CONTROL_CHANNEL_STREAM_ID`: channel and stream IDs used to bind a codec converter to an HDA stream.
- `AZF0ENDPOINTn_AZALIA_F0_CODEC_CONVERTER_CONTROL_DIGITAL_CONVERTER`: digital converter enable and IEC-style status/control bits such as validity, pre-emphasis, copyright, non-audio, professional, level, category code, and keepalive.
- `AZF0ENDPOINTn_AZALIA_F0_CODEC_CONVERTER_PARAMETER_STREAM_FORMATS` and `...SUPPORTED_SIZE_RATES`: capability bitmaps for supported stream formats, sample rates, and sample sizes.
- `AZF0ENDPOINTn_AZALIA_F0_CODEC_CONVERTER_STRIPE_CONTROL`, `...RAMP_RATE`, `...GTC_EMBEDDING`, and `...GTC_COUNTER_DELTA*`: stripe, ramp, and global time counter synchronization/control fields.
- `AZF0ENDPOINTn_AZALIA_F0_CODEC_PIN_PARAMETER_*`: output pin widget capabilities and connector capabilities such as HDMI/DP, jack-detect, output/input capability, EAPD, VREF, and balanced I/O flags.
- `AZF0ENDPOINTn_AZALIA_F0_CODEC_PIN_CONTROL_*`: pin control fields for unsolicited response tags, pin sense, widget output enable, channel/speaker allocation, audio descriptors 0-13, multichannel enable/mute/channel IDs, lip-sync response, HBR capable/enable, sink info, hot-plug audio enable, forced unsolicited response payloads, configuration default, digital output status, LPIB snapshot/current/timer values, coding type, format-change response, wireless display identification, and remote keepalive.
- `AZF0ENDPOINTn_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8`: IEC 60958 channel-status override fields for mode, source number, clock accuracy, word length, sampling frequency, original sampling frequency, sampling coefficient, MPEG surround, CGMS-A, and channel numbers for left/right plus channels 2-7.
- `AZF0ENDPOINTn_AZALIA_F0_AUDIO_ENABLE_STATUS`, `...AUDIO_ENABLED_INT_STATUS`, `...AUDIO_DISABLED_INT_STATUS`, and `...AUDIO_FORMAT_CHANGED_INT_STATUS`: endpoint audio state and interrupt flag/mask/type fields.

The unqualified `AZALIA_F0_*` field names used by common display audio code are mapped to the appropriate instance by register/field table macros. For DCN 1.0, `dcn10_resource.c` builds `audio_regs[]` with `AUD_COMMON_REG_LIST(id)` for endpoint instances 0-3 and uses `SF(AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_INDEX, AZALIA_ENDPOINT_REG_INDEX, ...)` and endpoint-data masks for the common indexed access path. Later endpoint instance macros remain part of the generated ASIC surface even when a resource table exposes fewer audio instances.

## Control Flow

This chunk has no runtime control flow. It is consumed by code that performs indexed Azalia endpoint MMIO:

1. Select the desired endpoint-local register through `AZALIA_F0_CODEC_ENDPOINT_INDEX`.
2. Read or write the endpoint payload through `AZALIA_F0_CODEC_ENDPOINT_DATA`.
3. Use the generated shift/mask macros to update individual fields in that payload.

The relevant display-core integration is in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h` and `dce_audio.c`:

- `AUD_COMMON_REG_LIST(id)` maps `AZALIA_F0_CODEC_ENDPOINT_INDEX` and `AZALIA_F0_CODEC_ENDPOINT_DATA` to `AZF0ENDPOINT{id}` instances.
- `struct dce_audio_registers`, `struct dce_audio_shift`, and `struct dce_audio_mask` carry register addresses plus endpoint index/data field masks into common audio code.
- `dce_aud_az_enable()` and `dce_aud_az_disable()` read `AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL`, toggle `CLOCK_GATING_DISABLE`, then set or clear `AUDIO_ENABLED`.
- `dce_aud_az_configure()` programs speaker/channel allocation, endpoint audio descriptors, sink/product strings, HBR state, and lip-sync/audio latency data from DRM/display audio metadata.
- `dce_aud_endpoint_valid()` reads `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT` and checks the port-connectivity field to decide whether the endpoint is usable.

Legacy DCE paths (`amdgpu/dce_v6_0.c`, `dce_v8_0.c`, and `dce_v10_0.c`) show the same HDA endpoint programming pattern using `RREG32_AUDIO_ENDPT` and `WREG32_AUDIO_ENDPT` against `ixAZALIA_F0_CODEC_PIN_CONTROL_*` indexed registers. They are not DCN 1.0 consumers of these exact instance-qualified macros, but they document the same hardware contract: configure audio descriptors, lip-sync, speaker allocation, and hot-plug audio enable via Azalia endpoint index/data registers.

Because the header is declarative, it does not enforce sequencing. Consumers must order clock-gating disable/enable, endpoint index selection, endpoint-data writes, HDA stream setup, modeset/link bring-up, and interrupt/status handling.

## State And Persistence Behavior

The header itself stores no state and has no persistence behavior. The macros describe hardware endpoint MMIO state.

The represented hardware state includes:

- Converter state: stream format, channel/stream IDs, digital converter control, supported format/rate bitmaps, striping, ramp rate, GTC embedding, and GTC counter-delta tracking.
- Pin capability and control state: pin/widget capabilities, unsolicited response configuration, pin sense, output enable, speaker/channel allocation, EDID-derived audio descriptor fields, multichannel enable/mute/channel IDs, HBR capability/enable, and HDMI/DP sink metadata.
- Hot-plug/audio state: clock gating disable, clock-on status, `AUDIO_ENABLED`, forced unsolicited response payloads, configuration-default reporting, digital output active status, wireless display identification, and remote keepalive enable/capability.
- IEC 60958 channel status override state: mode/source, clock accuracy, word length, sampling-frequency fields, sampling-frequency coefficient, MPEG surround/CGMS-A fields, and per-channel number fields.
- Position and timing state: LPIB snapshot lock, cyclic buffer wrap count, current LPIB, and LPIB timer snapshot.
- Event and interrupt state: coding type, format-change reason/response, audio enable status, audio-enabled/audio-disabled/audio-format-changed flags, masks, and type fields.

Persistence is field-specific and not encoded here. Some fields are programming knobs that persist until rewritten, reset, modeset, suspend/resume, power-gating transition, or GPU reset. Other fields are status, capability, interrupt, sticky, self-clearing, or latched snapshot values. Names such as `*_STATUS`, `*_FLAG`, `*_MASK`, `*_TYPE`, `*_ENABLE`, `*_CAPABILITY`, `*_SNAPSHOT_LOCK`, `*_ACK_UR_ENABLE`, and `*_RESPONSE` hint at semantics, but this generated header does not declare access type, reset value, side effects, or write-one-to-clear behavior.

## Dependencies And Integration Points

This chunk depends on the generated DCN 1.0 ASIC register-header ecosystem:

- `dcn_1_0_d.h` for the matching register/index address constants, including endpoint index/data and indexed `ixAZALIA_F0_CODEC_*` names.
- `dcn_1_0_enum.h` and related enum/value headers for symbolic field values used with these masks.
- Display-core helper macros such as `REG_SET`, `REG_SET_FIELD`, `get_reg_field_value`, `set_reg_field_value`, `SRI`, `SF`, `AZ_REG_READ`, and `AZ_REG_WRITE`.
- Runtime register access through the AMDGPU/DC context, which turns resource-table addresses plus masks/shifts into MMIO reads/writes.

Direct integration points visible in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h`: declares the common DCE/DCN audio register, mask, and shift tables and maps `AZF0ENDPOINT{id}` indexed registers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.c`: implements endpoint validation, Azalia enable/disable, HBR control, lip-sync latency, speaker/channel allocation, audio descriptor programming, and DTO setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn10/dcn10_resource.c`: instantiates DCN 1.0 audio register arrays and binds the endpoint index/data masks/shifts used by `dce_audio.c`.
- Later DCN resource files use the same common audio model for newer generated endpoint headers, so consistency in this generated naming contract matters across display generations.

Functional integration surfaces are HDMI/DisplayPort audio bring-up, EDID/ELD-derived audio capability propagation, sink description/manufacturer/product metadata reporting, HDA stream/channel binding, HBR audio enabling, audio clock/DTO setup, hot-plug audio enable/disable, audio format-change handling, and HDA/DRM audio debug.

## Risks And Edge Cases

- Masks and shifts are hardware ABI. A one-bit error can compile cleanly but program the wrong HDA field, corrupt adjacent endpoint state, leave audio disabled, misreport sink capabilities, or break HDMI/DP audio.
- The range is generated and very repetitive. Manual edits to `AZF0ENDPOINT3` through `AZF0ENDPOINT7` instance families are easy to skew; regeneration from the authoritative register database is safer than hand edits.
- This chunk starts and ends at chunk boundaries, not semantic boundaries. It begins after earlier `AZF0ENDPOINT3` pin/audio-descriptor fields and ends before the final `AZF0ENDPOINT7` pin/status tail in the next chunk.
- Endpoint count is generation/resource dependent. DCN 1.0 resource code exposes endpoint instances through `audio_regs[]`; generated macros for later endpoint numbers do not imply every board or ASIC path creates that many active audio objects.
- Indexed endpoint access is sequencing-sensitive. Selecting the wrong endpoint index/data pair or racing another indexed access can read/write the wrong endpoint-local register.
- `HOT_PLUG_CONTROL` combines clock-gating and `AUDIO_ENABLED`. Consumers must follow the established sequence of temporarily disabling clock gating before changing audio enable state.
- Audio descriptors encode EDID-derived capabilities. Bad `MAX_CHANNELS`, `SUPPORTED_FREQUENCIES`, or descriptor-byte fields can cause userspace/HD-audio layers to expose invalid formats or hide valid sink formats.
- IEC 60958 override fields are audio-format sensitive. Incorrect sampling frequency, word length, channel numbers, CGMS-A, or non-audio/professional bits can cause sink rejection, silence, wrong channel layout, or bad compressed-audio behavior.
- Interrupt/status fields mix flag, mask, and type naming. Misinterpreting them can lose enable/disable/format-change notifications or generate repeated unsolicited responses.
- LPIB and timer snapshot fields are likely latched/snapshot-style hardware state. Incorrect snapshot-lock handling can produce inconsistent position reporting.

## Test Signals

Useful validation is mainly build-time plus hardware/display-audio behavior:

- Build AMDGPU display-core DCN 1.0 code with this header included; generated macro drift should fail in `dcn10_resource.c`, `dce_audio.h`, or shared register-field helper users.
- Compare this chunk against adjacent chunks of `dcn_1_0_sh_mask.h`, the matching `dcn_1_0_d.h` indexed register names, and newer DCN headers to catch instance-index or field-name drift.
- Exercise HDMI and DisplayPort audio on DCN 1.0 hardware: hotplug, modeset, stream start/stop, suspend/resume, multi-monitor endpoint selection, and audio enable/disable transitions.
- Validate EDID/ELD-derived audio capabilities: stereo fallback, multichannel speaker allocation, compressed formats, HBR-capable formats, sample-rate/word-length exposure, and sink manufacturer/product/description metadata where visible.
- Test format changes while audio is active and watch for correct reprogramming of descriptor, converter format, channel-stream ID, IEC 60958 status, and audio format-change interrupt/status behavior.
- Check negative signals in kernel logs and user-visible behavior: missing HDMI/DP audio device, silent playback, wrong channel layout, invalid sample-rate exposure, HBR formats unavailable, repeated audio enable/disable interrupts, hotplug audio regressions, LPIB position anomalies, or resume leaving `AUDIO_ENABLED` cleared.

### subset-b-001602: lines 52213-54345

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h

Chunk: `subset-b-001602`
Covered source range: lines 52213-54345 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h`

## Purpose

This chunk is part of AMD's generated DCN 1.0 register shift/mask header. It contains preprocessor constants only; there are no functions, structs, enums, runtime branches, or storage objects in the covered range. The constants describe bit positions and masks for Azalia/HDA HDMI/DisplayPort audio codec endpoint registers.

The source path is under a local `ceph-client` mirror, but the file itself is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

The covered range starts mid-register with the final mask for `AZF0ENDPOINT7_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_7`, then completes the tail of output endpoint 7. After that it defines the full repeated field layouts for `azf0inputendpoint0_inputendpointind` through `azf0inputendpoint7_inputendpointind`. These input endpoint blocks expose indexed Azalia codec input converter and input pin fields, including audio widget capabilities, converter format, stream/channel IDs, IEC 60958 digital converter bits, supported formats/rates, pin capabilities, unsolicited responses, input sense, multichannel routing, high-bit-rate audio status, hotplug/audio enable state, configuration defaults, LPIB snapshots, input activity, and channel-status/infoframe capture.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. Its public interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least significant bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted bit mask in the register payload.
- Register names beginning with `AZF0ENDPOINT7_` describe fields behind output endpoint 7's indexed Azalia pin-control/function registers.
- Register names beginning with `AZF0INPUTENDPOINT0_` through `AZF0INPUTENDPOINT7_` describe eight repeated input endpoint indexed register blocks.

The endpoint 7 tail covers:

- `PIN_CONTROL_CODEC_CS_OVERRIDE_8`: IEC 60958 channel number fields for channels 6 and 7.
- `CODEC_PIN_ASSOCIATION_INFO`: full 32-bit association metadata.
- `CODEC_PIN_CONTROL_DIGITAL_OUTPUT_STATUS`: `OUTPUT_ACTIVE`.
- `CODEC_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL`, `LPIB`, and `LPIB_TIMER_SNAPSHOT`: link position snapshot lock, wrap count, 32-bit LPIB, and timer snapshot fields.
- `CODEC_PIN_CONTROL_CODING_TYPE`: 8-bit coding type.
- `CODEC_PIN_CONTROL_FORMAT_CHANGED`: format-changed latch, unsolicited-response enable, reason, and response fields.
- `CODEC_PIN_CONTROL_WIRELESS_DISPLAY_IDENTIFICATION` and `REMOTE_KEEPALIVE`: WFD identification, keepalive enable, and capability fields.
- `AUDIO_ENABLE_STATUS`, `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, and `AUDIO_FORMAT_CHANGED_INT_STATUS`: audio enable state plus flag/mask/type interrupt triplets.

Each input endpoint instance `0..7` repeats the same field families:

- `CODEC_INPUT_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`: HDA widget capability bits for channel capability, input/output amplifiers, amplifier-parameter override, format override, stripe, processing widget, unsolicited responses, connection list, digital support, power control, LR swap, delay, and widget type.
- `CODEC_INPUT_CONVERTER_CONTROL_CONVERTER_FORMAT`: channel count, bits per sample, sample-base divisor/multiple/rate, and stream type.
- `CODEC_INPUT_CONVERTER_CONTROL_CHANNEL_STREAM_ID`: channel ID and stream ID nibbles.
- `CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`: digital enable and IEC-style channel status flags such as validity, validity configuration, pre-emphasis, copy, non-audio, professional mode, level, channel-status category code, and keepalive.
- `CODEC_INPUT_CONVERTER_PARAMETER_STREAM_FORMATS` and `SUPPORTED_SIZE_RATES`: 32-bit format bitmap plus rate and bit-depth capability fields.
- `CODEC_INPUT_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `CAPABILITIES`: input pin widget capability bits plus pin capabilities for impedance sense, trigger requirement, jack detect, headphone drive, output/input capability, balanced I/O, HDMI, VREF control, EAPD, and DisplayPort.
- `CODEC_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE` and `UNSOLICITED_RESPONSE_FORCE`: tag/enable fields and a forced unsolicited-response payload trigger.
- `CODEC_INPUT_PIN_CONTROL_RESPONSE_INPUT_PIN_SENSE`: impedance sense and presence detect.
- `CODEC_INPUT_PIN_CONTROL_WIDGET_CONTROL`: `IN_ENABLE`.
- `CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2`: enable, mute, and channel-ID fields for multichannel slots 0-7.
- `CODEC_INPUT_PIN_CONTROL_RESPONSE_HBR`: HBR capable and HBR enable bits.
- `CODEC_INPUT_PIN_CONTROL_CHANNEL_ALLOCATION`: 8-bit channel allocation.
- `CODEC_INPUT_PIN_CONTROL_HOT_PLUG_CONTROL`: clock-gating disable, clock-on state, and audio-enabled bit.
- `CODEC_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT`: HDA configuration-default fields such as sequence, default association, misc, color, connection type, default device, location, and port connectivity.
- `CODEC_INPUT_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL`, `LPIB`, and `LPIB_TIMER_SNAPSHOT`: position and timer snapshot fields for input streams.
- `CODEC_INPUT_PIN_CONTROL_INPUT_STATUS_CONTROL`: input activity, channel layout, input-activity unsolicited-response enable, and channel-layout/channel-status infoframe-change unsolicited-response enable.
- `CODEC_INPUT_PIN_CONTROL_INFOFRAME`: channel count, channel allocation, infoframe byte 5, and infoframe-valid bit.

## Control Flow

This header chunk has no local control flow. Every significant line is a `#define` consumed by the C preprocessor.

Runtime control flow lives in AMD display/audio code that pairs this `dcn_1_0_sh_mask.h` metadata with offset/index definitions and register helpers:

1. DCN 1.0 resource code includes `dcn/dcn_1_0_offset.h` and this mask header, then builds audio register and field tables.
2. `display/dc/dce/dce_audio.h` defines `AUD_COMMON_REG_LIST`, `AUD_COMMON_MASK_SH_LIST`, and related `SF(...)` helpers. These concatenate register and field names into entries in `struct dce_audio_registers`, `struct dce_audio_shift`, and `struct dce_audio_mask`.
3. `display/dc/resource/dcn10/dcn10_resource.c` instantiates DCN 1.0 audio register tables for audio instances and maps `AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_INDEX` / `DATA` fields into the common audio mask/shift structures.
4. `display/dc/dce/dce_audio.c` writes `AZALIA_F0_CODEC_ENDPOINT_INDEX` to select an indexed Azalia codec register and reads or writes `AZALIA_F0_CODEC_ENDPOINT_DATA` to transfer the payload.
5. Higher-level audio paths such as `dce_aud_az_enable`, `dce_aud_az_disable`, and `dce_aud_az_configure` use `AZ_REG_READ`, `AZ_REG_WRITE`, `set_reg_field_value`, and `get_reg_field_value` against HDA codec pin/function fields. The fields in this chunk describe the same kind of payload layout for endpoint 7 and the input endpoint indexed blocks.

The chunk itself does not encode sequencing. Correct ordering around clock-gating disable, hotplug/audio enable, HBR capability exposure, stream format programming, descriptor updates, LPIB snapshots, and interrupt/status handling is imposed by `dce_audio.c`, stream encoder code, the HDA controller, and hardware register specifications.

## State And Persistence Behavior

The macros are stateless compile-time constants. They do not allocate memory, perform I/O, store persistent data, or modify hardware by themselves.

The hardware fields they describe are stateful. Output endpoint 7 fields can hold channel-status override data, association information, output-active status, LPIB snapshots, coding type, format-change state, wireless-display identification, keepalive settings, audio-enable state, and interrupt flag/mask/type state. Input endpoint fields can hold converter format, stream/channel IDs, digital converter flags, supported format/rate capability data, pin capabilities, unsolicited-response enables and force payloads, input sense, multichannel routing/mute/channel IDs, HBR state, hotplug/audio state, configuration defaults, LPIB snapshots, input activity, channel layout, and infoframe-derived channel information.

Those hardware values persist until changed by the driver, HDA/Azalia controller activity, audio stream start/stop, hotplug events, sink/source format changes, power management, display block reset, suspend/resume, or GPU reset. Some fields are configuration bits, some are capability or readback/status bits, some are interrupt mask/status fields, and some appear to be self-clearing or action-trigger fields based on names such as `*_FORCE`, `*_FLAG`, `*_STATUS`, `*_SNAPSHOT_LOCK`, and `*_FORMAT_CHANGED`. The header does not encode access type, reset value, reserved-bit policy, write-one-to-clear behavior, or power-domain restrictions.

## Dependencies And Integration Points

Immediate dependencies are the C preprocessor and AMD's generated register naming scheme. Practical integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_offset.h`, which supplies matching `ix...` indexed-register constants for the Azalia endpoint payloads and `mm...` constants for the endpoint index/data MMIO registers.
- DCN 1.0 resource construction in `display/dc/resource/dcn10/dcn10_resource.c`, which includes this mask header and builds `audio_shift` / `audio_mask` tables from generated field names.
- Common audio abstractions in `display/dc/dce/dce_audio.h`, especially `AUD_COMMON_REG_LIST`, `AUD_COMMON_MASK_SH_LIST_BASE`, `AUD_COMMON_MASK_SH_LIST`, and the `struct dce_audio_*` table types.
- Indirect Azalia access helpers in `display/dc/dce/dce_audio.c`: `write_indirect_azalia_reg`, `read_indirect_azalia_reg`, `AZ_REG_READ`, and `AZ_REG_WRITE`.
- Field manipulation helpers in `display/dc/inc/reg_helper.h`, including `REG_SET`, `REG_UPDATE`, `set_reg_field_value`, and `get_reg_field_value`.
- The HDA/Azalia controller and sink/source audio paths that consume endpoint capabilities, channel status, hotplug state, HBR capability, stream format, and infoframe/channel allocation data.

The repeated `AZF0INPUTENDPOINT0..7` naming is a key generated-header contract. Each instance is expected to have the same field layout. Code can then reason about endpoint instance selection through indexed register addresses while field extraction remains identical across instances. The mask header alone does not select an input endpoint; it defines the bit layout once per generated endpoint name.

## Risks And Edge Cases

- These constants are hardware ABI. A wrong shift or mask can compile cleanly but program or interpret the wrong bits in an indexed Azalia endpoint payload.
- The chunk starts mid-register. The final line for `AZF0ENDPOINT7_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_7` belongs with definitions in the previous chunk; final file-level reconciliation should merge it before treating endpoint 7's channel-status override fields as complete.
- The input endpoint blocks are highly repetitive. A copied endpoint number, field name, shift, or mask error can affect only one input endpoint and appear as an instance-specific audio capture, infoframe, presence-detect, or channel-layout problem.
- Many fields are protocol-sensitive HDA/HDMI/DP audio metadata. Misinterpreting converter format, sample-size/rate fields, channel allocation, IEC 60958 channel-status bits, or HBR state can produce missing audio, wrong channel mapping, unsupported-format advertisement, or non-audio/pro-audio flag mismatches while the display path still works.
- Indirect endpoint access has two layers: an MMIO index/data pair and an indexed payload register. Mixing `mm...`, `ix...`, and field-mask namespaces is not type-checked by C.
- Status, interrupt, and force fields likely have side effects that are not visible in this generated header. Treating a flag as ordinary read/write state can lose events, retrigger unsolicited responses, or fail to acknowledge a hardware condition.
- `CLOCK_GATING_DISABLE`, `CLOCK_ON_STATE`, and `AUDIO_ENABLED` fields affect hardware power/clock visibility. Writes while the endpoint is clock-gated, or leaving clock gating disabled after updates, can cause unreliable readback or unnecessary power use.
- LPIB snapshot fields combine a lock bit, wrap counter, position, and timer. Reading these without the intended snapshot sequence can produce inconsistent audio position/timestamp pairs.
- Capability fields such as widget capabilities, pin capabilities, supported size/rates, and HBR capability may be consumed by upper audio stacks. Advertising unsupported capabilities or hiding supported ones can shift failures into userspace audio enumeration rather than obvious kernel errors.

## Test Signals

Useful validation signals include:

- compile coverage for DCN 1.0 display/audio files that include `dcn_1_0_sh_mask.h`, especially `display/dc/resource/dcn10/dcn10_resource.c`, `display/dc/dce/dce_audio.c`, and `display/dc/dce/dce_audio.h`;
- generated-header consistency checks that every field in this range has both a `__SHIFT` and `_MASK`, except for the intentionally partial first line inherited from the previous chunk;
- consistency checks across `AZF0INPUTENDPOINT0..7` confirming identical field names, shifts, and masks for every repeated input endpoint instance;
- offset/mask pairing checks against `dcn_1_0_offset.h` to ensure matching `ixAZF0ENDPOINT7_...` and `ixAZF0INPUTENDPOINT0..7_...` indexed-register constants exist for the register names described here;
- hardware audio smoke tests over HDMI and DisplayPort: hotplug, modeset, enable/disable audio, suspend/resume, stream start/stop, and rapid display reconfiguration;
- HDA/Azalia enumeration checks confirming expected widget capabilities, supported rates/bit depths, pin capabilities, configuration defaults, HBR capability, and channel allocation;
- DP/HDMI audio functional tests for stereo, multichannel, HBR/non-HBR formats, sample-rate changes, non-audio bitstream formats, channel-status reporting, and infoframe channel allocation;
- event tests for unsolicited responses, format-changed interrupts, audio enabled/disabled interrupts, input activity changes, and infoframe/channel-layout changes;
- debug/readback checks for LPIB snapshot stability, wrap-count movement during playback/capture, `OUTPUT_ACTIVE` / `AUDIO_ENABLE_STATUS`, `INPUT_ACTIVITY`, `INFOFRAME_VALID`, and hotplug/audio-enabled state;
- negative signals in logs or user-visible behavior: missing ALSA HDMI/DP audio device, wrong EDID audio capability exposure, absent HBR formats, channel order errors, stuck audio-enabled state, repeated format-change events, stale LPIB snapshots, or failures isolated to endpoint 7 or a specific input endpoint instance.
