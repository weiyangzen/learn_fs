# sources/distributed-fs/ceph-client/arch/arm64/include/asm/mman.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mman.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/mman.h

### Purpose
`mman.h` defines ARM64-specific memory mapping policy helpers, especially executable mapping defaults and memory-tagging mmap flags.

### Important APIs, Types, And Functions
It wraps UAPI `mman` constants, defines `arch_calc_vm_prot_bits()`, `arch_validate_prot()`, `arch_validate_flags()`, and personality/read-implies-exec handling used by mmap/mprotect.

### Control Flow
Generic mmap/mprotect paths call the inline helpers to translate protection flags into `VM_*` bits and reject unsupported combinations. MTE-specific flags are accepted only when the architecture/configuration supports them.

### State, Persistence, And Dependencies
No owned state; policy depends on process personality, CPU MTE support, and VMA flags. It depends on generic MM constants and ARM64 MTE definitions.

### Integration Points
Used by userspace mapping syscalls, ELF loader behavior, JITs, and memory-tagged mappings that can back filesystem pages.

### Risks
Incorrect validation can allow unsupported tagged mappings or break executable mappings for legacy processes. ABI changes affect userspace.

### Test Signals
Run mmap/mprotect selftests, MTE userspace tests, READ_IMPLIES_EXEC tests, and compatibility-process mapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mman.h -->
