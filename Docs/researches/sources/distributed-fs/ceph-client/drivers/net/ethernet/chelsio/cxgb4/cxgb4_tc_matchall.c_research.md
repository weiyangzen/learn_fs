# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_matchall.c

Purpose: offloads TC matchall rules for cxgb4, supporting egress policing through scheduler classes and ingress mirror/redirect/filter actions through hardware filters.

Important APIs/functions: `cxgb4_tc_matchall_replace`, `cxgb4_tc_matchall_destroy`, `cxgb4_tc_matchall_stats`, `cxgb4_init_tc_matchall`, and `cxgb4_cleanup_tc_matchall`; internal helpers validate policers, allocate/free scheduler traffic classes, bind/unbind queues, allocate mirror VI state, and add/delete per-family ingress filters.

Control flow: egress replace validates a single police action, link speed limits, non-shared blocks, and queue class conflicts, then allocates a channel rate-limit scheduler class and binds every Ethernet TX queue. Ingress replace validates shared flow actions, optionally allocates a mirror VI, installs IPv4 and IPv6 matchall filters, and marks state enabled. Destroy checks cookies before freeing either scheduler state or ingress filters. Stats aggregate counters from all ingress filter types.

State and persistence: per-port state lives in `adap->tc_matchall->port_matchall[port]`, split into egress class/cookie/state and ingress filter ids/specs/mirror/counters. Hardware state includes scheduler classes, queue bindings, mirror VI allocation, and filter entries.

Dependencies/integration: uses shared scheduler APIs from `sched.c`, filter APIs from `cxgb4_uld.h`/`cxgb4_filter`, flow action validation from `cxgb4_tc_flower.c`, and TC classifier callbacks from `cxgb4_main.c`.

Risks: only one ingress and one egress matchall can be active per port. Cleanup calls hardware delete/free routines and may encounter partial failures. Egress policing uses bytes-per-second to Kbps conversion and must respect link speed. Shared TC blocks are rejected.

Test signals: TC matchall ingress mirror/drop/redirect, egress police at/beyond link rate, duplicate rule rejection, cookie mismatch destroy, shared-block rejection, queue bind conflict with mqprio/scheduler users, and driver removal with active offloads.
