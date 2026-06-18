# sources/distributed-fs/ceph-client/arch/arm64/include/asm/stage2_pgtable.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/stage2_pgtable.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/stage2_pgtable.h` Defines KVM stage-2 page-table level and cache-preallocation calculations for arm64. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
stage2_pgtable_levels(ipa), kvm_stage2_levels(mmu), kvm_mmu_cache_min_pages(mmu). The file is 33 lines / 1055 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Calculations account for hardware concatenation of up to 16 entry tables by applying stage-1 level math to IPA_SHIFT minus four bits.

### State, Persistence, And Dependencies
No local state; consumes mmu->vtcr and KVM MMU cache state elsewhere. Depends on linux/pgtable.h and VTCR helpers; integrates with KVM stage-2 page-table allocation and IPA size support.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Wrong level counts under-allocate page-table pages or program invalid VTCR levels, breaking guest memory translation.

### Test Signals
Run KVM guests across IPA sizes, LPA2 stage-2 configs, dirty-log/memslot stress, and allocation failure tests.
