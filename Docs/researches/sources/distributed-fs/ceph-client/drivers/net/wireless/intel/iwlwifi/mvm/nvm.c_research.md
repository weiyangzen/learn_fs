<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/nvm.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/nvm.c

## Purpose
Loads, writes, parses, and regulatory-updates Intel wireless NVM data for MVM devices. It reads hardware NVM/OTP sections through firmware commands, optionally overlays an external NVM file, parses antenna/MAC/regulatory information, uploads NVM sections back to the NIC, and drives LAR MCC regulatory updates.

## Important APIs, Types, And Functions
Public entry points are `iwl_nvm_init`, `iwl_mvm_load_nvm_to_nic`, `iwl_mvm_update_mcc`, `iwl_mvm_init_mcc`, and `iwl_mvm_rx_chub_update_mcc`. Static helpers include `iwl_nvm_write_chunk`, `iwl_nvm_read_chunk`, `iwl_nvm_write_section`, `iwl_nvm_read_section`, and `iwl_parse_nvm_sections`. It uses `struct iwl_nvm_access_cmd`, `struct iwl_nvm_access_resp`, `struct iwl_nvm_section`, `struct iwl_nvm_data`, multiple MCC response versions, and cfg80211 regdomain objects.

## Control Flow
`iwl_nvm_init` allocates a temporary EEPROM-sized buffer, iterates every possible NVM section, reads each section in 2 KiB chunks via `NVM_ACCESS_CMD`, handles absent sections as nonfatal, duplicates successful section data into `mvm->nvm_sections`, exposes debugfs blobs when enabled, optionally reads an external NVM file, then parses the required sections into `mvm->nvm_data`. `iwl_mvm_load_nvm_to_nic` walks stored sections and writes each nonempty one in chunks. `iwl_mvm_update_mcc` sends `MCC_UPDATE_CMD`, normalizes firmware response versions into v8 layout, validates variable payload lengths, handles world-domain MCC zero as `"00"`, and returns an allocated response. `iwl_mvm_init_mcc` replays saved FW regulatory data or asks cfg80211/BIOS for an initial MCC. `iwl_mvm_rx_chub_update_mcc` handles asynchronous CHUB MCC notifications and installs changed regdomains unless associated and the update came from Wi-Fi.

## State And Persistence
Mutates `mvm->nvm_sections`, `mvm->nvm_data`, debugfs NVM blob wrappers, `mvm->lar_regdom_set` through helpers, and the wiphy regulatory domain. NVM data is persistent hardware/firmware configuration copied into kernel memory; external NVM overrides can replace sections at initialization. MCC updates persist in cfg80211 regulatory state and may be replayed to firmware.

## Dependencies And Integration Points
Depends on firmware command transport through `iwl_mvm_send_cmd`, NVM parser/fixup helpers from `iwl-nvm-utils.h` and `iwl-nvm-parse.h`, cfg80211 regulatory APIs, BIOS MCC/SAR helpers, LAR firmware capabilities, and the INIT firmware path in `ops.c`. `mvm.h` inline helpers consume the parsed antenna and LAR fields.

## Risks And Edge Cases
Chunked reads must not overflow configured EEPROM size. `READ_NVM_CHUNK_NOT_VALID_ADDRESS` is nonfatal only after offset zero. Required sections vary by `nvm_type`; missing SW, regulatory, MAC/HW, or PHY_SKU sections cause parse failure. MCC responses are variable-length and version-dependent, so payload length validation is critical. Regulatory updates while associated can disrupt active connections and are intentionally filtered for Wi-Fi-sourced changes.

## Test Signals
Exercise blank OTP, missing optional sections, missing mandatory sections, EEPROM-size overflow guard, external NVM overlay, NVM writeback failures, all MCC response versions, LAR disabled/enabled combinations, BIOS MCC override, CHUB MCC updates while associated and idle, and regdomain allocation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/nvm.c -->
