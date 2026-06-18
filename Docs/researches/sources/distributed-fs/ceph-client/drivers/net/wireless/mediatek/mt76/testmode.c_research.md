# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/testmode.c

## Purpose
Implements shared nl80211 testmode handling for mt76 PHY manufacturing/calibration tests. It parses test attributes, tracks per-PHY test parameters, allocates synthetic TX frames, starts/stops finite test transmissions, reports TX/RX stats, and delegates hardware-specific state/parameter programming to chip `test_ops`.

## Important APIs, Types, And Functions
Exports `mt76_tm_policy`, `mt76_testmode_alloc_skb()`, `mt76_testmode_tx_pending()`, `mt76_testmode_set_state()`, `mt76_testmode_cmd()`, and `mt76_testmode_dump()`. Important helpers validate rate/length parameters, compute max MPDU length by PHY mode, build fragmented SKBs for large MPDUs, track which netlink parameters were present, initialize defaults, and dump common TX/RX counters.

## Control Flow
`mt76_testmode_cmd()` parses attributes, handles reset, initializes defaults, updates fields, validates bounds, calls driver `set_params()`, records present parameters, and optionally changes state. State changes first stop active TX, then initialize TX if entering `TX_FRAMES`, call driver `set_state()`, start TX scheduling, or clear RX stats. `mt76_testmode_tx_pending()` is called from the generic TX worker to clone the prepared SKB into hardware queues until count, queue, or queued-limit constraints stop it.

## State And Persistence
Per-PHY state lives in `phy->test`: current state, TX count/length/rate/antenna/power/frequency parameters, MAC addresses, `param_set` bitmap, `tx_skb`, pending/queued/done counters, RX stats, and optional MTD metadata. It is reset by `MT76_TM_ATTR_RESET` and transiently interacts with `dev->tx_wait`.

## Dependencies And Integration Points
Depends on nl80211 testmode netlink, mac80211 TX status, mt76 TX queue ops, mt76 test hooks, random payload generation, monitor-mode requirement for active test states, and optional `CONFIG_NL80211_TESTMODE` handling in the TX completion path.

## Risks
Parameter validation must match PHY capabilities; wrong NSS/rate/length acceptance can build invalid frames. TX stop disables the generic TX worker and waits for done counters, so completion accounting must be exact. Large MPDU fragmentation manually adjusts SKB length/data_len and is sensitive to allocation failure. Some HE-related modes are passed to driver code rather than fully validated here.

## Test Signals
Netlink set/dump round trips, reset to defaults, TX_FRAMES with finite counts and queued limits, RX_FRAMES stats accumulation, invalid parameter rejection, test mode blocked when device is not running or not in monitor mode, and no SKB leaks after stop or allocation failure.
