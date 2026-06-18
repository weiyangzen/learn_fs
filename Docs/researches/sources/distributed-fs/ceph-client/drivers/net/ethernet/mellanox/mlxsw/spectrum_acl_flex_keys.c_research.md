<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_flex_keys.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_flex_keys.c

## Purpose

`spectrum_acl_flex_keys.c` defines Spectrum flexible-key layouts for ACL matching. It maps logical AFK elements such as MACs, VLAN, system port, IPv4/IPv6 addresses, protocol, L4 ports, TCP flags, VRID, TTL, DSCP, ECN, and FDB miss into hardware key blocks for Spectrum-1, Spectrum-2/3, and Spectrum-4.

## Important APIs, Types, And Functions

- Static `mlxsw_afk_element_inst` arrays define element placement inside hardware blocks.
- `mlxsw_sp1_afk_blocks`, `mlxsw_sp2_afk_blocks`, and `mlxsw_sp4_afk_blocks` enumerate block IDs and supported elements.
- Spectrum-1 uses 16-byte blocks copied directly by `mlxsw_sp1_afk_encode_block()` and cleared by `mlxsw_sp1_afk_clear_block()`.
- Spectrum-2/4 use 36-bit block packing with `mlxsw_sp2_afk_blocks_layout`, `__mlxsw_sp2_afk_block_value_set()`, `mlxsw_sp2_afk_encode_block()`, and `clear_block()`.
- `mlxsw_sp1_afk_ops`, `mlxsw_sp2_afk_ops`, and `mlxsw_sp4_afk_ops` export the layouts and encoding callbacks.

## Control Flow

There is no dynamic policy control flow. AFK users request element usages; the generic AFK core chooses key blocks from these tables and calls the chip-specific `encode_block`/`clear_block` callbacks to build register payloads. Spectrum-4 reuses the Spectrum-2 packing callback but supplies revised block IDs and element widths, including high-entropy markings for selected blocks.

## State And Persistence

The file stores static layout tables only. Runtime state is produced by AFK key-info objects and encoded key/mask buffers in ACL rule insertion. Hardware persistence occurs when those buffers are written by TCAM backends.

## Dependencies And Integration Points

The layouts feed all ACL match encoding in `spectrum_acl.c`, `spectrum_acl_tcam.c`, A-TCAM/C-TCAM insertion, and multicast routing. The file depends on `core_acl_flex_keys.h`, `item.h` bitfield helpers, and exact Spectrum hardware key block definitions.

## Risks

- Any offset, width, block ID, or packing shift error changes hardware match semantics.
- Spectrum-2/4 36-bit packing is non-byte-aligned and must stay compatible with Bloom filter key offsets and ERP mask length assumptions.
- Spectrum-4 changes some VRID/source-port widths and block IDs; using the wrong ops for a device family causes subtle match failures.
- Static tables do not self-validate against hardware capabilities.

## Test Signals

Validate TC flower matches for every listed element, IPv4/IPv6 multicast route keys, VLAN/PCP/system-port/FDB miss matching, Spectrum-1 versus Spectrum-2/4 behavior, masks with partial fields, and encoded key buffers against known hardware layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_acl_flex_keys.c -->
