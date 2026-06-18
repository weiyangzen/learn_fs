# subset-b-000074 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/os/os_windows_test.go -->
# sources/cloud-native/containerd/pkg/os/os_windows_test.go

## Purpose
Windows-only integration tests for pkg/os path resolution, especially resolving local drive paths, UNC paths, symlinks, VHD volumes, and mounted volumes into stable final paths usable by EvalSymlinks.

## Important APIs, Types, And Functions
getWindowsBuildNumber reads the registry for CurrentBuild; setupVHDVolume creates, attaches, formats, and discovers a VHD volume; mountVolume binds a volume path to a mount point; TestResolvePath drives resolvePath through local, UNC, symlink, and VHD cases.

## Control Flow
The test prepares C: volume identity, temp symlinks, two formatted VHDs, and a volume mount point, then checks resolvePath output and verifies EvalSymlinks of the resolved output remains equivalent case-insensitively.

## State And Persistence
Persists only temporary VHD and mount-point state for the test lifetime and registers cleanups to close handles, detach disks, remove mount points, and delete temp paths.

## Dependencies And Integration Points
Depends on Windows registry APIs, go-winio/vhd, hcsshim computestorage, osversion build gates, and internal Windows path helpers from pkg/os.

## Risks And Edge Cases
High privilege and Windows storage APIs make this environment-sensitive. Build-number handling must match HcsFormatWritableLayerVhd handle expectations before and after 19H1. Cleanup failures can leave attached VHDs or mount points.

## Test Signals
Direct test coverage is TestResolvePath on Windows; it validates local/UNC preservation, symlink expansion, VHD volume path behavior, and compatibility with filepath.EvalSymlinks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/os/os_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/os/testing/fake_os.go -->
# sources/cloud-native/containerd/pkg/os/testing/fake_os.go

## Purpose
Provides a thread-safe fake implementation of pkg/os.OS for tests that need to observe or inject filesystem, mount, symlink, and hostname calls without mutating the host.

## Important APIs, Types, And Functions
FakeOS exposes optional function fields for MkdirAll, RemoveAll, Stat, ResolveSymbolicLink, FollowSymlinkInScope, CopyFile, WriteFile, Mount, Unmount, LookupMount, and Hostname. CalledDetail records call name and arguments. InjectError, InjectErrors, ClearErrors, and GetCalls control and inspect behavior.

## Control Flow
Each fake method records the call, consumes a one-shot injected error for that operation, then delegates to the configured function field or returns a neutral default.

## State And Persistence
Maintains in-memory call history and a map of one-shot errors protected by a mutex. No filesystem persistence occurs unless a test supplies function hooks that perform it.

## Dependencies And Integration Points
Implements github.com/containerd/containerd/v2/pkg/os.OS and uses core/mount.Info in LookupMount. Intended for unit tests across packages that accept the OS interface.

## Risks And Edge Cases
Injected errors are consumed on first use, so tests must be explicit about repeated failures. Default Stat returns nil FileInfo and nil error, which is useful for mocks but can hide assumptions if used carelessly.

## Test Signals
Compile-time interface assertion verifies API coverage. Downstream tests can assert GetCalls ordering and injected-error propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/os/testing/fake_os.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/progress/bar.go -->
# sources/cloud-native/containerd/pkg/progress/bar.go

## Purpose
Implements a simple fmt.Formatter-backed terminal progress bar rendered by the custom %r verb.

## Important APIs, Types, And Functions
Bar is a float64 progress ratio; Format clamps the value to [0,1], honors the left/right reversal flag, chooses a default width of 40, and emits colored plus/minus segments bounded by vertical bars.

## Control Flow
fmt calls Format with the requested rune. The code rejects non-r verbs by panic, computes filled and empty width, inserts ANSI green/reset escape sequences, and writes directly to fmt.State.

## State And Persistence
No persistent state. Output is derived entirely from the receiver and fmt formatting state.

## Dependencies And Integration Points
Depends on bytes, fmt, and escape constants from escape.go. Used by progress displays that rely on terminal ANSI colors.

## Risks And Edge Cases
Panicking on unexpected verbs is intentional but can surprise generic formatting. Width calculations count escape bytes separately to keep visible width stable, but terminal color support is assumed.

## Test Signals
No local test in this subset; coverage is indirect through callers or manual formatting behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/progress/bar.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/progress/doc.go -->
# sources/cloud-native/containerd/pkg/progress/doc.go

## Purpose
Declares the progress package documentation: helpers for displaying human-readable progress information.

## Important APIs, Types, And Functions
No exported API beyond the package comment.

## Control Flow
No runtime control flow.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Ties the package-level documentation to bar, writer, escape, and human-readable unit helpers.

## Risks And Edge Cases
No behavioral risk except stale documentation if package responsibilities change.

## Test Signals
No direct tests needed.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/progress/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/progress/escape.go -->
# sources/cloud-native/containerd/pkg/progress/escape.go

## Purpose
Centralizes ANSI escape sequences used by progress rendering.

## Important APIs, Types, And Functions
Defines escape, reset, red, and green constants; red is currently unused and annotated for lint suppression.

## Control Flow
No control flow.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Consumed by Bar formatting and potentially other progress terminal output.

## Risks And Edge Cases
Assumes ANSI-capable output; callers writing to non-terminal sinks will include raw escape bytes.

## Test Signals
No direct tests; effects are visible through formatted progress output.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/progress/escape.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/progress/humaans.go -->
# sources/cloud-native/containerd/pkg/progress/humaans.go

## Purpose
Provides human-readable byte and byte-per-second formatting for progress displays.

## Important APIs, Types, And Functions
Bytes.String formats base-1024 units with docker/go-units. BytesPerSecond represents a byte rate; NewBytesPerSecond computes bytes divided by duration seconds, and String appends /s.

## Control Flow
Callers wrap raw byte counts or call NewBytesPerSecond after measuring duration; String performs the actual rendering.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Depends on docker/go-units and time. Integrates with progress status output and logging.

## Risks And Edge Cases
NewBytesPerSecond does not guard zero duration, so callers must avoid duration=0 to prevent Inf conversion semantics.

## Test Signals
No local tests; behavior is straightforward unit formatting.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/progress/humaans.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/progress/writer.go -->
# sources/cloud-native/containerd/pkg/progress/writer.go

## Purpose
Implements a buffered terminal writer that clears previously printed progress lines before writing the next screen.

## Important APIs, Types, And Functions
Writer wraps an io.Writer, buffered output, and prior line count. NewWriter, Write, Flush, clearLines, countLines, and stripLine implement refresh behavior.

## Control Flow
Write appends to an internal buffer. Flush clears the previous number of lines, counts visible lines in the new buffer using console width and ANSI-stripped text, writes the buffer, and resets it.

## State And Persistence
State is in-memory only: buffered bytes and last visible line count. It reads console dimensions from os.Stdin at flush time.

## Dependencies And Integration Points
Depends on containerd/console and lazyregexp. Uses escape control sequences for moving up and clearing lines.

## Risks And Edge Cases
If stdin is not a console or width cannot be determined, countLines returns zero, so old output may not clear. stripLine only removes a narrow color-code pattern, not all ANSI sequences.

## Test Signals
No direct tests in this subset; observable through progress UI refresh behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/progress/writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/protobuf/proto/proto.go -->
# sources/cloud-native/containerd/pkg/protobuf/proto/proto.go

## Purpose
Compatibility shim for protobuf migration by exposing Marshal and Unmarshal under containerd pkg/protobuf/proto.

## Important APIs, Types, And Functions
Marshal and Unmarshal delegate to google.golang.org/protobuf/proto for google.Message values.

## Control Flow
Calls are pass-through with no extra validation or transformation.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Used by shim bootstrap, runtime option, and delete response code that imports containerd protobuf helpers instead of google directly.

## Risks And Edge Cases
Only supports the modern protobuf Message interface; callers with legacy gogo values need migration adapters elsewhere.

## Test Signals
Covered indirectly by all code paths that marshal bootstrap and shim responses.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/protobuf/proto/proto.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/protobuf/prototestutil/compare.go -->
# sources/cloud-native/containerd/pkg/protobuf/prototestutil/compare.go

## Purpose
Provides a cmp.Option for tests to compare protobuf messages by semantic proto equality rather than Go struct field equality.

## Important APIs, Types, And Functions
Compare filters values where both sides implement proto.Message and compares them with proto.Equal.

## Control Flow
go-cmp invokes the filter for candidate values and the comparer performs type assertions before calling proto.Equal.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Integrates tests using github.com/google/go-cmp/cmp with google.golang.org/protobuf/proto.

## Risks And Edge Cases
The comparer only applies when both values are proto.Message; mixed or wrapped values fall back to other cmp behavior.

## Test Signals
No direct test here; intended as shared test infrastructure.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/protobuf/prototestutil/compare.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/protobuf/timestamp.go -->
# sources/cloud-native/containerd/pkg/protobuf/timestamp.go

## Purpose
Wraps protobuf timestamp conversion for containerd callers during migration away from older protobuf APIs.

## Important APIs, Types, And Functions
ToTimestamp calls timestamppb.New; FromTimestamp calls AsTime.

## Control Flow
Simple pass-through conversions between time.Time and *timestamppb.Timestamp.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Used by shim delete responses and event envelopes that need protobuf timestamps.

## Risks And Edge Cases
FromTimestamp assumes non-nil input; nil would panic via method call. Callers should validate optional timestamp fields.

## Test Signals
Covered indirectly wherever timestamp fields are serialized or read.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/protobuf/timestamp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/protobuf/types/types.go -->
# sources/cloud-native/containerd/pkg/protobuf/types/types.go

