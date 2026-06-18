# subset-b-000030 Research

Grouped source-tree-aligned research for the 123 BuildKit files assigned to subset-b-000030. Each section preserves the original source path for reconciliation into per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/pb/policy_vtproto.pb.go -->
# sources/cloud-native/buildkit/sourcepolicy/pb/policy_vtproto.pb.go

## Purpose
Generated vtprotobuf fast-path methods for source policy protobuf messages. It adds CloneVT, EqualVT, MarshalVT/MarshalToSizedBufferVT, SizeVT, and UnmarshalVT for Rule, Update, Selector, AttrConstraint, and Policy.

## Important APIs, Types, And Functions
Package: `moby_buildkit_v1_sourcepolicy`. Build tags: `none`. Key declarations observed in the file: `CloneVT, CloneMessageVT, EqualVT, EqualMessageVT, MarshalVT, MarshalToVT, MarshalToSizedBufferVT, SizeVT, UnmarshalVT`.

## Control Flow, State, And Persistence
Control flow is generated per-message serialization/deserialization with explicit field tags, repeated field loops, map/list cloning, size precomputation, and unknown-field skipping. It has no persistence beyond protobuf byte slices.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/planetscale/vtprotobuf/protohelpers, google.golang.org/protobuf/proto, google.golang.org/protobuf/runtime/protoimpl`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are generated-code drift from policy.proto and malformed protobuf inputs. Test signal comes from protobuf generation consistency and sourcepolicy policy tests, not handwritten unit tests here.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/pb/policy_vtproto.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/policysession/denyerror.go -->
# sources/cloud-native/buildkit/sourcepolicy/policysession/denyerror.go

## Purpose
Typed deny-message error propagation for source policy decisions. It registers DecisionResponse with typeurl, wraps ordinary errors with repeated DenyMessage details, exposes Unwrap/ToProto for grpcerrors, and recursively extracts messages from an error chain.

## Important APIs, Types, And Functions
Package: `policysession`. Build tags: `none`. Key declarations observed in the file: `init, DenyMessagesError, Unwrap, ToProto, WrapDenyMessages, DenyMessages, WrapError`.

## Control Flow, State, And Persistence
The only state is the error chain; no persistence. Control flow preserves the wrapped error as the causal error and appends nested deny messages outermost after recursively collected inner messages.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/typeurl/v2, github.com/moby/buildkit/sourcepolicy/pb, github.com/moby/buildkit/util/grpcerrors, github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is loss of user-facing policy diagnostics if callers wrap errors without preserving the chain. Test signal is indirect through grpc typed error handling and policy-session use, not a local unit test.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/policysession/denyerror.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/policysession/policysession.pb.go -->
# sources/cloud-native/buildkit/sourcepolicy/policysession/policysession.pb.go

## Purpose
Generated Go protobuf definitions for the policy-session RPC contract. It defines CheckPolicyRequest, CheckPolicyResponse oneof wrappers, DecisionResponse, and DenyMessage plus descriptors/getters.

## Important APIs, Types, And Functions
Package: `policysession`. Build tags: `none`. Key declarations observed in the file: `CheckPolicyRequest, Reset, String, ProtoMessage, ProtoReflect, Descriptor, GetPlatform, GetSource, GetCaps, CheckPolicyResponse, GetResult, GetDecision, ...`.

## Control Flow, State, And Persistence
Control flow is protobuf runtime reflection and accessor code generated from policysession.proto. It stores request/response fields in memory only and integrates with frontend gateway, solver SourceOp, and sourcepolicy PolicyAction types.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/moby/buildkit/frontend/gateway/pb, github.com/moby/buildkit/solver/pb, github.com/moby/buildkit/sourcepolicy/pb, google.golang.org/protobuf/reflect/protoreflect, google.golang.org/protobuf/runtime/protoimpl`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are schema compatibility and oneof handling across clients. Runtime behavior is tested indirectly through provider/verifier integration.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/policysession/policysession.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/policysession/policysession.proto -->
# sources/cloud-native/buildkit/sourcepolicy/policysession/policysession.proto

## Purpose
Protocol schema for source policy verification sessions. It defines a unary PolicyVerifier.CheckPolicy RPC that can return either a policy decision or a metadata-resolution request.

## Important APIs, Types, And Functions
Package: `moby`. Build tags: `none`. Key declarations observed in the file: `none exported locally`.

## Control Flow, State, And Persistence
The request carries target Platform, ResolveSourceMetaResponse source metadata, and capability booleans. The response oneof is DecisionResponse or ResolveSourceMetaRequest; decisions include action, deny messages, and optional SourceOp update.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/moby/buildkit/frontend/gateway/pb/gateway.proto, github.com/moby/buildkit/solver/pb/ops.proto, github.com/moby/buildkit/sourcepolicy/pb/policy.proto`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are oneof/schema compatibility and cross-package imports from gateway, solver ops, and sourcepolicy policy schema. Generated Go/gRPC/vtproto files are derived from it.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/policysession/policysession.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/policysession/policysession_grpc.pb.go -->
# sources/cloud-native/buildkit/sourcepolicy/policysession/policysession_grpc.pb.go

## Purpose
Generated Go protobuf definitions for the policy-session RPC contract. It defines CheckPolicyRequest, CheckPolicyResponse oneof wrappers, DecisionResponse, and DenyMessage plus descriptors/getters.

## Important APIs, Types, And Functions
Package: `policysession`. Build tags: `none`. Key declarations observed in the file: `_, PolicyVerifierClient, policyVerifierClient, NewPolicyVerifierClient, CheckPolicy, PolicyVerifierServer, UnimplementedPolicyVerifierServer, testEmbeddedByValue, UnsafePolicyVerifierServer, RegisterPolicyVerifierServer, _PolicyVerifier_CheckPolicy_Handler, PolicyVerifier_ServiceDesc`.

## Control Flow, State, And Persistence
Control flow is protobuf runtime reflection and accessor code generated from policysession.proto. It stores request/response fields in memory only and integrates with frontend gateway, solver SourceOp, and sourcepolicy PolicyAction types.

## Dependencies And Integration Points
Important dependencies/imports: `google.golang.org/grpc, google.golang.org/grpc/codes, google.golang.org/grpc/status`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are schema compatibility and oneof handling across clients. Runtime behavior is tested indirectly through provider/verifier integration.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/policysession/policysession_grpc.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/policysession/policysession_vtproto.pb.go -->
# sources/cloud-native/buildkit/sourcepolicy/policysession/policysession_vtproto.pb.go

## Purpose
Generated vtprotobuf fast-path methods for policy-session messages. It covers CheckPolicyRequest, CheckPolicyResponse oneofs, DecisionResponse, and DenyMessage.

## Important APIs, Types, And Functions
Package: `policysession`. Build tags: `none`. Key declarations observed in the file: `CloneVT, CloneMessageVT, EqualVT, EqualMessageVT, MarshalVT, MarshalToVT, MarshalToSizedBufferVT, SizeVT, UnmarshalVT`.

## Control Flow, State, And Persistence
Control flow clones nested platform/source/cap maps, serializes oneof variants and repeated deny messages, and unmarshals protobuf wire data with unknown-field handling. It holds no durable state.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/moby/buildkit/frontend/gateway/pb, github.com/moby/buildkit/solver/pb, github.com/moby/buildkit/sourcepolicy/pb, github.com/planetscale/vtprotobuf/protohelpers, google.golang.org/protobuf/proto, google.golang.org/protobuf/runtime/protoimpl`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are regeneration drift from policysession.proto and oneof/map wire compatibility. Integration depends on gRPC policy verifier traffic.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/policysession/policysession_vtproto.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/policysession/provider.go -->
# sources/cloud-native/buildkit/sourcepolicy/policysession/provider.go

## Purpose
Server-side adapter for the PolicyVerifier gRPC service. PolicyCallback returns either a final DecisionResponse or a ResolveSourceMetaRequest asking the client/front-end to resolve more metadata.

## Important APIs, Types, And Functions
Package: `policysession`. Build tags: `none`. Key declarations observed in the file: `PolicyCallback, PolicyProvider, NewPolicyProvider, CheckPolicy, Register`.

## Control Flow, State, And Persistence
CheckPolicy delegates to the callback and enforces the oneof invariant that decision and meta request cannot both be returned. Register binds the provider to a grpc.Server.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/moby/buildkit/frontend/gateway/pb, github.com/pkg/errors, google.golang.org/grpc`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is callback contract misuse causing an error response. Tests are not local; generated gRPC and verifier integration are the main signals.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/policysession/provider.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/policysession/verifier.go -->
# sources/cloud-native/buildkit/sourcepolicy/policysession/verifier.go

## Purpose
Client-side session adapter for policy verification. It locates a BuildKit session by group id and constructs a generated PolicyVerifierClient over the session connection.

## Important APIs, Types, And Functions
Package: `policysession`. Build tags: `none`. Key declarations observed in the file: `NewVerifier, PolicyVerifier, Check`.

## Control Flow, State, And Persistence
NewVerifier depends on session.Manager.Get(ctx,gid,false); Check is a thin unary RPC wrapper over CheckPolicy. It holds no persistent state beyond the client handle.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/moby/buildkit/session`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is session lookup or RPC failure surfacing directly to callers. Test signal is integration-level because this file has no local test.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/policysession/verifier.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/apicaps/caps.go -->
# sources/cloud-native/buildkit/util/apicaps/caps.go

## Purpose
Capability registry and negotiation helper for BuildKit APIs. CapList defines known capabilities; CapSet compares a remote APICap list against local definitions; CapError produces actionable unsupported/disabled messages.

## Important APIs, Types, And Functions
Package: `apicaps`. Build tags: `none`. Key declarations observed in the file: `PBCap, ExportedProduct, CapStatus, CapID, Cap, CapList, Init, All, CapSet, Supports, Contains, CapError, ...`.

## Control Flow, State, And Persistence
Init populates an in-memory map, All emits sorted protobuf state, CapSet indexes remote capabilities by ID, Supports checks definition existence, remote presence, and enabled state. No disk persistence.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/moby/buildkit/util/apicaps/pb, github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are non-concurrent Init and message quality depending on ExportedProduct/SupportedHint. caps_test.go validates disabled-cap error behavior.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/apicaps/caps.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/apicaps/caps_test.go -->
# sources/cloud-native/buildkit/util/apicaps/caps_test.go

## Purpose
caps_test.go belongs to package apicaps and supports the BuildKit utility/source-policy area represented by its directory. Key declarations: TestDisabledCap.

## Important APIs, Types, And Functions
Package: `apicaps`. Build tags: `none`. Key declarations observed in the file: `TestDisabledCap`.

