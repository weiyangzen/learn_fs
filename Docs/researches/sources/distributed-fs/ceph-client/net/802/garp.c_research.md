<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/garp.c -->
# sources/distributed-fs/ceph-client/net/802/garp.c

This file implements the IEEE 802.1D Generic Attribute Registration Protocol applicant. It is used by VLAN GVRP to advertise and withdraw VLAN attributes over the bridge-group LLC SAP through the STP demux.

The core state is per-device `struct garp_port` published through `dev->garp_port`, per-application `struct garp_applicant`, and per-attribute `struct garp_attr` nodes stored in an rbtree keyed by type/length/data. The large `garp_applicant_state_table` drives applicant state transitions and transmit actions. Public APIs are `garp_request_join()`, `garp_request_leave()`, `garp_init_applicant()`, `garp_uninit_applicant()`, `garp_register_application()`, and `garp_unregister_application()`.

Control flow starts with application registration through `stp_proto_register()`. Applicant initialization creates the port/applicant, joins the multicast group, arms a randomized join timer, and publishes the applicant with RCU. Join/leave requests create or look up attributes and feed request events into the state table. The join timer emits pending PDUs, appends end marks and LLC headers, queues skbs, and transmits them. Receive flow enters through `garp_pdu_rcv()`, validates protocol id, parses messages/attributes/end marks, and applies remote events under the applicant lock.

Persistence is in memory only. Synchronization uses RTNL for lifecycle, RCU for device pointers, spinlocks for applicant state, timers, and skb queues. Risks include malformed PDU parsing, timer/lifecycle races, rbtree mutation during iteration, allocation failures while building PDUs, and a suspicious `dlen = sizeof(*ga) - ga->len` calculation that appears inverted and should be validated against the intended attribute-data length. Tests should cover GVRP join/leave, timer retransmission, final leave on uninit, malformed PDUs, concurrent device unregister, and multicast membership cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/garp.c -->
