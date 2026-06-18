# subset-b-007937 research

This grouped report covers the requested XRootD crypto, digFS, and erasure-coding files. Each section is bounded by the exact file markers used by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslgsiAux.cc -->
## sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslgsiAux.cc

### Purpose
This file implements OpenSSL-backed GSI proxy-certificate helpers for XrdCrypto. It creates RFC 3820 proxy certificates and proxy certificate requests, signs proxy requests, extracts VOMS attributes from certificate extensions, checks ProxyCertInfo extension validity, and exposes small helpers for reading or modifying proxy path-length constraints.

### Important APIs, Types, and Functions
- `XrdCryptosslProxyCertInfo(const void *extdata, int &pathlen, bool *haspolicy)` decodes modern or legacy ProxyCertInfo extensions and returns the optional path-length constraint.
- `XrdCryptosslSetPathLenConstraint(void *extdata, int pathlen)` decodes a ProxyCertInfo extension and updates its in-memory path-length integer when one exists.
- `XrdCryptosslX509CreateProxy(...)` reads an end-entity certificate and private key from PEM files, generates a new RSA key, builds and signs a proxy certificate, pushes proxy and EEC certificates into `XrdCryptogsiX509Chain`, returns an `XrdCryptoRSA`, and optionally writes the GSI proxy PEM bundle.
- `XrdCryptosslX509CreateProxyReq(...)` creates a new proxy request from an existing proxy certificate, preserving relevant extensions and decrementing the proxy path length.
- `XrdCryptosslX509SignProxyReq(...)` validates the request subject, clamps path-depth constraints, signs the request with the issuer proxy key, and returns an `XrdCryptosslX509`.
- `XrdCryptosslX509GetVOMSAttr(...)` and recursive `XrdCryptosslX509FillVOMS(...)` scan ASN.1 extension payloads for VOMS attribute certificate strings.
- `XrdCryptosslX509CheckProxy3(...)` validates that a proxy has a usable RFC 3820 or legacy ProxyCertInfo extension with a policy language.
- OpenSSL ASN.1 macros define `PROXY_CERT_INFO_EXTENSION_OLD` decoding for legacy proxy layout. Local smart-pointer aliases wrap many OpenSSL types in the newer request-signing paths.

### Control Flow
Proxy creation starts with PEM load of the EEC certificate and private key, expiry and RSA-key checks, then RSA key generation for the proxy. The subject is copied from the issuer and extended with a random `CN=<serial>`. The file builds a critical ProxyCertInfo extension, copies issuer extensions except SubjectAltName, warns if KeyUsage is absent, signs the new certificate with the issuer key, wraps OpenSSL objects in XRootD crypto classes, and optionally writes certificate, private key, and EEC certificate to a 0600 PEM file.

Proxy request creation follows the same subject-extension pattern but emits an `X509_REQ` and uses smart pointers for most temporaries. When extending an existing proxy, it reads the current ProxyCertInfo depth and decrements it when setting the new request's constraint.

Signing a proxy request validates that the request subject is issuer-subject plus a final CN component, with compatibility for older request versions. It copies safe extensions from the issuer proxy, rejects SubjectAltName, derives output path depth from issuer and request constraints, constructs a fresh critical ProxyCertInfo extension, sets validity to the issuer's remaining lifetime, and signs with the issuer private key.

VOMS parsing is recursive ASN.1 walking. It looks for the VOMS Attribute Certificate OID and then collects printable octet strings following the matching attribute-capability OID into a comma-separated `XrdOucString`.

### State and Persistence
Persistent outputs are only produced when `XrdCryptosslX509CreateProxy` receives `fnp`; it writes a proxy bundle with restrictive permissions. Otherwise state is in OpenSSL heap objects transferred to `XrdCryptosslX509`, `XrdCryptosslX509Req`, `XrdCryptosslRSA`, or a caller-owned chain. Random serials are drawn from `XrdSutRndm::GetUInt()`. No global mutable state is maintained here beyond OpenSSL initialization side effects and trace logging.

### Dependencies and Integration Points
The file depends heavily on OpenSSL ASN.1, X509, RSA/EVP, PEM, and X509v3 APIs. It integrates with `XrdCryptosslFactory`, which returns function pointers for proxy creation, request creation, signing, proxy checking, and VOMS extraction. `XrdCryptosslX509` uses `XrdCryptosslX509CheckProxy3` to classify proxy certificates. It also uses `XrdCryptogsiX509Chain`, `XrdCryptosslRSA`, `XrdCryptosslX509Req`, `XrdOucString`, and XrdCrypto error codes.

### Risks and Edge Cases
Manual OpenSSL ownership is inconsistent: older `CreateProxy` paths have many early returns after allocations without full cleanup, while later functions use RAII more consistently. Several decoded `PROXY_CERT_INFO_EXTENSION` objects in helper paths are not freed before return. `XrdCryptosslSetPathLenConstraint` mutates the decoded object but does not re-encode it into the original `X509_EXTENSION`, so callers should verify whether changes persist. Subject parsing relies on one-line string format and `rfind("/CN=")`, which can be brittle for unusual names. Random serial generation is only a 32-bit unsigned integer. VOMS ASN.1 parsing treats printable octet strings as attribute text and may miss non-printable or differently encoded attributes. Some `X509_REQ_get_pubkey` and OpenSSL object returns may need explicit ownership review.

### Test Signals
Useful tests are proxy creation from real PEM EEC/key pairs, path-depth decrement behavior across chained proxies, rejection of SubjectAltName in proxy signing, malformed ProxyCertInfo decoding, OpenSSL 1.1 versus 3.x key generation, VOMS extension extraction with multiple attribute values, and leak/error-path checks under ASAN or valgrind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptosslgsiAux.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptotest.cc -->
## sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptotest.cc

