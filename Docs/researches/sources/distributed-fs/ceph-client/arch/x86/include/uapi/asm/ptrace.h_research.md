<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ptrace.h

Purpose: Defines the userspace-visible `struct pt_regs` layout for i386 and x86_64 and includes the register offset and processor flag UAPI.

Important APIs/types/functions: `struct pt_regs` for i386 and x86_64, plus included `ptrace-abi.h` and `processor-flags.h`.

Control flow: Kernel ptrace, signal, and core-dump paths copy register frames to userspace using this layout; debuggers inspect or modify fields.

State and persistence behavior: `pt_regs` snapshots represent transient task entry/exception state, but their serialized layout is persistent ABI for ptrace and core dumps.

Dependencies and integration points: Depends on compiler `__user`, ptrace ABI offsets, and processor flags. Integrates with kernel entry, syscall tracing, signal delivery, core dumps, KVM/debug tooling, and userspace debuggers.

Risks and test signals: Risks include field order drift, mismatch with assembly entry frames, and 32-bit compat confusion. Test ptrace GETREGS/SETREGS, coredump notes, signal handlers, syscall tracing, and frame-offset assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ptrace.h -->
