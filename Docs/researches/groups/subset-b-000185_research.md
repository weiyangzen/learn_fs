# Research Report: subset-b-000185

This grouped report covers the subset-b-000185 source files from Moby libnetwork. Each file section is wrapped with the reconciliation markers required for splitting into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/resolvconf/resolvconf.go -->
# sources/cloud-native/moby/daemon/libnetwork/internal/resolvconf/resolvconf.go

## Purpose
Implements parsing, mutation, transformation, generation, and write/hash tracking for container `/etc/resolv.conf` content. It is the core DNS configuration adapter between host resolver state, Docker CLI DNS overrides, legacy networking, and networks with Docker's internal resolver.

## Important APIs, Types, And Functions
- `ResolvConf` stores parsed nameservers, search domains, options, unknown directives, and construction metadata.
- `ExtDNSEntry` records nameservers removed from the generated container file for use by the internal DNS resolver, including whether a loopback address must be reached from the host namespace.
- `Load` and `Parse` read resolv.conf from a path or reader, preserve source path metadata, parse only known directives into structured fields, keep unknown directives verbatim, and wrap scanner errors as `systemError`.
- `OverrideNameServers`, `OverrideSearch`, `OverrideOptions`, `AddOption`, and accessors mutate or expose DNS fields. Accessors clone slices to avoid external mutation.
- `TransformForLegacyNw` removes host-loopback nameservers and IPv6 nameservers when IPv6 is disabled, then falls back to Google public DNS defaults if no usable nameserver remains.
- `TransformForIntNS` replaces all nameservers with the internal resolver address, stashes previous nameservers in metadata, and ensures required resolver options such as `ndots`.
- `Generate` writes resolv.conf syntax plus optional diagnostic comments about source, transform, overrides, invalid nameservers, external servers, warnings, and ndots provenance.
- `WriteFile` writes the generated file and optional digest hash; `UserModified` compares the current file against that digest.
- `removeInvalidNDots` filters malformed `ndots` values when an internal resolver requires a valid setting.

## Control Flow
Parsing scans line by line, strips blank/comment lines, uses `strings.Fields`, and handles `nameserver`, `search`/`domain`, and `options`. Invalid nameserver tokens are not fatal; they are remembered for diagnostics. Legacy transformation is skipped when nameservers were explicitly overridden. Internal resolver transformation always moves existing nameservers to `ExtNameServers`, sets the only configured nameserver to the internal address, and conditionally adds required options without overwriting valid existing options.

## State And Persistence
Most state is in-memory on `ResolvConf`. Persistent effects happen only in `WriteFile`, which truncates/writes the target resolv.conf because it may be bind-mounted, and writes the hash atomically through `atomicwriter`. `UserModified` treats a missing hash file as "not modified yet" but reports unreadable or unparsable hashes as errors.

## Dependencies And Integration Points
Uses `net/netip` for address parsing, `opencontainers/go-digest` for modification detection, `moby/sys/atomicwriter` for hash updates, and containerd logging for fallback warnings. It integrates with libnetwork sandbox setup, the embedded resolver path, and user DNS override handling.

## Risks
The parser intentionally accepts unknown directives and invalid nameservers, so downstream users must rely on generated diagnostics rather than hard failures. `WriteFile` is not atomic for the resolv.conf target itself because bind mounts prevent rename-based replacement. Metadata such as `HostLoopback` depends on whether the nameservers came from host config or override, so incorrect override tracking could make the embedded resolver query the wrong namespace.

## Test Signals
`resolvconf_test.go` covers option lookup precedence, file/hash write and user modification detection, override generation golden files, legacy and internal resolver transforms, invalid ndots replacement, source path detection, invalid nameserver comments, unknown directive preservation, header insertion, parse error wrapping for overlong lines, and generation allocation benchmarks.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/resolvconf/resolvconf.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/resolvconf/resolvconf_path.go -->
# sources/cloud-native/moby/daemon/libnetwork/internal/resolvconf/resolvconf_path.go

## Purpose
Chooses which host resolv.conf file libnetwork should read. It detects the common systemd-resolved stub resolver case and redirects legacy networking to systemd's generated resolver file.

## Important APIs, Types, And Functions
- `defaultPath` is `/etc/resolv.conf`.
- `alternatePath` is `/run/systemd/resolve/resolv.conf`.
- `Path()` returns the selected path, using `sync.Once` to perform detection only once per process.

## Control Flow
On first call, `Path` loads `/etc/resolv.conf`. If loading fails, it silently keeps the default path because the same error will surface to later open/read callers. If exactly one nameserver exists and it is `127.0.0.53`, it records the alternate systemd-resolved path and logs the detection.

## State And Persistence
The selected path is process-global in `pathAfterSystemdDetection`. There is no filesystem mutation. Because detection runs once, changes to host resolver configuration after first call are not observed.

## Dependencies And Integration Points
Depends on `Load` from the same package and `netip` for comparing the stub resolver address. It is used by Docker DNS setup code before parsing host resolver state.

## Risks
The heuristic only handles the exact single-nameserver systemd stub case. Multi-nameserver files including `127.0.0.53` stay on `/etc/resolv.conf`. The one-time cache is efficient but stale if systemd-resolved state changes while the daemon runs.

## Test Signals
No direct test file in this subset targets `Path`; behavior is indirectly protected by `resolvconf.go` parser tests. Comments document that the alternate path is mainly for legacy networking and may become unnecessary after legacy networking removal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/resolvconf/resolvconf_path.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/resolvconf/resolvconf_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/internal/resolvconf/resolvconf_test.go

## Purpose
Specifies the expected behavior of resolv.conf parsing, mutation, transformation, rendering, and hash-based modification detection.

## Important APIs, Types, And Functions
- `TestRCOption` validates last-option-wins lookup and empty option values.
- `TestRCWrite` exercises `WriteFile` permissions, optional hash creation, and `UserModified`.
- `TestRCModify`, `TestRCTransformForLegacyNw`, `TestRCTransformForIntNS`, `TestRCInvalidNS`, `TestRCSetHeader`, and `TestRCUnknownDirectives` compare generated content against golden files.
- `TestRCTransformForIntNSInvalidNdots` checks malformed `ndots` replacement only when the internal resolver requires ndots.
- `TestRCRead` checks file loading, missing-file error propagation, and source-path inference from `os.File`.
- `TestRCParseErrors` asserts a stable message for scanner lines exceeding `bufio.MaxScanTokenSize`.
- `BenchmarkGenerate` measures rendering overhead with representative metadata.

## Control Flow
Tests construct resolv.conf snippets in memory, parse them, apply overrides or transforms, then inspect structured fields and rendered output. Golden-file tests are the primary regression signal for exact comments and directive ordering.

## State And Persistence
Temporary directories isolate file and hash writes. Golden files under the package testdata are external expectations. No daemon state is modified.

## Dependencies And Integration Points
Uses `gotest.tools`, `google/go-cmp`, Moby `sliceutil`, and golden files. The tests document expectations consumed by sandbox DNS generation and embedded resolver setup.

## Risks
Golden tests make deliberate output changes visible but can be brittle for harmless wording changes. The path-selection helper is not directly tested here. `TestRCWrite` has OS-specific permission behavior on Windows.

