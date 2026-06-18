<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_standalone.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_standalone.c

## Purpose
Provides the standalone conntrack module lifecycle and user-facing observability/configuration. It registers per-net conntrack state, `/proc` sequence files, per-CPU stats, sysctl tables, optional eager hook enablement, and global module initialization/cleanup.

## Important APIs, Types, and Functions
Exports `nf_conntrack_net_id`, `print_tuple()`, and `nf_conntrack_count()`. Procfs logic centers on `ct_seq_start()`, `ct_get_next()`, `ct_seq_show()`, and CPU stat seq ops. Sysctl setup uses `nf_conntrack_standalone_init_sysctl()` plus protocol-specific assignment helpers for TCP/SCTP/GRE. Per-net lifecycle is `nf_conntrack_pernet_init()`, `nf_conntrack_pernet_exit()`, and module lifecycle is `nf_conntrack_standalone_init()`/`fini()`.

## Control Flow
Module init starts core conntrack initialization, registers global sysctl `net/nf_conntrack_max`, finalizes core init, and registers a per-net subsystem. Per-net init sets checksum validation on, installs per-net sysctls and proc entries, initializes core conntrack net state, and optionally enables IPv4/IPv6 hooks when `enable_hooks=1`. Proc iteration walks the conntrack hash under RCU, handles nulls-list restarts, skips reply tuples, kills GC-eligible entries, and prints tuple/state/accounting/status metadata.

## State and Persistence
Persistent state includes module parameter `enable_hooks`, `nf_conntrack_net_id`, global sysctl header, per-net `nf_conntrack_net`, proc entries, sysctl table copies, conntrack hash/count/stat state owned by core, and per-net protocol timeout pointers. Non-init namespaces get read-only global sizing sysctls.

## Dependencies and Integration Points
Depends on conntrack core, L4 descriptors, helper/expect/acct/timestamp/zone APIs, procfs, seq_file, sysctl, LSM secctx, pernet subsystem, and net namespace userns ownership. It wires sysctl data pointers into the per-net protocol structs initialized elsewhere.

## Risks
Proc iteration over RCU nulls hash must preserve bucket/skip state during concurrent mutation. Sysctl table copies must be freed after unregister. Per-net failure paths must unwind proc/sysctl/core/hook setup in the right order. User-facing proc output is ABI-like and sensitive to field order.

## Test Signals
Load/unload conntrack, create/delete net namespaces, read `/proc/net/nf_conntrack` and `/proc/net/stat/nf_conntrack`, tune global and per-net sysctls, verify non-init namespace read-only sizing knobs, enable eager hooks, exercise acct/timestamp/zone/secmark output, and resize hash buckets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_standalone.c -->
