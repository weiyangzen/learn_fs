# subset-b-009129 Research

Grouped research for Git LFS files under `lfs`, `lfsapi`, `lfshttp`, and `locking`. Each section is source-tree aligned for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/pointer_test.go -->
# sources/sync-backup/git-lfs/lfs/pointer_test.go

Purpose: Exercises Git LFS pointer encoding/decoding, canonical-format detection, extension ordering, empty-file handling, and invalid-pointer rejection.

Important APIs/types/functions: Tests cover `NewPointer`, `NewPointerExtension`, `EncodePointer`, `DecodePointer`, `DecodeFrom`, pointer fields `Version`, `Oid`, `OidType`, `Size`, `Extensions`, and `Canonical`, plus `errors.IsNotAPointerError`.

Control flow: Tests construct literal pointer documents, decode from `bytes.Buffer` or `strings.Reader`, and assert parsed fields. Canonical tests run valid and non-canonical examples through the same decoder. Invalid tests iterate malformed samples and require an error.

State and persistence behavior: No persistent state; all data is in-memory buffers. `DecodeFrom` also returns a replay buffer for empty content and computes the empty SHA-256 and size.

Dependencies and integration points: Integrates with the pointer parser/encoder implementation in the `lfs` package and the shared error classification package. Uses `bufio.Reader` to verify line-by-line encoder output.

Risks and edge cases: Covers missing trailing newline, CRLF line endings, trailing whitespace, bad version strings, bad OID type/value, missing fields, extra keys, out-of-order keys, duplicate extension priorities, invalid extension names, and priorities outside supported range.

Test signals: Strong unit coverage for pointer format compatibility, including legacy prerelease version acceptance and extension sorting. It does not cover large-pointer-size performance or streaming decode beyond small literals.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/pointer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/scanner.go -->
# sources/sync-backup/git-lfs/lfs/scanner.go

Purpose: Defines common scanner constants, pointer result wrappers, and channel wrapper types used by Git LFS scanning pipelines.

Important APIs/types/functions: `blobSizeCutoff`, `stdoutBufSize`, `chanBufSize`, `WrappedPointer`, `catFileBatchCheck`, `catFileBatch`, `PointerChannelWrapper`, `StringChannelWrapper`, `TreeBlobChannelWrapper`, and their constructors.

Control flow: `catFileBatchCheck` creates small-revision, lockable, and error channels, delegates process setup to `runCatFileBatchCheck`, then returns a string wrapper and lockable channel. `catFileBatch` similarly prepares pointer and lockable channels, calls `runCatFileBatch`, and returns a pointer wrapper.

State and persistence behavior: No disk persistence. State is asynchronous and channel-based. Error channels are deliberately buffered to avoid goroutine blockage while scan consumers drain result channels and later call `Wait`.

Dependencies and integration points: Depends on `config.Environment`, `git.TreeBlob`, and `tools.BaseChannelWrapper`. The delegated `runCatFileBatch*` functions are the integration point with object database and Git cat-file behavior.

Risks and edge cases: Channel buffer sizes and error-channel capacities are correctness-sensitive; undersized buffers could deadlock if producers emit more errors than expected. `blobSizeCutoff` limits pointer scanning to small blobs, so changing pointer format size assumptions affects scanning.

Test signals: Direct tests are elsewhere; `scanner_test.go` and `scanner_git_test.go` validate scanner behavior through log parsing and repository scenarios.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/scanner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/scanner_git_test.go -->
# sources/sync-backup/git-lfs/lfs/scanner_git_test.go

Purpose: Provides git-level integration tests for `GitScanner` behavior across unpushed commits and historical pointer versions.

Important APIs/types/functions: Tests use `NewGitScanner`, `ScanUnpushed`, `ScanPreviousVersions`, `WrappedPointer`, test repository helpers, and `errors.Join` for callback aggregation.

Control flow: `TestScanUnpushed` creates branches and commits, pushes subsets to different remotes, and verifies pointer counts for all remotes, `origin`, and `upstream`. `TestScanPreviousVersions` creates a dated commit graph, scans old versions on `master` since a cutoff, sorts results by OID, and compares expected previous pointer states.

State and persistence behavior: Uses temporary Git repositories with real commit and remote state. No persistent repository mutation outside the test temp area; callbacks accumulate pointers in memory.

Dependencies and integration points: Integrates `lfs` scanner code with `config.New`, Git command execution, branch topology, remote refs, and pointer test utilities from `t/cmd/util`.

Risks and edge cases: Time-window tests depend on commit dates and branch ancestry. Remote-specific behavior must distinguish "pushed somewhere" from "pushed to a named remote".

Test signals: Strong integration signal for repository graph scanning. Does not inspect low-level channel error handling directly, but callback error aggregation would surface scanner failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/scanner_git_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/scanner_test.go -->
# sources/sync-backup/git-lfs/lfs/scanner_test.go

Purpose: Tests log-diff pointer scanning for additions and deletions, including path filtering and quoted/octal path decoding.

Important APIs/types/functions: Exercises `newLogScanner`, `LogDiffAdditions`, `LogDiffDeletions`, `scanner.Scan`, `scanner.Pointer`, `filepathfilter.New`, and helper assertions.

Control flow: A synthetic Git log diff containing deleted, modified, and added pointer documents is scanned in addition or deletion mode. Each test advances the scanner and asserts pointer name, OID, size, and filtering behavior.

State and persistence behavior: All input is an in-memory multiline string. Scanner state tracks the current diff file, plus/minus side, decoded pointer lines, and the latest parsed pointer.

Dependencies and integration points: Validates integration between log parsing, pointer decoding, Git path quoting/unquoting, and `filepathfilter` include/exclude semantics.

Risks and edge cases: Important cases include non-ASCII paths represented by Git octal escapes, pointers with extensions, modifications where both sides are pointers, and filters that include or exclude only matching paths.

Test signals: Good unit coverage for diff parser modes. It does not cover malformed diff input or asynchronous scanner wrappers.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/scanner_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/util.go -->
# sources/sync-backup/git-lfs/lfs/util.go

Purpose: Supplies platform detection, progress callback logging, path conversion, and file copy/link/temp helpers for LFS file operations.

Important APIs/types/functions: `Platform`, `GetPlatform`, `PathConverter`, `NewCurrentToRepoPathConverter`, `NewCurrentToRepoPatternConverter`, `CopyCallbackFile`, `CopyFileContents`, `LinkOrCopy`, and `TempFile`.

