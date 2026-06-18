
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/ntuple.py`

## Purpose
Tests ethtool NFC / ntuple flow steering to RX queues for IPv4/IPv6 and TCP/UDP, using different combinations of source/destination IP and L4 port match fields.

## Important APIs, Types, And Functions
- `NtupleField` enumerates source IP, destination IP, source port, and destination port.
- `_require_ntuple()` checks the `ntuple-filters` feature is active.
- `_setup_isolated_queue()` ensures multiple combined channels, sets RSS to queue 0, and selects a nonzero test queue.
- `_ntuple_rule_add()` installs a rule and defers deletion.
- `_send_traffic()` uses local/remote `socat` to generate deterministic flows.
- `queue()` is variant-expanded across IP versions, protocols, and field sets.

## Control Flow
Each `queue()` variant checks IP version and ntuple support, isolates default traffic to queue 0, records queue stats, installs a flow rule to a random nonzero queue, sends 40 packets, then verifies those packets hit the target queue and no unrelated idle queues.

## State And Persistence
Mutates combined channel count, RSS indirection table, and ntuple rules. All expected reversible changes use `defer()` so normal ksft cleanup restores channels, RSS defaults, and rule deletion.

## Dependencies And Integration Points
Depends on `NetDrvEpEnv`, `EthtoolFamily`, `NetdevFamily.qstats_get()`, ethtool `-N`, `-L`, `-X`, remote `socat`, and hardware queue stats. It uses `cfg.wait_hw_stats_settle()` to account for delayed stats updates.

## Risks
It assumes queue stats are accurate enough to identify per-queue packet counts and that background traffic does not hit idle queues. It skips if ntuple is unavailable rather than enabling it.

## Test Signals
At least 40 packets must appear on the selected queue, and the sum on idle queues excluding queue 0 and the test queue must remain zero.
