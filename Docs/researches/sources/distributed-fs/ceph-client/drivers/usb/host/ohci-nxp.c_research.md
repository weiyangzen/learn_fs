# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-nxp.c

## Purpose

`ohci-nxp.c` is the platform OHCI driver for NXP LPC32xx-style USB host devices. It configures an ISP1301 USB transceiver over I2C, enables the SoC host bit and VBUS, and registers the generic OHCI core.

## Important APIs, Types, and Functions

Important functions are `isp1301_configure_lpc32xx()`, `isp1301_vbus_on()`, `isp1301_vbus_off()`, `ohci_nxp_start_hc()`, `ohci_nxp_stop_hc()`, `ohci_hcd_nxp_probe()`, and `ohci_hcd_nxp_remove()`. The global `isp1301_i2c_client` tracks the transceiver reference.

## Control Flow

Probe resolves the optional DT `transceiver` phandle, obtains the ISP1301 I2C client, coerces a 32-bit DMA mask, checks USB enablement, enables the host clock, programs ISP1301 mode registers for DAT_SE0 operation, creates the HCD, maps the OHCI MMIO resource, gets the IRQ, sets the SoC `HOST_EN` bit, drives VBUS, and calls `usb_add_hcd()`. Remove reverses HCD registration, disables host/VBUS, releases the HCD, and drops the transceiver device reference.

## State and Persistence Behavior

Driver state is minimal and mostly global: the ISP1301 client pointer plus clock/devm resources and HCD state. Hardware state persists in ISP1301 I2C registers and the LPC32xx USB OTG status/control register until reset or stop.

## Dependencies and Integration Points

It depends on platform bus, OF phandle lookup, I2C SMBus access, ISP1301 register definitions, clocks, DMA mask setup, and the generic OHCI `hc_driver` from `ohci_init_driver()`. It matches `nxp,ohci-nxp` and platform alias `usb-ohci`.

## Risks and Test Signals

Risks include the global transceiver pointer preventing multiple instances, unchecked I2C write failures, fixed `USB_CONFIG_BASE` ioremap, no suspend/resume support, and clock/transceiver ordering problems. Test signals include deferred probe until ISP1301 is present, correct VBUS drive, successful enumeration on LPC32xx, cleanup after `usb_add_hcd()` failure, and remove/reprobe without leaked I2C references.
