<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/arch_data.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/arch_data.h

Purpose: defines LoongArch architecture-specific data embedded in vDSO/vvar pages.
Important APIs and types: provides `struct arch_vdso_data` fields used by vDSO time routines, notably counter/timer configuration and clocksource mode data.
Control flow: kernel timekeeping updates vvar data; vDSO userspace routines read it without syscalls.
State and persistence: fields persist in read-only/shared vvar mappings visible to user processes.
Dependencies and integration: used by generic vDSO data structures, `gettimeofday.h`, timer/clocksource code, and libc clock fast paths.
Risks and test signals: ABI/layout changes break existing vDSO code. Signals include vDSO clock tests, compat with libc, and time namespace validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/arch_data.h -->
