<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/rfi.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/rfi.c

## Purpose
Contains Radio Frequency Interference Mitigation (RFIm/RFI) command support and the default DDR-frequency-to-Wi-Fi-channel lookup table. In the code as read, runtime support is intentionally disabled pending platform support detection.

## Important APIs, Types, And Functions
Public APIs are `iwl_rfi_supported`, `iwl_rfi_send_config_cmd`, `iwl_rfi_get_freq_table`, and `iwl_rfi_deactivate_notif_handler`. The default `iwl_rfi_table` is an array of `struct iwl_rfi_lut_entry` with DDR frequency units of 16.666 MHz and affected 5 GHz/6 GHz channel lists.

## Control Flow
`iwl_rfi_supported` currently always returns false. Therefore `iwl_rfi_send_config_cmd` and `iwl_rfi_get_freq_table` return `-EOPNOTSUPP` before sending firmware commands. If enabled in the future, config command construction would require `mvm->mutex`, copy either the default table or an OEM-provided table, set `cmd.oem` for custom tables, and send `SYSTEM_GROUP/RFI_CONFIG_CMD`. Frequency-table query would send `SYSTEM_GROUP/RFI_GET_FREQ_TABLE_CMD` with `CMD_WANT_SKB`, validate response payload size, duplicate the response, and free the firmware response. Deactivate notifications log the firmware-provided reason.

## State And Persistence
No mutable host state is kept in the current disabled path. If enabled, firmware would persist the RFI table and expose a frequency table response until reset or reconfiguration. The handler only reads notification payload.

## Dependencies And Integration Points
Depends on firmware RFI command definitions, system command group IDs, PHY band constants, `iwl_mvm_send_cmd`, and the notification dispatch table in `ops.c` for `RFI_DEACTIVATE_NOTIF`. Public prototypes are declared in `mvm.h`.

## Risks And Edge Cases
The feature is hard-disabled even if firmware has RFI capability, so callers must handle `-EOPNOTSUPP`. Default table correctness is hardware/platform-sensitive. If support is enabled later, response-size validation, mutex coverage, OEM table sizing, and platform capability detection become critical.

## Test Signals
Current tests should assert unsupported returns for config and get-table calls, no firmware command emission when unsupported, and notification logging behavior. Future enabled tests should cover default vs OEM tables, firmware send errors, malformed response size, allocation failure, and deactivate reasons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/rfi.c -->