## Purpose
Defines type aliases for common protobuf well-known types to ease imports during protobuf migration.

## Important APIs, Types, And Functions
Aliases Empty, Any, and FieldMask to emptypb.Empty, anypb.Any, and fieldmaskpb.FieldMask.

## Control Flow
No control flow.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Used by shim runtime options and APIs that want stable containerd import paths.

## Risks And Edge Cases
Aliases expose exact upstream types, so upstream API changes propagate directly.

## Test Signals
Compile-time aliasing is the only needed signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/protobuf/types/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/rdt/rdt_linux.go -->
# sources/cloud-native/containerd/pkg/rdt/rdt_linux.go

## Purpose
Linux RDT integration layer that configures Intel resctrl/goresctrl support and maps Kubernetes/container annotations to RDT classes.

## Important APIs, Types, And Functions
IsEnabled reads guarded package state. SetConfig initializes goresctrl once, loads a config file with SetConfigFromFile, and marks RDT enabled. ContainerClassFromAnnotations delegates class selection to goresctrl.

## Control Flow
SetConfig disables RDT first, exits quietly for empty config, performs one-time rdt.Initialize, returns cached initialization errors, applies config, then sets enabled true.

## State And Persistence
Maintains process-global enabled state with RWMutex plus initOnce/initErr for one-time resctrl initialization. External persistence is the kernel resctrl filesystem state written by goresctrl.

## Dependencies And Integration Points
Depends on github.com/intel/goresctrl/pkg/rdt and containerd log. Called from CRI/runtime configuration paths when RDT is enabled.

## Risks And Edge Cases
Initialization is one-shot: a failed first Initialize is cached. Config changes affect global RDT state. Linux-only build excludes no_rdt.

## Test Signals
No direct tests in subset; behavior depends on goresctrl and host resctrl support.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/rdt/rdt_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/rdt/rdt_nonlinux.go -->
# sources/cloud-native/containerd/pkg/rdt/rdt_nonlinux.go

## Purpose
Non-Linux or no_rdt stub for RDT support.

## Important APIs, Types, And Functions
IsEnabled returns false, SetConfig is a no-op, and ContainerClassFromAnnotations returns empty class and nil error.

## Control Flow
All calls return immediately.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Maintains cross-platform API compatibility for packages that call rdt unconditionally.

## Risks And Edge Cases
Silent no-op behavior can hide configuration mistakes on unsupported builds unless higher layers report platform support.

## Test Signals
Build tags provide compile-time platform coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/rdt/rdt_nonlinux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/reference/reference.go -->
# sources/cloud-native/containerd/pkg/reference/reference.go

## Purpose
Parses schema-less containerd reference specifications into locator/object components while keeping digest and hostname helpers.

## Important APIs, Types, And Functions
Spec contains Locator and Object. Parse rejects explicit schemes, uses url.Parse with a dummy scheme, requires a host, splits object at the first path colon or at-sign, and normalizes with path.Join. Hostname, Digest, and String expose derived views.

## Control Flow
Parse builds a dummy URL, validates scheme/host, cuts object from the path with lazy regexp, strips leading colon from tag objects, and returns a normalized Spec. String reconstructs locator plus :object or @digest-only object.

## State And Persistence
No persistent state; splitRe is a lazily compiled package regexp.

## Dependencies And Integration Points
Depends on net/url, path, strings, lazyregexp, and opencontainers/go-digest. Used by remote/reference handling that accepts looser-than-Docker references.

## Risks And Edge Cases
It intentionally permits partial or invalid digest strings in Object; validation belongs to callers. path.Join cleans paths and may normalize duplicate separators.

## Test Signals
reference_test.go covers tags, digest-only refs, host ports, missing hostname, subdomains, punycode, and explicit-scheme rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/reference/reference.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/reference/reference_test.go -->
# sources/cloud-native/containerd/pkg/reference/reference_test.go

## Purpose
Table-driven tests for the schema-less reference parser and Spec helper methods.

## Important APIs, Types, And Functions
TestReferenceParser defines cases covering Normalized, Digest, Hostname, Expected Spec, and expected errors.

## Control Flow
Each case calls Parse, verifies exact error identity, compares returned Spec, applies default normalization, and checks String, Digest, and Hostname.

## State And Persistence
No persistent state; tests are pure.

## Dependencies And Integration Points
Depends on opencontainers/go-digest and testing. Exercises reference.go directly.

## Risks And Edge Cases
The table documents intentionally accepted inputs such as missing object and partial digest; future stricter parsing must update expectations deliberately.

## Test Signals
Strong direct unit coverage for all exported behavior in reference.go.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/reference/reference_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/rootfs/apply.go -->
# sources/cloud-native/containerd/pkg/rootfs/apply.go

## Purpose
Applies OCI image layers into a snapshotter and returns the resulting chain ID digest.

## Important APIs, Types, And Functions
Layer carries Diff and Blob descriptors. ApplyLayers, ApplyLayersWithOpts, ApplyLayer, ApplyLayerWithOpts, applyLayers, and uniquePart implement multi-layer and single-layer unpack.

## Control Flow
Top-level calls compute chain IDs, stat existing snapshots, recursively prepare parents as needed, create a unique unpack key, call diff.Applier.Apply, verify computed diff digest, and commit the snapshot under the chain ID.

## State And Persistence
Persistent state is snapshotter metadata and filesystem content created by Prepare/Commit. Temporary active snapshots are removed on error. uniquePart adds time plus random bytes to reduce key collisions.

## Dependencies And Integration Points
Integrates core/diff Applier, snapshots.Snapshotter, mount.Mounts, errdefs, image-spec identity. Used by image unpack/rootfs setup flows.

## Risks And Edge Cases
Concurrent unpack relies on AlreadyExists handling and unique keys. Cleanup is best-effort. Diff digest mismatch aborts after extraction. rand.Read errors are ignored, reducing but not eliminating uniqueness.

## Test Signals
No direct tests here; exercised by unpack and content integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/rootfs/apply.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/rootfs/diff.go -->
# sources/cloud-native/containerd/pkg/rootfs/diff.go

## Purpose
Creates an OCI layer diff descriptor by comparing a snapshot with its parent.

## Important APIs, Types, And Functions
CreateDiff stats a snapshot, creates a parent view, chooses active mounts or an upper view, and calls diff.Comparer.Compare.

## Control Flow
The function always prepares a temporary lower parent view, then either mounts an active upper snapshot or creates a temporary readonly view for committed snapshots before comparing.

## State And Persistence
Temporary snapshot views are removed via internal cleanup. The returned descriptor is persisted by whatever content writer the comparer uses.

## Dependencies And Integration Points
Depends on snapshots.Snapshotter, diff.Comparer, mount.Mount, and cleanup helpers. Used by image export/commit workflows.

## Risks And Edge Cases
Assumes the snapshot has a valid Parent; root snapshots need snapshotter behavior that tolerates empty parent. Cleanup ignores remove errors through cleanup.Do.

## Test Signals
Covered indirectly by diff/export integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/rootfs/diff.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/schedcore/prctl_linux.go -->
# sources/cloud-native/containerd/pkg/schedcore/prctl_linux.go

## Purpose
Linux wrapper for PR_SCHED_CORE operations used to create or join scheduler core-scheduling domains.

## Important APIs, Types, And Functions
PidType constants map to pid, thread-group, and process-group scopes. Create and ShareFrom call unix.Prctl with PR_SCHED_CORE_CREATE or SHARE_FROM.

## Control Flow
Callers choose a scope, then the wrapper forwards raw prctl arguments to the kernel.

## State And Persistence
No package state; changes occur in kernel scheduler state for target processes.

## Dependencies And Integration Points
Depends on x/sys/unix. Used by runtime code that wants core scheduling isolation or sharing.

## Risks And Edge Cases
Requires kernel support and privileges appropriate to PR_SCHED_CORE; errors are passed through without interpretation.

## Test Signals
No local tests; platform/kernel behavior is expected to be integration-tested.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/schedcore/prctl_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/seccomp/seccomp.go -->
# sources/cloud-native/containerd/pkg/seccomp/seccomp.go

## Purpose
Public seccomp capability probe facade.

## Important APIs, Types, And Functions
IsEnabled delegates to platform-specific isEnabled implementation.

## Control Flow
Single call path with platform dispatch by build tags.

## State And Persistence
No direct state here; Linux implementation caches probe result.

## Dependencies And Integration Points
Used by runtime feature detection code that needs cross-platform seccomp availability.

## Risks And Edge Cases
The meaning is kernel support for seccomp/filter, not whether a profile is active.

## Test Signals
Covered indirectly through platform implementations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/seccomp/seccomp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/seccomp/seccomp_linux.go -->
# sources/cloud-native/containerd/pkg/seccomp/seccomp_linux.go

## Purpose
Linux seccomp support detection based on prctl error behavior.

## Important APIs, Types, And Functions
isEnabled uses sync.Once and unix.Prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, nil) and treats EINVAL as unsupported and any other error as supported.

## Control Flow
The first call performs the kernel probe, stores enabled, and all later calls return the cached value.

## State And Persistence
Process-global cached boolean guarded by sync.Once; no filesystem persistence.

## Dependencies And Integration Points
Depends on x/sys/unix. Mirrors runc-style capability detection.

## Risks And Edge Cases
Relies on Linux prctl error semantics: EACCES/EFAULT imply configured support. A future kernel semantic change could misclassify.

## Test Signals
No direct tests; behavior is kernel-specific.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/seccomp/seccomp_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/seccomp/seccomp_unsupported.go -->
# sources/cloud-native/containerd/pkg/seccomp/seccomp_unsupported.go

