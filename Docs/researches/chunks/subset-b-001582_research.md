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
