<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/time32.h -->
# sources/distributed-fs/ceph-client/include/vdso/time32.h

Purpose: defines 32-bit legacy time types used by compat vDSO entry points.

Important APIs and types: `old_time32_t`, `old_timespec32`, and `old_timeval32` model signed 32-bit seconds plus nanosecond or microsecond subfields.

Control flow: 32-bit vDSO `clock_gettime`, `clock_getres`, and `gettimeofday` variants fill these structures for legacy ABIs.

State and persistence: no state; ABI type definitions only.

Dependencies and integration points: relies on `s32` being available from include context. It integrates with compat vDSO and Y2038 transition code.

Risks and test signals: risks include Y2038 overflow, missing type includes, and wrong prototype selection. Test 32-bit vDSO calls near overflow boundaries and compat libc behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/time32.h -->
