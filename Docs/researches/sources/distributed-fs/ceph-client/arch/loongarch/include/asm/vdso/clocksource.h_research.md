<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/clocksource.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/clocksource.h

Purpose: selects LoongArch vDSO clocksource mode definitions.
Important APIs and types: includes generic vDSO clocksource definitions and maps architecture mode constants.
Control flow: no local runtime flow; vDSO time code switches behavior based on clocksource mode.
State and persistence: mode fields are stored in vDSO data and read from userspace.
Dependencies and integration: integrates with LoongArch counter reads, generic vDSO timekeeping, and clocksource registration.
Risks and test signals: wrong mode selection sends userspace down invalid time paths. Signals include vDSO clocksource tests and clocksource watchdog behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/clocksource.h -->
