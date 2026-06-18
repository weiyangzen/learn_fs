# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h lines 12824-15508

## Purpose

This chunk is generated AMD DCN 3.1.6 register-offset metadata. It has no executable C logic; it publishes preprocessor constants that map display, DSC, HPO link, VGA, and Azalia audio register names to numeric offsets and, for MMIO-style `reg*` entries, to a `*_BASE_IDX` segment selector. Driver code combines these constants with DCN316 base-address tables and the matching `dcn_3_1_6_sh_mask.h` field definitions to build hardware register tables and perform read/write access.

The requested range covers 2,685 source lines and 2,345 `#define` entries. Within the chunk there are 713 `reg*` offset definitions, 714 companion `*_BASE_IDX` definitions, and 918 `ix*` indirect-index definitions. The count is intentionally not symmetric because the chunk starts inside `DCIO_UNIPHY5_UNIPHY_MACRO_CNTL_RESERVED30_BASE_IDX` and ends inside `azf0inputendpoint1_inputendpointind`.

Although the source path is under a local `ceph-client` mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or exported runtime symbols in this range. The public surface is the generated macro naming convention:

- `reg<REGISTER>`: DCN display-engine register offset within a base segment.
- `reg<REGISTER>_BASE_IDX`: index into the ASIC base segment table used by helper macros such as `BASE(reg..._BASE_IDX)`.
- `ix<REGISTER>`: indirect register index, commonly for VGA and Azalia codec/stream/endpoint spaces rather than direct DCN MMIO.

Major macro groups in this chunk:

- Tail of `DCIO_UNIPHY5` and full `DCIO_UNIPHY6`: reserved UNIPHY macro-control offsets with base index 2.
- `PWRSEQ0` and `PWRSEQ1`: panel/display power sequencing GPIO, delay, light-sleep, control, state/debug, and spare offsets.
- `DSCC0` through `DSCC2`, `DSCCIF0` through `DSCCIF2`, and `DSC_TOP0` through `DSC_TOP2`: DSC encoder configuration, PPS parameters, range-min/max/BPG tables, debug and status registers, DSCC interface config, top-level DSC control, and per-DSC perfmon counters `DC_PERFMON19` through `DC_PERFMON21`.
- HPO top and stream mapper: `HPO_TOP_CLOCK_CONTROL`, `HPO_TOP_HW_CONTROL`, and `DP_STREAM_MAPPER_CONTROL0` through `CONTROL3`.
- HPO HDMI and DP stream encoding: `AFMT5`, `DME5`, and `VPG5` for the HPO HDMI stream encoder; `DP_STREAM_ENC0` through `DP_STREAM_ENC3`, `APG0` through `APG3`, `DME6` through `DME9`, and `VPG6` through `VPG9` for HPO DP stream encoders.
- HPO DP symbol/link physical layers: `DP_SYM32_ENC0` through `DP_SYM32_ENC3`, `DP_LINK_ENC0`/`1`, and `DP_DPHY_SYM320`/`321` offsets for control, training-pattern, SAT/VC-rate, CRC, debug, and spare registers.
- `DCHVM`: host-VM/IOMMU-facing display registers such as `DCHVM_CTRL0`, fault address, and RIOMMU status.
- VGA indirect spaces: sequencer, CRT controller, graphics controller, and attribute-controller `ixSEQ*`, `ixCRT*`, `ixGRA*`, and `ixATTR*` indices.
- Azalia audio indirect spaces: root/function parameters, F2 codec converter/pin registers, descriptor and sink-info windows, input/output CRC channel results, 16 F0 stream windows, 8 F0 output endpoint windows, and the beginning of F0 input endpoint windows.

## Control Flow

This header has no runtime control flow. The effective control flow is supplied by DCN316 display and DMUB code that includes this offset header:

1. DCN316-specific C files include both `dcn/dcn_3_1_6_offset.h` and `dcn/dcn_3_1_6_sh_mask.h`.
2. Base helper macros expand `reg..._BASE_IDX` through DCN base-segment constants, then add the corresponding `reg...` offset. In `dmub_dcn316.c`, for example, `REG_OFFSET_EXP(reg_name)` expands to `BASE(reg##reg_name##_BASE_IDX) + reg##reg_name`.
3. Higher-level display code uses generated offset/mask/shift tables to program power sequencing, DSC compression, HPO stream/link encoders, DisplayPort symbol PHY paths, audio packet generation, and DMUB-visible register access.
4. `ix*` indirect indices are consumed through indirect-register access paths, where the numeric index selects a VGA or Azalia codec/stream/endpoint register inside an indexed aperture rather than a direct MMIO offset.

The constants do not encode programming order, lock ownership, polling requirements, sticky status behavior, write-one-to-clear behavior, or indirect-index address/data sequencing. Those rules live in the display driver and ASIC specification.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on disk or in memory. It describes hardware register locations whose values live in the GPU display/audio hardware.

Hardware state represented by the offsets includes:

