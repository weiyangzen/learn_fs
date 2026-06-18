# sources/distributed-fs/openafs/src/config/icl.h

Purpose: public/private definitions for the OpenAFS in-core logging (ICL) tracing package.

Important APIs/types/functions: defines `struct afs_icl_set`, `struct afs_icl_log`, set/log flags, default log sizes, syscall operation numbers `ICL_OP_*`, trace macros `afs_Trace0` through `afs_Trace4`, parameter types such as `ICL_TYPE_STRING`, `ICL_TYPE_FID`, and `ICL_TYPE_INT64`, size macro `ICL_SIZEHACK`, create flags, copyout flags, lock aliases, global ICL lists/locks, and error/info constants.

Control flow: trace macros check whether a set is active via `ICL_SETACTIVE` and call the corresponding `afs_icl_Event*` function with packed parameter-type bits. ICL syscall operation constants drive control paths in fstrace/kernel handlers for copyout, clear, enumerate, set status, resize, and version queries.

State and persistence: declares global in-memory state for all logs and sets: refcounts, locks, linked lists, circular log buffers, event flags, timestamps, and cookies. Persistent flags mark long-lived sets/logs in memory; the header itself writes no storage.

Dependencies and integration: included by kernel and user-space tracing code. Kernel builds include `afs/param.h`, `afs_osi.h`, `afs/lock.h`, and generated trace IDs; user builds use `afs/afs_lock.h`.

Risks and test signals: risks include ABI/layout drift for fstrace copyout, long-size differences captured by `ICL_LONG` and `afs_icl_sizeofLong`, packed parameter-type overflow, and disabled/default state surprises. Signals are fstrace event creation, copyout/clear operations, 32/64-bit offset tracing, string/FID formatting, and concurrent log/set refcount tests.
