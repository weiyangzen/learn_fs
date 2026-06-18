# sources/distributed-fs/ceph-client/drivers/gpio/gpio-xgene-sb.c

## Purpose
Implements the AppliedMicro X-Gene standby GPIO controller. It exposes a small MMIO GPIO block with a hierarchical IRQ domain for a configurable subset of pins and supports OF and ACPI-described systems.

## Important APIs, Types, And Functions
- `struct xgene_gpio_sb` stores a generic GPIO chip, register base, IRQ domain, IRQ-capable pin range, and parent IRQ base.
- `xgene_gpio_set_bit` performs read-modify-write bit updates via generic GPIO register helpers.
- `xgene_gpio_sb_irq_set_type`, `xgene_gpio_sb_irq_mask`, and `xgene_gpio_sb_irq_unmask` implement child irqchip operations.
- `xgene_gpio_sb_to_irq` builds an IRQ fwspec for GPIO-to-IRQ mapping.
- Domain callbacks `xgene_gpio_sb_domain_translate`, `xgene_gpio_sb_domain_alloc`, `xgene_gpio_sb_domain_activate`, and `xgene_gpio_sb_domain_deactivate` bridge child hwirqs to parent interrupts and lock GPIOs as IRQs.
- `xgene_gpio_sb_probe` initializes generic GPIO operations, property defaults, hierarchical domain, and ACPI GPIO event interrupts.

## Control Flow
Probe maps registers, obtains the platform IRQ's parent domain and hwirq as the parent base, initializes a generic chip for input/output/direction registers, reads optional `apm,irq-start`, `apm,nr-irqs`, and `apm,nr-gpios`, creates a hierarchical domain, registers the gpiochip, and requests ACPI GPIO event interrupts. GPIO-to-IRQ mapping is allowed only in the configured IRQ-capable range. Domain allocation maps child hwirqs to parent fwspecs with OF GIC or fwnode irqchip formatting.

## State And Persistence
Hardware registers store GPIO output, output enable, input, interrupt level, and select bits. Software state stores the IRQ-capable window and hierarchical IRQ domain. Remove frees ACPI interrupts and removes the domain.

## Dependencies And Integration Points
Depends on gpiolib generic MMIO, irqdomain hierarchy APIs, parent IRQ chip support, ACPI GPIO event helpers from `gpiolib-acpi.h`, OF/ACPI matching, and platform properties.

## Risks And Edge Cases
`xgene_gpio_sb_to_irq` uses `gpio > HWIRQ_TO_GPIO(priv, priv->nirq)`, which appears off by one because valid hwirq values are 0 to `nirq - 1`. IRQ type support collapses both-edge child requests to parent rising-edge and all non-both requests to parent level-high, relying on local level selection. Parent fwspec construction differs for OF and fwnode irqchips and can fail on unexpected parent domains. GPIO select bits use `gpio * 2`, making bit indexing important.

## Test Signals
Check default and property-specified IRQ windows, GPIO-to-IRQ boundaries, OF and ACPI matches, hierarchical allocation parent fwspecs, activation/deactivation GPIO lock behavior, interrupt type propagation for edge/level cases, and ACPI event request/free on probe/remove.
