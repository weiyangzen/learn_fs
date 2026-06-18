# Research: subset-b-007427 Hadoop HDFS client WebHDFS and striping utilities

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/StripedBlockUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/StripedBlockUtil.java

## Purpose

`StripedBlockUtil` is the HDFS erasure-coded striped block mapping utility. It translates logical byte ranges in a block group into internal-block offsets, aligned read stripes, chunk buffers, and zero-fill markers used by striped reads and recovery/decoding paths. It also constructs per-internal-block `LocatedBlock`/`ExtendedBlock` views from a `LocatedStripedBlock`.

## Important APIs, Types, And Functions

Key entry points are `parseStripedBlockGroup`, `constructInternalBlock`, `getInternalBlockLength`, `getSafeLength`, `offsetInBlkToOffsetInBG`, `divideOneStripe`, `divideByteRangeIntoStripes`, `spaceConsumedByStripedBlock`, `getNextCompletedStripedRead`, `checkBlocks`, and `getBlockIndex`. Important nested types are `BlockReadStats`, `StripingCell`, `AlignedStripe`, `VerticalRange`, `StripingChunk`, `ChunkByteBuffer`, `StripingChunkReadResult`, and `StripeRange`.

## Control Flow

Block-group parsing indexes returned striped locations by block index and constructs internal blocks with adjusted block IDs and lengths. Range division maps a logical request to `StripingCell`s, derives per-internal-block `VerticalRange`s, merges range boundaries into aligned stripes, maps destination `ByteBuffer` slices into requested chunks, and marks data chunks beyond short internal block length as `ALLZERO`. Async read completion pulls `Future<BlockReadStats>` from a `CompletionService` and normalizes success, failure, cancellation, and timeout into `StripingChunkReadResult`.

## State And Persistence

The class is stateless apart from mutable objects it returns. `StripingChunk` state flags model in-memory read progress only. `ChunkByteBuffer` holds `ByteBuffer` slices over caller buffers and can copy decoded data back. There is no persistence; correctness depends on stable block IDs, generation stamps, EC policy width, cell size, and block-group length supplied by HDFS metadata.

## Dependencies And Integration Points

It integrates with `LocatedStripedBlock`, `LocatedBlock`, `ExtendedBlock`, `ErasureCodingPolicy`, `DFSStripedOutputStream` cell layout, block tokens, storage IDs/types, datanode locations, async read executors, and HDFS striped reader/decoder code.

## Risks

Most risks are off-by-one or boundary errors: inclusive logical ranges are converted to half-open buffer ranges, last partial cells affect parity fetch spans, and block-group length can split a stripe. `spaceConsumedByStripedBlock` uses a parity index based on internal length symmetry and should be regression-tested for partial final stripes. `getBlockIndex` masks only low four bits, so it assumes the encoded internal index range remains within that contract.

## Test Signals

Useful tests cover full and partial stripes, single-stripe reads, reads crossing cell and stripe boundaries, partial final block groups, all-zero chunk preparation, async read success/failure/cancel/timeout, block token/location propagation, `checkBlocks` mismatch exceptions, safe length calculation, and parity space accounting for multiple EC policies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/StripedBlockUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/package-info.java

## Purpose

This file declares the `org.apache.hadoop.hdfs.util` package for HDFS client utility classes. It contains only the Apache license header and package declaration, with no package annotation or executable code.

## Important APIs, Types, And Functions

There are no APIs, classes, or methods. Its only exported effect is the Java package namespace.

## Control Flow

No runtime control flow exists. The Java compiler consumes this as package metadata.

## State And Persistence

No mutable state or persistence behavior exists.

## Dependencies And Integration Points

It integrates with Java package documentation conventions and the surrounding HDFS utility sources in the same package.

## Risks

Risk is limited to accidental package declaration mismatch or license/header drift. Since it has no annotations, changing it should not affect runtime behavior.

## Test Signals

Compilation of the `org.apache.hadoop.hdfs.util` package is sufficient; documentation generation may also verify the package is visible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/ByteRangeInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/ByteRangeInputStream.java

## Purpose

`ByteRangeInputStream` adapts HTTP byte-range reads to the `FSInputStream` contract. It hides repeated HTTP connection creation when callers seek, positioned-read, or read fully from WebHDFS-like endpoints.

## Important APIs, Types, And Functions

The main extension point is `URLOpener.connect(offset, resolved)`, plus subclass hook `getResolvedUrl(HttpURLConnection)`. State is tracked with `StreamStatus` values `NORMAL`, `SEEK`, and `CLOSED`. Core methods are `getInputStream`, `openInputStream`, `read`, `seek`, positioned `read`, `readFully`, `getPos`, `close`, and `available`.

## Control Flow

Construction immediately opens the first stream. `seek` records a new start/current position and puts the stream in `SEEK`. The next read closes the old stream, opens either the original or resolved URL with the requested offset, updates `fileLength` from `Content-Length` unless transfer encoding is chunked, and wraps non-chunked streams in `BoundedInputStream`. Positioned reads open temporary streams and do not disturb the main stream state.

## State And Persistence

State is in-memory: current input stream, original/resolved URL openers, `startPos`, `currentPos`, optional `fileLength`, and status. No persistence exists. `fileLength` may be unknown for chunked transfer encoding.

## Dependencies And Integration Points

It depends on `HttpURLConnection`, commons-io `BoundedInputStream`, Hadoop `FSInputStream`, `FSExceptionMessages`, and Guava HTTP header constants. `WebHdfsFileSystem.OffsetUrlInputStream` extends it for WebHDFS open redirects.

## Risks

