# sources/distributed-fs/ceph-client/drivers/irqchip/irq-stm32mp-exti.c

## Purpose
Implements STM32MP EXTI as a hierarchical interrupt controller in front of a parent GIC or interrupt router. It supports direct parent-forwarded interrupts, locally latched EXTI events, secure/reserved event detection, optional hwspinlock coordination, and wake state across system sleep.

## Important APIs, Types, And Functions
`stm32mp_exti_bank` describes offsets including rising/falling pending and security config. `stm32mp_exti_host_data` owns MMIO base, drvdata, optional hwspinlock, and bank data. Two irq chips are used: `stm32mp_exti_chip` for locally managed events and `stm32mp_exti_chip_direct` for direct parent-backed events. Allocation is handled by `stm32mp_exti_domain_alloc()`.

## Control Flow
Probe gets optional hwspinlock, match data, bank data, MMIO, initializes bank state, checks secure/RIF ownership, finds the parent domain, and creates a hierarchy. Allocation validates hwirq, rejects secure events, chooses local or direct chip based on trigger routing, then either parses `interrupts-extended` or uses static descriptor arrays to allocate the parent IRQ. Runtime mask/unmask updates EXTI IMR and parent state; EOI clears rising/falling pending and then EOIs the parent when present.

## State And Persistence
Per-bank state tracks mask cache, wake-active mask, saved RTSR/FTSR, secure event reservation, and a raw lock. Suspend programs IMR to wake-active only and resume restores trigger and mask caches. Optional hwspinlock protects trigger programming shared with another processor.

## Dependencies And Integration Points
Depends on OF platform probing, GIC binding constants, hierarchical irqdomains, hwspinlock framework, noirq PM ops, and compatible `st,stm32mp1-exti` or `st,stm32mp13-exti`.

## Risks
Static descriptor arrays must match SoC interrupt wiring unless DT supplies `interrupts-extended`. Secure/RIF detection can make events unavailable with `-EPERM`. Trigger reconfiguration in atomic context may fail if the hwspinlock cannot be acquired. Direct versus local chip selection depends on hardware routing bits.

## Test Signals
Probe STM32MP1 and STM32MP13, verify secure events are rejected, exercise direct and local lines, all supported edge types, software retrigger, wake-only suspend/resume, and systems with and without hwspinlock. DT tests should validate both descriptor-array and `interrupts-extended` paths.
