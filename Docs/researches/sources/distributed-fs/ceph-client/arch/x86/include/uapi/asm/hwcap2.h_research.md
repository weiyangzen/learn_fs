<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/hwcap2.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/hwcap2.h

Purpose: Defines x86 `AT_HWCAP2` feature bits exposed to userspace for ring-3 MONITOR/MWAIT and FSGSBASE availability.

Important APIs/types/functions: `HWCAP2_RING3MWAIT` and `HWCAP2_FSGSBASE`.

Control flow: CPU feature setup and ELF aux-vector code set these bits; userspace checks them before executing corresponding instructions.

State and persistence behavior: No private state. Values are process-visible feature bits in the auxiliary vector.

Dependencies and integration points: Depends on Linux bit constants. Integrates with CPU feature detection, ELF auxvec, libc/runtime feature dispatch, and instruction emulation policies.

Risks and test signals: Risks include exposing bits when the kernel has disabled user access or withholding bits when safe. Test `getauxval(AT_HWCAP2)`, user FSGSBASE instructions, ring-3 MWAIT policy, and CPU feature toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/hwcap2.h -->
