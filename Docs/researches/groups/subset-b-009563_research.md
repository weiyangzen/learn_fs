<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/block_blob_test.go -->
# sources/user-network-fs/blobfuse2/component/azstorage/block_blob_test.go

## Purpose
Live integration and behavior coverage for the Blobfuse2 block-blob storage backend. The file is a `testify/suite` suite behind the `!authtest` build tag and validates block-blob configuration, container connectivity, directory emulation, file CRUD, symlink metadata, read/write/truncate behavior, block-list based flush paths, MD5 handling, customer-provided keys, filtering, and paged listing against real Azure Blob Storage.

## Important APIs, Types, and Functions
The top-level helpers are `uuid`, `newUUID()`, and `uploadReaderAtToBlockBlob()`, which create deterministic Azure block-blob test fixtures by choosing single-upload or staged-block upload and committing a generated block ID list. `blockBlobTestSuite` carries the active `AzStorage`, Azure SDK `service.Client` and `container.Client`, generated container name, raw YAML config, and assertions. `newTestAzStorage()` loads YAML through `config.ReadConfigFromReader()`, constructs `NewazstorageComponent()`, and calls `Configure(true)`. `SetupTest()`, `setupTestHelper()`, `tearDownTestHelper()`, and `cleanupTest()` manage logging, `~/azuretest.json` credentials, component startup, container creation, and deletion.

The tests exercise public component methods such as `CreateDir`, `DeleteDir`, `IsDirEmpty`, `ReadDir`, `StreamDir`, `RenameDir`, `CreateFile`, `OpenFile`, `ReleaseFile`, `DeleteFile`, `RenameFile`, `ReadFile`, `ReadInBuffer`, `WriteFile`, `TruncateFile`, `CopyToFile`, `CopyFromFile`, `CreateLink`, `ReadLink`, `GetAttr`, `Chmod`, `Chown`, `GetFileBlockOffsets`, and `FlushFile`. They also directly inspect lower-level `AzConnection` and `BlockBlob` behavior through `storage.TestPipeline()`, `storage.List()`, `storage.UpdateConfig()`, `storage.ReadToFile()`, `storage.WriteFromFile()`, `storage.WriteFromBuffer()`, `storage.ReadBuffer()`, `storage.SetPrefixPath()`, and `BlockBlob.SetFilter()`.

## Control Flow, State, and Persistence
Each test creates or reuses a generated Azure container, starts the Blobfuse component, mutates remote blobs with either Blobfuse APIs or Azure SDK clients, then asserts remote state using `GetProperties`, `DownloadStream`, block-list inspection, or component reads. Directory tests validate marker blobs, virtual directories, prefix-path behavior, list blocking after mount, pagination tokens, and rename-by-copy/delete semantics. File tests cover zero-length creation, handle size refresh, read ranges, missing-handle reads, ETag propagation, parallel write visibility, metadata conservation, unsupported chmod/chown modes, and ENOENT/ERANGE error mapping.

Large write and flush tests build `handlemap` cache objects and `common.BlockOffsetList` values to simulate dirty, truncated, appended, and existing blocks before calling `FlushFile`. MD5 tests create local files, upload small and large payloads, compare `common.GetMD5()` with blob attributes, deliberately corrupt service MD5 headers, and verify `validate-md5` success or failure. CPK tests generate a base64 AES key and SHA256, then ensure encrypted blobs cannot be read without CPK options but can be read through the configured storage path. Persistent state is primarily remote Azure container contents, temporary local files, suite fields, and global config/log state reset during teardown.

## Dependencies and Integration Points
Depends on Azure SDK clients for blob, blockblob, container, service, streaming, and pointer helpers; Blobfuse internal packages `common`, `config`, `log`, `internal`, and `handlemap`; `testify/assert` and `testify/suite`; and a host-specific `~/azuretest.json` populated with block account credentials. It integrates with the `AzStorage` component lifecycle (`Configure`, `Start`, `Stop`), the `AzConnection` abstraction, Blobfuse handle/cache structures, Azure block-list limits, and storage metadata conventions such as `folderKey` and `symlinkKey`.

## Risks and Test Signals
The suite has strong end-to-end signal because it verifies actual service state, error codes, block-list transitions, content bytes, metadata, pagination, prefix handling, MD5 validation, and CPK reads/writes. The main risks are cost/flakiness from real Azure dependencies, generated container cleanup failures, reliance on `~/azuretest.json`, long runtime and memory use from 100 MB to 300 MB truncation cases, sleeps for timestamp checks, and hidden order sensitivity when subtests manually tear down and recreate suite state. Some paths, such as RA-GRS, are commented out, and auth modes beyond account key are mostly covered elsewhere.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/block_blob_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/config.go -->
# sources/user-network-fs/blobfuse2/component/azstorage/config.go