Header parsing assumes exact map keys from `HttpURLConnection`; case behavior depends on the JDK header map. Non-chunked responses without `Content-Length` fail. Negative seeks throw `EOFException`, but seeking beyond EOF is detected only when the server response or read length exposes it. `available` delegates to the current HTTP stream and can force a connection.

## Test Signals

Tests should cover first open, seek then read, positioned read isolation, chunked vs non-chunked responses, missing `Content-Length`, premature EOF detection, close behavior, and resolved URL reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/ByteRangeInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/JsonUtilClient.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/JsonUtilClient.java

## Purpose

`JsonUtilClient` converts WebHDFS/HttpFS JSON maps into Hadoop client objects. It is the client-side schema bridge for file status, blocks, tokens, quotas, checksums, ACLs, xattrs, snapshots, storage policies, erasure coding, server defaults, trash roots, and block locations.

## Important APIs, Types, And Functions

Important converters include `toRemoteException`, `toToken`, `toFileStatus`, `toHdfsFileStatusArray`, `toDirectoryListing`, `toDatanodeInfo`, `toLocatedBlock`, `toLocatedBlocks`, `toContentSummary`, `toQuotaUsage`, `toMD5MD5CRC32FileChecksum`, `toAclStatus`, `toXAttrs`, `toDelegationToken`, `getStoragePolicies`, `toECPolicy`, `toFsServerDefaults`, snapshot converters, `toBlockLocationArray`, and scalar helpers `getBoolean/getInt/getLong/getString/getList/getMap`.

## Control Flow

Each method expects a known JSON envelope and constructs the corresponding protocol or filesystem type. Some converters tolerate older or optional fields: datanodes can derive `ipAddr` and `xferPort` from legacy `name`, file status defaults absent `fileId` or storage policy, and server defaults provide proto-equivalent fallback values. Remote exceptions are converted to `RemoteException`, with `UnsupportedOperationException` thrown directly.

## State And Persistence

The class has no mutable persistent state. It allocates object graphs from parsed JSON maps and byte arrays. Checksum reconstruction reads serialized checksum bytes from JSON into Hadoop checksum implementations.

## Dependencies And Integration Points

It integrates tightly with `WebHdfsFileSystem` response decoding, Jackson object reading for xattr names, `DFSUtilClient`, HDFS protocol classes, token classes, ACL and permission classes, `DataChecksum`, `BlockStoragePolicy`, and erasure-coding metadata.

## Risks

Schema drift is the main risk. Many methods cast unchecked `Map`/`List`/`Number` values and will fail late if servers change field names or numeric shapes. `BlockLocation` parses `corrupt` through `Boolean.getBoolean(String)`, which checks system properties rather than normal string truth; this is a notable correctness risk. XAttr names parse a JSON-encoded string nested inside JSON, so escaping must match server output exactly.

## Test Signals

Tests need golden JSON for every WebHDFS response shape, old-server datanode compatibility, missing optional fields, unsupported-operation remote exceptions, checksum algorithm/length validation, xattr encodings, snapshot diff listings, EC policy states, storage-policy arrays, and block-location corruption flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/JsonUtilClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/KerberosUgiAuthenticator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/KerberosUgiAuthenticator.java

## Purpose

`KerberosUgiAuthenticator` customizes Hadoop HTTP Kerberos authentication so SPNEGO fallback uses Hadoop `UserGroupInformation` instead of the base pseudo-authenticator username lookup.

## Important APIs, Types, And Functions

It extends `KerberosAuthenticator` and overrides `getFallBackAuthenticator`. The returned anonymous `PseudoAuthenticator` overrides `getUserName` to return `UserGroupInformation.getLoginUser().getUserName()`.

## Control Flow

When an authenticated URL tries Kerberos and the server does not use SPNEGO, the fallback pseudo authenticator supplies the UGI login user name. `IOException` while retrieving the login user is wrapped as `SecurityException`.

## State And Persistence

The class owns no state. It reads current process login-user state from UGI.

## Dependencies And Integration Points

It is used by `URLConnectionFactory.openConnection(url, true)` through `AuthenticatedURL`. It depends on Hadoop security authentication client classes and UGI.

## Risks

Incorrect fallback identity can cause insecure-cluster or proxy-user behavior differences. Wrapping `IOException` in unchecked `SecurityException` changes failure handling relative to callers expecting checked authentication errors.

## Test Signals

Tests should cover SPNEGO fallback in simple-auth mode, UGI login-user selection, and failure when UGI cannot provide a user.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/KerberosUgiAuthenticator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/SSLConnectionConfigurator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/SSLConnectionConfigurator.java

## Purpose

`SSLConnectionConfigurator` applies Hadoop SSL client configuration to HTTP connections and sets socket timeouts.

## Important APIs, Types, And Functions

It implements `ConnectionConfigurator`. The constructor builds and initializes an `SSLFactory`, obtains `SSLSocketFactory` and `HostnameVerifier`, and stores connect/read timeouts. `configure` applies SSL pieces to `HttpsURLConnection` and always sets timeouts. `destroy` releases the `SSLFactory`.

## Control Flow

Factories are initialized once at construction. Each connection configuration checks whether the connection is HTTPS; if so, it installs the SSL socket factory and hostname verifier before setting timeout values.

## State And Persistence

State is in-memory SSL factory material plus immutable timeout values. No persistence exists, though SSLFactory may read keystores/truststores from configuration.

## Dependencies And Integration Points

`URLConnectionFactory` uses this for normal and OAuth WebHDFS connection factories. It depends on Hadoop `SSLFactory`, Java `HttpsURLConnection`, and authentication client `ConnectionConfigurator`.

## Risks

Constructor failures force callers to fall back or fail depending on path. Forgetting `destroy` can leak SSLFactory resources. HTTP URLs still receive timeouts but no TLS protection, so callers must enforce scheme policy where required.

