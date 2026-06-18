# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/radio.c

## Purpose
Implements b43legacy radio register access, channel programming, radio calibration, NRSSI calibration, adjacent-channel interference mitigation, TX antenna/power setup, and radio on/off sequencing. It is the companion to `phy.c` for RF-side behavior on legacy B/G devices.

## Important APIs, Types, and Functions
Important public functions include `b43legacy_radio_lock()`, `b43legacy_radio_unlock()`, `b43legacy_radio_read16()`, `b43legacy_radio_write16()`, `b43legacy_radio_aci_detect()`, `b43legacy_radio_aci_scan()`, `b43legacy_nrssi_*()`, `b43legacy_calc_nrssi_slope()`, `b43legacy_calc_nrssi_threshold()`, `b43legacy_radio_set_interference_mitigation()`, `b43legacy_radio_calibrationvalue()`, `b43legacy_radio_init2050()`, `b43legacy_radio_selectchannel()`, `b43legacy_radio_set_txantenna()`, `b43legacy_radio_set_txpower_a()`, `b43legacy_radio_set_txpower_bg()`, `b43legacy_default_*()`, `b43legacy_radio_turn_on()`, `b43legacy_radio_turn_off()`, and `b43legacy_radio_clear_tssi()`.

## Control Flow, State, and Persistence
Radio access maps logical offsets differently for 2050/2053 radios and B/G PHYs, then uses MMIO radio-control/data registers. Channel selection optionally runs the synthetic power-up workaround, writes frequency codes, updates Japan channel-14 flags, stores `phy->channel`, and waits for settling. Calibration paths save large PHY/radio/ILT stacks, force known gains, sample measurement registers, derive NRSSI slope/threshold and calibration values, then restore state. Interference mitigation uses explicit enable/disable scripts with stack save/restore and updates `phy->interfmode`, `aci_enable`, `aci_hw_rssi`, and `aci_wlan_automatic`. Radio power-off stores RF override context for later restore unless forced; power-on restores context and retunes the channel. TX power setters update attenuation fields and shared-memory radio attenuation, and may trigger LO adjustment.

## Dependencies and Integration Points
Depends on PHY accessors, ILT helpers, b43legacy MMIO/SHM, SPROM board flags/country code, sleep/delay APIs, and `struct b43legacy_phy` state. It is called from PHY initialization/power control, rfkill polling, sysfs interference control, channel change code, and transmit-power recalculation.

## Risks and Test Signals
High-risk areas are register stack balance, revision-specific radio offset mapping, channel-14 country handling, interference mitigation restore paths, and radio-off context preservation across rfkill/suspend. Test channel changes across 1-14, rfkill toggles, ACI mitigation sysfs modes, TX power changes, RSSI calibration, resume, and no stuck `RADIOLOCK` or corrupted attenuation/LO settings.
