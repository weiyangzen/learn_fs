# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h lines 10753-13311

## Purpose

This chunk is a generated AMD DCN 4.2.0 register offset header slice. It contains no executable C logic; it exports preprocessor constants that map symbolic display-controller register names to MMIO register offsets and base-index selectors. AMDGPU display code pairs these offset macros with the matching `dcn_4_2_0_sh_mask.h` field definitions and generic register helpers to build per-block register tables.

The requested range contains 2,384 `#define` lines: 1,192 register offset macros and 1,192 matching `_BASE_IDX` macros. It starts at the tail of the DIO DME1 block, covers legacy-style DIG/DP encoder instances 1 through 4, covers DSC instances 0 through 3 and their perfmon blocks, covers writeback instance 0, covers DCHVM registers, and then enters the first high-performance DP 2.x output path: HPO stream encoder 0, APG5/DME5/VPG5, DP_SYM32 encoder 0, link encoder 0, and the beginning of DP_DPHY_SYM320.

Although this path is under a local `ceph-client` source mirror, this chunk is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, locks, allocations, callbacks, or direct MMIO operations in this range. The exported interface is the generated macro naming convention:

- `reg<INSTANCE>_<REGISTER>`: the register's generated offset value.
- `reg<INSTANCE>_<REGISTER>_BASE_IDX`: the register's base-index selector, `2` for every register in this chunk.

Major register groups in this chunk:

- `DME1`: the tail of DIO metadata engine instance 1, with DME control and memory-control offsets.
- `DIG1` through `DIG4`: front-end/back-end digital encoder and HDMI/TMDS register offsets, including FE/BE control, clocks, enable, output CRC, test/random patterns, FIFO controls, HDMI metadata/audio/ACR/VBI/infoframe/generic packet controls, GC, DB control, ACR values/status, audio control, TMDS control/sync/DC-balancer registers, and DIG version.
- `DP1` through `DP4`: DisplayPort stream/link encoder offsets for each DIO instance, including link control, pixel format, MSA colorimetry/misc/timing, video stream control, steering FIFO, DPHY training/symbol/8b10b/PRBS/scramble/CRC controls and results, TU control, secondary-data/audio/timestamp/packet controls, MSE/MST rate and slot-allocation controls/status, HBLANK, MSO, ALPM, AUX-less ALPM, symbol counters, panel replay, and fast-training registers.
- `VPG2` through `VPG5`: generic packet access/data, GSP frame/immediate update controls, status, memory power, and ISRC access/data windows.
- `APG2` and `APG3`: full audio packet generator control/debug/audio CRC/ramp/memory-power blocks. `APG4` and `APG5` are shorter HPO-adjacent groups with APG control/control2/debug and memory-power offsets.
- `DME2` through `DME5`: metadata-engine control and memory-control offsets.
- `DSC_TOP0` through `DSC_TOP3`, `DSCCIF0` through `DSCCIF3`, and `DSCC0` through `DSCC3`: display stream compression top/interface/compressor offsets for four DSC instances.
- `DC_PERFMON17` through `DC_PERFMON21`: perf-counter and perfmon register offsets attached to DSC and DWB blocks.
- `DWB` and `FC`: writeback top, frame-capture/window, CRC, output, backpressure, host-read, overflow, reset, debug, HDR multiplier, gamut-remap, OGAM LUT, and OGAM RAM A/B curve-region offsets.
- `DCHVM`: display hub virtual-memory control, clock, memory, RIOMMU control, and RIOMMU status offsets.
- `DP_STREAM_ENC0`: HPO DP stream encoder 0 clock, input mux, audio, clock-ramp FIFO status, and spare offsets.
- `DP_SYM32_ENC0`: 32-bit-symbol HPO stream encoder video FIFO, MSA, pixel-format double-buffer, SDP/GSP, audio SDP, metadata packet, stream/VBID/panel replay, CRC, symbol-count, ALPM, memory-power, and spare offsets.
- `DP_LINK_ENC0`: HPO DP link encoder clock-control and spare offsets.
- `DP_DPHY_SYM320`: the beginning of HPO DP DPHY symbol32 lane/VC/eDP/ALPM metadata, through `DP_DPHY_SYM32_ALPM_SLEEP_CONFIG0`.

The DSC compressor groups are dense and user-visible. Each `DSCCn` block exposes configuration/status/interrupt offsets, `DSCC_PPS_CONFIG0` through `DSCC_PPS_CONFIG22`, memory-power controls, squared-error and max-absolute-error readbacks, output/rate-buffer fullness readbacks, and debug index/data registers. These offsets are consumed with field masks from the companion shift/mask header to program DSC picture parameter sets and monitor compression health.

