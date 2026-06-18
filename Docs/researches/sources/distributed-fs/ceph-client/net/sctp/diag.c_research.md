# sources/distributed-fs/ceph-client/net/sctp/diag.c

Purpose: implements SCTP support for inet `SOCK_DIAG`, allowing netlink dumps of listening endpoints and associations with addresses, timers, memory, and SCTP info.

Important APIs/types/functions: `inet_diag_msg_sctpasoc_fill()` fills identity/state/timer fields from an association. `inet_diag_msg_sctpladdrs_fill()` and `inet_diag_msg_sctpaddrs_fill()` serialize local and peer address arrays. `inet_sctp_diag_fill()` builds one endpoint or association netlink record. `sctp_sock_dump_one()`, `sctp_sock_dump()`, `sctp_sock_filter()`, and `sctp_ep_dump()` implement exact and table traversal callbacks. `sctp_diag_dump_one()` and `sctp_diag_dump()` are inet diag entry points. `sctp_diag_handler` registers the SCTP diag protocol handler.

Control flow: module init registers with inet diag. Dump requests optionally traverse endpoints for listening sockets, then traverse transport hashes for associations unless only listen states are requested. Exact lookup constructs local/peer addresses and calls SCTP transport lookup. Fill paths lock sockets where required, check cookies, verify association membership, and serialize netlink attributes.

State and persistence: no protocol state is owned. The file reads socket/endpoint/association state and uses `netlink_callback` args as dump cursors across multipart responses. Module registration persists while loaded.

Dependencies/integration: inet diag core, sock diag cookies, netlink attributes, SCTP endpoint/transport traversal, `sctp_get_sctp_info()`, socket memory accounting, network namespaces, `CAP_NET_ADMIN`, and module aliasing for sock diag autoload.

Risks: cursor fields in `cb->args[]` are subtle and can skip/duplicate records. Association membership must be rechecked after locking due to migration/peeloff. Address list count and copy happen under separate RCU sections and can hit `-EMSGSIZE`. Association fill assumes primary path and at least one local address.

Test signals: `ss`/diag dumps for listeners and multi-association sockets, exact lookup, IPv4/IPv6, local/peer address attributes, skmem and SCTP info, cookie mismatch, namespace and capability filtering, state/port/family filters, multipart continuation, peeloff during dump, and module unregister.
