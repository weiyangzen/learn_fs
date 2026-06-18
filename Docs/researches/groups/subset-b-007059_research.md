# subset-b-007059 research

Grouped source research for EOS MGM unit-test sources. Each file section is source-tree-aligned and bounded by reconciliation markers for deterministic per-file extraction.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/XrdMgmOfsTests.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/XrdMgmOfsTests.cc

Purpose: validates `eos::mgm::XrdMgmOfs::prepareOptsToString()` against XRootD prepare option bitmasks. The test is deliberately narrow and acts as a compatibility guard for string rendering used in logging, diagnostics, and prepare workflows.

Important APIs and types: `XrdMgmOfs`, XRootD `Prep_*` constants from `XrdSfs`, `XrdVersion.hh` version macros, and GoogleTest fixture `XrdMgmOfsTest`. Conditional coverage includes `Prep_CANCEL`, `Prep_QUERY`, and `Prep_EVICT` only when compiled with XRootD 4.10+ or 5+.

Control flow: the single `prepareOptsToString` test constructs one option mask at a time and asserts the exact comma-separated output. Priority-only flags render as `PRTY0` through `PRTY3`; non-priority flags implicitly include `PRTY0`.

State and persistence: no persistent state. The fixture has empty setup/teardown; all inputs are constants.

Dependencies and integration: this is a low-level MGM OFS compatibility test tied to XRootD option definitions. Failures signal drift between MGM stringification and XRootD prepare semantics.

Risks and test signals: the exact-string assertions are intentionally brittle. Adding or reordering rendered flags will fail tests even if behavior remains functionally equivalent. Version-gated cases risk coverage gaps on older build environments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/XrdMgmOfsTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/bulk-request/BulkRequestPrepareManagerTest.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/bulk-request/BulkRequestPrepareManagerTest.cc

Purpose: tests `BulkRequestPrepareManager` as the bulk-aware variant of prepare handling. It checks request construction, stage/cancel/evict workflows, per-file error recording, idempotent behavior for empty or missing paths, and CTA report emission.

Important APIs and types: `BulkRequestPrepareManager`, `BulkRequestFactory`, `StageBulkRequest`, `BulkRequest`, `File`, `PrepareArgumentsWrapper`, `MockPrepareMgmFSInterface`, `ClientWrapper`, `ErrorWrapper`, XRootD prepare flags `Prep_STAGE`, `Prep_CANCEL`, and `Prep_EVICT`. It also uses `eos::common::VirtualIdentity::Root()` for request factory coverage.

Control flow: each workflow constructs prepare arguments, installs GoogleMock expectations on the mock MGM filesystem, invokes `pm.prepare(...)`, then inspects return codes and `pm.getBulkRequest()`. Stage success calls existence checks, workflow xattr lookup, access checks, `FSctl`, and EOS-CTA report methods per file. Empty-path stage returns `SFS_DATA` with a zero-file bulk request. All-missing stage still returns `SFS_DATA` and stores errors for each file. Cancel with partially missing files remains successful in the bulk manager. Evict success performs filesystem actions but does not retain a bulk request.

State and persistence: state is in-memory inside the manager-owned `BulkRequest`. The test verifies files and file errors are retained in request order. No disk persistence is used.

Dependencies and integration: integrated with common test fixtures in `PrepareManagerTest.hh` and reusable behavior lambdas from `MockPrepareMgmFSInterface`. The test codifies interaction contracts with `IMgmFileSystemInterface`, xattrs such as prepare workflow markers, and EOS report records.

Risks and test signals: it asserts precise call counts, making it sensitive to internal refactors. The most important signal is semantic divergence from plain `PrepareManager`: bulk operations should preserve idempotent, per-file status behavior and should not fail the whole request when errors can be represented in the bulk request.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/bulk-request/BulkRequestPrepareManagerTest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/bulk-request/MockPrepareMgmFSInterface.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/bulk-request/MockPrepareMgmFSInterface.cc

Purpose: provides concrete static lambda implementations used by prepare-manager tests to simulate MGM filesystem outcomes without a real namespace or tape backend.

Important APIs and types: implements static `std::function` members declared in `MockPrepareMgmFSInterface.hh`. The lambdas target `IMgmFileSystemInterface` methods: `_exists`, `_attr_ls`, `_stat`, and `_access`. It uses `SFS_OK`, `SFS_ERROR`, `XrdSfsFileExistIsFile`, `XrdSfsFileExistNo`, `XRDSFS_HASBKUP`, and `XRDSFS_OFFLINE`.

Control flow: existence lambdas set output references and return success or error. Attribute-list lambdas populate xattr maps with stage, abort, evict, retrieve-error, archive-error, request-id, and request-time keys. Stat lambdas encode disk/tape state via `st_rdev` bits or set an error in `XrdOucErrInfo`. Access lambdas return allow or deny.

State and persistence: static function objects are process-wide test helpers. They mutate only caller-owned output arguments; no persistent state is stored beyond constants.

Dependencies and integration: depends on EOS common constants for xattr names and XRootD stat flags. The behavior feeds both `PrepareManagerTest.cc` and `BulkRequestPrepareManagerTest.cc`.

