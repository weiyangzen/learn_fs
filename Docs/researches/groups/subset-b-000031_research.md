# Research: subset-b-000031

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/errutil/errutil.go -->
## sources/cloud-native/buildkit/util/errutil/errutil.go

Purpose: improves registry and remote pull error readability by expanding containerd `ErrUnexpectedStatus` responses into Docker error payloads or bounded response-body details.

Important APIs/types/functions: `WithDetails(error) error` is the package entry point. It detects `remoteserrors.ErrUnexpectedStatus`, tries to decode `docker.Errors`, and otherwise wraps the status with `verboseUnexpectedStatusError`. `formattedDockerError` formats one or many Docker errors and includes string `Detail` fields. Both wrappers implement `Unwrap` so callers can still use error inspection.

Control flow: nil errors pass through. Unexpected status bodies first take the structured Docker error path; failed or empty Docker decoding falls back to body detail extraction. `verboseUnexpectedStatusError.Error` prefers JSON `details`, otherwise prints the raw body with a 256-byte cap and truncation count.

State/persistence: stateless; only formats in-memory error body bytes. Dependencies: `encoding/json`, containerd remotes/docker error types, `pkg/errors`-compatible wrapping via standard `errors`.

Integration points: used near image registry resolution/fetch code to make daemon/client errors actionable without losing the underlying containerd status. Risks: body truncation can hide useful tail data; structured Docker errors with non-string details only show base error text; `formattedDockerError.Error` appends a trailing newline for multi-error cases. Test signals: no local test in this subset, so behavior depends on containerd error-shape compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/errutil/errutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/estargz/labels.go -->
## sources/cloud-native/buildkit/util/estargz/labels.go

Purpose: generates snapshot labels needed by stargz snapshotter remote/lazy-pull integration for eStargz layers.

Important API: `SnapshotLabels(ref string, descs []ocispecs.Descriptor, targetIndex int) map[string]string` extracts TOC digest and uncompressed size annotations from the target descriptor, records remote reference and target digest, and builds a comma-separated layer digest list.

Control flow: if the descriptor slice is too short for the target index it returns nil; otherwise it iterates from `targetIndex` forward and appends layer digests until `containerd/pkg/labels.Validate` reports the label would exceed constraints. It trims the final comma before returning.

State/persistence: stateless label map creation. Dependencies: containerd labels validation, stargz snapshotter annotation keys, OCI descriptors.

Integration points: output labels are consumed by containerd snapshotters under `containerd.io/snapshot/remote/stargz.*`. Risks: the bounds check uses `len(descs) < targetIndex`, so `targetIndex == len(descs)` would panic; expected callers likely provide valid indices. Skipping layer digests is accepted but can reduce remote snapshotter performance. Test signals: no direct test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/estargz/labels.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/flightcontrol/cached.go -->
## sources/cloud-native/buildkit/util/flightcontrol/cached.go

Purpose: adds indefinite per-key memoization on top of `flightcontrol.Group`, preserving singleflight-style synchronization while caching successful results and optionally non-context errors.

Important API/type: `CachedGroup[T]` exposes `CacheError bool` and `Do(ctx, key, fn)`. Internal `result[T]` stores cached value/error pairs.

Control flow: `Do` delegates to the embedded `Group` so concurrent callers for the same key share execution. Inside the group callback it checks the cache under mutex. Successful cached values return immediately. Cached errors return only when `CacheError` is true; otherwise the function reruns. After `fn`, errors matching the current context cause are never cached. Nil errors and, when enabled, non-context errors are stored in `cache`.

State/persistence: in-memory map protected by mutex; no eviction and therefore unsuitable for unbounded or long-lived key spaces. `CacheError` is documented as immutable after first use. Dependencies: `context`, `sync`, `github.com/pkg/errors`.

Integration points: wraps the local `Group[T]` from `flightcontrol.go`. Risks: indefinite retention, mutable `CacheError`, and generic values that may themselves be mutable/shared. Test signals: `cached_test.go` covers successful memoization, default non-caching of errors, error caching, and cancellation-error exclusion.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/flightcontrol/cached.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/flightcontrol/cached_test.go -->
## sources/cloud-native/buildkit/util/flightcontrol/cached_test.go

Purpose: validates `CachedGroup` cache semantics.

Important tests: `TestCached` confirms distinct keys get distinct values, repeat successful calls bypass `fn`, and default errors do not poison cache. `TestCachedError` sets `CacheError` and verifies the first non-context error is reused, while a deadline/context-cause error does not cache.

Control flow/state: tests use booleans and repeated calls to observe whether callback execution occurs. The cancellation case uses `context.WithTimeoutCause`, waits for the context to be done, then calls with the same key and a callback that should run.

