# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_ptp.c

## Purpose
`hclge_ptp.c` implements PF hardware timestamping and PHC support for HNS3 devices with PTP capability. It registers a Linux PTP clock, configures timestamp modes through firmware commands, reads and writes PTP MMIO registers, handles TX and RX hardware timestamp delivery, supports clock get/set/adjtime/adjfine operations, and enables/disables PTP interrupts.

## Important APIs And Functions
- `hclge_ptp_init()` checks `HNAE3_DEV_SUPPORT_PTP_B`, creates the PHC if needed, reads cycle parameters, enables PTP interrupt, sets base frequency, restores timestamp mode, initializes PHC time from real time, and sets `HCLGE_STATE_PTP_EN`.
- `hclge_ptp_uninit()` disables interrupt and timestamp mode, clears state/flags, releases any pending TX skb, unregisters the PTP clock, and frees the PTP object.
- `hclge_ptp_set_tx_info()` is called from the TX path. It accepts at most one outstanding timestamp skb by testing `HCLGE_STATE_PTP_TX_HANDLING`, stores an skb reference, and increments counters.
- `hclge_ptp_clean_tx_hwts()` reads TX timestamp registers, stamps and frees the saved skb if present, records sequence id and counters, and clears the TX handling bit.
- `hclge_ptp_get_rx_hwts()` combines descriptor-provided low seconds/nanoseconds with high seconds from a current-time register under lock and writes skb hardware timestamp metadata.
- `hclge_ptp_get_cfg()`/`hclge_ptp_set_cfg()` implement hwtstamp get/set, validating that PHC support is enabled.
- PTP clock callbacks `hclge_ptp_adjfine()`, `hclge_ptp_adjtime()`, `hclge_ptp_gettimex()`, and `hclge_ptp_settime()` provide frequency, offset, read, and set operations.
- `hclge_ptp_cfg_qry()` is an exported firmware query helper used by diagnostics.

## Control Flow
Initialization allocates `struct hclge_ptp`, sets `ptp_clock_info` callbacks, maps `io_base` to the PTP register window, registers the PTP clock, validates cycle denominator, enables interrupt via `HCLGE_OPC_PTP_INT_EN`, writes cycle and timestamp mode config, and sets PHC time. Runtime timestamp configuration flows through `hclge_ptp_set_ts_mode()`: TX and RX filter settings are translated to hardware bits, `HCLGE_OPC_PTP_MODE_CFG` is sent, then software flags and cached `ts_cfg` are updated.

TX timestamp flow starts in the transmit path through `hclge_ptp_set_tx_info()`, then interrupt/service logic in PF main calls `hclge_ptp_clean_tx_hwts()` once hardware has produced a timestamp or timeout service needs cleanup. RX timestamp flow occurs per received skb with descriptor timestamp fields. Clock adjustment paths write MMIO registers protected by `ptp->lock`; large `adjtime` values fall back to get-plus-set.

## State And Persistence Behavior
`hdev->ptp` owns PTP state: registered clock, saved TX skb, mode flags, MMIO base, cached timestamp config, last TX sequence id, cycle parameters, counters, last RX time, and timeout counters. `HCLGE_STATE_PTP_EN` gates public operations; `HCLGE_STATE_PTP_TX_HANDLING` serializes TX timestamp requests. Configuration is in-memory and hardware-register-backed, and must be reinitialized after reset. The code uses `spin_lock_irqsave()` around PTP register sequences that require coherent multi-register access.

## Dependencies And Integration Points
The file depends on Linux PTP clock APIs, network timestamping APIs, skb timestamp helpers, MMIO read/write, firmware command descriptors, HNAE3 capability bits, and PF service/reset paths. It is wired into the PF operation table for `set_tx_hwts_info`, `get_rx_hwts`, `get_ts_info`, `hwtstamp_get`, and `hwtstamp_set`, and PF service code calls TX timestamp cleanup.

## Risks And Edge Cases
- Only one TX timestamp can be outstanding; additional timestamp requests are skipped and counted. Workloads expecting many concurrent TX timestamps may see drops.
- `hclge_ptp_set_tx_info()` increments `ptp->tx_skipped` after checking `ptp` but before any locking of the rest of `ptp`; lifecycle must ensure no concurrent uninit.
- RX high seconds are read from current-time registers rather than descriptor space; rollover between descriptor timestamp and high-second read is a subtle boundary risk.
- `hclge_ptp_init()` destroys the PTP clock on several failures, even when `hdev->ptp` was newly created in the same call; reset paths must not reuse stale pointers.
- Unsupported filters return `-ERANGE`; user tools should see normalized filters for accepted broad PTP v1/v2 event classes.

## Test Signals
Validate `ethtool -T`, `SIOCSHWTSTAMP`/netlink hwtstamp set/get for accepted and rejected filters, PHC registration, `phc2sys`/`testptp` adjustment, TX timestamp delivery and skipped-counter behavior under load, RX timestamp correctness near second rollover, reset/reinit preserving config, PTP interrupt enable failure paths, and debugfs/config query output.
