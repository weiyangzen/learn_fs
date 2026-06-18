# sources/distributed-fs/ceph-client/drivers/misc/mchp_pci1xxxx/mchp_pci1xxxx_gpio.c

## Purpose
`mchp_pci1xxxx_gpio.c` implements the PCI1xxxx GPIO auxiliary driver. It exposes 93 GPIOs, pin configuration, IRQ mapping, wake masks, and suspend/resume register programming over MMIO.

## Important APIs, Types, and Functions
Main state is `struct pci1xxxx_gpio`. GPIO callbacks are direction/get/set/set_config helpers. IRQ callbacks are `pci1xxxx_gpio_irq_ack()`, mask/unmask, `pci1xxxx_gpio_set_type()`, `pci1xxxx_gpio_set_wake()`, and `pci1xxxx_gpio_irq_handler()`. Probe/setup are `pci1xxxx_gpio_probe()` and `pci1xxxx_gpio_setup()`. PM callbacks are suspend/resume.

## Control Flow
Probe maps BAR0, initializes locks, writes a global GPIO config value, requests the parent IRQ as a threaded IRQ, configures `gpio_chip` and immutable `irq_chip`, reads PCI revision, stores driver data, and registers the gpiochip. GPIO operations do locked read-modify-write operations on banked registers. The IRQ handler enables global interrupt processing, scans three banks, acknowledges set bits, maps each GPIO hwirq, and calls `generic_handle_irq()`.

## State and Persistence
Persistent runtime state includes MMIO base, GPIO chip, two locks, device revision, IRQ base field, and `gpio_wake_mask[3]`. Register state persists in device hardware across callbacks and is altered during suspend/resume.

## Dependencies and Integration Points
Depends on gpiolib, gpiolib IRQ chip helpers, PCI config access through the parent device, auxiliary bus matching, IRQ core, and pinconf parameters.

## Risks
Register access must be serialized; most paths use `priv->lock`, but `set_type()` does not take it. `wa_lock` is used without visible initialization in probe. The IRQ handler assumes status width per bank and valid IRQ mappings. PM wake mask polarity must match hardware expectations.

## Test Signals
Signals are GPIO line direction/value tests, pinconf pull/open-drain tests, edge and level IRQ delivery across all banks, wake-from-D3 behavior, suspend/resume register restoration, and race testing under concurrent GPIO and IRQ operations.
