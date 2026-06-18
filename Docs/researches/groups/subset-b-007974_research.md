# subset-b-007974 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleManager.hh -->
# sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleManager.hh

Purpose: Declares the XrdThrottleManager service and its XrdThrottleTimer RAII helper. The manager enforces global and per-user throttles for bytes, operations, active I/O concurrency, open files, and connections while trying to preserve user fair share through hash-bucketed user IDs.

Important APIs/types/functions: Public configuration and enforcement entry points are Init(), FromConfig(), SetThrottles(), SetLoadShed(), SetMaxOpen(), SetMaxConns(), SetMaxWait(), LoadUserLimits(), ReloadUserLimits(), GetUserMaxConn(), OpenFile(), CloseFile(), Apply(), StartIOTimer(), PrepLoadShed(), CheckLoadShed(), and PerformLoadShed(). GetUserInfo() derives a username and uint16_t bucket. The Waiter struct owns per-user condition variables and EWMA accounting. XrdThrottleTimer starts timing in its constructor, links itself into a hashed TimerList, and calls StopIOTimer() from its destructor.

Control flow: Callers identify the user, call Apply() or StartIOTimer(), block behind Waiter::Wait() when shares or concurrency are exhausted, and rely on a recompute thread to refill shares and compute wake order. RecomputeInternal(), ComputeWaiterOrder(), UserIOAccounting(), NotifyOne(), GetShares(), and StealShares() are private implementation hooks declared here.

State/persistence: State is in memory: fixed-size share vectors, waiter arrays, relaxed atomics, open/connection maps, active-connection maps keyed by pid, per-user limit map, and reloadable config filename. No durable persistence is declared beyond reading user-limit configuration.

Dependencies/integration: Uses XrdSys atomics, condition variables, pthread bootstrap, XrdSecEntity, XrdOucTrace, XrdSysError, XrdXrootdGStream monitoring, and XrdThrottle::Configuration.

Risks: UID hashing can collide, so limits/fairness are approximate. The mix of relaxed atomics, std::mutex, XrdSysCondVar, and shared_mutex demands careful implementation. TimerList link/unlink correctness is critical because timer destructors mutate linked lists. User-limit wildcard semantics are only declared here and need implementation tests.

Test signals: Exercise throttle refill fairness, hashed-user collision behavior, max wait timeout, max open/max connection counters including pid cleanup, user-limit reload while readers call GetUserMaxConn(), load-shed opaque handling, and RAII timer cleanup under exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleManager.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleTrace.hh -->
# sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleTrace.hh

Purpose: Defines compile-time trace flags and macros for the throttle subsystem.

Important APIs/types/functions: The header exports TRACE_NONE, TRACE_ALL, TRACE_BANDWIDTH, TRACE_IOPS, TRACE_IOLOAD, TRACE_DEBUG, TRACE_FILES, and TRACE_CONNS. When NODEBUG is not set it includes XrdSysHeaders and XrdOucTrace, defaults XRD_TRACE to m_trace->, and defines TRACE(act,x), TRACEI(act,x), and TRACING(x). TRACE uses TraceID; TRACEI also expects TRACELINK->ID.

Control flow: Call sites wrap expensive diagnostic formatting behind TRACE or TRACING checks. At expansion time, XRD_TRACE What is masked with the requested flag, then Beg(), stream output to std::cerr, and End() delimit the trace record.

State/persistence: No persistent state is owned here. The macros depend on an ambient trace pointer, TraceID, and optionally TRACELINK supplied by the including class or function scope.

Dependencies/integration: This is tightly coupled to XrdOucTrace and the style used by XrdThrottleManager implementation files. NODEBUG removes tracing calls entirely.

Risks: Macro context requirements are implicit and can break compilation if included outside expected manager/link scopes. TRACE_ALL covers only 0x0fff; future flags outside that mask would not be included. std::cerr formatting side effects are skipped in NODEBUG builds.

Test signals: Compile throttle code with and without NODEBUG; enable individual trace masks and verify bandwidth, IOPS, IO load, file, and connection diagnostics appear only when requested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdTls/CMakeLists.txt

Purpose: Adds the TLS support sources to the XrdUtils target.

Important APIs/types/functions: Uses target_sources(XrdUtils PRIVATE ...) to compile XrdTls.cc/.hh, XrdTlsContext.cc/.hh, hostcheck and notary inline/header helpers, XrdTlsNotary.cc/.hh, XrdTlsPeerCerts.cc/.hh, XrdTlsSocket.cc/.hh, and XrdTlsTempCA.cc/.hh.

Control flow: There is no conditional logic in this file. Inclusion in the build is inherited from the surrounding build tree that defines XrdUtils and the OpenSSL/library dependencies.

State/persistence: No runtime state.

Dependencies/integration: The file makes TLS a built-in part of XrdUtils instead of a separate module. That means downstream users of XrdUtils get the common TLS abstractions, hostname validation, peer cert wrapper, and temporary CA bundling support.

Risks: The file lists .icc helpers but does not list XrdTlsTrace.hh, likely because it is a header-only include not needed by CMake for compilation. Build correctness depends on higher-level CMake linking XrdUtils against OpenSSL and other Xrd libraries used by these sources.

Test signals: A clean CMake configure/build should compile all listed units and fail if OpenSSL symbols or XrdCrypto/XrdSys dependencies are not available through the parent target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTls.cc -->
# sources/distributed-fs/xrootd/src/XrdTls/XrdTls.cc

Purpose: Implements common TLS diagnostics, debug control, and OpenSSL error-code conversion for the XrdTls facade.

