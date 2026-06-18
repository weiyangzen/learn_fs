# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_0_sh_mask.h lines 11768-15235

## Purpose

This chunk is a generated AMD DCE 11.0 register shift/mask header section. It does not implement runtime logic; it publishes preprocessor constants that describe packed bit fields for display-engine MMIO and indirect registers. Driver code combines these `*_MASK` and `*__SHIFT` definitions with register addresses from the companion `dce_11_0_d.h` header and with AMDGPU/DC register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, and audio endpoint accessors.

The covered range starts in the middle of `UNIPHY_POWER_CONTROL`, after the first power/reset fields that are in the prior chunk, and ends in the middle of `DISP_INTERRUPT_STATUS_CONTINUE3`, before the later CRTC3 vertical-interrupt and continuation fields. Within those boundaries it defines several major DCE 11.0 hardware areas:

- `UNIPHY_*` PHY, PLL, spread-spectrum, BIST, test-pattern, TMDS/DP analog, and debug fields.
- `DPG_*`, `DPGV0_*`, and `DPGV1_*` display-pipe memory arbitration, urgent watermark, stutter/self-refresh, DPM, and NB p-state-change fields.
- Large Azalia/HD-audio blocks, including root/function parameters, codec converter and pin widgets, HDMI/DP audio descriptors, stream descriptors, CORB/RIRB command rings, DMA position, CRC/debug/latency counters, clock gating, memory power control, and both F0 and F2 endpoint views.
- `BLND_*`, `WB_*`, and `CNV_*` blender, writeback, converter, CSC, update, underflow, debug, and test CRC fields.
- `DCFE_*` and `DCFEV_*` clock, reset, debug, memory power, DMIFV, and miscellaneous display frontend fields.
- `DC_HPD_*` hot-plug-detect status, control, fast-training, and debounce/toggle filter fields.
- `DCO_SCRATCH*`, `DCE_VCE_CONTROL`, and display interrupt status chain fields through part of `DISP_INTERRUPT_STATUS_CONTINUE3`.

The chunk is therefore a declarative hardware ABI surface for DCE 11 display, audio, power, and interrupt programming. Its correctness matters because users of these macros normally perform read-modify-write operations against hardware registers; a wrong bit position can change a different hardware control without any compiler warning.

## Important APIs, Types, And Functions

There are no C functions, structs, enums, or callable APIs in this chunk. The exported interface is the generated macro namespace. The recurring pattern is:

- `REGISTER__FIELD_MASK`: a constant with the field's bit mask in the 32-bit register value.
- `REGISTER__FIELD__SHIFT`: a constant with the field's least-significant bit position.

The most important macro families in this range are:

