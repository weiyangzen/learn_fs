# sources/distributed-fs/ceph-client/net/sched/sch_red.c

Purpose: implements Random Early Detection as a classful wrapper around one child qdisc, with optional ECN marking, harddrop/nodrop flags, adaptive RED timer, qevents for mark/early-drop, and hardware offload support.

Important APIs, types, and functions: `struct red_sched_data` stores limit, flags/userbits, adaptive timer, child qdisc, RED parameters/variables/stats, and qevents. Main routines are `red_enqueue`, `red_dequeue`, `__red_change`, `red_change`, `red_init`, `red_destroy`, `red_offload`, `red_adaptative_timer`, dump/stat helpers, and class graft/leaf/find operations.

Control flow: enqueue updates average queue length with `red_calc_qavg`, ends idle periods, asks `red_action` whether to pass, probabilistically mark/drop, or hard mark/drop. ECN-capable packets may be marked and sent through the mark qevent; non-ECT packets may still be queued in nodrop mode. Congestion drops can run the early-drop qevent before final drop. Accepted packets enqueue into the child and update root backlog/qlen; child drops increment `pdrop`. Dequeue pulls from the child, updates root stats, and starts an idle period when empty.

State and persistence behavior: RED state includes EWMA variables, idle tracking, stats counters, qevents, child qdisc, and optional adaptive timer. `__red_change` can create a new bfifo child, swap it under the tree lock, reset RED parameters/variables, and start/stop the adaptive timer. Destroy deletes qevents, timer, offload state, and child qdisc. Dumps reconstruct RED options and flags, not packet queue contents.

Dependencies and integration points: uses `<net/red.h>` algorithms, ECN helpers, qevent APIs, child qdisc grafting, netlink bitfield policy, qdisc offload helpers, and `ndo_setup_tc(TC_SETUP_QDISC_RED)`.

Risks: flag compatibility is split between historic `tc_red_qopt.flags` bits and new bitfield attributes; validation must keep combinations legal. Adaptive timer runs under root lock and must be canceled on destroy/change. Qevent handlers can consume the skb. Offload stats require driver support and the qdisc sets `TCQ_F_OFFLOADED` elsewhere based on core behavior. Child replacement purges old queues.

Test signals: validate required parms/stab, flag combinations including ECN/harddrop/nodrop, probabilistic and forced mark/drop counters, qevent mark/drop handling, adaptive timer operation, idle period behavior, child graft and dump class, offload replace/destroy/graft/stats, and netlink dump round trips.
