# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_mqprio.c

Purpose: implements TC mqprio full hardware offload for cxgb4 by allocating scheduler classes, ETHOFLD hardware queues, ETHOFLD software queues, and EOTID-backed flow contexts per traffic class.

Important APIs/functions: `cxgb4_setup_tc_mqprio`, `cxgb4_mqprio_stop_offload`, `cxgb4_init_tc_mqprio`, and `cxgb4_cleanup_tc_mqprio`; internal helpers validate mqprio settings, allocate/free ETHOFLD resources, create/free scheduler classes, initialize/free software queues, and bind/unbind flow contexts.

Control flow: setup validates full TC hardware offload, channel mode, bandwidth shaper, non-overlapping queue ranges, rate totals, and EOTID capacity. It stops queues/carrier if the interface is running, disables existing offload, allocates scheduler classes, creates ETHOFLD queues/EOTIDs, binds flow contexts, updates netdev TC queue maps, and restores carrier. Clear requests disable existing offload only.

State and persistence: adapter-wide `tc_mqprio` holds a refcount and mutex; per-port state stores current mqprio parameters, `sge_eosw_txq` array, hardware scheduler class map, and active/disabled state. Hardware state includes RX/TX ETHOFLD queues, IRQ/MSI-X allocation, scheduler classes, and flowc bindings.

Dependencies/integration: depends on Linux mqprio offload API, netdev TC queue APIs, cxgb4 SGE allocation/free helpers, EOTID helpers in `cxgb4_uld.h`, scheduler APIs in `sched.c`, and ETHOFLD completion handlers.

Risks: setup is invasive: queue counts and carrier state change while resources are rebuilt. Error unwinds must unbind flow contexts, free EOTIDs, kill tasklets, release MSI-X indices, and reset netdev TC state. `cxgb4_get_free_eotid`/bitmap updates are inline and need external serialization from the mqprio mutex.

Test signals: mqprio enable/disable while interface is up and down, overlapping queue rejection, rate sum rejection, EOTID exhaustion, IRQ allocation failure unwind, flowc completion timeout, device shutdown path that skips waits, and concurrent per-port mqprio operations.
