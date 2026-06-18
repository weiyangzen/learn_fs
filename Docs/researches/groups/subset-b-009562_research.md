# subset-b-009562 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/attr_cache/attr_cache.go -->
# sources/user-network-fs/blobfuse2/component/attr_cache/attr_cache.go

Purpose: implements the `attr_cache` pipeline component for BlobFuse. It sits above a storage component, caches positive and negative `internal.ObjAttr` lookups, invalidates entries after mutating filesystem operations, and runs a background expiry pass to prevent stale entries from accumulating indefinitely.

Important APIs/types/functions: `AttrCache` embeds `internal.BaseComponent` and implements `internal.Component`; `AttrCacheOptions` exposes `timeout-sec`, `max-files`, `no-symlinks`, and legacy cache-on-list knobs; `Start` initializes `cacheMap` and launches `backgroundCleanup`; `Stop` cancels and waits for cleanup; `Configure` reads component config and defaults to 120 seconds and 5 million cached files. Helper methods include `deleteDirectory`, `deletePath`, `invalidateDirectory`, `invalidatePath`, `updateCacheEntry`, `cacheAttributes`, and `cleanupExpiredEntries`. Public filesystem methods wrap next-component calls such as `CreateDir`, `DeleteDir`, `ReadDir`, `StreamDir`, `RenameDir`, `CreateFile`, `DeleteFile`, `RenameFile`, `WriteFile`, `TruncateFile`, `CopyFromFile`, `SyncFile`, `SyncDir`, `GetAttr`, `CreateLink`, `FlushFile`, `Chmod`, `Chown`, and `CommitData`.

Control flow: reads usually try cache first and fall through to `NextComponent` on miss, invalid, or expired entries. `GetAttr` truncates trailing directory separators, returns cached ENOENT for valid deleted entries, caches successful attributes, and caches `syscall.ENOENT` as a negative entry. Directory listings flow through storage first and then bulk-cache returned attributes. Mutating operations call the next component first, then mark affected cache entries deleted or invalid on success. Rename-directory recursively deletes the source subtree and invalidates the destination subtree; rename-file copies source attributes into a destination cache entry when it exists, then marks source deleted. Writes and copy-from-file first call `GetAttr` with metadata retrieval so existing metadata can be forwarded to storage.

State and persistence: all state is in-memory: `cacheMap`, `cacheTimeout`, `maxFiles`, cleanup context, and the cleanup done channel. Entries are keyed by truncated path and store `attrCacheItem` values. No on-disk persistence exists. Expiry is based on each item's `cachedAt`. The cleanup goroutine ticks at `cacheTimeout` seconds, with a one-second fallback for zero or negative intervals.

Dependencies/integration: depends on `common/config` for config, `common/log`, `internal` component contracts and path helpers, `handlemap`, Go contexts, locks, `syscall`, and `os` error checks. It registers as `attr_cache` and binds CLI/config flags in `init`.

Risks: several success paths acquire `cacheLock.RLock()` and then mutate entries via `markDeleted`, `invalidate`, `setSize`, `setMode`, or assignment through helper methods. That protects the map from structural writes only weakly and does not provide exclusive protection for item mutation; race detection would be important. `cacheAttributes` checks `len(ac.cacheMap)` outside the write lock and then writes under a per-item lock, so concurrent growth may overshoot `maxFiles`. `no-cache-on-list` is present in options but listing methods always cache returned attributes. `GetAttr` returns cached attr pointers directly through `getAttr`, so callers can potentially observe or mutate shared cached state.

Test signals: `attr_cache_test.go` covers default/config parsing, create/delete/rename directory and file cache effects, listing cache population, negative ENOENT caching, timeout behavior, cleanup removal, symlink invalidation, chmod/chown behavior, and path-prefix safety for nested directory operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/attr_cache/attr_cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/attr_cache/attr_cache_test.go -->
# sources/user-network-fs/blobfuse2/component/attr_cache/attr_cache_test.go

Purpose: provides the primary unit test suite for the `attr_cache` component. It uses gomock to isolate the next pipeline component and testify suite/assertions to verify cache mutations after each filesystem method.

