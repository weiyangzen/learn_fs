# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ssl/FileMonitoringTimerTask.java

## Purpose

`FileMonitoringTimerTask` is a reusable timer task that detects local file modification-time changes and invokes a callback, used for SSL store reloads.

## Important APIs, Types, and Functions

It provides constructors for one path or a list of paths, stores an `onFileChange` callback and optional failure callback, and implements `run`.

## Control Flow

Construction snapshots each file's current `lastModified`. `run` scans paths until it finds the first changed timestamp, calls `onFileChange` for that path, catches any throwable and sends it to `onChangeFailure` or logs it, then updates that path's last-processed timestamp.

## State and Persistence Behavior

State is the monitored path list and matching last-modified timestamp list. It reads file metadata only and persists nothing.

## Dependencies and Integration Points

It depends on `TimerTask`, `Path`, Java functional `Consumer`, Hadoop `Preconditions`, and SLF4J. `FileBasedKeyStoresFactory` schedules it for keystore/truststore reload.

## Risks and Edge Cases

Only the first changed file is processed per run. Timestamp granularity can miss rapid successive changes. If a reload callback fails, the timestamp is still advanced after handling, so a failed reload may not retry until the file changes again.

## Test Signals

Tests should cover null argument rejection, single and multiple path detection, callback invocation, failure callback/log fallback, timestamp advancement, and first-change-only behavior.
