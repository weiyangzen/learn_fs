# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/reg.c

## Purpose

`reg.c` converts firmware regulatory events into cfg80211 regdomains, handles user country hints, updates firmware scan channel lists, maintains per-band frequency ranges, and releases regulatory memory. It is the bridge between firmware WMI regulatory information and Linux regulatory/mac80211 state.

## Important APIs And Functions

- `ath12k_reg_init()` marks the wiphy self-managed and installs `ath12k_reg_notifier()`.
- `ath12k_reg_notifier()` handles driver-initiated and user-initiated regdomain changes, optionally sends WMI current/init country commands to every radio, stops 11d scans, and triggers firmware channel-list updates after driver regd changes.
- `ath12k_reg_update_chan_list()` builds `ath12k_wmi_scan_chan_list_arg` from enabled mac80211 channels within the radio frequency range and either sends it immediately or queues work.
- `ath12k_regd_update()` waits for firmware regulatory completion, updates per-radio frequency ranges, selects default/new firmware regdomain, copies it, and calls `regulatory_set_wiphy_regd()`.
- `ath12k_reg_build_regd()` combines 2 GHz, 5 GHz, and optional 6 GHz AP/client rules into an `ieee80211_regdomain`, maps DFS/NO_IR/radar/PHY/PSD flags, updates band frequency ranges, and splits ETSI weather radar rules to apply 10-minute CAC.
- `ath12k_reg_handle_chan_list()` stores default or new regdomains and queues update work after registration.
- `ath12k_reg_validate_reg_info()` drops, accepts, or falls back firmware regulatory events based on status and pdev index.
- `ath12k_reg_free()` frees stored reg info and regdomain pointers.

## Control Flow

Firmware WMI events are parsed elsewhere into `struct ath12k_reg_info`, validated, and passed to `ath12k_reg_handle_chan_list()`. Before MAC registration, generated regdomains are stored as defaults. After registration, new regdomains are stored and `regd_update_work` applies them asynchronously. User regulatory hints flow through the notifier, which sends country commands to firmware and marks the update as user-driven. Channel-list updates wait for 11d/hardware scans to complete before sending firmware scan channel lists.

## State And Persistence

State is in `ab->default_regd[]`, `ab->new_regd[]`, `ab->reg_info[]`, `ab->dfs_region`, `ab->reg_freq_2ghz/5ghz/6ghz`, `ah->regd_updated`, per-radio completions, and queued channel-list arguments. Regulatory domains are heap allocated and freed when replaced or during `ath12k_reg_free()`. No disk persistence exists.

## Dependencies And Integration

The file depends on cfg80211/regulatory APIs, rtnl/RCU access to wiphy regd, WMI country/channel commands, MAC scan state and frequency-range helpers, workqueues, spinlocks, mutexes, and firmware regulatory constants. It integrates with mac80211 self-managed regulatory behavior and with firmware scan/channel programming.

## Risks And Test Signals

Risks include incorrect 6 GHz AP/client rule selection, missed freeing of nested regulatory rule arrays, racey replacement of regdomains, timeouts waiting for firmware completion, channel lists becoming inconsistent during scans, and fallback behavior that is still TODO. Test signals include boot with default firmware regd, user country change, dynamic hints enabled/disabled, 2/5/6 GHz channel availability, ETSI weather radar CAC values, disabled channel filtering, 11d scan interaction, WMI channel-list contents, and cleanup leak checks.
