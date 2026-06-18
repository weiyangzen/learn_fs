# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-sm501.c

## Purpose

`ohci-sm501.c` is OHCI glue for the SM501 multifunction device. It uses SM501 local memory for DMA, powers and unmasks the USB host block, and integrates the generic OHCI core with SM501 platform resources.

## Important APIs, Types, and Functions

Important functions are `ohci_sm501_init()`, `ohci_sm501_start()`, `ohci_hcd_sm501_drv_probe()`, `ohci_hcd_sm501_drv_remove()`, `ohci_sm501_suspend()`, and `ohci_sm501_resume()`. It defines `ohci_sm501_hc_driver` and `ohci_hcd_sm501_driver`.

## Control Flow

Probe gets IRQ, reserves the SM501 local-memory resource and OHCI register resource, creates the HCD, maps registers, initializes core state, sets up `usb_hcd_setup_local_mem()` so USB buffers are copied into SM501-local DMA memory when needed, adds the HCD, enables wakeup, powers the SM501 USB host gate, and unmasks the SM501 interrupt. Remove unregisters the HCD, unmaps/releases resources, masks the interrupt, and powers the USB host off. PM suspend calls `ohci_suspend()` and powers off; resume powers on and calls `ohci_resume()`.

## State and Persistence Behavior

State is in platform resources, local-memory pool, HCD/OHCI structures, SM501 power gate, and SM501 IRQ mask. Local memory contents and register state are runtime-only and reset by remove/suspend.

## Dependencies and Integration Points

It depends on SM501 MFD APIs, SM501 register definitions, platform resources with separate register and local-memory windows, local-memory HCD support, and OHCI core internals included by the main module.

## Risks and Test Signals

Risks include resource index assumptions, enabling power after `usb_add_hcd()` rather than before, shared IRQ masking order, local-memory offset calculations, and PM without reinitializing all SM501-specific state. Test signals include SM501 probe with two MEM resources, local-memory DMA transfers, interrupt delivery after unmask, suspend/resume enumeration, and cleanup after `usb_add_hcd()` failure.
