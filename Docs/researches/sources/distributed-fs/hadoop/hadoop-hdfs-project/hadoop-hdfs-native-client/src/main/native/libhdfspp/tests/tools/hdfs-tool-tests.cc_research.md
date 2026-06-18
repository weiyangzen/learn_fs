<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-tool-tests.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-tool-tests.cc

## Purpose
Instantiates the shared command-line parser tests for libhdfs++ HDFS tools. It maps each command mock to positive and negative factory combinations so the common fixtures can exercise each tool's option grammar.

## Important APIs, Types, And Functions
The file includes every mock header plus `hdfs-tool-test-fixtures.h` and `hdfs-tool-tests.h`. It uses `INSTANTIATE_TEST_SUITE_P` for suites such as `HdfsAllowSnapshot`, `HdfsDisallowSnapshot`, `HdfsRenameSnapshot`, `HdfsCreateSnapshot`, `HdfsCat`, `HdfsDf`, `HdfsDu`, `HdfsLs`, `HdfsDeleteSnapshot`, `HdfsChown`, `HdfsChmod`, `HdfsChgrp` and more, covering help, normal paths, recursive options, numeric options, ownership arguments, snapshot names, and invalid argument counts.

## Control Flow
At test registration time, gtest records factory values for `HdfsToolBasicTest`, `HdfsToolNegativeTestThrows`, and `HdfsToolNegativeTestNoThrow`. At runtime, each factory creates a mock with expectations, the fixture calls `Do()`, and gtest/gmock validates return value or exception behavior.

## State And Persistence
No persistent state. All effects are in-memory gtest registration and per-test mock state.

## Dependencies And Integration Points
Integrates all tool mocks with the shared factory and fixture framework. It is compiled into the tools test executable alongside `main.cc`.

## Risks
This is the central coverage matrix; omissions here mean a parser branch can be untested even if a factory and mock branch exist. Many negative cases expect broad exceptions from Boost program_options rather than specific diagnostics.

## Test Signals
The signal is suite-level coverage across each command. Failures reveal changed accepted arity, option aliases, parser exception behavior, or dispatch argument order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-tool-tests.cc -->
