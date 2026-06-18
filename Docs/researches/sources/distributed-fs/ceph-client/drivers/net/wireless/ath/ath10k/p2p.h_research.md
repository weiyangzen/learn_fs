# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/p2p.h

## Purpose

`p2p.h` declares ath10k's P2P Notice of Absence update entry points. It is the small public header used by WMI/MAC code to publish firmware NOA reports into per-vif MAC-visible state.

## Important APIs, Types, and Functions

- `ath10k_p2p_noa_update(struct ath10k_vif *arvif, const struct wmi_p2p_noa_info *noa)` updates one vif.
- `ath10k_p2p_noa_update_by_vdev_id(struct ath10k *ar, u32 vdev_id, const struct wmi_p2p_noa_info *noa)` resolves a firmware vdev ID through active mac80211 interfaces and updates the matching vif.
- The header forward-declares `struct ath10k_vif` and `struct wmi_p2p_noa_info`.

## Control Flow and Integration

WMI event code uses this header when firmware reports P2P NOA changes. If the caller already has an `ath10k_vif`, it uses the direct API; if it has only a firmware vdev ID, it uses the iterator-based API. The implementation serializes the NOA data into `arvif->u.ap.noa_data` for beacon/probe-response code.

## State and Persistence Behavior

The header has no storage. Its APIs replace or clear per-vif NOA allocation state under `ar->data_lock`.

## Dependencies and Integration Points

`p2p.h` intentionally avoids large includes. Users must include suitable ath10k core/WMI definitions when they need complete types. The implementation depends on WMI NOA data, mac80211 active-interface iteration, and P2P vendor IE definitions.

## Risks and Contract Notes

- The second prototype uses `struct ath10k *` without a local forward declaration in this header, so standalone include order matters.
- Raw pointers must refer to live ath10k/vif/WMI objects.
- Vdev-ID updates ignore events for inactive or removed interfaces.

## Test Signals

- Compile direct and transitive includes to catch missing forward declarations.
- WMI NOA tests should exercise both direct and vdev-ID APIs.
- Interface teardown/recovery tests should verify stale events do not dereference destroyed vifs.
