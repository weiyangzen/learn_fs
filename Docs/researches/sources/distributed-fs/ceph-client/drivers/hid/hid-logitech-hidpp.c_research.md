<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-logitech-hidpp.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-logitech-hidpp.c

## Purpose

`hid-logitech-hidpp.c` is the HID++ protocol driver for Logitech devices reached over USB, Bluetooth, 27 MHz receivers, and virtual devices created by the DJ receiver driver. It implements the HID++ 1.0 register access protocol and HID++ 2.0 feature access protocol, then layers device naming, serial discovery, battery reporting, high-resolution scrolling, touchpad raw-mode handling, special keyboard and mouse quirks, wireless-status integration, and G920/G923 force feedback support on top of that transport.

## Important APIs, Types, and Functions

- `struct hidpp_report` models short, long, and very-long HID++ reports with a shared header and RAP/FAP payload union.
- `struct hidpp_device` is the per-device state object. It owns the HID device pointer, input pointer, synchronous send mutex and waitqueue, answer buffer state, protocol version, private class data, deferred connect work, reset-hi-res work, quirks, capability bits, supported report mask, battery state, scroll counter, wireless feature index, and connection history.
- `struct hidpp_battery` stores discovered battery feature indices, `power_supply_desc`, registered `power_supply`, exposed values, and supported unified-battery levels.
- `__hidpp_send_report`, `__do_hidpp_send_message_sync`, `hidpp_send_message_sync`, `hidpp_send_fap_command_sync`, and `hidpp_send_rap_command_sync` form the synchronous HID++ request/response transport.
- Protocol discovery and metadata helpers include `hidpp_root_get_protocol_version`, `hidpp_root_get_feature`, `hidpp_unifying_init`, `hidpp_non_unifying_init`, `hidpp_get_device_name`, and serial helpers for both Unifying and HID++ 2.0 device-info pages.
- Battery support spans HID++ 1.0 status/mileage registers and HID++ 2.0 pages `0x1000`, `0x1001`, `0x1004`, solar `0x4301`, and ADC `0x1f20`, all surfaced through `hidpp_initialize_battery` and `hidpp_battery_get_property`.
- Input and raw-event customization is handled by WTP touchpad helpers, M560 helpers, K400 tap-to-click helpers, Dinovo mapping, HID++ wheel/extra-button/consumer-key helpers, and generic high-resolution scroll conversion.
- Force feedback uses `struct hidpp_ff_private_data`, a single-thread workqueue, effect slot tracking, `hidpp_ff_upload_effect`, playback/erase/gain/autocenter callbacks, and G920 feature-page setup.
- Driver callbacks are `hidpp_probe`, `hidpp_remove`, `hidpp_report_fixup`, `hidpp_raw_event`, `hidpp_event`, `hidpp_input_configured`, `hidpp_input_mapping`, and `hidpp_input_mapped`.

## Control Flow

Probe allocates `struct hidpp_device` before parsing so descriptor fixups can see driver data. After `hid_parse`, `hidpp_validate_device` inspects output report definitions to confirm short, long, and optional very-long HID++ support. Non-HID++ devices are returned to generic HID handling. Known groups and product IDs add quirks, and class-specific private data is allocated for WTP or K400 devices.

The driver starts hardware without connecting subdrivers so it can open I/O and query protocol, name, and serial before hidinput or hidraw exposes the device to userspace. `hidpp_unifying_init` handles virtual DJ children; non-Unifying devices use HID++ 2.0 name and serial pages where available. It then connects HID subdrivers, starts I/O, runs `hidpp_connect_event`, and optionally initializes G920 force feedback. For delayed-init devices, the first successful connect event creates and registers an input device manually.

Synchronous commands lock `send_mutex`, copy the request shape into the response buffer, send the report, then wait up to five seconds for `hidpp_raw_hidpp_event` to match an answer or protocol error. Busy errors are retried up to three times. Raw HID++ input first satisfies any pending synchronous command, then handles connect events by scheduling work, battery events, high-resolution scroll reset on reconnect, HID++ 1.0 wheel events, extra mouse buttons, and consumer-key reports. Class raw handlers then process WTP or M560 packets if generic HID++ handling did not consume the report.

