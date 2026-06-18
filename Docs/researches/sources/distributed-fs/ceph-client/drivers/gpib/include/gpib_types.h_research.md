# sources/distributed-fs/ceph-client/drivers/gpib/include/gpib_types.h

## Purpose

`gpib_types.h` defines the core kernel data model for linux-gpib: board configuration, driver interface callbacks, board runtime state, event queues, pseudo IRQ support, status queues, descriptors, and per-file private data.

## Important APIs and Types

- `struct gpib_board_config` carries attach-time inputs: firmware blob, I/O base, MMIO base, IRQ, DMA channel, PCI bus/slot filters, sysfs path, and serial number.
- `struct gpib_interface` is the core driver contract. It contains attach/detach and callbacks for read, write, command, control ownership, IFC/REN, EOS, parallel poll, serial poll, status, addressing, T1 delay, local mode, and capability flags.
- `struct gpib_board` stores one physical board's runtime state, callbacks, buffers, locks, timers, device pointers, private driver data, address configuration, timeout, online count, autopoll state, event queue, pseudo IRQ state, copied config, and status flags.
- `struct gpib_event_queue` and `struct gpib_event` hold asynchronous bus events such as clear/trigger/IFC.
- `struct gpib_pseudo_irq` models timer-based polling.
- `struct gpib_status_queue` and `struct gpib_status_byte` track serial-poll bytes per addressed device.
- `struct gpib_descriptor` tracks per-open descriptor address, I/O busy count, kernel busy reference, and flags.
- `struct gpib_file_private` stores descriptor array and module/mutex state per open file.

## Control Flow and Integration

This header is the contract between gpib-common and board drivers. Board modules fill `struct gpib_interface`; gpib-common serializes user access with `user_mutex` and `big_gpib_mutex`, drives timers for timeout, sleeps drivers on `board->wait`, and exposes status/device operations through descriptors.

## State and Persistence Behavior

All state is in-memory for the lifetime of open files, online boards, and loaded modules. `board->config` stores a copy of attach parameters, while hardware drivers own `board->private_data`. Event/status queues persist until consumed or board teardown. Atomic fields and locks coordinate interrupt, timeout, file, and ioctl paths.

## Dependencies

When `__KERNEL__` is defined, it includes Linux GPIB, atomic, device, mutex, wait, scheduler, timer, and interrupt headers. The file is kernel-specific except for the include guard shell.

## Risks and Test Signals

The callback table has many nullable optional methods, so core callers must respect capability flags and NULL checks. Locking order is explicit: `user_mutex` must be first if held across multiple ioctls. Test signals include descriptor lifetime under concurrent I/O/close, timeout wakeups setting TIMO, interrupt wakeups on `board->wait`, event queue overflow/drop behavior, status queue overflow, pseudo IRQ start/stop, and correct module reference ownership.
