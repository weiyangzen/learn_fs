# sources/distributed-fs/ceph-client/drivers/scsi/fdomain.c

## Purpose

`fdomain.c` is the shared low-level SCSI core for Future Domain TMC-16x0 ISA and TMC-3260 PCI host adapters. It handles chip detection, reset, PIO/FIFO data movement, IRQ scheduling, the SCSI command phase state machine, abort/reset, BIOS geometry, host allocation, scanning, destruction, and resume reset.

## Important APIs, types, and functions

`enum chip_type` distinguishes TMC-1800, TMC-18C50, and TMC-18C30. `struct fdomain` stores I/O base, current command, chip type, and deferred work. Important functions include `fdomain_identify()`, `fdomain_test_loopback()`, `fdomain_reset()`, `fdomain_select()`, `fdomain_read_data()`, `fdomain_write_data()`, `fdomain_queue()`, `fdomain_irq()`, `fdomain_work()`, `fdomain_abort()`, `fdomain_host_reset()`, `fdomain_biosparam()`, `fdomain_create()`, and `fdomain_destroy()`.

## Control flow

Bus wrappers reserve resources and call `fdomain_create()`, which identifies and resets hardware, validates loopback, allocates a SCSI host, requests IRQ, adds the host, and scans. Commands enter through `fdomain_queue()`, which initializes command phase bookkeeping, stores the single active command, idles the bus, and starts arbitration. IRQ disables adapter interrupts and schedules work. `fdomain_work()` advances arbitration, selection, command, data, status, and message phases under `host_lock`, then calls `scsi_done()` on completion.

## State and persistence behavior

The host supports one active command (`can_queue = 1`). Command progress is stored in per-command `struct scsi_pointer`. Adapter state persists in I/O registers for bus control, interrupt control, adapter control, FIFO, and config. Runtime state is freed on remove; resume resets hardware.

## Dependencies and integration points

The file depends on SCSI midlayer APIs, low-level port I/O, interrupts, workqueues, delays, PCI/ISA wrappers, and `fdomain.h`. `fdomain_create()`/`fdomain_destroy()` are exported to bus-specific modules.

## Risks and edge cases

Missed interrupts or incorrect phase transitions can hang commands. The queue path relies on SCSI midlayer serialization rather than explicitly rejecting a second `cur_cmd`. Abort handling is blunt and noted as weak. FIFO residual accounting must avoid underflow. TMC-1800 versus later-chip data phase handling is delicate.

## Test signals

Build ISA and PCI variants. Exercise scan, read/write with varied transfer sizes and SG layouts, selection timeout, abort, host reset, unload, resume, IRQ sharing, and BIOS geometry paths.
