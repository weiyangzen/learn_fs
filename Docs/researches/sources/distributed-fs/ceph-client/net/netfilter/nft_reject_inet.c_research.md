
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_reject_inet.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_reject_inet.c

## Purpose

`nft_reject_inet.c` implements the inet-family nftables `reject` expression. It emits IPv4 or IPv6 ICMP unreachable messages or TCP resets according to the packet family, then drops the original packet.

## Important APIs, Types, and Functions

`nft_reject_inet_eval()` dispatches on `nft_pf(pkt)` and `priv->type`. It calls `nf_send_unreach()`, `nf_send_reset()`, `nf_send_unreach6()`, or `nf_send_reset6()`. The expression ops reuse shared `nft_reject_init()`, `nft_reject_dump()`, and `nft_reject_policy`.

## Control Flow

Evaluation switches first on IPv4 versus IPv6. For raw ICMP unreachable it uses the configured code; for TCP reset it sends a reset through the family helper; for ICMPX it maps generic codes to family-specific ICMP constants. It always sets `regs->verdict.code = NF_DROP`. Validation permits local-in, forward, local-out, prerouting, and ingress hooks for inet.

## State and Persistence Behavior

Persistent state is just reject type and ICMP code. Generated response packets and TCP reset construction are delegated to nf_reject helpers. No cross-packet state is kept.

## Dependencies and Integration Points

The file integrates with the shared reject module, nf_tables inet family registration, IPv4 and IPv6 reject helpers, packet hook metadata, and socket metadata for reset generation.

## Risks and Test Signals

Risks include incorrect family dispatch in inet chains, generated replies in unsupported hook contexts, and TCP reset helper behavior when socket metadata is absent. Test IPv4 and IPv6 ICMP unreachable, ICMPX mappings, TCP reset, ingress hook validation, and packet capture of generated errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_reject_inet.c -->
