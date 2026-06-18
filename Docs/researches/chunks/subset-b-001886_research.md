# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 52128-55341

## Scope

This chunk is a large middle slice of the generated DCN 3.1.5 register shift/mask header `dcn_3_1_5_sh_mask.h`. It contains C preprocessor constants only: `_SHIFT` macros for field low-bit positions, `_MASK` macros for raw register bit masks, register-name comments, and generated `// addressBlock:` comments. There are no functions, structs, enums, branches, loops, allocations, or direct software state transitions in this range.

The slice starts in the tail of the `dpg3_dpgdebugind` block with `DPG3_DPG_DEBUG0..2` shift definitions, then covers debug-indirect field definitions for FMT, OPP buffer, OPP pipe, OPP top, ODM, DMCU, RBBMIF, IHC, DMU, DC power-gating, DisplayPort/DIG/AUX/DIO/HPO debug, and APG debug surfaces. The second half defines Azalia/HDA codec, endpoint, descriptor, sink-info, CRC, input-endpoint, root, and stream field masks. It ends mid-block at `AZF0STREAM15_AZALIA_FIFO_SIZE_CONTROL__MIN_FIFO_SIZE_MASK`; the rest of stream 15 continues in the following chunk.

This file is generated hardware-description data. The useful API is the macro namespace, not executable behavior. Runtime behavior appears when AMD display code combines these symbols with matching register offsets from `dcn_3_1_5_offset.h` and MMIO helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_WRITE`, `REG_FIELD`, `SF`, or `DMUB_SF`.

## Purpose And Hardware Surface

The purpose of this chunk is to define the bit layout for DCN 3.1.5 display debug and display-audio registers. Companion offset headers identify where each register lives; this header tells consumers how to pack values for writes and decode readbacks from the same registers.

Major hardware areas represented here:

- Display debug buses for DPG, FMT, OPP, ODM, RBBMIF, IHC, DMU, DCPG, DP, DIG, AUX, DIO, HPO, HDMI, DP stream/symbol/link encoders, DP DPHY symbol blocks, and APG clocks.
- DMCU debug buses exposing microcontroller reset/interrupt status, ERAM/IRAM/SFR accesses, internal register access, RBBM/MBUS handshakes, address-decoder hits, request-state machines, last read/write values, scratch registers, condition-code bits, clock-enable indicators, and ABM interrupt wiring for multiple ABM instances.
- Azalia/HDA function-2 codec output controls for converter format, stream/channel ID, digital converter bits, stripe control, ramp rate, GTC presentation-time embedding, codec/pin capabilities, pin widget controls, unsolicited responses, pin sense, default configuration, speaker/channel allocation, downmix, ACP/audio descriptors, multichannel enable/mute/channel IDs, IEC 60958 channel-status override bytes, LPIB snapshot/readback, coding type, format-change status, remote keepalive, and wireless-display identification.
- Azalia endpoint descriptor and sink-info windows for ELD-like audio descriptors, manufacturer/product IDs, port IDs, and sink description bytes.
- Azalia controller CRC result windows for input and output channel CRCs.
- Azalia input endpoint controls mirroring many output codec concepts for input converter/pin paths, including input activity, channel layout, infoframe/status readback, and channel-status low/high words.
- Azalia root/function controls for vendor/device/revision/subordinate-node parameters, function power state, subsystem ID bytes, converter synchronization, codec reset, group type, supported rates/stream formats, and power-state capability bits.
- Azalia stream debug and latency counters for streams 0 through 14, plus the first field definitions for stream 15.

## Important Definitions

The exported API is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field low bit.
- `<REGISTER>__<FIELD>_MASK` gives the raw in-register bit mask.
- `//<REGISTER>` comments group fields by hardware register.
- `// addressBlock: <block>` comments identify the generated address block that owns the following registers.

