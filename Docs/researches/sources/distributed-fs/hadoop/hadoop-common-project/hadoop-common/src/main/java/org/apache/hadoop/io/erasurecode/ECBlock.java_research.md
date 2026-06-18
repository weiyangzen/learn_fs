# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ECBlock.java

Purpose: minimal block-level metadata wrapper for erasure coding, representing whether a block is parity and whether it is erased/missing.

Important APIs and control flow: constructors set `isParity` and `isErased`; setters and getters expose those flags. There is no validation or behavior beyond flag storage.

State and persistence: two mutable booleans, no persistence. It intentionally avoids HDFS block details so higher layers can subclass or wrap.

Dependencies and integration: used by `ECBlockGroup`, `BlockGrouper`, and coder step selection to identify input/output blocks.

Risks and test signals: tests should ensure erased/parity flags propagate into decoder output selection. Since fields are mutable, callers must avoid sharing instances across concurrent recovery calculations without coordination.
