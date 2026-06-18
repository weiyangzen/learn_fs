# sources/distributed-fs/ceph-client/drivers/iio/buffer/industrialio-buffer-cb.c

## Purpose
This file implements the IIO callback buffer, an in-kernel consumer path where samples pushed by an IIO provider are delivered to a caller-supplied callback instead of userspace file I/O.

## Important APIs, Types, And Functions
`struct iio_cb_buffer` embeds `struct iio_buffer`, callback pointer, private data, acquired channels, and provider IIO device. `iio_channel_get_all_cb()` allocates the buffer, acquires all channels for a consumer, validates that all channels belong to the same `iio_dev`, and builds the scan mask. `iio_buffer_cb_store_to()` invokes the callback from the buffer store path. Exported helpers set watermark, start/stop buffering with `iio_update_buffers()`, release resources, and expose channels/provider device.

## Control Flow
A consumer allocates a callback buffer, optionally sets a watermark, starts it, receives callbacks from provider buffer pushes, stops it, and releases it. Release drops channels and puts the buffer; the access `release` frees the scan mask and object.

## State And Persistence
State is in-memory and reference-counted through the embedded IIO buffer. The scan mask persists only for the lifetime of the callback buffer. The callback must be safe in any context and must not sleep.

## Dependencies And Integration Points
The implementation uses the IIO consumer API, IIO buffer core, bitmap allocation, and exported GPL symbols. Access modes are software and triggered buffering.

## Risks
Callbacks that sleep or assume process context can break provider paths. Multi-provider channel lists are rejected after allocation and must unwind cleanly. Watermark zero is invalid. Consumers must call stop before release if active to avoid provider-side lifecycle issues.

## Test Signals
Test single-provider and mixed-provider channel acquisition, callback invocation under trigger/software modes, watermark validation, start/stop ordering, and release/unwind paths with allocation failures.
