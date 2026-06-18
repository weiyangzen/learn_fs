# Research report: subset-b-007966

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsiProxy.cc -->
## sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsiProxy.cc

### Purpose
`XrdSecgsiProxy.cc` implements the `xrdgsiproxy` command-line utility for creating, inspecting, validating, and deleting GSI proxy certificate files. It is not the server authentication protocol itself; it is an operator/user tool layered on top of the XRootD crypto factory APIs. It loads an X.509-capable crypto plugin, obtains function hooks for proxy creation and certificate parsing, and then drives a small mode-based CLI around proxy files.

### Important APIs, types, and functions
The file defines `kModes` values for `init`, `info`, `destroy`, and `help`, and it keeps the selected mode plus all CLI settings in process-global variables. Key globals include `CryptoMod`, `CAdir`, `CRLdir`, default certificate/key/proxy paths, `Valid`, `Bits`, `PathLength`, `ClockSkew`, and hook pointers such as `XrdCryptoX509ParseFile_t ParseFile`, `XrdCryptoX509CreateProxy_t CreateProxy`, `XrdCryptoX509GetVOMSAttr_t GetVOMSAttr`, and `XrdCryptoProxyCertInfo_t ProxyCertInfo`.

`main()` initializes tracing, loads `XrdCryptoFactory::GetCryptoFactory(CryptoMod)`, resolves required X.509 hooks, and dispatches by mode. `ParseArguments()` parses CLI options and validates filesystem prerequisites. `CheckOption()` recognizes exact option names and `no<name>` variants for boolean switches. `Display()` prints proxy certificate metadata, path-length constraints, key strength, remaining lifetime, VOMS attributes, and optional extension dumps.

### Control flow
Argument parsing is the first gate. Missing proxy path defaults to `/tmp/x509up_u<uid>`, and `init` defaults certificate and key paths to `$HOME/.globus/usercert.pem` and `$HOME/.globus/userkey.pem`. In `init`, the private key must be a regular file with owner-only read/write semantics. After parsing, `main()` sets trace masks, loads the crypto module, resolves the factory hooks, and then executes the selected mode.

`init` converts the requested validity string with `XrdSutParseTime()`, fills `XrdProxyOpt_t`, calls `X509CreateProxy`, and displays the first certificate in the resulting `XrdCryptogsiX509Chain`. `destroy` simply unlinks the proxy file. `info` parses the proxy file into a chain, requires at least two certificates unless `-exists` is being used, displays the proxy, and displays a parent proxy when the subject indicates a limited proxy. The `-exists` path is quiet and returns non-zero if the proxy is absent, too short-lived for `-valid`, or below the requested key strength.

### State and persistence behavior
Persistent state is limited to the proxy file named by `PXcert`; `init` writes it through the crypto factory, `destroy` removes it, and `info` reads it. The tool derives defaults from the current uid and home directory but does not maintain its own metadata. Runtime state is stored in globals, so the program is single-shot and not reentrant as a library.

### Dependencies and integration points
This utility integrates with `XrdCrypto` for X.509 parsing, proxy creation, extension decoding, VOMS extraction, and trace settings. It uses `XrdSut` helpers for time parsing and path expansion, `XrdSysPwd` for uid/home resolution, and `XrdSecgsiTrace.hh` for trace macros. It assumes the selected crypto plugin exports the specific X.509 hook table needed by the GSI implementation.

### Risks and edge cases
CLI parsing is manual and permissive: unknown options are ignored after printing, and some option validation relies on `errno` without visibly resetting it before `strtol()`. `-bits` clamps to at least 2048, which is conservative but may surprise callers asking to validate weaker legacy proxies. `-exists` only checks remaining lifetime and bit strength, not full chain trust. The default `CAdir` and `CRLdir` globals are parsed but not used in this file. Security-sensitive paths are expanded and checked, but proxy file permissions are not validated on read.

