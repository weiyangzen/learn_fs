# sources/distributed-fs/ceph-client/drivers/irqchip/irq-atmel-aic-common.h

## Purpose
Declares the shared AIC helper interface consumed by the AT91 AIC and AIC5 drivers.

## Important APIs, Types, and Functions
The header exposes trigger encoding (`aic_common_set_type()`), priority encoding (`aic_common_set_priority()`), DT interrupt translation (`aic_common_irq_domain_xlate()`), common OF/generic-chip setup (`aic_common_of_init()`), and RTC/RTT fixup hooks.

## Control Flow
There is no runtime control flow in the header. It defines the contract that concrete AIC drivers follow: call common OF init, specialize chip registers/callbacks, then install their root IRQ handler.

## State and Persistence
No state is declared here. State lives in the common C file and in each concrete driver through irqdomains, generic chips, and MMIO state.

## Dependencies and Integration Points
Requires Linux irqdomain, OF device-node, and IRQ type definitions from included translation units. It couples the AIC and AIC5 drivers to a shared three-cell DT interrupt format and common SoC fixup behavior.

## Risks and Test Signals
Risks are ABI-style: changing prototypes or semantics affects both AIC implementations. Test signals are successful builds of both drivers and consistent behavior for trigger, priority, and fixup paths.
