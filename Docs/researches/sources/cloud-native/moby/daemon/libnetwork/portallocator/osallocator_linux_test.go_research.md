<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/osallocator_linux_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/portallocator/osallocator_linux_test.go

Purpose: Linux tests for real socket allocation behavior in `osallocator_linux.go`.

Important APIs/functions: helper `listen` creates competing TCP/UDP/SCTP listeners; `closeSocks` closes returned `*os.File` values. Tests call `NewOSAllocator().RequestPortsInRange`, `ReleasePorts`, `bindTCPOrUDP`, and `DetachSocketFilter`.

Control flow: tests bind exact ports and ranges for TCP/UDP/SCTP, check multi-address sockets with `Getsockname` and `SO_PROTOCOL`, simulate conflicts with external listeners, and verify retry behavior when a range contains busy ports. The packet-filter test starts dial/accept goroutines and proves connection payload is not accepted until the socket filter is detached.

State and persistence: all state is kernel socket state and logical allocator state. Tests carefully release logical ports and close sockets with defers to avoid contamination across cases.

Dependencies and integration points: uses `net`, SCTP, raw syscalls, `ss`, `/proc/sys/net/core/somaxconn`, `x/sys/unix`, and libnetwork `netutils`.

Risks and test signals: these are high-value regression tests for port races, socket backlog correctness, and the temporary drop filter used while firewall state is being prepared. They require Linux features, SCTP availability, `ss`, and permissions; environmental limits can make them fragile.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/osallocator_linux_test.go -->
