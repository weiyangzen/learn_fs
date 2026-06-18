## sources/distributed-fs/ceph-client/include/linux/ccp.h

**Purpose:** This header defines the client-facing command interface for AMD Cryptographic Coprocessor (CCP) operations.

**Important APIs/types/functions:** Config-gated APIs are `ccp_present()`, `ccp_version()`, and `ccp_enqueue_cmd()`, stubbing to `-ENODEV`/0 when CCP support is unavailable. It defines operation enums and parameter structs for AES, XTS-AES, SHA/HMAC, 3DES, RSA, passthrough, no-DMA passthrough, and ECC. `enum ccp_engine` selects the engine. `struct ccp_cmd` contains driver-owned list/work/device/return fields, flags (`CCP_CMD_MAY_BACKLOG`, `CCP_CMD_PASSTHRU_NO_DMA_MAP`), selected engine, engine error, a union of engine parameters, completion callback, and callback data.

**Control flow, state, persistence:** Clients fill a `ccp_cmd`, submit it, and receive completion through callback. Backlog-capable commands may complete first with `-EINPROGRESS` when promoted from backlog. Scatterlists and IV/hash contexts may be both input and output for certain engines. No data persists except hardware/driver queue state and caller buffers.

**Dependencies/integration:** Depends on scatterlists, workqueues, lists, DMA addresses, and crypto constants. Integrated by crypto API drivers and hardware acceleration users.

**Risks and test signals:** Risks include missing required fields per engine, invalid scatterlist lifetimes, callback races, unhandled backlog returns, IV/context mutation surprises, and config-off behavior. Test signals include crypto selftests for each engine/mode, async completion/backlog tests, DMA mapping debug, hardware error injection, and module unload with queued commands.