Important APIs/types/functions: `attrCacheTestSuite` owns assertions, the `AttrCache` under test, gomock controller, and `internal.MockComponent`. Helpers include `newTestAttrCache`, `getPathAttr`, `addPathToCache`, `assertDeleted`, `assertInvalid`, `assertUntouched`, `assertAttributesTransferred`, `assertSrcAttributeTimeChanged`, `generateNestedDirectory`, `generateNestedPathAttr`, and `addDirectoryToCache`. Tests are grouped by component method: config tests, directory operations, listing, file operations, `GetAttr`, timeout and cleanup, links, chmod, and chown.

Control flow: each test constructs a cache connected to a mock next component, seeds `cacheMap` where needed, sets gomock expectations for success or failure, invokes the attr-cache method, then inspects cache entries directly. Many tests loop over both `a` and `a/` to validate path truncation. Nested directory fixtures intentionally include `a`, children under `a/`, sibling prefix `ab`, and sibling file `ac` to detect accidental prefix overmatching.

State and persistence behavior: tests directly manipulate in-memory `cacheMap` and rely on `Start`/`Stop` to create and tear down the cleanup goroutine. They exercise negative entries, invalid entries, positive attr entries, timeout-driven cleanup, and config-derived fields such as `cacheTimeout`, `maxFiles`, and `noSymlinks`. No persistent state is involved.

Dependencies/integration: imports the repository's `common`, `config`, `log`, `internal`, and `handlemap` packages plus gomock and testify. The suite expects generated mocks for `internal.Component`. The silent logger avoids noisy test output; config is loaded from strings via `config.ReadConfigFromReader`.

Risks: the tests inspect private fields because they are in the same package, which is useful for cache correctness but couples tests to representation. Some assertions rely on wall-clock sleeps for timeout cleanup and may be timing-sensitive. The tests do not appear to run with race detection or assert lock correctness, leaving the RLock-while-mutating risk in the implementation uncovered. `getPathAttr` accepts a `metadata` parameter but does not set metadata, suggesting older metadata-specific behavior may have been simplified without test helper cleanup.

Test signals: strong coverage exists for cache invalidation semantics, deleted-entry ENOENT behavior, cleanup expiry, and path-prefix correctness. Coverage is weaker for concurrent access, `maxFiles` enforcement under concurrency, dynamic config reload, and the unused `no-cache-on-list` setting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/attr_cache/attr_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/attr_cache/cacheMap.go -->
# sources/user-network-fs/blobfuse2/component/attr_cache/cacheMap.go

Purpose: defines the per-path cache entry used by `AttrCache`. It stores the cached object attributes, the cache timestamp, and bitmap flags indicating whether the entry is valid and whether the path exists.

Important APIs/types/functions: constants `AttrFlagUnknown`, `AttrFlagExists`, and `AttrFlagValid` define bitmap positions. `attrCacheItem` contains `attr *internal.ObjAttr`, `cachedAt time.Time`, and `attrFlag common.BitMap64`. `newAttrCacheItem` initializes a valid positive or negative entry. Methods include `valid`, `exists`, `markDeleted`, `invalidate`, `getAttr`, `isDeleted`, `setSize`, and `setMode`.

Control flow: positive entries are created with both valid and exists bits set. Negative entries are valid but not exists. `markDeleted` converts any item into a valid negative entry with empty attributes and a supplied deletion timestamp. `invalidate` clears validity and resets attributes to an empty object. `setSize` and `setMode` update selected attributes and refresh `cachedAt`.

State and persistence behavior: entries are pure in-memory state and are stored in `AttrCache.cacheMap`. The timestamp drives both `GetAttr` staleness checks and background cleanup. There is no per-entry mutex, deep-copying, or persistence.

Dependencies/integration: depends on `common.BitMap64`, `internal.ObjAttr`, `os.FileMode`, and `time`. It is tightly coupled to `attr_cache.go`, which decides when to call the mutating methods.

Risks: methods mutate `attr`, `attrFlag`, and timestamps without their own locking; callers must provide synchronization. `getAttr` returns the stored pointer directly, so external callers can observe shared state. `setSize` and `setMode` assume `attr` is non-nil and suitable for mutation; callers check `valid` and `exists` before these calls in current code.

Test signals: `attr_cache_test.go` asserts deleted, invalid, untouched, chmod, truncate, and rename behaviors by directly inspecting this structure. Race and pointer-aliasing behavior is not tested.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/attr_cache/cacheMap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/azauth.go -->
# sources/user-network-fs/blobfuse2/component/azstorage/azauth.go

