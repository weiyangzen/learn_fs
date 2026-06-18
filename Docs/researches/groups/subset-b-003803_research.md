# subset-b-003803 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-logitech-dj.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-logitech-dj.c

## Purpose

`hid-logitech-dj.c` is the receiver-side HID driver for Logitech Unifying, DJ, Lightspeed, Bluetooth proxy, 27 MHz, and related multi-interface receivers. Its core job is to turn one physical receiver with multiple transport interfaces and several paired devices into per-device virtual HID children. It listens for DJ and HID++ receiver notifications, creates or destroys virtual `hid_device` instances for paired devices, synthesizes report descriptors for those children, and routes input, output, and HID++ traffic between child devices and the physical receiver.

## Important APIs, Types, and Functions

- `enum recvr_type` classifies receiver families, including classic DJ, HID++ only, gaming HID++, Lightspeed 1.3, mouse-only, 27 MHz, Bluetooth proxy, and Dinovo.
- `struct dj_receiver_dev` is the shared receiver object across related USB interfaces. It stores interface pointers (`mouse`, `keyboard`, `hidpp`), a `paired_dj_devices[]` table, a `kref`, a notification FIFO, work item, spinlock, readiness flags, receiver type, and unnumbered application state.
- `struct dj_device` is each virtual child device and carries the child `hid_device`, backpointer to the receiver, supported report bitmask, and receiver slot index.
- `struct dj_workitem` is the deferred unit used to handle pair, unpair, empty-list, and unknown-device recovery outside atomic raw-event context.
- `dj_get_receiver_dev`, `dj_find_receiver_dev`, `dj_put_receiver_dev`, and `dj_release_receiver_dev` maintain the global receiver list and reference count for multi-interface receivers.
- `logi_dj_recv_add_djhid_device` and `logi_dj_recv_destroy_djhid_device` create and remove virtual HID children with the custom low-level driver `logi_dj_ll_driver`.
- `logi_dj_ll_parse`, `logi_dj_ll_raw_request`, and `logi_dj_ll_may_wakeup` implement the virtual child's low-level HID operations.
- `logi_dj_raw_event`, `logi_dj_dj_event`, and `logi_dj_hidpp_event` parse physical receiver input reports and route them to notification handling, virtual input reports, or hidraw pass-through.
- `logi_dj_recv_switch_to_dj_mode`, `logi_dj_recv_query_paired_devices`, and `logi_dj_recv_query_hidpp_devices` initialize receiver mode and enumerate paired devices.
- The static descriptor arrays (`kbd_descriptor`, mouse variants, consumer/system/media, and `hidpp_descriptor`) are concatenated according to `reports_supported` to describe each child device.

## Control Flow

Probe starts with `hid_parse`, rejects KVM-created extra interfaces based on expected interface count, validates the DJ short output report shape when present, and checks for HID++ application collections. Related interfaces are merged under one `dj_receiver_dev` by comparing physical device paths. The first HID++ capable interface enables DJ/HID++ notifications with `logi_dj_recv_switch_to_dj_mode`, opens the hardware endpoint, starts I/O, marks the receiver ready, and queries paired devices.

Incoming reports enter `logi_dj_raw_event`. Unnumbered keyboard and mouse proxy reports are normalized by prepending or replacing a report ID, then routed to the virtual child that supports that report. Numbered DJ short/long reports go to `logi_dj_dj_event`; HID++ short/long reports go to `logi_dj_hidpp_event`; other numbered reports are forwarded by report ID. Pairing, unpairing, connection-status, and unknown-device cases enqueue `dj_workitem`s into `notif_fifo` under the receiver spinlock. `delayedwork_callback` later consumes FIFO entries and creates children, destroys children, or re-queries paired devices.

When a child is created, `logi_dj_ll_parse` builds a synthetic HID report descriptor by concatenating the pieces implied by the work item's report bitmask and receiver type. Child outbound HID++ requests are rewritten in `logi_dj_ll_raw_request` so the receiver slot index is set correctly, with a special pairing-information exception. LED output requests either go through the keyboard interface for non-DJ receiver families or are wrapped into a DJ output report for classic DJ receivers.

