# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/p2p.h

Purpose: Declares the public P2P NOA update interface for ath11k. It keeps WMI P2P NOA event handling decoupled from the implementation that builds and stores beacon-ready P2P NOA IEs.

Important APIs and types: `struct ath11k_p2p_noa_arg` carries a firmware `vdev_id` and `struct ath11k_wmi_p2p_noa_info` pointer into mac80211 interface iteration. `ath11k_p2p_noa_update()` updates a known `ath11k_vif`. `ath11k_p2p_noa_update_by_vdev_id()` locates the vif by vdev ID before updating. The header forward-declares `struct ath11k_wmi_p2p_noa_info` and includes WMI definitions needed by users.

Control flow: WMI event code can call the by-vdev helper when only a vdev ID is known. MAC/vif-specific code can call the direct helper when it already holds the `ath11k_vif`. Both routes converge in `p2p.c` and update cached AP NOA data under the radio data lock.

State and persistence behavior: The header has no own state. Its declared helpers mutate per-vif NOA cache state in the implementation. The `noa` pointer in `ath11k_p2p_noa_arg` is borrowed for the duration of interface iteration and must outlive that synchronous call.

Dependencies and integration points: Depends on ath11k core types, WMI P2P structures, and mac80211 interface iteration through the implementation. It is an integration point between firmware event decoding and AP beacon/probe-response generation.

Risks and edge cases: Callers must pass a valid `ath11k_vif` or vdev ID matching an active interface; otherwise the update is ignored. Since by-vdev iteration is atomic, the implementation must not sleep. The borrowed NOA pointer must not point to stack data that expires before iteration completes.

Test signals: Compile coverage for WMI users of the header, direct and by-vdev update paths, missing vdev ID handling, and AP teardown with pending NOA updates.
