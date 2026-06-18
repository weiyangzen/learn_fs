# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/caps.c

## Purpose
`caps.c` translates hardware generation and EEPROM header data into ath5k capability flags. It determines supported bands/modes, raw frequency ranges, TX queue count, PHY error counter availability, and multi-rate retry support. It also exposes legacy AR5210 PS-Poll enable/disable helpers.

## Important APIs and functions
- `ath5k_hw_set_capabilities(struct ath5k_hw *ah)`: fills `ah->ah_capabilities`.
- `ath5k_hw_enable_pspoll(struct ath5k_hw *ah, u8 *bssid, u16 assoc_id)`: clears AR5210 PS-Poll disable/default antenna bits.
- `ath5k_hw_disable_pspoll(struct ath5k_hw *ah)`: sets the same AR5210 bits to disable PS-Poll.

## Control flow
`ath5k_hw_set_capabilities` reads `caps->cap_eeprom.ee_header`. AR5210 is hard-coded to middle 5 GHz only and 802.11a mode. Later chips use EEPROM mode bits: 11a enables 5 GHz, optionally lowering the minimum to 4920 MHz when the regulatory helper allows 4.9 GHz; 11b and 11g enable 2 GHz ranges and modes unless `cap_needs_2GHz_ovr` requests SoC-specific override. RF2112 clears 11a because that 2 GHz radio cannot support it. Queue count is two for AR5210 without QCU and ten for later devices. PHY error counters are present from AR5213A. Multi-rate retry is flagged for AR5212.

## State and persistence behavior
The file mutates only in-memory capability fields and, for PS-Poll helpers, the `AR5K_STA_ID1` hardware register. It consumes EEPROM-derived values that were populated earlier by EEPROM initialization, but it does not read or write EEPROM directly.

## Dependencies and integration points
Capabilities feed `base.c` band setup, queue setup, MRR configuration, debugfs ANI reporting, and crypto/mac80211 feature decisions made around attach. The file depends on `ath5k.h`, `reg.h`, debug logging, and shared regulatory helper `ath_is_49ghz_allowed`.

## Risks and edge cases
- EEPROM header interpretation is the source of truth for advertised bands. Bad EEPROM reads can hide supported bands or expose invalid ones.
- `cap_needs_2GHz_ovr` is externally set for SoCs; if not set correctly, 2 GHz mode bits may be wrong.
- Raw range limits are broader than final regulatory permissions; callers must still apply cfg80211/regulatory filtering.
- PS-Poll helpers only support AR5210 and return `-EIO` for later chips, so generic callers must handle non-support.

## Test signals
Probe on representative AR5210, AR5211, AR5212, RF2112, RF2413/RF5413, and AHB SoC devices should show expected band exposure, queue count, MRR max-rates behavior, PHY error counter debugfs reporting, and no illegal 5 GHz mode on RF2112. Regulatory tests should verify that 4.9 GHz exposure depends on regdomain.