## State and Persistence Behavior

The persistent state is the shared `dj_receiver_dev` plus its virtual child devices. `kref` protects receiver lifetime across interfaces, `dj_hdev_list_lock` protects the global receiver list and interface pointer updates, and `djrcv_dev->lock` protects the child table, readiness flag, and notification FIFO. `last_query` rate-limits recovery queries when reports arrive for unknown children. `dj_mode` records whether switch/configuration commands succeeded.

Virtual child devices persist until an unpair work item, receiver removal, or probe failure path destroys them. On removal from any required receiver interface, the driver clears `ready`, cancels work, closes/stops the physical HID device, and destroys all paired virtual children because proper routing requires all receiver interfaces. The driver does not persist state across unplug or reset; resume only reissues switch-to-DJ-mode for the HID++ interface.

## Dependencies and Integration Points

This file integrates with the HID core through `struct hid_driver` callbacks (`probe`, `remove`, `raw_event`, `reset_resume`) and with virtual children through `struct hid_ll_driver`. It uses HID core APIs including `hid_parse`, `hid_hw_start`, `hid_hw_open`, `hid_device_io_start`, `hid_input_report`, `hid_report_raw_event`, `hid_allocate_device`, `hid_add_device`, and `hid_destroy_device`.

Receiver identity comes from `hid-ids.h`, USB interface metadata, HID applications, HID groups (`HID_GROUP_LOGITECH_DJ_DEVICE`, `HID_GROUP_LOGITECH_27MHZ_DEVICE`), and receiver product IDs. The file also depends on `kfifo`, workqueues, spinlocks, mutexes, `kref`, jiffies, unaligned little-endian helpers, and USB path comparison helpers. It hands created HID++ children to `hid-logitech-hidpp.c` by assigning Logitech HID groups and adding HID++ report descriptors.

## Risks and Edge Cases

- The shared receiver object spans multiple interfaces, so ordering matters. Work can be queued before the HID++ interface is bound; the `ready` guard prevents processing but can defer expected pairing state until later reports or queries.
- `notif_fifo` insertions do not check return length. If more than `DJ_MAX_NUMBER_NOTIFS` work items are queued, notifications can be dropped silently.
- Unknown-device recovery is rate-limited to two queries per second. This avoids storms but can delay child creation when receivers or KVMs drop pairing notifications.
- Several paths depend on receiver-specific packet sizes and report IDs. New receiver firmware that changes report layouts can cause reports to be ignored or misrouted.
- `logi_dj_ll_raw_request` mutates the caller's HID++ buffer to set device indices. Callers expecting the original buffer after failure need to tolerate that change.
- Child descriptor construction assumes `MAX_RDESC_SIZE` remains large enough for the selected largest descriptor combination.
- Classic DJ output uses `GFP_ATOMIC` because requests can originate from atomic paths; allocation failure returns `-ENOMEM` and drops the command.
- 27 MHz pairing does not always emit explicit unpair events, so replacement detection is based on HID++ connect reports and device IDs.

## Test Signals

Useful tests exercise multi-interface probe ordering, KVM extra-interface fallback, receiver switch/query failure tolerance, pair and unpair notifications, unknown report recovery, and removal while work is queued. Report routing tests should cover numbered DJ, numbered HID++, unnumbered keyboard, unnumbered mouse with 6/8/13 byte variants, LED output routing, and child HID++ pairing-information requests. Descriptor tests should verify the synthesized keyboard, mouse, Bluetooth, Lightspeed, 27 MHz, consumer, system, media, and HID++ descriptor combinations parse correctly. Runtime signals include correct virtual child creation under `/sys/bus/hid`, no stuck keys after link-loss null reports, hidraw still receiving receiver HID++ traffic, and no use-after-free or lockdep warnings during unplug, reset-resume, and concurrent pairing changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-logitech-dj.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-macally.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-macally.c

## Purpose

