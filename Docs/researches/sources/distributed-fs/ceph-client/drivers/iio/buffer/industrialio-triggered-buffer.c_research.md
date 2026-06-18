# sources/distributed-fs/ceph-client/drivers/iio/buffer/industrialio-triggered-buffer.c

## Purpose
This helper combines common IIO triggered-buffer setup: allocate a kfifo buffer, allocate a pollfunc, attach the buffer, and mark the device as triggered-buffer capable.

## Important APIs, Types, And Functions
`iio_triggered_buffer_setup_ext()` is the central exported setup helper. It accepts top-half and threaded pollfunc handlers, buffer direction, optional setup ops, and optional buffer attributes. `iio_triggered_buffer_cleanup()` deallocates the pollfunc and frees the kfifo. `devm_iio_triggered_buffer_setup_ext()` wraps setup with managed cleanup.

## Control Flow
Drivers call setup before registering the IIO device. The helper refuses to proceed if `indio_dev->buffer` already exists because cleanup assumes it owns that buffer. On success, it sets `indio_dev->setup_ops`, ORs `INDIO_BUFFER_TRIGGERED` into modes, attaches a kfifo buffer, and stores pollfunc metadata.

## State And Persistence
State consists of the allocated kfifo buffer and pollfunc pointers attached to `indio_dev`. It is released explicitly or through devm cleanup. No persistent configuration is stored.

## Dependencies And Integration Points
It depends on the kfifo buffer implementation, IIO trigger consumer/pollfunc APIs, IIO buffer core, and optional buffer setup ops from sensor drivers.

## Risks
Ownership assumptions are strict: using this helper after attaching another buffer returns `-EADDRINUSE`. Cleanup assumes setup succeeded and the buffer is the kfifo allocated here. Drivers that call non-devm setup must pair cleanup on all later registration errors and remove paths.

## Test Signals
Validate success path, pollfunc allocation failure unwind, pre-existing buffer rejection, attach failure unwind, devm action behavior, and driver remove/error paths using this helper.
