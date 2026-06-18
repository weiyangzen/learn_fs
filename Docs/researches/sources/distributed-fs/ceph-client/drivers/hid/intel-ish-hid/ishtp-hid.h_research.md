<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp-hid.h -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp-hid.h

## Purpose
`ishtp-hid.h` defines the hostif HID-over-ISH protocol structures, command constants, per-client/per-HID state containers, trace macro, and cross-file function prototypes shared by the ISHTP HID client and hid-core glue.

## Important APIs, Types, and Functions
Constants define fixed ISH HID VID/PID/version, command mask/response bit, hostif command IDs, and `MAX_HID_DEVICES`. Packed ABI structs include `hostif_msg_hdr`, `hostif_msg`, `hostif_msg_to_sensor`, `device_info`, `ishtp_version`, `report`, and `report_list`. `struct ishtp_cl_data` stores enumeration flags, descriptors, HID device pointers, waitqueues, counters, work items, and the ISHTP client device. `struct ishtp_hid_data` stores per-HID request state and raw request buffers.

## Control Flow
The header has no executable flow. `ishtp-hid-client.c` fills `ishtp_cl_data`, parses hostif messages, and calls functions declared here. `ishtp-hid.c` uses the same state to register hid devices and implement hid-core callbacks.

## State and Persistence Behavior
The structures define persistent runtime ownership: client-level state survives across HID device registration and reset work, while HID-level state survives until HID removal. Report descriptors and HID descriptors are indexed by firmware enumeration order.

## Dependencies and Integration Points
It depends on HID and ISHTP client types being visible to including C files. The hostif packed structs are an ABI with ISH firmware and must match firmware layout exactly.

## Risks and Edge Cases
`MAX_HID_DEVICES` is 32, but client code must explicitly validate firmware counts before indexing arrays. The trace macro calls the function pointer unconditionally; if `ishtp_hid_print_trace` is unset, it can fail. Packed layout and field widths are firmware-sensitive. Aggregated report structs contain flexible arrays and require byte-wise walking by consumers.

## Test Signals
Build both C files against this header, validate hostif struct sizes against firmware documentation, test firmware enumeration counts at boundaries, and verify command IDs and response-bit handling with real or mocked firmware messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/ishtp-hid.h -->
