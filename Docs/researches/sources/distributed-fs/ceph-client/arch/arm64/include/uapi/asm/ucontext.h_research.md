<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/ucontext.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/ucontext.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/ucontext.h` defines arm64 `ucontext` as exposed to userspace signal handlers, including flags, link pointer, stack, signal mask, and machine context. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `_UAPI__ASM_UCONTEXT_H`; types: `ucontext`, `sigcontext`. The file is 33 lines / 1081 bytes. Direct includes are `linux/types.h`.

### Control Flow
Signal delivery fills this structure and user handlers pass it to APIs such as `getcontext`-style consumers or sigreturn paths.

### State, Persistence, And Dependencies
Notable global/static state symbols are `uc_mcontext`. The structure persists on the signal stack while a handler executes. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Layout drift breaks libc, debuggers, language runtimes, and signal-handler context inspection.

### Test Signals
Run signal/ucontext ABI tests and compile libc consumers against installed headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/ucontext.h -->
