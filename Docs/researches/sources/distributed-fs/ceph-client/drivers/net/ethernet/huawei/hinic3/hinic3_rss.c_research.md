
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_rss.c

## Purpose
`hinic3_rss.c` manages Receive Side Scaling setup for hinic3. It allocates RSS key/indirection resources, chooses queue count, initializes default RSS hash types, programs hash key/type/indirection table into hardware, enables or disables RSS, and cleans software RSS resources.

## Important APIs, Types, And Functions
- `hinic3_try_to_enable_rss()` is the capability-gated setup path. It reads max queues, checks RSS feature support, allocates RSS key/indir arrays, sets the RSS flag, selects queue count, initializes default RSS parameters, and preloads hardware RSS resources with RSS disabled.
- `hinic3_rss_init()` enables RSS at interface start by calling `hinic3_set_hw_rss_parameters(netdev, 1)`.
- `hinic3_rss_uninit()` disables RSS with `hinic3_rss_cfg(..., 0, 0)`.
- `hinic3_clear_rss_config()` frees `rss_hkey` and `rss_indir`.
- `hinic3_rss_set_indir_tbl()` sends the indirection table through command queue `L2NIC_UCODE_CMD_SET_RSS_INDIR_TBL`.
- `hinic3_set_rss_type()`, `hinic3_rss_set_hash_type()`, `hinic3_rss_set_hash_key()`, and `hinic3_rss_cfg()` use management mailbox commands for RSS context, hash engine, key, and enable state.

## Control Flow
Capability setup starts by determining `max_qps` from hardware. If only one queue or no RSS feature is present, the driver clears RSS and uses available queues directly. Otherwise it allocates `rss_hkey` and `rss_indir`, fills a random-ish netdev RSS key, selects default queue count via `netif_get_num_default_rss_queues()`, enables default IPv4/IPv6/TCP/UDP hash types, writes hardware RSS key, fills the indirection table with `ethtool_rxfh_indir_default()`, programs indir/type/hash engine, and leaves RSS disabled until `hinic3_rss_init()` is called.

## State And Persistence Behavior
RSS state lives in `struct hinic3_nic_dev`: `rss_hkey`, `rss_indir`, `rss_hash_type`, `rss_type`, `q_params.num_qps`, `max_qps`, and `HINIC3_RSS_ENABLE` flag. Hardware holds RSS tables and key after mailbox/cmdq programming. The state is re-created at driver/device setup and freed by `hinic3_clear_rss_config()`.

## Dependencies And Integration Points
This file depends on ethtool RSS helpers, `hinic3_cmdq`, `hinic3_mbox`, `hinic3_nic_cfg`, `hinic3_hwif`, and `hinic3_nic_dev`. It integrates with netdev queue sizing, feature discovery from `hinic3_nic_io`, management firmware, and hardware L2NIC microcode.

## Risks And Edge Cases
- On RSS allocation or hardware programming failure, the driver falls back to one queue and clears RSS config.
- `hinic3_set_rss_type()` returns `MGMT_STATUS_CMD_UNSUPPORTED` directly for unsupported firmware; callers currently treat any nonzero result as failure.
- `hinic3_rss_cfg_hash_type()` stores enum values through a pointer and must keep set/get opcode semantics correct.
- Queue count must be initialized before building indirection table, or entries could point outside the configured queue set.

## Test Signals
Validate probe on hardware with and without RSS support, multi-queue packet distribution, ethtool RSS hash/key visibility if exposed elsewhere, fallback to single queue on injected mailbox/cmdq failures, and clean disable on interface stop.