Risks and test signals: these lambdas are part of the test oracle. If production logic changes xattr names, stat flag interpretation, or permission checks, tests may fail because the mock no longer mirrors production. Static mutable test helpers can also hide inter-test coupling if reassigned elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/bulk-request/MockPrepareMgmFSInterface.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/bulk-request/MockPrepareMgmFSInterface.hh -->
## sources/distributed-fs/eos/unit_tests/mgm/bulk-request/MockPrepareMgmFSInterface.hh

Purpose: declares a GoogleMock implementation of `IMgmFileSystemInterface` for prepare-manager tests, plus reusable static lambdas and constants describing common filesystem states.

Important APIs and types: `MockPrepareMgmFSInterface` mocks `addStats`, `isTapeEnabled`, `getReqIdMaxCount`, `Emsg`, overloaded `_exists`, `_attr_ls`, `_access`, `FSctl`, `_stat`, `_stat_set_flags`, `get_logId`, `get_host`, and `writeEosReportRecord`. It also exposes lambdas for file existence, directory workflow xattrs, query xattrs, stat states, and permission outcomes.

Control flow: the header is declarative; tests configure `ON_CALL` and `EXPECT_CALL` with either simple returns or `Invoke(...)` using the static lambdas. The mocked surface is broad enough to exercise stage, cancel, evict, and query prepare logic.

State and persistence: no instance state beyond gmock bookkeeping. Static constants include error strings, retrieve request id/time, and a regex for EOS report records.

Dependencies and integration: includes MGM namespace support, XRootD error and security entities, virtual identity, namespace xattr maps, and the bulk request filesystem interface. It is the central adapter between unit tests and prepare-manager dependencies.

Risks and test signals: overloaded mock methods must match production signatures exactly. Broad mocking makes interaction tests precise but can be brittle if implementation order or call grouping changes without changing external behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/bulk-request/MockPrepareMgmFSInterface.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/bulk-request/PrepareManagerTest.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/bulk-request/PrepareManagerTest.cc

Purpose: tests the non-bulk `PrepareManager` workflows for option stringification, argument wrapping, stage, cancel, evict, and query behavior.

Important APIs and types: `PrepareManager`, `PrepareUtils`, `PrepareArgumentsWrapper`, `QueryPrepareResult`, `MockPrepareMgmFSInterface`, `ClientWrapper`, `ErrorWrapper`, and XRootD return codes `SFS_OK`, `SFS_DATA`, and `SFS_ERROR`.

Control flow: stage tests validate successful workflow execution, duplicated path handling, no-path behavior, all-missing files, and one missing file. Cancel and evict tests mirror existence and workflow-xattr flows but expect different aggregate outcomes. Query tests construct a `QueryPrepareResult` and assert per-file fields including path order, online status, tape status, existence, request-id presence, request time, and error text.

State and persistence: no external persistence. The manager owns the injected mock interface. Query responses preserve input ordering, including duplicates, which is a key state contract for callers.

Dependencies and integration: tests calls into `IMgmFileSystemInterface` for existence, xattr listing, stat, access, `FSctl`, MGM logging identity, host identity, and EOS report records. It also covers xattr-derived retrieve/archive error propagation.

Risks and test signals: call counts encode implementation details. More importantly, tests document that plain `PrepareManager` is stricter than the bulk manager in some missing-file cancel/evict cases. Query behavior around permissions and tape/disk flags is high-risk because callers depend on exact status fields and user-facing error text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/bulk-request/PrepareManagerTest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/bulk-request/PrepareManagerTest.hh -->
## sources/distributed-fs/eos/unit_tests/mgm/bulk-request/PrepareManagerTest.hh

Purpose: provides shared fixtures and RAII helpers for prepare-manager unit tests.

Important APIs and types: `ClientWrapper` builds and owns an `XrdSecEntity` from protobuf helpers. `ErrorWrapper` builds and owns an `XrdOucErrInfo`. `PrepareManagerTest` initializes and resets `eos::common::Mapping`, exposes `getDefaultClient()`, `getDefaultError()`, `generateDefaultPaths()`, and `generateEmptyOinfos()`. `BulkRequestPrepareManagerTest` derives from `PrepareManagerTest`.

Control flow: setup initializes global mapping before each test; teardown resets it. Path generation returns reverse-numbered `pathN` strings. Opaque-info generation returns empty strings matching the path count.

State and persistence: manages heap allocations for XRootD client/error objects to avoid leaks. It also touches process-global mapping state, so teardown is essential for isolation.

Dependencies and integration: includes `XrdMgmOfs`, XRootD version headers, gtest/gmock, `PrepareUtils`, auth proto utilities, and `PrepareArgumentsWrapper`.

Risks and test signals: the helper returns wrappers by value; callers rely on RAII lifetimes lasting through the prepare call. Any change in auth proto conversion or mapping initialization can affect all prepare tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/bulk-request/PrepareManagerTest.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/BalancerEngineTypeTests.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/BalancerEngineTypeTests.cc

Purpose: validates string-to-`GroupStatus` conversion for group-balancer status labels.

