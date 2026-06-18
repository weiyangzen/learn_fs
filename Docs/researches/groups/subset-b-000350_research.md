# subset-b-000350 Research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/errors/errors.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/errors/errors.go

Purpose: centralizes reftracker error values and formatting helpers. The key exported sentinel is `ErrObjectOutOfDate`, used to represent failed RADOS `AssertVersion` optimistic-concurrency checks.

APIs and control flow: `UnexpectedReadSize`, `UnknownObjectVersion`, `FailedObjectRead`, and `FailedObjectWrite` wrap low-level errors with stable context. `TryRADOSAborted` inspects `rados.OperationError`, then an `ErrorCode()`-bearing operation error, mapping negative `EOVERFLOW` and `ERANGE` into `ErrObjectOutOfDate`; non-RADOS errors pass through, while unmatched RADOS operation errors return `nil`.

State and dependencies: no persistence. Depends on `github.com/ceph/go-ceph/rados` error shape and `golang.org/x/sys/unix` errno constants.

Integration points: called from v1 read/write paths to normalize stale-generation failures and from encoding parsers for length mismatch diagnostics.

Risks: `TryRADOSAborted` returning `nil` for unrecognized RADOS operation errno can suppress an underlying operation failure when wrapped through `FailedObjectRead/Write`. The comment above `FailedObjectWrite` incorrectly repeats `FailedObjectRead`.

Test signals: no direct test file in this subset, but v1 tests assert stale generation surfaces as `ErrObjectOutOfDate`.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/errors/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/radoswrapper/fakerados.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/radoswrapper/fakerados.go

Purpose: in-memory fake implementation of the reftracker RADOS wrapper interfaces for deterministic unit tests without a Ceph cluster.

APIs and types: `FakeRados` owns an object map; `FakeObj` stores object id, version, xattrs, omap, and data; `FakeIOContext` tracks last object version. `FakeWriteOp` and `FakeReadOp` collect operation steps keyed by internal executor indices. `fakeRadosError` implements `ErrorCode()` for errno-like failures.

Control flow: write and read operations execute in fixed order. Writes apply assert-version, remove, create, xattr, data, omap removal, and omap set steps, then increment the object version and `LastObjVersion` when the object still exists. Reads apply assert-version, object read, and omap lookup, then update `LastObjVersion`. `GetXattr` returns not-found or ENODATA-style errors.

State and persistence: purely in-memory process state. Input byte slices and maps are copied when queued so later caller mutation does not affect fake operations.

Dependencies and integration: mirrors the subset of go-ceph RADOS APIs used by reftracker. Tests build `FakeObj` fixtures directly to validate low-level v1 behavior and top-level idempotency.

Risks: fake operation ordering may not perfectly match librados semantics in all mixed-step combinations. The fake is not concurrency-safe, so it models serial operations rather than true parallel writers. Its version behavior increments after most mutating operations, including creation and metadata changes, which is suitable for current tests but remains a contract to watch.

Test signals: heavily exercised by reftracker, v1, and version tests as the backing store for success, not found, object exists, stale generation, xattr, omap, and read-size scenarios.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/radoswrapper/fakerados.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/radoswrapper/interface.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/radoswrapper/interface.go

Purpose: declares narrow wrapper interfaces around go-ceph RADOS types so reftracker logic can run against both real RADOS and the fake test implementation.

APIs: `IOContextW` exposes last-version lookup, xattr read, and factory methods for read/write ops. `WriteOpW` supports create, remove, xattr, full-object write, omap set/remove, assert-version, operate, and release. `ReadOpW` supports data reads, omap lookup by keys, assert-version, operate, and release. `ReadOpOmapGetValsByKeysStepW` exposes iterator `Next`.

Control flow and state: interfaces themselves hold no state, but they define the atomic operation surface used by v1 `Init`, `Add`, `Remove`, and `readObjectByKeys`.

Dependencies: imports go-ceph `rados` for create options, read steps, and omap key/value types.

Integration points: implemented by `radoswrapper.go` for production and `fakerados.go` for tests. This boundary is the main testability seam for reftracker persistence and concurrency checks.

Risks: the interface is intentionally minimal; any reftracker change needing additional RADOS features must update both real and fake implementations. Semantics of `AssertVersion` and `GetLastVersion` depend on go-ceph behavior and fake parity.

Test signals: validated indirectly because compile-time assertions in implementations require interface conformance and tests run reftracker logic through fake `IOContextW`.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/radoswrapper/interface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/radoswrapper/radoswrapper.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/radoswrapper/radoswrapper.go

Purpose: production wrapper implementation adapting go-ceph `rados.IOContext`, `WriteOp`, `ReadOp`, and omap iterators to the internal interfaces.

APIs and control flow: `NewIOContext` wraps an existing `*rados.IOContext`. `CreateWriteOp` and `CreateReadOp` allocate go-ceph ops while retaining the IO context needed by `Operate`. Methods mostly delegate directly to embedded go-ceph operations, with `Operate` passing `rados.OperationNoFlag`.

State and persistence: no independent persistence; all state lives in Ceph/RADOS and go-ceph operation handles. `Release` forwards resource cleanup to go-ceph.

Dependencies: `github.com/ceph/go-ceph/rados`.

Integration points: top-level reftracker callers pass this wrapper around real pools. It is the production counterpart to `FakeIOContext`.

Risks: thin wrappers mean correctness depends on preserving go-ceph operation lifecycle, especially `Release` and assert-version behavior. No direct retries are here; stale writes are surfaced to callers through reftracker error wrapping.

Test signals: no direct unit tests here. Coverage is mostly compile-time and via fake implementation parity; production behavior relies on go-ceph integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/radoswrapper/radoswrapper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/reftracker.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/reftracker.go

Purpose: public key-based reference tracker API. It tracks unique reference keys, preserving idempotent increments/decrements in a persistent RADOS object and supporting concurrent writers through object-version assertions.

APIs: `Add(ioctx, rtName, refs)` creates or updates a tracker and returns whether a new object was created. `Remove(ioctx, rtName, refs)` removes or masks references and returns whether the tracker object was deleted. Internal validators reject empty tracker names and empty/nil refs.

Control flow: both operations read the reftracker object version from xattr. `Add` initializes v1 state if the object is missing; otherwise it reads the last RADOS generation and dispatches to `v1.Add`. `Remove` treats a missing object as already deleted; otherwise it dispatches to `v1.Remove`. Unknown layout versions fail through `errors.UnknownObjectVersion`.

State and persistence: persistent state is in a RADOS object named `rtName`: a version xattr plus v1 body/omap layout. `GetLastVersion` immediately after version xattr read provides the generation used by subsequent v1 read/write assertions.

Dependencies and integration: uses `radoswrapper`, version dispatch, v1 implementation, `reftype`, and go-ceph `rados.ErrNotFound`.

Risks: callers must retry on `ErrObjectOutOfDate`; this package surfaces but does not loop. Version-read and last-version assumptions are central to concurrency safety. Empty refs are errors, not no-ops.

Test signals: `reftracker_test.go` covers input validation, new object creation, overlapping idempotent adds, missing-object remove semantics, bulk/single deletes, repeated add/remove cycles, and mask behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/reftracker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/reftracker_test.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/reftracker_test.go

Purpose: top-level behavior tests for the public reftracker API using the fake RADOS backend.

Important coverage: `TestRTAdd` verifies missing names/refs, bulk creation, and overlapping additions that do not double-count existing refs. `TestRTRemove` verifies missing refs validation, missing object idempotence, no-op removal of unknown refs, deletion when all tracked refs are removed, one-by-one removal, repeated lifecycle cycles, and overlap add followed by distinct removals. `TestRTMask` verifies mask operations, deletion when only masked refs remain, mask plus remove combinations, masked refs blocking future `Add`, and masked refs being removable with `Normal` before re-add.

Control flow and state: each subtest creates a fresh `FakeIOContext` and usually runs in parallel, avoiding shared fake state. Tests observe only returned booleans/errors at the public layer, leaving detailed object shape checks to v1 tests.

Dependencies: `testify/require`, fake RADOS, and `reftype`.

