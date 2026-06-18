# Research Group subset-b-000017

This grouped report covers BuildKit frontend, docker UI named context handling, gateway client/server forwarding, gRPC frontend client behavior, container execution support, and gateway protobuf helpers. Each section is source-tree aligned and bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerui/namedcontext.go -->
# sources/cloud-native/buildkit/frontend/dockerui/namedcontext.go

## Purpose

This file implements Docker UI named contexts: build option entries such as `context:<name>` are converted into lazy `llb.State` sources that frontends can use as additional build contexts. It supports image, Git, HTTP, OCI layout, local, and gateway input sources while preserving platform-aware names and optional digest capture.

## Important APIs, Types, And Functions

- `NamedContext` stores the raw context specifier, owning `*Client`, logical names, shared local-directory key, and `ContextOpt`.
- `(*Client).namedContext` looks up `context:<nameWithPlatform>` in build options and returns `nil` when the named context is absent.
- `(*NamedContext).Load` calls `load(ctx, 0)` and is the public loading entry point.
- `(*NamedContext).load` parses the `<scheme>:<payload>` context source and dispatches to source-specific LLB construction.
- `asyncLocalOutput` is an `llb.Output` wrapper that delays constructing `llb.Local` until `ToInput` or `Vertex` is called.
- `(*asyncLocalOutput).do` builds the local source with session ID, shared key hint, dockerignore exclusions, and optional caller-provided local options.

## Control Flow

`Load` validates `scheme:payload`, normalizes legacy `git@` SSH-style prefixes to `git`, then switches by scheme. `docker-image` resolves and unmarshals image config, converts non-image resolution results into recursively reloaded named contexts, returns scratch for `EmptyImageName`, and tags the LLB image with custom display names and platform constraints. `git`, `http`, and `https` delegate Git URL detection first; non-Git HTTP sources become `llb.HTTP` states. `oci-layout` parses the store ID and digest, resolves image config through the client session-backed OCI layout resolver, and returns `llb.OCILayout`.

For `local`, the code first solves a small LLB that only follows `.dockerignore`, reads and parses ignore rules unless disabled, then returns an `llb.NewState` around `asyncLocalOutput`. The actual local source is constructed later, which lets `ContextOpt.AsyncLocalOpts` run after initial context configuration is known. For `input`, the gateway client input definitions are loaded by name and optional `input-metadata:<name>` JSON supplies image config metadata.

## State And Persistence Behavior

The code mutates `bc.bopts.Opts[context:<name>]` only when image resolution reports `ResolveToNonImageError`; this encodes an updated non-image source and retries with a recursion limit of 10. Local source state depends on session IDs and shared key hints rather than durable repository state. `asyncLocalOutput` uses `sync.Once` to make lazy source construction idempotent and thread-safe for both `ToInput` and `Vertex`.

## Dependencies And Integration Points

It integrates with `llb` source constructors, `sourceresolver` image/OCI metadata, gateway `client.Client` solve/input APIs, BuildKit exporter image config metadata, Docker image spec structs, distribution reference parsing, image source-policy rewrite errors, and `.dockerignore` parsing from `patternmatcher/ignorefile`.

## Risks And Edge Cases

Incorrect context specifier formatting fails early. Recursive source-policy rewrites can loop, so `maxContextRecursion` is a key guard. Local `.dockerignore` parsing errors fail the context, but missing `.dockerignore` is ignored. OCI layout requires both a named reference and digest. `input` metadata JSON and image config JSON are trust boundaries and can fail parsing. Mutating build options during load means callers sharing a `Client` observe rewritten context specs.

## Test Signals

No direct tests are in this file, but gateway and frontend integration tests exercise reference reads and input/solve behavior that named contexts depend on. Strong targeted coverage would include source-policy image-to-Git/HTTP rewrites, OCI layout digest validation, local dockerignore parsing, and async local option invocation.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerui/namedcontext.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerui/requests.go -->
# sources/cloud-native/buildkit/frontend/dockerui/requests.go

## Purpose

This file handles Docker UI frontend subrequests selected through the `requestid` build option. It lets a frontend answer metadata-style requests such as subrequest descriptions, outline, target list, lint results, and LLB conversion without running the normal build path.

## Important APIs, Types, And Functions

- `keyRequestID` is the option key used to select a subrequest.
- `RequestHandler` groups optional handler callbacks for outline, targets, lint, and convert-LLB plus `AllowOther` fallback behavior.
- `(*Client).HandleSubrequest` dispatches the selected request and returns `(*client.Result, handled bool, error)`.
- `describe` builds the supported subrequest list and returns both JSON and text renderings in result metadata.

## Control Flow

`HandleSubrequest` first checks `bc.bopts.Opts["requestid"]`; if absent, it returns `(nil, false, nil)` so the caller can continue the normal build. For recognized requests it checks the matching callback, invokes it with the build context, converts the domain result to a gateway `client.Result`, and marks the request handled even when the callback returns nil. The describe request is synthesized from non-nil handlers. Unknown or unavailable requests return unsupported unless `AllowOther` tells the caller to handle it elsewhere.

## State And Persistence Behavior

The file does not persist state. It only reads build options and creates ephemeral result metadata. Returned metadata keys include `result.json`, `result.txt`, and `version`, which are consumed by clients asking for subrequest capabilities.

