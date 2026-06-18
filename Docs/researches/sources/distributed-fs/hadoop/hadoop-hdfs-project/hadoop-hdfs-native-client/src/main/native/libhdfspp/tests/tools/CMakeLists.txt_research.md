# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/CMakeLists.txt

## Purpose

This CMake file builds the libhdfspp command-line tool test binary from tool mocks, common tool fixtures, and production tool libraries.

## Important APIs, types, and functions

It defines `hdfs_tool_tests` from many `*-mock.cc` files, `hdfs-tool-test-fixtures.cc`, `hdfs-tool-tests.cc`, and `main.cc`. It adds include directories for test tool helpers and each production tool subdirectory, then links gmock and all tool libraries such as df, du, snapshot, chown/chmod/chgrp, copy/move, count, mkdir, rm, get, find, ls, setrep, stat, tail, and cat.

## Control flow, state, and persistence

There is no runtime logic in the build file. At build time it aggregates all mocks into one executable and registers it as `hdfs_tool_tests`.

## Dependencies and integration points

It integrates test mocks with production tool parser/handler libraries. The include-directory list mirrors the tool set and must be updated when tools are added or moved.

## Risks and test signals

The main risks are missing a new mock/source/library when a tool is added, include path drift, and link failures if production tool library names change. The single aggregate test binary provides quick coverage for command dispatch and argument handling across tools.
