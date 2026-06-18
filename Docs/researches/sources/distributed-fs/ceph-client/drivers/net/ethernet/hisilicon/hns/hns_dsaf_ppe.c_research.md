# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_ppe.c

## Purpose

`hns_dsaf_ppe.c` implements initialization, reset, configuration, statistics, and register dump support for the HNS DSAF PPE blocks. PPE sits between software rings/RCB and the DSAF switching fabric, so this file programs packet parsing/checksum behavior, queue-id mode selection, RSS key and indirection state for v2 hardware, VLAN stripping, per-channel port mode, and common PPE reset sequencing.

## Important APIs, Types, And Functions

The exported entry points are `hns_ppe_init`, `hns_ppe_uninit`, `hns_ppe_reset_common`, `hns_ppe_wait_tx_fifo_clean`, `hns_ppe_update_stats`, `hns_ppe_get_sset_count`, `hns_ppe_get_regs_count`, `hns_ppe_get_regs`, `hns_ppe_get_strings`, `hns_ppe_get_stats`, `hns_ppe_set_tso_enable`, `hns_ppe_set_rss_key`, and `hns_ppe_set_indir_table`. They operate on `struct hns_ppe_cb` and `struct ppe_common_cb` declared in `hns_dsaf_ppe.h`.

Key internal helpers allocate common PPE state with `devm_kzalloc`, derive MMIO bases from `dsaf_dev->ppe_base`, initialize per-PPE channel control blocks, select `enum ppe_qid_mode` from `dsaf_dev->dsaf_mode`, toggle soft resets via `dsaf_dev->misc_op`, and mask/clear exception interrupts.

## Control Flow

`hns_ppe_init` loops over `HNS_PPE_COM_NUM`, allocates PPE common state and matching RCB common state, populates per-PPE and per-RCB ring configuration, then calls `hns_ppe_reset_common` for each common block. `hns_ppe_reset_common` resets the PPE common block, initializes each existing PPE channel only if a matching `mac_cb` exists, initializes RCB common hardware, then commits the RCB initialization. `hns_ppe_init_hw` resets a channel, disables PPE exception interrupts, chooses GE mode for debug PPEs and XGE mode for service PPEs, enables protocol checksum checking, clears counters, and for v2 disables VLAN strip, sets max frame length, programs a generated RSS key, and installs a default linear indirection table.

Runtime mutation is small and direct: RSS and TSO setters write PPEv2 registers, and `hns_ppe_wait_tx_fifo_clean` polls `PPE_CURR_TX_FIFO0_REG` until the lower FIFO count bits drain or reports `-EBUSY`.

## State And Persistence

The durable driver state is in devm-managed `ppe_common_cb` objects attached to `dsaf_dev->ppe_common[]`, per-channel `hns_ppe_cb` shadows, RSS key/indirection arrays, and cumulative software-maintained `hns_ppe_hw_stats`. Hardware register state is volatile and reconstructed during reset or open flows. `hns_ppe_update_stats` accumulates hardware counters into 64-bit software fields; it does not clear all source counters except where hardware counter-clear enable has been configured.

## Dependencies And Integration Points

This file depends on `hns_dsaf_main.h`, `hns_dsaf_mac.h`, `hns_dsaf_rcb.h`, and the register helpers/macros in `hns_dsaf_reg.h`. It integrates with RCB setup through `hns_rcb_common_get_cfg`, `hns_rcb_get_cfg`, `hns_rcb_common_init_hw`, and `hns_rcb_common_init_commit_hw`, and with ethtool through stats strings and register dump callbacks routed by higher-level AE operations.

## Risks And Test Signals

Primary risks are bad DSAF-mode to QID-mode mappings, incorrect FIFO drain timeouts during reset or close, RSS table width assumptions (`& 0x1F`), and reset ordering between PPE and RCB. Useful test signals include successful probe across service/debug modes, no `get ppe queue mode failed` or FIFO timeout logs, RSS key/indir ethtool round-trips on v2 hardware, stable packet distribution after reset, and sane PPE counters in `ethtool -S` and register dumps.
