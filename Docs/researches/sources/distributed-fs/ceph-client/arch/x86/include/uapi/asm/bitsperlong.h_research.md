<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/bitsperlong.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/bitsperlong.h

Purpose: Selects `__BITS_PER_LONG` for x86 UAPI based on compiler target ABI, using 64 for normal x86_64 and 32 for i386 or x32 ILP32.

Important APIs/types/functions: `__BITS_PER_LONG` and inclusion of `asm-generic/bitsperlong.h`.

Control flow: Header preprocessing branches on `__x86_64__` and `__ILP32__`; there is no runtime flow.

State and persistence behavior: No runtime state. The selected value affects userspace-visible type widths and ABI structure layouts.

Dependencies and integration points: Integrated with all UAPI headers that use `long`-dependent generic types, including IPC, stat, signal, and syscall data structures.

Risks and test signals: Risks are x32 being treated as 64-bit long or cross-compiler macro mismatches. Test headers with i386, x86_64, and x32 toolchains and compile-time assertions for `sizeof(long)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/bitsperlong.h -->
