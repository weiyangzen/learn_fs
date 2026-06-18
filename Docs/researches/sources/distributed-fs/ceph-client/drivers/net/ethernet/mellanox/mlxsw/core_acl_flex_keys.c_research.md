# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_acl_flex_keys.c

## Purpose
`core_acl_flex_keys.c` implements ACL flexible-key selection and encoding. It maps requested match elements into a minimal ordered set of hardware key blocks, caches those key layouts, accepts key/mask values in an internal storage format, and encodes or clears the final hardware key and mask through device-specific block callbacks.

## Important APIs, Types, And Functions
- `mlxsw_afk_element_infos[]` defines internal scratchpad geometry for every `enum mlxsw_afk_element`: source system port, Ethernet addresses, ethertype, protocol, VLAN/PCP/TCP flags, L4 ports, TTL/ECN/DSCP, virtual router fields, IP address chunks, FDB miss, L4 range, and split virtual-router fields.
- `struct mlxsw_afk` owns cached key infos, maximum block count, ops, and available hardware blocks.
- `mlxsw_afk_create()` initializes the AFK context and validates that every hardware block instance has the same type and compatible size as its internal element definition.
- `struct mlxsw_afk_key_info` is a cached chosen layout: refcount, number of blocks, `element_to_block[]`, requested element usage, and an array of selected block definitions.
- The greedy picker functions count how many requested elements each block can cover, repeatedly choose the block with most remaining hits, then fill `key_info` with high-entropy blocks first followed by the rest.
- `mlxsw_afk_key_info_get()` caches/refcounts layouts by exact element-usage bitmap; `mlxsw_afk_key_info_put()` releases them.
- `mlxsw_afk_values_add_u32()` and `mlxsw_afk_values_add_buf()` populate internal key/mask scratch storage and mark elements used only when the mask is nonzero.
- `mlxsw_afk_encode()` emits block-by-block key and mask data by locating each element's selected block instance, copying from scratch storage, applying optional `u32_key_diff`, and calling `ops->encode_block()` for each block.
- `mlxsw_afk_clear()` calls `ops->clear_block()` over a requested block index range.

## Control Flow
A device driver creates an AFK context with its block table and encode/clear callbacks. Higher layers fill a `mlxsw_afk_element_usage` bitmap for a rule template and call `mlxsw_afk_key_info_get()`. If the same bitmap has been used, the cached layout is refcounted. Otherwise the picker allocates a new layout, computes block coverage, selects blocks until all requested elements are covered, enforces `max_blocks`, and links the layout into the cache.

For each rule instance, callers fill `mlxsw_afk_element_values`. Zero masks are ignored so irrelevant fields are not encoded. Encoding iterates selected blocks and currently used values, skips elements not assigned to the current block, writes a temporary 16-byte block key/mask, and delegates final placement into the output key/mask buffers to the device-specific `encode_block()` callback.

## State And Persistence Behavior
State is in-memory only. AFK caches key layouts in a list with refcounts; `mlxsw_afk_destroy()` warns if cached layouts remain. Element values are caller-owned transient storage. Encoded hardware keys are written into caller-provided buffers and are not persisted by this module.

## Dependencies And Integration Points
The implementation depends on Linux bitmaps, refcounts, and allocation helpers, plus local `item.h` field accessors. The hardware-specific integration is through `struct mlxsw_afk_ops`: the block catalog comes from the device family, and output encoding/clearing is delegated so this core code remains independent of the final register/key format.

## Risks And Edge Cases
- The greedy picker optimizes by current hit count, not by exhaustive search. It can fail with `-EINVAL` if coverage requires more than `max_blocks`.
- If a requested element appears in no block, `mlxsw_afk_picker_most_hits_get()` eventually returns a negative value. Callers must handle `ERR_PTR()`.
- Block validation uses `WARN_ON()` but does not reject creation, so a bad block table can still lead to bad encoding.
- `mlxsw_afk_encode()` assumes all elements in `values->elusage` are a subset of `key_info->elusage`; otherwise warning paths skip or return null element instances.
- Temporary block buffers are fixed at 16 bytes. Block definitions and encode callbacks must match that maximum.

## Test Signals
Useful tests build AFK contexts with overlapping block coverage and verify chosen block count/order, high-entropy block prioritization, cache refcount reuse, failure when elements are uncovered or `max_blocks` is too low, zero-mask omission, U32 diff application, buffer element copying, and clear callback ranges.
