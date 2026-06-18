# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 4728-7202

## Scope

This chunk is a generated DCN 3.0.2 register field definition slice from `dcn_3_0_2_sh_mask.h`. It contains only preprocessor constants: every meaningful entry is a register-field `_SHIFT` and matching `_MASK` value, plus comment markers naming register blocks. There are no C functions, structs, enums, or executable control-flow constructs in the range. Its purpose is to provide the bit layout contract consumed by AMDGPU Display Core register access helpers when they read, write, update, acknowledge, or decode display hardware registers.

The range begins in the middle of the `DC_GPU_TIMER_START_POSITION_FLIP_AWAY` definitions, covers the tail of display interrupt status continuation registers, then covers interrupt destination registers for many display subblocks. It then transitions through the `dce_dc_dmu_dmcub_dispdec` DMCUB register block, MCIF writeback and MMHUBBUB/VGAIF blocks, two display perfmon blocks, and Azalia HDA stream/endpoint/audio control blocks. Because this file is generated from ASIC register specifications, correctness depends on exact numeric parity with hardware documentation and the companion address header for the same IP version.

## Purpose And Hardware Surface

The constants define bit positions and bitmasks for DCN 3.0.2 display registers. Driver code can combine these with register addresses from companion `*_offset.h` headers and with helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, or generated register table initializers. The `_SHIFT` constants express the low bit of each field, while `_MASK` constants express the full raw register mask before shifting.

Major hardware areas represented in this chunk:

- Display interrupt status continuation: `DISP_INTERRUPT_STATUS_CONTINUE23`, `CONTINUE24`, and `CONTINUE25` expose pending status bits for DCPG domain power transitions, DSC underflow/core/perfmon events, DMCUB inbox/outbox/timer/general/fault events, MMHUBBUB warmup, and ABM2-ABM5 events.
- Interrupt routing/destination: `DCCG_INTERRUPT_DEST`, `DMU_INTERRUPT_DEST`, `DMU_INTERRUPT_DEST2`, `DCPG_INTERRUPT_DEST`, `DCPG_INTERRUPT_DEST2`, `MMHUBBUB_INTERRUPT_DEST`, `WB_INTERRUPT_DEST`, `DCHUB_INTERRUPT_DEST`, `DCHUB_PERFCOUNTER_INTERRUPT_DEST`, `DCHUB_INTERRUPT_DEST2`, `DPP_PERFCOUNTER_INTERRUPT_DEST`, `MPC_INTERRUPT_DEST`, `OPP_INTERRUPT_DEST`, `OPTC_INTERRUPT_DEST`, `OTG0_INTERRUPT_DEST` through `OTG5_INTERRUPT_DEST`, `DIG_INTERRUPT_DEST`, `I2C_DDC_HPD_INTERRUPT_DEST`, `DIO_INTERRUPT_DEST`, `DCIO_INTERRUPT_DEST`, `HPD_INTERRUPT_DEST`, `AZ_INTERRUPT_DEST`, `AUX_INTERRUPT_DEST`, and `DSC_INTERRUPT_DEST` define which display events are routed to interrupt destinations.
- DMCUB register block: `DMCUB_REGION*`, `DMCUB_REGION3_CW*`, interrupt enable/ack/status/type registers, external interrupt status/context/ack, fault address registers, secure and memory controls, inbox/outbox ring base/size/read/write pointers, timers, scratch registers, control, GPINT data registers, low-power wake, memory power, timer current, and processor ID.
- MCIF writeback block for `mcif_wb0`: buffer manager control/status, four writeback buffer status/status2 registers, pitch, Y/C base addresses and high address parts, arbitration, SCLK/P-state/watermark controls, clock/self-refresh controls, luma/chroma sizes, per-buffer resolution, VMID, and timing timeout fields.
- MMHUBBUB and VGAIF block: writeback P-state/watermark and warmup controls, warmup base/region/VMID, outstanding counters, VGA source split, memory power status/control, clock control, soft reset, DMU interface error status, and client unit IDs.
- Display performance monitor blocks: `DC_PERFMON3_*` for MMHUBBUB perfmon and `DC_PERFMON4_*` for Azalia perfmon, including counter control, counter control 2, counter state, perfmon control, counter-value interrupt misc, and low/high value readout fields.
- Azalia HDA display audio: stream index/data windows for streams 0-7, endpoint index/data windows for endpoints 0-7, `AZ_CLOCK_CNTL`, and `AZALIA_CONTROLLER_CLOCK_GATING`.

