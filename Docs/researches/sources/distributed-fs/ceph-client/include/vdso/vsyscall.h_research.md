<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/vsyscall.h -->
# sources/distributed-fs/ceph-client/include/vdso/vsyscall.h

Purpose: exposes architecture-specific vDSO/vsyscall update hooks to generic kernel timekeeping code.

Important APIs and types: includes `asm/vdso/vsyscall.h` and declares `vdso_update_begin()` and `vdso_update_end(flags)`.

Control flow: kernel writers call begin before updating vDSO data and end afterward, with architecture code using the returned flags to restore interrupt/preemption or mapping state as needed.

State and persistence: no owned state; hooks protect updates to shared vDSO/VVAR state.

Dependencies and integration points: depends on arch vDSO vsyscall headers and integrates with timekeeping update paths.

Risks and test signals: risks include mismatched begin/end flags, arch missing hooks, and update ordering with sequence counters. Test timekeeping updates, suspend/resume clocksource changes, and arch vDSO builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/vsyscall.h -->
