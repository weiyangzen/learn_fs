<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/quota.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/quota.c

## Purpose
Computes and uploads firmware time-quota allocation across active PHY bindings/MACs, with special handling for low-latency bindings and debugfs minimum quota overrides.

## Important APIs, Types, And Functions
The public function is `iwl_mvm_update_quotas`. Private state collection uses `struct iwl_mvm_quota_iterator_data` and `iwl_mvm_quota_iterator`. Command layout helpers are in `mvm.h`: `iwl_mvm_quota_cmd_size` and `iwl_mvm_quota_cmd_get_quota`.

## Control Flow
`iwl_mvm_update_quotas` requires `mvm->mutex`, exits early when firmware supports dynamic quota or when hardware restart is in progress, then iterates active interfaces. The iterator skips a caller-specified disabled vif, ignores inactive/unassociated roles, maps each vif to its PHY context ID as binding ID, validates color consistency, counts active interfaces per binding, records debugfs minimums, and marks low-latency bindings. The updater initializes all quota entries invalid, computes equal quota across active MACs or reserves `QUOTA_LOWLAT_MIN` when exactly one low-latency binding coexists with non-low-latency traffic, fills valid `id_and_color` entries, gives remainder to the first nonzero binding, suppresses practically unchanged commands unless forced, sends `TIME_QUOTA_CMD`, and caches the successful command in `mvm->last_quota_cmd`.

## State And Persistence
Reads active vif state (`assoc`, `ap_ibss_active`, `monitor_active`, `phy_ctxt`, low-latency flags), debugfs minimum quota, and `mvm->status`. Mutates only firmware scheduling state and `mvm->last_quota_cmd`; no durable host persistence exists.

## Dependencies And Integration Points
Depends on mac80211 active interface iteration, MVM vif/PHY context state, low-latency helper `iwl_mvm_vif_low_latency`, firmware dynamic-quota capability, command format version gating from `mvm.h`, and `iwl_mvm_send_cmd_pdu`. Called when interface/channel/low-latency state changes.

## Risks And Edge Cases
The code assumes `NUM_PHY_CTX <= MAX_BINDINGS` and currently `MAX_BINDINGS == 4`. PHY context ID is treated as binding ID. Equal split is by active interface count, not just binding count, so multi-interface bindings receive proportionally more quota. Low-latency reservation only applies when exactly one low-latency binding coexists with other bindings. Suppression threshold can skip small but real changes unless `force_update` is true. Zero quota for valid bindings warns.

## Test Signals
Cover no active interfaces, one STA, AP/IBSS active and inactive, monitor active, disabled vif exclusion, multiple vifs on one binding, multiple bindings, one low-latency binding with and without other traffic, multiple low-latency bindings, debugfs minimum override, unchanged-command suppression, forced upload, dynamic quota capability skip, hardware restart skip, and firmware send failure preserving `last_quota_cmd`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/quota.c -->
