# subset-b-007965 research

Grouped research for the XRootD `XrdSecgsi` GSI protocol and companion authorization / grid-map plugin sources. Each section preserves the source path and is delimited for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecProtocolgsi.cc -->
# sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecProtocolgsi.cc

## Purpose

`XrdSecProtocolgsi.cc` implements the XRootD security protocol plugin named `gsi`. It provides the runtime half of `XrdSecProtocolgsi`: one-time protocol initialization, per-connection protocol object creation, client credential generation, server authentication, post-handshake encryption/signing helpers, X.509 CA/CRL/proxy management, grid-map and authorization plugin integration, and server certificate name validation.

The file is the security-critical implementation for the GSI handshake. It negotiates a crypto backend and symmetric session cipher, exchanges and validates X.509 certificate chains, signs Diffie-Hellman material for newer protocol peers, enforces random-tag challenge/response, optionally maps certificate DNs to local users, optionally extracts VOMS attributes, optionally runs external authorization plugins, and optionally requests or accepts delegated proxies.

## Important APIs, functions, and entry points

- `XrdSecProtocolgsi::XrdSecProtocolgsi(int opts, const char *hname, XrdNetAddrInfo &endPoint, const char *parms)`: constructs a per-connection protocol object, initializes `gsiHSVars`, records the peer host/address, applies DNS trust behavior, and stores initial client-side server parameters when in client mode.
- `XrdSecProtocolgsi::Init(gsiOptions opt, XrdOucErrInfo *erp)`: static one-time configuration. It processes CA/CRL directories, crypto factories, server certificate/key, grid-map service, GMAP/Authz/VOMS plugin loading, proxy delegation options, client proxy/cert/key defaults, DNS trust, hash compatibility, and the server parameter string returned to clients.
- `XrdSecProtocolgsiInit(char mode, const char *parms, XrdOucErrInfo *erp)`: exported C initializer for the plugin. It parses client environment variables or server `sec.protocol ... gsi` parameters into `gsiOptions`, initializes tracing, and calls `Init`.
- `XrdSecProtocolgsiObject(...)`: exported C factory used by the XRootD security framework to instantiate a protocol object.
- `getCredentials(XrdSecParameters *parm, XrdOucErrInfo *ei)`: client-side handshake state machine. It consumes server parameters or continuation messages and emits serialized `XrdSecCredentials`.
- `Authenticate(XrdSecCredentials *cred, XrdSecParameters **parms, XrdOucErrInfo *ei)`: server-side handshake state machine. It consumes client credentials and either returns `kgST_more` with continuation parameters, `kgST_ok`, or `kgST_error`.
- `Encrypt`, `Decrypt`, `Sign`, `Verify`, `getKey`, `setKey`: post-handshake data protection and key export/import methods used after a session key, RSA keys, and message digest have been established.
- `ParseClientInput`, `ClientDoInit`, `ClientDoCert`, `ClientDoPxyreq`: client handlers for server steps `kXGS_init`, `kXGS_cert`, and `kXGS_pxyreq`.
- `ParseServerInput`, `ServerDoCertreq`, `ServerDoCert`, `ServerDoSigpxy`: server handlers for client steps `kXGC_certreq`, `kXGC_cert`, and `kXGC_sigpxy`.
- `AddSerialized`: serializes a main buffer, signs any returned random tag, adds a fresh random challenge, updates the handshake cache, and optionally encrypts the serialized payload into a global bucket.
- `CheckRtag`: validates the random tag returned by the peer by using `sessionKver` to decrypt the signed tag and comparing it to the cached challenge.
- `GetCA`, `VerifyCA`, `LoadCRL`, `VerifyCRL`, `GetCApath`, `ParseCAlist`: CA and CRL discovery, verification, caching, and chain construction.
- `QueryProxy`, `InitProxy`: client/server proxy discovery, proxy creation from user cert/key, validation, export-bucket creation, and proxy cache population.
- `QueryGMAP`, `LoadGMAPFun`, `LoadAuthzFun`, `LoadVOMSFun`: dynamic plugin integration for DN mapping, authorization, and VOMS extraction.
- `GetSrvCertEnt`: server certificate/key loading and cache refresh.
- `ServerCertNameOK`: validates certificate CNs against the requested host and configured `XrdSecGSISRVNAMES`/`-srvnames` style patterns.
- `CopyEntity` and `FreeEntity`: copy/free selected `XrdSecEntity` fields for authz cache persistence.

## Control flow

Initialization starts in `XrdSecProtocolgsiInit`. Client mode reads environment variables such as `XrdSecGSICADIR`, `XrdSecGSIUSERCERT`, `XrdSecGSIUSERKEY`, `XrdSecGSIUSERPROXY`, `XrdSecGSICACHECK`, `XrdSecGSICRLCHECK`, `XrdSecGSIDELEGPROXY`, `XrdSecGSICREATEPROXY`, `XrdSecGSISRVNAMES`, `XrdSecGSIUSEDEFAULTHASH`, and `XrdSecGSITRUSTDNS`. Server mode tokenizes plugin parameters such as `-certdir`, `-crldir`, `-cert`, `-key`, `-cipher`, `-md`, `-ca`, `-crl`, `-gridmap`, `-gmapfun`, `-authzfun`, `-authzcall`, `-authzpxy`, `-vomsat`, `-vomsfun`, `-dlgpxy`, `-exppxy`, `-defaulthash`, `-trustdns`, and `-showdn`.

