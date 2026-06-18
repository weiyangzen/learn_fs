# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h lines 7580-10140

## Purpose

This chunk is a generated AMD DCN 4.1.0 display-controller register-offset slice. It contains no executable C logic; it exports C preprocessor constants that map symbolic register names to MMIO register offsets and companion `_BASE_IDX` values used by AMDGPU display register helper tables.

The requested range contains 2,388 `#define` entries. Each hardware register normally appears as a pair: `reg...` for the offset and `reg..._BASE_IDX` for the register base index. The slice starts in the middle of MPCC MCM3 color-management definitions, covers MPC output color-space conversion, OPP/ABM/format/output-pipe/timing/DIO register blocks for instances 0 through 3 or 0 through 1 depending on the block, and ends in the middle of the `DP2` DisplayPort encoder register block. The line boundaries are therefore artificial chunk boundaries rather than complete hardware-block boundaries.

Although this file is under a local `ceph-client` source mirror, this chunk is AMDGPU DCN display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, locks, or direct I/O operations in this range. The public interface is the generated macro naming convention:

- `reg<block>_<REGISTER>`: register offset used by AMD display MMIO helpers.
- `reg<block>_<REGISTER>_BASE_IDX`: base-index selector used with generated register tables to choose the correct address aperture/base for the register.

The main register families in this chunk are:

- `MPCC_MCM3_*`: tail of MPCC MCM instance 3 color-management offsets, including second gamut-remap coefficients, MCM memory power control, and 3D LUT fast-load select/status.
- `MPC_OUT0` through `MPC_OUT3` plus `MPC_OCSC_*`: MPC output mux, denormalization clamp/control, output CSC coefficient format, per-output CSC modes, A/B coefficient banks, and OCSC debug index/data.
- `ABM0` through `ABM3`: adaptive backlight management and BL1 PWM offsets for ambient light, user level, target/current ABM level, duty-cycle bounds, sample-rate/update controls, register locks, histogram controls/data, luminance controls, debug/status, and master lock registers.
- `DPG0` through `DPG3`: display pattern generator control, dimensions, offset, background color, test pattern color, ramp, and status offsets.
- `FMT0` through `FMT3`: output formatter clamp, dynamic expansion, bit-depth control, dithering/randomization, temporal dither pattern, memory power, CRC, debug, and 4:2:2 control offsets.
- `OPPBUF0` through `OPPBUF3`, `OPP_PIPE0` through `OPP_PIPE3`, and `OPP_PIPE_CRC0` through `OPP_PIPE_CRC3`: output-pipe buffer, pipe control, and per-pipe CRC control/result offsets.
- `DSCRM0` through `DSCRM3`: DSC stream/forwarding configuration offsets.
- `OPP_TOP_*` and `OPP_ABM_CONTROL`: top-level OPP clock and ABM coordination offsets.
- `ODM0` through `ODM3`: OPTC input/global and output-data-mapping control offsets, including memory power, debug bus, double-buffer control, and spare register offsets.
- `OTG0` through `OTG3`: timing-generator offsets for horizontal/vertical totals, sync, blanking, border, interrupt controls, vline/vupdate/vready/state, stereo, 3D structure, CRC, test pattern, global swap lock, vertical count, frame count, manual flow control, static-screen, double-buffer, trigger, underflow, and spare registers.
- `OPTC`/`GSL` miscellaneous offsets: global swap-lock source selection, timing control, underflow controls, OTG clock-control/status, and miscellaneous spare registers.
- `DP0` and `DP1`: complete DisplayPort link/stream offsets for each DIO DP block in this slice, including link control, pixel format, MSA, stream enable, DPHY training/symbol/CRC/fast-training, transfer-unit control, secondary-data/audio packet controls, MST/MSE controls, ALPM, stream/link symbol counters, and panel replay control.
- `DIG0` and `DIG1`: digital front-end/back-end, HDMI, audio-format, HDCP/I2C, TMDS, CRC, FIFO, test-pattern, packet-control, ACR, and version offsets.
- `DP2`: beginning of the third DisplayPort block, from `DP_LINK_CNTL` through `DP_DPHY_INTERNAL_CTRL` within this requested slice.

