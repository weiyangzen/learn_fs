# sources/distributed-fs/ceph-client/include/net/netfilter/nf_reject.h

Purpose: Provides a shared checksum eligibility helper used by reject implementations before generating reject responses.

Important APIs/types/functions: `nf_reject_verify_csum(struct sk_buff *skb, int dataoff, __u8 proto)` returns whether a packet protocol has a checksum model suitable for normal reject validation.

Control flow: Reject code calls this helper before responding. UDP is accepted only if the UDP header is readable and the checksum field is nonzero; GRE, AH, ESP, SCTP, and UDPLite are rejected because they have optional, partial, or separate integrity semantics.

State and persistence: Stateless inline helper. It reads skb header data through `skb_header_pointer`.

Dependencies/integration: Depends on skbuff header access, protocol constants, UDP header layout, and IPv4/IPv6 reject code using this common filter.

Risks/test signals: Key risk is sending rejects for packets whose integrity was not verified or silently dropping valid edge cases. Test UDP zero-checksum, truncated transport headers, GRE/AH/ESP/SCTP/UDPLite, non-linear skbs, and both nft/iptables reject paths.
