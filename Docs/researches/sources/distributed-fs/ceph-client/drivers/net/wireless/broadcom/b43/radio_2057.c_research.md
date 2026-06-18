# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2057.c

`radio_2057.c` provides static initialization tables and channel lookup tables for Broadcom 2057 radios used by N-PHY devices. It translates PHY revision/radio revision combinations into radio register writes and channel-specific PLL, LO, TX, RX, and PHY bandwidth programming values.

Important pieces are the private `r2057_rev*_init` `{ register, value }` arrays, initializer macros `RADIOREGS7`, `RADIOREGS7_2G`, and `PHYREGS`, channel tables for rev8/radio5, rev16/radio9, and rev17/radio14, plus exported `r2057_upload_inittabs()` and `r2057_get_chantabent_rev7()`. Upload selects a table by `dev->phy.rev` and `dev->phy.radio_rev`, warns on unsupported combinations, and writes each pair through `b43_radio_write()`. Lookup clears both output pointers, selects the applicable table, scans by MHz frequency, and returns either a full rev7 entry or a compact 2 GHz entry.

The only persistent behavior is hardware radio programming during upload; channel lookup is read-only. The file depends on `b43.h`, `radio_2057.h`, and `phy_common.h`, and is integrated from N-PHY setup/channel-switching in `phy_n.c`.

Risks include sparse table coverage, revision matching mistakes, and table provenance from MMIO dumps. Rev8 init data is present but disabled in a TODO block. Test signals are clean `CONFIG_B43_NPHY` builds, channel lookup coverage for supported revisions, and hardware register trace comparison during channel changes.
