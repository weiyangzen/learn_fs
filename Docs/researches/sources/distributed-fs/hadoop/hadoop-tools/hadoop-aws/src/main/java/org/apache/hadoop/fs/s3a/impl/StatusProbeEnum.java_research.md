# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/StatusProbeEnum.java

## Purpose
`StatusProbeEnum` defines the S3 probes used to resolve path status: object HEAD, directory marker HEAD, and LIST.

## Important APIs and Types
Enum values are `Head`, `DirMarker`, and `List`. Static sets include `ALL`, `HEAD_ONLY`, `LIST_ONLY`, `FILE`, and `DIRECTORIES`.

## Control Flow
Callers choose a static set to control status resolution strategy. `FILE` maps to HEAD only; `DIRECTORIES` maps to list only; `ALL` contains `Head` and `List` but not `DirMarker`.

## State and Persistence
The enum and sets are in-memory constants. No persistence.

## Dependencies and Integration Points
It depends on `EnumSet` and Hadoop classification annotations. It integrates with S3A status probing/listing logic.

## Risks and Edge Cases
The naming can mislead: `ALL` excludes `DirMarker`. If callers expect directory marker HEADs, they must request it explicitly or use logic elsewhere.

## Test Signals
Status-resolution tests should assert exactly which probes are attempted for each set and verify marker-only directories with relevant probe configurations.
