# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_cmdbuf_res.c

## Purpose
Implements a per-context command-buffer resource manager. It tracks resources created or destroyed through command-buffer execution, stages additions/removals during execbuf validation, and commits or reverts those changes depending on whether command submission succeeds.

## Important APIs, Types, And Functions
- `struct vmw_cmdbuf_res_manager` owns a hash table of staged/committed resources and a list of committed resources.
- `struct vmw_cmdbuf_res` stores a refcounted `vmw_resource`, hash item, list node, staging state, and owning manager.
- `vmw_cmdbuf_res_lookup()` finds a resource by combined resource type and user key.
- `vmw_cmdbuf_res_add()` stages a new resource, inserts it in the hash immediately, refs the resource, and links it to the caller's staging list.
- `vmw_cmdbuf_res_remove()` stages removal or cancels an uncommitted add.
- `vmw_cmdbuf_res_commit()` finalizes staged additions/removals after commands are submitted.
- `vmw_cmdbuf_res_revert()` undoes staged additions/removals after validation/submission failure.

## Control Flow
Execbuf creates a staging list. Adds insert a hash-visible entry in `VMW_CMDBUF_RES_ADD` state. Removes find the hash entry; if the entry was only staged for add it is freed, otherwise it is removed from the committed hash/list and placed on the staging list as `VMW_CMDBUF_RES_DEL`. Commit calls resource `commit_notify()` and either moves adds to the committed list or drops deleted entries. Revert removes staged adds from the manager or restores staged deletes to the committed hash/list.

## State, Persistence, Dependencies, And Integration
State is in-memory and protected by `dev_priv->cmdbuf_mutex` according to the comments. Hash keys combine `user_key | (res_type << 24)`, so key-space assumptions are important. Dependencies include Linux hashtables, RCU hash deletion, vmwgfx resource references, and `enum vmw_cmdbuf_res_state`. The manager is owned by guest-backed/DX contexts and used by execbuf resource commands.

## Risks And Test Signals
Risks include key collisions if user keys exceed the assumed low bits, lookup during staged delete, missing commit/revert on an error path, and resource reference leaks. Test signals include add+commit, add+revert, committed remove+commit, committed remove+revert, remove of staged add, duplicate key rejection at higher layers, and manager destroy with live committed resources.
