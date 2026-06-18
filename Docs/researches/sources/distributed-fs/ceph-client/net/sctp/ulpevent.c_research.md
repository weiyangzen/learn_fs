# sources/distributed-fs/ceph-client/net/sctp/ulpevent.c

## Purpose
Creates, owns, accounts, and frees skb-backed SCTP ULP events delivered to sockets. It covers notifications, received DATA messages, ancillary receive info, association ownership, receive-window accounting, and event queue purging.

## Important APIs, Types, And Functions
Important exported constructors include `sctp_ulpevent_make_assoc_change`, `sctp_ulpevent_make_remote_error`, send-failed variants, shutdown/adaptation/auth/sender-dry events, stream reset/change/association reset events, `sctp_ulpevent_make_rcvmsg`, and `sctp_ulpevent_make_pdapi`. Other APIs include `sctp_ulpevent_notify_peer_addr_change`, read helpers for `SCTP_SNDRCV`, `SCTP_RCVINFO`, `SCTP_NXTINFO`, `sctp_ulpevent_free`, and `sctp_queue_purge_ulpevents`.

## Control Flow
Notification constructors allocate or clone skbs, prepend the notification struct, fill RFC-defined fields, hold the association, and set association ids. Receive-message construction checks socket or association rmem policy, schedules receive memory, clones the chunk skb, marks the TSN map, trims padding, holds the source chunk, charges rwnd recursively across fragments, and records stream/TSN flags. Read helpers emit cmsgs for application recvmsg. Free paths distinguish notifications from data: notifications drop owner refs, data increases rwnd, puts held chunks recursively, releases owner refs, then frees skbs.

## State And Persistence
Events are transient skb control-block objects. They hold association references and data receive memory accounting until delivered or purged; there is no durable state.

## Dependencies And Integration Points
Integrates with socket receive queues, SCTP association refcount/rwnd accounting, TSN map marking, chunk references, address-family user address conversion, ULP queue delivery, and RFC6458 ancillary data.

## Risks
High-risk areas are skb clone/copy length calculations, failing to undo memory admission on later failures, recursive fragment owner accounting, releasing chunk references exactly once, and filtering disabled notifications after allocation.

## Test Signals
Exercise each notification constructor, receive data with padding and skb fragments, memory-pressure failure before and after TSN marking, ancillary cmsg output, disabled subscription filtering through ULP queue paths, and purge/free accounting for mixed notification/data queues.
