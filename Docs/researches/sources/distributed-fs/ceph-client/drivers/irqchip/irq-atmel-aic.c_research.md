# sources/distributed-fs/ceph-client/drivers/irqchip/irq-atmel-aic.c

## Purpose
Implements the original 32-line Atmel AT91 Advanced Interrupt Controller as a root interrupt controller for ARM AT91 systems.

## Important APIs, Types, and Functions
`aic_of_init()` is registered for `atmel,at91rm9200-aic`. `aic_handle()` is the root IRQ entry. `aic_retrigger()`, `aic_set_type()`, PM callbacks, `aic_hw_init()`, and `aic_irq_domain_xlate()` specialize common AIC services. SoC fixup functions connect machine compatibles to RTC/RTT cleanup.

## Control Flow
Init rejects duplicate domains, calls `aic_common_of_init()` for a 32-line domain, fills generic-chip register offsets and callbacks, initializes hardware, then installs `set_handle_irq(aic_handle)`. The handler reads IVR/ISR; no active IRQ causes an EOI write, otherwise the domain IRQ matching IVR is dispatched.

## State and Persistence
Global `aic_domain` anchors the controller. Generic-chip mask and wake caches persist across callbacks. Hardware state includes SMR priority/type fields, SVR vector values, enable/disable/clear bits, and EOI state. PM callbacks save runtime mask/wake policy into hardware during suspend/resume or shutdown.

## Dependencies and Integration Points
Depends on `irq-atmel-aic-common`, ARM exception IRQ entry, OF irqchip declaration, and generic irqchip. The DT binding uses hwirq/type/priority cells and machine compatible strings for fixups.

## Risks and Test Signals
Risks include incorrect priority writes during xlate, unsupported trigger types, missed EOI causing locked nIRQ, and stale RTC/RTT sources. Test signals are clean boot with root handler installed, active IRQs reflected in `/proc/interrupts`, suspend/resume wake filtering, and no spurious AIC lockout.
