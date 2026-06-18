# sources/distributed-fs/ceph-client/drivers/irqchip/irq-xtensa-mx.c

## Purpose
Implements the Xtensa MX interrupt distributor, extending the built-in Xtensa interrupt controller with external interrupt routing, per-CPU mask caching, IPIs, and affinity programming.

## Important APIs, Types, And Functions
Per-CPU `cached_irq_mask` mirrors enabled local interrupt bits. `xtensa_mx_irq_map()` treats hardware IRQs 0-1 as per-CPU IPIs and delegates others to common Xtensa mapping. Mask/unmask either updates external MX enable registers (`MIENG`/`MIENGSET`) or the local `intenable` special register. Affinity writes `MIROUT()`.

## Control Flow
Legacy or DT init creates an irqdomain using MX ops, sets it as default, initializes this CPU's external interrupt mask, enables external edge/level bits, and routes all external interrupts to CPU0. Runtime mask/unmask checks whether an interrupt is an external MX line or a local core line, then updates the appropriate register. Retrigger only supports software interrupt types.

## State And Persistence
State is per-CPU cached mask plus MX routing registers. There is no explicit PM cache. Secondary CPU initialization re-establishes local external interrupt enable state.

## Dependencies And Integration Points
Depends on Xtensa architecture registers/helpers, common `xtensa_irq_map()` and `xtensa_irq_domain_xlate()`, SMP affinity, and compatible `cdns,xtensa-mx`.

## Risks
External interrupt numbering offsets are subtle: one/two-cell DT translation maps external specifiers with `HW_IRQ_EXTERN_BASE`. Affinity uses `cpumask_any_and()` without explicit no-CPU error handling. Local cached masks must remain in sync with `intenable`.

## Test Signals
Boot DT and legacy paths, verify IPI hwirqs 0-1, external interrupt mask/unmask through MX registers, local interrupt mask cache, affinity routing to online CPUs, secondary CPU init, and software retrigger validation.
