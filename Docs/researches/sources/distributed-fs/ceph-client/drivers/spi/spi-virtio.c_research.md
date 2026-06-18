<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-virtio.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-virtio.c

## Purpose

`spi-virtio.c` is the Linux SPI host driver for the virtio SPI device. It exposes a virtio-provided SPI controller to the SPI core and translates each `spi_transfer` into one virtqueue request containing a `spi_transfer_head`, optional TX payload, optional RX payload, and result status.

The implementation is deliberately simple: it supports only one in-flight transfer per controller and waits synchronously for virtqueue completion inside `transfer_one`.

## Important APIs, Types, and Functions

`struct virtio_spi_priv` stores the virtio device, single request virtqueue, and cached config fields (`mode_func_supported`, `max_freq_hz`). `struct virtio_spi_req` owns one transfer's completion, TX/RX buffer pointers, virtio transfer header, and result structure.

`virtio_spi_read_config()` reads virtio config space (`struct virtio_spi_config`) and maps supported mode/function bits to SPI controller `mode_bits`, chip-select count, bits-per-word mask, dual/quad/octal TX/RX support, loopback, and max frequency.

`virtio_spi_set_delays()` converts Linux SPI delay fields into nanoseconds for the virtio header: CS setup, max of device/transfer word delay, transfer delay plus CS hold, and CS inactive plus CS-change delay.

`virtio_spi_transfer_one()` builds the virtqueue scatter-gather list and translates virtio result codes to Linux errors. `virtio_spi_msg_done()` completes requests returned by `virtqueue_get_buf()`. `virtio_spi_find_vqs()` and `virtio_spi_del_vq()` manage the single queue. PM support is handled by `virtio_spi_freeze()` and `virtio_spi_restore()`.

## Control Flow

Probe allocates a devm SPI host, stores private state in `vdev->priv`, reads virtio config to size and advertise the controller, installs `transfer_one`, creates the single virtqueue named `"spi-rq"`, registers a devm cleanup action that resets the device and deletes queues, and registers the SPI controller.

For a transfer, the driver allocates a request, initializes the virtio header from the SPI device and transfer fields, asserts compile-time equality between Linux SPI mode constants and virtio constants, handles loopback mapping, writes requested frequency, converts all delay fields, and prepares scatterlist entries. The outgoing list always contains the transfer header and optionally the TX payload. The incoming list optionally contains the RX payload and always contains the result.

The request is submitted with `virtqueue_add_sgs()`, the queue is kicked, and the thread waits for `virtio_spi_msg_done()` to complete the request. After completion, `VIRTIO_SPI_TRANS_OK` returns success, `VIRTIO_SPI_PARAM_ERR` maps to `-EINVAL`, and other errors map to `-EIO`. On error the driver's current SPI message status is updated.

Freeze suspends the SPI controller and deletes virtqueues after resetting the virtio device. Restore recreates the virtqueue and resumes the SPI controller.

## State and Persistence Behavior

There is no persistent local storage. The controller state is virtio config space plus the active virtqueue. `max_freq_hz` is cached but not directly assigned to `ctrl->max_speed_hz` in this implementation. Each request is heap-allocated for one transfer and freed automatically at function exit.

Transfers can modify remote device state through the virtio backend and attached SPI target devices. The Linux driver itself stores no durable transaction log or replay state.

## Dependencies and Integration Points

The driver depends on the virtio core, virtqueue APIs, `linux/virtio_spi.h` ABI definitions, completions, scatterlists, and the SPI controller framework.

The main integration contract is the virtio SPI device ABI: header fields must be little-endian where specified, mode constants must match Linux SPI constants, result codes must be interpreted exactly, and the backend must return the request buffer for completion.

## Risks and Edge Cases

The synchronous one-transfer model is simple but limits queue depth and throughput. A hung or non-returning backend can block the transfer path indefinitely because `wait_for_completion()` has no timeout.

Delay conversion failures abort the transfer, but addition of delay components can overflow `int` before conversion to little-endian `u32` if extreme values are accepted upstream. The driver also caches `max_freq_hz` without enforcing it in `transfer_one`.

The `sgs` array ordering is subtle: when RX payload exists it is assigned at `sgs[outcnt]` and `incnt` is incremented, while the result is assigned at `sgs[outcnt + incnt]`. This is correct for virtqueue split output/input counts but should be preserved carefully.

Virtqueue deletion is registered with devm and also used in freeze; restore recreates queues. PM tests should ensure the devm cleanup action does not double-delete a queue after freeze/restore sequences.

## Test Signals

Tests should cover virtio config parsing for chip-select counts, word masks, CPOL/CPHA, CS high, LSB first, loopback, dual/quad/octal modes, and max frequency. Transfer tests should include TX-only, RX-only, full-duplex, zero-length, delay conversion fields, chip-select ids, loopback mode, and virtio result codes OK, parameter error, transfer error, and unknown.

Fault tests should cover allocation failure, `virtqueue_add_sgs()` failure, backend non-completion, freeze/restore during idle and after registered devices, and queue recreation after restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-virtio.c -->
