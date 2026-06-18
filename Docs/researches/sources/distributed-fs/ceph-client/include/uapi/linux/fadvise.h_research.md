# sources/distributed-fs/ceph-client/include/uapi/linux/fadvise.h

This header defines the Linux `posix_fadvise` advice constants shared by userspace and the kernel. It gives applications a way to describe expected file access patterns to the page cache and filesystem readahead logic.

Exports are `POSIX_FADV_NORMAL`, `POSIX_FADV_RANDOM`, `POSIX_FADV_SEQUENTIAL`, `POSIX_FADV_WILLNEED`, `POSIX_FADV_DONTNEED`, and `POSIX_FADV_NOREUSE`, with architecture-specific value handling where required by the UAPI.

Control flow is syscall driven: userspace calls `posix_fadvise`/`fadvise64` with an fd, offset, length, and advice; kernel/VFS applies cache, readahead, or eviction hints without changing file contents. State is transient page-cache/readahead state and file access heuristics. There is no persistent storage behavior, though `DONTNEED` may cause dirty pages to be written before cache eviction.

Dependencies are minimal and architecture UAPI glue supplies syscall ABI details. Integration points include libc wrappers, VFS page cache, readahead code, filesystem address-space operations, and performance-sensitive applications such as databases and backup tools.

Risks include applications treating hints as guarantees, performance regressions from inappropriate advice, arch value mismatches, and semantic changes to `NOREUSE`. Test signals include syscall ABI tests, cache/readahead behavior benchmarks, cross-arch header checks, and workloads validating that advice does not corrupt data or bypass required writeback.
