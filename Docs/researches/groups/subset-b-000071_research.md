# subset-b-000071 research

This grouped report covers the requested containerd CRI utility, internal helper, platform integration, and archive compression files. Each source file has its own marked section for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/util.go -->
# sources/cloud-native/containerd/internal/cri/store/util.go

## Purpose
Defines small store-level contracts for the CRI plugin: `StatsCollector` abstracts CPU/stat sample tracking for containers and sandboxes, and `StopCh` gives container state objects a one-shot stop notification channel.

## Important APIs, Types, And Functions
`StatsCollector` exposes `AddContainer` and `RemoveContainer`. `StopCh` owns a `chan struct{}` and `sync.Once`; `NewStopCh` creates the open channel, `Stop` closes it once, and `Stopped` returns a receive-only channel.

## Control Flow
Callers allocate `StopCh`, pass `Stopped()` to waiters, and invoke `Stop()` when lifecycle state reaches stopped. The `sync.Once` guard makes repeated stop paths safe.

## State And Persistence
All state is in-memory. `StopCh` persists only process-local notification state and does not encode container status.

## Dependencies And Integration Points
Depends only on `sync`. It integrates with CRI store objects and stats collectors that need stable interfaces without importing implementation details.

## Risks
Closing is irreversible, so a `StopCh` cannot be reused for restarted objects. Consumers must treat the returned channel as notification only and not infer why the container stopped.

## Test Signals
No direct tests in this file. Correctness is exercised indirectly by CRI lifecycle/store tests that wait on stop channels or manage stats collectors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/store/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/systemd/util.go -->
# sources/cloud-native/containerd/internal/cri/systemd/util.go

## Purpose
Provides Linux-only detection of whether the host booted with systemd. The CRI plugin can use this to decide whether systemd-specific integration paths are available.

## Important APIs, Types, And Functions
`IsRunningSystemd` checks `/run/systemd/system` once and caches the result in package globals `runningSystemd` and `detectSystemd`.

## Control Flow
The first call runs `os.Lstat`; success plus `IsDir()` sets the cached boolean. Later calls return the cached value without touching the filesystem.

## State And Persistence
State is process-local and immutable after first detection. It does not monitor changes to `/run/systemd/system`.

## Dependencies And Integration Points
Uses `os` and `sync`. It mirrors the behavior of systemd's `sd_booted(3)` and CoreOS go-systemd utility logic.

## Risks
The once-only cache can be stale in unusual test or chroot scenarios. The file has a Linux build tag, so non-Linux callers need alternate build paths.

## Test Signals
No direct tests in this subset. Testability is limited by the hard-coded host path and `sync.Once` global cache.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/systemd/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/testing/fake_cni_plugin.go -->
# sources/cloud-native/containerd/internal/cri/testing/fake_cni_plugin.go

## Purpose
Implements a fake CNI plugin for CRI tests that need a `go-cni`-compatible object without invoking real network setup.

## Important APIs, Types, And Functions
`FakeCNIPlugin` carries injectable `StatusErr` and `LoadErr`. `NewFakeCNIPlugin` constructs it. `Setup`, `SetupSerially`, `Remove`, `Check`, and `GetConfig` are no-op stubs; `Status` and `Load` return configured errors.

## Control Flow
Tests install the fake, configure status/load errors when needed, and exercise CRI code paths without side effects. Network setup and teardown always return successful empty results unless the tested path calls `Status` or `Load`.

## State And Persistence
Only the two error fields are stateful. There is no network, namespace, or CNI config persistence.

## Dependencies And Integration Points
Depends on `context` and `github.com/containerd/go-cni`. It is an internal test helper for CRI networking paths.

## Risks
Because setup/remove/check are always successful, tests using this fake do not cover CNI result parsing, interface ordering, namespace options, or cleanup failures.

## Test Signals
The file itself is test infrastructure. Its behavior is validated indirectly by CRI tests that use `NewFakeCNIPlugin`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/testing/fake_cni_plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/util/deep_copy.go -->
# sources/cloud-native/containerd/internal/cri/util/deep_copy.go

## Purpose
Provides a generic deep-copy helper for CRI data structures by JSON round-tripping from source to destination.

## Important APIs, Types, And Functions
`DeepCopy(dst any, src any) error` rejects nil arguments, marshals `src` with `encoding/json`, then unmarshals into `dst`, wrapping marshal/unmarshal errors.

## Control Flow
The caller supplies a pointer destination. Successful marshal output replaces destination fields according to JSON semantics.

## State And Persistence
No persistent state. Destination object is mutated on successful unmarshal and can be partially changed if JSON unmarshalling fails after writing earlier fields.

## Dependencies And Integration Points
Uses `encoding/json`, `errors`, and `fmt`. It is appropriate for JSON-compatible CRI structs but not for values with unexported fields, channels, funcs, or non-JSON representation requirements.

## Risks
JSON conversion may lose type information, skip unexported fields, coerce numbers, and allocate heavily. It is not a general Go object graph copier.

## Test Signals
`deep_copy_test.go` verifies nested slices, maps, and pointer values are replaced with source-equivalent values.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/util/deep_copy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/util/deep_copy_test.go -->
# sources/cloud-native/containerd/internal/cri/util/deep_copy_test.go

## Purpose
Tests the JSON-backed `DeepCopy` helper with nested composite values.

## Important APIs, Types, And Functions
Defines test struct `A` with strings, ints, slices, maps, and nested `*A` values. `TestCopy` builds distinct source, destination, and expected values.

## Control Flow
The test asserts the destination initially differs, calls `DeepCopy(dst, src)`, requires no error, then checks full equality with the expected copy.

## State And Persistence
Only in-memory test fixtures. The destination object is intentionally mutated.

## Dependencies And Integration Points
Uses Go testing and `testify/assert`. It directly covers `internal/cri/util.DeepCopy`.

## Risks
The test does not cover nil arguments, marshal errors, unmarshal errors, custom JSON methods, or partial mutation on unmarshal failure.

## Test Signals
Strong signal for ordinary JSON-compatible nested maps/slices and replacement semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/util/deep_copy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/util/id.go -->
# sources/cloud-native/containerd/internal/cri/util/id.go

## Purpose
Generates opaque random IDs for CRI/containerd internal use.

## Important APIs, Types, And Functions
`GenerateID` allocates 32 random bytes using `crypto/rand.Read` and returns a 64-character hex string.

## Control Flow
The function reads random bytes and encodes them without exposing errors to the caller.

## State And Persistence
No internal state. Returned IDs may be persisted by callers as object identifiers.

## Dependencies And Integration Points
Uses `crypto/rand` and `encoding/hex`. It is a small utility for callers needing high-entropy IDs.

## Risks
The return value ignores `rand.Read` errors, so a failing entropy source could silently produce all-zero or partially-filled data. Callers cannot distinguish random-source failure.

## Test Signals
No direct tests in this subset. Coverage would need length, hex format, uniqueness, and entropy-error behavior tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/util/id.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/util/references.go -->
# sources/cloud-native/containerd/internal/cri/util/references.go

## Purpose
Normalizes and classifies image references for CRI image status and metadata reporting.

## Important APIs, Types, And Functions
`ParseImageReferences` parses arbitrary strings with `distribution/reference.ParseAnyReference`, returning separate repo tag and repo digest slices. `GetRepoDigestAndTag` derives a repo digest from a named reference plus OCI digest and preserves a tag when the original reference was tagged.

## Control Flow
Invalid references are skipped. Canonical references become digests, tagged references become tags, and digest-only references without a repository are not reported as repo digests.

## State And Persistence
No internal state. Returned strings can be stored in CRI image status fields.

## Dependencies And Integration Points
Uses `github.com/distribution/reference` and `github.com/opencontainers/go-digest`. It integrates CRI image reporting with Docker/reference parsing rules.

## Risks
Silently skipping parse failures can hide malformed input unless callers log elsewhere. Reference normalization follows upstream parser behavior and may differ from user-provided spelling.

## Test Signals
`references_test.go` covers tagged, canonical, digest-only, invalid, and tag-plus-digest derivation cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/util/references.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/util/references_test.go -->
# sources/cloud-native/containerd/internal/cri/util/references_test.go

## Purpose
Validates CRI image reference parsing and repo digest/tag construction.

## Important APIs, Types, And Functions
`TestParseImageReferences` feeds canonical, tagged, digest-only, and arbitrary refs. `TestGetRepoDigestAndTag` parses Docker refs and checks returned repo digest and tag.

## Control Flow
Tests compare exact returned slices and strings after invoking the helpers.

## State And Persistence
No state beyond test vectors.

## Dependencies And Integration Points
Uses `testify/assert`, `distribution/reference`, and `opencontainers/go-digest`.

## Risks
The test vectors are narrow and do not cover multiple tags, ports, default registry normalization, uppercase rejection, or malformed digest algorithms.

## Test Signals
Good regression coverage for the core branch decisions: canonical versus tagged versus invalid.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/util/references_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/util/sanitize.go -->
# sources/cloud-native/containerd/internal/cri/util/sanitize.go

## Purpose
Redacts URL query parameters from errors, mainly to avoid leaking signed URL tokens or credentials in CRI/containerd error messages.

## Important APIs, Types, And Functions
`SanitizeError` detects `*url.Error` through `errors.As`, sanitizes its URL, and returns a `sanitizedError` wrapper when redaction changes the URL. `sanitizeURL` parses URLs and replaces every query value with `[REDACTED]`. `sanitizedError` implements `Error` and `Unwrap`.

## Control Flow
Non-URL or nil errors pass through unchanged. URL errors without query parameters also pass through. Wrapped URL errors preserve their original chain while changing the rendered message by replacing occurrences of the original URL.

## State And Persistence
No persistent state. The wrapper keeps the original error and sanitized URL.

