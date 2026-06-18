# sources/distributed-fs/ceph-client/net/core/lwtunnel.c

Purpose: Provides generic lightweight tunnel infrastructure for route encapsulation types such as MPLS, ILA, SEG6, BPF, RPL, IOAM6, and XFRM. It manages encap ops registration, state construction/destruction, netlink serialization, comparison, and datapath dispatch.

Important APIs, types, and functions: Exports static key `nf_hooks_lwtunnel_enabled`. State and registration APIs include `lwtunnel_state_alloc()`, `lwtunnel_encap_add_ops()`, `lwtunnel_encap_del_ops()`, `lwtunnel_build_state()`, `lwtunnel_valid_encap_type()`, `lwtunnel_valid_encap_type_attr()`, and `lwtstate_free()`. Netlink/route helpers are `lwtunnel_fill_encap()`, `lwtunnel_get_encap_size()`, and `lwtunnel_cmp_encap()`. Datapath callbacks are `lwtunnel_output()`, `lwtunnel_xmit()`, and `lwtunnel_input()`.

Control flow: Encapsulation ops are stored in an RCU pointer array indexed by encap type and installed/removed with `cmpxchg`; removal synchronizes the network stack. State build validates type, looks up ops under RCU, grabs the module owner, calls the type-specific `build_state()`, and drops the module ref on failure. Validation can autoload modules named `rtnl-lwt-<TYPE>` for supported types. Attribute validation walks nexthops and validates any `RTA_ENCAP_TYPE`. Free calls type-specific destroy if present and drops the module owner. Fill/size/compare dispatch to registered ops if available. Datapath output/xmit/input verify dst/lwtstate, enforce device transmit recursion limits, dispatch through type-specific callbacks under RCU, and free the skb on unsupported or invalid paths.

State and persistence: Global state is the RCU `lwtun_encaps[]` ops table and the netfilter static key. Per-route runtime state is `struct lwtunnel_state`, allocated with optional private data and module reference ownership. Persistence of route configuration is outside this file.

Dependencies and integration points: Integrates with rtnetlink route attributes, nexthop parsing, module autoload, dst entries, route output/input paths, per-encap modules such as BPF (`lwt_bpf.c`), MPLS/SEG6/etc., RCU, module refcounts, and dev transmit recursion accounting.

Risks: Module refcounting must match successful state builds and frees. Missing ops or unsupported callbacks free skbs in datapath, which is correct but easy to mis-handle in callers. Input expects softirq context. `lwtstate_free()` indexes `lwtun_encaps[lws->type]` without revalidating type, relying on valid constructed state. Recursion guard protects against route loops and must remain in every datapath.

Test signals: Register/unregister encap ops, validate module autoload, build/fill/size/cmp/free states for each encap type, parse multipath nexthop attrs, exercise output/xmit/input success and unsupported callbacks, route loop recursion limit, invalid dst/lwtstate, and concurrent ops removal under RCU.
