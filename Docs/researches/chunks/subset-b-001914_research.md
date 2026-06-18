# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 42180-44523

## Purpose

This chunk is generated AMD DCN 3.1.6 field shift/mask metadata. It contains no executable driver logic; it publishes C preprocessor constants that tell common AMD display register helpers where each hardware bitfield lives inside an MMIO register.

The requested range covers 2,181 `#define` lines: 1,084 `__SHIFT` constants and 1,097 `_MASK` constants. The range starts in the middle of `VPG1_VPG_GSP_FRAME_UPDATE_CTRL`, then covers the rest of the DIG1 VPG status/power/infoframe tail, complete DME/VPG blocks for DIG2 through DIG4, complete DP AUX blocks for AUX0 through AUX3, and the first half of DP AUX4 through `DP_AUX4_AUX_DPHY_RX_CONTROL0__AUX_RX_TRANSITION_FILTER_EN_MASK`. The range ends mid-register; later chunk research must complete the remaining DP AUX4 DPHY RX fields and any following AUX4 registers.

Although this repository path is under a local `ceph-client` mirror, this source is AMDGPU display hardware metadata, not Ceph or distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, allocations, or runtime APIs in this chunk. Its interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position used by `REG_GET`, `REG_SET`, `REG_UPDATE`, and related helpers.
- `<REGISTER>__<FIELD>_MASK`: bit mask used with the shift constant to isolate or program a field.
- `// addressBlock: ...` comments: generated grouping markers for hardware register blocks.

Major register families in this chunk:

- `VPG1_VPG_*` tail: completes generic packet frame/immediate update masks for packet slots 0-14, generic lock/conflict status, VPG GSP memory power, ISRC indexed data access, and MPEG infoframe bytes/update.
- `DME2_DME_*`, `DME3_DME_*`, and `DME4_DME_*`: Display Metadata Engine control and memory power fields. These include metadata HUBP requestor selection, engine enable, stream type, double-buffer pending/taken/disable/clear bits, missed-transmission status/clear bits, and DME memory power force/disable/state/default low-power fields.
- `VPG2_VPG_*`, `VPG3_VPG_*`, and `VPG4_VPG_*`: Video Packet Generator field layouts for generic packet memory access, packet payload bytes, per-slot frame update and immediate update requests/pending bits for slots 0-14, generic access conflict/clear state, GSP memory power, ISRC bytes, and MPEG infoframe payload/update fields.
- `DP_AUX0_AUX_*` through `DP_AUX3_AUX_*`: complete DisplayPort AUX engine field layouts for control, software transaction control, arbitration, interrupts, software and link-service status, software/link-service data windows, DPHY TX/RX timing controls and status, GTC synchronization control/error/status, and PHY wake control.
- `DP_AUX4_AUX_*`: partial fifth AUX engine field layouts, complete through software/link-service data windows and TX timing controls, ending partway through RX control 0.

The VPG instances share the same field geometry: generic packet access index uses bits 7:0; packet data bytes occupy 8-bit lanes at 0, 8, 16, and 24; generic packet update request bits occupy slots 0-14; update-pending bits occupy slots 16-30; memory power uses light-sleep disable at bit 0, force at bit 4, and state at bit 8.

The AUX instances also share a repeated layout. `AUX_CONTROL` exposes enable/reset/reset-done, link-service read enable/update disable, HPD disconnect handling, mode detect, HPD select, impedance calibration request enable, test mode, deglitch, and spare bits. `AUX_ARB_CONTROL` arbitrates SW and DMCU ownership. `AUX_SW_CONTROL` starts software transactions and programs start delay/write-byte count. `AUX_SW_DATA` is an indexed/autoincrementing data window. `AUX_SW_STATUS` and `AUX_LS_STATUS` report completion, request state, timeout/overflow/HPD disconnect, invalid symbol/stop/start conditions, reply byte count, arbitration state, CP IRQ, update, and update ack.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by consuming AMD display code:

1. DCN316 resource construction includes `dcn_3_1_6_offset.h` and this `dcn_3_1_6_sh_mask.h`.
2. Register-list macros in AMD display objects paste instance names into these generated constants.
3. Shift/mask tables are initialized once as static data, for example `vpg_shift`, `vpg_mask`, `aux_shift`, and `aux_mask` in `display/dc/resource/dcn316/dcn316_resource.c`.
4. Runtime helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and `REG_WAIT` use the selected register address plus the shift/mask entry to access the actual hardware field.

