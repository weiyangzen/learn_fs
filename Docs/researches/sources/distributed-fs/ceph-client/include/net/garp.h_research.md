# sources/distributed-fs/ceph-client/include/net/garp.h

Purpose: declares Generic Attribute Registration Protocol support, used by applications such as GVRP over STP-like link-layer control. It models GARP PDUs, applicant state machines, per-device applicants, and application registration.

Important APIs/types: wire structs include `garp_pdu_hdr`, `garp_msg_hdr`, and variable-length `garp_attr_hdr`. `enum garp_attr_event`, `enum garp_applicant_state`, `enum garp_event`, and `enum garp_action` encode the registration state machine. `struct garp_attr` stores registered attributes in an rb-tree. `struct garp_application` wraps an STP protocol descriptor. `struct garp_applicant` holds the app, device, join timer, spinlock, skb queue, pending PDU, GID tree, and RCU hook. Public APIs register/unregister applications, initialize/uninitialize applicants on devices, and request join/leave for an attribute.

Control flow and state: join/leave requests enqueue state-machine work for a device applicant. Attributes persist in memory under the applicant lock and are reclaimed by RCU. Timers drive join transmission; skb control block storage is accessed through `garp_cb()`.

Dependencies and integration: depends on Ethernet types, `net/stp.h`, net devices, timers, rbtrees, RCU, and skb queues. It integrates with bridge/VLAN registration protocols.

Risks: variable-length attributes and skb control-block reuse require strict bounds. State-machine transitions must be covered for every event/action pair. Tests should include duplicate joins, leaves of absent attributes, timer-driven PDU generation, application unregister while applicants exist, RCU lifetime, and malformed PDU parsing.
