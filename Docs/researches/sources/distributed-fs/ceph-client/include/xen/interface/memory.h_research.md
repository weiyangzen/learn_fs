# sources/distributed-fs/ceph-client/include/xen/interface/memory.h

## Purpose
`memory.h` defines Xen public memory-operation ABI structures and command numbers for changing domain reservations, exchanging pages, mapping foreign or special pages into guest pseudo-physical space, querying memory maps, and acquiring toolstack resources.

## Important APIs, Types, and Functions
Core commands include `XENMEM_increase_reservation`, `decrease_reservation`, `populate_physmap`, `exchange`, `maximum_ram_page`, `current_reservation`, `maximum_reservation`, `machphys_mfn_list`, `machphys_mapping`, `add_to_physmap`, `add_to_physmap_range`, `memory_map`, `machine_memory_map`, `remove_from_physmap`, and `acquire_resource`. Key structs are `xen_memory_reservation`, `xen_memory_exchange`, `xen_machphys_mfn_list`, `xen_add_to_physmap`, `xen_add_to_physmap_range`, `xen_memory_map`, `xen_remove_from_physmap`, and `xen_mem_acquire_resource`.

## Control Flow
Guests or tool domains fill command-specific structures with guest handles and call `HYPERVISOR_memory_op`. Reservation operations allocate/free extents, exchanges atomically replace old extents with new populated extents, physmap operations install or remove mappings, and resource acquisition maps grant-table or ioreq-server frames for a tools domain.

## State and Persistence Behavior
The ABI mutates Xen's domain memory reservation, p2m/m2p mappings, resource ownership, and guest-visible memory maps. State persists until later memory ops, ballooning, hotplug, teardown, or domain destruction.

## Dependencies and Integration Points
It depends on Xen public base types from `xen.h` and guest-handle macros. Linux balloon, memory hotplug, grant-table, device-model, and PV MMU code use these structures to coordinate with Xen.

## Risks and Test Signals
Risks include confusing MFN/GMFN/GPFN roles, uninitialized `nr_exchanged`, overlapping exchange arrays, per-index error handling in ranged mapping, partial resource acquisition cleanup, and privilege checks on foreign domains. Test signals include balloon increase/decrease, populate/exchange partial failures, add/remove physmap range tests, memory-map query sizing, and HVM/PV `acquire_resource` behavior.
