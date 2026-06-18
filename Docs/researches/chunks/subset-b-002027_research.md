# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 1-2371

## Purpose

This chunk is the beginning of AMD's generated DCN 3.2.1 shift/mask register-field header. It has no executable C logic; it publishes preprocessor constants that describe bit positions and bit masks for DCN 3.2.1 display-controller MMIO registers. Consumers include it with the matching `dcn_3_2_1_offset.h` so register-table macros can pair each register offset with typed field extraction/update metadata.

The requested range covers the file prologue and the first 2,371 lines of a 56,598-line header. It contains the complete header guard opening, 2,172 `#define` lines in the requested range, about 1,094 `__SHIFT` definitions, and about 1,085 `_MASK` definitions. The chunk starts with DCCG display-clock fields, moves through DCCG DTO/gating/reset/audio/vsync timing fields, then covers DMU/RBBMIF timeout and display interrupt-controller status/destination fields. The final requested line stops inside `OTG2_INTERRUPT_DEST`, so later chunks are required for the rest of the OTG destination family and for the rest of the file.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this chunk. The exported interface is the generated field-macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position used by register update/extract helpers.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to preserve, set, clear, or extract that field.

The key macro families in this chunk are:

- `DENTIST_DISPCLK_CNTL`: DISPCLK and DPPCLK divider, change-mode, change-toggle, done-toggle, and completion fields.
- PHY pixel-clock and display stream clock fields: `PHYPLLA` through `PHYPLLE` pixel-clock resync controls, `DPSTREAMCLK_CNTL`, `HDMISTREAMCLK_CNTL`, `HDMICHARCLK0_CLOCK_CNTL`, and per-PHY `SYMCLK` force/source controls.
- DCCG DTO and clock-control fields: `DP_DTO_DBUF_EN`, `DSCCLK[0-3]_DTO_PARAM`, `DPPCLK[0-3]_DTO_PARAM`, `DPPCLK_DTO_CTRL`, `DTBCLK_DTO[0-3]_{PHASE,MODULO}`, `DTBCLK_DTO_DBUF_EN`, `HDMISTREAMCLK0_DTO_PARAM`, and audio DTO phase/modulo/source fields.
- DCCG clock gating, power, timing, and status fields: `DCCG_GATE_DISABLE_CNTL` through `CNTL5`, `*_CGTT_BLK_CTRL_REG`, `DC_MEM_GLOBAL_PWR_REQ_CNTL`, `DCCG_CAC_STATUS*`, `MILLISECOND_TIME_BASE_DIV`, `MICROSECOND_TIME_BASE_DIV`, `DCCG_DISP_CNTL_REG`, `DCCG_SOFT_RESET`, `DMCUBCLK_CNTL`, and `DCE_VERSION`.
- OTG/pixel-rate and vsync counter fields: `OTG_PIXEL_RATE_DIV`, `OTG[0-3]_PIXEL_RATE_CNTL`, `OTG[0-3]_PHYPLL_PIXEL_RATE_CNTL`, `DP_DTO[0-3]_{PHASE,MODULO}`, `DCCG_VSYNC_OTG[0-5]_LATCH_VALUE`, `DCCG_VSYNC_CNT_CTRL`, and `DCCG_VSYNC_CNT_INT_CTRL`.
- RBBMIF timeout fields: `RBBMIF_TIMEOUT`, `RBBMIF_STATUS`, `RBBMIF_STATUS_2`, `RBBMIF_INT_STATUS`, `RBBMIF_TIMEOUT_DIS`, `RBBMIF_TIMEOUT_DIS_2`, and `RBBMIF_STATUS_FLAG`.
- Display interrupt status chain fields: `DISP_INTERRUPT_STATUS` and `DISP_INTERRUPT_STATUS_CONTINUE` through `CONTINUE25`, including interrupt-present continuation bits and status bits for DCCG, AUX/GTC, DCPG power, HUBP vblank/vline/timeout/flip, HUBBUB VM fault/timeout/compbuf changes, MPCC stalls, DCIO DPCS errors, Azalia audio endpoint changes, DIG fast-training/stream-disable events, OTG timing events, MMHUBBUB, writeback, and DWB/DWBSCL events.
- Interrupt destination fields: `DCCG_INTERRUPT_DEST`, `DMU_INTERRUPT_DEST`, `DMU_INTERRUPT_DEST2`, `DCPG_INTERRUPT_DEST`, `DCPG_INTERRUPT_DEST2`, `MMHUBBUB_INTERRUPT_DEST`, `WB_INTERRUPT_DEST`, `DCHUB_INTERRUPT_DEST`, `DCHUB_INTERRUPT_DEST2`, `MPC_INTERRUPT_DEST`, `OPTC_INTERRUPT_DEST`, and the beginning of `OTG0_INTERRUPT_DEST` through `OTG2_INTERRUPT_DEST`.

