# sources/distributed-fs/ceph-client/drivers/usb/mon/mon_main.c

## Purpose

`mon_main.c` is the usbmon core. It registers hooks with the USB core, tracks all USB buses plus pseudo bus 0, fans URB submit/error/complete events out to active text and binary readers, and coordinates bus add/remove with usbmon interface creation.

## Important APIs, Types, and Functions

Global state includes `mon_lock`, `mon_bus0`, and the `mon_buses` list. Exported helpers are `mon_reader_add()`, `mon_reader_del()`, and `mon_bus_lookup()`. Internal callbacks `mon_submit()`, `mon_submit_error()`, and `mon_complete()` are registered through `struct usb_mon_operations`. Lifecycle functions `mon_init()` and `mon_exit()` initialize text and binary subsystems, register USB bus notifications, create per-bus `struct mon_bus` records, and tear them down.

## Control Flow

Module init initializes text and binary interfaces, creates bus 0, registers usbmon operations, walks existing USB buses under `usb_bus_idr_lock`, and installs a notifier for later bus add/remove. Reader open paths call `mon_reader_add()` under `mon_lock`; the first reader sets `usb_bus->monitored` for the chosen bus or all buses for bus 0. USB core events call into the registered operations, which dispatch to the specific bus and always to bus 0. Bus removal removes debugfs and char-device endpoints, dissolves the USB bus association, and drops the `mon_bus` reference.

## State and Persistence Behavior

State is in-memory only: bus list, reader lists, reader counts, refs, event counters, and lost text counters. `mon_bus` objects are kref-managed and may outlive USB bus removal while readers exist; `mon_dissolve()` nulls `ubus->mon_bus` and `mbus->u_bus` to prevent stale hardware access.

## Dependencies and Integration Points

The file depends on USB core monitor registration, USB bus notifiers and IDR, text/binary/stat usbmon submodules, and the shared `usb_mon.h` types. It is the coordination point that lets multiple frontend formats observe the same URB stream.

## Risks and Test Signals

Risks include locking between `mon_lock` and per-bus spinlocks, handling bus removal with open readers, ensuring bus 0 monitoring toggles all current buses, and not dereferencing dissolved `u_bus`. Test signals include module load after USB buses already exist, hot-add and hot-remove host controllers, simultaneous bus-specific and bus-0 readers, event counters increasing on submit/complete/error paths, and unload refusal or leak diagnostics with outstanding opens.
