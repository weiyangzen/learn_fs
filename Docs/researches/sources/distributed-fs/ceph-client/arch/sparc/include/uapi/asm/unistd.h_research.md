<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/unistd.h

Purpose: Selects generated SPARC syscall-number headers and exposes SPARC kernel feature bits.

Important APIs and control flow: defines `__32bit_syscall_numbers__` for non-`__arch64__` builds, includes `unistd_64.h` or `unistd_32.h`, and defines `KERN_FEATURE_MIXED_MODE_STACK` for the `kern_features` syscall.

State, dependencies, and risks: state is syscall number ABI and feature bit reporting. Dependencies include generated Kbuild outputs and libc syscall wrappers. Risks are wrong syscall table selection for compat builds and stale feature bits. Test signals are syscall-number header generation, simple syscall invocation from 32-bit/64-bit userspace, and `kern_features` probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/unistd.h -->
