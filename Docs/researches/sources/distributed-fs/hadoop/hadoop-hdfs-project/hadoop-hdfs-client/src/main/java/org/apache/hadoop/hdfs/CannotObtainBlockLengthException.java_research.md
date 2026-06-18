# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/CannotObtainBlockLengthException.java

Purpose: public unstable `IOException` indicating that a `LocatedBlock` length could not be obtained.

Important APIs and functions: constructors support no-arg, message-only, located-block, and located-block-with-source-file variants.

Control flow and state: no custom behavior beyond message construction. `serialVersionUID` is fixed.

Dependencies and integration: integrates with HDFS protocol `LocatedBlock` and read/status code that needs block length metadata.

Risks and test signals: message constructors include the block and optional file path, improving diagnostics. No direct tests in this subset.
