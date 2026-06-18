# sources/distributed-fs/ceph-client/include/linux/rcu_segcblist.h

Purpose: defines simple and segmented RCU callback-list structures used by RCU and TREE SRCU to track callbacks across grace-period phases and optional no-CB CPU offloading.

Important APIs and types: `struct rcu_cblist` is a simple head/tail/length callback list with `RCU_CBLIST_INITIALIZER`. Segment indexes `RCU_DONE_TAIL`, `RCU_WAIT_TAIL`, `RCU_NEXT_READY_TAIL`, and `RCU_NEXT_TAIL` split callbacks into done, waiting for current GP, ready for next GP, and unassigned next callbacks. `struct rcu_segcblist` stores head, segment tails, per-segment grace-period sequence numbers, total length, per-segment lengths, and flags. Flags include `SEGCBLIST_ENABLED` and `SEGCBLIST_OFFLOADED`. `RCU_SEGCBLIST_INITIALIZER` initializes all tails to the head.

Control flow: callbacks enter the next segment, are assigned grace-period sequence numbers, advance through wait/ready/done segments as GPs complete, and are invoked when in the done segment. NOCB offloading state transitions move callback processing between local `rcu_core()` and offloaded callback/GP kthreads while preserving locking and bypass semantics.

State and persistence: state is in-memory callback queues and GP sequence metadata. With `CONFIG_RCU_NOCB_CPU`, length is atomic for offloaded coordination.

Dependencies and integration points: depends on `rcu_head`, atomics, RCU NOCB config, and SRCU sizing requirements. It integrates RCU callback queuing, grace-period accounting, and no-CB CPU offload.

Risks and test signals: risks include corrupt tail pointers, wrong segment advancement, GP sequence misassignment, length/seglen divergence, offload/deoffload state-machine races, and callbacks invoked too early or stranded. Test RCU torture, callback flood, NOCB offload/deoffload, CPU hotplug, expedited and normal grace periods, and debug validation of segment lengths.
