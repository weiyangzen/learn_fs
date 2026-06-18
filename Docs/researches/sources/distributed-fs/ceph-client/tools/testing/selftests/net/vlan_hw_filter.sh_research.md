# sources/distributed-fs/ceph-client/tools/testing/selftests/net/vlan_hw_filter.sh

Purpose: Regression tests for VLAN ID 0 and RX VLAN hardware filter toggling on bond devices, targeting previous crash/unregister/memleak paths.

Important APIs/functions: creates a unique namespace per test, uses `ip link` for bond/veth/VLAN creation and deletion, and `ethtool -K rx-vlan-filter` toggles. `tests_run()` executes `TESTS` or all tests; `fail()` records errors.

Control flow: tests cover deleting a veth peer after VLAN 0 devices on bond/slave, deleting VLAN 0 after enabling rx-vlan-filter while bond is up/down, adding VLAN 0 after enabling filter, deleting VLAN while bond down, and deleting a bond after toggling rx-vlan-filter off. Each test calls setup and cleanup explicitly.

State and persistence: temporary namespace and devices only. Trap attempts cleanup on exit. `ret` accumulates failures.

Dependencies and integration: requires bond driver support, VLAN support, ethtool, root privileges, and iproute2.

Risks: cleanup is called both in tests and trap; errors deleting already-removed namespace are ignored. Tests detect absence of crashes indirectly through command success, not deeper leak instrumentation.

Test signals: any failed key operation calls `fail` and final exit is nonzero. Kernel crash/hang would be an external failure signal.
