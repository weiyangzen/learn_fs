# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-nvm-utils.h

Purpose: Defines `struct iwl_nvm_data`, the parsed NVM capability container shared with mac80211 setup, and declares NVM utility helpers.

Important APIs and types: `struct iwl_nvm_data` contains MAC address count/address, calibration fields, SKU capability booleans, radio configuration, valid antenna masks, NVM version, max TX power, LAR/VHT160 flags, per-band `ieee80211_supported_band` structures, HE/EHT iftype data storage, and flexible `channels[]`. Declares `iwl_init_sband_channels()` and `iwl_init_ht_hw_capab()`.

Control flow: No executable flow beyond API declarations. Parser code allocates this structure with enough flexible channel entries and then fills it before mac80211 registration.

State and persistence: Instances are heap-owned runtime state and represent the driver’s parsed view of NVM/firmware capabilities. The embedded channel array and band pointers must remain valid for the lifetime of wireless hardware registration.

Dependencies and integration points: Includes Ethernet address, cfg80211, and transport definitions. Used by NVM parser, MVM configuration, mac80211 capability publication, and MEI NVM parsing.

Risks: Flexible-array sizing must match the selected channel table. Band channel pointers point inside `channels[]`, so moving/freeing data invalidates cfg80211 structures. Adding fields can affect allocation/copy assumptions.

Test signals: Allocation-size checks for legacy/ext/UHB channel counts, mac80211 registration using embedded bands, and lifetime cleanup tests for `iwl_nvm_data`.