Control flow: `CopyCallbackFile` checks `GIT_LFS_PROGRESS`, validates absolute path, creates the directory, opens the log in append mode, and returns a throttled `tools.CopyCallback`. Path converters compute current working directory relative to repo root and optionally append slash or normalize `./` patterns.

State and persistence behavior: `currentPlatform` caches runtime OS. Progress logging appends to an external file and syncs each emitted line. `CopyFileContents` writes through a temp file in the configured temp directory and renames atomically. `LinkOrCopy` tries hard-linking before copy fallback.

Dependencies and integration points: Depends on `config.Configuration`, `tools` file helpers, `tasklog.DefaultLoggingThrottle`, `clock` through `GitFilter`, and OS filesystem semantics.

Risks and edge cases: Progress logging silently disables when env/event/filename is empty but errors on relative progress paths. `CopyFileContents` may fail cross-device rename if temp dir is not on the destination filesystem. Path conversion relies on symlink resolution and current process cwd.

Test signals: `util_test.go` covers callback read accounting and progress throttling. Path conversion and copy/link behavior are not directly covered here.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/util_test.go -->
# sources/sync-backup/git-lfs/lfs/util_test.go

Purpose: Tests callback reader accounting and `GitFilter.CopyCallbackFile` progress-log throttling.

Important APIs/types/functions: Uses `tools.NewByteBodyWithCallback`, `tools.CallbackReader`, `GitFilter.CopyCallbackFile`, fake clock, and `tasklog.DefaultLoggingThrottle`.

Control flow: The first two tests read a five-byte payload in two chunks and assert callback counts and cumulative bytes. The throttle test configures `GIT_LFS_PROGRESS`, reads a larger buffer at controlled fake times, and asserts only delayed or final progress lines are written.

State and persistence behavior: Uses a temp progress log file and a fake clock. The callback keeps `prevWritten` and a deadline to suppress too-frequent writes.

Dependencies and integration points: Integrates LFS progress logic with `config.Environment`, `jmhodges/clock`, and `tools.CallbackReader`.

Risks and edge cases: Confirms final completion is logged even before the next throttle interval. It does not cover invalid progress paths, filesystem errors, or nil callback conditions.

Test signals: Good signal for progress log format: `event index/total written/total filename`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfs/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfsapi/auth.go -->
# sources/sync-backup/git-lfs/lfsapi/auth.go

Purpose: Implements authenticated LFS API request execution, credential selection, access-mode upgrades after challenges, and request Authorization header population.

Important APIs/types/functions: `DoWithAuth`, `DoWithAuthNoRetry`, `DoAPIRequestWithAuth`, `doWithAuth`, `doWithCreds`, `getCreds`, `getCredURLForAPI`, `fixSchemelessURL`, `requestHasAuth`, `setRequestAuth*`, `getReqOperation`, and `getAuthAccess`.

Control flow: `DoWithAuth` retries auth failures up to a mode-sensitive limit, closing failed bodies and refreshing access mode after challenges. `doWithAuth` applies extra headers, fills credentials, executes with creds, rejects or approves helper credentials, and stores multistage auth state headers. `doWithCreds` delegates Negotiate to Kerberos/SPNEGO handling, otherwise uses `lfshttp.Client.DoWithRedirect` and recursively reauthenticates redirected requests.

State and persistence behavior: Mutates request headers, endpoint access cache/config through `Endpoints.SetAccess`, credential-helper state fields, and `c.access` mode ordering. It can approve/reject credentials in configured helpers, which may persist outside process depending on helper.

Dependencies and integration points: Integrates `creds`, `lfshttp`, endpoint discovery, Git credential helpers, URL auth, netrc-like credential filling through helper wrappers, and HTTP response error classification.

Risks and edge cases: Existing Authorization or token query suppresses credential filling. Requests to a different scheme/host use request URL credentials rather than endpoint credentials. Multistage auth avoids rejecting creds between stages. Retry limit behavior is critical to avoid loops.

Test signals: `auth_test.go` covers basic/negotiate challenge parsing, approve/reject flows, no-retry mode, retry limit, multistage non-advancement, credential URL derivation, URL embedded auth, remote URL auth, mismatched scheme/host/port, and redirect reauthentication.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfsapi/auth.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfsapi/auth_test.go -->
# sources/sync-backup/git-lfs/lfsapi/auth_test.go

Purpose: Validates authenticated API behavior and credential selection across challenge modes, retries, URL sources, and redirects.

Important APIs/types/functions: Tests `getAuthAccess`, `DoWithAuth`, `DoWithAuthNoRetry`, `DoAPIRequestWithAuth`, `getCreds`, mock credential helpers, multistage helper behavior, and redirect reauthentication.

Control flow: HTTP test servers return 401, challenge headers, redirects, or success. Mock helpers fill, approve, reject, or preserve multistage state. Table-driven credential tests construct contexts with endpoint, remote, header, and config variations, then assert `Authorization`, helper input, and chosen credential URL.

State and persistence behavior: In-memory mock helpers track approved credentials keyed by protocol/host/path. Client endpoint access mode mutates from `none` to `basic` or `negotiate` after challenges.

Dependencies and integration points: Uses `httptest`, `git.NewReadOnlyConfig`, `lfshttp.NewContext`, `creds.CredentialCacher`, and `lfsapi.Client` credential wrappers.

Risks and edge cases: Covers avoiding retry when an explicit Authorization header is rejected, retry exhaustion, multistage helpers that never advance state, and reauthentication when redirects cross hosts.

Test signals: High confidence for auth retry semantics and credential source precedence. It does not exercise real external credential helpers or real Kerberos/SPNEGO negotiation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfsapi/auth_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfsapi/body.go -->
# sources/sync-backup/git-lfs/lfsapi/body.go

Purpose: Provides JSON request-body marshaling and a seekable, closable byte body for LFS API requests.

Important APIs/types/functions: `ReadSeekCloser`, `MarshalToRequest`, `NewByteBody`, and `closingByteReader.Close`.

Control flow: `MarshalToRequest` JSON-marshals an object, sets `Content-Length` header and `req.ContentLength`, then assigns a `NewByteBody` reader. `NewByteBody` wraps `bytes.Reader` with a no-op `Close`.

State and persistence behavior: Mutates the provided `http.Request` in memory. No external persistence.

Dependencies and integration points: Mirrors `lfshttp/body.go` and is used by API clients and tests that need rewindable request bodies for redirects, retries, and trace logging.

