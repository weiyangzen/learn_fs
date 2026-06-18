# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 51573-54012

## Scope

This chunk covers lines 51573-54012 of the generated AMD DCN 3.1.4 shift/mask header. It is entirely preprocessor metadata: 2,123 `#define` entries across 2,440 source lines, with 1,061 `__SHIFT` constants and 1,062 `_MASK` constants plus generated register and `addressBlock` comments. There are no functions, structs, enums, variables, includes, allocation paths, locks, or executable statements in this range.

The range starts in the middle of `DWB_OGAM_RAMA_REGION_24_25` with the final mask for RAMA region 25, then covers the tail of DWB OGAM RAMA region definitions, the full DWB OGAM RAMB programming block, DCHVM host-VM/control fields, HPO DisplayPort stream encoder instances 0 and 1, their APG/DME/VPG companion blocks, SYM32 encoder instances 0 and 1, HPO DP link encoders 0 and 1, and DPHY SYM32 instances 0 and 1. It ends at the comment for `DP_DPHY_SYM321_DP_DPHY_SYM32_CRC_CONFIG0`; the CRC config field definitions continue in the next chunk.

## Purpose

The purpose of this header slice is to publish exact bit positions and masks for DCN 3.1.4 display hardware registers. AMDGPU display code combines these macros with the matching DCN 3.1.4 offset header and register helper macros to pack MMIO writes, read individual status fields, and construct DMUB/display register tables without embedding raw bit numbers in driver logic.

This is a generated hardware contract. Its correctness depends on the macro names and numeric values matching the ASIC register database. Runtime behavior is implemented by consumers that use these constants; this file only supplies field layout.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask within a 32-bit register value.
- `//<REGISTER>` comments group fields belonging to a logical register.
- `// addressBlock: ...` comments group registers by decoded hardware block.

Major constant families in this chunk include:

- `DWB_OGAM_RAMA_REGION_26_27` through `DWB_OGAM_RAMA_REGION_32_33` and `DWB_OGAM_RAMB_*`, covering DWB output gamma RAM region starts, bases, slopes, ends, offsets, and per-region LUT offsets/segment counts for RGB channels.
- `DCHVM_CTRL0/1`, `DCHVM_CLK_CTRL`, `DCHVM_MEM_CTRL`, `DCHVM_RIOMMU_CTRL0`, and `DCHVM_RIOMMU_STAT0`, covering host-VM initialization, display/DCF clock gating controls, GPUVM retention power controls, RIOMMU prefetch requests, and RIOMMU active/done status.
- `DP_STREAM_ENC0_*` and `DP_STREAM_ENC1_*`, covering HPO DP stream encoder clock enable/reset/status, input mux stream source selection, audio stream source selection, clock-ramp-adjuster FIFO control/status, and spare fields.
- `APG0_*` and `APG1_*`, covering audio packet generator reset/enable, DP audio stream ID, channel-count override, debug audio generator controls, ACP/audio-info packet source selection, audio CRC control/result/status, output-active status, memory power, and spare registers.
- `DME5_*` and `DME6_*`, covering dynamic metadata engine requestor IDs, enablement, stream type, double-buffer pending/taken/clear/disable fields, missed-transmission status/clear, and DME memory power controls.
- `VPG5_*` and `VPG6_*`, covering generic packet indexed data access, generic sideband packet frame and immediate update controls for packet slots 0-14, conflict/lock status, VPG memory power, ISRC indexed data, and MPEG info packet fields.
- `DP_SYM32_ENC0_*` and `DP_SYM32_ENC1_*`, covering 32-bit symbol encoder enable/reset, video FIFO control, MSA and pixel-format double buffering, pixel format, MSA words 0-8, HBLANK minimum width, 15 generic sideband packet controls, SDP stream/audio/metadata packet controls, MSA/VBID scheduling, video stream enable/status, panel replay tunneling optimization, video CRC control/results/status, memory power, and spare fields.
- `DP_LINK_ENC0_*` and `DP_LINK_ENC1_*`, covering HPO DP link encoder clock enable and clock-on-SYMCLK32 controls.
- `DP_DPHY_SYM320_*` and `DP_DPHY_SYM321_*`, covering DPHY enable/reset/precoder/mode/lane count, status, SAT update, four virtual-channel rate controls, SAT VC configuration/status, training pattern configuration, PRBS seeds, square-pulse/custom test patterns, error status, and per-stream symbol override controls.