## Control Flow, State, And Persistence
Build tags: none. Important dependencies: github.com/moby/buildkit/util/apicaps/pb. Control flow is local to the declarations above and holds no persistent state unless noted by its package-level maps, globals, or content/database handles.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/moby/buildkit/util/apicaps/pb`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks and tests should be interpreted at package level: generated files risk schema drift, platform shims risk build-tag coverage, and utility files rely on adjacent tests or integration paths.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/apicaps/caps_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/apicaps/pb/caps.pb.go -->
# sources/cloud-native/buildkit/util/apicaps/pb/caps.pb.go

## Purpose
Generated Go protobuf definition for APICap. It exposes ID, Enabled, Deprecated, DisabledReason, DisabledReasonMsg, and DisabledAlternative fields used by capability negotiation.

## Important APIs, Types, And Functions
Package: `moby_buildkit_v1_apicaps`. Build tags: `none`. Key declarations observed in the file: `APICap, Reset, String, ProtoMessage, ProtoReflect, Descriptor, GetID, GetEnabled, GetDeprecated, GetDisabledReason, GetDisabledReasonMsg, GetDisabledAlternative, ...`.

## Control Flow, State, And Persistence
Control flow is protobuf reflection/getter boilerplate generated from caps.proto. No persistence; callers serialize or exchange APICap messages over API boundaries.

## Dependencies And Integration Points
Important dependencies/imports: `google.golang.org/protobuf/reflect/protoreflect, google.golang.org/protobuf/runtime/protoimpl`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are schema evolution and generated/runtime version drift. util/apicaps/caps_test.go validates consumer behavior for enabled/disabled states.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/apicaps/pb/caps.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/apicaps/pb/caps.proto -->
# sources/cloud-native/buildkit/util/apicaps/pb/caps.proto

## Purpose
Protocol schema for API capability advertisements. APICap is the wire format exchanged between clients and services to describe support, disablement, and alternatives.

## Important APIs, Types, And Functions
Package: `moby`. Build tags: `none`. Key declarations observed in the file: `none exported locally`.

## Control Flow, State, And Persistence
Fields are scalar and backward-compatible when appended. No control flow in the proto itself; generated code and apicaps.CapList consume it.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are field semantic drift, especially Deprecated and DisabledAlternative. caps.go and caps_test.go are the behavior consumers.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/apicaps/pb/caps.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/apicaps/pb/caps_vtproto.pb.go -->
# sources/cloud-native/buildkit/util/apicaps/pb/caps_vtproto.pb.go

## Purpose
Generated vtprotobuf fast-path methods for APICap. It provides CloneVT, EqualVT, MarshalVT, SizeVT, and UnmarshalVT optimized for capability negotiation.

## Important APIs, Types, And Functions
Package: `moby_buildkit_v1_apicaps`. Build tags: `none`. Key declarations observed in the file: `CloneVT, CloneMessageVT, EqualVT, EqualMessageVT, MarshalVT, MarshalToVT, MarshalToSizedBufferVT, SizeVT, UnmarshalVT`.

## Control Flow, State, And Persistence
Control flow serializes scalar string/bool fields and skips unknown wire fields. State is transient protobuf byte buffers only.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/planetscale/vtprotobuf/protohelpers, google.golang.org/protobuf/proto, google.golang.org/protobuf/runtime/protoimpl`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are generated-code drift from caps.proto and malformed wire input. caps_test.go exercises the higher-level APICap consumer rather than this generated file directly.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/apicaps/pb/caps_vtproto.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/appcontext/appcontext.go -->
# sources/cloud-native/buildkit/util/appcontext/appcontext.go

## Purpose
Process-wide application context for CLI tools. It creates static Context and Shutdown contexts that react to termination signals.

## Important APIs, Types, And Functions
Package: `appcontext`. Build tags: `none`. Key declarations observed in the file: `Context, Shutdown, initContexts`.

## Control Flow, State, And Persistence
sync.Once initializes signal.Notify on platform-specific terminationSignals, runs registered initializers, cancels appContext on first signal, cancels shutdownContext on second, and fatally logs on third. State is process-global only.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/moby/buildkit/util/bklog, github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is global lifetime/orphan goroutine behavior and late Register calls after initialization having no effect. No local tests.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/appcontext/appcontext.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/appcontext/appcontext_unix.go -->
# sources/cloud-native/buildkit/util/appcontext/appcontext_unix.go

## Purpose
Unix signal list for appcontext. It maps terminationSignals to SIGTERM and SIGINT.

## Important APIs, Types, And Functions
Package: `appcontext`. Build tags: `!windows`. Key declarations observed in the file: `terminationSignals`.

## Control Flow, State, And Persistence
Build-tagged for non-Windows; appcontext.go consumes the slice during signal.Notify. No state beyond the package variable.

## Dependencies And Integration Points
Important dependencies/imports: `golang.org/x/sys/unix`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is platform signal behavior; build tags are the main test signal.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/appcontext/appcontext_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/appcontext/appcontext_windows.go -->
# sources/cloud-native/buildkit/util/appcontext/appcontext_windows.go

## Purpose
Windows signal list for appcontext. It maps terminationSignals to os.Interrupt.

## Important APIs, Types, And Functions
Package: `appcontext`. Build tags: `none`. Key declarations observed in the file: `terminationSignals`.

## Control Flow, State, And Persistence
Build-tagged for Windows; appcontext.go consumes the slice during signal.Notify. No persistence.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is Windows console signal semantics; build tags are the test signal.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/appcontext/appcontext_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/appcontext/register.go -->
# sources/cloud-native/buildkit/util/appcontext/register.go

## Purpose
Registration hook for app context initializers. Initializer functions transform the base context during first app context creation.

## Important APIs, Types, And Functions
Package: `appcontext`. Build tags: `none`. Key declarations observed in the file: `Initializer, inits, Register`.

## Control Flow, State, And Persistence
Register appends to a package-level slice read by initContexts. It is intentionally simple and not synchronized against concurrent registration/initialization.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is ordering/race sensitivity if used after Context/Shutdown has already initialized. No local tests.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/appcontext/register.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/appdefaults/appdefaults.go -->
# sources/cloud-native/buildkit/util/appdefaults/appdefaults.go

## Purpose
Shared default network constants for BuildKit. It defines BridgeName buildkit0 and BridgeSubnet 10.10.0.0/16.

## Important APIs, Types, And Functions
Package: `appdefaults`. Build tags: `none`. Key declarations observed in the file: `none exported locally`.

## Control Flow, State, And Persistence
No control flow or state. Platform-specific appdefaults files add socket/root/config defaults.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is collisions with local network configuration. No tests.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/appdefaults/appdefaults.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/appdefaults/appdefaults_linux.go -->
# sources/cloud-native/buildkit/util/appdefaults/appdefaults_linux.go

## Purpose
Linux system defaults for BuildKit daemon sockets. It sets Address to unix:///run/buildkit/buildkitd.sock and traceSocketPath under /run/buildkit.

## Important APIs, Types, And Functions
Package: `appdefaults`. Build tags: `none`. Key declarations observed in the file: `none exported locally`.

## Control Flow, State, And Persistence
No control flow; appdefaults_unix.go uses traceSocketPath in TraceSocketPath. Build tags select this on Linux.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is distribution path differences. No local tests.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/appdefaults/appdefaults_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/appdefaults/appdefaults_unix.go -->
# sources/cloud-native/buildkit/util/appdefaults/appdefaults_unix.go

## Purpose
Unix default paths and user-scoped BuildKit locations. It derives sockets, root/config paths, CNI config, CDI dirs, and trace socket location from XDG or HOME environment variables.

## Important APIs, Types, And Functions
Package: `appdefaults`. Build tags: `!windows`. Key declarations observed in the file: `UserAddress, EnsureUserAddressDir, UserRoot, UserConfigDir, TraceSocketPath`.

## Control Flow, State, And Persistence
UserAddress/UserRoot/UserConfigDir parse colon-separated XDG paths and fall back to system defaults. EnsureUserAddressDir creates buildkit under XDG_RUNTIME_DIR with 0700 sticky permissions using os.OpenRoot.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are environment-dependent paths and permission errors. Platform build tags split Linux, non-Linux Unix, and Windows defaults; no local tests.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/appdefaults/appdefaults_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/appdefaults/appdefaults_unix_nolinux.go -->
# sources/cloud-native/buildkit/util/appdefaults/appdefaults_unix_nolinux.go

## Purpose
Non-Linux Unix system defaults for BuildKit daemon sockets. It uses /var/run/buildkit paths.

## Important APIs, Types, And Functions
Package: `appdefaults`. Build tags: `unix && !linux`. Key declarations observed in the file: `none exported locally`.

## Control Flow, State, And Persistence
No control flow beyond constants. Build tags select unix && !linux.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is OS-specific path convention mismatch. No local tests.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/appdefaults/appdefaults_unix_nolinux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/appdefaults/appdefaults_windows.go -->
# sources/cloud-native/buildkit/util/appdefaults/appdefaults_windows.go

## Purpose
Windows BuildKit default paths. It defines named-pipe Address, ProgramData-backed root/config, containerd CNI paths, and CDI spec directory.

## Important APIs, Types, And Functions
Package: `appdefaults`. Build tags: `none`. Key declarations observed in the file: `UserAddress, EnsureUserAddressDir, UserRoot, UserConfigDir, TraceSocketPath`.

## Control Flow, State, And Persistence
UserAddress returns Address and EnsureUserAddressDir is a no-op. UserCNIConfigPath and CDISpecDirs are package variables derived from environment variables at init time.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are ProgramData/ProgramFiles environment dependence and static init values. No local tests.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/appdefaults/appdefaults_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/386_binary.go -->
# sources/cloud-native/buildkit/util/archutil/386_binary.go

## Purpose
Generated embedded gzip-compressed executable probe for linux/386. The Binary386 constant is consumed by the matching supported check on non-native builds.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!386`. Key declarations observed in the file: `Binary386`.

## Control Flow, State, And Persistence
No runtime control flow in this file; check_unix.go decompresses the string to a temp executable and runs it through binfmt. Build tag !386 prevents compiling the probe constant on native 386 builds.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are stale generated probe bytes or mismatch with assembly fixture/generator. Validation is integration-level through SupportedPlatforms.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/386_binary.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/386_check.go -->
# sources/cloud-native/buildkit/util/archutil/386_check.go

## Purpose
Non-native linux/386 support probe wrapper. It calls check with the embedded Binary386 probe when this architecture is not the host build target.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!386`. Key declarations observed in the file: `i386Supported`.

## Control Flow, State, And Persistence
Control flow is one function, i386Supported, returning the check result. The probe may return an amd64 variant string or an execution error depending on architecture.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are binfmt/QEMU environment dependence. Build tags and archutil detection provide integration coverage.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/386_check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/386_check_386.go -->
# sources/cloud-native/buildkit/util/archutil/386_check_386.go

## Purpose
Native linux/386 support stub. On matching host architecture it reports support without executing a foreign probe.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `386`. Key declarations observed in the file: `i386Supported`.

## Control Flow, State, And Persistence
i386Supported returns empty variant and nil error, except amd64 native support is handled separately by go-archvariant in amd64_check_amd64.go.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is assuming the native runtime is executable for its own architecture. Build tags select this file only on matching GOARCH.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/386_check_386.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/amd64_binary.go -->
# sources/cloud-native/buildkit/util/archutil/amd64_binary.go

## Purpose
Generated embedded gzip-compressed executable probe for linux/amd64. The Binaryamd64 constant is consumed by the matching supported check on non-native builds.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!amd64`. Key declarations observed in the file: `Binaryamd64`.

## Control Flow, State, And Persistence
No runtime control flow in this file; check_unix.go decompresses the string to a temp executable and runs it through binfmt. Build tag !amd64 prevents compiling the probe constant on native amd64 builds.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are stale generated probe bytes or mismatch with assembly fixture/generator. Validation is integration-level through SupportedPlatforms.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/amd64_binary.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/amd64_check.go -->
# sources/cloud-native/buildkit/util/archutil/amd64_check.go

## Purpose
Non-native linux/amd64 support probe wrapper. It calls check with the embedded Binaryamd64 probe when this architecture is not the host build target.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!amd64`. Key declarations observed in the file: `amd64Supported`.

## Control Flow, State, And Persistence
Control flow is one function, amd64Supported, returning the check result. The probe may return an amd64 variant string or an execution error depending on architecture.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are binfmt/QEMU environment dependence. Build tags and archutil detection provide integration coverage.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/amd64_check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/amd64_check_amd64.go -->
# sources/cloud-native/buildkit/util/archutil/amd64_check_amd64.go

