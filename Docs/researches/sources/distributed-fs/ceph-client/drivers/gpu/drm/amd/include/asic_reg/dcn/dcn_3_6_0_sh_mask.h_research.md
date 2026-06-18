# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002118`: lines 1-2434, `Docs/researches/chunks/subset-b-002118_research.md`
- `subset-b-002119`: lines 2435-4812, `Docs/researches/chunks/subset-b-002119_research.md`
- `subset-b-002120`: lines 4813-7453, `Docs/researches/chunks/subset-b-002120_research.md`
- `subset-b-002121`: lines 7454-9969, `Docs/researches/chunks/subset-b-002121_research.md`
- `subset-b-002122`: lines 9970-12458, `Docs/researches/chunks/subset-b-002122_research.md`
- `subset-b-002123`: lines 12459-14996, `Docs/researches/chunks/subset-b-002123_research.md`
- `subset-b-002124`: lines 14997-17536, `Docs/researches/chunks/subset-b-002124_research.md`
- `subset-b-002125`: lines 17537-20052, `Docs/researches/chunks/subset-b-002125_research.md`
- `subset-b-002126`: lines 20053-22519, `Docs/researches/chunks/subset-b-002126_research.md`
- `subset-b-002127`: lines 22520-24994, `Docs/researches/chunks/subset-b-002127_research.md`
- `subset-b-002128`: lines 24995-27614, `Docs/researches/chunks/subset-b-002128_research.md`
- `subset-b-002129`: lines 27615-30081, `Docs/researches/chunks/subset-b-002129_research.md`
- `subset-b-002130`: lines 30082-32579, `Docs/researches/chunks/subset-b-002130_research.md`
- `subset-b-002131`: lines 32580-34984, `Docs/researches/chunks/subset-b-002131_research.md`
- `subset-b-002132`: lines 34985-37380, `Docs/researches/chunks/subset-b-002132_research.md`
- `subset-b-002133`: lines 37381-39778, `Docs/researches/chunks/subset-b-002133_research.md`
- `subset-b-002134`: lines 39779-42166, `Docs/researches/chunks/subset-b-002134_research.md`
- `subset-b-002135`: lines 42167-44553, `Docs/researches/chunks/subset-b-002135_research.md`
- `subset-b-002136`: lines 44554-47050, `Docs/researches/chunks/subset-b-002136_research.md`
- `subset-b-002137`: lines 47051-49491, `Docs/researches/chunks/subset-b-002137_research.md`
- `subset-b-002138`: lines 49492-51890, `Docs/researches/chunks/subset-b-002138_research.md`
- `subset-b-002139`: lines 51891-54330, `Docs/researches/chunks/subset-b-002139_research.md`
- `subset-b-002140`: lines 54331-56831, `Docs/researches/chunks/subset-b-002140_research.md`
- `subset-b-002141`: lines 56832-59202, `Docs/researches/chunks/subset-b-002141_research.md`
- `subset-b-002142`: lines 59203-61489, `Docs/researches/chunks/subset-b-002142_research.md`
- `subset-b-002143`: lines 61490-61940, `Docs/researches/chunks/subset-b-002143_research.md`

## Chunk Research

### subset-b-002118: lines 1-2434

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 1-2434

## Purpose

This chunk is generated AMD DCN 3.6.0 register field metadata. It has no executable C logic; it publishes `#define` constants for bit shifts and masks used by AMDGPU display code when packing, updating, and reading MMIO register fields. The matching `dcn_3_6_0_offset.h` header provides register addresses and base indices, while this file provides field layout inside those registers.

The assigned range starts at the header guard and covers early DCN 3.6.0 display/audio register blocks: HDA/Azalia controller and endpoint command rings, DCCG display clock generation and gating, DC perfmon blocks 0 through 2, DMU/RBBMIF status and timeout fields, GPU timer start/read selectors, and the first part of the display interrupt status chain through the beginning of `DISP_INTERRUPT_STATUS_CONTINUE13`.

Although the repository path is under a local `ceph-client` source tree, this file is AMDGPU display-driver hardware metadata and is unrelated to Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation sites, or locks in this chunk. Its public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the bit position of a field inside a hardware register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for that field.
- Numeric instance suffixes such as `AZCONTROLLER0`, `OTG3`, `DC_PERFMON2`, `DPPCLK3`, and `DISP_INTERRUPT_STATUS_CONTINUE10` describe repeated hardware instances or chained status registers.

Major macro families in this line range:

- HDA/Azalia controller capability and command transport fields: `GLOBAL_CAPABILITIES`, `GLOBAL_CONTROL`, `WAKE_ENABLE`, `STATE_CHANGE_STATUS`, `GLOBAL_STATUS`, stream interrupt enable/status registers, `WALL_CLOCK_COUNTER`, `STREAM_SYNCHRONIZATION`, CORB/RIRB base addresses, read/write pointers, DMA enables, memory-error status, response-interrupt controls, immediate command/response interfaces, DMA position buffer base addresses, and wall-clock aliases for `AZCONTROLLER0` and `AZCONTROLLER1`.
- HDA endpoint immediate command windows: `AZENDPOINT0/1_AZENDPOINT_IMMEDIATE_COMMAND_OUTPUT_INTERFACE_*` and `AZINPUTENDPOINT0/1_AZENDPOINT_IMMEDIATE_COMMAND_INPUT_INTERFACE_*` provide indexed/data command fields for output and input endpoints.
- DCCG display clock generation and clock gating: `DENTIST_DISPCLK_CNTL`, `DISPCLK_FREQ_CHANGE_CNTL`, `DCCG_GATE_DISABLE_CNTL`, `DCCG_GATE_DISABLE_CNTL2..6`, `DCCG_SOFT_RESET`, `DCCG_GLOBAL_FGCG_REP_CNTL`, `DCCG_CAC_STATUS`, and `DCCG_CAC_STATUS2`.
- Pixel, stream, symbol, DP, DPP, DSC, DTB, HDMI, and audio clocks: `PHYPLLA..E_PIXCLK_RESYNC_CNTL`, `DPSTREAMCLK_CNTL`, `SYMCLK32_SE_CNTL`, `SYMCLK32_LE_CNTL`, `DTBCLK_P_CNTL`, `OTG0..3_PIXEL_RATE_CNTL`, `OTG0..3_PHYPLL_PIXEL_RATE_CNTL`, `DP_DTO0..3_PHASE/MODULO`, `DP_DTO_DBUF_EN`, `DPPCLK0..3_DTO_PARAM`, `DPPCLK_CTRL`, `DPPCLK_DTO_CTRL`, `DSCCLK0..3_DTO_PARAM`, `DSCCLK_DTO_CTRL`, `DTBCLK_DTO0..3_PHASE/MODULO`, `DTBCLK_DTO_DBUF_EN`, `HDMICHARCLK0_CLOCK_CNTL`, `HDMISTREAMCLK_CNTL`, `HDMISTREAMCLK0_DTO_PARAM`, `DCCG_AUDIO_DTO_SOURCE`, `DCCG_AUDIO_DTO0/1_PHASE`, `DCCG_AUDIO_DTO0/1_MODULE`, and `DCCG_AUDIO_DTBCLK_DTO_PHASE/MODULO`.
- Timing and measurement support: `MILLISECOND_TIME_BASE_DIV`, `MICROSECOND_TIME_BASE_DIV`, `DCE_VERSION`, `DCCG_GTC_*`, `DCCG_DS_*`, `DCCG_VSYNC_OTG0..5_LATCH_VALUE`, `DCCG_VSYNC_CNT_CTRL`, and `DCCG_VSYNC_CNT_INT_CTRL`.
- DC perfmon blocks: repeated `DC_PERFMON0_*`, `DC_PERFMON1_*`, and `DC_PERFMON2_*` fields define event selection, counted-value selection, increment/run-enable mode, control select, counter state, report count, count-off interrupt controls, clock enable, start/stop trigger selectors, counter interrupt status/ack bits, and low/high counter readback.
- DMU/RBBMIF diagnostics: `DMCUB_RBBMIF_SEC_CNTL`, `RBBMIF_TIMEOUT`, `RBBMIF_STATUS`, `RBBMIF_STATUS_2`, `RBBMIF_INT_STATUS`, `RBBMIF_TIMEOUT_DIS`, `RBBMIF_TIMEOUT_DIS_2`, and `RBBMIF_STATUS_FLAG` cover timeout behavior, invalid-access reporting, FIFO status, interrupt status/ack bits, and per-client timeout disable bits.
- GPU timer and display interrupt status chain: `DC_GPU_TIMER_START_POSITION_V_UPDATE`, `DC_GPU_TIMER_START_POSITION_VSTARTUP`, `DC_GPU_TIMER_READ`, `DC_GPU_TIMER_READ_CNTL`, `DISP_INTERRUPT_STATUS`, and `DISP_INTERRUPT_STATUS_CONTINUE` through the first shift-only fields of `DISP_INTERRUPT_STATUS_CONTINUE13`.

Within lines 1-2434, the macro set is dominated by paired shift/mask definitions. The largest local families are display interrupt status registers, DCCG gate/clock controls, repeated DC perfmon blocks, RBBMIF timeout controls, and HDA/Azalia CORB/RIRB command transport.

## Control Flow

This header has no runtime control flow. Runtime use is indirect:

1. DCN 3.6 display code includes `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h`.
2. Token-pasting helper macros such as `SR`, `SRI`, `SF`, `DMUB_SR`, `DMUB_SF`, and IRQ table macros expand register and field names into symbols from this generated header.
3. DCN 3.6 resource, DMUB, and IRQ initialization code stores offsets, masks, and shifts in per-block register tables.
4. Operational code later uses register helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, and IRQ ack/set helpers. Those helpers use this chunk's masks and shifts to update individual fields without corrupting unrelated bits.

The macros do not encode ordering or access semantics. Callers must still sequence hardware correctly: stop or reset command rings before changing CORB/RIRB bases, wait for busy/done/status bits, program DTO phase/modulo and enable bits coherently, preserve shared clock-gating bits, latch GPU/vsync timer values before reading them, and acknowledge interrupts with the correct hardware write semantics.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed GPU state:

- HDA/Azalia fields represent controller capabilities, reset/flush state, stream interrupt enables/status, command and response ring pointers, DMA base addresses, immediate command status, DMA position buffer control, endpoint indexed command windows, and hardware wall-clock aliases.
- DCCG and DTO fields hold display clock dividers, source selectors, enable/status bits, double-buffer enables, clock-gate disables, soft-reset bits, pixel-rate source selections, error flags/counts, and audio/HDMI/DP/DPP/DSC/DTB clock ratios.
- Vsync/GTC/GPU timer fields expose global timing counters, OTG latch enables and latch values, interrupt status/clear selectors, timer read selectors, and per-display start positions.
- Perfmon fields hold programmable counter event selection, state, active/run-enable controls, thresholds/count-off behavior, interrupt status/ack bits, clock enable, and counter readback values.
- RBBMIF fields expose timeout values, timeout disables for clients 0 through 38, read-timeout and invalid-access status, invalid access address/type, FIFO empty/full state, and interrupt ack/status bits.
- Display interrupt status fields expose broad display events: OPTC underflow, OTG/IHC snapshot, forced vsync/count, trigger, vsync nominal, min-vtotal events, DIG fast training and stream-disable, HPD/HPDRX, AUX completion, DIO ALPM, RBBMIF timeout, I2C completion, vertical interrupts, DWB/WBSCL/DMCUB/MCIF events, AUX GTC sync status, perfmon interrupts, DCCG vsync latch interrupts, DRR timing updates, MPCC stalls, HUBBUB events, and DCPG domain power-up events.

Persistence is hardware-defined. Configuration fields usually remain until modeset reprogramming, suspend/resume, power gating, firmware reset, or ASIC reset. Status, ack, latch, busy, done, snapshot, clear, and interrupt fields can be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive. This generated mask file does not state access type, reset value, volatility, or side effects.

## Dependencies And Integration Points

This chunk must stay synchronized with AMD's generated DCN 3.6.0 register database and with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h`, which supplies matching register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c`, which includes this header and uses `DMUB_DCN35_REGS()`, `DMCUB_INTERNAL_REGS()`, and `DMUB_DCN35_FIELDS()` to initialize DCN 3.6 DMUB register offset/mask/shift tables from DCN 3.6 symbols.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c`, which includes this header and uses register-table token pasting for DCN 3.6 resource construction across DCCG, audio, DIO, DPP, DSC, hub, MMHUBBUB, AUX/I2C, and related display blocks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c`, which includes this header and constructs IRQ source tables using generated enable/status/ack masks for HPD, vblank, vline, page-flip, vupdate, and DMCUB outbox paths.
- Shared DC helpers under `display/dc/` and `display/dmub/` that consume initialized register tables for clock programming, display timing, perfmon readback, interrupt handling, audio setup, and firmware-mediated control.

The main integration pattern is C preprocessor token pasting. Macro spelling is therefore a source-level ABI between generated headers and handwritten/templated driver tables. Missing or renamed symbols usually fail at compile time; incorrect numeric masks or shifts can compile cleanly and only fail during hardware exercise.

## Risks And Edge Cases

- Generated masks are untyped constants. A wrong shift or mask can silently update neighboring hardware fields and appear as clock instability, no audio, missed interrupts, false diagnostics, stuck power/timer behavior, or display blanking.
- The chunk boundary is artificial. It starts at the beginning of the header but ends after `DISP_INTERRUPT_STATUS_CONTINUE13` shift fields for `DCPG_IHC_DOMAIN6_POWER_UP_INTERRUPT`; the corresponding `DISP_INTERRUPT_STATUS_CONTINUE13` mask fields and downstream status-chain registers are in later chunks.
- HDA/Azalia CORB/RIRB base-address and pointer fields include unimplemented low bits and reset bits. Treating address masks as full 32-bit addresses or mishandling pointer reset bits can break command transport or DMA position reporting.
- Immediate command status has busy/result-valid bits. Callers that use these masks without polling semantics can race command completion or read stale responses.
- DCCG gate-disable and soft-reset registers affect shared clock roots. Incorrect masks can leave symbol, DP stream, HDMI stream, DPP, DSC, DTB, audio, or PHY clocks gated or reset while an active pipe still depends on them.
- DTO phase/modulo fields are timing-sensitive. Bad DP, DPP, DSC, DTB, HDMI stream, or audio DTO masks can cause pixel-rate mismatch, FIFO errors, audio drift, link training failures, or intermittent underflow.
- Several status and control registers expose both enable and status fields for the same hardware path. The header does not distinguish readable status bits from writable control bits, so access semantics must come from hardware specs and caller code.
- Perfmon ack/status fields are tightly packed and repeated across blocks. Wrong counter select, interrupt ack, high/low read select, or active-state masks can produce misleading telemetry or acknowledge the wrong counter.
- RBBMIF timeout-disable bits span two registers and many clients. A wrong client bit can either mask a real timeout or create false timeout reporting for unrelated DMU/RBBMIF traffic.
- Display interrupt continuation relies on bit 31 chaining. Missing a continuation bit or consulting the wrong continuation register can hide downstream events such as DWB/MCIF, AUX GTC sync, perfmon, DCCG latch, DRR timing, MPCC stall, HUBBUB, or DCPG power-up interrupts.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN 3.6 enabled. The DCN 3.6 resource, DMUB, and IRQ token-pasting consumers should catch missing or renamed macros from this range.
- Mechanically verify every complete `__SHIFT` macro in lines 1-2434 has a matching `_MASK` macro and that each mask aligns with its shift and intended field width. Exclude fields deliberately cut off by the chunk boundary.
- Diff this DCN 3.6.0 range against AMD's authoritative register database and nearby generated DCN headers when compatibility is expected; focus on DCCG, perfmon, RBBMIF, and interrupt-chain deltas.
- Exercise modesets across DP and HDMI links, including pixel-clock changes, DP/HDMI stream-clock changes, DSC/DPP clock programming, dynamic refresh, suspend/resume, hotplug, link retraining, and repeated enable/disable cycles.
- Validate HDMI/DP audio paths that depend on HDA/Azalia controller and endpoint transport: command ring setup, immediate commands, wall-clock/DMA position readback, stream interrupts, and endpoint command indexing.
- Exercise DCCG timing behavior: DTO programming, double-buffer enables, clock-gating transitions, DPP/DSC/DTB/DP/audio clock enables, vsync counter latch/readback, and GPU timer read selectors.
- Exercise perfmon programming for blocks 0 through 2: event selection, start/stop triggers, counter active state, interrupt enable/ack, high/low readback, and count-off behavior.
- Exercise interrupt handling for HPD/HPDRX, AUX completion, vblank/vline/vupdate, DIG fast-training/video-disable, underflow, RBBMIF timeout, DWB/MCIF, AUX GTC sync, DCCG latch, DRR timing, MPCC stall, HUBBUB, and DCPG power-up events covered by the status chain in this chunk.
- Monitor kernel logs, DC traces, debugfs/register readback, display output, and audio playback for underflows, missed vblank/vline events, HPD/AUX loss, no-audio, channel drift, DTO status failures, RBBMIF timeout storms, invalid-access flags, stuck perfmon interrupts, and broken resume.

## Cross-Chunk Notes

This is a chunk-level document, not a final per-file report. Later chunks are required for the rest of `dcn_3_6_0_sh_mask.h`, including the masks for `DISP_INTERRUPT_STATUS_CONTINUE13`, later interrupt continuation registers, additional DCPG/DMU/HUBP/OPP/OTG/Azalia/display pipeline fields, and the closing header guard. The merge lane should preserve the source path and line range when reconciling this chunk with the rest of the generated DCN 3.6.0 shift/mask header.

### subset-b-002119: lines 2435-4812

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 2435-4812

## Scope

This chunk covers lines 2435-4812 of the generated AMD DCN 3.6.0 shift/mask header. The slice starts in the middle of the `DISP_INTERRUPT_STATUS_CONTINUE13` field list and ends at the `DMCUB_GPINT_DATAIN0` register marker. Within the assigned range there are 2,378 source lines, 196 commented register blocks, 1,082 `__SHIFT` macros, and 1,094 `_MASK` macros.

## Purpose

The file is a hardware register field map for the DCN 3.6 display block in the AMDGPU display driver. This chunk does not implement runtime logic; it defines the compile-time constants that let driver code extract, compose, enable, acknowledge, and route register bitfields without embedding literal bit positions in C code.

The covered registers describe three major areas:

- Display interrupt status continuation registers, including HUBBUB/HUBP, OPP, OPTC/OTG, audio (`AZ`), DCIO/DIG, DDC/I2C, DSC, HPO, and DMCUB interrupt status bits.
- Interrupt destination routing registers for DMU, DCPG, MMHUBBUB, WB, DCHUB, DPP, MPC, OPP, OPTC, OTG, DIG, I2C/DDC/HPD, HDCP/DIO/DCIO, AUX, DSC, and HPO sources.
- DMU, display power-gating, and DMCUB control/status registers, including clock gating, low-power/Z-state controls, domain power gate state, DMCUB memory window layout, DMCUB interrupts, security fault state, mailbox pointers, timers, scratch registers, and core control.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or callable APIs in this chunk. The effective interface is the generated macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit position.
- `REGISTER__FIELD_MASK` gives the already-shifted bit mask.
- Comment lines such as `//DISP_INTERRUPT_STATUS_CONTINUE24` and `// addressBlock: dce_dc_dmu_dmcub_dispdec` mark register and address-block boundaries used by generated address headers and driver-side register-list macros.

Important register groups in this chunk include:

- `DISP_INTERRUPT_STATUS_CONTINUE13` through `DISP_INTERRUPT_STATUS_CONTINUE25`: chained display interrupt status bitmaps. Bit 31 commonly carries the continuation flag to the next status register.
- `DC_GPU_TIMER_START_POSITION_*`: start-position field maps for vready, flip, v-update-no-lock, and flip-away GPU timer events across display pipes.
- `*_INTERRUPT_DEST`: destination selection fields that route many interrupt sources to an interrupt destination.
- `CC_DC_PIPE_DIS`, `DMU_CLK_CNTL`, `DMCUB_SMU_INTERRUPT_CNTL`, `SMU_INTERRUPT_CONTROL`, `ZSC_*`, and low-power clock-gating delay registers in the DMU misc address block.
- `DOMAIN*_PG_CONFIG` and `DOMAIN*_PG_STATUS` for display power-gating domains 0-3, 16-19, and 22-25.
- `DCPG_INTERRUPT_STATUS*` and `DCPG_INTERRUPT_CONTROL_*` for power-gate event status/type/enable fields across domain power-up and power-down events.
- `DMCUB_REGION*`, `DMCUB_REGION3_CW*`, and their high/top/offset fields for DMCUB memory aperture and code-window configuration.
- `DMCUB_INTERRUPT_ENABLE`, `DMCUB_INTERRUPT_ACK`, `DMCUB_INTERRUPT_STATUS`, and `DMCUB_INTERRUPT_TYPE` for DMCUB timer, inbox/outbox, GPINT, fault, power-up, and OTG resync interrupt handling.
- `DMCUB_SEC_CNTL`, `DMCUB_MEM_CNTL`, inbox/outbox base/size/read/write pointer registers, `DMCUB_TIMER_*`, `DMCUB_SCRATCH0` through `DMCUB_SCRATCH18`, and `DMCUB_CNTL`.

## Control Flow

This header has no local control flow. Its constants enter control flow when included by DCN 3.6 driver code:

- `display/dmub/src/dmub_dcn36.c` includes this header and uses `FD_MASK(reg, field)` / `FD_SHIFT(reg, field)` to populate the DCN 3.5-style DMUB register descriptor used for DCN 3.6. The macros expand directly to names from this header.
- `display/dc/irq/dcn36/irq_service_dcn36.c` includes this header and uses generated `_MASK` constants in `IRQ_REG_ENTRY` and `IRQ_REG_ENTRY_DMUB` expansions to build `irq_source_info_dcn36`. For example, the DMCUB outbox entry uses `DMCUB_INTERRUPT_ENABLE__DMCUB_OUTBOX1_READY_INT_EN_MASK` and `DMCUB_INTERRUPT_ACK__DMCUB_OUTBOX1_READY_INT_ACK_MASK`.
- `display/dc/resource/dcn36/dcn36_resource.c` includes this header alongside the offset header, then register-helper macros build register/field tables for DCN 3.6 display components.

The continuation status macros matter for interrupt traversal: status registers expose many independent sources, and the `DISP_INTERRUPT_STATUS_CONTINUE*` bit indicates that later continuation registers may also contain pending sources.

## State And Persistence Behavior

The header itself stores no runtime state. The state it describes is hardware-resident MMIO state:

- Interrupt status bits are latched by display hardware until acknowledged or cleared through companion control/ack registers.
- Interrupt destination fields affect where hardware reports events.
- Power-gating config/status fields reflect desired and finite-state-machine power state for display domains.
- DMCUB mailbox base/size/pointer fields persist in MMIO while the device is powered and define shared communication rings between host driver and DMCUB firmware.
- DMCUB scratch registers are general-purpose firmware/driver communication state and can carry diagnostic or boot/runtime metadata.
- DMCUB security and fault registers expose persistent fault status until cleared through fields such as `DMCUB_INST_FETCH_FAULT_CLEAR` and `DMCUB_DATA_WRITE_FAULT_CLEAR`.

## Dependencies And Integration Points

This header depends on matching generated address definitions in `dcn_3_6_0_offset.h`; shift/mask constants are only useful when paired with the corresponding register address macro. Driver code also depends on helper macros such as `FD_MASK`, `FD_SHIFT`, `SR`, `SRI`, and `IRQ_REG_ENTRY` to compose register tables.

Integration points are concentrated in AMDGPU display code:

- DMUB service setup initializes DMCUB register offset/mask/shift tables from these constants.
- DC IRQ service maps hardware source IDs to `dc_irq_source` values and uses these masks to describe enable and acknowledge register operations.
- DCN 3.6 resource construction feeds display blocks with register and field descriptors for hub, pipe, timing, link, DSC, clocking, power, and firmware paths.
- DMCUB firmware communication uses the inbox/outbox, GPINT, interrupt type, scratch, memory region, and security/fault fields from this range.

## Risks

- A wrong shift or mask silently targets the wrong hardware bit. In interrupt paths this can lose events, acknowledge the wrong source, or leave an interrupt storm uncleared.
- Continuation-register chain bits must align with hardware. A bad `DISP_INTERRUPT_STATUS_CONTINUE*` mask can make the IRQ handler stop early or read beyond the intended status chain.
- DMCUB inbox/outbox pointer or size masks are full-width; mismatched address/pointer interpretation can corrupt firmware communication rings.
- Power-gating and DMCUB security-control fields affect device bring-up, low-power transitions, and fault recovery. Incorrect bit definitions can cause hangs that only appear on specific ASIC revisions or power-management paths.
- This is generated ASIC-specific data. Manual edits are high risk because adjacent DCN versions have similar names but not necessarily identical register coverage.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware/runtime oriented:

- Build the AMDGPU display driver with DCN 3.6 enabled; missing or renamed field macros should fail where `FD_MASK`, `FD_SHIFT`, and IRQ register macros expand.
- Exercise display hotplug, HPD RX, page flip, vblank/vstartup, vupdate-no-lock, AUX/DDC, DSC, and DMCUB outbox paths on DCN 3.6 hardware and confirm interrupts are delivered and acknowledged once.
- Validate DMCUB firmware boot and command processing, including inbox/outbox pointer movement and low-priority outbox-ready interrupts.
- Run suspend/resume and display power-gating scenarios to catch bad `DOMAIN*_PG_*`, `DCPG_INTERRUPT_*`, `DMU_CLK_CNTL`, and `ZSC_*` field definitions.
- Check kernel logs for AMDGPU DC IRQ storms, DMCUB timeout/fault messages, HPD failures, AUX transaction failures, and display pipe underflow after display mode changes.

### subset-b-002120: lines 4813-7453

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 4813-7453

## Purpose

This chunk is a generated AMD DCN 3.6.0 register field shift/mask header segment. It does not implement executable logic; it defines `#define` constants used by the AMD display driver register helper layer to pack, unpack, update, and read individual hardware register fields safely. The chunk contributes 2,086 shift/mask macros for 422 register names spanning DMCUB communication tail registers, display writeback (DWB), writeback color processing, display/DC perf monitors, MCIF/MMHUBBUB writeback memory plumbing, HDA/Azalia audio controller registers, and DCHUBBUB arbitration/SDPIF controls.

The naming convention is uniform:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for the field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit MMIO register.

The generated constants are paired with offset headers and consumed through AMD display macros such as `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, `REG_SET`, `REG_READ`, and register list macros that initialize per-IP `shift` and `mask` tables.

## Major Register Groups

### DMCUB tail fields

The first part continues DMCUB definitions from the previous chunk. It includes general-purpose interrupt mailbox registers `DMCUB_GPINT_DATAIN0` through `DMCUB_GPINT_DATAIN6`, `DMCUB_GPINT_DATAOUT`, `DMCUB_UNDEFINED_ADDRESS_FAULT_ADDR`, low-power wake enable, memory power control, timer, processor ID, soft reset, region space selection, and scratch registers `DMCUB_SCRATCH19` through `DMCUB_SCRATCH23`.

These fields are full-width mailbox/scratch values or small control bits. Consumers in `display/dmub/src` read/write `DMCUB_GPINT_*`, scratch, reset, timer, and fault fields when booting DMUB firmware, sending commands, collecting debug state, or handling DMCUB faults.

### DWB top and frame capture

The `dce_dc_wb0_dispdec_dwb_top_dispdec` block defines display writeback enable, clock gating, memory power, frame capture, crop window, CRC, output format/denorm, backpressure, overflow, host-read throttle, and soft reset fields. Important registers include:

- `DWB_ENABLE_CLK_CTRL`: enables DWB, disables selected DWB clock gates, selects test clocks, and controls fine-grain clock-gating replacement.
- `DWB_MEM_PWR_CTRL`: controls output FIFO and OGAM LUT memory power force/disable/state bits.
- `FC_MODE_CTRL`, `FC_FLOW_CTRL`, `FC_WINDOW_START`, `FC_WINDOW_SIZE`, `FC_SOURCE_SIZE`: configure frame capture enable/rate, cropping, stereo eye selection, new-content signaling, first-pixel delay, and source/window dimensions.
- `DWB_UPDATE_CTRL`: supplies update lock and pending state for coherent DWB programming.
- `DWB_CRC_*`: controls DWB CRC collection, masks RGBA channels, and exposes CRC signature values.
- `DWB_OUT_CTRL`: selects output format, denormalization mode, and output min/max pixel values.
- `DWB_OVERFLOW_STATUS` and `DWB_OVERFLOW_COUNTER`: expose overflow flag/status/ack/mask/type and overflow coordinates.

The DWB driver uses these fields in `display/dc/dwb/dcn30/dcn30_dwb.c`. For example, `dwb3_enable()` sets `DWB_ENABLE_CLK_CTRL.DWB_ENABLE`, programs `FC_*`, color-processing, and `DWB_OUT_CTRL`, then enables `FC_MODE_CTRL.FC_FRAME_CAPTURE_EN`. `dwb3_update()` and `dwb3_set_fc_enable()` use `DWB_UPDATE_CTRL.DWB_UPDATE_LOCK` around multi-register updates.

### DWB color processing and OGAM

The `dce_dc_wb0_dispdec_dwbcp_dispdec` block defines writeback color pipeline fields:

- `DWB_HDR_MULT_COEF` for HDR multiplier coefficient programming.
- `DWB_GAMUT_REMAP_MODE`, `DWB_GAMUT_REMAP_COEF_FORMAT`, and A/B remap coefficient registers for 3x4 color matrix programming.
- `DWB_OGAM_CONTROL`, LUT index/data/control fields, and two banks of OGAM PWL region definitions (`RAMA` and `RAMB`).

The OGAM blocks define start/end base and slope values per channel plus 34 exp regions encoded as LUT offsets and segment counts. These constants back the DWB output gamma path; register-list macros in `dcn30_dwb.h` map them into `struct dcn30_dwbc_registers`, `struct dcn30_dwbc_shift`, and `struct dcn30_dwbc_mask`.

### DC perf monitor blocks

The chunk contains three nearly identical perfmon address blocks:

- `DC_PERFMON3_*` for DWB/writeback.
- `DC_PERFMON4_*` for MMHUBBUB.
- `DC_PERFMON5_*` for HDA/Azalia.

Each block defines per-counter selection/control fields, counter state fields, perfmon state/report count/control, interrupt status/ack bits, current value high/low fields, and read selector fields. These are diagnostic/performance collection registers rather than normal display programming flow. Incorrect masks would mainly break telemetry, profiling, or interrupt-based counter collection.

### MCIF_WB and MMHUBBUB writeback memory

The `dce_dc_mmhubbub_mcif_wb0_dispdec` block defines writeback buffer manager and memory-interface fields:

- `MCIF_WB_BUFMGR_SW_CONTROL` and `MCIF_WB_BUFMGR_STATUS`: enable, software interrupt enable/ack/status, overrun interrupt, lock, current/next buffer, buffer tag, line counters, and address-fence enable.
- `MCIF_WB_BUF_1_STATUS` through `MCIF_WB_BUF_4_STATUS` plus `STATUS2`: active, locked, overflow, disable/mode, buffer tag, next buffer, current line, new content, color depth, TMZ, overrun, and stereo eye flag per buffer.
- Buffer base address registers for Y and chroma planes, including high address registers; luma/chroma sizes; per-buffer resolution; pitch; VMID/security; p-state timing; arbitration; and VCE control.

The adjacent `dce_dc_mmhubbub_mmhubbub_dispdec` block adds MMHUBBUB-level watermarks, warmup, clock/power/reset, outstanding counters, DMU error status, WBIF unit ID, and VMID warmup controls. These fields integrate DWB buffer ownership with the MMHUBBUB memory path and SoC/display clock/power management.

### HDA/Azalia audio

The HDA section spans controller, root codec, miscellaneous, stream, endpoint, and input endpoint address blocks:

- Controller fields cover clock gating, DTO phase/module, SOCCLK deep sleep exit, underflow filler sample, data/BDL/CORB/RIRB/DP DMA snoop and isochronous settings, payload capabilities, output arbiter latency hiding, input/output CRC engines, and audio memory power control/status.
- Root codec fields expose vendor/device/revision IDs, channel count, resync FIFO, function group type, supported rates/formats/power states, power state control, reset, subsystem ID response, converter synchronization, DC audio port connectivity, input port connectivity, and GTC group offsets.
- `AZ_CLOCK_CNTL` and `AZ_MEM_GLOBAL_PWR_REQ_CNTL` control Azalia clock selection/gating and global memory power requests.
- `AZF0STREAM0` through `AZF0STREAM15` provide indexed stream register access through `AZALIA_STREAM_REG_INDEX`, `AZALIA_STREAM_REG_WRITE_EN`, and `AZALIA_STREAM_REG_DATA`.
- `AZF0ENDPOINT0` through `AZF0ENDPOINT7` and `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7` provide indexed codec endpoint data windows.

These masks bridge DC display audio support to the HDA/Azalia MMIO layout. The fields are especially sensitive to indexed access protocols: the index register selects an internal stream/endpoint register and the data register supplies or returns the 32-bit value.

### DCHUBBUB arbitration, timing, and SDPIF

The `dce_dc_dchubbubl_hubbub_dispdec` block defines memory arbitration and timing controls:

- `DCHUBBUB_ARB_DF_REQ_OUTSTAND`, `DCHUBBUB_ARB_SAT_LEVEL`, `DCHUBBUB_ARB_QOS_FORCE`, and `DCHUBBUB_ARB_DRAM_STATE_CNTL` control outstanding request limits, saturation level, forced QoS, self-refresh, p-state allowance, C-state/deep-sleep policy, and hysteresis.
- `DCHUBBUB_ARB_USR_RETRAINING_CNTL` and watermark sets A-D define data urgency, USR retraining, ref cycles per trip to memory, self-refresh enter/exit including Z8, UCLK/FCLK p-state change, and fractional urgent bandwidth.
- `DCHUBBUB_ARB_HOSTVM_CNTL` contains host VM force disable/status/limit fields for PRQ, read FIFO, return FIFO, and stall behavior.
- `DCHUBBUB_ARB_WATERMARK_CHANGE_CNTL` handles watermark-change requests, interrupt disable/enable/status/clear, urgent watermark selection, pending state, and timing status.
- `DCHUBBUB_ARB_MALL_CNTL` tracks MALL use and prefetch completion.
- Timer, surface checker address/in-use registers, VTG controls, soft reset, clock control, DCFCLK gating/delays, latency measurement, vline snapshot, ROB overflow status/clear, timeout detection/interrupts, and `FMON_CTRL` complete the block.

The block ends by entering `dce_dc_dchubbubl_hubbub_sdpif_dispdec` and beginning `DCHUBBUB_SDPIF_CFG0`, with only the first four field definitions present in this chunk: no outstanding request, port status, data response status, and response status. The following chunk continues the remaining SDPIF fields.

HUBBUB code uses these fields for watermark programming, clock and power decisions, timeout/error diagnostics, and SDPIF ownership. For example, `hubbub2_program_watermarks()` writes watermark and outstanding-request registers; `hubbub2_get_dchub_ref_freq()` reads `DCHUBBUB_GLOBAL_TIMER_CNTL`; `hubbub2_read_state()` captures watermark and DRAM-state control; `hubbub32_set_sdp_control()` writes `DCHUBBUB_SDPIF_CFG0.SDPIF_PORT_CONTROL`.

## APIs, Types, and Integration Points

This header provides preprocessor constants rather than C APIs. Its integration contract is with generated and hand-written display register plumbing:

- Offset headers such as `dcn_3_6_0_offset.h` provide register addresses/base indices; this file provides field shifts/masks.
- Register list macros in IP-specific headers, such as `DWBC_COMMON_REG_LIST_DCN30()` and `DWBC_COMMON_MASK_SH_LIST_DCN30()`, bind register names and fields into typed register/shift/mask structs.
- Driver code accesses fields through the register helper macros. The helpers use each field's shift and mask pair to read-modify-write only the intended bits.
- DMUB, DWB, HUBBUB/MMHUBBUB, perfmon, and HDA/Azalia code are the primary consumers for this chunk.

There are no functions, structs, dynamic allocations, reference counts, locks, or direct control-flow branches in this chunk itself. Control flow is external: higher-level DC code decides when to enable DWB, program color, update watermarks, read perf counters, or manipulate audio streams, and this header supplies the bit layout needed for those operations.

## State and Persistence Behavior

The state represented by these macros is persistent hardware MMIO state, not kernel memory state. Writes persist in the display/audio hardware register file until changed by the driver, reset by hardware, or affected by power management. Several groups have explicit state/ack/current conventions:

- DWB update state uses `DWB_UPDATE_LOCK` and `DWB_UPDATE_PENDING` so multiple DWB fields can be staged and applied coherently.
- DWB has current-state fields such as `FC_FRAME_CAPTURE_EN_CURRENT`, `DWB_GAMUT_REMAP_MODE_CURRENT`, and OGAM current selectors.
- Buffer manager and MCIF fields track active buffers, current/next buffer numbers, buffer tags, current line, overrun flags, TMZ state, and software/VCE locks.
- Interrupt/status fields frequently pair status bits with ack/clear bits, such as DWB overflow, MCIF writeback SW interrupt, perfmon interrupts, Azalia CRC completion, DMU error clear, DCHUBBUB timeout clear, and watermark-change interrupt clear.
- Memory/clock power fields expose force, disable, mode select, and state/status bits for DMCUB, DWB, MMHUBBUB/WBIF, and Azalia memories.

Because the file only defines masks, it has no persistence logic itself. Correct persistence behavior depends on consumers respecting hardware sequencing: lock before multi-field DWB updates, acknowledge status bits only when intended, avoid lowering watermarks unless safe, and account for indexed stream/endpoint register windows in Azalia.

## Dependencies

The direct dependency is the generated DCN 3.6.0 register naming scheme. The constants must match the corresponding hardware spec and the matching offset header. At compile time, consumers depend on:

- `reg_helper.h` and display register helper macros.
- IP-specific register structs and mask/shift structs for DWB, HUBBUB, DMUB, and audio blocks.
- Matching generation of register names across resource headers and ASIC-specific initialization tables.

The file is not self-validating. A field name typo, mask width mismatch, or shift/mask mismatch will compile if no consumer references it, but referenced mismatches can silently corrupt adjacent hardware fields.

## Risks and Failure Modes

- Bitfield drift against hardware is the main risk. A wrong shift or mask can write the wrong MMIO bits, causing display capture failure, audio malfunction, power-management instability, memory-request starvation, or interrupts that cannot be cleared.
- Generated header and offset-header mismatch can target the right field layout at the wrong address, or the right address with the wrong field layout.
- Partial chunk boundaries matter for generated documentation: this chunk begins mid-DMCUB block and ends mid-`DCHUBBUB_SDPIF_CFG0`. Final merged research should reconcile those edges with neighboring chunks.
- DWB update locking mistakes in consumers can expose partially programmed capture/color state to hardware.
- Watermark, p-state, C-state, and DCFCLK fields are performance and correctness sensitive; bad programming can cause underflow/overflow, missed self-refresh opportunities, or visible glitches.
- Indexed Azalia stream/endpoint access is protocol-sensitive. Incorrect index/write-enable/data field masks can read or write the wrong internal audio register.
- Status/ack/clear bits are side-effectful. Treating them like ordinary fields can lose diagnostic evidence or clear pending interrupts unexpectedly.

## Test Signals

Useful validation signals for changes touching this header or its consumers include:

- Build coverage for AMDGPU display code with DC enabled, ensuring all generated register/field references resolve.
- DWB enable/update/disable tests or runtime traces showing `DWB_ENABLE`, `FC_FRAME_CAPTURE_EN`, crop/source size, output format, and OGAM programming behave as expected.
- DWB CRC and overflow diagnostics: CRC values should update when enabled, and overflow flags/counters should clear and report consistently.
- Watermark programming traces from HUBBUB paths, including A-D watermark sets, global timer reference divider, `DCHUBBUB_ARB_WATERMARK_CHANGE_CNTL`, and timeout/ROB overflow status.
- Suspend/resume and power-management tests covering DMCUB, DWB, MMHUBBUB/WBIF, DCFCLK, and Azalia memory/clock power fields.
- Audio playback/HDMI/DP audio tests covering Azalia stream indexed registers, payload capabilities, DMA snoop/isochronous controls, and CRC/status fields.
- Perfmon smoke tests confirming counters can be configured, run, read, interrupt/ack, and reset without corrupting unrelated bits.

### subset-b-002121: lines 7454-9969

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 7454-9969

## Scope

This chunk is part of AMD DCN 3.6 generated ASIC register metadata. It contains C preprocessor definitions for register-field bit shifts and masks, not executable code. The covered range starts in the `dce_dc_dchubbubl_hubbub_sdpif_dispdec` block after `DCHUBBUB_SDPIF_CFG0`, continues through DCHUBBUB return path, VM request, DC perfmon, HUBP0/HUBPREQ0/HUBPRET0/CURSOR0_0, and ends at the beginning of HUBPREQ1 VM aperture definitions.

The definitions are consumed by AMD display driver register-list and field-list macros. Adjacent integration code maps register offsets from `dcn_3_6_0_offset.h` and shift/mask symbols from this header into typed register tables used by `REG_GET`, `REG_UPDATE`, `REG_UPDATE_2`, and related accessor macros.

## Purpose

The purpose of this header range is to encode the hardware contract for selected DCN 3.6 display hub fields:

- DCHUBBUB SDPIF and VM address aperture programming, including SDP request status, credit control, pipe security levels, no-allocation flags, physical request controls, and local HBM lock range fields.
- DCHUBBUB return-path memory power, CRC, DCC statistics, compression buffer, DET buffer, debug, and memory power mode/status fields.
- DCN VM context registers for contexts 0-15, default addresses, fault controls, fault status, and fault address capture.
- DC performance monitor 6 fields.
- HUBP0 surface, tiling, viewport, request sizing, control, clock, virtual memory page, MALL, measurement, and MALL status fields.
- HUBPREQ0 surface address, metadata address, surface control, flip sequencing, flip interrupts, in-use tracking, TTU/QoS, VM/aperture, timing/prefetch/delivery, cursor settings, memory power, pstate, and status fields.
- HUBPRET0 read-return control, memory power, read-line, and interrupt fields.
- CURSOR0_0 cursor control, surface address, size, position, hot spot, stereo, memory power, and DMData fields.
- DC performance monitor 7 fields.
- HUBP1 surface/control fields and the first part of HUBPREQ1, through `HUBPREQ1_DCN_VM_SYSTEM_APERTURE_HIGH_ADDR`.

This is source-tree-aligned low-level display metadata. Its correctness determines whether higher-level DCN 3.6 driver code writes the intended bits when programming display memory fetch, VM, cursor, CRC, performance counters, and power controls.

## Important APIs, Types, And Macros

There are no C functions or types declared in this chunk. The important interface is the naming convention for generated preprocessor symbols:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask within the 32-bit MMIO register.
- Register group comments such as `//HUBPREQ0_DCSURF_FLIP_CONTROL` and address-block comments divide the generated definitions into hardware blocks.

Important register families in this chunk include:

- `DCHUBBUB_SDPIF_CFG1`, `DCHUBBUB_SDPIF_CFG2`, `DCHUBBUB_SDPIF_PIPE_*`, and `SDPIF_REQUEST_RATE_LIMIT` for display fabric request behavior.
- `DCN_VM_FB_LOCATION_*`, `DCN_VM_AGP_*`, `DCN_VM_CONTEXT{0..15}_*`, `DCN_VM_DEFAULT_ADDR_*`, `DCN_VM_FAULT_CNTL`, `DCN_VM_FAULT_STATUS`, and `DCN_VM_FAULT_ADDR_*` for display VM and fault reporting.
- `DCHUBBUB_CRC_CTRL`, `DCHUBBUB_CRC0_VAL_*`, and `DCHUBBUB_CRC1_VAL_*` for hub CRC capture.
- `DCHUBBUB_DCC_STAT*`, `DCHUBBUB_COMPBUF_CTRL`, `DCHUBBUB_DET{0..3}_CTRL`, `DCHUBBUB_MEM_PWR_MODE_CTRL`, `DCHUBBUB_MEM_PWR_STATUS`, and `COMPBUF_MEM_PWR_CTRL_*` for compression, DET, and memory power state.
- `DC_PERFMON6_*` and `DC_PERFMON7_*` for performance-counter control, state, counter values, high/low count latches, and interrupt/status fields.
- `HUBP0_*` and `HUBP1_*` for hub pipe surface format, tiling, viewport, request size, underflow/status/control, clock gating, VMPG, MALL, and measurement windows.
- `HUBPREQ0_*` and `HUBPREQ1_*` for surface pitch/address/control, flips, VM, TTU/QoS, prefetch, vblank/nominal/flip parameters, per-line delivery, cursor settings, memory power, pstate force, and status.
- `HUBPRET0_*` for hub pipe return path control and interrupts.
- `CURSOR0_0_*` for cursor plane setup and DMData.

The key consumers are display driver macros and structures such as `HUBBUB_REG_LIST_DCN35`, `HUBBUB_MASK_SH_LIST_DCN35`, `HUBP_MASK_SH_LIST_DCN35`, and older inherited HUBP/HUBBUB mask lists. For DCN 3.6, `dcn36_resource.h` includes `DCHUBBUB_CRC_CTRL` in `HWSEQ_DCN36_REG_LIST()`, while `dcn35_hubbub.h` lists many DCHUBBUB registers present in this chunk, including `DCN_VM_FB_LOCATION_*`, `DCN_VM_AGP_*`, `DCHUBBUB_DET*`, `DCHUBBUB_COMPBUF_CTRL`, `DCN_VM_FAULT_*`, `SDPIF_REQUEST_RATE_LIMIT`, `DCHUBBUB_SDPIF_CFG0`, `DCHUBBUB_SDPIF_CFG1`, and memory/power/debug registers. HUBP inherited lists in `dcn10_hubp.h`, `dcn20_hubp.h`, `dcn30_hubp.h`, `dcn31_hubp.h`, `dcn32_hubp.h`, and `dcn35_hubp.h` consume fields like `HUBP0_DCHUBP_CNTL`, `HUBPREQ0_DCSURF_SURFACE_CONTROL`, `CURSOR0_0_CURSOR_CONTROL`, `HUBPREQ0_UCLK_PSTATE_FORCE`, and `HUBP0_DCHUBP_MALL_CONFIG`.

## Control Flow

This chunk has no runtime control flow. Its definitions influence control flow indirectly when driver code expands register accessor macros:

- Initialization paths such as `hubbub35_init()` update SDPIF fields. For example, the driver writes `DCHUBBUB_SDPIF_CFG0.SDPIF_PORT_CONTROL` and `DCHUBBUB_SDPIF_CFG1.SDPIF_MAX_NUM_OUTSTANDING`; the bit positions and masks for those fields come from this header range.
- HUBP programming paths use inherited field-list macros to program surface configuration, DCC/TMZ flags, tiling, viewport, cursor, TTU, VM, and flip state through `REG_UPDATE`-style wrappers.
- VM fault state paths use the `DCN_VM_FAULT_CNTL` and `DCN_VM_FAULT_STATUS` fields to clear errors, choose status mode, enable interrupts, and read/write fault indicators.
- CRC and perfmon paths use these masks to enable capture, select sources, latch one-shot/continuous counters, read values, and clear status bits.

The runtime sequence is therefore: a DCN resource constructor selects DCN 3.6 offset and shift/mask tables; component constructors store pointers to those tables; later display programming calls pass register and field names to accessor macros; the generated shifts and masks here are used to isolate or compose field values in MMIO writes and reads.

## State And Persistence Behavior

The file itself persists no software state. It describes persistent hardware register state across several domains:

- Control fields such as `SDPIF_PORT_CONTROL`, `SDPIF_FORCE_SNOOP`, `DCHUBBUB_CRC_EN`, `DCHUBBUB_CRC_CONT_EN`, HUBP blank/disable/underflow controls, cursor enable/mode, MALL selection, VMPG settings, TTU/QoS, and VM L1 TLB controls remain in hardware until reprogrammed, reset, or power-gated.
- Status and sticky fields include SDPIF response/credit errors, force-IO status, DCC stats, memory power status, VM fault status/address, perfmon status/counter values, HUBP underflow/no-outstanding/status, flip occurred/status bits, HUBPRET interrupt status, and cursor DMData status.
- Clear fields such as `SDPIF_RESPONSE_STATUS_CLEAR`, `SDPIF_REQ_CREDIT_ERROR_CLEAR`, `DCN_VM_ERROR_STATUS_CLEAR`, `DMDATA_VM_FAULT_STATUS_CLEAR`, `DMDATA_VM_UNDERFLOW_STATUS_CLEAR`, `SURFACE_FLIP_CLEAR`, `SURFACE_FLIP_AWAY_CLEAR`, and several interrupt clear fields are write-sensitive. Incorrect masks can fail to clear a latched fault or accidentally clear unrelated status.
- Address and VM fields store page table base/start/end, system aperture boundaries, surface addresses, metadata addresses, cursor surface addresses, and in-use address captures. These values persist as programmed display fetch state and must match current plane/cursor memory layout and VMID ownership.
- Power-control fields represent forced memory power modes, shutdown enables, request/ack/status, and clock-gating replication disable bits. Misprogramming can leave blocks powered unexpectedly or inaccessible during display updates.

## Dependencies And Integration Points

Primary dependencies:

- `dcn_3_6_0_offset.h` supplies register offsets and base indices that pair with the shift/mask symbols in this file.
- AMD DC register access macros in the display stack require exact symbol names. Macros such as `SR`, `SRII`, `HUBBUB_SF`, `HUBP_SF`, and `TF_SF` expand register and field names into structure initializers that depend on these generated defines existing.
- DCN 3.5 and earlier component code is reused by DCN 3.6 in places. The chunk is therefore integrated through inherited DCN 3.x HUBBUB and HUBP field lists, not just files named `dcn36`.
- DMUB and hardware sequencer code interacts with cursor and hub state. `dmub_cmd.h` mirrors cursor control bitfields, and DCN 3.5/4.0 hardware sequencer code serializes cursor state using fields with names matching `CURSOR0_0_CURSOR_CONTROL`.

Concrete integration examples in this tree:

- `display/dc/resource/dcn36/dcn36_resource.h` includes `DCHUBBUB_CRC_CTRL` in the DCN 3.6 hardware sequencer register list.
- `display/dc/hubbub/dcn35/dcn35_hubbub.h` lists DCHUBBUB registers from this chunk and maps additional masks through `HUBBUB_MASK_SH_LIST_DCN35`.
- `display/dc/hubbub/dcn35/dcn35_hubbub.c` writes `DCHUBBUB_SDPIF_CFG0.SDPIF_PORT_CONTROL` and `DCHUBBUB_SDPIF_CFG1.SDPIF_MAX_NUM_OUTSTANDING` during hubbub initialization.
- `display/dc/hubp/dcn35/dcn35_hubp.h` inherits DCN 3.2/3.1/3.0 HUBP fields and adds DCN 3.5 clock-gating fields; the inherited field lists consume many `HUBP0_*`, `HUBPREQ0_*`, and `CURSOR0_0_*` symbols defined in this chunk.
- `display/dc/hubbub/dcn20/dcn20_hubbub.c` reads `DCN_VM_FAULT_CNTL.DCN_VM_ERROR_STATUS_MODE`, relying on the VM fault field definitions shared by later generations.

## Risks

- Generated-header drift is high impact. If a shift or mask mismatches DCN 3.6 hardware, the driver can write the wrong field while compiling cleanly.
- Cross-generation reuse increases copy/paste risk. Nearby DCN 3.2, 3.5.1, and DCN 3.6 headers contain similar field names, but some fields differ, such as the `DF_CSTATE_DISALLOW` bit in `DCHUBBUB_SDPIF_CFG0` for this chunk. Reusing a different-generation mask table can subtly alter power or fabric behavior.
- Status-clear fields are especially sensitive. A one-bit mask error can leave sticky VM/fabric/flip/interrupt status uncleared, or can clear an adjacent diagnostic bit and hide a real fault.
- Address high/low fields, VM context bounds, VMID fields, and in-use capture fields span multiple registers. Incorrect field widths can truncate addresses, point display fetches at the wrong memory, or make fault reports misleading.
- HUBPREQ surface-control fields combine TMZ, DCC enable, DCC independent block, and metadata TMZ state for primary/secondary surfaces. Incorrect masks can break protected content, DCC metadata fetch, or chroma plane setup.
- HUBP/HUBPREQ0 and HUBP/HUBPREQ1 symmetry is easy to damage. Instance-specific prefixes must keep the same field layout where hardware expects replicated pipes, but the chunk ends mid-HUBPREQ1, so merge/reconciliation must combine this with the following chunk before making whole-file conclusions.
- Memory power and clock-gating fields can interact with display underrun behavior. Wrong force/shutdown/status masks could cause intermittent blanking, underflow, or resume failures that only appear under low-power or multi-plane workloads.
- Perfmon fields are broad and include many selector/status bits. A mismatch may not affect normal display output but can invalidate performance diagnostics or automated telemetry.

## Test Signals

Useful validation signals for changes touching this header or its generator:

- Compile coverage for DCN 3.6 display code with all generated register lists enabled. Missing or renamed shift/mask symbols should fail during structure initialization or macro expansion.
- Boot/probe smoke tests on DCN 3.6 hardware, confirming resource creation, hubbub/HUBP construction, and display bring-up without MMIO access faults.
- Display plane tests covering primary and secondary surfaces, DCC enabled/disabled, chroma planes, cursor enable/move/resize, page flips, triple buffering, and stereo/GSL flip paths. These exercise `HUBPREQ*_DCSURF_*`, `HUBP*_DCSURF_*`, `CURSOR0_0_*`, and flip interrupt fields.
- VM and fault-injection tests covering invalid surface addresses, VMID changes, page table base/start/end programming, aperture low/high bounds, and fault clear/readback through `DCN_VM_FAULT_CNTL`, `DCN_VM_FAULT_STATUS`, and fault address registers.
- Low-power and clock-gating tests across idle, blanking, PSR/sub-VP/MALL, resume, and zero-frame-buffer paths. These exercise SDPIF, HUBP/HUBPREQ/HUBPRET memory power, MALL, and pstate force fields.
- CRC tests that enable one-shot and continuous hub CRC capture, select pipe/surface/data source, and compare `DCHUBBUB_CRC{0,1}_VAL_*` readback against expected frame contents.
- Performance-counter diagnostics using `DC_PERFMON6_*` and `DC_PERFMON7_*`, including start/stop, counter selection, interrupt status, counter clear, and high/low readback.
- Regression comparison against vendor-generated headers for the same ASIC revision. For this kind of file, a mechanical diff against trusted register XML/header output is often the strongest signal.

## Notes For Merge Lane

This chunk should be merged with the adjacent `dcn_3_6_0_sh_mask.h` chunks before producing the final per-file report. The range begins after the `DCHUBBUB_SDPIF_CFG0` comment and ends mid-HUBPREQ1, at `HUBPREQ1_DCN_VM_SYSTEM_APERTURE_HIGH_ADDR`, so both boundaries are partial register-block boundaries. Whole-file analysis should account for earlier DCHUBBUB arbitration/global timer fields and later HUBPREQ1/HUBP2+ replicated pipe definitions.

### subset-b-002122: lines 9970-12458

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 9970-12458

## Purpose

This chunk is generated AMD DCN 3.6.0 register field metadata. It contains no executable C code; it publishes preprocessor constants that describe field bit positions and masks inside DCN hardware registers. The matching `dcn_3_6_0_offset.h` header supplies MMIO offsets and base indices, while this shift/mask header supplies the layout used by AMDGPU display code to pack and decode register fields without overwriting adjacent bits.

The assigned range begins at `HUBPREQ1_DCN_VM_SYSTEM_APERTURE_HIGH_ADDR` after the immediately preceding low-address aperture register, then covers the rest of HUBP/HUBPREQ/HUBPRET/cursor/perfmon definitions for pipe 1, all equivalent definitions for pipe 2, and most equivalent definitions for pipe 3. It ends inside `HUBPRET3_HUBPRET_INTERRUPT`, before that register's remaining status/int-status shifts and masks. Adjacent chunks are required for complete file-level treatment of split registers at both boundaries.

Although this source is under a local `ceph-client` mirror path, the file is AMDGPU display-driver hardware metadata and is not related to Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocations, locks, or direct includes in this chunk. The effective API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: zero-based bit position for a register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field.
- Instance prefixes such as `HUBP2_`, `HUBPREQ3_`, `HUBPRET1_`, `CURSOR0_2_`, and `DC_PERFMON9_` identify repeated display pipe instances and per-pipe subblocks.

The range contains 2,120 macro lines covering 337 distinct register tokens. Major families are:

- `HUBPREQ1_*`, continuing from a previous chunk: VM system aperture high address, L1 TLB control, display logic generator timing parameters, prefetch settings, vblank/flip/nominal PTE and metadata timing parameters, per-line delivery, cursor request scheduling, reference-to-pixel frequency conversion, DRQ limit, request-side memory power control/status, UCLK p-state force, and status registers.
- `HUBPRET1_*`: return-side control, DET buffer plane-1 base, 3-to-2 packing disable, component crossbar source selection, return-side memory power control/status, read-line programming, read-line interrupt control/status, current read-line value, and read-line window status.
- `CURSOR0_1_*`: cursor enable/mode/request/magnify/pitch/TMZ/chunk/perfmon fields, cursor surface address and high bits, size, position, hot spot, stereo, destination offset, cursor memory power state, and DMDATA address/control/QoS/status/software access fields.
- `DC_PERFMON8_*`: per-HUBP performance counter control, counter selection, counter state, perfmon enable/clear/interrupt control, threshold/current values, and high/low counter readback.
- `HUBP2_*`: pipe 2 request and surface-front-end fields for surface format, swizzle, tiling, primary/secondary luma/chroma viewports, request size, HUBP enable/blank/status/underflow paths, clock control/status, VMPG/MALL/sub-VP configuration, debug doorbell/debug, DCFCLK/DPPCLK measurement windows, and MALL status.
- `HUBPREQ2_*`: complete pipe 2 surface pitch, VMID, primary/secondary luma/chroma surface and metadata addresses, surface control/TMZ/DCC state, flip control and flip interrupt, surface in-use and earliest-in-use readbacks, expansion mode, TTU/QoS controls, DMDATA VM control, VM aperture, L1 TLB, DLG timing, prefetch, vblank/flip/nominal timing, delivery timing, cursor settings, memory power, UCLK p-state force, and status fields.
- `HUBPRET2_*`, `CURSOR0_2_*`, and `DC_PERFMON9_*`: pipe 2 equivalents of the return path, cursor, DMDATA, and perfmon register layouts.
- `HUBP3_*` and `HUBPREQ3_*`: pipe 3 equivalents of HUBP/HUBPREQ surface, request, VM, DLG, TTU, memory power, p-state, and status fields.
- `HUBPRET3_*`: pipe 3 return-side control, memory power, read-line control, and the first part of read-line/vblank interrupt fields. `HUBPRET3_HUBPRET_INTERRUPT` is split at the end boundary.

## Control Flow

This header has no runtime control flow. Runtime behavior is macro-driven:

1. DCN 3.6 code includes `dcn_3_6_0_offset.h` and this shift/mask header.
2. Register-table macros such as `SRI_ARR`, `HUBP_REG_LIST_DCN30_RI`, `HUBP_MASK_SH_LIST_DCN35`, and IRQ `IRQ_REG_ENTRY` paste block, instance, register, and field tokens into names defined here.
3. DCN 3.6 resource setup populates per-block register, shift, and mask tables. In this tree, `dcn36_resource.c` initializes four HUBP register instances with `HUBP_REG_LIST_DCN30_RI(id)` and uses `HUBP_MASK_SH_LIST_DCN35(__SHIFT/_MASK)` for HUBP masks and shifts.
4. Operational code then uses helpers such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, `REG_GET_7`, `REG_READ`, and `REG_WAIT`. Those helpers combine offsets, shifts, and masks from the generated tables to write MMIO registers or extract field values.

The macros do not encode programming order. Modeset, flip, cursor, VM, deadline, memory-power, and read-line code still owns sequencing: program VM/system aperture before enabling translations, program deadline/TTU values from DML output, update surface addresses and flip controls around vupdate/vblank rules, wait for read-line/vblank status where required, and preserve status/clear semantics for interrupt-like fields.

## State And Persistence Behavior

The file stores no software state and persists nothing by itself. It describes MMIO-backed GPU state:

- HUBP/HUBPREQ surface fields hold per-plane format, tiling, swizzle, viewport, address, metadata, TMZ, DCC, pitch, VMID, flip, and in-use state for luma and chroma surfaces.
- VM and aperture fields hold display-side translation behavior: system aperture high/low bounds, L1 TLB enable, system access mode, unmapped access behavior, and advanced-driver-model enable.
- DLG, TTU, vblank, flip, nominal, and per-line-delivery fields hold computed memory-fetch deadlines and request-delivery timing from Display Mode Library calculations.
- Cursor and DMDATA fields hold cursor image address, geometry, hot spot, stereo behavior, cursor request mode, cursor memory-power state, and display metadata DMA/software access status.
- HUBPREQ/HUBPRET memory power fields hold force/disable controls and status for DPTE, MPTE, metadata, PDE, DMROB, and PIXCDC memories.
- UCLK p-state force fields can disallow data or cursor memory clock p-state changes for timing-sensitive scenarios.
- HUBPRET crossbar and read-line fields hold return-path component mapping and read-line window/interrupt/readback state.
- PERFMON8/9 fields hold per-pipe performance counter selection, enable, clear, state, thresholds, current values, interrupt status/ack, and high/low counter data.
- Status registers expose transient hardware state such as blanking, HUBP enable, underflow, MPTE row ready, chunk request position, self-refresh, p-state allowance, QoS urgency, recovery/flush, flip active, clock states, MALL hit/miss, and VM/DMDATA faults or late/underflow conditions.

Persistence is hardware-defined. Configuration bits generally remain until modeset reprogramming, power-gating reset, suspend/resume, or ASIC reset. Status, interrupt, clear, pending, counter, and readback fields may be read-only, sticky, self-clearing, or write-one-to-clear. This generated header only describes bit layout; it does not document access type or side effects.

## Dependencies And Integration Points

This chunk must stay synchronized with AMD's generated DCN 3.6.0 register database and with local consumers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h`, the matching register-offset/base-index header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c`, which includes this header, builds DCN 3.6 resource register tables, and uses the HUBP shift/mask lists for the fields in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c`, which includes this header and uses `FD_MASK`/`FD_SHIFT` expansions through DMUB DCN35 field lists to initialize firmware-accessible register metadata for DCN 3.6.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c`, which includes this header and expands `HUBPREQn_DCSURF_SURFACE_FLIP_INTERRUPT` fields for pflip interrupt enable/ack programming.
- Shared HUBP code under `display/dc/hubp/`, especially `dcn10_hubp.c`, `dcn30_hubp.c`, and `dcn32_hubp.c`, which uses the generated tables for VM L1 TLB programming, deadline/DMDATA timing, cursor and surface state readback, HUBPREQ/HUBPRET memory-power readback, read-line waits, and UCLK p-state force updates.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.h`, whose reusable `HUBP_REG_LIST_*_RI` macros enumerate most register names covered here and are reused by DCN 3.6 resource setup.
- DML and HWSS/resource paths that calculate deadline, prefetch, MALL/SubVP, p-state, and memory-fetch values later written into these registers.

The integration contract is token spelling plus numeric correctness. Missing or renamed macros usually fail at compile time through token-pasted register tables. Incorrect numeric masks or shifts can compile cleanly and then program the wrong hardware bits at runtime.

## Risks And Edge Cases

- The chunk boundary is artificial. It begins with `HUBPREQ1_DCN_VM_SYSTEM_APERTURE_HIGH_ADDR`; the preceding low-address aperture and earlier pipe 1 HUBP/HUBPREQ fields are in the previous chunk. It ends after only the early `HUBPRET3_HUBPRET_INTERRUPT` shift definitions; the remaining shifts and all masks for that register continue in the next chunk.
- These are untyped integer constants. A one-bit shift or mask error can corrupt adjacent hardware fields without compiler diagnostics.
- Repeated instance layouts are easy to update inconsistently. A pipe 2 or pipe 3-only mismatch can leave single-pipe testing clean while multi-display, ODM, or pipe-reassignment scenarios fail.
- Surface address, metadata address, VMID, aperture, L1 TLB, TMZ, and DCC fields are security- and correctness-sensitive. Bad values can cause VM faults, protected-content mishandling, stale metadata fetches, corruption, black screens, or GPU hangs.
- DLG/TTU/vblank/flip/nominal delivery masks are timing-critical. Incorrect field widths can produce underflow, missed prefetch, late flips, failed SubVP/MALL behavior, unstable p-state transitions, or visible corruption only at high bandwidth.
- Memory power and p-state force fields interact with clock/power management. Wrong masks can leave memories forced on, power-gated when needed, or disallow UCLK transitions unnecessarily.
- Read-line and interrupt fields are side-effect-sensitive. Misprogramming clear/status/mask bits can hide vblank/read-line events, trigger spurious interrupts, or break waits such as `HUBPRET_READ_LINE_STATUS.PIPE_READ_VBLANK`.
- Perfmon fields are diagnostic but can still be stateful. Wrong enable/clear/ack/threshold fields produce misleading performance data or stale interrupts.

## Test Signals

Useful validation combines generated-header checks with hardware/display behavior:

- Build AMDGPU/DC with DCN 3.6 enabled. Token-pasted resource, DMUB, HUBP, and IRQ tables should catch missing or misspelled macro names.
- Mechanically verify every `__SHIFT` in the range has the expected `_MASK`, masks align with shifts and expected bit widths, and split boundary registers are reconciled with neighboring chunks before reporting mismatches.
- Diff the range against AMD's authoritative DCN 3.6 register database or adjacent generated DCN headers when compatibility is expected.
- Exercise multi-pipe modesets across pipe instances 1, 2, and 3: enable/disable, hotplug, suspend/resume, resolution/refresh changes, plane movement between pipes, and repeated atomic commits.
- Exercise surface formats and memory layouts that rely on HUBP/HUBPREQ fields: RGB, YUV 4:2:0, chroma viewports, DCC on/off, TMZ surfaces, metadata address changes, primary/secondary flips, and VMID changes.
- Exercise cursor and DMDATA paths: cursor enable/disable, size/position/hot spot changes, stereo cursor, cursor p-state force, DMDATA programming, and VM fault/late/underflow status readback.
- Exercise DML-sensitive timing paths: high-bandwidth modes, SubVP/MALL, DRR/vblank stretch, p-state changes, flip stress, and underflow detection while monitoring DC traces and kernel logs.
- Check debugfs or register-state capture for `hubp3_read_reg_state`-style readbacks of HUBPREQ/HUBPRET, memory-power, UCLK p-state, aperture, deadline, and read-line registers.
- Validate pflip, vblank/read-line, and related interrupt behavior for no missed acks, no interrupt storms, and no stuck status/clear bits.

## Cross-Chunk Notes

Previous chunks are needed for the beginning of pipe 1 HUBP/HUBPREQ definitions, including `HUBPREQ1_DCN_VM_SYSTEM_APERTURE_LOW_ADDR`. The next chunk continues `HUBPRET3_HUBPRET_INTERRUPT` with the remaining status/int-status shifts and all masks, then proceeds into `HUBPRET3_HUBPRET_READ_LINE_VALUE`, read-line status, and pipe 3 cursor definitions.

### subset-b-002123: lines 12459-14996

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 12459-14996

## Purpose

This chunk is a generated AMD DCN 3.6.0 register shift/mask slice. It contains no executable logic; it exports C preprocessor constants that describe bit positions and bit masks for memory-mapped display-controller registers. Driver code combines these constants with the matching `dcn_3_6_0_offset.h` register offsets so AMDGPU display helpers can pack, unpack, and update individual fields without hard-coding numeric bit layouts at call sites.

The requested range contains 2,113 `#define` entries, split into 1,052 `__SHIFT` macros and 1,061 `_MASK` macros, plus 389 register-name comments and 12 address-block comments. The chunk starts in the middle of the `HUBPRET3_HUBPRET_INTERRUPT` definition group and ends in the middle of `CM1_CM_GAMCOR_RAMB_REGION_18_19`, so both boundaries are artificial line-split boundaries rather than semantic hardware boundaries.

Although this file lives under a local `ceph-client` source mirror, this chunk is AMDGPU DCN display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocation paths, or direct I/O operations in this range. The public interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating or preserving that field during read/modify/write operations.

The main register families covered here are:

- `HUBPRET3_*`: tail of HUBP request/read-line status support for pipe vblank and read-line interrupts, current read line, snapshot read line, and inside/outside read-line status.
- `CURSOR0_3_*`: HUBP instance 3 cursor control, surface address, size, position, hot spot, stereo offsets, destination offset, cursor memory power state, dynamic metadata address/control/QoS/status/software-data fields.
- `DC_PERFMON10_*`: HUBP-side performance monitor and counter controls, counter state selection, count-off interrupt configuration, per-counter interrupt status/acknowledge bits, and low/high counter value fields.
- `CNVC_CFG0_*`: DPP0 converter/configuration fields for surface pixel format, format control, floating-point bias/scale, color keying, alpha LUT, pre-dealpha, pre-CSC matrices for main and B paths, coefficient format, pre-degamma, and pre-realpha.
- `CNVC_CUR0_*`: DPP0 converter cursor overlay fields for cursor enable/mode/color and floating-point cursor scale/bias.
- `DSCL0_*`: DPP0 scaler fields for coefficient RAM access, scaler mode and tap control, 2-tap controls, manual replication, horizontal/vertical scaling ratios and initial phases for luma/chroma/bottom fields, black color, update/autocal, overscan, OTG blanking, recout/MPC size, line-buffer format/memory/counter, DSCL memory power, and output-buffer controls.
- `CM0_*`: DPP0 color-management fields for post-CSC, gamut remap, bias, gamma-correction control, LUT index/data/control, gamma-correction RAM A/B start/end/slope/base/offset/region programming, HDR multiplier coefficients, memory power status, dealpha, coefficient format, debug access, and DPP CRC values.
- `DPP_TOP0_*`: top-level DPP0 control, soft reset, CRC control, and host-read controls.
- `DC_PERFMON11_*`: DPP-side performance monitor/counter fields mirroring the `DC_PERFMON10_*` shape for another performance-monitor instance.
- `CNVC_CFG1_*`, `CNVC_CUR1_*`, and `DSCL1_*`: beginning of the same converter, cursor, and scaler register layout for DPP1.
- `CM1_*`: beginning of DPP1 color-management register layout, continuing through post-CSC, gamut remap, bias, gamma-correction control, LUT access, and most of the gamma-correction RAM A/B region programming included before the chunk boundary.

Many groups are mechanically repeated per hardware instance. DPP0 and DPP1 use the same field names with different numeric instance prefixes, and `DC_PERFMON10` and `DC_PERFMON11` share the same performance-counter register shape.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU display code that includes this generated header:

1. DCN 3.6 code includes `dcn_3_6_0_offset.h` and this shift/mask header.
2. Register-list macros token-paste register and field names into per-block register, shift, and mask tables.
3. DCN 3.6 constructors wire those tables into resource-pool objects, IRQ service structures, DMUB service register tables, DPP/DSCL/HUBP blocks, and hardware-sequencer helpers.
4. Runtime display paths call register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`; the helpers use these masks and shifts to touch only the intended MMIO bits.

The macros do not encode sequencing rules. Consumers still need to program cursor memory before enabling the cursor, update scaler ratios and taps in the right update window, load gamma/CSC LUTs in hardware-defined order, acknowledge perfmon interrupts correctly, and coordinate DPP/HUBP state with pipe lock, vblank, power, and clock transitions.

## State And Persistence Behavior

This chunk stores no software state and persists nothing directly. It describes hardware-visible state in DCN 3.6 registers:

- HUBP vblank/read-line interrupt mask/type/clear/status bits and sampled read-line state.
- Cursor state for enablement, mode, memory address, dimensions, on-screen position, hot spot, stereo layout, trusted-memory-zone marking, request behavior, memory power, and dynamic metadata transport.
- Performance-monitor state for event selection, counting mode, hardware start/stop/count-off selection, active state, counter values, and interrupt status/acknowledge bits.
- Converter and cursor-overlay state for DPP pixel format conversion, alpha handling, floating-point scale/bias, color keying, pre-CSC/pre-degamma, and cursor colors.
- Scaler state for filter coefficients, tap counts, scaling ratios, phase initialization, recout dimensions, overscan, line-buffer memory layout, and DSCL/OBUF memory power.
- Color-management state for post-CSC, gamut remap, gamma-correction LUT programming, RAM A/B region metadata, HDR coefficients, memory power, debug index/data, and CRC capture.
- DPP top-level state for reset, CRC, and host-read behavior.

Persistence is hardware-defined. Configuration fields generally remain until a modeset, plane update, pipe reprogramming, power-gating event, suspend/resume, GPU reset, or ASIC reset rewrites them. Status, interrupt, snapshot, debug, CRC, and counter fields may be read-only, sticky, write-one-to-clear, self-clearing, clock-gated, or valid only while the associated pipe and block are powered. This generated header does not identify those access semantics; consumers must rely on the register specification and block-specific driver code.

## Dependencies And Integration Points

This file must remain synchronized with AMD's generated DCN 3.6.0 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h` supplies the matching MMIO addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c` includes both DCN 3.6 generated headers while initializing DMUB register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c` includes the same headers for DCN 3.6 IRQ source setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c` includes them for DCN 3.6 resource construction and hardware-sequencer register tables.
- Shared display block headers such as DPP, DSCL, HUBP, timing-generator, IRQ, and register-helper code consume these generated constants through macro tables rather than including this chunk's field names one by one at most call sites.

The most direct behavioral integration from this range is plane composition and scanout: cursor programming, DPP format conversion, scaler configuration, color management, per-pipe CRC/debug support, HUBP timing interrupts, and DC performance monitoring.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while touching the wrong MMIO bit, corrupting adjacent fields, or silently disabling a feature.
- The file is generated. Manual edits risk diverging from the authoritative register database, the matching offset header, firmware assumptions, and silicon documentation.
- The chunk boundaries are not semantic. The first `HUBPRET3_HUBPRET_INTERRUPT` fields started before line 12459, and the `CM1_CM_GAMCOR_RAMB_REGION_18_19` mask set continues after line 14996.
- Repeated DPP0/DPP1 and perfmon layouts make copy/generator drift hard to see. DPP0 working does not prove DPP1 fields are correct, and one perfmon instance can fail independently from another.
- Cursor address, size, position, pitch, stereo, and hot-spot masks are user-visible. Off-by-one or width errors can cause missing cursors, clipped cursors, wrong stereo cursor placement, invalid memory reads, or TMZ/security mismatches.
- Scaler ratio, phase, tap, and coefficient fields are precision-sensitive. Incorrect masks can cause image blur, ringing, chroma misalignment, crop errors, blank output, or filter RAM programming failures.
- Color-management fields are interoperability- and color-accuracy-sensitive. Wrong CSC, gamut-remap, gamma-region, LUT, bias, coefficient-format, or HDR multiplier masks can produce subtle color regressions that are not caught by simple modeset smoke tests.
- Interrupt/status/ack fields are side-effect-sensitive. Confusing status with clear/ack or enable bits can cause missed vblank/read-line events, stuck perfmon interrupts, or interrupt storms.
- Power-state fields for cursor, DSCL, OBUF, and CM memory can interact with clock gating and power gating; writing them at the wrong time can produce intermittent resume, modeset, or underflow failures.

## Test Signals

Useful validation combines generated-header checks with DCN 3.6 hardware behavior:

- Build AMDGPU display support with DCN 3.6 enabled. Missing or renamed constants should fail in DCN36 DMUB, IRQ, resource, DPP, DSCL, HUBP, or hardware-sequencer register-table construction.
- Mechanically compare this range against AMD's authoritative DCN 3.6.0 register source and the adjacent `dcn_3_6_0_offset.h` names. Allow for the known artificial boundary at the start and end of the requested line slice.
- Run static consistency checks that expected register fields have both `__SHIFT` and `_MASK` definitions when the complete register group is considered across adjacent chunks.
- Exercise cursor enable/disable, movement, hotspot changes, size changes, 2x magnification, stereo cursor paths, TMZ cursor surfaces, suspend/resume, and rapid modesets.
- Exercise DPP scaler paths across identity scale, up/downscale, chroma formats, fractional ratios, recout changes, overscan, line-buffer pressure, and filter coefficient reloads.
- Validate color paths with CRC or visual/color tests for pre-CSC, post-CSC, gamut remap, gamma correction RAM A/B, HDR multipliers, alpha/dealpha/realpha, color keying, and pixel-format conversion.
- Exercise perfmon setup and interrupts for `DC_PERFMON10` and `DC_PERFMON11`, checking counter start/stop, count-off behavior, status/ack handling, and counter high/low reads.
- Watch kernel logs and display diagnostics for vblank/read-line interrupt loss, cursor corruption, scaler underflow, CRC mismatches, color-management regressions, stuck perfmon interrupt status, memory-power transition failures, and resume-only display artifacts.

## Cross-Chunk Notes

The previous chunk contains the beginning of the `HUBPRET3_HUBPRET_INTERRUPT` group. The next chunk continues `CM1_CM_GAMCOR_RAMB_REGION_18_19` and the remaining DCN 3.6 register-field namespace. The final per-file research document should merge adjacent chunks before making whole-file claims about all DCN 3.6 shift/mask definitions or all DPP/HUBP instances.

### subset-b-002124: lines 14997-17536

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 14997-17536

## Scope

This chunk covers a generated AMD DCN 3.6 register shift/mask header slice. It contains 2,114 `#define` entries over 2,540 lines, split almost evenly between `__SHIFT` constants and `_MASK` constants. The covered region starts in the tail of DPP instance 1 color-management gamma-correction RAM-B fields, then covers DPP instance 2 configuration, scaler, color-management, top, CRC, and perfmon fields, and ends partway through DPP instance 3 color-management gamma-correction RAM-B region definitions.

The file is data-only: it declares preprocessor constants for hardware register bitfields and contains no C functions, structs, storage allocation, or executable control flow.

## Purpose

The constants describe bit positions and bit masks for DCN 3.6 display pipe processor (DPP) register fields. They are consumed by the AMD display driver register-helper layer to populate shift and mask tables used by `REG_SET`, `REG_UPDATE`, `REG_GET`, and wait/poll helpers. Correctness is hardware-contract correctness: each constant must match the corresponding ASIC register definition in `dcn_3_6_0_offset.h` and the DCN 3.x DPP programming code.

Major hardware areas in this chunk:

- `CM1`, `CM2`, and `CM3`: color management, including post-CSC, gamut remap, bias, gamma-correction LUT host access, gamma-correction piecewise-linear region descriptors, HDR multiplier, dealpha, coefficient format, memory power control/status, debug, and DPP CRC result fields.
- `CNVC_CFG2` and `CNVC_CFG3`: converter surface format, format control, fixed-point bias/scale, color keying, alpha LUT, pre-dealpha, pre-CSC matrix programming, coefficient format, pre-degamma, and pre-realpha.
- `CNVC_CUR2` and `CNVC_CUR3`: cursor enable/mode, color registers, and cursor floating-point scale/bias.
- `DSCL2` and `DSCL3`: display scaler coefficient RAM access, scaler mode, taps, 2-tap sharpness control, manual replication, scale ratios, initial phases, black color, update/autocal, overscan, OTG blanking geometry, recout/MPC size, line-buffer format and memory control, memory power state, and output-buffer power/control.
- `DPP_TOP1` and `DPP_TOP2`: DPP clock gates, dynamic gate disables, fine-grain clock-gating repeat disable, soft reset bits for CNVC/DSCL/CM/OBUF, DPP CRC control, and host-read throttling.
- `DC_PERFMON12` and `DC_PERFMON13`: DPP-local display performance monitor counter selection, state, control, counter-value readback, interrupt status/ack, high/low value registers, and read selectors.

## Important Definitions

This chunk follows the standard register-field naming pattern:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned field mask.
- Instance prefixes such as `CM2_`, `CNVC_CFG3_`, `DSCL2_`, and `DPP_TOP2_` bind otherwise repeated register layouts to a hardware DPP instance.

Notable field groups:

- Gamma correction RAM descriptors use `RAMA` and `RAMB` banks with mirrored field shapes: start control, start slope/base, end base/slope, offsets, and paired `REGION_N_N+1` descriptors. Region pairs pack two LUT offsets and segment counts into one register: low region offset at bits 0-8, low region segment count at bits 12-14, high region offset at bits 16-24, high region segment count at bits 28-30.
- CSC and gamut-remap matrix registers pack two 16-bit coefficients per register, with first coefficient in bits 0-15 and second in bits 16-31. The `_B_` suffixed copies provide alternate/banked coefficient sets.
- Format and color-conversion controls expose enable/bypass/state bits (`CNVC_BYPASS`, `ALPHA_EN`, `CNVC_UPDATE_PENDING`, `PRE_CSC_MODE_CURRENT`, `PRE_DEGAM_MODE`, `PRE_REALPHA_EN`) that higher-level plane programming uses to synchronize pixel format and color pipeline changes.
- DSCL geometry fields use packed X/Y or width/height values, generally low component in bits 0-12 or 0-13 and high component in bits 16-28 or 16-29.
- Memory-power controls expose force/disable fields and status/state fields for gamma correction memory, scaler LUT/line-buffer groups, and OBUF memory. These are used by power sequencing paths that may poll state after changing force bits.
- CRC controls define one-shot/continuous operation, source select, stereo/interlace/pixel/cursor format selection, and a 16-bit CRC mask. CRC value registers expose full 32-bit R/G/B/A channel results.
- Perfmon definitions include eight per-counter interrupt status/ack bits, counter run/stop selection, counted-value type, active state, high/low counter value readback, and threshold/interrupt control fields.

## Control Flow

There is no runtime control flow in this header. Its effective control flow is through compile-time macro expansion in DCN resource setup:

- `dcn36_resource.c` includes both `dcn_3_6_0_offset.h` and this `dcn_3_6_0_sh_mask.h`.
- `dcn36_resource.c` constructs `tf_shift` with `DPP_REG_LIST_SH_MASK_DCN35(__SHIFT)` and `tf_mask` with `DPP_REG_LIST_SH_MASK_DCN35(_MASK)`.
- `DPP_REG_LIST_SH_MASK_DCN35` extends the DCN 3.0 common DPP field list and uses `TF_SF(...)` entries to refer to symbols from this header, such as `CM0_CM_GAMCOR_CONTROL__CM_GAMCOR_MODE__SHIFT` or `DSCL0_SCL_MODE__DSCL_MODE_MASK`. For instances 2 and 3, equivalent generated definitions in this chunk must remain layout-compatible with the common instance-0 macro pattern because the register table initialization substitutes instance-specific register addresses while sharing the same field layouts.
- Runtime DPP code under `display/dc/dpp/` uses the populated shift/mask tables through register-helper macros, so a bad bit definition here turns into incorrect read-modify-write behavior rather than an obvious local compile-time control-flow error.

## State and Persistence

The header itself persists no state. It describes hardware state in MMIO registers. State affected by these fields lives in display hardware until overwritten, reset, power-gated, or reprogrammed during modeset/plane-update paths.

Important state classes:

- Color-pipeline programming state: CNVC format controls, pre-CSC/pre-degamma/pre-realpha, CM post-CSC, gamut-remap, bias, HDR multiplier, dealpha, and gamma-correction LUT regions.
- Double-buffer/current-state indicators: fields such as `*_MODE_CURRENT`, `*_SELECT_CURRENT`, `CNVC_UPDATE_PENDING`, `CUR0_UPDATE_PENDING`, `SCL_UPDATE_PENDING`, and `CM_UPDATE_PENDING` expose or coordinate pending hardware updates.
- Memory power state: `GAMCOR_MEM_PWR_STATE`, `LUT_MEM_PWR_STATE`, `LB_G*_MEM_PWR_STATE`, and `OBUF_MEM_PWR_STATE` reflect power-management state machines.
- Diagnostic state: CRC values and perfmon counters are readback state used for validation, telemetry, and debugging.

Because this is an ASIC register contract, persistence risks come from stale or mismatched constants: an incorrect mask may silently preserve stale bits, clear unrelated hardware state, or poll the wrong state field.

## Dependencies and Integration Points

Primary dependencies:

- `dcn_3_6_0_offset.h` provides register addresses and base-index macros; this file provides field layout for those addresses.
- `display/dc/resource/dcn36/dcn36_resource.c` includes this header and instantiates DPP shift/mask tables.
- `display/dc/dpp/dcn35/dcn35_dpp.h` defines the DPP mask/shift list shape used by DCN36 resource setup.
- `display/dc/dpp/dcn30/dcn30_dpp.h`, `dcn20_dpp.h`, and `dcn10_dpp.h` define common DPP field lists and the register helper field expectations that many entries in this chunk satisfy.
- `reg_helper.h` and the register access macros consume the populated shift/mask structs for MMIO read/write operations.

Integration expectations:

- Instance-specific symbols must exist for every DPP instance present in the offset table. This chunk contributes instance 2 and 3 symbols and the tail of instance 1 symbols.
- Register field names must match the names used in common DPP macro lists. Renaming a generated define without updating macro lists causes build failures; changing a numeric value without a name change causes runtime hardware misprogramming.
- The generated `L`-suffixed constants are intended as 32-bit masks despite C's platform-dependent `long` width; consumers store them in `uint32_t` mask fields.

## Risks

- Hardware layout drift: DCN 3.6 may differ subtly from DCN 3.5/3.2 even when the common DPP field-list macros are reused. Missing or stale generated masks can produce incorrect color conversion, scaling, cursor, CRC, or power behavior.
- Banked gamma LUT programming is dense and repetitive. Region pairs, RAMA/RAMB bank selection, and RGB channel suffixes are easy to misalign in generated output. A single region mask error can corrupt transfer-function programming for only part of the curve.
- Power-management fields are high impact. Incorrect `*_MEM_PWR_FORCE`, `*_MEM_PWR_DIS`, or status masks can leave memories powered down during programming or cause waits to poll unrelated bits.
- Update-pending/current fields are synchronization-sensitive. Bad masks for `CNVC_UPDATE_PENDING`, `SCL_UPDATE_PENDING`, `CM_UPDATE_PENDING`, or `*_CURRENT` fields can cause code to assume a programming update has landed when hardware has not latched it.
- Perfmon and CRC fields are often test/debug only, so regressions may escape normal functional display tests unless CRC/perf telemetry paths are exercised.
- This generated header has duplicate-looking layouts across DPP instances. Manual edits are risky because local consistency does not prove ASIC correctness; generated-source provenance should be preserved.

## Test Signals

Useful validation signals for changes touching this chunk:

- Build the AMDGPU display driver with DCN36 enabled; missing symbols from this header should fail at compile time in `dcn36_resource.c` or DPP shift/mask struct initialization.
- Exercise modesets and plane updates across DPP instances 1, 2, and 3, especially configurations that use scaling, cursor, alpha, FP16/format conversion, pre-CSC, post-CSC, gamut remap, and gamma correction.
- Validate color correctness with gamma/gamut/HDR paths enabled, including bank switching for GAMCOR RAMA/RAMB and LUT region programming.
- Check DSCL behavior for 4:4:4 and 4:2:0 content, horizontal/vertical scaling, chroma scaling, overscan, recout sizing, and line-buffer partition programming.
- Run display CRC capture or IGT/KMS CRC-style checks where available; mismatches can indicate DPP CRC source/format/mask or color-pipeline field errors.
- Exercise DC perfmon setup/readback if supported by local diagnostics, including interrupt ack/status paths and high/low counter reads.
- Test runtime power-management transitions or display idle/resume paths that force or disable GAMCOR, DSCL LUT/LB groups, or OBUF memories, watching for timeout waits on `*_MEM_PWR_STATUS`.

### subset-b-002125: lines 17537-20052

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 17537-20052

## Purpose

This chunk is a generated AMD DCN 3.6.0 register shift/mask header segment. It contains 2,099 preprocessor definitions and no executable C code. The macros describe bit positions and masks for fields in display color-management, DPP instance 3, DC performance monitor blocks, MPC/MPCC composition blocks, and MPCC output-gamma/gamut-remap blocks.

Consumers combine these `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants with register offsets from the matching `dcn_3_6_0_offset.h` header and AMD display register helpers. The values are hardware ABI data: build-time names may compile successfully while an incorrect bit number or mask silently programs the wrong MMIO field at runtime.

## Important API surface

There are no functions or types in this range. The public surface is the generated macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit for a hardware field.
- `REGISTER__FIELD_MASK` gives the packed field mask in the 32-bit register value.
- Driver-side register table macros and access helpers use these names through `FD_SHIFT`, `FD_MASK`, `SF`, `SE_SF`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and related AMD DC MMIO helper patterns.

The major field groups are:

- `CM3_CM_GAMCOR_RAMB_REGION_16_17` through `CM3_CM_GAMCOR_RAMB_REGION_32_33`, followed by `CM3_CM_HDR_MULT_COEF`, `CM3_CM_MEM_PWR_CTRL`, `CM3_CM_MEM_PWR_STATUS`, `CM3_CM_DEALPHA`, `CM3_CM_COEF_FORMAT`, `CM3_CM_TEST_DEBUG_INDEX`, `CM3_CM_TEST_DEBUG_DATA`, and `CM3_DPP_CRC_VAL_*`. These cover the tail of DPP3 color-management gamma-correction RAM B region descriptors, HDR multiplier, gamma-correction memory power control/status, dealpha controls, coefficient-format selection, CM test/debug index/data, and DPP CRC result channels.
- `DPP_TOP3_DPP_CONTROL`, `DPP_TOP3_DPP_SOFT_RESET`, `DPP_TOP3_DPP_CRC_CTRL`, and `DPP_TOP3_HOST_READ_CONTROL` in address block `dce_dc_dpp3_dispdec_dpp_top_dispdec`. These expose DPP3 clock-enable/gating/test-clock fields, per-subblock soft reset for CNVC/DSCL/CM/OBUF, DPP CRC source/format/mask/stereo/interlace/one-shot controls, and host-read throttling.
- `DC_PERFMON14_*` for DPP3 perfmon. The fields describe performance-counter event selection, counted-value selection, increment and run-enable modes, counter restart/interrupt/off-mask/active status, counter state for eight counters, perfmon run state/report count, counter-off interrupt control/status/ack, run-enable start/stop sources, current-value high/low fragments, and read selectors.
- `MPCC0` through `MPCC3` base composition fields in address blocks `dce_dc_mpc_mpcc[0-3]_dispdec`. Each instance has top/bottom input selection, OPP routing, blend mode, alpha mode, premultiplied-alpha mode, active-overlap-only blend, background bits-per-component, bottom gain mode, global alpha/gain, stereo-mixer control/status, update-lock selection/status, top and bottom gains, movable color-management location, background RGB/YCbCr components, OGAM memory power control/state, and idle/busy/disabled status.
- MPC-wide fields in `dce_dc_mpc_mpc_cfg_dispdec`: `MPC_CLOCK_CONTROL`, `MPC_SOFT_RESET`, `MPC_CRC_CTRL`, `MPC_CRC_SEL_CONTROL`, `MPC_PERFMON_EVENT_CTRL`, bypass background color registers, host-read control, DPP and OPP/MPCC/DWB pending-status registers, four vertical-update lock-set register families, MPC CRC result channels, and `MPC_DWB0_MUX`.
- `DC_PERFMON15_*` for MPC perfmon, structurally matching the DPP perfmon fields but attached to the MPC block.
- `MPCC_OGAM0` and `MPCC_OGAM1` full output-gamma/gamut-remap groups, plus `MPCC_OGAM2` from control through RAMB region `26_27`. These include OGAM mode/select/current status, PWL disable, LUT index/data/control, RAM A and RAM B PWL start/end/base/slope/offset fields per RGB channel, packed region descriptors for region pairs 0-33, coefficient format, gamut-remap mode/current status, and A/B coefficient-bank pairs such as `C11_C12`, `C13_C14`, `C21_C22`, `C23_C24`, `C31_C32`, and `C33_C34`.

## Control flow and data flow

This header has no runtime control flow. Its data flow is compile-time expansion into ASIC-specific register tables and MMIO read/modify/write operations:

1. DCN 3.6 display code includes `dcn_3_6_0_offset.h` and this `dcn_3_6_0_sh_mask.h` file.
2. Resource, DMUB, IRQ, DPP, MPC, MPCC, color-management, CRC, and perfmon register-list macros select register offsets and the corresponding field shifts/masks for the DCN 3.6 ASIC.
3. Runtime paths pack desired field values by shifting them into the masked bit positions, then write the resulting 32-bit values through AMDGPU/DC register helpers.
4. Status and diagnostic paths read MMIO registers, mask and shift fields back to logical values, and use them for polling, debug output, CRC validation, performance monitoring, update synchronization, and display pipeline decisions.

For DPP3 and CM fields, the runtime programming is driven by color-management and DPP setup paths. Gamma-correction RAM region descriptors, coefficient formats, dealpha controls, and HDR multiplier values define how pixels are transformed before they leave DPP3. DPP CRC fields are used by validation and debug flows that select a source/format and then read per-channel CRC result registers.

For MPC/MPCC fields, plane composition code configures which DPP feeds each MPCC top/bottom input, which OPP receives the composed result, how alpha and global gain are applied, and when update locks allow register changes to take effect. MPC pending-status fields provide synchronization signals around DPP surface/config/cursor updates, OPP updates, MPCC updates, and DWB updates.

For MPCC OGAM and gamut-remap fields, color-management paths program the output transfer function through LUT index/data/control registers, RAM A/B region descriptors, and per-channel PWL boundary/slope/offset registers. Gamut-remap code programs matrix coefficients in A/B banks and selects the active mode/bank through the control fields.

## State and persistence

The macros themselves have no state. They describe hardware-resident state that persists until overwritten, reset, power-gated, or reinitialized by modeset/resume/firmware flows:

- DPP3 clock, gate-disable, test-clock, soft-reset, host-read, and CRC-control fields affect the operating state and diagnostics of DPP instance 3.
- CM3 gamma-correction and coefficient fields define color pipeline state. RAM region descriptors and LUT-related state can produce visible color shifts if programmed partially or with stale values.
- Memory power fields such as `GAMCOR_MEM_PWR_FORCE`, `GAMCOR_MEM_PWR_DIS`, `GAMCOR_MEM_PWR_STATE`, `MPCC_OGAM_MEM_PWR_FORCE`, `MPCC_OGAM_MEM_PWR_DIS`, `MPCC_OGAM_MEM_LOW_PWR_MODE`, and `MPCC_OGAM_MEM_PWR_STATE` reflect or control local RAM power behavior.
- MPCC selection, OPP ID, blend mode, alpha/gain, background color, stereo-mixer, and movable color-management location fields define active plane-composition state.
- Update-lock and pending-status fields are synchronization state. They gate or report when register writes are latched relative to vertical update windows and pipeline update sequencing.
- Perfmon control, state, current-value, interrupt status, and ack fields are diagnostic state. Counter values and interrupt bits change as hardware events occur.
- CRC result registers expose frame-dependent diagnostic data and are timing-sensitive when one-shot or continuous modes are toggled.

## Dependencies and integration points

- This header must be paired with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h`; the masks/shifts alone do not identify MMIO addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c`, and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c` include the DCN 3.6 offset and shift/mask headers for ASIC-specific resource, DMUB, and IRQ setup.
- DPP and color-management implementations rely on the `CM3_*` and `DPP_TOP3_*` fields for DPP instance 3 color transforms, memory power behavior, reset, clock control, and CRC diagnostics.
- MPC/MPCC implementations rely on `MPCC[0-3]_*`, `MPC_*`, and `MPCC_OGAM[0-2]_*` fields for plane blending, routing to OPPs, update locking, CRC capture, writeback muxing, output gamma, and gamut remap.
- Perfmon consumers rely on `DC_PERFMON14_*` and `DC_PERFMON15_*` for event selection, counter control, current-value reads, interrupt status/ack, and run-enable trigger selection.
- Generated spelling is an integration point. Register table macros assume exact register and field names; missing or renamed macros fail builds, while numeric drift can survive compilation and surface as display corruption, failed synchronization, invalid CRCs, or broken performance diagnostics.

## Risks and edge cases

- The requested range starts in the middle of the `CM3_CM_GAMCOR_RAMB_REGION_14_15` group and ends in the middle of the `MPCC_OGAM2_MPCC_OGAM_RAMB_REGION_26_27` group. Adjacent chunks are required before the final per-file report can treat those families as complete.
- Repeated instance blocks are copy/generator sensitive. `MPCC0` through `MPCC3`, `DC_PERFMON14` versus `DC_PERFMON15`, and `MPCC_OGAM0` through `MPCC_OGAM2` should remain structurally consistent except for intentional instance numbering and chunk boundaries.
- Packed PWL region fields are high risk: LUT offsets use 9-bit masks, segment counts sit at bits 12-14 and 28-30 in packed region-pair registers, start segment fields use high bits around bit 20, start/base/slope/offset fields use 18- or 19-bit masks, and end/slope pairs split 16-bit halves. A single shift or width error corrupts gamma/output transfer programming.
- Some registers mix control, status, pending, interrupt, and ack fields. Read/modify/write paths must avoid clearing status or acking interrupts unintentionally.
- Soft-reset and clock-gating fields can destabilize active display pipes if written outside the expected sequencing windows.
- CRC one-shot pending and update-lock/pending-status bits are timing-sensitive. Tests that only read idle-state registers may miss races during modeset, page flip, cursor update, writeback, or stereo/interlace changes.
- Perfmon interrupt status/ack and current-value high/low reads can race with counter updates unless read sequences follow the hardware programming model.
- Cross-generation similarity is risky. Nearby DCN 3.x and DCN 4.x headers have similarly named MPCC, MPC, DPP, CM, OGAM, and perfmon fields, but masks and field availability can differ; consumers must not mix offset/mask headers across ASIC versions.

## Test signals

- Build coverage with DCN 3.6 enabled should catch missing macro names when resource, DMUB, IRQ, DPP, MPC, MPCC, OGAM, and perfmon register tables instantiate these fields.
- Static generated-header checks should verify that every field has a matching shift and mask, masks have the expected width after shifting, repeated instance blocks are structurally aligned, and chunk-boundary registers reconcile with adjacent ranges.
- Cross-version diffing against AMD's authoritative register database and nearby generated headers should show intentional DCN 3.6 changes, especially for `DPP_FGCG_REP_DIS`, MPCC/OGAM memory power fields, perfmon fields, and packed PWL region layouts.
- Runtime DPP/color tests should exercise DPP3 gamma/output color changes, HDR multiplier and coefficient-format selection, dealpha behavior, gamma-correction memory power sequencing, reset/resume, and per-channel DPP CRC capture.
- Runtime MPC/MPCC tests should cover multi-plane composition, top/bottom source changes, OPP routing, alpha blending, global alpha/gain, background color, movable color-management location, update locks, pending-status polling, DWB0 mux selection, and MPC CRC one-shot/continuous modes.
- Runtime color-management tests should update MPCC OGAM LUTs and PWL region descriptors across MPCC OGAM instances 0-2, switch A/B gamut-remap coefficient banks, and verify visible output or CRC signatures across modeset and suspend/resume.
- Perfmon tests should configure DPP3 and MPC perfmon events, verify counter increments/current-value reads, exercise run-enable start/stop selection, and validate interrupt status/ack handling without disrupting display.

### subset-b-002126: lines 20053-22519

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 20053-22519

## Purpose

This chunk is a generated shift/mask register-field slice for AMD DCN 3.6 display hardware. It contains no executable functions or C data structures; its public surface is a dense set of preprocessor constants named as `<register>__<field>__SHIFT` and `<register>__<field>_MASK`. The constants are consumed with the matching DCN 3.6 offset header and the AMD Display Core register-helper macros so code can program MMIO fields without embedding bit positions directly.

The covered lines are entirely within the MPC/MPCC color-management area. The slice begins with the tail of `MPCC_OGAM2`, covers the full `dce_dc_mpc_mpcc_ogam3_dispdec` address block, covers the full `dce_dc_mpc_mpcc_mcm0_dispdec` address block, and then covers most of `dce_dc_mpc_mpcc_mcm1_dispdec` through the start of `MPCC_MCM1_MPCC_MCM_1DLUT_RAMB_REGION_30_31`. In display-pipeline terms, these fields describe MPCC output gamma (OGAM), gamut remap matrices, movable color management (MCM) shaper LUTs, MCM 3D LUTs, MCM 1D LUTs, indexed RAM A/B region tables, and MCM memory power controls.

## Important APIs and register groups

- `MPCC_OGAM2_*` at the beginning is a boundary continuation from the prior chunk. It finishes output-gamma RAMB region definitions for regions 26-33, then defines `MPCC_GAMUT_REMAP_COEF_FORMAT`, `MPCC_GAMUT_REMAP_MODE`, and the A/B gamut-remap coefficient registers `MPC_GAMUT_REMAP_C11_C12` through `C33_C34`.
- `MPCC_OGAM3_MPCC_OGAM_CONTROL` exposes output-gamma mode, LUT bank select, PWL disable, and readback/current-state fields. `MPCC_OGAM_LUT_INDEX`, `MPCC_OGAM_LUT_DATA`, and `MPCC_OGAM_LUT_CONTROL` define indexed host access to 18-bit OGAM LUT entries, write color masks, read color select, host select, and configuration mode.
- `MPCC_OGAM3_MPCC_OGAM_RAMA_*` and `MPCC_OGAM3_MPCC_OGAM_RAMB_*` define dual-bank piecewise-linear output-gamma tables. Each bank has B/G/R start controls, start slopes, start bases, end controls, offsets, and region descriptors for regions 0-33. Region registers pack two regions per register with 9-bit LUT offsets and 3-bit segment counts.
- `MPCC_OGAM3_MPCC_GAMUT_REMAP_*` and `MPCC_OGAM3_MPC_GAMUT_REMAP_*` define the gamut-remap coefficient format, mode/current bits, and two coefficient banks. The coefficient registers pack two 16-bit matrix elements per register, with A and B banks allowing banked or double-buffered matrix programming.
- `MPCC_MCM0_MPCC_MCM_SHAPER_*` defines MCM shaper enable/control, per-channel 19-bit offsets, scale fields, shaper LUT index/data, write-enable color masks, RAMA/RAMB start/end controls, and 34 region descriptors per bank. This is the pre-3D-LUT transfer-function surface in the movable color-management pipeline.
- `MPCC_MCM0_MPCC_MCM_3DLUT_*` defines 3D LUT mode, indexed access, normal and 30-bit data paths, read/write control, output normalization factor, and per-channel output offsets. The read/write control fields include color-channel select, address update, and read/write selectors for host-driven table loading.
- `MPCC_MCM0_MPCC_MCM_1DLUT_*` mirrors the output-gamma style 1D LUT programming surface: control mode/select/PWL-disable/current bits, LUT index/data/control, RAMA/RAMB start controls, slopes, bases, end controls, offsets, and region descriptor tables.
- `MPCC_MCM0_MPCC_MCM_MEM_PWR_CTRL` defines memory power controls and readback states for the shaper, 3DLUT, and 1DLUT memories: force, disable, low-power mode, and power-state fields.
- `MPCC_MCM1_*` repeats the same shaper, 3DLUT, and 1DLUT field layout for MCM instance 1. This chunk reaches `MPCC_MCM1_MPCC_MCM_1DLUT_RAMB_REGION_30_31__MPCC_MCM_1DLUT_RAMB_EXP_REGION30_LUT_OFFSET__SHIFT`; the remaining region 30/31 masks, region 32/33, and MCM1 memory power fields are expected in the following chunk.

## Control flow and usage model

There is no local control flow in this header. The constants are generated hardware metadata. A typical DCN 3.6 use path is:

1. Include `dcn_3_6_0_offset.h` and this `dcn_3_6_0_sh_mask.h` file.
2. Expand register lists and field lists with macros such as `SRII`, `SRI_ARR`, `SF`, `FD_MASK`, and `FD_SHIFT`.
3. Store offsets, masks, and shifts in block-specific register tables, for example MPC/MPCC tables built from the DCN32 resource-header macros and instantiated from `dcn36_resource.c`.
4. Let color-management and hardware-sequencing code call register helpers such as `REG_SET`, `REG_UPDATE`, `REG_SET_2`, and indexed LUT write routines to program the hardware fields.

The key integration pattern is name concatenation. Resource headers refer to generic names such as `MPCC_MCM_1DLUT_RAMB_REGION_28_29` with a block and instance (`MPCC_MCM`, `0` or `1`); the preprocessor expands that into symbols from this generated header, such as `regMPCC_MCM1_MPCC_MCM_1DLUT_RAMB_REGION_28_29` from the offset header and `MPCC_MCM1_MPCC_MCM_1DLUT_RAMB_REGION_28_29__..._MASK` from this mask header. This makes exact generated naming part of the ABI between the ASIC register database and the driver sources.

## State and persistence behavior

The header itself has no mutable state and persists only as compile-time constants. The state described by these constants lives in MPCC/MPC MMIO registers and indexed LUT RAMs. That state is hardware-visible across a modeset or color-management update until overwritten, reset, power-gated, or lost through display IP reset/suspend/resume.

The output-gamma and MCM 1D/shaper LUT blocks are banked with RAMA/RAMB tables. Software selects banks, programs indexes/data/control fields, loads per-channel values, writes region descriptors, and then selects the active mode/bank. `*_CURRENT` fields expose the hardware's active mode or bank readback, while `*_SELECT` fields are software-programmed selections. The region tables are persistent programmed curves: incorrect offsets or segment counts remain active and can affect later frames until corrected.

The 3D LUT state is also indexed and persistent. Host programming depends on `INDEX`, `DATA`, `DATA_30BIT`, and `READ_WRITE_CONTROL` coordination. The output normalization and per-channel output offsets are separate persistent scalar fields that shape the result after table lookup.

`MPCC_MCM*_MEM_PWR_CTRL` is power-management state for LUT memories. The force/disable/low-power-mode fields affect whether the shaper, 3DLUT, and 1DLUT memories are accessible and retained, while the state fields are readbacks. These controls must be sequenced with LUT programming and runtime power management, because a powered-down LUT memory can make later indexed writes ineffective or stale.

## Dependencies and integration points

- Requires `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h` for matching register addresses and base indices.
- Included by DCN 3.6 display code such as `display/dc/resource/dcn36/dcn36_resource.c`, `display/dc/irq/dcn36/irq_service_dcn36.c`, and `display/dmub/src/dmub_dcn36.c`.
- Integrated through `display/dc/resource/dcn32/dcn32_resource.h`, whose MPC register lists enumerate `MPCC_OGAM_*` and `MPCC_MCM_*` registers for instances using `SRII`. DCN 3.6 resource initialization includes the DCN 3.6 offset and mask headers before expanding those register-list macros.
- Consumed by the Display Core register-helper layer through generated field masks and shifts. The field constants are not type checked; compile-time symbol resolution is the main guard against mismatched names.
- Tied to higher-level DC color-management APIs and state objects that describe output gamma, gamut remap, shaper LUTs, 3D LUTs, 1D LUTs, and the movable color-management pipeline placement. User-visible effects surface through HDR, color-managed desktop, display calibration, and multi-plane composition paths.
- Related debug state appears in `dc.h`, including pipe debug capture fields for `MPCC_OGAM_CONTROL` mode/select/PWL-disable. Those debug surfaces depend on these exact field positions when dumping or interpreting hardware state.

## Risks and edge cases

- Generated-header drift is the largest structural risk. The offset and shift/mask headers must describe the same ASIC register database. A stale mask with a new offset, or the reverse, can compile while programming the wrong bits.
- Instance mismatch is easy because `MPCC_OGAM2`, `MPCC_OGAM3`, `MPCC_MCM0`, and `MPCC_MCM1` have near-identical field names. Programming the wrong MPCC or MCM instance can produce per-pipe color failures that look like plane, stream, or timing issues.
- Chunk-boundary truncation matters for documentation and automated analysis: this chunk starts mid-`MPCC_OGAM2` and ends mid-`MPCC_MCM1_MPCC_MCM_1DLUT_RAMB_REGION_30_31`. Final per-file analysis must reconcile adjacent chunks before claiming complete coverage for those register families.
- Packed-field writes can corrupt neighboring fields. Many registers pack two coefficients, two region descriptors, multiple mode/current bits, or multiple per-memory power controls into one 32-bit register. Full-register writes can clobber adjacent fields or readback/status bits.
- Width constraints are hardware-specific: common fields here include 1-bit selectors, 2-bit modes, 3-bit segment counts, 9-bit LUT offsets, 16-bit coefficients and slope/end fields, 18-bit LUT data/start/base fields, 19-bit offsets, and 30-bit 3DLUT data. Callers must clamp before shifting.
- Bank and current-state sequencing is subtle. `SELECT`, `MODE`, `PWL_DISABLE`, and `*_CURRENT` fields imply double-buffered hardware behavior. Switching banks before all RAMA/RAMB or coefficient values are loaded can produce visible frame-to-frame color artifacts.
- Indexed LUT programming is order-sensitive. Wrong host selection, color write mask, read color select, index auto-update, or data width can silently load only one channel, load the wrong index, or mix 18-bit and 30-bit data paths incorrectly.
- Memory power controls can invalidate color programming assumptions. Disabling or low-powering shaper/3DLUT/1DLUT memory while a pipeline expects it active can cause black, bypassed, or distorted color output depending on hardware behavior.
- Cross-version copy assumptions are risky. These fields resemble DCN 3.2 and DCN 3.5 layouts, but DCN 3.6 is its own generated header. Any shared driver macro must still be verified against the DCN 3.6 generated symbols and bit positions.

## Test signals

- Build DCN 3.6 display support and ensure `dcn36_resource.c`, the DCN 3.6 IRQ service, and DMUB DCN 3.6 code compile against the paired `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h` headers.
- Static checks can compare repeated `MPCC_OGAM3`, `MPCC_MCM0`, and `MPCC_MCM1` field layouts against neighboring instances and against the register-list expectations in `dcn32_resource.h`.
- Color-management functional tests should load and switch MPCC OGAM LUTs, gamut-remap matrices, MCM shaper LUTs, MCM 3D LUTs, and MCM 1D LUTs across SDR, HDR, and calibrated-color paths.
- Bank-switch tests should verify RAMA/RAMB programming, `SELECT`/`CURRENT` readback, PWL enable/disable behavior, and no visible corruption during commit or modeset transitions.
- Instance-coverage tests should exercise multiple pipes/MPCCs so `OGAM2`, `OGAM3`, `MCM0`, and `MCM1` register tables are not only compile-tested.
- Runtime register-dump diagnostics should inspect `MPCC_OGAM*_MPCC_OGAM_CONTROL`, `MPCC_OGAM*_MPCC_GAMUT_REMAP_MODE`, `MPCC_MCM*_MPCC_MCM_3DLUT_MODE`, `MPCC_MCM*_MPCC_MCM_1DLUT_CONTROL`, LUT index/control registers, and `MPCC_MCM*_MPCC_MCM_MEM_PWR_CTRL` when investigating color artifacts or LUT programming failures.
- Power-management tests should cover suspend/resume, display off/on, runtime power gating, and memory low-power transitions while MCM shaper/3DLUT/1DLUT state is enabled.
- Visual validation should include gradients, color ramps, HDR metadata/color-management paths, and multi-plane composition, because bad region offsets, segment counts, coefficient packing, or bank selection often appears as banding, clipped channels, or only one affected pipe.

### subset-b-002127: lines 22520-24994

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 22520-24994

## Purpose

This chunk is a generated shift/mask register-field slice for AMD DCN 3.6 display hardware. It contains preprocessor constants only; there are no C functions, structs, enums, storage objects, or local executable paths. Its exported interface is the standard generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` namespace used by AMDGPU Display Core register-table code.

The range starts at the tail of the `MPCC_MCM1` movable color-management block, covers the full `MPCC_MCM2` block, begins the `MPCC_MCM3` block, then moves into MPC output mux/denorm/output-CSC fields and the beginning of `ABM0` ambient/backlight management fields. Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMD display hardware metadata and has no Ceph, filesystem, distributed-storage, network, or persistent-disk behavior.

## Important APIs, Types, And Macros

The only API surface is generated macros:

- `*_SHIFT` gives a register field's least-significant bit position.
- `*_MASK` gives the field mask in already-shifted register position.
- Register names encode hardware block and instance, such as `MPCC_MCM2_MPCC_MCM_SHAPER_CONTROL`, `MPCC_MCM3_MPCC_MCM_1DLUT_RAMA_REGION_8_9`, `MPC_OUT0_CSC_C11_C12_A`, and `ABM0_DC_ABM1_HG_MISC_CTRL`.

The `MPCC_MCM1_*` tail completes `MPCC_MCM1_MPCC_MCM_1DLUT_RAMB_REGION_32_33` and `MPCC_MCM1_MPCC_MCM_MEM_PWR_CTRL`. The memory-power register exposes force, disable, low-power-mode, and state fields for shaper, 3DLUT, and 1DLUT memories. This is a chunk-boundary continuation from the previous range, so complete `MCM1` analysis must merge adjacent chunks.

`MPCC_MCM2_*` is the largest complete block in this chunk. It defines movable color-management field geometry for MPC/MPCC instance 2:

- Shaper controls: `SHAPER_CONTROL`, per-channel offset/scale registers, LUT index/data registers, write color mask, RAM A/B selection, start/end controls for red/green/blue, and RAM A/B piecewise region descriptors from `REGION_0_1` through `REGION_32_33`.
- 3D LUT controls: `3DLUT_MODE`, `3DLUT_INDEX`, `3DLUT_DATA`, `3DLUT_DATA_30BIT`, `3DLUT_READ_WRITE_CONTROL`, output normalization, and output offset/scale fields for red, green, and blue.
- 1D LUT controls: `1DLUT_CONTROL`, `1DLUT_LUT_INDEX`, `1DLUT_LUT_DATA`, `1DLUT_LUT_CONTROL`, RAM A/B start controls, start slope controls, start base controls, end controls, offsets, and piecewise region descriptors from `REGION_0_1` through `REGION_32_33`.
- `MPCC_MCM_MEM_PWR_CTRL`, which carries memory force/disable/low-power/state fields for the shaper, 3DLUT, and 1DLUT memories.

`MPCC_MCM3_*` begins the same register family for instance 3. This chunk covers shaper setup, shaper RAM A/B regions, 3DLUT controls, 1DLUT control/index/data/control, and part of the 1DLUT RAM A/B region definitions. It stops before the complete `MCM3` block, so later chunks must reconcile the continuation before making whole-instance claims.

The `MPC_OUT*` block covers output-side muxing, denormalization, and output CSC for four MPC outputs:

- `MPC_OUT0_MUX` through `MPC_OUT3_MUX` provide `MPC_OUT_MUX`, rate-control enable/disable, flow-control mode, and flow-control count fields.
- `MPC_OUT*_DENORM_CONTROL` and clamp registers provide denorm mode plus min/max clamps for R/Cr, G/Y, and B/Cb.
- `MPC_OUT_CSC_COEF_FORMAT` selects coefficient format for output CSC.
- `MPC_OUT0_CSC_MODE` through `MPC_OUT3_CSC_MODE` select output CSC mode/current status.
- `MPC_OUT*_CSC_Cij_Ckl_A/B` registers pack pairs of 16-bit output CSC coefficients for two banks, allowing output color-space matrix programming per MPC output.

The `ABM0_*` block begins ambient backlight management instance 0:

- `BL1_PWM_AMBIENT_LIGHT_LEVEL`, `USER_LEVEL`, `TARGET_ABM_LEVEL`, `CURRENT_ABM_LEVEL`, `FINAL_DUTY_CYCLE`, and `MINIMUM_DUTY_CYCLE` are 17-bit-style PWM/backlight level fields.
- `BL1_PWM_ABM_CNTL` controls ABM use, ambient-light use, automatic current-level update, automatic final-duty calculation, and auto-update step size.
- `BL1_PWM_BL_UPDATE_SAMPLE_RATE` programs frame-count sampling and includes an ABM register-lock bit.
- `BL1_PWM_GRP2_REG_LOCK` defines group lock, update-pending, frame-start update, display selection, readback-double-buffer enable, and ignore-master-lock fields.
- `DC_ABM1_CNTL`, `IPCSC_COEFF_SEL`, ACE slope/offset and threshold registers, missed-frame status/clear fields, HGLS read-progress fields, and `HG_MISC_CTRL` define the first part of ABM image-statistics and adaptive contrast/enhancement controls.

## Control Flow And Usage Model

There is no local control flow. Runtime behavior is created by consumers that include `dcn_3_6_0_offset.h` and this header, then paste generated names into register tables and field-access helpers.

A typical DCN 3.6 path is:

1. Resource, IRQ, DMUB, MPC, and ABM code includes the matching DCN 3.6 offset and shift/mask headers.
2. Register-list macros such as `SR`, `SRI`, `SRI_ARR`, `SF`, `ABM_SF`, `FD_MASK`, and `FD_SHIFT` expand logical block fields into generated `reg*`, `*_MASK`, and `*__SHIFT` constants.
3. Runtime helpers such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, `REG_WAIT`, and indexed register programming code use the masks and shifts to access MMIO fields without hardcoding bit positions.

Visible integration anchors in this tree include `display/dc/resource/dcn36/dcn36_resource.c`, which includes `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h`; `display/dmub/src/dmub_dcn36.c`, which initializes DCN 3.6 DMUB register offsets/masks/shifts; and `display/dc/irq/dcn36/irq_service_dcn36.c`, which builds the DCN 3.6 IRQ service metadata from the generated headers. Common MPC code under `display/dc/mpc/dcn32/` programs `MPCC_MCM_*` fields for shaper, 3DLUT, 1DLUT, and memory-power operations. Common ABM code uses `ABM_MASK_SH_LIST_DCN35` in the DCN 3.6 resource path, and those field-list macros reference the `ABM0_*` fields present in this chunk.

## State And Persistence Behavior

This header has no mutable state and persists nothing. The described state lives in display hardware registers and indexed LUT memories, with lifetime controlled by resource construction, modeset programming, plane/stream updates, color-management changes, backlight/ABM updates, runtime power transitions, suspend/resume, GPU reset, and display IP reset.

The `MPCC_MCM*` fields describe stateful color pipeline resources. Shaper LUTs, 3D LUT contents, 1D LUT contents, RAM A/B selection, current-mode readbacks, per-channel offsets/scales, and piecewise-linear region descriptors remain in hardware until overwritten or reset. Memory-power force/disable/low-power/state fields determine whether those LUT memories are available and whether status polling can complete.

The `MPC_OUT*` fields define output routing and color transforms. Mux selection controls which MPC tree output feeds each output path. Denorm clamp and output CSC registers affect live scanout color conversion and can persist across modeset boundaries if not reprogrammed by the owning display path.

The `ABM0_*` fields represent backlight and ambient-light processing state. PWM target/current/final/minimum levels, automatic update step size, register locks, frame-start update behavior, ACE thresholds, missed-frame flags, read-progress flags, and histogram/luma statistics are hardware-owned or software-programmed display state. Several ABM fields are status or clear-on-write style fields rather than ordinary persistent controls.

## Dependencies And Integration Points

- The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h`. Representative matching offsets include `regMPCC_MCM2_MPCC_MCM_SHAPER_CONTROL`, `regMPCC_MCM3_MPCC_MCM_SHAPER_CONTROL`, `regMPC_OUT0_MUX`, `regABM0_BL1_PWM_AMBIENT_LIGHT_LEVEL`, and `regABM0_DC_ABM1_HG_MISC_CTRL`.
- The generated macros depend on AMDGPU Display Core's register-helper infrastructure. Field names must match the logical field-list macros exactly; compile-time failures catch many spelling errors, but a stale or cross-generation mask with a valid name can still misprogram hardware if paired with the wrong offset.
- DCN 3.6 resource construction (`dcn36_resource.c`) binds this header to hardware blocks for the ASIC revision selected by `ASICREV_IS_DCN36`.
- DMUB integration (`dmub_dcn36.c`) uses this header with generated field lists to initialize firmware-visible register metadata.
- IRQ integration (`irq_service_dcn36.c`) uses the same generated offset and mask headers for display interrupt source metadata.
- MPC color management integrates through common DCN32-era MPC code and field lists. The fields in this chunk back runtime programming of MPCC MCM shaper LUTs, 3DLUTs, 1DLUTs, RAM bank selection, memory power, and output CSC/denorm.
- ABM/backlight integration flows through `dce_abm.h` field-list macros and resource-specific ABM mask/shift tables; DCN 3.6 uses the DCN35 ABM field-list subset for the fields present here.

## Risks And Edge Cases

- Generated-header drift is the main risk. `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h` must remain paired; a valid mask with a stale offset silently writes the wrong register field.
- Chunk-boundary incompleteness matters. This slice starts after most of `MPCC_MCM1` and ends before the rest of `ABM0` and `MPCC_MCM3`; final per-file analysis must merge adjacent chunks before making complete per-block claims.
- Instance mixups are easy. `MPCC_MCM1`, `MPCC_MCM2`, `MPCC_MCM3`, and `MPC_OUT0` through `MPC_OUT3` repeat near-identical fields. Using one instance's register offset with another instance's mask can create pipe-specific color or routing failures.
- Indexed LUT programming is sequencing-sensitive. Shaper, 3DLUT, and 1DLUT registers require correct host selection, bank selection, write-color masks, index resets, and data writes. Wrong masks can produce visible color artifacts only under HDR, color-managed, or multi-plane configurations.
- Packed field widths must be respected. This chunk includes 9-bit LUT offsets, 3-bit segment counts, 16-bit matrix coefficients, 17-bit PWM/backlight levels, 19-bit shaper offsets, and 24-bit LUT data. Unclamped inputs can truncate into neighboring fields or be silently masked.
- Status and control fields are adjacent. Fields named `*_CURRENT`, `*_STATE`, `*_UPDATE_PENDING`, `*_READ_PROGRESS`, `*_MISSED_FRAME`, and `*_CLEAR` should not be treated as ordinary writable configuration.
- Memory-power hazards can cause hangs or stale programming. Forcing MCM memories off while programming or reading LUTs can make register waits fail, leave color tables incomplete, or increase power if force-on is left set.
- ABM lock/update fields are frame-synchronized. Misusing `HGLS_REG_LOCK`, group locks, frame-start update selection, or ignore-master-lock fields can miss updates, expose stale readback, or cause one-frame backlight/contrast glitches.
- Output CSC and denorm mistakes are visually subtle. Matrix coefficient bank selection, coefficient format, clamp limits, and mux selection can yield color shifts, clipping, or only-output-specific failures while the rest of the pipe appears healthy.

## Test Signals

- Build with DCN 3.6 enabled and ensure `dcn36_resource.c`, `dmub_dcn36.c`, `irq_service_dcn36.c`, MPC, and ABM consumers compile against matching `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h`.
- Static consistency checks should compare repeated `MPCC_MCM2`/`MPCC_MCM3` and `MPC_OUT0`-`MPC_OUT3` shift/mask layouts where hardware instances are expected to match, and should verify representative masks align with their offsets.
- Color-management tests should load shaper, 3DLUT, and 1DLUT tables on MPCC instances 2 and 3, switch RAM A/B banks, check current-mode readbacks, and validate SDR/HDR/color-managed output for visible artifacts.
- MPC output tests should exercise all four outputs, mux selection, denorm clamp programming, output CSC enable/mode selection, coefficient bank programming, and color-space conversion scenarios.
- Power-management tests should cover MCM memory power force/disable/low-power/state behavior across modeset, runtime idle, suspend/resume, and GPU reset.
- ABM/backlight tests should cover PWM user/target/current/final/minimum levels, automatic ABM update, ambient-light input, register lock/update-at-frame-start behavior, missed-frame clear fields, and HGLS read-progress reporting.
- Runtime diagnostics should inspect register dumps around `MPCC_MCM*_MEM_PWR_CTRL`, `MPCC_MCM*_SHAPER_CONTROL`, `MPCC_MCM*_3DLUT_MODE`, `MPCC_MCM*_1DLUT_CONTROL`, `MPC_OUT*_CSC_MODE`, and `ABM0_DC_ABM1_HG_MISC_CTRL` when debugging color artifacts, stuck LUT programming, output-routing problems, or ABM/backlight regressions.

### subset-b-002128: lines 24995-27614

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 24995-27614

## Purpose

This chunk is a generated shift/mask register-field slice for AMD DCN 3.6 display hardware. It contains no executable functions, structs, or persistent C objects; its API surface is a dense set of `#define` constants named as `<register>__<field>__SHIFT` and `<register>__<field>_MASK`. These constants are paired with `dcn_3_6_0_offset.h` register offsets and consumed through AMDGPU Display Core register-table macros such as `SF`, `SRI`, `FD_MASK`, `FD_SHIFT`, `REG_SET`, and `REG_UPDATE`.

The covered lines start in the middle of the ABM0 adaptive-backlight histogram/luma block, then define complete ABM1, ABM2, and ABM3 backlight/ambient/luma/histogram groups, OPP pipe 0-3 display-pattern-generator, formatter, buffer, pipe-control, and pipe-CRC groups, DSCRM DSC-forwarding controls, OPP top clock controls, DC perfmon instance 16 fields, ODM0-ODM3 OPTC input controls, and the beginning of OTG0 timing/trigger fields.

## Important APIs and register groups

- `ABM0_DC_ABM1_*` in this chunk continues ABM0 with histogram/luma scanout readback fields: luma sums, min/max and filtered min/max luma, pixel counts, min/max pixel-value thresholds, histogram sample rates, bin shift flags/indexes, 24 histogram result registers, and `BL_MASTER_LOCK`.
- `ABM1_*`, `ABM2_*`, and `ABM3_*` repeat the full adaptive backlight block for additional instances. Each instance includes PWM input/output levels (`BL1_PWM_AMBIENT_LIGHT_LEVEL`, `USER_LEVEL`, `TARGET_ABM_LEVEL`, `CURRENT_ABM_LEVEL`, `FINAL_DUTY_CYCLE`, `MINIMUM_DUTY_CYCLE`), ABM enable/auto-update controls, backlight update sampling, group-2 locking/update-pending fields, ABM core enable, IPCSC coefficient selection, ACE offset/slope and threshold tables, HGLS read progress/missed-frame status, histogram controls, luma statistics, sample-rate counters, histogram bin programming, histogram result readbacks, and master locks.
- `DPG0_*` through `DPG3_*` define output-pixel-processor display pattern generator fields for generated test patterns, including enable/mode, dynamic range, bit depth, vertical/horizontal resolution selectors, ramp offsets/increments, active dimensions, solid color channels, segment offsets, double-buffer-pending status, and DPG-side CRC result readbacks.
- `FMT0_*` through `FMT3_*` define formatter controls for output clamping, dynamic expansion, dithering, spatial/temporal dither controls, truncation, frame-random and RGB random seeds, 420 phase lock/source/pixel encoding/subsampling controls, clamp component enable/select, side-by-side stereo selection, 420 memory selection/status, and 422 left-edge extra-pixel count.
- `OPPBUF0_*` through `OPPBUF3_*` expose OPP buffer segmentation, overlap pixel count, 3D structure configuration, 3D address flags, stereo line packing, and dynamic expansion memory power controls.
- `OPP_PIPE0_OPP_PIPE_CONTROL` through `OPP_PIPE3_OPP_PIPE_CONTROL` expose the OPP pipe enable bit and clock-on status bit.
- `OPP_PIPE_CRC0_*` through `OPP_PIPE_CRC3_*` define output-pipe CRC controls and masks: enable/continuous/one-shot, stereo/interlace modes, pixel/source select, pending status, and 16-bit CRC masks.
- `DSCRM0_DSCRM_DSC_FORWARD_CONFIG` through `DSCRM3_*` select per-instance DSC forwarding via `DSCRM_DSC_FORWARD_EN` and `DSCRM_DSC_OPP_PIPE_SOURCE`.
- `OPP_TOP_CLK_CONTROL` contains top-level OPP clock gating/enable/status fields for OPP and OPPFIFO.
- `DC_PERFMON16_*` defines display performance monitor counter setup, counter selection, counter state, perfmon enable/continuous/start/reset, mode/status, interrupt thresholds and clear/mask bits, and low/high counter readbacks.
- `ODM0_OPTC_*` through `ODM3_OPTC_*` define OPTC/ODM input global controls, segment data-source selection, DSC data format and bytes-per-pixel fields, segment and slice width fields, input clock gate/enable/on bits, memory selection/status, spare register, and underflow threshold fields.
- `OTG0_OTG_*` begins the timing-generator instance 0 block: horizontal total/blank/sync and polarity, horizontal timing divider mode, vertical total/min/max/mid and dynamic refresh controls, vertical count stop controls, vtotal event interrupt status/ack/mask, nominal-vsync interrupt clear, vertical blank/sync and mode, and the first `TRIGA` trigger control fields at the chunk boundary.

## Control flow and usage model

There is no local control flow in this header. The generated constants are declarative data for higher-level register tables.

A typical consumer flow is:

1. Include `dcn_3_6_0_offset.h` and this header for DCN 3.6 offsets and field encodings.
2. Populate per-block `regs`, `shift`, and `mask` tables in DCN36 resource initialization using macros such as `ABM_MASK_SH_LIST_DCN35`, `OPP_MASK_SH_LIST_DCN35`, and `OPTC_COMMON_MASK_SH_LIST_DCN3_6`.
3. Let block implementations call typed register helpers, which combine the stored offset with the field mask and shift when programming MMIO.

The DCN36 resource path in `display/dc/resource/dcn36/dcn36_resource.c` constructs ABM, OPP, and OPTC mask/shift tables from this header. `display/dmub/src/dmub_dcn36.c` also includes the same header and uses `FD_MASK`/`FD_SHIFT` to initialize DMCUB-visible DCN35-style register metadata for DCN36. The IRQ service for DCN36 includes this header for interrupt field definitions. Shared block code under `display/dc/dce`, `display/dc/opp`, and `display/dc/optc` consumes the register tables rather than hardcoding these bit positions.

## State and persistence behavior

The header itself has no mutable state and persists only as compile-time constants. The mutable state is in display-engine MMIO registers and follows hardware lifecycle rules: display bring-up, modesets, ABM policy changes, panel brightness updates, test-pattern programming, color/output-format programming, ODM combine transitions, dynamic refresh changes, interrupt handling, suspend/resume, and GPU/display-IP reset.

Stateful hardware surfaces in this chunk include:

- ABM PWM levels and ABM enable/auto-update bits, which determine how ambient light, user brightness, target ABM brightness, and final duty cycle are combined.
- ABM HGLS read-progress, sample-rate, histogram bin, luma-statistic, and missed-frame clear fields, which represent live frame-scanning and histogram/luma collection state.
- OPP DPG fields, which can replace normal pixel output with test patterns and are double-buffered through pending status.
- FMT clamp, dither, truncation, pixel encoding, 420/422, and stereo controls, which affect visible output formatting and must match stream timing and sink format.
- OPPBUF segmentation/overlap and 3D parameters, which are part of multi-segment/ODM and stereo/3D output plumbing.
- OPP pipe CRC controls and masks, which maintain live CRC capture state and one-shot/continuous pending bits for validation and diagnostics.
- OPTC/ODM data source, segment count, DSC bytes-per-pixel, slice width, input clock, memory selection, and underflow status fields, which must track ODM combine mode and output timing.
- OTG0 timing and vtotal fields, which define scanout timing and dynamic refresh behavior; wrong values persist until reprogrammed or reset and can immediately destabilize display output.

## Dependencies and integration points

- Requires the matching `dcn_3_6_0_offset.h` register addresses. A shift/mask define is only meaningful when the same-generation offset define selects the correct MMIO register.
- Depends on AMDGPU/DC register macro infrastructure (`SF`, `SRI`, `FD_MASK`, `FD_SHIFT`, `REG_SET*`, `REG_UPDATE*`) to create typed shift/mask tables and perform read-modify-write operations.
- Integrates with `dce_abm` and `dmub_abm_lcd` for adaptive backlight and luma/histogram programming.
- Integrates with DCN36 resource construction through `dcn36_resource.c`, where ABM, OPP, and OPTC register tables are initialized for four hardware instances.
- Integrates with OPP code (`dcn20_opp` and later OPP variants) for display pattern generation, blanking/test pattern setup, formatter controls, OPP buffer programming, and OPP CRC diagnostics.
- Integrates with OPTC/timing-generator code (`dcn32_optc`-style helpers used by DCN36) for OTG timing, ODM segment routing, DSC slice geometry, input clock control, underflow handling, and dynamic refresh/vtotal programming.
- Integrates with DC performance monitoring/debug paths through the `DC_PERFMON16_*` fields and with display validation paths that read pipe CRCs or underflow status.

## Risks and edge cases

- Generated-pair drift is the main correctness risk: masks from this file must match offsets from `dcn_3_6_0_offset.h`. Mixing generations can compile while writing the wrong hardware field.
- Instance confusion is easy because ABM1-3, DPG/FMT/OPPBUF/OPP_PIPE/CRC0-3, DSCRM0-3, and ODM0-3 are highly repetitive. A wrong instance index can produce pipe-specific brightness, format, CRC, underflow, or timing failures.
- Many fields are adjacent packed bitfields. Whole-register writes can clobber status, clear, reserved, or pending bits; consumers should use field-aware read-modify-write helpers unless hardware requires a direct write.
- Status/control naming is mixed in the same register families. Fields such as `*_STATUS`, `*_CURRENT`, `*_PENDING`, `*_INT_STATUS`, and `*_ACK` are not ordinary configuration fields and may clear or latch hardware state when written.
- ABM programming has ordering hazards around HGLS register locks, group update-at-frame-start controls, master locks, sample-rate reset bits, and missed-frame clear bits. Reprogramming during active scanout can create stale statistics or visible brightness jumps.
- Formatter and OPP buffer fields can create visible artifacts if pixel encoding, 420/422, truncation, dithering, segment width, or overlap fields do not match stream timing and link encoding.
- Pipe CRC one-shot/continuous controls and masks must be synchronized with frame boundaries; otherwise diagnostics may capture stale frames or partial updates.
- ODM and OTG fields are timing-critical. Segment count/source, DSC slice width, bytes-per-pixel, memory selection, vtotal min/max/mid, and trigger fields can break scanout, underflow, or dynamic refresh if programmed outside the timing-generator update sequence.
- This chunk begins mid-register group for ABM0 and ends mid-register group at `OTG0_OTG_TRIGA_CNTL`; final per-file reconciliation must include adjacent chunks before drawing complete conclusions about those two groups.

## Test signals

- Build with DCN36 enabled and verify `dcn36_resource.c`, `dmub_dcn36.c`, and `irq_service_dcn36.c` compile against this header and the matching offset header.
- Static consistency checks should compare repeated ABM, OPP, DSCRM, and ODM instances for expected identical field layout, while allowing instance-specific register offsets.
- ABM tests should cover panel brightness changes, ambient/user/target/current/final duty-cycle programming, histogram/luma readback, sample-rate reset behavior, missed-frame clear behavior, and suspend/resume brightness restoration.
- OPP formatter tests should exercise RGB/YCbCr, 420/422 modes, dithering/truncation, clamp controls, stereo/3D modes, and output-depth transitions.
- Display pattern generator tests should program solid color and ramp patterns on pipes 0-3, check double-buffer pending behavior, and validate blanking/test-pattern output.
- CRC diagnostics should run one-shot and continuous OPP pipe CRC capture on each pipe and confirm mask/source/stereo/interlace settings produce stable expected results.
- ODM/OPTC tests should cover bypass, 2:1/4:1 ODM combine where supported, DSC slice-width/bytes-per-pixel programming, input-clock enable/gating, memory selection, and underflow status/clear behavior.
- OTG timing tests should cover modeset timing, dynamic refresh/vtotal min/max/mid transitions, vtotal interrupt status/ack/mask, vsync-nominal interrupt clear, and trigger source/polarity/delay programming.

### subset-b-002129: lines 27615-30081

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 27615-30081

## Purpose

This chunk is a generated AMD DCN 3.6 register shift/mask slice for the OPTC/OTG display timing-generator blocks. It contains no executable functions, structs, or inline logic. Its API surface is a large set of C preprocessor constants named as `<register>__<field>__SHIFT` and `<register>__<field>_MASK`; AMDGPU DC code combines these constants with the matching `dcn_3_6_0_offset.h` register addresses and register helper macros to program MMIO fields without hardcoding bit positions.

The assigned range starts inside `OTG0_OTG_TRIGA_CNTL`, then covers the remaining OTG0 field definitions, the full `dce_dc_optc_otg1_dispdec` address block, and almost all of `dce_dc_optc_otg2_dispdec` through `OTG2_OTG_PIPE_UPDATE_STATUS`. `OTG2_OTG_SPARE_REGISTER` and the next `OTG3` block begin immediately after this chunk. The range contains 2,135 `#define` lines, including 1,067 `__SHIFT` constants, 1,091 `_MASK` constants, and 328 comment/address-block markers.

## Important APIs and Register Groups

- Trigger and manual trigger fields: `OTG*_OTG_TRIGA_CNTL`, `OTG*_OTG_TRIGB_CNTL`, `OTG*_OTG_TRIGA_MANUAL_TRIG`, `OTG*_OTG_TRIGB_MANUAL_TRIG`, and `OTG*_OTG_TRIG_MANUAL_CONTROL` define source selection, source pipe selection, polarity, resync bypass, input/polarity status, occurred/clear bits, edge detection, frequency select, delay, and software manual trigger bits.
- Core timing and output control: `OTG*_OTG_CONTROL`, `OTG*_OTG_MASTER_EN`, `OTG*_OTG_DLPC_CONTROL`, `OTG*_OTG_COUNT_CONTROL`, `OTG*_OTG_COUNT_RESET`, `OTG*_OTG_STATUS`, `OTG*_OTG_STATUS_POSITION`, `OTG*_OTG_STATUS_FRAME_COUNT`, `OTG*_OTG_STATUS_VF_COUNT`, `OTG*_OTG_STATUS_HV_COUNT`, `OTG*_OTG_LONG_VBLANK_STATUS`, and `OTG*_OTG_NOM_VERT_POSITION` expose master enable state, disable/start points, output muxing, resync/snapshot location, horizontal/vertical active/blank/sync status, current counters, frame counters, repeated horizontal counting, and count reset.
- Vertical sync, interlace, stereo, and 3D fields: `OTG*_OTG_INTERLACE_CONTROL`, `OTG*_OTG_INTERLACE_STATUS`, `OTG*_OTG_MANUAL_FORCE_VSYNC_NEXT_LINE`, `OTG*_OTG_VERT_SYNC_CONTROL`, `OTG*_OTG_STEREO_FORCE_NEXT_EYE`, `OTG*_OTG_STEREO_STATUS`, `OTG*_OTG_STEREO_CONTROL`, and `OTG*_OTG_3D_STRUCTURE_CONTROL` describe interlace enable/field state, forced-vsync events, stereo eye selection/status, stereo sync output line/polarity, DP-specific stereo output disables, and 3D structure enable/update points.
- Snapshot and interrupt fields: `OTG*_OTG_SNAPSHOT_STATUS`, `OTG*_OTG_SNAPSHOT_CONTROL`, `OTG*_OTG_SNAPSHOT_POSITION`, `OTG*_OTG_SNAPSHOT_FRAME`, `OTG*_OTG_INTERRUPT_CONTROL`, `OTG*_OTG_VERTICAL_INTERRUPT0/1/2_POSITION`, `OTG*_OTG_VERTICAL_INTERRUPT0/1/2_CONTROL`, and `OTG*_OTG_GLOBAL_SYNC_STATUS` define snapshot trigger/clear/readback fields plus interrupt enable/type/status/clear fields for snapshot, force-count-now, forced-vsync, trigger A/B, nominal vsync, GSL gap, vertical interrupt lines, vstartup, vupdate, vupdate-no-lock, and vready.
- Double-buffer and update-lock fields: `OTG*_OTG_UPDATE_LOCK`, `OTG*_OTG_DOUBLE_BUFFER_CONTROL`, `OTG*_OTG_MASTER_UPDATE_MODE`, `OTG*_OTG_MASTER_UPDATE_LOCK`, `OTG*_OTG_VUPDATE_KEEPOUT`, `OTG*_OTG_GLOBAL_CONTROL0` through `OTG*_OTG_GLOBAL_CONTROL4`, and `OTG*_OTG_PIPE_UPDATE_STATUS` define update pending state, DRR/timing/3D/vstartup/DSC double-buffer pending bits, instant update mode, master update lock status, VUPDATE keepout windows, global update-lock enable/select, DIG update position/field/eye selection, and flip/DC-register/cursor pending status.
- CRC and pixel readback fields: `OTG*_OTG_PIXEL_DATA_READBACK0/1`, `OTG*_OTG_CRC_CNTL`, `OTG*_OTG_CRC0/1_WINDOW{A,B}_{X,Y}_CONTROL`, `OTG*_OTG_CRC{0,1,2,3}_DATA_{RG,B}`, `OTG*_OTG_CRC_SIG_RED_GREEN_MASK`, `OTG*_OTG_CRC_SIG_BLUE_CONTROL_MASK`, and the CRC window readback registers expose CRC source selection, continuous/enable state, window selection coordinates, CRC signature masks, data readback values, and window coordinate readbacks.
- Global-swap-lock and synchronization fields: `OTG*_OTG_GSL_VSYNC_GAP`, `OTG*_OTG_GSL_CONTROL`, `OTG*_OTG_GSL_WINDOW_X`, and `OTG*_OTG_GSL_WINDOW_Y` define allowed vsync-gap windows, GSL channel enables, master enable/mode, check/force delays, all-fields behavior, master-update-lock GSL coupling, and X/Y windows used for coordinated multi-pipe updates.
- Dynamic refresh and DSC/request fields: `OTG*_OTG_DRR_TIMING_INT_STATUS`, `OTG*_OTG_DRR_V_TOTAL_REACH_RANGE`, `OTG*_OTG_DRR_V_TOTAL_CHANGE`, `OTG*_OTG_DRR_TRIGGER_WINDOW`, `OTG*_OTG_DRR_CONTROL`, `OTG*_OTG_DRR_CONTOL2`, `OTG*_OTG_M_CONST_DTO0/1`, `OTG*_OTG_REQUEST_CONTROL`, and `OTG*_OTG_DSC_START_POSITION` define DRR timing-update and v-total-reach event/interrupt bits, DRR ranges and trigger windows, average-frame and last-vtotal readbacks, DTO phase/modulo values, duplicate horizontal request mode, and DSC start position.
- Static screen and clock fields: `OTG*_OTG_STATIC_SCREEN_CONTROL` and `OTG*_OTG_CLOCK_CONTROL` provide event-mask controls for static-screen detection and clock enable/gating status fields for the timing generator instance.

## Control Flow and Usage Model

There is no local control flow in this header. The constants become data for higher-level register tables:

1. DCN 3.6 code includes `dcn_3_6_0_offset.h` for register addresses and this header for bit encodings.
2. Resource setup expands register-list macros such as `OPTC_COMMON_REG_LIST_DCN3_5_RI(id)` and field-list macros such as `OPTC_COMMON_MASK_SH_LIST_DCN3_6(__SHIFT)` / `OPTC_COMMON_MASK_SH_LIST_DCN3_6(_MASK)` into `struct dcn_optc_registers`, `struct dcn_optc_shift`, and `struct dcn_optc_mask` instances.
3. Timing-generator and IRQ code then calls shared register helpers (`REG_SET`, `REG_UPDATE`, `REG_GET`, `FD_MASK`, `FD_SHIFT`, and related macros) through those tables.
4. Hardware side effects happen only when consumers read or write the corresponding MMIO registers; this generated header itself only supplies compile-time numeric constants.

`dcn36_resource.c` is the main DCN 3.6 construction point for these OPTC fields. It includes this header, initializes four `optc_regs` instances, and populates `optc_shift`/`optc_mask` from DCN 3.6 OPTC field-list macros. `irq_service_dcn36.c` includes the same header and uses per-instance OTG names in `IRQ_REG_ENTRY` expansions; for example vblank and vupdate-no-lock entries use `OTGx_OTG_GLOBAL_SYNC_STATUS` masks such as `VSTARTUP_INT_EN` and `VUPDATE_NO_LOCK_EVENT_CLEAR`. `dmub_dcn36.c` also includes the generated header to initialize DMUB register masks/shifts, though most fields in this specific chunk are consumed by DC timing-generator and IRQ paths rather than DMCUB internals.

## State and Persistence Behavior

The header has no mutable software state. The state described by the fields lives in DCN display MMIO registers and hardware latches. These values persist until changed by modeset programming, runtime display updates, suspend/resume restore, GPU/display IP reset, or firmware/driver reinitialization.

Several covered groups represent stateful or edge-triggered hardware behavior:

- Master enable, timing counters, blank/active/sync status, frame counters, and current master-enable state reflect live timing-generator state. They are tied to scanout timing and can change every line or frame.
- Trigger, force-count-now, forced-vsync, snapshot, vertical-interrupt, global-sync, and DRR interrupt fields include event-occurred and clear bits. Software must preserve the expected acknowledge semantics when writing these registers.
- Double-buffer pending, update lock, master update lock, VUPDATE keepout, and pipe update status fields coordinate when timing and plane/cursor updates become visible. Persistence across a modeset matters because stale locks or pending bits can block later updates.
- CRC windows, CRC masks, CRC data, and pixel readback fields are diagnostic state. Some fields are programmed controls, while data/readback fields are snapshots of hardware output.
- GSL and global control fields coordinate multi-pipe synchronization. Incorrect persistence can affect only synchronized displays, stereo/interlace modes, or multi-stream timing transitions.
- DRR and DTO fields encode variable-refresh behavior and timing adjustment state. The `*_LAST_USED_BY_DRR` fields are hardware readbacks rather than normal software-owned configuration.

## Dependencies and Integration Points

- The constants must stay paired with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h`; masks/shifts alone are not enough to address hardware.
- The generated names are consumed by AMD display register helper infrastructure in `reg_helper.h` and by macro families such as `SR`, `SRI_ARR`, `SF`, `FD_MASK`, and `FD_SHIFT`.
- DCN 3.6 resource construction in `display/dc/resource/dcn36/dcn36_resource.c` maps these fields into OPTC timing-generator objects. That resource file reuses the DCN 3.5 OPTC register list and adds the DCN 3.6 mask/shift list for CRC polynomial and 32-bit CRC data fields.
- Shared OPTC headers under `display/dc/optc/`, especially `dcn35_optc.h` and `dcn10_optc.h`, define the field-list structures that receive values from this generated header.
- DCN 3.6 IRQ setup in `display/dc/irq/dcn36/irq_service_dcn36.c` depends on `OTG*_OTG_GLOBAL_SYNC_STATUS` and vertical interrupt control/position field masks to map hardware source IDs to DAL interrupt sources.
- Display validation and debugging integrate with these fields through CRC capture, vblank/vline/vupdate IRQs, dynamic refresh-rate programming, update-lock sequencing, GSL synchronization, and per-pipe pending-status queries.

## Risks and Edge Cases

- Generated-header drift is the main risk. If `dcn_3_6_0_sh_mask.h` and `dcn_3_6_0_offset.h` are regenerated or copied out of sync, valid-looking masks may be applied to wrong MMIO addresses.
- The chunk boundary starts after the first two `OTG0_OTG_TRIGA_CNTL` fields. A final merged per-file report should reconcile this with the previous chunk before describing the full TRIGA layout.
- The range ends just before `OTG2_OTG_SPARE_REGISTER` and the `OTG3` address block. Any whole-file analysis must include the next block to cover all timing-generator instances.
- Many registers mix control, status, event, and clear bits. Full-register writes can accidentally clear interrupts, acknowledge events, alter lock state, or overwrite hardware-owned readback fields.
- Repeated OTG0/OTG1/OTG2 layouts are similar but instance-specific. Using OTG0 masks with an OTG1/OTG2 offset, or vice versa, can compile but program the wrong timing generator if table macros are expanded incorrectly.
- Field widths vary sharply: 1-bit enable/status fields sit next to 2-bit mode fields, 5-bit delay fields, 10/11/15-bit coordinate and line fields, 16-bit offsets, 24-bit frame counts, 31-bit/32-bit counters, and full 32-bit DTO values. Callers need input clamping before shifting values into masks.
- Update-lock, VUPDATE keepout, DRR, and GSL fields are timing-sensitive. Incorrect sequencing can produce missed flips, cursor/plane update stalls, vupdate-no-lock interrupts, scanout glitches, or multi-display desynchronization.
- CRC and pixel readback fields are often used for validation. Misprogrammed windows or masks can produce false failures in automated display tests even when scanout is visually correct.
- The generated typo `OTG_DRR_CONTOL2` appears consistently in the register names and must not be “fixed” locally unless the generated offset and all consumers are changed together.

## Test Signals

- Build DCN 3.6 display code and ensure `dcn36_resource.c`, `irq_service_dcn36.c`, and `dmub_dcn36.c` compile against the same generated offset and mask headers.
- Static consistency checks should verify that `OTG0`, `OTG1`, and `OTG2` repeated field layouts are bit-identical where the hardware block is repeated, and that DCN 3.6-specific OPTC fields in `OPTC_COMMON_MASK_SH_LIST_DCN3_6` resolve to generated constants.
- IRQ tests should exercise vblank, vline0, vupdate-no-lock, trigger, force-vsync, and DRR event paths, validating enable masks, clear masks, and source-to-DAL mapping.
- Modeset and page-flip tests should inspect `OTG*_OTG_DOUBLE_BUFFER_CONTROL`, `OTG*_OTG_MASTER_UPDATE_LOCK`, `OTG*_OTG_VUPDATE_KEEPOUT`, and `OTG*_OTG_PIPE_UPDATE_STATUS` for stuck pending bits or stale update locks.
- Variable-refresh tests should cover DRR v-total range, v-total reach interrupts, trigger windows, average-frame modes, and the `OTG_V_TOTAL_LAST_USED_BY_DRR` / `OTG_VCOUNT2_LAST_USED_BY_DRR` readbacks.
- Multi-display synchronization tests should exercise GSL windows, global update lock, stereo/interlace field selection, and master update lock behavior across more than one OTG instance.
- CRC validation should program CRC0/CRC1 windows, masks, continuous enable, polynomial select, and 32-bit CRC data readbacks where supported, then compare expected output signatures across SDR/HDR and DSC/non-DSC timing paths.
- Suspend/resume, GPU reset, and display hotplug tests should verify that master enable, interrupt enables, update locks, GSL, DRR, and CRC diagnostic state are either restored intentionally or reset to safe defaults.

### subset-b-002130: lines 30082-32579

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 30082-32579

## Purpose

This chunk is a generated AMD DCN 3.6.0 register field shift/mask slice. It contains no executable functions or C types; its API is preprocessor constants named as `<register>__<field>__SHIFT` and `<register>__<field>_MASK`. Display Core and DMUB code combine these constants with the matching `dcn_3_6_0_offset.h` register offsets and register helper macros to read, update, and write MMIO fields without hardcoding bit locations.

The range starts at the tail of the OTG2 block (`OTG2_OTG_PIPE_UPDATE_STATUS` and `OTG2_OTG_SPARE_REGISTER`), then covers the full `dce_dc_optc_otg3_dispdec` timing-generator block, OTG CRC32 readout blocks `OTG_CRC320` through `OTG_CRC323`, OPTC miscellaneous/global-source-lock/memory-power fields, DC perfmon counter 17, HPD0 through HPD4 hotplug detect fields, DisplayPort transmitter instance DP0, and the beginning of DIG0 frontend control.

## Important APIs and register groups

- `OTG3_OTG_H_*`, `OTG3_OTG_V_*`, and sync-control fields define horizontal/vertical totals, blanking, sync positions, sync polarity, timing division, dynamic refresh min/max/mid totals, v-total event interrupts, nominal vsync interrupt clearing, and count-stop controls for timing generator instance 3.
- `OTG3_OTG_TRIGA_CNTL`, `OTG3_OTG_TRIGB_CNTL`, manual trigger registers, and `OTG3_OTG_FORCE_COUNT_NOW_CNTL` expose trigger source selection, pipe selection, polarity, resync bypass, edge-detect mode, frequency, delay, occurred/status, clear, and force-count sequencing.
- `OTG3_OTG_CONTROL`, `OTG3_OTG_CLOCK_CONTROL`, `OTG3_OTG_MASTER_EN`, and interlace/stereo/3D fields control OTG enablement, disable/start points, output muxing, field-number behavior, clock enable/gating/reset/busy status, stereo eye selection, and 3D frame count behavior.
- `OTG3_OTG_STATUS*`, `OTG3_OTG_STATUS_POSITION`, `OTG3_OTG_STATUS_HV_COUNT`, `OTG3_OTG_STATUS_FRAME_COUNT`, `OTG3_OTG_STATUS_VF_COUNT`, snapshot registers, pixel readback registers, long-vblank/static-screen status, and manual vsync force fields provide live timing state and diagnostics.
- `OTG3_OTG_INTERRUPT_CONTROL`, `OTG3_OTG_VERTICAL_INTERRUPT0/1/2_*`, `OTG3_OTG_V_TOTAL_INT_STATUS`, and `OTG3_OTG_GLOBAL_SYNC_STATUS` define enable/type/status/clear/ack masks for vsync, vupdate, vstartup, vready, vertical interrupt lines, v-total changes, and no-lock events.
- `OTG3_OTG_CRC_CNTL`, CRC window registers, CRC data registers, signature masks, readback windows, and `OTG_CRC320` through `OTG_CRC323` data registers configure and read CRC capture for multiple CRC engines/windows, including 16-bit RG/B/C fields and 32-bit R/G/B/C/AES readouts.
- `OTG3_OTG_DOUBLE_BUFFER_CONTROL`, `OTG3_OTG_UPDATE_LOCK`, `OTG3_OTG_MASTER_UPDATE_LOCK`, `OTG3_OTG_MASTER_UPDATE_MODE`, `OTG3_OTG_VUPDATE_KEEPOUT`, and `OTG3_OTG_GLOBAL_CONTROL0` through `GLOBAL_CONTROL4` describe double-buffer, master update lock, keepout, and global update-lock timing windows.
- `OTG3_OTG_GSL_CONTROL`, `OTG3_OTG_GSL_VSYNC_GAP`, `OTG3_OTG_GSL_WINDOW_X/Y`, `GSL_SOURCE_SELECT`, `OPTC_DLPC_CONTROL`, and `OPTC_CLOCK_CONTROL` are global sync lock and OPTC misc fields for selecting GSL sources, windows, master modes, vsync-gap diagnostics, DLPC snapshot, and OPTC clock gating.
- `OTG3_OTG_DRR_*`, `OTG3_OTG_M_CONST_DTO0/1`, `OTG3_OTG_REQUEST_CONTROL`, `OTG3_OTG_DSC_START_POSITION`, and `OTG3_OTG_PIPE_UPDATE_STATUS` cover dynamic refresh rate timing interrupts, v-total range/change/trigger windows, DRR control, DTO constants, request disabling, DSC start position, and pipe update keepout status.
- `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL3`, and `ODM_MEM_PWR_STATUS` expose per-ODM-memory power force/disable/state fields for memories 0-7 plus unassigned/vblank power modes.
- `DC_PERFMON17_*` describes one display perfmon instance: event selection, counted-value source/type, increment mode, hardware control, run enable, restart/interrupt bits, eight counter states, count-off interrupt handling, clock enable, cvalue high/low, and perfmon high/low readback.
- `HPD0_DC_HPD_*` through `HPD4_DC_HPD_*` repeat the hotplug-detect layout for five connectors: HPD sense/status, delayed sense, RX interrupt status, ack, polarity, enable, connection/RX timers, connect fast-train/AUX delays, and toggle-filter connect/disconnect delays.
- `DP0_DP_LINK_CNTL`, `DP0_DP_PIXEL_FORMAT`, `DP0_DP_CONFIG`, `DP0_DP_VID_STREAM_CNTL`, `DP0_DP_VID_TIMING`, `DP0_DP_VID_N/M`, `DP0_DP_LINK_FRAMING_CNTL`, and MSA/VBID fields encode DP link/stream setup, pixel encoding, MSA colorimetry and timing, timing offset, enhanced framing, TU/link training behavior, and stream interrupt handling.
- `DP0_DP_DPHY_*` fields define PHY internal controls, lane symbol values, 8b/10b mode, PRBS/scrambler controls, HBR2 pattern selection, CRC controls/results/status, fast-training controls/status, and BS/SR symbol-count swap controls.
- `DP0_DP_SEC_*`, `DP0_DP_GSP8_CNTL` through `GSP11_CNTL`, `DP0_DP_SEC_METADATA_TRANSMISSION`, and `DP0_DP_GSP_EN_DB_STATUS` are secondary packet controls for audio/video packets, GSP 0-11 send/enable/line-number/pending/active/deadline status, metadata packets, PPS marking, and GSP enable double-buffer status.
- `DP0_DP_MSE_*`, `DP0_DP_MSO_*`, `DP0_DP_DSC_CNTL`, and SAT status registers cover Multi-Stream Transport/Multi-Stream Operation: stream allocation table entries for sources 0-5, encryption flags/types, slot counts, SAT update/status, link timing, secondary-packet enable masks per SST link, and DSC mode.
- `DP0_DP_ALPM_CNTL`, `DP0_DP_AUXLESS_ALPM_CNTL1` through `CNTL5`, and stream/link symbol counters define low-power link sleep/standby/wakeup/FEC scheduling, AUX-less ALPM hardware mode, frame/line-number tracking, wakeup interrupts, and stream/link symbol counter enable/reset/status.
- `DIG0_DIG_FE_CNTL` and the start of `DIG0_DIG_FE_CLK_CNTL` define DIG frontend source selection, stereosync selection/gating, digital bypass, split-link pixel grouping, input-pixel selection, frontend mode, clock enable, and soft reset. The chunk stops after `DIG_FE_SOFT_RESET_MASK`, so remaining DIG0 clock masks belong to the next chunk.

## Control flow and usage model

There is no local control flow. These macros are data consumed by generated register-table initializers and block-specific helper code.

A typical use flow is:

1. Include `dcn_3_6_0_offset.h` for addresses and this header for field encodings.
2. Build ASIC-specific register, mask, and shift tables with macros such as `SR`, `SF`, `FD_MASK`, and `FD_SHIFT`.
3. Use DC register helpers such as `REG_SET`, `REG_UPDATE`, and `REG_GET` so callers can update named fields while preserving unrelated bits.

At runtime, higher-level DC code programs OTG timing and update locks during modeset; IRQ code uses interrupt status/clear masks; DP encoder/link code programs DP0 stream, PHY, secondary-packet, MST/MSO, DSC, and ALPM fields; hotplug code consumes HPD status/control fields; diagnostics and validation paths read CRC, perfmon, symbol-count, and timing-status registers.

## State and persistence behavior

The header has no mutable state. The state described by the masks lives in display hardware registers and persists according to GPU/display IP lifecycle: boot initialization, modeset, stream enable/disable, link training, runtime power management, suspend/resume, and GPU/display reset.

Important stateful areas include:

- OTG3 timing totals, blanking/sync, v-total min/max/mid, DRR windows, master update locks, and vupdate keepout fields. These must match active mode timing and be sequenced around double-buffer/master-update locks.
- Interrupt status/clear/ack fields for vstartup/vupdate/vready/vsync/vertical lines, DRR timing, HPD, DP video, secondary packets, perfmon, static screen, and ALPM wakeup. Some fields are write-one-to-clear or ack-oriented and should not be treated as ordinary persistent controls.
- CRC and snapshot state. CRC windows and selection controls are programmed by software, while CRC data/readback fields are hardware-produced diagnostics tied to frame timing.
- GSL/master-update state spans multiple timing generators; source selection and global-lock fields affect cross-pipe synchronization and can stall updates if mismatched.
- ODM memory power controls and OPTC/DIG/OTG/DP clock gates affect hardware block availability and power. Forced-on or disabled states can outlive a single modeset until reset or explicit reprogramming.
- HPD filter timers and enable/ack bits track connector presence and AUX/HPD RX interrupt flow, with repeated per-instance state for HPD0-4.
- DP0 secondary-packet, GSP, MST/MSO SAT, ALPM, and DPHY training/status fields are live protocol state. Pending/active/deadline/status bits reflect hardware progress and may change asynchronously while the link is running.
- DC perfmon counter configuration, state, interrupts, and high/low readbacks are shared diagnostic state that must be selected/read consistently.

## Dependencies and integration points

- Requires `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h` for matching register offsets. The shift/mask and offset headers are generated as a pair and must remain synchronized.
- Depends on the AMDGPU Display Core register-access infrastructure. The field names must match table initializers exactly; compile-time macros catch missing names, but they do not validate hardware semantics.
- Integrates with DCN 3.6 timing generator/OPTC code for OTG3 programming, global sync lock, double-buffering, CRC capture, static-screen detection, and dynamic refresh behavior.
- Integrates with DC IRQ and hotplug handling for vblank/vupdate/vertical interrupts and HPD0-4 sense/RX interrupt control.
- Integrates with DP encoder/link code for DP0 link configuration, DPHY training, video stream setup, MSA/VBID programming, secondary data packets, metadata, MST/MSO slot allocation, DSC, ALPM, and symbol counters.
- Integrates with diagnostics and validation paths through OTG CRC/readback registers, DP DPHY CRC, stream/link symbol counters, perfmon counter 17, and timing/status readbacks.
- Shares many repeated layouts with adjacent DCN versions and adjacent hardware instances. The chunk is instance-specific for OTG3, DP0, HPD0-4, and DIG0; callers should use the version and instance tables rather than assuming another DCN or pipe instance is bit-identical.

## Risks and edge cases

- Offset/mask drift is the primary generated-header risk. A correct field mask paired with a stale offset can silently write the wrong register.
- This chunk has two boundary truncations: it begins after the first `OTG2_OTG_PIPE_UPDATE_STATUS` shift field and ends inside `DIG0_DIG_FE_CLK_CNTL`. Final per-file analysis should reconcile the previous and next chunks for complete register coverage.
- Packed control/status registers are dense. Full-register writes can clobber interrupt status, clear bits, pending bits, readback selectors, reserved fields, or adjacent controls; read-modify-write helpers are expected for most software-owned fields.
- Field width mistakes can corrupt timing or protocol state. Many values are 7-, 8-, 10-, 11-, 13-, 15-, or 16-bit subfields packed into one register, while some control/status bitmaps occupy high bits such as `0x80000000L`.
- Status/control confusion is easy in this range. Names ending in `STATUS`, `CURRENT`, `READBACK`, `PENDING`, `ACTIVE`, `OCCURRED`, and `DEADLINE_MISSED` often represent hardware-owned state or interrupt events, not stable software-owned configuration.
- Timing-generator hazards include programming totals, blanking, update-lock windows, DRR windows, or GSL fields outside the expected modeset/vblank sequence, which can cause visible glitches, stuck updates, or cross-pipe synchronization failures.
- DP protocol hazards include enabling secondary packets at the wrong line, leaving GSP sends pending, programming MST SAT/MSO slot masks inconsistently, changing DPHY training/scrambler/PRBS controls during active video, or entering ALPM sleep/wakeup with stale line/frame scheduling.
- HPD hazards include failing to acknowledge RX or connect/disconnect interrupts, using wrong polarity, or setting filter timers too aggressively, causing missed hotplug events or interrupt storms.
- Power/clock hazards include forcing ODM memories or clocks off while the block is active, leaving clocks forced on after debug, or soft-resetting DIG/OTG paths without coordinated stream teardown.

## Test signals

- Build coverage with DCN 3.6.0 enabled should compile all register tables that include `dcn_3_6_0_sh_mask.h` together with `dcn_3_6_0_offset.h`.
- Static consistency checks should compare generated `__SHIFT`/`_MASK` pairs for representative fields and verify repeated HPD0-4 layouts remain intentionally identical.
- Modeset and timing tests should exercise OTG3 with standard, interlaced, stereo/3D, DSC-start, DRR/VRR, and multi-display global-sync-lock scenarios.
- IRQ tests should validate vblank/vsync/vupdate/vstartup/vready/vertical-line interrupt enable, status, clear, and ack behavior, plus DRR timing interrupts.
- CRC diagnostics should program OTG3 CRC windows and read both 16-bit CRC data registers and CRC320-323 32-bit data paths.
- Hotplug tests should cover HPD0-4 connect/disconnect, HPD RX interrupts, polarity handling, fast-training delay settings, and debounce/toggle filter timing.
- DP link tests should cover DP0 SST, MST/MSO, DSC, MSA timing/colorimetry, DPHY training patterns, scrambler/PRBS/CRC diagnostics, secondary audio/metadata/GSP packets, and stream/link symbol counters.
- ALPM tests should validate normal and AUX-less ALPM sleep, standby, wakeup, FEC scheduling, wakeup interrupts, pending/status bits, and resume into active video.
- Power-management and suspend/resume tests should inspect OTG/OPTC/DIG/DP clock status, ODM memory power status, and persistent update-lock or pending-packet bits after runtime PM and GPU reset.

### subset-b-002131: lines 32580-34984

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 32580-34984

## Scope

This chunk is a generated AMD DCN 3.6.0 register field shift/mask header segment. It contains preprocessor constants only: every exported item is a `#define` naming a hardware register field's bit shift or bit mask. There are no functions, structs, control statements, allocations, locks, or direct MMIO accesses in this slice. Runtime behavior is created by code that includes this header and feeds these constants into AMD display register helper macros.

The covered lines span the tail of the `dce_dc_dio_dig0_dispdec` block, the complete `dce_dc_dio_dp1_dispdec` block visible in this slice, the `dce_dc_dio_dig1_dispdec` block, and the beginning of `dce_dc_dio_dp2_dispdec`.

## Purpose

The chunk supplies bitfield metadata for the DCN 3.6 display I/O encoder path:

- `DIG0_*` and `DIG1_*` define Digital Front End, HDMI, AFMT, backend clock, TMDS, FIFO, CRC, test pattern, metadata, generic packet, audio clock regeneration, deep color, double-buffer, and version fields for two DIG instances.
- `DP1_*` defines DisplayPort stream/link/PHY/secondary-data/MST/ALPM/debug counters for DP instance 1.
- `DP2_*` begins the same DisplayPort field set for DP instance 2 and continues past the end of this chunk.

These constants let generic display code write field names such as `HDMI_DEEP_COLOR_ENABLE`, `DP_SEC_GSP0_ENABLE`, or `DP_MSE_SAT_UPDATE` without embedding numeric bit positions in the driver source.

## Important Defines And Register Areas

### DIG0 HDMI/TMDS Tail

The chunk starts in the DIG0 clock-control tail, then defines:

- `DIG0_DIG_FE_EN_CNTL`, `DIG0_DIG_OUTPUT_CRC_CNTL`, `DIG0_DIG_OUTPUT_CRC_RESULT`, `DIG0_DIG_CLOCK_PATTERN`, `DIG0_DIG_TEST_PATTERN`, and `DIG0_DIG_RANDOM_PATTERN_SEED` for front-end enable, output CRC, deterministic/static/random test patterns, and FIFO controls.
- `DIG0_DIG_FIFO_CTRL0` and `DIG0_DIG_FIFO_CTRL1` for FIFO enable/reset, read-start level, output pixel mode, reset/error status, overwrite level, average/min/max calibration, and recalculation triggers.
- `DIG0_HDMI_METADATA_PACKET_CONTROL`, `DIG0_HDMI_CONTROL`, `DIG0_HDMI_STATUS`, `DIG0_HDMI_AUDIO_PACKET_CONTROL`, `DIG0_HDMI_ACR_PACKET_CONTROL`, and `DIG0_HDMI_VBI_PACKET_CONTROL` for HDMI metadata scheduling, scrambling, deep color, Dolby Vision flags, TMDS encoding/color format, AVMUTE/error status, ACR packet generation, and VBI packet sends.
- `DIG0_HDMI_GENERIC_PACKET_CONTROL0` through `CONTROL10`, plus `CONTROL5` and `CONTROL6`, for generic HDMI packet 0-14 sends, continuous mode, line references, line numbers, immediate-send pending bits, and enable double-buffer pending status.
- `DIG0_HDMI_DB_CONTROL` for HDMI/VUPDATE double-buffer pending/taken/clear/lock/disable control.
- `DIG0_HDMI_ACR_32_*`, `ACR_44_*`, `ACR_48_*`, and `ACR_STATUS_*` for CTS/N values and readback.
- `DIG0_AFMT_CNTL`, `DIG0_DIG_BE_CLK_CNTL`, `DIG0_DIG_BE_CNTL`, and `DIG0_DIG_BE_EN_CNTL` for audio formatter and backend clock/enable state.
- `DIG0_TMDS_*` registers for TMDS enable, control characters, sync patterns, stereo sync, control bits, DC balancer behavior, and per-control-symbol generation.

### DP1 DisplayPort Block

`DP1_DP_LINK_CNTL`, `DP1_DP_PIXEL_FORMAT`, `DP1_DP_MSA_COLORIMETRY`, `DP1_DP_CONFIG`, and `DP1_DP_VID_STREAM_CNTL` define base link, pixel encoding/depth, MSA miscellaneous colorimetry, lane count, video-stream enable/status/defer/keepout fields.

PHY and low-level link fields include:

- `DP1_DP_STEER_FIFO` for steer FIFO reset and overflow/TU overflow flags, interrupts, acknowledgements, masks, and TU size.
- `DP1_DP_DPHY_INTERNAL_CTRL`, `DP1_DP_DPHY_CNTL`, `DP1_DP_DPHY_TRAINING_PATTERN_SEL`, `DP1_DP_DPHY_SYM0..2`, `DP1_DP_DPHY_8B10B_CNTL`, `DP1_DP_DPHY_PRBS_CNTL`, and `DP1_DP_DPHY_SCRAM_CNTL` for alternate scrambler reset, FEC enable/readiness/status, ALPM FEC disable mode, scrambler selection/disable/advance, bypass/skew bypass, training pattern selection, symbol patterns, 8b/10b reset/disp, and PRBS setup.
- `DP1_DP_DPHY_CRC_CONTROL0/1`, `CRC_RESULT0..3`, `CRC_STATUS`, `FAST_TRAINING`, and `FAST_TRAINING_STATUS` for PHY CRC capture/validity/phase status and fast-training trigger/done fields.

Video timing and framing fields include `DP1_DP_VID_TIMING`, `DP1_DP_VID_N`, `DP1_DP_VID_M`, `DP1_DP_LINK_FRAMING_CNTL`, `DP1_DP_VID_MSA_VBID`, `DP1_DP_VID_INTERRUPT_CNTL`, `DP1_DP_MSA_MISC`, `DP1_DP_MSA_TIMING_PARAM1..4`, `DP1_DP_MSO_CNTL`, `DP1_DP_MSO_CNTL1`, and `DP1_DP_DSC_CNTL`. These expose M/N generation, enhanced frame mode, VBID/MSA placement, stream-disable interrupts, detailed MSA timing values, multi-stream output controls, and DSC mode.

Secondary-data and packet scheduling fields include:

- `DP1_DP_SEC_CNTL` and `DP1_DP_SEC_CNTL1..7` for ASP/ATP/AIP/ACM/MPG/ISRC/GSP0-11 enables, line reference/line number, send/send-any-line/send-in-idle, pending, active, deadline-missed, PPS, audio mute, collision status/ack, and enable double-buffer disable controls.
- `DP1_DP_SEC_FRAMING1..4`, `DP1_DP_SEC_AUD_N`, `DP1_DP_SEC_AUD_M`, readback registers, `DP1_DP_SEC_TIMESTAMP`, and `DP1_DP_SEC_PACKET_CNTL` for SDP frame/start/idle/hblank/vblank placement, audio M/N, timestamp mode, ASP coding type, priority, version, and channel count override.
- `DP1_DP_SEC_METADATA_TRANSMISSION` for metadata packet enable, line reference, MSO metadata enable, and packet line.

MST/MSE fields include `DP1_DP_MSE_RATE_CNTL`, `DP1_DP_MSE_RATE_UPDATE`, `DP1_DP_MSE_SAT0..2`, `DP1_DP_MSE_SAT_UPDATE`, `DP1_DP_MSE_LINK_TIMING`, `DP1_DP_MSE_MISC_CNTL`, and `DP1_DP_MSE_SAT0_STATUS..2_STATUS`. They define MSE rate numerator/denominator style fields, pending updates, source-to-slot allocation table entries for streams 0-5, encryption bits, slot counts, SAT update modes, 16-MTP keepout, link frame/line timing, blank/timestamp/zero-encoder behavior, and SAT readback status.

Power-management and diagnostics include `DP1_DP_ALPM_CNTL`, `DP1_DP_AUXLESS_ALPM_CNTL1..5`, `DP1_DP_DPIA_SPARE`, `DP1_DP_DB_CNTL`, `DP1_DP_MSA_VBID_MISC`, `DP1_DP_GSP8_CNTL..GSP11_CNTL`, `DP1_DP_GSP_EN_DB_STATUS`, and stream/link symbol counters. These fields cover ALPM sleep/standby send and pending states, wake/FEC timing, HW-mode state, wake interrupts, double-buffer state, VBID overrides, generic SDP 8-11 scheduling, and counters for stream blanking symbols, link SR symbols, and link cycles.

### DIG1 HDMI/TMDS Block

`DIG1_*` largely mirrors the DIG0 definitions in this chunk, adding `DIG1_DIG_FE_CNTL` at the start of the block and ending with `DIG1_DIG_DEBUG` and `DIG1_DIG_VERSION`. The repeated field families are front-end clock/enable, output CRC, test pattern, FIFO, HDMI metadata/control/status/audio/ACR/VBI/infoframe/generic packet control, HDMI DB control, AFMT, backend clock/control/enable, TMDS control characters, sync patterns, control bits, DC balancer, and TMDS control-symbol generation.

Because field names are instance-prefixed (`DIG1_...`) while internal field suffixes often match DIG0, the instance prefix is the important binding to the correct register address table.

### DP2 Start

The chunk ends at `DP2_DP_DPHY_FAST_TRAINING` and includes the same early DP fields seen for DP1: link control, pixel format, MSA colorimetry, lane config, video stream control, steer FIFO, MSA misc, DPHY internal control, video timing M/N, link framing, HBR2 eye pattern, MSA/VBID, video interrupt, DPHY control/training symbols/8b10b/PRBS/scrambler, and DPHY CRC control/status/result. Later DP2 secondary-data and ALPM fields are outside this chunk.

## APIs, Types, And Consumers

This header does not define C APIs or types. Its effective API is the stable naming convention:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

AMD display code consumes these values through generated register tables and helper macros. Nearby consumers include:

- `display/dc/inc/reg_helper.h`, where `FN`, `REG_SET`, `REG_UPDATE`, and `REG_GET` combine register addresses with shift/mask entries.
- `display/dmub/src/dmub_reg.h`, which has a parallel `FD`/`FN` and `REG_*` helper layer for DMUB-side register access.
- DCN 3.6 users that include this exact header: `display/dmub/src/dmub_dcn36.c`, `display/dc/irq/dcn36/irq_service_dcn36.c`, and `display/dc/resource/dcn36/dcn36_resource.c`.
- DIO stream/link encoder headers and sources such as `display/dc/dce/dce_stream_encoder.h`, `display/dc/dce/dce_stream_encoder.c`, and newer `display/dc/dio/dcn*_dio_stream_encoder.h`, which map fields like HDMI generic packet sends/lines and DP secondary packet/GSP enables into per-encoder register structs.

The field constants must also align with the address-register header for the same ASIC generation, typically `dcn_3_6_0_offset.h`, and with resource macros that instantiate per-DIG/per-DP address arrays.

## Control Flow

There is no local control flow. In runtime code, the typical flow is:

1. A DCN 3.6 resource or encoder constructor selects the DCN 3.6 register, shift, and mask tables.
2. A stream/link encoder operation calls a helper such as `REG_UPDATE`, `REG_UPDATE_N`, `REG_SET`, or `REG_GET`.
3. The helper resolves a field by name to this header's shift/mask constants and the companion address constant.
4. The helper reads, masks, shifts, and writes the MMIO register or extracts a status field.

For fields in this chunk, that runtime flow controls HDMI infoframe/generic packets, HDMI ACR/deep-color/scrambling, TMDS legacy/link behavior, DP stream enablement, DP PHY training/CRC/test patterns, DP secondary packet scheduling, DP MST slot allocation, DP ALPM state changes, and status counter reads.

## State And Persistence Behavior

The header itself is stateless and has no persistence. The constants describe persistent hardware register bits whose values live in display engine registers until reset, power-gated, or overwritten by the driver/firmware. State-bearing fields in this chunk include:

- Enable bits such as `DIG*_DIG_FE_ENABLE`, `HDMI_METADATA_PACKET_ENABLE`, `DP_VID_STREAM_ENABLE`, `DP_SEC_STREAM_ENABLE`, `DP_DSC_MODE`, and ALPM HW-mode enables.
- Request/pending/status/ack fields such as HDMI generic immediate-send pending bits, HDMI/DP double-buffer pending/taken bits, DP secondary-packet pending/active/deadline-missed fields, DP MSE rate update pending, DP ALPM wake/FEC pending/status, and DPHY CRC valid/phase error acknowledgements.
- Readback/counter fields such as ACR CTS/N status, DP SAT status, DP stream symbol counts, DP link SR/cycle counts, CRC results, FIFO status, and version/debug fields.

Drivers using these fields must respect hardware sequencing. A mask/shift typo can silently target the wrong bit and leave display hardware in a stale or inconsistent state across modesets, link training, hotplug handling, or runtime power transitions.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register namespace being internally consistent:

- Register address macros for `DIG0`, `DIG1`, `DP1`, and `DP2` must use matching register names and instance numbering.
- Field list macros in DIO/DCE resource headers must refer to fields that exist in this header. For example, searches show resource and encoder code referencing HDMI generic packet registers, TMDS control bits, DP secondary GSP fields, DP MSE SAT fields, and ALPM-related DP fields.
- The shift and mask pairs must be compatible: every field should have the same bit position in `__SHIFT` that its mask implies. Many one-bit fields use masks such as `0x00000010L` with shifts such as `0x4`; multi-bit fields like line numbers, M/N values, slot counts, and timing parameters expose wider masks.
- Instance-specific fields use `DIG0_`, `DIG1_`, `DP1_`, and `DP2_` prefixes. Generic consumer macros often remove or remap instance prefixes through resource macros, so the prefix/address pairing is critical.

The header is indirectly integrated into Linux DRM/KMS behavior through AMD DC stream encoding, link encoding, DP MST, HDMI infoframes, audio packet scheduling, DSC/PPS transport, link training, interrupt service, and DMUB interactions.

## Risks And Edge Cases

- Generated-header drift: if `dcn_3_6_0_sh_mask.h` diverges from the matching offset/header tables, helpers can write valid-looking fields to the wrong register address or bit lane.
- Copy/paste instance errors: DIG0 and DIG1, and DP1 and DP2, are near duplicates. A single wrong prefix or missing field in one instance can break only one connector/encoder instance and be hard to detect in single-display testing.
- Write-one-to-clear and ack semantics: fields named `*_ACK`, `*_CLR`, `*_STATUS`, `*_PENDING`, and `*_DEADLINE_MISSED` should not be treated as ordinary read/write state by higher-level code. Incorrect read-modify-write sequences can clear interrupts or leave pending bits stuck.
- Double-buffer timing: HDMI and DP `*_DB_*`, `*_EN_DB_PENDING`, and `VUPDATE_DB_*` fields imply synchronized update behavior. Misusing masks can apply packet or stream changes on the wrong vertical update boundary.
- Link-training and PHY diagnostics: DP DPHY training, PRBS, scrambler, CRC, and fast-training fields can disrupt active links if written outside expected training/debug paths.
- MST allocation: `DP_MSE_SAT*` source, encryption, and slot count fields define payload allocation. Incorrect shifts or consumers can route slots to the wrong stream or corrupt MST bandwidth accounting.
- ALPM sequencing: sleep, standby, wake, FEC enable, AUX-less timing, and interrupt fields affect low-power link transitions; mistakes can cause black screens, wake failures, or intermittent link loss.
- Chunk boundary risk: this slice starts after the beginning of DIG0 and ends at the start of DP2 fast training. Cross-chunk reconciliation must include adjacent chunks to understand complete DIG0 and DP2 coverage.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware/display integration signals:

- Build the AMDGPU display driver with DCN 3.6 enabled; missing or renamed macros should fail compilation in resource, IRQ, DMUB, or DIO code that includes `dcn_3_6_0_sh_mask.h`.
- Run static consistency checks comparing `__SHIFT` values against masks, checking that `(mask >> shift)` forms a contiguous field for non-reserved fields.
- Compare DIG0/DIG1 and DP1/DP2 repeated field families for expected symmetry, allowing only known generation/instance differences.
- Exercise HDMI modes with deep color, scrambling, infoframes, metadata packets, AVMUTE, audio ACR, and generic packets; watch for packet deadline/pending/status anomalies.
- Exercise DisplayPort SST and MST modes, including DSC/PPS secondary packets, GSP scheduling, MSE SAT updates, DP audio M/N, link training, FEC, CRC diagnostics, and stream/link symbol counter reads.
- Exercise ALPM and AUX-less ALPM paths on supported panels/links, checking sleep/wake/FEC pending/status fields and display resume reliability.
- Monitor DRM logs and hardware status reads for FIFO errors, steer/TU overflow, secondary-packet deadline misses, double-buffer pending bits that never clear, and DPHY CRC phase errors.

## Open Questions For Merge Lane

- Adjacent chunks should confirm the complete DIG0 block before line 32580 and the remaining DP2 secondary-data/MST/ALPM fields after line 34984.
- The final per-file report should identify the generator source, if present in the repository, because this file is generated and should normally be fixed at generator/input data level rather than by hand editing the header.

### subset-b-002132: lines 34985-37380

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 34985-37380

## Scope

This chunk is a generated-register slice of AMDGPU's DCN 3.6.0 shift/mask header. It contains preprocessor constants only: no functions, structs, enums, storage objects, includes, locking, allocation, or executable control flow. The exported contract is the standard generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` namespace used by AMD display register-helper code to pack and unpack MMIO fields.

The range starts in the middle of the `DP2_DP_DPHY_FAST_TRAINING` register fields, covers the rest of the DP2 DisplayPort encoder block, then covers the full `dce_dc_dio_dig2_dispdec` DIG/HDMI/TMDS block, most of the `dce_dc_dio_dp3_dispdec` DP3 DisplayPort encoder block, and ends at the start of the `dce_dc_dio_dig3_dispdec` DIG3 FIFO fields. In this exact range there are 2,171 `#define` entries: about 668 `DP2_*`, 590 `DIG2_*`, 838 `DP3_*`, and 75 `DIG3_*` macros.

Although the source tree path is under a local `ceph-client` mirror, this file is AMD display hardware metadata. It has no Ceph, filesystem, distributed-storage, network, or persistent-disk behavior.

## Purpose

The purpose of this header range is to provide DCN 3.6.0 bit geometry for DisplayPort and DIG/HDMI/TMDS encoder programming. Runtime AMD display code combines these masks and shifts with the matching `dcn_3_6_0_offset.h` register offsets, builds per-ASIC register tables, and uses generic helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` to touch only the intended hardware bits.

The covered hardware areas are:

- DP2 tail fields for fast link training, secondary-data-packet transmission, MST payload-slot allocation, main-stream-attribute timing, MSO/DSC, generic secondary packets, double-buffering, VBID/misc metadata, ALPM and auxless ALPM, and stream/link symbol counters.
- DIG2 front-end, HDMI, audio formatter, back-end, and TMDS fields, including clock/reset/enable, output CRC, test patterns, FIFO calibration, HDMI metadata packets, HDMI control/status, audio clock regeneration, VBI/infoframe/generic-packet scheduling, HDMI double buffering, audio clock-regeneration readback, TMDS control characters, DC balancing, and `DIG_VERSION`.
- DP3 fields from the beginning of the DP3 block through the same DP secondary-packet, MSE/MST, MSO/DSC, ALPM, and symbol-counter groups covered for DP2, plus earlier DP3 link/video/DPHY controls that are outside the DP2 tail in this chunk.
- DIG3 beginning fields for front-end clock/source selection, enable, output CRC, test pattern generation, random-pattern seed, and the start of FIFO control.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The important interface is the generated macro pattern:

- `*_SHIFT` gives a field's least-significant bit position.
- `*_MASK` gives the already-shifted mask used for read/modify/write or readback extraction.

The DP2 and DP3 secondary-data-packet groups define fields for `DP_SEC_CNTL`, `DP_SEC_CNTL1` through `DP_SEC_CNTL7`, `DP_SEC_FRAMING*`, `DP_SEC_PACKET_CNTL`, `DP_SEC_METADATA_TRANSMISSION`, `DP_GSP8_CNTL` through `DP_GSP11_CNTL`, and `DP_GSP_EN_DB_STATUS`. These fields control enable bits for audio stream packets, ASP/ATP/AIP/ACM packets, GSP0-GSP11 packets, MPG/ISRC/PPS use, packet line references, send and pending/deadline status, double-buffer-disable bits, and DB pending readbacks.

The DP2 and DP3 MSE/MST groups define `DP_MSE_RATE_CNTL`, `DP_MSE_RATE_UPDATE`, `DP_MSE_SAT0` through `DP_MSE_SAT2`, matching `*_STATUS` readbacks, `DP_MSE_LINK_TIMING`, and `DP_MSE_MISC_CNTL`. They describe stream-source selection, encryption enable/type, slot counts, update triggering/pending state, link timing, and miscellaneous MST behavior. `DP_MSO_CNTL` and `DP_MSO_CNTL1` extend secondary-packet enables across multiple SST links for MSO use, while `DP_DSC_CNTL` exposes DSC mode selection.

The DP timing and link-status groups include `DP_MSA_TIMING_PARAM1` through `PARAM4`, `DP_MSA_VBID_MISC`, and, for DP3, `DP_LINK_CNTL`, `DP_PIXEL_FORMAT`, `DP_MSA_COLORIMETRY`, `DP_CONFIG`, `DP_VID_STREAM_CNTL`, `DP_STEER_FIFO`, `DP_MSA_MISC`, `DP_VID_TIMING`, `DP_VID_N`, `DP_VID_M`, `DP_LINK_FRAMING_CNTL`, `DP_VID_MSA_VBID`, and `DP_VID_INTERRUPT_CNTL`. These fields encode MSA totals/start/sync/active-size values, VBID and misc bytes, pixel encoding/depth, lane count, stream enable/status, FIFO overflow/TU size, M/N generation, enhanced framing, and stream-disable interrupt ack/mask bits.

The DP3 DPHY groups include internal scrambler reset, FEC enable/ready/active and ALPM disable behavior, training pattern selection, 10-bit symbol fields, 8b/10b running-disparity controls, PRBS controls, scrambler controls, CRC control/result/status registers, and fast-training control/status fields. The DP2 part of this chunk starts after most comparable DPHY fields and only includes the tail of fast-training plus CRC result 2/3.

The ALPM groups are present for both DP2 and DP3. `DP_ALPM_CNTL` covers panel replay/ALPM-like enable, PHY sleep/repeat/delay, AUX wake enable, status, power-up PHY display-count, and update-pending bits. `DP_AUXLESS_ALPM_CNTL1` through `CNTL5` describe auxless sleep timing, wakeup send/immediate/pending bits, FEC-enable timing, line numbers, hardware-mode state, force-wakeup, frame counters, and wakeup interrupt mask/status/clear/frame/line fields.

The DIG2 and DIG3 front-end groups define `DIG_FE_CNTL`, `DIG_FE_CLK_CNTL`, `DIG_FE_EN_CNTL`, output CRC control/result, clock/test/random-pattern controls, and FIFO control/calibration fields. These macros select timing-generator source, stereosync, digital bypass, split-link grouping, input pixel select, front-end mode/clock/reset/gating, CRC source/link/data selection, deterministic or random output test patterns, FIFO reset/read level/read clock/output pixel mode, FIFO error, overwrite/calibration/min/max level, and recalibration controls. DIG3 is only partially covered, ending after the first `DIG3_DIG_FIFO_CTRL1` fields.

The DIG2 HDMI groups cover `HDMI_METADATA_PACKET_CONTROL`, `HDMI_CONTROL`, `HDMI_STATUS`, `HDMI_AUDIO_PACKET_CONTROL`, `HDMI_ACR_PACKET_CONTROL`, `HDMI_VBI_PACKET_CONTROL`, `HDMI_INFOFRAME_CONTROL0/1`, `HDMI_GENERIC_PACKET_CONTROL0/1/2/3/4/5/6/7/8/9/10`, `HDMI_GC`, `HDMI_DB_CONTROL`, `HDMI_ACR_*`, and `AFMT_CNTL`. They define packet enable/send/line/continue behavior for many generic packet slots, immediate-send and pending bits, double-buffer pending/taken/lock/disable state, keepout and scrambling controls, HDMI error ack/mask/status, Dolby Vision metadata status, TMDS encoding/deep color fields, ACR source/auto-send/CTS/N behavior, VBI enable/status, and audio clock gate/readback fields.

The DIG2 TMDS groups define back-end clock/control/enable fields and TMDS-specific controls: color depth, 8b/10b bypass, control characters, feedback, stereosync control selection, sync-character patterns, control-bit mappings, DC balancer enable/test/status, sync DC-balance character, and control-character generator fields for CTL0/1 and CTL2/3.

## Control Flow

This header range has no local runtime control flow. Runtime behavior is created by consumers that include the DCN 3.6.0 offset and shift/mask headers and expand register-list macros into register tables.

A typical path is:

1. DCN36 resource, IRQ, DMUB, DIO, stream-encoder, and link-encoder code includes `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h`.
2. Register-list macros paste logical register names onto generated instance names such as `DP2_DP_SEC_CNTL`, `DP3_DP_MSE_SAT_UPDATE`, `DIG2_HDMI_GENERIC_PACKET_CONTROL0`, or `DIG3_DIG_FE_CNTL`.
3. Field macros paste logical field names onto `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`.
4. Runtime register helpers perform MMIO reads/writes and read/modify/write updates using the generated offset, mask, and shift tables.

The header does not encode sequencing. Callers must still follow hardware ordering for link training, stream enable/disable, MST payload updates, secondary-packet scheduling, HDMI packet double-buffering, TMDS/HDMI mode switches, audio clock regeneration, ALPM/auxless wake transitions, interrupt ack/mask handling, FIFO reset/calibration, and suspend/resume restore.

## State And Persistence Behavior

The file itself stores no software state and persists nothing. It describes DCN 3.6.0 hardware register state whose lifetime is controlled by modesets, link training, hotplug, stream enable/disable, MST topology changes, power gating, suspend/resume, and GPU reset.

State represented by this chunk includes:

- DP stream and link state: stream enable/status, pixel format/depth, lane count, M/N timing, MSA timing/misc/VBID fields, link training completion, DPHY training pattern/symbol/scrambler/FEC/CRC/PRBS state, fast-training completion, and stream/link symbol counters.
- DP secondary-packet state: stream/audio packet enables, GSP0-GSP11 scheduling, send/pending/deadline status, line-number targeting, packet framing windows, metadata transmission, double-buffer disable/pending state, collision/audio mute status, and MPG/ISRC/PPS controls.
- MST/MSO/DSC state: MSE rate update, stream-to-slot allocation, slot counts, encryption bits, status readbacks, link timing, MSO per-link secondary packet enables, and DSC mode.
- ALPM state: AUX wake enable/status, PHY sleep/wake timing, auxless wake/FEC line scheduling, hardware-mode enable/status, current state, wakeup interrupts, and update-pending/readback bits.
- DIG/HDMI/TMDS state: front-end source and clock/reset/enable state, FIFO level/calibration/error state, output CRC and test-pattern state, HDMI packet scheduling and double buffering, HDMI control/status/error state, audio clock regeneration values, AFMT audio clock state, TMDS color/control/DC-balance state, and DIG version readback.

Persistence is hardware-defined. Many configuration fields remain active until the relevant stream, link, encoder, or power domain is reprogrammed or reset. Status bits can be read-only, sticky, self-clearing, write-one-to-clear, or valid only while the relevant clock is active. The generated masks do not state access semantics, so consuming code and ASIC documentation must determine whether a field is safe to write, poll, clear, or preserve.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h`, which provides matching register offsets. These mask/shift constants are correct only when paired with the DCN 3.6.0 register database and offset header.

Visible integration points in this tree include:

- `display/dc/resource/dcn36/dcn36_resource.c`, which includes the DCN 3.6.0 generated headers and expands DCN36 register and mask/shift lists while constructing the DCN36 resource pool.
- `display/dc/irq/dcn36/irq_service_dcn36.c`, which includes the same generated headers for DCN36 IRQ source metadata.
- `display/dmub/src/dmub_dcn36.c` and `display/dmub/src/dmub_dcn36.h`, where DCN36 DMUB register initialization binds firmware-service register offsets and field masks/shifts.
- Common stream-encoder code under `display/dc/dce/dce_stream_encoder.*`, which uses `DIG_FE_CNTL`, `DP_SEC_CNTL`, HDMI generic-packet controls, HDMI ACR/control/status fields, AFMT, and related field names through generated tables.
- Common link-encoder code under `display/dc/dce/dce_link_encoder.*`, which uses `DP_LINK_CNTL`, `DP_MSE_SAT*`, `DP_MSE_SAT_UPDATE`, `DP_SEC_CNTL`, and `DP_SEC_CNTL1` for link training completion, MST slot programming, and secondary-packet control.
- DIO stream-encoder code under `display/dc/dio/dcn32/`, which demonstrates later-generation use of `DIG_FE_CNTL` and `DP_SEC_CNTL` fields for clock/status and secondary-stream enable handling; DCN36 inherits the same generated-header pattern with ASIC-specific constants.

These macros are cross-generation in shape but not interchangeable. Similar names appear in DCN 3.5.x, 3.2.x, and later DCN headers, but field presence, exact masks, offsets, and instance counts may differ.

## Risks And Edge Cases

- Shift/mask constants are untyped preprocessor values. A wrong value can compile cleanly while writing an adjacent MMIO bit, truncating a field, decoding a status incorrectly, or leaving stale bits behind.
- The chunk starts and ends on artificial boundaries. It begins after the `DP2_DP_DPHY_FAST_TRAINING` comment and initial fields from the previous lines, and it ends in the middle of `DIG3_DIG_FIFO_CTRL1`; adjacent chunks are required before making complete claims about those registers.
- DP2 and DP3 are highly repetitive but not identical in this range. DP3 includes full link/video/DPHY setup from `DP_LINK_CNTL` onward, while DP2 is only the tail of its block. Copying conclusions or masks between instances without checking the generated names can hide instance-specific omissions.
- MST payload fields are sequencing-sensitive. Incorrect `DP_MSE_SAT*`, status, or update masks can produce wrong slot allocations, stuck update-pending state, bandwidth accounting errors, or failures that only appear with MST hubs and multiple streams.
- Secondary packet fields are display-protocol-sensitive. Bad GSP, infoframe, metadata, PPS, audio, MPG, or ISRC masks can cause missing HDR/VRR/DSC metadata, wrong audio packets, stale packets after modeset, deadline misses, or packet collision status that never clears.
- HDMI double-buffer fields can be side-effect-sensitive. Confusing pending, taken, clear, lock, and disable bits can leave packet programming stale, produce one-frame glitches, or make updates race vblank/vupdate timing.
- ALPM and auxless ALPM fields interact with PHY sleep/wake and FEC timing. Bad masks can cause wake failures, excessive power use, link instability, FEC transition problems, or wakeup interrupts that are missed or storming.
- DPHY and TMDS controls affect physical link behavior. Errors in scrambler, FEC, training pattern, 8b/10b, PRBS, DC balancer, color depth, or control-character fields can create blank displays, link-training failures, receiver-specific HDMI/DP failures, or intermittent corruption.
- Status/ack/mask naming is easy to confuse. Many fields have paired `*_STATUS`, `*_ACK`, `*_MASK`, `*_PENDING`, and `*_OCCURRED` names; using a mask constant for the wrong semantic can wedge interrupts or clear diagnostics unexpectedly.

## Test Signals

Useful validation combines generated-header consistency, build coverage, and hardware behavior:

- Build AMDGPU display with DCN36 enabled. Missing or renamed macros should fail in DCN36 resource construction, IRQ service, DMUB register initialization, stream encoder, or link encoder register-table expansion.
- Mechanically verify that every complete field in lines 34985-37380 has the expected `__SHIFT` and `_MASK` pair, while treating the first and last register groups as chunk-boundary partials.
- Diff this range against AMD's authoritative DCN 3.6.0 register database and nearby generated headers such as DCN 3.5.x or later DCN variants, with expected per-generation differences reviewed instead of blindly normalized.
- Exercise DisplayPort link training, stream enable/disable, pixel format/depth changes, M/N timing, CRC capture, PRBS/test patterns, FEC enable/disable, and fast-training status on DCN36 hardware.
- Test MST topologies with multiple streams, payload slot reallocation, hotplug/unplug, suspend/resume, DSC streams, and MSO cases; watch for stuck `DP_MSE_RATE_UPDATE`, wrong slot counts, or stream-to-slot mapping errors.
- Exercise DP secondary packets for audio, VSC, SPD, HDR static metadata, DSC PPS, ISRC/MPG, and generic GSP8-GSP11 packets across modeset, vblank-timed send, immediate send, and double-buffer updates.
- Exercise HDMI output with scrambling, deep color, Dolby Vision metadata status, VBI/infoframes, generic packets 0-14, metadata-packet missed status, ACR CTS/N values for 32/44.1/48 kHz families, and audio stream enable/disable.
- Validate TMDS behavior across 8b/10b bypass, color depth changes, control-character generation, DC balancer state, stereo sync, and receiver hotplug.
- Test ALPM and auxless ALPM with panel/link idle, forced wakeup, FEC wake scheduling, hardware-mode transitions, wakeup interrupts, and resume from suspend.
- Watch kernel logs, display diagnostics, and hardware status for link-training failures, blank output, packet deadline missed bits, HDMI DB pending stuck high, metadata-packet missed bits, FIFO error/overflow, CRC mismatches, audio loss, MST bandwidth failures, wakeup interrupt storms, and failures that appear only on DP2/DP3 or DIG2/DIG3 instances.

## Cross-Chunk Notes

This is not a standalone source module. It is one generated slice inside `dcn_3_6_0_sh_mask.h`. The preceding chunk owns the earlier DP2 DPHY fields and the beginning of `DP2_DP_DPHY_FAST_TRAINING`; this chunk owns the DP2 tail, full DIG2 block, most of the DP3 block, and the start of DIG3. The following chunk continues `DIG3_DIG_FIFO_CTRL1` and later DIG3 HDMI/TMDS/register groups. The merge/reconciliation lane should combine adjacent chunks before making whole-file claims about all DCN 3.6.0 DIO/DIG/DP register fields.

### subset-b-002133: lines 37381-39778

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 37381-39778

## Purpose

This chunk is a generated AMD DCN 3.6 register shift/mask header segment. It contains only preprocessor constants; there are no executable functions, C types, or local algorithms. The API surface is the generated naming contract where `REGISTER__FIELD__SHIFT` gives a field bit position and `REGISTER__FIELD_MASK` gives the packed register mask. Driver code combines these constants with matching register addresses from `dcn_3_6_0_offset.h` and AMD display register helpers such as `FD_SHIFT`, `FD_MASK`, `SE_SF`, `SRI`, `REG_UPDATE`, `REG_SET`, and `REG_GET`.

The requested range covers 2,168 `#define` constants across 218 register comment groups. It starts in the middle of `DIG3_DIG_FIFO_CTRL1`, then covers most of DIO digital encoder instance 3 HDMI/TMDS fields, the complete displayed DisplayPort instance 4 (`DP4`) field set in this range, digital encoder instance 4 (`DIG4`) front-end/FIFO/HDMI/TMDS fields, all AFMT instance 0 fields present for the chunk, and the beginning of AFMT instance 1 through the audio CRC control area at the line boundary.

## Important API Surface

There are no callable APIs. The important interfaces are the generated field macros consumed by register-list headers and resource construction:

- `DIG3_*` fields describe the tail of digital encoder 3 FIFO calibration plus HDMI packet generation, HDMI control/status, audio clock regeneration, generic packets, deep-color packet control, AFMT routing, digital backend clock/control/enable, TMDS control characters, DC balancing, sync character patterns, and the `DIG_VERSION` readout.
- `DP4_*` fields describe DisplayPort stream/link programming for DIO DisplayPort instance 4. The group includes link control, pixel format, MSA colorimetry and timing, stream enable/status, steer FIFO, DPHY internal/training/8b10b/PRBS/scrambler/CRC/fast-training controls, secondary packet and audio timing fields, MST/MSE rate and slot allocation, DSC, metadata transmission, ALPM and auxless ALPM controls, GSP8-GSP11 packet controls, and stream/link symbol-count diagnostics.
- `DIG4_*` repeats the digital encoder programming surface for instance 4: FE clock/enable/source selection, output CRC, clock/test/random patterns, FIFO controls, HDMI metadata/control/status/audio/ACR/VBI/infoframe/generic-packet fields, deep-color DB control, AFMT routing, backend control, TMDS encoding and DC-balancing fields, debug, and version.
- `AFMT0_*` covers audio format instance 0. The fields include ACP packet bytes, VBI packet source and HDMI audio-packet pacing, audio layout/channel enable/DP stream ID/HBR and IEC-60958 overrides, HDMI audio infoframe payload fields, IEC-60958 channel-status words, audio CRC controls/results, ramp test pattern controls, AFMT status, sample-send and acknowledge bits, audio infoframe update/source, audio source select, and memory power controls.
- `AFMT1_*` begins the same AFMT layout for instance 1 and reaches the audio CRC control/ramp-control boundary. It includes ACP, VBI packet control, packet-control2, audio infoframes, IEC-60958 words 0 and 1, and audio CRC field definitions within this range.

Representative high-risk field families include `HDMI_GENERIC*_SEND/CONT/LINE`, `HDMI_ACR_*_CTS/N`, `DP_MSA_*`, `DP_DPHY_*`, `DP_SEC_*`, `DP_MSE_*`, `DP_ALPM_*`, `AFMT_AUDIO_CHANNEL_ENABLE`, `AFMT_DP_AUDIO_STREAM_ID`, `AFMT_60958_*`, `AFMT_AUDIO_SAMPLE_SEND`, and `AFMT_MEM_PWR_*`. Many are packed next to status or pending bits, so field-level access helpers are expected rather than ad hoc whole-register writes.

## Control Flow and Usage Model

This header has no runtime control flow. Its compile-time data flow is:

1. DCN 3.6 source includes `dcn_3_6_0_offset.h` and this shift/mask header.
2. Resource and block constructors expand register-list macros such as `SRI`/`SRI_ARR` to bind instance-specific offsets, and `SE_SF`/`FD_MASK`/`FD_SHIFT` to copy field masks and shifts into block-local register structures.
3. Runtime display code programs or reads MMIO registers using those structures, so call sites can name logical fields instead of open-coding bit positions.

The direct include points found for this ASIC header are `display/dmub/src/dmub_dcn36.c`, `display/dc/irq/dcn36/irq_service_dcn36.c`, and `display/dc/resource/dcn36/dcn36_resource.c`. The DIO and AFMT fields in this chunk are mainly used through shared DCN30/DCN31/DCN35/DIO stream encoder and AFMT patterns rather than through functions in this header. For example, AFMT register tables use `AFMT0_AFMT_AUDIO_PACKET_CONTROL2`, `AFMT0_AFMT_AUDIO_PACKET_CONTROL`, `AFMT0_AFMT_60958_*`, and `AFMT0_AFMT_MEM_PWR` masks to drive audio layout, channel status, sample send, and AFMT memory power. DIO stream encoder tables in nearby generations use the same families for HDMI metadata/generic packets, HDMI ACR, TMDS pixel encoding/color format, DP MSA timing, DP secondary packets, and DIG FIFO/FE controls.

## State and Persistence Behavior

The macros themselves are stateless. The state they describe is hardware-resident MMIO state that persists until reprogrammed, reset, power-gated, or overwritten during modeset/resume:

- HDMI packet controls determine whether metadata, infoframes, generic packets, audio packets, ACR packets, null/GC/ACP/ISRC packets, and Dolby Vision metadata are emitted, whether they are continuous or one-shot, and which display line is used.
- HDMI/TMDS fields hold sink-facing link encoding state: scrambling, clock-channel rate, deep color, pixel encoding, color format, keepout behavior, control characters, DC balancing, sync patterns, and backend enable/clock controls.
- DP4 link and stream fields hold active DisplayPort state: lane/link framing, pixel format, MSA timing/colorimetry, VBID, training pattern, scrambler/PRBS/CRC, secondary packet scheduling, MST slot allocation/rate updates, DSC enablement, ALPM timing, and symbol-count diagnostics.
- AFMT fields hold audio packet and channel-status state, including HDMI/DP audio stream selection, channel enable mask, layout/HBR/IEC-60958 overrides, audio infoframe payload, audio CRC/test-ramp configuration, sample-send enable, status/acknowledge bits, and AFMT memory power state.
- Status and readback fields such as missed packet flags, pending packet sends, ACR status, CRC done/results/status, fast-training status, stream/link symbol counters, `AFMT_STATUS`, and memory-power state are hardware-observed state and should not be treated as ordinary software-owned configuration.

## Dependencies and Integration Points

- Requires the matching `dcn_3_6_0_offset.h`; this header provides bit layouts but not register addresses or base indices.
- Depends on AMD display register macro infrastructure in `reg_helper.h` and block headers that build `shift` and `mask` structures from generated `*_SHIFT`/`*_MASK` names.
- Integrates with DCN 3.6 resource construction in `dcn36_resource.c`, which includes the generated headers and defines `SRI`, `SRI_ARR`, and related macros for instance-aware register address setup.
- Integrates with DMUB register initialization in `dmub_dcn36.c`; that path copies selected generated fields into DMUB register tables. This chunk's DIO/AFMT fields are not the main DMUB scratch/mailbox surface, but they share the same generated-header dependency.
- Integrates with IRQ service compilation for DCN 3.6 through the same include pair, although this chunk is mostly stream/audio/link field definitions rather than interrupt routing logic.
- Uses shared block layouts from prior DCN generations. AFMT register-list headers from DCN30/DCN31 consume `AFMT0_*` masks with `SE_SF`; DIO stream encoder headers from later/nearby generations consume matching `DIG0_*` and `DP0_*` field families. Instance number changes (`DIG3`, `DIG4`, `DP4`, `AFMT0`, `AFMT1`) are resolved by register-table construction rather than by unique code paths for every instance.

## Risks and Edge Cases

- Boundary truncation: this chunk starts after the first `DIG3_DIG_FIFO_CTRL1` shift definitions and ends before the full `AFMT1` block is complete. The final per-file merge must reconcile adjacent chunks before declaring either group complete.
- Offset/mask drift: generated offset and shift/mask headers must match the same hardware register database. A correct-looking field mask paired with a stale offset can write a valid bit pattern into the wrong register.
- Repeated-instance mistakes: `DIG3` and `DIG4` are structurally similar, and `AFMT0`/`AFMT1` repeat the AFMT layout. A wrong instance table can create failures isolated to one connector, stream encoder, or audio formatter.
- Packed-field corruption: line numbers, packet-send bits, pending/missed flags, control bits, and status bits often share a register. Whole-register writes can unintentionally clear diagnostics, retrigger packets, or change timing.
- HDMI timing sensitivity: generic-packet line numbers, metadata packet enables, ACR CTS/N values, deep-color controls, scrambling, and TMDS color-format fields may fail only with specific HDMI sinks, HDR/Dolby Vision metadata, high pixel clocks, deep color, or audio sample-rate transitions.
- DP link-training and MST sensitivity: DPHY training/scrambler/PRBS fields, MSE slot/rate updates, DSC controls, ALPM/auxless ALPM fields, and secondary packet scheduling can produce sink-specific black screens, link drops, audio loss, or power-state regressions when programmed out of sequence.
- Status-versus-control confusion: fields named `*_STATUS`, `*_READBACK`, `*_DONE`, `*_PENDING`, `*_MISSED`, `*_RESULT`, and symbol-count status fields are diagnostic or hardware-owned in normal operation.
- Width validation: packed values include 4-bit channel numbers, 5-bit packet counts, 6-bit HDMI line fields, 8-bit infoframe and audio source/channel fields, 16-bit MSA/ACR/symbol-count fields, 24-bit CRC/ramp fields, and full 32-bit timestamp/symbol-count values. Callers must clamp before shifting.
- Power sequencing: `DIG*_DIG_BE_CLK_CNTL`, `DIG*_DIG_BE_EN_CNTL`, `DIG*_DIG_FE_CLK_CNTL`, `DIG*_DIG_FE_EN_CNTL`, `AFMT*_AFMT_MEM_PWR`, and DP ALPM fields interact with runtime power management. Forcing a block off or into low power while packets or audio are active can cause hangs or silent output loss.

## Test Signals

- Build with DCN 3.6 enabled to catch missing generated names in resource, IRQ, DMUB, DIO stream encoder, and AFMT register-table expansion.
- Static checks should verify every field in the chunk has coherent shift/mask geometry, no overlap within expected packed fields, and repeated layouts align where `DIG3`/`DIG4` or `AFMT0`/`AFMT1` are intended to mirror.
- HDMI runtime coverage should include modesets across 8bpc/deep-color, scrambling on/off, TMDS pixel encoding and color-format changes, HDR/Dolby Vision metadata, generic packet sends, infoframes, ACR updates for 32/44.1/48 kHz families, suspend/resume, and hotplug.
- DP4 coverage should exercise link training patterns, scrambler/PRBS/CRC diagnostics, MSA timing/colorimetry, SST and MST/MSE slot allocation, DSC, secondary audio/data packets, metadata transmission, ALPM/auxless ALPM, and stream/link symbol counters.
- Audio coverage should validate HDMI and DP audio enumeration, AFMT channel enable/layout, DP audio stream ID selection, IEC-60958 channel-status programming, HBR override behavior, audio sample send, audio CRC diagnostics, and audio disable/re-enable transitions.
- Power-management coverage should watch DIG FE/BE clock gating, AFMT memory power state, ALPM state, resume/retrain paths, and packet/audio recovery after display core reset.
- Register-dump diagnostics should inspect `DIG3_HDMI_*`, `DIG4_HDMI_*`, `DP4_DP_*`, `AFMT0_AFMT_*`, and `AFMT1_AFMT_*` fields when debugging sink-specific packet timing, link training, audio dropouts, color-format mismatches, or power regressions.

### subset-b-002134: lines 39779-42166

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 39779-42166

## Scope

This chunk is a middle slice of AMDGPU's generated DCN 3.6.0 register shift/mask header. It contains preprocessor constants only: no functions, structs, enums, storage objects, or executable control flow. Its interface is the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` namespace, where each macro describes one bitfield position and already-shifted mask for DCN 3.6.0 display hardware registers.

The range starts in the tail of the `AFMT1_AFMT_AUDIO_CRC_CONTROL` block, covers the remainder of AFMT1, then full AFMT2, AFMT3, and AFMT4 audio formatter field groups. It then covers DME and VPG metadata/generic-packet field groups for DIG0 through DIG4. The final portion covers full DP AUX0 and DP AUX1 field groups and ends after the first few DP AUX2 arbitration fields. Adjacent chunks own the beginning of AFMT1 and the remainder of DP AUX2 and later blocks.

Although this file lives under `sources/distributed-fs/ceph-client`, this source is AMD display hardware metadata. It has no Ceph, filesystem, distributed-storage, network-protocol, or persistent-disk behavior.

## Purpose

The purpose of this header range is to give DCN 3.6 display code exact bit geometry for audio packet generation, metadata packet generation, generic secondary-data packets, and DisplayPort AUX engines. Runtime code pairs these masks and shifts with `dcn_3_6_0_offset.h` offsets to build register tables and perform MMIO read/modify/write operations through AMD display helper macros.

The covered hardware areas are:

- `AFMT1` tail plus `AFMT2` through `AFMT4`: HDMI/DP audio formatter fields for ACP packet type bytes, VBI audio packet controls, audio layout/channel enable/DP stream ID, HDMI audio infoframe payload, IEC 60958 channel-status words, audio CRC generation/result, audio test ramp generation, audio status bits, packet-send/update/ack controls, audio source selection, and AFMT memory power.
- `DME0` through `DME4`: display metadata engine controls for metadata HUBP requester selection, metadata engine enable, stream type, double-buffer pending/taken state, DB clear/disable controls, missed-transmission status/clear, and DME memory power.
- `VPG0` through `VPG4`: video packet generator fields for indexed generic packet data, frame-synchronized and immediate generic packet update triggers/pending bits, generic-packet lock/conflict status, VPG GSP memory power, ISRC indexed packet data, and MPEG infoframe fields.
- `DP_AUX0` and `DP_AUX1`: DisplayPort AUX channel control, software transaction launch, arbitration, interrupt/status/ack/mask bits, software and link-service data windows, DPHY TX/RX timing and status, GTC sync control/error/status, and PHY wake handshakes.
- `DP_AUX2` beginning: AUX control, software transaction control, and the first arbitration fields before the chunk ends.

## Important APIs, Types, And Macros

There are no C APIs or concrete types in this chunk. The important API is the generated macro pattern:

- `*_SHIFT` gives the least-significant bit position for a field.
- `*_MASK` gives the field mask in final register position.
- The register prefix encodes the block and instance, for example `AFMT2_AFMT_AUDIO_PACKET_CONTROL2`, `DME3_DME_CONTROL`, `VPG4_VPG_GSP_FRAME_UPDATE_CTRL`, or `DP_AUX1_AUX_GTC_SYNC_STATUS`.

The AFMT groups are the audio packet programming surface for stream encoders. Key fields include `AFMT_AUDIO_CHANNEL_ENABLE`, `AFMT_AUDIO_LAYOUT_SELECT`, `AFMT_DP_AUDIO_STREAM_ID`, `AFMT_HBR_ENABLE_OVRD`, `AFMT_60958_OSF_OVRD`, `AFMT_AUDIO_INFO_*`, IEC 60958 channel-status masks across `AFMT_60958_0/1/2`, and send/update bits such as `AFMT_AUDIO_SAMPLE_SEND`, `AFMT_60958_CS_UPDATE`, and `AFMT_AUDIO_INFO_UPDATE`. AFMT status and ack fields expose audio enable, HBR enable, FIFO overflow, and audio-enable-change handling. `AFMT_MEM_PWR_*` fields describe formatter memory power force/disable/state controls.

The DME groups are compact but stateful. `DME*_DME_CONTROL` selects the `METADATA_HUBP_REQUESTOR_ID`, enables metadata transmission, selects metadata stream type, reports and clears double-buffer/taken state, can disable DB behavior, and reports/clears missed metadata transmission. `DME*_DME_MEMORY_CONTROL` provides memory power force, disable, state, and default low-power-state fields.

The VPG groups define generic and standardized packet payload access. `VPG*_VPG_GENERIC_PACKET_ACCESS_CTRL` selects an indexed data word and `VPG*_VPG_GENERIC_PACKET_DATA` packs four payload bytes. `VPG*_VPG_GSP_FRAME_UPDATE_CTRL` and `VPG*_VPG_GSP_IMMEDIATE_UPDATE_CTRL` provide update and pending bits for generic packet slots 0 through 14. `VPG*_VPG_GENERIC_STATUS` provides lock and conflict detection/clear fields. `VPG*_VPG_ISRC1_2_*` and `VPG*_VPG_MPEG_INFO*` define ISRC and MPEG infoframe byte packing and update fields.

The DP AUX groups describe the low-level AUX engine. `DP_AUX*_AUX_CONTROL` carries enable/reset/reset-done, link-service read/update controls, HPD disconnect handling, mode detection, HPD selection, impedance calibration request enable, test mode, deglitch, and spare bits. `AUX_SW_CONTROL` launches software transactions and programs start delay and write-byte count. `AUX_ARB_CONTROL` coordinates ownership between software and DMCU/firmware users. `AUX_INTERRUPT_CONTROL` exposes software done, link-service done, GTC sync lock, and GTC sync error interrupt/status/ack/mask fields.

The AUX status and data fields are transaction-critical. `AUX_SW_STATUS`, `AUX_LS_STATUS`, `AUX_SW_DATA`, and `AUX_LS_DATA` describe done/request status, timeout state, HPD disconnect, partial-byte and invalid-start/stop/sync conditions, reply byte count, NACK state, and 8-bit data bytes. DPHY controls define TX half-symbol timing, precharge, timeout, input hysteresis, RX threshold/filter/phase-detect behavior, and TX/RX state readback. GTC sync fields define enable, impedance calibration, lock acquisition/maintenance periods, retry/error thresholds, controller state, error acks, detailed RX error status, reply byte count, and master-request state. `AUX_PHY_WAKE_CNTL` exposes wake go/pending/priority/ack handshaking.

## Control Flow

The header itself has no local control flow. Runtime behavior comes from consumers that include both `dcn_3_6_0_offset.h` and this shift/mask header, expand register-list macros, then use register helper operations such as `REG_READ`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and related wrappers to access MMIO fields.

A typical DCN 3.6 path is:

1. DCN36 resource, IRQ, DMUB, AFMT, VPG, AUX, and stream-encoder code includes or indirectly consumes the DCN 3.6 generated offset and mask headers.
2. Resource construction macros such as `SRI`, `SRI_ARR`, and `SRI_ARR_INIT` paste logical register names onto generated instance names like `regAFMT2_AFMT_AUDIO_PACKET_CONTROL2`, `regVPG3_VPG_MEM_PWR`, or `regDP_AUX1_AUX_CONTROL`.
3. Field-list macros paste logical fields onto generated `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` constants.
4. Higher-level display code sequences the actual programming: audio infoframe/channel-status updates in AFMT, metadata/generic packet writes in DME/VPG, AUX transactions for DPCD/I2C-over-AUX, hotplug/HPD handling, link training, and low-power transitions.

Visible integration in this tree includes `dcn36_resource.c`, which includes this header and uses DCN36 resource macros to build VPG, AFMT, and AUX register tables; `dmub_dcn36.c`, which initializes DMUB-visible register masks/shifts via `FD_MASK` and `FD_SHIFT`; and `irq_service_dcn36.c`, which includes the generated headers while building DCN36 interrupt metadata.

## State And Persistence Behavior

This file stores no runtime state and persists nothing by itself. It describes fields in hardware registers whose state is owned by live display hardware and driver programming.

State represented by this chunk includes:

- AFMT audio state: audio channel enable/layout, DP stream ID, HBR override, audio infoframe bytes, IEC 60958 channel-status fields, sample-send/update controls, CRC/test-ramp configuration, status/ack bits, and AFMT memory power.
- DME metadata state: metadata engine enable, selected HUBP requester, stream type, DB pending/taken/clear/disable state, missed-transmission status, and memory power.
- VPG packet state: indexed generic packet payload bytes, frame/immediate update pending state for generic packet slots, lock/conflict status, memory power, ISRC payload bytes, and MPEG infoframe payload/update bits.
- AUX state: AUX enable/reset, transaction launch and arbitration ownership, interrupt masks and acks, SW/LS status and data windows, DPHY timing/filtering/status, GTC sync lock/error state, and PHY wake state.

Some fields are status-only or status-like readbacks, including reset done, pending bits, memory-power state, audio FIFO overflow, audio enable changes, generic conflict status, AUX done/request/error/status fields, reply byte counts, TX/RX state, GTC controller state, and PHY wake pending/ack. Other fields are write controls that can change active hardware immediately or at a synchronized update point. Indexed data registers are especially stateful because a selected index controls which payload word a later write reads or updates.

Bad programmed values can persist until a pipe is reprogrammed, an encoder/AUX block is reset, display power is cycled, suspend/resume restores state, or the GPU is reset. The generated header has no restore, locking, or validation logic; those responsibilities live in display resource, stream encoder, AFMT/VPG, AUX, DMUB, and IRQ code.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h`, which provides matching register offsets and base indices. These masks and shifts are only correct when paired with the DCN 3.6.0 offset header and the DCN36 register-instance layout.

Important integration points include:

- `display/dc/resource/dcn36/dcn36_resource.c`: includes this header, defines base/offset/field expansion macros, builds VPG and AFMT register tables through `VPG_DCN31_REG_LIST_RI(id)` and `AFMT_DCN31_REG_LIST_RI(id)`, builds AUX register tables through `DCN2_AUX_REG_LIST_RI(id)`, initializes `AUX_RESET_MASK` from `DP_AUX0_AUX_CONTROL__AUX_RESET_MASK`, and documents mapping of VPG/AFMT/DME register blocks to DIO instances.
- `display/dc/dcn31/dcn31_afmt.h` and AFMT implementation files: define the AFMT register and field lists consumed by DCN36 resource construction, including audio source, channel enable, 60958 channel status, sample send, and memory-power fields present in this chunk.
- `display/dc/dcn31/dcn31_vpg.h` and VPG implementation files: define VPG register/field lists for generic packet access, update controls, conflict handling, and VPG memory power that are backed by the VPG0-VPG4 masks in this chunk.
- `display/dc/dce/dce_aux.h` and AUX helpers: use the AUX register table and field masks for DP AUX and I2C-over-AUX transactions, timeouts, interrupt/status handling, and engine reset/wake behavior.
- `display/dmub/src/dmub_dcn36.c`: initializes DMUB register offsets, masks, and shifts using `FD_MASK` and `FD_SHIFT`, relying on this header for fields shared with firmware-facing services.
- `display/dc/irq/dcn36/irq_service_dcn36.c`: includes the same generated headers for DCN36 interrupt metadata and source mapping.

The namespace is generated and cross-generation-looking but not interchangeable. Nearby DCN 3.5.x and DCN 4.x headers may share many field names while differing in offset layout, block count, or exact bit geometry. Consumers must bind the right offset and shift/mask pair for the target ASIC.

## Risks And Edge Cases

The largest risk is silent hardware misprogramming. A wrong `*_SHIFT` or `*_MASK` still compiles, but it can update the wrong bits, leave stale bits behind, corrupt adjacent fields, or decode status incorrectly.

Chunk boundaries matter. The first lines are only the tail of `AFMT1_AFMT_AUDIO_CRC_CONTROL`, so this chunk alone cannot fully describe AFMT1. The final lines stop in `DP_AUX2_AUX_ARB_CONTROL`, so the remainder of DP AUX2 belongs to the following chunk. The merge lane must combine adjacent chunks before making whole-file or whole-block conclusions.

Instance mapping is critical. The same logical AFMT, DME, VPG, and AUX register layout repeats across instances. A mask from AFMT4 or DP_AUX1 is often bit-identical to AFMT2 or DP_AUX0, but it must still be paired with the correct generated offset and DIO/HPO mapping. Wrong instance selection can route audio, metadata, packet, or AUX operations to the wrong display link.

AFMT fields are visible to end users through audio behavior. Incorrect channel enable/layout, DP stream ID, HBR override, 60958 fields, infoframe update bits, or sample-send controls can cause missing audio, wrong channel mapping, bad sample-rate/word-length reporting, HDMI/DP sink compatibility problems, or stale audio infoframes.

DME/VPG fields affect secondary-data packet delivery. Incorrect indexed writes, update timing, conflict clear, pending-bit interpretation, ISRC/MPEG payload packing, or memory-power controls can cause missing or stale infoframes, HDR/metadata regressions in adjacent packet paths, packet conflicts, or display behavior that only fails on specific stream encoders.

AUX fields are high impact. Wrong control, arbitration, timeout, HPD-disconnect, interrupt, data, DPHY timing, or GTC sync masks can break EDID reads, DPCD access, link training, MST sideband messaging, LTTPR handling, PSR/replay interactions, firmware-mediated AUX access, or hotplug recovery. AUX errors may surface as timeouts or invalid replies rather than obvious bitfield bugs.

Power and reset fields are sensitive. AFMT/VPG/DME memory power, AUX reset, AUX PHY wake, and low-level DPHY controls interact with active display links. Bad sequencing can leave blocks inaccessible, force memories off while active, make reset-done polling fail, or create intermittent failures across suspend/resume and runtime power transitions.

## Test Signals

Useful validation is mostly generated-header, build, and hardware-behavior oriented:

- Compile coverage for DCN36 resource construction, AFMT/VPG stream encoder objects, AUX/I2C helpers, DMUB register initialization, and IRQ service code that includes the DCN 3.6 offset and shift/mask headers.
- Generated-register consistency checks that every `*_MASK` has a matching `*_SHIFT`, field masks match the hardware register database, and every register referenced by DCN36 resource lists exists in `dcn_3_6_0_offset.h`.
- Cross-generation diffs against AMD's authoritative DCN 3.6.0 register database and nearby DCN 3.5.x / DCN 4.x headers, with expected differences explicitly reviewed.
- AFMT tests for HDMI/DP audio bring-up, channel layouts, HBR audio, IEC 60958 channel status, sample-rate/word-length reporting, audio infoframe updates, FIFO-overflow status/ack behavior, CRC/test paths, and suspend/resume restore.
- VPG/DME packet tests for generic packet payload writes, frame-synchronized and immediate updates, pending-bit clearing, conflict reporting/clear, ISRC and MPEG infoframe payloads, metadata DB pending/taken transitions, missed-transmission reporting, and memory-power transitions.
- AUX tests for EDID and DPCD reads/writes, I2C-over-AUX, link training, HPD disconnect during transactions, timeout paths, invalid reply/status decoding, interrupt/ack/mask behavior, firmware/DMUB-mediated AUX operations, MST sideband traffic, LTTPR accesses, and AUX wake behavior.
- Power-management tests for AFMT/VPG/DME memory power, AUX reset/reset-done polling, AUX PHY wake, runtime display idle, hotplug, suspend/resume, and GPU reset recovery.

Regression symptoms from bad constants include missing or misreported display audio, stale or absent infoframes/metadata packets, generic-packet conflicts, broken EDID/DPCD access, DP link-training failures, MST failures, HPD/AUX timeout storms, stuck reset or wake bits, incorrect interrupt acks, and failures isolated to DCN 3.6 ASICs or specific DIO instances.

## Cross-Chunk Notes

This is not a standalone source module. It is a generated register-layout slice inside `dcn_3_6_0_sh_mask.h`. The preceding chunk owns earlier AFMT1 fields before line 39779. The following chunk owns the rest of DP AUX2 after line 42166. The merge/reconciliation lane should treat this document as the AFMT1-tail/AFMT2-4, DME0-4, VPG0-4, DP_AUX0-1, and DP_AUX2-beginning portion of the full DCN 3.6.0 shift/mask contract.

### subset-b-002135: lines 42167-44553

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 42167-44553

## Purpose

This chunk is a generated shift/mask register-field slice for AMD DCN 3.6.0 display hardware. It contains no executable C functions or declared C types; its interface is a set of `#define` constants named as `<register>__<field>__SHIFT` and `<register>__<field>_MASK`. Consumers combine these constants with `dcn_3_6_0_offset.h` and AMDGPU Display Core register helpers such as `FD_MASK`, `FD_SHIFT`, `REG_SET`, `REG_UPDATE`, and register-list macros.

The covered lines span the tail of the DisplayPort AUX2 block, complete AUX3 and AUX4 blocks, DPIA mux controls, the DOUT I2C/DDC engine, DIO miscellaneous power/clock/link-routing controls, DIG stream mapper controls, a DC perfmon instance, DCIO/UNIPHY routing and reset controls, and GPIO/DDC pad mask/value/enable/readback definitions through the start of GENLK GPIO fields.

## Important APIs and register groups

- `DP_AUX2_*`, `DP_AUX3_*`, and `DP_AUX4_*` define AUX channel register fields for software AUX transactions, link-service reads, arbitration between SW and DMCU/firmware users, interrupt status/ack/mask bits, data FIFO/index access, DPHY TX/RX timing/status, GTC sync control/error/status, and AUX PHY wake handshakes. AUX2 begins mid-block at `AUX_ARB_CONTROL` masks and continues through PHY wake; AUX3 and AUX4 are complete in this chunk.
- `DP_AUX*_AUX_CONTROL` fields enable/reset the AUX block, select HPD, allow link-service reads, control HPD-disconnect behavior, enable mode detection, request impedance calibration, and enable deglitch/test behavior.
- `DP_AUX*_AUX_SW_STATUS`, `AUX_LS_STATUS`, and `AUX_GTC_SYNC_STATUS` are dense status bitmaps for done/request state, receive timeout and overflow, HPD disconnect, partial/invalid byte framing, invalid start/stop/sync/receptacle conditions, reply byte count, NACK, CP IRQ, update ack, and GTC master request by RX.
- `DIO_DPIA_MUX0_DIO_DPIA_MUX_CONTROL` through `DIO_DPIA_MUX3_DIO_DPIA_MUX_CONTROL` expose enable/reset and `DIG_DP_SOURCE_SELECT` fields for routing USB4/DisplayPort-in-Alt-mode input adapter streams to DIG DP sources.
- `DC_I2C_*` defines the DOUT I2C engine: transaction launch/reset/DDC select/count, arbitration and abort controls, software and per-DDC hardware interrupt bits, SW status/NACK/timeout/overflow fields, DDC1-DDC5 hardware EDID detect status, per-DDC speed/setup timing fields, transaction descriptor fields, data read/write/index fields, EDID detect control, and read-request interrupt status/ack/mask fields.
- `DIO_DCN_STATUS`, `DIO_SCRATCH0` through `DIO_SCRATCH7`, `DIO_DP_ALPM_WAKEUP_INTERRUPT_STATUS`, `DIO_MEM_PWR_STATUS`, `DIO_MEM_PWR_CTRL`, and `DIO_MEM_PWR_CTRL2` cover DIO status/scratch state, DP ALPM wake interrupts, and light-sleep status/force/disable controls for I2C and DPA-DPG memory slices.
- `DIO_CLK_CNTL`, `DIO_POWER_MANAGEMENT_CNTL`, `DIO_HDMI_RXSTATUS_TIMER_CONTROL`, `DIO_PSP_INTERRUPT_STATUS`, `DIO_PSP_INTERRUPT_CLEAR`, and `DIO_STATUS` provide clock-gating overrides, DIO power-management reset/busy status, HDMI RX status timer control, PSP interrupt message/status/clear bits, and top-level DIO enable readback.
- `DIO_LINKA_CNTL` through `DIO_LINKF_CNTL` select encoder type and HPO HDMI/DP encoder mapping for each DIO link. `DIG0_STREAM_MAPPER_CONTROL` through `DIG4_STREAM_MAPPER_CONTROL` select the link target for each DIG stream.
- `DC_PERFMON18_*` defines one display perfmon block: event selection, counted-value selection, increment/run/interrupt modes, counter state selection for counters 0-7, perfmon run-control and count-off interrupt controls, current value high/low readback, and per-counter interrupt status/ack fields.
- `DC_GENERICA`, `DC_GENERICB`, `DCIO_CLOCK_CNTL`, `DC_REF_CLK_CNTL`, `UNIPHYA/B/C_LINK_CNTL`, `UNIPHYA/B/C/D/E_CHANNEL_XBAR_CNTL`, `DCIO_WRCMD_DELAY`, `DC_PINSTRAPS`, `DCIO_SPARE`, `INTERCEPT_STATE`, `DCIO_PATTERN_GEN_*`, `DCIO_GSL_*_PAD_CNTL`, and `DCIO_SOFT_RESET` cover generic DCIO muxing, reference clock output selection, UNIPHY lane polarity and channel crossbar routing, write-command delay, pinstrap readback, spare bits, pattern-generation control, genlock/swaplock pad control, and soft resets for individual UNIPHY/DPCS/DPIA/DIO components.
- `DC_GPIO_GENERIC_*` and `DC_GPIO_DDC1_*` through `DC_GPIO_DDCVGA_*` define GPIO mask, output value (`_A`), output enable (`_EN`), and input/readback (`_Y`) fields. DDC mask fields include clock/data masks, pull-down enables, receive enables, AUX pad mode, AUX polarity, hardware pull-down permission, and drive-strength fields.

## Control flow and usage model

There is no local control flow. These generated constants are compile-time data for ASIC-specific register tables:

1. DCN 3.6 code includes `dcn_3_6_0_offset.h` for register addresses and this header for field layout.
2. Register-list macros such as `SR`, `SRI`, `SF`, `HWS_SF`, `DMUB_SF`, AUX/I2C engine macros, IRQ-entry macros, and GPIO translation code populate register, mask, and shift structs.
3. Runtime code uses those structs through register helpers to program MMIO fields without spelling the bit positions in handwritten code.

Direct DCN 3.6 users include `display/dmub/src/dmub_dcn36.c`, which initializes DMUB register offsets/masks/shifts from this header; `display/dc/resource/dcn36/dcn36_resource.c`, which builds AUX, I2C, DIO, HWSEQ, and resource register tables; and `display/dc/irq/dcn36/irq_service_dcn36.c`, which creates HPD, HPD RX, I2C, DP sink, GPIO pad, underflow, vupdate/vblank/vline, and DMUB outbox interrupt source entries using generated fields.

## State and persistence behavior

The header itself has no mutable state. The state lives in DCN 3.6 MMIO registers and persists according to display hardware lifecycle: boot-time resource construction, link bring-up, modeset, AUX/DDC transactions, runtime power management, suspend/resume, GPU reset, and display IP reset.

Several hardware groups in this chunk are explicitly stateful:

- AUX software and link-service transactions maintain request/done bits, FIFO indices, reply byte counts, DPHY timing/status, arbitration ownership, interrupt ack/mask state, GTC sync lock/error state, and PHY wake handshakes.
- I2C/DDC state includes transaction descriptors, data indices, selected DDC line, SW and hardware transfer status, EDID detect status/state/valid tries, per-DDC timing/prescale/setup values, aborts, reset bits, and read-request interrupt latches.
- DIO memory, clock, and power fields persist low-power policy and clock-gating overrides. These values are touched by HWSEQ/DIO resource code and can affect whether I2C, DP, and link memories enter light sleep.
- DIO link and stream-mapper fields determine which encoder/link path is active for a given stream, including HPO DP/HDMI selections and DIG-to-link targets.
- DCIO/UNIPHY fields persist lane inversion, lane crossbar sources, DOUT PHY channel enables, soft-reset bits, pattern generation, genlock/swaplock pad selection, and pinstrap/spare state.
- GPIO/DDC fields persist pad mode, drive strength, pull-down, output enable, output value, and readback routing for DDC and generic GPIO pins. These are shared with DDC/AUX discovery paths and GPIO translation helpers.

## Dependencies and integration points

- Requires the matching `dcn_3_6_0_offset.h`. The mask/shift symbols are only correct when paired with the same generated offset file and base-index definitions.
- Depends on the AMD Display Core register helper layer to interpret field names through `FD_MASK`/`FD_SHIFT` and read-modify-write helpers. Misspelled or stale fields generally fail at compile time; stale masks paired with valid but wrong offsets can compile and misprogram hardware.
- Integrates with DCN 3.6 resource construction in `dcn36_resource.c`: `aux_engine_regs_init(1..4)` maps AUX engines for raw AUX and DMUB AUX transfers, `i2c_inst_regs_init(1..5)` maps DDC/I2C engines, `DIO_MASK_SH_LIST` includes `DIO_MEM_PWR_CTRL__I2C_LIGHT_SLEEP_FORCE`, and `dcn36_get_preferred_eng_id_dpia()` ties DPIA routing policy to DIG encoder choices.
- Integrates with `dce_aux.c` transaction flow: acquire the AUX engine, submit the request, poll status, read reply bytes, and release the engine. The AUX status, data, interrupt, arbitration, and timeout fields in this chunk are the hardware-side representation of that flow.
- Integrates with DC I2C/DDC and link detection through the DDC service and I2C hardware engine. The `DC_I2C_*` fields encode transaction count/type/stop/start, data bytes, NACK status, timeout, and EDID detection used by monitor detection and EDID reads.
- Integrates with GPIO translation code such as `gpio/dcn32/hw_translate_dcn32.c`, where DDC line offsets (`DC_GPIO_DDC1_A` through `DC_GPIO_DDCVGA_A`) and `*_CLK_A`/`*_DATA_A` masks map logical GPIO IDs to hardware pins.
- Integrates with DIO link encoder, stream encoder, HPO encoder, and link management code through UNIPHY transmitters, DIG stream targets, `DIO_LINK*` encoder selection fields, and `DIO_DPIA_MUX*` controls.
- Integrates with DCN 3.6 IRQ service through I2C done bits, HPD/HPD RX paths, DP sink interrupts, GPIO pad interrupts, and display timing interrupts. This chunk includes I2C interrupt bit layouts and AUX interrupt controls relevant to those sources.
- Integrates with diagnostics/performance tooling through `DC_PERFMON18_*`, which exposes event selection, counter state, current-value readback, and interrupt/ack state.

## Risks and edge cases

- Generated-header drift is the primary risk. `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h` must be regenerated and consumed as a pair; otherwise valid-looking constants can target wrong registers or fields.
- AUX2 starts mid-block in this chunk and GENLK GPIO ends mid-block at the chunk boundary. Whole-file analysis must reconcile adjacent chunks before making complete claims about those blocks.
- AUX and I2C fields mix controls, latched status, interrupt acks, masks, and readback-only fields. Treating status/ack fields as ordinary controls can clear diagnostics, drop interrupts, or leave transfer state inconsistent.
- Arbitration fields are shared between SW and firmware/DMCU users. Incorrect sequencing around `*_USE_*_REG_REQ`, pending aliases, and `*_DONE_USING_*` can deadlock or race AUX/I2C ownership.
- FIFO/index fields such as AUX data indices and I2C data indices are narrow and often auto-incremented. Incorrect index, byte count, or autoincrement behavior can corrupt transaction payloads or read stale reply bytes.
- Per-instance repetition is easy to misuse: AUX2/3/4, DDC1-DDC5, DIO_LINKA-F, DPIA_MUX0-3, DIG0-4, UNIPHY A-E, and DDC GPIO lines have similar field layouts but different hardware instances.
- Power/clock fields can cause hangs or power regressions if altered outside expected display sequencing. DIO light-sleep force/disable, memory power force bits, DIO clock-gating disables, and soft resets are especially sensitive.
- Link-routing fields can silently miswire display output paths. Wrong `DIG_DP_SOURCE_SELECT`, `DIG_STREAM_LINK_TARGET`, `ENC_TYPE_SEL`, HPO encoder selection, UNIPHY xbar source, or lane inversion can look like AUX failures, link training failures, no display, or lane polarity issues.
- DDC GPIO mask and pad-mode fields share physical pins with AUX/DDC behavior. Incorrect AUX pad mode, polarity, drive strength, pull-down, or output enable can break EDID reads or hotplug behavior.
- Perfmon fields expose state and interrupt bits for one counter instance. Incorrect event selection or ack handling can make performance/debug data misleading or generate unexpected interrupts.

## Test signals

- Build DCN 3.6 display code with this header and its matching offset header included by `dmub_dcn36.c`, `dcn36_resource.c`, and `irq_service_dcn36.c`.
- Static checks should compare repeated field layouts across AUX3/AUX4, DDC1-DDC5 speed/setup/status, DIO link A-F, DIG0-4 stream mapper, and DDC GPIO1-5/VGA groups where hardware intends identical structure.
- AUX validation should cover native DP AUX reads/writes, I2C-over-AUX, defer/retry paths, timeout handling, HPD-disconnect handling, invalid reply paths, GTC sync status/error reporting, and DMUB-routed AUX transfers.
- I2C/DDC validation should cover EDID reads on DDC1-DDC5 and VGA, SW and hardware done interrupts, NACK reporting, timeout/abort/reset paths, transaction descriptors 0-3, data FIFO indexing, and EDID detect state.
- Link bring-up tests should cover DPIA mux paths 0-3, preferred DIG encoder choices for DPIA, DIO link A-F encoder selection, DIG stream mapper targets, HPO DP/HDMI paths, and UNIPHY lane crossbar/inversion behavior.
- Power-management tests should exercise DIO memory light sleep, DP ALPM wake interrupts, clock gating overrides, HDMI RX status timer behavior, suspend/resume, display idle, and GPU/display reset paths.
- GPIO tests should verify DDC clock/data output/readback/enable mapping, AUX pad mode/polarity, drive strength, pull-down behavior, generic GPIO mapping, and hotplug/DDC behavior on all exposed physical DDC lines.
- Diagnostics should include register dumps for `DP_AUX*_AUX_SW_STATUS`, `DP_AUX*_AUX_INTERRUPT_CONTROL`, `DC_I2C_SW_STATUS`, `DC_I2C_DDC*_HW_STATUS`, `DIO_MEM_PWR_STATUS`, `DIO_LINK*_CNTL`, `DIG*_STREAM_MAPPER_CONTROL`, `UNIPHY*_CHANNEL_XBAR_CNTL`, and `DC_GPIO_DDC*_MASK` when investigating link training, EDID, AUX, power, or routing failures.

### subset-b-002136: lines 44554-47050

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 44554-47050

## Purpose

This chunk is generated AMD DCN 3.6 register field metadata. It contains no executable C logic; it publishes preprocessor constants for bit positions and bit masks inside DCN 3.6 MMIO registers. Runtime display code includes this file with the matching `dcn_3_6_0_offset.h` register-offset header, then uses helper macros to populate typed register/shift/mask tables for GPIO, DDC/AUX, panel power sequencing, DSC, IRQ, and DMUB register access.

The requested range covers the tail of `DC_GPIO_GENLK_MASK`, complete DC GPIO/HPD/AUX/DDC pad-control families, complete reserved UNIPHY macro-control fields for UNIPHY instances 1 through 4, complete `PWRSEQ0` and `PWRSEQ1` panel/backlight power-sequencer fields, complete DSC instance 0 DSCC/DSCCIF/top/perfmon fields, and the beginning of DSC instance 1 DSCC PPS range fields. It contains 2,094 `#define` lines, evenly paired as 1,047 `__SHIFT` macros and 1,047 `_MASK` macros.

Although this path is under a local `ceph-client` source mirror, the content is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocation paths, or direct I/O calls in this range. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the least significant bit position for a field inside a 32-bit register.
- `<REGISTER>__<FIELD>_MASK`: the unshifted register-bit mask for the same field.

Major macro families in this chunk:

- `DC_GPIO_GENLK_*`, `DC_GPIO_HPD_*`, `DC_GPIO_DRIVE_STRENGTH_S0/S1`, `DC_GPIO_DRIVE_TXIMPSEL`, `DC_GPIO_RXEN`, and `DC_GPIO_PULLUPEN`: GPIO field masks for genlock clock/vsync, swaplock lines, HPD pins 1-6, generic GPIO drive strength, transmit impedance selection, receive enables, and pull-up enables.
- `PHY_AUX_CNTL` and `DC_GPIO_AUX_CTRL_0` through `DC_GPIO_AUX_CTRL_5`: AUX/DDC electrical controls, including AUX pad wake and receive selection, fall slew selection, spike filter controls, comparator and bias selection, termination, DP/DN swap, hysteresis tuning, AUX control nibbles, voltage output tuning, DDC pad I2C mode, 1.2 V I2C rail enables, and DDC pad I2C control.
- `AUXI2C_PAD_ALL_PWR_OK`: per-PHY AUX/I2C pad power-good status bits for PHY1 through PHY6.
- `DCIO_UNIPHY{1,2,3,4}_UNIPHY_MACRO_CNTL_RESERVED0` through `...RESERVED57`: full-width reserved fields for the repeated UNIPHY macro-control register space. Each register is represented as one `UNIPHY_MACRO_CNTL_RESERVED` field with shift `0x0` and mask `0xFFFFFFFFL`.
- `PWRSEQ0_*` and `PWRSEQ1_*`: GPIO routing and pad control for `VARY_BL`, `DIGON`, and `BLON`, plus panel power-sequence enable/target/state/status, power-up and power-down delays, reference dividers, backlight PWM control, PWM period, double-buffer/register lock behavior, and spare fields.
- `DSCC0_*`: DSC compressor-client configuration, status, interrupt/status enable fields, DSC PPS programming registers 0-22, memory power control, squared-error counters, max absolute error counters, rate-buffer fullness counters, rate-control buffer fullness counters, and debug bus rotation fields.
- `DSCCIF0_*` and `DSC_TOP0_*`: DSC client-interface input format/dimensions/underflow status and top-level DSC clock/debug gating fields.
- `DC_PERFMON19_*`: DSC-local perf counter control, counter state, perfmon control, interrupt threshold control/status, and counter value registers.
- `DSCC1_*`: the beginning of the second DSC compressor-client field set, from config/status/interrupts through `DSCC1_DSCC_PPS_CONFIG21`; this chunk ends mid-register at `DSCC1_DSCC_PPS_CONFIG21__RANGE_MIN_QP11_MASK`.

## Control Flow

This header has no runtime control flow. Its constants participate in generated register-table setup:

1. DCN 3.6 resource, IRQ, and DMUB code includes `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h`.
2. Register-list macros paste register and field names into symbols such as `DSCC0_DSCC_PPS_CONFIG0__DSC_VERSION_MINOR__SHIFT`, `DC_GPIO_AUX_CTRL_5__DDC_PAD1_I2CMODE_MASK`, or `PWRSEQ1_PANEL_PWRSEQ_CNTL__PANEL_BLON_MASK`.
3. Helper macros such as `FD_MASK`, `FD_SHIFT`, `DSC_REG_LIST_SH_MASK_DCN35`, `REG_FIELD_LIST`, and GPIO/DDC `*_MASK_SH_LIST_*` macros copy these compile-time constants into runtime register descriptors.
4. Driver code later uses those descriptors with register read/modify/write helpers to program AUX/DDC pads, HPD handling, panel power rails, backlight PWM, DSC PPS state, DSC memory power, DSC interrupts/status, and perf counters.

The macros do not encode ordering. Callers must still sequence pad power, AUX/DDC setup, HPD acknowledgment, panel power delays, PWM lock/update behavior, DSC clocking, PPS double-buffering, memory power, interrupt clear/enable, and suspend/resume restore paths correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It describes fields in MMIO-backed hardware state.

Hardware state represented by the GPIO/AUX portion includes HPD mask/data/enable pins, genlock and swaplock GPIO pins, pad drive and impedance controls, receiver and pull-up enables, AUX electrical tuning, DDC I2C pad mode, DDC 1.2 V rail enables, and AUX/I2C PHY power-good status. These values affect connector detection, EDID/DDC transactions, DisplayPort AUX access, and external sync/swaplock signaling.

Hardware state represented by the power-sequencer portion includes panel power target state, actual panel power-sequence state bits, panel sync/digital/backlight output polarity and overrides, configurable power-up/power-down delays, reference time bases, backlight PWM duty and period, frame-start-synchronized PWM update behavior, and register lock/update-pending/readback behavior. These fields are persisted by hardware only while the relevant display block remains powered and not reset.

Hardware state represented by the DSC portion includes DSC slice and PPS configuration, rate-control buffer model values, quantization and BPG ranges, memory low-power controls, error/statistic counters, rate-buffer fullness counters, top-level DSC clock/debug controls, underflow status, and perfmon counters. Status and interrupt fields may be sticky, read-only, write-one-to-clear, self-clearing, or double-buffered depending on the hardware register; this generated header does not distinguish those access semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.6 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h` for the corresponding register addresses and base indices.
- Shared display register helpers such as `reg_helper.h`, `dmub_reg.h`, GPIO register-list macros, and DSC register-list macros that token-paste register and field names into these constants.

Concrete include sites and consumers visible in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c` includes this header and initializes DSC shift/mask tables with `DSC_REG_LIST_SH_MASK_DCN35(__SHIFT)` and `DSC_REG_LIST_SH_MASK_DCN35(_MASK)`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c` includes this header and fills DMUB DCN register masks/shifts through `DMUB_DCN35_FIELDS()`, `FD_MASK`, and `FD_SHIFT`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c` includes the same offset/mask pair for DCN 3.6 IRQ register programming and HPD source handling.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/ddc_regs.h` consumes `PHY_AUX_CNTL` and `DC_GPIO_AUX_CTRL_5` field masks in `DDC_MASK_SH_LIST_DCN2`, especially `AUXn_PAD_RXSEL` and `DDC_PADn_I2CMODE`.
- DSC code shared with DCN 2.x/3.x consumes the `DSCC0_*` and `DSCC1_*` PPS/config/status masks when constructing `struct dcn20_dsc_registers`, shift tables, and mask tables.

The final per-file research should merge adjacent chunks before making complete claims about all DCN 3.6 GPIO, UNIPHY, PWRSEQ, DSC, or perfmon field coverage, because this range starts inside `DC_GPIO_GENLK_MASK` and ends inside `DSCC1_DSCC_PPS_CONFIG21`.

## Risks And Edge Cases

- Generated mask/shift drift is the main risk. These constants are untyped and compile cleanly even when a mask points at the wrong bit; failures surface as incorrect hardware programming.
- Shift/mask pairing must remain exact. Every visible field in this chunk has both a `__SHIFT` and `_MASK` macro; losing one half breaks token-pasted initialization paths or silently corrupts field encode/decode.
- HPD/AUX/DDC fields are connector-sensitive. Wrong pad mode, receive select, pull-up, power-good, or I2C-control masks can cause hotplug storms, missing displays, AUX timeouts, EDID read failures, or failures limited to one connector index.
- PWRSEQ fields are sequencing-sensitive. Incorrect panel delay, target-state, override, polarity, or PWM lock masks can cause blank internal panels, backlight flicker, unsafe rail timing, stuck update-pending bits, or resume regressions.
- DSC PPS fields are format-sensitive. Wrong BPP, slice geometry, native 4:2:0/4:2:2, rate-control, range QP, BPG offset, or memory-power masks can produce compressed-stream corruption, link bandwidth failures, or errors only at high pixel clocks.
- Status/interrupt fields require correct access semantics. This header names occurrence and enable bits but does not document read-only, sticky, W1C, or self-clearing behavior; callers must get that from hardware specs and established driver code.
- Reserved UNIPHY fields are full-width and repeated across many registers. Treating them as ordinary safe programming fields outside vendor-guided flows can alter undocumented PHY behavior.
- The chunk boundary is artificial. The first register block is incomplete from earlier lines, and the last `DSCC1` PPS block continues in the next chunk.

## Test Signals

Useful validation combines generated-header consistency checks with hardware behavior:

- Build AMDGPU/DC with DCN 3.6 support enabled; macro rename or deletion should fail in `dcn36_resource.c`, `dmub_dcn36.c`, IRQ service code, GPIO/DDC helpers, and DSC register-table initialization.
- Mechanically verify this range still contains paired `__SHIFT` and `_MASK` macros for each field and that the count remains balanced for generated DCN 3.6 metadata.
- Diff the chunk against AMD's authoritative DCN 3.6 register database and neighboring generated headers where equivalent DPCS/DCN blocks are expected to remain stable.
- Exercise connector paths that use HPD1-HPD6, DDC1-DDC6, AUX1-AUX6, and GPIO genlock/swaplock pins: hotplug, unplug, EDID reads, DP AUX DPCD reads/writes, suspend/resume, and low-power wake.
- Validate panel power and backlight behavior on embedded panels using PWRSEQ0/PWRSEQ1: power-up/power-down timing, digital/backlight enable polarity, PWM duty/period programming, frame-start synchronized updates, and resume restore.
- Enable DSC on capable displays and test modes that stress PPS programming: high resolution, high refresh, native 4:2:0/4:2:2 where supported, multi-slice modes, link-rate changes, and repeated modesets.
- Watch kernel logs and display diagnostics for HPD storms, AUX timeouts, EDID failures, stuck PWRSEQ or PWM update-pending status, underflow interrupts, DSC rate-buffer overflow/underflow, DSC end-of-frame errors, visual corruption, and resume failures.

## Cross-Chunk Notes

Earlier chunks own the beginning of `DC_GPIO_GENLK_MASK` and likely the broader DCIO/GPIO register field namespace before this line range. Later chunks continue `DSCC1_DSCC_PPS_CONFIG21` and the remaining DCN 3.6 mask namespace. The merge/reconciliation lane should combine this report with adjacent chunks before producing the final source-tree-aligned per-file research document for `dcn_3_6_0_sh_mask.h`.

### subset-b-002137: lines 47051-49491

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 47051-49491

## Purpose

This chunk is a generated AMD DCN 3.6.0 register shift/mask slice. It contains no executable logic; it exports C preprocessor constants that describe bit positions and masks for memory-mapped display-controller registers. Runtime DCN code combines these constants with the companion `dcn_3_6_0_offset.h` register offsets and the AMD display register-helper macros so field updates can be expressed by register and field name rather than hard-coded numeric bit layouts.

The requested range contains 1,070 `__SHIFT` macros and 1,078 `_MASK` macros, organized by 237 register-name comments and 21 address-block comments. The range starts in the tail of `DSCC1_DSCC_PPS_CONFIG22` after earlier DSC picture-parameter-set fields for DSC compressor instance 1, covers complete DSC compressor/interface/top/perfmon groups for DSC instances 2 and 3, then covers HPO top, HPO DP stream mapping, HPO perfmon, HPO HDMI link/FRL/stream encoder, AFMT audio packet, DME, VPG, and the beginning of HDMI TB encoder fields. It ends at `HDMI_TB_ENC_HC_ACTIVE_BLANK`, with later HDMI TB CRC/encryption/mode fields continuing after the chunk boundary.

Although this source path is under a local `ceph-client` mirror, this file is AMDGPU DCN display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, memory allocations, or direct I/O operations in this slice. Its only API surface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating, preserving, or clearing a field during register read/modify/write.

The main register families in this chunk are:

- `DSCC1_*`: tail of DSC compressor instance 1 PPS range fields for rate-control QP/BPG ranges, DSC memory-power control, squared-error/max-absolute-error counters, rate-buffer and rate-control-buffer fullness levels, and test debug bus rotation.
- `DSCCIF1_*` and `DSC_TOP1_*`: DSC1 input-interface underflow/status, input pixel format, picture dimensions, DSC clock enable/gating, and debug clock selection.
- `DC_PERFMON20_*`: DSC1-side performance counter controls, counted-value mode, state selection for counters 0-7, count-off interrupt control, per-counter interrupt status/ack bits, and low/high counter value reads.
- `DSCC2_*` and `DSCC3_*`: complete DSC compressor layouts for instances 2 and 3, including slice layout, ICH behavior, rate-control buffer model size, status, overflow/underflow interrupt enables/status, full PPS programming registers `PPS_CONFIG0` through `PPS_CONFIG22`, memory-power state, error statistics, fullness counters, and debug bus rotation.
- `DSCCIF2_*`, `DSCCIF3_*`, `DSC_TOP2_*`, and `DSC_TOP3_*`: repeated DSC input-interface, picture-size, clock, dynamic clock-gating, and debug-control fields for DSC instances 2 and 3.
- `DC_PERFMON21_*` and `DC_PERFMON22_*`: performance-monitor instances paired with DSC2 and DSC3, mirroring the `DC_PERFMON20` field model.
- `HPO_TOP_*`: HPO top-level clock-control and hardware-control fields for register clock gating, HDMI stream encoder power state, HDMI character/output-clock enables, test clock selection, and HPO DP stream output enables.
- `DP_STREAM_MAPPER_CONTROL0..3`: HPO DP stream-to-link target selection fields, mapping logical streams onto HPO DP link targets.
- `DC_PERFMON23_*`: HPO-level performance-monitor controls and counters, with the same counter/run/interrupt/read shape as the DSC perfmon groups.
- `HDMI_LINK_ENC_*`, `HDMI_FRL_ENC_*`, and `HDMI_STREAM_ENC_*`: HPO HDMI link encoder enable/clock state, HDMI FRL enable/metadata/meter-buffer/memory-power fields, stream encoder clock/control/mux fields, and clock-ramp-adjuster FIFO status/control.
- `AFMT5_*`: audio formatter packet control and data fields for ACP, VBI/audio packets, audio infoframes, IEC 60958 channel-status words, audio CRC, ramp generator, audio source selection, packet-status bits, and AFMT memory-power controls.
- `DME5_*`: DME enable/reset/ready/state and DME memory-power control.
- `VPG5_*`: generic packet access/data, frame and immediate update controls for generic packets 0-14, packet lock/conflict status, VPG memory power, ISRC data access, and MPEG infoframe byte/update fields.
- `HDMI_TB_ENC_*`: beginning of HDMI TB encoder control, pixel-format, packet-control, ACR, VBI, general-control, generic-packet scheduling/immediate-send, packet line/EMP placement, double-buffer control, ACR CTS/N programmed and status values, borrow/rate-buffer controls, metadata packet scheduling, and active/blank timing fields.

Many groups are generated per hardware instance. `DSCC2` and `DSCC3` repeat the same register-field layout, while `DC_PERFMON20` through `DC_PERFMON23` repeat the same performance-counter layout for different display blocks.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU display code that includes this generated header:

1. DCN 3.6 code includes `dcn_3_6_0_offset.h` and this shift/mask header.
2. Register-list macros token-paste register and field names into typed register, shift, and mask tables for DCN display blocks.
3. DCN 3.6 resource, DMUB, IRQ, HPO, HDMI, AFMT, VPG, DSC, and perfmon setup code wires those tables into block objects and hardware service helpers.
4. Runtime display paths call register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`; those helpers use these masks and shifts to touch only the intended MMIO bits.

The macros do not encode programming order. Consumers still need to sequence DSC PPS programming with stream enablement, program HPO stream mapping before link activation, coordinate HDMI link/FRL/stream clocks, load and schedule infoframes at valid lines, handle audio packet and ACR setup with audio state, acknowledge perfmon/status bits correctly, and respect power/clock gating rules.

## State And Persistence Behavior

This chunk stores no software state and persists nothing directly. It describes hardware-visible state in DCN 3.6 registers:

- DSC compressor state: PPS parameters, slice geometry, rate-control model parameters, QP ranges, buffer thresholds, BPG offsets, initial delays, memory-power controls, status, error counters, buffer fullness counters, and debug-bus rotation.
- DSC input-interface and top-level state: input pixel format, bits per component, picture dimensions, underflow recovery/status/interrupt enables, clock enable, static/dynamic clock-gating controls, and debug clock muxing.
- Performance-monitor state: event selection, counted-value type, hardware start/stop/count-off routing, active/counting state, per-counter interrupt state/acknowledge bits, and low/high counter values.
- HPO and DP stream state: top-level HPO clock/output enable controls and DP stream-to-link target mappings.
- HPO HDMI state: link encoder enable/clock controls, FRL encoding controls, stream encoder mux/clock/ramp-adjuster controls, DME control, TB encoder mode and timing fields, packet scheduling, audio clock regeneration, buffer prefill, and memory-power controls.
- Audio/infoframe metadata state: AFMT audio, VBI, ACP, audio infoframe, IEC 60958, CRC, ramp, and source-selection fields; VPG generic packet, ISRC, MPEG, immediate-update, frame-update, conflict/lock, and memory-power fields.

Persistence is hardware-defined. Configuration fields generally remain until a modeset, link reconfiguration, DSC/FRL enable transition, audio reprogramming, power-gating event, suspend/resume, GPU reset, or ASIC reset rewrites them. Status, interrupt, pending, CRC, counter, conflict, ready, and error fields may be read-only, sticky, write-one-to-clear, self-clearing, or valid only while the owning block's clocks are running. This generated header does not identify access semantics; consumers must rely on the register specification and block-specific driver code.

## Dependencies And Integration Points

This file must stay synchronized with AMD's generated DCN 3.6.0 register database and the matching offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h` supplies the companion MMIO register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c` includes this generated shift/mask header for DCN 3.6 DMUB register setup.
- DCN 3.6 resource and IRQ setup code uses the generated register namespace to build hardware register tables for display block construction and interrupt handling.
- Shared HPO DP stream encoder code consumes `DP_STREAM_MAPPER_CONTROL0..3` fields to select HPO DP link targets.
- Shared HDMI/HPO stream and link encoder code consumes the HPO top, HDMI link, FRL, stream encoder, DME, VPG, AFMT, and HDMI TB fields when enabling HDMI 2.1/FRL paths, programming packet transport, and controlling audio/infoframe metadata.
- DSC programming code consumes `DSCC*`, `DSCCIF*`, and `DSC_TOP*` fields when setting Display Stream Compression PPS values, enabling DSC blocks, handling underflow/error status, and coordinating DSC clocks and memory power.
- Performance-monitor and diagnostics paths consume `DC_PERFMON20..23` fields for counter configuration, status, interrupt acknowledgement, and low/high counter reads.

The most direct behavioral integration from this range is display output bring-up and diagnostics for compressed streams and high-bandwidth HPO outputs: DSC PPS/rate-control setup, HPO DP stream mapping, HDMI FRL/link/stream encoder setup, audio clock regeneration, metadata/infoframe scheduling, generic packet updates, and per-block performance monitoring.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong MMIO bit, preserving stale adjacent bits, or silently disabling a hardware feature.
- The file is generated. Manual edits risk divergence from the authoritative register database, matching offset header, firmware assumptions, and silicon documentation.
- The chunk boundaries are not semantic. DSC1 PPS fields started before line 47051, and HDMI TB encoder fields continue after line 49491.
- Repeated DSC and perfmon layouts make generator drift hard to see. DSC2 can be correct while DSC3, or one perfmon instance, is wrong.
- DSC PPS fields are interoperability-sensitive. Incorrect rate-control, slice, buffer, QP, BPG, delay, or bits-per-pixel masks can produce link training failures, blank output, decompressor errors, compression artifacts, or sink incompatibility that appears only for particular resolutions and DSC slice layouts.
- Underflow, overflow, end-of-frame, status, pending, and ack fields are side-effect-sensitive. Confusing status with interrupt enable or ack bits can cause missed diagnostics, stuck interrupts, or interrupt storms.
- HPO stream mapping fields are topology-sensitive. Wrong stream-to-link target masks can route a stream to the wrong link, break MST-style mappings, or leave an enabled stream disconnected.
- HDMI FRL/link/stream encoder fields are timing- and clock-sensitive. Incorrect clock, ramp FIFO, FRL metadata, active/blank timing, pixel-format, or borrow/rate-buffer fields can cause black screens, audio/video dropouts, or failures only at high TMDS/FRL rates.
- AFMT, VPG, and HDMI TB packet fields are protocol-sensitive. Bad packet line, EMP, immediate-update, lock, generic-send, metadata, ISRC, MPEG, ACR, or audio-info masks can cause HDR/VRR/vendor infoframes, audio channel status, or metadata packets to be missing, duplicated, or sent on invalid lines.
- Memory-power fields for DSCC, HDMI FRL, AFMT, DME, VPG, and HDMI TB borrow buffers interact with clock/power gating. Writes at the wrong time can create intermittent resume, modeset, or high-bandwidth-link failures.

## Test Signals

Useful validation combines generated-header consistency checks with DCN 3.6 hardware behavior:

- Build AMDGPU display support with DCN 3.6 enabled. Missing or renamed constants should fail in DCN36 DMUB/resource/IRQ setup or in shared DSC, HPO, HDMI, AFMT, VPG, DME, and perfmon register-table construction.
- Mechanically compare this range against AMD's authoritative DCN 3.6.0 register source and `dcn_3_6_0_offset.h`, allowing for the artificial chunk boundaries at DSC1 PPS and HDMI TB encoder definitions.
- Run static consistency checks that complete register groups have matching `__SHIFT` and `_MASK` definitions, especially across adjacent chunks for the partial `DSCC1_*` and `HDMI_TB_ENC_*` groups.
- Exercise DSC on supported panels and links across no-DSC/DSC transitions, multiple slice counts, different bits-per-pixel and bits-per-component settings, RGB/YUV formats, suspend/resume, hotplug, and high-resolution/high-refresh modes.
- Check DSC underflow/overflow/end-of-frame status paths, buffer fullness counters, error counters, and DSC memory-power transitions during rapid modesets and link changes.
- Exercise HPO DP stream mapping with each available HPO link target and with multi-stream or multiple active display scenarios where routing mistakes are visible.
- Exercise HDMI FRL and stream encoder paths at multiple FRL rates and pixel formats, including clock-ramp FIFO behavior, active/blank timing, metadata packet scheduling, and borrow/rate-buffer prefill controls.
- Validate AFMT/VPG/TB packet behavior through audio playback, audio clock regeneration/ACR status, HDR/static metadata, vendor-specific infoframes, MPEG/ISRC packets where applicable, generic packet immediate updates, and packet lock/conflict status.
- Exercise `DC_PERFMON20` through `DC_PERFMON23` counter setup, start/stop routing, count-off interrupts, status/ack handling, and high/low counter reads.
- Watch kernel logs, display diagnostics, link-training traces, CRCs, and sink behavior for blank output, DSC decode errors, FRL retrains, packet conflicts, missing metadata, audio dropouts, stuck pending bits, interrupt storms, and resume-only failures.

## Cross-Chunk Notes

The previous chunk contains earlier `DSCC1_DSCC_PPS_CONFIG*` fields needed to describe the complete DSC1 PPS layout. The next chunk continues HDMI TB encoder fields after `HDMI_TB_ENC_HC_ACTIVE_BLANK`, including CRC/encryption/mode and later HDMI TB state. The final per-file research document should merge adjacent chunks before making whole-file claims about all DCN 3.6 shift/mask definitions, all DSC instances, or the full HDMI TB encoder register set.

### subset-b-002138: lines 49492-51890

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 49492-51890

## Purpose

This chunk is a generated AMD DCN 3.6.0 register shift/mask slice. It has no executable code; it exports preprocessor constants that describe bit positions and masks for memory-mapped display-controller registers. Runtime AMDGPU display code pairs these constants with `dcn_3_6_0_offset.h` register offsets and then uses register helpers to pack, isolate, update, or decode individual fields without hard-coding raw bit layouts in driver logic.

The requested range contains 2,139 `#define` entries: 1,070 `__SHIFT` macros and 1,069 `_MASK` macros. It also contains 215 register-name comments and 15 address-block comments. The range starts in the middle of `HDMI_TB_ENC_HC_ACTIVE_BLANK` and ends in the middle of `DP_SYM32_ENC2_DP_SYM32_ENC_SDP_GSP_CONTROL10`, so both boundaries are artificial chunk boundaries rather than semantic hardware boundaries.

Although this source is located under a local `ceph-client` tree, the content in this range is AMDGPU DCN display hardware metadata. It does not implement Ceph or distributed-filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocation paths, or direct MMIO operations in this range. The public interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for the named field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.

The major register families covered by this chunk are:

- `HDMI_TB_ENC_*`: tail of HDMI timing/block encoder fields for horizontal active/blank count, HDMI CRC control/result, EESS encryption control, borrow/skip mode, and input FIFO error status.
- `DP_STREAM_ENC0_*`, `DP_STREAM_ENC1_*`, and `DP_STREAM_ENC2_*`: HPO DP stream encoder fields for stream-clock enable/status selection, pixel/audio input muxing, FIFO reset/enable/read-start/read-clock selection, calibrated FIFO level reporting, and spare bits.
- `APG0_*`, `APG1_*`, and `APG2_*`: audio packet generator controls for reset, enable, DP audio stream ID, channel-count override, debug audio generation, ACP/audio-info source selection, audio CRC setup/result, audio/HBR/FIFO status, output-active status, memory-power controls, and spare bits.
- `DME6_*`, `DME7_*`, and `DME8_*`: display metadata engine controls for HUBP requestor ID, metadata engine enable, stream type, double-buffer pending/taken/clear/disable state, missed-transmission status/clear, and DME memory-power state.
- `VPG6_*`, `VPG7_*`, and `VPG8_*`: video packet generator generic-packet access/data, generic-stream-packet frame-update and immediate-update trigger bits for generic packet slots 0 through 14, conflict status/clear, memory-power controls, ISRC packet access/data, and MPEG info bytes.
- `DP_SYM32_ENC0_*` and `DP_SYM32_ENC1_*`: mostly complete HPO 32-bit DP symbol encoder layouts for reset/enable, pixel-to-symbol FIFO, MSA and pixel-format double-buffering, pixel format, MSA data lanes, hblank minimum symbol width, generic SDP/GSP controls 0 through 14, audio SDP controls, metadata packet controls, MSA/VBID/video-stream controls, panel replay, video CRC controls/results/status, symbol count status/control, memory power, and spare bits.
- `DP_SYM32_ENC2_*`: beginning of the same symbol-encoder layout for instance 2, through the first two `GSP_CONTROL10` shift fields at the chunk boundary. The remainder of instance 2 is in the next chunk.

The repeated instance numbering matters. `DP_STREAM_ENC0` pairs with `APG0`, `DME6`, `VPG6`, and `DP_SYM32_ENC0`; the next two HPO stream paths repeat as `DP_STREAM_ENC1`/`APG1`/`DME7`/`VPG7`/`DP_SYM32_ENC1` and `DP_STREAM_ENC2`/`APG2`/`DME8`/`VPG8`/`DP_SYM32_ENC2`. The DME/VPG numbering reflects the wider display block namespace rather than a zero-based local sequence.

## Control Flow

This header has no runtime control flow. Runtime behavior comes from AMDGPU display code that includes this generated file:

1. DCN 3.6 resource, IRQ, and DMUB code include `dcn_3_6_0_offset.h` and this `dcn_3_6_0_sh_mask.h` header.
2. Register-list macros such as `SE_SF(...)` token-paste register and field names into shift/mask tables.
3. DCN 3.6 resource construction wires those tables into HPO DP stream encoder, APG, VPG, DME, IRQ, DMUB, and other display block objects.
4. Runtime paths use helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`; those helpers rely on the tables populated from these macros to touch only the intended field bits.

The macros do not encode sequencing rules. Consumers still need to reset and enable stream/symbol encoders in the right order, wait for reset-done bits, set muxes before enabling output, program SDP packet memory before triggering transmission, coordinate audio packet generation with audio stream setup, and avoid reading status or CRC fields while the relevant clock or memory block is powered down.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes hardware-visible DCN 3.6 register state:

- HDMI timing/CRC/encryption/mode/FIFO diagnostic state.
- HPO DP stream encoder clock, pixel mux, audio mux, and FIFO state.
- APG reset, audio stream ID, debug generation, packet source, CRC, FIFO overflow, output-active, and memory-power state.
- DME metadata enablement, stream type, double-buffer handoff state, missed-transmission status, and memory-power state.
- VPG generic packet bytes, packet-slot update triggers, generic conflict flags, ISRC/MPEG packet bytes, and GSP memory-power state.
- DP symbol encoder reset/enable, video FIFO, pixel format, MSA payload, SDP/GSP scheduling, audio packet enable/mute controls, metadata packet controls, VBID and stream enablement, panel replay, CRC capture, symbol counting, and memory-power state.

Persistence is hardware-defined. Configuration fields generally remain until a modeset, stream teardown, power-gating transition, suspend/resume, GPU reset, or ASIC reset rewrites them. Status, reset-done, FIFO-error, conflict, CRC, symbol-count, double-buffer-pending, and missed-transmission fields may be read-only, sticky, write-one-to-clear, self-clearing, or valid only while the related clock domain is active. This generated header does not encode those access semantics; driver code and hardware documentation must provide them.

## Dependencies And Integration Points

This file must stay synchronized with AMD's generated DCN 3.6.0 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h` supplies the matching MMIO register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c` includes the generated DCN 3.6 headers for DMUB register setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c` includes the same headers for DCN 3.6 interrupt source tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c` includes this header and builds DCN 3.6 HPO DP stream encoder shift/mask tables from `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST(__SHIFT)` and `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST(_MASK)`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h` defines the shared HPO DP stream encoder register, shift, and mask table shape that consumes fields such as `DP_STREAM_ENC0_DP_STREAM_ENC_CLOCK_CONTROL`, `DP_SYM32_ENC0_DP_SYM32_ENC_CONTROL`, `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL*`, and `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_AUDIO_CONTROL0`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.h` consumes APG field names for reset, enable, DP audio stream ID, debug audio channel enablement, and memory-power forcing.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn31/dcn31_vpg.h` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_vpg.c` consume VPG generic packet, frame-update, immediate-update, status, and memory-power fields through register helpers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc21_enum.h` provides generated enum values for some fields represented here, including HDMI CRC source/type and input FIFO error values.

The direct behavioral integration surface is HPO DisplayPort and HDMI output programming: stream encoder clocking and input selection, DP symbol generation, audio packet generation, metadata/SDP packet transport, video packet updates, CRC diagnostics, and stream status readback.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while corrupting adjacent MMIO fields, disabling output, misrouting audio/video streams, or breaking readback decoding.
- The header is generated. Manual edits risk divergence from the authoritative register database, firmware assumptions, hardware documentation, and `dcn_3_6_0_offset.h`.
- The chunk boundaries are not semantic. The first register group is missing the `HDMI_HC_ACTIVE` shift from the previous line, and the `DP_SYM32_ENC2_DP_SYM32_ENC_SDP_GSP_CONTROL10` group continues after line 51890.
- Instance repetition makes generator or copy drift hard to spot. Instance 0 working does not prove instances 1 or 2 are correct, especially where DME/VPG indices use `6/7/8` while stream/APG/symbol encoder indices use `0/1/2`.
- Reset, enable, and reset-done fields are sequencing-sensitive. Incorrect masks can produce timeout loops, stuck disabled encoders, or writes that appear to succeed while the block remains in reset.
- Clock and FIFO fields are timing-sensitive. Wrong FIFO reset, read-start-level, read-clock-source, or active/error masks can cause intermittent underflow, corruption, or false diagnostics that only appear under high bandwidth or clock-ramp transitions.
- Generic SDP/GSP packet controls are packet-scheduling-sensitive. Incorrect one-shot, continuous, double-buffer, payload-size, SOF-reference, or line-number fields can send HDR/AVI/vendor/audio metadata on the wrong frame, miss deadlines, or leave pending bits stuck.
- APG and audio CRC/status fields are user-visible for DP audio. Mask mistakes can produce missing channels, wrong stream IDs, false FIFO overflow handling, invalid CRC results, or broken HBR audio enablement.
- DME and VPG memory-power fields interact with clock/power gating. Access while the block is gated can produce stale status or dropped packet programming unless the caller follows block-specific power sequencing.
- HDMI CRC and input FIFO fields are mostly diagnostic; a mask error may not affect ordinary display output but can break validation, factory diagnostics, or debug tooling.

## Test Signals

Useful validation combines generated-header checks with DCN 3.6 hardware behavior:

- Build AMDGPU display support with DCN 3.6 enabled. Missing or renamed constants should fail in DCN36 DMUB, IRQ, resource, HPO DP stream encoder, APG, VPG, DME, or register-helper table construction.
- Mechanically compare this range against AMD's authoritative DCN 3.6.0 register source and the adjacent `dcn_3_6_0_offset.h` names, accounting for the artificial line boundaries at the start and end.
- Run static consistency checks that complete register groups have matching `__SHIFT` and `_MASK` entries across chunk boundaries, especially `HDMI_TB_ENC_HC_ACTIVE_BLANK` and `DP_SYM32_ENC2_DP_SYM32_ENC_SDP_GSP_CONTROL10`.
- Exercise HPO DP stream enable/disable, stream mux selection, link bring-up, MST or multi-stream routing where available, hotplug, modesets, suspend/resume, and rapid stream teardown/recreation.
- Exercise DP audio through APG paths, including mute/unmute, channel-count changes, HBR audio, stream ID changes, audio CRC capture, and FIFO overflow status clearing.
- Exercise SDP/GSP metadata paths: HDR metadata, infoframes, vendor-specific packets, ISRC/MPEG packet programming, one-shot versus continuous transmission, frame-update versus immediate-update behavior, and packet-slot conflicts.
- Validate DME metadata double-buffer handling by checking pending/taken/missed-transmission status under normal modesets, high frame rates, and metadata updates near vblank boundaries.
- Validate DP symbol encoder CRC, symbol count, VBID compressed-stream flag fields, panel replay controls, and pixel-format/MSA double-buffering across common pixel formats, DSC/compressed stream scenarios, and low-power transitions.
- Watch kernel logs and display diagnostics for stuck reset-done waits, stream-enable failures, underflow/FIFO errors, packet deadline misses, stale pending bits, audio dropouts, CRC mismatches, memory-power transition failures, and resume-only HPO display artifacts.

## Cross-Chunk Notes

The previous chunk contains the beginning of the HDMI timing/block encoder group, including fields immediately before `HDMI_TB_ENC_HC_ACTIVE_BLANK__HDMI_HC_BLANK__SHIFT`. The next chunk continues `DP_SYM32_ENC2_DP_SYM32_ENC_SDP_GSP_CONTROL10` and the rest of the instance-2 DP symbol encoder fields. The final per-file research document should merge adjacent chunks before making whole-file claims about all DCN 3.6 shift/mask definitions or all HPO DP stream encoder instances.

### subset-b-002139: lines 51891-54330

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 51891-54330

## Scope And Purpose

This chunk is a generated AMD Display Core Next 3.6 register field map. It defines C preprocessor constants for hardware bit positions (`__SHIFT`) and bit masks (`_MASK`) used by the AMDGPU display driver when programming DCN 3.6 DisplayPort, DPIA, display-link power, virtualization, and Azalia HDMI/DP-audio registers.

The slice starts in the middle of `DP_SYM32_ENC2_DP_SYM32_ENC_SDP_GSP_CONTROL10` and ends in the middle of `AZALIA_F2_CODEC_PIN_CONTROL_FORMAT_CHANGED`. Adjacent chunks are needed for the complete first and last register definitions. Within the visible range, the content is entirely declarative: it has no functions, structs, enums, or executable control flow. Its purpose is to provide exact register-field constants consumed by generic register helper macros such as `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, `REG_WAIT`, `FD_MASK`, and `FD_SHIFT`.

## Register Areas Covered

The visible register groups are organized by address-block comments and by instance-numbered macro prefixes:

- `DP_SYM32_ENC2_*`: tail of HPO DisplayPort symbol encoder instance 2, covering SDP generic packet controls 10-14, SDP stream control, SDP audio controls, metadata packets, MSA/VBID/video stream controls, panel replay, video CRC, symbol count, memory power, spare, and CRC result registers.
- `dce_dc_hpo_dp_stream_enc3_dispdec`: stream encoder instance 3 fields for clock control, pixel/audio input muxing, clock-ramp FIFO reset/status, and spare bits.
- `dce_dc_hpo_dp_stream_enc3_apg_apg_dispdec`: audio packet generator instance 3 fields for APG enable/reset, format and channel layout, debug generator controls, packet update points, audio CRC, APG status, memory power, and spare.
- `dce_dc_hpo_dp_stream_enc3_dme_dme_dispdec`: DME9 dynamic metadata engine controls for enable, halt, ready/idle/status, line reference, frame counter, and memory power.
- `dce_dc_hpo_dp_stream_enc3_vpg_vpg_dispdec`: VPG9 video packet generator fields for generic packet access/data, GSP frame/immediate update slots, status, memory power, ISRC data, and MPEG infoframes.
- `dce_dc_hpo_dp_sym32_enc3_dispdec`: full HPO DisplayPort symbol encoder instance 3 fields for reset/enable, FIFO, double buffering, pixel format, MSA lane data, HBLANK, generic SDP packet slots 0-14, SDP/audio/metadata control, MSA/VBID/video stream state, panel replay, CRC, symbol counting, memory power, spare, and CRC result registers.
- `dce_dc_hpo_dp_link_enc0_dispdec` and `dce_dc_hpo_dp_link_enc1_dispdec`: HPO DP link encoder clock enable and spare fields for two link encoder instances.
- `dce_dc_hpo_dp_dphy_sym320_dispdec` and `dce_dc_hpo_dp_dphy_sym321_dispdec`: DP PHY SYM32 instance 0 and 1 fields for PHY control/status, SAT updates, virtual-channel rate control and status, training-pattern and PRBS/custom pattern registers, error status, symbol override, symbol counters, and CRC configuration/status/count.
- `dce_dc_dchvm_hvm_dispdec`: display controller HVM/RIOMMU fields for request timeout, HVM clock/memory power, RIOMMU client ID, poison response, and RIOMMU status.
- `dce_dc_dlpc_dlpc_dispdec`: display link power controller fields for enabling DLPC logic, counters, OPTC snapshots, power-up controls, OTG resync, ZSC/LONO power, spare, and counter initialization.
- `dce_dpia_dpia_mu0_dpiadec`: DPIA message unit fields for global and per-port clocks/resets, tunnel protocol interface status, interrupt status/control/ack, local interrupt handling, RBBMIF timeout/status, microsecond reference, port ADP status, glue/debug controls, performance counters, index/data access, and spare.
- `azendpoint_f2codecind`: Azalia F2 codec converter and pin endpoint fields for stream format, channel/stream IDs, digital converter flags, stripe control, ramp/GTC settings, widget capability parameters, supported rates/formats, pin connection/configuration/sense/speaker/channel/downmix controls, ACP data, audio descriptors, multichannel/HBR/lipsync/sink-info controls, IEC 60958 channel-status overrides, association and output status, LPIB snapshots, coding type, and the beginning of format-change reporting.

## Important APIs, Types, And Macros

This header exposes constants rather than C APIs. The important naming contract is:

- `REGISTER__FIELD__SHIFT`: the low-bit position for a register field.
- `REGISTER__FIELD_MASK`: the fully shifted bit mask for that field.
- `REGISTER` prefixes encode both block instance and hardware register name, for example `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL11`.
- Address-block comments divide the generated macro namespace into hardware units, but are not compiled.

The consumer-side APIs are elsewhere in AMD display code. `dcn36_resource.c`, `irq_service_dcn36.c`, and `dmub_dcn36.c` include both `dcn_3_6_0_offset.h` and this `_sh_mask.h` header. Resource initialization macros build register address tables from the offset header, while field-list macros load these shift/mask constants into per-block `shift` and `mask` structs. Runtime code then programs hardware through helpers from `reg_helper.h`.

Examples of the integration pattern visible in related source include:

- `SRI(reg_name, block, id)` expands instance-specific register offsets, such as `regDP_SYM32_ENC3_DP_SYM32_ENC_*`.
- `SE_SF(register, field, __SHIFT)` and `SE_SF(register, field, _MASK)` select constants from this header and populate stream encoder field tables.
- `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)` are used by DMUB register initialization to store field metadata.
- `REG_UPDATE`, `REG_GET`, and `REG_WAIT` take logical register and field names, then use the initialized mask/shift data to modify or poll exact hardware bits.

## Behavioral Model And Control Flow

There is no local control flow in this chunk. Its behavior is indirect: it determines how control flow in display, audio, IRQ, and DMUB code maps logical operations onto MMIO bitfields.

For HPO DP stream encoder code, these fields support sequences such as enabling stream clocks, asserting/deasserting `DP_SYM32_ENC_RESET`, waiting on `DP_SYM32_ENC_RESET_DONE`, enabling `DP_SYM32_ENC_ENABLE`, selecting pixel/audio stream sources, enabling `VID_STREAM_ENABLE`, resetting FIFOs, enabling SDP streams, muting audio, enabling audio packet types, and programming MSA/VBID/metadata packet transmission.

For APG/VPG/DME blocks, the fields describe packet-generation state machines: enable bits, reset done/status bits, line-number trigger positions, frame/immediate update requests, busy/done indicators, CRC capture controls, and memory power status. Driver code can use these to synchronize audio/video metadata packets with frame or line timing.

For DPHY blocks, the fields back link training, PHY status, virtual-channel allocation, test pattern generation, symbol override, error reporting, symbol counters, and CRC collection. Incorrect masks here would affect link bring-up diagnostics and training/test modes more than ordinary C control flow.

For DPIA and Azalia blocks, the fields back interrupt routing, per-port reset/clock state, tunnel status, performance counters, and HDMI/DP audio codec verb state. Those values connect display mode programming to audio exposure, sink capability reporting, multichannel enablement, lipsync data, HBR support, channel-status overrides, and format-change signaling.

## State And Persistence Behavior

This header itself has no mutable state and persists nothing. The constants describe hardware state that lives in MMIO registers and hardware-managed status bits.

Stateful hardware behavior represented by this chunk includes:

- Double-buffered SDP, MSA, pixel-format, metadata, VPG, and packet-update fields whose pending bits indicate that a programmed value has not yet latched.
- Enable/status pairs for stream, encoder, FIFO, APG, VPG, DME, DPHY, DLPC, HVM, and DPIA units.
- Reset and reset-done fields for DP stream FIFOs, APG/DME/VPG memory or block state, DPIA ports, and DP symbol encoders.
- Hardware counters and snapshots such as symbol counts, CRC values, LPIB, LPIB timer snapshot, DLPC counters, frame counters, wrap counters, and DPIA performance counters.
- Sticky or acked status/interrupt fields such as DPIA interrupt status/ack, DPHY error status, transmission pending/deadline missed flags, format-change indication, and output-active state.
- Power-management fields for memory/light-sleep/deep-sleep status in encoder/APG/VPG/DCHVM/DLPC-related blocks.

Persistence is therefore hardware-scoped. Values may survive until reset, power-gating, mode-set reprogramming, interrupt acknowledgement, or an explicit driver write. The header must remain synchronized with the ASIC register specification because the compiler cannot detect semantic errors in generated numeric masks.

## Dependencies And Integration Points

Primary dependencies are generated register-offset companions and AMD display register helper infrastructure:

- `dcn_3_6_0_offset.h` supplies the matching register addresses and base indices. This file supplies only shifts and masks.
- `drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c` includes this header while constructing DCN 3.6 resource objects and register tables.
- `drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c` includes this header for interrupt-source register enable/ack masks.
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c` includes this header to initialize DMUB-visible register masks and shifts.
- HPO DP stream/link encoder code under `drivers/gpu/drm/amd/display/dc/hpo/dcn31/` defines reusable DCN 3.x register-list and mask/shift-list macros that are instantiated with DCN 3.6 generated names.
- `soc24_enum.h` provides value enums for several Azalia codec fields whose bit positions are defined here.
- Linux DRM/AMDGPU display mode-setting, audio, hotplug, DisplayPort link training, panel replay, metadata packet, and DMUB paths all rely on correct field metadata even though this header has no direct function calls.

The source path is under `sources/distributed-fs/ceph-client/`, but the content is a vendored Linux AMDGPU display-driver header. It is not related to Ceph filesystem runtime behavior except through the repository's source layout.

## Risks And Edge Cases

The biggest risk is silent hardware misprogramming. A wrong shift or mask still compiles, but may write a neighboring field, fail to clear a pending bit, poll the wrong status bit, or corrupt a multi-bit value such as line number, channel allocation, CRC, audio format, or performance-counter select.

Specific risk areas in this chunk include:

- Chunk boundary splits: line 51891 omits earlier fields for `DP_SYM32_ENC2_DP_SYM32_ENC_SDP_GSP_CONTROL10`, and line 54330 omits the final mask for `AZALIA_F2_CODEC_PIN_CONTROL_FORMAT_CHANGED`. Reconciliation must merge adjacent chunks before treating those register definitions as complete.
- Repeated instance layouts: `DP_SYM32_ENC2`, `DP_SYM32_ENC3`, `DP_DPHY_SYM320`, and `DP_DPHY_SYM321` contain many duplicated field names. Copy-generation drift in only one instance can break a subset of physical ports.
- Wide masks: fields such as 16-bit line numbers, 16-bit CRC values, 24/32-bit data payloads, and full-register masks (`0xFFFFFFFFL`) need exact width. Overly wide masks can overwrite reserved bits.
- Status versus control fields: some registers combine writable control bits with hardware-owned status/pending bits. Register-update helpers must preserve unrelated bits where required.
- Double-buffer/pending semantics: enabling double buffers without checking pending fields can cause frame-timing-sensitive updates to apply late or not at all.
- Audio endpoint compatibility: Azalia codec fields encode externally visible HDMI/DP audio capabilities and stream parameters. Wrong values can lead to missing audio devices, wrong channel maps, muted streams, unsupported HBR behavior, or bad ELD/sink capability reporting.
- Interrupt and ack masks: DPIA interrupt status/control/ack fields must be exact to avoid interrupt storms or lost hotplug/tunnel events.
- Power and reset sequencing: memory power, clock enable, and reset status fields are often used in ordered programming sequences. Incorrect constants can lead to timeouts in `REG_WAIT` paths.

## Test Signals

There are no direct unit tests for this generated header in the chunk. Strong signals are compile-time and hardware/driver integration signals:

- AMDGPU display driver builds must succeed for DCN 3.6, proving all referenced field names from resource, IRQ, DMUB, stream encoder, link encoder, APG, VPG, DME, DPIA, and audio code resolve.
- DisplayPort bring-up on DCN 3.6 hardware should exercise `DP_STREAM_ENC*`, `DP_SYM32_ENC*`, `DP_LINK_ENC*`, and `DP_DPHY_SYM32*` fields through mode-set, blank/unblank, link training, FIFO reset, video stream enable, and CRC/debug paths.
- DP/HDMI audio tests should verify Azalia converter/pin behavior: supported formats, channel allocation, HBR enablement, mute state, lipsync, sink info, ACP/audio descriptor access, and format-change signaling.
- Hotplug, HPD-RX, DPIA tunnel, and USB4/DP-alt-mode scenarios should validate DPIA MU interrupt/status/ack and per-port reset/clock fields.
- Panel replay, metadata packet, HDR/VRR/adaptive-sync, VSC/SPD/infoframe, ISRC, and MPEG packet tests should cover SDP/GSP/VPG/DME fields and double-buffer pending behavior.
- Suspend/resume, runtime power management, and display idle tests should cover memory-power, light-sleep/deep-sleep, DLPC, DCHVM, and reset-done fields.
- Register readback or golden-register traces on real DCN 3.6 ASICs are the most direct validation for mask/shift correctness, because generated headers can compile while still encoding the wrong hardware bit.

### subset-b-002140: lines 54331-56831

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 54331-56831

## Purpose

This chunk is generated AMD DCN 3.6.0 register shift/mask metadata for the display audio, or Azalia/HDA, hardware path. It contains no executable C logic. Its public surface is C preprocessor constants that encode bit positions and bit masks for DCN 3.6 audio codec, stream, CRC, endpoint, sink-info, and channel-status registers.

The requested range contains 2,039 `#define` entries, split into 1,020 `__SHIFT` macros and 1,019 `_MASK` macros, across 382 register-name groups. It starts just after the `AZALIA_F2_CODEC_PIN_CONTROL_FORMAT_CHANGED` group from the previous chunk and ends in the middle of `AZF0ENDPOINT2_AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE`, so both boundaries are artificial line-split boundaries rather than complete hardware-block boundaries.

Although this file is under a local `ceph-client` source mirror, this chunk is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, locks, allocation paths, or direct MMIO operations in this range. The interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating or updating that field.

The main register families in this chunk are:

- `AZALIA_F2_CODEC_PIN_*`: tail of F2 pin status/parameter support, including wireless display identification, remote keepalive, audio widget capabilities, pin capabilities, and connection-list length.
- `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`: codec descriptor format fields for max channels, supported frequencies, descriptor byte 2, and stereo-frequency support.
- `AZALIA_F2_CODEC_PIN_CONTROL_*` sink metadata: manufacturer/product IDs, sink description length, port IDs, and monitor-name bytes `SINK_DESCRIPTION0` through `SINK_DESCRIPTION17`.
- `AZALIA_INPUT_CRC0/1_CHANNEL*` and `AZALIA_CRC0/1_CHANNEL*`: per-channel input and output CRC result fields for channels 0-7.
- `AZALIA_F2_CODEC_INPUT_*`: input converter and input pin controls for converter format, channel/stream ID, digital converter status, widget capabilities, supported sizes/rates, stream formats, unsolicited responses, pin sense, default configuration, channel allocation, multichannel enablement, HBR response, LPIB snapshots, input status, infoframe, and channel status.
- `AZALIA_F2_CODEC_ROOT_*` and `AZALIA_F2_CODEC_FUNCTION_*`: root/function node identity, revision, subordinate-node count, power state, subsystem ID response, converter synchronization, reset, supported size/rates, stream formats, group type, and power states.
- `AZF0STREAM0` through `AZF0STREAM15`: repeated Azalia stream FIFO-size and latency-counter controls, worst-case latency, cumulative latency, and cumulative request counters.
- `AZF0ENDPOINT0`, `AZF0ENDPOINT1`, and the beginning of `AZF0ENDPOINT2`: repeated F0 endpoint codec converter and pin fields for audio widget capabilities, converter format, channel/stream ID, digital converter control, supported formats/rates, stripe control, ramp rate, GTC embedding/counter deltas, pin capabilities, unsolicited responses, pin sense, widget output enable, speaker/channel allocation, ACP data, audio descriptors, multichannel enablement, lipsync, HBR, sink info, hot-plug control, unsolicited-response force, default configuration, IEC 60958 channel-status overrides, association info, digital output status, LPIB snapshots, coding type, format-changed state, wireless display identification, remote keepalive, audio enable/disable/format-change interrupt status, and endpoint fine-grain clock-gating repeat disable.

Many groups are mechanically repeated per stream or endpoint. The repeated shapes are intentional: one wrong generated field in a single instance can break only that stream or connector while adjacent instances still work.

## Control Flow

This header has no runtime control flow. Runtime behavior comes from AMDGPU display code that includes this generated header with the matching DCN 3.6 offset header:

1. DCN 3.6 code includes `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h`.
2. Register-list and field-list macros token-paste register and field names into per-block register, shift, and mask tables.
3. DCN 3.6 setup code wires those tables into DMUB, IRQ, resource, audio, and hardware-sequencer paths.
4. Runtime code reads, writes, or updates registers through helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `AZ_REG_READ`, `AZ_REG_WRITE`, `set_reg_field_value`, `FD_MASK`, and `FD_SHIFT`.

The chunk only defines bit layout. Sequencing is supplied by consumers. For example, `dce_audio.c` programs audio descriptors from EDID-derived audio modes, computes available bandwidth before exposing HBR support, writes sink manufacturer/product/name/port metadata, programs lipsync fields, and toggles hot-plug/audio-related fields through the Azalia register helpers.

## State And Persistence Behavior

This chunk stores no software state and persists nothing directly. It describes hardware-visible DCN 3.6 audio state:

- Codec capability state, including widget capabilities, pin capabilities, supported sample sizes/rates, stream format support, power states, and connection-list length.
- Audio format descriptor state for HDMI/DP audio format exposure, max channel count, sample-frequency support, descriptor byte 2, and stereo-frequency support.
- Input and output audio transport state for converter format, stream/channel IDs, digital converter bits, multichannel enable/mute/channel-ID fields, channel allocation, channel status, HBR capability/enablement, ACP packets, and infoframes.
- Sink identity state for ELD-like monitor information: manufacturer ID, product ID, sink description length, port IDs, and display-name bytes.
- Runtime status and diagnostics for output-active status, format-change notification/reason/response, audio enable/disable/format-change interrupt status, unsolicited responses, pin sense, LPIB and timer snapshots, stream FIFO size, stream latency counters, and per-channel CRC results.
- Timing and synchronization state for lipsync response fields, GTC embedding, GTC counter deltas/min/max, converter synchronization, and LPIB snapshot locking/wrap count.
- Power and clock-related state for codec/function power state, hot-plug control clock-gating bits, endpoint audio-enabled state, and endpoint fine-grain clock-gating repeat disable.

Persistence is hardware-defined. Configuration fields generally remain until modeset/audio reconfiguration, connector hotplug, stream teardown, suspend/resume, power gating, GPU reset, or ASIC reset. Status, interrupt, CRC, counter, snapshot, force, reset, and acknowledge fields can be read-only, sticky, write-one-to-clear, self-clearing, or valid only while the associated audio controller, stream, endpoint, and display link are powered and clocked. This generated header does not describe access semantics; consumers must follow the register specification and block-specific driver code.

## Dependencies And Integration Points

This file must stay synchronized with AMD's generated DCN 3.6.0 register database and with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h`, which supplies matching MMIO offsets and base indexes. A shift/mask header from one ASIC generation paired with a different offset header can compile while programming incorrect bits.

Direct DCN 3.6 integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c`, which includes the offset and shift/mask headers and initializes DMUB register masks/shifts with `FD_MASK` and `FD_SHIFT`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c`, which includes both generated headers for DCN 3.6 resource construction.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c`, which includes both generated headers for interrupt source setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.h`, whose register list includes Azalia-level resources such as `AZALIA_AUDIO_DTO` and `AZALIA_CONTROLLER_CLOCK_GATING`.
- Shared audio code such as `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.c`, which programs the same Azalia/HDA semantic fields for HBR capability, audio descriptors, lipsync, sink info, and hot-plug/audio control through generation-specific register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h`, which supplies semantic enum values for many Azalia field families such as converter format, digital converter bits, audio descriptor format codes, multichannel mute/mode, unsolicited-response enablement, and widget output enablement.

The behavioral integration surface is display audio over HDMI/DP, including EDID/ELD-derived capability exposure, audio stream formatting, bandwidth/HBR decisions, multichannel layout, sink identification, link-associated audio status, interrupt reporting, CRC diagnostics, and stream latency observability.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong mask or shift can compile cleanly while updating the wrong MMIO bits or preserving the wrong adjacent fields.
- The file is generated. Manual edits risk diverging from the authoritative register database, the matching offset header, firmware expectations, and silicon documentation.
- The chunk boundaries are not semantic. The previous chunk contains part of `AZALIA_F2_CODEC_PIN_CONTROL_FORMAT_CHANGED`; the next chunk continues the `AZF0ENDPOINT2_AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE` masks and later endpoint fields.
- Repeated stream and endpoint layouts can hide one-instance generator drift. Streams 0-15 and endpoints 0-2 should not be assumed correct merely because another instance works.
- Audio descriptor fields are user-visible through HDMI/DP audio capability reporting. Bad max-channel, frequency, or descriptor-byte masks can expose unsupported formats or hide valid formats, causing no-audio, fallback stereo, or compressed-audio failures.
- HBR, multichannel, and channel-status fields are interoperability-sensitive. Wrong masks can break 192 kHz/8-channel checks, compressed bitstream modes, IEC 60958 channel numbers, mute state, or channel mapping.
- Sink-info fields pack byte strings and IDs. Off-by-one masks or wrong byte lanes can corrupt monitor names, manufacturer/product IDs, or port identifiers consumed by audio user space.
- Interrupt/status fields are side-effect-sensitive. Confusing enable, status, clear, force, and response fields can cause missed audio format-change notifications, unsolicited-response storms, or stale hotplug/audio status.
- LPIB, timer snapshot, CRC, and latency-counter fields are diagnostic and timing-sensitive. Incorrect definitions can make debugging audio underruns, synchronization, or channel corruption misleading.
- Power, clock-gating, hot-plug, reset, and function power-state fields can interact with runtime PM and display power sequencing; invalid updates may only reproduce during suspend/resume, rapid hotplug, or clock-gated idle transitions.

## Test Signals

Useful validation should combine generated-header consistency checks with DCN 3.6 display-audio behavior:

- Build AMDGPU display support with DCN 3.6 enabled. Missing or renamed fields should fail where DCN36 DMUB, IRQ, resource, audio, or register-helper tables reference them.
- Mechanically compare this line range against AMD's authoritative DCN 3.6.0 register source and verify that all complete register groups have matching `__SHIFT` and `_MASK` entries, allowing for the known partial groups at both boundaries.
- Exercise HDMI and DisplayPort audio on DCN 3.6 hardware across stereo, 5.1/7.1 LPCM, 44.1/48/96/192 kHz, compressed formats, and HBR-capable modes.
- Verify EDID/ELD-derived audio descriptors and sink info from user space, including monitor name length/bytes, manufacturer/product IDs, port IDs, channel counts, sample rates, and compressed-format capability exposure.
- Test hotplug, unplug/replug, MST, suspend/resume, runtime power management, audio stream start/stop, and rapid modesets while watching for no-audio, stale audio devices, missing format-change events, or interrupt storms.
- Validate multichannel mapping and mute/channel-ID programming with channel-order tests and compressed bitstream playback.
- Use CRC, LPIB snapshot, latency-counter, and debug/status reads where available to confirm counters update and snapshots are coherent while audio is active.
- Watch kernel logs and display/audio diagnostics for HBR exposure mismatches, ELD corruption, HDMI/DP audio underruns, incorrect channel allocation, stuck audio-enabled/disabled interrupt status, and resume-only audio failures.

## Cross-Chunk Notes

The final per-file research document should merge this with adjacent chunks before making whole-file claims about all DCN 3.6 Azalia register fields. The preceding chunk owns the beginning of the `FORMAT_CHANGED` group, and the following chunk owns the rest of `AZF0ENDPOINT2` plus later endpoint and audio blocks.

### subset-b-002141: lines 56832-59202

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 56832-59202

## Purpose

This chunk is a generated AMD DCN 3.6.0 register shift/mask slice. It contains no executable logic; it exports C preprocessor constants that describe bit positions and masks for memory-mapped display/audio controller registers. Driver code combines these constants with the companion `dcn_3_6_0_offset.h` offsets so register helper macros can pack, unpack, and update specific hardware fields without spelling numeric bit layouts at each call site.

The requested range is focused on Azalia/HD-audio endpoint-indirect register fields for display audio. It contains 2,048 `#define` entries, including 1,023 `__SHIFT` macros and 1,037 `_MASK` macros, plus 311 register-name comments and 4 `addressBlock` comments. The line boundaries are artificial: the chunk starts midway through `AZF0ENDPOINT2` pin audio descriptor and multichannel definitions, includes complete or near-complete endpoint blocks for `AZF0ENDPOINT3`, `AZF0ENDPOINT4`, and `AZF0ENDPOINT5`, and ends midway through `AZF0ENDPOINT6` pin/channel-status definitions. The next chunk begins `AZF0ENDPOINT7`.

Although the file sits under a local `ceph-client` source mirror, this chunk is AMDGPU display/audio hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, allocations, includes, or direct I/O operations in this range. The interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a field inside the named register.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating or preserving that field in read/modify/write operations.

The main register families covered are:

- `AZF0ENDPOINT2_*`: tail of endpoint 2 pin control metadata, starting in audio descriptor 3-13 and multichannel control, then lip-sync/HBR response, sink information, hot-plug/audio enablement, unsolicited-response force, default configuration, IEC 60958 channel-status overrides, association information, LPIB snapshot/counter fields, coding type, format-change signaling, remote keepalive, audio enable/disable/format-change interrupt status, and endpoint fine-grain clock-gating repeat disable.
- `AZF0ENDPOINT3_*`, `AZF0ENDPOINT4_*`, and `AZF0ENDPOINT5_*`: repeated endpoint-indirect blocks containing converter widget capability and format controls, stream/channel IDs, digital converter channel-status bits, stream format and supported rate parameters, stripe control, ramp rate, GTC embedding/counter delta telemetry, pin widget capabilities, pin capabilities, unsolicited-response and pin-sense controls, widget output enable, channel/speaker mapping, ACP packet data, audio descriptors 0-13, multichannel pair/single controls, sink metadata, hot-plug/audio state, IEC 60958 override registers, LPIB/status/format-change registers, and audio interrupt status. Endpoint 5 also has `CODEC_CONVERTER_CONTROL_GTC_OFFSET_DEBUG`.
- `AZF0ENDPOINT6_*`: begins another repeated endpoint-indirect block and reaches through pin control multichannel mode and `PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8` plus the start of the post-override pin/status area before the chunk boundary.

Important field groups include:

- Audio format programming: `NUMBER_OF_CHANNELS`, `BITS_PER_SAMPLE`, `SAMPLE_BASE_DIVISOR`, `SAMPLE_BASE_MULTIPLE`, `SAMPLE_BASE_RATE`, and `STREAM_TYPE`.
- Stream routing and digital output: `CHANNEL_ID`, `STREAM_ID`, `DIGEN`, validity/copy/non-audio/professional bits, category/channel count, and `KEEPALIVE`.
- Sink and ELD-like metadata: manufacturer/product IDs, port IDs, display-description bytes, audio descriptor `MAX_CHANNELS`, supported frequencies, descriptor byte 2, and stereo frequency support for descriptor 0.
- Pin/output control: `OUT_ENABLE`, HDMI/DP connection indicators, speaker/channel allocation, LFE/downmix/level-shift bits, HBR capability/enable, lipsync values, hot-plug clock/audio state, and default association/configuration fields.
- Multichannel programming: pair-mode fields for `MULTICHANNEL01/23/45/67`, single odd-channel fields for `MULTICHANNEL1/3/5/7`, mute bits, per-channel IDs, and `MULTICHANNEL_MODE`.
- IEC 60958 channel-status override fields: mode, source number, clock accuracy, word length, sampling frequency, original sampling frequency, frequency coefficient, MPEG surround, CGMS-A, and channel numbers for left/right/2-7.
- Runtime observability and events: LPIB snapshot lock, cyclic wrap count, LPIB value, LPIB timer snapshot, coding type, format-changed flag/ack/reason/response, wireless display identification, remote keepalive capability, audio enable state, audio enabled/disabled/format-changed interrupt flags, masks, types, and endpoint fine-grain clock-gating repeat disable.

The symbolic enum values for many Azalia fields live outside this header, notably in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h`, while this chunk supplies only positions and masks.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU display/audio code that includes the generated DCN 3.6 headers:

1. DCN 3.6 code includes `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h`.
2. Register-list macros token-paste register and field names into per-block address, shift, and mask tables.
3. DCN 3.6 resource, IRQ, and DMUB setup code wires those tables into display block objects and firmware-facing register descriptions.
4. Runtime display/audio paths use register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` to manipulate only the intended MMIO fields.

The macros do not encode sequencing. Consumers still have to program audio format, channel mapping, IEC 60958 status, infoframes/AFMT state, sink metadata, enable bits, and interrupt/status bits in the order required by the display engine, HD-audio controller, and link type. They also have to coordinate with DRM connector state, ELD notification, hotplug, stream commit, suspend/resume, and display power/clock gating.

## State And Persistence Behavior

This chunk stores no software state and persists nothing directly. It describes hardware-visible state in Azalia endpoint registers:

- Converter state for current audio sample format, stream ID/channel ID, digital-converter status bits, supported stream formats/rates, ramp behavior, stripe control, and GTC embedding/counter-delta telemetry.
- Pin state for output enablement, channel/speaker mapping, ACP packet metadata, audio descriptors, multichannel enable/mute/channel IDs, lipsync/HBR capabilities, sink identity/description, default configuration, hot-plug/audio enable state, forced unsolicited responses, and association info.
- Channel-status override state for IEC 60958 fields consumed by HDMI/DP audio sinks and audio packet generation paths.
- Runtime status and event state for LPIB snapshots, coding type, audio format changes, wireless display/remote keepalive, audio enable/disable status, and endpoint interrupt flags/masks/types.
- Power/clock-related state through endpoint fine-grain clock-gating repeat disable and hot-plug clock state fields.

Persistence is hardware-defined. Configuration fields usually remain until a modeset, audio stream reprogramming, hotplug handling, suspend/resume, power-gating transition, GPU reset, or ASIC reset rewrites them. Status, interrupt, snapshot, LPIB, GTC, and debug fields may be read-only, sticky, write-one-to-clear, self-clearing, clock-gated, or valid only while the related endpoint and display pipe are powered. This generated header does not identify those access semantics; consumers must rely on the register specification and the block-specific driver logic.

## Dependencies And Integration Points

This file must remain synchronized with AMD's generated DCN 3.6.0 register database and the matching offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h` supplies the matching MMIO offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c` includes both DCN 3.6 generated headers while initializing DMUB register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c` includes them for DCN 3.6 interrupt-source setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c` includes them for DCN 3.6 resource construction and hardware register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h` provides symbolic values for many Azalia audio format, digital converter, pin, multichannel, and soft-reset fields whose masks are defined here.
- Display manager audio paths in `amdgpu_dm.c` maintain connector audio instances, expose ELD through the DRM audio component, fill audio info from EDID/SAD data, and notify audio clients when endpoints change.
- AFMT/APG code under `display/dc/dcn31/` handles audio packet and 60958 programming for nearby DCN generations; DCN 3.6 consumers use the same generated-header style even when field names are routed through version-specific register tables.

The most direct behavioral integration is HDMI/DisplayPort audio enumeration and playback: EDID-derived audio modes become stream/audio-info state, DCN audio/AFMT/APG logic programs endpoint and packet fields, and the Linux audio component obtains ELD/pin notifications for the HDA side.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong MMIO bit, clobbering an adjacent field, or silently leaving an audio feature disabled.
- The file is generated. Manual edits risk divergence from the authoritative register database, the offset header, firmware assumptions, and silicon documentation.
- The chunk boundaries are not semantic. Endpoint 2 starts before this range, endpoint 6 continues after this range, and the final per-file report should merge adjacent chunks before making whole-endpoint coverage claims.
- Endpoint blocks are highly repetitive. Generator drift in one endpoint can be hard to spot because endpoint 3, 4, 5, and 6 use near-identical field names with different prefixes.
- Audio format fields are interoperability-sensitive. Incorrect `NUMBER_OF_CHANNELS`, sample rate, bit depth, stream type, or stream/channel ID masks can cause missing audio, wrong sample rate, channel swaps, or sink rejection.
- IEC 60958 channel-status fields are subtle. Wrong clock accuracy, word length, sample frequency, source number, CGMS-A, or channel-number masks can create sink-specific failures even when simple stereo PCM works.
- Multichannel fields are user-visible. Pair-mode versus single-mode mistakes, incorrect mute bits, or wrong channel IDs can break surround audio, downmix behavior, or old audio-driver compatibility.
- Sink metadata and audio descriptors feed ELD-like behavior. Bad manufacturer/product IDs, port IDs, display description bytes, SAD descriptor fields, speaker allocation, or lipsync/HBR fields can cause ALSA/HD-audio clients to expose wrong capabilities.
- Status/interrupt fields are side-effect-sensitive. Confusing flag, mask, type, clear, or ack behavior can cause missed enable/disable/format-change notifications or interrupt storms.
- LPIB, timer snapshot, GTC, and wrap-count fields can be timing-sensitive and may be invalid while endpoints are gated, disabled, or in reset.
- Clock-gating and hot-plug audio state can interact with suspend/resume and runtime power management; wrong masks may produce failures only after idle, link retraining, or hotplug cycles.

## Test Signals

Useful validation combines generated-header checks with audio/display behavior on DCN 3.6 hardware:

- Build AMDGPU display support with DCN 3.6 enabled. Missing or renamed constants should fail in DCN36 DMUB, IRQ, resource, register-helper, audio, AFMT, or APG table construction if those fields are referenced.
- Mechanically compare this range against AMD's authoritative DCN 3.6.0 register source and the adjacent `dcn_3_6_0_offset.h` names. Account for the artificial start in endpoint 2 and artificial end in endpoint 6.
- Run static consistency checks that each complete register group has paired `__SHIFT` and `_MASK` definitions once adjacent chunks are considered.
- Exercise HDMI and DisplayPort audio hotplug with EDID/SAD parsing, ELD retrieval through the DRM audio component, connector audio instance assignment, and pin ELD notification.
- Validate stereo PCM and multichannel playback across 2/6/8 channel modes, 44.1/48/96/192 kHz rates where supported, 16/20/24-bit depths, HBR/non-PCM paths, and sink replug/retrain events.
- Check speaker allocation, channel allocation, LFE/downmix behavior, multichannel mute/channel IDs, pair versus single multichannel mode, and IEC 60958 channel-status reporting with a receiver or analyzer.
- Exercise format changes while audio is active and verify format-changed status/interrupt handling, LPIB progress, timer snapshots, and absence of stale endpoint status.
- Run suspend/resume, GPU reset, runtime power management, display off/on, and repeated modeset cycles while monitoring for lost audio, stale ELD, wrong sink capabilities, interrupt floods, or endpoint clock-gating failures.

## Cross-Chunk Notes

The previous chunk contains the beginning of `AZF0ENDPOINT2` converter/pin/audio descriptor definitions. This chunk continues endpoint 2, covers endpoint blocks 3 through 5, and starts endpoint 6. The next chunk continues endpoint 6 and begins endpoint 7. The final per-file research document should reconcile these neighboring chunks before summarizing all Azalia endpoint coverage in `dcn_3_6_0_sh_mask.h`.

### subset-b-002142: lines 59203-61489

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 59203-61489

## Purpose

This chunk is a generated AMD DCN 3.6.0 register shift/mask slice for Azalia/HD-audio endpoint register fields. It contains no executable C logic; its public surface is C preprocessor constants that give bit positions and masks for fields inside DCN 3.6 audio codec endpoint registers. Driver code combines these constants with the companion register-offset header to pack, extract, and update individual MMIO fields without repeating literal bit layouts.

The requested range contains 2,027 `#define` entries: 1,015 `__SHIFT` constants and 1,012 `_MASK` constants. The range is not a semantic hardware boundary. It starts in the middle of `AZF0ENDPOINT6_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_1`, covers the rest of endpoint 6's pin/audio-status tail, all of output endpoint 7, all of input endpoints 0 through 5, and ends in the middle of input endpoint 6's digital-converter control group. Adjacent chunks are required to recover the complete endpoint 6 and input endpoint 6 register groups.

Although the repository path is under a `ceph-client` mirror, this source is AMDGPU display hardware metadata. It does not implement Ceph, storage, or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocation paths, locks, callbacks, or direct I/O routines in this line range. The only API is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the low-bit position of a field within a 32-bit register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate or preserve that field in read/modify/write register operations.

The main macro families in this chunk are:

- `AZF0ENDPOINT6_*`: the tail of output endpoint 6. This begins with IEC 60958 channel-status override fields for clock accuracy, word length, sampling frequency, original sampling frequency, sample-frequency coefficient, MPEG surround information, CGMS-A, and channel-number fields. It then defines association information, digital-output activity, LPIB snapshot/LPIB/timer snapshot, coding type, format-change status and response, wireless-display identification, remote keepalive, audio enable status, audio enabled/disabled/format-changed interrupt status, and endpoint fine-grain clock-gating reporting disable.
- `AZF0ENDPOINT7_*`: a full output endpoint register block. It includes converter audio-widget capabilities, converter format programming, channel/stream ID, digital-converter bits (`DIGEN`, validity, VCFG, pre-emphasis, copyright, non-audio, professional, level, category code, keepalive), stream formats, supported sample-size/rate capabilities, stripe control, ramp rate, GTC embedding and counter-delta limits, pin widget capabilities, pin capability bits, unsolicited response controls, pin sense, widget control, speaker/channel mapping, ACP data, audio descriptors 0 through 13, multichannel enable fields, lipsync, HBR, sink information, hot-plug/audio-enabled state, forced unsolicited response payload, configuration default fields, multichannel mode, IEC 60958 channel-status overrides, association info, output status, LPIB state, coding type, format-change signaling, wireless-display identification, remote keepalive, audio enable/disable/format-change interrupt status, and endpoint FGCG reporting disable.
- `AZF0INPUTENDPOINT0_*` through `AZF0INPUTENDPOINT5_*`: six complete input endpoint register blocks. Each block defines input-converter widget capabilities, input converter format, channel/stream ID, digital-converter fields, stream format/rate capability fields, input-pin widget capabilities, input-pin capabilities, unsolicited response control, input pin-sense response, widget control, multichannel enable and multichannel enable2 fields, HBR response, channel allocation, hot-plug control, forced unsolicited response payload, configuration default fields, LPIB snapshot/LPIB/timer snapshot, input status control, and received infoframe fields.
- `AZF0INPUTENDPOINT6_*`: the beginning of input endpoint 6. This chunk covers its converter widget capabilities, converter format, channel/stream ID, and most of the digital-converter control fields before the line range ends. The stream-format, supported-size/rate, and pin-side fields continue in the next chunk.

The register families are mechanically repeated per endpoint instance. Output endpoint 7 mirrors the same conceptual layout used by earlier output endpoints, and input endpoints 0 through 5 share the same field layout with only the endpoint instance number changing.

## Control Flow

This header has no runtime control flow. The effective runtime flow is in consumers:

1. DCN 3.6 display code includes `dcn_3_6_0_offset.h` and this `dcn_3_6_0_sh_mask.h` file.
2. Register-table macros token-paste register and field names into offset, shift, and mask tables for DCN 3.6 blocks.
3. AMDGPU display and audio-related paths use register helper macros such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` to access the Azalia endpoint MMIO fields described here.
4. Hardware and firmware consume the resulting register state to advertise codec capabilities, configure audio stream formats, route audio channels, handle hot-plug and unsolicited-response events, report pin/converter status, and synchronize audio buffer position snapshots.

The macros do not encode ordering rules. Consumers remain responsible for programming converter format before enabling a stream, aligning channel/stream IDs with the active display/audio pipe, using HBR and multichannel fields only when supported, coordinating hot-plug and audio enable state with display link state, and acknowledging or masking interrupt/status bits according to hardware semantics.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes hardware-visible DCN Azalia endpoint state:

- Converter capability and format state: audio channel capabilities, amplifier and format override support, stripe support, processing widget support, unsolicited-response capability, connection-list presence, digital/power-control/LR-swap support, widget delay, type, number of channels, bits per sample, sample-base divisor/multiple/rate, and stream type.
- Digital-converter state: digital enable, validity, validity configuration, pre-emphasis, copyright, non-audio/professional flags, level bit, category code, and keepalive.
- Stream capability state: supported stream formats, supported audio rates, and supported bit depths.
- Output pin state: pin widget capabilities, pin capability bits, unsolicited-response tag and enable, pin sense, widget enable/control, speaker allocation, ACP packet bytes, audio descriptor metadata, multichannel enable/mute/channel-ID fields, lipsync, HBR capability/enable, sink information, hot-plug clock-gating/audio-enable state, forced unsolicited-response payloads, configuration defaults, channel-status override bytes, association info, output-active status, LPIB snapshots, coding type, format-change state, wireless-display identification, remote keepalive, and audio interrupt status.
- Input pin state: input pin capabilities, pin sense, multichannel enable/mute/channel-ID fields, HBR, channel allocation, hot-plug/audio-enabled state, configuration default, input activity, channel layout, input activity and channel-layout/channel-status-infoframe unsolicited-response enables, and incoming audio infoframe channel count/allocation/valid fields.
- Endpoint interrupt/status state: audio enabled, audio disabled, and audio format changed flags, masks, and type bits for output endpoints; input endpoints expose input activity and infoframe-change signaling through their input status control fields.

Persistence is hardware-defined. Configuration fields generally remain until reprogrammed by modeset, hot-plug handling, audio stream setup, power-gating, suspend/resume, GPU reset, or ASIC reset paths. Status, snapshot, interrupt, and forced-response fields may be read-only, sticky, write-one-to-clear, self-clearing, or valid only while the endpoint block is powered and clocked. This generated shift/mask header does not identify those access semantics; the register specification and consuming driver code must supply them.

## Dependencies And Integration Points

The chunk depends on generated register naming staying synchronized across the DCN 3.6 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h` supplies the matching register offsets for the field names defined here.
- Other DCN 3.6 generated headers such as enum and default-value tables may provide symbolic values or reset expectations for the same Azalia fields.
- AMDGPU display resource, IRQ, DMUB, link, and audio/display integration code use the generated DCN 3.6 offset and mask headers through register helper tables.
- HDMI/DisplayPort audio flows depend on these fields indirectly when exposing an HDA codec to the OS, reporting sink capabilities from ELD/infoframe-like metadata, programming sample rate/word length/channel allocation, handling hot-plug audio enablement, and supporting HBR or multichannel playback/capture.
- Firmware and hardware integrations may rely on the same endpoint state for unsolicited responses, GTC timestamp embedding, LPIB snapshots, remote keepalive, and endpoint clock-gating behavior.

Important cross-file consistency is with the matching offset header. A field mask without the matching register offset, or an offset table entry paired with the wrong instance prefix, can compile in some macro paths but access the wrong endpoint or bitfield at runtime.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong mask or shift compiles cleanly and can corrupt neighboring MMIO fields, especially in dense format, channel ID, channel-status, and interrupt/status registers.
- The file is generated. Manual edits risk diverging from AMD's authoritative register database, companion offsets, firmware expectations, and silicon documentation.
- The line boundaries are artificial. This chunk begins after the start of `AZF0ENDPOINT6_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_1` and ends before the rest of `AZF0INPUTENDPOINT6`; complete endpoint analysis must merge adjacent chunks.
- Output and input endpoint blocks are highly repetitive. Generator drift or copy mistakes can affect one endpoint instance while leaving others correct, making endpoint-count and instance-index tests important.
- Audio format fields are user-visible. Incorrect `NUMBER_OF_CHANNELS`, `BITS_PER_SAMPLE`, sample-base divisor/multiple/rate, stream type, or stream ID masks can cause silent audio, wrong sample rate, channel swapping, or HBR/non-HBR negotiation failures.
- IEC 60958 channel-status override masks are interoperability-sensitive. Bad clock-accuracy, word-length, sampling-frequency, original-frequency, CGMS-A, or channel-number masks can confuse HDMI/DP receivers even when audio appears to play.
- Multichannel enable/mute/channel-ID fields are packed densely. Width or shift errors can enable the wrong channel, mute active channels, or route audio to the wrong logical position.
- Hot-plug, unsolicited-response, and audio enable/disable interrupt fields are side-effect-sensitive. Confusing status, mask, type, force, and ack-like bits can cause missed audio hot-plug notifications, stale codec state, interrupt storms, or absent OS-level audio devices.
- LPIB snapshot and timer fields are synchronization-sensitive. Incorrect masks can break audio-position reporting, leading to underruns, drift, or bad A/V sync diagnostics.
- Input endpoint infoframe and input-activity fields are stateful and timing-dependent. A mask error can hide input activity, report stale channel allocation, or mis-handle channel-layout/channel-status infoframe changes.
- Keepalive, remote keepalive, GTC embedding, and FGCG reporting fields can interact with power management and clock gating; bugs may show up only after idle, suspend/resume, remote-display, or link-power transitions.

## Test Signals

Useful validation combines generated-header checks with DCN 3.6 audio/display behavior:

- Build AMDGPU display support with DCN 3.6 enabled. Missing or renamed macros should surface in register-table construction or DCN 3.6 audio/display code that includes the generated headers.
- Mechanically compare this line range against AMD's authoritative DCN 3.6.0 register source and the matching `dcn_3_6_0_offset.h` names. The comparison should account for the chunk starting and ending in the middle of endpoint groups.
- Run static consistency checks that every complete register group has paired `__SHIFT` and `_MASK` definitions across adjacent chunks, and that repeated endpoint instances have expected field parity.
- Exercise HDMI and DisplayPort audio hot-plug, unplug, modeset, suspend/resume, GPU reset, and monitor power-cycle paths while checking that HDA codec nodes appear and disappear correctly.
- Validate audio playback across stereo, multichannel, HBR, multiple sample rates, multiple bit depths, and channel allocations on outputs that map to endpoint 7 and nearby endpoints.
- Validate input endpoint behavior, if supported by the platform path, for input activity detection, channel layout, channel allocation, infoframe valid changes, HBR capability/enablement, and LPIB snapshot reporting.
- Inspect kernel logs, audio diagnostics, and display diagnostics for missing codec devices, bad ELD/sink info, wrong channel maps, audio underruns, A/V sync drift, unexpected unsolicited responses, stuck audio enable/disable/format-change status, and resume-only failures.
- Use register dumps or tracepoints to confirm packed fields such as channel/stream IDs, multichannel enable groups, channel-status override bytes, hot-plug audio-enabled bits, and digital-converter keepalive bits land in the expected bit positions.

## Cross-Chunk Notes

The previous chunk contains the beginning of output endpoint 6, including the start of the channel-status override group whose tail appears here. The next chunk continues input endpoint 6 after the digital-converter control fields and then completes the remaining input endpoint namespace. The final per-file research document should merge these chunks before making whole-file claims about all DCN 3.6 Azalia endpoints or all generated shift/mask definitions.

### subset-b-002143: lines 61490-61940

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 61490-61940

## Purpose

This chunk is the final slice of the generated AMD DCN 3.6.0 register shift/mask header. It contains C preprocessor constants for Azalia/HDA input endpoint register fields, specifically the tail of `AZF0INPUTENDPOINT6_*` and the complete `azf0inputendpoint7_inputendpointind` address block. The macros let AMDGPU display/audio code pack and unpack individual bitfields in indexed Azalia input endpoint registers without embedding raw bit positions in runtime code.

The requested range contains 403 `#define` entries: 200 `__SHIFT` macros, 203 `_MASK` macros, 43 register/address comments, and the closing `#endif` for the whole header. The start boundary is artificial: it begins in the middle of `AZF0INPUTENDPOINT6_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`, so the earlier `DIGEN`, `V`, `VCFG`, `PRE`, `COPY`, `NON_AUDIO`, and `PRO` fields for endpoint 6 are defined in the previous chunk. The end boundary is semantic for the file: it completes endpoint 7 input status/infoframe fields and closes the include guard.

Although the path is inside a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata, not Ceph or distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, locks, or direct MMIO operations in this range. The interface is entirely generated macros following the standard AMD register convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating, inserting, or preserving that field during read/modify/write.

The chunk covers these register groups:

- Endpoint 6 tail fields:
  - Input converter digital converter masks for `L`, `CC`, and `KEEPALIVE`.
  - Input converter stream format and supported size/rate capabilities.
  - Input pin audio widget capabilities and pin capabilities.
  - Unsolicited response tag/enable fields, input pin sense, widget input enable, multichannel enable/mute/channel-id banks for channels 0-7, HBR capability/enable, channel allocation, hot-plug audio enable/clock control, forced unsolicited response payload, default pin configuration, LPIB snapshot/LPIB/timer snapshot, input status, and captured infoframe fields.
- Endpoint 7 complete indexed input endpoint block:
  - Converter audio widget capabilities, converter format, channel/stream ID, digital converter control, stream formats, and supported size/rate capabilities.
  - Input pin audio widget capabilities and pin capabilities.
  - The same control/status groups as endpoint 6: unsolicited response, input pin sense, widget control, multichannel enable banks, HBR, channel allocation, hot-plug control, forced unsolicited response, default configuration, LPIB snapshot, LPIB value, timer snapshot, input status control, and infoframe decode.

The companion offset header defines the register addresses and indexed register numbers that match these masks:

- `regAZF0INPUTENDPOINT6_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX` / `DATA` and `regAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX` / `DATA` are the indexed access ports.
- `ixAZF0INPUTENDPOINT6_*` and `ixAZF0INPUTENDPOINT7_*` provide the indirect register indices, including converter parameter/control indices `0x0001` through `0x0006`, pin control indices `0x0020` through `0x0038`, and status/infoframe indices `0x0053` through `0x0068`.

## Control Flow

This header has no runtime control flow. Its control-flow role is indirect:

1. DCN 3.6 display/audio code includes `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h`.
2. Register-list macros token-paste register and field names into typed tables for display resources, audio blocks, interrupt service setup, and DMUB support.
3. Runtime helpers use those tables with register access macros such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.
4. For Azalia indexed registers, software writes an endpoint index register, reads or writes the endpoint data register, then applies these shifts and masks to interpret or update the selected field.

The macros do not enforce sequencing. Consumers still need to follow HDA/Azalia rules for converter programming, stream ID assignment, channel allocation, HBR setup, unsolicited response enablement, LPIB snapshot locking, hot-plug/audio-enable state, and infoframe/status sampling.

## State And Persistence Behavior

This chunk stores no software state and persists nothing directly. It describes hardware-visible state in DCN 3.6 Azalia input endpoint registers:

- Audio capability state: widget capabilities, pin capabilities, supported stream formats, sample-rate capabilities, bit-depth capabilities, HDMI/DP capability bits, power-control capability, and HBR support.
- Stream programming state: number of channels, bits per sample, sample base rate/divisor/multiple, stream type, channel ID, stream ID, digital converter status/control flags, channel allocation, and multichannel enable/mute/channel IDs.
- Hot-plug and notification state: unsolicited response tag/enable, forced unsolicited response payload, input activity unsolicited-response enable, channel-layout/channel-status infoframe change enable, and hot-plug audio enable/clock bits.
- Status and sampling state: pin sense, LPIB snapshot lock, cyclic buffer wrap count, LPIB value, LPIB timer snapshot, input activity, channel layout, decoded infoframe channel count/allocation/byte 5, and infoframe-valid flag.
- Default pin configuration state: sequence, association, misc, color, connection type, default device, location, and port connectivity fields.

Persistence is hardware-defined. Capability registers are typically read-only descriptions. Control fields generally persist until rewritten by a modeset/audio reconfiguration, hot-plug handling, suspend/resume, GPU reset, or ASIC reset. Status, snapshot, force, unsolicited response, and infoframe-valid fields may be read-only, sticky, self-clearing, write-one-to-clear, sampled only after a lock bit, or valid only while the audio endpoint and related display engine are powered and clocked. This generated header does not encode access semantics, side effects, or valid programming order.

## Dependencies And Integration Points

The immediate dependency is synchronization with AMD's generated DCN 3.6.0 register database and the matching offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h` supplies the corresponding direct `reg*` indexed access ports and indirect `ix*` register numbers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c` includes the generated offset and shift/mask headers, defines audio register tables with `AUD_COMMON_REG_LIST_RI(id)`, and creates DCE audio objects through `dce_audio_create()`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c` includes the same generated DCN 3.6 headers for DMUB register programming support.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c` includes the same generated headers for DCN 3.6 interrupt setup.
- Shared DCE/DCN audio code in `dce_audio.h` and related implementation files consumes audio register/shift/mask tables rather than spelling most endpoint-specific field names at each call site.

One notable integration detail is that `dcn36_resource.c` allocates `audio_regs[7]` and initializes entries 0 through 6, while `res_cap_dcn36` reports `num_audio = 5`. This chunk includes endpoint 7 generated definitions because the register database contains that block, but normal DCN 3.6 resource construction may not expose every generated endpoint as a runtime audio object.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while causing reads or writes to target the wrong bitfield.
- The file is generated. Manual edits risk diverging from the authoritative register database, the companion offset header, firmware assumptions, and hardware documentation.
- The chunk starts mid-register for endpoint 6, so any completeness check must combine this range with the previous chunk before deciding whether all digital converter fields have paired shifts and masks.
- Endpoint 6 and endpoint 7 groups are mechanically similar. Generator drift or copy errors can affect only one endpoint while adjacent endpoint smoke tests still pass.
- Indexed-register access is sensitive to pairing the correct endpoint index/data ports with the correct `ix*` register numbers. A mismatch can read or program a different endpoint than the masks imply.
- Stream format and channel layout fields are interoperability-sensitive. Incorrect masks can produce silent audio, wrong channel mapping, invalid HBR behavior, or bad HDMI/DP audio infoframes.
- Hot-plug, unsolicited response, input activity, and infoframe-change fields can affect interrupt behavior. Confusing enable, force, status, and payload fields can cause missed notifications, repeated notifications, or stale status.
- LPIB snapshot fields can be timing-sensitive. Reading LPIB/timer snapshots without honoring lock and wrap-count behavior can produce inconsistent position reporting.
- Capability masks for HDMI, DP, HBR, supported rates, supported bit depths, and pin capabilities influence feature advertisement. Wrong values may expose unsupported formats or hide valid display-audio modes.

## Test Signals

Useful validation is mostly build, generator-consistency, and hardware audio behavior:

- Build AMDGPU display support with DCN 3.6 enabled. Missing or renamed constants should fail where DCN36 resource, DMUB, IRQ, or audio register tables are constructed.
- Mechanically compare this range against AMD's authoritative DCN 3.6.0 register source and `dcn_3_6_0_offset.h`, including the artificial endpoint 6 boundary at line 61490.
- Check that complete register groups have both `__SHIFT` and `_MASK` definitions when adjacent chunks are considered together.
- Exercise HDMI/DP display audio on DCN 3.6 hardware across hot-plug, modeset, suspend/resume, and GPU reset.
- Validate PCM format negotiation across sample rates, bit depths, channel counts, channel allocation maps, and HBR-capable streams.
- Monitor unsolicited responses, input activity, infoframe-change events, and hot-plug audio enable behavior for missed or repeated notifications.
- Read back LPIB, LPIB timer snapshot, cyclic buffer wrap count, input status, and infoframe fields while audio is active to catch stale or incorrectly masked status bits.
