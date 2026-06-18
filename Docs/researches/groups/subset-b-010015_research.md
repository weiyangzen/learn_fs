# subset-b-010015 Research

Grouped research report for the SMBJ subset. Each section is source-tree aligned and wrapped for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/SmbFileSystem.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/SmbFileSystem.java

Purpose: `SmbFileSystem` adapts an SMB share to the Java NIO `FileSystem` contract. It owns the provider reference, a `ShareSource`, the share name, a root `SmbPath`, and an `open` flag.

Important APIs and control flow: path creation normalizes `/` to SMB backslashes and returns root, absolute, or relative `SmbPath` instances. Directory listing opens a `DiskShare`, calls `list`, filters `.` and `..`, applies the caller filter, and returns an `SmbDirectoryStream`. File operations translate NIO options into SMB access masks, create dispositions, and create options before opening `File` handles. Copy uses server-side `remoteCopyTo`; move opens with `FILE_WRITE_ATTRIBUTES` and renames; delete opens with `DELETE` and marks delete-on-close.

State, dependencies, and integration: every operation opens the configured share through `ShareSource`; channel lifetime is handed to `SmbFileChannel` with the share holder and SMB file. It depends on SMBJ share primitives, MS-SMB2 create/access enums, and NIO SPI types.

Risks: several NIO surfaces are unimplemented. `checkAccess` only supports existence checks, not modes. Option translation is partial, and same-share copy assumes source and destination are on one share holder. Test signals should cover path parsing, create/truncate/append modes, missing-file exception mapping, remote copy/move/delete, holder closing, and unsupported option behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/SmbFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/SmbFileSystemProvider.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/SmbFileSystemProvider.java

Purpose: `SmbFileSystemProvider` is the NIO service provider for `smb://` URIs. It creates and caches one `SmbFileSystem` per identity, host, and share.

Important APIs and control flow: `newFileSystem` builds a cache key, rejects duplicates, resolves auth from URI user-info and environment properties, selects port 445 by default, and delegates creation to a `Factory`. `getPath` strips the share prefix from the URI path and returns root or a share-relative path. NIO operations mostly validate `SmbPath` and forward to `SmbFileSystem`.

State, dependencies, and integration: `fileSystems` is guarded with synchronization. `FactoryImpl` wires `SMBClient`, `ShareSourceImpl`, host, port, `AuthenticationContext`, and share name. Passwords may come from URI, `String`, or `char[]`.

Risks: cache key omits password, so two credentials with the same identity collide. `removeFileSystem` removes from a map during enhanced iteration, relying on immediate return. Cross-filesystem move copies then deletes, but does not preserve all copy semantics. Many NIO features are unimplemented. Tests should cover URI parsing, env override precedence, duplicate detection, provider mismatch, cross-filesystem fallback, and invalid share URIs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/SmbFileSystemProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/SmbPath.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/SmbPath.java

Purpose: `smbfs.SmbPath` implements Java NIO `Path` for one `SmbFileSystem`, using backslash separators and a root object to distinguish absolute from relative paths.

Important APIs and control flow: factory methods create root, parsed, and element-backed paths. Name accessors derive file name, parent, subpaths, starts/ends-with, sibling resolution, relativization, iteration, comparison, equality, and string rendering. `resolve` returns the suffix unchanged when absolute, otherwise combines element lists under the current root semantics.

State, dependencies, and integration: immutable fields hold the owning filesystem, root reference, and path elements; `elements == null` means root. Provider methods require this exact path type through `requireSmbPath`.

Risks: `normalize`, `toUri`, `toRealPath`, and watch registration are unimplemented. `differentFileSystem` calls `path.getFileSystem()` before type validation and can throw for non-SMB paths. Case-insensitive `compareTo` may not match `equals`. No dot-dot normalization means SMB calls can receive unresolved segments. Tests should cover root/relative/absolute parsing, separator replacement, element validation, starts/ends edge cases, relativize across roots, and unsupported methods.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/SmbPath.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/ToBeImplementedException.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/ToBeImplementedException.java

Purpose: `ToBeImplementedException` is a package-local helper for explicit unsupported SMB filesystem SPI methods.

Important APIs and control flow: the private constructor prevents arbitrary message variants; static `toBeImplemented()` returns a new `UnsupportedOperationException` subclass.

State, dependencies, and integration: it has no state. It is statically imported throughout `smbfs` to mark unsupported NIO operations such as file stores, watch services, attribute views, path matching, and unsupported options.

Risks: the exception has no message, so failures can be opaque. Tests should assert unsupported paths throw this subtype or `UnsupportedOperationException` as expected, while supported NIO flows never route here unexpectedly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbfs/ToBeImplementedException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/GSSContextConfig.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/GSSContextConfig.java

Purpose: `GSSContextConfig` carries client-side GSS/SPNEGO context flags used by `SpnegoAuthenticator`.

Important APIs and control flow: `createDefaultConfig()` builds mutual authentication enabled and credential delegation disabled. Builder setters mutate a temporary config, and `build()` returns a defensive copy.

State, dependencies, and integration: it stores only `requestMutualAuth` and `requestCredDeleg`; additional GSS options are noted but not implemented. `SmbConfig` embeds it and passes it to SPNEGO authentication.

Risks: limited GSS controls may prevent configuring replay, sequence, confidentiality, integrity, or lifetime behavior. Tests should verify defaults, builder copy behavior, and that `SpnegoAuthenticator` applies both exposed options to the `GSSContext`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/GSSContextConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/ProgressListener.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/ProgressListener.java

Purpose: `ProgressListener` is a minimal callback interface for reporting API progress in bytes.

Important APIs and control flow: implementers receive `onProgressChanged(long numBytes, long totalBytes)`.

State, dependencies, and integration: it is stateless and can be used by transfer operations elsewhere in SMBJ to surface copy/read/write progress.

