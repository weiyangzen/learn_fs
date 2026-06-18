<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/affinity.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/affinity.c

## Purpose

This file manages HFI1 CPU affinity policy for MSI-X interrupts, completion vectors, and user processes. It builds NUMA-aware CPU masks, avoids hyperthread siblings where possible, spreads SDMA and receive interrupts, tracks CPUs reserved for completion vectors, reacts to user IRQ affinity changes, and recommends process CPU placement for PSM/user contexts.

## Important APIs, types, and functions

Public entry points are `init_real_cpu_mask()`, `node_affinity_init()`, `node_affinity_destroy_all()`, `hfi1_dev_affinity_init()`, `hfi1_dev_affinity_clean_up()`, `hfi1_comp_vectors_set_up()`, `hfi1_comp_vectors_clean_up()`, `hfi1_comp_vect_mappings_lookup()`, `hfi1_get_irq_affinity()`, `hfi1_put_irq_affinity()`, `hfi1_get_proc_affinity()`, and `hfi1_put_proc_affinity()`.

Important state includes global `node_affinity`, per-node `struct hfi1_affinity_node`, per-mask generation tracking in `struct cpu_mask_set`, the per-NUMA-node HFI device counter `hfi1_per_node_cntr`, per-device completion vector masks and mappings, and MSI-X entry masks. Internal helpers allocate per-node records, select least-used per-CPU completion-vector counters, create mapping tables, and update SDMA affinity notifiers.

## Control Flow

`node_affinity_init()` initializes global process masks, records topology counts, builds the real CPU mask by removing hyperthread siblings, scans PCI devices in `hfi1_pci_tbl`, and counts HFI devices per NUMA node. `hfi1_dev_affinity_init()` creates or reuses a NUMA-node entry, partitions CPUs into general/control, receive, SDMA/default, and completion-vector masks, reserves a per-device share of completion-vector CPUs, and stores the entry on the device.

`hfi1_comp_vectors_set_up()` converts a device completion-vector CPU mask into an index-to-CPU mapping, preferring CPUs not already used by default interrupts. `hfi1_get_irq_affinity()` selects a CPU based on IRQ type, sets `msix->mask`, publishes an IRQ affinity hint, and registers an SDMA notifier. If users later change an SDMA IRQ affinity through `/proc/irq`, the notifier updates `sde->cpu` and the global default interrupt mask. `hfi1_put_irq_affinity()` reverses accounting and removes hints/notifiers.

`hfi1_get_proc_affinity()` first respects a process already pinned to one CPU or a smaller explicit cpuset. Otherwise it chooses a CPU by generation: preferred NUMA node before other nodes, non-interrupt CPUs before interrupt CPUs, and physical cores before later hyperthreads. `hfi1_put_proc_affinity()` releases the CPU back to the global process mask.

## State and Persistence

All state is runtime-only. `node_affinity` and `hfi1_per_node_cntr` are module-global and protected by `node_affinity.lock` for list and mask mutation. Per-device state includes `dd->affinity_entry`, `dd->comp_vect`, `dd->comp_vect_possible_cpus`, and `dd->comp_vect_mappings`. `cpu_mask_set.gen` supports controlled overcommit by clearing or restoring `used` masks once all CPUs in a set have been consumed or released.

## Dependencies and Integration Points

The file depends on Linux topology, cpumask, interrupt affinity notifier, NUMA, PCI enumeration, and HFI1 internals from `hfi.h`, `sdma.h`, and `trace.h`. It integrates with MSI-X setup/teardown, SDMA engine CPU fields, RDMAVT completion-vector lookup, kernel receive queues, user context open/close paths, and debug tracing categories.

## Risks

Mask arithmetic is the main risk. Incorrect generation handling can overload CPUs prematurely or fail to release CPUs for later devices. NUMA fallback handles invalid PCI NUMA data by assigning one device per possible node, but performance may degrade. Some paths assume `node_affinity_lookup(dd->node)` succeeds after device init; calling IRQ teardown without prior init could dereference missing entries. `hfi1_update_sdma_affinity()` rejects `cpu > num_online_cpus()` rather than `cpu >= nr_cpu_ids`, which is worth reviewing for sparse CPU IDs. Completion-vector allocation depends on accurate `hfi1_per_node_cntr` and `dd->n_krcv_queues`; topology changes after init are not dynamically rebalanced.

## Test Signals

Validation signals include boot logs showing IRQ-to-CPU assignments, `/proc/interrupts` distribution across NUMA-local CPUs, SDMA notifier behavior when IRQ affinity is manually changed, completion-vector lookup returning stable CPUs, process affinity recommendations under default and pre-pinned cpusets, multi-device systems on the same NUMA node, systems with and without SMT, and invalid/missing PCI NUMA node fallback. Lockdep and KASAN are useful around init/cleanup and IRQ teardown ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/affinity.c -->
