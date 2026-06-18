# sources/distributed-fs/ceph-client/tools/testing/selftests/net/fcnal-ipv4.sh

Purpose: this tiny wrapper runs only the IPv4 portion of the functional networking address lookup suite.

Important behavior: it executes `./fcnal-test.sh -t ipv4`. The target harness expands `ipv4` into the IPv4 ping, TCP, UDP, bind, runtime, and netfilter test sets.

State and dependencies: this wrapper has no independent state, cleanup, or argument handling. All namespace, VRF, route, socket, process, and test-result behavior is delegated to `fcnal-test.sh`.

Integration points and risks: it must be run from a directory where `fcnal-test.sh` is executable and relative helper paths resolve. Its test signal is the exit status and summary emitted by the delegated harness.
