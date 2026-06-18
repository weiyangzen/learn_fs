# sources/distributed-fs/ceph-client/arch/arm64/include/asm/kfence.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kfence.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kfence.h

### Purpose
`kfence.h` provides ARM64 KFENCE hooks for protecting guard pages and deciding whether direct-map permissions can be changed early enough for the KFENCE pool.

### Important APIs, Types, And Functions
It exports `kfence_protect_page()`, `arm64_kfence_can_set_direct_map()`, `kfence_early_init`, and `arch_kfence_init_pool()` when KFENCE is enabled. The page protection path wraps `set_memory_valid()`.

### Control Flow
KFENCE calls `kfence_protect_page()` to invalidate or restore a direct-map page. If early direct-map mutation is available, `arch_kfence_init_pool()` initializes protected pool mappings; otherwise the inline fallback reports unsupported.

### State, Persistence, And Dependencies
State is limited to `kfence_early_init` and page-table permissions. It depends on `asm/set_memory.h`, KFENCE configuration, and direct-map page attribute management.

### Integration Points
The generic KFENCE allocator uses this header to install guard pages on ARM64. It is a diagnostic safety layer for kernel allocations used by filesystems, networking, and drivers.

### Risks
Incorrect direct-map permission updates can leave guard pages accessible or break legitimate kernel access. Early boot ordering is sensitive because KFENCE may initialize before full mapping APIs are ready.

### Test Signals
Boot with `CONFIG_KFENCE`; trigger KFENCE allocation faults; verify guard pages fault and unprotect cleanly; test early and non-early initialization paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kfence.h -->
