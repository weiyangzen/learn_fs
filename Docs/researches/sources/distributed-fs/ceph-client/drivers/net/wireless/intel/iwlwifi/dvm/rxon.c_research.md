# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/rxon.c

## Purpose
`rxon.c` owns DVM RXON context configuration and commit logic. RXON commands describe firmware receive/transmit context state: interface type, channel, band, BSSID, node address, association bit, basic ACK rates, HT flags, RX chains, hardware crypto, beacon timing, QoS, PAN coexistence slots, and TX power. The file translates mac80211 configuration and BSS changes into staging RXON state and decides whether firmware can be updated with `RXON_ASSOC` or needs a full RXON transition.

## Important APIs, Types, And Functions
- `iwl_connection_init_rx_config()` initializes `ctx->staging` from interface type, channel, band, and default HT basic rates.
- `iwlagn_commit_rxon()` is the central commit function for a staging RXON context.
- `iwl_full_rxon_required()` compares staging and active RXON fields to choose full RXON vs association update.
- `iwlagn_send_rxon_assoc()` sends the smaller RXON association update when only allowed flags/rates/chains changed.
- `iwlagn_rxon_disconn()` clears association, restores firmware station/key state, and updates active RXON.
- `iwlagn_rxon_connect()` sends timing/QoS/beacon data, full associated RXON, sensitivity init, and TX power.
- `iwl_send_rxon_timing()` computes and sends beacon timing, DTIM, listen interval, and beacon init values.
- `iwlagn_set_pan_params()` programs two-slot BSS/PAN time slicing.
- `iwl_set_rxon_ht()` and `_iwl_set_rxon_ht()` translate HT configuration into RXON channel-mode/protection flags and RX chain selection.
- `iwl_set_rxon_channel()` and `iwl_set_flags_for_band()` update channel and 2.4/5 GHz flags.
- `iwl_check_rxon_cmd()` validates staging RXON before commit.
- `iwl_calc_basic_rates()` derives firmware ACK/basic-rate bitmaps from mac80211 BSS basic rates plus mandatory lower rates.
- `iwlagn_mac_config()` handles global mac80211 configuration changes.
- `iwlagn_bss_info_changed()` handles per-vif BSS changes such as association, QoS, beaconing, HT operation, protection, BSSID, and IBSS station management.
- `iwlagn_post_scan()` applies deferred power/TX/RXON/PAN changes after scanning.

## Control Flow
Configuration is staged first, committed later. Interface creation or reset calls `iwl_connection_init_rx_config()` to populate `ctx->staging`. mac80211 changes enter through `iwlagn_mac_config()` and `iwlagn_bss_info_changed()`, which mutate staging fields while holding `priv->mutex`. If staging differs from active, they call `iwlagn_commit_rxon()`.

`iwlagn_commit_rxon()` recalculates basic rates, sets TSF-to-host and protection flags, adjusts short-slot state, validates the command, aborts conflicting channel switches, and then branches. If `iwl_full_rxon_required()` is false, it sends `RXON_ASSOC`, copies staging to active, applies deferred TX power, and updates power mode. If a full RXON is needed, it configures hardware crypto, first sends an unassociated RXON through `iwlagn_rxon_disconn()`, updates PAN parameters, and if the target is associated calls `iwlagn_rxon_connect()`.

Disconnect is special because unassociated RXON clears firmware station and WEP key tables. `iwlagn_rxon_disconn()` therefore clears the driver's ucode-active station bits, updates broadcast station LQ, restores driver-known stations, and restores default WEP keys before copying staging to active.

Association connect sends timing first for BSS contexts, updates QoS, sends a beacon before AP RXON when needed, sends the full associated RXON, sends IBSS beacon after assoc for adhoc, initializes sensitivity, and forces TX power programming because channel retune requires it.

Post-scan flow applies changes deferred while scanning: power mode, TX power, pending RXON commits for each context, and PAN parameters.

## State And Persistence Behavior
Each `struct iwl_rxon_context` maintains `staging` and `active` RXON commands. Staging is the desired software state; active mirrors the last committed firmware state. Additional persistent context state includes timing, beacon interval, QoS data, WEP keys, HT mode/protection, whether multiple chains are needed, station IDs, and active/vif flags.

The file also updates global persistent state such as `priv->band`, `priv->timestamp`, `priv->tx_power_user_lmt`, `priv->tx_power_next`, `priv->beacon_skb`, `priv->beacon_ctx`, `priv->have_rekey_data`, chain noise calibration state, and PAN slot settings in firmware.

Scanning can defer TX power and RXON commits. `iwlagn_post_scan()` is responsible for reconciling deferred software state with firmware.

## Dependencies And Integration Points
`rxon.c` depends on mac80211 config and BSS callbacks, firmware commands (`ctx->rxon_cmd`, `rxon_assoc_cmd`, `rxon_timing_cmd`, QoS and PAN commands), station restoration from `sta.c`, WEP key restoration, beacon command generation, power management, calibration, Bluetooth coexistence monitoring, scan status, and channel-switch completion.

It integrates with rate control and station code indirectly by changing HT40, RX chains, and station restoration conditions. It integrates with scan code by deferring changes during scan and by using `STATUS_SCAN_HW` in PAN slot calculations. It integrates with RF calibration by resetting chain-noise calibration after association.

## Risks And Edge Cases
- Incorrect full-RXON vs RXON_ASSOC classification can either retune unnecessarily or attempt an unsupported partial update.
- Full unassociated RXON clears firmware station and WEP state; failure to restore stations, broadcast station LQ, or keys breaks traffic after channel/interface changes.
- PAN timing has dual-context assumptions enforced by `BUILD_BUG_ON(NUM_IWL_RXON_CTX != 2)`. Extending contexts requires redesign.
- Beacon timing copies values between BSS and PAN in some association states; zero or mismatched beacon intervals can cause poor power-save or PAN behavior.
- `iwl_set_tx_power()` defers during scan or channel change and must restore previous limits on command failure.
- HT40 flags depend on mac80211 channel definition, peer capability, context association state, and regulatory/channel flags. A wrong flag can make firmware transmit with an invalid width.
- `iwl_check_rxon_cmd()` catches invalid combinations such as multicast addresses, missing mandatory basic rates, impossible CCK/short-slot combinations, and zero channel. Treat warnings as real configuration bugs.
- `iwlagn_bss_info_changed()` assumes context/vif readiness under mutex; races during teardown are handled by early returns, but new paths must preserve locking.

## Test Signals
High-value tests include association/disassociation, AP/IBSS/station modes, channel switch, HT20/HT40 changes, power-save and idle changes, TX power changes during scan and after scan, hardware and software crypto toggles, QoS updates, beacon interval changes, AP/IBSS beacon updates, BSS plus PAN coexistence, WEP key restoration after RXON, station restoration after full RXON, and chain-noise calibration start after association. Debug output from `iwl_print_rx_config_cmd()` and validation warnings from `iwl_check_rxon_cmd()` are useful diagnostics.
