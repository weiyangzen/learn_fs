# sources/distributed-fs/coda/coda-src/vol/index.h

Purpose: declares the recoverable vnode index abstraction used by the volume layer.

Important types/APIs: `vindex` exposes slot counts, allocated counts, empty checks, id-based and offset-based get/put operations. `vindex_iterator` exposes `operator()(VnodeDiskObject *)`, returning the current recoverable vnode index or `-1` at end. Write operations are annotated as requiring a transaction.

Control flow/state: `vindex` is a lightweight handle over a `VolumeId` and vnode class rather than owning storage. `vindex_iterator` owns a `rec_smolist_iterator` and walks one recoverable slot list at a time.

Dependencies/integration: depends on `VolumeId`, `Device`, `VnodeId`, `Unique_t`, `VnodeDiskObject`, `bit32`, and recoverable-list classes from the volume headers. Risks include public declaration of `operator=` without implementation, implicit default constructor values of `-1`, and caller responsibility for buffer size. Test signals: compile users in volume/dump/salvage paths and verify transaction enforcement around `put`/`oput`.
