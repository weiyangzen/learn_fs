<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/content_summary.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/content_summary.cc

## Purpose
Implements formatting for `ContentSummary`, the libhdfspp representation of HDFS content summary output.

## Important APIs, Types, And Functions
The constructor initializes length, file count, directory count, quota, consumed space, and space quota to zero. `str(bool include_quota)` renders content-summary columns, while `str_du()` renders a `du`-style line with left-padded length and path.

## Control Flow
Formatting functions build a `stringstream` from already-populated fields; `include_quota` controls whether quota columns are emitted.

## State And Persistence
State is per-object counters and path, populated elsewhere from namenode responses. No persistence or mutation beyond construction is performed here.

## Dependencies And Integration Points
Used by public content-summary APIs and CLI-style display code. Depends on `hdfspp/content_summary.h` and iostream formatting.

## Risks
The output format is positional and may be consumed by tests or clients, so spacing/column changes can break compatibility. Zero quota defaults may be ambiguous when quota is not requested.

## Test Signals
Tests should compare `str()` with and without quota and `str_du()` for empty and populated summaries, including paths with spaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/content_summary.cc -->
