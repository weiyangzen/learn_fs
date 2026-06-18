## sources/distributed-fs/ceph-client/arch/s390/mm/mmap.c

Purpose: defines s390 virtual memory layout policy for mmap base randomization, top-down vs legacy layout selection, unmapped-area search alignment, ASCE limit checking, and VM protection mapping.

Important APIs, types, and functions: `arch_mmap_rnd()`, `arch_get_unmapped_area()`, `arch_get_unmapped_area_topdown()`, `arch_pick_mmap_layout()`, `setup_protection_map()`, and `DECLARE_VM_GET_PAGE_PROT` are the arch-facing APIs. Helpers include `stack_maxrandom_size()`, `mmap_is_legacy()`, `mmap_base_legacy()`, `mmap_base()`, and `get_align_mask()`.

Control flow: process setup chooses bottom-up legacy layout when personality, unlimited stack, or sysctl demands it; otherwise it chooses top-down layout below stack with random gap. Unmapped-area search honors MAP_FIXED, caller hints, `mmap_min_addr`, hugepage alignment, shared/file ASLR alignment, and falls back from top-down to bottom-up on `-ENOMEM`. All successful candidate addresses go through `check_asce_limit()` so the process address-space control element supports the requested range.

State and persistence: fills `mm->mmap_base` and `MMF_TOPDOWN` per process. `protection_map[16]` is initialized once after boot and is read-only after init.

Dependencies and integration points: depends on generic mmap search, rlimits, randomization masks, hugetlb file checks, s390 ASCE growth limits, `mmap_min_addr`, stack guard gap, and generic `vm_get_page_prot` declaration.

Risks: ASCE limit checking is architecture-critical because s390 user page tables can upgrade levels lazily. Alignment behavior differs for hugepages, file/shared mappings, and anonymous private mappings; changes can affect ABI-visible mmap placement. Protection map deliberately makes private writable mappings initially read-only for COW, while shared writable maps are RW.

Test signals: mmap layout tests under legacy personality, unlimited/limited stack, ASLR on/off, MAP_FIXED, hint address, hugepage files, large allocations near TASK_SIZE, and permissions in `/proc/*/maps`/fault behavior.
