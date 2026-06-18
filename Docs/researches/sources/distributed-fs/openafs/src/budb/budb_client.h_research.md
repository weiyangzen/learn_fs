<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/budb_client.h -->
# sources/distributed-fs/openafs/src/budb/budb_client.h

## Purpose
Defines the client-side handles used by OpenAFS backup database consumers. The file is small, but it is the public shape for connecting to the Ubik replicated budb service and for caching typed text payloads.

## Important APIs, Types, And Functions
`udbHandleS` stores the RX security index/object, per-server `rx_connection` array, `ubik_client` handle, and client `instanceId`. `udbClientTextS` names a text object, carries its `textType`, cached `textVersion`, held `lockHandle`, byte size, and optional `FILE *` stream. `UF_SINGLESERVER` and `UF_END_SINGLESERVER` flag single-server Ubik calls.

## Control Flow
The header has no executable flow. Client code initializes a `udbHandleT`, establishes server connections, obtains a lock/instance via RPCs, then uses `udbClientTextT` metadata to fetch, cache, or replace server-side text blocks.

## State And Persistence
All state is client memory, except the fields mirror persistent server state: text versions/locks and Ubik server connections. A stale `lockHandle` or `textVersion` directly affects atomic text updates.

## Dependencies And Integration Points
It depends on `ubik.h`, RX/XDR, `afs/budb.h`, and `budb_errs.h`. It is consumed by backup clients and admin tools that talk to the budb RPC interface.

## Risks And Test Signals
Risks are ABI drift against generated RPC structures and misuse of stale lock handles. Signals are successful authenticated/noauth client connection setup, text version checks, lock acquisition/release, and single-server operation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/budb/budb_client.h -->
