# sources/distributed-fs/ceph-client/net/mptcp/protocol.h

## Purpose

`protocol.h` is the internal MPTCP contract shared by the protocol core, subflow code, options parser, path managers, scheduler, token code, crypto, sockopt handling, and diagnostics. It defines wire-option constants, shared socket/subflow/request structures, state bits, helper macros, inline functions, and cross-file function prototypes.

## Important APIs, types, and functions

- Wire constants: `OPTION_MPTCP_*`, `MPTCPOPT_*`, TCP option lengths, DSS/ADD_ADDR/PRIO/RST flags, and `MPTCP_SUPPORTED_VERSION`.
- Shared metadata: `struct mptcp_skb_cb`, `struct mptcp_options_received`, `struct csum_pseudo_header`.
- Path-manager types: `enum mptcp_pm_status`, `enum mptcp_pm_type`, `enum mptcp_addr_signal_status`, `struct mptcp_pm_data`, `struct mptcp_pm_local`, `struct mptcp_pm_addr_entry`.
- Core socket state: `struct mptcp_sock`, `struct mptcp_data_frag`, `struct mptcp_subflow_request_sock`, `struct mptcp_subflow_context`, `struct mptcp_delegated_action`.
- Iteration and conversion helpers: `mptcp_sk()`, `mptcp_for_each_subflow()`, `mptcp_subflow_ctx()`, `mptcp_subflow_tcp_sock()`, `subflow_get_local_id()`.
- Inline behavior helpers: receive-space conversion, RTT estimate, pending send-frag navigation, fallback checks, DATA_FIN checks, PM signal checks, delegated-action queueing, sndbuf propagation, and socket writeability helpers.
- Prototypes for protocol, subflow, scheduler, PM, userspace PM, netlink events, token, crypto, and sockopt modules.

## Control flow

The header does not run a top-level flow, but it shapes all MPTCP flows. Incoming TCP options are parsed into `mptcp_options_received`; subflow handshake code populates request and subflow contexts; `protocol.c` consumes the shared state to move data and drive socket lifecycle; PM modules inspect and mutate `mptcp_pm_data`; scheduler code uses `mptcp_sched_ops` hooks to mark subflows; and sockopt code syncs MPTCP-level options to subflows using `setsockopt_seq`.

Inline helpers also encode hot-path decisions: whether data is available, whether epoll should report readable, whether a subflow is active, whether fallback has occurred, how long PM options are on the wire, and how to schedule delegated per-CPU subflow work without directly taking parent locks in softirq context.

## State and persistence

The header defines the persistent in-memory layout of MPTCP sockets. `struct mptcp_sock` embeds `inet_connection_sock` first and persists connection-level sequence numbers, queues, timers, PM state, scheduler state, locks, fallback state, socket-option mirrors, and counters for diagnostics. `struct mptcp_subflow_context` persists per-TCP-subflow mapping, handshake, PM ID, reset, stale, delegated-action, and callback state. `struct mptcp_pm_data` carries path-manager counters, bitmaps, and address signaling lists.

## Dependencies and integration points

It includes Linux random, TCP, inet connection sock, generic netlink, UAPI MPTCP headers, and reset-reason definitions. The declarations bind together `protocol.c`, `subflow.c`, `options.c`, `pm.c`, `pm_netlink.c`, `pm_userspace.c`, `pm_kernel.c`, `sched.c`, `sockopt.c`, token and crypto modules, diagnostics, and optional IPv6/SYN-cookie support.

## Risks and edge cases

Because this file defines shared structure layout and inline semantics, changes have broad ABI-like internal impact. Bitfield ordering, reset groups used by `memset()`, socket embedding order, SKB control-block size, fallback helpers, and memory-accounting helpers are particularly sensitive. Conditional IPv6 and SYN-cookie declarations must stay consistent with implementation files. Any new field requires careful initialization in active, passive clone, disconnect, and destroy paths.

## Test signals

Build-time `BUILD_BUG_ON()` checks in implementation files validate some size assumptions. Runtime test signals are indirect: MPTCP selftests covering option parsing, fallback, PM behavior, joins, diagnostics, and socket options validate this contract. Static analysis and compile coverage across `CONFIG_MPTCP_IPV6`, `CONFIG_SYN_COOKIES`, and debug-net configurations are important because many helpers are conditional or lock-sensitive.
