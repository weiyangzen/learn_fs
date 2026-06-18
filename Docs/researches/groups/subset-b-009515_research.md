# subset-b-009515 Research

Grouped research report. Each section preserves the original source path for reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/api/api.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/api/api.go

## Purpose
Shared wire-contract schema for syz-cluster workflow steps, controller APIs, reporter APIs, and service conversions.

## Important APIs, Types, and Functions
Defines TriageResult, TestTarget, RetestTask, FuzzConfig, Tree, KernelFuzzConfig, BuildRequest/BuildResult/Build, SessionTest, SessionTestStep, RawFinding, Series/Patch, SessionReport, Finding, Job, SessionInfo, and string constants for focus areas, statuses, report types, and job types.

## Control Flow
No main algorithm; methods are schema helpers such as Series.PatchBodies. Control flow is driven by downstream clients/services that serialize these structs.

## State and Persistence
No direct persistence, but JSON/YAML tags and byte fields are the cross-process and Spanner/blob handoff contract.

## Dependencies and Integration Points
Depends on Go net/http/json helpers and is integrated by controller/reporter servers plus workflow clients.

## Risks and Edge Cases
Risks include wire-contract drift, weak validation of string statuses, memory buffering for large payloads, and coarse HTTP error mapping.

## Test Signals
Covered indirectly by controller, reporter, retest, fuzzconfig, and report integration tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/api/api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/api/client.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/api/client.go

## Purpose
Controller-facing HTTP client used by workflow steps and tests.

## Important APIs, Types, and Functions
NewClient plus methods for series/session/job retrieval, tree config, build/test/finding/base-finding uploads, artifact upload, previous finding lookup, test-step upload, and job submission.

## Control Flow
Methods format REST paths and call generic JSON or multipart helpers. finishRequest uses a one-minute http.Client, enforces HTTP 200, and decodes JSON.

## State and Persistence
Stateless except baseURL; persistence occurs behind controller services.

## Dependencies and Integration Points
Depends on Go net/http/json helpers and is integrated by controller/reporter servers plus workflow clients.

## Risks and Edge Cases
Risks include wire-contract drift, weak validation of string statuses, memory buffering for large payloads, and coarse HTTP error mapping.

## Test Signals
Covered indirectly by controller, reporter, retest, fuzzconfig, and report integration tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/api/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/api/http.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/api/http.go

## Purpose
Generic JSON and multipart HTTP helpers shared by clients and servers.

## Important APIs, Types, and Functions
getJSON, postJSON, postMultiPartFile, ReplyJSON, and ParseJSON.

## Control Flow
Client helpers build context-aware HTTP requests; server helpers enforce POST for ParseJSON and encode typed JSON responses.

## State and Persistence
No durable state; buffers JSON and multipart bodies in memory.

## Dependencies and Integration Points
Depends on Go net/http/json helpers and is integrated by controller/reporter servers plus workflow clients.

## Risks and Edge Cases
Risks include wire-contract drift, weak validation of string statuses, memory buffering for large payloads, and coarse HTTP error mapping.

## Test Signals
Covered indirectly by controller, reporter, retest, fuzzconfig, and report integration tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/api/http.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/api/reporter.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/api/reporter.go

## Purpose
Reporter-service client and reply/report request contracts.

## Important APIs, Types, and Functions
ReporterClient, NextReportResp, UpstreamReportReq, RecordReplyReq/Resp, LKMLReporter, GetNextReport, ConfirmReport, UpstreamReport, InvalidateReport, RecordReply.

## Control Flow
Builds /reports routes and delegates to postJSON; reply recording maps email message IDs to report IDs.

## State and Persistence
Stateless client; server mutates report, finding, and reply records.

## Dependencies and Integration Points
Depends on Go net/http/json helpers and is integrated by controller/reporter servers plus workflow clients.

## Risks and Edge Cases
Risks include wire-contract drift, weak validation of string statuses, memory buffering for large payloads, and coarse HTTP error mapping.

## Test Signals
Covered indirectly by controller, reporter, retest, fuzzconfig, and report integration tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/api/reporter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/api/urls.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/api/urls.go

## Purpose
Dashboard URL construction helper.

## Important APIs, Types, and Functions
URLGenerator and methods for finding log/repro links, series/session pages, build config/log links, and job patch links.

## Control Flow
Each method formats baseURL plus a fixed route template.

## State and Persistence
No persistence; generated links are embedded into API responses and emails.

## Dependencies and Integration Points
Depends on Go net/http/json helpers and is integrated by controller/reporter servers plus workflow clients.

## Risks and Edge Cases
Risks include wire-contract drift, weak validation of string statuses, memory buffering for large payloads, and coarse HTTP error mapping.

## Test Signals
Covered indirectly by controller, reporter, retest, fuzzconfig, and report integration tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/api/urls.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/app/config.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/app/config.go

## Purpose
Application YAML config loader and validator.

## Important APIs, Types, and Functions
AppConfig, EmailConfig, SMTPConfig, DashapiConfig, Config, loadConfig, Validate methods, sender constants, and validation helpers.

## Control Flow
Config uses sync.Once to load /config/config.yaml, apply defaults, unmarshal YAML, and validate URL/email/sender shape.

## State and Persistence
Process-wide cached configuration; no database persistence.

## Dependencies and Integration Points
Integrates configuration, environment variables, Spanner, blob storage, URL generation, and test harness setup.

## Risks and Edge Cases
Risks include hard-coded paths/service URLs, cached config reload limitations, and operational env var mistakes.

## Test Signals
Covered by config overlay tests and broad app.TestEnvironment integration tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/app/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/app/config_test.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/app/config_test.go

## Purpose
Deployment overlay config validation test.

## Important APIs, Types, and Functions
TestConfigs walks syz-cluster/overlays and loads every global-config.yaml.

## Control Flow
Discovers files from the pkg/app working directory and subtests each config.

## State and Persistence
Reads checked-in config files only.

## Dependencies and Integration Points
Integrates configuration, environment variables, Spanner, blob storage, URL generation, and test harness setup.

## Risks and Edge Cases
Risks include hard-coded paths/service URLs, cached config reload limitations, and operational env var mistakes.

## Test Signals
Covered by config overlay tests and broad app.TestEnvironment integration tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/app/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/app/env.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/app/env.go

## Purpose
Dependency injection setup for production and tests.

## Important APIs, Types, and Functions
AppEnvironment, Environment, TestEnvironment, DefaultSpannerURI, DefaultSpanner, DefaultStorage, DefaultClient, DefaultReporterClient.

## Control Flow
Production setup reads env/config and constructs Spanner/GCS/URL dependencies; tests create transient Spanner DB and local blob storage.

## State and Persistence
Holds shared clients/config; durable state lives in Spanner and blob storage.

