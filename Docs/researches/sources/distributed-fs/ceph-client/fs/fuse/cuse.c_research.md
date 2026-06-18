# sources/distributed-fs/ceph-client/fs/fuse/cuse.c

## Purpose
`cuse.c` implements CUSE, a FUSE-based mechanism for userspace character devices. A daemon opens `/dev/cuse`, completes a `CUSE_INIT` handshake, and the kernel creates a character device whose operations are proxied through FUSE requests.

## Important APIs, Types, and Functions
- `struct cuse_conn` embeds a dummy `fuse_mount`, a `fuse_conn`, and the created `cdev`/`device`.
- Frontend ops `cuse_read_iter()`, `cuse_write_iter()`, `cuse_open()`, `cuse_release()`, and ioctl wrappers forward to FUSE direct I/O/open/release/ioctl helpers.
- `cuse_parse_one()` and `cuse_parse_devinfo()` parse NUL-packed init strings such as `DEVNAME=...`.
- `cuse_send_init()` sends the asynchronous `CUSE_INIT` request.
- `cuse_process_init_reply()` validates the daemon reply and creates/registers the chrdev.
- `cuse_channel_open()`/`cuse_channel_release()` own `/dev/cuse` server channel lifetime.

## Control Flow
Opening `/dev/cuse` allocates `cuse_conn`, initializes a FUSE connection using the opener's user namespace, installs a FUSE device, marks the connection initialized, sends `CUSE_INIT` in the background, and stores the device handle in the channel file. When the daemon replies, the callback checks protocol version, records limits and flags, parses `DEVNAME`, reserves a device number, allocates a `struct device` and `struct cdev`, checks name uniqueness under `cuse_lock`, registers both, inserts the connection into a hash table by dev_t, and emits a uevent. Opening the created char device looks up the connection, takes a ref, and calls `fuse_do_open()`. Channel release removes the connection from the table, unregisters device/cdev, and releases the FUSE device.

## State and Persistence
State is in the global `cuse_conntbl`, a global class, per-connection FUSE state, `cdev`, and `struct device`. It persists only while the server channel is open. `unrestricted_ioctl` is negotiated during initialization and affects ioctl forwarding flags.

## Dependencies and Integration Points
CUSE builds on `fuse_dev_operations`, `fuse_direct_io`, `fuse_do_open`, `fuse_sync_release`, `fuse_do_ioctl`, Linux cdev/device/misc subsystems, sysfs attributes, and module init/exit. It deliberately disables `FUSE_DEV_IOC_CLONE` for the CUSE channel.

## Risks
Initialization is asynchronous, so error paths must free folios, init args, device numbers, and partially registered devices. Device-name uniqueness is enforced only within the CUSE table. Channel close is authoritative and can remove the character device while opens race; the lookup/refcount path must handle `-ENODEV`. The server is responsible for write locking and sanity checks for char-device I/O.

## Test Signals
Exercise successful CUSE device creation, malformed init info, missing `DEVNAME`, duplicate names, explicit major/minor conflicts, server death during init, frontend read/write/ioctl/poll, sysfs `waiting`/`abort`, and module unload after devices are removed.