Dependencies/integration: `testify/require`, `pkg/errors`, Go context deadlines. Risks covered: accidental caching of transient cancellation and incorrect `CacheError` behavior. Gaps: no high-concurrency test for cached group itself; underlying concurrency is covered in `flightcontrol_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/flightcontrol/cached_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/flightcontrol/flightcontrol.go -->
## sources/cloud-native/buildkit/util/flightcontrol/flightcontrol.go

Purpose: implements BuildKit's singleflight-like coordination with cancellation-aware shared contexts and progress replay for callers joining an in-flight operation.

Important APIs/types: `Group[T].Do(ctx, key, fn)` synchronizes by key. Internal `call[T]` owns result/error, ready/cleaned channels, waiter contexts, a shared context, and progress state. `sharedContext` implements context behavior whose done channel closes only when all waiter contexts are done. `progressState` stores latest progress by ID and fans raw progress to attached writers.

Control flow: `Do` loops over `g.do` and retries on internal `errRetry`, with randomized exponential backoff capped at 15 seconds. `g.do` creates a `call` if no key exists or waits on the existing one. `call.wait` attaches the caller's progress writer, appends a cancelable child context, starts `run` once, and returns either the shared result, the caller cancellation cause, or `errRetry` after cleanup when a previous errored call must be removed. `run` executes `fn` with the shared context, stores result/error, closes `ready`, and closes progress writer on exit.

State/persistence: in-memory map of active calls protected by `Group.mu`; entries are deleted only after `ready`. Progress state stores latest item per progress ID and live raw writers. No persistence. Dependencies: BuildKit `util/progress`, `sync`, `slices`, `math/rand`, `pkg/errors`.

Integration points: used for deduplicating expensive BuildKit operations while allowing multiple solve callers to observe progress. The custom context's `Value` bridges both progress context and the first active caller context.

Risks: complex cancellation races; errored calls trigger retry rather than sharing failure; backoff uses `time.Sleep` without observing caller cancellation during sleep; `Deadline` returns the first active deadline rather than the earliest. Progress replay stores latest-by-ID only, so historical intermediate states are not preserved. Test signals: `flightcontrol_test.go` covers sharing, one/both caller cancellation, race retry, contention, and massive parallel failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/flightcontrol/flightcontrol.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/flightcontrol/flightcontrol_test.go -->
## sources/cloud-native/buildkit/util/flightcontrol/flightcontrol_test.go

Purpose: stress-tests `Group` semantics around deduplication and cancellation.

Important tests: `TestNoCancel` expects two callers on one key to invoke `fn` once. `TestCancelOne` cancels one caller while another completes. `TestCancelRace` exercises retry after a cancellation race. `TestCancelBoth` verifies all callers cancel, then later calls can run fresh for both same and different keys. `TestContention` creates 100,000 calls. `TestMassiveParallel` sends 1000 failing waiters and checks retry timeout is not surfaced spuriously.

State/control flow: uses `errgroup`, atomic counters, context cancellation causes, and timed sleeps to expose synchronization behavior.

Dependencies/integration: `testify`, `x/sync/errgroup`, `pkg/errors`. Risks covered: duplicate execution, leaked failed calls, cancellation propagation, and contention. Gaps: progress replay behavior is not directly tested here.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/flightcontrol/flightcontrol_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/gitutil/git_cli.go -->
## sources/cloud-native/buildkit/util/gitutil/git_cli.go

Purpose: wraps `git` CLI execution with BuildKit-specific isolation, environment control, retry fallbacks, and configurable command execution/streams.

Important APIs/types: `GitCLI` stores binary, exec hook, extra args, working tree/git dir, SSH settings, stream factory, and host config opt-in. Options include `WithGitBinary`, `WithExec`, `WithArgs`, `WithDir`, `WithWorkTree`, `WithGitDir`, `WithSSHAuthSock`, `WithSSHKnownHosts`, `WithHostGitConfig`, and `WithStreams`. `Run(ctx,args...)` executes a git command and returns stdout bytes.

Control flow: `Run` builds `exec.Cmd`, adds `-c protocol.file.allow=user`, optional work-tree/git-dir and args, captures stdout/stderr, optionally tees streams, and constructs a restricted environment. By default it disables system/global/user git config via `GIT_CONFIG_NOSYSTEM`, `HOME=os.DevNull`, and `GIT_CONFIG_GLOBAL=os.DevNull`; host config variables are copied only with `WithHostGitConfig`. Proxy variables and SSH auth socket are forwarded. On errors it wraps stderr, handles context cause specially, retries without `--depth=1` for shallow/depth complaints, and retries `fetch` without a commit refspec for "not our ref" or unadvertised-object failures.

State/persistence: immutable-ish client config; `New` shallow-copies and clones args. No repository state is changed except whatever git command performs. Dependencies: `os/exec`, BuildKit git helpers, `pkg/errors`.

Integration points: used by BuildKit Git source resolver. Risks: stream setup defers `stdout.Close()`/`stderr.Close()` without nil checks if a custom stream factory returns nil; retry string matching depends on git stderr wording; `WithExec` uses `context.TODO()` in `CommandContext` and relies entirely on the hook for cancellation. Test signals: `git_cli_test.go` covers SSH command construction and git config environment isolation/opt-in.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/gitutil/git_cli.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/gitutil/git_cli_helpers.go -->
## sources/cloud-native/buildkit/util/gitutil/git_cli_helpers.go

Purpose: supplies convenience methods for repository paths and cleaned git output.

Important APIs: `Dir()` returns explicit dir or work tree. `WorkTree(ctx)` returns configured `workTree` or runs `git rev-parse --show-toplevel`. `GitDir(ctx)` returns configured `gitDir` or appends `.git` to the work tree. `clean([]byte,error)` keeps first output line, strips single quotes, and trims error newlines.

Control flow/state: methods delegate to `GitCLI.Run`, so they inherit environment isolation and retry behavior. No persistence.

Dependencies/integration: used by Git source code needing stable repository directories. Risks: `GitDir` assumes standard non-bare `.git` directory when not configured; `clean` removes all single quotes, which is useful for shell-quoted git output but lossy for unusual paths. Test signals: no direct helper test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/gitutil/git_cli_helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/gitutil/git_cli_test.go -->
## sources/cloud-native/buildkit/util/gitutil/git_cli_test.go

Purpose: verifies Git CLI environment and SSH helper behavior.

Important tests: `TestGetGitSSHCommandUsesConfigPath` checks default strict-host-key disabling and known-hosts override. `TestGitCLIConfigEnv` uses `WithExec` to inspect `cmd.Env`, confirming default isolation from host config and explicit `WithHostGitConfig` forwarding of HOME/XDG/Windows/global/system config variables.

Control flow/state: environment variables are set with `t.Setenv`; no actual git command is run because `WithExec` returns nil.

Risks covered: accidental host config leakage in daemon-side git operations and missing host config in client-side inspection. Gaps: no tests for depth/refspec retry, stream nil behavior, or context cancellation.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/gitutil/git_cli_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/gitutil/git_commit.go -->
## sources/cloud-native/buildkit/util/gitutil/git_commit.go

Purpose: validates whether a string is a lowercase Git object hash suitable for SHA-1 or SHA-256 commit IDs.

Important API: `IsCommitSHA(str string) bool` returns true only for length 40 or 64 and characters `0-9` or `a-f`.

Control flow/state: simple length and rune scan; stateless.

Integration points: used by Git fetch retry logic to identify commit refspecs and by URL/source handling that needs to distinguish refs from hashes. Risks: uppercase hex hashes are rejected even though Git may accept them; function name says commit SHA but validates only hash shape, not object existence/type. Test signals: `git_commit_test.go` covers valid SHA-1/SHA-256 lengths and invalid lengths/chars.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/gitutil/git_commit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/gitutil/git_commit_test.go -->
## sources/cloud-native/buildkit/util/gitutil/git_commit_test.go

Purpose: table-tests `IsCommitSHA`.

Important coverage: accepts 40-character SHA-1 and 64-character SHA-256 lowercase hex strings. Rejects empty, too-short/long, punctuation, and `z` characters at valid lengths.

Dependencies: `testify/assert`.

Risk/test signal: confirms current strict lowercase behavior but does not document whether uppercase should be accepted. No integration with actual git object lookup.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/gitutil/git_commit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/gitutil/git_url.go -->
## sources/cloud-native/buildkit/util/gitutil/git_url.go

Purpose: parses BuildKit Git remotes, including standard URLs and SCP-like SSH syntax, into a normalized `GitURL` with BuildKit fragment metadata.

Important APIs/types: constants for `http`, `https`, `ssh`, `git`; errors `ErrUnknownProtocol`, `ErrInvalidProtocol`; `GitURL` with scheme/host/path/user/query/options/remote; `GitURLOpts{Ref,Subdir}`. `ParseURL`, `IsGitTransport`, `FromURL`, and internal `fromSCPStyleURL` are the main functions.

Control flow: a protocol regexp detects `scheme://`; unsupported schemes error as invalid. Standard URLs go through `net/url.Parse` and `FromURL`, which strips fragment and raw query from `Remote` while preserving query separately. Non-standard inputs are parsed via `sshutil.ParseSCPStyleURL`. `parseOpts` splits fragment on the first `:` into ref and normalized subdir using `path.Join`.

State/persistence: stateless parser. Dependencies: `net/url`, BuildKit `sshutil`, `path`, `regexp`.

Integration points: used by Git source frontend/resolver to separate clone remote from BuildKit ref/subdir hints. Risks: query params are preserved in `Query` but excluded from `Remote`, so callers must intentionally handle query metadata. Fragment `ref:subdir` cannot represent refs containing a colon. Test signals: `git_url_test.go` covers protocol variants, credentials, ports, queries, fragments, SCP paths, invalid protocol, and case-insensitive schemes.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/gitutil/git_url.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/gitutil/git_url_test.go -->
## sources/cloud-native/buildkit/util/gitutil/git_url_test.go

Purpose: validates Git URL parsing coverage.

Important tests: standard HTTP/HTTPS, SSH URL, SCP-like SSH, absolute SCP paths, `git://`, username/password, ports, fragments with ref/subdir, query retention, uppercase schemes, and invalid `httpx://`.

Control flow/state: table test compares parsed fields and stringified user info; it does not assert the `Remote` field directly.

Dependencies/integration: `testify/require`, `net/url`. Risks covered: protocol detection and BuildKit fragment parsing. Gaps: no direct tests for `IsGitTransport`, `Remote` query stripping, empty fragments, or refs/subdirs containing special separators.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/gitutil/git_url_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/gitutil/gitobject/parse.go -->
## sources/cloud-native/buildkit/util/gitutil/gitobject/parse.go

Purpose: parses raw Git commit/tag objects, extracts headers, message, signatures, signed payload, actors, and verifies object checksums.

Important APIs/types: `GitObject{Type,Headers,Message,Signature,SignedData,Raw}`, `Actor`, `Commit`, `Tag`. Functions/methods: `Parse`, `Checksum`, `VerifyChecksum`, `ToCommit`, `ToTag`, and internal `parseActor`.

Control flow: `Parse` identifies tags by `object ` prefix; otherwise treats input as commit. It reads headers until the blank line, handles multi-line commit `gpgsig` and `gpgsig-sha256` by collecting signature lines while excluding them from `SignedData`, and for tags treats PGP/SSH signature blocks after the message as detached signature text. It validates required headers by type. `Checksum` prefixes raw data with `commit <len>\0` or `tag <len>\0`. `VerifyChecksum` chooses SHA-1 or SHA-256 by expected length. Converters copy first/slice header values into typed structs. `parseActor` uses last angle brackets and optional Unix timestamp plus numeric timezone.

State/persistence: in-memory parsing only. Dependencies: crypto SHA-1/SHA-256, hex, time, `pkg/errors`.

