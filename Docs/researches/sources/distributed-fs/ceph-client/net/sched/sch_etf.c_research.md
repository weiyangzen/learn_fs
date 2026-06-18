# sources/distributed-fs/ceph-client/net/sched/sch_etf.c

## Purpose
`sch_etf.c` implements the Earliest TxTime First qdisc. It orders packets by `skb->tstamp` transmit time, releases them only when they enter a configured delta window before txtime, optionally treats txtime as a deadline, reports missed/invalid txtime errors back to sockets, and can request hardware ETF offload.

## Important APIs, Types, and Functions
`struct etf_sched_data` stores offload/deadline/skip-socket-check flags, clockid, queue index, delta, last transmitted txtime, an rb-tree ordered by skb tstamp, a qdisc watchdog, and a clock read function pointer. Validation and packet checks are `validate_input_params()` and `is_packet_valid()`. Queue operations are `etf_enqueue_timesortedlist()`, `etf_peek_timesortedlist()`, `etf_dequeue_timesortedlist()`, `timesortedlist_drop()`, `timesortedlist_remove()`, and `timesortedlist_clear()`.

Other integration functions are `reset_watchdog()`, `report_sock_error()`, `etf_enable_offload()`, `etf_disable_offload()`, `etf_init()`, `etf_reset()`, `etf_destroy()`, and `etf_dump()`.

## Control Flow
Initialization requires `TCA_ETF_PARMS`, validates that the clock id is static, currently requires `CLOCK_TAI`, rejects negative delta, records the TX queue index, optionally enables offload through `ndo_setup_tc(dev, TC_SETUP_QDISC_ETF, ...)`, saves flags and parameters, selects the matching `ktime_get*()` function, and initializes a qdisc watchdog with the configured clock.

On enqueue, ETF validates the packet unless `skip_sock_check` is set. Normal validation requires a full socket with `SOCK_TXTIME`, matching socket clockid, matching deadline mode, a txtime not in the past, and a txtime not before the last transmitted txtime. Invalid packets are dropped and may generate a socket extended error with `SO_EE_ORIGIN_TXTIME`. Valid packets are inserted into a cached rb-tree ordered by txtime, qlen/backlog are incremented, and the watchdog is rearmed for the earliest packet's `txtime - delta`.

On dequeue, ETF peeks at the earliest packet. Expired packets with txtime before now are dropped in order and reported as missed. In deadline mode, the earliest valid packet is removed immediately and its timestamp is rewritten to now. In normal mode, the packet is removed only when now is after `txtime - delta`; otherwise dequeue returns `NULL` and the watchdog remains armed. Removal resets skb rbnode-overlaid list fields, restores `skb->dev`, updates backlog and byte stats, records `last`, and decrements qlen.

## State and Persistence
ETF state is in memory only. The rb-tree holds queued skbs ordered by txtime; `last` enforces non-decreasing transmit times; the watchdog schedules the next eligibility time. Offload and mode flags are qdisc-private config visible through dumps. Socket error reporting clones skbs transiently into the owning socket error queue when requested.

## Dependencies and Integration Points
ETF depends on rb-tree skb helpers, qdisc watchdog support, socket txtime fields and error queue APIs, POSIX clock ids, netlink `TCA_ETF_PARMS`, and hardware offload through `TC_SETUP_QDISC_ETF`. It registers qdisc id `etf` and has no class operations or child qdisc.

## Risks
Clock handling is strict: validation currently requires `CLOCK_TAI`, so users with other clocks are rejected even though a switch contains other clock readers. Packets can be dropped for socket mismatch, past txtime, or non-monotonic txtime relative to `last`; this is correct but easy to misconfigure. The rbnode overlays skb list fields, so removal must always reset `next`, `prev`, and `dev`. Offload enable failures abort init, and destroy must disable offload if it was enabled. Watchdog cancellation guards handle partially initialized qdiscs.

## Test Signals
Test missing/invalid parameters, non-TAI clock rejection, negative delta rejection, socket txtime validation, skip-socket-check mode, deadline and non-deadline dequeue timing, expired packet drops and socket errors, rb-tree ordering for equal and increasing txtimes, non-monotonic txtime rejection after `last`, offload success/failure/disable, reset clearing the tree, and watchdog arming for the earliest packet.
