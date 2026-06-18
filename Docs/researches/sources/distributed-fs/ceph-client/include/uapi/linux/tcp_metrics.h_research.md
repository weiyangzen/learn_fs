# sources/distributed-fs/ceph-client/include/uapi/linux/tcp_metrics.h

## Purpose
Defines the generic netlink ABI for querying and deleting cached TCP metrics by destination/source address.

## Important APIs, Types, and Constants
Family name/version are `tcp_metrics` and `0x1`. Metric indices include RTT, RTTVAR, ssthresh, cwnd, reordering, RTT in usec, and RTTVAR in usec. Nested metric attributes mirror those values. Top-level attributes include IPv4/IPv6 destination, age, TIME_WAIT timestamp data, nested values, Fast Open MSS, SYN drop counts/timestamps, Fast Open cookie, IPv4/IPv6 source address, and padding. Commands are get and delete.

## Control Flow, State, and Persistence
Userspace sends generic netlink get/delete commands. Kernel returns or removes cached per-peer TCP metrics used to initialize future connections. Cache entries persist until aged, replaced, or deleted.

## Dependencies and Integration Points
Depends on `<linux/types.h>`. Integrates with TCP metrics cache and generic netlink tooling.

## Risks and Test Signals
Risks include misspelled legacy attribute `REODERING`, address-family mismatches, and stale Fast Open cookie data. Test netlink dumps for IPv4/IPv6, source-filtered queries, delete behavior, nested metrics parsing, and compatibility with existing `ip tcp_metrics`.
