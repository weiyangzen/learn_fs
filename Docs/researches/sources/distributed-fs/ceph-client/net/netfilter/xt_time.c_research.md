<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_time.c -->
# sources/distributed-fs/ceph-client/net/netfilter/xt_time.c

## Purpose
`xt_time.c` implements time-of-day, date-range, weekday, and monthday matching for x_tables rules using wall-clock time.

## Important APIs, Types, and Functions
`time_mt()` is the matcher over `struct xt_time_info`. Calendar conversion is split across `localtime_1()`, `localtime_2()`, and `localtime_3()` using static day tables and `struct xtm`. `time_mt_check()` validates daytime and flags.

## Control Flow, State, and Persistence
Packet evaluation uses `ktime_get_real_seconds()` rather than skb timestamps, optionally adjusts by global `sys_tz`, checks date_start/date_stop, checks daytime including overnight ranges, optionally rewinds one day for contiguous overnight semantics, then checks weekday and monthday masks. No per-rule runtime state changes.

## Dependencies and Integration Points
It depends on x_tables, kernel real-time clock access, global timezone state, and UAPI masks. It registers an NFPROTO_UNSPEC match with IPv4/IPv6 aliases.

## Risks and Test Signals
Risks include wall-clock jumps, timezone configuration, y2038/y2106 expectations, overnight contiguous semantics, leap-year calendar conversion, and monthday bit numbering. Tests should cover date bounds, daytime bounds, overnight ranges with and without contiguous, weekdays, monthdays, leap days, timezone offsets, invalid flags, and time changes while packets traverse multiple rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/xt_time.c -->
