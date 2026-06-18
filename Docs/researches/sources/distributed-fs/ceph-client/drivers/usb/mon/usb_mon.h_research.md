# sources/distributed-fs/ceph-client/drivers/usb/mon/usb_mon.h

## Purpose

`usb_mon.h` is the shared internal header for usbmon. It defines bus and reader structures, common globals, and the contracts between the main, text, binary, and stat implementations.

## Important APIs, Types, and Functions

`struct mon_bus` represents one USB bus or pseudo bus 0, with bus linkage, lock, USB bus pointer, interface init flags, debugfs/device handles, reader list, kref, and counters. `struct mon_reader` is the embedded callback object for each open capture file and carries submit/error/complete function pointers. Prototypes expose reader add/delete, bus lookup, text and binary add/delete, subsystem init/exit, `mon_lock`, `mon_fops_stat`, and `mon_bus0`.

## Control Flow

The header has no runtime control flow. It establishes that frontend readers register callback triplets with `mon_main.c`, and that `mon_main.c` owns bus lifetime and monitoring toggles while frontend files own per-open buffering.

## State and Persistence Behavior

The structures are runtime-only and protected by `mon_lock` plus per-bus spinlocks as described in comments and use sites. The kref lets dissolved bus objects remain valid while readers are open.

## Dependencies and Integration Points

It depends on kernel list, slab, and kref declarations, while using USB types by pointer to keep includes light. It is the integration boundary for all four usbmon object files.

## Risks and Test Signals

Risks are local ABI coupling: field or callback changes must be reflected across `mon_main.c`, `mon_text.c`, `mon_bin.c`, and `mon_stat.c`. Test signals are compile coverage of every usbmon object, successful text and binary reader registration, and correct kref behavior when bus removal races with open files.
