# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 2497-4770

## Scope And Purpose

This chunk is a generated AMD DCN 3.0.1 register shift/mask header section. It exports C preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for display microcontroller, interrupt-routing, display interrupt decoder, and GPU timer registers. The companion offset header provides register addresses; this file provides the bitfield layout used by AMD display register helpers.

The requested range starts in the middle of `DMCU_INTERRUPT_STATUS`, after its field shifts and early masks were emitted in the previous chunk. It then covers DMCU interrupt status, host/UC enable masks, XIRQ routing, firmware scratch and mailbox registers, performance-monitor interrupt status/routing, DisplayPort receiver interrupt status/routing, continued DMCU interrupt status/routing, and the beginning of the `dce_dc_dmu_ihc_dispdec` address block. The display interrupt decoder portion covers `DC_GPU_TIMER_*`, `DISP_INTERRUPT_STATUS`, and `DISP_INTERRUPT_STATUS_CONTINUE` through `CONTINUE22`, then ends inside `DC_GPU_TIMER_START_POSITION_FLIP_AWAY`.

There are no functions, structs, runtime branches, or algorithms in this chunk. Its purpose is to keep hardware field metadata available at compile time for register-list macros and memory-mapped register accessors.

## Register Blocks Covered

The DMCU section includes the tail of `DMCU_INTERRUPT_STATUS`, full `DMCU_INTERRUPT_STATUS_1`, interrupt masks to host and microcontroller, and XIRQ selector registers. These fields describe ABM ready/update interrupts, static-screen interrupts, power-domain power-up/down events, vblank events, OTG range timing updates, generic DMCU interrupts, internal UC faults, and register-read timeout events.

The DMCU control and mailbox area includes `DC_DMCU_SCRATCH`, `DMCU_INT_CNT`, `DMCU_FW_CHECKSUM_SMPL_BYTE_POS`, `DMCU_UC_CLK_GATING_CNTL`, `MASTER_COMM_*`, and `SLAVE_COMM_*`. These registers expose scratch storage, interrupt counters, firmware checksum byte sampling, DMCU clock-gating delays, and byte-addressed command/data mailboxes with interrupt flags between host/master and DMCU/slave paths.

The performance-monitor groups include `DMCU_PERFMON_INTERRUPT_STATUS1` through `STATUS5`, matching `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK1` through `MASK5`, and matching `DMCU_PERFMON_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1` through `SEL5`. They define status, enable, and XIRQ routing for MPC, hubp, dpp, opp, otg, dsc, audio, dccg, dio, dchubbub, dchvm, dchubbubmem, dmub, dmcub, azalia, and other display performance/event sources.

The DisplayPort receiver groups include `DMCU_DPRX_INTERRUPT_STATUS1`, `DMCU_DPRX_INTERRUPT_TO_UC_EN_MASK1`, and `DMCU_DPRX_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1`. These define hotplug, AUX, DPRX, training, stream, FEC, MST, SDP, and link-event status/routing fields for multiple DP-related channels.

The continued DMCU interrupt groups include `DMCU_INTERRUPT_STATUS_CONTINUE`, `DMCU_INTERRUPT_TO_UC_EN_MASK_CONTINUE`, `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL_CONTINUE`, `DMCU_INT_CNT_CONTINUE`, `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL_CONT2`, `DMCU_INTERRUPT_STATUS_2`, `DMCU_INTERRUPT_TO_UC_EN_MASK_2`, `DMCU_INT_CNT_CONT2`, and `DMCU_INT_CNT_CONT3`. These extend the base interrupt namespace for additional domain power events, vertical events, ABM events, and later DCN interrupt sources.

The `dce_dc_dmu_ihc_dispdec` address block begins at line 3831. It includes GPU timer start-position fields for vupdate, vstartup, vready, flip, vupdate-no-lock, and the beginning of flip-away. It also includes `DC_GPU_TIMER_READ` and `DC_GPU_TIMER_READ_CNTL` for selecting and reading timer-related positions.

