# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_synproxy.h

## Purpose
Defines SYNPROXY option flags and configuration struct for netfilter SYN proxy handling.

## Important APIs, Types, And Functions
Exports `NF_SYNPROXY_OPT_MSS`, `NF_SYNPROXY_OPT_WSCALE`, `NF_SYNPROXY_OPT_SACK_PERM`, `NF_SYNPROXY_OPT_TIMESTAMP`, `NF_SYNPROXY_OPT_ECN`, `NF_SYNPROXY_OPT_MASK`, and `nf_synproxy_info`.

## Control Flow
Userspace configures SYNPROXY rules with selected TCP option handling, window scale, and MSS. Kernel SYN proxy logic uses this data when synthesizing handshake responses and validating connections.

## State, Persistence, And Dependencies
State persists in netfilter rules and per-flow SYNPROXY/conntrack state. Depends on `linux/types.h`.

## Integration Points
Used by nftables/iptables SYNPROXY targets and conntrack TCP handling.

## Risks
`NF_SYNPROXY_OPT_ECN` is defined but excluded from `NF_SYNPROXY_OPT_MASK`, so callers must follow mask semantics. Incorrect MSS/window scale settings can break legitimate clients.

## Test Signals
Validate rule insertion, option mask handling, SYN/SYN-ACK option synthesis, MSS/wscale values, timestamp/SACK behavior, and ECN handling expectations.
