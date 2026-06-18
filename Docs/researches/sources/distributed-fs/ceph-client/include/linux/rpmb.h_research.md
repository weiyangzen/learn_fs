# sources/distributed-fs/ceph-client/include/linux/rpmb.h

## Purpose
`rpmb.h` defines the kernel interface for Replay Protected Memory Block devices backed by eMMC, UFS, or NVMe storage.

## Important APIs, types, and functions
Key types are `enum rpmb_type`, `struct rpmb_descr`, `struct rpmb_dev`, and wire-format `struct rpmb_frame`. Request constants include `RPMB_PROGRAM_KEY`, `RPMB_GET_WRITE_COUNTER`, `RPMB_WRITE_DATA`, `RPMB_READ_DATA`, and `RPMB_RESULT_READ`. Enabled APIs include `rpmb_dev_get()`, `rpmb_dev_put()`, `rpmb_dev_find_device()`, `rpmb_interface_register()`, `rpmb_interface_unregister()`, `rpmb_dev_register()`, `rpmb_dev_unregister()`, and `rpmb_route_frames()`; disabled builds return `NULL` or `-EOPNOTSUPP`.

## Control flow, state, and persistence
Storage drivers provide `struct rpmb_descr`, including device ID, capacity, reliable write count, and a `route_frames()` callback, then register an `rpmb_dev`. Consumers find/get the device, construct one or more 512-byte `rpmb_frame` requests, and route frames through the provider. Persistent state is hardware-backed: authentication key programming, write counters, and RPMB data survive reboots; kernel state is the registered device and class-interface list.

## Dependencies and integration points
It depends on the device model, list handling, big-endian integer types, and storage-specific block transports. It integrates with trusted execution environments, key derivation using `dev_id`, eMMC/UFS/NVMe RPMB providers, and class-interface notification.

## Risks and test signals
Risks include programming an irreversible authentication key, wrong frame endianness, mismatched request/response frame counts, stale write counters, unreliable writes exceeding `reliable_wr_count`, and exposing unauthenticated data paths. Test signals include register/unregister lifetime tests, frame routing for all request types, MAC/counter validation with a known device or emulator, disabled-config stubs, and error injection in transport callbacks.