## Test Signals
Coverage is broad for parser/generator edge cases: invalid nameservers are warnings, unknown directives are preserved, search override drops `"."`, host-vs-override nameserver provenance affects `HostLoopback`, and overlong input becomes a system-style parse error.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/resolvconf/resolvconf_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/rlkclient/rootlesskit_client_linux.go -->
# sources/cloud-native/moby/daemon/libnetwork/internal/rlkclient/rootlesskit_client_linux.go

## Purpose
Provides Linux RootlessKit port-driver integration so libnetwork can notify RootlessKit when port mappings are added and removed in rootless mode.

## Important APIs, Types, And Functions
- `PortDriverClient` wraps the RootlessKit API client, driver name, supported protocol set, and optional non-loopback child IP.
- `NewPortDriverClient` connects to `$ROOTLESSKIT_STATE_DIR/api.sock`, fetches RootlessKit info, returns nil when no explicit port driver is active, and validates child IP requirements for drivers that disallow loopback child addresses.
- `proto` normalizes `tcp`/`udp` to `tcp4`, `tcp6`, `udp4`, or `udp6` based on host IP family.
- `ChildHostIP` maps host bind addresses to child-namespace addresses, preserving distinct loopback addresses but using family loopback for non-loopback addresses unless a forced child IP exists.
- `ProtocolUnsupportedError` is returned for unsupported protocol/family combinations.
- `AddPort` calls RootlessKit `PortManager.AddPort` and returns a cleanup function that removes the mapping with `context.WithoutCancel`.

## Control Flow
Construction reads environment, establishes API connection, validates driver info, records supported protocols, and optionally records a non-loopback child IP from the network driver. `AddPort` is a no-op for nil clients, rejects unsupported normalized protocols, constructs a `port.Spec` with same parent/child port, and returns a deferred remover.

## State And Persistence
State is held in the client object. Actual persistence/effects are external to Docker: RootlessKit owns the port mapping state behind its API socket. Cleanup depends on the caller invoking the returned function.

## Dependencies And Integration Points
Imports RootlessKit API and port packages. Integrates with rootless port publishing and DNAT rule generation where host IPs need translation into the child namespace.

## Risks
Environment and RootlessKit version are hard prerequisites. Unsupported IPv6 with some drivers is reported at add time. If callers drop the returned cleanup function, RootlessKit mappings may leak until daemon/container cleanup. Child IP mapping correctness is critical to avoid port collisions and unreachable bindings.

## Test Signals
`rootlesskit_client_linux_test.go` focuses on `ChildHostIP`: nil client passthrough, unsupported protocol returning invalid address, forced child IP for slirp4netns, loopback preservation, and IPv4/IPv6 loopback fallback for non-loopback host IPs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/rlkclient/rootlesskit_client_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/rlkclient/rootlesskit_client_linux_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/internal/rlkclient/rootlesskit_client_linux_test.go

## Purpose
Regression tests RootlessKit child-host-IP selection without needing a live RootlessKit daemon.

## Important APIs, Types, And Functions
- `TestChildHostIP` builds synthetic `PortDriverClient` values for builtin and slirp4netns-like drivers.

## Control Flow
Each case calls `ChildHostIP` with a protocol and host IP. Expected results cover passthrough, unsupported family/protocol, forced child IP, unspecified/non-loopback translations, and loopback preservation.

## State And Persistence
No external state is used. The test directly populates the client fields that would normally come from RootlessKit `Info`.

## Dependencies And Integration Points
Uses `netip` and `gotest.tools`. It documents the contract consumed by port publishing code.

## Risks
The test does not exercise API connection setup, `AddPort`, cleanup, or RootlessKit error propagation. It is intentionally limited to pure address/protocol decision logic.

## Test Signals
The most important signal is the regression for preserving non-default IPv4 loopback addresses such as `127.0.1.2`, preventing same-port loopback bindings from collapsing to one child address.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/rlkclient/rootlesskit_client_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/setmatrix/setmatrix.go -->
# sources/cloud-native/moby/daemon/libnetwork/internal/setmatrix/setmatrix.go

## Purpose
Implements a small generic, concurrency-safe map from keys to sets of comparable values. Libnetwork uses this pattern for service record indexes and other multi-value mappings.

## Important APIs, Types, And Functions
- `set[V]` is an internal `map[V]struct{}` with `Add`, `Contains`, `Remove`, `Cardinality`, `ToSlice`, and `String`.
- `SetMatrix[K,V]` holds `map[K]set[V]` plus a mutex.
- `Get`, `Contains`, `Insert`, `Remove`, `Cardinality`, `String`, and `Keys` are the public methods.

## Control Flow
All public methods lock the mutex. `Insert` lazily initializes the matrix and creates a set for new keys. `Remove` deletes the key from the matrix when its set becomes empty. Read methods return copies or scalar values, not direct set references.

## State And Persistence
State is in-memory only. The zero value is ready to use because the map is lazily allocated. There is no deterministic ordering for slices or strings because Go map iteration order is random.

## Dependencies And Integration Points
Only depends on `fmt` and `sync`. In this subset, `libnetwork_internal_test.go` exercises `setmatrix` indirectly through service DNS records.

## Risks
The mutex is coarse-grained, which is simple but can serialize heavy use. `String` and `ToSlice` expose arbitrary ordering, so callers must not depend on stable order. `Remove` returns `set.Cardinality()` even after deleting the key, which is safe because the local set map remains valid.

## Test Signals
`setmatrix_test.go` verifies idempotent insert/remove, key deletion after last value, negative lookups, string membership, key listing, and concurrent insert/remove loops with multiple keys.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/setmatrix/setmatrix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/setmatrix/setmatrix_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/internal/setmatrix/setmatrix_test.go

## Purpose
Validates the generic set-matrix container's basic semantics and thread-safety expectations.

## Important APIs, Types, And Functions
- `TestSetSerialInsertDelete` covers all public methods in a serial sequence.
- `insertDeleteRotuine` repeatedly inserts and removes one value until context cancellation or a failed operation.
- `TestSetParallelInsertDelete` starts multiple goroutines over shared keys and values.

## Control Flow
The serial test checks duplicates do not increase cardinality, values can be queried, string output contains all values, and removing the last value removes the key. The parallel test runs competing insert/remove cycles for 10 seconds and fails if any goroutine sees an unexpected duplicate insert or missing remove for its own value.

## State And Persistence
All state is local to a `SetMatrix` value. The parallel test uses context timeout and a channel to collect completion status.

## Dependencies And Integration Points
Uses standard library concurrency primitives only. It supports confidence for libnetwork service maps that can be mutated by concurrent endpoint/service operations.

## Risks
The 10-second timeout makes the parallel test relatively slow. The test does not run with an explicit race detector here, but the mutex use should make it race-clean.

## Test Signals
Confirms zero-value readiness, cardinality accuracy, empty-key deletion, negative lookup behavior, and resilience under concurrent insert/remove operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/setmatrix/setmatrix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/uint128/uint128.go -->
# sources/cloud-native/moby/daemon/libnetwork/internal/uint128/uint128.go

## Purpose
Provides a minimal unsigned 128-bit arithmetic helper for IPv6 address math and subnet accounting without pulling in big integers.

## Important APIs, Types, And Functions
- `Uint128` stores high and low 64-bit words.
- `From16` converts a big-endian 16-byte address to `Uint128`; `Fill16` writes back.
- `From` constructs from two words.
- `Add`, `Sub`, `Lsh`, `Rsh`, `And`, and `Not` implement basic arithmetic/bit operations.
- `Uint64` returns the low word; `Uint64Sat` saturates to max uint64 if the high word is non-zero.