`Init` then establishes static protocol state. On servers it loads crypto factories from the configured list, filters cipher and message-digest lists by backend support, loads and validates server certificate/key entries into `cacheCert`, initializes grid-map handling, loads optional plugin entry points, configures delegated proxy export behavior, and returns the advertised server options string `v:<version>,c:<cryptomod>,ca:<issuer-hashes>`. On clients it resolves proxy/cert/key defaults and delegation preferences and returns an empty parameter string.

The client handshake begins in `getCredentials`. On the initial `kXGS_init` exchange, `ClientDoInit` reads the server version, selected crypto list, and server CA list, chooses a crypto factory, loads the relevant CA, and obtains a user proxy chain from `QueryProxy`. The client sends version, crypto module, issuer hash, options, and then requests the server certificate. On `kXGS_cert`, `ClientDoCert` validates the cached handshake, verifies the server certificate chain and host identity, extracts the server signing key, verifies signed DH material when supported, creates the session cipher, chooses a digest, and sends the client certificate chain. If the server asks for proxy delegation with `kXGS_pxyreq`, `ClientDoPxyreq` either forwards the private key of the local proxy or signs a server-created proxy request, depending on negotiated options.

The server handshake begins in `Authenticate`. `ServerDoCertreq` processes the initial client request: it reads client version/options, selects the crypto module, loads the CA for the client issuer hash, finds the server certificate entry, and prepares a main buffer. The `kXGC_certreq` response sends signed server DH parameters, supported cipher/digest lists, and the server certificate. `ServerDoCert` then accepts the client certificate exchange: it finalizes the cipher with client DH data, decrypts the main buffer, parses and verifies the client chain, checks the client public key consistency for signed-DH peers, creates any delegated-proxy request state, and instantiates the chosen message digest. `Authenticate` then maps the user, fills `Entity`, optionally exports DN monitoring info, runs VOMS extraction, runs authorization cache/plugin logic, optionally exports proxy material into `Entity.creds` or `Entity.endorsements`, and either succeeds or asks for one more `kXGS_pxyreq` exchange. `ServerDoSigpxy` finishes delegated proxy creation or proxy forwarding and may save the proxy in memory, `Entity.creds`, or a resolved file path.

Errors consistently route through `ErrF`, `ErrC`, and `ErrS`, which populate `XrdOucErrInfo` and release temporary buffers. Successful handshakes delete `hs`; failed paths return null credentials or `kgST_error`.

## State and persistence behavior

The file relies on extensive static process-wide state: CA/CRL directories, server/user certificate paths, proxy defaults, crypto factory arrays, grid-map/authz/VOMS plugin function pointers, tracing handles, DNS trust flags, and caches. Main caches include `cacheCA` for CA chains and CRLs, `cacheCert` for server certificates, `cachePxy` for client proxies, `cacheGMAPFun` for plugin DN mapping results, and `cacheAuthzFun` for authorization plugin output. Cache entries store raw pointers in `buf1`/`buf2`/`buf3`/`buf4`, status values, modification/expiry times, and are protected by `XrdSutCERef` locks.

`gsiHSVars` is per-handshake state. It holds the current step, timestamp, remote version, selected crypto module, reference cipher, certificate/proxy chains, CRL pointer, random tag cache reference, proxy delegation options, and buffered initial parameters. Its destructor releases or detaches chains and CRLs according to ownership flags.

`Entity` is per-protocol-instance XRootD identity state. The code mutates `Entity.name`, `host`, `vorg`, `role`, `grps`, `creds`, `endorsements`, `moninfo`, and entity attributes as authentication progresses. `Delete()` frees these fields, handshake state, session crypto objects, delegated proxy chains, and expected host memory before deleting `this`.

Persistent filesystem interactions include loading CA files from `CAdir`, CRLs from `CRLdir`, server/user certs and keys, grid-map files, user proxy files, optional `.crl_url` files, and delegated proxy output files. `InitProxy` may create or refresh a proxy file through the crypto backend. `ServerDoSigpxy` may write a delegated proxy chain to a resolved path with `<uid>`/identity substitutions.

## Dependencies and integration points

This implementation is tightly integrated with XRootD's security and utility layers: `XrdSecProtocol`, `XrdSecCredentials`, `XrdSecParameters`, `XrdSecEntity`, `XrdOucErrInfo`, `XrdOucTokenizer`, `XrdOucGMap`, `XrdOucPinLoader`, `XrdSutBuffer`, `XrdSutBucket`, `XrdSutCache`, `XrdSutPFEntry`, `XrdSutRndm`, `XrdCryptoFactory`, `XrdCryptoCipher`, `XrdCryptoRSA`, `XrdCryptoX509`, `XrdCryptoX509Chain`, `XrdCryptoX509Req`, `XrdCryptoX509Crl`, and tracing macros from `XrdSecgsiTrace.hh`.

