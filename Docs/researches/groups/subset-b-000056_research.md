# Research: subset-b-000056

Grouped research for containerd GCE bootstrap helpers, seccomp defaults, snapshot/content/diff/event/image core packages, and image archive/converter utilities. Each section is keyed by the exact source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/gce/cloud-init/node.yaml -->
# sources/cloud-native/containerd/contrib/gce/cloud-init/node.yaml

Purpose: cloud-init configuration for GCE Kubernetes nodes that replaces or layers containerd into the node boot sequence. It writes systemd units for containerd installation, containerd runtime, Kubernetes installation/configuration, health monitors, log rotation, and target ordering.

Important behavior: `containerd-installation.service` downloads `containerd-configure-sh` from instance metadata into `/home/containerd/configure.sh`, makes it executable, and runs it. `containerd.service` depends on installation, loads `overlay`, reads `/etc/containerd/containerd.env`, and starts `/home/containerd/usr/local/bin/containerd`. Kubernetes installation similarly downloads `configure-sh`; configuration and monitor units run helper scripts installed under `/home/kubernetes/bin`.

Control flow and state: `runcmd` stops an existing containerd, reloads systemd, enables all generated units/timers/targets, starts `kubernetes.target`, then restarts Docker if enabled. Persistent state is mostly systemd unit files and downloaded executables under `/home/containerd` and `/home/kubernetes`.

Dependencies and integration: depends on GCE metadata server, cloud-init `write_files`/`runcmd`, systemd, Kubernetes GCE bootstrap conventions, logrotate, overlay kernel module, and optional Docker coexistence.

Risks: metadata-delivered scripts are privileged root execution; metadata unavailability blocks bootstrapping. The bind/remount-exec pattern assumes `/home` supports bind mounts. Duplicate `RemainAfterExit=yes` in one monitor is harmless but noisy. Ordering must remain correct or kubelet can start without a working CRI endpoint.

Test signals: no direct tests. Validation is operational: instance boot, metadata retrieval, systemd unit ordering, containerd socket availability, kubelet monitor health, and logrotate timer activation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/gce/cloud-init/node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/gce/configure.sh -->
# sources/cloud-native/containerd/contrib/gce/configure.sh

Purpose: privileged GCE node installer that fetches containerd/Kubernetes metadata, downloads or uses a preloaded CRI containerd tarball, installs it under `/home/containerd`, and writes the CRI plugin configuration used by kubelet.

Important APIs/functions: `fetch_metadata` queries instance attributes with the required metadata header. `fetch_env` reads YAML metadata such as `kube-env` and `containerd-env`, converts it to readonly shell assignments using Python/YAML, and sources the result. `is_preloaded` checks Kubernetes preload metadata. The main script resolves test/production deployment paths, package prefix, version, tarball name, optional GCS bearer token, and architecture-specific download path.

Control flow and state: strict shell options are enabled. It detects Python 2/3, sources metadata env files, optionally obtains `GCS_BUCKET_TOKEN`, resolves `CONTAINERD_VERSION`, downloads or skips a preloaded tarball, extracts it, removes bundled `crictl`, writes `/etc/containerd/config.toml`, writes Docker Hub mirror host config, writes `/etc/profile.d/containerd_env.sh`, and optionally runs a metadata-supplied test init script. State persists in `/home/containerd`, `/etc/containerd`, and profile/systemd-visible paths.

Dependencies and integration: GCE metadata, curl, YAML Python module, jq for some test paths, sha1sum, tar, Kubernetes GCE env variables, containerd CRI config v2, CNI locations, mirror.gcr.io, and optional extra runtime metadata.

Risks: metadata parsing uses `eval` of generated shell declarations, so correctness of YAML quoting is critical. The tarball name defaults to `linux-amd64` even though `aarch64` uses a GitHub arm64 URL, making architecture handling subtle. Missing version/preload data aborts. Secret token handling disables xtrace briefly but curl command structure still deserves care.

Test signals: no direct tests. Useful checks are generated TOML validity, containerd startup with CRI required plugin, CNI template selection for netd/network policy, authenticated GCS downloads, and test-mode extra init execution.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/gce/configure.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/gce/env -->
# sources/cloud-native/containerd/contrib/gce/env

Purpose: shell environment fragment used by Kubernetes GCE cluster setup to inject containerd-specific cloud-init and runtime metadata.

Important exports: `KUBE_MASTER_EXTRA_METADATA` and `KUBE_NODE_EXTRA_METADATA` point cloud-init user-data and `containerd-configure-sh` to local GCE files, while `containerd-env` points to `../version`. Runtime exports set Kubernetes to remote CRI mode with endpoint `unix:///run/containerd/containerd.sock`, runtime name `containerd`, and image import command using `ctr -n=k8s.io images import`. It also sets network provider fields and kubelet runtime cgroup args.

Control flow and state: resolves `GCE_DIR` relative to the script, verifies a sibling `version` file, then exports variables for a parent kube-up or test harness process. It does not write persistent files itself.

Dependencies and integration: assumes Kubernetes GCE scripts consume `KUBE_*` variables and instance metadata strings. Depends on `cloud-init/master.yaml`, `cloud-init/node.yaml`, `configure.sh`, and `../version`.

Risks: aborts if version file is absent. Some feature gates are legacy and may be ignored or rejected by newer Kubernetes. The empty `NETWORK_PROVIDER` and broad `NON_MASQUERADE_CIDR` are bootstrap-specific and should not leak into unrelated cluster configs.

Test signals: no direct tests; validate by sourcing from kube-up flow and confirming metadata values appear on master/node instances.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/gce/env -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/seccomp/seccomp.go -->
# sources/cloud-native/containerd/contrib/seccomp/seccomp.go

Purpose: OCI spec options for attaching seccomp profiles to container specs.

Important APIs: `WithProfile(profile string)` returns an `oci.SpecOpts` that initializes `s.Linux.Seccomp`, reads a JSON seccomp profile from disk, and unmarshals it into the runtime-spec structure. `WithDefaultProfile()` returns an `oci.SpecOpts` that calls `DefaultProfile(s)`.

Control flow and state: both options mutate only the in-memory OCI `specs.Spec` passed by containerd OCI generation. `WithProfile` performs a synchronous file read and JSON decode. `WithDefaultProfile` depends on process capabilities already being set, because default syscall allowances are capability-sensitive.

Dependencies and integration: integrates with `github.com/containerd/containerd/v2/pkg/oci` spec option pipelines, `core/containers.Container`, and `opencontainers/runtime-spec/specs-go`. It depends on the platform-specific `DefaultProfile` implementation in sibling files.

