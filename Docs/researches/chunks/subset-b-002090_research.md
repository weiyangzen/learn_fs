# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 6586-8803

## Purpose

This chunk is generated AMD DCN 3.5.1 register field metadata. It contains no executable C logic; it publishes `#define` constants for bit shifts and masks used by AMDGPU display code when packing, updating, and reading MMIO register fields. The companion DCN 3.5.1 offset header supplies register addresses, while this file supplies the layout of fields inside each register.

The assigned range starts in the DCCG/OTG clock-control area at `DP_DTO1_PHASE`, covers pixel-rate DTOs, DPP/DSC/DTBCLK/audio DTO controls, symbol and HDMI stream clocks, DCCG resets and vsync counter fields, then moves through Azalia HDMI/DP audio codec function, converter, pin, channel-status, and infoframe fields. The later part covers display performance monitor blocks 0 through 2, DCPG power-gating domains and interrupts, DMU/SMU/Z-state control, GPU timer readback/start-position selectors, and the first twenty display interrupt status chain registers through the beginning of `DISP_INTERRUPT_STATUS_CONTINUE19` masks.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display-driver hardware metadata. It is unrelated to Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation sites, or locks in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position of a field inside a hardware register.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field.
- Numeric instance suffixes, such as `OTG2`, `DP_DTO3`, `DC_PERFMON1`, `DOMAIN18`, and `DISP_INTERRUPT_STATUS_CONTINUE16`, expose repeated hardware block instances.

Major macro families in this slice:

- Pixel-rate and display-clock generation: `DP_DTO1/2/3_PHASE`, `DP_DTO1/2/3_MODULO`, `OTG1/2/3_PHYPLL_PIXEL_RATE_CNTL`, `OTG2/3_PIXEL_RATE_CNTL`, `DPPCLK_CGTT_BLK_CTRL_REG`, `DPPCLK0..3_DTO_PARAM`, `DPPCLK_DTO_CTRL`, `DSCCLK_DTO_CTRL`, `DTBCLK_DTO0..3_PHASE`, `DTBCLK_DTO0..3_MODULO`, `DTBCLK_DTO_DBUF_EN`, `DENTIST_DISPCLK_CNTL`, and `HDMISTREAMCLK0_DTO_PARAM`.
- DCCG clock, reset, and measurement controls: `SYMCLKA..E_CLOCK_ENABLE`, `FORCE_SYMCLK_DISABLE`, `DCCG_GATE_DISABLE_CNTL3`, `DCCG_SOFT_RESET`, `DCCG_CAC_STATUS2`, `DCCG_AUDIO_DTO_SOURCE`, `DCCG_AUDIO_DTO0/1_PHASE`, `DCCG_AUDIO_DTO0/1_MODULE`, `DCCG_AUDIO_DTBCLK_DTO_PHASE/MODULO`, `DCCG_VSYNC_CNT_CTRL`, `DCCG_VSYNC_CNT_INT_CTRL`, and `DCCG_VSYNC_OTG0..5_LATCH_VALUE`.
- HDMI character and stream clock selection: `HDMICHARCLK0_CLOCK_CNTL` and `HDMISTREAMCLK_CNTL`, plus gate-disable bits for six HDMI stream clocks and multiple `SYMCLK32` root/SE/LE gates.
- Azalia/HDA HDMI/DP audio codec metadata: `AZALIA_F2_CODEC_ROOT_PARAMETER_*`, function control/parameter registers, output converter controls, output pin controls, IEC 60958 channel-status override registers, LPIB snapshot and timer snapshot registers, audio descriptor and sink-info index/data registers, HBR, lipsync, multichannel enable/mute/channel-id registers, wireless-display identification, remote keepalive, and corresponding input converter/input pin control and capability registers.
- DC performance monitor blocks: `DC_PERFMON0_*`, `DC_PERFMON1_*`, and `DC_PERFMON2_*` cover per-counter event selection, counted-value selection, increment/run-enable mode, control select, state select for counters 0 through 7, perfmon state/report count, count-off interrupt control, clock enable, start/stop trigger selectors, counter interrupt status/ack bits, and low/high value readback fields.
- Display power, firmware, and low-power controls: `DOMAIN0..3_PG_CONFIG/STATUS`, `DOMAIN16..19_PG_CONFIG/STATUS`, `DCPG_INTERRUPT_STATUS`, `DCPG_INTERRUPT_STATUS_2`, `DCPG_INTERRUPT_CONTROL_1`, `DC_IP_REQUEST_CNTL`, `CC_DC_PIPE_DIS`, `DMU_CLK_CNTL`, `SMU_INTERRUPT_CONTROL`, `ZSC_CNTL`, `ZSC_CNTL2`, `DMU_MISC_ALLOW_DS_FORCE`, and `ZSC_STATUS`.
- GPU timer selectors: `DC_GPU_TIMER_START_POSITION_V_UPDATE`, `DC_GPU_TIMER_START_POSITION_VSTARTUP`, `DC_GPU_TIMER_READ`, and `DC_GPU_TIMER_READ_CNTL`.
- Display interrupt status chain: `DISP_INTERRUPT_STATUS` and `DISP_INTERRUPT_STATUS_CONTINUE` through `DISP_INTERRUPT_STATUS_CONTINUE19` define status bits for OPTC underflow, OTG IHC events, vertical interrupts, DIG fast-training/video-disable events, HPD and AUX completion, DIO/RBBMIF/I2C events, DWB/WBSCL and DMCUB events, DMU/SMU/FCH/DMUB events, DCCG/DSC/ABM/DPP/HUBP/OPP/OPTC/MMHUBBUB/AZ perfmon interrupts, HUBP vblank/vline/timeout/flip/flip-away events, DCIO DPCS errors, DCPG power-down interrupts, and Azalia endpoint audio format/enabled/disabled events.