## Purpose
Native amd64 support detector. It returns the current AMD64 microarchitecture variant using github.com/tonistiigi/go-archvariant.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `amd64`. Key declarations observed in the file: `amd64Supported`.

## Control Flow, State, And Persistence
amd64Supported has no persistence and does not execute probe binaries on native amd64. detect.go expands the returned variant into v2/v3/v4 platform variants.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/tonistiigi/go-archvariant`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is variant detection dependency and consistency with OCI platform variant semantics. No local test.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/amd64_check_amd64.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/arm64_binary.go -->
# sources/cloud-native/buildkit/util/archutil/arm64_binary.go

## Purpose
Generated embedded gzip-compressed executable probe for linux/arm64. The Binaryarm64 constant is consumed by the matching supported check on non-native builds.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!arm64`. Key declarations observed in the file: `Binaryarm64`.

## Control Flow, State, And Persistence
No runtime control flow in this file; check_unix.go decompresses the string to a temp executable and runs it through binfmt. Build tag !arm64 prevents compiling the probe constant on native arm64 builds.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are stale generated probe bytes or mismatch with assembly fixture/generator. Validation is integration-level through SupportedPlatforms.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/arm64_binary.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/arm64_check.go -->
# sources/cloud-native/buildkit/util/archutil/arm64_check.go

## Purpose
Non-native linux/arm64 support probe wrapper. It calls check with the embedded Binaryarm64 probe when this architecture is not the host build target.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!arm64`. Key declarations observed in the file: `arm64Supported`.

## Control Flow, State, And Persistence
Control flow is one function, arm64Supported, returning the check result. The probe may return an amd64 variant string or an execution error depending on architecture.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are binfmt/QEMU environment dependence. Build tags and archutil detection provide integration coverage.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/arm64_check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/arm64_check_arm64.go -->
# sources/cloud-native/buildkit/util/archutil/arm64_check_arm64.go

## Purpose
Native linux/arm64 support stub. On matching host architecture it reports support without executing a foreign probe.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `arm64`. Key declarations observed in the file: `arm64Supported`.

## Control Flow, State, And Persistence
arm64Supported returns empty variant and nil error, except amd64 native support is handled separately by go-archvariant in amd64_check_amd64.go.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is assuming the native runtime is executable for its own architecture. Build tags select this file only on matching GOARCH.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/arm64_check_arm64.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/arm_binary.go -->
# sources/cloud-native/buildkit/util/archutil/arm_binary.go

## Purpose
Generated embedded gzip-compressed executable probe for linux/arm. The Binaryarm constant is consumed by the matching supported check on non-native builds.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!arm`. Key declarations observed in the file: `Binaryarm`.

## Control Flow, State, And Persistence
No runtime control flow in this file; check_unix.go decompresses the string to a temp executable and runs it through binfmt. Build tag !arm prevents compiling the probe constant on native arm builds.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are stale generated probe bytes or mismatch with assembly fixture/generator. Validation is integration-level through SupportedPlatforms.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/arm_binary.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/arm_check.go -->
# sources/cloud-native/buildkit/util/archutil/arm_check.go

## Purpose
Non-native linux/arm support probe wrapper. It calls check with the embedded Binaryarm probe when this architecture is not the host build target.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!arm`. Key declarations observed in the file: `armSupported`.

## Control Flow, State, And Persistence
Control flow is one function, armSupported, returning the check result. The probe may return an amd64 variant string or an execution error depending on architecture.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are binfmt/QEMU environment dependence. Build tags and archutil detection provide integration coverage.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/arm_check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/arm_check_arm.go -->
# sources/cloud-native/buildkit/util/archutil/arm_check_arm.go

## Purpose
Native linux/arm support stub. On matching host architecture it reports support without executing a foreign probe.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `arm`. Key declarations observed in the file: `armSupported`.

## Control Flow, State, And Persistence
armSupported returns empty variant and nil error, except amd64 native support is handled separately by go-archvariant in amd64_check_amd64.go.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is assuming the native runtime is executable for its own architecture. Build tags select this file only on matching GOARCH.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/arm_check_arm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/check_unix.go -->
# sources/cloud-native/buildkit/util/archutil/check_unix.go

## Purpose
Unix probe executor for archutil. It gunzips an embedded static probe binary into a temp chroot and runs /check to determine whether binfmt can execute it.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!windows`. Key declarations observed in the file: `withChroot, check`.

## Control Flow, State, And Persistence
check creates a temp directory, writes executable probe bytes, sets SysProcAttr.Chroot, runs /check, and special-cases amd64 exit code 65/66 for v1/v2. State is temporary filesystem only.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are requiring chroot/binfmt permissions and interpreting amd64 variants only up to v2 in this probe path. No direct unit test.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/check_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/check_windows.go -->
# sources/cloud-native/buildkit/util/archutil/check_windows.go

## Purpose
Windows archutil probe stub. Since binfmt is unsupported on Windows, check always returns an explanatory error.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `windows`. Key declarations observed in the file: `check`.

## Control Flow, State, And Persistence
No state or persistence; all foreign-arch probes fail through this function on Windows builds.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is callers must tolerate warnings/errors rather than cross-exec support. Build tags are the test signal.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/check_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/detect.go -->
# sources/cloud-native/buildkit/util/archutil/detect.go

## Purpose
Runtime platform support detector. It reports native platform plus Linux foreign architectures that can execute probe binaries through binfmt/QEMU.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `none`. Key declarations observed in the file: `CacheMaxAge, SupportedPlatforms, WarnIfUnsupported, nativePlatform, linux, amd64vector, printPlatformWarning`.

## Control Flow, State, And Persistence
SupportedPlatforms caches results under a mutex for CacheMaxAge, probes each architecture with arch-specific supported functions, adds amd64 variants and arm v6 aliases, and WarnIfUnsupported logs validation failures without dropping candidates.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/platforms, github.com/moby/buildkit/util/bklog, github.com/opencontainers/image-spec/specs-go/v1`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are stale cache, environment-dependent binfmt behavior, and warning text based on error substrings. Tests are mostly build/integration dependent; probe binaries and assembly fixtures are generated inputs.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/detect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/fixtures/exit.386.s -->
# sources/cloud-native/buildkit/util/archutil/fixtures/exit.386.s

## Purpose
Assembly fixture for the linux/386 archutil probe. It builds a tiny static program that exits successfully when executed under the target architecture.

## Important APIs, Types, And Functions
Package: `n/a`. Build tags: `none`. Key declarations observed in the file: `none exported locally`.

## Control Flow, State, And Persistence
The generator compresses the compiled fixture into the corresponding *_binary.go constant. Runtime control flow is just architecture-specific syscall exit code handling.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are assembler/toolchain portability and syscall-number correctness. Integration signal is whether archutil probes execute under binfmt/QEMU.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/fixtures/exit.386.s -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/fixtures/exit.amd64.S -->
# sources/cloud-native/buildkit/util/archutil/fixtures/exit.amd64.S

## Purpose
Assembly fixture for the linux/amd64 archutil probe. It builds a tiny static program that exits successfully when executed under the target architecture. The amd64 fixture also checks CPUID feature bits and exits with variant-coded status.

## Important APIs, Types, And Functions
Package: `n/a`. Build tags: `none`. Key declarations observed in the file: `none exported locally`.

## Control Flow, State, And Persistence
The generator compresses the compiled fixture into the corresponding *_binary.go constant. Runtime control flow is just architecture-specific syscall exit code handling.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are assembler/toolchain portability and syscall-number correctness. Integration signal is whether archutil probes execute under binfmt/QEMU.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/fixtures/exit.amd64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/fixtures/exit.arm.s -->
# sources/cloud-native/buildkit/util/archutil/fixtures/exit.arm.s

## Purpose
Assembly fixture for the linux/arm archutil probe. It builds a tiny static program that exits successfully when executed under the target architecture.

## Important APIs, Types, And Functions
Package: `n/a`. Build tags: `none`. Key declarations observed in the file: `none exported locally`.

## Control Flow, State, And Persistence
The generator compresses the compiled fixture into the corresponding *_binary.go constant. Runtime control flow is just architecture-specific syscall exit code handling.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are assembler/toolchain portability and syscall-number correctness. Integration signal is whether archutil probes execute under binfmt/QEMU.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/fixtures/exit.arm.s -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/fixtures/exit.arm64.s -->
# sources/cloud-native/buildkit/util/archutil/fixtures/exit.arm64.s

## Purpose
Assembly fixture for the linux/arm64 archutil probe. It builds a tiny static program that exits successfully when executed under the target architecture.

## Important APIs, Types, And Functions
Package: `n/a`. Build tags: `none`. Key declarations observed in the file: `none exported locally`.

## Control Flow, State, And Persistence
The generator compresses the compiled fixture into the corresponding *_binary.go constant. Runtime control flow is just architecture-specific syscall exit code handling.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are assembler/toolchain portability and syscall-number correctness. Integration signal is whether archutil probes execute under binfmt/QEMU.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/fixtures/exit.arm64.s -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/fixtures/exit.loongarch64.s -->
# sources/cloud-native/buildkit/util/archutil/fixtures/exit.loongarch64.s

## Purpose
Assembly fixture for the linux/loongarch64 archutil probe. It builds a tiny static program that exits successfully when executed under the target architecture.

## Important APIs, Types, And Functions
Package: `n/a`. Build tags: `none`. Key declarations observed in the file: `none exported locally`.

## Control Flow, State, And Persistence
The generator compresses the compiled fixture into the corresponding *_binary.go constant. Runtime control flow is just architecture-specific syscall exit code handling.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are assembler/toolchain portability and syscall-number correctness. Integration signal is whether archutil probes execute under binfmt/QEMU.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/fixtures/exit.loongarch64.s -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/fixtures/exit.mips64.s -->
# sources/cloud-native/buildkit/util/archutil/fixtures/exit.mips64.s

## Purpose
Assembly fixture for the linux/mips64 archutil probe. It builds a tiny static program that exits successfully when executed under the target architecture.

## Important APIs, Types, And Functions
Package: `n/a`. Build tags: `none`. Key declarations observed in the file: `none exported locally`.

## Control Flow, State, And Persistence
The generator compresses the compiled fixture into the corresponding *_binary.go constant. Runtime control flow is just architecture-specific syscall exit code handling.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are assembler/toolchain portability and syscall-number correctness. Integration signal is whether archutil probes execute under binfmt/QEMU.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/fixtures/exit.mips64.s -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/fixtures/exit.mips64le.s -->
# sources/cloud-native/buildkit/util/archutil/fixtures/exit.mips64le.s

## Purpose
Assembly fixture for the linux/mips64le archutil probe. It builds a tiny static program that exits successfully when executed under the target architecture.

## Important APIs, Types, And Functions
Package: `n/a`. Build tags: `none`. Key declarations observed in the file: `none exported locally`.

## Control Flow, State, And Persistence
The generator compresses the compiled fixture into the corresponding *_binary.go constant. Runtime control flow is just architecture-specific syscall exit code handling.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are assembler/toolchain portability and syscall-number correctness. Integration signal is whether archutil probes execute under binfmt/QEMU.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/fixtures/exit.mips64le.s -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/fixtures/exit.ppc64.s -->
# sources/cloud-native/buildkit/util/archutil/fixtures/exit.ppc64.s

## Purpose
Assembly fixture for the linux/ppc64 archutil probe. It builds a tiny static program that exits successfully when executed under the target architecture.

## Important APIs, Types, And Functions
Package: `n/a`. Build tags: `none`. Key declarations observed in the file: `none exported locally`.

## Control Flow, State, And Persistence
The generator compresses the compiled fixture into the corresponding *_binary.go constant. Runtime control flow is just architecture-specific syscall exit code handling.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are assembler/toolchain portability and syscall-number correctness. Integration signal is whether archutil probes execute under binfmt/QEMU.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/fixtures/exit.ppc64.s -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/fixtures/exit.ppc64le.s -->
# sources/cloud-native/buildkit/util/archutil/fixtures/exit.ppc64le.s

## Purpose
Assembly fixture for the linux/ppc64le archutil probe. It builds a tiny static program that exits successfully when executed under the target architecture.

## Important APIs, Types, And Functions
Package: `n/a`. Build tags: `none`. Key declarations observed in the file: `none exported locally`.

## Control Flow, State, And Persistence
The generator compresses the compiled fixture into the corresponding *_binary.go constant. Runtime control flow is just architecture-specific syscall exit code handling.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are assembler/toolchain portability and syscall-number correctness. Integration signal is whether archutil probes execute under binfmt/QEMU.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/fixtures/exit.ppc64le.s -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/fixtures/exit.riscv64.s -->
# sources/cloud-native/buildkit/util/archutil/fixtures/exit.riscv64.s

## Purpose
Assembly fixture for the linux/riscv64 archutil probe. It builds a tiny static program that exits successfully when executed under the target architecture.

## Important APIs, Types, And Functions
Package: `n/a`. Build tags: `none`. Key declarations observed in the file: `none exported locally`.

## Control Flow, State, And Persistence
The generator compresses the compiled fixture into the corresponding *_binary.go constant. Runtime control flow is just architecture-specific syscall exit code handling.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are assembler/toolchain portability and syscall-number correctness. Integration signal is whether archutil probes execute under binfmt/QEMU.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/fixtures/exit.riscv64.s -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/fixtures/exit.s390x.s -->
# sources/cloud-native/buildkit/util/archutil/fixtures/exit.s390x.s

## Purpose
Assembly fixture for the linux/s390x archutil probe. It builds a tiny static program that exits successfully when executed under the target architecture.

## Important APIs, Types, And Functions
Package: `n/a`. Build tags: `none`. Key declarations observed in the file: `none exported locally`.

## Control Flow, State, And Persistence
The generator compresses the compiled fixture into the corresponding *_binary.go constant. Runtime control flow is just architecture-specific syscall exit code handling.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are assembler/toolchain portability and syscall-number correctness. Integration signal is whether archutil probes execute under binfmt/QEMU.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/fixtures/exit.s390x.s -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/generate.go -->
# sources/cloud-native/buildkit/util/archutil/generate.go

## Purpose
go:build ignore generator that converts compiled fixture binaries into gzip-compressed Go string constants. It is used by make archutil rather than normal builds.

## Important APIs, Types, And Functions
Package: `main`. Build tags: `ignore`. Key declarations observed in the file: `main, hexStringWriter, newHexStringWriter, Write, tmpl, Binary`.

## Control Flow, State, And Persistence
For each input architecture file, it gzip-compresses bytes through a hex string writer and writes <arch>_binary.go from a template guarded by !<arch>.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are generator output depending on fixture correctness and file naming. Generated binary files in this group are its artifacts.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/generate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/loong64_binary.go -->
# sources/cloud-native/buildkit/util/archutil/loong64_binary.go

## Purpose
Generated embedded gzip-compressed executable probe for linux/loong64. The Binaryloong64 constant is consumed by the matching supported check on non-native builds.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!loong64`. Key declarations observed in the file: `Binaryloong64`.