## Control Flow
Addition and subtraction use `math/bits` to propagate carries/borrows. Shifts split the operation across `hi` and `lo`, with special handling for counts greater than 64. Operations intentionally wrap like unsigned arithmetic.

## State And Persistence
The type is immutable by convention: methods return new values and do not mutate receivers. No persistent state exists.

## Dependencies And Integration Points
Used by `ipbits` for IPv6 address addition, subtraction, and bitfield extraction, and by default IPAM pool status to represent very large address counts before saturation.

## Risks
Shift behavior at exactly 64 uses expressions with `64-n`; in Go, shifting by zero is valid, but callers should treat this as a low-level helper with limited validation. `Uint64` silently drops high bits; callers needing capacity reporting should use `Uint64Sat`.

## Test Signals
There is no direct test file in this subset, but `ipbits_test.go` and default IPAM status paths exercise the helper indirectly for IPv6 arithmetic and saturation-sensitive subnet counts.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/uint128/uint128.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipamapi/contract.go -->
# sources/cloud-native/moby/daemon/libnetwork/ipamapi/contract.go

## Purpose
Defines libnetwork's IP Address Management contract for built-in and remote IPAM drivers, including registration, pool/address allocation, capabilities, request/response structures, and canonical errors.

## Important APIs, Types, And Functions
- `Registerer` lets drivers register by name with optional capabilities.
- `Ipam` is the driver interface: default address spaces, pool request/release, address request/release, and `IsBuiltIn`.
- `PoolStatuser` extends `Ipam` with `PoolStatus`.
- `PoolRequest` carries address space, pool, subpool, options, excluded prefixes, and IPv6 selection.
- `AllocatedPool` returns opaque pool ID, allocated prefix, and driver metadata.
- `Capability` expresses MAC-address and request-replay requirements.
- Error variables standardize invalid pool, overlap, exhaustion, duplicate IP, and out-of-range responses.

## Control Flow
This is contract-only code. Driver packages implement the interface and return these errors. The controller and network creation paths call the interface through registry lookups.

## State And Persistence
No state is stored. The opaque `PoolID` returned by drivers is persisted by higher libnetwork objects and later passed back to the same driver.

## Dependencies And Integration Points
Imports network API types for `SubnetStatus`, standard `net`/`netip`, and libnetwork `types` error classifiers. It is central to default, null, windows, and remote IPAM packages in this subset.

## Risks
`PoolRequest.Exclude` is documented as sorted, but enforcement is driver-specific. `PoolID` opacity is important; consumers parsing it would couple to one driver. Error identity matters because tests use `errors.Is` and callers may branch on classifications.

## Test Signals
Tests throughout `ipams/defaultipam`, `ipams/null`, `ipams/windowsipam`, `ipams/remote`, and `libnetwork_internal_test.go` exercise this contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipamapi/contract.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipamapi/labels.go -->
# sources/cloud-native/moby/daemon/libnetwork/ipamapi/labels.go

## Purpose
Defines reserved option label strings for libnetwork IPAM behavior.

## Important APIs, Types, And Functions
- `Prefix` is the reserved `com.docker.network` label namespace.
- `AllocSerialPrefix` is `com.docker.network.ipam.serial`, used to request serial/first-available allocation ordering.

## Control Flow
No runtime flow exists. Callers pass `AllocSerialPrefix: "true"` in address request options; default IPAM reads it in `addrSpace.requestAddress`.

## State And Persistence
No state. The string can be persisted in options maps or passed through remote IPAM requests.

## Dependencies And Integration Points
Default IPAM tests and allocation code use this label. Windows tests also pass other IPAM option labels through maps.

## Risks
Because labels are stringly typed, misspelling or non-`"true"` values silently fall back to non-serial behavior in default IPAM.

## Test Signals
`allocator_test.go` and `parallel_test.go` use `AllocSerialPrefix` to verify serial allocation/release behavior and concurrent allocation without duplicates.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipamapi/labels.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/address_space.go -->
# sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/address_space.go

## Purpose
Implements the per-address-space allocator backing default IPAM. It tracks allocated master pools, child subpools, address usage within pools, predefined dynamic pools, and pool status.

## Important APIs, Types, And Functions
- `addrSpace` contains ordered `allocated` prefixes, `subnets` map to `PoolData`, `predefined` split pools, and a mutex.
- `newAddrSpace` sorts predefined pools and removes longer overlapping entries.
- `allocateSubnet` and `allocateSubnetL` handle static master/subpool allocation and overlap checks.
- `allocatePredefinedPool` dynamically chooses the first available predefined subnet considering current allocations and reserved prefixes.
- `releaseSubnet` and `deallocate` remove pools/subpools and honor `autoRelease`.
- `requestAddress` and `releaseAddress` allocate/release addresses inside a pool or subpool.
- `allocationStatus` reports in-use and available counts with 128-bit arithmetic and uint64 saturation.

## Control Flow
All mutating and status operations lock `mu`. Static master pool allocation rejects overlaps; subpool allocation intentionally preserves historical behavior where parent overlap checks are weaker. Dynamic allocation merges current allocations with reserved prefixes, walks sorted predefined networks, handles full and partial overlaps, and inserts the selected subnet at the iterator's allocation index.

## State And Persistence
State is in-memory and lost when the allocator is rebuilt, but default IPAM advertises request replay so libnetwork can rebuild state on daemon restart. `PoolData` tracks reserved addresses and child subpools; `autoRelease` determines whether a parent is removed when the last child goes away.

## Dependencies And Integration Points
Uses `addrset` for address allocation, `netiputil` and `ipbits` for prefix ordering and arithmetic, `uint128` for counts, and `ipamapi` errors. Called by `Allocator` request/release methods.

## Risks
The dynamic allocator is subtle: it assumes sorted inputs and carefully handles duplicate/overlapping allocated and reserved prefixes. Historical subpool overlap behavior is deliberately inconsistent for compatibility. Any missed mutex path could duplicate pools or addresses under parallel network creation.

## Test Signals
`address_space_test.go` heavily covers predefined deduplication, dynamic allocation with many overlap shapes, requested subnet sizes, reserved exclusions, release/reallocation, and static ordering. `allocator_test.go` and `parallel_test.go` further stress address allocation and concurrency.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/address_space.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/address_space_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/address_space_test.go

## Purpose
Tests the lower-level address-space allocator, especially predefined dynamic pool selection and release/reuse behavior.

## Important APIs, Types, And Functions
- `TestNewAddrSpaceDedup` verifies overlapping predefined entries are sorted and deduplicated.
- `TestDynamicPoolAllocation` is a large table of allocation/reservation overlap scenarios and prefix-size requests.
- `TestStaticAllocation` checks sorted insertion of static pools.
- `TestPoolAllocateAndRelease` regresses release/reallocate behavior from Moby issue 48069.

## Control Flow
The dynamic allocation table constructs an `addrSpace`, injects existing allocations, calls `allocatePredefinedPool`, and compares returned prefix or expected error. Release tests use closures to simulate network name to subnet ownership, checking no duplicate or reserved allocation occurs.

## State And Persistence
All state is in-memory test allocator state. Tests deliberately manipulate `as.allocated` to exercise allocator internals.

