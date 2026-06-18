# sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk.h

Purpose: central internal header for the Broadcom VK PCI accelerator driver, defining register offsets, boot status bits, BAR layout, alert constants, device state, and cross-module functions.

Important APIs and types: register macros cover boot image pushing, firmware status, card telemetry, error logs, doorbells, BAR1 message-queue metadata, DMA/scratch addresses, authentication fields, and reset values. `struct bcm_vk` is the main per-device state with PCI device, BAR mappings, miscdevice, tty state, kref, message contexts, workqueues, DMA scratch area, panic notifier, heartbeat, alert state, peer log, and process monitor data. Inline helpers `vkread32`, `vkwrite32`, `vkread8`, and `vkwrite8` wrap MMIO access.

Control flow: `bcm_vk_dev.c` owns PCI lifecycle and firmware/reset ioctls; `bcm_vk_msg.c`, `bcm_vk_sg.c`, and optional `bcm_vk_tty.c` use the shared structures and prototypes to implement userspace messaging, DMA, and tty channels.

State and persistence: state is per PCI device and persists from probe until the last kref is released. Hardware state spans BAR registers, firmware boot phases, message queues, peer logs, and card telemetry.

Dependencies and integration points: depends on PCI, miscdevice, kref, poll, tty, firmware, UAPI `linux/misc/bcm_vk.h`, and internal `bcm_vk_msg.h`.

Risks: the header exposes a large shared mutable structure across modules, so locking discipline is distributed. Register offsets and masks are firmware ABI and must remain synchronized with card firmware. Optional tty stubs must match real function semantics.

Test signals: build all modules using this header, firmware ABI compatibility tests, BAR register smoke tests, message queue marker validation, and lockdep coverage for shared state.