Risks and edge cases: JSON marshal failures leave request body untouched. All marshaled bodies are buffered fully in memory, which is fine for API JSON payloads but not for large object streams.

Test signals: Covered indirectly by auth and locking API tests that assert `Content-Length` and JSON payloads.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfsapi/body.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfsapi/client.go -->
# sources/sync-backup/git-lfs/lfsapi/client.go

Purpose: Exposes `lfsapi.Client` methods that delegate generic HTTP behavior to the embedded `lfshttp.Client`.

Important APIs/types/functions: `NewRequest`, `Do`, `do`, `doWithAccess`, `LogRequest`, `GitEnv`, `OSEnv`, `ConcurrentTransfers`, `LogHTTPStats`, and `Close`.

Control flow: Most methods are pass-through wrappers. `Close` joins errors from shutting down pure SSH transfers and closing the HTTP client/logging resources.

State and persistence behavior: Delegates state to `lfshttp.Client` and SSH transfer map in `lfsapi.Client`. `Close` clears SSH transfers through `closeSSHTransfers`.

Dependencies and integration points: Integrates the API client abstraction with `lfshttp`, `config.Environment`, `creds.AccessMode`, and shared `errors.Join`.

Risks and edge cases: Wrapper methods preserve API shape while allowing auth layer to call generic HTTP routines. `do` currently ignores `remote` and `via`, relying on lower layers for redirects.

Test signals: Behavior is covered indirectly by auth, response, endpoint, and locking tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfsapi/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfsapi/endpoint_finder.go -->
# sources/sync-backup/git-lfs/lfsapi/endpoint_finder.go

Purpose: Resolves LFS API endpoints and access modes from Git config, remotes, push URLs, aliases, local paths, FETCH_HEAD, and URL schemes.

Important APIs/types/functions: `EndpointFinder`, `endpointGitFinder`, `NewEndpointFinder`, `Endpoint`, `RemoteEndpoint`, `GitRemoteURL`, `NewEndpointFromCloneURL`, `NewEndpoint`, `AccessFor`, `SetAccess`, `ReplaceUrlAlias`, `ExtractRemoteUrl`, and alias helpers.

Control flow: Endpoint resolution prefers `lfs.pushurl` for uploads, then `lfs.url`, then remote-specific LFS URLs, Git remote URLs, and finally `FETCH_HEAD` for default remote downloads. Clone URLs are converted to endpoint URLs by appending `.git/info/lfs` or `/info/lfs` unless file URLs are used.

State and persistence behavior: Caches remotes, aliases, push aliases, and per-URL access modes. `SetAccess` writes or unsets `lfs.<url>.access` in the Git config and updates the access cache under lock.

Dependencies and integration points: Uses `git.Configuration`, `config.URLConfig`, Git remotes, `lfshttp.Endpoint` constructors, `creds.Access`, and SSH metadata parsing.

Risks and edge cases: URL alias matching intends longest prefix selection but compares strings lexicographically rather than length, which may matter for overlapping aliases. `ExtractRemoteUrl` has a restrictive regex. Local path detection depends on `os.Stat`.

Test signals: `endpoint_finder_test.go` broadly covers config precedence, SSH/HTTP/git/file/local paths, access config, alias replacement, FETCH_HEAD extraction helper, custom git protocol, and URL parsing cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfsapi/endpoint_finder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfsapi/endpoint_finder_test.go -->
# sources/sync-backup/git-lfs/lfsapi/endpoint_finder_test.go

Purpose: Validates endpoint resolution, access-mode configuration, URL parsing, and alias replacement for LFS API endpoints.

Important APIs/types/functions: Tests `Endpoint`, `RemoteEndpoint`, `NewEndpoint`, `NewEndpointFromCloneURL`, `AccessFor`, `SetAccess`, `ExtractRemoteUrl`, and `ReplaceUrlAlias`.

Control flow: Tests construct `lfshttp.Context` objects with synthetic Git config and assert returned endpoint URL, SSH metadata, operation, and access modes. Table-driven cases cover bare SSH, bracketed ports, remote helpers, and `insteadOf`/`pushInsteadOf`.

State and persistence behavior: Access tests mutate in-memory Git config through `SetAccess`. Local-path tests create temp directories with or without `.git` to exercise file URL rewriting.

Dependencies and integration points: Integrates with `lfshttp.Endpoint`, `ssh.SSHMetadata`, `creds`, runtime OS detection, and `os.Stat`.

Risks and edge cases: Windows local path behavior is skipped due path canonicalization differences. Tests cover invalid FETCH_HEAD lines and remote URL extraction but not actual `parseFetchHead` filesystem fallback.

Test signals: Strong coverage of endpoint precedence and parsing. Helps prevent regressions in remote push URL and alias behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfsapi/endpoint_finder_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfsapi/kerberos.go -->
# sources/sync-backup/git-lfs/lfsapi/kerberos.go

Purpose: Handles Negotiate authentication path for API requests.

Important APIs/types/functions: `Client.doWithNegotiate`.

Control flow: When access mode is `creds.NegotiateAccess`, the client delegates to `doWithAccess` with Negotiate mode, allowing the lower HTTP transport to use SPNEGO. NTLM is explicitly not supported by this path.

State and persistence behavior: No direct state mutation beyond the delegated HTTP request.

Dependencies and integration points: Integrates with `creds.CredentialHelperWrapper`, `creds.NegotiateAccess`, and `lfshttp.Client.Transport`, which wraps transport with `spnego.Transport` for negotiate mode.

Risks and edge cases: `credWrapper` is unused here; any future NTLM or credential material handling would need explicit implementation. SPNEGO errors are converted to auth errors in `lfshttp`.

Test signals: Covered indirectly by auth mode selection tests; no real Kerberos integration test in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfsapi/kerberos.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfsapi/lfsapi.go -->
# sources/sync-backup/git-lfs/lfsapi/lfsapi.go

Purpose: Defines the high-level LFS API client composition, endpoint and credential dependencies, and pure SSH transfer lifecycle.

Important APIs/types/functions: `Client`, `NewClient`, `Context`, `SSHTransfer`, `initSSHTransfer`, and `closeSSHTransfers`.

Control flow: `NewClient` creates a default context if needed, builds endpoint finder, HTTP client, credential helper context, access-mode list, and SSH transfer map. `SSHTransfer` memoizes per operation/remote transfer objects and initializes them lazily. `initSSHTransfer` checks endpoint SSH metadata and `lfs.<url>.sshtransfer` config before attempting `ssh.NewSSHTransfer`.

