# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_irq.c

## Purpose
Centralizes MSI-X interrupt vector allocation for the `ice` PF and reserves a virtual vector range for SR-IOV VFs. It supports both static vectors allocated by `pci_alloc_irq_vectors()` and dynamic MSI-X allocation when the PCI core supports it.

## Important APIs, types, and functions
- `ice_init_interrupt_scheme()` determines min/max MSI-X counts, allocates vectors, initializes the xarray tracker, and initializes the VF bitmap tracker.
- `ice_clear_interrupt_scheme()` frees PCI vectors and destroys both trackers.
- `ice_alloc_irq()` reserves an `ice_irq_entry` and returns an `msi_map`, dynamically allocating with `pci_msix_alloc_irq_at()` for dynamic entries when possible.
- `ice_free_irq()` frees dynamic PCI MSI-X state if needed and removes the tracker entry.
- `ice_virt_get_irqs()` allocates a contiguous bitmap range for VF vector indices.
- `ice_virt_free_irqs()` clears a VF bitmap range.
- Internal helpers initialize/deinitialize trackers and allocate/free xarray entries.

## Control flow
Initialization computes the default desired MSI-X amount from LAN/OICR, RSS queues, Flow Director, and RDMA needs. If dynamic MSI-X is available, it initially allocates only the minimum static vectors; otherwise it allocates the full maximum. Runtime callers request vectors through `ice_alloc_irq()`, which first reserves the lowest valid tracker slot and then either maps an existing static vector or allocates a dynamic vector at that index. VF allocation is separate: it assigns indexes from a bitmap offset by `virt_irq_tracker.base`.

## State and persistence behavior
State lives in `pf->msix`, `pf->irq_tracker.entries`, and `pf->virt_irq_tracker.bm/base/num_entries`. This is in-memory state tied to PCI interrupt vectors; it is torn down by `ice_clear_interrupt_scheme()`.

## Dependencies and integration points
Depends on PCI MSI-X APIs, xarray, bitmap allocation, RSS queue defaults, Flow Director flag state, RDMA enablement, and `ice_pf` MSI-X capability data. Integrated callers include OICR and timestamp interrupt setup in `ice_main.c`, RDMA qvector allocation in `ice_idc.c`, and SR-IOV vector mapping code.

## Risks
Off-by-one errors in `num_static - 1` and dynamic/static boundaries would leak or misclassify vectors. `ice_free_irq()` logs and returns on unknown indexes, so double-free bugs are visible but not fatal. VF bitmap APIs assume callers pass indexes originally returned by `ice_virt_get_irqs()`.

## Test signals
Exercise devices with and without dynamic MSI-X support, low-vector configurations, RDMA enabled/disabled, Flow Director enabled/disabled, repeated vector alloc/free, allocation exhaustion, SR-IOV VF range allocation/free, and teardown after partial initialization failure.