Important APIs and types: `getGroupStatus`, `GroupStatus::ON`, `GroupStatus::DRAIN`, and `GroupStatus::OFF`. It uses both compile-time `static_assert` with string literals and runtime assertions with `std::string`, `const char*`, and string-view-like inputs.

Control flow: compile-time checks ensure constexpr conversion works for `"on"`, `"drain"`, and unknown values. Runtime checks exercise conversion overloads or implicit conversions.

State and persistence: none.

Dependencies and integration: depends only on `BalancerEngineTypes.hh` and GoogleTest. This is a guard for parsing config or group status text into balancer decisions.

Risks and test signals: unknown strings fall back to `OFF`, which is conservative but can hide malformed config unless higher-level validation reports it. Compile-time coverage is useful for refactors of constexpr parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/BalancerEngineTypeTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/FreeSpaceBalancerTests.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/FreeSpaceBalancerTests.cc

Purpose: tests `FreeSpaceBalancerEngine` calculations that classify groups by available free space and optional blocklist configuration.

Important APIs and types: `FreeSpaceBalancerEngine`, `populateGroupsInfo`, `configure`, `recalculate`, `updateGroups`, `getGroupFreeSpace`, `getFreeSpaceULimit`, `getFreeSpaceLLimit`, and `threshold_group_set`.

Control flow: the simple case populates five ON groups with used/capacity values, checks computed average free-space target and limits, and asserts over/under-threshold sets. The blocklisting case removes configured groups from source/target eligibility, recalculates, and verifies new target/source sets and limits.

State and persistence: all state is in-memory inside the engine's group data and config map. No external persistence.

Dependencies and integration: validates interaction between engine configuration parsing and group classification. It is part of the larger group-balancer decision path that chooses transfer source and target groups.

Risks and test signals: threshold arithmetic uses integer byte examples for deterministic expectations. Naming can be counterintuitive: under-threshold groups are targets in the free-space sense. Blocklist config key spelling is important to preserve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/FreeSpaceBalancerTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/GroupBalancerUtilsTests.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/GroupBalancerUtilsTests.cc

Purpose: tests utility functions used by balancer engines and transfer filtering.

Important APIs and types: `calculateAvg`, `is_valid_threshold`, `extract_percent_value`, `extract_commalist_value`, `SkipFileFn`, `NullFilter`, and `PrefixFilter`.

Control flow: average tests update a group-size map and assert exact ratio results. Threshold validation accepts positive numeric strings and rejects zero, negative, float suffixes, and nonnumeric strings. Percent extraction converts config values such as `"5"` to `0.05`, supports defaults, and returns zero for missing keys. Comma-list extraction trims entries into an unordered set. Skip-file tests simulate `getProcTransferNameAndSize` filtering, ensuring a null filter passes all paths and a prefix filter suppresses `/proc/` paths.

State and persistence: no persistent state; helpers operate on local maps and strings.

Dependencies and integration: depends on `BalancerEngineUtils.hh` and `ConverterUtils.hh`. These helpers feed engine configuration and transfer selection behavior.

Risks and test signals: exact floating-point equality is used where values are simple. The tests document accepted config syntax; broadening parser behavior could require updating the test oracle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/GroupBalancerUtilsTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/GroupsInfoFetcherTests.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/GroupsInfoFetcherTests.cc

Purpose: tests group status filtering behavior in `eosGroupsInfoFetcher`.

Important APIs and types: `eosGroupsInfoFetcher`, `GroupStatus`, and status predicates configured through the fetcher constructor or setter.

Control flow: the default test asserts default status acceptance. The drain-status test checks whether drain status is treated according to the configured predicate. The lambda-status test installs a custom lambda and verifies it controls validity.

State and persistence: predicate state is held in memory by the fetcher object. No external I/O is exercised.

Dependencies and integration: this is a boundary test for the component that feeds balancer engines with group data. Correct filtering determines which groups can act as sources or targets.

Risks and test signals: because tests are small, they mainly guard predicate plumbing rather than namespace-fetching behavior. Integration with real MGM group data is outside this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/GroupsInfoFetcherTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/MinMaxBalancerEngineTests.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/MinMaxBalancerEngineTests.cc

Purpose: tests `MinMaxBalancerEngine` threshold configuration and source/target classification based on fixed min/max occupancy limits.

Important APIs and types: `BalancerEngine`, `MinMaxBalancerEngine`, `configure`, `populateGroupsInfo`, `updateGroups`, `get_data`, `pickGroupsforTransfer`, and `threshold_group_set`.

Control flow: configuration converts percentages to fractions. The simple case uses min 80 percent and max 90 percent to classify group1 as underfilled and group5 as overfilled, then verifies transfer pair selection. The update-threshold case changes thresholds after population and calls `updateGroups()` to recompute sets.

State and persistence: engine state includes group sizes, threshold values, and derived over/under sets. No external persistence.

Dependencies and integration: part of the group-balancer engine polymorphic interface. Tests instantiate through `std::unique_ptr<BalancerEngine>` then cast to inspect implementation-specific thresholds.