Risks highlighted: duplicate subtest names appear for two remove cases, which can make targeted test runs less clear. There is no explicit test of public retry behavior because retrying is a caller concern.

Test signal quality: strong for idempotency and mask semantics; weaker for concurrent writer interleavings because fake usage is serial.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/reftracker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/reftype/reftype.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/reftype/reftype.go

Purpose: defines on-disk reference type encoding for reftracker omap values.

APIs and types: `RefType` is an `int8` enum with `Unknown`, `Normal`, and `Mask`. `Normal` contributes to refcount and can be removed or converted to mask. `Mask` does not contribute to refcount and prevents future `Add` calls from re-counting the same key until removed with `Normal`. `ToBytes` encodes one byte; `FromBytes` validates one-byte length and known values.

State and persistence: serialized values are stored in reftracker object omap entries keyed by reference id.

Dependencies: uses reftracker `errors.UnexpectedReadSize` and `fmt` for unknown enum diagnostics.

Integration points: v1 add/remove code serializes `Normal` and `Mask`, and read paths parse omap values through `FromBytes`.

Risks: the v1 layout comment says omap type is `uint32`, but the implementation stores one byte. Compatibility depends on this implementation and tests, so future layout changes should use explicit versioning.

Test signals: `reftype_test.go` covers byte encoding for normal/mask and errors for unknown/wrong-sized inputs.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/reftype/reftype.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/reftype/reftype_test.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/reftype/reftype_test.go

Purpose: validates binary serialization for `RefType`.

Coverage: `ToBytes` maps `Normal` to `{1}` and `Mask` to `{2}`. `FromBytes` accepts those values and rejects an invalid byte and a multi-byte slice.

Dependencies: `testify/require`.

State and integration: no persistence, but it protects the omap value contract used by v1 reftracker.

Risks and gaps: does not assert exact error messages or `Unknown` return on error, and does not test empty byte slice separately from wrong size.

Test signal quality: focused and sufficient for the current two valid encodings.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/reftype/reftype_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/v1/refcount.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/v1/refcount.go

Purpose: defines v1 reftracker version constant and binary encoding for the object body refcount.

APIs and types: private `refCount uint32`, `Version = 1`, and `refCountSize = 4`. `toBytes` writes big-endian uint32. `refCountFromBytes` requires exactly four bytes and parses big-endian uint32.

State and persistence: the encoded refcount is written as the full RADOS object body for v1 trackers.

Dependencies: standard `encoding/binary` and reftracker `UnexpectedReadSize`.

Integration points: `v1.Init`, `v1.Add`, `v1.Remove`, and `readObjectByKeys` use this encoding to maintain total normal refs.

Risks: arithmetic checks in `v1.Add` and `v1.Remove` must protect overflow/underflow because the type is unsigned. Layout changes require new version dispatch.

Test signals: `refcount_test.go` confirms `{0,0,0,0x7B}` for 123 and wrong-size errors.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/v1/refcount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/v1/refcount_test.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/v1/refcount_test.go

Purpose: checks v1 refcount serialization.

Coverage: encodes `refCount(123)` as a four-byte big-endian value and decodes it back. Rejects a three-byte slice.

Dependencies: `testify/require`.

Integration: protects the RADOS object body format used by all v1 tracker reads/writes.

Risks and gaps: no boundary tests for `0`, `math.MaxUint32`, overflow arithmetic, or empty input; overflow is covered indirectly in v1 add tests through a max refcount fixture.

Test signal quality: narrow but valuable for the binary format.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/v1/refcount_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/v1/v1.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/v1/v1.go

Purpose: implements reftracker layout version 1 on top of RADOS object body plus omap entries.

APIs: `Init` creates a new tracker with exclusive create, version xattr, normal omap refs, and body refcount. `Add` reads selected keys, adds only missing refs as `Normal`, detects uint32 overflow, and writes new refcount and omap entries under `AssertVersion`. `Remove` handles normal removal, normal-to-mask conversion, and adding new mask refs; if resulting normal refcount is zero, it removes the entire object. `readObjectByKeys` reads the body and requested omap keys under generation assertion.

Control flow: all modifications are read-modify-write with the caller-supplied RADOS generation. `readObjectByKeys` parses the object body into `refCount`, iterates omap values, and converts each through `reftype.FromBytes`.

State and persistence: xattr `csi.ceph.com/rt-version` stores layout version. Object body stores normal-ref total. Omap maps ref key to one-byte `reftype`. Mask refs persist only while at least one normal ref remains; if normal refcount reaches zero, the whole object is deleted, including masks.

Dependencies: go-ceph create options, wrapper interface, error normalization, `reftype`, and `version`.

Integration points: only used through top-level `reftracker` after version dispatch. `refsMapToKeysSlice` and `typedRefsMapToKeysSlice` provide omap lookup keys.

Risks: callers must retry stale generation errors. `readObjectByKeys` ignores `ReadOpReadStep.BytesRead` and relies on `refCountFromBytes` over the full buffer; a short object read may parse zero-filled bytes unless the fake or RADOS step signals error elsewhere. Layout comment says omap values are `uint32`, while implementation uses one byte. Mask semantics can leave mask omap entries until object deletion or explicit normal removal.

Test signals: `v1_test.go` directly checks initialization, add cases, remove/mask cases, missing objects, stale generations mapped to `ErrObjectOutOfDate`, and refcount overflow.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/v1/v1.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/v1/v1_test.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/v1/v1_test.go

Purpose: verifies v1 layout behavior at the object-shape level using fake RADOS.

Coverage: `TestV1Read` exercises successful add through read path, missing object failure, stale generation failure, refcount overflow, and error identity for stale generation. `TestV1Init` confirms exclusive create success and existing-object failure. `TestV1Add` checks adding a new ref increments object version/refcount/omap, existing ref no-ops without version bump, masked refs block re-add, and failure cases. `TestV1Remove` checks removal without deletion, deletion on last normal ref, masking without deletion, masking with deletion, adding a mask for a missing ref, no-op unknown normal removal, and stale generation error identity.

State assertions: tests compare entire `FakeObj` values, including `Ver`, `Omap`, and `Data`, which strongly protects layout and fake-version behavior.

Dependencies: fake RADOS, `reftype`, reftracker errors, and `testify/require`.

Risks and gaps: does not simulate true concurrent interleavings beyond stale generation. Duplicate remove fixture comments/cases are present. No explicit corrupt omap reftype test in v1 read path.

Test signal quality: strong for current v1 persistence contract and idempotent semantics.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/v1/v1_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/version/version.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/version/version.go

Purpose: handles reftracker object layout version xattr encoding and reading.

APIs: `XattrName` is `csi.ceph.com/rt-version`; `SizeBytes` is four. `ToBytes` and `FromBytes` encode/decode big-endian uint32. `Read` reads the xattr through `IOContextW.GetXattr`, validates returned byte count, and parses the value.

State and persistence: version is stored as a RADOS object xattr, separate from the object body and omap.

Dependencies: standard `encoding/binary`, reftracker errors, and RADOS wrapper interface.

Integration points: top-level `reftracker.Add`/`Remove` use `Read` to dispatch to v1 or fail unknown versions.

Risks: missing xattr, wrong length, or object not found bubble to callers; top-level code treats only object not found specially. Short reads are detected both by returned size and parser length.

Test signals: `version_test.go` covers encoding, decoding, missing object, missing xattr, and wrong-sized version data using fake RADOS.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/version/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/version/version_test.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/version/version_test.go

Purpose: protects the reftracker version xattr format and read behavior.

Coverage: `TestVersionBytes` verifies v1 value `1` encodes as `{0,0,0,1}` and wrong-size decode fails. `TestVersionRead` validates successful xattr read and errors for missing object, missing xattr, and wrong-sized xattr content.

Dependencies: fake RADOS and `testify/require`.

Integration: ensures `reftracker.Add`/`Remove` can reliably distinguish absent objects from readable v1 objects.

Risks and gaps: does not test unknown-but-well-formed versions; that is handled by top-level dispatch rather than this package.

