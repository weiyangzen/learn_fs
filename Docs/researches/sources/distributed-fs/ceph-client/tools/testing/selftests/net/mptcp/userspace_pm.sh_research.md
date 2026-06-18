# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/userspace_pm.sh

## Purpose
`userspace_pm.sh` validates the userspace MPTCP path-manager API and event stream with long-lived IPv4 and IPv6 connections. It checks sysctl mapping, ADD_ADDR/RM_ADDR commands, CREATE_SUBFLOW/DESTROY_SUBFLOW commands, mixed IPv4-on-IPv6 subflows, MP_PRIO signaling, and listener-created/listener-closed events.

## Important APIs, Types, And Functions
The script sources `mptcp_lib.sh`, uses event constants, and drives `pm_nl_ctl ann`, `rem`, `csf`, `dsf`, `set`, `listen`, and `events`. Key functions are `cleanup()`, `make_connection()`, `check_expected()`, `verify_announce_event()`, `test_announce()`, `verify_remove_event()`, `test_remove()`, `verify_subflow_events()`, `test_subflows()`, `test_subflows_v4_v6_mix()`, `test_prio()`, `verify_listener_events()`, and `test_listener()`.

## Control Flow
After feature checks, the script verifies the legacy `path_manager` sysctl maps correctly to `pm_type`, enables userspace PM in two namespaces, builds one veth link with two IPv4 and two IPv6 addresses per side, starts `pm_nl_ctl events` in both namespaces, and creates one persistent IPv4 and one persistent IPv6 MPTCP connection using `mptcp_connect`. `make_connection()` extracts tokens, source ports, `server_side`, and `deny_join_id0` attributes from event files. Test sections then send invalid and valid announces/removals, verify event attributes on the peer, create and destroy subflows in both directions and both families, exercise a v4 subflow on a v6 MPTCP connection, send a userspace MP_PRIO flag update, and verify listener lifecycle events.

## State, Persistence, And Dependencies
State includes two namespaces, two long-lived MPTCP connections, background client/server `mptcp_connect` processes, event log temp files, a random payload file, PM tokens parsed from events, dynamic address ids, and fixed application/new ports. Cleanup kills all background processes, removes namespaces, and deletes temp files. Dependencies are MPTCP support, `/proc/sys/net/mptcp/pm_type`, `/proc/kallsyms`, `ip`, `mptcp_connect`, `pm_nl_ctl`, and PM event support for listener tests.

## Integration Points
The test is a standalone counterpart to the userspace-PM block inside `mptcp_join.sh`. It exercises the kernel's userspace PM netlink commands through `pm_nl_ctl.c` and validates event parsing helpers in `mptcp_lib.sh`. It also confirms the `path_manager=userspace|kernel` sysctl compatibility path when present.

## Risks
The script relies on sleeps after netlink operations rather than robust waits for every event, which can be fragile on slow systems. It parses the first matching event from temp files, so stale events must be cleared carefully. Random two-digit ids can theoretically collide with existing values if setup changes. `make_connection()` appears to wait for `${port}` even though it sets `app_port`, so correctness depends on the shared wait helper tolerating the value or the listener being ready by the following sleep in the observed environment.

## Test Signals
Pass signals are TAP entries for namespace setup, connection establishment with valid tokens and flags, expected announce/remove/subflow/listener event attributes, and expected MP_PRIO MIB counters. Failures identify missing userspace PM support, malformed or absent events, invalid token handling regressions, incorrect address ids/ports/families, or nonzero final return status.