## Dependencies And Integration Points
Uses `errors`, `net/url`, and `strings`. It integrates with logging and error-return paths where `errors.As` compatibility must be preserved.

## Risks
Malformed URLs are returned unchanged. Redacted marker values are URL-encoded as `%5BREDACTED%5D`, which is safe but may surprise string comparisons. Only query values are redacted; credentials in userinfo or paths are not.

## Test Signals
`sanitize_test.go` covers direct and wrapped URL errors, nil/non-URL passthrough, no-query passthrough, and unwrap behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/util/sanitize.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/util/sanitize_test.go -->
# sources/cloud-native/containerd/internal/cri/util/sanitize_test.go

## Purpose
Tests URL-query redaction behavior for `SanitizeError`.

## Important APIs, Types, And Functions
Test cases create `url.Error` values with sensitive query strings, wrapped errors, non-URL errors, nil errors, and no-query URLs.

## Control Flow
The tests call `SanitizeError`, inspect concrete wrapper type for direct URL errors, compare rendered messages, and verify `errors.As` and `errors.Unwrap` still expose the original URL error.

## State And Persistence
Only in-memory error objects are used.

## Dependencies And Integration Points
Uses `errors`, `fmt`, `net/url`, `testing`, `testify/assert`, and `testify/require`.

## Risks
Tests do not cover malformed URLs, userinfo credentials, repeated query values, fragments, or multiple URL errors in one chain.

## Test Signals
Strong coverage for the intended signed-URL query redaction path and error-chain preservation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/util/sanitize_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/util/strings.go -->
# sources/cloud-native/containerd/internal/cri/util/strings.go

## Purpose
Provides small case-insensitive string-slice helpers for CRI configuration and option handling.

## Important APIs, Types, And Functions
`InStringSlice` performs case-insensitive membership. `SubtractStringSlice` removes all case-insensitive matches. `MergeStringSlices` combines two slices through Kubernetes `sets`.

## Control Flow
The first two helpers scan linearly with `strings.EqualFold`. Merge builds a set from the first slice, inserts the second, and returns an unsorted list.

## State And Persistence
No state. Returned slices are new result slices but string elements are shared.

## Dependencies And Integration Points
Uses `strings` and `k8s.io/apimachinery/pkg/util/sets`.

## Risks
`MergeStringSlices` is case-sensitive because Kubernetes sets use exact strings, unlike the other helpers. Its output order is unspecified.

## Test Signals
`strings_test.go` verifies case-insensitive membership and subtraction, including nil and empty inputs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/util/strings.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/util/strings_test.go -->
# sources/cloud-native/containerd/internal/cri/util/strings_test.go

## Purpose
Tests CRI string-slice helpers for case-insensitive lookup and removal.

## Important APIs, Types, And Functions
`TestInStringSlice` checks exact, case-different, missing, and nil-slice cases. `TestSubtractStringSlice` checks removal and no-op behavior.

## Control Flow
Each test builds a fixed slice and asserts expected booleans or returned slices.

## State And Persistence
No persistent state.

## Dependencies And Integration Points
Uses Go testing and `testify/assert`.

## Risks
The tests do not cover `MergeStringSlices`, duplicate preservation/removal, or output ordering.

## Test Signals
Good coverage for the two case-insensitive helpers, with a gap around merge semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/util/strings_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/util/util.go -->
# sources/cloud-native/containerd/internal/cri/util/util.go

## Purpose
Collects core CRI utility functions for namespaced containerd contexts, cleanup timeout handling, annotation filtering, label construction, OCI user-string generation, and shim ttrpc closed-error detection.

## Important APIs, Types, And Functions
`DeferContext`, `NamespacedContext`, and `WithNamespace` apply the Kubernetes containerd namespace and cleanup timeout. `GetPassthroughAnnotations` filters pod annotations by glob patterns. `BuildLabels` merges validated image labels with request labels and injects the CRI container kind label. `GenerateUserString` converts CRI username/uid/gid combinations into OCI user strings. `IsShimTTRPCClosed` recognizes closed shim ttrpc errors.

## Control Flow
Package init registers the defer cleanup timeout. Annotation matching uses `path.Match` so Windows backslashes are not treated as separators. Label building logs and skips invalid image labels, then lets config labels override. User generation follows CRI's allowed username/uid/gid matrix and rejects gid-only input.

## State And Persistence
State is limited to the global timeout key. Returned contexts, label maps, and strings are transient, but labels may be persisted in container metadata.

## Dependencies And Integration Points
Integrates Kubernetes CRI runtime API, containerd namespaces/timeouts/labels, CRI constants and labels, containerd logging, errdefs, and ttrpc.

## Risks
Invalid config labels are not revalidated after override. Annotation glob errors are ignored as non-matches. `IsShimTTRPCClosed` relies on string suffix matching inside an unknown error wrapper.

## Test Signals
`util_test.go` covers user-string combinations, annotation glob filtering, and shim closed-error detection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/util/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/util/util_test.go -->
# sources/cloud-native/containerd/internal/cri/util/util_test.go

## Purpose
Tests the main CRI utility behavior in `util.go`.

## Important APIs, Types, And Functions
The tests exercise `GenerateUserString`, `GetPassthroughAnnotations`, and `IsShimTTRPCClosed`, using CRI `Int64Value`, path-style patterns, and wrapped ttrpc errors.

## Control Flow
Table-driven cases compare expected user strings/errors, annotation maps filtered by runtime patterns, and boolean recognition of closed shim ttrpc errors.

## State And Persistence
No persisted state. Tests use in-memory maps and errors.

## Dependencies And Integration Points
Uses Go testing, CRI runtime API types, errdefs, ttrpc, and testify assertions.

## Risks
The tests do not cover `BuildLabels`, namespace context helpers, timeout registration, invalid label logging, or malformed annotation patterns.

## Test Signals
Strong signal for user-string edge cases and annotation glob semantics, with partial coverage of shim error classification.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/util/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/dmverity/dmverity.go -->
# sources/cloud-native/containerd/internal/dmverity/dmverity.go

## Purpose
Defines platform-neutral dm-verity options and metadata helpers shared by Linux and non-Linux implementations.

## Important APIs, Types, And Functions
`DmverityOptions` holds salt, hash algorithm, block sizes, data blocks, hash offset, hash type, superblock mode, and UUID. `DefaultDmverityOptions` returns sha256/4096-byte defaults. `MetadataPath`, `DevicePath`, `DmverityMetadata`, and `ReadMetadata` handle metadata file naming and JSON parsing.

## Control Flow
`ReadMetadata` maps a layer blob path to `*.dmverity`, reads JSON, unmarshals `roothash` and `hashoffset`, and rejects missing root hashes.

## State And Persistence
The metadata file is persistent sidecar state for dm-verity-enabled layer blobs. Options are caller-owned in memory.

## Dependencies And Integration Points
Uses JSON, filesystem reads, and string/path formatting. Linux code consumes these options when formatting/opening verity devices.

## Risks
Only root hash presence is validated here; hash format validation happens later. `MetadataPath` blindly appends `.dmverity` based on suffix and does not sanitize paths.

## Test Signals
`dmverity_test.go` covers metadata path/device path helpers, valid and invalid metadata JSON, and missing file/root hash cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/dmverity/dmverity.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/dmverity/dmverity_linux.go -->
# sources/cloud-native/containerd/internal/dmverity/dmverity_linux.go

## Purpose
Implements Linux dm-verity formatting, opening, closing, and verification using `go-dmverity` plus containerd loop-device helpers.

## Important APIs, Types, And Functions
`IsSupported` checks `/sys/module/dm_verity`. `convertToVerityParams` maps `DmverityOptions` to `verity.Params`. `Format` creates a hash tree and returns the root hash. `Open` creates read-only loop devices and opens a device-mapper verity target. `Close` closes the target. `VerifyDevice` checks device health and root hash.

## Control Flow
Formatting defaults options, computes data blocks if omitted, applies salt/UUID, and calls `verity.Create`. Opening validates root hash, chooses superblock or no-superblock params, sets up loop devices for data/hash files, calls `verity.Open`, then closes loop file handles after the kernel holds references.

## State And Persistence
Persistent effects include hash data written to the hash device and `/dev/mapper/<name>` targets. Loop devices use autoclear read-only settings.

## Dependencies And Integration Points
Depends on `core/mount`, `github.com/containerd/go-dmverity/pkg/utils`, and `verity`. Integrates with EROFS/layer integrity workflows that need transparent verified block devices.

## Risks
Requires Linux, loaded/built-in dm_verity, loop devices, device-mapper privileges, and correct offsets. Error cleanup must close loop devices on failures. Superblock versus no-superblock parameter mismatch can produce unusable mappings.

## Test Signals
Linux root tests cover support detection, same/separate device, superblock/no-superblock modes, open/close behavior, and invalid salt/UUID/root hash paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/dmverity/dmverity_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/dmverity/dmverity_other.go -->
# sources/cloud-native/containerd/internal/dmverity/dmverity_other.go

## Purpose
Provides non-Linux stubs for the dm-verity API so packages can compile across platforms.

## Important APIs, Types, And Functions
`errUnsupported` is returned by `IsSupported`, `Format`, `Open`, `Close`, and `VerifyDevice`.

## Control Flow
Every operation immediately reports unsupported; `IsSupported` also returns `false`.

## State And Persistence
No state and no side effects.

## Dependencies And Integration Points
Uses only `fmt`. It preserves the same API surface as the Linux implementation under a `!linux` build tag.

## Risks
Callers must check support or handle errors; otherwise integrity features will fail on non-Linux platforms.

## Test Signals
No direct non-Linux tests in this subset. Compile coverage is the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/dmverity/dmverity_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/dmverity/dmverity_test.go -->
# sources/cloud-native/containerd/internal/dmverity/dmverity_test.go

