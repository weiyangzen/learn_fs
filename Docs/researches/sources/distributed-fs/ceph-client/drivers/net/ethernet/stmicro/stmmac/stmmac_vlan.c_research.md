# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_vlan.c

Purpose: VLAN filtering, hash/perfect matching, insertion mode, RX tag acceleration, and VLAN ops tables for DWMAC/XGMAC variants.

Important APIs and functions: `vlan_add_hw_rx_fltr()` and `vlan_del_hw_rx_fltr()` update software VLAN filter shadow state and program hardware. `vlan_write_single()` writes single-filter hardware. `vlan_write_filter()` writes extended filter entries and polls the busy bit. `vlan_restore_hw_rx_fltr()` replays shadow state. `vlan_update_hash()` and `dwxgmac2_update_vlan_hash()` program DWMAC/XGMAC hash or perfect VLAN matching. `vlan_enable()` configures TX insertion behavior. `vlan_rx_hw()` transfers descriptor VLAN TCI into skb metadata. `vlan_set_hw_mode()` controls RX stripping/reporting. `stmmac_get_num_vlan()` decodes hardware filter capacity.

Control flow: netdev VLAN add/delete paths call ops selected by MAC family. Adds validate VID, handle single-filter limitations, find an extended slot, program live hardware if running, and update shadow state. Deletes clear matching slots. Restore runs after reset/open. Hash updates switch among hash, perfect, and disabled modes.

State and persistence: `mac_device_info` stores `vlan_filter[]`, `num_vlan`, and `hw_vlan_en`. Hardware registers store active filter table, hash, tag control, insertion mode, and strip mode. Shadow state persists across resets.

Dependencies and integration: STMMAC MAC info, descriptor callbacks, XGMAC packet filter definitions, `readl_poll_timeout()`, skb VLAN acceleration, and `hwif.c` operation-table selection.

Risks and test signals: single-filter hardware cannot add VID 0 and only supports one active VID. Extended writes can time out. The `proto` argument is not used by add/delete, so C/S-VLAN distinction relies on surrounding mode. Validate VLAN add/delete down/up, ethtool VLAN selftests, double VLAN, RX tag delivery, and hardware feature count decoding.
