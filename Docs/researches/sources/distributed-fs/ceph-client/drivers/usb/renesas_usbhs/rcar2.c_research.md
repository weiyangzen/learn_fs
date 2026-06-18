<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rcar2.c -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rcar2.c

## Purpose
R-Car Gen2 platform callbacks and driver parameters for Renesas USBHS.

## Important APIs, Types, And Functions
`usbhs_rcar2_hardware_init()` gets generic PHY `"usb"` and stores it in `priv->phy`. `usbhs_rcar2_hardware_exit()` puts it. `usbhs_rcar2_power_ctrl()` calls `phy_init()`/`phy_power_on()` on enable and `phy_power_off()`/`phy_exit()` on disable. `usbhs_rcar_gen2_plat_info` exports callbacks and enables USB-DMAC/new pipe configs.

## Control Flow
Common probe calls hardware init, runtime power calls power control, remove calls hardware exit. ID is fixed to gadget.

## State And Persistence
`priv->phy` and generic PHY power/init state; static const platform-info.

## Dependencies And Integration Points
Depends on generic PHY APIs and common platform callbacks. Selected by R-Car Gen2 compatibles.

## Risks
Without `CONFIG_GENERIC_PHY`, init returns `-ENXIO`. `phy_power_on()` failure after `phy_init()` is not locally balanced by `phy_exit()`. Role is forced gadget.

## Test Signals
Generic PHY enabled/disabled, missing PHY, power balance, power-on failure, and Gen2 compatible matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rcar2.c -->
