# sources/distributed-fs/ceph-client/virt/kvm/irqchip.c

## Purpose
This file provides common in-kernel interrupt routing support for KVM. It maintains the VM's GSI routing table, maps GSIs to kernel routing entries, dispatches interrupt assertions to registered route callbacks, supports userspace-originated MSI injection, and initializes/frees the default route table.

## Important APIs, Types, And Functions
`kvm_irq_map_gsi()` copies all routing entries for a GSI under IRQ SRCU. `kvm_irq_map_chip_pin()` maps an irqchip/pin pair back to a GSI. `kvm_send_userspace_msi()` validates MSI flags and calls `kvm_set_msi()`. `kvm_set_irq()` maps a GSI and calls each route entry's `set()` callback, combining delivery counts. `kvm_set_irq_routing()` builds a new `struct kvm_irq_routing_table`, validates userspace route entries, installs it with RCU, calls generic and architecture update hooks, waits for IRQ SRCU readers, and frees the old table. Weak hooks `kvm_arch_irq_routing_update()` and `kvm_arch_can_set_irq_routing()` let architectures constrain or react to routing changes.

## Control Flow And State
Routing state lives in `kvm->irq_routing`, protected for updates by `kvm->irq_lock` and for readers by `kvm->irq_srcu`. A table contains per-GSI hlist entries and a chip/pin lookup matrix initialized to `-1`. Route setup rejects duplicate mappings to the same irqchip and rejects multiple non-irqchip routes for one GSI. Replacement is copy-build-publish: allocate a complete new table, populate every entry, publish via `rcu_assign_pointer()`, then `synchronize_srcu_expedited()` before freeing the previous table.

## Dependencies And Integration Points
This code depends on `linux/kvm_host.h`, SRCU, RCU, tracepoints, and architecture-provided route translation through `kvm_set_routing_entry()`, `kvm_irq_routing_update()`, and MSI delivery. `kvm_main.c` calls `kvm_init_irq_routing()` during VM creation and `kvm_free_irq_routing()` during destruction; VM ioctls use `KVM_SET_GSI_ROUTING`.

## Risks And Test Signals
Risks include off-by-one `nr_rt_entries` sizing, userspace route validation gaps, stale route access without SRCU, and delivery accounting differences when route callbacks return negative, zero, or positive values. Tests should cover empty routing, duplicate GSI/chip entries, MSI flag validation, concurrent injection during table replacement, VM teardown, and architecture refusal through `kvm_arch_can_set_irq_routing()`.
