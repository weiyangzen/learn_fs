# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 2408-4719

## Scope And Purpose

This chunk is generated AMD DCN 3.0.3 register field metadata. It contains no executable C logic; its API surface is preprocessor constants that describe field shifts and masks for 32-bit MMIO registers. The matching `dcn_3_0_3_offset.h` header provides register offsets, while this file provides the bit layout consumed by AMDGPU Display Core and DMUB register helper macros.

The requested range begins inside the `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL_CONT2` register, covers DMCU-to-microcontroller interrupt status/enable fields for DPCS transmit interrupts, spans the `dce_dc_dmu_ihc_dispdec` block for GPU timer snapshots, display interrupt status continuation registers, and interrupt destination routing registers, then enters the `dce_dc_dmu_dmcub_dispdec` block for the beginning of DMCUB memory-window and interrupt-control definitions. It ends at the `//DMCUB_INTERRUPT_STATUS` marker; the actual DMCUB status field definitions are owned by the next chunk.

Although the repository path is under a `ceph-client` source mirror, this header is AMD GPU display hardware metadata, not Ceph filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, globals, locks, allocations, callbacks, or includes in this chunk. The relevant interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: low bit position for a field.
- `<REGISTER>__<FIELD>_MASK`: raw bitmask for that field before shifting.
- `// addressBlock: ...`: generated hardware block grouping.
- `//<REGISTER>`: generated register grouping marker.

This slice contains 2,187 `#define` entries, mostly paired shift/mask definitions. The pair count is not perfectly symmetric because the range starts in the middle of one register and ends just before the following register's fields. There are two address blocks in scope:

- `dce_dc_dmu_ihc_dispdec`: display interrupt handler/controller metadata, GPU timer read/start-position fields, interrupt status continuation, and interrupt destination routing.
- `dce_dc_dmu_dmcub_dispdec`: the start of the DMCUB display microcontroller register metadata, especially address windows and interrupt enable/ack fields.

Major register families:

- `DMCU_INTERRUPT_STATUS_2` and `DMCU_INTERRUPT_TO_UC_EN_MASK_2`: latched/clearable DPCS TXA-TXG interrupt status bits and enable masks for routing those events to the DMCU microcontroller path.
- `DC_GPU_TIMER_START_POSITION_*`, `DC_GPU_TIMER_READ`, and `DC_GPU_TIMER_READ_CNTL`: per-display timing selector fields for V_UPDATE, VSTARTUP, VREADY, FLIP, V_UPDATE_NO_LOCK, FLIP_AWAY, VSYNC_NOM, and full-width timer readback.
- `DISP_INTERRUPT_STATUS` through `DISP_INTERRUPT_STATUS_CONTINUE25`: a dense interrupt-status cascade covering OTG/OPTC, DIG, AUX, HPD/HPDRX, I2C/DDC, ABM, DMCU, DCPG power events, DCHUB/HUBP, DPP, MPC/OPP, DSC, MCIF writeback, DMCUB mailbox/timer/fault events, MMHUBBUB warmup, and continuation bits that link one status register to the next.
- `DCCG_INTERRUPT_DEST`, `DMU_INTERRUPT_DEST*`, `DCPG_INTERRUPT_DEST*`, `MMHUBBUB_INTERRUPT_DEST`, `WB_INTERRUPT_DEST`, `DCHUB_INTERRUPT_DEST*`, `DCHUB_PERFCOUNTER_INTERRUPT_DEST`, `DPP_PERFCOUNTER_INTERRUPT_DEST`, `MPC_INTERRUPT_DEST`, `OPP_INTERRUPT_DEST`, `OPTC_INTERRUPT_DEST`, `OTG0_INTERRUPT_DEST` through `OTG5_INTERRUPT_DEST`, `DIG_INTERRUPT_DEST`, `I2C_DDC_HPD_INTERRUPT_DEST`, `DIO_INTERRUPT_DEST`, `DCIO_INTERRUPT_DEST`, `HPD_INTERRUPT_DEST`, `AZ_INTERRUPT_DEST`, `AUX_INTERRUPT_DEST`, and `DSC_INTERRUPT_DEST`: interrupt destination selector fields for the same display subblocks and events.
- `DMCUB_REGION0/1/2/4/5/6/7_OFFSET`, matching `_OFFSET_HIGH`, and matching `_TOP_ADDRESS`: 40-bit-style low/high offset pieces plus top-address and enable fields for DMCUB memory regions. Low offsets start at bit 8 with `0xFFFFFF00L`; high offsets use `0x0000FFFFL`; top addresses use `0x1FFFFFFFL` with enable at bit 31.
- `DMCUB_REGION3_CW0` through `DMCUB_REGION3_CW7`: per-code-window base, top, enable, offset, and offset-high definitions for the DMCUB region-3 code-window aperture.
- `DMCUB_INTERRUPT_ENABLE` and `DMCUB_INTERRUPT_ACK`: timer, inbox, outbox, GPINT0-2, and undefined-address-fault interrupt enable/acknowledge bits. These are the only DMCUB interrupt-control fields fully defined in this chunk.