## Purpose
Validates dm-verity metadata helpers and Linux dm-verity device workflows.

## Important APIs, Types, And Functions
`TestDMVerity` covers `IsSupported`, `Format`, `Open`, and `Close` across superblock/no-superblock and same/separate device combinations. Helper functions create loopback devices and wait for mapper nodes. `TestReadMetadata`, `TestMetadataPath`, `TestDevicePath`, and `TestErrorHandling` cover helper and failure paths.

## Control Flow
Root-only tests skip when dm-verity is unsupported, create temporary backing files, attach loop devices, format/open mappings, verify `/dev/mapper` appearance, close targets, and detach loops.

## State And Persistence
Tests create temporary files, loop devices, and device-mapper targets, then clean them up.

## Dependencies And Integration Points
Uses containerd mount loop helpers, `testutil.RequiresRoot`, docker/go-units, os/stat polling, and testify.

## Risks
Tests are environment-sensitive and require root, loop device availability, device-mapper, and dm_verity support. Failures can leave kernel resources if cleanup paths break.

## Test Signals
High integration signal for Linux verity behavior plus good unit coverage for metadata parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/dmverity/dmverity_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/erofsutils/mount.go -->
# sources/cloud-native/containerd/internal/erofsutils/mount.go

## Purpose
Provides helpers for recognizing, creating, indexing, and locating EROFS layer blobs used by containerd snapshot/differ paths.

## Important APIs, Types, And Functions
`IsErofsMediaType` checks media-type prefixes. `ConvertTarErofs`, `GenerateTarIndexAndAppendTar`, and `ConvertErofs` invoke `mkfs.erofs`. `AddDefaultMkfsOpts` adds macOS block-size defaults. `MountsToLayer` maps snapshot mounts back to an EROFS layer directory. `SupportGenerateFromTar` probes `mkfs.erofs --help`.

## Control Flow
Conversion functions assemble command arguments, attach stdin/environment, run `mkfs.erofs`, and wrap combined-output failures. Tar-index generation tees input to a temp file, writes an index, then appends original tar data to the output layer. `MountsToLayer` inspects mount type/options and requires `.erofslayer` marker.

## State And Persistence
Creates persistent EROFS layer files and temporary tar files. Uses marker files in layer directories to confirm EROFS snapshot ownership.

## Dependencies And Integration Points
Depends on external `mkfs.erofs`, containerd `mount.Mount`, errdefs, logging, and OS/runtime behavior. It integrates differs, snapshot mounts, and EROFS media-type handling.

## Risks
External command availability/version is critical. Mount option parsing assumes known overlay/bind/mkfs shapes. Temporary file storage can be large for tar-index generation.

## Test Signals
Indirectly covered by fsview EROFS tests that require `mkfs.erofs` tar support and by differ/snapshot integration tests outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/erofsutils/mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/eventq/eventq.go -->
# sources/cloud-native/containerd/internal/eventq/eventq.go

## Purpose
Implements a generic in-process event queue with fan-out subscribers and a short retention window for events sent before any subscriber exists.

## Important APIs, Types, And Functions
`EventQueue[T]` exposes `Send`, `Subscribe`, and `Shutdown`. `New` starts the dispatcher goroutine. `eventSubscription` wraps subscriber channel delivery and close signaling.

## Control Flow
The dispatcher receives events, publishes to active subscribers, queues events if none are active, drains queued events to a new subscriber, discards expired events via `discardFn`, and closes subscriber channels on shutdown.

## State And Persistence
State is in-memory: event channels, subscriber list, discard queue, and timers. No events persist beyond process lifetime.

## Dependencies And Integration Points
Uses Go channels, generics, `io.Closer`, and `time`. It can support runtime event notifications where late subscribers should receive recent events.

## Risks
`Shutdown` sends on then closes `shutdownC`; concurrent repeated shutdowns can panic. `Subscribe` sends on `subscriberC` without a shutdown select, so subscribing after shutdown may block. Subscriber channel buffer is fixed at 100 and slow subscribers can backpressure publishing.

## Test Signals
`eventq_test.go` covers single/multiple subscribers, missed events, late subscribers, time-based discard, and shutdown discard.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/eventq/eventq.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/eventq/eventq_test.go -->
# sources/cloud-native/containerd/internal/eventq/eventq_test.go

## Purpose
Tests event queue delivery, replay, discard, and shutdown behavior.

## Important APIs, Types, And Functions
Tests create `EventQueue[int]` instances and use a helper `collector` goroutine that subscribes, records events until channel close, and closes its subscription.

## Control Flow
Scenarios send events before and after subscription, create multiple subscribers, sleep past discard deadlines, call `Shutdown`, and compare collected/discarded slices.

## State And Persistence
All state is in-memory test channels and slices.

## Dependencies And Integration Points
Uses `testing`, `time`, and `testify/assert`.

## Risks
Timing-based discard tests can be flaky on heavily loaded machines. Tests do not cover concurrent `Shutdown`, subscribe-after-shutdown, or slow subscriber backpressure.

## Test Signals
Good behavioral signal for normal delivery semantics and the pre-subscriber retention queue.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/eventq/eventq_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/failpoint/fail.go -->
# sources/cloud-native/containerd/internal/failpoint/fail.go

## Purpose
Implements configurable failpoints for tests and fault-injection paths, inspired by FreeBSD fail(9).

## Important APIs, Types, And Functions
`Type` enumerates off, error, panic, and delay actions. `Failpoint` stores a function name and ordered `failpointEntry` terms. `NewFailpoint`, `Evaluate`, `DelegatedEval`, and `Marshal` are public. Parsing helpers handle `count*type(arg)->...` term strings.

## Control Flow
Evaluation locks the failpoint, finds the first entry with remaining count, decrements it, unlocks, then executes the selected action. Cascading terms allow off/delay/error/panic sequences.

## State And Persistence
Entry counts are mutable in-memory state and are serialized by `Marshal`. There is no global registry or file persistence.

## Dependencies And Integration Points
Uses parsing primitives from bytes/strings/strconv, synchronization, and time sleeps. It can be embedded at selected code points where callers decide whether to trigger delegated errors.

## Risks
Malformed terms return parse errors, but map iteration in `parseType` relies on non-overlapping prefixes. Delay failpoints block the caller. Panic actions intentionally crash the evaluated path.

## Test Signals
`fail_test.go` covers parse errors, cascading terms, evaluate sequencing, delay duration, panic, and final marshaled counts.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/failpoint/fail.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/failpoint/fail_test.go -->
# sources/cloud-native/containerd/internal/failpoint/fail_test.go

## Purpose
Tests failpoint term parsing, marshaling, and runtime evaluation effects.

## Important APIs, Types, And Functions
`TestParseTerms` checks valid and invalid off/error/panic/delay/cascade strings. `TestEvaluate` executes a sequence containing error, off, delay, and panic terms.

## Control Flow
Parsing tests compare expected error presence and marshal round-trips. Evaluation tests call through an injected function, time the delay, recover from panic, and verify counts reach zero.

## State And Persistence
Tests mutate `Failpoint` entry counts in memory.

## Dependencies And Integration Points
Uses `reflect`, `testing`, and `time`.

## Risks
Delay assertion requires at least one second and can slow/fluctuate tests. No concurrent evaluation test is present.

## Test Signals
Strong coverage for grammar and sequential state transitions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/failpoint/fail_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsmount/fsmount_linux.go -->
# sources/cloud-native/containerd/internal/fsmount/fsmount_linux.go

## Purpose
Wraps the Linux new mount API (`fsopen`, `fsconfig`, `fsmount`, `move_mount`) to mount filesystems while avoiding traditional `mount(2)` option string size limits.

## Important APIs, Types, And Functions
`Fsopen` opens a filesystem context. `SupportsFsmount` detects syscall availability. `Fsmount` configures source/options, creates a mount fd, and moves it to the target. Internal `mountAttrFlags` maps common options to `MOUNT_ATTR_*` flags.

## Control Flow
`Fsmount` opens a context, sets `ro` before source when present, configures key/value and flag options individually, calls `FsconfigCreate`, creates a detached mount, and moves it into place.

## State And Persistence
Creates kernel mount state at the target path. File descriptors are closed after use.

## Dependencies And Integration Points
Depends on `golang.org/x/sys/unix` and containerd `core/mount.Mount`. It integrates with snapshotters or mount code needing large option lists.

## Risks
Linux 5.2+ and privileges are required. Option classification can mis-handle filesystem-specific options if they overlap with mount attribute names. Target path handling and mount cleanup are caller responsibilities.

## Test Signals
No direct tests in this subset. Coverage likely comes from mount integration tests on supporting kernels.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsmount/fsmount_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsverity/fsverity_linux.go -->
# sources/cloud-native/containerd/internal/fsverity/fsverity_linux.go

## Purpose
Provides Linux fs-verity support detection, enablement, and enabled-state checks for files.

## Important APIs, Types, And Functions
`IsSupported(rootPath)` checks kernel version and attempts to enable fs-verity on a temp file under `rootPath`. `IsEnabled(path)` reads inode flags with `FS_IOC_GETFLAGS`. `Enable(path)` builds `fsverityEnableArg` and calls `FS_IOC_ENABLE_VERITY`.

## Control Flow
Support detection requires kernel >= 5.4 and successful enablement on a temp file. Enable chooses block size from page size and filesystem block size, then performs the ioctl.

## State And Persistence
`Enable` permanently marks a file fs-verity-enabled at the filesystem level. `IsSupported` creates and removes a temporary check directory/file.

## Dependencies And Integration Points
Uses kernelversion helpers, `unix` syscalls/ioctls, os/filesystem operations, and unsafe pointer syscall arguments. Integrates with content integrity workflows.

## Risks
Requires Linux kernel/filesystem support and appropriate privileges/capabilities. `Enable` opens files without deferring close in the current implementation, which is a file descriptor leak risk. Once enabled, file contents become immutable.

