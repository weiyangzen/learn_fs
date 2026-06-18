# sources/distributed-fs/ceph-client/drivers/usb/misc/yurex.c

## Purpose

`yurex.c` is a character-device USB driver for the Meywa-Denki/KAYAC YUREX gadget. It exposes the device counter value through `/dev/yurexN`, accepts command writes for LED, animation, read, version, and set-count operations, and reports asynchronous counter updates through SIGIO.

## Important APIs, Types, and Functions

`struct usb_yurex` stores the USB device/interface, interrupt-in URB and coherent buffer, HID class control URB and coherent buffer, kref, I/O mutex, disconnect flag, fasync queue, wait queue, spinlock, and signed 64-bit BBU counter. `yurex_probe()` allocates URBs and buffers, configures a HID SET_REPORT control request, submits the interrupt URB, and registers a USB minor. `yurex_interrupt()` decodes `CMD_COUNT`, `CMD_READ`, and `CMD_ACK`. File operations `yurex_open()`, `yurex_read()`, `yurex_write()`, `yurex_release()`, and `yurex_fasync()` implement userspace access.

## Control Flow

Probe finds an interrupt-in endpoint, starts a continuously resubmitted interrupt URB, then registers the class device. Incoming interrupt packets either update `dev->bbu` from five payload bytes and send SIGIO, or wake command writers after an ACK. Writes build an 8-byte HID output report padded with `0xff`, submit the control URB, wait up to two seconds for ACK or callback wakeup, kill the URB to ensure it is idle, and optionally update the cached counter for successful SET commands. Disconnect deregisters the minor, poisons both URBs, marks the device disconnected under mutex, wakes readers/writers, signals fasync listeners, and drops the kref.

## State and Persistence Behavior

Runtime state is the cached BBU counter and in-flight URBs. `bbu` starts at `-1`, is updated by interrupt reports or successful SET writes, and is guarded by a spinlock. Open file references hold krefs; disconnect prevents new I/O with `disconnected`. No state is persisted across unplug or module reload.

## Dependencies and Integration Points

The driver depends on USB core, USB class minors, HID report constants, coherent DMA buffers, `simple_read_from_buffer()`, wait queues, fasync, and user-copy helpers. It presents a simple character device rather than using the HID input stack, but sends commands as HID class output reports.

## Risks and Test Signals

Risks include trusting short command buffers for commands that read `buffer[1]`, control URB serialization around a single shared buffer, ACK timeout ambiguity, and ensuring poisoned URBs cannot wake freed objects. Test signals include read format after interrupt count packets, write commands `A`, `L`, `R`, `V`, `S123`, numeric-only SET, disconnect during blocking write, fasync SIGIO on counter update, and probe failure cleanup after each allocation stage.
