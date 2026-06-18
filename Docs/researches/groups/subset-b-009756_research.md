# subset-b-009756 grouped research

This grouped report covers the exact source manifest assigned to `subset-b-009756`. Each file section is delimited with the required `BEGIN_FILE_RESEARCH` and `END_FILE_RESEARCH` markers so reconciliation can split one source-tree-aligned research document per source file.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/swift/swift_test.go -->
# sources/user-network-fs/rclone/backend/swift/swift_test.go

## Purpose
This file is Swift backend integration and internal behavioral coverage. It runs the generic `fstests` suite against `TestSwiftAIO:` and adds focused tests for the Swift backend's major non-standard paths: unchunked streaming, segmented uploads, segmented upload cleanup on reader failure, large-object server-side copy, and storage policy discovery.

## Important APIs, types, and functions
`TestIntegration` delegates broad filesystem contract coverage to `fstests.Run`. `SetUploadChunkSize` exposes the backend's private chunk-size setter through `fstests.SetUploadChunkSizer`. `InternalTest` registers `PolicyDiscovery`, `NoChunk`, `WithChunk`, `WithChunkFail`, and `CopyLargeObject`. The helper tests mutate `f.opt.NoChunk`, `f.opt.ChunkSize`, `f.opt.StoragePolicy`, and `f.opt.UseSegmentsContainer`, then restore them with deferred cleanup.

## Control flow and state
The streaming tests build `fstest.Item` and `object.NewStaticObjectInfo` with unknown size (`-1`) to drive `PutStream`. `testNoChunk` verifies the direct upload path, hash consistency, object reread, usage accounting, and removal. `testWithChunk` forces a tiny chunk size to exercise segmented upload. `testWithChunkFail` injects a reader error after partial content and verifies neither the final object nor leftover segments remain. `testCopyLargeObject` copies a segmented object and checks usage includes both objects. `testPolicyDiscovery` creates containers, fetches storage policy, and checks segment-container policy inheritance.

## Dependencies and integration points
The tests depend on `github.com/ncw/swift/v2`, rclone `fs`, `hash`, `object`, `fstest`, `fstests`, `random`, `readers`, and testify. They require a configured Swift all-in-one test remote and exercise backend internals (`f.c`, container names, segment naming conventions) beyond the public `fs.Fs` surface.

## Risks and test signals
The main regression signals are cleanup after failed chunked streaming, accurate usage deltas, correct segmented copy size, and storage policy propagation. The suite is integration-heavy and environment-dependent; absent `TestSwiftAIO:` means these signals may not run in normal unit jobs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/swift/swift_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/ulozto/api/types.go -->
# sources/user-network-fs/rclone/backend/ulozto/api/types.go

## Purpose
This file defines JSON request and response contracts for the Uloz.to backend. It is intentionally data-oriented: the backend in `ulozto.go` imports these types to authenticate, list folders/files, create folders, upload payloads, commit upload sessions, move/rename resources, fetch download links, and interpret API errors.

## Important APIs, types, and functions
`Error` implements `error` with an `Is` method so callers can use `errors.As` and causal matching. Listing types include `ListResponseMetadata`, `Folder`, `File`, `ListFoldersResponse`, and `ListFilesResponse`. Storage accounting is represented by `FolderSize`, `FolderSizes`, and `FolderSizesResponse`. Mutating request types include `CreateFolderRequest`, `DeleteFoldersRequest`, `BatchUpdateFilePropertiesRequest`, `CommitUploadBatchRequest`, `UpdateDescriptionRequest`, `MoveFolderRequest`, `RenameFolderRequest`, and `MoveFileRequest`. Upload/download/session types include `CreateUploadURLRequest`, `CreateUploadURLResponse`, `SendFilePayloadResponse`, `GetDownloadLinkRequest`, `GetDownloadLinkResponse`, `AuthenticateRequest`, and `AuthenticateResponse`.

## Control flow and state
There is no active control flow besides `Error.Error` and `Error.Is`. State is transient JSON state mapped with field tags. Nested structs preserve Uloz.to's API shape for authentication session user details, file processing data, and upload batch results.

## Dependencies and integration points
Only standard `errors`, `fmt`, and `time` are imported. The backend relies on exact JSON tag spelling when calling `/v5`, `/v6`, `/v7`, `/v8`, and `/v9` endpoints through `rest.CallJSON`.

## Risks and test signals
This file has no direct unit tests. Risks are schema drift, weakly typed `[]any` preview/download fields, and broad `Error.Is` behavior that treats any `*Error` target as matching. Compile-time usage in `ulozto.go` is the main signal; live integration tests cover whether tags still match the service.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/ulozto/api/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/ulozto/ulozto.go -->
# sources/user-network-fs/rclone/backend/ulozto/ulozto.go

## Purpose
This file implements the rclone `ulozto` backend. It registers configuration, authenticates with Uloz.to, maps rclone directory and object operations onto Uloz.to folder/file APIs, performs resumable-style upload sessions, and stores rclone-only metadata such as hashes and mtime inside the Uloz.to file description.

## Important APIs, types, and functions
`Options` holds app token, credentials, optional root folder slug, encoding, and list page size. `Fs` owns name/root/options, authenticated REST client, unauthenticated CDN client, `dircache`, and pacer. `NewFs` configures clients, authenticates, resolves the root folder, and handles root-as-file. Core `Fs` methods include `About`, `Put`, `PutUnchecked`, `Mkdir`, `Rmdir`, `Move`, `DirMove`, `NewObject`, `List`, `FindLeaf`, `CreateDir`, and `DirCacheFlush`. `UploadSession` and `uploadUnchecked` create upload URLs, stream payloads to CDN, verify MD5, patch destination metadata, and commit batches. `Object` implements `Open`, `Update`, `Remove`, `SetModTime`, `Hash`, and standard object metadata methods. `DescriptionEncodedMetadata` encodes MD5, SHA256, and modtime with gob/base64 prefixed by version `1;`.

## Control flow and state
Initialization strips slashes, sets `X-Auth-Token`, calls `/v6/session`, then chooses either the authenticated user's root slug or configured `root_folder_slug`. Directory state is cached in `dircache`. Listing pages loop until a returned page is shorter than `ListPageSize`, decoding names through the configured encoder. Upload flow is multi-step: create or renew upload session, tee payload into a multi-hasher, upload multipart payload to CDN URL, compare returned MD5, encode metadata in description, patch file properties to final name/folder, and confirm the private upload batch. Updates upload a replacement first, delete the old file twice, then copy new object fields.

## Dependencies and integration points
The backend depends on rclone `fs`, `config`, `dircache`, `encoder`, `pacer`, `rest`, `hash`, `fshttp`, `obscure`, and Uloz.to API structs. It integrates with rclone optional interfaces for duplicate files, empty directories, put-unchecked, move, dir move, and dir cache flush.

