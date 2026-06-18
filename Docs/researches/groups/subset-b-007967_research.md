# subset-b-007967 research

Grouped research for XRootD password, SSS, Unix, and ZTN security module sources. Each section preserves its source path for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecpwd/XrdSecpwdSrvAdmin.cc -->
# sources/distributed-fs/xrootd/src/XrdSecpwd/XrdSecpwdSrvAdmin.cc

Purpose: standalone `xrdpwdadmin`-style administration program for XRootD password security files. It creates and mutates admin, user, netrc, and server-public-key files under `~/.xrd/` by default.

Important APIs and functions: `main()` parses options, opens an `XrdSutPFile`, handles actions, and writes `XrdSutPFEntry` records. `ParseArguments()`, `ParseCrypto()`, and `CheckOption()` drive global CLI state. `AddPassword()` has hashed and raw-password variants. `SavePasswd()`, `ReadPasswd()`, `SavePuk()`, `ReadPuk()`, `GeneratePuk()`, `ExpPuk()`, and `LocateFactoryIndex()` manage generated passwords and public-key cipher material.

Control flow: startup selects mode and file path, loads crypto factories, creates the backing file if requested, then dispatches `add`, `update`, `read`, `remove`, `disable`, `copy`, `trim`, or `browse`. Admin mode also ensures special entries for server ID, email, hostname, and cipher public keys. Password updates loop over crypto modules, create tags suffixed by crypto factory ID, and write one entry per module.

State and persistence: most program state is global. Persistent state is stored in `XrdSutPFile` records and side files under `genpwd/` and `genpuk/`. Password entries store salts and derived hashes unless `-nohash` is used for netrc compatibility. Public-key backup files serialize factory IDs, lengths, and cipher buckets.

Dependencies and integration: depends on `XrdSut` password-file primitives, `XrdCryptoFactory`, `XrdCryptoCipher`, `XrdOucString`, POSIX file APIs, user lookup, and directory scanning. Its outputs are consumed by the password security protocol and administrative deployment flows.

Risks: sensitive credentials can be written to generated password files by design, so permissions are critical. The code has many globals, manual memory ownership, interactive branches, and fixed-size parsing buffers. The default `PukFile` initializer contains a stale absolute path but is normally overwritten. Some write loops only retry `EINTR` and do not validate short writes.

Test signals: exercise all four modes with temporary `HOME`, verify file modes, add/update/remove/disable/copy/trim behavior, crypto-list handling, imported password/public-key parsing, one-time password state, public-key rotation preserving old buffers, and failure paths for missing factories or malformed import files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecpwd/XrdSecpwdSrvAdmin.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecpwd/XrdSecpwdTrace.hh -->
# sources/distributed-fs/xrootd/src/XrdSecpwd/XrdSecpwdTrace.hh

Purpose: small trace macro header for the password security module. It centralizes debug, authentication, and dump tracing behind `XrdOucTrace`.

Important APIs and types: exposes `QTRACE`, `PRINT`, `TRACE`, `NOTIFY`, `DEBUG`, and `EPNAME` macros when `NODEBUG` is not defined. Defines trace bit masks `TRACE_ALL`, `TRACE_Dump`, `TRACE_Authen`, and `TRACE_Debug`, and declares external `XrdOucTrace *pwdTrace`.

Control flow: callers declare an endpoint name with `EPNAME()` and call trace macros. `QTRACE` checks `pwdTrace->What` against the requested bit, `PRINT` wraps output in `Beg()`/`End()`, and `TRACE` conditionally prints. In `NODEBUG` builds, macros expand to empty forms.

State and persistence: no persistence. Runtime state is the external trace pointer and its `What` mask.

Dependencies and integration: includes `XrdOucTrace.hh` and, for debug builds, `XrdSysHeaders.hh` for stream output. Integrated by password protocol code that wants compile-time removable diagnostics.

Risks: macro-based logging can evaluate stream expressions only when active, but callers must still ensure referenced names such as `epname` exist. The file banner says `XrdSecgsiTrace.hh`, likely copy-paste drift. Empty `QTRACE(x)` in `NODEBUG` can be unsafe if used in expression contexts expecting a value.

