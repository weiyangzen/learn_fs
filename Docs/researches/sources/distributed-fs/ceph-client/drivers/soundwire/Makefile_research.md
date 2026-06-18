# sources/distributed-fs/ceph-client/drivers/soundwire/Makefile

## Purpose
Builds the SoundWire bus core, optional helper modules, and platform master drivers according to the Kconfig symbols. It defines how the subsystem source files are grouped into kernel modules or built-in objects.

## Important APIs, Types, and Functions
`soundwire-bus-y` groups the core files: `bus_type.o`, `bus.o`, `master.o`, `slave.o`, `mipi_disco.o`, `stream.o`, `sysfs_slave.o`, and `sysfs_slave_dpn.o`. Optional additions are `debugfs.o` under `CONFIG_DEBUG_FS` and `irq.o` under `CONFIG_IRQ_DOMAIN`. `soundwire-generic-allocation-objs` contains `generic_bandwidth_allocation.o`. Driver aggregates are `soundwire-amd-y := amd_init.o amd_manager.o`, `soundwire-cadence-y := cadence_master.o`, `soundwire-intel-y := intel.o intel_ace2x.o intel_ace2x_debugfs.o intel_auxdevice.o intel_init.o dmi-quirks.o intel_bus_common.o`, and `soundwire-qcom-y := qcom.o`.

## Control Flow
The Makefile has build-time flow only. `obj-$(CONFIG_SOUNDWIRE)` emits the bus module. `obj-$(CONFIG_SOUNDWIRE_GENERIC_ALLOCATION)`, `obj-$(CONFIG_SOUNDWIRE_AMD)`, `obj-$(CONFIG_SOUNDWIRE_CADENCE)`, `obj-$(CONFIG_SOUNDWIRE_INTEL)`, and `obj-$(CONFIG_SOUNDWIRE_QCOM)` emit their respective objects. Optional debugfs and IRQ objects are appended to the core bus object list only when their configs are enabled.

## State and Persistence Behavior
There is no runtime state. The generated state is the object graph and module boundaries: the bus core is separated from generic allocation, AMD, Cadence, Intel, and Qualcomm modules unless those are linked built-in by configuration.

## Dependencies and Integration Points
This file is the build integration point for all SoundWire sources in this directory. It mirrors the Kconfig library relationships: AMD links `amd_init.o` and `amd_manager.o` together; Intel links `dmi-quirks.o` into the Intel module rather than the core bus; Cadence is a library object selected by Intel and usable by other platform glue.

## Risks
Moving a source between aggregates changes module ownership and symbol availability. Optional `debugfs.o` and `irq.o` alter exported behavior only when config symbols are enabled, so missing stubs in `bus.h` or callers can break non-debug or non-IRQ-domain builds. Intel-specific `dmi-quirks.o` being in the Intel aggregate means core ACPI discovery cannot rely on those remaps unless the Intel module is enabled.

## Test Signals
Useful signals include clean `M=drivers/soundwire` builds for builtin and module variants, builds with and without `CONFIG_DEBUG_FS` and `CONFIG_IRQ_DOMAIN`, symbol export resolution for generic allocation and Cadence helpers, and module load order for `soundwire-bus`, `soundwire-generic-allocation`, `soundwire-amd`, `soundwire-cadence`, `soundwire-intel`, and `soundwire-qcom`.
