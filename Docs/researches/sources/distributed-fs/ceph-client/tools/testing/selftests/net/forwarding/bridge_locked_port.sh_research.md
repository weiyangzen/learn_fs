# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/bridge_locked_port.sh

## Purpose
`bridge_locked_port.sh` tests bridge locked-port behavior and MAC Authentication Bypass (MAB). It verifies that locked ports block traffic until authorized by an FDB entry, that VLAN and IPv6 cases behave like IPv4, and that MAB-created locked FDB entries have correct lifecycle, roaming, configuration, flush, and redirect behavior.

## Important APIs, Functions, and Types
The script sources forwarding `lib.sh` and uses `ip`, `bridge`, `tc`, `$MZ`, `ping_do`, `ping6_do`, `vlan_create`, `vlan_destroy`, `mac_get`, `check_locked_port_support`, and `check_port_mab_support`. The topology has two hosts and two switch ports under VLAN-filtering bridge `br0`; `swp1` starts with learning disabled. Host helpers create IPv4/IPv6 addresses and VLAN subinterfaces for VLAN 100 tests.

## Control Flow
After setup, `tests_run` dispatches eight tests. `locked_port_ipv4()`, `locked_port_ipv6()`, and `locked_port_vlan()` confirm baseline connectivity, enable `locked on`, verify traffic fails without a static FDB entry, add a static entry for the host MAC, and verify traffic succeeds. `locked_port_mab()` enables learning, locked mode, and MAB, verifies a locked FDB entry is created by denied traffic, then replaces it with a static entry to authorize traffic. `locked_port_mab_roam()` checks that a locked entry can roam to an unlocked port but cannot roam back to a locked one. `locked_port_mab_config()` enforces that MAB requires both `locked on` and learning enabled. `locked_port_mab_flush()` ensures disabling MAB flushes only locked entries on that port. `locked_port_mab_redirect()` verifies tc mirred redirection can pass traffic from a locked port without creating locked entries until the redirect filter is removed.

## State and Persistence
The script creates `br0`, enslaves two switch ports, configures VLAN 100 as needed, toggles bridge link attributes (`learning`, `locked`, `mab`), adds and removes static and locked FDB entries, and installs a temporary tc `clsact` filter for redirection. Cleanup tears down bridge, VLANs, host addresses, and VRFs.

## Dependencies and Integration Points
It depends on forwarding `lib.sh`, bridge locked-port support, bridge MAB support for MAB tests, VLAN filtering, tc flower/mirred for redirect, and mausezahn for synthetic source MAC injection. Unsupported locked or MAB features are skipped per test through library support checks.

## Risks
The bridge port state is mutable across tests, so failure to restore `learning`, `locked`, or `mab` could affect later cases. Tests use command substitution with backticks for `mac_get`, which is functional but fragile if a helper emits extra text. MAB learning and roam checks depend on timely FDB updates after synthetic traffic. The redirect test must remove tc filters and qdiscs or it can perturb following bridge tests.

## Test Signals
Signals include pings succeeding before locking, failing while locked without FDB authorization, succeeding after static FDB authorization, locked FDB entries appearing with the `locked` marker under MAB, replacement removing the `locked` marker, allowed roam to unlocked ports, denied roam to locked ports, rejected invalid MAB configurations, selective flush of locked entries when MAB is disabled, and no locked entry for redirected traffic until redirection is removed.