Risks and test signals: boundary values expose floating-point comparison issues; comments note that values exactly at thresholds can classify unexpectedly due to subtraction precision. This is a risk for production balancing near limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/MinMaxBalancerEngineTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/StdDevBalancerEngineTests.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/StdDevBalancerEngineTests.cc

Purpose: tests `StdDevBalancerEngine`, which classifies groups by deviation from average occupancy using configurable min and max thresholds.

Important APIs and types: `StdDevBalancerEngine`, `BalancerEngine`, `calculateAvg`, threshold getters, `populateGroupsInfo`, `updateGroups`, `get_data`, and `pickGroupsforTransfer`.

Control flow: configure test checks percent parsing. The simple test populates five groups around an average of 0.85 and expects group5 as source and group1 as target. Threshold update tests reduce deviation thresholds and assert recomputed over/under sets. The multi-threshold test verifies asymmetric min/max threshold handling.

State and persistence: in-memory engine state only. Derived sets depend on configured thresholds and current group map.

Dependencies and integration: extends the common balancer engine abstraction and utility average calculation. It validates behavior used by group-balancing transfer planning.

Risks and test signals: exact and near floating-point assertions expose precision sensitivity. Comments document known boundary quirks where equality can become over-threshold because of floating-point subtraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/StdDevBalancerEngineTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/StdDrainerTests.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/StdDrainerTests.cc

Purpose: tests `StdDrainerEngine`, which selects transfers from groups in drain state to eligible online target groups.

Important APIs and types: `StdDrainerEngine`, `engine_conf_t`, `GroupStatus::DRAIN`, `GroupStatus::ON`, `pickGroupsforTransfer`, and `eos::common::pickIndexRR`.

Control flow: default config checks fallback threshold `0.0001`. The simple case classifies one draining source and two under-threshold targets. Round-robin tests populate multiple drain sources and online targets, then verify deterministic source/target selection for explicit seeds and wraparound over many iterations. `pickFS` simulates per-group filesystem selection using separate seeds.

State and persistence: engine stores group classification and thresholds in memory. The test-local `mGroupFSSeed` models independent filesystem round-robin state per source group.

Dependencies and integration: validates drain-specific balancing decisions and expected interaction with container utility round-robin helpers.

Risks and test signals: seed type is `uint8_t`; the loop explicitly checks wraparound after 5000 increments. Production code relying on small seed types must tolerate rollover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/groupbalancer/StdDrainerTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/groupdrainer/DrainProgressTrackerTests.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/groupdrainer/DrainProgressTrackerTests.cc

Purpose: tests `DrainProgressTracker`, an in-memory tracker for per-filesystem drain progress.

Important APIs and types: `DrainProgressTracker`, `setTotalFiles`, `increment`, `getTotalFiles`, `getFileCounter`, `getDrainStatus`, and `dropFsid`.

Control flow: `SetTotalFiles` verifies initial totals, increments, ignored decreases, accepted increases, and recomputed percentages. `Deletions` checks reset after `dropFsid`. `NullTests` and `InvalidFS` cover zero totals, missing fsids, and transitions from invalid to valid totals.

State and persistence: the tracker holds per-fsid counters and totals in memory. No persistent store or external MGM state is involved.

Dependencies and integration: used by group drainer logic to report drain completion percentage. Tests encode percentage semantics: a single increment against total 100 reports `1`, while counter equal to total reports `100`.

Risks and test signals: lowering totals is intentionally ignored to avoid regressions during evolving scans. This can overstate denominator size if production discovers fewer files later.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/groupdrainer/DrainProgressTrackerTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/groupdrainer/GroupDrainerRetry.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/groupdrainer/GroupDrainerRetry.cc

Purpose: tests `RetryTracker`, the small timing helper used to decide when a group-drainer retry/update should run.

Important APIs and types: `RetryTracker`, fields `count` and `last_run_time`, methods `need_update()` and `update()`, and `eos::common::SteadyClock` test clock.

Control flow: verifies the initial tracker needs an update, `update()` increments count and sets time, a fresh tracker does not need another update before the retry interval, and a manually advanced test clock beyond 900 seconds permits update.

State and persistence: state is local to `RetryTracker` fields. Time can be read from real steady clock or injected test clock.

Dependencies and integration: guards retry throttling for group drainer workflows. Correct behavior avoids excessive retries while ensuring stalled drains can be revisited.

Risks and test signals: mixed use of real `std::chrono::steady_clock::now()` and test clock requires careful interpretation. Time-dependent code can become flaky if the clock abstraction changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/groupdrainer/GroupDrainerRetry.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/groupdrainer/GroupDrainerTests.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/groupdrainer/GroupDrainerTests.cc

Purpose: tests static status-reduction helpers in `GroupDrainer`.

Important APIs and types: `GroupDrainer::checkGroupDrainStatus`, `GroupDrainer::isDrainFSMapEmpty`, `GroupStatus`, `FsidStatus`, `fs_status_map_t`, `drain_fs_map_t`, `ActiveStatus`, and `DrainStatus`.

