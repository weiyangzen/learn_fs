# sources/distributed-fs/ceph-client/drivers/irqchip/irq-apple-aic.c

Purpose: Implements Apple Silicon AIC/AIC2/AIC3 interrupt controllers, including hardware IRQs, FIQ sources, virtualized IPIs through `ipi_mux`, timer/PMU FIQ handling, affinity hints, and KVM VGIC maintenance integration.

Important APIs/types/functions: `struct aic_irq_chip`, `struct aic_info`, `aic_handle_irq()`, `aic_handle_fiq()`, `aic_irq_mask()/unmask()/eoi()`, FIQ mask/unmask/eoi helpers, `aic_irq_domain_translate()`, `aic_irq_domain_alloc()`, `aic_ipi_send_fast()`, `aic_handle_ipi()`, `aic_init_cpu()`, `build_fiq_affinity()`, and `aic_of_ic_init()`.

Control flow: OF init maps controller registers, selects version capabilities from compatible data, derives register layout/die stride, creates a tree IRQ domain, initializes `ipi_mux`, parses optional FIQ affinity children, installs IRQ and FIQ exception handlers, masks/clears all IRQs across dies, sets default targets for AICv1, enables AIC2/3 config, registers CPU hotplug initialization, optionally maps the VGIC maintenance FIQ, and publishes VGIC info. IRQ handling reads event registers until empty, dispatching IRQ events or IPI events; FIQ handling probes fast IPI, timer, PMU, and uncore PMU sources directly from sysregs.

State and persistence: Global `aic_irqc`, per-CPU FIQ unmasked bits, static keys for fast/local IPIs, per-FIQ affinity masks, register offsets, die/IRQ counts, and hardware mask/software-trigger state persist for the boot lifetime.

Dependencies/integration: Uses ARM64 sysregs, Apple PMU definitions, irqdomain hierarchy, `ipi_mux`, CPU hotplug, OF bindings, KVM VGIC info, static branches, and ARM exception hooks.

Risks and test signals: Test AICv1/v2/v3 register layouts, EL1 versus EL2 timer remapping, fast/local IPI selection, FIQ storms from unsupported PMU/uncore sources, multi-die IRQ encoding, affinity parsing, VGIC maintenance disable path, and CPU hotplug reinitialization.