Purpose: defines the common authentication configuration and factory for Azure Storage connections. It chooses the correct auth implementation for Blob or ADLS accounts and centralizes Azure Identity client option construction.

Important APIs/types/functions: `azAuthConfig` carries account name/type, protocol, auth mode, key/SAS/MSI/SPN/workload identity fields, OAuth resource and authority overrides, and endpoint. `azAuth` is the interface implemented by each auth mode with `getEndpoint`, `setOption`, and `getServiceClient`. `getAzAuth`, `getAzBlobAuth`, and `getAzDatalakeAuth` dispatch by account type and auth mode. `azAuthBase` supplies default endpoint and no-op option behavior. `azOAuthBase.getAzIdentityClientOptions` builds `azcore.ClientOptions`.

Control flow: storage setup calls `getAzAuth` with parsed config. The factory logs account details, selects Blob or ADLS, then returns a concrete key, SAS, MSI, SPN, Azure CLI, or workload identity wrapper. Unsupported auth modes log critical errors and return nil. OAuth option creation starts from cloud configuration for the storage endpoint, adds SDK logging, and optionally overrides Active Directory authority host and resource manager endpoint.

State and persistence behavior: auth config is copied into each concrete auth object. SAS auth can later update its in-memory `SASKey` through `setOption`; other modes ignore dynamic options by default. No credentials are persisted here.

Dependencies/integration: depends on Azure SDK `azcore` and `cloud`, local logging, account/auth enum helpers, cloud configuration and SDK log helpers defined elsewhere in azstorage. Concrete auth implementations in sibling files satisfy the `azAuth` interface.

Risks: a nil return from the factory is the main failure signal and must be checked by storage setup. The OAuth resource override mutates `cloud.ResourceManager`, which is used as the service scope in the SDK options; correctness depends on the rest of the SDK expecting this shape for storage auth. Config contains many credential fields in memory, so logging must avoid printing secrets; this file logs account and endpoint only.

Test signals: `azauth_test.go` exercises invalid auth/account cases and each major auth mode at integration level through `NewAzStorageConnection`, `SetupPipeline`, and `TestPipeline`, but relies on external Azure credentials.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/azauth.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/azauthWorkloadIdentity.go -->
# sources/user-network-fs/blobfuse2/component/azstorage/azauthWorkloadIdentity.go

Purpose: implements workload identity/client assertion authentication for Blob and ADLS service clients. It exchanges a managed identity token for a client assertion credential, optionally using an on-behalf-of flow.

Important APIs/types/functions: `azAuthWorkloadIdentity` embeds `azAuthBase` and `azOAuthBase`; `getTokenCredential` returns an `azcore.TokenCredential`. `azAuthBlobWorkloadIdentity.getServiceClient` constructs a Blob service client, while `azAuthDatalakeWorkloadIdentity.getServiceClient` constructs an ADLS service client.

Control flow: `getTokenCredential` builds identity client options, creates a managed identity credential using `ApplicationID` as client ID, then defines a callback that requests a token for `api://AzureADTokenExchange` or the configured auth resource. If `UserAssertion` is empty, it creates `ClientAssertionCredential`; otherwise it creates an on-behalf-of credential with client assertions. Service-client methods obtain this credential, build storage service client options, and call the Azure SDK client constructors.

State and persistence behavior: no durable state exists. Tokens are obtained through Azure Identity credential objects and callback flow. Config values remain in memory on the auth object.

Dependencies/integration: depends on Azure SDK `azidentity`, `azcore`, token policy options, Blob service client, ADLS service client, and local logging/client option helpers. It is selected by `azauth.go` when `AuthMode` is workload identity.

Risks: token acquisition uses `context.Background()` inside the client assertion callback rather than the callback's provided context, limiting cancellation propagation. `ApplicationID` is always used as the managed identity client ID; absent or wrong values will fail later during token retrieval. The behavior of `AuthResource` is overloaded as both token exchange scope and cloud service override through the shared OAuth option helper.

Test signals: no dedicated unit test appears in this file set. Integration coverage would require a correctly configured managed identity and workload identity environment, which `azauth_test.go` does not explicitly enumerate.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/azauthWorkloadIdentity.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/azauth_test.go -->
# sources/user-network-fs/blobfuse2/component/azstorage/azauth_test.go

Purpose: provides integration tests for azstorage authentication modes. The tests verify that invalid auth/account configurations fail and that valid key, SAS, MSI, SPN-related, and Azure CLI configurations can set up and test a storage pipeline.

