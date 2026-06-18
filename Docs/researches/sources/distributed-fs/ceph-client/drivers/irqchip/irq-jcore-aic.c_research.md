<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-jcore-aic.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-jcore-aic.c

## Purpose
Implements the J-Core SoC AIC1/AIC2 local interrupt controller using a legacy irqdomain and a minimal irqchip.

## Important APIs, Types, And Functions
The file uses a single static `struct irq_chip jcore_aic`. `aic_irq_of_init()` allocates descriptors and creates a legacy domain. `jcore_aic_irqdomain_map()` installs `handle_jcore_irq()`, which chooses `handle_percpu_devid_irq()` for per-CPU requested IRQs and `handle_simple_irq()` otherwise. `noop()` satisfies mask/unmask requirements.

## Control Flow
OF init chooses a minimum hwirq range based on AIC1 or AIC2. AIC1 additionally maps per-CPU register resources and writes all priorities enabled to `JCORE_AIC1_INTPRI_REG`. It then allocates descriptors and creates a legacy domain covering the valid hwirq range.

## State And Persistence
There is no private state object. Hardware state is limited to AIC1 priority initialization. The irqchip has no real mask/unmask because masking is CPU-global rather than per-source.

## Dependencies And Integration Points
It depends on OF mapping, CPU iteration, legacy irqdomains, and compatibles `jcore,aic1` and `jcore,aic2`. It integrates with request-time IRQF_PERCPU state rather than knowing per-CPU sources at mapping time.

## Risks
No per-source masking means Linux cannot disable individual AIC sources through this chip. AIC1 mapping assumes one MMIO resource per present CPU. Legacy descriptor allocation must not collide with platform IRQ numbering.

## Test Signals
Test AIC1 priority programming for all present CPUs, AIC2 descriptor/domain creation, per-CPU and non-per-CPU request handling, descriptor range boundaries at 16/64/127, and missing per-CPU MMIO resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-jcore-aic.c -->