## Purpose
Configuration schema, environment binding, parsing, validation, and dynamic reconfiguration for the Blobfuse2 Azure storage component. It converts YAML/env options into `AzStorageConfig`, normalizes endpoints and proxy settings, selects account/auth modes, validates required credentials, sets retry and feature defaults, and supports runtime SAS/rate-limit updates.

## Important APIs, Types, and Functions
`AuthType` and `AccountType` are enum-backed integer types with parser/string support for `key`, `sas`, `spn`, `msi`, `azcli`, `workloadidentity`, `block`, and `adls`. `AzStorageOptions` is the user-facing config struct with `config` and `yaml` tags for account identity, auth credentials, endpoints, container/subdirectory, transfer sizing, retries, proxies, unsupported operation behavior, MD5 flags, virtual directories, compression, telemetry, ACL/CPK controls, blob filters, and read/IOPS caps.

`RegisterEnvVariables()` binds Azure environment variables to `azstorage.*` config keys. `formatEndpointProtocol()` adds `http://` or `https://` and a trailing slash. `formatEndpointAccountType()` rewrites `.blob.` and `.dfs.` hostnames to match block or ADLS account type. `validateMsiConfig()` enforces mutual exclusion between MSI application, object, and resource IDs. `ParseAndValidateConfig()` performs full startup validation and fills `az.stConfig`. `configureBlobFilter()` enables `blobfilter.BlobFilter` only when the global `read-only` flag is set. `ParseAndReadDynamicConfig()` updates reloadable fields and can refresh a live SAS-backed service client.

## Control Flow, State, and Persistence
Startup parsing first requires `AccountName`, defaults missing account type to block, honors the legacy `use-adls` override, validates block size against Azure's maximum staged block size, and requires a container unless `mount-all-containers` is set. It maps legacy `use-https` to `UseHTTP`, validates CPK key material, defaults the endpoint to `<account>.blob.core.windows.net` or `<account>.dfs.core.windows.net`, normalizes protocol/account type, stores the Active Directory endpoint, strips leading slashes from `subdirectory`, and chooses proxy behavior based on HTTP mode.

Dynamic fields are applied before auth selection: block size, max concurrency, tier, unsupported access modifier behavior, MD5 flags, virtual directory defaulting, list-page size, compression, ACL honoring, and rate caps. If no auth mode is explicit, `autoDetectAuthMode()` chooses MSI, key, SAS, or SPN from populated credentials. Auth validation stores key/SAS/MSI/SPN/AZCLI/workload identity fields and rejects missing required secrets or invalid modes. Retry defaults are set to 5 retries, 900 second max timeout, 4 second backoff, and 60 second max retry delay unless overridden. On SAS reload, the old SAS is restored if `az.storage.UpdateServiceClient("saskey", ...)` fails.

## Dependencies and Integration Points
Depends on Azure SDK block-blob limits and access-tier types, Blobfuse config/log packages, shared helpers from `utils.go` such as `sanitizeSASKey()`, `autoDetectAuthMode()`, `getAccessTierType()`, and `removeLeadingSlashes()`, and `github.com/vibhansa-msft/blobfilter`. It writes into `AzStorage.stConfig`, which is consumed by `NewAzStorageConnection()`, `BlockBlob`, `Datalake`, auth providers in `azauth.go`, and runtime component reload paths.

## Risks and Test Signals
Important risks include broad mutable global config state, legacy option interactions (`use-adls`, `use-https`, unsupported v1 flags), endpoint rewriting that assumes `.blob.`/`.dfs.` hostnames, possible secret exposure through logs if callers extend logging carelessly, CPK validation limited to presence rather than base64/length, and runtime SAS refresh dependency on a non-nil live storage client. Unit coverage in `config_test.go` validates missing/invalid account types, protocol/proxy behavior, auth modes, MSI mutual exclusion, compression, SAS refresh, max list results, and rate limits, while live block-blob tests validate defaults and endpoint behavior against Azure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/config_test.go -->
# sources/user-network-fs/blobfuse2/component/azstorage/config_test.go

## Purpose
Unit-style `testify/suite` coverage for `config.go` parsing and dynamic reconfiguration. The tests focus on validation failures, default values, legacy flags, auth selection, proxy normalization, reloadable SAS configuration, compression toggles, max list result sizing, and rate-limit defaults without requiring Azure service access.

## Important APIs, Types, and Functions
`configTestSuite` provides `SetupTest()` that installs a silent debug logger. Each test constructs an `AzStorage` and `AzStorageOptions`, optionally mutates the global config package with `config.Set*`, calls `ParseAndValidateConfig()` or `ParseAndReadDynamicConfig()`, and asserts fields on `az.stConfig`. `TestConfigTestSuite()` registers the suite.

