# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_dmac_flt.c

`otx2_dmac_flt.c` manages CGX/RPM destination-MAC hardware filters used as a whitelist-style complement to NPC MCAM ntuple filtering. It adds, removes, updates, and sizes DMAC entries through AF mailbox messages while maintaining the mapping from driver bitmap slots to firmware hardware indexes.

Public functions are `otx2_dmacflt_add`, `otx2_dmacflt_remove`, `otx2_dmacflt_update`, and `otx2_dmacflt_get_max_cnt`. PF interface MACs use `cgx_mac_addr_set` and `cgx_mac_addr_reset`; non-PF MACs use add/delete messages. Updates send `cgx_mac_addr_update` and store the returned index back into `flow_cfg->bmap_to_dmacindex`.

Flow code decides which ethtool rules qualify as DMAC filters. On add, the returned hardware index is stored at `bmap_to_dmacindex[bit_pos]`; remove and update recover that index from the same array. Maximum filter count is discovered during MCAM flow initialization and stored in `flow_cfg->dmacflt_max_flows`.

State is runtime-only: `dmacflt_bmap` tracks logical active slots in `otx2_flows.c`, while `bmap_to_dmacindex` maps those slots to CGX/RPM indexes. Hardware filters are reinstalled after interface reopen. Dependencies are mailbox CGX/RPM MAC messages, `mbox.lock`, Ethernet address helpers, and flow management.

Risks include stale index mapping, calling without valid DMAC support or `flow_cfg`, and the special PF-MAC set/reset semantics differing from ordinary add/delete. Test by adding, updating, deleting PF and non-PF DMAC ethtool rules, filling the table, reopening the interface, and checking firmware index remapping.
