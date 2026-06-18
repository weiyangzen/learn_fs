# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/UfsBlockReadOptions.java

## Purpose
`UfsBlockReadOptions` is an immutable value object describing how to read a block from UFS: mount ID, offset within the UFS file, UFS path, whether to cache into Alluxio, and optional user.

## Important APIs, Types, and Functions
`fromProto()` validates required mount ID, offset, and UFS path, then converts `noCache` to `cacheIntoAlluxio`. Accessors expose each field. `equals()` and `hashCode()` include mount ID, offset, path, and cache flag, but not user.

## Control Flow, State, and Persistence
The object performs no IO. It controls how `PagedUfsBlockReader` opens UFS streams and whether `PagedBlockReader` caches fetched pages.

## Dependencies and Integration Points
It depends on protobuf `Protocol.OpenUfsBlockOptions` and is used by `PagedBlockStore`, `PagedBlockReader`, and `PagedUfsBlockReader`.

## Risks and Test Signals
Risks include `getUser()` returning nullable as a plain `String`, equality ignoring user despite metrics depending on user, and callers swallowing missing-option errors for MUST_CACHE-like paths. Tests should cover required-field validation, no-cache inversion, nullable user, and equality semantics.
