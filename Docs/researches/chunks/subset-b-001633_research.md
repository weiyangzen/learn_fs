# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 56985-59503

## Scope And Purpose

This chunk is part of AMDGPU's generated DCN 2.0 register field mask/shift header. It contains no executable C logic. Its purpose is to publish compile-time bit layout constants for DCN 2.0 display and display-audio MMIO registers.

Each exposed field follows the generated AMD register-header convention:

- `REGISTER__FIELD__SHIFT` gives the least-significant bit position for a field.
- `REGISTER__FIELD_MASK` gives the already-positioned mask for that field.

The constants are meaningful together with the matching register-address macros in `dcn_2_0_0_offset.h` and with AMD display register helpers such as `SF(...)`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and lower-level MMIO read/write wrappers. The repository path is under a local `ceph-client` source tree, but this file is AMDGPU display-driver hardware metadata and has no Ceph filesystem behavior.

The covered range spans several hardware blocks:

- Tail of the DPP4 color-management (`CM4`) block, including shaper RAMB regions 18-33, shaper/HDR 3D LUT memory power control/status, 3D LUT programming fields, output normalization/offset/scale fields, and CM test-debug index/data.
- DPP4 display performance monitor `DC_PERFMON27`.
- DPP5 top-level DPP control, soft reset, CRC, and host-read controls.
- DPP5 CNVC format-conversion, color keying, alpha LUT, and cursor fields.
- DPP5 DSCL scaler, line-buffer, output-buffer, memory-power, and geometry fields.
- DPP5 color-management (`CM5`) matrix, degamma, blend gamma, shaper, 3D LUT, memory-power, coefficient-format, dealpha, HDR multiplier, and test-debug fields.
- DPP5 display performance monitor `DC_PERFMON28`.
- HDA/Azalia controller, endpoint/root immediate-command windows, input-endpoint command windows, and output stream descriptors for streams 0-3 plus the beginning of stream 4.

## Important APIs, Types, And Macros

There are no functions, structs, enums, storage objects, or runtime APIs in this chunk. The macro namespace is the API surface consumed by generated register-table code.

Important macro families:

- `CM4_CM_SHAPER_RAMB_REGION_20_21` through `CM4_CM_SHAPER_RAMB_REGION_32_33` complete the chunk-local tail of CM4 shaper RAMB region metadata. Each paired-region register packs an even and odd exponential region's LUT offset and segment count. The range begins with the final masks for `CM4_CM_SHAPER_RAMB_REGION_18_19`, whose matching comment and earlier shifts are in the previous chunk.
- `CM4_CM_MEM_PWR_CTRL2`, `CM4_CM_MEM_PWR_STATUS2`, `CM4_CM_3DLUT_*`, and `CM4_CM_TEST_DEBUG_*` describe CM4 shaper/HDR 3D LUT RAM power gating, 3D LUT mode/index/data/write/read status, output normalization and RGB offset/scale, and CM debug access.
- `DC_PERFMON27_*` and `DC_PERFMON28_*` define identical display performance counter layouts for DPP4 and DPP5 perfmon blocks: event selection, counted value type, hardware stop/count-off selection, counter state selector/status pairs, global perfmon enable/start/clear/counting mode, current-value interrupt thresholds and status, and high/low counter reads.
- `DPP_TOP5_DPP_CONTROL`, `DPP_TOP5_DPP_SOFT_RESET`, `DPP_TOP5_DPP_CRC_*`, and `DPP_TOP5_HOST_READ_CONTROL` expose DPP5 enable/output mux, per-subblock soft-reset, CRC control/result fields, and host read-enable fields for scaler, line buffer, gamut remap, cursor, input/output CSC, 3D LUT, shaper, degamma, format-converter, and output-buffer paths.
- `CNVC_CFG5_*` exposes DPP5 format conversion state: surface pixel format, component expansion, output CSC mode, floating-point bias/scale, color-keyer enable/alpha/RGB low-high bounds, and 2-bit alpha LUT entries.
- `CNVC_CUR5_CURSOR0_*` exposes cursor enable, expansion, pixel inversion, ROM/mode, pixel alpha modulation, update-pending status, cursor colors, and floating-point cursor scale/bias.
- `DSCL5_*` exposes DPP5 scaler and line-buffer layout: coefficient RAM tap select/data, scaler mode, tap counts, 2-tap hardcoded/sharp controls, manual replication, horizontal/vertical luma and chroma ratios/init phases, black offsets, update pending, autocal pipe selection, overscan, OTG blanking mirrors, recout/MPC sizes, line-buffer memory format/partitioning/counters, DSCL memory power controls/status, output-buffer controls, and output-buffer memory power state.
- `CM5_CM_*` is the largest group. It covers CM bypass/update status, input CSC and gamut remap coefficient banks A/B, bias fields, degamma control/LUT/index/write-enable plus RAM A/B region tables, blend-gamma control/LUT/index/write-enable plus RAM A/B region tables, HDR multiplier, shared/blend/shaper/3D-LUT memory-power controls and status, dealpha enable, coefficient format selections, shaper control/offset/scale/LUT/write-enable plus RAM A/B regions, 3D LUT mode/index/data/30-bit/write-read control/output normalization/RGB output offset-scale, and CM test-debug index/data.
- `CORB_*`, `RIRB_*`, `IMMEDIATE_*`, `DMA_POSITION_*`, and `WALL_CLOCK_COUNTER_ALIAS` expose HDA/Azalia controller command/response ring, immediate command/response, DMA position buffer, and wall-clock fields.
- `AZENDPOINT_*`, `AZROOT_*`, and `AZENDPOINT_IMMEDIATE_COMMAND_INPUT_*` expose endpoint/root immediate-command index/data windows.
- `AZSTREAM[0-3]_OUTPUT_STREAM_DESCRIPTOR_*` define complete HDA output stream descriptor layouts: control/status, link position, cyclic buffer length, last valid index, FIFO size, stream format, buffer descriptor list lower/upper base addresses, and link-position alias.
- `AZSTREAM4_OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS` begins at the end of the chunk and includes control/status shifts plus the first masks through `TRAFFIC_PRIORITY_MASK`; remaining stream 4 masks and descriptor fields are in the following chunk.