Test signal quality: strong for xattr read and binary format.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/version/version_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/stripsecrets/stripsecrets.go -->
## sources/control-plane/ceph-csi/internal/util/stripsecrets/stripsecrets.go

Purpose: redacts Ceph secret material from command argument slices before logging.

APIs and control flow: `InArgs(args)` copies the input slice, attempts to redact the first `--key=` or `--keyfile=` argument, and only if no key/keyfile is found attempts to redact the first `secret=` option. `stripSecret` uses `strings.Cut` to preserve prefix and suffix around comma-separated option values.

State and persistence: stateless; input slice is left unchanged.

Dependencies: standard `strings`.

Integration points: intended for logging command arguments that may include Ceph credentials in explicit key flags or mount option strings.

Risks: intentionally handles only one occurrence and prioritizes key/keyfile over `secret=`, so multiple secrets can remain if present. `stripSecret` suffix reconstruction is index-sensitive and should be tested for options before/after `secret=`.

Test signals: no test file listed in this subset, so behavior is inferred from implementation comments.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/stripsecrets/stripsecrets.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/topology.go -->
## sources/control-plane/ceph-csi/internal/util/topology.go

Purpose: converts Kubernetes node labels and CSI topology requirements into Ceph-CSI topology maps and topology-constrained pool selections.

APIs: `GetTopologyFromDomainLabels` reads requested node labels from Kubernetes and returns CSI topology segments prefixed with `topology.<driverName>/`. `GetTopologyFromRequest` parses JSON `topologyConstrainedPools` from CreateVolume parameters and returns it with accessibility requirements. `MatchPoolAndTopology` filters to a requested pool before matching. `FindPoolAndTopology` prefers matching `Preferred` topology entries, then `Requisite`. `matchPoolToTopology` and `extractDomainsFromlabels` implement domain-label matching.

Control flow: label input is comma-split and checked for duplicates, then Kubernetes node labels are fetched; missing requested labels error. Pool matching treats a configured pool's domain segments as requirements that must all match the requested topology domain map.

State and persistence: no persistence. Reads current Kubernetes Node labels through `k8s.GetNodeLabels`.

Dependencies: CSI protobuf types, internal k8s and log packages, JSON parsing.

Integration points: used during driver topology publication and volume creation when StorageClass parameters include topology-constrained pools.

Risks: label domain extraction uses the substring after `/`; labels without `/` produce the full string due to index `-1`, which may be intentional but is subtle. `GetTopologyFromDomainLabels` is hard to unit test because it calls Kubernetes directly. Empty domain segments in a configured pool can act as a broad match.

Test signals: `topology_test.go` thoroughly covers pool/topology matching but leaves node-label fetching commented out as a TODO requiring client injection.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/topology.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/topology_test.go -->
## sources/control-plane/ceph-csi/internal/util/topology_test.go

Purpose: verifies topology-constrained pool selection logic, including `FindPoolAndTopology` and `MatchPoolAndTopology`.

Coverage: tests nil inputs, empty pool lists, missing pool names, mismatched domain labels/values, empty/partial accessibility requirements, valid singleton and multiple-pool matches, preferred ordering, data pool return, explicit pool filtering success, and non-existent pool errors.

State and dependencies: pure in-memory CSI `TopologyRequirement` and `TopologyConstrainedPool` fixtures; no Kubernetes API calls.

Integration signals: demonstrates that pools with empty or partial domain segments can match a richer requested topology, and preferred requirements are evaluated before requisite entries.

Risks and gaps: `GetTopologyFromDomainLabels` is commented out because Kubernetes label reads are not injectable. The `checkOutput` condition has a precedence pattern that may not fail on all malformed topology maps as intended.

Test signal quality: good for matching semantics, weak for node label integration.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/topology_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/util.go -->
## sources/control-plane/ceph-csi/internal/util/util.go

Purpose: shared Ceph-CSI utility layer for driver configuration, size rounding, mount helpers, driver name validation, volume context filtering, client IP conversion, and controller publish secret lookup.

APIs and types: driver type constants, build-time `GitCommit`/`DriverVersion`, and large `Config` struct for process flags. Size helpers include `RoundOffVolSize`, `RoundOffBytes`, and `RoundOffCephFSVolSize`. Other exported helpers include `ValidateDriverName`, `GenerateVolID`, `CreateMountPoint`, `IsCorruptedMountError`, `Mount`, `MountOptionsAdd`, `CallStack`, `GetVolumeContext`, `ParseClientIP`, `ConvertIPToCIDR`, and `GetControllerPublishSecretRef`.

Control flow: size helpers round small requests by MiB and larger requests by GiB, with CephFS rounding to 4MiB boundaries first. `ValidateDriverName` uses Kubernetes DNS1123 subdomain validation on lowercase input. `GenerateVolID` resolves pool id if needed and composes a `CSIIdentifier`. `GetControllerPublishSecretRef` decodes cluster id from volume id, tries direct config lookup by driver type, then cluster mapping fallbacks.

State and persistence: reads filesystem paths for mount staging checks elsewhere, creates mount directories, reads Kubernetes/CSI config files through internal config helpers, and uses build-time variables.

Dependencies: Kubernetes validation, mount utils, cloud-provider volume helpers, network parsing, internal k8s/config helpers.

Integration points: broad driver bootstrap and request path use. Secret ref lookup bridges volume ID decoding, Ceph-CSI config map data, and cluster ID mapping.

Risks: `checkDirExists` treats non-`IsNotExist` stat errors as existence. `ParseClientIP` scans space-separated address tokens and accepts first parseable host, which is suitable for Ceph client address strings but should be documented for multi-address inputs. Secret-ref lookup depends on config file state and mapping order.

Test signals: `util_test.go` covers rounding, mount option dedupe, IP parsing, and CIDR conversion; other helpers depend on broader integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/util_test.go -->
## sources/control-plane/ceph-csi/internal/util/util_test.go

Purpose: unit tests for selected general utilities.

Coverage: `TestRoundOffBytes` and `TestRoundOffVolSize` cover MiB/GiB rounding behavior. `TestMountOptionsAdd` covers empty inputs, duplicate avoidance, leading/trailing commas, and multiple additions. `TestRoundOffCephFSVolSize` covers sub-4MiB, MiB, MB, near-GiB, and GiB rounding. `TestParseClientIP` covers IPv4, IPv6 bracketed addresses, compressed IPv6, and invalid input. `TestConvertIPToCIDR` covers IPv4, IPv6, zero/loopback, and invalid strings.

State and dependencies: pure unit tests, no Ceph/Kubernetes dependencies.

Integration signals: confirms user-facing capacity normalization and network filter helper behavior.

Risks and gaps: no coverage for `ValidateDriverName`, `GenerateVolID`, mount wrappers, call stack, volume context filtering, or controller publish secret lookup.

Test signal quality: good for arithmetic/string helpers; intentionally limited for cluster-integrated helpers.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/validate.go -->
## sources/control-plane/ceph-csi/internal/util/validate.go

Purpose: validates CSI request fields, volume IDs, read-only mode constraints, and service account mount restrictions.

APIs: validation functions for ControllerPublish/Unpublish, NodeStage/Unstage, NodePublish/Unpublish; `CheckReadOnlyManyIsSupported`; `ValidateVolumeID`; `IsStaticVol`; and `ValidateServiceAccountRestriction`. Constants define CSI volume/publish context keys for service account and pod UID.

Control flow: request validators enforce non-empty volume id, volume capability where required, node id/paths, secrets for stage, and staging path existence. `ValidateVolumeID` rejects empty IDs, path traversal `..`, slash/backslash, and for dynamic volumes enforces `hhhh-hhhh-[A-Za-z0-9_-]+`. Static volumes skip only the format check. Service-account restriction allows empty policy, warns and allows empty pod SA, otherwise exact-matches a comma-separated list.

State and persistence: checks local filesystem existence for node staging target. Logs service-account warning/debug messages.

Dependencies: CSI protobufs, gRPC status codes, regex/string parsing, internal log.

Integration points: called at CSI RPC boundaries before driver-specific handling. Service-account restriction relies on kubelet `podInfoOnMount` and controller publish context data.

