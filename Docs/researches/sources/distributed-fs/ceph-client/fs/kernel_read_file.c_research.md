<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernel_read_file.c -->
# sources/distributed-fs/ceph-client/fs/kernel_read_file.c

## Purpose
`kernel_read_file.c` provides generic helpers for reading regular files into kernel memory with LSM mediation. It supports direct `struct file` callers plus convenience wrappers for path, init namespace path, and file descriptor inputs.

## Important APIs, types, and functions
The exported functions are `kernel_read_file`, `kernel_read_file_from_path`, `kernel_read_file_from_path_initns`, and `kernel_read_file_from_fd`. Important dependencies are `kernel_read`, `deny_write_access/allow_write_access`, `security_kernel_read_file`, `security_kernel_post_read_file`, `vmalloc/vfree`, `filp_open`, `file_open_root`, `get_fs_root`, and the fd cleanup `CLASS(fd, f)` helper.

## Control flow
`kernel_read_file` rejects unsupported partial-read forms, non-regular files, write-access denial failures, empty files, files larger than `SSIZE_MAX`, and whole-file reads that cannot fit in the caller buffer. It asks LSMs whether the read may proceed, reports full file size if requested, allocates a vmalloc buffer when `*buf` is NULL, loops with `kernel_read` until the requested buffer size or EOF, and for whole-file reads verifies the final position reached `i_size` before calling post-read LSM hooks. On errors after internal allocation it frees the buffer and nulls the caller pointer. All exits release write denial.

Path wrappers validate nonempty paths, open the file, call the core helper, and drop the file. The init namespace wrapper obtains `init_task`'s root under task lock and opens relative to that root. The fd wrapper validates a readable fd and delegates.

## State and persistence behavior
The function has no persistent storage. Runtime side effects are temporary write denial on the file, optional vmalloc ownership transfer to the caller, LSM audit/measurement hooks, and file position via the local `pos` variable rather than changing `file->f_pos`.

## Dependencies and integration points
It is used by kernel subsystems that load firmware-like blobs, certificates, policies, or module-adjacent data and need a consistent LSM inspection point. The `enum kernel_read_file_id` classifies the read for security policy.

## Risks and test signals
Risks include stale `i_size` if files change during partial reads, pointer arithmetic on `void *` relying on kernel compiler behavior, whole-file post-read checks skipped for chunked reads, and cleanup ownership when callers pass preallocated buffers. Tests should cover LSM allow/deny and post-read denial, allocated versus caller buffers, partial offset reads, too-small buffers, empty/non-regular/huge files, fd mode validation, init namespace path resolution, and concurrent modification during reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/kernel_read_file.c -->
