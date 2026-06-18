# sources/distributed-fs/ceph-client/drivers/char/agp/Makefile

## Purpose
This Makefile builds the generic AGPGART backend and chipset-specific AGP bridge modules.

## Important APIs, Types, and Functions
`agpgart-y` combines `backend.o`, `generic.o`, and `isoch.o`. Other `obj-$(CONFIG_*)` lines map chipset config symbols to modules such as `ali-agp.o`, `ati-agp.o`, `amd-k7-agp.o`, `amd64-agp.o`, `alpha-agp.o`, and `efficeon-agp.o`.

## Control Flow
When `CONFIG_AGP` is enabled, the generic `agpgart` object is built. Chipset options compile their corresponding PCI/architecture bridge drivers.

## State and Persistence Behavior
No runtime state. It defines which AGP object code enters the kernel/module build.

## Dependencies and Integration Points
The Makefile aligns with AGP Kconfig symbols and driver filenames. Chipset drivers depend on backend symbols exported by `backend.o` and generic helpers from `generic.o`.

## Risks
The generic backend must be available before chipset modules can resolve symbols. Any Kconfig/Makefile mismatch leaves selected drivers unbuilt or built without dependencies.

## Test Signals
Build each listed AGP chipset option as module and built-in, confirming `agpgart` and chipset modules link.
