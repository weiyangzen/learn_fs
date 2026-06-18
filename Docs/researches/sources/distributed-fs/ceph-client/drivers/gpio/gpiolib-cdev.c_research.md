# sources/distributed-fs/ceph-client/drivers/gpio/gpiolib-cdev.c

## Purpose
`gpiolib-cdev.c` implements the GPIO character device ABI exposed as `/dev/gpiochipN`. It handles chip information, line information, line watching, v2 line requests, optional v1 handle/event ABI compatibility, edge event delivery, debounce support, hardware timestamp engine support, descriptor request/release, and gpiochip character device registration.

## Important APIs, Types, And Functions
The exported lifecycle functions are `gpiolib_cdev_register()` and `gpiolib_cdev_unregister()`. The main per-open chip state is `struct gpio_chardev_data`, which stores the GPIO device, watched-line bitmap, event FIFO, notifier blocks, wait queue, and file pointer. V2 requested lines use `struct linereq` and per-line `struct line`. V1 compatibility uses `struct linehandle_state` and `struct lineevent_state` under `CONFIG_GPIO_CDEV_V1`.

Important v2 helpers include `gpio_v2_line_config_validate()`, `gpio_v2_line_flags_validate()`, `linereq_create()`, `linereq_ioctl()`, `linereq_get_values()`, `linereq_set_values()`, `linereq_set_config()`, `edge_detector_setup()`, `edge_detector_update()`, `edge_detector_stop()`, `debounce_setup()`, `debounce_work_func()`, `edge_irq_handler()`, and `edge_irq_thread()`. Line info helpers include `gpio_desc_to_lineinfo()`, `lineinfo_get()`, `lineinfo_unwatch()`, `lineinfo_changed_notify()`, and `lineinfo_watch_read()`.

## Control Flow
`gpiolib_cdev_register()` initializes `gdev->chrdev`, assigns `devt`, creates an ordered high-priority workqueue for line-state notifications, and registers the cdev/device pair. Opening `/dev/gpiochipN` allocates `gpio_chardev_data`, creates a watched-line bitmap, registers raw line-state and blocking device-unregister notifiers, stores the file pointer, and returns a nonseekable file.

Chip ioctls dispatch through `gpio_ioctl()`. They return chip info, line info, line watch setup, line unwatch, v2 line request creation, and optional v1 handle/event creation. All ioctl paths guard `gdev->srcu` and fail with `-ENODEV` once the chip disappears.

V2 line requests copy and validate `gpio_v2_line_request`, allocate a flexible `linereq`, request each descriptor, apply flags, set transitory false, configure direction and output values, optionally set up edge detection, notify requested state, register an unregister notifier, and return an anonymous file descriptor. The line fd supports get/set values, reconfiguration, poll, read, and proc fdinfo.

Edge handling uses either IRQ hard/thread handlers, software debounce delayed work, or HTE callbacks. Events enter a kfifo under the waitqueue spinlock and wake poll waiters. Overflow drops the oldest v2 event via `kfifo_skip()` and logs rate-limited debug.

Line-info watching records watched offsets in a bitmap. Descriptor state notifications allocate a context in atomic context, snapshot line info without sleeping, then finish the pinctrl-dependent used-line check and FIFO insertion in the gpio device ordered workqueue.

## State And Persistence
All state is in-memory and scoped by file descriptors or gpiochip registration. Descriptor flags are updated to reflect requested direction, active-low, bias, drive, edge, clock, and debounce state. `linereq` stores sequence numbers, event FIFO, per-line debounce and timestamp fields, and a config mutex. `gpio_chardev_data` stores watch ABI version for v1/v2 compatibility and a watched-line bitmap. Cleanup unregisters notifiers, stops edge detectors, frees IRQs/HTE handles/work, frees descriptors, drops GPIO device refs, and frees FIFOs.

## Dependencies And Integration Points
The file depends on anon inodes, cdev, file descriptor allocation helpers, kfifo, wait queues, poll, mutex/spinlock/SRCU, IRQ APIs, workqueues, timekeeping, uaccess, HTE, pinctrl, and UAPI structures from `uapi/linux/gpio.h`. It integrates with descriptor state notifications emitted elsewhere in gpiolib, gpiochip unregister notification, pinctrl line availability checks, and the userspace libgpiod ABI.

## Risks
This is a concurrency-heavy userspace ABI surface. Risks include descriptor lifetime during gpiochip removal, event FIFO overflow semantics, line reconfiguration racing with IRQ/debounce callbacks, compatibility ABI size differences, HTE sequence accounting, correct active-low inversion for edge triggers, and preserving exact ioctl validation behavior. The code deliberately accepts slightly stale reads for some per-line fields; changing those assumptions can introduce locking regressions.

## Test Signals
Test with libgpiod v2 requests for input, output, multi-line values, per-line attributes, debounce, realtime and monotonic clocks, HTE-enabled clocks, reconfiguration, and edge polling/reading. Exercise v1 handle and event ioctls when enabled, 32-bit compat ioctls, line-info watch/unwatch mixed ABI rejection, chip unregister while fds are open, FIFO overflow, invalid padding/flags, nonblocking reads, and proc fdinfo output.
