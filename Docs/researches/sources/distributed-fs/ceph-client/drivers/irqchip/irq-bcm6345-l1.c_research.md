# sources/distributed-fs/ceph-client/drivers/irqchip/irq-bcm6345-l1.c

## Purpose
Implements Broadcom BCM6345-style Level 1 interrupt controllers with per-CPU packed enable/status register windows and a single enable register per word.

## Important APIs, Types, and Functions
`struct bcm6345_l1_chip` tracks lock, word count, domain, CPU mask, and per-CPU data. `struct bcm6345_l1_cpu` stores register mapping, parent IRQ, and enable cache. Core functions are `bcm6345_l1_irq_handle()`, mask/unmask helpers, `bcm6345_l1_set_affinity()`, `bcm6345_l1_init_one()`, and `bcm6345_l1_of_init()`.

## Control Flow
Init iterates possible CPUs, maps each CPU register resource, establishes a parent chained handler, records valid CPU mappings, creates a linear domain sized by register words, and maps children as per-CPU IRQs. Chained dispatch reads pending AND enable for each word and dispatches set bits.

## State and Persistence
Per-CPU `enable_cache[]` mirrors hardware enable registers and is protected by a raw spinlock. Effective affinity chooses which CPU register window owns a child. Register offset helpers differ by CPU endianness.

## Dependencies and Integration Points
Depends on OF multi-resource/multi-parent IRQ descriptions, chained IRQ helpers, cpumask/SMP APIs, and irqdomain one-cell translation. It is a cascaded L1 controller under CPU-local parent IRQs.

## Risks and Test Signals
Risks include inconsistent word counts across CPU resources, endian offset mistakes, affinity migration losing enabled state, and incomplete cleanup on partial per-CPU init failures. Test signals are registration logs per CPU, correct affinity moves, interrupts delivered only on target CPU, and no spurious dispatch for unmapped bits.
