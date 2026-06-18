# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/link.h

Purpose: Defines per-link state for MLD VIFs and declares link lifecycle, notification, channel-load, and link-grade APIs.

Important APIs/types/functions: `struct iwl_probe_resp_data`, `struct iwl_mld_link`, `iwl_mld_cleanup_link()`, `NORMALIZE_PERCENT_TO_255`, and prototypes for link add/remove/activate/deactivate/change, missed beacon handling, association update, link grade, channel load, and beacon filter notification handling.

Control flow: The inline cleanup helper frees RCU probe response data, clears restart-cleaned link fields, and frees internal broadcast, multicast, and monitor STAs if allocated. It is used during firmware restart and VIF cleanup before links are reused or freed.

State/persistence: `struct iwl_mld_link` intentionally separates restart-cleaned fields from state that survives restart. Firmware ID, active flag, EDCA params, channel context, RU block, and key pointers are reset on restart. Internal STAs, RSSI event history, AP early keys, average beacon energy, silent deactivation, and probe response data are outside that group but cleanup still frees relevant dynamic resources.

Dependencies/integration: Includes mac80211, MLD root state, STA state, datapath notification structures, AP key flows, P2P NoA data, and MLO policies.

Risks: Cleanup must be called before freeing or reusing link state, otherwise RCU probe data or internal station IDs can leak. AP early key capacity is fixed at six entries. `NORMALIZE_PERCENT_TO_255` multiplies by 256/100, so callers should expect a 0..256 style scale, not a strict 0..255 maximum.

Test signals: Restart cleanup tests should validate internal STA freeing and RCU pointer clearing. Link-state tests should confirm that fields intended to survive restart are not accidentally zeroed by `CLEANUP_STRUCT`.
