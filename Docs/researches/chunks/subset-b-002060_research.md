# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 8816-11033

## Purpose

This chunk is generated AMD DCN 3.5 register field metadata. It contains no executable driver logic; it publishes C preprocessor constants for field shifts and bit masks in `dcn_3_5_0_sh_mask.h`. Consumers pair these `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros with the matching DCN 3.5 register-offset header to build typed register tables used by AMDGPU display, DMUB, IRQ, writeback, memory-hub, and diagnostic code.

The requested range starts at `DISP_INTERRUPT_STATUS_CONTINUE19`, covers the rest of the display interrupt-status continuation chain through `CONTINUE25`, then covers GPU timer start-position fields, per-block interrupt-destination routing fields, DMCUB/RBBMIF security and mailbox fields, MCIF writeback buffer-manager and buffer fields, MMHUBBUB/warmup/power fields, DC perfmon instance 3 and the start of instance 4, and finally the Azalia stream index/data registers plus `AZ_CLOCK_CNTL`.

Although the repository path is under a local `ceph-client` source mirror, this file is AMD display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, locks, or callbacks in this range. The exported interface is entirely the generated macro namespace:

- `REGISTER__FIELD__SHIFT`: the bit offset for `FIELD` within `REGISTER`.
- `REGISTER__FIELD_MASK`: the bit mask for the same field.

Major macro families in this chunk:

- `DISP_INTERRUPT_STATUS_CONTINUE19` through `DISP_INTERRUPT_STATUS_CONTINUE25`: status bits for Azalia endpoint audio changes, OTG vupdate/vstartup/vready/no-lock and DRR events, I2C/DDC done/read-request events, DMCUB outbox, AUX/DIG/HPD/display block events, and continuation bits linking the status chain.
- `DC_GPU_TIMER_START_POSITION_*`: compact per-pipe start-position fields for vready, flip, vupdate-no-lock, and flip-away timing on display pipes D1 through D6.
- `*_INTERRUPT_DEST`: interrupt routing/destination fields for DCCG, DMU, DCPG, MMHUBBUB, WB, DCHUB, DPP perf counters, MPC, OPP, OPTC, OTG0-OTG5, DIG, I2C/DDC/HPD, DIO, DCIO, HPD, AZ, AUX, DSC, and HPO blocks.
- `DMCUB_*` and `RBBMIF_*`: DMCUB security, region/window, mailbox, timer, scratch, GPINT, interrupt enable/ack/status/type, memory power, reset/control, and fault-address fields, plus RBBMIF timeout and status fields.
- `MCIF_WB_*`: display writeback buffer-manager control/status, per-buffer address/status/resolution, pitch, arbitration, p-state/watermark, security, VMID, and minimum-time-to-output fields.
- `MMHUBBUB_*`, `WBIF*`, `DMU_IF_ERR_STATUS`, and `MULTI_LEVEL_QOS_CTRL`: memory-hub warmup, low-power, clock-gating, reset, watermark, outstanding-counter, and error-status fields.
- `DC_PERFMON3_*` and partial `DC_PERFMON4_PERFCOUNTER_CNTL`: display perf counter event selection, counted-value selection, increment/run/stop controls, counter state, interrupt status/ack, counter high/low values, and perfmon control fields.
- `AZF0STREAM0` through `AZF0STREAM7` and `AZ_CLOCK_CNTL`: indexed Azalia stream register access/data fields and audio clock-gating/test-clock selection fields.

## Control Flow

This header has no runtime control flow. It is compiled into control flow through register helper macros in AMD display code:

1. DCN 3.5 display modules include `dcn_3_5_0_sh_mask.h` alongside the matching offset header.
2. Register-list macros token-paste register and field names into shift/mask table members. For example, DMUB code uses `DMUB_SF(DMCUB_INTERRUPT_ENABLE, DMCUB_GPINT_IH_INT_EN)`, IRQ code uses `IRQ_REG_ENTRY_DMUB(... DMCUB_INTERRUPT_ENABLE, DMCUB_OUTBOX1_READY_INT_EN, DMCUB_INTERRUPT_ACK, DMCUB_OUTBOX1_READY_INT_ACK)`, and MMHUBBUB/writeback code uses `SF(MCIF_WB_BUFMGR_SW_CONTROL, MCIF_WB_BUF_ADDR_FENCE_EN, mask_sh)`.
3. Runtime paths call helpers such as `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, `REG_SET`, and DMUB register helpers. Those helpers use the generated shift/mask constants to preserve unrelated bits while setting, clearing, reading, or acknowledging fields.
4. Hardware sequencing is supplied by the consuming modules. This chunk only says where a field lives; it does not encode whether a field is read-only, write-one-to-clear, sticky, self-clearing, clock-gated, reset-sensitive, or safe to access while a display block is powered down.

## State And Persistence Behavior

The chunk stores no software state and persists nothing on its own. It describes MMIO-backed GPU display state.

Represented state includes interrupt status/routing state, DMCUB firmware control windows and mailboxes, RBBMIF security/timeout state, writeback buffer ownership and address state, MMHUBBUB warmup and power-management state, display perfmon counters, Azalia stream register index/data windows, and audio clock-gating controls.