## Control Flow

This header has no local control flow. Runtime flow is supplied by code that includes it:

1. DCN303 resource and IRQ code include `dcn_3_0_3_offset.h` and this matching mask header.
2. Register-table macros expand offsets from the offset header and masks/shifts from this header into per-ASIC tables.
3. AMDGPU Display Core and DMUB service code use helper macros such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and IRQ table initializers to program or decode hardware registers.
4. Hardware interprets the encoded bits as timer selection, interrupt status, interrupt routing, DMCUB memory-window configuration, or DMCUB interrupt enable/ack state.

Direct consumers in this tree include `display/dc/resource/dcn303/dcn303_resource.c`, `display/dc/irq/dcn303/irq_service_dcn303.c`, and `display/dmub/src/dmub_dcn303.c`. The DMUB file constructs `dmub_srv_dcn303_regs` from `DMUB_COMMON_REGS()`, `DMCUB_INTERNAL_REGS()`, and `DMUB_COMMON_FIELDS()`, using `REG_OFFSET`, `FD_MASK`, and `FD_SHIFT` against this generated header. Shared DMUB definitions in nearby headers, such as the DCN31 register list, show the concrete DMCUB fields used by the service layer, including region code-window top/enable fields and `DMCUB_INTERRUPT_ENABLE`/`DMCUB_INTERRUPT_ACK`.

## State And Persistence Behavior

The header stores no software state and persists nothing by itself. It describes hardware state:

- Interrupt status fields are volatile or latched hardware events. Some fields use paired occurred/clear naming, and acknowledgement or clear writes may have side effects.
- Interrupt destination fields persist routing policy inside the display interrupt controller until reprogrammed, reset, or affected by power management.
- GPU timer selector/read fields expose display timing snapshots and timer readback state; timing values change as scanout and vertical events progress.
- DMCUB region fields persist firmware-visible memory window configuration: offsets, top addresses, enables, and code-window base/top mappings.
- DMCUB interrupt enable fields persist which DMCUB events can raise interrupts; ACK fields are write-side clear/ack controls for timer, inbox/outbox, GPINT, and undefined-address-fault events.

Power transitions, DMCUB reset, display core reset, ASIC reset, suspend/resume, and firmware boot sequencing can all change or require reprogramming of the described hardware state. The macros do not encode ordering constraints; callers must know when a register is safe to read, update, or acknowledge.

## Dependencies And Integration Points

This chunk must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_offset.h`, which supplies the matching register offsets for these field names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn303/dcn303_resource.c`, which includes the header for DCN303 resource construction and register-table initialization.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn303/irq_service_dcn303.c`, which includes the header for DCN303 IRQ source mapping and register-backed IRQ entries.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn303.c`, which includes this header to build the DCN303 DMUB register, shift, and mask tables.
- Shared DMUB service code and headers that use common DMCUB register names for firmware boot, memory-window setup, inbox/outbox traffic, GPINT signaling, fault handling, and debug snapshots.
- Display subsystems represented by interrupt destination/status fields: OTG/OPTC, HUBP/DCHUB, DPP, MPC, OPP, DCCG, DCPG, DIO/DCIO, AUX/DDC/I2C, HPD/HPDRX, DSC, MCIF writeback, Azalia audio, ABM, DMCU, and DMCUB.

