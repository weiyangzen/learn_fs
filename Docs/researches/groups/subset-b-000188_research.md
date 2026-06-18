# Research: subset-b-000188

This grouped report covers the subset-b-000188 libnetwork files from `sources/cloud-native/moby`. Each file section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/sandbox_linux_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/osl/sandbox_linux_test.go

Purpose: Linux integration tests for the OSL network namespace sandbox implementation. The file exercises namespace creation, interface migration, address assignment, live restore, duplicate creation, garbage collection, and interface removal.

Important APIs and helpers: `generateRandomName`, `newKey`, and `newInfo` build temporary netns keys and veth/interface fixtures. `verifySandbox` opens the namespace path with `netns.GetFromPath` and checks expected destination interface names through `nlwrap.NewHandleAt`. `verifyCleanup` asserts namespace bind paths are removed. Tests call production APIs such as `NewSandbox`, `Namespace.AddInterface`, `SetGateway`, `SetGatewayIPv6`, `Destroy`, `Interface.Remove`, `setInterfaceIP`, and `setInterfaceIPv6`.

Control flow: each test creates isolated network context with `netnsutils.SetupTestOSContext`, creates veth pairs in the test namespace, then moves/configures interfaces into a sandbox. `TestLiveRestore` creates a second sandbox with `isRestore=true` and verifies existing addresses remain instead of being reconfigured destructively.

State and persistence: test state is kernel netns paths, veth links, IPv4/IPv6 addresses, routes, and gateway settings. Cleanup depends on `Destroy` removing namespace files and links.

Dependencies and integration points: uses netlink/netns, Docker `types.ParseCIDR`, `nlwrap`, and OSL `Namespace` internals. These are privileged Linux tests.

Risks and test signals: strong coverage for route-conflict errors, IPv6 DAD disabling via `IFA_F_NODAD`, namespace GC, duplicate sandbox keys, and interface add/remove. Risks are flakiness from kernel capabilities, permissions, and global temporary names.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/sandbox_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/sandbox_unsupported.go -->
## sources/cloud-native/moby/daemon/libnetwork/osl/sandbox_unsupported.go

Purpose: build-tagged fallback for platforms other than Linux, Windows, and FreeBSD where OSL sandboxes are not implemented.

Important APIs/types/functions: exposes `ErrNotImplemented`, `NewSandbox(key string, osCreate, isRestore bool) (*Namespace, error)`, and `GenerateKey(containerID string) string`. `NewSandbox` always returns `nil, ErrNotImplemented`; `GenerateKey` returns an empty string.

Control flow: there is no runtime state transition. The file exists so higher-level packages compile on unsupported targets while any attempt to create a namespace fails explicitly.

State and persistence: no namespace state, filesystem path, or persisted key is created. The empty `GenerateKey` value is a signal that unsupported platforms cannot derive usable namespace keys.

Dependencies and integration points: imports only `errors`. It satisfies references from libnetwork sandbox restore/create code at compile time for unsupported GOOS values.

Risks and test signals: callers must not assume sandbox operations are available merely because symbols compile. A risk is accidental use of empty `GenerateKey` if higher-level code fails to gate unsupported platforms. The implementation is intentionally tiny; coverage is mostly by build matrix compilation rather than behavior tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/osl/sandbox_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/osallocator_linux.go -->
## sources/cloud-native/moby/daemon/libnetwork/portallocator/osallocator_linux.go

Purpose: Linux OS-backed port allocator. It reserves a logical port through `PortAllocator`, then binds or listens on real host sockets so Docker can hold the port while NAT and proxy plumbing are installed.

Important APIs/types/functions: `OSAllocator` wraps a `*PortAllocator`. `NewOSAllocator` returns the singleton-backed allocator. `RequestPortsInRange(addrs, proto, start, end)` retries up to `maxAllocateAttempts`, delegates to `attemptAllocation`, and returns the common port plus bound `*os.File` sockets. `ReleasePorts` releases logical reservations. Socket helpers include `listenTCP`, `bindTCPOrUDP`, `listenSCTP`, `bindSCTP`, `DetachSocketFilter`, and `setSocketFilter`.

Control flow: allocation requests a common logical port across all addresses, then binds each address for TCP, UDP, or SCTP. On any bind/listen error, defers close already-open sockets and release logical reservations. Explicit single-port requests fail immediately; dynamic/ranged requests retry unless the logical allocator reports exhaustion.

State and persistence: state is in-memory logical allocation plus live socket file descriptors owned by the caller. Bound sockets carry a cBPF drop filter until `DetachSocketFilter` is called.

Dependencies and integration points: uses Linux syscalls, `x/sys/unix`, `x/net/bpf`, SCTP library, and libnetwork `types.Protocol`. NAT port mappers consume the returned sockets.

Risks and test signals: incorrect cleanup leaks ports or file descriptors. Drop-filter ordering is security/availability sensitive because sockets must not accept traffic before DNAT/proxy setup. Tests cover exact/range allocation, in-use ports, multi-address binding, UDP exclusivity, backlog size, SCTP, and filter detachment.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/osallocator_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/osallocator_linux_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/portallocator/osallocator_linux_test.go

Purpose: Linux tests for real socket allocation behavior in `osallocator_linux.go`.

Important APIs/functions: helper `listen` creates competing TCP/UDP/SCTP listeners; `closeSocks` closes returned `*os.File` values. Tests call `NewOSAllocator().RequestPortsInRange`, `ReleasePorts`, `bindTCPOrUDP`, and `DetachSocketFilter`.

Control flow: tests bind exact ports and ranges for TCP/UDP/SCTP, check multi-address sockets with `Getsockname` and `SO_PROTOCOL`, simulate conflicts with external listeners, and verify retry behavior when a range contains busy ports. The packet-filter test starts dial/accept goroutines and proves connection payload is not accepted until the socket filter is detached.

State and persistence: all state is kernel socket state and logical allocator state. Tests carefully release logical ports and close sockets with defers to avoid contamination across cases.

Dependencies and integration points: uses `net`, SCTP, raw syscalls, `ss`, `/proc/sys/net/core/somaxconn`, `x/sys/unix`, and libnetwork `netutils`.

Risks and test signals: these are high-value regression tests for port races, socket backlog correctness, and the temporary drop filter used while firewall state is being prepared. They require Linux features, SCTP availability, `ss`, and permissions; environmental limits can make them fragile.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/osallocator_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/osallocator_windows.go -->
## sources/cloud-native/moby/daemon/libnetwork/portallocator/osallocator_windows.go

