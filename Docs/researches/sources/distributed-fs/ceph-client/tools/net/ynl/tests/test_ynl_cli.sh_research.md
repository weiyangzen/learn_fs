# sources/distributed-fs/ceph-client/tools/net/ynl/tests/test_ynl_cli.sh

Purpose: KTAP shell selftest for the generic Python YNL CLI (`pyynl/cli.py`). It validates family listing and operations across netdev, ethtool, rtnetlink route/address/link/neigh/rule, and nlctrl.

Important functions: `cli_list_families`, `cli_netdev_ops`, `cli_ethtool_ops`, `cli_rt_route_ops`, `cli_rt_addr_ops`, `cli_rt_link_ops`, `cli_rt_neigh_ops`, `cli_rt_rule_ops`, and `cli_nlctrl_ops` each run CLI commands and assert output with grep or command exit status. `setup()` loads netdevsim, creates a temporary netns, adds a netdevsim device, renames it, brings it up, and creates a veth pair. `cleanup()` removes the device and namespace.

Control flow/state: the script checks the CLI path, traps cleanup, prints KTAP header, runs setup, sets a fixed plan, then executes all tests. It mutates netns routes, addresses, links, neighbors, and rules and performs best-effort deletion after each case.

Dependencies/integration: needs kselftest `ktap_helpers.sh`, root privileges, iproute2, netdevsim, veth, and relevant YNL YAML families.

Risks/test signals: grep-based assertions are broad but good integration smoke tests. Family availability gates skip some rtnetlink cases. Cleanup failures can leave namespace state until trap. Strong signal for JSON request parsing, create flags, dump/do modes, and installed-vs-tree CLI path handling.
