<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/clocksource.h -->
# sources/distributed-fs/ceph-client/include/vdso/clocksource.h

Purpose: defines vDSO clock mode identifiers, including architecture clock modes and the special time-namespace marker.

Important APIs and types: `enum vdso_clock_mode` includes `VDSO_CLOCKMODE_NONE`, optional `VDSO_ARCH_CLOCKMODES`, `VDSO_CLOCKMODE_MAX`, and `VDSO_CLOCKMODE_TIMENS = INT_MAX`.

Control flow: vDSO readers inspect `vdso_clock.clock_mode` to decide whether a clocksource is usable in userspace, requires arch-specific handling, or is a time namespace indirection that must use the slow path.

State and persistence: no state here; values are stored in the VVAR `vdso_clock` data page by kernel timekeeping code.

Dependencies and integration points: depends on `vdso/limits.h` and optionally `asm/vdso/clocksource.h` under generic gettimeofday. It integrates with `vdso/helpers.h` and generic vDSO time code.

Risks and test signals: risks include arch enum collisions and incorrect time namespace detection. Test clock_gettime fast/slow paths with and without time namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/clocksource.h -->
