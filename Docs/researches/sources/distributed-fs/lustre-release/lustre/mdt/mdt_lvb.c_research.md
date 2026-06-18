# sources/distributed-fs/lustre-release/lustre/mdt/mdt_lvb.c

## Purpose

`mdt_lvb.c` implements MDT `ldlm_valblock_ops` for LDLM lock value blocks. It provides quota-resource delegation to QMT handlers, Data-on-MDT `struct ost_lvb` allocation/update/fill/free, and layout-lock LVB filling from the file LOV xattr. These callbacks let LDLM carry small pieces of MDT-side state in lock replies and glimpse callbacks.

## Important APIs, Types, and Functions

- `mdt_lvbo` is the exported `struct ldlm_valblock_ops` instance wired into the MDT namespace.
- `mdt_lvbo_init()`, `mdt_lvbo_update()`, `mdt_lvbo_size()`, `mdt_lvbo_fill()`, and `mdt_lvbo_free()` are the LDLM entry points.
- `mdt_dom_lvb_alloc()` allocates `res->lr_lvb_data` as `struct ost_lvb`, sets `res->lr_lvb_len`, and marks `lvb_blocks` with `-ENODATA` until real data is available.
- `mdt_dom_lvb_is_valid()` treats a missing LVB or error-coded `lvb_blocks` as invalid.
- `mdt_dom_disk_lvbo_update()` refreshes DoM LVB fields from MDT object inode attributes.
- `mdt_dom_lvbo_update()` merges an optional RPC-supplied `RMF_DLM_LVB` and a backing inode refresh into the resource LVB.

## Control Flow

Quota resources are detected first in each operation with `IS_LQUOTA_RES(res)` and delegated to `qmt_hdls` when `mdt->mdt_qmt_dev` exists. Non-quota resources use MDT-local handling.

DoM update begins in `mdt_dom_lvbo_update()`. It skips update during OBD failover, allocates the LVB if needed, extracts the FID from the LDLM resource name, optionally swabs and merges an RPC-provided `struct ost_lvb`, then finds the MDT object and calls `mdt_dom_disk_lvbo_update()`. Both RPC and disk merge paths update size, times, and blocks under the resource lock, honoring `increase_only` unless a full refresh is requested.

`mdt_lvbo_size()` chooses the reply LVB length. Quota resources ask QMT, DoM locks return `sizeof(struct ost_lvb)`, layout locks return `mdt->mdt_max_mdsize`, and other locks return zero. DoM is preferred over layout when bits are combined because the file layout is not returned in combined open/getattr LVB replies, while glimpse ASTs use the DoM LVB.

`mdt_lvbo_fill()` handles three cases. Quota fill delegates to QMT. DoM fill ensures the LVB is valid by forcing an update if needed, copies resource LVB bytes under the resource lock, and returns the `ost_lvb` length. Layout fill only runs for granted layout locks: it resolves the FID, finds a local existing object, queries `XATTR_NAME_LOV` length with `mo_xattr_get(..., LU_BUF_NULL, ...)`, updates `mdt_max_mdsize` if the EA has grown beyond the known maximum, returns `-ERANGE` with the required length for undersized buffers, or fills the caller buffer with the LOV EA.

## State and Persistence Behavior

The primary state is `ldlm_resource.lr_lvb_data` and `lr_lvb_len`. For DoM locks this is a heap `struct ost_lvb` whose fields cache size, blocks, and timestamps derived from client RPC LVBs and the backing MDT object. The state is in-memory and associated with the LDLM resource lifetime; `mdt_lvbo_free()` releases it.

The disk-persistent source of truth for DoM values is the MDT object's inode attributes read through `mo_attr_get()`. Layout LVB content is read from the persistent LOV xattr, but this file only copies it into reply buffers; it does not modify it. The file can adjust `mdt->mdt_max_mdsize` at runtime when it discovers a larger layout EA.

## Dependencies and Integration Points

This file depends on LDLM resource/lock APIs, resource-name-to-FID extraction, MDT object lookup/lifetime helpers, `mo_attr_get()`, `mo_xattr_get()`, request capsule swabbing for `RMF_DLM_LVB`, QMT quota handlers, and MDT thread-local buffers. It integrates with open/getattr/glimpse paths that request DoM or layout ibits, and with the MDS PTLRPC service through the current `lu_env`.

## Risks and Edge Cases

- `mdt_dom_lvbo_update()` asserts that `lu_env_find()` succeeds. Calling LDLM update without an MDT-capable environment would trip assertions or return `-ENOMEM` through missing thread info.
- The `increase_only` merge policy can preserve stale larger values after truncation unless a caller explicitly requests a non-increase-only refresh.
- `mdt_lvbo_fill()` converts most negative errors other than `-ERANGE` to zero, which avoids protocol failures but can hide object/xattr lookup problems from callers.
- `mdt_max_mdsize` is updated without explicit serialization in this file when a larger EA is discovered.
- `mdt_dom_lvb_is_valid()` overloads `lvb_blocks` as an error marker. Future code must not treat all bit patterns in `lvb_blocks` as valid block counts before checking `OST_LVB_IS_ERR()`.

## Test Signals

Tests should exercise quota delegation with and without `mdt_qmt_dev`, DoM LVB first allocation and `-ENODATA` marker, RPC-supplied LVB merge with swabbing, disk refresh after truncation with `increase_only` both true and false, layout fill with exact/undersized/oversized buffers, `mdt_max_mdsize` growth, remote or missing object behavior, and `lvbo_free()` cleanup for quota and DoM resources.
