# sources/distributed-fs/ceph-client/drivers/hid/hid-rapoo.c

## Purpose

`hid-rapoo.c` adds a small companion input device for Rapoo 2.4 GHz receivers so side-button bits in a vendor-specific raw report are exposed as standard `KEY_BACK` and `KEY_FORWARD` events.

## Important APIs, Types, and Functions

- `rapoo_devices[]`: matches `USB_VENDOR_ID_RAPOO` / `USB_DEVICE_ID_RAPOO_2_4G_RECEIVER`.
- `rapoo_probe()`: parses and starts HID, then allocates/registers a managed input device for USB interface number 1.
- `rapoo_raw_event()`: intercepts report ID 1, reads `data[1]`, maps `0x08` to `KEY_BACK` and `0x10` to `KEY_FORWARD`, syncs the input device, and consumes the report.
- `RAPOO_BTN_BACK` and `RAPOO_BTN_FORWARD`: bit masks for the vendor report byte.

## Control Flow

Probe runs `hid_parse()` and `hid_hw_start()` for every matched receiver. For USB devices, only interface 1 gets the extra input device; other interfaces keep normal HID handling with no driver data. On the active interface, the driver creates an input device named `Rapoo 2.4G Wireless Mouse`, sets bus/vendor/product/version metadata, advertises `EV_KEY`, `KEY_BACK`, and `KEY_FORWARD`, registers it, and stores it as HID driver data.

Raw event processing is intentionally narrow. If no input device was installed, the report is ignored by this driver. If the report ID is 1 and the buffer is at least two bytes, the side-button bits are reported and the function returns 1 so generic HID does not process the same vendor report.

## State and Persistence Behavior

The only persistent state is the devm-managed `struct input_dev` stored in HID driver data. Button state is not cached; each qualifying raw report emits current key states and an input sync. Device teardown relies on devm cleanup and HID core removal.

## Dependencies and Integration Points

The driver integrates with HID parse/start, USB interface metadata, and the Linux input subsystem. It depends on `hid-ids.h` for Rapoo IDs and on input key definitions from `linux/input-event-codes.h`.

## Risks and Edge Cases

- `rapoo_probe()` returns success early for non-interface-1 USB interfaces after `hid_hw_start()`, so those interfaces still rely on HID core lifetime management without driver-private state.
- A failure after `hid_hw_start()` during input allocation or registration returns an error without an explicit `hid_hw_stop()` in this file.
- The raw event assumes `data[1]` semantics for all matched receiver variants.
- Returning 1 consumes report ID 1, which is correct for the side-button vendor report but would be risky if future devices reuse the ID for normal input.

## Test Signals

Test with the matched receiver should show a second input node only on USB interface 1, no duplicate generic events for the side buttons, correct press/release transitions for back/forward, and normal operation of non-side-button interfaces. Error-path testing should cover input allocation/registration failure after `hid_hw_start()`.