Several comment-only register markers in the range, such as `DCHUB_PERFCOUNTER_INTERRUPT_DEST`, `DPP_PERFCOUNTER_INTERRUPT_DEST`, `OPP_INTERRUPT_DEST`, and some continuation registers, have no field defines in this chunk. That is still meaningful generated metadata: the register exists in the database, but no visible fields are emitted in this slice.

## Control Flow

This header has no runtime control flow. The runtime sequence is supplied by AMDGPU display code:

1. DCN 3.2.1 resource and clock-management code includes `dcn_3_2_1_offset.h` and this shift/mask header.
2. Register-list macros token-paste symbolic register and field names into table initializers.
3. The resulting register, shift, and mask tables are stored in hardware block objects such as DCCG, clock manager, HUBP, HUBBUB, IRQ service, DIO, timing generator, stream encoder, audio, and resource-pool components.
4. Runtime code calls helpers such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and IRQ mask/ack helpers. Those helpers use these constants to modify only the intended bits in MMIO registers.

The macros do not encode sequencing rules. Consumers must still order clock changes, DTO programming, clock gating, soft resets, power-domain transitions, interrupt masking/acknowledgement, display timing updates, link training, audio clocking, suspend/resume restore, and error recovery correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing on its own. It describes hardware state that lives in DCN 3.2.1 registers:

- Clock generator state for DISPCLK, DPPCLK, DPREFCLK, DTBCLK, DSCCLK, DMCUBCLK, SYMCLK, HDMI stream/character clocks, and PHY pixel-clock resynchronization.
- DTO state for DP, DSC, DPP, DTBCLK, HDMI stream clock, and audio clock generation.
- Power and gating state for DCCG roots, per-clock gates, memory power requests, clock-turn-on/off delays, force-disable paths, and soft reset bits.
- Timing-observation state for millisecond/microsecond bases, OTG pixel-rate controls, vsync latch values, latch interrupt status/clear/mask bits, and GPU timer start/read controls.
- Error and status state for RBBMIF timeouts, timeout client vectors, timeout disable bits, timeout address/op/read-write/ack/mask fields, and status flags.
- Interrupt state and routing for display events spanning clock, AUX, HUBP, HUBBUB, DCPG, MPCC, DCIO, Azalia audio, DIG, OTG, MMHUBBUB, WB, DCHUB, MPC, and OPTC blocks.

Persistence is entirely hardware-defined. Configuration fields usually retain values until a modeset, power-gate cycle, suspend/resume, driver reset, or ASIC reset. Status, interrupt, clear, ack, continuation, timeout, and latch fields may be read-only, sticky, write-one-to-clear, self-clearing, or valid only while related clocks and power domains are enabled. This generated header does not distinguish those access semantics; consuming driver code and the hardware programming guide must do that.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.2.1 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h`, which provides the companion MMIO register offsets.
- The DCN 3.2.1 resource path in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`, which includes both the offset and shift/mask headers.
- The clock-manager macro path in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/clk_mgr_internal.h` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`, where `CLK_COMMON_MASK_SH_LIST_DCN321(__SHIFT)` and `CLK_COMMON_MASK_SH_LIST_DCN321(_MASK)` build DCN321 shift/mask tables.
- AMD display register helper macros that paste register and field names into generated symbols and use the numeric shift/mask values for read-modify-write operations.

