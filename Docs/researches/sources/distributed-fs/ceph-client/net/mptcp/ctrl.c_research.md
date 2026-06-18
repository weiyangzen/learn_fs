<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/ctrl.c -->
# sources/distributed-fs/ceph-client/net/mptcp/ctrl.c

## Purpose
Provides per-network-namespace MPTCP control state, sysctls, default scheduler/path-manager selection, active blackhole detection/backoff, and MPTCP subsystem initialization.

## Important APIs, Types, and Functions
`struct mptcp_pernet` stores sysctl-controlled namespace state. Getter APIs include `mptcp_is_enabled()`, `mptcp_get_add_addr_timeout()`, `mptcp_is_checksum_enabled()`, `mptcp_allow_join_id0()`, `mptcp_stale_loss_cnt()`, `mptcp_close_timeout()`, `mptcp_get_pm_type()`, `mptcp_get_path_manager()`, and `mptcp_get_scheduler()`. Sysctl handlers include scheduler/path-manager setters, available-list readers, `proc_pm_type()`, and blackhole timeout reset. Active fallback logic is in `mptcp_active_disable()`, `mptcp_active_should_disable()`, `mptcp_active_enable()`, and `mptcp_active_detect_blackhole()`. Initialization uses `mptcp_init()` and optionally `mptcpv6_init()`.

## Control Flow
Namespace init sets defaults and registers `/proc/sys/net/mptcp` entries. Sysctl writes validate scheduler/path-manager names against registered ops and keep `pm_type` and `path_manager` synchronized for kernel/userspace managers. Blackhole detection observes repeated SYN retransmissions for active MP_CAPABLE attempts, triggers fallback, records a disable timestamp/count, and applies exponential active-MPTCP disable windows capped at 64 times the configured timeout. Successful non-loopback active MPTCP connections reset disable count.

## State and Persistence
State is per-netns and persists for the namespace lifetime: enable flags, checksum setting, join-id0 allowance, stale loss count, close timeout, blackhole timeout, SYN retrans threshold, active-disable timestamp/counter, scheduler string, path-manager string, and PM type. Sysctl writes are runtime configuration, not durable across boot unless user space persists them.

## Dependencies and Integration Points
Depends on netns generic storage, sysctl, MPTCP scheduler/path-manager registries, MIB stats, TCP retransmission state, destination device lookup, and core protocol init. It integrates with connection setup, fallback, path manager, scheduler selection, and `/proc/sys/net/mptcp` user controls.

## Risks
Scheduler/path-manager string writes must validate under RCU or leave stale configuration. `pm_type` and `path_manager` can diverge if future names are added without updating the mapping logic. Blackhole detection relies on memory ordering between timestamp and atomic disable count. Loopback success intentionally does not reset blackhole state; changing that can mask real network middlebox failures. Non-init netns sysctl table copies must be freed correctly.

## Test Signals
Signals include sysctl read/write validation, available scheduler/path-manager lists, switching between kernel and userspace PM, active MP_CAPABLE SYN drop fallback, exponential blackhole timeout behavior, reset after successful non-loopback MPTCP, IPv6 init with `CONFIG_MPTCP_IPV6`, and per-netns isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/ctrl.c -->