## Risks and test signals
Key risks are session/token expiry during multi-step uploads, service schema drift, duplicate names because Uloz.to permits them, metadata loss when descriptions are missing or user-edited, and partial replacement semantics where a new upload may succeed before old deletion fails. Retry handling reauthenticates only selected 401 error code `70001`. Tests include generic integration and `TestListWithoutMetadata`, which verifies listing and mtime changes continue when description metadata is absent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/ulozto/ulozto.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/ulozto/ulozto_test.go -->
# sources/user-network-fs/rclone/backend/ulozto/ulozto_test.go

## Purpose
This file provides Uloz.to backend tests. It runs the standard rclone filesystem integration suite and adds a regression test for files whose description metadata is missing or unreadable.

## Important APIs, types, and functions
`TestIntegration` invokes `fstests.Run` with `RemoteName: "TestUlozto:"` and `NilObject: (*Object)(nil)`. `TestListWithoutMetadata` uses `fstest.RandomRemoteName`, `fs.NewFs`, `fstests.PutTestContents`, `fstest.CheckListing`, `Object.updateFileProperties`, and `operations.Purge`.

## Control flow and state
The metadata test creates a unique subremote, uploads a known payload with expected SHA256 and MD5, checks listing, then patches the Uloz.to description to an empty string. It expects subsequent listing to still show the file with server-side mtime fallback and empty hashes. It then calls `SetModTime` and checks that mtime is encoded again while hashes remain empty because the original hash metadata was not available.

## Dependencies and integration points
The test depends on configured remote `TestUlozto:`, rclone test helpers, and the backend's private `updateFileProperties` method with `api.UpdateDescriptionRequest`.

## Risks and test signals
The main signal is graceful degradation when files were not uploaded by rclone or metadata was modified externally. The test is live-service dependent and skips only when the remote is absent from config. It also validates cleanup via `operations.Purge`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/ulozto/ulozto_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/common/options.go -->
# sources/user-network-fs/rclone/backend/union/common/options.go

## Purpose
This small package holds configuration shared by `backend/union` and `backend/union/policy` without creating import cycles. It centralizes the option schema consumed by the union backend and upstream wrappers.

## Important APIs, types, and functions
`Options` contains `Upstreams`, deprecated `Remotes`, action/create/search policy names, usage `CacheTime`, and `MinFreeSpace`. `Upstreams` and `Remotes` are `fs.SpaceSepList` values so config parsing preserves quoted remotes and space-separated backend specs.

## Control flow and state
There is no runtime control flow. The struct is populated by `configstruct.Set` in `union.NewFs` and then passed by pointer into each `upstream.Fs`.

## Dependencies and integration points
The only dependency is `github.com/rclone/rclone/fs`. `union.NewFs` handles backward compatibility from `Remotes` to `Upstreams`; policy files read `MinFreeSpace` through upstream options during least-free-space selection.

## Risks and test signals
The file's risks are config compatibility and tag drift. Since it is schema-only, tests exercise it indirectly through union integration tests that build remotes with upstream, policy, cache, and read-only/no-create suffixes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/common/options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/entry.go -->
# sources/user-network-fs/rclone/backend/union/entry.go

## Purpose
This file defines the union-level object and directory wrappers returned to rclone callers. The wrappers present the union `Fs` as the parent while retaining candidate upstream entries for action, search, metadata, and writeback behavior.

## Important APIs, types, and functions
`Object` embeds `*upstream.Object` and tracks its union `Fs`, candidate entries `co`, and a `writebackMu`. `Directory` embeds `*upstream.Directory` with candidate directories `cd`. Methods include `Object.Update`, `Remove`, `SetModTime`, `Open`, `GetTier`, `ID`, `MimeType`, `SetTier`, and directory `ModTime`, `Size`, `SetMetadata`, and `SetModTime`. `update`, `UnWrapUpstream`, `Fs`, and `candidates` support internal wrapping.

## Control flow and state
Object mutations select candidate entries through the union action policy. If update candidates are all unwritable (`fs.ErrorPermissionDenied`), `Update` falls back to creating a new object through `f.put` and updates the wrapper in place. Multi-target updates use `multiReader` to tee the input and run writes concurrently, aggregating errors. `Open` serializes writeback with `writebackMu`, asks the upstream object to copy into a configured writeback layer if needed, appends any new object candidate, and opens the selected object.

## Dependencies and integration points
The file depends on `upstream`, rclone `fs`, standard `io`, `sync`, `time`, and `errors`. It is tightly coupled to `union.go` policy dispatch, `Errors`, `multiReader`, and `multithread`.

## Risks and test signals
Important risks are partial multi-upstream writes, input drain requirements after one branch fails, and writeback candidate duplication. Directory modtime/size are aggregate views, not native union state. Internal tests exercise read-only fallback write behavior; generic union tests exercise object update/remove/listing contracts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/entry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/errors.go -->
# sources/user-network-fs/rclone/backend/union/errors.go

## Purpose
This file defines `Errors`, a small multi-error type used throughout the union backend to aggregate per-upstream errors from concurrent operations.

## Important APIs, types, and functions
`Errors` is `[]error` with `Map`, `FilterNil`, `Err`, `Error`, and `Unwrap`. `Map` transforms and optionally drops errors. `FilterNil` removes nil entries. `Err` returns nil when there are no non-nil errors, otherwise returns the filtered `Errors` value. `Error` formats empty, single, and multiple errors. `Unwrap` returns the underlying slice for Go multi-error matching.

## Control flow and state
The type is stateless besides its slice contents. Union operations allocate an `Errors` sized to upstream count, fill indexes from goroutines, then call `Err` or `FilterNil` to decide final behavior.

## Dependencies and integration points
It imports `bytes` and `fmt`. `errors.Is` can inspect contained errors because `Unwrap() []error` follows Go's multi-error convention. The type is used by object updates/removes, directory operations, list error reconciliation, shutdown, cleanup, and upload tee errors.

## Risks and test signals
Risks include losing positional context after `FilterNil` and callers needing to wrap errors with upstream names before aggregation. Unit tests in `errors_test.go` verify mapping, nil filtering, returned error semantics, formatting, and `errors.Is` behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/errors_test.go -->
# sources/user-network-fs/rclone/backend/union/errors_test.go

## Purpose
This file unit-tests the union backend's `Errors` multi-error helper.

## Important APIs, types, and functions
The tests define sentinel `err1`, `err2`, and `err3`. `TestErrorsMap` verifies transformations and dropping nil results. `TestErrorsFilterNil` checks nil removal. `TestErrorsErr` checks that mixed slices return filtered `Errors` and all-nil slices return nil. `TestErrorsError` asserts exact formatted strings. `TestErrorsUnwrap` checks slice unwrapping and `errors.Is` matching.

## Control flow and state
Each test constructs small literal `Errors` values and compares with testify assertions. There is no persistence or external state.

## Dependencies and integration points
Imports are standard `errors`, `testing`, and testify `assert`. The tests are direct coverage for the aggregation type used by concurrent union operations.

## Risks and test signals
The exact string assertions are useful regression signals for user-visible aggregate errors. `errors.Is` coverage confirms the type remains compatible with Go multi-error unwrapping if implementation changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/errors_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/all.go -->
# sources/user-network-fs/rclone/backend/union/policy/all.go

