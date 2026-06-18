<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hid.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hid.h

## Purpose
`hid.h` defines common USB HID class constants exposed to userspace and shared by HID-related character-device APIs.

## Important APIs, types, and functions
Constants include `USB_INTERFACE_CLASS_HID`, boot subclass and keyboard/mouse protocol codes, descriptor type values `HID_DT_HID`, `HID_DT_REPORT`, and `HID_DT_PHYSICAL`, and `HID_MAX_DESCRIPTOR_SIZE`. `enum hid_report_type` names input, output, and feature reports in Linux's zero-based internal ordering. `enum hid_class_request` defines USB class requests such as `GET_REPORT`, `GET_IDLE`, `GET_PROTOCOL`, `SET_REPORT`, `SET_IDLE`, and `SET_PROTOCOL`.

## Control flow
The header has no executable flow. HID core, hidraw, and user tools use these constants when parsing report descriptors, issuing class requests, and bounding descriptor buffers.

## State and persistence behavior
HID protocol, idle, descriptors, and reports are device state managed by USB/HID drivers. The header only fixes numeric IDs and maximum descriptor size.

## Dependencies and integration points
It is included by `hidraw.h` and aligns with USB HID class definitions used by kernel HID core, hiddev, hidraw, and userspace HID libraries.

## Risks and test signals
Risks include confusion between Linux zero-based report type enum and HID specification report numbers, descriptor truncation at 4096 bytes, and missing USB type definitions in consumers. Test signals include hidraw descriptor reads, boot keyboard/mouse enumeration, class request handling, malformed descriptor rejection, and report type mapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hid.h -->
