# sources/distributed-fs/ceph-client/drivers/irqchip/irq-econet-en751221.c

## Purpose
Implements the EcoNet EN751221 interrupt controller for MIPS 34Kc MT SMP systems, including per-VPE masking through DT-defined shadow interrupts.

## Important APIs, Types, and Functions
Global `econet_intc` stores MMIO and `interrupt_shadows[]` classifications. `get_shadow_interrupts()` parses `econet,shadow-interrupts`. `econet_chmask()` applies real versus shadow mask routing. `econet_intc_from_parent()` is the chained handler, and `econet_intc_map()` selects level versus percpu-devid handlers.

## Control Flow
Init parses shadow pairs, maps the parent IRQ and MMIO resource, requests/remaps memory, masks all sources, creates a 40-entry one-cell domain, and chains to the parent. Parent dispatch reads two pending registers and handles all set bits. Mapping rejects shadow-only hwirqs and marks real per-CPU interrupts with `handle_percpu_devid_irq`.

## State and Persistence
Persistent state is the `interrupt_shadows[]` routing table and hardware mask registers. A raw spinlock serializes read-modify-write register updates. Per-CPU behavior is encoded by using the shadow hwirq when running on VPE1.

## Dependencies and Integration Points
Depends on OF, chained IRQ helpers, MIPS SMP `smp_processor_id()`, and one-cell irqdomain translation. It cascades under a parent CPU interrupt and provides percpu semantics without hardware multicast.

## Risks and Test Signals
Risks include off-by-one validation (`shadow > IRQ_COUNT`), assumptions of at most two VPEs, direct shadow manipulation warnings, and no masking of pending bits in handler. Test signals include rejection of shadow hwirqs, correct per-VPE masking, valid shadow DT parsing logs, and no spurious parent IRQs when pending registers are zero.