Risks: both functions assume `s.Linux` is non-nil; callers must use normal Linux spec initialization before applying them. A malformed or unavailable profile fails container spec generation. Applying default profile before capabilities are configured can produce an over- or under-permissive profile.

Test signals: default profile behavior is covered in `seccomp_default_test.go`; external profile loading errors are not directly tested here.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/seccomp/seccomp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/seccomp/seccomp_default.go -->
# sources/cloud-native/containerd/contrib/seccomp/seccomp_default.go

Purpose: Linux implementation of containerd's default seccomp allowlist.

Important APIs/functions: `arches()` maps `runtime.GOARCH` to OCI seccomp architectures, including compatible sub-architectures. `DefaultProfile(sp *specs.Spec)` returns a `*specs.LinuxSeccomp` with `DefaultAction: ActErrno`, architecture list, broad safe syscall allowlist, socket-domain filters that block `AF_ALG` and `AF_VSOCK`, restricted `personality` values, kernel-version gated ptrace/process-vm syscalls, arch-specific syscalls, and capability-gated syscalls.

Control flow and state: the function constructs an in-memory profile each call. It consults the running kernel version for a `>=4.8` gate, switches on GOARCH, then scans `sp.Process.Capabilities.Bounding`. `CAP_SYS_ADMIN` enables broad namespace/mount/bpf/perf and sets an `admin` flag; if admin is absent, it allows only masked namespace `clone` and explicitly returns `ENOSYS` for `clone3`.

Dependencies and integration: uses `golang.org/x/sys/unix`, containerd `kernelversion`, and OCI runtime-spec seccomp types. It feeds `WithDefaultProfile` in OCI generation and ultimately runtime engines such as runc/crun/libseccomp.

Risks: `sp.Process.Capabilities` must be non-nil or this panics. The allowlist includes very new syscall names, so runtime/libseccomp handling of unknown syscalls matters. Socket filtering is intentionally split into three rules due to runc/libseccomp semantics; modifying it risks reopening blocked domains. Capability-derived allowances must stay aligned with kernel security expectations.

Test signals: `seccomp_default_test.go` verifies io_uring syscalls remain disallowed. There is no exhaustive golden test for the syscall list, architectures, or capability gates.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/seccomp/seccomp_default.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/seccomp/seccomp_default_test.go -->
# sources/cloud-native/containerd/contrib/seccomp/seccomp_default_test.go

Purpose: regression test for one security property of the default seccomp profile.

Important test: `TestIOUringIsNotAllowed` builds a default profile with an empty bounding capability set and scans all `ActAllow` syscall entries for `io_uring_enter`, `io_uring_register`, and `io_uring_setup`.

Control flow and state: constructs a minimal `specs.Spec` with `Process.Capabilities.Bounding` initialized, calls `DefaultProfile`, and fails if any disallowed io_uring syscall is in an allow rule.

Dependencies and integration: depends on the Linux default profile implementation and runtime-spec types. It is a targeted security regression test, not a profile conformance suite.

Risks: it only detects allowlisted io_uring names in `ActAllow` blocks; it does not validate default action, `ErrnoRet`, arch lists, capability gates, socket filters, or kernel-version behavior.

Test signals: strong signal for the explicit io_uring policy. Additional tests would be valuable for nil capability handling, blocked socket domains, `clone3` ENOSYS, and capability-derived syscalls.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/seccomp/seccomp_default_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/seccomp/seccomp_default_unsupported.go -->
# sources/cloud-native/containerd/contrib/seccomp/seccomp_default_unsupported.go

Purpose: non-Linux fallback for `DefaultProfile`.

Important API: under build tag `!linux`, `DefaultProfile(sp *specs.Spec)` returns an empty `specs.LinuxSeccomp` object.

Control flow and state: no logic, no state, ignores the input spec. It exists to satisfy package builds on unsupported platforms.

Dependencies and integration: imports runtime-spec types only. Used indirectly by `WithDefaultProfile` on non-Linux builds.

Risks: callers expecting meaningful enforcement on non-Linux receive an empty profile. This is likely acceptable because Linux seccomp is not portable, but downstream code should not interpret the returned object as a hardened policy.

Test signals: no direct tests. Build coverage on non-Linux platforms is the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/seccomp/seccomp_default_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/snapshotservice/service.go -->
# sources/cloud-native/containerd/contrib/snapshotservice/service.go

Purpose: adapter exposing a `snapshots.Snapshotter` as the containerd snapshots gRPC API server.

Important APIs: `FromSnapshotter` returns a `snapshotsapi.SnapshotsServer`. Methods map RPC requests to snapshotter calls: `Prepare`, `View`, `Mounts`, `Commit`, `Remove`, `Stat`, `Update`, server-streaming `List`, `Usage`, and optional `Cleanup`.

Control flow and state: the service holds only the wrapped snapshotter. It translates labels into `snapshots.WithLabels`, commit parent into `snapshots.WithParent`, mount slices through `mount.ToProto`, snapshot info through `proxy.InfoToProto/InfoFromProto`, and native errors through `errgrpc.ToGRPC`. `List` buffers up to 100 `Info` entries per response.

Dependencies and integration: integrates with `api/services/snapshots/v1`, core `mount`, core `snapshots`, snapshot proxy conversion helpers, and `errdefs`/`errgrpc`.

Risks: `List` returns raw walk errors without `errgrpc.ToGRPC`, unlike most unary methods. `Cleanup` only works for snapshotters implementing `snapshots.Cleaner`. Update mask handling trusts proto paths. Batching size is fixed.

Test signals: `service_test.go` specifically verifies `Commit` passes parent and labels via options; broader RPC methods are not covered here.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/snapshotservice/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/snapshotservice/service_test.go -->
# sources/cloud-native/containerd/contrib/snapshotservice/service_test.go

Purpose: unit test for `snapshotservice.service.Commit` option propagation.

Important types/functions: `mockSnapshotter` implements `snapshots.Snapshotter` and captures `commitOpts`. `TestCommitParentOption` drives four cases: parent only, no parent, labels plus parent, and labels only.

Control flow and state: the test creates the service via `FromSnapshotter`, calls `Commit`, applies captured options to a `snapshots.Info`, and compares resulting `Parent` and `Labels`.

Dependencies and integration: uses the snapshots API request type and core snapshot option functions. It exercises only local adapter behavior, not a real gRPC transport.

