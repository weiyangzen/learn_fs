# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 14926-17341

## Scope

This chunk is a generated DCN 3.0.3 register-field mask slice from `dcn_3_0_3_sh_mask.h`. It contains preprocessor constants only: `_SHIFT` values for field bit positions, `_MASK` values for unshifted 32-bit register masks, and comment markers that name registers and hardware address blocks. There are no C functions, structs, enums, local variables, loops, branches, or runtime data structures in this range.

The slice starts in the tail of the `OTG0` timing-generator definitions, covers the full `dce_dc_optc_otg1_dispdec` `OTG1` register-field surface, then moves through OPTC miscellaneous and perfmon registers, DIO I2C/DDC, DIO scratch/power/clock/reset/generic-interrupt registers, HPD0/HPD1 hotplug detect registers, DIO perfmon registers, all of DP AUX0, and the beginning of DP AUX1 through its interrupt-control fields.

## Purpose And Hardware Surface

The purpose of this header range is to provide the bit layout ABI between AMDGPU Display Core code and DCN 3.0.3 display hardware. Companion offset headers provide register addresses; this mask header provides field positions and masks used by register helper macros to encode values, decode MMIO readbacks, and perform read/modify/write updates without hard-coding numeric bit positions in functional code.

Major hardware areas represented here:

- `OTG0` tail fields for global sync status, master update lock, global swap lock, vupdate keepout, global/manual flow control, dynamic refresh rate timing interrupts, DTO constants, DSC start position, pipe-update status, and spare state.
- `OTG1` timing generator fields for horizontal/vertical totals, blanking, sync, trigger A/B, force-count-now, flow control, stereo/interlace, status/counters, snapshots, interrupts, update locks, blank color, vertical interrupts, CRC windows/data, static screen detection, 3D structure, GSL vsync gap, clocks, vstartup/vupdate/vready, master/global update locks, DRR, DSC start position, pipe-update status, and spare state.
- OPTC miscellaneous muxing and power fields: display writeback source selection, GSL ready/timing source selection, OPTC clock control, ODM memory power controls/status, and OPTC spare register.
- `DC_PERFMON10` for OPTC perfmon counters and `DC_PERFMON11` for DIO perfmon counters, including event selection, counter state, run/stop control, counter-value interrupt status/ack, and low/high readback.
- DIO I2C/DDC registers for software I2C control/arbitration, interrupt control, software status, DDC1/DDC2 hardware status, DDC speed/setup, four transaction descriptors, indexed data, EDID detect control, and DDC read-request interrupts.
- DIO common registers for scratch words, light-sleep memory power state/control for I2C and DIG/DP links, DIO clock gating, power-management clock gating, DIG soft reset, additional clock controls, HDMI RX status timer control, and generic interrupt message/clear.
- HPD0 and HPD1 hotplug-detect fields for interrupt status/control, connection/RX interrupt timers, fast-train sequencing, and toggle filter delays.
- DP AUX0 register fields for AUX enable/reset, software AUX transactions, arbitration between software and DMCU users, interrupt status/ack/mask bits, software/link-service status, indexed SW/LS data windows, DPHY TX/RX controls/status, GTC sync control/error/status, and PHY wake request/acknowledge.
- DP AUX1 starts at the end of the chunk and includes AUX control, software-control, arbitration, and interrupt-control fields.

## Important Definitions

The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit.
- `<REGISTER>__<FIELD>_MASK` gives the field's raw bitmask within the 32-bit register.
- `// addressBlock: ...` comments identify the hardware register aperture for following definitions.
- `//<REGISTER>` comments group field definitions by register.

Important field families in this chunk:

- Timing-generator fields use 15-bit-ish horizontal/vertical coordinate masks for totals, blanking, sync points, window start/end coordinates, snapshot positions, CRC windows, and DSC start positions. These are used when the display pipe programs scanout timing and validates live position/status.
- OTG update and lock fields include per-OTG update locks, master update locks, global update lock enables, vupdate keepout ranges, double-buffer pending bits, update-instantly controls, and GSL-controlled master update locking. These coordinate atomic timing updates with vblank/vupdate boundaries.
- DRR fields include vertical total min/max/mid controls, vtotal min event interrupt state, DRR timing-update and vtotal-reach status/clear/mask/type bits, vtotal reach ranges, vtotal change limits, trigger windows, average-frame selection, and last-used vtotal readback. These support variable refresh behavior.
- Trigger and flow-control fields cover TRIGA/TRIGB source selection, pipe selection, polarity, edge detection, frequency selection, delay, occurred/clear bits, manual trigger bits, force-count-now modes, and manual/global flow control selection.
- Stereo/interlace/3D fields expose current/next field, current eye, stereo sync output/selection, eye flag polarity, force-next-eye pending state, 3D structure enable/update mode, frame-count reset/pending/count, and DP-related stereo/field output disables.
- CRC fields include enable, dual-link mode, blank-only, continuous/one-shot pending bits, stereo/interlace modes, CRC selectors, two window sets for CRC0/CRC1, CRC data readbacks for CRC0-CRC3, and signature masks. These are display validation and diagnostics hooks.
- Interrupt fields are split into status, clear/ack, mask/enable, and type fields. Examples include OTG vertical interrupts, vstartup/vupdate/vready/global sync status, GSL vsync gap, HPD connect/RX events, I2C software/hardware completion, DDC read requests, AUX SW/LS/GTC events, and perfmon counter interrupts.
- Perfmon controls for `DC_PERFMON10` and `DC_PERFMON11` provide event selectors, counter-value selection, increment mode, run-enable mode, hardware stop controls, count-off selection, active state, perfmon state, report count, clock enable, run start/stop selectors, interrupt status/ack bits for counters 0-7, and low/high counter readout.
- I2C/DDC fields represent both software-driven I2C and hardware DDC/EDID detection. Transaction descriptors include read/write direction, stop-on-NACK, start/stop bits, and transfer count. The data register uses an index, data byte, read/write bit, and index-write bit.
- AUX fields distinguish software AUX, link-service AUX, GTC sync AUX, DPHY controls, data windows, arbitration, and wake flow. Status fields enumerate timeout, overflow, HPD disconnect, partial byte, non-AUX mode, invalid start/stop/sync/reply, NACK, reply byte count, and arbitration state.
- DIO and OPTC clock/power fields are single-bit or small enum controls for light sleep, clock gating, memory power force/disable/state, soft reset, power-management gating, and clock-on/busy status.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior appears only when other AMDGPU Display Core code combines these constants with register addresses and helper macros. A typical usage pattern is:

1. Select the DCN 3.0.3 register address from a companion offset/header table.
2. Use this chunk's `_SHIFT` and `_MASK` macros to pack or unpack the desired field.
3. Perform an MMIO read, write, or read/modify/write through the display register abstraction.
4. Let hardware retain, consume, update, or clear the register-backed state according to the register semantics.

The state represented here is hardware state, not in-memory driver state:

- OTG timing, lock, DRR, stereo/interlace, CRC, blank color, snapshot, and global sync fields persist in timing-generator registers until reprogrammed, reset, or power-gated.
- Status and counter fields are volatile readbacks generated by display hardware, for example current scan position, frame counts, vblank/hsync/vsync state, pipe update pending state, perfmon values, I2C/AUX transaction state, and HPD sense state.
- ACK, clear, and reset fields are write paths that mutate hardware-latched events or state machines. They should not be treated as durable configuration bits.
- I2C/AUX transaction descriptors and data windows are shared hardware queues/register windows. Their state depends on arbitration, transaction completion, abort/timeout/NACK conditions, and ownership by software or DMCU/firmware clients.
- Clock, memory-power, and light-sleep controls influence whether related display subblocks are usable. Driver code must sequence these with register access and reset/power transitions.

The masks themselves do not enforce ordering. Correct code must still respect display hardware sequencing, such as holding update locks while changing double-buffered timing fields, clearing interrupt latches after service, waiting for reset-done or clock-on status, programming I2C/AUX transaction data before asserting go bits, and avoiding live timing/CRC/DRR changes at unsafe scan positions.

## Dependencies And Integration Points

This chunk integrates with:

- Companion DCN 3.0.3 register offset/address headers, especially the matching `dcn_3_0_3_offset.h` style generated headers.
- AMDGPU Display Core register access helpers that consume register-name, mask, and shift tables for `REG_GET`, `REG_SET`, `REG_UPDATE`, and related operations.
- OTG/OPTC timing code that programs scanout geometry, vblank/vsync timing, DRR, global swap lock, update locks, CRC capture, stereo/interlace, DSC start position, and pipe update synchronization.
- IRQ code for OTG vertical interrupts, vstartup/vupdate/vready, GSL gap, HPD, I2C/DDC completion, DDC read requests, AUX completion/error, and perfmon counter interrupts.
- AUX/DDC/I2C code that performs DisplayPort AUX and monitor EDID transactions, handles HPD disconnects and NACK/timeouts, and arbitrates AUX register ownership with firmware/DMCU.
- Hotplug-detect code using HPD0/HPD1 sense, RX interrupt, debounce/toggle filter, connection timers, and fast-train delay/enable fields.
- Clock and power-management paths that control DIO/OPTC/DIG clocks, soft resets, light sleep, memory power, HDMI RX status timers, and power-management gating.
- Debug, validation, and diagnostics tooling that reads OTG status/counters, CRC signatures, perfmon counters, DIO scratch registers, AUX/I2C status, and HPD sense/timer state.