## Dependencies and Integration Points
Integrates configuration, environment variables, Spanner, blob storage, URL generation, and test harness setup.

## Risks and Edge Cases
Risks include hard-coded paths/service URLs, cached config reload limitations, and operational env var mistakes.

## Test Signals
Covered by config overlay tests and broad app.TestEnvironment integration tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/app/env.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/app/logging.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/app/logging.go

## Purpose
Minimal application logging wrappers.

## Important APIs, Types, and Functions
Errorf and Fatalf.

## Control Flow
Delegates to standard log.Printf/log.Fatalf.

## State and Persistence
No durable state.

## Dependencies and Integration Points
Integrates configuration, environment variables, Spanner, blob storage, URL generation, and test harness setup.

## Risks and Edge Cases
Risks include hard-coded paths/service URLs, cached config reload limitations, and operational env var mistakes.

## Test Signals
Covered by config overlay tests and broad app.TestEnvironment integration tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/app/logging.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/blob/gcs.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/blob/gcs.go

## Purpose
GCS-backed blob.Storage implementation.

## Important APIs, Types, and Functions
NewGCSClient, gcsDriver.Write, gcsDriver.Read, parseURI.

## Control Flow
Write copies a reader into gcs.Client.FileWriter under bucket/path parts; Read validates gcs://bucket/object URIs.

## State and Persistence
Persists blobs outside Spanner; services store returned URIs.

## Dependencies and Integration Points
Integrated by app environment and services that offload logs, configs, patches, reports, and reproducers.

## Risks and Edge Cases
Risks include orphaned blobs after DB failures, URI validation gaps, upload close errors, and in-memory/local overwrite behavior.

## Test Signals
Covered by LocalStorage unit tests and higher-level service/controller tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/blob/gcs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/blob/storage.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/blob/storage.go

## Purpose
Blob storage interface and local test implementation.

## Important APIs, Types, and Functions
Storage, LocalStorage, NewLocalStorage, Write, Read, ReadAllBytes.

## Control Flow
Local Write base64-encodes joined parts and writes a file; Read validates local:// and opens it.

## State and Persistence
Local filesystem persistence for tests; production uses other Storage implementations.

## Dependencies and Integration Points
Integrated by app environment and services that offload logs, configs, patches, reports, and reproducers.

## Risks and Edge Cases
Risks include orphaned blobs after DB failures, URI validation gaps, upload close errors, and in-memory/local overwrite behavior.

## Test Signals
Covered by LocalStorage unit tests and higher-level service/controller tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/blob/storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/blob/storage_test.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/blob/storage_test.go

## Purpose
LocalStorage contract test.

## Important APIs, Types, and Functions
TestLocalStorage.

## Control Flow
Writes two objects, reads them back, and checks bad URI/error cases.

## State and Persistence
Uses t.TempDir only.

## Dependencies and Integration Points
Integrated by app environment and services that offload logs, configs, patches, reports, and reproducers.

## Risks and Edge Cases
Risks include orphaned blobs after DB failures, URI validation gaps, upload close errors, and in-memory/local overwrite behavior.

## Test Signals
Covered by LocalStorage unit tests and higher-level service/controller tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/blob/storage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/controller/api.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/controller/api.go

## Purpose
Main controller HTTP server implementing api.Client routes.

## Important APIs, Types, and Functions
APIServer, NewAPIServer, Mux, and handlers for builds, findings, series, sessions, tests, artifacts, trees, base findings, test steps, and jobs.

## Control Flow
Handlers parse JSON/multipart requests, call service layer methods, map known errors to HTTP statuses, and ReplyJSON responses.

## State and Persistence
Server is stateless; services mutate Spanner rows and blob objects.

## Dependencies and Integration Points
Integrates api contracts, app environment, service layer, httptest clients, Spanner repositories, and blob storage.

## Risks and Edge Cases
Risks include incomplete request validation, inconsistent method enforcement, and broad 500 mappings for domain errors.

## Test Signals
controller/api_test.go provides full API integration coverage.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/controller/api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/controller/api_test.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/controller/api_test.go

## Purpose
End-to-end controller API integration tests.

## Important APIs, Types, and Functions
Tests cover series/build/finding/artifact/base-finding/previous-finding/test-step/tree/job/session-info flows.

## Control Flow
Uses app.TestEnvironment, httptest controller, public api.Client calls, and direct db checks where needed.

## State and Persistence
Exercises transient Spanner plus local blob storage across most core entities.

## Dependencies and Integration Points
Integrates api contracts, app environment, service layer, httptest clients, Spanner repositories, and blob storage.

## Risks and Edge Cases
Risks include incomplete request validation, inconsistent method enforcement, and broad 500 mappings for domain errors.

## Test Signals
controller/api_test.go provides full API integration coverage.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/controller/api_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/controller/testutil.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/controller/testutil.go

## Purpose
Shared controller/reporter/retest test helpers.

## Important APIs, Types, and Functions
UploadTestSeries, UploadTestBuild, TestServer, DummySeries, DummyBuild, DummyFindings, FakeSeriesWithFindings, StartSession, MarkSessionFinished, UploadTestSessionReport, FakeJobSession.

## Control Flow
Composes public API calls and direct repository mutations for setup shortcuts.

## State and Persistence
Creates transient Spanner records and httptest servers.

## Dependencies and Integration Points
Integrates api contracts, app environment, service layer, httptest clients, Spanner repositories, and blob storage.

## Risks and Edge Cases
Risks include incomplete request validation, inconsistent method enforcement, and broad 500 mappings for domain errors.

## Test Signals
controller/api_test.go provides full API integration coverage.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/controller/testutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/base_finding_repo.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/base_finding_repo.go

## Purpose
Repository for BaseFindings with exact/date-window existence checks.

## Important APIs, Types, and Functions
BaseFindingRepository, Save, Exists.

## Control Flow
Save upserts; Exists searches by config/arch/title and commit hash or seven-day commit-date span.

## State and Persistence
Persists BaseFindings in Spanner.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/base_finding_repo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/base_finding_repo_test.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/base_finding_repo_test.go

## Purpose
Tests BaseFindingRepository matching semantics.

## Important APIs, Types, and Functions
TestBaseFindingRepository.

## Control Flow
Checks unknown title, exact match, close-date match, future-date rejection, and far-past rejection.

## State and Persistence
Uses transient Spanner.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/base_finding_repo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/build_repo.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/build_repo.go

## Purpose
Repository for Build rows and latest matching build lookup.

## Important APIs, Types, and Functions
BuildRepository, Insert, LastBuildParams, LastBuiltTree.

## Control Flow
Insert assigns UUID if missing; LastBuiltTree builds optional filters and orders by CommitDate DESC LIMIT 1.

