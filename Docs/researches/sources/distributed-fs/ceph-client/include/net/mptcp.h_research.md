<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mptcp.h -->
# sources/distributed-fs/ceph-client/include/net/mptcp.h

## Purpose
`mptcp.h` is the core MPTCP interface header for TCP option generation/parsing, skb extension ownership, scheduler and path-manager plugin hooks, IPv6 support, BPF exposure, and disabled-build stubs.

## Important APIs, types, and functions
Important types are `struct mptcp_ext`, `struct mptcp_rm_list`, `struct mptcp_addr_info`, `struct mptcp_out_options`, `struct mptcp_sched_ops`, and `struct mptcp_pm_ops`. Exported functions include MPTCP init, option builders/parsers, option writer, diagnostics, request-sock helpers, reset-option helpers, blackhole detection, MPTCPv6 init/mapped handling, and BPF subflow conversion.

## Control flow
TCP handshake and established paths ask MPTCP helpers to reserve and populate options, parse incoming options, and write encoded options into the TCP header. skb extensions carry data sequence mapping, ACKs, checksum, FIN, reset, and frozen/copy state. Collapse/copy/move helpers preserve or compare extension state so TCP skb coalescing does not merge incompatible mappings.

## State and persistence
State is in MPTCP sockets/subflows, skb extensions, scheduler/path-manager registered lists, request-sock flags, and optional IPv6/BPF integration. The disabled configuration collapses calls into TCP fallback stubs.

## Dependencies and integration points
It depends on TCP, skb extensions, module/list infrastructure, IPv4/IPv6 address types, seq_file, and BPF when enabled. It integrates tightly with TCP transmit, receive, request-sock, diagnostics, and pluggable MPTCP policy modules.

## Risks and test signals
Risks include skb extension ownership transfer leaks, frozen extension copy semantics, collapse of incompatible data mappings, option-size accounting, 32/64-bit DSN/ACK mismatches, disabled-build fallback behavior, and scheduler/path-manager module lifetime. Tests should cover SYN/SYNACK/established options, skb clone/collapse/move, reset options, IPv6 mapped subflows, BPF lookup, and CONFIG_MPTCP off builds.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mptcp.h` completely for this pass (340 lines, 8052 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mptcp.h -->
