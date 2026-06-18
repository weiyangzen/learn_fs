# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mcc.c

Purpose: Handles MCC/regulatory communication with firmware and converts firmware channel profiles into cfg80211 regulatory domains.

Important APIs/types/functions: `iwl_mld_get_regdomain()`, `iwl_mld_init_mcc()`, `iwl_mld_update_changed_regdomain()`, `iwl_mld_handle_update_mcc()`, and internal helpers `iwl_mld_update_mcc()`, `iwl_mld_copy_mcc_resp()`, `iwl_mld_get_current_regdomain()`, and `iwl_mld_apply_last_mcc()`.

Control flow: `iwl_mld_update_mcc()` sends `MCC_UPDATE_CMD` with alpha2/source and expects a response SKB. `iwl_mld_copy_mcc_resp()` validates payload length based on channel count before copying. `iwl_mld_get_regdomain()` parses the response through NVM regulatory helpers, records MCC source, and updates puncturing allowance for applicable RF types. Init first replays an existing wiphy regdomain if present; otherwise it gets current firmware regdomain and optionally overrides with BIOS MCC. CHUB update notifications are ignored for WiFi source while associated, otherwise they fetch a new regdomain and install it if changed.

State/persistence: Updates `mld->mcc_src`, wiphy regulatory domain, and `IEEE80211_HW_DISALLOW_PUNCTURING` flag based on BIOS/firmware policy. Temporary firmware MCC responses and parsed regdomains are allocated and freed by caller flow.

Dependencies/integration: Depends on firmware MCC commands/notifications, host command response SKBs, `iwl_parse_nvm_mcc_info()`, cfg80211 regulatory APIs, BIOS MCC data, UEFI puncturing policy, and active interface iteration.

Risks: MCC response length validation is critical because channel array length is firmware-controlled. `regulatory_set_wiphy_regd_sync()` can fail init. Ignoring WiFi MCC updates while associated avoids regulatory churn but can defer changes. Puncturing policy is conditional on RF type and BIOS permissions.

Test signals: Tests should cover malformed response lengths, zero MCC warnings, changed status handling, replay of previous regdomain source, BIOS MCC override, associated WiFi-source notification ignore, regulatory set failures, and puncturing flag toggling.
