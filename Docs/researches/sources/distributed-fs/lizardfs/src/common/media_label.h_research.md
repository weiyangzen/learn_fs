<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/media_label.h -->
# sources/distributed-fs/lizardfs/src/common/media_label.h

## Purpose
Declares media label interning and the lightweight `MediaLabel` value wrapper. The source was read completely for this report.

## Important APIs, Types, And Functions
`MediaLabelManager::HandleValue`, `getHandle`, `getLabel`, `isLabelValid`, `kWildcard`; `MediaLabel` constructors, string/handle conversions, comparisons, and hash functor are public.

## Control Flow
Most methods forward to the singleton manager or compare the stored handle.

## State And Persistence Behavior
`MediaLabel` stores only a 16-bit handle; the manager owns label/handle maps globally.

## Dependencies And Integration Points
Used by chunk storage/media-label selection code and unordered containers via `MediaLabel::hash`.

## Risks And Edge Cases
Default-constructed label has handle 0 and converting it to string throws because 0 is not registered. Handles are process-local assignments unless callers guarantee consistent registration ordering.

## Test Signals
Unit tests should cover default invalid conversion, ordering, hashing, and concurrent registration if used across threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/media_label.h -->
