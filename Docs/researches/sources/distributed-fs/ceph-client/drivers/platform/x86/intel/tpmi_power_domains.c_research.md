# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/tpmi_power_domains.c

## Purpose

This module builds a mapping between Linux CPU numbers and Intel TPMI/P-unit power-domain identifiers using `MSR_PM_LOGICAL_ID`. Other TPMI-based drivers use it to translate package/domain/core IDs and obtain power-domain CPU masks.

## Important APIs, Types, And Functions

`struct tpmi_cpu_info` stores Linux CPU, package, P-unit thread/core/domain IDs, and a hash node. Exported APIs are `tpmi_get_linux_cpu_number()`, `tpmi_get_punit_core_number()`, `tpmi_get_power_domain_id()`, `tpmi_get_power_domain_mask()`, and `tpmi_get_linux_die_id()`. `tpmi_cpu_online()` populates per-CPU info, per-domain cpumasks, hash entries, and domain-to-die mapping.

## Control Flow

Module init matches supported Intel models, verifies MSR `0x54`, allocates `topology_max_packages() * MAX_POWER_DOMAINS` masks and die-map entries, then installs a dynamic CPU hotplug online callback. Each online CPU reads the logical ID MSR, decodes LP/module/domain fields, and records mapping data under `tpmi_lock`. Exit removes the hotplug state and frees arrays.

## State And Persistence

State includes per-CPU `tpmi_cpu_info`, a global hash keyed by P-unit core ID, per-package/domain cpumasks, and a package/domain die map. It is volatile kernel memory.

## Dependencies And Integration Points

The module depends on x86 CPU model matching, cpuhotplug, topology APIs, MSR access, cpumasks, and exports namespace `INTEL_TPMI_POWER_DOMAIN`, imported by TPMI SST and related drivers.

## Risks

There is no CPU offline callback to clear masks/hash entries, so CPU hot-unplug could leave stale mappings. `tpmi_get_power_domain_mask()` returns a pointer after dropping the mutex guard, so callers see shared mutable masks. Hash lookup by core ID also filters package/domain, but duplicate core IDs within a domain would return the first online CPU. Domain count is fixed at 8.

## Test Signals

CPU model matching, MSR decode correctness, CPU hotplug online population, exported lookup functions for all online CPUs, multi-package/domain masks, invalid CPU/package/domain rejection, and hot-unplug behavior should be tested.
