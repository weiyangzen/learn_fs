# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-iproc-msi.c

## Purpose

`pcie-iproc-msi.c` implements the internal event-queue MSI controller used by older Broadcom iProc PCIe variants when MSI is not handled by an external GIC ITS. It creates a PCI MSI parent domain, allocates MSI vectors across hardware event queues, programs event-queue and MSI write-address memory, chains GIC interrupts, and supports CPU-affinity steering by changing hardware IRQ numbers.

## Important APIs, Types, And Functions

- `struct iproc_msi` owns MSI controller state: register layout, GIC IRQ groups, CPU count, vector bitmap, IRQ domain, DMA event queue memory, and MSI posted-write address.
- `struct iproc_msi_grp` binds one GIC interrupt to one MSI event queue.
- `iproc_msi_init()` validates the MSI OF node, sizes IRQ groups, selects PAXB/PAXC register layouts, allocates vector bitmap and group state, maps GIC IRQs, allocates coherent event queue memory, creates the parent MSI domain, installs chained handlers for online CPUs, and enables hardware.
- `iproc_msi_exit()` disables hardware, removes chained handlers, removes the IRQ domain, frees coherent memory, and disposes IRQ mappings.
- `iproc_msi_handler()` drains an event queue by comparing head/tail pointers, decodes MSI data, dispatches through `generic_handle_domain_irq()`, and advances the head pointer.
- `iproc_msi_irq_domain_alloc()` and `iproc_msi_irq_domain_free()` manage vector allocation with CPU-stride reservations.
- `iproc_msi_irq_set_affinity()` rewrites `irq_data->hwirq` to select the target CPU's group.
- `iproc_msi_irq_compose_msi_msg()` writes the MSI target address and data payload expected by iProc hardware.

## Control Flow

The common iProc host code calls `iproc_msi_init()` when an `msi-parent` or `msi-map` node is compatible with `brcm,iproc-msi`. Initialization rejects nodes without `msi-controller`, existing MSI state, insufficient GIC IRQs for CPU affinity, and incompatible controller types. It may reduce the IRQ group count to a multiple of CPU count. After allocating state, it maps each GIC IRQ, allocates DMA memory for event queues, creates the MSI parent domain, installs chained handlers per online CPU, programs queue pages and MSI address pages, and enables queue interrupts. Runtime MSI delivery enters through the chained GIC IRQ, drains queue entries, decodes canonical hardware IRQs, and dispatches to the inner domain.

## State And Persistence

MSI vector ownership persists in `msi->bitmap` under `bitmap_lock`. Event queue contents live in coherent DMA memory shared with hardware. `irq_data->hwirq` can change when affinity changes; canonical hardware IRQ allocation remains CPU0-based for freeing. Register state is programmed during enable and cleared during disable. The file does not write persistent storage.

## Dependencies And Integration Points

The file depends on OF MSI nodes, `of_irq_count()`, `irq_of_parse_and_map()`, irqdomain MSI library, chained IRQ APIs, coherent DMA allocation, CPU masks/online CPU iteration, and the shared `struct iproc_pcie`. It is compiled only when `CONFIG_PCIE_IPROC_MSI` exposes the declarations in `pcie-iproc.h`.

## Risks And Edge Cases

- MSI affinity assumes the number of hardware IRQ groups is at least the CPU count and is reduced to a multiple of CPUs. Hotplug or unusual CPU topology could leave only online CPUs configured at init time.
- Multi-MSI allocation is rejected when multiple CPUs are present, because affinity steering reserves CPU-strided vectors.
- `CFG`/event queue memory ordering depends on hardware guarantee that queue data is visible before tail update.
- `iproc_msi_exit()` does not explicitly set `pcie->msi = NULL`; teardown order currently prevents reuse, but reinitialization assumptions should be checked if lifecycle changes.
- The parent ops object is global and has supported flags modified when `nr_cpus == 1`, so flag state is shared across instances.

## Test Signals

Validate with a `brcm,iproc-msi` node, multiple GIC IRQ counts, single-CPU and multi-CPU configurations, MSI and MSI-X endpoint interrupts, affinity changes, vector exhaustion, event queue wraparound, missing `msi-controller`, incompatible PAXB_V2/PAXC_V2 cases, teardown during remove, and `/proc/interrupts` distribution across expected GIC IRQs.