## Dependencies And Integration Points

It integrates with BuildKit subrequest packages: `subrequests`, `outline`, `targets`, `lint`, and `convertllb`. It returns gateway client results and uses `errdefs.NewUnsupportedSubrequestError` so unsupported request errors are recognizable by frontend callers.

## Risks And Edge Cases

The dispatch is callback-driven, so a frontend can advertise only handlers it supplies. `describe` currently lists outline and targets plus describe; lint and convert-LLB are handled by `HandleSubrequest` but are not included in the describe list, which may be intentional compatibility behavior or a discoverability gap. `AllowOther` changes unknown-request behavior from hard error to caller fallback, so misuse can hide typos.

## Test Signals

This file has no colocated tests in the subset. Useful tests would validate `handled` semantics for nil callback results, unsupported subrequest errors, and describe metadata contents.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/dockerui/requests.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/frontend.go -->
# sources/cloud-native/buildkit/frontend/frontend.go

## Purpose

This file defines the core BuildKit frontend contracts shared by gateway and non-gateway frontends. It keeps the interface between solver, executor, session manager, source metadata resolver, and frontend implementations compact.

## Important APIs, Types, And Functions

- `KeySource` is the gateway frontend option key for the external frontend image/source.
- `KeyDevelDeprecated` rejects the old development gateway mode.
- `Result` aliases `result.Result[solver.ResultProxy]`.
- `Attestation` aliases `result.Attestation[solver.ResultProxy]`.
- `Frontend` is implemented by frontend backends and exposes `Solve`.
- `FrontendLLBBridge` combines source metadata resolution, solver `Solve`, and warning reporting.
- `SolveRequest`, `CacheOptionsEntry`, and `WarnOpts` alias gateway client request types.

## Control Flow

The file is declarative. Runtime control flow is in implementations such as `gatewayFrontend.Solve` and forwarders. The `Frontend.Solve` signature passes an LLB bridge, executor, option map, frontend inputs, session ID, and session manager to concrete frontends.

## State And Persistence Behavior

There is no mutable state. Type aliases stabilize package boundaries and avoid duplicate structures across frontend/gateway code.

## Dependencies And Integration Points

It integrates with `sourceresolver.MetaResolver`, BuildKit `executor`, gateway client types, sessions, solver result proxies, solver protobuf definitions, and digest-based warning APIs. It is the common contract used by gateway forwarding and image-based frontends.

## Risks And Edge Cases

Because aliases point to gateway client types, changes in gateway client request structures affect the general frontend interface. Implementations must honor session ID and session manager lifetimes because the interface exposes both.

## Test Signals

No direct tests are needed for the type alias file, but integration tests under `frontend_test.go` exercise frontend callbacks and gateway client behavior through this interface.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/frontend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/frontend_test.go -->
# sources/cloud-native/buildkit/frontend/frontend_test.go

## Purpose

This integration test file validates basic frontend gateway behavior against BuildKit workers: returning nil or empty results, reading files, reading directories, statting files, and evaluating refs.

## Important APIs, Types, And Functions

- `init` selects Docker, OCI, and containerd workers for integration coverage.
- `TestFrontendIntegration` registers test functions with the shared integration runner.
- `testReturnNil` verifies frontends can return nil or an empty result without failing the build.
- `testRefReadFile` checks full and ranged `Reference.ReadFile` behavior.
- `testRefReadDir` checks `Reference.ReadDir` with root/subdirectory and glob include patterns.
- `testRefStatFile` verifies `Reference.StatFile`.
- `testRefEvaluate` verifies lazy result evaluation succeeds for valid LLB and fails for invalid LLB.

## Control Flow

Each test creates a BuildKit client, prepares an optional local filesystem, defines a gateway frontend callback, then calls `client.Build`. Inside callbacks, local or scratch LLB is solved through the gateway client, refs are extracted, and gateway reference operations are asserted.

## State And Persistence Behavior

Tests create temporary directories via integration helpers and close BuildKit clients. They clear `ModTime` in directory listing expectations to avoid nondeterministic filesystem timestamps. No repository state is modified.

## Dependencies And Integration Points

The tests integrate the external client package, `llb`, gateway client frontend callbacks, integration sandbox utilities, worker initialization helpers, `fsutil`, and `fstest`.

## Risks And Edge Cases

The integration suite depends on worker availability and can be skipped or vary by worker backend configuration. Directory stat comparison normalizes only fields expected to vary, but other platform-specific fs metadata could still cause test differences. `testRefEvaluate` specifically catches the risk that refs stay lazy and errors surface late.

## Test Signals

These tests are primary signals for gateway reference filesystem APIs. They cover ranged reads including overruns, directory include patterns, stat equivalence, and evaluate error surfacing.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/frontend_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/client/attestation.go -->
# sources/cloud-native/buildkit/frontend/gateway/client/attestation.go

## Purpose

This file converts BuildKit result attestations between in-memory generic result types and gateway protobuf messages. It allows attestations to cross the gateway API while rejecting callback-based attestation content that cannot be serialized.

## Important APIs, Types, And Functions

