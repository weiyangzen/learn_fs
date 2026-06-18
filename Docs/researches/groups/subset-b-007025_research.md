# subset-b-007025 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Server.cc -->
## sources/distributed-fs/eos/mgm/FuseServer/Server.cc

Purpose: implements the EOS MGM FUSEX metadata server. It translates `eos::fusex::md` protobuf operations into namespace reads and mutations, capability issuance/validation, file locks, flush tracking, quota checks, client broadcasts, audit events, and workflow triggers. It is the central server-side authority for FUSE clients after they have connected through the MGM ZMQ task path.

Important APIs and functions: `Server::start` launches heartbeat and capability monitor threads; `MonitorCaps` expires capabilities and periodically refreshes quota state for active caps; `FillContainerMD` and `FillFileMD` serialize directory/file metadata from namespace services into protobufs; `FillContainerCAP`, `ValidateCAP`, `ValidatePERM`, `InodeFromCAP`, and `Header` implement the capability and fallback permission model. Operation handlers are split by request type: `OpGetLs`, `OpSet`, `OpSetDirectory`, `OpSetFile`, `OpSetLink`, `OpDelete*`, `OpGetCap`, `OpGetLock`, `OpSetLock`, and `HandleMD`. Static helpers `ApplyDirOwnerAuth` and `CheckOwnerAcl` enforce `sys.owner.auth` and chown-like ownership changes.

Control flow: `HandleMD` logs and classifies the protobuf request, prefetches relevant namespace entries, then dispatches to the operation handler. GET/LS builds a container response and may stream directory listings in batches. SET first applies owner-auth impersonation, validates a write capability or recomputes permissions, then calls the directory/file/link variant. DELETE validates delete permission and calls the typed delete path. Lock operations bridge protobuf lock records to the internal lock tracker and also respect xattr locks.

State and persistence: persistent metadata changes go through `gOFS->eosDirectoryService`, `gOFS->eosFileService`, `gOFS->eosView`, quota nodes, and container accounting. New objects inherit selected parent attributes and store `sys.eos.btime`, `sys.vtrace`, and `sys.fusex.state` markers. Hard links are represented through `sys.mdino` and `sys.nlink`; deletions and overwrites update these attributes manually. Capabilities are stored in `mCaps`, broadcast to clients, and removed on deletion. The monitor thread keeps in-memory out-of-quota state to avoid repeated cap broadcasts.

Dependencies and integration points: this file depends on the global MGM `gOFS` object, namespace interfaces, quota, recycle/versioning, policy/layout selection, geotree placement, workflows, replication tracking, audit helpers, protobuf JSON/debugging, FUSE lock tracking, xattr lock parsing, and ZMQ task replies. It integrates with `Acl` for cap mode calculation and fallback permissions, `AccessChecker`-style POSIX semantics indirectly, and client-side FUSE expectations about capabilities, clocks, and broadcast invalidations.

Risks: correctness relies on consistent namespace locking around many service calls; several recycle/version branches intentionally release the namespace lock and comments identify hard-to-trigger races. Capability fallback after MGM restart is useful but expands the importance of `ValidatePERM` parity with cap issuance. Hard-link bookkeeping is security-sensitive; the code now validates target parsing, same-parent constraints, and rejects hard-link chains, but overwrite/delete paths still have complex `sys.nlink` mutation cases. Auditing is inconsistent in detail across operation types and has nested loops for file xattr removal under the `md.attr()` loop, which may duplicate removals. There is a likely typo in forced lease lookup: it checks `sys.force.leasetime` but reads `sys.forced.leasetime`.

Test signals: high-value tests should cover GET/LS batching and child caps, cap expiry and fallback permission checks, `sys.owner.auth` keyed and sticky behavior, ACL denial precedence in caps, cross-parent hard-link rejection, hard-link deletion/overwrite reference counts, recycle/version rename races, quota denial for create, sticky-bit delete denial, xattr lock conflict behavior, audit emission for create/update/delete/xattr/ACL changes, and workflow failures on create/delete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Server.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Server.hh -->
## sources/distributed-fs/eos/mgm/FuseServer/Server.hh

Purpose: declares the FUSEX metadata `Server` class in `eos::mgm::FuseServer`. The class owns the managers used by FUSE clients (`Clients`, `Caps`, `Lock`, `Flush`) and exposes the operation surface implemented in `Server.cc`.

