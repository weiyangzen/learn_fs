# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h lines 10423-13004

## Scope

This chunk covers lines 10423-13004 of the generated DCN 3.0.1 register-offset header. The content is preprocessor data: `#define` constants mapping AMD display hardware register names to register offsets, plus matching `*_BASE_IDX` selector constants for MMIO base table selection. There are no C functions, types, or executable control-flow constructs in this span.

Within this chunk there are 2390 preprocessor defines: 1613 register/index offset macros and 777 `*_BASE_IDX` companion macros. The first line continues the previous `MPCC_OGAM0` block, and the final line ends mid-pattern inside the `azf0endpoint7_endpointind` block; whole-file reconciliation must account for neighboring chunks.

## Purpose

The header gives the AMDGPU DC display driver stable symbolic names for DCN 3.0.1 hardware registers. Driver code can refer to register names such as `mmMPC_CLOCK_CONTROL`, `mmABM0_BL1_PWM_USER_LEVEL`, or `ixAZF0ENDPOINT6_AZALIA_F0_CODEC_PIN_CONTROL_LPIB` without embedding numeric offsets directly. The `mm` names are memory-mapped display registers; the `ix` names are indexed/indirect register offsets used through an index/data access path.

This chunk specifically covers late MPC/MPCC color-processing registers, ABM backlight/statistics registers, legacy VGA indexed registers, and Azalia/HD-audio codec, stream, CRC, and endpoint register indices.

## Main Register Groups

- `MPCC_OGAM0` tail: starts at the continuation of output gamma RAM A/B region and gamut remap macros, including `RAMA_REGION_*`, `RAMB_START_*`, `RAMB_END_*`, `RAMB_OFFSET_*`, `RAMB_REGION_*`, and `MPC_GAMUT_REMAP_*` definitions.
- `MPCC_OGAM1`, `MPCC_OGAM2`, and `MPCC_OGAM3`: complete repeated output-gamma blocks at base addresses `0x200`, `0x400`, and `0x600`. Each block exposes LUT index/data/control, RAM A/B piecewise gamma controls for B/G/R channels, region tables, gamut remap format/mode, and two banks of 3x4 remap coefficients.
- `MPC_CFG`: global MPC control/status registers such as clock control, soft reset, CRC control/results, perfmon event selection, bypass background values, host read control, DPP pending status, pending misc status, VUPDATE lock sets 0-3, and DWB mux selection.
- `MPC_OCSC`: output mux, denormalization clamp, and output color-space-conversion definitions for outputs 0-3. The repeated `MPC_OUT*_CSC_*` macros define mode and coefficient banks A/B.
- `MPC_RMU`: retiming/mapping unit color pipeline registers including RMU control/memory power, shaper LUT controls, shaper RAM A/B controls and regions for RMU0/RMU1, and 3D LUT mode/index/data/output normalization/offset registers.
- `DC_PERFMON21`: display performance counter and monitor control/state/value macros for perfmon instance 21.
- `ABM0` through `ABM3`: OPP adaptive backlight management blocks at base addresses `0x0`, `0x104`, `0x208`, and `0x30c`. Each exposes PWM ambient/user/target/current/final/minimum levels, ABM control, update sample rate, register lock, histogram/gather controls, luma statistics, histogram result bins 1-24, and backlight master lock.
- `vga_*ind`: indexed VGA sequencer, CRT controller, graphics controller, and attribute controller register indices.
- `azendpoint_f2codecind`, `azinputendpoint_f2codecind`, and `azroot_f2codecind`: Azalia function 2 codec, input codec, pin, root, converter, power, stream format, multichannel, sink-info, LPIB, coding, format-change, and keepalive indices.
- `azendpoint_descriptorind` and `azendpoint_sinkinfoind`: audio descriptor and audio sink metadata index constants.
- `azf0controller_*crc*ind`: Azalia input/output CRC result channel index constants.
- `azf0stream0` through `azf0stream15`: repeated FIFO size and latency counter indices for 16 Azalia streams.
- `azf0endpoint0` through `azf0endpoint7`: repeated endpoint register index maps. This chunk fully covers endpoints 0-6 and starts endpoint 7, with converter capability/control, pin capability/control, descriptor, multichannel, sink, hot-plug, channel-status override, LPIB, coding, format-change, wireless display, remote keepalive, and audio enable/interrupt status indices.

## Important APIs, Types, and Macros

The exported API surface is entirely macro names consumed by register access helpers elsewhere in the AMD display driver. Important naming conventions:

- `mm...` macros map direct MMIO register names to offsets in the selected ASIC register base space.
- `ix...` macros map indirect/indexed register names to index values.
- `..._BASE_IDX` macros, all visible examples in this chunk using value `3`, identify the register base index used by generated access macros and register tables.
- Instance numbers are encoded in the macro name, for example `MPCC_OGAM1`, `MPC_OUT3`, `ABM2`, `AZF0STREAM15`, and `AZF0ENDPOINT6`.
- Repeated hardware blocks preserve the same local register layout while shifting the direct MMIO offsets by block instance. For example, `MPCC_OGAM1` begins at `0x0180`, `MPCC_OGAM2` at `0x0200`, and `MPCC_OGAM3` at `0x0280`.

