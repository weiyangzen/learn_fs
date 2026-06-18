# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_phy_lcn.h

Purpose: Declares the LCN-PHY table access API and typed table-address macros for b43 LCN PHY code.

Important APIs and types: Defines `B43_LCNTAB_TYPEMASK`, width tags `B43_LCNTAB_8BIT`, `B43_LCNTAB_16BIT`, `B43_LCNTAB_32BIT`, and address constructors `B43_LCNTAB8/16/32`. Defines `B43_LCNTAB_TX_GAIN_SIZE` as 128. Declares `b43_lcntab_read`, `b43_lcntab_read_bulk`, `b43_lcntab_write`, `b43_lcntab_write_bulk`, and `b43_phy_lcn_tables_init`.

Control flow encoded by the header: LCN callers construct typed offsets with the macros, then the C implementation decodes the high bits and performs matching register-width IO. The TX gain size constant constrains the private gain table and the initializer loop.

State and persistence: The header has no stored state. Declared operations mutate device LCN-PHY table memory; initialization effects last until PHY reset or reinitialization.

Dependencies and integration points: Relies on b43 include ordering for `u32`, `size_t`, and `struct b43_wldev`. Used by `tables_phy_lcn.c` and LCN code in `phy_lcn.c`.

Risks: Raw offsets without width tags hit warning paths in the implementation. The macros do not range-check table ids or offsets. `B43_LCNTAB_TX_GAIN_SIZE` must remain synchronized with the private 128-entry LCN gain table.

Test signals: Compile tests catch prototype drift. Runtime table IO tests should verify all three width tags and confirm the initializer writes exactly 128 TX gain entries.
