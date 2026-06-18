<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso.h

Purpose: declares LoongArch vDSO image and mapping interfaces.
Important APIs and types: exposes vDSO symbol/page data, `vdso_init`, `arch_setup_additional_pages`, and constants for mapping vvar/vdso pages into userspace.
Control flow: exec/mmap setup maps the vDSO into new processes; time/signal code references vDSO entry points and data pages.
State and persistence: vDSO image pages and per-mm mappings persist for process lifetime; vvar data is updated by timekeeping.
Dependencies and integration: integrates with ELF auxvec `AT_SYSINFO_EHDR`, signal return, gettimeofday vDSO, time namespaces, and mm mapping code.
Risks and test signals: mapping or symbol errors break libc fast paths. Signals include `vdso_test`, clock_gettime/gettimeofday tests, signal return, ASLR, and auxvec validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso.h -->