## Test Signals
`fsverity_test.go` runs root/ext4-dependent checks for enabling and reading enabled status.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsverity/fsverity_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsverity/fsverity_other.go -->
# sources/cloud-native/containerd/internal/fsverity/fsverity_other.go

## Purpose
Provides non-Linux stubs for the fs-verity API.

## Important APIs, Types, And Functions
`IsSupported`, `IsEnabled`, and `Enable` all return errors stating fs-verity is Linux-only.

## Control Flow
Every call exits immediately without side effects.

## State And Persistence
No state and no filesystem mutation.

## Dependencies And Integration Points
Uses only `fmt` and preserves the package API for non-Linux builds.

## Risks
Callers must not assume integrity support is available on non-Linux platforms.

## Test Signals
No direct non-Linux tests in this subset; compile coverage is the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsverity/fsverity_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsverity/fsverity_test.go -->
# sources/cloud-native/containerd/internal/fsverity/fsverity_test.go

## Purpose
Tests enabling fs-verity on supported Linux/ext4 systems and contains helpers to inspect ext4 feature flags.

## Important APIs, Types, And Functions
`TestEnable` creates a temp file, resolves its backing device, checks ext4 verity support with `ext4IsVerity`, calls `Enable`, and checks `IsEnabled`. Helpers parse `/proc/self/mountinfo` and read ext4 superblock feature bits.

## Control Flow
The test requires root, skips non-ext4 or unsupported devices, creates/removes a temp file, and compares runtime support with expected filesystem support.

## State And Persistence
Temporarily creates an fs-verity-enabled file and reads host mount/device metadata.

## Dependencies And Integration Points
Uses `testutil.RequiresRoot`, `unix` major/minor helpers, binary decoding, and OS mountinfo.

## Risks
Highly environment-dependent. It assumes ext4 and direct device readability, and it mutates a file into immutable fs-verity state before removal.

## Test Signals
Good integration signal on properly configured ext4 hosts; otherwise mostly skip behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsverity/fsverity_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsview/mount.go -->
# sources/cloud-native/containerd/internal/fsview/mount.go

## Purpose
Builds read-only `fs.FS` views from containerd mount descriptions without performing kernel mounts when possible.

## Important APIs, Types, And Functions
`View` extends `fs.FS` with `Close`. `FSMounts` resolves the last mount. `resolveMount` handles registered handlers, bind/rbind, overlay, and `format/.../overlay`. Helpers open bind paths, overlay paths, format templates, and template suffixes.

## Control Flow
Mount resolution tries registered handlers first, then built-ins. Bind opens an `os.Root`. Overlay collects upper/lower paths and creates an overlay view. Format overlays evaluate templates with `source`, `mount`, and `overlay` functions that can resolve preceding mounts and optional suffixes.

## State And Persistence
Views own open root/file resources and close them through composed cleanup functions. No persistent filesystem changes are made.

## Dependencies And Integration Points
Depends on `core/mount`, `errdefs`, `os.OpenRoot`, `io/fs`, and text templates. Plugins extend behavior through `Register`.

## Risks
Template execution can open multiple resources and must close on errors. Only known mount types are supported. Overlay path option parsing is simple and may not cover all kernel overlay options.

## Test Signals
`mount_test.go` and `mount_format_test.go` cover bind-last behavior, EROFS plugin views, overlay format templates, suffix handling, and unsupported mount errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsview/mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsview/mount_format_test.go -->
# sources/cloud-native/containerd/internal/fsview/mount_format_test.go

## Purpose
Tests `format/overlay` mount template handling in fsview.

## Important APIs, Types, And Functions
Tests exercise `{{ overlay start end }}`, reversed ranges, `{{ mount i }}`, unsupported mount types, and suffix handling through `FSMounts`.

## Control Flow
Temporary EROFS layers or bind roots are assembled, then format overlay mounts reference preceding mounts. Tests read files, check whiteouts, and expect `errdefs.ErrNotImplemented` for unsupported types.

## State And Persistence
Creates temporary layer files/directories and closes returned views.

## Dependencies And Integration Points
Uses containerd mount types, fsview, EROFS test helpers, `io/fs`, and testify.

## Risks
Many cases depend on EROFS helper availability and plugin registration. Template tests do not cover malformed template syntax exhaustively.

## Test Signals
Strong signal for template-based composition of layered filesystem views.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsview/mount_format_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsview/mount_test.go -->
# sources/cloud-native/containerd/internal/fsview/mount_test.go

## Purpose
Tests fsview mount resolution over bind, EROFS, overlay, and formatted overlay mounts.

## Important APIs, Types, And Functions
Includes helpers for `mkfs.erofs` availability and creating EROFS layers from tar fixtures. Tests call `FSMounts`, `NewOverlayFS`, and read files through returned views.

## Control Flow
The tests create temporary directories/layers, build mount slices, resolve views, read expected paths, and check absence of hidden/whiteouted paths.

## State And Persistence
Creates temporary directories and EROFS layer files. Views are closed with defer.

## Dependencies And Integration Points
Depends on `mkfs.erofs` for some cases, the EROFS fsview plugin import, `tartest`, and containerd mount structs.

## Risks
External command/version dependency causes skips. The test file is integration-heavy and platform-sensitive.

## Test Signals
Good coverage for last-mount selection, EROFS reading, overlay composition, and whiteout/opaque semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsview/mount_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsview/overlay.go -->
# sources/cloud-native/containerd/internal/fsview/overlay.go

## Purpose
Implements a userspace overlay `fs.FS` over ordered layers, including directory merging, whiteouts, opaque directories, and symlink resolution.

## Important APIs, Types, And Functions
`NewOverlayFS` returns an `overlayFS`. `Open`, `Lstat`, and `ReadLink` implement view operations. Internal helpers include `resolve`, `openDirect`, `lstatDirect`, `readlinkDirect`, `hasOpaqueParent`, and `overlayDir.ReadDir`.

## Control Flow
Paths are validated, symlinks are resolved component-by-component across the overlay, then direct open/stat/readlink scans layers from upper to lower, stopping at whiteouts or opaque parents. Directories collect mergeable layers and sorted unique entries.

## State And Persistence
State is only the ordered layer list and per-directory read offsets/cache. No writes are performed.

## Dependencies And Integration Points
Uses `io/fs`, path manipulation, registered xattr/whiteout helpers, and platform-specific overlay helpers. It underpins fsview overlay and formatted EROFS overlay behavior.

## Risks
Symlink resolution is complex and capped at 255 to avoid loops. Layers without `fs.ReadLinkFS` degrade final symlink behavior. Whiteout/opaque detection depends on platform xattrs or registered handlers.

## Test Signals
Overlay tests cover whiteouts, opaque directories, symlink chains, absolute symlinks across layers, directory/file replacement, and EROFS whiteouts.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsview/overlay.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsview/overlay_erofs_test.go -->
# sources/cloud-native/containerd/internal/fsview/overlay_erofs_test.go

## Purpose
Tests overlay semantics over EROFS-backed filesystem layers.

## Important APIs, Types, And Functions
Tests build or open EROFS layers, call `fsview.FSMounts` and `NewOverlayFS`, and inspect files, directory entries, and EROFS whiteout metadata.

## Control Flow
Cases verify base-layer reads, upper-over-lower precedence, whiteout hiding, opaque directory behavior, multiple EROFS layers, and mixed EROFS plus directory upper layers.

## State And Persistence
Creates temporary EROFS images and directories during tests.

## Dependencies And Integration Points
Depends on `mkfs.erofs`, `github.com/erofs/go-erofs`, the fsview EROFS plugin, and tartest fixtures.

## Risks
Tests skip or fail depending on external tool support. Whiteout assertions depend on EROFS stat representation.

## Test Signals
High-value integration coverage for the EROFS plugin plus userspace overlay semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsview/overlay_erofs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsview/overlay_linux.go -->
# sources/cloud-native/containerd/internal/fsview/overlay_linux.go

## Purpose
Provides Linux-specific xattr and whiteout detection used by the userspace overlay filesystem.

## Important APIs, Types, And Functions
`getxattr` reads xattrs from `*os.File` using `unix.Fgetxattr` or delegates to registered handlers. `isOpaque` checks overlay opaque xattrs for value `y`. `isWhiteout` detects character device entries with `Rdev == 0` or delegates to handlers.

## Control Flow
Overlay code calls these helpers while scanning layers. Native Linux files use syscalls first; non-native fs implementations can participate through registered handlers.

## State And Persistence
No state beyond global registered handlers maintained in `register.go`.

## Dependencies And Integration Points
Uses `io/fs`, `os`, `syscall`, `golang.org/x/sys/unix`, and fsview plugin registration.

## Risks
Fixed 256-byte xattr buffer is sufficient for opaque marker values but not general xattr reads. Whiteout detection relies on `syscall.Stat_t` for native files.

## Test Signals
Linux overlay tests exercise `user.overlay.opaque` and whiteout behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsview/overlay_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsview/overlay_linux_test.go -->
# sources/cloud-native/containerd/internal/fsview/overlay_linux_test.go

## Purpose
Tests Linux-specific overlay behavior, especially xattr-based opaque directories and symlink resolution across layers.

## Important APIs, Types, And Functions
Tests create real directories, files, symlinks, and `user.overlay.opaque` xattrs, then call `FSMounts` over overlay lowerdir options and read/stat paths.

## Control Flow
Cases validate upper precedence, relative and absolute symlink targets, chained symlinks, cross-layer symlink target replacement, and file-over-directory replacement under opaque parents.

## State And Persistence
Uses temporary directories and Linux xattrs. No persistent state after test cleanup.

## Dependencies And Integration Points
Uses `golang.org/x/sys/unix` for xattrs, `io/fs`, `os`, `path/filepath`, and containerd mount/fsview APIs.

