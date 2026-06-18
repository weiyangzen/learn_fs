# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/XAttrNotFoundException.java

## Purpose
`XAttrNotFoundException` is a specific `IOException` used when a requested extended attribute does not exist.

## Important APIs, Types, and Functions
The class defines `DEFAULT_EXCEPTION_MSG` as "At least one of the attributes provided was not found." The no-arg constructor uses that default, and the string constructor passes a custom message to `IOException`.

## Control Flow
There is no control flow beyond exception construction.

## State and Persistence Behavior
The only state is the inherited exception message and serial version UID. It is suitable for RPC propagation as an HDFS protocol exception type.

## Dependencies and Integration Points
It depends only on `IOException` and Hadoop interface annotations. It is used by xattr read/list paths in NameNode and client code to distinguish missing attributes from other I/O failures.

## Risks and Edge Cases
Callers that catch generic `IOException` can lose the specific "not found" signal. The default message intentionally handles one or more missing attributes, not a single named attribute.

## Test Signals
XAttr tests should assert the exception type and default/custom messages for missing extended attributes.
