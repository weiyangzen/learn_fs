<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/auxclock.h -->
# sources/distributed-fs/ceph-client/include/vdso/auxclock.h

Purpose: provides the generic auxiliary clock resolution hook for vDSO time code.

Important APIs and types: `aux_clock_resolution_ns()` is an always-inline helper returning `1` nanosecond.

Control flow: vDSO clock_getres-style code can call this helper for auxiliary clocks when reporting resolution.

State and persistence: no state; the value is a compile-time generic resolution.

Dependencies and integration points: includes UAPI time and type headers and integrates with auxiliary vDSO clock support referenced by `vdso/datapage.h`.

Risks and test signals: risk is inaccurate generic resolution if an architecture-specific auxiliary clock needs different semantics. Test aux clock getres behavior and architecture overrides where present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/auxclock.h -->