## Dependencies And Integration Points
Uses `netip`, `ipamutils.NetworkToSplit`, `ipamapi` errors, and `cmpopts` for prefix-comparable assertions.

## Risks
The tests document many compatibility cases but also reveal the allocator's complexity. If reserved prefixes are not sorted in real callers despite the API contract, behavior may diverge from the tested cases.

## Test Signals
Strong coverage of full overlap, partial overlap, duplicate allocations, reserved exclusions, invalid requested sizes, specified subnet sizes larger/smaller than predefined defaults, and reusing released subnets.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/address_space_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/allocator.go -->
# sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/allocator.go

## Purpose
Implements Docker's built-in default IPAM driver. It exposes the `ipamapi.Ipam` and `PoolStatuser` contracts over four address spaces: local/global and IPv4/IPv6.

## Important APIs, Types, And Functions
- `DriverName`, `localAddressSpace`, and `globalAddressSpace` define driver identity and default address spaces.
- `Register` creates an allocator and registers it with `RequiresRequestReplay`.
- `Allocator` owns `local4`, `local6`, `global4`, and `global6` `addrSpace` instances.
- `NewAllocator` splits configured pools by IP family and initializes address spaces.
- `splitByIPFamily` validates canonical pool definitions and normalizes IPv4-mapped addresses.
- `RequestPool` parses static/dynamic pool requests, handles unspecified prefixes as dynamic size requests, validates subpools, and returns driver-specific pool IDs.
- `ReleasePool`, `RequestAddress`, `ReleaseAddress`, `PoolStatus`, and `IsBuiltIn` implement the driver API.
- `newPoolData` reserves network/subnet-router-anycast and IPv4 broadcast addresses, with RFC 3021 /31 exceptions.
- `getAddress` maps `addrset` errors into IPAM errors and supports preferred, subpool, serial, and any-address allocation.

## Control Flow
`RequestPool` requires an address space, selects v4/v6 address space, parses pool and subpool strings, treats unspecified pool addresses as dynamic requests with preferred prefix length, and delegates to `addrSpace`. `RequestAddress` parses the opaque default pool ID, converts optional preferred IP to `netip`, then delegates. `ReleaseAddress` and `ReleasePool` reverse those paths.

## State And Persistence
Allocator state is in-memory in the four `addrSpace` objects. Persistence is achieved by libnetwork replaying pool/address requests because the driver registers `RequiresRequestReplay`.

## Dependencies And Integration Points
Depends on `addrset`, `ipamapi`, `ipamutils`, libnetwork `types`, network API `SubnetStatus`, `netiputil`, and containerd logging. It is the default driver registered by `ipams/drivers.go` and used by network creation tests in `libnetwork_internal_test.go`.

## Risks
Opaque pool IDs are parseable only by this driver and encode address space plus pool/subpool. Compatibility code accepts child subnets larger than parents by collapsing them to parent behavior for pre-v24 networks. Incorrect address-space selection can cross IPv4/IPv6 or local/global state. Concurrency safety relies on `addrSpace` locks.

## Test Signals
`allocator_test.go` covers ID parsing/stringification, overlap detection, subpool behavior, dynamic predefined pools, address request/release, serial allocation, unusual /31 subnets, random deallocation, duplicate prevention, and parallel predefined pool allocation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/allocator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/allocator_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/allocator_test.go

## Purpose
Provides broad behavioral and regression coverage for the default IPAM driver.

## Important APIs, Types, And Functions
- Tests cover `PoolID` round-tripping, pool add/release, predefined dynamic pools, preferred subnet sizes, overlap checks, subpool allocation, address allocation/release, serial mode, syntax validation, unusual subnets, random deallocate/reallocate, and parallel scenarios.
- Benchmarks measure request exhaustion and pool ID conversion overhead.

## Control Flow
Tests build fresh allocators from default pools, issue IPAM API requests, and assert returned pool IDs, IPNet masks, address sequences, and error identities. Some tests intentionally request historical edge cases such as overlapping subpools and child subnet compatibility.

## State And Persistence
All allocator state is in-memory. Parallel tests use package-level synchronization for `t.Parallel` cases and errgroups for racing request/release operations.

## Dependencies And Integration Points
Uses `ipamapi`, `ipamutils`, `addrset`, `netiputil`, `types`, and `errgroup`. These tests are the main safety net for default IPAM behavior consumed by libnetwork network creation.

## Risks
Some random tests use current time as seed; failures log the seed but are not deterministic by default. Several tests are skipped or constrained by Go test parallelism flags. Heavy allocation loops can be expensive for large subnets, so some exhaustive cases are commented out.

## Test Signals
Strong signals include duplicate address prevention under concurrent release/request, `ErrNoAvailableIPs` on exhaustion, `ErrIPOutOfRange` on invalid preferred addresses, reusing released addresses, preserving /31 usable endpoints, and maintaining compatibility with documented validation inconsistencies.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/allocator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/parallel_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/parallel_test.go

## Purpose
Stress-tests default IPAM under concurrent pool, address allocation, and address release workloads.

## Important APIs, Types, And Functions
- `testContext` stores allocator, options, allocated IPs, pool ID, and expected capacity.
- `TestRequestPoolParallel` allocates every /24 from a /10 predefined range concurrently.
- `TestFullAllocateRelease`, `TestOddAllocateRelease`, and serial-release variants run address allocation and release with varying parallelism.
- `allocate` and `release` are helper routines using semaphores, goroutines, and errgroups.

## Control Flow
Tests allocate more goroutines than available IPs, collect successful allocations, assert no duplicates and exact capacity, then release all/odd/even subsets in parallel. Pool parallel test builds the expected complete subnet list and ensures all were allocated exactly once.

## State And Persistence
State is in-memory within the allocator and test context. The helpers coordinate with channels, wait groups, semaphores, and errgroups.

## Dependencies And Integration Points
Uses `errgroup`, `semaphore`, `ipamapi.AllocSerialPrefix`, and `ipamutils`. It validates `addrSpace` mutex behavior under real driver calls.

## Risks
Concurrency tests can be timing-sensitive. Some helper code ignores errors from `RequestAddress` during over-capacity goroutine runs and filters nils, which is intentional for exhaustion but could mask unexpected error types.

## Test Signals
Key signal is no duplicate IPs and no release failures across masks /29, /25, /24, /23, and /21 with parallelism up to 8.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/parallel_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/structures.go -->
# sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/structures.go

## Purpose
Defines default IPAM internal data structures for pool identity, pool data, subnet keys, and merged prefix iteration.

## Important APIs, Types, And Functions
- `PoolID` combines an address space with a `SubnetKey`.
- `PoolData` holds allocated addresses, child subpools, and auto-release marker.
- `SubnetKey` stores master and child prefixes and exposes `Is6`.
- `PoolIDFromString` parses `addressSpace/ip/bits` or `addressSpace/ip/bits/child/bits`.
- `(*PoolID).String` serializes the opaque ID used by the driver.
- `(*PoolData).String` prints child count for debugging.
- `mergeIter` merges two sorted prefix slices without allocating a combined slice.

## Control Flow
Pool ID parsing splits on `/`, expects 3 or 5 parts, and reconstructs CIDR strings for `netip.ParsePrefix`. `mergeIter` tracks indexes into allocated and reserved slices and selects the next item according to a caller-supplied comparator.

## State And Persistence
`PoolID.String` output is persisted by libnetwork as the driver's opaque pool ID. `PoolData` is in-memory allocator state. `mergeIter` is transient during dynamic allocation.