Externally visible plugin integration depends on C symbols:

- `XrdSecProtocolgsiInit`
- `XrdSecProtocolgsiObject`
- GMAP plugin symbol `XrdSecgsiGMAPFun`
- Authz plugin symbols `XrdSecgsiAuthzFun`, `XrdSecgsiAuthzKey`, `XrdSecgsiAuthzInit`
- VOMS plugin symbols `XrdSecgsiVOMSFun`, `XrdSecgsiVOMSInit`

Build integration in `src/XrdSecgsi/CMakeLists.txt` compiles this file and the header/options header into the main `XrdSecgsi-${PLUGIN_VERSION}` module linked against `XrdCrypto` and `XrdUtils`.

## Risks and edge cases

- This is security-sensitive code with manual memory management. Ownership of `Entity.creds`, X.509 chains, cached pointers, and buckets varies by path; regressions can cause leaks, double frees, stale pointer use, or accidental failure to free credentials.
- The protocol has backward compatibility branches for old peers that do not sign DH material. In those paths it disables proxy delegation, but cipher/session negotiation still has legacy complexity and should be tested carefully.
- Hostname verification intentionally has DNS fallback when `TrustDNS` is true. Delegation is disabled if DNS fallback was used, but host identity behavior is subtle and depends on SAN presence, CN format, `expectedHost`, and configured allowed-name patterns.
- Authz cache expiration logic uses both configured timeout and end-proxy `NotAfter`; incorrect interpretation can preserve stale authorization state or force excessive plugin calls.
- `QueryProxy` can source credentials from `XrdSecCREDS`, proxy files, cert/key files, or generated proxies. Each path has different assumptions about key presence, chain length, and file permissions.
- CRL behavior is configurable from ignore to require/update. Downloading CRLs from certificate URI or `.crl_url` files affects availability and may block authentication if remote or file data is stale or malformed.
- Some parameter parsing has legacy quirks. For example, server `-ca:` first calls `getOptVal(caVerOpts, op+4)` but then assigns `atoi(op+4)`, so symbolic values like `verifyss` appear vulnerable to being overwritten as zero. That should be reviewed against expected configuration behavior.
- `ServerDoSigpxy` returns success-like local control (`0`) for several delegation failures by setting `cmsg`; callers may still complete authentication without delegated proxy material. This is intentional for optional delegation but risky if operators assume delegation is mandatory.
- The caches store raw pointers with custom lifetime management and reference stacks. Thread-safety depends on correct `XrdSutCache` locking and `GSIStack` reference counting.

## Test signals

Useful tests should include full client/server handshake success using valid CA/server/client certs, failure on missing CA, expired certificate, bad CRL, wrong host SAN/CN, unsupported crypto/cipher/digest, and random-tag mismatch. Compatibility tests should cover peers below and above `XrdSecgsiVersDHsigned` and `XrdSecgsiVersCertKey`.

Operational tests should exercise environment-driven client proxy paths, URL-supplied `xrd.gsiusrpxy`/`xrd.gsiusrcrt`/`xrd.gsiusrkey`, `XrdSecCREDS`, pure cert/key authentication, auto proxy creation, and non-tty behavior. Server tests should cover grid-map optional vs required modes, DN-hash vs DN-name fallback, GMAP plugin cache expiration, authz plugin success/failure/cache hit/cache expiry, VOMS extract vs require behavior, proxy export to `Entity.creds`/`endorsements`, delegated proxy request/signing, forwarded proxy, and file export with `<uid>` substitution.

Regression tests should explicitly verify that proxy delegation is disabled when hostname validation used DNS fallback or unsigned DH parameters, that `-ca:` symbolic values map correctly, and that `Delete()`/failed handshake paths do not leak or double-free via sanitizers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecProtocolgsi.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecProtocolgsi.hh -->
# sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecProtocolgsi.hh

## Purpose

`XrdSecProtocolgsi.hh` declares the GSI security protocol interface, constants, handshake enums, option carrier, plugin callback types, proxy helper structs, reference stack helper, `XrdSecProtocolgsi` class, and `gsiHSVars` handshake-state class. It is the shared contract used by `XrdSecProtocolgsi.cc` and any code that instantiates or interacts with the `gsi` security plugin.

## Important APIs, types, and constants

