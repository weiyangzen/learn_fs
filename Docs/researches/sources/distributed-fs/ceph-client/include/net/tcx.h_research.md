# sources/distributed-fs/ceph-client/include/net/tcx.h

## Purpose

`tcx.h` defines the TCX attachment layer for BPF programs at traffic-control ingress and egress. It bridges netdevice TC hooks, `bpf_mprog` multi-program bundles, mini qdisc presence, and BPF link/program attach/query operations.

## Important APIs, types, and functions

Key types are `struct tcx_entry`, containing an RCU mini qdisc pointer, `bpf_mprog_bundle`, active miniq count, and RCU head, and `struct tcx_link`, wrapping `struct bpf_link` plus the target netdevice. Helpers include `tcx_set_ingress()`, `tcx_entry()`, `tcx_link()`, `tcx_entry_update()`, `tcx_entry_fetch()`, `tcx_entry_create()`, `tcx_entry_free()`, `tcx_entry_fetch_or_create()`, `tcx_skeys_inc()`/`dec()`, `tcx_miniq_inc()`/`dec()`, `tcx_entry_is_active()`, and `tcx_action_code()`. BPF syscall-facing declarations include `tcx_prog_attach()`, `tcx_link_attach()`, `tcx_prog_detach()`, `tcx_prog_query()`, and `tcx_uninstall()`.

## Control flow

Under `CONFIG_NET_XGRESS`, callers hold RTNL, fetch or create a `bpf_mprog_entry`, attach/detach programs through BPF syscall handlers, then publish ingress or egress entries with `rcu_assign_pointer()`. Updates synchronize after a/b entry swaps with `synchronize_rcu()`. On packet execution, TCX maps program return codes to `TCX_PASS`, `TCX_DROP`, `TCX_REDIRECT`, or `TCX_NEXT`; `TCX_PASS` also propagates `tc_classid` into `skb->tc_index`.

## State and persistence behavior

Persistent state lives on `struct net_device` RCU pointers `tcx_ingress` and `tcx_egress`, in the `bpf_mprog_bundle`, and in mini qdisc active counts. Global ingress/egress static-key accounting is adjusted with `tcx_skeys_inc()`/`dec()`. Entries are freed by RCU and must remain stable for readers during datapath execution.

## Dependencies and integration points

It depends on BPF core, BPF links, multi-program bundles, `sch_generic.h`, netdevice TC ingress/egress queues, RTNL locking, and optional `CONFIG_BPF_SYSCALL`. Without the needed config, attach/query helpers return `-EINVAL` and uninstall is a no-op.

## Risks and test signals

Risks include publishing entries without RTNL, freeing before RCU readers finish, mismatched miniq reference counts, static-key leaks, and incorrect action-code handling. Tests should cover attach/detach/query for ingress and egress, link lifetime, program chain replacement under traffic, miniq coexistence, disabled-config stubs, and BPF return-code mapping.