The integration contract is exact name/value parity. Register helpers generally combine a `REG_*` offset with a field name that resolves through these masks and shifts. Pairing a field from the wrong ASIC version, wrong register instance, or wrong companion offset header can compile in some macro contexts but update the wrong hardware bit.

## Risks And Edge Cases

- Generated mask/shift drift is the core risk. A one-bit error can silently corrupt interrupt routing, clear the wrong latched event, or misconfigure a DMCUB firmware memory aperture.
- This chunk starts and ends on chunk boundaries that split register groups. `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL_CONT2` is missing its first TXA/TXB shift definitions in this document, and `DMCUB_INTERRUPT_STATUS` is only a marker here. The final per-file research must merge adjacent chunks before making complete claims for those registers.
- Interrupt status continuation registers are dense and repetitive. A bad continuation bit can hide later status registers; a bad per-event bit can misreport only one display pipe, endpoint, or subblock.
- ACK/clear fields are side-effectful. Treating `DMCUB_INTERRUPT_ACK` or DMCU clear masks like persistent configuration can drop evidence of pending events or suppress servicing.
- Destination fields affect system-level interrupt routing. Incorrect routing for HPD, AUX/DDC, vblank/vline, flip, DSC, DMCUB, DCPG, or writeback events can cause missed hotplug, display update stalls, interrupt storms, or events delivered to an unexpected handler.
- DMCUB region windows are security- and stability-sensitive. Wrong base/top/offset masks can point firmware execution or data windows at the wrong memory, trigger undefined-address/fetch/write faults, or break mailbox setup during boot.
- The DCN303 DMCUB interrupt set in this chunk exposes only GPINT0-2 and no `DMCUB_GPINT_IH_INT_EN` field seen on newer ASIC headers. Shared code must use the correct per-ASIC common field list.
- These are untyped C macros. The compiler will not prevent mixing a mask from one register with a shift from another when generic helper code is misused.

## Test Signals

Useful validation is mostly compile-time, generated-header consistency, and hardware smoke behavior:

- Build AMDGPU with DCN303 display support enabled; `dcn303_resource.c`, `irq_service_dcn303.c`, and `dmub_dcn303.c` should compile against the generated names.
- Mechanically verify every field in this range has the expected mask/shift pair, and that each mask aligns with its shift and width. Treat the first and last partial register groups as cross-chunk checks.
- Cross-check all registers in this range against `dcn_3_0_3_offset.h` so offset names and field names come from the same generated ASIC database.
- Compare repeated instance families: `OTG0`-`OTG5` destination layouts, DMCUB region 0/1/2/4/5/6/7 fields, and DMCUB region-3 `CW0`-`CW7` fields should be structurally consistent where the hardware instances are expected to match.
- Exercise IRQ paths for vblank/vstartup, vline, flip, HPD/HPDRX, AUX/DDC/I2C completion, DSC errors/underflow, writeback, DCPG power transitions, DMCU/DMCUB mailbox events, and DMCUB faults while checking for missed events or interrupt storms.
- Validate DMUB firmware boot and reset on DCN303 hardware: region windows should be programmed with correct offsets/top/enables, and DMCUB interrupt enable/ack should allow expected mailbox or trace events to be serviced.
- Run suspend/resume, display hotplug, modeset, fast update, PSR/ABM-related, and DMCUB reset paths to catch stale interrupt destination state or DMCUB window state after power transitions.
- For timer fields, inspect vblank counters, scanout position, and timing-related debug paths around modesets and vertical events to confirm GPU timer selectors and readback masks decode plausible values.

## Cross-Chunk Notes

The previous chunk owns the beginning of the DMCU interrupt-selector area, including earlier `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL_CONT2` shift definitions. This chunk completes that selector's visible masks, covers the main display interrupt-status and destination-routing surface, and begins DMCUB region and interrupt-control metadata. The next chunk begins with the `DMCUB_INTERRUPT_STATUS` fields and continues DMCUB control/mailbox/fault definitions, so final per-file research should merge this document with adjacent chunks before summarizing the complete DCN 3.0.3 mask header.
