# sources/distributed-fs/ceph-client/kernel/irq/affinity.c

## Purpose
`affinity.c` computes default interrupt affinity masks for multiqueue devices and determines a suitable vector count from driver affinity requirements. It spreads managed vectors over present CPUs while preserving pre/post vectors that should use default affinity.

## Important APIs, types, and functions
Public functions are `irq_create_affinity_masks()` and `irq_calc_affinity_vectors()`. The helper `default_calc_sets()` fills a single affinity set. The code operates on `struct irq_affinity`, `struct irq_affinity_desc`, `irq_default_affinity`, CPU masks, and `group_cpus_evenly()`.

## Control flow
`irq_create_affinity_masks()` subtracts pre/post vectors from total vectors, installs a default set calculator when the caller did not provide one, asks the callback to partition affinity vectors into sets, allocates one descriptor per vector, fills pre vectors with default affinity, spreads each set with `group_cpus_evenly()`, fills any trailing or excess vectors with default affinity, and marks the actual affinity range as managed. `irq_calc_affinity_vectors()` rejects configurations where reserved vectors exceed the minimum and otherwise returns reserved vectors plus either callback-limited or CPU-count-limited affinity vectors.

## State and persistence
The only persisted state is the caller-owned returned `irq_affinity_desc` array. The function may mutate `affd->calc_sets`, `affd->nr_sets`, and `affd->set_size[]` via the callback. No global state is modified.

## Dependencies and integration points
This file is used by PCI/MSI and other multiqueue interrupt allocation paths before descriptors are allocated. It depends on SMP CPU masks, `irq_default_affinity`, allocation helpers, and `group_cpus_evenly()` from the CPU grouping code.

## Risks and test signals
Risks include off-by-one handling of pre/post vectors, mismatched callback set sizes versus available vectors, empty CPU-group allocation failures, `IRQ_AFFINITY_MAX_SETS` overflow, and surprising default-affinity fallback for non-managed vectors. Test signals include vector counts below, equal to, and above reserved pre/post counts; multiple set layouts; CPU hotplug/topology variations; allocation failure; and managed mask propagation into descriptor allocation.
