<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-fsl-usb.h -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-fsl-usb.h

## Purpose

`phy-fsl-usb.h` defines the Freescale USB dual-role controller register map, OTGSC/PORTSC/USBCMD bitfields, OTG timing constants, software timer structure, controller MMIO layout, and `struct fsl_otg` state used by `phy-fsl-usb.c`.

## Important APIs, Types, and Functions

Important macros cover USBCMD, USBSTS, USBINTR, DEVICEADDR, PORTSC, OTGSC, USBMODE, control register fields, OTG interrupt status/enable masks, and OTG timing constants such as `TA_WAIT_VRISE`, `TA_WAIT_BCON`, `TB_DATA_PLS`, and `TB_SRP_FAIL`. `struct usb_dr_mmap` models the memory-mapped dual-role controller. `struct fsl_otg_timer` and `otg_timer_initializer()` model software timers. `struct fsl_otg` embeds `struct usb_phy`, `struct otg_fsm`, MMIO pointer, delayed work, host-working flag, and IRQ. Public declarations are `fsl_otg_add_timer()`, `fsl_otg_del_timer()`, and `fsl_otg_pulse_vbus()`.

## Control Flow

The C file uses these definitions to reset and program the controller, mask write-one-to-clear bits, configure PHY interface type, manipulate VBUS/SRP/HNP signals, and run OTG FSM timers. `struct usb_dr_mmap` lets code address operational registers by field name.

## State and Persistence Behavior

The header defines both volatile kernel state (`struct fsl_otg`, `struct fsl_otg_timer`) and hardware register state. Register writes affect controller role, port power, OTG signaling, interrupt enable/status, and PHY interface configuration.

## Dependencies and Integration Points

It depends on Linux OTG FSM and USB OTG headers. It is private to the Freescale OTG transceiver driver and platform data using Freescale USB2 controller conventions.

## Risks and Test Signals

The risk is bitfield misuse in mixed host/device/OTG register spaces. Write-one-to-clear masks are especially important for PORTSC/OTGSC. Header changes should be validated by build coverage, register-offset audits, and role-transition tests on Freescale dual-role hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-fsl-usb.h -->
