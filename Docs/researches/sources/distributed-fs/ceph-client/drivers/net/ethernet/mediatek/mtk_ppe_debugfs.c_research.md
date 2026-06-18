<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_ppe_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_ppe_debugfs.c

## Purpose
`mtk_ppe_debugfs.c` provides debugfs visibility into PPE FOE entries. It creates per-PPE debugfs directories with `entries` and `bind` files and formats active FOE table entries, including state, packet type, original/new tuples, L2 header rewrite fields, VLAN tags, IB words, and optional MIB packet/byte counters.

## Important APIs And Functions
`mtk_foe_entry_state_str` and `mtk_foe_pkt_type_str` translate hardware state and packet type enums to compact strings. `mtk_print_addr` and `mtk_print_addr_info` print IPv4/IPv6 endpoint data. `mtk_ppe_debugfs_foe_show` is the main seq-file renderer; `mtk_ppe_debugfs_foe_all_show` and `mtk_ppe_debugfs_foe_bind_show` select all non-invalid entries or only bound entries. `mtk_ppe_debugfs_init` creates `ppe%d/entries` and `ppe%d/bind`.

## Control Flow
When a debugfs file is read, the renderer iterates all `MTK_PPE_ENTRIES`, skips invalid entries, optionally filters to `MTK_FOE_STATE_BIND`, reads accounting via `mtk_foe_entry_get_mib`, decodes packet type using version-aware helpers, selects IPv4 or IPv6 tuple storage, prints original and translated addresses, selects the L2/IB2 storage based on packet type, reconstructs source and destination MAC addresses from split fields, and emits one line per entry.

## State And Persistence
The file does not own flow state. It reads live FOE DMA memory and may read-clear MIB hardware counters through `mtk_foe_entry_get_mib`, which also accumulates software totals. The debugfs directory name is persisted in `ppe->dirname`; the actual entries reflect current hardware/software state and can change while being read.

## Dependencies And Integration Points
It depends on debugfs, seq_file, IPv6 helpers, `mtk_eth_soc.h`, and PPE APIs. It is initialized from `mtk_ppe_init` after the PPE table and accounting structures are allocated. It uses the same version-aware packet type helpers as the core PPE code, avoiding direct NETSYS layout assumptions for `ib1`.

## Risks
Reading `entries` can be expensive because it scans all 16K FOE entries and may touch MIB hardware for each non-invalid entry. Accounting reads may alter counters if MIB read-clear is enabled, so debugfs reads are observability with side effects. The renderer only has packet type strings for routable/tunnel types and prints bridge types as `UNKNOWN`, which can confuse diagnostics for L2 offload. It reads live hardware without taking `ppe_lock`, so entries can change while being formatted.

## Test Signals
With debugfs enabled, verify `ppe0/entries` and `ppe0/bind` exist, invalid entries are skipped, bound flow lines show tuple/MAC/VLAN/IB data, MIB counters grow across traffic, and repeated reads do not crash while flows are added or removed. Test IPv4, IPv6, bridge, VLAN, PPPoE, DSA, and WED-directed entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_ppe_debugfs.c -->
