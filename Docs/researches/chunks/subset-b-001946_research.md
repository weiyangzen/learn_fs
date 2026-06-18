# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 42213-44674

## Purpose

This chunk is a generated AMD DCN 3.2.0 register shift/mask slice. It contains C preprocessor metadata only: `__SHIFT` macros for field low-bit positions, `_MASK` macros for raw register bit masks, register comments, and generated `// addressBlock:` grouping comments. There are no executable functions, structs, enums, allocations, locks, branches, or direct MMIO accesses in this range.

The range starts in the tail of `DSCC0_DSCC_PPS_CONFIG21`, covers the end of DSC compressor instance 0, all visible DSC compressor/interface/top fields for DSC instances 1 through 3, then moves into HPO output registers for stream mapping, HDMI/DP audio/video packet blocks, DP stream encoder 0, APG 0, and DP symbol32 encoder 0. It ends mid-register-family at `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL14`, so adjacent chunks are required for complete file-level coverage.

Although the source tree path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem logic.

## Important APIs, Types, And Macros

The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field low bit.
- `<REGISTER>__<FIELD>_MASK` gives the in-register bit mask.
- `//<REGISTER>` comments group fields by hardware register.
- `// addressBlock: <block>` comments identify the generated hardware address block for following registers.

This slice defines 2,134 `#define` lines: 1,067 shift macros and 1,067 mask macros. Major register families are:

- `DSCC0` tail fields: final DSC picture-parameter-set range table fields, DSC memory power controls, squared-error and max-absolute-error counters, rate-buffer fullness counters, and test-debug bus rotate/index fields.
- `DSCCIF0` plus `DSC_TOP0`: DSC input-interface underflow recovery/status, input pixel format, bits per component, picture size, top-level DSC clock enable/gating, and debug clock mux fields. `DSC_TOP0_DSC_DEBUG_CONTROL` appears in repeated generated comment/macro fragments in this range.
- `DSCC1`, `DSCC2`, and `DSCC3`: repeated DSC compressor instances covering compressor configuration, rate-control buffer model size, ICH controls, double-buffer status, overflow/underflow/end-of-frame interrupt status and enables, PPS configuration words 0 through 22, memory power, error counters, and buffer fullness counters.
- `DSCCIF1`, `DSCCIF2`, and `DSCCIF3`: input-interface underflow recovery, interrupt/status, pixel format, component depth, double-buffer pending, picture width, and picture height fields for the matching DSC instances.
- `DSC_TOP1`, `DSC_TOP2`, and `DSC_TOP3`: top-level DSC clock enable and display/DSC clock gating controls for additional DSC instances.
- `HPO_TOP`: HPO top clock and hardware controls, including HPO clock enable and stream clock enable fields.
- `DP_STREAM_MAPPER_CONTROL0..3`: HPO DP stream-to-link target routing fields.
- `AFMT5`: HDMI/HPO audio formatter fields for VBI packet control, audio packet controls, audio infoframe words, IEC 60958 channel-status words, audio CRC control/result, audio ramp controls, formatter status, interrupt status, audio source control, and formatter memory power.
- `DME5` and `DME6`: DME control and memory-power fields for HDMI and DP HPO paths.
- `VPG5` and `VPG6`: generic packet access/data, frame/immediate update controls, generic status, memory power, ISRC packet access/data, and MPEG infoframe fields.
- `DP_STREAM_ENC0`: stream encoder clock control, input mux, audio source selection, clock-ramp-adjuster FIFO reset/enable/status, and spare fields.
- `APG0`: audio packet generator control, debug generator, audio packet control, CRC control/result/status, memory power, and spare fields.
- `DP_SYM32_ENC0`: DP symbol32 encoder reset/enable, video FIFO controls, video MSA and pixel-format double buffering, pixel encoding, MSA timing/colorimetry fields, hblank control, and generic stream packet control registers `SDP_GSP_CONTROL0..14` visible in this slice.

