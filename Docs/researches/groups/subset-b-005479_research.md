# Research: subset-b-005479

This grouped report covers USB core files under `sources/distributed-fs/ceph-client/drivers/usb/core/`. Each section is delimited for reconciliation into the required source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/driver.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/endpoint.c -->
# sources/distributed-fs/ceph-client/drivers/usb/core/endpoint.c

## Purpose

`endpoint.c` creates and removes per-endpoint sysfs child devices for USB host endpoints. These devices expose descriptor-derived read-only attributes such as endpoint address, attributes, max packet size, polling interval, transfer type, and direction.

## Important APIs, Types, and Functions

- `struct ep_device` stores a pointer to the endpoint descriptor, the parent `struct usb_device`, and an embedded `struct device`.
- `usb_ep_attr()` creates simple descriptor field show functions for `bLength`, `bEndpointAddress`, `bmAttributes`, and `bInterval`.
- Custom sysfs attributes `wMaxPacketSize_show()`, `type_show()`, `interval_show()`, and `direction_show()` format decoded endpoint properties.
- `ep_dev_attrs`, `ep_dev_attr_grp`, and `ep_dev_groups` define the endpoint sysfs group.
- `usb_ep_device_type` identifies endpoint devices as `usb_endpoint` and uses `ep_device_release()` to free the allocation.
- `usb_create_ep_devs()` allocates/registers the endpoint device and stores it in `endpoint->ep_dev`.
- `usb_remove_ep_devs()` unregisters the device and clears `endpoint->ep_dev`.

## Control Flow

Endpoint device creation allocates `struct ep_device`, points `desc` at `endpoint->desc`, stores `udev`, sets the sysfs groups and device type, parents the device under the supplied parent, names it `ep_%02x` using `bEndpointAddress`, and calls `device_register()`. On success it enables async suspend on the endpoint device and records the created object in `endpoint->ep_dev`; on registration failure it calls `put_device()` so the release function frees memory.

Removal is intentionally small: if `endpoint->ep_dev` exists, `device_unregister()` drops it from the device model and `endpoint->ep_dev` is cleared. Memory is released later by the driver core through `ep_device_release()`.

## State and Persistence Behavior

The only persistent state is live kernel/device-model state: the `endpoint->ep_dev` backpointer and the allocated `ep_device`. Attribute values are not cached beyond the endpoint descriptor pointer; reads decode current descriptor values. There is no disk persistence.

## Dependencies and Integration Points

This file depends on the Linux device model, sysfs attribute groups, USB endpoint descriptor helpers (`usb_endpoint_type`, `usb_endpoint_maxp`, `usb_decode_interval`, `usb_endpoint_dir_in`, `usb_endpoint_xfer_control`), and endpoint lifecycle calls from configuration/interface setup and teardown code elsewhere in USB core.

## Risks and Edge Cases

- `ep_device::desc` points into the owning endpoint object, so teardown ordering must unregister endpoint devices before endpoint descriptor storage is freed.
- Attribute output is descriptor-derived and assumes valid descriptors; malformed descriptors may yield unusual but bounded strings.
- Registration failure relies on `put_device()` to release the allocation; double-removal is avoided by clearing `endpoint->ep_dev`.
- The endpoint child device must not outlive its parent interface/device hierarchy.

## Test Signals

Signals include sysfs endpoint directory creation after setting a configuration, correct read-only values for control/bulk/interrupt/isoc endpoints, interval formatting in microseconds vs milliseconds, endpoint directories disappearing on configuration reset or disconnect, and leak checks on `device_register()` failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/endpoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/file.c -->
# sources/distributed-fs/ceph-client/drivers/usb/core/file.c

## Purpose

`file.c` implements the USB major-number dispatch layer and `usbmisc` class-device support for USB interface drivers that expose character devices. It maps minor numbers to driver-provided `file_operations`, swaps the opened file to the real operations table, and creates/destroys the corresponding class device.

## Important APIs, Types, and Functions

- `usb_minors[MAX_USB_MINORS]` maps USB minor numbers to registered `struct file_operations`.
- `minor_rwsem` protects the minor table across open/register/deregister.
- `usb_open()` looks up the minor, gets a module-safe fops reference with `fops_get()`, calls `replace_fops()`, and then invokes the real `open()` if present.
- `usb_fops` is the registered major-level dispatch fops for `USB_MAJOR`.
- `usb_devnode()` delegates devnode naming/mode to an optional `usb_class_driver::devnode`.
- `usbmisc_class` is the class used for created USB miscellaneous devices.
- `usb_major_init()` and `usb_major_cleanup()` register/unregister the USB major.
- `usb_register_dev()` allocates a minor, stores driver fops, sets `intf->minor`, and calls `device_create()`.
- `usb_deregister_dev()` destroys the class device, clears the minor-table entry, and resets interface minor state.

