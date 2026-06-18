# sources/distributed-fs/ceph-client/drivers/usb/core/port.c

## Purpose
Implements the `usb_port` device model for hub downstream ports, including sysfs attributes, port power control, runtime PM, USB2/USB3 peer-port linking, Type-C connector component binding, and port device create/remove lifecycle.

## Important APIs, Types, And Functions
External entry points are `usb_hub_create_port_device()` and `usb_hub_remove_port_device()`. Important internal functions include sysfs handlers for `disable`, `early_stop`, `location`, `connect_type`, `state`, `over_current_count`, `quirks`, and `usb3_lpm_permit`; runtime PM callbacks `usb_port_runtime_suspend()` and `usb_port_runtime_resume()`; peer helpers `link_peers()`, `unlink_peers()`, `find_and_link_peer()`, and `match_location()`; connector component callbacks `connector_bind()` and `connector_unbind()`. Main state is in `struct usb_port`, `struct usb_hub`, `struct usb_device`, PM QoS request storage, and optional Type-C connector handle.

## Control Flow
Port creation allocates `usb_port` plus PM QoS request, derives OF connect type, stores it in the hub's port array, sets default power bits, configures sysfs groups including SuperSpeed LPM policy attributes, registers the device, obtains the `state` kernfs node, installs a default no-power-off PM QoS request, adds Type-C component matching, links peer ports, enables runtime PM, and optionally exposes PM QoS flags when hub or ACPI can power-manage the port. Removal unlinks peers, removes component binding, drops the sysfs node reference, and unregisters the device.

The `disable` attribute breaks sysfs active protection before taking the hub device lock, optionally disconnects a child, toggles hub port power, waits the power-good delay, and clears change bits. Runtime suspend checks hub reset state, PM QoS no-power-off policy, global peer-link failure block, then turns port power off and queues peer PM changes. Runtime resume powers the peer SuperSpeed side before USB2 when needed, powers on the port, debounces reconnect, may request warm reset recovery, and wakes the child device for revalidation.

## State And Persistence
Port state is kernel memory exposed through sysfs. Mutated fields include `child`, `peer`, `connector`, `connect_type`, `location`, `state`, `over_current_count`, `quirks`, USB3 LPM permit bits, `early_stop`, PM QoS request, runtime PM usage, and hub bitmaps such as `power_bits`, `warm_reset_bits`, and `child_usage_bits`. Peer links and connector links are sysfs links, not persistent storage.

## Dependencies And Integration Points
Depends on hub control helpers, runtime PM, PM QoS, sysfs/kernfs, Type-C component framework, OF connect-type discovery, ACPI power manageability, HCD shared-HCD topology, and USB LPM helpers. It integrates with hub configuration/removal and user-space power policy through sysfs.

## Risks And Test Signals
High-risk areas include deadlocks between sysfs active protection and device unregister, peer-link races with runtime suspend/resume, global `usb_port_block_power_off` fallback after peer failures, child disconnect while toggling power, ACPI/OF mismatches in connect type or location, PM QoS ownership transfer, and Type-C attach notifications when a child already exists. Test signals include hub port sysfs reads/writes during unregister, USB2/USB3 peer pairing by location and default topology, runtime suspend/resume with connected devices, disabled port behavior, SuperSpeed LPM permit updates, Type-C connector binding, and lockdep/PM runtime traces.
