<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/get-content-summary-state.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/get-content-summary-state.h

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/get-content-summary-state.h` declares `GetContentSummaryState`, the shared callback state used by `hdfs_du` while it fans out asynchronous content-summary requests. The source was read as a complete 68-line file for this report.

## Important APIs, Types, and Functions

`GetContentSummaryState` stores a final status handler, `request_counter`, `find_is_done`, accumulated `hdfs::Status`, and a mutex. The constructor moves the handler and initializes the counter and find-completion flag.

## Control Flow

The struct itself has no flow. `hdfs-du.cc` increments `request_counter` for each `GetContentSummary` call, decrements it in callbacks, sets `find_is_done` when listing completes, and invokes `handler(status)` once both conditions are satisfied.

## State and Persistence Behavior

All state is in-memory and command-lifetime only. The mutex protects shared fields because content-summary callbacks can run concurrently.

## Dependencies and Integration Points

It depends on `<functional>`, `<mutex>`, and `hdfspp/hdfspp.h`, and is tightly coupled to the asynchronous `FileSystem::GetContentSummary` callback contract.

## Risks and Edge Cases

Incorrect counter updates can deadlock the command or complete before all results print. Maintaining the first failure while still draining callbacks is the key concurrency invariant.

## Test Signals

Recursive `du` tests with empty directories, many entries, injected `GetContentSummary` failures, and concurrent callback ordering are the strongest signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/get-content-summary-state.h -->
