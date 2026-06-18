# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/io/MetricAccountingBlockReader.java

Purpose: Decorates a `BlockReader` to increment cache read byte metrics for every read path.

Important APIs: Overrides `read`, `getChannel`, `transferTo`, `getLength`, `isClosed`, `getLocation`, `toString`, and `close`.

Control flow: `read` counts bytes remaining in the returned `ByteBuffer`; wrapped channel counts successful `read` byte counts; `transferTo` counts non-EOF byte counts. Other methods delegate.

State and persistence: Holds one delegate reader. Metrics are emitted to `MetricsSystem`; no local persistence.

Dependencies and integration: Uses `MetricKey.WORKER_BYTES_READ_CACHE`, Netty `ByteBuf`, and Java NIO channels. It integrates with block reader creation paths that want cache metrics.

Risks and test signals: ByteBuffer position/limit assumptions determine counted bytes. Tests should cover EOF `-1`, partial channel reads, transferTo EOF, close delegation, and that counting does not double count across APIs.
