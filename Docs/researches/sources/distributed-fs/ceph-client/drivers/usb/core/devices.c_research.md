# Research: sources/distributed-fs/ceph-client/drivers/usb/core/devices.c

Purpose: implements the read operation for the USB devices listing, producing a text snapshot of USB topology, device descriptors, strings, configurations, interfaces, IADs, endpoints, drivers, speeds, and root-hub bandwidth usage.

Important APIs and functions: exported file operations are `usbfs_devices_fops` with `.read = usb_device_read` and `.llseek = no_seek_end_llseek`. Formatting helpers include `class_decode`, `usb_dump_endpoint_descriptor`, `usb_dump_interface_descriptor`, `usb_dump_interface`, `usb_dump_iad_descriptor`, `usb_dump_config_descriptor`, `usb_dump_config`, `usb_dump_device_descriptor`, `usb_dump_device_strings`, `usb_dump_desc`, and recursive `usb_device_dump`.

Control flow: `usb_device_read` locks `usb_bus_idr_lock`, iterates registered USB buses, skips unregistered root hubs, locks the root hub, and recursively dumps each device tree. `usb_device_dump` allocates an 8 KiB scratch buffer per device, formats topology and optional root-hub bandwidth, appends descriptor/config/interface/endpoint lines, handles skip/count for file offsets, copies the requested slice to userspace, frees the buffer, then recurses over child devices while locking each child.

State and persistence: no persistent state. Output is generated live from USB bus/device structures. File position drives skip behavior across reads; no private iterator is stored.

Dependencies and integration points: depends on USB bus IDR, hub child iteration, device locks, descriptor caches from `config.c`, `usb_decode_interval`, HCD bandwidth accounting, and uaccess. It provides the classic `/sys/kernel/debug/usb/devices` or usbfs devices-style text view.

Risks: generated output can be truncated per device if descriptor text exceeds the scratch buffer. Holding `usb_bus_idr_lock` while traversing and locking devices makes lock ordering important. Serial numbers are included when `ALLOW_SERIAL_NUMBER` is defined, which has privacy implications. The recursive traversal must obey `MAX_TOPO_LEVEL`.

Test signals: read with multiple buses, nested hubs, devices disconnecting during read, many configurations/altsettings/endpoints, long strings, root hub bandwidth values, offset/partial reads, and topology depth limits.
