<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/special_insns.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/special_insns.h

Purpose: provides inline wrappers for privileged and special x86 instructions. Important APIs include CR0/CR2/CR3/CR4 read/write helpers, native CR variants, `wbinvd()`, `clflush*`, `stts()/clts()`, `native_halt()`, `safe_halt()`, `rdpkru()/wrpkru()`, `serialize()`, `mwait/monitor`, `tile_release()`, and related feature-conditional helpers.

Control flow: low-level kernel code uses wrappers to manipulate control registers, cache state, protection keys, halt/mwait idle, and serialization. Alternative patching or paravirt can replace some operations; callers handle feature checks.

State and persistence: mutates CPU control registers, TLB/cache state, PKRU, TS bit, and idle state. Dependencies include processor flags, barriers, paravirt, CPU features, and asm constraints. Risks are severe: wrong control-register writes can crash the CPU; missing memory clobbers or ordering can corrupt page-table/security state. Test signals include boot, CPU hotplug, idle, cache flush, PKU selftests, CR4 shadow tests, and objtool/compiler validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/special_insns.h -->
