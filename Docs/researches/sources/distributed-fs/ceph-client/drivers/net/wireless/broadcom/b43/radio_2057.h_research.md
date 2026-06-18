# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2057.h

`radio_2057.h` is the public register map and data-structure interface for b43 N-PHY 2057 radio support. It names common, per-core, TX, AFE, calibration, and revision-7-specific radio register offsets.

The constants cover PLL/VCO calibration, LOGEN, TX gain and mixer tuning, IPA/PAD/PGA blocks, LNA/RXMIX/TIA/RXBB/RSSI paths, RCCAL/RCAL status, override registers, and per-core TX IQ/TSSI controls. `R2057_VCM_MASK` defines a calibration field mask. `struct b43_nphy_chantabent_rev7` stores full 2.4/5 GHz channel programming values plus `struct b43_phy_n_sfo_cfg`; `struct b43_nphy_chantabent_rev7_2g` is the smaller 2 GHz variant. The header declares `r2057_upload_inittabs()` and `r2057_get_chantabent_rev7()`.

There is no executable logic or state in the header. It is a compile-time contract used by `radio_2057.c` and N-PHY code that programs radio/PHY values. It depends on `linux/types.h` and `tables_nphy.h`.

Risks are mostly hardware-contract risks: wrong offsets or field order corrupt RF programming. The two channel-entry structures are similar but not interchangeable. Test signals include N-PHY builds, register trace review, and channel switching across both 2.4 and 5 GHz on supported 2057 revisions.
