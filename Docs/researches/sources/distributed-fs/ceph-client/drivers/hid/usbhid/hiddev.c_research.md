# sources/distributed-fs/ceph-client/drivers/hid/usbhid/hiddev.c

## Purpose

`hiddev.c` implements the legacy USB HID character-device interface exposed as `/dev/usb/hiddev*` / `hiddev%d`. It gives userspace access to HID report metadata, values, raw usage events, report GET/SET requests, strings, and device information for USB HID devices selected by HID core.

## Important APIs, Types, And Data

- `struct hiddev_list` is per-open-file state: a fixed 2048-entry ring of `struct hiddev_usage_ref`, head/tail indexes, per-open flags, fasync state, backpointer to `struct hiddev`, list linkage, and `thread_lock` to serialize readers on one file.
- `hiddev_lookup_report()` handles direct report IDs plus `HID_REPORT_ID_FIRST` and `HID_REPORT_ID_NEXT` iteration semantics.
- `hiddev_lookup_usage()` scans all reports of a type to find a usage code and fills in report, field, and usage indexes.
- `hiddev_hid_event()` is exported to HID core and translates individual field/usage/value events to `hiddev_usage_ref`.
- `hiddev_report_event()` generates report-level events with `HID_FIELD_INDEX_NONE`.
- `hiddev_read()`, `hiddev_poll()`, `hiddev_ioctl()`, `hiddev_open()`, `hiddev_release()`, and `hiddev_fasync()` implement the character-device ABI.
- `hiddev_connect()` and `hiddev_disconnect()` are the HID core integration points.

## Control Flow

`hiddev_connect()` decides whether a device should expose hiddev. Unless forced, it requires at least one non-input application collection. It allocates `struct hiddev`, initializes wait queues, list lock and existence lock, stores it on `hid->hiddev`, registers the USB class device with `usb_register_dev()`, records the minor, and initializes the report state according to `HID_QUIRK_NO_INIT_REPORTS`.

Opening resolves the USB interface from the minor with `usbhid_find_interface()`, gets the `hid_device`, locks `existancelock`, and calls `__hiddev_open()` if the device still exists. The first opener powers the HID device to `PM_HINT_FULLON` and calls `hid_hw_open()`. Each opener gets a `hiddev_list` and is added to `hiddev->list`.

HID events arrive through `hiddev_hid_event()` and `hiddev_report_event()`. Both call `hiddev_send_event()`, which takes `hiddev->list_lock`, appends to every open file ring buffer if the event is eligible for that file's flags, sends async SIGIO, drops the lock, and wakes blocking readers.

Reads block while the per-open ring is empty unless the file is non-blocking, a signal is pending, or the device no longer exists. Data is returned either as old `struct hiddev_event` pairs or as full `struct hiddev_usage_ref` records when `HIDDEV_FLAG_UREF` is enabled.

`hiddev_ioctl()` supports version, application iteration, device info, flags, USB string retrieval, report initialization, GET/SET report requests, report/field/collection metadata, usage value get/set, multi-usage get/set, collection index lookup, and variable-length name/physical path reads.

Disconnect deregisters the USB class device, marks `exist` false under `existancelock`, closes HID hardware if files are still open, wakes readers, and defers freeing `struct hiddev` until the last release.

## State And Persistence Behavior

State is in memory and tied to a connected HID device. `struct hiddev` tracks existence, open count, initialized flag, minor, wait queue, and open-file list. Each open file has an independent event ring and flag set. The ring overwrites old entries when head wraps; there is no explicit overflow counter.

`hiddev->initialized` gates lazy `usbhid_init_reports()` calls. Report values are the live HID core `field->value[]` arrays; set-usage ioctls mutate those arrays and `HIDIOCSREPORT` sends them to hardware. No state persists across disconnect.

## Dependencies And Integration Points

- Depends on USB HID infrastructure through `usbhid_find_interface()`, `usbhid_init_reports()`, `struct usbhid_device`, `usb_register_dev()`, and `usb_deregister_dev()`.
- Depends on HID core report structures, `hid_hw_open()`, `hid_hw_close()`, `hid_hw_power()`, `hid_hw_request()`, and `hid_hw_wait()`.
- Exposes a userspace ABI from `<linux/hiddev.h>`.
- Uses `hid_to_usb_dev()` from `usbhid.h` and `array_index_nospec()` for user-provided indexes.

## Risks And Edge Cases

- Ring-buffer overflow silently drops the oldest unread events by wrapping `head`.
- `hiddev_send_event()` writes ring entries under `list_lock`, while `hiddev_read()` consumes using only per-list `thread_lock`.
- The API allows userspace to mutate output/feature field values before sending reports; validation is mostly bounds checking, not semantic validation.
- Disconnect races are mitigated by `existancelock`, open count, and wakeups, but open file operations must consistently check `exist`.

## Test Signals

- Userspace hiddev tests should open, poll, read both event formats, toggle `HIDDEV_FLAG_UREF`/`HIDDEV_FLAG_REPORT`, and verify fasync notifications.
- Ioctl tests should cover report iteration, invalid report types, invalid indexes, multi-usage bounds, GET/SET report restrictions, and `HIDIOCINITREPORT`.
- Disconnect tests with blocking readers should observe wakeup with `-EIO` or poll `EPOLLERR|EPOLLHUP`.