- `XrdSecPROTOIDENT`, `XrdSecPROTOIDLEN`, `XrdSecgsiVERSION`, `XrdSecNOIPCHK`, `XrdSecDEBUG`, `XrdCryptoMax`, and protocol feature version constants define protocol identity, versioning, flags, and compatibility gates.
- `kgsiStatus` defines server return status: error, ok, or more data required.
- `kgsiClientSteps` and `kgsiServerSteps` define the client/server handshake step IDs. Client steps are certificate request, certificate packet, and signed proxy packet; server steps are init, certificate packet, and proxy request.
- `kgsiHandshakeOpts` defines delegation and proxy flags such as delegated proxy request, proxy forwarding, signing request acceptance, server request, save-to-file, save-as-credentials, proxy creation, and ownership cleanup.
- `kgsiErrors` enumerates protocol-specific error codes used by `ErrF`, `ErrC`, and `ErrS`.
- Plugin callback typedefs declare external dynamic plugin contracts: `XrdSecgsiGMAP_t`, `XrdSecgsiAuthz_t`, `XrdSecgsiAuthzInit_t`, `XrdSecgsiAuthzKey_t`, and aliases for VOMS extraction.
- `gsiOptions` is the initialization option bundle used by `XrdSecProtocolgsi::Init`. It holds client/server settings for crypto modules, CA/CRL paths, cert/key/proxy paths, proxy validity/depth/bits, grid-map files and functions, authorization functions, authz cache behavior, delegation behavior, VOMS extraction, monitoring information, DNS trust, hash compatibility, and DN display.
- `ProxyOut_t` and `ProxyIn_t` pass proxy chain/key/export information into and out of `QueryProxy` and `InitProxy`.
- `GSIStack<T>` wraps an `XrdOucHash<T>` plus mutex to track shared CA/CRL objects by pointer string. It adds entries with an extra count and decrements references on deletion.
- `XrdSecProtocolgsi` subclasses `XrdSecProtocol` and exposes `Authenticate`, `getCredentials`, crypto helpers, session key helpers, `Init`, `Delete`, and `EnableTracing`.
- `gsiHSVars` stores per-handshake mutable state such as selected crypto module, remote version, reference cipher, exported certificate bucket, cache entry, CA chain, CRL, proxy chain, random-tag status, last step, options, peer hash algorithm, and buffered parameters.

## Control flow represented by declarations

The header splits public framework-facing methods from private state-machine helpers. Public methods implement the XRootD security interface. Private client handlers parse server messages and generate the next client response, while private server handlers parse client messages and produce continuation data or final identity state. Auxiliary methods handle crypto parsing, CA loading, CRL loading, proxy loading, dynamic plugin loading, error reporting, random-tag checks, server certificate name validation, grid-map lookup, and entity copying.

The header also encodes lifecycle expectations. The normal C++ destructor is empty because callers are expected to invoke `Delete()`, which frees protocol-owned resources and deletes the object. `gsiHSVars` owns cleanup of temporary handshake objects and uses option flags to decide whether chains and proxies are owned by the handshake or by caches.

## State and persistence behavior

Most persistent process state is declared as static members of `XrdSecProtocolgsi`: paths, default options, crypto factories, reference ciphers, caches, grid-map service, CA/CRL stacks, plugin function pointers, trace/logger objects, and runtime flags. Per-instance state includes endpoint address, session crypto objects, delegated proxy chain, expected hostname, IV behavior, URL-specified credential paths, and the active `gsiHSVars` pointer.

The header makes clear that cache data and handshake data share objects: CA chains and CRLs may be referenced from caches and tracked by `GSIStack`, while proxy chains may be owned by `cachePxy`, the handshake, or the protocol instance depending on `kOptsDelPxy` and delegation completion.

## Dependencies and integration points

The header includes XRootD networking (`XrdNetAddrInfo`), utility (`XrdOuc*`), system synchronization (`XrdSysPthread`), security interface (`XrdSecInterface`), GSI tracing, SUT cache/buffer/random utilities, and crypto factory/X.509/CRL/chain types. It defines the binary and source-level contract for the main `secgsi` plugin module and for dynamic GMAP/Authz/VOMS modules loaded by the implementation.

## Risks and edge cases

- The class uses numerous static mutable members, so initialization order, test isolation, and repeated initialization in one process are important risks.
- Ownership flags in `gsiHSVars` (`kOptsDelChn`, `kOptsDelPxy`) are essential for avoiding deletion of cached chains; misuse can corrupt shared cache state.
- `GSIStack` tracks objects by formatted pointer string and relies on `Hash_count`; pointer reuse or mismatched add/delete calls would be hard to debug.
- The empty C++ destructor combined with `Delete()` can surprise maintainers. Deleting an `XrdSecProtocolgsi` through normal C++ deletion would skip cleanup logic.
- `gsiOptions` contains raw `char *` pointers and comments that cleanup happens in `XrdSecProtocolgsiInit`, so copy/lifetime assumptions matter during parsing.

## Test signals

Tests should compile plugin consumers against this header and verify ABI symbols through the exported C factory/init functions. Runtime tests should inspect `Delete()` cleanup rather than relying on the C++ destructor. Handshake tests should exercise all declared step transitions and option flags, especially proxy delegation flags and cleanup flags. Static-analysis or sanitizer runs should focus on raw-pointer fields in `gsiOptions`, `gsiHSVars`, caches, and `Entity`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecProtocolgsi.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsiAuthzFunDN.cc -->
# sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsiAuthzFunDN.cc

## Purpose