Control flow: status tests build maps of filesystem active/drain states and assert group-level results. All online drained filesystems yield `DRAINCOMPLETE`. Any offline filesystem yields `OFF` and takes precedence. Failed drain states yield `DRAINFAILED` unless unknown/expired online states push the result to the catchall `ON`. `isDrainFSMapEmpty` checks empty maps and groups with empty vectors.

State and persistence: no persistent state. Tests reduce local maps into derived status.

Dependencies and integration: these helpers are central to group-drainer state aggregation from filesystem-level MGM status.

Risks and test signals: precedence ordering is the main risk. Offline dominates failed, while certain unknown states return `ON`; callers must understand that this is not a pure severity ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/groupdrainer/GroupDrainerTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/http/HttpServerTests.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/http/HttpServerTests.cc

Purpose: tests static HTTP path and opaque-token parsing helpers in `HttpServer`.

Important APIs and types: `HttpServer::BuildPathAndEnvOpaque`, `extractPathAndOpaque`, `extractOpaqueWithoutAuthz`, `XrdOucEnv`, normalized HTTP header maps, `xrd-http-fullresource`, `authorization`, `authz`, and `eos.app`.

Control flow: `ParsePathAndToken` verifies missing resource failure, plain resource success, authz from query opaque, authz from header, conflict rejection when both are present, propagation of extra opaque fields, default `eos.app=http`, and client app suffixing as `http/<value>`. Table-driven tests split full paths into path/opaque pairs and strip `authz` from opaque strings regardless of position.

State and persistence: parsing creates a per-call `XrdOucEnv` object; no global state.

Dependencies and integration: uses `IN_TEST_HARNESS` to access test-visible `HttpServer` internals. These helpers integrate HTTP requests with MGM authorization and opaque-info conventions.

Risks and test signals: token precedence and duplicate `eos.app` handling are security-sensitive. The tests assert conflict failure when authorization is supplied both in header and opaque data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/http/HttpServerTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/http/rest-api/tape/JsonCPPTapeModelBuilderTest.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/http/rest-api/tape/JsonCPPTapeModelBuilderTest.cc

Purpose: tests JSON-to-C++ model building for tape stage REST requests.

Important APIs and types: `CreateStageRequestModelBuilder`, `JsonValidationException`, `FILES_KEY_NAME`, `File`, endpoint id `restApiEndpointID`, and request fields such as path, activity, and endpoint.

Control flow: invalid JSON, empty JSON, wrong field names, non-array `files`, malformed file entries, and wrong element formats throw `JsonValidationException`. Valid formats build a model with expected files. Activity-related tests distinguish default endpoint behavior from explicitly supplied endpoint values.

State and persistence: builder state is local to each test. Parsed request objects are in memory only.

Dependencies and integration: includes tape REST model builders and JSON validation exception classes. It validates the REST API boundary before requests enter MGM/tape prepare logic.

Risks and test signals: strict validation protects downstream prepare code from malformed input. Tests focus on schema shape and selected fields, so deeper semantic validation may be elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/http/rest-api/tape/JsonCPPTapeModelBuilderTest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/http/rest-api/tape/JsonCPPTapeModelBuilderTest.hh -->
## sources/distributed-fs/eos/unit_tests/mgm/http/rest-api/tape/JsonCPPTapeModelBuilderTest.hh

Purpose: declares the GoogleTest fixture for tape REST JSON model builder tests.

Important APIs and types: `JsonCPPTapeModelBuilderTest`, inherited `::testing::Test`, and static `std::string restApiEndpointID`.

Control flow: setup and teardown are empty. The static endpoint id is defined in the `.cc` file and reused by builder construction tests.

State and persistence: only fixture-local state plus the static endpoint-id string. No persistence or external services.

Dependencies and integration: includes `mgm/Namespace.hh` and gtest. It gives the `.cc` tests a shared place for endpoint identity constants.

Risks and test signals: minimal fixture. Any future shared setup should preserve isolation because JSON builder tests expect no cross-test state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/http/rest-api/tape/JsonCPPTapeModelBuilderTest.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/http/rest-api/tape/RestApiTest.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/http/rest-api/tape/RestApiTest.cc

Purpose: tests tape REST handler routing and URL parsing/building utilities.

Important APIs and types: `RestHandler`, `TapeRestHandler`, `TapeRestApiConfig`, `RestException`, `URLParser`, `common::HttpResponse`, and fixture `RestApiTest`.

Control flow: constructor tests reject programmer-supplied wrong base URLs. Handler tests call `handleRequest` with missing resource, missing version, unknown resource, and valid resource/version combinations, checking HTTP response status or exceptions. URL parser tests verify prefix matching, parameter extraction from route templates, and URL construction.

State and persistence: handler/config objects are in memory. No network server or persistent state is started.

Dependencies and integration: this is the routing layer between MGM HTTP requests and tape REST handlers. It validates that route structure and version/resource matching behave before business handlers execute.

Risks and test signals: URL shape is an API contract. Exact routing and status behavior can break clients if changed. These are unit-level tests and do not exercise full HTTP transport.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/http/rest-api/tape/RestApiTest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/http/rest-api/tape/RestApiTest.hh -->
## sources/distributed-fs/eos/unit_tests/mgm/http/rest-api/tape/RestApiTest.hh

