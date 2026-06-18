<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/adb.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/adb.c

Purpose: This file is the unified Apple Desktop Bus core and `/dev/adb` character-device interface. It selects one platform ADB controller, scans and resets the bus, dispatches ADB input to registered device handlers, manages sleep/reset notifications, and exposes user requests through major 56.

Important APIs and state: Exported APIs include `adb_request()`, `adb_register()`, `adb_unregister()`, `adb_input()`, `adb_try_handler_change()`, `adb_get_infos()`, `adb_poll()`, and the blocking notifier head `adb_client_list`. `struct adb_handler` records per-address handler, original address, handler ID, and busy flag. Handler metadata is protected by `adb_handler_mutex`; dispatch uses `adb_handler_lock` rwlock. `/dev/adb` uses `struct adbdev_state` with pending count, completed request list, waitqueue, spinlock, and in-use flag.

Control flow: `adb_init()` filters unsupported machines, chooses the first probing controller backend from the compiled list, initializes it, creates `/dev/adb`, and schedules an ADB bus reset. `do_adb_reset_bus()` disables autopoll, sends pre-reset notifications, clears handler state, asks the controller to reset, scans devices, enables autopoll for detected devices, and sends post-reset notifications. `adb_scan_bus()` probes addresses, handles collisions by moving devices to a high free address, records original addresses and handler IDs, and returns an autopoll mask. `adb_request()` builds an ADB packet and optionally waits on a completion for synchronous requests. `adb_input()` dispatches packets by address unless sleep is in progress.

`/dev/adb` control flow: `adb_write()` copies a request from userspace, increments pending count, waits for probe/reset mutex, handles special ADB queries and bus reset, or sends to the controller. Completion callback `adb_write_done()` queues replies for readers or frees requests after close. `adb_read()` waits for a completed request, copies its reply to userspace, and frees it.

State and persistence: The selected controller, handler table, autopoll mask, sleep state, and `/dev/adb` open state are global kernel runtime state. Device address assignments are rederived on every bus reset. PM suspend disables autopoll and notifies clients; resume schedules a new reset.

Dependencies and integration: It integrates with ADB controller backends, platform device PM hooks, character-device registration, device class creation, blocking notifier clients such as ADB HID, OF/machine detection, and PowerMac/m68k architecture code.

Risks and test signals: Bus scanning and handler changes are legacy protocol-sensitive. `adb_unregister()` waits for busy handlers by yielding while holding/releasing the write lock. `/dev/adb` close with pending requests relies on `inuse` and pending count to free state. Test controller absence, reset during userspace requests, sleep/resume notifications, handler registration conflicts, user query handling, nonblocking reads, and bus reset from userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/adb.c -->
