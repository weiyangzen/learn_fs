# sources/distributed-fs/ceph-client/drivers/tee/optee/notif.c

## Purpose
`notif.c` implements OP-TEE notification wait/send synchronization for values posted by secure world or by OP-TEE RPC notification commands.

## Important APIs, Types, And Functions
`struct notif_entry` stores a waiting key and completion on a list. `optee_notif_wait()` validates the key, allocates an entry, checks whether the key was already posted in the bitmap, rejects duplicate waiters, optionally waits with a timeout, removes the entry, and returns 0, `-ETIMEDOUT`, `-EBUSY`, `-ENOMEM`, or `-EINVAL`. `optee_notif_send()` either completes a waiting entry for the key or records the key in the bitmap for a future waiter. `optee_notif_init()` initializes the spinlock/list and allocates the bitmap. `optee_notif_uninit()` frees the bitmap.

## Control Flow And State
Notification state is per `struct optee` in `optee->notif`. A spinlock protects both the active wait-list and posted-key bitmap. If send happens before wait, the bit is set and consumed by the next waiter without sleeping. If wait happens first, the waiter sleeps on a completion until send or timeout.

## Dependencies And Integration Points
This code is used by RPC notification handling in `rpc.c` and async interrupt/FF-A notification paths in backend files. It depends on Linux completions, bitmaps, spinlocks, and the OP-TEE max notification key negotiated during probe.

## Risks
The bitmap is allocated with `bitmap_zalloc(max_key, ...)` while valid keys are checked as `key > max_key`, which makes `key == max_key` appear valid but may be outside the allocated bitmap bit range depending on bitmap API expectations. Duplicate waiters return `-EBUSY`, treated by RPC code as bad parameters. Timeout removes the entry while a concurrent send is serialized by the spinlock, so lost completion should be avoided.

## Test Signals
Wait after pre-posted send, send after wait, timeout wait, duplicate wait on the same key, invalid key above max, and boundary key equal to max. Exercise from both interrupt-triggered async notifications and RPC notification wait/send commands.