Purpose: declares shared fixture state for tape REST API tests.

Important APIs and types: `RestApiTest`, `TapeRestApiConfig`, `RestHandler`, static API URL/path/version/resource constants, and helper members used by the `.cc` test implementation.

Control flow: the fixture provides empty setup/teardown and shared constants so route tests are consistent.

State and persistence: static constants only. No persistent or network state.

Dependencies and integration: includes MGM namespace support, REST handler abstractions, and tape REST config. It binds the tests to the REST API version/resource naming contract.

Risks and test signals: changes to API version strings, resource names, or base paths must update both config and tests. The fixture centralizes those values to reduce drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/http/rest-api/tape/RestApiTest.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/placement/ClusterMapFixture.hh -->
## sources/distributed-fs/eos/unit_tests/mgm/placement/ClusterMapFixture.hh

Purpose: defines `SimpleClusterF`, a reusable placement-test fixture with a small hierarchical cluster.

Important APIs and types: `ClusterMgr`, `StorageHandler`, `addBucket`, `addDisk`, `Disk`, `StdBucketType::ROOT`, `SITE`, and `GROUP`, plus disk `ConfigStatus::kRW` and `ActiveStatus::kOnline`.

Control flow: setup builds root bucket 0, two site buckets, three group buckets, and thirty disks distributed as ten disks per group. Group IDs are negative bucket IDs; disk IDs are positive.

State and persistence: fixture owns an in-memory `ClusterMgr`. No external cluster state is used.

Dependencies and integration: used heavily by `SchedulerTests.cc` to exercise round-robin, random, thread-local, and flat scheduler behavior over a stable topology.

Risks and test signals: topology assumptions are embedded in downstream expected counts. Changing disk distribution or bucket IDs will affect many scheduler expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/placement/ClusterMapFixture.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/placement/ClusterMapTests.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/placement/ClusterMapTests.cc

Purpose: tests `ClusterMgr` and storage-handler construction of placement cluster data.

Important APIs and types: `ClusterMgr`, `ClusterData`, `StorageHandler`, `addClusterData`, `getClusterData`, `addBucket`, `addDiskSequential`, `addDisk`, `Bucket`, `Disk`, and standard bucket types.

Control flow: default and dummy-data tests verify cluster-data pointer presence and empty structures. Storage-handler tests build root/site/group hierarchies and validate bucket vector size, bucket indices, IDs, item ordering, and disk vector sizes for sequential, in-order, and sparse/out-of-order disk IDs. `BM_Layout` creates a larger root-to-groups layout with 32 groups and 16 disks per group.

State and persistence: all cluster data is in memory. Sparse disk IDs can grow the disk vector to the maximum ID range, as shown by out-of-order disk test expecting size 150.

Dependencies and integration: this is foundational for placement schedulers that consume `ClusterData`.

Risks and test signals: bucket indexing uses negative bucket IDs mapped to positive vector indexes, which is easy to break. Sparse disk IDs have memory implications and are explicitly tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/placement/ClusterMapTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/placement/FsSchedulerTests.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/placement/FsSchedulerTests.cc

Purpose: tests `FSScheduler`, a higher-level scheduler wrapper that consumes cluster-manager handlers and placement strategy configuration.

Important APIs and types: `FSScheduler`, `ClusterMgr`, `ClusterMgrHandler`, `TestClusterMgrHandler`, strategy configuration methods, and placement result APIs.

Control flow: the test handler builds or exposes cluster state for the scheduler. Tests cover construction, null-handler behavior, default scheduler behavior, geo-scheduler error paths, round-robin placement, and changing placement strategies globally or per space.

State and persistence: state resides in scheduler configuration and the test cluster manager. No persistent cluster store is used.

Dependencies and integration: bridges placement schedulers with MGM-facing cluster-manager handler abstractions. It validates error handling around missing handler state and strategy changes.

Risks and test signals: this file is a contract test for integration wiring rather than deep strategy correctness. Strategy name/config changes can break expected behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/placement/FsSchedulerTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/placement/PlacementStrategyTests.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/placement/PlacementStrategyTests.cc

Purpose: tests `PlacementResult`, the common result object returned by placement strategies and schedulers.

Important APIs and types: `PlacementResult`, `ret_code`, `ids`, `is_valid_placement`, `contains`, boolean conversion, and invalid placement semantics.

Control flow: default construction is expected to be invalid. Valid-placement tests set result code and IDs, then check requested replica count. Contains tests verify membership for valid result IDs and false behavior for invalid or absent IDs.

State and persistence: only local result objects.

Dependencies and integration: `PlacementResult` is consumed throughout placement scheduling; its truthiness and validation methods shape caller error handling.

Risks and test signals: mismatch between `ret_code`, ID count, and boolean conversion could allow bad placements to propagate. These tests guard those small but widely used invariants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/placement/PlacementStrategyTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/placement/RRSeedTests.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/placement/RRSeedTests.cc

