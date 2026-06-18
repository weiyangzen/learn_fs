# sources/distributed-fs/ceph-client/net/bridge/netfilter/ebt_log.c

## Purpose
Implements the legacy ebtables `log` watcher/target, preserving classic ebtables syslog formatting while optionally delegating to the netfilter logging backend.

## Important APIs, Types, And Functions
Key functions are `ebt_log_tg`, `ebt_log_tg_check`, `ebt_log_packet`, `print_ports`, and `xt_target ebt_log_tg_reg`. Local helper structs describe minimal TCP/UDP and ARP payload fields.

## Control Flow
Validation checks log bitmask and loglevel, and NUL-terminates the prefix. Runtime constructs `nf_loginfo`, then either calls `nf_log_packet` when `EBT_LOG_NFLOG` is requested or prints classic bridge log output under a spinlock. The classic path prints MAC fields and optionally decodes IPv4, IPv6, ARP/RARP, and transport ports using safe skb header reads.

## State And Persistence Behavior
No per-rule mutable state exists. Runtime side effects are logs to syslog/netfilter logging; non-init network namespaces are suppressed unless `sysctl_nf_log_all_netns` permits logging.

## Dependencies And Integration Points
Depends on `nf_log`, IPv4/IPv6/ARP helpers, bridge ebtables log UAPI, xtables, and optional `CONFIG_BRIDGE_EBT_IP6` for IPv6 decoding.

## Risks And Test Signals
Risks include log format regressions, namespace logging policy, incomplete header reads, rate/volume effects, and lock-held printing. Tests should verify prefix truncation, loglevel rejection, IP/IPv6/ARP decode, NFLOG delegation, namespace behavior, and malformed packet logging.
