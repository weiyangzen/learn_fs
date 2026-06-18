# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipv6_flowlabel.sh

Purpose: Orchestrates IPv6 flowlabel management and datapath tests in separate network namespaces to avoid flowlabel database conflicts.

Important commands: Runs `./in_netns.sh ./ipv6_flowlabel_mgr`, then several `./in_netns.sh sh -c ... ./ipv6_flowlabel` invocations with sysctls for `auto_flowlabels`, `flowlabel_reflect`, and `ping_group_range`.

Control flow: The script first tests management behavior. It then runs datapath tests with auto flowlabels disabled, auto flowlabels enabled, ping sockets with reflection, `IPV6_FLOWINFO_SEND`, and ping sockets plus flowinfo-send. `set -e` stops on the first failure.

State and persistence: Each test gets a fresh temporary namespace. Sysctl changes are namespace-local. No persistent output is written.

Dependencies and integration: Depends on `in_netns.sh`, compiled `ipv6_flowlabel` and `ipv6_flowlabel_mgr`, and kernel support for ping sockets and flowlabel sysctls.

Risks: Sysctl availability varies by kernel. The script isolates cases but also repeats namespace creation many times, so failures can be environmental.

Test signals: Final `OK. All tests passed` means management and all datapath variants completed successfully.
