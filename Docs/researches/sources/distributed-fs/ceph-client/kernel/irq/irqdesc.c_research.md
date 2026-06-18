# sources/distributed-fs/ceph-client/kernel/irq/irqdesc.c

## Purpose
`irqdesc.c` manages IRQ descriptors: early initialization, sparse/non-sparse allocation, descriptor lookup, sysfs/debugfs/proc registration, generic IRQ dispatch by number/domain, demux redirection, dynamic descriptor allocation/free, per-CPU statistics, and lockdep class assignment.

## Important APIs, types, and functions
Key APIs include `early_irq_init()`, `irq_to_desc()`, `irq_get_nr_irqs()`, `irq_set_nr_irqs()`, `irq_lock_sparse()`, `irq_unlock_sparse()`, `handle_irq_desc()`, `generic_handle_irq()`, `generic_handle_irq_safe()`, `generic_handle_domain_irq()`, `generic_handle_domain_irq_safe()`, `generic_handle_domain_nmi()`, `generic_handle_demux_domain_irq()`, `irq_free_descs()`, `__irq_alloc_descs()`, `irq_get_next_irq()`, `__irq_get_desc_lock()`, `__irq_put_desc_unlock()`, `irq_set_percpu_devid()`, `kstat_irqs_cpu()`, `kstat_irqs_usr()`, snapshot helpers, and `__irq_set_lockdep_class()`. Internal structures include sparse maple tree `sparse_irqs`, `sparse_irq_lock`, sysfs kobjects, and per-descriptor masks/stats.

## Control flow
Early init establishes default affinity, asks the architecture for IRQ counts, allocates initial descriptors, and calls architecture early IRQ init. Sparse builds store descriptors in an RCU-enabled maple tree, allocate/free descriptors dynamically, and expose sysfs attributes for counts/chip/hwirq/type/wakeup/name/actions. Non-sparse builds initialize a static array and reset descriptors on free. Dispatch helpers resolve IRQ numbers or domain hwirqs to descriptors and call the installed flow handler, with safe variants saving local IRQ state. Dynamic allocation finds a free range, expands `nr_irqs` when possible, initializes masks/stats/locks, inserts descriptors, and registers sysfs/debugfs/proc entries.

## State and persistence
Persistent runtime state includes global `nr_irqs`, sparse maple tree or static descriptor array, descriptor locks/masks/actions/stats, sysfs kobjects, RCU-delayed descriptor frees, and default affinity masks. Per-IRQ stats persist since boot and may have per-CPU snapshot references when enabled. No disk persistence exists.

## Dependencies and integration points
This file is the backbone for `chip.c`, `handle.c`, irqdomain, procfs, sysfs, debugfs, CPU affinity, KVM symbol users, architecture IRQ initialization, and interrupt statistics exposed to userspace. It depends on maple tree, RCU, kobjects, percpu allocation, cpumasks, and architecture hooks.

## Risks and test signals
Risks include descriptor lifetime races across RCU/debugfs/sysfs/proc, sparse tree allocation range mistakes, non-sparse reset divergence, dispatch from wrong context when IRQ context is enforced, demux redirection to offline CPUs, managed affinity flags set from affinity descriptors, and stat races tolerated with data-race reads. Test signals include sparse and non-sparse boots, dynamic allocation/free/reuse, sysfs attributes, generic domain dispatch, demux redirection, percpu devid setup, kstat reads during free, snapshot stats, and lockdep class changes.