Integration points: used by signature verification and Git provenance/trust code. Risks: object type inference is narrow; commit SSH signatures in headers are collected like PGP but test coverage focuses on PGP; malformed actor timezone hour/minute digits are ignored if `Atoi` fails, yielding zero offsets. Test signals: `parse_test.go` covers signed commit, signed tag, checksums, conversion, and actor edge cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/gitutil/gitobject/parse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/gitutil/gitobject/parse_test.go -->
## sources/cloud-native/buildkit/util/gitutil/gitobject/parse_test.go

Purpose: validates raw Git object parsing, signed-data extraction, checksum verification, and actor parsing.

Important tests: `TestParseGitObject` parses a real signed merge commit with two parents and a signed tag, verifies SHA-1 checksums, signature block normalization, `SignedData` exclusion/inclusion rules, header maps, `ToCommit`, `ToTag`, and wrong-type conversion errors. `TestParseActor` covers normal actors, missing/invalid timestamps, malformed timezone, missing brackets, extra spaces, and names containing `<`.

Dependencies: `crypto/sha1`, `testify/require`, time zones.

Risk/test signal: strong fixtures for PGP commit/tag formats and actor parsing. Gaps: no SHA-256 object fixture, no SSH signature fixture, no invalid required-header tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/gitutil/gitobject/parse_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/gitutil/gitsign/gitsign.go -->
## sources/cloud-native/buildkit/util/gitutil/gitsign/gitsign.go

Purpose: verifies signatures extracted from parsed Git objects, supporting both OpenPGP and SSH signature formats.

Important APIs/types: `Signature{PGPSignature,SSHSignature}`, `VerifySignature(obj,pubKeyData,policy)`, `ParseSignature`, `parseSignatureBlock`, plus private PGP/SSH verification helpers.

Control flow: `VerifySignature` requires `obj.Signature`, parses it, dispatches to PGP verification over `obj.SignedData` using `pgpsign.VerifyArmoredDetachedSignature`, or SSH verification using `sshsig`. SSH verification enforces version 1, SHA-256/SHA-512 hash, namespace `git`, parses authorized-key public data, and verifies over signed data. `ParseSignature` detects PEM armor headers.

State/persistence: stateless. Dependencies: ProtonMail OpenPGP packet types, `hiddeco/sshsig`, BuildKit `gitobject` and `pgpsign`, `x/crypto/ssh`.

Integration points: combines `gitobject.Parse` output with key material from trust policy/source configuration. Risks: no local tests; unsupported SSH hash/namespace rejection is intentional but may fail future Git signature variants; PGP policy behavior is delegated to `pgpsign`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/gitutil/gitsign/gitsign.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/gogo/proto/enum.go -->
## sources/cloud-native/buildkit/util/gogo/proto/enum.go

Purpose: compatibility helpers for enum JSON marshaling/unmarshaling formerly supplied by gogo/protobuf.

Important APIs: `MarshalJSONEnum(map[int32]string,value)` returns a JSON string of the symbolic enum name or decimal number if unknown. `UnmarshalJSONEnum(map[string]int32,data,enumName)` accepts quoted symbolic JSON or numeric JSON.

Control flow: unmarshal checks `data[0] == '"'` for string mode, decodes and map-lookups symbolic values, otherwise decodes an int32. Errors mention enum name and bad representation.

State/persistence: stateless. Dependencies: `encoding/json`, `strconv`, `pkg/errors`.

Integration points: used by generated or migrated proto enum code in BuildKit that still expects gogo-compatible helpers. Risks: assumes `data` is non-empty and can panic on empty input; unknown numeric values are accepted. Test signals: no local test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/gogo/proto/enum.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/grpcerrors/grpcerrors.go -->
## sources/cloud-native/buildkit/util/grpcerrors/grpcerrors.go

Purpose: converts BuildKit errors to/from gRPC status errors while preserving status codes, stack traces, typed error details, unknown protobuf details, and contextual messages.

Important APIs/types: `TypedError` and `TypedErrorProto` contracts; `ToGRPC(ctx,err)`, `FromGRPC(err)`, `Code(err)`, `WrapCode(err,code)`, `AsGRPCStatus(err)`. Internal wrappers include `grpcStatusError`, `withCodeError`, and unwrap interfaces.

Control flow: `ToGRPC` starts from existing status or `status.New(Code(err), err.Error())`, fixes mismatched codes, expands status message when outer error has more context, collects stack traces and typed errors through all single/multi unwraps, and adds details as JSON-encoded `Any` values using containerd `typeurl`. `Code` prioritizes internal/resource-exhausted BuildKit errdefs, explicit `Code`, `GRPCStatus`, unwrap chains, joined errors, and context errors. `FromGRPC` decodes status details, splits stack and typed detail protos from unknown details, rebuilds a `grpcStatusError`, wraps stacks, applies typed `WrapError`, and enables stack handling.

State/persistence: no persistence; transforms error object graphs. Dependencies: gRPC status/codes, protobuf Any, containerd typeurl, BuildKit errdefs/stack/logging.

Integration points: server/client interceptors and APIs returning rich BuildKit errors. Risks: typed details must be registered with typeurl; joined errors pick the first non-OK/non-Unknown code; details are JSON-marshaled into Any values rather than binary proto wire format. Test signals: `grpcerrors_test.go` covers unknown-detail preservation, typed error preservation, code/status extraction, context mapping, and contextual message retention.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/grpcerrors/grpcerrors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/grpcerrors/grpcerrors_test.go -->
## sources/cloud-native/buildkit/util/grpcerrors/grpcerrors_test.go

Purpose: regression tests for rich gRPC error conversion.

Important tests: `TestFromGRPCPreserveUnknownTypes` checks unknown `Any` details survive decode and roundtrip. `TestFromGRPCPreserveTypes` joins an unknown-detail status with a typed solve error and verifies both survive. `TestCode` covers explicit `Code`, `GRPCStatus`, wrapped errors, joined errors, and context errors. `TestAsGRPCStatus` covers nil, direct, wrapped, joined, and absent statuses. `TestToGRPCMessage` avoids duplicate code prefixes and keeps extra outer context.

Dependencies: solver errdefs, gRPC status/codes, protobuf Any, standard `errors.Join`, `pkg/errors`, `testify`.

Risks covered: loss of unknown/typed detail and degraded messages across gRPC. Gaps: no direct stack trace assertion and no failure path for unregistered typed details.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/grpcerrors/grpcerrors_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/grpcerrors/intercept.go -->
## sources/cloud-native/buildkit/util/grpcerrors/intercept.go

Purpose: gRPC server/client interceptors that automatically encode outgoing BuildKit errors and decode incoming gRPC errors.

Important APIs: `UnaryServerInterceptor`, `StreamServerInterceptor`, `UnaryClientInterceptor`, `StreamClientInterceptor`.

Control flow: server unary/stream handlers pass errors through `ToGRPC` and call `stack.Helper` when errors are present. Unary server defends against invalid conversion returning nil by logging or panicking under `BUILDKIT_DEBUG_PANIC_ON_ERROR`, then restoring the original error. Client unary decodes with `FromGRPC`; stream client currently returns `ToGRPC(ctx, err)` for streamer errors.

State/persistence: stateless middleware except environment-variable panic behavior. Dependencies: gRPC, BuildKit stack, `log`, `os`.

Integration points: plugged into BuildKit gRPC server/client setup. Risks: stream client uses `ToGRPC` rather than `FromGRPC`, which is notable because unary client decodes remote errors; may be intentional for local streamer setup errors but deserves care. Test signals: indirect through `grpcerrors_test.go`; no interceptor-specific tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/grpcerrors/intercept.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/grpcutil/encoding/proto/proto.go -->
## sources/cloud-native/buildkit/util/grpcutil/encoding/proto/proto.go

Purpose: registers a custom gRPC protobuf codec with the standard proto codec name that avoids resetting messages on unmarshal and supports vtprotobuf fast paths.

Important APIs/types: package `init` calls `encoding.RegisterCodecV2(codec{})`. `codec.Marshal`, `codec.Unmarshal`, and `codec.Name` implement gRPC encoding. `vtprotoMessage` captures vtprotobuf methods.

Control flow: marshal/unmarshal switch on vtproto, proto v2, and proto v1 adapted to v2. Small messages use plain byte slices; larger messages use `grpc/mem.DefaultBufferPool`. Unmarshal materializes buffer slices then calls `UnmarshalVT` or `proto.UnmarshalOptions{Merge:true}` to avoid reset semantics and align vt behavior.