Important APIs and types: public accessors `Client`, `Cap`, `Locks`, and `Flushs` expose internal managers. Metadata helpers `FillContainerMD`, `FillFileMD`, and `FillContainerCAP` serialize namespace state and issue capabilities. Authorization helpers `ValidateCAP`, `ValidatePERM`, and `InodeFromCAP` guard mutating operations. The operation API mirrors FUSEX protobuf operations: flush begin/end, get/list, set directory/file/link, get cap, delete directory/file/link, get/set lock, and top-level `HandleMD`. Lifecycle methods are `start`, `shutdown`, `MonitorCaps`, `terminate`, and `should_terminate`.

Control flow: callers are expected to use `HandleMD` for dispatch, while individual `Op*` methods are exposed for internal routing and tests. The class keeps a termination atomic used by background monitor threads. `Header` formats framed synchronous responses.

State and persistence: the header itself stores no persistent namespace state, but it declares in-memory `mClients`, `mCaps`, `mLocks`, `mFlushs`, the termination flag, and `c_max_children`, which bounds directory listing size. Persistent effects are performed by the implementation through MGM namespace services.

Dependencies and integration points: includes namespace macros from `Namespace.hh`, generated `fusex.pb.h`, lock tracker headers, FUSE server subcomponents, and `IFileMD`. The class inherits `eos::common::LogId`, making it part of EOS logging/audit context. Consumers include the MGM ZMQ/FUSE server path.

Risks: the accessors expose mutable internal managers directly, so thread safety depends on each manager and caller discipline. `Flushs` is misspelled but part of the public interface. Many methods accept mutable `VirtualIdentity&`, and implementation can rewrite it for owner-auth; tests need to check caller-visible mutation expectations.

Test signals: compile/API tests should ensure operation declarations match protobuf dispatch in `Server.cc`; unit seams can target `Header`, cap validation, permission fallback, and lifecycle termination behavior with fake manager state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Server.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/Namespace.hh -->
## sources/distributed-fs/eos/mgm/Namespace.hh

Purpose: provides namespace convenience macros for MGM code. It centralizes `namespace eos::mgm` and subnamespace wrappers for FUSE server, TGC, bulk, and REST code, plus matching `using namespace` helper macros.

Important APIs and types: `EOSMGMNAMESPACE_BEGIN/END`, `EOSFUSESERVERNAMESPACE_BEGIN/END`, `EOSTGCNAMESPACE_BEGIN/END`, `EOSBULKNAMESPACE_BEGIN/END`, and `EOSMGMRESTNAMESPACE_BEGIN/END` expand to nested namespace declarations. `USE_EOSMGMNAMESPACE`, `USE_EOSFUSESERVERNAMESPACE`, and `USE_EOSBULKNAMESPACE` expand to `using namespace` statements.

Control flow: no runtime control flow; it is purely preprocessor structure.

State and persistence: no state and no persistence.

Dependencies and integration points: included by MGM headers and implementation files that want consistent namespace spelling. In this work item it scopes `Access`, `Acl`, `AdminSocket`, `AccessChecker`, and `FuseServer::Server`.

Risks: macro-based namespace management hides actual C++ syntax from tools and can make refactors/error messages less direct. `using namespace` macros can broaden lookup and collision risk if used in headers or wide scopes.

Test signals: build coverage is the main signal. Static analysis or style checks can flag accidental macro misuse and unwanted `USE_*` expansion in headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/Namespace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/access/Access.cc -->
## sources/distributed-fs/eos/mgm/access/Access.cc

Purpose: implements global MGM admission-control configuration: banned and allowed users/groups/hosts/domains/tokens, stall rules, redirection rules, stall host filters, find limits, and thread limits. These rules are read by higher-level MGM request handling such as stall and redirect decisions.

Important APIs and functions: static storage is defined for all sets/maps declared in `Access.hh`, protected by `gAccessMutex`. `Reset` clears in-memory rules; `EnforceConfig` loads serialized global config from `FsView::gFsView`; `StoreAccessConfig` serializes current rules back; `GetFindLimits` derives rate limits from `rate:*` stall rules; `SetStallRule`, `RemoveStallRule`, `SetSlaveToMasterRules`, and `SetMasterToSlaveRules` mutate stall/redirection state; `ThreadLimit` resolves per-user and global thread caps; `CanStall` applies regex-based host allow/deny lists.