## Control Flow, State, And Persistence
No runtime control flow in this file; check_unix.go decompresses the string to a temp executable and runs it through binfmt. Build tag !loong64 prevents compiling the probe constant on native loong64 builds.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are stale generated probe bytes or mismatch with assembly fixture/generator. Validation is integration-level through SupportedPlatforms.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/loong64_binary.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/loong64_check.go -->
# sources/cloud-native/buildkit/util/archutil/loong64_check.go

## Purpose
Non-native linux/loong64 support probe wrapper. It calls check with the embedded Binaryloong64 probe when this architecture is not the host build target.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!loong64`. Key declarations observed in the file: `loong64Supported`.

## Control Flow, State, And Persistence
Control flow is one function, loong64Supported, returning the check result. The probe may return an amd64 variant string or an execution error depending on architecture.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are binfmt/QEMU environment dependence. Build tags and archutil detection provide integration coverage.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/loong64_check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/loong64_check_loong64.go -->
# sources/cloud-native/buildkit/util/archutil/loong64_check_loong64.go

## Purpose
Native linux/loong64 support stub. On matching host architecture it reports support without executing a foreign probe.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `loong64`. Key declarations observed in the file: `loong64Supported`.

## Control Flow, State, And Persistence
loong64Supported returns empty variant and nil error, except amd64 native support is handled separately by go-archvariant in amd64_check_amd64.go.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is assuming the native runtime is executable for its own architecture. Build tags select this file only on matching GOARCH.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/loong64_check_loong64.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/mips64_binary.go -->
# sources/cloud-native/buildkit/util/archutil/mips64_binary.go

## Purpose
Generated embedded gzip-compressed executable probe for linux/mips64. The Binarymips64 constant is consumed by the matching supported check on non-native builds.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!mips64`. Key declarations observed in the file: `Binarymips64`.

## Control Flow, State, And Persistence
No runtime control flow in this file; check_unix.go decompresses the string to a temp executable and runs it through binfmt. Build tag !mips64 prevents compiling the probe constant on native mips64 builds.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are stale generated probe bytes or mismatch with assembly fixture/generator. Validation is integration-level through SupportedPlatforms.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/mips64_binary.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/mips64_check.go -->
# sources/cloud-native/buildkit/util/archutil/mips64_check.go

## Purpose
Non-native linux/mips64 support probe wrapper. It calls check with the embedded Binarymips64 probe when this architecture is not the host build target.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!mips64`. Key declarations observed in the file: `mips64Supported`.

## Control Flow, State, And Persistence
Control flow is one function, mips64Supported, returning the check result. The probe may return an amd64 variant string or an execution error depending on architecture.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are binfmt/QEMU environment dependence. Build tags and archutil detection provide integration coverage.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/mips64_check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/mips64_check_mips64.go -->
# sources/cloud-native/buildkit/util/archutil/mips64_check_mips64.go

## Purpose
Native linux/mips64 support stub. On matching host architecture it reports support without executing a foreign probe.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `mips64`. Key declarations observed in the file: `mips64Supported`.

## Control Flow, State, And Persistence
mips64Supported returns empty variant and nil error, except amd64 native support is handled separately by go-archvariant in amd64_check_amd64.go.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is assuming the native runtime is executable for its own architecture. Build tags select this file only on matching GOARCH.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/mips64_check_mips64.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/mips64le_binary.go -->
# sources/cloud-native/buildkit/util/archutil/mips64le_binary.go

## Purpose
Generated embedded gzip-compressed executable probe for linux/mips64le. The Binarymips64le constant is consumed by the matching supported check on non-native builds.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!mips64le`. Key declarations observed in the file: `Binarymips64le`.

## Control Flow, State, And Persistence
No runtime control flow in this file; check_unix.go decompresses the string to a temp executable and runs it through binfmt. Build tag !mips64le prevents compiling the probe constant on native mips64le builds.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are stale generated probe bytes or mismatch with assembly fixture/generator. Validation is integration-level through SupportedPlatforms.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/mips64le_binary.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/mips64le_check.go -->
# sources/cloud-native/buildkit/util/archutil/mips64le_check.go

## Purpose
Non-native linux/mips64le support probe wrapper. It calls check with the embedded Binarymips64le probe when this architecture is not the host build target.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!mips64le`. Key declarations observed in the file: `mips64leSupported`.

## Control Flow, State, And Persistence
Control flow is one function, mips64leSupported, returning the check result. The probe may return an amd64 variant string or an execution error depending on architecture.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are binfmt/QEMU environment dependence. Build tags and archutil detection provide integration coverage.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/mips64le_check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/mips64le_check_mips64le.go -->
# sources/cloud-native/buildkit/util/archutil/mips64le_check_mips64le.go

## Purpose
Native linux/mips64le support stub. On matching host architecture it reports support without executing a foreign probe.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `mips64le`. Key declarations observed in the file: `mips64leSupported`.

## Control Flow, State, And Persistence
mips64leSupported returns empty variant and nil error, except amd64 native support is handled separately by go-archvariant in amd64_check_amd64.go.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is assuming the native runtime is executable for its own architecture. Build tags select this file only on matching GOARCH.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/mips64le_check_mips64le.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/ppc64_binary.go -->
# sources/cloud-native/buildkit/util/archutil/ppc64_binary.go

## Purpose
Generated embedded gzip-compressed executable probe for linux/ppc64. The Binaryppc64 constant is consumed by the matching supported check on non-native builds.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!ppc64`. Key declarations observed in the file: `Binaryppc64`.

## Control Flow, State, And Persistence
No runtime control flow in this file; check_unix.go decompresses the string to a temp executable and runs it through binfmt. Build tag !ppc64 prevents compiling the probe constant on native ppc64 builds.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are stale generated probe bytes or mismatch with assembly fixture/generator. Validation is integration-level through SupportedPlatforms.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/ppc64_binary.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/ppc64_check.go -->
# sources/cloud-native/buildkit/util/archutil/ppc64_check.go

## Purpose
Non-native linux/ppc64 support probe wrapper. It calls check with the embedded Binaryppc64 probe when this architecture is not the host build target.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!ppc64`. Key declarations observed in the file: `ppc64Supported`.

## Control Flow, State, And Persistence
Control flow is one function, ppc64Supported, returning the check result. The probe may return an amd64 variant string or an execution error depending on architecture.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are binfmt/QEMU environment dependence. Build tags and archutil detection provide integration coverage.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/ppc64_check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/ppc64_check_ppc64.go -->
# sources/cloud-native/buildkit/util/archutil/ppc64_check_ppc64.go

## Purpose
Native linux/ppc64 support stub. On matching host architecture it reports support without executing a foreign probe.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `ppc64`. Key declarations observed in the file: `ppc64Supported`.

## Control Flow, State, And Persistence
ppc64Supported returns empty variant and nil error, except amd64 native support is handled separately by go-archvariant in amd64_check_amd64.go.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is assuming the native runtime is executable for its own architecture. Build tags select this file only on matching GOARCH.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/ppc64_check_ppc64.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/ppc64le_binary.go -->
# sources/cloud-native/buildkit/util/archutil/ppc64le_binary.go

## Purpose
Generated embedded gzip-compressed executable probe for linux/ppc64le. The Binaryppc64le constant is consumed by the matching supported check on non-native builds.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!ppc64le`. Key declarations observed in the file: `Binaryppc64le`.

## Control Flow, State, And Persistence
No runtime control flow in this file; check_unix.go decompresses the string to a temp executable and runs it through binfmt. Build tag !ppc64le prevents compiling the probe constant on native ppc64le builds.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are stale generated probe bytes or mismatch with assembly fixture/generator. Validation is integration-level through SupportedPlatforms.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/ppc64le_binary.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/ppc64le_check.go -->
# sources/cloud-native/buildkit/util/archutil/ppc64le_check.go

