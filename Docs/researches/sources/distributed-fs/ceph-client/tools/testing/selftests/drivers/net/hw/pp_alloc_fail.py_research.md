
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/pp_alloc_fail.py`

## Purpose
Tests driver resilience and stats reporting when page pool allocation failures are injected through kernel function error injection while traffic is running.

## Important APIs, Types, And Functions
- `_write_fail_config()` writes debugfs fail-function knobs.
- `_enable_pp_allocation_fail()` injects `page_pool_alloc_netmems` failures with interval 511, probability 100, and unlimited times.
- `_disable_pp_allocation_fail()` disables injection and clears the inject target.
- `test_pp_alloc()` checks `rx-alloc-fail` qstats, starts sustained `GenerateTraffic`, enables failures, validates counters and traffic continuity, then tries a ring-size wobble with `ethtool -G`.

## Control Flow
The test first ensures qstats expose `rx-alloc-fail`; if not, it skips. It starts iperf traffic, confirms packets are flowing, enables fail injection, samples counters for three seconds, checks failure growth against packet count, optionally changes RX ring size, and confirms traffic still flows. A `finally` block disables injection, stops traffic, and restores ring size if changed.

## State And Persistence
Mutates `/sys/kernel/debug/fail_function/*` and possibly NIC RX ring size. The critical fail injection state is restored in `finally`, reducing risk of leaving global kernel fault injection enabled.

## Dependencies And Integration Points
Depends on debugfs, `CONFIG_FUNCTION_ERROR_INJECTION`, page pool fail injection support, `NetdevFamily.qstats_get()`, `GenerateTraffic`, iperf3, and ethtool ring configuration.

## Risks
Global fail-function settings can affect unrelated networking during the test. Thresholds are heuristic: failure rate is expected at roughly one per 512 buffers with a 3.1x safety margin, and low failure rates become skips rather than failures.

## Test Signals
Pass requires traffic rate above 4000 RX packets per second before/during injection, increasing `rx-alloc-fail`, expected minimum fail count, and no traffic collapse after optional ring resize.