## Test Signals

Tests should verify configured HTTPS socket factory/hostname verifier, timeout propagation for HTTP and HTTPS, failure fallback in `URLConnectionFactory`, and `destroy` invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/SSLConnectionConfigurator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/SWebHdfsFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/SWebHdfsFileSystem.java

## Purpose

`SWebHdfsFileSystem` is the HTTPS variant of `WebHdfsFileSystem`.

## Important APIs, Types, And Functions

It overrides `getScheme` to return `swebhdfs`, `getTransportScheme` to return `https`, `getTokenKind` to return `SWEBHDFS delegation`, and `getDefaultPort` to return the configured HDFS NameNode HTTPS default.

## Control Flow

All filesystem behavior remains in `WebHdfsFileSystem`; this subclass changes URI scheme, transport, token kind, and default port selection during initialization and URL construction.

## State And Persistence

It adds no state and no persistence.

## Dependencies And Integration Points

It integrates with Hadoop `FileSystem` scheme resolution, WebHDFS token management, SSL connection configuration, and `HdfsClientConfigKeys.DFS_NAMENODE_HTTPS_PORT_DEFAULT`.

## Risks

Wrong scheme/token-kind pairing would break token selection and renewals. HTTPS relies on correct SSL configuration from the inherited connection factory path.

## Test Signals

Tests should initialize `swebhdfs://` URIs, verify HTTPS URLs/default ports, and validate SWEBHDFS delegation-token selection and renewal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/SWebHdfsFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/TokenAspect.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/TokenAspect.java

## Purpose

`TokenAspect` centralizes delegation-token behavior for HTTP-based HDFS filesystems, including token selection from UGI, lazy token acquisition, renewal registration, reset, and token renewer dispatch.

## Important APIs, Types, And Functions

Important pieces are nested `TokenManager`, `DTSelecorByKind`, `TokenManagementDelegator`, constructor `TokenAspect(fs, serviceName, kind)`, `ensureTokenInitialized`, `reset`, `initDelegationToken`, `removeRenewAction`, and `selectDelegationToken`.

## Control Flow

`initDelegationToken` selects an existing token for the service and installs it into the filesystem. `ensureTokenInitialized` fetches a new delegation token when none has been initialized or the renew action became invalid; fetched tokens are registered with `DelegationTokenRenewer`. `TokenManager` renews/cancels tokens by deriving a WebHDFS/SWebHDFS URI from token kind and service, opening the matching filesystem, and delegating token operations.

## State And Persistence

State includes the renew action, optional renewer singleton, token selector, filesystem reference, service name, and `hasInitedToken`. No durable persistence exists; token state is in UGI/filesystem memory and renewer queues.

## Dependencies And Integration Points

It depends on `DelegationTokenRenewer`, `TokenRenewer`, HA token utilities, `SecurityUtil`, `FileSystem.get`, UGI token sets, and `WebHdfsConstants` token kinds.

## Risks

Token-kind and service-name mismatches can prevent token reuse or renewals. `TokenManager.isManaged` always returns true for handled kinds, so invalid service URIs surface later. Synchronization protects local state but external UGI token changes require reset or reinitialization.

## Test Signals

Tests should cover logical and physical token services, WebHDFS vs SWebHDFS kinds, existing UGI token selection, lazy fetch, invalid renew-action refresh, remove renew action, and token manager renew/cancel URI resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/TokenAspect.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/URLConnectionFactory.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/URLConnectionFactory.java

## Purpose

`URLConnectionFactory` constructs and configures URL connections for WebHDFS clients, including timeouts, SSL, OAuth2, and optional SPNEGO authentication.

## Important APIs, Types, And Functions

Key APIs are `DEFAULT_SOCKET_TIMEOUT`, `DEFAULT_SYSTEM_CONNECTION_FACTORY`, `newDefaultURLConnectionFactory`, `newOAuth2URLConnectionFactory`, `openConnection(URL)`, `openConnection(URL, boolean isSpnego)`, private `getSSLConnectionConfiguration`, `setTimeouts`, and `destroy`.

## Control Flow

Factory methods attempt to create `SSLConnectionConfigurator`; default factories fall back to timeout-only configuration on SSL setup failure, while OAuth factory treats setup failure as fatal. `openConnection` either opens a plain URL and applies the configurator or opens an `AuthenticatedURL` with `KerberosUgiAuthenticator` after refreshing the current user's TGT.

## State And Persistence

The factory stores one `ConnectionConfigurator`. No persistent state exists. `destroy` tears down the SSL configurator if the direct configurator is an `SSLConnectionConfigurator`.

## Dependencies And Integration Points

It integrates with WebHDFS initialization, OAuth2 connection configuration, SSL factory setup, Hadoop UGI, `AuthenticatedURL`, and Kerberos fallback auth.

## Risks

The OAuth path requires SSL configurator construction and wraps all failures as `IOException`. `destroy` does not reach an SSL configurator nested inside `OAuth2ConnectionConfigurator`, so lifecycle coverage differs by mode. Returning null from the unreachable `AuthenticationException` path in `openConnection(URL)` would be hazardous if assumptions change.

## Test Signals

Tests should cover default timeout-only fallback, SSL configuration success, OAuth factory failure, SPNEGO open path with TGT refresh, non-HTTP URL behavior, and destroy lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/URLConnectionFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/WebHdfsConstants.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/WebHdfsConstants.java

## Purpose

`WebHdfsConstants` holds scheme and delegation-token-kind constants shared by WebHDFS and SWebHDFS plus a small path-type enum used for JSON status conversion.

## Important APIs, Types, And Functions