Risks: label validation checks only expected keys when labels are present and does not assert absent labels for nil cases. Other service methods, error translation, `List` batching, and `Cleanup` are uncovered.

Test signals: good regression coverage for a subtle API addition: preserving `CommitSnapshotRequest.Parent` into `snapshots.WithParent`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/snapshotservice/service_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/v2-migrate.sh -->
# sources/cloud-native/containerd/contrib/v2-migrate.sh

Purpose: one-shot shell migration helper that rewrites Go import paths from pre-v2 containerd paths to containerd/v2 module layout and related package moves.

Important behavior: iterates over all `.go` files outside `vendor`, applies many Perl in-place regex substitutions, then runs `gofmt -s -w`. It first inserts `/v2` for `github.com/containerd/containerd` imports except `/v2` and `/api`, then rewrites moved packages into `core`, `plugins`, `pkg`, `internal`, split-out repositories, and API packages.

Control flow and state: mutates every matching Go file in the current working tree. There is no dry-run, backup, or git safety check.

Dependencies and integration: depends on POSIX shell, `find`, `grep`, Perl, and gofmt. Encodes containerd v2 package layout knowledge, including split packages such as `github.com/containerd/platforms`, `github.com/containerd/errdefs`, `github.com/containerd/plugin`, and `github.com/moby/sys/user/userns`.

Risks: regex-based import rewriting can miss unusual import formatting or rewrite unintended strings if they look like imports. Running from the wrong directory can damage unrelated Go code. It does not update non-Go references or module requirements.

Test signals: no tests. Validation requires `git diff`, `go test`, `go list`, and manual review of import aliases after running.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/v2-migrate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/containers/containers.go -->
# sources/cloud-native/containerd/core/containers/containers.go

Purpose: core container metadata model and storage interface.

Important APIs/types: `Container` captures namespace-scoped `ID`, mutable `Labels`, `Image`, runtime `Spec`, optional `SnapshotKey`, immutable `Runtime`, `Snapshotter`, and `SandboxID`, timestamps, and typed `Extensions`. `RuntimeInfo` holds runtime name and typed options. `Store` defines CRUD and filtered list operations.

Control flow and state: no implementation, only contracts. Comments document mutability rules that store implementations must enforce: ID/runtime/snapshotter/sandbox identity fields are immutable while labels/image/spec/snapshot key are mutable.

Dependencies and integration: uses `context.Context`, timestamps, and `typeurl.Any` for runtime options, OCI specs, and extensions. Store implementations are provided elsewhere, commonly metadata-backed services.

Risks: invariants are comment-level in this file; enforcement depends on backing stores. Typeurl payload compatibility matters for persisted specs/options. Partial updates rely on implementation-specific fieldpath handling.

Test signals: none in this file. Tests should target store implementations for immutability, namespace isolation, fieldpath updates, and extension round-trips.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/containers/containers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/content/adaptor.go -->
# sources/cloud-native/containerd/core/content/adaptor.go

Purpose: filter adaptor for `content.Info` values.

Important APIs: `AdaptInfo(info Info)` returns a `filters.Adaptor` supporting `digest` and `labels.*` field paths. `checkMap` joins nested label field path components with `.` before looking up a map key.

Control flow and state: stateless closure over one `Info`. Empty field paths are absent. `size` is recognized but deliberately unsupported with a TODO for size-based filtering.

Dependencies and integration: integrates with containerd's `pkg/filters` package, allowing content stores or walkers to evaluate filters against content metadata.

Risks: label keys containing dots are intentionally addressed through joined field paths, but there is no escaping distinction between nested and literal dots. Size filters silently appear unsupported, which can surprise callers.

Test signals: `adaptor_test.go` covers empty paths, digest, unsupported size, simple labels, and dotted label keys.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/content/adaptor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/content/adaptor_test.go -->
# sources/cloud-native/containerd/core/content/adaptor_test.go

Purpose: unit tests for `AdaptInfo`.

Important coverage: table-driven tests check absent empty field path, digest string conversion, unsupported `size`, simple `labels.foo`, and joined dotted label path `labels.foo.bar.qux`.

Control flow and state: each test constructs an `Info`, calls `AdaptInfo`, then calls `Field` with the field path and compares value plus presence with testify assertions.

Dependencies and integration: exercises the filter adaptor without invoking the full filters parser/matcher.

Risks: no negative label lookup tests with non-empty maps, no nil map behavior beyond absent labels through default zero values, and no integration with parsed filter expressions.

Test signals: good focused signal for the adaptor's current public behavior, especially that size is not currently filterable.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/content/adaptor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/content/content.go -->
# sources/cloud-native/containerd/core/content/content.go

Purpose: central content store interface definitions and option types.

Important APIs/types: `Store` combines `Manager`, `Provider`, `IngestManager`, and `Ingester`. `ReaderAt` adds `Size` and `Close`. `Provider.ReaderAt`, `Ingester.Writer`, ingest management methods, `Info`, `Status`, `WalkFunc`, `InfoProvider`, `Manager`, and `Writer` define the content lifecycle. `Syncer`, `ReferrersProvider`, `Opt`, `WithLabels`, `WriterOpts`, `WriterOpt`, `WithDescriptor`, and `WithRef` complete the contract.

Control flow and state: no implementation. Comments define lifecycle semantics: writes are invisible until commit, active ingestions are tracked by ref, committed content is queried by digest, and commit closes the writer.

Dependencies and integration: OCI descriptors and opencontainers digests are the exchange currency. Implementations include local stores, metadata stores, and remote proxies.

Risks: behavior such as resumability, locking, partial update fieldpaths, and duplicate commits is contract-dependent and must be consistently implemented. `WithLabels` replaces label map on the mutable `Info` object rather than merging.

Test signals: the reusable `testsuite` package validates many implementations against these contracts.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/content/content.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/content/helpers.go -->
# sources/cloud-native/containerd/core/content/helpers.go

Purpose: helper functions for reading, writing, resuming, copying, and checking content blobs.

Important APIs/functions: `NewReader` adapts `ReaderAt` to `io.Reader`, using a custom `Reader()` method when present. `BlobReadSeeker` and `ReadBlob` use embedded descriptor `Data` when size and digest validate. `WriteBlob` opens and commits a writer. `OpenWriter` retries unavailable refs with randomized exponential backoff. `Copy`, `CopyReaderAt`, `CopyReader`, `seekReader`, `copyWithBuffer`, and `Exists` implement resumable copying and existence checks.

