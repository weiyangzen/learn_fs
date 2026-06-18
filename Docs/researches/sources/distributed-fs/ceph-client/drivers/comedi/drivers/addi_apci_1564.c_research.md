# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_1564.c

## Purpose

This driver supports the ADDI-DATA APCI-1564 digital I/O board. It handles 32 DI, 32 DO, change-of-state interrupts for channels 4-19, a 12-bit timer, optional revision-2 counters, an 8-bit watchdog, and two diagnostic inputs.

## Important APIs, types, and functions

`struct apci1564_private` stores EEPROM, timer, optional counter bases, and cached COS masks/control. Important functions are `apci1564_reset()`, `apci1564_interrupt()`, `apci1564_di_insn_bits()`, `apci1564_do_insn_bits()`, `apci1564_diag_insn_bits()`, `apci1564_cos_insn_config()`, `apci1564_cos_cmdtest()`, `apci1564_cos_cmd()`, `apci1564_cos_cancel()`, `apci1564_timer_insn_config()`, `apci1564_counter_insn_config()`, timer/counter read/write handlers, and `apci1564_auto_attach()`.

## Control Flow

Auto-attach enables PCI, reads the EEPROM revision nibble, chooses revision-1 or revision-2 register mapping, resets all hardware blocks, optionally requests a shared IRQ, and allocates seven subdevices: DI, DO, COS event DI, timer, counter, watchdog, and diagnostics. COS configuration caches mode masks from `INSN_CONFIG_DIGITAL_TRIG`, masks them to channels 4-19, and `do_cmd` writes the masks/control to hardware. The ISR collects COS, timer, and counter interrupt sources into a single 32-bit event sample in `dev->read_subdev`, clears each source by toggling its control register, and calls `comedi_handle_events()` when any event bit was set.

## State and Persistence

Runtime state includes the revision-dependent register bases, cached COS `mode1`, `mode2`, `ctrl`, subdevice states, watchdog private state, and timer/counter control registers. The event sample encodes event flags plus COS input state. Attach/detach reset outputs, interrupt masks, watchdog, timer, and counters. There is no nonvolatile state modification.

## Dependencies and Integration Points

The driver depends on COMEDI PCI, Linux IRQs, `addi_tcw.h` for timer/counter/watchdog register offsets, and `addi_watchdog.h` for the watchdog subdevice. It integrates COMEDI async command flow for COS but controls timer and counters through synchronous `insn_config`.

## Risks

The revision-dependent BAR map is a major risk; wrong EEPROM revision interpretation moves every register base. The timer and counter portions carry FIXME notes that the datasheet does not fully define `ADDI_TCW_TIMEBASE_REG` or counter operation, so raw values may not behave as user-visible COMEDI conventions imply. The shared `read_subdev` event stream mixes COS, timer, and counters, so consumers must parse flags correctly. COS command validation allows no command unless masks/control are configured.

## Test Signals

Useful tests include revision-1 and revision-2 probe, DI/DO reads/writes, COS edge and level interrupts only for channels 4-19, timer arm/disarm/status/read/write, revision-2 counter arm/disarm/status/read/write, watchdog operation, diagnostic input reads, and detach resetting all interrupt and output state.