Representative field groups include DSC PPS fields such as `BITS_PER_PIXEL`, `PIC_WIDTH`, `PIC_HEIGHT`, `SLICE_WIDTH`, `SLICE_HEIGHT`, rate-control offsets, QP range minima/maxima, and BPG offsets; DSC status/interrupt fields for per-buffer overflow and underflow; AFMT/APG fields for audio packet enable, mute/sample controls, CRC, and memory power; VPG generic packet fields for address/data/update/status; and DP symbol32 GSP fields for continuous transmission, one-shot trigger, double buffering, payload size, SOF reference, pending/deadline status, and transmission line number.

## Control Flow

There is no runtime control flow in this header. Runtime use is table-driven:

1. DCN 3.2.0 consumers include `dcn_3_2_0_offset.h` for register addresses and this file for field masks and shifts.
2. Register-list macros expand names such as `DSCC1_DSCC_PPS_CONFIG*`, `DP_STREAM_MAPPER_CONTROL*`, `AFMT5_*`, `VPG6_*`, or `DP_SYM32_ENC0_*` into offset, mask, and shift tables.
3. Driver code uses helper macros such as `FD_MASK`, `FD_SHIFT`, `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and HPO/DSC-specific field-list macros to access the underlying MMIO registers.
4. Hardware latches configuration fields or returns live status/debug/counter fields according to the real register side effects.

The macros do not encode ordering. Consumers still have to sequence DSC clock enable, compressor reset/configuration, PPS programming, interface configuration, interrupt clear/enable, memory-power transitions, HPO stream routing, audio formatter setup, VPG packet updates, APG audio packet control, stream encoder FIFO reset, symbol32 encoder enable, MSA programming, and generic packet double-buffer commits correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes MMIO-backed hardware state:

- DSC compressor state for slice layout, native/simple 4:2:2 or 4:2:0 behavior, block prediction, rate-control model size, PPS parameters, QP range tables, memory power, and error/fullness telemetry.
- DSC interface state for input format, component depth, picture dimensions, underflow recovery, underflow interrupt enable/status, and double-buffer pending status.
- DSC top-level state for functional clock enables and clock-gating controls.
- HPO routing state for mapping DP streams to target links.
- HDMI/DP sideband packet state in AFMT, VPG, APG, and DME blocks, including audio infoframes, IEC 60958 metadata, generic packets, ISRC/MPEG packet windows, CRC controls/results, mute/source controls, and block memory-power state.
- DP stream/symbol encoder state for stream clocking, input muxes, FIFO reset/enable/status, pixel format, video MSA timing fields, hblank minimum symbol width, and generic stream packet scheduling.

Persistence and side effects are hardware-defined. Configuration fields may retain values until modeset, stream disable, power gating, suspend/resume, or ASIC reset. Status, pending, underflow, overflow, CRC, double-buffer, memory-power, FIFO reset-done, and one-shot trigger fields may be read-only, sticky, self-clearing, or write-one-to-clear depending on the register. This generated header only exposes bit positions and masks; it does not describe access type, reset value, volatility, or side effects.

## Dependencies And Integration Points

This chunk must remain synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`, which supplies the matching DCN 3.2.0 register offsets and base indices. A shift/mask header mismatch with the offset header can compile cleanly but write or decode the wrong MMIO fields.