## Risks
Linux filesystem must support user xattrs. Tests do not directly cover trusted overlay xattrs, which may require elevated privileges.

## Test Signals
Strong signal for the hard parts of overlay path resolution and opaque-directory semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsview/overlay_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsview/overlay_other.go -->
# sources/cloud-native/containerd/internal/fsview/overlay_other.go

## Purpose
Provides non-Linux overlay helper behavior using registered handlers only.

## Important APIs, Types, And Functions
`getxattr` delegates to registered handlers. `isOpaque` checks overlay opaque xattrs through that abstraction. `isWhiteout` recognizes char-device mode only if a handler confirms it.

## Control Flow
Userspace overlay code can still handle non-native filesystem implementations such as EROFS plugins if they register xattr and whiteout capabilities.

## State And Persistence
No state beyond the shared handler registry.

## Dependencies And Integration Points
Uses `io/fs` and `register.go` handlers.

## Risks
Native non-Linux filesystems will not detect overlay whiteouts/opaque dirs unless a handler is registered. Behavior may differ from Linux overlay semantics.

## Test Signals
No direct non-Linux tests in this subset. Compile and plugin-driven EROFS behavior provide indirect signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsview/overlay_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsview/register.go -->
# sources/cloud-native/containerd/internal/fsview/register.go

## Purpose
Defines the plugin extension point for fsview filesystem handlers.

## Important APIs, Types, And Functions
`FSHandler` optionally supplies `HandleMount`, `Getxattr`, and `IsWhiteout`. `Register` appends handlers to the package-level `registered` slice.

## Control Flow
Mount resolution and overlay helpers iterate registered handlers in append order, using handler functions when present.

## State And Persistence
Global in-memory `registered` slice persists for the process. There is no synchronization around registration or lookup.

## Dependencies And Integration Points
Depends on `io/fs` and containerd `mount.Mount`. EROFS fsview plugin registration uses this hook.

## Risks
Registration should happen at init time before concurrent use. Handler order affects which filesystem claims a mount or xattr first.

## Test Signals
Indirect coverage from fsview tests importing the EROFS plugin and resolving EROFS mounts.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/fsview/register.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/kmutex/kmutex.go -->
# sources/cloud-native/containerd/internal/kmutex/kmutex.go

## Purpose
Implements keyed mutual exclusion so callers can serialize operations per resource ID while allowing different keys to proceed concurrently.

## Important APIs, Types, And Functions
`KeyedLocker` exposes `Lock(ctx, key)` and `Unlock(key)`. `New` returns a `keyMutex`. Internally each key maps to `klock`, a one-permit weighted semaphore plus reference count.

## Control Flow
`Lock` creates or finds a per-key semaphore under a map mutex, increments refcount, then waits on the semaphore with caller context. If waiting is canceled, it decrements refcount and removes the key if unused. `Unlock` releases the semaphore and removes the key when the refcount reaches zero.

## State And Persistence
State is an in-memory map from key to semaphore/refcount. It is cleaned up after the last waiter/holder leaves.

## Dependencies And Integration Points
Uses `sync`, `context`, and `golang.org/x/sync/semaphore`. It supports CRI/container operations keyed by container or sandbox ID.

## Risks
Unlocking an unheld key panics. Callers must pair successful `Lock` calls with `Unlock`; calling `Unlock` after a canceled `Lock` would corrupt semantics and panic or release another waiter.

## Test Signals
`kmutex_test.go` covers basic blocking, context cancellation, panic on unlock, same-key serialization, and different-key concurrency.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/kmutex/kmutex.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/kmutex/kmutex_test.go -->
# sources/cloud-native/containerd/internal/kmutex/kmutex_test.go

## Purpose
Tests keyed lock correctness under basic and concurrent scenarios.

## Important APIs, Types, And Functions
`TestBasic` inspects internal refcounts while blocking and canceling waiters. `TestReleasePanic` checks panic on invalid unlock. Stress tests acquire many keys or the same key across goroutines.

## Control Flow
Tests use goroutines, wait loops, random tiny sleeps, and wait groups to exercise contention and cleanup.

## State And Persistence
Mutates `keyMutex.locks` in memory. No persistent state.

## Dependencies And Integration Points
Uses `runtime`, `sync`, `context`, `time`, `randutil`, and testify.

## Risks
Stress loops can be timing-sensitive. Some tests inspect private state and therefore couple tightly to implementation details.

## Test Signals
Good concurrency regression signal for refcount cleanup and cancellation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/kmutex/kmutex_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/kmutex/noop.go -->
# sources/cloud-native/containerd/internal/kmutex/noop.go

## Purpose
Provides a `KeyedLocker` implementation that performs no synchronization.

## Important APIs, Types, And Functions
`NewNoop` returns `*noopMutex`. `Lock` always returns nil and `Unlock` does nothing.

## Control Flow
Callers can swap this implementation where serialization is disabled or unnecessary.

## State And Persistence
No state.

## Dependencies And Integration Points
Depends only on `context` and the local `KeyedLocker` interface.

## Risks
Using it in paths that require real serialization can introduce races. It intentionally does not detect unlock misuse.

## Test Signals
No direct tests. Compile-time interface compatibility is the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/kmutex/noop.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/lazyregexp/lazyregexp.go -->
# sources/cloud-native/containerd/internal/lazyregexp/lazyregexp.go

## Purpose
Delays regexp compilation for package-level regex variables until first use, while compiling immediately during tests to catch invalid patterns early.

## Important APIs, Types, And Functions
`Regexp` stores the pattern string, `sync.Once`, and compiled `*regexp.Regexp`. `New` constructs it. Methods proxy selected regexp operations: `FindStringIndex`, `FindStringSubmatch`, `MatchString`, `ReplaceAll`, and `String`.

## Control Flow
First method call invokes `re.once.Do(re.build)`, compiles with `regexp.MustCompile`, stores the regexp, and clears the source string. In test binaries, `New` compiles immediately.

## State And Persistence
In-memory lazy compiled regexp state. Once compiled, the original pattern string is discarded but `String()` can recover it from the regexp.

## Dependencies And Integration Points
Uses `regexp`, `sync`, `os.Args`, and string suffix checks. Copied from Go's module internals with added methods.

## Risks
Invalid patterns panic at first use in production but at construction in tests. Only a subset of regexp methods is exposed.

## Test Signals
`lazyregexp_test.go` verifies immediate panic for invalid regex under tests and successful matching for a valid pattern.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/lazyregexp/lazyregexp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/lazyregexp/lazyregexp_test.go -->
# sources/cloud-native/containerd/internal/lazyregexp/lazyregexp_test.go

## Purpose
Tests lazy regexp compilation behavior in the test environment.

## Important APIs, Types, And Functions
`TestCompileOnce` has invalid and valid subtests using `New` and `MatchString`.

## Control Flow
The invalid case expects a panic from `New("[")` because tests compile early. The valid case checks a simple match.

## State And Persistence
Only in-memory regexp state.

## Dependencies And Integration Points
Uses Go testing.

## Risks
Does not prove production lazy behavior where invalid regex panics on first use rather than construction. Does not test concurrent first use.

## Test Signals
Confirms the test-mode early compile guard works.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/lazyregexp/lazyregexp_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/nri/config.go -->
# sources/cloud-native/containerd/internal/nri/config.go

## Purpose
Defines containerd's NRI configuration and converts it into options for the NRI adaptation layer.

## Important APIs, Types, And Functions
`Config` includes disable flag, socket/plugin/config paths, plugin timeouts, external-connection disabling, and default validator config. `DefaultConfig`, `toOptions`, and `ConfigureTimeouts` are key functions.

## Control Flow
Default config copies NRI defaults. `toOptions` conditionally appends adaptation options, metrics, default validator, and OpenTelemetry ttrpc interceptors. `ConfigureTimeouts` updates package-level NRI timeout settings when non-zero.

## State And Persistence
Config is usually loaded from TOML/JSON. `ConfigureTimeouts` mutates global timeout settings in the NRI adaptation package.

## Dependencies And Integration Points
Uses local `tomlext.Duration`, `containerd/nri` adaptation, default validator, otel ttrpc, and ttrpc client/server options.

## Risks
Global timeout mutation affects all NRI adaptation behavior in process. Nil default validator disables the built-in validator option.

## Test Signals
No direct tests in this subset; NRI startup and plugin tests elsewhere likely exercise option conversion.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/nri/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/nri/container.go -->
# sources/cloud-native/containerd/internal/nri/container.go

## Purpose
Defines the container metadata interface that containerd domains must implement for NRI, plus common conversion to NRI container protobuf/adaptation structures.

## Important APIs, Types, And Functions
`ContainerStatus`, `Container`, and `LinuxContainer` describe status, labels, args, mounts, hooks, Linux resources/devices, CDI devices, rlimits, user, seccomp, and networking. `commonContainerToNRI` and `containersToNRI` build NRI objects.

## Control Flow
Conversion reads fields from the interface and copies them into an `nri.Container`. Platform-specific files add Linux fields on Linux and omit them elsewhere.

## State And Persistence
No internal state. Converted NRI structures are snapshots of current domain state.

## Dependencies And Integration Points
Depends on `github.com/containerd/nri/pkg/adaptation`. Domain implementations in CRI or other namespaces supply concrete containers.

## Risks
Interface methods may return maps/slices by reference; conversion does not deep-copy them. Nil status would panic when fields are accessed.

## Test Signals
No direct tests in this subset. Conversion is exercised indirectly by NRI lifecycle tests/integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/nri/container.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/nri/container_linux.go -->
# sources/cloud-native/containerd/internal/nri/container_linux.go

## Purpose
Adds Linux-specific container metadata to NRI conversion.

