# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/files/SuccessData.java

## Purpose
JSON format written to `_SUCCESS` by S3A committers. It identifies the committer, job, host, committed filenames, metrics, diagnostics, state, stage, and IO statistics, and is intended to remain compatible with the manifest committer success format.

## Important APIs, Types, And Functions
`VERSION` is 1 and `NAME` embeds the format identity. `validate()` requires the exact name. `save()` forces the name before writing. `load()` reads and validates. `dumpMetrics()`, `dumpDiagnostics()`, and `joinMap()` produce sorted text reports. `recordJobFailure()` marks failure and stores exception text plus stack trace.

## Control Flow
After successful job commit, `CommitOperations.createSuccessMarker()` may add filesystem metrics and save `SuccessData` to output `_SUCCESS`. Abort or diagnostic paths may write failure summaries elsewhere.

## State And Persistence
Persists public-facing JSON fields: success flag, timestamp/date, hostname, committer, description, job ID and source, metrics, diagnostics, filenames, IO statistics, state, and stage.

## Dependencies And Integration Points
Extends `PersistentCommitData`; used by committers and tests to distinguish S3A committers from classic zero-length `_SUCCESS` markers.

## Risks
The JSON format is compatibility-sensitive. Large jobs intentionally cap filename lists elsewhere, so consumers must not infer complete output inventory from this file.

## Test Signals
Read classic empty marker versus loadable `SuccessData`, validate incompatible names, ensure sorted metric/diagnostic dumps, verify failure diagnostics capture exceptions, and confirm manifest-format compatibility expectations.