## Control Flow

USB core initialization calls `usb_major_init()` to register `USB_MAJOR` with `usb_fops`. A USB interface driver that wants a character device calls `usb_register_dev()`. The function validates `class_driver->fops`, rejects interfaces already assigned a minor, chooses either the requested `minor_base` or zero under `CONFIG_USB_DYNAMIC_MINORS`, scans for a free table entry while holding `minor_rwsem` for write, stores fops, assigns `intf->minor`, formats a class-device name, and creates the `usbmisc` class device. If `device_create()` fails it rolls back the table entry and minor assignment.

When user space opens the char device, VFS enters `usb_open()` through the common USB major. The function takes `minor_rwsem` for read, obtains the real fops from the minor table, atomically replaces the file fops with `replace_fops()`, and invokes the real `open()`. Deregistration destroys the class device first, clears the fops table under the write semaphore, and resets `intf->usb_dev`/`intf->minor`.

## State and Persistence Behavior

The minor table and `intf->minor`/`intf->usb_dev` are live kernel state. Device nodes may be created by devtmpfs/udev from the `usbmisc` class device, but this file itself stores no durable state. `fops_get()` provides module lifetime protection for an open; table updates are serialized by `minor_rwsem`.

## Dependencies and Integration Points

This layer integrates with VFS character devices, Linux device classes, devtmpfs/udev, USB interface driver probe/disconnect paths, and the `struct usb_class_driver` contract. Drivers must explicitly call `usb_register_dev()` after `usb_register_driver()` and must call `usb_deregister_dev()` during disconnect or teardown.

## Risks and Edge Cases

- Minor allocation can fail with `-EXFULL` if all 256 slots are used or static minor ranges collide.
- `usb_open()` returns `-ENODEV` when a device is gone or the fops table entry has already been cleared.
- Deregistration must be ordered with driver disconnect so new opens stop seeing the fops while existing opens remain protected by fops references.
- `snprintf(name, sizeof(name), class_driver->name, minor - minor_base)` assumes driver-provided names fit the 20-byte buffer and are intended as printf-style patterns.
- Drivers that forget to deregister leak minor slots and class devices.

## Test Signals

Useful tests include registering multiple USB class devices, dynamic-minor allocation, static minor collision handling, open after disconnect, module unload with open file references, `device_create()` failure injection, custom `devnode()` behavior, and verification that `/dev` nodes and sysfs `usbmisc` entries appear/disappear with interface bind/unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/generic.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/hcd-pci.c -->
# sources/distributed-fs/ceph-client/drivers/usb/core/hcd-pci.c

## Purpose

`hcd-pci.c` is the PCI bus glue for USB host controller drivers. It enables PCI devices, maps controller resources, allocates IRQ vectors for non-xHCI HCDs, creates and registers `struct usb_hcd` objects with the common HCD core, coordinates EHCI companion controllers, and supplies PCI system/runtime PM callbacks.

## Important APIs, Types, and Functions

- Companion coordination: `companions_rwsem`, `is_ohci_or_uhci()`, `for_each_companion()`, `ehci_pre_add()`, `ehci_post_add()`, `non_ehci_add()`, `ehci_remove()`, and PM-only `ehci_wait_for_companions()` coordinate EHCI with UHCI/OHCI controllers in the same PCI slot.
- Probe/remove/shutdown: `usb_hcd_pci_probe()`, `usb_hcd_pci_remove()`, and `usb_hcd_pci_shutdown()` are exported for PCI HCD drivers to use as standard callbacks.
- PowerMac platform hook: `powermac_set_asic()` toggles USB ASIC clocks under `CONFIG_PPC_PMAC`.
- PM gates: `check_root_hub_suspended()`, `suspend_common()`, `resume_common()`, sleep callbacks (`hcd_pci_suspend`, `hcd_pci_freeze`, `hcd_pci_suspend_noirq`, `hcd_pci_poweroff_late`, `hcd_pci_resume_noirq`, `hcd_pci_resume`, `hcd_pci_restore`) and runtime callbacks (`hcd_pci_runtime_suspend`, `hcd_pci_runtime_resume`) feed `usb_hcd_pci_pm_ops`.

## Control Flow

Probe begins by rejecting disabled USB or missing `hc_driver`, enabling the PCI device, and allocating one INTx/MSI vector for pre-USB3 HCDs. It creates an HCD with `usb_create_hcd()`, records AMD resume-bug state, maps either memory BAR 0 for memory-mapped controllers or the first I/O BAR for UHCI-style controllers, and sets bus mastering.