## Purpose
Non-native linux/ppc64le support probe wrapper. It calls check with the embedded Binaryppc64le probe when this architecture is not the host build target.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!ppc64le`. Key declarations observed in the file: `ppc64leSupported`.

## Control Flow, State, And Persistence
Control flow is one function, ppc64leSupported, returning the check result. The probe may return an amd64 variant string or an execution error depending on architecture.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are binfmt/QEMU environment dependence. Build tags and archutil detection provide integration coverage.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/ppc64le_check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/ppc64le_check_ppc64le.go -->
# sources/cloud-native/buildkit/util/archutil/ppc64le_check_ppc64le.go

## Purpose
Native linux/ppc64le support stub. On matching host architecture it reports support without executing a foreign probe.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `ppc64le`. Key declarations observed in the file: `ppc64leSupported`.

## Control Flow, State, And Persistence
ppc64leSupported returns empty variant and nil error, except amd64 native support is handled separately by go-archvariant in amd64_check_amd64.go.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is assuming the native runtime is executable for its own architecture. Build tags select this file only on matching GOARCH.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/ppc64le_check_ppc64le.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/riscv64_binary.go -->
# sources/cloud-native/buildkit/util/archutil/riscv64_binary.go

## Purpose
Generated embedded gzip-compressed executable probe for linux/riscv64. The Binaryriscv64 constant is consumed by the matching supported check on non-native builds.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!riscv64`. Key declarations observed in the file: `Binaryriscv64`.

## Control Flow, State, And Persistence
No runtime control flow in this file; check_unix.go decompresses the string to a temp executable and runs it through binfmt. Build tag !riscv64 prevents compiling the probe constant on native riscv64 builds.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are stale generated probe bytes or mismatch with assembly fixture/generator. Validation is integration-level through SupportedPlatforms.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/riscv64_binary.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/riscv64_check.go -->
# sources/cloud-native/buildkit/util/archutil/riscv64_check.go

## Purpose
Non-native linux/riscv64 support probe wrapper. It calls check with the embedded Binaryriscv64 probe when this architecture is not the host build target.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!riscv64`. Key declarations observed in the file: `riscv64Supported`.

## Control Flow, State, And Persistence
Control flow is one function, riscv64Supported, returning the check result. The probe may return an amd64 variant string or an execution error depending on architecture.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are binfmt/QEMU environment dependence. Build tags and archutil detection provide integration coverage.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/riscv64_check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/riscv64_check_riscv64.go -->
# sources/cloud-native/buildkit/util/archutil/riscv64_check_riscv64.go

## Purpose
Native linux/riscv64 support stub. On matching host architecture it reports support without executing a foreign probe.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `riscv64`. Key declarations observed in the file: `riscv64Supported`.

## Control Flow, State, And Persistence
riscv64Supported returns empty variant and nil error, except amd64 native support is handled separately by go-archvariant in amd64_check_amd64.go.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is assuming the native runtime is executable for its own architecture. Build tags select this file only on matching GOARCH.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/riscv64_check_riscv64.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/s390x_binary.go -->
# sources/cloud-native/buildkit/util/archutil/s390x_binary.go

## Purpose
Generated embedded gzip-compressed executable probe for linux/s390x. The Binarys390x constant is consumed by the matching supported check on non-native builds.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!s390x`. Key declarations observed in the file: `Binarys390x`.

## Control Flow, State, And Persistence
No runtime control flow in this file; check_unix.go decompresses the string to a temp executable and runs it through binfmt. Build tag !s390x prevents compiling the probe constant on native s390x builds.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are stale generated probe bytes or mismatch with assembly fixture/generator. Validation is integration-level through SupportedPlatforms.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/s390x_binary.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/s390x_check.go -->
# sources/cloud-native/buildkit/util/archutil/s390x_check.go

## Purpose
Non-native linux/s390x support probe wrapper. It calls check with the embedded Binarys390x probe when this architecture is not the host build target.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `!s390x`. Key declarations observed in the file: `s390xSupported`.

## Control Flow, State, And Persistence
Control flow is one function, s390xSupported, returning the check result. The probe may return an amd64 variant string or an execution error depending on architecture.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are binfmt/QEMU environment dependence. Build tags and archutil detection provide integration coverage.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/s390x_check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/s390x_check_s390x.go -->
# sources/cloud-native/buildkit/util/archutil/s390x_check_s390x.go

## Purpose
Native linux/s390x support stub. On matching host architecture it reports support without executing a foreign probe.

## Important APIs, Types, And Functions
Package: `archutil`. Build tags: `s390x`. Key declarations observed in the file: `s390xSupported`.

## Control Flow, State, And Persistence
s390xSupported returns empty variant and nil error, except amd64 native support is handled separately by go-archvariant in amd64_check_amd64.go.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is assuming the native runtime is executable for its own architecture. Build tags select this file only on matching GOARCH.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/archutil/s390x_check_s390x.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/attestation/types.go -->
# sources/cloud-native/buildkit/util/attestation/types.go

## Purpose
Constants for Docker attestation manifest annotations. They name reference type, digest, description, and the default reference type value.

## Important APIs, Types, And Functions
Package: `attestation`. Build tags: `none`. Key declarations observed in the file: `none exported locally`.

## Control Flow, State, And Persistence
No control flow or state; other exporter/attestation code consumes these strings when annotating OCI artifacts.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is annotation key compatibility with Docker consumers. No local tests.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/attestation/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/bklog/log.go -->
# sources/cloud-native/buildkit/util/bklog/log.go

## Purpose
BuildKit logging bridge. It installs BuildKit/containerd log functions, stores logrus entries in context, and adds OpenTelemetry trace/span IDs when present.

## Important APIs, Types, And Functions
Package: `bklog`. Build tags: `none`. Key declarations observed in the file: `init, WithLogger, GetLogger, TraceLevelOnlyStack`.

## Control Flow, State, And Persistence
init overrides containerd/log globals. WithLogger stores a context value; GetLogger prefers that value, then containerd log, then package default. TraceLevelOnlyStack only calls debug.Stack when trace logging is enabled.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/log, github.com/sirupsen/logrus`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are global logger mutation, context value type assertions, and logging cost at trace level. No local tests.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/bklog/log.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/bkmaps/syncmap.go -->
# sources/cloud-native/buildkit/util/bkmaps/syncmap.go

## Purpose
Generic typed wrapper around sync.Map. It provides Delete, Load, LoadOrStore, Range, and Store without repeated type assertions at call sites.

## Important APIs, Types, And Functions
Package: `bkmaps`. Build tags: `none`. Key declarations observed in the file: `SyncMap, Delete, Load, LoadOrStore, Range, Store`.

## Control Flow, State, And Persistence
State is the embedded sync.Map. Methods type-assert keys/values to K/V and return zero values when absent.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is panic if mixed untyped access stores incompatible values. No local tests.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/bkmaps/syncmap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/bkslices/dedupe.go -->
# sources/cloud-native/buildkit/util/bkslices/dedupe.go

## Purpose
Generic stable de-duplication helper. It returns the first occurrence of each comparable value while preserving input order.

## Important APIs, Types, And Functions
Package: `bkslices`. Build tags: `none`. Key declarations observed in the file: `Dedupe`.

## Control Flow, State, And Persistence
Control flow keeps a seen map and appends unseen values to an output slice preallocated to input length. No persistence.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is memory proportional to input cardinality. No local tests.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/bkslices/dedupe.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/cachedigest/db.go -->
# sources/cloud-native/buildkit/util/cachedigest/db.go

## Purpose
Bolt-backed debug database for mapping content digests to encoded debug frames. It supports default DB registration, async frame persistence, lookup, and iteration.

## Important APIs, Types, And Functions
Package: `cachedigest`. Build tags: `none`. Key declarations observed in the file: `ErrInvalidEncoding, ErrNotFound, bucketName, DB, defaultDB, SetDefaultDB, GetDefaultDB, NewDB, Close, NewHash, FromBytes, saveFrames, ...`.

## Control Flow, State, And Persistence
NewDB opens bbolt; FromBytes and Hash.Sum call saveFrames asynchronously via WaitGroup; Get/All parse digest keys, decode frames, and return type plus data/skip frames. Close waits before closing.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/opencontainers/go-digest, github.com/pkg/errors, go.etcd.io/bbolt`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are async writes needing Wait/Close, corrupt frame data, and nil DB returning not found/no-op. db_test.go covers FromBytes, NewHash, frame decoding, invalid encodings, and All.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/cachedigest/db.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/cachedigest/db_test.go -->
# sources/cloud-native/buildkit/util/cachedigest/db_test.go

## Purpose
Unit tests for cachedigest DB/frame/hash behavior. They create temporary bbolt databases and reset the package default DB around each test.

## Important APIs, Types, And Functions
Package: `cachedigest`. Build tags: `none`. Key declarations observed in the file: `tempDB, TestFromBytesAndGet, TestNewHashAndGet, TestEncodeDecodeFrames, TestDecodeFramesInvalid, TestAll`.

## Control Flow, State, And Persistence
Tests cover FromBytes/Get, NewHash with WriteNoDebug skip coalescing, encode/decode round-trip, invalid frame encodings, and All iteration over multiple records.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/opencontainers/go-digest`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk signals include async write waiting, frame endian handling, ErrNotFound, and ErrInvalidEncoding behavior.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/cachedigest/db_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/cachedigest/digest.go -->
# sources/cloud-native/buildkit/util/cachedigest/digest.go

## Purpose
Hash wrapper that records debug frames while computing sha256 digests. It can omit sensitive/noisy data through skip frames and recursively load sub-records referenced by digest strings.

## Important APIs, Types, And Functions
Package: `cachedigest`. Build tags: `none`. Key declarations observed in the file: `Type, String, NewHash, FromBytes, Hash, Reset, BlockSize, Size, Write, WriteNoDebug, Sum, Record, ...`.

## Control Flow, State, And Persistence
Write stores data frames, WriteNoDebug coalesces little-endian skip lengths, Sum persists typed frames, and Record.LoadSubRecords scans string/digest-list/file-list payloads for sha256 references and loads them recursively.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/moby/buildkit/util/bklog, github.com/opencontainers/go-digest`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are recursive graph growth, malformed file-list entries, and warnings rather than hard failures for missing subrecords. db_test.go covers hash recording and skip coalescing.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/cachedigest/digest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/cachedigest/frame.go -->
# sources/cloud-native/buildkit/util/cachedigest/frame.go

## Purpose
Binary frame codec for cachedigest debug records. Frames encode a FrameID and payload length followed by payload bytes.

## Important APIs, Types, And Functions
Package: `cachedigest`. Build tags: `none`. Key declarations observed in the file: `FrameID, String, Frame, encodeFrames, decodeFrames`.

## Control Flow, State, And Persistence
encodeFrames appends big-endian id/length/data records; decodeFrames walks the byte slice and rejects truncated headers or payload overruns with ErrInvalidEncoding.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is format compatibility and memory use proportional to encoded payloads. db_test.go validates round-trip and invalid inputs.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/cachedigest/frame.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/cachestore/store.go -->
# sources/cloud-native/buildkit/util/cachestore/store.go

## Purpose
Cache-key graph exporter. It walks a solver.CacheKeyStorage with link-walking support and builds serializable Records containing parent/child relationships and stable IDs.

## Important APIs, Types, And Functions
Package: `cachestore`. Build tags: `none`. Key declarations observed in the file: `Record, Link, storeWithLinks, Records, setLinkIDs, setIndex, loadRecord`.