The display interrupt decoder status chain covers `DISP_INTERRUPT_STATUS` and `DISP_INTERRUPT_STATUS_CONTINUE` through `CONTINUE22`. These packed status words expose interrupt presence for OPTC/OTG timing, HPD and HPD RX, AUX completion, DP fast-training and stream-disable events, DIO/DP encoder events, I2C/DDC events, ABM events, DCPG domain power events, OTG vstartup/vready/vupdate-no-lock, GSL/vsync-gap, DRR v-total-reach, underflow, and continue-link bits into the next status word.

## Important APIs, Types, And Macros

The exported API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for packing or extracting a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for that field in the register value.
- Status and clear fields often intentionally share the same bit position and mask, such as `*_OCCURRED` and `*_CLEAR`.
- Enable-mask and XIRQ-selector registers mirror status register field names so firmware-facing routing can be derived from the same interrupt source vocabulary.
- Register comments such as `//DMCU_DPRX_INTERRUPT_STATUS1` and address-block comments such as `// addressBlock: dce_dc_dmu_ihc_dispdec` are generated delimiters for human orientation.

The chunk is consumed indirectly through AMD register helper macros such as `FD_MASK`, `FD_SHIFT`, `REG_FIELD`, `REG_GET`, `REG_SET`, and `REG_UPDATE`. `display/dmub/src/dmub_dcn301.c` includes both `dcn_3_0_1_offset.h` and this header, then builds `dmub_srv_dcn301_regs` by expanding `DMUB_COMMON_REGS()`, `DMCUB_INTERNAL_REGS()`, and `DMUB_COMMON_FIELDS()` into register offsets, masks, and shifts. Older DMCU/ABM/link-encoder paths also use the same style of mailbox and DMCU field definitions through shared DCE/DCN register-list macros.

The display interrupt fields integrate with AMD interrupt source ID headers. For example, `include/ivsrcid/dcn/irqsrcs_dcn_1_0.h` maps several `DISP_INTERRUPT_STATUS_CONTINUE22` fields to source IDs for DCPG domain power events, ABM0 ready/update events, OTG vupdate-no-lock interrupts, and DRR v-total-reach interrupts.

## Control Flow And State Behavior

This header has no direct control flow. Runtime behavior appears when display or DMUB code expands register-list macros and uses the generated masks and shifts to perform memory-mapped register reads and writes.

The DMCU interrupt status registers are event/state latches. Fields named `*_OCCURRED`, `*_INT`, or `*_INTERRUPT` report pending hardware events, while paired `*_CLEAR` fields acknowledge or clear those events. Enable-mask registers persistently control whether sources are routed to host or microcontroller firmware. XIRQ selector fields persistently select which microcontroller interrupt input receives a given event.

The mailbox registers represent persistent command/data state until overwritten by host, firmware, or reset. `MASTER_COMM_DATA_REG*`, `MASTER_COMM_CMD_REG`, and `MASTER_COMM_CNTL_REG` hold host-to-DMCU command bytes and the master interrupt bit. `SLAVE_COMM_DATA_REG*`, `SLAVE_COMM_CMD_REG`, and `SLAVE_COMM_CNTL_REG` hold DMCU-to-host response bytes, a slave interrupt bit, and a message-in-progress indicator.

The performance-monitor and DPRX fields are event routing and observation state. Status bits reflect hardware events from display subsystems; enable masks and XIRQ selectors determine whether those events are delivered to microcontroller firmware and on which interrupt line.

The display interrupt decoder status words form a continuation chain. The high bit in several `DISP_INTERRUPT_STATUS_CONTINUE*` registers points to the next status register, so interrupt service logic must walk or decode the correct continuation level before interpreting an event bit. The timer start-position registers are packed per-display fields, commonly six or eight 3-bit fields at 4-bit spacing, holding hardware-selected start positions for vupdate, vstartup, vready, flip, vupdate-no-lock, and flip-away events.

## Dependencies And Integration Points

This file depends on the DCN 3.0.1 hardware register database and must remain aligned with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h`, which supplies the matching register offsets. A shift/mask without the matching offset, or an offset whose fields drift from this file, breaks register access silently.

The direct DCN 3.0.1 include site found in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c`. That file builds the DMUB service register table using offsets from `dcn_3_0_1_offset.h` and masks/shifts from this header.

