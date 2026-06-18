# sources/distributed-fs/ceph-client/kernel/irq/irq_sim.c

## Purpose
`irq_sim.c` implements an interrupt simulator backed by an IRQ domain and `irq_work`. It is useful for tests and drivers that need software-triggerable IRQ lines without real hardware.

## Important APIs, types, and functions
Core types are `struct irq_sim_work_ctx` and `struct irq_sim_irq_ctx`. Public APIs are `irq_domain_create_sim()`, `irq_domain_create_sim_full()`, `irq_domain_remove_sim()`, `devm_irq_domain_create_sim()`, and `devm_irq_domain_create_sim_full()`. The simulated chip is `irq_sim_irqchip` with mask/unmask, set_type, get/set pending state, and resource request/release callbacks. Domain operations are `irq_sim_domain_map()` and `irq_sim_domain_unmap()`.

## Control flow
Domain creation allocates work context, a pending bitmap, and a linear IRQ domain using the work context as host data. Mapping allocates per-IRQ context, installs `irq_sim_irqchip`, chip data, `handle_simple_irq`, and status flags. Setting pending state on an enabled IRQ sets a bit and queues hard irq_work. The irq_work handler drains pending bits, resolves each hwirq to a virq, and calls `handle_simple_irq()` on its descriptor. Removal synchronizes irq_work, frees the bitmap/work context, and removes the domain; devm variants register this removal as a device action.

## State and persistence
Simulator state persists in the domain host data, pending bitmap, hard irq_work item, optional user ops/data, and per-IRQ enabled flags. Pending bits are transient and cleared by the work handler. The state ends with explicit or devm domain removal.

## Dependencies and integration points
The file depends on IRQ domains, simple IRQ flow handling, irq_work, bitmap allocation, irqchip state APIs, devres, and optional `struct irq_sim_ops` callbacks for request/release notifications. It is selected by `IRQ_SIM`.

## Risks and test signals
Risks include pending-state operations ignored while masked, work handler resolving an unmapped IRQ during teardown if synchronization is wrong, unsupported non-edge trigger types, callback failures during request, and missing descriptor freeing by domain callers. Test signals include create/remove, devm cleanup, pending state set/get, masked pending behavior, request/release callbacks, trigger type rejection, and multiple pending IRQ drain ordering.
