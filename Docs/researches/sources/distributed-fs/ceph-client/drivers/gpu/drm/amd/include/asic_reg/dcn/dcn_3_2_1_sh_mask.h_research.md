# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002027`: lines 1-2371, `Docs/researches/chunks/subset-b-002027_research.md`
- `subset-b-002028`: lines 2372-4913, `Docs/researches/chunks/subset-b-002028_research.md`
- `subset-b-002029`: lines 4914-7582, `Docs/researches/chunks/subset-b-002029_research.md`
- `subset-b-002030`: lines 7583-10082, `Docs/researches/chunks/subset-b-002030_research.md`
- `subset-b-002031`: lines 10083-12636, `Docs/researches/chunks/subset-b-002031_research.md`
- `subset-b-002032`: lines 12637-15195, `Docs/researches/chunks/subset-b-002032_research.md`
- `subset-b-002033`: lines 15196-17712, `Docs/researches/chunks/subset-b-002033_research.md`
- `subset-b-002034`: lines 17713-20169, `Docs/researches/chunks/subset-b-002034_research.md`
- `subset-b-002035`: lines 20170-22676, `Docs/researches/chunks/subset-b-002035_research.md`
- `subset-b-002036`: lines 22677-25260, `Docs/researches/chunks/subset-b-002036_research.md`
- `subset-b-002037`: lines 25261-27725, `Docs/researches/chunks/subset-b-002037_research.md`
- `subset-b-002038`: lines 27726-30144, `Docs/researches/chunks/subset-b-002038_research.md`
- `subset-b-002039`: lines 30145-32540, `Docs/researches/chunks/subset-b-002039_research.md`
- `subset-b-002040`: lines 32541-34936, `Docs/researches/chunks/subset-b-002040_research.md`
- `subset-b-002041`: lines 34937-37346, `Docs/researches/chunks/subset-b-002041_research.md`
- `subset-b-002042`: lines 37347-39686, `Docs/researches/chunks/subset-b-002042_research.md`
- `subset-b-002043`: lines 39687-42210, `Docs/researches/chunks/subset-b-002043_research.md`
- `subset-b-002044`: lines 42211-44669, `Docs/researches/chunks/subset-b-002044_research.md`
- `subset-b-002045`: lines 44670-47065, `Docs/researches/chunks/subset-b-002045_research.md`
- `subset-b-002046`: lines 47066-49630, `Docs/researches/chunks/subset-b-002046_research.md`
- `subset-b-002047`: lines 49631-52079, `Docs/researches/chunks/subset-b-002047_research.md`
- `subset-b-002048`: lines 52080-54448, `Docs/researches/chunks/subset-b-002048_research.md`
- `subset-b-002049`: lines 54449-56598, `Docs/researches/chunks/subset-b-002049_research.md`

## Chunk Research

### subset-b-002027: lines 1-2371

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

### subset-b-002028: lines 2372-4913

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h - subset-b-002028

## Scope

- Chunk id: `subset-b-002028`
- Source lines: 2372-4913
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h`
- Observed content: 2,542 lines, 2,140 `#define` entries, 1,063 `__SHIFT` macros, 1,109 `_MASK` macros, and 384 register/block comments.

This chunk is part of the generated AMD DCN 3.2.1 register shift/mask header. It has no executable C logic; it publishes bit positions and masks for display interrupt routing, DMU/DMCUB control, display writeback, legacy VGA, MCIF writeback, and the beginning of MMHUBBUB warmup control. The macros are the field-layout half of the register API and are used with matching address macros from `dcn_3_2_1_offset.h`.

## Purpose

The purpose of this slice is to describe hardware register fields for several DCN 3.2.1 display subsystems:

- Interrupt destination routing for timing generators, digital encoders, I2C/DDC, HPD, audio, AUX, DCIO, DSC, and HPO-related paths.
- DMU and display power-gating control, including DMCUB enable, clock gating, SMU interrupt fields, domain power-gate config/status, and power-gate interrupt status/mask/clear fields.
- DMCUB memory-window, interrupt, mailbox, scratch, security/fault, timer, GPINT, reset, and memory-power fields.
- DWB frame-capture/writeback and writeback color-processing registers, including crop/source dimensions, update locking, CRC, output format/range, overflow, gamut remap matrices, output gamma LUT control, and two output-gamma RAM bank register sets.
- MMHUBBUB VGA and VGAIF register fields for legacy VGA paging/rendering, pipe selection, memory/cache/HDP controls, CRTC/index/data legacy ports, interrupt status/clear, QoS, and source selection.
- MCIF writeback buffer-manager, buffer-address, status, QoS, watermark, security, resolution, pstate, and VMID fields, plus the first fields of `MMHUBBUB_WARMUP_CONTROL_STATUS`.

In practice, DCN code should never hard-code these bit positions. It references these generated names through register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, and table initializers that convert the generated macro namespace into per-block shift/mask structures.

## Important APIs, Types, and Macros

There are no functions, structs, enums, or static storage declarations in this chunk. The public interface is a set of generated preprocessor macros named as `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`.

Important macro families include:

- `OTG2_INTERRUPT_DEST` tail, then complete `OTG3_INTERRUPT_DEST`, `OTG4_INTERRUPT_DEST`, and `OTG5_INTERRUPT_DEST`: routes OTG CPU start-of-scan, DRR timing, vertical update, snapshot, force-count, force-vsync, trigger A/B, GSL vsync gap, vertical interrupt 0/1/2, vstartup, vready, vsync nominal, no-lock update, and DRR vtotal-reach events.
- `DIG_INTERRUPT_DEST`, `I2C_DDC_HPD_INTERRUPT_DEST`, `DIO_INTERRUPT_DEST`, `DCIO_INTERRUPT_DEST`, `HPD_INTERRUPT_DEST`, `AZ_INTERRUPT_DEST`, `AUX_INTERRUPT_DEST`, and `DSC_INTERRUPT_DEST`: route digital stream-disable and fast-training events, I2C/DDC hardware/software completion and read-request events, DIO ALPM, DCIO DPCS TX/RX errors, HPD and HPD RX events, Azalia endpoint audio format/enabled/disabled events, AUX software/LS/GTC-sync events, and DSC underflow/core-error events.
- DMU miscellaneous and power gating: `CC_DC_PIPE_DIS`, `DMU_CLK_CNTL`, `DMCUB_SMU_INTERRUPT_CNTL`, `SMU_INTERRUPT_CONTROL`, `DMU_MISC_ALLOW_DS_FORCE`, `DOMAIN{0,1,2,3,16,17,18,19}_PG_CONFIG`, `DOMAIN*_PG_STATUS`, `DCPG_INTERRUPT_STATUS`, `DCPG_INTERRUPT_STATUS_2`, `DCPG_INTERRUPT_CONTROL_1`, `DCPG_INTERRUPT_CONTROL_3`, and `DC_IP_REQUEST_CNTL`.
- DMCUB address and firmware-control surfaces: `DMCUB_REGION{0,1,2,4,5,6,7}_OFFSET`, matching `_OFFSET_HIGH`, matching `_TOP_ADDRESS`, `DMCUB_REGION3_CW{0..7}_BASE_ADDRESS`, matching `_TOP_ADDRESS`, matching `_OFFSET`, and matching `_OFFSET_HIGH`.
- DMCUB runtime and interrupt fields: `DMCUB_INTERRUPT_ENABLE`, `DMCUB_INTERRUPT_ACK`, `DMCUB_INTERRUPT_STATUS`, `DMCUB_INTERRUPT_TYPE`, `DMCUB_EXT_INTERRUPT_STATUS`, `DMCUB_EXT_INTERRUPT_CTXID`, `DMCUB_EXT_INTERRUPT_ACK`, fault-address registers, `DMCUB_SEC_CNTL`, `DMCUB_MEM_CNTL`, inbox/outbox base/size/read/write pointers, timer trigger/current/window, scratch registers 0-23, `DMCUB_CNTL`, GPINT data registers, light-sleep wake interrupt enable, `DMCUB_MEM_PWR_CNTL`, `DMCUB_PROC_ID`, `DMCUB_CNTL2`, and `DMCUB_REGION3_TMR_AXI_SPACE`.
- DWB top-level writeback registers: `DWB_ENABLE_CLK_CTRL`, `DWB_MEM_PWR_CTRL`, `FC_MODE_CTRL`, `FC_FLOW_CTRL`, `FC_WINDOW_START`, `FC_WINDOW_SIZE`, `FC_SOURCE_SIZE`, `DWB_UPDATE_CTRL`, `DWB_CRC_*`, `DWB_OUT_CTRL`, `DWB_MMHUBBUB_BACKPRESSURE_*`, `DWB_HOST_READ_CONTROL`, `DWB_OVERFLOW_STATUS`, `DWB_OVERFLOW_COUNTER`, and `DWB_SOFT_RESET`.
- DWB color-processing registers: `DWB_HDR_MULT_COEF`, `DWB_GAMUT_REMAP_MODE`, `DWB_GAMUT_REMAP_COEF_FORMAT`, all `DWB_GAMUT_REMAP{A,B}_C*` coefficient registers, `DWB_OGAM_CONTROL`, `DWB_OGAM_LUT_INDEX`, `DWB_OGAM_LUT_DATA`, `DWB_OGAM_LUT_CONTROL`, `DWB_OGAM_RAM{A,B}_START_*`, `_END_*`, `_OFFSET_*`, and `_REGION_0_1` through `_REGION_32_33`.
- Legacy VGA and VGAIF registers: `VGA_MEM_WRITE_PAGE_ADDR`, `VGA_MEM_READ_PAGE_ADDR`, `VGA_RENDER_CONTROL`, `VGA_SEQUENCER_RESET_CONTROL`, `VGA_MODE_CONTROL`, surface/base-address registers, `VGA_HDP_CONTROL`, `VGA_CACHE_CONTROL`, `D1VGA_CONTROL` through `D6VGA_CONTROL`, status/interrupt/clear registers, `VGA_MAIN_CONTROL`, `VGA_TEST_CONTROL`, `VGA_QOS_CTRL`, legacy indexed/data registers such as `CRTC8_IDX`, `CRTC8_DATA`, `SEQ8_IDX`, `SEQ8_DATA`, `GRPH8_IDX`, `GRPH8_DATA`, palette/DAC registers, `VGA_SOURCE_SELECT`, and VGAIF `MCIF_CONTROL`, write-combine control, and phase outstanding counters.
- MCIF writeback and MMHUBBUB fields: `MCIF_WB_BUFMGR_SW_CONTROL`, `MCIF_WB_BUFMGR_STATUS`, `MCIF_WB_BUF_PITCH`, `MCIF_WB_BUF_{1..4}_STATUS`, `MCIF_WB_BUF_{1..4}_STATUS2`, buffer Y/C address low/high registers, `MCIF_WB_BUFMGR_VCE_CONTROL`, `MCIF_WB_NB_PSTATE_CONTROL`, `MCIF_WB_CLOCK_GATER_CONTROL`, `MCIF_WB_SELF_REFRESH_CONTROL`, `MULTI_LEVEL_QOS_CTRL`, `MCIF_WB_SECURITY_LEVEL`, luma/chroma sizes, per-buffer resolutions, pstate-change duration, VMID, minimum time-to-urgent, `MCIF_WB_NB_PSTATE_LATENCY_WATERMARK`, `MCIF_WB_WATERMARK`, `MMHUBBUB_WARMUP_CONFIG`, and the first `MMHUBBUB_WARMUP_CONTROL_STATUS` shifts.

## Control Flow

This header chunk has no local control flow. Runtime behavior comes from the display driver and hardware:

1. DCN 3.2.1 resource code includes `dcn_3_2_1_offset.h` and this shift/mask header.
2. Resource initialization builds register tables and shift/mask structures, for example `MCIF_WB_COMMON_MASK_SH_LIST_DCN32(__SHIFT)` and `_MASK` in `dcn321_resource.c`.
3. Hardware blocks use those structures through AMD display register helpers. A field update resolves to the register address from the offset header and the shift/mask pair from this header.
4. Hardware then performs the actual state transition: routing an interrupt, changing power-gate state, programming DMCUB memory windows, enabling DWB capture, acknowledging a DWB/MCIF/DMCUB interrupt, programming a VGA path, or polling a status bit.

Several fields encode common hardware control-flow idioms: interrupt status/mask/clear triplets, enable/status/ack pairs, power-gate request/status pairs, DMCUB window base/top/enable sequences, DWB update lock/pending synchronization, double-buffered output-gamma RAM A/B programming, MCIF buffer-manager enable/interrupt/lock/status flows, and MMHUBBUB warmup enable/status/ack behavior.

## State and Persistence Behavior

The macros themselves are compile-time constants and carry no state. They describe MMIO state stored in DCN hardware registers.

Persistent or semi-persistent configuration state includes interrupt destination bits, DMCUB memory windows and mailbox pointers, DMCUB security/QoS/reset controls, DWB crop/source/output/gamut/gamma configuration, VGA memory/page/source/cache controls, MCIF buffer addresses/pitches/sizes/resolutions/security/VMID, watermark values, arbitration slice/time-per-pixel/QoS values, clock-gater overrides, self-refresh policy, and power-gate force/gate controls. These values generally remain until changed by the driver or reset by hardware.

Transient and latched state includes power-gate status, DMCUB interrupt/status/fault bits, DMCUB scratch and GPINT communication values, DWB update pending and overflow status/counters, DWB CRC readback values, VGA interrupt/status bits, MCIF current buffer/current line/overflow/new-content state, watermark-change acknowledgements, and MMHUBBUB warmup interrupt status. Clear and ack fields must be treated as action fields rather than ordinary retained configuration.

The chunk also contains security-sensitive state. `DMCUB_SEC_CNTL`, DMCUB fault clear bits, `MCIF_WB_SECURITY_LEVEL`, `MCIF_WB_SPACE`, `MCIF_WB_VMID_CONTROL`, and TMZ-related MCIF buffer status bits affect or observe protected display memory access. Incorrect use can map firmware or writeback traffic into the wrong memory security domain.

## Dependencies

This generated namespace depends on:

- Matching DCN 3.2.1 register offsets from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h`.
- AMD display register-helper conventions, especially the `REG_*`, `SR`, `SRI`, `SRI2`, `SF`, and `HWS_SF` macro families that expect `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` names.
- DCN 3.2 and DCN 3.2.1 block-specific structures and initializers. Direct observed consumers include `dcn321_resource.c`, which includes this file and initializes MCIF writeback and hardware-sequencer shift/mask tables, and `dcn32_mmhubbub.[ch]`, whose DCN32 MCIF writeback and warmup helpers consume many `MCIF_WB_*` and `MMHUBBUB_WARMUP_*` fields.
- DMCUB service code and firmware contracts for DMCUB memory windows, mailboxes, GPINTs, scratch registers, interrupts, and fault handling.
- DC interrupt-service, link/AUX/I2C/HPD/audio, hardware-sequencer, DWB, MCIF writeback, and VGA disable paths that rely on stable field names across generated ASIC headers.

The correctness of this header is tied to the hardware register database used by AMD's generator. A local source edit that changes a mask or shift without changing the underlying ASIC definition would create silent MMIO corruption.

## Integration Points

The interrupt-destination fields integrate with DC interrupt setup and routing. They determine how OTG, DIG, DDC/I2C, HPD, AUX, audio, DCIO, and DSC events are delivered to the interrupt handling path. The chunk begins in the tail of `OTG2_INTERRUPT_DEST`, so adjacent chunk reports are needed for complete OTG0-2 coverage.

The DMU and power-gating fields integrate with the display hardware sequencer. In `dcn321_resource.c`, `HWSEQ_DCN32_MASK_SH_LIST` consumes domain power force/gate/status fields and `DC_IP_REQUEST_CNTL`. Misprogramming these fields can keep domains powered, power them down while active, or cause polling loops to observe the wrong power state.

DMCUB fields integrate with DMUB boot, memory-window setup, mailbox communication, GPINT signaling, interrupt enable/ack/status logic, and diagnostics. Window registers expose base/top/offset/high halves and enable bits, while inbox/outbox registers expose firmware communication queues. Security and fault fields are part of firmware isolation and recovery.

DWB fields integrate with display writeback controller creation in `dcn321_dwbc_create()` and DCN30 DWB helpers. They configure frame capture, crop dimensions, CRC generation, output format and clamping, overflow reporting, HDR multiplier, gamut remap matrices, and output gamma LUT/RAM banks.

MCIF writeback and MMHUBBUB fields integrate with `dcn321_mmhubbub_create()` and `dcn32_mmhubbub.c`. The DCN32 MCIF code programs four luma/chroma buffer addresses, high address parts, pitch, resolutions, luma/chroma sizes, arbitration and watermarks, buffer-manager interrupts/locks, VMID/security, and warmup base/region/control status. The warmup helper waits on `MMHUBBUB_WARMUP_SW_INT_STATUS`, acknowledges `MMHUBBUB_WARMUP_SW_INT_ACK`, and clears `MMHUBBUB_WARMUP_EN`.

VGA and VGAIF fields integrate with legacy display disable, boot/VBIOS handoff, hardware sequencing, and compatibility paths. `dcn321_resource.c` includes VGA control registers in its hardware-sequencer register set, while common DCE/DCN hardware-sequencer code uses VGA mode fields to blank or disable old VGA paths during modern modeset.

## Risks and Edge Cases

- This file is generated register metadata, so small-looking numeric changes are high risk. A one-bit error in a mask or shift can route interrupts incorrectly, acknowledge the wrong event, program an invalid memory window, or write protected memory.
- The chunk begins mid-register (`OTG2_INTERRUPT_DEST` masks only) and ends inside `MMHUBBUB_WARMUP_CONTROL_STATUS` before that register's masks. The final per-file report must merge adjacent chunks before drawing conclusions about those edge blocks.
- Interrupt fields often have separate destination, status, mask, type, clear, and ack registers with similar names. Confusing `_STATUS`, `_ACK`, `_CLEAR`, `_MASK`, and destination fields can either drop interrupts or create interrupt storms.
- DMCUB memory-window programming requires correct pairing of low/high offset, base, top, and enable fields. Incorrect top/base fields can make firmware fetch from the wrong memory region or fault during boot.
- DMCUB fault clear and security reset fields are action-oriented and security-sensitive. Treating them as ordinary read-modify-write bits can hide faults, trigger resets, or leave data-fault interrupts disabled.
- DWB color/gamma programming is dense and banked. Incorrect RAM A/B region, start/end, base/slope, or LUT-control fields can cause visibly wrong writeback color, stale LUT data, or tearing during update.
- MCIF writeback addresses use split low/high fields and hardware-specific alignment; the consumer code shifts addresses before writing. A mask drift in address or high-address fields can redirect writeback DMA.
- MCIF buffer status registers contain active/locked/overflow/new-content/TMZ/overrun state. Polling or clearing logic must respect which bits are read-only status and which are control or ack fields.
- Power-gate force/gate/status fields are shared with broader display sequencing. Incorrect force-on/gate use may produce hangs around suspend/resume, display idle, or DMCUB-controlled power transitions.
- Legacy VGA fields are still important during boot and handoff even if modern display paths do not use VGA rendering. Incorrect VGA disable or source-select behavior can leave stale VGA memory accesses active.

## Test Signals

Useful validation signals for this chunk include:

- Compile coverage for DCN 3.2.1 resource builds, especially `dcn321_resource.c`, to catch missing or renamed generated macros.
- Generated-header consistency checks that every consumed `SF(..., field, __SHIFT)` has a matching `_MASK`, and that masks are aligned with their shifts and expected field widths.
- Unit or build-time coverage of MCIF writeback tables using `MCIF_WB_COMMON_MASK_SH_LIST_DCN32` for the fields defined here.
- DMCUB boot and firmware communication tests that exercise region setup, inbox/outbox pointers, GPINT data/status, interrupt enable/ack/status, scratch registers, and fault recovery.
- Display writeback validation with multiple buffer slots, luma/chroma planar addresses, high-address bits, pitch/size/resolution programming, watermark/pstate changes, overflow reporting, CRC readback, and output-gamma/gamut programming.
- Hotplug, AUX, I2C/DDC, HPD RX, audio, DSC error, OTG vertical/update, and DCIO error interrupt tests to verify destination routing and clear/ack behavior.
- Suspend/resume and idle-power tests that cover DMU clock gating, domain power gating, DMCUB memory power, DWB memory power, MMHUBBUB/VGA memory power, and MCIF self-refresh/clock-gater fields.
- Legacy VGA handoff/disable tests that confirm `D1VGA_CONTROL` through `D6VGA_CONTROL`, VGA status/clear, source select, and memory/cache controls do not leave stale VGA scanout or memory access active.

## Chunk Boundary Notes

Line 2372 is inside the `OTG2_INTERRUPT_DEST` register block; the shifts and early masks for that block are in the previous chunk. Line 4913 ends after the `MMHUBBUB_WARMUP_CONTROL_STATUS__MMHUBBUB_WARMUP_SW_INT_STATUS__SHIFT` definition; the remaining shifts/masks for that register and later MMHUBBUB fields continue in the next chunk. The merge lane should combine this research with adjacent chunk documents for full-file conclusions.

### subset-b-002029: lines 4914-7582

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h - subset-b-002029

## Scope

- Chunk id: `subset-b-002029`
- Source lines: 4914-7582
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h`
- Observed content: 2,669 lines, 2,053 `#define` entries, 1,025 `__SHIFT` macros, 1,028 `_MASK` macros, 489 register comments, and 42 address-block markers.

This chunk is a generated AMD DCN 3.2.1 register field mask/shift segment. It has no executable C code, no functions, and no C data types. Its purpose is to publish compile-time bit positions and bit masks for DCN321 display hardware registers so AMDGPU Display Core code can pack, unpack, and read-modify-write memory-mapped register fields safely.

## Purpose

The chunk covers the tail of the `dce_dc_mmhubbub_mmhubbub_dispdec` block and then several large display/audio/memory-request blocks:

- `dce_dc_mmhubbub_mmhubbub_dispdec`: MMHUBBUB warmup, writeback watermark, clock, memory-power, soft-reset, VGA/WBIF, and DMU interface status fields.
- `dce_dc_hda_*`: Azalia HDA audio controller, codec root, stream index/data windows, output endpoints, input endpoints, audio clocks, DMA behavior, CRC diagnostics, power states, and audio port connectivity.
- `dce_dc_dchubbubl_hubbub_dispdec`: DCHUBBUB arbitration, watermark set A/B/C/D fields, MALL state, VTG controls, global timer, surface-check addresses, soft reset, clock gating, performance measurement, timeout detection, and FMON controls.
- `dce_dc_dchubbubl_hubbub_sdpif_dispdec`: SDPIF request/response status, PRQ error detection, force-IO capture, framebuffer/AGP/HBM aperture fields, per-pipe security levels, no-allocate behavior, request rate limiting, and SDPIF memory-power state.
- `dce_dc_dchubbubl_hubbub_ret_path_dispdec`: DCHUBBUB return-path memory power, CRC generation/result registers, DCC statistics, compressed buffer controls, DET buffer controls, global memory-power controls, debug, and reserved compbuf space fields.
- `dce_dc_dchubbubl_hubbub_vmrq_if_dispdec`: DCN VM context 0-15 page table controls, context base/start/end address fields, default address, fault control/status, and fault address capture.
- `dce_dc_dcbubp0_dispdec_hubp_dispdec`: HUBP0 surface format, address and tiling configuration, viewport dimensions, request sizing, HUBP control, clock control, VM page config, MALL config/status, and measurement windows.
- `dce_dc_dcbubp0_dispdec_hubpreq_dispdec`: HUBPREQ0 pitch, VMID, primary/secondary/meta surface addresses, flip control, flip interrupts, in-use addresses, TTU/QoS, VM aperture/TLB controls, prefetch, blanking, nominal/vblank/flip delivery parameters, cursor settings, memory power, pstate force, and status.
- `dce_dc_dcbubp0_dispdec_hubpret_dispdec`: HUBPRET0 return/crossbar control, memory power, read-line programming, vblank/read-line interrupts, and read-line snapshots.

The generated pattern is consistent throughout:

- A `//REGISTER_NAME` marker names the hardware register.
- `REGISTER__FIELD__SHIFT` gives the least-significant bit position for a field.
- `REGISTER__FIELD_MASK` gives the field mask within the 32-bit register.

The matching register offsets live in `dcn_3_2_1_offset.h`; this header supplies only field layout.

## Important APIs, Types, and Macros

There are no C APIs, functions, structs, or enums in this chunk. The public interface is the macro namespace.

Important macro families include:

- MMHUBBUB and writeback integration:
  - `MMHUBBUB_WARMUP_CONTROL_STATUS`, `MMHUBBUB_WARMUP_BASE_ADDR_LOW/HIGH`, `MMHUBBUB_WARMUP_ADDR_REGION`, and `MMHUBBUB_WARMUP_VMID_CONTROL` define warmup enable, software interrupt, base address, region, increment, and VMID fields.
  - `WBIF_SMU_WM_CONTROL`, `WBIF0_MISC_CTRL`, and `WBIF0_PHASE*_OUTSTANDING_COUNTER` define writeback watermark change request/ack, SOCCLK deep sleep, interrupt status, timeout, and outstanding-counter fields.
  - `MMHUBBUB_MEM_PWR_STATUS`, `MMHUBBUB_MEM_PWR_CNTL`, `MMHUBBUB_CLOCK_CNTL`, `MMHUBBUB_SOFT_RESET`, `DMU_IF_ERR_STATUS`, and `MMHUBBUB_CLIENT_UNIT_ID` define memory power, gate-disable, soft-reset, DMU error clear, and client unit-id fields.
- Azalia HDA controller and audio codec:
  - `AZALIA_CONTROLLER_CLOCK_GATING`, `AZALIA_AUDIO_DTO`, `AZALIA_AUDIO_DTO_CONTROL`, `AZALIA_SOCCLK_CONTROL`, and `AZ_CLOCK_CNTL` describe audio clock gating, DTO phase/module, forced DTO behavior, SOCCLK deep-sleep exit, and test-clock selection.
  - `AZALIA_DATA_DMA_CONTROL`, `AZALIA_BDL_DMA_CONTROL`, `AZALIA_RIRB_AND_DP_CONTROL`, and `AZALIA_CORB_DMA_CONTROL` describe snoop/isochronous behavior and DMA/control-ring behavior for audio data, BDL, RIRB, DP updates, and CORB traffic.
  - `AZALIA_INPUT_CRC*` and `AZALIA_CRC*` define CRC enable, sample/continuous/block modes, block iteration, completion/status, channel select, and CRC result fields.
  - `AZALIA_MEM_PWR_CTRL` and `AZALIA_MEM_PWR_STATUS` expose global audio memory power plus per-input-stream memory power state for streams 0-5.
  - `AZALIA_F0_CODEC_*`, `CC_RCU_DC_AUDIO_*`, and `REG_DC_AUDIO_*` publish codec vendor/revision, supported rates/formats/power states, reset, subsystem response, converter sync, GTC group offsets, and audio output/input port connectivity override fields.
  - `AZF0STREAM0` through `AZF0STREAM15`, `AZF0ENDPOINT0` through `AZF0ENDPOINT7`, and `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7` are repeated index/data windows for stream and endpoint register access.
- DCHUBBUB arbitration and global controls:
  - `DCHUBBUB_ARB_DF_REQ_OUTSTAND`, `DCHUBBUB_ARB_SAT_LEVEL`, `DCHUBBUB_ARB_QOS_FORCE`, `DCHUBBUB_ARB_DRAM_STATE_CNTL`, and `DCHUBBUB_ARB_USR_RETRAINING_CNTL` define request outstanding thresholds, saturation, urgent/nominal QoS force, self-refresh/pstate gating, and retraining policy.
  - `DCHUBBUB_ARB_*_WATERMARK_A/B/C/D`, `DCHUBBUB_ARB_FRAC_URG_BW_*`, and `DCHUBBUB_ARB_WATERMARK_CHANGE_CNTL` define four watermark sets for urgency, self-refresh enter/exit, UCLK/FCLK pstate change, retraining, trip-to-memory, urgent bandwidth fractions, and the request/done/status handshake used to switch sets.
  - `DCHUBBUB_ARB_MALL_CNTL`, `SURFACE_CHECK*_ADDRESS_*`, `VTG0_CONTROL` through `VTG3_CONTROL`, `DCHUBBUB_GLOBAL_TIMER_CNTL`, `DCHUBBUB_PERFORMANCE_MEASUREMENT_CNTL*`, `DCHUBBUB_TIMEOUT_*`, and `FMON_CTRL` define MALL use/prefetch state, surface checker addresses, vertical timing generator counters, timer setup, latency instrumentation, timeout status/interrupts, and frame monitor controls.
- SDPIF, aperture, and security:
  - `DCHUBBUB_SDPIF_CFG0/1/2` define outstanding request status, port/response state, credit errors, PRQ errors, force-snoop, host VM security level, and unit-id bitmasks.
  - `VM_REQUEST_PHYSICAL`, `DCHUBBUB_FORCE_IO_STATUS_0/1`, `DCN_VM_FB_LOCATION_*`, `DCN_VM_AGP_*`, and `DCN_VM_LOCAL_HBM_ADDRESS_*` define physical request forcing/capture and the display VM aperture ranges for framebuffer, AGP, and local HBM.
  - `DCHUBBUB_SDPIF_PIPE_*_SEC_LVL`, `DCHUBBUB_SDPIF_PIPE_NOALLOC`, and `SDPIF_REQUEST_RATE_LIMIT` define per-pipe security, per-request-class security, no-allocate, and rate-limiting fields.
- Return path, CRC, DCC, and buffers:
  - `DCHUBBUB_RET_PATH_MEM_PWR_*`, `DCHUBBUB_CRC_CTRL`, `DCHUBBUB_CRC*_VAL_*`, and `DCHUBBUB_DCC_STAT*` define return-path SRAM state, CRC mode/selection/result, and DCC statistics.
  - `DCHUBBUB_COMPBUF_CTRL`, `DCHUBBUB_DET*_CTRL`, `DCHUBBUB_MEM_PWR_MODE_CTRL`, `COMPBUF_MEM_PWR_CTRL_*`, `DCHUBBUB_MEM_PWR_STATUS`, `COMPBUF_RESERVED_SPACE`, and `DCHUBBUB_DEBUG_CTRL_0` define compressed-buffer size, DET buffer configuration, per-bank memory power force/disable/mode, memory status, reserved space, and debug selection.
- DCN VM context and faults:
  - `DCN_VM_CONTEXT0_CNTL` through `DCN_VM_CONTEXT15_CNTL` define page-table depth and block size for each VMID context.
  - Each context has `PAGE_TABLE_BASE_ADDR_HI32/LO32`, `PAGE_TABLE_START_ADDR_HI32/LO32`, and `PAGE_TABLE_END_ADDR_HI32/LO32` fields for directory base and logical page range programming.
  - `DCN_VM_DEFAULT_ADDR_MSB/LSB`, `DCN_VM_FAULT_CNTL`, `DCN_VM_FAULT_STATUS`, and `DCN_VM_FAULT_ADDR_MSB/LSB` define default fault address behavior, fault clear/mode/interrupt enable, range/PRQ fault disable bits, faulting VMID/table level/pipe, and captured fault address.
- HUBP0 and HUBPREQ0 surface request path:
  - `HUBP0_DCSURF_SURFACE_CONFIG`, `HUBP0_DCSURF_ADDR_CONFIG`, `HUBP0_DCSURF_TILING_CONFIG`, viewport registers, `HUBP0_DCHUBP_REQ_SIZE_CONFIG*`, `HUBP0_DCHUBP_CNTL`, `HUBP0_HUBP_CLK_CNTL`, `HUBP0_DCHUBP_VMPG_CONFIG`, and `HUBP0_DCHUBP_MALL_*` define pixel format, rotation, mirroring, alpha plane enable, swizzle/tiling, chunk sizes, stereo/blanking/reorder behavior, clock gating, VM page config, and MALL mode/status.
  - `HUBPREQ0_DCSURF_*_ADDRESS*`, `HUBPREQ0_DCSURF_SURFACE_CONTROL`, `HUBPREQ0_DCSURF_FLIP_CONTROL*`, `HUBPREQ0_DCSURF_SURFACE_FLIP_INTERRUPT`, and `HUBPREQ0_DCSURF_SURFACE_INUSE*` define primary/secondary/luma/chroma/meta addresses, flip mode, flip request/ack/pending status, interrupt control/clear/status, and in-use/earliest-in-use address tracking.
  - `HUBPREQ0_DCN_TTU_QOS_WM`, `HUBPREQ0_DCN_GLOBAL_TTU_CNTL`, `HUBPREQ0_DCN_SURF*_TTU_CNTL*`, `HUBPREQ0_DCN_CUR*_TTU_CNTL*`, `HUBPREQ0_DCN_DMDATA_VM_CNTL`, `HUBPREQ0_DCN_VM_*`, `HUBPREQ0_PREFETCH_SETTINGS*`, `HUBPREQ0_VBLANK_PARAMETERS_*`, `HUBPREQ0_FLIP_PARAMETERS_*`, `HUBPREQ0_NOM_PARAMETERS_*`, and `HUBPREQ0_PER_LINE_DELIVERY*` define TTU/QoS, cursor and surface delivery timing, metadata VM behavior, aperture/TLB controls, prefetch, vblank, flip, and nominal request timing.
- HUBPRET0 return/timing:
  - `HUBPRET0_HUBPRET_CONTROL`, `HUBPRET0_HUBPRET_MEM_PWR_*`, `HUBPRET0_HUBPRET_READ_LINE_CTRL*`, `HUBPRET0_HUBPRET_READ_LINE0/1`, `HUBPRET0_HUBPRET_INTERRUPT`, and `HUBPRET0_HUBPRET_READ_LINE_VALUE` define DET base, 3-to-2 packing, crossbar source selection, return-path memory power, programmable read-line windows, vblank/read-line interrupt mask/type/clear/status, and current/snapshotted pipe read line.

## Control Flow

The header has no runtime control flow. The runtime flow is supplied by DCN321 display code:

1. `drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c` includes `dcn_3_2_1_offset.h` and `dcn_3_2_1_sh_mask.h`.
2. DC resource construction builds register, shift, and mask tables for blocks such as hubbub, VMID, HUBP, audio, AFMT/VPG/APG, DWB, and MMHUBBUB.
3. Block constructors such as `hubbub32_construct`, `dce_audio_create`, `dcn30_dwbc_construct`, and `dcn32_mmhubbub_construct` receive pointers to those register/shift/mask tables.
4. Runtime code uses AMD display register helpers to write fields by applying the generated shift/mask constants to 32-bit MMIO register values.
5. Hardware state machines then act on the programmed bits, while status and diagnostic fields are read back through the same macro contract.

The implied hardware flows include:

- Programming watermark set A/B/C/D fields, requesting a DCHUBBUB watermark switch, and checking the change-done status.
- Programming VM context base/start/end registers before enabling HUBP/HUBPREQ fetches for a VMID.
- Staging surface address, pitch, tiling, viewport, TTU, and prefetch fields before surface flip request/ack handling.
- Handling flip and vblank/read-line interrupts by masking, clearing, and reading the status fields.
- Configuring audio clocks, stream windows, endpoint windows, and DMA/CRC behavior through Azalia index/data and control registers.
- Reading timeout, VM fault, force-IO, CRC, DCC, outstanding request, and memory-power status fields for debug and recovery.

## State and Persistence Behavior

The macros are compile-time constants and persist only in the compiled driver image. They describe hardware register state with these lifetimes:

- Persistent until reset or reprogrammed: surface format/tiling/pitch, viewport dimensions, VM context page-table ranges, MALL policy, TTU/QoS timing, watermark sets, audio DTO/DMA policy, memory-power modes, clock-gate disables, soft-reset control bits, and endpoint/stream index selections.
- Transactional or handshake state: DCHUBBUB watermark change request/done/status, WBIF watermark change request/status, surface flip request/ack/pending, interrupt clear/status bits, warmup interrupt status/ack, timeout clear, VM fault clear, CRC sample/reset controls, and memory-power force/disable transitions.
- Captured or sampled status: outstanding counters, VM fault VMID/table/pipe/address, force-IO address/request type, CRC result values, DCC statistics, surface-in-use addresses, pipe read-line snapshots, MALL prefetch complete, ROB overflow, FMON state, pstate/self-refresh permissions, and HUBPREQ status registers.
- Power-management state: multiple blocks expose paired `*_MEM_PWR_CTRL` and `*_MEM_PWR_STATUS` fields. Driver writes force/disable/mode bits and polls or reads state bits for MMHUBBUB, Azalia, SDPIF, return path, compbuf/DET, HUBPREQ, and HUBPRET memories.

Because this is a hardware register contract, incorrect constants can be persistent at runtime even though the macros themselves are static. A wrong mask or shift can cause the driver to preserve, clear, or set the wrong MMIO bits until the affected block is reset or reprogrammed.

## Dependencies

Direct dependencies and pairings:

- The matching offset header `dcn_3_2_1_offset.h` provides register addresses and base-index information. This file provides the field layout for those addresses.
- AMD Display Core register helpers (`reg_helper.h` and related macros) consume shift/mask pairs to compose writes and extract readback fields.
- DCN321 resource construction in `display/dc/resource/dcn321/dcn321_resource.c` includes this header and passes generated tables into hubbub, HUBP, audio, DWB, MMHUBBUB, timing, stream, and encoder-related block constructors.
- Shared DCN32/DCN30/DCN20 implementations consume these tables because DCN321 reuses many common block implementations while providing chip-specific register offsets and field masks.
- Hardware semantics come from DCN 3.2.1 display IP: DCHUBBUB, HUBP/HUBPREQ/HUBPRET, MMHUBBUB/WBIF, Azalia HDA, SDPIF, and VM request interfaces.

## Integration Points

- DCN321 device bring-up: `amdgpu_dm.c` selects `DMUB_ASIC_DCN321`, and `dc_resource.c` creates the DCN321 resource pool, which includes this header through `dcn321_resource.c`.
- HUBBUB and VMID: `dcn321_hubbub_create()` initializes DCHUBBUB and VMID register/shift/mask tables, including the DCHUBBUB arbitration/VM/fault fields in this chunk.
- HUBP0 request pipeline: `dcn321_hubp_create()` initializes HUBP instances. The HUBP0/HUBPREQ0/HUBPRET0 fields in this chunk are the instance-0 template for surface fetch and timing behavior; generated macro-list patterns commonly replicate these for other instances through offset/header conventions.
- Audio: `dcn321_create_audio()`, AFMT, VPG, APG, and stream encoder creation use audio-related register tables. The Azalia and audio codec macros here are the low-level HDA field definitions for display audio paths.
- Writeback/MMHUBBUB: `dcn321_dwbc_create()` and `dcn321_mmhubbub_create()` construct writeback and MMHUBBUB objects using generated register fields such as WBIF, MCIF/WB, MMHUBBUB warmup, watermark, and memory-power controls.
- Diagnostics and recovery: VM fault, timeout, CRC, DCC, force-IO, outstanding counter, and interrupt status fields provide observable signals for debugfs, driver logs, hardware recovery paths, and bring-up validation.

## Risks

- Generated-header drift: This file must match the actual DCN 3.2.1 register specification and `dcn_3_2_1_offset.h`. A mismatch can silently program the wrong bits.
- Cross-version confusion: Many names are similar to DCN 3.2.0 and later DCN 3.5.x headers, but fields can diverge. Copying masks between ASIC generations risks invalid programming.
- Read-modify-write hazards: A wrong mask can clobber adjacent control bits, especially in dense registers such as `DCHUBBUB_ARB_DRAM_STATE_CNTL`, `HUBPREQ0_DCSURF_SURFACE_CONTROL`, `HUBPREQ0_DCSURF_FLIP_CONTROL`, `DCHUBBUB_CRC_CTRL`, and Azalia memory-power controls.
- Interrupt and clear-bit semantics: Registers with `*_CLEAR`, `*_ACK`, `*_STATUS`, and `*_INT_STATUS` fields may use write-one-to-clear or sticky semantics. Treating them as ordinary persistent fields can lose interrupts or leave stale status asserted.
- VM and fault containment: VM context, aperture, default address, and fault-disable fields affect display memory translations. Incorrect settings can produce blank scanout, GPU page faults, or reads from unintended physical ranges.
- Power and clock gating: MMHUBBUB, DCHUBBUB, HUBP, HUBPREQ, HUBPRET, SDPIF, Azalia, and WBIF power/clock fields can gate required memories or clocks. Bad programming may surface as hangs, underruns, audio dropouts, timeout interrupts, or failed flips.
- Timing sensitivity: Watermark, TTU, prefetch, pstate, and per-line delivery fields interact with display mode timing. Incorrect values may pass compile tests but fail under high bandwidth, multi-plane, MALL, self-refresh, or pstate-transition workloads.
- Repeated index/data windows: Azalia stream/endpoint macros are repetitive. Off-by-one instance use can route programming to the wrong audio stream or endpoint without compiler diagnostics.

## Test Signals

Useful validation signals for changes involving this chunk:

- Build coverage: compile AMDGPU/DC with DCN321 enabled; missing or renamed macros should fail at compile time in `dcn321_resource.c` or shared DCN block code.
- Register table sanity: compare generated shift/mask entries against `dcn_3_2_1_offset.h` and the ASIC register source used to generate both files.
- Boot/probe: verify DCN321 hardware initializes the resource pool, creates hubbub, HUBP, audio, DWB, and MMHUBBUB objects, and reaches display modeset without register access faults.
- Display modes: exercise single and multi-plane scanout, rotation/mirroring/alpha plane, luma/chroma formats, DCC/meta surfaces, cursor, page flips, vblank, and read-line interrupts.
- Memory and VM: test VMID context programming, GPUVM/system aperture modes, fault reporting, force-IO status capture, and fault interrupt clear/status paths.
- Power management: test MALL, self-refresh, UCLK/FCLK pstate transitions, clock gating, memory power collapse/restore, warmup, and writeback watermark changes while watching timeout, ROB overflow, underrun, and flip status fields.
- Audio: test DP/HDMI audio stream creation, endpoint routing, HBR/compressed channel counts, audio DTO programming, DMA snoop/isochronous settings, and CRC/underflow diagnostics.
- Diagnostics: read CRC results, DCC stats, DCHUBBUB performance counters, FMON state, outstanding counters, surface-in-use addresses, and HUBPREQ status under active scanout to confirm masks extract plausible non-stuck values.

### subset-b-002030: lines 7583-10082

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 7583-10082

## Scope

This chunk is a generated AMD DCN 3.2.1 register field shift/mask header segment. It covers 2,500 source lines and 2,111 `#define` entries. The chunk has no executable C code; its API surface is the macro namespace that gives low-bit shifts and already-positioned masks for display HUBP, HUBPREQ, HUBPRET, cursor, DMDATA, VM, timing, MALL, power, and status registers.

The range begins at the tail of pipe 0 HUBPRET read-line status, covers the pipe 0 cursor block, then spans the complete visible HUBP/HUBPREQ/HUBPRET/cursor groups for pipes 1 and 2. It ends inside the pipe 3 HUBPREQ timing block at `HUBPREQ3_PREFETCH_SETTINGS__VRATIO_PREFETCH__SHIFT`, so adjacent chunks are needed to complete pipe 3.

## Purpose

The purpose of this header slice is to provide compile-time metadata for packing and unpacking DCN 3.2.1 display hub register fields. Every hardware field is represented as:

- `<REGISTER>__<FIELD>__SHIFT`, the least-significant bit position.
- `<REGISTER>__<FIELD>_MASK`, the field mask in its register position.

Driver code combines these constants with register offset macros from `dcn_3_2_1_offset.h` and register helper macros from AMD Display Core. This keeps register programming code focused on semantic field names such as `SURFACE_PIXEL_FORMAT`, `CURSOR_ENABLE`, `VMID`, `SURFACE_FLIP_PENDING`, `REFCYC_PER_REQ_DELIVERY`, or `HUBP_UNDERFLOW_STATUS`, while the generated header preserves the exact silicon bit layout.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or storage objects in this chunk. The important API is the set of generated preprocessor constants.

The covered register families include:

- `HUBPRET0_HUBPRET_READ_LINE_STATUS`: pipe 0 read-line/vblank status bits at the chunk boundary.
- `CURSOR0_0_*`, `CURSOR0_1_*`, and `CURSOR0_2_*`: cursor enable, request mode, magnification, mode, trusted-memory-zone bit, pitch, line chunking, surface address, size, position, hot spot, stereo offsets, destination offset, cursor memory power state, and DMDATA controls/status.
- `HUBP1_*` and `HUBP2_*`: surface format, rotation, mirror, alpha-plane enable, tiling/address configuration, primary/secondary viewport geometry for luma and chroma planes, request sizing, HUBP blank/reset/status controls, clock gating/status, virtual-memory page config, MALL config, sub-viewport MALL start lines, clock-measurement windows, and MALL state.
- `HUBPREQ1_*` and `HUBPREQ2_*`: surface pitch, VMID, primary/secondary and meta surface addresses for luma/chroma, TMZ and DCC surface-control bits, flip control, flip interrupts, in-use/earliest-in-use address readbacks, expansion modes, TTU/QoS controls, DMDATA VM controls, system aperture and L1 TLB controls, blank/destination/prefetch timing, vblank/flip/nominal delivery parameters, cursor fetch settings, memory power controls/status, UCLK p-state force controls, and request/status registers.
- `HUBPRET1_*` and `HUBPRET2_*`: DET buffer base, crossbar source selection, pack disable, memory power control/status, read-line thresholds, interrupt fields, read-line values, and read-line status.
- `HUBP3_*` and the start of `HUBPREQ3_*`: pipe 3 repeats the same HUBP surface, viewport, request-size, MALL, and early HUBPREQ surface-address/flip/VM/timing layout before the chunk cuts off.

The macro prefixes are pipe-indexed. For example, `HUBPREQ1_DCSURF_PRIMARY_SURFACE_ADDRESS_HIGH__PRIMARY_SURFACE_ADDRESS_HIGH_MASK` and `HUBPREQ2_DCSURF_PRIMARY_SURFACE_ADDRESS_HIGH__PRIMARY_SURFACE_ADDRESS_HIGH_MASK` describe the same field shape on different hardware instances. Higher-level register table macros typically use pipe 0 names as templates and pair them with per-instance register offsets.

## Control Flow And Behavior

This header has no runtime control flow. Runtime behavior appears when included by DCN 3.2.1 resource construction and consumed through AMD Display Core register helper tables.

A typical consumer flow is:

1. A DCN 3.2.1 resource file includes `dcn_3_2_1_offset.h` and `dcn_3_2_1_sh_mask.h`.
2. HUBP/DPP/IPP register-table macros such as `HUBP_SF` or related field-list helpers copy the generated shift and mask values into hardware block descriptors.
3. Runtime code uses `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, or related helpers to modify fields by semantic names rather than open-coded bit arithmetic.
4. Hardware latches the values into the display hub pipeline, where they control fetch addresses, tiling, DCC/TMZ, timing, prefetch, VM translation, cursor fetch, MALL behavior, and flip synchronization.

Important implied hardware flows represented by the chunk:

- Plane programming: pixel format, rotation, mirror, alpha-plane state, address configuration, tiling, viewport start/dimension, pitch, DCC, TMZ, primary/secondary surface addresses, and meta addresses describe how HUBP fetches the current scanout surface.
- Flip sequencing: `DCSURF_FLIP_CONTROL`, `DCSURF_FLIP_CONTROL2`, `SURFACE_FLIP_INTERRUPT`, in-use address registers, earliest-in-use registers, stereo sync fields, GSL/triple-buffer controls, and pending-delay/min-time fields support atomic flips and frame-latched surface transitions.
- Display timing and watermarks: `BLANK_OFFSET_*`, `DST_DIMENSIONS`, `DST_AFTER_SCALER`, `PREFETCH_SETTINGS`, `VBLANK_PARAMETERS_*`, `FLIP_PARAMETERS_*`, `NOM_PARAMETERS_*`, `PER_LINE_DELIVERY*`, `DCN_TTU_QOS_WM`, and `DCN_*_TTU_CNTL*` encode DML-derived delivery timing and QoS programming.
- VM and memory fetch: VMID, system aperture, L1 TLB enable/mode, VM group/request timing, page-table request sizes, DPTE/MPTE/meta/PDE memory power fields, and DMDATA VM fault/underflow/late/done status connect display fetch to GPU virtual memory.
- Cursor and DMDATA: cursor address, size, position, hot spot, stereo, chunking, memory power, DMDATA address/control/QoS/status, and software DMDATA controls support hardware cursor display and display metadata delivery.
- MALL and power management: `DCHUBP_MALL_CONFIG`, `DCHUBP_MALL_SUB_VP`, `HUBP_MALL_STATUS`, `UCLK_PSTATE_FORCE`, clock gates, memory power state fields, self-refresh allowances, and p-state status bits expose low-power scanout and memory/cache behavior.
- Interrupt/status paths: read-line/vblank, flip, timeout, underflow, segmentation allocation error, MALL status, VM faults, and request-status registers provide diagnostics and event state.

## State And Persistence

The header itself stores no state. Its constants describe state held in GPU hardware registers after driver or firmware writes them.

State classes represented here include:

- Latched plane state: format, tiling, viewport, pitch, surface and metadata addresses, VMID, TMZ/DCC enablement, and cursor address/geometry persist in the display pipe until reprogrammed, reset, or power-gated.
- Flip and scanout state: pending, in-use, earliest-in-use, stereo-sync, update-lock, GSL, and triple-buffer fields track transition state across frame and vblank boundaries.
- Timing state: prefetch, vblank, flip, nominal, TTU, QoS, and per-line delivery fields are derived from mode timing and bandwidth calculations and must match the current stream/plane configuration.
- VM and fault state: system aperture, L1 TLB mode, VMID, DMDATA VM status, underflow, late, fault status, and clear bits are tied to GPU VM programming and display fetch health.
- Power and residency state: clock-enable/status, memory power force/disable/state, MALL use, sub-viewport MALL retrieval, self-refresh, p-state allowance, and UCLK force bits reflect low-power display operation.
- Sticky or clear-on-write status: underflow clear, timeout status clear, DMDATA underflow/fault clears, flip clears, and read-line interrupt clears likely require precise hardware-defined write sequences.

Because this is a generated bitfield schema, it does not encode read/write permissions, reset defaults, legal enumerations, self-clearing behavior, polling requirements, or ordering constraints. Those rules live in the hardware programming sequence and in the display core functions that use the fields.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.2.1 generated register map:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h`

`dcn321_resource.c` directly includes both generated headers. HUBP field-list macros in files such as `display/dc/hubp/dcn31/dcn31_hubp.h`, `display/dc/hubp/dcn32/dcn32_hubp.h`, and the shared DCN hubp headers consume the same field names through `HUBP_SF` definitions. The resulting mask/shift descriptors are used by hubp implementation files through register helpers such as `REG_UPDATE`, `REG_UPDATE_2`, `REG_UPDATE_4`, `REG_GET`, and related macros.

Cursor fields also integrate with DMUB cursor offload payload structures in `display/dmub/inc/dmub_cmd.h`, which use matching field-oriented names for cursor address, size, position, hot spot, destination offset, enable, mode, magnification, pitch, and line-chunk data. This means cursor register layout changes affect both host-side register programming and firmware offload command interpretation.

Even though this repository path is under `ceph-client`, the researched code is AMDGPU display hardware metadata. It has no Ceph filesystem protocol behavior, distributed filesystem persistence, or storage control flow.

## Risks And Edge Cases

- Silent hardware misprogramming: a wrong `_MASK` or `__SHIFT` compiles cleanly but can update the wrong MMIO bits, causing blank screens, underflow, incorrect colors, address faults, or unstable flips.
- Pipe-index repetition: the same field shapes are repeated for `HUBP1`, `HUBP2`, `HUBP3`, `HUBPREQ1`, `HUBPREQ2`, `HUBPREQ3`, `HUBPRET1`, `HUBPRET2`, and cursor instances. Generation or copy errors can be valid C while affecting only one physical pipe.
- Chunk boundaries: the range starts after the beginning of the pipe 0 HUBPRET block and ends inside `HUBPREQ3_PREFETCH_SETTINGS`; final per-file analysis must reconcile adjacent chunks before drawing conclusions about full pipe 0 or pipe 3 coverage.
- Address width and high-bit handling: surface and metadata addresses are split into low 32-bit and high 16-bit fields, with VMID fields often in high address registers. Incorrect packing can point scanout at the wrong memory object or VM context.
- Flip synchronization hazards: update locks, pending flags, stereo sync mode, GSL enable/mask, triple buffering, and in-use address readbacks are timing-sensitive and can deadlock or tear if accessed out of order.
- VM and fault clear hazards: DMDATA VM fault, underflow, late, done, system aperture, L1 TLB mode, and clear fields can mask real GPU VM faults or leave stale fault state if decoded incorrectly.
- Power-management coupling: MALL, UCLK p-state force, self-refresh allow bits, memory power force/disable/state, and clock-gating fields interact with runtime power management and display underflow margins.
- Reserved or status fields: status and clear bits should not be treated as ordinary writable configuration fields. The header names and masks alone do not prevent unsafe writes.

## Test Signals

Useful validation signals for consumers of this chunk include:

- Kernel build coverage for DCN 3.2.1 display resource construction and HUBP/DPP/IPP register-table initialization.
- Generated-header consistency checks that every paired `_MASK` and `__SHIFT` describes a non-overlapping field and matches the authoritative register database.
- Boot and modeset tests on DCN 3.2.1 hardware using all available display pipes, with rotation, mirroring, alpha planes, luma/chroma surfaces, DCC, TMZ, and cursor enabled.
- Atomic page-flip and vblank tests that exercise update locks, flip pending, flip interrupts, stereo/GSL/triple-buffer paths, in-use address readbacks, and earliest-in-use tracking.
- Cursor tests for address split, size, hot spot, position, destination offset, magnification, pitch, chunk size, MALL cursor caching, and DMUB cursor offload.
- Display bandwidth and DML validation using high-resolution and multi-plane modes to confirm prefetch, vblank, flip, nominal, TTU, QoS, and per-line delivery programming avoids underflow.
- GPU VM tests that exercise display VMID, system aperture, L1 TLB, DMDATA VM fault/underflow/late/done status, and VM fault clear behavior.
- Runtime power tests covering MALL, sub-viewport MALL, static-screen behavior, UCLK/FCLK p-state transitions, clock gating, memory power state, suspend/resume, and hotplug.
- Debugfs or trace readbacks for HUBP underflow, timeout, segment allocation errors, read-line/vblank status, MALL status, DMDATA status, flip status, and request status registers.

## Research Notes

The source was read as a large generated-header chunk rather than as hand-written logic. The final per-file research document should merge this with neighboring chunks of `dcn_3_2_1_sh_mask.h` so the complete repeated-pipe layout is described once, with this chunk contributing the pipe 1/2 hub, request, return, cursor, VM, MALL, timing, and status details plus the pipe 3 boundary note.

### subset-b-002031: lines 10083-12636

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 10083-12636

Chunk: `subset-b-002031`
Covered source range: lines 10083-12636 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h`

## Purpose

This chunk is a generated AMD DCN 3.2.1 register field shift/mask header section. It contains C preprocessor constants used to encode and decode bitfields in display-controller MMIO registers; it does not contain executable driver logic.

The covered range contains 2,107 `#define` entries: 1,054 `__SHIFT` constants and 1,059 `_MASK` constants, grouped under 414 register comments and 11 address-block boundaries. It starts mid-register at the tail of `HUBPREQ3_PREFETCH_SETTINGS`, continues through the rest of several HUBP/DPP instance 3 and DPP instance 0/1 blocks, and ends mid-table inside `CM1_CM_GAMCOR_RAMB_REGION_26_27`.

Major hardware areas covered are:

- `HUBPREQ3` timing, prefetch, vblank, flip, nominal delivery, cursor request, memory power, UCLK p-state force, and status fields.
- `HUBPRET3` detile/read-line control, buffer crossbar, memory power, interrupt, and read-line status fields.
- `CURSOR0_3` cursor surface, size, position, hot spot, stereo, memory power, DMDATA address/control/QoS/status, and software DMDATA fields for HUBP/DPP instance 3.
- `CNVC_CFG0` and `CNVC_CFG1` format-converter fields for surface pixel format, alpha, format expansion, 16-bit conversion, crossbar, floating-point bias/scale, color/luma keying, pre-dealpha, pre-CSC matrices, coefficient format, pre-degamma, and pre-realpha.
- `CNVC_CUR0` and `CNVC_CUR1` cursor formatter fields for cursor mode, expansion, enable, pixel inversion, alpha modulation, ROM selection, colors, and FP scale/bias.
- `DSCL0` and `DSCL1` scaler fields for coefficient RAM access, mode, tap count, 2-tap controls, manual replication, horizontal/vertical scaling ratios and initial phases for luma/chroma, black color, update/autocal, overscan, blanking, RECOUT, MPC size, line-buffer format/memory, memory power, OBUF control, and OBUF memory power.
- `CM0` and `CM1` color-management fields for post-CSC matrices, gamut-remap matrices, bias, gamma-correction control and LUT access, gamma RAM A/B region programming, HDR multiplier, memory power, dealpha, coefficient format, and debug index.
- `DPP_TOP0` top-level DPP clock, soft-reset, CRC value/control, and host-read rate fields.

## Important APIs, Types, And Macros

There are no functions, structs, enums, callbacks, or runtime APIs in this chunk. The interface is the generated macro contract shared by AMDGPU Display Core:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for the field.
- `//<REGISTER>` comments group fields that belong to one register.
- `// addressBlock: ...` comments mark hardware register-block boundaries.
- The companion offset header, `dcn_3_2_1_offset.h`, supplies matching `reg<REGISTER>` and `reg<REGISTER>_BASE_IDX` address constants.

Important field families in this range include:

- HUBP request timing: `HUBPREQ3_VBLANK_PARAMETERS_*`, `HUBPREQ3_FLIP_PARAMETERS_*`, `HUBPREQ3_NOM_PARAMETERS_*`, `HUBPREQ3_PER_LINE_DELIVERY*`, `HUBPREQ3_REF_FREQ_TO_PIX_FREQ`, and `HUBPREQ3_DST_Y_DELTA_DRQ_LIMIT` describe VM/PTE/meta request timing during vblank, flip, nominal scanout, prefetch, and per-line delivery.
- HUBP power/status: `HUBPREQ3_HUBPREQ_MEM_PWR_CTRL`, `HUBPREQ3_HUBPREQ_MEM_PWR_STATUS`, `HUBPREQ3_UCLK_PSTATE_FORCE`, and `HUBPREQ3_HUBPREQ_STATUS_REG*` expose memory power force/disable/state, UCLK p-state force controls, row/chunk readiness, self-refresh entry/exit, p-state-change allowance, urgent QoS, vblank, pipe recovery/flush, HUBP enable, and flip-active status.
- HUBPRET read-line/detile controls: `HUBPRET3_HUBPRET_CONTROL`, memory power fields, `HUBPRET3_HUBPRET_READ_LINE_CTRL*`, `HUBPRET3_HUBPRET_READ_LINE*`, interrupt fields, read-line value, and status fields support detector-buffer layout, crossbar source selection, read-line capture, and line interrupt behavior.
- Cursor/DMDATA: `CURSOR0_3_CURSOR_*` fields control GPU cursor memory address, dimensions, pitch/mode, enable, x/y position, hot spot, stereo behavior, destination offsets, cursor memory power, and dynamic metadata payload address/control/status/software update semantics.
- CNVC format conversion: `CNVC_CFG0_*` and `CNVC_CFG1_*` fields map surface pixel format, alpha plane, bypass, MSB alignment, clamp, channel crossbar, color-key thresholds, 2-bit alpha LUT, floating-point conversion scale/bias, pre-dealpha, pre-CSC mode/matrix, pre-degamma selection, and pre-realpha controls.
- DSCL scaler programming: `DSCL0_*` and `DSCL1_*` fields cover scaler mode, coefficient RAM selection/phase/filter/tap data, tap counts, 2-tap sharpening, manual replication, luma/chroma scale ratios and init phases, autocal pipe selection, recout/MPC geometry, line-buffer partitioning, clock/memory power, and OBUF controls.
- CM color management: `CM0_*` and `CM1_*` fields cover post-CSC and gamut-remap 3x4 matrix programming, gamma-correction mode/current mode, LUT index/data/control, RAMA/RAMB start/end/offset/region metadata for B/G/R channels, HDR multiplier, GAMCOR memory power, dealpha, coefficient format, and debug index.
- DPP top-level diagnostics and control: `DPP_TOP0_DPP_CONTROL`, `DPP_TOP0_DPP_SOFT_RESET`, `DPP_TOP0_DPP_CRC_*`, and `DPP_TOP0_HOST_READ_CONTROL` control DPP clocks/gating/test clock, CNVC/DSCL/CM/OBUF reset, DPP CRC capture/readback, and host-read pacing.

The repeated-instance pattern matters. The chunk contains full `CNVC_CFG0`, `CNVC_CUR0`, `DSCL0`, `CM0`, and `DPP_TOP0` definitions, then repeats much of the same DPP surface for instance 1. Instance 3 appears for HUBPREQ/HUBPRET/cursor state at the beginning. A macro from the wrong instance usually has the same field meaning but must be paired with the correct register address table.

## Control Flow

This header has no internal control flow. Runtime flow occurs in Display Core consumers that include this file, expand generated register-list macros, and pass the resulting address, shift, and mask tables to hardware object constructors.

The main path in this tree is `display/dc/resource/dcn321/dcn321_resource.c`. That file includes `dcn/dcn_3_2_1_offset.h` and `dcn/dcn_3_2_1_sh_mask.h`, defines address-expansion helpers such as `SR` and `SRI`, initializes per-instance register tables, and constructs objects such as HUBP and DPP instances. In particular, `dcn321_hubp_create()` passes `hubp_regs`, `hubp_shift`, and `hubp_mask` into `hubp32_construct()`, while `dcn321_dpp_create()` passes `dpp_regs`, `tf_shift`, and `tf_mask` into `dpp32_construct()`.

The generated fields in this chunk are then consumed indirectly by common register helpers such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, and `REG_WAIT`. Typical runtime sequences are:

1. Resource construction builds per-instance HUBP/DPP register tables using `reg<REGISTER>` offsets and this chunk's masks/shifts.
2. Plane setup programs HUBP timing/prefetch/vblank/flip fields and DPP format-converter/scaler/color-management fields for each active pipe.
3. Cursor updates program `CURSOR0_3_*` and `CNVC_CUR*` fields for cursor memory, geometry, format, colors, and metadata.
4. Scaling and viewport updates program DSCL coefficient RAM, tap counts, mode, ratios, phase init, recout geometry, line-buffer settings, and autocal fields.
5. Color pipeline updates program CNVC pre-CSC/pre-degamma/pre-alpha, CM post-CSC, gamut remap, gamma LUT and RAMA/RAMB region fields.
6. Power-management paths force or release HUBPREQ, HUBPRET, DSCL, OBUF, cursor, and GAMCOR memory power states and poll matching status fields.
7. Diagnostics use DPP CRC, HUBPREQ status, HUBPRET read-line status, DSCL memory status, DMDATA status, and CM/DPP debug fields to verify programmed state.

## State And Persistence Behavior

The header itself is stateless. It allocates no memory, has no locks, performs no I/O, and persists nothing outside compiled constants.

The represented state is GPU display hardware register state. Programmed values remain in registers until overwritten by the driver or firmware, reset by a display-block reset, affected by power gating, lost across suspend/resume or ASIC reset, or reprogrammed during modeset/plane/cursor/color updates.

Persistent programmed state includes:

- HUBP request scheduling for vblank, flip, nominal delivery, prefetch, per-line delivery, cursor request offsets, and p-state force controls.
- HUBPRET crossbar, detile/read-line configuration, memory power control, and line-interrupt configuration.
- Cursor surface addresses, high addresses, dimensions, pitch/mode, enable, position, hot spot, stereo, destination offset, metadata buffer addresses, metadata size/repeat/update policy, and software metadata payload data.
- CNVC surface format, alpha handling, channel crossbar, color-key ranges, pre-dealpha/re-alpha, pre-CSC coefficients, pre-degamma mode, FP conversion bias/scale, and cursor formatter colors.
- DSCL scaling mode, coefficient RAM contents, tap configuration, luma/chroma scaling ratios and init phases, overscan, RECOUT/MPC sizes, line-buffer memory layout, autocal parameters, OBUF controls, and memory power settings.
- CM post-CSC/gamut-remap matrices, gamma-correction mode, LUT index/data/control, RAMA/RAMB region descriptors, HDR multiplier, dealpha behavior, and coefficient format.
- DPP clock/gating controls, soft resets, CRC capture controls, and host-read throttling.

Volatile readback state includes HUBPREQ status registers, HUBPRET read-line interrupt/status/value, cursor and DMDATA completion/status, current pre-CSC/post-CSC/gamut/gamma mode fields, memory power states for HUBPREQ/HUBPRET/DSCL/OBUF/GAMCOR/cursor memories, DPP CRC values, CRC pending/status-like bits, and line-buffer counters.

Some fields are side-effecting or access-sensitive even though the header does not encode access type. Examples include interrupt enable/status/ack fields in `HUBPRET3_HUBPRET_INTERRUPT`, reset fields in `DPP_TOP0_DPP_SOFT_RESET`, update/trigger bits such as `DMDATA_UPDATED` and `DMDATA_SW_UPDATED`, memory power force/disable fields, coefficient/LUT host-select/write controls, and CRC one-shot/pending controls. Consumers must use the existing register helper conventions and the hardware programming sequence for each block.

## Dependencies And Integration Points

Immediate dependency:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h`, which supplies matching register offsets and base indexes.

Primary local integration points:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c` includes this header and constructs DCN321 resource objects from the generated register, shift, and mask tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn32/dcn32_hubp.h` extends the HUBP mask/shift list with DCN32 fields such as `HUBPREQ0_UCLK_PSTATE_FORCE`; through instance expansion in DCN321 resource construction, the same field lists map onto the per-instance generated macros in this header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn31/dcn31_hubp.h` provides the common HUBP mask/shift list for prefetch, vblank, flip, cursor, HUBPRET read-line, and VM/request scheduling fields represented by the `HUBPREQ3`, `HUBPRET3`, and `CURSOR0_3` macros in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.h` defines DPP register and mask/shift lists for CNVC, CNVC cursor, DSCL, CM, DPP top, gamma, gamut, CSC, and memory-power fields represented by the `CNVC_CFG*`, `CNVC_CUR*`, `DSCL*`, `CM*`, and `DPP_TOP*` macros in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp.c`, `dcn10_dpp_dscl.c`, and `dcn10_dpp_cm.c` contain shared DPP programming routines that consume the generated DPP shift/mask tables through register helpers for format, cursor, scaler, and color-management programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn32/dcn32_hubp.c` and older HUBP implementations consume HUBP register tables for cursor, p-state, MALL, buffering, and initialization behavior.

The chunk also depends on generated consistency with nearby DCN 3.2.x and DCN 3.x headers. Many DPP/HUBP field names are intentionally shared across generations and instances, but small numeric differences can be generation-specific. Copying masks from `dcn_3_2_0_sh_mask.h` or other ASIC headers without checking the authoritative DCN 3.2.1 register database can silently misprogram hardware.

## Risks And Edge Cases

- The chunk starts mid-register: only the `DST_Y_PREFETCH` shift and `VRATIO_PREFETCH`/`DST_Y_PREFETCH` masks for `HUBPREQ3_PREFETCH_SETTINGS` are present here; earlier fields are in the previous chunk.
- The chunk ends mid gamma-table family at `CM1_CM_GAMCOR_RAMB_REGION_26_27`; later RAMB regions and any following CM1 fields are in the next chunk. File-level reconciliation must merge adjacent chunks before claiming complete CM1 coverage.
- Generated mask/shift errors compile cleanly. A wrong bit position in HUBP prefetch/vblank/flip scheduling can cause underflow, flicker, missed flips, p-state stalls, or bandwidth failures only under specific modes.
- Repeated instance prefixes are easy to mix. `DSCL0` and `DSCL1`, `CNVC_CFG0` and `CNVC_CFG1`, `CM0` and `CM1`, and `CURSOR0_3` must be matched to the correct register offsets for the pipe being programmed.
- Power-control fields are timing-sensitive. Incorrect HUBPREQ/HUBPRET/DSCL/OBUF/cursor/GAMCOR memory power masks can leave SRAM blocks forced on, forced off, or stuck waiting for a state transition.
- Cursor and DMDATA address/control fields touch GPU memory-backed surfaces and metadata. Wrong high-address, mode, pitch, size, repeat, update, or QoS masks can produce corrupt cursors, stale dynamic metadata, or memory fetch faults.
- DSCL coefficient RAM and tap/phase fields are visually sensitive. Incorrect masks can produce blurring, chroma misalignment, bad 4:2:0 behavior, incorrect viewport/recout geometry, or scaler underflow.
- Color-management tables are large and repetitive. Gamma RAMA/RAMB region start/end/slope/base/offset fields and LUT host-select/write fields are vulnerable to off-by-one, wrong-channel, or wrong-RAM-bank programming mistakes that may only appear in HDR, color-managed, or high-bit-depth modes.
- DPP soft-reset and CRC controls are side-effecting. Incorrect masks can reset the wrong sub-block, leave reset asserted, miss CRC one-shot completion, or read meaningless CRC values.
- High-bit masks such as `0xFFFF0000L`, `0x70000000L`, and similar values should remain in unsigned 32-bit register-helper paths; ad hoc signed arithmetic can create subtle packing bugs.

## Test Signals

Useful validation should combine build-time generated-header checks with hardware-visible DCN321 behavior:

- Build AMDGPU Display Core with DCN321 enabled and ensure all `dcn321_resource.c`, HUBP, DPP, DIO, IRQ, DMUB, clock-manager, GPIO, and resource users resolve the generated DCN 3.2.1 mask/shift names.
- Run generated-register consistency checks over the complete `dcn_3_2_1_sh_mask.h`: every field should have a paired shift/mask except at intentional chunk boundaries; masks should stay within 32 bits; fields in one register should not overlap unexpectedly; and every register should have a matching offset in `dcn_3_2_1_offset.h`.
- Exercise multi-plane modes across all available DCN321 pipes, especially pipes using DPP0/DPP1 and HUBP instance 3, while checking for underflow, missed flips, p-state-change failures, and visual corruption.
- Validate HUBP timing by testing page flips, vblank-heavy workloads, cursor movement, high refresh rates, memory-clock p-state changes, SubVP/MALL-related scenarios where applicable, suspend/resume, and hotplug modesets.
- Validate cursor paths with different cursor sizes, pitches, pixel formats, stereo settings, hot spots, negative/edge positions, dynamic metadata updates, and rapid enable/disable transitions.
- Validate DSCL paths with scaling up/down, 4:4:4 and 4:2:0 formats, chroma scaling, fractional ratios, viewport/recout changes, overscan, tap changes, coefficient RAM reloads, and line-buffer memory pressure.
- Validate CNVC and CM paths with RGB/YCbCr formats, alpha-plane use, pre/post CSC, gamut remap, SDR/HDR switching, degamma/gamma LUT programming, color-keying, dealpha/re-alpha, and high-bit-depth formats.
- Validate DPP diagnostics by enabling DPP CRC one-shot and continuous modes before and after color/scaler/cursor changes, comparing stable CRC values, and checking CRC pending/readback fields.
- Validate memory power behavior by toggling DSCL, OBUF, HUBPREQ, HUBPRET, cursor, and GAMCOR power controls through normal plane enable/disable, idle, blank/unblank, and suspend/resume paths, then polling matching state fields.

## Chunk-Specific Summary

Lines 10083-12636 define DCN 3.2.1 bit shifts and masks for the tail of HUBP request instance 3, HUBPRET instance 3, cursor instance 3, complete DPP0 format/scaler/color/top control blocks, and the beginning-to-mid section of DPP1 format/scaler/color blocks. The chunk is generated register ABI data, not executable logic. Correctness depends on exact numeric masks, pairing with `dcn_3_2_1_offset.h`, safe handling of side-effecting reset/interrupt/update/power fields, and validation across plane flips, cursor updates, scaler programming, color-management LUTs/matrices, DPP CRC diagnostics, and memory-power transitions.

### subset-b-002032: lines 12637-15195

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 12637-15195

## Chunk Scope

This chunk covers lines 12637-15195 of the generated AMD DCN 3.2.1 shift/mask header. It starts mid-register, with the final masks for `CM1_CM_GAMCOR_RAMB_REGION_26_27`, continues through DPP instance 1 top-level fields, full DPP instance 2 CNVC/DSCL/CM/DPP_TOP masks, full DPP instance 3 CNVC/DSCL/CM/DPP_TOP masks, and then enters MPC MPCC instance 0 plus most of MPCC instance 1. It ends mid-register at `MPCC1_MPCC_STATUS__MPCC_BUSY__SHIFT`; the remaining `MPCC1_MPCC_STATUS` masks are outside this chunk.

The file is a hardware register definition header, not executable logic. Every item in this range is a preprocessor macro that names either a bit shift (`__SHIFT`) or bit mask (`_MASK`) for a specific DCN 3.2.1 register field.

## Purpose

The chunk supplies the field-level layout used by the AMD display driver to program DCN 3.2.1 display pipeline blocks safely through generic register helper macros. It maps semantic field names such as `CM_GAMCOR_MODE`, `SCL_COEF_RAM_TAP_PAIR_IDX`, `DPP_CLOCK_ENABLE`, and `MPCC_GLOBAL_ALPHA` to their exact bit positions and masks inside MMIO registers.

The main hardware areas represented here are:

- DPP color management (`CM1`, `CM2`, `CM3`): post color space conversion, gamut remap, bias, gamma correction LUTs, RAMA/RAMB PWL region metadata, HDR multiplier, coefficient format, dealpha, and color-management memory power state.
- DPP top control (`DPP_TOP1`, `DPP_TOP2`, `DPP_TOP3`): DPP clock enable/gating, soft reset, CRC capture, and host read rate control.
- DPP conversion/configuration (`CNVC_CFG2`, `CNVC_CFG3`): surface pixel format, alpha plane enable, format expansion/conversion, bypass, clamping, color key ranges, 2-bit alpha LUT, pre-dealpha, pre-CSC matrices, coefficient format, pre-degamma, and pre-realpha.
- Cursor conversion (`CNVC_CUR2`, `CNVC_CUR3`): cursor enable/mode/ROM/pixel-alpha controls plus cursor colors and FP scale/bias.
- DPP scaler (`DSCL2`, `DSCL3`): coefficient RAM selection/data, scaling mode, tap counts, 2-tap controls, manual replicate controls, scale ratios, initial phases, black color, update/autocal, overscan, blanking, recout/MPC dimensions, line-buffer format/memory, vertical counters, DSCL memory power, and OBUF controls.
- MPC compositor (`MPCC0`, `MPCC1`): top/bottom input selection, OPP routing, blend/control modes, stereo/SM controls, update lock selection, top/bottom gains, movable CM routing, background color, output gamma memory power, and status.

## Important APIs, Types, and Macro Families

There are no C functions or structs in this chunk. The exported API surface is the macro naming contract consumed by register-list and field-list code.

The core macro pattern is:

- `<REGISTER>__<FIELD>__SHIFT`: integer bit offset for packing/unpacking a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the field in the 32-bit register value.

Representative field groups:

- `CM*_CM_POST_CSC_*` and `CM*_CM_GAMUT_REMAP_*` provide 16-bit matrix coefficient fields for active and "B" coefficient banks. `*_CONTROL` registers include requested mode and current mode fields, supporting double-buffered or latched color updates.
- `CM*_CM_GAMCOR_*` covers gamma-correction mode/select, LUT index/data/control, RAMA/RAMB start/end/offset controls, and region tables. Region-pair registers follow the repeated pattern `REGION_N_N+1` with low region fields at shifts `0x0`/`0xc` and high region fields at `0x10`/`0x1c`; masks are usually `0x000001FF`, `0x00007000`, `0x01FF0000`, and `0x70000000`.
- `DPP_TOP*_DPP_CONTROL` exposes clock enable, gate-disable, dynamic gate-disable, DSCL gate, DISPCLK gates, fine-grain clock-gating repeat disable, and test clock select.
- `DPP_TOP*_DPP_CRC_*` exposes CRC value fields and controls for enable, continuous mode, one-shot pending, 4:2:0 component selection, source selection, stereo/interlace/pixel-format/cursor-format selection, and a 16-bit CRC mask.
- `CNVC_CFG*_FORMAT_CONTROL` defines format expansion/conversion, alpha enable, bypass alignment, positive clamp controls, update pending, and RGB crossbar selection fields.
- `CNVC_CFG*_PRE_CSC_*` and `*_PRE_CSC_B_*` provide paired 16-bit pre-CSC coefficient fields, with `PRE_CSC_MODE` exposing requested/current mode.
- `DSCL*_SCL_COEF_RAM_TAP_SELECT` and `DSCL*_SCL_COEF_RAM_TAP_DATA` define the coefficient RAM programming interface used by scaler code: tap pair index, phase, filter type, even/odd tap coefficients, and enable bits.
- `DSCL*_SCL_MODE`, `DSCL*_SCL_TAP_CONTROL`, and scale/init registers define scaler mode, coefficient RAM bank selection/current state, chroma/alpha coefficient modes, horizontal/vertical tap counts, integer/fractional scale ratios, and initial phases for luma/chroma/bottom fields.
- `DSCL*_DSCL_MEM_PWR_CTRL`, `DSCL*_DSCL_MEM_PWR_STATUS`, `DSCL*_OBUF_MEM_PWR_CTRL`, and `CM*_CM_MEM_PWR_*` define memory power force/disable/mode/state bits for DSCL LUT/LB/OBUF and CM GAMCOR memories.
- `MPCC*_MPCC_CONTROL` defines MPCC blend mode, alpha blend mode, premultiplied alpha mode, active-overlap-only blending, background bpc, bottom gain mode, global alpha, and global gain.
- `MPCC*_MPCC_SM_CONTROL`, `MPCC*_MPCC_UPDATE_LOCK_SEL`, `MPCC*_MPCC_MEM_PWR_CTRL`, and `MPCC*_MPCC_STATUS` define stereo/multi-plane control, update-lock routing/status, OGAM memory power, and idle/busy/disabled status bits.

## Control Flow

This header has no runtime control flow. Its macros become part of control flow indirectly when included by DCN 3.2.1 resource initialization and block implementations:

- `dcn321_resource.c` includes both `dcn_3_2_1_offset.h` and this `dcn_3_2_1_sh_mask.h`, then uses macros such as `SRI`, `SRI_ARR`, and field-list expansions to build per-block register address, shift, and mask tables.
- DPP and MPC block headers define register-field lists that map generic driver fields to generated macros. For example, DPP DSCL code uses `SCL_COEF_RAM_*`, `DSCL_MEM_PWR_*`, and color-management field names through `REG_SET_*`, `REG_UPDATE`, and `REG_WAIT` helpers. MPC code uses the MPCC field masks for compositor programming.
- At runtime, display programming functions pass semantic field names to register helpers; the helpers combine the register address from the offset header with the shift and mask values from this header to pack, update, poll, or decode MMIO values.

Because the values are compile-time constants, the important "control flow" risk is whether the symbolic field referenced by a block implementation resolves to the correct generated field for the target ASIC instance.

## State and Persistence Behavior

The header itself owns no state and persists nothing. The state described by these masks lives in DCN display hardware registers and internal memories:

- Color-management registers persist requested/current CSC, gamut remap, GAMCOR LUT, RAMA/RAMB, HDR multiplier, bias, and format state until reprogrammed, reset, or power-gated by hardware.
- DSCL registers persist scaler coefficient RAM contents, scale ratios, initial phases, recout geometry, line-buffer partitioning, memory power state, and OBUF settings.
- MPCC registers persist compositor routing, blend modes, gains, background color, update-lock state, memory power state, and idle/busy/disabled status.
- Several fields are explicitly status/current fields (`*_CURRENT`, `*_UPDATE_PENDING`, `*_MEM_PWR_STATE`, `MPCC_IDLE`, `MPCC_BUSY`, `MPCC_DISABLED`). Driver code generally writes requested fields and polls or reads current/status fields to synchronize with hardware latching.

## Dependencies and Integration Points

The chunk depends on the matching generated offset header for register addresses:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h`

It is directly included from:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`

Important consumers and integration surfaces include:

- `display/dc/dpp/dcn30/dcn30_dpp.h` and `display/dc/dpp/dcn32/dcn32_dpp.h`, which define DPP register and field lists for CM, CNVC, DSCL, and DPP_TOP programming.
- `display/dc/dpp/dcn10/dcn10_dpp_dscl.c`, `display/dc/dpp/dcn30/*`, and `display/dc/dpp/dcn32/*`, which use generic register helpers for scaler coefficients, memory power sequencing, color management, and DPP state.
- `display/dc/mpc/dcn30/dcn30_mpc.h`, `display/dc/mpc/dcn32/dcn32_mpc.h`, and related MPC C files, which use MPCC masks for compositor routing, blending, locks, and status.
- The common register helper layer (`reg_helper.h` and related macros) that expects each register field to have a matching shift and mask macro with stable spelling.

The generated naming is instance-specific (`CNVC_CFG2`, `DSCL2`, `CM2`, `DPP_TOP2`, etc.) while block implementation code often uses generic field names. Resource macros bridge those layers by selecting the correct instance-specific macro for each hardware instance.

## Risks and Edge Cases

- Chunk boundary risk: lines 12637-12638 are only the tail of `CM1_CM_GAMCOR_RAMB_REGION_26_27`, and lines 15194-15195 are only the shift definitions for the beginning of `MPCC1_MPCC_STATUS`. Merge logic must combine adjacent chunks before making whole-register claims for those two registers.
- Generated constant drift: any incorrect shift or mask silently corrupts MMIO field updates. A wrong mask can clear neighboring fields, and a wrong shift can write the intended value into an unrelated control/status bit.
- Instance symmetry can hide copy errors. DPP2 and DPP3 blocks are highly repetitive; a single mismatched instance prefix or field spelling may compile if another macro exists but program the wrong register table entry.
- Current/status fields should not be treated as ordinary writable configuration fields. Fields such as `*_CURRENT`, `*_UPDATE_PENDING`, memory power state, and MPCC status bits are used for synchronization or diagnostics.
- Memory power controls are sequencing-sensitive. DSCL LUT/LB/OBUF, CM GAMCOR, and MPCC OGAM memory power fields interact with register waits and hardware state transitions; incorrect masks can cause hangs, timeouts, or loss of display processing state.
- GAMCOR region packing is dense. Region-pair registers pack two regions into one 32-bit word with non-contiguous offset and segment fields. Region table programming must preserve the untouched region half during partial updates.
- CRC and debug fields can affect validation paths. DPP CRC masks and source/format controls are used for hardware CRC capture; wrong values can make display validation or automated CRC tests fail even when visual output appears correct.
- MPCC blending fields directly affect composition semantics. Errors in `MPCC_ALPHA_BLND_MODE`, `MPCC_ALPHA_MULTIPLIED_MODE`, `MPCC_GLOBAL_ALPHA`, or gain masks can produce subtle overlay, plane, and HDR blending regressions.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing:

- Build test the AMD display driver for a DCN 3.2.1 target. Missing or misspelled shift/mask macros should fail compilation through resource field-list expansion.
- Exercise modeset and plane composition on DCN 3.2.1 hardware, especially multiple planes, cursor enable/format, alpha blending, global alpha/gain, and MPCC update-lock paths.
- Exercise color-management paths that program pre-CSC, post-CSC, gamut remap, bias, GAMCOR LUT/RAMA/RAMB region tables, HDR multiplier, dealpha, pre-dealpha, and pre-realpha.
- Exercise scaler paths with non-1:1 scaling, chroma scaling, alpha scaling, 2-tap modes, custom coefficient RAM programming, overscan, and recout/MPC sizing.
- Check memory power sequencing with display blank/unblank, suspend/resume, runtime power transitions, and repeated modesets; watch for `REG_WAIT` timeouts around DSCL/CM/MPCC memory power state fields.
- Use DPP CRC capture paths to verify `DPP_TOP*_DPP_CRC_*` field masks and source/format selections.
- Compare this header against the same register families in neighboring generated headers (`dcn_3_2_0_sh_mask.h`, `dcn_3_1_6_sh_mask.h`, or later DCN revisions) when diagnosing suspected generation drift. Repetition across revisions is a useful sanity signal but not a substitute for ASIC register spec validation.

## Summary for Merge Lane

This chunk is a dense generated macro segment for DCN 3.2.1 DPP color/conversion/scaler/top blocks and MPC MPCC blocks. It contributes no executable logic, but it is critical to all downstream register helper operations because it defines the exact bit layouts for color management, scaling, clock/reset/CRC, cursor conversion, memory power, and compositor blending/status registers. The merge lane should preserve the partial-register boundary notes for `CM1_CM_GAMCOR_RAMB_REGION_26_27` and `MPCC1_MPCC_STATUS` when synthesizing the full-file report.

### subset-b-002033: lines 15196-17712

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 15196-17712

## Scope

This chunk is a generated AMD DCN 3.2.1 register field mask/shift header segment. It covers 2,517 source lines and 2,082 preprocessor definitions: 1,040 `__SHIFT` macros and 1,042 `_MASK` macros. There are no C functions, structs, enums, or software storage objects in this range.

The chunk begins inside the tail of the `MPCC1_MPCC_STATUS` field group, then covers the complete `MPCC2`, `MPCC3`, MPC configuration, and `MPCC_OGAM0` through most of `MPCC_OGAM3` field groups. It ends at `MPCC_OGAM3_MPC_GAMUT_REMAP_C31_C32_B__MPCC_GAMUT_REMAP_C32_B__SHIFT`, before the corresponding mask definitions and the remaining `C33_C34_B` group that continue in the next chunk.

## Purpose

The purpose of this header slice is to provide compile-time bitfield metadata for DCN 3.2.1 display Multi-Plane Compositor hardware. Each register field has the generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the low bit position for inserting or extracting a value.
- `<REGISTER>__<FIELD>_MASK`, the positioned bit mask for the same field.

Driver code combines these constants with register addresses from `dcn_3_2_1_offset.h` and with the AMD display register helper macros. The macros are a hardware layout contract, not an algorithm. Correctness depends on the masks and shifts matching the silicon register database.

The hardware surfaces covered here are:

- MPCC blender instances `MPCC1` tail, `MPCC2`, and `MPCC3`: compositor plane selection, OPP binding, alpha/blend control, stereo or frame-alternate control, update locks, per-layer gain, background color, OGAM memory power control, and status bits.
- MPC global configuration: clock gating/test clock selection, soft resets for MPCC/SFR/SFT/MPC blocks, CRC control and readback, bypass background values, host read control, DPP pending status, vupdate lock sets, and DWB mux selection.
- MPCC OGAM instances `MPCC_OGAM0` through `MPCC_OGAM3`: output gamma/1D LUT mode, LUT host access, RAM A/RAM B piecewise-linear region programming, RGB offsets/start/end/slope/base fields, gamut remap coefficient format, gamut remap mode, and matrix coefficients for RAM A/B.

## Important APIs, Types, And Macros

The macro namespace is the only API in this chunk. Consumers do not call into this file; instead, DCN register tables expand these names into shift and mask structures used by register helper calls such as `REG_UPDATE`, `REG_SET`, `REG_GET`, and related field access macros.

Important register families in the chunk include:

- `MPCC2_MPCC_*` and `MPCC3_MPCC_*`: `TOP_SEL`, `BOT_SEL`, `OPP_ID`, `CONTROL`, `SM_CONTROL`, `UPDATE_LOCK_SEL`, `TOP_GAIN`, `BOT_GAIN_INSIDE`, `BOT_GAIN_OUTSIDE`, `MOVABLE_CM_LOCATION_CONTROL`, background RGB/YUV components, `MEM_PWR_CTRL`, and `STATUS`.
- `MPC_*`: `CLOCK_CONTROL`, `SOFT_RESET`, `CRC_CTRL`, `CRC_SEL_CONTROL`, CRC result registers, bypass background values, `HOST_READ_CONTROL`, `DPP_PENDING_STATUS`, `PENDING_STATUS_MISC`, four `*_VUPDATE_LOCK_SET*` groups, and `MPC_DWB0_MUX`.
- `MPCC_OGAM{0,1,2,3}_MPCC_OGAM_*`: OGAM mode/select/PWL-disable state, LUT index/data/control, RAM A and RAM B PWL region start/end/offset/region definitions, and RAM selection or current-state fields.
- `MPCC_OGAM{0,1,2,3}_MPCC_GAMUT_REMAP_*` and `MPCC_OGAM{0,1,2,3}_MPC_GAMUT_REMAP_*`: gamut remap coefficient format/mode and packed 16-bit matrix coefficient fields for coefficients `C11` through `C34` in A and B banks.

The dominant data shape is a 32-bit hardware register containing one or more packed fields. Examples include:

- 4-bit MPCC selectors and OPP IDs.
- 8-bit `MPCC_GLOBAL_ALPHA` and `MPCC_GLOBAL_GAIN` fields inside `MPCC*_MPCC_CONTROL`.
- 12-bit background color fields for R/Cr, G/Y, and B/Cb.
- 19-bit gain, LUT offset, region base, end, and offset fields in OGAM PWL programming.
- 16-bit packed gamut remap coefficients, with two coefficients per register.
- Current/readback fields such as `MPCC_OGAM_MODE_CURRENT`, `MPCC_OGAM_SELECT_CURRENT`, `MPCC_GAMUT_REMAP_MODE_CURRENT`, `MPCC_UPDATE_LOCKED_STATUS`, `MPC_DWB0_MUX_STATUS`, and `MPCC_OGAM_MEM_PWR_STATE`.

## Control Flow And Behavior

This chunk has no executable control flow. Runtime behavior is created by other AMD display code that includes the generated header, selects a register address from the matching offset header, and then performs hardware reads or writes through DC register helpers.

The implied hardware flows represented by these fields are:

1. MPCC composition setup: software selects top and bottom inputs, assigns an OPP, chooses blend mode and alpha mode, programs global alpha/gain, selects background bit depth, and applies per-plane top or bottom gain.
2. Update synchronization: MPCC update lock selection and vupdate lock set fields coordinate register updates with display timing so composition changes do not tear or partially apply.
3. MPC reset and diagnostics: MPC soft reset fields can reset MPCC, SFR, SFT, or whole-MPC blocks; CRC controls select windows and components for display-pipeline verification; pending status fields report DPP and MPC outstanding work.
4. Memory power sequencing: `MPCC*_MPCC_MEM_PWR_CTRL` exposes OGAM memory force/disable/low-power/state bits. In the DCN32 MPC code, `mpc32_mpc_init()` programs `MPCC_OGAM_MEM_LOW_PWR_MODE` across MPCC instances when MPC memory low power is enabled.
5. OGAM LUT programming: callers select RAM A or RAM B, set LUT index/data and write-color masks, program PWL region starts/end slopes/base/offsets for RGB channels, then switch or verify the active/current OGAM mode and selected RAM.
6. Gamut remap programming: the gamut remap coefficient format/mode fields and packed coefficient registers describe the per-MPCC color matrix state used by MPC gamut remap paths.
7. DWB routing: `MPC_DWB0_MUX` and status fields select and observe the display writeback mux source.

The header does not encode safe sequencing, register volatility, read/write permissions, or timeouts. Those requirements live in the MPC implementation and hardware programming guide.

## State And Persistence Behavior

The file stores no software state and has no persistence behavior by itself. It describes hardware register state in the GPU display block.

State classes represented in this chunk include:

- Latched compositor configuration: MPCC input selection, OPP binding, blend/alpha/gain/background color, DWB mux, and OGAM/gamut-remap mode.
- Double-buffered or banked color state: OGAM RAM A/RAM B LUT entries, PWL region programming, and gamut remap A/B coefficient banks.
- Synchronization state: update lock selection, locked-status readback, vupdate lock set values, and current-mode/current-select readback fields.
- Power state: OGAM memory force/disable/low-power configuration and memory power-state readback.
- Reset and transient control state: soft-reset bits and CRC control fields can have immediate hardware side effects.
- Diagnostic/readback state: CRC result registers, DPP pending status, pending-status misc fields, MPCC idle/busy/disabled status, and DWB mux status.

Because the macros only expose bit locations, they cannot distinguish read-only status fields from writable control fields. Consumers must avoid writing status/current fields unless the programming sequence explicitly requires it.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.2.1 register map set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h` supplies the matching register addresses and base indices. For example, the offset header defines registers such as `regMPCC2_MPCC_CONTROL`, `regMPC_SOFT_RESET`, `regMPCC_OGAM0_MPCC_OGAM_CONTROL`, and `regMPCC_OGAM0_MPC_GAMUT_REMAP_C33_C34_B`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h` supplies the field masks and shifts studied here.

Direct include evidence in this tree shows DCN 3.2.1 resource construction includes both generated headers from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`. The broader MPC field tables and functions are shared with DCN32-era code:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.h` maps many of these mask/shift names through `MPC_COMMON_MASK_SH_LIST_DCN32`, including MPCC memory power fields, OGAM controls, PWL region fields, gamut remap fields, and DWB mux fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn32/dcn32_mpc.c` uses the populated mask/shift tables for memory low-power initialization, LUT power control, post-1D LUT programming, gamut remap hooks, and MPC function dispatch.
- Older and newer MPC headers (`dcn30`, `dcn42`) show the same generated-mask contract reused across DCN generations, so this chunk is part of an established register-table pattern rather than a standalone API.

Although the repository path is under a local `ceph-client` mirror, this source has AMDGPU display hardware semantics. It has no Ceph filesystem protocol behavior and no distributed-filesystem persistence model.

## Risks And Edge Cases

- Mask/shift drift can silently program wrong hardware bits. A bad constant may still compile but break blending, color correction, update locking, writeback routing, or memory power behavior.
- Chunk boundaries are artificial. This chunk starts after the beginning of `MPCC1_MPCC_STATUS` and ends before the final `MPCC_OGAM3_MPC_GAMUT_REMAP_C31_C32_B` masks and subsequent group. The final per-file merge must reconcile adjacent chunks.
- Repetitive instance blocks are easy to miscompare. `MPCC2` and `MPCC3`, and `MPCC_OGAM0` through `MPCC_OGAM3`, intentionally share field layouts. A generated prefix or instance-offset error would look plausible in review but affect only one compositor path.
- Bank selection and current readback must be kept straight. OGAM and gamut remap expose A/B banks and current-mode/current-select fields; using the wrong bank can make a LUT or matrix update appear to succeed while inactive.
- LUT programming has packed, width-sensitive fields. Region offsets, segment counts, start/end slopes, bases, and RGB offsets occupy different widths. Open-coded arithmetic instead of shared field helpers risks truncation or overlap.
- Update-lock and vupdate-lock mistakes can cause visible tearing, partial composition updates, or stale state if writes land outside the intended blanking/update window.
- Reset fields are broad. `MPC_SOFT_RESET` contains per-MPCC, SFR, SFT, and whole-MPC reset bits; accidental writes could disrupt unrelated pipes.
- Power-management fields interact with hardware readiness. Forcing OGAM memory low power or disable state at the wrong time can corrupt LUT access or color processing, especially around suspend/resume, modeset, and runtime power transitions.
- CRC and status fields are diagnostic-sensitive. Incorrect decode can mislead validation by reporting the wrong component, pending state, or CRC result.

## Test Signals

Useful validation signals for code using this chunk include:

- Kernel build coverage for DCN 3.2.1 resource and MPC paths that include `dcn_3_2_1_offset.h` and `dcn_3_2_1_sh_mask.h`.
- Generated-register consistency checks comparing each `*_MASK`/`*__SHIFT` pair against the authoritative register database and against the matching offsets in `dcn_3_2_1_offset.h`.
- Static checks that repeated MPCC and OGAM instances have identical field widths where the hardware intends identical layouts, and that the MPCC/OGAM instance count matches the resource configuration.
- Modeset and plane-composition tests that exercise MPCC top/bottom selection, OPP routing, blend modes, global alpha/gain, background color, and update locks.
- Color-management tests that program OGAM PWL LUTs, switch RAM A/B banks, program gamut remap coefficients, and verify current-mode/current-select readbacks.
- Display CRC tests using MPC CRC control, selection, and result registers to confirm decoded results match expected frames.
- Display writeback tests that exercise `MPC_DWB0_MUX` selection and status readback.
- Runtime power-management, suspend/resume, and hotplug tests that check OGAM memory power fields and verify LUT state survives or is restored as expected.
- Debug traces or register dumps showing sane `MPCC_IDLE`, `MPCC_BUSY`, `MPCC_DISABLED`, pending-status, vupdate-lock, DWB mux status, and OGAM current-state values after programming.

## Research Notes

This is source-tree-aligned chunk research only. The final per-file document should merge this with neighboring chunks of `dcn_3_2_1_sh_mask.h` to describe the entire generated DCN 3.2.1 mask namespace, including the portion of `MPCC1_MPCC_STATUS` before line 15196 and the remainder of `MPCC_OGAM3` plus the following MPC MCM blocks after line 17712.

### subset-b-002034: lines 17713-20169

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 17713-20169

## Scope And Purpose

This chunk is part of AMD's generated DCN 3.2.1 register shift/mask header. It contains C preprocessor constants for hardware register bitfields, not executable driver logic. The constants are used with matching DCN 3.2.1 register-address headers and AMD display register helpers to pack and unpack fields in memory-mapped display hardware registers.

The requested range contains 2,079 `#define` lines: 1,041 `__SHIFT` macros and 1,038 `_MASK` macros. The imbalance is caused by chunk boundaries. The range starts in the tail of `MPCC_OGAM3` gamut-remap bank-B coefficient fields and ends inside `MPCC_MCM2_MPCC_MCM_1DLUT_RAMA_REGION_6_7` before that register's final shift and mask lines. It also contains 372 comment lines, including address-block boundaries for `dce_dc_mpc_mpcc_mcm0_dispdec`, `dce_dc_mpc_mpcc_mcm1_dispdec`, and `dce_dc_mpc_mpcc_mcm2_dispdec`.

The substantive hardware covered here is the multi-plane compositor color-management register layout for `MPCC_MCM0`, `MPCC_MCM1`, and the beginning of `MPCC_MCM2`. These blocks describe shaper LUTs, 3D LUTs, 1D LUTs, RAM A/B piecewise LUT regions, LUT read/write data ports, and memory power-control fields for per-MPCC color processing.

## Important Constants And Register Areas

The opening lines complete the preceding `MPCC_OGAM3` gamut-remap matrix bank B. The visible fields are `MPCC_OGAM3_MPC_GAMUT_REMAP_C31_C32_B` and `C33_C34_B`, each packing two 16-bit gamut-remap coefficients with low and high halfword masks. The earlier matrix coefficients and control fields belong to the previous chunk.

`MPCC_MCM0_*` is complete in this range. It covers:

- `MPCC_MCM_SHAPER_CONTROL`, offsets, scales, LUT index/data, and shaper LUT write-enable selection.
- `MPCC_MCM_SHAPER_RAMA_*` and `MPCC_MCM_SHAPER_RAMB_*`, including per-channel start/end controls and region descriptors for regions 0 through 33.
- `MPCC_MCM_3DLUT_MODE`, index, data, 30-bit data, read/write control, output normalization, and per-channel output offset/scale fields.
- `MPCC_MCM_1DLUT_CONTROL`, LUT index/data/control, 1D LUT RAM A/B start, slope, base, end, offset, and region descriptors.
- `MPCC_MCM_MEM_PWR_CTRL`, which controls and reports memory power state for shaper, 3D LUT, and 1D LUT memories.

`MPCC_MCM1_*` repeats the same complete programming surface for MPCC MCM instance 1. The field layout is structurally parallel to MCM0, which makes instance-to-instance diffing a useful validation signal for generated-header changes.

`MPCC_MCM2_*` begins the same repeated register family for instance 2. This chunk includes its shaper control and RAM A/B definitions, 3D LUT definitions, 1D LUT control and LUT data/control definitions, and the start of 1D LUT RAM A programming through the first three shift macros of `MPCC_MCM2_MPCC_MCM_1DLUT_RAMA_REGION_6_7`. The masks for that final region register and the rest of MCM2 continue after the requested range.

Common bitfield shapes in this chunk include:

- Two halfword fields packed into one 32-bit register, such as 3D LUT data entries or coefficient pairs, using shifts `0x0` and `0x10`.
- Region descriptor registers that pack two regions per register: LUT offset at bit 0 or bit 16, and segment count at bit 12 or bit 28, with masks `0x000001FF`, `0x00007000`, `0x01FF0000`, and `0x70000000`.
- Per-channel B/G/R start, slope, base, end, and offset registers for piecewise LUT programming.
- Mode/current-mode pairs such as shaper mode, 3D LUT mode, and 1D LUT mode, where programmed state and active hardware state may be separately readable.
- Memory power-control fields grouped by shaper, 3D LUT, and 1D LUT memories, with force, disable, low-power mode, and status fields.

## APIs, Types, And Functions

There are no functions, structs, enums, or inline helpers in this chunk. The API surface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT` gives the bit position of a field.
- `REGISTER__FIELD_MASK` gives the positioned field mask.
- `//REGISTER` and `// addressBlock: ...` comments group macros by hardware register and generated address block.

Consumers pair these masks and shifts with matching `reg...` offset macros from `dcn_3_2_1_offset.h`. For example, the corresponding offset header defines `regMPCC_MCM0_MPCC_MCM_MEM_PWR_CTRL` at base index 3, and similarly defines MCM1, MCM2, and MCM3 addresses. The shift/mask values in this file are only correct for the matching DCN 3.2.1 register map.

The larger AMD display stack typically consumes generated register metadata through register helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, register field lists, and ASIC-specific resource or block initialization tables. This chunk supplies the field layout for those helpers; it does not enforce valid enum values, sequencing, or read/write permissions.

## Control Flow And Runtime Behavior

This header has no local control flow. Runtime behavior occurs when display driver code writes or reads the described registers.

The implied control flows are color-pipeline programming flows. A caller selects LUT modes, writes LUT data through index/data ports, configures piecewise region descriptors, selects RAM A or RAM B banks, and then enables or observes the active color-management mode. Shaper LUTs and 1D LUTs use start/end/slope/base/offset fields and region tables to describe piecewise transfer functions. The 3D LUT path uses mode, size, RAM selection, 30-bit enable, data write-enable masks, read selection, output normalization, and output offset/scale fields.

The memory power-control registers introduce power-management flows. Driver code may force, disable, or observe low-power state for shaper, 3D LUT, and 1D LUT memories. These fields must be coordinated with LUT programming and active display timing because powering down a memory while its color path is selected can corrupt output or produce hardware-visible faults.

The region descriptor tables are mechanically regular, but the chunk boundary is not. The final visible MCM2 region register is incomplete in this research slice, so any whole-register validation of `MPCC_MCM2_MPCC_MCM_1DLUT_RAMA_REGION_6_7` must include the next source chunk.

## State And Persistence

The file itself stores no mutable state. It defines how software addresses state stored in DCN hardware registers and LUT RAMs.

Persistent hardware state represented in the chunk includes shaper offsets/scales, shaper LUT data, 3D LUT data and output normalization, 1D LUT data, RAM A/B start/end/slope/base/offset values, region segmentation tables, mode selections, active/current mode readbacks, and memory power state. These values can persist across frames and across parts of the display pipeline lifetime until reset or reprogrammed by modeset, color-management, power-management, or resume paths.

Double-buffered RAM A/B and mode/current fields are especially important. They imply that a driver can prepare one LUT bank while another is active, then switch or observe active state at a controlled point. The macros do not document the required synchronization point; that must come from higher-level DCN programming sequences.

## Dependencies And Integration Points

This generated header depends on the matching DCN 3.2.1 address header and the AMDGPU display register helper framework. Numeric masks are not portable across ASIC generations unless the corresponding hardware register database says the layouts match.

Important integration points include:

- DCN 3.2.1 MPC/MPCC color management, where these fields program shaper LUTs, 3D LUTs, 1D LUTs, and gamut/color transform state.
- Per-plane or per-compositor color pipelines that map logical MPCC instances to `MPCC_MCM0`, `MPCC_MCM1`, `MPCC_MCM2`, and later instances.
- Display color-management APIs that load 1D LUT, 3D LUT, shaper, degamma/gamma, or gamut-remap data.
- Runtime power-management code that coordinates memory power state with active color blocks.
- Generated register-list macros that rely on stable token naming across offset, shift, and mask headers.

The adjacent generated enum headers provide semantic values for many fields, including MCM 3D LUT size and 30-bit mode, gamma LUT mode, RAM selection, LUT segment counts, read color selection, LUT config mode, and memory power force/state values. This shift/mask file gives bit positions only; semantic interpretation comes from those enums and the caller's programming sequence.

## Risks And Edge Cases

Generated-header drift is the main risk. A wrong shift or mask compiles cleanly but can silently write the wrong register bits, causing bad color output, failed LUT updates, stale current-mode readback, or unsafe memory power transitions.

Chunk boundaries create local incompleteness. The start belongs to an earlier `MPCC_OGAM3` gamut-remap block, and the end cuts off `MPCC_MCM2_MPCC_MCM_1DLUT_RAMA_REGION_6_7` before its complete field set. Per-file reconciliation must merge neighboring chunks before making complete claims for either register family.

Repeated-instance consistency matters. MCM0 and MCM1 are complete and structurally parallel in this range; MCM2 begins the same pattern. A generator error that affects only one instance could produce output defects only on the corresponding MPCC path, so tests must cover multiple pipes and compositor instances.

RAM bank and write-enable fields are sequencing-sensitive. Writing LUT data to the wrong RAM bank, using the wrong color write mask, or switching modes before the table is fully programmed can create visible color discontinuities. Current-mode fields should not be assumed to update synchronously with programmed-mode writes unless the hardware sequence says so.

Memory power fields are side-effect-prone. Force, disable, low-power mode, and state fields for shaper, 3D LUT, and 1D LUT memories can affect retention and availability of color data. Callers should avoid ad hoc writes to these fields and should use established DCN power-management sequences.

Mask width and signedness are minor but real maintenance risks. Constants use `L` suffixes and full 32-bit masks such as `0xFFFF0000L` and `0x70000000L`; consumers should use unsigned register-width types and central field macros rather than open-coded arithmetic.

## Test And Validation Signals

Build validation should include all DCN 3.2.1 display objects that include `dcn_3_2_1_sh_mask.h` and use generated register lists. Missing or renamed macros usually surface at compile time; wrong numeric values usually require hardware or register-database validation.

Useful generated-data checks include:

- Compare the chunk against the authoritative DCN 3.2.1 register database.
- Diff repeated instances, especially `MPCC_MCM0` versus `MPCC_MCM1`, and continue into later chunks for `MPCC_MCM2` and `MPCC_MCM3`.
- Verify that each complete field has a non-overlapping mask and matching shift, allowing for the intentional incomplete first and last register groups.
- Cross-check adjacent ASIC generation headers only after accounting for intended generation-specific color-pipeline differences.

Runtime signals include successful modesets on DCN 3.2.1 hardware, correct color output with shaper LUT, 1D LUT, 3D LUT, and gamut/color transforms enabled, stable transitions between LUT RAM banks, correct readback of current mode and memory power state fields, and no visual artifacts across suspend/resume, hotplug, multi-monitor, and runtime power-management transitions.

## Research Notes

This is source-tree-aligned chunk research only. It intentionally writes only `Docs/researches/chunks/subset-b-002034_research.md`. Whole-file research for `dcn_3_2_1_sh_mask.h` must merge adjacent chunks to complete the preceding `MPCC_OGAM3` gamut-remap block and the following `MPCC_MCM2` register block.

### subset-b-002035: lines 20170-22676

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 20170-22676

## Scope

This chunk is a generated AMD DCN 3.2.1 register field mask segment. It covers 2,507 source lines with 2,093 `#define` entries: 1,045 `__SHIFT` constants, 1,048 `_MASK` constants, and 399 register-group comment markers. The source is not executable C; it is a compile-time bitfield schema consumed by AMD display register helper code.

The chunk starts in the middle of `MPCC_MCM2` 1D LUT region definitions, then covers complete or near-complete blocks for:

- `dce_dc_mpc_mpcc_mcm3_dispdec`: `MPCC_MCM3` shaper LUT, 3D LUT, 1D LUT, and LUT memory power-control fields.
- `dce_dc_mpc_mpc_ocsc_dispdec`: `MPC_OUT0` through `MPC_OUT3` mux, denormalization, clamp, and output CSC fields.
- `dce_dc_opp_abm0_dispdec`, `dce_dc_opp_abm1_dispdec`, and the beginning of `dce_dc_opp_abm2_dispdec`: backlight PWM and Adaptive Backlight Management fields.

The file-level include guard and license live outside this span. The corresponding address macros are in `dcn_3_2_1_offset.h`; this chunk only supplies shifts and masks.

## Purpose

The purpose of the chunk is to let DCN 3.2.1 driver code program hardware register fields by name instead of hard-coding bit positions. Each field uses the generated convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit index.
- `<REGISTER>__<FIELD>_MASK` gives the full register mask for the field.

The MPCC/MCM portions describe color-management storage and control in an MPC compositor path. They define shaper RAM A/B region layouts, 3D LUT indexing/data/control fields, 1D LUT RAM A/B segment definitions, output offsets, write enables, current mode readbacks, and memory power state controls. These fields are the low-level contract behind high-level color features such as shaper curves, 3D LUTs, gamut remap, 1D transfer functions, and memory power gating for those tables.

The MPC OCSC portion describes post-composition output routing and color conversion. It covers four MPC outputs, each with mux selection, rate/flow control flags, denormalization clamp ranges for R/Cr, G/Y, and B/Cb, CSC mode/current-mode fields, and two coefficient banks (`A` and `B`) for 3x4 output color-space conversion coefficients.

The ABM portions describe backlight and image-statistics state for up to three ABM instances. ABM fields cover PWM levels, automatic ambient/backlight update control, frame-sampled update cadence, grouped register locks, ACE thresholds and slope/offset curves, histogram and luma-statistic controls, histogram result readbacks, and master locks.

## Important APIs, Types, and Data Shapes

There are no functions, structs, enums, or inline helpers in this chunk. The exposed API is the macro namespace used by the AMD display register helper layer. DCN code commonly feeds these macros through register-list and mask/shift-list generators such as `SRII`, `SRI_ARR`, and `SF`, then stores the resulting values in hardware block register tables.

Important data shapes in this span include:

- `MPCC_MCM*_MPCC_MCM_SHAPER_*`: shaper mode/current-mode, per-channel offsets and scales, 8-bit LUT index, 24-bit LUT data, write-mask/write-select fields, and RAM A/B piecewise-region metadata.
- `MPCC_MCM*_MPCC_MCM_3DLUT_*`: 3D LUT mode, 12-bit index, 30-bit data path, read/write done and select flags, output normalization, and signed-looking output offsets packed as 19-bit fields.
- `MPCC_MCM*_MPCC_MCM_1DLUT_*`: 1D LUT mode/current-mode, selection, read/write control, direct LUT index/data access, RAM A/B start/end/base/slope/offset values, and paired region entries.
- LUT region packing: most `*_REGION_N_M` registers pack two regions. Each region usually has a 9-bit LUT offset and a 3-bit segment count at shifts `0x0`/`0xc` for the first region and `0x10`/`0x1c` for the second.
- `MPCC_MCM*_MPCC_MCM_MEM_PWR_CTRL`: force/disable/low-power controls and readback state for shaper, 3D LUT, and 1D LUT memories.
- `MPC_OUT*_MUX`: output selection, overflow error, error acknowledgment, rate-control disable/control, flow-control mode, and an 11-bit flow-control count.
- `MPC_OUT*_DENORM_*`: 12-bit min/max clamp fields and a 3-bit denorm mode.
- `MPC_OUT*_CSC_*`: output CSC mode/current mode plus packed 16-bit coefficient pairs for banks `A` and `B`.
- `ABM*_BL1_PWM_*`: 17-bit ambient/user/target/current/final/minimum duty-level fields, ABM enable bits, ambient-level enable, auto-update controls, and 16-bit step size.
- `ABM*_DC_ABM1_*`: ABM enable/bypass, input CSC coefficient selection, ACE slope/offset and threshold registers, histogram/luma statistic controls, sample-rate controls, shift flags and indexes, 24 histogram result words, and lock/readback/update-pending fields.

The `L` suffix on masks makes these long integer constants. Consumers should still use the driver’s unsigned register helpers rather than ad hoc signed arithmetic.

## Control Flow and Behavior

This header has no runtime control flow. Runtime behavior is created when DCN 3.2.1 resource construction includes `dcn/dcn_3_2_1_sh_mask.h` and combines these field definitions with address registers from `dcn_3_2_1_offset.h`. In this tree, `dcn321_resource.c` includes both headers and `dcn32_resource.h` defines broad register-list macros for the MCM, MPC OCSC, and ABM families represented here.

The implied hardware flows are:

- MCM color programming: higher-level color code selects shaper, 3D LUT, and 1D LUT modes, writes LUT entries through index/data registers, configures RAM A/B regions and start/end slopes, then relies on mode-current/read-write status fields to confirm the active programming path.
- MCM memory power management: power-control fields can force, disable, or place shaper/3D LUT/1D LUT memories into low-power modes, with corresponding state bits for readback.
- MPC output routing: mux fields select the composed stream feeding each MPC output. Rate and flow-control fields expose pacing or overflow/error recovery behavior for those output paths.
- Output color conversion: OCSC mode and coefficient-bank fields define post-composition color-space conversion. Banked coefficients allow programming one bank while another may be active, depending on the surrounding hardware sequence.
- Denormalization and clamping: denorm mode plus per-channel min/max clamps constrain output component ranges before the data leaves the MPC output path.
- ABM/backlight update: PWM level fields represent ambient input, user level, target/current ABM level, final duty cycle, and minimum duty cycle. Control bits decide whether ABM and ambient level are used and whether current level/final duty are automatically updated.
- ABM statistics and ACE processing: luma-sum/min/max/pixel-count registers and histogram bins feed adaptive contrast/backlight decisions. ACE slope/offset/threshold fields configure the image-dependent transform.
- Frame-synchronized updates: ABM grouped locks, HGLS locks, update-at-frame-start, frame-start display select, readback-double-buffer enable, and update-pending bits describe synchronization around frame boundaries.

Because this chunk only declares field positions, it does not enforce ordering. Correct sequencing, polling, locks, timeouts, and value ranges are responsibilities of the display block implementations and hardware programming guide.

## State and Persistence

No software state is allocated or persisted by this file. The persistent state represented by the macros lives in GPU display hardware registers after driver writes.

State classes represented in the chunk include:

- Latched color configuration: shaper/3D LUT/1D LUT modes, LUT entries, region segment metadata, offsets, scales, output normalization, OCSC modes, CSC coefficients, denorm modes, and clamp bounds.
- Double-buffered or frame-synchronized state: MCM mode-current fields, ABM grouped lock fields, readback double-buffer enables, update-at-frame-start selectors, and update-pending bits.
- Hardware memory power state: shaper/3D LUT/1D LUT memory force, disable, low-power mode, and state readbacks.
- Backlight control state: user, ambient, target, current, minimum, and final PWM duty values plus ABM enable and auto-update controls.
- Image statistics readback state: luma sums, min/max luma, filtered min/max luma, pixel counts, min/max pixel-value counters, histogram bin shifts/indexes, and 24 histogram result registers per complete ABM instance in this span.
- Error/status/clear state: MPC rate-control overflow and acknowledgement fields, ABM missed-frame flags and clear bits, HGLS read-in-progress and missed-frame clear bits.

Some fields likely have read-only or write-one-to-clear semantics despite appearing as plain masks. Examples include `*_CURRENT`, `*_DONE`, `*_UPDATE_PENDING`, `*_MISSED_FRAME_CLEAR`, read-in-progress, and lock-related fields. The header itself does not encode access permissions.

## Dependencies and Integration Points

This chunk depends on the generated AMD register header set:

- `dcn_3_2_1_offset.h` supplies register addresses and base indices.
- `dcn_3_2_1_sh_mask.h` supplies shifts and masks.
- `reg_helper.h` and display block register-list macros combine address, shift, and mask data into typed register tables used by DCN hardware blocks.

Key integration points in this tree include:

- `display/dc/resource/dcn321/dcn321_resource.c`, which includes this exact DCN 3.2.1 shift/mask header during DCN321 resource construction.
- `display/dc/resource/dcn32/dcn32_resource.h`, whose MCM register-list macros enumerate the `MPCC_MCM_SHAPER`, `MPCC_MCM_3DLUT`, `MPCC_MCM_1DLUT`, and `MPCC_MCM_MEM_PWR_CTRL` register families covered here.
- MPC block code and headers such as `display/dc/mpc/dcn32/dcn32_mpc.h`, which expose `MPC_OUT0_MUX` field definitions for output mux/rate/flow control.
- Color-management paths in `display/dc/core/dc.c`, `display/dc/core/dc_hw_sequencer.c`, and `display/amdgpu_dm/amdgpu_dm_color.c`, which refer to shaper, 3D LUT, 1D LUT, OCSC, and CTM placement at a higher abstraction level.
- DMUB ABM code such as `display/dc/dce/dmub_abm_lcd.c`, which programs ABM sample-rate and backlight-related registers through the shared register helper mechanism.

The chunk is source-tree-aligned with a DCN321 generated header, but many register families are shared with DCN32/DCN35-style blocks. Adjacent chunks are needed to complete `MPCC_MCM2` before line 20170 and `ABM2` after line 22676.

## Risks

- Generated-header drift: if a mask or shift disagrees with the silicon register specification, callers will compile cleanly while programming the wrong bits.
- Chunk-boundary incompleteness: this span starts mid-register for `MPCC_MCM2_MPCC_MCM_1DLUT_RAMA_REGION_6_7` and ends at `ABM2_DC_ABM1_LS_SUM_OF_LUMA`. Per-file synthesis must merge adjacent chunks before making claims about whole families.
- Bank and instance confusion: MCM RAM A/B, CSC banks A/B, MPC output indices 0-3, MPCC MCM instances 2/3, and ABM instances 0-2 are all encoded textually. Copy/paste mistakes can program the wrong instance or inactive bank.
- LUT write sequencing hazards: index/data/write-enable/read-write-control fields usually require precise write order and completion polling. A bad sequence can leave partially loaded shaper, 3D LUT, or 1D LUT tables.
- Region packing hazards: paired region registers share one 32-bit value. Updating one region without preserving the other can corrupt neighboring segment metadata.
- Power-control hazards: MCM memory power force/disable/low-power fields can make LUT memories unavailable. These fields should not be toggled blindly while color programming is active.
- Frame-synchronization hazards: ABM locks, update-pending bits, update-at-frame-start, and missed-frame clears imply timing-sensitive access. Ignoring these fields can produce stale readbacks, missed updates, or visible brightness jumps.
- Read/write semantic ambiguity: the generated masks do not identify read-only, write-one-to-clear, self-clearing, or reserved behavior. Callers must rely on block-specific programming code and hardware documentation.
- Width and signedness issues: many color coefficients and offsets use 16-bit, 18/19-bit, 24-bit, 30-bit, or full 32-bit masks. Manual shifts can mishandle sign extension or truncation; central field macros should be preferred.
- ABM user-visible impact: incorrect PWM minimum/final/target/current duty fields can produce brightness flicker, backlight clipping, slow convergence, or inaccessible panel brightness behavior.

## Test Signals

Useful validation signals for consumers of this chunk include:

- Build coverage for DCN321 display resources and any DCN32 block code that uses the shared MCM, MPC, and ABM register-list macros.
- Static consistency checks that every field has a non-overlapping mask/shift pair and that paired region fields preserve the expected `0x0`, `0xc`, `0x10`, and `0x1c` packing.
- Color pipeline tests that load shaper curves, 3D LUTs, 1D LUTs, and OCSC matrices, then verify mode-current/readback fields and visual output.
- HDR, CTM, gamma, degamma, color-space conversion, and gamut-remap tests that exercise the shaper/3D LUT/1D LUT/OCSC programming path.
- Register readback after MCM memory power transitions to confirm LUT memories are available before writes and return expected power-state values afterward.
- Multi-output display tests that exercise `MPC_OUT0` through `MPC_OUT3` mux and flow-control fields under clone, extended desktop, and hotplug scenarios.
- ABM/backlight tests covering user brightness changes, ambient-light input, automatic duty-cycle calculation, suspend/resume, panel power sequencing, and rapid frame updates.
- Histogram/luma-statistics diagnostics checking nonzero luma sum, plausible min/max values, pixel counts, histogram bins, missed-frame flags, and update-pending behavior.
- Stress tests around frame-boundary updates to catch stuck locks, missed-frame flags, or incomplete double-buffer updates.

## Research Notes

This is chunk-level research only. The final per-file document should reconcile this with neighboring chunks because the MPCC MCM2 1D LUT family begins before this span and the ABM2 family continues after it. Direct source searches show this exact header included by DCN321 resource construction, while many individual field names are consumed through macro-generation patterns rather than direct hand-written references.

### subset-b-002036: lines 22677-25260

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 22677-25260

## Scope

This chunk is a generated AMD DCN 3.2.1 register shift/mask header segment. It contains C preprocessor constants only: `__SHIFT` macros give field low-bit positions and `_MASK` macros give positioned masks for hardware register fields. There are no C functions, structs, enums, branches, loops, allocations, locks, or direct MMIO operations in this range.

The slice covers 2,584 source lines with 2,114 `#define` entries, including 1,061 shift definitions and 1,070 mask definitions, grouped by 374 register comments. It starts inside the `ABM2_DC_ABM1_LS_SUM_OF_LUMA` register group: the register comment is at line 22676, just before this chunk. It ends inside `OTG1_OTG_V_TOTAL_CONTROL`: the shift definitions are in this chunk, while that register's masks begin at line 25261 and continue after the chunk. Merge-time reconciliation should treat both boundary register groups as partial.

## Purpose

This header is part of the generated register ABI for the AMDGPU Display Core. Matching offset headers define register addresses; this `*_sh_mask.h` file defines the bit layout used by register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, and related DC register table initialization code. Runtime display code includes the header through the DCN 3.2.1 resource path, notably `display/dc/resource/dcn321/dcn321_resource.c`, which includes both `dcn_3_2_1_offset.h` and `dcn_3_2_1_sh_mask.h`.

The hardware surface in this chunk spans the output/display-tail side of DCN:

- The tail of `dce_dc_opp_abm2_dispdec` and the full `dce_dc_opp_abm3_dispdec` block for ambient backlight management, luma statistics, histogram results, adaptive contrast enhancement, PWM level calculation, and ABM register locks.
- Repeated OPP pipe instances 0-3 for display pattern generation (`DPG`), output formatter (`FMT`), output processor buffer (`OPPBUF`), pipe clock/bypass control, and OPP pipe CRC.
- DSC remap (`DSCRM0..3`) forwarding configuration and OPP top-level clock/ABM selection.
- ODM/OPTC input blocks 0-3 for output data merger input reset, underflow status/interrupts, segment source selection, DSC format/bytes-per-pixel, segment widths, input clocks, and memory selection.
- The complete `OTG0` timing generator field set in this slice and the start of `OTG1`, covering mode timing, triggers, status, interrupts, CRC, static-screen detection, global sync lock, double-buffer/update locking, dynamic refresh rate, DSC start position, and pipe update status.

## Important APIs And Data Shapes

The only API exposed here is the macro namespace. Each complete field normally appears as a pair:

- `<REGISTER>__<FIELD>__SHIFT`, the least-significant bit index for the field.
- `<REGISTER>__<FIELD>_MASK`, the field mask in register position.

The comments are generated structure:

- `// addressBlock: ...` marks hardware address-block transitions such as `dce_dc_opp_fmt0_dispdec`, `dce_dc_optc_odm0_dispdec`, and `dce_dc_optc_otg0_dispdec`.
- `//<REGISTER>` introduces the following field definitions until the next register comment.

Important definition families in this range include:

- ABM2/ABM3 luma and histogram state: `*_LS_SUM_OF_LUMA`, `*_LS_MIN_MAX_LUMA`, `*_LS_FILTERED_MIN_MAX_LUMA`, `*_LS_PIXEL_COUNT`, min/max pixel threshold/count registers, `*_HG_SAMPLE_RATE`, `*_LS_SAMPLE_RATE`, histogram bin shift/index registers, and `*_HG_RESULT_1..24`.
- ABM/PWM and ACE controls: `ABM3_BL1_PWM_*` ambient/user/target/current/final/minimum duty-cycle fields, `ABM3_BL1_PWM_ABM_CNTL`, sample-rate and group-2 lock fields, `ABM3_DC_ABM1_CNTL`, IPCSC coefficient selection, ACE offset/slope and threshold fields, ACE missed-frame status, HGLS read-progress status, HGLS locks, and `ABM*_BL_MASTER_LOCK`.
- DPG 0-3: `DPG_CONTROL`, ramp control, active dimensions, two-color RGB/YCbCr values, offset segment, and double-buffer-pending status for test-pattern or generated-display output.
- FMT 0-3: component clamp lower/upper bounds, dynamic expansion, pixel encoding and subsampling fields, truncation/spatial/temporal dithering controls, random seed and offset values, clamp format, side-by-side stereo active width, 4:2:0 memory power controls, and 4:2:2 edge handling.
- OPPBUF and OPP pipe 0-3: active width, display segmentation, overlap pixels, pixel repetition, 3D spacing/dummy data, padded segment pixels, pipe clock enable/on status, and digital bypass.
- OPP pipe CRC 0-3: CRC enable/continuous/one-shot controls, stereo and interlace selection, pixel/source selection, CRC masks, and A/R/G/B/C result fields.
- DSCRM/OPP top: DSC forward-map controls per instance, OPP display-clock gate/test-clock/ABM-clock status, and backlight PWM selection.
- ODM 0-3: soft reset, underflow interrupt/status/clear/current flags, double-buffer pending, number of input/output segments, segment source selectors, data format, DSC mode, DSC bytes per pixel, segment and DSC slice width, input clock gating/enabled/on status, memory selection/status, and spare registers.
- OTG0: horizontal/vertical totals and blank/sync windows, variable vertical-total controls and status, nominal vsync status, trigger A/B controls, force-count-now, flow control, stereo/interlace controls and status, pixel/status readback, counters, snapshot controls, interrupt controls, update locks, double-buffer controls, master enable, vertical interrupts 0-2, CRC windows/results/masks, static-screen detection, 3D structure, GSL timing, master-update mode/locks, vstartup/vupdate/vready timing, global sync status, GSL windows, global control, DRR interrupt/range/change/window/control fields, M-constant DTO, DSC start position, and pipe-update status.
- OTG1 beginning: H total, H blank/sync, H sync control, H timing divider, V total/min/max/mid, and the shift side of V total control.

## Control Flow And State Behavior

This header has no executable control flow. Runtime behavior is implied by callers that combine these masks with register offsets and perform MMIO reads/writes.

Typical display flows represented by the fields are:

1. Panel/backlight code programs ABM and PWM fields, then reads luma statistics, histogram bins, min/max counts, filtered values, update-pending bits, missed-frame status, and lock status.
2. OPP construction and stream enablement code configures generated patterns, formatter clamp/dither/subsampling, OPP buffer segmentation, pipe clock/bypass state, and pipe CRC capture.
3. DSC/ODM setup code routes compressed or uncompressed data through DSCRM and ODM/OPTC input blocks, selecting segments, slice widths, bytes per pixel, memory configuration, and input clocks while checking underflow and double-buffer status.
4. OTG code programs timing totals, sync/blank ranges, master enable, interlace/stereo behavior, trigger and flow-control sources, vstartup/vupdate/vready windows, update locks, vertical interrupts, DRR windows, GSL, CRC windows, and DSC start position.
5. Diagnostics and validation paths read OTG counters/status, snapshot registers, CRC results, static-screen events, underflow state, ABM statistics, OPP pipe CRC values, and pipe update pending flags.

The state represented here is hardware register state:

- Persistent programmed state includes PWM and ABM control values, ACE threshold and slope values, DPG pattern parameters, FMT clamp/dither/pixel-format controls, OPP buffer segmentation, pipe clock/bypass bits, ODM source/format/width/memory settings, OTG timing, update-lock windows, interrupt masks/types, CRC windows, DRR settings, GSL parameters, and DSC start positions.
- Volatile readback includes luma/histogram statistics, filtered min/max luma, ABM/HGLS read/update/missed-frame bits, DPG/OPP/FMT/ODM double-buffer pending flags, OPP pipe CRC results, underflow status/current bits, clock-on status, OTG current master-enable state, interlace/stereo status, HV/frame/VF counters, snapshot data, interrupt occurrence/status bits, CRC data, static-screen state, global sync status, DRR events, and pipe update pending bits.
- Sequencing-sensitive fields include register-lock/master-lock bits, readback-double-buffer selects, update-at-frame-start controls, underflow clear bits, OTG master/update locks, double-buffer enable/update-pending controls, interrupt clear/ack fields, one-shot CRC and trigger clear bits, DRR timing updates, GSL/master-update locking, and soft reset/clock-enable fields.

## Dependencies And Integration Points

The definitions depend on exact agreement with the DCN 3.2.1 register specification and with `dcn_3_2_1_offset.h`. A missing macro usually fails the build; an incorrect shift or mask can compile cleanly while causing wrong hardware programming.

Primary integration points are:

- `display/dc/resource/dcn321/dcn321_resource.c`, which includes this header and builds DCN 3.2.1 resource objects from register-offset and shift/mask tables.
- ABM and panel-control paths, including DMUB ABM integration, that consume ABM/PWM/luma/statistics fields for backlight and adaptive brightness behavior.
- OPP and formatter code that uses DPG, FMT, OPPBUF, OPP pipe, and OPP pipe CRC field tables when creating output pixel processor instances and validating output color/CRC behavior.
- OPTC/OTG timing-generator code, especially DCN 3.2 OPTC definitions that use `OTG0_*` masks for timing programming, update locks, vstartup/vupdate/vready, global controls, DRR, and CRC.
- ODM and DSC routing code that uses OPTC input and DSCRM fields for multi-segment output, DSC mode, bytes-per-pixel, slice width, underflow handling, and input clock/memory selection.
- IRQ services and diagnostics that depend on OTG vertical interrupt fields, OTG status/clear bits, ODM underflow interrupts, OPP pipe CRC results, and static-screen or DRR event bits.

## Risks And Maintenance Notes

- This is generated hardware ABI. Manual edits to shifts or masks are high risk because register helper code will still compile while targeting the wrong bits.
- Repeated instance families are copy/paste-sensitive: ABM2/ABM3, DPG/FMT/OPPBUF/OPP pipe/CRC instances 0-3, DSCRM0-3, ODM0-3, and OTG0/OTG1 must stay aligned with the register generator and address headers.
- Many fields are packed into adjacent bit ranges. A one-bit mask error can corrupt neighboring controls such as interrupt clear/mask bits, update locks, pixel-format selection, dithering controls, DRR state, or underflow handling.
- Clear/ack/reset fields are side-effect-prone. Misusing underflow clear, interrupt ack/clear, trigger clear, force-count clear, CRC one-shot pending, soft reset, or update-lock fields can produce intermittent display glitches or stuck status.
- Timing fields are user-visible. Bad OTG total/blank/sync, vstartup/vupdate/vready, DRR, GSL, or DSC start-position masks can surface as black screens, flicker, missed vblank, tearing, bad variable-refresh behavior, or DSC timing faults.
- Color-path fields are visually sensitive. Incorrect FMT clamp, pixel encoding, subsampling, dithering, truncation, or dynamic-expansion masks may cause color shifts, banding, chroma ordering errors, or CRC mismatches.
- Boundary completeness matters. This chunk starts after the `ABM2_DC_ABM1_LS_SUM_OF_LUMA` comment and ends before the `OTG1_OTG_V_TOTAL_CONTROL` masks, so final file-level documentation should merge adjacent chunks before claiming complete register-group coverage.

## Test Signals

Useful validation signals include:

- Build AMDGPU Display Core with DCN 3.2.1 enabled and confirm DCN321 resource, OPP, OPTC, ODM, ABM, IRQ, and DSC paths compile with this generated header and the matching offset header.
- Run generated-register consistency checks: each complete register group should have paired shifts and masks, masks should not overlap unexpectedly, repeated instance families should be numerically consistent, and boundary partial groups should reconcile with neighboring chunks.
- Compare all ABM, DPG/FMT/OPP, DSCRM, ODM, and OTG field values against the authoritative DCN 3.2.1 register source, prioritizing lock/update-pending bits, clear/ack bits, timing fields, CRC fields, underflow state, and packed pixel-format/dither fields.
- Exercise display modes across common and edge timings, including interlace where supported, stereo/3D paths where available, DSC, ODM/multi-segment output, 4:2:0/4:2:2 formats, high bit depth, and variable refresh/DRR.
- Validate panel brightness and ABM behavior by sampling luma statistics, histogram results, PWM target/current/final duty-cycle fields, HGLS read progress, missed-frame flags, and lock/update-pending behavior.
- Capture OPP and OTG CRCs before and after enabling formatter dither/truncation, chroma subsampling, generated patterns, DSC, and stereo/interlace modes; unexpected CRC drift points to format or timing mask issues.
- Monitor ODM underflow status/interrupts, OTG vertical interrupts, vblank timing, pipe update pending, global sync status, and DRR events during mode set, page flip, cursor update, suspend/resume, hotplug, and VRR transitions.
- Use register dumps around mode programming and updates to confirm that read-modify-write helpers affect only intended fields, especially locks, interrupt clears, update windows, timing totals, and clock/power gate controls.

## Chunk-Specific Summary

Lines 22677-25260 define generated bitfield masks and shifts for the tail of ABM2, the full ABM3 block, repeated OPP output pipe and formatter blocks 0-3, DSC remap and OPP top controls, ODM/OPTC input blocks 0-3, the complete OTG0 timing/control/status surface in this slice, and the beginning of OTG1 timing fields. The content is data-only register ABI. Correctness depends on exact generated values, repeated-instance consistency, careful handling of partial boundary registers, and hardware validation through ABM, formatting, CRC, ODM/DSC, timing, interrupt, DRR, and update-lock flows.

### subset-b-002037: lines 25261-27725

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 25261-27725

## Purpose

This chunk is generated AMD DCN 3.2.1 register field metadata. It contains no executable C logic; it publishes `#define` constants for bit shifts and bit masks used to access fields inside display-controller MMIO registers. Consumers combine these constants with register-offset macros from the matching DCN 3.2.1 offset header and then use `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and related helpers to program the display hardware.

The requested range starts at the mask half of `OTG1_OTG_V_TOTAL_CONTROL`, so the first eight `OTG1` shift definitions live in the previous chunk. It then covers the remainder of the `dce_dc_optc_otg1_dispdec` timing-generator field map, all of the `dce_dc_optc_otg2_dispdec` and `dce_dc_optc_otg3_dispdec` field maps, the `dce_dc_optc_optc_misc_dispdec` miscellaneous OPTC/GSL/ODM masks, and the beginning of the `dce_dc_dio_hpd0_dispdec` hotplug-detect block. The range ends on the `HPD0_DC_HPD_CONTROL` comment before that register's field definitions, so HPD0 control fields are owned by the next chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, storage objects, includes, locking primitives, allocation paths, or runtime APIs in this slice. Its interface is the generated preprocessor namespace:

- `<register>__<field>__SHIFT`: the field's least significant bit position.
- `<register>__<field>_MASK`: the field's unshifted bit mask in the 32-bit MMIO register.

Major macro families in this chunk:

- `OTG1_*`, `OTG2_*`, and `OTG3_*`: output timing generator fields for vertical timing, horizontal timing, triggers, flow control, master enable, interlace, stereo/3D, pixel readback, status counters, snapshots, interrupts, update locks, double buffering, CRC windows and data, static screen detection, global sync lock, update windows, dynamic refresh rate, DSC start position, and pipe update status.
- `GSL_SOURCE_SELECT`: genlock/swaplock source selection fields for three GSL ready groups plus the timing-sync source.
- `OPTC_CLOCK_CONTROL`: OPTC display-clock gating/status/test-clock and fine-grain clock-gating override fields.
- `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL3`, and `ODM_MEM_PWR_STATUS`: output data merger memory power force/disable/mode/status fields for memory banks 0 through 7.
- `OPTC_MISC_SPARE_REGISTER`: an 8-bit spare field.
- `HPD0_DC_HPD_INT_STATUS` and `HPD0_DC_HPD_INT_CONTROL`: HPD0 interrupt/sense/RX status, toggle filter timer values, interrupt ack, polarity, enable, RX ack, and RX enable fields.

The repeated OTG instance layout is intentionally near-identical across `OTG1`, `OTG2`, and `OTG3`. For each instance, masks such as `OTG*_OTG_H_TOTAL__OTG_H_TOTAL_MASK`, `OTG*_OTG_V_TOTAL_CONTROL__...`, `OTG*_OTG_INTERRUPT_CONTROL__...`, and `OTG*_OTG_PIPE_UPDATE_STATUS__...` are selected by token-pasting macros in DCN resource code.

## Control Flow

This header has no runtime control flow. The effective runtime flow is supplied by the display driver:

1. DCN 3.2.1 resource code includes the DCN 3.2.1 register offset and shift/mask headers.
2. Register-list macros instantiate per-pipe timing-generator tables. In DCN 3.2 era code, `OPTC_COMMON_REG_LIST_DCN3_2_RI(inst)` includes OTG registers such as `OTG_VSTARTUP_PARAM`, `OTG_V_TOTAL_CONTROL`, `OTG_TRIGA_CNTL`, `OTG_CRC_CNTL`, `OTG_GSL_CONTROL`, `OTG_DRR_CONTROL`, and `OTG_PIPE_UPDATE_STATUS`, and also includes `GSL_SOURCE_SELECT`.
3. The shift/mask macros from this file are placed in per-block field tables through `FN(reg, field)` style helpers.
4. Runtime modeset, page-flip, IRQ, link, HPD, and power-management code uses those tables to read, update, poll, clear, or acknowledge individual hardware fields.

The macros themselves do not encode ordering. Consumers must still sequence timing programming, double-buffer locks, vupdate/vstartup/vready windows, GSL synchronization, DRR changes, CRC capture, interrupt ack/clear, HPD enablement, and clock/power transitions correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes fields in MMIO-backed GPU state.

The OTG fields represent hardware state for:

- Mode timing: active totals, blanking ranges, sync start/end/polarity, divide mode, interlace, stereo, and 3D structure.
- Timing generator enablement and routing: master enable, output mux, current enable state, flow control, request mode, DSC start position, and manual trigger paths.
- Atomic update machinery: update locks, double-buffer controls, master update modes, global update/lock fields, vstartup/vupdate/vready positions, keepout windows, and pipe update pending bits.
- Interrupt and event surfaces: vtotal min events, nominal vsync, snapshot, force count, force vsync next line, external trigger A/B, GSL vsync gap, vertical interrupts 0 through 2, DRR timing/update/reach events, and interrupt mask/type/clear/ack fields.
- Diagnostics: live H/V status, frame/VF/HV counters, nominal vertical position, pixel readback, CRC windows/data/signature masks, static-screen status, clock-on status, global sync lock status, and spare registers.
- DRR support: min/max/mid vtotal, event active period, vtotal reach ranges, change limits, trigger windows, average-frame reporting, and last vtotal used by DRR.

The OPTC misc fields represent GSL source selection, OPTC clock-gating status/control, and ODM memory power policy/status. The HPD0 fields represent hotplug sense, delayed sense, HPD interrupt status, HPD RX interrupt status, filter timer readback, interrupt polarity, enables, and acknowledgements.

Persistence is hardware-defined. Configuration fields usually remain in the display block until a modeset, stream teardown, power gating, suspend/resume, or ASIC reset changes them. Status, counter, clear, ack, interrupt, and pending fields may be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive. This header only gives bit positions; it does not identify access type or side effects.

## Dependencies

This chunk depends on the AMD generated DCN 3.2.1 register database. It must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h`, which provides the corresponding `mm...` register offsets and base indexes.
- DCN 3.2 resource macros such as `SRI_ARR(...)`, `SR_ARR(...)`, and `OPTC_COMMON_REG_LIST_DCN3_2_RI(inst)` in `drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.h`.
- Link encoder HPD register-list macros such as `HPD_REG_LIST_RI(id)`, which instantiate `DC_HPD_CONTROL`, `DC_HPD_INT_STATUS`, and `DC_HPD_TOGGLE_FILT_CNTL` register tables.
- Generic AMD display register helpers that use field tables built from these macros, including `generic_reg_update_ex()`, `REG_UPDATE`, `REG_SET`, and `REG_GET` patterns.
- IRQ source metadata under `drivers/gpu/drm/amd/include/ivsrcid/dcn/`, which maps many OTG interrupt fields to display interrupt source IDs and contexts.

Because these are preprocessor constants, the compiler only checks that names exist and expressions are syntactically valid. It cannot prove that a mask matches hardware.

## Integration Points

The central integration point is the DCN timing generator, often exposed in DC code as an OPTC or timing-generator object. Resource construction builds per-instance register and field tables for OTG pipes. Modeset and flip sequencing then uses those tables to program timing, enable or disable the CRTC, manage double-buffered updates, set DRR ranges, wait for update-pending bits, configure CRC capture, and collect status.

GSL fields integrate with global sync lock and swaplock/genlock sequencing. Hardware sequencing includes a `TG_SET_GSL_SOURCE_SELECT` step, and resource tables include `GSL_SOURCE_SELECT` so the driver can choose which OTG feeds timing synchronization and ready-source groups.

The ODM memory power fields integrate with display power management. They expose force/disable/status controls for per-bank output data merger memory, plus unassigned and vblank power modes. Incorrect field definitions here can affect power savings, wake latency, or display stability around blanking and pipe reconfiguration.

The HPD0 interrupt fields integrate with link encoder and connector-detection code. DCN link encoder helpers use the HPD register table to enable or disable HPD, and IRQ handling uses HPD status/control fields to detect cable plug/unplug events and DP AUX HPD RX interrupts.

This chunk is also tied to adjacent chunks. The first line is part of `OTG1_OTG_V_TOTAL_CONTROL`; its shift macros are immediately before the requested range. The final line is a register comment for `HPD0_DC_HPD_CONTROL`; the actual HPD0 control masks follow after the requested range.

## Risks And Edge Cases

- Field drift is the main risk. A wrong shift or mask can compile cleanly while causing the driver to write the wrong bits in a live MMIO register.
- Repeated OTG instances are copy-sensitive. `OTG1`, `OTG2`, and `OTG3` are structurally similar, but a single instance-specific typo may only fail on one pipe or one multi-display topology.
- The range starts inside a register definition. Any review of `OTG1_OTG_V_TOTAL_CONTROL` needs the preceding lines for the matching `__SHIFT` values.
- The range ends before `HPD0_DC_HPD_CONTROL` fields. This chunk can describe HPD0 status/control interrupt masks, but not the HPD0 enable/control-field layout that follows.
- Many fields are side-effect-sensitive. Interrupt `ACK`, `CLEAR`, and mask fields, update locks, double-buffer pending bits, DRR event controls, force-count controls, and HPD RX interrupt fields may require specific read/write ordering.
- Timing fields are mode-critical. Incorrect H/V totals, blanking, sync, vstartup, vupdate, vready, DSC start, or keepout masks can produce blank displays, underflow, flicker, missed page flips, or modes that work only at some refresh rates.
- DRR and VRR behavior depends on multiple fields across `V_TOTAL_*`, DRR range/change/trigger windows, and event status. Partial or mismatched definitions can cause stutter, missed vtotal transitions, or stuck interrupts.
- CRC and pixel readback fields are diagnostic but still user-visible through debug and test paths. Bad masks can create false CRC failures or hide real scanout corruption.
- Clock and memory power fields can be harmful if written while blocks are gated, reset, or actively scanning out. The header does not encode safe access windows.

## Test Signals

Useful validation signals combine generated-header checks with display hardware behavior:

- Build AMDGPU/DC with DCN 3.2/3.2.1 support enabled. Missing or renamed macros should fail during resource, timing-generator, HPD, and IRQ table construction.
- Mechanically compare every `__SHIFT` and `_MASK` in lines 25261-27725 against AMD's authoritative DCN 3.2.1 register database and against the matching `dcn_3_2_1_offset.h` register names.
- Check repeated instance consistency for `OTG1`, `OTG2`, and `OTG3`: equivalent registers should expose equivalent field names, shifts, and masks unless the hardware database intentionally differs.
- Exercise modesets and page flips on enough displays to use OTG1, OTG2, and OTG3, including enable/disable cycles, suspend/resume, fast updates, cursor updates, and pipe update pending waits.
- Test timing-sensitive modes: high refresh, low refresh, interlace if supported, stereo/3D if supported, DSC-enabled modes, ODM combinations, and DRR/VRR transitions.
- Validate IRQ behavior for vertical interrupts, vupdate/vstartup/vready events, DRR timing events, nominal vsync, snapshot/force count, GSL vsync gap, and HPD0 plug/unplug plus HPD RX interrupts.
- Use CRC capture and pixel-readback diagnostics to confirm CRC window programming, data readout, and signature masks behave as expected on each covered OTG instance.
- Watch kernel logs and display diagnostics for underflow, missed flips, stuck update locks, stuck interrupt status bits, HPD storms, AUX/HPD RX failures, link retraining loops, clock-gating issues, and resume failures.

## Cross-Chunk Notes

Previous chunks own the beginning of `dce_dc_optc_otg1_dispdec`, including the offset-aligned first half of `OTG1_OTG_V_TOTAL_CONTROL`. Later chunks own `HPD0_DC_HPD_CONTROL` fields and the rest of the HPD/DIO register-field namespace. The final per-file research document should merge those adjacent chunks before making complete claims about all OTG1 fields, all HPD0 fields, or the complete `dcn_3_2_1_sh_mask.h` hardware map.

### subset-b-002038: lines 27726-30144

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 27726-30144

## Scope

This chunk is a generated AMD DCN 3.2.1 register field shift/mask header slice. It covers the tail of HPD0, HPD1-HPD4 hot-plug-detect blocks, all visible DP0 DisplayPort and DIG0 digital encoder field definitions, and the beginning of DP1 DisplayPort field definitions through `DP1_DP_ALPM_CNTL__DP_LINK_TRAINING_SWITCH_BETWEEN_VIDEO_MASK`. It defines C preprocessor constants only; there are no functions, structs, storage objects, or executable control flow in this chunk.

## Purpose

The constants provide the bit positions and bit masks used by AMD display driver register helpers to read, write, and compose DCN 3.2.1 hardware registers. Each hardware field appears as a pair of macros:

- `<REGISTER>__<FIELD>__SHIFT`, giving the least significant bit index.
- `<REGISTER>__<FIELD>_MASK`, giving the already-positioned register bit mask.

These macros are consumed indirectly by DCN 3.2.1 resource and hardware object constructors, especially `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`, which includes both `dcn_3_2_1_offset.h` and this `dcn_3_2_1_sh_mask.h`. The resource code expands register-list macros into per-block register address tables plus shift/mask tables, then passes those tables into link encoder, stream encoder, VPG, AFMT, audio, and related constructors.

## Important Macro Families

- HPD registers: `HPD0_DC_HPD_CONTROL`, `HPD0_DC_HPD_FAST_TRAIN_CNTL`, `HPD0_DC_HPD_TOGGLE_FILT_CNTL`, and full `HPD1` through `HPD4` sets. The full HPD instances include interrupt status, interrupt control, connection/RX timers, enable bits, fast-training connect delays, AUX transmit enable, and toggle filter delays. These support connector hotplug sense, delayed sense, RX interrupt acknowledgment, HPD interrupt polarity, and filtering/debounce behavior.
- DP0 link core: `DP0_DP_LINK_CNTL`, `DP0_DP_PIXEL_FORMAT`, `DP0_DP_CONFIG`, `DP0_DP_VID_STREAM_CNTL`, `DP0_DP_STEER_FIFO`, `DP0_DP_VID_TIMING`, `DP0_DP_VID_N`, `DP0_DP_VID_M`, `DP0_DP_LINK_FRAMING_CNTL`, and `DP0_DP_VID_INTERRUPT_CNTL`. These describe link training completion/status, lane count, video-stream enable/defer/status bits, transfer-unit and FIFO overflow reporting, video M/N generation, VBID/enhanced framing, and stream-disable interrupt control.
- DP0 DPHY and training: `DP0_DP_DPHY_CNTL`, `DP0_DP_DPHY_TRAINING_PATTERN_SEL`, `DP0_DP_DPHY_SYM0..2`, `DP0_DP_DPHY_8B10B_CNTL`, `DP0_DP_DPHY_PRBS_CNTL`, `DP0_DP_DPHY_SCRAM_CNTL`, CRC control/result/MST status registers, `DP0_DP_DPHY_FAST_TRAINING`, `DP0_DP_DPHY_FAST_TRAINING_STATUS`, `DP0_DP_DPHY_BS_SR_SWAP_CNTL`, and `DP0_DP_DPHY_HBR2_PATTERN_CONTROL`. These are the low-level DP PHY fields for FEC, scrambler, training patterns, test symbols, PRBS, CRC capture, MST CRC slot selection, fast-training state and completion interrupt/ack paths.
- DP0 secondary data packet and audio: `DP0_DP_SEC_CNTL`, `DP0_DP_SEC_CNTL1..7`, framing registers, audio `N`/`M` and readback registers, timestamp mode, packet control, metadata transmission, and GSP enable/send/active/deadline fields. These define the sideband/secondary packet machinery for audio stream packets, audio timestamping, generic secondary packets, ISRC, metadata/PPS-like packet sends, double-buffer disable bits, and send-active/send-in-idle status.
- DP0 MST/MSO: `DP0_DP_MSE_RATE_CNTL`, `DP0_DP_MSE_RATE_UPDATE`, `DP0_DP_MSE_SAT0..2`, `DP0_DP_MSE_SAT*_STATUS`, `DP0_DP_MSE_SAT_UPDATE`, `DP0_DP_MSE_LINK_TIMING`, `DP0_DP_MSE_MISC_CNTL`, `DP0_DP_MSO_CNTL`, and `DP0_DP_MSO_CNTL1`. These fields drive Multi-Stream Transport allocation, source IDs, encryption flags, slot counts, rate X/Y, SAT update pending/status, MSO secondary packet enables, and link timing fields.
- DP0 panel power behavior: `DP0_DP_ALPM_CNTL` and `DP0_DP_AUXLESS_ALPM_CNTL1..5` describe link PHY sleep/standby sends, pending bits, line/pattern counts, AUX-less ALPM enable/control, detected-sleep/standby states, IRQ mask/status/clear fields, and frame/line coordinates for wake events.
- DIG0 digital encoder: `DIG0_DIG_FE_CNTL`, output CRC control/result, test and random pattern registers, FIFO controls, metadata packet control, HDMI control/status/audio/ACR/VBI/infoframe/generic packet controls, HDMI double-buffer controls, AFMT, back-end enable/control, TMDS control-character/sync/DC-balance/generator controls, DIG version, and forced disable. These fields back HDMI/TMDS/DVI-style output setup, CRC/test-pattern diagnostics, packet generator scheduling, deep color/scrambling, AVMUTE/status/error handling, generic packet immediate sends, and digital front-end/back-end routing.
- DP1 beginning: the DP1 register set mirrors DP0 for link, video, DPHY, secondary packets, MST/MSO, double-buffering, metadata, and ALPM until the chunk ends at the early masks for `DP1_DP_ALPM_CNTL`. The visible DP1 definitions are structurally aligned with DP0 and are instance-specific for the second DIO DP block.

## Control Flow and Data Flow

This header has no runtime branches or calls. Its behavior is compile-time token substitution into AMD display register-helper call sites. The data flow is:

1. `dcn321_resource.c` includes this shift/mask header and the matching offset header.
2. Register-list initialization macros in resource and hardware-object code concatenate register and field names into constants such as `DP0_DP_DPHY_CNTL__DPHY_FEC_EN_MASK` or `DIG0_HDMI_CONTROL__HDMI_DEEP_COLOR_DEPTH__SHIFT`.
3. Constructors populate hardware-object tables, for example `link_enc_hpd_regs`, `link_enc_regs`, `stream_enc_regs`, `vpg_regs`, `afmt_regs`, and their shift/mask companions.
4. Runtime helpers such as `REG_GET`, `REG_SET`, `REG_SET_2`, `generic_reg_get`, and related AMD display macros use the precomputed shift/mask values to preserve unrelated bits while extracting or updating a field in memory-mapped DCN registers.

Important integration examples visible from nearby code include `dcn321_link_encoder_construct`, which receives link, AUX, HPD, shift, and mask tables; `dcn321_stream_encoder_create`, which passes stream encoder registers plus VPG/AFMT instances into `dcn32_dio_stream_encoder_construct`; and HPD setup paths that use the HPD masks through the link encoder function table for enable, disable, state read, and filter programming.

## State and Persistence Behavior

The file itself has no mutable state and persists no data. It encodes hardware state layout: using a macro against a live register may change or observe persistent hardware state in the GPU display engine. Relevant state surfaces in this chunk include HPD interrupt latch/ack bits, DP stream enable/status, FIFO and TU overflow flags, DPHY CRC result-valid/result bytes, fast-training complete/ack bits, MST allocation table status, secondary packet send-pending/deadline-missed flags, double-buffer pending/taken/lock/disable bits, HDMI packet/status/error bits, and ALPM sleep/standby pending/status/interrupt bits.

Because many fields are status or acknowledge fields, read/write semantics come from the hardware register specification and caller code, not from this header. A mask typo can therefore cause durable hardware misprogramming even though the header is syntactically passive.

## Dependencies and Integration Points

- Depends on the matching DCN 3.2.1 offset header for register addresses; the shift/mask macros are meaningful only when paired with the same-generation register offsets.
- Depends on AMD display register helper conventions in `reg_helper.h` and hardware object code that expects field names to be available through token concatenation.
- Integrates with DCN 3.2.1 resource construction in `display/dc/resource/dcn321/dcn321_resource.c`, which includes this header and constructs resource-specific register/shift/mask tables.
- Integrates with DIO link encoder code, including HPD operations, DP output enable, MST allocation, FEC control, DIO PHY mux, and DP fast-training support through `dcn321_dio_link_encoder.c` and inherited `dcn10/dcn20/dcn31/dcn32` helpers.
- Integrates with stream encoder, AFMT, VPG, audio, HDMI packet generation, secondary data packets, and TMDS output programming because DIG0/DP0/DP1 masks feed the corresponding constructor tables.
- Generated constants are intentionally duplicated by instance (`DP0`, `DP1`, `DIG0`, `HPD1` etc.) rather than parameterized at runtime. This matches the hardware-register naming model and allows the macro layer to build static per-instance tables.

## Risks

- Offset/header mismatch: using this `dcn_3_2_1_sh_mask.h` with another ASIC generation's offset header can silently write the wrong fields.
- Bitfield drift: generated values for fields such as `DPHY_FEC_EN`, `DP_SEC_GSP*_SEND`, `HDMI_DEEP_COLOR_DEPTH`, `DP_MSE_SAT_SLOT_COUNT*`, or HPD ack/status bits are hardware ABI. One incorrect shift or mask can break link training, hotplug detection, MST bandwidth allocation, HDMI packet scheduling, or ALPM wake behavior.
- Acknowledge and status fields are easy to misuse because names like `_ACK`, `_CLEAR`, `_PENDING`, and `_STATUS` appear side by side. The header does not encode write-one-to-clear or read-only semantics.
- Repeated instance blocks invite copy/paste or generator errors. DP1 mostly mirrors DP0, and HPD1-HPD4 mirror one another; a single instance-specific anomaly must be intentional and checked against hardware source data.
- The chunk begins in the middle of HPD0 definitions and ends in the middle of `DP1_DP_ALPM_CNTL`, so final per-file reconciliation must combine adjacent chunks before making whole-file claims about completeness.

## Test Signals

- Compile coverage is the first signal: any renamed/missing field macro breaks builds in DCN 3.2.1 resource or DIO object initialization because token concatenation cannot resolve the constants.
- Register-table construction review: ensure `dcn321_resource.c` still compiles when it includes `dcn_3_2_1_offset.h` and this header, and that HPD, link encoder, stream encoder, AFMT, VPG, and audio constructor tables receive the expected shift/mask structures.
- Runtime display smoke tests should include HPD plug/unplug detection, DP link training, DP MST stream allocation, HDMI output with deep color/scrambling as applicable, audio/secondary packet transmission, panel self-refresh or fast-training paths, and ALPM entry/exit on supported panels.
- Diagnostic tests can exercise output CRC and DPHY CRC fields, FIFO/TU overflow flags, HDMI packet error status, generic packet send-pending bits, and fast-training completion/ack fields to catch field-position mistakes.
- Cross-generation diffing against adjacent generated headers such as DCN 3.2.0/3.5.1 is useful for detecting accidental generator regressions, but differences must be validated against DCN 3.2.1 register specifications rather than assumed wrong.

## Chunk Boundaries

This report is intentionally limited to lines 27726-30144. It does not summarize the entire source file. The merge/reconciliation lane should combine this with neighboring chunk reports for the final per-file research document.

### subset-b-002039: lines 30145-32540

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 30145-32540

## Scope And Purpose

This chunk is a generated DCN 3.2.1 shift/mask register definition slice for AMD display hardware. It covers the tail of the `DP1` DisplayPort block, the complete `DIG1` digital front/back-end block, the complete `DP2` DisplayPort block, the complete `DIG2` block, and the beginning of `DP3`. The file is not executable code; it is the hardware register field contract used by the AMD DC driver to build per-ASIC register tables and perform register read-modify-write operations through the display core's `REG_*` helper macros.

The chunk's main purpose is to publish exact bit positions (`__SHIFT`) and bit masks (`_MASK`) for display link programming on DCN 3.2.1. These fields control HDMI/TMDS packet generation, DP stream enablement, DP secondary data packets, DSC PPS generic stream packets, MST allocation registers, DP PHY training/test state, active link power management, double-buffer status, CRC/test-pattern plumbing, and encoder enable/disable state.

## Register Groups Covered

The slice begins in the existing `dce_dc_dio_dp1_dispdec` address block. It includes `DP1_DP_GSP8_CNTL` through `DP1_DP_GSP11_CNTL`, `DP1_DP_GSP_EN_DB_STATUS`, and `DP1_DP_AUXLESS_ALPM_CNTL1` through `DP1_DP_AUXLESS_ALPM_CNTL5`. These define generic stream packet controls for SDP/GSP slots 8-11, pending/active/deadline status bits, line-number fields, and auxless ALPM wake/sleep timing and interrupt fields.

The `dce_dc_dio_dig1_dispdec` block defines the first digital encoder instance. It includes `DIG1_DIG_FE_CNTL`, output CRC, clock/test/random pattern registers, FIFO control/status-related fields, HDMI metadata/infoframe/generic packet controls, ACR/audio control and readback fields, AFMT audio clock fields, digital back-end enable and HPD/source selection fields, TMDS control character and DC-balance fields, and DIG version/force-disable bits.

The `dce_dc_dio_dp2_dispdec` block is the largest part of this chunk. It defines DP2 stream/link fields: link status and embedded-panel mode, pixel format and MSA colorimetry, lane count, video stream enable/status/defer controls, steering FIFO overflow/TU size, M/N timing generation, framing, interrupt controls, DPHY controls and test symbols, 8b/10b and scrambler controls, PHY CRC controls and status, fast training, secondary packet enable/send/line fields, DP audio M/N/readback/timestamp fields, MST/MSE rate and slot allocation tables, BS/SR swap and HBR2 pattern controls, MSA timing parameters, MSO and DSC controls, metadata transmission, ALPM, GSP8-11 controls, double-buffer status, and auxless ALPM.

The `dce_dc_dio_dig2_dispdec` block mirrors the DIG1 fields for the second digital encoder instance. The masks are instance-prefixed (`DIG2_*`) but otherwise model the same front-end, HDMI packet, AFMT, back-end, TMDS, version, and force-disable fields.

The chunk ends at the beginning of `dce_dc_dio_dp3_dispdec`, covering DP3 through the opening `DP3_DP_VID_INTERRUPT_CNTL` fields. This partial DP3 block includes base link, format, lane, stream, FIFO, MSA, DPHY internal, M/N timing, framing, HBR2 eye-pattern, VBID, and video-disable interrupt fields. Later DP3 registers continue in the next chunk.

## APIs, Types, And Macros

There are no C functions or structs defined in this header slice. The important API surface is the generated macro naming convention:

- `<REG>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `<REG>__<FIELD>_MASK` gives the already-positioned bit mask.
- The register instance prefix (`DP1`, `DP2`, `DP3`, `DIG1`, `DIG2`) binds the field layout to an address-block instance.

These constants are consumed indirectly by display-core register table macros. `dcn321_resource.c` includes both `dcn_3_2_1_offset.h` and this `dcn_3_2_1_sh_mask.h`, then uses helper macros such as `SRI(...)` to map register addresses by instance and macros such as `SE_SF(...)` / `LE_SF(...)` to copy shift/mask pairs into stream-encoder and link-encoder mask tables.

Relevant consumers in the same source tree include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`, which selects the DCN 3.2.1 offset and shift/mask headers for resource construction.
- `drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_stream_encoder.h`, whose stream encoder mask lists reference fields present here such as `DP_SEC_GSP*`, `DP_GSP11_CNTL`, `DP_VID_STREAM_CNTL`, `DP_STEER_FIFO`, `DP_VID_TIMING`, `HDMI_*`, `AFMT_CNTL`, and generic HDMI packet controls.
- `drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_stream_encoder.c`, which uses `REG_UPDATE`, `REG_UPDATE_2`, `REG_SET_*`, and `REG_GET` against these logical fields to program DP info packets, DSC PPS packets, AFMT clock state, SDP line numbers, and stream enablement.
- `drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_link_encoder.h`, whose link encoder register list references DP link, DPHY, PRBS, scrambler, training pattern, MST allocation, and TMDS DC balancer registers covered by the DP2/DIG blocks.

## Control Flow

This header contributes data to runtime control flow rather than executing itself. During DCN 3.2.1 resource initialization, the driver includes this header and builds register, shift, and mask tables for each stream/link encoder instance. Later, common DCN stream and link encoder functions use logical field names through `REG_UPDATE`, `REG_SET`, `REG_GET`, and `REG_WAIT`. Those helpers combine the selected register address from the offset table with the field shift/mask from this header and issue MMIO read-modify-write or read operations.

For HDMI/DIG paths, the control flow commonly starts from stream configuration and info-packet update code. The encoder code programs `DIG*_DIG_FE_CNTL` source, color/TMDS settings, `HDMI_CONTROL` scrambling/deep-color state, ACR/audio packet fields, generic HDMI packet send/continuous/line controls, and `HDMI_DB_CONTROL` double-buffer behavior. DIG FIFO and output CRC/test-pattern fields provide diagnostic and validation paths.

For DP paths, link and stream setup code programs `DP*_DP_LINK_CNTL`, `DP*_DP_CONFIG`, `DP*_DP_PIXEL_FORMAT`, `DP*_DP_VID_STREAM_CNTL`, M/N timing fields, MSA fields, and DPHY training/scrambler/FEC/test fields. Secondary data packet control flows use `DP_SEC_CNTL*` and `DP_GSP*_CNTL` fields to enable specific packet slots, request sends, poll pending/active/deadline state, and schedule packets on particular lines. DSC PPS setup in `dcn30_dio_stream_encoder.c` is a concrete example: it sets `DP_SEC_GSP11_PPS`, updates generic info packet payloads, writes `DP_SEC_GSP11_LINE_NUM`, enables `DP_SEC_GSP11_ENABLE`, and enables `DP_SEC_STREAM_ENABLE`.

For MST/MSO paths, the DP2 fields in this chunk define MSE rate and slot-allocation table registers (`DP_MSE_RATE_*`, `DP_MSE_SAT*`, `DP_MSE_SAT*_STATUS`, `DP_MSE_SAT_UPDATE`) and MSO controls (`DP_MSO_CNTL`, `DP_MSO_CNTL1`). The control flow is register-table driven: higher-level MST allocation code writes source IDs and slot counts, triggers updates, and checks update/status fields.

## State And Persistence Behavior

The header itself has no mutable state, allocation, persistence, or lifetime behavior. Its constants become compile-time metadata in the amdgpu display driver.

The hardware fields described by the chunk are stateful MMIO registers. Some are programmed configuration state, such as pixel encoding, color depth, lane count, stream enable, FIFO levels, secondary packet enable bits, line numbers, ACR N/CTS values, DSC/MSO/MSE settings, and ALPM timings. Some are transient command bits, such as `*_SEND`, `*_ACK`, `*_CLEAR`, `*_RESET`, and immediate update controls. Some are hardware status/readback bits, such as packet pending/active/deadline, double-buffer pending/taken, FIFO error/calibrated, link status, stream status, ALPM interrupt/status/pending, CRC result valid, and MSE slot status.

Persistence is therefore hardware-scoped. Values can survive across parts of a modeset or link training sequence until the driver rewrites them or the display engine is reset. Incorrect masks can leave stale fields in place during read-modify-write operations, while incorrect shifts can write valid-looking values into unrelated hardware fields.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.2.1 register offset header for actual MMIO addresses. A mask from this file is only meaningful when paired with the corresponding `reg...` address and base index in `dcn_3_2_1_offset.h`.

The main integration point is the AMD display core register helper layer. The generated field names must match the logical names expected by stream/link encoder mask-list macros. For example, a `SE_SF(DP0_DP_GSP11_CNTL, DP_SEC_GSP11_ENABLE, mask_sh)` entry depends on this header providing the matching per-instance field layout, even when the runtime object is built for DP1/DP2 style instances through register-list expansion.

The chunk also integrates with protocol-level features:

- HDMI 2.x/FRL-adjacent packet generation, scrambling, deep color, ACR, audio, AVI/audio/MPEG infoframes, metadata packets, and generic packets.
- DisplayPort main link stream control, MSA/VBID timing, FEC/DPHY control, link training/test patterns, scrambler and CRC diagnostics.
- DisplayPort secondary data packets and generic stream packets used for VSC, SPD, HDR static metadata, adaptive sync, DSC PPS, and other SDP payloads.
- DisplayPort MST slot allocation and update status.
- DSC, MSO, ALPM, and auxless wake/sleep behavior.

## Risks And Edge Cases

Generated header correctness is critical because most mistakes compile cleanly. A wrong mask or shift can cause hardware programming errors without a type-system signal.

High-risk fields in this chunk include write-one or command/status-style bits such as `*_ACK`, `*_CLEAR`, `*_SEND`, `*_RESET`, and `*_IMMEDIATE`. If a mask is too wide, a read-modify-write can acknowledge or clear adjacent status unintentionally. If a mask is too narrow, a command may never reach hardware.

DP secondary packet and GSP fields are timing-sensitive. `DP_SEC_GSP*_LINE_NUM`, `*_LINE_REFERENCE`, `*_SEND_PENDING`, `*_SEND_ACTIVE`, and `*_SEND_DEADLINE_MISSED` must align with vblank/line scheduling expectations. Errors can manifest as missing HDR metadata, VSC/Adaptive-Sync packets, or DSC PPS packets even when the display link otherwise trains successfully.

HDMI generic packet controls span many packet slots across `HDMI_GENERIC_PACKET_CONTROL0`, `5`, `6`, and `10`, with line fields split across additional control registers. Slot numbering errors or instance-prefix mismatches can route packet control to the wrong generic packet buffer.

MST/MSE allocation fields pack multiple source IDs and slot counts into the same registers. Incorrect widths can corrupt neighboring allocation entries and cause bandwidth allocation failures only on multi-stream topologies.

ALPM and auxless ALPM fields mix command, timing, interrupt, and line/frame scheduling state. Bad definitions can create intermittent resume/wakeup, FEC timing, or panel power behavior problems that are difficult to reproduce in simple single-monitor testing.

The DIG1/DIG2 blocks are intentionally duplicated. Copy/paste or generator drift between instances would create asymmetric behavior where only one connector/encoder instance fails. The same applies to DP1/DP2/DP3 instance families, especially because this chunk starts and ends mid-instance.

## Test Signals

Build-time test signals are limited: this header is primarily validated by successful compilation of the amdgpu display driver with DCN 3.2.1 resources enabled. Missing or renamed macros should fail compilation in resource, stream encoder, or link encoder mask-list construction.

Runtime validation requires display hardware or register-level simulation. Useful signals include:

- HDMI modeset tests covering deep color, scrambling, audio ACR, generic/infoframe/metadata packets, AVMUTE, and TMDS character generation on both DIG1 and DIG2.
- DP link training and modeset tests covering link status, lane count, stream enable/status, M/N timing, MSA/VBID fields, FEC, scrambler, PRBS/test patterns, and DPHY CRC.
- DSC enablement tests that verify PPS packets are sent through GSP11 and that `DP_SEC_GSP11_ENABLE`, `DP_SEC_GSP11_LINE_NUM`, and `DP_SEC_GSP11_PPS` interact correctly.
- HDR, VSC, SPD, Adaptive-Sync, and other SDP packet tests that confirm GSP enable/send/pending/deadline behavior.
- MST tests that exercise MSE rate programming, slot allocation table updates, status readback, and multiple streams sharing a DP link.
- ALPM/auxless ALPM suspend-resume and panel power tests that check wakeup interrupts, wake/FEC line numbers, sleep intervals, and hardware-mode transitions.
- Register dump comparisons against AMD golden values or firmware traces for DCN 3.2.1 are strong regression signals because they catch silent bitfield drift in generated mask headers.

### subset-b-002040: lines 32541-34936

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 32541-34936

## Purpose

This chunk is generated AMD DCN 3.2.1 display-controller register field metadata. It contains no executable C code; it publishes `#define` constants for field shifts and masks used to pack and unpack MMIO register values in the AMDGPU display driver.

The assigned range covers the tail of the `DP3` DisplayPort stream/link block, the complete visible `DIG3` digital encoder front/back-end block, most of the `DP4` DisplayPort block, and the beginning of the `DIG4` digital encoder block. The range contains 2,172 `#define` entries plus generated register-name comments. Every field appears as a pair or set of `__SHIFT` and `_MASK` macros that consumers feed into register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, and field-description tables.

Although this repository path is under a `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, or local control constructs in this span. The public surface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: low-bit position for a field inside a 32-bit hardware register.
- `<REGISTER>__<FIELD>_MASK`: bitmask for the same field.
- Register comments such as `//DP4_DP_SEC_CNTL2` and address-block comments such as `// addressBlock: dce_dc_dio_dp4_dispdec`, which group the generated symbols by display hardware block.

Major field families in this chunk:

- `DP3_DP_DPHY_*`: DisplayPort PHY control fields for analog-test lane selection, FEC enable/status shadows, scrambler selection, bypass/skew bypass, training pattern selection, explicit 8b/10b symbols, PRBS generation, scrambler behavior, CRC enable/control/results, MST CRC phase status, fast-training timing/status, HBR2 pattern control, and blanking-symbol swap/load state.
- `DP3_DP_SEC_*`: secondary-data packet and audio fields for stream enable, ASP/ATP/AIP/ACM/ISRC/MPG/GSP enable bits, packet framing windows, audio `N`/`M` programming and readback, timestamp mode, ASP packet coding/priority/version, generic stream packet send/pending/deadline/line-number controls, enable double-buffer status, metadata transmission, and DB lock/taken/pending status.
- `DP3_DP_MSE_*`, `DP3_DP_MSO_*`, and `DP3_DP_DSC_CNTL`: MST/MSE stream allocation fields for rate ratio, SAT source/encryption/slot count tables and readback, SAT update, link timing, blank-code/timestamp/zero-encoder controls, MSO split-link secondary-data enables, and a DSC mode bit.
- `DP3_DP_ALPM_*` and `DP3_DP_AUXLESS_ALPM_*`: DisplayPort low-power/AUX-less ALPM controls for main-link PHY sleep/standby sends and pending bits, sleep sequence mode, line-number scheduling, LFPS wakeup timing, immediate wake/FEC enable controls, hardware-mode enable/disable, frame-number fields, and wakeup interrupt mask/status/clear fields.
- `DIG3_DIG_*`: digital encoder front-end/back-end fields for source selection, stereosync, digital bypass, split-link pixel grouping, input pixel select, Dolby Vision enable/missed metadata, symbol clock status, TMDS pixel encoding/color format, output CRC, test/random/static patterns, FIFO enable/reset/read-level/calibration/error, and version/forced-disable controls.
- `DIG3_HDMI_*`: HDMI metadata/control/status/audio fields, including keepout, scrambling, clock-channel rate, packet generator version, error ack/mask, unscrambled-control line, deep-color enable/depth, active AVMUTE, audio/VBI packet errors, audio layout, ACR packet source/timing, VBI/infoframe/generic packet send/continuous/line-reference/update-lock controls, immediate send pending bits, generic-packet line fields, DB lock/taken/pending fields, ACR CTS/N programming and status for 32/44.1/48 kHz families, and GC AVMUTE/packing phase controls.
- `DIG3_TMDS_*`: TMDS sync phase, control-character enables, feedback selection/delay, stereosync control selection, sync-character patterns, control bits, DC balancer controls, and generated control 0/1/2/3 data selection, delay, invert, modulation, feedback, and pattern output fields.
- `DP4_DP_*`: the same high-level DisplayPort link/stream/DPHY/secondary-packet/MSE/MSO/ALPM/GSP/AUX-less ALPM families as `DP3`, but for instance 4. This begins with `DP4_DP_LINK_CNTL`, `DP4_DP_PIXEL_FORMAT`, MSA timing/colorimetry/misc fields, link framing, stream timing, video `M/N`, interrupt controls, and then continues through DPHY, secondary-data, MST/MSE, DSC, DB, metadata, GSP8-GSP11, and AUX-less ALPM fields.
- `DIG4_DIG_*` and initial `DIG4_HDMI_*`: the beginning of digital encoder instance 4, covering front-end source/bypass/Dolby/TMDS-color fields, output CRC, test pattern, FIFO controls, HDMI metadata control, HDMI core control, and the start of HDMI status.

## Control Flow

This header chunk has no runtime control flow. Runtime behavior comes from AMD display code that includes this file together with `dcn_3_2_1_offset.h` and then builds register/field tables.

The key integration path in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`, which includes both `dcn/dcn_3_2_1_offset.h` and `dcn/dcn_3_2_1_sh_mask.h`. That file defines token-pasting helpers such as `SR(...)` and `SRI(...)` for register addresses; the corresponding field macros from this chunk are consumed by the broader DC register helper layer when code writes or reads selected fields.

Typical runtime sequencing, outside this generated file, is:

1. DCN 3.2.1 resource construction selects register offsets and field masks for each display block instance.
2. Link encoder, stream encoder, HDMI/DP audio, packet, and modeset code chooses an instance such as `DP3`, `DIG3`, `DP4`, or `DIG4`.
3. Register helper macros combine the instance address from the offset header with the field shift/mask from this header.
4. Driver code programs link training, stream enable/disable, pixel format, MSA timing, secondary-data packets, HDMI packet generation, audio clock regeneration, MST slot allocation, DSC mode, ALPM, and test/debug paths.

The macros do not encode sequencing rules. Correct consumers must still order clock/power enablement, link training, video stream enablement, packet double-buffer updates, interrupt clear/ack writes, FEC/DSC transitions, MST allocation updates, and suspend/resume restoration according to hardware requirements.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on disk. It describes fields in MMIO-backed display hardware state.

Represented hardware state includes:

- Per-instance DP PHY state for FEC, scramblers, training patterns, explicit symbol patterns, PRBS, CRC capture, fast training, HBR2 patterns, and PHY low-power transitions.
- Per-instance DP stream state for link status, pixel format, stream enable/status, MSA timing/colorimetry/misc fields, video `M/N`, VBID overrides, secondary-data packet framing, metadata transmission, audio `M/N`, and packet collision/mute status.
- MST/MSO/MSE state for stream allocation tables, slot counts, encryption bits, rate updates, link timing, MSO secondary-data enables, and SAT status readback.
- Generic stream packet state for GSP0-GSP11 enable/send/line/deadline/pending controls and double-buffer pending status.
- ALPM/AUX-less ALPM state for PHY sleep/standby sends, scheduled wake/FEC enable line numbers, LFPS timing, hardware-mode ALPM enable, frame/line counters, wakeup interrupts, and immediate wakeup behavior.
- DIG/HDMI/TMDS state for selected source, bypass, stereo sync, Dolby Vision metadata, FIFO calibration/error status, output CRC, test patterns, HDMI scrambling/deep-color/keepout/error handling, metadata/infoframe/generic-packet scheduling, ACR CTS/N programming and readback, AVMUTE, and TMDS control-pattern generation.

Persistence is hardware-defined. Configuration fields generally retain values until modeset, link reconfiguration, power gating, suspend/resume, or ASIC reset. Status, pending, clear, ack, readback, interrupt, and calibration fields may be read-only, sticky, self-clearing, or write-one-to-clear depending on the register. This generated header gives only bit locations; it does not identify access type or side effects.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.2.1 register database and must stay consistent with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h`, which defines the matching `regDP3_*`, `regDIG3_*`, `regDP4_*`, and `regDIG4_*` register offsets and base indexes.
- AMD display register helper code that interprets `__SHIFT`/`_MASK` pairs as field descriptors for `REG_*` operations.
- DCN 3.2.1 resource initialization in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`, the direct include site found in this tree.
- DIO/link encoder, stream encoder, HDMI audio/packet, MST, DSC, ALPM, and hotplug/modeset paths that program DP and DIG blocks through generated register tables.

The repeated instance naming is a major integration contract. `DP3` fields must align with `regDP3_*` offsets, `DIG3` with `regDIG3_*`, `DP4` with `regDP4_*`, and `DIG4` with `regDIG4_*`. Cross-generation comparison shows similar fields in nearby generated headers such as `dcn_3_2_0_sh_mask.h` and `dcn_3_5_1_sh_mask.h`, but the DCN 3.2.1 file is the authoritative mask/shift source for this ASIC generation.

## Risks And Edge Cases

- Generated mask drift is the central risk. A wrong shift or mask compiles cleanly but can update the wrong bits in MMIO, corrupting unrelated hardware state in the same register.
- Instance copy errors are hard to detect statically. `DP3`, `DIG3`, `DP4`, and `DIG4` are structurally similar, so a mismatched instance prefix may only fail on connectors routed to one physical display engine.
- Chunk boundaries are artificial. The first line is the final mask from the previous `DP3_DP_VID_INTERRUPT_CNTL` register, and the final line stops immediately after the start of `DIG4_HDMI_STATUS`; adjacent chunks are required for complete file-level conclusions.
- Status and command fields are side-effect-sensitive. Pending, taken, clear, ack, interrupt clear, wakeup send, immediate send, and deadline-missed fields can be sticky or self-clearing; using the right bit location is necessary but not sufficient.
- MST/MSO fields are table-like and timing-sensitive. Wrong SAT source, slot-count, update, rate, or status masks can produce failures only under MST, MSO, DSC, or multi-stream bandwidth pressure.
- HDMI packet and audio fields interact with vertical blank timing. Incorrect generic-packet line, update-lock, immediate-send, ACR, AVMUTE, or metadata masks can cause intermittent infoframe loss, audio dropouts, or sink-specific HDMI failures.
- ALPM and FEC fields interact with link training and low-power states. Bad wake/sleep/FEC scheduling can create resume-only, low-power-only, or panel-specific blanking issues.
- This file provides no type safety. All macros are integer constants, so build success only proves symbol availability, not hardware correctness.

## Test Signals

Useful validation signals include:

- Build AMDGPU/DC with DCN 3.2.1 support enabled; missing or renamed field macros should fail in resource and display block register-table initialization.
- Mechanically verify that each visible field in lines 32541-34936 has a `__SHIFT` and matching `_MASK` macro, and that each mask is consistent with the implied bit position and field width.
- Diff this span against the same register families in `dcn_3_2_0_sh_mask.h` and AMD's authoritative DCN 3.2.1 register database; intentional differences should be tied to ASIC changes.
- Exercise displays routed through DP/DIG instances 3 and 4, including hotplug, link training, stream enable/disable, mode changes, color-depth/pixel-format changes, suspend/resume, and high-bandwidth modes.
- Test DP secondary-data paths: audio playback, audio mute, metadata packets, GSP packets, ISRC/MPG/ASP/AIP/ACM behavior, packet collision handling, DB pending/taken state, and metadata line scheduling.
- Test HDMI paths on `DIG3` and `DIG4`: scrambling, deep color, AVMUTE, metadata/infoframes, generic packets, ACR CTS/N values, audio at 32/44.1/48 kHz families, and TMDS control/test patterns.
- Validate MST/MSO/MSE behavior on `DP3` and `DP4`: SAT allocation, rate updates, payload timing, slot-count readback, MSO secondary-data enables, DSC mode, and multi-stream reconfiguration.
- Exercise ALPM/AUX-less ALPM and FEC transitions, especially low-power entry/exit, wakeup interrupts, immediate wakeup, FEC enable timing, and resume from panel/link idle states.
- Watch kernel logs and display diagnostics for link-training failures, AUX/ALPM wake failures, stuck pending bits, packet deadline misses, audio dropouts, HDMI packet errors, FIFO errors, CRC mismatches, MST payload errors, and display blanking isolated to connector instances 3 or 4.

## Cross-Chunk Notes

Earlier chunks contain the start of the `DP3` block, including the register fields before `DP3_DP_DPHY_CNTL` and most of `DP3_DP_VID_INTERRUPT_CNTL`. Later chunks continue `DIG4_HDMI_STATUS` and the rest of digital encoder instance 4. The final merged per-file research should combine adjacent chunks before making whole-file claims about all DCN 3.2.1 display register masks or all DP/DIG instances.

### subset-b-002041: lines 34937-37346

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 34937-37346

## Scope

This chunk is a generated DCN 3.2.1 register-field shift/mask slice for AMDGPU Display Core. It contains preprocessor constants only: 2,164 `#define` entries in this range, with 1,081 `_SHIFT` macros and 1,083 `_MASK` macros. There are no C functions, structs, enums, executable branches, allocations, locks, or direct MMIO accesses in the chunk.

The range starts inside the `DIG4_HDMI_STATUS` register, after the earlier status field shifts from the preceding chunk, and continues through the rest of the `DIG4` HDMI, audio-format, backend, and TMDS field definitions. It then covers five repeated DIO-associated audio-format blocks, `AFMT0` through `AFMT4`; five dynamic metadata engine blocks, `DME0` through `DME4`; five video packet generator blocks, `VPG0` through `VPG4`; and ends at the beginning of the `DP_AUX0_AUX_CONTROL` field list. The final `DP_AUX0_AUX_CONTROL__SPARE_1_MASK` and subsequent AUX fields are outside this chunk.

## Purpose And Hardware Surface

This header is part of the generated register ABI used by the DCN 3.2.1 display driver. The companion offset header names the MMIO registers, while this file supplies the bit positions and masks used by register helper macros to pack fields into 32-bit hardware registers and extract readback/status fields.

Major hardware areas represented here:

- `DIG4` HDMI packet generation and status: HDMI audio delay, ACR generation, VBI packets, audio/MPEG infoframes, 15 generic packet slots, generic packet line scheduling, generic packet checksums, double-buffer enable/pending state, general-control packet fields, ACR N/CTS values for 32/44.1/48 kHz families, and ACR readback.
- `DIG4` digital backend and TMDS output: AFMT audio clock gating, backend enable/source/mode/HPD select, TMDS sync phase, control characters, feedback path selection, stereo sync selection, sync patterns, TMDS control bits, DC balancer controls, generated control-symbol controls, digital version, and force-disable state.
- `AFMT0` through `AFMT4`: per-DIO audio formatting blocks for HDMI/DP audio packet limits, audio layout/channel/stream selection, audio infoframe bytes, IEC 60958 channel-status fields, audio CRC test/readback, audio ramp/test data, AFMT status, audio sample send controls, audio source selection, and AFMT memory power state.
- `DME0` through `DME4`: per-DIO dynamic metadata engines with HUBP requestor selection, enable, stream type, double-buffer pending/taken/clear/disable state, missed-transmission status/clear, and DME memory power controls.
- `VPG0` through `VPG4`: per-DIO video packet generators for indexed generic packet data bytes, frame-update and immediate-update triggers for generic packet slots 0-14, update-pending readback, conflict status/clear, GSP memory power controls, ISRC indexed data access, and MPEG infoframe payload/update fields.
- `DP_AUX0_AUX_CONTROL`: the opening of the first DP AUX block, including AUX enable/reset/read/update-disable behavior, HPD-disconnect handling, mode detect, HPD selection, impedance calibration request enable, test mode, deglitch, and spare fields.

## Important Definitions

The naming convention is consistent with generated AMD DC register headers:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted 32-bit field mask.
- `//<REGISTER>` comments group fields by register.
- `// addressBlock: ...` comments mark generated hardware block boundaries such as `dce_dc_dio_dig0_afmt_afmt_dispdec`, `dce_dc_dio_dig0_dme_dme_dispdec`, `dce_dc_dio_dig0_vpg_vpg_dispdec`, and `dce_dc_dio_dp_aux0_dispdec`.

Important macro families in this chunk:

- `DIG4_HDMI_GENERIC_PACKET_CONTROL0/6` define send, continuous-send, line-reference, and update-lock-disable bits for HDMI generic packet slots 0-14. `CONTROL1/2/3/4/7/8/9/10` provide line-number scheduling, checksum bytes, double-buffer enable bits, and double-buffer pending status for those slots.
- `DIG4_HDMI_DB_CONTROL` defines packet double-buffer handshake state: pending, taken, clear, lock, disable, and vupdate-pending/taken/clear fields.
- `DIG4_HDMI_ACR_*` and `DIG4_HDMI_ACR_STATUS_*` define audio clock regeneration CTS/N programming and readback fields. The fixed 20-bit masks are used for HDMI audio sample-rate timing families.
- `DIG4_TMDS_*` define TMDS serializer and control-symbol behavior, including control-character enable, feedback selection/delay, sync character patterns, DC-balance behavior, generated CTL0-CTL3 data select/delay/invert/modulation/feedback/pattern fields, and the two-bit counter enable.
- `AFMTn_AFMT_AUDIO_PACKET_CONTROL2`, `AFMTn_AFMT_AUDIO_INFO0/1`, `AFMTn_AFMT_60958_0/1/2`, and `AFMTn_AFMT_AUDIO_PACKET_CONTROL` are repeated for instances 0-4. They are the per-stream audio-format programming surface used to route audio source IDs, select audio layout/channel map, program HDMI audio infoframes and IEC 60958 channel status, trigger channel-status updates, and control audio sample sending.
- `AFMTn_AFMT_AUDIO_CRC_CONTROL/RESULT`, `AFMTn_AFMT_RAMP_CONTROL0-3`, and `AFMTn_AFMT_STATUS` define audio diagnostics and status: CRC enable/continuous/source/channel/count, CRC completion/result, generated ramp bounds/increment/decrement, FIFO overflow, HBR state, audio-enable state, and audio-enable-change status.
- `DMEn_DME_CONTROL` defines metadata-engine runtime state and side-effecting status clear bits for dynamic metadata transmission. `DMEn_DME_MEMORY_CONTROL` defines memory power force/disable/state/default-low-power fields.
- `VPGn_VPG_GENERIC_PACKET_ACCESS_CTRL` and `VPGn_VPG_GENERIC_PACKET_DATA` define indexed payload access to generic packet data. `VPGn_VPG_GSP_FRAME_UPDATE_CTRL` and `VPGn_VPG_GSP_IMMEDIATE_UPDATE_CTRL` define frame-synchronous versus immediate update requests plus corresponding pending readback for generic packets 0-14.
- `VPGn_VPG_GENERIC_STATUS`, `VPGn_VPG_MEM_PWR`, `VPGn_VPG_ISRC1_2_*`, and `VPGn_VPG_MPEG_INFO*` define packet update conflict handling, GSP memory light-sleep state, ISRC payload byte access, and MPEG infoframe bytes/update state.
- `DP_AUX0_AUX_CONTROL` starts the AUX channel control surface, but this chunk only contains part of that register's definitions. The next chunk is needed for the complete AUX0 block.

## Control Flow And State Behavior

This chunk has no executable control flow. Runtime behavior comes from Display Core code that includes `dcn_3_2_1_offset.h` and `dcn_3_2_1_sh_mask.h`, initializes register/shift/mask tables, and then uses helpers such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, `REG_WAIT`, `SRI(...)`, `SR_ARR(...)`, and `SE_SF(...)` to access MMIO registers.

Typical runtime flow using these fields:

1. `dcn321_resource.c` includes the DCN 3.2.1 generated offset and shift/mask headers and expands mask-list macros into typed shift and mask structures for stream encoders, VPG, AFMT, DIO, AUX, and related blocks.
2. During stream encoder construction, per-instance register tables map logical stream encoder objects onto `DIG`, `AFMT`, `DME`, and `VPG` register instances. The repeated `AFMT0-4`, `DME0-4`, and `VPG0-4` fields in this chunk supply the instance-zero field names used by the `SE_SF(...)` style macros, then are applied across instances through register arrays.
3. HDMI enable and modeset paths program `DIG4` HDMI packet controls, ACR N/CTS, infoframes, generic packet scheduling, DB handshakes, TMDS symbols, backend mode/source selection, and AFMT audio clock state.
4. Audio setup paths program AFMT audio source selection, channel enable masks, audio layout overrides, IEC 60958 channel-status fields, audio infoframe fields, sample-send control, HBR/OSF override bits, and diagnostic CRC/ramp fields.
5. Dynamic metadata paths enable DME, select the HUBP requestor and stream type, coordinate metadata double-buffer state, and clear taken or missed-transmission statuses.
6. Generic packet paths write VPG indexed payload bytes, request immediate or frame-synchronous updates for generic packet slots 0-14, and watch pending/conflict status before reusing packet storage.
7. AUX initialization paths begin by using `DP_AUX0_AUX_CONTROL` fields for enable/reset/update/read behavior; complete AUX software transaction, arbitration, interrupt, and timing programming is in following lines outside this chunk.

The state described here is hardware register state:

- Persistent programmed state includes HDMI generic-packet scheduling policy, ACR timing values, TMDS control-symbol generation, DIG4 backend source/mode/HPD selection, AFMT channel/audio-info/channel-status programming, DME enable/requestor/stream selection, VPG packet payload bytes, MPEG/ISRC data bytes, and memory power policy bits.
- Volatile readback includes HDMI packet/error and DB pending/taken state, ACR status N/CTS readback, AFMT audio enable/HBR/FIFO overflow/audio-enable-change status, audio CRC done/result, DME DB pending/taken and missed-transmission status, VPG update-pending and conflict status, VPG/DME/AFMT memory power state, and AUX reset-done/read-control status.
- Side-effecting fields include HDMI/VUPDATE DB clear bits, HDMI generic send triggers, AFMT audio FIFO overflow and audio-enable-change acknowledgements, AFMT channel-status update, DME DB-taken clear, DME missed-transmission clear, VPG frame/immediate update triggers, VPG conflict clear, and AUX reset.

There is no disk persistence or driver-owned durable storage in this header. Values persist only in hardware registers until reset, power gating, suspend/resume, hotplug reconfiguration, a new modeset, or another driver path rewrites them.

## Dependencies And Integration Points

This chunk depends on generated-name consistency across the DCN 3.2.1 register header set. The register names and base-index symbols in `dcn_3_2_1_offset.h` must match these shift/mask names, and the Display Core mask-list macros must refer to fields that exist in this generated header.

Known integration points include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`, which includes `dcn/dcn_3_2_1_offset.h` and `dcn/dcn_3_2_1_sh_mask.h`, builds DCN321 shift/mask tables, and maps VPG/AFMT/DME register blocks to DIO stream encoder instances.
- `drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_stream_encoder.h`, whose `SE_COMMON_MASK_SH_LIST_DCN32` refers to HDMI generic packet fields, `DIG0_AFMT_CNTL`, and `DME0_DME_CONTROL` fields that correspond to the repeated generated definitions in this chunk.
- `drivers/gpu/drm/amd/display/dc/dcn31/dcn31_afmt.h`, which defines AFMT register lists and masks for audio packet control, audio source selection, IEC 60958 channel-status fields, and audio sample send behavior.
- `drivers/gpu/drm/amd/display/dc/dcn31/dcn31_vpg.h` and related VPG implementations, which define VPG register lists and fields for generic packet data, frame/immediate update controls, conflict handling, and memory power state.
- `drivers/gpu/drm/amd/display/dc/dio/dcn30/dcn30_dio_stream_encoder.c` and inherited stream encoder code paths, which program AFMT clocks/audio packets, HDMI ACR values, infoframes/generic packets, and DME metadata controls through the generated register tables.
- `drivers/gpu/drm/amd/display/dce/dce_aux.c` and DCN AUX resource initialization, which use the generated AUX shift/mask table for `DP_AUX0_AUX_CONTROL` and subsequent AUX registers.

The repeated hardware-instance pattern is the central integration constraint. The generated macros are instance-specific (`AFMT0` versus `AFMT4`, `DME0` versus `DME4`, `VPG0` versus `VPG4`, `DIG4` versus other DIGs), while Display Core tables often use instance-zero field names as field descriptors and separate register address tables for each instance. A mismatched instance prefix can compile if a table is wired incorrectly, but it can program the wrong encoder block at runtime.

## Risks And Maintenance Notes

- Numeric mask/shift drift is the primary risk. Incorrect values for HDMI generic packet sends, line references, DB handshakes, ACR N/CTS, TMDS control symbols, AFMT channel maps, DME clear bits, or VPG update requests can compile successfully and fail only on DCN 3.2.1 hardware.
- The chunk boundaries split registers. `DIG4_HDMI_STATUS` is only partially present at the beginning, and `DP_AUX0_AUX_CONTROL` is only partially present at the end. Per-file reconciliation must merge adjacent chunks before making complete-register claims.
- Side-effecting clear, ack, update, send, and reset fields are sensitive. A wrong mask can clear the wrong DME/VPG/AFMT/HDMI status, fail to clear a stale event, repeatedly send stale metadata, or leave an update pending.
- Generic packet slots 0-14 have repetitive fields spread across several HDMI and VPG registers. Off-by-one or copied-mask mistakes may affect only a specific packet slot, making failures mode-specific, such as HDR metadata, vendor packets, MPEG infoframes, or ISRC packets.
- AFMT audio programming is format-sensitive. Bad channel-status, sample frequency, channel map, HBR override, or audio layout masks can produce silent audio, wrong speaker mapping, bad AVR reporting, or failures only at particular sample rates and channel counts.
- DME and HDMI/VPG double-buffer fields need synchronization with vupdate or stream update locks. Incorrect pending/taken/clear behavior can cause metadata tearing, dropped HDR dynamic metadata, missed-transmission flags, or stale packet payloads.
- TMDS fields are HDMI/DVI output critical. Incorrect control-symbol, sync-pattern, DC-balance, or generated CTL bit masks can break link stability, deep-color modes, or compliance tests while leaving DisplayPort paths unaffected.
- Memory power fields in AFMT, DME, and VPG blocks can cause intermittent issues if programmed with wrong masks, especially after suspend/resume, display idle, power gating, or hotplug.
- `DP_AUX0_AUX_CONTROL` bits affect low-level AUX channel reset and enable behavior. Because this chunk ends mid-register, any analysis or edits involving AUX0 must include the next chunk for the full field set.

## Test Signals

Useful validation should combine generated-header checks with DCN321 display hardware coverage:

- Build AMDGPU Display Core with DCN 3.2.1 enabled and verify that `dcn321_resource.c`, DIO stream encoders, AFMT, VPG, DME, and AUX users resolve all generated fields from the header.
- Run generated-register consistency checks for this range: paired `_SHIFT`/`_MASK` macros where full registers are inside the chunk, 32-bit mask fit, expected non-overlap within each register, repeated `AFMT0-4`, `DME0-4`, and `VPG0-4` structural parity, and explicit allowance for the split `DIG4_HDMI_STATUS` and `DP_AUX0_AUX_CONTROL` boundary registers.
- Exercise HDMI through the `DIG4` stream encoder with audio enabled, deep color and scrambling where applicable, AVI/audio/MPEG infoframes, vendor/HDR generic packets, general-control packets, ACR sample-rate families at 32/44.1/48 kHz multiples, and TMDS compliance/test-pattern scenarios.
- Validate AFMT audio behavior across 2-channel and multichannel layouts, HBR modes, sample-rate changes, channel-status updates, audio source switching, FIFO overflow handling, and audio CRC/ramp diagnostic paths.
- Test DME dynamic metadata with HDR dynamic metadata enabled and disabled, HUBP requestor changes, stream type changes, DB pending/taken clear sequences, missed-transmission clear handling, and vupdate timing.
- Exercise VPG generic packet updates for slots 0-14 with both frame-synchronous and immediate updates. Watch update-pending, conflict, conflict-clear, payload index/data writes, and memory power state.
- Stress suspend/resume, display blank/unblank, hotplug, modeset, and idle power transitions while monitoring AFMT/DME/VPG memory power states, stale pending bits, packet conflicts, metadata missed flags, HDMI errors, and audio recovery.
- Validate AUX0 reset/enable behavior only together with the following chunk, because this range does not include the complete AUX0 control register or the software/arbitration/interrupt AUX registers.

## Chunk-Specific Summary

Lines 34937-37346 define DCN 3.2.1 bit shifts and masks for the tail of `DIG4` HDMI/status and packet generation, `DIG4` AFMT/backend/TMDS controls, repeated `AFMT0-4` audio-format blocks, repeated `DME0-4` dynamic metadata blocks, repeated `VPG0-4` packet-generator blocks, and the opening of `DP_AUX0_AUX_CONTROL`. The content is generated register ABI rather than executable driver logic. Correctness depends on exact numeric masks, careful instance mapping, safe handling of side-effecting update/clear/send/reset fields, and validation across HDMI audio/metadata, AFMT audio formatting, DME dynamic metadata, VPG packet updates, TMDS output, memory power transitions, and AUX initialization.

### subset-b-002042: lines 37347-39686

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h - subset-b-002042

## Scope

- Chunk id: `subset-b-002042`
- Source lines: 37347-39686
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h`
- Observed content: 2,340 source lines with 2,184 `#define` entries, 1,092 `__SHIFT` macros, 1,127 `_MASK` macros, and 109 register block comments.

This chunk is generated AMD DCN 3.2.1 register field metadata. It does not define executable C, functions, structs, enums, or persistent software objects. Its public interface is the preprocessor namespace of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants used by AMDGPU/DCN register helpers.

## Purpose

The chunk publishes bit layouts for a contiguous Display I/O area covering DisplayPort AUX channels, display DDC I2C registers, and DIO misc power/clock/reset/link controls:

- `DP_AUX0_*` through `DP_AUX4_*` define AUX channel control, software transaction, arbitration, interrupt, status, data FIFO/index, DPHY TX/RX timing/status, GTC sync, sync error, sync controller/status, and PHY wake fields for five DP AUX engines.
- `DC_I2C_*` defines shared DDC hardware I2C control, arbitration, interrupt, software status, per-DDC hardware status, speed/setup, transaction slots, data, EDID detect, and read-request interrupt fields.
- `DIO_SCRATCH0` through `DIO_SCRATCH7` provide full 32-bit scratch data field masks for DIO firmware/driver scratch use.
- `DIO_DP_ALPM_WAKEUP_INTERRUPT_STATUS`, `DIO_MEM_PWR_STATUS`, `DIO_MEM_PWR_CTRL`, and `DIO_MEM_PWR_CTRL2` describe wake interrupt state and light-sleep memory power state/control for I2C and DP link memories.
- `DIO_CLK_CNTL`, `DIO_POWER_MANAGEMENT_CNTL`, `DIG_SOFT_RESET`, `DIO_CLK_CNTL2`, and `DIO_CLK_CNTL3` describe DIO clock gating, power reset, front-end/back-end DIG soft resets, AFMT symbol clock gates, and TMDS symbol clock gates.
- The chunk ends after the first field of `DIO_HDMI_RXSTATUS_TIMER_CONTROL`, so its remaining timer fields continue in the next chunk.

The macros are paired by convention: `REGISTER__FIELD__SHIFT` is the least-significant bit position and `REGISTER__FIELD_MASK` is the already-shifted mask. Consumers combine these with register offsets from `dcn_3_2_1_offset.h`.

## Important APIs, Types, and Macros

There are no normal C APIs or types here. Important exported macro groups are:

- AUX engine programming:
  - `DP_AUXn_AUX_CONTROL` fields include enable, reset, reset-done, link-service read enable, update disable, HPD-disconnect ignore, mode detect, HPD select, impedance calibration request enable, test mode, and deglitch enable.
  - `DP_AUXn_AUX_SW_CONTROL`, `AUX_SW_DATA`, and `AUX_SW_STATUS` fields drive software AUX transactions through `AUX_SW_GO`, start delay, write byte count, indexed data, autoincrement disable, done/request bits, timeout/overflow/HPD-disconnect/protocol error bits, reply byte count, and arbitration status.
  - `DP_AUXn_AUX_ARB_CONTROL` fields arbitrate register ownership among software, link service, and DMCU/firmware users through priority, register ownership status, queued-go disables, pending request aliases, and done-using bits.
  - `DP_AUXn_AUX_INTERRUPT_CONTROL` exposes software done, link-service done, GTC sync lock done, and GTC sync error interrupt/status/ack/mask bits.
  - `DP_AUXn_AUX_LS_STATUS` and `DP_AUXn_AUX_LS_DATA` mirror status/data fields for link-service AUX reads, including CP IRQ, updated, and updated-ack bits.
- AUX physical layer and timing:
  - `DP_AUXn_AUX_DPHY_TX_REF_CONTROL`, `AUX_DPHY_TX_CONTROL`, `AUX_DPHY_RX_CONTROL0`, and `AUX_DPHY_RX_CONTROL1` define TX reference/rate/divider, precharge, output-enable timing, receive windows, threshold behavior, phase detect length, timeout length/multiplier, and precharge skip fields.
  - `DP_AUXn_AUX_DPHY_TX_STATUS` and `AUX_DPHY_RX_STATUS` report TX current-sense calibration and RX mode-detection state.
  - `DP_AUXn_AUX_GTC_SYNC_*` fields configure and observe DP AUX global-time-code synchronization: lock enable, RX global timestamp counters, phase offsets, error timeout/threshold/counter, controller state, continuous update, locked/lost/error status, and status clear.
  - `DP_AUXn_AUX_PHY_WAKE_CNTL` exposes AUX wake enable/status/clear/mask and the AUX connect request status.
- DDC I2C:
  - `DC_I2C_CONTROL`, `DC_I2C_ARBITRATION`, `DC_I2C_INTERRUPT_CONTROL`, and `DC_I2C_SW_STATUS` describe GO/reset/status reset, send reset, software status, transaction count, DDC select, soft reset, register ownership, queuing policy, interrupt acks/masks, timeout, NACK, stop, and overflow state.
  - `DC_I2C_DDC1_HW_STATUS` through `DC_I2C_DDC5_HW_STATUS` describe hardware request, done, status, byte count, setup failure, arbitration loss, timeout, reset, EDID detection, and request type for each DDC engine.
  - `DC_I2C_DDC1_SPEED` through `DC_I2C_DDC5_SETUP` define prescale, threshold, start/stop timing, time limits, enable, data drive enable, setup fail trigger, and send-reset length.
  - `DC_I2C_TRANSACTION0` through `DC_I2C_TRANSACTION3` define stop-on-NACK, start/stop generation, RW, count, and STOP bits for up to four transaction descriptors; `DC_I2C_DATA` supplies RW, byte, index, and autoincrement disable fields.
  - `DC_I2C_EDID_DETECT_CTRL` and `DC_I2C_READ_REQUEST_INTERRUPT` expose EDID detect mode/enable and read-request interrupt ack/mask bits.
- DIO misc:
  - `DIO_MEM_PWR_*` tracks and controls I2C and DPA-DPG memory light sleep, including force/disable controls.
  - `DIO_CLK_CNTL*` controls DISPCLK/REFCLK/SOCCLK/SYMCLK gates for DIGA-DIGG, AFMT, and TMDS paths.
  - `DIG_SOFT_RESET` has paired front-end/back-end soft reset fields for DIGA-DIGG.
  - `DIO_POWER_MANAGEMENT_CNTL` exposes PM reset and all-busy-off state.

## Control Flow

This header has no runtime control flow. Runtime control is implemented by display components that include the matching offset and shift/mask headers, populate register/field tables, and call DC register helper macros such as `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and `REG_UPDATE_N`.

External flows implied by this chunk include:

1. AUX transactions: a caller acquires AUX register ownership via `AUX_ARB_CONTROL`, programs `AUX_SW_DATA` and `AUX_SW_CONTROL` byte count/start delay, asserts `AUX_SW_GO`, polls or interrupts on `AUX_SW_DONE`, reads reply byte count/data/status, acknowledges `AUX_SW_DONE_ACK`, and releases ownership with `AUX_SW_DONE_USING_AUX_REG`.
2. AUX link-service reads and CP IRQ handling: link-service status/data and updated/ack bits allow hardware-assisted AUX monitoring separate from direct software transactions.
3. AUX DPHY setup: link encoder initialization uses RX start/receive windows, threshold, transition filter, precharge skip, timeout length, TX precharge, and mode-detect delay fields before normal hotplug/link traffic.
4. I2C/DDC operations: hardware I2C setup deasserts soft reset, optionally wakes I2C memory from light sleep, acquires I2C arbitration, programs speed/setup/transactions/data, handles interrupts/status, releases the engine, and may force I2C memory back into light sleep.
5. Link encoder muxing and reset: DCN link encoder code writes `DIO_LINKx_CNTL` fields in adjacent chunks for HPO HDMI/DP routing; this chunk provides the DIO clock, reset, and power fields that bound that programming.
6. Power and clock gating: display initialization, suspend/resume, and low-power paths use DIO memory power status/control, clock gate disables, and DIG soft-reset masks to coordinate access to DIO sub-blocks.

## State and Persistence Behavior

The macros are stateless compile-time constants. They describe MMIO register fields whose state lives in display hardware:

- Persistent configuration until reset or reprogramming: AUX enable, HPD select, mode detect, deglitch, DPHY timing, GTC sync configuration, I2C speed/setup limits, DDC select, DIO light-sleep disable/force fields, clock gate disable fields, DIG soft reset bits, and PM reset fields.
- Transient command or handshake fields: `AUX_SW_GO`, link-service read trigger, interrupt ACK bits, GTC status clear, AUX wake clear, I2C GO, send reset, status reset, transaction START/STOP, EDID detect controls, read-request interrupt ACK, and done-using arbitration bits.
- Status/observation fields: AUX done/request/error/reply-count/arbitration, DPHY TX/RX status, GTC controller/sync/error status, AUX wake/connect request, I2C hardware/software status, I2C timeout/NACK/overflow/stop, DDC EDID detection, DIO memory power states, ALPM wake interrupt state, PM all-busy-off, and HDMI RX status timer state.
- Scratch registers are modeled as full 32-bit fields and may preserve opaque firmware/driver state until overwritten or reset by the relevant hardware domain.

## Dependencies

This chunk depends on the generated AMDGPU/DCN register infrastructure:

- Matching register offsets and base indices in `drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h`.
- DC register access helpers and field-table macros that expect the `REG__FIELD__SHIFT` and `REG__FIELD_MASK` naming convention.
- AUX consumers in `display/dc/dce/dce_aux.h` and related AUX engine code, which map `DP_AUX0_*` fields into `struct dce110_aux_registers` and AUX mask/shift tables.
- DDC I2C consumers in `display/dc/dce/dce_i2c_hw.c` and `dce_i2c_hw.h`, which use `DIO_MEM_PWR_CTRL`, `DIO_MEM_PWR_STATUS`, and `DC_I2C_*` fields for hardware I2C transactions.
- Link encoder/resource consumers such as `display/dc/dio/dcn31/dcn31_dio_link_encoder.*`, `dcn35_dio_link_encoder.*`, and DCN resource files, which use AUX DPHY fields, DIO clock fields, memory power fields, and DIG/DIO register tables.

The path is inside a Ceph client source corpus, but the content is Linux AMDGPU display driver register metadata and is not Ceph-specific.

## Integration Points

Important integration points are:

- DisplayPort AUX transport for DPCD reads/writes, link training support traffic, HDCP/CP IRQ handling, hotplug-related AUX wake, and AUX-to-GTC synchronization.
- Display DDC hardware I2C for EDID reads, HDMI/DP sink management, HDCP polling, and DDC arbitration with firmware/hardware users.
- Link encoder initialization, where AUX DPHY timing and DIO clock/reset state must be correct before a transmitter can communicate reliably.
- Display power management, where low-power memory controls and clock gate disables interact with register availability and suspend/resume behavior.
- Firmware/DMUB/DMCU coordination, especially around AUX/I2C arbitration and shared ownership fields.
- Hardware diagnostics and bring-up tooling, where scratch registers, protocol error status bits, GTC sync status, DPHY status, and DIO clock/reset bits are useful readback signals.

## Risks and Edge Cases

- Generated mask/shift drift would silently corrupt MMIO field access. AUX/I2C ownership, status ack, clock gate, reset, and power fields are especially sensitive because wrong bits can hang register access or break hotplug/DDC.
- The chunk repeats nearly identical register layouts for AUX0-AUX4 and DDC1-DDC5. Copy/paste or generated-index mistakes can compile while programming the wrong engine.
- Ownership fields have aliases such as pending request and use request sharing the same bit. Callers must use the correct semantic name for readability and must still follow the hardware handshake.
- ACK, clear, GO, reset, and done-using fields may have pulse or write-one semantics. Generic read-modify-write behavior can lose events if callers do not respect the hardware protocol.
- Multi-bit fields such as HPD select, start delay, write byte count, reply byte count, RX timeout, timestamp counters, I2C prescale/time limits, byte counts, and test clock select require proper masking and range validation.
- I2C memory light sleep must be coordinated with register access. `dce_i2c_hw.c` explicitly wakes memory and waits on `I2C_MEM_PWR_STATE` before setup, then can force light sleep on release.
- AUX and I2C arbitration crosses software and firmware/hardware users. Failing to release ownership can starve DMUB/DMCU or hardware pollers; releasing while a transaction is active can corrupt bus traffic.
- Clock gate and soft-reset fields affect shared DIO/DIG blocks across multiple links. Per-link changes can have cross-link impact when clocks or reset domains are shared.
- The chunk boundary starts after the `DP_AUX0_AUX_CONTROL` shift definitions and ends before the full `DIO_HDMI_RXSTATUS_TIMER_CONTROL` block is present. The final merged report needs adjacent chunks for complete field coverage.

## Test Signals

Useful validation signals for code using this chunk:

- Build coverage for DCN 3.2.1 consumers that include `dcn_3_2_1_offset.h` and this shift/mask header, catching missing or renamed generated macros.
- Generated consistency checks that every field has aligned shift/mask pairs, masks match shifts, and repeated AUX/DDC instances have equivalent field layouts where expected.
- Unit-style field insert/extract tests for multi-bit fields: AUX HPD select, AUX write/reply byte counts, AUX RX timeout length/multiplier, GTC timestamps/offsets, I2C prescale/time limits, I2C transaction count, DDC byte count, DIO test clock select, and DIG reset bits.
- Hardware smoke tests for DP AUX DPCD reads/writes, EDID reads over DDC1-DDC5, hotplug with AUX wake, link training, HDCP polling, and suspend/resume with I2C memory low power enabled.
- Register trace checks that AUX/I2C arbitration is acquired and released, ACK/clear bits are written only after the corresponding status event, and light-sleep force is paired with a successful power-state wait.
- Display mode-set and link recovery tests across multiple transmitters to catch clock gate, soft reset, or repeated-instance indexing errors.

## Chunk Boundary Notes

The first visible line is the final `SPARE_1_MASK` entry for `DP_AUX0_AUX_CONTROL`; that register's shift entries and earlier masks are in the previous chunk. The last visible line is `DIO_HDMI_RXSTATUS_TIMER_CONTROL__DIO_HDMI_RXSTATUS_TIMER_ENABLE__SHIFT`; the rest of that register's fields continue after line 39686. The merge/reconciliation lane should combine this report with adjacent chunks before producing the final per-file research document for `dcn_3_2_1_sh_mask.h`.

### subset-b-002043: lines 39687-42210

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 39687-42210

## Scope

This chunk is a generated AMD DCN 3.2.1 register shift/mask slice. It contains preprocessor constants only: each `<REGISTER>__<FIELD>__SHIFT` macro gives a field bit position and each `<REGISTER>__<FIELD>_MASK` macro gives the corresponding in-register mask. `//<REGISTER>` comments group constants by hardware register and `// addressBlock:` comments identify the generated hardware address block.

There are no C functions, structs, enums, loops, branches, direct MMIO calls, locking paths, allocation paths, or software persistence paths in this range. Runtime behavior comes from AMDGPU Display Core code that includes this header with the matching `dcn_3_2_1_offset.h` register-address header and then feeds these constants to register helper macros such as `REG_UPDATE`, `REG_GET`, and related generated field helpers.

The range starts in the middle of `DIO_HDMI_RXSTATUS_TIMER_CONTROL`: the `DIO_HDMI_RXSTATUS_TIMER_ENABLE__SHIFT` line is immediately before this chunk, while the remaining shifts and all masks are here. It ends in the middle of `DSCC0_DSCC_PPS_CONFIG19`: this chunk includes shifts through `RANGE_MIN_QP8__SHIFT`, while the remaining shifts and all masks for config 19 continue in the next chunk. The later merge lane should treat both boundary registers as split.

## Purpose And Hardware Surface

The purpose of this header section is to provide the bit layout for DCN 3.2.1 display I/O, GPIO, UNIPHY, panel power sequencing, backlight PWM, and DSC encoder registers. These macros are a hardware ABI for the display driver: callers can assemble or decode packed MMIO register values without hardcoding raw bit positions.

The chunk covers these address blocks and register families:

- DIO and DCIO display decode registers: HDMI RX status timer fields, DIO link A-F encoder mux selection, generic clock/test outputs, DCIO clock/ref-clock control, UNIPHY lane inversion and channel crossbar fields, write-command delay, pinstraps, spare bits, intercept state, pattern generator state, genlock/swaplock pad controls, and DCIO soft reset bits.
- GPIO/DDC/HPD/AUX registers: generic GPIO masks, DDC1-DDC5 and DDCVGA mask/A/EN/Y fields, genlock GPIO fields, HPD mask/A/EN/Y fields, drive strength registers, power sequence enable bits, pad strength, AUX PHY control, TX impedance and TX12 enable fields, AUX control registers 0-5, RX enable and pull-up enable fields, and AUX/I2C pad power status.
- UNIPHY macro reserved register windows: repeated `DCIO_UNIPHY0` through `DCIO_UNIPHY4` `UNIPHY_MACRO_CNTL_RESERVED0..57` full-width masks. These expose generated placeholders or opaque macro-control words for five UNIPHY instances.
- Panel power sequence and backlight registers: `DC_GPIO_PWRSEQ_*`, `PANEL_PWRSEQ_*`, `BL_PWM_*`, lock/ref-divider/spare registers.
- DSC compressor control registers: `DSCC0_DSCC_CONFIG0/1`, `DSCC0_DSCC_STATUS`, `DSCC0_DSCC_INTERRUPT_CONTROL_STATUS`, and `DSCC0_DSCC_PPS_CONFIG0..19` through the start of config 19.

## Important Definitions

The DIO link selector group is a primary integration surface. `DIO_LINKA_CNTL` through `DIO_LINKF_CNTL` all define `ENC_TYPE_SEL`, `HPO_HDMI_ENC_SEL`, and `HPO_DP_ENC_SEL`. DCN link encoder code uses these fields to route a UNIPHY transmitter to legacy, HDMI FRL, or DP 128b/132b encoder paths and to choose the HPO encoder instance.

The DCIO/UNIPHY control group defines clock and physical lane steering fields:

- `DC_GENERICA` and `DC_GENERICB` select generic clock outputs and UNIPHY refdiv/fbdiv/fbdiv-SSC/div2 sources.
- `DCIO_CLOCK_CNTL` selects a test clock and disables the display-clock-to-DCIO gate.
- `DC_REF_CLK_CNTL` selects HSYNC and genlock clock outputs.
- `UNIPHYA` through `UNIPHYE` link and channel-crossbar controls define per-channel inversion bits and 2-bit source selectors for channels 0-3.
- `DCIO_WRCMD_DELAY` exposes the UNIPHY write-command delay field.
- `DCIO_SOFT_RESET` provides one-bit soft reset fields for AUX engines, I2C DDC engines, generic GPIO, HPD, DIO, DCIO outputs, backlight, genlock, and all UNIPHY links A-E.

The GPIO and connector-detect group is broad and repetitive:

- `DC_GPIO_GENERIC_*`, `DC_GPIO_DDC1_*` through `DC_GPIO_DDC5_*`, and `DC_GPIO_DDCVGA_*` provide mask, input/action, output-enable, and output-value bit fields for generic, DDC, AUX-pad, VGA, and DDC power-down controls.
- `DC_GPIO_GENLK_*` provides mask/A/EN/Y fields for genlock, swaplock, VSYNC, and related pad enable/value controls.
- `DC_GPIO_HPD_*` defines mask, A, enable, and Y bits for HPD1-HPD5 in this DCN 3.2.1 variant. Display GPIO translation code maps HPD ids to these masks.
- `DC_GPIO_DRIVE_STRENGTH_S0/S1`, `DC_GPIO_PAD_STRENGTH_1/2`, `DC_GPIO_DRIVE_TXIMPSEL`, `DC_GPIO_TX12_EN`, `DC_GPIO_RXEN`, and `DC_GPIO_PULLUPEN` tune or enable pad electrical behavior.
- `PHY_AUX_CNTL` and `DC_GPIO_AUX_CTRL_0..5` configure AUX pad RX selection, HPD RX mode, DDC pad I2C mode, pull-ups, and AUX/DDC pad behavior used by DDC/AUX helper code.
- `AUXI2C_PAD_ALL_PWR_OK` exposes per-pad power-good status for DDC/AUX pad groups.

The UNIPHY reserved blocks define `DCIO_UNIPHY{0..4}_UNIPHY_MACRO_CNTL_RESERVED{0..57}__RESERVED_*` fields, mostly as full-register `0xFFFFFFFFL` masks. Although named reserved, they are still generated addressable fields and should be treated as opaque hardware-owned words unless an ASIC specification gives a reason to access them.

The panel and backlight group includes:

- `DC_GPIO_PWRSEQ_EN`, `DC_GPIO_PWRSEQ_CTRL`, `DC_GPIO_PWRSEQ_MASK`, and `DC_GPIO_PWRSEQ_A_Y` for GPIO-controlled panel/backlight/Vary-Bright pin ownership and values.
- `PANEL_PWRSEQ_CNTL`, `PANEL_PWRSEQ_STATE`, `PANEL_PWRSEQ_DELAY1/2`, and `PANEL_PWRSEQ_REF_DIV1/2` for panel power-up/power-down sequencing, target state readback, delays, and reference dividers.
- `BL_PWM_CNTL`, `BL_PWM_CNTL2`, `BL_PWM_PERIOD_CNTL`, and `BL_PWM_GRP1_REG_LOCK` for backlight PWM enable, polarity, period/count, group lock, and multi-panel group fields.

The DSCC0 group defines the DSC compressor control and picture-parameter-set packing:

- `DSCC0_DSCC_CONFIG0/1` exposes slice counts, ICH behavior, 4:2:0/4:2:2 mode, bits-per-component, BPG offset, native mode, and line-buffer depth controls.
- `DSCC0_DSCC_STATUS` reports idle state.
- `DSCC0_DSCC_INTERRUPT_CONTROL_STATUS` defines overflow, underflow, rate-control buffer model overflow, end-of-frame-not-reached status bits, and matching interrupt-enable bits.
- `DSCC0_DSCC_PPS_CONFIG0..18` maps DSC PPS fields including DSC version, PPS identifier, line-buffer depth, bits/component, bits/pixel, VBR/native/convert/block-pred flags, chunk size, picture and slice dimensions, initial delays, scale intervals, BPG offsets, initial/final offsets, flatness QP, rate-control model size, edge factor, quantization limits, target offsets, RC thresholds, and range QP/BPG-offset entries 0-6.
- `DSCC0_DSCC_PPS_CONFIG19` begins range entries 7-8 but is incomplete in this chunk.

## Control Flow And State Behavior

This chunk has no executable control flow. The effective control flow is in consumers:

1. DCN 3.2.1 resource initialization includes `dcn_3_2_1_offset.h` and this `dcn_3_2_1_sh_mask.h`, then expands generated register lists and field lists into per-block register/shift/mask tables.
2. Link encoder paths program `DIO_LINK*_CNTL` when selecting a transmitter's encoder type and HPO encoder instance.
3. GPIO/DDC/HPD translation code uses DDC, AUX, and HPD mask/shift fields to map logical connector services to physical pins, then register helpers read or update mask, A, EN, and Y registers.
4. Panel control and hardware sequencing code programs power-sequence controls, reads target state, stores/restores backlight-related registers, and updates BL PWM period/count/polarity fields.
5. DSC setup code writes `DSCC0_DSCC_CONFIG*` and `DSCC0_DSCC_PPS_CONFIG*` fields from computed display stream compression parameters, while interrupt/status paths can observe buffer underflow/overflow and end-of-frame errors.

The state represented here is MMIO hardware register state, not software-owned persistence. Programmed state includes DIO muxing, clock/test output selection, reset bits, GPIO ownership/enable/output values, AUX/DDC electrical modes, UNIPHY crossbar/inversion settings, panel sequencing delays and state targets, backlight PWM settings, DSC mode configuration, DSC PPS payload, and DSC interrupt enables. Volatile/readback state includes pin input values, HPD/DDC pad status, AUX/I2C power-good bits, panel power-sequence target state, DSC idle status, and DSC error occurrence bits.

Several fields are sequencing-sensitive even though they are only constants here. Soft reset bits, panel `DIGON/BLON` overrides, PWM register locks, interrupt occurrence/enable fields, HPD/DDC pin ownership bits, and DSC PPS fields should be updated through the established display helper paths so reserved and unrelated fields are preserved.

## Dependencies And Integration Points

This generated header depends on exact consistency with DCN 3.2.1 hardware register specifications and the matching offset header. `dcn321_resource.c` includes both `dcn_3_2_1_offset.h` and `dcn_3_2_1_sh_mask.h`; the resource macros combine `reg<NAME>` addresses with `<REGISTER>__<FIELD>` masks and shifts to populate the DCN register structures.

Important integration points include:

- `display/dc/resource/dcn321/dcn321_resource.c`, which imports this ASIC register namespace for DCN 3.2.1 resource construction.
- `display/dc/dio/dcn31/dcn31_dio_link_encoder.*`, where `DIO_LINKA_CNTL` through `DIO_LINKF_CNTL` fields drive the DIO PHY mux for HDMI FRL and DP 128b/132b paths.
- `display/dc/gpio/ddc_regs.h` and related GPIO translation files, which use DDC/AUX/HPD masks and shifts to build connector GPIO tables.
- `display/dc/gpio/dcn32/hw_translate_dcn32.c` and adjacent generation-specific translation files, which map logical HPD pins onto `DC_GPIO_HPD_A` masks from this family of headers.
- `display/dc/dcn31/dcn31_panel_cntl.c` and panel-control headers, which consume `PANEL_PWRSEQ_*` and backlight PWM fields for embedded panel sequencing and brightness restoration.
- DSC support under `display/dc/dsc/`, especially shared DCN DSC field-list macros that expect `DSCC0_DSCC_*` and `DSCC0_DSCC_PPS_CONFIG*` fields to exist with the generated names.

## Risks And Maintenance Notes

- Numeric drift is the main risk. A wrong shift or mask can compile cleanly but direct writes to the wrong bits, breaking link muxing, HPD/DDC/AUX behavior, panel power sequencing, backlight PWM, or DSC PPS programming only on affected hardware.
- The chunk is highly repetitive. DIO link A-F, DDC1-DDC5, HPD groups, UNIPHY0-4 reserved windows, and DSC PPS threshold/range fields are susceptible to copy-generation mistakes that are hard to notice in review.
- Boundary completeness matters. The start omits one shift from `DIO_HDMI_RXSTATUS_TIMER_CONTROL`; the end omits the rest of `DSCC0_DSCC_PPS_CONFIG19`. The final merged per-file research should describe those registers using adjacent chunks.
- Fields named `RESERVED_*` should not be written opportunistically. Many reserved UNIPHY macro-control entries are full-width masks, but callers should still treat them as opaque unless the hardware spec or generated access layer explicitly requires access.
- GPIO and panel sequencing fields interact with external connectors and embedded panels. Incorrect ownership, enable, polarity, or delay bits can present as hotplug loss, failed EDID reads, panel blanking, stuck backlight, or suspend/resume regressions.
- DSC PPS fields are protocol-visible. Incorrect values may produce visual corruption, link training failures, or sink-side DSC rejection even when the driver compiles and the MMIO write path functions.

## Test Signals

Useful validation signals for changes touching this header region are:

- Build coverage for AMDGPU display code that includes DCN 3.2.1 generated register headers, especially `dcn321_resource.c` and shared DCN DIO/GPIO/panel/DSC users.
- Static comparison against the generated register source or ASIC register specification for every `_SHIFT`/`_MASK` pair in this chunk, including repeated DDC/HPD/UNIPHY/DSC families.
- Display bring-up tests on DCN 3.2.1 hardware across DP, HDMI FRL, hotplug, EDID/DDC, AUX transactions, and HPD interrupt paths.
- Embedded panel tests covering power on/off, backlight enable, PWM brightness changes, suspend/resume, and register restore behavior.
- DSC mode tests using compressed high-bandwidth modes, including visual validation, sink acceptance, and register dumps of `DSCC0_DSCC_CONFIG*` and `DSCC0_DSCC_PPS_CONFIG*`.
- Register dump checks before and after link/panel/DSC programming to confirm reserved bits remain stable and only intended fields change.

### subset-b-002044: lines 42211-44669

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h - subset-b-002044

## Scope

- Chunk id: `subset-b-002044`
- Source lines: 42211-44669
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h`
- Observed content: 2,459 source lines with 2,135 `#define` entries, 1,070 `__SHIFT` macros, 1,065 `_MASK` macros, 282 register/block comments, and 21 visible `addressBlock` markers.

This chunk is generated AMD DCN 3.2.1 register field metadata. It does not contain executable C code, structs, enums, storage, or inline helpers. Its public interface is a preprocessor namespace of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants consumed by AMDGPU display code through generated register tables and MMIO field helpers.

## Purpose

The chunk covers a contiguous part of the DCN 3.2.1 display register mask header:

- The tail of DSC compressor 0 (`DSCC0`) picture parameter set and diagnostic fields: final rate-control range entries, memory power controls, squared-error accumulators, max absolute-error counters, rate-buffer fullness counters, and debug bus rotation.
- DSC compressor/interface/top instances 1 through 3 (`DSCC1`, `DSCC2`, `DSCC3`, `DSCCIF1`, `DSCCIF2`, `DSCCIF3`, `DSC_TOP1`, `DSC_TOP2`, `DSC_TOP3`) plus `DSCCIF0` and `DSC_TOP0` blocks. These define the hardware bit layout for Display Stream Compression configuration, PPS programming, interrupt/status bits, input format reporting, and clock/debug controls.
- HPO top-level and stream mapper fields, including clock gate controls, HPO I/O enable, and four `DP_STREAM_MAPPER_CONTROL*` link-target selectors.
- HPO HDMI stream encoder 0 blocks: `AFMT5` audio formatter, `DME5` metadata engine, and `VPG5` video packet generator.
- HPO DP stream encoder 0 blocks: `DP_STREAM_ENC0`, `APG0` audio packet generator, `DME6` metadata engine, `VPG6` video packet generator, and the beginning of `DP_SYM32_ENC0` symbol encoder controls.

The masks and shifts define how driver code inserts values into 32-bit MMIO registers and extracts status values from them. They are the contract between AMD display driver code, generated register-offset headers, and DCN 3.2.1 display hardware.

## Important APIs, Types, and Macros

There are no normal APIs or C types in this chunk. The important exported interface is the generated naming scheme:

- `REGISTER__FIELD__SHIFT` is the bit position for the least significant bit of a field.
- `REGISTER__FIELD_MASK` is the already shifted mask for that field.
- Consumers combine these with matching offset macros from `dcn_3_2_1_offset.h` and AMD display accessors such as `REG_UPDATE`, `REG_GET`, and generated `*_SF(..., mask_sh)` tables.

Important register families in this chunk include:

- `DSCC*_DSCC_CONFIG0`, `DSCC*_DSCC_CONFIG1`, and `DSCC*_DSCC_STATUS` expose DSC slice layout, ICH behavior, rate-control buffer model size, optional ICH disable, and double-buffer update pending status.
- `DSCC*_DSCC_INTERRUPT_CONTROL_STATUS` exposes overflow, underflow, rate-control buffer model overflow, end-of-frame-not-reached status, and the matching interrupt-enable bits for each compressor instance.
- `DSCC*_DSCC_PPS_CONFIG0` through `DSCC*_DSCC_PPS_CONFIG22` encode the DSC PPS register layout: DSC version, PPS identifier, line buffer depth, component depth, bits per pixel, VBR, 4:2:2/4:2:0/native modes, chunk size, picture and slice dimensions, initial delays, scale values and intervals, BPG offsets, initial/final offsets, flatness QP, RC model size, RC edge/quant/tgt offsets, 14 RC buffer thresholds, and 15 range table entries.
- `DSCC*_DSCC_MEM_POWER_CONTROL`, `*_SQUARED_ERROR_*`, `*_MAX_ABS_ERROR*`, and `*_RATE*_MAX_FULLNESS_LEVEL` expose DSC memory low-power controls and hardware diagnostic counters for compression error and rate-buffer fullness.
- `DSCCIF*_DSCCIF_CONFIG0` and `DSCCIF*_DSCCIF_CONFIG1` expose DSC input interface underflow recovery/status, pixel format, bits per component, double-buffer pending state, and picture dimensions.
- `DSC_TOP*_DSC_TOP_CONTROL` and `DSC_TOP*_DSC_DEBUG_CONTROL` expose DSC clock enable/gate controls and debug clock mux selection.
- `HPO_TOP_CLOCK_CONTROL`, `HPO_TOP_HW_CONTROL`, and `DP_STREAM_MAPPER_CONTROL0` through `3` expose HPO clock gating, HPO I/O enable, and stream-to-link mapping.
- `AFMT5_AFMT_*` registers define HDMI/DP audio formatter fields: VBI audio packet limits, layout/channel selection, DP audio stream ID, audio infoframe bytes, IEC 60958 channel status words, audio CRC control/result, ramp generator controls, audio FIFO/status acknowledgments, infoframe update source, audio source select, and AFMT memory power.
- `DME5_DME_*` and `DME6_DME_*` define metadata engine enable, HUBP requestor ID, stream type, double-buffer pending/taken status and clears, missed-transmission status and clears, and memory power controls.
- `VPG5_VPG_*` and `VPG6_VPG_*` define generic packet byte access, frame and immediate update controls for generic packet slots 0 through 14, pending bits, lock/conflict status, memory power controls, ISRC packet byte access, and MPEG infoframe fields.
- `DP_STREAM_ENC0_DP_STREAM_ENC_*` defines stream encoder clock enable/status inputs, pixel and audio source mux selectors, clock-ramp FIFO reset/enable/read-level/calibration/error state, and a spare full-width field.
- `APG0_APG_*` defines DP audio packet generator reset/enable, stream ID, channel count override, debug generator controls, packet source selections, audio CRC controls/results, status/clear bits, memory power controls, and spare fields.
- `DP_SYM32_ENC0_DP_SYM32_ENC_*` begins the 32-symbol DP encoder register set: encoder enable/reset/reset-done, pixel-to-symbol FIFO enable/reset/status, MSA and pixel-format double buffering, pixel encoding/component depth, MSA data words 0 through 8, HBLANK minimum symbol width, and repeated SDP generic stream packet controls.

## Control Flow

This file has no local runtime control flow. The runtime flow is implemented by display driver components that include this header indirectly through generated register tables:

1. A DCN 3.2.1 component selects a register offset from the matching offset header.
2. The component selects the corresponding shift and mask macros from this header.
3. AMD display MMIO helpers insert or extract bitfields through read-modify-write or readback operations.
4. Hardware interprets the resulting register value as DSC setup, packet/audio/metadata control, stream mapping, clock gating, FIFO reset, double-buffer update, or status/interrupt state.

The hardware flows implied by the fields are:

- DSC setup flows program PPS fields, slice count/dimensions, rate-control parameters, and input format before enabling compressed output paths.
- DSC error handling flows observe overflow/underflow/end-of-frame status and may enable corresponding interrupt bits.
- Double-buffered flows set update or enable bits, then poll pending/status bits before assuming new PPS, MSA, pixel-format, generic-packet, or metadata values are active.
- HPO stream routing flows map each DP stream to a link target and enable the required HPO, DP stream, HDMI stream, symbol, metadata, video packet, and audio packet clocks.
- Audio/metadata packet flows write packet bytes through indexed data registers, select sources and stream IDs, trigger frame/immediate updates, and clear taken/missed/conflict/FIFO/CRC status where required.
- DP SYM32 encoder flows reset and enable the encoder and pixel-to-symbol FIFO, program MSA/pixel format/HBLANK/GSP transmission timing, then observe reset-done, FIFO overflow, double-buffer pending, and deadline/pending status fields.

## State and Persistence Behavior

The macros are stateless compile-time constants. They describe hardware state with several lifetimes:

- Persistent configuration until reset or reprogramming: DSC PPS values, slice layout, rate-control buffer model size, input pixel format, clock gate disables, HPO I/O enable, DP stream link target, AFMT/APG source selections, stream IDs, channel enables, packet bytes, MSA data, pixel encoding format, FIFO read-start levels, HBLANK width, and memory power policies.
- Double-buffered or update-gated state: DSC double-buffer pending, DSCCIF double-buffer pending, AFMT audio/infoframe update, DME metadata double-buffer pending/taken, VPG frame/immediate update and pending bits, DP SYM32 MSA/pixel-format double-buffer controls, and repeated GSP double-buffer controls.
- Transient command or clear state: FIFO reset, APG reset, audio FIFO overflow acknowledgments, AZ audio-enable-change acknowledgments, CRC done clears, DME taken/missed clears, VPG conflict clears, metadata missed clears, GSP trigger-one-shot-send, and similar clear/status handshake bits.
- Status and diagnostic state: DSC rate-buffer overflow/underflow, end-of-frame-not-reached, rate-buffer fullness maxima, squared-error and max-absolute-error counters, input underflow status, AFMT/APG audio FIFO overflow and HBR/audio-enable status, DME pending/taken/missed status, VPG lock/conflict status, DP stream FIFO calibrated/min/max/average/error state, and SYM32 FIFO/double-buffer/deadline/pending status.
- Memory power state: DSC, AFMT, DME, VPG, and APG blocks expose low-power disable/force/state fields. These reflect block-level SRAM or small-memory power behavior rather than software persistence.

## Dependencies

This chunk depends on the AMDGPU/DCN generated register infrastructure:

- Matching register offsets in `drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h`.
- DCN 3.2.1 display code that populates register, shift, and mask tables with `SR(...)`, `DSC_SF(...)`, `SE_SF(...)`, and related macros.
- AMD display MMIO helpers such as `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, `REG_SET`, and field-list macros that expect the generated `REG__FIELD__SHIFT` and `REG__FIELD_MASK` naming convention.
- Display component implementations under `drivers/gpu/drm/amd/display/dc/dsc`, `drivers/gpu/drm/amd/display/dc/hpo`, `drivers/gpu/drm/amd/display/dc/clk_mgr`, and `drivers/gpu/drm/amd/display/dc/resource`.
- DCN 3.2.1 resource selection and DMUB ASIC identification paths that choose the correct generated register set for this ASIC generation.

The file is part of the AMDGPU display driver tree. It is not Ceph-specific despite the corpus path prefix `sources/distributed-fs/ceph-client`.

## Integration Points

Likely integration points are:

- DSC encoder creation and programming, where `DSCC*`, `DSCCIF*`, and `DSC_TOP*` fields back per-instance compressor register tables.
- Mode set and bandwidth validation paths that compute DSC PPS values and program slice, rate-control, and color-format fields before enabling compressed transport.
- DSC diagnostics and interrupt handling, where overflow, underflow, end-of-frame, squared-error, max-error, and buffer-fullness fields provide health signals.
- HPO DP stream encoder code, where `DP_STREAM_MAPPER_CONTROL*` maps streams to links and `DP_STREAM_ENC0`/`DP_SYM32_ENC0` fields configure stream source, clocks, FIFO, MSA, pixel format, HBLANK, and SDP generic stream packet scheduling.
- HDMI and DP audio paths, where `AFMT5` and `APG0` fields define audio packet generation, IEC 60958 status, channel selection, stream IDs, CRC, mute/test/status, and overflow acknowledgement behavior.
- Metadata and infoframe paths, where `DME5`, `DME6`, `VPG5`, and `VPG6` fields provide generic packet storage, double-buffer update, ISRC, MPEG, infoframe, and metadata transmission controls.
- Power-management paths, where DSC/AFMT/DME/VPG/APG memory power controls and HPO clock-gate fields must match block enable sequencing.

## Risks and Edge Cases

- Generated mask/shift drift silently corrupts MMIO field access. This is high risk for DSC PPS fields, FIFO reset/status, clock gates, stream routing, audio source selection, and packet update controls because the surrounding C code usually trusts generated constants.
- Repeated instances are nearly identical. `DSCC1`, `DSCC2`, `DSCC3`, `DSCCIF*`, `VPG5`/`VPG6`, and many `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL*` fields can be mixed up by copy/paste while still compiling.
- Chunk boundaries split logical register groups. This chunk begins in the middle of `DSCC0_DSCC_PPS_CONFIG19` and ends in the middle of `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL13`; adjacent chunks are required for a complete per-file view.
- Some status and clear bits are adjacent or similarly named. Incorrect read-modify-write handling can lose events for audio FIFO overflow, CRC done, metadata taken/missed, VPG conflict, DSC buffer overflow/underflow, and GSP transmission deadline/pending state.
- Double-buffer pending bits require sequencing. Programming MSA, pixel format, DSC PPS, VPG generic packet bytes, or metadata fields without waiting for pending bits to drain can cause stale packets or visible mode-set artifacts.
- PPS range and threshold fields are narrow and packed. Values must be range-checked before shifting; otherwise high bits can bleed into adjacent QP, BPG offset, threshold, or chunk-size fields.
- Full-width diagnostic fields such as squared-error counters and MSA data fields use `0xFFFFFFFFL`; callers need to know whether a register is writable data, read-only status, or latched diagnostic state before writing it.
- Memory power force/disable/state fields are easy to misuse across low-power transitions. Forcing memory on or off in one display block can affect resume, blanking, or metadata/audio packet delivery if not restored.
- Clock gate disable fields have inverted semantics. A field named `*_GATE_DIS` enables or disables gating rather than the clock itself, so call sites must distinguish clock enable from gate override.

## Test Signals

Useful validation signals for code using this chunk:

- Compile coverage for DCN 3.2.1 display with `dcn_3_2_1_sh_mask.h` and the matching offset header to catch missing or renamed generated fields.
- Generated consistency checks that every visible non-empty register field has matching `__SHIFT` and `_MASK` definitions, masks align with shifts, and fields in the same register do not overlap unexpectedly.
- Unit or static tests for representative packed fields: DSC bits-per-pixel, picture/slice dimensions, RC thresholds, range min/max QP and BPG offsets, AFMT channel enable, APG stream ID, FIFO read levels, DP stream link target, pixel encoding/component depth, and GSP transmission line number.
- Hardware smoke tests for DSC enable/disable, DSC-compressed modes, multi-slice modes, native 4:2:2/4:2:0 paths, hotplug, suspend/resume, and link recovery.
- DisplayPort HPO tests that verify stream-to-link mapping, SYM32 reset/reset-done, pixel-to-symbol FIFO reset/enable, MSA programming, HBLANK width, and SDP generic packet scheduling.
- HDMI/DP audio tests that verify AFMT/APG audio enable, stream ID, channel layout, IEC 60958 data, HBR status, CRC done/clear, and FIFO overflow acknowledgement.
- Metadata and packet tests that exercise VPG generic packet frame/immediate updates, pending bits, lock/conflict status, ISRC and MPEG packet data, and DME taken/missed clear handling.
- Power-management tests that read back DSC/AFMT/DME/VPG/APG memory power state and HPO clock gate behavior across idle, blank, suspend, and resume transitions.

## Chunk Boundary Notes

The first visible lines complete `DSCC0_DSCC_PPS_CONFIG19`, whose earlier range-min shift fields are in the previous chunk. The last visible line is inside `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL13`; the rest of that repeated GSP control register and later DP SYM32 fields are expected in the following chunk. The merge/reconciliation lane should combine this report with adjacent chunks before producing the final per-file research document for `dcn_3_2_1_sh_mask.h`.

### subset-b-002045: lines 44670-47065

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 44670-47065

## Scope

This chunk is a generated AMD DCN 3.2.1 register-field shift/mask slice. It contains preprocessor constants only: 2,139 `#define` entries for bit positions and bit masks across 213 register groups. There are no C functions, structs, enums, branches, allocations, locks, direct MMIO operations, or durable-storage operations in this range.

The chunk begins in the middle of `DP_SYM32_ENC0_DP_SYM32_ENC_SDP_GSP_CONTROL13`, covers the tail of HPO `DP_SYM32_ENC0`, then covers repeated HPO DisplayPort stream encoder blocks for stream instances 1 and 2, and continues into stream instance 3. It ends in the middle of `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL6`; the remaining fields for that register and the rest of encoder 3 are in the next manifest chunk. Final file-level conclusions need to merge this with neighboring chunks.

## Purpose And Hardware Surface

This header is part of the AMDGPU Display Core register ABI for DCN 3.2.1. The paired `dcn_3_2_1_offset.h` file supplies MMIO register offsets; this `*_sh_mask.h` file supplies field shifts and unshifted 32-bit masks used by register helper macros to read, write, and wait on individual fields.

The hardware surface in this slice is centered on the HPO DisplayPort stream path:

- Tail of `DP_SYM32_ENC0`: generic secondary-data packet controls, SDP stream/audio controls, metadata packet controls, video MSA/VBID/stream controls, panel replay tunneling optimization, video CRC, memory power, and spare bits.
- `DP_STREAM_ENC1`, `DP_STREAM_ENC2`, and `DP_STREAM_ENC3`: stream encoder clock enable/status fields, pixel/audio input mux selectors, clock ramp adjuster FIFO control/status, FIFO calibration/read-level fields, and spare fields.
- `APG1`, `APG2`, and `APG3`: audio packet generator reset, enable, stream ID, debug audio generation, packet source selection, audio CRC control/result/status, FIFO overflow status/clear, output active status, memory power controls, and spare fields.
- `DME7`, `DME8`, and `DME9`: metadata engine requestor ID, engine enable, stream type, double-buffer pending/taken/clear/disable state, missed-transmission status/clear, and memory power controls.
- `VPG7`, `VPG8`, and `VPG9`: video packet generator generic packet data access, generic packet payload bytes, frame-update and immediate-update controls for generic packet slots 0-14, update-pending bits, conflict status/clear, memory power state, ISRC data access, and MPEG infoframe fields.
- `DP_SYM32_ENC1` and `DP_SYM32_ENC2`: full symbol encoder instances for video/SDP/audio/metadata, including reset/enable, pixel-to-symbol FIFO, MSA double-buffering, pixel format, MSA data words, HBlank minimum symbol width, 15 GSP control registers, audio mute/packet enables, metadata packet timing, stream/VBID controls, panel replay tunneling, CRC, memory power, and spare fields.
- Beginning of `DP_SYM32_ENC3`: reset/enable, video FIFO, MSA and pixel-format double buffering, pixel format, MSA data words, HBlank control, and GSP control registers 0 through part of 6.

The repeated instance pattern is deliberate. The generated names encode both block type and instance number, for example `VPG8_VPG_GSP_FRAME_UPDATE_CTRL__VPG_GENERIC12_FRAME_UPDATE_PENDING_MASK` or `DP_SYM32_ENC2_DP_SYM32_ENC_VID_STREAM_CONTROL__VID_STREAM_ENABLE_MASK`. This lets one set of runtime helper structures select the proper offsets and masks for each stream instance.

## Important Definitions

The naming convention is consistent across this chunk:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted 32-bit mask for the field.
- `//<REGISTER>` comments group field macros by register.
- `// addressBlock: ...` comments mark generated hardware address-block boundaries such as `dce_dc_hpo_dp_stream_enc1_dispdec`, `dce_dc_hpo_dp_stream_enc1_apg_apg_dispdec`, `dce_dc_hpo_dp_stream_enc1_dme_dme_dispdec`, `dce_dc_hpo_dp_stream_enc1_vpg_vpg_dispdec`, and the corresponding stream 2 and stream 3 blocks.

Important register families in this chunk:

- `DP_STREAM_ENC*_DP_STREAM_ENC_CLOCK_CONTROL` defines `DP_STREAM_ENC_CLOCK_EN` and clock-on status bits for `DISPCLK`, `SOCCLK`, `DPSTREAMCLK`, and `SYMCLK32`.
- `DP_STREAM_ENC*_DP_STREAM_ENC_INPUT_MUX_CONTROL` and `DP_STREAM_ENC*_DP_STREAM_ENC_AUDIO_CONTROL` define 3-bit pixel and audio stream source selectors.
- `DP_STREAM_ENC*_DP_STREAM_ENC_CLOCK_RAMP_ADJUSTER_FIFO_STATUS_CONTROL0/1` define FIFO enable/reset/read-start-level/read-clock-source/status/error fields and calibration/overwrite/min/max/average-level fields.
- `APG*_APG_CONTROL` and `APG*_APG_CONTROL2` define APG reset/done, enable, DisplayPort audio stream ID, and ASP channel-count override.
- `APG*_APG_DBG_GEN_CONTROL`, `APG*_APG_PACKET_CONTROL`, `APG*_APG_AUDIO_CRC_CONTROL*`, `APG*_APG_AUDIO_CRC_RESULT`, and `APG*_APG_STATUS*` define audio debug generation, ACP/audio-info source selection, audio CRC start/count/channel/result/done/clear, audio/HBR enable status, FIFO overflow status/clear, and output active state.
- `DME*_DME_CONTROL` defines metadata request routing and double-buffer lifecycle fields: `METADATA_HUBP_REQUESTOR_ID`, `METADATA_ENGINE_EN`, `METADATA_STREAM_TYPE`, `METADATA_DB_PENDING`, `METADATA_DB_TAKEN`, `METADATA_DB_TAKEN_CLR`, `METADATA_DB_DISABLE`, `METADATA_TRANSMISSION_MISSED`, and `METADATA_TRANSMISSION_MISSED_CLR`.
- `VPG*_VPG_GENERIC_PACKET_ACCESS_CTRL` and `VPG*_VPG_GENERIC_PACKET_DATA` define indexed writes of four generic packet bytes at a time.
- `VPG*_VPG_GSP_FRAME_UPDATE_CTRL` and `VPG*_VPG_GSP_IMMEDIATE_UPDATE_CTRL` define update request and pending bits for generic packet slots 0-14, split between low update bits and high pending bits.
- `VPG*_VPG_GENERIC_STATUS` defines lock/conflict status and conflict clear fields.
- `VPG*_VPG_ISRC1_2_*` and `VPG*_VPG_MPEG_INFO*` define indexed ISRC payload bytes and MPEG infoframe/checksum/update fields.
- `DP_SYM32_ENC*_DP_SYM32_ENC_CONTROL` defines symbol encoder enable/reset/reset-done.
- `DP_SYM32_ENC*_DP_SYM32_ENC_VID_FIFO_CONTROL` defines pixel-to-symbol FIFO enable/reset/reset-done/overflow.
- `DP_SYM32_ENC*_DP_SYM32_ENC_VID_PIXEL_FORMAT` defines DP 2.0-style pixel encoding, uncompressed encoding, and component depth fields.
- `DP_SYM32_ENC*_DP_SYM32_ENC_VID_MSA0` through `VID_MSA8` carry 32-bit MSA data words, while `VID_MSA_CONTROL` and `VID_MSA_DOUBLE_BUFFER_CONTROL` control MSA line timing, stereo override, and double-buffer state.
- `DP_SYM32_ENC*_DP_SYM32_ENC_SDP_GSP_CONTROL0-14` define per-generic-packet transmission policy: video/idle continuous transmission enables, one-shot trigger and trigger position, double-buffer enable/pending, payload size, SOF reference, transmission deadline missed/pending, and transmission line number.
- `DP_SYM32_ENC*_DP_SYM32_ENC_SDP_AUDIO_CONTROL0/1` define ASP/ATP/AIP/ACM/ISRC enables, ASP priority, ATP version, audio mute/status, and ASP concatenation sample-count controls for 2-channel, 8-channel, and HBR layouts.
- `DP_SYM32_ENC*_DP_SYM32_ENC_SDP_METADATA_PACKET_CONTROL` defines metadata packet enable, double-buffer enable/pending, SOF reference, and transmission line number.
- `DP_SYM32_ENC*_DP_SYM32_ENC_VID_STREAM_CONTROL`, `VID_VBID_CONTROL`, `VID_PANEL_REPLAY_CONTROL`, `VID_CRC_*`, and `MEM_POWER_CONTROL` define stream enable/status, compressed-stream VBID timing, panel replay tunneling optimization, video CRC control/result/valid state, and local memory low-power state.

## Control Flow And Runtime Behavior

This chunk has no executable control flow by itself. Runtime behavior appears when Display Core code includes `dcn_3_2_1_sh_mask.h`, initializes typed register shift/mask tables, and calls register helpers such as `REG_UPDATE`, `REG_UPDATE_2`, `REG_WAIT`, and generated field macros such as `SE_SF(...)`.

The DCN321 resource path includes this header in `drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c` together with `dcn_3_2_1_offset.h`. That file initializes the HPO stream encoder, VPG, APG, stream encoder, and other register tables with macros such as `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST(__SHIFT)`, `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST(_MASK)`, `DCN3_VPG_MASK_SH_LIST(__SHIFT)`, and `DCN31_APG_MASK_SH_LIST(_MASK)`.

The main runtime flows that consume fields in this chunk include:

1. Resource construction maps generated offsets plus these shift/mask values into per-instance structures for HPO DP stream encoders, VPGs, APGs, and stream encoders.
2. HPO DP stream enable paths turn on `DP_STREAM_ENC_CLOCK_EN`, reset and enable `DP_SYM32_ENC`, route the input mux, enable the video stream, reset/enable the pixel-to-symbol FIFO, reset/enable the clock-ramp-adjuster FIFO, and optionally enable video CRC diagnostics.
3. Stream attribute programming uses `DP_SYM32_ENC_VID_PIXEL_FORMAT`, MSA data registers, MSA double buffering, VBID compressed stream timing, HBlank symbol width, metadata packet controls, and GSP packet controls.
4. Blank/disable paths clear `VID_STREAM_ENABLE`, wait on `VID_STREAM_STATUS`, disable SDP transmission, disable FIFOs, and eventually disable the symbol encoder and stream encoder clocks.
5. VPG paths write generic packet payload bytes through indexed access registers, then request frame-bound or immediate update for generic packet slots and monitor conflict/pending status.
6. APG paths reset/enable audio packet generation, assign DisplayPort audio stream IDs, configure debug generation and audio CRC, and monitor audio enable/HBR/FIFO overflow/output-active state.
7. DME paths enable metadata delivery from a selected HUBP requestor, use metadata double-buffer state, and clear taken or missed-transmission status.

## State And Persistence Behavior

The state represented here is hardware register state, not driver-owned persistent data. It persists only as long as the relevant display hardware remains powered and configured, and can be reset or overwritten by modesets, link retraining, hotplug handling, power gating, suspend/resume, or firmware/display microcontroller activity.

Programmed state includes:

- Stream encoder clock enables, mux selections, FIFO read levels, FIFO overwrite/calibration controls, and symbol encoder enable/reset state.
- Video stream enable, pixel format, MSA data words, MSA and pixel-format double-buffer enables, HBlank minimum symbol width, and compressed-stream VBID timing.
- SDP stream enable, GSP transmission policy, GSP payload size, SOF references, line numbers, metadata packet enable/timing, and audio packet enables/mute.
- APG enable, DP audio stream ID, debug generation, packet source selection, audio CRC parameters, and APG memory power controls.
- DME metadata requestor ID, engine enable, stream type, DB disable, and DME memory power controls.
- VPG generic packet bytes, packet update requests, ISRC data bytes, MPEG info fields, and VPG memory power controls.

Volatile readback/status includes:

- FIFO reset done, video stream active, FIFO error, FIFO min/max/average/calibrated status, `VID_STREAM_STATUS`, CRC valid/results, audio mute status, and memory power state.
- GSP trigger-pending, double-buffer-pending, and deadline-missed fields.
- APG reset done, audio/HBR enable status, FIFO overflow status, output active state, audio CRC done/result, and memory power state.
- DME DB pending/taken, metadata transmission missed, and memory power state.
- VPG generic lock/conflict status and update-pending bits for frame and immediate packet updates.

Side-effecting fields need special care: reset toggles, status clear bits such as `APG_AUDIO_FIFO_OVERFLOW_STATUS_CLEAR`, `APG_AUDIO_CRC_DONE_CLEAR`, `METADATA_DB_TAKEN_CLR`, `METADATA_TRANSMISSION_MISSED_CLR`, `VPG_GENERIC_CONFLICT_CLR`, one-shot GSP triggers, update requests, FIFO recalibration/recompute controls, and memory-power force fields can change hardware state when written.

## Dependencies And Integration Points

This chunk depends on generated-name consistency across the DCN 3.2.1 register header set. The register names in this file must match offsets in `dcn_3_2_1_offset.h` and the field names expected by Display Core mask-list macros. A missing macro is usually a compile-time failure; a wrong numeric shift or mask can compile and fail only on real hardware.

Primary integration points include:

- `drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`, which includes `dcn_3_2_1_sh_mask.h` and builds DCN321 register, shift, and mask tables.
- `drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h`, where `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST` consumes `DP_STREAM_ENC0_*` and `DP_SYM32_ENC0_*` field names from generated headers and maps them into reusable per-instance field structures.
- `drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.c`, which uses the HPO stream encoder register helpers for clock enable, reset/wait, FIFO reset/enable, stream enable/status, pixel format, MSA, SDP, metadata, audio, and CRC operations.
- `drivers/gpu/drm/amd/display/dc/dcn30/dcn30_vpg.h` and VPG implementation code, which consume `VPG*_VPG_*` fields for generic packet payload writes, update triggering, and conflict handling.
- `drivers/gpu/drm/amd/display/dc/dcn31/dcn31_apg.h` and APG implementation code, which consume `APG*_APG_*` fields for HPO audio packet generation.
- Shared register helper infrastructure in `reg_helper.h`, where `_SHIFT` and `_MASK` constants become typed values used by `REG_*` macros.

The generated instance-0 mask lists often reference `DP_STREAM_ENC0_*`, `DP_SYM32_ENC0_*`, `VPG0_*`, or `APG0_*` field names and then reuse those shift/mask values for other instances through per-instance offset tables. This works only if the repeated hardware instances keep identical field layouts. This chunk shows repeated layouts for stream/APG/VPG/DME/SYM32 instances 1-3, so it is a useful cross-check against the instance-0 definitions in earlier chunks.

## Risks And Maintenance Notes

- Numeric drift in these generated constants is the highest risk. Incorrect masks for stream enables, reset-done bits, FIFO controls, packet update requests, metadata DB clears, or audio CRC/status fields can compile cleanly and produce runtime-only display/audio/metadata failures.
- The chunk boundaries split real register groups. `DP_SYM32_ENC0_SDP_GSP_CONTROL13` is partial at the start, and `DP_SYM32_ENC3_SDP_GSP_CONTROL6` is partial at the end. Any audit that checks field completeness must include adjacent chunks.
- Repeated instance families create copy-generation hazards. `DP_STREAM_ENC1/2/3`, `APG1/2/3`, `DME7/8/9`, `VPG7/8/9`, and `DP_SYM32_ENC1/2/3` are similar, but code may still rely on a subset of instance-0 fields. Cross-instance differences must be intentional and verified against the hardware register database.
- GSP and VPG update controls are timing-sensitive. Wrong update or pending masks can leave stale HDR/metadata/generic packets active, miss a frame update, or trigger a packet at the wrong time.
- Metadata and audio clear bits are side-effecting. A bad clear mask can hide metadata transmission misses, leave `DB_TAKEN` asserted, clear the wrong APG FIFO overflow, or make CRC diagnostics unreliable.
- FIFO reset and calibration fields are in display timing paths. Bad reset-done, enable, level, or error masks can cause black screens, intermittent stream start failures, or timing-dependent failures after modeset and resume.
- Memory-power force/default/state fields appear for APG, DME, VPG, and SYM32 blocks. Wrong masks can cause excess power draw, inaccessible memories during packet updates, or failures only around clock/power transitions.
- Panel replay tunneling and compressed-stream VBID fields are user-visible only on specific panels or compressed stream configurations, so regressions may escape basic display tests.

## Test Signals

Useful validation should combine build-time checks with DCN321 hardware behavior:

- Build AMDGPU Display Core with DCN321 enabled and confirm `dcn321_resource.c` resolves `dcn_3_2_1_sh_mask.h` and all HPO stream encoder, VPG, APG, and DME mask-list fields.
- Run generated-header consistency checks for this range: paired `_SHIFT`/`_MASK` definitions, 32-bit mask width, no unexpected field overlap within a register, and expected repeated layouts across instances 1, 2, and 3.
- Exercise HPO DisplayPort stream enable/blank/disable on streams backed by `DP_STREAM_ENC1`, `DP_STREAM_ENC2`, and `DP_STREAM_ENC3`; monitor reset-done bits, `VID_STREAM_STATUS`, FIFO reset/enable state, and FIFO error fields.
- Validate stream attribute changes across RGB, YCbCr444, YCbCr422, YCbCr420, 8/10/12 bpc, compressed stream, and double-buffered updates; watch MSA/pixel-format pending behavior and VBID compressed-stream timing.
- Test SDP and GSP packet delivery with HDR metadata, adaptive sync metadata, DSC-related packets, audio sample/timestamp packets, and generic packet slots 0-14; monitor GSP pending, double-buffer pending, deadline-missed, and VPG update-pending/conflict signals.
- Validate APG audio paths with basic audio, HBR audio where available, stream ID changes, audio mute/unmute, FIFO overflow status/clear, and APG audio CRC done/result handling.
- Exercise DME metadata flows with multiple HUBP requestor IDs, metadata stream types, double-buffer update/taken/clear behavior, DB disable, and missed-transmission clear/status.
- Stress power transitions: display idle, blank/unblank, hotplug, suspend/resume, and power gating while checking APG/DME/VPG/SYM32 memory power state fields and packet/FIFO recovery.
- Use CRC and status diagnostics: video CRC valid/result fields, APG audio CRC result, VPG generic conflict status, FIFO calibrated/min/max/error state, metadata missed status, and GSP deadline-missed bits before and after modesets and packet updates.

## Chunk-Specific Summary

Lines 44670-47065 define DCN 3.2.1 bit shifts and masks for the tail of HPO symbol encoder 0, full stream/APG/DME/VPG/SYM32 coverage for stream instances 1 and 2, and the beginning of stream instance 3. The content is generated register ABI rather than executable logic. Correctness depends on exact numeric field values, instance-prefix consistency, careful handling of side-effecting reset/clear/update/trigger fields, and validation across HPO DisplayPort stream bring-up, packet generation, metadata, audio, FIFO, CRC, and power-management scenarios.

### subset-b-002046: lines 47066-49630

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 47066-49630

## Scope

This chunk is a generated AMD DCN 3.2.1 register shift/mask slice. It contains preprocessor constants only: `_SHIFT` macros define field least-significant bit positions and `_MASK` macros define field masks already positioned within the register. `//<REGISTER>` comments group the constants by hardware register, and `// addressBlock:` comments identify the indexed or MMIO register block being described.

There are no C functions, structs, enums, loops, branches, allocation paths, locking primitives, direct MMIO calls, or persistent data structures in this range. Runtime behavior comes from AMDGPU Display Core code that includes this header together with matching offset headers and uses the constants through register helper macros.

The range starts in the middle of `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL6`; the shifts and early masks for that register are in the preceding chunk. It ends on the comment for `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL4_ENABLE`; that register's field definitions begin in the next chunk. The final per-file reconciliation should merge adjacent chunks before treating either boundary register as complete.

## Purpose And Hardware Surface

The file is the `sh_mask` companion for DCN 3.2.1 display hardware register definitions. The macros let display and audio code compose writes and decode reads without hardcoding bit positions. This chunk spans two major surfaces:

- High-performance DisplayPort output pieces: the tail of DP Sym32 encoder 3 secondary-data-packet control, HPO DP link encoder 0/1 clock/spare controls, and DP DPHY Sym32 instances 0/1.
- Display audio and legacy display compatibility pieces: the HDA/Azalia controller, HDA endpoints, output stream descriptors 0-7, legacy VGA indexed sequencer/CRT/graphics/attribute registers, HDMI/DP codec endpoint controls, audio descriptors, sink info storage, audio CRC result blocks, and the start of the Azalia input codec endpoint.

The chunk defines 2,074 `#define` lines and 435 comment/group lines. Its address blocks are:

- `dce_dc_hpo_dp_link_enc0_dispdec` and `dce_dc_hpo_dp_link_enc1_dispdec` for HPO DP link encoder clock control.
- `dce_dc_hpo_dp_dphy_sym320_dispdec` and `dce_dc_hpo_dp_dphy_sym321_dispdec` for DP 32-symbol physical/link scheduling, test pattern, error, symbol override, and CRC fields.
- `dce_dc_hda_azcontroller_azdec`, `azendpoint`, `azinputendpoint`, `azroot`, and `azstream0` through `azstream7` for HD Audio command rings, response rings, immediate command interfaces, DMA position buffers, wall clock, endpoints, and stream descriptors.
- `vga_vgaseqind`, `vga_vgacrtind`, `vga_vgagrphind`, and `vga_vgaattrind` for legacy VGA indexed register bit layouts.
- `azendpoint_f2codecind`, `azendpoint_descriptorind`, and `azendpoint_sinkinfoind` for display codec converter, pin widget, audio descriptor, and sink metadata controls.
- `azf0controller_azinputcrc0resultind`, `azinputcrc1resultind`, `azcrc0resultind`, and `azcrc1resultind` for per-channel audio CRC readback.
- `azinputendpoint_f2codecind` for the beginning of input codec converter and input pin controls.

## Important Definitions

The generated API pattern is consistent throughout this chunk:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the corresponding mask in register position.
- Full-width fields use masks such as `0xFFFFFFFFL`; one-bit controls and statuses use single-bit masks.

Important DisplayPort definitions include:

- `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL6` through `GSP_CONTROL14` define Generic SDP enable, idle/video continuous transmission, one-shot trigger, double-buffer, payload size, start-of-frame reference, pending/deadline status, and line-number fields. `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_CONTROL` adds SDP stream enable, GSP0 priority, and CRC16 enable.
- `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_AUDIO_CONTROL0/1` cover audio secondary packet enables for ASP/ATP/AIP/ACM/ISRC, ASP priority, ATP version, audio mute/status, and ASP concatenation sample-count limits.
- `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_METADATA_PACKET_CONTROL`, `VID_MSA_CONTROL`, `VID_VBID_CONTROL`, `VID_STREAM_CONTROL`, `VID_PANEL_REPLAY_CONTROL`, and `VID_CRC_*` define metadata packet double buffering, MSA/VBID line timing, video stream enable/defer/status, panel replay tunneling optimization, video CRC enable/continuous mode/results/valid, memory power control, and spare fields.
- `DP_LINK_ENC0/1_DP_LINK_ENC_CLOCK_CONTROL` provide HPO link encoder clock enable and `SYMCLK32` clock-on fields.
- `DP_DPHY_SYM320/321_DP_DPHY_SYM32_*` define DPHY enable/reset/precoder/mode/lane-count, status and update-pending bits, virtual-channel rate controls, scheduler allocation table stream-source/slot-count fields, test pattern selection/PRBS seed/custom-symbol registers, error status bits, per-stream symbol override, and DPHY CRC configuration/status/count.

Important HDA/Azalia controller definitions include:

- `CORB_*` and `RIRB_*` fields describe command output ring and response input ring write/read pointers, resets, DMA enables, memory/overrun/response interrupt controls and statuses, ring base addresses, response interrupt count, and supported ring sizes.
- `IMMEDIATE_COMMAND_OUTPUT_INTERFACE`, `IMMEDIATE_RESPONSE_INPUT_INTERFACE`, and `IMMEDIATE_COMMAND_STATUS` define immediate verb/response data paths, index fields, busy state, immediate response status, and unsolicited-response flags.
- `DMA_POSITION_LOWER/UPPER_BASE_ADDRESS` and `WALL_CLOCK_COUNTER_ALIAS` expose DMA position-buffer base and wall-clock counter fields.
- Endpoint, input-endpoint, and root immediate-command registers repeat data/index fields for scoped HDA access.
- `AZSTREAM0` through `AZSTREAM7_OUTPUT_STREAM_DESCRIPTOR_*` repeat a stream descriptor layout covering traffic priority, stripe control, descriptor error/FIFO completion/status/interrupt enables, stream reset/run bits, link position in current buffer, cyclic buffer length, last valid index, FIFO size, stream format, BDL pointer lower/upper base address, and link-position aliases.

Important legacy VGA definitions include:

- Sequencer registers `SEQ00` through `SEQ04` define synchronous/asynchronous reset, clocking mode, plane write mask, character-map select, and memory mode fields.
- CRT controller registers `CRT00` through `CRT22` include horizontal/vertical timing totals, display end, blanking and retrace starts/ends, cursor start/end/location, start address, offset, underline location, mode control, line compare, readback data, and memory mapping fields.
- Graphics controller registers `GRA00` through `GRA08` define set/reset, enable set/reset, color compare, rotate/function select, read map, mode, miscellaneous, color-dont-care, and bit mask fields.
- Attribute controller registers `ATTR00` through `ATTR14` define palette entries, mode control, overscan color, color plane enable, horizontal pixel panning, color select, and reserved fields.

Important codec endpoint definitions include:

- `AZALIA_F2_CODEC_CONVERTER_*` defines converter format, channel/stream ID, digital converter flags, stripe control, ramp rate, GTC embedding, audio widget capabilities, supported size/rate masks, and stream formats.
- `AZALIA_F2_CODEC_PIN_CONTROL_*` covers connection list entry, widget output enable, unsolicited response tag/enable, pin sense impedance/presence, default configuration fields, speaker/channel allocation, downmix and audio descriptor access, multichannel enable/mute/channel ID pairs, lipsync, high bit rate capability, audio sink info index/data, channel status override words, pin association, digital output status, LPIB snapshot/LPIB/timer snapshot, coding type, format-changed status, wireless display identification, remote keepalive, and pin capability parameters.
- `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13` provide per-descriptor sample-rate/bit-depth/channel fields and descriptor enable bits.
- `AZALIA_F2_CODEC_PIN_CONTROL_MANUFACTURER_ID`, `PRODUCT_ID`, `SINK_DESCRIPTION_LEN`, `PORTID0/1`, and `SINK_DESCRIPTION0` through `SINK_DESCRIPTION17` define sink metadata storage.
- `AZALIA_INPUT_CRC*` and `AZALIA_CRC*` channel registers are full-width CRC result fields for channels 0-7 across input and output CRC result banks.
- `AZALIA_F2_CODEC_INPUT_*` begins the input converter and input pin controls for converter format, channel/stream ID, digital converter flags, input widget capabilities, supported sizes/rates, stream formats, input enable, unsolicited response, pin sense, configuration default fields, channel allocation, and multichannel 0/2 enable/mute/channel ID fields.

## Control Flow And State Behavior

This chunk has no executable control flow. The effective control flow is in callers that combine these constants with generated register offsets and AMDGPU register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, or lower-level MMIO/indexed-register accessors.

Typical runtime flows enabled by these definitions are:

1. DisplayPort stream setup programs SDP, audio packet, metadata, MSA/VBID, video stream, panel replay, and CRC fields on DP Sym32 encoder 3.
2. HPO link bring-up enables link encoder clocks and configures DPHY mode, lane count, scheduler allocation table state, virtual-channel rates, test pattern generation, symbol overrides, and CRC diagnostics for DPHY instances 0 and 1.
3. Link diagnostics poll DPHY status, rate/SAT update pending bits, error status, CRC done/value/count fields, and video CRC result/valid fields.
4. HDA controller initialization configures CORB/RIRB base addresses, pointers, ring sizes, DMA enables, interrupt controls, immediate command paths, DMA position buffer, and wall-clock reads.
5. Audio playback streams configure stream descriptor control/status, cyclic buffer length, last valid index, FIFO size, stream format, BDL base address, and current link position for stream descriptors 0-7.
6. Codec verb handling reads or writes converter format, stream ID, pin widget control, unsolicited response, pin sense, default configuration, channel/speaker allocation, audio descriptors, sink info, and remote keepalive state.
7. Input audio paths use the input codec converter and pin controls to configure input stream format, digital converter metadata, input enable, presence sense, and multichannel input routing.
8. Legacy VGA compatibility paths can use the indexed VGA definitions to preserve or decode sequencer, CRTC, graphics, and attribute register state during modeset, resume, or VGA handoff.

The state represented here is hardware register state:

- Programmed state includes DP SDP/audio/metadata/video enables, DPHY enable/reset/mode/lane count, VC rates, SAT slot assignments, test patterns, symbol override controls, HDA ring base addresses and DMA enables, stream descriptor formats and BDL pointers, codec converter and pin controls, audio descriptor data, sink metadata, and VGA indexed-register fields.
- Volatile readback includes SDP/GSP pending/deadline bits, video stream status, CRC valid/results, DPHY current mode/update-pending/error/CRC status, CORB/RIRB and immediate-command status, stream FIFO/status/link position, pin presence sense, digital output status, LPIB snapshots, format-changed status, keepalive state, and per-channel CRC values.
- Sequencing-sensitive fields include one-shot SDP triggers, double-buffer pending bits, stream enable/defer controls, DPHY reset and SAT update, CRC reset/start/end event selection, CORB/RIRB pointer resets, stream reset/run bits, interrupt status/clear-style fields, unsolicited-response enable, and LPIB snapshot controls.

## Dependencies And Integration Points

The definitions depend on exact consistency with the DCN 3.2.1 hardware register specification and matching generated offset headers. Compilation can catch missing macro names, but wrong numeric shifts or masks may still compile and only fail on hardware.

Key integration points are:

- AMDGPU Display Core DisplayPort and HPO link code that configures DP Sym32 encoders, link encoder clocks, DPHY mode/lane scheduling, SDP packets, video timing metadata, panel replay, and CRC diagnostics.
- Display audio code and the Linux HDA/DRM audio integration that configure Azalia controller rings, immediate commands, stream descriptors, codec widgets, channel allocation, sink info, and audio descriptors.
- Hotplug, modeset, suspend/resume, link retrain, and audio stream start/stop paths that need stable register programming across resets and power transitions.
- Firmware or diagnostic tooling that dumps DPHY errors/CRC values, video CRC, audio CRC banks, HDA ring state, stream positions, pin sense, sink metadata, and VGA compatibility state.
- Register dump and hardware validation scripts that expect generated `*_SHIFT` and `*_MASK` names to align with the DCN 3.2.1 offset namespace.

## Risks And Maintenance Notes

- Numeric drift is the main risk. A single incorrect shift or mask can route writes to the wrong hardware field, corrupting link setup, packet scheduling, HDA DMA, stream descriptor programming, codec verb responses, or legacy VGA restore.
- Repetition increases copy/paste risk. The DPHY 0/1 blocks, stream descriptor 0-7 blocks, audio descriptor 0-13 blocks, sink description 0-17 blocks, and CRC channel 0-7 blocks are intentionally patterned; one mismatched instance can affect only a specific link, stream, descriptor, or channel.
- Several fields are one-bit strobes or reset-like controls. SDP one-shot triggers, DPHY reset/CRC reset, SAT update, CORB/RIRB pointer resets, stream reset/run, interrupt status/control bits, and LPIB snapshot controls are sensitive to ordering and write semantics in callers.
- Reserved and full-width fields should be preserved unless the hardware specification says otherwise. This header documents bit packing; it does not make reserved bits safe to write.
- The HDA stream descriptor and ring fields describe DMA-facing state. Wrong base address, pointer, length, or enable masks can cause stream underruns, missing audio interrupts, stale position reporting, or DMA faults.
- Boundary completeness matters for this chunk. `GSP_CONTROL6` and `MULTICHANNEL4_ENABLE` are split across chunk boundaries and should be documented as complete only in the merged per-file report.

## Test Signals

Useful validation signals for changes touching these macros are mostly build-time and hardware-facing:

- Build coverage for AMDGPU Display Core and display audio code that includes `dcn_3_2_1_sh_mask.h` and references DP Sym32, HPO DPHY, HDA/Azalia, VGA, or codec endpoint fields.
- Static comparison against generated register collateral or the DCN 3.2.1 hardware specification for every `_SHIFT`/`_MASK` pair in the affected register families.
- DisplayPort bring-up, hotplug, retrain, suspend/resume, panel replay, MST or multi-stream scheduling, SDP/audio packet, and CRC diagnostic testing on DCN 3.2.1 hardware.
- Audio playback tests across HDA streams 0-7, including stream start/stop, format changes, channel allocation, HBR paths, LPIB position reporting, DMA position buffer reads, and unsolicited response handling.
- Codec and sink-info validation that checks pin sense, EDID-derived audio descriptors, speaker/channel allocation, sink description/manufacturer/product/port IDs, remote keepalive, and format-changed status.
- Register dump comparisons before and after modeset/audio start/resume to verify intended fields change, volatile status behaves as expected, and reserved bits remain stable.

### subset-b-002047: lines 49631-52079

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 49631-52079

## Scope

This chunk is a generated AMD DCN 3.2.1 shift/mask header slice. It contains preprocessor constants only: register grouping comments, `_SHIFT` macros for field bit positions, and `_MASK` macros for register-positioned field masks. There are no C functions, structs, enums, branches, loops, allocations, locks, or direct file-backed persistence in this range.

The requested range covers 2,449 source lines, 2,033 `#define` lines, and 374 register or address-block comments. It starts in the middle of the `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL4_ENABLE` family, covers the remaining F2 input-pin audio fields, the F2 codec root/function parameter block, all 16 Azalia stream indirect latency/FIFO blocks, complete endpoint 0 through endpoint 2 codec converter/pin blocks, and the beginning of endpoint 3 through `AZF0ENDPOINT3_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR11`. The chunk ends before the rest of endpoint 3's pin-control register family, so adjacent chunks are required for a whole-file view.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU Display Core hardware metadata for DCN 3.2.1 Azalia/HD Audio programming, not Ceph filesystem code.

## Purpose

The purpose of this range is to describe bit layouts for DCN 3.2.1 Azalia audio codec, stream, and endpoint indirect registers. The matching offset header supplies MMIO and indirect-index addresses; this header supplies the field positions and masks used by generated register tables and helper macros to pack writes, decode reads, and preserve unrelated bits during read/modify/write sequences.

The hardware surfaces represented here are:

- F2 codec input-pin control and parameter fields for multichannel enable/mute/channel-id controls, HBR capability/enable, LPIB snapshots, input activity, audio infoframe content, channel status, widget capabilities, and pin capabilities.
- F2 codec root and function parameters for vendor/device ID, revision, subordinate node counts, power state, subsystem ID response bytes, converter synchronization, reset, supported sample rates/bit depths, stream formats, and supported power states.
- `AZF0STREAM0` through `AZF0STREAM15` stream-indirect latency/FIFO telemetry, each with FIFO size limits, latency-counter reset, worst-case latency, cumulative latency, and cumulative request counters.
- `AZF0ENDPOINT0`, `AZF0ENDPOINT1`, and `AZF0ENDPOINT2` endpoint-indirect codec converter and pin-control definitions, including audio widget capability, converter format, channel/stream ID, digital converter channel-status bits, supported formats/rates, stripe/ramp/GTC timing controls, pin descriptors, speaker/channel allocation, sink information, hotplug/audio enable controls, IEC 60958 channel-status overrides, LPIB snapshots, format-change reporting, remote keepalive, and audio interrupt status.
- The start of `AZF0ENDPOINT3`, covering the same converter block and early pin block through audio descriptor 11.

These constants are generated data rather than executable logic, but they form an ABI between AMDGPU display/audio code, generated register access tables, firmware-facing display code, and the GPU's HD Audio/Azalia hardware. A wrong shift or mask can compile cleanly while causing HDMI/DisplayPort audio setup, channel mapping, timing readback, hotplug reporting, or interrupt handling to touch the wrong hardware bits.

## Important APIs, Types, And Macros

This chunk exports the standard AMD generated register-field naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in register-positioned form.
- `//<REGISTER>` comments group the following definitions by hardware register.
- `// addressBlock: ...` comments mark indirect register windows such as codec root, stream, and endpoint blocks.

There are no callable APIs or C data types in this chunk. Runtime code consumes these symbols through AMD display register-list and mask/shift-list infrastructure, normally paired with addresses from `dcn_3_2_1_offset.h`.

Important macro families in this range include:

- `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_*` and `AZALIA_F2_CODEC_INPUT_PIN_PARAMETER_*`.
- `AZALIA_F2_CODEC_ROOT_PARAMETER_*` and `AZALIA_F2_CODEC_FUNCTION_*`.
- `AZF0STREAM[0-15]_AZALIA_FIFO_SIZE_CONTROL`, `AZALIA_LATENCY_COUNTER_CONTROL`, `AZALIA_WORSTCASE_LATENCY_COUNT`, `AZALIA_CUMULATIVE_LATENCY_COUNT`, and `AZALIA_CUMULATIVE_REQUEST_COUNT`.
- `AZF0ENDPOINT[0-3]_AZALIA_F0_CODEC_CONVERTER_*` for converter format, channel stream ID, digital converter status, supported stream/rate information, stripe control, ramp rate, GTC embedding, and GTC counter deltas.
- `AZF0ENDPOINT[0-3]_AZALIA_F0_CODEC_PIN_PARAMETER_*` and `AZF0ENDPOINT[0-3]_AZALIA_F0_CODEC_PIN_CONTROL_*` for pin capabilities, unsolicited responses, pin sense, widget output enable, speaker/channel allocation, audio descriptors, HBR/lipsync/sink info, hotplug state, multichannel state, LPIB state, format-change reporting, and remote keepalive.
- `AZF0ENDPOINT[0-2]_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_*` for IEC 60958 channel-status override controls.
- `AZF0ENDPOINT[0-2]_AZALIA_F0_AUDIO_ENABLE_STATUS`, `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, and `AUDIO_FORMAT_CHANGED_INT_STATUS`.

## F2 Input Pin And Codec Root Fields

The chunk begins with the tail of the F2 input-pin multichannel controls. The visible multichannel families expose a repeated layout: an enable bit at bit 0, mute at bit 1, and a 4-bit channel ID at bits 4 through 7. The range includes odd/even multichannel registers across channels 1, 3, 5, 7 and the tail of channel 4 plus channel 6, while earlier channel definitions live in the preceding chunk.

`AZALIA_F2_CODEC_INPUT_PIN_CONTROL_HBR` exposes high-bit-rate audio capability and enable bits. The LPIB families define a snapshot lock, an 8-bit cyclic-buffer wrap count, the 32-bit link position in buffer, and a 32-bit timer snapshot. `INPUT_STATUS_CONTROL` exposes input activity, channel-layout state, and unsolicited-response enables for activity or channel-layout/channel-status infoframe changes. `INFOFRAME` exposes channel count, channel allocation, byte 5, and validity. `CHANNEL_STATUS_L` and `_H` expose full 32-bit low/high channel-status payloads.

The F2 input pin parameter families describe HD Audio widget/pin capabilities. `AUDIO_WIDGET_CAPABILITIES` includes flags for channel capability, input/output amplifier presence, amplifier parameter override, stripe, processing widget, unsolicited response support, connection list, digital output, power control, left/right swap, widget delay, and type. `PARAMETER_CAPABILITIES` includes impedance sense, trigger required, jack detection, headphone drive, output/input capability, balanced I/O, HDMI, VREF control, EAPD, and DP capability bits.

The `azroot_f2codecind` address block then defines root and function-level codec fields. Root parameters provide vendor/device ID, revision ID, and subordinate node count. Function-control registers expose power-state set/actual values, clock-stop OK, settings reset, subsystem ID response bytes, converter synchronization, and codec reset. Function parameter registers expose subordinate node count, group type, supported sample rates/bit depths, supported stream formats, and power-state capability flags such as clock-stop and EPSS.

## Stream Indirect Blocks

The `azf0stream0_streamind` through `azf0stream15_streamind` blocks are structurally identical. Each stream exposes:

- `AZALIA_FIFO_SIZE_CONTROL`, with 7-bit minimum FIFO size, 7-bit maximum FIFO size, and an 8-bit maximum latency support field.
- `AZALIA_LATENCY_COUNTER_CONTROL`, with a latency-counter reset bit.
- `AZALIA_WORSTCASE_LATENCY_COUNT`, a full 32-bit worst-case latency counter.
- `AZALIA_CUMULATIVE_LATENCY_COUNT`, a full 32-bit cumulative latency counter.
- `AZALIA_CUMULATIVE_REQUEST_COUNT`, a full 32-bit cumulative request counter.

These definitions are used by runtime display/audio code or diagnostics to configure or inspect stream buffering and latency behavior. The macros do not identify which stream is active for a given audio path; that mapping is supplied by higher-level resource allocation and hardware programming code. The counters should be treated as hardware telemetry, not persistent software accounting.

## Endpoint Converter Blocks

Endpoint 0 through endpoint 2 are complete in this chunk, and endpoint 3 begins with the same converter structure. The converter parameter and control registers define the digital audio converter attached to each endpoint:

- `CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` describes converter widget flags such as channel capability, amplifier presence, format override, stripe support, processing widget, unsolicited-response support, digital/power-control behavior, LR swap, delay, and widget type.
- `CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT` packs number of channels, bits per sample, sample base divisor, sample base multiple, sample base rate, and stream type.
- `CODEC_CONVERTER_CONTROL_CHANNEL_STREAM_ID` maps converter channel ID and stream ID.
- `CODEC_CONVERTER_CONTROL_DIGITAL_CONVERTER` exposes digital converter enable and IEC-style channel-status bits such as validity, validity-config, pre-emphasis, copy, non-audio, professional mode, level, category code, and keepalive.
- `CODEC_CONVERTER_PARAMETER_STREAM_FORMATS` and `SUPPORTED_SIZE_RATES` expose supported stream formats, audio rate capabilities, and audio bit-depth capabilities.
- `CODEC_CONVERTER_STRIPE_CONTROL` exposes stripe-control and stripe-capability fields.
- `CODEC_CONVERTER_CONTROL_RAMP_RATE` defines an 8-bit ramp-rate control.
- `CODEC_CONVERTER_CONTROL_GTC_EMBEDDING` controls presentation-time embedding, offset-changed signaling, GTC min/max delta clearing, and presentation-time embedding group selection.
- `CODEC_CONVERTER_GTC_COUNTER_DELTA`, `_MIN`, and `_MAX` expose 32-bit GTC delta readbacks.

The converter blocks are central to HDMI/DP audio stream setup. Format, channel count, stream ID, channel ID, sample-rate fields, and digital converter status must remain synchronized with the display audio stream and with the sink's ELD/EDID-derived capabilities.

## Endpoint Pin Blocks

Endpoint pin parameter and control registers describe the external audio pin side of each endpoint. Complete endpoint 0 through 2 blocks include pin widget capabilities, pin capabilities, unsolicited-response controls, pin-sense readback, widget output enable, speaker/channel allocation, audio descriptors, multichannel controls, sink information, hotplug/audio enable state, channel-status overrides, LPIB snapshots, format-change state, remote keepalive, and interrupt status. Endpoint 3 is included through audio descriptor 11 in this chunk.

Key pin-control families include:

- `CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES` and `CODEC_PIN_PARAMETER_CAPABILITIES`, which mirror the HD Audio widget/pin capability surfaces for each endpoint.
- `CODEC_PIN_CONTROL_UNSOLICITED_RESPONSE`, with a 6-bit tag and enable bit.
- `CODEC_PIN_CONTROL_RESPONSE_PIN_SENSE`, exposing a 31-bit impedance-sense field in the visible endpoint blocks.
- `CODEC_PIN_CONTROL_WIDGET_CONTROL`, exposing output enable.
- `CODEC_PIN_CONTROL_CHANNEL_SPEAKER`, with speaker allocation, channel allocation, HDMI/DP connection flags, extra connection info, LFE playback level, level shift, and down-mix inhibit.
- `CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR0` through `13` on complete endpoints, each exposing maximum channels, supported frequencies, descriptor byte 2, and for descriptor 0 an additional stereo-frequency byte.
- `CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2`, which pack enable, mute, and channel ID fields for multichannel pairs or individual odd channels.
- `CODEC_PIN_CONTROL_RESPONSE_LIPSYNC` and `RESPONSE_HBR`, used for sink timing and high-bit-rate audio capability/enable reporting.
- `CODEC_PIN_CONTROL_SINK_INFO0` through `8`, which expose sink manufacturer/product IDs and packed 8-bit description bytes.
- `CODEC_PIN_CONTROL_HOT_PLUG_CONTROL`, with clock gating disable, clock-on state, and an audio-enabled bit.
- `CODEC_PIN_CONTROL_UNSOLICITED_RESPONSE_FORCE`, with a payload and force bit for synthetic unsolicited responses.
- `CODEC_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT`, describing sequence, default association, misc, color, connection type, default device, location, and port connectivity.
- `CODEC_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL`, `LPIB`, and `LPIB_TIMER_SNAPSHOT`, which expose per-pin link-position and timer snapshots.
- `CODEC_PIN_CONTROL_CODING_TYPE`, `FORMAT_CHANGED`, `WIRELESS_DISPLAY_IDENTIFICATION`, and `REMOTE_KEEPALIVE`.

For endpoint 3, the chunk stops in the middle of the audio descriptor list. The final merged file-level report should combine this range with the next chunk to cover endpoint 3's remaining descriptors, multichannel fields, sink info, hotplug controls, and interrupt/status fields.

## Channel Status Overrides And Interrupt Status

Endpoint 0 through endpoint 2 include `AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8`. These fields map to IEC 60958 channel-status override knobs:

- Mode and source number.
- Clock accuracy, word length, and corresponding override-enable bits.
- Sampling frequency, original sampling frequency, and corresponding override-enable bits.
- Sampling-frequency coefficient, MPEG surround info, CGMS-A, and CGMS-A validity.
- Channel numbers for left/right and channels 2 through 7.

These override fields can alter the channel-status information presented to an audio sink. They are value/override style controls in practice: programming an override value without enabling the relevant override bit may have no effect, while leaving an override enabled can make the sink receive stale or policy-inconsistent audio metadata.

Endpoint 0 through endpoint 2 also include audio state and interrupt status surfaces. `AUDIO_ENABLE_STATUS` reports current audio-enable state. `AUDIO_ENABLED_INT_STATUS`, `AUDIO_DISABLED_INT_STATUS`, and `AUDIO_FORMAT_CHANGED_INT_STATUS` each expose a flag bit, a mask bit, and a type bit. These definitions support interrupt handling around audio enable/disable and audio format changes. The macros do not state whether flags are write-one-to-clear, read-clear, level, or edge-triggered; the driver code and hardware documentation must supply that behavior.

## Control Flow

There is no executable control flow in this header. Runtime flow is supplied by AMDGPU display code that includes this generated mask file, includes the matching generated offset file, and expands generated register access macros or register tables.

Typical runtime usage is:

1. DCN 3.2.1 resource, link-encoder, audio, DMUB, clock, IRQ, or diagnostic code selects an Azalia root, stream, or endpoint indirect register.
2. Generated offset symbols from `dcn_3_2_1_offset.h` identify the MMIO register or indirect index/data pair.
3. Generated register helpers bind those offsets to one or more `_SHIFT` and `_MASK` symbols from this file.
4. Runtime code packs writes, performs read/modify/write updates, reads status fields, polls counters or flags, or decodes register dumps using these masks and shifts.
5. Hardware latches stream/converter/pin configuration, reports sink/audio status, updates latency and LPIB counters, generates audio-related unsolicited responses or interrupts, or exposes channel-status and infoframe data.

This file does not encode reset values, valid enumerations, indirect-index access ordering, volatile semantics, write-one-to-clear behavior, required delays, interrupt acknowledgement rules, or policy for HDMI versus DisplayPort audio.

## State And Persistence Behavior

No software state is stored by this file. It describes MMIO-backed and indirect-register-backed hardware state whose lifetime is governed by GPU reset, display hotplug, modeset, audio stream allocation, link training, sink capability discovery, runtime power management, suspend/resume, interrupt handling, and diagnostic tooling.

Persistent or latched hardware configuration fields in this chunk include codec/function power state, converter synchronization/reset controls, converter format, channel and stream IDs, digital converter enable/channel-status bits, stripe/ramp controls, GTC embedding controls, pin output enable, channel/speaker allocation, multichannel enable/mute/channel IDs, hotplug clock/audio enable controls, configuration default fields, channel-status overrides, coding type, format-change response controls, wireless-display identification, remote keepalive, interrupt masks, and latency-counter reset controls.

Volatile or readback-oriented fields include vendor/device/revision parameters, subordinate node counts, supported formats/rates/power states, HBR capability, LPIB values, timer snapshots, cyclic buffer wrap count, input activity, infoframe validity/content, channel status, stream worst-case and cumulative latency counters, cumulative request counters, GTC delta/min/max readbacks, pin sense, sink info, audio enable status, interrupt flags, output-active state, and format-changed state.

Side-effecting or sequencing-sensitive fields include codec reset, power-state transitions, converter synchronization, HBR enable, digital converter enable, hotplug audio enable, unsolicited-response force, interrupt masks/flags, LPIB snapshot lock, latency-counter reset, GTC min/max clear, channel-status override enables, and format-change acknowledgement controls. Treating these as ordinary static fields can leave audio disabled, generate spurious unsolicited responses, hide real format changes, or report inaccurate timing/counter data.

## Dependencies And Integration Points

This chunk depends on the matching generated DCN 3.2.1 offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h`

The offset and mask headers must be generated from the same hardware register database. The matching offset file contains the Azalia index/data MMIO registers such as `regAZF0STREAM0_AZALIA_STREAM_INDEX`, `regAZF0STREAM0_AZALIA_STREAM_DATA`, `regAZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_INDEX`, and `regAZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_DATA`, plus indirect offsets such as `ixAZALIA_F2_CODEC_ROOT_PARAMETER_VENDOR_AND_DEVICE_ID`, `ixAZF0STREAM0_AZALIA_FIFO_SIZE_CONTROL`, and `ixAZF0ENDPOINT0_AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`.

Local DCN 3.2.1 integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`, which includes `dcn/dcn_3_2_1_offset.h` and `dcn/dcn_3_2_1_sh_mask.h`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn321/dcn321_dio_link_encoder.c` and `.h`, which provide DCN 3.2.1 link-encoder construction.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`, which has DCN321-specific register/mask wiring for clock management.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_srv.c` and `dmub_srv.h`, which identify `DMUB_ASIC_DCN321`.
- Higher-level display/audio paths under AMDGPU DM and Display Core that use the DCN321 resource pool, link encoders, hotplug handling, audio endpoint setup, and DMUB firmware interactions.

Practical integration surfaces are HDMI/DP audio enumeration, audio stream format programming, channel allocation, HBR audio, sink description reporting, LPIB/timing readback, GTC presentation-time embedding, audio hotplug, unsolicited HD Audio responses, and audio enable/disable/format-change interrupts.

## Risks And Edge Cases

- The chunk starts and ends inside register families. `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL4_ENABLE` is partial at the start, and endpoint 3's pin descriptor family is partial at the end.
- Generated-header drift from the authoritative DCN 3.2.1 register database is the primary risk. Wrong numeric shifts or masks usually compile but produce runtime audio failures.
- The stream blocks are highly repetitive across 16 streams. Copying a symbol with the wrong `AZF0STREAMN` prefix can silently read or reset the wrong stream's latency counters.
- Endpoint blocks are highly repetitive across endpoints 0 through 3. A wrong endpoint prefix can program channel allocation, sink info, converter format, or interrupts for the wrong audio endpoint.
- Many fields are packed byte or nibble fields. Incorrect masks for channel IDs, descriptor bytes, source/channel numbers, sample frequency, or word length can corrupt only part of a metadata word and be difficult to spot in register dumps.
- HBR, channel allocation, speaker allocation, and audio descriptor fields must match sink capabilities. This header provides bit placement only, not validation.
- LPIB snapshot lock, timer snapshots, stream latency counters, and GTC deltas are timing-sensitive readback surfaces. Incorrect access ordering or stale snapshots can produce misleading audio/video synchronization diagnostics.
- Interrupt status fields expose flag, mask, and type bits but not acknowledgement semantics. Treating an interrupt flag as ordinary read-only state can lose or repeat audio enable/disable/format-change events.
- Channel-status override fields can make the sink receive metadata that differs from the active stream format if override-enable bits remain asserted after modesets or stream changes.
- Unsolicited-response force controls are diagnostic-like surfaces. Accidental writes can synthesize HD Audio events and confuse hotplug/audio state machines.
- This mask header cannot protect callers from invalid values, wrong indirect-register selection, wrong write order, missing locking around shared Azalia index/data windows, or writes to status/readback-only fields.

## Test Signals

Useful validation signals for this chunk include:

- Compile coverage for DCN321 display objects that include `dcn_3_2_1_sh_mask.h`, especially `dcn321_resource.c` and any generated register-list users. Missing or renamed macros surface at build time.
- Consistency checks against `dcn_3_2_1_offset.h`: every register family used from this chunk should have a matching direct or indirect offset/index definition.
- Register-database or generated-header diff checks against adjacent ASIC generations to catch unintended DCN 3.2.1 changes in Azalia field placement.
- HDMI and DisplayPort audio smoke tests across stereo, multichannel PCM, and HBR-capable paths, verifying stream format, channel allocation, sink descriptor, and audio enable state.
- Hotplug and modeset tests that confirm unsolicited responses, audio enable/disable interrupts, and format-change interrupts fire and clear correctly.
- Suspend/resume and runtime power-management tests that verify codec/function power state, converter format, channel-status overrides, and audio enable state are restored or reprogrammed correctly.
- Audio/video synchronization diagnostics that compare LPIB snapshots, timer snapshots, GTC delta/min/max, and latency counters against expected stream behavior.
- Register dump decoding for endpoints 0 through 3 and streams 0 through 15, checking that decoded fields align with the active display/audio topology.
- Negative or recovery tests that switch between HDMI and DP sinks, change channel counts and sample rates, enable/disable HBR audio, and verify stale channel-status overrides or multichannel mutes do not persist.

## Chunk Notes

This is source-tree-aligned chunk research only. It intentionally writes only `Docs/researches/chunks/subset-b-002047_research.md`. Whole-file research for `dcn_3_2_1_sh_mask.h` must merge adjacent chunks to complete the preceding F2 input-pin multichannel block and the following endpoint 3 Azalia pin-control block.

### subset-b-002048: lines 52080-54448

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 52080-54448

## Scope

This chunk is a generated AMD DCN 3.2.1 register shift/mask header slice for Azalia F0 audio endpoint indirect registers. It contains preprocessor constants only: register-group comments, `_SHIFT` macros for bit positions, and `_MASK` macros for register-positioned masks. There are no C functions, structs, enums, branches, allocations, locking paths, or software persistence mechanisms in this range.

The requested range covers 2,369 source lines, 2,049 `#define` lines, and 312 register/address-block comments. It starts inside endpoint 3 pin-control audio descriptor data, then covers the tail of `AZF0ENDPOINT3_AZALIA_F0_*`, complete repeated register layouts for `azf0endpoint4_endpointind`, `azf0endpoint5_endpointind`, and `azf0endpoint6_endpointind`, plus most of `azf0endpoint7_endpointind`. It ends inside `AZF0ENDPOINT7_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_4`; two masks for that register continue immediately after the chunk.

Although this repository path is under a `ceph-client` source mirror, this file is AMDGPU Display Core hardware metadata. The slice is about HDMI/DisplayPort audio codec endpoint programming, not Ceph filesystem behavior.

## Purpose

The purpose of this header range is to provide named bit layouts for DCN 3.2.1 Azalia F0 endpoint codec registers. AMD display audio code pairs these masks with offsets from `dcn_3_2_1_offset.h` and with the generic DCE audio register helpers so it can program HDMI/DP audio format, channel mapping, sink metadata, HBR capability, lipsync values, hotplug audio enable state, IEC 60958 channel-status overrides, and endpoint interrupt/status fields without hard-coding raw bit positions.

The main hardware surfaces represented here are:

- Converter widget capabilities and converter controls for endpoints 4 through 7, including stream format, channel/stream ID, digital-converter channel-status bits, supported stream formats/rates, stripe control, ramp rate, and GTC embedding/counter delta fields.
- Pin widget capabilities and pin controls, including unsolicited response, pin sense, widget output enable, speaker/channel allocation, HDMI vs DP connection flags, LFE level, downmix inhibit, and extra connection info.
- Fourteen audio descriptor registers per endpoint, exposing max channels, supported frequencies, descriptor byte 2, and for descriptor 0 an extra stereo-frequency byte.
- Multichannel enable/mute/channel-ID packing for both channel pairs (`01/23/45/67`) and odd individual channels (`1/3/5/7`), plus multichannel mode.
- Sink information registers carrying manufacturer/product IDs, sink display-name length, port IDs, and up to 18 bytes of monitor description text.
- Hot-plug/audio enable control, lipsync response, HBR response, forced unsolicited response payloads, configuration default response, digital output status, LPIB snapshot/data, coding type, format-change response fields, remote keepalive, audio enable status, and endpoint audio interrupt status.
- IEC 60958 channel-status override registers for mode, source number, clock accuracy, word length, sampling frequency, original sampling frequency, sampling-frequency coefficient, MPEG surround info, CGMS-A, CGMS-A valid, and per-channel numbers.

These constants form a generated hardware ABI between the display driver and DCN 3.2.1 audio hardware. A wrong shift or mask can compile cleanly while causing HDMI/DP audio to expose incorrect EDID-derived capabilities, route channels incorrectly, leave HBR disabled, report stale sink identity, or fail to acknowledge endpoint audio events.

## Important APIs, Types, And Macros

There are no callable APIs or C data types in this chunk. Its exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the register-positioned bit mask.
- `//<REGISTER>` comments group the subsequent field definitions by endpoint-indirect register.
- `// addressBlock: azf0endpointN_endpointind` comments mark repeated endpoint register blocks.

Important macro families include:

- Endpoint converter capabilities and controls: `AZF0ENDPOINT[4-7]_AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, `...CONTROL_CONVERTER_FORMAT`, `...CONTROL_CHANNEL_STREAM_ID`, `...CONTROL_DIGITAL_CONVERTER`, `...PARAMETER_STREAM_FORMATS`, `...PARAMETER_SUPPORTED_SIZE_RATES`, `...STRIPE_CONTROL`, `...CONTROL_RAMP_RATE`, `...CONTROL_GTC_EMBEDDING`, and `...GTC_COUNTER_DELTA*`.
- Pin capabilities and controls: `AZF0ENDPOINT[4-7]_AZALIA_F0_CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, `...PIN_PARAMETER_CAPABILITIES`, `...PIN_CONTROL_UNSOLICITED_RESPONSE`, `...RESPONSE_PIN_SENSE`, `...WIDGET_CONTROL`, and `...CHANNEL_SPEAKER`.
- Audio descriptor tables: `AZF0ENDPOINT[3-7]_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`.
- Multichannel controls: `...PIN_CONTROL_MULTICHANNEL_ENABLE`, `...MULTICHANNEL_ENABLE2`, and `...MULTICHANNEL_MODE`.
- Sink metadata and hotplug/audio response controls: `...RESPONSE_LIPSYNC`, `...RESPONSE_HBR`, `...SINK_INFO0` through `SINK_INFO8`, `...HOT_PLUG_CONTROL`, `...UNSOLICITED_RESPONSE_FORCE`, and `...RESPONSE_CONFIGURATION_DEFAULT`.
- IEC 60958 channel-status overrides: `...PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8`.
- Endpoint status/interrupt registers: `...AUDIO_ENABLE_STATUS`, `...AUDIO_ENABLED_INT_STATUS`, `...AUDIO_DISABLED_INT_STATUS`, and `...AUDIO_FORMAT_CHANGED_INT_STATUS`.

The chunk also indirectly supports generic non-endpoint-specific audio code. In `drivers/gpu/drm/amd/display/dc/dce/dce_audio.h`, the audio object is built around `AZALIA_F0_CODEC_ENDPOINT_INDEX` and `AZALIA_F0_CODEC_ENDPOINT_DATA`; endpoint-indirect register names such as `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_HBR` are selected through the endpoint index/data path rather than by open-coding each endpoint's concrete `AZF0ENDPOINTN_...` symbol at every call site.

## Endpoint Coverage And Register Layout

Endpoint 3 is only partially represented. The chunk begins with the last mask for `AUDIO_DESCRIPTOR11`, then includes descriptor 12 and 13, multichannel controls, lipsync/HBR responses, sink-info registers, hot-plug/audio-enable control, unsolicited-response forcing, configuration default, IEC 60958 override registers, association/status/LPIB/coding/format-change/keepalive controls, and the endpoint audio enable/disable/format-change interrupt status registers.

Endpoints 4, 5, and 6 are complete within this chunk. Each block starts at an `addressBlock` marker and repeats the same converter, pin, descriptor, multichannel, sink-info, hotplug, channel-status override, LPIB, format-change, keepalive, audio-enable status, and audio interrupt register families. This repetition is intentional: each audio endpoint has the same endpoint-indirect register shape but a distinct endpoint instance and macro prefix.

Endpoint 7 starts at line 53990 and is mostly covered through the early IEC 60958 override registers. The visible range includes converter and pin capability/control registers, all fourteen audio descriptors, multichannel controls, sink-info registers, hotplug/audio enable, unsolicited/configuration response, and override registers 0 through the first two masks of override register 4. The remaining masks for `CGMS_A` and `CGMS_A_VALID` are in the next chunk.

## Runtime Control Flow

This header has no executable control flow. Runtime flow is supplied by AMDGPU display audio code:

1. DCN 3.2.1 resource construction wires audio register offsets and field masks into `struct dce_audio_registers`, `struct dce_audio_shift`, and `struct dce_audio_mask`. In this tree, `drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c` defines `audio_regs[5]` and binds common Azalia endpoint index/data fields via `DCE120_AUD_COMMON_MASK_SH_LIST`.
2. `drivers/gpu/drm/amd/display/dc/dce/dce_audio.c` selects an endpoint instance and uses `AZ_REG_READ`, `AZ_REG_WRITE`, `set_reg_field_value`, and `get_reg_field_value` around the generic endpoint-indirect register names.
3. The helper layer writes the endpoint index register, reads or writes endpoint data, and uses this generated shift/mask data to pack or extract individual fields.
4. Hardware then latches converter/pin/audio metadata, reports audio enable/disable/format-change state, and exposes endpoint status to the display interrupt and audio paths.

Representative consumers visible in `dce_audio.c` include:

- `set_high_bit_rate_capable()` reads and writes `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_HBR` using `HBR_CAPABLE`.
- `set_video_latency()` and `set_audio_latency()` update `VIDEO_LIPSYNC` and `AUDIO_LIPSYNC`.
- `dce_aud_az_enable()` and `dce_aud_az_disable()` toggle `CLOCK_GATING_DISABLE` and `AUDIO_ENABLED` in `HOT_PLUG_CONTROL`.
- `dce_aud_az_configure()` programs `CHANNEL_SPEAKER`, `AUDIO_DESCRIPTOR0 + format_index`, `SINK_INFO0` through `SINK_INFO8`, HBR capability, and lipsync fields from the detected HDMI/DP audio information.

The IRQ source IDs for endpoint audio enabled, disabled, and format-changed events are declared in `drivers/gpu/drm/amd/include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`; the status/mask/type register fields in this chunk are the endpoint-local hardware status surface that corresponds to those classes of events.

## State And Persistence Behavior

The macros themselves store no software state. They describe MMIO-backed endpoint-indirect hardware registers whose lifetime is governed by GPU reset, display core initialization, endpoint selection, hotplug handling, modeset/audio configuration, suspend/resume, runtime power management, and HDMI/DP audio driver interactions.

Persistent or latched hardware configuration fields in this range include converter stream format, channel/stream ID, digital converter channel-status bits, stripe control, ramp-rate mode, GTC embedding parameters, pin widget output enable, speaker allocation, HDMI/DP connection flags, audio descriptors, multichannel enable/mute/channel IDs, sink manufacturer/product/port/display-name metadata, HBR capability/enable, lipsync values, configuration default response, IEC 60958 channel-status override values, remote keepalive, and hotplug audio-enable state.

Volatile or event/status-oriented fields include pin sense, digital output active, LPIB and LPIB timer snapshots, cyclic-buffer wrap count, format-changed status/reason/response, wireless display identification, audio enable status, and audio enabled/disabled/format-changed interrupt flag/mask/type fields.

Several fields are sequencing-sensitive. `HOT_PLUG_CONTROL` includes `CLOCK_GATING_DISABLE`, `CLOCK_ON_STATE`, and `AUDIO_ENABLED`; `dce_audio.c` explicitly disables clock gating before changing audio enable state and then re-enables gating. `LPIB_SNAPSHOT_LOCK` is a lock/snapshot control, not ordinary metadata. The interrupt status registers have flag/mask/type triplets, so acknowledgement and masking policy must preserve the intended flag semantics. The forced unsolicited-response register has a payload plus force bit, so stale payload data can be emitted if the force bit is misused.

## Dependencies And Integration Points

The direct generated-header pair for this chunk is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h`

The offsets identify endpoint index/data and endpoint-indirect register addresses; this chunk provides the field packing metadata. These files must be generated from the same DCN 3.2.1 register database.

Important local integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h`: declares the common audio register, shift, and mask structures and the `AUD_COMMON_*` register-list macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.c`: programs HBR, lipsync, hotplug audio enable, channel/speaker allocation, ACP data, audio descriptor tables, sink info, and audio clock DTO state.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`: constructs DCN 3.2.1 audio register arrays and binds the common Azalia endpoint index/data masks into audio objects.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`: declares endpoint audio enabled, disabled, and format-changed interrupt source/context IDs.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h`: contains related Azalia enum values for converter format fields, digital converter bits, audio descriptor format codes, and multichannel mute semantics on newer/generated register descriptions.

Practical runtime integration points are HDMI audio, DP audio, DP MST audio endpoints, EDID/audio-info propagation, sink display-name and port-ID reporting, HBR exposure for high-bit-rate compressed formats, lipsync reporting, hotplug audio enable/disable sequencing, endpoint interrupt handling, and audio debug/register-dump decoding.

## Risks And Edge Cases

- The chunk starts and ends inside register definitions. Endpoint 3 `AUDIO_DESCRIPTOR11` is partial at the beginning, and endpoint 7 `CODEC_CS_OVERRIDE_4` is partial at the end. Adjacent chunks are required for complete per-register coverage at the boundaries.
- The endpoint blocks are highly repetitive. Copying a symbol with the wrong `AZF0ENDPOINTN` prefix can target the wrong audio endpoint while keeping the field layout valid enough to compile.
- Endpoint count must match resource construction. This chunk exposes endpoints 3 through 7, while `dcn321_resource.c` declares five audio objects; instance-to-endpoint mapping must remain consistent with the offset header and hardware topology.
- Audio descriptors are programmed by index arithmetic in `dce_audio.c` (`AUDIO_DESCRIPTOR0 + format_index`). The descriptor registers must remain contiguous and consistently shaped for that code to be correct.
- `AUDIO_DESCRIPTOR0` has the extra `SUPPORTED_FREQUENCIES_STEREO` field, while descriptors 1 through 13 do not. Generic descriptor-writing code must only use that field for descriptor 0.
- `CHANNEL_SPEAKER` contains both HDMI and DP connection bits. Incorrect setting can advertise the wrong transport to the audio driver or sink.
- `HOT_PLUG_CONTROL` is power/clock sensitive. Updating `AUDIO_ENABLED` without the expected clock-gating sequence can race hardware state or fail to latch the change.
- `RESPONSE_HBR` separates capability and enable bits. Advertising unsupported HBR or failing to set capability when bandwidth allows can break high-bit-rate audio formats.
- Sink info registers pack bytes of display name and port IDs. Off-by-one string length, nonzero stale bytes, or wrong byte order can expose incorrect monitor identity through the audio codec interface.
- IEC 60958 override fields are standards-visible channel-status metadata. Bad sampling-frequency, word-length, clock-accuracy, CGMS-A, or channel-number values can create audio-driver or receiver interoperability problems.
- Interrupt status registers expose flag/mask/type fields with repeated names such as `AUDIO_ENABLED_MASK_MASK`. Automated name processing must preserve the generated spelling.
- This header does not encode reset values, access permissions, write-one-to-clear behavior, volatile semantics, value enumerations, required delays, or endpoint selection rules. Callers must rely on the hardware specification and existing helper code for those semantics.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for DCN 3.2.1 display audio consumers, especially `dcn321_resource.c` and `dce_audio.c`, so missing or renamed masks fail at compile time.
- Generated-header consistency checks that each visible field has a matching shift and mask, masks do not overlap within a register unless documented, and endpoint 4/5/6 repeated layouts remain identical except for the endpoint prefix.
- Static validation that `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13` remain contiguous in the matching offset header, because runtime descriptor programming uses indexed writes.
- HDMI and DP audio smoke tests across hotplug, modeset, suspend/resume, and audio enable/disable transitions.
- EDID/audio-info propagation tests that verify speaker allocation, audio descriptor formats, supported sample rates, HBR capability, lipsync values, sink manufacturer/product IDs, port IDs, and display-name bytes are visible through the audio codec interface.
- DP MST tests with multiple active audio endpoints, to catch wrong endpoint-prefix or instance mapping mistakes.
- Interrupt tests or trace validation for endpoint audio enabled, disabled, and format-changed events, including flag/mask/type handling.
- Register dump comparison against the DCN 3.2.1 hardware register database for endpoint 3 through endpoint 7 Azalia blocks.

## Summary

This chunk is a dense generated bitfield map for DCN 3.2.1 Azalia F0 HDMI/DP audio endpoint registers. Its practical value is naming the fields that AMD display audio code uses to expose sink capabilities, program audio format and channel metadata, toggle endpoint audio, report lipsync/HBR state, manage sink identity strings, and observe endpoint audio events. The main engineering risks are stale generated data, wrong endpoint instance selection, descriptor-table assumptions, standards-visible IEC 60958 metadata mistakes, and power/event sequencing bugs around hotplug audio enable and interrupt status.

### subset-b-002049: lines 54449-56598

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 54449-56598

## Scope

- Chunk id: `subset-b-002049`
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h`
- Source lines: 54449-56598
- Observed content: 2,150 generated header lines containing 1,922 `#define` entries, split into 960 `__SHIFT` macros and 962 `_MASK` macros.

This chunk is the final generated shift/mask slice of the AMD DCN 3.2.1 register-field header. It has no executable C logic. It starts in the middle of the `AZF0ENDPOINT7_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_4` field group, completes the remaining output endpoint 7 Azalia/HDA audio pin-control and audio interrupt fields, then covers all eight `azf0inputendpointN_inputendpointind` indexed input endpoint address blocks. The range ends with the file's closing `#endif`.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display/audio hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The chunk provides compile-time bit positions and masks for DCN321 Azalia function 0 endpoint registers. These constants are paired with register offsets and indexed-register IDs from `dcn_3_2_1_offset.h` so AMD display code can program or inspect HDA/HDMI/DP audio codec endpoint state through register helper macros.

The covered hardware surface is audio-specific:

- The tail of `AZF0ENDPOINT7` output endpoint fields for IEC 60958 channel-status overrides, channel numbers, association info, digital-output status, LPIB snapshots, coding type, audio format-change reporting, wireless-display identification, remote keepalive, audio enable state, and enable/disable/format-change interrupt status.
- `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7` input endpoint fields for converter capabilities, stream format, channel/stream IDs, digital converter control, supported size/rate reports, pin capabilities, unsolicited response setup, input pin sense, widget control, multichannel enable maps, HBR capability/enable, channel allocation, hot-plug/audio-enable state, forced unsolicited responses, configuration defaults, LPIB snapshots, input activity/status controls, and received infoframe metadata.

The `AZF0INPUTENDPOINT*` groups are highly regular repeated instances. Each endpoint has the same generated field layout, with the endpoint number encoded in the macro prefix.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, variables, includes, locks, or runtime APIs in this chunk. The public interface is the generated preprocessor namespace:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: 32-bit mask for isolating or updating that field.
- `// addressBlock: azf0inputendpointN_inputendpointind`: generated block markers for indexed input endpoint register groups.

Important field families in this range include:

- IEC/channel-status override fields: `IEC_60958_CS_CHANNEL_NUMBER_*`, `IEC_60958_CS_CGMS_A`, and validity bits in the output endpoint 7 `CODEC_CS_OVERRIDE_*` registers.
- Output endpoint 7 status and event fields: `OUTPUT_ACTIVE`, `FORMAT_CHANGED`, `FORMAT_CHANGED_ACK_UR_ENABLE`, `FORMAT_CHANGE_REASON`, `FORMAT_CHANGE_RESPONSE`, `REMOTE_KEEP_ALIVE_ENABLE`, `REMOTE_KEEP_ALIVE_CAPABILITY`, `AUDIO_ENABLE_STATUS`, and audio enabled/disabled/format-changed flag/mask/type triples.
- Input converter capability fields: `AUDIO_CHANNEL_CAPABILITIES`, amplifier-present bits, `FORMAT_OVERRIDE`, `DIGITAL`, `POWER_CONTROL`, `LR_SWAP`, widget delay, and widget `TYPE`.
- Input converter format fields: `NUMBER_OF_CHANNELS`, `BITS_PER_SAMPLE`, `SAMPLE_BASE_DIVISOR`, `SAMPLE_BASE_MULTIPLE`, `SAMPLE_BASE_RATE`, and `STREAM_TYPE`.
- Input digital converter fields: `DIGEN`, validity/config/preemphasis/copy/non-audio/professional bits, category code `CC`, and `KEEPALIVE`.
- Input pin capability and sense fields: impedance sense, trigger/jack detection, output/input capability, HDMI/DP capability bits, VREF control, EAPD capability, `IMPEDANCE_SENSE`, and `PRESENCE_DETECT`.
- Input pin routing and multichannel fields: `CHANNEL_ID`, `STREAM_ID`, `IN_ENABLE`, multichannel 0-7 enable/mute/channel-id bitfields split across `MULTICHANNEL_ENABLE` and `MULTICHANNEL_ENABLE2`, `CHANNEL_ALLOCATION`, and HBR capability/enable.
- Input status/metadata fields: `AUDIO_ENABLED`, `INPUT_ACTIVITY`, `CHANNEL_LAYOUT`, unsolicited-response enable bits, `CHANNEL_COUNT`, `CHANNEL_ALLOCATION`, `INFOFRAME_BYTE_5`, and `INFOFRAME_VALID`.

The companion offset header exposes both MMIO selector/data registers, such as `regAZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX` and `regAZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_ENDPOINT_DATA`, and indexed IDs such as `ixAZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME`. This chunk supplies the field layout for those indexed register payloads.

## Control Flow

This header chunk has no local control flow. Runtime behavior is supplied by AMDGPU Display Core:

1. DCN321 resource construction includes `dcn_3_2_1_offset.h` and this shift/mask header.
2. Register-list and field-list macros paste generated names into register, shift, and mask tables.
3. Audio helper code selects an Azalia endpoint indexed register through endpoint index/data registers or direct register tables.
4. Helper macros such as `REG_SET`, `REG_UPDATE`, `REG_READ`, and audio-specific indexed helpers pack or extract field values using these masks and shifts.
5. Hardware implements the actual behavior: codec capability reporting, stream-format programming, channel allocation, HBR enablement, LPIB snapshotting, unsolicited responses, hotplug/audio-enable indication, and input infoframe/status capture.

The chunk does not encode ordering rules. Consumers still need to sequence endpoint index selection, register data reads/writes, audio stream enable/disable, infoframe updates, hotplug handling, interrupt masking/acknowledgement, and audio format-change response according to the HDA/Azalia and DCN programming model.

## State And Persistence Behavior

The macros are stateless constants. State exists only in the underlying hardware registers:

- Capability and descriptor-style fields report stable hardware or firmware-populated codec properties, such as widget capabilities, supported stream formats, supported sample rates/bit depths, pin capabilities, HDMI/DP capability bits, and default configuration values.
- Programmed configuration state includes converter format, channel/stream IDs, digital converter controls, unsolicited-response enable/tag values, input widget enablement, multichannel enable/mute/channel mapping, HBR enablement, hot-plug clock gating controls, forced unsolicited-response payloads, and UR-enable bits for input activity or infoframe changes.
- Live or latched status includes output active, input activity, audio-enabled status, presence detect, LPIB position, LPIB timer snapshots, cyclic-buffer wrap count, infoframe validity and contents, format-change reason/response, audio enabled/disabled/format-changed flags, and HBR capability/status.

Persistence is hardware-defined. Some fields are read-only capability/status, some are writable configuration, and some status or interrupt bits may be sticky, write-one-to-clear, self-clearing, or valid only while the associated display/audio clock and endpoint are powered. The generated shift/mask header does not identify access semantics; consumers must preserve reserved or unrelated bits through read-modify-write paths where required.

## Dependencies And Integration Points

Direct dependencies and consumers include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h`, which supplies the matching MMIO offsets and indexed register IDs for the Azalia endpoint blocks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`, which includes this header and builds DCN321 register/shift/mask tables. The `DCE120_AUD_COMMON_MASK_SH_LIST` macro references the `AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_INDEX` and `AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_DATA` fields, while common audio masks cover function-level audio fields outside this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.c` and `dce_audio.h`, which implement shared display audio operations around Azalia endpoint index/data access, stream format support, HBR response, hotplug control, speaker/channel mapping, sink info, audio descriptors, and configuration-default fields.
- DCN resource and stream/link paths that create audio objects for display connectors. On DCN321, the declared audio register array has five entries, while the generated register database includes more endpoint and input endpoint definitions. That mismatch is normal for generated ASIC metadata but means not every generated endpoint is necessarily instantiated by the driver.
- HDA/Azalia, HDMI, and DisplayPort audio flows visible to users as monitor audio device enumeration, format negotiation, hotplug audio enable/disable, high-bit-rate audio, channel allocation, and infoframe handling.

The input endpoint blocks are generated and paired with index/data register accessors in the offset header, but local display code primarily exercises output audio endpoint paths. Input endpoint definitions still matter for ASIC register database completeness, future consumers, diagnostics, and cross-generation table consistency.

## Risks And Edge Cases

- Numeric drift is the main risk. A wrong mask or shift can compile cleanly but update the wrong HDA codec field, causing silent audio format negotiation failures, bad channel mapping, missed hotplug/audio enable state, incorrect LPIB reporting, or broken unsolicited responses.
- The range starts mid-register at the tail of `CODEC_CS_OVERRIDE_4`. Final per-file synthesis must combine the previous chunk before making complete claims about output endpoint 7 IEC channel-status override coverage.
- Repeated endpoint names are easy to misuse. `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7` share nearly identical field layouts, but the endpoint number is part of the selected indexed register namespace.
- Output endpoint and input endpoint fields are similar but not interchangeable. For example, output pin-sense and input pin-sense fields use different generated register names, and output endpoint audio controls may have additional sink-info/audio-descriptor/lipsync fields outside this chunk.
- Indexed endpoint access requires correct selector/data sequencing. Using the right field mask with the wrong indexed register ID or stale endpoint index can read or write unrelated codec state.
- Multichannel enable fields pack enable, mute, and channel-id values for eight logical channels across two registers. Off-by-one channel mapping mistakes can produce valid-looking register values with wrong speaker layout.
- Format and stream fields are compact bitfields. Incorrect values for sample base, divisor, multiplier, bits per sample, stream type, or channel count can break only specific audio modes.
- Status, flag, mask, and type fields often have side effects. Incorrect handling of audio enabled/disabled/format-changed flags or unsolicited-response force bits can cause missed events or interrupt storms.
- `PRESENCE_DETECT`, `INFOFRAME_VALID`, `INPUT_ACTIVITY`, and LPIB snapshots are live or latched observations. Tests must account for timing, power state, and stream activity rather than assuming static readback.

## Test Signals

Useful validation signals for this chunk are build-time consistency checks plus DCN321 hardware audio behavior:

- Build AMDGPU Display Core with DCN321 enabled and ensure `dcn321_resource.c`, audio register tables, and `dce_audio` consumers resolve all referenced Azalia endpoint shift/mask names.
- Generated-header consistency checks: every expected field should have a matched `__SHIFT` and `_MASK`, masks should fit within 32 bits, repeated `AZF0INPUTENDPOINT0-7` field layouts should be identical where the hardware database intends them to be, and indexed register IDs in `dcn_3_2_1_offset.h` should have matching field names in this header.
- HDMI/DP audio smoke tests on DCN321 hardware: monitor audio device enumeration, hotplug/unplug, modeset with audio enabled, suspend/resume, stream disable/enable, and format renegotiation.
- Audio format coverage: 2-channel and multichannel LPCM, different sample rates and sample widths, HBR audio when supported, non-audio/professional/copy bits, and IEC channel-status override behavior.
- Channel mapping validation with layouts that exercise `MULTICHANNEL_ENABLE`, `MULTICHANNEL_ENABLE2`, `CHANNEL_ALLOCATION`, `CHANNEL_ID`, and `STREAM_ID`.
- Event-path validation for audio enabled/disabled/format-changed interrupts, unsolicited responses, hot-plug control, format-change response, and remote keepalive behavior.
- Diagnostics using LPIB/LPIB timer snapshots, cyclic-buffer wrap counts, digital-output active state, input activity, presence detect, infoframe validity, and HBR capability/enable readback.

## Chunk Boundary Notes

Line 54449 begins after the comment and first fields for `AZF0ENDPOINT7_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_4`; adjacent prior chunk coverage is needed for the complete register group. Lines 54534-56597 cover all eight generated input endpoint blocks, and line 56598 closes the header guard. The merge/reconciliation lane should combine this report with adjacent `dcn_3_2_1_sh_mask.h` chunks before producing the final per-file research document.
