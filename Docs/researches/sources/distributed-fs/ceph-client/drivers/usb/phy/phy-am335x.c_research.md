<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-am335x.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-am335x.c

## Purpose

`phy-am335x.c` provides a USB2 PHY driver for AM335x SoCs by combining the generic NOP USB PHY framework with AM335x-specific control-module power and wake callbacks.

## Important APIs, Types, and Functions

`struct am335x_phy` embeds `struct usb_phy_generic`, a `struct phy_control *`, PHY ID, and USB data-role mode. Important callbacks are `am335x_init()`, `am335x_shutdown()`, `am335x_phy_suspend()`, and `am335x_phy_resume()`. Lifecycle functions are `am335x_phy_probe()` and `am335x_phy_remove()`.

## Control Flow

Probe allocates state, retrieves control callbacks through `am335x_get_phy_control()`, reads the DT alias ID `phyN`, derives role mode via `of_usb_get_dr_mode_by_phy()`, creates a generic PHY, overrides its init/shutdown callbacks, disables wakeup by default to avoid immediate DS0 wake, powers the PHY down, and registers it with `usb_add_phy_dev()`. Init powers the PHY on through the control module; shutdown powers it off. Suspend optionally enables PHY wakeup if userspace allowed device wake, then powers off; resume powers on and disables wakeup again.

## State and Persistence Behavior

Runtime state is per-platform-device. Hardware state is owned by the control-module registers reached through callbacks. Wakeup policy persists in the device power-management flags while the device exists.

## Dependencies and Integration Points

The driver depends on OF aliases and role parsing, `phy-am335x-control`, generic USB PHY helper code, platform PM, and the legacy USB PHY registry. It is selected with `AM335X_PHY_USB`.

## Risks and Test Signals

Risks include alias absence, control driver probe ordering, role-mode propagation, and wakeup policy mismatch between standby and DS0. Tests should cover PHY0/PHY1 aliases, missing `ti,ctrl_mod`, host/peripheral/OTG modes, init/shutdown sequencing, suspend/resume with wakeup enabled and disabled, and removal while registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-am335x.c -->
