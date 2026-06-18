<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/ktime.h -->
# sources/distributed-fs/ceph-client/include/vdso/ktime.h

Purpose: exposes low-resolution kernel time constants for vDSO-compatible code.

Important APIs and types: `LOW_RES_NSEC` and `KTIME_LOW_RES` both map to `TICK_NSEC`.

Control flow: vDSO getres paths can use these constants for coarse/low-resolution clocks.

State and persistence: no state.

Dependencies and integration points: depends on `vdso/jiffies.h`; integrates with generic vDSO time code.

Risks and test signals: risk is limited to mismatch with kernel clock resolution. Test clock_getres coarse/low-res outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/ktime.h -->
