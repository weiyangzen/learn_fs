# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2059.h

`radio_2059.h` defines the HT-PHY 2059 radio core selectors, selected register offsets, channel-entry structure, and exported functions used by b43 HT radio initialization and channel switching.

`R2059_C1`, `R2059_C2`, `R2059_C3`, and `R2059_ALL` select individual or all radio cores. Named offsets cover RCAL/RCCAL, RFPLL control, XTAL config, and calibration status. `struct b43_phy_ht_channeltab_e_radio2059` contains a channel frequency, 21 radio programming fields, and a `struct b43_phy_ht_channeltab_e_phy` block. Exports are `r2059_upload_inittabs()` and `b43_phy_ht_get_channeltab_e_r2059()`.

The header has no control flow or state. It depends on `linux/types.h` and `phy_ht.h`, tying the radio table to HT-PHY channel programming. `radio_2059.c` implements the data and functions; `phy_ht.c` consumes them.

Risks center on structure field order and register selector correctness. Any field insertion or reorder must be synchronized with initializer macros and consumers. Test signals are HT-PHY builds, 2059 init/channel-switch hardware tests, and NULL handling for unsupported frequencies.
