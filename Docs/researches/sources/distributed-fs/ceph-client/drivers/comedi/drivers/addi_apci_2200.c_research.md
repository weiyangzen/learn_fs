# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_2200.c

## Purpose

This driver supports the ADDI-DATA APCI-2200 relay board with 8 digital inputs, 16 digital outputs, and an ADDI watchdog/timer block exposed as a watchdog subdevice.

## Important APIs, types, and functions

The file defines simple register offsets for DI, DO, and watchdog. Main functions are `apci2200_di_insn_bits()`, `apci2200_do_insn_bits()`, `apci2200_reset()`, `apci2200_auto_attach()`, and `apci2200_detach()`. Watchdog handling is delegated to `addi_watchdog_init()` and `addi_watchdog_reset()`.

## Control Flow

PCI probe invokes COMEDI PCI auto-config. Auto-attach enables PCI resources, sets BAR 1 as `dev->iobase`, allocates three subdevices, initializes the DI and DO subdevices, initializes the watchdog subdevice at the watchdog offset, and resets outputs/watchdog. DO writes read the current output state, update requested bits through `comedi_dio_update_state()`, and write the new 16-bit state. Detach resets hardware before generic PCI cleanup.

## State and Persistence

Runtime state is output state in hardware and `s->state`, watchdog private state, and `dev->iobase`. There is no persistent storage. Outputs and watchdog reload/control are cleared on attach and detach.

## Dependencies and Integration Points

The driver depends on COMEDI PCI helpers, COMEDI DIO helpers, and the shared ADDI watchdog helper. It binds one ADDI-DATA PCI device ID.

## Risks

The implementation assumes BAR 1 layout exactly matches the register map. DO state is initialized from hardware on each write, which is robust to external state changes but can surprise tests that expect attach-time `s->state` initialization. The watchdog helper uses an 8-bit reload value and a fixed 20 ms time base.

## Test Signals

Signals include successful probe, 8-bit DI reads, 16-bit DO masked writes, outputs reset to zero, watchdog arm/read/ping/disarm, and detach resetting output and watchdog registers.