## Dependencies And Integration Points
Depends on `addrset` for per-pool address tracking and libnetwork `types` for invalid parameter errors. Used by `allocator.go` and `address_space.go`.

## Risks
Pool ID parsing assumes address spaces do not contain `/`. IPv6 prefixes contain colons but still split correctly on slash. Consumers outside the driver should not parse this ID despite its readable form. `mergeIter` assumes both input slices are sorted.

## Test Signals
`allocator_test.go` tests pool ID round-tripping and benchmarks conversions. `structures_test.go` verifies merge iteration order when allocated and reserved contain equal prefixes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/structures.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/structures_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/structures_test.go

## Purpose
Tests the `mergeIter` helper used by dynamic predefined pool allocation.

## Important APIs, Types, And Functions
- `TestMergeIter` constructs allocated and reserved prefix slices and advances `newMergeIter`.

## Control Flow
The test expects the iterator to return allocated and reserved equal prefixes in comparator order, then subsequent allocated prefixes, then the zero prefix sentinel after exhaustion.

## State And Persistence
No persistent state. The iterator mutates only its internal indices.

## Dependencies And Integration Points
Uses `netiputil.PrefixCompare`, matching the comparator used in `address_space.go`.

## Risks
The test is narrow and does not cover all merge iterator edge cases, but broader dynamic allocation tests exercise it through allocator behavior.

## Test Signals
Confirms duplicate equal prefixes across allocated/reserved streams are both visible to the dynamic allocation algorithm.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/defaultipam/structures_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/drivers.go -->
# sources/cloud-native/moby/daemon/libnetwork/ipams/drivers.go

## Purpose
Registers all IPAM drivers that libnetwork should know about: default, Windows, null, and remote plugin drivers.

## Important APIs, Types, And Functions
- `Register(r, pg, lAddrPools, gAddrPools)` sequentially calls `defaultipam.Register`, `windowsipam.Register`, `null.Register`, and `remote.Register`.

## Control Flow
Registration stops at the first error. The default driver receives configured local/global pools; Windows registration is a no-op on non-Windows builds; remote registration also installs plugin activation handling.

## State And Persistence
No direct state, but it populates the libnetwork IPAM registry passed through `ipamapi.Registerer`.

## Dependencies And Integration Points
Imports all IPAM driver packages, `ipamutils` for configured address pools, and `plugingetter` for managed plugin discovery. Called during controller initialization.

## Risks
Ordering matters: built-ins are registered before remote plugin handlers. A default registration failure prevents null or remote drivers from registering. Remote registration behavior changes depending on whether a plugin getter is available.

## Test Signals
Driver registration is indirectly covered by libnetwork controller tests and specific driver tests; this file has no direct test in the subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/drivers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/null/null.go -->
# sources/cloud-native/moby/daemon/libnetwork/ipams/null/null.go

## Purpose
Implements a built-in null IPAM driver that satisfies the IPAM contract without reserving specific pools or addresses.

## Important APIs, Types, And Functions
- `DriverName` is `"null"`; default address space is `"null"`.
- Default pools are `0.0.0.0/0` and `::/0` with corresponding pool IDs.
- `allocator` implements `ipamapi.Ipam`.
- `RequestPool` accepts only the default address space and no explicit pool/subpool, then returns the v4 or v6 default pool.
- `RequestAddress` returns nil address/data for valid default pool IDs.
- `ReleasePool` is always successful; `ReleaseAddress` validates pool ID.
- `Register` registers the driver name.

## Control Flow
The driver rejects address spaces other than `"null"` and rejects specific pool/subpool requests because it does not manage real ranges. Address requests do not allocate and always return nil for recognized pools.

## State And Persistence
Stateless; no pool or address usage is stored.

## Dependencies And Integration Points
Uses `ipamapi` and libnetwork `types` errors. It can be selected by networks that do not need Docker-managed IPAM.

## Risks
Because it returns nil addresses, callers must be prepared for no allocated address. It only validates pool IDs on address operations, so pool releases are no-ops for any string.

## Test Signals
`null_test.go` verifies v4/v6 default pool return, rejection of unknown address space and explicit pools/subpools, nil address results for valid pools, and errors for unknown pool IDs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/null/null.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/null/null_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/ipams/null/null_test.go

## Purpose
Tests the stateless null IPAM driver's accepted and rejected request forms.

## Important APIs, Types, And Functions
- `TestPoolRequest` validates default IPv4/IPv6 pool allocation and invalid pool request errors.
- `TestOtherRequests` validates nil address responses and unknown pool ID errors.

## Control Flow
Tests instantiate `allocator{}` directly and issue IPAM API calls. Assertions check exact pool IDs, prefixes, and error substrings.

## State And Persistence
No persistent or shared state.

## Dependencies And Integration Points
Uses `ipamapi` and `gotest.tools`. The tests establish the behavior expected by users selecting the `null` IPAM driver.

## Risks
The tests do not cover `ReleasePool`, `ReleaseAddress` valid path, or `Register`, but those paths are trivial.

## Test Signals
Confirms the driver is intentionally narrow: only empty pool/subpool requests in the `"null"` address space are valid.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/null/null_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/remote/api/api.go -->
# sources/cloud-native/moby/daemon/libnetwork/ipams/remote/api/api.go

## Purpose
Defines JSON-serializable request and response structures for the remote IPAM plugin protocol.

## Important APIs, Types, And Functions
- `Response` embeds the common plugin `Error` string and implements `IsSuccess` and `GetError`.
- `GetCapabilityResponse` and `ToCapability` convert plugin capability fields to `ipamapi.Capability`.
- `GetAddressSpacesResponse`, `RequestPoolRequest`, `RequestPoolResponse`, `ReleasePoolRequest`, `ReleasePoolResponse`, `RequestAddressRequest`, `RequestAddressResponse`, `ReleaseAddressRequest`, and `ReleaseAddressResponse` model plugin RPC payloads.

## Control Flow
This file contains no RPC logic. The remote allocator sends these structures through the plugin client and checks the embedded `Response`.

## State And Persistence
No state. Payloads are transient request/response values.

## Dependencies And Integration Points
Depends on `ipamapi` only for capability conversion. Used by `remote.go` and remote plugin tests.

## Risks
Protocol fields are exported and stringly typed for JSON compatibility. Remote plugins must return CIDR-formatted pools and addresses; parsing errors surface later in `remote.go`.

## Test Signals
`remote_test.go` uses these payload shapes through an HTTP test plugin, including capabilities, default address spaces, pool data, and address responses.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/remote/api/api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/remote/remote.go -->
# sources/cloud-native/moby/daemon/libnetwork/ipams/remote/remote.go

## Purpose
Implements the IPAM driver adapter for remote Docker plugins. It translates `ipamapi.Ipam` calls into plugin RPC calls and registers active/activated plugins.

## Important APIs, Types, And Functions
- `allocator` holds plugin client and name.
- `PluginResponse` abstracts responses with `IsSuccess` and `GetError`.
- `newAllocator` constructs an `ipamapi.Ipam`.
- `Register` registers existing managed plugins and installs a handler for future plugin activation.
- `getPluginClient` adapts v1 plugin clients or managed plugin addresses into `plugins.Client`.
- `call` invokes `IpamDriver.<method>` and converts plugin error fields into Go errors.
- `getCapabilities`, `GetDefaultAddressSpaces`, `RequestPool`, `requestPool`, `checkOverlaps`, `ReleasePool`, `RequestAddress`, `ReleaseAddress`, and `IsBuiltIn` implement the driver behavior.

