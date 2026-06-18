# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/time-sync.h

## Purpose

`time-sync.h` declares the MVM time-sync API and provides the inline frame filter/queue helper used by TX/RX paths before firmware timestamp notifications arrive.

## Important APIs

It declares initialization, measurement event handling, confirmation event handling, and configuration: `iwl_mvm_init_time_sync()`, `iwl_mvm_time_sync_msmt_event()`, `iwl_mvm_time_sync_msmt_confirm_event()`, and `iwl_mvm_time_sync_config()`. The inline `iwl_mvm_time_sync_frame()` checks whether a frame belongs to the configured peer and is a timing-measurement or FTM action frame; matches are appended to `mvm->time_sync.frame_list` and ownership is transferred to the time-sync completion path.

## State, dependencies, and risks

State is external in `struct iwl_time_sync_data`, especially `peer_addr` and `frame_list`. The header depends on `mvm.h` and Linux 802.11 helpers. The risk is ownership confusion: if the inline returns true, the caller must not free or continue normal processing of the SKB. Matching only by peer address and frame type is intentionally broad; dialog-token matching happens later in `time-sync.c`.

## Test signals

Compile coverage plus unit tests for frame classification, peer matching, queue insertion, and nonmatching frame passthrough validate the header contract.