## Control Flow

This chunk has no runtime control flow. It is declarative bitfield metadata.

Runtime control appears in AMDGPU/DCN consumers that include `dcn_2_0_0_sh_mask.h` and pair these masks/shifts with offset macros:

1. DCN20 resource and hardware-object setup code builds register, shift, and mask tables for display pipes, color modules, scalers, performance monitors, IRQ/GPIO, clock, DMUB, and related blocks.
2. DC color-management code programs degamma, shaper, 3D LUT, gamut remap, input CSC, blend gamma, and related coefficient/register RAM windows by selecting indices or RAM banks, writing data fields, and checking update/config status bits.
3. DPP/scaler code programs DSCL ratios, initialization phases, taps, coefficient RAMs, line-buffer partitions, recout/MPC sizes, overscan, and memory-power controls during plane programming and modeset.
4. Cursor and CNVC code programs cursor state, surface format conversion, alpha/color-keying, floating-point scale/bias, and component format controls as planes are enabled or updated.
5. Perfmon/debug code selects events and counter modes, starts/stops counters, reads high/low counter values, or uses CRC/test-debug registers for diagnostics.
6. HDA/Azalia audio code programs CORB/RIRB DMA rings, immediate commands, stream descriptors, BDL base addresses, cyclic lengths, sample format, stream run/reset, and interrupt/status bits during display audio enablement and teardown.

The header does not enforce sequencing. Consumers must know when fields are double-buffered, read-only, sticky, self-clearing, write-one-to-clear, reset-sensitive, or power-gating dependent. Names such as `*_UPDATE_PENDING`, `*_CONFIG_STATUS`, `*_MEM_PWR_STATE`, `*_SOFT_RESET`, `*_RUN`, `*_RESET`, `*_INTERRUPT_STATUS`, and `*_DMA_ENABLE` identify control-sensitive fields, but access semantics are outside this generated mask header.

## State And Persistence Behavior

The file stores no software state and has no persistence mechanism. The macros describe hardware MMIO state.

The represented hardware state includes:

- CM4 and CM5 color pipeline state: input CSC coefficients, gamut remap matrices, bias, degamma LUTs, blend gamma LUTs, shaper LUTs, 3D LUT data, RGB offsets/scales, HDR multiplier, coefficient formats, dealpha enablement, and bypass/update status.
- DPP5 scaler and composition state: scale ratios, filter phases, coefficient RAM contents, tap modes, line-buffer memory configuration and counters, recout/MPC dimensions, overscan, blanking mirror values, output-buffer controls, and DPP enable/reset/output muxing.
- Plane format and cursor state: CNVC pixel format, component expansion, output CSC mode, floating-point conversion bias/scale, color keying, alpha LUT entries, cursor enable/mode/colors/scale/bias, and cursor update-pending status.
- Diagnostic and monitoring state: DPP CRC values/control, CM test-debug windows, and DPP4/DPP5 perfmon event/counter/cvalue interrupt registers.
- Power-gating state: CM shared/blend/shaper/HDR3DLUT memory power controls/status, DSCL LUT/line-buffer group memory power controls/status, and OBUF memory power controls/status.
- HDA/Azalia state: command output/response input ring pointers, ring base addresses, DMA enable bits, immediate command busy/result status, DMA position buffer base, wall clock, endpoint/root immediate-command windows, stream run/reset/interrupt enables/status, stream number, FIFO readiness/errors, cyclic buffer length, last valid descriptor index, stream format, BDL addresses, and link-position counters.

Persistence is hardware-specific. Some fields are persistent programming knobs until rewritten, modeset, power transition, suspend/resume, or ASIC reset. Other fields are live counters, snapshots, interrupt status bits, command/status handshakes, or power-state/status readbacks. This generated header does not encode reset values, volatility, read/write permissions, or side effects.

## Dependencies And Integration Points

