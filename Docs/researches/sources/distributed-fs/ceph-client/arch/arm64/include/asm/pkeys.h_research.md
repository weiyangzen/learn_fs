# sources/distributed-fs/ceph-client/arch/arm64/include/asm/pkeys.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/pkeys.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/pkeys.h` Implements arm64 protection-key integration for Permission Overlay Extension using VMA flags and mm context allocation state. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
ARCH_VM_PKEY_FLAGS, arch_max_pkey(), arch_set_user_pkey_access(), arch_pkeys_enabled(), vma_pkey(), arch_override_mprotect_pkey(), execute_only_pkey(), mm_pkey_allocation_map(), mm_set_pkey_allocated/free(), mm_pkey_is_allocated(), mm_pkey_alloc(), mm_pkey_free(). The file is 105 lines / 2389 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Allocation checks FEAT_POE availability, verifies the 3-bit key range is not exhausted, finds a free bit with ffz(), and updates mm->context.pkey_allocation_map. mprotect preserves the existing VMA pkey unless an explicit key is supplied.

### State, Persistence, And Dependencies
Persistent state is per-mm pkey_allocation_map and per-thread POR_EL0 access programmed elsewhere. The header itself has no storage. Depends on VM_PKEY flags, mm_struct context, system_supports_poe(), errno, bitops; consumed by generic pkey syscalls, mprotect, pgtable permission checks, and POR helpers.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Allocator trust is central: returning an invalid key would poison later PTE/POR checks; missing POE gating could expose unsupported ABI paths; freeing pkey 0 or out-of-range keys must stay rejected.

### Test Signals
Run pkey_alloc/free/mprotect selftests under POE-capable configs, compat and non-compat builds, and page-fault tests that validate read/write/exec denial through POR.
