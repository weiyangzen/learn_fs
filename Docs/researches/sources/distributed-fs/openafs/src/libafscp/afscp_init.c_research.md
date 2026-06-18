## sources/distributed-fs/openafs/src/libafscp/afscp_init.c

Purpose: Initializes and finalizes the RX runtime and callback service required by `libafscp`.

Important APIs and functions: `afscp_Init` starts RX with `rx_Init(0)`, starts a callback server through `start_cb_server`, and optionally sets the default cell. `afscp_Finalize` returns callbacks, frees cell and server registries, finalizes RX, and closes the callback service socket. `start_cb_server` creates a null server security object and an RX service using `RXAFSCB_ExecuteRequest`.

Control flow: Initialization is guarded by a static `init` state. Calls after successful initialization return immediately. `start_cb_server` registers service id 1 named `afs` and invokes `rx_StartServer(0)`. Finalization does not reset `init`, so it is effectively a terminal cleanup path rather than a restartable lifecycle.

State and persistence: Maintains static RX security class and service pointers, plus `init`. It also triggers cleanup of global callback, cell, and server process state. No durable persistence.

Dependencies and integration: Depends on RX, rxnull, callback server dispatch from `afscp_internal.h`, and the server/cell/callback modules. Must be called before network operations that expect RX connections and callback handling.

Risks: `afscp_Finalize` dereferences `serv` after `rx_Finalize`; if callback server startup partially failed, finalization assumptions may not hold. The `init` flag is not cleared, preventing clean reinitialization in the same process. `rx_StartServer(0)` behavior is global and may interact with embedding applications already using RX.

Test signals: Check idempotent double initialization, initialization with explicit and default cells, callback server creation failure, finalize after partial init, and repeated init/finalize expectations for embedded users.