`hid-macally.c` is a narrowly scoped HID descriptor quirk driver for the Macally iKey keyboard. The keyboard advertises logical and usage maximum values of 101 even though its power key and equals key use usages 102 and 103. The driver patches those descriptor bytes before the HID core parses the report descriptor so the affected keys are accepted as valid inputs.

## Important APIs, Types, and Functions

- `macally_report_fixup(struct hid_device *hdev, __u8 *rdesc, unsigned int *rsize)` is the only behavioral hook. It checks for a descriptor of at least 60 bytes and two known byte values at offsets 53 and 59.
- `macally_id_table` matches `USB_VENDOR_ID_SOLID_YEAR` plus `USB_DEVICE_ID_MACALLY_IKEY_KEYBOARD` from `hid-ids.h`.
- `macally_driver` registers the `.report_fixup` callback with the HID core.
- `module_hid_driver(macally_driver)` supplies module initialization and exit boilerplate.

## Control Flow

When the HID core probes a matching USB device, it invokes the driver's report fixup before normal descriptor parsing. If the descriptor has the expected shape, the driver logs an informational message and changes both maximum bytes from `0x65` to `0x67`. It always returns the descriptor pointer, either modified in place or unchanged. There are no input callbacks, raw-event handlers, or runtime control paths.

## State and Persistence Behavior

The file maintains no per-device state and allocates no memory. The only persistent effect is that the HID core parses the patched descriptor for the lifetime of that device instance. There is no sysfs state, module parameter, delayed work, or reconnect-specific behavior.

## Dependencies and Integration Points

The driver depends on the HID core report-fixup mechanism, module registration helpers, and the USB vendor/product IDs in `hid-ids.h`. Its output is consumed by generic HID input parsing and downstream input handling. It deliberately relies on exact descriptor offsets rather than implementing a descriptor parser.

## Risks and Edge Cases

- The fixup is offset-specific. A firmware revision with the same IDs but a shifted descriptor would not be patched, or could be patched incorrectly if those offsets coincidentally contain `0x65`.
- The guard checks only descriptor size and two byte values. It does not verify the surrounding HID item structure.
- Because the patch is in-place, callers must provide a mutable descriptor buffer, as expected by HID report fixup.
- No runtime validation confirms that the power and equals keys work after parsing.

## Test Signals

Tests should attach or emulate the Macally iKey descriptor and verify that offsets 53 and 59 become `0x67`, that descriptors shorter than 60 bytes are left unchanged, and that nonmatching descriptors with different values are untouched. Integration signals are successful HID parsing, expected key events for usages 102 and 103, and no regressions for unrelated Solid Year devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-macally.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-magicmouse.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-magicmouse.c

## Purpose

`hid-magicmouse.c` is the Apple Magic Mouse and Magic Trackpad HID driver. It switches supported Apple devices into multitouch mode, decodes proprietary touch reports, reports multitouch slots and pointer/button events through the input subsystem, emulates middle button and scroll wheel behavior for Magic Mouse devices, normalizes trackpad input capabilities, and polls USB Magic Mouse 2 and Magic Trackpad 2 battery reports when needed.

## Important APIs, Types, and Functions

- Module parameters control behavior: `emulate_3button`, `emulate_scroll_wheel`, `scroll_speed`, `scroll_acceleration`, and `report_undeciphered`.
- `struct magicmouse_sc` is the per-device state. It stores the input device, touch count, scroll acceleration and timing, per-tracking-ID touch/scroll state, raw tracking IDs, HID device pointer, delayed multitouch work, and USB battery timer.
- `magicmouse_emit_touch` decodes raw touch records for Magic Mouse, Magic Mouse 2, Magic Trackpad, and Magic Trackpad 2 formats, updates tracking state, emits multitouch ABS events, and optionally synthesizes scroll wheel events.
- `magicmouse_emit_buttons` applies three-button emulation based on existing button state and the position of the single firm touch.
- `magicmouse_raw_event` validates report sizes, handles mouse, trackpad, mouse2, trackpad2 USB/Bluetooth, and double-report packets, then emits relative motion, buttons, multitouch frames, and input sync.
- `magicmouse_setup_input`, `magicmouse_input_mapping`, and `magicmouse_input_configured` reshape hidinput capabilities for mice and trackpads.
- `magicmouse_enable_multitouch` sends feature reports needed to enable touch data for each transport and product family; `magicmouse_enable_mt_work` retries one problematic Magic Mouse 2 case.
- `magicmouse_fetch_battery` and `magicmouse_battery_timer_tick` request USB battery reports under `CONFIG_HID_BATTERY_STRENGTH`.
- `magicmouse_report_fixup` adjusts USB Magic Mouse 2 and Magic Trackpad 2 battery descriptors so they expose a Generic Desktop Mouse usage instead of a vendor usage.

