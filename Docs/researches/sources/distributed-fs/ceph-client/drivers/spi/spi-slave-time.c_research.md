# sources/distributed-fs/ceph-client/drivers/spi/spi-slave-time.c

## Purpose

`spi-slave-time.c` is a SPI target protocol handler that continuously returns the local uptime captured at the time the previous SPI message was submitted. The payload is two big-endian 32-bit integers: seconds since boot and microseconds within the current second.

## Important APIs, Types, and Functions

`struct spi_slave_time_priv` stores the `spi_device`, a termination completion, one reusable transfer/message pair, and a two-word transmit buffer. `spi_slave_time_submit()` samples `local_clock()`, converts nanoseconds into seconds and microseconds with `do_div()`, stores values in network byte order, initializes a one-transfer message, and queues it with `spi_async()`. The completion callback checks `msg.status` and resubmits on success. Probe allocates state, sets the TX buffer and length, submits the first message, and stores drvdata. Remove aborts the target transaction and waits for termination.

## Control Flow

The driver maintains one outstanding asynchronous TX message. The buffer is refreshed immediately before submission, so the SPI host receives the timestamp of the last submission, effectively the previous request boundary. On successful completion, the callback immediately submits the next message. Any error or resubmit failure stops the loop and completes `finished`.

## State and Persistence Behavior

The only durable in-kernel state is the reusable message/transfer and the current two-word timestamp buffer. There is no filesystem or firmware persistence. The time source is `local_clock()`, so semantics are uptime-like and local CPU clock dependent rather than wall-clock time.

## Dependencies and Integration Points

The file depends on the SPI target-device API, `local_clock()` from scheduler clock support, big-endian conversion helpers, and completions. It requires a target-capable SPI controller with working abort semantics.

## Risks and Edge Cases

The 32-bit seconds field wraps after roughly 136 years of uptime; the microseconds field is derived from nanosecond remainder and is safe within one second. `local_clock()` may have CPU-local behavior on some platforms, so cross-CPU callback migration could expose tiny discontinuities depending on architecture. Remove can block if `spi_target_abort()` does not terminate the queued async message. There is no timeout or flow control beyond SPI core completion.

## Test Signals

Validate big-endian encoding, monotonic progression across repeated host reads, behavior under fast polling, remove while a message is pending, SPI error completion, and target abort. Tests should also compare returned seconds/microseconds against kernel uptime within reasonable scheduling tolerance.
