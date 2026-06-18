# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/stf.c

Purpose: Implements space/time/frequency transmit-chain, antenna, STBC, and spatial-stream policy management for brcmsmac.

Important APIs: `brcms_c_stf_attach/detach()`, `brcms_c_tempsense_upd()`, `brcms_c_stf_ss_algo_channel_get()`, `brcms_c_stf_stbc_rx_set()`, `brcms_c_stf_txchain_set()`, `brcms_c_stf_ss_update()`, `brcms_c_stf_phy_txant_upd()`, `brcms_c_stf_phy_chain_calc()`, `brcms_c_stf_phytxchain_sel()`, and `brcms_c_stf_d11hdrs_phyctl_txant()`. Static helpers update STBC beacon/probe state, TX core maps, spatial policy, and hardware TX antenna fields.

Control flow and state: The module mutates `wlc->stf` and per-band `band_stf_*` fields. Temperature updates shrink/restore TX chain based on PHY-reported active chains. Attach initializes 2G/5G SISO/CDD defaults, STBC off, and auto algorithm state. TX chain changes validate hardware masks, recalculate stream counts, update STBC/SS modes, choose TX antenna defaults, push chain state to PHY, and refresh TX core maps.

Dependencies and integration: Uses mac80211, D11, rate, PHY HAL, channel, main, and debug APIs. It directly updates BMAC antenna state, PHY chain state, beacons, probe responses, and MAC suspend/enable windows. Risks include invalid chain masks, PHY revision-specific antenna encodings, silent no-op `force` parameter, and user/thermal changes racing with live traffic. Test signals include thermal chain throttling, STBC capability changes, beacon/probe refresh, NPHY antenna encoding, 1/2 stream transitions, and TX header antenna fields.
