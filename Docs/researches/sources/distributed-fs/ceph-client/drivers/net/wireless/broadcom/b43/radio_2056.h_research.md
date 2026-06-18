# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/radio_2056.h

`radio_2056.h` is the N-PHY 2056 radio register map and channel-switch contract for the b43 Broadcom wireless driver. It defines SYN/TX/RX bank selectors, symbolic offsets for synthesizer, transmit, receive, RSSI, PLL, LO generator, filter, amplifier, and calibration registers, and the `b43_nphy_channeltab_entry_rev3` layout consumed by N-PHY channel setup code.

Important API surface includes `B2056_SYN`, `B2056_TX0`, `B2056_TX1`, `B2056_RX0`, `B2056_RX1`, `B2056_ALLTX`, `B2056_ALLRX`, power/select bit masks such as `B2056_LNA1_A_PU` and `B2056_RSSI_W1_SEL`, `struct b43_nphy_channeltab_entry_rev3`, and declarations for `b2056_upload_inittabs()`, `b2056_upload_syn_pll_cp2()`, and `b43_nphy_get_chantabent_rev3()`.

There is no runtime control flow or persisted software state in this header. Constants are compiled into callers that write hardware radio registers; channel entries are immutable contracts and state persists only in device registers after upload. It depends on Linux integer types and `tables_nphy.h` for `struct b43_phy_n_sfo_cfg`.

Risks: the file contains a duplicated block of 2056 register definitions. Values are currently identical, but future edits could diverge. Testing should include N-PHY builds, register-offset review against vendor data, and hardware channel switching on 2056 devices.
