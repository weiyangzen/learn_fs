# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h lines 1-8494

## Scope And Purpose

This chunk is the first 8,494 lines of AMD's generated `soc24_enum.h` hardware enum header for SOC24-class AMDGPU blocks. It is a compile-time register-value contract, not executable logic: it defines enum names and exact numeric encodings used when programming SOC24 graphics, memory, SDMA, display, timing, link, audio, AUX, I2C, and interrupt-control registers.

The path sits under a `ceph-client` source mirror, but this file is AMDGPU hardware metadata. It is unrelated to Ceph filesystem protocol behavior except that it is part of the mirrored kernel source tree.

The header begins with the `_soc24_ENUM_HEADER` include guard and a non-`_DRIVER_BUILD` compatibility block mapping `GL__*` OpenGL-style blend names onto `BLEND_*` symbols when `GL_ZERO` is not already defined. The rest of this chunk is generated `typedef enum` declarations. There are no functions, structs, global variables, allocations, locks, direct MMIO reads/writes, or persistence code.

## Important APIs, Types, And Enums

The exported API is the generated enum namespace. Each enum value is intended to match a hardware field encoding exactly; consumers generally pass these values to register-field helper macros, packet builders, or hardware abstraction code that already knows the target register and bitfield.

Major enum families in this chunk:

- Command processor, cache, memory, and MMU encodings: `CP_PERFMON_ENABLE_MODE`, `CP_PERFMON_STATE`, `GL0V_CACHE_POLICIES`, `GL1_CACHE_POLICIES`, `GL1_CACHE_STORE_POLICIES`, `GL2_CACHE_POLICIES`, `GL2_NACKS`, `GL2_OP`, `GL2_OP_MASKS`, `Hdp_SurfaceEndian`, `MTYPE`, `TCC_MTYPE`, `SCOPE`, `GATCL1RequestType`, `UTCL0FaultType`, `UTCL0RequestType`, `UTCL1FaultType`, and `UTCL1RequestType`. These cover performance counter state, cache policy, L2 operation opcodes, endian mode, memory type, request scope, and retry/XNACK fault semantics.
- SDMA and streaming performance monitor values: `PERFMON_COUNTER_MODE`, `PERFMON_SPM_MODE`, `SDMA_PERFMON_SEL`, `SDMA_PERF_SEL`, and `SPM_PERFMON_STATE`. The SDMA selectors enumerate ring-buffer, IB, doorbell, context-change, cache/TLB invalidation, UTCL2, metadata, GCR, command operation, queue, and channel request/return events.
- Compression and cache policy controls: `READ_COMPRESSION_MODE`, `WRITE_COMPRESSION_MODE`, `ReadPolicy`, and `WritePolicy`, including bypass, raw-compressed, decompressed, stream, no-allocate, and cache-bypass selections.
- DPP/color/frontend display values: color/luma keying, denormalization, format crossbars, pixel expansion, pre-CSC/pre-degamma, `SURFACE_PIXEL_FORMAT`, cursor modes, scaler modes, line-buffer and output-buffer controls, sharpening, and the large CM/CMC LUT and color-matrix families. `SURFACE_PIXEL_FORMAT` maps hardware pixel-format codes for ARGB/RGBA, YCbCr, planar 4:2:0, packed 4:2:2, 10/12/16-bit, FP, RGBE, mono, and fixed/float 11:11:10 formats.
- Display CRC, perf counter, and hub/hubp setup: `CRC_*`, `TEST_CLK_SEL`, `PERFCOUNTER_*`, `PERFMON_*`, `BIGK_FRAGMENT_SIZE`, `CHUNK_SIZE`, `DPTE_GROUP_SIZE`, `META_CHUNK_SIZE`, `MIN_CHUNK_SIZE`, `VMPG_SIZE`, `VM_GROUP_SIZE`, `ROTATION_ANGLE`, `SWATH_HEIGHT`, and HUBP blanking, VTG, TTU, surface DCC, flip, stereo, TMZ, and update-lock enums.
- Cursor, metadata, hubbub, MPC, MPCC, DPG, FMT, OPP, and OTG display pipeline families. These define crossbar routing, memory power states, cursor pitch/snoop/stereo/TMZ/system-address modes, DMDATA update/underflow semantics, AXI-like response statuses, MPC/MPCC LUT/color/gamut/blending/stereo modes, display pattern generator bit depth/range/pattern, formatter dithering/clamping/subsampling, OPP CRC, and extensive OTG timing, update-lock, trigger, static-screen, vertical-interrupt, stereo, DRR, CRC, GSL, and flow-control values.
- DMCUB, RBBMIF, IHC, DMU, and DCCG values: DMCUB interrupt/timer-window encodings, invalid register access causes, GPU timer read selectors, interrupt destination/status, SMU interrupt controls, display clock gating, DTO source selection, deep-color DTO ratios, FIFO error detection, reference-clock selection, PHY/PLL pixel-rate sources, audio DTO choices, and clock/test mux controls.
- Link encoder and PHY values: DPHY 8b/10b, CRC, FEC, PRBS, training, fast training, component depth, compressed pixel format, DisplayPort pixel encoding, MST/MSE/MSO controls, DP secondary packet/audio/generic-stream packet controls, steering overflow, sync polarity, TU overflow, lane count, VBID, and stream disable/defer fields.
- DIG/HDMI/TMDS/DIO/I2C/DME/VPG/AFMT/AUX/HPD/HPO/stream-mapper values: DIG backend/front-end mode/source/stereo/fifo/test-pattern controls, HDMI ACR/audio/infoframe/null/generic/metadata packet controls, TMDS pattern and transmitter controls, DOUT I2C arbitration/DDC/EDID/transaction controls, DIO memory and clock gating, AFMT audio CRC/source/layout/infoframe/power controls, DP AUX arbitration/DPHY timing/GTC sync/interrupt/reset/timeout controls, HPD acknowledge/polarity, HPO test clock, and DP stream mapper targets.

