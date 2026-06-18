# sources/distributed-fs/ceph-client/drivers/hid/hid-multitouch.c

## Purpose

`hid-multitouch.c` is the generic HID multitouch driver for a large range of USB, I2C, Bluetooth, and Win8-certified touchscreens/touchpads. It converts HID digitizer descriptors and reports into Linux input-mt slot events, applies extensive device-class quirks, sets HID feature modes such as input mode/latency/contact reporting, supports haptic touchpads, and maintains a broad VID/PID match table for devices that need non-default behavior.

## Important APIs, Types, and Functions

- `struct mt_class` describes class-level quirks, signal/noise ratios, maximum contacts, direct/indirect behavior, and whether non-touch inputs should be exported.
- `struct mt_device` is per-HID-device state: selected class, release timer, haptic state, maximum contacts, input mode, buttonpad/pressurepad/haptic flags, serial detection, application list, report list, and `mt_io_flags`.
- `struct mt_application` tracks one HID application/report identity, per-contact usage list, quirks, scan time/contact count pointers, expected/received contacts, button aggregation, palm-release bitmap, timestamp state, and input-mt flags.
- `struct mt_usages` stores pointers to HID field values for one contact slot: coordinates, tool size, pressure, azimuth, contact ID, tip, in-range, and confidence.
- Parsing helpers allocate/find applications and reports, store field pointers, fetch feature reports, and map HID usages (`mt_feature_mapping()`, `mt_touch_input_mapping()`, `mt_input_mapping()`).
- Runtime handlers `mt_report()`, `mt_touch_report()`, `mt_process_slot()`, `mt_sync_frame()`, and `mt_expired_timeout()` convert full HID reports into input events and release sticky contacts.
- Mode/power helpers `mt_set_modes()`, `mt_need_to_apply_feature()`, `mt_suspend()`, `mt_resume()`, `mt_reset_resume()`, `mt_on_hid_hw_open()`, and `mt_on_hid_hw_close()` program feature reports.
- `mt_probe()` selects a class, sets HID quirks, parses/starts hardware, creates sysfs `quirks`, and initializes haptics.

## Control Flow

Probe chooses a class from `id->driver_data`, allocates `mt_device` and haptic storage, sets default touchscreen input mode, forces HID no-input-sync and per-application input handling, optionally forces multi-input behavior, parses the descriptor, applies descriptor/constant-field fixes, starts HID, creates the quirks sysfs group, and sends normal latency/all-report feature settings.

During descriptor parsing, `mt_feature_mapping()` reads contact max/button type/inputmode-related features and haptic features. `mt_input_mapping()` creates report/application bookkeeping and either maps multitouch collections itself or lets hid-input handle non-touch collections when allowed. Repeated HID usage fields are grouped into `mt_usages` records representing contacts.

At runtime, `.event` consumes individual events for multitouch collections, and `.report` processes whole reports. `mt_touch_report()` computes timestamps and expected contact count, processes every stored contact through `mt_process_slot()`, forwards non-touch events such as buttons, syncs when expected contacts have arrived, and manages a timer for sticky-finger release. Slot selection depends on class quirks: contact ID, contact number, Cypress special rules, minus-one IDs, or input-mt key lookup.

## State and Persistence Behavior

All state is runtime per HID device. The class quirks can be read and overwritten through the `quirks` sysfs attribute, which updates each application and drops contact-count accuracy when unavailable. Applications persist across parsed reports and retain pointers into HID field values. `mt_io_flags` contains a running bit lock and low bits for active slots. Feature-mode settings are written to the device on probe/open/close/suspend/resume but are not stored by this driver beyond `inputmode_value`.

## Dependencies and Integration Points

The file integrates deeply with HID core callbacks (`probe`, `remove`, `report_fixup`, `feature_mapping`, `input_mapping`, `input_mapped`, `input_configured`, `event`, `report`, PM/open/close), Linux input-mt, timers, sysfs attributes, haptic support from `hid-haptic.h`, and many vendor/product constants from `hid-ids.h`. Its comments explicitly call out hid-tools regression tests as an expected validation path.

## Risks and Edge Cases

- The quirk matrix is large; changing default class behavior can affect many devices.
- `mt_probe()` overwrites `td->mtclass.quirks` with only `MT_QUIRK_ORIENTATION_INVERT` when one axis is inverted, rather than OR-ing it with existing class quirks; this is a subtle behavior worth review.
- Contact processing relies on descriptor-time pointers into HID field values and assumptions about report ordering.
- Sticky-finger timer and report processing coordinate through bit locks; missed unlocks or long report handlers could suppress releases.
- Feature report writes are best-effort and often ignore return values, so devices may remain in unexpected modes.
- Sysfs quirk writes can alter live parsing behavior without reinitializing slots or input capabilities.

## Test Signals

Run hid-tools regression suites for known multitouch devices. Add targeted tests for descriptor mapping, contact ID/contact number slot selection, duplicate suppression, confidence/in-range/tip validity, Win8 button aggregation, timestamp wrap/resync, sticky-finger release timer, feature-mode programming, haptic pressure integration, Goodix descriptor fixup, Yoga Book report filtering/naming, sysfs quirk writes, suspend/resume/open/close mode changes, and representative entries from the device table.
