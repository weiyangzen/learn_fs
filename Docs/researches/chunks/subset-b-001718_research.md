# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h lines 5218-7845

## Purpose

This chunk is generated AMD DCN 3.0.1 register-offset metadata. It contains no executable C logic; it exports preprocessor constants that map symbolic display-controller register names to numeric MMIO offsets plus companion base-index selectors. DCN 3.0.1 driver code combines each `mm...` offset with the matching `mm..._BASE_IDX` through `BASE(...)`, `SR(...)`, `SRI(...)`, or DMUB `REG_OFFSET(...)` helpers to build concrete register tables.

The requested range starts inside the DPP2 color-management block at `CM2` shaper/3D LUT registers, covers a complete DPP3 processing pipe, covers OPP/FMT/DPG/OPPBUF/OPP pipe and CRC instances 0 through 3, covers OPTC/ODM and OTG timing generators 0 through 3, then enters DIO with I2C/DDC, HPD, AUX channel 0 through 3, VPG0, AFMT0, DME0, and the beginning of DIG0 HDMI output registers. The range contains 2,400 `#define` lines: 1,200 register-offset macros and 1,200 matching `_BASE_IDX` macros. All `_BASE_IDX` values in this range are `2`.

Although the path is under a local `ceph-client` source mirror, this header is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, allocations, locks, or error paths in this chunk. Its API is the generated macro namespace:

- `mm<block>_<register>`: a DCN 3.0.1 MMIO register offset.
- `mm<block>_<register>_BASE_IDX`: the base-address segment selector for the same register.

Every visible non-`_BASE_IDX` macro in lines 5218-7845 has exactly one matching `_BASE_IDX` macro. The numeric offset alone is not sufficient; the base index is part of the address contract with `DCN_BASE__INST0_SEG2` and related generated SOC base definitions.

Major macro families in this chunk:

- `CM2` tail: shaper RAM A/B region controls, color-management memory power, 3D LUT index/data/read-write/output normalization, and CM test-debug access for DPP instance 2.
- `DC_PERFMON12`: DPP2 perfmon counter control, state, current value, and high/low counter registers.
- `DPP_TOP3`, `CNVC_CFG3`, `CNVC_CUR3`, `DSCL3`, and `CM3`: DPP3 top reset/CRC/read controls, pixel-format conversion, keying, pre-CSC/pre-degamma, cursor controls, scaler coefficient RAM and filter controls, line-buffer and output-buffer memory power, post-CSC, gamut remap, gamma-correction RAM A/B, blend gamma RAM A/B, HDR multiplier, shaper LUT/RAM, 3D LUT, and debug access.
- `DC_PERFMON13`: DPP3 perfmon counter controls and values.
- `FMT0` through `FMT3`: output formatter clamp, dynamic expansion, bit depth, dither seeds, side-by-side stereo, 4:2:0 map-memory control, and 4:2:2 control.
- `DPG0` through `DPG3`: display pattern generator control, ramp, dimensions, RGB/YUV color values, offset segment, and status.
- `OPPBUF0` through `OPPBUF3`, `OPP_PIPE0` through `OPP_PIPE3`, and `OPP_PIPE_CRC0` through `OPP_PIPE_CRC3`: OPP buffer controls, 3D parameters, pipe control, pipe CRC mask and result registers.
- `OPP_TOP`, `DSCRM0` through `DSCRM2`, and `DC_PERFMON14`: OPP clock/ABM controls, DSC forward-routing controls, and OPP perfmon counters.
- `ODM0` through `ODM3`: OPTC input global control, data-source select, data-format and bytes-per-pixel controls, width, input clock, memory config, and spare registers.
- `OTG0` through `OTG3`: timing-generator horizontal/vertical totals, blanking, sync, trigger, flow, stereo, status/readback, counters, snapshots, interrupts, update lock, double buffering, master enable, blank colors, CRC windows/data, static-screen/3D/GSL/global-sync controls, dynamic refresh-rate controls, DTO constants, request control, DSC start position, and pipe update status.
- `OPTC` misc: DWB/GSL source selection, OPTC clock control, ODM memory power control/status, spare register, and `DC_PERFMON15`.
- `DC_I2C`, `DIO`, `HPD0` through `HPD3`, and `DC_PERFMON16`: DIO I2C/DDC control, arbitration, interrupt/status, DDC speed/setup, transactions/data, EDID-detect/read-request interrupt, DIO scratch and power/clock/interrupt registers, hot-plug-detect status/control/filtering, and DIO perfmon counters.
- `DP_AUX0` through `DP_AUX3`: AUX control, software control/status/data, low-speed status/data, arbitration, interrupt, DPHY TX/RX control and status, GTC sync controls/status, error controls, controller status, and PHY wake control.
- `VPG0`, `AFMT0`, `DME0`, and partial `DIG0`: generic-packet and ISRC/MPEG packet registers, audio formatter packet/info/status/CRC/ramp/source/memory-power registers, DME control/memory control, and the first DIG0 front-end, CRC, pattern, FIFO, HDMI metadata/audio/ACR/VBI/infoframe/generic-packet registers.

