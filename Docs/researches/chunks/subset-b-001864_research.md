# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h lines 12819-15195

## Purpose

This chunk is generated AMD DCN 3.1.5 register-address metadata. It contains no executable C logic; it publishes preprocessor constants for hardware register offsets, indexed-register offsets, and per-register base-segment selectors used by AMDGPU display code. The companion `dcn_3_1_5_sh_mask.h` header supplies field shifts and masks for the same register namespace.

Although this source tree is under a local `ceph-client` mirror, this file is AMDGPU display-driver hardware metadata and has no Ceph or distributed filesystem behavior.

The requested range is the tail of the file. It starts inside the HPO HDMI stream encoder 0 DME block, then covers HPO HDMI VPG5, HPO DP stream encoders 0 through 3, APG0 through APG3, DME6 through DME9, VPG6 through VPG9, DP 32-symbol encoders 0 through 3, HPO DP link encoders 0 through 1, DP DPHY SYM32 blocks 0 through 1, DCHVM, HDA/Azalia controller/root/stream/endpoint/input-endpoint registers, legacy VGA indexed windows, and indexed Azalia endpoint windows. The chunk has 2,042 `#define` lines: 1,555 register or indexed-register offset constants and 487 `_BASE_IDX` constants.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, locks, allocations, or direct persistence APIs in this line range. Its public interface is the generated macro naming convention:

- `reg<REGISTER_OR_BLOCK_REGISTER>`: MMIO register offset within a generated base segment.
- `reg<REGISTER_OR_BLOCK_REGISTER>_BASE_IDX`: segment selector consumed by `BASE(reg..._BASE_IDX)` helper macros.
- `ix<INDEXED_REGISTER>`: indexed-register offset used through an index/data register window rather than direct MMIO.

Important register families in this chunk:

- HPO HDMI residual blocks: the chunk begins with the final `DME5_DME_CONTROL` base selector and `DME5_DME_MEMORY_CONTROL`, then lists `VPG5` generic packet access/data, frame/immediate update controls, status, memory power, ISRC data, and MPEG info registers for HPO HDMI stream encoder 0.
- HPO DP stream encoders 0 through 3: `DP_STREAM_ENC*_DP_STREAM_ENC_CLOCK_CONTROL`, input mux, audio control, clock-ramp FIFO status/control, and spare registers.
- DP APG and DME blocks: `APG0` through `APG3` audio packet generator control/status/debug/CRC/memory-power/spare registers and `DME6` through `DME9` control and memory-control registers.
- DP VPG blocks: `VPG6` through `VPG9` generic packet access/data, GSP update controls, status, memory power, ISRC, and MPEG info registers.
- DP SYM32 encoders 0 through 3: control, FIFO control, MSA double-buffer and MSA0 through MSA8, pixel format, HBLANK, SDP/GSP controls, audio/metadata packet controls, stream/VBID/panel replay, CRC control/results/status, memory-power, and spare registers.
- HPO DP link and DPHY blocks: link-encoder control, vid/audio stream enables, link-test pattern, training, error-status, CRC, clock controls, main-link channel coding, PHY control, and DPHY SYM32 control/status/debug/test/CRC/memory-power registers.
- `DCHVM`: display core host-VM control, aperture, fault address, VMID, and memory power registers.
- HDA/Azalia direct registers: controller capability/status/control, DMA/RIRB/CORB, stream descriptors 0 through 7, root codec parameters, audio DTO, audio wall-clock, clock gating, CRC controls/results, endpoint and input-endpoint index/data windows, and memory-power control/status.
- Legacy VGA indexed windows: sequencer, CRT controller, graphics controller, and attribute-controller indexed constants.
- Azalia indexed windows: codec function, descriptor, sink info, stream 0 through 15, endpoint 0 through 7, and input endpoint 0 through 7 indexed register constants.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code that includes this generated DCN 3.1.5 offset header and expands register-list macros.

Typical flow:

1. DCN315 resource, DMUB, IRQ, and GPIO code include `dcn_3_1_5_offset.h` together with `dcn_3_1_5_sh_mask.h`.
2. Resource code expands `SR`, `SRI`, `SF`, `SE_SF`, and related token-paste helpers into register tables. For example, `dcn315_resource.c` builds audio, VPG, AFMT, APG, stream encoder, HPO DP stream encoder, HPO DP link encoder, hardware sequencer, and VMID register tables.
3. HPO DP stream-encoder helpers use `DCN3_1_HPO_DP_STREAM_ENC_REG_LIST(id)` with `SRI(DP_STREAM_ENC_..., DP_STREAM_ENC, id)` and `SRI(DP_SYM32_ENC_..., DP_SYM32_ENC, id)`, so the DP stream and SYM32 offsets in this chunk become concrete addresses for instances 0 through 3.
4. Audio helpers use `AUD_COMMON_REG_LIST(id)` and DCN315-specific masks to create Azalia endpoint register tables. Indexed `ixAZF0ENDPOINT*` and `ixAZF0INPUTENDPOINT*` constants describe the codec windows reached through endpoint index/data registers.
5. Runtime display, link, audio, interrupt, and firmware paths then use the populated tables through register access helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_GET`, and Azalia index/data access wrappers.

The offsets do not encode ordering or access side effects. Consumers must still follow hardware programming sequences around clock enablement, reset assertion/release, FIFO reset completion, stream disable/enable, packet double buffering, indexed-window address/data ordering, audio DMA/ring management, hotplug behavior, memory power gating, and suspend/resume restore.

## State And Persistence Behavior

The chunk stores no software state and persists nothing on disk. It names MMIO and indexed registers whose values live in GPU display hardware.

State represented by these definitions includes:

- HPO DP and HDMI packet state: generic packet RAM access, GSP frame/immediate update controls, ISRC and MPEG metadata, VPG/DME memory power, and stream packet status.
- HPO DP stream and symbol state: stream encoder clocks, pixel/audio input muxing, clock-ramp FIFO reset/enable/status, DP SYM32 reset/enable, pixel format, MSA data, HBLANK policy, SDP/GSP packet controls, audio sideband packet enables, metadata packet enables, VBID and panel replay state, CRC controls/results, and memory power.
- DP link/PHY state: link-encoder enable and training controls, channel coding, test patterns, CRC, error status, DPHY test/debug/status controls, and link/PHY memory power.
- HDA/Azalia state: controller command/status, CORB/RIRB/DMA positions, stream descriptor buffer and format registers, codec root parameters, audio wall-clock and DTO configuration, audio CRC, endpoint/input endpoint index/data windows, sink-info and descriptor indexed data, and codec power/reset/connectivity fields.
- Legacy VGA indexed state: sequencer, CRT controller, graphics controller, and attribute-controller index spaces that can still be exposed for VGA compatibility paths.
- DCHVM state: host VM aperture, fault address/VMID reporting, and host-VM memory power/control registers.

Persistence is hardware-defined. Some registers are configuration values that remain until modeset, reset, power gating, suspend/resume, or ASIC reset. Others are read-only status, sticky error, write-one-to-clear, self-clearing request, or index/data window entries. This generated offset header does not express those access classes; the display code and ASIC documentation supply that context.

## Dependencies And Integration Points

This chunk must match the generated DCN 3.1.5 register database and its companion field-layout header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h`

