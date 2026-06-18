# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/acpi.c

## Purpose

`intel_th/acpi.c` is the ACPI platform glue driver for Intel Trace Hub controllers. It matches ACPI IDs, collects memory and IRQ resources, allocates the shared Intel TH core object, and frees it on removal.

## Important APIs, Types, and Functions

Static `intel_th_drvdata` instances for PCH and uncore set `host_mode_only = 1`. `intel_th_acpi_ids` matches `INTC1000` and `INTC1001`. `intel_th_acpi_probe` filters platform resources into a fixed `TH_MMIO_END` array and calls `intel_th_alloc`. `intel_th_acpi_remove` calls `intel_th_free`. `module_platform_driver` registers `intel_th_acpi_driver`.

## Control Flow

Probe obtains the ACPI companion and matching ID, copies IRQ and memory resources up to the core limit, allocates the Intel TH core with ID-specific drvdata, and stores the returned pointer in `adev->driver_data`. Remove gets the platform drvdata and frees the core.

## State and Persistence Behavior

The Intel TH core object persists after successful probe until remove. The drvdata marks ACPI devices as host-mode-only, reflecting externally controlled trace capture. No sysfs state is created directly by this glue file.

## Dependencies and Integration Points

The file depends on Linux ACPI/platform APIs, module infrastructure, resource flags, and `intel_th.h` core allocation/free routines. It is built by `CONFIG_INTEL_TH_ACPI`.

## Risks and Edge Cases

Probe stores `adev->driver_data = th`, while remove uses `platform_get_drvdata(pdev)`; correctness depends on `intel_th_alloc` or platform/ACPI glue setting platform drvdata consistently. Resource filtering preserves only IRQ and memory resources and stops at `TH_MMIO_END`, so unexpected resource ordering or extra resources are ignored.

## Test Signals

Test matching for `INTC1000` and `INTC1001`, no-match `-ENODEV`, resource filtering limits, `intel_th_alloc` error propagation, remove-time free, and host-mode-only behavior in the core driver.
