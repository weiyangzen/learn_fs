
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_payload.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nft_payload.c

## Purpose

`nft_payload.c` implements nftables payload load and payload write expressions. It extracts bytes from link, network, transport, inner, and tunnel-relative headers into nft registers, writes register data back into packets, handles hardware-accelerated VLAN tag compensation, supports selected flow offload translation, and repairs checksums for payload modification.

## Important APIs, Types, and Functions

The main expression type is `nft_payload_type`, whose `select_ops` chooses normal load, fast load, or set/write operations. `nft_payload_eval()` reads packet bytes into `regs->data`; `nft_payload_set_eval()` writes bytes from a source register into an skb. `nft_payload_inner_eval()` is called by inner tunnel parsing support using an explicit `nft_inner_tun_ctx`. `nft_payload_inner_offset()` derives inner payload offsets for UDP, TCP, GRE version 0, and IP-in-IP. The offload helpers map common Ethernet, VLAN, IPv4, IPv6, TCP, and UDP fields to flow dissector keys. `struct nft_payload_set` extends payload attributes with checksum type, checksum offset, and L4 pseudo-header checksum flags.

## Control Flow

Initialization parses base, offset, length, and register attributes, then validates register load or store size. Read evaluation chooses a base offset from skb metadata, applies VLAN reconstruction when offloads stripped the VLAN header, adds the configured offset, and copies bytes with `skb_copy_bits()`. Write evaluation chooses the same base classes, optionally updates checksum state by comparing old bytes to new register bytes, ensures skb writability, and stores data with `skb_store_bits()`. SCTP checksum mode recomputes the whole SCTP checksum after modification. Unsupported header bases, missing L4 metadata, fragments, and short packets break rule evaluation via `NFT_BREAK`.

## State and Persistence Behavior

The expression stores only static netlink configuration in private expression data. Runtime state is packet-local: destination/source registers, skb header offsets, VLAN tag fields, checksum fields, and `regs->verdict`. Payload writes mutate the skb persistently for later expressions and later network stack stages. Inner offset caching mutates `nft_pktinfo` flags and `inneroff`.

## Dependencies and Integration Points

The file integrates with nf_tables core register parsing, skb accessors, VLAN helpers, TCP/UDP/SCTP/ICMPv6 headers, GRE parsing, and nf_tables flow offload. It is used by nft payload syntax and by tunnel inner expression support. Offload support depends on `nft_offload_ctx`, `nft_flow_rule`, and Linux flow dissector keys.

## Risks and Test Signals

Risks concentrate around offset arithmetic, fragments, non-linear skbs, VLAN hardware acceleration, and checksum repair. Incorrect checksum flags can corrupt transport checksums; incorrect inner offset handling can read attacker-controlled wrong bytes. Test signals include nftables payload get/set tests, VLAN-tagged packets with hwaccel tags, fragmented IPv4 packets, TCP/UDP/SCTP checksum validation, GRE/IPIP encapsulation, and flowtable offload rules matching Ethernet/IP/port fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nft_payload.c -->
