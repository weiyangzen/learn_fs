<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-ab8500-usb.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-ab8500-usb.c

## Purpose

`phy-ab8500-usb.c` is the USB transceiver driver for ST-Ericsson AB8500/AB8505 PMIC-family chips. It detects USB link-status changes, classifies cable/charger/ACA states, powers host or peripheral PHY modes, notifies Ux500 MUSB glue through USB PHY notifiers, manages regulators/clock/pinctrl, applies PMIC PHY tuning and watchdog workarounds, and registers a legacy `usb_phy`.

## Important APIs, Types, and Functions

`struct ab8500_usb` stores `struct usb_phy`, PMIC pointer, current mode, VBUS draw, delayed PHY-disable work, system clock, three regulators, saved voltage, previous link status, pinctrl handles, charger-detection flag, and behavior flags. Link status enums model AB8500 and AB8505 register encodings; `enum ab8500_usb_mode` tracks idle, peripheral, host, dedicated charger, and UART states.

Key functions include regulator helpers, `ab8500_usb_phy_enable()`, `ab8500_usb_phy_disable()`, AB8500/AB8505 link-status update functions, `abx500_usb_link_status_update()`, IRQ handlers for link status and disconnect, `ab8500_usb_set_host()`, `ab8500_usb_set_peripheral()`, `ab8500_usb_restart_phy()`, tuning helpers, `ab8500_usb_probe()`, and `ab8500_usb_remove()`.

## Control Flow

Probe rejects old AB8500 revisions, allocates PHY/OTG structures, sets flags based on chip family, obtains regulators and sysclk, requests link/status/disconnect IRQs, registers the USB2 PHY, applies tuning for newer AB8500/AB8505, runs watchdog and PHY restart sequences, then reads initial link status. Link-status IRQ reads a PMIC line-status register and dispatches to the family-specific decoder. USB host/peripheral links enable the corresponding PHY, call `UX500_MUSB_PREPARE`, and send `UX500_MUSB_ID` or `UX500_MUSB_VBUS`; charger states send charger notifications and USB charger events; idle/disconnect states reset mode and VBUS draw.

Disconnect IRQ disables host/peripheral/UART PHY paths, sends notifier cleanup for peripheral mode, handles AB8500 v2.0 dedicated-charger workaround, and returns idle. `set_host` and `set_peripheral` only update pointers directly; when called with NULL from contexts that may be atomic they schedule delayed work to disable PHY safely.

## State and Persistence Behavior

Runtime state is held in `struct ab8500_usb` and PMIC registers. Persistent hardware effects include regulator voltage/load changes, PMIC PHY control bits, PHY tuning registers, pinctrl state, watchdog control register toggles, and link-status/charger detection behavior. No filesystem persistence exists.

## Dependencies and Integration Points

The file depends on ABx500 MFD register APIs, AB8500 chip-id helpers, regulators, clocks, pinctrl, threaded IRQs, USB PHY/OTG core, and Ux500 MUSB notifier event constants. It is a key provider for `ux500.c` OTG notifications.

## Risks and Test Signals

Risks include duplicated `if (ab->mode == USB_IDLE)` text in the AB8505 peripheral path, a duplicated `return irq;` line in IRQ setup, races between IRQs and scheduled disable work, regulator-voltage restoration when USB is not sole consumer, and correct handling of spurious link statuses. Tests should cover AB8500 and AB8505 cable matrix, ACA RID A/B/C, charger detection, boot-with-cable, disconnect in host/peripheral/UART/charger modes, NULL host/gadget callbacks, regulator failures, tuning failures, and remove while work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-ab8500-usb.c -->
