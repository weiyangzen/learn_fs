<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-am335x-control.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-am335x-control.c

## Purpose

`phy-am335x-control.c` is the AM335x USB control-module companion driver. It owns the shared control registers used by AM335x USB PHY instances and exports a `struct phy_control` callback table so per-PHY drivers can power PHY 0/1 and configure wakeup bits.

## Important APIs, Types, and Functions

`struct am335x_control_usb` stores device, PHY control register base, wakeup register base, spinlock, and embedded `struct phy_control`. Internal callbacks are `am335x_phy_power()` and `am335x_phy_wkup()`. Exported lookup API is `am335x_get_phy_control(struct device *dev)`.

## Control Flow

Probe matches `ti,am335x-usb-ctrl-module`, maps named resources `phy_ctrl` and `wakeup`, initializes the spinlock, copies the static callback table, and stores drvdata. `am335x_get_phy_control()` parses the caller's `ti,ctrl_mod` phandle, finds the matching platform device bound to this driver, retrieves drvdata, drops references, and returns the callback table. Power operations select register offsets for ID 0 or 1, clear or set PHY power-down bits, and configure VBUS/session comparator bits based on host vs non-host mode. Wake operations update PHY wake-enable bits under spinlock.

## State and Persistence Behavior

State persists in mapped control-module registers: power-down bits, OTG VBUS detect/session-end enable bits, and wake-enable bits. Kernel state is the single control object plus exported callback pointers.

## Dependencies and Integration Points

The file depends on OF phandles, platform bus lookup, MMIO, spinlocks, and the header `phy-am335x-control.h`. It is consumed by `phy-am335x.c`.

## Risks and Test Signals

Risks include cross-device lifetime of returned callback pointers, no NULL checks in inline wrappers, invalid PHY IDs producing only `WARN_ON`, and mixed locked/unlocked register updates. Tests should cover phandle absence/defer, both PHY IDs, host/peripheral power-on bit patterns, wake enable/disable, invalid IDs, and probe resource failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-am335x-control.c -->
