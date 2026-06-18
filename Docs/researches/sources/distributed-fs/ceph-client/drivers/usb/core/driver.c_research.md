# sources/distributed-fs/ceph-client/drivers/usb/core/driver.c

## Purpose

`driver.c` is the USB bus driver-model bridge. It is not a hardware driver; it supplies the shared binding, matching, registration, unregistration, dynamic-ID, interface claiming, forced rebind, system PM, runtime PM, autosuspend/autoresume, and USB2 hardware LPM plumbing used by real USB device and interface drivers. It defines `usb_bus_type`, whose `.match` and `.uevent` callbacks make USB devices and interfaces visible to the Linux driver core.

## Important APIs, Types, and Functions

- Dynamic IDs: `usb_store_new_id()`, `usb_show_dynids()`, `new_id_store()`, `remove_id_store()`, `usb_create_newid_files()`, `usb_free_dynids()`, and `usb_match_dynamic_id()` maintain `struct usb_dynids` lists protected by `usb_dynids_lock`. `usb_store_new_id()` parses vendor/product/interface-class data, optionally copies `driver_info` from a reference static ID, appends a `struct usb_dynid`, then calls `driver_attach()`.
- Driver-model callbacks: `usb_probe_device()`, `usb_unbind_device()`, `usb_probe_interface()`, `usb_unbind_interface()`, and `usb_shutdown_interface()` are installed as `struct device_driver` callbacks during USB driver registration.
- Interface ownership APIs: `usb_driver_claim_interface()` and `usb_driver_release_interface()` let compound drivers bind additional interfaces, set `dev->driver`, manage `usb_set_intfdata()`, update `USB_INTERFACE_*` conditions, and coordinate runtime PM state.
- Matching APIs: `usb_match_device()`, `usb_match_one_id_intf()`, `usb_match_one_id()`, `usb_match_id()`, `usb_device_match_id()`, `usb_driver_applicable()`, `usb_device_match()`, and `usb_uevent()` implement descriptor matching, dynamic matching, USB device-vs-interface separation, and uevent `PRODUCT`/`TYPE` fields.
- Registration APIs: `usb_register_device_driver()`, `usb_deregister_device_driver()`, `usb_register_driver()`, `usb_deregister()`, and `is_usb_device_driver()` wire either whole-device drivers or interface drivers into `usb_bus_type`.
- Rebind helpers: `usb_forced_unbind_intf()`, `usb_unbind_and_rebind_marked_interfaces()`, `unbind_marked_interfaces()`, `rebind_marked_interfaces()`, and PM-specific `unbind_no_pm_drivers_interfaces()` manage `needs_binding` when reset-resume or suspend/resume support is missing.
- PM APIs: `usb_suspend()`, `usb_resume()`, `usb_resume_complete()`, `usb_runtime_suspend()`, `usb_runtime_resume()`, `usb_runtime_idle()`, `usb_enable_autosuspend()`, `usb_disable_autosuspend()`, `usb_autosuspend_device()`, `usb_autoresume_device()`, and the `usb_autopm_*interface*()` helpers are the main runtime/system PM surface exposed to USB drivers.
- LPM APIs: `usb_enable_usb2_hardware_lpm()` and `usb_disable_usb2_hardware_lpm()` delegate to `hcd->driver->set_usb2_hw_lpm()` and update `udev->usb2_hw_lpm_enabled`.

## Control Flow

Interface driver registration through `usb_register_driver()` populates the embedded `driver` fields, initializes dynamic IDs, registers with the driver core, and creates `new_id`/`remove_id` sysfs attributes when dynamic IDs are allowed. Matching for interface devices flows through `usb_device_match()`: interface drivers are rejected for whole-device nodes, static IDs are tried via `usb_match_id()`, and dynamic IDs are tried via `usb_match_dynamic_id()`.

Interface probing starts in `usb_probe_interface()`. It rejects owned devices and unauthorized devices/interfaces, finds a static or dynamic ID, autoresumes the device, marks the interface `USB_INTERFACE_BINDING`, prepares runtime PM, optionally disables hub-initiated LPM, performs deferred altsetting-zero restoration, invokes the driver `probe()`, and finally marks the interface `USB_INTERFACE_BOUND`. On failure it clears driver data, remote-wakeup needs, condition state, LPM disable refs, runtime PM enablement, and the device usage count.

Interface unbinding starts in `usb_unbind_interface()`. It marks `USB_INTERFACE_UNBINDING`, autoresumes for possible `SetInterface`, disables LPM if policy requires it, disables endpoints unless `soft_unbind` is allowed and the device remains present, calls driver `disconnect()`, frees SuperSpeed bulk streams, restores or defers altsetting 0, clears driver data and wakeup needs, disables runtime PM for autosuspend-capable drivers, and autosuspends the device if autoresume succeeded.

