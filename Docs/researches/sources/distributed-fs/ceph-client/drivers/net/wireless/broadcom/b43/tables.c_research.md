# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/tables.c

`tables.c` contains shared b43 PHY calibration/filter lookup tables and helper functions for reading and writing OFDM and G-PHY hardware tables.

Exported arrays include rotor, retard, fine-frequency A/G, noise, noise-scale, sigma-square, and RSSI AGC tables. `assert_sizes()` uses `BUILD_BUG_ON()` against size macros from `tables.h`; it is referenced after a return in `b43_ofdmtab_read16()` to force compile-time checking. `b43_ofdmtab_read16/write16/read32/write32()` access OFDM tables through `B43_PHY_OTABLECTL`, `B43_PHY_OTABLEI`, and `B43_PHY_OTABLEQ`. `b43_gtab_read()` and `b43_gtab_write()` access G tables through `B43_PHY_GTABCTL` and `B43_PHY_GTABDATA`.

The OFDM helpers cache the last table address and direction in `dev->phy.g->ofdmtab_addr` and `ofdmtab_addr_direction`, avoiding redundant address writes for sequential same-direction accesses. Writes persist into PHY hardware table memory; reads return current hardware contents. The file depends on `b43.h`, `tables.h`, and `phy_g.h`; `wa.c` consumes the arrays and size macros for PHY workarounds.

Risks include size macro drift, unreachable-code compile assertions being overlooked by tooling, and stale cached table address state if other code writes the hardware control register directly. Tests should build G-PHY paths, exercise sequential/nonsequential 16/32-bit table access, and verify array sizes remain synchronized.
