# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h lines 10375-12949

## Purpose

This chunk is generated AMD DCN 3.0 register-offset metadata. It contains no executable C logic; it publishes preprocessor constants that map symbolic display-controller register names to numeric MMIO offsets and companion base-index selectors. Consumers combine each `mm...` offset with its matching `mm..._BASE_IDX` to form the absolute register address for DCN 3.0 display hardware.

The range is a mid-file slice of `dcn_3_0_0_offset.h`. It starts at the tail of the `DP_AUX2` AUX/GTC/wake registers, covers complete `DP_AUX3` through `DP_AUX5` blocks, covers the repeated stream-output families for DIG/DP/VPG/AFMT/DME instances 0 through 5, covers DCIO GPIO/DDC/AUX pad control, and then enters the DSC register map for DSC instance 0 and the beginning of DSC instance 1. The requested range contains 2,410 `#define` lines: 1,205 register-offset macros and 1,205 matching `_BASE_IDX` macros.

Although the path is under a local `ceph-client` source mirror, this header is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, allocation paths, or locking primitives in this range. The interface is the generated macro namespace:

- `mm<block>_<register>`: a DCN 3.0 MMIO register offset.
- `mm<block>_<register>_BASE_IDX`: the base-address segment selector used by helper macros such as `BASE(mm..._BASE_IDX) + mm...`, `SR(...)`, `SRI(...)`, and DMUB `REG_OFFSET(...)`.

Every visible register offset in this chunk has a matching `_BASE_IDX`, and all `_BASE_IDX` values in the requested range are `2`. That value is part of the ABI between this generated header and the SOC15/DCN base-address tables; the numeric offset alone is not enough to address hardware safely.

Major macro families in this slice:

- `DP_AUX2` tail and complete `DP_AUX3`, `DP_AUX4`, `DP_AUX5`: AUX transaction control, software/low-speed status and data, DPHY TX/RX controls and status, GTC sync control/status/error registers, interrupt control, arbitration, and PHY wake control.
- `VPG0` through `VPG5`: generic packet access/data, generic-stream-packet frame/immediate update controls, status, memory power, ISRC access/data, and MPEG info registers used for secondary-data packet generation.
- `AFMT0` through `AFMT5`: audio/VBI packet control, HDMI/DP audio info, IEC 60958 channel status words, ramp controls, audio CRC, interrupt/status, audio source selection, infoframe control, and AFMT memory power.
- `DME0` through `DME5`: Display Micro Engine control and memory-control offsets.
- `DIG0` through `DIG5`: front-end/back-end control, output CRC, test and clock patterns, FIFO status, HDMI packet/audio/ACR/control/status registers, AFMT bridge control, TMDS control and symbols, lane enable, version, and forced disable.
- `DP0` through `DP5`: DisplayPort link and stream configuration, MSA colorimetry/timing/misc/VBID, video `M/N`, DPHY and link framing, HBR2 pattern, video interrupt control, training/lane/PHY status and test registers, secondary-data packet control, DPCSTX debug and PHY-control registers, MST and SEC packet controls, CRC, pixel-format, and VC payload-allocation registers.
- `DCIO`, `LVTMA`, `UNIPHYA` through `UNIPHYF`, and `DC_GPIO*`: link/backlight/panel-power, DCIO debug/mux, pad-strength and polarity controls, GPIO masks/data/enable/pull-up/AUX controls, and AUX/I2C pad power-good state.
- `DSC_TOP0`, `DSCCIF0`, `DSCC0`, `DC_PERFMON21`, `DSC_TOP1`, `DSCCIF1`, and partial `DSCC1`: display stream compression top/control/debug, DSC client interface config, compressor config/status/interrupt, PPS config registers, memory power, error counters, rate-buffer fullness counters, debug bus selectors/data, and DSC-local perfmon registers.

## Control Flow

This header has no runtime control flow. Runtime code supplies the sequencing:

1. DCN 3.0 resource, IRQ, GPIO, DIO, DSC, and DMUB code includes `dcn_3_0_0_offset.h` together with the matching `dcn_3_0_0_sh_mask.h`.
2. Register-list macros paste instance IDs into names such as `mmDIG4_HDMI_CONTROL`, `mmDP2_DP_LINK_CNTL`, `mmVPG1_VPG_GENERIC_PACKET_DATA`, or `mmDSCC0_DSCC_PPS_CONFIG0`.
3. Helper macros add the base segment selected by `*_BASE_IDX` to the offset and store the result in per-block register tables.
4. Driver code later uses those tables with `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and wait/poll helpers to program links, packet generators, audio formatting, AUX/DDC, GPIO, panel power, and DSC.

The macros do not encode ordering requirements. Consumers must still sequence clock/power enablement, link training, AUX arbitration, hotplug handling, audio packet setup, double-buffered packet updates, DSC PPS programming, interrupt clear/ack behavior, and suspend/resume restoration correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing. It describes MMIO-backed GPU state. The represented hardware state includes:

- AUX channel state for DisplayPort DPCD/EDID transactions, low-speed data movement, DPHY TX/RX status, GTC sync, interrupts, arbitration, and wake control.
- Stream encoder state for HDMI/TMDS and DP output: lane enable, front-end/back-end control, test patterns, CRC capture, FIFO status, HDMI generic packets, metadata packets, audio clock regeneration, TMDS symbols, and DP link/stream/secondary-packet/MST controls.
- Infoframe/audio packet state in `VPG*` and `AFMT*`, including generic packets, ISRC/MPEG metadata, audio-info fields, channel-status words, CRC/status, and memory-power state.
- DCIO and GPIO state for link routing, panel/backlight power, AUX/DDC pad control, GPIO masks/data/enables, pull-up configuration, mux/debug selection, and pad power-good reporting.
- DSC state for compressor enable/config, PPS payload registers, memory power, interrupt/status, rate-buffer fullness, error counters, debug buses, and DSC perfmon counters.

Persistence is hardware-defined. Configuration registers usually retain values until modeset, link reconfiguration, power gating, suspend/resume, or ASIC reset. Status, interrupt, debug, counter, clear/ack, wake, and power-status registers may be read-only, sticky, self-clearing, write-one-to-clear, or sequencing-sensitive. This header does not distinguish those behaviors; the companion mask header and consuming driver code provide the field-level semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.0 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h` for field shifts and masks.
- SOC15/DCN base-address headers that define `DCN_BASE__INST0_SEG2` and related segment constants consumed by `BASE(mm..._BASE_IDX)`.

Direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c`

The primary integration pattern is token-pasting register construction. DCN resource files define macros such as `SR(reg_name)` and `SRI(reg_name, block, id)` that expand to `BASE(mm..._BASE_IDX) + mm...`. DMUB uses `REG_OFFSET(reg_name)` in `dmub_reg.h` with the same address contract. GPIO translate/factory code maps logical pins, AUX channels, DDC lines, HPD lines, panel power, and backlight control to concrete `mmDC_GPIO*`, `mmAUX*`, and DCIO offsets.

## Risks And Edge Cases

- Offset or base-index drift is the central risk. These macros are untyped constants, so a wrong `mm...` value or `_BASE_IDX` can compile cleanly while programming the wrong MMIO register or segment.
- Repeated instance families are copy-sensitive. `DIG0`-`DIG5`, `DP0`-`DP5`, `VPG0`-`VPG5`, `AFMT0`-`AFMT5`, and `DME0`-`DME5` are structurally similar but not interchangeable; an instance-specific typo may only fail on one connector or multi-display configuration.
- The chunk boundaries are artificial. The first lines are only the tail of `DP_AUX2`, and the final line stops inside `DSCC1_PPS_CONFIG11`; adjacent chunks are required for full file-level coverage.
- AUX/DDC and GPIO registers are side-effect-sensitive. Incorrect status/interrupt/clear/wake handling can break hotplug, EDID reads, DPCD transactions, panel wake, or low-power resume.
- Link-training and packet registers interact with timing and link state outside this header. Bad DP/TMDS/HDMI/AFMT/VPG offsets can cause blank displays, audio loss, CRC mismatch, infoframe corruption, MST payload errors, or failures limited to specific link rates and lane counts.
- DSC programming is stateful and format-sensitive. Wrong PPS, memory-power, status, interrupt, or debug offsets can produce compressed-stream corruption, link bandwidth failures, or pipe-specific issues when DSC is enabled.
- Power and memory-control offsets are high risk because writes may be ignored or harmful when the relevant display block is gated, reset, or clock-disabled.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN 3.0 and DCN 3.0.2 support enabled; missing or renamed macros should fail in resource, IRQ, GPIO, DIO, DSC, and DMUB register-table construction.
- Mechanically verify that every non-`_BASE_IDX` `mm...` macro in lines 10375-12949 has exactly one matching `_BASE_IDX` macro and that all base-index values remain `2`.
- Diff this chunk against AMD's authoritative DCN 3.0 register database and nearby generated headers such as `dcn_2_1_0_offset.h` or later DCN 3.x headers where compatibility is expected.
- Exercise systems with enough active displays to use high-numbered instances: DP/HDMI link training on `DIG`/`DP` instances 0 through 5, hotplug, EDID/DDC, AUX DPCD reads/writes, MST, link-rate/lane-count changes, and suspend/resume.
- Validate stream packets and audio: HDMI and DP audio playback, audio clock regeneration, infoframes, generic packets, ISRC/MPEG metadata, CRC capture, and packet update timing.
- Test GPIO/DCIO paths for panel power, backlight, DDC/AUX pad routing, HPD behavior, pull-up controls, and low-power wake.
- Enable DSC on capable panels and verify modesets, PPS programming, stream stability, rate-buffer/fullness counters, interrupt/status handling, and visual integrity at high bandwidth.
- Watch kernel logs and display diagnostics for AUX timeouts, hotplug storms, link-training failures, audio dropouts, CRC mismatches, underflow, DSC errors, stuck interrupts, and resume failures.

## Cross-Chunk Notes

Previous chunks own the beginning of the DCN 3.0 DIO/AUX area, including most of `DP_AUX2`. Later chunks continue `DSCC1` after `DSCC1_PPS_CONFIG11` and cover the remaining DCN 3.0 register-offset namespace. The final per-file research document should merge adjacent chunks before making complete claims about all AUX channels, all DSC instances, or the complete `dcn_3_0_0_offset.h` hardware map.