There are no structs, enums, inline functions, function pointers, or C symbols with storage duration in this chunk.

## Control Flow and Data Flow

This header chunk has no runtime control flow. Its data flow is compile-time substitution:

1. The C preprocessor expands symbolic register names into numeric offsets.
2. Register-access macros or generated register lists in the display driver pair those offsets with `*_BASE_IDX` values.
3. The driver then performs MMIO or indexed register reads/writes against the GPU display hardware.

The effective runtime behavior is therefore defined by consumer code, not by this header. Typical consumers will program color pipelines, backlight behavior, audio endpoints, or collect diagnostics by reading/writing the offsets declared here.

## State and Persistence

The file itself maintains no software state and has no persistence behavior. The constants address hardware state:

- MPCC/MPC OGAM, CSC, shaper, gamut remap, and 3D LUT registers hold display color-pipeline configuration.
- MPC status, CRC, perfmon, pending, and VUPDATE lock registers expose transient display-controller state and synchronization controls.
- ABM registers hold or report backlight control levels, luma statistics, histogram bins, and lock state.
- Azalia stream, endpoint, codec, CRC, and sink-info indices represent audio hardware or monitor/codec state exposed through indexed register windows.

Incorrect constants can persistently affect the live display session until the driver reprograms hardware or the device is reset, even though the constants themselves are stateless.

## Dependencies and Integration Points

This chunk depends on the AMD DCN 3.0.1 hardware register layout generated from ASIC register descriptions. It integrates with:

- AMDGPU display core register access helpers that concatenate register base addresses, offsets, masks, and shifts.
- DC color-management code that writes OGAM, gamut remap, output CSC, shaper, and 3D LUT registers.
- MPC/MPCC composition and output-pipeline setup code that programs muxes, resets, clocks, CRC, and update locks.
- OPP/ABM code that programs adaptive backlight behavior and reads histogram/luma statistics.
- Display audio/Azalia code that uses `ix` indexed constants for codec, pin, stream, endpoint, sink, and CRC operations.
- Diagnostic and validation code reading CRC/perfmon/status registers.

The neighboring offset and shift/mask headers must remain in sync with this file. A register offset without matching mask/shift definitions, or vice versa, is a strong signal of generator or integration drift.

## Risks

- The file is generated-style hardware ABI data; hand edits are risky because a one-value mismatch can redirect a register write to unrelated hardware.
- Repeated blocks are easy to misalign. A missing or shifted macro in one instance of `MPCC_OGAM*`, `ABM*`, stream, or endpoint blocks could affect only one display pipe/audio endpoint and be hard to notice in broad tests.
- The chunk starts and ends inside larger repeated patterns, so merge/reconciliation must not infer completeness from this chunk alone.
- Direct `mm` offsets and indirect `ix` indices are different address spaces; using an `ix` value through a direct MMIO path, or an `mm` value through an indexed path, would be a consumer bug with potentially confusing symptoms.
- `*_BASE_IDX` value consistency matters. The visible direct-register base index value is consistently `3`; changing this would alter address-base selection for consumers.
- ABM and color-pipeline register errors can manifest as visible color/gamma/backlight defects rather than compile failures.
- Azalia endpoint/index errors can manifest as HDMI/DP audio failures, incorrect sink capabilities, stale LPIB snapshots, or missed audio enable/format-change interrupts.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing:

- Build tests that include DCN 3.0.1 display headers and compile AMDGPU register access users without undefined macro errors.
- Generator consistency checks comparing this offset header against its corresponding mask/shift header and source ASIC register database.
- Display color-management tests exercising OGAM LUT programming, gamut remap, output CSC, shaper LUTs, and 3D LUT paths on DCN 3.0.1 hardware.
- Multi-pipe display tests covering MPCC OGAM instances 0-3 and output CSC instances 0-3.
- ABM/backlight tests on panels supporting adaptive backlight, checking PWM level programming, luma histogram reads, sample rates, and lock behavior across ABM0-ABM3.
- CRC/perfmon diagnostics validating `MPC_CRC_*`, `DC_PERFMON21_*`, and Azalia CRC result indices.
- HDMI/DP audio tests covering codec root/function parameters, converter format, channel/stream IDs, hot-plug/audio-enable interrupts, LPIB snapshots, sink info, multichannel controls, HBR, and endpoints 0-7.
- Runtime register tracing can confirm that consumers write expected offsets and do not mix direct MMIO and indexed-register access paths.

## Open Questions for Merge

- The prior chunk should include the start of `MPCC_OGAM0`, including its control, LUT, RAMA start/end, and early region macros before this chunk begins at `RAMA_REGION_6_7_BASE_IDX`.
- The following chunk should complete `azf0endpoint7_endpointind`, because this chunk ends after the early endpoint-7 pin-control/audio-descriptor definitions.
- Whole-file synthesis should verify how many MPCC OGAM, ABM, Azalia stream, and endpoint instances are expected for DCN 3.0.1 and flag any missing instance only after all chunks are available.
