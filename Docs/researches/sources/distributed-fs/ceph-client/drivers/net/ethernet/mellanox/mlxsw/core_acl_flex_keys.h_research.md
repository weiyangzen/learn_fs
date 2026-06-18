# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/core_acl_flex_keys.h

## Purpose
`core_acl_flex_keys.h` defines the abstract match-element vocabulary and public AFK API used to build hardware ACL key blocks. It describes what fields can be matched, how device-specific blocks declare element placement, how callers represent requested element usage and values, and how selected key layouts are encoded.

## Important APIs, Types, And Functions
- `enum mlxsw_afk_element` lists supported match elements: system port, MAC fields, ethertype, protocol, IPv4/IPv6 address chunks, L4 ports, VLAN ID/PCP, TCP flags, IP TTL/ECN/DSCP, virtual-router variants, FDB miss, and L4 port range.
- `enum mlxsw_afk_element_type` distinguishes U32 bitfield elements from byte-buffer elements.
- `struct mlxsw_afk_element_info` and `MLXSW_AFK_ELEMENT_INFO_*` macros describe internal scratchpad layout.
- `struct mlxsw_afk_element_inst` and `MLXSW_AFK_ELEMENT_INST_*` macros describe where an element appears in a concrete hardware block, including optional key-value adjustment and size-check override.
- `struct mlxsw_afk_block` describes one available hardware key block: encoding ID, element instances, instance count, and high-entropy priority.
- `struct mlxsw_afk_element_usage` wraps a bitmap with helpers to add, zero, fill, iterate, and test subset relationships.
- `struct mlxsw_afk_ops` supplies the block catalog plus `encode_block()` and `clear_block()` callbacks.
- Public APIs create/destroy AFK contexts, get/put selected key layouts, query selected block encodings/count, add U32 or buffer values, encode key/mask output, and clear block ranges.

## Control Flow
Callers first describe all fields needed by a rule template in `mlxsw_afk_element_usage`. `mlxsw_afk_key_info_get()` returns a selected layout. Rule instances then place actual key/mask values into `mlxsw_afk_element_values` and call `mlxsw_afk_encode()` with the layout to produce hardware key and mask buffers.

## State And Persistence Behavior
The header exposes two main state lifetimes: `struct mlxsw_afk` is a long-lived context with a block catalog and cached layouts, while `struct mlxsw_afk_element_values` is per-rule transient storage. `mlxsw_afk_key_info` is opaque and refcounted through get/put.

## Dependencies And Integration Points
The header depends on Linux bitmap/types and local `item.h`. It is consumed by Spectrum ACL code that knows the device-specific block encodings and by flow parsing code that translates tc flower or other rules into AFK element usage/value sets.

## Risks And Edge Cases
- `MLXSW_AFK_ELEMENT_STORAGE_SIZE` must grow when adding elements beyond the current scratchpad range; otherwise value writes can overflow intended storage.
- Element instance definitions must match the element's type and size unless `avoid_size_check` is deliberately used.
- Subset checks are directional. Passing arguments in the wrong order can accept incompatible key layouts.
- `VIRT_ROUTER` and split virtual-router elements coexist; users must select the form expected by their hardware blocks.

## Test Signals
Compile tests should cover every macro form. Functional tests should validate element-usage helpers, layout get/put, block encoding IDs, value addition for U32 and buffer elements, subset checks, storage-size assumptions when new elements are added, and device-specific encode/clear callbacks.
