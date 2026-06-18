# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_mqprio.h

Purpose: defines mqprio offload constants, per-port state, adapter-level state, and public mqprio lifecycle functions for cxgb4.

Important APIs/types: queue descriptor defaults for ETHOFLD software/hardware queues, RX queue interrupt defaults, `CXGB4_FLOWC_WAIT_TIMEOUT`, `enum cxgb4_mqprio_state`, `struct cxgb4_tc_port_mqprio`, `struct cxgb4_tc_mqprio`, and prototypes for setup, stop, init, and cleanup.

Control flow/state: the structures define the persistent mqprio state used by `cxgb4_tc_mqprio.c`: per-port active flag, saved `tc_mqprio_qopt_offload`, software TX queue array, TC-to-hardware-class map, plus adapter-wide refcount and mutex.

Dependencies/integration: includes `<net/pkt_sched.h>` and relies on SGE queue types from core cxgb4 headers. It is consumed by TC setup dispatch and adapter teardown.

Risks: `tc_hwtc_map` is sized with `TC_QOPT_MAX_QUEUE`; validation must keep requested TCs within that range and hardware scheduler limits. Timeout constants affect setup latency and shutdown behavior.

Test signals: compile coverage with mqprio enabled, resource allocation/free paths, and netdev queue mapping validation.
