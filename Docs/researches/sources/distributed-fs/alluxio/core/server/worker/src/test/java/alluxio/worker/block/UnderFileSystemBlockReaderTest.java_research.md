## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/UnderFileSystemBlockReaderTest.java

**Purpose:** Tests `UnderFileSystemBlockReader`, which reads UFS blocks and opportunistically caches fully read blocks into the local block store.

**Important APIs:** Exercises `UnderFileSystemBlockReader.create`, `read`, `transferTo`, `close`, `getLocation`, `LocalBlockStore.createBlock`, `requestSpace`, `commitBlock`, `pinBlock`, and metrics counters/meters for UFS bytes read.

**Control flow:** Setup writes a two-block increasing-byte UFS file, builds a local `TieredBlockStore`, UFS client, input-stream cache, open options, block meta, and metrics. Tests read full or partial ranges, overlap reads until a full block is covered, disable caching with `noCache`, inject local create/request-space failures, transfer to Netty `ByteBuf`, and validate the cached temp block after close.

**State and persistence:** Uses real UFS and local worker storage. Full reads should leave a temp block that can be committed and read locally; partial reads and cache failures should not leave local metadata.

**Dependencies and integration:** Integrates UFS client/cache, local block store, Netty pooled buffers, Alluxio metrics tags, byte-buffer utilities, and open UFS block options.

**Risks:** Partial coverage tracking and cache-on-close behavior are subtle. Cache failures must not break read success. Netty buffers require release to avoid leaks.

**Test signals:** Strong coverage for full/partial/offset/overlap reads, no-cache, local cache resource exhaustion, `transferTo`, local cached data correctness, and reader location.