Whole-device driver probing through `usb_probe_device()` uses generic USB device-driver behavior when `generic_subclass` is set and otherwise calls a specialized driver `probe()`. If a specialized whole-device driver returns `-ENODEV`, the code can set `udev->use_generic_driver` and return `-EPROBE_DEFER` so the generic USB driver can bind later.

System suspend uses `usb_suspend()`: first unbind interface drivers lacking suspend/resume, compute the remote-wakeup policy, call `usb_suspend_both()`, and optionally disable the port for `USB_QUIRK_DISCONNECT_SUSPEND`. `usb_suspend_both()` suspends interfaces in reverse order, suspends the device, ignores selected system-sleep errors, blocks new URB submissions by clearing `udev->can_submit`, and flushes all endpoints unless device offload is active. Resume uses `usb_resume_both()` to set `can_submit`, resume the device, resume interfaces, mark activity, and then `usb_resume()` refreshes runtime PM active state and unbinds interfaces that need later rebinding.

Runtime PM uses `autosuspend_check()` as the gate. It rejects unattached devices, active interfaces, missing remote-wakeup support, HCDs that cannot receive wakeups, and reset-resume combinations where interface drivers cannot reset-resume. `usb_runtime_suspend()` calls `usb_suspend_both(PMSG_AUTO_SUSPEND)` and normalizes most child-device failures to `-EBUSY`; `usb_runtime_idle()` schedules autosuspend but returns `-EBUSY` so the PM core does not immediately suspend by itself.

## State and Persistence Behavior

Persistent in-kernel state includes per-driver dynamic ID lists, `usb_interface::condition`, `needs_binding`, `needs_altsetting0`, `needs_remote_wakeup`, `dev.power` runtime-PM counters, `usb_device::use_generic_driver`, `do_remote_wakeup`, `reset_resume`, `can_submit`, and USB2 hardware LPM flags. There is no durable storage; sysfs `new_id`/`remove_id` mutates live driver state only. The bus type is static process lifetime state.

The PM helpers are usage-count based. `usb_autoresume_device()` and `usb_autopm_get_interface*()` increment usage or queue resumes; matching `put` helpers decrement usage and mark last busy. Probe/unbind paths deliberately balance these refs. The suspend path changes `can_submit`, and the unbind path may defer altsetting-zero restoration when the interface is prepared for system sleep or the device is suspended.

## Dependencies and Integration Points

This file depends on Linux driver core APIs (`driver_register`, `device_attach`, `device_release_driver`, bus matching, uevents), runtime PM (`pm_runtime_*`), USB core descriptor and configuration helpers, HCD hooks for LPM, hub/port suspend-resume helpers, `usb_generic_driver`, and interface endpoint management helpers such as `usb_disable_interface()`, `usb_enable_interface()`, `usb_set_interface()`, `usb_free_streams()`, and `usb_hcd_flush_endpoint()` indirectly through unbind. It integrates with usbfs and user space through uevents and dynamic ID sysfs attributes.

## Risks and Edge Cases

- PM reference leaks or underflows are high risk because probe, unbind, explicit interface claiming, runtime autosuspend, and device-level autoresume all balance the same runtime-PM counters.
- Deferred altsetting-zero restoration depends on `needs_altsetting0`; missed restoration can leave unbound interfaces in a non-default alternate setting.
- Dynamic IDs are live and protected by one global mutex; malformed `new_id` input, missing reference IDs, or careless `driver_info` inheritance can bind drivers to unintended devices.
- Forced unbind/rebind for missing reset-resume or PM support is lock-order sensitive and must preserve multi-interface drivers by unbinding all marked interfaces before rebinding any of them.
- Offload-aware suspend skips selected interfaces and endpoint flushing; regressions can leave URBs active across system suspend.
- Generic whole-device fallback relies on `use_generic_driver` and `-EPROBE_DEFER`; specialized device-driver matching changes can alter which driver owns a device.

## Test Signals

Useful signals include USB driver bind/unbind tests, sysfs dynamic-ID add/remove and reprobe tests, authorization rejection tests, multi-interface claim/release drivers, runtime PM usage-counter tracing, autosuspend/resume with remote wakeup, reset-resume devices, altsetting changes during unbind, LPM-disabled drivers, hub-initiated LPM failure injection, and suspend/resume across devices with and without `suspend`, `resume`, and `reset_resume` callbacks. Kernel logs for `probe`, `disconnect`, `suspend error`, `resume error`, and `rebind failed` are direct behavioral indicators.
