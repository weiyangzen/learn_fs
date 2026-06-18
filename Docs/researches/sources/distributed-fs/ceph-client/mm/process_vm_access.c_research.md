# sources/distributed-fs/ceph-client/mm/process_vm_access.c

## Purpose
`process_vm_access.c` implements the `process_vm_readv(2)` and `process_vm_writev(2)` system calls. These calls copy bytes directly between the calling process and another process address space using local and remote iovec arrays, avoiding an intermediate pipe or ptrace data loop. The code is generic process-memory access infrastructure, not filesystem-specific.

## Important APIs, Types, and Functions
The syscall entry points are `SYSCALL_DEFINE6(process_vm_readv, ...)` and `SYSCALL_DEFINE6(process_vm_writev, ...)`, both delegating to `process_vm_rw()`. `process_vm_rw()` imports the local iovec into an `iov_iter`, imports the remote iovec array, validates that flags are zero, and calls `process_vm_rw_core()`.

`process_vm_rw_core()` resolves the target task by PID, performs ptrace-style permission checks through `mm_access(task, PTRACE_MODE_ATTACH_REALCREDS)`, sizes a temporary `struct page *` array, and iterates each remote vector. `process_vm_rw_single_vec()` pins remote pages with `pin_user_pages_remote()`, copies each batch through `process_vm_rw_pages()`, unpins pages, and dirties them for writes with `unpin_user_pages_dirty_lock()`. `process_vm_rw_pages()` performs the actual page-to-iterator or iterator-to-page copy with `copy_page_to_iter()` and `copy_page_from_iter()`.

## Control Flow
The syscall path first rejects nonzero flags with `-EINVAL`. The local iovec is imported as `ITER_DEST` for reads from the target process and `ITER_SOURCE` for writes to the target process. Empty local iterators short-circuit successfully. The remote iovec is copied from userspace, with compat handling when needed.

Core execution computes the largest number of remote pages needed by any remote iovec. It uses a stack page-pointer array for small batches and kmallocs at most two pages of pointer storage for larger requests. After task lookup and permission checks, each remote iovec is processed until the local iterator is exhausted or an error occurs. For each remote range, the code computes the starting page, offset, and number of pages; pins pages in bounded batches under the remote mmap read lock; copies bytes page by page; advances address and offsets; and unpins. If any bytes were copied before an error, the syscall returns the partial byte count rather than the error.

## State and Persistence Behavior
The code has no persistent state. It temporarily pins remote pages, maps local iovec state in an `iov_iter`, holds task and mm references, and optionally dirties remote pages on writes. Writes persist only as normal modifications to the remote process memory and its backing pages; file-backed shared mappings may later participate in normal dirty/writeback behavior through generic MM mechanisms. All temporary page pins and references are released before returning.

## Dependencies and Integration Points
Dependencies include the syscall layer, iovec import helpers, `iov_iter`, task lookup/refcounting, ptrace permission checks, `mm_access()`, remote GUP (`pin_user_pages_remote()`), highmem-safe page copy helpers, and dirty unpin helpers. The integration point for filesystems is indirect: if the target memory is a writable shared file mapping, dirtying and later writeback are handled by generic MM and the underlying filesystem.

## Risks and Edge Cases
The main externally visible semantics are partial transfer and error mapping. A short copy due to a later bad remote address returns the bytes copied so far. Permission failures from `mm_access()` map `-EACCES` to `-EPERM`. Remote pages can disappear between vector validation and pinning, producing `-EFAULT`. The temporary page-pointer array is deliberately bounded for reliability. Write mode must pass `FOLL_WRITE` and dirty pages on unpin; failing to dirty would lose writes to file-backed mappings. Holding and releasing the remote mmap lock follows `pin_user_pages_remote()`'s `locked` protocol.

## Test Signals
Useful tests include same-process and cross-process read/write, invalid flags, invalid local and remote iovecs, zero-length vectors, permission-denied targets, exited target tasks, remote unmapped pages mid-vector, partial transfers over multiple iovecs, writes to private anonymous memory, writes to shared file mappings with dirty propagation, large vectors that force kmalloc pointer storage, compat syscall coverage, and stress with concurrent unmap/mprotect in the target process.
