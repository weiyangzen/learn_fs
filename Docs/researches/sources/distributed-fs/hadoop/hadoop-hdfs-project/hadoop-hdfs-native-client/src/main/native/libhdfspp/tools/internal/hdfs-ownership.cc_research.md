<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/hdfs-ownership.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/hdfs-ownership.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/hdfs-ownership.cc` implements the `Ownership` parser and equality semantics for native ownership-changing tools. The source was read as a complete 44-line file for this report.

## Important APIs, Types, and Functions

`Ownership::Ownership(const std::string&)` splits on the first colon. Without a colon, the whole input is the user. With a colon, the prefix is `user_` and the suffix becomes optional `group_`. `operator==` compares users and requires both groups to be present and equal or both absent.

## Control Flow

Construction performs one `find(':')` and either stores the entire string as user or populates user/group substrings. Equality first checks user equality, then branches on group optionality.

## State and Persistence Behavior

The implementation persists no external state. It creates immutable parsed ownership values used later by command handlers.

## Dependencies and Integration Points

It includes `hdfs-ownership.h` and lives in `hdfs::tools`, feeding chown/chgrp command parsing and tests.

## Risks and Edge Cases

There is no validation for empty user or group components; `user:` produces an engaged empty group. Only the first colon is structural, so additional colons remain inside the group string.

## Test Signals

Focused parser/equality tests for no-colon, colon, empty components, multiple colons, and optional group equality cover this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/hdfs-ownership.cc -->