- `UNIPHY_POWER_CONTROL`, `UNIPHY_PLL_FBDIV`, `UNIPHY_PLL_CONTROL1`, `UNIPHY_PLL_CONTROL2`, `UNIPHY_PLL_SS_STEP_SIZE`, and `UNIPHY_PLL_SS_CNTL`: PHY bandgap/bias selection, PLL feedback divider, enable/reset/clock controls, loop-filter/bandwidth controls, reference-clock selection, post-divider and reference-divider fields, VCO mode, and spread-spectrum modulation parameters.
- `UNIPHY_DATA_SYNCHRONIZATION`, `UNIPHY_REG_TEST_OUTPUT`, `UNIPHY_ANG_BIST_CNTL`, `UNIPHY_TMDP_REG0` through `UNIPHY_TMDP_REG6`, `UNIPHY_TPG_CONTROL`, `UNIPHY_TPG_SEED`, and `UNIPHY_DEBUG`: synchronization status, PLL lock/unlock test fields, BIST control/error reporting, TMDS/DP analog impedance calibration controls, TX/RX bias and calibration status, test-pattern generation, and debug selects.
- `DPG_PIPE_ARBITRATION_CONTROL*`, `DPG_WATERMARK_MASK_CONTROL`, `DPG_PIPE_URGENCY_CONTROL`, `DPG_PIPE_DPM_CONTROL`, `DPG_PIPE_STUTTER_CONTROL`, `DPG_PIPE_NB_PSTATE_CHANGE_CONTROL`, and `DPG_PIPE_STUTTER_CONTROL_NONLPTCH`: pipe memory timing, watermark masks, urgent thresholds, memory-clock-change policy, stutter/self-refresh behavior, and NB p-state transitions for the base DPG block.
- `DPGV0_*` and `DPGV1_*`: duplicated DPG field layouts for virtual/display-pipe instances 0 and 1, including arbitration, urgency, stutter, DPM, p-state change, repeater, debug, and check/preprocessor controls.
- `AZROOT_*`, `AZENDPOINT_*`, `AZALIA_*`, `AZALIA_F0_*`, and `AZALIA_F2_*`: HD-audio controller and codec register fields. These cover immediate command input/output interfaces, global capability/control/status, interrupt control/status, CORB/RIRB rings, DMA position and output stream descriptors, audio DTO/SCLK controls, memory power controls, CRC engines, latency counters, stream-indexed debug/data registers, and endpoint codec widgets.
- `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13` and `AZALIA_F0/F2_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR*`: HDMI/DP short audio descriptor fields such as maximum channel count, coding type, supported frequencies, sample sizes, max bit rate, and descriptor copy-to-verb controls.
- `SINK_DESCRIPTION0` through `SINK_DESCRIPTION17`, `AZALIA_F0/F2_CODEC_PIN_CONTROL_SINK_INFO*`, and related manufacturer/product/port/speaker/allocation fields: sink identity and audio-capability reporting fields exposed through the codec pin controls.
- `AZALIA_F0/F2_CODEC_*_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, `*_PARAMETER_CAPABILITIES`, `*_CONTROL_CONVERTER_FORMAT`, `*_CONTROL_DIGITAL_CONVERTER`, `*_MULTICHANNEL*`, `*_HBR`, `*_LIPSYNC`, `*_UNSOLICITED_RESPONSE`, and `*_RESPONSE_CONFIGURATION_DEFAULT`: codec function, converter, pin, input converter, and input pin widget fields. These are used by display audio code to advertise audio capabilities, program channel layouts, set stream IDs, enable HBR, report pin sense, and handle hot-plug or format-change responses.
- `BLND_CONTROL`, `BLND_CONTROL2`, `BLND_UPDATE`, `BLND_UNDERFLOW_INTERRUPT`, `BLND_V_UPDATE_LOCK`, and `BLND_REG_UPDATE_STATUS`: blender enable/bypass/global alpha, update locking, pending update status, and data-underflow interrupt fields.
- `WB_ENABLE`, `WB_EC_CONFIG`, `WB_DEBUG_CTRL`, `WB_DBG_MODE`, `WB_HW_DEBUG`, and `WB_SOFT_RESET`: writeback block enable, error-concealment/configuration, debug, and reset fields.
- `CNV_MODE`, `CNV_WINDOW_START`, `CNV_WINDOW_SIZE`, `CNV_UPDATE`, `CNV_SOURCE_SIZE`, `CNV_CSC_*`, `CNV_TEST_*`, and `CNV_INPUT_SELECT`: converter mode, source/window geometry, update, color-space conversion coefficients/clamps/rounding, CRC test output, and input selection fields.
- `DCFE_CLOCK_CONTROL`, `DCFE_SOFT_RESET`, `DCFE_MEM_PWR_CTRL`, `DCFE_MEM_PWR_CTRL2`, `DCFE_MEM_PWR_STATUS`, `DCFEV_*`, and `DCFEV_DMIFV_*`: display frontend clock enable/selection, resets, memory power control/status for line buffers and related memories, vertical-pipe variant controls, and DMIFV clock/memory/debug fields.
- `DC_HPD_INT_STATUS`, `DC_HPD_INT_CONTROL`, `DC_HPD_CONTROL`, `DC_HPD_FAST_TRAIN_CNTL`, and `DC_HPD_TOGGLE_FILT_CNTL`: HPD sense, delayed sense, interrupt status/ack/enable/polarity, RX interrupt handling, connection timers, AUX/fast-training delay controls, and connect/disconnect debounce timers.
- `DCO_SCRATCH0` through `DCO_SCRATCH7`: full-width scratch register masks.
- `DCE_VCE_CONTROL`: video and audio pipe selection fields for VCE/display integration.
- `DISP_INTERRUPT_STATUS`, `DISP_INTERRUPT_STATUS_CONTINUE`, `DISP_INTERRUPT_STATUS_CONTINUE2`, and the beginning of `DISP_INTERRUPT_STATUS_CONTINUE3`: chained display interrupt summary bits for SCL mode changes, blender underflows, line-buffer vline/vblank events, CRTC snapshot/trigger/vsync/DRR events, DIG fast-training or stream-disable events, HPD/RX HPD, AUX completion, I2C completion, DMCU, ABM, writeback/scaler conflicts, external timing sync, and continuation bits.

The matching register address constants are in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_0_d.h`. Examples from that companion file include `mmUNIPHY_POWER_CONTROL`, `mmDPG_PIPE_STUTTER_CONTROL`, `mmDC_HPD_INT_STATUS`, and `mmDISP_INTERRUPT_STATUS_CONTINUE3`. Many Azalia endpoint registers use indirect/indexed register names such as `ixAZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT`, which are accessed through audio endpoint helpers rather than plain MMIO offsets.