Risks: no threading, monotonicity, or error contract is specified. Tests should verify callers pass expected byte counts and tolerate listeners that observe total size boundaries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/ProgressListener.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/SMBClient.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/SMBClient.java

Purpose: `SMBClient` is the top-level public client API and connection pool for SMB servers.

Important APIs and control flow: `connect(host)` and `connect(host, port)` look up `host:port`, lease an existing connected `Connection` if possible, otherwise construct and connect a new one. It subscribes to `SMBEventBus`; `ConnectionClosed` removes cached connections and unregisters the server. `close()` force-closes remaining connections.

State, dependencies, and integration: state is held in a concurrent connection table, `ServerList`, `SmbConfig`, and event bus. Connection creation injects config, client, bus, and server list.

Risks: pooling depends on `Connection.lease()` and event delivery; stale connections must be removed reliably. `close()` iterates current values without clearing the map directly. Tests should cover connection reuse, failed connect cleanup, close behavior, event-driven removal, and concurrent connect calls for the same host.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/SMBClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/SmbConfig.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/SmbConfig.java

Purpose: `SmbConfig` is the immutable runtime configuration for SMB connections, negotiation, security, authentication, transport, and IO sizing.

Important APIs and control flow: `builder()` establishes defaults: SMB 3.1.1 through 2.0.2 dialects, signing enabled, DFS disabled, direct TCP transport, proxy socket factory, 1 MiB buffers, 60 second operation timeouts, BC security provider, GSS config, NTLM config, and default authenticators. The builder validates non-null components, positive sizes, socket timeout bounds, dialect presence, signing invariants, SMB3 signing restrictions, and encryption requiring SMB3-compatible dialects.

State, dependencies, and integration: config exposes defensive copies for dialects and authenticators. Default authenticators load SPNEGO reflectively outside Android, then add NTLM. Client capabilities are derived from SMB3 support, DFS, and encryption.

Risks: reflective SPNEGO factory failure aborts default config. `Random` and mutable factories are shared by reference. Disabling signing is forbidden for SMB3 dialects but defaults include SMB3, so tests must account for invariant interactions. Test signals include default values, builder copy isolation, capability derivation, authenticator ordering, timeout conversion, and invalid configuration failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/SmbConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/AuthenticateResponse.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/AuthenticateResponse.java

Purpose: `AuthenticateResponse` is the mutable handoff object returned by authenticators during session setup.

Important APIs and control flow: it carries a SPNEGO token, session key, Windows version, NetBIOS name, and NTLM negotiate flags. Constructors allow an empty response or token-initialized response.

State, dependencies, and integration: `SMBSessionBuilder` serializes `negToken`, stores `sessionKey`, and copies server metadata into `ConnectionContext`. NTLM and SPNEGO authenticators populate different fields.

Risks: byte arrays and negotiate flag sets are not defensively copied, so callers can mutate secrets or flags after publication. Tests should verify each authenticator populates required fields for each authentication phase and handles null session keys.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/AuthenticateResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/AuthenticationContext.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/AuthenticationContext.java

Purpose: `AuthenticationContext` stores username, password, and domain for NTLM-style authentication.

Important APIs and control flow: constructor copies the provided password into an internal `char[]`; factories create anonymous and guest contexts. `isAnonymous` and `isGuest` are used by authenticators and signing logic to choose flags and session behavior.

State, dependencies, and integration: fields are final, but `getPassword()` returns the internal array. `SmbFileSystemProvider` creates instances from URI/env values, and `NtlmAuthenticator` consumes them.

Risks: returning the password array exposes mutable secret state, and `username` may be null if callers pass null. Tests should cover defensive construction, anonymous/guest detection, URI-derived values, and string representation not leaking passwords.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/AuthenticationContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/Authenticator.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/Authenticator.java

Purpose: `Authenticator` defines the session-setup authentication strategy interface.

Important APIs and control flow: `init(SmbConfig)` prepares per-authenticator state, `supports(AuthenticationContext)` selects compatible contexts, and `authenticate(context, gssToken, connectionContext)` consumes a server token and returns the next token/session key response or `null` when complete.

State, dependencies, and integration: implementations are created through named factories configured in `SmbConfig`, selected by `SMBSessionBuilder`, and may be stateful across token exchanges.

Risks: the interface assumes one authenticator instance per session setup; sharing instances would corrupt state. Tests should use fake authenticators to verify selection, multi-step token exchange, and failure propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/Authenticator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/ExtendedGSSContext.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/ExtendedGSSContext.java

Purpose: `ExtendedGSSContext` reflectively accesses vendor-specific JGSS extensions to retrieve the Kerberos session key.

Important APIs and control flow: static initialization locates either Sun or IBM `ExtendedGSSContext` and `InquireType`, resolves `KRB5_GET_SESSION_KEY`, and stores the reflective method. `krb5GetSessionKey` invokes it and wraps failures in `TransportException`.

State, dependencies, and integration: it is used by `SpnegoAuthenticator` after GSS context establishment to obtain the SMB session key.

Risks: unsupported JVMs fail class initialization with `IllegalStateException`. Reflective access may break under module restrictions or vendor differences. Tests should isolate supported and unsupported JVM paths, invocation failures, and key extraction behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/ExtendedGSSContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/GSSAuthenticationContext.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/GSSAuthenticationContext.java

Purpose: `GSSAuthenticationContext` extends `AuthenticationContext` for Kerberos/SPNEGO authentication using a JAAS `Subject` and optional `GSSCredential`.

Important APIs and control flow: constructor stores username/domain with an empty password, plus subject and credentials. Getters expose both GSS objects. `toString` identifies the subject rather than password data.

State, dependencies, and integration: `SpnegoAuthenticator.supports` requires this exact class and runs authentication inside `Subject.doAs`.

