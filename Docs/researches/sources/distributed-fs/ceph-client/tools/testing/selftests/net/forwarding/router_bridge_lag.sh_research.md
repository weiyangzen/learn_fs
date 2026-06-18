# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/router_bridge_lag.sh

Purpose: validates routing when both hosts and router ports are LACP team devices, with LAG2 enslaved to an 802.1Q-aware bridge and LAG3 operating as a routed interface. It exercises bridge/LAG remastering and physical slave churn.

Key APIs are shell functions `team_create`, `team_destroy`, `simple_if_init`, `__addr_add_del`, `forwarding_enable`, and local mutators `config_deslave`, `config_enslave`, `config_remaster_lag2`, and `config_remaster_lag3`. `ALL_TESTS` can be overridden, and `EXTRA_SOURCE` can inject additional behavior, making this script a reusable base for variants.

Control flow creates host LAG1/LAG4 with VRFs, router LAG2/LAG3, bridge `br1`, static routes, and addresses. The test sequence pings, detaches and reattaches each LAG slave, remasters LAG2 out of and back into the bridge, and temporarily moves LAG3 into the bridge. State is entirely kernel/teamd networking state. Risks include teamd dependency, convergence timing, overridden test lists, and leaving physical ports with changed MAC/master state after failures. Test signals are dual-stack reachability through `lag1` after each mutation and explicit `setup_wait_dev` for LAG readiness.