## Purpose
Non-Linux seccomp support stub.

## Important APIs, Types, And Functions
isEnabled always returns false.

## Control Flow
No control flow beyond return.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Preserves seccomp package API on unsupported platforms.

## Risks And Edge Cases
Silent false may need higher-level user-facing diagnostics for seccomp-required configs.

## Test Signals
Build-tag coverage only.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/seccomp/seccomp_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/compat.go -->
# sources/cloud-native/containerd/pkg/shim/compat.go

## Purpose
Compatibility adapter from pre-2.3 shim launch inputs to the new bootstrap protocol.

## Important APIs, Types, And Functions
readBootstrapParamsFromDeprecatedFields fills BootstrapParams from parsed flags, legacy env vars, publish binary, debug flag, and optionally runc options unmarshaled from stdin.

## Control Flow
The start path in shim.go first tries new proto input and falls back here when input is empty or not a BootstrapParams proto.

## State And Persistence
No persistent state; it reads process environment and adds extensions to an in-memory BootstrapParams.

## Dependencies And Integration Points
Integrates bootapi, runc options, ReadRuntimeOptions, and shim env constants.

## Risks And Edge Cases
Compatibility path is intentionally permissive until the new API is stable; malformed runtime options are ignored unless adding a successfully parsed extension fails.

## Test Signals
Covered indirectly by shim start compatibility and runtime option tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/compat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/deprecated.go -->
# sources/cloud-native/containerd/pkg/shim/deprecated.go

## Purpose
Deprecated shim Manager API wrapper retained for older shim implementations.

## Important APIs, Types, And Functions
StartOpts, BootstrapParams, Manager, managerShim, and Run bridge the old Manager interface to the new Shim interface.

## Control Flow
Run wraps a Manager in managerShim and calls the shared run path. managerShim.Start maps BootstrapParams to StartOpts and maps the old result back to bootapi.BootstrapResult.

## State And Persistence
No state beyond wrapped manager references.

## Dependencies And Integration Points
Integrates legacy shim binaries with bootapi-based RunShim.

## Risks And Edge Cases
Deprecated fields and protocol strings must remain compatible until callers are migrated.

## Test Signals
Indirectly covered by older shim integration paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/deprecated.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/publisher.go -->
# sources/cloud-native/containerd/pkg/shim/publisher.go

## Purpose
Remote event publisher used by shims to forward container/task events to containerd over ttrpc.

## Important APIs, Types, And Functions
NewPublisher, RemoteEventsPublisher, Publish, Close, Done, processQueue, queue, and forwardRequest manage event forwarding and retry.

## Control Flow
Publish requires namespace, marshals the event through typeurl, builds an envelope with timestamp, tries Forward immediately, and requeues on failure. processQueue retries delayed items up to maxRequeue; forwardRequest reconnects on ttrpc.ErrClosed.

## State And Persistence
Maintains client connection state and an in-memory retry queue; no durable event persistence, so events can be lost after retry exhaustion or process exit.

## Dependencies And Integration Points
Depends on ttrpcutil.Client, ttrpc events service, namespaces, protobuf timestamps, typeurl, and containerd events interfaces.

## Risks And Edge Cases
Queue send occurs in goroutines and can block if the queue fills. Context timeouts are five seconds per forward. Events are dropped after maxRequeue.

## Test Signals
No direct tests in subset; exercised by shim event paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/publisher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim.go -->
# sources/cloud-native/containerd/pkg/shim/shim.go

## Purpose
Main shim binary bootstrap and server runner for the v2/v3 shim lifecycle.

## Important APIs, Types, And Functions
Defines Publisher, StopStatus, Shim, Opts, Config, TTRPC service/interceptor interfaces, parseFlags, setRuntime, setLogger, RunShim, runInfo, run, serve, dumpStacks, and setupPprof.

## Control Flow
run parses flags, handles version/info/delete/start actions, builds namespace and shutdown contexts, falls back from new bootstrap proto to deprecated fields, starts managers, registers plugins, builds ttrpc server/interceptors, serves until signal/reaper shutdown, and cleans sockets.

## State And Persistence
Process-global flags are parsed into package vars. Runtime tuning changes GOGC and optionally GOMAXPROCS. Plugins get state dirs under bundle path. Socket-dir symlink/address files support cleanup.

## Dependencies And Integration Points
Integrates boot/task APIs, plugin registry, namespaces, shutdown service, protobuf helpers, event publisher, ttrpc server, platform socket/signal helpers, and optional pprof plugin.

## Risks And Edge Cases
Complex lifecycle risks include partial bootstrap reads, logger FIFO setup failure, missing ttrpc services, plugin init failures, signal/reaper races, socket leaks after crashes, and Windows named-pipe readiness timing.

## Test Signals
shim_test.go checks runtime GOMAXPROCS and context options; other shim util tests cover sockets/interceptors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim_darwin.go -->
# sources/cloud-native/containerd/pkg/shim/shim_darwin.go

## Purpose
Darwin shim server platform shim.

## Important APIs, Types, And Functions
newServer returns ttrpc.NewServer; subreaper is a no-op.

## Control Flow
Used by shared run when building/serving ttrpc on Darwin.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Depends on containerd/ttrpc and platform build tags.

## Risks And Edge Cases
No same-user Unix socket handshaker and no subreaper behavior compared with Linux.

## Test Signals
Indirect platform coverage only.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim_freebsd.go -->
# sources/cloud-native/containerd/pkg/shim/shim_freebsd.go

## Purpose
FreeBSD shim server platform shim.

## Important APIs, Types, And Functions
newServer returns ttrpc.NewServer; subreaper is a no-op.

## Control Flow
Used by shared shim run path on FreeBSD.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Depends on containerd/ttrpc.

## Risks And Edge Cases
Child reaping behavior lacks Linux PR_SET_CHILD_SUBREAPER; lifecycle assumptions differ by platform.

## Test Signals
Indirect platform coverage only.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim_linux.go -->
# sources/cloud-native/containerd/pkg/shim/shim_linux.go

## Purpose
Linux shim server platform behavior.

## Important APIs, Types, And Functions
newServer appends UnixSocketRequireSameUser handshaker; subreaper calls reaper.SetSubreaper(1).

## Control Flow
Shared run calls subreaper before serving unless disabled and creates a ttrpc server with same-user socket authentication.

## State And Persistence
Kernel subreaper flag is process state; no filesystem persistence.

## Dependencies And Integration Points
Depends on pkg/sys/reaper and ttrpc.

## Risks And Edge Cases
Subreaper setup requires prctl support; same-user handshake affects clients over Unix sockets.

## Test Signals
Indirectly covered through shim lifecycle and reaper tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim_test.go -->
# sources/cloud-native/containerd/pkg/shim/shim_test.go

## Purpose
Unit tests for shim runtime tuning and context option storage.

## Important APIs, Types, And Functions
Tests setRuntime behavior with and without GOMAXPROCS and OptsKey context value retrieval.

## Control Flow
Each test mutates env/context, invokes helper, and asserts GOMAXPROCS or Opts.Debug.

## State And Persistence
Mutates process GOMAXPROCS and restores in the empty-env test; no persistence.

## Dependencies And Integration Points
Depends on runtime and testing. Exercises shim.go helpers.

## Risks And Edge Cases
The non-empty GOMAXPROCS test assumes runtime.NumCPU matches the runtime-set default in that environment.

## Test Signals
Direct coverage for setRuntime and Opts context use.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim_unix.go -->
# sources/cloud-native/containerd/pkg/shim/shim_unix.go

## Purpose
Unix signal, listener, reaping, logging, and pipe readiness helpers for shim server.

## Important APIs, Types, And Functions
setupSignals, setupDumpStacks, serveListener, reap, handleExitSignals, openLog, and awaitPipeReady implement Unix behavior.

## Control Flow
Signals are registered for TERM/INT/PIPE and optionally CHLD. serveListener uses inherited fd 3 or an explicit Unix socket path. reap consumes SIGCHLD and calls reaper.Reap. openLog opens the log FIFO on stderr fd.

## State And Persistence
Registers process signal handlers and opens listeners/FIFOs; no durable state by itself.

## Dependencies And Integration Points
Integrates pkg/sys/reaper, containerd/fifo, x/sys/unix, and shared shim server logic.

## Risks And Edge Cases
Unix socket path limit is enforced only for explicit paths. Signal channels are shared with exit handling, so short actions intentionally ignore exit signals in reap.

## Test Signals
Socket behavior covered by util_unix_test and abstract socket tests; reaping covered by reaper package.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim_windows.go -->
# sources/cloud-native/containerd/pkg/shim/shim_windows.go

## Purpose
Windows stubs and named-pipe readiness logic for shim server support.

## Important APIs, Types, And Functions
Most server/signal/log/subreaper helpers return ErrNotImplemented; awaitPipeReady polls winio.DialPipe for up to five seconds.

## Control Flow
The start helper calls awaitPipeReady after manager.Start returns an address so the parent does not consume the bootstrap result before the named pipe is connectable.

## State And Persistence
No persistent state; only timed polling.

## Dependencies And Integration Points
Depends on go-winio, errdefs, ttrpc types, and shared shim run path.

## Risks And Edge Cases
Long-running Windows serving is not implemented in these helpers, but readiness polling must tolerate pipe-not-found and deadline/busy states without blocking containerd indefinitely.

## Test Signals
No direct tests in subset; behavior is platform integration-driven.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/shim_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/util.go -->
# sources/cloud-native/containerd/pkg/shim/util.go

