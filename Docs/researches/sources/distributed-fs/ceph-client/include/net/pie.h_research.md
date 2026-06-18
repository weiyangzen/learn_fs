# sources/distributed-fs/ceph-client/include/net/pie.h

Purpose: declares Proportional Integral controller Enhanced active queue management parameters, variables, stats, skb private control block, and algorithm entry points for PIE qdiscs.

Important APIs and types: `struct pie_params` stores target delay, update interval, queue limit, alpha/beta controls, ECN, bytemode, and delay-rate estimator flags. `struct pie_vars` stores current/old delay, burst allowance, dequeue timestamp/count, average dequeue rate, backlog, and drop probability. `struct pie_stats` tracks enqueue/drop/mark/limit stats. `struct pie_skb_cb` stores enqueue time and memory usage. Inline initializers set defaults; helpers validate and access qdisc skb private data. Core functions are `pie_drop_early()`, `pie_process_dequeue()`, and `pie_calculate_probability()`.

Control flow: enqueue records timestamp and may drop/mark early based on probability; dequeue updates rate/delay state; periodic update recalculates drop probability from queue delay trends.

State and persistence: qdisc-local runtime variables and stats only.

Dependencies and integration points: depends on qdisc timing, ECN helpers, skbuff control blocks, and packet scheduler core.

Risks and test signals: risks include qdisc CB size conflicts, fixed-point probability overflow, stale dequeue rate, ECN/bytemode interaction, and wrong time unit conversion. Test default parameters, ECN marking, bytemode, burst allowance, delay estimator mode, queue limit drops, and high-rate/idle transitions.
