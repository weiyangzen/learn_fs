<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls_toe.c -->
# sources/distributed-fs/ceph-client/net/tls/tls_toe.c

## Purpose
`tls_toe.c` supports TCP offload engines that handle TLS records outside the normal software/device kTLS paths. It maintains a registry of TOE devices, lets a device claim a socket during ULP initialization, and forwards hash/unhash events to registered devices.

## Important APIs, Types, and Functions
- Global `device_list` and `device_spinlock` protect registered `struct tls_toe_device` entries.
- `tls_toe_register_device()` and `tls_toe_unregister_device()` are exported for TOE drivers.
- `tls_toe_bypass()` scans devices, calls their `feature()` predicate, creates a TLS context, marks both directions `TLS_HW_RECORD`, swaps the socket destructor, and installs TOE proto operations.
- `tls_toe_hash()` and `tls_toe_unhash()` wrap the underlying TCP proto hash/unhash while invoking device callbacks under kref protection.
- `tls_toe_sk_destruct()` restores ULP data and frees the TLS context after the original destructor runs.

## Control Flow
During `tls_init()`, the TOE path can return `1` from `tls_toe_bypass()`, indicating the socket was claimed and normal kTLS context setup should be skipped. Later, when the socket is inserted or removed from TCP hashes, TLS proto operations call `tls_toe_hash()`/`tls_toe_unhash()`, which invoke all registered device callbacks and then delegate to the original protocol. On socket destruction, the saved destructor is called and the TOE TLS context is cleared.

## State and Persistence
The device registry is process-global and protected by a BH spinlock. Per-socket state is a normal `tls_context`, but configured as `TLS_HW_RECORD` in both directions and with saved destructor/proto callbacks. Device references are temporarily pinned with `kref_get()` while callbacks execute outside the registry lock.

## Dependencies and Integration Points
This file integrates with `tls_main.c` protocol matrices under `CONFIG_TLS_TOE`, `net/tls_toe.h` device driver contracts, inet connection socket ULP data, and TCP hash/unhash lifecycle.

## Risks and Edge Cases
The registry can change while callbacks execute, so the kref protocol is critical. `tls_toe_hash()` ORs callback errors and calls unhash on failure, so device callbacks must tolerate cleanup after partial success. `tls_toe_bypass()` currently returns `0` if context allocation fails, which lets normal TLS init continue rather than surfacing allocation failure from the TOE claim path.

## Test Signals
TOE driver tests should register/unregister devices, claim and reject sockets through `feature()`, force hash callback failures, race unregister with hash/unhash, and validate that socket destruction clears ULP data and frees TLS context exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls_toe.c -->
