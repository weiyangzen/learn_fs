# sources/distributed-fs/ceph-client/tools/net/ynl/tests/rt-addr.sh

Purpose: wrapper for the `rt-addr` C selftest. It creates the netdevsim device and configured addresses needed by `rt-addr.c`.

Control flow/state: sources `ynl_nsim_lib.sh`, calls `nsim_setup`, and runs the local `rt-addr` binary. The helper installs cleanup for the netdevsim device.

Dependencies/integration: needs root privileges, netdevsim, IPv6, `iproute2`, `udevadm`, and the compiled test binary. The helper assigns exactly the IPv4/IPv6 addresses that the C test searches for.

Risks/test signals: if the wrapper succeeds but the C test misses addresses, likely signals generated rtnetlink address parsing or dump filtering problems.
