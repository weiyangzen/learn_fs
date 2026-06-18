# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/server/datanode/ReplicaNotFoundException.java

Purpose: `ReplicaNotFoundException` is a DataNode-side `IOException` that signals a requested block replica is absent or not in the expected state for append/recovery operations.

Important APIs/types/functions: it exposes standard message constants for non-RBW, unfinalized, non-existent, and unexpected-generation-stamp replicas. The `ExtendedBlock` constructor builds a user-oriented message including `POSSIBLE_ROOT_CAUSE_MSG`, which points at benign balancer/removal scenarios and advises log inspection. A default constructor and raw-message constructor support generic IOException usage.

Control flow: callers throw this exception when a block lookup or state check fails. The exception itself contains no branching beyond message construction; downstream control is in DataNode/DFSClient recovery code that treats it as an I/O failure.

State and persistence behavior: immutable exception state is carried in the inherited message/cause fields. The static message constants are part of the diagnostic contract used by callers and tests.

Dependencies and integration points: depends on `ExtendedBlock` from HDFS protocol. It integrates with block append, recovery, and replica lookup paths in the DataNode.

Risks and test signals: message text is operationally significant because admins and tests may match it. Tests should assert construction with `ExtendedBlock`, preservation of provided custom messages, and inclusion of the possible-root-cause hint for block-based construction.
