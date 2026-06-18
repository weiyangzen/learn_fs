# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-nvm-parse.h

Purpose: Declares NVM/regulatory parsing data structures, channel flag definitions, and public NVM parser entry points.

Important APIs and types: `enum iwl_nvm_sbands_flags`, `struct iwl_reg_capa`, `enum iwl_nvm_channel_flags`, `struct iwl_nvm_section`, `iwl_parse_nvm_data()`, `iwl_parse_nvm_mcc_info()`, `iwl_read_external_nvm()`, `iwl_nvm_fixups()`, `iwl_get_nvm()`, `iwl_parse_mei_nvm_data()`, and `iwl_reinit_cab()`. KUnit builds also expose `iwl_nvm_get_regdom_bw_flags()`.

Control flow: This header defines the callable contract for code that reads NVM from firmware, files, or MEI and then updates mac80211/cfg80211 capabilities. Callers own returned allocation lifetimes as documented.

State and persistence: Header owns no state. `struct iwl_nvm_section` points to section data cached by callers; `iwl_nvm_data` comes from `iwl-nvm-utils.h` and is heap-owned by callers.

Dependencies and integration points: Includes cfg80211, NVM utility definitions, and MEI NVM structures. Used by MVM startup, regulatory update handling, external NVM flows, and MEI ownership/NVM handoff.

Risks: Channel flag values mirror firmware/NVM ABI and regulatory semantics. Misdocumented ownership of returned regdomains or NVM data can leak memory or double-free. MEI inclusion couples NVM parsing to CSME integration.

Test signals: Compile with and without KUnit/MEI, parser-call ownership tests, regulatory update tests, and external NVM load/unload cleanup validation.
