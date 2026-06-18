## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netdev-l2addr.sh

Purpose: tests link-layer address reporting and setting for `netdevsim`, including current address, broadcast address, and permanent address (`permaddr`) semantics.

Important APIs and tools: sources `lib.sh`, uses `setup_ns`, `create_netdevsim`, `create_netdevsim_port`, `cleanup_netdevsim`, `ip -j link show`, `jq`, and `ip link set ... address/brd`.

Control flow: creates a namespace and netdevsim instance, verifies `address` and `broadcast` JSON fields exist, verifies `permaddr` is absent before a permanent address is configured, changes address and broadcast to a test MAC, and re-reads JSON to assert the changes. It then verifies that creating a netdevsim port with the broadcast MAC as permanent address fails, creates a port with a valid permanent address, and confirms the `permaddr` JSON field equals the requested value.

State and persistence: creates netdevsim devices under a fixed test id (`2025`) and one namespace; trap cleanup removes both. Dependencies include netdevsim support, JSON output from iproute2, and `jq`. Risks include fixed simulator id collisions, missing netdevsim debugfs support, and `fail()` using shell `$_` for return display rather than the exact failed command status. Test signal is exit code `RET_CODE` plus stderr failure messages.
