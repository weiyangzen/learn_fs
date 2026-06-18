
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/rss_input_xfrm.py`

## Purpose
Tests symmetric RSS input transforms by sending UDP traffic with swapped source/destination ports and asserting both directions map to the same incoming CPU while still using multiple CPUs across different flows.

## Important APIs, Types, And Functions
- `traffic()` sends one remote `socat` UDP packet and returns the local socket's `SO_INCOMING_CPU`.
- `_rss_input_xfrm_try_enable()` reads current RSS input transforms and tries to enable a symmetric transform from ethtool netlink constants.
- `test_rss_input_xfrm()` runs repeated swapped-port probes for one IP version.
- `test_rss_input_xfrm_ipv4()` and `test_rss_input_xfrm_ipv6()` wrap the common test with IP-version requirements.

## Control Flow
The test skips unless at least two CPUs and Python `SO_INCOMING_CPU` are available. It enables or reuses a symmetric transform, then tries up to 100 random port pairs until 10 successful swapped-port comparisons pass. It finally checks that observed CPUs include at least two values, proving hashing is not trivially pinned.

## State And Persistence
Mutates RSS `input-xfrm` if no symmetric transform is already active. A deferred netlink set restores the original transform set.

## Dependencies And Integration Points
Depends on `NetDrvEpEnv`, `EthtoolFamily`, `socat` on remote, ethtool netlink `input-xfrm` constants, Python socket CPU reporting, and IPv4/IPv6 endpoint configuration.

## Risks
The broad `except` in the loop ignores transient failures and keeps trying, which helps with random port collisions but can hide repeated send/setup issues until the final fail. CPU mapping is an indirect proxy for queue hashing.

## Test Signals
Pass requires matching CPUs for each swapped-port pair, ten successful probes, and at least two distinct CPUs across all successful probes. Lack of symmetric transform support produces a skip.