Important APIs/types/functions: XrdTls::Emsg() routes optional messages through a global callback and can flush the OpenSSL error queue via ERR_print_errors_cb(). XrdTls::RC2Text() maps XrdTls::RC values to user-facing reason strings. SetDebug() overloads connect XrdTlsGlobal::SysTrace to either an XrdSysLogger or callback. SetMsgCB() installs the global message callback. ssl2RC(), ssl2Text(), and ClearErrorQueue() translate or clear OpenSSL state.

Control flow: Default messages go to stderr through ToStdErr(). Emsg() normalizes a null trace id to TLS, emits msg if present, optionally mirrors to stderr when dbgOUT/echoMsg is active, then prints pending OpenSSL errors if flush is true. ssl_msg_CB() is the ERR_print_errors_cb adapter.

State/persistence: Global process state includes XrdTlsGlobal::SysTrace, msgCB, and echoMsg. There is no durable persistence.

Dependencies/integration: Used by XrdTlsContext and XrdTlsSocket for all error reporting and by TLS trace macros through XrdTlsGlobal::SysTrace. Depends on OpenSSL ERR/SSL and XrdSysE2T.

Risks: Global callbacks are not protected by locks here, so applications should set them during initialization as documented. Emsg() only clears OpenSSL errors when flush is true; callers that pass false must ensure the queue is otherwise handled.

Test signals: Verify RC2Text/ssl2RC/ssl2Text mappings, callback routing, dbgOUT mirroring, and OpenSSL error queue flushing in failure paths from context and socket code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTls.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTls.hh -->
# sources/distributed-fs/xrootd/src/XrdTls/XrdTls.hh

Purpose: Declares the common TLS facade used by XRootD TLS context and socket code.

Important APIs/types/functions: Defines enum RC with success, connection closed, missing cert/context, hostname validation failure, SSL/system/unknown/verification failures, and OpenSSL WANT states. Declares Emsg(), RC2Text(), SetMsgCB(), SetDebug() overloads, ssl2RC(), ssl2Text(), and ClearErrorQueue(). It also defines debug masks dbgOFF, dbgCTX, dbgSOK, dbgSIO, dbgALL, and dbgOUT.

Control flow: This header has no runtime flow, but defines the error and debug contract that XrdTlsSocket returns to callers and that XrdTlsContext uses for construction diagnostics.

State/persistence: No owned state in the header. Implementations use process-global message/debug state.

Dependencies/integration: Forward declares XrdSysLogger and avoids OpenSSL includes in the public header except through implementation. It is included by XrdTlsSocket.hh, XrdTlsContext.cc, XrdTls.cc, and tracing code.

Risks: RC values are ABI-visible because callers may compare enum values. Debug flags are bitmasks used by macros; changes must remain coordinated with XrdTlsTrace.hh.

Test signals: Compile consumers against the public header, validate no OpenSSL header leakage is required, and test that every RC produced by socket/context code has sensible RC2Text output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTls.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsContext.cc -->
# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsContext.cc

Purpose: Implements XrdTlsContext, the owner of OpenSSL SSL_CTX objects, TLS library initialization, certificate/key/CA validation, CRL refresh, session creation, session cache settings, and runtime client-auth toggling.

Important APIs/types/functions: XrdTlsContextImpl stores ctx, pending ctxnew, CTX_Params, crlMutex, flusher condition variable, refresh flags, lastCertModTime, and session cache replay state. XrdTlsCrl::Refresh() periodically clones contexts when CRLs or host certs change. XrdTlsFlush::Flusher() flushes OpenSSL session cache. InitTLS() initializes OpenSSL. VerPaths() validates filesystem permissions. verifyPeerCB() logs verification failures and can soft-fail missing CRLs when crlAM is set. Constructor, Clone(), Session(), SessionCache(), SetContextCiphers(), SetDefaultCiphers(), SetCrlRefresh(), x509Verify(), newHostCertificateDetected(), and SetTlsClientAuth() form the main behavior.

Control flow: Construction initializes debug/OpenSSL once, fills CA/cert paths from explicit parameters or environment for client contexts, validates paths, creates SSL_CTX with TLS_method(), sets secure options, loads CA locations and verification flags, sets ciphers, loads certificate/private key, starts CRL refresh if requested, and keeps the ctx. Session() fast-paths SSL_new(ctx) but, if ctxnew exists, swaps in the refreshed SSL_CTX under a write lock, repairs ex_data to point at the surviving owner, creates a session, and deletes the replacement wrapper.

State/persistence: State is process-local. Persistent inputs are cert/key/CA files and environment variables X509_CERT_DIR, X509_CERT_FILE, X509_USER_KEY, X509_USER_PROXY, XRDTLS_DEBUG. CRL and certificate changes are detected by periodic refresh and stat modification time.

Dependencies/integration: Depends on OpenSSL SSL/BIO/ERR/X509, XrdOucUtils path/modtime helpers, XrdSys locks/threads/timers, XrdTls diagnostics, and XrdTlsTrace. XrdTlsSocket consumes Session() and GetParams().

Risks: Thread lifetime is delicate: destructor may leave pImpl for refresh/flusher threads to delete. Session() swaps SSL_CTX ownership and nulls ctxnew->pImpl->ctx to avoid double free. The CRL refresh loop clones contexts outside locks and must handle construction failure without losing the existing ctx. Permission masks in VerPaths() are security-sensitive.