### Purpose
This is a standalone diagnostic program for the XrdCrypto factory abstraction. It exercises message digests, symmetric ciphers, bucket encryption, key derivation, RSA generation/import/export/encryption, key-agreement cipher setup, and a small X509 load path.

### Important APIs, Types, and Functions
- `main(int argc, char **argv)` selects a crypto module, defaults to `ssl`, obtains `XrdCryptoFactory::GetCryptoFactory`, and runs all checks in sequence.
- Uses `XrdCryptoMsgDigest::Update`, `Final`, and `AsHexString` with MD5.
- Uses `XrdCryptoCipher` creation by cipher name and key-agreement forms, plus `Encrypt`, `Decrypt`, `EncOutLength`, `DecOutLength`, `Public`, and `Finalize`.
- Uses `XrdCryptoKDFun_t` from the factory and compares deterministic expected strings for local and ssl providers.
- Uses `XrdCryptoRSA` generation, copy construction through the factory, public/private export/import, public/private encryption pairs, and `XrdSutBucket` encryption helpers.

### Control Flow
The program enables verbose SUT and crypto tracing, extracts the executable basename for output, chooses a factory module, and then proceeds linearly. Each feature block creates an object, performs a known operation, compares the result to a literal expected value or round-trip result, prints success or mismatch, and continues. It exits with status 1 only when the factory cannot be loaded or key-agreement public data is unavailable; most feature failures are printed but do not change the process exit code.

### State and Persistence
State is transient and heap allocated. The program prints potentially sensitive RSA private material and cipher data to standard error/stdout for debug purposes. It contains a hard-coded X509 path `/home/ganis/.globus/usercert.pem`, so the X509 block is environment-specific and only runs for factory ID 1.

### Dependencies and Integration Points
This test links against XrdCrypto interfaces and XrdSut helpers. It is useful as a manual smoke test for the factory module selected at runtime, especially `ssl` and `local`. It is not a formal unit test harness and does not appear to be integrated into CTest from this file alone.

### Risks and Edge Cases
The program uses fixed-size stack buffers and `strcpy` for command-line inputs, so long module names or executable names can overflow. It uses weak legacy primitives such as MD5 and 1024-bit RSA for testing. Several allocated objects are not deleted on all branches. It prints private keys, making it unsuitable for normal logs. Because many failures only print messages, automation cannot rely on exit status to determine pass/fail.

### Test Signals
The expected MD5 digest for `"prova"`, KDF outputs for local/ssl, symmetric cipher round trips, RSA import/export and encryption round trips, bucket equality checks, and key-agreement cipher equality are the observable pass signals. A stronger modern test would convert these into assertions with deterministic exit status and avoid printing secrets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCrypto/XrdCryptotest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdDig/CMakeLists.txt -->
## sources/distributed-fs/xrootd/src/XrdDig/CMakeLists.txt

### Purpose
This build fragment adds the built-in dig file system implementation to the `XrdServer` target.

### Important APIs, Types, and Functions
It contributes `XrdDigAuth.cc/.hh`, `XrdDigConfig.cc/.hh`, and `XrdDigFS.cc/.hh` as private sources. There are no exported CMake options in this file.

### Control Flow
When the parent `src/CMakeLists.txt` adds the `XrdDig` subdirectory, this file unconditionally appends the dig sources to `XrdServer`.

### State and Persistence
No runtime state is handled here. Build state is limited to target source membership.

### Dependencies and Integration Points
The digFS code is compiled directly into `XrdServer`; runtime integration happens through `XrdDigGetFS` and xrootd configuration code in `XrdXrootdConfig.cc`.

### Risks and Edge Cases
Because this is private target source inclusion rather than a separate library, source-level dependencies and platform guards must be correct in the `.cc` files. Build failures in digFS affect the server target.

### Test Signals
Successful configuration and compilation of `XrdServer` with the XrdDig sources is the primary signal. Runtime coverage comes from xrootd configuration tests that enable the digFS path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdDig/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdDig/XrdDigAuth.cc -->
## sources/distributed-fs/xrootd/src/XrdDig/XrdDigAuth.cc

### Purpose
This file implements authorization for digFS administrative information exposure. It reads a dig authorization file, builds an in-memory ACL list, refreshes it when the file changes, and authorizes clients against protocol, name, host, virtual organization, role, and group fields.

### Important APIs, Types, and Functions
- `XrdDig::Auth` is the global `XrdDigAuth` instance used by configuration and filesystem code.
- `XrdDigAuth::Configure(const char *aFN)` stores the auth-file path and performs initial setup.
- `XrdDigAuth::Authorize(const XrdSecEntity *client, XrdDigAuthEnt::aType aType, bool aVec[])` refreshes when needed, matches the client against ACL records, and returns either a specific access decision or fills the access vector.
- `Parse(XrdOucStream&, int)` parses a single auth file line into `XrdDigAuthEnt`.
- `Refresh()` deletes and rebuilds the ACL list under the auth mutex.
- `SetupAuth(...)` opens, stats, reads, and validates the file, then logs initialization or refresh status.
- `OkGrp` matches a group token inside a space-separated group list; `Squash` converts `\s` escapes to spaces.

### Control Flow
Authorization takes the mutex, checks whether the next scheduled `authCHK` refresh time has passed, stats the auth file, and refreshes if missing, changed, or previously present but removed. It resets the caller's access vector when supplied, checks global resource availability through the summary `accOK` mask, and then scans ACL records. A record matches only when protocol matches and all specified entity predicates match. A matched record returns the requested access bit or copies all bits into `aVec`.

Parsing first consumes access tokens such as `all`, `conf`, `core`, `logs`, `proc`, and negated forms like `-logs`, then expects an auth protocol. Entity selectors are encoded by first character using `"nhorg"` for name, host, VO, role, and group. Values are packed into one allocated `rec` buffer and `eChk` pointers are relocated into that buffer.

