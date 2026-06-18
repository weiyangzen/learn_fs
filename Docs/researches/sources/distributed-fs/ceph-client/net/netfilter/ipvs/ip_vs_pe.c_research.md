# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_pe.c

## Purpose
Provides the registry for IPVS persistence engines. Persistence engines extract and compare protocol-specific persistence keys, such as SIP Call-ID, so IPVS templates can be keyed by data other than the client address.

## Important APIs, Types, and Functions
`__ip_vs_pe_getbyname()` looks up a persistence engine under RCU and takes a module reference. `ip_vs_pe_getbyname()` adds module autoload via `request_module("ip_vs_pe_%s", name)`. `register_ip_vs_pe()` and `unregister_ip_vs_pe()` add and remove engines from the global RCU list and adjust the IPVS module use count. The list is protected by `ip_vs_pe_mutex`.

## Control Flow
Consumers request an engine by name; the registry scans the RCU list and tries `try_module_get()` before returning a matching engine. If not found, module autoload is attempted and lookup repeats. Registration rejects duplicate names and links the engine with `list_add_rcu()`. Unregistration removes with `list_del_rcu()` and decrements the IPVS use count; callers are expected to synchronize RCU on module exit.

## State and Persistence
Global state is the `ip_vs_pe` list and module reference counts. No per-netns state is stored here. Registered engines persist until their module unregisters.

## Dependencies and Integration Points
Depends on Linux module reference counting, RCU list traversal, mutexes, and `ip_vs_use_count_inc/dec()`. It integrates with service configuration, connection template lookup, sync processing, and protocol-specific PE modules such as `ip_vs_pe_sip.c`.

## Risks
Callers must release returned engines with `ip_vs_pe_put()` or equivalent module put. Unregister does not validate list membership in this file, so registry users must obey lifecycle ordering. RCU grace periods are handled by provider modules, not centrally. Duplicate-name detection is the main consistency check.

## Test Signals
Load and unload a persistence engine, request it by name before and after module autoload, register duplicate names and expect failure, and verify module refcounts prevent unloading while an engine is in use.
