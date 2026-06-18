<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/auxvec.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/auxvec.h

Purpose: Defines x86-specific ELF auxiliary vector entries for vDSO/sysinfo discovery and the architecture aux-vector size budget.

Important APIs/types/functions: `AT_SYSINFO`, `AT_SYSINFO_EHDR`, and `AT_VECTOR_SIZE_ARCH`.

Control flow: ELF exec setup emits these auxiliary entries; userspace dynamic linkers and runtimes read them during process startup to locate vDSO or legacy vsyscall helpers.

State and persistence behavior: No persistent kernel state, but aux-vector contents are part of every process's initial userspace ABI.

Dependencies and integration points: Integrates with ELF binary loading, vDSO mapping, IA32 emulation, x32/non-compat x86-64 startup, and libc runtime initialization.

Risks and test signals: Risks include wrong aux-vector sizing for compat tasks and missing vDSO pointers. Test 32-bit, x32, and 64-bit process startup, `getauxval(AT_SYSINFO_EHDR)`, static and dynamic binaries, and IA32 emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/auxvec.h -->