Risks: subject and credentials are package-private mutable references. Tests should verify SPNEGO selection, subject propagation, and failure when a plain `AuthenticationContext` is offered to SPNEGO.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/GSSAuthenticationContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/NtlmAuthenticator.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/NtlmAuthenticator.java

Purpose: `NtlmAuthenticator` implements NTLMSSP over SPNEGO for SMB session setup.

Important APIs and control flow: after `init`, state starts at `NEGOTIATE`. First `authenticate` builds NTLM negotiate flags, serializes `NtlmNegotiate` into `NegTokenInit`, and moves to `AUTHENTICATE`. The next call parses `NegTokenTarg`, reads `NtlmChallenge`, intersects flags with server support, requires 128-bit encryption, computes NTLMv2 response and session key, optionally encrypts a random exported session key, calculates MIC when target-info flags require it, and returns `NtlmAuthenticate` in `NegTokenTarg`.

State, dependencies, and integration: it holds security provider, random, NTLM config, NTLMv2 functions, current flags, and the original negotiate message for MIC. It supports only exact `AuthenticationContext`, while `NtlmSealer` may wrap it.

Risks: stateful instances cannot be reused. Anonymous/guest flag handling is subtle. MIC and target-info behavior has TODOs. Tests should cover negotiate flag composition, challenge parsing, unsupported 128-bit failure, anonymous and guest paths, MIC calculation, session-key derivation, and state completion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/NtlmAuthenticator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/NtlmSealer.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/NtlmSealer.java

Purpose: `NtlmSealer` wraps `NtlmAuthenticator` to add NTLM Extended Session Security signing/sealing for SPNEGO mech-list MIC.

Important APIs and control flow: it delegates authentication, derives signing and sealing keys from the exported session key when present, records negotiated mech types from `NegTokenInit`, and on `NegTokenTarg` signs the DER-encoded mech list using a sequence number. If key exchange is negotiated, it RC4-encrypts the signature before storing it as mech-list MIC.

State, dependencies, and integration: it stores derived keys, an atomic sequence number, mech types, wrapped authenticator, and security provider. `SMBSessionBuilder` inserts this wrapper when NTLM integrity is enabled.

Risks: only client-to-server constants are implemented. `mechTypes` must be captured before signing target tokens. Legacy sealing key branches depend on Windows version. Tests should cover wrapper selection, DER mech-list signing, sequence increment, key-exchange encryption, and no-op behavior before session key exists.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/NtlmSealer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/SpnegoAuthenticator.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/SpnegoAuthenticator.java

Purpose: `SpnegoAuthenticator` performs Kerberos/SPNEGO authentication using Java GSS APIs.

Important APIs and control flow: `authenticate` casts to `GSSAuthenticationContext` and executes inside its `Subject`. On first token it creates a `GSSContext` for `cifs@server`, applies mutual-auth and delegation flags, then calls `initSecContext`. It returns a raw SPNEGO token and, when established, queries the Kerberos session key and pads/truncates it to SMB's 16-byte requirement.

State, dependencies, and integration: it stores one `GSSContext` and `GSSContextConfig`. `SMBSessionBuilder` chooses it through the configured factory OID and GSS context type.

Risks: exact class casts mean misuse fails at runtime. `adjustSessionKeyLength` fills to `SIGNATURE_SIZE - 1`, which should be checked for off-by-one padding. Tests should cover multi-token GSS flows with fakes, key length adjustment, config flag application, and GSS exception wrapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/auth/SpnegoAuthenticator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/common/Check.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/common/Check.java

Purpose: `Check` centralizes small assertion helpers.

Important APIs and control flow: `ensureEquals(byte[], byte[], message)` throws `IllegalArgumentException` on byte mismatch; `ensure(condition, message)` throws `IllegalStateException` on false.

State, dependencies, and integration: stateless utility depending only on `Arrays`.

Risks: exception types differ by helper, so callers must match intent. Tests should verify exact exception types and messages for validation paths that use this utility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/common/Check.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/common/Pooled.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/common/Pooled.java

Purpose: `Pooled` provides reference-count style leasing for reusable objects such as `Connection`.

Important APIs and control flow: instances start with one lease. `lease()` increments and returns `this` if the previous count was positive, otherwise returns null. `release()` decrements and returns true when the count reaches zero or below.

State, dependencies, and integration: it uses an `AtomicInteger`; subclasses use the generic self type.

Risks: `lease()` increments even when the object is already closed, making the counter less intuitive after zero. Multiple releases can drive negative counts. Tests should cover concurrent lease/release behavior, close-on-last-release, and no resurrection after close.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/common/Pooled.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/common/SMBException.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/common/SMBException.java

Purpose: `SMBException` is the checked IOException base for SMB-level failures.

Important APIs and control flow: constructors accept message or cause. The static `Wrapper` preserves existing `SMBException` instances and wraps other throwables.

State, dependencies, and integration: used with SMBJ future utilities that require an `ExceptionWrapper`.

Risks: cause-only constructor has no message except the cause string. Tests should verify wrapper idempotency and integration with futures that convert asynchronous errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/common/SMBException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/common/SMBRuntimeException.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/common/SMBRuntimeException.java

Purpose: `SMBRuntimeException` is the unchecked SMBJ exception wrapper for internal and asynchronous failures.

Important APIs and control flow: constructors accept cause, message, or both. The static `Wrapper` preserves existing runtime exceptions and wraps other throwables.

State, dependencies, and integration: used by promises, IO chunk providers, crypto helpers, and negotiation/session code for failures that cannot be expressed as checked exceptions.

Risks: broad wrapping can obscure original checked exception semantics. Tests should verify wrapper behavior and that critical transport/security failures retain causes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/common/SMBRuntimeException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/common/SmbPath.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/common/SmbPath.java

Purpose: `smbj.common.SmbPath` is a lightweight UNC path value object distinct from the NIO `smbfs.SmbPath`.