Most debug-bus registers in the first half are single-field, full-register or zero-shift definitions. Examples include `FMTx_FMT_DEBUG*__FMT_DEBUG*__SHIFT`, `OPPBUFx_OPPBUF_DEBUG*__OPPBUF_DEBUG*__SHIFT`, `DPx_DP_DEBUG_*__DP_DEBUG_*__SHIFT`, `DP_AUXx_DP_AUX_DEBUG_*__DP_AUX_DEBUG_*__SHIFT`, `HDMI_STREAM_ENC_*_DEBUG_*__...__SHIFT`, and DP/HPO/APG debug ID macros. These are mainly decode selectors or opaque debug payload fields where the generated header exposes a single shift value of `0x0`.

The DMCU block is denser and exposes named bit positions for internal microcontroller debug words:

- `DMCU_DEBUG_00` reports reset/IRQ/XIRQ pins, ABM0/1/2 interrupt lines, IHC-to-DMCU interrupts, SCP/MCP interrupt lines, CP1 copies of selected signals, power/ack signals, and the DMCU clock-enable bit.
- `DMCU_DEBUG_01..0B` cover ERAM and IRAM arbitration, chip-select/read/write strobes, address fragments, read/write data fragments, write-enable masks, and XA request-handler state.
- `DMCU_DEBUG_0C..0F` cover internal register write/read control and data, including write byte enables, accepted flags, read wait/data-valid state, register addresses, and ABM2 interrupt bits.
- `DMCU_DEBUG_10..18` cover DMCU-to-RBBM arbitration and MBUS access handshakes, request/data FIFO states, MBUS request/complete/write/address fields, and address-decoder hit bits for DCREG, interrupt, perfmon, DPRX, ERAM, and IRAM targets.
- `DMCU_DEBUG_19..2C` expose full MBUS/RBBM read/write data and last-address/data/readback values.
- `DMCU_DEBUG_2D..31` expose ERAM/IRAM/SFR TDM debug group offsets.
- `DMCU_DEBUG_32..3C` expose CP2 reset/gating/read-delay state, microcontroller registers (`index`, accumulators, math registers, condition-code bits), SFR scratch bytes, IRQ/XIRQ disable bits, and ABM3 interrupt signals.
- `DMCU_DEBUG_CONSTANT` provides two 16-bit constant fields, `DBG_DMCU_5a5a` and `DBG_DMCU_beef`, used as debug signature readbacks.

The DisplayPort/DIG/AUX/DIO debug families are instance-repeated:

- `DP0..DP4` have a `dpdebugind` block for `DP_DEBUG_K/L/M/G/O/P/Q/R/S` and a `dpfedebugind` block for `DP_DEBUG_T/U/V/W/X/Y/I/J/N/H/A/B/C/D/E/F`.
- `DIG0..DIG4` have DIG front-end debug ID plus AFMT and VPG debug registers.
- `DP_AUX0..DP_AUX4` expose AUX debug ID and debug buses A through Q.
- `DIO_MISC` exposes I2C debug, DIO/DIG RBBMIF debug buses, DME debug buses, and packed HPD debug fields where `HPD_1_2_DEBUG`, `HPD_3_4_DEBUG`, and `HPD_5_6_DEBUG` place paired HPD values at shifts `0x0` and `0x10`.

The HDMI/HPO/DP high-performance output definitions cover mostly debug selector IDs:

- `HPO_TOP_DEBUG_ID`, `HDMI_LINK_ENC_DEBUG_ID`, and `HDMI_FRL_ENC_DEBUG_ID`.
- `HDMI_STREAM_ENC_HDMISTREAMCLK_DEBUG_ID` plus debug words 0 through 15.
- `HDMI_STREAM_ENC_DISPCLK_DEBUG_ID` plus debug words 0 through 4.
- DP stream encoder debug IDs for streams 0 through 3 across dispclk, dpstreamclk, and symclk32 domains.
- DP symbol32 encoder debug IDs for symclk32 and dpstreamclk domains.
- DP link encoder 0/1 debug IDs and debug buses 0 through 3.
- DP DPHY symbol32 debug blocks 0/1 with debug buses 0 through 18.
- APG socclk and encclk debug IDs/words.