Control flow: config loading tokenizes colon-separated lists for identities/hosts and comma/tilde-separated entries for stall/redirection rules. Applying redirect/stall can be disabled while still keeping rate/thread rules. Store reverses the process and escapes commas/tildes in stall comments with sentinel strings.

State and persistence: in-memory static sets/maps are authoritative during runtime; persistence is the MGM global configuration store through `FsView::gFsView.GetGlobalConfig` and `SetGlobalConfig`. Atomic booleans cache the presence of global/read/write/user-group stall rules for fast checks.

Dependencies and integration points: depends on `FsView`, `StringConversion`, POSIX regex, and `Mapping` for UID/GID string conversion. Failover hooks adjust access rules when transitioning between master and slave roles.

Risks: serialization is hand-rolled and delimiter-based; malformed values are mostly ignored or parsed as zero by `atoi`. `StoreAccessConfig` appears to append banned domains into `hostval` rather than `domainval`, which could drop or misstore domain bans. `SetStallRule` sets `gStallGlobal` from the supplied `mIsGlobal` without recomputing read/write/user-group flags. `CanStall` assumes the caller already holds the read lock, so misuse can race with config updates.

Test signals: tests should round-trip every global config key, especially domains/tokens/comments with escaped delimiters; verify master/slave transition side effects; check per-user/group/wildcard find limits; exercise `CanStall` whitelist and blacklist regex behavior; and confirm thread limits under explicit and default rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/access/Access.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/access/Access.hh -->
## sources/distributed-fs/eos/mgm/access/Access.hh

Purpose: declares the static `eos::mgm::Access` rule engine used for global bans, allows, stalling, redirection, rate limits, and thread limits. It is a process-wide configuration facade rather than an instantiable request object.

Important APIs and types: string constants define global config keys such as `BanUsers`, `AllowedHosts`, `Stall`, `Redirection`, `StallHosts`, and `NoStallHosts`. Static sets/maps hold banned/allowed identities, stall/redirection rules, comments, and per-user/group redirection placeholders. `StallInfo` carries a stall type, delay, comment, and global flag. Public static methods load/store/reset config and query limits.

Control flow: callers update the static containers, then call `StoreAccessConfig`, or refresh from persistent config with `EnforceConfig`. Request paths query booleans/maps and may call `CanStall` or limit helpers under `gAccessMutex`.

State and persistence: all rule state is static and guarded by `eos::common::RWMutex gAccessMutex`; the implementation persists it via `FsView::gFsView`.

Dependencies and integration points: includes namespace macros, EOS `RWMutex`, `Mapping`, STL sets/maps/vectors/strings, and atomics. Documentation notes use by `XrdMgmOfs::ShouldStall` and `ShouldRedirect`.

Risks: public static containers make it easy to bypass helper invariants and forget lock discipline. Atomic summary flags can drift from maps if callers mutate maps directly. Several comments have copy/paste inaccuracies, which can mislead maintainers about host/domain/token semantics.

Test signals: header-level compile tests should include this from multiple MGM units; behavioral tests should mutate through helpers rather than raw containers and verify lock-protected readers observe consistent state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/access/Access.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/acl/Acl.cc -->
## sources/distributed-fs/eos/mgm/acl/Acl.cc

Purpose: implements ACL parsing and permission-flag calculation for EOS MGM metadata. It converts `sys.acl`, `user.acl`, and token ACL strings into booleans consumed by FUSE capability issuance, namespace access checks, xattr authorization, quota/workflow permissions, and token issuance.

Important APIs and functions: constructors build ACLs from explicit strings, xattr maps, or a path lookup. `SetFromAttrMap` selects directory/file user ACLs based on `sys.eval.useracl`, merges file `sys.acl` into directory `sys.acl`, and obtains token ACLs. `Set` parses rules and computes flags like read/write/write-once/update/browse/delete/chmod/chown/quota/archive/prepare/token/sys-acl/xattr. `IsValid` validates ACL syntax with POSIX regexes. `ConvertIds` converts `u:`/`g:` rules between names and numeric IDs. `TokenAcl` derives a rule from `VirtualIdentity::token`. `AllowXAttrUpdate` checks whether a sys xattr can be modified.

