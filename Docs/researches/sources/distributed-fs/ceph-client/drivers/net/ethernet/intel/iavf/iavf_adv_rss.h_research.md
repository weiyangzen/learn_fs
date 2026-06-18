# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_adv_rss.h

Purpose: this header defines the iavf advanced RSS rule model, packet header masks, hash-field masks, and exported helper prototypes.

Important APIs/types: it defines `enum iavf_adv_rss_state_t` for add/delete request, pending, and active states; `enum iavf_adv_rss_flow_seg_hdr` for IPv4/IPv6, TCP/UDP/SCTP, and GTP control/user-plane variants; grouped masks for L3, L4, and GTP headers; `enum iavf_adv_rss_flow_field` and corresponding 64-bit hash-field masks; and `struct iavf_adv_rss` containing list linkage, packet headers, hash fields, symmetric flag, state, and the prepared `virtchnl_rss_cfg` message.

Control flow and state: ethtool paths allocate/update `struct iavf_adv_rss`, set state to request/pending/active as PF messages are sent and completed, and use the helper functions to build and find rules. The field enum explicitly notes that it must fit within 64 bits because hash masks are `u64`.

Dependencies and integration: the header forward-declares `struct iavf_adapter` and relies on virtchnl RSS configuration types through including contexts. It is included by `iavf.h`, making advanced RSS state part of the adapter.

Risks and test signals: adding fields beyond 64 bits would break mask representation. Header bit combinations must stay aligned with `iavf_adv_rss.c` parsing and PF virtchnl expectations. Tests should cover add/delete state transitions, duplicate packet header detection, mask construction, and compile coverage for all exported helpers.
