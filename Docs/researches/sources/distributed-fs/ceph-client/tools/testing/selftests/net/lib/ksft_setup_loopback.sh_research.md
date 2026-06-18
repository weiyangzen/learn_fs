# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/ksft_setup_loopback.sh

## Purpose
This setup wrapper runs a kselftest over a real network interface in hardware loopback mode while isolating the actual test inside two macvlan-backed namespaces.

## Important APIs and Functions
The script is primarily linear. `cleanup` removes server/client macvlan interfaces and namespaces, disables NIC loopback with `ethtool -K`, restores `gro_flush_timeout` and `napi_defer_hard_irqs`, and exits with the original status. It exports `LOCAL_V6`, `REMOTE_V6`, `NETIF=server`, `REMOTE_TYPE=netns`, and `REMOTE_ARGS=<client namespace>` for the invoked test.

## Control Flow and State
The script validates `NETIF`, snapshots sysfs GRO/NAPI settings, creates random server and client namespaces, enables hardware loopback, adjusts NAPI/GRO timers, creates server/client macvlans with fixed MAC and IPv6 addresses, and finally runs the requested command with `ip netns exec` inside the server namespace. Persistent state is limited to temporary namespaces, macvlan devices, NIC loopback feature state, and sysfs knob values restored by the EXIT trap.

## Dependencies and Integration
It depends on root, `ip`, `ethtool`, sysfs paths under `/sys/class/net/$NETIF`, macvlan support, and a NIC that supports loopback. It replaces older loopback setup scripts and is installed by the networking helper Makefile.

## Risks and Test Signals
It changes real hardware state, so cleanup correctness matters. Missing sysfs attributes or unsupported loopback will fail early. Because the test sees only the macvlan name `server`, callers must rely on exported environment variables rather than the original `NETIF`. Successful setup prints namespace names and then delegates pass/fail status to the wrapped test.
