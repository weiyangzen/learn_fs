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