### State and Persistence
Runtime state is in `authFN`, `authTOD`, `authCHK`, `authList`, and the summary `accOK` mask, protected by `authMutex`. The auth file is persistent external configuration. Missing auth files suspend access but are not necessarily fatal. Refresh scheduling uses short backoffs of 5, 30, or 60 seconds depending on stat/read state.

### Dependencies and Integration Points
The file depends on `XrdSecEntity`, `XrdNetAddrInfo`, `XrdOucStream`, `XrdSysError`, and `XrdSysE2T`. `XrdDigConfig` calls `Auth.Configure` during digFS initialization and `Auth.Authorize` when generating listings or mapping logical dig paths to real paths.

### Risks and Edge Cases
`Configure` stores `strdup(aFN)` into a `const char *` and never frees it. The ACL list is singly linked and refreshed wholesale, which is simple but can briefly make access unavailable on parse errors. `OkGrp` uses substring search with only trailing space or end checks, so a match at the middle of another group name may be possible if not preceded by a delimiter. Host comparison depends on `addrInfo->Name("")` and exact string equality. `Authorize` dereferences `client->addrInfo` when host matching without checking it. Parsing uses a fixed 4096-byte value buffer.

### Test Signals
Tests should cover valid and invalid auth lines, negated access tokens, `all`, each entity selector, escaped spaces, missing auth file behavior, refresh after file mtime change, group boundary matching, and concurrent authorization during refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdDig/XrdDigAuth.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdDig/XrdDigAuth.hh -->
## sources/distributed-fs/xrootd/src/XrdDig/XrdDigAuth.hh

### Purpose
This header declares the digFS authorization record and authorization manager.

### Important APIs, Types, and Functions
- `XrdDigAuthEnt` is one ACL record. It stores `next`, a packed `rec` allocation, `prot`, entity-check pointers, and per-resource `accOK` flags.
- `XrdDigAuthEnt::eType` indexes entity selectors: name, host, virtual organization, role, and group.
- `XrdDigAuthEnt::aType` indexes protected dig resources: `conf`, `core`, `logs`, and `proc`; `aNum` is also used as a sentinel for vector queries.
- `XrdDigAuth` exposes `Configure` and `Authorize` and keeps refresh/parsing helpers private.

### Control Flow
The public contract is intentionally small: initialize with an auth-file path, then authorize clients against a requested resource. Private helpers parse and refresh the list on demand.

### State and Persistence
`XrdDigAuth` owns a mutex, the auth-file path, mtime and next-check timestamps, a linked list of ACL records, and a summary access mask. Individual entries own one packed record buffer released in the destructor.

### Dependencies and Integration Points
The header includes `XrdSecEntity.hh` and `XrdSysPthread.hh`, making the authorization manager directly tied to XRootD security identity and mutex primitives. It is consumed by `XrdDigAuth.cc` and `XrdDigConfig.cc`.

### Risks and Edge Cases
The `XrdDigAuth` destructor does not free `authFN` or the linked `authList`; process lifetime likely owns these globals, but repeated construction in tests would leak. `memset` initialization assumes plain pointer/bool layout. The packed-buffer model requires pointer relocation to be correct after parse.

### Test Signals
Header-level tests are compile/interface tests: enum order must match token arrays in `XrdDigAuth.cc` and `XrdDigConfig.cc`, `aNum` must size all access vectors, and `XrdSecPROTOIDSIZE` must bound protocol strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdDig/XrdDigAuth.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdDig/XrdDigConfig.cc -->
## sources/distributed-fs/xrootd/src/XrdDig/XrdDigConfig.cc

### Purpose
This file configures digFS path exposure. It builds the remapping template under `XRDADMINPATH`, processes optional `dig.*` configuration directives, configures authorization, creates locate responses, validates exported roots, maps logical dig paths to real admin files, and audits allowed or denied access.

### Important APIs, Types, and Functions
- `XrdDig::Config` is the global `XrdDigConfig` instance.
- `Configure(const char *cFN, const char *parms)` parses the auth-file parameter, processes config, initializes `Auth`, sets locate responses, stats root, and validates `conf/core/logs/proc` exported roots.
- `GenAccess` returns visible top-level entries for a client based on authorization and available exported roots.
- `GenPath` validates top-level prefixes, authorizes the client, applies `/proc` safety checks, audits access, and returns a `strdup` real path generated from `fnTmplt`.
- `GetLocResp` returns hostname or IP locate responses.
- `StatRoot` copies cached root stat data.
- Private `AddPath`, `Empty`, `ValProc`, `xacf`, and `xlog` implement `dig.addconf` and `dig.log` directives.

### Control Flow
Initialization requires `XRDADMINPATH`, creates a template like `<admin>/.xrd/=/%s`, deletes stale `conf/etc` exports, tokenizes the first digFS parameter as the auth file, optionally parses a config file for `dig.addconf` and `dig.log`, and initializes authorization. It then prepares locate responses from local host/port and stats whether each protected prefix exists under the template.

Path generation maps a logical name to one of `conf`, `core`, `logs`, or `proc`, checks availability and authorization, performs extra proc traversal checks, audits if the target is a file and logging is enabled, formats the real path, and appends a slash for directory opens.

### State and Persistence
Persistent filesystem effects include symlink creation through `XrdOucUtils::ReLink` for `dig.addconf`, cleanup of stale `conf/etc`, and use of admin-path exports. Runtime state includes `fnTmplt`, locate response strings and lengths, `rootStat`, `pTab[].isOK`, and logging booleans. Authorization state lives in `XrdDigAuth`.