Constants are `WEBHDFS_SCHEME`, `SWEBHDFS_SCHEME`, `WEBHDFS_TOKEN_KIND`, and `SWEBHDFS_TOKEN_KIND`. Nested `PathType` has values `FILE`, `DIRECTORY`, `SYMLINK` and `valueOf(HdfsFileStatus)`.

## Control Flow

`PathType.valueOf` checks directory first, symlink second, and otherwise returns file.

## State And Persistence

Only static constants exist. `Text` token-kind instances are shared immutable-ish Hadoop values by convention.

## Dependencies And Integration Points

Used by `WebHdfsFileSystem`, `SWebHdfsFileSystem`, `TokenAspect`, and `JsonUtilClient` status parsing.

## Risks

Changing constant strings breaks filesystem scheme resolution and existing delegation token compatibility. `PathType` ordering must match HDFS status semantics.

## Test Signals

Tests should verify scheme registration, token-kind selection/renewal, and file/directory/symlink JSON status conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/WebHdfsConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/WebHdfsFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/WebHdfsFileSystem.java

## Purpose

`WebHdfsFileSystem` implements Hadoop `FileSystem` over the WebHDFS REST API. It maps filesystem methods to HTTP operations, manages authentication and delegation tokens, handles HA failover/retry, parses JSON responses, and provides streaming reads/writes over redirected NameNode/DataNode connections.

## Important APIs, Types, And Functions

Important public methods include initialization, status/list/open/create/append/delete/rename/mkdirs, xattr/ACL/snapshot/storage-policy/EC/quota/checksum/trash/block-location APIs, delegation-token operations, KMS integration, capabilities, and multipart uploader creation. Important nested runners are `AbstractRunner`, `AbstractFsPathRunner`, `FsPathResponseRunner`, `FsPathOutputStreamRunner`, `URLRunner`, `WebHdfsInputStream`, and `ReadRunner`.

## Control Flow

`initialize` configures user/ACL patterns, connection factory, HA/non-HA retry policy, token service, working directory, security fallback rules, CSRF headers, and statistics. URLs are built from operation parameters plus either delegation tokens or user/doAs parameters. `AbstractRunner` executes calls inside UGI `doAs`, resolves redirects for DataNode operations, validates response codes, refreshes expired tokens, excludes failed datanodes, and applies retry/failover policy. Filesystem methods wrap this pattern with operation-specific params and JSON decoders.

## State And Persistence

State includes UGI, URI, current delegation token, token service, NameNode addresses/current index, retry policy, working/home directories, CSRF settings, connection factory, server-compatibility flags, and read-stream connection state. No client-side persistence exists. Closing cancels owned delegation tokens and destroys the connection factory.

## Dependencies And Integration Points

It integrates with Hadoop `FileSystem`, WebHDFS resource params/op enums, `JsonUtilClient`, UGI/SPNEGO/delegation tokens, HA utilities, retry policies, KMS/key providers, storage statistics, HTTP headers, SSL/OAuth factories, and HDFS protocol models.

## Risks

This is high-blast-radius code. Risks include auth fallback mistakes between secure and insecure clusters, token refresh during retries, HA failover state races, redirect handling for create/append/open/checksum, CSRF header method filtering, JSON schema compatibility, old server fallback for block locations, and stream reconnection after seek/read failures. `ReadRunner.closeInputStream` nulls `in` before closing it, so any intended stream close relies on connection close behavior and merits focused review.

## Test Signals

Coverage should include MiniDFS/WebHDFS secure and insecure modes, HA failover, token acquisition/renew/cancel/expiry replacement, create/append two-step redirects, open/seek/read retry behavior, encrypted file reads, CSRF configuration, all REST operation mappings, old/new block location ops, KMS token issuer behavior, and response validation/error unwrapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/WebHdfsFileSystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/AccessTokenProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/AccessTokenProvider.java

## Purpose

`AccessTokenProvider` is the base SPI for supplying OAuth2 bearer tokens to WebHDFS HTTP connections.

## Important APIs, Types, And Functions

It implements Hadoop `Configurable`, stores `Configuration`, and declares abstract `getAccessToken()`.

## Control Flow

Connection configurators call `getAccessToken` for each connection. Subclasses own caching and refresh behavior.

## State And Persistence

Only the Hadoop configuration reference is stored. No token state is held in the base class.

## Dependencies And Integration Points

`OAuth2ConnectionConfigurator` instantiates subclasses by configuration and calls `setConf`. Implementations use WebHDFS OAuth configuration keys.

## Risks

Implementations must be performant and thread-safe because tokens are requested per connection. Misconfigured providers fail during reflection or first token request.

## Test Signals

Tests should cover configuration injection, subclass selection, exception propagation, and repeated connection calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/AccessTokenProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/AccessTokenTimer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/AccessTokenTimer.java

## Purpose

`AccessTokenTimer` tracks OAuth access-token expiry and decides when refresh should occur before actual expiration.

## Important APIs, Types, And Functions

Key members are `EXPIRE_BUFFER_MS`, `Timer`, `nextRefreshMSSinceEpoch`, constructors, `setExpiresIn`, `setExpiresInMSSinceEpoch`, `getNextRefreshMSSinceEpoch`, `shouldRefresh`, and static `convertExpiresIn`.

## Control Flow

OAuth `expires_in` seconds are converted to epoch milliseconds using the injected timer. `shouldRefresh` returns true when current time is later than expiry minus the 30-second buffer.

## State And Persistence

It stores only the next refresh epoch in memory. Configuration-based refresh-token provider can seed this from a configured epoch.

## Dependencies And Integration Points

Used by credential and refresh-token OAuth providers. It depends on Hadoop `Timer` for testable time.

## Risks

Bad numeric strings throw unchecked parse exceptions. Very short expiry values refresh immediately. Clock skew and wall-clock jumps can affect behavior.

