# sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_hook.c

## Purpose
`nfnetlink_hook.c` exposes registered netfilter hooks to userspace through an nfnetlink dump-only subsystem. It reports hook function names, module names, hook number, priority, and optional typed descriptions for nftables chains, nft flowtables, and BPF netfilter links.

## Important APIs, Types, and Functions
The subsystem callback is `nfnl_hook_get()`, which only supports `NLM_F_DUMP`. Dump setup, iteration, and cleanup are `nfnl_hook_dump_start()`, `nfnl_hook_dump()`, and `nfnl_hook_dump_stop()`. Hook-array lookup is `nfnl_hook_entries_head()`. Message creation is `nfnl_hook_dump_one()`, with typed nested helpers `nfnl_hook_put_bpf_prog_info()`, `nfnl_hook_put_nft_chain_info()`, and `nfnl_hook_put_nft_ft_info()`.

`struct nfnl_dump_hook_data` stores the target netdev name, initial hook-head pointer value for consistency checks, and hook number.

## Control Flow, State, and Persistence
The user must provide a hook number; `NFPROTO_NETDEV` additionally requires a device name. Start validates hook range and resolves the current hook entries pointer under RCU. The pointer is stored only as a consistency token. Dump re-resolves hook entries each iteration, bumps the netlink dump sequence if the head pointer changed or the cursor is beyond the current entry count, retrieves `nf_hook_ops` pointers, and emits one netlink message per hook operation.

For each hook op, KALLSYMS support formats `%ps` into function and optional module names. `NFPROTO_INET` ingress is reported as netdev ingress for hook-number compatibility. For nftables hooks, only active chains/flowtables are described, including table name, object name, and family. BPF link information includes the BPF program id when configured.

Persistent state is limited to subsystem registration. Dump allocations are temporary and freed in `done`.

## Dependencies and Integration Points
This file reads netfilter hook arrays for IPv4, IPv6, ARP, bridge, and netdev ingress/egress families; nftables active-state helpers; optional BPF netfilter link support; KALLSYMS; and netdevice lookup under RCU. It uses `NFNL_CB_RCU` and a helper that temporarily drops/reacquires RCU around `netlink_dump_start()`.

## Risks and Test Signals
Risks include inconsistent dumps while hooks are registered/unregistered, netdev rename/removal races, optional-family build coverage, missing KALLSYMS output, and active-state filtering of nftables objects during transactions. Tests should dump every supported family/hook, require device for netdev family, verify function/module name attributes when KALLSYMS is enabled, inspect nft chain/flowtable descriptors, handle hook-array mutation during dump, and reject unsupported non-dump get requests.
