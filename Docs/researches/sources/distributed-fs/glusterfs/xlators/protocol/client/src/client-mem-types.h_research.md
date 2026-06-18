# sources/distributed-fs/glusterfs/xlators/protocol/client/src/client-mem-types.h

## Purpose

`client-mem-types.h` defines memory-accounting type IDs for allocations owned by the protocol/client xlator. These IDs let Gluster's memory accounting and statedump tooling attribute client configuration, request buffers, fd contexts, and lock migration request nodes to the client component.

## Important APIs, types, and functions

- `enum gf_client_mem_types_` starts at `gf_common_mt_end + 1` to avoid overlap with common allocation IDs.
- `gf_client_mt_clnt_conf_t` accounts `clnt_conf_t` allocations.
- `gf_client_mt_clnt_req_buf_t` accounts client request buffers.
- `gf_client_mt_clnt_fdctx_t` accounts `clnt_fd_ctx_t` allocations used for saved remote fd state.
- `gf_client_mt_clnt_lock_request_t` accounts serialized active-lock migration request list nodes.
- `gf_client_mt_end` marks the end of this component's memory type range.

## Control flow

The header has no runtime control flow. Its enum values are consumed by `GF_CALLOC`, `GF_MALLOC`, and related memory-accounted allocation calls in client implementation files.

## State and persistence behavior

There is no runtime state here. The enum values are stable process-local identifiers used by memory accounting; changing or reordering them affects diagnostics rather than on-disk data.

## Dependencies and integration points

The file includes `<glusterfs/mem-types.h>` for `gf_common_mt_end`. `client.h`, `client-rpc-fops_v2.c`, and helper code use these IDs when allocating fd contexts and lock request structures. Gluster memory accounting and statedump infrastructure consume the resulting allocation categories.

## Risks and edge cases

- New client allocation classes should be appended before `gf_client_mt_end`; inserting or reusing values can confuse memory diagnostics.
- If code allocates client-owned objects with common or wrong memory types, leak reports become less useful.
- The enum is tiny, so missing IDs may encourage overloading existing categories.

## Test signals

Compile coverage verifies enum visibility. Memory-accounting or statedump tests should show `clnt_fd_ctx_t` allocations under `gf_client_mt_clnt_fdctx_t` and active lock request nodes under `gf_client_mt_clnt_lock_request_t`.
