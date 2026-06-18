# Research: sources/distributed-fs/ceph-client/net/llc/llc_sap.c

## sources/distributed-fs/ceph-client/net/llc/llc_sap.c

Purpose: Implements SAP driver routines for frame allocation, upper-layer primitive metadata, SAP state-machine processing, TEST/XID sends, datagram socket lookup, multicast delivery, and SAP PDU receive dispatch.

Important APIs/types/functions: Exports/defines `llc_alloc_frame()`, `llc_save_primitive()`, `llc_sap_rtn_pdu()`, `llc_build_and_send_test_pkt()`, `llc_build_and_send_xid_pkt()`, and `llc_sap_handler()`. Internal helpers handle SAP transition lookup/action execution, dgram unicast lookup, multicast matching, and clone fanout.

Control flow: Send helpers populate `llc_sap_state_ev` source/destination addresses and primitive fields before entering `llc_sap_state_process()`. Receive handling decodes the destination address; multicast frames are cloned to all matching datagram sockets on the device, while unicast frames look up one datagram socket by netns/local MAC/SAP. `llc_sap_state_process()` runs the transition table and queues indications to the owning socket unless it is a listener.

State and persistence behavior: It does not own global SAP state but reads/mutates SAP and socket-associated state. It assigns skb ownership with `sock_hold()` and `sock_efree`, writes `sockaddr_llc` metadata into skb control storage, and uses socket queues for delivery. Multicast fanout temporarily stores held socket pointers in a stack array.

Dependencies and integration points: Called from `llc_input.c` via SAP type handler. Uses `llc_sap_state_table`, SAP actions/events, PDU decoders, net namespace checks, SAP socket hash tables maintained by `llc_conn.c`, and Linux datagram socket receive queueing.

Risks and test signals: High-risk points are skb ownership, multicast clone failure paths, nulls-list RCU revalidation, and listener exclusion during SAP indications. Tests should cover datagram unicast, multicast to many sockets, clone allocation failure, namespace isolation, socket removal during lookup, and correctness of saved `sockaddr_llc` fields for UI/XID/TEST.
