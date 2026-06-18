# sources/distributed-fs/ceph-client/drivers/irqchip/irq-atmel-aic-common.c

## Purpose
Provides shared support for Atmel AT91 AIC and AIC5 interrupt controllers. It centralizes trigger/priority encoding, generic-chip domain allocation, external interrupt policy, and SoC-specific RTC/RTT interrupt fixups.

## Important APIs, Types, and Functions
`struct aic_chip_data` stores per-generic-chip external IRQ masks. Exported internal helpers include `aic_common_set_type()`, `aic_common_set_priority()`, `aic_common_irq_domain_xlate()`, `aic_common_of_init()`, `aic_common_rtc_irq_fixup()`, and `aic_common_rtt_irq_fixup()`. `aic_common_shutdown()` delegates shutdown to the chip mask callback.

## Control Flow
`aic_common_of_init()` maps the controller, allocates per-chip private data, creates a linear irqdomain sized to 32-entry chip chunks, allocates generic chips with `handle_fasteoi_irq`, initializes generic-chip methods and wake policy, parses `atmel,external-irqs`, and invokes machine fixups selected by `of_machine_get_match_data()`.

## State and Persistence
Persistent state includes mapped controller registers, allocated `aic_chip_data` array, generic-chip `mask_cache`/wake state, and external IRQ bitmasks. RTC/RTT fixups directly clear peripheral interrupt enables to avoid stale interrupt state before the AIC takes over.

## Dependencies and Integration Points
This file is used by `irq-atmel-aic.c` and `irq-atmel-aic5.c`. It depends on generic irqchip infrastructure, OF matching, MMIO, and Atmel DT bindings using three interrupt cells: hwirq, trigger type, and priority.

## Risks and Test Signals
Risks include invalid priorities, unsupported low/falling types on non-external IRQs, memory leaks on partial init failures, and missing peripheral fixups causing boot-time interrupt storms. Test signals are successful AIC/AIC5 domain creation, correct DT xlate rejection for bad cells, wake mask behavior across suspend, and quiet boot on affected RTC/RTT SoCs.