## Purpose
This file registers and implements the `all` union policy. It behaves like `epall` for action and search but differs for create: it applies creation to all creatable branches without requiring the target path or parent to already exist.

## Important APIs, types, and functions
`All` embeds `EpAll`. `init` registers `"all"`. `Create` filters candidate upstream filesystems with `filterNC`; `CreateEntries` filters candidate entries with `filterNCEntries`.

## Control flow and state
Both create methods return `fs.ErrorObjectNotFound` for no candidates and `fs.ErrorPermissionDenied` when all candidates are marked no-create. Otherwise they return every creatable upstream or entry unchanged.

## Dependencies and integration points
The file imports `context`, union `upstream`, and rclone `fs`. It participates in `policy.Get` registry lookup and is used by `Rand` as a base policy.

## Risks and test signals
The policy can intentionally duplicate new files across all writable branches. Misconfigurations may create broader fan-out than users expect. Union policy tests exercise `all` as action/create/search in `TestPolicy3` and as an action/search component in other configurations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/all.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/epall.go -->
# sources/user-network-fs/rclone/backend/union/policy/epall.go

## Purpose
`EpAll` implements the existing-path-all policy: select every branch on which the target path, or creation parent path, exists.

## Important APIs, types, and functions
`EpAll` embeds `EpFF` for search behavior and registers as `"epall"`. `epall` concurrently probes all upstream roots with `findEntry`. `Action`, `ActionEntries`, `Create`, and `CreateEntries` apply read-only/no-create filtering and return the matching set.

## Control flow and state
`epall` builds a result slice in upstream order after goroutine probes finish. `Action` filters non-writable upstreams, then requires the exact path to exist. `Create` filters non-creatable upstreams, then checks `path+"/.."` to select branches where the parent exists. Entry-based methods assume their candidates already represent existing paths, so they only filter permissions.

## Dependencies and integration points
It depends on `context`, `path`, `sync`, union `upstream`, and rclone `fs`. `All`, space-selection policies, and random existing-path policies build on this behavior.

## Risks and test signals
The policy performs remote listings on every candidate and can be latency-sensitive. It depends on `findEntry` semantics and case sensitivity. Union tests with `epall` action and `epmfs` create cover common behavior, while policy-specific edge cases are mostly exercised indirectly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/epall.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/epff.go -->
# sources/user-network-fs/rclone/backend/union/policy/epff.go

## Purpose
`EpFF` implements existing-path-first-found. It selects one upstream where a path exists, using the first positive result delivered by concurrent probes rather than a strict sequential walk.

## Important APIs, types, and functions
`EpFF` registers as `"epff"`. `epff` launches a goroutine per upstream, runs `findEntry`, and returns the first non-nil upstream received on a channel. `Action`, `Create`, and `Search` provide rclone policy category methods; entry methods return the first entry after permission filtering.

## Control flow and state
For action, non-writable upstreams are removed before probing. For create, non-creatable upstreams are removed and the parent path (`path+"/.."`) is probed. Search probes the target path. A cancellable child context is created but only canceled on return.

## Dependencies and integration points
It depends on `context`, `path`, union `upstream`, and `fs`. Other policies embed `EpFF` directly or indirectly for search behavior.

## Risks and test signals
Despite the name, concurrent channel return means the first responding upstream wins, not necessarily the earliest configured upstream. This is a behavioral risk when latency differs across remotes. Generic union tests configure `search_policy=ff` and `action_policy=epall`; direct `epff` behavior is not heavily isolated.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/epff.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/eplfs.go -->
# sources/user-network-fs/rclone/backend/union/policy/eplfs.go

## Purpose
`EpLfs` implements existing-path least-free-space selection. It first narrows to upstreams where the path exists, then chooses the candidate with the least free space above configured `min_free_space`.

## Important APIs, types, and functions
`EpLfs` embeds `EpAll` and registers as `"eplfs"`. Helper methods `lfs` and `lfsEntries` query `GetFreeSpace`, compare against `u.Opt.MinFreeSpace`, and return `errNoUpstreamsFound` if none qualify.

## Control flow and state
Action and create delegate to `EpAll` for existence and permission filtering, then select one upstream by `lfs`. Search calls `epall` directly and selects one candidate. Entry variants apply the same free-space decision to candidate entries.

## Dependencies and integration points
It imports `context`, `errors`, `math`, union `upstream`, and `fs`. It relies on upstream usage caching and sentinel values from `upstream.GetFreeSpace`.

## Risks and test signals
If a backend does not support free space, upstream wraps that as a very large value and this policy treats it as effectively infinite after logging. The `min_free_space` threshold can cause no candidate to be selected. Tests only exercise this policy indirectly through generic policy configurations when used.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/eplfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/eplno.go -->
# sources/user-network-fs/rclone/backend/union/policy/eplno.go

## Purpose
`EpLno` implements existing-path least-number-of-objects selection. It chooses the existing candidate whose upstream reports the smallest object count.

## Important APIs, types, and functions
`EpLno` embeds `EpAll` and registers as `"eplno"`. `lno` and `lnoEntries` call `GetNumObjects` and choose the minimum. Category methods delegate to `EpAll` for permission/existence filtering, then select one entry/upstream.

## Control flow and state
Action/create methods operate on the filtered existing-path set. Search checks object existence with `epall` and then chooses by object count. Unsupported object counts are logged and treated as zero by upstream wrappers, which can bias selection toward unsupported backends.

## Dependencies and integration points
Dependencies are `context`, `math`, union `upstream`, and rclone `fs`. It relies on upstream cached usage and optional `About` support.

## Risks and test signals
Unsupported usage data can dominate selection because zero is considered least. `lnoEntries` can return nil without an explicit error if invoked with an empty slice after caller mistakes, though public methods guard len zero. Coverage is indirect through union tests and compile-time registry use.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/eplno.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/eplus.go -->
# sources/user-network-fs/rclone/backend/union/policy/eplus.go

## Purpose
`EpLus` implements existing-path least-used-space selection. It chooses an upstream among existing candidates based on the smallest reported used bytes.

## Important APIs, types, and functions
`EpLus` embeds `EpAll` and registers as `"eplus"`. `lus` and `lusEntries` call `GetUsedSpace`; category methods reuse `EpAll` then reduce to a single upstream or entry.

## Control flow and state
Action and create first require writable/creatable existing candidates. Search calls `epall` and then `lus`. Unsupported used-space values are logged and treated as zero by upstream wrappers, making unsupported backends attractive for this policy.

## Dependencies and integration points
Dependencies are `context`, `math`, union `upstream`, and `fs`. Concrete create policy `Lus` embeds this file's policy and overrides create behavior to avoid requiring existing parent candidates through `EpAll.Create`.

## Risks and test signals
The main risk is usage metric availability and cache staleness. Union tests include `create_policy=lus` in `TestPolicy1`, giving broad behavior coverage but not exhaustive metric ordering validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/eplus.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/epmfs.go -->
# sources/user-network-fs/rclone/backend/union/policy/epmfs.go

