# sources/distributed-fs/ceph-client/include/linux/irq_sim.h

## Purpose
`irq_sim.h` exposes a framework for creating simulated IRQ domains whose IRQs can be requested like real interrupts and triggered from process context.

## Important APIs, types, and functions
The header defines `struct irq_sim_ops` callbacks for request/release notification and APIs `irq_domain_create_sim`, `devm_irq_domain_create_sim`, `irq_domain_create_sim_full`, `devm_irq_domain_create_sim_full`, and `irq_domain_remove_sim`.

## Control flow
Users create a firmware-node-backed simulated domain, optionally receive callbacks when simulated hwirqs are requested or released, use the IRQs through normal request/free paths, and remove the domain on teardown.

## State and persistence
State is runtime-only in the allocated irqdomain and simulator-private data pointer.

## Dependencies and integration points
It depends on the device model, fwnodes, and irqdomain core. It is useful for GPIO simulators, tests, and virtual devices.

## Risks and test signals
Risks include leaked domains, request/release callback ordering, simulated hwirq bounds, and devm cleanup mismatches. Tests should cover domain allocation failure, devm teardown, requesting every simulated IRQ, and remove while no IRQs are live.