### Test signals
Useful tests include `xrdgsiproxy info -f <proxy>`, `xrdgsiproxy -exists -valid <duration> -bits <n> -f <proxy>` exit-code checks, `init` with a temporary certificate/key pair, `destroy` against a temporary proxy file, and negative tests for unreadable keys, bad permissions, malformed proxy chains, missing crypto hook functions, and `-extensions` dumping. Integration with `XrdSecgsitest.cc` covers the lower-level crypto/GSI operations that this tool calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsiProxy.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsiTrace.hh -->
## sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsiTrace.hh

### Purpose
`XrdSecgsiTrace.hh` provides the trace macro layer used by GSI-related tools and protocol code. It centralizes the mapping between named trace categories and `XrdOucTrace::What` bits and compiles trace calls away when `NODEBUG` is defined.

### Important APIs, types, and functions
The header exposes macros `QTRACE(act)`, `PRINT(y)`, `TRACE(act,x)`, `NOTIFY(y)`, `DEBUG(y)`, and `EPNAME(x)`. `QTRACE` checks the global `XrdOucTrace *gsiTrace` and tests a `TRACE_<act>` bit. `PRINT` starts a trace record using the local `epname` symbol, writes to `std::cerr`, and ends the trace record. `NOTIFY` maps to `TRACE(Debug, ...)`; `DEBUG` maps to `TRACE(Authen, ...)`.

Trace bit constants are `TRACE_ALL`, `TRACE_Dump`, `TRACE_Authen`, and `TRACE_Debug`. The file declares, but does not define, `extern XrdOucTrace *gsiTrace`.

### Control flow
The macros are intended to be embedded directly in functions. `EPNAME("name")` defines a function-local static endpoint name. Calls like `DEBUG("message")` only emit output if `gsiTrace` exists and the corresponding bit is enabled. Under `NODEBUG`, all macros expand to empty forms, leaving no runtime checks or output.

### State and persistence behavior
The only state is the external process-global `gsiTrace` pointer and its `What` mask. The header does not allocate, free, or persist anything. Files using this header must define `gsiTrace`, initialize it with an `XrdOucTrace`, and attach an `XrdSysError`/logger if output is desired.

### Dependencies and integration points
The header depends on `XrdOuc/XrdOucTrace.hh` and, in debug builds, `XrdSys/XrdSysHeaders.hh` for stream support. It is used by `XrdSecgsiProxy.cc` and `XrdSecgsitest.cc` in this subset and likely by the GSI protocol plugin elsewhere. Its category names are part of the local tracing convention, so call sites must use `TRACE_` suffixes that match the defined constants.

### Risks and edge cases
The macros assume a visible local `epname` when `PRINT`, `TRACE`, `NOTIFY`, or `DEBUG` are used; call sites that forget `EPNAME()` can fail to compile in debug builds. The macros are statement-like but not wrapped in `do { } while (0)`, so they can be fragile in nested `if/else` contexts. Because tracing writes to `std::cerr`, very verbose tracing can interleave across threads unless `XrdOucTrace` serialization is sufficient.

### Test signals
Compile tests should cover both normal and `NODEBUG` builds. Runtime tests can set `gsiTrace->What` to individual bits and verify that `NOTIFY` and `DEBUG` produce output only for enabled categories. A simple GSI utility invocation with `-debug` is an integration signal that the global trace pointer and masks are wired correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsiTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsitest.cc -->
## sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsitest.cc

### Purpose
`XrdSecgsitest.cc` is a standalone integration test utility for GSI-related crypto functionality. It exercises user certificate/proxy loading, proxy recreation, CA chain construction and verification, bucket import/export, proxy request signing, CRL handling, and GSI-specific chain verification.

### Important APIs, types, and functions
The program defines global paths for the end-entity certificate, key, proxy, generated proxy chain, and CA directory. `pdots()` and `pline()` format PASS/FAIL output. `printHelp()` documents environment-driven inputs. `main()` is the full test body and uses `XrdCryptoFactory` hooks such as `X509CreateProxy`, `X509ParseFile`, `X509ExportChain`, `X509ParseBucket`, `X509CreateProxyReq`, `X509SignProxyReq`, `X509ChainToFile`, and `X509Crl`.