Control flow: parsing splits ACLs by comma, resolves primary or secondary groups, builds match tags for UID/GID/name/egroup/key/everyone, and scans each permission character. Denials and reallows are tracked in arrays and reconciled after all matching rules so `+d` and `+u` can re-enable specific system ACL denials. Token ACLs replace normal ACLs entirely.

State and persistence: `Acl` instances are transient and store only computed booleans plus remembered ACL strings and user-ACL evaluation flags. Persistent ACL data lives in file/container xattrs and in tokens.

Dependencies and integration points: depends on `Mapping`, `StringConversion`, `Egroup`, global `gOFS`, `_attr_ls`, namespace xattr maps, and token objects on `VirtualIdentity`. `Server.cc` and `AccessChecker.cc` consume the computed booleans.

Risks: token path handling is counterintuitive: `TokenAcl` returns a permission rule when `ValidatePath(vid.scope)` is false and returns a restrictive root rule when true; this depends on the token API's return convention and deserves regression coverage. `Set` loops across secondary groups and can repeatedly apply user-specific rules for each group, so denial/reallow ordering is subtle. `mCanChown` is set true even under deny for `c`, matching the comment but surprising. Regex validation and parser behavior must stay aligned, including `wo`, `!`, and `+` combinations.

Test signals: tests should cover numeric/name ACL validation, conversion failures, secondary group matching, egroup matching, `z:` everyone rules, key rules, deny/reallow precedence, immutable `i`, write-once `wo`, sys-only permissions `A/X/p/t/q`, token ACL replacement and scope failures, file-level user ACL evaluation, and `AllowXAttrUpdate` for `sys.acl` versus other `sys.*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/acl/Acl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/acl/Acl.hh -->
## sources/distributed-fs/eos/mgm/acl/Acl.hh

Purpose: declares `eos::mgm::Acl`, a compact interpreter for EOS ACL strings stored in metadata xattrs or carried by tokens. The class exposes permission booleans used by authorization code.

Important APIs and types: four regex constants describe generic/numeric user and system ACL syntax. Static helpers `IsValid` and `ConvertIds` validate and normalize ACL strings. Constructors accept explicit sys/user ACLs, xattr maps, or a path plus error object. `SetFromAttrMap` and `Set` recompute state. Inline getters expose all permission flags, original/effective ACL strings, and whether user ACLs were evaluated. `TokenAcl` extracts token permissions. `AllowXAttrUpdate` authorizes ACL/sys xattr updates.

Control flow: callers construct an `Acl` near the access decision, then inspect getters. `SetFromAttrMap` is the preferred path when metadata xattrs are already available and avoids another namespace lookup.

State and persistence: instance state is a set of booleans and cached ACL strings; no persistence is performed by the header. Xattrs and tokens are the durable sources.

Dependencies and integration points: includes namespace macros, identity mapping, container/file metadata interfaces, and `XrdOucErrInfo` forward declaration. Used by `AccessChecker` and `FuseServer::Server`.

Risks: many permissions are represented as independent booleans, so new rights require updates in constructors, parser, getters, debug output, validators, and consumers. Inline `TokenAcl` declaration hides a nontrivial implementation in the `.cc`. The public API exposes both positive and negative flags, and consumers must apply denial precedence consistently.

Test signals: compile tests should ensure all regex constants remain valid POSIX extended regexes; behavior tests should instantiate from xattr maps and confirm getters used by `Server`/`AccessChecker` reflect expected effective rights.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/acl/Acl.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/adminsocket/AdminSocket.cc -->
## sources/distributed-fs/eos/mgm/adminsocket/AdminSocket.cc

Purpose: implements a small ZeroMQ REP admin socket that accepts IPC requests, maps them to MGM proc commands, executes them as root identity, and returns command output.

Important APIs and functions: `AdminSocket::Run` creates a ZMQ context/socket, binds to `mSocket`, polls with a 100 ms timeout, receives request bytes, splits command and CGI at `?`, creates an `IProcCommand` through `ProcInterface::GetProcCommand`, opens/stat/reads/closes it, and sends the result as the reply.

Control flow: the thread loops until `ThreadAssistant` reports termination. Invalid receives are ignored after logging. Requests without `?` do not create a proc command and receive an empty reply. ZMQ send/receive exceptions are logged and the loop continues.

State and persistence: no persistent state is owned here. The socket path is in `mSocket`; all command side effects are delegated to the proc command implementation and global MGM services.

Dependencies and integration points: depends on `zmq.hpp`, `IProcCommand`, `ProcInterface`, `XrdOucErrInfo`, EOS logging, and `VirtualIdentity::Root`. The header starts this function in an `AssistedThread`.

Risks: every valid command is executed as root and identified as `adminsocket@localhost`, so socket filesystem permissions and path ownership are the effective security boundary. There is no explicit maximum reply size beyond command `stat` result. Empty or malformed input silently returns an empty frame, which may hide client errors. Binding failures are not caught in `Run`.

Test signals: tests should cover command/CGI splitting, empty request behavior, proc command errors, large outputs, termination while polling, ZMQ exception handling, and deployment checks for IPC socket permissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/adminsocket/AdminSocket.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/adminsocket/AdminSocket.hh -->
## sources/distributed-fs/eos/mgm/adminsocket/AdminSocket.hh

Purpose: declares `eos::mgm::AdminSocket`, a lightweight threaded wrapper around the ZeroMQ admin command loop.

Important APIs and types: default constructor leaves the object inactive. The path constructor prefixes `ipc://`, logs the socket path, stores it in `mSocket`, and starts `mThread` with `AdminSocket::Run`. The destructor joins the assisted thread. `Run(ThreadAssistant&) noexcept` is implemented in the `.cc`.