Purpose: tests `RRSeed<uint64_t>`, a round-robin seed/counter utility used by placement strategies.

Important APIs and types: `RRSeed`, construction with bounds, `get`, increment/next behavior, wraparound handling, and multithreaded access.

Control flow: construction and out-of-bounds tests verify initial validity. Single-thread tests check deterministic incrementing over a range. The multithread test spawns threads to exercise concurrent seed acquisition. Wraparound verifies behavior near integer limits or configured bounds.

State and persistence: in-memory counter state, likely atomic or locked internally. No external state.

Dependencies and integration: used by round-robin and weighted scheduling paths where fairness and thread safety matter.

Risks and test signals: concurrency correctness is the main risk. If seed increments are not atomic, placement can become biased or duplicate-heavy under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/placement/RRSeedTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/placement/SchedulerTests.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/placement/SchedulerTests.cc

Purpose: extensively tests placement strategies and `FlatScheduler` across hierarchical cluster topologies, weighted strategies, excluded filesystem IDs, forced groups, and concurrent cluster updates.

Important APIs and types: `RoundRobinPlacement`, `FlatScheduler`, `PlacementArguments`, `AccessArguments`, `PlacementResult`, `PlacementStrategyT`, `WeightedRandomStrategy`, `ClusterMgr`, `StorageHandler`, `Disk`, bucket types, `kBaseGroupOffset`, and `SimpleClusterF`.

Control flow: basic tests descend root-to-site-to-group-to-disk using round-robin, random, and thread-local round-robin. Loop tests count distribution across 30 disks and assert every disk is selected. Flat scheduler tests verify recursive scheduling returns valid replica sets. Single-site/no-site tests build alternate topologies and run repeated scheduling. Exclusion tests run many iterations across several strategies and assert excluded fsid 1 never appears. Forced-group tests constrain placement to a specified group and verify out-of-range errors. Weighted tests check that higher disk weights receive more selections. The concurrency test starts many reader threads scheduling while writer threads add groups and disks.

State and persistence: scheduler and cluster state are in memory, but concurrency tests exercise shared `ClusterMgr` snapshot/update behavior. Diagnostic memory output reads `/proc/self/status`.

Dependencies and integration: this is a major integration surface for placement logic, cluster maps, strategy selection, weighting, and thread safety.

Risks and test signals: randomized/weighted behavior is asserted statistically and can be sensitive to algorithm changes. High iteration counts and 100 reader threads make the concurrency test valuable but potentially expensive. Forced-group and exclusion behavior are high-risk because they are policy constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/placement/SchedulerTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/placement/ThreadLocalRRSeedTests.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/placement/ThreadLocalRRSeedTests.cc

Purpose: tests `ThreadLocalRRSeed`, the per-thread seed source for thread-local round-robin placement.

Important APIs and types: `ThreadLocalRRSeed` and its random/seed retrieval behavior.

Control flow: the `random` test obtains seed values and checks that the API returns usable values. It intentionally avoids deterministic ID assertions because thread-local round-robin starts from randomized per-thread positions.

State and persistence: state is thread-local in process memory. No external persistence.

Dependencies and integration: feeds `PlacementStrategyT::kThreadLocalRoundRobin`, reducing cross-thread contention while preserving local round-robin behavior.

Risks and test signals: coverage is light; it mostly catches construction or gross API failures. Distribution quality and independence are tested indirectly in scheduler loop tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/placement/ThreadLocalRRSeedTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/tgc/CachedValueTests.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/tgc/CachedValueTests.cc

Purpose: tests `CachedValue<T>`, a small time-based value cache used in tape garbage collection components.

Important APIs and types: `CachedValue<uint64_t>`, constructor with getter lambda and `maxAgeSecs`, and `get()`.

Control flow: the no-cache test sets `maxAgeSecs` to zero, changes the backing source value, and expects the second `get()` to call the getter again. The cached test uses a long max age and expects the second `get()` to return the original cached value.

State and persistence: cache stores the last value and age metadata in memory. No external persistence.

Dependencies and integration: used by TGC components that poll expensive values such as free space or stats. Tests ensure cache age configuration controls freshness.

Risks and test signals: tests do not manipulate time directly, so expiration after a nonzero age is not covered here. They do protect the important zero-cache behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/tgc/CachedValueTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/tgc/FreedBytesHistogramTests.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/tgc/FreedBytesHistogramTests.cc

Purpose: tests `FreedBytesHistogram`, which tracks bytes freed over a rolling time window for tape garbage collection reporting.

Important APIs and types: `FreedBytesHistogram`, `DummyClock`, `RealClock`, TGC constants, `bytesFreed`, `getTotalBytesFreed`, `getNbBytesFreedInLastNbSecs`, `getFreedBytesInBin`, `setBinWidthSecs`, and exceptions `InvalidNbBins`, `InvalidBinWidth`, `InvalidBinIndex`, and `TooFarBackInTime`.