## Important Definitions

The primary API surface is the macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field shift count.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the unshifted register word.
- Comment-only `// addressBlock: ...` lines group subsequent register definitions by hardware aperture.
- Comment-only `//<REGISTER>` lines group the field macros for each register.

Notable field families:

- Interrupt status bits are single-bit flags, commonly at direct bit positions. Examples include DCPG power up/down bits in `DISP_INTERRUPT_STATUS_CONTINUE23`, DMCUB inbox/outbox/timer/fault bits in `DISP_INTERRUPT_STATUS_CONTINUE24`, and ABM ready/backlight update bits in `DISP_INTERRUPT_STATUS_CONTINUE25`.
- Interrupt destination bits are also single-bit selectors. They mirror the status-event taxonomy and let driver code select routing for OTG timing events, HUBP vblank/vline/timeout/flip events, HPD/RX events, AUX/DDC events, DSC error/perfmon events, DMCUB mailbox events, and display block perf counters.
- DMCUB region address fields use large address masks, for example low offsets starting at bit 8 with `0xFFFFFF00L`, high offsets with `0x0000FFFFL`, top-address masks like `0x1FFFFFFFL`, and enable bits at bit 31. Region 3 is subdivided into code windows `CW0` through `CW7`, each with base, top, offset, and offset-high definitions.
- DMCUB mailbox registers use full-width or size/pointer masks for firmware/driver ring-buffer communication. The register names distinguish inboxes from host to DMCUB and outboxes from DMCUB to host, each with base address, size, write pointer, and read pointer.
- DMCUB interrupt registers separate enable, acknowledge, current status, and type. This makes it possible to configure interrupt generation, inspect fault or mailbox completion state, and clear individual bits without conflating status and control semantics.
- MCIF writeback buffer fields track buffer ownership and progress through active, software-locked, VCE-locked, overflow, disabled, mode, buffer tag, next buffer, current line, new content, color depth, TMZ, Y/C overrun, and eye-flag fields. The duplicated buffer 1-4 layout means writeback clients must use the instance-matched register and field names.
- Perfmon controls provide event selection, counter value selection, increment mode, hardware control source, run enable mode, restart, interrupt enable, off-mask, active state, counter selection, counted value type, hardware stops, count-off selection, perfmon run start/stop controls, interrupt status/ack bits, and low/high counter readout fields.
- Azalia stream and endpoint windows are indirect index/data pairs. Stream index fields include register index and write-enable bits; endpoint index fields expose the endpoint register index, while data registers are full 32-bit payload fields.

## Control Flow And State Behavior

There is no local control flow in this header. Runtime behavior emerges only when other driver code uses these constants to manipulate MMIO registers. The likely flow is:

1. Display code selects a register address from the matching DCN 3.0.2 offset header.
2. It uses a field macro from this file to encode a value, decode a readback, or set/clear a bit.
3. Hardware persists the resulting state in display registers until overwritten, reset, power-gated, or acknowledged according to the register semantics.

The state represented by these fields is entirely hardware-backed:

- Interrupt status and fault fields are volatile state generated by display hardware or DMCUB firmware. ACK fields are write paths used to clear latched events.
- Interrupt destination fields persist interrupt routing policy inside display hardware.
- DMCUB region, mailbox, scratch, control, and memory power fields persist firmware boot/configuration state and host-firmware communication state.
- MCIF writeback buffer fields persist live buffer ownership, addresses, dimensions, and error/status state for display writeback.
- MMHUBBUB/VGAIF fields persist memory-client controls, warmup setup, outstanding counter state, reset controls, and clock/memory-power settings.
- Perfmon fields persist counter configuration and expose volatile counter values and interrupt states.
- Azalia stream/endpoint indirect windows persist selected index/write-enable state and pass data to or from the underlying HDA display-audio registers.

