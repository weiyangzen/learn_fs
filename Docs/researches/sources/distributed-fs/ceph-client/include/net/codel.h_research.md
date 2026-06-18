# sources/distributed-fs/ceph-client/include/net/codel.h

Read `sources/distributed-fs/ceph-client/include/net/codel.h` completely for this pass (167 lines, 6002 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/codel.h_research.md`.

Purpose: declares common data types for the CoDel controlled-delay active queue management algorithm: time representation, tunable parameters, runtime variables, statistics, and callback types used by qdisc implementations.

Important APIs/types/functions: `codel_time_t` and `codel_tdiff_t` encode a 1024 ns tick in 32-bit arithmetic. `codel_get_time()`, `codel_time_after/before/after_eq/before_eq`, and `codel_time_to_us()` implement wrap-safe time handling. `struct codel_params` holds `target`, `ce_threshold`, `interval`, `mtu`, ECN enable, and optional DS field selector/mask for CE threshold marking. `struct codel_vars` stores count, lastcount, dropping state, reciprocal inverse square root, first-above time, next-drop time, and latest delay. `struct codel_stats` records max packet, drop counts/bytes, ECN marks, and CE marks. Callback typedefs abstract skb length, enqueue time, drop, and dequeue operations.

Control flow: qdiscs initialize params/vars/stats via helpers in `codel_impl.h`, timestamp packets with `codel_qdisc.h`, and pass callbacks into `codel_dequeue()`. The algorithm compares packet sojourn time against target for at least one interval, then enters a dropping/marking state whose interval is controlled by `interval / sqrt(count)`.

State and persistence: CoDel state is per queue or per flow in the owning qdisc. `codel_params` is configured by qdisc settings, `codel_vars` evolves while a queue remains active, and `codel_stats` accumulates runtime telemetry. Nothing is durable beyond qdisc lifetime.

Dependencies and integration points: depends on ktime, skbuffs, kernel type checking, and qdisc implementations such as CoDel/FQ-CoDel/CAKE-style users that provide callbacks and storage.

Risks: time arithmetic wraps after roughly 2199 seconds and must use provided signed-serial comparisons. Misconfigured `mtu` can suppress drops when backlog is below or equal to MTU. `ce_threshold` and DS field selector settings can mark more or fewer packets than intended. Stats use direct/WRITE_ONCE updates but broader qdisc locking remains the caller's responsibility.

Test signals: validate default target/interval conversions, wrap-safe time comparisons, time-to-us conversion, queue below/above target transitions, MTU suppression, ECN/CE threshold behavior, and stats updates in qdisc selftests or packetdrill/netem scenarios.