Risks: comma-separated service-account values are not trimmed, so spaces become part of names. Allowing missing pod service account when a restriction exists favors compatibility over strict enforcement. Static volumes still reject traversal and separators, which is important for path safety.

Test signals: `validate_test.go` covers `ValidateVolumeID` and service account restriction, including path traversal and multiple allowed SAs; broader CSI request validators are not covered here.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/validate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/validate_test.go -->
## sources/control-plane/ceph-csi/internal/util/validate_test.go

Purpose: validates security-sensitive checks for volume IDs and service-account restrictions.

Coverage: dynamic volume IDs with valid prefixes, underscores, long cluster IDs, invalid hex, missing prefixes, special chars, spaces, null byte, Unicode, empty strings, path traversal, and slash/backslash injection. Static volumes skip format but still reject traversal/separators. Service-account tests cover unrestricted, exact match, mismatch, missing pod SA allowed, comma-separated matches, and partial-name rejection.

Dependencies: `testify/require`.

State and integration: pure unit tests; logs may be emitted for missing pod SA cases but are not asserted.

Risks and gaps: does not cover CSI request validator functions or status codes. Does not test whitespace around comma-separated service account values.

Test signal quality: strong for current volume ID hardening and exact SA matching.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/validate_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/volid.go -->
## sources/control-plane/ceph-csi/internal/util/volid.go

Purpose: composes and decomposes Ceph-CSI volume identifiers that embed encoding version, cluster ID length, cluster ID, location/pool id, and object UUID.

APIs and types: `CSIIdentifier` carries `LocationID`, private `encodingVersion`, `ClusterID`, and `ObjectUUID`. `ComposeCSIID` validates maximum length and object UUID length, defaults encoding version to 1, big-endian hex encodes version, cluster length, and location id, then joins fields with `-`. `DecomposeCSIID` parses the inverse format with underflow and exact-size checks.

State and persistence: IDs are persisted externally as CSI volume handles and later decoded to locate cluster and pool/filesystem state.

Dependencies: standard binary/hex/errors/strings.

Integration points: `GenerateVolID`, validation, controller publish secret lookup, and troubleshooting tools depend on this format.

Risks: `LocationID` is cast to `uint64` during compose and back to `int64` during decompose; negative values would round-trip through two's complement if ever supplied. `DecomposeCSIID` trusts separator positions indirectly by fixed slicing and hex decode errors rather than explicitly checking separators. Object UUID length is checked but UUID syntax is not.

Test signals: `volid_test.go` checks a representative compose/decompose round trip with non-default encoding version.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/volid.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/volid_test.go -->
## sources/control-plane/ceph-csi/internal/util/volid_test.go

Purpose: verifies one canonical CSI ID compose/decompose round trip.

Coverage: fixture includes `LocationID 0xffff`, encoding version `0xffff`, a 36-byte cluster ID, and a 36-byte object UUID. Test asserts composed string equality and decomposed struct equality.

Dependencies: Go testing package only.

Integration: protects the field order and hex widths expected by CSI volume handles and related tools.

Risks and gaps: only one fixture. No negative tests for overflow, malformed hex, bad UUID length, missing separators, short strings, max length, default version, or negative location id.

Test signal quality: basic format guard, but edge-case coverage is sparse.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/volid_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/lychee.toml -->
## sources/control-plane/ceph-csi/lychee.toml

Purpose: configures Lychee link checking for Ceph-CSI documentation.

Behavior: excludes vendor paths under actions/retest, api, e2e, and top-level vendor. Runs in `offline = true` mode, so it checks local/offline links without network requests. Output format is markdown.

State and dependencies: no runtime state. Consumed by the Lychee CLI in CI or local documentation checks.

Integration points: complements markdown lint and documentation CI by avoiding vendored dependency churn and flaky external link checks.

Risks: offline mode will not detect dead external URLs. Excluding vendor paths is appropriate but can hide documentation issues in vendored content by design.

Test signals: no tests; correctness is through CI usage.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/lychee.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/pkg/util/crypto/types.go -->
## sources/control-plane/ceph-csi/pkg/util/crypto/types.go

Purpose: defines encryption mode enum parsing and stringification for public crypto utilities.

APIs: `EncryptionType` enum values are invalid, none, block, and file. `ParseEncryptionType` accepts `"block"`, `"file"`, and empty string for none; all other strings are invalid. `String` returns stable config strings, empty for none, `"INVALID"` for invalid, and `"UNKNOWN"` for unrecognized enum values.

State and persistence: stateless, but string values are configuration surface area.

Dependencies: none outside standard language.

Integration points: used by encryption configuration parsing for RBD block encryption and CephFS/file encryption (`fscrypt`) mode selection.

Risks: parser is case-sensitive and intentionally rejects combined values such as `file,block`. Comment above `EncryptionTypeFile` incorrectly says `EncryptionTypeBlock`.

Test signals: `types_test.go` covers valid, empty, invalid, combined invalid values, and round-trip string outputs.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/pkg/util/crypto/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/pkg/util/crypto/types_test.go -->
## sources/control-plane/ceph-csi/pkg/util/crypto/types_test.go

Purpose: unit test for encryption type parsing and string output.

Coverage: invalid examples `wat?`, `both`, `file,block`, and `block,file`; valid block/file; empty string as none; and `ParseEncryptionType(s).String() == s` for supported string values.

Dependencies: `testify/require`.

Integration: protects config parsing from accidentally accepting ambiguous combined encryption modes.

Risks and gaps: no direct assertions for `EncryptionTypeInvalid.String()` or unknown enum `String()` branch. No case-insensitivity tests, implying exact lowercase strings are the contract.

Test signal quality: good for accepted config surface.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/pkg/util/crypto/types_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/pkg/util/kernel/version.go -->
## sources/control-plane/ceph-csi/pkg/util/kernel/version.go

Purpose: obtains and evaluates Linux kernel versions against feature support requirements, including enterprise backports.

APIs and types: `GetKernelVersion` wraps `unix.Uname` and trims NUL bytes from release. `KernelVersion` describes minimum or backport-supported version fields. `parseKernelRelease` extracts version, patchlevel, sublevel, and numeric extra version from release strings. `CheckKernelSupport` compares a release against supported version rules, with generic minimum checks or strict distro/backport checks.

State and persistence: reads current kernel release via syscall; no persistence.

Dependencies: `golang.org/x/sys/unix`, internal log, string parsing.

Integration points: used by Ceph-CSI feature gates such as quota and deep-flatten support decisions.

Risks: parser accepts some suffix forms like `5.12xlinux` as version 5.12, which tests document. Backport matching uses substring containment for distribution. Warnings/errors are logged instead of returned with details because public API returns bool.

Test signals: `version_test.go` covers syscall result shape, parser good/bad releases, quota support, and deep-flatten support including RHEL-style backports.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/pkg/util/kernel/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/pkg/util/kernel/version_test.go -->
## sources/control-plane/ceph-csi/pkg/util/kernel/version_test.go

Purpose: tests kernel version retrieval, parsing, and support matching.

Coverage: `GetKernelVersion` must return a non-empty, non-NUL-suffixed string. Parser rejects malformed releases and accepts documented suffix/extraversion forms with expected numeric tuples. Support checks include generic minimum kernels and RHEL `.el7`/`.el8` backports for quota and deep-flatten feature examples.

State and dependencies: one test depends on the host kernel syscall; remaining tests are pure.

Integration: confirms support rules can represent both upstream and vendor-backported features.

Risks and gaps: host-dependent test could fail only on unusual Unix environments. No tests for multiple supported rules with overlapping distro substrings beyond current examples.

Test signal quality: good coverage for parser behavior and feature support policy.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/pkg/util/kernel/version_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/build-multi-arch-image.sh -->
## sources/control-plane/ceph-csi/scripts/build-multi-arch-image.sh

Purpose: builds per-architecture Ceph-CSI images using architecture-specific base image digests.

