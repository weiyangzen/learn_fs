<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_flavors_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_flavors_test.sh

## Purpose

`srv6_end_flavors_test.sh` tests SRv6 End behavior with the PSP flavor. It builds a four-router IPv6 topology, installs inline SRv6 policies, and verifies that PSP behaves like normal End when not penultimate and pops the SRH when it is penultimate.

## Important APIs, Types, and Functions

The script defines namespace naming helpers using a random suffix, topology helpers (`create_router`, `create_host`, `add_link_rt_pairs`, `get_network_prefix`), SRv6 helpers (`setup_rt_local_sids`, `__setup_rt_policy`, `setup_rt_policy_ipv6`), host/router setup, connectivity checks, and feature probes (`test_iproute2_supp_or_ksft_skip`, `test_kernel_supp_or_ksft_skip`, `test_dummy_dev_or_ksft_skip`). It uses `encap seg6local action End`, `End flavors psp`, and `encap seg6 mode inline`.

## Control Flow

Preflight requires root and tools `ip`, `ping`, `sysctl`, `grep`, `cut`, `sed`, `sort`, and `xargs`, plus dummy and PSP support in iproute2/kernel. Setup creates routers 1-4, hosts 1-2, full inter-router veth links, host links, local SID tables, and two policies: host 1 to 2 traverses rt3, rt4 with PSP but not penultimate, and rt2 with PSP as penultimate; host 2 to 1 uses rt1 PSP as penultimate. It then runs all-pairs router connectivity, host-gateway checks, and host-to-host SRv6 checks.

## State and Persistence Behavior

All namespaces have a unique suffix and are removed in `cleanup`. `SETUP_ERR` controls whether cleanup exits skip when setup fails. Routes, dummy devices, proxy NDP, and sysctls are namespace-local.

## Dependencies and Integration Points

It depends on SRv6 End, PSP flavor support, inline SRH insertion, dummy devices, IPv6 forwarding, and iproute2 flavor syntax. It integrates with kernel SRH processing and PSP header-removal semantics.

## Risks and Edge Cases

Because the test checks reachability rather than packet capture, it infers PSP behavior from successful forwarding. It does not directly inspect whether the SRH was removed. Setup uses `set -e`, so unexpected command failure routes to cleanup as skip before tests run.

## Test Signals

Success includes all router pair pings, host-to-gateway pings, and bidirectional host pings over PSP policies. Preflight skip messages distinguish missing userspace or kernel PSP support from behavioral failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/srv6_end_flavors_test.sh -->
