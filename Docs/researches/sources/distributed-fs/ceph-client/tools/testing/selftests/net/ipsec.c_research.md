# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ipsec.c

Purpose: Large XFRM/IPsec selftest that creates paired network namespaces connected by veth, drives UDP traffic through plain and XFRM tunnel paths, and validates XFRM state, policy, SPI, acquire, expire, and SPD info netlink behavior.

Important APIs and types: Uses raw netlink `NETLINK_ROUTE` and `NETLINK_XFRM`, `RTM_NEWLINK`, `RTM_NEWADDR`, `RTM_NEWROUTE`, `XFRM_MSG_NEWSA`, `NEWPOLICY`, `DELSA`, `DELPOLICY`, `ALLOCSPI`, `ACQUIRE`, `EXPIRE`, `POLEXPIRE`, `NEWSPDINFO`, `GETSPDINFO`, `struct xfrm_desc`, `struct test_desc`, pipes with `O_DIRECT`, socketpairs, netns file descriptors, `setns`, `unshare`, and kselftest reporting.

Control flow: `main` parses process count, creates three net namespaces, veth pairs, child workers, a test-plan pipe, and a result pipe. `write_test_plan` emits compatibility tests plus AH, COMP, and ESP algorithm combinations. Each child switches to one namespace, reads descriptors, coordinates with a grandchild in the peer namespace over a socketpair, and executes the selected action. Tunnel tests first verify UDP reachability, install policies and states on both ends, verify XFRM state dumps, retest through tunnel source addresses, then delete state and policy. Compatibility actions test SPI allocation, acquire multicast monitoring, state/policy expire messages, and SPD threshold attributes.

State and persistence: Runtime state includes namespace file descriptors, veth devices, XFRM states and policies, randomized keys/payload buffers, and IPC pipes. It relies on process exit and netns lifetime for cleanup rather than named namespace deletion.

Dependencies and integration: Requires root or capabilities, XFRM algorithms, veth, netlink UAPI compatibility, and enough process capacity for requested workers.

Risks: The harness is concurrency-heavy and sensitive to partial pipe messages, netlink sequence handling, missing crypto algorithms, and ABI struct-size differences. Some algorithm lists are intentionally disabled with `#if 0`.

Test signals: kselftest plan equals `proto_plan + compat_plan`; each result line reports pass/fail for descriptor type, protocol, and algorithms. Failures identify tunnel setup, data-path loss, netlink ABI regression, or unsupported algorithms.