Test signals: Test client/server context creation with explicit and env-derived paths, invalid permissions, missing CA in client mode, CRL soft fail, logVF output, cert/key mismatch, CRL refresh swap, host certificate modtime refresh, session cache id/flush options, and SetTlsClientAuth toggling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsContext.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsContext.hh -->
# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsContext.hh

Purpose: Declares XrdTlsContext, the public wrapper around OpenSSL SSL_CTX and TLS configuration options.

Important APIs/types/functions: CTX_Params records cert, pkey, cadir, cafile, opts, and crlRT. Public methods include Clone(), Context(), GetParams(), Init(), isOK(), Session(), SessionCache(), SetContextCiphers(), SetDefaultCiphers(), SetCrlRefresh(), SetTlsClientAuth(), x509Verify(), newHostCertificateDetected(), and the constructor/destructor. Option masks define handshake timeout, verify depth, log verification failures, server mode, DNS fallback, proxy-cert policy, CRL refresh/checking/full-chain checking, CRL soft-fail, auto-retry, and client-cert request disabling. TLS_SET_HSTO, TLS_SET_REFINT, and TLS_SET_VDEPTH pack option fields.

Control flow: The header documents that callers construct, immediately check isOK(), then request sessions through Session() for socket wrappers. Clone() can remove verification when full=false or start CRL refresh on the clone.

State/persistence: Runtime state is hidden behind XrdTlsContextImpl. Configuration state is captured in CTX_Params and exposed read-only by pointer.

Dependencies/integration: Forward declares XrdTlsSocket and XrdSysLogger. The ctxIndex static is used by OpenSSL ex_data callbacks in the implementation.

Risks: Option fields are ABI/API contracts. Some comments have drift from implementation, for example session cache replay in Clone() is now implemented. Context() exposes the raw SSL_CTX and bypasses locking constraints noted in the implementation.

Test signals: Compile public consumers, verify option macros preserve unrelated bits, and validate that comments about client/server CA behavior match constructor outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsContext.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsHostcheck.hh -->
# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsHostcheck.hh

Purpose: Declares curl-derived hostname wildcard matching used by TLS hostname validation.

Important APIs/types/functions: Defines CURL_HOST_NOMATCH, CURL_HOST_MATCH, and int Curl_cert_hostcheck(const char *match_pattern, const char *hostname).

Control flow: The implementation is in XrdTlsHostcheck.icc, included inside XrdTlsNotary.cc. XrdTlsNotaryUtils.icc can call Curl_cert_hostcheck while validating certificate SAN or CN names.

State/persistence: No state.

Dependencies/integration: This header is a small imported compatibility layer from curl. It avoids depending on libcurl at runtime by embedding the matching helper.

Risks: Hostname wildcard matching is security-sensitive and must match certificate validation rules. Any behavior change here can allow overbroad certificate matches or reject valid wildcard certificates.

Test signals: Unit test exact names, wildcard prefixes, embedded wildcard rejection, case-insensitivity if implemented by the .icc, malformed inputs, and IDN/punycode expectations if supported elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsHostcheck.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsNotary.cc -->
# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsNotary.cc

Purpose: Implements hostname validation for peer certificates after TLS connection establishment.

Important APIs/types/functions: XrdTlsNotary::Validate(const SSL *, const char *, XrdNetAddrInfo *) is the main API. Static cnOK controls whether Common Name fallback is permitted. The file includes XrdTlsHostcheck.icc and XrdTlsNotaryUtils.icc in anonymous namespaces, providing matches_subject_alternative_name() and matches_common_name().

Control flow: Validate() obtains the peer certificate, requires SSL_get_verify_result() to be X509_V_OK, checks the Subject Alternative Name extension first, and accepts on MatchFound. If SAN exists but does not match and DNS fallback is unavailable, validation fails immediately. If CN fallback is enabled or DNS fallback is available, it tries the common name. Finally, with addrInfo, it compares the requested host to reverse DNS name information.

State/persistence: Only process-global cnOK is kept. Certificates are fetched from the live SSL session and freed after SAN evaluation.

Dependencies/integration: Called by XrdTlsSocket::Connect() when thehost is provided. Depends on OpenSSL SSL/X509 and XrdNetAddrInfo.

Risks: The implementation frees the peer certificate before later calling matches_common_name() in the visible code path, which would be unsafe if the pointer is used after free; this deserves focused review against compiler/include behavior. CN fallback is deprecated but default-enabled. DNS reverse lookup fallback can be controversial for security.

Test signals: Validate SAN match/mismatch/malformed SAN/no SAN, verified vs unverified certs, CN fallback enabled/disabled, DNS fallback success/failure, and memory-safety under sanitizers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsNotary.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsNotary.hh -->
# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsNotary.hh

Purpose: Declares the hostname validation policy wrapper used by client TLS connections.

Important APIs/types/functions: XrdTlsNotary::Validate() validates a hostname against a peer SSL certificate and optional XrdNetAddrInfo for DNS fallback. UseCN(bool) controls whether Common Name fallback is permitted. Static cnOK stores that policy.

Control flow: The comments define policy order: SAN match first, CN fallback when allowed, then optional reverse DNS fallback if netInfo is supplied. The returned const char * is null on success or a diagnostic reason on failure.

State/persistence: Only static cnOK policy state.

Dependencies/integration: Includes openssl/ssl.h and forward declares XrdNetAddrInfo. XrdTlsSocket::Connect() uses this API after SSL_connect().

Risks: Since Validate() returns string literals/internal diagnostics, callers must not free the return. cnOK is global and not synchronized, so configure it at process initialization. The documented DNS fallback must be evaluated carefully in deployments with mutable reverse DNS.

