# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fcnal-ipv6.sh

Purpose: this wrapper selects the IPv6 portion of the functional networking address lookup suite.

Important behavior: it executes `./fcnal-test.sh -t ipv6`. The main harness maps that selector to IPv6 ping, TCP, UDP, bind, runtime, and netfilter tests, including link-local, multicast, VRF, and l3mdev permutations.

State and dependencies: the wrapper itself does not create state. All network namespaces, routes, sysctls, sockets, and cleanup are owned by `fcnal-test.sh`.

Integration points and risks: it depends on relative execution from the net selftest directory and on the main harness plus generated `nettest` helper. Its only direct test signal is the delegated command's exit status.