Important APIs/types/functions: `storageTestConfiguration` maps `~/azuretest.json` fields for block and ADLS accounts, containers, keys, SAS tokens, MSI identifiers, SPN credentials, skip flags, and proxy address. `authTestSuite.SetupTest` configures a base logger and loads the JSON file. `validateStorageTest` builds `NewAzStorageConnection`, runs `SetupPipeline`, and calls `TestPipeline`. `generateEndpoint` builds Blob or DFS endpoints.

Control flow: each test constructs `AzStorageConfig` with an embedded `azAuthConfig`, then validates either expected failure or successful pipeline authentication. Invalid cases include unsupported auth mode, invalid account type, empty or malformed shared key, and empty SAS. Positive cases cover block/adls shared key, SAS, container SAS, MSI by application/resource/object ID, and Azure CLI. SAS tests also exercise `UpdateServiceClient("saskey", ...)`.

State and persistence behavior: tests read external persistent config from the user's home directory and write logs to `./logfile.txt`. They do not create repository state. Runtime storage clients authenticate against real Azure services.

Dependencies/integration: depends on local `common` and `log`, the azstorage configuration/connection stack, testify suite/assert, the OS home directory, and a live Azure account configuration. The build tag `!authtest` means these tests are included unless the `authtest` tag is set, but they still require external setup.

Risks: tests call `os.Exit(1)` from setup on missing config or logger setup failures, which can abort the whole package test run rather than reporting a normal test failure. They are environment-dependent and may be flaky due to network, Azure service state, credential expiry, or local Azure CLI login. Secrets are loaded from a home-dir JSON file, so developer machines and CI need careful secret handling.

Test signals: useful as broad live-auth smoke tests across account types and auth modes. They do not mock credential construction, do not cover workload identity explicitly, and do not isolate individual auth wrapper failure branches beyond the storage pipeline boundary.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/azauth_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/azauthcli.go -->
# sources/user-network-fs/blobfuse2/component/azstorage/azauthcli.go

Purpose: implements Azure CLI authentication for Blob and ADLS service clients using Azure Identity's CLI credential.

Important APIs/types/functions: `azAuthCLI` embeds `azAuthBase` and provides `getTokenCredential`, which calls `azidentity.NewAzureCLICredential(nil)`. `azAuthBlobCLI.getServiceClient` and `azAuthDatalakeCLI.getServiceClient` create Blob and ADLS service clients respectively.

Control flow: service-client creation gets a CLI token credential, builds storage SDK client options through shared helpers, then calls `service.NewClient` for Blob or `serviceBfs.NewClient` for ADLS. Errors from credential or option construction are logged and returned immediately; client creation errors are logged and returned.

State and persistence behavior: the auth object stores only config. Authentication state is external to the process in the user's Azure CLI login/cache. No token or credential data is persisted by this code.

Dependencies/integration: depends on `azidentity`, `azcore`, Blob and ADLS service packages, and local logging/options helpers. It is selected by the central auth factory for `AZCLI` auth mode.

Risks: runtime behavior depends on the `az` CLI being installed, authenticated, and authorized for the storage account. `NewAzureCLICredential(nil)` does not receive the custom cloud/client options used by MSI/SPN flows, so sovereign cloud or custom authority behavior may differ from other OAuth modes.

Test signals: `azauth_test.go` includes block and ADLS Azure CLI tests that expect `TestPipeline` errors when `SkipAzCLI` is true and success otherwise.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/azauthcli.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/azauthkey.go -->
# sources/user-network-fs/blobfuse2/component/azstorage/azauthkey.go

Purpose: implements shared-key authentication for Blob and ADLS storage accounts.

Important APIs/types/functions: `azAuthKey` embeds `azAuthBase`. `azAuthBlobKey.getServiceClient` validates `AccountKey`, creates an `azblob.SharedKeyCredential`, builds Blob service client options, and constructs a Blob service client. `azAuthDatalakeKey.getServiceClient` mirrors this with `azdatalake.NewSharedKeyCredential` and the ADLS service client.

Control flow: empty shared keys fail fast with a logged error and explicit error value. Invalid key material fails during SDK credential construction. Valid credentials are paired with shared storage client options and used to create service clients for the configured endpoint.

State and persistence behavior: account key is held in memory in `azAuthConfig`. No key material is written by this code. Service clients retain SDK credential state after construction.

