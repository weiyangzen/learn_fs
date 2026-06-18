# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_phy_ht.h

Purpose: Declares the HT-PHY table access contract for the b43 driver and exposes the late HT gain table used outside the table initializer.

Important APIs and types: Defines `B43_HTTAB_TYPEMASK`, width tags `B43_HTTAB_8BIT`, `B43_HTTAB_16BIT`, `B43_HTTAB_32BIT`, and address constructors `B43_HTTAB8/16/32`. Declares `b43_httab_read`, `b43_httab_read_bulk`, `b43_httab_write`, `b43_httab_write_few`, `b43_httab_write_bulk`, and `b43_phy_ht_tables_init`. Defines `B43_HTTAB_1A_C0_LATE_SIZE` and declares `b43_httab_0x1a_0xc0_late`.

Control flow encoded by the header: The caller chooses data width through the address macro, then the implementation routes the operation to 8-, 16-, or 32-bit register access. The varargs write helper supports small sequential writes without defining temporary arrays in callers.

State and persistence: The header stores no state. All declared writes affect HT-PHY table memory on the device. The exported late table is immutable static data defined in `tables_phy_ht.c`.

Dependencies and integration points: Relies on `struct b43_wldev` being visible to including C files through other b43 headers. Used by `tables_phy_ht.c` and HT runtime code in `phy_ht.c`.

Risks: The macros do not validate table ids or offsets; misuse can route valid-width writes to wrong hardware locations. The varargs API has no type safety beyond runtime `B43_WARN_ON` range checks for 8/16-bit values. The late table size constant must stay synchronized with the implementation.

Test signals: Compile tests validate prototypes and the exported array size assertion in `tables_phy_ht.c`. Runtime tests should cover all width constructors and small varargs writes from `phy_ht.c`.
