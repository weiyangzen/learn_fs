# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_topology.h

## Purpose
Defines KFD topology property structures used to represent HSA nodes, memory banks, caches, I/O links, performance blocks, system properties, and DMI memory descriptors.

## Important APIs, Types, And Functions
`struct kfd_node_properties` mirrors node-level sysfs properties including capability fields, debug properties, clocks, device identifiers, queue counts, SDMA counts, CWSR/control stack sizes, and public name. `struct kfd_mem_properties`, `struct kfd_cache_properties`, and `struct kfd_iolink_properties` carry per-child sysfs attributes and optional GPU pointers for permission checks. `struct kfd_topology_device` groups all lists and kobjects for one HSA node. `struct kfd_system_properties` owns global topology sysfs kobjects and generation/platform fields. The header declares topology device allocation/release helpers and `kfd_update_svm_support_properties` when KFD is enabled.

## Control Flow
The implementation allocates these structures while parsing CRAT/VCRAT, links them into topology lists, builds sysfs from embedded attributes/kobjects, and frees them on topology removal/shutdown.

## State And Persistence
All structures are runtime state. They mirror sysfs output but do not persist outside the kernel. OEM fields are copied from CRAT data; DMI memory device data is used to patch CPU memory width and clock values.

## Dependencies And Integration Points
Depends on Linux DMI, list, types, and `linux/kfd_sysfs.h` constants plus KFD CRAT structures. The shape of these structs is tightly coupled with sysfs show/build code in `kfd_topology.c` and CRAT parser fill routines.

## Risks
Embedded `struct attribute` and kobject pointers require strict lifetime pairing. Changing property fields without updating sysfs show code or CRAT parsing can silently hide or misreport topology data. `CACHE_SIBLINGMAP_SIZE` bounds generated cache sibling maps and must remain large enough for supported XCC/CU layouts.

## Test Signals
Compile checks catch type drift. Runtime tests should compare sysfs `properties` files against expected struct fields, especially for cache sibling maps, P2P links, debug properties, and SVM capability updates.