`XrdSecgsiAuthzFunDN.cc` implements an example or simple authorization plugin for the GSI protocol. It exports the standard authz plugin symbols expected by `XrdSecProtocolgsi::LoadAuthzFun`: `XrdSecgsiAuthzFun`, `XrdSecgsiAuthzKey`, and `XrdSecgsiAuthzInit`. Its main behavior is minimal: it sets a dummy VO value, and its cache key is derived from the subject DN of the end proxy certificate.

The filename and comments indicate DN-based authorization behavior, but the authorization function itself is effectively a placeholder that always succeeds after setting `entity.vorg`.

## Important APIs and functions

- `XrdVERSIONINFO(XrdSecgsiAuthzFun, secgsiauthz)`, `XrdVERSIONINFO(XrdSecgsiAuthzKey, secgsiauthz)`, and `XrdVERSIONINFO(XrdSecgsiAuthzInit, secgsiauthz)` publish version metadata for dynamic loading.
- `extern XrdOucTrace *gsiTrace` integrates with the main GSI tracing macros.
- Static `gCertfmt` records the credential format requested by the plugin: default `1` for PEM base64, `0` for raw chain pointer.
- `XrdSecgsiAuthzFun(XrdSecEntity &entity)` logs a dummy call, sets `entity.vorg = strdup("VO.dummy.test")`, and returns success.
- `XrdSecgsiAuthzKey(XrdSecEntity &entity, char **key)` validates inputs, reconstructs or uses the proxy chain depending on `gCertfmt`, reorders PEM-parsed chains, selects `chain->End()`, extracts its subject DN, allocates `*key` with `new char[]`, copies the DN, and returns success.
- `XrdSecgsiAuthzInit(const char *cfg)` tokenizes space-separated config and recognizes `certfmt=raw`; it returns the credential format expected by the plugin.

## Control flow

The main protocol loads the plugin, calls `XrdSecgsiAuthzInit`, then invokes `XrdSecgsiAuthzKey` to get a cache key whenever authz should run. If the returned key is not already cached, the protocol calls `XrdSecgsiAuthzFun` and then caches selected `XrdSecEntity` fields.

For PEM credentials, `XrdSecgsiAuthzKey` wraps `entity.creds` in an `XrdOucString`, creates an `XrdSutBucket`, parses it into a new `XrdCryptoX509Chain` via `XrdCryptosslX509ParseBucket`, and reorders the chain before using the final certificate. For raw credentials, it treats `entity.creds` as an existing `XrdCryptoX509Chain *`.

## State and persistence behavior

The only plugin-local persistent state is the static `gCertfmt`. The function mutates the caller-owned `XrdSecEntity` by assigning a newly allocated `vorg` string. The cache key function allocates the returned key with `new char[]`, matching the main protocol's expectation that `AuthzKey` results are freed with `delete []`.

No files are read by this plugin. PEM parsing allocates a temporary bucket and chain, but the observed implementation does not delete the PEM-mode `XrdSutBucket` and `XrdCryptoX509Chain` on the success path, which is a potential leak.

## Dependencies and integration points

The plugin depends on XRootD version metadata, GSI tracing, `XrdSecEntity`, `XrdSutBucket`, `XrdOucString`, and OpenSSL-backed X.509 parsing through `XrdCryptosslX509ParseBucket`. It integrates only through dynamic symbol lookup by `XrdSecProtocolgsi::LoadAuthzFun`.

In the local `XrdSecgsi/CMakeLists.txt`, the VO authz and DN GMAP modules are built, but this DN authz source is not listed in the visible module targets. That may mean it is legacy, optional, or built elsewhere; packaging should be checked before relying on it.

## Risks and edge cases

- `XrdSecgsiAuthzFun` overwrites `entity.vorg` without freeing an existing value, which can leak if VOMS or prior code already set it.
- The authz decision always returns success and sets a dummy VO, so this plugin should not be treated as an enforcement plugin without modification.
- In PEM mode, success path allocation for the bucket and parsed chain appears not to be released.
- Error paths after `chain->End()` may return without deleting PEM-mode temporary objects.
- Raw mode trusts that `entity.creds` is a valid `XrdCryptoX509Chain *`; using the wrong `certfmt` would reinterpret string memory as a chain pointer.
- `XrdSecgsiAuthzKey` returns `0` on success rather than the DN length; the main protocol treats negative as fatal but also stores the key pointer, so this works for fatal/nonfatal distinction but may not match the documented "return length" expectation.

## Test signals

Tests should load the plugin dynamically through `LoadAuthzFun`, verify `certfmt=raw` and default PEM return values, verify that PEM and raw chains produce the end-proxy subject DN as cache key, and verify failure on missing `key`, missing `entity.creds`, empty chain, parse failure, and empty subject. Memory-sanitizer tests should specifically cover repeated PEM-mode key extraction and repeated authz calls with pre-existing `entity.vorg`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsiAuthzFunDN.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsiAuthzFunVO.cc -->
# sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsiAuthzFunVO.cc

## Purpose

