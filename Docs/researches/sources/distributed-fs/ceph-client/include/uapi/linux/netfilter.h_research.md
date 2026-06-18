# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter.h

## Purpose
Defines base netfilter UAPI verdicts, verdict encoding helpers, hook numbers, protocol family IDs, and generic IPv4/IPv6 address union.

## Important APIs, Types, And Functions
Exports verdict constants `NF_DROP` through `NF_STOP`, masks/flags `NF_VERDICT_*`, helpers `NF_QUEUE_NR` and `NF_DROP_ERR`, hooks `nf_inet_hooks`/`nf_dev_hooks`, `NFPROTO_*`, and `nf_inet_addr`.

## Control Flow
Netfilter rules/hooks return verdict values; high bits encode queue numbers or drop errno. Hook numbers identify traversal points for IPv4/IPv6/netdev, and protocol IDs identify rule family.

## State, Persistence, And Dependencies
State persists in netfilter rulesets and packet traversal context. Depends on types, compiler annotations, and IPv4/IPv6 address headers.

## Integration Points
Used by nftables/iptables, nfqueue, conntrack/NAT headers, firewall extensions, and kernel hooks.

## Risks
Verdict lower 8 bits and high-bit auxiliary encoding must be masked correctly. `NF_STOP` is deprecated but retained for userspace compatibility. DECnet is userspace-only.

## Test Signals
Validate verdict masking, queue-number encoding, drop errno encoding, hook IDs, protocol family IDs, and address union layout.
