# sources/distributed-fs/ceph-client/tools/testing/selftests/net/test_vxlan_fdb_changelink.sh

## Purpose
`test_vxlan_fdb_changelink.sh` verifies VXLAN FDB behavior across `ip link set` changes. It checks that multiple default remote FDB entries survive changing the VXLAN remote and that multicast group membership updates correctly when the remote changes between multicast and unicast.

## Important APIs, Types, And Functions
Functions include `check_remotes()`, `test_set_remote()`, `fmt_remote()`, `change_remote()`, `check_membership()`, and `test_change_mc_remote()`. It uses `lib.sh` helpers such as `adf_ip_link_add`, `adf_ip_link_set_up`, `check_err`, `check_err_fail`, `check_command`, `tests_run`, and deferred cleanup.

## Control Flow
`test_set_remote()` creates a VXLAN device, appends two all-zero FDB default remote entries, changes the device remote to one of them with `ip link set`, and checks that two default remotes remain. `test_change_mc_remote()` creates a veth underlay and a VXLAN with multicast remote `224.1.1.1`, checks netstat group membership, changes the remote to `224.1.1.2`, checks membership moved, then changes to unicast `192.0.2.2` and checks no multicast membership remains.

## State, Persistence, And Dependencies
State is temporary links, VXLAN devices, FDB entries, multicast memberships, and deferred cleanup scopes from `lib.sh`. It depends on `ip`, `bridge`, and `netstat` for the multicast test. No persistent files are written.

## Integration Points
The test exercises VXLAN changelink paths and their effect on bridge FDB default remotes and IGMP/multicast group join/leave state on the underlay device.

## Risks
`check_remotes()` counts all-zero FDB rows and can be confused by unexpected entries on a non-isolated device name, though the helper-created device should be scoped. Multicast membership parsing depends on `netstat -n --groups` output format. The multicast test skips if `netstat` is unavailable.

## Test Signals
Passing signals are two default-remotes after append and after link-set, membership in only the configured multicast group after creation and MC-to-MC change, and no listed test groups after MC-to-unicast change.
