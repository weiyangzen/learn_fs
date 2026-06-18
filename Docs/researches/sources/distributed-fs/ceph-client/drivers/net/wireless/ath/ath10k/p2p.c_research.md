# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/p2p.c

## Purpose

`p2p.c` maintains Wi-Fi Direct Notice of Absence information for ath10k AP/P2P-GO virtual interfaces. Firmware reports NOA timing through WMI, and this file converts `struct wmi_p2p_noa_info` into a vendor-specific P2P information element stored on `struct ath10k_vif` for beacon/probe-response use.

## Important APIs, Types, and Functions

- `ath10k_p2p_noa_update()` updates one `ath10k_vif`.
- `ath10k_p2p_noa_update_by_vdev_id()` iterates active mac80211 interfaces and updates the vif whose `vdev_id` matches a firmware event.
- `ath10k_p2p_noa_ie_len_compute()` returns zero for no descriptors/no OppPS, otherwise computes the full vendor IE length.
- `ath10k_p2p_noa_ie_fill()` serializes the WFA P2P vendor IE and `ieee80211_p2p_noa_attr`.
- `ath10k_p2p_noa_ie_assign()` frees old NOA data and installs a new pointer/length under `data_lock`.
- `struct ath10k_p2p_noa_arg` carries vdev ID and NOA pointer through the mac80211 iterator.

## Control Flow

The direct update path takes `ar->data_lock`, clears existing NOA state, computes the required IE length, returns if no IE is needed, allocates with `GFP_ATOMIC`, fills the IE, and stores it. The vdev-ID path wraps the WMI vdev ID and calls `ieee80211_iterate_active_interfaces_atomic()`, whose callback compares `arvif->vdev_id` and invokes the direct update.

IE serialization writes the vendor element ID/length, WFA OUI and P2P type, NOA attribute ID/length, index, CTWindow/OppPS byte, and each descriptor. `type_count` is converted from WMI little-endian storage; the remaining descriptor timing fields are copied as represented by the WMI structure.

## State and Persistence Behavior

Persistent state is per-vif AP storage:

- `arvif->u.ap.noa_data`
- `arvif->u.ap.noa_len`

Old allocations are freed before new data is installed. Allocation failure leaves the vif with no NOA IE rather than stale data. Updates are protected by `ar->data_lock`.

## Dependencies and Integration Points

The file depends on `core.h`, `wmi.h`, `mac.h`, and `p2p.h`; WMI NOA fields; mac80211/cfg80211 P2P vendor IE definitions; and `ieee80211_iterate_active_interfaces_atomic()`. Beacon/probe-response generation consumes the stored NOA buffer.

## Risks and Edge Cases

- Correct bounds depend on WMI `num_descriptors` matching the mac80211 NOA descriptor array contract.
- `GFP_ATOMIC` allocation can fail under memory pressure and silently clear NOA data.
- The vdev-ID path runs in atomic iteration context, so the implementation cannot block.
- Duration/interval/start-time endian assumptions are inherited from `struct wmi_p2p_noa_info`.

## Test Signals

- P2P GO frame captures should show the NOA IE only when descriptors or OppPS are active.
- Synthetic WMI events should cover zero descriptors, maximum descriptors, OppPS-only, repeated replacement, and clear paths.
- Lockdep and leak checks should verify `data_lock` discipline and old-buffer freeing.