## Control Flow
Registration probes plugin capabilities when possible; legacy plugins without capabilities are still registered. `RequestPool` first gets the global default address space, calls the plugin, and for local dynamic requests loops while returned pools overlap the request's excluded prefixes. Overlapping temporary leases are held to prevent the plugin from returning the same pool again, then released in a deferred cleanup.

## State And Persistence
The adapter itself stores only plugin endpoint/name. Actual allocation state is owned by the remote plugin. Temporary overlapping leases are released before returning from `RequestPool`.

## Dependencies And Integration Points
Uses Moby plugin APIs, `plugingetter`, `ipamapi`, remote API structs, libnetwork `types`, and containerd logging. It integrates plugin lifecycle with libnetwork's IPAM registry.

## Risks
Remote correctness depends on plugin behavior and protocol compatibility. The overlap loop can spin until plugin exhaustion/error if the plugin keeps handing excluded ranges. The code preserves old request-pool behavior including skipping overlap checks for explicit pools, global address space, and `0.0.0.0/0`. Missing or invalid address strings produce `ErrNoIPReturned` or parse errors.

## Test Signals
`remote_test.go` validates capability probing, legacy capability failure, default address space retrieval, pool/subpool request payload handling, metadata propagation, address request/release, and plugin spec HTTP setup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/remote/remote.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/remote/remote_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/ipams/remote/remote_test.go

## Purpose
Tests the remote IPAM plugin adapter against a local HTTP plugin simulation.

## Important APIs, Types, And Functions
- `handle` registers RPC endpoint handlers for `IpamDriver.<method>`.
- `setupPlugin` creates a plugin spec file and activation endpoint around an `httptest.Server`.
- `TestGetCapabilities`, `TestGetCapabilitiesFromLegacyDriver`, `TestGetDefaultAddressSpaces`, and `TestRemoteDriver` cover adapter behavior.

## Control Flow
Tests write temporary plugin specs in Docker's plugin directory, discover the plugin via `plugins.Get`, build a client with `getPluginClient`, then call the allocator. The test plugin decodes JSON request maps and emits expected response maps.

## State And Persistence
The tests mutate the system plugin spec directory (`/etc/docker/plugins` on Unix, ProgramData path on Windows) and clean it afterward. Server state is in-memory.

## Dependencies And Integration Points
Uses `httptest`, Moby `plugins`, and `ipamapi`. This is a relatively integration-style unit test because it exercises plugin discovery and HTTP transport.

## Risks
Writing under `/etc/docker/plugins` can require permissions or conflict in constrained environments. The overlap-loop behavior in `RequestPool` is not deeply tested here.

## Test Signals
Confirms endpoint names, JSON field names, capability conversion, metadata propagation, pool/subpool ID formatting by plugin, default address space strings, preferred address forwarding, and release payload validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/remote/remote_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/windowsipam/windowsipam.go -->
# sources/cloud-native/moby/daemon/libnetwork/ipams/windowsipam/windowsipam.go

## Purpose
Provides the built-in Windows IPAM driver. It behaves like a minimal/null-style IPAM for Windows local networks while returning explicit requested pools when supplied.

## Important APIs, Types, And Functions
- Build-tagged for Windows only.
- `DefaultIPAM` is `"windows"`.
- Default address spaces are `LocalDefault` and `GlobalDefault`; default pool is `0.0.0.0/0`.
- `Register` registers the driver.
- `RequestPool` rejects subpools and IPv6, parses an explicit pool if supplied, otherwise returns default pool.
- `RequestAddress` parses the pool ID as CIDR and returns the preferred address with the pool mask, or nil if no preferred address is supplied.
- Release methods are no-ops with logging; `IsBuiltIn` returns true.

## Control Flow
Pool requests are simple: validate unsupported features, choose default or parsed pool, and return pool string as pool ID. Address requests require pool ID to parse as CIDR, then echo preferred IP when present.

## State And Persistence
Stateless; Windows HNS or higher layers own actual network/address state.

## Dependencies And Integration Points
Uses `ipamapi`, libnetwork `types`, `net/netip`, and logging. Registered from `ipams/drivers.go` only on Windows builds.

## Risks
No overlap or allocation tracking is performed. IPv6 and subpools are explicitly unsupported. The comment mentions allocating `0.0.0.0/32` by default, but implementation returns nil for no preferred address.

## Test Signals
`windowsipam_test.go` validates default and explicit pool responses, unsupported subpool/IPv6 errors, preferred address echoing, options tolerance, and no-op releases on Windows builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/windowsipam/windowsipam.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/windowsipam/windowsipam_other.go -->
# sources/cloud-native/moby/daemon/libnetwork/ipams/windowsipam/windowsipam_other.go

## Purpose
Provides a non-Windows build stub for the Windows IPAM package.

## Important APIs, Types, And Functions
- Build-tagged `!windows`.
- `Register(ipamapi.Registerer) error` is a no-op returning nil.

## Control Flow
No runtime behavior beyond successful return.

## State And Persistence
No state.

## Dependencies And Integration Points
Allows `ipams/drivers.go` to import and call `windowsipam.Register` on all platforms without conditional compilation in the caller.

## Risks
None beyond ensuring Windows-only behavior is not accidentally expected on other platforms.

## Test Signals
No direct test; cross-platform compilation is the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/windowsipam/windowsipam_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/windowsipam/windowsipam_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/ipams/windowsipam/windowsipam_test.go

## Purpose
Windows-only tests for the Windows IPAM driver contract.

## Important APIs, Types, And Functions
- `TestWindowsIPAM` exercises `RequestPool`, `ReleasePool`, `RequestAddress`, and `ReleaseAddress`.

## Control Flow
The test requests default and explicit pools, checks unsupported subpool and IPv6 errors, releases a pool, requests nil and preferred addresses, passes a gateway request option, and releases the address.

## State And Persistence
No persistent state; the allocator is stateless.

## Dependencies And Integration Points
Uses `ipamapi`, `netlabel.Gateway`, libnetwork `types`, and `gotest.tools`. Build tag means it only runs on Windows.

## Risks
Does not verify integration with HNS or controller network creation. It documents the minimal behavior rather than full Windows networking semantics.

## Test Signals
Confirms the driver returns `0.0.0.0/0` by default, echoes explicit pools, rejects unsupported features, and returns preferred IPs with the pool mask.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipams/windowsipam/windowsipam_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipamutils/utils.go -->
# sources/cloud-native/moby/daemon/libnetwork/ipamutils/utils.go

## Purpose
Provides default IPAM address-pool definitions and helper methods for splitting base networks into smaller allocatable prefixes.

## Important APIs, Types, And Functions
- `NetworkToSplit` combines a base `netip.Prefix` and target subnet size.
- `FirstPrefix` returns the first subnet derived from the base and size.
- `Overlaps` checks whether a prefix overlaps the base.
- `GetGlobalScopeDefaultNetworks` and `GetLocalScopeDefaultNetworks` return shallow clones of default pool slices.

## Control Flow
No complex flow. Defaults include Docker's local IPv4 private ranges and global `10.0.0.0/8` split into /24 pools.