### Control flow
The CLI accepts `-v`, `-vv`, and help options. It initializes GSI tracing, sets SUT and crypto trace levels, loads the `ssl` crypto factory, and resolves the effective user's home directory. It locates input files using `X509_USER_CERT`, `X509_USER_KEY`, `X509_USER_PROXY`, and `X509_CERT_DIR`, falling back to conventional Grid Security paths.

The test loads the user certificate and proxy, recreates a proxy from the certificate/key, and validates that the proxyCertInfo extension exists. It walks issuer hashes through up to five CA certificates until it finds a self-signed root. It then parses the proxy file into a chain, adds CAs, reorders, verifies, exports to an `XrdSutBucket`, imports the bucket into plain and GSI-specific chains, and verifies both. Later phases verify direct certificate signatures, create and sign a proxy request, write a signed proxy chain to `<proxy>p`, inspect CRL distribution point extensions, load a CRL, verify its signature, and perform sample revocation checks.

### State and persistence behavior
The test reads real user and CA material from the filesystem and may create or overwrite the user proxy via `X509CreateProxy`. It writes an additional signed proxy chain to the proxy filename with a `p` suffix. There is no isolation or fixture management in the file itself, so running it against a live account can mutate credential files.

### Dependencies and integration points
The file depends on XRootD crypto abstractions, GSI chain classes, SUT serialization buckets, OpenSSL X.509 extension types, and the GSI trace header. It is tightly coupled to an OpenSSL-backed crypto factory named `ssl` and to grid-style certificate directory naming by issuer hash.

### Risks and edge cases
This is an environment-sensitive integration test rather than a deterministic unit test. It assumes valid local credentials, readable private keys, CA files named by issuer hash, CRL distribution information, and network or local CRL availability depending on the crypto factory. The CA array is fixed at five entries. Some failure paths print FAILED and continue, while others exit immediately, so automation should treat the process exit code and output together. Because it can recreate and write proxy files, it should be run only in controlled test environments.

### Test signals
A successful run prints PASSED markers through proxy recreation, chain reorder/verify, GSI chain verify/copy, certificate verification, request creation/signing, proxy chain save, and CRL checks. Valuable negative tests include missing user cert/key/proxy, absent CA issuer file, invalid proxy chain, unavailable `ssl` factory, and CA chain verification failure. The file itself is also a smoke test for the XRootD crypto plugin API used by `xrdgsiproxy`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsitest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSeckrb5/CMakeLists.txt -->
## sources/distributed-fs/xrootd/src/XrdSeckrb5/CMakeLists.txt

### Purpose
This CMake file builds and installs the Kerberos 5 security protocol plugin for XRootD. It is intentionally small and gates all work on the top-level `BUILD_KRB5` option.

### Important APIs, types, and functions
The build target is named `XrdSeckrb5-${PLUGIN_VERSION}` and is created as a `MODULE` library from `XrdSecProtocolkrb5.cc`. It links privately against `XrdUtils` and `${KERBEROS5_LIBRARIES}`, includes `${KERBEROS5_INCLUDE_DIR}`, and installs the resulting module library into `${CMAKE_INSTALL_LIBDIR}`.

### Control flow
Configuration returns immediately when `BUILD_KRB5` is false. Otherwise it defines the versioned plugin target, adds the module, configures link libraries and include directories, and installs it.

### State and persistence behavior
No runtime state is managed here. The only persistent effect is the generated plugin artifact in the build tree and its installation into the library directory.

### Dependencies and integration points
This file relies on top-level discovery of Kerberos include and library variables and on a project-wide `PLUGIN_VERSION`. The plugin target is expected to be dynamically loaded through XRootD's security plugin mechanism, where the exported C symbols in `XrdSecProtocolkrb5.cc` are discovered.