Purpose: Windows OS-backed port allocation by creating dummy listeners to reserve host ports.

Important APIs/types/functions: `ErrPortMappedForIP` and `ErrPortNotMapped` describe mapping state failures. `OSAllocator` stores `osListeners map[types.Protocol]map[netip.AddrPort]io.Closer`, a lock, and a logical `PortAllocator`. `New` constructs it. `AllocateHostPort` reserves a logical port and creates a TCP, UDP, or SCTP listener through `allocateHostPort`. `Deallocate` closes and removes the listener and releases the logical reservation.

Control flow: allocation locks the allocator, gets a logical port, validates host IP, checks duplicate `proto/address/port`, then opens a listener with protocol version selected from host IP family. On error it releases logical state and closes any partial listener. Deallocation validates the key, closes the listener if present, deletes map state, and releases the port.

State and persistence: in-memory listener map plus OS listener handles. No on-disk persistence.

Dependencies and integration points: uses Go `net` TCP/UDP listeners, SCTP library, libnetwork `types.Protocol`, and the shared logical allocator. It is a Windows counterpart to Linux socket reservation but without Linux cBPF filter behavior.

Risks and test signals: listener leaks or missed logical releases can permanently block ports in the daemon. Duplicate detection is per `netip.AddrPort` and protocol. Direct tests are not in this subset; behavior is validated by Windows build/test coverage and consumers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/osallocator_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator.go -->
## sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator.go

Purpose: shared in-memory logical host-port allocator for TCP, UDP, and SCTP across IP addresses.

Important APIs/types/functions: `PortAllocator` contains a mutex, default IP, `ipMap`, default dynamic range, and reserved ports. Public methods are `Get`, `GetPortRange`, `RequestPort`, `RequestPortInRange`, `RequestPortsInRange`, `ReleasePort`, and `ReleaseAll`. Internal structures `portMap` and `portRange` track allocated ports and per-range cursors. Errors include `errAllPortsAllocated`, `errUnknownProtocol`, and `alreadyAllocatedErr`.

Control flow: `RequestPortsInRange` validates protocol/range/input, normalizes IPs with `netip`, creates missing maps, and builds a set of port maps that must be free. Unspecified addresses reserve against all addresses in their family; specific addresses also check the corresponding unspecified map. Exact requests check all required maps before marking allocating maps. Dynamic/range requests scan from the first address range cursor and skip system reserved ports only for default ephemeral allocation.

State and persistence: singleton process memory only. No datastore persistence; `ReleaseAll` resets maps using the current dynamic range.

Dependencies and integration points: platform-specific `getDynamicPortRange` and `getReservedPorts` supply defaults. OS allocators and NAT mappers layer real sockets on top.

Risks and test signals: address-family and unspecified-address semantics are subtle. Tests cover duplicates, reuse, ranges, multiple IPs, reserved ports, unknown protocols, and exhaustion.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_freebsd.go -->
## sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_freebsd.go

Purpose: FreeBSD platform implementation for discovering the system ephemeral port range.

Important APIs/functions: `getDynamicPortRange` runs `/sbin/sysctl` for `net.inet.ip.portrange.hifirst` and `net.ip.portrange.hilast`, parses integer output, and returns start/end. `getReservedPorts` returns nil because no reserved-port integration is implemented here.

Control flow: the function executes the low and high sysctl commands separately, parsing each buffer with `fmt.Sscanf`. Any command failure or parse count mismatch becomes a descriptive error, which the shared allocator catches and replaces with default range values.

State and persistence: reads OS sysctl state only; does not write or persist allocator state.

Dependencies and integration points: depends on `/sbin/sysctl`, command execution, and the shared `dynamicPortRange` fallback behavior in `portallocator.go`.

Risks and test signals: parsing assumes sysctl output format can be scanned directly as an integer, which may depend on FreeBSD command formatting. If it fails, Docker falls back to defaults. No FreeBSD-specific tests are in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_linux.go -->
## sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_linux.go

Purpose: Linux platform implementation for dynamic port range and reserved port discovery.

Important APIs/functions: `getDynamicPortRange` reads `/proc/sys/net/ipv4/ip_local_port_range` and scans start/end. `getReservedPorts` reads `/proc/sys/net/ipv4/ip_local_reserved_ports`. `parseReservedPorts` parses comma-separated single ports and ranges, filters to the allocator range, and returns a `map[uint16]struct{}`.

Control flow: dynamic range parsing expects two numbers. Reserved-port parsing trims whitespace, handles empty files as nil, splits entries on commas and optional hyphens, validates uint16 values and range ordering, then inserts only ports between `begin` and `end`.

State and persistence: reads kernel procfs configuration at allocator initialization/reset. The resulting reserved map affects only default ephemeral allocation, not explicit port or explicit range requests.

Dependencies and integration points: used by `newInstance`, `dynamicPortRange`, and `reservedPorts` in the shared allocator.

Risks and test signals: malformed kernel reserved-port contents are logged and ignored by the caller, which may allow Docker to auto-pick administratively reserved ports. Tests in `portallocator_linux_test.go` cover empty input, single/multiple ports, ranges, filtering, and parse errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_linux_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_linux_test.go

Purpose: unit tests for Linux reserved-port parsing.

Important APIs/functions: `TestParseReservedPorts` directly exercises `parseReservedPorts`.

Control flow: table-driven cases pass kernel-style strings such as empty input, single ports, multiple ports, port ranges, and malformed entries. Expected maps verify that only ports in the requested allocator bounds survive.

State and persistence: no persistent state; tests operate entirely on strings and returned maps.

Dependencies and integration points: uses `gotest.tools` assertions and the Linux-only parser in `portallocator_linux.go`.

Risks and test signals: validates the parser layer that prevents default auto-allocation from selecting `/proc/sys/net/ipv4/ip_local_reserved_ports`. It does not read real procfs, so environmental reserved-port settings are not required.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_test.go

Purpose: shared allocator unit tests for protocol validation, exact/dynamic/range allocation, release, exhaustion, multiple IPs, unspecified address interactions, and reserved-port semantics.

Important APIs/functions: tests instantiate `newInstance` to avoid singleton contamination and call `RequestPort`, `RequestPortInRange`, `RequestPortsInRange`, `ReleasePort`, and `ReleaseAll`. `BenchmarkAllocatePorts` measures full-range allocation/reset.

