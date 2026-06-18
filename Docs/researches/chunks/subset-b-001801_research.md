# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h lines 12817-15089

## Purpose

This chunk is the final generated offset slice for the DCN 3.1.2 register-address header. It contains C preprocessor constants that map symbolic AMD display/audio register names to MMIO register offsets or indirect-register indices, plus companion `*_BASE_IDX` constants for directly addressed display registers. The range starts at the tail of the DSC2 compressor block, covers HPO top/stream/link/audio packet blocks, then ends with VGA and Azalia/HD-audio indirect index definitions through `azf0inputendpoint7_inputendpointind`.

The file has no executable code. Its purpose is to provide the address half of the generated ASIC register ABI used by the AMDGPU DC display stack. Runtime code includes this header together with generated shift/mask headers and register-list macros so it can program DCN 3.1.2 display hardware without hard-coding numeric offsets in functional C code.

## Important APIs, Types, And Register Groups

- `regDSCC2_*`, `regDSCCIF2_*`, `regDSC_TOP2_*`, and `regDC_PERFMON21_*` finish DSC instance 2. The visible DSCC tail covers rate-buffer and rate-control maximum fullness levels plus debug-bus rotate; DSCCIF and DSC top expose configuration/control/debug offsets; the DSC perfmon block exposes counter control, state, interrupt/misc current value, and high/low readback registers.
- `regHPO_TOP_*`, `regDP_STREAM_MAPPER_CONTROL0..3`, and `regDC_PERFMON22_*` define the high-performance output top-level clock/hardware control, stream mapper routing controls, and HPO perfmon counter/readback registers.
- `regAFMT5_*`, `regDME5_*`, and `regVPG5_*` describe the HPO HDMI stream encoder 0 sideband/audio packet path. AFMT5 covers VBI/audio packet controls, audio info, IEC 60958 words, CRC, ramp controls, status, infoframe control, interrupt status, source control, and memory power. DME5 provides DME control and memory control. VPG5 covers generic packet access/data, generic packet frame/immediate updates, status, memory power, ISRC access/data, and MPEG info registers.
- `regDP_STREAM_ENC0_*` through `regDP_STREAM_ENC3_*` define four HPO DP stream encoder instances. Each stream encoder has clock control, input mux, audio control, clock-ramp-adjuster FIFO status controls, and a spare register.
- `regAPG0_*` through `regAPG3_*`, `regDME6_*` through `regDME9_*`, and `regVPG6_*` through `regVPG9_*` attach APG audio packet generators, DME blocks, and VPG packet generators to the DP stream encoders. The APG instances expose main/debug/packet controls, audio CRC controls/results, status/status2, memory power, and spare offsets.
- `regDP_SYM32_ENC0_*` through `regDP_SYM32_ENC3_*`, `regDP_LINK_ENC0_*`/`regDP_LINK_ENC1_*`, and `regDP_DPHY_SYM320_*`/`regDP_DPHY_SYM321_*` describe HPO DP transport/link hardware. They include stream packer controls, link/lane/frame controls, SDP and MST controls, HDCP/metadata/secondary-data controls, FIFO/debug/state/status registers, PHY symbol controls, DPHY misc/clock-pattern/skew controls, and DPHY test/debug registers.
- `regDCHVM_*` provides display HVM/DCHVM clock/reset, page table, control/status, debug, register-read data, and test-debug bus offsets. Unlike most nearby HPO blocks, this block has base address `0x0` and `BASE_IDX` 1 in the visible definitions.
- `ixSEQ*`, `ixCRT*`, `ixGRA*`, and `ixATTR*` are legacy VGA indexed-register constants. They are indirect indices rather than direct MMIO offsets and cover sequencer, CRT controller, graphics controller, and attribute controller registers.
- `ixAZALIA_*`, `ixAUDIO_DESCRIPTOR*`, and `ixSINK_DESCRIPTION*` define Azalia/HD-audio codec and sink-info indirect indices, including converter and pin parameters/control, audio descriptors 0-13, sink info 0-8, hotplug/unsolicited/configuration response controls, LPIB snapshot registers, audio enable/format interrupt status, and root/audio function-group metadata.
- `ixAZF0STREAM0_*` through `ixAZF0STREAM15_*` define per-stream indirect indices for stream descriptor status/control, link position in current buffer, cyclic buffer length, FIFO size, and format.
- `ixAZF0ENDPOINT0_*` through `ixAZF0ENDPOINT7_*` repeat the output endpoint codec converter and pin-control register index set for eight endpoints. `ixAZF0INPUTENDPOINT0_*` through `ixAZF0INPUTENDPOINT7_*` repeat the smaller input endpoint converter/input-pin index set for eight input endpoints.

The direct `reg*` macros use generated MMIO offsets and, for this chunk, mainly `BASE_IDX` 2 or 3 depending on address space. The `ix*` macros are indirect register indices and intentionally do not have `BASE_IDX` companions.

## Control Flow

There is no C control flow in this chunk. The effective runtime flow is created by display and audio driver code that:

1. Selects the correct generated register list for DCN 3.1.2.
2. Chooses an instance-specific macro such as a DP stream encoder, APG, VPG, link encoder, DPHY, DSC, perfmon, or Azalia endpoint constant.
3. Combines the offset with the selected base index or indirect-access path.
4. Uses AMDGPU/DC register helpers to perform MMIO reads/writes, read-modify-write operations with shift/mask macros, or indexed Azalia/VGA accesses.
5. Polls or clears status/interrupt/debug registers where required by the block programming sequence.