Dependencies/integration: depends on Azure SDK Blob and ADLS shared-key credential constructors, service client packages, local logging, and client option helpers. It is selected by `azauth.go` for `KEY` auth mode.

Risks: shared keys are high-value secrets kept in process memory. The implementation guards against empty keys but not accidental logging elsewhere. Invalid base64 or malformed keys are surfaced from SDK constructors. Consumers must ensure HTTPS unless explicitly configured otherwise.

Test signals: `azauth_test.go` covers empty block/adls keys, malformed block key, and positive shared-key auth for block and ADLS accounts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/azauthkey.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/azauthmsi.go -->
# sources/user-network-fs/blobfuse2/component/azstorage/azauthmsi.go

Purpose: implements managed identity authentication for Blob and ADLS storage clients.

Important APIs/types/functions: `azAuthMSI` embeds `azAuthBase` and `azOAuthBase`; `getTokenCredential` builds `azidentity.ManagedIdentityCredentialOptions` and chooses client ID, resource ID, or object ID when configured. `azAuthBlobMSI.getServiceClient` and `azAuthDatalakeMSI.getServiceClient` build the respective storage clients.

Control flow: credential creation starts with shared OAuth client options. Identity selection priority is `ApplicationID`, then `ResourceID`, then `ObjectID`. If none is provided, the default managed identity is used. Service-client methods get the token credential, build client options, construct SDK clients, and propagate errors.

State and persistence behavior: only config is stored in memory. The actual token lifecycle is managed by Azure Identity and the managed identity endpoint. No persistent state is written.

Dependencies/integration: depends on `azidentity`, `azcore`, Blob/ADLS service packages, and local logging/options helpers. A commented-out Azure CLI fallback for object ID remains but is inactive.

Risks: only one identity selector is honored due to priority order; conflicting config silently picks the first non-empty value. Managed identity failures generally occur when acquiring tokens rather than when the credential object is built, so pipeline validation is important. The custom authority/resource behavior comes from `azOAuthBase`.

Test signals: `azauth_test.go` includes block MSI tests for app/resource/object IDs and ADLS MSI app/resource ID tests, gated by `SkipMsi`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/azauthmsi.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/azauthsas.go -->
# sources/user-network-fs/blobfuse2/component/azstorage/azauthsas.go

Purpose: implements SAS-token authentication for Blob and ADLS service clients.

Important APIs/types/functions: `azAuthSAS` embeds `azAuthBase`, overrides `setOption` for `saskey`, and overrides `getEndpoint` to append the SAS token to the configured endpoint. `azAuthBlobSAS.getServiceClient` and `azAuthDatalakeSAS.getServiceClient` create no-credential SDK service clients.

Control flow: service-client creation rejects empty SAS keys, builds the relevant storage SDK client options, then calls `NewClientWithNoCredential` with the endpoint plus normalized SAS query. `strings.TrimLeft(..., "?")` allows either raw or question-mark-prefixed SAS values. Dynamic SAS refresh flows through `setOption` and later service-client recreation.

State and persistence behavior: SAS token is stored in memory in `azAuthConfig`. No token is written to disk. `getEndpoint` constructs a full URL containing the token each time it is called.

Dependencies/integration: depends on Blob and ADLS service client packages, logging, strings, and client option helpers. `BlockBlob.UpdateServiceClient` uses this auth mode's `setOption` to refresh SAS credentials.

Risks: SAS-bearing endpoints include secret query parameters. Logging code must avoid printing full SAS endpoints; this file logs only failures and not the full constructed endpoint. Empty SAS fails early, but expired or insufficient SAS permissions fail during pipeline validation or operations.

Test signals: `azauth_test.go` covers empty SAS failures, account/container SAS success paths, HTTP container SAS, ADLS SAS, and dynamic SAS update through `UpdateServiceClient`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/azauthsas.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/azauthspn.go -->
# sources/user-network-fs/blobfuse2/component/azstorage/azauthspn.go

Purpose: implements service-principal authentication for Blob and ADLS, including client secret, federated token file, and workload identity token assertion flows.

Important APIs/types/functions: `azAuthSPN` embeds `azAuthBase` and `azOAuthBase`; `getTokenCredential` returns an `azcore.TokenCredential`. `azAuthBlobSPN.getServiceClient` and `azAuthDatalakeSPN.getServiceClient` construct storage service clients with that credential.

