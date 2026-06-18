# sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu_context_64.h

## sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu_context_64.h

### Purpose
`sources/distributed-fs/ceph-client/arch/sparc/include/asm/mmu_context_64.h` implements SPARC64 context-switch glue for TSB switching, secondary context loading, TLB flushing, and ADI MCDPER save/restore. It is part of the SPARC architecture support imported in the Ceph client Linux source tree. Its direct consumers are low-level kernel architecture, bus, MMU, interrupt, PROM, and driver code; Ceph filesystem code depends on it only indirectly through a correctly functioning kernel platform layer.

### Important APIs, Types, And Functions
Source read size: 198 lines, 5621 bytes. Primary surface: `get_new_mmu_context`, `init_new_context`, `destroy_context`, `__tsb_context_switch`, `tsb_context_switch_ctx`, `switch_mm`, `activate_mm`, `arch_start_context_switch`, `finish_arch_post_lock_switch`, and `mm_untag_mask`. Symbol scan highlights: `__SPARC64_MMU_CONTEXT_H`, `get_new_mmu_context`, `init_new_context`, `destroy_context`, `__tsb_context_switch`, `struct tsb_config`, `tsb_context_switch_ctx`, `tsb_context_switch`, `tsb_grow`, `smp_tsb_sync`, `load_secondary_context`, `__volatile__`, `__flush_tlb_mm`, `switch_mm`, `activate_mm`, `__HAVE_ARCH_START_CONTEXT_SWITCH`, `arch_start_context_switch`, `finish_arch_post_lock_switch`, `struct pt_regs`, `mm_untag_mask`.

### Control Flow
`switch_mm` records the active mm per CPU, allocates a context if invalid, unconditionally switches TSB state to avoid stale TSB growth races, flushes local TLBs for first-use contexts, and restores ADI/MCDPER state around scheduler switches. Because this is a header, most runtime behavior is selected by preprocessor branches or inlined/declared for implementation files; the executable flow is in the architecture, driver, or firmware-call code that includes it.

### State And Persistence
global context bitmaps/cache, per-CPU secondary-mm pointers, per-mm locks/TSB descriptors, and task flags for ADI state are live kernel state. There is no userspace filesystem persistence in this file; persistent effects are kernel memory, firmware data, CPU registers, device registers, page tables, interrupt state, or ABI constants depending on the specific header.

### Dependencies
Direct includes: `<linux/spinlock.h>`, `<linux/mm_types.h>`, `<linux/smp.h>`, `<linux/sched.h>`, `<asm/spitfire.h>`, `<asm/adi_64.h>`, `<asm-generic/mm_hooks.h>`, `<asm/percpu.h>`, `<asm-generic/mmu_context.h>`. Integration dependencies: `linux/sched.h`, `linux/smp.h`, `asm/spitfire.h`, `asm/adi_64.h`, percpu support, generic MM hooks, and TLB flush implementation.

### Integration Points
The header integrates with SPARC boot, MMU/page-table setup, PROM/OpenFirmware discovery, interrupt delivery, DMA/IOMMU, PCI, LEON/AMBA platform support, LDOM/LDC, or parport paths according to its exported contract. For the distributed filesystem tree, the link is indirect but important: Ceph client networking, block I/O, page cache, and memory reclaim depend on these architecture contracts being correct for the kernel configuration.

### Risks
the documented TSB grow race is high-risk; skipping a context switch or TLB flush can leave CPUs using stale TSBs. ADI register save/restore must match task flags and register encodings.

### Test Signals
SMP context-switch stress, TSB grow under CPU migration, THP/hugetlb workloads, ADI tests, and TLB shootdown validation. Also require representative SPARC cross-builds and include-user compile coverage because many failures only appear in specific 32-bit, 64-bit, sun4v, LEON, or legacy SBus configurations.
