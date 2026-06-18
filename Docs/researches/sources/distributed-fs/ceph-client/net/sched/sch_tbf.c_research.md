# sources/distributed-fs/ceph-client/net/sched/sch_tbf.c

Purpose: implements the Token Bucket Filter qdisc. It shapes traffic with a main token bucket and optional peak bucket, stores packets in a child qdisc, and uses a qdisc watchdog to resume dequeue when enough tokens have accumulated.

Important APIs/types/functions: `struct tbf_sched_data` stores limit, max packet size, bucket depths, main/peak `psched_ratecfg`, token counters, time checkpoint, child qdisc, and watchdog. `psched_ns_t2l()` converts time to bytes. `tbf_enqueue()` validates size, optionally GSO-segments, and enqueues into the child. `tbf_dequeue()` peeks the head packet, replenishes tokens, dequeues only when both buckets can pay, or schedules the watchdog. `tbf_change()` parses netlink options, computes rates/bursts, creates/updates the bfifo child, swaps config under lock, and triggers offload. Class ops expose one child qdisc.

Control flow: init creates the watchdog, starts with `noop_qdisc`, requires options, records current time, and calls change. Enqueue mirrors child backlog/qlen into the root. Dequeue intentionally does not search for smaller later packets, preserving order. Reset purges child and refills buckets; destroy cancels watchdog, disables offload, and releases the child.

State and persistence: token counters, rate config, child qdisc, and watchdog are live in-memory qdisc state. Runtime change resets tokens to full bucket values and may replace the child. Hardware offload state is pushed to the driver but not persisted by this file.

Dependencies/integration: qdisc rate helpers, TBF netlink ABI, GSO helpers, fifo child qdisc helpers, watchdogs, classful grafting, qdisc stats, and `TC_SETUP_QDISC_TBF` offload hooks.

Risks: correctness depends on rate/time conversion, overhead handling, peak bucket math, and accounting during GSO segmentation. Very small burst values warn but may still create poor shaping. `limit` is effective for the default fifo child but not necessarily after grafting arbitrary child qdiscs. Offload behavior depends on driver support and stats callbacks.

Test signals: rate and peak shaping, watchdog timing, no-reordering under blocked head packet, malformed netlink, peak <= rate rejection, burst/limit changes, GSO segmentation accounting, child grafting, dump round trip with 64-bit rates, and offload replace/destroy/graft/stats.