## Control Flow

This chunk has no executable control flow. Its operational behavior is compile-time macro substitution:

1. A DCE 11 display, audio, GPIO, AUX, clock, IRQ, or power-management translation unit includes `dce/dce_11_0_sh_mask.h`.
2. The source selects a register address from `dce_11_0_d.h` or an indexed Azalia register.
3. The source uses `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`, usually indirectly through `REG_SET_FIELD` or `REG_GET_FIELD`, to insert or extract a field.
4. The resulting value is written to or read from hardware through AMDGPU/DC register access helpers.

Several control-flow-sensitive hardware concepts are encoded by these constants even though the header itself is declarative:

- Display audio setup code can sequence Azalia converter and pin programming by selecting endpoint registers, reading/writing stream IDs and converter formats, advertising ELD-derived audio descriptors, enabling audio on hot plug, and acknowledging unsolicited/format-change status.
- IRQ code can traverse the display interrupt chain by checking continuation bits: `DISP_INTERRUPT_STATUS` points at `DISP_INTERRUPT_STATUS_CONTINUE`, which points at `CONTINUE2`, which points at `CONTINUE3`. This range contains the chain through part of `CONTINUE3`.
- Power and clock-management paths can gate or ungate DPG, DCFE/DCFEV, Azalia, and memory sub-blocks by setting enable, force-on, shutdown, power status, and reset fields.
- HPD handling code can read `DC_HPD_INT_STATUS__DC_HPD_SENSE_MASK` and acknowledge or enable related interrupt bits in `DC_HPD_INT_CONTROL`.

The chunk boundaries matter: the first line is only the shift for `UNIPHY_POWER_CONTROL__UNIPHY_BIASREF_SEL`, with that field's mask immediately before this chunk; the last line is only the shift for `DISP_INTERRUPT_STATUS_CONTINUE3__CRTC3_EXT_TIMING_SYNC_INTERRUPT`, with more fields for the same register immediately after this chunk. The later merge lane must combine neighboring chunks for complete per-register descriptions.

## State And Persistence Behavior

The header stores no software state. It defines constants that describe hardware state locations. State becomes persistent only when another component writes registers using these definitions:

- `UNIPHY_*` fields persist in PHY/PLL hardware until the PHY block is reprogrammed or reset. Incorrect PLL divider, reference-clock, bandgap, impedance calibration, or spread-spectrum fields can prevent link lock, create unstable clocks, or break analog display output.
- `DPG*` watermark, stutter, DPM, and p-state fields persist as display memory-service policy. These values affect underrun risk, memory power saving, stutter/self-refresh entry and exit, and whether memory clock or NB p-state changes are allowed during scanout.
- `AZALIA_*` controller, codec, stream, and endpoint fields persist as the display-audio programming model. CORB/RIRB pointers, stream descriptor status, codec capabilities, endpoint descriptor content, hot-plug controls, and unsolicited-response fields are stateful at the audio controller or codec-emulation level.
- `BLND_*`, `WB_*`, and `CNV_*` fields persist in the display pipe. Update-lock and pending-update bits coordinate when new blender/converter/writeback state takes effect relative to scanout timing.
- `DCFE/DCFEV_*` fields persist as frontend clock/reset/memory-power state. These settings can power down local memories or gate clocks, so consumers must respect hardware sequencing and status bits.
- `DC_HPD_*` fields persist in HPD debounce, interrupt, and fast-training state. Ack bits are transient write-to-clear style controls in the consumer logic even though this header only provides masks.
- `DISP_INTERRUPT_STATUS*` fields represent latched or summary interrupt state. Some are read-only status and some are interpreted with separate control/ack registers outside this exact family.
- `DCO_SCRATCH*` fields are full 32-bit scratch values and may be used by firmware, BIOS, driver, or diagnostics depending on platform conventions.