Control flow and state: `Copy` checks writer status, resumes source at the writer offset, copies through a pooled 1 MiB buffer, retries on `ErrReset`, commits, and treats `ErrAlreadyExists` as success. `seekReader` prefers `io.Seeker`, then `io.ReaderAt`, then discarding bytes.

Dependencies and integration: uses `errdefs`, containerd logging, internal random utility, OCI descriptors, and go-digest.

Risks: `ReadBlob` allocates the full blob and is unsuitable for layers. Descriptor data with matching size but invalid digest returns an error instead of falling through. Non-seekable resume discards data, which may be expensive or impossible for streaming sources. `OpenWriter` returns the last unavailable error on context cancellation.

Test signals: `helpers_test.go` covers reset retries, offsets, already-exists commit handling, descriptor data validation, and provider bypass/fallback behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/content/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/content/helpers_test.go -->
# sources/cloud-native/containerd/core/content/helpers_test.go

Purpose: unit tests for content helper copy and descriptor-data fast paths.

Important coverage: `TestCopy` validates no-offset copying, offset resume from seeker and unseekable sources, `ErrAlreadyExists` on commit, and repeated `ErrReset` success/failure paths using `fakeWriter`. `TestUseDescriptorData` covers matching data/digest/size, sha512, empty data, size mismatches, malformed or unsupported digests, and digest mismatch. `TestBlobReadSeeker_WithDescriptorData` and `TestReadBlob_WithDescriptorData` verify valid embedded data bypasses provider and invalid/mismatched data falls back or errors.

Control flow and state: tests use in-memory buffers, fake content provider, and fake reader-at implementation to assert whether the content provider was invoked.

Dependencies and integration: imports crypto hash registration for go-digest algorithms, errdefs, OCI descriptors, and testify.

Risks: does not cover `OpenWriter` retry timing, `CopyReaderAt`, `CopyReader`, `Exists`, or very large allocation behavior. Some fake reset closures capture `Status` by value, so they simulate only the intended buffer reset path.

Test signals: strong signal around descriptor `Data` trust rules and resumable `Copy` behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/content/helpers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/content/proxy/content_reader.go -->
# sources/cloud-native/containerd/core/content/proxy/content_reader.go

Purpose: remote `content.ReaderAt` implementation backed by the content service streaming read API.

Important type/methods: `remoteReaderAt` stores parent context, digest, size, and a `TTRPCContentClient`. `Size` returns known size. `ReadAt` sends `ReadContentRequest` with digest, offset, and requested size, receives stream chunks, and fills the caller buffer. `Close` is a no-op.

Control flow and state: each `ReadAt` call opens a child context and cancels it to avoid gRPC stream goroutine leaks, then repeatedly `Recv`s until the buffer is filled or an error occurs. State is immutable except local counters.

Dependencies and integration: used by `proxyContentStore.ReaderAt`. Depends on content service API and go-digest.

Risks: it does not specially translate EOF semantics; remote stream errors propagate directly. If the server returns more bytes than remaining buffer, extra bytes are ignored by `copy`, but the loop exits once the requested buffer is filled. The parent context lifetime controls all future reads.

Test signals: no direct tests here; behavior is indirectly covered by content store tests against the proxy implementation where present.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/content/proxy/content_reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/content/proxy/content_store.go -->
# sources/cloud-native/containerd/core/content/proxy/content_store.go

Purpose: client-side proxy implementing `content.Store` over containerd content gRPC or ttrpc APIs.

Important APIs: `NewContentStore` accepts `contentapi.ContentClient`, `grpc.ClientConnInterface`, `contentapi.TTRPCContentClient`, or `*ttrpc.Client` and returns a `content.Store`. Methods implement `Info`, `Walk`, `Delete`, `ReaderAt`, `Status`, `Update`, `ListStatuses`, `Writer`, and `Abort`. Conversion helpers bridge gRPC client streams to ttrpc-shaped interfaces and convert `content.Info` to/from protobuf.

Control flow and state: read operations call remote unary/streaming APIs and translate errors to native errdefs. `ReaderAt` first calls `Info` to discover size. `Writer` applies writer opts, negotiates a write stream by sending a `STAT` request with ref/size/expected, and returns a `remoteWriter` with initial offset.

Dependencies and integration: core content interfaces, content service protobufs, grpc, ttrpc, protobuf timestamp helpers, OCI descriptors, and `errgrpc`.

Risks: constructor panics on unsupported clients. `infoFromGRPC` trusts digest strings without validation. `Walk` stops immediately on callback errors without remote cancellation beyond stream context. The comment on `Abort` has a stray phrase but implementation is direct.

Test signals: no direct tests in this file; expected to be exercised by service/proxy integration and content testsuite runs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/content/proxy/content_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/content/proxy/content_writer.go -->
# sources/cloud-native/containerd/core/content/proxy/content_writer.go

Purpose: remote content writer backed by a bidirectional content write stream.

Important type/methods: `remoteWriter` tracks ref, stream client, offset, and digest. `send` performs synchronous request/response exchange and updates digest from responses. `Status`, `Digest`, `Write`, `Commit`, `Truncate`, and `Close` implement `content.Writer`.

Control flow and state: `Write` chunks input into half of `defaults.DefaultMaxSendMsgSize`, sends `WRITE` requests with the current offset, updates offset based on server response, and returns `io.ErrShortWrite` if the server advances less than the sent chunk. `Commit` applies content opts to collect labels, sends `COMMIT`, validates size and digest when provided, updates local state, and always closes the stream in a defer. `Truncate` only adjusts the local offset until a later write/commit validates it remotely.

Dependencies and integration: content service API, errgrpc, default message-size constants, protobuf time conversion, go-digest.

Risks: `Write` returns `0` on the first chunk send error even if previous chunks in the same call succeeded, because the error branch does not return accumulated `n`. `Truncate` is optimistic. Commit closes the stream even on error, so callers needing retry must open a new writer.

Test signals: no direct unit tests here; content testsuite can expose status, resume, commit, and short-write behavior when run through the proxy.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/content/proxy/content_writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/content/testsuite/testsuite.go -->
# sources/cloud-native/containerd/core/content/testsuite/testsuite.go

Purpose: reusable conformance suite for `content.Store` implementations.

Important APIs/functions: `StoreInitFn` initializes stores for tests. `ContentSuite` runs core writer/status/resume/blob/label/error-state tests. Cross-namespace suites validate shared and isolated content policies. `ContextWrapper`, `SetContextWrapper`, and `Name` support namespace/lease decoration. Helpers include `checkContentStoreWriter`, `checkResumeWriter`, `checkCommitExists`, `checkCommitErrorState`, `checkUpdateStatus`, `checkLabels`, resume strategies, cross-namespace checks, `checkStatus`, `checkInfo`, `checkContent`, and deterministic `createContent`.

