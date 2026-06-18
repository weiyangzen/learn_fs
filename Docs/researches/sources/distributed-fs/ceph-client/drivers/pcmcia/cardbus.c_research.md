# sources/distributed-fs/ceph-client/drivers/pcmcia/cardbus.c

Purpose: Bridges CardBus insertion/removal into the Linux PCI core. It scans devices below a CardBus bridge, sizes and assigns resources, sets shared IRQ/cacheline settings, invokes socket-specific bridge tuning, and removes downstream devices on eject.

Important APIs and functions: Public internal functions are `cb_alloc()` and `cb_free()`, declared through `cs_internal.h`. `cardbus_config_irq_and_cls()` recursively sets PCI interrupt lines and cacheline sizes for downstream devices.

Control flow: On CardBus insert, `cb_alloc()` locks PCI rescan/remove, scans slot 0, scans any bridges in two passes, sizes and assigns bridge resources, configures IRQ/cacheline values, calls optional `s->tune_bridge()`, adds devices to the PCI bus, and unlocks. On eject, `cb_free()` locates the subordinate bus of `s->cb_dev` and removes every child PCI device under the same PCI lock.

State and persistence: This file does not own long-lived state. It mutates PCI core bus/device/resource state and uses socket fields `cb_dev`, `pci_irq`, `functions`, and `tune_bridge`.

Dependencies and integration points: Depends on `CONFIG_CARDBUS`, Linux PCI bus scanning/resource APIs, and the PCMCIA socket core's CardBus state machine in `cs.c`.

Risks: CardBus has only one socket IRQ in this model, so all downstream devices are forced to the same IRQ line. Resource sizing/assignment is delegated to PCI and can fail if bridge windows are constrained. Removal must hold PCI locks to avoid racing driver bind/unbind or rescan paths.

Test signals: Insert a CardBus card, observe PCI device creation, IRQ line programming, cacheline setup, driver binding, bridge resource assignment, and clean removal on eject/resume.
