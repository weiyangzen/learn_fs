<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/bridge_linux_test.go -->
# sources/cloud-native/moby/integration/network/bridge/bridge_linux_test.go

Purpose: Linux bridge-driver integration suite covering network creation semantics, IPAM, gateway modes, firewall policy/backend behavior, port mappings, legacy links, live daemon restarts, API compatibility, and rollback after failed joins.

Important APIs/types/functions: tests use the Moby API client, `integration/internal/network` creation options, `integration/internal/container` helpers, `daemon.Daemon`, bridge driver labels/options, `netlink`/`nlwrap`, and `networking` firewall/L3 helpers. Key tests include `TestCreateWithMultiNetworks`, IPv6 ULA/default-option tests, `TestFilterForwardPolicy`, `TestPointToPoint`, `TestIsolated`, custom-ifname, port-binding, firewalld, legacy-link, backend-switch, IPAM status, join-error, and preferred-subnet-restore scenarios.

Control flow: most tests start from `setupTest`, create or restart daemons with specific flags, create bridge networks with driver/IPAM/options, run containers, inspect network/container state, and assert routes, addresses, port maps, firewall rules, or daemon startup outcomes. Firewall tests build isolated `L3Segment` namespaces, start daemons inside them with OTLP disabled, mutate sysctls/policies, and compare expected iptables/ip6tables/nftables cleanup. Port-binding tests create containers under old/new API versions and, for old-container compatibility, stop the daemon, tamper on-disk container config, restart, and inspect backfilled bindings.

State/persistence: heavily exercises persisted network configuration across daemon restart (`PreferredSubnetRestore`, port mapping restore, live restore), container config backfilling, bridge IPAM counters, host firewall rules/chains/tables, sysctls, netlink bridge devices, and firewalld reload state. Cleanup removes networks/containers and sometimes starts a fresh daemon to clear docker0 rules.

Dependencies/integration: integrates Docker API types, libnetwork bridge labels, daemon test harness, netlink, host `iptables`, `ip6tables`, `nft`, `firewall-cmd`, `ip`, and BusyBox images. API-version gates guard features such as multi-network create and gateway priority/status fields.

Risks: tests require privileged Linux networking and are sensitive to rootless, firewalld, firewall backend, IPVS, and kernel behavior. Hard-coded subnets, ports like `8000`, and bridge names can collide if cleanup fails. Several tests intentionally manipulate global firewall state; failed cleanup can poison later tests. The suite also encodes API compatibility details such as port-binding backfill warnings, so version changes must update assertions carefully.

Test signals: asserts include network inspect IPAM config/status, route table contents, firewall rule existence/removal, daemon startup failure/success, service/container reachability, port map shape, custom interface names, and exact rollback after join error. Skips and TODOs document known gaps, including API 1.53 port-binding behavior and a firewalld/IPv6 isolated XFAIL.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/bridge_linux_test.go -->
