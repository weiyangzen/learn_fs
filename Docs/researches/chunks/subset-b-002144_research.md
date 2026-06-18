# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h lines 1-2613

## Purpose

This chunk is the opening slice of AMD's generated DCN 4.1.0 register-offset header. It has no executable C logic; it publishes preprocessor constants that map symbolic DCN register names to MMIO offsets and to a `_BASE_IDX` selector used by AMDGPU display register-table macros.

The requested range covers the license/header guard opening and 1,389 `#define reg...` entries when counting both offset macros and matching `_BASE_IDX` macros. It starts with DCCG clock-generation offsets and ends at the first register of the `HUBPRET1` block. The rest of the 16,662-line header continues in later chunks.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, or allocation paths in this chunk. The exported interface is a generated macro namespace:

- `reg<REGISTER>`: register offset within the selected DCN base segment.
- `reg<REGISTER>_BASE_IDX`: selector passed to `BASE(reg<REGISTER>_BASE_IDX)` in DCN 4.1.0 consumers. In this chunk, DCCG/DFS entries use base index `1`, while most display-decoder, DMU, DWB, HDA, hubbub, VM, HUBP, HUBPREQ, HUBPRET, and cursor entries use base index `2`.

The main register families in this range are:

- DCCG and DCCG DFS: `DENTIST_DISPCLK_CNTL`, PHY PLL pixel-clock resync controls, DP/DSC/DPP clock DTO phase/modulo/parameter registers, OTG pixel-rate controls for OTG0-OTG5, symbol-clock enables for PHY lanes A-G, HDMI stream/char clock controls, clock-gating controls, time-base dividers, soft reset, and VSYNC latch/counter registers.
- DMU, RBBMIF, IHC, DCPG, and DMCUB: display interrupt status and destination routing, GPU timer positions, power-gating domain controls and status, DMUB/DMCUB reset/control/status, memory-region address/window registers, mailbox and outbox base/size/read/write pointers, scratch registers, GPINT registers, fault registers, timer registers, and register inbox/outbox command registers.
- DWB and DWB color pipeline: display writeback top controls, frame-composition window/source registers, CRC controls and values, overflow/backpressure/debug registers, HDR multiplier, gamut remap matrices, OGAM LUT controls, and RAM A/B piecewise gamma registers.
- MMHUBBUB and MCIF writeback: writeback memory interface address/stride/pitch/watermark/arbitration/debug registers, MMHUBBUB clock, memory power, warmup VMID, error status, and outstanding-counter registers.
- HDA/Azalia: controller clocking, DTO, DMA controls, payload capabilities, audio CRC controls, root codec parameters, miscellaneous audio clock/power straps, 16 stream index/data windows, 8 output endpoint index/data windows, and 8 input endpoint index/data windows.
- DCHUBBUB and VM request interface: arbitration watermarks for sets A/B, urgent bandwidth fractions, self-refresh and P-state transition watermarks, SAT/QOS controls, global timer/CRC/debug/status/memory-power controls, VM framebuffer/AGP/default address registers, VM fault registers, and VM context 0-15 page-table control/base/start/end address registers.
- HUBP/HUBPREQ/HUBPRET/cursor instances: complete register groups for HUBP0 and the beginning of HUBP1, including surface configuration, tiling, viewport, request sizing, MALL/cache/debug controls, primary/secondary surface addresses, flip controls, surface-in-use tracking, TTU/QOS/prefetch/nominal/flip/vblank timing parameters, VM aperture/TLB settings, HUBPREQ memory power/status, HUBPRET read-line controls, and CURSOR0 position, hot spot, size, color, address, and 3DLUT-related registers.

Several blocks are mechanically repeated by instance. Examples include OTG0-OTG5 clock controls, AZF0STREAM0-15, AZF0ENDPOINT0-7, AZF0INPUTENDPOINT0-7, HUBP0/HUBP1, and HUBPREQ0/HUBPREQ1. The chunk boundary is artificial and cuts off `dcn_dcec_dcbubp1_dispdec_hubpret_dispdec` after `regHUBPRET1_HUBPRET_READ_LINE0`.

