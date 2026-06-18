# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_watchdog.h

## Purpose

This header declares the shared ADDI-DATA watchdog helper API used by board drivers with TCW-compatible watchdog blocks.

## Important APIs, types, and functions

It forward-declares `struct comedi_subdevice` and declares `addi_watchdog_reset(unsigned long iobase)` plus `addi_watchdog_init(struct comedi_subdevice *s, unsigned long iobase)`.

## Control Flow

There is no runtime control flow. Including drivers call `addi_watchdog_init()` during subdevice setup and `addi_watchdog_reset()` from reset/detach paths.

## State and Persistence

The header stores no state. State is allocated and managed by `addi_watchdog.c`.

## Dependencies and Integration Points

The include guard `_ADDI_WATCHDOG_H` prevents duplicate declarations. The forward declaration keeps this header lightweight for board drivers that already include COMEDI headers indirectly.

## Risks

API changes here must be synchronized with all ADDI board drivers and the helper implementation. Since the reset API accepts a raw I/O base, callers are responsible for passing the watchdog block base, not the board main base unless the watchdog is at offset zero.

## Test Signals

Signals are clean compilation of all including drivers, correct symbol resolution when `CONFIG_COMEDI_ADDI_WATCHDOG` is enabled, and no duplicate prototype warnings.