Test signals: compile modules with and without `NODEBUG`, verify trace masks enable expected output, and check no password secrets are logged at normal debug levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecpwd/XrdSecpwdTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdSecsss/CMakeLists.txt

Purpose: build description for the SSS shared-secret security plugin and its administration utility.

Important targets: sets `XrdSecsss` to `XrdSecsss-${PLUGIN_VERSION}`. Adds support sources `XrdSecsssCon`, `Ent`, `ID`, `KT`, and `Map` to `XrdUtils`. Builds module library from `XrdSecProtocolsss.cc`, its header, and `XrdSecsssRR.hh`. Optionally builds `xrdsssadmin` when `XRDCL_LIB_ONLY` is false.

Control flow: target setup is straightforward: utility sources become part of `XrdUtils`, plugin module links `XrdCryptoLite` and `XrdUtils`, the umbrella `plugins` target depends on it, and install rules place module libraries and the admin executable in standard CMake install dirs.

State and persistence: no runtime state. It defines packaging/install topology and determines which SSS helpers are available to both the plugin and other XRootD components through `XrdUtils`.

Dependencies and integration: integrates with the repository-level `PLUGIN_VERSION`, `plugins` aggregate target, `CMAKE_INSTALL_LIBDIR`, and `CMAKE_INSTALL_BINDIR`. The admin tool only links `XrdUtils` because keytab logic is compiled there.

Risks: adding implementation files to `XrdUtils` broadens ABI and link exposure. `XRDCL_LIB_ONLY` disables the admin executable, so packaging tests should cover both client-only and full builds.

Test signals: configure/build with full and `XRDCL_LIB_ONLY` options, verify module name includes plugin version, confirm install paths, and run a link check for `xrdsssadmin`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecProtocolsss.cc -->
# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecProtocolsss.cc

Purpose: implementation of the XRootD `sss` security protocol. It creates encrypted credentials from local or mapped identities on clients and authenticates them on servers using shared keytabs.

Important APIs and functions: implements `Authenticate()`, `getCredentials()`, `Init_Client()`, `Init_Server()`, `Load_Client()`, `Load_Server()`, exported `XrdSecProtocolsssInit()`, and exported `XrdSecProtocolsssObject()`. Private helpers `Decode()`, `Encode()`, `getCred()`, `getLID()`, `Load_Crypto()`, `myClock()`, `setID()`, and `setIP()` manage packets, crypto, and identity buffers. Local `Persona` accumulates decoded identity fields.

Control flow: load-time init chooses keytab and crypto settings. Client object init parses server parameters of the form encryption/lifetime/keytab. `getCredentials()` extracts socket and URL identity hints, obtains serialized identity data from `XrdSecsssID` or static identity, selects a key, fills an SSS record header, and encrypts the data. Server `Authenticate()` validates size and protocol, decrypts via keytab lookup, checks credential age and source host/IP unless disabled by key options, handles mutual-auth login-ID exchange, maps identity and groups based on key options, and populates `XrdSecEntity`.

State and persistence: static process-wide defaults include `ktObject`, `CryptObj`, `idMap`, `staticID`, `aProts`, `deltaTime`, and mode flags. Per-instance state holds endpoint names/IPs, active keytab/crypto references, sequence state, and a reusable identity buffer. Persistent secrets live in keytab files managed by `XrdSecsssKT`.

Dependencies and integration: integrates with the XRootD security plugin ABI, `XrdSecEntity`, `XrdOucErrInfo`, `XrdOucEnv`, `XrdOucPup`, `XrdNetAddrInfo`, `XrdNetUtils`, `XrdCryptoLite`, `XrdSecsssKT`, `XrdSecsssID`, `XrdSecsssEnt`, and RR wire structs. Environment variables include `XrdSecDEBUG`, `XrdSecSSSKT`, and `XrdSecsssKT`.

Risks: security-sensitive parsing uses packed binary data, manual allocation, `alloca`, and static mutable globals guarded only during some init paths. Clock skew causes credential expiry. Host/IP checks can be disabled by key-name convention. V1/V2 buffer limits and key-name padding require exact compatibility tests.

