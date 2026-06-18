# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/AbstractJournalProgressLogger.java

## Purpose
`AbstractJournalProgressLogger` rate-limits progress logging during journal replay or catch-up.

## Important APIs, Types, And Functions
Subclasses provide `getLastAppliedIndex` and `getJournalName`. `logProgress` uses exponential backoff capped by `MAX_LOG_INTERVAL_MS`, computes entries read since the last measurement, and optionally estimates remaining entries/time from an end commit index.

## Control Flow, State, Dependencies, Risks, And Tests
The logger stores last measurement time, last commit index, and log count in memory only. Dependencies are SLF4J and `OptionalLong`. Risks include initial `mLastCommitIdx` set to zero for journals with nonzero starting indices, division by zero avoidance relying on finite checks, and non-thread-safe mutable counters. Tests should control time or subclass behavior to verify rate limiting, estimate formatting, absent end index, and backoff cap.
