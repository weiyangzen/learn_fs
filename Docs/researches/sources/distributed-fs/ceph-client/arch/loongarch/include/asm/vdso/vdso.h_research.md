<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/vdso.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/vdso.h

Purpose: defines LoongArch vDSO architecture glue for generic vDSO headers.
Important APIs and types: provides vDSO page, symbol, and data access conventions used by architecture and generic code.
Control flow: build and runtime mapping code use these definitions to expose the vDSO image to processes.
State and persistence: describes persistent vDSO image/data placement but does not own mutable state.
Dependencies and integration: integrates with ELF aux vectors, `vdso.h`, time vDSO, signal return, and mm additional-page setup.
Risks and test signals: symbol/page alignment mistakes break userspace vDSO discovery. Signals include auxvec inspection, vDSO selftests, and libc clock/signal tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/vdso.h -->
