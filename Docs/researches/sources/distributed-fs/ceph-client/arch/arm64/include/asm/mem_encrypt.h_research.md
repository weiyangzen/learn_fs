# sources/distributed-fs/ceph-client/arch/arm64/include/asm/mem_encrypt.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mem_encrypt.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/mem_encrypt.h

### Purpose
`mem_encrypt.h` supplies ARM64 stubs or hooks for confidential-computing memory encryption interfaces expected by generic kernel code.

### Important APIs, Types, And Functions
It defines architecture predicates/helpers for encrypted memory, DMA decryption/encryption hooks, and related no-op implementations where ARM64 has no active memory encryption backend in this tree.

### Control Flow
Generic memory-encryption call sites compile against these helpers. On this ARM64 version, most paths are compile-time no-ops or constant false unless a platform feature adds behavior elsewhere.

### State, Persistence, And Dependencies
No header-owned state. It depends on generic memory encryption API shape and DMA/memory-management call sites.

### Integration Points
Allows common kernel code shared with encrypted-memory architectures to build for ARM64. Filesystem I/O is affected indirectly through DMA/page handling call sites.

### Risks
A false no-op is dangerous if platform memory encryption is later introduced without updating this layer. API drift can break generic code.

### Test Signals
Compile all generic memory-encryption consumers on ARM64; run DMA and memory hotplug tests; verify encrypted-memory predicates remain correct for platform configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/mem_encrypt.h -->
