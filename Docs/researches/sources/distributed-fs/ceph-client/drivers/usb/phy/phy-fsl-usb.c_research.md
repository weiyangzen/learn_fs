<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-fsl-usb.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-fsl-usb.c

## Purpose

`phy-fsl-usb.c` is the Freescale USB2 OTG transceiver driver. It implements a legacy USB OTG finite-state-machine backend for Freescale dual-role controller registers, manages SRP/HNP signaling, ID-change interrupts, OTG timers, VBUS drive/charge/discharge, and start/stop handoff to host and gadget drivers.

## Important APIs, Types, and Functions

Global objects include `usb_dr_regs`, `fsl_otg_dev`, `srp_wait_done`, OTG FSM timers, driver timers, and `active_timers`. Hardware actions are `fsl_otg_chrg_vbus()`, `fsl_otg_dischrg_vbus()`, `fsl_otg_drv_vbus()`, `fsl_otg_loc_conn()`, `fsl_otg_loc_sof()`, `fsl_otg_start_pulse()`, and `write_ulpi()`.

OTG operation callbacks are collected in `fsl_otg_ops`. Host/gadget integration uses `fsl_otg_set_host()`, `fsl_otg_set_peripheral()`, `fsl_otg_start_host()`, `fsl_otg_start_gadget()`, `fsl_otg_start_srp()`, and `fsl_otg_start_hnp()`. Lifecycle and interrupt functions are `fsl_otg_conf()`, `usb_otg_start()`, `fsl_otg_probe()`, `fsl_otg_remove()`, and `fsl_otg_isr()`.

## Control Flow

Probe requires platform data, allocates the global OTG object and `usb_otg`, initializes timers and FSM ops, registers the USB2 PHY, maps the dual-role controller MMIO resource, runs board `init`, selects endian accessors on PPC, requests a shared IRQ, stops and resets the controller, programs idle USB mode and PHY interface type, enables system-interface output if present, clears/sets OTGSC bits, records initial ID state, and enables ID interrupts.

ID interrupts update FSM `id`, `default_a`, host/gadget role metadata, and either schedule delayed switch-to-gadget or immediately stop gadget, drive VBUS, and start host. SRP starts with data-line pulsing followed by VBUS pulsing, discharge, and wait timers. Host and gadget start/stop call PM suspend/resume methods on registered host/gadget parent devices.

## State and Persistence Behavior

This driver is heavily global and effectively single-instance. FSM inputs, timers, active timer list, role flags, host-working state, mapped MMIO, and PHY registration persist until remove. Hardware state persists in USBCMD, USBMODE, PORTSC, OTGSC, ULPI viewport, and optional system-interface control registers.

## Dependencies and Integration Points

It depends on `linux/usb/otg-fsm.h`, Freescale platform data, host and gadget driver PM callbacks, shared controller resources, IRQs, timers, workqueues, and the register map in `phy-fsl-usb.h`.

## Risks and Test Signals

This source tree shows strong bug signals: duplicated braces near `fsl_otg_get_timer()`, timer switch cases returning `a_wait_vrise_tmr` for many timer IDs, duplicated `.drv_vbus` initializer, pointer debug casts through `int`, busy-wait reset loops without timeout, global singleton state, and cleanup paths that free global objects on some start failures. Tests should include build/static analysis, single and repeated probe/remove, ID cable switching, SRP/HNP flows, host/gadget registration/unregistration, big/little-endian MMIO, IRQ sharing, board init/exit failures, and timer add/delete behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-fsl-usb.c -->
