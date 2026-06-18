# sources/distributed-fs/ceph-client/net/ipv4/sysctl_net_ipv4.c

## Purpose

This file registers and validates the `/proc/sys/net/ipv4` sysctl surface for global and per-network-namespace IPv4, TCP, UDP, ICMP, IGMP, FIB, multipath, ping, CIPSO, and related networking settings. It provides custom handlers for settings that need validation, derived display values, namespace pointer adjustment, key parsing, side effects, or netevent notifications.

## Important APIs, Types, and Functions

- Bounds and constants at file scope define sysctl min/max values for port ranges, TTL, TCP retry counts, MSS, RTO, TCP PLB, ECN modes, ping group IDs, hash table sizing, and ICMP extension masks.
- `set_local_port_range()` and `ipv4_local_port_range()`: read/write ephemeral port range, enforce ordering and non-overlap with privileged ports, and warn once for same-parity endpoints.
- `ipv4_privileged_ports()`: validates `ip_unprivileged_port_start` against the current local port range.
- `inet_get_ping_group_range_table()`, `set_ping_group_range()`, and `ipv4_ping_group_range()`: expose ping socket group range with seqlock protection and user namespace GID translation.
- `ipv4_fwd_update_priority()`: writes forwarding priority sysctl and emits `NETEVENT_IPV4_FWD_UPDATE_PRIORITY_UPDATE`.
- Congestion-control handlers: `proc_tcp_congestion_control()`, `proc_tcp_available_congestion_control()`, and `proc_allowed_congestion_control()`.
- TCP Fast Open handlers: `sscanf_key()`, `proc_tcp_fastopen_key()`, and `proc_tfo_blackhole_detect_timeout()`.
- Read-only derived handlers: `proc_tcp_available_ulp()`, `proc_tcp_ehash_entries()`, and `proc_udp_hash_entries()`.
- Multipath handlers under `CONFIG_IP_ROUTE_MULTIPATH`: `proc_fib_multipath_hash_policy()`, `proc_fib_multipath_hash_fields()`, `proc_fib_multipath_hash_init_rand_seed()`, `proc_fib_multipath_hash_set_seed()`, and `proc_fib_multipath_hash_seed()`.
- `ipv4_table[]`: init-net/global sysctls such as orphan limits, inet peer settings, `tcp_mem`, CIPSO, available ULP, `udp_mem`, and FIB sync memory.
- `ipv4_net_table[]`: large per-net sysctl table for ICMP, ping, ECN, demux, TTL, ports, PMTU, bind behavior, TCP tuning, syncookies, multipath, UDP, FIB notifications, PLB, and RTO settings.
- `ipv4_sysctl_init_net()` / `ipv4_sysctl_exit_net()`: per-net registration and cleanup.
- `sysctl_ipv4_init()`: initcall that registers init-net global table, initializes multipath random seed, and registers per-net sysctl operations.

## Control Flow

At boot, `sysctl_ipv4_init()` registers `ipv4_table` under `net/ipv4` for `init_net`, initializes the multipath seed helper, and registers `ipv4_sysctl_ops`. For each network namespace, `ipv4_sysctl_init_net()` either uses the static `ipv4_net_table` for `init_net` or duplicates it for child namespaces. In child namespaces it adjusts every non-null `.data` pointer from `init_net` storage to the current `struct net`, while entries with no data pointer are treated as global views and made read-only. The table is registered under `net/ipv4`, local reserved port bitmap storage is allocated, and multipath hash seed state is initialized.

On sysctl reads and writes, generic handlers handle most scalar values with min/max enforcement. Custom handlers copy current state into temporary storage, call the generic parser, then commit only valid updates. Some writes trigger side effects: local port range updates use `WRITE_ONCE()`, ping group writes use a seqlock, TFO timeout resets active blackhole disable counters, multipath hash changes notify listeners through `NETEVENT_IPV4_MPATH_HASH_UPDATE`, and forwarding priority changes notify route users.

On namespace teardown, `ipv4_sysctl_exit_net()` frees the reserved port bitmap, unregisters the sysctl header, and frees the duplicated table.

## State and Persistence Behavior

Most state is stored in `struct net.ipv4` fields, so values persist for the lifetime of the network namespace and are isolated per namespace after pointer adjustment. Some settings are global or init-net-only through `ipv4_table`. `ip_local_reserved_ports` is an allocated bitmap per namespace. Ping group range uses a seqlock-protected pair of `kgid_t`. Multipath hash seed stores both the user-provided seed and the effective seed; a zero user seed maps to a boot-random seed. TCP Fast Open key writes update cipher state rather than storing raw text in this file.

## Dependencies and Integration Points

The file integrates with the generic sysctl framework, network namespace lifecycle, TCP congestion-control registry, TCP Fast Open cipher management, TCP ULP registry, TCP and UDP hash tables, ICMP/FIB/IGMP/PING/CIPSO state, netevent notifier chains, user namespace GID conversion, seqlocks, and many `struct net.ipv4` fields consumed throughout IPv4, TCP, UDP, and routing code. The `tcp_syncookies` sysctl exposed here directly gates the syncookie path in `syncookies.c`; multipath sysctls affect route hashing in `route.c`.

## Risks and Edge Cases

- Pointer adjustment for duplicated namespace tables is broad; entries with unusual `.data` semantics, such as `.data = &init_net`, require custom handlers that understand the table layout.
- Port range and privileged port validation must remain consistent in both directions to avoid overlapping unprivileged and ephemeral ranges.
- User namespace GID conversion can produce invalid kgids; invalid or reversed ping ranges intentionally become empty.
- String handlers allocate temporary buffers; missing NUL bounds or malformed TFO keys must fail without partially replacing keys.
- Read-only derived sysctls for child namespace hash tables use negative values to signal shared global tables; tests should preserve that ABI.
- Multipath hash policy, fields, and seed updates have immediate route-selection effects and must notify route users.
- Several entries are config-gated; table shape and proc availability vary by kernel configuration.

## Test Signals

Test signals include namespace creation/destruction with sysctl registration, pointer isolation across netns, write validation for `ip_local_port_range` and `ip_unprivileged_port_start`, ping group range with user namespace mappings, congestion-control read/write permissions, TFO key parsing for one and two keys, TFO blackhole timeout counter reset, derived TCP/UDP hash entry display in init and child namespaces, multipath policy/field/seed notifications, config-gated sysctl presence, reserved port bitmap behavior, and representative min/max enforcement for TCP, ICMP, UDP, and FIB knobs.
