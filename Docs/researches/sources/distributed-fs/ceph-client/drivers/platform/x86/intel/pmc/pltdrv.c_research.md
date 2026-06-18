# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/pltdrv.c

Purpose: creates a fallback `intel_pmc_core` platform device on older supported Intel systems that lack the preferred ACPI `INT33A1` device.

Important APIs/types/functions: `intel_pmc_core_platform_ids[]` lists legacy CPU models where fallback enumeration is allowed. `pmc_core_platform_init()` checks ACPI, virtualization, CPU match, allocates a `platform_device`, and registers it. `pmc_core_platform_exit()` unregisters it. `intel_pmc_core_release()` frees the manually allocated device.

Control flow: module init exits with `-ENODEV` if ACPI already exposes `INT33A1`, if running under a hypervisor outside Xen dom0, or if the CPU is not in the fallback list. Otherwise it creates a platform device named `intel_pmc_core`, which binds to the core platform driver in `core.c`.

State and persistence: global `pmc_core_device` stores the created platform device until module exit. No hardware state is touched directly here.

Dependencies and integration points: depends on ACPI enumeration, x86 CPU matching, Xen dom0 detection, and the `intel_pmc_core` platform driver name. The file explicitly should not grow for new platforms because ACPI enumeration is preferred.

Risks: overly broad fallback enumeration could attach the PMC driver in unsupported VMs or systems without safe MMIO access; the hypervisor/Xen checks mitigate this. If ACPI detection misses an existing device, duplicate registration could occur, though ACPI presence is checked first.

Test signals: on listed older hardware without ACPI `INT33A1`, `platform_device_register()` should cause `core.c` probe. On newer platforms, VMs, and systems with ACPI device, module init should return `-ENODEV` without side effects.
