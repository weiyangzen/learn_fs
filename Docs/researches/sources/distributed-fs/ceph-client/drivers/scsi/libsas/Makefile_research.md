# sources/distributed-fs/ceph-client/drivers/scsi/libsas/Makefile

## Purpose

This Makefile assembles the libsas helper library object. It defines the always-included core libsas source files and conditionally includes SATA and host SMP support based on Kconfig symbols.

## Important APIs, Types, and Functions

`obj-$(CONFIG_SCSI_SAS_LIBSAS) += libsas.o` creates the libsas composite object. The core `libsas-y` members are `sas_init.o`, `sas_phy.o`, `sas_port.o`, `sas_event.o`, `sas_discover.o`, `sas_expander.o`, `sas_scsi_host.o`, and `sas_task.o`. `libsas-$(CONFIG_SCSI_SAS_ATA)` adds `sas_ata.o`; `libsas-$(CONFIG_SCSI_SAS_HOST_SMP)` adds `sas_host_smp.o`. `ccflags-y` defines `DEBUG` and adds `drivers/scsi` to the include path.

## Control Flow

There is no runtime flow. Kbuild expands the composite object membership according to configuration and compiles all libsas objects with the listed flags.

## State and Persistence Behavior

The file persists build composition only. It does not define runtime state.

## Dependencies and Integration Points

It integrates with the kernel Kbuild system and the libsas Kconfig symbols. The include path supports internal SCSI headers used by libsas sources.

## Risks and Edge Cases

Because `sas_event.o`, `sas_discover.o`, and `sas_expander.o` are core members, topology discovery and event handling are always present with libsas. If `CONFIG_SCSI_SAS_ATA` is unset, references to SATA helper functions must be excluded by preprocessor guards or alternate stubs elsewhere. The unconditional `-DDEBUG` can enable debug code paths or messages expected by this older source tree.

## Test Signals

Build signals include `libsas.o` link membership under each Kconfig combination, absence of unresolved references when ATA or host SMP are disabled, and expected module/built-in generation for `CONFIG_SCSI_SAS_LIBSAS`.