Test signals: round-trip credentials for static, mapped, mutual, and proxied modes; key-name V2 lookup; expired credential rejection; IP mismatch rejection; keytab refresh; malformed packet sizes/types; unsupported crypto; missing keytab; and attribute key/value ordering errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecProtocolsss.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecProtocolsss.hh -->
# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecProtocolsss.hh

Purpose: class declaration for the SSS security protocol object implementing `XrdSecProtocol`.

Important APIs and types: declares `Authenticate()`, `getCredentials()`, `Delete()`, `Init_Client()`, `Init_Server()`, static `Load_Client()`, `Load_Server()`, `eMsg()`, `Fatal()`, and nested `Crypto` descriptor. Private methods cover encoding/decoding, credential selection, crypto loading, endpoint setup, and identity string packing.

Control flow: the constructor records protocol name `sss`, duplicates the remote host name, and stores endpoint IP formats. Object creation through the plugin ABI calls init methods, while deletion is explicit through `Delete()` because the destructor is private.

State and persistence: declares static defaults shared across instances: keytab object, crypto object, ID map, allowed proxy protocols, static identity, lifetime, and mode flags. Instance state tracks active keytab/crypto, endpoint, serialized identity buffer, data options, sequence state, and V2 endpoint negotiation.

Dependencies and integration: includes crypto-lite, network endpoint, security interface, keytab, ID, and record/response headers. This header is the integration contract between the plugin ABI and SSS implementation internals.

Risks: static mutable fields mean process-global behavior can be surprising in tests or mixed client/server contexts. The private destructor requires all users to call `Delete()`. `char *` ownership is manual.

Test signals: compile ABI exports against this declaration, instantiate client/server objects, call `Delete()` under leak sanitizers, and verify static defaults are initialized exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecProtocolsss.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssAdmin.cc -->
# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssAdmin.cc

Purpose: command-line keytab administration utility `xrdsssadmin` for adding, deleting, installing, and listing SSS shared-secret keys.

Important APIs and functions: `main()` parses options into `XrdsecsssAdmin_Opts`. Actions dispatch to `XrdSecsssAdmin_addKey()`, `delKey()`, `insKey()`, and `lstKey()`. Helpers include `getXDate()`, `isNo()`, `Usage()`, `XrdSecsssAdmin_isKey()`, and `XrdSecsssAdmin_Here()` for filtering and sorting.

Control flow: options select key name/user/group, expiration, keep count, key length, key number, debug, and sort column. `add` creates or opens a keytab, appends a generated key, and rewrites. `del` filters by key attributes or number and may unlink the file if no keys remain. `install` reads keytab data from stdin and writes selected keys to a destination. `list` loads, sorts, filters, and prints table rows.

State and persistence: persistent state is the keytab file path, defaulting through `XrdSecsssKT::genFN()`. Rewrites prune expired keys and enforce the per-name keep count. Expiration accepts days-from-midnight or `%D` date format.

Dependencies and integration: built from `XrdSecsss/CMakeLists.txt`, linked with `XrdUtils`, and depends on `XrdSecsssKT`, POSIX file APIs, `XrdSysTimer`, and error translation.

Risks: destructive delete paths are interactive but still powerful. `install` depends on stdin parsing through the keytab class. Option `-h` is used for hold count rather than help. Expiration parsing through `strptime("%D")` is locale/time-zone sensitive.

Test signals: add/list/delete/install against temporary keytabs, check key length normalization to multiples of four, expiration pruning, sorting columns, nonexistent file behavior, all-keys-deleted prompt, and stdin install filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssAdmin.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssCon.cc -->
# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssCon.cc

Purpose: implementation of contact tracking for mapped SSS identities. It records outbound contacts against a registered login ID so they can be cleaned up when the identity is unregistered.

Important API: `XrdSecsssCon::Contact(const std::string &lgnid, const std::string &hostID)` is the only function. It is paired with the abstract `Cleanup()` declared in the header.

Control flow: the method first verifies this object is the process-global tracker. It extracts the login portion before `@`, strips an optional password after `:`, validates size and shape, locks the global SSS registry, looks up the login ID, and calls `XrdSecsssEnt::AddContact()` on the mapped entity.

State and persistence: no persistence. Runtime state is global `conTrack`, global `Registry`, and each entity's in-memory `Contacts` set.