### Risks and edge cases
If Kerberos variables are unset or inconsistent while `BUILD_KRB5` is true, compilation or linking fails at this target. Unlike the password plugin CMake file, this file does not add an explicit dependency on a global `plugins` target, so packaging logic must not assume that dependency is present unless defined elsewhere. The module name includes the plugin version, so loader configuration must match the installed naming convention.

### Test signals
Build tests should verify both `BUILD_KRB5=OFF`, where the directory is skipped, and `BUILD_KRB5=ON`, where the module compiles and links with the platform Kerberos library. Install/package tests should confirm that `XrdSeckrb5-${PLUGIN_VERSION}` lands in the expected library directory and can be loaded by XRootD.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSeckrb5/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSeckrb5/XrdSecProtocolkrb5.cc -->
## sources/distributed-fs/xrootd/src/XrdSeckrb5/XrdSecProtocolkrb5.cc

### Purpose
`XrdSecProtocolkrb5.cc` implements the Kerberos 5 XRootD security protocol plugin. It supports client-side AP-REQ credential generation, server-side AP-REQ validation against a service principal and keytab, optional IP address checking, and optional forwarding/export of delegated Kerberos credentials into a server-side credential cache file.

### Important APIs, types, and functions
The central class is `XrdSecProtocolkrb5 : public XrdSecProtocol`. Public protocol methods are `getCredentials()` for clients and `Authenticate()` for servers. Static initialization and configuration are handled by `Init()`, `setOpts()`, `setClientOpts()`, `setParms()`, and `setExpFile()`. Private helpers include `Fatal()`, `get_krbCreds()`, `get_krbFwdCreds()`, `exp_krbTkn()`, and `SetAddr()`.

The required plugin exports are `XrdSecProtocolkrb5Init()` and `XrdSecProtocolkrb5Object()`, plus `XrdVERSIONINFO(XrdSecProtocolkrb5Object,seckrb5)`. The protocol identifier embedded in credential buffers is `"krb5"`.

### Control flow
On server initialization, `XrdSecProtocolkrb5Init('s', parms, erp)` parses optional keytab path, `-ipchk`, `-exptkn[:template]`, and the service principal. `<host>` in the principal is expanded to the local hostname. `Init()` creates a Kerberos context, opens the default credential cache and keytab, checks that the keytab can be read, parses the service principal, and returns parameters containing the principal plus `,fwd` when forwarding is requested.

On client initialization, the init function sets debug and `kinit` retry options from environment variables and defers most context/cache setup to `getCredentials()`. `XrdSecProtocolkrb5Object()` creates per-connection protocol objects. Clients take the target principal from server parameters; servers use the already initialized static context.

Client `getCredentials()` locates a credential cache from `xrd.k5ccname`, `KRB5CCNAME`, or `/tmp/krb5cc_<euid>`, initializes a client context, opens the cache, strips a `,fwd` suffix from the service when present, obtains service credentials, optionally runs `kinit` or `kinit -f` when configured and interactive, creates an auth context, and serializes a Kerberos request after the `"krb5"` prefix. If the handshake has already advanced and forwarding is enabled, it calls `get_krbFwdCreds()` and returns the forwarded credential blob.

Server `Authenticate()` validates the prefix, handles the second-step forwarded credential by calling `exp_krbTkn()`, and otherwise reads the AP-REQ using `krb5_rd_req()`. Unless `XrdSecNOIPCHK` is set, it binds the auth context to the peer address. Successful authentication maps the Kerberos principal to a local name with `krb5_aname_to_localname()` and stores it in `Entity.name`. If forwarding is enabled, it returns `kpST_more` semantics by setting `*parms` to a fake `fwdtgt` parameter buffer and expecting a second credential packet.

### State and persistence behavior
Static state includes server and client Kerberos contexts, credential caches, the keytab, parsed server principal, exported parameter string, option flags, and the forwarding export filename template. Per-object state includes endpoint address, service principal, step counter, auth contexts, ticket, credentials, and the mapped client name.

