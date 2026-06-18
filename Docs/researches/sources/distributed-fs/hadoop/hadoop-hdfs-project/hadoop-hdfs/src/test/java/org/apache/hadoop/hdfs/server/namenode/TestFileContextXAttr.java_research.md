<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFileContextXAttr.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFileContextXAttr.java

Purpose: `TestFileContextXAttr` reruns the shared XAttr base suite through `FileContext` XAttr APIs, checking parity with the normal HDFS client API for set, get, list, and remove extended attributes.

Important APIs, types, and functions: it extends `FSXAttrBaseTest`, overrides `createFileSystem`, and defines `FileContextFS extends DistributedFileSystem`. Overridden methods delegate `setXAttr` with and without flags, `getXAttr`, `getXAttrs`, `getXAttrs(names)`, and `removeXAttr` to a `FileContext` created at initialization.

Control flow: inherited XAttr tests receive the adapter filesystem. General filesystem setup and non-XAttr calls use `DistributedFileSystem`; XAttr-specific calls are routed to `FileContext`, exercising that API path against the same mini cluster and namespace.

State and persistence behavior: state is HDFS inode XAttr metadata manipulated by inherited tests. This class contributes no direct persistence checks beyond whatever `FSXAttrBaseTest` performs; it focuses on API equivalence.

Dependencies and integration points: depends on `FSXAttrBaseTest`, `FileContext`, `XAttrSetFlag`, `DistributedFileSystem`, and the NameNode XAttr implementation.

Risks and edge cases: like the ACL adapter, it is only a partial facade. Any un-overridden XAttr overload would bypass the FileContext path if added to the base suite. The class assumes base static configuration/cluster setup is already supplied by `FSXAttrBaseTest`.

Test signals: inherited XAttr tests pass while XAttr operations delegate through `FileContext`, confirming FileContext behavior for the covered overloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFileContextXAttr.java -->
