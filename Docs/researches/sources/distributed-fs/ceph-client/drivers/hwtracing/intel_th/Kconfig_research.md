# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/Kconfig

## Purpose

`intel_th/Kconfig` defines configuration symbols for the Intel Trace Hub controller, platform glue, subdevices, output devices, and optional debugging support.

## Important APIs, Types, and Functions

The main symbol is `INTEL_TH`, a tristate depending on `HAS_DMA` and `HAS_IOMEM`. Child symbols include `INTEL_TH_PCI`, `INTEL_TH_ACPI`, `INTEL_TH_GTH`, `INTEL_TH_STH`, `INTEL_TH_MSU`, `INTEL_TH_PTI`, and `INTEL_TH_DEBUG`. Dependencies include `PCI`, `ACPI`, `STM`, `MMU`, and `DEBUG_FS` as appropriate.

## Control Flow

When `INTEL_TH` is enabled, the nested menu exposes transport glue and subdevice choices. PCI and ACPI instantiate controllers; GTH is the central switch; STH integrates software sources through STM; MSU stores traces in memory; PTI emits trace through a parallel port; DEBUG adds debugfs support.

## State and Persistence Behavior

Kconfig state controls which objects are built into the kernel or as modules. It does not define runtime state, but selected symbols determine available device probing and user-visible trace functionality.

## Dependencies and Integration Points

The file integrates with the `intel_th/Makefile` object rules and the Linux hwtracing menu hierarchy. It gates ACPI, PCI, STM, memory storage, and debugfs code.

## Risks and Edge Cases

Misconfigured dependencies can produce unbuildable combinations or missing subdevices. Enabling ACPI indicates host-debugger mode where target controls may not be available, which can surprise users expecting local capture control.

## Test Signals

Run build matrix coverage for built-in and module variants, including `INTEL_TH` alone, PCI, ACPI, GTH, STH with STM, MSU with MMU, PTI, and DEBUG with DEBUG_FS.