Control flow: tests allocate default dynamic ports, exact ports, all ports in the range, custom ranges, ports across multiple IP addresses, and combinations of specific and unspecified addresses. Reserved-port tests mutate `p.reserved` to prove default ephemeral allocation skips reserved values but explicit requests/ranges still honor caller intent.

State and persistence: all allocator state is in-memory maps and range cursors. Tests confirm release makes exact ports reusable and exhaustion returns `errAllPortsAllocated`.

Dependencies and integration points: uses Go `net` IPs and `gotest.tools`. It indirectly validates behavior consumed by OS allocators and port mappers.

Risks and test signals: strong signal for subtle collision rules between `0.0.0.0`/`::` and concrete addresses. Some spelling in test names is legacy, but behavior is precise.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_unix.go -->
## sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_unix.go

Purpose: non-Windows default dynamic port range constants.

Important APIs/types/functions: defines `defaultPortRangeStart = 49153` and `defaultPortRangeEnd = 65535`.

Control flow: no functions. The shared allocator uses these constants when platform range discovery fails.

State and persistence: no state.

Dependencies and integration points: selected by `//go:build !windows`. Used by `dynamicPortRange` fallback in `portallocator.go` for Linux, FreeBSD, and other Unix-like builds.

Risks and test signals: fallback differs from Windows defaults and should remain aligned with expected Unix/Linux ephemeral ranges. Coverage is indirect through allocator tests and platform build coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_windows.go -->
## sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_windows.go

Purpose: Windows default dynamic port range and reserved-port implementation.

Important APIs/functions: defines `defaultPortRangeStart = 60000`, `defaultPortRangeEnd = 65000`, `getDynamicPortRange`, and `getReservedPorts`.

Control flow: `getDynamicPortRange` returns constants directly. `getReservedPorts` returns nil, so the shared allocator has no Windows reserved-port skip list.

State and persistence: no OS reads or writes; no persisted state.

Dependencies and integration points: used by the shared allocator and Windows `OSAllocator`.

Risks and test signals: Windows behavior does not consult dynamic system settings here, so configured OS ranges may diverge from Docker allocator defaults. Test signal is primarily Windows build/test coverage outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/portallocator_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/sctp_linux_386.go -->
## sources/cloud-native/moby/daemon/libnetwork/portallocator/sctp_linux_386.go

Purpose: Linux 386-specific SCTP setsockopt wrapper.

Important APIs/functions: `setSCTPInitMsg(sd int, options sctp.InitMsg) syscall.Errno` uses `SYS_SOCKETCALL` with `sysSetsockopt = 14` to set `SCTP_INITMSG`.

Control flow: a single raw `syscall.Syscall6` passes socket descriptor, SCTP level, option name, unsafe pointer to `sctp.InitMsg`, and option size. It returns the raw errno.

State and persistence: mutates kernel socket options only.

Dependencies and integration points: used by `bindSCTP` in `osallocator_linux.go`; build-selected for 32-bit x86 Linux where socket calls go through `socketcall`.

Risks and test signals: unsafe pointer and architecture-specific syscall ABI are the main risks. SCTP allocation tests indirectly exercise this on linux/386.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/sctp_linux_386.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/sctp_linux_others.go -->
## sources/cloud-native/moby/daemon/libnetwork/portallocator/sctp_linux_others.go

Purpose: Linux non-386 SCTP setsockopt wrapper.

Important APIs/functions: `setSCTPInitMsg(sd int, options sctp.InitMsg) syscall.Errno` calls `SYS_SETSOCKOPT` directly to set `SCTP_INITMSG`.

Control flow: raw `syscall.Syscall6` passes socket fd, SCTP level, option, unsafe pointer to options, option size, and a final zero argument. It returns errno for caller handling.

State and persistence: only modifies kernel socket option state for a socket under construction.

Dependencies and integration points: used by Linux SCTP port binding in `osallocator_linux.go`; selected by `//go:build linux && !386`.

Risks and test signals: unsafe syscall usage must track Linux ABI and SCTP struct layout. Indirectly covered by SCTP allocation tests on supported architectures.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portallocator/sctp_linux_others.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portmapper/proxy_linux.go -->
## sources/cloud-native/moby/daemon/libnetwork/portmapper/proxy_linux.go

Purpose: starts and stops the Linux `docker-proxy` userland proxy for a port binding.

Important APIs/functions: `StartProxy(pb types.PortBinding, proxyPath string, listenSock *os.File)` returns a stop function. It builds proxy arguments, optionally passes `-use-listen-fd`, and uses an extra pipe for startup status.

Control flow: validates proxy path, creates a pipe, configures `exec.Cmd` with `Pdeathsig`, rootless `nsenter` wrapping if needed, starts the proxy on a locked OS thread, waits for startup status or a 16-second timeout, then returns a stop function that sends interrupt and waits. If an old proxy cannot handle passed listen fd, startup error is made explicit.

State and persistence: owns a child process and pipe/file descriptors. Stop state is tracked by `atomic.Bool`.

Dependencies and integration points: integrates with rootless detached netns, Linux process death signaling, and NAT port bindings that pass pre-bound sockets from `OSAllocator`.

Risks and test signals: thread locking is critical because `Pdeathsig` is tied to the creating thread. Startup pipe protocol and proxy binary version mismatch are operational risks. Tests are not in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portmapper/proxy_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portmapperapi/api.go -->
## sources/cloud-native/moby/daemon/libnetwork/portmapperapi/api.go

Purpose: shared API contract between libnetwork and pluggable port mappers.

Important APIs/types/functions: `Registerer` registers mappers by name. `PortMapper` defines `MapPorts` and `UnmapPorts`. `PortBindingReq` extends `types.PortBinding` with `Mapper` and transient `ChildHostIP`. `PortBinding` extends `types.PortBinding` with mapper name, NAT target, forwarding flag, bound socket, rootless child IP, port-driver cleanup callback, proxy stop callback, and rootless unsupported marker. `ChildPortBinding` returns the daemon-visible host IP binding.

Control flow: `PortBindingReq.Compare` orders requests by mapper, exact-before-range, container port, protocol, host range, host IP, and container IP so equivalent multi-IP bindings are adjacent and can share a host port.

State and persistence: API structs carry runtime-only fields excluded from JSON. NAT/forwarding fields tell callers how to program firewall and proxy state.