Test signals: Public API tests should assert null/non-null semantics and verify UseCN(false) changes no-SAN certificate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsNotary.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsNotaryUtils.hh -->
# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsNotaryUtils.hh

Purpose: Declares imported helper types and functions for OpenSSL certificate hostname validation.

Important APIs/types/functions: Defines HostnameValidationResult with MatchFound, MatchNotFound, NoSANPresent, MalformedCertificate, and Error. Declares validate_hostname(const char *hostname, const X509 *server_cert).

Control flow: The header describes RFC 6125-style validation: check Subject Alternative Name first, then Common Name if SAN is absent. The .icc implementation is included into XrdTlsNotary.cc and provides lower-level helpers used by Validate().

State/persistence: No state.

Dependencies/integration: Requires X509 to be visible from OpenSSL includes in the including translation unit. Paired with XrdTlsHostcheck.hh for wildcard matching.

Risks: This file is imported code with its own license block; changes should preserve license terms. It is not include-guarded, so it is intended for controlled inclusion rather than broad public inclusion.

Test signals: Validate all enum outcomes through notary-level tests and direct helper tests where possible, especially malformed NUL-containing SAN/CN data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsNotaryUtils.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsPeerCerts.cc -->
# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsPeerCerts.cc

Purpose: Implements ownership behavior for XrdTlsPeerCerts.

Important APIs/types/functions: Destructor frees cert with X509_free() when present. getCert(bool upref) optionally increments the X509 reference count with X509_up_ref() before returning the cert pointer.

Control flow: XrdTlsSocket::getCerts() constructs this wrapper with SSL_get_peer_certificate() and SSL_get_peer_cert_chain(). The wrapper owns the peer cert reference but not the chain.

State/persistence: The object holds borrowed/owned pointers only for the lifetime of the TLS session/wrapper. No persistence.

Dependencies/integration: Depends on OpenSSL X509 and XrdTlsPeerCerts.hh. Consumers must observe the ownership contract from the header.

Risks: Passing getCert(false) to code that frees the certificate can double-free when the wrapper is destroyed. getChain() returns a session-owned chain, invalid after SSL_free().

Test signals: Reference-count tests around getCert(true), wrapper destruction, and using chain before/after socket shutdown with sanitizer instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsPeerCerts.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsPeerCerts.hh -->
# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsPeerCerts.hh

Purpose: Declares a small wrapper for a peer certificate and its peer certificate chain.

Important APIs/types/functions: XrdTlsPeerCerts(X509 *, STACK_OF(X509) *) stores the certificate and chain. getCert(upref) returns the certificate and can increment its reference count. getChain() returns the chain pointer. hasCert() and hasChain() expose presence checks.

Control flow: The object is created by XrdTlsSocket::getCerts() after optional verification. Callers delete it when done.

State/persistence: Holds one cert pointer and one chain pointer. The cert is owned by the wrapper; the chain is borrowed from the SSL session.

Dependencies/integration: Includes OpenSSL SSL for X509 stack types. It bridges XrdTlsSocket with security plugins needing certificate material.

Risks: The ownership asymmetry is easy to misuse. The header explicitly warns that many opaque APIs free certs and therefore require getCert(true). The chain lifetime is tied to the SSL session, not this wrapper.

Test signals: API tests should cover null cert/chain, hasCert/hasChain, upref failure handling, and caller ownership scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsPeerCerts.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsSocket.cc -->
# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsSocket.cc

Purpose: Implements XrdTlsSocket, a TLS I/O wrapper around an existing file descriptor and an XrdTlsContext-generated SSL session.

Important APIs/types/functions: XrdTlsSocketImpl stores SSL pointer, context, fd, trace id, handshake timeout/state, fatal error marker, client/server role, connection flags, and serialization policy. Accept(), Connect(), Init(), Peek(), Pending(), Read(), Write(), Shutdown(), NeedHandShake(), Version(), getCerts(), Diagnose(), Err2Text(), NeedHS(), and Wait4OK() are implemented here.

Control flow: Init() obtains SSL from context, sets connect/accept state, creates socket BIOs according to read/write blocking mode, handles nonblocking handshake setup for blocking-read server sockets, and attaches BIOs. Accept() loops SSL_accept(), verifies peer cert if configured, handles WANT_READ/WANT_WRITE by either returning nonblocking RC or polling, and restores blocking mode when needed. Connect() loops SSL_connect(), then validates hostname through XrdTlsNotary if requested. Read/Write/Peek use SSL_read/write/peek, translate OpenSSL WANT states, and optionally block with poll(). Shutdown() performs forced/fast/clean shutdown then frees SSL.

State/persistence: State is per socket object and no fd ownership is taken. Fatal SSL/SYSCALL errors are remembered to avoid later OpenSSL calls that could crash. The traceID pointer must outlive the socket.

Dependencies/integration: Depends on OpenSSL SSL/BIO/ERR, fcntl/poll/socket APIs, XrdSysE2T, XrdSysMutex, XrdTlsContext, XrdTlsNotary, XrdTlsPeerCerts, and trace macros.

Risks: Blocking mode transitions mutate the underlying fd and affect other users of the same fd. Wait4OK uses handshake timeout only until hsDone; later I/O can block indefinitely when configured blocking. fatal state protects against unsafe reuse but requires callers to respect return codes. Non-serialized mode shifts thread-safety responsibility to callers.

