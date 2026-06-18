# sources/distributed-fs/ceph-client/net/netfilter/ipset/ip_set_core.c

## Purpose

`ip_set_core.c` implements the core IP set subsystem. It registers set-type modules, manages per-network-namespace set arrays, exposes kernel APIs used by xtables/nftables set consumers, implements the nfnetlink userspace protocol for `ipset(8)`, and provides a legacy getsockopt compatibility interface for iptables/ip6tables.

## Important APIs And Types

Global registries include `ip_set_type_list` protected by `ip_set_type_mutex` and per-set reference counters protected by `ip_set_ref_lock`. `struct ip_set_net` stores the per-net RCU array of set pointers, maximum set count, and deletion/destroy flags. Exported APIs include `ip_set_type_register`, `ip_set_type_unregister`, `ip_set_alloc`, `ip_set_free`, `ip_set_get_ipaddr4`, `ip_set_get_ipaddr6`, `ip_set_init_comment`, `ip_set_extensions`, `ip_set_elem_len`, `ip_set_get_extensions`, `ip_set_put_extensions`, `ip_set_match_extensions`, `ip_set_test`, `ip_set_add`, `ip_set_del`, `ip_set_get_byname`, `ip_set_put_byindex`, `ip_set_name_byindex`, `ip_set_nfnl_get_byindex`, `ip_set_nfnl_put`, and `ip_set_put_flags`.

The nfnetlink subsystem `ip_set_netlink_subsys` dispatches create, destroy, flush, rename, swap, list/save, add, delete, test, header, type, protocol, get-by-name, and get-by-index commands. `so_set` implements legacy `SO_IP_SET` getsockopt operations.

## Control Flow

Type lookup first searches registered types under RCU. If a type is missing, `load_settype` temporarily drops the nfnetlink mutex, calls `request_module("ip_set_%s", name)`, then retries. `ip_set_create` validates the netlink protocol, allocates a base `struct ip_set`, references the type module, parses type-specific creation data, calls the type's `create`, finds or grows a free slot in the per-net set array, and publishes the set.

Destroy is two-stage for single sets: it checks `ref` and `ref_netlink`, removes the set pointer, cancels GC, waits for list-set flushes when needed, then releases through `call_rcu`. Destroy-all cancels all GCs, optionally waits for RCU barriers, then destroys every set. Flush, rename, and swap are serialized by nfnetlink and use set locks or `ip_set_ref_lock` as needed.

Kernel packet APIs fetch the set by index, validate dimensions and family, and call the variant `kadt`. `ip_set_test` treats `-EAGAIN` as a type request to complete an element by adding it, then converts errors to no-match. Userspace add/delete/test parse nested ADT attributes and call `uadt`; `call_ad` handles resize retries, range continuations, and restore-line error reporting.

Dumping uses netlink dump callbacks. It pins the set with `ref_netlink`, asks variants for headers and list elements, supports one-set and all-set dumps, and dumps list-like sets last. Extension helpers parse and serialize timeouts, counters, comments, skbinfo, and counter match operations.

## State And Persistence

All set data is per network namespace and in memory. `max_sets` defaults from `CONFIG_IP_SET_MAX` but can be overridden as a module parameter. Set pointers are RCU-protected, while set references prevent destruction under packet users or netlink dumps. Comments use RCU-allocated strings and contribute to `set->ext_size`. There is no disk persistence; userspace restore is required after reboot.

## Dependencies And Integration

The core depends on nfnetlink, net namespaces, RCU, x_tables action parameters, skbuffs, netlink attributes, module autoloading, and each registered type's variant contract. It integrates with `ip_set_getport.c`, pfxlen helpers, bitmap/hash/list modules, xt_set/SET target users, and `ipset(8)`.

## Risks

Concurrency and lifetime are the main risks. Set arrays are RCU-published and can grow; references must be balanced across packet path, netlink dumps, destroy, and namespace teardown. The nfnetlink mutex serializes userspace structural operations, but kernel packet operations can race resize and destroy. Extension layout is shared with every type, so changes to `ip_set_elem_len` or extension order can corrupt stored elements. Type autoload drops and reacquires locks, so retry paths must be correct. Restore-line error rewriting copies netlink payloads and requires strict bounds handling.

## Test Signals

Exercise all nfnetlink commands, including batch add/delete with line numbers, list/save dumps with small skb sizes, resize retries, set array growth past the initial maximum, module autoload, namespace teardown, legacy getsockopt operations, comments/counters/skbinfo/timeouts, concurrent packet matching during create/destroy/swap/resize, and lockdep/KASAN/KCSAN runs.
