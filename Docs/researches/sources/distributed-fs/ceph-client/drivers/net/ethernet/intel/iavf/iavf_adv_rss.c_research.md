# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_adv_rss.c

Purpose: this file implements iavf advanced RSS ethtool support. It converts driver packet-header/hash-field selections into `virtchnl_rss_cfg` protocol-header messages that can be sent to the PF, searches configured RSS rules, and logs rule status.

Important APIs/functions: exported functions are `iavf_fill_adv_rss_cfg_msg`, `iavf_find_adv_rss_cfg_by_hdrs`, and `iavf_print_adv_rss_cfg`. Internal helpers fill virtchnl headers for IPv4, IPv6, TCP, UDP, SCTP, and GTP variants. Hash-field bitmasks drive calls to `VIRTCHNL_ADD_PROTO_HDR_FIELD_BIT`; packet header bits drive `VIRTCHNL_SET_PROTO_HDR_TYPE`.

Control flow: `iavf_fill_adv_rss_cfg_msg` chooses symmetric or asymmetric Toeplitz, sets tunnel level to outer layer, appends at most one L3 header, one L4 header, and optional GTP header(s), and rejects unsupported or ambiguous L3/L4/GTP combinations. GTP handling maps GTPC/GTPU forms to the proper virtchnl protocol header type; selected GTPU forms append an IPv4 header for destination-IP hashing. Lookup iterates `adapter->adv_rss_list_head` by `packet_hdrs`. Print builds a human-readable hash option string from packet header and hash field masks.

State and persistence: RSS rule state itself lives in `struct iavf_adv_rss` nodes on the adapter list and is declared in the header. This file populates the per-rule `cfg_msg` payload and reads rule fields for lookup/logging.

Dependencies and integration: it depends on `iavf.h`, virtchnl protocol header macros, adapter advanced-RSS list state, ethtool rule creation paths, and PF support for `VIRTCHNL_VF_OFFLOAD_ADV_RSS_PF`.

Risks and test signals: risks include exceeding virtchnl header count, accepting invalid combined L3/L4 masks, mismapping GTP tunnel variants, and `hash_opt` logging truncation or stale text if future fields exceed the static buffer. Tests should cover IPv4/IPv6 TCP/UDP/SCTP combinations, symmetric/asymmetric mode, invalid mixed L3/L4 masks, each GTP variant, duplicate header lookup, and PF accept/reject completion handling.