This chunk depends on the generated AMD DCN 2.0 register-header set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h` supplies matching register addresses/base indices.
- Other generated DCN/DCE enum headers supply legal symbolic values for many fields.
- AMD display/DC register helper macros convert the mask/shift constants into read-modify-write operations and per-block register tables.

Direct include points for `dcn_2_0_0_sh_mask.h` found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

Practical integration points are DRM plane programming, DCN20 resource construction, DPP/scaler setup, color-management application, HDR/3D-LUT programming, cursor updates, perf counter sampling, DPP CRC/debug collection, memory power-gating transitions, display audio command/stream setup, hotplug/modeset audio enablement, and suspend/resume restore paths.

## Risks And Edge Cases

- These macros are hardware ABI. A wrong mask or shift can compile cleanly while updating the wrong bits in a live display or audio register.
- The chunk boundaries are artificial. It starts inside `CM4_CM_SHAPER_RAMB_REGION_18_19` and ends inside `AZSTREAM4_OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS`; adjacent chunks are required for complete source-file coverage.
- The repeated region tables are easy to corrupt manually. `*_RAMA_REGION_*` and `*_RAMB_REGION_*` entries pack two regions per register with fixed offsets and segment-count fields. Off-by-one region drift can affect only part of a LUT and be visible as color banding or incorrect transfer functions.
- CM5 color-management fields are color-critical. Bad CSC/gamut/remap/coefficient-format, degamma, blend-gamma, shaper, or 3D-LUT masks can cause wrong color conversion, incorrect HDR behavior, clipping, banding, or failure to update the intended RAM bank.
- DSCL fields are timing and image-quality sensitive. Incorrect ratios, init phases, taps, coefficient RAM selection, line-buffer partitioning, recout/MPC sizes, or update-pending handling can produce scaling artifacts, underflow, black frames, or pipe-update failures.
- Memory power fields interact with register availability. Forcing or disabling CM, DSCL, line-buffer, OBUF, shaper, blend-gamma, or HDR3DLUT memory power at the wrong time can lose programmed tables or cause reads/status polling to misbehave.
- Perfmon and debug registers can be status/clear sensitive. Wrong `*_INT_STATUS`, clear, active, restart, or counter-selection masks can hide real performance events or create misleading debug captures.
- HDA/Azalia controller and stream fields are side-effect heavy. CORB/RIRB pointer reset, DMA enable, immediate command busy/result-valid, stream reset/run, interrupt status, descriptor error, FIFO error, and BDL base fields must be sequenced with audio hardware expectations. Bad masks can cause missing HDMI/DP audio, stuck command rings, descriptor DMA faults, or interrupt storms.
- Stream descriptors repeat across `AZSTREAM0` through `AZSTREAM4`. Instance suffix drift or copied masks from a neighboring stream could affect only one audio stream and evade broad compile-only checks.

## Test Signals

Useful validation combines generated-header consistency, compile coverage, and hardware behavior:

- Build AMDGPU/DC with DCN20 support enabled; missing or renamed macros should fail in DCN20 resource, IRQ, GPIO, clock-manager, DMUB, GMC, and display hardware-object paths.
- Check generated mask/shift consistency against AMD's register database and the matching `dcn_2_0_0_offset.h` entries. For each field, `(mask >> shift)` should match the intended field width and should not overlap unrelated fields in the same register.
- Compare repeated DPP4/DPP5, CM4/CM5, perfmon, DSCL, and AZ stream blocks against adjacent instances and adjacent ASIC families where hardware is expected to remain compatible.
- Exercise DCN20 modesets with scaling enabled and disabled, luma/chroma scaling, cursor updates, color keying, format conversion, SDR/HDR-like color-management changes, 3D LUT programming, gamma/shaper updates, blank/unblank, hotplug, and suspend/resume.
- Validate visual signals: no black screens, no scaling artifacts, no color shifts, no banding from LUT region programming, correct cursor rendering, correct alpha/color-key behavior, and stable page-flip/vblank completion.
- Validate diagnostics: DPP CRC values, CM test-debug access, `DC_PERFMON27`/`DC_PERFMON28` counter programming and reads, update-pending/config-status polling, and absence of unexpected underflow or power-gating errors in kernel logs.
- Validate HDMI/DP audio: CORB/RIRB command handling, immediate command completion, stream reset/run sequencing, BDL programming, cyclic buffer length/last valid index handling, link-position reporting, stereo and multichannel sample formats, hotplug audio recovery, and suspend/resume audio restore.
- Negative signals include compile failures in generated register tables, silent color mismatch, LUT update failures, scaler underflow, stuck update-pending bits, perf counters that never start/stop, command ring timeouts, descriptor/FIFO errors, missing audio after modeset, or interrupt storms.

## Cross-Chunk Notes

Earlier chunks contain the start of the CM4 shaper RAMB region list and preceding DPP4 color-management definitions. Later chunks continue the `AZSTREAM4_OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS` masks and the rest of stream 4 plus subsequent HDA/display register metadata. The final per-file research document should treat this chunk as one slice of a generated DCN 2.0 hardware register-layout contract, not as standalone algorithmic code.
