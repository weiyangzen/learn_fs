# sources/distributed-fs/ceph-client/include/linux/serio.h

## Purpose

`serio.h` defines the Linux serio bus contract for low-level serial input ports such as PS/2 keyboard and mouse controllers. It models serio ports, serio drivers, registration helpers, interrupt delivery, driver data access, and RX pause locking.

## Important APIs, Types, And Functions

The core type `struct serio` contains per-port data, names, physical path, firmware ID, manual bind flag, device ID, interrupt-protection spinlock, transport callbacks (`write`, `open`, `close`, `start`, `stop`), hierarchy pointers and child lists, driver pointer protected by `drv_mutex` and `lock`, embedded `struct device`, global list node, and optional shared `ps2_cmd_mutex`.

`struct serio_driver` supplies ID matching, manual binding, `write_wakeup`, interrupt, connect/reconnect/fast_reconnect, disconnect, cleanup, and embedded `device_driver`. APIs include `serio_open()`, `serio_close()`, `serio_rescan()`, `serio_reconnect()`, `serio_interrupt()`, `serio_register_port()`, `serio_unregister_port()`, `serio_unregister_child_port()`, `serio_register_driver()`, `serio_unregister_driver()`, `module_serio_driver()`, `serio_write()`, `serio_drv_write_wakeup()`, `serio_get_drvdata()`, `serio_set_drvdata()`, `serio_pause_rx()`, and `serio_continue_rx()`.

## Control Flow

Port providers register a `struct serio`; drivers register a `struct serio_driver` with an ID table. Bus matching calls driver connect paths, opening the port through `serio_open()`. Hardware interrupt handlers report bytes through `serio_interrupt()`, which dispatches to the bound driver's `interrupt()` callback. Reconnect and rescan paths recover devices after transport disruption. The inline `serio_write()` delegates outbound bytes to the port transport when available.

## State And Persistence

`struct serio` persists for the lifetime of the port and stores hierarchy depth, parent-child links, current driver, and embedded device state. Driver-private state is attached to `serio->dev` through standard device driver data helpers. RX critical sections are protected by `serio->lock`; driver binding is protected by `drv_mutex` plus the spinlock because interrupt handlers read `serio->drv`.

## Dependencies And Integration Points

Dependencies include cleanup guards, interrupt return types, list/spinlock/mutex primitives, the device model, module device tables, and UAPI serio IDs. Integration points are the input subsystem, PS/2 layer, i8042-like shared hardware, module registration, sysfs device binding, and firmware-described input ports.

## Risks And Test Signals

Risks are racing driver unbind with interrupt delivery, failing to pause RX around driver critical sections, hierarchy leaks when unregistering child ports, and shared PS/2 command deadlocks without `ps2_cmd_mutex`. Test signals include hotplug/register/unregister loops, PS/2 interrupt storms, manual bind/unbind, reconnect after suspend, write wakeups, and lockdep coverage around `serio_pause_rx()` sections.
