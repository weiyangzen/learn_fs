# sources/distributed-fs/ceph-client/drivers/staging/greybus/authentication.c

## Purpose

`authentication.c` implements the kernel-side Greybus Component Authentication Protocol char-device bridge. It creates one `/dev/gb-authenticate-*`-style device per CAP connection and exposes ioctls for endpoint UID, IMS certificate retrieval, and authentication.

## Important APIs, Types, and Functions

Core state is `struct gb_cap`, containing parent device, Greybus connection, kref/list membership, disabled flag, mutex, cdev, class device, and dev_t. Protocol helpers are `cap_get_endpoint_uid()`, `cap_get_ims_certificate()`, and `cap_authenticate()`. File operations are `cap_open()`, `cap_release()`, and `cap_ioctl_unlocked()`. Lifecycle functions are `gb_cap_connection_init()`, `gb_cap_connection_exit()`, `cap_init()`, and `cap_exit()`.

## Control Flow

Connection init allocates `gb_cap`, initializes locking/refcounting, adds it to a global lookup list, enables the Greybus connection, allocates a minor, adds a cdev, and creates the class device. Open finds the matching cdev under the global list lock and takes a kref. Ioctl serializes all operations with `cap->mutex`, refuses new work after disable, takes a runtime PM reference, dispatches to protocol helpers, copies results to user space, and autosuspends. Exit removes the device node and cdev, marks disabled while waiting for active ioctls, disables the connection, removes list visibility, and drops the final reference.

## State and Persistence Behavior

State is volatile per connection plus global class/minor/list state. The ioctls exchange authentication data but do not persist it in kernel storage. Module authentication outcome lives in module firmware/security state and user buffers.

## Dependencies and Integration Points

It depends on Greybus operation APIs, runtime PM, Linux cdev/class/device infrastructure, IDA minor allocation, uaccess helpers, krefs, and UAPI definitions in `greybus_authentication.h`. Firmware class init/exit code calls `cap_init()`/`cap_exit()` and connection init/exit.

## Risks and Edge Cases

Variable-length certificate/signature responses compute `payload_size - sizeof(*response)` without explicitly checking underflow or user-structure capacity beyond protocol limits. All ioctls are serialized, which avoids parallel authentication but can block unrelated UID/certificate queries. `CAP_TIMEOUT_MS` is defined but unused here. Open handles disconnect through krefs, but any missed list/kref ordering would become a use-after-free risk.

## Test Signals

Test open during disconnect, ioctl during disconnect, concurrent ioctls, minor exhaustion, cdev/device-create failures, short Greybus responses, oversized certificates/signatures, copy_to/from_user failures, PM get failures, and class init/exit rollback.