The DIO DP groups are structurally repeated across `DP1` through `DP4`. Each instance describes the legacy DP stream/link surface used for link training, main stream attribute programming, secondary-data packets, audio, MST/MSE scheduling, panel replay, ALPM, symbol counting, and PHY diagnostics.

## Control Flow

This header has no runtime control flow. Runtime use follows the AMD display register-table pattern:

1. DCN 4.2 code includes `dcn_4_2_0_offset.h` and `dcn_4_2_0_sh_mask.h`.
2. Resource headers and block constructors use token-pasting helpers such as `SR`, `SRI_ARR`, `SRI2_DWB`, `SRI_ARR_DWB`, and `SE_SF`-style field macros to bind generic block register names to generated offsets, base indices, shifts, and masks.
3. Constructed display objects store those tables for encoders, DSC, DWB, HPO stream/link encoders, IRQ/GPIO, clock, and DMUB-facing code.
4. Runtime paths use register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` against those tables during modeset, link training, audio/packet setup, DSC programming, writeback capture, hotplug/IRQ handling, and power-management transitions.

The macros themselves do not encode programming order. Sequencing for stream disable/enable, DP link training, DSC PPS updates, DWB update locking, writeback memory programming, DCHVM setup, HPO stream/link allocation, DPHY lane setup, ALPM, and interrupt/status acknowledgement is supplied by consuming driver code and the hardware programming model.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It names hardware-backed state surfaces:

- Digital encoder state for FE/BE enable, clocks, FIFOs, HDMI/TMDS packet generation, audio packets, ACR values, test patterns, and CRC readbacks.
- DisplayPort stream/link state for pixel format, MSA timing/colorimetry, video stream enable, DPHY training/patterns, secondary-data packets, audio timestamps/N/M values, MST/MSE allocation, MSO, ALPM, panel replay, and symbol-count diagnostics.
- Packet and metadata state in VPG/APG/DME blocks, including generic packets, GSP updates, ISRC payload windows, audio packet generation, metadata-engine memory power, and related debug registers.
- DSC state for compressor configuration, status, interrupt registers, PPS payload, memory-power controls, error counters, buffer-fullness counters, and debug buses.
- Perfmon state for attached DSC/DWB performance counters and current-value readbacks.
- DWB/frame-capture state for enable/clock/memory, capture windows, output format, CRC, backpressure counters, host-read controls, overflow state, reset/debug, HDR/gamut remap, and output gamma RAM/LUT programming.
- DCHVM state for display virtual-memory and RIOMMU control/status.
- HPO DP 2.x stream/link state for stream muxing, audio, 32-bit symbol encoder video MSA/pixel/SDP/CRC/ALPM/memory-power controls, link encoder clocks, DPHY enable/status, stream VC rates, slot allocation table entries, eDP ASSR, and initial ALPM sleep configuration.

Persistence and side effects are hardware-defined. Configuration fields usually remain until modeset, block disable, power gating, suspend/resume, GPU reset, or ASIC reset rewrites them. Status, interrupt, CRC, counter, update-pending, overflow, error, and debug fields may be read-only, latched, self-clearing, write-one-to-clear, or valid only while the relevant block is powered and clocked. This generated offset file does not express those access semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DCN 4.2.0 register database and its companion shift/mask header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h` supplies the matching field positions and masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c` includes this header and constructs DCN42 resource tables, including DIG/link encoder mapping, HPO stream encoders, DWB resources, and register/mask/shift tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.h` defines the register-list macros that directly expect names from this chunk, including the DIG HDMI/FE list and `DCN42_HPO_DP_STREAM_ENC_REG_LIST_RI(id)` for `DP_STREAM_ENC`, `DP_SYM32_ENC`, and related HPO stream registers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn42/dcn42_hpo_dp_link_encoder.c` reads HPO DPHY status, control, slot allocation, and VC-rate registers whose offsets are in the `DP_DPHY_SYM320` portion of this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn32/dcn32_hpo_dp_link_encoder.h` provides the shared HPO link encoder mask/shift list shape that expects `DP_DPHY_SYM320_*` register names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_dwb.h` and DCN42 resource glue consume the DWB/FC offset names through DWB common register-list macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn42/irq_service_dcn42.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_factory_dcn42.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_translate_dcn42.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn42/dcn42_clk_mgr.c`, and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c` include the DCN42 generated headers for interrupt/GPIO translation, clock management, and DMUB register access.

Behaviorally, this range is part of several display paths: legacy DIO HDMI/DP stream encoding, DSC compression, writeback capture/color processing, display VM setup, and HPO DP 2.x stream/link encoding. The repeated instance numbering must align with resource-pool capabilities and engine identifiers used by DCN42 resource construction.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong offset or base index can compile cleanly and only fail as bad MMIO at runtime.
- The file is generated. Manual edits risk divergence from AMD's authoritative register database, the companion shift/mask header, firmware expectations, and silicon documentation.
- Chunk boundaries are not semantic. The range starts after the address-block comment for DME1 and only includes its last two registers. It ends inside `DP_DPHY_SYM320`; ALPM wake/control and test-pattern registers continue in the next chunk.
- Repeated instances are copy-sensitive. DIG/DP instances 1-4 and DSC instances 0-3 are structurally similar; an offset error can affect only one connector, one stream encoder, or one DSC pipe.
- Legacy DIO DP and HPO DP 2.x registers coexist in this slice. Consumers must use the right register list for the selected encoder type; mixing `DPn_*` and `DP_SYM32_ENC0`/`DP_DPHY_SYM320` offsets can produce plausible but wrong hardware access.
- DSC PPS offsets must align exactly with the shift/mask definitions. A mismatch can corrupt compressed stream parameters, causing blank displays, decompressor mismatch, underrun/overflow status, or mode-specific visual corruption.
- DWB update, overflow, CRC, OGAM, and backpressure registers are sequencing-sensitive. Bad offsets can silently break capture output, color conversion/gamma, or diagnostics while normal display scanout still works.
- DCHVM and RIOMMU control/status registers are low-level display memory integration points. Incorrect offsets can appear as page faults, blank display after resume, writeback failures, or DMUB/display-memory handoff issues.
- HPO DPHY VC-rate and SAT registers are link-bandwidth critical. Wrong offsets can break MST/USB4-style stream allocation, link bring-up, ALPM, panel replay, eDP ASSR handling, or only high-bandwidth DP modes.
- Base-index selectors are all `2` in this range. A generator or merge error that changes an offset without the correct base index would route generic register helpers to the wrong address aperture.

## Test Signals

Useful validation combines generated-header consistency checks with runtime display coverage:

- Build AMDGPU display with DCN42 enabled. Missing or renamed macros should fail in DCN42 resource, HPO, IRQ, GPIO, clock-manager, DMUB, DSC, or DWB table construction.
- Mechanically verify every `reg...` offset in this chunk has exactly one adjacent matching `reg..._BASE_IDX` definition and that all base-index values are `2`.
- Cross-check this offset range against `dcn_4_2_0_sh_mask.h` and AMD's DCN 4.2.0 register database so every consumed register has matching field definitions.
- Compare repeated instance layouts for `DIG1-4`, `DP1-4`, `VPG2-5`, `DME1-5`, `DSC_TOP0-3`, `DSCCIF0-3`, and `DSCC0-3`, allowing only intentional offset spacing and HPO-specific truncation.
- Exercise HDMI and legacy DP connectors backed by DIG/DP instances in this range: modeset, audio, infoframes, CRC/test patterns, link training, secondary-data packets, MST/MSO where supported, panel replay, fast training, suspend/resume, and hotplug.
- Exercise DSC on all four instances with modes that require compression. Expected signals are successful modesets, valid PPS programming, no stuck update-pending state, no unexpected DSCC interrupt/status errors, and sane error/fullness readbacks.
- Exercise DWB capture with different source sizes, windows, output formats, CRC checks, gamut-remap/OGAM programming, backpressure monitoring, overflow interrupt/status handling, and suspend/resume.
- Exercise DCHVM/RIOMMU paths under display memory pressure and resume/reset scenarios; watch for page-fault, RIOMMU status, blanking, or DMUB/display handoff errors.
- Exercise HPO DP 2.x stream/link encoder 0 with high-bandwidth DP modes, MST allocation, eDP ASSR where applicable, ALPM, panel replay, symbol-count/CRC diagnostics, and DPHY status polling. Expected signals are stable link training, correct VC-rate/SAT programming, no stuck rate/SAT update-pending bits, and no cross-encoder register aliasing.

## Cross-Chunk Notes

The previous chunk owns the earlier DME1 address-block context and register families before `DME_CONTROL`. This chunk owns the DME1 tail, complete DIG/DP instances 1-4, DSC instances 0-3, DWB0, DCHVM, and the first HPO DP stream/link encoder 0 sections through `DP_DPHY_SYM32_ALPM_SLEEP_CONFIG0`. The next chunk continues the `DP_DPHY_SYM320` block with ALPM wake/control and test-pattern registers, so the final per-file report should merge these boundaries before making whole-block claims about HPO DP DPHY support in `dcn_4_2_0_offset.h`.
