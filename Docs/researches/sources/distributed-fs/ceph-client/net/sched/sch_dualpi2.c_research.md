# sources/distributed-fs/ceph-client/net/sched/sch_dualpi2.c

## Purpose
`sch_dualpi2.c` implements DualPI2, a dual-queue AQM for L4S and classic traffic. It follows RFC 9332-style coupled dual-queue PI2 behavior: L4S packets use a low-latency queue with scalable ECN marking, classic packets use the main queue with squared probability, and both queues share a PI controller plus weighted starvation protection.

## Important APIs, Types, and Functions
`struct dualpi2_sched_data` stores the L queue, classic qdisc pointer, classifier block, PI2 parameters and hrtimer, step-AQM parameters, classic protection credit/weights, memory and ECN settings, GSO/drop policy flags, and statistics. `struct dualpi2_skb_cb` stores enqueue timestamp, step eligibility, classification result, and ECN codepoint. Classification values are `DUALPI2_C_CLASSIC`, `DUALPI2_C_L4S`, and `DUALPI2_C_LLLL`.

Important helpers include `dualpi2_read_ect()`, `dualpi2_skb_classify()`, `must_drop()`, `dualpi2_classic_marking()`, `dualpi2_scalable_marking()`, `dualpi2_mark()`, `dequeue_packet()`, `do_step_aqm()`, `calculate_probability()`, `dualpi2_timer()`, `dualpi2_calculate_c_protection()`, and alpha/beta scaling helpers. Qdisc callbacks are `dualpi2_qdisc_enqueue()`, `dualpi2_qdisc_dequeue()`, `dualpi2_change()`, `dualpi2_init()`, `dualpi2_reset()`, `dualpi2_destroy()`, `dualpi2_dump()`, and `dualpi2_dump_stats()`. Minimal class ops expose a filter block and two logical classes through `dualpi2_walk()`.

## Control Flow
Initialization marks dequeue-side drops, sets up the PI2 hrtimer, creates a default `pfifo` L queue, obtains a classifier block, installs defaults, applies optional netlink config, and starts the timer. Defaults include limit 10000, target 15 ms, update interval 16 ms, scaled alpha/beta, step threshold 1 ms, C protection weight 10 percent classic / 90 percent L queue, L4S ECN mask, coupling factor 2, dequeue-time dropping, overload dropping, and GSO splitting.

On enqueue, `dualpi2_skb_classify()` reads the packet ECN bits, classifies ECT(1)-matching packets as L4S by mask, allows `skb->priority` to choose one of the logical classes, and otherwise runs tc filters. GSO packets may be segmented; each segment inherits classification and ECN metadata before independent enqueue. `dualpi2_enqueue_skb()` enforces packet and memory limits, optionally performs early PI2 marking/dropping, stamps enqueue time, updates memory/max stats, and enqueues to either the L queue or the main classic queue. L-queue packets are counted both in the child qdisc and in the parent qdisc's aggregate qlen/backlog.

On dequeue, `dequeue_packet()` chooses L or classic queue using the sign of `c_protection_credit`, queue availability, and configured weights. It removes from the selected queue, updates head timestamps, parent/child qlen and backlog, memory usage, and returns a credit delta proportional to packet length. `dualpi2_qdisc_dequeue()` then applies dequeue-time PI2 marking/dropping if configured, applies the L-queue step AQM for eligible L4S packets, updates byte stats and protection credit on success, or defers tree backlog reduction for dropped packets until the loop completes.

The PI2 hrtimer locks the root qdisc and periodically recomputes `pi2_prob` from the max of classic and L queue head delays. The update combines integral (`alpha`) and proportional (`beta`) terms against target and previous delay, clamps probability, and optionally caps L4S probability when overload dropping is disabled.

## State and Persistence
DualPI2 keeps volatile runtime state in its private qdisc data plus the embedded main queue and separate L child queue. Per-packet qdisc control block metadata carries timestamps and classification. PI probability, queue head timestamps, memory usage, packet counters, ECN/step mark counters, deferred drop counters, and C protection credit change continuously. Reset clears queues and runtime stats while preserving configuration. Nothing is persisted outside kernel memory.

## Dependencies and Integration Points
The qdisc depends on ECN helpers, GSO segmentation, hrtimers, tc classifier blocks, default `pfifo` child queue, qdisc queue/backlog helpers, and netlink `TCA_DUALPI2_*` attributes with range validation. It integrates with tc filters through a minimal class API and with qdisc core through dequeue-side drop accounting.

## Risks
The aggregate accounting is subtle because L packets are counted in both the L child and parent aggregate; drops and dequeues must adjust both exactly once. The timer locks the root qdisc while reading queue delay state, so lock ordering must stay compatible with qdisc teardown. Probability scaling uses fixed-point 32-bit values and explicit overflow bounds; incorrect alpha/beta validation could destabilize marking. GSO splitting requires negative backlog compensation when segments replace the original skb. Early-vs-dequeue dropping changes semantics and must keep deferred drop stats paired with parent backlog reduction.

## Test Signals
Test default init/dump, each netlink parameter and validation range, L4S ECN-mask classification, priority/filter classification to all logical classes, GSO splitting on/off, packet and memory limit enforcement, early and dequeue drop modes, overload drop vs mark behavior, step threshold in packets and microseconds, non-ECT L-queue step drops, PI timer probability changes under induced delay, reset clearing both queues, and qlen/backlog consistency after deferred drops.
