# sources/distributed-fs/ceph-client/drivers/net/ethernet/airoha/airoha_ppe_debugfs.c

## Purpose
`airoha_ppe_debugfs.c` exposes read-only debugfs views of Airoha PPE forwarding entries. It formats all non-empty entries and a bind-only subset for manual inspection of hardware offload state.

## Important APIs and functions
- `airoha_ppe_debugfs_init()` creates `/sys/kernel/debug/ppe/entries` and `/sys/kernel/debug/ppe/bind` and stores the directory dentry in `ppe->debugfs_dir`.
- `airoha_ppe_debugfs_foe_show()` iterates `airoha_ppe_get_total_num_entries()`, fetches each entry with `airoha_ppe_foe_get_entry()`, decodes state/type, prints original and translated tuples, L2 metadata, VLANs, IB words, and packet/byte stats.
- `airoha_debugfs_ppe_print_tuple()` prints IPv4/IPv6 address and optional port pairs, converting the stored CPU-order IPv6 words back to network-order display form.
- `DEFINE_SHOW_ATTRIBUTE` creates file operations for both all-entry and bind-only views.

## Control flow
Opening either debugfs file invokes the seq-file show callback. The show code skips missing entries, invalid state, and non-bind state when requested. It selects tuple/L2 fields based on FOE packet type and calls `airoha_ppe_foe_entry_get_stats()` to include counter values.

## State and persistence behavior
The file owns only the debugfs dentry pointer stored in `struct airoha_ppe`; the displayed state comes from live PPE FOE memory/hardware and NPU stats. Removing the PPE calls `debugfs_remove()` in `airoha_ppe_deinit()`.

## Dependencies and integration points
It depends on debugfs/seq-file helpers and the PPE API declared in `airoha_eth.h`. It is conditionally compiled by `CONFIG_DEBUG_FS`; otherwise the header provides a no-op initializer.

## Risks and edge cases
The dump iterates the full PPE entry count, which can be large, and each SRAM entry read may involve MMIO polling. Output is diagnostic only and has no locking beyond what `airoha_ppe_foe_get_entry()` provides. Formatting assumes FOE type-specific layouts are valid for nonzero state; corrupted hardware entries may produce confusing tuple or MAC output.

## Test signals
With debugfs enabled, verify `entries` shows non-invalid offloads, `bind` filters to bound entries, IPv4/IPv6 and VLAN fields decode as expected, stats match flow offload counters, and removing the driver removes the debugfs directory without stale dentries.
