# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tlc.c

Purpose: Builds and sends firmware TLC/rate-control configuration for MLD link stations, translates mac80211 HT/VHT/HE/EHT/UHR capabilities into firmware rate bitmaps/flags, handles TLC debug host commands, updates TLC configuration after PHY changes, and processes TLC notifications for last TX rate and A-MSDU limits.

Important APIs and functions: `iwl_mld_config_tlc_link()` configures one link STA. `iwl_mld_config_tlc()` configures all active links for a station. `iwl_mld_tlc_update_phy()` refreshes stations on a link after PHY/channel context changes. `iwl_mld_send_tlc_dhc()` sends TLC debug host commands. `iwl_mld_handle_tlc_notif()` processes rate and A-MSDU updates.

Control flow: TLC config computes max channel width, feature flags, valid chains, SGI support, max MPDU/A-MSDU length, PHY ID, non-HT rates, and HT/VHT/HE/EHT/UHR MCS bitmaps. It then adapts the generic v6 command to firmware command versions 6, 5, or 4 and sends it asynchronously. Notifications validate station ID, update `last_rate_n_flags` from firmware rate encoding, then optionally update max RC A-MSDU and per-TID A-MSDU lengths constrained by TX FIFO sizes.

State and persistence: Updates link STA `last_rate_n_flags`, `link_sta->agg.max_rc_amsdu_len`, `max_tid_amsdu_len[]`, and aggregate recalculation. Reads station state to limit AP-mode channel width before authorization and to disable A-MSDU before association. State is runtime-only.

Dependencies and integration points: Depends on mac80211 capabilities, MLD station/link/PHY helpers, firmware RS/TLC/DHC ABIs, valid antenna helpers, firmware shared memory TX FIFO sizes, and mac80211 aggregate recalculation. It is called from station add/update and PHY change paths.

Risks: Capability translation is standards-dense and easy to regress for EHT/UHR, SMPS static NSS limits, 20 MHz-only cases, 160/320 MHz support, and own-vs-peer MCS intersections. Older command-version conversion requires a single STA bit in `sta_mask`. A-MSDU notification sizes below 2000 are forced off, and sizes above mac80211 max are rejected. Async command send means callers cannot assume immediate firmware state.

Test signals: Cover HT/VHT/HE/EHT/UHR rate bitmap construction, LDPC/STBC/DCM/extra-LTF/UHR flags, SMPS static behavior, firmware command versions 4/5/6, AP pre-authorization 20 MHz limiting, PHY update skipping stations not in FW, TLC notification rate conversion, invalid STA ID, and A-MSDU per-TID FIFO limiting.
