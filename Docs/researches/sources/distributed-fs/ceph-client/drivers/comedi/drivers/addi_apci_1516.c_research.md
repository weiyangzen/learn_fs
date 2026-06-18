# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_1516.c

## Purpose

This driver supports the ADDI-DATA APCI-1016, APCI-1516, and APCI-2016 PCI digital I/O boards. Depending on board ID, it exposes digital input, digital output, and an ADDI watchdog subdevice.

## Important APIs, types, and functions

The board table `apci1516_boardtypes[]` describes per-board DI channel count, DO channel count, and watchdog presence. `struct apci1516_private` stores the watchdog BAR base. Main functions are `apci1516_di_insn_bits()`, `apci1516_do_insn_bits()`, `apci1516_reset()`, `apci1516_auto_attach()`, and `apci1516_detach()`. Watchdog setup delegates to `addi_watchdog_init()` and reset to `addi_watchdog_reset()`.

## Control Flow

PCI probe passes the board table index as context. Auto-attach validates the index, sets the board name, allocates private data, enables PCI resources, records BAR 1 as the DIO base and BAR 2 as the watchdog base, allocates three subdevices, and marks unsupported per-board subdevices as unused. DO writes read the current hardware state, update masked bits with `comedi_dio_update_state()`, and write the result back. Attach finishes by resetting outputs/watchdog as applicable. Detach resets the board before generic PCI cleanup.

## State and Persistence

State is limited to `dev->iobase`, watchdog base, subdevice `state`, and hardware output/watchdog registers. No persistent configuration is stored.

## Dependencies and Integration Points

The file depends on COMEDI PCI helpers and the shared ADDI watchdog helper. It integrates with three PCI IDs through the PCI ID table and with COMEDI DIO instruction handling.

## Risks

`apci1516_reset()` returns early for boards without watchdog, so APCI-1016 output reset is irrelevant because it has no DO channels, but future board-table changes could make that control flow surprising. The driver assumes BAR 1 and BAR 2 layouts are consistent across the three IDs. DO state is initialized lazily from hardware during writes rather than during attach.

## Test Signals

Validation includes each PCI ID selecting the right subdevice mix, DI reads for APCI-1016/APCI-1516, DO writes for APCI-1516/APCI-2016, watchdog arm/disarm/ping on watchdog boards, outputs reset to zero on attach/detach, and unused subdevices for absent functions.
