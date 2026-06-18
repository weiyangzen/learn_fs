# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/non_ether_header_ops.sh

Purpose: Reproduces a non-Ethernet `header_ops` stacking scenario that previously could crash when callbacks inherited the wrong `net_device` context.

Important APIs/functions: Sources net namespace helper `net/lib.sh`, uses `setup_ns`/`cleanup_all_ns`, and creates `dummy`, GRE, bond, and team devices. It triggers IPv6 MLD/report paths using address assignment and multicast ping.

Control flow: Creates namespace `ns1`, adds dummy `d0` with IPv4 address, creates GRE `g0`, bond `b0` in active-backup mode, and team `t0`. It enslaves GRE to bond and bond to team, brings all devices up, assigns IPv6 to team, then sends repeated IPv6 multicast pings on `t0`. If the kernel does not crash, it prints PASS and exits.

State and persistence: All devices live inside the temporary namespace. `trap cleanup_all_ns EXIT` removes the namespace and devices.

Dependencies and integration: Requires GRE, bonding, team, IPv6, iproute2, and namespace support. It is a crash regression rather than a packet-delivery validation.

Risks: Success is absence of a crash; the script ignores ping failures. It assumes IPv6 address assignment triggers MLD joins that call `dev_hard_header` through the stack.

Test signals: PASS output indicates the GRE-over-bond-over-team stack handled IPv6 multicast header generation without crashing or warning fatally.
