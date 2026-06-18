# sources/distributed-fs/ceph-client/include/rdma/uverbs_types.h

Purpose: Defines the core uverbs object type classes, user file state, lookup modes, and allocation macros for IDR-backed and FD-backed RDMA userspace objects.

Important APIs/types/functions: `enum rdma_lookup_mode` distinguishes read, write, and destroy lookups. `struct uverbs_obj_type_class` defines callbacks for allocation, lookup, destroy, handle removal, and object swapping. `struct uverbs_obj_type`, `uverbs_obj_idr_type`, and `uverbs_obj_fd_type` specialize object storage. `struct ib_uverbs_file` owns context, async file, object lists, hw-destroy synchronization, mmap state, IDR xarray, and disassociation locking. Functions include lookup/allocation/commit/abort/assign, kref get/put, object locking, and FD release.

Control flow and state: Valid lifecycles are documented as allocate-begin/commit/abort, lookup-get/put, and destroy lookup/remove/put sequences. `hw_destroy_rwsem` coordinates hardware object teardown with object-list traversal. `ucontext_lock` protects context access, while the object list and xarray map user handles to `ib_uobject`s.

Dependencies and integration: Depends on RDMA verbs, Linux krefs, mutexes, rwsems, xarray, file operations, and uverbs API objects. It is the substrate used by `uverbs_ioctl.h` and `uverbs_std_types.h`.

Risks and test signals: Risks include violating documented lifecycle order, detaching objects concurrently with driver calls, incorrect lookup lock mode, FD close races, and disassociation cleanup. Tests should include parallel object lookup/destroy, FD object release, driver unload while userspace holds handles, context cleanup, and lockdep coverage of `hw_destroy_rwsem`.
