# sources/distributed-fs/ceph-client/net/ipv6/sysctl_net_ipv6.c

## Purpose
`sysctl_net_ipv6.c` registers `/proc/sys/net/ipv6` sysctl tables. It provides per-network-namespace IPv6 tunables, route and ICMP subtrees, and a small init-net read-oriented table for global MLD and optional CALIPSO settings.

## Important APIs, types, and functions
`ipv6_table_template[]` defines per-netns entries such as `bindv6only`, `anycast_src_echo_reply`, flowlabel controls, `fwmark_reflect`, id generation timing, nonlocal bind, extension-header limits, multipath hash policy and fields, `seg6_flowlabel`, route-notification policy, and IOAM IDs. `ipv6_rotable[]` defines `mld_max_msf`, `mld_qrv`, and optional NetLabel CALIPSO cache controls.

`proc_rt6_multipath_hash_policy()` and `proc_rt6_multipath_hash_fields()` wrap min/max handlers and emit `NETEVENT_IPV6_MPATH_HASH_UPDATE` on successful writes. Lifecycle is handled by `ipv6_sysctl_net_init()`, `ipv6_sysctl_net_exit()`, `ipv6_sysctl_register()`, and `ipv6_sysctl_unregister()`.

## Control flow
At global registration, the file first registers `ipv6_rotable` in init_net under `net/ipv6`, then registers a pernet subsystem. For each netns, `ipv6_sysctl_net_init()` duplicates `ipv6_table_template`, adjusts every `.data` pointer by the offset from `init_net` to the target `struct net`, obtains dynamically built route and ICMP sysctl tables from `ipv6_route_sysctl_init()` and `ipv6_icmp_sysctl_init()`, and registers `net/ipv6`, `net/ipv6/route`, and `net/ipv6/icmp`.

Failure paths unwind in reverse order: unregister registered headers and free copied tables. Netns exit reads the original allocated table pointers from `ctl_table_arg`, unregisters ICMP, route, and root IPv6 headers, and frees all three table allocations. Global unregister removes the init-net table and pernet subsystem.

## State and persistence
Sysctl values mostly live in `struct net.ipv6.sysctl` and are therefore per-network-namespace in-memory state. The duplicated ctl tables are per-netns allocations whose data pointers target that namespace. `ip6_header` stores the init-net global table header. Values persist only for the lifetime of the namespace or kernel boot.

## Dependencies and integration points
This file integrates with the sysctl core, pernet subsystem, IPv6 route sysctl generation, ICMPv6 sysctl generation, netevent notifications, IOAM defaults, FIB multipath hash fields, MLD globals, and optional NetLabel CALIPSO controls. Multipath write handlers notify listeners that route hashing behavior may need recalculation.

## Risks and edge cases
Pointer rebasing assumes every template `.data` points into `init_net` at the same struct offset used by every netns; adding a non-netns data pointer to the template would be unsafe unless handled specially. Registration failure paths must match the allocation/registration order to avoid leaks or unregistering invalid headers. Multipath handlers must notify only after successful writes. Min/max bounds protect several u8/u32/u64 values; missing bounds on new sysctls could expose invalid network behavior.

## Test signals
Tests should create and destroy network namespaces, read and write representative `/proc/sys/net/ipv6` values, verify per-netns isolation, check route and ICMP subtrees exist, validate min/max rejection for flowlabel reflect, auto flowlabels, multipath policy/fields, fib notify mode, and IOAM IDs, and confirm multipath hash writes emit `NETEVENT_IPV6_MPATH_HASH_UPDATE`.
