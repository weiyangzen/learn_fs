<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/module.mk.in -->
# sources/distributed-fs/orangefs/src/common/mgmt/module.mk.in

Purpose: build fragment for the OrangeFS common management subsystem. It enumerates the source files that implement operation management, queues, completion contexts, and worker models.

Important variables: `DIR := src/common/mgmt`; `MGMT_SRC` includes `pint-op.c`, `pint-queue.c`, `pint-mgmt.c`, `pint-context.c`, the queue/threaded queue workers, blocking worker, per-operation worker, pool placeholder, and external worker. `LIBSRC` and `SERVERSRC` both append `MGMT_SRC`, which means these abstractions are available in common library code and server-side code.

Control flow is build-time source aggregation only. There is no runtime state, but this file is the integration point that binds together otherwise separate worker implementations behind the `PINT_worker_impl` vtable contract.

Dependencies are the repository's make include convention and the variables consumed by higher-level build rules. It deliberately excludes `pint-worker-none.c`, suggesting that file is an obsolete or non-built prototype rather than an active implementation.

Risks: because all active worker variants are compiled into both library and server artifacts, ABI or compile errors in an experimental implementation can break broad builds even if the type is not used at runtime. `pint-worker-pool.c` is compiled but has no implementation callbacks, while `PINT_manager_worker_add()` returns `-PVFS_ENOSYS` for pool workers, so tests should confirm this unsupported path fails predictably. Build tests should verify clean compilation with pthread support and all active management headers included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/mgmt/module.mk.in -->
