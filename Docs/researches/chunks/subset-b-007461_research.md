# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_2.6.0.xml lines 16840-19520

## Purpose

This chunk is the public JDiff API surface for the Hadoop HDFS 2.6.0 WebHDFS client and WebHDFS REST parameter model. It begins at the tail of `org.apache.hadoop.hdfs.web.ParamFilter`, then covers `SWebHdfsFileSystem`, the full visible API of `WebHdfsFileSystem`, and the `org.apache.hadoop.hdfs.web.resources` classes that encode WebHDFS request parameters, operation enums, user injection, exception mapping, ACLs, snapshots, delegation tokens, and xattrs.

The code represented here is not implementation source; it is an XML API snapshot. That means method bodies, enum constant names, private helpers, and private state are not visible. The chunk is still substantive because it exposes the stable public/protected contract that WebHDFS clients, tests, Jersey resources, and compatibility tooling depended on in Hadoop HDFS 2.6.0.

At a high level, the API maps Hadoop `FileSystem` operations to HTTP/WebHDFS operations. `WebHdfsFileSystem` provides the `webhdfs://` implementation over HTTP; `SWebHdfsFileSystem` specializes it for secure HTTPS transport. The resource parameter classes define how REST query parameters are named, typed, serialized, parsed, and converted back to Hadoop types such as `Path`, `FsPermission`, `FsAction`, `AclEntry`, `XAttrCodec`, `CreateFlag`, `Options.Rename`, delegation tokens, and snapshot names.

## Important APIs, Types, and Functions

