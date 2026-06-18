# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h lines 12823-14737

## Purpose

This chunk is the tail of the generated AMD DCN 3.2.0 register-offset header. It contains no executable code; it publishes C preprocessor constants that name hardware register offsets and indirect-register indexes for DCN 3.2 display, HPO DisplayPort, DPCS/PHY, legacy VGA, and Azalia/HDA audio blocks.

The requested range contains 1,620 `#define` entries across 73 address blocks. Of those, 476 are `reg*` register-offset or `_BASE_IDX` macros and 1,144 are `ix*` indirect index macros. The block begins at the final `DME9_DME_MEMORY_CONTROL` entry from the prior DME block, covers HPO DP stream/link/PHY offsets, then shifts into DPCS pipe indirect indexes and the HDA/Azalia controller, stream, endpoint, input endpoint, CRC, descriptor, sink-info, and C20 PHY indirect index spaces. Although this file lives under a mirrored `ceph-client` source tree, the content is AMDGPU display-driver ASIC metadata, not Ceph or distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, allocation paths, or exported C symbols in this range. The API surface is the generated macro namespace:

- `reg<REGISTER>` gives an MMIO register offset relative to the base segment identified by the companion macro.
- `reg<REGISTER>_BASE_IDX` selects the entry in `ctx->dcn_reg_offsets[]` that must be added to the offset by DCN register-list construction code.
- `ix<REGISTER>` gives an indirect register index written through an index/data register pair rather than directly added to a DCN base offset.

Major macro families in this chunk:

- HPO DP stream encoder packet-generation offsets: `regVPG9_*` for generic packet access/data, GSP frame/immediate update controls, generic status, memory power, ISRC access/data, and MPEG info registers.
- HPO DP 32-symbol stream encoder offsets: `regDP_SYM32_ENC3_*` for stream control, video FIFO, MSA double buffering, pixel format, MSA0-8, hblank control, sideband/generic/audio/metadata packet controls, VBID, panel replay, video CRC, memory power, and spare registers.
- HPO DP link and PHY offsets: `regDP_LINK_ENC0_*`, `regDP_LINK_ENC1_*`, `regDP_DPHY_SYM320_*`, and `regDP_DPHY_SYM321_*` for link clocks/spares, DPHY enable/reset/status, stream allocation table (`SAT`) updates, virtual-channel rates, test-pattern configuration, PRBS/custom patterns, symbol override, error/status, deskew, lane enablement, memory power, and flow-control/status registers.
- DPCS pipe indirect offsets: `ixRDPCSPIPE[0-4]_*` for pipe clock and pipe resets at per-pipe base offsets.
- HDA/Azalia controller offsets: `regCORB_*`, `regRIRB_*`, immediate command/response interface registers, DMA position base registers, wall-clock alias, and endpoint/root/input endpoint immediate command aliases.
- HDA output stream descriptors: `regAZSTREAM[0-7]_*` for stream control/status, link position, cyclic-buffer length, last-valid index, FIFO size, format, BDL lower/upper base, and link-position aliases.
- Legacy VGA indirect register indexes: `ixSEQ*`, `ixCRT*`, `ixGRA*`, and `ixATTR*` for sequencer, CRT controller, graphics, and attribute register spaces.
- Azalia codec and sink indexes: `ixAZALIA_F2_*`, audio descriptors, sink manufacturer/product/port/description entries, output/input CRC channel result indexes, function parameter indexes, and latency/FIFO counters for `AZF0STREAM0` through `AZF0STREAM15`.
- Repeated Azalia endpoint indexes: `ixAZF0ENDPOINT0_*` through `ixAZF0ENDPOINT7_*` for converter parameters, converter controls, stream IDs, digital converter controls, stripe/ramp/GTC controls, pin capabilities, pin sense, speaker/channel allocation, audio descriptors, sink info, hot-plug, unsolicited response force, codec status, LPIB snapshots, coding/format-change/wireless/keepalive fields, and audio enable/disable/format-change interrupt status.
- Repeated Azalia input endpoint indexes: `ixAZF0INPUTENDPOINT0_*` through `ixAZF0INPUTENDPOINT7_*` for input converter controls, input pin controls, multichannel/HBR status, channel allocation, hot-plug, LPIB snapshots, input status, and infoframe.
- C20 PHY indirect indexes: `ixC20_PHY_CR[0-4]_*` for per-lane VGA adaptation status and raw-lane TX/RX interrupt mask indexes, plus lane-X aggregate aliases.