EHCI probe takes `companions_rwsem` for write, stores driver data, unconfigures and locks UHCI/OHCI companion root hubs before adding EHCI, calls `usb_add_hcd()`, clears drvdata on failure, then reconfigures/unlocks companions and records successful high-speed companion pointers. Non-EHCI probe takes the semaphore for read, adds the HCD, and records `hs_companion` if an EHCI controller is present. Successful probe enables controller wakeup and may drop runtime PM usage for run-wake-capable devices.

Remove reverses probe. It bumps runtime PM usage for run-wake devices, invokes a fake IRQ with local interrupts disabled so the driver can notice physical removal, clears EHCI companion pointers or the non-EHCI `hs_companion`, calls `usb_remove_hcd()`, clears drvdata under the companion semaphore, drops the HCD ref, frees IRQ vectors for pre-USB3 HCDs, and disables the PCI device. Shutdown calls the HCD `shutdown()` method when hardware is accessible, frees the primary IRQ, and disables PCI.

PM suspend uses `suspend_common()`: compute wakeup policy, require root hubs to already be suspended, call optional `driver->pci_suspend()`, avoid suspending if root-hub wakeup is pending, synchronize the IRQ when needed, and disable the PCI device. `hcd_pci_suspend_noirq()` saves PCI state, adjusts wakeup if the HCD is dead, prepares PCI sleep, and disables PowerMac ASIC clocks. Resume re-enables PCI, sets bus master, waits for EHCI companions on system resume, calls `driver->pci_resume()`, and reports controller death on failure.

## State and Persistence Behavior

State is live PCI/HCD state: `pci_set_drvdata()`, mapped BAR resources, allocated IRQ vectors, HCD resource fields, `hcd->self.hs_companion`, PCI power state, wakeup enablement, `hcd->amd_resume_bug`, and PowerMac ASIC clock state. No durable persistence exists.

## Dependencies and Integration Points

This file integrates PCI core APIs, Linux PM callbacks, common HCD lifecycle (`usb_create_hcd()`, `usb_add_hcd()`, `usb_remove_hcd()`, `usb_put_hcd()`), PCI resource management, IRQ allocation, EHCI/UHCI/OHCI class codes, xHCI-specific IRQ ownership convention, root-hub configuration via `usb_set_configuration()`, and platform PowerMac firmware hooks.

## Risks and Edge Cases

- EHCI companion ordering is subtle: companions are unconfigured and locked while EHCI grabs ports, then reconfigured after success/failure. Locking or drvdata ordering mistakes can break low/full-speed devices.
- xHCI manages IRQs itself, so generic IRQ allocation/free must remain gated by HCD speed flags.
- PM suspend must happen only after root hubs are suspended; otherwise DMA or downstream traffic may continue while PCI is disabled.
- Wakeup races are explicitly checked before and after `pci_suspend()`. Missing these checks can lose wake events.
- Physical removal can occur before remove; the fake IRQ path gives HCDs a chance to detect inaccessible hardware.
- Shared HCDs and primary IRQ ownership require careful shutdown/remove handling.

## Test Signals

Signals include PCI HCD probe/remove for UHCI/OHCI/EHCI/xHCI-style drivers, EHCI companion handoff with same-slot controllers, PCI BAR conflict and IRQ allocation failure injection, runtime suspend/resume with root hub suspended, system suspend/resume with wakeup pending, controller death during resume, PowerMac clock paths when configured, and hot-unplug/CardBus-style removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/hcd-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/hcd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/core/hcd.c

## Purpose

`hcd.c` is the common USB Host Controller Driver framework. It provides virtual root-hub descriptors and request handling, bus-number registration, root-hub registration, URB queue/link/unlink/giveback lifecycle, DMA mapping and local-memory bounce buffering, endpoint shutdown/bandwidth/streams helpers, root-hub and bus PM, IRQ dispatch, HCD death handling, HCD allocation/refcounting, add/remove lifecycle, local memory setup, and usbmon registration.

## Important APIs, Types, and Functions