State/persistence: global codec registration at init; pooled buffers are freed after materialization. Dependencies: gRPC encoding/mem, protobuf adaptors, default proto import for name override.

Integration points: affects all gRPC calls using the registered proto codec in this process. Risks: merge/no-reset behavior can surprise callers expecting zeroed reused messages; overriding default codec name is process-wide; vtproto implementations must honor buffer contracts. Test signals: no local tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/grpcutil/encoding/proto/proto.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/imageutil/config.go -->
## sources/cloud-native/buildkit/util/imageutil/config.go

Purpose: resolves an image reference to its manifest digest and configuration blob, using content cache, resolver fetcher, platform selection, and temporary leases.

Important APIs/types: `ContentCache` combines containerd content interfaces. Lease globals `CancelCacheLeases`, `AddLease` manage deferred lease cleanup. `ResolveToNonImageError` describes policy mutation to non-image refs. `Config(ctx,str,resolver,cache,leaseManager,p)` is the main entry point. Helpers: `childrenConfigHandler`, `DetectManifestMediaType`, `DetectManifestBlobMediaType`.

Control flow: `Config` parses the reference and platform matcher, optionally creates a temporary 5-minute lease and defers its cleanup registration. If the reference is digest-pinned, it probes cache for an existing manifest whose source label matches and detects media type. Missing media type triggers `resolver.Resolve`. It creates a fetcher, rejects Docker schema1 manifests with conflict, builds handlers to fetch/retry, apply distribution source labels, and traverse only one matching manifest/config, dispatches them, then reads and returns config blob data with the resolved manifest digest.

State/persistence: writes/fetches blobs into content cache; creates leases and stores deferred cleanup funcs in package globals until `CancelCacheLeases`. Dependencies: containerd content/images/leases/remotes/docker/reference/platforms, BuildKit contentutil/leaseutil/resolver handlers, OCI specs.

Integration points: image source resolution, frontend metadata, cache warming. Risks: global lease list uses `context.TODO` on cancellation; temporary lease deletion is intentionally delayed and may retain blobs until cleanup; media type detection reads whole blob into memory; unknown child media types hard-error. Test signals: `config_test.go` covers multi-platform index selection from cache and non-matching platform errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/imageutil/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/imageutil/config_test.go -->
## sources/cloud-native/buildkit/util/imageutil/config_test.go

Purpose: tests `Config` platform selection and cache-first behavior for multi-platform images.

Important test: `TestConfigMultiplatform` builds fake amd64/386/arm64 manifests and an OCI index. Only amd64 manifest/config are in cache; resolver/fetcher reads from the same test cache and errors if missing. It verifies amd64 config is returned without remote fetch and arm/v7 reports containerd not found. The test shuffles manifests to avoid order assumptions.

Support types: `testCache` implements minimal content manager/provider/ingester pieces; `testResolver` implements resolver/fetcher; `makeDesc` and `Add` create digest-addressed descriptors.

Risks covered: wrong platform selection from index and accidental fetch of unavailable manifests. Gaps: schema1 rejection, lease behavior, digest source-label validation, media type ambiguity, and resolver errors are not tested here.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/imageutil/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/iohelper/helper.go -->
## sources/cloud-native/buildkit/util/iohelper/helper.go

Purpose: small IO adapter utilities for closing composition, write counting, and ReaderAt-to-ReadCloser conversion.

Important APIs/types: `NopWriteCloser`, `WithCloser(r, closer)`, `WriteCloser{io.WriteCloser, CloseFunc}`, `Counter`, `ReaderAtCloser`, and `ReadCloser(in)`.

Control flow: composed closers call the wrapped closer first and the additional close func second, returning wrapped first error with second error embedded in message or returning the second error. `Counter.Write` increments byte count under mutex and reports full write. `ReadCloser` wraps a `ReaderAtCloser` in a section reader over `Size`.

State/persistence: `Counter` keeps in-memory count protected by mutex. Dependencies: standard `io`, `sync`, `pkg/errors`.

Integration points: content streaming, progress/log counting, wrappers around content `ReaderAt`. Risks: `WithCloser` and `WriteCloser.Close` always invoke both closers but only preserve first error structurally; `ReadCloser` assumes stable `Size()` and random access. Test signals: no local tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/iohelper/helper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/leaseutil/manager.go -->
## sources/cloud-native/buildkit/util/leaseutil/manager.go

Purpose: helper layer for containerd leases, including temporary lease creation, adoption into an existing lease, and namespace-scoped lease manager wrapper.

Important APIs/types: `WithLease(ctx,manager,opts...)`, `NewLease`, `LeaseRef{Discard,Adopt}`, `MakeTemporary`, `WithNamespace`, and `Manager` methods implementing lease manager operations with a fixed namespace.

Control flow: `WithLease` is a no-op if the context already carries a lease; otherwise it creates one and returns a delete callback. `NewLease` applies random ID and default one-hour expiration before caller opts. `Adopt` lazily lists resources once, requires a current lease in target context, adds each resource to the current lease, discards empty leases immediately, and asynchronously discards adopted non-empty source leases. `Discard` uses `context.WithoutCancel`.

State/persistence: creates/deletes/adopts real containerd lease records and resources. `LeaseRef` caches listed resources and first error under `sync.Once`. Dependencies: containerd leases/namespaces, `time`, `pkg/errors`.

Integration points: image/content cache lifetime management. Risks: asynchronous discard errors are ignored; resource list is cached even if adoption happens much later; namespace wrapper assumes all calls should be forced into its namespace. Test signals: no local tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/leaseutil/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/cniprovider/bridge.go -->
## sources/cloud-native/buildkit/util/network/cniprovider/bridge.go

Purpose: Linux-only auto-generated CNI bridge provider that can use BuildKit-shipped CNI plugin binaries or a configured plugin directory.

Important API/functions: `NewBridge(opt)`, `bridgeByName`, `removeBridge`.

Control flow: `NewBridge` looks for `buildkit-cni-bridge`, `buildkit-cni-loopback`, `buildkit-cni-host-local`, and `buildkit-cni-firewall`; if all exist it builds plugin dirs and uses their discovered binary names. Otherwise it requires `opt.BinaryDir/bridge`. It creates a CNI conflist with loopback, bridge IPAM, and firewall, forcing firewall backend to iptables under RootlessKit. It takes init lock, checks for an existing bridge in detached netns when needed, creates CNI handle, schedules bridge removal only if it created it, cleans old namespaces, initializes network, pre-fills namespace pool, and returns provider.

State/persistence: may create bridge device, CNI config state, network namespaces under `opt.Root`, and pool entries. Dependencies: `containerd/go-cni`, netlink, BuildKit logging/network.

Integration points: selected by `netproviders` for mode `bridge` or `BUILDKIT_NETWORK_BRIDGE_AUTO`. Risks: plugin discovery is all-or-nothing; bridge existence check relies on netns context; bridge removal on close can affect other users if ownership detection is wrong. Test signals: no direct bridge test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/cniprovider/bridge.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/cniprovider/cni.go -->
## sources/cloud-native/buildkit/util/network/cniprovider/cni.go

Purpose: shared CNI network provider implementation with namespace pooling, setup/removal, hostname args, network sampling hooks, and provider close lifecycle.

Important APIs/types: `Opt`, `New(opt)`, `cniProvider`, `cniNS`, `newCNIPool`, `cniProvider.New`, `cniProvider.Close`, `cniNS.Set`, `Close`, `Sample`, `release`.

Control flow: `New` validates config and binary paths, builds CNI options including loopback/min network count on non-Windows and config file/conflist, creates CNI handle in detached netns if necessary, cleans old namespaces, builds pool, initializes one namespace, and asynchronously fills pool. `New` on provider uses the pool for empty hostnames or Windows; custom hostnames get a fresh non-pooled namespace. `newNS` creates a native namespace, runs CNI setup (serially in detached netns), extracts the host veth name, and primes sampling baseline. `Close` returns namespaces to pool or releases resources. `release` removes CNI config, unmounts, and deletes namespace.

State/persistence: creates OS network namespaces under root, CNI runtime state, pooled namespace objects, optional veth sample offsets. Dependencies: containerd go-cni, BuildKit identity/logging/network/netpool, OCI specs, OpenTelemetry trace.