- `AttestationToPB[T]` converts `result.Attestation[T]` to `pb.Attestation`.
- `AttestationFromPB[T]` converts a protobuf attestation back to `result.Attestation[T]`.
- `digestSliceToPB` and `digestSliceFromPB` convert digest slices between typed `digest.Digest` and strings.

## Control Flow

`AttestationToPB` first rejects `ContentFunc`, then maps every in-toto subject to protobuf fields and copies top-level kind, metadata, path, predicate type, and subjects. `AttestationFromPB` rejects nil attestations and nil subjects, then rebuilds the generic result attestation.

## State And Persistence Behavior

There is no persistent state. Metadata maps and digest slices are passed through or shallow-copied according to protobuf/result field behavior; digest slices are explicitly cloned into new slices.

## Dependencies And Integration Points

It integrates with gateway protobuf package, BuildKit `solver/result` attestations, and Open Containers digests. Server and client return paths call these functions when solving or returning gateway results with attestations.

## Risks And Edge Cases

Callback attestations are intentionally unsupported over gateway and cause errors. Nil protobuf subjects are rejected to avoid panics or malformed attestations. Because metadata is assigned directly, callers should avoid mutating shared maps after conversion if aliasing matters.

## Test Signals

No direct test in this subset targets attestation conversion. Gateway solve and return paths exercise error behavior when attestations are present; targeted tests should cover nil input, nil subject, content callback rejection, and digest round trips.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/client/attestation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/client/client.go -->
# sources/cloud-native/buildkit/frontend/gateway/client/client.go

## Purpose

This file defines the public gateway client API implemented by in-process forwarders and by the gRPC frontend client. It is the contract external frontends use to solve LLB, resolve image metadata, access inputs, create containers, read refs, and emit warnings.

## Important APIs, Types, And Functions

- `Result` and `Attestation` alias generic result types parameterized by gateway `Reference`.
- `BuildFunc` is the callback signature for gateway frontends.
- `NewResult` returns an empty result.
- `Client` includes metadata resolution, `Solve`, image config resolution, build options, inputs, `NewContainer`, and `Warn`.
- `NewContainerRequest`, `Mount`, `Container`, `StartRequest`, `ContainerProcess`, and `WinSize` define gateway exec behavior.
- `Reference`, `ReadRequest`, `ReadDirRequest`, and `StatRequest` define filesystem operations on solved refs.
- `SolveRequest.Clone` deep-copies mutable solve request fields.
- `BuildOpts` exposes option map, session ID, worker info, product, and API/LLB capabilities.
- `WarnOpts` carries warning source ranges, detail, and URL.

## Control Flow

This file mainly declares interfaces and value objects. `SolveRequest.Clone` performs the only substantial control flow: it clones the definition, frontend options, frontend input definitions including nil preservation, cache import entries and their attributes, and source policies.

## State And Persistence Behavior

The types are request/response carriers. Persistent state is held by concrete implementations. `Clone` prevents unintended aliasing of nested mutable maps, slices, definitions, and source policies when callers need to mutate a request copy.

## Dependencies And Integration Points

The API bridges `llb`, `sourceresolver`, solver protobuf definitions, source policies, API capabilities, Open Containers platforms, filesystem stat structures, and process I/O. Both `forwarder.BridgeClient` and `grpcclient.grpcClient` implement this contract.

## Risks And Edge Cases

Implementations must honor capability checks for optional features. `Mount` permits either `Ref` or `ResultID`, so concrete implementations need type and existence validation. `Clone` must stay current as fields are added; missing deep copies would cause mutation leaks. `ContainerProcess` exposes asynchronous resize/signal operations, so lifecycle race handling belongs to implementations.

## Test Signals

`client_test.go` verifies `SolveRequest.Clone` deep-copies `FrontendInputs`, preserves nil entries, clones `FrontendOpt`, and prevents metadata mutation in clones from leaking to originals.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/client/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/client/client_test.go -->
# sources/cloud-native/buildkit/frontend/gateway/client/client_test.go

## Purpose

This file tests that `SolveRequest.Clone` correctly deep-copies frontend inputs and associated mutable fields.

## Important APIs, Types, And Functions

- `TestSolveRequestCloneCopiesFrontendInputs` constructs a solve request with frontend options and frontend input definitions, clones it, mutates the clone, and asserts the original is unchanged.

## Control Flow

The test builds a request containing a real `pb.Definition` and a nil input entry. It calls `Clone`, checks the cloned map retains both keys, asserts the non-nil definition pointer differs but is equal in value, mutates cloned frontend option and metadata, and verifies original data remains intact.

## State And Persistence Behavior

Only in-memory test state is used. The key persistence signal is negative: cloned state must not share mutable nested maps with the original request.

## Dependencies And Integration Points

It uses solver protobuf `pb.Definition`, `pb.OpMetadata`, and `testify/require`. It specifically protects the gateway client API used by forwarders and grpc clients when solve requests are reused or amended.

## Risks And Edge Cases

The test focuses on frontend inputs. Other fields in `Clone`, such as cache imports and source policies, rely on implementation review or separate coverage. If new mutable fields are added to `SolveRequest`, this test will not automatically detect missing clone logic unless extended.

## Test Signals

This is a strong regression signal for frontend input aliasing. It demonstrates that nil input definitions remain represented and that nested metadata maps are cloned through `CloneVT`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/client/client_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/container/container.go -->
# sources/cloud-native/buildkit/frontend/gateway/container/container.go

