# sources/distributed-fs/ceph-client/drivers/hid/uhid.c

Purpose: user-space HID transport exposed as `/dev/uhid`. It lets a userspace process create a virtual HID device, feed input reports to the HID core, and service output/get/set report requests emitted by HID drivers.

Important APIs/types: `struct uhid_device` tracks per-open instance state: dev mutex, running flag, report descriptor, HID device, output event ring, blocking report request state, and worker. `uhid_hid_driver` implements HID low-level callbacks. `uhid_fops` implements char-device open/read/write/poll/release. The misc device is registered with `module_misc_device()`.

Control flow: userspace writes `UHID_CREATE`/`CREATE2`; the driver copies descriptor data, allocates `hid_device`, marks it running, and schedules worker-based `hid_add_device()` so probe-time feature requests can round-trip to userspace. HID start/open/close/output/request callbacks enqueue events to the userspace-readable ring. Blocking get/set report callbacks serialize on `report_lock`, enqueue a request with an ID, wait up to 5 seconds, and are completed by userspace reply events. Input events written by userspace are passed to `hid_input_report()`.

State and persistence: each file descriptor owns one virtual device. `running` gates HID callbacks and is cleared on destroy, failed add, or release. Ring state is protected by spinlock; high-level lifecycle by `devlock`.

Dependencies and integration: depends on miscdevice, HID core, input, waitqueues, compat syscall handling, and `uapi/linux/uhid.h`. It integrates unprivileged-ish userspace device emulators with normal HID drivers.

Risks: `UHID_CREATE` contains a userspace pointer and is rejected when file credentials differ from current credentials; `CREATE2` avoids that. Queue overflow drops events. Failed `hid_add_device()` intentionally leaves `hid` allocated until close/reinit to avoid races. Blocking report operations depend on userspace timely replies.

Test signals: uhid selftests/userspace samples, create/destroy loops, compat `UHID_CREATE`, poll/read event ordering, get/set report timeout and reply handling, and input report delivery to HID/input subsystems.