Control flow and state: `makeTest` creates a temp root, initializes the store, optionally wraps context, registers cleanup, and dumps temp content on failure. Tests write deterministic random content, check writer status/digest/timestamps, reopen refs, verify commit errors preserve state, mutate labels, and assert cross-namespace visibility rules.

Dependencies and integration: core content helpers/interfaces, `testutil.DumpDirOnFailure`, errdefs, logtest, OCI descriptors, go-digest, testify.

Risks: timestamp assertions are relaxed on Windows. Some expectations are intentionally skipped/commented where implementations do not guarantee `Status.Expected`. Large blob test writes `16 << 21` bytes, so slow stores need capacity.

Test signals: very strong behavioral contract for local and remote content stores, especially resumability, lock/unavailable refs, commit failure recovery, labels, and namespace policy.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/content/testsuite/testsuite.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/diff/apply/apply.go -->
# sources/cloud-native/containerd/core/diff/apply/apply.go

Purpose: filesystem diff applier that reads layer content from a content provider, runs stream processors, applies the resulting tar stream to mounts, and returns the uncompressed applied-layer descriptor.

Important APIs/types: `NewFileSystemApplier`, `NewFileSystemApplierWithMountManager`, `fsApplier.Apply`, `readCounter`, `progressReader`, and read closer adapters.

Control flow and state: `Apply` gathers `diff.ApplyConfig`, opens content `ReaderAt`, wraps progress if requested, builds a processor chain using the descriptor media type, repeatedly resolves processors until it reaches `ocispec.MediaTypeImageLayer`, tees processed bytes into a canonical digester, optionally activates a mount manager for multi-mount setups, calls platform-specific `apply`, drains trailing data, checks processor `Err()` hooks, and returns descriptor with uncompressed size/digest/media type.

Dependencies and integration: core content, core diff processors, mount manager, archive application via platform files, go-digest, OCI descriptors, errdefs, logging.

Risks: processor chain must eventually produce OCI layer media type or fail. Progress reports bytes read before each read plus final close. Mount manager activation uses random-ish IDs and is skipped for single mounts. Draining trailing data is important for processor error propagation.

Test signals: platform-specific helper has a small Linux test; full `Apply` behavior requires integration tests with content stores and mounts.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/diff/apply/apply.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/diff/apply/apply_linux.go -->
# sources/cloud-native/containerd/core/diff/apply/apply_linux.go

Purpose: Linux implementation of applying a tar diff stream onto mounted filesystems.

Important functions: `apply` handles overlay fast path, bind-mount sync path, and generic temp mount path. `getOverlayPath` parses `upperdir=` and `lowerdir=` mount options. `doSyncFs` calls `unix.Syncfs` on a path.

Control flow and state: for a single overlay mount outside a user namespace, it extracts directly into `upperdir` with `archive.OverlayConvertWhiteout` and optional lower parents. If overlay options are invalid, it falls back to temp mounting. For single bind mounts with sync requested, it defers `syncfs` on the source after generic apply. All other cases use `mount.WithTempMount` and `archive.Apply`.

Dependencies and integration: containerd mount package, archive apply package, errdefs, `moby/sys/userns`, and `golang.org/x/sys/unix`.

Risks: overlay fast path is disabled in user namespaces because whiteout conversion uses device nodes. Overlay option parsing is string-based and only understands `upperdir`/`lowerdir`. `syncfs` requires opening the target path and may fail due to permissions or missing path.

Test signals: `apply_linux_test.go` covers `getOverlayPath` success and missing upperdir error. Extraction/sync behavior is not directly unit-tested here.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/diff/apply/apply_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/diff/apply/apply_linux_test.go -->
# sources/cloud-native/containerd/core/diff/apply/apply_linux_test.go

Purpose: unit test for Linux overlay mount option parsing.

Important test: `TestGetOverlayPath` verifies a mount option list with `upperdir`, colon-separated `lowerdir`, and `workdir` yields the expected upper path and two lower parents, then verifies missing `upperdir` returns an error.

Control flow and state: pure parsing test, no filesystem or mount operations.

Dependencies and integration: covers helper used by `apply_linux.go` overlay fast path.

Risks: does not test malformed lowerdir, multiple upperdir entries, escaping, user namespace branch, archive application, or syncfs behavior.

Test signals: useful guard for the most important overlay option extraction invariant.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/diff/apply/apply_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/diff/apply/apply_other.go -->
# sources/cloud-native/containerd/core/diff/apply/apply_other.go

Purpose: non-Linux implementation of diff application.

Important function: build-tagged `apply` applies tar streams either directly into a bind mount source when bind mounts are unsupported and there is a single bind mount, or via `mount.WithTempMount` otherwise.

Control flow and state: on direct bind path, it adds `archive.WithNoSameOwner` when not root, applies to `mounts[0].Source`, and ignores sync because Windows sync semantics are TODO. Generic path temp-mounts and applies normally.

Dependencies and integration: core mount and archive packages plus `os.Getuid`.

Risks: `os.Getuid` availability/meaning varies by non-Linux platform. Sync is explicitly unimplemented. The direct bind path depends on `mount.HasBindMounts` platform constant.

Test signals: no direct tests. Platform build and integration tests must validate behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/diff/apply/apply_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/diff/diff.go -->
# sources/cloud-native/containerd/core/diff/diff.go

Purpose: core diff comparison/application interfaces and option definitions.

Important APIs/types: `Config`, `Opt`, `Comparer`, `ApplyConfig`, `ApplyOpt`, and `Applier`. Options include `WithCompressor`, `WithMediaType`, `WithReference`, `WithLabels`, `WithPayloads`, `WithSyncFs`, `WithProgress`, and `WithSourceDateEpoch`.

Control flow and state: no implementation; defines contracts. `Comparer.Compare` computes diff content between lower/upper mounts. `Applier.Apply` applies descriptor content to mounts. Options mutate config structs used by implementations.

Dependencies and integration: mount types, OCI descriptors, `typeurl.Any` for processor payloads, and time for reproducible source date epoch.

Risks: compressor and media type must be coherent; comments require media type when custom compressor is used, but enforcement is in implementations. Progress semantics are implementation-defined except start/final expectation. Source date epoch only affects diff generation implementations that honor it.

