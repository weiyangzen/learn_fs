# sources/distributed-fs/ceph-client/drivers/phy/ti/phy-tusb1210.c

## Purpose
ULPI PHY driver for TI TUSB1210/TUSB1211. It creates a generic ULPI PHY, controls optional reset/chip-select GPIOs, programs vendor tuning and DP/DM swap, switches host/device OTG bits, and optionally exposes TUSB1211 charger detection through power-supply.

## APIs, Flow, And State
`struct tusb1210` stores device, PHY, GPIOs, cached `ULPI_OTG_CTRL`, cached vendor register, and optional charger-detection work state. Probe asserts GPIOs, reads `TUSB1210_VENDOR_SPECIFIC2`, applies `ihstx`, `zhsdrv`, and `datapolarity` properties, writes the result, optionally starts charger detection, and creates an ULPI PHY. Power-on asserts GPIOs, waits 50 ms, and restores vendor settings. `.set_mode()` updates host/device OTG pull-down, pull-up, and VBUS-drive bits.

## Dependencies And Integration
Depends on ULPI bus helpers, generic ULPI PHY creation, GPIO descriptors, device properties, workqueues, parent runtime PM, and optional power-supply core. Matches TI vendor IDs for TUSB1210 and TUSB1211.

## Risks And Tests
Power-on ignores restore write failure. Charger detection is DCP/SDP only and depends on hard-coded charger power-supply names. Test GPIO optionality, property bitfields, host/device mode writes, reset restore, charger detect only on TUSB1211, notifier reconnect/disconnect, power-supply properties, and remove cleanup.
