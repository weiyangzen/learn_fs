# sources/distributed-fs/ceph-client/fs/ecryptfs/kthread.c

## Purpose

`kthread.c` provides the eCryptfs helper kernel thread used to open lower files with read-write access when a direct open by the caller fails. This lets eCryptfs maintain a single lower file per upper inode and still obtain write-capable lower access for encrypted writeback when permitted.

## Important APIs, types, and functions

The file defines `struct ecryptfs_open_req`, static `ecryptfs_kthread_ctl`, and static `ecryptfs_kthread`. Exported functions are `ecryptfs_init_kthread()`, `ecryptfs_destroy_kthread()`, and `ecryptfs_privileged_open()`. The worker body is `ecryptfs_threadfn()`.

## Control flow

Initialization sets up the request-list mutex, waitqueue, and list head, then starts `ecryptfs-kthread`. The thread waits in a freezable wait loop until requests arrive or shutdown is requested. Each request contains a lower path, result pointer, completion, and list node. The thread removes requests from the queue, opens the lower path with `O_RDWR | O_LARGEFILE` using current credentials, stores the resulting `struct file *` or error pointer, and completes the request.

`ecryptfs_privileged_open()` first tries `dentry_open()` directly with `O_RDONLY` when the lower inode is read-only, otherwise `O_RDWR`. If direct read-write open fails, it queues a request to the helper thread, wakes it, and waits for completion. During shutdown, new requests are rejected and queued requests are completed with `ERR_PTR(-EIO)`.

## State and persistence behavior

There is no on-disk state. Runtime state is the global kthread, a guarded request queue, a zombie flag, and per-request completions. Successful opens create lower file references that are later closed by `ecryptfs_put_lower_file()` or directory release paths.

## Dependencies and integration points

The file depends on kthread, freezer, waitqueue, completion, mount/path, and VFS open APIs. `main.c` initializes and destroys the kthread at module load/unload. `main.c` lower-file lifetime code calls `ecryptfs_privileged_open()` through `ecryptfs_init_lower_file()`.

## Risks

Credential context is subtle: direct open uses the caller's supplied credentials, while queued opens occur in the helper thread using its current credentials. The request's `cred` parameter is not used in the queued path, which is intentional historical behavior but sensitive. Shutdown ordering must complete all queued requests before `kthread_stop()` to avoid waiters hanging. File reference ownership comments require matching `fput()` on lower-file release.

## Test signals

Signals include successful direct read-only and read-write lower opens, fallback queued open after direct write-open denial, concurrent opens on the same inode, module unload with pending requests, freezer interaction during suspend, and reference cleanup after open failure or delayed success.
