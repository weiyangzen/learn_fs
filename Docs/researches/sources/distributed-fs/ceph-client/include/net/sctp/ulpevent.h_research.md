# sources/distributed-fs/ceph-client/include/net/sctp/ulpevent.h

## Purpose
This header defines `sctp_ulpevent`, the compact event object stored in `skb->cb` to deliver SCTP data and notifications from the state machine to the socket upper layer.

## Important APIs, Types, And Functions
`struct sctp_ulpevent` carries association, chunk, receive-memory length, stream sequence or message id, PPID or FSN, TSN, cumulative TSN, stream, flags, and message flags. Helpers convert between event and skb. Factory APIs create association-change, peer-address-change, remote-error, send-failed, shutdown, partial-delivery, adaptation, receive-message, auth-key, sender-dry, stream-reset, association-reset, stream-change, and reassembled-message events. Reader APIs fill `sndrcvinfo`, `rcvinfo`, and `nxtinfo`; subscription helpers set and test notification bits.

## Control Flow
SCTP receive/reassembly builds data events, state-machine side effects build notifications, and ULP queue/socket receive paths deliver only notifications enabled by the socket subscription mask.

## State And Persistence
Events live inside skb control buffers and carry receive-memory accounting length for socket ownership. Subscription masks persist in socket/association state.

## Dependencies And Integration Points
It integrates with `sk_buff`, SCTP chunks/associations/transports, socket ancillary data, notification UAPI structs, and `sctp_ulpq`.

## Risks And Test Signals
Risks include `skb->cb` size overflow, packed-layout assumptions, stale association pointers, notification filtering bugs, and receive-memory accounting mismatch. Test signals include all SCTP notification socket options, fragmented reassembly events, send failure, auth key notifications, stream reset/change, and partial delivery API events.