Dependencies and integration: uses `XrdSecsssMap` globals shared with `XrdSecsssID`, and `XrdSecsssEnt` to store contacts. Cleanup is invoked from entity deletion.

Risks: the `lgnid` parameter is unused; the login is derived from `hostID`. Invalid host strings are silently rejected. Global locking protects map access, but cleanup behavior depends on external subclass correctness.

Test signals: register mapped identities, add duplicate and distinct contacts, verify password stripping, reject malformed host IDs, unregister and assert subclass `Cleanup()` receives the expected set and entity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssCon.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssCon.hh -->
# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssCon.hh

Purpose: abstract interface for tracking and cleaning contacts created by SSS mapped identities.

Important APIs: subclasses implement `Cleanup(const std::set<std::string>&, const XrdSecEntity&)`. Concrete `Contact(const std::string &lgnid, const std::string &hostID)` records a connection in the registered entity if tracking is enabled.

Control flow: lifecycle is external. A tracker is passed to `XrdSecsssID`; when an entity is deleted, `XrdSecsssEnt::Delete()` calls `Cleanup()` with the accumulated contacts and entity, then deletes the entity.

State and persistence: the interface itself owns no state. Contact state lives in `XrdSecsssEnt`.

Dependencies and integration: includes C++ `set` and `string`, forward declares `XrdSecEntity`, and integrates with `XrdSecsssID` construction.

Risks: cleanup is synchronous and subclass-defined, so slow or throwing implementations could affect unregister paths. The comments say contacts use `user[:pswd]@host:port`; password-bearing strings require careful downstream handling.

Test signals: compile a mock subclass, pass it into mapped ID mode, call `Contact()`, unregister identities, and verify cleanup ordering and ownership expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssCon.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssEnt.cc -->
# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssEnt.cc

Purpose: serializes `XrdSecEntity` identity data into SSS record/response data blocks and owns per-entity contact cleanup state.

Important APIs and functions: `AddContact()`, `Delete()`, `RR_Data()`, `Serialize()`, and static `setHostName()`. Local `copyAttrs` walks `XrdSecEntityAttr` key/value pairs twice: first for sizing, then for packing.

Control flow: construction optionally serializes an entity. `Serialize()` computes V1 identity size, pads small payloads with random data, computes V2 extras, includes protocol, trace ID, uid/gid names for cloned protocols, entity attributes, capabilities, and optional credentials. `RR_Data()` lazily serializes if needed, prepends client IP and cached hostname, selects V1 or V2 payload length, and returns a malloc-owned buffer.

State and persistence: per-object state includes packed `eData`, V1 length, total V2 length, credential length, source entity pointer, reference count, and contact set. Static state caches packed local hostname. No disk persistence.

Dependencies and integration: uses `XrdOucPup` packing, `XrdOucUtils` uid/gid lookup, `XrdSecEntity`, `XrdSecEntityAttr`, `XrdSecsssRR`, `XrdSecsssKT::genKey`, and optional `XrdSecsssCon` cleanup.

Risks: `RR_Data()` computes `strlen(hostIP)` before checking for null, so callers must pass a non-null IP despite later conditional code. Deferred serialization requires the original `XrdSecEntity` to remain valid. Manual packed-size math must stay in sync with wire constants.

Test signals: serialize minimal and full entities, V1/V2 option combinations, credentials at and above `MaxCSz`, entity attributes, non-sss underlying protocols, null/empty host handling, and cleanup callback invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssEnt.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssEnt.hh -->
# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssEnt.hh

Purpose: declares the SSS entity serialization and contact-tracking object used by the protocol client side and ID mapper.

Important APIs and types: public fields `eData`, `iLen`, and `tLen` expose packed data and lengths. Methods include `AddContact()`, `Delete()`, `RR_Data()`, `Ref()`, `UnRef()`, and static `setHostName()`. Constants `addExtra`, `addCreds`, and `v2Client` control serialized data detail.

Control flow: construction stores an `XrdSecEntity` pointer and serializes immediately unless `defer` is true. Destruction is private; callers use `Delete()` or reference counting.

State and persistence: owns malloc-packed identity data, reference count, optional contacts, credential length, and static hostname buffer. No persistent storage.

