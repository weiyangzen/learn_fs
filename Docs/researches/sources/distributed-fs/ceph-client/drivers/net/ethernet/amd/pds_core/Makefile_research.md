# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/pds_core/Makefile

## Purpose
This Makefile defines the build composition for the AMD/Pensando core driver. It builds the `pds_core.o` module/object when `CONFIG_PDS_CORE` is enabled and aggregates all implementation units that make up the core PCI, devlink, admin queue, auxiliary bus, debugfs, firmware, and hardware setup functionality.

## Important APIs, Types, And Functions
There are no C APIs in this file. The important build variable is `obj-$(CONFIG_PDS_CORE) := pds_core.o`, which binds Kconfig selection to the object. `pds_core-y` lists `main.o`, `devlink.o`, `auxbus.o`, `dev.o`, `adminq.o`, `core.o`, `debugfs.o`, and `fw.o` as the compiled units linked into `pds_core.o`.

## Control Flow
Kbuild evaluates the conditional object assignment. If `CONFIG_PDS_CORE=y` it links the objects into the built-in kernel image; if `CONFIG_PDS_CORE=m` it links them into a loadable module; if unset it builds none of them. Object ordering places `main.o` first, but runtime entry still comes from `module_init` in `main.c`.

## State And Persistence
The file has no runtime state. Its persistent effect is the static build contract: adding or removing a source file from the driver requires updating `pds_core-y`, and changing the Kconfig symbol changes whether any of these files are compiled.

## Dependencies And Integration Points
It integrates with kernel Kbuild and the `CONFIG_PDS_CORE` Kconfig symbol. The listed object files depend on common Pensando/AMD UAPI and internal headers under `include/linux/pds/` plus core kernel subsystems such as PCI, devlink, auxiliary bus, debugfs, workqueues, timers, and firmware.

## Risks
If a new implementation file is introduced but omitted from `pds_core-y`, unresolved symbols or missing functionality will appear only at build/link time. Conversely, stale object entries break builds when a source is renamed. Because the driver exports symbols to auxiliary clients, build composition must stay in sync with exported helper implementations.

## Test Signals
Primary checks are `make M=drivers/net/ethernet/amd/pds_core`, full kernel builds for built-in and modular `CONFIG_PDS_CORE`, and link/load tests that confirm `pds_core` contains all exported symbols used by client drivers.