## Control Flow, State, And Persistence
Records finds root cache keys with random:/sha256: prefixes, recursively loadRecord walks outbound links, detects cycles with nil sentinels, then setIndex assigns deterministic child order by digest and setLinkIDs materializes integer references.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/moby/buildkit/solver, github.com/opencontainers/go-digest, github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are store implementations without WalkLinksAll, cycles, and graph size. No local tests in this subset.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/cachestore/store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/compression/attrs.go -->
# sources/cloud-native/buildkit/util/compression/attrs.go

## Purpose
Parser for exporter compression attributes. It accepts compression, force-compression, and compression-level strings and returns a Config.

## Important APIs, Types, And Functions
Package: `compression`. Build tags: `none`. Key declarations observed in the file: `ParseAttributes`.

## Control Flow, State, And Persistence
ParseAttributes defaults to Gzip, parses type through Parse, treats empty force-compression as true, and validates bool/integer forms before setting Config fields.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are user input validation and default semantics. No local tests in this subset.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/compression/attrs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/compression/compression.go -->
# sources/cloud-native/buildkit/util/compression/compression.go

## Purpose
Core compression abstraction for layer blobs. It defines Type, Config, compressor/decompressor/finalizer contracts, media-type conversion maps, and compression detection.

## Important APIs, Types, And Functions
Package: `compression`. Build tags: `none`. Key declarations observed in the file: `Compressor, Decompressor, Finalizer, Type, Config, New, SetForce, SetLevel, Default, parse, fromMediaType, IsMediaType, ...`.

## Control Flow, State, And Persistence
DetectLayerMediaType reads blob headers and estargz footer; convertLayerMediaType maps Docker/OCI layer media types; decompress opens content.ReaderAt and delegates to estargz or containerd decompression while closing both readers.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/images, github.com/containerd/containerd/v2/pkg/archive/compression, github.com/containerd/stargz-snapshotter/estargz, github.com/moby/buildkit/util/bklog, github.com/moby/buildkit/util/iohelper, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go/v1, ...`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are unsupported media types, estargz detection cost, and warning/fallback for unmapped media types. Coverage is mostly integration-level.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/compression/compression.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/compression/estargz.go -->
# sources/cloud-native/buildkit/util/compression/estargz.go

## Purpose
eStargz compression.Type implementation. It converts tar streams into seekable gzip layers and records TOC/uncompressed-size annotations.

## Important APIs, Types, And Functions
Package: `compression`. Build tags: `none`. Key declarations observed in the file: `EStargzAnnotations, estargzLabel, Compress, Decompress, NeedsConversion, NeedsComputeDiffBySelf, OnlySupportOCITypes, MediaType, String, Is, decompressEStargz, compressionInfo, ...`.

## Control Flow, State, And Persistence
Compress wires an io.Pipe through estargz writer and blob-info calculation, finalize returns annotations, Is checks labels/footers, Decompress uses estargz reader. It maintains per-compression closure state under a mutex.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/images, github.com/containerd/containerd/v2/pkg/archive/compression, github.com/containerd/containerd/v2/pkg/labels, github.com/containerd/stargz-snapshotter/estargz, github.com/moby/buildkit/util/iohelper, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go/v1, ...`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are goroutine/pipe error propagation, annotation correctness, and content store reads. Integration tests elsewhere are the main signal.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/compression/estargz.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/compression/gzip.go -->
# sources/cloud-native/buildkit/util/compression/gzip.go

## Purpose
gzip implementation of compression.Type for layer blobs. It compresses with containerd gzip writer and uses common decompression logic.

## Important APIs, Types, And Functions
Package: `compression`. Build tags: `none`. Key declarations observed in the file: `Compress, Decompress, NeedsConversion, NeedsComputeDiffBySelf, OnlySupportOCITypes, MediaType, String, gzipWriter`.

## Control Flow, State, And Persistence
NeedsConversion checks Force and media type/compression detection; NeedsComputeDiffBySelf is true when level/force require recompute; MediaType returns OCI gzip layer type.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/images, github.com/opencontainers/image-spec/specs-go/v1`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are level handling and media-type mismatch. Covered indirectly by converter/exporter integration.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/compression/gzip.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/compression/nydus.go -->
# sources/cloud-native/buildkit/util/compression/nydus.go

## Purpose
Nydus compression.Type extension. It registers the nydus type, recognizes Nydus media types, and enforces OCI-only support.

## Important APIs, Types, And Functions
Package: `compression`. Build tags: `nydus`. Key declarations observed in the file: `nydusType, Nydus, init, Parse, FromMediaType, Compress, Decompress, NeedsConversion, NeedsComputeDiffBySelf, OnlySupportOCITypes, MediaType, String, ...`.

## Control Flow, State, And Persistence
Parse/FromMediaType are extended in init-time wrappers. Compress returns unsupported because conversion requires external Nydus tooling; Decompress handles nydus labels/media where supported.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/images, github.com/containerd/containerd/v2/pkg/labels, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go/v1, github.com/pkg/errors, github.com/containerd/nydus-snapshotter/pkg/converter`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are global parse wrapper behavior and unsupported compression attempts. Integration-level coverage only.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/compression/nydus.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/compression/parse.go -->
# sources/cloud-native/buildkit/util/compression/parse.go

## Purpose
Public wrappers for compression type parsing. Parse and FromMediaType delegate to package-level function variables so extensions such as nydus can wrap them.

## Important APIs, Types, And Functions
Package: `compression`. Build tags: `!nydus`. Key declarations observed in the file: `Parse, FromMediaType`.

## Control Flow, State, And Persistence
No state besides the mutable function variables defined elsewhere. Control flow is a single delegation.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is init-order/global wrapper complexity. No local tests.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/compression/parse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/compression/uncompressed.go -->
# sources/cloud-native/buildkit/util/compression/uncompressed.go

## Purpose
Uncompressed compression.Type implementation. It passes data through without compression and maps to OCI uncompressed layer media type.

## Important APIs, Types, And Functions
Package: `compression`. Build tags: `none`. Key declarations observed in the file: `Compress, Decompress, NeedsConversion, NeedsComputeDiffBySelf, OnlySupportOCITypes, MediaType, String`.

## Control Flow, State, And Persistence
Compress returns a nop write closer, Decompress opens raw blob content, and NeedsConversion detects compressed input unless Force is false and type already matches.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/images, github.com/moby/buildkit/util/iohelper, github.com/opencontainers/image-spec/specs-go/v1`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are media-type/diffID expectations and large raw layer streams. Integration-level coverage only.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/compression/uncompressed.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/compression/zstd.go -->
# sources/cloud-native/buildkit/util/compression/zstd.go

## Purpose
Zstandard compression.Type implementation. It writes zstd-compressed OCI layers with optional compression levels.

## Important APIs, Types, And Functions
Package: `compression`. Build tags: `none`. Key declarations observed in the file: `Compress, Decompress, NeedsConversion, NeedsComputeDiffBySelf, OnlySupportOCITypes, MediaType, String, zstdWriter, toZstdEncoderLevel`.

## Control Flow, State, And Persistence
Compress returns a zstd encoder writer, Decompress uses common decompression, NeedsConversion checks force/type, and toZstdEncoderLevel maps integer levels into klauspost/compress levels.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/images, github.com/klauspost/compress/zstd, github.com/opencontainers/image-spec/specs-go/v1`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are level mapping and OCI-only consumer support. Integration-level coverage only.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/compression/zstd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/cond/cond.go -->
# sources/cloud-native/buildkit/util/cond/cond.go

## Purpose
Stateful wrapper around sync.Cond. It remembers one pending signal so a Wait after Signal does not block.

## Important APIs, Types, And Functions
Package: `cond`. Build tags: `none`. Key declarations observed in the file: `NewStatefulCond, StatefulCond, Wait, Signal`.

## Control Flow, State, And Persistence
Wait unlocks the caller-provided main lock, waits under an internal mutex unless signalled is set, consumes the signal, then relocks main. Signal sets signalled and wakes one waiter.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are single-signal semantics and callers needing to hold the main lock correctly. cond_test.go covers initial blocking, pre-signal behavior, and signal between waits.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/cond/cond.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/cond/cond_test.go -->
# sources/cloud-native/buildkit/util/cond/cond_test.go

## Purpose
cond_test.go belongs to package cond and supports the BuildKit utility/source-policy area represented by its directory. Key declarations: TestCondInitialWaitBlocks, TestInitialSignalDoesntBlock, TestSignalBetweenWaits.

## Important APIs, Types, And Functions
Package: `cond`. Build tags: `none`. Key declarations observed in the file: `TestCondInitialWaitBlocks, TestInitialSignalDoesntBlock, TestSignalBetweenWaits`.

## Control Flow, State, And Persistence
Build tags: none. Important dependencies: standard library or generated runtime only. Control flow is local to the declarations above and holds no persistent state unless noted by its package-level maps, globals, or content/database handles.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks and tests should be interpreted at package level: generated files risk schema drift, platform shims risk build-tag coverage, and utility files rely on adjacent tests or integration paths.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/cond/cond_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/buffer.go -->
# sources/cloud-native/buildkit/util/contentutil/buffer.go

## Purpose
In-memory content store implementing provider, ingester, ingest manager, and manager subsets for tests and transient content.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `Buffer, NewBuffer, buffer, Info, Update, Walk, Delete, Writer, Status, ListStatuses, Abort, ReaderAt, ...`.

## Control Flow, State, And Persistence
NewBuffer maintains mutex-protected digest-to-bytes, content.Info, and ref-lock maps. Writers buffer bytes, validate size/digest on Commit, add content info, support Truncate(0), ReaderAt, Info, and label Update. Walk/Delete/status are mostly no-ops.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/errdefs, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go/v1, github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are memory-only storage, incomplete content.Manager methods, and ref lock bookkeeping. buffer_test.go covers write/read, ReaderAt, digest/size errors, and labels.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/buffer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/buffer_test.go -->
# sources/cloud-native/buildkit/util/contentutil/buffer_test.go

## Purpose
Unit tests for contentutil buffer.go behavior. The tests use in-memory/local stores, stub providers, descriptors, and digest fixtures to verify content utility contracts.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `TestReadWrite, TestReaderAt, TestLabels`.

## Control Flow, State, And Persistence
Control flow constructs test content, exercises public APIs, and asserts digest, size, labels, cache hits, referrer handling, source detection, or fetch behavior depending on the file.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/remotes/docker, github.com/containerd/errdefs, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go/v1, github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk signals include canceled reads, resumed ingests, label updates, slow fetches, and provider routing. These tests are the strongest regression signal for contentutil in this subset.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/buffer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/cache.go -->
# sources/cloud-native/buildkit/util/contentutil/cache.go

## Purpose
Caching wrapper for a ReferrersProvider. It fetches blobs/referrers once into a local content buffer/store and adds GC labels to keep cached dependencies reachable.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `ReferrersProviderWithBuffer, _, ReferrersProviderBuffer, ReaderAt, FetchReferrers, SetGCLabels, filterRefs, addName, readArtifactType`.