Dependencies and integration points: used by NAT and routed mappers and higher libnetwork port-binding reconciliation.

Risks and test signals: incorrect compare ordering can prevent grouped multi-address allocations from sharing the same port. Test file covers the ordering dimensions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portmapperapi/api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portmapperapi/api_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/portmapperapi/api_test.go

Purpose: unit tests for `PortBindingReq.Compare`.

Important APIs/functions: `TestPortBindingReqsCompare` mutates a base TCP binding and asserts ordering relations.

Control flow: cases compare same object, mapper names, container port, protocol, host port, exact versus range, and host-port-end differences. Each comparison checks both forward and reverse sign.

State and persistence: no persistent state; pure value comparison.

Dependencies and integration points: uses `types.PortBinding`, `types.TCP/UDP`, and `gotest.tools` assertions. It protects sort behavior used before invoking port mappers.

Risks and test signals: test is focused but does not cover host IP/container IP ordering or invalid IP inputs. It gives good regression signal for the highest-level grouping fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portmapperapi/api_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portmappers/nat/mapper_linux.go -->
## sources/cloud-native/moby/daemon/libnetwork/portmappers/nat/mapper_linux.go

Purpose: Linux NAT port mapper that allocates host ports, binds sockets, prepares NAT metadata, and integrates with RootlessKit port drivers.

Important APIs/types/functions: `PortDriverClient` abstracts RootlessKit child IP and port-add calls. `Register` registers mapper name `nat`. `Config` passes `RlkClient`. `PortMapper.MapPorts` and `UnmapPorts` implement the mapper. Helpers `setChildHostIP` and `configPortDriver` handle rootless child namespace translation and cleanup callbacks.

Control flow: `MapPorts` verifies all grouped requests share protocol, container port, and host range. Unsupported rootless requests are dropped. It requests one common port for all child host IPs from `portallocator.NewOSAllocator`, constructs `PortBinding` entries with `BoundSocket` and `NAT`, then configures the port driver. On any error, a defer unmaps partial bindings. `UnmapPorts` closes sockets, invokes RootlessKit removal callbacks, then releases logical ports.

State and persistence: state is returned to callers as bindings; no mapper-owned persistent map. Socket ownership transfers through `BoundSocket`.

Dependencies and integration points: depends on `portallocator`, `portmapperapi`, RootlessKit client errors, and firewall/proxy consumers.

Risks and test signals: grouped request mismatch is guarded. Dropping unsupported rootless requests can produce fewer bindings. Cleanup must close sockets and release allocations. Test covers mismatch error.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portmappers/nat/mapper_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portmappers/nat/mapper_linux_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/portmappers/nat/mapper_linux_test.go

Purpose: focused unit test for NAT mapper grouped-request validation.

Important APIs/functions: `TestBindHostPortsError` constructs two `PortBindingReq` values with same protocol/container port but different host port ranges, then calls `MapPorts`.

Control flow: the mapper should reject the mismatched group before allocating sockets. The test asserts the exact internal error text and nil bindings.

State and persistence: no persistent state; no sockets should be allocated because validation fails early.

Dependencies and integration points: uses `portmapperapi`, libnetwork `types`, and `gotest.tools`.

Risks and test signals: verifies a critical caller contract: grouped requests must only differ by host IP. It does not cover happy-path allocation or rootless port-driver behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portmappers/nat/mapper_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portmappers/routed/mapper_linux.go -->
## sources/cloud-native/moby/daemon/libnetwork/portmappers/routed/mapper_linux.go

Purpose: Linux routed-mode port mapper for networks where NAT is disabled and host port numbers should not be allocated.

Important APIs/types/functions: registers mapper name `routed`; `PortMapper` implements `MapPorts` and `UnmapPorts`.

Control flow: `MapPorts` returns one `PortBinding` for each request with `Forwarding=true`. If a host port or host range is specified, it logs that the host port is ignored because NAT is disabled and clears `HostPort`/`HostPortEnd`. `UnmapPorts` is a no-op.

State and persistence: no internal state, no sockets, no logical port allocations.

Dependencies and integration points: used by libnetwork port-mapper registry. The returned `Forwarding` flag tells higher layers to allow forwarding to the container address without DNAT.

Risks and test signals: users may be surprised that requested host ports are ignored in routed mode, but the log makes the behavior explicit. No direct test is in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portmappers/routed/mapper_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/resolvconf/resolvconf.go -->
## sources/cloud-native/moby/daemon/libnetwork/resolvconf/resolvconf.go

Purpose: public compatibility wrapper exposing the host `resolv.conf` path helper.

Important APIs/functions: `Path() string` returns `internal/resolvconf.Path()`.

Control flow: direct delegation only.

State and persistence: no state. It reports whichever path the internal resolver-conf package determines for the host.

Dependencies and integration points: used outside the internal package boundary, with a FIXME noting it should eventually be removed or moved. It bridges libnetwork internals to daemon setup code.

Risks and test signals: the file exists to avoid import-boundary problems. Risk is API persistence: consumers may keep depending on this wrapper. No direct tests are in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/resolvconf/resolvconf.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/resolver.go -->
## sources/cloud-native/moby/daemon/libnetwork/resolver.go

Purpose: Docker embedded DNS server implementation. It listens in the sandbox namespace, answers Docker-owned names, and forwards other DNS queries to configured external resolvers.

Important APIs/types/functions: `DNSBackend` defines sandbox/network callbacks. `Resolver` stores backend, external DNS lists, UDP/TCP servers, forwarding policy, semaphore, and logger. Public methods include `NewResolver`, `SetupFunc`, `Start`, `Stop`, `SetExtServers`, `SetForwardingPolicy`, `SetExtServersForSrc`, `NameServer`, and `ResolverOptions`. Query handlers include A/AAAA, MX, PTR, SRV, forwarding, and upstream exchange.

Control flow: `SetupFunc` binds UDP/TCP sockets. `Start` installs NAT redirect rules via OS-specific `setupNAT` and starts DNS servers. `serveDNS` dispatches local query handlers, truncates authoritative responses to negotiated UDP/TCP sizes, handles ndots behavior, and otherwise calls `forwardExtDNS`. Forwarding selects per-source or global upstreams, enforces `maxConcurrent`, skips host-loopback upstreams when proxying is disabled, retries on SERVFAIL/REFUSED, and records A/AAAA responses with the backend.

