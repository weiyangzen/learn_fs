# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/commit/files/package-info.java

## Purpose
Package documentation and stability annotations for committer persistent data formats.

## Important APIs, Types, And Functions
Declares `org.apache.hadoop.fs.s3a.commit.files` as private and unstable. The Javadoc identifies `PersistentCommitData` as the common base and describes single pending commits, multiple-file pending sets, and `_SUCCESS` summary data.

## Control Flow
No executable control flow.

## State And Persistence
Documents the JSON formats that become part of commit state exchange between tasks and job committers, and the visible `SuccessData` marker after completion.

## Dependencies And Integration Points
References `PersistentCommitData` and `SuccessData`, including compatibility with manifest committer success data.

## Risks
The package is marked unstable, but some JSON payloads are effectively interoperable with other committers; changes should preserve expected compatibility where documented.

## Test Signals
Javadoc/package annotation checks and compatibility tests around `SuccessData` and pending metadata formats.
