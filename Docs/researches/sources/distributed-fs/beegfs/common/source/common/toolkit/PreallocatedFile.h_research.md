<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/PreallocatedFile.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/PreallocatedFile.h

**Purpose:** Provides a template for fixed-size, preallocated on-disk storage of one serializable value with a one-byte validity tag, intended for writes that should not fail for lack of space inside the allocated range.

**Important APIs/types/functions:** `detail::PreallocatedFileDefaultSize<T>` defaults size to `sizeof(T)` for trivial types. `PreallocatedFile<T, Size>` exposes a constructor, `write(const T&)`, and `read() const` returning `boost::optional<T>`.

**Control flow:** Construction opens/creates the file read-write and calls `posix_fallocate` for `Size + 1`. `write` serializes into a stack buffer at offset 1, sets tag byte 1, validates serializer success, and `pwrite`s the full fixed region. `read` `pread`s the full fixed region; tag byte 0 returns `boost::none`, otherwise the remaining bytes are deserialized into `T`.

**State and persistence behavior:** Persists a fixed-size file. Byte 0 is validity state; bytes 1..Size contain serialized object data. Writes are not fsynced, so persistence across power loss depends on caller/fsync policy.

**Dependencies and integration points:** Uses `FDHandle`, BeeGFS `Serializer`/`Deserializer`, `boost::optional`, POSIX `open`, `posix_fallocate`, `pwrite`, and `pread`. Tests in this subset cover allocation and read/write behavior.

**Risks:** The buffer is stack-allocated, so large `Size` can overflow stacks. Serialization larger than `Size` throws. Short reads/writes are treated as system errors using current `errno`, which may not fully describe partial I/O. Network filesystems may violate the preallocation guarantees described in the comments.

**Test signals:** `TestPreallocatedFile.cpp` verifies allocated size/blocks, large allocation failure, successful `uint64_t` write/read, too-small buffer failure, empty-file optional behavior, and truncated-file read failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/PreallocatedFile.h -->