## State and Persistence
Persists Builds in Spanner.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/build_repo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/build_repo_test.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/build_repo_test.go

## Purpose
Tests latest successful build lookup.

## Important APIs, Types, and Functions
TestLastSuccessfulBuild.

## Control Flow
Verifies nil result, status filtering, successful build selection, and mismatched filters.

## State and Persistence
Uses transient Spanner.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/build_repo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/entities.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/entities.go

## Purpose
Spanner entity definitions and small domain helpers.

## Important APIs, Types, and Functions
Series, Patch, Build, Session, SessionTest, SessionTestStep, Finding, SessionReport, ReportReply, BaseFinding, SeriesStats, Job and status/helper methods.

## Control Flow
Methods set nullable fields and derive session status/duration; repositories serialize these structs.

## State and Persistence
Defines the persisted schema-facing model.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/entities.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/finding_repo.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/finding_repo.go

## Purpose
Repository for logical finding replacement and listing.

## Important APIs, Types, and Functions
FindingRepository, FindingID, Store, mustStore, ListForSession.

## Control Flow
Store loads old finding/session in a transaction, calls callback, deletes old row, and inserts replacement.

## State and Persistence
Persists Findings with blob URI fields.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/finding_repo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/finding_repo_test.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/finding_repo_test.go

## Purpose
Tests finding insertion uniqueness and list ordering.

## Important APIs, Types, and Functions
TestFindingRepo.

## Control Flow
Creates tests/findings, asserts duplicate errors through mustStore, and verifies ordered list output.

## State and Persistence
Uses transient Spanner.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/finding_repo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/job_repo.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/job_repo.go

## Purpose
Repository for Jobs with ExtID duplicate prevention.

## Important APIs, Types, and Functions
JobRepository, Insert, ErrJobExists.

## Control Flow
Transactionally checks Jobs by ExtID, runs callback once, then inserts.

## State and Persistence
Persists Jobs; callback may set PatchURI.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/job_repo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/job_repo_test.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/job_repo_test.go

## Purpose
Tests JobRepository duplicate ExtID behavior.

## Important APIs, Types, and Functions
TestJobRepo.

## Control Flow
Inserts one job and expects ErrJobExists for same ExtID.

## State and Persistence
Uses transient Spanner plus prerequisite report/session.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/job_repo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/report_reply_repo.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/report_reply_repo.go

## Purpose
Repository for report reply records and parent lookup.

## Important APIs, Types, and Functions
ReportReplyRepository, FindParentReportID, Insert, ErrReportReplyExists.

## Control Flow
FindParentReportID joins replies to reports by reporter; Insert rejects duplicate report/message pairs.

## State and Persistence
Persists ReportReplies.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/report_reply_repo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/report_reply_repo_test.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/report_reply_repo_test.go

## Purpose
Tests report reply insert/duplicate/lookup behavior.

## Important APIs, Types, and Functions
TestReportReplyRepository.

## Control Flow
Creates a report, inserts replies, checks duplicate rejection, and verifies parent lookup.

## State and Persistence
Uses transient Spanner.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/report_reply_repo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/report_repo.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/report_repo.go

## Purpose
Repository for SessionReports and unsent report selection.

## Important APIs, Types, and Functions
ReportRepository, Insert, ListNotReported, randomReportID.

## Control Flow
Insert uses caller ID or random short hex IDs; ListNotReported filters ReportedAt IS NULL by reporter.

## State and Persistence
Persists SessionReports.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/report_repo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/report_repo_test.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/report_repo_test.go

## Purpose
Tests report repository and missing-report queue behavior.

## Important APIs, Types, and Functions
TestReportRepository and TestSessionsWithoutReports.

## Control Flow
Checks unsent counts and finished sessions with findings/no report selection.

## State and Persistence
Uses transient Spanner across reports/sessions/findings.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/report_repo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/series_repo.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/series_repo.go

## Purpose
Repository for series, patches, dashboard filters, search, and version history.

## Important APIs, Types, and Functions
SeriesRepository, Insert, GetByExtID, ListLatest, ListPreviousVersions, ListPatches, Count, PatchByID.

## Control Flow
Insert rejects duplicate ExtID and stores patches; ListLatest builds filters then enriches with latest sessions and finding counts.

## State and Persistence
Persists Series/Patches and reads Sessions/Findings/Stats.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/series_repo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/series_repo_test.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/series_repo_test.go

## Purpose
Broad tests for series repository behavior.

## Important APIs, Types, and Functions
Tests get/list/search/update/previous versions.

## Control Flow
Exercises ordering, cc/status/finding filters, SEARCH queries, invalidated findings, and updates.

## State and Persistence
Uses transient Spanner.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/series_repo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/series_stats_repo.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/series_stats_repo.go

## Purpose
Repository for series statistics refresh selection and bulk update.

## Important APIs, Types, and Functions
SeriesStatsRepository, ListOutdated, BulkUpdate, ListOutdatedFilter.

## Control Flow
Lists finished latest-session series missing/current-version stats; bulk updates existing stats rows.

## State and Persistence
Persists SeriesStats.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/series_stats_repo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/series_stats_repo_test.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/series_stats_repo_test.go

## Purpose
Tests outdated stats selection.

## Important APIs, Types, and Functions
TestSeriesStatsOutdated.

## Control Flow
Creates finished and unfinished latest sessions and expects only finished series.

## State and Persistence
Uses transient Spanner.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/series_stats_repo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/session_repo.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/session_repo.go

## Purpose
Repository for sessions, lifecycle start, scheduling queues, and report-generation queue.

## Important APIs, Types, and Functions
SessionRepository, Start, Insert, ListRunning, ListWaiting, ListForSeries, MissingReportList.

## Control Flow
Start sets StartedAt and updates Series.LatestSessionID for non-job sessions; ListWaiting prioritizes job sessions.

## State and Persistence
Persists Sessions and mutates Series latest-session pointer.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/session_repo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/session_repo_test.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/session_repo_test.go

## Purpose
Tests session lifecycle and queue behavior.

## Important APIs, Types, and Functions
Tests latest-session update, FIFO waiting order, job priority, and job sessions not updating latest session.

## Control Flow
Creates series/sessions/jobs/reports and calls repository methods.

## State and Persistence
Uses transient Spanner.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/session_repo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/session_test_repo.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/session_test_repo.go

## Purpose
Repository for SessionTests and build enrichment.

## Important APIs, Types, and Functions
SessionTestRepository, InsertOrUpdate, Get, BySession, BySessionRaw, FullSessionTest.

## Control Flow
Upserts tests by session/name; BySession loads referenced base/patched builds and attaches pointers.

## State and Persistence
Persists SessionTests and reads Builds.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/session_test_repo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/session_test_repo_test.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/session_test_repo_test.go

## Purpose
Tests SessionTestRepository build enrichment.

