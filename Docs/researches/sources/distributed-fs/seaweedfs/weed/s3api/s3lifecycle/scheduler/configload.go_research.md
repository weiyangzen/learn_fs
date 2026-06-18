# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/scheduler/configload.go

## Purpose
This file loads S3 bucket lifecycle configurations from filer bucket entries and converts them into `engine.CompileInput` records for lifecycle snapshot compilation.

## Important APIs and functions
`BucketLifecycleConfigurationXMLKey` names the extended attribute containing lifecycle XML. `ParseError` records per-bucket parse failures without aborting the whole load. `LoadCompileInputs` lists bucket entries under a buckets path, parses non-empty lifecycle XML via `lifecycle_xml.ParseCanonical`, and returns compile inputs plus parse errors. `IsBucketVersioned` interprets the bucket versioning extended attribute as versioned when it is `Enabled` or `Suspended`, case/space normalized. `AllActivePriorStates` creates event-driven bootstrap-complete prior states for every action kind in every rule.

## Control flow and state behavior
`LoadCompileInputs` paginates through bucket entries with a 1024 entry page size and `startFrom` continuation. It skips non-directories, buckets with missing or empty lifecycle XML, malformed configs after recording `ParseError`, and configs that parse to zero rules. Transport/listing errors abort the entire load. No data is persisted here; compile inputs are regenerated from filer metadata.

## Dependencies and integration points
The file depends on `filer_pb.SeaweedList`, bucket entry extended attributes, S3 lifecycle XML canonicalization, S3 constants for versioning, and the engine compile API. It is part of scheduler refresh, feeding `engine.New().Compile` elsewhere. `AllActivePriorStates` is a temporary or out-of-band scheduler behavior that treats all loaded actions as ready for event-driven dispatch.

## Risks and edge cases
Malformed XML is intentionally non-fatal but can disable lifecycle for that bucket until corrected. Pagination correctness is important at cluster scale; a bad `startFrom` loop could skip buckets. `AllActivePriorStates` bypasses incremental bootstrap completeness and may schedule immediately for all rules, so production callers must understand the current bootstrap model.

## Test signals
`configload_test.go` covers versioning value parsing, prior-state seeding, empty/missing configs, file skipping, valid XML, malformed XML parse errors, and pagination beyond one page.