Within lines 6586-8803 there are 198 distinct register names represented by paired or grouped shift/mask macros. The largest families are the display interrupt status chain, Azalia audio codec controls, DC performance monitor blocks, DCCG clock controls, and DCPG power/interrupt controls.

## Control Flow

This header has no runtime control flow. Runtime use is indirect:

1. DCN 3.5.1 display code includes generated offset and shift/mask headers for the ASIC.
2. Register-table macros such as `SR`, `SRI`, `SF`, and block-specific wrappers paste register and field tokens into names from this file.
3. Resource constructors and DMUB register-initialization code populate per-block register-offset, shift, and mask tables for clock generation, audio, perfmon, power-gating, low-power coordination, GPU timer, and interrupt handling.
4. Operational code later uses helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, and polling/wait helpers. Those helpers use this chunk's shifts and masks to preserve unrelated hardware bits while programming DTO ratios, enabling clocks, changing power states, reading status bits, acknowledging interrupts, and selecting timer/perfmon readbacks.

The macros do not encode ordering. The caller remains responsible for hardware sequencing: waiting for DTO or clock status bits, respecting reset ordering, latching vsync counters before reading values, programming audio converter/pin registers consistently with HDA verbs and stream state, acknowledging interrupt bits with the correct write semantics, and synchronizing power-gating/low-power transitions with DMU/SMU firmware.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed GPU state:

- DTO phase/modulo registers and clock-control fields hold display, DP, DPP, DSC, HDMI stream, DTBCLK, and audio clock ratios, enable bits, source selectors, and status/error counters.
- DCCG reset and gate-control fields affect display clock tree reset, symbol-clock availability, stream-clock gating, and audio DTO clock reset behavior.
- Vsync counter fields configure global vsync counting, OTG latch enables, trigger selection, interrupt status/clear bits, and latched OTG counter values.
- Azalia codec fields represent hardware-emulated HDA codec state for HDMI/DP audio: function power state, supported sample sizes/rates, stream/channel IDs, converter format, digital converter flags, pin widget control, unsolicited response settings, pin sense, default configuration, speaker/channel allocation, audio descriptors, sink info, lipsync, high-bit-rate capability, multichannel routing, LPIB snapshots, infoframes, channel status, and format-change notifications.
- Perfmon fields hold programmable event selection, counter mode, active/run status, interrupt enable/status/ack bits, count-off threshold behavior, clock enable, trigger selectors, and current counter values.
- DCPG domain fields expose force-on/power-gate requests and desired/current power-gating FSM state for several display domains; interrupt registers expose power-up/down and wakeup event status/masking for DCPG-controlled domains.
- DMU/SMU/ZSC fields expose display microcontroller clocks, DC-to-SMU interrupts, Z-state allowance, SoC access forcing, deep-sleep forcing, and fence/access status.
- GPU timer fields expose a 32-bit read register and select which timer/start-position value is sampled.
- Display interrupt status fields expose broad hardware event state across display pipes, link encoders, AUX/HPD, perfmon, HUBP/OPP/OPTC, power domains, DCIO, and Azalia endpoints.

Persistence is hardware-defined. Configuration fields usually remain until modeset reprogramming, suspend/resume, power-gating, firmware reset, or ASIC reset. Status, clear, ack, snapshot, latch, interrupt, sticky, and busy/done fields can be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive. This generated mask file does not identify access type, reset value, or side effects.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5.1 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h`, which provides matching register offsets and base indices.
- DCN 3.5.1 resource and register-table setup code under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/`, which includes generated DCN headers and maps field names into resource structures.
- DCCG/display-clock code under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/`, which consumes DTO, clock-source, clock-gating, reset, and vsync counter fields.
- Display audio code under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/` and related audio/hwss paths, which consumes Azalia codec, converter, pin, infoframe, channel-status, HBR, LPIB, and format-change fields for HDMI/DP audio.
- Perfmon and diagnostic code that consumes `DC_PERFMON0..2_*` fields and display interrupt status bits for counter programming and event attribution.
- Power-management and firmware integration paths that use DCPG, DMU, SMU, ZSC, and `CC_DC_PIPE_DIS` fields to coordinate display-domain gating, low-power entry/exit, and DMCUB enablement.
- Interrupt service and DMUB-facing code that maps `DISP_INTERRUPT_STATUS*` fields to display IRQ sources such as HPD/AUX, OTG/OPTC, DIG, HUBP, DCIO, power-domain, and Azalia events.