## Test Signals

Tests should use fake timers for before-buffer, inside-buffer, expired, zero/default, and configured epoch cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/AccessTokenTimer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/ConfCredentialBasedAccessTokenProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/ConfCredentialBasedAccessTokenProvider.java

## Purpose

`ConfCredentialBasedAccessTokenProvider` supplies the client credential for the OAuth2 client-credentials grant from Hadoop configuration.

## Important APIs, Types, And Functions

It extends `CredentialBasedAccessTokenProvider`, stores `credential`, overrides `setConf`, and implements `getCredential`.

## Control Flow

`setConf` initializes common OAuth config in the superclass, then requires `dfs.webhdfs.oauth2.credential`. Token refresh is inherited; when a token is needed, superclass calls `getCredential`.

## State And Persistence

State is the configured credential string and inherited access-token/timer state. No durable persistence exists.

## Dependencies And Integration Points

It is the default OAuth token provider selected by `OAuth2ConnectionConfigurator` when a provider class is not explicitly set.

## Risks

Credentials live in configuration and memory. `getCredential` throws if called before proper configuration. Missing config keys fail at initialization.

## Test Signals

Tests should cover configured credential, missing credential, superclass config requirements, and token refresh body content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/ConfCredentialBasedAccessTokenProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/ConfRefreshTokenBasedAccessTokenProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/ConfRefreshTokenBasedAccessTokenProvider.java

## Purpose

`ConfRefreshTokenBasedAccessTokenProvider` obtains WebHDFS OAuth2 access tokens from a configured refresh token using the authorization-code refresh-token flow.

## Important APIs, Types, And Functions

It defines config keys `dfs.webhdfs.oauth2.refresh.token` and `dfs.webhdfs.oauth2.refresh.token.expires.ms.since.epoch`. Important methods are constructors, `setConf`, synchronized `getAccessToken`, package-visible `refresh`, and `getRefreshToken`.

## Control Flow

`setConf` loads refresh token, expiry epoch, client ID, and refresh URL. `getAccessToken` refreshes when the timer says the token is expired or near expiry. `refresh` posts URL-encoded `grant_type=refresh_token`, refresh token, and client ID, requires HTTP 200, parses JSON `expires_in` and `access_token`, and updates timer/token.

## State And Persistence

State is in-memory access token, refresh token, client ID, refresh URL, and timer. No refreshed token is written back to configuration.

## Dependencies And Integration Points

It uses Apache HttpClient, `JsonSerialization`, OAuth constants, `URLConnectionFactory.DEFAULT_SOCKET_TIMEOUT`, and WebHDFS OAuth config keys.

## Risks

The initial access token is null until the first successful refresh, so bad expiry config can produce immediate network failure. Response entity is converted to string multiple times in error/success paths. Secrets remain in memory and may appear in test/log diagnostics if not careful.

## Test Signals

Tests should mock token endpoint success/failure, missing config, expiry-triggered refresh, JSON parse failures, non-200 responses, and synchronized concurrent calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/ConfRefreshTokenBasedAccessTokenProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/CredentialBasedAccessTokenProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/CredentialBasedAccessTokenProvider.java

## Purpose

`CredentialBasedAccessTokenProvider` implements the OAuth2 client-credentials token flow for providers that can supply a client secret/credential.

## Important APIs, Types, And Functions

It defines `dfs.webhdfs.oauth2.credential`, stores timer, client ID, refresh URL, access token, and `initialCredentialObtained`, declares abstract `getCredential`, overrides `setConf`, synchronized `getAccessToken`, and package-visible `refresh`.

## Control Flow

`getAccessToken` refreshes if the token is near expiry or no token has been obtained. `refresh` posts `client_secret`, `grant_type=client_credentials`, and `client_id` to the configured token endpoint, requires HTTP 200, parses `expires_in`, and stores `access_token`.

## State And Persistence

OAuth token and timer are in memory only. The credential comes from subclasses.

## Dependencies And Integration Points

`ConfCredentialBasedAccessTokenProvider` supplies the credential. `OAuth2ConnectionConfigurator` calls this through the `AccessTokenProvider` base. Apache HttpClient performs token endpoint calls.

## Risks

Refresh failures are wrapped as `IOException`, losing some endpoint-specific structure. Missing or malformed JSON fields throw during refresh. Token endpoint timeout is fixed to the default socket timeout.

## Test Signals

Tests should verify first-call refresh, expiry refresh, credential inclusion, error wrapping, malformed endpoint responses, and thread synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/CredentialBasedAccessTokenProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/OAuth2ConnectionConfigurator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/OAuth2ConnectionConfigurator.java

## Purpose

`OAuth2ConnectionConfigurator` applies OAuth2 bearer-token authentication to WebHDFS HTTP connections, optionally after SSL configuration.

## Important APIs, Types, And Functions

Important members are `HEADER = "Bearer "`, `AccessTokenProvider accessTokenProvider`, optional `ConnectionConfigurator sslConfigurator`, constructors, and `configure`.

## Control Flow

Construction requires the access-token-provider config key, resolves the provider class with `conf.getClass`, instantiates it with `ReflectionUtils`, and calls `setConf`. `configure` first delegates to SSL if present, then requests an access token and sets request property `AUTHORIZATION` to `Bearer <token>`.

## State And Persistence

It stores provider and optional SSL configurator. Token state lives in the provider. No persistence exists.

## Dependencies And Integration Points

Created by `URLConnectionFactory.newOAuth2URLConnectionFactory` and used for all OAuth-enabled WebHDFS connections.

## Risks

