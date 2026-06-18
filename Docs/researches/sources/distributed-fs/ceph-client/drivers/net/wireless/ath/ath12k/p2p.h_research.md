# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/p2p.h

## Purpose

`p2p.h` declares the minimal P2P NOA update API used by WMI/event code and MAC management-frame generation. It keeps P2P-specific details out of broader MAC headers except where cached NOA IEs are appended.

## Important APIs And Types

- `struct ath12k_p2p_noa_arg` is the iterator payload for vdev-based NOA updates. It carries the target `vdev_id`, `struct ath12k *ar`, and firmware `struct ath12k_wmi_p2p_noa_info *`.
- `ath12k_p2p_noa_update()` updates a known `struct ath12k_link_vif`.
- `ath12k_p2p_noa_update_by_vdev_id()` resolves an update by firmware vdev ID through active mac80211 interface iteration.

## Control Flow, State, And Integration

The header exposes functions implemented in `p2p.c`. Callers usually receive WMI P2P NOA data, then either already know the link vif or only know a firmware vdev ID. The implementation updates `ath12k_vif` AP state under the radio data lock and later MAC code appends cached data to management frames.

## Dependencies, Risks, And Test Signals

It includes `wmi.h` for the firmware NOA type and relies on ath12k core type declarations from including contexts. API risk is low, but signature changes affect WMI event consumers and management TX paths. Test signals are build coverage and P2P GO NOA updates producing expected beacon/probe-response IEs.
