# sources/distributed-fs/ceph-client/drivers/xen/xenbus/Makefile

## Purpose
This Makefile defines how the Xenbus support objects are built into the kernel. It groups common Xenbus client, communication, Xenstore, and probe code into the `xenbus` composite object, then conditionally adds backend, frontend, and misc-device support based on Xen configuration symbols.

## Important APIs, Types, And Functions
There are no C APIs in this file, but its object selections determine which APIs exist. `xenbus-y` always includes `xenbus_client.o`, `xenbus_comms.o`, `xenbus_xs.o`, and `xenbus_probe.o`. `xenbus-$(CONFIG_XEN_BACKEND)` adds `xenbus_probe_backend.o`. Separate built-in objects are `xenbus_dev_frontend.o`, optional `xenbus_dev_backend.o`, and optional `xenbus_probe_frontend.o`.

## Control Flow
Build control is straightforward: `obj-y += xenbus.o` includes the common composite whenever this directory is part of the Xen build, while frontend/backend probing and backend device nodes are compiled only when their Kconfig symbols are enabled. This affects initcall availability at runtime.

## State And Persistence
The Makefile persists no runtime state, but it is the source of build-time state for feature inclusion. Enabling or disabling `CONFIG_XEN_BACKEND` changes whether backend bus probing and `/dev/xen/xenbus_backend` exist.

## Dependencies And Integration Points
It integrates with Kbuild and the Xen driver directory. Runtime dependencies among the C files assume the common `xenbus.o` exports helper functions needed by frontend and backend modules.

## Risks
The main risk is configuration skew: compiling a backend driver without backend Xenbus probe support would prevent devices from binding. The unconditional frontend misc device may exist on Xen domains even when frontend bus probing is configured separately.

## Test Signals
Build matrix checks for `CONFIG_XEN_BACKEND` and `CONFIG_XEN_XENBUS_FRONTEND`, link symbol availability, and boot logs showing the expected frontend/backend bus registration validate this file.