## Important APIs, Types, And Functions
`containerToNRI` calls `commonContainerToNRI`, obtains `LinuxContainer`, and fills `nri.LinuxContainer` fields including namespaces, devices, resources, cgroups path, IO priority, scheduler, net devices, RDT, seccomp profile, sysctls, and seccomp policy.

## Control Flow
The function is selected by the `linux` build tag and attaches Linux payload before returning the NRI container.

## State And Persistence
No internal state; output is a metadata snapshot.

## Dependencies And Integration Points
Uses NRI adaptation helpers, including `nri.Int` for optional OOM score values. Feeds the NRI adaptation layer during container lifecycle calls and synchronization.

## Risks
Assumes `GetLinuxContainer` returns non-nil on Linux. Returned nested structures are not deep-copied.

## Test Signals
No direct tests in this subset; covered by NRI integration on Linux.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/nri/container_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/nri/container_other.go -->
# sources/cloud-native/containerd/internal/nri/container_other.go

## Purpose
Provides non-Linux container-to-NRI conversion without Linux-specific fields.

## Important APIs, Types, And Functions
`containerToNRI` simply returns `commonContainerToNRI(ctr)`.

## Control Flow
Selected for `!linux` builds to keep the API portable.

## State And Persistence
No state.

## Dependencies And Integration Points
Depends on NRI adaptation types through the common conversion.

## Risks
NRI plugins on non-Linux receive no Linux payload. Callers must not expect Linux-specific adjustments to apply.

## Test Signals
No direct tests; compile coverage on non-Linux is the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/nri/container_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/nri/domain.go -->
# sources/cloud-native/containerd/internal/nri/domain.go

## Purpose
Defines the namespace-specific domain abstraction that lets the generic NRI adapter list, update, and evict containers across containerd namespaces.

## Important APIs, Types, And Functions
`Domain` includes listing/getting pods and containers plus update/evict operations. `RegisterDomain` adds a domain to global `domains`. `domainTable` manages registered domains and applies NRI updates/evictions.

## Control Flow
Registration enforces unique namespace names. Listing aggregates all domains. Update/evict resolves a container ID to a domain, wraps the context with that namespace, invokes domain methods, logs failures, and returns failed requests.

## State And Persistence
Global in-memory domain registry protected by a mutex. No persistent data.

## Dependencies And Integration Points
Uses containerd namespaces, errdefs, logging, and NRI adaptation update/eviction types.

## Risks
Container IDs are searched across domains with a TODO noting possible namespace conflicts. `RegisterDomain` logs fatal on duplicate registration. Registry iteration order is map order.

## Test Signals
No direct tests in this subset; NRI synchronization and update flows exercise it indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/nri/domain.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/nri/metrics.go -->
# sources/cloud-native/containerd/internal/nri/metrics.go

## Purpose
Exposes NRI plugin activity metrics for Prometheus-compatible collection.

## Important APIs, Types, And Functions
Global metrics include plugin invocation counter, latency timer, adjustment counter, and active plugin gauge. `nriMetrics` implements `nri.Metrics` with `RecordPluginInvocation`, `RecordPluginLatency`, `RecordPluginAdjustments`, and `UpdatePluginCount`. `getErrorType` normalizes context and gRPC errors.

## Control Flow
Package init registers a `containerd_nri` metrics namespace. Recording methods update labels for plugin, operation, status/error, adjustment type, or plugin count.

## State And Persistence
Metrics are process-global in-memory counters/gauges/histograms exposed by the metrics registry.

## Dependencies And Integration Points
Uses docker/go-metrics, gRPC status/codes, context errors, and the NRI adaptation metrics interface.

## Risks
Global metric registration can conflict in repeated test processes or embedded uses. Label cardinality depends on plugin names and operation strings.

## Test Signals
`metrics_test.go` checks invocation labels, latency histogram sum/count, adjustment counts, and active plugin gauge.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/nri/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/nri/metrics_test.go -->
# sources/cloud-native/containerd/internal/nri/metrics_test.go

## Purpose
Tests NRI metrics recording and Prometheus gathering.

## Important APIs, Types, And Functions
Tests call `newNRIMetrics` methods and helper assertions `assertCounter`, `assertGauge`, and `assertTimer` over `prometheus.DefaultGatherer`.

## Control Flow
Each test records one or more observations, gathers all metric families, finds matching labels, and checks counter/gauge/histogram values.

## State And Persistence
Uses global Prometheus/default metrics state, so values can accumulate across tests.

## Dependencies And Integration Points
Uses prometheus client model, testify, gRPC status/codes, and context errors.

## Risks
Because counters are global, tests use greater-or-equal for counters. Reusing labels across tests or packages can create cross-test coupling.

## Test Signals
Good coverage for error-type normalization and metric updates.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/nri/metrics_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/nri/nri.go -->
# sources/cloud-native/containerd/internal/nri/nri.go

## Purpose
Implements containerd's generic NRI API adapter, forwarding pod/container lifecycle events to NRI plugins and applying plugin-requested updates or evictions through registered domains.

## Important APIs, Types, And Functions
`API` defines lifecycle methods. `local` owns config, adaptation instance, mutex, and per-ID state map. `New`, `Start`, `Stop`, lifecycle methods, `syncPlugin`, `updateFromPlugin`, `applyUpdates`, `evictContainers`, and state helpers implement the adapter.

## Control Flow
If disabled, most methods no-op. Enabled methods serialize under `local.Lock`, convert pod/container metadata to NRI requests, call adaptation APIs, update local state, and apply/evict additional plugin requests. Plugin sync lists all domains, seeds state, calls the plugin sync callback, and applies returned updates.

## State And Persistence
In-memory `state` tracks Created/Running/Stopped/Removed to avoid duplicate stop/remove events. No state persists across restart; plugin sync rebuilds from domains.

## Dependencies And Integration Points
Integrates containerd version info, logging, NRI adaptation, domain registry, metrics/config options, and namespace-specific domain implementations.

## Risks
All lifecycle calls are serialized, so slow plugins or domain updates can block other NRI events. Several update/eviction failures are logged and ignored by design. `NotifyContainerExit` launches a goroutine using the caller context.

## Test Signals
No direct tests in this subset. Metrics tests and domain/conversion integration elsewhere provide indirect coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/nri/nri.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/nri/sandbox.go -->
# sources/cloud-native/containerd/internal/nri/sandbox.go

## Purpose
Defines pod sandbox metadata interfaces and common conversion to NRI pod sandbox objects.

## Important APIs, Types, And Functions
`PodSandbox` exposes domain, ID, name, UID, namespace, labels, annotations, runtime handler, Linux sandbox, PID, and IPs. `LinuxPodSandbox` exposes namespaces and Linux resource/cgroup fields. `commonPodSandboxToNRI` and `podSandboxesToNRI` convert values.

## Control Flow
Common conversion copies platform-neutral fields; platform-specific files add Linux fields on Linux.

## State And Persistence
No state. Output is a metadata snapshot for NRI plugin calls.

## Dependencies And Integration Points
Depends on NRI adaptation types and is used by `nri.go` lifecycle and sync requests.

## Risks
Returned maps/slices are not deep-copied. Nil Linux sandbox on Linux would panic in the Linux conversion.

## Test Signals
No direct tests in this subset; exercised by NRI lifecycle integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/nri/sandbox.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/nri/sandbox_linux.go -->
# sources/cloud-native/containerd/internal/nri/sandbox_linux.go

## Purpose
Adds Linux pod sandbox fields to NRI conversion.

## Important APIs, Types, And Functions
`podSandboxToNRI` calls `commonPodSandboxToNRI`, obtains `LinuxPodSandbox`, and fills namespaces, pod overhead/resources, cgroup parent/path, and resources.

## Control Flow
Selected on Linux builds and attaches the Linux payload before returning.

## State And Persistence
No state. Produces a snapshot for plugin requests.

## Dependencies And Integration Points
Uses NRI adaptation Linux pod sandbox types and feeds NRI Run/Update/Post lifecycle calls.

## Risks
Assumes `GetLinuxPodSandbox` is non-nil on Linux. No deep copy of nested resource structures.

## Test Signals
No direct tests in this subset; covered through NRI Linux integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/nri/sandbox_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/nri/sandbox_other.go -->
# sources/cloud-native/containerd/internal/nri/sandbox_other.go

## Purpose
Provides non-Linux pod sandbox conversion without Linux-specific fields.

## Important APIs, Types, And Functions
`podSandboxToNRI` returns `commonPodSandboxToNRI(pod)`.

## Control Flow
Build-tagged for `!linux`.

## State And Persistence
No state.

## Dependencies And Integration Points
Keeps the NRI package portable on non-Linux platforms.

## Risks
Non-Linux NRI plugins receive only platform-neutral pod metadata.

## Test Signals
No direct tests; compile coverage is the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/nri/sandbox_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/oom/oom.go -->
# sources/cloud-native/containerd/internal/oom/oom.go

## Purpose
Defines the Linux OOM watcher interface used to monitor cgroup v2 out-of-memory events for containers.

## Important APIs, Types, And Functions
`EventFunc` is a callback receiving a container ID. `Interface` exposes `Add(containerID, pid, fn)` and `Stop(containerID)`.

## Control Flow
Implementations start monitoring the cgroup for a process PID and invoke callbacks when `oom_kill` events increase.

## State And Persistence
Interface only; implementation state is in `watcher.go`.

## Dependencies And Integration Points
Linux build tag. Integrates CRI/container lifecycle monitoring with cgroup v2 memory events.

## Risks
The interface still takes a PID because cgroups v2 package does not expose the cgroup path directly, as noted by TODO.

## Test Signals
`watcher_test.go` validates the concrete implementation under root/cgroup-v2 conditions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/oom/oom.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/oom/utils.go -->
# sources/cloud-native/containerd/internal/oom/utils.go

