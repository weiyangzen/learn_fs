# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/devices.c

## Purpose

`devices.c` provides DVM device-family specialization for Intel 1000/100/2000/105/2030/135/5000/5150/6000/6000i/6005/6050/6150/6030 families. It fills `struct iwl_dvm_cfg` instances with family-specific callbacks, sensitivity tables, thermal thresholds, BT coexistence defaults, NIC register configuration, and channel-switch command implementations.

## Important APIs, Types, and Functions

The exported objects are the `iwl_dvm_*_cfg` constants selected by `main.c` based on `trans->mac_cfg->device_family`. Local helpers include `iwl1000_set_ct_threshold()`, `iwl1000_nic_config()`, beacon-time helpers `iwl_usecs_to_beacons()` and `iwl_add_beacon_time()`, family-specific `*_hw_set_hw_params()` callbacks, `iwl2000_nic_config()`, `iwl_temp_calib_to_offset()`, `iwl5150_temperature()`, `iwl5000_hw_channel_switch()`, `iwl6000_nic_config()`, and `iwl6000_hw_channel_switch()`.

Static `struct iwl_sensitivity_ranges` tables define per-family OFDM/CCK energy/correlation thresholds. Static `struct iwl_dvm_bt_params` instances define advanced coexistence capabilities, priority boost, aggregation time limit, SCO handling, and command-session version.

## Control Flow

At op-mode start, `main.c` chooses one config object and later calls `priv->lib->set_hw_params()`, `priv->lib->nic_config()`, `priv->lib->temperature()`, and optionally `priv->lib->set_channel_switch()`. Hardware parameter callbacks set CT-kill thresholds and sensitivity table pointers. NIC callbacks set CSR/peripheral bits, such as SVR voltage for 1000, radio IQ inversion for 2000, calibration version and radio SKU bits for 6000-series variants.

Channel-switch callbacks build either `struct iwl5000_channel_switch_cmd` or dynamically allocated `struct iwl6000_channel_switch_cmd`, compute firmware switch time from mac80211 CSA count, TSF, current ucode beacon time, and beacon interval, set channel/RXON flags/radar expectations, and send `REPLY_CHANNEL_SWITCH`.

## State and Persistence Behavior

The file writes persistent fields in `priv->hw_params`, `priv->temperature`, and family config constants. NIC config writes hardware CSR/PRPH registers. Channel-switch updates are sent to firmware but rely on mac80211-side state prepared in `mac80211.c` (`ctx->staging`, `priv->switch_channel`, and `STATUS_CHANNEL_SWITCH_PENDING`).

## Dependencies and Integration Points

Dependencies include `iwl-io.h`, `iwl-prph.h`, `iwl-nvm-utils.h`, `agn.h`, `dev.h`, `commands.h`, Linux unit conversions, mac80211 channel-switch structures, and DVM command send helpers. Thermal callbacks integrate with `iwl_tt_handler()`, and channel switch integrates with `iwlagn_mac_channel_switch()` and firmware notifications.

## Risks and Edge Cases

Beacon-time arithmetic is sensitive to interval units and wrap behavior. The channel-switch code is explicitly marked `MULTI-FIXME`; it assumes the BSS context and is not fully correct for multiple active interfaces. `iwl5150_set_ct_threshold()` uses calibration values and a negative voltage-to-temperature coefficient, so bad NVM calibration can misprogram CT-kill. `iwl6000_nic_config()` warns on unknown device families, making selector correctness critical.

## Test Signals

Validation should cover boot/probe for every device family mapping, thermal threshold programming, 5150 temperature conversion with known calibration values, CSA on 5000 and 6000 command formats, radar-channel switch expectations, and register traces confirming family-specific NIC config bits.
