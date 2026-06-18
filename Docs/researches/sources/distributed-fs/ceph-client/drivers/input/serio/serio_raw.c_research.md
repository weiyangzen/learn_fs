# sources/distributed-fs/ceph-client/drivers/input/serio/serio_raw.c

## Purpose
`serio_raw.c` exposes selected serio ports as raw misc character devices, emulating the historical `/dev/psaux` byte stream. It is manually bound to 8042-compatible ports so userspace can read incoming bytes, write outgoing bytes, poll for data, and receive async notifications.

## Important APIs, types, and functions
`struct serio_raw` holds a 64-byte circular receive queue, kref lifetime, underlying `struct serio`, miscdevice, waitqueue, client list, and dead flag. `struct serio_raw_client` stores per-open fasync state. File operations are `serio_raw_open()`, `release()`, `read()`, `write()`, `poll()`, and `fasync()`. Serio callbacks are `serio_raw_connect()`, `serio_raw_interrupt()`, `serio_raw_reconnect()`, and `serio_raw_disconnect()`.

## Control flow
Connect allocates the raw object, opens the serio port, links it into `serio_raw_list`, and registers a misc device, first trying `PSMOUSE_MINOR` and falling back to a dynamic minor. Incoming bytes are queued from the serio interrupt path while holding the serio lock; readers drain bytes under `serio_pause_rx()`, blocking on the waitqueue unless nonblocking. Writes are serialized by `serio_raw_mutex` and send at most 32 bytes through `serio_write()`. Disconnect deregisters the misc device, marks the object dead, wakes readers, sends fasync hangup, closes serio, and drops the kref.

## State and persistence
Runtime state is in the in-memory queue, open-client list, kref, and `dead` flag. The raw device has no persistent configuration. Open file descriptors keep the object alive after disconnect until release, but operations then fail or hang up based on `dead`.

## Dependencies and integration points
The driver integrates with the serio driver model, miscdevice subsystem, waitqueues, poll/fasync, usercopy helpers, and `PSMOUSE_MINOR`. Its ID table covers `SERIO_8042` and `SERIO_8042_XL`, and `manual_bind = true` keeps it from automatically taking over normal keyboard/mouse ports.

## Risks
The receive queue silently drops a byte when the ring would become full because the head update is skipped on overflow. Read-side checks of head/tail are partly lockless before the locked fetch, so correctness depends on retry behavior and simple byte queue semantics. The fixed-minor fallback must not confuse userspace expecting psaux-compatible numbering. Disconnect must wake all blocking and async users so stale file descriptors do not hang indefinitely.

## Test signals
Exercise manual binding/unbinding to an 8042 port, blocking and nonblocking reads, partial writes and write error propagation, poll masks before and after disconnect, fasync `SIGIO` delivery, queue overflow behavior, reconnect preserving the same raw device, and misc minor fallback when `PSMOUSE_MINOR` is unavailable.
