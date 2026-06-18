# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/StartupProgressServlet.java

## Purpose

`StartupProgressServlet.java` exposes NameNode startup progress as JSON at `/startupProgress`. The source was read as a complete 139-line file.

## Important APIs, Types, and Functions

The servlet extends `DfsServlet`, declares `PATH_SPEC`, and overrides `doGet`. Helpers `writeNumberFieldIfDefined` and `writeStringFieldIfNotNull` omit undefined values. JSON keys include `elapsedTime`, `percentComplete`, `phases`, `steps`, `status`, `count`, `total`, `file`, and `size`.

## Control Flow

`doGet` sets the response content type, fetches `StartupProgress` from the NameNode HTTP server context, creates a snapshot `StartupProgressView`, and streams a JSON object using Jackson. It emits global progress fields, then iterates phases and phase steps, adding type descriptions, counts, totals, percentages, elapsed time, and optional file/size metadata. The generator is closed in a `finally` block.

## State and Persistence Behavior

The servlet owns no persistent state. It serializes a point-in-time view of in-memory startup progress maintained elsewhere by NameNode startup code.

## Dependencies and Integration Points

It integrates with `NameNodeHttpServer.getStartupProgressFromContext`, `StartupProgress`, `StartupProgressView`, `Phase`, `Step`, `StepType`, Jackson `JsonGenerator`, and the NameNode web UI/API surface.

## Risks and Edge Cases

Consumers may depend on stable JSON field names. Undefined size values are represented by omission, not null. Errors while writing response JSON are normal servlet IO failures. If the context lacks startup progress, the failure will occur outside this class's own validation.

## Test Signals

Tests should issue servlet GETs for empty, partial, and complete progress views; validate JSON shape, content type, optional field omission, phase/step ordering from the view, and cleanup on generator/write failures.