The covered test methods are `TestEmptyAccountName`, `TestEmptyAccountType`, `TestInvalidAccountType`, `TestUseADLSFlag`, `TestBlockSize`, `TestProtoType`, `TestProxyConfig`, `TestMaxResultsForList`, `TestAuthModeNotSet`, `TestAuthModeKey`, `TestAuthModeSAS`, `TestAuthModeMSI`, `TestAuthModeSPN`, `TestOtherFlags`, `TestCompressionType`, `TestSASRefresh`, and `TestRateLimitConfig`.

## Control Flow, State, and Persistence
Most tests defer `config.ResetConfig()` to isolate global config keys. Account-type tests verify empty account names fail, invalid type strings fail, and the legacy `azstorage.use-adls` setting overrides an otherwise invalid type string into ADLS or block. Block-size coverage verifies MB-to-byte conversion and rejection over `blockblob.MaxStageBlockBytes`, though the oversized case passes a byte-valued SDK constant into an MB-valued option. Protocol and proxy tests exercise `use-https`, `UseHTTPS`, `UseHTTP`, HTTP proxy rejection under HTTPS, HTTPS proxy acceptance, and protocol/trailing slash formatting.

Auth tests verify default MSI selection, key mode requiring `AccountKey`, SAS mode requiring `SaSKey`, MSI optional identity fields and mutual exclusion, and SPN requiring client ID, tenant ID, and one credential source. Dynamic config tests confirm `disable-compression` only takes effect when explicitly set, SAS reload calls through a synthetic `BlockBlob` auth object, and read/IOPS caps default to `-1` then accept positive values. State is limited to the in-memory `AzStorage` struct and the shared config registry.

## Dependencies and Integration Points
Depends on `testing`, Azure SDK block-blob constants, Blobfuse `common`, `config`, and `log` packages, and `testify/assert`/`suite`. It reaches into package-private `AzStorage` and `AzStorageConfig` fields because it is in package `azstorage`, making it a close regression suite for the config parser rather than a public API test.

## Risks and Test Signals
The suite gives fast signal for parser invariants and default propagation, but it does not start real pipelines or validate actual credentials. Risks include reliance on global config cleanup, missing coverage for AZCLI, workload identity, CPK failure paths, blob filter read-only enforcement, Active Directory endpoint formatting, auth resource, telemetry, ACL preservation, and mount-all-containers behavior. Several tests intentionally expect later validation errors while still checking partial state, which is useful for parser ordering but could mask changes where earlier failures prevent state population.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/connection.go -->
# sources/user-network-fs/blobfuse2/component/azstorage/connection.go

## Purpose
Defines the storage backend configuration object, the common `AzConnection` interface implemented by block-blob and ADLS backends, and the factory that selects the correct concrete connection for an account type.

## Important APIs, Types, and Functions
`AzStorageConfig` is the internal parsed configuration shared by storage implementations. It embeds `azAuthConfig` and stores container, prefix path, transfer sizing, default access tier, mount-time list blocking, retry policy, proxy address, unsupported-operation behavior, mount-all-containers, MD5 flags, virtual-directory settings, list page size, compression, telemetry, ACL behavior, CPK key material, optional `blobfilter.BlobFilter`, and read/IOPS caps.

`AzStorageConnection` is a small base struct containing `Config AzStorageConfig`. `AzConnection` is the backend contract: lifecycle/config methods (`Configure`, `UpdateConfig`, `SetupPipeline`, `TestPipeline`, `UpdateServiceClient`, `SetPrefixPath`, `SetFilter`), account/container methods, namespace methods, file IO methods, write/block-list methods, POSIX modifier methods, and block-list staging/commit methods. `NewAzStorageConnection()` returns a configured `*BlockBlob` for block accounts, a configured `*Datalake` for ADLS accounts, logs invalid account types, and returns nil when no valid implementation matches.

## Control Flow, State, and Persistence
The factory is intentionally simple: inspect `cfg.authConfig.AccountType`, allocate the selected backend, call its `Configure(cfg)` method, ignore the returned error, and return the backend pointer. The connection state is persisted in the concrete backend's embedded config and clients after later `SetupPipeline()` calls. The interface makes no distinction between operations natively implemented by the backend and operations delegated to another backend, which is important because `Datalake` implements many file/block operations by forwarding to an embedded `BlockBlob`.

## Dependencies and Integration Points
Depends on Azure SDK blob access-tier types, Blobfuse `common.BlockOffsetList`, `internal.ObjAttr`, `internal.WriteFileOptions`, `internal.TruncateFileOptions`, logging, and `blobfilter`. This file is the contract boundary between `AzStorage` component methods in `azstorage.go` and concrete storage implementations in `block_blob.go` and `datalake.go`. Any new backend must satisfy every method in `AzConnection`, including test-only `SetPrefixPath`.

