# sources/distributed-fs/ceph-client/drivers/s390/net/smsgiucv_app.c

Purpose: bridges z/VM CP SMSGs with prefix `APP` into userspace uevents on a synthetic IUCV device, optionally filtering by sender.

Important APIs and functions: module parameter `sender` restricts accepted z/VM user IDs. `smsg_app_callback()` is registered with `smsg_register_callback()`. `smsg_app_event_alloc()` builds uevent environment strings, `smsg_event_work_fn()` emits queued `KOBJ_CHANGE` events, and lifecycle functions allocate/register/unregister the app device.

Control flow: init requires z/VM and the SMSGIUCV core driver, allocates an IUCV device, registers it, uppercases configured sender, and registers the `APP` callback. The callback filters sender, skips the prefix and leading whitespace, ignores empty text, allocates an event, appends it to a spinlock-protected queue, and schedules work. The work function takes a device reference, splices the queue locally, emits each uevent, and frees each event.

State and persistence: global runtime state includes `smsg_app_dev`, `sender`, and the queued event list. Events persist only until the work function emits them. Exit unregisters the callback, cancels work, flushes any queued events by calling the worker, and unregisters the device.

Dependencies and integration: depends on the SMSGIUCV exported API, IUCV bus device allocation, workqueues, kobject uevents, and z/VM environment. Userspace observes `SMSG_SENDER`, `SMSG_ID`, and `SMSG_TEXT`.

Risks: callback allocation uses `GFP_ATOMIC`; under memory pressure messages can be silently dropped. Sender filtering is case-sensitive after the configured value is uppercased, relying on the core sender format. Message text is included in the uevent environment, so length and content can stress userspace consumers. Exit deliberately emits queued events after cancelling work, so teardown can still notify userspace.

Test signals: module load without core driver, sender filter acceptance/rejection, empty message drop, environment formatting, workqueue queue splicing under multiple messages, device reference handling, and exit with pending events.