## Control Flow

This chunk has no runtime control flow. Its effective flow is compile-time token expansion:

1. DCN 3.1.4 display code includes the generated offset and shift/mask headers.
2. Register helpers concatenate register and field identifiers to resolve `__SHIFT` and `_MASK` macros from this file.
3. Runtime driver code uses the resolved constants to perform MMIO or indexed-register reads, writes, read-modify-write updates, and field decoding.

The declaration order mirrors hardware organization. Within the HPO DP area, instance 0 is declared first, followed by its APG, DME, VPG, SYM32 encoder, link encoder, and DPHY blocks; instance 1 repeats the same structure. Repeated field layouts are intentionally duplicated per instance so helper macros can resolve instance-specific names.

## State And Persistence Behavior

The header itself stores no software state and persists no data. It describes bit locations for hardware state in DCN 3.1.4 registers.

Writable fields in this range can program DWB output gamma transfer curves, DCHVM power/clock/RIOMMU behavior, HPO DP stream encoder clocking and routing, APG audio packet generation, DME metadata transmission, VPG generic packet scheduling, SYM32 video/audio/metadata sideband packet generation, video stream enablement, panel replay optimization, DPHY mode/lane/rate/SAT/training-pattern behavior, and memory power controls for several subblocks.

Hardware-updated fields expose FIFO reset/done/active/error state, APG CRC/status/FIFO overflow, DME pending/taken/missed status, VPG lock/conflict/update-pending status, SYM32 double-buffer pending, stream status, CRC valid/results, DPHY active/reset/current-mode/update-pending/error/CRC-related status, RIOMMU state, and memory power state. Access type, reset values, read-clear or write-one-to-clear semantics, and required sequencing are not encoded in this header.

Programmed values persist according to the underlying hardware power and reset domains. They may survive until rewritten, display block reset, audio/link reinitialization, suspend/resume restore, GPU reset, or ASIC reset. Status and counter-like observations can change asynchronously relative to C code that includes this header.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.1.4 register offset header for addresses. The shift/mask header identifies bit placement only; it does not say where a register is mapped.