The most direct integration surface from this specific chunk is DCCG/clock manager setup, display interrupt handling, and DCN321 resource construction. The interrupt field families are also consumed indirectly by IRQ service tables and event handling paths that need stable bit positions for vblank, vline, flip, underflow, timeout, power-domain, AUX, audio, and link events.

## Risks And Edge Cases

- The constants are untyped preprocessor values. A wrong shift or mask can compile cleanly while making a register update touch the wrong bit, fail to clear an interrupt, or corrupt an adjacent field.
- This chunk is generated metadata, so manual edits are risky. Local corrections that do not match the authoritative register database can diverge from firmware, hardware documentation, and companion offset headers.
- Repeated instance families are copy-sensitive. PHY A-E, OTG 0-6, HUBP 0-7, DCPG domain 0-7, Azalia endpoint 0-7, and clock/DTO instance fields use similar bit layouts but are not interchangeable.
- The chunk boundary is artificial. It ends in the middle of `OTG2_INTERRUPT_DEST`, and the file continues for many more register blocks. File-level conclusions about all OTG destinations or all DCN321 fields require adjacent chunks.
- Interrupt fields are side-effect-sensitive. Wrong status, mask, clear, destination, or continuation-bit definitions can cause missed vblank/flip events, interrupt storms, unacknowledged underflow/timeouts, broken audio hotplug state, stuck power events, or incorrect routing to CPU/DMU/IH destinations.
- Clock and DTO fields are sequencing-sensitive. Incorrect DCCG masks can lead to blank displays, unstable pixel clocks, broken DSC/audio timing, link training failures, FIFO underflow, or resume-only failures when clocks were gated.
- Timeout and power-domain fields are diagnostic and recovery-critical. Bad RBBMIF or DCPG definitions can hide real hangs, acknowledge the wrong event, or make low-power transitions appear to succeed while a display block is still faulted.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU display support with DCN321 enabled. Missing or renamed macros should fail in DCN321 resource construction, clock-manager table construction, IRQ-related tables, and DCCG users.
- Mechanically verify that every emitted field in lines 1-2371 has matching `__SHIFT` and `_MASK` definitions where the generated database expects a pair, while allowing legitimate comment-only register markers and duplicated interrupt/clear fields that intentionally share the same bit.
- Diff this range against AMD's authoritative DCN 3.2.1 register database and adjacent generated headers, especially `dcn_3_2_0_sh_mask.h` or nearby DCN 3.x variants where the hardware block is expected to be compatible.
- Exercise display clock changes, DPPCLK/DSCCLK/DTBCLK/HDMI clock DTO programming, clock gating/ungating, and suspend/resume on DCN321 hardware while watching for blanking, link retraining, FIFO error detection, and timing instability.
- Exercise interrupt paths: vblank/vline/flip/flip-away events, OTG vstartup/vready/vupdate/DRR timing, HUBP timeouts, HUBBUB VM faults, DCPG power up/down events, MPCC stalls, OPTC underflows, AUX/GTC events, audio endpoint changes, and writeback/DWBSCL overflow events.
- Validate RBBMIF timeout reporting and acknowledgement with fault-injection or stress scenarios that pressure display register access paths.
- Watch kernel logs and display diagnostics for stuck interrupts, IRQ storms, missed page flips, underflows, AUX timeout reports, clock-change timeouts, link-training failures, audio enable/disable mismatches, and resume failures.

## Cross-Chunk Notes

This is the opening chunk of `dcn_3_2_1_sh_mask.h`. Later chunks continue the `OTG2_INTERRUPT_DEST` family and cover the rest of the DCN 3.2.1 field namespace, including many additional display, link, audio, compression, hub, and codec register blocks. The final per-file research document should merge adjacent chunks before making whole-file claims about the complete interrupt map, complete clock map, or all generated DCN321 register fields.
