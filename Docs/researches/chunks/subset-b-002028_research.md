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
