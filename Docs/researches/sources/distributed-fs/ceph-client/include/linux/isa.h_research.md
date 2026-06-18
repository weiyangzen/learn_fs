# sources/distributed-fs/ceph-client/include/linux/isa.h

## Purpose
`isa.h` defines the small ISA bus driver registration API and module helper macros for legacy devices enumerated by fixed slot/base-index counts.

## Important APIs, types, and functions
It defines `struct isa_driver` with match/probe/remove/shutdown/suspend/resume callbacks, embedded `device_driver`, and devices pointer; `to_isa_driver`; `isa_register_driver`; `isa_unregister_driver`; module init/exit helper macros including IRQ-count validation; and `max_num_isa_dev`.

## Control flow
ISA drivers declare an `isa_driver` and number of devices. Registration creates per-index devices and runs match/probe callbacks. Module macros install init/exit functions, with the IRQ variant validating base and IRQ array counts.

## State and persistence
State is runtime device model state for registered ISA pseudo-devices and driver-owned fixed resources. No persistent state exists.

## Dependencies and integration points
It depends on the device model, errno, kernel logging, module init/exit, and optional `CONFIG_ISA_BUS_API`.

## Risks and test signals
Risks include disabled-config `-ENODEV`, fixed resource collisions, wrong device count, suspend callback misuse, and IRQ count mismatch. Tests should cover registration/probe/remove, module helper validation, disabled config, and multiple legacy ISA device instances.