Persistent side effects occur only when delegated credentials are exported. `exp_krbTkn()` expands `<user>` and `<uid>` in the `ExpFile` template, reads forwarded credentials with `krb5_rd_cred()`, resolves and initializes a credential cache at that path, stores the credential, closes the cache, and chmods the file to `0600`.

### Dependencies and integration points
The plugin depends on MIT/Heimdal Kerberos APIs, com_err, XRootD network endpoint abstractions, `XrdOucErrInfo`, `XrdOucTokenizer`, `XrdSysMutex`, `XrdSysPwd`, and the `XrdSecInterface` plugin ABI. It integrates with XRootD by exporting protocol init/object constructors that the security loader calls.

### Risks and edge cases
The Kerberos contexts and caches are static and protected by broad mutexes, which reduces concurrency risk but serializes credential operations. `exp_krbTkn()` has several early returns while holding `krbContext.Lock()`, so errors in that path can leave the mutex locked. The `<uid>` expansion path uses `memmove(puid+ln, pusr+5, lm)` where `pusr` may be null or unrelated to the `<uid>` placeholder, which is a suspicious buffer manipulation bug. `Parms` is static but freed in each object's `Delete()`, so multiple objects can race or double-free shared parameters. Invoking `system("kinit")` from the client path depends on an interactive terminal and external command availability. IP checking defaults to disabled in init options unless `-ipchk` is supplied.

### Test signals
Coverage should include plugin initialization with valid and invalid principals/keytabs, client credential generation from `KRB5CCNAME` and `xrd.k5ccname`, AP-REQ validation success and failure, local-name mapping failures, `-ipchk` address mismatch, forwarding requested by `-exptkn`, exported cache permissions, and non-interactive behavior when no valid ticket exists. Static analysis should flag the forwarding export error-unlock paths and the `<uid>` template buffer code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSeckrb5/XrdSecProtocolkrb5.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecpwd/CMakeLists.txt -->
## sources/distributed-fs/xrootd/src/XrdSecpwd/CMakeLists.txt

### Purpose
This CMake file builds the password-based XRootD security protocol plugin and, for full builds, the `xrdpwdadmin` administrative tool.

### Important APIs, types, and functions
The module target is `XrdSecpwd-${PLUGIN_VERSION}` and is built from `XrdSecProtocolpwd.cc`, `XrdSecProtocolpwd.hh`, and `XrdSecpwdPlatform.hh`. It links privately against `XrdCrypto`, `XrdUtils`, and `${CRYPT_LIBRARY}`. The target is added as a dependency of the aggregate `plugins` target and installed to `${CMAKE_INSTALL_LIBDIR}`.

When `XRDCL_LIB_ONLY` is false, the file also builds `xrdpwdadmin` from `XrdSecpwdSrvAdmin.cc`, links it with `XrdCrypto` and `XrdUtils`, and installs it to `${CMAKE_INSTALL_BINDIR}`.

### Control flow
Configuration always defines and installs the password plugin. The admin executable is conditional on building more than the client library subset.

### State and persistence behavior
No runtime state is managed here. Build outputs are the versioned plugin module and optionally the admin executable.

### Dependencies and integration points
The plugin depends on the XRootD crypto library because the password protocol performs key agreement and hashing. `${CRYPT_LIBRARY}` supplies platform `crypt()` support when available. `xrdpwdadmin` is the operational companion for creating or managing the password files consumed by the plugin.

### Risks and edge cases
The source header is listed as part of the module source set, which is harmless for IDE visibility but does not affect compilation behavior. If `${CRYPT_LIBRARY}` is empty on a platform where crypt-style passwords are enabled, link or runtime support may be incomplete. `XRDCL_LIB_ONLY` skips the admin tool, so deployments that need server-side password administration must ensure they are not using a client-only build.

### Test signals
Build tests should verify plugin compilation with and without a separate crypt library, installation of `XrdSecpwd-${PLUGIN_VERSION}`, and conditional presence of `xrdpwdadmin`. Runtime smoke tests should verify that the module can be dynamically loaded by XRootD and that `xrdpwdadmin` is available in non-client-only packages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecpwd/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecpwd/XrdSecProtocolpwd.cc -->
## sources/distributed-fs/xrootd/src/XrdSecpwd/XrdSecProtocolpwd.cc

