# sources/distributed-fs/ceph-client/drivers/usb/misc/usb-ljca.c

## Purpose
`usb-ljca.c` is the Intel La Jolla Cove Adapter USB bridge driver. It binds the LJCA USB device, establishes a vendor message protocol over bulk endpoints, enumerates GPIO/I2C/SPI functions exposed by firmware, and creates auxiliary devices for subsystem-specific client drivers.

## Important APIs, Types, and Functions
`struct ljca_adapter` owns the USB interface, bulk pipes, one persistent RX URB, RX/TX buffers, command response buffer pointers, a spinlock for shared packet state, a mutex that serializes command transmission, a completion for command acknowledgements, a client list, a disconnect flag, and a reset sequence ID. The protocol header is `struct ljca_msg` with type, command, flags, length, and counted payload.

Exported APIs in namespace `LJCA` are `ljca_transfer`, `ljca_transfer_noack`, `ljca_register_event_cb`, and `ljca_unregister_event_cb`. They are used by auxiliary client drivers through `struct ljca_client` from `linux/usb/ljca.h`. Core internal functions include `ljca_send`, `ljca_recv`, `ljca_handle_cmd_ack`, `ljca_handle_event`, `ljca_reset_handshake`, `ljca_enumerate_gpio`, `ljca_enumerate_i2c`, `ljca_enumerate_spi`, and `ljca_new_client_device`.

## Control Flow
`ljca_probe` allocates the adapter and TX buffer, initializes locks and completion, finds the first bulk-in and bulk-out endpoints, allocates an RX buffer and URB, submits the RX URB, and then performs client enumeration. RX completion validates message length; ACK messages complete the current command after copying payload into the waiting external buffer, while non-ACK messages are dispatched as events to a matching client callback. `ljca_send` serializes commands with `adap->mutex`, prepares the TX header under spinlock, takes an autosuspend reference, sends a bulk message, optionally waits for ACK completion, clears transient response pointers, and releases runtime PM.

Enumeration first performs a management reset handshake with a monotonically increasing reset ID. It then asks firmware for GPIO, I2C, and SPI descriptors, validates response lengths with `struct_size`, builds platform data, binds ACPI companions where possible, initializes auxiliary devices, and adds them to the client list. Disconnect sets `disconnect`, kills the RX URB, deletes and uninitializes auxiliary devices in reverse order, frees the RX URB, and destroys the mutex. Suspend kills RX; resume resubmits it.

## State and Persistence
State is volatile and centered on the adapter object and auxiliary client list. Command response state (`ex_buf`, `ex_buf_len`, `actual_length`) is valid only while `ljca_send` holds the command mutex. Event callbacks are protected by each client's spinlock. ACPI companion binding persists in device model state for the lifetime of each auxiliary device. There is no disk persistence.

## Dependencies and Integration Points
The driver depends on USB bulk messaging, runtime PM/autosuspend, ACPI enumeration, the Linux auxiliary bus, completions, mutexes, spinlocks, and exported LJCA headers. It integrates with GPIO, I2C, and SPI child drivers by auxiliary device names `ljca-gpio`, `ljca-i2c`, and `ljca-spi`, plus platform data structures describing valid pins, bus capacity, and interrupt pins.

## Risks and Edge Cases
The protocol supports only one in-flight command because a single TX buffer, response pointer pair, and completion are shared. Firmware events are matched only by client type; a comment notes that multiple clients of the same type would need an ID in the firmware message. `ljca_handle_event` calls the registered callback for a matching type; event arrival before callback registration or after unregistration is a key race to reason about. ACK mismatch logs an error but leaves the sender waiting for timeout. Enumeration treats SPI timeout as normal, but GPIO/I2C descriptor failures abort the whole adapter and tear down already-created clients. Suspend kills RX, so command users must tolerate failed or delayed transfers across PM transitions.

## Test Signals
Tests should cover successful reset handshake, GPIO/I2C/SPI descriptor parsing with exact and malformed lengths, auxiliary-device creation and ACPI companion matching, ACK mismatch and timeout behavior, event callback registration/unregistration, disconnect while a command waits, suspend/resume RX URB resubmission, and runtime PM reference balancing during `ljca_transfer`.