The mapped range ends at line 8494 immediately after the first enumerator in `DP_STREAM_ENC_READ_CLOCK_CONTROL`; the enum closes on lines 8495-8496 outside this chunk. Final per-file reconciliation must merge the next chunk before treating that enum as complete.

## Control Flow And Runtime Behavior

There is no local control flow. Runtime behavior is created by code that includes this header and writes these enum values into SOC24 registers or command packets.

Typical usage pattern:

1. AMDGPU SOC24 code includes `soc24_enum.h` alongside register address, mask, and shift headers.
2. Higher-level driver logic chooses an enum value based on ASIC capability, display state, memory/cache policy, SDMA/perf event selection, link mode, or interrupt policy.
3. Register helpers pack the enum value into the appropriate field and perform the actual MMIO or indirect register operation.
4. Hardware persists or reports the resulting state until reset, power transition, reprogramming, or a hardware-owned status update changes it.

Direct include users in this tree include `amdgpu/gfx_v12_0.c`, `amdgpu/gfx_v12_1.c`, `amdgpu/gmc_v12_0.c`, `amdgpu/gfxhub_v12_0.c`, `amdgpu/mmhub_v4_1_0.c`, `amdgpu/mmhub_v4_2_0.c`, and `amdkfd/kfd_device_queue_manager_v12.c`. Display code also uses overlapping enum names and values such as surface formats through the DC hardware type layer; a search shows many `SURFACE_PIXEL_FORMAT_*` consumers in `display/dc`, `display/amdgpu_dm`, DPP, HUBP, DML, and resource calculation paths.

## State And Persistence Behavior

The header itself owns no state and persists nothing. The values describe stateful hardware fields whose side effects depend on the target register:

- configuration fields, such as cache policy, memory type, compression mode, pixel format, line buffer layout, update-lock mode, clock source, or AUX timing;
- action/handshake fields, such as reset, interrupt acknowledge, FIFO reset, AUX/I2C go, software trigger, or underflow clear;
- status selectors and readback encodings, such as invalid register access type, interrupt line status, DMCUB timer windows, DMU GPU timer sources, DPHY/FEC readiness, overflow/underflow status, and AUX arbitration state;
- power-management state, such as memory light/deep sleep/shutdown force/status controls across hub, MPCC MCM, formatter, DIO, DME, VPG, AFMT, DCOH, and HPO blocks.

Several enums intentionally use field-local names for identical `0`/`1` encodings. That is useful documentation and prevents mixing domains casually, but C does not enforce register-field compatibility once the value is used as an integer. Reserved values are present throughout and should remain preserved unless the hardware programming guide explicitly requires them.

## Dependencies And Integration Points

This generated enum header must stay synchronized with companion SOC24 register address and field headers under `drivers/gpu/drm/amd/include`, plus the display DC register programming layer that maps abstract DC state to hardware fields. It is part of the AMDGPU SOC24 contract for GFX12, GMC12, MMHUB/GFXHUB v12, KFD queue management, and DCN4-era display blocks.

Key integration surfaces:

- GFX/GMC/MMHUB/GFXHUB setup uses cache, MTYPE, GL2 operation, UTCL fault/request, scope, and perf monitor encodings.
- SDMA/KFD and performance tooling use the SDMA performance selector enums and perf counter state/mode enums.
- DC plane programming uses pixel-format, crossbar, DCC, swath/chunk/page, rotation, cursor, hubp, metadata, and surface flip/update-lock values.
- Color management uses CM/CMC/MPCC LUT, segment count, RAM selection, gamma, gamut remap, 3D LUT, coefficient format, and pending-state values.
- Timing and synchronization code uses OTG/OPTC/OPP CRC, trigger, DRR, GSL, vertical interrupt, stereo, update lock, static screen, and flow-control enums.
- Clock and power paths use DCCG, DCOH, HPO, PHY, PLL, DTO, deep-color, clock gating, soft reset, and memory-power enums.
- Display output paths use DP, HDMI, TMDS, DIG, DIO, DOUT I2C, AFMT audio/infoframe, DP AUX, HPD, stream mapper, and stream encoder values.

## Risks And Edge Cases

- Numeric values are ABI-like hardware contracts. A compile-clean value drift can silently program the wrong hardware behavior, especially for cache policy, GL2 opcodes, MTYPE, SDMA perf selectors, pixel formats, AUX timing, clock source selection, or interrupt acknowledge fields.
- The generated namespace is broad and not strongly typed at use sites. Many fields use generic names such as `ENABLE`, `BYPASS`, `SIGNED`, `INT_LEVEL`, `RESERVED_*`, or repeated `*_FALSE`/`*_TRUE` encodings; collisions or accidental cross-domain reuse are plausible in C.
- Some enum names preserve generated spelling, including apparent typos such as `SURFACE_INUSE_RAED_NO_LATCH`, `OPP_PIPE_DIGTIAL_BYPASS_CONTROL`, `FMT_CONTROL_SUBSAMPLING_MOME_*`, `OTG_3D_STRUCTURE_*_PROGRASSIVE`, and `DP_AUX_GTC_SYNC_CONTROL_OFFSET_CALC_MAX_ATTEMPT__*_ATTAMPS`. Renaming them for style would break consumers that depend on generated names.
- Reserved enumerators are explicit but not necessarily safe to write. Runtime code should use documented values and masked field writes rather than full-register writes that may alter adjacent reserved fields.
- Some values are active-low or counterintuitive: for example several `*_DIS_MODE` enums encode enable as `0`, many clock-gating disable controls encode enabled gating as `0`, and reset/ack/action fields may be pulse-like or self-clearing depending on the register.
- The chunk boundary splits `DP_STREAM_ENC_READ_CLOCK_CONTROL`; only `DP_STREAM_ENC_DCCG = 0` is inside this work item, while the second value and closing typedef are in the next lines.
- `SURFACE_PIXEL_FORMAT` here contains raw hardware encodings, while display DC code also defines abstract `SURFACE_PIXEL_FORMAT_*` values. Mapping between the two must be deliberate; raw enum values should not be assumed to match every software-facing DC enum.
- Power and link training fields often interact with timing-sensitive hardware state. Incorrect AUX timeout/precharge, DPHY training/FEC, HPD ack, I2C reset, or stream-disable values can cause display detection, link training, audio, or hotplug failures that are workload and monitor dependent.

## Test Signals

Useful validation for this chunk includes:

- Build AMDGPU with SOC24, GFX12/GMC12/MMHUB/GFXHUB, KFD, and DC display support enabled so include users and enum references compile.
- Mechanically compare `soc24_enum.h` against the authoritative generated SOC24 register database and companion address/mask headers.
- Check generated enum completeness and boundaries: every `typedef enum` started before line 8494 should close within the chunk except the intentionally split `DP_STREAM_ENC_READ_CLOCK_CONTROL`.
- Exercise GFX/GMC/KFD paths that program cache, MTYPE, MMU fault, queue, and performance monitor fields.
- Exercise SDMA performance counter selection and ring/doorbell/context-change paths under copy, VM invalidation, and queue workloads.
- Exercise display plane programming across RGB, YCbCr, 4:2:0, 10/12/16-bit, FP, DCC, cursor, rotation, flip, TMZ, and stereo/update-lock cases.
- Run DC color-management and CRC tests covering LUT RAM selection, gamma/PWL, gamut remap, 3D LUT, MPCC blending, OPP/OTG CRC, and formatter dithering/clamping/subsampling.
- Validate link/output behavior on DP, HDMI, TMDS, AUX, HPD, I2C/DDC, audio/infoframe, MST/MSO, FEC, fast-training, and hotplug scenarios.
- Watch for kernel warnings, failed MMIO assertions, bad CRCs, page faults/XNACK anomalies, SDMA perf counter mismatches, display underflow/overflow, AUX/I2C timeouts, link training failures, audio packet loss, incorrect pixel formats, and suspend/resume regressions.

## Cross-Chunk Notes

This is a large-file chunk for lines 1-8494 only. Later chunks are required to complete `DP_STREAM_ENC_READ_CLOCK_CONTROL` and the rest of `soc24_enum.h`. The final per-file document should merge all chunks before making whole-file claims about the generated SOC24 enum namespace.
