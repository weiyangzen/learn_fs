# sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgtable-prot.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgtable-prot.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/pgtable-prot.h` Defines arm64 page-protection bit layouts and canonical pgprot values for kernel, user, stage-2, PIE, POE, GCS, BTI, LPA2, realm shared memory, userfaultfd write-protect, dirty/write tracking, device memory, normal memory, tagged memory, and execute-only mappings. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
PTE_WRITE/PTE_DIRTY/PTE_SPECIAL/PTE_PRESENT_INVALID, PROT_* and _PAGE_* constants, PAGE_* pgprot macros, PAGE_S2_MEMATTR(), PTE_MAYBE_NG, PTE_MAYBE_SHARED, PHYS_MASK_SHIFT/PHYS_MASK, PTE_MAYBE_GP, pte_pi_index(), PIE_E0, PIE_E1, _PAGE_GCS, _PAGE_GCS_RO. The file is 191 lines / 8497 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Most behavior is compile-time constant composition, with small runtime conditionals for LPA2, BTI, non-global mappings, and CCA realm shared mappings. Callers receive pgprot_t encodings that are later consumed by pgtable.h setters and TLB/cache maintenance paths.

### State, Persistence, And Dependencies
No owned storage except extern policy variables arm64_use_ng_mappings and prot_ns_shared; state persists in page-table entries, MAIR/PIR/POR interpretation, and CPU feature decisions. Depends on memory.h, pgtable-hwdef.h, cpufeature.h, pgtable-types.h, rsi.h, sysreg PIE/POE encodings; integrates with core-mm mmap/mprotect, KVM stage-2, MTE, BTI, GCS, and Arm CCA realm code.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Wrong bit masks can corrupt permissions, expose executable or writable mappings, break LPA2 physical addressing, or make present-invalid/PROT_NONE entries visible to hardware incorrectly.

### Test Signals
Build 4K/16K/64K, LPA2, BTI, MTE, GCS, userfaultfd, and CCA configs; run page-table permission, mprotect, ptdump, KVM stage-2, and LKDTM W^X checks.
