# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/ReplicaAccessor.java

Purpose: `ReplicaAccessor` is a public stable plugin API that lets external code provide direct access to an HDFS block replica, bypassing normal `BlockReader` construction when a specialized local, hardware, or network path is available.

Important APIs/types/functions: implementations must provide positional `read(long pos, byte[] buf, int off, int len)`, positional `read(long pos, ByteBuffer buf)`, `close()`, `isLocal()`, and `isShortCircuit()`. The default `getNetworkDistance()` returns `0` for local access and `Integer.MAX_VALUE` otherwise.

Control flow: the API is pull based. HDFS builds an accessor through `ReplicaAccessorBuilder`, wraps it in `ExternalBlockReader`, and calls positional reads. The contract says reads return a full requested count unless EOF is reached, and return `-1` only when no bytes can be returned at EOF. `close()` should leave the accessor closed even if it throws.

State and persistence behavior: this abstract class has no fields, but implementors commonly hold file descriptors, device handles, or network resources. The visible length is supplied at build time, so implementations should not expose bytes appended later unless reopened through HDFS.

Dependencies and integration points: `BlockReaderFactory.tryToCreateExternalBlockReader()` constructs plugin builders configured through `dfs.client.replica.accessor.builder.classes` and wraps successful `ReplicaAccessor` instances. The API contributes local, short-circuit, and network-distance read statistics through `isLocal`, `isShortCircuit`, and `getNetworkDistance`.

Risks: incorrect EOF semantics can break HDFS read loops that expect no short reads before EOF. ByteBuffer implementations must advance buffer position consistently. Resource leaks are possible if `close()` throws before cleanup. Tests should validate EOF behavior, byte-array and ByteBuffer parity, statistics classification, network-distance override behavior, and cleanup on caller exceptions.
