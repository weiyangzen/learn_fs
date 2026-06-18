# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/snps_udc_plat.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/snps_udc_plat.c` is the platform-device wrapper for the Synopsys UDC core. It allocates the UDC instance, maps MMIO resources, acquires IRQ and PHY resources from device tree, optionally tracks USB cable/device-mode state through extcon, creates DMA pools, registers the common core with the gadget framework, and handles remove and system sleep. The source was read as a complete 325-line file for this report.

## Important APIs, Types, and Functions

The main platform callbacks are `udc_plat_probe`, `udc_plat_remove`, `udc_plat_suspend`, and `udc_plat_resume`. The platform driver is `udc_plat_driver`, matched by `of_udc_match` entries `brcm,ns2-udc`, `brcm,cygnus-udc`, and `brcm,iproc-udc`. Role and cable helpers are `start_udc`, `stop_udc`, `udc_drd_work`, and `usbd_connect_notify`.

The file calls core functions declared by `amd5536udc.h`: `udc_probe`, `udc_remove`, `udc_irq`, `udc_basic_init`, `udc_enable_dev_setup_interrupts`, `udc_mask_unused_interrupts`, `empty_req_queue`, `init_dma_pools`, and `free_dma_pools`.

## Control Flow

Probe allocates `struct udc` with devres, initializes the spinlock, maps resource 0, derives CSR/device/endpoint/FIFO register windows from the mapped base, parses the IRQ, obtains and powers on the PHY, and optionally registers an extcon notifier for `EXTCON_USB`. If USB is already present, `conn_type` is initialized so delayed work can bring the controller up. When `use_dma` is enabled, DMA pools are initialized before requesting the shared IRQ and calling `udc_probe`.

Extcon notification stores the new connection state in `udc->conn_type` and schedules `udc_drd_work`. The work item calls `start_udc` on device connection, enabling setup interrupts, reinitializing the core, and marking connected. It calls `stop_udc` on disconnect, flushing the RX FIFO, masking interrupts, invoking the gadget driver's `disconnect` callback outside the spinlock, and emptying all endpoint queues.

Remove unregisters the gadget UDC, requires the gadget driver to already be detached, frees DMA pools, calls core remove, powers off/exits the PHY, unregisters extcon, and clears drvdata. Suspend forces `stop_udc`, powers down the PHY, and resume reinitializes and powers the PHY then restarts the UDC if extcon says USB is connected.

## State and Persistence Behavior

The platform file owns platform lifetime state inside `struct udc`: mapped register bases, physical address, IRQ, PHY, extcon device and notifier, delayed DRD work, connection type, and the core's gadget state. It has no file-backed persistence. Hardware state persists only while the device is powered and the PHY is active. Devres owns memory/MMIO/IRQ allocations, while DMA pools and PHY power are explicitly unwound.

## Dependencies and Integration Points

Dependencies include platform bus APIs, Open Firmware address/IRQ parsing, PHY framework, extcon, DMA pools, Linux interrupt handling, and module platform-driver registration. The local integration point is the common Synopsys core in `snps_udc_core.c`; this file supplies hardware resources and lifecycle calls while the core supplies gadget behavior and interrupt handling.

## Risks and Edge Cases

The extcon path has asymmetry risks: some error and remove paths call `extcon_unregister_notifier` based only on `udc->edev`, so no-extcon configurations and probe-defer cleanup need careful validation. Suspend/resume calls `extcon_get_state(udc->edev, EXTCON_USB)` unconditionally under `CONFIG_PM_SLEEP`, which is risky if no extcon property exists. `stop_udc` invokes gadget callbacks while coordinating spinlock-protected queue state, so callback reentrancy and disconnect timing matter. Probe error labels must keep PHY, DMA, and extcon unwind ordering correct.

## Test Signals

Build with platform UDC and Broadcom device-tree compatibles enabled; boot/probe on `brcm,ns2-udc`, `brcm,cygnus-udc`, or `brcm,iproc-udc`; verify IRQ registration and `udc_probe` success; plug/unplug through extcon and confirm start/stop transitions; bind a gadget function and verify disconnect queue draining; test no-extcon device-tree configurations, probe deferral from extcon/PHY, and system suspend/resume with and without a connected cable.