Because this file is generated hardware metadata, the persistence risk is not memory lifetime inside C code; it is keeping bit layouts synchronized with the ASIC register database and with the register addresses in the companion header.

## Dependencies

This chunk depends on the surrounding AMDGPU/DC generated-register ecosystem:

- The file-level include guard `DCE_11_0_SH_MASK_H`, license block, and earlier macro definitions in `dce_11_0_sh_mask.h`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_0_d.h` for corresponding MMIO and indexed register address definitions.
- AMDGPU/DC register helper macros that expect the `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` naming convention.
- DCE 11 display code that includes this header, including DCE 11 IRQ service, GPIO factory/translation, AUX, audio, link encoder, timing generator, compressor, vertical display-pipe blocks, hardware sequencing, clock manager, and resource setup.
- Power-management code that includes this header for BACO or display/power interactions on DCE 11-era ASICs.
- Hardware contracts for Azalia/HD-audio, HDMI/DP audio descriptors, HPD/AUX behavior, display-pipe watermarks, DCFE memory power, and display interrupt routing.

Search results in this tree show direct consumers of related names in older DCE files as well, for example `dce_v10_0.c` and `dce_v6_0.c` use `DISP_INTERRUPT_STATUS_CONTINUE3__LB_D4_VBLANK_INTERRUPT_MASK`, `DC_HPD_INT_STATUS__DC_HPD_SENSE_MASK`, and Azalia pin-control fields. DCE 11-specific DC files include this header and follow the same generated macro convention.

## Integration Points

Primary integration points are low-level display hardware programming paths:

- Display IRQ routing: `DISP_INTERRUPT_STATUS*` masks map hardware summary bits to vblank, vline, HPD, AUX, DIG, DMCU, ABM, writeback/scaler, and external timing events. The `*_CONTINUE*` continuation bits let interrupt handling proceed to later summary registers.
- Hot-plug detection and link handling: `DC_HPD_INT_STATUS`, `DC_HPD_INT_CONTROL`, `DC_HPD_CONTROL`, `DC_HPD_FAST_TRAIN_CNTL`, and `DC_HPD_TOGGLE_FILT_CNTL` integrate with connector detection, HPD RX, AUX wakeups, and fast training for DisplayPort links.
- Display audio: Azalia root/function/converter/pin/control fields integrate with `dce_audio.c` and related endpoint helpers. They encode HDMI/DP audio capabilities, stream assignment, channel/speaker allocation, HBR capability, lip-sync, ELD/sink data, hot-plug audio enable, and unsolicited responses.
- Power management: DPG and DPGV watermarks/stutter/DPM/p-state fields integrate with display clock and memory clock policy. DCFE/DCFEV memory-power fields integrate with display block gating and power-state transitions.
- Display pipeline programming: BLND, CNV, and WB fields integrate with blender configuration, color-space conversion, writeback, update locking, underflow interrupts, and CRC/debug paths.
- Link encoder and PHY programming: UNIPHY fields integrate with PHY/PLL setup, TMDS/DP transmitter calibration, PLL lock tests, BIST, test pattern generation, and debug selection.
- Firmware/diagnostic scratch use: `DCO_SCRATCH*`, test debug, CRC, latency, and stream-debug fields provide register-level observability and platform coordination points.

The integration is entirely by name and bit layout. This header must stay in lockstep with DCE 11 address headers and with any generated offset tables used by DC code.

## Risks And Edge Cases

- The chunk has split-register coverage at both ends. The `UNIPHY_POWER_CONTROL__UNIPHY_BIASREF_SEL_MASK` definition is outside this range, while its shift is inside; the end of `DISP_INTERRUPT_STATUS_CONTINUE3` continues in the next chunk. A per-file report must reconcile adjacent chunks before claiming full register coverage.
- Wrong shifts or masks silently corrupt hardware programming. For example, bad `DC_HPD_INT_CONTROL` masks can acknowledge or enable the wrong HPD interrupt, and bad `DISP_INTERRUPT_STATUS_CONTINUE3` masks can route or classify the wrong display event.
- Many fields are duplicated across repeated instances (`DPGV0`/`DPGV1`, F0/F2 codecs, input/output pins, audio descriptors, sink-description bytes, and interrupt continuation registers). Generation drift can leave a copied field name or bit position that compiles cleanly but breaks one instance.
- Several fields use the high bits of a 32-bit register, including masks such as `0x80000000`. Callers must use unsigned 32-bit values and helper macros that avoid sign-extension or undefined shifts.
- Audio endpoint registers mix global HD-audio controller state with codec-emulation and endpoint-specific state. Writing the correct field to the wrong endpoint index can advertise incorrect capabilities, break HDMI/DP audio enumeration, or mis-handle format-change/hot-plug events.
- CORB/RIRB, DMA position, stream descriptor, and immediate command fields represent hardware queues and command paths. Bad masks can cause command ring stalls, wrong buffer pointers, or incorrect interrupt acknowledgment.
- DPG/DPGV and DCFE/DCFEV fields affect active scanout power behavior. Incorrect watermarks, stutter settings, or memory power controls can cause visible underflow, flicker, missed p-state transitions, or hangs around clock-gating transitions.
- HPD debounce and fast-training timing fields are timing-sensitive. Incorrect timer masks or shifts can produce noisy connector detection, missed disconnects, delayed hot-plug, or unreliable fast training.
- Interrupt status registers contain continuation bits. If a consumer misinterprets continuation masks, later interrupt status registers may not be inspected, causing lost events for pipes 2, 3, 4, or related AUX/HPD/DIG sources.
- Generated headers are broad include dependencies. A malformed macro or accidental edit here can break many display translation units even though the file contains no C statements.

## Test Signals

Useful validation is primarily compile-time, static, and hardware-integration oriented:

- Build AMDGPU/DC translation units that include `dce/dce_11_0_sh_mask.h`; failures will expose missing, duplicate, or malformed macro definitions.
- Run static consistency checks that pair every `REGISTER__FIELD_MASK` with a matching `REGISTER__FIELD__SHIFT` and confirm that every expected address exists in `dce_11_0_d.h`.
- Compare repeated layouts across instances: `DPG` versus `DPGV0/DPGV1`, F0 versus F2 codec families, audio descriptors 0-13, sink-description bytes, CRC channel arrays, and `DISP_INTERRUPT_STATUS_CONTINUE*` chains.
- Validate mask overlap within each register: fields should not overlap unless explicitly reserved or aliased, and high-bit fields should remain within 32-bit values.
- Exercise display IRQ handling on DCE 11 hardware or emulation by checking vblank/vline, HPD/HPD RX, AUX done, DIG fast-training/stream-disable, underflow, DMCU, ABM, and continuation-register paths.
- Exercise connector hot plug and unplug with debounce and fast-training enabled, verifying `DC_HPD_INT_STATUS` sense/status fields and `DC_HPD_INT_CONTROL` ack/enable behavior.
- Exercise HDMI/DP audio enumeration and playback, including ELD-derived descriptor programming, HBR-capable formats, channel allocation, pin sense, hot-plug audio enable, and unsolicited-response paths.
- Verify CORB/RIRB or immediate-command paths if display audio codec verbs are used, including read/write pointer behavior and response interrupt status.
- Exercise power-management transitions involving stutter/self-refresh, memory-clock changes, NB p-state changes, and DCFE/DCFEV memory power gating while monitoring for underflow, blanking, or clock-gating regressions.
- Use register readback tests around `REG_SET_FIELD` and `REG_GET_FIELD` for representative low, middle, and high-bit fields such as HPD ack bits, audio descriptor fields, watermark thresholds, and continuation interrupt bits.
