# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/bonding/lag_lib.sh

Purpose: Shared LAG helper library for bonding/team cleanup and recovery tests.

Important APIs/functions: `test_LAG_cleanup()`, `lag_setup2x2()`, `lag_cleanup()`, `lag_setup_network()`, `lag_reset_network()`, `create_bond()`, `test_bond_recovery()`, global `NAMESPACES`, dummy/veth creation, bridge setup, and connectivity checks.

Control flow: `test_LAG_cleanup()` creates bonding or team LAG devices over dummy slaves, adds IPv6/multicast addresses, then verifies addresses added to slaves are removed after LAG teardown. Recovery helpers create a two-host/two-link topology, reset a bond with caller-supplied options, force link changes, and verify traffic recovers after updelay scenarios.

State and persistence: Tracks namespaces in `NAMESPACES`, creates temporary links/bridges/bonds/team devices, and removes them in cleanup.

Dependencies and integration points: Shared by mode recovery scripts. Requires bonding, optionally team, dummy/veth/bridge, IPv6, and common net selftest assertions.

Risks and test signals: A helper failure affects recovery scripts. Tests reveal LAG address-list leaks, bond recovery timing regressions, or cleanup failures.
