# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/stf.h

Purpose: Declares brcmsmac STF management functions for attach/detach, thermal chain updates, spatial-stream mode selection, antenna updates, TX chain configuration, STBC RX configuration, chain calculation, and TX header antenna selection.

Important APIs: The functions declared here are implemented in `stf.c` and operate on `struct brcms_c_info *` plus band, chanspec, or ratespec parameters. They expose both lifecycle (`attach`, `detach`) and runtime policy changes (`tempsense_upd`, `txchain_set`, `stbc_rx_set`, `ss_update`).

Control flow and state: No executable code in the header. The API implies mutation of `wlc->stf`, PHY chain masks, BMAC TX antenna state, and beacon/probe-response advertised HT/STBC state.

Dependencies and integration: Includes `types.h` for forward declarations. Consumers include main driver setup, PHY/channel handling, TX header construction, and thermal polling. Risks are contract-level: callers must pass valid `wlc` and ratespec values, and must respect that several functions touch live hardware state. Test signals include compile coverage of all declarations, attach path initialization, TX chain sysfs/ioctl-style changes, and TX header antenna selection under SISO/CDD/STBC modes.
