## sources/distributed-fs/orangefs/src/client/usrint/request.c

Purpose: Converts POSIX `struct iovec` arrays into OrangeFS `PVFS_Request` memory datatypes for vector I/O.

Important APIs, types, and functions: `pvfs_convert_iovec` delegates to `pvfs_check_vector`. `pvfs_check_vector` builds arrays of block sizes, displacements, and child `PVFS_Request`s, coalescing runs of equal-length, equally-strided, non-overlapping iovec entries into `PVFS_Request_vector` requests and using `PVFS_BYTE` for singleton regions.

Control flow: The first iovec base becomes the memory request base returned in `*buf`. The loop groups adjacent vectors by equal `iov_len` and consistent positive stride. After grouping, `PVFS_Request_struct` combines the blocks, `PVFS_Request_commit` commits the result, and non-byte child requests are freed.

State and persistence: Allocates temporary arrays only. The returned `PVFS_Request` is caller-owned and must be freed by the caller.

Dependencies and integration points: Depends on `usrint.h`, PVFS request constructors, and POSIX `struct iovec`. Used by readv/writev-style usrint I/O paths.

Risks and test signals: The third allocation check mistakenly tests `disp_array` instead of `req_array`, so `req_array` allocation failure can lead to `memset(NULL, ...)`. It assumes ascending iovec bases; negative address deltas are cast into `PVFS_size`. It does not check PVFS request-constructor return codes. Test empty vectors, singleton vectors, strided runs, unequal lengths, overlapping buffers, descending buffers, allocation failures, and request-free discipline.