Test signals: Integration tests with client/server TLS sockets should cover every RW_Mode and HS_Mode, WANT_READ/WANT_WRITE nonblocking returns, handshake timeout, hostname validation failure, missing/failed peer cert verification, shutdown variants, fatal error reuse, and fd blocking restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsSocket.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsSocket.hh -->
# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsSocket.hh

Purpose: Declares the public TLS socket wrapper used for TLS handshakes and encrypted I/O over existing file descriptors.

Important APIs/types/functions: Defines RW_Mode combinations for blocking/nonblocking read/write BIOs, HS_Mode for blocking vs nonblocking handshakes, SDType for shutdown style, constructors, Init(), Accept(), Connect(), Context(), getCerts(), Peek(), Pending(), Read(), SetTraceID(), Shutdown(), Write(), NeedHandShake(), and Version().

Control flow: Users can either construct with full parameters and catch exceptions or default-construct and call Init() for error-string return. After Init(), client code calls Connect() and server code calls Accept(); I/O methods may perform implicit handshake if needed.

State/persistence: Implementation state is opaque in XrdTlsSocketImpl. The wrapper never closes the underlying fd.

Dependencies/integration: Includes XrdTls.hh and forward declares context, peer cert wrapper, and XrdNetAddrInfo. It is the boundary between XRootD network code and OpenSSL.

Risks: trace id lifetime is caller-owned. serial=false can expose OpenSSL session concurrency issues. Blocking semantics are subtle because handshake and read/write blocking modes are independent.

Test signals: Compile API users, validate constructor exception and Init() error-string paths, and verify I/O return-code contract under blocking and nonblocking modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsSocket.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsTempCA.cc -->
# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsTempCA.cc

Purpose: Implements a temporary bundled CA/CRL file manager that scans a CA directory, deduplicates PEM CAs and CRLs, writes consolidated files under XRDADMINPATH/.xrdtls, and refreshes them periodically for consumers such as libcurl.

Important APIs/types/functions: Local Set wraps output FILE ownership. CASet::processFile() parses certificates into XrdCryptoX509Chain and writes unique subject hashes. CRLSet::processFile() parses CRLs, tracks unique issuer hashes, records whether any CRL was valid, and defers CRLs with critical extensions for processCRLWithCriticalExt(). TempCAGuard::create(), commit(), and destructor manage mkstemps-created files. XrdTlsTempCA constructor/destructor, Maintenance(), and MaintenanceThread() own lifecycle.

Control flow: Constructor creates two pipes, runs initial Maintenance(), then starts a refresh thread. Maintenance() requires XRDADMINPATH, creates temp CA/CRL files, opens the configured CA directory, iterates regular files/symlinks, processes each first as CA then as CRL, writes deferred critical-extension CRLs at the end, atomically renames temp files to ca_file.pem/crl_file.pem, and publishes shared_ptr filenames. MaintenanceThread() polls for shutdown or refresh interval, retrying sooner after failure.

State/persistence: Persistent outputs are ca_file.pem and crl_file.pem under XRDADMINPATH/.xrdtls. Runtime state includes pipe fds, m_ca_file/m_crl_file shared pointers, and m_atLeastOneCRLFound.

Dependencies/integration: Uses XrdSysFD wrappers, XrdSysError, XrdSysThread, XrdCrypto X509/CRL helpers, OpenSSL-backed parsing, filesystem dirent/stat APIs, and XrdVersion.

Risks: Destructor pipe loops appear to continue while rval != -1 || errno == EINTR, which deserves review because successful write/read may not break. Directory fd ownership on fdopendir failure may leak. Publishing shared_ptr filenames avoids locking but callers can observe old file paths until refresh completes. Output file permissions inherit mkstemps defaults/umask.

Test signals: Tests should cover missing XRDADMINPATH, unreadable CA dir, mixed CA/CRL/noncert files, duplicate hashes, CRLs with critical extensions, atomic file replacement, refresh after failure, shutdown thread exit, and IsValid/atLeastOneValidCRLFound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsTempCA.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsTempCA.hh -->
# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsTempCA.hh

Purpose: Declares XrdTlsTempCA, a manager for consolidated temporary CA and CRL files generated from a CA directory.

Important APIs/types/functions: Public methods are constructor, destructor, IsValid(), CAFilename(), CRLFilename(), and atLeastOneValidCRLFound(). Nested TempCAGuard exposes create(), getCAFD(), getCAFilename(), getCRLFD(), getCRLFilename(), commit(), and RAII cleanup.

Control flow: The class owns a maintenance thread that periodically invokes private Maintenance() and uses pipes for shutdown acknowledgement. Successful refresh interval is 900 seconds; failure retry interval is 10 seconds.

State/persistence: Holds pipe descriptors, XrdSysError reference, CA directory string, shared_ptr file path snapshots, CRL-found boolean, and generated files in an admin temp directory.

Dependencies/integration: Forward declares XrdSysError. Consumers can hand CAFilename()/CRLFilename() to libraries that require file paths instead of OpenSSL stores.

Risks: The class is noncopyable only through TempCAGuard; XrdTlsTempCA itself does not explicitly delete copy/move in the header, though fd/thread ownership makes copying unsafe if attempted. Thread shutdown behavior depends on implementation pipe protocol.

Test signals: Compile for accidental copy prevention expectations, construct/destruct repeatedly under sanitizers, and verify filename snapshots remain valid across refreshes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsTempCA.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsTrace.hh -->
# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsTrace.hh

Purpose: Defines TLS tracing macros for context, socket, and socket I/O operations.