### Dependencies and Integration Points
This file depends on XrdOuc stream/tokenizer/env utilities, XrdNet address formatting, XrdSys logging/error conversion, `XrdDigAuth`, and POSIX filesystem calls. `XrdDigFS` calls `GenAccess`, `GenPath`, `GetLocResp`, and `StatRoot` for every user-facing operation.

### Risks and Edge Cases
`fnTmplt` and locate response strings are `strdup` allocations with process-lifetime ownership. `Configure` returns success even if `ConfigProc` cannot open the config file due to `return 1`, which may be intentional but is suspicious. `GenAccess` iterates `sizeof(aOK)-1`, relying on `bool` size and enum count. `ValProc` tries to prevent symlink traversal under proc but accepts shallow proc paths and only checks components after a certain depth. `AddPath` opens source paths read-only and may reject directories that need execute-only traversal. The locate response construction depends on environment `XRDPORT`.

### Test Signals
Tests should cover missing/long `XRDADMINPATH`, no parameters, auth file failures, `dig.addconf` target name derivation, rejection of target names containing `/`, `dig.log` combinations, top-level listing by authorization, denied audit logging, locate response for hostname/IPv4/IPv6, and proc symlink escape prevention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdDig/XrdDigConfig.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdDig/XrdDigConfig.hh -->
## sources/distributed-fs/xrootd/src/XrdDig/XrdDigConfig.hh

### Purpose
This header declares the configuration and path-mapping service for digFS.

### Important APIs, Types, and Functions
- `Configure` initializes digFS from a config file and parameter string.
- `pType` classifies expected logical path type as any, directory, or file.
- `GenAccess` fills a top-level access list for a client.
- `GenPath` maps a logical dig path and operation name to a real filesystem path and errno-style result.
- `GetLocResp` and `StatRoot` support locate and stat operations.
- Private helpers implement config parsing, audit logging, path export, proc validation, and directives.

### Control Flow
Consumers call `Configure` once, then call `GenAccess` for root directory listing or `GenPath` for concrete operations. Private parser methods are invoked only during configuration.

### State and Persistence
The class stores path-template and locate-response heap strings, response lengths, and grant/deny logging flags. It has no explicit destructor cleanup, consistent with global process-lifetime use.

### Dependencies and Integration Points
Forward declarations reduce header coupling to XrdOuc, XrdSec, and POSIX `stat`. `XrdDigFS.cc` consumes the public methods and `XrdDigConfig.cc` implements the private configuration grammar.

### Risks and Edge Cases
The public `GenPath` returns a `char *` that callers must `free`. The class is not obviously thread-safe internally; safety depends on configuration being immutable after startup and authorization using its own mutex. `locRlen*` are `short`, so response lengths assume small locate strings.

### Test Signals
Compile tests should ensure the `pType` enum remains aligned with `GenPath` logic. Runtime tests should assert `GenPath` ownership and error codes for unauthorized, invalid-prefix, too-long, file, and directory paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdDig/XrdDigConfig.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdDig/XrdDigFS.cc -->
## sources/distributed-fs/xrootd/src/XrdDig/XrdDigFS.cc

### Purpose
This file implements the read-only digFS `XrdSfsFileSystem`, directory, and file objects. It exposes selected server administrative files through XRootD's SFS interface, with authorization and path mapping delegated to `XrdDigConfig`.

### Important APIs, Types, and Functions
- `XrdDigGetFS(...)` is the plugin entry point used by xrootd configuration to initialize and return a singleton `XrdDigFS`.
- `XrdDigDirectory::open`, `nextEntry`, and `close` implement authorized directory listing, including synthesized root entries and Linux `/proc` symlink tagging.
- `XrdDigFile::open`, `read`, `readv`, AIO read wrapper, `stat`, `fctl`, and `close` implement read-only file access.
- `XrdDigFS::exists`, `fsctl`, `stat`, `getVersion`, `Validate`, `Reject`, and `Emsg` provide filesystem-level operations and common error formatting.
- `XrdDigUFS` wraps POSIX `open`, `close`, `stat`, `lstat`, and `fstat` for easier replacement or isolation.

### Control Flow
`XrdDigGetFS` sets the global error route, configures the global `Config`, and returns a static filesystem on success. Directory opens either synthesize the dig root listing through `Config.GenAccess` or validate/map/open a real directory. `nextEntry` loops over directory entries, optionally autostats them, normalizes modes to read-only, and, for Linux proc paths, appends `" -> target"` text for symlinks unless listing the proc root.

File open rejects write/create modes, validates and maps the path, applies Linux `/proc` restrictions by requiring a regular non-`/mem` target, opens read-only, and verifies the descriptor is a regular file. Reads use `pread`; `readv` loops over individual `pread` calls and treats short reads as an error. Filesystem-level stat handles the dig root specially and otherwise delegates to `Config.GenPath` then POSIX `stat`.

### State and Persistence
The filesystem is read-only; mutation methods return `EROFS`. Runtime state lives in each directory/file object: open DIR/file descriptor, allocated real filename, proc/base flags, autostat buffer pointer, and EOF state. Global state is `eDest` and `Config`. No persistent state is written by this file.

### Dependencies and Integration Points
The file depends on XrdSfs interfaces, XrdSec identity, XrdSys logging, XrdVersion, XrdOuc error info, and POSIX filesystem APIs. Xrootd's config path calls `XrdDigGetFS`; SFS calls allocate `XrdDigDirectory` and `XrdDigFile` via `newDir`/`newFile`.

### Risks and Edge Cases
`exists` appears to call `Statfn(path, ...)` on the supplied logical path rather than a mapped real path, unlike `stat` and `open`; this may be intentional for local-prefixed paths but is worth testing. In `getMmap`, `if (Addr) Addr = 0` does not clear `*Addr`. `XrdDigFile::open` stores negative errno values in `oh` and then passes them through `Emsg`, which normalizes sign. Directory symlink tagging writes into `dirent` name storage and depends on buffer layout. `readv` treats any short read as `ESPIPE`, which may be harsh near EOF. Proc validation and `/mem` substring blocking need security regression coverage.

