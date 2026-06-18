<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limits_database.cc -->
# sources/distributed-fs/lizardfs/src/common/io_limits_database.cc

## Purpose
Implements a per-I/O-group token-bucket database that grants byte counts according to configured KB/sec limits and accumulation windows. The source was read completely for this report.

## Important APIs, Types, And Functions
`setLimits`, `getGroups`, `getGroupsAndLimits`, and `request` are the active methods. `setLimits` reconciles the ordered group map with the parsed config and reconfigures each `TokenBucket`.

## Control Flow
Configuration walks existing groups and new limits in sorted order, erasing removed groups, inserting new `TokenBucket(now)` states, and converting limits from KB/sec to bytes/sec and max accumulated bytes. Requests dispatch to the matching bucket and return the granted byte count.

## State And Persistence Behavior
Runtime state is an ordered `std::map<GroupId, TokenBucket>`. No disk persistence; limits are reconstructed from config/reconfigure events.

## Dependencies And Integration Points
Consumes `IoLimitsConfigLoader::LimitsMap`; emits serializable `IoGroupAndLimit` records for management/status protocols.

## Risks And Edge Cases
Limit arithmetic multiplies by 1024 and `accumulate_ms`; large limits can overflow `uint64_t` in extreme configs. Unknown groups throw `InvalidGroupIdException`.

## Test Signals
Unit tests cover group listing, partial grants, token accumulation caps, and request timing progression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/io_limits_database.cc -->
