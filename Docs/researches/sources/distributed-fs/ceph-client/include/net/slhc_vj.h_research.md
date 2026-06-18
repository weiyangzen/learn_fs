# sources/distributed-fs/ceph-client/include/net/slhc_vj.h

## Purpose
This legacy header defines Van Jacobson TCP/IP header compression state and APIs for SLIP/PPP-style low-bandwidth links.

## Important APIs, Types, And Functions
Constants define compressed packet types (`SL_TYPE_IP`, `SL_TYPE_UNCOMPRESSED_TCP`, `SL_TYPE_COMPRESSED_TCP`), changed-field flags (`NEW_C`, `NEW_I`, `NEW_S`, `NEW_A`, `NEW_W`, `NEW_U`), special cases, and push-bit handling. `struct cstate` stores per-conversation cached IP/TCP headers, options, header size, connection id, and ring linkage. `struct slcompress` stores transmit/receive state arrays, slot limits, current/oldest ids, toss flag, and detailed in/out counters. APIs are `slhc_init()`, `slhc_free()`, `slhc_compress()`, `slhc_uncompress()`, `slhc_remember()`, and `slhc_toss()`.

## Control Flow
Transmit compression searches cached connection state, emits compressed or uncompressed TCP packets, and updates counters. Receive decompression uses the connection id to reconstruct full headers; on errors it enters toss mode until an uncompressed packet resynchronizes state.

## State And Persistence
Compression state persists per serial link in `struct slcompress`, with cached headers per slot and counters useful for diagnostics.

## Dependencies And Integration Points
It depends on IPv4 and TCP header structs and is integrated by SLIP/PPP compression implementations rather than mainstream Ethernet paths.

## Risks And Test Signals
Risks include stale header reconstruction, option buffer bounds, slot-id desynchronization, endian/sequence delta mistakes, and toss-mode recovery failures. Test signals are compressed/uncompressed TCP round trips, packet loss resync, option-bearing TCP headers, slot-limit edge cases, and counter accuracy.
