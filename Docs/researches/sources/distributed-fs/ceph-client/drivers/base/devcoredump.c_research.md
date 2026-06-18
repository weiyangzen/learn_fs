# sources/distributed-fs/ceph-client/drivers/base/devcoredump.c

## Purpose
`devcoredump.c` implements `/sys/class/devcoredump`, allowing drivers to publish temporary crash dumps for failed devices. It supports vmalloc buffers, scatterlist dumps, custom read/free callbacks, timeout-based cleanup, manual deletion, and a global security disable knob.

## Important APIs, Types, And Functions
`struct devcd_entry` wraps the class device, dump data, callbacks, owner module, failing device reference, deletion work, and race-protection mutex flags. Public APIs are `dev_coredumpv()`, `dev_coredumpsg()`, `dev_coredumpm_timeout()`, and `dev_coredump_put()`. Sysfs exposes binary `data` and class attribute `disabled`.

## Control Flow, State, And Persistence
Creation rejects dumps when disabled or when a dump already exists for the failing device, pins the callback module, initializes a `devcd` device, schedules deletion before `device_add()`, links to the failing device, enables uevents, and marks initialization complete. Reading dispatches through the stored read callback; writing to `data` schedules immediate deletion. The delayed worker, disable path, and explicit put converge on `devcd_free()` and `__devcd_del()`, with `deleted` preventing double destruction.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include the device class core, sysfs binary attributes, workqueues, module refs, scatterlist copy helpers, vmalloc, and failing-device kobjects. Risks are lifetime races between device creation and deletion, disable-vs-worker concurrency, one-dump-per-device policy discarding later dumps, and careful ownership transfer of caller data. Test signals include duplicate dump suppression, read/write delete, timeout expiry, disabled write-once behavior, sgtable reads with offsets, module unload using `dev_coredump_put()`, and link cleanup after failing device removal.