The range depends on generated-name consistency across DCN 3.0.3 headers and driver tables. Because these are preprocessor macros, a stale field name is a compile-time failure only where referenced; a stale numeric mask or shift can compile cleanly and cause runtime hardware misprogramming.

## Risks And Maintenance Notes

- Numeric drift from the ASIC register specification is the primary risk. A wrong mask or shift can write the wrong bits in MMIO registers and corrupt timing, interrupt, power, AUX/DDC, or hotplug behavior.
- The chunk is highly repetitive across OTG0/OTG1, perfmon10/perfmon11, HPD0/HPD1, and AUX0/AUX1. Copying code between instances with the wrong prefix can target the wrong pipe, interrupt source, AUX channel, or hotplug block.
- Clear/ACK fields are side-effecting. Using them in generic read/modify/write paths without care can unintentionally drop pending interrupts, AUX/GTC errors, HPD events, perfmon events, or force-count/snapshot/DRR state.
- Update-lock and double-buffer fields are sequencing-sensitive. Misuse can cause partially applied timing changes, missed vupdate/vready events, visible glitches, or inconsistent pipe update status.
- DRR and vtotal fields interact with scanout timing and frame pacing. Incorrect min/max/mid/range/window programming can produce unstable variable-refresh behavior.
- I2C and AUX transaction fields include timeout, overflow, invalid symbol, NACK, HPD disconnect, and arbitration state. Ignoring these status bits can lead to stuck transactions, failed EDID reads, or DisplayPort link-management failures.
- DIO clock, reset, and light-sleep fields can make subsequent register reads/writes unreliable if toggled while dependent subblocks are active.
- Full-width fields such as DTO phase/modulo, scratch registers, perfmon low values, I2C data windows, and AUX data windows provide no type or range checking. Callers must validate widths, indices, ownership, and transaction lengths.
- The chunk ends partway through DP AUX1. Later chunks must complete AUX1 coverage; this document should not be treated as the full per-file register map.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, generated-header consistency, and hardware/display smoke tests:

- Build AMDGPU with DCN 3.0.3 support and ensure all referenced generated macro names resolve.
- Run static/generated-header checks that every field has a matching `_SHIFT`/`_MASK` pair, masks fit in 32 bits, and fields do not overlap unexpectedly within each register.
- Exercise display modesetting on pipes using OTG1, including timing programming, vblank/vsync interrupts, update locks, double-buffered updates, and pipe-update status.
- Test DRR/VRR behavior and verify vtotal min/max/mid, DRR timing-update, vtotal-reach, and vupdate/vready signals behave as expected.
- Use display CRC diagnostics to enable CRC capture, configure windows/selectors, read CRC0-CRC3 data, and confirm one-shot/continuous pending bits clear correctly.
- Exercise hotplug on HPD0 and HPD1, including debounce/toggle filtering, RX interrupt handling, connection timers, fast-train delays, and interrupt acknowledgements.
- Run EDID/DDC tests over DDC1/DDC2 and software I2C paths, checking transaction counts, start/stop/stop-on-NACK behavior, completion interrupts, NACK/timeout/abort states, and EDID detect state.
- Run DisplayPort AUX tests over AUX0 and the initial AUX1 register set, including SW and LS transactions, AUX arbitration with firmware/DMCU, HPD disconnect handling, timeout/overflow/invalid-reply reporting, data-window indexing, and interrupt ACK/mask behavior.
- Validate DIO/OPTC power and clock transitions around suspend/resume, runtime power management, display blank/unblank, and DIG soft reset.
- Configure `DC_PERFMON10` and `DC_PERFMON11`, sample counter low/high values, trigger counter interrupts, and verify status/ack bits clear without losing counter state.

## Chunk-Specific Summary

Lines 14926-17341 define a dense DCN 3.0.3 register-field surface rather than executable code. The most important responsibilities in this slice are OTG0 tail and OTG1 timing-generator control, atomic update synchronization, DRR, CRC, HPD, I2C/DDC, AUX0 and partial AUX1 transaction handling, DIO/OPTC clock and memory-power controls, and display perfmon counters. Correctness is measured by exact generated mask/shift values, instance-correct macro use, and successful hardware behavior under modeset, interrupt, hotplug, AUX/DDC, power-management, CRC, DRR, and perfmon workloads.
