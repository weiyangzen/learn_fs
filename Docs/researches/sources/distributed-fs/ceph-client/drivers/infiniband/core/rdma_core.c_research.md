# sources/distributed-fs/ceph-client/drivers/infiniband/core/rdma_core.c

## Purpose
`rdma_core.c` implements the user-verbs object lifetime engine. It provides common allocation, lookup, locking, commit, abort, destroy, FD release, and ufile teardown behavior for uverbs objects backed by IDR/XArray handles or anonymous file descriptors. This is the central control point that keeps user handles, hardware objects, resource cgroup charges, and device disassociation synchronized.

## Important APIs, types, and functions
- `uverbs_uobject_put()`, `uverbs_try_lock_object()`, and `rdma_lookup_put_uobject()` manage references and per-object access locking.
- `rdma_lookup_get_uobject()` resolves a user object by ID or FD and locks it for read/write/destroy.
- `rdma_alloc_begin_uobject()`, `rdma_alloc_commit_uobject()`, and `rdma_alloc_abort_uobject()` implement the transactional create path.
- `uobj_destroy()`, `__uobj_get_destroy()`, `__uobj_perform_destroy()`, and static `uverbs_destroy_uobject()` implement command-driven and cleanup-driven destruction.
- `uverbs_destroy_ufile_hw()` and helpers destroy all hardware state associated with an open uverbs file.
- Exported type-class instances `uverbs_idr_class` and `uverbs_fd_class` define the object-class operations.
- `rdma_uattrs_has_raw_cap()` checks whether the uverbs file’s RDMA device namespace has raw capability.

## Control flow and behavior
The create path obtains an `ib_ucontext` if needed, allocates a type-sized `ib_uobject`, starts it write-locked with `usecnt = -1`, reserves an XArray ID or FD, and charges rdmacg resources for IDR objects. Commit adds the object to `ufile->uobjects`, releases the write lock, stores the XArray pointer or installs the FD, and drops `hw_destroy_rwsem`. Abort destroys any valid hardware object, removes provisional handles, uncharges resources, and releases the original reference.

Lookup first obtains a kref under RCU/XArray or `fget()`, rejects stale or mismatched objects, blocks non-destroy operations once the uverbs device is disassociated, and then applies read/shared or write/exclusive locking through the atomic `usecnt`. Destroy removes or invalidates hardware via the object type class, clears context/object pointers, removes destroy handles when appropriate, unlinks from the ufile list, and balances krefs. Ufile teardown takes `hw_destroy_rwsem` for write, repeatedly attempts to destroy listed uobjects, uses a driver-failure fallback if cleanup cannot drain the list, then tears down the ucontext.

## State, persistence, and dependencies
Persistent in-kernel state includes `ufile->idr`, `ufile->uobjects`, per-object `usecnt`, `ref`, `context`, `object`, and type-class pointers. Synchronization uses RCU, `hw_destroy_rwsem`, `uobjects_lock`, XArray locking, file references, krefs, and atomic counters. Resource cgroup state is charged for HCA handles and IDR-backed objects. FD-backed objects additionally hold the uverbs file kref until file release.

## Integration points
The file integrates with `uverbs_ioctl` attribute bundles, uverbs object type classes from `<rdma/uverbs_types.h>`, ib_device driver callbacks for ucontext cleanup, mmap disassociation, anon inode FD installation, rdmacg accounting, SRCU device disassociation, and external command handlers that call `uverbs_get_uobject_from_file()` / `uverbs_finalize_object()`.

## Risks and test signals
Key risks are reference leaks, unbalanced `hw_destroy_rwsem`, object access after disassociation, double uncharge, FD release races, destroy paths leaving objects locked, and failure paths that commit objects when driver abort destruction fails. Test signals include KASAN/KCSAN/lockdep under parallel create/lookup/destroy, uverbs command tests for IDR and FD objects, device hot-unplug during active commands, rdmacg charge accounting tests, and fault injection around `xa_alloc`, `anon_inode_getfile`, driver `destroy_object`, and `ib_uverbs_get_ucontext_file()`.