Control flow: sources `build_step.inc.sh`, enables Docker experimental manifest support, reads `BASE_IMAGE` from `build.env`, inspects base image manifests with `docker manifest inspect` and `jq`, starts `multiarch/qemu-user-static`, then loops over `amd64` and `arm64` to run `GOARCH=<arch> BASE_IMAGE=<base>@<digest> make image-cephcsi`.

State and persistence: pushes/builds container image artifacts via Docker/Makefile; changes no repo files directly.

Dependencies: Docker with manifest support, jq, QEMU user static container, `build.env`, Make targets.

Integration points: release/CI image build path for multi-arch output.

Risks: digest extraction via awk over JSON text is brittle compared with jq filtering. Requires privileged Docker run. Only amd64/arm64 are hardcoded.

Test signals: no direct tests; validation is through image build CI.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/build-multi-arch-image.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/build_step.inc.sh -->
## sources/control-plane/ceph-csi/scripts/build_step.inc.sh

Purpose: shared shell helper for periodic build-step progress logging.

APIs and control flow: creates a temp file for current step, `build_step` writes the step and starts a background loop that logs `running:` every minute, and `build_steps_cleanup` kills the logger and removes the temp file via EXIT trap.

State and persistence: temporary file and background process. No repo state.

Dependencies: POSIX shell utilities, `date`, `mktemp`, `sleep`, `kill`.

Integration points: sourced by build scripts to avoid silent long-running CI stages.

Risks: `build_step` never calls a separate done function; callers rely on overwriting current step and final trap. If a sourced script exits abnormally without trap execution, temp/log process cleanup could lag.

Test signals: no tests; behavior is operational in CI logs.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/build_step.inc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/check-env.sh -->
## sources/control-plane/ceph-csi/scripts/check-env.sh

Purpose: checks local build prerequisites for Ceph-CSI development.

Control flow: detects rpm/dpkg for package advice, creates a temporary cgo program including `rados/librados.h` and `rbd/librbd.h`, runs `go run -mod=vendor`, reports missing Ceph development packages, checks Go version >= 1.13, verifies `GO111MODULE` is on/auto/empty, and requires `CGO_ENABLED=1`. Accumulates errors and exits with count.

State and persistence: creates/removes temporary Go file.

Dependencies: Go toolchain, CGO, Ceph headers/libraries, package manager detection.

Integration points: developer preflight and CI environment diagnostics.

Risks: temp file cleanup occurs only when Go exists and compile path is reached; failures before removal may leave temp files. Go version parsing assumes classic `go version` format.

Test signals: no direct tests; output is intended for humans.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/check-env.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/codespell.conf -->
## sources/control-plane/ceph-csi/scripts/codespell.conf

Purpose: configures `codespell` spelling checks.

Behavior: skips git/vendor/generated-like paths and e2e vendor, ignores specific project terms such as `ExtraVersion`, `extraversion`, `ba`, `ro`, `RO`, and `AfterAll`, and enables filename checking.

State and dependencies: consumed by codespell; no runtime state.

Integration points: non-Go linting or pre-commit spelling checks.

Risks: ignored words can hide legitimate misspellings where those tokens appear accidentally. Vendor skip is intentional to avoid third-party noise.

Test signals: no tests; enforced through lint jobs.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/codespell.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/deploy-ceph-csi-operator.sh -->
## sources/control-plane/ceph-csi/scripts/deploy-ceph-csi-operator.sh

Purpose: deploys or cleans up the external Ceph-CSI Operator plus driver custom resources for tests.

Control flow: sources `utils.sh` and `build.env`, normalizes operator version `latest` to `main`, fetches operator install YAML from GitHub, rewrites namespace, generates image set and encryption config maps, creates an `OperatorConfig`, and creates RBD/CephFS/NFS `Driver` resources. Cleanup regenerates matching resources and deletes them before deleting operator install YAML.

State and persistence: creates Kubernetes resources in `OPERATOR_NAMESPACE` and temp YAML files under a trap-cleaned directory.

Dependencies: `curl`, `kubectl_retry`, raw GitHub manifests, build.env sidecar image versions, Kubernetes cluster with operator CRDs.

Integration points: e2e/operator test deployment path.

Risks: remote `main` manifests make `latest` non-reproducible. `kubectl create` rather than apply means existing resources rely on retry wrapper's AlreadyExists behavior. Secrets/encryption config is empty by default.

Test signals: no direct tests; operational validation is pod/operator readiness in e2e.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/deploy-ceph-csi-operator.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/golangci.yml.in -->
## sources/control-plane/ceph-csi/scripts/golangci.yml.in

Purpose: template configuration for `golangci-lint` v2.

Behavior: configures build tags placeholder `@@BUILD_TAGS@@`, concurrency, 20-minute timeout, vendor module mode, all linters by default with many project-specific disables, linter thresholds/settings, exclusions for tests, and formatters (`gofmt`, `gofumpt`, `goimports`, `gci`).

State and dependencies: consumed by generation or lint scripts to produce `scripts/golangci.yml`. Requires golangci-lint version compatible with v2 config and selected linters.

Integration points: `scripts/lint-go.sh` runs the generated config.

Risks: enabling all linters while disabling a curated list means new golangci-lint releases can add linters that break CI until added to disables. Placeholder substitution must happen before use.

Test signals: validation through lint CI, not unit tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/golangci.yml.in -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/install-helm.sh -->
## sources/control-plane/ceph-csi/scripts/install-helm.sh

Purpose: installs Helm if needed and deploys or removes Ceph-CSI Helm charts for CephFS and RBD in a test cluster.

Control flow: detects arch, downloads Helm when absent, labels nodes for topology/read affinity, optionally fetches Rook fsid/admin key to generate StorageClasses and secrets, installs CephFS chart, checks Deployment/DaemonSet readiness, deletes shared config maps to avoid RBD install conflicts, installs RBD chart with topology and snapshot settings, and supports cleanup removing labels, uninstalling charts, and deleting namespace.

State and persistence: creates Kubernetes namespace/resources, labels nodes, optionally creates secrets/storageclasses, downloads Helm into `/tmp/cephcsi-helm-test`.

Dependencies: Helm, kubectl, Rook toolbox pod, build.env, `kubectl_retry`, chart directories.

Integration points: local/e2e chart validation for both CephFS and RBD.

Risks: command-line parsing allows legacy two-arg mode and option mode, making edge cases possible. Readiness checks compare replica fields that may be empty early. Secrets passed via `--set` can appear in process lists/logs. Cleanup deletes namespace entirely.

Test signals: no unit tests; install success is checked by Kubernetes readiness loops.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/install-helm.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/install-snapshot.sh -->
## sources/control-plane/ceph-csi/scripts/install-snapshot.sh

Purpose: installs or removes Kubernetes CSI snapshot controller and snapshot/group-snapshot CRDs for tests.

Control flow: builds URLs for external-snapshotter release, downloads RBAC/controller YAML to temp files, rewrites namespace and image tag, injects `--feature-gates=CSIVolumeGroupSnapshot=true` on create, applies or deletes group snapshot CRDs, controller resources, and standard snapshot CRDs. Install waits for snapshot-controller pod readiness.

State and persistence: Kubernetes CRDs/RBAC/deployment in target namespace; temp files.

Dependencies: curl, sed, kubectl_retry, external-snapshotter GitHub raw manifests.

Integration points: required before snapshot e2e tests and volume group snapshot tests.

Risks: a sed expression for replacing a false feature gate contains `----feature-gates`, which may fail to update an existing false argument. Remote manifests and default `v5.0.1` must remain compatible with cluster version. Deletes CRDs cluster-wide.

Test signals: readiness loop validates pod availability; no unit tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/install-snapshot.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/create-configmap.sh -->
## sources/control-plane/ceph-csi/scripts/k8s-storage/create-configmap.sh

Purpose: creates or replaces a `ceph-csi-config` ConfigMap for Kubernetes external storage e2e jobs using Rook cluster information.

Control flow: requires namespace argument, fetches Rook toolbox pod, reads Ceph fsid and monitor service IP/port, chooses `kubectl replace` if ConfigMap exists otherwise `create`, and writes JSON config with clusterID and monitors.