## Control Flow, State, And Persistence
ReaderAt opens a writer by digest ref, resets resumed offsets, copies source ReaderAt into cache, commits, records blob descriptors, and avoids poisoning later attempts on abort. FetchReferrers caches filtered referrers and names; SetGCLabels writes content and referrer GC references.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/remotes, github.com/containerd/errdefs, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go/v1`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are partial ingest cleanup, label collisions, artifact-type filtering, and concurrent cache maps. cache_test.go covers blob caching, referrer caching, canceled reads, resumed offsets, and GC labels.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/cache_test.go -->
# sources/cloud-native/buildkit/util/contentutil/cache_test.go

## Purpose
Unit tests for contentutil cache.go behavior. The tests use in-memory/local stores, stub providers, descriptors, and digest fixtures to verify content utility contracts.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `stubProvider, newStubProvider, ReaderAt, FetchReferrers, add, addReferrer, buf, Close, newBuf, stubManifest, TestReferrersProviderBuffer, TestReferrersProviderRefsBuffer, ...`.

## Control Flow, State, And Persistence
Control flow constructs test content, exercises public APIs, and asserts digest, size, labels, cache hits, referrer handling, source detection, or fetch behavior depending on the file.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/remotes, github.com/containerd/containerd/v2/plugins/content/local, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go, github.com/opencontainers/image-spec/specs-go/v1, github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk signals include canceled reads, resumed ingests, label updates, slow fetches, and provider routing. These tests are the strongest regression signal for contentutil in this subset.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/copy.go -->
# sources/cloud-native/buildkit/util/contentutil/copy.go

## Purpose
Recursive OCI content copier. It copies a descriptor and its children/referrers from a provider to an ingester using containerd image handlers.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `CopyInfo, CopyOption, WithReferrers, Copy, localFetcher, Fetch, rc, Read, Seek, CopyChain, copyChain, annotateDistributionSourceHandler`.

## Control Flow, State, And Persistence
Copy wraps a local provider as a fetcher; CopyChain uses a visited SyncMap to avoid duplicate descriptors, dispatches handlers for children and optional referrers, and annotates distribution-source labels from the source provider.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/images, github.com/containerd/errdefs, github.com/moby/buildkit/util/bkmaps, github.com/moby/buildkit/util/resolver/limited, github.com/moby/buildkit/util/resolver/retryhandler, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go/v1, ...`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are graph traversal cycles, handler compatibility, and missing referrers support. copy_test.go validates basic copy behavior.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/copy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/copy_test.go -->
# sources/cloud-native/buildkit/util/contentutil/copy_test.go

## Purpose
Unit tests for contentutil copy.go behavior. The tests use in-memory/local stores, stub providers, descriptors, and digest fixtures to verify content utility contracts.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `TestCopy`.

## Control Flow, State, And Persistence
Control flow constructs test content, exercises public APIs, and asserts digest, size, labels, cache hits, referrer handling, source detection, or fetch behavior depending on the file.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go/v1`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk signals include canceled reads, resumed ingests, label updates, slow fetches, and provider routing. These tests are the strongest regression signal for contentutil in this subset.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/copy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/fetcher.go -->
# sources/cloud-native/buildkit/util/contentutil/fetcher.go

## Purpose
Adapter from remotes.Fetcher to content.Provider plus referrers support. It converts streaming fetches into ReaderAt-capable objects.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `ReferrersProvider, FromFetcher, fetchedProvider, ReaderAt, FetchReferrers, readerAt, ReadAt, Size`.

## Control Flow, State, And Persistence
ReaderAt fetches a stream, reads it fully into memory, and returns a readerAt wrapper with Size and Close. FetchReferrers delegates to fetchers implementing remotes.ReferrersFetcher.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/remotes, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go/v1, github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are memory use for large blobs and slow fetch behavior. fetcher_test.go covers normal and slow fetch cases.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/fetcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/fetcher_test.go -->
# sources/cloud-native/buildkit/util/contentutil/fetcher_test.go

## Purpose
Unit tests for contentutil fetcher.go behavior. The tests use in-memory/local stores, stub providers, descriptors, and digest fixtures to verify content utility contracts.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `TestFetcher, TestSlowFetch, dummySlowFetcher, Fetch, newSlowBuffer, slowBuffer, Seek, Read, Close`.

## Control Flow, State, And Persistence
Control flow constructs test content, exercises public APIs, and asserts digest, size, labels, cache hits, referrer handling, source detection, or fetch behavior depending on the file.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go/v1`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk signals include canceled reads, resumed ingests, label updates, slow fetches, and provider routing. These tests are the strongest regression signal for contentutil in this subset.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/fetcher_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/multiprovider.go -->
# sources/cloud-native/buildkit/util/contentutil/multiprovider.go

## Purpose
Content provider multiplexer with lazy provider registration. It routes descriptors to per-digest providers while falling back to a base provider.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `NewMultiProvider, MultiProvider, SnapshotLabels, ReaderAt, Info, Add, UnlazySession`.

## Control Flow, State, And Persistence
Add stores provider overrides, ReaderAt/Info select provider by digest, SnapshotLabels records indexed labels for descriptors, and UnlazySession exposes session groups from lazy providers.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/errdefs, github.com/moby/buildkit/session, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go/v1, github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are stale provider maps and label/index assumptions. multiprovider_test.go covers routing and label snapshots.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/multiprovider.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/multiprovider_test.go -->
# sources/cloud-native/buildkit/util/contentutil/multiprovider_test.go

## Purpose
Unit tests for contentutil multiprovider.go behavior. The tests use in-memory/local stores, stub providers, descriptors, and digest fixtures to verify content utility contracts.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `TestMultiProvider`.

## Control Flow, State, And Persistence
Control flow constructs test content, exercises public APIs, and asserts digest, size, labels, cache hits, referrer handling, source detection, or fetch behavior depending on the file.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/errdefs, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go/v1, github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk signals include canceled reads, resumed ingests, label updates, slow fetches, and provider routing. These tests are the strongest regression signal for contentutil in this subset.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/multiprovider_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/pusher.go -->
# sources/cloud-native/buildkit/util/contentutil/pusher.go

## Purpose
Adapter from remotes.Pusher to content.Ingester. It exposes content.Writer handles backed by remote push streams.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `FromPusher, pushingIngester, Writer, writer, Status, Commit, Close`.

## Control Flow, State, And Persistence
Writer resolves descriptor/ref options, asks the pusher for a writer, tracks offset/status, validates expected digest on Commit, and closes remote resources.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/remotes, github.com/containerd/errdefs, github.com/opencontainers/go-digest, github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are streaming push failures and limited local status semantics. No direct local test in this subset.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/pusher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/refs.go -->
# sources/cloud-native/buildkit/util/contentutil/refs.go

## Purpose
Registry reference helpers for content providers and ingesters. It resolves pull refs into descriptors/providers and push refs into ingesters.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `ResolveOpt, ResolveOptFunc, WithCredentials, ProviderFromRef, IngesterFromRef, pusher, ingester, Writer, lockedWriter, Commit, Close`.

## Control Flow, State, And Persistence
ProviderFromRef parses references, optionally uses credentials, creates resolver/fetcher, and resolves a descriptor. IngesterFromRef creates a pusher-backed ingester with serialized writer locking.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/remotes, github.com/containerd/containerd/v2/core/remotes/docker, github.com/containerd/errdefs, github.com/moby/buildkit/version, github.com/opencontainers/go-digest, github.com/opencontainers/image-spec/specs-go/v1, github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are network/auth behavior, reference parsing, and writer lock contention. Tests are not local.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/refs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/source.go -->
# sources/cloud-native/buildkit/util/contentutil/source.go

## Purpose
Checks whether content.Info labels indicate a descriptor came from a registry source reference.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `HasSource`.

## Control Flow, State, And Persistence
HasSource normalizes a reference spec and compares it against containerd distribution source labels for matching host/repository information.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/pkg/reference`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are label format drift and reference normalization. source_test.go validates positive/negative source detection.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/source.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/source_test.go -->
# sources/cloud-native/buildkit/util/contentutil/source_test.go

## Purpose
Unit tests for contentutil source.go behavior. The tests use in-memory/local stores, stub providers, descriptors, and digest fixtures to verify content utility contracts.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `TestHasSource`.

## Control Flow, State, And Persistence
Control flow constructs test content, exercises public APIs, and asserts digest, size, labels, cache hits, referrer handling, source detection, or fetch behavior depending on the file.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/pkg/reference`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk signals include canceled reads, resumed ingests, label updates, slow fetches, and provider routing. These tests are the strongest regression signal for contentutil in this subset.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/source_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/storewithprovider.go -->
# sources/cloud-native/buildkit/util/contentutil/storewithprovider.go

## Purpose
Decorator that lets a content.Store fall back to another provider for reads.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `NewStoreWithProvider, storeWithProvider, ReaderAt`.

## Control Flow, State, And Persistence
ReaderAt first tries the store and falls back to the provider only when content is missing; all other store behavior is inherited by embedding.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/opencontainers/image-spec/specs-go/v1`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is masking missing local content with external provider access. No local test.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/storewithprovider.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/types.go -->
# sources/cloud-native/buildkit/util/contentutil/types.go

## Purpose
types.go belongs to package contentutil and supports the BuildKit utility/source-policy area represented by its directory. Key declarations: RegisterContentPayloadTypes.

## Important APIs, Types, And Functions
Package: `contentutil`. Build tags: `none`. Key declarations observed in the file: `RegisterContentPayloadTypes`.

## Control Flow, State, And Persistence
Build tags: none. Important dependencies: github.com/containerd/containerd/v2/core/remotes. Control flow is local to the declarations above and holds no persistent state unless noted by its package-level maps, globals, or content/database handles.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/remotes`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks and tests should be interpreted at package level: generated files risk schema drift, platform shims risk build-tag coverage, and utility files rely on adjacent tests or integration paths.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/contentutil/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/converter/converter.go -->
# sources/cloud-native/buildkit/util/converter/converter.go

## Purpose
Layer conversion pipeline for recompressing blobs and optionally rewriting tar timestamps. It returns containerd converter functions only when conversion is needed.

## Important APIs, Types, And Functions
Package: `converter`. Build tags: `none`. Key declarations observed in the file: `New, NewWithRewriteTimestamp, conversion, bufioPool, rewriteTimestampInTarHeader, convert, onceWriteCloser, Close, labelRewrittenTimestamp`.

