# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_matchall.h

Purpose: declares per-port matchall offload state and the cxgb4 TC matchall operations.

Important APIs/types: `enum cxgb4_matchall_state`, `struct cxgb4_matchall_egress_entry`, `struct cxgb4_matchall_ingress_entry`, `struct cxgb4_tc_port_matchall`, `struct cxgb4_tc_matchall`, and prototypes for replace/destroy/stats/init/cleanup.

Control flow/state: the header captures matchall persistence: egress stores hardware scheduler class and cookie; ingress stores filter TIDs and specs for `CXGB4_FILTER_TYPE_MAX`, mirror VI id, byte/packet counters, and `last_used` timestamp.

Dependencies/integration: includes `<net/pkt_cls.h>` and depends on filter specification types from cxgb4 headers. It is used by TC setup dispatch in `cxgb4_main.c` and by cleanup during adapter teardown.

Risks: structure indexes are per physical port, so callers must use the same port id for allocation and teardown. Counter fields are not individually locked here; access discipline is implemented in the `.c` file.

Test signals: compile coverage for classifier callbacks, per-port state allocation/free, and active ingress/egress offload cleanup.
