# sources/distributed-fs/glusterfs/xlators/meta/src/active-link.c

## Purpose
Implements the `active` symlink in the meta filesystem, pointing at the active graph UUID.

## Important APIs, Types, and Functions
- `active_link_fill()` writes `this->ctx->active->graph_uuid` into the strfd.
- `active_link_ops` exposes `.link_fill`.
- `meta_active_link_hook()` attaches the ops to the inode.

## Control Flow
On lookup/hook, `meta_active_link_hook()` sets inode ops. Later readlink calls invoke `active_link_fill()`.

## State and Persistence
Reads runtime context active graph pointer; no owned state.

## Dependencies and Integration Points
Depends on meta ops helpers and GlusterFS context graph state. Referenced by `graphs-dir.c`.

## Risks
Assumes `this->ctx->active` is valid. Active graph changes should be reflected dynamically because fill reads context at access time.

## Test Signals
Meta filesystem readlink for `graphs/active` should return current active graph UUID.