State and persistence behavior: Holds mutable endpoint/access state, credential helper, HTTP client cache, and SSH transfer map protected by a mutex. `closeSSHTransfers` shuts down all live transfers and clears the map.

Dependencies and integration points: Integrates `lfshttp`, `creds`, `config.URLConfig`, `ssh.SSHTransfer`, and tracer logging. Locking code uses this to choose HTTP versus pure SSH lock clients.

Risks and edge cases: A failed SSH transfer initialization is not cached, so repeated calls may retry. Config values other than `negotiate` or `always` disable pure SSH transfer. Concurrency depends on the transfer mutex.

Test signals: Indirect coverage through locking generic client behavior and endpoint tests. No direct test for transfer shutdown errors in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfsapi/lfsapi.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfsapi/response_test.go -->
# sources/sync-backup/git-lfs/lfsapi/response_test.go

Purpose: Tests API response error classification and message extraction for auth, fatal, and nonfatal server statuses.

Important APIs/types/functions: Uses `Client.Do`, `lfshttp.handleResponse`, `lfshttp.DecodeJSON`, `errors.IsAuthError`, and `errors.IsFatalError`.

Control flow: Test servers return specific status codes with or without JSON bodies. Tests assert wrapped error category and resulting message or prefix.

State and persistence behavior: No persistent state; each test uses temporary HTTP servers and in-memory counters.

Dependencies and integration points: Connects `lfsapi.Client` pass-through `Do` to `lfshttp` response classification and JSON error decoding.

Risks and edge cases: Covers 401, 500, 501, 507, and 509. It does not cover 422, 429 retry-after, 403/404 default errors, or invalid JSON bodies.

Test signals: Good signal that JSON `message` bodies override default messages and empty bodies get status-specific fallbacks.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfsapi/response_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/body.go -->
# sources/sync-backup/git-lfs/lfshttp/body.go

Purpose: Provides JSON body marshaling and a seekable/closable byte body for HTTP client requests.

Important APIs/types/functions: `ReadSeekCloser`, `MarshalToRequest`, `NewByteBody`, and `closingByteReader.Close`.

Control flow: JSON-marshals input, sets `Content-Length`, assigns `ContentLength`, and wraps bytes in a `bytes.Reader` that implements `Close`.

State and persistence behavior: Mutates only the passed `http.Request`; no external state.

Dependencies and integration points: Used by `lfshttp.Client.NewRequest`, retry logic, verbose tracing, and tests. Seekability is required because tracing and retry/redirect handling rewind bodies.

Risks and edge cases: Fully buffers JSON payloads in memory. Non-JSON or large streaming bodies should not use this helper.

Test signals: `client_test.go`, `retries_test.go`, and verbose/stats tests exercise body creation and rewinding indirectly.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/body.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/certs.go -->
# sources/sync-backup/git-lfs/lfshttp/certs.go

Purpose: Configures TLS certificate verification, client certificates, and root CA pools from Git config and environment.

Important APIs/types/functions: `isCertVerificationDisabledForHost`, `isClientCertEnabledForHost`, `decryptPEMBlock`, `getClientCertForHost`, `getRootCAsForHostFromGitconfig`, `appendCertsFromFilesInDir`, `appendCertsFromFile`, `appendCerts`, and `appendCertsFromPEMData`.

Control flow: Host-specific `sslverify=false` or global skip disables verification. Client certs require both host `sslKey` and `sslCert`, expand paths, read PEM files, decrypt encrypted keys via credential helper when needed, and load `tls.X509KeyPair`. Root CAs are selected from `GIT_SSL_CAINFO`, URL config, `GIT_SSL_CAPATH`, or `http.sslcapath`, with schannel exceptions.

State and persistence behavior: Reads certificate/key files and may approve/reject passphrases via credential helpers. Builds in-memory `x509.CertPool`; no direct file writes.

Dependencies and integration points: Used by `Client.Transport` to configure `tls.Config`. Depends on `config.URLConfig`, `tools.ExpandPath`, Cygwin path translation, credential helper context, and tracer logging.

Risks and edge cases: Missing or unparsable cert files log and return unchanged pools. Returning nil preserves system roots; returning an empty pool would be dangerous, so append helpers avoid that. Decryption assumes helper returns a password.

Test signals: `certs_test.go` covers CA file/path config and env sources, schannel behavior, and global/host SSL verification disabling.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/certs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/certs_test.go -->
# sources/sync-backup/git-lfs/lfshttp/certs_test.go

Purpose: Tests root CA discovery and SSL verification disabling from Git config and environment.

Important APIs/types/functions: Uses `getRootCAsForHostFromGitconfig`, `clientForHost`, `Client.HttpClient`, and `http.Transport.TLSClientConfig`.

Control flow: Tests write a temporary PEM certificate, configure CA info/path in Git or environment, and assert a non-nil cert pool for matching hosts. SSL verify tests construct clients and inspect `InsecureSkipVerify` on host transports.

State and persistence behavior: Uses temp files/directories for certificate fixtures. Client transport cache stores per-host HTTP clients during tests.

Dependencies and integration points: Validates `config.URLConfig` host matching, OS env settings (`GIT_SSL_CAINFO`, `GIT_SSL_CAPATH`, `GIT_SSL_NO_VERIFY`), and schannel settings.

Risks and edge cases: Host-specific CA config matches `git-lfs.local` but not host:port or unrelated hosts. Schannel defaults ignore CA info unless `schannelusesslcainfo` is enabled.

Test signals: Good coverage of root CA and verification toggles. Client-certificate loading and encrypted key decryption are not covered here.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/certs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/client.go -->
# sources/sync-backup/git-lfs/lfshttp/client.go

Purpose: Implements the core Git LFS HTTP client: request construction, SSH auth resolution, redirects, retries, extra headers, TLS/proxy transport, protocol selection, and client caching.

Important APIs/types/functions: `Client`, `NewClient`, `NewRequest`, `Do`, `DoWithAccess`, `DoWithRedirect`, `doWithRedirects`, `Transport`, `HttpClient`, `ExtraHeadersFor`, `configureProtocols`, `sshResolveWithRetries`, `newRequestForRetry`, and `deadlineConn`.

Control flow: `NewRequest` optionally resolves SSH metadata through `git-lfs-authenticate`, validates HTTP(S), joins endpoint/suffix, applies SSH headers, Accept, and JSON body. `Do` adds extra headers, gets a cached HTTP client by host/access mode, executes with redirects and error handling. Redirect handling caps chains, resolves relative locations, blocks HTTPS-to-HTTP downgrades, strips Authorization across host changes, and preserves body/context. Transport setup applies proxy, timeouts, activity deadlines, TLS certs/root CAs, HTTP version, cookie jar, and SPNEGO for Negotiate.