Dependencies and integration: uses `XrdSysAtomics`/mutex fallback, C++ sets, and `XrdSecEntity`. It is stored in `XrdSecsssID` registries and consumed by `XrdSecProtocolsss::getCred()`.

Risks: public packed-data members expose mutable internals. Deferred mode depends on external entity lifetime. Manual ref counting can conflict with `Delete()` if ownership rules are mixed.

Test signals: construct immediate/deferred entities, call `RR_Data()` repeatedly, verify reference count deletion, and run under leak/thread sanitizers around contact cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssEnt.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssID.cc -->
# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssID.cc

Purpose: implements the optional process-wide login-ID-to-entity registry for SSS clients.

Important APIs and functions: constructor `XrdSecsssID::XrdSecsssID()`, private destructor, `Find()`, static `genID()`, static `getObj()`, and public `Register()`. Namespace `XrdSecsssMap` defines global mutex, mapper pointer, contact tracker, and registry map.

Control flow: only one mapper can be effective. Construction validates auth type, creates a default identity, installs the global mapper, and optionally enables contact tracking for mapped modes. `getObj()` returns current auth mode and default identity, generating one if needed. `Register()` adds, replaces, or removes mappings under lock. `Find()` looks up a login ID and falls back to default identity, returning serialized RR data.

State and persistence: all state is in process memory: global mapper, registry, default identity, and contact tracker. `genID()` derives identity from process uid/gid unless secure mode forces `nobody/nogroup`, and may set endorsements from `XrdSecsssENDORSEMENT`.

Dependencies and integration: used by `XrdSecProtocolsss::Load_Client()` and credential generation. Depends on `XrdSecEntity`, `XrdSecsssEnt`, `XrdSecsssMap`, `XrdOucUtils`, and `XrdSysMutex`.

Risks: singleton behavior means later construction is ineffective. Deferred registration can store pointers to mutable external entities. `Find()` calls `RR_Data()` while holding the global mutex, so serialization cost and callbacks can extend lock hold time.

Test signals: singleton construction, each auth type, default identity generation, register/replace/delete behavior, mapped fallback, environment endorsements, and concurrent register/find access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssID.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssID.hh -->
# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssID.hh

Purpose: public interface for applications to configure SSS client identity mapping before connecting to SSS-enabled servers.

Important APIs and types: `authType` enumerates dynamic, mapped, mapped mutual, static, and static mutual modes. The constructor installs the singleton mapper with optional default identity and contact tracker. `Register()` creates, replaces, or deletes login-ID mappings.

Control flow: users create one instance before connections. The protocol later calls private `getObj()` and `Find()` to determine whether credentials are static, mapped, or mutual-authenticated.

State and persistence: declares default identity pointer, auth type, static/mapped flag, and tracking flag. Actual registry state is implemented in `XrdSecsssID.cc`; no disk persistence.

Dependencies and integration: forward declares `XrdSecEntity`, `XrdSecsssCon`, and `XrdSecsssEnt`, keeping the public header light. Applications must link with `libXrdUtils.so`.

Risks: comments note the object cannot be deleted once created, effectively making it process-global configuration. Mutual authentication depends on login IDs matching server-returned values unless mapped modes override lookup.

Test signals: API compile tests in external clients, construction with every auth type, register failure in static mode, and integration with protocol credential generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssID.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssKT.cc -->
# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssKT.cc

Purpose: keytab storage, parsing, refresh, random key generation, lookup, and atomic rewrite support for SSS shared-secret keys.

Important APIs and functions: constructor/destructor, `addKey()`, `delKey()`, `getKey()`, `genFN()`, `genKey()`, `Refresh()`, `Rewrite()`, `getKeyTab()`, `fileMode()`, `isKey()`, `keyB2X()`, `keyX2B()`, and `ktDecode0()`. `XrdSecsssKTRefresh()` is the refresh-thread entry point.

Control flow: construction opens random source, stats and parses the keytab, then starts a refresh thread for client/server modes. `getKeyTab()` checks permissions, reads records, decodes tagged fields, discards expired non-admin keys, and orders entries. `getKey()` selects by name, key ID, or both, preferring unexpired keys for clients. `Rewrite()` creates parent paths, writes a temporary file, prunes expired/old keys, and renames atomically.