Concrete consumer paths verified in this tree:

- `display/dc/resource/dcn316/dcn316_resource.c` includes this header, builds `vpg_regs[]` for VPG0-VPG9 with `VPG_DCN31_REG_LIST(id)`, initializes `vpg_shift`/`vpg_mask` with `DCN31_VPG_MASK_SH_LIST`, builds AUX register arrays for AUX0-AUX4, and initializes `aux_shift`/`aux_mask` with `DCN_AUX_MASK_SH_LIST`.
- `display/dc/dcn30/dcn30_vpg.c` writes generic info packets by polling `VPG_GENERIC_STATUS.VPG_GENERIC_CONFLICT_OCCURED`, clearing `VPG_GENERIC_CONFLICT_CLR`, selecting `VPG_GENERIC_DATA_INDEX`, writing header/body bytes through `VPG_GENERIC_PACKET_DATA`, and then triggering either a per-packet immediate update or frame update.
- `display/dc/dcn31/dcn31_vpg.c` uses the VPG memory-power fields to force/allow light sleep and read `VPG_GSP_MEM_PWR_STATE`.
- `display/dc/dce/dce_aux.c` acquires AUX ownership via `AUX_ARB_CONTROL`, enables/resets the AUX block via `AUX_CONTROL`, programs AUX request bytes through `AUX_SW_CONTROL` and `AUX_SW_DATA`, triggers `AUX_SW_GO`, waits on `AUX_SW_STATUS.AUX_SW_DONE`, and parses reply length/status with `AUX_SW_REPLY_BYTE_COUNT`.
- `display/dc/dio/dcn32/dcn32_dio_stream_encoder.h` includes DME metadata fields in the stream encoder mask/shift list, so DME control bits are part of DCN stream encoder metadata programming.

## State And Persistence Behavior

This chunk stores no software state. It describes MMIO-backed display hardware state:

- VPG registers hold generic SDP/info packet staging memory, per-packet update request state, update-pending status, conflict/lock status, ISRC and MPEG infoframe payloads, and VPG GSP memory power controls.
- DME registers hold metadata-engine routing and enable state, double-buffer lifecycle bits, missed-transmission status, and DME memory low-power policy/state.
- AUX registers hold DisplayPort sideband transaction engine state, AUX ownership arbitration between software and DMCU/firmware, interrupt status/ack/mask bits, SW and link-service request/reply buffers, physical-layer TX/RX timing configuration, GTC synchronization state/error counters, and PHY wake behavior.

Persistence is hardware-defined. Configuration fields usually persist until driver reprogramming, display power-gating, suspend/resume, GPU reset, or ASIC reset. Status, pending, ack, clear, interrupt, and data-window fields can be read-only, sticky, self-clearing, write-one-to-clear, or side-effecting depending on the hardware register; this generated header does not encode access type or ordering semantics.

## Dependencies And Integration Points

This chunk must stay synchronized with:

- The companion offset header `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h`, because these field layouts are only meaningful when paired with the matching register offsets and base indices.
- Common AMD display register helper macros from `display/dc/inc/reg_helper.h` and object-specific list macros such as `DCN31_VPG_MASK_SH_LIST`, `DCN_AUX_MASK_SH_LIST`, and stream encoder `SE_SF` lists.
- DCN316 resource construction in `display/dc/resource/dcn316/dcn316_resource.c`, which binds these generated constants into per-object tables used by VPG, AUX, link encoder, and stream encoder instances.
- VPG implementation files under `display/dc/dcn30/` and `display/dc/dcn31/`, which perform packet staging, update triggering, and VPG memory power handling.
- AUX implementation files under `display/dc/dce/` and link encoder code under `display/dc/dio/`, which use the AUX control/arbitration/status/data fields for DP AUX and I2C-over-AUX transactions.
- Stream encoder metadata paths, especially DCN32-style metadata fields in `display/dc/dio/dcn32/dcn32_dio_stream_encoder.h`, where DME control bits are listed for dynamic metadata/secondary-data-packet programming.

The in-tree DCN316 resource table instantiates five AUX engines (`AUX0` through `AUX4`) and at least VPG instances 0-9. This chunk therefore covers live DCN316 instances, not merely unused generated definitions.

## Risks And Edge Cases

