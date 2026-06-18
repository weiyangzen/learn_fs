# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_conntrack_tcp.h

## Purpose
Defines TCP conntrack state enum, TCP tracking flags, challenge-ACK/simultaneous-open bits, and flag/mask struct exposed to userspace.

## Important APIs, Types, And Functions
Exports `tcp_conntrack`, alias `TCP_CONNTRACK_SYN_SENT2`, timeout/diagnostic states, `IP_CT_TCP_FLAG_*`, `IP_CT_EXP_CHALLENGE_ACK`, `IP_CT_TCP_SIMULTANEOUS_OPEN`, and `nf_ct_tcp_flags`.

## Control Flow
Conntrack updates TCP states as packets progress through handshake, established data, FIN/close, retransmission, ignore, and unacknowledged paths. Flags capture negotiated TCP options and tracking policy.

## State, Persistence, And Dependencies
State persists in TCP conntrack protocol info. Depends on `linux/types.h`.

## Integration Points
Used by ctnetlink, conntrack tools, nft/iptables ct matches, and TCP NAT sequence adjustment.

## Risks
`TCP_CONNTRACK_LISTEN` is obsolete but aliased for SYN_SENT2 compatibility. Flags have mask semantics, so updates must distinguish desired value from affected bits.

## Test Signals
Validate state machine reporting across handshakes/closes/retransmits, TCP option flags, simultaneous open, challenge ACK expectation, and ctnetlink flag mask updates.
