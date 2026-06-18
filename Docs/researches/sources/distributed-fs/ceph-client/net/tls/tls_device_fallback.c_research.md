# sources/distributed-fs/ceph-client/net/tls/tls_device_fallback.c

## Purpose
Provides the software encryption fallback for kTLS TX device offload. It encrypts outgoing skbs when they are transmitted through a device that is not the offload device, after offload is degraded, or through explicit fallback helpers.

## Important APIs, Types, And Functions
The exported/public functions are `tls_validate_xmit_skb`, `tls_validate_xmit_skb_sw`, `tls_encrypt_skb`, and `tls_sw_fallback_init`. Internal helpers allocate AEAD requests, encrypt one or more records across scatterwalks, update TCP checksums, clone/complete replacement skbs, build input and output scatterlists, and perform the fallback transformation.

## Control Flow And State
Fallback initialization validates an offloadable cipher, allocates an async AEAD transform, sets the key, and configures authentication tag size. During xmit validation, packets sent through the original offload device or a bond master pass through unchanged; others enter `tls_sw_fallback`. The fallback locates the TLS record covering the skb TCP sequence via `tls_get_record`, accounts for any sync data before the packet payload, builds scatterlists from saved record frags plus the skb payload, allocates a replacement skb, encrypts records with AEAD using reconstructed IV/AAD/record sequence, copies headers, adjusts ownership and checksum state, releases temporary fragment references, and consumes or frees the original skb.

## Dependencies And Integration Points
Depends on `tls_device.c` record tracking, cipher descriptors and AAD helpers from `tls.h`, Linux crypto AEAD, scatterwalk, skb fragment reference helpers, TCP/IP checksum helpers, xmit validation hooks, and public `net/tls.h` context accessors.

## Risks And Test Signals
Risks include incorrect record lookup after ACK cleanup, sync-size edge cases for packets before offload start, scatterlist sizing with fragmented records and skbs, checksum ownership accounting, async crypto failure, partial record handling where auth tags are intentionally discarded from output, and route changes causing frequent fallback. Test signals include retransmits through non-offload devices, device down after TX offload, packets before the start marker, fragmented sendfile records, IPv4 and IPv6 checksum validation, AEAD setup failures, and comparing fallback ciphertext with normal software kTLS output.
