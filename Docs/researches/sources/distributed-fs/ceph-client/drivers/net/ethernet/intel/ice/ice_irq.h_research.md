# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_irq.h

## Purpose
Defines interrupt tracking data structures and declares the PF/VF interrupt allocation interface.

## Important APIs, types, and functions
- `struct ice_irq_entry` records vector index and whether the entry was dynamically allocated.
- `struct ice_irq_tracker` owns the xarray of allocated PF vectors plus total/static counts.
- `struct ice_virt_irq_tracker` owns the VF bitmap, number of entries, and PF-relative base index.
- Declares `ice_init_interrupt_scheme()`, `ice_clear_interrupt_scheme()`, `ice_alloc_irq()`, `ice_free_irq()`, `ice_virt_get_irqs()`, and `ice_virt_free_irqs()`.

## Control flow
No executable flow. The structures define how `ice_irq.c` tracks static, dynamic, and VF-reserved MSI-X indices.

## State and persistence behavior
The structs are embedded in `struct ice_pf` and represent in-memory PCI interrupt allocation state. No persistent storage is involved.

## Dependencies and integration points
Requires `struct ice_pf`, `struct msi_map`, xarray, and bitmap users in implementation. It is included by code that allocates vectors for LAN, RDMA, timestamping, and virtualization.

## Risks
The header-level contract exposes `dyn_only`/dynamic behavior through a boolean; callers must understand whether static fallback is allowed. Layout changes affect `struct ice_pf` users.

## Test signals
Compile and runtime tests around vector allocation, dynamic-only RDMA vectors, and SR-IOV vector bitmap allocation cover this interface.
