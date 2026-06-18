# sources/distributed-fs/ceph-client/net/netfilter/nfnetlink_cttimeout.c

## Purpose
`nfnetlink_cttimeout.c` provides userspace-managed conntrack timeout policies. It supports named timeout objects attached to conntracks, replacement of timeout data for the same protocol kind, deletion with reference checks, dump/get operations, and getting or setting per-net default protocol timeouts through each L4 protocol's timeout serializer.

## Important APIs, Types, and Functions
Named objects are `struct ctnl_timeout`, embedding `struct nf_ct_timeout` after list/refcount/name metadata. Per-net storage is `struct nfct_timeout_pernet`. Parser/formatter functions are `ctnl_timeout_parse_policy()`, `ctnl_timeout_fill_info()`, `cttimeout_default_fill_info()`, and protocol default access in `cttimeout_default_get()`.

nfnetlink callbacks are `cttimeout_new_timeout()`, `cttimeout_get_timeout()`, `cttimeout_del_timeout()`, `cttimeout_default_set()`, and `cttimeout_default_get()`. Integration with conntrack core is via `struct nf_ct_timeout_hooks hooks`, `ctnl_timeout_find_get()`, `ctnl_timeout_put()`, and the global RCU pointer `nf_ct_timeout_hook`.

## Control Flow, State, and Persistence
Creation requires name, L3 protocol, L4 protocol, and nested timeout data. Existing names can be replaced only when L3 and L4 protocol kind match; replacement re-parses into the existing timeout data. New objects find the L4 protocol, allocate storage sized by `l4proto->ctnl_timeout.obj_size`, parse protocol-specific attributes via `nlattr_to_obj`, initialize `nf_ct_timeout`, set refcount, pin the module, and append to the per-net RCU list.

Get supports dumps with RCU cursor continuation or named unicast. Delete without name tries all objects; named delete calls `ctnl_timeout_try_del()`, which only removes unreferenced objects, calls `nf_ct_untimeout()` to detach the policy from conntracks, and frees through RCU. Default set passes `NULL` as the destination object to the L4 parser, relying on protocol code to update per-net defaults. Default get selects protocol-specific per-net timeout arrays for ICMP, TCP, UDP, ICMPv6, SCTP, GRE, and generic protocol 255.

Namespace teardown first moves live objects to a freelist in `pre_exit` before the core synchronize-RCU point, then detaches all conntracks and frees unreferenced objects in `exit`. Module exit unregisters hooks and clears timeout pointers from existing conntracks through `nf_ct_iterate_destroy()`.

## Dependencies and Integration Points
The file depends on conntrack core, L4 protocol timeout descriptors, per-net protocol timeout storage, nfnetlink, RCU, and refcounts. It is consumed by conntrack extensions that resolve named timeout policies through `nf_ct_timeout_hook`.

## Risks and Test Signals
Risks include protocol-specific parser misuse for default updates, L4 protocol support checks, refcount/module refcount balance, namespace exit ordering, stale timeout pointers on module unload, and delete races with conntrack attachment. Tests should cover create/replace kind mismatch, malformed protocol data, named and dump get, busy delete, default get/set for every enabled protocol, namespace teardown with attached policies, and module unload clearing conntrack timeout extensions.