Control flow: credential selection is branch-based. If `OAuthTokenFilePath` is set, it creates an `azidentity.WorkloadIdentityCredential`. If `WorkloadIdentityToken` is set, it creates a `ClientAssertionCredential` whose callback returns the configured token. Otherwise it creates a `ClientSecretCredential`. Service-client methods then create SDK clients with shared options and propagate/log errors.

State and persistence behavior: client secret or assertion token remains in process memory through `azAuthConfig`; token-file mode reads through Azure Identity. No persistence is performed by this code.

Dependencies/integration: depends on Azure Identity, Azure SDK core, Blob/ADLS service packages, local logging, and client option helpers. It is selected for `SPN` auth mode by `azauth.go`.

Risks: the workload identity token branch creates `ClientAssertionCredentialOptions{}` without passing `clOpts`, unlike the other SPN branches; that may skip custom cloud, authority, resource, or SDK logging options. The callback ignores its context but returns only an in-memory token. Client secret mode needs careful secret handling in config and logs.

Test signals: this file set does not show explicit SPN tests in the visible portion of `azauth_test.go`; the config struct includes SPN fields, so SPN coverage may be elsewhere or absent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/azauthspn.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/azstorage.go -->
# sources/user-network-fs/blobfuse2/component/azstorage/azstorage.go

Purpose: implements the `azstorage` BlobFuse pipeline component. It adapts the component interface to an `AzConnection` backend, manages config validation, startup/shutdown, list blocking on mount, handle creation, stats collection, and filesystem operation forwarding.

Important APIs/types/functions: `AzStorage` embeds `internal.BaseComponent` and holds `storage AzConnection`, `stConfig AzStorageConfig`, `startTime`, and `listBlocked`. Core methods include `Configure`, `OnConfigChange`, `configureAndTest`, `Start`, `Stop`, directory methods (`CreateDir`, `DeleteDir`, `IsDirEmpty`, `ReadDir`, `StreamDir`, `RenameDir`), file methods (`CreateFile`, `OpenFile`, `ReleaseFile`, `DeleteFile`, `RenameFile`, `ReadFile`, `ReadInBuffer`, `WriteFile`, `GetFileBlockOffsets`, `TruncateFile`, `CopyToFile`, `CopyFromFile`), symlink/attribute methods, and block staging/commit methods.

Control flow: configuration unmarshals azstorage options, parses/validates them, creates an `AzConnection`, sets up and tests the pipeline in parent mode, and auto-reconfigures from flat blob to ADLS when account detection says HNS and account type was not explicit. `Start` initializes list-block timing and stats. `ReadDir` and `StreamDir` optionally return empty results until `cancelListForSeconds` has elapsed. Listing uses continuation markers; `StreamDir` recursively retries when Azure returns an empty page with a non-empty marker. File operations mostly forward to `storage`, adding handle bookkeeping and stats events.

State and persistence behavior: state is runtime-only: storage client, parsed config, list-block timer, and global `azStatsCollector`. The component does not persist data itself; persistence happens through the storage backend. Dynamic config updates mutate the existing storage config and SDK log listener.

Dependencies/integration: depends on config/log/common packages, `internal.Component`, `handlemap`, `stats_manager`, Cobra flag registration, and the `AzConnection` implementations such as `BlockBlob`. It registers itself as component `azstorage` and binds many hidden and visible CLI flags.

Risks: `Stop` assumes `azStatsCollector` is non-nil after `Start`; unusual lifecycle calls could panic. `ReadLink` appears to push stats only when `err != nil`, which likely counts failed reads instead of successful reads. `ReadInBuffer` uses handle size or provided size to clamp reads and returns `ERANGE` when offset is beyond size; stale handle size could hide valid appended data until refreshed. `Configure` uses a `goto` reconfiguration path, so config parsing must remain idempotent.

Test signals: `azauth_test.go` exercises setup/test pipeline behavior for auth configurations. Operation-level behavior is likely covered by separate azstorage tests outside this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/azstorage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/azstorage_constants.go -->
# sources/user-network-fs/blobfuse2/component/azstorage/azstorage_constants.go

Purpose: centralizes metric/event field names and safe Azure SDK logging allowlists for the azstorage component.