Important APIs/types/functions: When NODEBUG is not set, includes XrdSysTrace.hh and defines TRACING(act), DBG_CTX(y), DBG_SOK(y), DBG_SIO(y), DBG_TLS(y), and EPNAME(x). NODEBUG builds define no-op debug macros.

Control flow: Call sites set EPNAME at function scope and then use DBG_* macros. The macros check XrdTlsGlobal::SysTrace.What against XrdTls debug flags and emit SYSTRACE records with either no trace id for context or pImpl->traceID for socket operations.

State/persistence: No state owned here. Depends on process-global XrdTlsGlobal::SysTrace and ambient pImpl/epname symbols in calling scope.

Dependencies/integration: Coupled to XrdTls.hh debug flags and XrdTls.cc global trace object. Used heavily by XrdTlsContext.cc and XrdTlsSocket.cc.

Risks: Macro context is implicit; DBG_SOK/DBG_SIO/DBG_TLS require pImpl. TRACING lacks parentheses around the full expression, so callers should use it carefully in larger expressions.

Test signals: Build with and without NODEBUG, enable XRDTLS_DEBUG=ctx/sok/sio/all for client contexts, and verify traces are emitted without altering TLS behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdTls/XrdTlsTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdVersion.hh.in -->
# sources/distributed-fs/xrootd/src/XrdVersion.hh.in

Purpose: Template header generated by CMake to define XRootD version strings, numeric version values, plugin SO version, and macros for embedding version information in objects/plugins.

Important APIs/types/functions: Defines XrdVERSION, XrdVNUMBER, XrdVSTRING, XRDPLUGIN_SOVERSION, XrdDEFAULTPORT, XrdMajorVNUM(), XrdMinorVNUM(), XrdPatchVNUM(), struct XrdVersionInfo, and macros XrdVERSIONINFODEF(), XrdVERSIONINFO(), XrdVERSIONINFOREF(), and XrdVERSIONINFOVAR().

Control flow: At configure time placeholders are replaced. At compile time XrdVERSIONINFO() emits an extern "C" XrdVersionInfo symbol named x##_ with prefix @V: and component/version string.

State/persistence: Version metadata is compiled into object files and discoverable with strings/grep. No runtime mutable state.

Dependencies/integration: Used by plugin entry points such as XrdVomsHttp.cc to export loader-visible version information and by XrdSysPlugin logic.

Risks: Macro token concatenation and symbol naming are ABI-sensitive. XrdDEFAULTPORT includes a trailing semicolon in the macro body, which callers must tolerate. Generated values must match plugin version rules.

Test signals: Configure output should substitute all placeholders; plugin shared objects should contain @V: records; loader compatibility tests should read exported symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdVersion.hh.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdVersionPlugin.hh -->
# sources/distributed-fs/xrootd/src/XrdVersionPlugin.hh

Purpose: Defines plugin version-checking rules, strict versioned plugin library names, and directive-to-plugin-symbol mappings for XRootD plugin loading.

Important APIs/types/functions: XrdVersionPlugin describes a creator symbol name/prefix/suffix, processing mode, and minimum compatible major/minor versions. Macros define DoNotChk, Optional, Required, XrdVERSIONPLUGIN_Rule, XrdVERSIONPLUGINRULES, XrdVERSIONPLUGIN_Maxim, XrdVERSIONPLUGINMAXIMS, XrdVERSIONPLUGINSTRICT, XrdVersionMapD2P, XrdVERSIONPLUGIN_Mapd, and XrdVERSIONPLUGINMAPD2P.

Control flow: XrdSysPlugin.cc consumes these macro-expanded tables to decide whether a loaded plugin must have version info, whether missing info is warning/fatal, and how directives map to creator symbols.

State/persistence: Static compile-time table data only.

Dependencies/integration: Includes entries for security, HTTP, storage, checksum, cache, XrdCl, VOMS, throttle, and other plugins. VOMS-specific entries include XrdSecgsiVOMSFun, XrdSecgsiVOMSInit, and strict libraries libXrdSecgsiVOMS.so/libXrdVoms.so.

Risks: Any plugin interface ABI change must update these rules. Missing strict names can allow unversioned fallback where not intended. New directives must be added to the mapping table to get correct loader diagnostics.

Test signals: Plugin loader tests for required/optional/missing version info, strict library name fallback rejection, directive mapping, and future major/minor compatibility boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdVersionPlugin.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdVoms/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdVoms/CMakeLists.txt

Purpose: Conditionally builds and installs the VOMS plugin module.

Important APIs/types/functions: Clears BUILD_VOMS cache, returns unless ENABLE_VOMS, uses find_package(VOMS) or REQUIRED when FORCE_ENABLED, sets BUILD_VOMS on success, creates plugin target XrdVoms-${PLUGIN_VERSION}, and symlinks libXrdHttpVOMS-${PLUGIN_VERSION}.so and libXrdSecgsiVOMS-${PLUGIN_VERSION}.so to the same module.

Control flow: If VOMS is disabled or unavailable, the whole directory contributes no target. When found, it compiles XrdVomsFun.cc, XrdVomsHttp.cc, XrdVomsMapfile.cc, and XrdVomsgsi.cc, links XrdUtils, VOMS libraries, and OpenSSL::SSL, and installs the module plus symlinks.

State/persistence: Build cache variable BUILD_VOMS records availability. Install-time symlinks persist in the install libdir.

Dependencies/integration: Integrates with external VOMS headers/libraries, XrdUtils, OpenSSL, and XRootD plugin naming/version scheme.