Test signals: behavior is tested in concrete diff implementations/proxies rather than this contract file.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/diff/diff.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/diff/proxy/differ.go -->
# sources/cloud-native/containerd/core/diff/proxy/differ.go

Purpose: remote diff comparer/applier that forwards operations to the diff gRPC service.

Important APIs: `NewDiffApplier` returns a `diffRemote` implementing both `Apply` and `Compare`. `Apply` converts descriptors/mounts/payloads into `ApplyRequest`; `Compare` converts mount sets and diff config into `DiffRequest`.

Control flow and state: `Apply` applies local options, marshals processor payloads with typeurl, invokes progress callback with 0 before RPC and descriptor size after success, sends `SyncFs`, and converts response descriptor. `Compare` applies options, pulls source date epoch from context when not explicitly set, converts it to protobuf timestamp, sends media type/ref/labels, and returns response descriptor.

Dependencies and integration: diff API protobufs, errgrpc, mount/OCI conversion helpers, epoch context, typeurl, protobuf `Any`, timestamp helpers.

Risks: progress is coarse for remote apply; it does not stream server progress. `NewDiffApplier` returns `any`, so callers rely on type assertions or documented dual-interface behavior. Payload marshal assumes proto-compatible typeurl payloads.

Test signals: no direct tests here; service integration should cover descriptor/mount translation and epoch propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/diff/proxy/differ.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/diff/stream.go -->
# sources/cloud-native/containerd/core/diff/stream.go

Purpose: stream processor registry and default layer decompression pipeline for diff application.

Important APIs/types: `RegisterProcessor`, `GetProcessor`, `Handler`, `StaticHandler`, `StreamProcessorInit`, `RawProcessor`, `StreamProcessor`, `NewProcessorChain`, `BinaryHandler`, and default `compressedHandler`. `ErrNoProcessor` signals missing handlers.

Control flow and state: package init registers `compressedHandler`. Registered handlers are stored globally and searched in reverse registration order so user handlers take precedence. `compressedHandler` uses image media type compression detection to either wrap a decompressor or pass through to a standard processor, both returning OCI uncompressed layer media type. `BinaryHandler` builds handler closures that invoke external processors for selected media types.

Dependencies and integration: core image media type helpers, archive compression package, typeurl payloads, OCI media types, and platform-specific `NewBinaryProcessor`.

Risks: global handler registry is unsynchronized and should be configured during init, not concurrently. Repeated registration affects process-wide behavior. External binary processors introduce process, payload, and error propagation concerns.

Test signals: no direct tests in this file. Coverage depends on diff apply and configured stream processor integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/diff/stream.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/diff/stream_unix.go -->
# sources/cloud-native/containerd/core/diff/stream_unix.go

Purpose: Unix implementation of external binary stream processors.

Important APIs/types: `NewBinaryProcessor` starts an external command that transforms a stream from input media type to return media type. `binaryProcessor` implements `StreamProcessor`, `RawProcessor`, `Err`, `Wait`, and cleanup methods.

Control flow and state: it constructs `exec.CommandContext`, inherits environment, appends custom env and `STREAM_PROCESSOR_MEDIATYPE`, optionally marshals typeurl payload into an extra file descriptor, connects input from either a raw file or stream, pipes stdout to the returned processor reader, captures stderr, starts the process, closes duplicated handles, and records exit errors asynchronously.

Dependencies and integration: os/exec, pipes, protobuf marshal of typeurl payloads, and the diff stream registry.

Risks: `Close` kills the process after closing the read pipe; consumers must call `Err` or `Wait` to observe processor failures. Payload delivery via extra file descriptor requires processor agreement. Stderr is fully buffered in memory. RawProcessor input file is closed after start.

Test signals: no direct unit tests. Integration should cover processor exit errors, payload fd, and cancellation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/diff/stream_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/diff/stream_windows.go -->
# sources/cloud-native/containerd/core/diff/stream_windows.go

Purpose: Windows implementation of external binary stream processors.

Important APIs/types: same processor surface as Unix, but payload delivery uses a named pipe path exposed through `STREAM_PROCESSOR_PIPE`. `getUiqPath` creates and removes a temp directory to get a unique path component.

Control flow and state: when payload exists, it creates a winio named pipe, starts a goroutine to accept a connection and copy marshaled payload bytes, sets media type env, connects stdin/stdout/stderr, starts the process, and returns a `binaryProcessor` that reads stdout and tracks process completion.

Dependencies and integration: `github.com/Microsoft/go-winio`, os/exec, typeurl/protobuf marshal, containerd logging, and diff stream registry.

Risks: payload goroutine logs but does not propagate accept/copy errors to processor construction. Named pipe cleanup is listener close only. Like Unix, stderr is buffered and errors require `Err`/`Wait`. `Close` kills the process.

Test signals: no direct tests. Windows integration tests are needed for named pipe payload compatibility and cancellation behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/diff/stream_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/events/events.go -->
# sources/cloud-native/containerd/core/events/events.go

Purpose: core event model and publish/forward/subscribe interfaces.

Important APIs/types: `Envelope` holds timestamp, namespace, topic, and typeurl-encoded event payload. `Envelope.Field` implements filter access for namespace, topic, and nested event fields when the decoded event implements `Field([]string)`. `Publisher`, `Forwarder`, and `Subscriber` define event bus contracts.

Control flow and state: `Field` is read-only and decodes the `typeurl.Any` payload on demand for `event.*` lookups.

Dependencies and integration: typeurl for typed event encoding and containerd filter adaptors via the `Field` convention.

Risks: timestamp is intentionally not filterable here. Decode errors or event types lacking a field adaptor make `event.*` absent. Repeated field matching can repeatedly unmarshal payloads.

Test signals: exchange filter tests exercise `Envelope.Field` indirectly for topics and event fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/events/events.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/events/exchange/exchange.go -->
# sources/cloud-native/containerd/core/events/exchange/exchange.go

Purpose: in-process event exchange implementing publisher, forwarder, and subscriber interfaces.

Important APIs/functions: `NewExchange`, `Exchange.Forward`, `Exchange.Publish`, `Exchange.Subscribe`, `validateTopic`, `validateEnvelope`, and `adapt`.

Control flow and state: `Exchange` wraps a docker `go-events` broadcaster. `Publish` requires namespace from context, validates topic, marshals the event, stamps UTC time, and writes an envelope. `Forward` validates a caller-supplied envelope and writes it unchanged. `Subscribe` creates a broadcaster channel/queue, optionally wraps it in a filters matcher, forwards envelopes to an output channel until context cancellation, and reports terminal errors on a buffered error channel.

