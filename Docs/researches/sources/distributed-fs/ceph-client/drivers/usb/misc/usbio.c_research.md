# sources/distributed-fs/ceph-client/drivers/usb/misc/usbio.c

## Purpose
`usbio.c` is the Intel USBIO Bridge driver. It binds USBIO bridge devices, negotiates firmware/control information, enumerates GPIO banks and I2C buses, exposes child functions as auxiliary devices, and exports bridge transfer helpers for those child drivers.

## Important APIs, Types, and Functions
`struct usbio_device` owns the USB interface, quirks, control and bulk mutexes, endpoint pipes and buffers, one persistent bulk-in URB, a completion for response packets, auxiliary client list, and discovered GPIO/I2C descriptors. `struct usbio_client` wraps each auxiliary device and protects its bridge pointer with a mutex.

Exported namespace `USBIO` APIs are `usbio_control_msg`, `usbio_bulk_msg`, `usbio_acquire`, `usbio_release`, `usbio_get_txrxbuf_len`, `usbio_get_quirks`, and `usbio_acpi_bind`. Internal protocol helpers include `usbio_ctrl_msg`, `usbio_bulk_recv`, `usbio_add_client`, `usbio_enum_gpios`, and `usbio_enum_i2cs`.

## Control Flow
Probe allocates and initializes `struct usbio_device`, determines endpoint-zero max packet for the control buffer, finds the first bulk-in/out endpoints, applies quirks such as 63-byte bulk max packet, allocates TX/RX buffers and a persistent RX URB, submits the URB, and performs serialized control commands: handshake, protocol version, firmware version, GPIO enumeration, and I2C enumeration. It then creates one `USBIO_GPIO_CLIENT` auxiliary device and one `USBIO_I2C_CLIENT` per bus descriptor.

`usbio_control_msg` locks the client, takes a runtime PM reference, serializes on `ctrl_mutex`, and sends an endpoint-zero vendor packet. `usbio_bulk_msg` is called while the client and bridge bulk mutex are already held by `usbio_acquire`; it optionally sends a bulk packet and waits for the persistent RX URB to complete a matching response. Disconnect completes any waiters, sets every client's bridge pointer to `NULL`, kills/frees the URB, and deletes/uninitializes auxiliary devices.

## State and Persistence
Bridge state is volatile: descriptors are cached from firmware, auxiliary devices point into those cached descriptor arrays as platform data, and the bridge pointer becomes `NULL` on disconnect. The persistent RX URB is resubmitted after every completion and again on resume. Quirks come from `usb_device_id.driver_info`.

## Dependencies and Integration Points
The driver depends on USB control/bulk APIs, auxiliary bus, ACPI companion matching, completions, mutexes, cleanup guards, and `linux/usb/usbio.h`. It integrates with child GPIO/I2C drivers through auxiliary device names and exported transfer APIs. USB IDs include Lattice NX40/NX33/NX33U and Synaptics Sabre variants with per-device quirks.

## Risks and Edge Cases
The split locking contract is important: `usbio_bulk_msg` asserts that callers hold both the client mutex and `bulk_mutex`, while `usbio_acquire` deliberately leaves the client locked until `usbio_release` to avoid ABBA deadlocks. Disconnect must not free `usbio_device` until clients can no longer enter bridge operations; it sets bridge pointers under each client mutex before killing the URB. `usbio_bulk_recv` resubmits the URB even after errors other than `-ENOENT`, and return handling of that resubmit is not checked. Control timeout is defined as zero, so endpoint-zero behavior depends on USB core semantics for zero timeout. Auxiliary creation return values in enumeration are ignored, which can hide partial child-device creation failures.

## Test Signals
Validation should cover control handshake and descriptor parsing, quirk-specific buffer sizing, bulk request/response matching, unsupported bulk-command `-EPIPE` behavior, acquire/release lock ordering under lockdep, disconnect while clients wait, suspend/resume URB lifecycle, ACPI binding by HID/UID, and partial auxiliary-device add failures.
