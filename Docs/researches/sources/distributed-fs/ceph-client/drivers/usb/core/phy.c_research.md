# sources/distributed-fs/ceph-client/drivers/usb/core/phy.c

## Purpose
Wraps one or more generic PHYs associated with a USB root hub and fans out initialization, mode, calibration, connect/disconnect notification, power, suspend, and resume operations. It lets host-controller code keep several PHYs in a consistent lifecycle state.

## Important APIs, Types, And Functions
The private `struct usb_phy_roothub` is both the list head and per-PHY list entry, containing a `struct phy *` and `list_head`. Exported APIs are `usb_phy_roothub_alloc()`, `usb_phy_roothub_alloc_usb3_phy()`, `usb_phy_roothub_init()`, `usb_phy_roothub_exit()`, `usb_phy_roothub_set_mode()`, `usb_phy_roothub_calibrate()`, `usb_phy_roothub_notify_connect()`, `usb_phy_roothub_notify_disconnect()`, `usb_phy_roothub_power_on()`, `usb_phy_roothub_power_off()`, `usb_phy_roothub_suspend()`, and `usb_phy_roothub_resume()`.

## Control Flow
Allocation is skipped when `CONFIG_GENERIC_PHY` is disabled or no `phys` phandles exist. `usb_phy_roothub_alloc()` prefers a named `usb2-phy`; if present it returns a roothub with that PHY, otherwise it adds all PHYs by index. `usb_phy_roothub_alloc_usb3_phy()` only allocates a separate USB3 PHY wrapper when `usb2-phy` is present, avoiding duplicate ownership when the primary wrapper already took all PHYs. Lifecycle methods iterate the list and call matching generic PHY operations. Init and power-on roll back already-processed entries in reverse order on failure. Suspend powers off PHYs and exits them only if the controller cannot wake the system; resume re-inits when needed, powers on, and rolls back init on power failure.

## State And Persistence
PHY wrapper state is devm-managed memory attached to the controller device. It stores only the list of PHY handles; actual PHY hardware state lives in PHY providers. There is no filesystem persistence.

## Dependencies And Integration Points
Depends on OF `phys`/`phy-names`, generic PHY APIs, device wakeup policy, and host-controller probe/suspend/resume paths. It is a service layer for HCD drivers that need to operate root-hub PHYs as a unit.

## Risks And Test Signals
Risks include double-claiming PHYs when naming conventions are wrong, partial rollback correctness, differing wakeup requirements across controllers, error propagation from one PHY blocking later PHYs, and ordering-sensitive power-off. Test signals include DT with named usb2/usb3 PHYs, indexed PHY fallback, init/power failure injection verifying reverse rollback, system suspend with wakeup enabled and disabled, and connect/disconnect notification propagation.
