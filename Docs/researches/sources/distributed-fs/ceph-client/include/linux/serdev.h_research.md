# sources/distributed-fs/ceph-client/include/linux/serdev.h

Purpose: `serdev.h` defines the serial device bus abstraction that lets devices attached behind UART controllers bind to normal device drivers instead of ad hoc line-discipline plumbing.

Important APIs/types/functions: Core types are `struct serdev_device_ops`, `struct serdev_device`, `struct serdev_device_driver`, `enum serdev_parity`, `struct serdev_controller_ops`, and `struct serdev_controller`. APIs include device/controller allocation/add/remove/put helpers, driver register/unregister macros, open/close, devm open, baudrate, flow control, write buffer/write blocking/write flush/wait, modem control, break control, parity, TTY-port registration, ACPI UART resource lookup, and OF controller lookup.

Control flow: A UART controller registers a `serdev_controller`; discovery creates a `serdev_device`; a client driver binds, sets receive/write-wakeup ops, opens the device, configures serial parameters, and exchanges data through controller callbacks. Receive and write-wakeup calls flow from controller to client ops.

State and persistence behavior: Device/controller objects are device-model managed. `serdev_device` stores ops, completion, and write mutex; `serdev_controller` stores host, bus number, attached serdev, and ops. Open state, modem signals, and queued writes are maintained by implementation code.

Dependencies and integration points: It depends on the device model, completions, mutexes, termios, polling helpers, TTY core, ACPI, OF, and serial controller drivers. Disabled configs return `-ENODEV`, `-EOPNOTSUPP`, false, or NULL stubs.

Risks: `write_wakeup` must not sleep, while `receive_buf` may sleep. Controller callbacks must handle partial writes and lifetime of attached devices. Matching release/unregister functions are needed to avoid dangling device references.

Test signals: Controller add/remove, client probe/remove/shutdown, disabled config stubs, blocking writes with timeout, partial write wakeups, RX callback byte counts, CTS polling, RTS/parity/break controls, TTY-port bridge registration, ACPI/OF discovery, and hot-unplug races.
