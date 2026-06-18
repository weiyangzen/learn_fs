# sources/distributed-fs/ceph-client/net/sched/sch_pie.c

Purpose: implements the PIE active queue management qdisc, controlling queue delay by periodically adjusting a probabilistic early drop/mark value and optionally estimating dequeue rate.

Important APIs, types, and functions: `struct pie_sched_data` contains `pie_vars`, `pie_params`, `pie_stats`, an adaptation timer, and a backpointer to the qdisc. Exported algorithm helpers include `pie_drop_early`, `pie_process_dequeue`, and `pie_calculate_probability`. Qdisc operations are `pie_qdisc_enqueue`, `pie_qdisc_dequeue`, `pie_change`, `pie_init`, `pie_reset`, `pie_destroy`, `pie_dump`, and `pie_dump_stats`.

Control flow: enqueue first enforces `sch->limit`, then calls `pie_drop_early` using backlog and packet size. If the random decision does not drop, the skb is tail-enqueued and enqueue time is recorded when dequeue-rate estimation is disabled. If PIE would drop and ECN is enabled with probability at or below 10%, ECN-capable packets are marked and enqueued instead. Dequeue pops the head packet and calls `pie_process_dequeue`, which updates queue delay from skb timestamps or from measured drain rate and reduces burst allowance. The timer periodically calls `pie_calculate_probability` under the root qdisc lock and reschedules itself by `tupdate`.

State and persistence behavior: all state is runtime: parameters, delay variables, drop probability, accumulated probability, drain-rate samples, burst allowance, and stats counters. `pie_change` updates parameters under the tree lock and drops excess packets if the limit shrinks. `pie_reset` clears the queue and reinitializes variables; destroy stops the timer. Dumps convert psched time back to microseconds and expose stats through xstats.

Dependencies and integration points: depends on `<net/pie.h>` for common PIE math/state, qdisc queue helpers, ECN marking, timers, psched time conversion, random bytes, and netlink attributes. Exported helpers can be reused by other PIE-derived qdiscs.

Risks: timer and enqueue/dequeue paths share variables, so READ/WRITE_ONCE and locking choices matter. Probability arithmetic uses fixed-point-style scaling and must avoid overflow/underflow. Bytemode scales probability by packet size only up to MTU. Limit reduction drops queued packets synchronously. Misconfigured `tupdate`, target, or alpha/beta values can create unstable delay behavior.

Test signals: validate default init, parameter changes and dumps, limit shrink backlog reduction, ECN marking threshold, bytemode behavior for small/large packets, dequeue-rate estimator on/off paths, timer probability adjustment, burst allowance decay, reset variable reinitialization, and xstats values for drops/marks/delay/probability.
