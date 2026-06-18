# sources/distributed-fs/ceph-client/drivers/ps3/vuart.h Research

## Purpose
`vuart.h` declares the PS3 virtual UART port-driver interface used by PS3 logical devices such as AV settings. It is a local contract between PS3 VUART bus support and port-specific drivers.

## Important APIs, Types, And Functions
`struct ps3_vuart_stats` records byte and interrupt counters. `struct ps3_vuart_work` wraps `work_struct`, a trigger bitmask, and the owning `ps3_system_bus_device`. `struct ps3_vuart_port_driver` embeds `struct ps3_system_bus_driver` and supplies `probe`, `remove`, `shutdown`, and `work` callbacks. Inline helpers convert a system-bus device to its VUART driver and a work item to its device. Function declarations cover driver registration, synchronous read/write, async read setup/cancel, RX byte clearing, trigger get/set, and enabling/disabling TX, RX, and disconnect interrupts.

## Control Flow
Port drivers register a `ps3_vuart_port_driver`. The VUART core matches devices, calls driver callbacks, schedules work using `ps3_vuart_work`, and exposes byte-oriented transport through `ps3_vuart_write()` and `ps3_vuart_read()`. Interrupt trigger helpers allow port drivers to tune or enable event notification.

## State And Persistence
This header does not own storage. It defines the shapes of per-port state managed by the VUART core and by drivers. Work items retain only a device pointer and trigger state until executed.

## Dependencies And Integration Points
It depends on PS3 system-bus definitions from `asm/ps3.h` and the Linux workqueue type. `ps3av.c` consumes this interface directly. Other PS3 VUART clients can share the same registration and I/O operations.

## Risks
The inline conversion helpers assume valid embedding and use `BUG_ON()` for missing bus drivers. Async read and interrupt semantics are only declared here, so users must coordinate lifetimes with the VUART implementation. Work items hold raw device pointers and require the core to prevent use-after-free during remove/shutdown.

## Test Signals
Useful tests include registering a mock port driver, matching by `match_id`, verifying work-to-device conversion, exercising sync and async reads, confirming trigger programming, and validating interrupt enable/disable paths during remove and disconnect.
