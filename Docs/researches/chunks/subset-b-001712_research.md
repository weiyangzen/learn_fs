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