### Purpose
`XrdSecProtocolpwd.cc` implements the password-based XRootD security protocol plugin. It provides an encrypted multi-step handshake between client and server, optional server and client public-key verification, password checking against XRootD password files, per-user password files, system `crypt()` or shadow password hashes, autologin caches, auto-registration, password change flows, and optional server-side export of accepted credentials.

### Important APIs, types, and functions
The implementation backs the `XrdSecProtocolpwd` class declared in `XrdSecProtocolpwd.hh`. Core protocol methods are `getCredentials()` and `Authenticate()`. Static setup is in `XrdSecProtocolpwd::Init()`, invoked by the exported `XrdSecProtocolpwdInit()`. Object construction is exported through `XrdSecProtocolpwdObject()`, and plugin metadata is declared with `XrdVERSIONINFO`.

Important helpers include `ParseCrypto()`, `ParseClientInput()`, `ParseServerInput()`, `AddSerialized()`, `QueryCreds()`, `QueryUser()`, `CheckCreds()`, `SaveCreds()`, `ExportCreds()`, `UpdateAlog()`, `GetUserHost()`, `DoubleHash()`, `QueryCrypt()`, `QueryNetRc()`, `CheckTimeStamp()`, and `CheckRtag()`. The code uses `XrdSutBuffer` and `XrdSutBucket` for protocol messages and `XrdSutPFile`/`XrdSutPFCache` for persisted credential entries.

### Control flow
Initialization splits by mode. Client init reads environment variables such as `XrdSecDEBUG`, `XrdSecPWDVERIFYSRV`, `XrdSecPWDSRVPUK`, `XrdSecPWDAUTOLOG`, `XrdSecPWDALOGFILE`, and `XrdSecPWDMAXPROMPT`, then initializes the server-public-key file and optional autologin cache. Server init parses parameters such as `-upwd`, `-a`, `-vc`, `-dir`, `-udir`, `-c`, `-d`, `-syspwd`, `-lf`, `-maxfail`, `-cryptfile`, `-keepcreds`, `-expcreds`, and `-expfmt`. It loads admin files, server identity/email entries, password caches, crypto factories, and reference ciphers. The server returns parameter text containing version, server id, crypto module list, and priority options.

Client `getCredentials()` receives server parameters or continuation parameters, parses the selected crypto module and main buffer, checks any previous random challenge, and switches on the server step. It may send its public key, request server verification, add username and credentials, respond to credential requests, acknowledge failures, or sign random tags. Credentials come from `XrdSecCREDS`, the autologin PFile, `XrdSecNETRC`, cached prompt results, or interactive password prompts. Normal credentials are self-hashed before transmission; crypt and AFS modes send the real password because the server must compare with external hash formats.

Server `Authenticate()` parses the client buffer, establishes or reuses the session cipher, validates signed random tags and timestamps as configured, extracts the username, and switches on the client step. It can sign server verification challenges, handle auto-registration by sending public keys, query user status, request missing credentials, verify supplied credentials, enforce max failure counts and credential lifetimes, request password changes or refreshed credentials, cache accepted credentials in memory, and export credentials to files. When more information is needed it serializes encrypted continuation parameters; on success or terminal failure it deletes handshake state.

### State and persistence behavior
Static state includes admin, user, server-public-key, autologin, and export file paths; `XrdSutPFile` handles; caches for admin/server-puk/user/autologin data; crypto factory ids and reference ciphers; and global policy flags. Per-connection state lives in `pwdHSVars`: iteration, timestamp, crypto module, user/tag, remote version, factory, handshake cipher, reference cipher, handshake id, cache entries, random-tag status, terminal availability, current/last step, system password mode, AFS cell, and deferred server parameter buffer.

