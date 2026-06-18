# sources/distributed-fs/ceph-client/drivers/usb/core/of.c

## Purpose
Implements Device Tree helpers for USB devices, interfaces, and hub ports. It maps USB topology concepts such as hub port numbers, connect type, combined device/interface nodes, and interface nodes onto OF child nodes and graph endpoints.

## Important APIs, Types, And Functions
Exported APIs are `usb_of_get_device_node()`, `usb_of_has_combined_node()`, `usb_of_get_connect_type()`, and `usb_of_get_interface_node()`. The internal `usb_of_has_devices_or_graph()` distinguishes hubs with explicit child or graph descriptions from hubs with no OF port modeling. It uses `struct device_node`, `struct usb_device`, `struct usb_device_descriptor`, `struct usb_config_descriptor`, and `enum usb_port_connect_type`.

## Control Flow
`usb_of_get_device_node()` scans hub child nodes for a one-cell `reg` equal to the one-based port number. `usb_of_has_combined_node()` returns true only when a device has an OF node, one configuration, one interface, and device class per-interface or hub. `usb_of_get_connect_type()` first checks whether the hub node has graph or child-port modeling; absent modeling yields `UNKNOWN`, while present modeling defaults unmentioned ports to `NOT_USED`. It treats an available graph remote endpoint as `HOT_PLUG` and an available child node with matching `reg` as `HARD_WIRED`. `usb_of_get_interface_node()` scans child nodes for a two-cell `reg` matching interface number and configuration value.

## State And Persistence
The helpers do not persist state. They return refcounted `device_node` pointers where documented, requiring callers to drop references. Their decisions become persistent only when callers store resulting OF nodes or connect types in USB device/interface/port objects.

## Dependencies And Integration Points
Depends on OF core and OF graph APIs. `message.c` uses combined-node and interface-node helpers while creating interface devices; `port.c` uses connect-type discovery when creating hub port devices. The results influence sysfs `connect_type`, interface firmware companion data, and whether disabled OF nodes suppress interface registration.

## Risks And Test Signals
Risks include refcount leaks on returned nodes, ambiguity when both graph endpoints and child nodes describe a port, inactive remote endpoints, malformed `reg` properties, and devices with descriptors that do not match firmware topology. Test signals include DT hubs with no port modeling, explicit hotplug connectors, hard-wired child devices, disabled child/remote nodes, combined-node one-interface devices, and multi-configuration/interface devices that must not reuse combined nodes.
