# sources/distributed-fs/ceph-client/drivers/perf/arm_cspmu/arm_cspmu.h

Purpose: Defines the shared register constants, attribute helpers, data structures, implementer-backend contracts, and exported helper prototypes for the ARM CoreSight PMU architecture driver and vendor modules.

Important APIs and types: Provides register offsets and bitfields for PMEV counters, filters, PMCR, PMCFGR, PMIIDR/PMPIDR, event/filter masks, default format/event attribute macros, implementer IDs, and maximum counter constants. Defines `struct arm_cspmu_hw_events`, `struct arm_cspmu_impl_ops`, `struct arm_cspmu_impl_match`, `struct arm_cspmu_impl`, and `struct arm_cspmu`. Declares `arm_cspmu_sysfs_event_show()`, `arm_cspmu_impl_register()`, `arm_cspmu_impl_unregister()`, and ACPI helper `arm_cspmu_acpi_dev_get()` with a stub outside ACPI+ARM64.

Control flow: The header has no executable runtime logic except the ACPI helper stub. It establishes callback flow: generic probe fills default `arm_cspmu_impl_ops`, vendor modules register an `arm_cspmu_impl_match`, and the generic driver calls backend hooks for attributes, naming, event decoding, filter programming, reset, and validation.

State and persistence: No direct state. Structure fields define persistent runtime ownership for PMU device state, counter bitmaps, active CPU masks, MMIO bases, implementation context, and sysfs attribute group pointers.

Dependencies and integration points: Included by `arm_cspmu.c`, `nvidia_cspmu.c`, and `ampere_cspmu.c`. Pulls in Linux ACPI, device, cpumask, perf, platform, module, bitfield, and type headers. The exported registration prototypes are the link contract for vendor backend modules.

Risks: Register definitions are shared by all backends; incorrect offsets or masks break generic and vendor behavior. `ARM_CSPMU_MAX_HW_CNTRS` sizes bitmaps and arrays and must match architectural limits. Callback semantics must remain stable because backend modules may be loaded separately from the generic module. Attribute macros create compound-literal attributes, so use remains intended for static attribute arrays.

Test signals: Compile all generic/vendor combinations, inspect generated sysfs format strings, validate PMIIDR implementer matching, and run sparse/build checks for structure and callback signature drift.
