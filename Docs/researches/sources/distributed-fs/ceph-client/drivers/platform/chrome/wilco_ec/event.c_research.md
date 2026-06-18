<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/event.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/event.c

## Purpose

This optional Wilco EC ACPI event driver exposes EC events to userspace through `/dev/wilco_eventN`. It installs an ACPI notify handler, fetches event buffers via the `QSET` ACPI method, queues parsed events, and supports blocking reads and polling.

## Important APIs, Types, And Functions

`struct ec_event` models variable-length EC events. `struct ec_event_queue` is a bounded circular queue. `struct event_device_data` owns the queue, spinlock, wait queue, cdev, embedded device, existence flag, and single-open guard. `enqueue_events()` validates and copies packed events. `event_device_notify()` handles ACPI Notify `0x90`. `event_open()`, `event_poll()`, `event_read()`, and `event_release()` implement the character device.

## Control Flow

Module init creates a class, allocates a major range, and registers the ACPI platform driver for `GOOG000D`. Probe allocates a minor, creates the cdev/device, and installs the ACPI notify handler. On notify, the driver evaluates `QSET`, validates an ACPI buffer, parses one or more events, pushes them to the circular queue, and wakes readers. Reads return one complete event at a time, blocking unless opened nonblocking. Remove uninstalls ACPI notify, deletes the cdev, frees the minor, marks the device nonexistent, and wakes waiters.

## State And Persistence

Runtime state is per ACPI device. The queue is bounded by module parameter `queue_size` and overwrites oldest events when full. Events are volatile and removed when read or during device teardown. Device lifetime is reference-counted so open files can close safely after remove.

## Dependencies And Integration Points

The file depends on ACPI notifications/method evaluation, cdev/device core, IDA minor allocation, wait queues, spinlocks, and userspace poll/read consumers.

## Risks

The queue capacity parameter is not clamped against zero in the local code; invalid module parameters could stress queue indexing. Event parsing trusts packed EC event size fields after bounds checks. Only one reader may open the device, which is intentional but can surprise diagnostic tools. Dropping oldest events on overflow can hide bursts.

## Test Signals

Test class/major allocation, probe/remove with open readers, ACPI notify values other than `0x90`, malformed `QSET` returns, oversized event word counts, queue overflow behavior, blocking and nonblocking reads, poll wakeups, and single-open enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/event.c -->