## Control Flow, State, And Persistence
NewWithRewriteTimestamp checks compression NeedsConversion and timestamp annotation, selects decompressor from current media type, streams decompressed data through optional tarconverter, computes diffID, compresses to a new content writer, commits labels, and applies compression finalizer annotations.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/content, github.com/containerd/containerd/v2/core/images/converter, github.com/containerd/containerd/v2/pkg/labels, github.com/containerd/errdefs, github.com/moby/buildkit/identity, github.com/moby/buildkit/util/bklog, github.com/moby/buildkit/util/compression, github.com/moby/buildkit/util/converter/tarconverter, ...`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are large streaming failures, immutable diffID bypass, media-type mismatches, and timestamp reproducibility. tarconverter tests cover tar padding for the timestamp rewrite reader.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/converter/converter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/converter/tarconverter/tarconverter.go -->
# sources/cloud-native/buildkit/util/converter/tarconverter/tarconverter.go

## Purpose
Streaming tar header transformer. It rebuilds a tar stream while applying an optional HeaderConverter to each header.

## Important APIs, Types, And Functions
Package: `tarconverter`. Build tags: `none`. Key declarations observed in the file: `HeaderConverter, NewReader`.

## Control Flow, State, And Persistence
A goroutine reads src tar entries, mutates headers, writes headers and file bodies to an io.Pipe tar.Writer, then drains the source after EOF to preserve reader behavior.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are malformed tar streams, decompression-bomb concerns acknowledged by nolint, and goroutine error propagation through pipe close. tarconverter_test.go checks output padding length.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/converter/tarconverter/tarconverter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/converter/tarconverter/tarconverter_test.go -->
# sources/cloud-native/buildkit/util/converter/tarconverter/tarconverter_test.go

## Purpose
Unit test for tarconverter stream padding behavior. It creates a tiny tar archive and verifies conversion preserves the original padded archive length.

## Important APIs, Types, And Functions
Package: `tarconverter`. Build tags: `none`. Key declarations observed in the file: `createTar, TestPaddingForReader`.

## Control Flow, State, And Persistence
createTar builds a tar with a regular file; TestPaddingForReader rewrites ModTime through NewReader, reads all output, closes the reader, and compares lengths.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk signal is regression coverage for tar padding after header rewriting, especially around BuildKit PR discussions on draining/padding behavior.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/converter/tarconverter/tarconverter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/cpuset/cpuset.go -->
# sources/cloud-native/buildkit/util/cpuset/cpuset.go

## Purpose
Parser, validator, and formatter for Linux cpuset-style strings such as 0-3,5.

## Important APIs, Types, And Functions
Package: `cpuset`. Build tags: `none`. Key declarations observed in the file: `MaxCPU, Parse, Validate, Format`.

## Control Flow, State, And Persistence
Parse splits comma parts, trims whitespace, expands inclusive ranges, rejects negative/reversed/non-numeric entries, and caps indices at MaxCPU to avoid huge allocations. Format sorts and collapses contiguous ranges.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are hard MaxCPU assumptions and accepting empty string as unset. cpuset_test.go covers parse, format, validation, whitespace, bounds, and round-trip.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/cpuset/cpuset.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/cpuset/cpuset_test.go -->
# sources/cloud-native/buildkit/util/cpuset/cpuset_test.go

## Purpose
Unit tests for cpuset parsing, formatting, and validation. They exercise valid empty/single/range/list forms and invalid negative, non-numeric, reversed, and oversized forms.

## Important APIs, Types, And Functions
Package: `cpuset`. Build tags: `none`. Key declarations observed in the file: `TestParse, TestFormat, TestValidate`.

## Control Flow, State, And Persistence
Tests call Parse, Format, and Validate with table-style subtests and assert exact sets or formatted strings.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk signal is protection against unbounded allocation through the MaxCPU checks and preservation of round-trip formatting.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/cpuset/cpuset_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/db/boltutil/db.go -->
# sources/cloud-native/buildkit/util/db/boltutil/db.go

## Purpose
Thin bbolt opener implementing BuildKit util/db.DB. It wraps bolt.Open and returns the database through the local interface type.

## Important APIs, Types, And Functions
Package: `boltutil`. Build tags: `none`. Key declarations observed in the file: `Open`.

## Control Flow, State, And Persistence
No additional state or control flow beyond propagating open errors.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/moby/buildkit/util/db, go.etcd.io/bbolt`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is direct bbolt open failure. SafeOpen adds recovery behavior in the sibling file.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/db/boltutil/db.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/db/boltutil/safe_open.go -->
# sources/cloud-native/buildkit/util/db/boltutil/safe_open.go

## Purpose
Resilient bbolt opener for disposable BuildKit databases. It recovers from open panics/errors by backing up a non-empty database and creating a new one.

## Important APIs, Types, And Functions
Package: `boltutil`. Build tags: `none`. Key declarations observed in the file: `SafeOpen, fallbackOpen, fileHasContent`.

## Control Flow, State, And Persistence
SafeOpen defers panic-to-error conversion, checks fileHasContent on failure, calls fallbackOpen to rename the corrupt file with identity.NewID and reopen.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/moby/buildkit/identity, github.com/moby/buildkit/util/bklog, github.com/moby/buildkit/util/db, github.com/pkg/errors, go.etcd.io/bbolt`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is intentional data loss after corruption and backup rename failure. No local test in this subset.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/db/boltutil/safe_open.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/db/db.go -->
# sources/cloud-native/buildkit/util/db/db.go

## Purpose
Database interface contract used by BuildKit utilities. DB combines io.Closer with the Transactor interface.

## Important APIs, Types, And Functions
Package: `db`. Build tags: `none`. Key declarations observed in the file: `DB`.

## Control Flow, State, And Persistence
No control flow. It abstracts bbolt so callers depend on View/Update/Close rather than concrete bolt.DB.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is interface drift with transaction users. No tests.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/db/db.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/db/transactor.go -->
# sources/cloud-native/buildkit/util/db/transactor.go

## Purpose
Transaction interface for bbolt-backed utility databases. It defines View and Update methods accepting *bolt.Tx callbacks.

## Important APIs, Types, And Functions
Package: `db`. Build tags: `none`. Key declarations observed in the file: `Transactor`.

## Control Flow, State, And Persistence
No state or implementation; concrete bolt.DB satisfies it.

## Dependencies And Integration Points
Important dependencies/imports: `go.etcd.io/bbolt`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is bbolt-specific type leakage through the interface. No tests.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/db/transactor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/disk/disk.go -->
# sources/cloud-native/buildkit/util/disk/disk.go

## Purpose
Shared disk statistics type. DiskStat holds Total, Free, and Available byte counts returned by platform-specific GetDiskStat implementations.

## Important APIs, Types, And Functions
Package: `disk`. Build tags: `none`. Key declarations observed in the file: `DiskStat`.

## Control Flow, State, And Persistence
No control flow. Platform files fill this struct from statfs/statvfs/GetDiskFreeSpaceEx equivalents.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk is semantic differences between free and available across platforms. disk_test.go checks positive values on the running platform.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/disk/disk.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/disk/disk_freebsd.go -->
# sources/cloud-native/buildkit/util/disk/disk_freebsd.go

## Purpose
freebsd disk statistics implementation. It calls the platform statfs/statvfs syscall and converts block counts into byte totals.

## Important APIs, Types, And Functions
Package: `disk`. Build tags: `freebsd`. Key declarations observed in the file: `GetDiskStat`.

## Control Flow, State, And Persistence
Control flow wraps syscall errors with the root path and fills DiskStat Total, Free, and Available using platform-specific block-size fields.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are OS-specific field semantics and integer overflow on unusual filesystems. disk_test.go is the smoke test on supported platforms.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/disk/disk_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/disk/disk_netbsd.go -->
# sources/cloud-native/buildkit/util/disk/disk_netbsd.go

## Purpose
netbsd disk statistics implementation. It calls the platform statfs/statvfs syscall and converts block counts into byte totals.

## Important APIs, Types, And Functions
Package: `disk`. Build tags: `netbsd`. Key declarations observed in the file: `GetDiskStat`.

## Control Flow, State, And Persistence
Control flow wraps syscall errors with the root path and fills DiskStat Total, Free, and Available using platform-specific block-size fields.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/pkg/errors, golang.org/x/sys/unix`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are OS-specific field semantics and integer overflow on unusual filesystems. disk_test.go is the smoke test on supported platforms.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/disk/disk_netbsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/disk/disk_openbsd.go -->
# sources/cloud-native/buildkit/util/disk/disk_openbsd.go

## Purpose
openbsd disk statistics implementation. It calls the platform statfs/statvfs syscall and converts block counts into byte totals.

## Important APIs, Types, And Functions
Package: `disk`. Build tags: `openbsd`. Key declarations observed in the file: `GetDiskStat`.

## Control Flow, State, And Persistence
Control flow wraps syscall errors with the root path and fills DiskStat Total, Free, and Available using platform-specific block-size fields.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are OS-specific field semantics and integer overflow on unusual filesystems. disk_test.go is the smoke test on supported platforms.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/disk/disk_openbsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/disk/disk_test.go -->
# sources/cloud-native/buildkit/util/disk/disk_test.go

## Purpose
Smoke test for platform disk statistics. It calls GetDiskStat("/") and asserts total is positive and free/available are non-negative.

## Important APIs, Types, And Functions
Package: `disk`. Build tags: `none`. Key declarations observed in the file: `TestGetDiskStat`.

## Control Flow, State, And Persistence
Control flow is a single platform-dependent call. It does not validate exact filesystem accounting.

## Dependencies And Integration Points
Important dependencies/imports: `standard library or generated runtime only`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risk signal is basic syscall/API availability on the test platform.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/disk/disk_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/disk/disk_unix.go -->
# sources/cloud-native/buildkit/util/disk/disk_unix.go

## Purpose
unix disk statistics implementation. It calls the platform statfs/statvfs syscall and converts block counts into byte totals.

## Important APIs, Types, And Functions
Package: `disk`. Build tags: `!windows && !freebsd && !netbsd && !openbsd`. Key declarations observed in the file: `GetDiskStat`.

## Control Flow, State, And Persistence
Control flow wraps syscall errors with the root path and fills DiskStat Total, Free, and Available using platform-specific block-size fields.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/pkg/errors`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are OS-specific field semantics and integer overflow on unusual filesystems. disk_test.go is the smoke test on supported platforms.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/disk/disk_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/disk/disk_windows.go -->
# sources/cloud-native/buildkit/util/disk/disk_windows.go

## Purpose
Windows disk statistics implementation. It calls GetDiskFreeSpaceEx via x/sys/windows and returns total/free/available bytes.

## Important APIs, Types, And Functions
Package: `disk`. Build tags: `windows`. Key declarations observed in the file: `GetDiskStat`.

## Control Flow, State, And Persistence
Control flow converts the root path to UTF-16, invokes the Windows API, and maps available/free/total outputs to DiskStat.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/pkg/errors, golang.org/x/sys/windows`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are path formatting and Windows API semantics. disk_test.go is the smoke test.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/disk/disk_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/entitlements/entitlements.go -->
# sources/cloud-native/buildkit/util/entitlements/entitlements.go

## Purpose
Entitlement parsing and allow-list enforcement for privileged BuildKit features. It covers security.insecure, network.host, and device with optional device config/aliases.

## Important APIs, Types, And Functions
Package: `entitlements`. Build tags: `none`. Key declarations observed in the file: `Entitlement, String, all, EntitlementsConfig, DevicesConfig, _, ParseDevicesConfig, Merge, Parse, WhiteList, Set, Allowed, ...`.

## Control Flow, State, And Persistence
Parse handles device=<csv fields>, WhiteList validates allowed values against optional daemon-supported list and merges device configs, Set.Check validates requested Values for network/security.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/pkg/errors, github.com/tonistiigi/go-csvvalue`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are config parsing errors, unsupported daemon entitlements, and device entitlement not checked by Values.Check here. No local tests.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/entitlements/entitlements.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/entitlements/security/security_linux.go -->
# sources/cloud-native/buildkit/util/entitlements/security/security_linux.go

## Purpose
Linux insecure container spec mutator. It grants current capabilities, removes readonly/masked path restrictions, clears AppArmor, permits device cgroups, and mounts common host devices outside user namespaces.

## Important APIs, Types, And Functions
Package: `security`. Build tags: `none`. Key declarations observed in the file: `WithInsecureSpec, getFreeLoopID, getCurrentCaps, getAllCaps, linux35Caps`.

## Control Flow, State, And Persistence
WithInsecureSpec calls getAllCaps, appends capabilities to all capability sets, clears restrictions, allows char/block devices, probes /dev/loop-control for free loop id, and adds loop devices around that range. Cap discovery is cached with sync.Once.

## Dependencies And Integration Points
Important dependencies/imports: `github.com/containerd/containerd/v2/core/containers, github.com/containerd/containerd/v2/pkg/cap, github.com/containerd/containerd/v2/pkg/oci, github.com/moby/buildkit/util/bklog, github.com/opencontainers/runtime-spec/specs-go, github.com/pkg/errors, golang.org/x/sys/unix`. The file integrates through its package path and adjacent BuildKit components; generated protobuf files integrate with their `.proto` schema and the Go/gRPC/protobuf runtimes.

## Risks And Test Signals
Risks are intentionally privileged behavior, user namespace differences, loop-control failures, and kernel capability variance. Test signal is integration/security review rather than local unit tests.

<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/entitlements/security/security_linux.go -->
