# sources/distributed-fs/ceph-client/net/netfilter/ipset/Kconfig

## Purpose

This Kconfig file defines the IP set subsystem and its set-type modules. IP set lets userspace create named sets and lets netfilter rules match or update those sets through the `set` match and `SET` target.

## Important Symbols

`IP_SET` is a tristate menuconfig depending on `INET && NETFILTER` and selecting `NETFILTER_NETLINK`, because `ip_set_core.c` registers an nfnetlink subsystem. `IP_SET_MAX` is an integer with default `256` and range `2..65534`; it becomes the default maximum per-network-namespace set count, overridable by the `ip_set` module parameter `max_sets`.

The bitmap set types are `IP_SET_BITMAP_IP`, `IP_SET_BITMAP_IPMAC`, and `IP_SET_BITMAP_PORT`. The hash types include `IP_SET_HASH_IP`, `IP_SET_HASH_IPMARK`, `IP_SET_HASH_IPPORT`, `IP_SET_HASH_IPPORTIP`, `IP_SET_HASH_IPPORTNET`, `IP_SET_HASH_IPMAC`, `IP_SET_HASH_MAC`, `IP_SET_HASH_NETPORTNET`, `IP_SET_HASH_NET`, `IP_SET_HASH_NETNET`, `IP_SET_HASH_NETPORT`, and `IP_SET_HASH_NETIFACE`. `IP_SET_LIST_SET` enables ordered unions of other sets.

## Control Flow And State

All set-type symbols are nested under `if IP_SET`, so no type module is visible unless the core subsystem is enabled. The chosen symbols drive which type modules are compiled by the ipset Makefile. Runtime state is owned by the modules, not Kconfig, but the selected values persist in `.config` and determine what `ipset(8)` can create or autoload.

## Dependencies And Integration

This file integrates with `net/netfilter/Kconfig` through its `source` line, with `ipset/Makefile` through symbol-to-object mappings, with userspace `ipset(8)`, and with xtables/nftables consumers that reference set names and indexes. Every type depends on `IP_SET` and therefore inherits nfnetlink availability.

## Risks

The primary risk is a mismatch between configured type modules and userspace expectations. A deployment may support the core IP set API but fail to create a specific set family if its symbol is off. Another risk is raising or lowering `IP_SET_MAX`: too low can break rule restore workloads, while too high increases possible per-net allocation and lookup surface.

## Test Signals

Use build tests for `CONFIG_IP_SET=y` and `m`, plus per-type module builds. Runtime smoke tests should create, add, test, list, flush, rename, swap, and destroy representative bitmap, hash, and list sets through `ipset(8)`, then exercise xtables rules that match those sets.
