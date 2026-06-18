<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/hwcap.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/hwcap.h

Purpose: defines LoongArch hardware capability bits advertised to userspace.
Important APIs and types: `HWCAP_LOONGARCH_*` bits cover CPUCFG, LAM, UAL, FPU, LSX, LASX, CRC32, complex/crypto instructions, LVZ, binary translation extensions, PTW, LSPW, SCQ, and LAM_BH.
Control flow: CPU probe sets matching bits in `elf_hwcap`; ELF exec exposes them through auxvec for libc and applications.
State and persistence: HWCAP bits are user ABI and must remain stable once assigned.
Dependencies and integration: tied to `cpu-probe.c`, ELF auxvec, libc feature detection, JITs, crypto libraries, and vector code dispatch.
Risks and test signals: advertising unsupported features causes illegal instructions; hiding features reduces performance. Signals include CPU feature probes, auxvec checks, vector/FPU tests, and userspace dispatch validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/hwcap.h -->
