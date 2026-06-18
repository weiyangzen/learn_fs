# sources/distributed-fs/ceph-client/drivers/hid/hidraw.c

## Purpose

`hidraw.c` implements the `/dev/hidrawN` character-device interface. It exposes raw HID reports to user-space without HID input translation, supports raw output and feature/input/output GET/SET_REPORT ioctls, buffers input reports per open file, and manages hidraw minors across HID device connect/disconnect.

## Important APIs, Types, and Functions

- Globals: `hidraw_major`, `hidraw_cdev`, `hidraw_class`, `hidraw_table[]`, and `minors_rwsem`.
- File operations: `hidraw_read`, `hidraw_write`, `hidraw_poll`, `hidraw_open`, `hidraw_release`, `hidraw_ioctl`, and `hidraw_fasync`.
- Report I/O helpers: `hidraw_send_report` and `hidraw_get_report`.
- Ioctl helpers: `hidraw_fixed_size_ioctl`, `hidraw_rw_variable_size_ioctl`, and `hidraw_ro_variable_size_ioctl`.
- Device lifecycle: `hidraw_connect`, `hidraw_disconnect`, `drop_ref`, `hidraw_init`, and `hidraw_exit`.
- Event ingress: `hidraw_report_event` copies incoming raw reports into every non-revoked open file buffer and wakes poll/read/fasync waiters.

## Control Flow

Subsystem init allocates a character-device major, registers class `hidraw`, and adds the cdev range. HID core calls `hidraw_connect` when a HID device requests HIDRAW, which allocates a minor, creates `/dev/hidrawN`, initializes wait queues/list locks, and stores the back pointer in `hid->hidraw`. Opening a node powers and opens the HID hardware on first open, allocates a `hidraw_list`, and links it into the device reader list.

Reads block until the per-open ring has data, the device disappears, a signal arrives, or `O_NONBLOCK` applies. Incoming reports are copied with `GFP_ATOMIC` into each reader ring unless the file is revoked or full. Writes send output reports, preferring interrupt output where allowed and falling back to SET_REPORT. Ioctls expose descriptor size/content, raw bus/vendor/product info, revoke, raw strings, and variable-length feature/input/output report transfers. Disconnect marks the device nonexistent, destroys the node, wakes readers, and frees state after the last open closes.

## State and Persistence Behavior

`struct hidraw` persists per connected HID device and tracks minor, open count, existence, waitqueue, list lock, and open reader list. Each open `struct hidraw_list` owns its ring buffer, read mutex, fasync state, and revoke flag. `minors_rwsem` protects the global table, open count, and connect/disconnect/release races. `list_lock` protects reader list traversal and ring insertion/freeing.

## Dependencies and Integration Points

It integrates with VFS character devices, uaccess, poll/fasync, HID core raw request/output hooks, device model class nodes, and power management hints. HID core calls `hidraw_report_event`, `hidraw_connect`, and `hidraw_disconnect`.

## Risks and Edge Cases

- Full per-open rings silently drop new reports for that reader.
- `HIDIOCREVOKE` only sets a per-file flag; it does not wake blocked readers immediately in `hidraw_revoke`.
- `hidraw_release` indexes `hidraw_table[minor]` under the write semaphore; this assumes disconnect keeps the table entry until open count reaches zero.
- Variable ioctl size comes from `_IOC_SIZE(cmd)` and must stay bounded by `HID_MAX_BUFFER_SIZE` checks in report helpers.
- Multiple readers get independent copies, so high report rates can allocate many atomic buffers.

## Test Signals

- Open multiple readers, generate reports, and verify each gets independent ordered data.
- Test blocking read, nonblocking read, poll, fasync, disconnect wakeup, and revoke behavior.
- Exercise all HIDIOC descriptor/info/name/phys/uniq and feature/input/output GET/SET paths with numbered and unnumbered reports.
- Stress high-rate reports to observe dropped ring entries and allocation failure handling.
- Run lockdep around open/disconnect/release races.
