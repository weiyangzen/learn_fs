# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/magic/MagicCommitTracker.java

## Purpose
Abstract `PutTracker` base for magic commits. It redirects stream close behavior so uploaded MPU parts are not made visible until the job committer completes them.

## Important APIs, Types, And Functions
Stores the original under-magic key, final destination key, pending metadata key, nominal path, bucket, `WriteOperationHelper`, and `PutTrackerStatistics`. `initialize()` returns true to start MPU immediately. `outputImmediatelyVisible()` returns false. `aboutToComplete()` remains abstract for S3-backed and in-memory metadata implementations.

## Control Flow
Created by S3A magic integration when a write targets a magic path. The stream uploads MPU parts to the final destination key, then the concrete tracker saves pending commit metadata and returns false so normal completion is skipped.

## State And Persistence
Holds runtime metadata required by subclasses. Persistence is delegated to `S3MagicCommitTracker` or `InMemoryMagicCommitTracker`.

## Dependencies And Integration Points
Extends `PutTracker`; uses S3A write helpers and statistics. It must not import MapReduce types, keeping filesystem write paths independent of MR.

## Risks
Subclasses must always record enough metadata for later completion; returning the wrong boolean can expose objects early or lose commit data.

## Test Signals
Verify delayed visibility, immediate MPU initialization, correct destination key selection, and subclass behavior for metadata persistence.
