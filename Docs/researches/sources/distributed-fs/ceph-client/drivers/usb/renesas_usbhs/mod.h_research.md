<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/mod.h -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/mod.h

## Purpose
Defines the internal host/gadget mode abstraction and interrupt callback contract.

## Important APIs, Types, And Functions
`struct usbhs_irq_state` snapshots interrupt and pipe status registers. `struct usbhs_mod` stores start/stop hooks and IRQ callbacks for DVST, CTRT, BEMP, BRDY, ATTCH, DTCH, SIGN, and SACK. `struct usbhs_mod_info` stores registered modes, current mode, autonomy VBUS callback, and VBUS getter. `usbhs_mod_call()` and `usbhs_mod_info_call()` invoke optional callbacks.

## Control Flow
Common hotplug switches modules and calls start/stop. IRQ dispatch fans out through this callback table. FIFO code updates `irq_bempsts`/`irq_brdysts` and refreshes masks.

## State And Persistence
Persistent state is callback tables and current mode pointer; IRQ snapshots are transient.

## Dependencies And Integration Points
Includes `common.h` and mode IDs from `linux/usb/renesas_usbhs.h`. Conditional host/gadget declarations align with Makefile object inclusion.

## Risks
Missing callbacks return 0 and can hide inactive behavior. Stub guards must match Makefile conditions. Registered mode slots must be populated before current-mode use.

## Test Signals
Build frontend matrices and runtime callback install/remove plus interrupt mask updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/mod.h -->
