# sources/distributed-fs/ceph-client/include/linux/irqdesc.h

## Purpose
`irqdesc.h` defines the generic IRQ descriptor structure and descriptor-level helpers used by core IRQ handling, statistics, proc/debugfs/sysfs exposure, action lists, threaded IRQ synchronization, and mapping hardware interrupts to flow handlers.

## Important APIs, types, and functions
Important types include `struct irqstat`, `struct irq_redirect`, and `struct irq_desc`. Helpers include sparse IRQ locking, `irq_desc_kstat_cpu`, `irq_data_to_desc`, descriptor getters, `generic_handle_irq_desc`, `handle_irq_desc`, `generic_handle_irq*`, domain handle helpers, `irq_desc_has_action`, locked handler/chip setters, status checks, balancing/percpu predicates, and lockdep-class setup.

## Control flow
Architecture or domain code resolves an IRQ descriptor and invokes its `handle_irq`. Flow handlers inspect descriptor state, call actions, update stats, coordinate threaded handlers, and use locks. Domain helpers translate hwirq to desc before dispatch.

## State and persistence
Descriptor state includes common/chip data, stats, flow handler, actions, status bits, disable/wake depth, spurious counters, locks, percpu enable masks, affinity hints, pending masks, threaded IRQ bookkeeping, proc/debugfs/sysfs nodes, parent IRQ, owner, and software resend node.

## Dependencies and integration points
It depends on irq work, kobjects, mutexes, RCU, generic IRQ domains, proc/debugfs, sparse IRQ, SMP affinity, PM sleep, and lockdep.

## Risks and test signals
Risks include descriptor lifetime races under sparse IRQ, action teardown while handlers run, stats drift, wrong locked setter use, threaded IRQ synchronization bugs, and proc/debugfs stale entries. Tests should cover request/free races, generic/domain dispatch, threaded oneshot handlers, sparse descriptor allocation/free, CPU affinity changes, and PM suspend counters.