State and persistence behavior: Caches `http.Client` instances in `hostClients`, stores URL config and env, may use SSH auth cache, and may attach HTTP stats logger. Reads Git config/env for timeouts, SSL, proxy, cookies, HTTP version, and transfer concurrency.

Dependencies and integration points: Central integration point for `lfsapi`, transfer adapters, `lfshttp` cert/proxy/cookie/stats/verbose/retry helpers, `creds`, `ssh`, SPNEGO, and Go `http.Transport`.

Risks and edge cases: Request bodies must be seekable for tracing/retries; non-seekable bodies with tracing path error. `Close` delegates to `httpLogger.Close`, which is nil-safe through the method. Extra headers are deduplicated to avoid retry duplication. HTTP/2 is TLS-only by config.

Test signals: `client_test.go`, `retries_test.go`, `verbose_test.go`, `stats_test.go`, `proxy_test.go`, `certs_test.go`, and `ssh_test.go` cover major behaviors.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/client_test.go -->
# sources/sync-backup/git-lfs/lfshttp/client_test.go

Purpose: Tests core HTTP client setup, redirect safety, request body marshaling, HTTP protocol selection, SSL verification flags, and extra-header deduplication.

Important APIs/types/functions: Exercises `NewClient`, `NewRequest`, `MarshalToRequest`, `Do`, `configureProtocols`, and `ExtraHeadersFor`.

Control flow: Redirect tests build multiple HTTP/TLS servers for local, external, upgrade, and downgrade redirects. Protocol tests use TLS and non-TLS servers to verify HTTP/2 and HTTP/1.1 behavior. Extra-header test applies headers twice to the same request.

State and persistence behavior: Uses in-memory client transport caches and server counters. Request bodies are marshaled to seekable byte readers and reused through redirects.

Dependencies and integration points: Covers `httptest`, TLS settings, `config.Environment`, URL-specific `http.version`, and `http.extraHeader`.

Risks and edge cases: Confirms Authorization survives same-host redirects but is stripped cross-host, and HTTPS-to-HTTP redirect is refused. Confirms bad HTTP version config fails before requests.

Test signals: Strong signal for redirect and transport policy. Does not cover activity timeout deadlines or cookie jars.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/client_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/cookies.go -->
# sources/sync-backup/git-lfs/lfshttp/cookies.go

Purpose: Enables host-specific cookie jar loading from Git config.

Important APIs/types/functions: `isCookieJarEnabledForHost` and `getCookieJarForHost`.

Control flow: Checks `http.https://<host>.cookieFile` via URL config. If configured, expands the path and loads a cookie jar file with `cookiejarparser`.

State and persistence behavior: Reads a configured cookie file and returns an in-memory `http.CookieJar`. No writes.

Dependencies and integration points: Used by `Client.HttpClient` after transport construction. Depends on `tools.ExpandPath` and `github.com/ssgelm/cookiejarparser`.

Risks and edge cases: Only checks HTTPS host key form. Load errors are logged in `HttpClient` and do not fail client creation.

Test signals: No direct tests in this subset; behavior is only indirectly covered if `HttpClient` cookie configuration is exercised elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/cookies.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/endpoint.go -->
# sources/sync-backup/git-lfs/lfshttp/endpoint.go

Purpose: Defines endpoint metadata and URL conversion helpers for HTTP, SSH, bare SSH, local path, and file URL remotes.

Important APIs/types/functions: `Endpoint`, `UrlUnknown`, `endpointOperation`, `EndpointFromSshUrl`, `EndpointFromBareSshUrl`, `EndpointFromHttpUrl`, `EndpointFromLocalPath`, and `EndpointFromFileUrl`.

Control flow: SSH URL parsing extracts user/host, optional port, path, original URL, and derives an HTTPS fallback URL. Bare SSH URLs are rewritten to `ssh://` form, supporting bracketed host:port. HTTP and file URLs pass through. Local paths are rewritten through Git path helpers.

State and persistence behavior: Pure value construction; no state persists.

Dependencies and integration points: Used by `lfsapi.EndpointFinder` and `lfshttp.Client.NewRequest`. Integrates with `ssh.SSHMetadata` and `git.RewriteLocalPathAsURL`.

Risks and edge cases: Bare SSH parsing uses colon splitting and special handling for bracketed ports; unusual paths containing additional colons may be fragile. Invalid SSH hosts yield `UrlUnknown`.

Test signals: Covered extensively by `endpoint_finder_test.go` through endpoint parsing and suffix derivation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/endpoint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/errors.go -->
# sources/sync-backup/git-lfs/lfshttp/errors.go

Purpose: Converts HTTP responses into typed Git LFS errors with decoded server messages and status-specific defaults.

Important APIs/types/functions: `IsHTTP`, `ClientError`, `handleResponse`, `statusCodeError`, `NewStatusCodeError`, and `defaultError`.

Control flow: `handleResponse` returns nil for status <400, attempts JSON decode into `ClientError`, falls back to default status messages, then wraps selected statuses as auth, unprocessable, retriable/rate-limit, or fatal errors.

State and persistence behavior: Reads and closes response bodies through `DecodeJSON`. No persistence.

Dependencies and integration points: Used by `Client.do` and redirect handling. Integrates with shared `errors` categories and `lfshttp.DecodeJSON`.

Risks and edge cases: Decoding consumes and closes the response body. Non-JSON error bodies are ignored and replaced with defaults. 500 is fatal except 501, 507, and 509; 429 may become retriable-later based on `Retry-After`.

Test signals: `response_test.go` covers auth/fatal/nonfatal body and no-body paths. Other statuses are not directly tested here.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/lfshttp.go -->
# sources/sync-backup/git-lfs/lfshttp/lfshttp.go

Purpose: Defines HTTP context abstraction and JSON response decoding rules for LFS HTTP APIs.

Important APIs/types/functions: `Context`, `NewContext`, `testContext`, `IsDecodeTypeError`, `decodeTypeError`, and `DecodeJSON`.

Control flow: `NewContext` supplies default Git config and map-backed envs. `DecodeJSON` accepts only Git LFS JSON or generic JSON media types, decodes response body into the target object, closes the body, and wraps parse errors.

State and persistence behavior: Context holds config and env maps in memory. Decode consumes response bodies.