- Panel power state and sequencing state for `PWRSEQ0`/`PWRSEQ1`, including GPIO control, delays, light sleep, debug, and spare state.
- DSC encoder state for three DSCC instances: slice/PPS programming, rate-control tables, buffer model values, interrupt/status/debug registers, and DSC top-level control.
- HPO output state: stream mapper routing, HDMI audio/video packet formatting, DP stream encoder clocks and VID timing, APG/VPG packet-generator state, DME memory/control registers, and DP symbol encoder state.
- DP link/PHY state: DPHY enable/reset, lane/mode selection, training pattern control, SAT stream allocation, VC rate control, CRC results, and debug counters.
- DCHVM/IOMMU-facing state such as display VM control, fault addresses, and RIOMMU status.
- Legacy VGA indexed state and Azalia audio codec state, including converter formats, stream/channel IDs, pin-sense/configuration defaults, ELD/audio descriptors, sink info, hot-plug/audio-enable status, LPIB snapshots, CRC channel results, and unsolicited response controls.

Persistence is hardware-defined. Configuration values generally remain until modeset, stream disable, power-gating transition, suspend/resume restore, audio endpoint reset, or ASIC reset changes them. Status, CRC, fault, hot-plug, LPIB, and interrupt fields may be volatile, sticky, latched, self-clearing, or write-one-to-clear depending on the register. This offset header only names where such registers are.

## Dependencies And Integration Points

Primary companion dependency:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h`, which provides field shifts and masks for the register names declared here.

Observed integration sites in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c` includes this offset header and the matching mask header, defines DCN316 base segments, and builds `dmub_srv_dcn316_regs` from `DMUB_DCN31_REGS()` and `DMUB_DCN31_FIELDS()`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` includes the same generated headers while constructing DCN316 display resources and register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_srv.c` selects DCN316 DMUB register support through `DMUB_ASIC_DCN316`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm.c` maps the ASIC to `DMUB_ASIC_DCN316` and references the `amdgpu/dcn_3_1_6_dmcub.bin` firmware name.

Broader integration is with AMDGPU DC resource construction, DMUB service register tables, DSC programming, HPO DP/HDMI output paths, audio endpoint handling, and diagnostic paths that read CRC, perfmon, debug, or fault registers. The `reg*` entries must remain aligned with the DCN316 base segment constants, and the `ix*` entries must remain aligned with their indirect address/data access mechanisms.

## Risks And Edge Cases

- Offset drift is the main risk. These are untyped preprocessor constants, so an incorrect offset or base index can compile cleanly while directing writes to the wrong hardware register.
- This chunk begins in the middle of the `DCIO_UNIPHY5` reserved register list and ends in the middle of `azf0inputendpoint1_inputendpointind`. Final file-level reconciliation must merge neighboring chunks before making complete-instance claims for those two blocks.
- `reg*` and `ix*` macros have different access models. Treating an indirect `ixAZALIA*`, `ixCRT*`, or `ixATTR*` index like a direct MMIO `reg*` offset would target the wrong bus/aperture.
- Repeated instances are copy-generated. A single bad instance number or base index in `DSCC0`-`2`, `DP_STREAM_ENC0`-`3`, `DP_SYM32_ENC0`-`3`, `APG0`-`3`, `VPG5`-`9`, or `AZF0ENDPOINT0`-`7` can appear only on a specific display pipe, link, stream, or audio endpoint.
- DSC offsets cover compression PPS and rate-control state. Misaddressed writes can cause visual corruption, DSC negotiation failures, buffer underflow/overflow interrupts, or blank output only on compressed-link modes.
- HPO DP symbol/DPHY offsets control training patterns, virtual-channel rate, SAT allocation, and CRC/debug state. Errors can break high-bandwidth DisplayPort link training or MST-style stream mapping while leaving simpler paths unaffected.
- Azalia audio offsets include pin-sense, hot-plug, ELD/sink info, LPIB snapshots, stream IDs, and audio format changed status. Bad index values can lead to HDMI/DP audio enumeration failures, stale sink capabilities, missed format-change interrupts, or incorrect audio-channel routing.
- Reserved UNIPHY and spare registers should not be assumed safe for arbitrary use. Their presence in a generated header does not imply stable semantics across ASIC revisions.

## Test Signals

Useful validation signals are mostly integration and hardware-facing rather than unit-test oriented:

- Build coverage for DCN316 display and DMUB code should catch missing macro names, duplicate definitions, or broken token-pasting with `REG_OFFSET_EXP`, `FD_MASK`, and `FD_SHIFT`.
- Register-table sanity checks should verify that DCN316 offsets use the intended base segment and that repeated instances advance consistently across DSC, HPO stream, symbol encoder, DPHY, and audio endpoint blocks.
- Display smoke tests should include panel power sequencing, modesets using DSC, HPO DP/HDMI output, multi-stream or multi-pipe routing, suspend/resume, and hotplug.
- Link diagnostics should exercise DP link training, CRC/debug reads, and HPO stream mapper paths.
- Audio tests should cover HDMI/DP audio enumeration, ELD/sink-info propagation, stream format changes, LPIB snapshots, hot-plug audio enable/disable status, and multi-channel/HBR-capable paths.
- Runtime logs or diagnostics showing DSC underflow/overflow, DPHY training failures, audio format changed interrupts, RIOMMU faults, or unexpected CRC deltas are strong signals to re-check these offsets against the generated source and ASIC tables.
