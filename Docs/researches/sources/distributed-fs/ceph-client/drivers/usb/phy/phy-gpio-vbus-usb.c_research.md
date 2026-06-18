<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-gpio-vbus-usb.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-gpio-vbus-usb.c

## Purpose

`phy-gpio-vbus-usb.c` implements a peripheral-only USB PHY that detects VBUS with a GPIO, optionally controls a data-line pullup GPIO, and optionally limits VBUS current through a regulator. It is intended for internal-transceiver B-device controllers without role switching.

## Important APIs, Types, and Functions

`struct gpio_vbus_data` stores VBUS and pullup GPIOs, `struct usb_phy`, regulator, delayed work, cached VBUS state, IRQ, and current draw. Important functions are `gpio_vbus_probe()`, `gpio_vbus_remove()`, `gpio_vbus_irq()`, `gpio_vbus_work()`, `gpio_vbus_set_peripheral()`, `gpio_vbus_set_power()`, `gpio_vbus_set_suspend()`, and PM suspend/resume hooks.

## Control Flow

Probe allocates state and `usb_otg`, gets required `vbus` GPIO, obtains IRQ from platform resource or GPIO, gets optional `pullup` GPIO, requests an edge IRQ, initializes delayed work, gets optional `vbus_draw` regulator, and registers the USB2 PHY. IRQ schedules 100 ms delayed work when a gadget is registered. Work debounces VBUS, updates OTG state and `last_event`, calls `usb_gadget_vbus_connect()` or disconnect, sets default 100 mA draw on connect, toggles optional pullup, sends notifiers, and updates USB PHY event.

`set_peripheral()` binds/unbinds the gadget and forces initial state sampling by calling the IRQ handler. `set_power()` updates current draw only in B-peripheral state; suspend drops draw to zero and restore uses cached current.

## State and Persistence Behavior

Runtime state is in `gpio_vbus_data`; hardware state is GPIO levels and regulator current/enable state. There is no persistent storage.

## Dependencies and Integration Points

The file depends on GPIO descriptors, IRQs, delayed work, regulator framework, USB gadget VBUS helpers, and legacy USB PHY/OTG notifiers. It matches DT compatible `gpio-usb-b-connector`.

## Risks and Test Signals

Risks include edge-trigger bounce, work running during gadget unregister, regulator current-limit failures ignored after logging, sysfs notification name mismatch risk around `vbus_state` in nearby code patterns, and assumption that pullup control belongs in this PHY. Tests should cover VBUS connect/disconnect debounce, gadget bind/unbind with VBUS already high, optional pullup absent/present, regulator absent/failing, suspend/resume IRQ wake, and remove with pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-gpio-vbus-usb.c -->
