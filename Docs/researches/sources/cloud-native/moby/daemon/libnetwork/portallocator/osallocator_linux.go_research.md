<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/osallocator_linux.go -->
## sources/cloud-native/moby/daemon/libnetwork/portallocator/osallocator_linux.go

Purpose: Linux OS-backed port allocator. It reserves a logical port through `PortAllocator`, then binds or listens on real host sockets so Docker can hold the port while NAT and proxy plumbing are installed.

Important APIs/types/functions: `OSAllocator` wraps a `*PortAllocator`. `NewOSAllocator` returns the singleton-backed allocator. `RequestPortsInRange(addrs, proto, start, end)` retries up to `maxAllocateAttempts`, delegates to `attemptAllocation`, and returns the common port plus bound `*os.File` sockets. `ReleasePorts` releases logical reservations. Socket helpers include `listenTCP`, `bindTCPOrUDP`, `listenSCTP`, `bindSCTP`, `DetachSocketFilter`, and `setSocketFilter`.

Control flow: allocation requests a common logical port across all addresses, then binds each address for TCP, UDP, or SCTP. On any bind/listen error, defers close already-open sockets and release logical reservations. Explicit single-port requests fail immediately; dynamic/ranged requests retry unless the logical allocator reports exhaustion.

State and persistence: state is in-memory logical allocation plus live socket file descriptors owned by the caller. Bound sockets carry a cBPF drop filter until `DetachSocketFilter` is called.

Dependencies and integration points: uses Linux syscalls, `x/sys/unix`, `x/net/bpf`, SCTP library, and libnetwork `types.Protocol`. NAT port mappers consume the returned sockets.

Risks and test signals: incorrect cleanup leaks ports or file descriptors. Drop-filter ordering is security/availability sensitive because sockets must not accept traffic before DNAT/proxy setup. Tests cover exact/range allocation, in-use ports, multi-address binding, UDP exclusivity, backlog size, SCTP, and filter detachment.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/osallocator_linux.go -->