The generated masks do not enforce ordering. Driver code must still respect hardware sequencing, for example disabling interrupts before changing routing, acknowledging latched interrupt bits after service, programming DMCUB region windows before firmware access, updating mailbox pointers in the expected order, and avoiding writeback buffer address changes while a buffer is active or locked.

## Dependencies And Integration Points

This header is not useful by itself; it integrates with:

- Companion DCN 3.0.2 register address headers, especially `dcn_3_0_2_offset.h`, which provide the MMIO register offsets for the names defined here.
- AMDGPU Display Core register helper layers that combine register offsets, masks, and shifts into safe read/modify/write operations.
- DMCUB host interface code that initializes DMCUB memory regions, ring buffers, scratch registers, GPINT paths, fault handling, and interrupt enable/ack/status registers.
- IRQ handling code that maps display block events into Linux DRM/AMDGPU interrupt handling paths.
- Display timing/pipe code for OTG, HUBP, DPP, OPP, MPC, DCCG, DSC, DIO/DCIO, AUX, HPD, DDC/I2C, and writeback paths.
- Display audio code using Azalia stream and endpoint indirect register windows.
- Debug/performance tooling that configures or samples DC perfmon counters.

The chunk also depends on exact naming consistency across generated headers and driver register tables. A typo or stale field name can break compile-time macro expansion even if the numeric value is correct.

## Risks And Maintenance Notes

- Generated-header drift is the main risk. Any mismatch between `_SHIFT`/`_MASK` values and the ASIC specification can silently corrupt unrelated bits during register updates or cause interrupt/fault handling to read the wrong bit.
- Interrupt status and destination definitions are dense and repetitive. Copying an `OTG`, `HUBP`, `DPP`, `DSC`, `ABM`, `DCPG`, `AUX`, `HPD`, or `DMCUB` field across instances without changing the instance number can route or clear the wrong event.
- Several fields are ACK bits. Treating ACK masks like ordinary persistent control bits can clear pending events or hide fault evidence.
- DMCUB address-window fields are security- and stability-sensitive. Incorrect base/top/offset masks can expose the firmware to the wrong memory region, generate undefined-address faults, or break firmware boot/mailbox traffic.
- MCIF writeback buffer fields include active/locked/overflow/TMZ/Y-C overrun state. Misprogramming them can corrupt captured frames, trigger underflow/overflow reports, or violate trusted-memory handling.
- Full-width data fields such as mailbox base/data, scratch registers, Azalia data registers, and perfmon low counters carry no range checking in this header. Callers must validate address alignment, size, and ownership constraints separately.
- Because these constants are preprocessor macros, there is no type safety. Incorrectly pairing a mask from one register with a shift from another can compile successfully if done through generic helper code.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, register-table, and hardware smoke tests:

- The AMDGPU driver should compile with DCN 3.0.2 support enabled, proving all referenced macro names still exist.
- Register helper tests or static checks should verify that every generated field has a mask/shift pair and that shifted masks fit within 32 bits.
- IRQ smoke tests should exercise hotplug, AUX/DDC completion, vblank/vline, flip, DSC error/underflow, DMCUB mailbox, and DMCUB fault paths and confirm the expected status/ack/destination bits are used.
- DMCUB firmware boot tests should confirm region windows, inbox/outbox pointers, scratch registers, GPINT data, and undefined-address/fetch/write fault reporting work.
- Display writeback tests should capture through MCIF writeback and check buffer active/lock/tag/current-line/new-content/overflow status transitions.
- Display audio tests should validate Azalia stream and endpoint indirect index/data access and audio enable/format-change interrupt reporting.
- Perfmon diagnostics should configure `DC_PERFMON3` and `DC_PERFMON4`, trigger counter interrupts, read low/high values, and acknowledge counter interrupt status bits.

## Chunk-Specific Summary

Lines 4728-7202 define a broad DCN 3.0.2 register-field surface rather than executable behavior. The most important responsibilities in this slice are interrupt status/routing for display subsystems, DMCUB memory/mailbox/interrupt/fault control, MCIF writeback and MMHUBBUB memory-client control, perfmon counter programming, and Azalia display-audio indirect register access. The constants are low-level ABI between the driver and display hardware; correctness is measured by exact field values, consistent generated naming, and successful hardware register behavior under interrupt, firmware, writeback, performance-monitor, and audio workloads.