The main integration pattern is token pasting, so macro spelling is effectively a source-level ABI between generated headers and shared driver tables. Missing or renamed fields tend to break compilation; incorrect numeric masks or shifts can compile successfully and fail only under hardware exercise.

## Risks And Edge Cases

- Generated masks are untyped constants. A wrong shift or mask can silently update neighboring hardware fields and appear as display clock instability, audio failure, missed interrupts, broken power gating, or misleading diagnostics.
- The chunk boundary is artificial. It begins after earlier `OTG1_PIXEL_RATE_CNTL` fields from the previous chunk and ends midway through `DISP_INTERRUPT_STATUS_CONTINUE19`, with only the first seven audio-format-changed masks present. Adjacent chunks are required for a complete file-level view.
- DTO and clock source fields are timing-sensitive. Bad phase/modulo, enable, source-select, or double-buffer-enable masks can produce link-clock mismatch, FIFO errors, unstable pixel rate, incorrect DPP/DSC clocks, or display blanking.
- DCCG reset and gate-disable fields can affect shared clock domains. Incorrect masks can leave symbol, stream, audio, DPP, DSC, or DTB clocks gated or reset while the pipe is active.
- Vsync counter interrupt and clear fields reuse bit positions for status and clear names. Callers must preserve hardware clear semantics; treating them as ordinary read/write bits can drop interrupts or leave stale latches.
- Azalia codec and pin-control fields are exposed through HDA/HDMI/DP audio behavior. Incorrect stream-format, channel-id, infoframe, speaker-allocation, HBR, LPIB snapshot, or format-change masks can cause no-audio, wrong channel mapping, bad sample-rate reporting, or audio/video sync issues.
- IEC 60958 channel-status override fields are small bitfields with explicit override-enable bits. Programming channel status without the matching override can make tests pass in software but not affect transmitted audio metadata.
- Perfmon control/status fields include active, restart, interrupt, count-off, read-select, and ack bits. Wrong masks can hide counter overflow, acknowledge the wrong counter, read a stale high/low value, or produce misleading telemetry.
- DCPG, DMU, SMU, and ZSC fields coordinate firmware-managed low power. Wrong force/gate/fence/status masks can create suspend/resume failures, failed Z-state entry, stuck power-domain transitions, or false wake/fence diagnostics.
- The interrupt status chain uses continuation bits at bit 31. Missing the continuation bit or using the wrong register in the chain can cause the driver to miss downstream events such as HUBP vblank/vline, DCIO errors, DCPG power-down, or Azalia endpoint events.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN 3.5.1 support enabled. Token-pasting consumers in resource, DCCG, audio, perfmon, power-management, DMUB, and interrupt code should catch missing or renamed macros.
- Mechanically verify that every `__SHIFT` macro in this line range has the expected matching `_MASK` macro and that each mask aligns with its shift and expected field width. Pay special attention to status/clear pairs with identical shifts and to fields ending at the chunk boundary.
- Diff the chunk against AMD's authoritative DCN 3.5.1 register database and nearby generated headers, especially DCN 3.5.0, when compatibility or intentional deltas are expected.
- Exercise modesets across multiple OTG/DIG instances, including DP and HDMI paths, pixel-clock changes, DSC/DPP clock changes, suspend/resume, hotplug, link retraining, and repeated enable/disable cycles.
- Validate HDMI/DP audio: EDID audio capability parsing, stream format changes, channel allocation, multichannel enable/mute, HBR, lipsync, infoframe/channel-status data, LPIB snapshot readback, and endpoint enabled/disabled/format-change interrupts.
- Exercise DCCG and vsync counter behavior with vertical interrupt tests, latched OTG counter readback, dynamic refresh scenarios, and clock-gating transitions.
- Exercise perfmon programming for all three local DC perfmon blocks, including event selection, counter start/stop triggers, interrupt enable/ack, high/low readback, and overflow/count-off behavior.
- Exercise low-power and power-gating paths: display idle, Z-state entry/exit, DCPG domain power transitions, SMU interrupts, DMU deep-sleep forcing, and suspend/resume while watching for stuck fences or stale sticky status.
- Monitor kernel logs, DC traces, debugfs/register readback, display output, and audio playback for underflows, HPD/AUX interrupt loss, missed vblank/vline events, DCIO errors, DCPG interrupt storms, stuck DTO status, bad clock readback, no-audio, channel mismatch, or power-transition timeouts.

## Cross-Chunk Notes

Adjacent chunks are required for a complete file report. The previous chunk contains earlier DCCG/OTG pixel-rate fields including the start of the OTG1 pixel-rate control sequence. The next chunk continues `DISP_INTERRUPT_STATUS_CONTINUE19` masks, `DISP_INTERRUPT_STATUS_CONTINUE20`, additional interrupt control/status fields, and later generated register families. The merge lane should preserve that this is a chunk-level document for `dcn_3_5_1_sh_mask.h`, not a final per-file report.