`XrdSecgsiAuthzFunVO.cc` implements a simple VO-based authorization plugin for the GSI protocol. It propagates `entity.vorg` into the local Unix-style user and/or group fields according to CGI-formatted configuration parameters, with optional VO allow-list enforcement. It exports the standard authz plugin symbols consumed by `XrdSecProtocolgsi::LoadAuthzFun`.

## Important APIs and functions

- `XrdSecgsiAuthzInit(const char *cfg)`: parses plugin parameters from a CGI-style string, sets debugging, `vo2grp`, `vo2usr`, `valido`, and CN-to-user behavior, and returns `1` to request PEM/base64 credentials.
- `XrdSecgsiAuthzFun(XrdSecEntity &entity)`: validates `entity.vorg`, optionally checks it against `valido`, formats `entity.grps` from `vo2grp`, formats `entity.name` from `vo2usr`, or derives `entity.name` from the first `/CN=` component when configured to do so. It logs entity fields under a static mutex when debug is enabled.
- `XrdSecgsiAuthzKey(XrdSecEntity &entity, char **key)`: allocates a cache key by copying `entity.creds` and returns `entity.credslen`.
- Static configuration state in the anonymous namespace: `g_certificate_format`, `g_maxvolen`, `g_valido`, `g_vo2grp`, `g_vo2usr`, `g_debug`, and `g_cn2usr`.

## Control flow

The main GSI protocol loads this module as an authz function and calls `XrdSecgsiAuthzInit` with `-authzfunparms`. The init function first copies at most 2047 bytes and truncates at the first space to guard against accidental trailing protocol parameters, then parses the string using `XrdOucEnv`.

During authentication, the main protocol sets `Entity.creds` in PEM form because the init function returns `1`, optionally after VOMS extraction has filled `entity.vorg`. `XrdSecgsiAuthzKey` uses the entire PEM credential string as the authz cache key. On a cache miss, `XrdSecgsiAuthzFun` validates and rewrites selected entity fields. A nonzero return causes the main protocol to fail authentication.

`XrdSecgsiAuthzFun` first checks that `entity.vorg` exists, is no longer than 255 bytes, and is present in `g_valido` if an allow-list is configured. It then formats group and user strings with `snprintf` into a fixed buffer. If no `vo2usr` is configured and CN-to-user derivation is enabled, it tries to extract the text after `/CN=`, replace spaces with underscores, and assign it to `entity.name`.

## State and persistence behavior

All configuration is stored in process-wide static variables. `g_vo2grp`, `g_vo2usr`, and `g_valido` are heap-duplicated during init and are never freed in this file, which is acceptable for one-time plugin initialization but relevant to repeated load/unload tests. The plugin mutates `entity.name` and `entity.grps` by freeing existing values and assigning `strdup` results. It does not read or write files.

The cache key is a full copy of `entity.creds`, so authz cache persistence in the main protocol is scoped to the exact PEM credential text. This avoids collisions across different proxies but can be large and sensitive.

## Dependencies and integration points

The plugin depends on `XrdSecEntity`, `XrdOucEnv`, `XrdOucLock`, `XrdSysMutex`, and XRootD version metadata. It integrates with the GSI protocol's authz plugin loader through `XrdSecgsiAuthzFun`, `XrdSecgsiAuthzKey`, and `XrdSecgsiAuthzInit`. The local `CMakeLists.txt` builds it as `XrdSecgsiAUTHZVO-${PLUGIN_VERSION}` and links it against `XrdUtils`.

Expected configuration examples include `debug=1`, `valido=<comma-list>`, `vo2grp=<printf-format>`, and `vo2usr=<printf-format or *>`. `vo2usr=*` preserves `entity.name` as set by the GSI module.

## Risks and edge cases

- The CN-to-user derivation block appears to use `n`, the length of `entity.vorg`, as the null-termination index after copying from the CN. That likely truncates or mis-terminates the CN-derived username when VO length differs from CN length.
- The trailing-underscore cleanup loop initializes `cP` to the end of the string but checks `*cP` while decrementing `i`, which likely does not inspect the intended trailing characters. This should be tested and possibly fixed.
- `vo2grp` and `vo2usr` are used as `snprintf` format strings controlled by configuration. They are expected to contain one `%s`, but malformed or hostile format strings can produce unexpected formatting behavior.
- `XrdSecgsiAuthzKey` allocates `entity.credslen + 1` and calls `strcpy`, assuming `entity.creds` is NUL-terminated and at least `credslen` bytes. The main protocol provides PEM strings, but defensive tests should cover null or inconsistent lengths.
- `valido` matching uses substring search on a comma-prefixed allow-list. It prefixes the candidate VO with a comma but does not append a comma, so allow-list boundary behavior should be verified for names where one VO is a prefix of another.
- Static globals are not protected during init; the module assumes one-time initialization before concurrent auth calls.

## Test signals