State and persistence: persistent state is the keytab file, defaulting to `$HOME/.xrd/sss.keytab`. In-memory state is a linked list of `ktEnt`, file mtime, mode, refresh interval, highest key ID, mutex, refresh thread, and static random fd.

Dependencies and integration: used by the SSS protocol and `xrdsssadmin`. Depends on `XrdOucStream`, `XrdOucUtils`, `XrdSysThread`, POSIX file APIs, and `/dev/urandom` or fallback pseudo-random generation.

Risks: security depends on strict file modes; `.grp` files intentionally allow group read. Fallback random generation is weaker. Refresh thread runs forever until destructor kills it. Text parser must reject malformed tags and overlong fields. `Refresh()` contains a suspicious expression `if ((retc == eInfo.getErrInfo()) == 0)`.

Test signals: parse valid/invalid keytabs, permissions rejection, `.grp` mode allowance, expired key pruning, name/key-ID lookup, refresh after mtime change, rewrite atomicity and keep count, random key length, and admin stdin mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssKT.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssKT.hh -->
# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssKT.hh

Purpose: declares the SSS keytab manager and key entry representation.

Important APIs and types: nested `ktEnt` defines maximum key/name/user/group sizes, `ktData`, option bits `allUSR`, `anyUSR`, `anyGRP`, `usrGRP`, and `noIPCK`, plus helpers `NUG()` and `Set()`. `XrdSecsssKT` exposes add/delete/get/list/refresh/rewrite/path APIs, `genFN()`, `genKey()`, and mode enum `isAdmin`, `isClient`, `isServer`.

Control flow: callers construct with an error object, keytab path, mode, and refresh interval. Admin mode mutates and rewrites keytabs; client/server modes use lookup and background refresh.

State and persistence: header declares linked-list key state, keytab path, mtime, mode, refresh interval, mutex, refresh thread ID, and static random fd. Persistence format is implemented in the `.cc`.

Dependencies and integration: includes time, string/memory helpers, and `XrdSysPthread`. Used by protocol, RR header for key-name size, and admin CLI.

Risks: fixed-size char arrays require strict bounds in parser and CLI. `ktEnt::Set()` copies only selected fields, intentionally not name/user/group/options, which is correct for same-NUG replacement but risky if misused elsewhere.

Test signals: compile users against constants, verify option-bit effects in protocol auth, and unit-test `Same()`, `setPath()`, key list ownership, and lifecycle with refresh threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssKT.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssMap.hh -->
# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssMap.hh

Purpose: shared internal declarations for the SSS identity registry namespace.

Important APIs and types: declares global `XrdSysMutex sssMutex`, `XrdSecsssID *IDMapper`, `XrdSecsssCon *conTrack`, `typedef std::map<std::string, XrdSecsssEnt*> EntityMap`, and external `Registry`.

Control flow: no executable code. It lets `XrdSecsssID.cc`, `XrdSecsssCon.cc`, and entity code share the same registry and lock.

State and persistence: declares process-global in-memory state only. Definitions live in `XrdSecsssID.cc`.

Dependencies and integration: includes C++ map/string and forward declarations, but relies on `XrdSysMutex` being visible from includers; this works because implementation files include mutex headers before or through other headers.

Risks: global mutable registry creates singleton semantics and can complicate tests. Header does not include the mutex type declaration directly, making include-order assumptions fragile.

Test signals: compile include-order checks, registry operations under concurrency, and teardown behavior when mapped entities are deleted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssMap.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssRR.hh -->
# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssRR.hh

Purpose: defines the SSS wire-format request/response headers and encrypted data tags.

Important types: `XrdSecsssRR_Hdr` is the unencrypted protocol header with protocol ID, key-name size, encryption type, and key ID. `XrdSecsssRR_Hdr2` extends it with a padded key name for V2 clients. `XrdSecsssRR_DataHdr` carries random bytes, generation time, padding, and options. `XrdSecsssRR_Data` defines max/min payload sizes and typed fields for identity, attributes, credentials, login ID, and host. `XrdSecsssRR_DataResp` is a short server response.