## State And Persistence
Default slice variables are package-level. Getter functions clone the slice header but not the pointed-to `NetworkToSplit` structs, so callers modifying struct fields through pointers can mutate shared defaults.

## Dependencies And Integration Points
Used by default IPAM registration and tests. `NetworkToSplit` values are also accepted as user-configured default address pools.

## Risks
The shallow clone behavior is a mutation risk. Default pool definitions are IPv4-only here unless callers provide IPv6 pools. Validation of canonical form happens in default IPAM, not these helpers.

## Test Signals
Covered indirectly by default IPAM tests that consume defaults and custom `NetworkToSplit` lists.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipamutils/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipbits/ipbits.go -->
# sources/cloud-native/moby/daemon/libnetwork/ipbits/ipbits.go

## Purpose
Implements numeric and bitfield helpers for `netip.Addr`, supporting both IPv4 and IPv6.

## Important APIs, Types, And Functions
- `Add(ip, x, shift)` returns `ip + (x << shift)`.
- `SubnetsBetween(a1, a2, sz)` returns how many `sz`-sized subnets fit between two addresses, capped by `uint128.Uint64`.
- `subAddr` subtracts one address from another using `uint128`.
- `Field(ip, u, v)` extracts a bitfield where bit 0 is the most significant bit.

## Control Flow
IPv4 paths use big-endian uint32 operations. IPv6 paths convert addresses to `uint128`. `SubnetsBetween` validates address family/order, masks both endpoints to prefix size, subtracts, then right-shifts by host-bit count.

## State And Persistence
Pure functions, no state.

## Dependencies And Integration Points
Depends on internal `uint128`. Used by default IPAM dynamic pool allocation to measure gaps between prefixes and by other address math paths.

## Risks
`Add` wraps on overflow. `Field` documents undefined behavior for invalid ranges. `SubnetsBetween` returns zero for invalid/mismatched inputs, which callers must distinguish from a valid no-gap result if needed.

## Test Signals
`ipbits_test.go` covers IPv4/IPv6 addition, bitfield extraction, subnet distances, and benchmarks allocation-free address addition.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipbits/ipbits.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipbits/ipbits_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/ipbits/ipbits_test.go

## Purpose
Tests IP address arithmetic helpers used by IPAM allocation logic.

## Important APIs, Types, And Functions
- `TestAdd` validates IPv4 and IPv6 shifted additions.
- `BenchmarkAdd` measures IPv4/IPv6 add performance.
- `TestField` verifies bitfield extraction across byte and wider boundaries.
- `TestSubnetsBetween` validates subnet counts for IPv4 and IPv6 gaps.

## Control Flow
Table-driven tests compare pure function outputs against known addresses or integer values.

## State And Persistence
No state.

## Dependencies And Integration Points
Uses `netip` and `gotest.tools`. The expected values mirror default IPAM gap-detection needs.

## Risks
Tests do not cover invalid argument behavior for `Field`, which is explicitly undefined. Overflow behavior is not asserted.

## Test Signals
Confirms IPv6 128-bit arithmetic works for high-bit shifts and large subnet counts such as `/64` gaps.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/ipbits/ipbits_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/iptables/conntrack.go -->
# sources/cloud-native/moby/daemon/libnetwork/iptables/conntrack.go

## Purpose
Deletes Linux conntrack state associated with container IP addresses or published ports so stale NAT/connection entries do not outlive network changes.

## Important APIs, Types, And Functions
- `checkConntrackProgrammable` verifies the netlink handle supports `NETLINK_NETFILTER`.
- `DeleteConntrackEntries` purges flows by IPv4/IPv6 container IP lists.
- `DeleteConntrackEntriesByPort` purges flows matching protocol, destination port, and optional host IP.
- `purgeConntrackState` deletes NAT-any-IP conntrack entries for one address/family.

## Control Flow
Both public functions return early for empty inputs, check netfilter support, then iterate targets. Per-target filter construction or deletion failures are logged and skipped so one bad entry does not abort the whole cleanup. Port cleanup queries both IPv4 and IPv6 families for each binding.

## State And Persistence
Effects are external kernel conntrack table mutations through netlink. No Go state persists.

## Dependencies And Integration Points
Uses libnetwork `nlwrap.Handle`, `types.PortBinding`, vishvananda `netlink`, and Linux syscall constants. Called by networking code when endpoint/port mappings change.

## Risks
Filtering by NAT-any-IP or port can delete broader state than intended if assumptions about unique subnets or bindings are violated. Unspecified host IP intentionally skips destination-IP filter because real conntrack entries use concrete interface IPs. Errors after initial programmability check are warnings, not returned.

## Test Signals
No direct tests in this subset. Behavior is integration-sensitive and depends on kernel netfilter support.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/iptables/conntrack.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/iptables/firewalld.go -->
# sources/cloud-native/moby/daemon/libnetwork/iptables/firewalld.go

## Purpose
Integrates Docker's iptables programming with Linux firewalld over D-Bus. It detects firewalld, applies Docker zone/policy setup, proxies iptables calls through firewalld passthrough, and reacts to reload signals.

## Important APIs, Types, And Functions
- `Conn` stores D-Bus connection, runtime/config objects, and signal channel.
- `UsingFirewalld` and `FirewalldReloadedAt` expose current integration status.
- `firewalldInit`, `newConnection`, `signalHandler`, `dbusConnectionChanged`, `connectionEstablished`, `connectionLost`, `reloaded`, and `OnReloaded` manage lifecycle and callbacks.
- `checkRunning` probes service availability.
- `passthrough` calls `direct.passthrough`.
- `firewalldZone.settings`, `setupDockerZone`, and `setupDockerForwardingPolicy` create permanent Docker firewalld configuration.
- `AddInterfaceFirewalld` and `DelInterfaceFirewalld` manage runtime interface membership in the Docker zone.
- `interfaceNotFound` marks not-found errors.

## Control Flow
Initialization honors `DOCKER_TEST_NO_FIREWALLD`, connects to the system bus, checks running state, starts a signal handler when connected, ensures the `docker` zone and forwarding policy exist, and reloads firewalld if configuration was added. Reload signals invoke registered callbacks under a mutex and update an atomic timestamp.

## State And Persistence
Global process state tracks connection, running flag, callbacks, and last reload time. Persistent firewalld config is modified by adding the Docker zone and forwarding policy. Runtime zone interfaces are modified through D-Bus.

## Dependencies And Integration Points
Uses `github.com/godbus/dbus/v5`, containerd logging, and package-local iptables passthrough. `iptables.Raw` uses firewalld passthrough when `firewalldRunning` is true.

## Risks
Global mutable state and asynchronous D-Bus signals are concurrency-sensitive. Some operations ignore unknown-method or name-conflict errors for compatibility. Firewalld running in the host namespace is skipped in rootless mode by `iptables.go`. Runtime interface deletion returns a typed not-found error.

## Test Signals
`firewalld_test.go` runs only when D-Bus/firewalld are available. It tests initialization, reload callback recreation of rules, and passthrough add/delete.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/iptables/firewalld.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/iptables/firewalld_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/iptables/firewalld_test.go

## Purpose
Integration-tests firewalld-backed iptables behavior on Linux hosts where firewalld is available.

## Important APIs, Types, And Functions
- `skipIfNoFirewalld` detects D-Bus/firewalld availability.
- `TestFirewalldInit` checks initialization.
- `TestReloaded` verifies registered reload callbacks restore rules after flush/removal.
- `TestPassthrough` adds and deletes an INPUT rule through firewalld passthrough.