## Control Flow

Probe allocates `magicmouse_sc` with devm, initializes scroll acceleration, stores driver data, parses the HID descriptor, and starts hardware. USB Magic Mouse 2 and Magic Trackpad 2 devices set up a timer that periodically fetches battery reports. Some USB devices return early after generic hidinput setup because they expose their multitouch-capable input differently. Other devices ensure an input node was configured, register the proprietary touch report IDs, set a nominal report size, and send the feature report that enables multitouch data. If Magic Mouse 2 returns `-EIO` for the enable command, a delayed retry is scheduled because that error is treated as a known device behavior.

Raw input is the main runtime path. Each supported report ID has strict size and alignment checks before touch records are decoded. `DOUBLE_REPORT_ID` recursively processes two embedded reports after validating the embedded length. For mouse products, touch state is decoded before clicks so middle/right/left emulation can use current finger position; relative motion and click state are reported afterward. Trackpad products report buttonpad state and multitouch frames, using pointer emulation for the first-generation trackpad and tracked multitouch for Trackpad 2.

Input setup clears unwanted buttons and relative axes for trackpads, sets buttonpad properties, initializes 16 multitouch slots, configures per-product coordinate ranges and resolutions, exposes pressure where available, adds high-resolution wheel axes for scroll emulation, optionally enables raw MSC reporting for unknown touch-state bits, and disables autorepeat.

## State and Persistence Behavior

Per-device touch and scroll state persists in `magicmouse_sc` across reports. Each tracking ID stores the last coordinate, touch size, scroll anchors, high-resolution scroll anchors, and active-axis flags. `ntouches` is reset for each report and counts current down touches. `scroll_accel` and `scroll_jiffies` persist across scroll gestures to implement optional accelerated scrolling and reset behavior. Button state is read from the input device key bitmap so emulation can keep an existing button held until release.

The delayed multitouch work and battery timer persist until remove or probe failure cleanup. Remove cancels delayed work, deletes the battery timer for USB Magic Mouse 2 and Trackpad 2 devices, and stops HID hardware. Module parameters are global and affect all matching devices while the module is loaded.

## Dependencies and Integration Points

The driver integrates with HID report parsing, report fixup, raw-event callbacks, input mapping/configuration, feature reports, and HID battery infrastructure. It uses the input multitouch helper API, relative and absolute input events, workqueues, timers, jiffies, module parameters, and Apple IDs from `hid-ids.h`. It exposes normal Linux input devices and, when configured, battery state through the HID battery layer. Its descriptor fixup affects how the HID core sees battery-capable USB devices before input setup.

## Risks and Edge Cases

- Proprietary report decoding relies on packed bit extraction and fixed offsets. Incorrect size validation or a new Apple report format can produce wrong coordinates, IDs, or button state.
- `MOUSE2_REPORT_ID` allows size 8, but computes `npoints = (size - 14) / 8`; integer division makes this zero for size 8, which is intentional but easy to misread.
- Recursive double-report handling must reject short or inconsistent embedded lengths to avoid out-of-bounds reads; the current code performs those checks.
- Scroll speed is constrained to 0..63 to avoid divide-by-zero from `(64 - scroll_speed)`.
- Middle-button emulation depends on the single firm touch heuristic and x thresholds; unusual hand posture can produce unexpected button choices.
- USB battery polling only runs when HID battery support is enabled and only for selected USB products.
- The descriptor fixup shifts the descriptor pointer by one byte and reduces size, which is unusual and should be tested against descriptor ownership assumptions.