Risks: The install(CODE) symlink commands assume Unix-like ln and lib prefix/suffix. Both HTTP and SecGSI plugin entry points must live in the same shared object. If FORCE_ENABLED is set, missing VOMS is a hard configure failure.

Test signals: Configure with ENABLE_VOMS off/on, FORCE_ENABLED on with missing VOMS, build plugin, verify symlinks, and load both HTTP and GSI plugin symbols from the installed module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdVoms/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdVoms/XrdVoms.hh -->
# sources/distributed-fs/xrootd/src/XrdVoms/XrdVoms.hh

Purpose: Defines the common VOMS input structure for passing OpenSSL certificate and chain data to the VOMS extraction function.

Important APIs/types/functions: Includes voms/voms_api.h, openssl/x509.h, and openssl/pem.h. Defines Voms_x509_in_t with X509 *cert and STACK_OF(X509) *chain for the gCertX509 input format.

Control flow: XrdVomsHttp.cc fills Voms_x509_in_t from an SSL session and points XrdSecEntity::creds at it. XrdVomsFun::VOMSFun() consumes it when gCertFmt == gCertX509.

State/persistence: No state.

Dependencies/integration: Bridges OpenSSL TLS certificate objects with libvoms extraction and XrdSecEntity population.

Risks: The struct contains borrowed pointers; callers must keep the SSL session/cert alive while VOMSFun runs and must free only owned references.

Test signals: Compile both HTTP and GSI VOMS entry points and validate VOMSFun correctly interprets STACK_OF(X509) inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdVoms/XrdVoms.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsFun.cc -->
# sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsFun.cc

Purpose: Implements the VOMS authorization extraction function that reads proxy certificate chains, extracts VO/group/role/FQAN data via libvoms, populates XrdSecEntity fields, and optionally applies VOMS mapfile name mapping.

Important APIs/types/functions: XrdVomsFun constructor sets default raw cert format. NameOneLine(), FmtExtract(), FmtReplace(), VOMSFun(), and VOMSInit() are key methods. Macros handle SafeFree, debug printing, replacement of <g>/<r>/<vo>/<an>, and space-to-tab conversion.

Control flow: VOMSFun() sets ent.prox to xrdvoms, builds pxy and STACK_OF(X509) from raw XrdCryptoX509Chain, PEM bytes, or Voms_x509_in_t, calls vomsdata::Retrieve(RECURSE_CHAIN), filters VOs/groups, selects first/last/all group tuples, writes ent.vorg/grps/role/endorsements, applies output format replacements, frees temporary chain objects according to input ownership, returns failure if required VOMS fields are absent, and then applies m_mapfile if configured. VOMSInit() parses cfg options by locating tag ranges, validates certfmt and grpopt, builds group/VO hash filters, records format strings/debug level, logs configuration, and configures XrdVomsMapfile.

State/persistence: Per-object configuration includes cert format, group selection mode, debug level, group/VO filters, required string, output formats, logger/error destination, and singleton mapfile pointer. No durable writes.

Dependencies/integration: Uses libvoms, OpenSSL, XrdCryptoX509Chain/X509, XrdSecEntity, XrdOucString/Hash, XrdSysLogger, and XrdVomsMapfile.

Risks: Manual memory ownership around ent fields and X509 stacks is fragile. Config parsing is ad hoc and range-based, so quoted strings and tag ordering deserve tests. Multi-value VO/group/role strings are space-separated and then sometimes tab-normalized, which can affect downstream consumers.

Test signals: Test raw, PEM, and X509 input formats; missing proxy/chain; VOMS retrieval failure; VO/group filters; usefirst/uselast/useall; formatting placeholders; debug output; mapfile success/failure precedence; and sanitizer runs for X509/ent field ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsFun.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsFun.hh -->
# sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsFun.hh

Purpose: Declares XrdVomsFun, the configurable VOMS extraction engine used by GSI and HTTP security plugins.

Important APIs/types/functions: CertFormat enum supports gCertRaw, gCertPEM, and gCertX509. Public methods are SetCertFmt(), VOMSFun(XrdSecEntity &), VOMSInit(const char *), constructor, and destructor. Private helpers FmtExtract(), NameOneLine(), and FmtReplace() support configuration parsing and output formatting.

Control flow: Callers construct with XrdSysError, initialize from plugin parameters through VOMSInit(), optionally override cert format, then call VOMSFun() per authenticated entity.

State/persistence: Holds configuration filters/format strings and a pointer to XrdVomsMapfile. The comment notes instances are normally never deleted except HTTP.

Dependencies/integration: Depends on OpenSSL headers, XrdOucHash/String, XrdSecEntity, XrdSysError/Logger, and XrdVomsMapfile.

Risks: Object state is mutable and not obviously synchronized; sharing one instance across concurrent calls requires confirming plugin threading model. Destructor intentionally does not own m_mapfile.

Test signals: Compile consumers and test initialization idempotence, cert format overrides, and concurrent VOMSFun calls if plugin instances are shared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsFun.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsHttp.cc -->
# sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsHttp.cc

Purpose: Implements the HTTP security extractor plugin entry point that populates XrdSecEntity VOMS information from an HTTPS client certificate.

Important APIs/types/functions: Local class XrdVomsHttp derives from XrdHttpSecXtractor and implements GetSecData(), Init(), InitSSL(), and FreeSSL(). XrdHttpGetSecXtractor() is the exported factory. XrdVERSIONINFO(XrdHttpGetSecXtractor, XrdVomsHttp) emits plugin version metadata.

