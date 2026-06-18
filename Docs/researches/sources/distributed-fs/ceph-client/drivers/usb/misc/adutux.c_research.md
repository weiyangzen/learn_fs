# sources/distributed-fs/ceph-client/drivers/usb/misc/adutux.c

## Purpose
`adutux.c` is a character-device USB driver for Ontrak Control Systems ADU devices. It exposes interrupt-in and interrupt-out endpoint traffic to userspace through `/dev/usb/adutux%d`, with single-open policy and buffered reads/writes.

## Important APIs, Types, And Functions
`struct adu_device` stores the USB device/interface, minor, serial, open/disconnect state, primary and secondary read buffers, interrupt buffers, endpoints, URBs, wait queues, mutexes, and spinlock-protected completion flags. USB binding uses `adu_driver`, `device_table`, `adu_probe()`, and `adu_disconnect()`. Character operations are `adu_open()`, `adu_release()`, `adu_read()`, and `adu_write()`. URB callbacks are `adu_interrupt_in_callback()` and `adu_interrupt_out_callback()`. Cleanup helpers are `adu_abort_transfers()` and `adu_delete()`.

## Control Flow
Probe allocates device state, initializes locks/waits, finds interrupt-in and interrupt-out endpoints, allocates double read buffers plus endpoint buffers and URBs, reads a serial string, stores interface data, and registers the USB class device. Open finds the interface by minor, enforces one opener, resets read buffer length, submits an initial interrupt-in URB, and marks the interrupt-out path idle.

Read drains the secondary buffer first. If empty, it swaps in primary data filled by the interrupt callback or submits/waits for an input URB. It handles timeout, signals, and copy errors while using `mtx` for high-level serialization and `buflock` for callback-shared buffer flags. Write waits for any prior interrupt-out URB to complete, copies up to endpoint maxpacket from userspace, submits an interrupt-out URB, and repeats until the user buffer is consumed. Disconnect deregisters the devnode, poisons URBs, marks disconnected under locks, and frees immediately only when not open; release frees after unplug if it is the last user.

## State And Persistence
State is per ADU device and lasts from probe until disconnect plus final close. Read data is staged in a primary buffer filled by interrupt callbacks and a secondary buffer drained by userspace. Completion flags `read_urb_finished` and `out_urb_finished` coordinate sleepers. No data persists beyond driver lifetime.

## Dependencies And Integration Points
The driver depends on USB core, `usb_class_driver`, interrupt URBs, user-copy helpers, wait queues, mutexes, spinlocks, and dynamic/static minor allocation. It integrates with userspace as a simple char device rather than a higher-level subsystem.

## Risks
The locking scheme is documented but delicate: global `adutux_mutex` covers open count, `mtx` covers sleeping operations, and `buflock` covers callback-visible buffers. `adu_interrupt_out_callback()` returns without setting `out_urb_finished` or waking waiters for nonzero status, which can cause write-side timeout behavior. The read buffer capacity is `4 * maxpacket`; overflow is logged and data is dropped. `adu_abort_transfers()` waits for output completion while handling disconnect/open lifetime. Serial string retrieval failure rejects the device.

## Test Signals
Test open exclusivity, read/write with endpoint maxpacket boundaries, partial reads from secondary buffer, timeout paths, signal interruption, unplug during blocking read/write, open-after-disconnect, disconnect while open followed by release, and URB completion errors. Dynamic minor and static minor configurations should both be built.
