# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/scheduler/configload_test.go

## Purpose
This file tests scheduler lifecycle config loading from filer bucket metadata. It verifies bucket versioning classification, prior-state seeding, and bucket directory pagination/skip/error semantics.

## Important APIs and helpers
The tests use `bucketEntry`, `dirEntry`, `fileEntry`, and `fakeFilerClient` from `testhelpers_test.go`. `minimalLifecycleXML` provides a valid one-rule XML config. Tests call `IsBucketVersioned`, `AllActivePriorStates`, and `LoadCompileInputs`.

## Control flow and state behavior under test
Versioning tests assert that missing attributes are false, `Enabled` and `Suspended` are accepted case-insensitively with whitespace, and unrelated values are rejected. Prior-state tests verify empty inputs produce empty maps and that every action kind receives a `BootstrapComplete=true`, `ModeEventDriven` state keyed by bucket and rule hash. Loader tests assert empty directories, stray files, buckets without XML, and buckets with empty XML are skipped. Valid config becomes one compile input, versioning propagates, malformed XML becomes a parse error while good buckets still load, and 1030 buckets force multi-page listing without skip/duplication.

## Dependencies and integration points
The tests use `filer_pb`, S3 constants, lifecycle rules, engine action keys, and testify assertions. They exercise the fake stream implementation enough to model `SeaweedList` pagination.

## Risks and gaps
The tests do not connect to a real filer or validate all XML variants; parser details are delegated to `lifecycle_xml` tests. They do not test cancellation except through helper stream support.

## Test signals
The suite provides good regression coverage for scheduler refresh correctness, especially the risk of silently missing buckets after the first page or conflating prior states between buckets with identical rules.