- Field drift is the central risk. A wrong mask or shift compiles cleanly but causes `REG_UPDATE` and `REG_GET` to touch the wrong bits in a live MMIO register.
- The chunk boundaries are artificial. The first visible lines are the tail of `VPG1_VPG_GSP_FRAME_UPDATE_CTRL`, so full VPG1 ownership is split with the previous chunk. The last visible lines stop mid-`DP_AUX4_AUX_DPHY_RX_CONTROL0`, so full AUX4 ownership is split with the next chunk.
- VPG packet update bits are indexed by packet slot 0-14. A shifted or mismatched field can update the wrong generic packet, leave a pending bit uncleared, or cause stale HDR/AVI/vendor/ISRC/MPEG metadata to be transmitted.
- VPG conflict and memory-power fields are sequencing-sensitive. Bad conflict clearing or light-sleep control can race with hardware reads of GSP memory and cause packet corruption or intermittent update failures.
- DME metadata fields affect dynamic metadata routing and double-buffer lifecycle. Incorrect HUBP requestor, stream type, pending/taken clear, or missed-transmission clear fields can silently drop or misroute metadata packets.
- AUX arbitration fields protect shared ownership between software and firmware. Bad `AUX_SW_USE_AUX_REG_REQ`, `AUX_SW_DONE_USING_AUX_REG`, DMCU request, or status bits can deadlock access, steal an engine from firmware, or make software believe the engine is available when it is not.
- AUX status and reply count fields feed error handling in `dce_aux.c`. Wrong timeout, overflow, HPD disconnect, invalid symbol, or reply-byte-count masks can convert real link errors into bogus successful replies, truncate DPCD/EDID data, or cause retry storms.
- AUX data-window fields are side-effecting and indexed. Wrong `AUX_SW_INDEX`, `AUX_SW_DATA_RW`, `AUX_SW_AUTOINCREMENT_DISABLE`, or data-byte masks can corrupt outgoing DP AUX headers/payloads or read the wrong reply bytes.
- AUX DPHY timing and GTC sync fields are link-quality sensitive. Incorrect TX precharge, RX detection/window/timeout, or GTC sync masks may only fail on marginal cables, adapters, resume paths, or compliance tests.
- Instance repetition hides copy/paste hazards. AUX0-AUX4 and VPG2-VPG4 should generally share layouts; a single instance-specific deviation may only affect one connector or one stream encoder.

## Test Signals

Useful validation combines generated-header checks, build coverage, and hardware behavior:

- Build AMDGPU display support with DCN316 enabled. Missing or renamed macros should fail in `dcn316_resource.c`, VPG mask/shift lists, AUX mask/shift lists, or stream encoder metadata lists.
- Mechanically verify every complete field in this range has exactly one `__SHIFT` and one `_MASK` macro, allowing for the known partial boundaries at the start and end of the chunk.
- Diff VPG2/VPG3/VPG4 and AUX0/AUX1/AUX2/AUX3 repeated layouts against each other and against AMD's authoritative DCN 3.1.6 register database. Treat unexpected per-instance differences as high risk.
- Exercise generic info packet programming on DCN316: modesets, HDR metadata, vendor-specific packets, ISRC/MPEG packets if exposed, immediate update and frame update paths, and multi-stream cases using different VPG instances.
- Monitor for VPG conflict timeouts, persistent update-pending bits, stale metadata on the wire, display metadata CRC/compliance failures, and failures after display power-gating or suspend/resume.
- Exercise DME metadata paths with dynamic metadata enabled where supported, including stream changes, HUBP/requestor changes, and double-buffer update timing.
- Exercise DP AUX and I2C-over-AUX: DPCD reads/writes, EDID reads, link training, HPD plug/unplug, HPD-low transaction aborts, MST sideband if available, eDP panel bring-up, and suspend/resume.
- Watch kernel logs and display diagnostics for AUX acquisition failures, AUX timeout/overflow/invalid-reply retries, EDID/DPCD read failures, link training instability, HPD storms, and one-connector-only failures that point to an AUX instance layout issue.
- Run DP compliance or analyzer-based tests for AUX waveform/timing and GTC sync when changing any AUX DPHY or sync field definitions.

## Cross-Chunk Notes

This chunk must be reconciled with `subset-b-001913` for the beginning of VPG1 and with `subset-b-001915` for the remainder of DP AUX4. The final per-file report should avoid treating this chunk as a complete description of either `VPG1_VPG_GSP_FRAME_UPDATE_CTRL` or `DP_AUX4_AUX_DPHY_RX_CONTROL0`; both are split by chunk boundaries.