State and persistence: creates/replaces Kubernetes ConfigMap in the supplied namespace.

Dependencies: kubectl, Rook namespace/pods/services, Ceph toolbox.

Integration points: StorageClasses and driver manifests use this config map for e2e provisioning.

Risks: assumes first toolbox pod and first monitor service/port are valid. Does not use `kubectl_retry`. Only writes a single monitor endpoint.

Test signals: no unit tests; e2e setup validates indirectly.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/create-configmap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/create-storageclasses.sh -->
## sources/control-plane/ceph-csi/scripts/k8s-storage/create-storageclasses.sh

Purpose: materializes StorageClass templates for k8s storage e2e tests.

Control flow: finds Rook toolbox pod, reads Ceph fsid, loops over `sc-*.yaml.in`, substitutes `@@CLUSTER_ID@@`, and pipes each manifest to `kubectl create -f -`.

State and persistence: creates Kubernetes StorageClasses.

Dependencies: kubectl, Rook toolbox, template files.

Integration points: paired with driver YAMLs that reference existing storage class names.

Risks: repeated runs fail if StorageClasses already exist. Substitution only handles cluster ID and assumes templates contain all other correct values.

Test signals: no tests; e2e provisioning is validation.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/create-storageclasses.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/create-volumesnapshotclasses.sh -->
## sources/control-plane/ceph-csi/scripts/k8s-storage/create-volumesnapshotclasses.sh

Purpose: materializes VolumeSnapshotClass templates for k8s storage e2e tests.

Control flow: reads Rook fsid from toolbox pod, loops over `volumesnapshotclass-*.yaml.in`, substitutes `@@CLUSTER_ID@@`, and creates each manifest.

State and persistence: creates Kubernetes VolumeSnapshotClasses.

Dependencies: kubectl, Rook toolbox, snapshot CRDs already installed, template files.

Integration points: driver YAMLs reference these snapshot class names for snapshot e2e coverage.

Risks: repeated runs fail on existing resources. Assumes snapshot CRDs/controllers are installed separately.

Test signals: no unit tests; snapshot e2e validates indirectly.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/create-volumesnapshotclasses.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/driver-cephfs.yaml -->
## sources/control-plane/ceph-csi/scripts/k8s-storage/driver-cephfs.yaml

Purpose: Kubernetes storage e2e driver configuration for CephFS.

Content and behavior: names existing StorageClass and SnapshotClass `k8s-storage-e2e-cephfs`, sets driver name `cephfs.csi.ceph.com`, supported size range 1Gi to 16Ti, mount option `rw`, and capability matrix including persistence, multipods, online/controller expansion, read-write-once-pod, read-only-many, exec, RWX, snapshot/PVC data sources, and no block/topology/node expansion.

State and dependencies: consumed by Kubernetes e2e test framework, not by the driver at runtime.

Integration points: aligned with `sc-cephfs.yaml.in` and `volumesnapshotclass-cephfs.yaml.in`.

Risks: capability drift with actual CephFS driver behavior can cause false test expectations. `fsGroup` and topology are declared unsupported here.

Test signals: used by e2e suite.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/driver-cephfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/driver-rbd.yaml -->
## sources/control-plane/ceph-csi/scripts/k8s-storage/driver-rbd.yaml

Purpose: Kubernetes storage e2e driver configuration for RBD.

Content and behavior: uses existing StorageClass and SnapshotClass `k8s-storage-e2e-rbd`, driver name `rbd.csi.ceph.com`, size range 1Gi to 16Ti, fs types ext4/xfs, mount option `rw`, and capability matrix including persistence, block, exec, controller/node expansion, multipods, read-write-once-pod, snapshot/PVC data sources, and read-only-many for snapshot data sources; RWX and topology are false.

State and dependencies: consumed by Kubernetes storage e2e framework.

Integration points: paired with `sc-rbd.yaml.in` and `volumesnapshotclass-rbd.yaml.in`.

Risks: declared capabilities must track actual RBD behavior and e2e requirements. Topology is disabled in this e2e configuration even though other Ceph-CSI code supports topology-aware provisioning.

Test signals: e2e test configuration.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/driver-rbd.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/sc-cephfs.yaml.in -->
## sources/control-plane/ceph-csi/scripts/k8s-storage/sc-cephfs.yaml.in

Purpose: CephFS StorageClass template for external storage e2e tests.

Content: provisioner `cephfs.csi.ceph.com`, cluster ID placeholder, fsName `myfs`, Rook CephFS provisioner/node secret references, `Delete` reclaim policy, and volume expansion enabled.

State and dependencies: materialized by `create-storageclasses.sh` after replacing `@@CLUSTER_ID@@`; depends on Rook-created secrets and CephFS `myfs`.

Integration points: referenced by `driver-cephfs.yaml`.

Risks: hardcoded secret names/namespaces and fsName assume Rook test deployment defaults. No mount options or topology parameters.

Test signals: validated by e2e provisioning and expansion tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/sc-cephfs.yaml.in -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/sc-rbd.yaml.in -->
## sources/control-plane/ceph-csi/scripts/k8s-storage/sc-rbd.yaml.in

Purpose: RBD StorageClass template for external storage e2e tests.

Content: provisioner `rbd.csi.ceph.com`, cluster ID placeholder, pool `replicapool`, imageFeatures `layering`, Rook provisioner/expand/node-stage secret references, fstype ext4, `Delete` reclaim policy, expansion enabled, and `discard` mount option.

State and dependencies: materialized by `create-storageclasses.sh`; depends on Rook pool and secrets.

Integration points: referenced by `driver-rbd.yaml`.

Risks: hardcoded pool and secret names tie it to Rook sample deployment. `discard` mount option can affect performance/behavior and should match test expectations.

Test signals: validated by e2e provisioning/expansion/snapshot tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/sc-rbd.yaml.in -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/volumesnapshotclass-cephfs.yaml.in -->
## sources/control-plane/ceph-csi/scripts/k8s-storage/volumesnapshotclass-cephfs.yaml.in

Purpose: CephFS VolumeSnapshotClass template for e2e snapshot tests.

Content: driver `cephfs.csi.ceph.com`, cluster ID placeholder, Rook CephFS snapshotter secret reference, and `Delete` deletion policy.

State and dependencies: created by `create-volumesnapshotclasses.sh`; requires snapshot CRDs and Rook secrets.

Integration points: referenced by `driver-cephfs.yaml` as existing snapshot class.

Risks: hardcoded secret namespace/name and delete policy. Snapshot controller must be installed separately.

Test signals: used by snapshot e2e tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/volumesnapshotclass-cephfs.yaml.in -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/volumesnapshotclass-rbd.yaml.in -->
## sources/control-plane/ceph-csi/scripts/k8s-storage/volumesnapshotclass-rbd.yaml.in

Purpose: RBD VolumeSnapshotClass template for e2e snapshot tests.

Content: driver `rbd.csi.ceph.com`, cluster ID placeholder, Rook RBD snapshotter secret reference, and `Delete` deletion policy.

State and dependencies: created by `create-volumesnapshotclasses.sh`; requires snapshot CRDs and Rook secrets.

Integration points: referenced by `driver-rbd.yaml`.

Risks: hardcoded secret namespace/name and delete policy. Repeated create can fail if class already exists.

Test signals: used by snapshot e2e tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/k8s-storage/volumesnapshotclass-rbd.yaml.in -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/lint-extras.sh -->
## sources/control-plane/ceph-csi/scripts/lint-extras.sh

Purpose: runs non-Go lint checks for shell, YAML, Markdown, Helm charts, and Python.

APIs and control flow: `run_check` finds matching files excluding vendor and runs a checker if installed, warning unless `lint-all` set `all_required=1`. Commands include `lint-shell`, `lint-yaml`, `lint-markdown`, `lint-helm`, `lint-py`, and `lint-all`.

State and dependencies: no persistent state. Depends on shellcheck, bash, yamllint, mdl, helm, pylint, find/xargs.

Integration points: CI lint jobs and local developer checks.

Risks: optional mode silently skips missing tools for individual lint commands. Regex-based file selection can miss unusual filenames or include generated files not intended. Helm lint command expands chart dirs dynamically.

