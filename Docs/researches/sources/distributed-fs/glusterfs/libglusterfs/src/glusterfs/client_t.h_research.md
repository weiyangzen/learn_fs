# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/client_t.h

## Purpose
`client_t.h` declares the core GlusterFS client identity object, authentication data shared with RPC, client table entries, client context storage, and diagnostics/disconnect APIs.

## Important APIs, Types, and Functions
- `client_auth_data_t`: RPC-compatible auth flavour, length, and fixed 400-byte data payload.
- `struct client_ctx`: key/value scratch context entries.
- `client_t`: atomic bind/count refs, bound/current xlators, table index, opversion, auth info, subdir mount state, fd counter, scratch context lock/table, and flexible `client_uid`.
- `clienttable_t` and `cliententry_t`: free-list table for `client_t *` entries.
- `gf_client_get()`, `gf_client_ref()`, `gf_client_unref()`, `gf_client_put()`: lifecycle and table ownership.
- `client_ctx_set/get/del/dump()`: per-client scratch context helpers.
- fdtable/inode dump helpers and `gf_client_disconnect()`.

## Control Flow
The header defines table constants and APIs; implementation uses a free-list table similar to fd tables, atomic reference counters for client lifetime, and scratch context slots guarded by `scratch_ctx_lock`. Client get locates or creates a client using xlator/auth/uid/subdir identity.

## State and Persistence
Client state is in memory. It tracks identity, auth, subdir root inode/GFID, open fd count for detach behavior, and per-client scratch contexts. Diagnostics export state to dicts or statedump output.

## Dependencies and Integration Points
Depends on Gluster locks, atomics, xlator/inode/dict types, and RPC authentication conventions. It is central to server-side connection management, translator client callbacks, detach/disconnect flows, and per-client fd/inode accounting.

## Risks and Edge Cases
- Flexible array `client_uid[]` requires allocation sized for the UID string.
- Auth data exists in both fixed and dynamic forms; comparisons must avoid length/termination mistakes.
- Scratch context table starts fixed-size; implementation must handle collisions or expansion carefully.
- Disconnect must coordinate refs, bind state, fd counts, and translator callbacks.

## Test Signals
Test client lookup/create identity matching, ref/unref teardown, table expansion/free-list behavior, auth comparison with binary data, subdir mount fields, scratch context set/get/delete, disconnect callback behavior, and fd/inode dump outputs.