Header name casing is literal `AUTHORIZATION`; HTTP is case-insensitive, but tests/proxies may expect `Authorization`. Provider reflection/config failures occur at construction. SSL configurator lifecycle is not exposed through this class.

## Test Signals

Tests should verify provider selection, missing config failures, Authorization header content, SSL delegation order, and exception propagation from provider refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/OAuth2ConnectionConfigurator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/OAuth2Constants.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/OAuth2Constants.java

## Purpose

`OAuth2Constants` centralizes string constants for WebHDFS OAuth2 form bodies and JSON fields.

## Important APIs, Types, And Functions

It defines `URLENCODED`, `ACCESS_TOKEN`, `BEARER`, `CLIENT_CREDENTIALS`, `CLIENT_ID`, `CLIENT_SECRET`, `EXPIRES_IN`, `GRANT_TYPE`, `REFRESH_TOKEN`, and `TOKEN_TYPE`. The constructor is private.

## Control Flow

No runtime logic exists beyond class loading constants.

## State And Persistence

Only static final strings exist.

## Dependencies And Integration Points

Used by OAuth token providers and request configurator when building form data and parsing token endpoint responses.

## Risks

Changing any value breaks OAuth protocol interoperability. The `BEARER` constant is not the same as `OAuth2ConnectionConfigurator.HEADER`, so duplicated bearer spelling should remain consistent.

## Test Signals

OAuth provider request-body and response-parse tests indirectly validate these constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/OAuth2Constants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/Utils.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/Utils.java

## Purpose

`Utils` provides small package-private helpers for WebHDFS OAuth2 configuration and form encoding.

## Important APIs, Types, And Functions

Functions are `notNull(Configuration, String)` and `postBody(String... kv)`.

## Control Flow

`notNull` fetches a configuration value and throws `IllegalArgumentException` if absent. `postBody` requires an even number of key/value arguments, URL-encodes each using UTF-8, and joins them as `application/x-www-form-urlencoded` pairs.

## State And Persistence

No state exists.

## Dependencies And Integration Points

Used by OAuth providers/configurator for required config validation. `postBody` is available but current token providers use Apache `UrlEncodedFormEntity` instead.

## Risks

`notNull` treats empty strings as valid. `postBody` throws checked `UnsupportedEncodingException` even though UTF-8 should always exist on Java platforms.

## Test Signals

Tests should cover missing config, present empty values if policy matters, odd key/value arrays, special-character encoding, and pair ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/Utils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/package-info.java

## Purpose

This package-info documents `org.apache.hadoop.hdfs.web.oauth2` as OAuth2-based WebHDFS authentication and marks it `@InterfaceAudience.Public`.

## Important APIs, Types, And Functions

No classes or functions are declared. The package annotation is the important API signal.

## Control Flow

No runtime control flow exists.

## State And Persistence

No state or persistence exists.

## Dependencies And Integration Points

It imports Hadoop `InterfaceAudience` and applies package-level public audience metadata for OAuth2 WebHDFS classes.

## Risks

Changing the annotation affects compatibility/audience documentation. Package declaration mismatch would break compilation.

## Test Signals

Compilation and Javadoc/audience checks validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/AccessTimeParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/AccessTimeParam.java

## Purpose

`AccessTimeParam` models the WebHDFS `accesstime` query parameter for `SETTIMES`.

## Important APIs, Types, And Functions

It extends `LongParam`, defines `NAME = "accesstime"` and `DEFAULT = "-1"`, and has constructors from `Long` or `String`.

## Control Flow

The `Long` constructor permits values from `-1` upward. The `String` constructor parses through the domain. `getName` returns the query key.

## State And Persistence

State is the inherited immutable parsed parameter value. No persistence exists.

## Dependencies And Integration Points

Used by `WebHdfsFileSystem.setTimes` with `ModificationTimeParam`.

## Risks

Negative values other than `-1` are rejected by the inherited range. Server semantics must continue treating `-1` as unchanged/default.

## Test Signals

Tests should parse valid timestamps, `-1`, invalid negatives, and query serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/AccessTimeParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/AclPermissionParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/AclPermissionParam.java

## Purpose

`AclPermissionParam` serializes and parses the `aclspec` WebHDFS parameter for ACL operations.

## Important APIs, Types, And Functions

It extends `StringParam`, defines mutable static `DOMAIN`, constructors from string and `List<AclEntry>`, test hooks `getAclPermissionPattern`, `setAclPermissionPattern`, parser `getAclPermission`, and helper `parseAclSpec`.

## Control Flow

Strings equal to empty default become null. ACL entry lists are converted to comma-separated stable ACL entry strings. Parsing delegates to `AclEntry.parseAclSpec` with caller-selected permission inclusion.

## State And Persistence

The static domain/pattern is mutable process-wide and initialized from the default HDFS client ACL regex. Individual params store parsed string values only.

## Dependencies And Integration Points

`WebHdfsFileSystem.initialize` can replace the pattern from configuration. ACL mutation methods use this parameter.

## Risks

Global mutable regex affects all clients in the JVM. Constructor from list calls `parseAclSpec` twice. Null entries serialize as empty components, which can be surprising.

## Test Signals

Tests should cover configured regex, empty/null ACLs, multiple entries, includePermission parsing, invalid specs, and process-wide pattern reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/AclPermissionParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/AllUsersParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/AllUsersParam.java

## Purpose

`AllUsersParam` models the `allusers` boolean query parameter for operations such as listing trash roots.

## Important APIs, Types, And Functions

It extends `BooleanParam`, defines `NAME = "allusers"` and default `false`, and supports Boolean/String constructors.

## Control Flow

String construction parses case-insensitive `true` or `false`; invalid values fail in `BooleanParam.Domain`.

## State And Persistence

Only inherited parameter value is stored.

