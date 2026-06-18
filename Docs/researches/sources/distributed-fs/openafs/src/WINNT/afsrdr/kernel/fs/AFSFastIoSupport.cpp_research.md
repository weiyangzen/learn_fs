# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/fs/AFSFastIoSupport.cpp

Purpose: supplies the driver fast-I/O callback routines and cache-manager locking callbacks. Most data fast paths deliberately return `FALSE`, forcing normal IRP processing, while acquire/release callbacks coordinate FCB, paging, and section-object resources.

Important APIs/types/functions: `AFSFastIoCheckIfPossible()`, read/write/info/lock/unlock/devctl/network-open/MDL/compressed/query-open callbacks return `FALSE`. `AFSFastIoAcquireFile()` takes FCB and section-object resources exclusively and references the section-create file object. `AFSFastIoReleaseFile()` releases those resources and dereferences saved file objects. `AFSFastIoAcquireForCCFlush()` and `AFSFastIoReleaseForCCFlush()` coordinate paging and section-object locks for cache flush. Cache-manager callback analogs in `AFSGeneric.cpp` handle lazy write and read ahead.

Control flow: direct fast-I/O callbacks are stubs that decline the fast path. Acquire callbacks assume `FileObject->FsContext` is an `AFSFcb`, acquire resources with `AFSAcquire*()`, set `FSRTL_CACHE_TOP_LEVEL_IRP` when needed, and release in reverse-like order. `AFSFastIoAcquireFile()` stores `SectionCreateFO` only if not already set and references it until release.

State/persistence: mutates in-memory FCB resources and `Specific.File.SectionCreateFO`. It also manipulates the thread's top-level IRP marker for cache-manager recursion control. No durable persistence.

Dependencies/integration: relies on FCB/NPFcb structures from `AFSCommon.h`, resource wrappers in `AFSGeneric.cpp`, Cache Manager (`CcGetFileObjectFromSectionPtrs`), object reference APIs, and the `FAST_IO_DISPATCH` table declared in `AFSData.cpp`.

Risks: fast I/O stub returns protect correctness by avoiding unsupported direct paths, but they can cost performance. Acquire/release imbalance can deadlock cache manager paths. `AFSFastIoAcquireForCCFlush()` checks `SectionObjectResource` shared state and then acquires exclusive or shared, so resource recursion/ownership semantics matter. `FileObject->FsContext` must be a valid file FCB, not a redirector root/control flag.

Test signals: verify every unsupported fast callback returns `FALSE`; stress cache flush/lazy-write/read-ahead with concurrent close/cleanup; validate no leaked `SectionCreateFO` references; assert top-level IRP is set and cleared; run Driver Verifier-style resource tracking for acquire/release symmetry.
