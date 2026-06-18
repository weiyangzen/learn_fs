# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2059.c

`radio_2059.c` supplies initialization and channel-switch tables for 2059 radios used by b43 HT-PHY devices. It maps channel frequencies to radio synthesizer/RXTX fields and PHY bandwidth fields.

Key data includes `r2059_phy_rev1_init`, `RADIOREGS`, `PHYREGS`, and `b43_phy_ht_channeltab_radio2059`. `r2059_upload_inittabs()` supports PHY revision 1, warns and returns for others, and writes each init entry with `R2059_ALL | register` through `b43_radio_write()`. `b43_phy_ht_get_channeltab_e_r2059()` scans the static table for a matching MHz frequency and returns NULL on miss.

Persistent effects are limited to hardware radio register writes during init. Lookup is read-only over immutable table data. The file depends on `b43.h` and `radio_2059.h`; `phy_ht.c` calls the upload and lookup APIs during HT-PHY initialization and channel switching.

Risks include stale table values, especially channels 2467 and 2472, which comments mark as outdated from older driver data. Broadcast writes assume all cores should receive the same init values. Testing should build HT-PHY support, exercise lookup for every listed channel and unsupported frequencies, and compare register traces against known-good hardware captures.
