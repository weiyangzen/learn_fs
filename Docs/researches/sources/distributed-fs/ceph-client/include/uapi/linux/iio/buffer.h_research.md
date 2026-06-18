
# sources/distributed-fs/ceph-client/include/uapi/linux/iio/buffer.h

## Purpose

`iio/buffer.h` defines Industrial I/O buffer DMABUF UAPI objects and ioctls for exporting, attaching, detaching, and enqueuing DMA buffers. The complete 32-line file was read.

## Important APIs, Types, and Functions

It defines `IIO_BUFFER_DMABUF_CYCLIC`, `IIO_BUFFER_DMABUF_SUPPORTED_FLAGS`, `struct iio_dmabuf` with fd/flags/bytes_used, and ioctls `IIO_BUFFER_GET_FD_IOCTL`, `IIO_BUFFER_DMABUF_ATTACH_IOCTL`, `IIO_BUFFER_DMABUF_DETACH_IOCTL`, and `IIO_BUFFER_DMABUF_ENQUEUE_IOCTL`.

## Control Flow

User space obtains or supplies DMABUF file descriptors through ioctls, attaches them to an IIO buffer, queues transfers with `iio_dmabuf`, and the kernel/device driver consumes or fills the buffer.

## State and Persistence Behavior

DMABUF attachments and queued buffers are kernel IIO buffer state. `bytes_used` describes the active transfer amount, and cyclic mode persists for that queued buffer/attachment as interpreted by the driver.

## Dependencies and Integration Points

It includes `linux/types.h` and relies on ioctl macros from surrounding UAPI context. It integrates with IIO character devices, DMA-BUF, sensor/ADC/DAC drivers, and zero-copy data paths.

## Risks and Edge Cases

Risks include fd lifetime management, bytes_used exceeding DMABUF size, unsupported flags, cyclic transfer semantics, and driver-specific DMA constraints.

## Test Signals

IIO buffer tests should attach/detach valid and invalid DMABUF fds, enqueue normal and cyclic buffers, validate `bytes_used` limits, and verify ioctl error paths.