Integration points: `netproviders` default CNI mode; executor calls `Set` on OCI specs and `Sample` for resource metrics. Risks: pooled namespaces must be reset correctly via CNI; custom-hostname namespaces are not pooled; Windows lacks cleanup mechanism per comment; setup uses `context.TODO` for CNI calls after namespace creation. Test signals: Linux dialing/sampling-adjacent behavior is covered in `cni_linux_test.go`; generic pooling is tested in `netpool`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/cniprovider/cni.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/cniprovider/cni_linux.go -->
## sources/cloud-native/buildkit/util/network/cniprovider/cni_linux.go

Purpose: Linux-specific CNI namespace sampling, RootlessKit detached-netns entry, and namespace-aware outbound dialing.

Important functions: `(*cniNS).sample`, `readFileAt`, `withDetachedNetNSIfAny`, `DialContext`, `dialer`, `isLoopbackHost`, `dialInNS`, `dialInNetNS`.

Control flow: `sample` opens `/sys/class/net/<veth>/statistics`, reads tx/rx counters with `openat`, parses int64 values, and updates `prevSample`. Detached-netns wrapper checks `$ROOTLESSKIT_STATE_DIR/netns` with `os.OpenRoot` and runs the callback via CNI `netns.WithNetNSPath` with context marker. `DialContext` captures current namespace for loopback DNS and dials inside the target namespace with `FallbackDelay=-1` to avoid Happy Eyeballs goroutine namespace escapes. Resolver `Dial` uses caller namespace for loopback resolver addresses and target namespace otherwise.

State/persistence: reads sysfs counters; temporarily switches OS thread netns during dial/listen operations. Dependencies: CNI plugins netns package, syscall, Go net resolver.

Integration points: `cniNS` implements `network.Dialer` for proxy egress and resource sampling. Risks: namespace switching requires careful OS-thread pinning handled by dependency; sysfs veth disappearance returns nil sample; custom resolver logic is subtle around loopback DNS. Test signals: `cni_linux_test.go` targets dial namespace escape prevention, in-namespace dialing, loopback DNS, and loopback host classification.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/cniprovider/cni_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/cniprovider/cni_linux_test.go -->
## sources/cloud-native/buildkit/util/network/cniprovider/cni_linux_test.go

Purpose: Linux-only tests for namespace-aware dialing and resolver behavior.

Important tests: `TestDialContextDoesNotEscapeNetNS` creates an isolated namespace and host loopback listeners, then expects dialing `localhost` from target ns to fail rather than escaping. `TestDialContextDialsInsideNetNS` brings up loopback inside namespace and expects success. `TestLoopbackDNSUsesCallerNetNS` verifies resolver dial to a loopback address uses caller namespace. `TestIsLoopbackHost` covers IPv4/IPv6 loopback and non-loopback host strings.

State/control flow: helper `createTestNetNS` requires root, unshares/mounts netns on a locked goroutine, and cleans up. Tests use timeouts to avoid hanging.

Risks covered: Go resolver/Happy Eyeballs namespace escape, loopback DNS handling. Gaps: CNI setup/removal and sysfs sampling are not directly tested.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/cniprovider/cni_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/cniprovider/cni_nolinux.go -->
## sources/cloud-native/buildkit/util/network/cniprovider/cni_nolinux.go

Purpose: non-Linux stubs for sampling and detached netns handling.

Important functions: `(*cniNS).sample` always returns nil sample and nil error. `withDetachedNetNSIfAny` simply invokes the callback.

State/persistence: none. Dependencies: resource sample type and context.

Integration points: lets shared `cni.go` compile on non-Linux platforms. Risks: no network metrics on non-Linux. Test signals: no local non-Linux tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/cniprovider/cni_nolinux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/cniprovider/createns_linux.go -->
## sources/cloud-native/buildkit/util/network/cniprovider/createns_linux.go

Purpose: Linux network namespace file lifecycle for CNI provider.

Important functions: `cleanOldNamespaces`, `unshareAndMountNetNS`, `createNetNS`, `setNetNS`, `unmountNetNS`, `deleteNetNS`.

Control flow: `cleanOldNamespaces` scans `<root>/net/cni` and asynchronously releases leftover namespaces through CNI remove/unmount/delete. `createNetNS` creates a bind-mount target file, launches a goroutine locked to an OS thread, unshares `CLONE_NEWNET`, bind-mounts `/proc/self/task/<tid>/ns/net`, and returns the path. `setNetNS` mutates OCI spec with a Linux network namespace path. Cleanup ignores `EINVAL`/`ENOENT` unmount and missing files.

State/persistence: creates bind-mounted namespace files under BuildKit root. Dependencies: containerd OCI helper, unix/syscall, BuildKit logger.

