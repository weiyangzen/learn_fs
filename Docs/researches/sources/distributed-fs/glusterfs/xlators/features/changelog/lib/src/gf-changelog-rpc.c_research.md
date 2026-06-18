# sources/distributed-fs/glusterfs/xlators/features/changelog/lib/src/gf-changelog-rpc.c

## Purpose
Provides the libgfchangelog client-side probe RPC used to contact a brick’s changelog xlator and request reverse event delivery.

## APIs, Types, and Functions
`gf_changelog_rpc_init()` hashes the brick path into the well-known changelog Unix socket path and calls `changelog_rpc_client_init()`. `gf_probe_changelog_filter()` builds a `changelog_probe_req` containing the reverse socket path and notification filter, then submits `CHANGELOG_RPC_PROBE_FILTER`. `gf_changelog_invoke_rpc()` wraps `changelog_invoke_rpc()`. `gf_changelog_procs` and `gf_changelog_clnt` define the client RPC program table for `CHANGELOG_RPC_PROGNUM`/version 1.

## Control Flow, State, and Persistence
There is no on-disk persistence. A connection is opened to `/var/run`-style changelog socket derived by `CHANGELOG_MAKE_SOCKET_PATH()`, a frame is created by common RPC code, and the probe request tells the server where to connect back. Notification handling is currently a no-op across connect, disconnect, message, destroy, and ping events.

## Dependencies and Integration
Depends on `gf-changelog-rpc.h`, `changelog-rpc-common.h`, `changelog-misc.h`, XDR serialization for `changelog_probe_req`, and the `gf_changelog_t` connection structure. It is orchestrated by `gf_changelog_setup_rpc()` after the reverse listener is created.

## Risks and Test Signals
Risks include copying `strlen(sock)` bytes without explicit NUL assignment into the XDR string field, lack of connection-state handling, and reliance on sleep-based timing in the caller before probe. Test signals include successful probe filter submission, malformed or long reverse socket paths, brick socket path hashing, and behavior when RPC connect/start succeeds but probe fails.