The Azalia output endpoint fields are the main non-debug field-pack definitions in this chunk:

- `AZALIA_F2_CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT` packs number of channels, bits per sample, sample divisor/multiple/base rate, and PCM/non-PCM stream type into a 16-bit stream format value.
- `AZALIA_F2_CODEC_CONVERTER_CONTROL_CHANNEL_STREAM_ID` packs 4-bit channel and stream IDs.
- `AZALIA_F2_CODEC_CONVERTER_CONTROL_DIGITAL_CONVERTER` exposes digital enable, validity/config/pre-emphasis/copyright/non-audio/professional/channel-status low bits, and keepalive.
- `AZALIA_F2_CODEC_CONVERTER_STRIPE_CONTROL`, `RAMP_RATE`, and `GTC_EMBEDDING` cover stripe programming, ramp rate, and presentation-time embedding.
- Audio widget capability and supported-size/rate macros define HDA capability readback fields, including digital, power-control, LR-swap, delay, type, rate capabilities, and bit-depth capabilities.
- Pin control fields include output enable, unsolicited-response tag/enable, pin sense presence, default configuration nibbles, speaker allocation, channel allocation, downmix, ACP index/data, audio descriptor fields, LPIB snapshot, coding type, format-change status/reason/response, wireless display ID, and remote keepalive.
- Multichannel enable registers appear as paired `01/23/45/67` controls and odd-channel `1/3/5/7` controls, each with enable, mute, and channel ID fields.
- `AZALIA_F2_PIN_CONTROL_CODEC_CS_OVERRIDE_0..8` provide IEC 60958 channel-status override fields for mode/source, clock accuracy, word length, sampling frequency, original sampling frequency, coefficient/MPEG/CGMS-A, and per-channel channel numbers.
- Pin parameter capability fields expose impedance sense, trigger/jack/headphone/output/input/balanced-I/O/HDMI/VREF/EAPD/DP capability bits.

The Azalia descriptor and sink-info blocks expose repeated data windows:

- `AUDIO_DESCRIPTOR0..13` each provide max channels, supported frequencies, descriptor byte 2, and stereo frequency fields.
- `AZALIA_F2_CODEC_PIN_CONTROL_MANUFACTURER_ID`, `PRODUCT_ID`, `SINK_DESCRIPTION_LEN`, `PORTID0`, and `PORTID1` provide sink identity fields.
- `SINK_DESCRIPTION0..17` provide one 8-bit description byte per register.

The Azalia CRC and stream blocks are repeated telemetry surfaces:

- `AZALIA_INPUT_CRC0_CHANNEL0..7`, `AZALIA_INPUT_CRC1_CHANNEL0..7`, `AZALIA_CRC0_CHANNEL0..7`, and `AZALIA_CRC1_CHANNEL0..7` expose full 32-bit channel CRC results.
- `AZF0STREAM0..14` each expose FIFO min/max size and max latency support, latency counter reset, worst-case latency count, cumulative latency count, cumulative request count, and stream debug data. The chunk begins the same pattern for `AZF0STREAM15` but includes only the FIFO size-control shifts and `MIN_FIFO_SIZE_MASK` before the requested range ends.

## Control Flow And State Behavior

There is no executable control flow in this header. The runtime flow is table-driven:

1. A DCN 3.1.5 consumer includes `dcn_3_1_5_offset.h` and `dcn_3_1_5_sh_mask.h`.
2. Register-list macros bind an offset such as `regAZALIA_F2_CODEC_*`, `regDP_AUX*_...`, or a debug register offset to the matching shift/mask constants in this file.
3. Hardware-block code reads or writes MMIO through AMD display register helpers.
4. Hardware latches configuration fields, returns live status/debug values, or clears counters/status according to the register's real side effects.

Most state represented here is hardware state rather than software-owned persistence:

- Persistent or semi-persistent configuration fields include Azalia converter format, stream/channel ID, digital converter flags, keepalive, stripe, ramp rate, GTC embedding, pin widget output enable, unsolicited-response enable/tag, speaker/channel allocation, downmix policy, ACP/audio descriptor selection, multichannel enable/mute/channel IDs, IEC 60958 channel-status overrides, remote keepalive, codec power-state set, converter synchronization, codec reset, and per-stream FIFO sizing/latency support controls.
- Volatile telemetry fields include debug bus readbacks, DMCU internal signal snapshots, RBBMIF/IHC/DMU/DCPG/DP/DIG/AUX/DIO/HPO/APG debug data, pin sense, output active status, format changed/reason/response, LPIB snapshots, input activity and infoframe validity, CRC results, latency counters, cumulative request counters, and stream debug data.
- Side-effecting or sequencing-sensitive fields include latency counter reset, codec reset, power-state settings reset, format-change acknowledgment/UR enable, unsolicited response enable, LPIB snapshot lock, input activity/CL-CS infoframe change UR enables, and any debug selector/register that changes which internal bus is sampled.

The macros do not encode ordering. Callers must still respect display power state, audio codec command protocol, HDA stream setup rules, AUX/DIG/DIO routing, hotplug timing, and any hardware-specific requirements around reading debug buses or clearing counters. A value can be correctly masked and still be wrong if written while the relevant block is power-gated, reset, clock-gated, routed to another encoder, or in the middle of an audio stream transition.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.1.5 register-address definitions in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`. The offset header supplies the `reg...` constants and base indices; this file supplies the bit positions and masks for fields in those registers. A mismatch between the two can compile in some cases but produce wrong MMIO programming or bad readback decoding.

Known direct include sites for DCN 3.1.5 generated offsets and masks include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`, which builds the DMUB DCN315 register interface using `DMUB_DCN315_FIELDS()`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`, which uses the generated register namespace for DCN315 interrupt-service tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.c` and `hw_translate_dcn315.c`, which bind DCN315 GPIO/HPD/DDC/AUX-related hardware translation to generated register definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`, which constructs the DCN315 resource pool and register tables for display hardware blocks.

Functional integration points include:

- DMUB service code, where generated masks/shifts populate firmware-visible register tables. Although this chunk is mostly debug/audio definitions, incorrect generated constants can affect diagnostics and any firmware-service reads that depend on these fields.
- IRQ and GPIO/hotplug paths, especially where DIO, HPD, AUX, and related debug/status fields help diagnose connector and link behavior.
- Display resource construction and hardware block constructors for DCN315. These register definitions are part of the same namespace used to build stream encoders, link encoders, AUX engines, APG/VPG/AFMT/audio objects, HPO blocks, and diagnostics.
- Audio-over-display code paths that program or inspect Azalia/HDA display-audio state. The `AZALIA_F2_CODEC_*`, descriptor, sink-info, CRC, root/function, and `AZF0STREAM*` fields are the register-field ABI for display audio capability reporting, stream setup, codec status, and latency/CRC diagnostics.
- Debugging and silicon bring-up flows that read debug indirect registers. The many zero-shift debug-bus fields are intentionally opaque payload windows whose exact decoded meaning is usually in hardware documentation, register databases, or debug tooling rather than in driver C code.

## Risks And Maintenance Notes

- Generated-header drift is the primary risk. Wrong numeric masks or shifts can compile cleanly while corrupting audio stream format, channel allocation, channel-status overrides, codec reset/power-state fields, or latency counter control.
- This chunk has partial boundaries. It begins after the start of `dpg3_dpgdebugind` and ends in the middle of `azf0stream15_streamind`; the merge lane should combine neighboring chunks before making file-level completeness claims.
- Many debug registers are single-field `SHIFT 0x0` definitions. They look trivial but still name specific hardware windows. Deleting or renaming them can break register-list expansion, debug tooling, or compile-time consumers even when no ordinary driver path writes the field.
- DMCU debug fields expose internal microcontroller, memory, bus, and ABM interrupt state. These are observational fields, not stable software contracts for normal control flow. Tests and diagnostics should avoid making policy decisions based solely on transient debug bus values.
- DMCU field names include CP1/CP2 copies, split address/data fragments, and similarly named ERAM/IRAM/SFR/RBBM/MBUS state. It is easy to decode the wrong field or join split fields in the wrong order during manual debugging.
- DP/DIG/AUX/DIO debug blocks are heavily instance-repeated. Confusing instance 0-4, link encoder 0/1, stream encoder 0-3, or symbol32 block 0/1 can produce valid reads from the wrong physical/logical link.
- HPD paired debug fields share registers with 16-bit spacing. Consumers must use the correct shift for HPD1 versus HPD2, HPD3 versus HPD4, and HPD5 versus HPD6.
- Azalia output and input endpoint fields have near-identical names. Output converter/pin controls and input converter/pin controls are not interchangeable even when their masks match.
- Several Azalia fields are HDA protocol surfaces rather than arbitrary driver flags. Stream format, channel IDs, IEC 60958 channel status, widget capabilities, pin capabilities, unsolicited response, LPIB, and power-state fields must remain consistent with HDA/display-audio expectations.
- Full-width CRC, LPIB, latency, cumulative latency, cumulative request, descriptor, and port-ID fields use `0xFFFFFFFFL` masks. Truncating, sign-extending, or treating them as small fields can produce misleading diagnostics.
- The stream 15 definitions in this chunk are incomplete. A report or tool generated from this chunk alone should not infer that stream 15 lacks the latency-counter, count, request, or debug registers.

## Test Signals

High-signal validation for changes touching this chunk includes:

- Compile coverage for AMDGPU Display Core with DCN315 enabled. Missing or malformed macros should be caught in `dmub_dcn315.c`, `irq_service_dcn315.c`, `hw_factory_dcn315.c`, `hw_translate_dcn315.c`, and `dcn315_resource.c`.
- Static comparison against the authoritative DCN 3.1.5 register database or a regenerated `dcn_3_1_5_sh_mask.h`, especially for Azalia masks/shifts and DMCU debug bit positions.
- Cross-revision spot checks against adjacent generated headers such as DCN 3.1.4, DCN 3.1.6, and DCN 3.2.0 where the hardware block is expected to be compatible, while preserving intentional DCN315 differences.
- Display-audio functional testing on DCN315 hardware: HDMI/DP audio playback, stream format changes, channel count changes, HBR/non-audio modes where supported, silent-stream/keepalive behavior, multichannel enable/mute/channel IDs, and suspend/resume with audio active.
- Audio diagnostics that read codec capabilities, pin capabilities, sink descriptors, manufacturer/product/port IDs, LPIB snapshots, CRC channels, and latency counters. Expected signals are sane field values, stable counter reset behavior, and no corruption of unrelated bits after masked updates.
- Hotplug/link diagnostic testing for DP/DIG/AUX/DIO/HPO/APG debug surfaces. Useful signals are successful HPD detection, EDID/DPCD reads, AUX transaction recovery, link training, and debug register reads that do not fault or target the wrong instance.
- DMCU/DMUB diagnostic readback during display bring-up, ABM/backlight events, suspend/resume, and interrupt handling. Expected signals include coherent reset/interrupt/bus-state debug values and no reliance on stale sampled debug buses.
- Register-dump comparison before and after audio or debug operations. Packed writes should affect only intended masked bits, and readback decoding should match the mask/shift definitions in this chunk.

## Open Questions For Merge

- The final per-file report should reconcile this chunk with the previous DPG3 lines and the following stream 15 lines so partial block boundaries are not mistaken for missing hardware support.
- This chunk documents generated field layout only. Any final behavioral claims about HDA command sequencing, DMCU debug interpretation, or debug-bus selector programming should be corroborated with the functional display/audio source files that use these macros.
