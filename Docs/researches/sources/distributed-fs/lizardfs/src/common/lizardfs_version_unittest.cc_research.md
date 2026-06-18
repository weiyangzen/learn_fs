<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lizardfs_version_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/lizardfs_version_unittest.cc

## Purpose
Tests numeric encoding of LizardFS versions. The source was read completely for this report.

## Important APIs, Types, And Functions
Calls `lizardfsVersion` for representative major/minor/micro combinations.

## Control Flow
Straight-line expectations compare against hexadecimal encoded constants.

## State And Persistence Behavior
No state or persistence.

## Dependencies And Integration Points
Depends on gtest and `lizardfs_version.h`.

## Risks And Edge Cases
Does not test `lizardfsVersionToString`, milestone constants, or boundary values.

## Test Signals
Passing tests protect the base encoding formula used by protocol feature gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lizardfs_version_unittest.cc -->
