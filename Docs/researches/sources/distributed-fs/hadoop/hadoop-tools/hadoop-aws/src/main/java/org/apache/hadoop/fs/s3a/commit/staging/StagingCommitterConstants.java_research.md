# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/staging/StagingCommitterConstants.java

## Purpose
Constants used by staging committers for temporary directories and partition naming.

## Important APIs, Types, And Functions
`FILESYSTEM_TEMP_PATH` defaults cluster staging to `tmp/staging`. `TABLE_ROOT` names root-table output as a synthetic partition. `STAGING_UPLOADS` names the directory holding pending upload manifests.

## Control Flow
`Paths` uses these constants while building staging upload directories and partition sets.

## State And Persistence
No runtime state. The constants shape persistent staging paths and pending-manifest locations.

## Dependencies And Integration Points
Used by `Paths`, `StagingCommitter`, and partitioned conflict resolution.

## Risks
Changing names breaks cleanup and discovery of existing staging manifests. `TABLE_ROOT` must not collide with real partition handling assumptions.

## Test Signals
Path construction and partition extraction tests should assert these constant values where behavior depends on them.
