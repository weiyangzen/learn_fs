# sources/distributed-fs/ceph-client/kernel/irq/chip.c

## Purpose
`chip.c` is the generic IRQ-chip and flow-handler core. It configures IRQ chips and handlers, manages startup/shutdown/disable/mask/unmask state, implements standard level/edge/fasteoi/percpu/NMI flow handlers, supports chained interrupts, forwards operations through IRQ domain hierarchies, and manages chip runtime PM.

## Important APIs, types, and functions
Configuration APIs include `irq_set_chip()`, `irq_set_irq_type()`, `irq_set_handler_data()`, `irq_set_msi_desc[_off]()`, `irq_set_chip_data()`, `irq_get_irq_data()`, `__irq_set_handler()`, `irq_set_chained_handler_and_data()`, `irq_set_chip_and_handler_name()`, and `irq_modify_status()`. Lifecycle helpers include `irq_startup()`, `irq_activate()`, `irq_shutdown()`, `irq_shutdown_and_deactivate()`, `irq_disable()`, `mask_irq()`, `unmask_irq()`, and percpu enable/disable. Flow handlers include `handle_simple_irq()`, `handle_level_irq()`, `handle_fasteoi_irq()`, `handle_fasteoi_nmi()`, `handle_edge_irq()`, `handle_percpu_irq()`, and `handle_percpu_devid_irq()`. Hierarchy helpers include the `irq_chip_*_parent()` family, MSI compose, redirect affinity, and PM get/put.

## Control flow
Startup clears disable depth, handles managed-affinity interrupts specially, activates domains, optionally sets affinity before or after chip startup, and may resend pending interrupts. Shutdown clears resend state, increments depth, calls chip shutdown or disable, marks disabled/masked, and deactivates the domain when requested. Flow handlers lock the descriptor, perform chip-specific ack/mask/eoi operations, test PM and action eligibility, update stats, run handlers through `handle_irq_event()`, and unmask or resend according to type and oneshot state. Chained handler installation marks descriptors no-probe/no-request/no-thread, installs a synthetic action, takes chip PM, and starts the line immediately.

## State and persistence
Persistent state is stored in `struct irq_desc` and `struct irq_data`: chip pointers, handler data, MSI descs, status bits, `IRQD_*` state, disable depth, action list, threaded oneshot state, affinity, and PM references. Hierarchical domains persist parent `irq_data` chains. No disk persistence exists.

## Dependencies and integration points
This file is used by nearly every irqchip driver and interrupt consumer. It depends on descriptor locking from `irqdesc.c`, status helpers from `settings.h`, event execution from `handle.c`, irqdomain activation/deactivation, resend/spurious/PM support, tracepoints, kernel stats, SMP affinity, and MSI/domain hierarchy callbacks.

## Risks and test signals
Risks include imbalanced disable depth for managed interrupts, lazy disable leaving unsafe devices unmasked, action-less chained IRQ misuse, incorrect ack/mask/eoi ordering for controller type, pending resend loops on edge interrupts, parent hierarchy callback absence, runtime PM reference leaks, and races with affinity migration. Test signals include level/edge/fasteoi/oneshot threaded IRQs, chained controller setup/removal, managed IRQ CPU hotplug, domain activation failure, wakeup during suspend, parent-domain forwarding, `IRQCHIP_EOI_THREADED`, and KUnit depth/hotplug tests.