Persistent files include the server admin password file, client autologin file, client known-server public-key file, optional per-user password files, optional crypt-hash files under user homes, optional `XrdSecNETRC`, and exported credentials files. `SaveCreds()` writes salted double-hashed credentials back to the admin cache and flushes it. `UpdateAlog()` flushes autologin cache updates. `ParseClientInput()` stores newly received server public keys and flushes the known-server key cache. `ExportCreds()` writes accepted credentials either as a PFile entry, hex blob, raw blob, or raw no-keyword format, depending on `-expfmt`.

### Dependencies and integration points
The file integrates with XRootD security plugin ABI, `XrdCryptoFactory` for ciphers and KDF hooks, `XrdSut` for protocol buffers, random tags, password prompts, PFile storage, path resolution, and tracing, `XrdSysPrivGuard` for temporary privilege changes, `XrdSysPwd` for account lookup, and platform `crypt()` or shadow password APIs via `XrdSecpwdPlatform.hh`. It is paired operationally with the admin tool built in the same directory.

### Risks and edge cases
The handshake is complex and highly stateful, with many paths depending on `hs->Cref`, `hs->Pent`, and previous step values. Several caches hold sensitive material in memory; only some buffers are cleared before release. `CheckCreds()` and export modes may retain raw or crypt-style passwords when `KeepCreds` or export options are enabled. `DoubleHash()` mutates buckets in place, making call order important. The protocol uses a process-wide mutex around most handshake parsing and verification, limiting concurrency. Several file writes depend on privilege switching and cache flushing; partial failures often log warnings but continue authentication success. AFS support is stubbed by `CheckCredsAFS()` returning false. Manual option parsing and fixed-size buffers deserve fuzzing, especially around long usernames, hostnames, server ids, template expansion, and serialized bucket sizes.

### Test signals
Important tests include client/server plugin initialization with default and custom files, crypto module negotiation, first-login without cached server public key, server verification challenge, client random-tag verification, timestamp-only verification, valid and invalid password checks, expired and one-time credentials, auto-registration allowed/denied modes, max-failure lockout, password change flow, autologin update and invalidation, `XrdSecCREDS` import, `XrdSecNETRC` exact and wildcard matches, system crypt/shadow checks under privilege constraints, exported credential formats, and non-interactive clients that cannot answer continuation prompts. Fuzzing serialized `XrdSutBuffer` inputs is valuable because parsing errors directly affect authentication state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecpwd/XrdSecProtocolpwd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecpwd/XrdSecProtocolpwd.hh -->
## sources/distributed-fs/xrootd/src/XrdSecpwd/XrdSecProtocolpwd.hh

### Purpose
`XrdSecProtocolpwd.hh` declares the password security protocol's public class, state containers, enums, constants, and helper method surface. It is the contract shared by the plugin implementation and build target for the password authentication module.

### Important APIs, types, and functions
The header defines protocol constants such as `XrdSecPROTOIDENT` (`"pwd"`), `XrdSecpwdVERSION`, buffer limits, option flags, and `XrdCryptoMax`. Its enums describe protocol status (`kpST_*`), auto-registration modes, autologin update modes, credential input sources, credential types, credential actions, client steps (`kXPC_*`), server steps (`kXPS_*`), and password-specific error codes.

`pwdStatus_t` is the compact status word exchanged in protocol buffers. `pwdOptions` aggregates client/server initialization settings parsed from environment or server parameters. `pwdHSVars` stores per-handshake mutable state: iteration, timestamp, crypto selection, user/tag, remote version, ciphers, cache entries, random-tag state, tty state, current/last step, system-password mode, AFS cell, and deferred parameters.

`XrdSecProtocolpwd` derives from `XrdSecProtocol` and declares `Authenticate()`, `getCredentials()`, constructor, `Delete()`, static `Init()`, `PrintTimeStat()`, and `EnableTracing()`. Private methods cover parsing, errors, credential querying/checking, timestamp/random-tag validation, saving/exporting, serialization, and hashing.