## Control Flow

This header has no runtime control flow. The runtime path is supplied by AMDGPU display code:

1. DCN 4.1.0 modules include this offset header together with `dcn_4_1_0_sh_mask.h`.
2. Register-list macros such as `SR(...)`, `SRI_ARR(...)`, `HUBP_SF(...)`, and block-specific lists token-paste symbolic register names into offset, shift, and mask table initializers.
3. Consumers compute an address as `BASE(reg<name>_BASE_IDX) + reg<name>`. For example, `dmub_dcn401.c` defines `REG_OFFSET_EXP(reg_name)` this way with `DCN_BASE__INST0_SEG2`, while `dcn401_clk_mgr.c` does the same for clock-manager registers with `DCN_BASE__INST0_SEG1`.
4. Runtime paths call helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`; those helpers use the constructed tables to program the actual MMIO registers.

The macros do not encode sequencing rules. Consumers must still order clock changes, DMCUB reset/boot/mailbox setup, interrupt acknowledgement, writeback setup, HDA stream/endpoint programming, hubbub watermark programming, VM/page-table setup, plane flips, cursor updates, and power transitions correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes hardware state in DCN 4.1.0 registers:

- Clock and timing state for DISPCLK, DPPCLK, DSCCLK, DP stream clocks, HDMI stream/char clocks, PHY symbol clocks, OTG pixel rates, time-base dividers, and VSYNC latch/counter values.
- Firmware-controller state for DMCUB boot, reset, mailbox windows, ring pointers, scratch registers, GPINT command/response registers, timer registers, and instruction/data/undefined-address fault registers.
- Interrupt routing and status state for display, DCCG, DMU, DCPG, DCHUB, MMHUBBUB, DPP, MPC, OPP, OPTC/OTG, DIG, I2C/DDC/HPD, HDCP, DIO/DCIO, AZ, AUX, DSC, HPO, and DMCUB interrupt destinations.
- Writeback and color-pipeline state for frame capture geometry, flow control, CRC, overflow, gamut remap, HDR multiplier, and output gamma LUT/RAM programming.
- Audio state for Azalia clocking, DMA, payload capability, CRC, stream index/data windows, endpoint index/data windows, root codec identity/capabilities, and hotplug-facing audio connectivity.
- Memory and hub state for MMHUBBUB/MCIF arbitration, warmup, memory-power controls, DCHUBBUB watermarks, urgent bandwidth, self-refresh, P-state change handling, VM page-table contexts, fault reporting, and HUBP/HUBPREQ surface, flip, cursor, prefetch, TTU, MALL, cache, and power registers.

Persistence is hardware-defined. Configuration fields generally survive until modeset reprogramming, power-gating, DMCUB reset, suspend/resume restore, driver reset, or ASIC reset. Status, counter, pointer, interrupt, and fault fields may be read-only, sticky, write-one-to-clear, self-clearing, or valid only while related clocks and power domains are active. This generated header does not encode those access semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 4.1.0 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h`, which provides the matching field shifts and masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.c`, which includes this header and builds `dmub_srv_dcn401_regs` for DMCUB reset, boot windows, mailboxes, GPINT, timer, diagnostics, and register inbox/outbox access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c`, which includes this header for DCN401 clock-manager register tables and uses the `DENTIST_DISPCLK_CNTL`, DCCG, DTO, and related clock-control offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c` and `.h`, which include or consume DCN401 register-list macros for resource construction, hubbub, audio, timing, and related display blocks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn401`, `dc/hubp/dcn401`, `dc/gpio/dcn401`, `dc/irq/dcn401`, and related DCN401 modules that rely on these symbolic offsets through block-specific register tables.

The most direct behavioral integrations from this exact chunk are DCN401 display clock programming, DMUB firmware control/mailboxes, display interrupt routing, display writeback, HDMI/DP audio controller access, hubbub watermark/VM programming, and the first two HUBP/HUBPREQ plane-fetch instances.