### Test Signals
Expected tests include successful plugin initialization, denied startup on config failure, root listing filtered by auth, read-only rejection for all mutating operations, stat/open/read/readv success for exported files, locate `fsctl`, `/proc` symlink display and open rejection, logical path validation, and error-info contents for common failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdDig/XrdDigFS.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdDig/XrdDigFS.hh -->
## sources/distributed-fs/xrootd/src/XrdDig/XrdDigFS.hh

### Purpose
This header declares the digFS directory, file, and filesystem classes implementing XRootD's SFS interface.

### Important APIs, Types, and Functions
- `XrdDigDirectory` derives from `XrdSfsDirectory` and exposes `open`, `nextEntry`, `close`, `FName`, and `autoStat`.
- `XrdDigFile` derives from `XrdSfsFile` and exposes read-only `open`, `close`, `fctl`, `read`, `readv`, AIO read, `stat`, and no-op/rejected write-style operations.
- `XrdDigFS` derives from `XrdSfsFileSystem`, allocates directory/file objects, rejects mutating methods, implements `exists`, `fsctl`, `stat`, `getVersion`, and common `Emsg`/`Validate`.

### Control Flow
The SFS server obtains an `XrdDigFS`, then calls `newDir` or `newFile` to handle individual operations. Most mutators inline-call `Reject`, making the filesystem explicitly read-only at the interface level.

### State and Persistence
Directory objects keep `DIR *`, a mapped filename, optional autostat buffer, directory fd, EOF/base/proc flags, and a fixed union buffer for directory entries or synthesized root entries. File objects keep an fd, mapped filename, and proc flag. Filesystem objects are stateless.

### Dependencies and Integration Points
The header includes `XrdSfsInterface.hh`, POSIX `dirent`/types, and is implemented by `XrdDigFS.cc`. It is part of `XrdServer` through `XrdDig/CMakeLists.txt`.

### Risks and Edge Cases
The fixed `dirent_full` storage needs to be large enough for directory names plus proc symlink tags on all supported platforms. The inline no-op writes return `SFS_OK`, while filesystem-level mutators reject; callers must not interpret file write support from these methods. Destructor cleanup calls virtual-like `close` methods during destruction but the methods are local concrete implementations.

### Test Signals
Compile and ABI tests should confirm SFS signature compatibility. Runtime tests should cover object lifecycle, repeated open protection, destructor cleanup of open handles, autostat behavior, and read-only method behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdDig/XrdDigFS.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/CMakeLists.txt -->
## sources/distributed-fs/xrootd/src/XrdEc/CMakeLists.txt

### Purpose
This build file defines the optional `XrdEc` shared library for erasure-coded client-side storage support.

### Important APIs, Types, and Functions
When `BUILD_XRDEC` is enabled, it builds `XrdEc` from configuration, object-layout, reader, redundancy provider, streaming writer, thread-pool, utility, and write-buffer sources. It links `XrdCl`, `XrdUtils`, and `${ISAL_LIBRARIES}`, and includes `${ISAL_INCLUDE_DIRS}`.

### Control Flow
The first guard returns immediately if `BUILD_XRDEC` is false. Otherwise the library target is created, linked, versioned, and installed together with its private headers.

### State and Persistence
Build state includes the shared-library target and installed private headers under `${CMAKE_INSTALL_INCLUDEDIR}/xrootd/private/XrdEc`. Runtime state is handled by the compiled sources.

### Dependencies and Integration Points
The library depends on ISA-L for erasure coding and CRC helpers, plus XrdCl/XrdUtils. XrdCl includes EC handler code that constructs `XrdEc::Reader`, `StrmWriter`, and `ObjCfg`.

### Risks and Edge Cases
If ISA-L include or library variables are misconfigured, the target will fail to build or link. Headers are installed under a private include path, indicating consumers should be internal XRootD components rather than stable public API users.

### Test Signals
`BUILD_XRDEC=ON` builds and installs `libXrdEc` with the expected SONAME/version. Link-time checks should confirm ISA-L symbols and XrdCl/XrdUtils dependencies resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/XrdEcConfig.hh -->
## sources/distributed-fs/xrootd/src/XrdEc/XrdEcConfig.hh

### Purpose
This header defines the singleton module configuration for XrdEc. It mainly caches `RedundancyProvider` instances keyed by erasure-code layout and controls whether XrdCl plugin support is enabled inside EC-created files/archives.

### Important APIs, Types, and Functions
- `Config::Instance()` returns a process-local singleton.
- `GetRedundancy(const ObjCfg &objcfg)` returns a cached `RedundancyProvider` for `nbchunks`, `nbparity`, and `datasize`.
- `enable_plugins` is a public boolean used when constructing `XrdCl::ZipArchive` or `XrdCl::File`.

### Control Flow
`GetRedundancy` builds a string key from object layout values, locks `mtx`, looks up an existing provider, and constructs one in-place if absent.

### State and Persistence
State is process-local: an unordered map of redundancy providers and a mutex. There is no persistence across processes. The singleton defaults `enable_plugins` to true, while `XrdClEcHandler` can disable it to avoid recursive plugin use.

### Dependencies and Integration Points
The header includes `XrdEcRedundancyProvider.hh` and `XrdEcObjCfg.hh`. Reader recovery and write-buffer encoding paths use `Config::Instance().GetRedundancy`.