Dependencies and integration: namespaces, identifiers, filters, errdefs, logging, typeurl, and docker/go-events.

Risks: filters match any provided filter string, with comma syntax used by the filter parser for AND. The subscription goroutine sends a nil error on normal cancellation because it writes `errq <- err`; consumers must handle nil. Invalid non-envelope events should be impossible through public methods but is guarded.

Test signals: `exchange_test.go` covers fan-out, filtering, and topic validation for publish/forward.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/events/exchange/exchange.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/events/exchange/exchange_test.go -->
# sources/cloud-native/containerd/core/events/exchange/exchange_test.go

Purpose: unit tests for the in-process event exchange.

Important coverage: `TestExchangeBasic` publishes three container-create events and verifies two subscribers receive all of them. `TestExchangeFilters` creates multiple subscriptions with no filters, topic filters, event field filters, regex filters, OR filters, and an AND topic/id filter. `TestExchangeValidateTopic` verifies publish and forward accept slash-prefixed topics and reject a topic without a leading slash with `ErrInvalidArgument`.

Control flow and state: tests use namespace contexts, async publisher goroutines, subscriber cancellation once expected events are received, and typeurl unmarshal plus protobuf-aware cmp.

Dependencies and integration: API event types, core events, namespaces, prototest comparison helpers, errdefs, typeurl.

Risks: tests can hang if expected events are not received because they wait on channels. They do not cover invalid filter syntax, invalid namespace, empty topic, one-component slash-only topic, forwarded zero timestamp, or unexpected broadcaster event types.

Test signals: strong signal for event fan-out and filter semantics over topic and event fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/events/exchange/exchange_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/events/proxy/remote_events.go -->
# sources/cloud-native/containerd/core/events/proxy/remote_events.go

Purpose: remote event service client implementing publish, forward, and subscribe over gRPC or ttrpc.

Important APIs/types: `EventService` combines core event interfaces. `NewRemoteEvents` accepts gRPC/ttrpc clients or connections and returns either `grpcEventsProxy` or `ttrpcEventsProxy`. Both proxies implement `Publish`, `Forward`, and streaming `Subscribe`.

Control flow and state: publish marshals event into typeurl `Any`, wraps it in API request, and translates RPC errors to native. Forward converts envelope timestamp and event payload into API envelope. Subscribe opens a remote stream, starts a goroutine to receive API envelopes, converts timestamps to `time.Time`, forwards envelopes on `evq`, and reports receive/context errors on `errq`.

Dependencies and integration: events service API, API envelope types, typeurl, grpc, ttrpc, errgrpc, protobuf timestamp helpers.

Risks: constructor panics on unsupported client. Subscribe returns remote receive errors directly rather than `errgrpc.ToNative`. Event queue channel is not explicitly closed, only error queue closes; consumers should watch errs/context. gRPC and ttrpc implementations are duplicated and must stay in sync.

Test signals: no direct tests here. Integration tests should cover stream cancellation, error translation, and envelope round-trip.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/events/proxy/remote_events.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/images/annotations.go -->
# sources/cloud-native/containerd/core/images/annotations.go

Purpose: central constants for containerd image-related descriptor annotations.

Important constants: `AnnotationImageName` stores the containerd image name on descriptors in `index.json`. `AnnotationManifestSubject` marks descriptors that are referrers to a subject manifest and should not create a new image during import/export handling.

Control flow and state: none; constants only.

Dependencies and integration: used by image archive exporter/importer, image stores, and referrer handling to preserve names and avoid treating subject referrers as primary images.

Risks: annotation spelling is part of archive compatibility. Misusing `AnnotationManifestSubject` can hide legitimate images or create unwanted images.

Test signals: no direct tests. Archive import/export tests should assert these annotations are written and interpreted correctly.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/images/annotations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/images/archive/exporter.go -->
# sources/cloud-native/containerd/core/images/archive/exporter.go

Purpose: OCI/Docker-compatible image archive exporter.

Important APIs/functions: export options include `WithPlatform`, `WithAllPlatforms`, `WithSkipDockerManifest`, `WithImage`, `WithImages`, `WithManifest`, `WithBlobFilter`, `WithSkipNonDistributableBlobs`, `WithReferrersProvider`, and `WithSkipMissing`. Core helpers include `addNameAnnotation`, `copySourceLabels`, `Export`, `getRecords`, `filterReferrers`, `blobRecord`, `ociLayoutFile`, `ociIndexRecord`, `manifestsRecord`, and `writeTar`.

Control flow and state: `Export` builds tar records beginning with `oci-layout`, copies distribution source labels into descriptors, walks manifest/index trees to collect blob records, handles platform selection and index resolution for Docker `manifest.json`, optionally includes referrers, writes `index.json`, optionally writes Docker-compatible `manifest.json`, creates blob directory records, sorts records by path, skips duplicate tar names, and verifies copy sizes/digests.

Dependencies and integration: content info/reader provider, image handlers/walkers, OCI/Docker media types, platforms matching, labels, errdefs, tar/json.

Risks: `WithSkipMissing` can export a manifest without descendants if a child is missing, which is intentional but subtle. Platform sorting assumes a non-nil platform comparer when multiple manifests are selected. Duplicate tar path suppression can hide descriptor duplication. Blob filtering returns empty records that must be filtered by `writeTar`.

Test signals: no direct file tests in this subset; archive integration tests should verify OCI layout, Docker manifest compatibility, missing blob semantics, referrers, non-distributable filtering, and digest validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/images/archive/exporter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/images/archive/importer.go -->
# sources/cloud-native/containerd/core/images/archive/importer.go

Purpose: Docker and OCI image archive importer that ingests tar entries into a content store and returns an OCI index descriptor.

Important APIs/functions: `WithImportCompression`, `ImportIndex`, `onUntarJSON`, `onUntarBlob`, `resolveLayers`, `compressBlob`, `writeManifest`, and `detectLayerMediaType`.

Control flow and state: `ImportIndex` scans tar entries, tracks symlinks, ingests regular files as blobs, parses `oci-layout` and Docker `manifest.json`, then either returns the OCI `index.json` descriptor or constructs a new OCI index from Docker manifests. Docker import resolves configs/layers, optionally maps symlinked layers, normalizes repo tags into annotations, writes schema2 manifests and final index into the content store.

Dependencies and integration: tar/json, content store ingestion/reading/walking, archive compression, image platform/media helpers, labels, errdefs, platforms.