Control flow: protocol code casts raw credential buffers to these structs, encrypts/decrypts the data header and payload, and iterates `<type><packed value>` entries.

State and persistence: no persistent state. Constants encode compatibility constraints for V1 and V2 peers.

Dependencies and integration: includes integer/time headers and `XrdSecsssKT.hh` for key-name size. Used by protocol, entity serialization, and ID mapping.

Risks: layout is ABI/wire-format critical; padding, endian conversion, and struct sizes must remain stable. Comments say protocol ID is `"sss"` while the field is four bytes and code copies the null terminator. Max size constants must match protocol buffer checks.

Test signals: static assertions or serialization tests for struct sizes, V1/V2 packet round trips, malformed type streams, max credential payloads, and key-name padding/termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssRR.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecunix/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdSecunix/CMakeLists.txt

Purpose: build description for the Unix security plugin.

Important targets: sets module target name `XrdSecunix-${PLUGIN_VERSION}`, builds it from `XrdSecProtocolunix.cc`, links privately to `XrdUtils`, adds it to the `plugins` aggregate target, and installs the module library.

Control flow: no conditional branches; the Unix plugin is always built when this directory is included.

State and persistence: no runtime state. It controls target naming and install layout.

Dependencies and integration: depends on repository-level plugin version and standard install variables. The module exports the security plugin ABI implemented in the `.cc`.

Risks: minimal CMake means no direct tests or platform guards here; portability issues surface in the implementation.

Test signals: configure/build, confirm module output name and install path, and run plugin loading smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecunix/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecunix/XrdSecProtocolunix.cc -->
# sources/distributed-fs/xrootd/src/XrdSecunix/XrdSecProtocolunix.cc

Purpose: simple Unix identity security protocol plugin that sends effective user and group names as credentials.

Important APIs and functions: local class `XrdSecProtocolunix` implements `Authenticate()`, `getCredentials()`, and `Delete()`. Exports `XrdSecProtocolunixInit()` and `XrdSecProtocolunixObject()` for the XRootD security plugin ABI.

Control flow: client `getCredentials()` creates a buffer beginning with `"unix"`, appends effective username and optional group name, and returns `XrdSecCredentials`. Server `Authenticate()` accepts empty credentials as host identity, verifies the `"unix"` protocol ID, duplicates the credential string, splits username and group on spaces, and fills `XrdSecEntity`. Object creation stores endpoint host/address.

State and persistence: per-instance state is endpoint address, allocated host string, and duplicated credential buffer. No persistence, no cryptographic state, and init returns empty parameters.

Dependencies and integration: uses `XrdOucUtils::UserName()` and `GroupName()`, `XrdNetAddrInfo`, `XrdSecInterface`, and XRootD version/export macros.

Risks: this protocol does not authenticate cryptographically; it trusts client-supplied username/group and is appropriate only in trusted/local contexts. Credential parsing is space-delimited, so unusual names are not supported. Empty credentials map to `prot=host` and name `"?"`.

Test signals: plugin load, credential generation for known euid/egid, server parse with and without group, protocol mismatch error, empty credential handling, and leak checks for repeated authentication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecunix/XrdSecProtocolunix.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecztn/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdSecztn/CMakeLists.txt

Purpose: build description for the ZTN security plugin.

Important targets: sets `XrdSecztn` to `XrdSecztn-${PLUGIN_VERSION}`, builds a module from `XrdSecProtocolztn.cc` and `XrdSecztn.cc`, links privately to `XrdUtils`, and installs the module library.

Control flow: no conditionals or aggregate dependency line in this file; it assumes the parent build includes and installs the module target.

State and persistence: no runtime state. It only controls build/install metadata for the ZTN plugin.

Dependencies and integration: uses repository plugin-version conventions and CMake install lib dir. The implementation files are outside this work item but are the runtime integration points.

Risks: unlike the SSS and Unix CMake files, this one does not call `add_dependencies(plugins ${XrdSecztn})`; if the parent expects that aggregate dependency, ZTN may be omitted from plugin umbrella builds.

Test signals: configure/build, verify the module is produced and installed, and compare plugin aggregate behavior with other security modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecztn/CMakeLists.txt -->
