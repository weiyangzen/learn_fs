# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_log.h

## Purpose
Defines netfilter logging option flags and maximum log prefix length.

## Important APIs, Types, And Functions
Exports `NF_LOG_TCPSEQ`, `NF_LOG_TCPOPT`, `NF_LOG_IPOPT`, `NF_LOG_UID`, reserved `NF_LOG_NFLOG`, `NF_LOG_MACDECODE`, `NF_LOG_MASK`, and `NF_LOG_PREFIXLEN`.

## Control Flow
Userspace logging rules pass these flags to request extra packet metadata in log output; logging backends mask and decode supported options.

## State, Persistence, And Dependencies
State persists in firewall logging rule configuration. No dependencies.

## Integration Points
Used by iptables/nftables log targets, kernel netfilter loggers, and userspace rule builders.

## Risks
`NF_LOG_NFLOG` is marked unsupported and must not be reused. Prefix length is an ABI limit for rule validation.

## Test Signals
Validate flag mask handling, prefix length enforcement, TCP/IP option logging, UID logging, MAC decode output, and rejection/ignore behavior for unsupported bits.