Risks: JSON parsing is capped at 20 MiB. All regular files outside recognized JSON are ingested as blobs, so malformed archive layouts can consume content store space before failing. `resolveLayers` reuses existing compressed blobs by `LabelUncompressed` and can compress uncompressed layers, making media type/digest changes. Windows platform OSVersion is filled from host defaults when missing.

Test signals: no direct tests in this subset. Important coverage includes OCI layout import, Docker v1.1/v1.2 import, symlink layers, compression option, missing files, empty layer media detection, and normalized annotations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/images/archive/importer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/images/archive/reference.go -->
# sources/cloud-native/containerd/core/images/archive/reference.go

Purpose: reference translation helpers for image archive import/export.

Important APIs/functions: `FilterRefPrefix`, `AddRefPrefix`, `refTranslator`, `isImagePrefix`, `normalizeReference`, `familiarizeReference`, `ociReferenceName`, and `DigestTranslator`.

Control flow and state: translators return closures. Tag-only references are converted to `image:tag`; full references containing `/`, `:`, or `@` are either returned or filtered based on prefix. Normalize/familiarize delegate to Docker distribution reference parsing. `ociReferenceName` prefers the parsed object component when it is not a digest object, otherwise uses the full name. `DigestTranslator` creates `prefix@digest` strings.

Dependencies and integration: containerd reference parser, Docker distribution reference parser, go-digest. Used by archive importer/exporter to set `io.containerd.image.name`, OCI ref names, and Docker `RepoTags`.

Risks: the heuristic for full references is simple and may classify unusual names based on punctuation. Prefix checking avoids partial namespace matches by requiring delimiter after prefix. OCI ref names are constrained by OCI grammar, so digest references use the full name.

Test signals: no direct tests here. Archive reference tests should cover tag-only translation, prefix filtering, partial prefix rejection, normalized Docker names, familiar tags, and digest references.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/images/archive/reference.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/images/converter/converter.go -->
# sources/cloud-native/containerd/core/images/converter/converter.go

Purpose: top-level image conversion entry point and option wiring.

Important APIs/types: `Opt`, `WithLayerConvertFunc`, `WithDockerToOCI`, `WithPlatform`, `WithIndexConvertFunc`, `WithUpdateManifest`, `Client`, and `Convert`.

Control flow and state: `Convert` applies options, defaults platform matcher to `platforms.All`, builds a default index conversion function unless supplied, opens a lease through the client, fetches source image, converts its target descriptor tree, builds destination image metadata, deletes any existing destination when `dstRef != srcRef`, then creates or updates image service entry.

Dependencies and integration: content store, image store, leases, platforms, digest map in default converter when update callback is used.

Risks: `WithDockerToOCI(v bool)` ignores its parameter and always enables conversion. Destination delete ignores errors before create. Conversion occurs under a lease, but deletion/create semantics can still race with external image operations. Caller-supplied convert functions must preserve content and labels correctly.

Test signals: no direct tests here. Conversion integration tests should cover same-ref update, different-ref create, lease release, option wiring, and the `WithDockerToOCI(false)` behavior if intentional.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/images/converter/converter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/images/converter/default.go -->
# sources/cloud-native/containerd/core/images/converter/default.go

Purpose: default recursive image descriptor converter for layers, manifests, indexes, configs, Docker-to-OCI media types, GC labels, and diff ID rewrites.

Important APIs/types: `ConvertFunc`, `UpdateManifestFunc`, `DefaultIndexConvertFunc`, `ConvertHookFunc`, `ConvertHooks`, `IndexConvertFuncWithHook`, `defaultConverter`, `DualConfig`, `ReadJSON`, `WriteJSON`, `ConvertDockerMediaTypeToOCI`, and `ClearGCLabels`.

Control flow and state: `convert` dispatches by media type, runs optional post-convert hook, converts Docker media types to OCI or strips annotations from Docker descriptors. `convertManifest` reads manifest labels, converts layers concurrently, updates GC labels, records old->new diff IDs, converts config, writes a new manifest when modified, and calls update-manifest callback. `convertIndex` concurrently filters platforms and converts children while updating labels. `convertConfig` rewrites `rootfs.diff_ids` using `diffIDMap` and clears Docker legacy dummy image IDs. JSON writes create new content blobs with preserved labels.

Dependencies and integration: content store, images helpers, platforms, errgroup, log, go-digest, OCI specs.

Risks: layer conversion goroutines update a shared `diffIDMap`; locks protect the map, but config conversion relies on layer conversion finishing first. Platform filtering removes descriptors and GC labels. Annotation stripping for Docker media types can surprise hooks. `ReadJSON` returns the store's label map directly, so mutations affect the map object passed into writes.

Test signals: no direct tests in this subset. Important coverage includes concurrent layer conversion, GC label updates, diffID config rewrite, media type conversion, hook behavior, and platform filtering.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/images/converter/default.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/images/converter/erofs/erofs.go -->
# sources/cloud-native/containerd/core/images/converter/erofs/erofs.go

Purpose: EROFS layer conversion support for image converter pipelines, plus manifest platform update for EROFS images.

Important APIs/functions: convert options `WithCompressors`, `WithMkfsOptions`, `WithBlobCompression`; `LayerConvertFunc`; and `UpdateManifestPlatform`.

Control flow and state: `LayerConvertFunc` skips non-layers, existing EROFS media types, and non-distributable layers. It uncompresses compressed layers first, reads source labels, converts uncompressed tar content to a temporary EROFS file using `erofsutils.ConvertTarErofs`, writes the EROFS blob to content store, optionally zstd-compresses the EROFS blob while recording uncompressed digest label, commits with labels, and returns a descriptor with EROFS media type and new size/digest. `UpdateManifestPlatform` ensures manifest platform/config `os.features` includes `erofs`, writes a new config, updates manifest GC label, writes a new manifest, and sets descriptor platform.

Dependencies and integration: core content/images, converter helpers, uncompress converter, internal erofs utilities, compression, labels, errdefs, logging, platforms, UUID generation.

Risks: requires external/system EROFS conversion support through `erofsutils`; temp files must be cleaned. Blob compression option currently recognizes string `"zstd"` only. Labels are taken from original compressed desc info, then applied to converted content. Commit with already-exists is tolerated, but writer state and info lookup must still succeed.

Test signals: no direct tests in this subset. Integration should cover compressed/uncompressed input, zstd blob compression, mkfs option defaults, non-distributable skip, existing EROFS skip, temp cleanup, and platform/config feature update.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/images/converter/erofs/erofs.go -->