Direct include sites for the DCN 3.2.0 offset and mask headers in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`

Functional integration points include:

- DSC programming code, which uses DSCC, DSCCIF, and DSC top fields to enable DSC, program PPS values, set slice geometry/rate-control state, configure input format, and monitor compressor/interface error status.
- DCN32 resource construction, where generated offset/mask/shift values are assembled into per-block register tables for display objects.
- DMUB register initialization, where `DMUB_DCN32_FIELDS()` populates firmware-visible mask and shift tables through `FD_MASK` and `FD_SHIFT`.
- HPO DP stream encoder code, especially the DCN31/DCN32 HPO path that uses `DP_STREAM_MAPPER_CONTROL*`, `DP_STREAM_ENC0_*`, and `DP_SYM32_ENC0_*` fields to map streams, reset/enable FIFOs, program video MSA/pixel format, and schedule secondary data packets.
- Display audio and packet paths, where AFMT, APG, DME, and VPG fields control audio packets, generic sideband packets, infoframes, CRC telemetry, and memory power.
- IRQ, clock, GPIO, and hotplug/resource paths that rely on the same generated namespace as part of the wider DCN32 hardware register ABI.

## Risks And Edge Cases

- Generated-header drift is the main risk. Incorrect numeric masks or shifts can build successfully while corrupting DSC PPS programming, HPO stream routing, audio packet metadata, DP MSA fields, or generic packet scheduling.
- The chunk boundaries are partial. The first line is already inside `DSCC0_DSCC_PPS_CONFIG21`, and the last line stops inside the `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL*` family.
- DSC instances are highly repeated. Confusing `DSCC0` through `DSCC3`, `DSCCIF0` through `DSCCIF3`, or `DSC_TOP0` through `DSC_TOP3` can target a valid but wrong compressor instance.
- PPS fields are dense and protocol-sensitive. Wrong QP range, BPG offset, chunk size, slice size, or bits-per-pixel masks can produce link-training failures, visible corruption, bandwidth miscalculation symptoms, or DSC decoder incompatibility.
- Interrupt/status fields are side-effect sensitive. Overflow, underflow, end-of-frame-not-reached, pending, and enable bits must be cleared, enabled, and read according to hardware rules outside this header.
- Memory-power and clock-gating fields can make otherwise correct writes ineffective if a block is gated or powered down during programming.
- AFMT/APG/VPG/DME packet fields mix configuration, payload windows, update triggers, and status bits. Writing packet data without the right access/update sequencing can transmit stale or partial sideband packets.
- DP symbol32 MSA, pixel-format, FIFO, hblank, and GSP controls are timing-sensitive. Incorrect fields may show up only under high refresh, DSC, HDR/metadata, audio, or multi-stream HPO configurations.
- The repeated generated `DSC_TOP0_DSC_DEBUG_CONTROL` fragments should be treated as source-generation output, not hand-deduplicated, unless regenerated from the authoritative register database.

## Test Signals

Useful validation for changes touching this chunk includes:

- Build AMDGPU Display Core with DCN32 support enabled. Missing or malformed generated symbols should be caught in DCN32 resource, DMUB, IRQ, clock, GPIO, DSC, HPO stream encoder, and audio/packet users.
- Mechanically compare this range against the authoritative AMD DCN 3.2.0 register database or a regenerated `dcn_3_2_0_sh_mask.h`; every visible shift should have the expected same-field mask.
- Cross-check the companion `dcn_3_2_0_offset.h` so register names, base indices, and field names stay aligned.
- Exercise DSC modes on DCN32 hardware: multiple DSC instances, different slice counts, 4:4:4/4:2:2/4:2:0 formats where supported, high bits per component, high refresh, suspend/resume, and hotplug.
- Watch for DSC-specific symptoms: compressor underflow/overflow, end-of-frame-not-reached status, double-buffer update stalls, error counter changes, blank displays, corruption, or sink DSC decode failures.
- Exercise HPO DP paths with stream mapping, DP symbol32 encoder enable/reset, MSA programming, FIFO reset, hblank programming, and generic stream packets such as HDR metadata or other SDP traffic.
- Test HDMI/DP audio and packet paths that use AFMT/APG/VPG/DME: audio playback, mute/unmute, channel-status metadata, CRC readback, generic packet updates, ISRC/MPEG/infoframe updates, and memory-power transitions.
- Use register-dump comparisons before and after DSC/HPO/audio operations. Masked writes should affect only intended bits, and status/pending fields should decode consistently with the macros in this chunk.

## Cross-Chunk Notes

The final per-file report should merge this chunk with the previous DSCC0 PPS definitions and the following DP symbol32 encoder packet-control definitions before making complete claims about DSC instance 0 or the full `DP_SYM32_ENC0` sideband packet register family. This chunk should be treated as a source-tree-aligned research artifact for lines 42213-44674 only.