Important APIs and control flow: constructors accept host, share, and optional path, rewriting `/` to `\` and trimming leading UNC separators. Child construction requires a fully specified parent share. `toUncPath` emits `\\host\share\path`, and `parse` splits host/share/path into up to three parts.

State, dependencies, and integration: immutable fields hold hostname, share name, and path. Helpers expose parent, same-host, and same-share checks.

Risks: equality is case-sensitive even though SMB host/share comparisons may be case-insensitive in practice. `getParent` returns itself for share roots. Tests should cover parsing leading slashes, child construction, UNC rendering, parent edge cases, and same-host/share comparisons.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/common/SmbPath.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/Connection.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/Connection.java

Purpose: `Connection` is the live transport/session coordinator for one SMB server connection.

Important APIs and control flow: construction creates the transport and packet handler chain. `connect` opens the socket, creates `ConnectionContext`, negotiates dialect, initializes encryption, and selects local or DFS path resolving. `authenticate` delegates session establishment to `SMBSessionBuilder`. `send` assigns credits and message IDs under a lock, registers an outstanding request, writes the packet, and returns a cancellable future. Incoming packets are passed through the handler chain.

State, dependencies, and integration: it owns `SessionTable`, preauth session table, `OutstandingRequests`, `SequenceWindow`, signatory, encryptor, transport, event bus, server list, and path resolver. It extends `Pooled` for client connection reuse.

Risks: send ordering and credit accounting are concurrency-sensitive. Cancel assumes the session is still present. Forced close skips session logoff. Test signals include negotiation, request registration/removal, credit assignment, cancellation, error propagation to outstanding requests, close events, packet handler ordering, and DFS resolver selection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/Connection.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/ConnectionContext.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/ConnectionContext.java

Purpose: `ConnectionContext` stores negotiated connection metadata and capability decisions.

Important APIs and control flow: constructed with client GUID, server address, and client config. `negotiated` installs the negotiated response, server object, `NegotiatedProtocol`, cipher, compression algorithms, preauth hash data, and server time offset. Capability helpers report signing, encryption, DFS, leasing, multichannel, and multicredit support.

State, dependencies, and integration: it references a `Server`, client capabilities, negotiated protocol, SMB 3.1.1 preauth fields, cipher, compression ids, Windows version, and NetBIOS name. It feeds session setup, encryption, signing, and path resolution.

Risks: `supportsMultiCredit()` consults server capabilities before `negotiatedProtocol` is initialized, which is intentional during negotiation but fragile. GSS negotiate token remains empty in this code. Tests should verify capability derivation for SMB2, SMB3, and SMB3.1.1, time offset, preauth defaults, and encryption preference logic.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/ConnectionContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/NegotiatedProtocol.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/NegotiatedProtocol.java

Purpose: `NegotiatedProtocol` is an immutable summary of the chosen SMB dialect and negotiated IO limits.

Important APIs and control flow: constructor stores dialect and max transact/read/write sizes. If multi-credit is not supported, sizes are clamped with `Math.max(..., SINGLE_CREDIT_PAYLOAD_SIZE)`.

State, dependencies, and integration: `ConnectionContext` exposes it to sessions, shares, and send-size calculations.

Risks: the clamping direction should be reviewed against protocol intent; single-credit connections usually need an upper bound, not a larger minimum. Tests should cover size behavior with and without multicredit and dialect propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/NegotiatedProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/NoSignatory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/NoSignatory.java

Purpose: `NoSignatory` is the null-object implementation of packet signing.

Important APIs and control flow: `sign` returns the original packet and `verify` always returns true.

State, dependencies, and integration: `Connection` installs it when signing is disabled in config.

Risks: safe only when config/protocol invariants permit unsigned packets. Tests should verify it leaves packets untouched and that SMB3 configs cannot disable signing through `SmbConfig`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/NoSignatory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/OutstandingRequests.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/OutstandingRequests.java

Purpose: `OutstandingRequests` tracks sent requests awaiting responses and cancellation lookup.

Important APIs and control flow: read lock methods check and retrieve by message ID or cancel ID. `registerOutstanding` inserts into both maps. `receivedResponseFor` removes from both maps and throws if missing. `handleError` drains all requests and delivers the error to their promises.

State, dependencies, and integration: protected by `ReentrantReadWriteLock`; used by `Connection.send` and packet handlers.

Risks: duplicate message IDs overwrite prior requests. Missing responses become runtime exceptions. Tests should cover concurrent registration/response, cancellation lookup, duplicate handling expectations, and error fan-out.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/OutstandingRequests.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/PacketEncryptor.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/PacketEncryptor.java

Purpose: `PacketEncryptor` wraps SMB2 packets into SMB3 transform packets and decrypts SMB3 encrypted packet data.

Important APIs and control flow: `init` chooses SMB3.1.1 negotiated cipher or AES-128-CCM for older SMB3. `canDecrypt` checks dialect, remaining payload, and algorithm flag. `decrypt` builds AAD from the transform header, decrypts with AEAD, and combines update/final plaintext. `encrypt` returns an `EncryptedPacketWrapper` that serializes plaintext, creates a nonce and transform header, authenticates header fields, encrypts, stores the 16-byte tag as signature, then writes ciphertext.

State, dependencies, and integration: depends on `SecurityProvider`, negotiated dialect/cipher, `SMB2TransformHeader`, and session encryption/decryption keys. Used by `Connection` and `SMB3DecryptingPacketHandler`.

Risks: nonce generation uses `System.nanoTime` and an unused counter, so uniqueness across processes/keys deserves review. AEAD parameter class is `GCMParameterSpec` even for CCM provider abstractions. Tests should cover AAD bytes, encrypt/decrypt round trip, nonce length per cipher, malformed packet rejection, and missing keys.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/PacketEncryptor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/PacketSignatory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/PacketSignatory.java

Purpose: `PacketSignatory` signs outgoing SMB2 packets and verifies incoming packet signatures.

Important APIs and control flow: `sign` wraps a packet when a secret key is available. The wrapper sets the signed flag, writes through a `SigningBuffer` that updates a MAC as bytes are emitted, then copies the first signature bytes into the SMB2 header signature position. `verify` recalculates the MAC over header bytes before the signature, an empty signature field, and the remaining message, then compares with the received signature.

State, dependencies, and integration: it uses `SecurityProvider` MACs keyed by session signing keys and is used by `Connection` and signature verification handler.

Risks: offset arithmetic is security-critical. `verify` compares byte-by-byte with early exit rather than constant time. `SigningBuffer` overrides selected write methods only. Tests should include known SMB signing vectors, signed flag/header placement, tamper detection, and null-key pass-through.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/PacketSignatory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/Request.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/Request.java

Purpose: `Request` represents one outstanding SMB request and its response promise.

Important APIs and control flow: constructor stores original packet, message ID, cancel ID, timestamp, and creates a `Promise`. Async handlers may set `asyncId`. `getFuture` wraps the promise future in a cancellable future with a callback.

State, dependencies, and integration: used by `OutstandingRequests`, `Connection.send`, async response handling, cancellation, and response processing.

Risks: original packet reference is mutable; converter depends on it to deserialize matching responses. Tests should cover promise delivery, cancellation callback invocation, async ID update, and timestamp availability for logging.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/Request.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/SMBPacketSerializer.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/SMBPacketSerializer.java

Purpose: `SMBPacketSerializer` adapts SMB packet objects to transport buffers.

Important APIs and control flow: `write` creates an `SMBBuffer`, asks the packet to serialize itself, and returns the buffer.

State, dependencies, and integration: stateless; passed into `PacketHandlers` by `Connection` transport setup.

Risks: all serialization errors occur inside packet write logic. Tests should verify it returns the exact bytes emitted by representative SMB1, SMB2, signed, and encrypted packet wrappers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/SMBPacketSerializer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/SMBProtocolNegotiator.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/SMBProtocolNegotiator.java

Purpose: `SMBProtocolNegotiator` sends SMB negotiate requests, validates responses, and populates connection negotiation context.

Important APIs and control flow: `negotiateDialect` chooses SMB2-only or multiprotocol negotiation, checks NT status, parses SMB3.1.1 negotiate contexts, validates server identity against `ServerList`, and updates `ConnectionContext`. SMB3.1.1 handling enforces single preauth and encryption contexts, accepts compression capabilities, and computes the preauth hash from zero state plus request and response bytes. Multiprotocol negotiation sends SMB1 negotiate first and falls back to SMB2-only on SMB_2XX.

State, dependencies, and integration: it owns a temporary `NegotiationContext` containing request, response, cipher, compression ids, preauth hash, and server. It uses security digest providers, packet bytes, server cache, and connection send/future paths.

Risks: unknown SMB3.1.1 contexts throw rather than ignoring future extensions. Compression is recorded but not fully implemented. Tests should cover SMB2-only, multiprotocol fallback, unsuccessful status, duplicate negotiate contexts, preauth hash vectors, server cache mismatch, and encryption cipher selection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/SMBProtocolNegotiator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/SMBSessionBuilder.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/SMBSessionBuilder.java

Purpose: `SMBSessionBuilder` establishes authenticated SMB sessions and derives session cryptographic keys.

Important APIs and control flow: `establish` selects an authenticator compatible with server mech types and the auth context, optionally wraps NTLM with `NtlmSealer`, initializes it, processes tokens, and recursively calls session setup until success. `setupSession` handles `STATUS_MORE_PROCESSING_REQUIRED`, maintains SMB3.1.1 preauth sessions, updates preauth hashes, processes final tokens, installs the session key, validates signing rules, derives signing/encryption/decryption/application keys, marks the context established, and registers the session.

State, dependencies, and integration: uses `Connection`, `ConnectionContext`, session tables, configured authenticator factories, SPNEGO token classes, security provider KDF/digest, and `SessionFactory`.

Risks: recursive setup depends on authenticator eventually completing. Signing rules for guest/null/encrypted sessions are protocol-sensitive. KDF labels and preauth context must match SMB dialect. Tests should cover authenticator selection, multi-round NTLM/SPNEGO, guest signing rejection, SMB3.1.1 preauth hash updates, key derivation vectors, failed statuses, and preauth table cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/SMBSessionBuilder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/SequenceWindow.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/SequenceWindow.java

Purpose: `SequenceWindow` manages SMB message IDs and credits.

Important APIs and control flow: starts with one available permit and lowest ID zero. `get()` or `get(credits)` waits up to five seconds for permits, then returns a consecutive range and increments `lowestAvailable`. `creditsGranted` releases permits. `disableCredits` swaps in a semaphore that never blocks.

State, dependencies, and integration: `Connection.send` consumes sequence numbers and credit grants; packet handlers add credits from responses.

Risks: timeout and permit math directly affect throughput and deadlock behavior. `disableCredits` is a test/protocol escape hatch. Tests should cover initial ID zero, consecutive ranges, timeout failure, interrupted waits, credit grants, and no-op semaphore behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/SequenceWindow.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/SessionTable.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/SessionTable.java

Purpose: `SessionTable` maps SMB session IDs to active `Session` objects.

Important APIs and control flow: register, find, remove, active check, and snapshot active sessions are all guarded by a `ReentrantLock`.

State, dependencies, and integration: used by `Connection`, session setup, packet signature/decryption handlers, and close/logoff event handling.

Risks: duplicate registration overwrites silently. Snapshot active sessions may include sessions closing concurrently. Tests should cover lock-protected register/find/remove, active session snapshots, and duplicate-session behavior expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/SessionTable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/Signatory.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/Signatory.java

Purpose: `Signatory` abstracts packet signing and verification.

Important APIs and control flow: `sign(SMB2Packet, SecretKey)` may return a wrapped packet; `verify(SMB2PacketData, SecretKey)` returns signature validity.

State, dependencies, and integration: implemented by `PacketSignatory` and `NoSignatory`; injected into sessions and packet handlers.

Risks: callers must provide the correct dialect/session/channel signing key. Tests should verify both implementations through the shared interface and packet handler integration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/Signatory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/AbstractIncomingPacketHandler.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/AbstractIncomingPacketHandler.java

Purpose: `AbstractIncomingPacketHandler` provides chain-of-responsibility plumbing for incoming SMB packet handlers.

Important APIs and control flow: `handle` checks `canHandle`; if true, calls `doHandle`, otherwise delegates to `next`. `setNext` stores and returns this handler to enable fluent chain construction.

State, dependencies, and integration: state is the next handler reference. `Connection.init` builds the incoming chain from these handlers.

Risks: if `next` is null and `canHandle` is false, handling throws `NullPointerException`; the chain relies on a dead-letter tail. Tests should cover delegation order and terminal behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/AbstractIncomingPacketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/DeadLetterPacketHandler.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/DeadLetterPacketHandler.java

Purpose: `DeadLetterPacketHandler` is the terminal sink for packets rejected or unhandled by the incoming chain.

Important APIs and control flow: `canHandle` always returns true and `doHandle` logs a warning without throwing.

State, dependencies, and integration: used as the final handler after SMB1 handling in `Connection`.

Risks: invalid packets may only be logged, leaving request promises unresolved if a prior handler did not deliver an error. Tests should verify dead-letter paths for unknown responses and assess whether outstanding requests time out.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/DeadLetterPacketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/IncomingPacketHandler.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/IncomingPacketHandler.java

Purpose: `IncomingPacketHandler` defines the packet-handler chain contract.

Important APIs and control flow: handlers must implement `handle(SMBPacketData<?>)` and `setNext(IncomingPacketHandler)`.

State, dependencies, and integration: `Connection` uses the interface to compose decryption, compounding, validation, credit, async, deserialization, and dead-letter stages.

Risks: chain ordering is external to the interface and security-sensitive. Tests should verify the composed chain order rather than isolated interface behavior only.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/IncomingPacketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB1PacketHandler.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB1PacketHandler.java

Purpose: `SMB1PacketHandler` rejects incoming SMB1 packet data.

Important APIs and control flow: `canHandle` checks `SMB1PacketData`; `doHandle` throws `SMB1NotSupportedException`.

State, dependencies, and integration: located near the end of the connection packet chain to fail SMB1 packets after SMB2-specific handlers decline them.

Risks: multiprotocol negotiation can send SMB1 negotiate, but normal received SMB1 packets are unsupported. Tests should verify SMB1 data raises the expected transport-level failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB1PacketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2AsyncResponsePacketHandler.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2AsyncResponsePacketHandler.java

Purpose: `SMB2AsyncResponsePacketHandler` handles interim SMB2 asynchronous responses.

Important APIs and control flow: it retrieves the matching request, logs round-trip time, and if the packet is an intermediate async response, stores the server async ID and stops processing. Final async responses continue down the chain.

State, dependencies, and integration: depends on `OutstandingRequests`; request async ID is later used by cancel packets.

Risks: assumes the request exists after earlier outstanding check. It does not extend expiration timers. Tests should cover pending async response, final async response, cancel ID use, and missing request behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2AsyncResponsePacketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2CompoundedPacketHandler.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2CompoundedPacketHandler.java

Purpose: `SMB2CompoundedPacketHandler` splits compounded SMB2 responses into individual packet data views.

Important APIs and control flow: it handles only SMB2 data with `isCompounded()`, sends the current packet to the next handler, advances with `packetData.next()`, and repeats until no packet remains.

State, dependencies, and integration: placed early in the packet chain after decryption so each response is independently validated and delivered.

Risks: malformed compound offsets become `TransportException`. Compound session ID validation for decrypted packets is left elsewhere as TODO. Tests should cover two-plus response chains, final response handling, and malformed next-command data.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2CompoundedPacketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2CreditGrantingPacketHandler.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2CreditGrantingPacketHandler.java

Purpose: `SMB2CreditGrantingPacketHandler` returns server-granted credits to the sequence window.

Important APIs and control flow: for each SMB2 response it calls `creditsGranted(header.getCreditResponse())`, logs availability, and delegates onward.

State, dependencies, and integration: depends on the connection `SequenceWindow`; placed before async/final response processing so credits become available quickly.

Risks: blindly releases credit response values; malformed or unexpected values depend on packet parsing validation. Tests should cover zero and positive grants, waiting sender release, and handler ordering relative to promise delivery.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2CreditGrantingPacketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2IsOutstandingPacketHandler.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2IsOutstandingPacketHandler.java

Purpose: `SMB2IsOutstandingPacketHandler` verifies that a response maps to a known request unless it is an oplock break notification.

Important APIs and control flow: it reads the message sequence number, checks `OutstandingRequests`, and forwards either the packet or a `DeadLetterPacketData`.

State, dependencies, and integration: placed before signature verification and processing, so unknown responses do not deserialize into promises.

Risks: dead-lettering unknown packets may leave malicious or stray data only logged. Tests should cover known request, unknown request, oplock notification, and dead-letter forwarding.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2IsOutstandingPacketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2PacketHandler.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2PacketHandler.java

Purpose: `SMB2PacketHandler` is a typed base class for handlers that operate on `SMB2PacketData`.

Important APIs and control flow: `canHandle` checks the data type; `doHandle` casts and calls `doSMB2Handle`.

State, dependencies, and integration: superclass for async, compound, credit, outstanding, process, and signature handlers.

Risks: raw casts are safe only because `canHandle` gates the path. Tests should cover delegation for SMB2 and pass-through for non-SMB2 data.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2PacketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2ProcessResponsePacketHandler.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2ProcessResponsePacketHandler.java

Purpose: `SMB2ProcessResponsePacketHandler` deserializes final SMB2 responses and completes matching request promises.

Important APIs and control flow: it looks up the original request, asks `SMB2MessageConverter` to read the response packet in request context, removes the outstanding request by response message ID, and delivers the packet to the promise.

State, dependencies, and integration: terminal successful SMB2 handler in the chain. It depends on original request packet type for command-specific parsing.

Risks: deserialization failure throws `TransportException` but may leave the outstanding request unless caller handles connection error. Tests should cover successful delivery, converter failures, command mismatch behavior, and outstanding removal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2ProcessResponsePacketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2SignatureVerificationPacketHandler.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2SignatureVerificationPacketHandler.java

Purpose: `SMB2SignatureVerificationPacketHandler` enforces inbound SMB2 signature expectations.

Important APIs and control flow: it skips all-ones message IDs and decrypted packets. Signed packets with nonzero session IDs and non-session-setup commands are verified using the session signing key. Missing sessions or invalid signatures are dead-lettered. Unsigned packets are allowed for interim async and oplock notifications, but dead-lettered when the session requires signing.

State, dependencies, and integration: uses `SessionTable` and `Signatory`; runs after outstanding check and before credit/async/process stages.

Risks: the explicit deviation skipping session setup signatures is protocol-sensitive. Dead-lettered required-signing packets may leave promises unresolved. Tests should cover signed valid/invalid packets, missing session, decrypted bypass, unsigned required-signing rejection, and exceptions around session setup responses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB2SignatureVerificationPacketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB3DecryptingPacketHandler.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB3DecryptingPacketHandler.java

Purpose: `SMB3DecryptingPacketHandler` decrypts SMB3 transform packets before the SMB2 handler chain processes them.

Important APIs and control flow: it handles `SMB3EncryptedPacketData`, validates decryptability, finds the session by transform session ID, decrypts with the session decryption key, inspects the decrypted protocol ID, rejects nested encryption, forwards compressed data as `SMB3CompressedPacketData`, or wraps SMB2 plaintext in `SMB2DecryptedPacketData`. It dead-letters mismatched session IDs.

State, dependencies, and integration: depends on `SessionTable` and `PacketEncryptor`; it is first in the connection incoming chain.

Risks: compressed validation and compounded session ID validation are TODOs. Decryption failures become runtime exceptions from the encryptor. Tests should cover encrypted SMB2, compressed payloads, nested encryption rejection, unknown protocol rejection, missing session, and session ID mismatch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/SMB3DecryptingPacketHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/event/ConnectionClosed.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/event/ConnectionClosed.java

Purpose: `ConnectionClosed` is an event carrying the closed server hostname and port.

Important APIs and control flow: constructor stores values; getters expose them; equality and hash code are value-based.

State, dependencies, and integration: published by `Connection.close` and consumed by `SMBClient` to remove cached connections and unregister servers.

Risks: hostname must be non-null for equality/hash code. Tests should verify event publication effects and value equality.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/event/ConnectionClosed.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/event/SMBEvent.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/event/SMBEvent.java

Purpose: `SMBEvent` is the marker interface for events published through SMBJ's event bus.

Important APIs and control flow: no methods; it establishes a common message type for the bus.

State, dependencies, and integration: implemented by connection, session, and tree events.

Risks: marker-only design puts schema validation on individual event classes. Tests should focus on bus publication and handler subscription behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/event/SMBEvent.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/event/SMBEventBus.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/event/SMBEventBus.java

Purpose: `SMBEventBus` wraps MBassador so the rest of SMBJ depends on a local event facade.

Important APIs and control flow: default construction uses a synchronous MBassador bus with an error handler that logs publication errors. `subscribe`, `unsubscribe`, and `publish` delegate to the wrapped bus.

State, dependencies, and integration: used by `SMBClient`, `Connection`, sessions, and tree connections for lifecycle cleanup.

Risks: synchronous publication means handler exceptions are logged by MBassador but can affect timing. Tests should cover subscription, unsubscription, publication, and error logging with a fake or real bus.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/event/SMBEventBus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/event/SessionEvent.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/event/SessionEvent.java

Purpose: `SessionEvent` is the package-private base for events tied to an SMB session ID.

Important APIs and control flow: constructor stores `sessionId`; getter exposes it; equality and hash code compare exact event class and session ID.

State, dependencies, and integration: extended by `SessionLoggedOff` and `TreeDisconnected`.

Risks: exact-class equality means different session event subtypes with the same ID are intentionally not equal. Tests should verify equality semantics and event consumer matching.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/event/SessionEvent.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/event/SessionLoggedOff.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/event/SessionLoggedOff.java

Purpose: `SessionLoggedOff` signals that a session has logged off.

Important APIs and control flow: it only passes the session ID to `SessionEvent`.

State, dependencies, and integration: handled by `Connection` to remove sessions from `SessionTable`.

Risks: cleanup depends on event publication during session close. Tests should cover session logoff event leading to session table removal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/event/SessionLoggedOff.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/event/TreeDisconnected.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/event/TreeDisconnected.java

Purpose: `TreeDisconnected` signals that a tree/share connection was disconnected within a session.

Important APIs and control flow: extends `SessionEvent` and adds `treeId`.

State, dependencies, and integration: consumed by components that track per-session tree connections.

Risks: unlike `SessionEvent`, equality/hash code do not include `treeId` because it inherits the base implementation. Tests should confirm whether this is intentional, especially when multiple tree IDs disconnect under one session.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/event/TreeDisconnected.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/ArrayByteChunkProvider.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/ArrayByteChunkProvider.java

Purpose: `ArrayByteChunkProvider` streams chunks from an in-memory byte array.

Important APIs and control flow: constructor captures source array, buffer offset, length, and remote file offset. `getChunk` copies up to the chunk buffer length, advances the array offset, and decrements remaining bytes. `prepareWrite` is a no-op.

State, dependencies, and integration: used by SMB write paths that can source data from byte arrays.

Risks: source array is not copied, so caller mutation affects writes. Constructor does not validate offset/length bounds. Tests should cover partial writes, file offset reporting, bytes-left updates, and invalid constructor ranges.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/ArrayByteChunkProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/BufferByteChunkProvider.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/BufferByteChunkProvider.java

Purpose: `BufferByteChunkProvider` streams chunks from SMBJ's protocol `Buffer`.

Important APIs and control flow: `isAvailable` and `bytesLeft` mirror `buffer.available()`. `getChunk` reads the smaller of destination length and available bytes, wrapping `BufferException` as `IOException`.

State, dependencies, and integration: used directly for buffer-backed writes and internally by `CachingByteChunkProvider`.

Risks: consumes from the buffer's read position. Tests should cover exact, short, and exhausted reads plus exception wrapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/BufferByteChunkProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/ByteBufferByteChunkProvider.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/ByteBufferByteChunkProvider.java

Purpose: `ByteBufferByteChunkProvider` adapts a Java `ByteBuffer` to cached SMB write chunks.

Important APIs and control flow: `prepareChunk` reads up to destination length, requested bytes, and `buffer.remaining()`, returning -1 when no bytes are needed. `isAvailable` checks both cached data and remaining source buffer bytes.

State, dependencies, and integration: extends `CachingByteChunkProvider`; constructors optionally set remote file offset.

Risks: advances the caller-supplied `ByteBuffer` position. Tests should cover prepare/write cycles, zero-byte prepare, direct and heap buffers, offset propagation, and availability before and after cache fill.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/ByteBufferByteChunkProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/ByteChunkProvider.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/ByteChunkProvider.java

Purpose: `ByteChunkProvider` is the abstract base for streaming data into SMB write requests.

Important APIs and control flow: subclasses report availability, prepare data, provide chunks, and report bytes left. Base methods write one or more chunks to an `OutputStream` or protocol `Buffer`, update remote offset by written size, and track `lastWriteSize`. IO failures are wrapped as `SMBRuntimeException`.

State, dependencies, and integration: shared state includes remote `offset`, `chunkSize` defaulting to 64 KiB, and `lastWriteSize`. Used by share/file write implementations.

Risks: allocates a fresh chunk buffer per write call. Runtime wrapping hides checked IO from callers. Tests should cover offset and last-write updates, multi-chunk writes, zero-byte providers, and close behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/ByteChunkProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/CachingByteChunkProvider.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/CachingByteChunkProvider.java

Purpose: `CachingByteChunkProvider` buffers source data before write calls so stream-like sources can be prepared to a target size.

Important APIs and control flow: constructor creates a big-endian plain buffer and a `BufferByteChunkProvider` over it. `prepareWrite` compacts the cache, computes bytes needed, repeatedly calls subclass `prepareChunk`, and appends data to the cache until enough data or EOF. `getChunk`, `bytesLeft`, `isAvailable`, and `close` delegate to the cache provider.

State, dependencies, and integration: base for `InputStreamByteChunkProvider` and `ByteBufferByteChunkProvider`.

Risks: read buffer is fixed at 1024 bytes, which may limit preparation efficiency. `buffer` is never null despite guard. Tests should cover compaction, EOF handling, partial fills, repeated prepare/write loops, and runtime wrapping of IO failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/CachingByteChunkProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/EmptyByteChunkProvider.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/EmptyByteChunkProvider.java

Purpose: `EmptyByteChunkProvider` represents an empty write source at a given file offset.

Important APIs and control flow: `isAvailable` is false, `getChunk` and `bytesLeft` return zero, and `prepareWrite` is a no-op.

State, dependencies, and integration: used when a write path needs a provider object but no payload bytes.

Risks: callers must not assume `getChunk` returning zero means progress. Tests should cover offset initialization and no writes emitted.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/EmptyByteChunkProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/FileByteChunkProvider.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/FileByteChunkProvider.java

Purpose: `FileByteChunkProvider` streams bytes from a local file for SMB writes.

Important APIs and control flow: constructor opens a `FileInputStream`, wraps it in `InputStreamByteChunkProvider`, skips to the requested offset, and sets the remote file offset. All provider methods delegate to the underlying input-stream provider.

State, dependencies, and integration: owns the local `File`, opened stream through the delegate, and offset state.

Risks: `ensureSkipped` calls `fis.skip(offset)` each loop rather than the remaining amount, which can overshoot accounting or loop oddly. `available()` is not a reliable file length indicator. Tests should cover offset zero/nonzero, skip failure, close closes the stream, and large offsets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/FileByteChunkProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/InputStreamByteChunkProvider.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/InputStreamByteChunkProvider.java

Purpose: `InputStreamByteChunkProvider` adapts an `InputStream` to the cached chunk provider contract.

Important APIs and control flow: constructor uses an existing `BufferedInputStream` as-is or wraps the stream and marks it owned. `prepareChunk` reads up to requested bytes and chunk length. `isAvailable` returns cached availability or `is.available() > 0`. `close` closes only streams it wrapped itself.

State, dependencies, and integration: extends `CachingByteChunkProvider`; used directly and by `FileByteChunkProvider`.

Risks: `InputStream.available()` is not a reliable EOF or readiness signal for all streams. A provided `BufferedInputStream` is not closed by this provider. Tests should cover wrapped versus unwrapped close ownership, EOF reads, partial availability, and IO exception wrapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/io/InputStreamByteChunkProvider.java -->