The DMCU mailbox fields integrate with shared display-core DMCU and ABM abstractions, including `display/dc/dce/dce_dmcu.h` and `display/dc/dce/dce_abm.h`, where register lists include `MASTER_COMM_DATA_REG1`, `MASTER_COMM_CMD_REG`, `MASTER_COMM_CNTL_REG`, `DMCU_INTERRUPT_TO_UC_EN_MASK`, and related fields. These abstractions use the byte-field masks for firmware commands and interrupt signaling.

The display interrupt decoder fields integrate with the IRQ source ID definitions under `include/ivsrcid/dcn/`. The field names in this chunk are the status-bit side of the mapping between raw display interrupt status words and logical DC interrupt sources.

Power and timing integration is broad. DCPG domain power-up/down bits are consumed by power-management and interrupt paths; OTG vstartup, vready, vupdate-no-lock, GSL, and DRR bits feed timing-sensitive display update logic; HPD/AUX/I2C/DP bits feed connector detection, link management, EDID/DDC transactions, and DisplayPort training/stream event handling.

## Risks And Edge Cases

The highest risk is generated metadata drift. A wrong mask or shift in this file can cause the driver to read a false interrupt source, clear the wrong latched event, route an interrupt to the wrong firmware line, or write mailbox bytes into the wrong positions.

Clear/status aliasing is easy to misuse. Many interrupt fields have identical masks for `*_OCCURRED` and `*_CLEAR`; callers must know whether a register read observes state and whether a write acknowledges it. Treating a clear mask as ordinary configuration can drop pending events.

Continuation status words require exact bit interpretation. A missing or wrong `*_CONTINUE*` bit can stop interrupt decoding before later status words, while an incorrect event bit can report the wrong logical source ID. This is especially relevant around `DISP_INTERRUPT_STATUS_CONTINUE21` and `CONTINUE22`, where DDC, DP, DCPG, ABM, OTG, and DRR events are packed together.

Mailbox fields are byte-packed. Command/data registers use four 8-bit lanes per 32-bit register, so callers must avoid truncation and must preserve unrelated bytes when updating a single field. Interrupt bits in `MASTER_COMM_CNTL_REG` and `SLAVE_COMM_CNTL_REG` are separate from the data payload and should be sequenced after payload writes.

Packed timer start-position fields are narrow. Most per-display timer position fields use 3-bit masks at 4-bit spacing. Overwide values are truncated by masks, and incorrect per-display indexing can shift a timer configuration to another pipe.

The chunk boundaries are partial. The first lines only complete masks for `DMCU_INTERRUPT_STATUS`; the paired shifts are immediately before the requested range. The final lines only start `DC_GPU_TIMER_START_POSITION_FLIP_AWAY`; remaining masks continue in the next chunk. Merge/reconciliation should not treat either boundary register as fully owned by this document alone.

## Test Signals

Build-time signals include successful compilation of DCN 3.0.1 DMUB code that includes this header, especially expansion of `FD_MASK` and `FD_SHIFT` in `dmub_dcn301.c`. Missing or renamed generated macros should surface as compile errors in register table initialization or in shared DMCU/ABM register-list code.

Static validation should compare this chunk against the generated hardware register database and against `dcn_3_0_1_offset.h` for register-name alignment. Cross-generation comparisons with nearby DCN headers can also catch accidental field omissions, but differences must be checked against DCN 3.0.1 hardware rather than normalized away.

Runtime validation requires DCN 3.0.1-class hardware. High-signal checks include DMUB firmware boot and command exchange, ABM mailbox commands completing, DMCU/DMUB interrupts arriving and clearing correctly, HPD/AUX/DDC events working during connector hotplug and EDID reads, and DP link training/stream-disable events being routed to the expected interrupt sources.

Display timing tests should exercise vblank, vstartup, vready, vupdate-no-lock, DRR v-total-reach, GSL/vsync-gap, and underflow interrupt paths across multiple pipes. Useful failure signals include lost interrupts, interrupt storms, stale status bits after clear, incorrect source IDs, stuck mailbox message-in-progress state, unstable variable-refresh behavior, or unexpected display underflow during modeset and page-flip workloads.
