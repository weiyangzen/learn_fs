<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/helpers.go -->
# sources/cloud-native/moby/integration/network/helpers.go

Purpose: Linux-oriented helper functions for network integration tests, covering dummy/VLAN link setup, link existence assertions, and network-list comparisons.

Important APIs/types/functions: `CreateMasterDummy`, `CreateVlanInterface`, `DeleteInterface`, `LinkExists`, `LinkDoesntExist`, `IsNetworkAvailable`, and `IsNetworkNotAvailable`.

Control flow: link helpers shell out through `testutil.RunCommand` to `ip link` and `iptables`, asserting expected success/failure with `icmd`. Network comparison helpers return gotest comparison closures that call `NetworkList`, scan by network name, and return success or descriptive failure.

State/persistence: mutates host network interfaces and flushes iptables nat/filter tables in `DeleteInterface`. Network comparisons are read-only API calls.

Dependencies/integration: Linux `ip` and `iptables` tools, Docker `client.NetworkAPIClient`, `testutil`, `icmd`, and gotest comparison API. Macvlan/ipvlan/mixed-network tests rely on these helpers.

Risks: flushing iptables is broad and can affect other tests if used outside isolated contexts. Link names are hard-coded by callers and can collide if cleanup fails. Helpers assume Linux command output/exit codes.

Test signals: indirect coverage from macvlan, ipvlan, and mixed bridge/ipvlan tests that create dummy parents, VLAN subinterfaces, and assert network presence.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/helpers.go -->
