<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/time64.h -->
# sources/distributed-fs/ceph-client/include/vdso/time64.h

Purpose: provides time unit conversion constants for vDSO and lightweight kernel time code.

Important APIs and types: defines milliseconds, microseconds, nanoseconds, picoseconds, and femtoseconds per second or smaller unit constants.

Control flow: vDSO helpers and tick constants use these values for clock resolution and conversion.

State and persistence: no state; constants only.

Dependencies and integration points: standalone; used by `vdso/jiffies.h` and time conversion code.

Risks and test signals: low risk; test is compile-time use and unit conversion consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/time64.h -->