### Control flow
The header encodes the state-machine vocabulary used by the implementation. Client steps start with normal packets, server verification requests, signed random tags, credential packets, auto-registration, and failure acknowledgement. Server steps include initial parameters, credential requests, random-tag challenges, signed random-tag replies, new public keys, public keys after auto-registration, and failure. The implementation switches on these values in `getCredentials()` and `Authenticate()`.

### State and persistence behavior
The class declares extensive static state for persistent file names, PFile handles, caches, crypto factory slots, reference ciphers, runtime policy flags, and trace objects. Per-instance state includes endpoint address, options, client name, mode flag, handshake variables, and optionally retained client credentials. The header makes clear that persistence is mediated through `XrdSutPFile` and `XrdSutPFCache` rather than plain text structures.

### Dependencies and integration points
The header depends on XRootD network, error, threading, tokenizer, security interface, password tracing, SUT PFile/buffer/random helpers, and crypto factory/cipher APIs. Any source including it receives the protocol ABI and storage model needed by `XrdSecProtocolpwd.cc`.

### Risks and edge cases
Several constants enforce small legacy limits, including `kMAXUSRLEN` and `kMAXPWDLEN`, while implementation paths may handle longer values through dynamic strings and fixed arrays. `pwdStatus_t` is packed manually into an integer in the implementation, so field size and byte-order assumptions matter. The destructor for `pwdHSVars` deletes only selected pointers; other pointers are borrowed from static caches or factories and require disciplined ownership. The protocol class has many static mutable members, so initialization order and client/server mode separation are critical.

### Test signals
Compile coverage should ensure all enum values and method declarations match the implementation. Protocol tests should assert that status words, client step values, and server step values round-trip correctly through `XrdSutBuffer` serialization. Initialization tests should verify that `pwdOptions` defaults match expected server/client behavior and that `pwdHSVars` starts with safe empty state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecpwd/XrdSecProtocolpwd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecpwd/XrdSecpwdPlatform.hh -->
## sources/distributed-fs/xrootd/src/XrdSecpwd/XrdSecpwdPlatform.hh

### Purpose
`XrdSecpwdPlatform.hh` isolates platform-specific declarations needed by the password protocol for `crypt()` and shadow password access. It keeps the main protocol source portable across Linux, GNU/Hurd-like, Solaris, macOS, OSF, SGI, and optional shadow-password configurations.

### Important APIs, types, and functions
The header conditionally includes `<crypt.h>` on platforms that provide it and declares `extern "C" char *crypt(const char *, const char *)` on platforms where the function may exist without that header. It always includes `<grp.h>` and includes `<shadow.h>` when `HAVE_SHADOWPW` is defined.

### Control flow
There is no runtime control flow. Preprocessor branches select the correct declarations at compile time based on platform macros and configure-time feature macros.

### State and persistence behavior
The header declares no state and performs no persistence. It enables `XrdSecProtocolpwd.cc` to call `crypt()` and, when available, `getspnam()` against system password databases.

### Dependencies and integration points
This file is included by `XrdSecProtocolpwd.cc`. Its declarations support `CheckCreds()` for crypt-style password comparison and `QueryCrypt()` for reading system shadow password hashes. It also connects the build-time `HAVE_SHADOWPW` feature check to the protocol's runtime behavior.

### Risks and edge cases
Platform detection must match the C library and compiler environment. Missing `crypt()` declarations can cause build failures or unsafe implicit declarations on older compilers. Shadow password support requires both headers and sufficient runtime privileges; the header only exposes the API, while `XrdSecProtocolpwd.cc` must still handle permission failures.

### Test signals
Build matrix coverage should include Linux/glibc with `<crypt.h>`, macOS-style explicit `crypt()` declaration, and configurations with and without `HAVE_SHADOWPW`. Runtime tests for the password protocol's crypt and shadow paths confirm that these declarations link correctly with `${CRYPT_LIBRARY}`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecpwd/XrdSecpwdPlatform.hh -->
