
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/rss_ctx.py`

## Purpose
Provides extensive RSS behavior tests for real drivers, focused on RSS key/indirection programming, context isolation, ntuple-to-context steering, context lifetime, queue reconfiguration safety, and persistence across interface down/up.

## Important APIs, Types, And Functions
- `get_rss()`, `ethtool_create()`, `require_ntuple()`, `require_context_cnt()`, `_get_rx_cnts()`, `_send_traffic_check()`, and `_ntuple_rule_check()` are shared helpers.
- `test_rss_key_indir()` checks key and table changes plus traffic distribution.
- `test_rss_queue_reconfigure()` validates table preservation and queue-count rejection for used queues.
- `test_rss_context*()` families create one to many contexts, steer flows with ntuple rules, and validate queue sets.
- `test_rss_context_persist_ifupdown()` is marked `ksft_disruptive` and verifies contexts/filters after link cycling.

## Control Flow
`main()` creates `NetDrvEpEnv`, initializes `EthtoolFamily` and `NetdevFamily`, then runs a fixed case list from basic RSS key/table tests through context creation, overlap, deletion, default context rules, and link-cycle persistence. Traffic checks use iperf-generated packet counts and queue qstats to assert which queues receive traffic.

## State And Persistence
The test frequently changes channel counts, RSS indirection tables, hash keys, ntuple filters, and link state. `defer()` generally restores channel count, RSS defaults, and context/rule deletion. The persistence tests intentionally create contexts before or while the interface is down and expect state to remain through `ip link down/up`.

## Dependencies And Integration Points
Depends on hardware queue stats, ethtool CLI, ethtool netlink, `NetdevFamily.qstats_get()`, ntuple filters, iperf3 via `GenerateTraffic`, and stable remote connectivity. Some cases require many queues and up to 32 RSS contexts.

## Risks
Many assertions are traffic-distribution based and may be noisy on active systems, so helper parameters distinguish target, empty, and noise queues. `cfg.context_cnt` is opportunistically learned when a driver cannot allocate all requested contexts, so test order matters.

## Test Signals
Pass signals include exact queue-hit expectations, nonzero RSS keys, duplicate-free context dumps, EBUSY on deleting in-use contexts, failure for missing contexts or nonexistent target queues, no carrier/error changes for hitless key update, and preserved contexts/ntuple rules after interface up/down.
