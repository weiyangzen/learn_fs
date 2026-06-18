# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_tc_flower.h

Purpose: defines the data structures and public interface for cxgb4 TC flower and generic flow-rule offload.

Important APIs/types: `struct ch_tc_flower_stats`, `struct ch_tc_flower_entry`, pedit field identifiers and offsets, `enum cxgb4_action_natmode_flags`, `struct cxgb4_natmode_config`, and prototypes for flow action processing/validation, TC flower replace/destroy/stats, lower-level flow rule replace/destroy, and init/cleanup.

Control flow/state: the header encodes the shape of per-rule persistent state: hardware filter spec, stats, cookie key, rhashtable node, RCU head, stats lock, and filter id. Pedit macros map TC mangle offsets into `struct ch_filter_specification` fields.

Dependencies/integration: includes `<net/pkt_cls.h>` and requires `struct ch_filter_specification` from cxgb4 filter definitions. It is shared by flower code and matchall ingress code, which reuses flow action validation and processing.

Risks: pedit offsets and sizes must stay synchronized with hardware filter-spec layout. Adding actions or fields requires updating both validation and processing paths or invalid offloads may be accepted.

Test signals: build tests after filter-spec layout changes, TC flower pedit/NAT regression tests, and matchall ingress tests that rely on the shared action parser.