Persistence is hardware-defined. Configuration fields generally retain values until modeset, block reset, power gating, suspend/resume, or ASIC reset. Status, interrupt, timeout, fault, counter, and ack fields can be sticky, edge-triggered, read-only, write-one-to-clear, or self-clearing depending on the underlying register. Because these are untyped macros, the consuming driver code must know the correct ordering for enabling interrupts, acknowledging status, programming DMCUB windows, changing MCIF buffers, and reading perf counters.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h` for the corresponding MMIO offsets and base-index selectors.
- AMD display register helper infrastructure that consumes `mask` and `shift` tables, including `REG_*`, `SF`, `SRI`, `SRI2`, `DMUB_SR`, `DMUB_SF`, and `IRQ_REG_ENTRY*` style macros.

Representative integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c` and `dmub_dcn35.h`, which include this header and consume `DMCUB_*` fields for DMUB reset, setup windows, mailboxes, scratch/GPINT state, and interrupt control.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn35/irq_service_dcn35.c`, which uses DMCUB interrupt enable/ack fields for the DMCUB outbox IRQ path and uses generated interrupt register metadata for display IRQ service tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn32/` and related writeback/memory-hub code, whose shared register lists consume `MCIF_WB_*` and `MMHUBBUB_*` shift/mask definitions for writeback buffer programming, address fences, watermarks, memory power, warmup, and reset.
- Display diagnostics and performance-monitoring paths that program `DC_PERFMON*` fields to select events, run counters, read high/low counter values, and handle counter interrupts.
- Audio/display output paths that rely on `AZ_INTERRUPT_DEST`, `AZF0STREAM*`, and `AZ_CLOCK_CNTL` fields for Azalia stream access, audio endpoint events, and audio clock gating.

## Risks And Edge Cases

- Shift/mask drift is the primary risk. These macros are untyped constants; an incorrect bit position can compile cleanly while silently changing the wrong hardware field.
- Interrupt fields are especially sensitive. Bad `DISP_INTERRUPT_STATUS_CONTINUE*`, `*_INTERRUPT_DEST`, or DMCUB enable/ack masks can cause stuck interrupts, missed hotplug, missed vblank/vupdate, I2C/DDC completion loss, audio endpoint event loss, or interrupt storms.
- Repeated instance blocks are copy-sensitive. OTG0-OTG5, MCIF writeback buffers 1-4, DMCUB region3 cache windows 0-7, Azalia streams 0-7, and perfmon instances use near-identical field layouts; an instance-specific typo may only fail on one pipe, stream, buffer, or diagnostic path.
- DMCUB fields cross a firmware boundary. Incorrect region top/offset/high/enable, mailbox pointer, GPINT, scratch, or fault-address field metadata can break firmware boot, command submission, outbox handling, secure-memory windows, or fault diagnosis.
- MCIF writeback fields carry address, pitch, size, VMID, security, and buffer-state information. Wrong masks can corrupt captured frames, program the wrong buffer, mishandle TMZ/security state, or fence/lock buffers incorrectly.
- Power and clock fields in MMHUBBUB, MCIF, WBIF, DMCUB, and Azalia areas can be ignored or harmful when accessed while a block is gated, reset, or not clocked.
- Perfmon fields may have read/ack ordering constraints. Incorrect counter selection, state selection, interrupt ack, or high/low value handling can produce misleading diagnostics without obvious functional failures.
- The chunk boundary is artificial. It begins in the middle of the interrupt continuation definitions and ends inside the `DC_PERFMON4_PERFCOUNTER_CNTL` field group; adjacent chunks are needed for complete file-level conclusions.

## Test Signals

Useful validation signals are a mix of generated-header consistency checks and hardware behavior:

- Build AMDGPU/DC with DCN 3.5 support enabled; missing or renamed macros should fail in DMUB, IRQ, writeback/MMHUBBUB, audio, and perfmon register-table construction.
- Mechanically verify that each field in lines 8816-11033 has matching `__SHIFT` and `_MASK` definitions where the generated pattern expects both, and that masks align with `SHIFT` values and field widths.
- Diff this chunk against AMD's authoritative DCN 3.5 register database and nearby generated headers such as `dcn_3_5_1_sh_mask.h` where compatibility is expected.
- Exercise IRQ-heavy display flows: hotplug, EDID/DDC reads, DP AUX transactions, vblank/vupdate, vstartup/vready/no-lock, DRR v-total reach, HPD, DMCUB outbox, audio endpoint enable/disable/format changes, and suspend/resume.
- Validate DMUB firmware paths: reset/release, backdoor load/window setup, inbox/outbox command traffic, GPINT handling, scratch registers, fault reporting, and secure-region behavior.
- Test display writeback capture with multiple buffers, planar and packed formats, address-fence enablement, buffer locks, overrun/slice interrupts, VMID/security settings, watermarks, p-state changes, and resume.
- Exercise MMHUBBUB warmup, memory power, clock gating, soft reset, low-power transitions, and outstanding-counter diagnostics.
- Program and read DC perfmon counters, including event selection, run/stop conditions, counter overflow/interrupt ack, and high/low counter reads.
- Watch kernel logs and display diagnostics for stuck interrupts, AUX/I2C timeouts, hotplug storms, blank displays, audio dropouts, DMUB command timeouts, writeback corruption, MCIF overflows, power-gating failures, and inconsistent perf counter results.

## Cross-Chunk Notes

Previous chunks own the earlier DCN 3.5 shift/mask definitions, including the beginning of the display interrupt-status chain before `CONTINUE19`. Later chunks continue `DC_PERFMON4_PERFCOUNTER_CNTL` and cover the remaining field metadata in `dcn_3_5_0_sh_mask.h`. The final per-file research document should merge adjacent chunks before making complete claims about all interrupts, all perfmon instances, or the complete DCN 3.5 register field map.