Test signals: no tests; CI exit status is validation.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/lint-extras.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/lint-go.sh -->
## sources/control-plane/ceph-csi/scripts/lint-go.sh

Purpose: runs Go linting through `golangci-lint`.

Control flow: enables pipefail, checks for executable `golangci-lint`, then runs `golangci-lint --config=scripts/golangci.yml run ./... -v "$@"`; otherwise prints a warning and exits successfully.

State and dependencies: no state; requires generated `scripts/golangci.yml` and golangci-lint for actual enforcement.

Integration points: local/CI Go lint entrypoint.

Risks: missing golangci-lint only warns, so enforcement depends on CI image having the tool. Config path is generated from `golangci.yml.in`.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/lint-go.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/mdl-style.rb -->
## sources/control-plane/ceph-csi/scripts/mdl-style.rb

Purpose: markdownlint style configuration.

Behavior: starts from `all`, sets MD013 line length to 80 while ignoring code blocks and tables, and excludes inline HTML, missing fenced code language, and first-line top-level header rules.

State and dependencies: consumed by `mdl` from `lint-extras.sh`.

Integration points: keeps Markdown linting compatible with GitHub-flavored docs and repository conventions.

Risks: excluded rules allow HTML and untyped fences, which may reduce documentation consistency but avoids noisy failures.

Test signals: lint CI.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/mdl-style.rb -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/minikube.sh -->
## sources/control-plane/ceph-csi/scripts/minikube.sh

Purpose: provisions and manages a Minikube-based Kubernetes/Rook/Ceph-CSI test environment.

Control flow: installs/detects minikube and kubectl, validates container command, optionally installs a podman wrapper, starts Minikube with configured resources/driver/CNI/feature gates, adjusts kubelet verbosity and storage paths, disables default storage addons, delegates Rook and snapshotter operations to companion scripts, copies Ceph-CSI and sidecar images into the cluster, and tears down resources.

State and persistence: modifies host binaries under `/usr/local/bin` and `/usr/bin` for installs/wrapper, starts/stops/deletes Minikube cluster, labels/images cluster state, and manipulates `/var/lib/rook` inside Minikube.

Dependencies: curl, sudo, minikube, kubectl, ssh, Docker/Podman, Rook scripts, build.env sidecar versions, external Kubernetes stable version endpoint when `KUBE_VERSION=latest`.

Integration points: local e2e environment setup for Ceph-CSI and Rook.

Risks: powerful host modifications, privileged podman wrapper, network-dependent version downloads, and driver-specific disk assumptions. For Kubernetes minor >=36, it disables `ExtendWebSocketsToKubelet` to work around cri-dockerd streaming behavior.

Test signals: no unit tests; validation is successful cluster startup and delegated e2e scripts.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/minikube.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/rook.sh -->
## sources/control-plane/ceph-csi/scripts/rook.sh

Purpose: deploys, validates, and tears down a Rook Ceph cluster for Ceph-CSI testing.

Control flow: fetches Rook example manifests, disables Rook's own CSI drivers, optionally rewrites Ceph cluster image and health checks, deploys cluster/toolbox/filesystem/pool/subvolumegroup resources, then polls CephCluster health, manager pod, MDS pods, and RBD pool stats. Also creates/deletes additional replicated and erasure-coded block pools. An ERR trap dumps nodes, events, pods, operator logs, and Ceph CR YAML.

State and persistence: creates/deletes cluster-scoped and namespace Kubernetes resources and writes short-lived manifest files.

Dependencies: kubectl, curl, Rook raw GitHub manifests, Ceph toolbox, `kubectl_retry`.

Integration points: called by `minikube.sh` and e2e setup paths.

Risks: remote manifest version coupling, namespace/resource assumptions, and destructive teardown. Temporary `subvolumegroup.yaml` and pool files are created in current directory. Error trap exits process after log dump.

Test signals: health polling functions validate operational readiness, no unit tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/rook.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/skip-doc-change.sh -->
## sources/control-plane/ceph-csi/scripts/skip-doc-change.sh

Purpose: determines whether functional tests can be skipped for documentation/config-only changes.

Control flow: reads changed files from `git diff --name-only "$TRAVIS_COMMIT_RANGE"`, exits 1 if no changed files, treats docs, markdown, scripts, license/config files, GitHub metadata, and similar patterns as skippable except `minikube.sh`, and exits 1 after printing "Skipping functional tests" when all files are skippable.

State and dependencies: depends on Git and Travis-style environment variable.

Integration points: CI job gating.

Risks: inverted exit semantics may be specific to CI wiring and can confuse manual use. Scripts are generally skippable except minikube, which may miss functional-impacting script changes. Travis variable naming may be stale in other CI systems.

Test signals: no tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/skip-doc-change.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/test-go.sh -->
## sources/control-plane/ceph-csi/scripts/test-go.sh

Purpose: runs Go tests across non-vendor, non-e2e packages, with optional exit-first and coverage modes.

Control flow: detects vendor mode, lists packages, and either execs a single `go test` command or loops packages individually. Coverage mode writes a combined `profile.cov`, appends package cover profiles, optionally prints function coverage or writes HTML files under `GO_COVER_DIR`, and exits with failure count.

State and persistence: writes `cover.out`, combined coverfile, and optional HTML coverage artifacts.

Dependencies: Go toolchain, package list, environment variables `GO_COVER_DIR`, `TEST_EXITFIRST`, `TEST_COVERAGE`, `GO_TAGS`.

Integration points: unit-test CI entrypoint.

Risks: `GO_COVER_DIR` must be set for coverage paths. Package loop continues after failures unless exit-first is enabled, which is useful for complete reports but can be slower.

Test signals: this is the test runner itself.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/test-go.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/utils.sh -->
## sources/control-plane/ceph-csi/scripts/utils.sh

Purpose: shared Kubernetes retry helper for shell scripts.

APIs and control flow: `kubectl_retry action args...` runs `kubectl`, capturing stdout/stderr to temp files. It retries up to `KUBECTL_RETRY` with delay, logs diagnostics to stderr, ignores `AlreadyExists`/warnings for create and `NotFound`/warnings for delete, then emits captured stdout/stderr and returns final status.

State and persistence: creates temporary files named `rook-kubectl-stdout.*` and `rook-kubectl-stderr.*`, removed at end.

Dependencies: kubectl, mktemp, grep, sleep.

Integration points: used by operator, Helm, snapshot, Rook, and Minikube scripts to tolerate transient Kubernetes API failures and idempotent create/delete.

Risks: temp files are in current directory and can remain if interrupted. Only create/delete have special idempotency handling. stdout is appended through retries, so callers parsing stdout can receive output from failed attempts plus success.

Test signals: no unit tests; operational scripts depend on it.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/utils.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/tools/Makefile -->
## sources/control-plane/ceph-csi/tools/Makefile

Purpose: provides a Make target for regenerating deployment YAML artifacts.

Behavior: phony `generate-deploy` depends on `yamlgen/main.go` and runs `go run yamlgen/main.go`.

State and persistence: generator writes deployment YAMLs under `deploy/`.

Dependencies: Go toolchain and yamlgen source dependencies.

Integration points: developer/release workflow for syncing generated manifests from API definitions.

Risks: running from the wrong working directory may affect relative output paths because yamlgen uses `../deploy/...`.

Test signals: no tests; generated file diff is the signal.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/tools/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/tools/yamlgen/main.go -->
## sources/control-plane/ceph-csi/tools/yamlgen/main.go

Purpose: generates checked-in Kubernetes/OpenShift deployment YAMLs from Go API defaults.

APIs and control flow: `yamlArtifacts` lists output filenames, YAML constructor functions, and defaults for OCP SCC, CephFS/NFS/RBD CSI drivers and config maps/RBAC. `main` iterates artifacts. `writeArtifact` creates parent dirs, creates/truncates output file, writes a generated-file header, invokes the constructor via reflection with defaults, and writes returned YAML, panicking on failures or empty output.

State and persistence: writes files under `../deploy/...` relative to `tools/yamlgen`.