Integration points: used by `cniProvider.newNS` and tests. Risks: goroutine intentionally leaves thread locked so runtime terminates it; cleanup is asynchronous and warnings only; root privileges/capabilities are required. Test signals: exercised by `cni_linux_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/cniprovider/createns_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/cniprovider/createns_unix.go -->
## sources/cloud-native/buildkit/util/network/cniprovider/createns_unix.go

Purpose: unsupported non-Linux, non-Windows CNI namespace stubs.

Important functions: `createNetNS`, `setNetNS`, `unmountNetNS`, and `deleteNetNS` all return unsupported errors; `cleanOldNamespaces` is a no-op.

State/persistence: none. Dependencies: OCI spec type and `pkg/errors`.

Integration points: compile-time platform fallback for Unix systems without implemented netns support. Risks: selecting CNI provider on these platforms will fail at namespace creation rather than provider construction. Test signals: no local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/cniprovider/createns_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/cniprovider/createns_windows.go -->
## sources/cloud-native/buildkit/util/network/cniprovider/createns_windows.go

Purpose: Windows Host Compute Network namespace lifecycle for CNI provider.

Important functions: `createNetNS`, `setNetNS`, `unmountNetNS`, `deleteNetNS`, `cleanOldNamespaces`.

Control flow: creates an HCN guest namespace and returns its ID. `setNetNS` ensures `specs.Windows` and `WindowsNetwork` exist, then sets `NetworkNamespace`. Unmount is a no-op. Delete looks up HCN namespace by ID and deletes it. Old namespace cleanup is not implemented.

State/persistence: creates/deletes Windows HCN namespaces. Dependencies: Microsoft hcsshim/hcn, OCI specs.

Integration points: Windows CNI provider support. Risks: comment in shared provider notes Windows pool cleanup is limited; stale HCN namespaces may remain after crashes. Test signals: no local Windows tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/cniprovider/createns_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/host.go -->
## sources/cloud-native/buildkit/util/network/host.go

Purpose: non-Windows host-network provider and namespace implementation.

Important APIs/types: `NewHostProvider`, `host`, `hostNS`. `host.New` returns `hostNS`; `hostNS.Set` applies containerd `oci.WithHostNamespace(specs.NetworkNamespace)`; `DialContext` uses the default `net.Dialer`.

State/persistence: no state, no cleanup. Dependencies: containerd OCI spec helper, resource sample type, Go net.

Integration points: default fallback on Unix when CNI is not configured, explicit `pb.NetMode_HOST`, and proxy egress mode. Risks: hostname parameter is ignored; `Sample` has no metrics; unavailable on Windows. Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/host.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/netpool/pool.go -->
## sources/cloud-native/buildkit/util/network/netpool/pool.go

Purpose: generic reusable pool for expensive network namespace-like resources with target prefill and delayed shrink.

Important APIs/types: `Opt[T]`, `Pool[T]`, `New`, `Fill`, `Get`, `Put`, `Discard`, `Close`.

Control flow: `Fill` creates and returns new resources until `actualSize >= targetSize` or an error occurs. `Get` pops an available resource or calls `getNew`. `Put` appends available resource with last-used time; if actual size exceeds target it schedules cleanup after five minutes. `cleanupToTargetSize` releases oldest available entries older than the grace period. `Close` marks closed, releases currently available resources, and later returned resources are released in `Put`.

State/persistence: in-memory counts and available slice protected by mutex. Underlying `Release` may delete OS resources. Dependencies: BuildKit logger, `sync`, `time`, `pkg/errors`.

Integration points: CNI and proxy network namespace pools. Risks: checked-out resources are not forcibly released on `Close` until returned; cleanup timer ignores release errors; `actualSize` accounting depends on every checked-out item eventually being `Put` or `Discard`. Test signals: `pool_test.go` covers reuse and close behavior for available/returned values.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/netpool/pool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/netpool/pool_test.go -->
## sources/cloud-native/buildkit/util/network/netpool/pool_test.go

Purpose: validates basic netpool lifecycle semantics.

Important tests: `TestPoolReusesReturnedValue` ensures `Put` then `Get` returns the same item and `New` is called once. `TestPoolCloseReleasesAvailableAndReturnedValues` closes while an item is checked out, then verifies returning it releases it and future `Get` errors.

State/control flow: uses integer resources and slices to record releases.

Risks covered: resource reuse, close behavior, checked-out item release after close. Gaps: no delayed shrink/grace-period test, no new/release error propagation under race.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/netpool/pool_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/netproviders/network.go -->
## sources/cloud-native/buildkit/util/network/netproviders/network.go

Purpose: selects and returns BuildKit network providers and optional exec proxy provider based on configured mode and platform support.

Important API/type: `Opt{CNI,Mode}` and `Providers(opt) (map[pb.NetMode]network.Provider, network.ProxyProvider, resolvedMode string, err error)`.

Control flow: supports `cni`, `host`, `bridge`, `auto`, and empty mode. `bridge` maps resolved mode to `cni`. Auto uses `BUILDKIT_NETWORK_BRIDGE_AUTO=true` to prefer bridge, else CNI config path if present, else platform fallback. It always registers `UNSET` default and `NONE`; registers proxy provider on supported platforms with UNSET and optional HOST egress; registers HOST if available.

State/persistence: may instantiate CNI/bridge/proxy providers that create namespaces, bridges, pools, and certs. Dependencies: solver protobuf net modes, CNI provider, proxy provider, BuildKit network, `os`, `strconv`.

Integration points: worker/executor network setup. Risks: provider construction has side effects before full map return; auto fallback differs by platform; proxy egress providers include only default and host, not none. Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/netproviders/network.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/netproviders/network_linux.go -->
## sources/cloud-native/buildkit/util/network/netproviders/network_linux.go

Purpose: Linux implementation of bridge-provider selection.

Important function: `getBridgeProvider(opt)` delegates to `cniprovider.NewBridge`.

State/persistence: side effects are in CNI bridge provider creation. Integration: enables `Mode: "bridge"` and bridge auto mode on Linux.

Risks/test signals: no logic beyond delegation; no local test.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/netproviders/network_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/netproviders/network_nobridge.go -->
## sources/cloud-native/buildkit/util/network/netproviders/network_nobridge.go

Purpose: non-Linux bridge-provider fallback.

Important function: `getBridgeProvider` returns an error naming `runtime.GOOS`.

State/persistence: none. Integration: prevents unsupported bridge mode outside Linux. Test signals: no local test.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/netproviders/network_nobridge.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/netproviders/network_unix.go -->
## sources/cloud-native/buildkit/util/network/netproviders/network_unix.go

Purpose: non-Windows host-provider and fallback selection.

Important functions: `getHostProvider` returns `network.NewHostProvider`; `getFallback` logs a warning and returns host provider with resolved mode `"host"`.

State/persistence: none beyond logging. Integration: default network mode on Unix when CNI config is absent. Risks: host fallback may be less isolated than users expect; warning is the only signal. Test signals: no local test.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/netproviders/network_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/netproviders/network_windows.go -->
## sources/cloud-native/buildkit/util/network/netproviders/network_windows.go

Purpose: Windows host-provider and fallback selection.

Important functions: `getHostProvider` reports no host support. `getFallback` logs and returns none provider with empty resolved mode.

State/persistence: none beyond logging. Integration: Windows defaults to null networking when CNI is absent. Risks: resolved mode empty may need careful UI/reporting handling. Test signals: no local test.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/netproviders/network_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/network.go -->
## sources/cloud-native/buildkit/util/network/network.go

Purpose: defines common network provider, namespace, and dialer contracts used by executors, CNI, host, none, and proxy implementations.

Important types: `Provider` embeds `io.Closer` and creates `Namespace`. `Namespace` embeds `io.Closer`, mutates OCI specs with `Set`, and optionally returns resource samples. `NamespaceOptions` is currently empty. `Dialer` supplies namespace-aware `DialContext`.

State/persistence: interface-only file. Dependencies: context, io, net, OCI specs, BuildKit resource sample types.

Integration points: central abstraction for worker networking and proxy egress. Risks: empty `NamespaceOptions` suggests future extension; not every namespace implements `Dialer`, so proxy provider checks dynamically. Test signals: implementations are tested elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/network.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/none.go -->
## sources/cloud-native/buildkit/util/network/none.go

Purpose: null network provider for disabled/no network mode.

Important APIs/types: `NewNoneProvider`, `none`, `noneNS`. `Set`, `Close`, and `Sample` are no-ops/nil.

State/persistence: no state. Dependencies: OCI specs and resource sample types.

Integration points: registered as `pb.NetMode_NONE` and Windows fallback. Risks: does not actively remove default network from specs by itself; relies on executor/runtime default spec construction to be networkless. It also does not implement `Dialer`, so cannot be proxy egress. Test signals: no local test.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/none.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/proxy.go -->
## sources/cloud-native/buildkit/util/network/proxy.go

Purpose: defines exec proxy policy/provider interfaces and captures HTTP material metadata for reproducible/source-policy-aware builds.

Important types/APIs: `ProxyPolicy`, `ProxyConfig`, `ProxyProvider`, `ProxyNamespace`, `ProxyMaterial`, `ProxyRequest`, `ProxyIncomplete`, `ProxyCapture` with `AddMaterial`, `AddRequest`, `AddIncomplete`, `Materials`, `Requests`, and `Incomplete`.

Control flow: capture add methods are nil-safe and mutex-protected. `Materials` clones direct materials, builds redirect URL mapping from requests, then iteratively adds aliases so redirected URLs inherit the final digest. `Requests` and `Incomplete` return copies.

State/persistence: in-memory capture slices protected by mutex; no external persistence here. Dependencies: solver protobuf ops, OCI digest.

Integration points: implemented by `proxyprovider`, used by source policy and build result material capture. Risks: redirect alias expansion can loop until no new digest aliases; maps prevent duplicate URLs but request list can grow unbounded during long executions. Test signals: proxy provider tests exercise material capture, redirects, redaction, incomplete reasons.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/proxy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/proxyprovider/provider_linux.go -->
## sources/cloud-native/buildkit/util/network/proxyprovider/provider_linux.go

Purpose: Linux exec proxy network provider that creates isolated exec/proxy namespaces, injects an HTTP(S) MITM proxy, enforces source policy, routes egress through selected network mode, and captures downloaded material digests.

Important APIs/types: `Opt`, `Supported`, `New`, provider `Close/NewProxy/newNS/certForHost`, `proxyNS` implementing `ProxyNamespace`, and `proxyHandler` implementing HTTP proxy behavior. Helpers manage netns files, veth setup, certificate generation/cache, URL redaction/normalization, and body digest tracking.

Control flow: `New` cleans old proxy namespaces, creates a CA, builds a namespace pool, and pre-fills it. `newNS` creates paired exec and proxy namespaces, assigns veth interfaces and /30 IPs. `NewProxy` pulls a namespace from the pool and starts a proxy. `startProxy` listens inside the proxy namespace, creates an egress namespace from configured providers, requires it to implement `network.Dialer`, clones transport with egress dialer, and serves HTTP. `ProxyEnv` returns HTTP/HTTPS proxy variables pointing at the proxy-side listener and localhost `NO_PROXY`; `ProxyCACert` returns generated CA PEM.

HTTP handling: plain requests are normalized to absolute URLs, policy-checked and optionally converted for GET URL rewrites, then sent upstream with proxy headers and Accept-Encoding stripped. CONNECT is MITM'd with per-host leaf certs, reads HTTP requests inside TLS, applies the same policy/conversion, and writes upstream responses back. Successful complete GET 2xx responses record SHA-256 material digests; non-GET, ranges/partial responses, transformed/unreadable bodies, and >=400 responses are recorded as incomplete where applicable. Redirects are captured for later aliasing.

State/persistence: creates namespace bind mounts under `<root>/net/proxy`, veth devices, per-provider CA private key, LRU leaf cert cache up to 1024 entries, pooled namespaces, live HTTP servers/transports, and capture records. Dependencies: netlink/netns, containerd OCI, BuildKit network/netpool/source protobufs, TLS/X509, HTTP, OCI digest.

Integration points: constructed by `netproviders` when Linux proxy support is enabled. Executor uses returned namespace/spec/proxy env/CA. Source policy engine evaluates requests through `ProxyPolicy`.

Risks: MITM proxy requires containers to trust injected CA; namespace and veth cleanup must run to avoid leaks; generated CA is per provider lifetime and in memory; policy conversion supports URL-only GET rewrites; digest capture only represents full successful untransformed bodies. Tests in `provider_linux_test.go` cover capture, transforms, canceled contexts, HTTP/2 transport clone, MITM response framing, incomplete classification, redirects, redaction, policy conversion/rejection, and cert cache refresh.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/proxyprovider/provider_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/proxyprovider/provider_linux_test.go -->
## sources/cloud-native/buildkit/util/network/proxyprovider/provider_linux_test.go

Purpose: Linux tests for proxy handler capture, policy conversion, URL redaction, transport behavior, and cert cache.

Important tests: capture successful GET digest; strip Accept-Encoding while preserving compressed response; ignore canceled client context for upstream round trip; ensure `ForceAttemptHTTP2` and cloned HTTP/2 dialing; adjust MITM response close behavior for unknown length; mark POST incomplete; map redirect aliases to final digest; redact credentials and normalize default ports; apply source policy URL conversion; redact credentials in policy errors; reject non-GET conversion and converted attrs; cache and refresh per-host certs.

State/control flow: uses `httptest` servers, a test proxy handler with cloned default transport, synthetic policy evaluators, and generated test CA.

Risks covered: reproducibility capture correctness, credential leakage, HTTP/2 regressions, unsupported policy conversions, cert cache expiry. Gaps: full namespace/veth lifecycle and actual CONNECT tunnel integration are not end-to-end tested here.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/proxyprovider/provider_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/proxyprovider/provider_unsupported.go -->
## sources/cloud-native/buildkit/util/network/proxyprovider/provider_unsupported.go

Purpose: non-Linux proxy provider stub.

Important APIs: same `Opt` shape as Linux, `Supported() bool` returns false, `New` returns an unsupported error.

State/persistence: none. Integration: `netproviders` checks `Supported` before constructing proxy provider. Risks: proxy capture/source-policy network proxy features are Linux-only. Test signals: no local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/network/proxyprovider/provider_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/overlay/overlay.go -->
## sources/cloud-native/buildkit/util/overlay/overlay.go

Purpose: tiny cross-platform overlay mount classifier.

Important API: `IsOverlayMountType(mount.Mount) bool` returns true when `mnt.Type == "overlay"`.

State/persistence: none. Dependencies: containerd mount type.

Integration points: Linux overlay differ uses this helper while parsing snapshot mounts. Risks: only recognizes literal `overlay`, not platform aliases or fuse-overlayfs. Test signals: indirect via overlay Linux tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/overlay/overlay.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/overlay/overlay_linux.go -->
## sources/cloud-native/buildkit/util/overlay/overlay_linux.go

Purpose: Linux overlayfs-aware differ that derives layer changes directly from overlay upperdir and writes layer tar archives efficiently.

Important APIs/functions: `GetUpperdir`, `GetOverlayLayers`, `WriteUpperdir`, `Changes`, `checkDelete`, `checkOpaque`, `checkRedirect`, `sameDirent`, stat/xattr/content comparison helpers.

Control flow: `GetUpperdir` compares lower and upper mount layer lists to identify the single top upper layer. `GetOverlayLayers` parses `upperdir` and reversed `lowerdir` options while rejecting unknown options. `WriteUpperdir` mounts lower and an upperdir view over an empty lower, then uses archive `ChangeWriter` over `Changes`. `Changes` walks upperdir, rebases paths, rejects redirect_dir xattrs, interprets char device 0/0 as whiteout deletes, compares existing base entries as modifies while skipping unchanged parent dirs, detects adds, and for opaque directories delegates to continuity `fs.Changes` against the clean upper view.

State/persistence: reads overlay upperdir, xattrs, device nodes, and may create temp mount points; writes tar stream to provided writer. Uses a typed `sync.Pool` buffer for slow content comparison. Dependencies: containerd mount/archive/continuity fs/sysx/devices, unix, BuildKit pools.

Integration points: snapshot differ/export code can use overlay metadata instead of full walking differ. Risks: redirect_dir unsupported and errors; unknown overlay options cause fallback; requires privilege/mount support; slow content compare still needed for truncated timestamps; xattr access can fail by filesystem/capabilities. Test signals: `overlay_linux_test.go` ports many continuity differ cases for adds/modifies/deletes, renames, nested deletions, permissions, timestamps, symlinks.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/overlay/overlay_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/overlay/overlay_linux_test.go -->
## sources/cloud-native/buildkit/util/overlay/overlay_linux_test.go

Purpose: validates overlayfs-optimized change detection against continuity-style filesystem diff cases.

Important tests: simple file/dir add-modify-delete, rename fallback, empty unchanged file, nested deletion collapse, directory replace, remove directory trees, file replaced by directory, parent directory permissions, timestamp/content comparison edge cases, and symlink lchtimes. Helper functions mount overlay with temp lower/upper/work dirs, apply fstest layers, collect `Changes`, and compare path/kind/source metadata.

State/control flow: requires Linux overlay mount support; uses temp dirs and actual overlayfs behavior including whiteouts and xattrs.

Risks covered: wrong whiteout handling, unchanged parent dirs being emitted, timestamp truncation decisions, and recursive opaque-like directory behavior. Gaps: explicit redirect_dir error path, `GetUpperdir`, `WriteUpperdir`, and xattr capability comparison are not directly isolated.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/overlay/overlay_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/pgpsign/pgpsign.go -->
## sources/cloud-native/buildkit/util/pgpsign/pgpsign.go

Purpose: OpenPGP signature parsing and verification helpers with BuildKit policy checks for hashes, key algorithms, key expiry/revocation, RSA size, and precomputed digest verification.

Important APIs/types: `VerifyPolicy{RejectExpiredKeys}`, `ParseArmoredDetachedSignature`, `ReadAllArmoredKeyRings`, `VerifyArmoredDetachedSignature`, `VerifySignatureWithDigest`. Internal helpers map signature hash to OCI digest algorithm and validate entities/signature times.

Control flow: signature parsing decodes armor and returns the first packet signature. keyring reading accepts concatenated public or private armored key blocks. Detached verification parses signature/keyring, rejects weak hash and unsupported public-key algorithms, optionally sets OpenPGP verification time to signature creation time when expired keys are allowed, runs `openpgp.CheckDetachedSignature`, then validates signer usability, revocation, RSA length, and future creation time. Digest verification constructs a `staticHash` with precomputed sum and tries primary/subkeys.

State/persistence: stateless, operates on in-memory key/signature data and signed streams. Dependencies: ProtonMail OpenPGP, OCI digest, crypto hash/RSA.

Integration points: called by Git signature verification and provenance/trust features. Risks: accepts private key blocks as keyrings; policy defaults allow expired keys by verifying at signature creation time; only SHA-256/384/512 and selected pubkey algos are accepted; `staticHash.Write` discards bytes by design for prehashed verification. Test signals: no local tests in this subset, but `gitobject` and `gitsign` rely on this behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/pgpsign/pgpsign.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/pools/pools.go -->
## sources/cloud-native/buildkit/util/pools/pools.go

Purpose: generic typed wrapper around `sync.Pool`.

Important API/type: `Pool[T]`, `New(newFn)`, `Get`, and `Put`.

Control flow/state: `New` stores a `sync.Pool` whose `New` returns the typed value as `any`; `Get` type-asserts; `Put` returns values. No cleanup or reset callback.

Integration points: used by overlay differ for reusable byte buffers. Risks: callers must reset values before/after reuse as needed; type assertion assumes only this wrapper writes to the pool. Test signals: no local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/pools/pools.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/profiler/profiler.go -->
## sources/cloud-native/buildkit/util/profiler/profiler.go

Purpose: attaches hidden profiling flags to a urfave CLI command and starts/stops requested profile collectors around command execution.

Important API: `Attach(app *cli.Command)` mutates flags and wraps `Before`/`After` hooks. Hidden flags include CPU, memory, memory rate, block, mutex, and trace profile paths.

Control flow: wrapped `Before` calls any existing hook first, then starts each requested profile via `pkg/profile.Start` with `NoShutdownHook`, storing stoppers. Wrapped `After` calls existing hook first, then stops all stoppers.

State/persistence: process-global profiling side effects and profile files under requested paths. `stoppers` slice is captured in `Attach` closure. Dependencies: `pkg/profile`, urfave/cli v3.

Integration points: BuildKit command binaries can opt into hidden profiling flags. Risks: if existing `After` returns error, stoppers are not stopped; repeated command executions on the same attached command may accumulate stoppers; profile path semantics are delegated to pkg/profile. Test signals: no local tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/profiler/profiler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/controller/controller.go -->
## sources/cloud-native/buildkit/util/progress/controller/controller.go

Purpose: reference-counted progress controller for a named vertex and status updates.

Important type/API: `Controller` implements `progress.Controller` with `Start(ctx) (context.Context, done)` and `Status(id,action) func()`. Fields include digest/name/writer factory/progress group.

Control flow: `Start` increments count under mutex. On first active start it initializes start time, writer, and vertex ID, then writes a started vertex if digest is set. It returns a context carrying the writer and a done func. The done func decrements count; when zero it writes completed vertex with optional error string, closes writer, and clears state. `Status` writes start/completion status around an action using the current writer when present.

State/persistence: in-memory count, timestamps, writer, ID protected by mutex; progress is emitted to configured writer. Dependencies: BuildKit client vertex types, identity, solver progress group, OCI digest.

Integration points: used by code that wants nested operations to share one visible progress vertex. Risks: `Status` reads `c.writer` without locking, so races are possible if used concurrently with `Start`/done; missing `WriterFactory` would panic when called. Test signals: no direct controller tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/controller/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/logs/logs.go -->
## sources/cloud-native/buildkit/util/progress/logs/logs.go

Purpose: converts stdout/stderr byte streams into BuildKit progress log vertices with size/speed clipping and optional local printing.

Important APIs/types: `NewLogStreams(ctx, printOutput)` returns stdout/stderr write closers plus flush function. `streamWriter` handles limits, clipping, circbuf tail, and writes `client.VertexLog`. `LoggerFromContext` returns a stderr logger function.

Control flow: env config is read once from `BUILDKIT_STEP_LOG_MAX_SIZE` and `BUILDKIT_STEP_LOG_MAX_SPEED`. `Write` computes allowed bytes based on max total size or speed-derived budget, initializes a 256 KiB circular buffer once clipping starts, emits an output-clipped message at transition, writes limited data to progress and optionally OS stdout/stderr, and reports the original byte count. `flushBuffer` emits buffered tail. `Close` closes progress writer.

State/persistence: per-stream counters, clipping flags, optional circbuf tail; package-level defaults mutate after env read. Dependencies: BuildKit progress/client, circbuf, units, identity.

Integration points: Git CLI streams and executor logs. Risks: config read once means later env changes are ignored; when clipping, returned write count hides dropped bytes intentionally; `Close` does not flush tail automatically. Test signals: no local tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/logs/logs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/multireader.go -->
## sources/cloud-native/buildkit/util/progress/multireader.go

Purpose: fans out a single progress reader to multiple readers while replaying already-sent progress to late joiners.

Important APIs/types: `MultiReader`, `NewMultiReader(pr)`, `Reader(ctx)`, internal `handle`.

Control flow: `Reader` creates a new progress context/writer pair. If progress has already been sent or the main reader is done, a goroutine replays `mr.sent` to the new writer in batches, respecting context cancellation, then registers it for live updates if not done. The first `Reader` call starts `handle`, which continuously reads main progress, writes raw progress to registered writers, appends sent history, and on EOF closes all writers and marks done.

State/persistence: in-memory sent progress slice grows for lifetime; writer map and done cause protected by mutex. Dependencies: local progress primitives, `context`, `io`.

Integration points: lets multiple consumers observe solver progress streams. Risks: unbounded history growth; `handle` non-EOF errors return without closing `done`, potentially leaving readers waiting; replay loop variable shadowing is subtle but works because outer index is updated after each chunk. Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/multireader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/multiwriter.go -->
## sources/cloud-native/buildkit/util/progress/multiwriter.go

Purpose: aggregates progress writes and replays sorted history to newly attached writers.

Important APIs/types: `MultiWriter`, `NewMultiWriter`, `Add`, `Delete`, `Write`, `WriteRawProgress`, `Close`, and cycle-detection helper `contains`.

Control flow: `Write` creates a timestamped `Progress` with shared metadata, stores it, and forwards to attached raw writers. `Add` accepts only writers implementing raw progress, detects `MultiWriter` cycles and panics on loops, sorts existing items by timestamp, replays them, and registers writer. `WriteRawProgress` decorates incoming progress with metadata without overwriting existing metadata.

State/persistence: in-memory history, writer set, metadata map protected by mutex. Dependencies: `slices`, `sync`, time.

Integration points: progress fan-in/fan-out for solver and flightcontrol. Risks: unbounded history; `Close` is no-op so attached writers are not closed; writing while holding lock means a slow writer blocks all writes and may deadlock if it calls back. Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/multiwriter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progress.go -->
## sources/cloud-native/buildkit/util/progress/progress.go

Purpose: core context-based progress pipe abstraction for BuildKit operations.

Important APIs/types: `WriterFactory`, `FromContext`, `NewFromContext`, `NewContext`, `WithProgress`, `WithMetadata`, `Controller`, `Writer`, `Reader`, `Progress`, `Status`, `OneOff`. Internal `progressReader`/`progressWriter` implement a collapsing progress pipe.

Control flow: `NewContext` creates a reader/writer pipe and stores writer in context. `FromContext` returns a factory that creates child writers from an existing writer, or returns a `MultiWriter` as-is, or a no-op writer if no progress is present. `Read` waits on condition variable until dirty progress is available, context is canceled, or all writers close after pipe cancellation; it collapses by progress ID and returns items sorted by timestamp. Writers store last progress per ID and broadcast. Metadata options are copied/decorated into child writers. `OneOff` writes start and completion status around a call.

State/persistence: in-memory writer set and dirty map protected by mutex; closed writer has a `done` flag. No persistence. Dependencies: context, sync, time, `maps`, `slices`, `pkg/errors`.

Integration points: central for progress emitted by solvers, flightcontrol, logs, controllers, and UI. Risks: `progressWriter.done` is checked/set outside a mutex, so misuse may race; collapse-by-ID drops intermediate statuses between reads; writers must be closed to let readers finish. Test signals: `progress_test.go` covers nested progress, metadata propagation, ID collapse/final status expectations.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progress.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progress_test.go -->
## sources/cloud-native/buildkit/util/progress/progress_test.go

Purpose: tests core progress context behavior and nested writer propagation.

Important tests: `TestProgress` verifies code can run without progress, then with a progress context/writer carrying metadata, and confirms captured items all include metadata. `TestProgressNested` runs nested synchronous and parallel calculations, reads progress until EOF, and verifies final last-by-ID statuses.

Support functions: `calc` emits start/calculating/done statuses; `reduceCalc` creates nested writers and parallel goroutines; `saveProgress` drains a reader.

Risks covered: metadata propagation, nested writer creation, reader EOF after cancellation/close, collapsed final statuses. Gaps: cancellation errors, writing after close, no-op writer, and MultiReader/MultiWriter are not directly tested here.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progress_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progressui/colors.go -->
## sources/cloud-native/buildkit/util/progress/progressui/colors.go

Purpose: parses `BUILDKIT_COLORS` customization for progress UI semantic colors.

Important functions: `setUserDefinedTermColors`, `readBuildkitColorsEnv`, `readRGB`, `parseKeys`, `isValidRGB`, `isValidRGBValue`. `termColorMap` maps named colors to `aec` ANSI values.

Control flow: environment string is parsed as colon-separated CSV fields; each field must be `key=value` with no extra equals. Values are matched against named colors or parsed as comma-separated RGB triplets. Keys update `colorRun`, `colorCancel`, `colorError`, or `colorWarning`; unknown keys/values log warnings and are ignored.

State/persistence: mutates package-level color variables in progress UI; no persistence. Dependencies: BuildKit logger, `morikuni/aec`, `tonistiigi/go-csvvalue`.

Integration points: terminal progress display configuration. Risks: invalid config only warns; RGB parsing depends on CSV escaping; package-level mutation affects subsequent displays globally. Test signals: no color tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/progress/progressui/colors.go -->