- Global state and locks: `usb_bus_idr`, `usb_bus_idr_lock`, `hcd_root_hub_lock`, `hcd_urb_list_lock`, `hcd_urb_unlink_lock`, and `usb_kill_urb_queue`.
- Root hub descriptors and control: static root-hub device/config descriptors, `ascii2desc()`, `rh_string()`, `rh_call_control()`, `usb_hcd_poll_rh_status()`, `rh_queue_status()`, `rh_urb_enqueue()`, and `usb_rh_urb_dequeue()`.
- Bus/root hub lifecycle: `usb_bus_init()`, `usb_register_bus()`, `usb_deregister_bus()`, `register_root_hub()`, `usb_hcd_start_port_resume()`, and `usb_hcd_end_port_resume()`.
- URB lifecycle: `usb_hcd_link_urb_to_ep()`, `usb_hcd_check_unlink_urb()`, `usb_hcd_unlink_urb_from_ep()`, `usb_hcd_submit_urb()`, `usb_hcd_unlink_urb()`, `usb_hcd_giveback_urb()`, `__usb_hcd_giveback_urb()`, and `usb_giveback_urb_bh()`.
- DMA/local memory: `hcd_alloc_coherent()`, `hcd_free_coherent()`, `usb_hcd_map_urb_for_dma()`, `usb_hcd_unmap_urb_setup_for_dma()`, `usb_hcd_unmap_urb_for_dma()`, `map_urb_for_dma()`, and `unmap_urb_for_dma()`.
- Endpoint/bandwidth/stream helpers: `usb_hcd_flush_endpoint()`, `usb_hcd_alloc_bandwidth()`, `usb_hcd_disable_endpoint()`, `usb_hcd_reset_endpoint()`, `usb_alloc_streams()`, `usb_free_streams()`, `usb_hcd_synchronize_unlinks()`, and `usb_hcd_get_frame_number()`.
- PM and wake: `hcd_bus_suspend()`, `hcd_bus_resume()`, `usb_hcd_resume_root_hub()`, `hcd_resume_work()`, and OTG-only `usb_bus_start_enum()`.
- HCD infrastructure: `usb_hcd_irq()`, `usb_hc_died()`, `__usb_create_hcd()`, `usb_create_hcd()`, `usb_create_shared_hcd()`, `usb_get_hcd()`, `usb_put_hcd()`, `usb_hcd_is_primary_hcd()`, `usb_hcd_find_raw_port_number()`, `usb_add_hcd()`, `usb_remove_hcd()`, `usb_hcd_platform_shutdown()`, `usb_hcd_setup_local_mem()`, `usb_mon_register()`, and `usb_mon_deregister()`.

## Control Flow

`usb_add_hcd()` is the main bring-up path. It allocates/init/powers PHY roothub resources unless skipped, records device authorization policy from the module parameter, marks hardware accessible and interfaces authorized, creates HCD buffer pools, registers a USB bus number, allocates a root-hub `usb_device`, sets root-hub speed/lane fields from `hcd->speed`, enables root-hub wakeup capability, sets `HCD_FLAG_RH_RUNNING`, calls optional `driver->reset()`, calibrates PHYs, initializes high- and low-priority giveback workqueues, requests the primary IRQ, starts the hardware with `driver->start()`, and registers the root hub unless registration is deferred. Error labels unwind in reverse: stop, free IRQ, drop root hub, deregister bus, destroy buffers, power off/exit PHY.

Root-hub control URBs are handled synchronously in `rh_call_control()`. The function links the URB under root-hub lock, decodes the setup packet, responds directly to standard device/config/string/interface/endpoint requests where possible, delegates hub-class and BOS requests to `hcd->driver->hub_control()`, patches descriptors for wakeup and integrated transaction translator capability, copies response bytes, unlinks the URB, and completes it through `usb_hcd_giveback_urb()`. Root-hub interrupt URBs are stored as `hcd->status_urb` by `rh_queue_status()` and completed by `usb_hcd_poll_rh_status()` when `hub_status_data()` reports changes, with timer polling used when the HCD does not use new polling.

Normal URB submission in `usb_hcd_submit_urb()` increments URB/device refs, notifies usbmon, routes root-hub URBs to `rh_urb_enqueue()`, maps DMA for non-root URBs, and calls `hcd->driver->urb_enqueue()`. On submission error it reports usbmon submit error, clears state, decrements `use_count` and `urbnum`, wakes kill waiters when rejected, and drops the URB ref. Unlinking uses `usb_hcd_unlink_urb()` to safely hold the device while `unlink1()` calls either root-hub dequeue or HCD `urb_dequeue()`.

Completion flows through `usb_hcd_giveback_urb()`. The final status is stored in `urb->unlinked`; interrupt/isoc URBs and all root-hub URBs are normally queued to high-priority or low-priority BH work, while other URBs can complete immediately when `HCD_BH` is not set. `__usb_hcd_giveback_urb()` clears `hcpriv`, enforces `URB_SHORT_NOT_OK`, unmaps DMA, notifies usbmon, suspends anchor wakeups, unanchors, reports LED activity, invokes the completion callback under KCOV softirq coverage, resumes anchor wakeups, decrements use count with memory ordering, wakes kill waiters, and drops the URB ref.

