# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fq_band_pktlimit.sh

## Purpose

This selftest verifies that the `fq` qdisc enforces its packet limit per band rather than globally. It queues delayed IPv6 UDP packets into one priority band, fills that band, then sends traffic in a different priority band to prove it has its own quota.

## Important APIs, Types, and Functions

The script uses `in_netns.sh`, `ip`, `tc`, and the local `cmsg_sender` helper with `SO_TXTIME`. The only local helper is `die`, which reports a failed expectation and exits nonzero.

## Control Flow

If invoked without arguments, the script re-executes itself inside a private namespace. In the subprocess, it creates `dummy0`, assigns an IPv6 route, installs `tc qdisc ... fq ... limit 10`, sends three batches of 20 delayed packets, captures `tc -s qdisc` output after each batch, sleeps past the delay, captures final stats, prints all stats, and greps for expected sent/drop counts.

## State and Persistence Behavior

State is isolated to the private namespace: a dummy link, IPv6 address and route, `fq` qdisc state, delayed queued packets, and qdisc statistics. No persistent files are modified.

## Dependencies and Integration Points

It depends on `in_netns.sh`, `cmsg_sender`, IPv6, dummy netdev, `tc fq`, and `SO_TXTIME` scheduling. It integrates with the kernel fair queueing scheduler and packet priority band selection.

## Risks and Edge Cases

The test assumes delayed packets remain queued while subsequent batches are sent; timing is controlled by a 400000 microsecond delay and 0.6 second sleep. Grep-based statistic matching depends on stable `tc -s qdisc` output formatting. If `cmsg_sender` cannot set the desired priority or txtime, band isolation will not be tested correctly.

## Test Signals

Expected stats are 10 drops after the first 20 packets in one band, 30 drops after another 20 in the same band, 40 drops after sending 20 in priority band 7, and finally 20 packets sent with 40 dropped after queued packets become eligible.
