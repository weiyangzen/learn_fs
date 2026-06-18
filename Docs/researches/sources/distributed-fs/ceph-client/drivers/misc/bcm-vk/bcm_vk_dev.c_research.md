# sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk_dev.c

Purpose: implements Broadcom VK PCI device lifecycle, firmware boot loading, reset handling, notification work, mmap/ioctl entry points, panic reset, and module parameters.

Important APIs and functions: PCI lifecycle is `bcm_vk_probe`, `bcm_vk_remove`, and `bcm_vk_shutdown`. Userspace file operations include `bcm_vk_ioctl` and `bcm_vk_mmap` plus message operations declared elsewhere. Firmware helpers are `bcm_vk_load_image_by_type`, `bcm_vk_auto_load_all_images`, `bcm_vk_load_image`, and `bcm_vk_next_boot_image`. Reset and access control use `bcm_vk_reset`, `bcm_vk_trigger_reset`, `bcm_vk_blk_drv_access`, and `bcm_vk_reset_successful`. Notifications use `bcm_vk_notf_irqhandler`, `bcm_vk_wq_handler`, and `bcm_vk_handle_notf`.

Control flow: probe allocates state, enables PCI, requests regions, configures 64-bit DMA, allocates scratch DMA, allocates MSI-X vectors, maps BAR0/1/2, registers IRQs, allocates a device id, registers `/dev/bcm-vk.N`, creates a workqueue, initializes message queues, syncs card info, registers panic notifier, optionally initializes tty, triggers asynchronous autoload from BROM state, and starts heartbeat. Firmware loading pushes BOOT1 through BAR1 ITCM after SRAM open and BOOT2 through DMA chunks after DDR open, then waits for firmware ready, checks interface version, syncs queues, and reads card info. Reset drains queues, sends shutdown, kills users, rings reset doorbells, and validates firmware reset status.

State and persistence: `struct bcm_vk` owns persistent PCI, BAR, IRQ, misc, workqueue, DMA, message, alert, heartbeat, and card-info state. Firmware images and reset choices change card hardware state across driver operations.

Dependencies and integration points: depends on PCI/MSI-X, DMA coherent allocation, firmware loader, miscdevice, panic notifier, Broadcom VK UAPI, internal message/SG/tty/heartbeat code, and firmware files such as `vk*-boot1.bin` and `vk*-boot2.bin`.

Risks: this snapshot contains a malformed-looking comma after `misc_device->fops = &bcm_vk_fops`, which is a build risk if not source corruption. Firmware loading and reset paths are highly stateful and rely on BAR status bits, fixed timeouts, and correct image names. `bcm_vk_blk_drv_access` sends SIGKILL to client processes. Mmap exposes BAR2 MMIO to userspace with bounds checks. Error unwind mixes devm IRQs, PCI vectors, and manual frees and needs careful regression testing.

Test signals: PCI probe/remove/unwind injection, MSI-X allocation variants, firmware autoload/manual load for BOOT1/BOOT2, reset in BROM/BOOT1/BOOT2/ramdump states, `/dev/bcm-vk.N` ioctl and mmap tests, panic notifier behavior, heartbeat/notification alerts, and concurrent userspace access during reset.