## Dependencies And Integration Points

Used by `WebHdfsFileSystem.getTrashRoots(boolean allUsers)`.

## Risks

Null string handling is inherited and may fail if callers do not supply the explicit default.

## Test Signals

Tests should cover true/false parsing, invalid values, and query serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/AllUsersParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/BlockSizeParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/BlockSizeParam.java

## Purpose

`BlockSizeParam` represents optional WebHDFS `blocksize` values for file creation.

## Important APIs, Types, And Functions

It extends `LongParam`, defines `NAME = "blocksize"` and default `NULL`, supports Long/String constructors, and adds `getValue(Configuration)`.

## Control Flow

Explicit values must be at least 1. If unset, `getValue(conf)` returns `dfs.blocksize` from configuration with default fallback.

## State And Persistence

Only the parsed value is stored. Configuration is consulted on demand.

## Dependencies And Integration Points

Used by `WebHdfsFileSystem.create` and `createNonRecursive`.

## Risks

Differences between omitted query parameters and explicit default block size can affect server-side defaults. Very large values depend on `LongParam` and server validation.

## Test Signals

Tests should cover null default resolution, invalid zero/negative values, string parsing, and create URL serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/BlockSizeParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/BooleanParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/BooleanParam.java

## Purpose

`BooleanParam` is the package-private base for WebHDFS boolean query parameters.

## Important APIs, Types, And Functions

It extends `Param<Boolean, BooleanParam.Domain>`, defines string constants `TRUE` and `FALSE`, overrides `getValueString`, and defines nested `Domain` parser.

## Control Flow

The domain parser accepts case-insensitive `true` or `false` and rejects any other string. Value serialization calls `Boolean.toString`.

## State And Persistence

Only inherited parameter value/domain state exists.

## Dependencies And Integration Points

Subclasses include `AllUsersParam`, `CreateParentParam`, and other WebHDFS boolean params outside this subset.

## Risks

`getValueString` assumes `value` is non-null; callers must avoid serializing null-valued boolean params unless `Param` filters them first.

## Test Signals

Tests should cover case-insensitive parsing, invalid parse errors, null handling through `Param`, and subclass serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/BooleanParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/BufferSizeParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/BufferSizeParam.java

## Purpose

`BufferSizeParam` models optional WebHDFS `buffersize` values for open/create/append flows.

## Important APIs, Types, And Functions

It extends `IntegerParam`, defines `NAME = "buffersize"` and default `NULL`, constructors from Integer/String, and `getValue(Configuration)`.

## Control Flow

Explicit values must be at least 1. Unset values resolve to `io.file.buffer.size` from configuration.

## State And Persistence

Only inherited parsed value is stored.

## Dependencies And Integration Points

Used by `WebHdfsFileSystem` create, append, open, and read-runner URL construction.

## Risks

Omitted vs explicit buffer size can change URL behavior. Large values affect memory and HTTP stream buffering.

## Test Signals

Tests should cover default lookup, invalid zero/negative values, serialization, and open/read URL parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/BufferSizeParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/ConcatSourcesParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/ConcatSourcesParam.java

## Purpose

`ConcatSourcesParam` serializes the `sources` query parameter for WebHDFS concat operations.

## Important APIs, Types, And Functions

It extends `StringParam`, defines `NAME = "sources"`, constructors from raw string and `Path[]`, helper `paths2String`, and `getAbsolutePaths`.

## Control Flow

Path arrays are converted to comma-separated URI paths; null or empty arrays become empty string. `getAbsolutePaths` splits the stored string on commas.

## State And Persistence

Only inherited string value exists.

## Dependencies And Integration Points

Used by `WebHdfsFileSystem.concat`.

## Risks

Comma-separated encoding assumes paths cannot contain unescaped commas in a way that survives URI path conversion. Empty source arrays serialize as empty rather than being rejected locally.

## Test Signals

Tests should cover multiple paths, empty/null arrays, absolute path preservation, comma-containing paths if supported, and server-side concat validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/ConcatSourcesParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/CreateFlagParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/CreateFlagParam.java

## Purpose

`CreateFlagParam` serializes an `EnumSet<CreateFlag>` as the WebHDFS `createflag` parameter.

## Important APIs, Types, And Functions

It extends `EnumSetParam<CreateFlag>`, defines `NAME = "createflag"`, default empty string, domain over `CreateFlag.class`, and constructors from enum set or string.

## Control Flow

Enum sets are serialized by the inherited enum-set machinery. Strings are parsed by the domain into the corresponding enum set.

## State And Persistence

Only parsed enum-set value is stored.

## Dependencies And Integration Points

Used by `WebHdfsFileSystem.createNonRecursive`; create with overwrite uses `OverwriteParam` instead.

## Risks

Client and server must agree on enum names and delimiter format. Empty defaults must map to server-side create semantics.

## Test Signals

Tests should cover standard create flags, mixed-case string parsing if inherited, empty values, invalid flags, and create URL output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/CreateFlagParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/CreateParentParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/CreateParentParam.java

## Purpose

`CreateParentParam` models the WebHDFS `createparent` boolean parameter for create operations.

## Important APIs, Types, And Functions

It extends `BooleanParam`, defines `NAME = "createparent"` and default `true`, and supports Boolean/String constructors.

## Control Flow

String construction treats null as the default `true`; otherwise it parses through the boolean domain. `getName` returns the query key.

## State And Persistence

Only inherited parsed boolean value exists.

## Dependencies And Integration Points

Used by `WebHdfsFileSystem.createNonRecursive` with `false` and symlink/create APIs where parent creation is exposed.

## Risks

Defaulting null to true is operation-sensitive; callers that intend omission vs explicit true need to understand inherited serialization behavior.

