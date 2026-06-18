# sources/distributed-fs/coda/coda-src/vol/recov.h

Purpose: public interface for Coda recoverable storage volume operations.

Important APIs: initialization (`coda_init`), volume header creation/deletion/extraction (`NewVolHeader`, `DeleteVolume`, `DeleteRvmVolume`, `ExtractVolHeader`, `VolHeaderByIndex`), integrity checks, vnode extraction/replacement/growth, volume disk info read/write, vnode lookup/existence/count helpers, volume type/partition lookup, volume-cache setup, and max volume id allocation/get/set.

Control flow/state: callers operate over the RVM global volume list and class-local recoverable vnode lists. Mutators that change persistent structures are annotated as requiring transactions or excluding transactions when they manage their own transaction boundaries.

Dependencies/integration: depends on `volume.h` and Coda transaction annotations. It is consumed by volume attach/create/delete, salvage, dump tools, and vnode index wrappers. Risks include broad mutable API surface, mixed transaction ownership, and index/id confusion because many functions accept integer volume indexes and class-local vnode indexes. Test signals: first-time RVM init, new volume creation, vnode create/delete/replace, volume deletion, array growth, invalid index handling, and salvage recovery after interrupted transactions.