## Purpose
`EpMfs` implements existing-path most-free-space selection. It chooses the existing candidate with the largest reported free space.

## Important APIs, types, and functions
`EpMfs` embeds `EpAll` and registers as `"epmfs"`. `mfs` and `mfsEntries` compare `GetFreeSpace` values. Action/create/search methods delegate to existing-path selection and then return one candidate.

## Control flow and state
Action and create are restricted by `EpAll` filtering. Search calls `epall`. If no candidate reports a free-space value greater than the initialized zero, the policy returns `fs.ErrorObjectNotFound`.

## Dependencies and integration points
It uses `context`, union `upstream`, and `fs`. It is the union backend's default `create_policy`, so `union.NewFs` commonly routes new object placement through the non-existing-path `Mfs` variant that embeds this implementation.

## Risks and test signals
Backends without free-space support are logged and represented as near-infinite by upstream wrappers, which can bias placement. Cached usage can lag recent writes. Default union tests exercise `create_policy=epmfs`/`mfs`-style placement broadly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/epmfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/eprand.go -->
# sources/user-network-fs/rclone/backend/union/policy/eprand.go

## Purpose
`EpRand` implements existing-path random selection. It first gathers all existing candidates using `EpAll`, then returns one random candidate.

## Important APIs, types, and functions
`EpRand` embeds `EpAll` and registers as `"eprand"`. Helpers `rand` and `randEntries` call `math/rand.Intn`. Category methods call the corresponding `EpAll` method and reduce the result to one.

## Control flow and state
Action/create methods inherit permission and existing-parent filtering from `EpAll`. Search checks existence with `epall`. Entry methods return random entries after `EpAll` filtering. The policy holds no state and uses the package-global pseudo-random generator.

## Dependencies and integration points
It imports `context`, `math/rand`, union `upstream`, and `fs`. It is distinct from `Rand`, which uses `All` for creation and therefore does not require existing parent candidates in the same way.

## Risks and test signals
Selection is nondeterministic and the global random source is not explicitly seeded here. Tests with random policies can only verify contract-level behavior, not exact branch choice.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/eprand.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/ff.go -->
# sources/user-network-fs/rclone/backend/union/policy/ff.go

## Purpose
`FF` implements first-found create behavior while inheriting existing-path behavior from `EpFF` for action and search.

## Important APIs, types, and functions
`FF` embeds `EpFF` and registers as `"ff"`. Its `Create` method filters no-create upstreams and returns the first remaining upstream.

## Control flow and state
`Create` returns object-not-found for no candidates and permission-denied for no creatable candidates. Unlike `EpFF.Create`, it does not check that the target parent path exists before selecting; it simply chooses the first creatable configured upstream.

## Dependencies and integration points
Imports are `context`, union `upstream`, and `fs`. `ff` is the default union `search_policy`; it is also used as a create policy in some configurations.

## Risks and test signals
The file's behavior is straightforward, but callers may expect "first found" to mean existence-based for creation. Generic union tests use `search_policy=ff` and validate contract behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/ff.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/lfs.go -->
# sources/user-network-fs/rclone/backend/union/policy/lfs.go

## Purpose
`Lfs` implements least-free-space create behavior without requiring the target path to exist. Action and search behavior come from `EpLfs`.

## Important APIs, types, and functions
`Lfs` embeds `EpLfs` and registers as `"lfs"`. `Create` filters creatable upstreams and calls `p.lfs` to return one selected upstream.

## Control flow and state
Create returns object-not-found for empty candidates, permission-denied when all are no-create, and otherwise selects the qualifying upstream with least free space above `min_free_space`.

## Dependencies and integration points
It imports `context`, union `upstream`, and `fs`. It reuses the free-space helper and risks from `eplfs.go`.

## Risks and test signals
The policy can select a nearly full backend by design, as long as it is above the configured minimum. It depends on usage cache freshness and optional About support. Coverage is indirect through policy registration and union functional tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/lfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/lno.go -->
# sources/user-network-fs/rclone/backend/union/policy/lno.go

## Purpose
`Lno` implements least-number-of-objects create behavior. It embeds `EpLno` for action/search and overrides create to choose among all creatable upstreams.

## Important APIs, types, and functions
`Lno` registers as `"lno"`. `Create` filters no-create upstreams and calls `p.lno`.

## Control flow and state
The create path has no path-existence check beyond permission filtering. Selection is based on upstream object-count metrics returned through cached `About` data.

## Dependencies and integration points
It imports `context`, union `upstream`, and `fs`, and reuses helpers from `eplno.go`.

## Risks and test signals
Unsupported object count is treated as zero by upstream wrappers, which may bias new files to backends that cannot report counts. Tests are indirect.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/lno.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/lus.go -->
# sources/user-network-fs/rclone/backend/union/policy/lus.go

## Purpose
`Lus` implements least-used-space create behavior. It embeds `EpLus` for existing-path categories and overrides create to choose by used bytes among all creatable upstreams.

## Important APIs, types, and functions
`Lus` registers as `"lus"`. `Create` filters creatable upstreams and calls `p.lus`, returning a single upstream.

## Control flow and state
Create does not require the parent to already exist. Usage metrics are read from upstream cache via `GetUsedSpace`, and unsupported metrics are treated as zero.

## Dependencies and integration points
It imports `context`, union `upstream`, and `fs`. `TestPolicy1` configures this as create policy, making it one of the explicitly exercised non-default policies.

## Risks and test signals
Unsupported or stale used-space values may skew placement. The policy can concentrate writes on a backend whose usage data is unavailable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/lus.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/mfs.go -->
# sources/user-network-fs/rclone/backend/union/policy/mfs.go

## Purpose
`Mfs` implements most-free-space create behavior and is the default create-policy family for union remotes.

## Important APIs, types, and functions
`Mfs` embeds `EpMfs` and registers as `"mfs"`. `Create` filters no-create upstreams and calls `p.mfs`.

## Control flow and state
Create returns a single creatable upstream with the largest free-space metric. It does not require the path or parent to already exist, leaving directory creation to the caller's recursive creation path when needed.

## Dependencies and integration points
It imports `context`, union `upstream`, and `fs`. `union.NewFs` defaults to `epmfs` in config, and many examples use this placement semantics.

## Risks and test signals
Free-space data may be unsupported or cached. A backend reporting near-infinite free space because `About` is unsupported may be selected frequently. Generic union tests with default policy configuration are the primary coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/mfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/newest.go -->
# sources/user-network-fs/rclone/backend/union/policy/newest.go

## Purpose
`Newest` selects the candidate with the latest modification time. It is an existing-path policy useful when duplicate paths exist across upstreams and the most recently modified version should win.

## Important APIs, types, and functions
`Newest` embeds `EpAll` and registers as `"newest"`. `newest` concurrently probes upstreams with `findEntry` and reads `ModTime`. `newestEntries` reads entry modtimes under a five-second context timeout. Action, create, and search methods select one candidate after permission/existence filtering.

## Control flow and state
Action filters writable upstreams, then chooses the newest exact path. Create filters creatable upstreams and chooses the newest parent path (`path+"/.."`). Search chooses newest target path. Entry methods choose newest from provided candidates.

