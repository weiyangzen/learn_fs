# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_queue.c

## Purpose
`zcrypt_queue.c` implements shared zcrypt queue-device lifetime, common queue sysfs attributes, online/offline behavior, load reporting, registration into the zcrypt card queue list, and cleanup.

## Important APIs, Types, And Functions
Externally visible functions are `zcrypt_queue_force_online()`, `zcrypt_queue_alloc()`, `zcrypt_queue_free()`, `zcrypt_queue_get()`, `zcrypt_queue_put()`, `zcrypt_queue_register()`, and `zcrypt_queue_unregister()`. Sysfs handlers implement `online` read/write and `load` read. Internal release is handled by `zcrypt_queue_release()`.

## Control Flow
Allocation zeroes a `zcrypt_queue`, allocates a reply buffer sized by the card/driver caller, initializes the list and refcount, and returns the queue. Registration takes the global zcrypt list lock, finds the parent `zcrypt_card` from AP card driver data, increments the card refcount, links the queue into the card queue list, creates the sysfs group, and adds the hardware RNG device when the selected ops provide `.rng`. Unregistration removes the queue from the list, removes RNG support and sysfs, drops the parent card, and releases the queue ref. The `online` store path validates requested values and underlying AP/card config/checkstop state, refuses online if parent zcrypt card is offline, updates `zq->online`, emits an AP online uevent, and flushes queued AP messages when transitioning offline.

## State And Persistence
The file manages in-memory queue state: reply buffer, list node, refcount, online flag, load counter, parent card pointer, and sysfs attributes. No persistent storage exists.

## Dependencies And Integration Points
It depends on zcrypt global list locking and card refcounting, AP queue/card state, AP uevents and flushing, sysfs, and optional zcrypt RNG device registration. CEX card/queue probe paths call these routines.

## Risks And Test Signals
Risks include refcount/list imbalance on registration failure, sysfs lifecycle mismatches, racing online changes with AP queue operations, and failure to flush when offline. Test signals include allocation failure injection, register/unregister cycles, sysfs online validation, uevent emission, AP flush on offline, and RNG add/remove symmetry.
