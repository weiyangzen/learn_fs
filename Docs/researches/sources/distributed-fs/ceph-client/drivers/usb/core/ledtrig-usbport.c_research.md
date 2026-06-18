# sources/distributed-fs/ceph-client/drivers/usb/core/ledtrig-usbport.c

## Purpose

`ledtrig-usbport.c` implements the `usbport` LED trigger. It lets an LED turn on when at least one USB device is connected to a selected set of USB hub ports, with per-port sysfs toggles and optional device-tree `trigger-sources` defaults.

## Important APIs, Types, and Functions

`struct usbport_trig_data` stores the bound LED class device, list of known ports, USB notifier block, and count of connected devices on observed ports. `struct usbport_trig_port` stores one observed-capable port entry: trigger data, hub USB device, port number, generated sysfs attribute name, observed flag, device attribute, and list node.

Core helpers are `usbport_trig_usb_dev_observed()`, which checks whether a connected USB device sits below an observed port; `usbport_trig_update_count()`, which scans all USB devices and sets LED brightness to `LED_FULL` or `LED_OFF`; sysfs callbacks `usbport_trig_port_show()` and `usbport_trig_port_store()`; `usbport_trig_port_observed()`, which reads OF `trigger-sources`; add/remove helpers for ports; `usbport_trig_notify()`, which reacts to `USB_DEVICE_ADD` and `USB_DEVICE_REMOVE`; and trigger lifecycle callbacks `usbport_trig_activate()` and `usbport_trig_deactivate()`. The file registers `usbport_led_trigger` with `module_led_trigger()`.

## Control Flow

Activation allocates trigger data, creates a `ports` sysfs group under the LED device, enumerates all current USB devices with `usb_for_each_dev()` and creates an attribute for every hub port, recalculates the connected observed-device count, stores trigger data on the LED, and registers a USB notifier. A user can write `0` or `1` to each generated `ports/<hub>-portN` attribute, which updates `observed` and recomputes the count.

On `USB_DEVICE_ADD`, the notifier first adds sysfs entries for the new device's child ports if it is a hub, then turns the LED on if the newly added device is connected to an observed port and the previous count was zero. On `USB_DEVICE_REMOVE`, it removes any port entries belonging to the removed hub and decrements the count if the removed device was connected to an observed port, turning the LED off when the count reaches zero. Deactivation removes all port attributes, removes the group, unregisters the USB notifier, and frees trigger data.

## State and Persistence Behavior

Observed-port selection and connected-device count are in-memory state tied to a specific LED trigger activation. Per-port sysfs files expose and mutate `observed`; values are not persisted by this file. Device-tree `trigger-sources` only seed the initial `observed` value. The LED brightness is derived state: nonzero matching device count maps to `LED_FULL`, zero maps to `LED_OFF`.

## Dependencies and Integration Points

The file depends on the LED trigger framework, USB device iteration and notifier APIs, sysfs groups and attributes, OF helpers, USB OF node lookup, and slab allocation. It integrates externally through LED trigger selection, per-LED sysfs `ports` attributes, `trigger-sources` phandles in firmware, and USB add/remove notifications emitted by the USB core.

## Risks and Test Signals

Risks include notifier/list/sysfs lifetime races during device removal and trigger deactivation, lack of explicit locking around the ports list and count, unchecked failures from `usbport_trig_add_port()` while bulk-adding existing or newly added hub ports, count underflow if notifications and observed state get out of sync, and the noted OF FIXME where `usb_of_get_device_node()` may return the connected device node rather than the physical port node. The show callback also returns `sysfs_emit(...) + 1`, which is unusual because `sysfs_emit()` already returns the number of bytes written. Test signals include activating/deactivating the trigger while USB devices are present, toggling generated port attributes, OF default matching through `trigger-sources`, connecting/removing devices on observed and unobserved ports, adding/removing hubs so nested port attributes appear/disappear, and stress testing concurrent USB hotplug while changing LED trigger state.