## Purpose
Daemon-side and shared shim utility functions for launching shim binaries, resolving binary names, reading address/options files, and composing ttrpc interceptors.

## Important APIs, Types, And Functions
CommandConfig, Command, BinaryName, BinaryPath, Connect, WritePidFile, ReadAddress, ReadRuntimeOptions, and chainUnaryServerInterceptors are key APIs.

## Control Flow
Command builds legacy flags/env for all shims and sends either legacy options for v1 shim names or new BootstrapParams on stdin for start. Utilities atomically write pid files, read address files, unmarshal Any runtime options, and wrap interceptors from first to last.

## State And Persistence
Writes pid files atomically and reads address files. Command mutates only exec.Cmd fields. Runtime options are read fully from an io.Reader.

## Dependencies And Integration Points
Integrates namespaces, bootapi, protobuf/typeurl, atomicfile, errdefs, log, ttrpc, and version metadata.

## Risks And Edge Cases
Command has compatibility branches based on binary basename; incorrect Action is rejected. ReadRuntimeOptions requires registered typeurl types. Interceptor chaining order is subtle and tested.

## Test Signals
util_test.go covers interceptor order, context propagation, and unmarshaler wrapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/util_abstract_test.go -->
# sources/cloud-native/containerd/pkg/shim/util_abstract_test.go

## Purpose
Non-Windows, non-Darwin test for abstract Unix socket support.

## Important APIs, Types, And Functions
TestNewSocketAbstract calls NewSocket on an abstract-style address and dials the translated Unix path.

## Control Flow
Creates listener, dials it, closes connection and listener via cleanup.

## State And Persistence
No filesystem state for abstract sockets.

## Dependencies And Integration Points
Exercises util_unix.go socket path parsing and NewSocket behavior.

## Risks And Edge Cases
Skipped on Darwin/Windows because abstract sockets are not available there.

## Test Signals
Direct coverage for abstract socket creation/connectivity.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/util_abstract_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/util_test.go -->
# sources/cloud-native/containerd/pkg/shim/util_test.go

## Purpose
Tests ttrpc unary interceptor chaining helper.

## Important APIs, Types, And Functions
TestChainUnaryServerInterceptors constructs two interceptors and a method, validating context propagation, info propagation, and unmarshal wrapping order.

## Control Flow
The chained interceptor calls first, then second, then method; each layer checks expected context values and numeric transformations.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Exercises chainUnaryServerInterceptors in util.go and ttrpc function signatures.

## Risks And Edge Cases
A regression in order or unmarshal wrapping would change expected numeric results and fail the test.

## Test Signals
Direct high-signal unit test for interceptor composition.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/util_unix.go -->
# sources/cloud-native/containerd/pkg/shim/util_unix.go

## Purpose
Unix shim socket and dial utility implementation.

## Important APIs, Types, And Functions
getSysProcAttr, AdjustOOMScore, SocketAddress, CreateSocketAddress, AnonDialer, AnonReconnectDialer, NewSocket, RemoveSocket, SocketEaddrinuse, CanConnect, vsock/hybrid-vsock dialers, writeSocketDir, and cleanupSockets are key APIs.

## Control Flow
Addresses are parsed as unix, vsock, hybrid-vsock, or abstract Unix. Socket addresses are hashed from namespace/socketPath/id/debug. NewSocket creates directories and chmods filesystem sockets. cleanup removes recorded and derived sockets.

## State And Persistence
Creates socket files, socket directory symlink s, and may adjust kernel OOM score. Uses hashed socket names under state dir to avoid path length issues.

## Dependencies And Integration Points
Depends on defaults, namespaces, pkg/sys OOM helpers, mdlayher/vsock, net, and filesystem APIs. Used by daemon/shim connection setup.

## Risks And Edge Cases
Abstract socket detection treats unprefixed addresses as abstract. Hybrid-vsock handshake retries EOF until timeout. cleanup falls back to default state dir if symlink is missing.

## Test Signals
util_unix_test and util_abstract_test cover filesystem and abstract sockets; OOM behavior is covered in pkg/sys tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/util_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/util_unix_test.go -->
# sources/cloud-native/containerd/pkg/shim/util_unix_test.go

## Purpose
Unix socket creation tests for shim utilities.

## Important APIs, Types, And Functions
TestNewSocket verifies nested-directory and existing-directory filesystem socket cases.

## Control Flow
Each subtest creates a temp dir, calls NewSocket with unix:// path, dials the socket, and closes resources.

## State And Persistence
Creates temporary directories and socket files cleaned at test end.

## Dependencies And Integration Points
Exercises NewSocket and socket.path from util_unix.go.

## Risks And Edge Cases
Uses /tmp explicitly for temp dirs; platform build tag excludes Windows.

## Test Signals
Direct coverage for directory creation and socket connectivity.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/util_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/util_windows.go -->
# sources/cloud-native/containerd/pkg/shim/util_windows.go

## Purpose
Windows shim utility implementation for named-pipe dialing and compatibility no-ops.

## Important APIs, Types, And Functions
Defines shimBinaryFormat .exe, nil getSysProcAttr, AnonDialer, AnonReconnectDialer, RemoveSocket, writeSocketDir, and cleanupSockets.

## Control Flow
AnonDialer retries pipe-not-found for up to five seconds for newly starting shims. AnonReconnectDialer fails fast on missing pipes for daemon restart scanning. cleanup reads address but RemoveSocket is a no-op.

## State And Persistence
No filesystem socket state is removed. Named pipe connection state is external to the process.

## Dependencies And Integration Points
Depends on go-winio and Windows build tags. Used by shim Command/Connect paths on Windows.

## Risks And Edge Cases
Retry timing is tuned around Windows SCM startup deadlines and shim startup races. RemoveSocket being no-op means pipe cleanup is owned elsewhere.

## Test Signals
No local tests; behavior is integration/platform-specific.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/util_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shutdown/shutdown.go -->
# sources/cloud-native/containerd/pkg/shutdown/shutdown.go

## Purpose
Context-like shutdown service with asynchronous callbacks and error propagation.

## Important APIs, Types, And Functions
Service interface, ErrShutdown, WithShutdown, shutdownService.Shutdown, Done, Err, and RegisterCallback are exported or central.

## Control Flow
WithShutdown returns a context backed by shutdownService. Shutdown marks one-time state, runs callbacks concurrently under a 30-second timeout via errgroup, stores first error or ErrShutdown, and closes doneC.

## State And Persistence
Keeps callback list, shutdown flag, terminal error, and done channel in memory under a mutex. No persistence.

## Dependencies And Integration Points
Used by shim server plugins to coordinate graceful shutdown and plugin callbacks.

## Risks And Edge Cases
Parent context cancellation does not cancel the shutdown context by design. RegisterCallback after Shutdown appends but will not run in the current implementation. Err returns nil until callbacks finish.

## Test Signals
No direct tests in subset; shim run path relies on Done/Err semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shutdown/shutdown.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/snapshotters/annotations.go -->
# sources/cloud-native/containerd/pkg/snapshotters/annotations.go

## Purpose
Adds image reference, manifest digest, layer digest, and remaining-layer-list annotations to layer descriptors during image handling for remote snapshotters.

## Important APIs, Types, And Functions
Constants TargetRefLabel, TargetManifestDigestLabel, TargetLayerDigestLabel, TargetImageLayersLabel; AppendInfoHandlerWrapper; getLayers.

## Control Flow
The wrapper calls the inner handler, then when the descriptor is a manifest it annotates layer children with ref, own digest, manifest digest, and a comma-separated suffix of layer digests capped by label validation.

## State And Persistence
Annotations are in-memory descriptor metadata propagated to snapshotters as labels; no direct persistence here.

## Dependencies And Integration Points
Depends on core/images media-type helpers, labels.Validate, log, and OCI descriptors. Important for remote/lazy snapshotter pull optimization.

## Risks And Edge Cases
Layer list truncation is validation-driven and silently logged at debug. The label names retain cri prefix for compatibility despite non-CRI use.

## Test Signals
annotations_test.go validates layer-list truncation behavior under a synthetic size limit.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/snapshotters/annotations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/snapshotters/annotations_test.go -->
# sources/cloud-native/containerd/pkg/snapshotters/annotations_test.go

## Purpose
Unit tests for snapshotter image-layers annotation truncation.

## Important APIs, Types, And Functions
TestImageLayersLabel builds sample descriptors and a validator with a max key+value length.

## Control Flow
The test calls getLayers for two and five layer cases and checks how many comma-separated digests fit before validation fails.

## State And Persistence
Pure in-memory test state.

## Dependencies And Integration Points
Exercises annotations.go getLayers and validation cutoff behavior.

## Risks And Edge Cases
Counting strings.Split on an empty result would be misleading, but test inputs always include layers and expect non-empty output.

## Test Signals
Direct coverage for avoiding oversized labels.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/snapshotters/annotations_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/stdio/platform.go -->
# sources/cloud-native/containerd/pkg/stdio/platform.go

## Purpose
Defines platform-specific stdio/console behavior contract.

## Important APIs, Types, And Functions
Platform interface requires CopyConsole, ShutdownConsole, and Close.

## Control Flow
No implementation in this file; concrete platform packages implement the interface.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Used by task/shim stdio code to abstract console copying and teardown.

## Risks And Edge Cases
Interface stability matters across platform implementations.

## Test Signals
Compile-time implementation checks are expected elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/stdio/platform.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/stdio/stdio.go -->
# sources/cloud-native/containerd/pkg/stdio/stdio.go

## Purpose
Small value type describing process stdio FIFO paths and terminal mode.

