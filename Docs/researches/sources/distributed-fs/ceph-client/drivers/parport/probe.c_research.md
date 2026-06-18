# sources/distributed-fs/ceph-client/drivers/parport/probe.c

Purpose: obtains and parses IEEE 1284 Device ID strings for devices attached to parport ports, filling `port->probe_info[]` and logging human-readable class/manufacturer/model information.

Important APIs/types/functions: `parport_device_id()` is the exported entry point. It opens a daisy device, claims the port, negotiates compatibility then nibble Device ID mode, calls `parport_read_device_id()`, restores compatibility mode, parses returned fields with `parse_data()`, and closes the pardevice. `classes[]` maps IEEE class tokens to parport class IDs and descriptions.

Control flow/state: `parport_read_device_id()` reads the two-byte length header, handles big-endian/little-endian and off-by-two broken devices by trying sorted candidate lengths, drains excess data when the caller buffer is too small, terminates the caller buffer, and reports short/malformed IDs. `parse_data()` tokenizes semicolon-separated key/value pairs, normalizes keys, stores dynamically allocated strings in `parport_device_info`, guesses printers from PJL/PCL command sets, and invokes `pretty_print()`.

Dependencies/integration: depends on parport open/claim/negotiate/read/release/close APIs, daisy-chain naming, kernel string helpers, and allocation APIs. Risks include malformed device IDs, memory churn when replacing probe strings, blocking while claiming the port, and reliance on device behavior during repeated reads. Test signals include successful `/proc/sys/dev/parport/.../autoprobe*` content, logs for class/model, malformed length handling, small-buffer behavior, and no leaks after repeated probes.
