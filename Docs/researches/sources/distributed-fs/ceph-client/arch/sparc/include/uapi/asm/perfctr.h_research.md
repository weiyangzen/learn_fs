<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/perfctr.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/perfctr.h

Purpose: Historical UltraSPARC `sys_perfctr()` ABI definitions, retained even though perf events superseded the syscall.

Important APIs and control flow: `enum perfctr_opcode` defines enable, disable, read, clear PIC, set PCR, and get PCR operations. Comments document that user pointers refer to 64-bit accumulators/PCR values and that enabled counter state followed fork/clone until exec or explicit disable. The header also defines privilege/user/system mode bits, Ultra-I/II and Ultra-III PIC event encodings for both counter fields, and `vcounter_struct`.

State, dependencies, and risks: state would be per-process performance counter accumulator pointers and PCR/PIC registers in legacy kernels. Dependencies are UltraSPARC PCR/PIC hardware and old syscall implementations. Risks are stale ABI consumers, unsafe user pointers in historical implementations, and event encoding differences across CPU generations. Test signals are mostly compile compatibility now; on old support trees, counter enable/read/clear and fork/exec retention are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/perfctr.h -->
