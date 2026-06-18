# sources/distributed-fs/ceph-client/drivers/iio/buffer/kfifo_buf.c

## Purpose
`kfifo_buf.c` provides the standard software/triggered IIO buffer backed by Linux `kfifo`, supporting sample push, userspace read/write, data/space reporting, and dynamic reallocation when datum size or length changes.

## Important APIs, Types, And Functions
`struct iio_kfifo` embeds `struct iio_buffer`, the kfifo, a `user_lock`, and an update flag. Access callbacks include `iio_store_to_kfifo()`, `iio_read_kfifo()`, `iio_kfifo_write()`, `iio_kfifo_remove_from()`, availability callbacks, length/datum setters, and `iio_request_update_kfifo()`. Exported helpers are `iio_kfifo_allocate()`, `iio_kfifo_free()`, and `devm_iio_kfifo_buffer_setup_ext()`.

## Control Flow
Allocation initializes the buffer with length 2 and marks an update needed. When the IIO core requests an update, the kfifo is allocated or reset. Producers push one datum at a time; userspace reads bytes through `kfifo_to_user()`, and output consumers can remove samples or accept writes from userspace.

## State And Persistence
The kfifo storage is volatile and protected by `user_lock` for userspace-facing operations. `update_needed` defers reallocation until request-update time. Buffer length is clamped to at least two to avoid invalid states.

## Dependencies And Integration Points
It integrates with IIO buffer access functions, kfifo, poll wakeups, mutexes, and devm buffer setup for drivers that need a software buffer without full triggered-buffer helper setup.

## Risks
`iio_store_to_kfifo()` is not protected by `user_lock`, matching kfifo producer assumptions but requiring correct IIO core serialization. Overflow returns `-EBUSY`. Length overflow is checked before kfifo power-of-two rounding. Data availability returns sample count from `kfifo_len()`, so consumers must understand kfifo element sizing.

## Test Signals
Test allocation/reallocation on length and datum-size changes, invalid zero sizes, overflow protection, push/read ordering, write/remove output paths, poll wake on remove, and devm attach behavior.