## Purpose

This file implements gateway container creation, mount preparation, process execution, lazy filesystem access, stat conversion, and cleanup. It backs `client.Container` for both in-process and gRPC gateway frontends.

## Important APIs, Types, And Functions

- `NewContainerRequest` and `Mount` are server-side container request types using `worker.WorkerRef`.
- `NewContainer` prepares mounts, creates a `gatewayContainer`, and returns it as `client.Container`.
- `setupLocalMounts` maps original mount indexes to executor mountables used by container filesystem read APIs.
- `PreparedMounts`, `MountRef`, `MountMutableRef`, and `MakeMutable` describe mount preparation outputs.
- `PrepareMounts` transforms protobuf mounts and worker refs into executor root/mount lists plus output and active refs.
- `gatewayContainer.Start`, `Release`, `ReadFile`, `ReadDir`, `StatFile`, and `mount` implement runtime behavior.
- `loadSecretEnv`, `addDefaultEnvvar`, `MountWithSession`, `mkstat`, `readlink`, and `relpath` support execution and filesystem inspection.
- `gatewayContainerProcess` implements wait, resize, and signal forwarding.

## Control Flow

`NewContainer` builds mount and ref slices, assigns `Mount.Input` indexes, calls `PrepareMounts`, records root/mounts/local mounts, and registers cleanup functions for active and output refs. On preparation error it releases any prepared refs in reverse order.

`PrepareMounts` iterates mount specs. Bind mounts may clone readonly inputs, create mutable children for outputs, or create active mutable refs for writable non-output mounts. Cache mounts come from the mount manager and may return cloned input refs as outputs. Tmpfs, secret, and SSH mounts delegate to mount manager helpers. Root mount validation requires bind mount type. Non-root mounts are made absolute relative to `cwd`, wrapped with session-aware mountables, and sorted by destination so parent paths mount first.

`Start` creates executor process metadata, adds default `PATH` and optional `TERM`, resolves secret environment variables through the session manager, and calls `executor.Run` for the first process or `executor.Exec` for later processes. `Release` cancels the container context, waits for all process errgroups, then runs cleanup LIFO. Filesystem read/stat APIs lazily mount the selected mount index and operate through `fs.FS`.

## State And Persistence Behavior

`gatewayContainer` owns mutable lifecycle state: `started`, cleanup stack, lazy `localMounts` filesystem handles, and cancellation context. Mount and ref cleanup is not persistent but is critical for cache ref and mount lifecycle. Lazy mounts are cached per mount index after first access and unmounted/closed during release. `sync.Mutex` protects start state, cleanup additions during lazy mount, and process channels.

## Dependencies And Integration Points

It integrates with BuildKit cache managers, executor, sessions, secrets, snapshot local mounters, solver mount manager, worker refs, filesystem stat types, system path helpers, and gateway client interfaces. It is used by the in-process forwarder and by the gateway gRPC server when servicing `NewContainer`/`ExecProcess` requests.

## Risks And Edge Cases

Mount lifecycle is the primary risk: every mutable ref, cloned output ref, local mounter, and opened root must be released once and in safe order. `Start` switches behavior after the first process, so concurrent first starts depend on the mutex. `ReadDir` does not apply include patterns here; container server/client paths do not pass include matching to `fs.ReadDir`, so filtering semantics differ from cacheutil-backed reference reads unless handled elsewhere. `StatFile` has a deliberate fallback for symlinks that escape an `os.Root`, returning lstat data so clients can resolve safely. Secret env optional handling appends empty values if not found and optional.

## Test Signals

No full container lifecycle tests are in this subset, but `util_test.go` covers path escape error detection used by `StatFile`. Gateway gRPC code paths exercise container creation and process I/O indirectly. More coverage would target mount preparation matrix behavior, duplicate cleanup, concurrent starts, secret env missing/optional cases, and container filesystem read/stat behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/container/container.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/container/util.go -->
# sources/cloud-native/buildkit/frontend/gateway/container/util.go

## Purpose

This file provides small utility functions for gateway containers: parsing extra host IPs and identifying `os.Root` path escape errors.

## Important APIs, Types, And Functions

- `ParseExtraHosts` converts protobuf host/IP records to executor host/IP records using `net.ParseIP`.
- `isPathEscapesRootError` checks whether an error is an `*os.PathError` whose wrapped error text contains `path escapes`.

## Control Flow

`ParseExtraHosts` allocates an output slice of the same length as input, parses each IP, returns an error on the first invalid IP, and copies host names through. `isPathEscapesRootError` first uses `errors.As` to verify `*os.PathError`, then checks the error string.

## State And Persistence Behavior

No state is stored. Output slices are newly allocated.

## Dependencies And Integration Points

`ParseExtraHosts` feeds `executor.ProcessInfo.Meta.ExtraHosts` from gateway new-container requests. `isPathEscapesRootError` is used by `gatewayContainer.StatFile` to decide when to fall back from stat to lstat for symlink escapes.

## Risks And Edge Cases

The path escape detector depends on error text, which is less stable than a sentinel error. It is scoped by requiring `*os.PathError`, reducing false positives. `ParseExtraHosts` accepts any `net.ParseIP` output, including IPv4 and IPv6.

