# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h lines 12836-15485

## Purpose

This chunk is generated AMD DCN 3.6.0 register-offset metadata. It contains no executable C logic; it exports `#define` constants for MMIO register offsets, per-register base-index selectors, and indirect-register indexes. Consumers pair these offsets with `dcn_3_6_0_sh_mask.h` field masks/shifts so AMDGPU display register-helper macros can build typed register tables for DCN 3.6 hardware.

The requested range starts inside the `DSCC2` Display Stream Compression block, then covers `DSCCIF2`, `DSC_TOP2`, `DC_PERFMON21`, full `DSCC3`/`DSCCIF3`/`DSC_TOP3`/`DC_PERFMON22`, HPO top and HDMI/DisplayPort stream/link encoder blocks, DLPC/DCHVM/DPIA control blocks, and Azalia audio endpoint/index spaces through input endpoint 7. Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata and does not implement Ceph or distributed filesystem behavior.

The slice contains 2,307 `#define` lines: 1,293 `reg*` MMIO offset/base-index macros and 1,014 `ix*` indirect register-index macros. The first line is a chunk-boundary continuation, `regDSCC2_DSCC_PPS_CONFIG2_BASE_IDX`, whose matching offset macro appears just before this range. The last macro is `ixAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME`, followed by the header guard close.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or direct I/O operations in this chunk. The exported interface is the generated macro namespace:

- `reg<block>_<REGISTER>`: a numeric MMIO register offset relative to the base selected by the companion base-index macro.
- `reg<block>_<REGISTER>_BASE_IDX`: the DCN register-base segment index used by `BASE(...)`/`BASE_INNER(...)` style token-paste helpers.
- `ix<block>_<REGISTER>`: an indirect register index, usually accessed through an endpoint or stream index/data window rather than direct MMIO.

Major macro families in this range:

- `DSCC2`, `DSCCIF2`, and `DSC_TOP2`: the tail of DSC instance 2. The covered registers include PPS config words 3-22, memory power control, squared-error and max-absolute-error telemetry, rate-buffer fullness telemetry, DSCCIF config, DSC top control, and DSC debug control.
- `DC_PERFMON21` and `DC_PERFMON22`: performance counter controls, state, high/low counter values, current-value interrupt/misc status, and per-block perfmon control for DSC instances 2 and 3.
- `DSCC3`, `DSCCIF3`, and `DSC_TOP3`: the complete offset block for DSC instance 3, including config/status, interrupt control/status, PPS config words 0-22, memory power, error metrics, rate-buffer fullness levels, interface config, top control, and debug control.
- HPO common and stream-mapper registers: `HPO_TOP_*`, `HPO_DP_STREAM_MAPPER_CONTROL*`, and stream-clock generation/enable registers for high-performance output routing.
- HPO HDMI instance 0: `HDMI_*`, `HDMI_FRL_*`, `HDMI_GC`, `HDMI_ACR*`, `HDMI_VBI_PACKET_CONTROL`, `HDMI_INFOFRAME_CONTROL*`, `HDMI_GENERIC_PACKET_CONTROL*`, `AFMT5_*`, `DME5_*`, `VPG5_*`, and `HDMI_TB_*` offsets. These cover HDMI link encoding, Fixed Rate Link encoding, stream encoding, audio/video infoframes, generic packets, audio formatter state, data-mapping engine state, video packet generator state, and timing bridge control.
- HPO DisplayPort stream encoders 0-3: repeated `DP_STREAM_ENC*`, `APG*`, `DME6-9`, `VPG6-9`, and `DP_SYM32_ENC*` groups. Each instance has video control/timing, M/N, MSA timing/colorimetry, secondary-data packet controls, VSC/DSC/PPS payload areas, audio packet registers, DSC/DB control, DME/VPG controls, and 32-bit symbol encoder controls.
- HPO DP link encoders 0-1 and DP PHY symbol blocks: `DP_LINK_ENC*` and `DP_DPHY_SYM32*` control, status, training, PRBS, debug, FIFO, CRC, and DPCSTX data/clock-lane controls.
- `DCHVM`, `DLPC`, and `DPIA_MU0`: host-VM control/flush, low-power/control-status, DPIA doorbell, request, reply, and command data offsets.
- Azalia output/audio indirect spaces: function-2 codec registers, audio descriptor registers 0-13, sink-description registers 0-17, sink info, input/output CRC result registers, input endpoint root/function parameters, stream latency/FIFO indexes for streams 0-15, and output endpoint 0-7 codec endpoint registers.
- Azalia input endpoint 0-7 indexes: input converter capability/control registers, input pin capability/control registers, multichannel/HBR/channel-allocation/hot-plug/configuration-default/LPIB/input-status/infoframe indexes.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU display code that includes the generated offset and shift/mask headers, then token-pastes names into register tables:

1. DCN 3.6 support includes `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h` from `dcn36_resource.c`, `irq_service_dcn36.c`, and `dmub_dcn36.c`.
2. Register-list macros such as `SR`, `SRI`, `SRII`, `SRII2`, `HWS_SF`, and stream-encoder/audio helper macros expand symbolic names into `BASE(reg..._BASE_IDX) + reg...` offsets and matching field masks/shifts.
3. Resource construction initializes DCN 3.6 tables for hardware sequencing, DIO, audio, stream encoders, clock/power control, VMID, IRQ handling, and DMUB service access.
4. Runtime paths call helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and `REG_WAIT`; those helpers use these constants to address the correct DCN 3.6 MMIO or indirect register.
5. Sequencing for DSC programming, HDMI/DP stream enable, packet/audio setup, HPO link training, DPIA mailbox traffic, hotplug handling, and interrupt acknowledgement lives in the consumers. This generated header only supplies addresses.

The macro names are part of the ABI between AMD's generated register database and the handwritten display driver tables. A typo or offset drift here is usually not caught by types; it either fails at compile time when a referenced macro is missing or silently targets the wrong hardware register.

## State And Persistence Behavior

This chunk stores no software state and persists nothing in memory or files. It describes hardware state reachable through DCN 3.6 direct MMIO and indirect index/data windows.

Represented hardware state includes DSC PPS/configuration and error telemetry, DSC interface/top/debug state, perfmon counter state, HPO output routing and clocking, HDMI FRL and stream/audio/infoframe packet state, DisplayPort stream timing/MSA/secondary-data/audio/DSC packet state, HPO DP link training and PHY symbol status, DCHVM host-VM flush/control state, DLPC low-power control/status, DPIA mailbox command/reply state, and Azalia codec/audio endpoint state.