Primary consumers are AMDGPU display register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD_MASK`, `FD_SHIFT`, and generated register tables that paste register and field names into these macro symbols. A missing or renamed symbol usually fails at build time. A wrong numeric shift or mask can compile successfully and only show up as hardware misprogramming or misread status.

Key integration areas are:

- DWB/gamma programming paths that load output gamma RAM region descriptors and per-channel start/end/base/slope/offset values.
- Display VM and power-management paths that manipulate DCHVM clock, retention, and RIOMMU request/status fields.
- HPO DisplayPort bring-up and modeset paths that configure stream encoders, link encoders, DPHY instances, virtual-channel rates, SAT slots, stream source selection, symbol encoding, training/test patterns, and CRC diagnostics.
- Display audio and packet-generation paths that use APG, VPG, DME, and SYM32 SDP fields for DP audio packets, generic sideband packets, metadata packets, ISRC/MPEG info, and audio/video CRC validation.
- Panel replay, MST/SAT, and metadata scheduling paths that rely on line-number, SOF-reference, double-buffer, pending, and deadline-missed fields being packed correctly.

The generated offset and shift/mask headers must come from the same DCN 3.1.4 register database. Mixing this file with DCN 3.1.2, DCN 3.1, or later ASIC headers is risky because many field names are structurally similar while offsets or bit layouts can diverge.

## Risks And Edge Cases

- The chunk starts mid-register. Only the final `DWB_OGAM_RAMA_REGION_24_25__DWB_OGAM_RAMA_EXP_REGION25_NUM_SEGMENTS_MASK` line for `DWB_OGAM_RAMA_REGION_24_25` is present; preceding shifts/masks for that register are in the previous chunk.
- The chunk ends at the `DP_DPHY_SYM321_DP_DPHY_SYM32_CRC_CONFIG0` comment. The actual CRC config shifts and masks for DPHY instance 1 continue in the next chunk.
- Repeated HPO instance layouts are copy-sensitive. `DP_STREAM_ENC0`/`1`, `APG0`/`1`, `VPG5`/`6`, `DP_SYM32_ENC0`/`1`, `DP_LINK_ENC0`/`1`, and `DP_DPHY_SYM320`/`321` differ mostly by instance number, so generator drift can be difficult to review manually.
- Many fields are control/status adjacent. For example, enable/reset fields sit near reset-done/status bits; sideband packet trigger bits sit near pending/deadline bits; CRC enable bits sit near result/status fields. Blind read-modify-write patterns must respect hardware access rules outside this header.
- High-bit packed fields such as transmission line numbers (`0xFFFF0000L`), VC rate X values (`0xFE000000L`), DPHY symbol override stream fields, and OGAM region descriptors can corrupt unrelated settings if a shift or mask is wrong.
- Full-width masks such as spare registers and MSA data words use `0xFFFFFFFFL`; consumers should avoid signed-width assumptions and preserve 32-bit register semantics.
- DPHY training pattern, PRBS seed, custom pattern, symbol override, and error-status fields are link-training and diagnostic sensitive. Incorrect masks can break link bring-up or make CRC/error diagnostics misleading while still compiling.
- VPG/APG/DME update-pending and double-buffer fields imply hardware sequencing. This header does not document when software should poll, clear, or defer updates.

## Test Signals

Useful validation is mostly build-time consistency plus hardware integration:

- Build AMDGPU display code for a DCN 3.1.4-enabled configuration to catch missing or renamed macros used by register helper expansion.
- Mechanically verify that each complete register in this line range has matching `__SHIFT` and `_MASK` symbols for every field, while accounting for the partial first and last registers.
- Compare this slice against the authoritative DCN 3.1.4 register database and the matching offset header to ensure every register comment has the intended address and every field has the intended bit layout.
- Exercise DWB output gamma programming with nontrivial transfer functions, checking for channel-specific artifacts that would indicate bad RAMB/RAMA start, segment, slope, offset, or region fields.
- Exercise HPO DisplayPort link bring-up, modeset, stream enable/disable, MST/SAT scheduling, link training, training-pattern diagnostics, sideband packet transmission, metadata packet scheduling, panel replay, and CRC capture on DCN 3.1.4 hardware.
- Exercise DP audio paths through APG/VPG/SYM32 fields: stream ID routing, packet generation, ISRC/MPEG info, audio CRC, mute/status behavior, hotplug/resume reprogramming, and multichannel/HBR-like stress cases where available.
- Watch for FIFO errors, DME metadata missed-transmission bits, VPG generic packet conflicts, SYM32 double-buffer pending stuck states, DPHY rate/SAT update pending states, and DPHY error-status bits during display/audio tests.

## Open Cross-Chunk Notes

The merge lane should combine this chunk with the previous chunk to describe `DWB_OGAM_RAMA_REGION_24_25` completely. It should combine this chunk with the next chunk to describe `DP_DPHY_SYM321_DP_DPHY_SYM32_CRC_CONFIG0` and the remainder of the DPHY/SYM32 instance 1 diagnostics completely. Whole-file analysis should reconcile this chunk with neighboring DCN 3.1.4 generated-header chunks before making final claims about the complete set of HPO DP, DWB, DCHVM, APG, DME, VPG, and DPHY registers exposed by `dcn_3_1_4_sh_mask.h`.