## Test Signals

`util_test.go` creates a symlink escaping an opened root and asserts the detector returns true for the resulting `fs.Stat` error.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/container/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/container/util_test.go -->
# sources/cloud-native/buildkit/frontend/gateway/container/util_test.go

## Purpose

This file tests detection of `os.Root` path escape errors for container stat fallback behavior.

## Important APIs, Types, And Functions

- `TestIsPathEscapesRootError` creates a temp root, symlinks `sh` to `/bin/sh`, opens the root with `os.OpenRoot`, stats the symlink through `fs.Stat`, and checks `isPathEscapesRootError`.

## Control Flow

The test constructs the escaping symlink, opens the restricted root filesystem, expects `fs.Stat(fsys.FS(), "sh")` to error, and requires the helper to classify it as a path escape.

## State And Persistence Behavior

Only a temporary directory and symlink are created. The opened root is closed with `defer`.

## Dependencies And Integration Points

The test uses Go `io/fs`, `os.OpenRoot`, filesystem symlinks, and `testify/require`. It protects the fallback path in `gatewayContainer.StatFile`.

## Risks And Edge Cases

The test depends on platform support for `os.OpenRoot` and symlink semantics. It verifies only positive detection; negative cases for non-`PathError` or unrelated `PathError` are not covered.

## Test Signals

This is a focused regression signal for safely statting symlinks that would otherwise escape the mounted root.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/container/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/forwarder/forward.go -->
# sources/cloud-native/buildkit/frontend/gateway/forwarder/forward.go

## Purpose

This file adapts an in-process `frontend.FrontendLLBBridge` into the public gateway `client.Client` interface. It lets Go frontends run locally against the BuildKit solver without going through the stdio gRPC protocol.

## Important APIs, Types, And Functions

- `LLBBridgeToGatewayClient` constructs a `BridgeClient`.
- `BridgeClient` embeds `FrontendLLBBridge` and implements `client.Client`.
- `Solve`, `ResolveImageConfig`, `BuildOpts`, `Inputs`, `Warn`, and `NewContainer` implement gateway client operations.
- `wrapSolveError` and `registerResultIDs` translate solver errors into gateway solve errors with result IDs.
- `toFrontendResult`, `discard`, and `discardMounts` convert returned client results back to frontend results and release resources.
- `ref` implements `client.Reference` over a `solver.ResultProxy`.

## Control Flow

`Solve` delegates to `FrontendLLBBridge.Solve`, rejects callback-based attestations, converts each solver result proxy to a gateway `ref`, and records refs for later cleanup. `NewContainer` resolves mount refs in parallel, builds server-side container mount requests, parses extra hosts, gets the default cache manager, and calls `container.NewContainer`. Reference filesystem methods lazily mount worker refs through `snapshot.LocalMounter` and call `cacheutil` read/stat helpers.

Error wrapping captures exec, file-action, and slow-cache errors, registers involved worker refs as IDs, and wraps the original error with solve subject metadata. `toFrontendResult` converts gateway references back to solver proxies by splitting result proxies so returned refs remain valid after bridge cleanup. `discard` releases containers, mounters, worker refs, result proxies, and on error also releases result proxy clones.

## State And Persistence Behavior

`BridgeClient` tracks refs, worker refs by ID, containers, and mounted snapshot mounters. A mutex protects ref registration and result conversion, while a separate mutex protects mount cache. State is per build invocation and must be discarded at the end. Mounters persist until `discardMounts`; repeated reads reuse the same mounter by result ID.

## Dependencies And Integration Points

It integrates frontend interfaces, gateway client interfaces, container implementation, solver error types, worker refs, sessions, cache utilities, snapshots, API caps, identity IDs, and source metadata resolver. `forwarder/frontend.go` uses it to implement `GatewayForwarder`.

## Risks And Edge Cases

Resource ownership is subtle: result proxies are split and released differently on success versus error; worker refs from solve errors are registered so clients can mount them later. NewContainer's loop captures range values using Go's per-iteration variables, which is safe in modern Go but would have been risky in older versions. `discardMounts` ignores unmount errors. Attestation callbacks cannot cross this boundary and fail solve/return conversion.

## Test Signals

Frontend integration tests exercise reference reads through this bridge. There are no direct unit tests for error wrapping, resource discard, or container creation in this subset; those would be valuable because lifecycle bugs can leak refs or mounts.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/forwarder/forward.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/forwarder/frontend.go -->
# sources/cloud-native/buildkit/frontend/gateway/forwarder/frontend.go

## Purpose

This file wraps a gateway `client.BuildFunc` as a BuildKit `frontend.Frontend`. It is the lightweight in-process frontend adapter.

## Important APIs, Types, And Functions

- `NewGatewayForwarder` returns a `frontend.Frontend` backed by worker info and a build callback.
- `GatewayForwarder` stores worker info and the callback.
- `(*GatewayForwarder).Solve` constructs a `BridgeClient`, invokes the callback, and converts the result back to a frontend result.

## Control Flow

`Solve` calls `LLBBridgeToGatewayClient`, defers `c.discard(retErr)` so resources are released after result conversion or error, runs the callback, returns callback errors directly, and converts successful gateway results using `toFrontendResult`.