## Important APIs, Types, and Functions
TestSessionTestRepository.

## Control Flow
Creates builds and tests, then verifies BySession returns build pointers.

## State and Persistence
Uses transient Spanner.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/session_test_repo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/spanner.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/spanner.go

## Purpose
Spanner setup, migration, test-emulator, query, and generic repository helpers.

## Important APIs, Types, and Functions
ParseURI, CreateSpannerInstance, CreateSpannerDB, RunMigrations, NewTransientDB, NewTestDB, readEntity/readEntities, addLimit, genericEntityOps.

## Control Flow
Production runs embedded migrations; tests start emulator and isolated DBs; generic ops wrap insert/update/upsert/get.

## State and Persistence
Manages Spanner DBs and helper access to persisted rows.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/spanner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/spanner_test.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/spanner_test.go

## Purpose
Migration reversibility smoke test.

## Important APIs, Types, and Functions
TestMigrations.

## Control Flow
Runs all migrations down and back up on a transient DB.

## State and Persistence
Uses transient Spanner.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/spanner_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/stats_repo.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/stats_repo.go

## Purpose
Dashboard/statistics aggregate query repository.

## Important APIs, Types, and Functions
StatsRepository and weekly/monthly count/status/delay/prevented-bug/job query methods.

## Control Flow
Runs Spanner SQL aggregations and post-computes finished status counts.

## State and Persistence
Read-only aggregate queries over Spanner.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/stats_repo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/stats_repo_test.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/stats_repo_test.go

## Purpose
Smoke tests stats SQL queries.

## Important APIs, Types, and Functions
TestStatsSQLs.

## Control Flow
Calls every stats query over empty/started/finding/finished states.

## State and Persistence
Uses transient Spanner.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/stats_repo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/test_step_repo.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/test_step_repo.go

## Purpose
Repository for SessionTestSteps and base/patched grouping.

## Important APIs, Types, and Functions
SessionTestStepRepository, Store, ListForSession, GroupTestSteps, TestStepGroup.

## Control Flow
Store replaces a logical step by deleting old row and inserting new row; grouping aligns base/patched by title.

## State and Persistence
Persists SessionTestSteps.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/test_step_repo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/test_step_repo_test.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/test_step_repo_test.go

## Purpose
Tests test-step storage and listing.

## Important APIs, Types, and Functions
TestSessionTestStepRepository.

## Control Flow
Stores patched/base steps linked to findings and checks list contents.

## State and Persistence
Uses transient Spanner.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/test_step_repo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/util_test.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/db/util_test.go

## Purpose
Shared db test fixture helpers.

## Important APIs, Types, and Functions
dummyTestData and helpers for series/session/test/report/finding lifecycle.

## Control Flow
Directly creates and mutates repository rows while asserting success.

## State and Persistence
Creates transient Spanner fixture state.

## Dependencies and Integration Points
Depends on Cloud Spanner, db entity structs, and shared helpers in spanner.go; service/controller layers consume these repositories.

## Risks and Edge Cases
Risks center on schema drift, transactional callback side effects, nullable field handling, and query semantics changing dashboard/workflow behavior.

## Test Signals
Repository tests use NewTransientDB and Spanner emulator to validate SQL and persistence behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/db/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/emailclient/sender.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/emailclient/sender.go

## Purpose
Email sender factory for SMTP and dashapi backends.

## Important APIs, Types, and Functions
Sender type, MakeSender, newSMTPSender, SMTP secret constants, queryCredentials, querySecret, TestEmailConfig.

## Control Flow
Switches on app.EmailConfig.Sender; SMTP reads GCP secrets and dashapi builds sender config directly.

## State and Persistence
Reads external secrets and sends through external services; no app DB writes.

## Dependencies and Integration Points
Integrates app.EmailConfig, syzkaller email sender backends, GCP project/secret lookup, and SMTP/dashapi services.

## Risks and Edge Cases
Risks include secret lookup retries without backoff, runtime GCP dependency, and assuming config was validated earlier.

## Test Signals
No direct unit test here; app config validation and email/report tests cover adjacent behavior.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/emailclient/sender.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/base.cfg -->
# sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/base.cfg

## Purpose
Base syz-manager template embedded by GenerateBase.

## Important APIs, Types, and Functions
Static JSON fields for base kernel object/image/workdir/syzkaller/qemu VM/procs/sandbox/experimental cover settings.

## Control Flow
Embedded or loaded through syzkaller config parsers and merged/generated by fuzzconfig code.

## State and Persistence
No runtime persistence; controls syz-manager VM and syscall behavior.

## Dependencies and Integration Points
Depends on syzkaller pkg/config and pkg/mgrconfig, embedded templates, and api focus constants.

## Risks and Edge Cases
Risks include stale syscall allowlists, upstream mgrconfig default changes, and careless golden fixture rewrites.

## Test Signals
generate_test.go golden-tests singular, mixed, and no-focus outputs.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/base.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/generate.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/generate.go

## Purpose
Generates syz-manager configs from embedded base/patched templates and api.FuzzConfig focus choices.

## Important APIs, Types, and Functions
GenerateBase, GeneratePatched, applyFuzzConfig, setFocus map, noFlakyFsCalls, noFlakyTraceCalls.

## Control Flow
Loads embedded JSON, merges patched delta when needed, parses mgrconfig partial data, and appends focus-specific syscall/VM adjustments.

## State and Persistence
No persistence; returns in-memory mgrconfig.Config for workflow fuzzing.

## Dependencies and Integration Points
Depends on syzkaller pkg/config and pkg/mgrconfig, embedded templates, and api focus constants.

## Risks and Edge Cases
Risks include stale syscall allowlists, upstream mgrconfig default changes, and careless golden fixture rewrites.

## Test Signals
generate_test.go golden-tests singular, mixed, and no-focus outputs.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/generate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/generate_test.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/generate_test.go

## Purpose
Golden tests for fuzzconfig generation.

## Important APIs, Types, and Functions
TestSingularFocus, TestNoFocus, TestMultipleFocus, runTest, compareOrSave, -write flag.

## Control Flow
Generates base/patched configs and compares normalized JSON against testdata fixtures.

## State and Persistence
Reads fixtures; optional -write rewrites them.

## Dependencies and Integration Points
Depends on syzkaller pkg/config and pkg/mgrconfig, embedded templates, and api focus constants.

## Risks and Edge Cases
Risks include stale syscall allowlists, upstream mgrconfig default changes, and careless golden fixture rewrites.

## Test Signals
generate_test.go golden-tests singular, mixed, and no-focus outputs.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/generate_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/patched.cfg -->
# sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/patched.cfg

## Purpose
Patched syz-manager delta template merged over base config.

