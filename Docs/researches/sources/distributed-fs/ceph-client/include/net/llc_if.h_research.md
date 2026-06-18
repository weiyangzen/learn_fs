# Research: sources/distributed-fs/ceph-client/include/net/llc_if.h

Purpose: `llc_if.h` defines the LLC interface exposed to the network-layer side of the LLC implementation. It names service primitives, primitive types, status/reason codes, and declares high-level connection/data/disconnect helpers.

Important APIs/types/functions: primitive constants include `LLC_DATAUNIT_PRIM`, `CONN_PRIM`, `DATA_PRIM`, `DISC_PRIM`, `RESET_PRIM`, `FLOWCONTROL_PRIM`, `DISABLE_PRIM`, `XID_PRIM`, `TEST_PRIM`, `SAP_ACTIVATION`, and `SAP_DEACTIVATION`. Primitive types are request, indication, response, and confirmation. Reason/status constants cover reset origin, disconnect due to DM/DISC/ACK timeout, and connection/data statuses such as connected, disconnected, failed, impossible, received, remote busy, refuse, conflict, and reset done. APIs are `llc_establish_connection()`, `llc_build_and_send_pkt()`, and `llc_send_disc()`.

Control flow: upper layers request connection establishment, data send, or disconnect using these primitives and helper functions. The LLC connection and SAP state machines encode primitive and primitive-type values into skb event metadata, execute transitions, and later report indications/confirmations back to sockets.

State and persistence behavior: the header itself has no state. It defines values stored transiently in event structures and persistently reflected in `llc_sock` connection state and socket queues.

Dependencies and integration points: it includes Linux LLC UAPI, ARP/etherdevice helpers, `net/llc.h`, and network interface definitions. It bridges AF_LLC socket operations with the internal SAP/connection state machines.

Risks: primitive/status numeric contracts must remain consistent with state table code and users of `skb->cb` event fields. Unsupported flow-control primitive is declared but noted unsupported, so callers must not assume full flow-control behavior.

Test signals: check connect/data/disconnect socket operations, status propagation to users, reset/disconnect reason reporting, unsupported flow-control handling, and packet send failures through `llc_build_and_send_pkt()`.