### Risks and Edge Cases
The cache key omits `chunksize`, `nbdata`, and digest choice directly; `datasize` plus `nbchunks` and `nbparity` implies `nbdata` and chunk size for valid configurations, but only if object configs are internally consistent. The returned reference remains valid because unordered-map nodes are stable for references across rehash, but lifecycle is singleton-global. Public mutable `enable_plugins` is not synchronized.

### Test Signals
Tests should verify that identical layouts reuse a provider, different layouts create distinct providers, and plugin toggling affects newly created XrdCl archive/file objects without causing recursive EC plugin loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/XrdEcConfig.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/XrdEcObjCfg.hh -->
## sources/distributed-fs/xrootd/src/XrdEc/XrdEcObjCfg.hh

### Purpose
This header defines `XrdEc::ObjCfg`, the immutable layout and placement description for one erasure-coded object, plus the selected checksum implementation.

### Important APIs, Types, and Functions
- `isal_crc32` wraps ISA-L `crc32_gzip_refl`.
- `ObjCfg` constructor accepts object id/path, data stripe count, parity count, chunk size, checksum selection, and optional no-metadata-file mode.
- Derived constants include `nbchunks`, `datasize`, `paritysize`, and `blksize`.
- `GetDataUrl(i)` and `GetMetadataUrl(i)` build placement URLs with optional CGI strings.
- `GetFileName(blknb, strpnb)` names zip entries as `obj.<block>.<stripe>`.
- `digest` points to either XRootD crc32c or ISA-L crc32.

### Control Flow
`ObjCfg` is constructed by the EC handler after URL parameters are parsed. Placements and CGI vectors are filled afterward by the caller. Reader and writer code use the object to map logical offsets to block/stripe file names and remote data/metadata URLs.

### State and Persistence
Most layout fields are `const`, while placement vectors and CGI vectors are mutable configuration populated after construction. It does not own remote state, but its naming scheme determines the persistent zip-entry names and metadata object names.

### Dependencies and Integration Points
Depends on XrdOuc CRC32C and ISA-L CRC APIs. Used by `Reader`, `StrmWriter`, `WrtBuff`, `RedundancyProvider`, `Config`, and XrdCl EC handler code.

### Risks and Edge Cases
`nbdata + nbparity` is stored as `uint8_t`; invalid large counts can wrap if not validated before construction. URL getters assume placement and CGI vectors contain an entry for index `i`. `blksize` comment says MB but value is bytes. `digest` is a raw function pointer and must be valid for object lifetime.

### Test Signals
Tests should cover layout arithmetic, URL generation with and without CGI, metadata URL suffixing, file-name format, digest selection, and invalid placement-index behavior at the EC handler validation layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/XrdEcObjCfg.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/XrdEcReader.cc -->
## sources/distributed-fs/xrootd/src/XrdEc/XrdEcReader.cc

### Purpose
This file implements asynchronous reads from XrdEc striped/erasure-coded objects. It opens data archives, reads metadata or xattrs, maps logical reads to block/stripe zip entries, verifies checksums, reconstructs missing stripes through `RedundancyProvider`, supports scalar reads and a host-batched vector-read path, and closes archives.

### Important APIs, Types, and Functions
- `OpenOnlyImpl` is a private XrdCl zip operation that opens an archive without parsing its central directory immediately.
- Internal `block_t` caches all stripes for one block and tracks stripe state: `Empty`, `Loading`, `Valid`, `Missing`, and `Recovering`.
- `block_t::read`, `read_callback`, `error_correction`, `get_stripes`, `carryout`, and `fail_missing` implement per-block cache reads and recovery.
- `Reader::Open`, `Read`, `VectorRead`, and `Close` implement public operations.
- `Reader::Read(blknb, strpnb, buffer, cb)` reads one zip entry, verifies its CRC, and schedules callback.
- `ReadMetadata`, `ReadSize`, `ParseMetadata`, `AddMissing`, and `IsMissing` build the URL map and missing-stripe set.
- `MissingVectorRead` and `ErrorCorrected` coordinate vector-read fallback reconstruction.

### Control Flow
Open constructs a `ZipArchive` per placement URL. In normal metadata mode it opens data archives with `OpenOnly` and reads one replicated metadata file, then installs central directories into the zip archives and builds `urlmap`. In `nomtfile` mode it opens archives normally and reads `xrdec.filesize` from xattrs. The open operation requires at least `nbdata` data archives.

Scalar `Read` trims reads past EOF in `nomtfile` mode, splits the requested range by block and data stripe, obtains or creates a cached `block_t`, and issues `block_t::read` for each stripe. The shared read context aggregates byte counts and final status before scheduling the user's handler.

`block_t::read` starts an async stripe read for empty stripes, queues pending user reads while loading or recovering, serves valid cached data immediately, and triggers error correction when a requested stripe is missing. Recovery is possible if missing plus recovering stripes do not exceed parity and enough valid stripes are available; otherwise it loads additional empty stripes until `nbdata` are available and marks missing stripes recovering. When recovery succeeds, pending reads for recovered stripes are carried out.

Vector read groups requested stripe zip offsets by host/archive, issues XrdCl vector reads per host in chunks of at most 1024, verifies each requested stripe checksum, and falls back to `MissingVectorRead` for failed or corrupt stripes. The final handler waits on `waitMissing`, copies data from reconstructed block buffers into either a global buffer or per-chunk buffers, and returns success only if all segments are valid.

### State and Persistence
Reader state includes data archive map, central-directory metadata buffers during open, `urlmap`, missing set, a one-block scalar-read cache, file size, archive index map, and vector-read missing coordination state. It does not write persistent data. Persistent inputs are remote zip archives, optional `.mt` metadata files, and `xrdec.filesize` xattrs.

### Dependencies and Integration Points
The implementation depends on XrdCl async pipelines, `ZipArchive`, file and zip operations, XrdZip record parsers, XrdEc utilities, thread pool, singleton config, and redundancy provider. XrdCl EC handler owns `Reader` and forwards File read/vector-read operations to it.

