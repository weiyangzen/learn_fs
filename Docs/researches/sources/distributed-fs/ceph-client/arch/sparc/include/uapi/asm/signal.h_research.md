<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/signal.h

Purpose: Defines SPARC signal numbers, sub-signal codes, signal-set sizes, sigaction layouts, signal-stack structures, and signal mask operations.

Important APIs and control flow: signal numbers follow SunOS-influenced SPARC ordering, including `SIGEMT`, `SIGLOST`, and realtime range 32-64. Subsignal constants distinguish illegal instruction, FP errors, bus/alignment faults, and segmentation causes. Conditional macros select old 32-signal or new 64-signal ABI names depending on kernel/POSIX1B needs. The header defines old/new sigset types, SunOS `sigstack`, sigvec/sa flags, mask operations, minimum/default stack sizes, old/new sigaction layouts, and `stack_t`.

State, dependencies, and risks: state is process signal masks, handler dispositions, alternate stacks, and delivered trap subcodes. Dependencies include `sigcontext.h`, generic signal definitions, and POSIX types. Risks are nonstandard signal numbering, old/new sigset aliasing, unsupported-but-numeric flags, and 32-bit pointer comments in legacy `sigstack`. Test signals are signal number ABI tests, sigaction/sigaltstack, fault delivery subcodes, realtime signal masks, and compat signal frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/signal.h -->