## Risks And Edge Cases

- These constants are untyped preprocessor values. A wrong offset or `_BASE_IDX` can compile cleanly while directing `REG_*` helpers to the wrong MMIO address.
- The file is generated metadata. Manual edits can diverge from the authoritative AMD register database, the paired shift/mask header, firmware expectations, and silicon documentation.
- `_BASE_IDX` is as important as the offset. DCCG entries in this chunk use segment index `1`; most later entries use segment index `2`. Mixing these produces plausible-looking but wrong physical addresses.
- The chunk contains a visible formatting anomaly on `regPHYPLLE_PIXCLK_RESYNC_CNTL_BASE_IDX`, where the line has an extra trailing `1`. Because the macro replacement still begins with `1`, this may compile if only used in simple numeric contexts, but it is a generator-quality signal worth checking against the authoritative source.
- Repeated instances can hide one-off errors. AZF0 stream/endpoint windows, VM contexts, OTG clock controls, and HUBP/HUBPREQ instances are mostly mechanical, so one working instance does not prove all sibling offsets are correct.
- The chunk boundary is artificial. It ends inside the `HUBPRET1` block, so whole-file conclusions about all HUBP/HUBPRET instances require later chunks.
- DMCUB mailbox, GPINT, scratch, reset, and fault registers are sequencing-sensitive. Incorrect offsets can cause firmware boot failures, stuck waits, missed responses, or writes into unrelated display registers.
- Hubbub watermark, VM, and HUBPREQ address/prefetch registers are bandwidth- and memory-safety-sensitive. Wrong offsets can manifest as underflow, black frames, page faults, memory corruption symptoms, or resume-only failures.
- Audio and writeback registers are interoperability-sensitive. Wrong Azalia stream/endpoint, DMA, payload, or CRC offsets can produce silent HDMI/DP audio, hotplug issues, bad format changes, or broken capture/writeback diagnostics.

## Test Signals

Useful validation combines generated-header checks with hardware behavior:

- Build AMDGPU display support with DCN401 enabled. Missing or renamed macros should fail in DCN401 DMUB, clock-manager, GPIO, IRQ, hubbub, hubp, and resource register-table construction.
- Mechanically verify that every non-`_BASE_IDX` `reg...` macro in lines 1-2613 has a matching `_BASE_IDX` macro in the same chunk, except for the final artificial boundary where `regHUBPRET1_HUBPRET_READ_LINE0` appears without its `_BASE_IDX` before line 2614.
- Compare this range against AMD's authoritative DCN 4.1.0 register database and nearby generated headers such as `dcn_4_2_0_offset.h` where compatible blocks should retain expected offsets or only have documented deltas.
- Exercise DCN401 hardware through boot, modeset, hotplug, suspend/resume, display clock changes, DMCUB reset/boot, mailbox traffic, GPINT command/response, and display interrupt handling.
- Validate hubbub/HUBP behavior with multiple planes, cursor updates, flips, VM-enabled surfaces, MALL/cache paths, prefetch pressure, P-state changes, and low-power memory states; watch for underflow, VM fault, stale surface-in-use, or blanking glitches.
- Validate HDMI/DP audio across plug/unplug, stream enable/disable, format changes, multichannel and HBR formats, and suspend/resume; watch for HDA timeouts, bad endpoint index/data access, missing hotplug responses, or silent audio.
- Validate display writeback by enabling DWB, checking CRC/debug/overflow counters, and confirming output geometry/color programming survives clock and power transitions.

## Cross-Chunk Notes

This is the first chunk of `dcn_4_1_0_offset.h`. Later chunks continue `HUBPRET1` and then cover additional DCN 4.1.0 display, plane, timing, link, compression, audio indexed-register, and other register namespaces. The final per-file research document should merge adjacent chunks before making whole-file claims about all DCN 4.1.0 registers or all repeated block instances.
