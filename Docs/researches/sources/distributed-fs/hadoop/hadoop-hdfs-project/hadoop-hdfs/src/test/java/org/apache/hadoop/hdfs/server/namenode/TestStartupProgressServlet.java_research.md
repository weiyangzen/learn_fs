# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestStartupProgressServlet.java

## Purpose

`TestStartupProgressServlet` verifies the JSON emitted by `StartupProgressServlet` for empty, running, and complete NameNode startup progress state.

## Important APIs, Types, and Functions

The fixture uses Mockito to provide a `ServletContext` containing a `StartupProgress` under `NameNodeHttpServer.STARTUP_PROGRESS_ATTRIBUTE_KEY`, mocks request/response, and calls the real `doGet`. It uses helper state builders from `StartupProgressTestHelper`, Jetty `JSON.toString`, and `ImmutableMap` expected bodies.

## Control Flow

Each test configures a `StartupProgress` snapshot, calls `doGetAndReturnResponseBody`, removes nondeterministic `elapsedTime` fields through `filterJson`, and compares the exact JSON structure. Expected output always has top-level `percentComplete` and `phases`; phase entries include name, description, status, completion fraction, and step details.

## State and Persistence Behavior

The servlet reads in-memory startup progress only. No persistent state is changed. The test intentionally filters elapsed time because it changes at runtime.

## Dependencies and Integration Points

This is an HTTP-layer contract test between NameNode startup progress tracking and web UI/API consumers. It depends on phase and step names such as `LoadingFsImage`, `LoadingEdits`, `SavingCheckpoint`, `SafeMode`, `Inodes`, and `AwaitingReportedBlocks`.

## Risks and Edge Cases

The exact JSON comparison catches field renames, ordering changes, status regressions, and percentage calculation changes. It is brittle to intentional schema evolution and only ignores elapsed-time volatility.

## Test Signals

Signals are exact equality against pending state at `0.0`, running state at `0.375` with fsimage complete and edits half complete, and final state at `1.0` with all phases complete and populated steps.