## Dependencies and integration points
Imports include `context`, `path`, `sync`, `time`, union `upstream`, and `fs`. It relies on accurate modtime support from underlying remotes and `findEntry` list semantics.

## Risks and test signals
Backends with weak modtime precision or slow `ModTime` calls can affect choice and latency. `newestEntries` uses `context.Background()` rather than caller context, so cancellation does not propagate there. Coverage appears indirect via registry/functional use rather than dedicated tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/newest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/policy.go -->
# sources/user-network-fs/rclone/backend/union/policy/policy.go

## Purpose
This file defines the union policy interface, registry, and shared helpers. Policies decide which upstream filesystem or upstream entry a union operation should act on.

## Important APIs, types, and functions
`Policy` has three filesystem-level methods (`Action`, `Create`, `Search`) and three entry-level methods (`ActionEntries`, `CreateEntries`, `SearchEntries`). `registerPolicy` stores lower-cased names in a package map, and `Get` resolves configured policy names. Helpers `filterRO`, `filterROEntries`, `filterNC`, `filterNCEntries`, `parentDir`, `clean`, and `findEntry` implement permission filtering and path lookup.

## Control flow and state
Policy registration occurs from individual policy file `init` functions. `findEntry` cleans a remote, lists its parent directory, handles root specially, and compares remote names case-sensitively or case-insensitively based on backend features.

## Dependencies and integration points
Dependencies are `context`, `fmt`, `path`, `strings`, `time`, union `upstream`, and `fs`. `union.NewFs` calls `Get` for action/create/search policy names. Every policy implementation shares these helpers.

## Risks and test signals
The global registry has no collision protection. `findEntry` performs a list of the parent, so lookup cost and correctness depend on backend listing behavior and case-insensitivity flags. Policy test coverage is mostly via union integration configurations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/rand.go -->
# sources/user-network-fs/rclone/backend/union/policy/rand.go

## Purpose
`Rand` implements random selection across all eligible candidates. It differs from `EpRand` by inheriting `All`, so create selects from all creatable upstreams instead of existing-path candidates.

## Important APIs, types, and functions
`Rand` embeds `All` and registers as `"rand"`. Helpers `rand` and `randEntries` call `math/rand.Intn`. Action, create, and entry methods call `All` then reduce to one; search calls `epall` and reduces to one.

## Control flow and state
Action and create first collect all eligible candidates via `All`. Search still requires existing paths through `epall`. Entry search returns a random entry from all provided entries after guarding empty input.

## Dependencies and integration points
Imports are `context`, `math/rand`, union `upstream`, and `fs`. `TestPolicy2` configures `create_policy=rand`, giving contract-level coverage.

## Risks and test signals
Selection is nondeterministic and uses the package-global random source. Tests should avoid asserting exact placement. Random create placement can make behavior harder to reproduce when debugging multi-upstream state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/policy/rand.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/union.go -->
# sources/user-network-fs/rclone/backend/union/union.go

## Purpose
This file implements rclone's `union` backend, presenting multiple upstream remotes as one overlay filesystem. It registers config options, resolves upstream wrappers, applies action/create/search policies, merges listings, fans out writes, and aggregates quota/features/errors.

## Important APIs, types, and functions
`Fs` stores name/root/options/upstreams, feature mask, hash intersection, and three `policy.Policy` instances. Key methods include `NewFs`, `wrapEntries`, `Mkdir`, `MkdirMetadata`, `Rmdir`, `Purge`, `Copy`, `Move`, `DirMove`, `DirSetModTime`, `ChangeNotify`, `DirCacheFlush`, `Put`, `PutStream`, `About`, `List`, `ListR`, `NewObject`, `mergeDirEntries`, `Shutdown`, and `CleanUp`. Helpers include `multiReader`, `put`, `parentDir`, and `multithread`.

## Control flow and state
`NewFs` parses options, migrates deprecated `remotes`, rejects empty/single/self-referential upstreams, constructs upstreams concurrently, handles root-as-file, prepares writeback, resolves policies, masks features across upstreams, computes hash intersection, and marks the backend as overlay. Listing concurrently lists all upstreams, wraps entries, and merges by remote path before search-policy selection chooses the visible entry. Writes select create-policy upstreams, recursively create parents when needed, tee input to multiple branches with `multiReader`, and wrap resulting objects. Action operations fan out to action-policy candidates.

## Dependencies and integration points
The implementation depends on union `common`, `policy`, `upstream`, rclone `fs`, `configstruct`, `hash`, `operations`, `walk`, and standard concurrency/io/path packages. It exposes many optional rclone interfaces including purge, put stream, copy/move, dir move, metadata mkdir, change notify, list recursive, shutdown, and cleanup.

## Risks and test signals
Risks include partial multi-upstream failures, feature masking mismatches, stale usage decisions, nondeterministic policy behavior, and large memory/backpressure effects from teeing streams. `MkdirMetadata` can pass nil entries for upstreams that lack metadata support before wrapping. Tests cover standard/RO/NC/policy configurations, internal read-only write fallback, and mixed Move/Copy capability.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/union.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/union_internal_test.go -->
# sources/user-network-fs/rclone/backend/union/union_internal_test.go

## Purpose
This file contains union backend internal tests that require access to unexported fields. It validates read-only fallback behavior and move support when upstreams have complementary server-side capabilities.

## Important APIs, types, and functions
`MakeTestDirs` creates temporary local directories. `TestInternalReadOnly` is run via `InternalTest` for `TestUnionRO`. `TestMoveCopy` constructs a union over a local backend and memory backend and checks feature exposure plus actual moves.

## Control flow and state
The read-only test writes a file directly to the read-only upstream, reads it through union, updates through union, verifies the writable layer shadows it, removes the union object, then verifies the original read-only object reappears. `TestMoveCopy` builds `:union,upstreams='<local> :memory:bucket':`, inspects underlying feature sets, writes one object to each upstream, and uses `operations.Move` to ensure local move and memory copy-plus-remove both work under union.

## Dependencies and integration points
Dependencies include rclone `fs`, `object`, `operations`, `fstest`, `fstests`, `random`, testify, and standard test/runtime/time utilities. It integrates with `fstests.InternalTester`.

## Risks and test signals
These tests guard subtle overlay behavior: updates to read-only candidates must create a writable replacement rather than fail, and union `Move` should be enabled when every upstream can move either through native move or copy/delete fallback. The macOS feature adjustment accounts for local backend copy behavior differences.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/union_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/union_test.go -->
# sources/user-network-fs/rclone/backend/union/union_test.go

## Purpose
This file defines external union backend test configurations for the generic rclone filesystem test suite.

## Important APIs, types, and functions
`TestIntegration` runs against a user-provided remote. `TestStandard`, `TestRO`, `TestNC`, `TestPolicy1`, `TestPolicy2`, and `TestPolicy3` synthesize local upstream directories and pass union config through `fstests.ExtraConfigItem`. The file also lists unimplementable FS/Object methods for the generic suite.