State and persistence: all state is in-memory. External DNS is persisted by sandbox state, not resolver itself.

Dependencies and integration points: uses `miekg/dns`, OpenTelemetry, rate limiting, sandbox `ExecFunc`, and network service records.

Risks and test signals: concurrency, namespace dialing, truncation, invalid records, and forwarding policy are sensitive. Tests cover oversized upstream replies, SERVFAIL, NXDOMAIN proxying, invalid PTR, local A/MX resolution, and upstream retry.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/resolver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/resolver_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/resolver_test.go

Purpose: unit/regression tests for resolver query handling and upstream forwarding.

Important APIs/types/functions: fake `dns.ResponseWriter` (`tstwriter`), fake address type, `noopDNSBackend`, `badSRVDNSBackend`, `ptrDNSBackend`, helper response assertions, and `testLogger`.

Control flow: `TestOversizedDNSReply` runs a UDP upstream that returns a non-EDNS reply over 512 bytes and verifies the resolver forwards it successfully. `TestReplySERVFAIL` checks internal errors, disabled proxying, and missing upstreams. `TestProxyNXDOMAIN` verifies an upstream NXDOMAIN with SOA is preserved. `TestInvalidReverseDNS` confirms invalid PTR answers produce SERVFAIL.

State and persistence: only transient test DNS servers and resolver memory. No sandbox persistence.

Dependencies and integration points: uses `miekg/dns`, `netnsutils.AssertSocketSameNetNS`, log redirection, and fake `DNSBackend` implementations.

Risks and test signals: high-value coverage for production DNS edge cases: oversized replies, namespace leakage canary, upstream response preservation, and robust error replies. Tests avoid full daemon setup except local sockets.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/resolver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/resolver_unix.go -->
## sources/cloud-native/moby/daemon/libnetwork/resolver_unix.go

Purpose: Unix/Linux NAT setup for the embedded DNS resolver.

Important APIs/functions: `setupNAT` selects nftables or iptables. `setupIptablesNAT` programs `DOCKER_OUTPUT` and `DOCKER_POSTROUTING` chains. `setupNftablesNAT` creates a `docker-dns` table with DNAT/SNAT base chains.

Control flow: `setupNAT` extracts UDP/TCP listener addresses and ports, then chooses nftables when enabled. iptables path runs inside the sandbox namespace via backend `ExecFunc`, creates or flushes custom chains, inserts jumps from OUTPUT/POSTROUTING, then inserts DNAT/SNAT rules to map port 53 to the actual listener ports. nftables path builds equivalent output and postrouting chains and applies them in namespace.

State and persistence: mutates per-sandbox firewall state. Rules are tied to the sandbox namespace lifecycle.

Dependencies and integration points: depends on libnetwork `iptables`, internal `nftables`, and resolver sockets from `SetupFunc`.

Risks and test signals: firewall rule idempotency and chain cleanup are critical. IPv6 is TODO. Tests indirectly exercise DNS startup and forwarding on Unix.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/resolver_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/resolver_unix_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/resolver_unix_test.go

Purpose: Unix/Linux integration tests for resolver behavior with real libnetwork controller, bridge network, sandbox, and local upstream DNS server.

Important APIs/functions: `TestDNSIPQuery` builds a controller/network/endpoint/sandbox, injects service records, and calls `Resolver.serveDNS`. `TestDNSProxyServFail` starts a local TCP DNS server that fails once, configures two identical upstream entries, and verifies retry.

Control flow: the first test joins an endpoint to a sandbox, adds a service record, verifies case-insensitive A lookup, MX implicit success for known names, and SERVFAIL for unknown MX with proxying disabled. The second test runs in a test OS context, waits for the DNS server, then expects two upstream requests because the first returns SERVFAIL.

State and persistence: temporary controller datastore and kernel namespace state; all cleaned up through controller/network/sandbox deletion.

Dependencies and integration points: uses real libnetwork config, default IPAM, bridge network, `netnsutils`, and `miekg/dns`.

Risks and test signals: good integration signal but requires Linux namespace/network support. Covers local service records and upstream retry semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/resolver_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/resolver_windows.go -->
## sources/cloud-native/moby/daemon/libnetwork/resolver_windows.go

Purpose: Windows resolver NAT stub.

Important APIs/functions: `func (r *Resolver) setupNAT(context.Context) error` returns nil.

Control flow: no firewall setup occurs for the embedded resolver on Windows through this path.

State and persistence: no state.

Dependencies and integration points: selected by Windows build tags so shared resolver startup compiles and runs without Unix iptables/nftables.

Risks and test signals: behavior depends on Windows networking/DNS integration elsewhere. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/resolver_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox.go -->
## sources/cloud-native/moby/daemon/libnetwork/sandbox.go

Purpose: core libnetwork `Sandbox`, the container-scoped network object that owns endpoints, resolver, OS namespace, DNS/hosts config, service enablement, and datastore state.

Important APIs/types/functions: `SandboxOption`, `Sandbox`, `containerConfig`, getters, `Delete`, `Rename`, `Refresh`, `UpdateLabels`, JSON marshal/unmarshal, endpoint list management, `populateNetworkResources`, DNS backend methods (`ResolveName`, `ResolveIP`, `ResolveService`, `HandleQueryResp`), `hasExternalAccess`, `EnableService`, `DisableService`, endpoint `Less`, and `NdotsSet`.

Control flow: deletion marks `inDelete`, leaves/deletes endpoints, stops resolver, destroys OS sandbox if owned, deletes store state, and removes controller map entry. Joining/populating resources delegates OS work, updates service records, default gateway, resolver forwarding, cluster driver info, and load balancers. Name resolution tries aliases before real names and, in swarm mode, sorts endpoints by network type.

State and persistence: in-memory guarded by `mu`, `joinLeaveMu`, and `service`; persisted through `sandbox_store.go`. Endpoint ordering affects gateway selection.

Dependencies and integration points: integrates with `osl`, networks/endpoints, service discovery, OpenTelemetry, etchosts, and scope constants.

Risks and test signals: concurrency around delete/join/leave and gateway ordering is subtle. Tests cover sandbox lookup, empty delete, endpoint priority, family-specific gateways, and same-priority ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_dns_unix.go -->
## sources/cloud-native/moby/daemon/libnetwork/sandbox_dns_unix.go

Purpose: Unix sandbox `/etc/hosts`, `/etc/resolv.conf`, and embedded DNS resolver setup.

