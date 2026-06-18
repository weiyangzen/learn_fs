<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/TimedOutTestsListener.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/TimedOutTestsListener.java

## Purpose

`TimedOutTestsListener.java` builds test-timeout diagnostics for Hadoop tests, including timestamped thread dumps and deadlock reports.

## Important APIs, Types, and Functions

Public APIs are constructors using `System.err` or an injected `PrintWriter`, `testFailure(RuntimeException)`, and static `buildThreadDiagnosticString()`. Internal helpers include `buildThreadDump`, `buildDeadlockInfo`, `printThreadInfo`, `printThread`, and `printLockInfo`. It uses `ThreadMXBean`, `ThreadInfo`, `MonitorInfo`, `LockInfo`, and `StringUtils.getStackTrace`.

## Control Flow

`testFailure` looks for timeout-like exception messages beginning with `test timed out after`; on a timeout it writes diagnostic output. `buildThreadDiagnosticString` combines a date header, all thread info, and deadlock info. The thread dump walks `ThreadMXBean.dumpAllThreads(true, true)`, while deadlock info calls `findDeadlockedThreads` and formats the returned thread infos.

## State and Persistence Behavior

The listener owns only an output writer. It samples live JVM thread/lock state and writes text diagnostics, with no durable persistence beyond the receiving stream.

## Dependencies and Integration Points

It integrates with JUnit timeout failure handling, JVM management beans, Hadoop `StringUtils`, and test infrastructure that invokes listeners on runtime failures.

## Risks and Edge Cases

Timeout detection is string-prefix based, so changes in upstream exception text can bypass diagnostics. Management APIs may return null for no deadlocks, and thread dumps are inherently race-prone snapshots of live threads.

## Test Signals

The paired `TestTimedOutTestsListener` covers deadlock output. Additional useful signals are synthetic timeout/non-timeout failures and injected `PrintWriter` capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/TimedOutTestsListener.java -->