Control flow: constructor tests validate bin count/width and zero initialization. Invalid constructor and setter tests assert exceptions for zero or too-large values. The main sequence advances a dummy clock through bins, records bytes, checks rolling totals by lookback duration, then advances beyond one full history window. Bin-width migration tests change width from 3 seconds to 4, 5, 6, 2, and 1, asserting redistribution into new bins. Additional tests cover multiple passes, many updates in the same bin, and a time gap larger than the histogram window.

State and persistence: histogram state is in-memory rolling bins plus total freed bytes. Dummy clock provides deterministic time.

Dependencies and integration: feeds TGC telemetry and JSON/status reporting. Accurate rolling-window math is important for operational decisions.

Risks and test signals: this is high-value coverage for off-by-one time boundaries, bin migration, and history-window overflow. It does not test concurrency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/tgc/FreedBytesHistogramTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/tgc/LruTests.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/tgc/LruTests.cc

Purpose: tests `Lru`, the least-recently-used file-id queue used by tape garbage collection.

Important APIs and types: `Lru`, `FidQueue`, `fileAccessed`, `fileDeletedFromNamespace`, `getAndPopFidOfLeastUsedFile`, `size`, `empty`, `maxQueueSizeExceeded`, `toJson`, and exceptions `MaxQueueSizeIsZero`, `QueueIsEmpty`, and `MaxLenExceeded`.

Control flow: construction tests validate queue-size rules. Empty-pop throws. Ordered access tests confirm least-recently-used pop order and that re-accessing an existing fid moves it to the most-recent side. Deletion removes namespace-deleted fids. Max-size tests verify queue truncation/exceeded flag semantics. A disabled performance test exists for 500000 files. JSON tests verify MRU-to-LRU hex formatting and max-length exception behavior.

State and persistence: in-memory queue and index only. No namespace I/O; deletion is simulated through API calls.

Dependencies and integration: LRU feeds selection of candidate files for TGC eviction/cleanup. JSON output integrates with status reporting.

Risks and test signals: queue truncation intentionally retains older candidates after over-capacity insertion, so semantics must be understood before changing. JSON string exactness is brittle but useful for API compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/tgc/LruTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/tgc/MultiSpaceTapeGcTests.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/tgc/MultiSpaceTapeGcTests.cc

Purpose: tests `MultiSpaceTapeGc`, which coordinates tape garbage collectors across one or more EOS spaces.

Important APIs and types: `MultiSpaceTapeGc`, `DummyTapeGcMgm`, `MaxLenExceeded`, start/stop/restart operations, and per-space GC accessors.

Control flow: constructor and start tests create one-space and two-space configurations, start workers, and assert expected GC creation/running state. Stop and restart tests verify lifecycle transitions for one and two spaces.

State and persistence: state is in-memory orchestration of per-space GC instances and worker running flags. Tests may start worker threads but use dummy MGM behavior rather than real namespace/tape state.

Dependencies and integration: integrates `SpaceToTapeGcMap`-style space management with actual TGC lifecycle controls.

Risks and test signals: lifecycle tests are important because repeated start/stop can create duplicate workers or stale GC state. The tests focus on orchestration, not detailed file garbage-collection behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/tgc/MultiSpaceTapeGcTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/tgc/SmartSpaceStatsTests.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/tgc/SmartSpaceStatsTests.cc

Purpose: tests `SmartSpaceStats`, the TGC helper that obtains free-byte information for spaces, optionally through a configured script.

Important APIs and types: `SmartSpaceStats`, `DummyTapeGcMgm`, constructor/config methods, and `get`-style free-byte retrieval.

Control flow: constructor test verifies initial state. The no-script test obtains stats through default/dummy MGM behavior. The script-configured test sets a free-bytes script and verifies values are returned through that path.

State and persistence: state is in-memory configuration plus any dummy MGM counters. It does not persist results; it computes or fetches them per call.

Dependencies and integration: bridges TGC decision logic with MGM space statistics and optional external script configuration.

Risks and test signals: external-script execution is a production risk, but tests use controlled dummy behavior. Coverage should be supplemented by integration tests for script failures and parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/tgc/SmartSpaceStatsTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/tgc/SpaceToTapeGcMapTests.cc -->
## sources/distributed-fs/eos/unit_tests/mgm/tgc/SpaceToTapeGcMapTests.cc

Purpose: tests `SpaceToTapeGcMap`, the map from EOS space names to per-space tape garbage collector instances.

Important APIs and types: `SpaceToTapeGcMap`, `DummyTapeGcMgm`, `getGc`, `createGc`, `destroyAllGc`, `toJson`, and `MaxLenExceeded`.

Control flow: constructor test checks initial empty state. Unknown-space lookup returns no GC. `createGc` creates a GC for a space, duplicate creation is rejected or handled as already exists, and `createAndDestroyAllGc` verifies cleanup. JSON tests check serialized map state and max-length exception behavior.

State and persistence: in-memory map of space names to GC objects. `destroyAllGc` clears managed instances; no external persistence.

Dependencies and integration: used by multi-space TGC management to create, retrieve, report, and destroy per-space collectors.

Risks and test signals: ownership and duplicate handling are the main risks. JSON max-length behavior protects status APIs from excessive output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/tgc/SpaceToTapeGcMapTests.cc -->
