# sources/distributed-fs/ceph-client/include/net/fq_impl.h

Purpose: provides static fair-queue implementation helpers to be embedded by includers that define their own enqueue/dequeue policy. It implements removal accounting, DRR++ tin dequeue, hash classification, collision handling, overlimit drops, and reset/filter operations.

Important APIs/functions: `__fq_adjust_removal()` updates tin, flow, global packet, and memory counters and clears bitmap/list membership when a flow drains. `fq_flow_dequeue()` pops one skb. `fq_flow_drop()` drops up to half a flow queue, capped at 32 packets. `fq_tin_dequeue()` walks new then old flows, refills deficits by `fq->quantum`, demotes new flows, and updates tx counters. `fq_flow_idx()` maps skb hash to the flow array. `fq_flow_classify()` detects cross-tin collisions and uses `tin->default_flow`. `fq_find_fattest_flow()` selects the largest backlog flow for pressure drops. `fq_tin_enqueue()` enqueues skb chains and enforces limits.

Control flow and state: all helpers assert `fq->lock`. Enqueue marks skbs off-list before queueing, increments backlog/memory, and drops fattest flows when packet or memory limits are exceeded. Dequeue loops until it finds an eligible nonempty flow or all lists drain.

Dependencies and integration: includes `fq.h`; relies on skb queue primitives, bitmaps, list management, lockdep, and caller-provided free/filter/dequeue callbacks.

Risks: counter drift is the main failure mode; every enqueue/drop/dequeue must mirror byte, packet, and truesize accounting. Default-flow collision behavior can hide unfairness. Tests should verify draining removes bitmap/list entries, overlimit/overmemory counters increment, chained skb enqueue works, filter callbacks can drop safely, and DRR deficit prevents starvation.