Control flow: construction with a path starts serving immediately; destruction requests/join behavior is delegated to `AssistedThread`.

State and persistence: state is limited to an `AssistedThread` and socket URI string. It does not persist admin command results.

Dependencies and integration points: includes `AssistedThread`, logging, namespace macros, `zmq.hpp`, and standard string/types. Integrates with MGM process command handling through the implementation.

Risks: starting a thread in the constructor can expose partially constructed object state if future fields are added. The default constructor creates an object whose destructor still joins `mThread`, so `AssistedThread` must tolerate a never-started thread. Socket lifecycle and unlink behavior are not visible in the header.

Test signals: constructor/destructor lifecycle tests should validate default and path-created objects, fast destruction after construction, and safe shutdown when `Run` is blocked in polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/adminsocket/AdminSocket.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/auth/AccessChecker.cc -->
## sources/distributed-fs/eos/mgm/auth/AccessChecker.cc

Purpose: implements stateless metadata access decisions for containers, files, and public anonymous paths. It combines POSIX mode checks with `Acl` flags and special EOS identity rules.

Important APIs and functions: `checkContainer(IContainerMD*, XAttrMap, mode, vid)` builds an `Acl` and delegates to `checkContainer(IContainerMD*, Acl, mode, vid)`. The main container check handles root, daemon read/browse, immutable ACLs, prepare permission, sticky-bit delete rules, POSIX access, and ACL recovery/denial. `checkFile` enforces sticky parent deletion and file execute/browse bits. `checkPublicAccess` gates anonymous/public access based on `eosnobody`, protocol `sss`, squash files, and configured public access depth.

Control flow: container access first applies early allow/deny rules, then performs a POSIX access check unless token identity is present. If POSIX fails and ACLs exist, it tests requested write/read/execute bits against positive and negative ACL flags. File checks are intentionally narrower and currently only inspect execute permission except deletion.

State and persistence: no mutable state or persistence. It reads metadata fields, xattr-derived ACLs, and global mapping/public-access configuration.

Dependencies and integration points: depends on `Acl`, `common/Definitions.hh` permission bits such as `P_OK` and `D_OK`, `IFileMD`, `IContainerMD`, `common::Path`, and `Mapping`. It provides a lower-level authorization utility used by MGM code paths outside direct FUSE capability issuance.

Risks: token identities bypass POSIX checks and rely entirely on ACL evaluation; consumers must pass a token-derived ACL scope correctly. File access does not evaluate file ACLs, only mode bits for browse and parent container checks elsewhere. Sticky-bit delete logic is split between container and file checks, so both must be called for complete semantics.

Test signals: tests should cover root/daemon shortcuts, immutable ACL write denial, prepare permission, sticky directory delete for owner/non-owner, ACL positive recovery after POSIX denial, explicit ACL denials overriding mode bits, token behavior, file execute bit matrix, eosnobody squash access, and public access depth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/auth/AccessChecker.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/auth/AccessChecker.hh -->
## sources/distributed-fs/eos/mgm/auth/AccessChecker.hh