## Control Flow

This header has no direct control flow. Runtime sequencing is supplied by AMD display code that includes this generated header and its paired shift/mask header:

1. DCN 3.2 code includes `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`.
2. Resource setup macros such as `SR`, `SR_ARR`, `SRI`, and `SRI_ARR` token-paste register names into `reg...` and `reg..._BASE_IDX`, then compute absolute MMIO offsets from `ctx->dcn_reg_offsets[]`.
3. Register helper macros such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, and `REG_GET` use those offsets, and indirect helpers use `ix...` indexes through endpoint/index-data windows.
4. Higher-level DCN code performs modeset, HPO DP enablement, link training/test-pattern setup, audio endpoint programming, CRC reads, stream descriptor setup, interrupt handling, and power-management sequencing.

The macros only provide addresses and indexes. They do not encode required ordering, access permissions, polling rules, write-one-to-clear behavior, or timing boundaries for display/audio hardware updates.

## State And Persistence Behavior

The file stores no software state and persists nothing on disk. It describes MMIO-backed and indirect-indexed hardware state. The represented state includes:

- HPO DP packet, stream, and link state: packet payload access, GSP/update timing, MSA/pixel format/VBID, sideband packet routing, panel replay controls, video CRC results/status, memory-power controls, link clocks, PHY reset/enable/status, lane configuration, VC rates, SAT programming, test patterns, symbol override, and flow control.
- DPCS and PHY state: per-pipe clock/reset controls, per-lane adaptation status, and raw-lane TX/RX interrupt mask indexes.
- HDA/Azalia DMA and command state: CORB/RIRB buffers, immediate command/response windows, DMA position buffers, wall-clock reads, output stream descriptors, FIFO size, stream format, BDL base addresses, link-position aliases, and latency counters.
- Codec endpoint and pin state: audio widget capabilities, converter format/stream ID/digital converter settings, audio descriptors, sink information, channel and speaker allocation, lip-sync/HBR/multichannel controls, hot-plug and unsolicited response state, pin sense, LPIB snapshots, coding type, format-change status, keepalive, and audio enable/disable interrupts.
- Diagnostic state: input/output audio CRC channel indexes, DP video CRC registers, DPHY error/status registers, and PHY interrupt masks.

Persistence is hardware-defined. Configuration registers usually retain state until reprogramming, power gating, suspend/resume restore, or ASIC reset. Status, CRC, interrupt, link-position, command-response, FIFO, latency, snapshot, and `*_STATUS` registers can be read-only, sticky, self-clearing, or side-effect-sensitive depending on the hardware register specification; the offset header does not classify those semantics.

## Dependencies And Integration Points

This chunk must match the corresponding DCN 3.2.0 shift/mask header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h`, and the generated symbol names expected by DCN 3.2 display code.

Direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`

Specific downstream consumers include `dcn32_resource.h` register-list macros for audio endpoint registers and HPO DP DPHY/SYM32 register arrays. The `dcn32_hpo_dp_link_encoder.h` field-list macros reference the `DP_DPHY_SYM320_*` naming in this range, while `dcn32_resource.c` uses Azalia endpoint index/data macros for audio resource construction. Older DCE code in the same tree shows the common use pattern for `ixAZALIA_*` indexes through `RREG32_AUDIO_ENDPT` and `WREG32_AUDIO_ENDPT` helpers, even though this chunk provides the DCN 3.2 generated index namespace.

## Risks And Edge Cases