Dependencies and integration points: Used throughout `lfshttp` and `lfsapi` tests, lock API decoding, and error handling. Depends on `git.Configuration`, `config.Environment`, and shared errors.

Risks and edge cases: Empty or unexpected content type returns a typed decode error without consuming body. JSON parse errors include request method and URL context.

Test signals: Covered indirectly by response and locking tests. No standalone tests for media type regex edge cases in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/lfshttp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/proxy.go -->
# sources/sync-backup/git-lfs/lfshttp/proxy.go

Purpose: Selects HTTP/S proxy settings from environment and Git config with Git LFS-specific localhost and SOCKS handling.

Important APIs/types/functions: `proxyFromClient` and `getProxyServers`.

Control flow: Per request, reads HTTPS/HTTP proxy and no-proxy values, lets URL-specific or global Git `http.proxy` override environment, normalizes `socks5h://` to `socks5://`, and delegates matching to `httpproxy.Config.ProxyFunc`. Localhost is rewritten to `127.0.0.1` to permit proxying.

State and persistence behavior: Stateless aside from reading client URL config and OS env.

Dependencies and integration points: Used by `Client.Transport`. Depends on `config.URLConfig`, `config.Environment`, and `golang.org/x/net/http/httpproxy`.

Risks and edge cases: `getProxyServers` returns nothing when OS env is nil, even if URL config is present. HTTP requests do not use `HTTPS_PROXY`; they require `HTTP_PROXY` or Git proxy. No-proxy wildcard behavior delegates to `httpproxy`.

Test signals: `proxy_test.go` covers env and Git config precedence, URL-specific config, no-proxy, wildcard, SOCKS, and nil proxy behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/proxy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/proxy_test.go -->
# sources/sync-backup/git-lfs/lfshttp/proxy_test.go

Purpose: Tests proxy selection precedence and no-proxy behavior.

Important APIs/types/functions: Exercises `NewClient`, `proxyFromClient`, and generated proxy functions.

Control flow: Each test builds a client with env/config proxy settings, creates a request, invokes the proxy function, and asserts returned proxy URL or nil.

State and persistence behavior: Uses map-backed env/config only; no external state.

Dependencies and integration points: Validates integration with Git URL config and `httpproxy` matching.

Risks and edge cases: Confirms Git config overrides environment, URL-specific proxy overrides global, `NO_PROXY` suppresses proxy, wildcard no-proxy works, and `socks5h` is normalized.

Test signals: Good coverage for proxy decision logic. It does not test lowercase env variables separately beyond implementation paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/proxy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/retries.go -->
# sources/sync-backup/git-lfs/lfshttp/retries.go

Purpose: Stores per-request network retry counts in request context.

Important APIs/types/functions: `ckey`, `contextKeyRetries`, `defaultRequestRetries`, `WithRetries`, and `Retries`.

Control flow: `WithRetries` returns a cloned request with retry count in context. `Retries` reads and type-asserts the value.

State and persistence behavior: Request context carries retry state in memory. No global state.

Dependencies and integration points: Used by `Client.DoWithRedirect` to retry network errors and rewind seekable bodies. Default retries are zero unless annotated.

Risks and edge cases: Negative retry counts are normalized by caller with `max(0, retries)`. Non-seekable bodies may not replay correctly on retry.

Test signals: `retries_test.go` covers context storage, absence, and successful retry of a POST body after dropped connections.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/retries.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/retries_test.go -->
# sources/sync-backup/git-lfs/lfshttp/retries_test.go

Purpose: Tests request retry annotation and body replay after transient network failures.

Important APIs/types/functions: Exercises `WithRetries`, `Retries`, `Client.Do`, and `MarshalToRequest`.

Control flow: The retry integration test runs a server that hijacks and closes the first two connections, then returns success on the third request. The client sends a JSON POST with retry count high enough to succeed.

State and persistence behavior: Uses atomic request counter and in-memory request context. The seekable body is rewound between failed attempts.

Dependencies and integration points: Integrates retry context with `DoWithRedirect`, request tracing, and `httptest` raw connection hijacking.

Risks and edge cases: Test skips if the server cannot hijack raw connections. It verifies body replay but not retry exhaustion error shape.

Test signals: Strong signal that retries preserve JSON body content across network-level failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/retries_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/ssh.go -->
# sources/sync-backup/git-lfs/lfshttp/ssh.go

Purpose: Resolves SSH-based LFS authentication into HTTPS href/header data and optionally caches responses.

Important APIs/types/functions: `SSHResolver`, `withSSHCache`, `sshCache`, `sshCache.Resolve`, `sshAuthResponse`, `IsExpiredWithin`, `sshAuthClient`, and `sshAuthClient.Resolve`.

Control flow: Cache lookup keys by user/host, port, path, and method. Non-expired entries are returned; expired/missing entries delegate to the wrapped resolver. The concrete resolver executes `git-lfs-authenticate`, captures stdout/stderr, decodes JSON on success, stores creation time, and applies default token TTL if no expiry is provided.

State and persistence behavior: `sshCache` uses `sync.Map` for in-process cache. External SSH command execution may consult user SSH/config state. No files written here.

Dependencies and integration points: Used by `Client.NewRequest` through `sshResolveWithRetries`. Depends on `ssh.GetLFSExeAndArgs`, `subprocess.ExecCommand`, `tools.IsExpiredAtOrIn`, Git env, and tracer logging.

Risks and edge cases: Cache only stores successful resolutions. Expiration considers a five-second safety window in caller. Ambiguous expiry fields defer to helper semantics. Command stderr becomes `Message` for wrapped errors.

Test signals: `ssh_test.go` covers cache hits, expiry by `expires_at` and `expires_in`, concurrent resolves under race detector, and error non-caching.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/ssh.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/ssh_test.go -->
# sources/sync-backup/git-lfs/lfshttp/ssh_test.go

Purpose: Tests SSH auth cache behavior, expiry semantics, error handling, and concurrent access.

Important APIs/types/functions: Exercises `withSSHCache`, `sshCache.Resolve`, `sshAuthResponse.IsExpiredWithin`, fake `SSHResolver`, and `sync.Map` cache storage.

Control flow: Tests seed cache entries or fake resolver responses, call `Resolve`, and assert whether cached or real response is returned. Concurrency test starts two goroutines resolving the same endpoint.

State and persistence behavior: Cache state is in memory. Fake resolver stores responses in a map, while cache stores successful responses in `sync.Map`.

