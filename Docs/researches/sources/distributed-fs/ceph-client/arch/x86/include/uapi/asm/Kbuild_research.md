<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/Kbuild

Purpose: Lists generated x86 UAPI syscall-number headers for Kbuild export: `unistd_32.h`, `unistd_64.h`, and `unistd_x32.h`.

Important APIs/types/functions: `generated-y` entries for the three generated unistd headers.

Control flow: During header generation/export, Kbuild creates or includes these ABI-specific syscall-number headers so userspace-facing installs have complete syscall definitions.

State and persistence behavior: No runtime state. The persistent artifact is the generated header set installed into exported UAPI headers.

Dependencies and integration points: Integrates with x86 syscall table generation and `uapi/asm/unistd.h` ABI selection for i386, x86_64, and x32.

Risks and test signals: Risks are missing generated headers in exported UAPI installs or stale syscall table generation. Test `make headers_install`, userspace builds against all three x86 ABIs, and syscall-number consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/Kbuild -->