## Test Signals

Raw-report tests should cover each report ID, invalid sizes, maximum 15 touch points, double-report recursion, no-touch reports, and per-device coordinate decoding. Input tests should verify Magic Mouse left/right/middle emulation, scroll and high-resolution scroll emission, trackpad buttonpad behavior, multitouch slot lifetimes, pressure on Trackpad 2, and suppression of default Magic Mouse 2 hidinput button handling. Configuration tests should cover module parameter changes, feature-report failures including the Magic Mouse 2 `-EIO` retry path, battery timer setup/removal, and descriptor fixup for USB Magic Mouse 2 and Magic Trackpad 2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-magicmouse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-maltron.c -->
# sources/distributed-fs/ceph-client/drivers/hid/hid-maltron.c

## Purpose

`hid-maltron.c` is a descriptor replacement driver for the Maltron L90 keyboard. The original USB report descriptor is malformed for media-key handling because the consumer-control report lacks explicit logical bounds. This driver recognizes the exact buggy descriptor and replaces it with a patched descriptor that adds logical minimum and maximum items for report ID 3, allowing consumer/media key events to be accepted as valid HID input.

## Important APIs, Types, and Functions

- `maltron_rdesc_o` is the exact original descriptor expected from the device. It includes system-control, consumer-control, and vendor-defined collections.
- `maltron_rdesc` is the replacement descriptor. It is mostly identical but inserts logical minimum `0` and logical maximum `32767` into the consumer-control collection before report count and report size.
- `maltron_report_fixup(struct hid_device *hdev, __u8 *rdesc, unsigned int *rsize)` compares the incoming descriptor size and bytes against `maltron_rdesc_o`; on exact match it returns `maltron_rdesc` and updates `*rsize`.
- `maltron_devices` matches the Alcor/Maltron keyboard USB ID from `hid-ids.h`.
- `maltron_driver` registers only `.report_fixup`.

## Control Flow

During HID probe for the matching device, the HID core calls `maltron_report_fixup` before parsing. The function performs a strict size and `memcmp` check against the known bad descriptor. If it matches, the driver logs that it is replacing the descriptor, changes the descriptor size to the patched descriptor length, and returns the static patched descriptor. If it does not match, the original descriptor pointer is returned unchanged.

There are no raw input handlers or output paths. After descriptor replacement, normal HID input parsing and event delivery are handled by the HID core and generic input layer.

## State and Persistence Behavior

The driver maintains no mutable per-device state and allocates no memory. The only persistent effect is the HID core parsing the returned static descriptor for that device instance. The original device firmware is not modified, and there is no state persisted across unplug or module reload.

## Dependencies and Integration Points

This file depends on HID report fixup, module registration helpers, standard device ID matching, and `memcmp`. It integrates indirectly with generic HID input handling by making the descriptor acceptable to the parser. The descriptor contents define system sleep/wake, consumer control, vendor-defined feature/output reports, and LED outputs, but this driver only patches descriptor metadata.

## Risks and Edge Cases

- The fix applies only to an exact descriptor byte sequence. Any firmware revision with a near-identical but not byte-identical descriptor will bypass the fix.
- Returning a static descriptor is safe for parsing but must remain immutable; no later code should attempt to modify the returned pointer in place.
- The replacement descriptor length differs from the original because logical bounds are inserted. Consumers must use the updated `*rsize`.
- Because the driver is ID-specific and exact-match specific, it has low blast radius but can miss compatible variants.

## Test Signals

Tests should feed the exact `maltron_rdesc_o` and verify that `maltron_report_fixup` returns `maltron_rdesc`, updates the size, and preserves all nonpatched collections. Negative tests should cover wrong size and one-byte descriptor mismatches. Integration signals are successful HID parsing, working media keys from report ID 3, preserved system sleep/wake behavior, and no changes for unrelated Alcor devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/hid-maltron.c -->