- `ParamFilter` ends in this range with `getRequestFilter()` and `getResponseFilter()` returning Jersey request/response filters. Its documented purpose is to lowercase parameter names so WebHDFS parameter names are treated case-insensitively.
- `SWebHdfsFileSystem` extends `WebHdfsFileSystem` and exposes secure scheme constants through public static final `SCHEME` and `TOKEN_KIND`. It overrides `getScheme()`, protected `getTransportScheme()`, protected `getTokenKind()`, and `getDefaultPort()`, making it the HTTPS/WebHDFS variant.
- `WebHdfsFileSystem` extends `org.apache.hadoop.fs.FileSystem` and implements `DelegationTokenRenewer.Renewable` plus `TokenAspect.TokenManagementDelegator`. It is the main `webhdfs` filesystem client surface.
- `WebHdfsFileSystem` connection and identity API includes synchronized `initialize(URI, Configuration)`, `getCanonicalUri()`, static `isEnabled(Configuration, Log)`, protected synchronized `getDelegationToken()`, `getDefaultPort()`, `getUri()`, protected `canonicalizeUri(URI)`, static `getHomeDirectoryString(UserGroupInformation)`, `getHomeDirectory()`, synchronized `getWorkingDirectory()`, and synchronized `setWorkingDirectory(Path)`.
- `WebHdfsFileSystem` file and metadata operations include `getFileStatus(Path)`, `getAclStatus(Path)`, `mkdirs(Path, FsPermission)`, `createSymlink(Path destination, Path f, boolean createParent)`, two `rename` overloads, xattr accessors and mutators, owner and permission changes, ACL mutators, snapshot create/delete/rename, replication and timestamp setters, `getDefaultBlockSize()`, `getDefaultReplication()`, `concat(Path, Path[])`, `create(...)`, `append(...)`, `delete(Path, boolean)`, `open(Path, int)`, synchronized `close()`, `listStatus(Path)`, block location lookups, `access(Path, FsAction)`, `getContentSummary(Path)`, and `getFileChecksum(Path)`.
- `WebHdfsFileSystem` delegation token API includes public `getDelegationToken(String renewer)`, synchronized `getRenewToken()`, `setDelegationToken(Token)`, synchronized `renewDelegationToken(Token)`, synchronized `cancelDelegationToken(Token)`, and `getCanonicalServiceName()`.
- `WebHdfsFileSystem` exposes public constants/fields `LOG`, `SCHEME`, `VERSION`, `PATH_PREFIX`, `TOKEN_KIND`, `CANT_FALLBACK_TO_INSECURE_MSG`, plus protected mutable `connectionFactory` and protected `tokenServiceName`. The `connectionFactory` doc explicitly notes that tests may override it to use smaller timeouts.
- Numeric parameter classes include `AccessTimeParam`, `BlockSizeParam`, `BufferSizeParam`, `LengthParam`, `ModificationTimeParam`, `OffsetParam`, and `ReplicationParam`. They extend `LongParam`, `IntegerParam`, or `ShortParam`, provide constructors from boxed values and strings, expose `NAME` and `DEFAULT`, and in the block/buffer/replication cases provide `getValue(Configuration)` to resolve defaults from configuration when the value is absent.
- String/path/security parameter classes include `DelegationParam`, `DestinationParam`, `DoAsParam`, `ExcludeDatanodesParam`, `GroupParam`, `NamenodeAddressParam`, `OldSnapshotNameParam`, `OwnerParam`, `RenewerParam`, `SnapshotNameParam`, `TokenArgumentParam`, `TokenKindParam`, `TokenServiceParam`, `UriFsPathParam`, and `UserParam`.
- `AclPermissionParam` extends `StringParam`, can be constructed from a string or `List`, and exposes `getAclPermission(boolean includePermission)` to decode ACL specs.
- `ConcatSourcesParam` extends `StringParam`, can be constructed from a string or `Path[]`, and exposes final `getAbsolutePaths()` for concat source resolution.
- `CreateParentParam`, `OverwriteParam`, and `RecursiveParam` extend `BooleanParam` and carry boolean WebHDFS switches for symlink parent creation, overwrite behavior, and recursive delete/list behavior.
- `FsActionParam` wraps `org.apache.hadoop.fs.permission.FsAction` and string forms for access checks.
- `PermissionParam` extends `ShortParam`, can be constructed from `FsPermission` or string, exposes static `getDefaultFsPermission()`, and converts back with `getFsPermission()`.
- `RenameOptionSetParam` extends `EnumSetParam`, can be constructed from `Options.Rename[]` or string, and represents WebHDFS rename option sets.
- `Param<T, D extends Param.Domain<T>>` is the abstract base for request parameters. It exposes static `toSortedString(String separator, Param[] parameters)`, final `getValue()`, abstract `getValueString()`, abstract `getName()`, and `toString()`.
- `HttpOpParam` extends `EnumParam` and is the abstract base for the `op` query parameter. It exposes `NAME`, `DEFAULT`, and overrides `getValueString()`.
- `HttpOpParam.Op` is the operation interface implemented by all operation enums. It exposes `getType()`, `getRequireAuth()`, `getDoOutput()`, `getRedirect()`, `getExpectedHttpResponseCode()`, and `toQueryString()`.
- `HttpOpParam.TemporaryRedirectOp` wraps an existing `HttpOpParam.Op`, preserves operation metadata, and overrides the expected response code to HTTP 307 Temporary Redirect.
- `HttpOpParam.Type` is the HTTP method/category enum for operations. JDiff exposes `values()` and `valueOf(String)` but not enum constants.
- `DeleteOpParam`, `GetOpParam`, `PostOpParam`, and `PutOpParam` each extend `HttpOpParam` and parse string operation names. Their nested `Op` enums implement `HttpOpParam.Op` and expose the same operation metadata methods. JDiff does not list the individual operation constants, but this API is the central contract used to map REST `op=` values to behavior.
- `ExceptionHandler` implements `javax.ws.rs.ext.ExceptionMapper`, exposes `toResponse(Exception)` and `initResponse(HttpServletResponse)`, and is documented as the WebHDFS exception handler.
- `UserProvider` extends Jersey's `AbstractHttpContextInjectable` and implements `InjectableProvider`; it exposes `getValue(HttpContext)`, `getScope()`, and `getInjectable(ComponentContext, Context, Type)` to inject `UserGroupInformation` into HTTP operations.
- XAttr parameter classes include `XAttrEncodingParam`, `XAttrNameParam`, `XAttrSetFlagParam`, and `XAttrValueParam`. They encode xattr codec selection, xattr names, `EnumSet` create/replace flags, and string-to-byte value decoding.

## Control Flow

