# sources/distributed-fs/ceph-client/fs/nfs/nfs40.h

## Purpose
`nfs40.h` declares the NFSv4.0 minor-version-specific client and recovery hooks shared between NFSv4.0 client setup and procedure handling files.

## Important APIs, Types, And Functions
The header declares `nfs40_shutdown_client()`, `nfs40_init_client()`, `nfs40_handle_cb_pathdown()`, extern `nfs_v4_0_minor_ops`, and `nfs40_discover_server_trunking()`.

## Control Flow And Integration Points
`nfs40client.c` implements client initialization, shutdown, callback path-down handling, and server trunking discovery. `nfs40proc.c` exports `nfs_v4_0_minor_ops`, which references those functions and installs NFSv4.0 sequence, lease renewal, migration, and recovery behavior into the common NFSv4 code.

## State And Persistence Behavior
The header holds no state directly. It exposes functions that allocate/free the NFSv4.0 slot table, update client callback state, and participate in client ID/trunking state transitions.

## Dependencies
Dependencies include NFSv4 client structures, credentials, and the `struct nfs4_minor_version_ops` type from the broader NFSv4 implementation.

## Risks And Edge Cases
Because this header separates NFSv4.0 behavior from later minor versions, declarations must match implementation exactly. The trunking discovery API returns either an existing client or the probed client; callers must honor reference and readiness semantics.

## Test Signals
Build NFSv4.0, mount `vers=4,minorversion=0`, trigger callback path-down recovery, exercise trunked server discovery, and run state recovery after server reboot and lease expiry.
