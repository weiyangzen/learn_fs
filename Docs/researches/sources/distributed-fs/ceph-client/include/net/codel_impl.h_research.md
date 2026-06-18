# sources/distributed-fs/ceph-client/include/net/codel_impl.h

Read `sources/distributed-fs/ceph-client/include/net/codel_impl.h` completely for this pass (273 lines, 8799 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/codel_impl.h_research.md`.

Purpose: implements the generic CoDel algorithm as static helpers parameterized by skb callbacks, allowing multiple qdisc implementations to reuse the same controlled-delay dequeue/drop/mark logic.

Important APIs/types/functions: `codel_params_init()` sets default interval 100 ms, target 5 ms, disabled CE threshold, no selector mask, and ECN off. `codel_vars_init()` zeros runtime state. `codel_stats_init()` resets max packet. `codel_Newton_step()` updates `rec_inv_sqrt` using a fixed-point reciprocal square-root iteration. `codel_control_law()` computes next drop time. `codel_should_drop()` evaluates sojourn delay, backlog, first-above time, and packet size. `codel_dequeue()` is the main algorithm entry point.

Control flow: `codel_dequeue()` obtains a packet from the caller's dequeue callback, computes current time, and calls `codel_should_drop()`. If already dropping, it leaves dropping state when delay falls below target or loops while now has passed `drop_next`, dropping or ECN-marking packets and scheduling the next drop using the control law. If not dropping and the queue has stayed above target for an interval, it drops/marks one packet, initializes or reuses the drop count, enters dropping state, and schedules the next drop. At the end it optionally CE-marks surviving packets whose delay exceeds `ce_threshold` and whose DS field matches the selector/mask.

State and persistence: mutates caller-owned `codel_vars`, `codel_stats`, and queue backlog through callbacks. `count`, `lastcount`, `dropping`, `first_above_time`, `drop_next`, and `ldelay` persist for the lifetime of the qdisc queue/flow and directly affect future drop cadence.

Dependencies and integration points: includes `net/inet_ecn.h` for ECN marking and uses `skb_get_dsfield()` for selector matching. It is included by qdisc code rather than compiled as a standalone object, so all functions are static and caller-specific.

Risks: `backlog` must reflect bytes queued after drops/dequeues or CoDel may overdrop/underdrop. Callback contracts are strict: dequeue must return the head packet and drop must free/account it exactly once. ECN marking path skips actual drops when marking succeeds, changing stats. `codel_stats_init()` only resets `maxpacket`; callers needing zeroed drop counters must clear the structure first. Fixed-point reciprocal square-root logic is sensitive to count initialization.

Test signals: qdisc tests with sustained queue delay, delay recovery, ECN-enabled and ECN-disabled flows, large backlog requiring multiple drops in one dequeue call, DS-field-gated CE threshold, drop count reuse after quick re-entry, empty queue resets, and callback accounting consistency.