The XML does not include method bodies, but the API shape shows the WebHDFS call path. Client code obtains a `FileSystem` instance for `webhdfs://` or secure `swebhdfs://`, `initialize()` binds it to a URI and `Configuration`, then high-level `FileSystem` methods translate Hadoop operations into HTTP requests using `HttpOpParam` and the typed resource parameters. Methods that need mutable client state, such as initialization, working-directory access, close, and delegation token renewal/cancel operations, are marked synchronized in the API snapshot.

Operation dispatch is organized around the `op` parameter. `GetOpParam`, `PutOpParam`, `PostOpParam`, and `DeleteOpParam` parse a string operation value into a nested enum implementing `HttpOpParam.Op`. The operation object then tells the HTTP layer which method/type to use, whether authentication must be direct rather than token-based, whether the request writes a body, whether the call redirects, and which HTTP status code is expected. `TemporaryRedirectOp.valueOf(Op)` is a wrapper path used when a request should expect HTTP 307 instead of the original operation response.

Resource parameters follow a common parse/serialize flow. Each class names a query parameter through `NAME`, supplies a string `DEFAULT` where applicable, accepts either a typed value or a string representation, and returns a typed value through either `getValue()`, a specialized conversion method, or a default-resolving method. `Param.toSortedString(separator, parameters)` provides deterministic parameter encoding for URI query strings, which matters for stable tests, logging, and tokenized request construction.

`WebHdfsFileSystem` exposes the client side of almost every HDFS filesystem behavior supported over WebHDFS in this API version: file status/listing, open/create/append/delete, mkdirs, rename, symlinks, owner/permission/ACL/xattr mutation, snapshots, concat, replication, timestamps, checksums, block locations, access checks, and content summaries. Reads and writes likely route through NameNode WebHDFS endpoints and, for data transfer operations, DataNode redirects; the redirect metadata is reflected in the operation API even though the implementation bodies are outside this XML.

Delegation token control flow is also visible at the contract level. The filesystem acts as a renewable token owner for Hadoop's `DelegationTokenRenewer`, can get or set the active delegation token, returns a renew token, and exposes synchronized renew/cancel methods. Token-related query parameters split authentication token usage (`DelegationParam`) from token method arguments (`TokenArgumentParam`), token kind (`TokenKindParam`), token service (`TokenServiceParam`), and renewer identity (`RenewerParam`).

Server-side REST integration is represented by `ParamFilter`, `ExceptionHandler`, and `UserProvider`. `ParamFilter` normalizes query names to lower case before Jersey resource binding. `UserProvider` produces `UserGroupInformation` from the HTTP context for resource methods. `ExceptionHandler` maps thrown exceptions into JAX-RS responses and can initialize the servlet response, forming the public error-conversion hook.

## State and Persistence Behavior

`WebHdfsFileSystem` is stateful as a Hadoop `FileSystem` instance. Visible mutable or per-instance state includes protected `connectionFactory` and `tokenServiceName`; synchronized methods indicate internal state for initialization, working directory, close lifecycle, and token renewal. The public fields `SCHEME`, `VERSION`, `PATH_PREFIX`, and `TOKEN_KIND` are stable protocol constants. `SWebHdfsFileSystem` changes scheme, transport scheme, token kind, and default port but otherwise inherits WebHDFS behavior.

The parameter classes are value objects around parsed query values. They preserve both typed value behavior and string serialization behavior. Defaults are encoded as public static strings, while some classes resolve effective values from a `Configuration`: `BlockSizeParam.getValue(conf)`, `BufferSizeParam.getValue(conf)`, and `ReplicationParam.getValue(conf)` use cluster/client defaults when no parameter value is provided. `PermissionParam.getDefaultFsPermission()` centralizes default permission behavior.

Persistence is mostly indirect. The classes do not store metadata themselves; they encode operations that persist changes in HDFS NameNode state: directories/files, symlinks, permissions, ACLs, xattrs, snapshots, replication, timestamps, and tokens. For writes and appends, the API returns Hadoop stream types (`FSDataOutputStream`, `FSDataInputStream`) whose underlying implementation persists data through WebHDFS HTTP flows. XAttr values are byte arrays decoded from string parameters and therefore have encoding-sensitive persistence behavior.