## Important APIs, Types, And Functions
Stdio has Stdin, Stdout, Stderr, Terminal; IsNull reports whether all three paths are empty.

## Control Flow
No control flow beyond IsNull.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Used by task/process creation and shim IO setup.

## Risks And Edge Cases
Terminal can be true even when paths are empty; IsNull only checks path fields.

## Test Signals
No direct tests in subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/stdio/stdio.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/eintr_unix.go -->
# sources/cloud-native/containerd/pkg/sys/eintr_unix.go

## Purpose
Unix helper to retry syscalls interrupted by signals.

## Important APIs, Types, And Functions
IgnoringEINTR loops a function until the returned error is not unix.EINTR.

## Control Flow
Callers pass a syscall closure; EINTR is swallowed and retried indefinitely.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Used by pidfdWaitid and checkPidFD waitid paths; copied from Go runtime behavior.

## Risks And Edge Cases
A closure that always returns EINTR will loop forever. Only exact unix.EINTR is retried.

## Test Signals
Covered indirectly by pidfd/unshare paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/eintr_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/filesys_unix.go -->
# sources/cloud-native/containerd/pkg/sys/filesys_unix.go

## Purpose
Unix filesystem helper wrapper for ACL-aware mkdir API compatibility.

## Important APIs, Types, And Functions
MkdirAllWithACL delegates to os.MkdirAll.

## Control Flow
Single pass-through call.

## State And Persistence
Creates directories according to os.MkdirAll semantics.

## Dependencies And Integration Points
Keeps API parity with Windows ACL implementation.

## Risks And Edge Cases
Does not apply ACLs on Unix; callers must not assume Windows-style ACL behavior cross-platform.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/filesys_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/filesys_windows.go -->
# sources/cloud-native/containerd/pkg/sys/filesys_windows.go

## Purpose
Windows directory creation helpers that understand volume paths and optional LocalSystem/Administrators ACLs.

## Important APIs, Types, And Functions
SddlAdministratorsLocalSystem, MkdirAllWithACL, MkdirAll, mkdirall, mkdirWithACL, fixRootDirectory, and makeSecurityAttributes.

## Control Flow
MkdirAllWithACL builds security attributes from SDDL, then mkdirall recursively creates parents unless the path is a volume GUID path. mkdirWithACL uses CreateDirectory when ACL attributes are supplied.

## State And Persistence
Creates directories and security descriptors on disk. Volume GUID paths are treated as already existing roots.

## Dependencies And Integration Points
Depends on x/sys/windows, lazyregexp, syscall, unsafe. Used by Windows content/root/state setup code.

## Risks And Edge Cases
Code mirrors os.MkdirAll and must track compatibility. Incorrect root fixing for extended drive paths can break recursive creation. ACL applies inheritance to child objects.

## Test Signals
No local tests in subset; Windows integration paths cover it indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/filesys_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/namespace_linux.go -->
# sources/cloud-native/containerd/pkg/sys/namespace_linux.go

## Purpose
Linux helper for retrieving the owning user namespace file descriptor for another namespace fd.

## Important APIs, Types, And Functions
GetUsernsForNamespace performs ioctl NS_GET_USERNS and wraps the returned fd as *os.File.

## Control Flow
Calls raw SYS_IOCTL on the provided fd and returns an os.File named under /proc/<pid>/fd/<fd>.

## State And Persistence
Returns a live fd the caller must close; no persistent state.

## Dependencies And Integration Points
Used by namespace ownership tests and code that needs userns relationships. Depends on x/sys/unix and syscall.

## Risks And Edge Cases
Requires Linux kernel support for ioctl_ns. Returned fd leaks if callers forget Close.

## Test Signals
namespace_linux_test.go validates netns-to-userns and parent userns relationships under root/kernel gates.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/namespace_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/namespace_linux_test.go -->
# sources/cloud-native/containerd/pkg/sys/namespace_linux_test.go

## Purpose
Root-only Linux tests for GetUsernsForNamespace.

## Important APIs, Types, And Functions
TestGetUsernsForNamespace plus getInode helper.

## Control Flow
The test creates a bind-mounted netns from a child process created by UnshareAfterEnterUserns, then asks the kernel for its owning userns and that userns parent.

## State And Persistence
Creates temp namespace bind mount and unmounts it with continuity testutil. Opens namespace fds that are closed by defer.

## Dependencies And Integration Points
Depends on kernel version >=4.9, root, unix.Mount, and UnshareAfterEnterUserns.

## Risks And Edge Cases
Environment-sensitive because it needs root, kernel support, and namespace operations.

## Test Signals
Directly verifies inode equality against /proc namespace files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/namespace_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/oom_linux.go -->
# sources/cloud-native/containerd/pkg/sys/oom_linux.go

## Purpose
Linux OOM score adjustment utilities for processes.

## Important APIs, Types, And Functions
OOMScoreAdjMin/Max, AdjustOOMScore, SetOOMScore, GetOOMScoreAdj, and runningPrivileged.

## Control Flow
AdjustOOMScore clips input and calls SetOOMScore. SetOOMScore validates range, writes /proc/<pid>/oom_score_adj, and ignores permission errors for unprivileged/userns cases. GetOOMScoreAdj reads and parses the file.

## State And Persistence
Persists kernel OOM adjustment for target process through procfs.

## Dependencies And Integration Points
Used by shim AdjustOOMScore and runtime process setup. Depends on moby/sys/userns and x/sys/unix.

## Risks And Edge Cases
Ignoring permission errors for negative scores in unprivileged contexts preserves compatibility but can hide failed hardening. GetOOMScoreAdj cannot distinguish unset from zero.

## Test Signals
oom_linux_test.go covers positive, negative privileged, bounds, and skipped unprivileged behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/oom_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/oom_linux_test.go -->
# sources/cloud-native/containerd/pkg/sys/oom_linux_test.go

## Purpose
Tests Linux OOM score helpers.

## Important APIs, Types, And Functions
Tests SetOOMScore positive/negative, boundaries, adjustOom helper, and waitForPid.

## Control Flow
Tests spawn a sleep process, read initial score, set requested score, and read it back. Negative unprivileged test is currently skipped due CI instability.

## State And Persistence
Creates child processes killed by defer and mutates their procfs oom_score_adj.

## Dependencies And Integration Points
Depends on root/userns status and sleep binary.

## Risks And Edge Cases
Some cases are environment-gated; a process with OOMScoreAdjMin limits lower-score tests.

## Test Signals
Direct coverage for range validation and procfs write/read behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/oom_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/oom_unsupported.go -->
# sources/cloud-native/containerd/pkg/sys/oom_unsupported.go

## Purpose
Non-Linux OOM score stubs.

## Important APIs, Types, And Functions
Defines OOMScoreMaxKillable/OOMScoreAdjMax as zero and no-op AdjustOOMScore, SetOOMScore, GetOOMScoreAdj.

## Control Flow
All calls return success or zero immediately.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Maintains cross-platform compilation for callers that adjust OOM scores on Linux.

## Risks And Edge Cases
Silent success can mask unsupported behavior if caller expects enforcement.

## Test Signals
Build-tag coverage only.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/oom_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/pidfd_linux.go -->
# sources/cloud-native/containerd/pkg/sys/pidfd_linux.go

## Purpose
Linux pidfd support probe used before pidfd-based namespace helpers.

## Important APIs, Types, And Functions
SupportsPidFD caches checkPidFD result. checkPidFD tests pidfd_open, pidfd_send_signal, and waitid(P_PIDFD) behavior.

## Control Flow
First call opens a pidfd for current process, sends signal 0, calls waitid expecting ECHILD, then marks supported; errors are logged and cached as false.

## State And Persistence
Process-global support boolean cached with sync.Once; no persistence.

## Dependencies And Integration Points
Used by UnshareAfterEnterUserns before relying on CLONE_PIDFD/P_PIDFD.

## Risks And Edge Cases
One-time negative cache means transient syscall restrictions persist for process lifetime. Logs at error level on unsupported kernels.

## Test Signals
Indirect coverage through unshare tests on kernel >=5.10.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/pidfd_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/reaper/reaper_unix.go -->
# sources/cloud-native/containerd/pkg/sys/reaper/reaper_unix.go

## Purpose
Unix process reaper and subscription monitor for child exit notifications.

## Important APIs, Types, And Functions
ErrNoSuchProcess, Reap, Default Monitor, Monitor.Start, StartLocked, Wait, WaitTimeout, Subscribe, Unsubscribe, notify, reap, and exitStatus.

## Control Flow
SIGCHLD handlers call Reap, which wait4-reaps all children and notifies subscribers. Wait consumes matching exit events then calls cmd.Wait and unsubscribes. notify retries subscriber sends with short timeouts until all receive.

## State And Persistence
Maintains in-memory subscriber map and per-subscriber channels. Reaps kernel child process state.

## Dependencies And Integration Points
Used by shim signal loop and command execution that needs subreaper-style wait semantics. Depends on go-runc Exit and x/sys/unix.

## Risks And Edge Cases
Slow or abandoned subscribers can make notify spin until delivery. WaitTimeout kills only the command pid. Correct use requires Reap to be called on SIGCHLD.

## Test Signals
Indirectly covered by shim/reaper integration; no local test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/reaper/reaper_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/reaper/reaper_utils_linux.go -->
# sources/cloud-native/containerd/pkg/sys/reaper/reaper_utils_linux.go

## Purpose
Linux prctl helpers for child subreaper state.

## Important APIs, Types, And Functions
SetSubreaper sets PR_SET_CHILD_SUBREAPER; GetSubreaper reads PR_GET_CHILD_SUBREAPER.