Direct include sites found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_translate_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`

Key integration points:

- `dmub_dcn315.c` expands `DMUB_DCN31_REGS()`, `DMCUB_INTERNAL_REGS()`, and `DMUB_DCN315_FIELDS()` into `dmub_srv_dcn315_regs`. This chunk is mostly outside the DMCUB-specific register list, but it shares the same `BASE(reg..._BASE_IDX) + reg...` contract used throughout the generated file.
- `dcn315_resource.c` directly uses HPO DP stream encoder offsets from this chunk via `DCN3_1_HPO_DP_STREAM_ENC_REG_LIST(id)` and `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST`. It also uses Azalia endpoint offsets through `audio_regs[]`, `DCE120_AUD_COMMON_MASK_SH_LIST`, `AZALIA_AUDIO_DTO`, and hardware sequencer register lists.
- `dcn31_hpo_dp_stream_encoder.h` defines the common DCN3.1 HPO DP stream-encoder register and field lists that token-paste names such as `DP_STREAM_ENC0_DP_STREAM_ENC_CLOCK_CONTROL` and `DP_SYM32_ENC0_DP_SYM32_ENC_CONTROL`; those exact instance-0 names and instance-specific offsets are present in this chunk.
- `dce_audio.h` and `dce_audio.c` use `AZF0ENDPOINT*` endpoint index/data registers to program codec capabilities, rates, power-state bits, hotplug control, ELD/sink information, and audio format behavior.
- `irq_service_dcn315.c` and GPIO translation/factory code include the same offset header to build IRQ and GPIO register tables. Their direct use is mostly in earlier line ranges, but they depend on the whole header remaining a coherent generated unit.

## Risks And Edge Cases

- Generated offset drift is the main risk. A wrong constant compiles cleanly but causes register helpers to access the wrong MMIO address or indexed slot.
- The chunk starts in the middle of the `dce_dc_hpo_hdmi_stream_enc0_dme_dme_dispdec` block. The `regDME5_DME_CONTROL` offset and address-block comment are in the previous chunk, while `regDME5_DME_CONTROL_BASE_IDX` and `regDME5_DME_MEMORY_CONTROL` are here. File-level reconciliation must merge the adjacent chunk before treating DME5 as complete.
- HPO DP stream/SYM32 offsets are modeset critical. Bad clock-control, input-mux, FIFO reset/status, reset-done, pixel-format, MSA, stream-enable, VBID, HBLANK, or packet-control offsets can cause a blank display, link-training failures, malformed sideband data, incorrect audio packetization, or CRC diagnostics that point at the wrong block.
- VPG/APG/DME packet registers are update-order sensitive. Generic packet RAM access and frame/immediate update controls must be programmed with the expected double-buffer or frame-boundary semantics, otherwise infoframes, ISRC data, MPEG metadata, and audio packets can be stale or torn.
- HPO DP link and DPHY offsets affect physical link behavior. Wrong training, test-pattern, channel-coding, CRC, or error-status addresses can make link bring-up fail or hide real PHY faults.
- Azalia has both direct MMIO and indexed-register windows. Mixing endpoint instances, index constants, or data-window offsets can program the wrong codec node, stream descriptor, sink info, channel allocation, hotplug control, or power-state register.
- Audio stream descriptor registers are DMA-facing. Incorrect `AZSTREAM*` buffer, length, format, control, status, or LPIB offsets can corrupt audio playback/capture state or leave DMA/ring interrupts stuck.
- Legacy VGA indexed constants may look obsolete but still participate in compatibility paths. Wrong VGA index values can disturb low-level display state during firmware handoff, resume, or fallback modes.
- Memory power control registers for VPG/APG/SYM32/DPHY/Azalia/DCHVM must be touched only when the corresponding block is idle or in the documented transition sequence.

## Test Signals

Useful validation combines build checks, generated-header consistency checks, and hardware behavior:

- Build AMDGPU/DC with DCN315 enabled. Missing or renamed macros should fail in `dmub_dcn315.c`, `irq_service_dcn315.c`, `hw_factory_dcn315.c`, `hw_translate_dcn315.c`, and `dcn315_resource.c`.
- Mechanically verify that every direct `reg...` macro in this chunk that represents an MMIO register has the expected `_BASE_IDX` companion, while allowing indexed `ix...` constants and the known DME5 boundary split.
- Compare the offsets against AMD's authoritative DCN 3.1.5 register database and adjacent generated DCN 3.1.x headers where register layouts are expected to remain compatible.
- Exercise HPO DP modesets on all available stream/link encoder instances: clock enable, FIFO reset/done polling, pixel/audio stream muxing, MSA programming, SDP/GSP metadata packets, audio sideband packets, stream enable/disable, HBLANK control, panel replay bits, and CRC readback.
- Exercise HPO HDMI/DP packet paths: VPG generic packet RAM access, ISRC/MPEG infoframes, GSP frame/immediate updates, APG audio packet control/status, and DME memory-control transitions.
- Exercise DP link and PHY diagnostics: link training, test patterns, channel coding, CRC, DPHY status/error/debug registers, and memory power transitions.
- Exercise HDMI/DP audio through Azalia: endpoint index/data accesses, codec capability reads, supported rate/power-state reads, stream descriptor setup, CORB/RIRB behavior, DMA position/LPIB reporting, hotplug control, channel allocation, ELD/sink info, audio DTO, and audio CRC.
- Exercise suspend/resume and display power-gating paths that touch VPG/APG/SYM32/DPHY/Azalia/DCHVM memory-power registers and ensure registers are restored or reprogrammed in the expected order.
- Exercise legacy VGA handoff or fallback modes, if supported, to catch regressions in sequencer/CRT/graphics/attribute indexed windows.

## Cross-Chunk Notes

The previous chunk owns the beginning of the HPO HDMI stream encoder 0 DME5 block, including the address-block comment and `regDME5_DME_CONTROL` offset. This chunk owns the DME5 tail, the rest of the file's offset/index definitions, and the final `#endif`. The final per-file research document should merge adjacent chunks before making complete claims about DME5 coverage or full-file generated-header structure.
