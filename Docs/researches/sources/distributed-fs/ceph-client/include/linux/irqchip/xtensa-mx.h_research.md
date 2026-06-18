# sources/distributed-fs/ceph-client/include/linux/irqchip/xtensa-mx.h

## Purpose
`xtensa-mx.h` declares legacy initialization for the Xtensa MX interrupt distributor.

## Important APIs, types, and functions
It forward-declares `struct device_node` and declares `xtensa_mx_init_legacy(struct device_node *interrupt_parent)`.

## Control flow
Legacy Xtensa platform code calls the initializer with the parent interrupt-controller node to register MX distribution behavior.

## State and persistence
State is owned by the Xtensa MX irqchip implementation and generic IRQ domains/descriptors.

## Dependencies and integration points
It integrates Xtensa legacy interrupt setup with firmware nodes and parent controllers.

## Risks and test signals
Risks include missing parent node, wrong legacy ordering, and IRQ domain mismatches. Tests should boot Xtensa MX configurations and verify child interrupt delivery.