Security state is externalized through `UserGroupInformation` and Hadoop delegation tokens. `UserParam` can be built from a UGI and exposes static mutation of its username pattern domain through `getUserPatternDomain()`, `setUserPatternDomain(...)`, and `setUserPattern(String)`. That static configurability is process-wide API state and can affect parsing/validation of user parameters across requests/tests.

`Param.toSortedString(...)` provides deterministic serialization of parameter sets. This is a state-stability behavior rather than persistence, but it matters because REST URLs, logs, and signatures/tests can depend on repeatable query ordering.

## Dependencies and Integration Points

This chunk integrates Hadoop filesystem, security, HDFS, Jersey, servlet, and JAX-RS APIs:

- Hadoop core filesystem APIs: `FileSystem`, `Path`, `FileStatus`, `FSDataInputStream`, `FSDataOutputStream`, `BlockLocation`, `ContentSummary`, `MD5MD5CRC32FileChecksum`, `FsPermission`, `AclStatus`, `FsAction`, `Options.Rename`, `XAttrCodec`, and xattr set flags.
- Hadoop configuration and utility APIs: `Configuration`, `Progressable`, `Log`, and `Text`.
- Hadoop security APIs: `UserGroupInformation`, `Token`, `DelegationTokenRenewer.Renewable`, and WebHDFS `TokenAspect.TokenManagementDelegator`.
- HDFS server/client integration: `NameNode` for `NamenodeAddressParam`, WebHDFS URI schemes and token kinds, NameNode/Datanode REST redirect behavior implied by `HttpOpParam.Op.getRedirect()`, and WebHDFS enablement through `WebHdfsFileSystem.isEnabled(conf, log)`.
- Jersey/JAX-RS/servlet integration: `ContainerRequestFilter`, `ContainerResponseFilter`, `ExceptionMapper`, `Response`, `HttpServletResponse`, `HttpContext`, `ComponentContext`, `Context`, `Injectable`, `InjectableProvider`, `ComponentScope`, and Jersey `AbstractHttpContextInjectable`.
- Java platform types: `URI`, `IOException`, `EnumSet`, `List`, `Map`, `Type`, primitive wrapper constructors, strings, arrays, and byte arrays.

The merge/reconciliation lane should connect this chunk with earlier WebHDFS classes in the same XML, especially lower-level parameter base classes such as `BooleanParam`, `IntegerParam`, `LongParam`, `ShortParam`, `StringParam`, `EnumParam`, and `EnumSetParam` if they occur in prior chunks. This chunk references those base classes but does not define them.

## Risks and Edge Cases

- This is a JDiff API snapshot, not source code. It does not show method bodies, enum constant names, private fields, generic bounds in full fidelity, or implementation details such as retry policy, redirect URL construction, JSON parsing, stream handling, or exception mapping internals. Research consumers should not treat inferred control flow as line-by-line implementation.
- WebHDFS is a public compatibility surface. Changes to method signatures, query parameter names, operation metadata, defaults, expected HTTP status codes, or token kind/scheme constants can break existing clients and REST tests.
- `ParamFilter` lowercases parameter names, making query-name matching case-insensitive. Any code that assumes case-sensitive duplicate parameters or preserves original query casing could behave differently through this filter.
- `HttpOpParam.Op.getRequireAuth()` distinguishes operations that cannot use a token. Mistakes in this metadata can create security regressions by permitting token fallback where direct auth is required, or availability regressions by rejecting valid token-based calls.
- `HttpOpParam.Op.getRedirect()` and `TemporaryRedirectOp` are critical for data-path operations. Wrong expected status handling can cause clients to treat redirects as failures, fail to follow NameNode-to-DataNode redirects, or accept the wrong response code.
- `WebHdfsFileSystem.connectionFactory` is protected and documented as test-overridable. That is useful for timeout-sensitive tests but also means subclasses/tests can alter network behavior process-locally.
- Several state-affecting methods are synchronized, but most file operations are not. The filesystem likely relies on immutable per-call parameters and internal thread-safe helpers for regular operations; callers should still be careful when mutating working directory or tokens concurrently.
- `UserParam` exposes static setters for username pattern validation. Tests that change the pattern/domain can leak process-wide state into later tests unless restored.
- String-backed parameters for paths, ACLs, xattrs, token material, and usernames are encoding- and validation-sensitive. Bad escaping, malformed ACL specs, malformed xattr values, or invalid path normalization can propagate into HDFS operations.
- `BlockSizeParam`, `BufferSizeParam`, and `ReplicationParam` default from `Configuration`. Tests must pin configuration values when asserting effective values; otherwise cluster defaults can make behavior environment-dependent.
- `PermissionParam` represents `FsPermission` as a short. Leading-zero/octal formatting and default permission semantics are easy places for test and client mistakes.
- XAttr parameters convert between query strings, byte arrays, codecs, and enum sets. Incompatible encoding choices or missing set flags can produce incorrect persisted xattr values or wrong create/replace behavior.
- The chunk starts inside `ParamFilter` and ends at the XML/API close. Complete class-level documentation for `ParamFilter` and any package-level context may live outside this range.