- Generated offset drift is the central risk. A wrong value or `_BASE_IDX` can compile cleanly but point register helpers at the wrong hardware block.
- `reg*` and `ix*` macros are different address spaces. Treating an indirect `ixAZF0ENDPOINT*` or `ixC20_PHY*` value as an MMIO offset, or adding a DCN base to it, would access the wrong register path.
- HPO DP register families are highly replicated. `DP_SYM32_ENC3`, `DP_LINK_ENC0/1`, and `DP_DPHY_SYM320/321` names differ by instance; token-paste mistakes can route one stream or link lane set to the wrong encoder instance.
- Audio endpoint families are also highly replicated. `AZF0ENDPOINT0-7`, `AZF0INPUTENDPOINT0-7`, and `AZF0STREAM0-15` share nearly identical local indexes, so generator or caller mix-ups can affect only one display/audio function and be hard to diagnose.
- Some offsets alias multiple logical registers at one numeric address, such as HDA stream `FIFO_SIZE` and `FORMAT` or controller `RIRB_*` and response interrupt/status fields. Correct behavior depends on field masks and access size/semantics outside this offset header.
- Status and interrupt registers are side-effect-sensitive. CRC result/status, audio enable/disable/format-change interrupt status, LPIB snapshots, hot-plug/unsolicited response, command status, and PHY IRQ mask/status paths need access helpers that preserve clear/ack semantics.
- HPO link/PHY test-pattern, PRBS, symbol override, lane-enable, and reset registers can disturb active links if programmed out of sequence. The header provides no guard against writes during live display.
- The chunk boundary starts at the tail of a DME instance and ends at `#endif`, so complete per-file conclusions must reconcile this range with prior chunks for the earlier DCN 3.2.0 offset map.

## Test Signals

Useful validation signals for consumers of this chunk include:

- Build AMDGPU/DC with DCN 3.2 support enabled so token-pasted `reg...`, `reg..._BASE_IDX`, and `ix...` names resolve in `dcn32_resource.c`, `dmub_dcn32.c`, HPO DP encoder code, GPIO, IRQ, clock-manager, and GMC paths.
- Mechanically verify that every `reg*` entry used by DCN 3.2 register-list macros has a companion `_BASE_IDX` and that every generated base index maps to a valid `ctx->dcn_reg_offsets[]` slot for the target ASIC.
- Compare these offsets and indirect indexes against AMD's authoritative DCN 3.2.0 register database or a known-good generated header.
- Exercise HPO DP modesets across stream/link encoder instances, including sideband packet programming, MSA/pixel-format changes, VBID, panel replay, video CRC reads, DPHY enable/reset, SAT updates, VC rate changes, and link training/test patterns.
- Exercise display audio through HDMI/DP sinks: stream descriptor setup, CORB/RIRB command flow, immediate command-response access, channel allocation, audio descriptors, HBR/multichannel modes, hot-plug handling, LPIB snapshot reads, and format-change interrupts.
- Validate DPCS/C20 PHY paths with lane-level status reads and TX/RX IRQ mask programming during link bring-up, link retraining, suspend/resume, and display hotplug.
- Run power-management and resume tests around VPG/SYM32/DPHY/Azalia memory-power or clock-gating controls to catch offsets that only fail when blocks are gated or restored.
- Run CRC and diagnostic tests for DP video CRC, Azalia input/output CRC channels, latency counters, and stream link-position aliases to catch wrong indirect indexes or address aliases.

## Cross-Chunk Notes

Earlier chunks in `dcn_3_2_0_offset.h` contain the preceding DCN 3.2 register-offset families that lead into the `DME9` tail seen at the top of this range. This chunk reaches the file terminator and completes the offset/index namespace with HPO DP, DPCS/PHY, VGA, HDA/Azalia, endpoint, input endpoint, and C20 PHY indirect definitions. The final per-file research document should merge adjacent chunk notes before making complete claims about all DCN 3.2.0 display, audio, PHY, and memory/controller register coverage.