The register families imply several hardware programming sequences even though the header does not encode them: HPO top clocks and hardware control before stream/link programming; stream mapper and input mux routing before enabling DP/HDMI encoders; APG/VPG/AFMT packet memory and packet controls before sending audio/infoframes; link encoder and DPHY setup before training or enabling DP transport; perfmon counter selection before reading high/low values; and Azalia converter/pin setup through indirect command/index paths before exposing display audio streams.

## State And Persistence Behavior

The macros themselves are compile-time constants and have no mutable state. The hardware registers they identify hold device state until changed by driver writes, hardware events, reset, suspend/resume, power gating, or a new modeset/audio reconfiguration.

Persistent or stateful hardware surfaced by this chunk includes DSC rate-control fullness/debug state, HPO clock/hardware enable state, DP stream routing, HDMI/DP audio packet generator state, infoframe/generic packet memory contents, APG/AFMT/VPG/DME memory power state, stream encoder FIFO/status/debug state, DP link encoder and DPHY lane/symbol/test state, DCHVM page-table/control/status registers, VGA indexed state, and Azalia codec endpoint/stream/pin state.

Several constants name readback or event registers rather than ordinary configuration registers, for example `*_STATUS`, `*_INTERRUPT_STATUS`, `*_CRC_RESULT`, `*_PERFCOUNTER_STATE`, `*_PERFMON_LOW`, `*_PERFMON_HI`, `*_TEST_DEBUG_*`, `*_LPIB`, and audio enable/format interrupt status indices. Access semantics such as read-only, write-one-to-clear, latched readback, or indirect-index side effects are defined by the hardware spec and the functional driver code, not by this offset header.

## Dependencies And Integration Points

This header is included by DCN 3.1 code paths such as DMUB support, IRQ service setup, and DCN 3.1 resource construction. It is useful only with the matching generated DCN 3.1.2 shift/mask headers and AMD display register-helper machinery. The generated names must match register-list initializers and macro expansions used throughout the AMD display stack.

The direct HPO/DSC/DCHVM definitions integrate with MMIO register access paths. Their `BASE_IDX` values select the correct register aperture in the generated register infrastructure. The Azalia and VGA `ix*` definitions integrate through indexed register access paths, where the value is an index written to an indirect register interface rather than an MMIO address.

The chunk is also tied to hardware instance topology. It defines DP stream encoders 0-3, APG instances 0-3, VPG instances 5-9, DME instances 5-9, DP link encoders 0-1, DPHY symbol blocks 320-321, Azalia streams 0-15, output endpoints 0-7, and input endpoints 0-7. Higher-level code can abstract instance selection, but build correctness depends on the generated per-instance names and offsets remaining exact.

## Risks And Edge Cases

- Offset drift is high impact: a single incorrect numeric value can direct a write to the wrong hardware register while still compiling cleanly.
- The chunk mixes direct MMIO offsets and indirect indices. Treating an `ix*` Azalia/VGA constant as a direct `reg*` offset, or losing a `BASE_IDX` on a direct register, would route access through the wrong mechanism.
- Repeated instance blocks are vulnerable to generation or copy drift. DP stream encoders, APG/VPG/DME instances, Azalia streams, and endpoint/input-endpoint sets should remain structurally consistent except where the hardware intentionally differs.
- HPO DP/HDMI blocks are sequencing-sensitive. Programming stream encoders, packet generators, link encoders, or DPHY registers while clocks, memory power, stream mapping, or link state are wrong can cause blank displays, bad infoframes/audio, CRC failures, link-training failures, or hangs.
- Packet and audio registers have externally visible behavior. Bad AFMT/APG/VPG/Azalia offsets can produce missing audio, wrong channel allocation, incorrect infoframes, stale ISRC/MPEG metadata, or spurious hotplug/unsolicited responses.
- Perfmon, CRC, and debug registers may be readback or latched state. Misclassifying status/ack behavior in caller code can leave interrupts asserted or produce misleading diagnostics.
- The chunk starts in the middle of the DSCC2 register list. Whole-file reconciliation must combine this with the previous chunk to present DSC2 as a complete block.

## Test Signals

- Build coverage should catch missing, renamed, or malformed macro names in DCN 3.1.2 register-list consumers, including DMUB, IRQ, and resource code that includes this header.
- Generated-header comparison against the ASIC register database should validate numeric offsets, base indices, and repeated instance consistency across DP stream encoders, APG/VPG/DME blocks, Azalia streams, and endpoint sets.
- Display runtime tests should include HPO DP and HDMI modesets, stream remapping, multi-stream DP/MST configurations, link training, suspend/resume, hotplug, and mode changes that exercise stream encoder, link encoder, DPHY, and HPO top registers.
- Audio validation should cover HDMI/DP audio enable/disable, channel allocation, high bit rate audio, infoframe updates, unsolicited response/hotplug behavior, stream descriptor programming, and endpoint/input-endpoint codec state.
- Packet-path tests should verify VPG generic packets, ISRC and MPEG metadata, AFMT audio/infoframe packet controls, CRC result readback, and memory power transitions for APG/VPG/AFMT/DME blocks.
- Debug and performance tests should exercise DSC/HPO perfmon counter programming and high/low reads, DP link/DPHY debug status, DCHVM debug/register-read paths, and VGA/Azalia indirect access sanity checks.