## Control Flow
Tests skip when system D-Bus or firewalld is absent. Reload test creates a forwarding chain and jump, adds link rules, registers `OnReloaded`, removes rules, calls `reloaded`, and checks rules are recreated.

## State And Persistence
Mutates host/test namespace iptables and firewalld runtime state. Cleanup removes chains/rules where possible.

## Dependencies And Integration Points
Uses D-Bus, `GetIptable`, `ChainInfo.Link`, and package reload machinery. These are closer to integration tests than pure unit tests.

## Risks
Host environment controls whether tests run. Firewalld in a different namespace can make rule visibility tricky. Cleanup failures could leave test rules on development machines.

## Test Signals
Confirms the D-Bus passthrough path can program real rules and that reload callbacks are sufficient to rebuild Docker rules after firewalld reload.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/iptables/firewalld_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/iptables/iptables.go -->
# sources/cloud-native/moby/daemon/libnetwork/iptables/iptables.go

## Purpose
Provides Linux iptables/ip6tables programming helpers for libnetwork. It abstracts tables, chains, actions, policy management, idempotent rule operations, firewalld passthrough, rootless namespace execution, and xtables lock waiting.

## Important APIs, Types, And Functions
- Types: `Action`, `Policy`, `Table`, `IPVersion`, `IPTable`, `ChainInfo`, `ChainError`, and `Rule`.
- `GetIptable` constructs an IPTable for IPv4 or IPv6.
- `NewChain`, `RemoveExistingChain`, `ChainInfo.Remove`, `Prerouting`, `Output`, and `Link` manage chains and common linking rules.
- `ProgramRule`, `Exists`, `ExistsNative`, `Raw`, `raw`, `RawCombinedOutput`, and `RawCombinedOutputNative` implement idempotent command execution.
- `FlushChain`, `SetDefaultPolicy`, `HasPolicy`, `AddReturnRule`, `EnsureJumpRule`, and `DeleteJumpRule` manage common chain state.
- `Rule` wraps a rule with idempotent `Append`, `Insert`, `Delete`, `Exists`, `WithChain`, and `String`.

## Control Flow
Initialization is lazy through `initOnce`, detecting firewalld and iptables binaries. `Raw` prefers firewalld passthrough when running, falling back to native iptables for missing D-Bus service-file errors. Native execution prepends `--wait`, optionally wraps the command with `nsenter` into a detached rootless namespace, runs combined output, filters xtables-lock warnings, and logs slow operations.

## State And Persistence
Global binary paths and firewalld state are cached. The main effects are kernel iptables/nftables rule mutations. `Rule` values are immutable-ish wrappers around command arguments.

## Dependencies And Integration Points
Uses `os/exec`, rootless namespace helpers, firewalld functions, and containerd logging. It is a central integration point for bridge networking, port publishing, forwarding, NAT, and cleanup paths.

## Risks
Host binary availability, permissions, firewalld state, namespace selection, and xtables contention all affect behavior. Some remove paths intentionally ignore errors for cleanup idempotency. `Exists` cannot report initialization errors and returns false. `EnsureJumpRule` deletes then inserts, which may briefly remove a jump.

## Test Signals
`iptables_test.go` tests chain creation, link rule pairs, PREROUTING/OUTPUT rules, concurrent programming with `--wait`, cleanup, raw exists checks, `Rule` idempotency, and flushing. Tests require Linux iptables and sometimes isolate with test network namespaces.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/iptables/iptables.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/iptables/iptables_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/iptables/iptables_test.go

## Purpose
Integration-tests Linux iptables helper behavior against actual iptables commands.

## Important APIs, Types, And Functions
- `createNewChain` sets up NAT and filter chains.
- `TestNewChain`, `TestLink`, `TestPrerouting`, `TestOutput`, `TestConcurrencyWithWait`, `TestCleanup`, `TestExistsRaw`, `TestRule`, and `TestFlushChain` cover the helper API.
- `addSomeRules` adds representative DNAT, filter, and masquerade rules.
- `mustDumpChain` inspects chain rules through `iptables -S`.

## Control Flow
Tests create chains, add rules via helper methods, verify existence through `Exists` or `iptables-save`, and clean up. Some tests use `netnsutils.SetupTestOSContext` to isolate rules; firewalld-running cases are skipped where host namespace passthrough cannot modify the test namespace.

## State And Persistence
Mutates iptables state and depends on cleanup. Uses hard-coded test chain names such as `DOCKEREST`, `TESTCHAIN`, and `TESTFLUSHCHAIN`.

## Dependencies And Integration Points
Requires Linux, iptables binaries, suitable privileges, and sometimes network namespace support. Uses `errgroup` for concurrent rule additions.

## Risks
Environment sensitivity is high. Missing privileges or firewalld namespace mismatches can skip or fail tests. Hard-coded chain names can collide if cleanup failed from a previous run.

## Test Signals
Confirms idempotent rule operations, exact reciprocal link rules, `--wait` preventing xtables lock failures under concurrency, cleanup removing chain references, raw existence checks rejecting truncated rules, and flush preserving empty chain definitions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/iptables/iptables_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/libnetwork_internal_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/libnetwork_internal_test.go

## Purpose
Provides internal libnetwork tests for JSON persistence, IPAM cleanup, service DNS records, endpoint labels, auxiliary address validation, SRV lookup, and failure rollback behavior.

## Important APIs, Types, And Functions
- `TestNetworkMarshalling` and `TestEndpointMarshalling` validate JSON round-trip of private network/endpoint fields.
- Comparison helpers check IPAM configs, IPAM info, endpoint interfaces, maps, and address lists.
- `TestAuxAddresses` validates aux-address ranges during `ipamAllocate`.
- `TestEndpointNameLabel` checks endpoint name is included in IPAM options.
- `TestUpdateSvcRecord`, `getSvcRecords`, `TestSRVServiceQuery`, and `TestServiceVIPReuse` cover service DNS record maps and resolver behavior.
- `TestIpamReleaseOnNetDriverFailures` verifies IPAM allocations are released after network or endpoint driver failures.
- `badDriver` simulates network driver failures.

## Control Flow
Tests create controllers with temp data directories and isolated network namespaces where needed, create networks/endpoints/sandboxes, mutate service records, resolve names/IPs/services, and assert expected cleanup. The bad driver first fails network creation, then endpoint creation, to verify different rollback paths.

## State And Persistence
Marshalling tests exercise JSON persistence of network/endpoint structs. Other tests create temporary controller state and modify in-memory service maps. Network namespace and bridge setup are external OS state isolated by test helpers.

## Dependencies And Integration Points
Integrates default IPAM, bridge driver behavior, service record `setmatrix`, netlabel constants, netutils reverse-IP logic, driver registry, and controller lifecycle.

## Risks
Tests are platform-sensitive and skip Windows for Linux-only bridge/namespace behavior. They rely on cleanup through `defer`; failures can leave transient network state. These tests also exercise private fields, making refactors visible.

## Test Signals
Strong signals include persistence compatibility for private fields, aux-address validation against pools/subpools, endpoint-name metadata reaching IPAM, v4/v6 DNS record add/delete, SRV target resolution, service VIP reference counting by service ID, and IPAM release after driver failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/libnetwork_internal_test.go -->
