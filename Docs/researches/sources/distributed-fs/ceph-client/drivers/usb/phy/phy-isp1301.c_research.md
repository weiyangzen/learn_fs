<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-isp1301.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-isp1301.c

## Purpose

`phy-isp1301.c` is an I2C driver for the NXP ISP1301 USB transceiver. It initializes the transceiver into USB mode, configures pull-downs and interrupt masks, drives VBUS, registers a legacy USB2 PHY, and exports a helper for other code to get the underlying I2C client.

## Important APIs, Types, and Functions

`struct isp1301` stores `struct usb_phy`, mutex, and I2C client. Important helpers are `isp1301_write()`, `isp1301_clear()`, `isp1301_phy_init()`, `isp1301_phy_set_vbus()`, `isp1301_probe()`, `isp1301_remove()`, and exported `isp1301_get_client()`.

## Control Flow

Probe allocates state, initializes the PHY callbacks and label, sets client data, registers the PHY, and stores a singleton fallback client. PHY init clears UART mode, sets mode-control bits, configures OTG control pull-downs, clears pull-ups, and masks all interrupts. `set_vbus` sets or clears `OTG1_VBUS_DRV`. `isp1301_get_client()` first looks up a DT-referenced I2C node, then falls back to the singleton non-DT client with a device reference.

## State and Persistence Behavior

State is the I2C client plus PHY registration. Hardware register writes persist inside the ISP1301 until reset or later configuration. The file-scope fallback client is singleton state.

## Dependencies and Integration Points

It depends on I2C SMBus byte writes, ISP1301 register definitions, OF I2C lookup, and legacy USB PHY registration. Other platform glue can call `isp1301_get_client()`.

## Risks and Test Signals

Risks include ignoring `usb_add_phy_dev()` return, singleton fallback limiting non-DT multi-device systems, unused mutex around I2C access, and no error propagation from init register writes. Tests should cover I2C probe/remove, DT lookup reference handling, non-DT singleton lookup, init register sequence failure injection, VBUS drive toggling, and multiple-device behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-isp1301.c -->
