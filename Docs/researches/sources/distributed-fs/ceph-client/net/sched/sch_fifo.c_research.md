# sources/distributed-fs/ceph-client/net/sched/sch_fifo.c

## Purpose
`sch_fifo.c` provides the simple packet-count FIFO (`pfifo`), byte-count FIFO (`bfifo`), and packet FIFO with head-drop-on-full (`pfifo_head_drop`) qdiscs. It also exports helpers used by other schedulers to create or resize embedded FIFO children.

## Important APIs, Types, And Functions
The qdisc ops are `pfifo_qdisc_ops`, `bfifo_qdisc_ops`, and `pfifo_head_drop_qdisc_ops`. Packet paths are `pfifo_enqueue()`, `bfifo_enqueue()`, and `pfifo_tail_enqueue()`, all paired with generic head dequeue/peek. Configuration/lifecycle functions include `__fifo_init()`, `fifo_init()`, `fifo_hd_init()`, `fifo_dump()`, and `fifo_destroy()`. Exported helpers `fifo_set_limit()` and `fifo_create_dflt()` are used by classful qdiscs that embed FIFO leaves.

## Control Flow
`__fifo_init()` sets `sch->limit` from user `tc_fifo_qopt` or defaults to device `tx_queue_len` for packets and `tx_queue_len * mtu` for bytes. It toggles `TCQ_F_CAN_BYPASS` when the limit can hold at least one packet/MTU. `pfifo_enqueue()` accepts while `q.qlen < limit`; `bfifo_enqueue()` accepts while `backlog + packet_len <= limit`; otherwise both drop the incoming skb. `pfifo_tail_enqueue()` drops immediately for limit zero, appends when not full, and on a full queue drops the current head then appends the new packet, returning `NET_XMIT_CN`.

## State And Persistence
There is no private qdisc state. The limit lives in `sch->limit`, packets live in the generic qdisc queue, and stats live in generic qdisc stats. Dump emits the `tc_fifo_qopt` limit. Head-drop adjusts parent backlog with `qdisc_tree_reduce_backlog()` after replacing the head.

## Dependencies And Integration Points
The file uses generic qdisc queue helpers, netlink attributes, `psched_mtu()`, and optional hardware offload through `ndo_setup_tc(TC_SETUP_QDISC_FIFO)` for `pfifo` and `bfifo`. `pfifo_qdisc_ops` and `bfifo_qdisc_ops` are exported for other schedulers to instantiate default children. `fifo_set_limit()` deliberately detects FIFO qdiscs by ops id string shape.

## Risks
`fifo_set_limit()` uses a historical id-string heuristic and should not be generalized without care. Byte FIFO default limit depends on MTU and can surprise callers expecting packet semantics. Head-drop returns congestion notification even though the new packet is queued, so parent accounting must remain precise. Offload init/destroy/stats are absent for `pfifo_head_drop`.

## Test Signals
Test packet and byte limits at exactly full and one byte/packet over. Validate zero-limit behavior, head-drop replacement ordering, `NET_XMIT_CN` return from head drop, bypass flag toggling for small limits, dump/change round trips, `fifo_create_dflt()` failure cleanup, and offload replace/destroy/stats calls for supported FIFO variants.
