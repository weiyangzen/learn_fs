<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mroute6.h -->
# sources/distributed-fs/ceph-client/include/linux/mroute6.h

## Purpose
`mroute6.h` declares IPv6 multicast routing interfaces and IPv6-specific MFC cache entries built on `mroute_base.h`.

## Important APIs, Types, and Functions
It defines `ip6_mroute_opt()`, `ip6_mroute_setsockopt()`, `ip6_mroute_getsockopt()`, `ip6_mr_input()`, `ip6mr_compat_ioctl()`, `ip6_mr_init()`, `ip6_mr_output()`, `ip6_mr_cleanup()`, `ip6mr_ioctl()`, `ip6mr_rule_default()`, `VIFF_STATIC`, `struct mfc6_cache_cmp_arg`, `struct mfc6_cache`, `MFC_ASSERT_THRESH`, `ip6mr_get_route()`, `mroute6_is_socket()`, `ip6mr_sk_done()`, and `ip6mr_sk_ioctl()`. Stubs preserve normal IPv6 output when multicast routing is disabled.

## Control Flow and State
IPv6 multicast socket options/ioctls configure routing tables. Input and output hooks route multicast packets through MFC/VIF state when enabled; disabled output falls back to `ip6_output()`. `ip6mr_sk_ioctl()` copies UAPI request structs through `sock_ioctl_inout()` for supported commands.

## State and Persistence Behavior
Runtime state resides in per-net IPv6 multicast routing tables, shared base MFC/VIF structures, and socket associations. The header adds IPv6 address keys and assert-throttle timing.

## Dependencies and Integration Points
It depends on IPv6 networking, PIM, skbuffs, net namespaces, fib rules, sockptr, UAPI mroute6, and shared multicast routing base code.

## Risks
IPv6 disabled stubs must avoid breaking normal output. Usercopy ioctl wrappers must use correct request sizes. Multi-table rule defaults depend on config. MFC key layout must match rhashtable comparison code.

## Test Signals
IPv6 multicast forwarding, PIM daemon operations, ioctl compatibility tests, route dumps, disabled-config output tests, multi-table rules, and assert rate-limiting behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mroute6.h -->
