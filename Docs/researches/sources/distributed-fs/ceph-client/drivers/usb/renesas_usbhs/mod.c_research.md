<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/mod.c -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/mod.c

## Purpose
Mode registration/selection and top-level interrupt dispatch for Renesas USBHS. It arbitrates host/gadget modules and autonomy VBUS detection.

## Important APIs, Types, And Functions
Mode APIs: `usbhs_mod_register()`, `usbhs_mod_get()`, `usbhs_mod_get_current()`, `usbhs_mod_is_host()`, `usbhs_mod_change()`, `usbhs_mod_probe()`, `usbhs_mod_remove()`. Autonomy APIs: `usbhs_mod_autonomy_mode()` and `usbhs_mod_non_autonomy_mode()`. IRQ APIs: `usbhs_status_get_device_state()`, `usbhs_status_get_ctrl_stage()`, `usbhs_interrupt()`, `usbhs_irq_callback_update()`.

## Control Flow
Probe installs host/gadget modules and requests the controller IRQ. Hotplug selects a current module. IRQ handling snapshots status under lock, clears INTSTS/BRDY/NRDY/BEMP registers with required masks, then dispatches VBUS, device-state, control-stage, empty/ready, attach/detach, setup ACK, and setup error callbacks.

## State And Persistence
`usbhs_mod_info` stores registered modules, current module, VBUS IRQ callback, and VBUS getter. Each `usbhs_mod` stores callback pointers and BRDY/BEMP masks. Hardware interrupt enable state is updated by `usbhs_irq_callback_update()`.

## Dependencies And Integration Points
Bridges common hotplug, FIFO IRQ mask updates, and host/gadget callbacks. Uses conditional frontend probe/remove stubs from `mod.h`.

## Risks
`usbhs_mod_change(-1)` clears current mode but returns `-EINVAL`; callers intentionally ignore it. `usbhs_mod_is_host()` returns `-EINVAL` when no current mode exists, which is risky in boolean contexts. Interrupt clear ordering is hardware-sensitive.

## Test Signals
Host/gadget IRQ dispatch, autonomy VBUS, BRDY/BEMP masks, attach/detach, setup ACK/error, and mode changes with pending interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/mod.c -->