Important APIs/functions: `AddHostsEntry`, `UpdateHostsEntry`, `rebuildHostsFile`, `startResolver`, `setupResolutionFiles`, `buildHostsFile`, `makeHostsRecs`, `addHostsEntries`, `deleteHostsEntries`, path restore helpers, `setExternalResolvers`, `loadResolvConf`, `setupDNS`, `updateDNS`, `rebuildDNS`, `createBasePath`, and `copyFile`.

Control flow: sandbox creation creates hosts and resolv.conf paths under `/var/lib/docker/network/files/<sandbox>`. Host-mode with no extra hosts copies the origin hosts file. DNS setup loads host resolv.conf, applies user overrides, and writes a hash. On endpoint join, `updateDNS` rewrites non-user-modified files for legacy networks. When embedded DNS starts, `rebuildDNS` swaps nameservers to `127.0.0.11`, stores external resolvers, and preserves/sets `ndots`.

State and persistence: files on disk, hash files for user-modification detection, `sb.extDNS`, and `sb.ndotsSet`.

Dependencies and integration points: internal `resolvconf`, `etchosts`, resolver, sandbox IPv6 probing, and container mount setup.

Risks and test signals: user-edited resolv.conf must not be overwritten; hash behavior in `rebuildDNS` is intentionally legacy. Tests cover DNS option precedence and invalid ndots handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_dns_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_dns_unix_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/sandbox_dns_unix_test.go

Purpose: Unix tests for sandbox DNS option handling.

Important APIs/functions: `getResolvConfOptions` reads and parses the sandbox resolv.conf; `TestDNSOptions` exercises `setupDNS`, `startResolver`, and `rebuildDNS`.

Control flow: first sandbox starts resolver, writes DNS config, and verifies default embedded resolver option `ndots:0`. It then sets `ndots:5` and confirms setup/rebuild preserves it. A second sandbox verifies explicit `ndots:0` remains, while invalid values such as `ndots:foobar` and `ndots:-1` fall back to valid `ndots:0`.

State and persistence: uses temporary controller data dir and sandbox resolv.conf file paths. Cleanup deletes sandboxes.

Dependencies and integration points: uses internal resolvconf parser and libnetwork controller creation.

Risks and test signals: protects user DNS option precedence and resolver option sanitization. It does not exercise user-modified hash behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_dns_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_dns_windows.go -->
## sources/cloud-native/moby/daemon/libnetwork/sandbox_dns_windows.go

Purpose: Windows stubs for Unix-style sandbox DNS and hosts file management.

Important APIs/functions: `setupResolutionFiles`, `restoreHostsPath`, `restoreResolvConfPath`, and `deleteHostsEntries`.

Control flow: all functions are no-ops or return nil.

State and persistence: no Unix-style `/etc/hosts` or `resolv.conf` file state is managed here.

Dependencies and integration points: selected for Windows builds so shared sandbox code compiles. Windows endpoint resolver population is handled in `sandbox_windows.go`.

Risks and test signals: platform divergence is intentional; callers must not expect Unix file behavior on Windows. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_dns_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_externalkey_unix.go -->
## sources/cloud-native/moby/daemon/libnetwork/sandbox_externalkey_unix.go

Purpose: Linux/FreeBSD external network namespace key handoff for containers created by an OCI runtime.

Important APIs/types/functions: reexec registration `libnetwork-setkey`, `setKeyData`, `processSetKeyReexec`, `setKey`, `setExternalKey`, `processReturn`, controller `startExternalKeyListener`, `acceptClientConnections`, `processExternalKey`, and `stopExternalKeyListener`.

Control flow: runtime reexec reads OCI `specs.State` from stdin, derives `/proc/<pid>/ns/net`, and sends container ID/key plus OpenTelemetry trace context over a Unix socket under `<exec-root>/libnetwork/<short-controller-id>.sock`. The controller listener accepts JSON requests, finds the sandbox, calls `Sandbox.SetKey`, and returns `"success"` or an error string.

State and persistence: creates a Unix socket and stores listener on controller. The actual sandbox namespace state is updated by `SetKey`.

Dependencies and integration points: uses `reexec`, OCI runtime state, controller exec root, OpenTelemetry propagation, and Unix sockets.

Risks and test signals: socket permissions/path cleanup and partial JSON reads are sensitive. External key setup is critical for joining an already-created container netns. Tests for external key behavior exist elsewhere; this subset includes no direct test.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_externalkey_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_externalkey_unsupported.go -->
## sources/cloud-native/moby/daemon/libnetwork/sandbox_externalkey_unsupported.go

Purpose: no-op external key listener for platforms other than Linux and FreeBSD.

Important APIs/functions: `Controller.startExternalKeyListener` returns nil; `Controller.stopExternalKeyListener` does nothing.

Control flow: no listener is created and no external namespace key is accepted.

State and persistence: none.

Dependencies and integration points: selected by `//go:build !linux && !freebsd` to satisfy controller calls on unsupported platforms.

Risks and test signals: higher-level code must account for platform support. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_externalkey_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_linux.go -->
## sources/cloud-native/moby/daemon/libnetwork/sandbox_linux.go

Purpose: Linux-specific sandbox OS namespace operations.

Important APIs/functions: `releaseOSSboxResources`, `Statistics`, `updateGateway`, `ExecFunc`, `SetKey`, `NetnsPath`, `IPv6Enabled`, `releaseOSSbox`, `restoreOslSandbox`, `finishEndpointConfig`, `canPopulateNetworkResources`, and `populateNetworkResourcesOS`.

Control flow: `SetKey` attaches a sandbox to an externally created namespace, destroys old OS sandbox resources if needed, restarts resolver in the new namespace, refreshes IPv6 loopback state, rebuilds hosts, and finishes deferred endpoint configuration. `populateNetworkResourcesOS` validates `osSbox`, starts resolver if needed, adds interfaces with addresses/routes/sysctls/advertisement settings, handles IPv6 address removal if sysctls disabled it, configures DSR VIP aliasing, static routes, gateway updates, hosts entries, DNS, load balancers, and store update.

State and persistence: mutates `sb.osSbox`, `populatedEndpoints`, endpoint interface state, kernel routes, aliases, and datastore checkpoints.

Dependencies and integration points: OSL namespace, endpoint join info, netutils, service load balancers, DNS file code, and gateway selection.

