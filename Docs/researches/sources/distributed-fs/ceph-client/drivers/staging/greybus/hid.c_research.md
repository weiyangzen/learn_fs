# sources/distributed-fs/ceph-client/drivers/staging/greybus/hid.c

## Purpose
Greybus HID class driver. It binds HID-class Greybus bundles and presents the remote HID device through the Linux HID low-level driver interface.

## Important APIs, Types, And Functions
`struct gb_hid` stores bundle, connection, Linux `hid_device`, Greybus HID descriptor, flags, and input buffer. Protocol helpers fetch HID descriptor/report descriptor, set power, get report, and set report. `gb_hid_ll_driver` supplies HID callbacks: parse, start, stop, open, close, power, and raw_request. `gb_hid_request_handler()` receives input report IRQ events.

## Control Flow
Probe requires exactly one HID CPort, creates/enables the connection, allocates a HID device, reads the Greybus HID descriptor, initializes HID identity and low-level callbacks, adds the HID device, and drops runtime PM. HID parse fetches and parses the report descriptor. Start allocates a maximum report buffer and initializes reports unless quirked. Open powers on and marks started; close clears started and powers off. IRQ events feed input reports only while started.

## State And Persistence
State is in-memory: descriptor cache, started flag, buffer size/input buffer, and Linux HID device state. Power state is requested over Greybus and not persisted locally beyond flags.

## Dependencies And Integration Points
Uses Greybus HID protocol, Greybus runtime PM, Linux HID core, HID report parsing, and bundle class matching through `GREYBUS_CLASS_HID`.

## Risks
`gb_hid_request_handler()` assumes payload contains an input report and does not explicitly size-check beyond operation payload. `__gb_hid_output_raw_report()` currently returns `0` after set-report instead of the adjusted transfer length, which is a behavioral concern. Runtime PM wraps descriptor/report/power operations.

## Test Signals
Test descriptor size bounds, report descriptor parsing failure, report get/set paths, numbered and unnumbered reports, IRQ event before/after open, power transitions, disconnect while open, and raw_request return values.
