# sources/distributed-fs/ceph-client/net/ipv6/addrconf_core.c

## Purpose
`addrconf_core.c` contains small IPv6 address-configuration primitives that must remain available to static components even when the full IPv6 module is not configured or loaded. It exports core address classification, address notifier chains, well-known IPv6 constants, an optional FIB6 flush hook, and final `inet6_dev` destruction.

## Important APIs, Types, and Functions
- `void (*__fib6_flush_trees)(struct net *)`: exported function pointer used by XFRM or other code to request IPv6 route tree flushes when full IPv6 registers an implementation.
- `__ipv6_addr_type(const struct in6_addr *addr)`: exported classifier returning `IPV6_ADDR_*` type and encoded scope bits for multicast, link-local, site-local, ULA, compatible IPv4, mapped IPv4, loopback, unspecified, and global unicast addresses.
- `register_inet6addr_notifier()`, `unregister_inet6addr_notifier()`, `inet6addr_notifier_call_chain()`: exported atomic notifier chain for address lifecycle events.
- `register_inet6addr_validator_notifier()`, `unregister_inet6addr_validator_notifier()`, `inet6addr_validator_notifier_call_chain()`: exported blocking notifier chain used before address creation so validators can veto or annotate errors.
- Exported constants: `in6addr_loopback`, `in6addr_any`, `in6addr_linklocal_allnodes`, `in6addr_linklocal_allrouters`, `in6addr_interfacelocal_allnodes`, `in6addr_interfacelocal_allrouters`, and `in6addr_sitelocal_allrouters`.
- `in6_dev_finish_destroy()`: exported final destroy path for `struct inet6_dev`; it validates that address/multicast/timer state is gone, drops the netdevice reference, marks alive-free bugs, and schedules RCU freeing.

## Control Flow
- Address classification is a straight decision tree over the leading address bits and special low-word forms. It returns early for broad global-unicast prefixes, multicast with multicast scope, link/site local, ULA, unspecified, loopback, IPv4-compatible, and IPv4-mapped forms.
- Notifier registration functions delegate to kernel atomic/blocking notifier helpers; `addrconf.c` invokes the validator chain during blocking address add and invokes the atomic chain on address up/down notifications.
- `in6_dev_finish_destroy()` is called after higher-level addrconf teardown has removed addresses, multicast state, and timers. It warns on leftover state, drops the `net_device` hold, refuses to free an object not marked dead, and otherwise calls `call_rcu()` to free SNMP allocations and the `inet6_dev`.

## State and Persistence Behavior
- The file owns two static notifier heads: `inet6addr_chain` and `inet6addr_validator_chain`.
- It exports immutable aligned `struct in6_addr` constants for common protocol addresses.
- Device destruction frees memory only after RCU grace period via `in6_dev_finish_destroy_rcu()`, including per-device IPv6, ICMPv6, and ICMPv6 message MIB allocations. No persistent storage is involved.

## Dependencies and Integration Points
- Used by `addrconf.c`, `af_inet6.c`, routing, XFRM, tunnel, and transport code needing IPv6 address type tests and well-known addresses.
- Includes only core networking headers (`ipv6.h`, `addrconf.h`, `ip.h`) so these symbols are available to static/non-module pieces.
- The validator notifier is an integration point for subsystems that must reject address assignment before `inet6_ifaddr` allocation is committed.

## Risks and Edge Cases
- `__ipv6_addr_type()` is a foundational classifier; any change to masks or scope encoding affects source selection, bind validation, addrlabel matching, routing, and DAD behavior.
- The classifier treats ULAs (`fc00::/7`) as global scope per RFC 4193. That can be surprising but is intentional for address-selection scope.
- Destroy path warnings indicate lifecycle bugs elsewhere. Freeing an `inet6_dev` not marked dead intentionally leaks/returns after warning rather than freeing active state.
- Notifier chains differ intentionally: validators are blocking and may sleep; lifecycle notifications are atomic.

## Test Signals
- Unit-style address classification vectors for `::`, `::1`, `::ffff:0:0/96`, `::/96`, `ff00::/8` scopes, `fe80::/10`, `fec0::/10`, `fc00::/7`, and ordinary global unicast.
- Register/unregister notifier probes and verify calls on address add/delete and validator rejection propagation.
- Device teardown tests should verify no warnings with clean addrconf teardown and intentional warnings when address list, multicast list, timer, or `dead` state is wrong.