### Risks and Edge Cases
The scalar cache only stores one block, so interleaved reads across blocks can evict useful state. `Read` only trims EOF in `nomtfile` mode; metadata mode appears to rely on missing zip entries to signal EOF. In checksum verification, one branch checks `st` instead of the result variable from `GetCRC32`, which may miss CRC lookup failures. `IsMissing` returns true for `nomtfile` when `fntoblk(fn) <= lstblk`, which looks counterintuitive and deserves tests. Vector read allocates `StatInfo* info` and may use it without guarding failed `Stat`; it also ignores per-chunk statuses in `VectorReadInfo` and treats whole-host status as representative. `missingChunksVectorRead` wait can deadlock if a fallback callback is never invoked. The vector final copy does not trim against `filesize` the same way scalar read does.

### Test Signals
Tests should include open with metadata and no-metadata modes, missing metadata replicas, central directory parsing, scalar reads crossing stripe and block boundaries, checksum mismatch recovery, unrecoverable missing count, EOF behavior, close of open archives, vector read with many chunks, failed host fallback, per-stripe CRC failure, global versus per-chunk buffers, and concurrency between scalar/vector reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/XrdEcReader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/XrdEcReader.hh -->
## sources/distributed-fs/xrootd/src/XrdEc/XrdEcReader.hh

### Purpose
This header declares the public and private interface for the XrdEc reader that reconstructs logical object reads from erasure-coded zip archives.

### Important APIs, Types, and Functions
- `buffer_t` is `std::vector<char>` for stripe and metadata buffers.
- `callback_t` is a status plus byte-count callback for internal stripe reads.
- `Reader` exposes `Open`, `Read`, `VectorRead`, `Close`, and `GetSize`.
- Private helpers include stripe-level `Read`, metadata and size reads, metadata parsing, missing set handling, vector fallback recovery, and callback generation.
- Friend declarations for `MicroTest`, `XrdEcTests`, and `block_t` expose internals to tests and implementation.

### Control Flow
The public lifecycle is open, read/vector-read zero or more times, then close. Private maps are populated during open and consumed during read mapping. Vector-read recovery coordination uses a mutex, vector of missing chunk ids, and condition variable.

### State and Persistence
The reader holds a reference to `ObjCfg`, archive and metadata maps, zip-entry-to-url mapping, missing stripe set, one cached block, synchronization primitives, last block number, file size, archive indices, and vector-read missing state. It owns no persistent remote objects.

### Dependencies and Integration Points
The header includes XrdEc object config, XrdCl zip archive and operations, and standard containers/synchronization. It is instantiated by `XrdClEcHandler` and implemented in `XrdEcReader.cc`.

### Risks and Edge Cases
`ObjCfg` is held by reference, so the config must outlive the reader. The one-block cache is protected by `blkmtx`, while block internals use their own mutex. `missingChunksVectorRead` tracks tuples globally for the reader, so overlapping vector reads can interfere unless calls are serialized by higher layers.

### Test Signals
Interface tests should validate lifecycle ordering, config lifetime assumptions, concurrent read behavior, size reporting after open, vector-read callback behavior, and close when no archives are open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/XrdEcReader.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/XrdEcRedundancyProvider.cc -->
## sources/distributed-fs/xrootd/src/XrdEc/XrdEcRedundancyProvider.cc

### Purpose
This file implements parity generation and missing-stripe recovery using ISA-L erasure-coding primitives, with a replication shortcut when there is one data stripe.

### Important APIs, Types, and Functions
- `gf_gen_decode_matrix(...)` is adapted from ISA-L tests and builds a decode matrix for a known error pattern.
- `RedundancyProvider::RedundancyProvider(const ObjCfg&)` creates a Cauchy encode matrix.
- `getErrorPattern(stripes_t&)` encodes missing/invalid stripes as a binary string.
- `getCodingTable(pattern)` expands the error pattern, builds/caches block indices and ISA-L decode tables.
- `replication(stripes_t&)` fills missing stripes from any healthy stripe for one-data-stripe layouts.
- `compute(stripes_t&)` performs no-op, replication, or erasure-code reconstruction depending on layout.

### Control Flow
`compute` first derives the error pattern. With no parity it returns. With one data stripe it calls replication. Otherwise it obtains a cached coding table for the exact missing pattern, builds input buffer pointers from selected healthy stripes, allocates temporary output buffers for each error, calls `ec_encode_data`, and copies reconstructed buffers back into the missing stripe slots.

`getCodingTable` locks the provider, counts errors and data-source errors, rejects patterns with more errors than parity, computes a decode matrix from the encode matrix and error arrays, initializes ISA-L tables, caches the table, and returns it.

### State and Persistence
Provider state is in an owned `ObjCfg` copy, Cauchy encode matrix, cached coding tables, and mutex. The cache persists for the provider lifetime and is shared by all readers/writers using the same singleton config key.

### Dependencies and Integration Points
This file depends on ISA-L `gf_gen_cauchy1_matrix`, `gf_invert_matrix`, `gf_mul`, `ec_init_tables`, and `ec_encode_data`; it also uses XrdEc utility `stripes_t` and `IOError`. Reader recovery and write-buffer encoding call through `Config::GetRedundancy`.

### Risks and Edge Cases
Variable-length arrays such as `unsigned char* inbuf[objcfg.nbdata]` and `outbuf[dd.nErrors]` rely on compiler extensions in C++. `dd.table.resize(objcfg.nbdata * objcfg.nbparity * 32)` may be larger than needed but should be sufficient for ISA-L table entries. `replication` chooses the last valid stripe encountered. `compute` does not mark `stripes[i].valid` true after recovery; callers must treat filled buffers as valid or update state separately. Error handling throws `IOError`, so callers must catch it.

