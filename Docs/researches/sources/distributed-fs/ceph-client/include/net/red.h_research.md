# sources/distributed-fs/ceph-client/include/net/red.h

Purpose: implements inline Random Early Detection and adaptive RED fixed-point arithmetic, parameters, variables, stats, validation, and action selection helpers for RED/GRED qdiscs.

Important APIs and types: `struct red_parms` stores thresholds, scaling, max probability, reciprocal, adaptive targets, and idle decay table. `struct red_vars` stores qcount, random cache, average queue length, and idle timestamp. `struct red_stats` tracks probability/forced drops/marks and queue-limit drops. Helpers validate parameters/flags, set parameters, reset/restart vars, model idle decay, calculate queue average, choose random thresholds, compare thresholds, decide mark/drop action, and run adaptive probability updates.

Control flow: enqueue paths update `qavg`, call `red_action()` to return no mark/probability mark/hard mark, and optionally adapt `max_P` on timer intervals. Idle periods decay queue average using `Stab`.

State and persistence: qdisc-local RED parameters, variables, and stats only.

Dependencies and integration points: depends on qdisc time helpers, ECN/dsfield helpers, random numbers, reciprocal division, netlink extack, and RED/GRED UAPI flags.

Risks and test signals: risks include fixed-point overflow, invalid threshold/scale values, nodrop without ECN, stale reciprocal after adaptive updates, and idle decay approximation errors. Test parameter validation, ECN/nodrop/harddrop flags, below/between/above thresholds, adaptive RED, idle queue decay, random probability distribution, and GRED multi-DP stats.