Persistence is hardware-defined. Configuration registers usually retain programmed values until modeset reprogramming, stream teardown, clock/power gating, suspend/resume restore, GPU reset, or ASIC reset. Status, interrupt, error, counter, mailbox, sink, LPIB, CRC, and training registers may be read-only, sticky, write-one-to-clear, self-clearing, latched, or valid only while the relevant clock/power domain is enabled. This offset header does not encode those access semantics; consuming code and the hardware register specification must provide them.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.6.0 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h`, which provides matching field shifts and masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c`, which includes this header pair and builds DCN 3.6 register, shift, and mask tables for resource-pool and hardware-sequencer use.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c`, which includes this header pair for DCN 3.6 IRQ source register initialization.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c`, which initializes DMUB-visible DCN 3.6 register offsets with `BASE(reg..._BASE_IDX) + reg...`.
- Shared DIO and stream-encoder helpers under `display/dc/dio` and `display/dc/dce`, which consume HPO/DP/HDMI/AFMT-style register names through token-pasted register-list macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h`, whose Azalia endpoint register-list pattern maps endpoint index/data windows and codec capabilities onto generated `AZF0ENDPOINT` names.
- DSC helper code and register tables that consume `DSCC`, `DSCCIF`, and `DSC_TOP` offsets for programming PPS values, reading DSC state, and collecting compression diagnostics.

The most direct behavioral integration points for this slice are display compression setup, HPO HDMI/DP stream and link programming, HDMI/DP audio packetization, Azalia codec/endpoint discovery, DPIA communication, display low-power/host-VM control, and perfmon/debug telemetry.

## Risks And Edge Cases

- Generated offsets are untyped integer macros. A wrong value can compile cleanly while sending register reads/writes to the wrong block, wrong instance, or wrong indirect index.
- The range starts at an artificial boundary. `regDSCC2_DSCC_PPS_CONFIG2_BASE_IDX` is present without its matching offset macro in this chunk, so adjacent chunks are required for complete `DSCC2` coverage.
- Instance repetition is high-risk. DP stream encoders 0-3, APG/DME/VPG instances, endpoint 0-7 groups, and stream 0-15 groups are mechanically similar; a single instance-specific generator error can create connector-specific or stream-specific failures.
- HPO HDMI/DP offsets are sequencing-sensitive. Incorrect stream encoder, link encoder, symbol encoder, FRL, MSA, audio, infoframe, DSC/PPS, or generic-packet offsets can cause blank displays, bad link training, malformed packets, missing DSC enablement, or receiver-specific interoperability failures.
- Audio offsets affect both direct HDMI/DP packet generation and Azalia codec state. Incorrect AFMT, descriptor, sink-info, endpoint, HBR, multichannel, LPIB, hotplug, or input-status indexes can produce silent audio, wrong channel layout, bad sample-rate reporting, stale hotplug state, or broken position reporting.
- DSC and perfmon registers include status/counter/debug surfaces. Misaddressed error counters can hide compression faults or make diagnostics misleading even when normal modesets appear to work.
- DPIA mailbox and DCHVM/DLPC registers can have side effects. Wrong offsets can corrupt command/reply handshakes, host-VM flush behavior, low-power transitions, or interrupt/status acknowledgement.
- Base-index mismatches are as dangerous as offset mismatches. `*_BASE_IDX` values select the MMIO segment used by `BASE(...)`; a correct-looking register offset with the wrong base index can target a different address space.
- Access while a block is power gated or clock gated can hang, timeout, or return stale values. The header does not indicate which offsets require clocks, power domains, or reset deassertion.

## Test Signals

Useful validation combines generated-header checks with hardware behavior:

- Build AMDGPU display with DCN 3.6 enabled. Missing or renamed macros should fail in `dcn36_resource.c`, `irq_service_dcn36.c`, `dmub_dcn36.c`, and shared DIO/audio/stream-encoder table construction.
- Mechanically verify that each `reg*` offset in this range has the expected `reg*_BASE_IDX` pair, allowing the known chunk-boundary exception at the first line, and that all paired base indexes match the intended address block.
- Diff this range against AMD's authoritative DCN 3.6.0 register database and neighboring generated DCN headers where block layouts are expected to be compatible.
- Exercise DSC on every supported pipe/instance with compressed DisplayPort modes, DSC PPS programming, modeset/fast-modeset transitions, suspend/resume, and error telemetry reads.
- Exercise HPO HDMI FRL and HPO DP paths across link training, high bit rate modes, DSC, HDR/infoframe updates, generic packet sends, stream enable/disable, hotplug, MST/SST where applicable, and multi-display configurations.
- Validate HDMI/DP audio across plug/unplug, EDID/audio descriptor discovery, 2-channel and multichannel LPCM, HBR/compressed formats, sample-rate changes, mute/unmute, audio packet control, endpoint hotplug state, LPIB snapshots, and suspend/resume.
- Exercise DPIA paths with USB4/DP tunneling scenarios, mailbox request/reply traffic, virtual-link creation, unplug/replug, and error handling. Watch for command timeouts or mismatched reply data.
- Use register dumps or debug traces for representative `DSCC3`, `HPO_TOP`, `HDMI_*`, `DP_STREAM_ENC*`, `DP_LINK_ENC*`, `DPIA_MU0`, and `AZF0ENDPOINT*` offsets to confirm programmed addresses match expected base-index plus offset calculations.
- Monitor kernel logs for `REG_WAIT` timeouts, IRQ storms, missed hotplug/audio events, bad DSC state, link-training failures, FIFO/CRC/perfmon anomalies, and resume-only display or audio regressions.

## Cross-Chunk Notes

Earlier chunks contain the start of `dcn_3_6_0_offset.h`, including the beginning of `DSCC2` and the offset partner for this chunk's first `DSCC2` base-index macro. This chunk reaches the end of the file and closes the header guard. The final per-file research document should merge adjacent chunks before making whole-file claims about all DCN 3.6.0 offsets or all repeated DSC, HPO, DPIA, and Azalia instances.
