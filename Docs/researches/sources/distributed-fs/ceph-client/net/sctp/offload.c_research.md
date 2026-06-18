# sources/distributed-fs/ceph-client/net/sctp/offload.c

## Purpose
`offload.c` registers SCTP Generic Segmentation Offload support for IPv4 and IPv6. It handles segmentation of SCTP GSO skbs and checksum preparation when hardware cannot compute SCTP CRC32c.

## Important APIs, Types, And Functions
The main initialization entry is `sctp_offload_init()`. Static integration tables are `sctp_offload` and `sctp6_offload`, both with `.callbacks.gso_segment = sctp_gso_segment`. Helpers are `sctp_gso_segment()` and `sctp_gso_make_checksum()`.

## Control Flow
`sctp_offload_init()` registers IPv4 offload first with `inet_add_offload()` and IPv6 offload next with `inet6_add_offload()`, rolling back IPv4 registration if IPv6 registration fails. `sctp_gso_segment()` rejects non-SCTP-GSO skbs, ensures the SCTP common header is pullable, temporarily pulls it before segmentation decisions, and then either accepts robust hardware GSO by recalculating `gso_segs` from the head/frags or calls `skb_segment()` with checksum-capable features.

After software segmentation, if `NETIF_F_SCTP_CRC` is unavailable, it walks produced segments and fills SCTP checksums for `CHECKSUM_PARTIAL` skbs using `sctp_gso_make_checksum()`. That helper resets checksum mode, primes GSO checksum metadata for potential UDP tunneling checksums, and computes CRC from the SCTP transport offset.

## State And Persistence
The file owns only static offload registration structures. Runtime state is per-skb segmentation metadata such as `gso_type`, `gso_segs`, `ip_summed`, `csum_not_inet`, and SCTP checksum fields. Nothing is persisted.

## Dependencies And Integration Points
It integrates with the networking offload framework, IPv4/IPv6 inet offload registries, skbuff GSO helpers, SCTP checksum code, and the output path that marks large SCTP packets as `SKB_GSO_SCTP` or UDP tunnel GSO.

## Risks
Checksum correctness is the central risk. SCTP uses CRC32c rather than the standard Internet checksum, and UDP-encapsulated SCTP also needs correct outer checksum metadata. Incorrect header pulling or `gso_segs` accounting can cause malformed segmentation, bad statistics, or device-driver offload failures. Rollback on init failure must remain paired so SCTP is not partially registered.

## Test Signals
Test native SCTP GSO over IPv4 and IPv6, devices with and without `NETIF_F_SCTP_CRC`, software fallback segmentation, UDP-encapsulated SCTP GSO, cloned/nonlinear skbs, robust GSO paths that return `NULL`, and module init paths where IPv6 offload registration fails after IPv4 succeeds.
