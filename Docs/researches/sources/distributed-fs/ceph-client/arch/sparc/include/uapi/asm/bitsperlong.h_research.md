<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/bitsperlong.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/bitsperlong.h

Purpose: Selects the user-visible long width for SPARC ABIs.

Important APIs and control flow: when building for SPARC64 userspace (`__sparc__ && __arch64__`), `__BITS_PER_LONG` is 64. Otherwise the generic header supplies the 32-bit definition. This feeds time, socket, stat, and ioctl ABI conditionals.

State, dependencies, and risks: no runtime state. Dependencies are compiler ABI defines and `asm-generic/bitsperlong.h`. Risks are high for userspace ABI if the condition is wrong, particularly for time64 socket option selection and struct layouts. Test signals are 32-bit and 64-bit header compile tests and sizeof assertions for UAPI structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/bitsperlong.h -->
