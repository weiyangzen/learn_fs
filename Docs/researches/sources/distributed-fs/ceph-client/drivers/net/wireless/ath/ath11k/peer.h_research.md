# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/peer.h

Purpose: Defines ath11k peer state and declares peer-management APIs. It is the shared contract for MAC, WMI, HTT/DP, and crypto code that needs to create, find, update, or remove firmware peers.

Important APIs and types: `struct ath11k_peer` contains list linkage, mac80211 STA pointer, vdev ID, MAC address, firmware peer ID, AST hash, pdev index, HW peer ID, key pointers indexed by WMI key slot, DP RX TID state for all TIDs plus management, rhashtable heads for ID/address lookup, MIC verification key indexes, security types, authorization state, and DP setup status. Declared functions cover map/unmap event handling, lookup by vdev/address/ID, cleanup, create/delete/wait-delete, rhashtable table init/destroy, and rhashtable deletion.

Control flow: WMI/HTT event handlers call map/unmap declarations when firmware reports peer ID association changes. MAC station/vdev code calls create/delete and waits for firmware completion. Data path code can look up peers by address or ID to process RX/TX metadata and security state. Recovery and teardown call cleanup and table destroy.

State and persistence behavior: The structure represents runtime peer state only. Fields annotated as protected by `ab->data_lock` must be accessed under that lock, while list/rhash fields are managed under `base_lock` and `tbl_mtx_lock` in the implementation. Key pointers are non-owning references to mac80211 key configuration and must be cleared when keys are removed.

Dependencies and integration points: Depends on list/rhashtable infrastructure, mac80211 STA/key types, WMI key constants, DP RX TID structures, and core ath11k locks. It integrates peer security, DP reorder/TID handling, firmware peer IDs, and MAC station state.

Risks and edge cases: Consumers must honor lock ownership or risk stale peer pointers after unmap. Address and ID rhashtable entries can be absent during create/delete transitions even while a list entry exists. Same-address peers on different vdevs need vdev-sensitive checks. `rx_tid[IEEE80211_NUM_TIDS + 1]` includes an extra management/non-QoS slot; users must index consistently.

Test signals: Compile users after structure changes, run lockdep under station association/disassociation, validate peer lookup by ID/address under traffic, add/remove keys across peer deletion, and test recovery cleanup with outstanding peer map/unmap events.