## Control Flow
Thin wrappers around unix.Prctl.

## State And Persistence
Mutates/reads process kernel subreaper flag.

## Dependencies And Integration Points
Used by shim_linux.go.

## Risks And Edge Cases
Requires Linux prctl support; unsafe pointer is used for GetSubreaper output.

## Test Signals
No direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/reaper/reaper_utils_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/socket_unix.go -->
# sources/cloud-native/containerd/pkg/sys/socket_unix.go

## Purpose
Unix local listener helpers with path length, directory ownership, chmod, and stale socket unlink handling.

## Important APIs, Types, And Functions
CreateUnixSocket, GetLocalListener, and mkdirAs.

## Control Flow
CreateUnixSocket checks 104-byte path limit, creates parent dir, unlinks stale socket, and listens. GetLocalListener creates/chowns parent dir, creates socket, chmods and chowns socket.

## State And Persistence
Creates directories and Unix socket filesystem entries.

## Dependencies And Integration Points
Used by daemon service listeners and platform socket setup. Depends on x/sys/unix.

## Risks And Edge Cases
mkdirAs returns existing stat errors directly; ownership changes require privileges. Path length limit is conservative for BSDs.

## Test Signals
No direct tests in subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/socket_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/socket_windows.go -->
# sources/cloud-native/containerd/pkg/sys/socket_windows.go

## Purpose
Windows local listener helper backed by named pipes.

## Important APIs, Types, And Functions
GetLocalListener calls winio.ListenPipe and ignores uid/gid parameters.

## Control Flow
Single pass-through to Windows named pipe listener creation.

## State And Persistence
Creates a named pipe endpoint managed by Windows.

## Dependencies And Integration Points
Used by daemon service listener setup on Windows.

## Risks And Edge Cases
ACL/ownership are not applied here; security depends on winio defaults or caller path configuration.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/socket_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/unshare_linux.go -->
# sources/cloud-native/containerd/pkg/sys/unshare_linux.go

## Purpose
Creates a child process in a new user namespace, then unshares selected namespaces inside it while attributing namespace ownership to a target host UID.

## Important APIs, Types, And Functions
UnshareAfterEnterUserns, parseIDMapping, startProcessWithUserNamespace, startProcessWithUsernsLocked, pidfdWaitid, capSnapshot, getCurrentCaps, setCurrentCaps.

## Control Flow
Validates flags and mappings, requires pidfd support, locks an OS thread, temporarily sets effective UID, restores capabilities, starts /proc/self/exe ptraced with CLONE_NEWUSER plus unshare flags and pidfd, runs optional callback with pid, verifies liveness, then kills/waits via pidfd.

## State And Persistence
Creates temporary child process and kernel namespaces; no filesystem persistence except procfs observations. Uses thread-local credential changes carefully.

## Dependencies And Integration Points
Depends on Linux namespaces, capabilities, pidfds, IgnoringEINTR, and x/sys/unix. Used by tests and namespace setup requiring ownership semantics.

## Risks And Edge Cases
Very sensitive to kernel version, privileges, userns restrictions, capability restoration, and thread state. On errors before restoring UID the goroutine intentionally does not unlock the OS thread.

## Test Signals
unshare_linux_test.go covers valid unshare, child death, invalid flags, and namespace owner UID.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/unshare_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/unshare_linux_test.go -->
# sources/cloud-native/containerd/pkg/sys/unshare_linux_test.go

## Purpose
Root-only Linux tests for UnshareAfterEnterUserns.

## Important APIs, Types, And Functions
TestUnshareAfterEnterUserns and subtests should work, killpid, invalid flags, and ownership; getNamespaceInode helper.

## Control Flow
Tests compare namespace inode changes, inspect uid/gid maps and setgroups, kill the child to verify liveness errors, pass invalid flags, and check NS_GET_OWNER_UID.

## State And Persistence
Creates short-lived namespace child processes and reads procfs namespace/map files.

## Dependencies And Integration Points
Requires root and kernel >=5.10. Depends on unix ioctl and /proc.

## Risks And Edge Cases
Highly environment-sensitive; failures may reflect host namespace policy rather than code regression.

## Test Signals
Direct integration coverage for the most complex sys helper.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/sys/unshare_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/testutil/helpers.go -->
# sources/cloud-native/containerd/pkg/testutil/helpers.go

## Purpose
Shared test helpers for root-gated tests, directory dumping, and unmount cleanup.

## Important APIs, Types, And Functions
rootEnabled flag registration, DumpDir, DumpDirOnFailure, and Unmount.

## Control Flow
init registers or observes -test.root. DumpDir walks paths and logs symlink targets, small regular-file content, and metadata. Unmount calls mount.UnmountAll and asserts no error.

## State And Persistence
Reads filesystem and unmounts mount points during tests; no persistent state beyond registered flag.

## Dependencies And Integration Points
Depends on core/mount and testify/assert. Used across containerd tests.

## Risks And Edge Cases
DumpDir fatals on walk errors, so it is diagnostic but intrusive. Root flag interop handles continuity/testutil duplicate registration.

## Test Signals
Helpers are exercised by many tests, including namespace tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/testutil/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/testutil/helpers_unix.go -->
# sources/cloud-native/containerd/pkg/testutil/helpers_unix.go

## Purpose
Unix root requirement helpers for tests.

## Important APIs, Types, And Functions
RequiresRoot skips unless -test.root is set and asserts os.Getuid()==0; RequiresRootM exits from TestMain-style contexts.

## Control Flow
Checks rootEnabled first, then UID.

## State And Persistence
No persistence except process exit in RequiresRootM.

## Dependencies And Integration Points
Used by tests needing mounts, namespaces, or privileged syscalls.

## Risks And Edge Cases
Tests running as root without -test.root still skip, preventing accidental privileged execution.

## Test Signals
Indirectly covered by root-gated tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/testutil/helpers_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/testutil/helpers_windows.go -->
# sources/cloud-native/containerd/pkg/testutil/helpers_windows.go

## Purpose
Windows no-op root requirement helpers.

## Important APIs, Types, And Functions
RequiresRoot and RequiresRootM do nothing.

## Control Flow
Immediate return.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Keeps test code portable when root concepts are Unix-specific.

## Risks And Edge Cases
May let Windows tests proceed where equivalent Unix tests would be privilege-gated; Windows-specific APIs must handle their own permissions.

## Test Signals
Build-tag coverage only.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/testutil/helpers_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/timeout/timeout.go -->
# sources/cloud-native/containerd/pkg/timeout/timeout.go

## Purpose
Global registry of named timeout durations with context helper.

## Important APIs, Types, And Functions
DefaultTimeout, Set, Get, WithContext, and All.

## Control Flow
Set stores a duration under a key. Get returns key value or DefaultTimeout. WithContext creates context.WithTimeout using Get. All returns a copy of the map.

## State And Persistence
Process-global timeout map protected by RWMutex.

## Dependencies And Integration Points
Used by packages that need configurable operation timeouts without passing durations everywhere.

## Risks And Edge Cases
Global mutable state can leak between tests or subsystems; All returns a copy to avoid external mutation.

## Test Signals
No local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/timeout/timeout.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/helpers.go -->
# sources/cloud-native/containerd/pkg/tracing/helpers.go

## Purpose
Converts arbitrary Go values to OpenTelemetry attribute key-values.

## Important APIs, Types, And Functions
keyValue handles nil, bool/int/float/string scalar and slice types, fmt.Stringer, JSON-marshaled fallback, and fmt.Sprintf fallback.

## Control Flow
Type switch maps values to the most specific attribute constructor, converting narrower ints to int/int64 slices as needed.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Used by tracing.Attribute and logrus hook field conversion.

## Risks And Edge Cases
Unsupported numeric types such as uint fall through to JSON/string. JSON fallback can expose structured data as a string rather than semantic attributes.

## Test Signals
Indirectly covered by tracing/log behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/helpers_spanopts.go -->
# sources/cloud-native/containerd/pkg/tracing/helpers_spanopts.go

## Purpose
Span option helper that adds containerd namespace attribute when present.

## Important APIs, Types, And Functions
WithNamespace returns a SpanOpt that appends trace.WithAttributes(Attribute("namespace", ns)) if namespaces.NamespaceRequired succeeds.

## Control Flow
When StartSpan applies the option, it reads namespace from the supplied context and appends span options best-effort.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Integrates pkg/namespaces with OpenTelemetry tracing helpers.

## Risks And Edge Cases
Missing namespace is silently ignored, so absence may be hard to diagnose in traces.

## Test Signals
No direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/helpers_spanopts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/log.go -->
# sources/cloud-native/containerd/pkg/tracing/log.go

## Purpose
Logrus hook that turns log entries into OpenTelemetry span events and can inject trace_id into log fields.

## Important APIs, Types, And Functions
NewLogrusHook, WithTraceIDField, LogrusHook.Levels, Fire, and logrusDataToAttrs.

## Control Flow
Fire extracts span from entry context, optionally adds trace_id to entry.Data when span context is valid, and if recording adds a span event with log fields, level, and timestamp.

## State And Persistence
Mutates the log entry Data map by adding trace_id when enabled. No persistence.

## Dependencies And Integration Points
Depends on containerd/log and otel trace/attribute. Used to correlate logs and traces.

## Risks And Edge Cases
entry.Data must be non-nil if trace_id injection is enabled. Non-recording spans still get trace_id injection but no event.

## Test Signals
log_test.go covers trace_id injection enabled, disabled, and no-span cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/log.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/log_test.go -->
# sources/cloud-native/containerd/pkg/tracing/log_test.go

