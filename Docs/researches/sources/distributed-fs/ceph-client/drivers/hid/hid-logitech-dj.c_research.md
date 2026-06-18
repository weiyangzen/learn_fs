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