## Control flow and state
When no `-remote` is supplied, tests create three temp local directories and configure union with different upstream suffixes and policies. Standard uses `epall`/`epmfs`/`ff`; RO marks two upstreams `:ro`; NC marks two `:nc`; policy variants exercise `all`, `lus`, `rand`, and `ff` combinations. Each run delegates behavior assertions to `fstests.Run`.

## Dependencies and integration points
It imports local and memory backends for registration, the union package, `fstest`, and `fstests`.

## Risks and test signals
These tests are broad contract signals for common configurations and permission suffixes, but they do not assert exact policy placement. `QuickTestOK` enables faster local contract runs for synthetic configurations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/union_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/upstream/upstream.go -->
# sources/user-network-fs/rclone/backend/union/upstream/upstream.go

## Purpose
This file wraps real rclone filesystems and entries with union-specific metadata: root path, permissions, usage cache, writeback target, and helpers for optional object/directory interfaces.

## Important APIs, types, and functions
`Fs` embeds `fs.Fs` and stores `RootFs`, `RootPath`, options, writable/creatable flags, usage cache, and writeback fields. `Directory`, `Object`, and `Entry` wrap `fs.Directory`, `fs.Object`, and `fs.DirEntry`. `New` parses upstream specs and suffixes `:ro`, `:nc`, and `:writeback`. `Prepare` validates at most one writeback upstream. Methods wrap entries, expose permissions, proxy `Put`, `PutStream`, `Update`, metadata/tier/id/mime methods, `Writeback`, `About`, `GetFreeSpace`, `GetUsedSpace`, `GetNumObjects`, and usage cache refresh.

## Control flow and state
`New` resolves both the root filesystem and rooted filesystem through rclone cache and pins the wrapper. Usage starts empty and expires based on `CacheTime`. First usage read runs synchronously via `sync.Once`; later refreshes may run in the background. Put/update methods adjust cached used/free/object counts optimistically after successful writes.

## Dependencies and integration points
Dependencies include union `common`, rclone `fs`, `cache`, `fspath`, `operations`, and standard concurrency/time packages. Policy files query permission and usage methods; union entry `Open` invokes `Writeback`.

## Risks and test signals
Usage adjustment in `Object.Update` computes a `delta` but adds the old size rather than delta, which is a risk for cached accounting. Background `cacheUpdate` is not fully mutex-protected. Unsupported usage fields return sentinel values that materially affect placement policies. Internal tests exercise read-only and writeback-adjacent behavior indirectly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/union/upstream/upstream.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/webdav/api/types.go -->
# sources/user-network-fs/rclone/backend/webdav/api/types.go

## Purpose
This file defines XML types and helpers for WebDAV PROPFIND/PROPPATCH/error/quota responses. It normalizes divergent WebDAV server representations into values consumed by `webdav.go`.

## Important APIs, types, and functions
Types include `Multistatus`, `Response`, `Prop`, `PropValue`, `Error`, custom `Time`, and `Quota`. `Prop.Code` parses the first HTTP status string. `Prop.StatusOK` returns true if any propstat status is 2xx and treats missing status as OK. `Prop.Hashes` extracts ownCloud/Nextcloud checksum strings or Fastmail `ME:sha1hex`. `Time.MarshalXML` and `Time.UnmarshalXML` handle multiple date formats. `Error.Error` formats WebDAV server errors.

## Control flow and state
`UnmarshalXML` tries RFC1123, RFC1123Z, UnixDate, no-leading-zero RFC1123, and RFC3339-like formats, then logs a parse failure once and uses epoch. `Hashes` lowercases checksum strings and splits space-separated algorithms. `StatusOK` handles multi-propstat responses by accepting any 2xx response.

## Dependencies and integration points
It imports XML, regex, string/time utilities, sync, rclone `fs`, and `hash`. `webdav.go` relies on these types for listing, metadata, quota, and error handling.

## Risks and test signals
The XML struct tags intentionally flatten multiple propstats, which is convenient but lossy. Time parse fallback to epoch can mask server issues. `types_test.go` directly covers mixed-status `StatusOK` behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/webdav/api/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/webdav/api/types_test.go -->
# sources/user-network-fs/rclone/backend/webdav/api/types_test.go

## Purpose
This file unit-tests the WebDAV API `Prop.StatusOK` helper.

## Important APIs, types, and functions
`TestPropStatusOK` defines table cases for empty status, single 200, single 404, mixed 404/200, mixed 200/404, and all non-2xx statuses.

## Control flow and state
Each subtest constructs a `Prop` with a status slice and compares `StatusOK()` with the expected boolean. There is no external state.

## Dependencies and integration points
Only `testing` is imported. The test protects behavior used by `webdav.listAll`, `readMetaDataForPath`, and modtime PROPPATCH response handling.

## Risks and test signals
The key signal is that any 2xx propstat makes the property usable. This matters for multi-propstat servers where missing optional properties produce 404 alongside valid core properties.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/webdav/api/types_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/webdav/chunking.go -->
# sources/user-network-fs/rclone/backend/webdav/chunking.go

## Purpose
This file implements Nextcloud chunked upload support using WebDAV upload directories under `/dav/uploads/USER/`.

## Important APIs, types, and functions
`shouldRetryChunkMerge` handles Nextcloud merge retry semantics, especially 423 Locked and post-lock 404 behavior. `setUploadChunkSize` supports tests. `getChunksUploadDir` derives a stable upload directory name from MD5 of the destination file path. `getChunksUploadURL` extracts base URL and user from `/dav/files/USER`. `shouldUseChunkedUpload`, `updateChunked`, `uploadChunks`, `createChunksUploadDirectory`, `mergeChunks`, and `purgeUploadedChunks` implement the upload lifecycle.

## Control flow and state
Chunked update purges any stale upload directory, creates a new MKCOL directory, uploads sequential chunk objects named by zero-padded byte ranges, then MOVEs `.file` to the final destination with headers from `extraHeaders`. Upload chunks use repeatable readers and `GetBody` so low-level retries can replay request bodies. Merge retries back off after 423 and treats a later 404 as success if a lock was observed.

## Dependencies and integration points
It depends on `fs`, `readers`, `rest`, and standard crypto/http/path/time packages. It is selected from `Object.Update` in `webdav.go` when vendor is Nextcloud, chunking is enabled, and source size exceeds chunk size.

## Risks and test signals
Chunk uploads are sequential and leave cleanup to purge-on-next-attempt if merge fails. The URL regex requires the configured endpoint to use `/dav/files/USERNAME`, not `/webdav`. Generic WebDAV Nextcloud integration config includes chunked upload coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/webdav/chunking.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/webdav/odrvcookie/fetch.go -->
# sources/user-network-fs/rclone/backend/webdav/odrvcookie/fetch.go

## Purpose
This file fetches SharePoint Online authentication cookies (`FedAuth` and `rtFa`) for WebDAV access using a username/password WS-Trust flow.