## Purpose
Unit tests for trace_id field injection in LogrusHook.

## Important APIs, Types, And Functions
TestLogrusHookTraceID uses fixed TraceID/SpanID and table cases.

## Control Flow
Each case builds a context with or without span context, fires the hook, and asserts trace_id presence/value.

## State And Persistence
Pure in-memory test state.

## Dependencies And Integration Points
Exercises NewLogrusHook, WithTraceIDField, and Fire.

## Risks And Edge Cases
Does not cover recording span event emission or attribute conversion.

## Test Signals
Direct coverage for log correlation behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/log_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/plugin/otlp.go -->
# sources/cloud-native/containerd/pkg/tracing/plugin/otlp.go

## Purpose
Containerd plugin registrations for OTLP trace exporting and global tracer provider setup.

## Important APIs, Types, And Functions
Registers otlp TracingProcessorPlugin and tracing InternalPlugin. OTLPConfig, TraceConfig, checkDisabled, newExporter, newTracer, warnTraceConfig, and warnOTLPConfig implement setup.

## Control Flow
Plugin init warns for deprecated config, skips when OTEL_SDK_DISABLED or no OTLP endpoint, validates OTEL_TRACES_EXPORTER, creates HTTP/protobuf or gRPC exporter, collects span processors, sets propagator/tracer provider, and returns a closer for shutdown.

## State And Persistence
Mutates process environment by setting OTEL_SERVICE_NAME to containerd if unset and sets global OpenTelemetry provider/propagator. Exporter sends trace data externally.

## Dependencies And Integration Points
Depends on containerd plugin registry, warning service, deprecation IDs, errdefs, and OpenTelemetry SDK/exporters.

## Risks And Edge Cases
Environment variables dominate config. Unsupported protocols fail with ErrNotImplemented. Deprecated config only warns when warning plugin is available.

## Test Signals
No direct tests in subset; plugin graph/init tests elsewhere should exercise it.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/plugin/otlp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/plugin/ttrpc.go -->
# sources/cloud-native/containerd/pkg/tracing/plugin/ttrpc.go

## Purpose
Registers ttrpc OpenTelemetry interceptor plugin.

## Important APIs, Types, And Functions
init registers plugin ID otelttrpc of type TTRPCPlugin. otelttrpcopts implements UnaryServerInterceptor and UnaryClientInterceptor.

## Control Flow
Plugin init returns a stateless otelttrpcopts value; callers request interceptors when composing ttrpc servers/clients.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Used by shim event publisher and shim ttrpc server when plugin registry loads tracing ttrpc integration.

## Risks And Edge Cases
Always registers; actual tracing depends on global OpenTelemetry setup.

## Test Signals
No direct tests in subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/plugin/ttrpc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/tracing.go -->
# sources/cloud-native/containerd/pkg/tracing/tracing.go

## Purpose
General OpenTelemetry tracing convenience wrappers for spans, attributes, HTTP clients, and status mapping.

## Important APIs, Types, And Functions
StartConfig, SpanOpt, WithAttribute, UpdateHTTPClient, StartSpan, SpanFromContext, Span methods, Name, Attribute, and HTTPStatusCodeAttributes.

## Control Flow
StartSpan applies SpanOpts, chooses parent tracer provider when valid, starts a span, and wraps it. Span methods delegate to otel span operations. UpdateHTTPClient wraps transport with otelhttp.

## State And Persistence
Mutates http.Client.Transport in place; spans are exported according to global provider state.

## Dependencies And Integration Points
Depends on otel, otelhttp, trace/codes/attribute. Used throughout containerd for consistent tracing APIs.

## Risks And Edge Cases
UpdateHTTPClient overwrites any existing transport by wrapping it; callers must configure client before calling. Name simply joins with dots and does not sanitize segments.

## Test Signals
Covered indirectly by tracing users; log tests cover context/span interaction partially.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/tracing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/ttrpcutil/client.go -->
# sources/cloud-native/containerd/pkg/ttrpcutil/client.go

## Purpose
Reconnectable TTRPC client wrapper for containerd daemon services.

## Important APIs, Types, And Functions
Client, NewClient, Reconnect, EventsService, Client, and Close.

## Control Flow
NewClient builds a connector that dials with a five-second timeout. Client lazily connects under a mutex. Reconnect closes old client and reconnects unless closed. EventsService wraps the current client.

## State And Persistence
Maintains in-memory ttrpc client pointer, connector, mutex, and closed flag. Network connection is external state.

## Dependencies And Integration Points
Used by shim RemoteEventsPublisher to forward events to containerd ttrpc services.

## Risks And Edge Cases
Close marks closed, but Client does not check closed before lazy initial connect; Reconnect does. Connector nil would make Reconnect fail.

## Test Signals
No direct tests in subset; publisher paths exercise it indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/ttrpcutil/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/content_local_fuzz_test.go -->
# sources/cloud-native/containerd/plugins/content/local/content_local_fuzz_test.go

## Purpose
Fuzzes resumable local content writer behavior over arbitrary byte slices.

## Important APIs, Types, And Functions
FuzzContentStoreWriter and checkCopyFuzz.

## Control Flow
The fuzz target opens a store, creates and closes a writer, reopens it with same ref, copies fuzz data, computes expected digest, and commits.

## State And Persistence
Uses temp content store directories and ingest/blob files cleaned by test tempdir.

## Dependencies And Integration Points
Exercises NewStore, Writer resume, Write, and Commit for arbitrary data.

## Risks And Edge Cases
Commit errors are tolerated for some fuzz inputs/conditions, so the target primarily catches panics and copy failures.

## Test Signals
Fuzz coverage for writer resume and digest commit path.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/content_local_fuzz_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/helper_test.go -->
# sources/cloud-native/containerd/plugins/content/local/helper_test.go

## Purpose
Shared test setup for local content store tests.

## Important APIs, Types, And Functions
contentStoreEnv creates temp dir, NewStore, cancellable context, and cleanup function.

## Control Flow
Tests call helper, use returned content.Store and temp path, then cleanup cancels context.

## State And Persistence
Creates a temporary filesystem-backed store.

## Dependencies And Integration Points
Used by store_test.go benchmarks and tests.

## Risks And Edge Cases
Uses NewStore without label store, so label-update tests need separate setup.

## Test Signals
Indirect support for local content tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/helper_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/locks.go -->
# sources/cloud-native/containerd/plugins/content/local/locks.go

## Purpose
In-memory per-ref lock manager for local content ingests.

## Important APIs, Types, And Functions
lock records since time; store.tryLock and store.unlock manage the locks map.

## Control Flow
tryLock rejects an already locked ref with ErrUnavailable and duration information; unlock deletes the entry.

## State And Persistence
State is process-local and not persisted, so it coordinates writers only within one store process.

## Dependencies And Integration Points
Used by store.Writer to enforce single active writer per ref.

## Risks And Edge Cases
Does not coordinate across processes; stale locks are cleared only by unlock or process exit.

## Test Signals
locks_test.go validates duplicate lock error text.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/locks.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/locks_test.go -->
# sources/cloud-native/containerd/plugins/content/local/locks_test.go

## Purpose
Unit test for local store ref locks.

## Important APIs, Types, And Functions
TestTryLock calls tryLock twice on the same ref and checks second error contains lock duration text.

## Control Flow
Creates minimal store with locks map, locks/unlocks a ref.

## State And Persistence
Pure in-memory state.

## Dependencies And Integration Points
Exercises locks.go duplicate protection.

## Risks And Edge Cases
Does not test concurrent goroutines or unlock of absent refs.

## Test Signals
Direct coverage for duplicate lock behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/locks_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/plugin/plugin.go -->
# sources/cloud-native/containerd/plugins/content/local/plugin/plugin.go

## Purpose
Registers the local content store as a containerd content plugin.

## Important APIs, Types, And Functions
init registers plugins.ContentPlugin with ID content and an InitFn.

## Control Flow
InitFn reads PropertyRootDir from plugin context, exports it in metadata, and returns local.NewStore(root).

## State And Persistence
Creates/uses the content root directory via NewStore. Plugin metadata exports root path.

## Dependencies And Integration Points
Integrates containerd plugin registry with plugins/content/local package.

## Risks And Edge Cases
Root property must be populated by plugin host. Label store is nil, so mutable labels are not supported by this plugin instance unless wrapped elsewhere.

## Test Signals
Covered by plugin integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/plugin/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/readerat.go -->
# sources/cloud-native/containerd/plugins/content/local/readerat.go

## Purpose
Filesystem-backed content.ReaderAt implementation for blobs.

## Important APIs, Types, And Functions
sizeReaderAt, OpenReader, ReadAt, Size, Close, and Reader.

## Control Flow
OpenReader stats and opens a blob path, returning ErrNotFound-wrapped errors for missing files. ReadAt delegates to os.File.ReadAt; Reader returns a LimitReader of the open file.

## State And Persistence
Holds an open file descriptor and immutable size captured at open time.

## Dependencies And Integration Points
Used by store.ReaderAt to serve blob reads through content.Store.

## Risks And Edge Cases
Reader() shares the same file offset as the underlying file, while ReadAt is offset-independent. Missing files are normalized to errdefs.ErrNotFound.

## Test Signals
Covered by content testsuite through ReaderAt operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/readerat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/store.go -->
# sources/cloud-native/containerd/plugins/content/local/store.go

## Purpose
Core filesystem implementation of content.Store with digest-addressed blobs, resumable ingest transactions, optional labels, and optional fsverity integrity.

