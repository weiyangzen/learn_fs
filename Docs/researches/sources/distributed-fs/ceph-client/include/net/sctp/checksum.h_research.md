# sources/distributed-fs/ceph-client/include/net/sctp/checksum.h

## Purpose
This header provides the inline SCTP CRC32c checksum computation for packets held in `sk_buff`.

## Important APIs, Types, And Functions
`sctp_compute_cksum(const struct sk_buff *skb, unsigned int offset)` locates the SCTP header at `skb->data + offset`, saves and clears the checksum field, computes CRC32c over the SCTP packet bytes, restores the old field, and returns the little-endian checksum.

## Control Flow
Transmit and receive validation paths call the helper with the transport offset. The helper mutates the checksum field only temporarily so callers can operate on packet data in place.

## State And Persistence
No persistent state is held. The observable packet checksum field is restored before returning.

## Dependencies And Integration Points
It depends on `struct sctphdr`, `sk_buff`, `skb_crc32c()`, and endian conversion. It is used by SCTP input validation and output checksum filling unless checksum disable paths bypass it.

## Risks And Test Signals
Risks include invalid offsets, non-linear skb handling assumptions delegated to `skb_crc32c()`, and concurrent modification of shared skb data. Test signals are SCTP checksum receive rejection, transmit checksum verification, UDP-encapsulated SCTP offsets, and checksum-disable configuration tests.
