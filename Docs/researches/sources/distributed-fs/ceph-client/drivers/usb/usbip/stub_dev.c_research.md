# sources/distributed-fs/ceph-client/drivers/usb/usbip/stub_dev.c

## Purpose

`stub_dev.c` binds selected physical USB devices for export through USB/IP. It exposes per-device sysfs controls, accepts a userspace-provided TCP socket, starts host RX/TX threads, and implements shutdown/reset/unusable event operations.

## Important APIs, Types, and Functions

Sysfs attributes are `usbip_status` and write-only `usbip_sockfd`. `stub_device_alloc()` initializes `struct stub_device`, common event-handler ops, URB/unlink lists, and stable `devid`. `stub_probe()` checks the bus-id table, rejects hubs and VHCI devices, sets driver data, and claims the hub port. `stub_shutdown_connection()`, `stub_device_reset()`, and `stub_device_unusable()` are common event callbacks. `stub_disconnect()` releases the hub port, shuts down active USB/IP state, and restores bus-id status.

## Control Flow

Userspace first adds a busid through driver sysfs, causing probe to claim matching devices. Writing a nonnegative socket fd to `usbip_sockfd` validates availability and socket type, creates `stub_rx` and `stub_tx` kthreads, stores socket/task state, and marks the device used. Writing `-1` queues a down event. Disconnect or removal queues a removed event and waits for event handling unless already inside the event handler.

## State and Persistence Behavior

Per-device state includes socket, task pointers, status, URB lists, and bus-id shutdown flags. It does not persist beyond module/device lifetime; userspace must re-add bus IDs after reload.

## Dependencies and Integration Points

It integrates with USB device-driver binding, hub port claiming, sysfs, sockets via `sockfd_lookup()`, kthreads, the common USB/IP event handler, and `stub_main` bus-id tables.

## Risks and Test Signals

Risks include socket/task setup races, leaving a claimed hub port on error, disconnect during reset, event-handler reentrancy, and bus-id status restoration. Test signals include export attach/detach, invalid fd/type handling, hub/VHCI rejection, physical disconnect during active export, remote reset event, and module unload cleanup.