Purpose: declares the stateless `eos::mgm::AccessChecker` authorization helper for containers, files, and public path access.

Important APIs and types: two `checkContainer` overloads accept either linked attributes or an already built `Acl`. `checkFile` checks a file with requested mode and parent directory mode. `checkPublicAccess` checks anonymous/public access for a full path and virtual identity.

Control flow: callers are expected to gather all required metadata and xattrs before invoking these methods; the header notes that no external information should be needed by the overload that accepts `Acl`.

State and persistence: no instance or static state is declared; methods are static and read-only over supplied metadata/identity.

Dependencies and integration points: includes namespace macros, identity mapping, and `IContainerMD`; forward-declares file/container metadata and `Acl`. Used by authorization-sensitive MGM paths that need reusable POSIX+ACL checks.

Risks: the API takes raw metadata pointers and does not express nullability. `checkFile` requires the parent directory to be checked separately; callers can accidentally use it alone and miss directory permissions.

Test signals: compile tests should verify callers can pass prebuilt ACLs without pulling path lookup dependencies. Unit tests should exercise null handling expectations if callers may pass missing metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/auth/AccessChecker.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/authz/XrdMgmAuthz.cc -->
## sources/distributed-fs/eos/mgm/authz/XrdMgmAuthz.cc

Purpose: implements the XRootD authorization plugin entry points for EOS MGM and a minimal `XrdMgmAuthz::Access` decision. The plugin primarily ensures requests have an authenticated identity or EOS token before allowing XRootD-layer access; deeper authorization is handled by MGM logic.

Important APIs and functions: global `gMgmAuthz` stores the singleton plugin instance. `XrdAccAuthorizeObject` creates or returns it and emits version/initialization messages. `XrdAccAuthorizeObjAdd` rejects chaining and delegates to the main factory. `XrdMgmAuthz::Access` logs path/env/entity, grants all privileges for EOS token environments, requires either `Entity->name` or entity attribute `request.name`, and otherwise returns no privileges.

Control flow: plugin construction is lazy and singleton. Access decisions are intentionally coarse: EOS token means `XrdAccPriv_All`; missing entity/name means `XrdAccPriv_None`; otherwise all privileges are granted.

State and persistence: only the process-global plugin pointer is retained. No policy is persisted here.

Dependencies and integration points: depends on XRootD `XrdAccAuthorize`, `XrdSysError`, `XrdOucEnv`, `XrdSecEntityAttr`, version macros, EOS token detection, security entity logging, and EOS logging. It plugs into XRootD via the C symbols expected by `authlib`.

Risks: `Test` in the header always returns deny, so callers must use `Access` results directly or this implementation would fail privilege tests. The broad `XrdAccPriv_All` return means MGM request handlers must enforce actual authorization. Plugin chaining is explicitly unsupported. Entity attribute API use assumes `eaAPI` exists when `Entity` exists.

Test signals: plugin load tests should verify singleton behavior, duplicate load messages, no-chaining behavior, EOS token grant, null entity denial, request-name fallback, and compatibility with XRootD versions used in deployment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/authz/XrdMgmAuthz.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/authz/XrdMgmAuthz.hh -->
## sources/distributed-fs/eos/mgm/authz/XrdMgmAuthz.hh

Purpose: declares `XrdMgmAuthz`, the EOS MGM XRootD authorization plugin class implementing `XrdAccAuthorize`.

Important APIs and types: `Access` is the main override returning privileges for a path/operation/environment. `Audit` is overridden as a no-op success. `Test` is overridden but always returns 0. `gMgmAuthz` is declared as the global plugin handle.

Control flow: XRootD obtains an instance through C factory functions in the `.cc`, then calls `Access`, optionally `Audit`/`Test`.

State and persistence: no per-instance state beyond inherited logging identity. The global pointer controls singleton lifecycle.

Dependencies and integration points: includes XRootD authorization headers and EOS logging. The class lives in the global namespace, matching plugin ABI expectations rather than MGM namespace macros.

Risks: `Audit` and `Test` are placeholders, which is safe only if the server does not rely on them for enforcement or audit records. The header exposes a mutable global pointer and default destructor without ownership cleanup.

Test signals: ABI tests should confirm the class satisfies XRootD virtual interface expectations. Integration tests should verify actual XRootD authorization uses `Access` and not `Test` for final decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/authz/XrdMgmAuthz.hh -->