## Test Signals

Useful validation should exercise both public API compatibility and WebHDFS behavior:

- Verify `WebHdfsFileSystem.getScheme()` returns `webhdfs`, `SWebHdfsFileSystem.getScheme()` returns the secure scheme, and secure transport/token-kind/default-port behavior remains distinct from the base class.
- Instantiate WebHDFS through `FileSystem` with a minimal `Configuration`, confirm `initialize()`, `getUri()`, `getCanonicalUri()`, `getHomeDirectory()`, and synchronized working-directory getters/setters behave consistently.
- Test `WebHdfsFileSystem.isEnabled(conf, log)` with WebHDFS enabled and disabled configuration values.
- Exercise representative WebHDFS operations against a mini HDFS cluster: `mkdirs`, `create`, `append`, `open`, `listStatus`, `getFileStatus`, `rename`, `delete`, `setPermission`, `setOwner`, ACL mutation/readback, xattr mutation/readback, snapshots, concat, checksums, block locations, content summary, and `access`.
- Run secure and insecure token flows: `getDelegationToken(renewer)`, `getRenewToken()`, `setDelegationToken(token)`, `renewDelegationToken(token)`, `cancelDelegationToken(token)`, and `getCanonicalServiceName()`.
- Verify `Param.toSortedString(separator, params)` sorts parameters deterministically and encodes null/default values as intended by each parameter domain.
- Round-trip each parameter class from typed value to string and from string back to typed value, especially `AclPermissionParam`, `ConcatSourcesParam`, `FsActionParam`, `PermissionParam`, `RenameOptionSetParam`, `UriFsPathParam`, `UserParam`, and the XAttr parameter classes.
- Validate `BlockSizeParam.getValue(conf)`, `BufferSizeParam.getValue(conf)`, and `ReplicationParam.getValue(conf)` with explicit values, absent values, and changed configuration defaults.
- Check operation metadata for GET/PUT/POST/DELETE ops: type, auth requirement, output flag, redirect flag, expected HTTP response code, and query string. Include `TemporaryRedirectOp.valueOf(op)` to confirm only the expected response code changes to 307 while other metadata is preserved.
- Exercise server-side Jersey integration with mixed-case parameter names to confirm `ParamFilter` lowercases request parameters; verify `UserProvider` injects expected `UserGroupInformation`; verify `ExceptionHandler.toResponse(Exception)` maps common HDFS/WebHDFS exceptions to expected HTTP responses.
- Include concurrency tests around working directory and token methods if subclasses or test code share a `WebHdfsFileSystem` instance.

## Chunk Boundary Notes

Lines 16840-19520 cover the end of `ParamFilter`, all visible `SWebHdfsFileSystem` and `WebHdfsFileSystem` API entries in this XML, the `org.apache.hadoop.hdfs.web.resources` package entries from `AccessTimeParam` through `XAttrValueParam`, and the closing `</api>`. The final per-file report should merge this with adjacent chunks for the earlier WebHDFS package classes and the parameter base classes that this range depends on.
