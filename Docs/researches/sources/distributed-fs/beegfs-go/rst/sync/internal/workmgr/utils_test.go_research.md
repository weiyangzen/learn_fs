# sources/distributed-fs/beegfs-go/rst/sync/internal/workmgr/utils_test.go

## Purpose
This file tests BeeSync utility behavior for initial work-result creation and segment-to-part splitting.

## Important APIs, Types, and Functions
`TestNewWorkResponseFromRequest` verifies `newWorkFromRequest` copies job/request IDs, sets scheduled status, writes the expected message, and creates the expected number of parts. `TestGenerateParts` table-tests the part generator across empty files, even splits, uneven splits, and nonzero offsets/part numbers.

## Control Flow
The tests instantiate protobuf segments and repeatedly call the closure returned by `generatePartsFromSegment`, checking emitted tuples until the sentinel `-1, -1, -1` appears.

## State and Persistence Behavior
The tests are in-memory only. They validate data that will later be persisted into the BeeSync work journal.

## Dependencies and Integration Points
The tests depend on Testify assertions and protobuf `flex` builders. They provide coverage for the initialization path used by `Manager.SubmitWorkRequest`.

## Risks and Edge Cases
The tests do not cover nil segments, invalid part ranges, zero parts, or reversed offsets. They also do not verify checksum/entity-tag fields because those are populated later during work execution.

## Test Signals
Passing tests confirm current inclusive offset math and last-part remainder behavior, including the special empty-file marker.
