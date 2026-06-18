# sources/distributed-fs/ceph-client/net/sysctl_net.c

## Purpose
This file provides the network namespace aware sysctl root for `/proc/sys/net` and helpers for registering per-netns networking sysctl tables safely.

## Important APIs, Types, And Functions
Important functions are `net_ctl_header_lookup()`, `is_seen()`, `net_ctl_permissions()`, `net_ctl_set_ownership()`, `net_sysctl_init()`, `ensure_safe_net_sysctl()`, `register_net_sysctl_sz()`, and `unregister_net_sysctl_table()`. The file defines `net_sysctl_root`, pernet operations for sysctl set lifecycle, and a global `net_header` for the top-level `/proc/sys/net` directory.

## Control Flow
Boot-time `net_sysctl_init()` registers an empty top-level `net` sysctl directory outside network namespaces, then registers pernet sysctl setup. Each net namespace initializes `net->sysctls` with a root that resolves lookups to the current task's net namespace. When a table is registered for a non-init netns, `ensure_safe_net_sysctl()` scans writable entries and downgrades any entry whose data pointer targets kernel or module global data.

## State And Persistence
Per namespace state lives in `struct net.sysctls`; ownership is mapped to root inside the namespace user namespace. Sysctl registrations persist until unregistered or namespace teardown. Permission checks dynamically grant network administrators in the namespace root-like access bits for sysctl entries.

## Dependencies And Integration Points
The file depends on sysctl core, net namespaces, user namespaces, capabilities, and kernel/module address classification helpers. It exports `register_net_sysctl_sz()` and `unregister_net_sysctl_table()` for networking subsystems.

## Risks And Test Signals
Risks include unsafe writable sysctls sharing global data across net namespaces, incorrect permission mapping in user namespaces, and registration after namespace teardown. Test signals include creating non-init netns and registering writable per-net sysctls, verifying global-data warnings and write-bit stripping, checking `/proc/sys/net` ownership in user namespaces, and namespace create/destroy leak checks.