## Important APIs, types, and functions
`CookieAuth` stores user, password, and endpoint. `CookieResponse` holds cookies. XML response types include `SharepointSuccessResponse`, `SuccessResponseBody`, `SharepointError`, and `ErrorResponseBody`. `New`, `Cookies`, `getSPCookie`, `getSPTokenURL`, and `getSPToken` implement the flow. `spTokenURLMap` maps endpoint TLDs to Microsoft login hosts.

## Control flow and state
`Cookies` first posts a templated SOAP request to the appropriate STS endpoint to get a binary security token. It then posts that token to `/_forms/default.aspx?wa=wsignin1.0` on the SharePoint host using an HTTP client with cookie jar, collecting `rtFa` and `FedAuth`.

## Dependencies and integration points
Dependencies include XML/template/http/cookiejar/url, rclone `fs`/`fshttp`, and `publicsuffix`. `webdav.setQuirks("sharepoint")` creates `CookieAuth`, sets cookies on the rest client, and starts periodic renewal.

## Risks and test signals
This is a legacy username/password authentication path and is sensitive to Microsoft auth changes, TLD mapping, MFA, and error XML shape. There are no direct unit tests in this subset; WebDAV SharePoint integration is the main signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/webdav/odrvcookie/fetch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/webdav/odrvcookie/renew.go -->
# sources/user-network-fs/rclone/backend/webdav/odrvcookie/renew.go

## Purpose
This file provides a tiny periodic cookie renewal helper for SharePoint WebDAV authentication.

## Important APIs, types, and functions
`CookieRenew` stores a `time.Ticker` and renewal callback. `NewRenew` creates the ticker, starts `Renew` in a goroutine, and returns the struct. `Renew` loops forever, invoking `renewFn` on every tick.

## Control flow and state
The goroutine blocks on ticker ticks and never stops; there is no close or cancellation method. State is limited to the ticker and callback.

## Dependencies and integration points
It imports only `time`. `webdav.setQuirks("sharepoint")` uses `NewRenew(12*time.Hour, ...)` to refresh `FedAuth` and `rtFa` cookies.

## Risks and test signals
The lack of a stop method can leak goroutines for short-lived `Fs` instances. Renewal failures are handled by the caller's callback logging, not by this helper. No direct unit tests cover it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/webdav/odrvcookie/renew.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/webdav/tus-errors.go -->
# sources/user-network-fs/rclone/backend/webdav/tus-errors.go

## Purpose
This file defines error values used by the WebDAV TUS upload implementation for ownCloud Infinite Scale.

## Important APIs, types, and functions
Exported sentinel errors include `ErrChunkSize`, `ErrNilLogger`, `ErrNilStore`, `ErrNilUpload`, `ErrLargeUpload`, `ErrVersionMismatch`, `ErrOffsetMismatch`, `ErrUploadNotFound`, `ErrResumeNotEnabled`, and `ErrFingerprintNotSet`. `ClientError` carries an HTTP status code and body and implements `Error`.

## Control flow and state
There is no dynamic control flow besides formatting `ClientError`. The sentinel errors are returned by TUS creation/chunk retry code.

## Dependencies and integration points
Imports are standard `errors` and `fmt`. `tus.go` returns version/large-upload/nil-upload errors; `tus-uploader.go` returns offset/version/large-upload errors.

## Risks and test signals
Some errors (`ErrNilLogger`, `ErrNilStore`, resume/fingerprint errors) appear retained from a fuller TUS client design and are not active in current flow. No direct tests cover these constants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/webdav/tus-errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/webdav/tus-upload.go -->
# sources/user-network-fs/rclone/backend/webdav/tus-upload.go

## Purpose
This file defines the in-memory upload model used by the WebDAV TUS uploader.

## Important APIs, types, and functions
`Metadata` is a string map. `Upload` stores an `io.ReadSeeker`, size, current offset, fingerprint, and metadata. Methods include `updateProgress`, `Finished`, `Progress`, `Offset`, `Size`, and `EncodedMetadata`. `NewUpload` converts non-seekable readers into an in-memory buffer and returns an upload object.

## Control flow and state
`EncodedMetadata` base64-encodes each metadata value and joins key/value pairs with commas, matching TUS metadata header format. `NewUpload` reads an entire non-seekable input into memory to provide seek support, then initializes offset zero and metadata map.

## Dependencies and integration points
Dependencies are `bytes`, `encoding/base64`, `fmt`, `io`, and `strings`. `tus.go` builds uploads for Infinite Scale, and `tus-uploader.go` seeks and reads from the stream for chunk uploads.

## Risks and test signals
The major risk is memory use: non-seekable large uploads are fully buffered. `Progress` divides by size and should not be called for zero-size uploads unless guarded. Metadata map iteration order is nondeterministic, though TUS metadata order should not matter.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/webdav/tus-upload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/webdav/tus-uploader.go -->
# sources/user-network-fs/rclone/backend/webdav/tus-uploader.go

## Purpose
This file implements chunk-by-chunk upload for the TUS protocol used by ownCloud Infinite Scale.

## Important APIs, types, and functions
`Uploader` stores the target upload URL, `Upload`, current offset, abort flag, progress subscribers, notify channel, and PATCH override setting. Methods include `NotifyUploadProgress`, `Upload`, `UploadChunk`, `uploadChunk`, `broadcastProgress`, and `NewUploader`. `Fs.shouldRetryChunk` interprets TUS chunk responses.

## Control flow and state
`Upload` loops until offset reaches upload size or abort is set. `UploadChunk` seeks to current offset, reads up to configured chunk size, sends a PATCH (or POST override) with `Upload-Offset` and `Tus-Resumable`, updates offset from the server's `Upload-Offset` header on HTTP 204, and notifies subscribers. `broadcastProgress` runs forever reading from `notifyChan`.

## Dependencies and integration points
It depends on `bytes`, `context`, `io`, `net/http`, `net/url`, `strconv`, rclone `fs`, and `rest`. `Object.updateViaTus` creates the uploader after TUS resource creation.

## Risks and test signals
The uploader has no close path for `notifyChan`, so broadcaster goroutines can persist. Chunk request bodies do not define `GetBody`, limiting low-level retry after body write. Offset mismatch/version/large upload are mapped to sentinel errors. No dedicated unit tests appear in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/webdav/tus-uploader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/webdav/tus.go -->
# sources/user-network-fs/rclone/backend/webdav/tus.go

## Purpose
This file wires WebDAV object updates to the TUS resumable upload protocol for ownCloud Infinite Scale.

## Important APIs, types, and functions
`Object.updateViaTus` constructs TUS metadata (`filename`, `mtime`, `filetype`), creates an `Upload`, creates an `Uploader`, and starts upload. `Fs.getTusLocationOrRetry` interprets creation responses. `Object.CreateUploader` performs the initial TUS `POST` to create an upload resource.

## Control flow and state
For creation, the object path is reduced to its parent directory. A zero-length POST is sent to the endpoint root with `Upload-Length`, `Upload-Metadata`, and `Tus-Resumable: 1.0.0`. HTTP 201 supplies the upload location; 412 and 413 return protocol-specific errors. The returned uploader starts from offset zero; resume/fingerprint logic is not implemented.