## Important APIs, Types, and Functions
Static JSON overrides for patched name, kernel object/image/kernel path, fuzzing_vms, and larger VM count.

## Control Flow
Embedded or loaded through syzkaller config parsers and merged/generated by fuzzconfig code.

## State and Persistence
No runtime persistence; controls syz-manager VM and syscall behavior.

## Dependencies and Integration Points
Depends on syzkaller pkg/config and pkg/mgrconfig, embedded templates, and api focus constants.

## Risks and Edge Cases
Risks include stale syscall allowlists, upstream mgrconfig default changes, and careless golden fixture rewrites.

## Test Signals
generate_test.go golden-tests singular, mixed, and no-focus outputs.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/patched.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/mixed/bpf_io_uring.base.cfg -->
# sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/mixed/bpf_io_uring.base.cfg

## Purpose
Golden base syz-manager fixture for focus set bpf_io_uring.

## Important APIs, Types, and Functions
Canonical normalized JSON output including enabled/disabled/no-mutate syscalls, VM settings, and Experimental defaults.

## Control Flow
generate_test.go compares generated configs to this fixture after parsing and marshaling.

## State and Persistence
Checked-in test fixture; no runtime persistence.

## Dependencies and Integration Points
Depends on syzkaller pkg/config and pkg/mgrconfig, embedded templates, and api focus constants.

## Risks and Edge Cases
Risks include stale syscall allowlists, upstream mgrconfig default changes, and careless golden fixture rewrites.

## Test Signals
generate_test.go golden-tests singular, mixed, and no-focus outputs.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/mixed/bpf_io_uring.base.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/mixed/bpf_io_uring.patched.cfg -->
# sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/mixed/bpf_io_uring.patched.cfg

## Purpose
Golden patched syz-manager fixture for focus set bpf_io_uring.

## Important APIs, Types, and Functions
Canonical normalized JSON output including enabled/disabled/no-mutate syscalls, VM settings, and Experimental defaults.

## Control Flow
generate_test.go compares generated configs to this fixture after parsing and marshaling.

## State and Persistence
Checked-in test fixture; no runtime persistence.

## Dependencies and Integration Points
Depends on syzkaller pkg/config and pkg/mgrconfig, embedded templates, and api focus constants.

## Risks and Edge Cases
Risks include stale syscall allowlists, upstream mgrconfig default changes, and careless golden fixture rewrites.

## Test Signals
generate_test.go golden-tests singular, mixed, and no-focus outputs.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/mixed/bpf_io_uring.patched.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/bpf.base.cfg -->
# sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/bpf.base.cfg

## Purpose
Golden base syz-manager fixture for focus set bpf.

## Important APIs, Types, and Functions
Canonical normalized JSON output including enabled/disabled/no-mutate syscalls, VM settings, and Experimental defaults.

## Control Flow
generate_test.go compares generated configs to this fixture after parsing and marshaling.

## State and Persistence
Checked-in test fixture; no runtime persistence.

## Dependencies and Integration Points
Depends on syzkaller pkg/config and pkg/mgrconfig, embedded templates, and api focus constants.

## Risks and Edge Cases
Risks include stale syscall allowlists, upstream mgrconfig default changes, and careless golden fixture rewrites.

## Test Signals
generate_test.go golden-tests singular, mixed, and no-focus outputs.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/bpf.base.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/bpf.patched.cfg -->
# sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/bpf.patched.cfg

## Purpose
Golden patched syz-manager fixture for focus set bpf.

## Important APIs, Types, and Functions
Canonical normalized JSON output including enabled/disabled/no-mutate syscalls, VM settings, and Experimental defaults.

## Control Flow
generate_test.go compares generated configs to this fixture after parsing and marshaling.

## State and Persistence
Checked-in test fixture; no runtime persistence.

## Dependencies and Integration Points
Depends on syzkaller pkg/config and pkg/mgrconfig, embedded templates, and api focus constants.

## Risks and Edge Cases
Risks include stale syscall allowlists, upstream mgrconfig default changes, and careless golden fixture rewrites.

## Test Signals
generate_test.go golden-tests singular, mixed, and no-focus outputs.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/bpf.patched.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/default.base.cfg -->
# sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/default.base.cfg

## Purpose
Golden base syz-manager fixture for focus set default.

## Important APIs, Types, and Functions
Canonical normalized JSON output including enabled/disabled/no-mutate syscalls, VM settings, and Experimental defaults.

## Control Flow
generate_test.go compares generated configs to this fixture after parsing and marshaling.

## State and Persistence
Checked-in test fixture; no runtime persistence.

## Dependencies and Integration Points
Depends on syzkaller pkg/config and pkg/mgrconfig, embedded templates, and api focus constants.

## Risks and Edge Cases
Risks include stale syscall allowlists, upstream mgrconfig default changes, and careless golden fixture rewrites.

## Test Signals
generate_test.go golden-tests singular, mixed, and no-focus outputs.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/default.base.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/default.patched.cfg -->
# sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/default.patched.cfg

## Purpose
Golden patched syz-manager fixture for focus set default.

## Important APIs, Types, and Functions
Canonical normalized JSON output including enabled/disabled/no-mutate syscalls, VM settings, and Experimental defaults.

## Control Flow
generate_test.go compares generated configs to this fixture after parsing and marshaling.

## State and Persistence
Checked-in test fixture; no runtime persistence.

## Dependencies and Integration Points
Depends on syzkaller pkg/config and pkg/mgrconfig, embedded templates, and api focus constants.

## Risks and Edge Cases
Risks include stale syscall allowlists, upstream mgrconfig default changes, and careless golden fixture rewrites.

## Test Signals
generate_test.go golden-tests singular, mixed, and no-focus outputs.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/default.patched.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/fs.base.cfg -->
# sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/fs.base.cfg

## Purpose
Golden base syz-manager fixture for focus set fs.

## Important APIs, Types, and Functions
Canonical normalized JSON output including enabled/disabled/no-mutate syscalls, VM settings, and Experimental defaults.

## Control Flow
generate_test.go compares generated configs to this fixture after parsing and marshaling.

## State and Persistence
Checked-in test fixture; no runtime persistence.

## Dependencies and Integration Points
Depends on syzkaller pkg/config and pkg/mgrconfig, embedded templates, and api focus constants.

## Risks and Edge Cases
Risks include stale syscall allowlists, upstream mgrconfig default changes, and careless golden fixture rewrites.

## Test Signals
generate_test.go golden-tests singular, mixed, and no-focus outputs.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/fs.base.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/fs.patched.cfg -->
# sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/fs.patched.cfg

## Purpose
Golden patched syz-manager fixture for focus set fs.

## Important APIs, Types, and Functions
Canonical normalized JSON output including enabled/disabled/no-mutate syscalls, VM settings, and Experimental defaults.