Risks and test signals: namespace moves, resolver restart, IPv6 sysctl side effects, and gateway ordering are high-risk. Tests in this subset cover OSL primitives and sandbox endpoint/gateway ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_options.go -->
## sources/cloud-native/moby/daemon/libnetwork/sandbox_options.go

Purpose: option constructors used to configure `Sandbox` creation.

Important APIs/functions: hostname/domain/hosts path/origin hosts, extra host, resolv.conf path/origin, DNS nameservers/search/options, default sandbox, external key, exposed ports, port mappings, ingress marker, and load-balancer marker.

Control flow: each function returns a `SandboxOption` closure that mutates `sb.config` or sandbox flags. Exposed ports and port mappings defensively copy slices before storing in `config.generic` under netlabel keys for drivers. Ingress/load-balancer options append OSL sandbox type markers.

State and persistence: options initialize sandbox config that later affects file creation, namespace key selection, driver labels, exposed port data, and load balancer behavior. Some values are persisted indirectly through sandbox state or endpoint/driver state.

Dependencies and integration points: used by controller `NewSandbox`, restore flows, daemon container setup, network drivers via `netlabel`, and OSL sandbox type tuning.

Risks and test signals: missing defensive copies would let caller mutations affect driver config; this file avoids that for slices. Direct tests are mostly through sandbox creation and integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_store.go -->
## sources/cloud-native/moby/daemon/libnetwork/sandbox_store.go

Purpose: datastore serialization, update, delete, and restore for sandboxes.

Important APIs/types/functions: `epState`, `sbState`, datastore methods (`Key`, `KeyPrefix`, `Value`, `SetValue`, `Index`, `SetIndex`, `Exists`, `Skip`, `New`, `CopyTo`), `Sandbox.storeUpdate`, `storeDelete`, and `Controller.sandboxRestore`.

Control flow: `storeUpdate` rebuilds endpoint references from current sandbox memory, skips non-persistent endpoints, and retries on `datastore.ErrKeyModified`. Restore lists stored sandboxes, creates a `Sandbox` object, applies active sandbox options if present, recreates/opens OSL sandbox with `osl.NewSandbox`, restores endpoints from network/endpoint stores, deletes stale inactive sandboxes, restores OSL interfaces/routes/gateways for active sandboxes, and re-adds service records when appropriate.

State and persistence: persists sandbox ID, container ID, endpoint IDs/network IDs, endpoint priority, and external DNS as `ExtDNS2`. `dbIndex`/`dbExists` maintain optimistic store state.

Dependencies and integration points: controller store, OSL, endpoint/network stores, swarm scope logic, live restore.

Risks and test signals: restore must tolerate missing networks/endpoints and avoid destructive cleanup for active live-restore containers. Tests are mostly broader store/live-restore tests outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_unix_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/sandbox_unix_test.go

Purpose: Unix integration tests for controller sandbox lookup, sandbox deletion, endpoint ordering, and gateway endpoint selection.

Important APIs/functions: `getTestEnv` builds a controller and optional bridge networks. Tests include `TestControllerGetSandbox`, `TestSandboxAddEmpty`, `TestSandboxAddMultiPrio`, `TestGatewayEndpointRespectsPriorityPerAddressFamily`, and `TestSandboxAddSamePrio`.

Control flow: tests create sandboxes/networks/endpoints, join endpoints with or without priorities, and inspect controller sandbox endpoint ordering. They verify invalid and missing sandbox lookup errors, empty sandbox deletion, priority dominance, internal-network lowest precedence, IPv6/gateway precedence, and separate IPv4/IPv6 gateway endpoint selection.

State and persistence: uses temporary data dirs, bridge network state, endpoint lists, and sandbox controller maps. Cleanup deletes sandboxes/networks and stops controller.

Dependencies and integration points: bridge driver, default IPAM, netns test context, network labels, and join options.

Risks and test signals: protects the endpoint ordering logic that drives default gateway choice and DNS/network preference. Requires Unix network namespace support.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_windows.go -->
## sources/cloud-native/moby/daemon/libnetwork/sandbox_windows.go

Purpose: Windows-specific sandbox behavior where `Sandbox.osSbox` is not used.

Important APIs/functions: no-op `releaseOSSboxResources`, `updateGateway`, `ExecFunc`, `releaseOSSbox`, `restoreOslSandbox`, `NetnsPath`, `canPopulateNetworkResources`, `populateNetworkResourcesOS`, and `IPv6Enabled`.

Control flow: most OS namespace operations are no-ops. `populateNetworkResourcesOS` calls `addEpToResolver` with network name, endpoint name, sandbox config, endpoint interface, and network resolvers, wrapping errors with `errdefs.System`. `IPv6Enabled` always returns false/true because Windows container network drivers currently do not support IPv6.

State and persistence: no OSL namespace state. Resolver state is populated through Windows network resolver integration.

Dependencies and integration points: Windows HNS/resolver path elsewhere; endpoint interface and network resolver data.

Risks and test signals: platform divergence means shared sandbox code must not require `osSbox` on Windows. Tests are in Windows-specific suites outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/scope/scope.go -->
## sources/cloud-native/moby/daemon/libnetwork/scope/scope.go

Purpose: defines libnetwork datastore/network scope constants.

Important APIs/types/functions: constants `Local`, `Global`, and `Swarm`.

Control flow: none.

State and persistence: no state. Values are string labels used throughout libnetwork to classify network and datastore scope.

Dependencies and integration points: `Sandbox.populateNetworkResources` and restore logic use `scope.Swarm` to decide whether service records should be updated locally or handled by swarm/multihost control paths.

Risks and test signals: constants are stable API-like values; changing them would break comparisons and persisted/configured data. Test signal is indirect through network and service behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/scope/scope.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/service.go -->
## sources/cloud-native/moby/daemon/libnetwork/service.go

Purpose: shared service/load-balancer data structures for swarm service discovery and dataplane programming.

Important APIs/types/functions: global `fwMarkCtr` with mutex, `portConfigs.String`, `serviceKey`, `service`, `assignIPToEndpoint`, `removeIPToEndpoint`, `printIPToEndpoint`, `lbBackend`, and `loadBalancer`.

Control flow: service IP-to-endpoint mapping uses a set-matrix to track transient duplicate endpoint/IP states. `portConfigs.String` creates a stable key fragment from published/target/protocol tuples. Load balancers store per-network VIP, fwmark, backends, and service alias reference counts.

