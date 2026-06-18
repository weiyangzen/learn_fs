<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/afscp_callback.c -->
# sources/distributed-fs/openafs/src/tests/afscp_callback.c

## Purpose
Provides minimal RXAFSCB callback service implementations needed by `afscp.c` so fileservers can probe or identify the client during direct RX fetch/store tests.

## Important APIs, Types, And Functions
Defines globals `afs_cb_inited` and `afs_cb_interface`, helper `init_afs_cb`, and many `SRXAFSCB_*` RPC handlers. Most handlers return success with no data or `RXGEN_OPCODE`; `WhoAreYou` and `ProbeUuid` return meaningful interface/UUID data.

## Control Flow
`init_afs_cb` creates a UUID, gathers local interface addresses with `rx_getAllAddr`, converts addresses to host byte order for XDR, and marks initialized. `WhoAreYou` lazily initializes and copies the interface address. `ProbeUuid` compares the supplied UUID to the local callback UUID.

## State And Persistence
Only transient process globals store callback UUID and interface addresses. No disk state is written.

## Dependencies And Integration Points
Compiled with `afscp.c`, OpenAFS callback interface definitions, RX utilities, and the RX callback service registered by `start_cb_server`.

## Risks And Test Signals
Most callbacks are stubs, so this is sufficient for simple copy tests but not cache manager behavior validation. Multihomed address handling depends on `AFS_MAX_INTERFACE_ADDR`. Signals are fileserver callbacks/probes succeeding during `afscp` transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/afscp_callback.c -->