## Control Flow
generate_test.go compares generated configs to this fixture after parsing and marshaling.

## State and Persistence
Checked-in test fixture; no runtime persistence.

## Dependencies and Integration Points
Depends on syzkaller pkg/config and pkg/mgrconfig, embedded templates, and api focus constants.

## Risks and Edge Cases
Risks include stale syscall allowlists, upstream mgrconfig default changes, and careless golden fixture rewrites.

## Test Signals
generate_test.go golden-tests singular, mixed, and no-focus outputs.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/fs.patched.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/io_uring.base.cfg -->
# sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/io_uring.base.cfg

## Purpose
Golden base syz-manager fixture for focus set io_uring.

## Important APIs, Types, and Functions
Canonical normalized JSON output including enabled/disabled/no-mutate syscalls, VM settings, and Experimental defaults.

## Control Flow
generate_test.go compares generated configs to this fixture after parsing and marshaling.

## State and Persistence
Checked-in test fixture; no runtime persistence.

## Dependencies and Integration Points
Depends on syzkaller pkg/config and pkg/mgrconfig, embedded templates, and api focus constants.

## Risks and Edge Cases
Risks include stale syscall allowlists, upstream mgrconfig default changes, and careless golden fixture rewrites.

## Test Signals
generate_test.go golden-tests singular, mixed, and no-focus outputs.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/io_uring.base.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/io_uring.patched.cfg -->
# sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/io_uring.patched.cfg

## Purpose
Golden patched syz-manager fixture for focus set io_uring.

## Important APIs, Types, and Functions
Canonical normalized JSON output including enabled/disabled/no-mutate syscalls, VM settings, and Experimental defaults.

## Control Flow
generate_test.go compares generated configs to this fixture after parsing and marshaling.

## State and Persistence
Checked-in test fixture; no runtime persistence.

## Dependencies and Integration Points
Depends on syzkaller pkg/config and pkg/mgrconfig, embedded templates, and api focus constants.

## Risks and Edge Cases
Risks include stale syscall allowlists, upstream mgrconfig default changes, and careless golden fixture rewrites.

## Test Signals
generate_test.go golden-tests singular, mixed, and no-focus outputs.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/io_uring.patched.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/kvm.base.cfg -->
# sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/kvm.base.cfg

## Purpose
Golden base syz-manager fixture for focus set kvm.

## Important APIs, Types, and Functions
Canonical normalized JSON output including enabled/disabled/no-mutate syscalls, VM settings, and Experimental defaults.

## Control Flow
generate_test.go compares generated configs to this fixture after parsing and marshaling.

## State and Persistence
Checked-in test fixture; no runtime persistence.

## Dependencies and Integration Points
Depends on syzkaller pkg/config and pkg/mgrconfig, embedded templates, and api focus constants.

## Risks and Edge Cases
Risks include stale syscall allowlists, upstream mgrconfig default changes, and careless golden fixture rewrites.

## Test Signals
generate_test.go golden-tests singular, mixed, and no-focus outputs.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/kvm.base.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/kvm.patched.cfg -->
# sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/kvm.patched.cfg

## Purpose
Golden patched syz-manager fixture for focus set kvm.

## Important APIs, Types, and Functions
Canonical normalized JSON output including enabled/disabled/no-mutate syscalls, VM settings, and Experimental defaults.

## Control Flow
generate_test.go compares generated configs to this fixture after parsing and marshaling.

## State and Persistence
Checked-in test fixture; no runtime persistence.

## Dependencies and Integration Points
Depends on syzkaller pkg/config and pkg/mgrconfig, embedded templates, and api focus constants.

## Risks and Edge Cases
Risks include stale syscall allowlists, upstream mgrconfig default changes, and careless golden fixture rewrites.

## Test Signals
generate_test.go golden-tests singular, mixed, and no-focus outputs.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/kvm.patched.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/net.base.cfg -->
# sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/net.base.cfg

## Purpose
Golden base syz-manager fixture for focus set net.

## Important APIs, Types, and Functions
Canonical normalized JSON output including enabled/disabled/no-mutate syscalls, VM settings, and Experimental defaults.

## Control Flow
generate_test.go compares generated configs to this fixture after parsing and marshaling.

## State and Persistence
Checked-in test fixture; no runtime persistence.

## Dependencies and Integration Points
Depends on syzkaller pkg/config and pkg/mgrconfig, embedded templates, and api focus constants.

## Risks and Edge Cases
Risks include stale syscall allowlists, upstream mgrconfig default changes, and careless golden fixture rewrites.

## Test Signals
generate_test.go golden-tests singular, mixed, and no-focus outputs.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/net.base.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/net.patched.cfg -->
# sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/net.patched.cfg

## Purpose
Golden patched syz-manager fixture for focus set net.

## Important APIs, Types, and Functions
Canonical normalized JSON output including enabled/disabled/no-mutate syscalls, VM settings, and Experimental defaults.

## Control Flow
generate_test.go compares generated configs to this fixture after parsing and marshaling.

## State and Persistence
Checked-in test fixture; no runtime persistence.

## Dependencies and Integration Points
Depends on syzkaller pkg/config and pkg/mgrconfig, embedded templates, and api focus constants.

## Risks and Edge Cases
Risks include stale syscall allowlists, upstream mgrconfig default changes, and careless golden fixture rewrites.

## Test Signals
generate_test.go golden-tests singular, mixed, and no-focus outputs.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/fuzzconfig/testdata/singular/net.patched.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/report/email.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/report/email.go

## Purpose
Renders session reports into email body text.

## Important APIs, Types, and Functions
Render and embedded templateFS for template.txt and test_reply_template.txt.

## Control Flow
Chooses bug or patch-test template, parses templates, executes with Report and EmailConfig.

## State and Persistence
No persistence; transforms API report state into outbound message text.

## Dependencies and Integration Points
Integrates api.SessionReport, app.EmailConfig, embedded text templates, and reporter-generated report data.

## Risks and Edge Cases
Risks include template/schema drift and golden files masking regressions if regenerated without review.

## Test Signals
email_test.go golden-tests user-visible email bodies.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/report/email.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/report/email_test.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/report/email_test.go

## Purpose
Golden tests for report email rendering.

## Important APIs, Types, and Functions
TestRender and -write flag.

## Control Flow
Loads JSON fixtures, toggles moderation for bug reports, renders, and compares expected text files.

## State and Persistence
Reads fixtures; optional -write rewrites golden outputs.

## Dependencies and Integration Points
Integrates api.SessionReport, app.EmailConfig, embedded text templates, and reporter-generated report data.

## Risks and Edge Cases
Risks include template/schema drift and golden files masking regressions if regenerated without review.

