# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockWriter.java

## Purpose
`PagedBlockWriter` implements `BlockWriter` by appending block bytes into temporary cache pages.

## Important APIs, Types, and Functions
`append(ByteBuffer)` and `append(ByteBuf)` split incoming bytes across page boundaries, create `BlockPageId.newTempPage` IDs, and call `CacheManager.append` with a temporary cache context. `append(DataBuffer)` prefers a Netty `ByteBuf` output and falls back to a read-only `ByteBuffer`. `getPosition()` returns bytes written; `getChannel()` is unsupported.

## Control Flow, State, and Persistence
The writer tracks `mPosition` and advances it after successful appends. Page bytes are persisted through the cache manager into temp page files. Final commit is handled by `PagedBlockStore`/`PagedBlockMetaStore`, not the writer.

## Dependencies and Integration Points
It depends on `CacheManager`, `BlockPageId`, `CacheContext`, `DataBuffer`, Netty `ByteBuf`, and `BlockWriter`.

## Risks and Test Signals
Risks include per-page byte-array copies, no `close()` override, unsupported channel access, append failure after partial page writes, and reliance on `DataBuffer.getNettyOutput()` casting. Tests should cover page boundary writes, ByteBuf and ByteBuffer paths, fallback path, append failure, and position accounting.
