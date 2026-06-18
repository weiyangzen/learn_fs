# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/p2p.c

## Purpose

`p2p.c` maintains Wi-Fi Direct Notice of Absence (NOA) information for AP/P2P GO interfaces. Firmware reports NOA state through WMI; this code converts it into a vendor-specific P2P IE and stores it on the ath12k vif so beacon and probe-response generation can include current absence scheduling.

## Important Functions

- `ath12k_p2p_noa_ie_len_compute()` decides whether a NOA IE is needed and computes its exact length from descriptor count and opportunistic power-save bits.
- `ath12k_p2p_noa_ie_fill()` writes the vendor IE header, WFA OUI/type, NOA attribute, index, OPPPS/CTWindow, and descriptor array.
- `ath12k_p2p_noa_ie_assign()` frees the previous `ahvif->u.ap.noa_data` and installs a new pointer/length under `ar->data_lock`.
- `ath12k_p2p_noa_update()` is the direct exported updater for a known link vif.
- `ath12k_p2p_noa_update_by_vdev_id()` iterates active mac80211 interfaces atomically and updates the default link matching the radio and firmware `vdev_id`.

## Control Flow

The update path clears any old IE first, computes whether firmware state is non-empty, allocates with `GFP_ATOMIC` while under a bottom-half spinlock, fills the IE, and assigns it. The vdev-id path builds `struct ath12k_p2p_noa_arg`, walks active interfaces with `ieee80211_iterate_active_interfaces_atomic()`, checks `is_created`, radio pointer, and vdev ID, then calls the locked updater.

## State And Persistence

NOA state is transient in memory: `ahvif->u.ap.noa_data` and `noa_len`. The old allocation is always freed before storing new state or clearing. There is no disk persistence. The data remains until the next WMI NOA update, interface removal cleanup, or explicit zero-length update.

## Dependencies And Integration

The file depends on mac80211 P2P IE structures, WMI NOA bit definitions, `core.h`, `mac.h`, and `p2p.h`. It feeds `ath12k_mac_add_p2p_noa_ie()`, which attaches the cached IE to outgoing beacon/probe-response SKBs.

## Risks And Test Signals

The code trusts firmware descriptor count to fit the destination `ieee80211_p2p_noa_attr::desc[]`; malformed or future firmware counts are a bounds risk unless upstream struct sizing and WMI validation constrain them. Allocation failure silently drops the IE. Test signals include P2P GO operation with NOA/OPPPS changes, beacon/probe-response capture verifying vendor IE encoding, interface iteration under RCU, and lockdep coverage for `ar->data_lock`.