Tests should cover missing VO, overlong VO, allowed/disallowed VO lists, `vo2grp`, `vo2usr`, `vo2usr=*`, CN-derived usernames, names with spaces, and repeated debug logging from concurrent threads. Cache-key tests should verify that the copied key length and contents match PEM credentials. Negative tests should include null `key`, null credentials, malformed config strings, long VO values, and potentially dangerous format strings. A focused unit test should catch the suspected CN truncation/trailing-underscore bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsiAuthzFunVO.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsiGMAPFunDN.cc -->
# sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsiGMAPFunDN.cc

## Purpose

`XrdSecgsiGMAPFunDN.cc` implements a DN-to-user mapping plugin for the GSI protocol. It exports `XrdSecgsiGMAPFun`, the dynamic symbol loaded by `XrdSecProtocolgsi::LoadGMAPFun`, and maps certificate distinguished names to local user names using a simple configuration file with exact, prefix, suffix, or contains match rules.

## Important APIs, types, and functions

- `XrdVERSIONINFO(XrdSecgsiGMAPFun, secgsigmap)` publishes plugin version metadata.
- `XrdSecgsi_Match` enumerates match types: full, begins, ends, and contains.
- `XrdSecgsiMapEntry_t` stores a match value, target user, and match type.
- Static `gMappings` is an `XrdOucHash<XrdSecgsiMapEntry_t>` storing configured mappings.
- `FindMatchingCondition` is the hash apply callback used to scan non-exact mappings and stop on first match.
- `XrdSecgsiGMAPFun(const char *dn, int now)` is both initializer and mapper. `now <= 0` treats `dn` as the initialization parameter string and calls `XrdSecgsiGMAPInit`; `now > 0` treats `dn` as an actual distinguished name and returns a newly allocated mapped username or null.
- `XrdSecgsiGMAPInit(const char *parms)` parses `[cfg]|[d|dbg|debug]`, initializes plugin-local logging/tracing, resolves config path from parameters or `XRDGSIGMAPDNCF`, reads mappings, and populates `gMappings`.

## Control flow

The main protocol calls the plugin once with `now == 0` during loading. Initialization parses pipe-separated tokens; debug tokens enable `TRACE_Authen`, and the remaining token is the config file path. If no path is supplied, `XRDGSIGMAPDNCF` is used. The config file is read line by line, ignoring short lines and comments. Each valid line is parsed as `<pattern> <user>`.

Pattern syntax is compact:

- `^value` means DN begins with `value`.
- `value$` means DN ends with `value`.
- `value+` means DN contains `value`.
- Otherwise, the entry is a full-pattern match using `XrdOucString::matches`.

During authentication, `XrdSecProtocolgsi::QueryGMAP` calls this function with the end-entity DN and current timestamp. The plugin first tries `gMappings.Find(dn)`. If no exact hash key exists, it allocates a temporary match probe and applies `FindMatchingCondition` across the hash until a rule matches. On success it returns a heap-allocated `char[]` username to the main protocol, which caches it in `cacheGMAPFun`.

## State and persistence behavior

Mapping rules persist in the static `gMappings` hash for the life of the process. The plugin also creates static logger/tracer objects, with `dnTrace` allocated during initialization. It reads one config file at initialization and does not reload it by itself; any cache expiration in the main protocol re-runs mapping against the in-memory mapping table, not the file.

Returned usernames are allocated with `new char[]`; this matches the main protocol's use of `SafeDelArray` on cached GMAP plugin results. The temporary probe allocated in the non-exact path is not deleted in the visible implementation, which creates a per-lookup leak.

## Dependencies and integration points

The plugin depends on `XrdOucHash`, `XrdOucString`, `XrdOucTrace`, `XrdSysError`, `XrdSysLogger`, XRootD version metadata, and standard C file I/O. The main integration point is dynamic loading via `XrdSecProtocolgsi::LoadGMAPFun` and server configuration `-gmapfun:<plugin>` plus optional `-gmapfunparms:<cfg>|debug`.

The local `CMakeLists.txt` builds this source as `XrdSecgsiGMAPDN-${PLUGIN_VERSION}` and links it against `XrdUtils`.

## Risks and edge cases

- In the exact-match path, the code allocates `name` using `mc->val.length() + 1` and copies `mc->val`, not `mc->user`. That appears to return the pattern/DN rather than the mapped username for exact hash hits. Non-exact matches return `mc->user`.
- The non-exact lookup allocates `new XrdSecgsiMapEntry_t` and never deletes it.
- `gMappings.Add(p, ...)` keys all entries by the stripped pattern. Exact lookup only works when the DN string exactly equals a configured key; wildcard-style `matches` rules are only reached after exact lookup misses.
- Config parsing uses whitespace splitting via `sscanf`, so DN patterns containing spaces cannot be represented directly.
- Rule priority for scanned mappings depends on hash apply order, not file order. If multiple prefix/suffix/contains rules match, selected user may be order-dependent.
- Reinitialization does not clear `gMappings`, so repeated init calls can accumulate stale mappings.
- The plugin returns `(char *)-1` on init failure through `XrdSecgsiGMAPFun`, a sentinel expected by `LoadGMAPFun`; normal callers must not treat it as a username.

## Test signals