## State And Persistence Behavior

The forwarder itself only stores worker info and callback. Per-build state is held in `BridgeClient` and discarded at the end of `Solve`.

## Dependencies And Integration Points

It connects the generic frontend interface, executor, session manager, solver protobuf definitions, worker info, and gateway client build callbacks. It is used when BuildKit embeds a Go gateway frontend rather than launching a frontend image.

## Risks And Edge Cases

The deferred discard receives named return values so resource release can know whether the build failed. If result conversion returns an error, cloned result proxies are released by discard. Returning nil gateway results is allowed and converts to nil frontend results.

## Test Signals

`frontend_test.go` validates nil and empty gateway frontend results through integration builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/forwarder/frontend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/gateway.go -->
# sources/cloud-native/buildkit/frontend/gateway/gateway.go

## Purpose

This file implements the image-based BuildKit gateway frontend and the server-side LLBBridge gRPC service exposed to frontend containers. It loads an external frontend source, runs it as a container, forwards solve/source/container/filesystem/warning APIs over stdio, and converts returned protobuf results back into solver results.

## Important APIs, Types, And Functions

- `NewGatewayFrontend` parses optional allowed repositories and returns a `frontend.Frontend`.
- `gatewayFrontend.checkSourceIsAllowed` enforces source repository allowlists.
- `(*gatewayFrontend).Solve` loads the external frontend image/context, prepares metadata and environment, starts the bridge server, runs the frontend container, and returns its result.
- `metadataMount`, `bind`, and `bindMount` expose the current frontend definition at `/run/config/buildkit/metadata/frontend.bin`.
- `llbBridgeForwarder` implements `pb.LLBBridgeServer` with solve, source metadata, image config, reads, evaluate, ping, return, inputs, container, exec, warning, and cleanup behavior.
- `serveLLBBridgeForwarder`, `newPipe`, and `serve` create an HTTP/2 gRPC server over process stdio pipes.
- `processIO`, `outputWriter`, and `ExecProcess` implement multiplexed process stdin/stdout/stderr, resize, signal, started, exit, and done messages.
- Helper functions include `wrapSolveError`, `registerResultIDs`, `cloneRef`, `convertRef`, `ToPBResolveSourceMetaResponse`, checksum conversion, attestation-chain conversion, `getCaps`, and `addCapsForKnownFrontends`.

## Control Flow

`Solve` rejects deprecated gateway development mode, requires `frontend.KeySource`, checks allowlist, and creates a forwarder-backed docker UI client. If a named context for the source exists, it loads that; otherwise it resolves an image config for the source, pins digest when available, and builds an `llb.Image` marked as frontend usage. The source state is solved to a worker ref, converted to a mutable rootfs, and run with args/env/cwd derived from image config. Build options are injected as indexed `BUILDKIT_FRONTEND_OPT_N` environment variables, along with session ID, workers JSON, and exported product.

Capabilities are read from frontend image labels and requested `frontend.caps`; known legacy dockerfile frontend digests get input capability added manually. Unsupported requested caps return unimplemented solve errors. The bridge server is started over two pipes before executing the frontend. The frontend definition is mounted read-only as metadata. If executor run fails and the frontend did not already return an error/result, that run error becomes the gateway result.

The LLBBridge service maps protobuf calls to the underlying `FrontendLLBBridge`: resolving source metadata, resolving image config, solving LLB/frontend requests, reading refs, statting refs, evaluating refs, returning final results, exposing inputs, creating containers, reading container mounts, releasing containers, executing container processes, and sending warnings. Solve responses allocate opaque ref IDs and retain result proxies. Return clones refs so returned results outlive the server ref table.

`ExecProcess` maintains one bidirectional stream for all process messages. Init creates a process I/O pipe set, starts the target container process, sends Started before output, forwards output as file messages, turns process wait errors into Exit messages, handles nonzero exit as normal return data, and sends Done after file pipes close. Incoming File, Resize, and Signal messages are routed by process ID.

## State And Persistence Behavior

`gatewayFrontend` stores only immutable worker info and allowed repository names. `llbBridgeForwarder` stores per-run mutable state: ref ID map, worker ref ID map, final result/error, done channel, active containers, mounted snapshot mounters, pipe handles, and server-closed flag. Mutexes protect result/ref state, containers, and mount caches. `Discard` releases containers, unmounts mounters, releases worker refs, releases result refs on error, and releases outstanding refs.

Temporary metadata directories are created with `os.MkdirTemp` and removed by deferred release. Source rootfs mutable refs are released at the end of `Solve`. The gRPC server lifecycle is tied to a cancelable context and stdio pipe connection.

## Dependencies And Integration Points

This file is a central integration point for distribution reference parsing, docker UI named contexts, LLB source and solve APIs, executor, worker refs, cache managers, sessions, snapshot mounts, source metadata resolution, protobuf gateway service definitions, gRPC/http2 transport, tracing, API capability sets, warning APIs, image specs, signal maps, and typed gRPC errors.

## Risks And Edge Cases

Security and lifecycle risks are high. Allowed repositories must be normalized consistently because tags are stripped before comparison. Frontend images control entrypoint, env, labels, working directory, and requested caps. Build options are injected through environment variables, so parsing in the client must match the indexed `key=value` format. Resource cleanup spans rootfs refs, temporary metadata dirs, pipe connections, containers, mounts, result refs, and worker refs.