Dependencies and integration points: Validates `ssh.SSHMetadata` keying and shared `errors` wrapping for failed fake resolution.

Risks and edge cases: Covers expired entries being bypassed but not deleted. Ambiguous expiration with future `expires_in` and past `expires_at` still returns cache.

Test signals: Good race-safety signal for cache map access. It does not run real `git-lfs-authenticate`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/ssh_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/standalone/standalone.go -->
# sources/sync-backup/git-lfs/lfshttp/standalone/standalone.go

Purpose: Implements the standalone `file://` transfer agent protocol for copying LFS objects between local repositories without an API server.

Important APIs/types/functions: `inputMessage`, `errorMessage`, `outputErrorMessage`, `completeMessage`, `fileHandler`, `fileUrlFromRemote`, `gitDirAtPath`, `fixUrlPath`, `newHandler`, `dispatch`, `respond`, `upload`, `download`, and `ProcessStandaloneData`.

Control flow: `ProcessStandaloneData` reads newline-delimited JSON messages, creates a handler from the first message's remote, dispatches init/upload/download/terminate, and writes JSON responses. Upload links/copies local object into remote object storage unless already present. Download verifies remote object existence, creates a temp output path, and links/copies from remote object storage.

State and persistence behavior: Reads config/remotes and remote Git object storage. Writes uploaded objects to remote filesystem, creates temporary download files under configured temp dir, and removes handler temp dir at end. `gitDirAtPath` temporarily changes process cwd while invoking `git rev-parse`.

Dependencies and integration points: Integrates `config.Configuration`, `lfsapi.EndpointFinder`, `lfs.LinkOrCopy`, remote LFS filesystem, `subprocess.ExecCommand`, Git executable, and transfer-agent JSON protocol.

Risks and edge cases: Process-wide `os.Chdir` is risky if called concurrently. Only `file://` remotes are accepted. Windows URL path handling is special-cased. Handler creation failures are reported as JSON error messages before returning.

Test signals: No direct tests in this subset; behavior depends on integration coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/standalone/standalone.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/stats.go -->
# sources/sync-backup/git-lfs/lfshttp/stats.go

Purpose: Logs HTTP transfer timing and body-size statistics for requests and responses.

Important APIs/types/functions: `httpTransfer`, `LogHTTPStats`, `LogRequest`, `syncLogger`, `syncLogger.LogRequest`, `syncLogger.LogResponse`, `logTransfer`, and `Close`.

Control flow: `LogHTTPStats` writes a header and installs an async logger. `LogRequest` attaches `httptrace.ClientTrace` callbacks to a request context. Traced request/response bodies call logger methods from verbose tracing when bytes are read. `syncLogger` serializes log lines through a buffered channel and wait group.

State and persistence behavior: Writes log lines to the provided `io.WriteCloser`. Transfer timing state is in request context and updated atomically.

Dependencies and integration points: Integrated by `Client.LogRequest`, `verbose.go` traced bodies, and transfer code needing HTTP stats. Uses `httptrace`, atomics, and `UserAgent`.

Risks and edge cases: Response stats are emitted only when the response body reaches EOF. If callers do not drain/close bodies, response lines may be missing. The logger wait-group pattern requires `Close` for flush.

Test signals: `stats_test.go` covers enabled with key, enabled without request key, and disabled behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/stats_test.go -->
# sources/sync-backup/git-lfs/lfshttp/stats_test.go

Purpose: Tests HTTP stats logging header, request/response log lines, and disabled no-op behavior.

Important APIs/types/functions: Exercises `LogHTTPStats`, `LogRequest`, `Client.Do`, `syncLogger.Close`, and `nopCloser`.

Control flow: Test servers accept JSON POSTs, clients optionally enable logging, requests optionally carry a stats key, and tests drain response bodies before closing the client to flush logs.

State and persistence behavior: Logs write to in-memory buffers. Atomic server counters verify request counts.

Dependencies and integration points: Validates interplay between stats tracing, verbose traced response body wrapping, and JSON request body marshaling.

Risks and edge cases: Confirms no per-request lines are emitted without `LogRequest` key/context, only the header. Disabled logging leaves `LogStats` empty.

Test signals: Good coverage of log shape and flush behavior. Does not assert exact timing values.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/stats_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/verbose.go -->
# sources/sync-backup/git-lfs/lfshttp/verbose.go

Purpose: Implements HTTP trace output for requests and responses, including body tracing for textual content and redaction of Basic auth by default.

Important APIs/types/functions: `traceRequest`, `tracedRequest`, `traceResponse`, `tracedResponse`, `tracedRead`, `traceHTTPDump`, `isTraceableContent`, and `traceReq`.

Control flow: `traceRequest` logs method/URL, optionally dumps request headers, validates body seekability, rewinds body, and wraps it for size accounting and optional textual output. `traceResponse` logs status, wraps body to trace reads and stats, and optionally dumps response headers. `traceHTTPDump` prefixes lines and redacts Basic Authorization unless debugging verbose is enabled.

State and persistence behavior: Mutates `req.Body` and `res.Body` wrappers in memory. Writes verbose output to `VerboseOut` and tracer logs. Response stats emit on EOF.

Dependencies and integration points: Works with `lfshttp.Client.DoWithRedirect`, `stats.go`, `httputil.Dump*`, and `tracerx`.

Risks and edge cases: Request bodies must implement `ReadSeekCloser`; non-seekable non-nil bodies return an error. Binary content bodies are not printed, but headers still are. Redaction is specific to Basic authorization lines.

Test signals: `verbose_test.go` covers verbose text output, binary body suppression, redaction, debugging mode unredaction, and disabled output.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/verbose.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/verbose_test.go -->
# sources/sync-backup/git-lfs/lfshttp/verbose_test.go

Purpose: Tests verbose HTTP logging output, body filtering, and Authorization redaction controls.

Important APIs/types/functions: Exercises `Client.Do`, `MarshalToRequest`, `traceRequest`, `traceResponse`, `traceHTTPDump`, and `isTraceableContent`.

Control flow: Test servers validate requests and return JSON or binary responses. Tests configure `Verbose`, `VerboseOut`, and `DebuggingVerbose`, then inspect emitted dump strings.

State and persistence behavior: Uses in-memory output buffers and temporary test servers. No persistent state.

Dependencies and integration points: Validates interaction with JSON request bodies, response body draining, and HTTP dump formatting.

Risks and edge cases: Confirms Basic auth is redacted by default and visible only in debugging verbose mode. Confirms binary request/response body bytes are not printed.