`hidpp_connect_event` is the main reconfiguration path after connect or reconnect. It verifies protocol presence, applies class setup such as WTP raw reports, M560 button mode, K400 tap-to-click, HID++ 1.0 report enables, discovers wireless status, updates names if delayed, initializes or refreshes battery state, enables high-resolution scrolling, and registers delayed input devices.

## State and Persistence Behavior

Most state persists for the HID device lifetime through devm-managed `hidpp_device` allocation. The send path is serialized with `send_mutex`, while asynchronous replies use `answer_available`, `send_receive_buf`, and `wait`. Battery state persists and is updated by both periodic queries during connect and spontaneous HID++ events; a registered `power_supply` exposes this state to sysfs and userspace. `usb_set_wireless_status` is updated for devices with the wireless-status quirk.

Input-specific state persists in `hidpp->input`, `hidpp->private_data`, the high-resolution scroll counter, and class-specific state such as WTP geometry and K400 feature index. Force feedback state is owned by input FF core after `hidpp_ff_init`: effect slots, gain, range, and the FF workqueue survive until FF destroy. On remove, the driver removes the sysfs group, stops hardware, cancels work items, and destroys the send mutex; devm allocations and power supply registration are device-managed.

## Dependencies and Integration Points

The file is deeply integrated with the HID core (`hid_parse`, `hid_hw_start`, `hid_hw_open`, `hid_connect`, raw events, usage tables, report fixup, input mapping/configuration), input core (`input_report_*`, multitouch slots, FF callbacks), power supply core, sysfs, USB helpers, workqueues, waitqueues, mutexes, atomics, `kfifo`, unaligned access helpers, fixed-point trig, and scheduler clock timing. It relies on `hid-ids.h`, Logitech HID groups from `hid-logitech-dj.c`, and `usbhid` behavior for output-report quirks. Userspace integrations include hidraw, input devices, force-feedback ioctls, power-supply sysfs, and the `builtin_power_supply` marker attribute.

## Risks and Edge Cases

- Synchronous command matching depends on `mutex_is_locked(&send_mutex)` and one outstanding request. Unexpected unsolicited packets matching the current request shape can complete the wait incorrectly.
- `hidpp_send_message_sync` retries busy errors only while response report IDs indicate expected protocol families; malformed responses can stop retries.
- Several battery pages return intermittent resource errors. The code intentionally ignores some cases, but devices can appear offline or battery-less until reconnect or a later event.
- Very-long report length is accepted from descriptors up to 64 bytes; all FAP parameter handling must stay within `sizeof(fap.params)`.
- Some feature helpers use positive protocol errors and transport errors differently. Callers must preserve the distinction or avoid treating protocol errors as Linux errno values.
- `hidpp10_consumer_keys_report_fixup` searches binary descriptors with `strnstr` against a NUL-terminated pattern; descriptor fragments containing embedded NUL before the match could make this fragile.
- Force-feedback commands are queued asynchronously and only warn when the queue grows; slow hardware can accumulate latency. Memory ownership moves to FF core and the workqueue must be destroyed only after queued work is no longer reachable.
- `hidpp_ff_init` can return `-ENOMEM` after `input_ff_create` succeeds if later allocations fail, which needs review against FF-core cleanup expectations.
- Device tables include overlapping product IDs and broad `HID_ANY_ID` Logitech groups; ordering and quirk selection matter.
- Delayed input creation must not race remove or repeated connect events; `delayed_input` is used as the guard.

## Test Signals

Transport tests should cover short, long, very-long, forced output report, timeout, busy retry, protocol error, and unsolicited event paths. Probe tests should verify fallback to generic HID when report lengths are insufficient, name and serial updates before `hid_connect`, and 27 MHz quirk assignment by application. Battery tests should cover HID++ 1.0 status/mileage, HID++ 2.0 battery level, voltage, unified battery, solar, ADC measurement, power-supply property exposure, reconnect offline/online transitions, and USB wireless status updates. Input tests should cover high-resolution scroll conversion and reset, WTP raw multitouch, M560 remapped buttons, K400 tap-to-click module parameter behavior, Dinovo vendor usage mapping, consumer-key descriptor fixup, extra mouse buttons, and delayed input registration. Force-feedback tests should exercise G920/G923 discovery, slot count, upload/play/stop/erase, autocenter, gain, range sysfs, queue drain, and remove while work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-logitech-hidpp.c -->