## Test Signals
email_test.go golden-tests user-visible email bodies.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/report/email_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/report/testdata/1.in.json -->
# sources/test-tools/syzkaller/syz-cluster/pkg/report/testdata/1.in.json

## Purpose
JSON input fixture for multi-finding bug report with series metadata, repro links, build details, and dashboard link.

## Important APIs, Types, and Functions
Maps directly to api.SessionReport fields such as id, type, moderation, series, tests, findings, links, and error.

## Control Flow
email_test.go unmarshals it and passes it to report.Render for golden comparison.

## State and Persistence
Checked-in test fixture only; represents report state normally produced by services.

## Dependencies and Integration Points
Integrates api.SessionReport, app.EmailConfig, embedded text templates, and reporter-generated report data.

## Risks and Edge Cases
Risks include template/schema drift and golden files masking regressions if regenerated without review.

## Test Signals
email_test.go golden-tests user-visible email bodies.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/report/testdata/1.in.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/report/testdata/2.in.json -->
# sources/test-tools/syzkaller/syz-cluster/pkg/report/testdata/2.in.json

## Purpose
JSON input fixture for single-finding bug report fixture.

## Important APIs, Types, and Functions
Maps directly to api.SessionReport fields such as id, type, moderation, series, tests, findings, links, and error.

## Control Flow
email_test.go unmarshals it and passes it to report.Render for golden comparison.

## State and Persistence
Checked-in test fixture only; represents report state normally produced by services.

## Dependencies and Integration Points
Integrates api.SessionReport, app.EmailConfig, embedded text templates, and reporter-generated report data.

## Risks and Edge Cases
Risks include template/schema drift and golden files masking regressions if regenerated without review.

## Test Signals
email_test.go golden-tests user-visible email bodies.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/report/testdata/2.in.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/report/testdata/patch_test_fail.in.json -->
# sources/test-tools/syzkaller/syz-cluster/pkg/report/testdata/patch_test_fail.in.json

## Purpose
JSON input fixture for patch-test reply fixture with failed repro step and resulting finding.

## Important APIs, Types, and Functions
Maps directly to api.SessionReport fields such as id, type, moderation, series, tests, findings, links, and error.

## Control Flow
email_test.go unmarshals it and passes it to report.Render for golden comparison.

## State and Persistence
Checked-in test fixture only; represents report state normally produced by services.

## Dependencies and Integration Points
Integrates api.SessionReport, app.EmailConfig, embedded text templates, and reporter-generated report data.

## Risks and Edge Cases
Risks include template/schema drift and golden files masking regressions if regenerated without review.

## Test Signals
email_test.go golden-tests user-visible email bodies.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/report/testdata/patch_test_fail.in.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/report/testdata/patch_test_infra_err.in.json -->
# sources/test-tools/syzkaller/syz-cluster/pkg/report/testdata/patch_test_infra_err.in.json

## Purpose
JSON input fixture for patch-test reply fixture for infrastructure error path.

## Important APIs, Types, and Functions
Maps directly to api.SessionReport fields such as id, type, moderation, series, tests, findings, links, and error.

## Control Flow
email_test.go unmarshals it and passes it to report.Render for golden comparison.

## State and Persistence
Checked-in test fixture only; represents report state normally produced by services.

## Dependencies and Integration Points
Integrates api.SessionReport, app.EmailConfig, embedded text templates, and reporter-generated report data.

## Risks and Edge Cases
Risks include template/schema drift and golden files masking regressions if regenerated without review.

## Test Signals
email_test.go golden-tests user-visible email bodies.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/report/testdata/patch_test_infra_err.in.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/report/testdata/patch_test_ok.in.json -->
# sources/test-tools/syzkaller/syz-cluster/pkg/report/testdata/patch_test_ok.in.json

## Purpose
JSON input fixture for patch-test reply fixture for successful build and repro retest.

## Important APIs, Types, and Functions
Maps directly to api.SessionReport fields such as id, type, moderation, series, tests, findings, links, and error.

## Control Flow
email_test.go unmarshals it and passes it to report.Render for golden comparison.

## State and Persistence
Checked-in test fixture only; represents report state normally produced by services.

## Dependencies and Integration Points
Integrates api.SessionReport, app.EmailConfig, embedded text templates, and reporter-generated report data.

## Risks and Edge Cases
Risks include template/schema drift and golden files masking regressions if regenerated without review.

## Test Signals
email_test.go golden-tests user-visible email bodies.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/report/testdata/patch_test_ok.in.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/reporter/api.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/reporter/api.go

## Purpose
Reporter HTTP server for report delivery workflow.

## Important APIs, Types, and Functions
APIServer, NewAPIServer, Mux, upstreamReport, invalidateReport, nextReports, confirmReport, recordReply, reply, TestServer.

## Control Flow
Routes parse requests, call ReportService/DiscussionService, and centralize error-to-status mapping.

## State and Persistence
Server is stateless; services mutate reports, findings, and replies in Spanner.

## Dependencies and Integration Points
Integrates report services, discussion services, controller-created sessions/findings, report generator, and ReporterClient.

## Risks and Edge Cases
Risks include report ordering assumptions, age-window omissions in generation, and incomplete HTTP method validation.

## Test Signals
reporter/api_test.go and dedup_test.go exercise report delivery, replies, invalidation, and patch-test reports.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/reporter/api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/reporter/api_test.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/reporter/api_test.go

## Purpose
End-to-end reporter API tests.

## Important APIs, Types, and Functions
Tests cover report flow, reply recording, invalidation, patch-test reports, triage skip, and failed-step infrastructure errors.

## Control Flow
Creates controller-side sessions/findings, runs ReportGenerator, then uses ReporterClient against httptest reporter server.

## State and Persistence
Exercises report, reply, job, session, finding, test, and step rows.

## Dependencies and Integration Points
Integrates report services, discussion services, controller-created sessions/findings, report generator, and ReporterClient.

## Risks and Edge Cases
Risks include report ordering assumptions, age-window omissions in generation, and incomplete HTTP method validation.

## Test Signals
reporter/api_test.go and dedup_test.go exercise report delivery, replies, invalidation, and patch-test reports.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/reporter/api_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/reporter/dedup_test.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/reporter/dedup_test.go

## Purpose
Regression test for report finding deduplication.

## Important APIs, Types, and Functions
TestDeduplicationInReport.

## Control Flow
Creates duplicate-title findings across tests, generates a report, and asserts one finding remains.

## State and Persistence
Uses transient Spanner/local blob through controller and reporter APIs.

## Dependencies and Integration Points
Integrates report services, discussion services, controller-created sessions/findings, report generator, and ReporterClient.

## Risks and Edge Cases
Risks include report ordering assumptions, age-window omissions in generation, and incomplete HTTP method validation.

## Test Signals
reporter/api_test.go and dedup_test.go exercise report delivery, replies, invalidation, and patch-test reports.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/reporter/dedup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/reporter/generator.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/reporter/generator.go