Tests should load the plugin through `LoadGMAPFun`, initialize from a temp config file, and verify exact, begins, ends, contains, and no-match behavior. A regression test should confirm whether exact matches return the configured user or the DN/pattern; the current code suggests the latter. Tests should verify `XRDGSIGMAPDNCF` fallback, debug parameter parsing, comments/blank lines, malformed lines, repeated init behavior, and memory behavior under repeated non-exact lookups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsiGMAPFunDN.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsiOpts.hh -->
# sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsiOpts.hh

## Purpose

`XrdSecgsiOpts.hh` defines the option mapping tables and parsing helpers used by `XrdSecProtocolgsi.cc` to turn textual GSI configuration values into integer flags. It is included into the implementation file and uses an anonymous namespace, making the option constants and tables internal to each translation unit that includes it.

## Important APIs, types, and constants

- `WARN(x)` writes configuration warnings to `std::cerr`.
- `OTINIT(a,b,x)` initializes an `OptsTab` with option name, default value, number of entries, and mapping array.
- `OptsMap` maps a textual option key to an integer value.
- `OptsTab` stores one option table: option name, default value, mapping count, and `OptsMap *`.
- `LIB_XRDVOMS` defines the default VOMS plugin library name `libXrdVoms.so`.
- `azCallOpts` maps `-authzcall` values: `always` and `novoms`.
- `azPxyOpts` maps `-authzpxy` values for exporting full chain or last cert into `Entity.creds` or `Entity.endorsements`.
- `caVerOpts` maps `-ca` values: `noverify`, `verifyss`, and `verify`.
- `crlOpts` maps `-crl` values: ignore, try, use, use with update, require, and require with update.
- `sDlgOpts` maps server `-dlgpxy` values: ignore or request.
- `gmoOpts` maps `-gmapopt`/GMAP behavior: no map, try map, require map, and DN-name fallback variants.
- `tdnsOpts` maps `-trustdns`/`-showdn` style booleans.
- `vomsatOpts` maps VOMS attribute handling: ignore, extract, require.
- `getOptName(OptsTab &oTab, int opval)` returns the textual name for a mapped value or `"nothing"`.
- `getOptVal(OptsTab &oTab, const char *oVal)` parses either a numeric value or exact textual key and returns the mapped value or the table default with a warning.

## Control flow

Server parameter parsing in `XrdSecProtocolgsiInit` calls `getOptVal` for options such as `-crl`, `-gmapopt`, `-authzcall`, `-dlgpxy`, `-authzpxy`, `-vomsat`, `-trustdns`, and `-showdn`. `gsiOptions::Print` calls `getOptName` to render the current settings for trace output. `XrdSecProtocolgsi::Init` also uses constants such as `caVerifyss`, `crlTry`, `dlgReqSign`, `gmoTryMap`, `vatIgnore`, and authz proxy constants to interpret the integer options.

The parser first treats strings beginning with a digit as numeric and accepts them only when equal to a mapped value. Non-numeric strings must match a mapping key exactly. Invalid values fall back to `opDflt` when that default is nonnegative and print a warning.

## State and persistence behavior

The file defines internal static constants and non-const mapping arrays/tables. There is no runtime persistence or dynamic allocation. Because the content is in an anonymous namespace in a header, every translation unit including the header gets its own internal copies. In this repository scope it is included by the main protocol implementation.

## Dependencies and integration points

This header expects standard C/C++ functions and streams used by `isdigit`, `atoi`, `strcmp`, and `std::cerr`; the including translation unit provides the relevant includes. Its constants are consumed directly by `XrdSecProtocolgsi.cc` and defaults in `XrdSecProtocolgsi.hh`'s `gsiOptions` constructor. It also defines `LIB_XRDVOMS`, used when server config says `-vomsat` without an explicit VOMS plugin.

## Risks and edge cases

- `getOptVal` dereferences `*oVal` without null or empty checks. Current callers pass substrings after recognized `-opt:` prefixes, but malformed empty values can still reach it.
- Numeric parsing accepts only values present in the mapping table. This is good for validation but means composite future values must be added to the table.
- Invalid values silently become defaults after warning. For security options such as `-ca`, `-crl`, `-gmapopt`, and `-trustdns`, fallback defaults must be reviewed to avoid surprising permissive behavior.
- The currently disabled two-table `getOptVal` overload suggests older support for comma-composed values; adding new combined options requires care.
- In the observed server parser, `-ca:` calls `getOptVal(caVerOpts, op+4)` and then immediately overwrites the result with `atoi(op+4)`, which undermines this header's symbolic parser for `-ca`. That issue is in the consumer but directly affects these tables.

## Test signals

Unit tests should cover every option table with textual values, numeric values, and invalid strings. Security-focused tests should assert defaults for invalid `-ca`, `-crl`, `-gmapopt`, `-vomsat`, `-dlgpxy`, `-authzpxy`, and `-trustdns`. Integration tests should parse realistic server parameter strings and verify that `gsiOptions` receives the expected integers, especially `-ca:verifyss` and `-ca:verify`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsiOpts.hh -->
