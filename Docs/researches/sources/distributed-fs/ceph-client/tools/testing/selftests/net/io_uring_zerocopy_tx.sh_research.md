# sources/distributed-fs/ceph-client/tools/testing/selftests/net/io_uring_zerocopy_tx.sh

Purpose: Namespace harness for `io_uring_zerocopy_tx`, sending data between two veth-connected namespaces and a `msg_zerocopy` receiver.

Important commands and variables: Creates `NS1` and `NS2`, veth `veth0`, fixed IPv4 and IPv6 addresses, high MTU, fixed MACs, `net.core.optmem_max`, and toggles `kernel.io_uring_disabled` when needed. Runs `msg_zerocopy` as receiver and `io_uring_zerocopy_tx` as sender.

Control flow: With no arguments it recursively runs IPv4 and IPv6 UDP/TCP tests for modes 1, 2, and 3. With arguments it parses IP version and transmit mode, maps raw or packet modes to receiver modes when needed, creates namespaces and veth, configures addresses, enables io_uring if disabled, starts receiver in `NS2`, runs transmitter in `NS1`, waits, and reports `ok`.

State and persistence: Runtime state is temporary namespaces plus a saved sysctl value for `kernel.io_uring_disabled`, restored in cleanup. No durable files are written.

Dependencies and integration: Requires root, `ip`, sysctl access, built `io_uring_zerocopy_tx`, and built `msg_zerocopy`.

Risks: Cleanup assumes both namespaces exist. The global io_uring sysctl is host-wide, so restoration is important. Receiver startup uses a fixed short sleep rather than a readiness probe.

Test signals: Automated mode ending with `OK. All tests passed` confirms transmit and receive behavior across the mode matrix.
