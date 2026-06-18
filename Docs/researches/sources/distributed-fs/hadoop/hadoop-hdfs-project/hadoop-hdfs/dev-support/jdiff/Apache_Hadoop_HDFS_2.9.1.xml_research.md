# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_2.9.1.xml

## Purpose

This XML is the JDiff baseline for `Apache Hadoop HDFS 2.9.1`, generated on 2018-04-16. It is used by API compatibility tooling to validate the public annotated HDFS module surface for the 2.9 maintenance line.

## Important APIs, Types, And Functions

The file contains 38 packages, 4 public types, and 12 public methods. The significant surfaces are the JournalNode management bean (`getJournalsStatus()`), the NameNode `AuditLogger` interface, the abstract `HdfsAuditLogger` with overloads for caller context and delegation token secret manager data, and `INodeAttributeProvider` for lifecycle, inode attribute substitution, and external access-control enforcement. These APIs are extension and observability contracts rather than direct file IO APIs.

## Control Flow And State

There is no executable path. The JDiff control model is a static tree walk over packages, types, methods, constructors, params, and docs. The state is the public API signature set for 2.9.1, including documentation that audit logging happens in a NameNode critical section and therefore must return quickly.

## Dependencies And Integration Points

The generation metadata references Hadoop 2.9.1 build artifacts and the same broad ecosystem of Hadoop common/auth, HDFS client, servlet/Jersey, protobuf, Netty, logging, and tracing dependencies needed to run the doclet. Integration points are Hadoop's `dev-support/jdiff` checks plus downstream implementations of audit loggers, inode attribute providers, access-control enforcers, and JournalNode monitoring clients.

## Risks And Test Signals

Risks center on compatibility drift from 2.8.x and 2.9.2, or on treating the embedded build path as authoritative runtime configuration. Good test signals are XML well-formedness, the API name `Apache Hadoop HDFS 2.9.1`, unchanged method signatures against 2.9.2 when expected, and NameNode/JournalNode tests that exercise these extension hooks.
