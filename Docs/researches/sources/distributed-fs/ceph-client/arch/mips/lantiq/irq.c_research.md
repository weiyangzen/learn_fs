# sources/distributed-fs/ceph-client/arch/mips/lantiq/irq.c

Purpose: implements Lantiq ICU/EIU interrupt-controller support and hooks it into irqchip/irqdomain and MIPS CPU interrupt handling.

Important APIs/functions: `ltq_eiu_get_irq`, `ltq_enable_irq`, `ltq_disable_irq`, `ltq_mask_and_ack_irq`, `ltq_eiu_settype`, `ltq_startup_eiu_irq`, `ltq_shutdown_eiu_irq`, `ltq_hw_irq_handler`, `icu_map`, `icu_of_init`, `get_c0_perfcount_int`, `get_c0_compare_int`, and `arch_init_irq`.

Control flow: `IRQCHIP_DECLARE` invokes `icu_of_init()` for `lantiq,icu`; it maps per-CPU ICU resources, disables and clears interrupts, initializes MIPS CPU IRQs, installs chained handlers for CPU IRQs 2.., creates a linear irqdomain, maps perfcount IRQ, and optionally maps EIU resources from DT. Chained handling reads ICU pending bits, applies silicon-bug `__fls()` filtering, translates to hwirq, and calls `generic_handle_domain_irq()`.

State and persistence: global state includes ICU/EIU MMIO bases, irqdomain pointer, EIU hwirq list, perfcount mapping, and spinlocks. Hardware interrupt enable, type, pending, and resend registers hold runtime state.

Dependencies and integration: depends on OF irq/address APIs, generic irqdomain, MIPS CPU IRQ controller, Lantiq EBU ack registers, and SMP affinity masks.

Risks: incorrect DT EIU lists break external IRQs. The handler trusts only the highest pending bit due to silicon behavior. EBU IRQs need special ack to avoid deadlock. Affinity fallback during hotplug can route to the current CPU.

Test signals: interrupt storm tests, GPIO/EIU edge/level type tests, SMP affinity changes, perf counter IRQ mapping, EBU device IRQ acking, and DT probe failures.
