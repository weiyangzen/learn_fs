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
