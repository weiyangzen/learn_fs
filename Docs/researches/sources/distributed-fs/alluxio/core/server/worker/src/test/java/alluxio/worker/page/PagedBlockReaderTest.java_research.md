# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/PagedBlockReaderTest.java

Purpose: parameterized tests for `PagedBlockReader` reading block bytes through a cache manager and UFS-backed page reader.

Important APIs and helpers: parameters vary page size, buffer size, and block offset. Setup creates a temp UFS block with increasing bytes, mounts it in `UfsManager`, creates `PagedUfsBlockReader`, `PagedBlockMeta`, and `PagedBlockReader` with `ByteArrayCacheManager`. Tests cover one-shot sequential read, multi-round sequential reads, random reads to EOF, random jumping reads, and `transferTo`.

Control flow and state: reads request byte ranges from the block. The reader fetches pages through the cache manager, which loads from UFS on miss. Assertions validate returned `ByteBuffer`/Netty buffer contents against increasing-byte patterns and EOF behavior after full transfer.

Dependencies and integration: depends on page-store options, UFS block read options, `UfsInputStreamCache`, `ByteArrayCacheManager`, Netty `ByteBuf`, and local filesystem UFS.

Risks and test signals: strong for page-boundary and offset math. It avoids real local cache persistence by using in-memory cache, so page-store crash recovery is out of scope.
