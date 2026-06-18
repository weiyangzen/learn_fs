# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_sh_mask.h lines 11515-15026

## Scope And Purpose

This chunk is a generated AMD DCE 11.2 register shift/mask header section. It contains only C preprocessor constants of the form `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`; there are no functions, structs, enums, storage objects, or executable branches in the mapped range.

The range starts at the tail of `PRESCALE_VALUES_G` and ends after the first macro of `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL7_ENABLE`, so both boundary register groups are partial and need adjacent chunk context for complete per-register documentation. Within those boundaries, the chunk defines bitfield constants for display color management, gamma correction, FIFO error reporting, unpinned graphics plane programming, legacy VGA indexed register compatibility, display pipe arbitration and stutter controls, and a large Azalia/HD Audio controller and codec endpoint block used for HDMI/DisplayPort audio.

## Important APIs, Types, And Macro Families

The public interface is the macro namespace itself. Consumers combine the masks and shifts with register addresses from the sibling DCE 11.2 address header and helper APIs such as `REG_SET_FIELD()`, `REG_GET_FIELD()`, `set_reg_field_value()`, `get_reg_field_value()`, `RREG32()`, `WREG32()`, `dm_read_reg()`, and `dm_write_reg()`.

Important macro families in this chunk include:

- Color management output and denormalization: `PRESCALE_VALUES_G/B`, `COL_MAN_OUTPUT_CSC_CONTROL`, `OUTPUT_CSC_C11_C12_A` through `OUTPUT_CSC_C33_C34_B`, `DENORM_CLAMP_CONTROL`, `DENORM_CLAMP_RANGE_R_CR/G_Y/B_CB`, and `COL_MAN_FP_CONVERTED_FIELD` define prescale bias/scale, output color-space conversion matrix coefficients for A/B banks, clamp mode, per-channel clamp min/max, and converted floating-point field access.
- Gamma correction: `GAMMA_CORR_CONTROL`, `GAMMA_CORR_LUT_INDEX`, `GAMMA_CORR_LUT_DATA`, `GAMMA_CORR_LUT_WRITE_EN_MASK`, and `GAMMA_CORR_CNTLA_*` / `GAMMA_CORR_CNTLB_*` define gamma LUT access and piecewise exponential-region layout for two banks. The region registers pack LUT offsets and segment counts for regions 0 through 15.
- FIFO and input-gamma status: `PACK_FIFO_ERROR` and `OUTPUT_FIFO_ERROR` expose underflow/overflow occurred and acknowledgement fields. `INPUT_GAMMA_LUT_AUTOFILL`, `INPUT_GAMMA_LUT_RW_INDEX`, `INPUT_GAMMA_LUT_SEQ_COLOR`, `INPUT_GAMMA_LUT_PWL_DATA`, `INPUT_GAMMA_LUT_30_COLOR`, `COL_MAN_INPUT_GAMMA_CONTROL1/2`, and `INPUT_GAMMA_BW_OFFSETS_*` define input gamma LUT loading, autofill, mode, exponent/region controls, and black/white offsets.
- Unpinned graphics plane: `UNP_GRPH_ENABLE`, `UNP_GRPH_CONTROL`, `UNP_GRPH_CONTROL_C`, `UNP_GRPH_CONTROL_EXP`, `UNP_GRPH_SWAP_CNTL`, luma/chroma primary and secondary surface address registers, high-address registers, bottom-field addresses, pitch, x/y offsets, start/end coordinates, `UNP_GRPH_UPDATE`, in-use address readbacks, `UNP_DVMM_PTE_CONTROL`, interrupt status/control, stereosync flip, flip control, CRC, line-buffer gap, rotation, debug, and test debug registers describe a graphics/video scanout path with separate luma/chroma programming and synchronized update behavior.
- Legacy VGA register compatibility: `GENMO_*`, `GENENB`, `GENFC_*`, `GENS*`, DAC palette registers, `SEQ*`, `CRT*`, `GRA*`, `ATTR*`, `VGA_RENDER_CONTROL`, `VGA_SOURCE_SELECT`, `VGA_SEQUENCER_RESET_CONTROL`, `VGA_MODE_CONTROL`, `VGA_SURFACE_PITCH_SELECT`, VGA memory/base/dispbuf address fields, `VGA_HDP_CONTROL`, `VGA_CACHE_CONTROL`, `D1VGA_CONTROL` through `D6VGA_CONTROL`, and VGA status, interrupt, clear, main-control, test, debug, and page-address fields map legacy VGA state into modern display hardware.
- DAC and display pipe gateway controls: `BPHYC_DAC_MACRO_CNTL` and `BPHYC_DAC_AUTO_CALIB_CONTROL` define analog DAC macro and calibration fields. `DPG_PIPE_ARBITRATION_CONTROL1/2`, `DPG_WATERMARK_MASK_CONTROL`, `DPG_PIPE_URGENCY_CONTROL`, `DPG_PIPE_DPM_CONTROL`, `DPG_PIPE_STUTTER_CONTROL`, `DPG_PIPE_NB_PSTATE_CHANGE_CONTROL`, `DPG_PIPE_STUTTER_CONTROL_NONLPTCH`, and debug/test registers define display pipe arbitration, watermarks, urgency, DPM, memory stutter, NB p-state changes, and repeater/check preprocessor controls.
- Virtual or per-viewport display pipe gateway controls: `DPGV0_*` and `DPGV1_*` mirror the DPG arbitration, watermark, urgency, DPM, stutter, NB p-state, repeater, hardware debug, and check preprocessor fields for two related DPGV instances.
- Azalia immediate command and codec identity: `AZROOT_IMMEDIATE_COMMAND_OUTPUT_INTERFACE_*`, `AZENDPOINT_IMMEDIATE_COMMAND_OUTPUT_INTERFACE_*`, `AZENDPOINT_IMMEDIATE_COMMAND_INPUT_INTERFACE_*`, and `IMMEDIATE_COMMAND_*` fields define HDA immediate command input/output index/data/status. `AZALIA_F2_CODEC_ROOT_PARAMETER_*`, `AZALIA_F2_CODEC_FUNCTION_*`, `AZALIA_F0_CODEC_ROOT_PARAMETER_*`, and `AZALIA_F0_CODEC_FUNCTION_*` define root/function vendor, revision, subordinate node, group type, supported rates, formats, power states, reset, subsystem ID, and converter synchronization.
- Azalia global controller, DMA, CORB/RIRB, and stream descriptors: `GLOBAL_CAPABILITIES`, version, payload capability, `GLOBAL_CONTROL`, wake/status registers, `INTERRUPT_CONTROL`, `INTERRUPT_STATUS`, `WALL_CLOCK_COUNTER`, `STREAM_SYNCHRONIZATION`, CORB/RIRB base pointers, read/write pointers, control/status/size, DMA position base, and output stream descriptor control/status/format/BDL/LPIB fields describe the HDA controller command/response rings and audio DMA stream machinery.
- Azalia output converter and pin widgets: `AZALIA_F2_CODEC_CONVERTER_*`, `AZALIA_F2_CODEC_PIN_*`, `AZALIA_F0_CODEC_CONVERTER_*`, `AZALIA_F0_CODEC_PIN_*`, audio descriptor registers, sink description registers, channel/speaker allocation, multichannel enable/mute/channel ID, lipsync, HBR, sink info, hot-plug control, unsolicited response force, channel-status override, LPIB snapshots, format-changed state, wireless display identification, remote keepalive, and audio enable/format interrupt status describe HDMI/DP audio presentation and ELD-like sink metadata paths.
- Azalia input converter and input pin widgets: `AZALIA_F0_CODEC_INPUT_CONVERTER_*`, `AZALIA_F0_CODEC_INPUT_PIN_*`, `AZALIA_F2_CODEC_INPUT_CONVERTER_*`, and `AZALIA_F2_CODEC_INPUT_PIN_*` define input converter capabilities, format, channel stream ID, digital converter status, input pin capabilities, unsolicited responses, pin sense, widget controls, multichannel input mapping, HBR, channel allocation, input status, infoframe, LPIB, and timer snapshots. The chunk ends before all fields for `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL7_ENABLE` are present.
- Azalia debug, clock, CRC, and memory power: `AZALIA_CONTROLLER_CLOCK_GATING`, `AZALIA_AUDIO_DTO`, `AZALIA_SCLK_CONTROL`, underflow filler samples, data/BDL/CORB/RIRB DMA controls, cyclic buffer sync, output/input payload capability, stream arbiter control, controller debug, `AZALIA_MEM_PWR_CTRL`, `AZALIA_MEM_PWR_STATUS`, `DCI_PG_DEBUG_CONFIG`, input/output CRC control/result/channel registers, latency counters, stream index/data/debug, and test debug registers provide low-level diagnostics, clocking, DMA control, and power-state observability.

