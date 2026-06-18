# File Research: sources/block-storage/stratisd/src/dbus/manager/manager_3_8/methods.rs

Purpose: Implements r8 manager `create_pool_method` and `start_pool_method`.

Create pool behavior:
- Accepts multiple key descriptions and Clevis entries with optional token slots.
- Parses Clevis JSON strings into `serde_json::Value`.
- Builds `InputEncryptionInfo`.
- Accepts integrity settings: journal size, integrity tag spec, and allocate-superblock flag.
- Calls `engine.create_pool` with an `IntegritySpec`.
- On creation, registers the pool and returns pool path plus blockdev paths.

Start pool behavior:
- Accepts id/id_type, nested optional unlock method, and optional key file descriptor.
- Converts zbus `Fd` into raw fd using `AsRawFd`.
- Calls `engine.start_pool(..., key_fd, false)`.
- Registers filesystems, pool, and block devices on success.
- Emits locked-pools and stopped-pools signals as appropriate.

Failure handling:
- Invalid UUID, unknown id type, bad JSON, invalid integrity tag spec, engine errors, and D-Bus registration errors are converted to D-Bus return tuples.