Concurrency risks include simultaneous gRPC calls mutating ref maps, process streams sending messages concurrently, and server shutdown racing with executor failure. The code uses thread-safe stream sending and locks, but send/receive ordering is delicate: Started is intentionally sent before output and before wait is allowed to send Exit. Capability compatibility paths are complex; older frontend images without caps labels get special cases only for known digests. `ReadFileContainer` and related APIs address containers by `Ref` field carrying container ID, which is semantically overloaded.

## Test Signals

`gateway_test.go` directly tests allowed source matching, including no restrictions, tag-insensitive repository matching, rejection of other repositories, and Docker Hub normalization for `alpine`. Broader integration tests exercise gateway reference operations. Missing focused tests include capability negotiation, frontend env option parsing, gRPC return formats, process I/O ordering, container release on errors, and source metadata conversion.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/gateway.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/gateway_test.go -->
# sources/cloud-native/buildkit/frontend/gateway/gateway_test.go

## Purpose

This file tests gateway frontend source allowlist behavior.

## Important APIs, Types, And Functions

- `TestCheckSourceIsAllowed` constructs gateway frontends with different allowed repositories and calls `checkSourceIsAllowed`.

## Control Flow

The test first verifies an empty allowlist permits any source. It then creates an allowlist with a fully tagged repository, confirms the same tagless repository and another tag are accepted because comparison trims tags, and confirms a different repository is rejected. Finally it verifies Docker Hub normalization makes `alpine`, `library/alpine`, and `docker.io/library/alpine` equivalent.

## State And Persistence Behavior

Only in-memory gateway frontend structs are created. No external state is modified.

## Dependencies And Integration Points

It uses `NewGatewayFrontend`, the concrete `gatewayFrontend`, distribution reference normalization indirectly, and `testify/require`.

## Risks And Edge Cases

The test covers tag-insensitive matching and Docker Hub normalization. It does not cover invalid allowlist entries, invalid source strings, digested sources, or registry case/normalization edge cases.

## Test Signals

This is the direct regression signal for repository allowlist behavior used before launching external gateway frontends.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/gateway_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/grpcclient/client.go -->
# sources/cloud-native/buildkit/frontend/gateway/grpcclient/client.go

## Purpose

This file implements the gRPC client used inside external frontend containers. It connects to the BuildKit gateway LLBBridge over stdio, exposes the public `client.Client` API, performs capability negotiation and compatibility fallbacks, returns final results, resolves metadata, runs gateway exec containers, and represents remote refs.

## Important APIs, Types, And Functions

- `GrpcClient` extends `client.Client` with `Run`.
- `New`, `current`, `RunFromEnvironment`, `grpcClientConn`, and `stdioConn` initialize the client from explicit parameters or BuildKit environment.
- `grpcClient.Run` runs a `client.BuildFunc` and sends a `Return` request or old inline final solve.
- `defaultCaps` and `defaultLLBCaps` define frozen fallback capabilities for older servers.
- `Solve`, `ResolveSourceMetadata`, `ResolveImageConfig`, `BuildOpts`, `CurrentFrontend`, `Inputs`, and `Warn` implement core client operations.
- `messageForwarder`, `procMessageForwarder`, `msgWriter`, `container`, and `containerProcess` implement gateway exec process stream handling.
- `reference` implements remote ref filesystem and state APIs.
- Environment helpers `opts`, `sessionID`, `workers`, and `product` parse gateway runtime environment.

## Control Flow

`New` pings the server with a timeout, fills missing capability lists with defaults, and creates a grpc client with an exec message forwarder. `Run` decides whether the server supports explicit `Return`; if so, it defers conversion of the build result or error into `ReturnRequest`. Without `Return`, it uses the legacy inline final solve path by marking the solve request for the returned ref as final and serializing metadata into exporter attrs. It always releases the exec message forwarder at the end.

`Solve` checks LLB metadata caps, propagates cache import options from top-level build opts when absent, sends a protobuf solve request, handles evaluate either natively or by deferred `StatFile(".")`, then converts deprecated or modern ref wire formats and attestations to client results. `ResolveSourceMetadata` uses the new source-meta resolver when supported; otherwise it falls back to image config resolution only for docker-image/oci-layout and rejects newer image attestation or HTTP checksum features. `ResolveImageConfig` similarly prefers source metadata when supported, else uses the older resolve-image RPC.

Gateway exec uses a single shared stream. `NewContainer` sends container creation, starts the stream once, and returns a remote container handle. `container.Start` registers a process ID, sends Init with requested file descriptors, waits for Started, forwards stdin as file messages, receives output/exit/done messages, converts nonzero exits to `pb.ExitError`, and deregisters on wait. Resize and Signal become stream messages with capability/known-signal checks. Container filesystem methods require `CapGatewayExecFilesystem`.

## State And Persistence Behavior

`grpcClient` stores server caps, LLB caps, build opts, session ID, worker list, a map from returned ref IDs to solve requests for legacy final return, and a long-lived message forwarder. The message forwarder owns a context, one exec stream, per-process message channels, a start-once guard, and stored start error. Remote refs contain their ID and optional definition. No durable filesystem state is created except reading `/run/config/buildkit/metadata/frontend.bin` in `CurrentFrontend`.

