# sources/distributed-fs/ceph-client/drivers/usb/core/generic.c

## Purpose

`generic.c` implements the generic USB whole-device driver named `usb`. Its main responsibilities are choosing an initial configuration, setting that configuration so interface devices are registered, notifying usbfs/listeners about device add/remove and suspend/resume, and providing generic device-level PM behavior for root hubs and ordinary USB devices.

## Important APIs, Types, and Functions

- Configuration heuristics: `is_rndis()`, `is_activesync()`, `is_audio()`, `is_uac3_config()`, and `usb_choose_configuration()` select a suitable configuration from device descriptors.
- Generic-driver matching: `__check_for_non_generic_match()` and `usb_generic_driver_match()` prevent the generic driver from taking a device that a more specific USB device driver can bind, unless `udev->use_generic_driver` is set.
- Driver callbacks: `usb_generic_driver_probe()` chooses and installs a configuration, then calls `usb_notify_add_device()`. `usb_generic_driver_disconnect()` notifies removal and unconfigures on unbind.
- PM callbacks: `usb_generic_driver_suspend()` and `usb_generic_driver_resume()` select between root-hub bus suspend/resume and normal port suspend/resume.
- `struct usb_device_driver usb_generic_driver` exports the generic device driver with `.supports_autosuspend = 1`.

## Control Flow

`usb_generic_driver_match()` first honors `udev->use_generic_driver`, which may be set by `driver.c` after a specialized whole-device driver declines. Otherwise it scans registered USB device drivers with `bus_for_each_drv()` and returns false if any non-generic applicable driver exists.

`usb_generic_driver_probe()` is invoked as a whole-device probe. If the device is unauthorized it logs that fact and does not configure it. Otherwise it calls `usb_choose_configuration()`, and when a nonnegative configuration value is returned, calls `usb_set_configuration()`. That call registers interfaces and allows interface drivers to bind. The function reports set-configuration failures except physical removal, but still notifies add-device observers because users may set another configuration later.

`usb_choose_configuration()` lets a device driver override selection through `choose_configuration()`. Without an override, it rejects configurations exceeding available bus power, treats audio specially by preferring UAC3 when present or the first audio config otherwise, avoids first RNDIS/ActiveSync configurations when RNDIS host support is unavailable and alternatives exist, prefers non-vendor-specific interface classes for class-driver support, and otherwise falls back to the first acceptable vendor-specific config.

For PM, root hubs route through `hcd_bus_suspend()`/`hcd_bus_resume()`. Non-root devices route through `usb_port_suspend()`/`usb_port_resume()`, except non-root USB2 devices during freeze/prethaw, where no action is needed. Successful PM transitions notify usbfs through `usbfs_notify_suspend()`/`usbfs_notify_resume()`.

## State and Persistence Behavior

This file mutates live `usb_device` state by choosing configurations through `usb_set_configuration()`, honoring `udev->authorized`, reading `udev->use_generic_driver`, and indirectly creating/removing interface devices. It stores no durable state. Notifications are transient observer events.

## Dependencies and Integration Points

It depends on USB descriptor parsing, bus power accounting (`usb_get_max_power()` and `udev->bus_mA`), kernel configuration for RNDIS host support, UAC protocol constants, `driver.c` matching helpers, configuration management (`usb_set_configuration()`), usbfs notification hooks, HCD root-hub PM functions, and hub/port PM helpers. It is registered and called via the USB bus type defined in `driver.c`.

## Risks and Edge Cases

- Configuration heuristics are policy-heavy; small changes can alter which interfaces appear and therefore which drivers bind.
- Devices with broken power descriptors or broken GET_STATUS behavior are explicitly tolerated, so stricter validation could regress real hardware.
- Audio handling intentionally bypasses the general class/vendor heuristics after detecting audio; changing this can break non-UAC3 audio devices.
- Generic-driver matching must not starve specialized whole-device drivers or usbip-like drivers that intentionally decide in probe.
- `usb_generic_driver_probe()` returns success even if `usb_set_configuration()` fails for non-removal errors, relying on later user action.

## Test Signals

Signals include enumeration of devices with multiple configurations, insufficient bus power logging, RNDIS/ActiveSync devices with and without RNDIS host support, UAC3 and non-UAC3 audio devices, unauthorized devices, specialized whole-device driver registration after generic binding, configuration reset on unbind, and suspend/resume notifications observed through usbfs.