Dependencies: Ceph-CSI API deploy packages, `reflect`, `os`, path handling.

Integration points: `tools/Makefile generate-deploy` and release manifest maintenance.

Risks: reflection hides compile-time function signature checking for artifact entries. `os.Create` truncates outputs before validating generated YAML. Directory mode is `0775` despite gosec note because generated files are public.

Test signals: no unit tests; generated manifest diffs and build compile are validation.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/tools/yamlgen/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/troubleshooting/tools/tracevol.py -->
## sources/control-plane/ceph-csi/troubleshooting/tools/tracevol.py

Purpose: troubleshooting CLI that maps Kubernetes PVCs and VolumeSnapshots to Ceph backend RBD images or CephFS subvolumes and validates related RADOS omap entries.

APIs and control flow: argparse accepts PVC name, kubectl/oc command, kubeconfig, namespaces, toolbox mode, Ceph user/key, and config map names. `list_pvc_vol_name_mapping` fetches PVCs, `format_table` gets PV data, volume handle, pool/fs, UUID, omap presence, and backend existence, then prints PrettyTable summaries for RBD and CephFS. Snapshot paths use `kube_client`, inspect VolumeSnapshotContent handles, read omap values, and print RBD/CephFS snapshot tables.

State and persistence: reads Kubernetes resources and Ceph/RADOS state; does not mutate cluster state. Executes commands either locally or through Rook toolbox pod.

Dependencies: Python 3, `prettytable`, `kubectl` or `oc`, Ceph CLI tools, Rook toolbox, Ceph-CSI config map.

Integration points: manual debugging of Ceph-CSI volume/snapshot metadata consistency.

Risks: several command builders add `--id/--key` when `not arg.userkey`, which appears inverted and can pass empty keys. RBD pool id comparison uses `is` instead of `==` for integers. Error detection with `subprocess.Popen(..., stderr=STDOUT)` checks `stderr`, which will always be `None`, so failures are inferred from stdout content or JSON parse errors. Parsing RADOS output with regex is fragile. Main always lists snapshots after PVCs.

Test signals: no automated tests; reliability depends on manual use against clusters.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/troubleshooting/tools/tracevol.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/.cloudbuild.sh -->
## sources/control-plane/csi-driver-host-path/.cloudbuild.sh

Purpose: Google Cloud Build entrypoint for Kubernetes CSI hostpath driver image builds.

Behavior: sources `release-tools/prow.sh` and calls `gcr_cloud_build`.

State and dependencies: delegates all build state and behavior to imported csi-release-tools scripts. Requires that release-tools are present in the repo.

Integration points: referenced by `cloudbuild.yaml` as the build step entrypoint.

Risks: thin wrapper means compatibility depends entirely on release-tools API stability. Shellcheck source is disabled because the file is external/symlink-style.

Test signals: validated by Cloud Build/Prow image jobs.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/.cloudbuild.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/.github/dependabot.yaml -->
## sources/control-plane/csi-driver-host-path/.github/dependabot.yaml

Purpose: configures Dependabot updates for the hostpath driver repository.

Behavior: daily updates for Go modules at `/` and GitHub Actions workflows at `/`, both labeled `area/dependency`, `release-note-none`, and `ok-to-test`, with at most 10 open PRs per ecosystem.

State and dependencies: consumed by GitHub Dependabot.

Integration points: dependency maintenance automation.

Risks: daily cadence can create maintenance churn. Labels must match repository automation expectations.

Test signals: GitHub Dependabot behavior, no local tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/.github/dependabot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/.prow.sh -->
## sources/control-plane/csi-driver-host-path/.prow.sh

Purpose: Prow test/build entrypoint configuration for the Kubernetes CSI hostpath driver.

Behavior: sets Ginkgo parallelism, hostpath driver name, sanity test selection, and a pinned external e2e version `release-1.31` for resizer-related fixes, then sources `release-tools/prow.sh` and calls `main`.

State and dependencies: delegates to release-tools; uses environment variables to steer the shared Prow logic.

Integration points: Kubernetes CSI Prow jobs.

Risks: pinned e2e branch can become stale. High parallelism (`-nodes 40`) can stress CI resources. Typo-like variable `CSI_PROW_GINKO_PARALLEL` matches existing release-tools expectations if intentional.

Test signals: Prow job results.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/.prow.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/Dockerfile -->
## sources/control-plane/csi-driver-host-path/Dockerfile

Purpose: container image for the CSI hostpath plugin binary.

Behavior: starts from Alpine, labels maintainers/description, accepts `binary` build arg defaulting to `./bin/hostpathplugin`, installs util-linux, coreutils, socat, and tar, updates/upgrades Alpine packages, copies binary to `/hostpathplugin`, and sets it as entrypoint.

State and dependencies: runtime image contains the plugin and utilities needed for loop devices/socat/tar operations.

Integration points: built by release-tools Makefile and Cloud Build with architecture-specific binaries.

Risks: `apk update && apk upgrade` makes builds depend on current Alpine repository state and can reduce reproducibility. Base image tag is unpinned `alpine`.

Test signals: image build and hostpath e2e tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/Makefile -->
## sources/control-plane/csi-driver-host-path/Makefile

Purpose: top-level build entrypoint for the hostpath CSI driver.

Behavior: sets `CMDS=hostpathplugin`, default target `all: build`, and includes `release-tools/build.make`, which supplies standard build/image/test targets.

State and dependencies: generated binaries/images are controlled by release-tools.

Integration points: local builds, Prow, and Cloud Build.

Risks: almost all behavior is externalized to release-tools; changes there affect this Makefile. Requires release-tools checkout/symlink.

Test signals: release-tools build targets and CI jobs.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/cloudbuild.yaml -->
## sources/control-plane/csi-driver-host-path/cloudbuild.yaml

Purpose: Google Cloud Build configuration for multi-arch staging image builds.

Behavior: sets 7200s timeout, allows loose substitutions, runs `gcr.io/k8s-staging-test-infra/gcb-docker-gcloud:v20260205-38cfa9523f` with entrypoint `./.cloudbuild.sh`, and passes git tag, base ref, registry, and HOME environment. Defines default substitutions for tag, base ref, and staging project.

State and dependencies: produces container images in Kubernetes staging registry via release-tools and Cloud Build.

Integration points: Kubernetes image promotion workflow and Prow-triggered Cloud Build.

Risks: builder image tag and release-tools behavior are external dependencies. Default substitutions are placeholders and must be overridden by real jobs.

Test signals: Cloud Build success/failure.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/cloudbuild.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/cmd/hostpathplugin/main.go -->
## sources/control-plane/csi-driver-host-path/cmd/hostpathplugin/main.go

Purpose: executable entrypoint for the Kubernetes CSI hostpath test driver.

APIs and control flow: builds `hostpath.Config`, binds many flags for endpoint, driver name, state dir, node id, ephemeral mode, capacity, attach, lifecycle checks, volume size/expansion, topology, controller modify volume, snapshot metadata, mutable parameters, attach limit, version, and proxy endpoint. It initializes klog and automaxprocs, handles `--version`, warns on deprecated ephemeral mode, optionally runs a CSI proxy to another endpoint until signal, validates snapshot metadata block type, creates `hostpath.NewHostPathDriver`, and runs it until termination signal.

State and persistence: driver state dir defaults to `/csi-data-dir`; signal channels control shutdown. Version is injected at build time.

Dependencies: CSI protobuf enum for block metadata type, hostpath driver package, proxy package, klog, csi-lib-utils standard flags.

Integration points: container entrypoint, Prow/e2e tests, and Kubernetes CSI sidecars. Proxy mode supports test suites that intercept/mock CSI behavior.

Risks: invalid snapshot metadata block type exits with status 1 after printing to stdout. Deprecated `node-expand-required` and new `enable-volume-expansion` bind to the same config field; flag order means either can set it. `MaxVolumeExpansionSizeNode` defaults to max volume size when zero.

Test signals: no direct tests here; behavior is exercised by hostpath sanity/e2e suites.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/cmd/hostpathplugin/main.go -->
