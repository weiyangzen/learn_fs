# sources/distributed-fs/ceph-client/net/core/gen_estimator.c

Purpose: Implements the generic rate estimator used by networking subsystems to derive smoothed packet-per-second and byte-per-second rates from basic counters. It is designed for controlled load service style estimation, not as a primary statistics collection mechanism.

Important APIs, types, and functions: `struct net_rate_estimator` stores source counter pointers, optional stats lock, per-cpu counter pointer, EWMA parameters, seqcount-protected samples, last byte/packet totals, timer state, and RCU head. Public APIs are `gen_new_estimator()`, `gen_kill_estimator()`, `gen_replace_estimator()`, `gen_estimator_active()`, and `gen_estimator_read()`. `est_fetch_counters()` snapshots `gnet_stats_basic_sync`; `est_timer()` updates EWMA values and reschedules itself.

Control flow: `gen_new_estimator()` validates netlink `gnet_estimator` options, allowing interval values from -2 through 3 and `ewma_log` from 1 through 30. It allocates state, initializes seqcount and source pointers, snapshots current counters, replaces any existing estimator under the optional lock, preserves old average rates, schedules the first timer tick, RCU-publishes the new pointer, and RCU-frees the old estimator after deleting its timer. Timer callbacks fetch counters, compute deltas scaled by interval, apply EWMA decay, publish `avbps` and `avpps` under seqcount with preemption disabled, advance `next_jiffies`, compensate delayed timers, and re-arm. `gen_kill_estimator()` atomically clears the RCU pointer, synchronously shuts down the timer, and frees by RCU. Reads use RCU plus seqcount retry.

State and persistence: Estimator state is dynamically allocated and referenced through an RCU pointer owned by the caller. It persists only while the owning qdisc/class/object keeps the pointer. Samples are in fixed-point form internally and right-shifted by 8 when exported.

Dependencies and integration points: Relies on `gen_stats.c` basic counter helpers, u64 stats synchronization, timers, jiffies, RCU, netlink estimator attributes, and optional caller spinlocks. `gnet_stats_copy_rate_est()` consumes `gen_estimator_read()` output.

Risks: Incorrect locking around caller counters can produce inconsistent rates. Timer replacement must avoid use-after-free and preserve existing estimates. Invalid EWMA/interval options must be rejected to avoid shifts outside supported range. Delayed timers can cause bursts or stale rates; the code clamps next scheduling when behind.

Test signals: Create, replace, read, and kill estimators for global and per-cpu counters. Validate option rejection for short attributes, interval out of range, and bad `ewma_log`. Use rapidly changing counters and delayed timer conditions to confirm monotonic timer rescheduling, seqcount-consistent reads, and no timer firing after `gen_kill_estimator()`.