Test signals: Strong coverage for user-visible verbose output. It does not test non-seekable body error handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/lfshttp/verbose_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/api.go -->
# sources/sync-backup/git-lfs/locking/api.go

Purpose: Implements Git LFS locking API clients for HTTP and dispatch to pure SSH lock transfer when available.

Important APIs/types/functions: `lockClient`, `httpLockClient`, `lockRequest`, `lockResponse`, `unlockRequest`, `unlockResponse`, `lockSearchRequest.QueryValues`, `lockList`, `lockVerifiableRequest`, `lockVerifiableList`, `User`, `genericLockClient`, and lock methods `Lock`, `Unlock`, `Search`, `SearchVerifiable`.

Control flow: HTTP methods choose upload/download endpoints, build requests with `lfsapi.Client.NewRequest`, log request keys, execute through `DoAPIRequestWithAuth`, decode JSON on success, and return response/status/error. `genericLockClient` memoizes per remote/operation client, choosing SSH lock client if `Client.SSHTransfer` succeeds, otherwise HTTP.

State and persistence behavior: No lock persistence here beyond remote API effects. `genericLockClient` caches selected lock clients in memory. `SetAccess`/auth side effects happen in `lfsapi`.

Dependencies and integration points: Integrates `lfsapi.Client`, `lfshttp.DecodeJSON`, Git refs, locking schema types, and pure SSH lock client implementation outside this file.

Risks and edge cases: `Unlock` always dereferences `ref.Refspec()`, so callers must pass a non-nil ref. Lock/unlock require either a lock object or server message; otherwise response is invalid. Search only decodes JSON on HTTP 200, preserving status for non-OK responses.

Test signals: `api_test.go` covers request shape, JSON schemas, status propagation, query parameters, and response decoding for HTTP paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/api_test.go -->
# sources/sync-backup/git-lfs/locking/api_test.go

Purpose: Tests HTTP locking API request/response shapes against JSON schemas.

Important APIs/types/functions: Exercises `httpLockClient.Lock`, `Unlock`, `Search`, `SearchVerifiable`, schema loaders, and `assertSchema`.

Control flow: Test servers assert path, method, headers, body content, and query parameters. Responses are encoded through schema writer loaders and decoded by the client. Schema fixtures are loaded during package init from `schemas/*.json`.

State and persistence behavior: Uses in-memory test servers and schema objects. No remote state persists beyond request counters implicit in handlers.

Dependencies and integration points: Integrates locking API with `lfsapi.NewClient`, `lfshttp.NewContext`, `gojsonschema`, and Git ref formatting.

Risks and edge cases: Schema load failures are printed during init and produce nil schema assertions if not guarded. Tests cover happy paths but not auth errors, conflict responses, invalid server responses, or non-200 search behavior.

Test signals: Strong contract signal for wire format and headers: `Accept`, `Content-Type`, and JSON payload structure.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/api_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/cache.go -->
# sources/sync-backup/git-lfs/locking/cache.go

Purpose: Provides a local two-way cache of locks by path and by encoded lock ID.

Important APIs/types/functions: `LockCache`, `NewLockCache`, `Add`, `RemoveByPath`, `RemoveById`, `Locks`, `Clear`, `Save`, `encodeIdKey`, `decodeIdKey`, and `isIdKey`.

Control flow: `Add` stores the same `Lock` under path and `*id*://<id>`. Removal by either path or id looks up one side and removes both keys. `Locks` visits the KV store and returns only non-id-key entries.

State and persistence behavior: Backed by `tools/kv.Store`; mutations are in the store and `Save` persists to the configured file. `Clear` removes all entries.

Dependencies and integration points: Used by locking client code for fast local lock lookups. Depends on `kv.NewStore` and the `Lock` type.

Risks and edge cases: `Locks` type-asserts stored values to `*Lock`, so store corruption can panic. Duplicate IDs/paths overwrite prior entries. `decodeIdKey` is currently unused in this file.

Test signals: `cache_test.go` covers add, list, remove by path, and remove by id behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/cache_test.go -->
# sources/sync-backup/git-lfs/locking/cache_test.go

Purpose: Tests lock cache add/list/remove behavior.

Important APIs/types/functions: Exercises `NewLockCache`, `Add`, `Locks`, `RemoveByPath`, and `RemoveById`.

Control flow: Creates a temp cache file, adds three locks, asserts listed locks, removes one by path, asserts remaining locks, removes another by id, and asserts final state.

State and persistence behavior: Uses a temporary store file but does not call `Save`; the tested behavior is in-memory store mutation.

Dependencies and integration points: Depends on `Lock` equality through testify `Contains` and `kv.Store` behavior.

Risks and edge cases: Does not test persistence reload, clear, id key encoding idempotence, or store corruption.

Test signals: Basic correctness signal for bidirectional removal.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/lockable.go -->
# sources/sync-backup/git-lfs/locking/lockable.go

Purpose: Manages `.gitattributes` lockable patterns and filesystem write flags for lockable files.

Important APIs/types/functions: `GetLockablePatterns`, `getLockableFilter`, `ensureLockablesLoaded`, `refreshLockablePatterns`, `IsFileLockable`, `FixAllLockableFileWriteFlags`, `FixFileWriteFlagsInDir`, `fixFileWriteFlags`, `FixLockableFileWriteFlags`, and `fixSingleFileWriteFlags`.

Control flow: Lockable patterns are lazily loaded under mutex from Git attributes. File write-flag fixers build filters for lockable/unlockable patterns, enumerate tracked files with `git.NewLsFiles`, and call `tools.SetFileWriteFlag` based on whether a file is lockable and locked by the current committer.

State and persistence behavior: Caches lockable patterns and filter on `Client`. Mutates filesystem permissions by setting files read-only or writable. Reads Git attributes and Git index/tracked-file state.

Dependencies and integration points: Integrates `gitattr`, `filepathfilter`, `git.NewLsFiles`, lock ownership checks through `Client.IsFileLockedByCurrentCommitter`, and `tools.SetFileWriteFlag`.

Risks and edge cases: Permission changes ignore missing files but return other errors. Cached patterns require explicit refresh elsewhere after attribute changes. `fixFileWriteFlags` accepts `absPath` but enumerates from `workingDir`, so directory-scoped behavior depends on `git.NewLsFiles` semantics rather than `absPath` filtering.

Test signals: No direct tests in this subset. Behavior depends on broader locking checkout/attribute integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/lockable.go -->