## Dependencies And Integration Points

It integrates with gateway protobuf client stubs, grpc interceptors, insecure stdio transport, `llb`, source resolver options, image utility rewrite errors, API caps, solver protobuf caps, typed grpc errors, signal maps, filesystem stat types, Open Containers descriptors/platforms/digests, and the public gateway client interfaces.

## Risks And Edge Cases

Compatibility logic is dense. Capability polarity must be read carefully because `Supports` returns nil on support. Old servers may omit caps and get default caps; changing defaults would break compatibility. In `Run`, the deferred exec release assignment appears to set `retError = err` when both `err != nil` and `retError != nil`, which would replace an existing build error with release error rather than preserve the original; this may be intentional but is worth review. Process stream handling depends on Started, Exit, Done ordering and can block if stdin is an interactive source; the code intentionally keeps stdin copy outside the errgroup. Result attestation conversion assumes `a.Ref` is non-nil before checking `a.Ref.Id` in `Solve`, which could panic if protobuf attestations omit a ref. Environment option parsing trusts the `BUILDKIT_FRONTEND_OPT_N=key=value` format.

## Test Signals

No direct tests in this subset cover grpc client behavior. Integration tests exercise the client indirectly inside external frontend scenarios elsewhere. Needed targeted tests include Run return/legacy paths, capability fallbacks, source metadata fallback errors, attestation ref nil handling, process I/O exit conversion, and environment option parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/grpcclient/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/pb/caps.go -->
# sources/cloud-native/buildkit/frontend/gateway/pb/caps.go

## Purpose

This file defines the gateway frontend API capability IDs and registers them in a global `apicaps.CapList`. Capabilities document and gate wire/API features for compatibility between frontend clients and BuildKit daemons.

## Important APIs, Types, And Functions

- `Caps` is the global gateway capability list.
- Capability constants include solve, inline return, image resolution, file read, explicit return, result maps, read dir, stat file, cache imports, proto ref arrays, reference output, frontend inputs, gateway metadata, exec, exec extra hosts, secret env, signals, exec filesystem, frontend caps, evaluate, warnings, attestations, and source metadata resolver feature levels.
- `init` registers each capability with ID, optional name, enabled state, status, and deprecation flag.

## Control Flow

During package initialization, every capability is added to `Caps`. Most are enabled experimental capabilities. `CapSolveInlineReturn` is marked deprecated. The comments establish the compatibility policy: non-compatible changes need new capability rows, experimental by default, immutable after merge, and stable capabilities should not be disabled.

## State And Persistence Behavior

`Caps` is global package state initialized once. It is exported through gateway ping responses and converted into capability sets by clients and forwarders. It is not persisted to disk.

## Dependencies And Integration Points

It depends on `util/apicaps`. Server-side `Ping` returns `pb.Caps.All()`, the grpc client checks support before optional API calls, and gateway image frontend label checks compare requested frontend capabilities with labels.

## Risks And Edge Cases

Capability IDs are wire contracts and must not be renamed. Some comments are copy-paste inaccurate for secret env and signals, but the IDs and names are distinct. Adding a feature without gating it here can break old clients or servers. Marking capabilities enabled by default means unsupported implementations must not advertise them.

## Test Signals

No direct tests are in this subset. Compatibility is exercised indirectly by grpc client and server integration. Snapshot-style tests over the cap list could catch accidental ID changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/pb/caps.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/pb/exit.go -->
# sources/cloud-native/buildkit/frontend/gateway/pb/exit.go

## Purpose

This file defines the typed gateway exec exit error used to carry container process exit status over gRPC error details and local APIs.

## Important APIs, Types, And Functions

- `UnknownExitStatus` is the sentinel exit status `255` for cases where a process never starts or exit status cannot be obtained.
- Package `init` registers `ExitMessage` with `typeurl` for typed error conversion.
- `ExitError` stores `ExitCode` and wrapped `Err`.
- `(*ExitError).ToProto`, `Error`, and `Unwrap` implement typed gRPC error and normal Go error behavior.
- `(*ExitMessage).WrapError` reconstructs an `ExitError` from protobuf error details.

## Control Flow

When a process exits nonzero, gateway server/client code wraps status information in `ExitMessage`/`ExitError`. `Error` delegates to the wrapped error message when present, otherwise formats the exit code. `WrapError` is called by typed error conversion to attach the code to a received error.

## State And Persistence Behavior

Only global type registration is performed. Exit errors are transient process results.

## Dependencies And Integration Points

It integrates with `containerd/typeurl` and BuildKit `grpcerrors.TypedErrorProto`. `gateway.go` emits exit messages from `ExecProcess`, and `grpcclient/client.go` converts received nonzero exit messages into `pb.ExitError`.

## Risks And Edge Cases

`UnknownExitStatus` is intentionally aligned with containerd behavior without importing containerd. If a real process exits 255, callers must distinguish context from wrapped error details. If `Err` is nil, the error text is a plain exit-code message.

## Test Signals

No direct tests are in this subset. Useful coverage would assert typed registration round trips, wrapping/unwrapping behavior, and nonzero process exit conversion in gateway exec.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/gateway/pb/exit.go -->