Most families are mechanically repeated across hardware instances with different register offsets. For example, `OTG0` starts at `0x1b2a`, `OTG1` at `0x1baa`, `OTG2` at `0x1c2a`, and `OTG3` at `0x1caa`; `DP0` starts at `0x211e`, `DP1` at `0x2242`, and the partial `DP2` block starts at `0x2366`.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU display code that includes this generated offset header alongside the matching DCN 4.1.0 shift/mask header:

1. DCN 4.1 display components include `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h`.
2. Register-list macros token-paste these symbolic register names into per-block register tables for resource construction, IRQ service setup, DMUB register access, clock/gpio helpers, timing generators, encoders, MPC/OPP blocks, and output formatters.
3. Runtime display paths use helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`; those helpers combine the offsets from this file with masks/shifts from the companion generated header.
4. Hardware sequencing, locking, blanking windows, double-buffering, power transitions, and interrupt handling are controlled by the consumer code and the hardware specification, not by this header.

The macros do not encode programming order. Consumers still need to program timing, output format, color conversion, ABM, DisplayPort/HDMI packets, link training, CRC, and power state in valid hardware sequences.

## State And Persistence Behavior

This chunk stores no software state and persists nothing directly. It names hardware-visible DCN 4.1.0 register state:

- MPC/MPCC color pipeline state for output muxing, denormalization, CSC/gamut-remap coefficient banks, memory power, and LUT fast-load state.
- OPP state for ABM/PWM, pattern generation, output formatting, pipe buffering, DSC forwarding, output CRC, and top-level OPP control.
- OPTC/OTG state for display timing, blanking/sync geometry, interrupt windows, stereo/3D signaling, CRC, test patterns, frame and vertical counters, global swap lock, underflow, and trigger/update behavior.
- DIO state for DisplayPort and HDMI/DIG blocks, including link configuration, stream attributes, main-stream attributes, DPHY training and diagnostics, audio/secondary packets, MST/MSE allocation, ALPM, panel replay, TMDS, HDCP, and ACR timing.

Persistence is hardware-defined. Configuration registers generally remain until modeset, link retraining, plane/stream reprogramming, power-gating, suspend/resume, GPU reset, or ASIC reset rewrites them. Status, CRC, counter, interrupt, debug, and fast-training registers may be read-only, sticky, write-one-to-clear, self-clearing, clock-gated, or valid only while the relevant display block is powered. This offset header does not describe those access semantics; consumers must rely on the register specification and block-specific driver code.

## Dependencies And Integration Points

This file must stay synchronized with AMD's generated DCN 4.1.0 register database and its companion generated files:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h` supplies the matching field shifts and masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.c` includes the DCN 4.1.0 generated headers for DMUB-facing register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn401/irq_service_dcn401.c` includes them for IRQ source setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c` includes them while constructing DCN 4.1 display resources and register lists.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_translate_dcn401.c` and `hw_factory_dcn401.c` include them for GPIO translation/factory behavior.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c` includes them for DCN 4.1 clock-manager register access.

The behavioral integration points represented by this chunk are output composition and scanout after DPP/MPC processing: MPC output color programming, OPP formatting and ABM, timing generation, CRC/test diagnostics, DisplayPort link/stream programming, HDMI/TMDS/DIG packet handling, and display interrupt/status paths.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong offset or base index can compile cleanly while directing register helpers to the wrong MMIO address.
- The file is generated. Manual edits risk divergence from the authoritative register database, companion shift/mask definitions, firmware expectations, and silicon documentation.
- The chunk boundaries are not semantic. The first definitions continue the `MPCC_MCM3` group that began before line 7580, and the `DP2` block continues after line 10140.
- Repeated instance layouts make generator drift hard to detect. `OTG0` working does not prove `OTG1` through `OTG3` offsets are correct; similarly, `DP0` and `DP1` can diverge independently from the partial `DP2` block.
- Color-management and CSC offsets are precision-sensitive and user-visible. Wrong MPC/MPCC offsets can cause incorrect color conversion, wrong LUT/gamut-remap bank updates, or failed fast-load status polling.
- ABM/PWM offsets affect panel backlight behavior. Mistakes can produce brightness jumps, stuck ABM levels, bad ambient-light response, or failure to respect user brightness limits.
- Timing-generator offsets are display-critical. Wrong OTG total/sync/blanking/update/trigger offsets can cause blank screens, unstable modesets, underflow, missed vblank/vupdate interrupts, bad stereo/3D signaling, or CRC/test-pattern misdiagnosis.
- DIO offsets affect link training and protocol packets. Wrong DP/DIG offsets can break DisplayPort link training, MST/MSE allocation, ALPM, panel replay, HDMI audio/video infoframes, HDCP I2C handling, TMDS output, or audio clock regeneration.
- Status and interrupt registers can have side effects. Confusing a status, clear, acknowledge, or enable register through a bad offset may cause missed interrupts, stuck interrupt status, or interrupt storms.
- Power and clock-gated blocks may reject or drop MMIO accesses if consumers use the offsets outside the required enable sequence; this header cannot protect against those ordering errors.

## Test Signals

Useful validation combines generated-header consistency checks with DCN 4.1 hardware behavior:

- Build AMDGPU display support with DCN 4.1 enabled. Missing or renamed constants should fail in DCN401 DMUB, IRQ, resource, GPIO, clock-manager, and display-block register-table construction.
- Mechanically compare this range against AMD's authoritative DCN 4.1.0 register source and the adjacent `dcn_4_1_0_sh_mask.h` names. Treat the start and end of the requested line slice as artificial boundaries.
- Run static checks that each non-`_BASE_IDX` register macro has a corresponding `_BASE_IDX` macro and that repeated instance groups have expected stride/pattern relationships.
- Exercise ABM/backlight paths across user brightness changes, ambient-light updates, panel idle/static-screen transitions, suspend/resume, and rapid modesets.
- Exercise MPC output CSC/gamut remap/LUT fast-load paths with visual color tests or CRC-based validation for multiple pipes and coefficient-bank updates.
- Exercise OPP formatter paths across bit depths, dithering modes, dynamic expansion, 4:2:2 output, output CRC capture, pattern generation, and DSC forwarding.
- Exercise OTG modesets over multiple timings, vblank/vline/vupdate interrupts, stereo/3D modes, test patterns, global swap lock, frame counters, underflow detection, and double-buffered update triggers on OTG0 through OTG3.
- Exercise DisplayPort and HDMI/DIG paths for DP0/DP1 and adjacent DP2 coverage: link training, stream enable/disable, MSA programming, audio/secondary packets, MST/MSE, ALPM, panel replay, HDCP, TMDS, ACR, hotplug, suspend/resume, and link retraining.
- Watch kernel logs and display diagnostics for MMIO register-access failures, missed vblank/update interrupts, underflows, CRC mismatches, link-training failures, audio packet loss, HDCP failures, ABM brightness anomalies, and resume-only display artifacts.

## Cross-Chunk Notes

The previous chunk contains the beginning of the `MPCC_MCM3` color-management register group, including earlier 1D LUT region and first/second gamut-remap definitions. The next chunk continues the `DP2` DisplayPort block after `DP_DPHY_INTERNAL_CTRL`. The final per-file research document should merge adjacent chunks before making whole-file claims about all DCN 4.1.0 offset definitions, all MPCC instances, or all DIO DP/DIG instances.
