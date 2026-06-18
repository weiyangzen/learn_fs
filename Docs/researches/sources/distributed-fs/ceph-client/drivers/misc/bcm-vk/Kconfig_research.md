# sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/Kconfig

Purpose: declares configuration for the Broadcom VK accelerator PCI host driver and optional tty console support.

Important APIs and symbols: `BCM_VK` is a tristate depending on `PCI_MSI`. `BCM_VK_TTY` is a bool depending on `TTY` and `BCM_VK`, enabling tty ports named like `/dev/bcm-vk.x_ttyVKy`.

Control flow: selecting `BCM_VK` builds the PCI misc driver, message queue, and scatter-gather support. Selecting `BCM_VK_TTY` also builds tty support and enables IRQ allocation/structures for VK tty channels.

State and persistence: no runtime state. The selected config determines whether userspace sees only `/dev/bcm-vk.N` or also tty devices.

Dependencies and integration points: integrates with PCI MSI/MSI-X, miscdevice userspace access, optional tty core, and Broadcom VK accelerator firmware loading.

Risks: help text describes broad accelerator use cases but not firmware file requirements or auto-load behavior. `BCM_VK_TTY` is bool rather than tristate, so it follows the base driver's build mode.

Test signals: menu visibility, builds with and without tty, PCI probe on MSI-X-capable systems, and device-node creation checks.
