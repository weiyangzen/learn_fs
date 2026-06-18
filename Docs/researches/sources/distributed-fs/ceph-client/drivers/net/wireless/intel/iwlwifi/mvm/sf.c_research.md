# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/sf.c

### Purpose
`sf.c` manages iwlwifi MVM Smart FIFO configuration. Smart FIFO changes firmware buffering/watermark and timeout behavior based on active interface count and whether the single active station interface is associated with an AP.

### Important APIs, Types, And Functions
The public entry point is `iwl_mvm_sf_update()`. `struct iwl_mvm_active_iface_iterator_data` carries state while iterating active interfaces. `iwl_mvm_bound_iface_iterator()` counts active non-P2P-device MACs with bound PHY contexts and captures station AP state. `iwl_mvm_fill_sf_command()` builds `struct iwl_sf_cfg_cmd` watermarks and timeout tables. `iwl_mvm_sf_config()` validates and sends `REPLY_SF_CFG_CMD` and updates `mvm->sf_state`.

### Control Flow
`iwl_mvm_sf_update()` exits early when firmware exposes the newer Smart FIFO offload API, during hardware restart, or for P2P-device vifs. It iterates active interfaces excluding the changed vif, optionally adds the changed vif if it is not being removed, and chooses the target state. With no active MACs it selects `SF_INIT_OFF`; with one active MAC it selects `SF_FULL_ON` only for an associated station vif with a DTIM period, `SF_INIT_OFF` for unassociated station state, or `SF_UNINIT` for a single non-station interface; with multiple active MACs it selects `SF_UNINIT`. It then delegates to `iwl_mvm_sf_config()`.

`iwl_mvm_sf_config()` avoids redundant commands except when remaining in `SF_FULL_ON`, because station antenna/NSS capabilities may have changed and the watermarks need recalculation. For `SF_FULL_ON`, it requires a station pointer. `iwl_mvm_fill_sf_command()` derives the full-on watermark from the AP station link capabilities: legacy uses `SF_W_MARK_LEGACY`; HT/VHT/HE/EHT links choose SISO, MIMO2, or MIMO3 by maximum RX NSS across links. Unassociated/default configuration uses MIMO2 and the default timeout table. All long-delay timeouts use `SF_LONG_DELAY_AGING_TIMER`; full-on timeouts are copied from station or default static tables.

### State, Persistence, And Dependencies
Persistent driver state is `mvm->sf_state`; firmware state is updated asynchronously by `REPLY_SF_CFG_CMD`. The command contains state, two watermark slots, long-delay timeout matrix, and full-on timeout matrix. The file depends on mac80211 active-interface iteration, MVM vif wrappers, station link capabilities under RCU, firmware API capability checks, Smart FIFO constants/macros from MVM headers, and `iwl_mvm_send_cmd_pdu()`.

### Integration Points
Smart FIFO updates are expected around vif add/remove and association state transitions. The logic integrates with interface binding (`deflink.phy_ctxt`), station association (`vif->cfg.assoc`, `bss_conf.dtim_period`, `mvmvif->ap_sta`), MLO link station capabilities, hardware restart state, and firmware capability negotiation. It deliberately ignores P2P devices and turns Smart FIFO off/uninitialized when multiple active MACs make single-BSS assumptions invalid.

### Risks
The state choice depends on active-interface iteration plus a separate changed-vif adjustment, so callers must pass `changed_vif` and `remove_vif` accurately. `SF_FULL_ON` requires `mvmvif->ap_sta`; missing AP station data returns `-EINVAL`. NSS selection scans all station links under RCU and treats any HT/VHT/HE/EHT support as non-legacy; incorrect link capability data can produce wrong watermarks. The command is sent asynchronously, so `mvm->sf_state` records successful submission rather than firmware completion. Firmware supporting `IWL_UCODE_TLV_API_SMART_FIFO_OFFLOAD` bypasses this path entirely.

### Test Signals
Exercise transitions for zero interfaces, one unassociated station, one associated station with DTIM, one AP/non-station interface, multiple active MACs, changed-vif removal, P2P-device ignore, hardware restart ignore, and firmware offload-capability ignore. Validate watermark selection for legacy, 1x1, 2x2, and 3+ NSS AP links, including MLO stations with multiple links. Check that repeated non-`SF_FULL_ON` states suppress duplicate commands and repeated `SF_FULL_ON` recalculates after antenna capability changes.
