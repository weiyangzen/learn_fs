# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_vlan.h

Purpose: STMMAC VLAN register definitions and exported VLAN operation declarations.

Important APIs and definitions: defines `VLAN_TAG`, `VLAN_TAG_DATA`, `VLAN_HASH_TABLE`, `VLAN_INCL`, and `HW_FEATURE3`; masks and bits for double VLAN, hash mode, inverse matching, S-VLAN selection, exact tag matching, filter data validity, tag insertion control, strip modes, descriptor reporting, and hardware filter count. Declares `dwmac_vlan_ops`, `dwxgmac210_vlan_ops`, `dwxlgmac2_vlan_ops`, and `stmmac_get_num_vlan()`.

Control flow: core initialization and VLAN implementation include this header to choose ops, program registers, and decode hardware capacity.

State and persistence: no state. It defines hardware ABI used to maintain persistent VLAN state in `mac_device_info`.

Dependencies and integration: includes bitfield helpers and XGMAC definitions from `dwxgmac2.h`. Consumed by `stmmac_vlan.c` and MAC initialization.

Risks and test signals: bit definitions must match MAC revisions. Unknown filter-count encodings fall back to one filter. Test through compile coverage and runtime VLAN filtering/stripping/insertion.