## Risks and Test Signals
The main risks are interface breadth, ignored `Configure()` errors in the factory, nil returns for invalid account types, and tight coupling of high-level component behavior to backend-specific block-list semantics. Because `AzConnection` includes both blob-native and POSIX-like operations, additions require changes across all implementations. Test signals come indirectly from `block_blob_test.go`, `config_test.go`, and ADLS-specific tests elsewhere: they verify factory selection through account type config, block/ADLS behavior, and dynamic config updates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/connection.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/datalake.go -->
# sources/user-network-fs/blobfuse2/component/azstorage/datalake.go

## Purpose
ADLS Gen2/HNS implementation of `AzConnection`. It wraps Azure Data Lake service/filesystem clients for namespace, permission, ACL, and directory operations while delegating many blob-compatible data-plane operations to an embedded `BlockBlob` configured against the corresponding blob endpoint.

## Important APIs, Types, and Functions
`Datalake` embeds `AzStorageConnection` and holds an `azAuth`, `*service.Client`, `*filesystem.Client`, embedded `BlockBlob`, and optional Data Lake `*file.CPKInfo`. `transformAccountEndpoint()` rewrites `.dfs.` endpoints to `.blob.` for delegated blob APIs and warns on custom endpoints. `transformConfig()` changes the account type to block and applies the transformed endpoint for the embedded block backend. `Configure()` stores config, builds Data Lake CPK options, configures `BlockBlob`, and forces list details to include permissions. `UpdateConfig()` and `UpdateServiceClient()` update local fields, Data Lake clients, and the embedded block client.

Native ADLS methods include `createServiceClient()`, `SetupPipeline()`, `TestPipeline()`, `CreateFile()`, `CreateDirectory()`, `DeleteFile()`, `DeleteDirectory()`, `RenameFile()`, `RenameDirectory()`, `GetAttr()`, `WriteFromFile()` ACL preservation, `ChangeMod()`, `ChangeOwner()`, and `SetFilter()`. Delegated methods include container listing, prefix setting, symlinks, list, reads, buffer writes, offset writes, block offset retrieval, truncate, stage/commit, committed block lists, stage block, and commit blocks.

## Control Flow, State, and Persistence
Configuration creates both ADLS and block-blob views of the same account. `SetupPipeline()` creates the ADLS service client and filesystem client, then sets up the block pipeline. `TestPipeline()` skips validation for mount-all-containers, validates the filesystem client, lists up to two paths with the configured prefix, rejects non-HNS accounts when returned paths lack permissions, then delegates to block-blob validation for remaining checks.

ADLS namespace methods use filesystem file/directory clients rooted at `filepath.Join(prefixPath, name)`. Create/delete/rename methods translate service errors to POSIX-style `syscall` values for not found, exists, permission denied, lease conflicts, and path-too-deep cases where handled. `GetAttr()` reads file properties, converts ADLS permission strings to `os.FileMode`, fills `internal.ObjAttr`, marks directories by resource type, optionally recomputes mode from ACLs for the configured object ID, and applies blob filters. `WriteFromFile()` optionally reads the existing ACL when `preserveACL` is enabled, delegates upload to `BlockBlob`, then restores ACL with `SetAccessControl()`. `ChangeMod()` writes POSIX permissions through ADLS ACL permissions. `ChangeOwner()` returns success only when unsupported access modifiers are ignored; otherwise it returns `ENOTSUP`.

## Dependencies and Integration Points
Depends on Azure SDK packages `azcore`, `azcore/to`, and ADLS `service`, `filesystem`, `directory`, and `file`; Blobfuse `common`, `internal`, `log`, shared utility/error helpers such as `storeDatalakeErrToErr()`, `getFileMode()`, `getFileModeFromACL()`, `getACLPermissions()`, `parseMetadata()`, and `modifyLMTandEtag()`; and `blobfilter`. Integration is deliberately hybrid: ADLS operations preserve namespace semantics and ACLs, while data transfer, listing shape, symlink emulation, block staging, truncation, and filters stay aligned with `BlockBlob`.

## Risks and Test Signals
Key risks are dual-client consistency, custom endpoint uncertainty when a DFS endpoint cannot reliably map to blob APIs, URL escaping/path joining differences across rename and normal operations, ACL restoration failures being logged but not returned, possible nil dereferences if service properties omit permissions/resource type, and delegated block operations that may not fully preserve ADLS ACL semantics unless `preserveACL` paths are used. Test signals in this file are indirect; interface conformance is compile-time checked with `var _ AzConnection = &Datalake{}`. Behavior is primarily validated by ADLS integration tests elsewhere and by shared block-blob tests for delegated data-plane operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/datalake.go -->
