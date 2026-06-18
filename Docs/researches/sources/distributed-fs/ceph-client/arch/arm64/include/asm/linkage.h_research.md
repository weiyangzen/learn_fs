# sources/distributed-fs/ceph-client/arch/arm64/include/asm/linkage.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/linkage.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/linkage.h

### Purpose
`linkage.h` defines ARM64 assembly linkage macros for symbol alignment, function annotations, and BTI landing-pad handling.

### Important APIs, Types, And Functions
It provides architecture-specific `SYM_FUNC_START*`, alignment, and `BTI_C`/landing-pad style macros used by assembly files and generic linkage helpers.

### Control Flow
The macros expand during assembly preprocessing. They shape symbol boundaries and instruction sequences but do not implement C runtime flow.

### State, Persistence, And Dependencies
No runtime state. The persistent effect is ELF symbol metadata and instruction layout. It depends on generic linkage conventions and ARM64 BTI configuration.

### Integration Points
Used by low-level ARM64 assembly, including exception vectors, entry code, and KVM hyp assembly.

### Risks
Incorrect symbol annotations break unwinding, kallsyms, objtool-like validation, or BTI enforcement. Alignment changes can affect alternative patching.

### Test Signals
Build with BTI and without; inspect symbols/unwind metadata; boot-test exception and hyp paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/linkage.h -->
