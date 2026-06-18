# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_retention_test.go

## Purpose

This test file validates Object Lock retention/legal-hold parsing and validation plus bucket Object Lock configuration behavior.

## Important APIs, Types, and Functions

Tests cover `ValidateRetention`, `ValidateLegalHold`, object-lock XML parsers, `ValidateObjectLockConfiguration`, `validateDefaultRetention`, `StoreObjectLockConfigurationInExtended`, `LoadObjectLockConfigurationFromExtended`, and `CreateObjectLockConfiguration`.

## Control Flow

Table tests exercise valid and invalid retention modes, missing fields, past dates, legal hold status, namespace/no-namespace XML, malformed XML, days/years rules, configured maximums, and stale-years cleanup when switching to days.

## State and Persistence Behavior

All state is in-memory XML request bodies and `filer_pb.Entry.Extended`. The tests verify `DaysSet`/`YearsSet` presence tracking and cleanup of stale persisted default-retention keys.

## Dependencies and Integration Points

The file depends on `filer_pb.Entry`, S3 constants, XML request parsing, and Object Lock validation/storage helpers.

## Risks and Edge Cases

Risks covered include lowercase legal hold values, malformed XML, Veeam-compatible no-namespace XML, both/neither days and years, out-of-range durations, and stale config metadata.

## Test Signals

The validation matrices are strong pure-unit signals. End-to-end handler tests remain a gap.