## Purpose
Background generator for SessionReport rows.

## Important APIs, Types, and Functions
ReportGenerator, NewGenerator, Loop, Process, generateReportsPeriod/Limit, relevantReportAge.

## Control Flow
Periodically queries finished sessions missing reports, then inserts moderation or job-specific reports.

## State and Persistence
Persists SessionReports and reads Sessions/Jobs.

## Dependencies and Integration Points
Integrates report services, discussion services, controller-created sessions/findings, report generator, and ReporterClient.

## Risks and Edge Cases
Risks include report ordering assumptions, age-window omissions in generation, and incomplete HTTP method validation.

## Test Signals
reporter/api_test.go and dedup_test.go exercise report delivery, replies, invalidation, and patch-test reports.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/reporter/generator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/retest/retest.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/retest/retest.go

## Purpose
Runner for retesting reproducers on base and patched kernels.

## Important APIs, Types, and Functions
Runner, Run, retestFinding, testOnEnv, testResult, uploadStep.

## Control Flow
Fetches original finding, tests optional base and patched envs, uploads steps, and uploads a new finding only for patched-only crashes.

## State and Persistence
Persists results through controller API calls to SessionTestSteps and Findings.

## Dependencies and Integration Points
Integrates syzkaller instance.Env, controller API, findings, test steps, and retest workflow tasks.

## Risks and Edge Cases
Risks include partial per-finding failures returning nil from Run, nil environment assumptions, and base-crash suppression semantics.

## Test Signals
retest_test.go covers major pass/crash/error scenarios with mock environments.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/retest/retest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/retest/retest_test.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/retest/retest_test.go

## Purpose
Retest runner scenario tests with mocked instance.Env.

## Important APIs, Types, and Functions
mockEnv, runTest, TestParams, TestRetestScenarios.

## Control Flow
Builds original and retest sessions, runs Runner, then verifies findings and step statuses.

## State and Persistence
Uses transient controller API, Spanner, and local blob storage.

## Dependencies and Integration Points
Integrates syzkaller instance.Env, controller API, findings, test steps, and retest workflow tasks.

## Risks and Edge Cases
Risks include partial per-finding failures returning nil from Run, nil environment assumptions, and base-crash suppression semantics.

## Test Signals
retest_test.go covers major pass/crash/error scenarios with mock environments.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/retest/retest_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/service/base_finding.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/service/base_finding.go

## Purpose
Service wrapper for base-kernel finding upload/status checks.

## Important APIs, Types, and Functions
BaseFindingService, NewBaseFindingService, ErrBuildNotFound, Upload, Status, makeBaseFinding.

## Control Flow
Resolves BuildID to commit/config/arch/date and saves or queries BaseFindingRepository.

## State and Persistence
Reads Builds and writes/reads BaseFindings in Spanner.

## Dependencies and Integration Points
Service layer integrates api contracts, db repositories, blob storage, URL generation, and controller/reporter handlers.

## Risks and Edge Cases
Risks include orphaned blobs after DB write failures, subtle dedup/grouping semantics, and caller-visible domain errors needing correct HTTP mapping.

## Test Signals
Covered by controller/reporter/retest integration tests plus db repository tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/service/base_finding.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/service/build.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/service/build.go

## Purpose
Service wrapper for build upload and lookup.

## Important APIs, Types, and Functions
BuildService, NewBuildService, Upload, LastBuild, makeBuildInfo.

## Control Flow
Maps api.UploadBuildReq to db.Build, writes log/config blobs, inserts build, and maps latest build back to API.

## State and Persistence
Persists Builds in Spanner and log/config blobs in blob storage.

## Dependencies and Integration Points
Service layer integrates api contracts, db repositories, blob storage, URL generation, and controller/reporter handlers.

## Risks and Edge Cases
Risks include orphaned blobs after DB write failures, subtle dedup/grouping semantics, and caller-visible domain errors needing correct HTTP mapping.

## Test Signals
Covered by controller/reporter/retest integration tests plus db repository tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/service/build.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/service/discussion.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/service/discussion.go

## Purpose
Service for recording email replies and identifying the original report.

## Important APIs, Types, and Functions
DiscussionService, NewDiscussionService, RecordReply, identifyReport.

## Control Flow
Identifies a report by explicit ReportID or root message ID/reporter, then inserts a ReportReply and handles duplicates idempotently.

## State and Persistence
Persists ReportReplies and reads SessionReports.

## Dependencies and Integration Points
Service layer integrates api contracts, db repositories, blob storage, URL generation, and controller/reporter handlers.

## Risks and Edge Cases
Risks include orphaned blobs after DB write failures, subtle dedup/grouping semantics, and caller-visible domain errors needing correct HTTP mapping.

## Test Signals
Covered by controller/reporter/retest integration tests plus db repository tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/service/discussion.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/service/finding.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/service/finding.go

## Purpose
Service for finding save/list/get/invalidate/previous-version logic.

## Important APIs, Types, and Functions
FindingService, Save, saveAssets, InvalidateSession, List, ListPreviousFindings, Get, matchesPrevFindingsReq, deduplicateFindings, isBetterFinding.

## Control Flow
Saves blob assets, transactionally replaces logical findings, maps DB rows to public api.Finding, reads raw blobs back, and deduplicates reports by title.

## State and Persistence
Persists Findings and blob URIs; invalidation stamps InvalidatedAt.

## Dependencies and Integration Points
Service layer integrates api contracts, db repositories, blob storage, URL generation, and controller/reporter handlers.

## Risks and Edge Cases
Risks include orphaned blobs after DB write failures, subtle dedup/grouping semantics, and caller-visible domain errors needing correct HTTP mapping.

## Test Signals
Covered by controller/reporter/retest integration tests plus db repository tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/service/finding.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/service/job.go -->
# sources/test-tools/syzkaller/syz-cluster/pkg/service/job.go

## Purpose
Service for user-submitted patch-test jobs.

## Important APIs, Types, and Functions
JobService, NewJobService, GetJob, getFindingGroups, SubmitJob, JobLink, ErrPatchTooLarge.

## Control Flow
Validates report/session, stores bounded patch data, inserts Job, creates job-linked Session, and groups original findings by patched build for retest tasks.

## State and Persistence
Persists Jobs and job Sessions; stores patch blobs externally.

## Dependencies and Integration Points
Service layer integrates api contracts, db repositories, blob storage, URL generation, and controller/reporter handlers.

## Risks and Edge Cases
Risks include orphaned blobs after DB write failures, subtle dedup/grouping semantics, and caller-visible domain errors needing correct HTTP mapping.

## Test Signals
Covered by controller/reporter/retest integration tests plus db repository tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/service/job.go -->
