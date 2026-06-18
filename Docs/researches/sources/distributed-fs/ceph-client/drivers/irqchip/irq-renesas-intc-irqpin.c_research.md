<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-intc-irqpin.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-intc-irqpin.c

## Purpose
`irq-renesas-intc-irqpin.c` drives Renesas INTC external IRQ pin blocks. It turns one to eight external pins into Linux IRQs, handling sense configuration, priority masking, source clearing, optional shared parent IRQs, wake propagation, and runtime PM.

## Important APIs, Types, and Functions
`struct intc_irqpin_priv` contains register descriptors, per-line IRQ metadata, sense width, platform device, irqchip, domain, wakeup counter, and shared IRQ mask. `struct intc_irqpin_iomem` abstracts 8-bit versus 32-bit access. Core helpers include `intc_irqpin_read_modify_write()`, `intc_irqpin_mask_unmask_prio()`, `intc_irqpin_set_sense()`, enable/disable variants, `intc_irqpin_irq_set_type()`, `intc_irqpin_irq_set_wake()`, per-line and shared handlers, domain map, probe/remove, and suspend.

## Control Flow
Probe enables runtime PM, gathers mandatory register resources and up to eight IRQ resources, maps each register with width-specific accessors, optionally selects individual IRQ mode via IRLM, masks priorities, clears pending source bits, detects whether all lines share one parent IRQ, selects enable/disable strategy, creates a simple domain, and requests either one shared parent IRQ or one parent per line. Runtime demux checks source status, clears the active bit, and invokes the domain IRQ.

## State and Persistence
Software state is per platform instance and devm-managed except the irqdomain. `shared_irq_mask` tracks disabled children when one parent line is shared. `wakeup_path` counts wake-enabled child IRQs and marks the device as a wakeup path during suspend. Register state is not cached across power loss.

## Dependencies and Integration Points
It integrates with platform resources, OF compatibles for several Renesas variants, runtime PM, irqdomain two-cell translation, parent IRQ request APIs, lockdep classing, and `postcore_initcall()` registration.

## Risks and Edge Cases
Mandatory register resources must be in the expected order and size. Shared source registers and priority/sense RMW paths need locking, but source/mask/clear registers assume single-driver ownership. `control-parent` force-masks parent chips directly and assumes 1:1 non-shared parent mapping. Wake counter imbalance would misreport wake paths.

## Test Signals
Test 8-bit and 32-bit register variants, one to eight lines, shared and non-shared parents, `control-parent`, all supported trigger senses, wake enable/disable and suspend marking, IRLM-capable SoCs, and pending-source clear behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-intc-irqpin.c -->
