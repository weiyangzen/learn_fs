# sources/distributed-fs/ceph-client/drivers/usb/typec/Makefile

## Purpose

`drivers/usb/typec/Makefile` maps Type-C Kconfig symbols to the core Type-C objects, controller-driver objects, and child directories.

## Important APIs, Types, and Functions

`obj-$(CONFIG_TYPEC)` builds `typec.o`, `altmodes/`, and `mux/`. The `typec-y` composite includes `class.o`, `mux.o`, `bus.o`, `pd.o`, `retimer.o`, and `mode_selection.o`, with `port-mapper.o` added for ACPI. Controller objects include `anx7411.o`, `hd3ss3220.o`, `stusb160x.o`, `rt1719.o`, and `wusb3801.o`; subdirectories include `tcpm/`, `ucsi/`, and `tipd/`.

## Control Flow

Kbuild evaluates each `obj-$()` expression from `.config`. Enabling `TYPEC` builds the core and descends into mux and altmode directories. Enabling controller-specific symbols adds the corresponding module or built-in object.

## State and Persistence Behavior

There is no runtime state. Build selections persist through `.config` and the generated build graph.

## Dependencies and Integration Points

The file integrates with Type-C Kconfig symbols, Kbuild composite-object rules, and child Makefiles under Type-C subdirectories. It must stay synchronized with source file names and driver symbols.

## Risks and Edge Cases

Missing an object here makes a visible Kconfig option build nothing; stale object names break builds. Directory descent under `CONFIG_TYPEC` means alternate-mode and mux builds depend on the core symbol being enabled.

## Test Signals

Run `make olddefconfig`, `allmodconfig`, and representative module/built-in combinations to ensure every selected Type-C symbol produces a valid object or directory traversal.
