# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/sched.c

Purpose: manages per-port hardware scheduling classes and binds either Ethernet queues or ETHOFLD flow contexts to those classes.

Important APIs/functions: `cxgb4_sched_queue_lookup`, `cxgb4_sched_class_bind`, `cxgb4_sched_class_unbind`, `cxgb4_sched_class_alloc`, `cxgb4_sched_class_free`, `t4_init_sched`, and `t4_cleanup_sched`; internal helpers issue firmware scheduler commands, bind/unbind queue or flowc entries, look up existing bindings, and unbind all users of a class.

Control flow: class allocation optionally reuses an existing FLOW-mode class with matching params, otherwise finds an unused class, programs firmware with `t4_sched_params`, and marks it active. Binding unbinds any previous class for the queue/flowc, sends firmware params or flowc work request, records the binding in the class list, and increments refcount. Unbind sends firmware reset, removes list entry, and frees the class if refcount reaches zero. Free resets class rates to link max or 100 Gbps fallback.

State and persistence: each port owns a `sched_table` with flexible array of `ch_sched_class` records, each containing class index, params, binding type, entry list, state, and atomic refcount. Hardware scheduler state persists until reset by free/cleanup.

Dependencies/integration: uses firmware `t4_sched_params` and `t4_set_params`, ETHOFLD `cxgb4_ethofld_send_flowc`, netdev port info, and link speed query. Matchall and mqprio are primary consumers.

Risks: `t4_sched_class_unbind_all` iterates lists while unbind deletes entries, which requires careful list traversal assumptions. Class reuse is limited to flow mode; queue mode always consumes a new class. `cxgb4_sched_class_free` indexes by classid without its own range check, relying on callers.

Test signals: scheduler class allocation/reuse/free, queue binding conflicts, flowc bind/unbind completion paths, link speed query failure fallback, cleanup with active bindings, and invalid class/queue/tid inputs.
