<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limits_database.h -->
# sources/distributed-fs/lizardfs/src/common/io_limits_database.h

## Purpose
Declares the I/O limits database and the serializable group/limit pair used to expose configured limits. The source was read completely for this report.

## Important APIs, Types, And Functions
`IoGroupAndLimit`, `IoLimitsDatabase::InvalidGroupIdException`, `setLimits`, `getGroups`, `getGroupsAndLimits`, and `request` define the contract.

## Control Flow
The header describes token-bucket-backed limiting; executable behavior is in `io_limits_database.cc` and `token_bucket.h`.

## State And Persistence Behavior
Holds a `std::map<GroupId, TokenBucket>` keyed by string group id. The map is mutable runtime state and not synchronized internally.

## Dependencies And Integration Points
Depends on `io_limits_config_loader.h`, `serialization_macros.h`, `token_bucket.h`, and `time_utils` through bucket APIs.

## Risks And Edge Cases
Callers must provide external synchronization if accessed concurrently. The comment says limits are bytes/sec, while implementation consumes loader limits as KB/sec and converts them.

## Test Signals
Validated by `io_limits_database_unittest.cc`; integration tests should cover concurrent reconfiguration and mount/master request loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limits_database.h -->
