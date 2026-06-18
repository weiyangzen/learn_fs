# sources/distributed-fs/ceph-client/drivers/w1/w1_internal.h

## Purpose
Private W1 core header shared by `w1.c`, `w1_family.c`, `w1_int.c`, and `w1_io.c`. It declares internal state flags, async command structure, core helpers, globals, and exported cross-file functions.

## Important APIs, Types, and Functions
Defines slave flags `W1_SLAVE_ACTIVE` and `W1_SLAVE_DETACH`. `struct w1_async_cmd` is the callback node processed by the master kthread. Declarations cover master attributes, search, slave lookup/refcounting, attach/detach, reconnect, master removal, family get/put/lookup, globals `w1_masters`, `w1_mlock`, `w1_flock`, and `w1_process()`.

## Control Flow
No executable logic. The declared interfaces define the internal call graph between master lifecycle, family registration, search, and low-level I/O modules.

## State and Persistence
No storage is allocated here. The header exposes in-memory globals and state flags used elsewhere.

## Dependencies and Integration Points
Includes public `<linux/w1.h>`, completion, and mutex definitions. It is not a public driver API; external master/slave drivers use `<linux/w1.h>` instead.

## Risks and Test Signals
Because this header exposes globals and internal functions, locking contracts must be preserved by all users. Test signals are compile coverage and lockdep/race testing around async callbacks, slave detach, and family reconnect paths.