State and persistence: process memory only. Service bindings are held on `Controller.serviceBindings`; fwmarks are monotonic from 256 and not persisted here.

Dependencies and integration points: used heavily by `service_common.go`, `service_linux.go`, and `service_windows.go` to manage DNS records, IPVS/HNS policy, and alias lifetime.

Risks and test signals: alias reference counts and transient duplicate IP states are sensitive during rolling updates. Tests in `service_common_unix_test.go` cover alias ref-counting and cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/service_common.go -->
## sources/cloud-native/moby/daemon/libnetwork/service_common.go

Purpose: shared Linux/Windows service discovery and service binding bookkeeping.

Important APIs/functions: endpoint/container DNS record add/delete helpers, `newService`, `getLBIndex`, `cleanupServiceDiscovery`, `cleanupServiceBindings`, `makeServiceCleanupFunc`, `addServiceBinding`, and `rmServiceBinding`.

Control flow: adding a service binding locks by network ID, creates/reuses a `service`, creates a per-network `loadBalancer` with fwmark, diffs service aliases against prior backend aliases, maintains VIP alias reference counts, records backend IP-to-endpoint mapping, programs network load balancer backend, and adds DNS records. Removal either disables or fully removes a backend, decrements alias refs, removes load-balancer service when last backend leaves, deletes DNS records when requested, and removes the service object only after all load balancers are gone.

State and persistence: in-memory controller maps for service bindings and service records. DNS records are maintained per network.

Dependencies and integration points: calls network `addSvcRecords/deleteSvcRecords`, `addLBBackend/rmLBBackend`, network locker, and `setmatrix`.

Risks and test signals: locking order avoids network deletion races; alias ref-counting prevents DNS flaps during rolling updates. Tests cover service discovery cleanup and alias ref-counting per network/rebind.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/service_common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/service_common_unix_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/service_common_unix_test.go

Purpose: Unix tests for service discovery cleanup and service alias reference counting.

Important APIs/functions: `TestCleanupServiceDiscovery` and `TestServiceAliasRefCounting`.

Control flow: cleanup test creates two bridge networks, adds service records to both, verifies `cleanupServiceDiscovery(nID)` removes only one network and `cleanupServiceDiscovery("")` removes all. Alias tests add/remove service bindings with VIPs across rolling-update, per-network, and same-endpoint rebind scenarios, using `Network.ResolveName` to verify DNS visibility.

State and persistence: temporary controller/network state, `svcRecords`, `serviceBindings`, load-balancer alias refs, and resolver records. Networks are deleted after tests.

Dependencies and integration points: controller setup, bridge networks, IPAM defaults, service binding functions, DNS resolver records, and netns context.

Risks and test signals: strong regression signal for the alias ref-counting behavior documented in service structs. Ensures aliases do not disappear too early or leak across networks.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/service_common_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/service_linux.go -->
## sources/cloud-native/moby/daemon/libnetwork/service_linux.go

Purpose: Linux dataplane implementation for swarm service load balancing, ingress port rules, IPVS backends, and firewall marks.

Important APIs/functions: `Sandbox.populateLoadBalancers`, `Network.findLBEndpointSandbox`, `findIfaceDstName`, `Network.addLBBackend`, `Network.rmLBBackend`, ingress helpers (`addIngressPorts`, `removeIngressPorts`, `restoreIngressPorts`, `filterPortConfigs`, `initIngressConfiguration`, rule generation/program/delete), proxy helpers, `configureFWMark`, and `addRedirectRules`.

Control flow: adding a backend finds the LB endpoint sandbox, ensures VIP alias and IPVS service exist, configures ingress ports and firewall mark rules, adds IPVS destination, and applies OS tweaks. Removing deweights or deletes destinations, removes service/VIP/firewall/ingress state when last backend leaves. Ingress setup creates `DOCKER-INGRESS`, NAT/filter jumps, route_localnet, MASQUERADE, per-port DNAT/ACCEPT rules, and dummy listeners to reserve ingress ports.

State and persistence: global ingress rule/proxy/reference maps, kernel iptables state, IPVS state, namespace aliases, and `/proc` sysctl writes.

Dependencies and integration points: `moby/ipvs`, iptables, bridge driver chains, netlink, SCTP, sandbox `ExecFunc`.

Risks and test signals: rollback/refcount correctness is critical; IPv6 TODOs remain. Direct tests are not in this subset; broader swarm/ingress integration tests cover behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/service_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/service_unsupported.go -->
## sources/cloud-native/moby/daemon/libnetwork/service_unsupported.go

Purpose: fallback service/load-balancer stubs for platforms other than Linux and Windows.

Important APIs/functions: no-op cleanup functions, `addServiceBinding`/`rmServiceBinding` returning `"not supported"`, no-op `Sandbox.populateLoadBalancers`, and no-op `arrangeIngressFilterRule`.

Control flow: service binding calls fail immediately; cleanup/load-balancer hooks do nothing.

State and persistence: none.

Dependencies and integration points: selected by build tags to satisfy shared code references.

Risks and test signals: unsupported platforms cannot use swarm service binding/load balancing through this implementation. Build coverage is the primary signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/service_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/service_windows.go -->
## sources/cloud-native/moby/daemon/libnetwork/service_windows.go

Purpose: Windows dataplane implementation for service load balancing through HNS/VFP policy lists.

Important APIs/types/functions: `policyLists`, global `lbPolicylistMap`, `Network.addLBBackend`, `Network.rmLBBackend`, `numEnabledBackends`, no-op `Sandbox.populateLoadBalancers`, and no-op `arrangeIngressFilterRule`.

Control flow: adding a backend finds the load balancer endpoint source VIP, resolves HNS endpoints for enabled backends, deletes any existing policy lists for the load balancer, creates an internal load balancer policy, then creates external policies for published ingress ports while coalescing matching TCP/UDP pairs to wildcard protocol where needed. Removing a backend reprograms policies if enabled backends remain; otherwise it deletes ILB/ELB policy lists and removes the map entry.

State and persistence: process-global map from `*loadBalancer` to HNS policy list handles; actual dataplane state lives in HNS/VFP.

Dependencies and integration points: Microsoft `hcsshim`, service common binding state, network endpoints, and Windows HNS endpoint names.

Risks and test signals: stale policy lists can survive if map state is lost; cleanup order matters because policy lists must be removed before HNS network deletion. Windows integration tests outside this subset provide coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/service_windows.go -->
