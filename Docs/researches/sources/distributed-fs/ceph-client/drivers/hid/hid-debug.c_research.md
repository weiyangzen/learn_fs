# sources/distributed-fs/ceph-client/drivers/hid/hid-debug.c

## Purpose
`hid-debug.c` provides HID debugfs support and exported formatting helpers used to inspect HID report descriptors, parsed report fields, input mappings, raw reports, and live input values. Most of the file is static lookup data: HID usage names and Linux input event/code names that make debug output readable.

## Important APIs, Types, And Functions
`hid_debug_root` is the debugfs root dentry for `/sys/kernel/debug/hid`. `struct hid_usage_entry` and `hid_usage_table[]` map HID usage pages/usages to descriptions. `resolv_usage_page()` and exported `hid_resolv_usage()` convert numeric HID usages into text, either directly into a `seq_file` or into an allocated buffer for event FIFO use. Exported `hid_dump_field()` and `hid_dump_device()` print parsed HID report structure. Exported `hid_debug_event()`, `hid_dump_report()`, and `hid_dump_input()` enqueue live debug text into per-reader FIFOs. The event-name arrays (`events`, `keys`, `relatives`, `absolutes`, `misc`, `leds`, `repeats`, `sounds`, `software`, `force`, `force_status`, and `names`) back `hid_resolv_event()` and `hid_dump_input_mapping()`.

The debugfs file operations are `hid_debug_rdesc_show()` for one-shot descriptor and mapping dumps, plus `hid_debug_events_open()`, `hid_debug_events_read()`, `hid_debug_events_poll()`, and `hid_debug_events_release()` for blocking live event reads. `hid_debug_register()`, `hid_debug_unregister()`, `hid_debug_init()`, and `hid_debug_exit()` create and remove debugfs entries.

## Control Flow
During HID subsystem initialization, `hid_debug_init()` creates the root debugfs directory. Each HID device calls `hid_debug_register()`, which creates a per-device directory containing `rdesc` and `events` files and sets `hdev->debug`. Reading `rdesc` prints raw descriptor bytes, then takes `driver_input_lock`, dumps parsed reports/fields, and dumps HID-to-input mappings.

Opening `events` allocates a `hid_debug_list`, allocates a FIFO, takes a reference on the HID device, initializes the read mutex, and links the reader into `hdev->debug_list` under `debug_list_lock`. Producers call `hid_debug_event()` or the higher-level dump helpers, which push text into every reader FIFO and wake `debug_wait`. Reads block unless data is available, a signal arrives, nonblocking mode is set, or the device is unregistered. Release unlinks the reader, frees the FIFO, drops the HID device reference through `hiddev_free`, and frees the list.

## State And Persistence
State is entirely runtime/debug state: debugfs dentries on each HID device, per-reader FIFOs, per-reader mutexes, the device `debug_list`, and wait queues. No device configuration or persistent kernel state is changed. The resolver allocates temporary buffers with `GFP_ATOMIC` in event paths so it can be called from contexts where sleeping is not allowed.

## Dependencies And Integration Points
The file depends on debugfs, seq_file, kfifo, poll, wait queues, spinlocks, krefs, HID core structures, and Linux input code constants. Other HID code uses the exported resolver and dump functions to produce debug output. User space integrates by reading `/sys/kernel/debug/hid/<device>/rdesc` for static state or `/sys/kernel/debug/hid/<device>/events` for live event streams.

## Risks
Large static name tables must track kernel input and HID usage definitions; missing entries degrade readability but do not break device operation. FIFO writes happen for every debug reader, so heavy debug use can add overhead and drop text if FIFOs fill. The read path explicitly handles races with unregister, but lifetime and wakeup ordering remain delicate because readers can block while devices are being removed. Formatting helpers that allocate buffers in atomic context can fail and return reduced debug output.

## Test Signals
Build coverage should catch stale input constants. Runtime validation includes debugfs root creation, per-device `rdesc` content showing raw bytes plus parsed fields, `events` blocking and waking on HID input, poll returning readable data or hangup on unregister, nonblocking reads returning `-EAGAIN`, signal interruption returning `-ERESTARTSYS`, and clean removal while `events` is open.
