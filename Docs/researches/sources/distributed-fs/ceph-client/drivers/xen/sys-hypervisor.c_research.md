# sources/distributed-fs/ceph-client/drivers/xen/sys-hypervisor.c

## Purpose
`sys-hypervisor.c` exposes Xen hypervisor metadata and selected runtime controls under `/sys/hypervisor`. It reports guest type, Xen version, build and feature information, start flags, UUID, and optional VPMU settings.

## Important APIs, types, and functions
The central type is `struct hyp_sysfs_attr`, a wrapper around `struct attribute` with show/store callbacks and per-attribute data. Attribute groups cover `version`, `compilation`, `properties`, `start_flags`, and optional `pmu`. Important show/store functions call `HYPERVISOR_xen_version`, xenbus UUID fallback reads, and `HYPERVISOR_xenpmu_op`. Init functions create files and groups from `hyper_sysfs_init`, while `hypervisor_subsys_init` installs custom sysfs ops on `hypervisor_kobj`.

## Control flow
During device init, the Xen-only initializer creates the basic type and guest-type files, then version, compilation, UUID, property, start-flag, and optional PMU groups, unwinding in reverse order on failure. Sysfs reads dispatch through `hyp_sysfs_show` to the attribute's show function. Writable PMU attributes parse user input and call Xen PMU hypercalls.

## State and persistence
State is mostly sysfs metadata and static attribute arrays. Runtime values are read from the hypervisor on demand. PMU writes affect hypervisor runtime state but are not persisted by this file. UUID may fall back to xenstore if `XENVER_guest_handle` is unavailable.

## Dependencies and integration points
It depends on Xen hypercall interfaces, Xen version structures, xenbus, `hypervisor_kobj`, Linux sysfs/kobject APIs, and optional Xen PMU headers. It integrates with userspace inventory/debug tools that inspect `/sys/hypervisor`.

## Risks and test signals
Risks include init-order coupling with `hypervisor_kobj`, sysfs group unwind mistakes, binary build-id output handling, feature string sizing, xenstored readiness for UUID fallback, and PMU permission/hypervisor support differences. Test signals include booting PV/HVM/PVH/ARM Xen guests, reading all sysfs files, denied build-id behavior, xenstored-delayed UUID fallback, PMU mode/feature read-write tests in dom0, and sysfs error injection.
