# sources/distributed-fs/ceph-client/tools/net/ynl/tests/rt-route.sh

Purpose: wrapper for route dump testing. It prepares the netdevsim interface and addresses that induce connected routes, then runs the `rt-route` binary.

Control flow/state: sources `ynl_nsim_lib.sh`, calls `nsim_setup`, and executes the script-relative `rt-route` binary. Netdevsim cleanup is handled by the helper trap.

Dependencies/integration: requires root/network admin privileges, netdevsim, IPv6, iproute2, and compiled YNL test binary. It pairs directly with the expected route prefixes in `rt-route.c`.

Risks/test signals: wrapper success plus C failure points to route dump/parsing or kernel route behavior. Wrapper failure is usually missing module or permissions.
