# sources/distributed-fs/ceph-client/drivers/parport/parport_atari.c

## Purpose
`parport_atari.c` adapts the Atari built-in parallel port to parport. The hardware has output data, strobe control, and BUSY interrupt/status only, so the driver provides a minimal PC-style parport surface.

## Important APIs, Types, and Functions
`parport_atari_ops` implements data access through YM sound-chip registers, strobe control, BUSY status, IRQ enable/disable, forward direction setup, and generic IEEE 1284 fallback functions. `parport_atari_init()` checks `MACH_IS_ATARI`, configures sound-chip and MFP registers, registers the port, requests `IRQ_MFP_BUSY`, and announces it. `parport_atari_exit()` removes and releases it.

## Control Flow
Data reads/writes select YM register 15 under `local_irq_save()`. Control accesses select YM register 14 and manipulate bit 5 for STROBE. Init configures sound-chip ports as outputs, sets strobe high, configures MFP port I0 as input and high-to-low edge interrupt, registers the parport, requests IRQ, and announces. Reverse direction and state callbacks are empty because the hardware does not support meaningful reverse data state here.

## State and Persistence
Global `this_port` holds the registered port. Hardware state lives in YM and MFP registers. No persistent state exists; state callbacks are no-ops.

## Dependencies and Integration Points
The driver depends on Atari platform globals (`sound_ym`, `st_mfp`), Atari IRQ definitions, parport core, and generic IEEE 1284 operations. It integrates with parport IRQ handling via `parport_irq_handler`.

## Risks
The operation table advertises generic reverse/advanced functions even though `data_reverse()` is empty and status lines are sparse, so advanced IEEE 1284 modes may not work beyond simple compatibility use. Register access needs interrupt masking because YM register select/data writes are shared hardware state.

## Test Signals
On Atari hardware, init should announce one port with `IRQ_MFP_BUSY`. Functional checks should verify YM data writes, strobe toggling, BUSY status polarity, interrupt delivery on MFP I0, and clean unload.
