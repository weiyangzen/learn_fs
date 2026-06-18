# sources/distributed-fs/ceph-client/drivers/usb/core/sysfs.c

## Purpose
Defines sysfs attributes and binary attributes for USB devices, root hubs, interfaces, interface association descriptors, wireless status, power-management controls, authorization controls, and raw descriptor exposure.

## Important APIs, Types, And Functions
Exported-to-core functions are `usb_create_sysfs_dev_files()`, `usb_remove_sysfs_dev_files()`, `usb_update_wireless_status_attr()`, `usb_create_sysfs_intf_files()`, and `usb_remove_sysfs_intf_files()`. Global attribute group arrays are `usb_device_groups[]` and `usb_interface_groups[]`. Major attributes include configuration fields, descriptor fields, product/manufacturer/serial, speed/lanes/path/version, quirks, avoid-reset quirk, authorization, remove, LTM capability, runtime PM `power/*` controls, persist, USB2/USB3 LPM status and tuning, root-hub authorization defaults, IAD fields, interface modalias, supports_autosuspend, interface authorization, and wireless status. Binary attributes expose raw configuration descriptors and BOS descriptors.

## Control Flow
Most show handlers format fields from `struct usb_device` or `struct usb_interface`; mutable handlers parse text, lock devices where required, and call core operations such as `usb_set_configuration()`, `usb_authorize_device()`, `usb_deauthorize_device()`, `usb_remove_device()`, `usb_enable_autosuspend()`, `usb_disable_autosuspend()`, USB2 LPM helpers, and interface authorization helpers. Power and persist attributes are merged into the `power` group after device creation. Root hubs receive authorization default attributes. Device string and BOS binary groups use visibility callbacks to hide missing data. Interface sysfs file creation optionally fetches/caches the interface string and creates the `interface` file; removal deletes it. Wireless status updates refresh the group, notify sysfs, and emit a uevent.

## State And Persistence
Sysfs files reflect live kernel memory, not durable storage. Writes mutate `udev->actconfig`, `udev->quirks`, `persist_enabled`, runtime autosuspend delay, `usb2_hw_lpm_allowed`, L1 timeout/BESL, HCD authorization policy flags, interface `authorized`, and related PM state. Binary descriptor files read from `udev->descriptor`, `rawdescriptors`, config descriptors, and optional BOS memory.

## Dependencies And Integration Points
Depends on USB device/interface locking, runtime PM, sysfs groups and binary attributes, OF `devspec`, HCD authorization flags, LPM helpers, descriptor caches, and configuration/message APIs. It is the primary user-space management surface for usbcore.

## Risks And Test Signals
High-risk areas include lock ordering for sysfs writes that call into device removal/configuration, hiding attributes correctly when optional data is absent, deprecated `power/level` compatibility, raw descriptor offset/count arithmetic, LPM tuning without full locking for simple fields, interface deauthorization during unregister, and root-hub policy propagation. Test signals include sysfs attribute presence by speed/capability/root-hub status, concurrent reads/writes during disconnect, configuration changes through `bConfigurationValue`, safe remove, authorization toggles, descriptor binary reads with offsets, PM attribute behavior, wireless status uevents, and lockdep/KASAN.
