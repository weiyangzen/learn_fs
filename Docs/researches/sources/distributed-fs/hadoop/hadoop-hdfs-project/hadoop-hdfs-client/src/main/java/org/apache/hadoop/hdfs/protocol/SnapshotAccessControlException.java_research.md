# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshotAccessControlException.java

## Purpose
`SnapshotAccessControlException` is the HDFS protocol exception for snapshot access violations, especially attempts to mutate read-only snapshot paths.

## APIs and Behavior
It extends `AccessControlException` and provides constructors for a message or cause.

## State, Dependencies, and Integration
There is no additional state. It appears in `ClientProtocol` method documentation for create, append, rename, delete, mkdir, set quota/times, symlink creation, and other namespace mutations that must reject read-only snapshot paths.

## Risks and Test Signals
Tests should verify the specific exception is raised for snapshot mutation attempts, that cause/message are preserved across RPC, and that normal permission-denied cases still use the correct access-control exception type.
