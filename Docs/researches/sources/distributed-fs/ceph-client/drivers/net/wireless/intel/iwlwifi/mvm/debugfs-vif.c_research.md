# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/debugfs-vif.c

## Purpose

Implements per-VIF and per-link MVM debugfs entries for power-management overrides, TX power limit, MAC/VIF state, beacon filter tuning, OS/device time delta, low latency, U-APSD misbehavior, RX PHY info, quota minimum, max TXOP, FTM unprotected mode, and device-to-netdev debugfs symlinks.

## Important APIs, Types, and Functions

`iwl_mvm_vif_add_debugfs()` creates VIF files. `iwl_mvm_vif_dbgfs_add_link()`/`rm_link()` maintain symlinks. `iwl_mvm_link_add_debugfs()` creates per-link directories. Handler groups include PM params, BF params, low latency/force, U-APSD misbehaving, RX PHY info, quota minimum, max TXOP, MAC params, and time-diff reads.

## Control Flow

Registration creates `iwlmvm` under `vif->debugfs_dir`, conditionally adds PM and BF files, then adds general VIF files. Writes parse bounded text buffers, validate values, lock `mvm->mutex`, update debug override state, and often re-send power, beacon filter, PHY context, quota, or low-latency configuration. RX PHY info copies channel context under RCU before firmware reprogramming. Quota writes ensure only one VIF has a debug quota minimum.

## State and Persistence Behavior

Runtime debug state includes `dbgfs_pm`, `dbgfs_bf`, `low_latency`, `uapsd_misbehaving_ap_addr`, global `dbgfs_rx_phyinfo`, `dbgfs_quota_min`, `max_tx_op`, `ftm_unprotected`, and symlink dentries.

## Dependencies and Integration Points

Depends on debugfs, mac80211 VIF/link debug directories, MVM power, beacon filter, low-latency, PHY context, quota, station, TCM, and time-sync helpers plus macro wrappers from `debugfs.h`.

## Risks

Debugfs writes actively mutate firmware/driver state. Fixed input buffers truncate writes. Firmware commands must not be sent while holding RCU read lock. Quota and link/VIF state must remain serialized against teardown.

## Test Signals

Validate file creation for station/P2P/AP/monitor, PM/BF bounds, low-latency force transitions, RX PHY info reprogramming, quota conflict handling, symlink add/remove, and reads while associated/disassociated.