Endpoint shutdown uses `usb_hcd_flush_endpoint()` to repeatedly unlink queued URBs and then wait until the endpoint queue drains. `usb_hcd_alloc_bandwidth()` reprograms HCD endpoint scheduling when configurations or alternate settings change, using `add_endpoint`, `drop_endpoint`, `check_bandwidth`, and `reset_bandwidth` driver hooks. Streams APIs validate SuperSpeed bulk endpoints and delegate stream allocation/free to the HCD.

PM root-hub bus suspend clears `HCD_FLAG_RH_RUNNING`, moves state to quiescing, calls `driver->bus_suspend()`, sets the root hub suspended, optionally suspends PHYs, and checks for wakeup races through `hub_status_data()`. Resume powers/calibrates PHYs, calls `driver->bus_resume()`, clears wakeup pending, restores root-hub device state and `HCD_FLAG_RH_RUNNING`, and delays for global resume when child ports need it. `usb_hcd_resume_root_hub()` records wakeup pending and queues freezable work to call `usb_remote_wakeup()`.

Removal in `usb_remove_hcd()` clears root-hub running, marks state quiescing, marks the root hub unregistered under lock, cancels wakeup/death work, disconnects the root hub, stops polling and hardware, frees the primary IRQ, deregisters the bus, destroys buffers, powers off/exits PHYs, invalidates the root-hub pointer under peer lock, and clears HCD flags.

## State and Persistence Behavior

State is entirely live kernel state. Bus numbers are allocated from `usb_bus_idr`; root-hub device state lives in `hcd->self.root_hub`; URB queue membership lives on endpoint `urb_list`; HCD state uses flags such as `HCD_FLAG_RH_RUNNING`, `HCD_FLAG_POLL_RH`, `HCD_FLAG_POLL_PENDING`, `HCD_FLAG_DEAD`, `HCD_FLAG_HW_ACCESSIBLE`, and state values such as `HC_STATE_RUNNING`, `QUIESCING`, `SUSPENDED`, and `HALT`. DMA mapping state is tracked in URB transfer flags and DMA handles. Shared HCDs share address0 and bandwidth mutexes and cross-reference each other until final release. No on-disk persistence exists.

## Dependencies and Integration Points

`hcd.c` is central to the USB stack. It integrates with HCD driver callbacks in `struct hc_driver`, hub core (`usb_new_device`, `usb_disconnect`, `usb_kick_hub_wq`, `usb_hub_for_each_child`), PM runtime/system paths, USB PHY roothub helpers, DMA mapping APIs, genalloc local memory pools, workqueues/timers, IRQ core, usbmon, KCOV, LED activity, OTG, root-hub descriptor emulation, and platform/PCI glue.

## Risks and Edge Cases

- URB lifecycle races are high risk: list membership, `urb->unlinked`, `use_count`, `reject`, and device references must stay ordered across submit, unlink, giveback, kill, and disconnect.
- DMA mapping flags must be idempotently cleared; setup and transfer mappings can be single, page, SG, sgtable sync, or local-memory bounce buffers.
- Root-hub control handling mixes generic emulation with HCD-specific `hub_control()`; incorrect descriptor length or patching can break enumeration.
- Root-hub polling must not complete a stale `status_urb` after removal or HCD death.
- Shared HCD release must not free shared mutexes while a peer remains.
- `usb_hc_died()` must handle both primary and shared HCDs and wake hub cleanup exactly once.
- `usb_hcd_alloc_bandwidth()` must roll back HCD schedule state on add/drop/check failures or later transfers may use invalid endpoint schedules.
- Suspend/resume wakeup races are explicitly checked; missing a pending wake can leave devices inaccessible.
- Local-memory bounce buffering stores original virtual addresses at the end of the bounce buffer, making size and alignment correctness important.

## Test Signals

Signals include HCD add/remove under success and failure injection, root-hub descriptor reads across USB1.1/2/3/3.1/3.2 speeds, root-hub status URB polling and dequeue, normal URB submit/unlink/kill/giveback, DMA mapping error paths including stack-buffer warnings, SG and sgtable sync paths, endpoint flush on disconnect/suspend, configuration and altsetting bandwidth checks, SuperSpeed stream allocation/free, root-hub bus suspend/resume with wakeup races, HCD death handling, shared HCD creation/release, local-memory pool setup, usbmon registration, and leak/race detection with lockdep/KASAN/KCSAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/hcd.c -->
