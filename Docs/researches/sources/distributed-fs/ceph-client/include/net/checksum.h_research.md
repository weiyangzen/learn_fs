# sources/distributed-fs/ceph-client/include/net/checksum.h

Read `sources/distributed-fs/ceph-client/include/net/checksum.h` completely for this pass (191 lines, 4961 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/checksum.h_research.md`.

Purpose: provides generic networking checksum helpers for copying data while checksumming, one's-complement checksum arithmetic, incremental checksum updates, protocol checksum replacement, remote checksum adjustment, and checksum negation. Architecture-specific implementations can override several helpers.

Important APIs/types/functions: fallback `csum_and_copy_from_user()`, `csum_and_copy_to_user()`, and `csum_partial_copy_nocheck()` combine copying with `csum_partial()`. Arithmetic helpers include `csum_add()`, `csum_sub()`, `csum16_add()`, `csum16_sub()`, `csum_shift()`, `csum_block_add()`, `csum_block_sub()`, `csum_unfold()`, `csum_replace_by_diff()`, `csum_replace4()`, `csum_replace2()`, `csum_replace()`, `csum_from32to16()`, `remcsum_adjust()`, `remcsum_unadjust()`, and `wsum_negate()`. External protocol-aware helpers are `inet_proto_csum_replace4()`, `inet_proto_csum_replace16()`, and `inet_proto_csum_replace_by_diff()`. `CSUM_MANGLED_0` represents UDP-style zero checksum mangling.

Control flow: callers build or update packets by computing partial sums over copied buffers, adding/subtracting one's-complement sums, folding 32-bit sums to 16-bit header checksums, or replacing header fields incrementally rather than recomputing whole packets. `inet_proto_csum_replace*()` updates skb checksum metadata when pseudo-header or payload checksum fields change. `remcsum_adjust()` removes an outer prefix contribution, writes a derived checksum at an offset, and returns a delta later consumed by `remcsum_unadjust()`.

State and persistence: no persistent state is stored. The functions mutate caller-provided checksums, packet memory, and sometimes skb checksum metadata through external helpers. User-copy fallbacks return zero on copy fault, so callers must treat zero as a failure signal in these contexts.

Dependencies and integration points: depends on asm checksum primitives, byte order helpers, `linux/uaccess.h` for fallbacks, `struct sk_buff`, and the IP/TCP/UDP/XFRM/tunnel stack. It is used across IPv4/IPv6, transport protocols, encapsulation, NAT, segmentation, and checksum-offload adjustment paths.

Risks: one's-complement arithmetic has non-obvious carry and zero-mangling rules. `csum_shift()` must match odd-byte alignment semantics. Incremental update helpers require old/new fields in network-endian typed forms. `inet_proto_csum_replace2()` intentionally packs 16-bit values into a 32-bit replacement path. Remote checksum helpers assume valid offsets into writable packet data. Copy-and-checksum fallbacks collapse copy faults to zero, which can be ambiguous if callers ignore error conventions.

Test signals: checksum selftests over odd/even offsets, endian variants, carry wraparound, RFC 1624 replacement cases, IPv4 header TOS/TTL/NAT changes, IPv6 pseudo-header replacement, remote checksum offload adjust/unadjust round trips, user-copy fault injection, and comparisons with architecture-specific checksum implementations.
