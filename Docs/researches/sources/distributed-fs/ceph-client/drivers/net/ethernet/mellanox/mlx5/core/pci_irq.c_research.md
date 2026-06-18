# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/pci_irq.c

## Purpose

`pci_irq.c` manages MSI-X IRQ allocation for mlx5 PCI PF/VF devices and for subfunctions that borrow their parent device IRQ table. It provides refcounted IRQ objects, IRQ pools for PCI functions and SF control/completion vectors, notifier fanout from the interrupt handler to EQ users, dynamic MSI-X vector allocation when supported, CPU affinity hints, and VF MSI-X table sizing commands.

## Important APIs, Types, and Functions

The central objects are `struct mlx5_irq`, which owns an atomic notifier head, affinity mask, MSI map, pool index, and refcount, and `struct mlx5_irq_table`, which points to `pcif_pool`, `sf_ctrl_pool`, and `sf_comp_pool`. Pool layout is defined by `struct mlx5_irq_pool` in `pci_irq.h`.

Public entry points include `mlx5_irq_table_init()`, `mlx5_irq_table_create()`, `mlx5_irq_table_destroy()`, `mlx5_irq_table_free_irqs()`, `mlx5_irq_table_cleanup()`, `mlx5_irq_table_get()`, `mlx5_irq_table_get_num_comp()`, `mlx5_irq_table_get_sfs_vec()`, `mlx5_irq_table_get_comp_irq_pool()`, `mlx5_ctrl_irq_request()`, `mlx5_ctrl_irq_release()`, `mlx5_irq_request()`, `mlx5_irq_request_vector()`, `mlx5_irq_release_vector()`, `mlx5_irq_attach_nb()`, `mlx5_irq_detach_nb()`, and accessors for IRQ number, index, pool, and affinity mask. VF sizing helpers are `mlx5_get_default_msix_vec_count()` and `mlx5_set_msix_vec_count()`.

## Control Flow

Table creation calculates PCI function completion vectors from ports, online CPUs, EQ capacity, and PCI MSI-X count. If dynamic MSI-X allocation is supported, only vector 0 is allocated initially and later completion vectors use `pci_msix_alloc_irq_at()`. Otherwise all requested vectors are statically allocated by `pci_alloc_irq_vectors()`. `irq_pools_init()` creates the base PCI pool and, if SF capacity exists, carves SF control and completion pools from the remaining vector range.

An IRQ request enters `irq_pool_request_vector()`, which locks the pool and either increments the refcount of an existing xarray entry or calls `mlx5_irq_alloc()`. Allocation creates the `mlx5_irq`, obtains the static or dynamic MSI map, optionally adds a CPU rmap entry for RFS, formats a name, calls `request_irq()` with `irq_int_handler()`, applies affinity hints, and stores the object in the pool xarray. The interrupt handler only calls the atomic notifier chain; EQ objects attach/detach notifier blocks with `mlx5_irq_attach_nb()` and `mlx5_irq_detach_nb()`.

Release uses `_mlx5_irq_release()` to synchronize the IRQ line and decrement the refcount. When it reaches zero, `irq_release()` erases the xarray entry, clears affinity/rmap state, frees the IRQ and dynamic MSI-X vector if needed, releases the cpumask, and frees the object. Shutdown has a special `mlx5_system_free_irq()` path used by `mlx5_irq_table_free_irqs()` to drop OS IRQ resources while keeping mlx5 software IRQ objects alive for later teardown.

## State and Persistence Behavior

Persistent driver state includes `dev->priv.irq_table`, pool xarrays, per-IRQ refcounts, per-IRQ notifier chains, affinity masks, pool thresholds, and optional SF `irqs_per_cpu` arrays. Hardware/PCI state includes allocated MSI-X vectors and per-VF `dynamic_msix_table_size` set through HCA capability commands. SF devices do not own an IRQ table; `mlx5_irq_table_get()` redirects them to `parent_mdev->priv.irq_table`.

## Dependencies and Integration Points

The file integrates with Linux PCI MSI-X APIs, IRQ request/free APIs, `irq_affinity_desc`, RFS `cpu_rmap`, mlx5 EQ code, SF capability helpers, vport capability access for VF MSI-X table updates, and SR-IOV control (`mlx5_core_sriov_set_msix_vec_count()`). Control IRQs are used by async/event EQs; completion IRQs are used by data path EQs.

## Risks and Edge Cases

The code has several split teardown paths: normal refcount release, table destroy cleanup, and system-free for shutdown. Double-free prevention relies on caller sequencing and xarray/refcount invariants. `mlx5_irq_request()` logs `af_desc->mask` and assumes affinity descriptor is present; callers should avoid passing NULL there. Dynamic MSI-X support changes index semantics because nonzero vectors may be allocated at any MSI index while `pool_index` remains the logical index. SF pools can be absent, in which case SFs fall back to PCI function IRQs with lower performance.

## Test Signals

Exercise static and dynamic MSI-X platforms, single-vector devices, multiport devices, SF-heavy configurations, CPU hotplug/online CPU count changes, RFS-enabled builds, notifier attach/detach failure paths, driver shutdown with live EQ references, and VF MSI-X resizing via sysfs. Inspect `/proc/interrupts`, IRQ affinity hints, xarray leak warnings, and that completion EQs do not share above pool thresholds unexpectedly.
