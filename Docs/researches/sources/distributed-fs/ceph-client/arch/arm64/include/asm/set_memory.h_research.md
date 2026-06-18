# sources/distributed-fs/ceph-client/arch/arm64/include/asm/set_memory.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/set_memory.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/set_memory.h` Declares arm64 memory-attribute and direct-map validity helpers. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
can_set_direct_map(), set_memory_valid(), set_direct_map_invalid_noflush(), set_direct_map_default_noflush(), set_direct_map_valid_noflush(), kernel_page_present(), set_memory_encrypted(), set_memory_decrypted(). The file is 22 lines / 715 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Implementation files change PTE validity/encryption attributes and may defer TLB flushes for noflush variants; this header defines the callable surface.

### State, Persistence, And Dependencies
Persistent effects are page-table attributes and memory encryption/shared state. Header owns no storage. Depends on mem_encrypt and asm-generic/set_memory; integrates with module/text permissions, direct map hardening, memory hotplug, confidential computing, and page allocator/debug code.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Changing direct-map validity without required flushes or encryption coordination can expose stale mappings or corrupt data.

### Test Signals
Run set_memory selftests, rodata/text permission checks, direct-map debug tests, memory hotplug, and encrypted/decrypted transition tests.