## Purpose
Contains Linux helpers for opening inotify watches on cgroup v2 memory event files and parsing cgroup stat files.

## Important APIs, Types, And Functions
`memoryEventNonBlockFD` creates an inotify fd and watches `memory.events` and `cgroup.events`. `getCgroup2Path` maps a PID to `/sys/fs/cgroup/<group>`. `readKVStatsFile`, `parseKV`, and `parseUint` read key/value stats.

## Control Flow
Watcher setup opens nonblocking inotify, adds two modify watches, and returns an `os.File`. Stat parsing scans fields and treats negative values as zero for compatibility with cgroups parsing.

## State And Persistence
Creates kernel inotify watch state held by the returned fd. No file writes.

## Dependencies And Integration Points
Uses cgroups v3 cgroup2 helpers, `unix` syscalls, and cgroup v2 files.

## Risks
Requires unified cgroup v2, readable cgroup files, and valid PID mapping. Inotify setup must close the fd on partial failure.

## Test Signals
Covered indirectly by `watcher_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/oom/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/oom/watcher.go -->
# sources/cloud-native/containerd/internal/oom/watcher.go

## Purpose
Implements cgroup v2 OOM event monitoring for Linux containers.

## Important APIs, Types, And Functions
`New` returns an `oomWatchers` registry. `Add` creates a per-container `watcher`, opens cgroup event fd, and starts monitoring. `Stop` stops a watcher. `watcher.start` reads inotify events and detects increases in `memory.events` `oom_kill`.

## Control Flow
`Add` resolves cgroup path from PID, opens inotify watches, checks duplicate container IDs, starts a goroutine, and stores it. The goroutine reads events, reloads memory stats, invokes callback on increased kills, exits on fd close or deleted cgroup, and reports errors on `errCh`.

## State And Persistence
In-memory map of container ID to watcher and kernel inotify fd state. It does not persist events.

## Dependencies And Integration Points
Uses `errdefs`, Linux inotify, cgroup v2 files, and the OOM interface.

## Risks
`Stop` does not remove the watcher from the map, so repeated add after stop may still see existing entry. `stop` waits on `errCh`; goroutine exit must happen after fd close. Root/cgroup permissions are required.

## Test Signals
`watcher_test.go` launches a constrained `dd` process in a cgroup and asserts one OOM callback.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/oom/watcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/oom/watcher_test.go -->
# sources/cloud-native/containerd/internal/oom/watcher_test.go

## Purpose
Integration-tests the Linux cgroup v2 OOM watcher.

## Important APIs, Types, And Functions
`TestWatcher` creates a cgroup v2 manager, starts `dd`, adds it to the cgroup, registers an OOM callback, sets memory/swap limits, and waits for an OOM kill. Helpers skip unsupported environments.

## Control Flow
The test requires root, unified cgroup v2, and `dd`. It constrains memory below the workload size, waits for the process to be killed, then uses `require.Eventually` to observe callback count.

## State And Persistence
Creates a temporary cgroup and process, plus watcher inotify state. Cleanup stops watchers and waits for the process.

## Dependencies And Integration Points
Uses containerd cgroups v3, `testutil.RequiresRoot`, exec, atomics, and testify.

## Risks
Highly host-dependent and can be slow/flaky due to kernel scheduling and OOM timing. Requires careful cleanup of process/cgroup resources.

## Test Signals
Strong real-kernel signal for watcher functionality when prerequisites are met.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/oom/watcher_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/pprof/plugin.go -->
# sources/cloud-native/containerd/internal/pprof/plugin.go

## Purpose
Registers containerd's pprof and expvar HTTP handler plugin.

## Important APIs, Types, And Functions
`init` registers a plugin of type `plugins.HTTPHandler` with ID `pprof`. `newHandler` returns an `http.Server` with `/debug/vars` and standard `/debug/pprof` endpoints.

## Control Flow
Plugin initialization constructs a serve mux and returns it to the plugin system. The server sets `ReadHeaderTimeout` to five minutes.

## State And Persistence
Registers global plugin metadata at init. Runtime state is the HTTP server and handlers.

## Dependencies And Integration Points
Uses expvar, net/http/pprof, containerd plugin registry, and plugin type constants.

## Risks
Exposes profiling and expvar data wherever the containerd HTTP handler plugin is served, so endpoint access control is important outside this file.

## Test Signals
No direct tests in this subset. Plugin registration is covered by containerd plugin initialization integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/pprof/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/randutil/randutil.go -->
# sources/cloud-native/containerd/internal/randutil/randutil.go

## Purpose
Provides crypto-random integer helpers analogous to `math/rand` functions.

## Important APIs, Types, And Functions
`Int63n`, `Int63`, `Intn`, and `Int` read from `crypto/rand.Reader` through `rand.Int`.

## Control Flow
`Int63n` generates a random big integer below `n`, panicking on error. The other helpers delegate to it with max bounds or type conversions.

## State And Persistence
No state.

## Dependencies And Integration Points
Uses `crypto/rand`, `math`, and `math/big`. Used by tests such as keyed mutex stress tests to avoid deterministic math/rand global state.

## Risks
`Int63n` inherits `rand.Int` behavior and panics for invalid bounds or entropy errors. Converting to `int` may narrow on 32-bit platforms.

## Test Signals
No direct tests. Indirect use in concurrency tests provides light exercise.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/randutil/randutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/registrar/registrar.go -->
# sources/cloud-native/containerd/internal/registrar/registrar.go

## Purpose
Implements a thread-safe one-to-one reservation table between names and keys.

## Important APIs, Types, And Functions
`Registrar` owns `nameToKey` and `keyToName` maps under a mutex. `NewRegistrar`, `Reserve`, `ReleaseByName`, and `ReleaseByKey` manage mappings. `ReservedErr` reports conflicts and implements `Conflict()`.

## Control Flow
`Reserve` rejects empty fields, returns nil for idempotent same mapping, errors if either side is already reserved for a different counterpart, and otherwise inserts both map entries. Release methods delete both directions if present.

## State And Persistence
All reservations are in-memory only.

## Dependencies And Integration Points
Uses `sync` and `fmt`. The `Conflict()` marker can integrate with containerd error classification.

## Risks
No lookup API is provided. Error messages expose existing names/keys. Callers must release reservations on lifecycle cleanup to avoid leaks.

## Test Signals
`registrar_test.go` covers reservation, idempotence, conflicts, releases, re-reservation, and same-name/key mapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/registrar/registrar.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/registrar/registrar_test.go -->
# sources/cloud-native/containerd/internal/registrar/registrar_test.go

## Purpose
Tests registrar reservation and release semantics.

## Important APIs, Types, And Functions
`TestRegistrar` uses a new registrar and checks `Reserve`, `ReleaseByKey`, `ReleaseByName`, and `ReservedErr`.

## Control Flow
The test reserves two mappings, repeats an idempotent reservation, tries conflicting mappings, releases both directions, then reserves new mappings including identical name/key.

## State And Persistence
Mutates in-memory registrar maps.

## Dependencies And Integration Points
Uses Go testing and testify assertions.

## Risks
No concurrent access test is present despite the type being concurrency-safe.

## Test Signals
Good unit signal for core conflict and release behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/registrar/registrar_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/tomlext/toml_v2_util.go -->
# sources/cloud-native/containerd/internal/tomlext/toml_v2_util.go

## Purpose
Defines a TOML/JSON-friendly duration wrapper around `time.Duration`.

## Important APIs, Types, And Functions
`Duration` is a named `time.Duration`. `UnmarshalText` parses Go duration strings. `MarshalText` serializes using `time.Duration.String`. `ToStdTime` and `FromStdTime` convert to/from standard duration.

## Control Flow
Text unmarshalling receives bytes from TOML decoding, parses them, and stores the converted duration.

## State And Persistence
Values are persisted in configuration as strings such as `5s` or `1m0s`.

## Dependencies And Integration Points
Uses `time`. NRI config uses this type for plugin registration/request timeouts.

## Risks
Only Go duration syntax is accepted; plain integer TOML durations are not. String formatting may normalize input representation.

## Test Signals
No direct tests in this subset. Indirect coverage through config parsing tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/tomlext/toml_v2_util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/truncindex/truncindex.go -->
# sources/cloud-native/containerd/internal/truncindex/truncindex.go

## Purpose
Provides Docker-compatible lookup of full IDs by unique prefixes using a Patricia trie.

## Important APIs, Types, And Functions
Errors include `ErrEmptyPrefix`, `ErrIllegalChar`, `ErrNotExist`, and `ErrAmbiguousPrefix`. `TruncIndex` owns a trie and full-ID set. `NewTruncIndex`, `Add`, `Delete`, `Get`, and `Iterate` are public.

## Control Flow
Add validates non-empty/no-space/unique IDs and inserts into both map and trie. Delete requires an exact full ID. Get visits the prefix subtree and returns the only matching full ID or ambiguity/not-exist errors. Iterate locks and visits all trie entries.

## State And Persistence
In-memory trie and map protected by an RW mutex. No persistence.

## Dependencies And Integration Points
Uses `github.com/tchap/go-patricia/v2/patricia`. Used wherever containerd wants shorthand ID resolution.

## Risks
`Iterate` holds the write lock and warns handlers not to call public methods, which would deadlock. Add is not rollback-safe if trie insert failed after map insert, though failures are unlikely.

## Test Signals
No direct tests listed in this subset. Behavior likely covered by Docker-derived or container ID lookup tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/truncindex/truncindex.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/userns/idmap.go -->
# sources/cloud-native/containerd/internal/userns/idmap.go

## Purpose
Handles user-namespace UID/GID mapping translation and string serialization.

## Important APIs, Types, And Functions
`User` stores UID/GID. `IDMap` stores OCI `LinuxIDMapping` slices. `RootPair`, `ToHost`, `Marshal`, and `Unmarshal` are methods. Helpers include `toHost`, `safeSum`, `serializeLinuxIDMapping`, and `deserializeLinuxIDMapping`.

## Control Flow
Mapping translation finds the mapping range containing a container ID, checks overflow, and computes host ID. Nil maps mean identity mapping. Marshal joins `container:host:size` entries; Unmarshal splits comma-separated strings and appends parsed mappings.

## State And Persistence
`IDMap` holds in-memory mapping slices that can be serialized to strings for metadata/config storage.

## Dependencies And Integration Points
Uses OCI runtime spec Linux ID mappings. It is copied/customized from Moby idtools.

## Risks
`Unmarshal` appends to existing slices rather than clearing them. Zero-size mappings deserialize successfully but map no IDs. Overflow handling returns sentinel invalid IDs.

## Test Signals
`idmap_test.go` covers root mapping, host translation, overflow, marshal/unmarshal, invalid strings, and identity mapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/userns/idmap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/userns/idmap_test.go -->
# sources/cloud-native/containerd/internal/userns/idmap_test.go

## Purpose
Tests user namespace ID mapping translation, overflow handling, and serialization.

## Important APIs, Types, And Functions
Tests cover `RootPair`, `ToHost`, `Marshal`, `Unmarshal`, and helper behavior through table-driven mappings.

## Control Flow
Cases build `IDMap` values, translate container users to host users, expect errors for unmapped/overflow IDs, compare marshaled strings, and parse valid/invalid mapping strings.

## State And Persistence
Only in-memory mappings and serialized strings.

## Dependencies And Integration Points
Uses OCI runtime spec mapping structs and testify.

## Risks
Tests focus on deterministic mappings and do not cover concurrent access, because `IDMap` is not synchronized.

## Test Signals
Good coverage for mapping boundaries and serialization contracts.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/userns/idmap_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/wintls/wintls_other.go -->
# sources/cloud-native/containerd/internal/wintls/wintls_other.go

## Purpose
Provides non-Windows stubs for Windows certificate-store TLS setup.

## Important APIs, Types, And Functions
`CertResource` aliases `io.Closer`. `NoopCertResource` implements `Close`. `SetupTLSFromWindowsCertStore` returns nil TLS config, nil cert pool, a noop resource, and nil error.

## Control Flow
Non-Windows callers can invoke the API without build failures, but receive no TLS material.

## State And Persistence
No state.

## Dependencies And Integration Points
Uses context, crypto/tls, crypto/x509, and io for API compatibility.

## Risks
Returning nil error with nil TLS config requires callers to interpret platform behavior correctly. It is a no-op, not an unsupported error.

## Test Signals
No direct tests. Compile coverage is the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/wintls/wintls_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/wintls/wintls_windows.go -->
# sources/cloud-native/containerd/internal/wintls/wintls_windows.go

## Purpose
Builds a TLS client/server configuration from a certificate and private key in the Windows certificate store.

## Important APIs, Types, And Functions
`WindowsCertResource` owns a `certtostore.WinCertStore` and `windows.CertContext`, with `Close` freeing both. `SetupTLSFromWindowsCertStore` opens the "My" store, finds a certificate by common name, obtains its private key, builds a cert pool and `tls.Certificate`, and returns cleanup resource.

## Control Flow
Each failure path closes/free resources acquired so far. Successful setup filters the leaf out of intermediate chains, attaches leaf raw bytes plus intermediates to TLS certificate, and returns caller-managed cleanup.

## State And Persistence
Opens Windows certificate store handles and certificate contexts. No certificate is persisted or modified.

## Dependencies And Integration Points
Uses `github.com/google/certtostore`, Windows syscalls, and Go crypto/tls/x509. Integrates Windows certificate management with containerd TLS configuration.

## Risks
Context parameter is currently unused. `Close` returns only the last close/free error if both fail. Certificate lookup by common name may be ambiguous depending on store contents.

## Test Signals
No direct tests in this subset; Windows integration/manual tests are needed.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/wintls/wintls_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/apparmor/apparmor.go -->
# sources/cloud-native/containerd/pkg/apparmor/apparmor.go

## Purpose
Exposes a portable public `HostSupports` helper for AppArmor availability.

## Important APIs, Types, And Functions
`HostSupports` delegates to platform-specific `hostSupports`.

## Control Flow
On Linux it checks kernel/AppArmor/parser/container state; on non-Linux it returns false.

## State And Persistence
State is handled by platform implementations, including Linux `sync.Once` caching.

## Dependencies And Integration Points
The package is used by runtime/security profile code deciding whether AppArmor profiles can be used.

## Risks
This wrapper hides platform-specific caching and environment assumptions. Callers should treat false as "do not use AppArmor".

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/apparmor/apparmor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/apparmor/apparmor_linux.go -->
# sources/cloud-native/containerd/pkg/apparmor/apparmor_linux.go

## Purpose
Detects AppArmor host support on Linux.

## Important APIs, Types, And Functions
`hostSupports` uses package globals `appArmorSupported` and `checkAppArmor sync.Once`.

## Control Flow
The first call checks `/sys/kernel/security/apparmor`, ensures environment variable `container` is empty to avoid docker-in-docker, checks `/sbin/apparmor_parser`, then reads `/sys/module/apparmor/parameters/enabled` and requires leading `Y`.

## State And Persistence
Detection result is cached in memory for the process.

## Dependencies And Integration Points
Uses `os` filesystem and environment checks. Derived from runc/libcontainer AppArmor detection with extra parser and container checks.

## Risks
Hard-coded parser path may miss distributions with a different path. The one-time cache can be stale in tests or after environment changes.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/apparmor/apparmor_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/apparmor/apparmor_unsupported.go -->
# sources/cloud-native/containerd/pkg/apparmor/apparmor_unsupported.go

## Purpose
Provides non-Linux AppArmor support detection.

## Important APIs, Types, And Functions
`hostSupports` returns false under a `!linux` build tag.

## Control Flow
Immediate false result.

## State And Persistence
No state.

## Dependencies And Integration Points
Keeps the AppArmor package portable.

## Risks
No AppArmor behavior is available on non-Linux builds.

## Test Signals
No direct tests; compile coverage is the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/apparmor/apparmor_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/compression/benchmark_test.go -->
# sources/cloud-native/containerd/pkg/archive/compression/benchmark_test.go

## Purpose
Benchmarks decompression performance for gzip, zstd, and optional external gzip accelerators.

## Important APIs, Types, And Functions
`BenchmarkDecompression` downloads test data, expands it to 32/64/128/256 MiB, compresses it with helper functions, and benchmarks `testDecompress` with zstd, pure Go gzip, `igzip`, and `unpigz` when present.

## Control Flow
The benchmark mutates package global `gzipPath` to force decompressor selection and restores it after sub-benchmarks.

## State And Persistence
Downloads data from the network during benchmark execution and mutates `gzipPath` process-global state temporarily.

## Dependencies And Integration Points
Uses net/http, exec.LookPath, testing benchmarks, and package compression helpers.

## Risks
Network dependency makes benchmarks non-hermetic. Global `gzipPath` mutation means benchmarks should not run concurrently with other compression tests.

## Test Signals
Performance-only signal; not intended as correctness coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/compression/benchmark_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/compression/compression.go -->
# sources/cloud-native/containerd/pkg/archive/compression/compression.go

## Purpose
Detects, compresses, and decompresses archive streams using uncompressed, gzip, and zstd formats, with optional external gzip decompressors.

## Important APIs, Types, And Functions
`Compression` enum includes `Uncompressed`, `Gzip`, `Zstd`, and `Unknown`. `DetectCompression`, `DecompressStream`, `CompressStream`, and `Extension` are public. Internals include pooled buffered readers, zstd skippable-frame detection, gzip external command detection, and `cmdStream`.

## Control Flow
Decompression peeks at the first 10 bytes, detects magic, then returns a wrapper around raw buffered input, gzip reader/external command pipe, or zstd reader. Compression returns an appropriate write closer. Gzip command detection prefers `igzip`, then `unpigz`, unless disabled by env vars.

## State And Persistence
Uses package-global `sync.Once` and `gzipPath` cache plus a `sync.Pool` of buffered readers. No persistent files are created.

## Dependencies And Integration Points
Uses Go gzip, klauspost zstd, external `igzip`/`unpigz`, containerd logging, and archive unpack/pull paths.

## Risks
Map iteration in `DetectCompression` is safe because magic values do not overlap, but order is not deterministic. `writeCloserWrapper.Close` ignores closer errors. External command stderr is surfaced only after read/pipe completion. Gzip path is detected once and cached despite later env/path changes.

## Test Signals
Fuzzer coverage calls `DecompressStream` on arbitrary bytes. Benchmarks cover performance and external gzip selection. Correctness tests may exist outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/compression/compression.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/compression/compression_fuzzer_test.go -->
# sources/cloud-native/containerd/pkg/archive/compression/compression_fuzzer_test.go

## Purpose
Fuzz-tests decompression stream detection and reader construction against arbitrary input bytes.

## Important APIs, Types, And Functions
`FuzzDecompressStream` passes random byte slices through `DecompressStream(bytes.NewReader(data))` and ignores the result.

## Control Flow
The fuzzer stresses detection, peeking, gzip/zstd reader creation, and error handling without reading returned decompressed streams.

## State And Persistence
No persistent state; may touch package-global gzip detection if inputs look gzip-like and path detection initializes.

## Dependencies And Integration Points
Uses Go fuzzing support, bytes reader, and compression package APIs.

## Risks
Because it does not read from successful returned readers, it may miss panics or hangs during actual decompression consumption. External gzip command paths could complicate fuzz environments.

## Test Signals
Useful input-hardening signal for `DecompressStream` setup paths, but not full decompression correctness.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/compression/compression_fuzzer_test.go -->