## Control Flow And Data Flow

This header chunk has no runtime control flow. Its data flow is compile-time substitution into register access code. A caller reads or builds a 32-bit MMIO value, inserts a field by masking and shifting, writes it to a DCE 11.2 register address, and later reads status fields with the inverse mask/shift operation.

The implied hardware flows are:

- Color and gamma programming flows write prescale, CSC, denormal clamp, gamma LUT index/data, and gamma region fields as part of display pipe color setup. A/B coefficient and gamma banks suggest double-buffered or alternate-bank programming where software can prepare one bank while another is active, depending on the surrounding display block sequencing.
- FIFO error flows read occurred bits and write acknowledgement bits for pack and output FIFO underflow/overflow handling. These fields are diagnostic and recovery points for display underflow or packing faults.
- UNP graphics flows program format, tiling, stereo, surface addresses, chroma/luma addresses, pitch, offsets, and rectangle coordinates, then use update-lock, pending, flip, stereosync, and interrupt fields to commit scanout changes coherently.
- VGA flows expose legacy indexed VGA registers and modern routing controls. Driver code can select source pipes, enable/disable VGA memory, control sequencer reset, map aperture page addresses, and observe/clear VGA access and interrupt status.
- DPG and DPGV flows set arbitration, urgency watermarks, DPM, stutter, and p-state change controls for display memory access. The legacy Vegam powerplay code reads `DPG_PIPE_STUTTER_CONTROL.STUTTER_ENABLE` when deciding whether an MCLK level can enable stutter mode.
- Azalia/HDA flows configure global controller capabilities and control, command output and response input rings, immediate command transactions, stream descriptor DMA, codec converter/pin capabilities, channel allocation, HBR and multichannel modes, sink metadata, LPIB snapshots, infoframe status, unsolicited responses, clocking, CRC, latency counters, and memory power states.