Important APIs/types/functions: string constants name stats counters/events such as bytes downloaded/uploaded, progress events, filesystem operation names, open handles, and event fields (`mode`, `count`, `src`, `dest`, `size`, `target`). `allowedHeaders` and `allowedQueryParams` list request/response header and query names that may be logged without redaction.

Control flow: no executable control flow beyond package initialization of slices. Other azstorage files use these constants when pushing stats events and configuring SDK log redaction.

State and persistence behavior: package-level slices are initialized in memory. They do not persist state, but they influence what request metadata can appear in logs.

Dependencies/integration: used by azstorage operations and SDK logging helpers elsewhere in the package. The allowlists are security-sensitive integration points between Azure SDK diagnostics and BlobFuse logging.

Risks: allowlists include some SAS fields such as `se`, `sp`, `spr`, `srt`, `ss`, `st`, and `sv`, but exclude high-risk signature-like fields. Any future addition must be reviewed for secret leakage. Because slices are mutable package variables, accidental runtime modification is possible.

Test signals: no direct tests in this subset. Indirect signal comes from log behavior and operation stats tests elsewhere.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/azstorage_constants.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/block_blob.go -->
# sources/user-network-fs/blobfuse2/component/azstorage/block_blob.go

Purpose: implements the Blob Storage `AzConnection` backend for flat namespace/block blob accounts, with support for service setup, listing, virtual directories, metadata-derived attributes, uploads/downloads, copy-delete renames, truncate, block staging, commits, CPK, filters, and stats progress events.

Important APIs/types/functions: `BlockBlob` embeds `AzStorageConnection` and holds auth, service/container clients, CPK info, download options, list details, and keyed block locks. Key methods include `Configure`, `UpdateConfig`, `UpdateServiceClient`, `createServiceClient`, `SetupPipeline`, `TestPipeline`, `IsAccountADLS`, `ListContainers`, `SetPrefixPath`, create/delete/rename file and directory methods, `GetAttr`, `List`, blob item/prefix processors, read/write helpers, block-list helpers, truncate helpers, `Write`, `StageAndCommit`, `StageBlock`, `CommitBlocks`, and `SetFilter`.

Control flow: setup creates an auth-specific service client and then a container client. Pipeline validation performs a small hierarchical list and maps Azure response errors into clearer mount failures. Listing builds a prefix-aware hierarchy pager, converts blob items into `ObjAttr`, adds synthetic directory attributes from blob prefixes when marker blobs are absent, and applies optional filters to non-directories. Reads use `DownloadFile`, `DownloadBuffer`, or streaming reads with optional ETag output. Uploads use buffer or file SDK methods, selecting block size based on file size and max block constraints. Rename-file starts server-side copy, polls copy status if pending, updates source attr LMT/ETag on success, then deletes source with ENOENT retries. Rename-directory lists all children and rename-files each child before marker handling. Truncate either rewrites a small buffer or converts/manipulates committed block lists and stages/commits modified blocks.

State and persistence behavior: persistent data lives in Azure Blob Storage. In-process state includes SDK clients, config, CPK options, block locks, and download/list options. `StageAndCommit` serializes commits per blob name through `common.KeyedMutex`. Block operations mutate `common.BlockOffsetList` flags/data before committing.

Dependencies/integration: heavily depends on Azure SDK packages (`azcore`, `blob`, `blockblob`, `container`, `service`, streaming helpers), repository `common`, `log`, `internal`, `stats_manager`, and `blobfilter`. It is the concrete backend used by `AzStorage` for block accounts.

Risks: `RenameDirectory` logs child rename errors but continues, which can produce partial renames before returning marker status. `Write` ignores errors from `ReadBuffer` for small no-block blobs (`oldData, _ := ...`), risking overwrite behavior after a failed read. `removeBlocksTruncate` decrements the search index and may be sensitive to new size at or before the first block start; callers avoid zero-size in the top-level truncate path. MD5 validation after range downloads computes the MD5 of the whole local file handle and compares to blob ContentMD5, which may not match partial download semantics. `stageAndCommitModifiedBlocks` advances its data offset only for dirty blocks, so data slicing depends on dirty-block ordering and buffer construction. Secret-bearing SAS endpoints are created outside this file but used by service clients; logging must remain redacted.

Test signals: auth tests validate service setup and pipeline probing. This subset does not include focused unit tests for listing conversion, block truncate edge cases, rename partial failure, CPK paths, filters, or staged commit behavior; those are high-value areas for targeted tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/block_blob.go -->