## Test Signals

Tests should cover null string, true/false values, invalid values, and create-non-recursive URL behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/CreateParentParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/DelegationParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/DelegationParam.java

## Purpose

`DelegationParam` carries an encoded delegation token in the WebHDFS `delegation` query parameter.

## Important APIs, Types, And Functions

It extends `StringParam`, defines `NAME = "delegation"` and empty default, and has a string constructor plus `getName`.

## Control Flow

Null or empty-default strings become null, suppressing a parameter value through normal `Param` behavior. Non-empty strings are preserved.

## State And Persistence

Only the token string is stored in memory.

## Dependencies And Integration Points

`WebHdfsFileSystem.getAuthParameters` adds it when a delegation token is available.

## Risks

Tokens in URLs can be logged by clients, proxies, or servers. Empty strings are silently omitted.

## Test Signals

Tests should cover URL encoding of token strings, omission for null/empty, and secure-operation auth parameter selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/DelegationParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/DeleteOpParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/DeleteOpParam.java

## Purpose

`DeleteOpParam` models the WebHDFS `op` query parameter for HTTP DELETE operations.

## Important APIs, Types, And Functions

It extends `HttpOpParam<DeleteOpParam.Op>`. Enum `Op` includes `DELETE`, `DELETESNAPSHOT`, and `NULL`, each with expected HTTP code. Op methods define HTTP type, auth requirement, output behavior, redirect behavior, expected response, and query string.

## Control Flow

Construction parses a string into an enum op and rewrites invalid parse errors to identify DELETE operations. DELETE operations do not require auth at the op layer, do not output a body, and do not redirect.

## State And Persistence

Only parsed operation value is stored.

## Dependencies And Integration Points

Used by WebHDFS server/client op dispatch for file delete and snapshot delete. `WebHdfsFileSystem.delete` and `deleteSnapshot` use enum constants directly.

## Risks

Expected response-code mismatches break validation. Adding DELETE operations requires updating both client enum and server handling.

## Test Signals

Tests should cover op parsing, invalid op messages, expected HTTP codes, query string output, and delete/delete-snapshot calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/DeleteOpParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/DestinationParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/DestinationParam.java

## Purpose

`DestinationParam` carries absolute destination paths for WebHDFS rename and symlink operations.

## Important APIs, Types, And Functions

It extends `StringParam`, defines `NAME = "destination"`, empty default, static `validate`, constructor, and `getName`.

## Control Flow

Null or empty strings become null. Non-empty values must start with `/`; valid values are normalized through `new Path(str).toUri().getPath()`.

## State And Persistence

Only the validated path string is stored.

## Dependencies And Integration Points

Used by `WebHdfsFileSystem.rename`, rename with options, and `createSymlink`.

## Risks

Relative paths are rejected locally. Path normalization may alter raw encoding or redundant separators compared with caller input.

## Test Signals

Tests should cover absolute paths, relative path rejection, empty/null omission, URI normalization, and rename URL serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/DestinationParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/DoAsParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/DoAsParam.java

## Purpose

`DoAsParam` represents the `doas` query parameter for WebHDFS proxy-user requests.

## Important APIs, Types, And Functions

It extends `StringParam`, defines `NAME = "doas"` and empty default, with constructor and `getName`.

## Control Flow

Null or empty-default values are stored as null. Non-empty proxy user names are passed through the domain without a regex in this class.

## State And Persistence

Only the proxy user string is stored.

## Dependencies And Integration Points

`WebHdfsFileSystem.getAuthParameters` emits this when current UGI has a real user.

## Risks

Validation is delegated elsewhere, so malformed names reach server-side checks. User identity values in URLs can be logged.

## Test Signals

Tests should cover proxy-user auth parameter construction, omission for non-proxy users, empty/null values, and URL encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/DoAsParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/ECPolicyParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/ECPolicyParam.java

## Purpose

`ECPolicyParam` carries the WebHDFS `ecpolicy` string parameter for erasure-coding policy operations.

## Important APIs, Types, And Functions

It extends `StringParam`, defines `NAME = "ecpolicy"` and empty default, and has a string constructor plus `getName`.

## Control Flow

Null or empty-default values are stored as null; non-empty policy names are passed through.

## State And Persistence

Only inherited string value exists.

## Dependencies And Integration Points

Used by `WebHdfsFileSystem.enableECPolicy`, `disableECPolicy`, and `setErasureCodingPolicy`.

## Risks

Policy-name validity is deferred to the server. Empty policy may be meaningful for unset operations, so callers must use the right operation/param combination.

## Test Signals

Tests should cover common policy names, empty/null handling, URL encoding, and server rejection of invalid names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/ECPolicyParam.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/EnumParam.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/EnumParam.java

## Purpose

`EnumParam` is the package-private base for single-enum WebHDFS query parameters.

## Important APIs, Types, And Functions

It extends `Param<E, EnumParam.Domain<E>>`. Nested `Domain` stores the enum class, reports valid constants via `getDomain`, and parses strings with uppercase normalization.

## Control Flow

Subclasses provide a domain and enum value. Parsing calls `Enum.valueOf(enumClass, StringUtils.toUpperCase(str))`, so accepted strings are case-insensitive for ASCII enum names.

## State And Persistence

State is inherited parameter value plus the enum class in each domain.

## Dependencies And Integration Points

Used by WebHDFS resource params representing single enum values, while `CreateFlagParam` uses the related enum-set base.

## Risks

Null strings will fail in uppercase/valueOf paths. Enum renames or server/client enum mismatch break compatibility.

## Test Signals

Tests should cover lowercase/mixed-case parsing, invalid values, domain string output, and representative subclass serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/EnumParam.java -->
