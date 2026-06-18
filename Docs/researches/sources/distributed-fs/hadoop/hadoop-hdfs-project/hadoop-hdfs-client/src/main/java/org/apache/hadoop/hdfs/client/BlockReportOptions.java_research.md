# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/client/BlockReportOptions.java

Purpose: `BlockReportOptions` is a public evolving immutable value object for manually triggering DataNode block reports with optional incremental mode and optional NameNode target address.

Important APIs/types/functions: fields are `incremental` and `namenodeAddr`. Accessors are `isIncremental()` and `getNamenodeAddr()`. Nested `Factory` provides `setIncremental(boolean)`, `setNamenodeAddr(InetSocketAddress)`, and `build()`. `toString()` exposes both fields for diagnostics.

Control flow: callers create a `Factory`, mutate builder fields, and call `build()`, which invokes the private constructor. Defaults are full block report (`incremental=false`) and no explicit NameNode address.

State and persistence behavior: `BlockReportOptions` instances are immutable references after construction. The builder is mutable and reusable. There is no persistence in this class.

Dependencies and integration points: depends on `InetSocketAddress` and Hadoop audience/stability annotations. It integrates with HDFS administrative paths that trigger block reports against DataNodes/NameNodes.

Risks: no validation is performed for the NameNode address; downstream code must handle null or unresolved addresses. Tests should verify defaults, builder mutation, immutability of produced options relative to later builder changes, and `toString()` content.
