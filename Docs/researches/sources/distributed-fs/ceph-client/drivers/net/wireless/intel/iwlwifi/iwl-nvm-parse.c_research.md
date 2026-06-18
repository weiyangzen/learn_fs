# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-nvm-parse.c

Purpose: Converts NVM, firmware NVM responses, MEI-provided NVM, and MCC regulatory data into `iwl_nvm_data`, cfg80211 channel/band/capability structures, MAC address data, and regulatory domains.

Important APIs and functions: Exports `iwl_parse_nvm_data()`, `iwl_parse_mei_nvm_data()`, `iwl_reinit_cab()`, `iwl_parse_nvm_mcc_info()`, `iwl_nvm_fixups()`, `iwl_read_external_nvm()`, `iwl_get_nvm()`, and KUnit-visible `iwl_nvm_get_regdom_bw_flags()`. Static helpers map channel indexes, derive NVM flags, initialize HT/VHT/HE/EHT/6GHz capability structures, parse SKU/radio/MAC fields, handle LAR, and apply regulatory capability API v1/v2/v4 differences.

Control flow: Parse entry points allocate flexible `iwl_nvm_data` with enough channel slots for legacy, extended, or UHB channel tables; derive SKU/radio/antenna/MAC state; set LAR and workaround flags; build channel maps; initialize 2.4/5/6 GHz supported-band structures; and return data for mac80211 registration. MCC parsing groups contiguous valid channels with identical regulatory flags into cfg80211 rules, adds WMM data for ETSI 5GHz, and creates a dummy unusable rule if firmware reports no valid channels. External NVM reading requests firmware, skips optional headers, validates sections, applies fixups, and replaces section buffers.

State and persistence: Produces heap-owned `iwl_nvm_data` and external NVM section buffers. It reads immutable firmware capabilities, module parameters, hardware registers for MAC addresses, and CSME/MEI NVM snapshots. No on-disk persistence is written.

Dependencies and integration points: Integrates with cfg80211/mac80211 channel and capability APIs, firmware command `NVM_GET_INFO`, FW TLV capabilities/APIs, MEI NVM structures, CSR/PRPH MAC registers, ACPI/debug headers, request_firmware, and module parameters including FIPS-sensitive behavior.

Risks: Regulatory handling is safety-critical. Firmware response versions change channel-profile width and capability flag meanings. 6GHz/EHT advertisement depends on FIPS, WPA3/MFP assumptions, bandwidth limits, PCIe link speed, reduced-capability SKUs, and antenna masks. External NVM parsing must reject malformed sizes/IDs. MAC byte order differs by source.

Test signals: KUnit for `iwl_nvm_get_regdom_bw_flags()`, NVM parse fixtures for legacy/ext/UHB, MCC API v1/v2/v4 regulatory domains, RF-kill empty-channel response, external NVM header/section validation, MEI NVM parse, MAC override fallback, FIPS capability suppression, and disable_11n/11ac/11ax/11be matrices.
