<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/setup.h

Purpose: Defines SPARC command-line buffer size for UAPI consumers.

Important APIs and control flow: `COMMAND_LINE_SIZE` is 2048 for SPARC64 and 256 for SPARC32.

State, dependencies, and risks: state is boot command-line storage sizing. Dependencies are compiler ABI macros and setup code. Risks are truncation expectations and userspace tools assuming a larger command line on 32-bit systems. Test signals are boot command-line length tests and header compile checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/setup.h -->