## State And Persistence Behavior

The header stores no software state. The mutable and persistent state lives in DCE 11.2 MMIO registers, codec widget register files, HDA DMA rings, display pipe shadow/update registers, and hardware status latches.

State classes represented in the chunk include:

- Persistent display programming: output CSC matrices, prescale values, denormal clamp ranges, gamma LUT entries/regions, UNP surface addresses, pitch, offsets, format/tile settings, DPG watermarks, and stutter/DPM controls remain effective until rewritten, reset, or power-gated.
- Shadowed or synchronized update state: `UNP_GRPH_UPDATE`, flip control, stereosync flip, surface-in-use readbacks, and related pending/lock/enable fields participate in safe display updates and expose which programmed address is currently active.
- Latched error and interrupt state: pack/output FIFO error occurred/ack fields, UNP graphics interrupt status/control, VGA status/interrupt/clear registers, HDA interrupt control/status, audio enable/disable/format-changed interrupt status, unsolicited response fields, input activity/status fields, CRC results, and hot-plug controls represent event state that software must acknowledge or clear with the correct semantics.
- DMA and ring state: CORB/RIRB lower and upper base addresses, read/write pointers, sizes, controls, response interrupt count, DMA position buffer base, output stream descriptor BDL/LPIB/CBL/LVI/FIFO/format fields, and cyclic buffer snapshots describe persistent HDA controller state shared between the GPU display/audio block and the host audio driver path.
- Hardware-derived observability: LPIB timer snapshots, wall clock, GTC delta counters, CRC channel/result registers, stream latency counters, memory power status, controller debug, VGA/debug data, DPG/DPGV status, and input infoframe fields are readback and diagnostic state rather than configuration-only data.

Wrong masks or shifts can persist in hardware until a later mode set, audio reconfiguration, suspend/resume, or GPU reset reprograms the affected block. That is especially risky for scanout addresses, color coefficients, watermarks, stutter controls, CORB/RIRB pointers, stream descriptor DMA, and interrupt acknowledgement fields.

## Dependencies And Integration Points

This chunk depends on the rest of the generated DCE 11.2 register headers, especially `dce_11_2_d.h` for register addresses and adjacent portions of `dce_11_2_sh_mask.h` for complete register groups at the chunk boundaries. It also relies on the AMDGPU/DC register helper idiom where field names are expanded into `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`.

Observed local include and use points for the DCE 11.2 header family include:

- `drivers/gpu/drm/amd/display/dc/dce112/dce112_compressor.c`, which includes `dce_11_2_sh_mask.h` with DCE and GMC address/mask headers for DCE112 framebuffer compression and display memory interface programming.
- `drivers/gpu/drm/amd/display/dc/hwss/dce112/dce112_hwseq.c`, which includes the header for DCE112 hardware sequencing and register field access.
- `drivers/gpu/drm/amd/display/dc/clk_mgr/dce112/dce112_clk_mgr.c` and `drivers/gpu/drm/amd/display/dc/resource/dce112/dce112_resource.c`, which include the header while constructing DCE112 clock and resource objects.
- `drivers/gpu/drm/amd/pm/powerplay/smumgr/vegam_smumgr.c`, which includes `dce_11_2_sh_mask.h` and reads `DPG_PIPE_STUTTER_CONTROL.STUTTER_ENABLE` through `PHM_READ_FIELD()` when populating memory DPM levels.