## Dependencies and integration points
It imports `context`, `fmt`, `io`, `net/http`, `path/filepath`, `strconv`, rclone `fs`, and `rest`. `webdav.Object.Update` selects this path when `f.canTus` is true, set by `setQuirks("infinitescale")`.

## Risks and test signals
There is no persistent resume store despite TUS terminology. `getTusLocationOrRetry` assumes `resp` is non-nil, so caller behavior on transport-level nil response matters. Infinite Scale coverage depends on integration configuration rather than local unit tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/webdav/tus.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/webdav/webdav.go -->
# sources/user-network-fs/rclone/backend/webdav/webdav.go

## Purpose
This file implements rclone's generic WebDAV backend with vendor-specific behavior for Fastmail, Nextcloud, ownCloud, ownCloud Infinite Scale, SharePoint, SharePoint NTLM, rclone's WebDAV server, and generic servers.

## Important APIs, types, and functions
`Options` covers endpoint URL, vendor, credentials, bearer token command, encoding, headers, pacer sleep, Nextcloud chunk size, ownCloud filters, Unix socket, and auth redirect. `Fs` stores endpoint/rest client, feature flags, vendor quirks, auth singleflight, and upload settings. Major methods include `NewFs`, `setQuirks`, `shouldRetry`, `listAll`, `List`, `ListP`, `NewObject`, `Put`, `PutStream`, `Mkdir`, `Rmdir`, `Purge`, `Copy`, `Move`, `DirMove`, `About`, and object methods `Open`, `Update`, `SetModTime`, `Hash`, `Remove`, and metadata readers.

## Control flow and state
Initialization normalizes URL/root, reveals password, configures auth, headers, NTLM transport serialization, error handler, vendor quirks, and root-as-file detection. Listing uses PROPFIND with Depth, requested props, optional auth redirect, URL joining, encoding decode, share/mount filtering, and list helper batching. Upload selection in `Object.Update` creates parents, then chooses TUS for Infinite Scale, Nextcloud chunked upload for large files, or simple PUT. Copy/move use WebDAV COPY/MOVE with Destination and optional ownCloud mtime headers. Metadata is cached per object after PROPFIND and refreshed after updates.

## Dependencies and integration points
The file depends on WebDAV API XML types, SharePoint cookie auth, rclone config/fs/hash/list/rest/pacer/encoder packages, Azure NTLM, singleflight, and standard HTTP/XML/path/concurrency utilities. It implements many rclone optional interfaces including purge, put stream, copy, move, dir move, listp, and about.

## Risks and test signals
Risk clusters are vendor quirks, auth refresh, redirect credential preservation, path escaping, chunk/TUS upload cleanup, PROPFIND response variance, and weak modtime/hash support. `Object.setMetaData` assumes checksum map is non-nil when hash flags are enabled, relying on API helper behavior. Tests cover integration remotes, headers, auth redirect, reserved character escaping, and API status parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/webdav/webdav.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/webdav/webdav_internal_test.go -->
# sources/user-network-fs/rclone/backend/webdav/webdav_internal_test.go

## Purpose
This file contains WebDAV tests that exercise backend internals with local HTTP test servers.

## Important APIs, types, and functions
`prepareServer` builds a server that verifies configured headers on every request and returns a quota PROPFIND response. `prepare` creates a WebDAV `Fs`. Tests include `TestHeaders`, `TestListAllAuthRedirect`, and `TestReservedCharactersInPathAreEscaped`.

## Control flow and state
`TestHeaders` calls `About` and checks custom headers are sent. `TestListAllAuthRedirect` redirects a PROPFIND to a different hostname, enables `auth_redirect`, and asserts the target receives Authorization. `TestReservedCharactersInPathAreEscaped` captures request URI from a 404 server and checks semicolon escaping as `%3B`.

## Dependencies and integration points
Dependencies include `httptest`, `configfile`, `configmap`, `obscure`, rclone `fs`, the webdav package, and testify. These tests validate config parsing, rest-client redirect behavior, and path escaping in `filePath`.

## Risks and test signals
The tests guard security-sensitive and interoperability-sensitive paths: forwarding auth across redirects only when explicitly configured, preserving custom headers, and escaping reserved characters. They are fast local tests compared with the live integration suite.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/webdav/webdav_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/webdav/webdav_test.go -->
# sources/user-network-fs/rclone/backend/webdav/webdav_test.go

## Purpose
This file defines live WebDAV integration test entries for multiple vendors.

## Important APIs, types, and functions
`TestIntegration` runs `TestWebdavNextcloud:` with chunked upload configuration. `TestIntegration2` runs ownCloud when no `-remote` is set and skips chunked upload. `TestIntegration3` runs rclone WebDAV server config and skips chunked upload. `TestIntegration4` runs `TestWebdavNTLM:`. `SetUploadChunkSize` exposes the private chunk-size setter for `fstests`.

## Control flow and state
Each integration test delegates to `fstests.Run` with backend-specific `RemoteName` and `NilObject`. Some skip when `fstest.RemoteName` is set to avoid clashing with explicit remote runs.

## Dependencies and integration points
Imports are rclone `fs`, `fstest`, and `fstests`. The tests depend on external configured remotes for each vendor and on the backend's optional chunk-size test interface.

## Risks and test signals
These are broad contract tests for vendor-specific behavior. They are powerful but environment-dependent; local CI without configured remotes will not cover live WebDAV server variation. Nextcloud chunked upload gets explicit minimum chunk-size coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/webdav/webdav_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/yandex/api/types.go -->
# sources/user-network-fs/rclone/backend/yandex/api/types.go

## Purpose
This file defines JSON API data structures for the Yandex Disk backend and helper behavior for sort-mode values and API errors.

## Important APIs, types, and functions
Types include `DiskInfo`, `ResourceInfoRequestOptions`, `ResourceInfoResponse`, `ResourceListResponse`, `AsyncInfo`, `AsyncStatus`, `CustomPropertyResponse`, `SortMode`, and `ErrorResponse`. `SortMode` provides fluent methods `Default`, `ByName`, `ByPath`, `ByCreated`, `ByModified`, `BySize`, `Reverse`, `String`, and `UnmarshalJSON`. `ErrorResponse` implements `error`.

## Control flow and state
The API structs are plain JSON containers. `SortMode` wraps an unexported `mode` string; builder methods return new values rather than mutating the receiver. `Reverse` toggles a leading `-`. `UnmarshalJSON` stores raw or unquoted string values. `ErrorResponse.Error` formats status, error name, description, and message.

## Dependencies and integration points
Imports are standard `fmt` and `strings`. The Yandex backend uses these structs to request resource listings, parse embedded resources, monitor async operations, carry custom properties, and report API errors.

## Risks and test signals
Because `SortMode.mode` is unexported, callers must use helpers or JSON unmarshal. Manual quote stripping in `UnmarshalJSON` is simple but less strict than `encoding/json` string unmarshalling. No direct tests are in this subset; compile-time backend usage and Yandex integration tests provide signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/yandex/api/types.go -->
