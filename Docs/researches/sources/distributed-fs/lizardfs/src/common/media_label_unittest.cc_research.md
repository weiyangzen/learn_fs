<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/media_label_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/media_label_unittest.cc

## Purpose
Tests media label validation and handle/string round trips. The source was read completely for this report.

## Important APIs, Types, And Functions
Uses `MediaLabelManager::isLabelValid`, `getHandle`, `getLabel`, `MediaLabel`, and wildcard constants.

## Control Flow
Tests assert accepted alphanumeric/underscore labels up to length 32, reject empty/space/punctuation/too-long labels, and validate handle behavior.

## State And Persistence Behavior
Global singleton state persists across tests in-process, so labels registered in one test remain registered.

## Dependencies And Integration Points
Depends on gtest and `media_label.h`.

## Risks And Edge Cases
Does not test concurrent registration or default invalid `MediaLabel` string conversion.

## Test Signals
Passing tests protect the user-visible label grammar and basic interning behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/media_label_unittest.cc -->