### Test Signals
Tests should cover no-parity no-op, one-data replication, all single-stripe failures, mixed data/parity failures, too many failures, cache reuse for repeated patterns, checksum-before-recovery expectations, and byte-for-byte reconstruction against known ISA-L examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/XrdEcRedundancyProvider.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/XrdEcRedundancyProvider.hh -->
## sources/distributed-fs/xrootd/src/XrdEc/XrdEcRedundancyProvider.hh

### Purpose
This header declares the `RedundancyProvider` class, which computes missing data/parity blocks for a configured erasure-code layout.

### Important APIs, Types, and Functions
- Public `compute(stripes_t &stripes)` reconstructs missing stripe buffers or throws on invalid/unrecoverable input.
- Constructor fixes layout parameters from `ObjCfg`.
- Private `CodingTable` stores ISA-L table bytes, selected healthy block indices, and error count.
- Private `getErrorPattern`, `getCodingTable`, and `replication` support the implementation.

### Control Flow
Consumers construct or retrieve a provider for one layout and repeatedly call `compute` with a full stripe vector. The provider hides decode-table construction and caching behind the public method.

### State and Persistence
State includes an `ObjCfg` copy, encode matrix, decode-table cache keyed by error pattern, and mutex. There is no external persistence.

### Dependencies and Integration Points
The header depends on `XrdEcObjCfg.hh` and `XrdEcUtilities.hh` for layout and stripe descriptors. `XrdEcConfig` caches instances, `Reader` uses them for recovery, and write-buffer code uses them for parity generation.

### Risks and Edge Cases
The contract says blocks can be arbitrary size but equal within a stripe; the implementation uses `objcfg.chunksize`, so caller buffers must be sized accordingly. The class is thread-safe around cache construction but not around caller-owned stripe buffers. Exceptions are the error channel, not status returns.

### Test Signals
Compile tests should catch ISA-L type compatibility. Runtime tests should assert `compute` behavior for valid and invalid stripe vectors, exception propagation, and concurrent calls with identical and distinct error patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/XrdEcRedundancyProvider.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/XrdEcStrmWriter.cc -->
## sources/distributed-fs/xrootd/src/XrdEc/XrdEcStrmWriter.cc

### Purpose
This file implements the streaming writer for XrdEc objects. It opens placement archives, buffers user writes into erasure-code blocks, asynchronously encodes/checksums blocks, writes stripe zip entries across shuffled servers with retry, writes metadata or xattrs at close, and reports final status through XrdCl handlers.

### Important APIs, Types, and Functions
- `StrmWriter::Open` opens a `ZipArchive` for each placement in new/write mode and requires all `nbchunks` archives.
- `Write` appends user bytes into `WrtBuff` objects and enqueues complete blocks for encoding while reporting immediate user success after buffering.
- `Close` enqueues partial final data and delegates close sequencing to `global_status`.
- `WriteBuff` writes one encoded block's stripe entries as zip files named by `ObjCfg::GetFileName`, shuffling server placement and retrying failed stripe writes on other servers.
- `GetMetadataBuffer` packages each data archive's central directory into a metadata zip-like buffer with LFH/CDFH/EOCD records.
- `CloseImpl` sets xattrs, closes data archives, and optionally replicates metadata files.

### Control Flow
Open creates all archive objects and sends parallel open requests. Write first checks global error state, increments outstanding byte count, fills the current `WrtBuff`, and when a buffer becomes complete, passes it to `EnqueueBuff` from the header, where a thread-pool task encodes parity and CRCs. A dedicated writer thread dequeues prepared buffers and calls `WriteBuff`.

`WriteBuff` shares one prepared buffer across all stripe write pipelines, randomizes server order for block placement, builds one append operation per stripe, retries failed appends on an unused server, and reports the data-byte count for the block to `global_status` after all writes complete. Close marks no more writes, waits through `global_status` until outstanding bytes are reported, then runs `CloseImpl`. In metadata-file mode, `CloseImpl` closes all data archives and writes replicated metadata to at least `nbparity + 1` placements; in no-metadata mode it sets `xrdec.filesize` and `xrdec.strpver` xattrs and closes data archives only.

### State and Persistence
Persistent outputs are remote data zip archives containing stripe entries, optional `.mt` metadata files holding central-directory summaries, and xattrs recording file size and stripe version. Runtime state includes data/metadata archive vectors, current write buffer, queue of futures for prepared buffers, background writer thread, next block number, and global write/close status.

### Dependencies and Integration Points
The implementation depends on `XrdEcStrmWriter.hh`, `WrtBuff`, `ThreadPool`, XrdCl zip/file/parallel operations, XrdZip LFH/CDFH/EOCD helpers, and `ObjCfg`. `XrdClEcHandler` constructs this writer for EC file writes.

### Risks and Edge Cases
`Write` reports success once data is buffered, so later remote write failures surface only through subsequent writes or close. `Open` invokes `handler->HandleResponse` without null-checking `handler`. `WriteBuff` retries failed appends but if no alternate server remains, the lambda returns without directly reporting that stripe failure; final parallel status behavior must be verified. The random engine is static and shared. `global_status_t::report_wrt` subtracts from unsigned `btsleft`, so mismatched byte accounting can underflow. Close handler timeout is not preserved when deferred in `issue_close`. Background-thread shutdown depends on queue interrupt and join.

### Test Signals
Tests should cover open success/failure thresholds, writes smaller/larger than one block, partial final block close, server shuffle and retry, failed writes surfacing at close, metadata-file contents parseable by `Reader::ParseMetadata`, no-metadata xattrs, background thread shutdown, and concurrent write/close ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdEc/XrdEcStrmWriter.cc -->