## Important APIs, Types, And Functions
LabelStore interface; store fields; NewStore/NewLabeledStore; Info, ReaderAt, Delete, Update, Walk, Status, ListStatuses, WalkStatusRefs, Writer, Abort, blobPath, ingestRoot, timestamp helpers.

## Control Flow
New store creates root and probes fsverity. Writer locks a ref, hashes ref to ingest path, resumes valid ingest by replaying data into the digester or creates ref/timestamp/total files, then returns writer. Info/Walk read blobs under blobs/<alg>/<encoded>. Status reads ingest metadata. Update delegates label mutations and adjusts atime.

## State And Persistence
Persistent layout: root/blobs/<algorithm>/<digest> for committed blobs and root/ingest/<digest(ref)>/{ref,data,startedat,updatedat,total} for active uploads. Labels are stored by optional LabelStore, not filesystem by default. ensureIngestRootOnce memoizes directory creation.

## Dependencies And Integration Points
Implements core/content.Store and integrates filters, errdefs, fsverity, digest algorithms, and writer.go commit logic. Registered by plugin/plugin.go.

## Risks And Edge Cases
In-memory locks are not cross-process. Resume rehashes entire data file and can be slow. Walk tolerates invalid digest paths by logging. Label updates are unsupported when ls is nil. Delete uses RemoveAll on blob path.

## Test Signals
store_test.go, locks_test.go, content testsuite, benchmarks, and fuzz test cover creation, writer resume, duplicate commits, walk, fsverity, labels, truncation recovery, and timestamp parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/store_bsd.go -->
# sources/cloud-native/containerd/plugins/content/local/store_bsd.go

## Purpose
BSD/Darwin/NetBSD access-time extraction for content.Info UpdatedAt.

## Important APIs, Types, And Functions
getATime reads syscall.Stat_t.Atimespec or falls back to ModTime.

## Control Flow
Called by store.info when building content.Info.

## State And Persistence
No state; reads os.FileInfo syscall data.

## Dependencies And Integration Points
Platform-specific companion to store.go.

## Risks And Edge Cases
Depends on Stat_t shape for darwin/freebsd/netbsd.

## Test Signals
Covered indirectly by Info tests on those platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/store_bsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/store_openbsd.go -->
# sources/cloud-native/containerd/plugins/content/local/store_openbsd.go

## Purpose
OpenBSD access-time extraction for content.Info UpdatedAt.

## Important APIs, Types, And Functions
getATime reads syscall.Stat_t.Atim or falls back to ModTime.

## Control Flow
Called by store.info.

## State And Persistence
No state; reads file metadata.

## Dependencies And Integration Points
Platform-specific store.go helper.

## Risks And Edge Cases
OpenBSD Stat_t field differs from other BSDs, hence separate file.

## Test Signals
Indirect platform coverage only.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/store_openbsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/store_test.go -->
# sources/cloud-native/containerd/plugins/content/local/store_test.go

## Purpose
Comprehensive tests and benchmarks for the local content store.

## Important APIs, Types, And Functions
memoryLabelStore, TestContent, TestContentRootDir, TestInvalidPermissionRootDir, TestContentWriter, TestWalkBlobs, BenchmarkIngests, helper generators, TestWriterTruncateRecoversFromIncompleteWrite, TestWriteReadEmptyFileTimestamp.

## Control Flow
Tests run content testsuite, create stores under temp dirs, write random blobs with sha256/sha512, resume writers, assert duplicate commit errors, verify readonly permissions and fsverity when available, walk blobs, and recover from truncated ingest.

## State And Persistence
Creates temp content store roots, ingest directories, committed blobs, and optional immutable directory state via chattr in a root-only test.

## Dependencies And Integration Points
Exercises store.go, writer.go, readerat.go, lock behavior via Writer, fsverity integration, and content package helpers.

## Risks And Edge Cases
Some tests are root/tool/fsverity dependent. Benchmarks generate random blob maps for two algorithms, potentially doubling blob count.

## Test Signals
High-signal direct coverage for store correctness and persistence layout.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/store_unix.go -->
# sources/cloud-native/containerd/plugins/content/local/store_unix.go

## Purpose
Linux/Solaris access-time extraction for content.Info UpdatedAt.

## Important APIs, Types, And Functions
getATime reads syscall.Stat_t.Atim or falls back to ModTime.

## Control Flow
Called by store.info.

## State And Persistence
No state; reads file metadata.

## Dependencies And Integration Points
Platform-specific store.go helper.

## Risks And Edge Cases
Depends on Unix Stat_t Atim field presence.

## Test Signals
Indirect platform coverage only.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/store_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/store_windows.go -->
# sources/cloud-native/containerd/plugins/content/local/store_windows.go

## Purpose
Windows access-time fallback for local content store.

## Important APIs, Types, And Functions
getATime returns FileInfo.ModTime.

## Control Flow
Called by store.info on Windows.

## State And Persistence
No state.

## Dependencies And Integration Points
Keeps store.go portable on Windows where Unix atime fields are unavailable.

## Risks And Edge Cases
UpdatedAt is less precise semantically because it mirrors modification time.

## Test Signals
Indirect Windows content tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/store_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/writer.go -->
# sources/cloud-native/containerd/plugins/content/local/writer.go

## Purpose
Write transaction implementation for local content store ingests.

## Important APIs, Types, And Functions
writer fields and methods Status, Digest, Write, Commit, Close, Truncate, and Sync.

## Control Flow
Write appends to data file, updates digester and offset. Commit syncs/stat/closes, validates size/digest, optionally rehashes to expected algorithm, renames ingest data to blob path, syncs parent dir, enables fsverity, timestamps, cleans ingest, stores labels, and chmods readonly on non-Windows. Close leaves resumable state.

## State And Persistence
Persists ingest data while open/closed before commit; commit atomically promotes by rename into blobs tree and removes ingest dir. Uses file mtimes for committed info.

## Dependencies And Integration Points
Tightly coupled to store.go paths/locks and fsverity. Implements content.Writer.

## Risks And Edge Cases
Write increments offset by len(p) rather than n, which matters if a partial write returns n<len(p) with error. Commit after Close fails. Cross-device rename would fail if ingest/blob roots diverged, but they share root.

## Test Signals
store_test.go covers sha256/sha512 commits, duplicate content, fsverity, truncate recovery, and content testsuite behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/writer_unix.go -->
# sources/cloud-native/containerd/plugins/content/local/writer_unix.go

## Purpose
Unix directory sync helper for durable blob commit.

## Important APIs, Types, And Functions
syncDir opens a directory and calls Sync.

## Control Flow
Commit calls syncDir after renaming blob into place.

## State And Persistence
Forces directory metadata to storage on Unix filesystems.

## Dependencies And Integration Points
Used by writer.go.

## Risks And Edge Cases
Directory sync can fail on filesystems that do not support fsync on directories.

## Test Signals
Covered indirectly by writer commit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/writer_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/writer_windows.go -->
# sources/cloud-native/containerd/plugins/content/local/writer_windows.go

## Purpose
Windows no-op directory sync helper.

## Important APIs, Types, And Functions
syncDir returns nil.

## Control Flow
Commit calls it but no operation occurs.

## State And Persistence
No state or persistence beyond normal file operations.

## Dependencies And Integration Points
Platform companion for writer.go.

## Risks And Edge Cases
Windows lacks the same directory sync support, so crash-durability differs from Unix.

## Test Signals
Indirect Windows content tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/content/local/writer_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/cri/cri.go -->
# sources/cloud-native/containerd/plugins/cri/cri.go

## Purpose
Registers and initializes the top-level Kubernetes CRI gRPC plugin by wiring runtime/image services, sandbox controllers, NRI, streaming config, warnings, and containerd in-memory services.

## Important APIs, Types, And Functions
init registration, initCRIService, imageService and initializer interfaces, criGRPCServer, criGRPCServerWithTCP, getNRIAPI, getSandboxControllers, and configMigration.

## Control Flow
Init loads runtime and image CRI service dependencies, propagates runtime-specific snapshotters to image service, validates config and emits warnings, creates an in-memory containerd client, collects sandbox controllers, builds server.CRIServiceOptions, starts the CRI service readiness goroutine, and returns a gRPC registrar with optional TCP registration.

## State And Persistence
Long-running CRI service state is owned by server.NewCRIService and its Run loop. Config migration mutates pluginConfigs maps during daemon startup.

## Dependencies And Integration Points
Depends on containerd client, plugin registry, internal CRI config/server/images/instrument packages, sandbox/NRI plugins, warning service, grpc, Kubernetes CRI API, and platform defaults.

## Risks And Edge Cases
Startup is dependency-heavy; missing runtime/image services or bad config abort plugin init. NRI type mismatch disables NRI. DisableTCPService changes returned interface capabilities. Migration preserves only selected streaming/TCP fields from old grpc.cri config.

## Test Signals
cri_test.go covers configMigration field retention/removal. Broader CRI behavior is tested in internal CRI packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/cri/cri.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/cri/cri_test.go -->
# sources/cloud-native/containerd/plugins/cri/cri_test.go

## Purpose
Unit test for CRI gRPC plugin config migration.

## Important APIs, Types, And Functions
TestCRIGRPCServerConfigMigration builds old grpc.cri config map with removed and retained keys.

## Control Flow
Calls configMigration with config version 2, then asserts registry/containerd subsections were removed and streaming/TCP keys remain.

## State And Persistence
Pure in-memory map mutation.

## Dependencies And Integration Points
Exercises configMigration in cri.go.

## Risks And Edge Cases
Only tests one old version path and one plugin name; does not cover current-version no-op.

## Test Signals
Direct coverage for migration contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/cri/cri_test.go -->
