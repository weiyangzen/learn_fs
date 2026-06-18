# sources/distributed-fs/ceph-client/include/linux/irqchip/xtensa-pic.h

## Purpose
`xtensa-pic.h` declares legacy initialization for the built-in Xtensa programmable interrupt controller.

## Important APIs, types, and functions
It forward-declares `struct device_node` and declares `xtensa_pic_init_legacy(struct device_node *interrupt_parent)`.

## Control flow
Xtensa platform setup invokes the initializer to register the built-in PIC against an optional parent node before normal IRQ handling begins.

## State and persistence
Runtime state is in the PIC implementation and generic IRQ descriptors/domains.

## Dependencies and integration points
It integrates Xtensa architecture interrupt setup with generic irqchip initialization.

## Risks and test signals
Risks include wrong parent relationship, legacy init running too late, and interrupt number mapping errors. Tests should cover Xtensa PIC boot, timer IRQ delivery, and nested/parented configurations.