## Control Flow

This header has no runtime control flow. Runtime sequencing is provided by DCN resource, link, timing, color, AUX/I2C, HPD, audio, and DMUB code:

1. DCN 3.0.1 code includes `dcn_3_0_1_offset.h` with `dcn_3_0_1_sh_mask.h` and the SOC base-offset header.
2. Resource-table macros paste register names and instance numbers into symbols such as `mmCM3_CM_3DLUT_DATA`, `mmOTG2_OTG_UPDATE_LOCK`, `mmDP_AUX1_AUX_SW_DATA`, or `mmAFMT0_AFMT_AUDIO_PACKET_CONTROL`.
3. `BASE(mm..._BASE_IDX) + mm...` is evaluated into register-table fields.
4. Hardware-specific code later uses those tables with `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, wait/poll helpers, and DMUB service code to program display pipes.

The macros do not encode ordering requirements. Consumers still need to sequence DPP color programming, scaler coefficient updates, OPP/OTG double-buffered updates, pipe locking, timing-generator enable/disable, vblank/vertical-interrupt handling, dynamic refresh-rate changes, AUX/I2C arbitration, HPD interrupt clears, audio/infoframe packet updates, and suspend/resume restoration correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing in files. It names MMIO-backed GPU state. The represented hardware state includes:

- Color-management and scaler state in DPP2/DPP3: gamma/blend/shaper RAM contents, 3D LUT data, CSC/gamut matrices, cursor state, scaler taps/ratios/init values, line-buffer and output-buffer power state, and debug-indexed access.
- Output-pipe state in OPP/FMT/DPG/OPPBUF: formatter pixel processing, dither and bit-depth settings, generated test patterns, OPP buffer controls, DSC-forward routing, ABM control, and OPP pipe CRC capture.
- Timing-generator state in ODM/OTG/OPTC: source routing, timing totals, blanking/sync, triggers, master enable, double-buffer/update locks, vblank/vertical interrupts, CRC capture windows, snapshots, GSL/global sync, dynamic refresh-rate parameters, DTO constants, DSC start, and memory-power status.
- DIO state: I2C/DDC transactions and status, EDID detection, scratch registers, power/clock controls, DIG soft reset, HPD interrupts/filtering/fast-train controls, AUX transaction/status/PHY/GTC/wake state, VPG packet-generator state, AFMT audio packet/infoframe/CRC state, DME controls, and initial DIG0 HDMI stream-encoder state.
- Perfmon state for DPP2, DPP3, OPP, OPTC, and DIO local counters.

Persistence is hardware-defined. Configuration registers generally retain values until modeset, pipe reprogramming, block power gating, suspend/resume, or ASIC reset. Status, interrupt, counter, debug, wake, and power-status registers may be read-only, sticky, self-clearing, write-one-to-clear, or valid only while clocks are enabled. This offset header does not describe those semantics; they come from the companion shift/mask header, hardware documentation, and consuming driver code.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.0.1 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h` for field shifts and masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c`, which includes this offset header and defines `BASE`, `SR`, `SRI`, `SRI2`, `SRIR`, `SRII`, and `SRII2` helpers that materialize register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c`, which includes this header and uses `REG_OFFSET(reg)` through `dmub_reg.h`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_reg.h`, where `REG_OFFSET(reg_name)` expands to `BASE(mm##reg_name##_BASE_IDX) + mm##reg_name`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/vangogh_ip_offset.h`, included by the DCN301 resource and DMUB code to provide the matching IP segment base constants.

The likely consumers of these specific register families are DCN301 resource construction, DPP color/scaler objects, OPP/OPTC timing objects, DIO stream/link encoder paths, DCE AUX/I2C/HPD helpers, audio/infoframe packet code, and DMUB service initialization. Their integration pattern is compile-time token pasting; a register name typo or missing macro normally breaks the build, while a wrong numeric value compiles and fails only on hardware.

## Risks And Edge Cases

- Offset or base-index drift is the central risk. The macros are untyped constants, so an incorrect numeric value can compile cleanly while directing MMIO to the wrong register.
- Chunk boundaries are artificial. The first line starts in the middle of `CM2` shaper RAM A definitions, and the final line stops after `mmDIG0_HDMI_GENERIC_PACKET_CONTROL6`; adjacent chunks are required for full-file claims.
- Repeated instance families are copy-sensitive. `FMT0`-`FMT3`, `DPG0`-`DPG3`, `OPPBUF0`-`OPPBUF3`, `OTG0`-`OTG3`, `HPD0`-`HPD3`, and `DP_AUX0`-`DP_AUX3` have similar register layouts but instance-specific offsets. A one-instance mistake may only appear with particular pipes, connectors, or multi-display topologies.
- Color pipeline programming is stateful. Bad CM/3D LUT/shaper/gamma/scaler offsets can cause wrong color conversion, HDR or gamut errors, cursor artifacts, invalid scaling, line-buffer failures, or blank/underflow conditions.
- Timing-generator and update-lock registers are high impact. Wrong OTG/ODM/OPTC offsets can cause missed vblank, stuck update locks, incorrect dynamic refresh-rate behavior, bad CRC captures, global-sync failures, or display modeset hangs.
- AUX/I2C/HPD registers are side-effect-sensitive. Incorrect interrupt/status/clear/wake/arbitration offsets can break EDID reads, DPCD transactions, hotplug detection, link training, wake from low power, or cause interrupt storms.
- Audio and packet registers affect protocol-visible stream metadata. Wrong VPG/AFMT/DIG HDMI offsets can corrupt infoframes, generic packets, audio clock regeneration, channel status, CRC reporting, or HDMI metadata packets.
- Power and memory-control offsets should only be used when the corresponding clocks and power domains are valid; writing while blocks are gated or reset can be ignored or produce hard-to-debug display bring-up failures.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN301 support enabled. Missing or renamed macros should fail in `dcn301_resource.c`, DMUB DCN301 register initialization, and hardware-object register-list construction.
- Mechanically verify this chunk's invariant: lines 5218-7845 contain 1,200 non-`_BASE_IDX` `mm...` macros, 1,200 matching `_BASE_IDX` macros, no unmatched pairs, and all base-index values are `2`.
- Diff `dcn_3_0_1_offset.h` and `dcn_3_0_1_sh_mask.h` against AMD's authoritative DCN 3.0.1 register source and against neighboring DCN headers where compatibility is expected.
- Exercise DPP3 and the tail of DPP2 color paths: modesets with color management, gamma/gamut/shaper/3D LUT programming, HDR output, cursor composition, scaling, CRC/debug reads, and suspend/resume.
- Exercise OPP/OPTC instances 0 through 3: multi-display modesets, pipe splitting or ODM use where supported, timing changes, vblank/vertical interrupt delivery, update locks, CRC capture, dynamic refresh rate, global sync, and DSC start-position programming.
- Exercise DIO paths represented here: DDC/EDID reads, AUX DPCD reads/writes, HPD plug/unplug and IRQ handling on connectors mapped to AUX/HPD 0 through 3, low-power wake, and link training.
- Validate VPG/AFMT/DIG0 stream metadata: HDMI/DP audio playback, infoframes, generic packets, MPEG/ISRC packets, audio CRC/status, ACR packet programming, and HDMI metadata packet updates.
- Watch kernel logs and display diagnostics for AUX timeouts, HPD storms, EDID failures, link-training failures, blank displays, vblank misses, update-lock stalls, underflow, CRC mismatches, audio dropouts, and resume failures.

## Cross-Chunk Notes

Previous chunks own the beginning of the DPP2 `CM2` color-management block before `CM2_CM_SHAPER_RAMA_REGION_12_13`. Later chunks continue the DIG0 HDMI/generic-packet and stream-encoder register set after `mmDIG0_HDMI_GENERIC_PACKET_CONTROL6` and likely cover additional DIG/DP/VPG/AFMT/DME instances. The final per-file research document should merge adjacent chunks before making complete claims about all DPP, OPP, OPTC, DIO, or DIG register coverage in `dcn_3_0_1_offset.h`.
