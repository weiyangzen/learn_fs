# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-da8xx.c

## Purpose
`ohci-da8xx.c` is the TI DA8xx/OMAP-L1x platform glue for the generic OHCI host driver. It powers and clocks the USB1.1 OHCI block, integrates a PHY, optionally controls VBUS through a regulator, reports overcurrent through either a GPIO or regulator error flags, and overrides root-hub callbacks so the one real external port is represented correctly.

## Important APIs, types, and functions
`struct da8xx_ohci_hcd` extends OHCI private data with the HCD pointer, USB1.1 clock, PHY, optional VBUS regulator, regulator notifier, and optional overcurrent GPIO. `ocic_mask` is a global volatile bitmask for overcurrent-indicator-change reporting. `da8xx_overrides` sets `.reset = ohci_da8xx_reset` and `.extra_priv_size`.

Resource/power helpers are `ohci_da8xx_enable()`, `ohci_da8xx_disable()`, `ohci_da8xx_set_power()`, `ohci_da8xx_get_power()`, `ohci_da8xx_get_oci()`, `ohci_da8xx_has_set_power()`, and `ohci_da8xx_has_oci()`. Overcurrent callbacks are `ohci_da8xx_regulator_event()`, `ohci_da8xx_oc_thread()`, and `ohci_da8xx_register_notify()`. OHCI integration is via `ohci_da8xx_reset()`, `ohci_da8xx_hub_status_data()`, `ohci_da8xx_hub_control()`, `ohci_da8xx_probe()`, `ohci_da8xx_remove()`, optional suspend/resume, and module init/exit.

## Control flow
Module init initializes a generic OHCI driver with DA8xx reset/private overrides, saves the generic `hub_control` and `hub_status_data` callbacks, replaces them with DA8xx wrappers, and registers the platform driver. Probe allocates the HCD, gets the clock and `"usb-phy"`, optionally gets a `"vbus"` regulator, optionally gets an `"oc"` GPIO and threaded IRQ, maps registers, gets the main IRQ, calls `usb_add_hcd()`, enables wakeup, and registers a regulator overcurrent notifier if applicable.

During OHCI reset, `ohci_da8xx_enable()` enables the clock, initializes the PHY, powers it on, forces `ohci->num_ports = 1` because the hardware root-hub register reports two ports, calls `ohci_setup()`, and patches root hub register A to advertise per-port power switching and overcurrent support when the platform has those capabilities.

Hub status wraps the original OHCI status bitmap and adds port 1 status-change notification if `ocic_mask` is set. Hub control intercepts GetPortStatus for port 1 to combine generic `roothub_portstatus()` with regulator/GPIO power and overcurrent state, and intercepts Set/ClearPortFeature POWER and C_OVER_CURRENT. Everything else delegates to the original OHCI callback.

Suspend waits for OHCI state-change timing, calls `ohci_suspend()`, disables PHY/clock, and marks the HCD suspended. Resume reenables clock/PHY and calls `ohci_resume()`.

## State and persistence behavior
Private HCD state is per-controller. `ocic_mask` is file-global, not per-controller, which is acceptable only if one controller/port is expected. VBUS regulator state persists in regulator framework state; PHY/clock state is controlled through runtime calls. The overcurrent change bit remains latched in `ocic_mask` until a ClearPortFeature C_OVER_CURRENT hub request clears it.

## Dependencies and integration points
This file depends on generic OHCI internals (`ohci.h`, `ohci_setup()`, `ohci_init_driver()`, root-hub helpers, suspend/resume), platform device resources, Linux clock, PHY, regulator, GPIO descriptor, threaded IRQs, jiffies timing, unaligned access helpers, and OF matching for `ti,da830-ohci`.

## Risks and edge cases
The global `ocic_mask` is not protected by a lock and is shared across potential instances. Regulator and GPIO overcurrent paths have different polarity/semantics: the GPIO thread disables the regulator when the GPIO reads asserted and a regulator exists, while `ohci_da8xx_get_oci()` reports GPIO value directly. If platform polarity is misdescribed, root-hub overcurrent reporting and VBUS shutdown can invert. Probe registers the regulator notifier after `usb_add_hcd()`, so an early overcurrent event during registration window may be missed. Suspend/resume manually rate-limits around `ohci->next_statechange`; missed timing can affect OHCI state transitions.

## Test signals
Validate enumeration on DA8xx with only the mandatory clock/PHY, with a VBUS regulator, with an overcurrent GPIO, and with regulator overcurrent events. Check that the root hub advertises one port, Set/ClearPortFeature POWER toggles VBUS, overcurrent sets OCIC and disables VBUS, ClearPortFeature C_OVER_CURRENT clears `ocic_mask`, and suspend/resume restores enumeration. Inspect `roothub.a` behavior after reset to confirm power/OCI capability bits match platform resources.
