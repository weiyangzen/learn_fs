<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/vendor-cmd.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/vendor-cmd.c

Purpose: Registers Intel cfg80211 vendor commands/events for MVM and implements host userspace access to CSME connection information, CSME ownership transfer, and roaming-forbidden notifications.

Important APIs/functions: `iwl_mvm_vendor_cmds_register()` installs command and event arrays into `mvm->hw->wiphy`. `iwl_mvm_vendor_get_csme_conn_info()` returns CSME connection attributes in a vendor reply skb. `iwl_mvm_vendor_host_get_ownership()` asks MEI/CSME support code to transfer ownership to the host. `iwl_mvm_send_roaming_forbidden_event()` emits an async vendor event with vif address and forbidden flag.

Control flow: Vendor commands are selected by Intel OUI and subcommand id. The CSME info command locks `mvm->mutex`, calls `iwl_mvm_get_csme_conn_info()`, allocates a reply skb, appends auth mode, SSID, pairwise cipher, channel, and BSSID attributes, unlocks, and sends the reply. The ownership command only locks around `iwl_mvm_mei_get_ownership()`. Roaming events allocate a vendor event skb for the given wdev, append attributes, and call `cfg80211_vendor_event()`.

State and persistence: This file stores no private persistent state. Registration mutates `wiphy` vendor command/event pointers and counts. Runtime commands read CSME connection state and may mutate MEI/CSME ownership through called helpers. Events consume short-lived skbs allocated with `GFP_ATOMIC`.

Dependencies/integration: Depends on `linux/nl80211-vnd-intel.h` attribute/subcommand definitions, cfg80211 vendor command/event APIs, netlink attribute policies, mac80211 `wiphy_to_ieee80211_hw()`, MVM private object lookup, and MEI/CSME helper functions from the MVM layer.

Risks: `iwl_mvm_send_roaming_forbidden_event()` calls `ieee80211_vif_to_wdev(vif)` during allocation before checking `WARN_ON(!vif)`, so a null `vif` caller would already be unsafe. The reply skb size is fixed at 200 bytes and depends on the bounded SSID/BSSID attributes remaining small. Policy covers more attributes than each command consumes and does not validate command-specific required inputs because current commands are effectively getters. Command registration overwrites wiphy vendor pointers, so ordering matters if other code also sets them.

Test signals: Validate vendor command discovery, CSME info success and missing-info `-EINVAL`, reply allocation failure, netlink `nla_put` failure cleanup, ownership transfer return propagation, event emission with valid vif, event allocation failure, attribute encoding lengths, and lockdep coverage for `mvm->mutex`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/vendor-cmd.c -->
