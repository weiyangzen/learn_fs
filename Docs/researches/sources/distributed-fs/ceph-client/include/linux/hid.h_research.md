# sources/distributed-fs/ceph-client/include/linux/hid.h

## Purpose
`hid.h` is the central kernel HID core interface. It defines HID descriptor item constants, usage IDs, quirk flags, device groups, parser state, report/field/usage structures, `struct hid_device`, driver callbacks, low-level transport callbacks, report parsing and I/O APIs, input mapping helpers, power/wakeup wrappers, and logging macros.

## Important APIs, Types, And Functions
Core types include `struct hid_item`, `struct hid_global`, `struct hid_local`, `struct hid_collection`, `struct hid_usage`, `struct hid_field`, `struct hid_report`, `struct hid_report_enum`, `struct hid_input`, `struct hid_battery`, `struct hid_device`, `struct hid_parser`, `struct hid_driver`, and `struct hid_ll_driver`. Driver registration uses `hid_register_driver()`, `hid_unregister_driver()`, and `module_hid_driver()`. Device/report APIs include `hid_add_device()`, `hid_destroy_device()`, `hid_parse_report()`, `hid_open_report()`, `hid_parse()`, `hid_connect()`, `hid_disconnect()`, `hid_input_report()`, `hid_safe_input_report()`, `hid_hw_start()`, `hid_hw_stop()`, `hid_hw_open()`, `hid_hw_close()`, `hid_hw_raw_request()`, `hid_hw_output_report()`, and `hid_report_raw_event()`.

## Control Flow And State
Low-level bus drivers allocate a `hid_device`, attach a `hid_ll_driver`, parse or provide a report descriptor, add the device, and start hardware. HID core parses descriptor items into collections, reports, fields, and usages. Matching HID drivers bind through ID tables and callbacks. Input reports flow from transport to BPF hooks, hidraw/hiddev/debug, raw driver events, parsed fields/usages, and input devices. Output/feature requests flow from core/hidraw/drivers down through low-level callbacks. State is held in parsed descriptor arrays, report ID hashes, input list, claimed flags, status/quirks bits, low-level open count and lock, driver data, debugfs state, batteries, hidraw/hiddev pointers, and optional HID-BPF data.

## Dependencies And Integration Points
The header depends on input, workqueue, mutex/semaphore, power_supply, uapi HID, and `hid_bpf.h`. It integrates USB, Bluetooth, I2C, SPI, hidraw, hiddev, input, force feedback, debugfs, power management, BPF, and module/device-driver infrastructure.

## Risks
Risks are high because this is shared ABI inside the kernel. Descriptor parser bounds (`HID_MAX_USAGES`, `HID_MAX_FIELDS`, `HID_MAX_IDS`), report buffer sizing, report ID handling, quirk semantics, BPF recursion/source tracking, lock ordering around `driver_input_lock`, and input mapping bounds all need careful validation. Driver hooks have nuanced return conventions. `report_fixup()` lifetime rules are easy to violate.

## Test Signals
Test with descriptor fuzzing, hid-tools/selftests, USB/Bluetooth/I2C/SPI devices, hidraw userspace, hiddev when enabled, BPF attach paths, input mapping edge cases, battery reports, suspend/resume/reset_resume, force feedback, quirk matching, disconnect during open, and high report ID/count limits.
