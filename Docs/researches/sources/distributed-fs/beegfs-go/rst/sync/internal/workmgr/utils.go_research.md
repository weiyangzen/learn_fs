# sources/distributed-fs/beegfs-go/rst/sync/internal/workmgr/utils.go

## Purpose
This file contains BeeSync work-manager test helpers plus production helpers for creating initial work results and splitting a work segment into upload parts.

## Important APIs, Types, and Functions
`tempPathForTesting` creates temporary Badger directories for tests. `assertDBEntriesLenForTesting` counts entries in the work journal and job store. `newWorkFromRequest` creates an initial scheduled `work` result from a `workRequest`. `generatePartsFromSegment` returns a closure that yields `(partNumber, offsetStart, offsetStop)` tuples until `-1, -1, -1`.

## Control Flow
`newWorkFromRequest` computes the number of parts, generates part descriptors from the request segment, and returns a `flex.Work` with scheduled status and initialized parts. `generatePartsFromSegment` special-cases empty files where `OffsetStop == -1`, otherwise divides the inclusive byte range across the requested part numbers and assigns any remainder to the final part.

## State and Persistence Behavior
The test helpers create and delete temporary directories and iterate persistent stores. The production helpers do not persist directly, but their generated `work` records are stored in the work journal and later updated by workers.

## Dependencies and Integration Points
The file depends on `kvstore` iteration through manager stores, `flex` protobuf builders, Testify `require` in test helpers, and the `work`/`workRequest` wrappers from `work.go`. `SubmitWorkRequest` calls `newWorkFromRequest` to initialize journal state.

## Risks and Edge Cases
`newWorkFromRequest` computes `numberOfParts` before checking whether `Segment` is nil, which could panic for nil segments despite the later nil check. Part splitting assumes valid part ranges and does not validate negative or reversed part numbers. Temporary cleanup sleeps one second to avoid DB shutdown races, slowing tests.

## Test Signals
`utils_test.go` covers initial work response generation, empty file part generation, evenly divided ranges, remainders assigned to the last part, and nonzero starting offsets/part numbers.