Broader integration surfaces are:

- DRM/KMS mode setting and DC resource construction for display pipe color, scanout, update, and interrupt behavior.
- AMDGPU power management and SMU table construction for display watermark, stutter, and memory clock decisions.
- HDMI/DisplayPort audio through the GPU's Azalia/HDA controller, including codec widget capabilities, stream DMA, ELD/sink metadata, channel allocation, HBR, unsolicited responses, and LPIB position reporting.
- Legacy VGA handoff, VGA memory aperture control, and VGA-compatible display routing.
- Hardware bring-up, debugfs-style diagnostics, ASIC validation, and failure triage paths that read CRC, FIFO, latency, memory power, debug, and interrupt fields.

## Risks And Edge Cases

The main risk is numeric drift between this generated header and the authoritative DCE 11.2 register database. The C compiler can catch a missing macro but cannot prove that a mask or shift targets the intended hardware bits.

Specific risks in this chunk are:

- Partial chunk boundaries: line 11515 starts after the first `PRESCALE_VALUES_G` fields, and line 15026 contains only the first `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL7_ENABLE` macro. Full conclusions for those registers require adjacent chunks.
- Repeated A/B, F0/F2, input/output, luma/chroma, DPG/DPGV0/DPGV1, D1-D6, and multichannel0-7 layouts are copy-sensitive. A one-field offset error can silently program the wrong color bank, audio function, pin widget, channel ID, or display pipe.
- Fields named `MASK_MASK`, `INT_MASK`, `STATUS`, `CLEAR`, `ACK`, `ENABLE`, and `FORCE` have different write/read semantics. Confusing status, mask, clear, acknowledgement, and enable fields can drop interrupts, leave sticky status uncleared, or create repeated interrupt delivery.
- UNP surface-address and update fields are scanout critical. Wrong high/low address masks, chroma/luma address fields, pitch, tiling, or update-lock bits can produce corrupted frames, stale flips, page faults, or display underflow.
- DPG stutter, watermark, urgency, and NB p-state fields affect memory bandwidth and power behavior. Bad constants can cause underflow, visible corruption, or overly conservative power-management decisions.
- VGA compatibility fields are globally sensitive because they affect boot console handoff, VGA memory apertures, indexed register access, sequencer reset behavior, and pipe routing.
- Azalia/HDA DMA and command-ring fields are host-interface critical. Incorrect CORB/RIRB/stream descriptor, BDL, LPIB, interrupt, or format fields can break HDMI/DP audio, corrupt command/response flow, misreport playback position, or trigger audio underruns.
- Audio sink and infoframe fields encode externally visible capabilities and channel layout. Wrong masks can advertise invalid channel allocations, HBR capability, speaker allocation, pin configuration, or sink metadata to the audio stack.

## Test Signals

There are no unit tests for this header alone. Useful validation signals are build coverage, generated-header comparison, and hardware integration tests:

- Build AMDGPU/DC configurations that include DCE112 and Vegam powerplay paths. This catches missing or renamed macros and helper expansion failures.
- Compare lines 11515-15026 against the authoritative AMD DCE 11.2 register source or an upstream generated copy, paying special attention to repeated Azalia widget groups, DPG/DPGV mirrors, VGA indexed registers, and the partial boundary registers.
- Exercise DCE112 mode setting with color-management changes: output CSC, denormal clamp, gamma LUT programming, and input gamma modes should produce expected visual output and register readback.
- Exercise plane flips and UNP-style scanout paths where available, including luma/chroma surfaces, pitch/offsets, rotation, CRC, flip interrupts, and surface-in-use readbacks.
- Run display memory pressure, stutter, and MCLK/p-state transition tests while checking DPG watermark, urgency, stutter, and underflow indicators.
- Validate legacy VGA handoff or VGA-compatible paths by checking VGA memory disable/source selection, indexed VGA access, sequencer reset behavior, and VGA status/interrupt clear behavior.
- Exercise HDMI/DisplayPort audio: hotplug, EDID/ELD-like sink metadata, channel allocation, HBR, multichannel mappings, stream start/stop, suspend/resume, LPIB position reporting, CORB/RIRB command response, and interrupt delivery.
- Use CRC, FIFO error, Azalia latency, memory power, debug index/data, and stream debug registers as diagnostic signals during ASIC bring-up or regression testing.