Control flow: The factory creates XrdVomsFun, initializes it from parms, forces gCertX509 because HTTP passes OpenSSL certificate objects, and returns a new XrdVomsHttp. GetSecData() ignores unverified TLS sessions by returning success with no entity, obtains peer cert and chain from SSL, points sec.creds to a Voms_x509_in_t stack object, calls VOMSFun(), sets sec.prot to gsi on success, frees the peer cert, clears sec.creds, and returns the VOMSFun result.

State/persistence: The extractor owns a reference to an XrdVomsFun allocated by the factory. No durable state.

Dependencies/integration: Depends on XrdHttpSecXtractor API, XrdSecEntity, OpenSSL SSL/X509, XrdVomsFun, XrdVoms.hh, and version macros.

Risks: The factory allocates XrdVomsFun and passes it by reference without visible destructor cleanup in XrdVomsHttp. Returning success on unverified SSL intentionally leaves no VOMS identity but may be surprising. sec.creds points to a stack object only during VOMSFun().

Test signals: Plugin load/version tests, verified cert with VOMS attributes, unverified cert behavior, missing peer cert, VOMSInit failure, and memory leak checks around plugin unload if supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsHttp.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsMapfile.cc -->
# sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsMapfile.cc

Purpose: Implements optional VOMS FQAN-to-local-username mapping from a mapfile with live reload.

Important APIs/types/functions: Static singleton mapper and tried_configure gate global configuration. Constructor stats/parses the mapfile and starts MaintenanceThread(). ParseMapfile(), ParseLine(), Map(), Compare(), MakePath(), Apply(), Get(), Configure(), and MaintenanceThread() form the implementation.

Control flow: Configure() imports XRDCONFIGFN, reads XRootD config through XrdOucStream, handles voms.mapfile and voms.trace directives, creates the singleton, and returns null, VOMS_MAP_FAILED, or a mapper. ParseLine() accepts quoted FQAN-like paths and printable targets with escapes. Apply() respects successful gridmap.name mappings first, tokenizes entity.vorg/role/grps in parallel, enforces that the FQAN root equals the VO, appends Role=... and Capability=NULL, maps the first matching entry, and replaces entity.name. MaintenanceThread() sleeps 30 seconds, stats ctime, and reparses on change.

State/persistence: Runtime singleton stores mapfile path, last ctime, atomic-ish shared_ptr entries snapshot, error stream, and validity flag. Persistent input is the configured mapfile.

Dependencies/integration: Uses XrdOucEnv, XrdOucStream, XrdOucString wildcard matches, XrdSecEntity extended attributes, XrdSysError, XrdSysThread, and POSIX stat/open.

Risks: Maintenance thread runs forever with no shutdown path. m_is_valid is read/written across threads without atomic protection. ParseLine grammar is strict and may silently skip malformed lines. Configure caches failure and will not retry a later fixed config in the same process.

Test signals: Test mapfile parsing with escapes/comments/invalid lines, wildcard matching, gridmap precedence, VO root enforcement, parallel token lengths, live ctime reload, missing config file, trace mask parsing, and thread-safety under concurrent Apply() while reloading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsMapfile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsMapfile.hh -->
# sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsMapfile.hh

Purpose: Declares the optional VOMS mapfile singleton and its FQAN mapping API.

Important APIs/types/functions: VOMS_MAP_FAILED is a sentinel pointer for configured-but-failed mapfile setup. Public static Configure() and Get() expose singleton access. Apply(XrdSecEntity &) mutates the entity name when a mapping matches. IsValid() reports last parse validity. Private MapfileEntry stores parsed path and target; private helpers parse, map, compare, make paths, and run maintenance.

Control flow: Configure() should be called during VOMS initialization; Apply() is called after VOMS attributes are populated.

State/persistence: Holds mapfile path, last ctime, shared parsed entries, error destination, validity flag, and static singleton/tried_configure. The mapfile itself is external persistent config.

Dependencies/integration: Includes XrdOucString, XrdSysError, and XrdSecEntity. It integrates XrdVomsFun with site-local username policy.

Risks: Reconfigure() is declared but not defined in the observed source, suggesting dead API or implementation drift. Shared singleton state means only one mapfile per process. Thread-safety of m_is_valid and m_edest updates deserves scrutiny.

Test signals: Header/API tests should assert sentinel handling, singleton reuse, SetErrorStream after prior configure, and Apply() behavior when mapper is null or invalid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsMapfile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsTrace.hh -->
# sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsTrace.hh

Purpose: Provides VOMS debug/print macros.

Important APIs/types/functions: When NODEBUG is not set, includes XrdSysLogger.hh and defines PRINT(y), DEBUG(y), and EPNAME(x). PRINT writes to std::cerr with gLogger->traceBeg()/traceEnd() and the XrdVoms prefix when gDebug is nonzero. DEBUG requires gDebug > 1. NODEBUG makes them no-ops.

Control flow: XrdVomsFun sets EPNAME in functions and uses PRINT/DEBUG through VOMSDBG/VOMSDBGSUBJ wrappers.

State/persistence: No state is owned here. Macros depend on ambient gDebug and gLogger members.

Dependencies/integration: Coupled to XrdVomsFun private member names and XrdSysLogger trace formatting.

Risks: Macro context is implicit, and printing goes directly to std::cerr while using logger trace delimiters. Debug output may include certificate subjects and VOMS attributes, so enable carefully in production.

Test signals: Build with NODEBUG and normal builds; run VOMSInit with dbg/dbg2 and verify expected log verbosity without crashes when gLogger is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsTrace.hh -->
