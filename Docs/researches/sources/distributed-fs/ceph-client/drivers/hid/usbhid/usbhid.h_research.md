# sources/distributed-fs/ceph-client/drivers/hid/usbhid/usbhid.h

## Purpose

`usbhid.h` is the shared private header for USB HID support. It declares the USB HID core helper APIs used by sibling modules, defines USBHID I/O state flags, and describes `struct usbhid_device`, the USB-transport-specific state attached to a generic `struct hid_device`.

## Important APIs, Types, And Data

- `usbhid_init_reports(struct hid_device *hid)` initializes report values from hardware.
- `usbhid_find_interface(int minor)` maps a hiddev minor to a USB interface.
- I/O flag constants describe transport state in `usbhid_device.iofl`: control/output/input running, reset pending, suspended, halt clear, disconnected, started, keys pressed, no bandwidth, resume running, opened, and input polling.
- `struct usbhid_device` stores the HID backpointer, USB interface/number, URB buffer size, input/control/output URBs, DMA buffers, control and output FIFOs, last I/O timestamps, mutex/spinlock, retry timer, reset work, retry parameters, and wait queue.
- `hid_to_usb_dev(hid_dev)` converts a HID device parent chain to the underlying `struct usb_device`.

## Control Flow

This header has no executable control flow. It defines the data shape that `hid-core.c` and other USBHID users operate on. Runtime control flow is in USBHID core code that submits interrupt input URBs, queues control/output transfers, handles retries and reset work, and coordinates open/close/start/stop through the fields declared here.

## State And Persistence Behavior

`struct usbhid_device` is per USB HID interface and is owned by USBHID core. Its fields are volatile kernel runtime state: URBs, DMA buffers, FIFO heads/tails, flags, timers, and work items. It does not persist across disconnect or driver unbind.

The state is split by concurrency domain. `mutex` serializes lifecycle operations, `lock` protects FIFOs and I/O flags, `io_retry` and `reset_work` defer recovery work, and `wait` supports sleeping callers waiting for I/O progress.

## Dependencies And Integration Points

- Includes core kernel infrastructure headers for types, allocation, lists, mutexes, timers, wait queues, workqueues, and input.
- Used by `hiddev.c` for `usbhid_find_interface()`, `usbhid_init_reports()`, `struct usbhid_device`, and `hid_to_usb_dev()`.
- Used by USB HID core implementation as the private `hid->driver_data` layout.

## Risks And Edge Cases

- The macro `hid_to_usb_dev()` assumes a specific HID device parent hierarchy. Non-USB HID devices must not use it.
- FIFO sizes and `unsigned char` head/tail fields imply bounded circular queues; producers must handle full queues correctly in implementation code.
- Correctness depends on consistent flag-bit ownership and lock discipline in USBHID core. This header documents flags but does not enforce locking.

## Test Signals

- Build tests should catch drift between this struct definition and USBHID core users.
- Runtime tests for USB HID suspend/resume, reset, clear-halt, no-bandwidth, open/close, and disconnect paths exercise the flags and work/timer fields.
- hiddev tests using `HIDIOCGDEVINFO` indirectly verify that `hid->driver_data` is a valid `struct usbhid_device` with a correct interface number.
