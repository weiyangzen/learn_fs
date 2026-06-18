# sources/distributed-fs/ceph-client/drivers/power/supply/smb347-charger.c

## Purpose
Summit SMB345/SMB347/SMB358 charger driver. It exposes mains and/or USB power supplies, configures charger current/voltage/temperature behavior, handles charger interrupts, and registers a fixed 5 V USB VBUS regulator for OTG mode.

## Important APIs, Types, and Functions
`struct smb347_charger` stores regmap, mains/USB supplies, regulator, online state, configuration limits, thermal limits, feature flags, and enable polarity. Lookup tables convert hardware selectors for fast/precharge/termination/input/compensation currents. Important functions include `smb347_probe()`, `smb347_hw_init()`, `smb347_interrupt()`, `smb347_get_property()`, `smb347_irq_init()`, `smb347_usb_vbus_regulator_enable()`, and DT/battery-info parsing helpers.

## Control Flow
Probe parses firmware properties, registers enabled power supplies, overlays battery-info constraints, programs hardware while configuration writes are enabled, initializes IRQ support when available, and registers the USB VBUS regulator. Interrupts read STAT/IRQSTAT registers, report charger errors, termination/taper, timeout, and under-voltage input changes, then update online state and notify supplies. Regulator enable disables charging, optionally toggles INOK polarity, enables OTG, and restores current limit.

## State and Persistence
`mains_online`, `usb_online`, `irq_unsupported`, and `usb_vbus_enabled` are volatile software state. Hardware config registers are writable only when `CMD_A_ALLOW_WRITE` is set; comments describe volatile RAM mirrored from nonvolatile defaults after POR, but the driver itself does not persist new NVM settings.

## Dependencies and Integration Points
Depends on I2C, regmap with cache, power_supply, regulator framework, DT binding constants, firmware properties, optional IRQ, and battery-info data. Compatible strings support `summit,smb345`, `summit,smb347`, and `summit,smb358`.

## Risks and Test Signals
IRQs are disabled around property reads and write-window changes, so deadlock/latency should be checked. OTG regulator enable intentionally disables charging and may require platform-specific INOK toggling. Current conversion floors to supported table entries. Test mains-only, USB-only, dual-supply, no-IRQ, IRQ, OTG enable/disable, thermal limits from battery info, and remove/shutdown cleanup.
