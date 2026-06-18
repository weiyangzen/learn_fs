# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/phy.c

## Purpose
Implements b43legacy baseband PHY initialization, calibration, antenna diversity, local-oscillator measurement, and closed-loop transmit-power control for legacy Broadcom B/G PHYs. It programs many revision-specific PHY, radio, shared-memory, and ILT values, with code paths split by PHY type, PHY revision, analog revision, radio version/revision, board flags, and SPROM power calibration fields.

## Important APIs, Types, and Functions
Public entry points include `b43legacy_phy_lock()`, `b43legacy_phy_unlock()`, `b43legacy_phy_read()`, `b43legacy_phy_write()`, `b43legacy_phy_calibrate()`, `b43legacy_phy_init_tssi2dbm_table()`, `b43legacy_phy_init()`, `b43legacy_phy_set_antenna_diversity()`, `b43legacy_phy_lo_b_measure()`, `b43legacy_phy_lo_g_measure()`, `b43legacy_phy_lo_adjust()`, `b43legacy_phy_lo_mark_all_unused()`, `b43legacy_phy_xmitpower()`, `b43legacy_phy_set_baseband_attenuation()`, and `b43legacy_power_saving_ctl_bits()`. Internal helpers cover B-PHY init revisions 2/4/5/6, G-PHY setup and AGC tables, loopback gain calculation, TSSI-to-dBm table generation, LO pair search, and power-control initialization.

## Control Flow, State, and Persistence
Initialization dispatches on `dev->phy.type` and `dev->phy.rev`, then runs large register scripts and radio setup. Calibration for G rev 1 temporarily resets the wireless core. LO measurement saves register stacks, forces known channel/gain states, searches low/high LO pairs, writes selected pairs into `phy->_lo_pairs`, and restores hardware state. Transmit-power recalculation reads recent TSSI samples from shared memory, converts them through `phy->tssi2dbm`, clamps to SPROM/regulatory limits, updates `phy->bbatt`, `phy->rfatt`, and `phy->txctl1`, then applies radio/PHY attenuation under PHY and radio locks. Persistent driver state is in `struct b43legacy_phy`: calibration flags, channel, attenuation, power table pointer, LO pairs, NRSSI values, saved power-control register, antenna diversity, and debug/manual-power flags. Dynamically generated TSSI tables allocate memory and set `dyn_tssi_tbl`.

## Dependencies and Integration Points
Depends on b43legacy MMIO, SHM, ILT, radio, MAC suspend/resume, core reset, SPROM board data, mac80211 mode information, and debug helpers. `radio.c` calls PHY helpers for attenuation and LO adjustment; `xmit.c` uses PHY RSSI state indirectly through RX reporting; rfkill and sysfs paths can trigger radio and interference changes that rely on this file.

## Risks and Test Signals
Risk is high because this is timing-sensitive undocumented hardware programming. Register-save omissions, wrong revision checks, or bad SPROM interpretation can leave radio gain, LO, antenna diversity, or power control miscalibrated. Test signals include successful association on B/G devices, stable RSSI, channel changes, no excessive retries, correct regulatory TX power, suspend/resume with power control intact, sysfs interference changes, and no warnings from LO pair range checks or invalid max-power handling.
