# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables_nphy.h

Purpose: Declares the public N-PHY table interface and the data structures used by N-PHY calibration, RF override, TX IQ/LO calibration, gain-control workaround, and table access code.

Important APIs and types: Defines `struct b43_phy_n_sfo_cfg`, `struct nphy_txiqcal_ladder`, `struct nphy_rf_control_override_rev2`, `struct nphy_rf_control_override_rev3`, `struct nphy_rf_control_override_rev7`, and `struct nphy_gain_ctl_workaround_entry`. Defines `B43_NTAB_TYPEMASK`, the width tags `B43_NTAB_8BIT`, `B43_NTAB_16BIT`, `B43_NTAB_32BIT`, and the address constructors `B43_NTAB8/16/32`. Declares `b43_ntab_read`, `b43_ntab_read_bulk`, `b43_ntab_write`, `b43_ntab_write_bulk`, `b43_nphy_tables_init`, TX gain and RF power table lookup helpers, gain workaround lookup, and rev7 RF control override lookup.

Control flow encoded by the header: Callers construct a typed table offset with `B43_NTAB8/16/32`; the implementation decodes the high bits and routes to the correct register-width access sequence. Macro constants map logical N-PHY table names to table ids and offsets for legacy static tables, legacy volatile tables, rev3+ tables, rev7+ variants, and TX IQ/LO calibration table sizes. This header does not execute logic but establishes the table addressing contract used across `tables_nphy.c` and `phy_n.c`.

State and persistence: No state is stored in the header. The declared helpers mutate device table SRAM and return pointers to static calibration tables in `tables_nphy.c`. The comment on `b43_nphy_get_gain_ctl_workaround_ent` promises a non-NULL return, but the returned object is mutable static storage, so callers should treat it as shared driver data.

Dependencies and integration points: Includes `<linux/types.h>` and forward-declares `struct b43_wldev`. It is consumed by `tables_nphy.c` and N-PHY runtime code in `phy_n.c`. The address and size constants must remain synchronized with the static arrays in the implementation.

Risks: The width tag lives in the upper nibble of a `u32` offset while table and element offsets share the lower bits. Passing a raw address without a width tag triggers warning paths and usually returns zero or writes nothing useful. Changing any `*_SIZE` constant without matching the implementation arrays breaks compile-time assertions. The non-NULL comment for the workaround helper is stronger than the implementation's general style and could conceal the fact that returned entries are shared and modified in place.

Test signals: Compile tests validate declarations and many table-size invariants indirectly. Static analysis should check every `B43_NTAB*` use for correct width. Runtime tests should exercise reads/writes for all three widths and ensure callers handle NULL from gain/RF table lookup helpers declared here.
